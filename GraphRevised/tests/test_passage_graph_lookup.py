"""Passage-specific MCP reasoning without a model provider or database."""

import asyncio
import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from GraphRevised.discovery.passage_graph_lookup import MAX_TOOL_CALLS, TOOLS, explore
from GraphRevised.proposals.passage_reader import ReaderOutput, _read_source, with_lookup_rationale
from GraphRevised.proposals.registry import load_registry
from GraphRevised.tests.test_passage_reader_offline import INQUIRY, claim, drafts


class Session:
    def __init__(self):
        self.calls = []

    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=name, description="", inputSchema={"type": "object"})
                                      for name in TOOLS])

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        value = ({"id": arguments["entity_id"], "kind": "Person", "label": "Augustus",
                  "status": "provisional", "authorityLinks": [{"identifier": "Q1405", "status": "accepted"}]}
                 if name == "get_entity" else {"matches": []})
        return SimpleNamespace(isError=False, structuredContent=value, content="")


class Request:
    type = "tool_use"

    def __init__(self, name, value, identifier="1"):
        self.name, self.input, self.id = name, value, identifier

    def model_dump(self, **kwargs):
        return {"type": self.type, "id": self.id, "name": self.name, "input": self.input}


def response(*requests, stop="tool_use"):
    usage = SimpleNamespace(input_tokens=10, output_tokens=5, cache_read_input_tokens=0,
                            cache_creation_input_tokens=0)
    return SimpleNamespace(model="test", stop_reason=stop, content=list(requests), usage=usage)


def client(*responses):
    return SimpleNamespace(messages=SimpleNamespace(create=Mock(side_effect=responses)))


