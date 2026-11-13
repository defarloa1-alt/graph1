"""The passage reader through a lens (39-LENS-SPECIALISTS.md), without a model call or a database."""

import io
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from GraphRevised.proposals.lens import lens_registry, lens_text, load_lens
from GraphRevised.proposals.passage_reader import (
    LENS_PROMPT_VERSION, PROMPT_VERSION, PROPOSER_ID, Inquiry, LensPredicateNeed, LensReaderOutput, ReaderClaim,
    ReaderDepictedEvent, ReaderNote, ReaderOutput, _read_source, proposer, read_passage, reader_prompt_version, to_drafts, to_predicate_needs,
)
from GraphRevised.proposals.registry import load_registry

OBSERVATION = "chr:observation:test:passage"
INQUIRY = Inquiry(
    id="chr:inquiry:test", version=1, label="Test inquiry", subject={"id": "chr:subject:test", "label": "Test"},
    focus=[], scope=[], guidance=[], source={"type": "perseus-tei", "edition": "none.xml", "chapters": "1-2"},
    work_id="chr:entity:test-work", narrative_event_id="chr:entity:test-battle", calendar="julian",
)
MILITARY = load_lens("military", "roman-republic")
LENSED = replace(INQUIRY, lens=MILITARY)


def claim(predicate="commanded", **extra):
    fields = dict(
        predicate=predicate, subject_id="chr:entity:test-admiral", object_id="chr:entity:test-wing",
        quotation="the admiral, as legate, held the left wing", rationale="The passage names his wing.",
        relevance="Command of part of the fleet.", ambiguities=[], role_id=None, role_quotation=None,
        time_source_expression=None, time_quotation=None, time_edtf=None, context_id=None, context_quotation=None,
    )
    return ReaderClaim(**(fields | extra))


def output(*claims):
    return ReaderOutput(claims=list(claims), unresolved_mentions=[], notes=[], periods=[])


def mocked_client(parsed):
    usage = SimpleNamespace(input_tokens=0, output_tokens=0, cache_read_input_tokens=0, cache_creation_input_tokens=0)
    response = SimpleNamespace(model="test", stop_reason="end_turn", usage=usage, _request_id="test",
                               parsed_output=parsed)
    parse = Mock(return_value=response)
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=parse))), parse


EDITION = SimpleNamespace(author="Author", title="Title", translator="Translator", citation="Citation")