class PassageGraphLookupTests(unittest.TestCase):
    def setUp(self):
        self.entity_id = "chr:entity:augustus"
        self.selected = {"selections": [{"entity_id": self.entity_id, "name": "Octavius",
                                          "rationale": "The context and authority identify Augustus."}]}

    def run_lookup(self, session, model):
        return asyncio.run(explore(session, model, "test", INQUIRY, "Octavius came to Philippi.", []))

    def test_inspection_and_selection_produce_auditable_review(self):
        session = Session()
        model = client(response(Request("find_entities", {"name": "Octavius"})),
                       response(Request("get_entity", {"entity_id": self.entity_id})),
                       response(Request("select_entities", self.selected)))
        report = self.run_lookup(session, model)
        self.assertEqual([x["name"] for x in report["toolCalls"]], ["find_entities", "get_entity"])
        self.assertEqual(report["selections"][0]["entity"]["authorityLinks"][0]["status"], "accepted")
        self.assertEqual(report["usage"]["inputTokens"], 30)

    def test_uninspected_and_unquoted_selections_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "not inspected"):
            self.run_lookup(Session(), client(response(Request("select_entities", self.selected))))
        self.selected["selections"][0]["name"] = "Caesar"
        with self.assertRaisesRegex(ValueError, "does not occur"):
            self.run_lookup(Session(), client(response(Request("get_entity", {"entity_id": self.entity_id})),
                                              response(Request("select_entities", self.selected))))

    def test_same_name_cannot_select_two_entities(self):
        self.selected["selections"].append({"entity_id": "chr:entity:father", "name": "Octavius",
                                            "rationale": "Another possible historical person."})
        model = client(response(Request("get_entity", {"entity_id": self.entity_id}),
                                Request("get_entity", {"entity_id": "chr:entity:father"}, "2")),
                       response(Request("select_entities", self.selected)))
        with self.assertRaisesRegex(ValueError, "Ambiguous name"):
            self.run_lookup(Session(), model)

    def test_unknown_tools_rejected_and_excess_calls_not_executed(self):
        with self.assertRaisesRegex(ValueError, "Disallowed"):
            self.run_lookup(Session(), client(response(Request("write_graph", {}))))
        requests = [Request("find_entities", {"name": str(i)}, str(i)) for i in range(MAX_TOOL_CALLS + 1)]
        session = Session()
        model = client(response(*requests), response(Request("select_entities", {"selections": []})))
        self.run_lookup(session, model)
        self.assertEqual(len(session.calls), MAX_TOOL_CALLS)
        results = model.messages.create.call_args_list[1].kwargs["messages"][-1]["content"]
        self.assertTrue(results[-1]["is_error"])

    def test_force_selection_near_tool_budget(self):
        requests = [Request("find_entities", {"name": str(i)}, str(i)) for i in range(MAX_TOOL_CALLS - 2)]
        model = client(response(*requests), response(Request("select_entities", {"selections": []})))
        self.run_lookup(Session(), model)
        self.assertEqual([tool["name"] for tool in model.messages.create.call_args_list[1].kwargs["tools"]],
                         ["select_entities"])

    def test_force_selection_on_final_model_turn(self):
        model = client(*(response(Request("find_entities", {"name": str(i)}, str(i))) for i in range(4)),
                       response(Request("select_entities", {"selections": []})))
        self.run_lookup(Session(), model)
        self.assertEqual([tool["name"] for tool in model.messages.create.call_args_list[4].kwargs["tools"]],
                         ["select_entities"])

    def test_no_selection_is_valid_and_refusal_is_explicit(self):
        report = self.run_lookup(Session(), client(response(Request("select_entities", {"selections": []}))))
        self.assertEqual(report["selections"], [])
        with self.assertRaisesRegex(RuntimeError, "without selections"):
            self.run_lookup(Session(), client(response(stop="refusal")))

    def test_partial_tool_trace_is_retained_on_failure(self):
        class FailingSession(Session):
            async def call_tool(self, name, arguments):
                return SimpleNamespace(isError=True, content="tool failure")

        audit = {}
        with self.assertRaisesRegex(RuntimeError, "tool failure"):
            asyncio.run(explore(FailingSession(), client(response(Request("find_entities", {"name": "Octavius"}))),
                                "test", INQUIRY, "Octavius came to Philippi.", [], audit))
        self.assertEqual(audit["toolCalls"][0]["name"], "find_entities")
        self.assertNotIn("result", audit["toolCalls"][0])
        self.assertEqual(audit["usage"]["inputTokens"], 10)

    def test_identification_reason_is_persisted_in_relevant_draft(self):
        (draft,), _ = drafts(claim(subject_id=self.entity_id))
        enriched = with_lookup_rationale(draft, self.selected["selections"])
        self.assertIn("Octavius -> chr:entity:augustus", enriched.rationale)
        self.assertIn("context and authority", enriched.rationale)
        unrelated = with_lookup_rationale(draft, [{**self.selected["selections"][0], "entity_id": "other"}])
        self.assertEqual(unrelated, draft)

    @patch("GraphRevised.proposals.passage_reader.submit")
    @patch("GraphRevised.proposals.passage_reader.run_write")
    @patch("GraphRevised.proposals.passage_reader.depicted_events", return_value=[])
    @patch("GraphRevised.proposals.passage_reader.read_passage")
    @patch("GraphRevised.discovery.passage_graph_lookup.lookup")
    @patch("GraphRevised.proposals.passage_reader.open_source")
    def test_selected_entity_is_scoped_per_passage_and_reason_reaches_submission(
            self, source, lookup, read, depicted, write, submit):
        source.return_value = SimpleNamespace(
            refs=lambda _: ["1.1", "1.2"],
            observation=lambda ref: {"id": f"chr:observation:test:{ref}", "passageText": "Octavius came to Philippi."},
            author="Plutarch",
        )
        lookup.side_effect = [{
            "selections": [{**self.selected["selections"][0],
                            "entity": {"id": self.entity_id, "label": "Augustus", "kind": "Person",
                                       "status": "provisional"}}],
            "toolCalls": [], "usage": {},
        }, {"selections": [], "toolCalls": [], "usage": {}}]
        reader_claim = claim(subject_id=self.entity_id, object_id=None, predicate="participatedIn",
                             quotation="Octavius came to Philippi.")
        output = ReaderOutput(claims=[reader_claim], unresolved_mentions=[], notes=[], periods=[])
        meta = {"model": "test", "inputTokens": 1, "cacheReadTokens": 0, "cacheWriteTokens": 0,
                "outputTokens": 1, "stopReason": "end_turn"}
        read.return_value = (output, meta)
        validation = SimpleNamespace(outcome=SimpleNamespace(value="valid"), reasons=[], notes=[],
                                     proposal_id="proposal", related_assertions=[])
        submit.return_value = SimpleNamespace(validation=validation, stored=True)
        tx = SimpleNamespace(commit=Mock(), rollback=Mock())
        session = SimpleNamespace(execute_read=lambda fn: [], begin_transaction=lambda: tx)
        args = SimpleNamespace(sections="1.1,1.2", found=False, chapters=None, model="test", submit=True,
                               graph_lookup=True)
        totals = {key: 0 for key in ("stored", "malformed", "inputTokens", "cacheReadTokens",
                                     "cacheWriteTokens", "outputTokens")}
        log = io.StringIO()
        with patch("GraphRevised.proposals.passage_reader._related_lines", return_value=[]):
            _read_source(args, INQUIRY, session, None, {}, load_registry(), object(), log, {}, None, totals, {"claims"})
        self.assertIn(self.entity_id, [e["id"] for e in read.call_args_list[0].args[2].scope])
        self.assertNotIn(self.entity_id, [e["id"] for e in read.call_args_list[1].args[2].scope])
        self.assertEqual(INQUIRY.scope, [])
        self.assertEqual(submit.call_count, 1)
        self.assertIn("Octavius -> chr:entity:augustus", submit.call_args.args[1].rationale)
        records = [json.loads(line) for line in log.getvalue().splitlines()]
        self.assertEqual(records[1]["graphLookup"]["selections"][0]["entity_id"], self.entity_id)
        self.assertEqual(records[2]["drafts"][0]["outcome"], "out_of_scope")
        tx.commit.assert_called_once()