class LoadLensTests(unittest.TestCase):
    def test_a_lens_names_its_specialist(self):
        self.assertEqual(MILITARY.specialist_id, "lens-specialist:military/roman-republic")
        self.assertIn("commanded", MILITARY.predicates)
        self.assertTrue(MILITARY.native_terms)
        self.assertTrue(MILITARY.rules)

    def test_unknown_lens_and_missing_grounding_are_refused(self):
        with self.assertRaisesRegex(ValueError, "no lens 'astrology'"):
            load_lens("astrology", "roman-republic")
        with self.assertRaisesRegex(ValueError, "no grounding for scope"):
            load_lens("military", "ptolemaic-kingdom")

    def test_a_lens_without_grounding_in_the_scope_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "somewhere.json").write_text(json.dumps({"version": 1, "lenses": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "has no military lens yet"):
                load_lens("military", "somewhere", grounding_directory=Path(directory))

    def test_the_registry_narrows_to_the_lens_predicates(self):
        narrowed = lens_registry(load_registry(), MILITARY)
        self.assertEqual(set(narrowed.predicates), set(MILITARY.predicates))

    def test_a_lens_predicate_missing_from_the_registry_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "registry lacks"):
            lens_registry(load_registry(), replace(MILITARY, predicates=("commanded", "sackedCity")))

    def test_a_lens_without_predicates_asks_for_them(self):
        economic = load_lens("economic", "roman-republic")
        self.assertEqual(economic.predicates, ())
        self.assertIn("draft no claims", lens_text(economic))


class LensDraftTests(unittest.TestCase):
    def test_drafts_name_the_specialist_and_the_lens_prompt(self):
        (draft,), malformed = to_drafts(output(claim()), OBSERVATION, "test-model", LENSED)
        self.assertEqual(malformed, [])
        self.assertEqual(draft.proposed_by, "lens-specialist:military/roman-republic")
        self.assertEqual(draft.prompt_version, LENS_PROMPT_VERSION)
        self.assertEqual(draft.mode, "attributed")

    def test_the_general_reader_is_unchanged(self):
        (draft,), _ = to_drafts(output(claim()), OBSERVATION, "test-model", INQUIRY)
        self.assertEqual(draft.proposed_by, PROPOSER_ID)
        self.assertEqual(draft.prompt_version, PROMPT_VERSION)
        self.assertEqual(proposer(INQUIRY), PROPOSER_ID)
        self.assertEqual(reader_prompt_version(LENSED), LENS_PROMPT_VERSION)

    def test_a_predicate_outside_the_lens_is_malformed(self):
        drafts, malformed = to_drafts(output(claim("childOf")), OBSERVATION, "test-model", LENSED)
        self.assertEqual(drafts, [])
        self.assertIn("not a predicate of the military lens", malformed[0]["error"])


class LensPacketTests(unittest.TestCase):
    def test_the_packet_carries_the_lens_and_only_its_predicates(self):
        parsed = LensReaderOutput(claims=[], unresolved_mentions=[], notes=[], depicted_events=[], predicate_needs=[])
        client, parse = mocked_client(parsed)
        read_passage(client, "test", LENSED, EDITION, "1", {"passageText": "A passage."}, [], load_registry())
        kwargs = parse.call_args.kwargs
        system, packet = kwargs["system"][0]["text"], kwargs["system"][1]["text"]
        self.assertIn("16. Lens.", system)
        self.assertIn("never a predicate", system)
        self.assertIn("Lens: Military, for Roman Republic", packet)
        self.assertIn("imperium", packet)
        self.assertIn("- commanded (", packet)
        self.assertNotIn("- childOf (", packet)
        self.assertIs(kwargs["output_format"], LensReaderOutput)

    def test_the_general_reader_has_no_lens(self):
        client, parse = mocked_client(None)
        read_passage(client, "test", INQUIRY, EDITION, "1", {"passageText": "A passage."}, [], load_registry())
        kwargs = parse.call_args.kwargs
        self.assertNotIn("16. Lens.", kwargs["system"][0]["text"])
        self.assertIs(kwargs["output_format"], ReaderOutput)

    def test_a_lens_reading_returns_the_reader_output_and_its_needs(self):
        need = LensPredicateNeed(name="defectedTo", definition="changed sides to", subject_kinds=["Person"],
                                 object_kinds=["Person"], quotation="Dellius deserted to Caesar")
        event = ReaderDepictedEvent(key="e1", label="the admiral captures ships", existing_id="",
                                    quotation="Dellius deserted to Caesar", within_narrative_event=True,
                                    participants=[], objects=[], place_id="", place_quotation="", time_expression="",
                                    time_quotation="", relative_offset="", links=[])
        note = ReaderNote(note_type="motive", note="Why he left.", quotation="Dellius deserted to Caesar",
                          concerns=["chr:entity:test-admiral"])
        parsed = LensReaderOutput(claims=[claim()], unresolved_mentions=[], notes=[note], depicted_events=[event],
                                  predicate_needs=[need])
        client, _ = mocked_client(parsed)
        result, meta = read_passage(client, "test", LENSED, EDITION, "1", {"passageText": "x"}, [], load_registry())
        self.assertIsInstance(result, ReaderOutput)
        self.assertEqual(len(result.claims), 1)
        self.assertEqual(result.periods, [])
        self.assertEqual([e.key for e in result.depicted_events], ["e1"])
        self.assertEqual(meta["predicateNeedsDrafted"][0]["name"], "defectedTo")


class PredicateNeedTests(unittest.TestCase):
    PASSAGE = {"id": OBSERVATION, "passageText": "Then Dellius deserted to Caesar, fearing Cleopatra."}

    def need(self, **extra):
        return {"name": "defectedTo", "definition": "changed sides to", "subject_kinds": ["Person"],
                "object_kinds": ["Person"], "quotation": "Dellius deserted to Caesar"} | extra

    def test_a_verbatim_need_is_kept_with_its_observation(self):
        (need,), refused = to_predicate_needs([self.need()], self.PASSAGE)
        self.assertEqual(refused, [])
        self.assertEqual(need["observationId"], OBSERVATION)

    def test_needs_without_a_quotation_name_or_definition_are_refused(self):
        needs, refused = to_predicate_needs([
            self.need(quotation="Dellius went over to Octavian"),
            self.need(name="Defected To"),
            self.need(definition=" "),
        ], self.PASSAGE)
        self.assertEqual(needs, [])
        self.assertEqual([r["reason"] for r in refused], [
            "quotation does not appear verbatim in the passage",
            "a need's name is one camelCase word",
            "a need has a definition",
        ])


class NewEventScopeTests(unittest.TestCase):
    """A new depicted event's own claims are checked against the passage's scope, which includes it."""

    @patch("GraphRevised.proposals.passage_reader._related_lines", return_value=[])
    @patch("GraphRevised.proposals.passage_reader.submit")
    @patch("GraphRevised.proposals.passage_reader.propose_depicted_event")
    @patch("GraphRevised.proposals.passage_reader.run_write")
    @patch("GraphRevised.proposals.passage_reader.depicted_events", return_value=[])
    @patch("GraphRevised.proposals.passage_reader.read_passage")
    @patch("GraphRevised.proposals.passage_reader.open_source")
    def test_claims_on_a_new_event_reach_validation(self, source, read, depicted, write, propose, submit, related):
        text = "Then the admiral's whole wing took the enemy's ships at the tenth hour."
        source.return_value = SimpleNamespace(refs=lambda _: ["1.1"], author="Author",
                                              observation=lambda ref: {"id": OBSERVATION, "passageText": text})
        fleet = {"id": "chr:entity:test-wing", "label": "Wing", "kind": "Group"}
        battle = {"id": "chr:entity:test-battle", "label": "Battle", "kind": "Event"}
        inquiry = replace(LENSED, scope=[fleet, battle], proposable_kinds=("Event",))
        event = ReaderDepictedEvent(
            key="e1", label="the wing takes the ships", existing_id="", quotation="the admiral's whole wing took",
            within_narrative_event=True,
            participants=[{"entity_id": fleet["id"], "quotation": "the admiral's whole wing", "role_id": "",
                           "role_quotation": ""}],
            objects=[], place_id="", place_quotation="", time_expression="", time_quotation="", relative_offset="", links=[])
        output = ReaderOutput(claims=[], unresolved_mentions=[], notes=[], periods=[], depicted_events=[event])
        read.return_value = (output, {"model": "test", "inputTokens": 1, "cacheReadTokens": 0,
                                      "cacheWriteTokens": 0, "outputTokens": 1, "stopReason": "end_turn"})
        propose.side_effect = lambda tx, operations, **kw: {"id": kw.get("id") or "x", "created": True}
        validation = SimpleNamespace(outcome=SimpleNamespace(value="valid"), reasons=[], notes=[],
                                     proposal_id="p", related_assertions=[])
        submit.return_value = SimpleNamespace(validation=validation, stored=True)
        tx = SimpleNamespace(commit=Mock(), rollback=Mock())
        session = SimpleNamespace(execute_read=lambda fn: [], begin_transaction=lambda: tx)
        args = SimpleNamespace(sections="1.1", found=False, chapters=None, model="test", submit=True,
                               graph_lookup=False)
        totals = {key: 0 for key in ("stored", "malformed", "inputTokens", "cacheReadTokens",
                                     "cacheWriteTokens", "outputTokens")}
        log = io.StringIO()
        _read_source(args, inquiry, session, None, {}, load_registry(), object(), log, {}, None, totals,
                     {"claims", "events"})
        (record,) = [json.loads(line) for line in log.getvalue().splitlines()][1:]
        outcomes = {draft["outcome"] for draft in record["drafts"]}
        self.assertTrue(record["drafts"])
        self.assertNotIn("out_of_scope", outcomes)
        self.assertEqual(propose.call_args.kwargs["proposed_by"], "lens-specialist:military/roman-republic")


if __name__ == "__main__":
    unittest.main()
