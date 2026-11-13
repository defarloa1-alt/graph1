"""MCP-backed exploration without network, a model provider, or Neo4j."""

import asyncio
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from GraphRevised.discovery.graph_explorer import ALLOWED_TOOLS, MAX_OUTPUT_TOKENS, MAX_TOOL_CALLS, explore


class Session:
    def __init__(self):
        self.calls = []
        self.fail = False

    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=name, description=name,
                                                      inputSchema={"type": "object"}) for name in ALLOWED_TOOLS])

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        value = ({"id": arguments["subject_id"], "focus": [{"id": "chr:entity:battle"}]}
                 if name == "get_subject" else {"id": arguments.get("entity_id"), "status": "proposed"})
        return SimpleNamespace(isError=self.fail, structuredContent=value, content="tool failure")


def response(stop, content):
    return SimpleNamespace(stop_reason=stop, content=content, usage=SimpleNamespace(input_tokens=10, output_tokens=5))


class Request:
    type = "tool_use"

    def __init__(self, name="get_entity", identifier="1"):
        self.name, self.id, self.input = name, identifier, {"entity_id": "chr:entity:battle"}

    def model_dump(self, **kwargs):
        return {"type": self.type, "id": self.id, "name": self.name, "input": self.input}


def client(*responses):
    create = Mock(side_effect=list(responses))
    return SimpleNamespace(messages=SimpleNamespace(create=create))


class GraphExplorerTests(unittest.TestCase):
    def test_seed_and_tool_calls_are_recorded_for_review(self):
        session = Session()
        model = client(response("tool_use", [Request()]),
                       response("end_turn", [SimpleNamespace(type="text", text="Proposed battle; review needed.")]))
        report = asyncio.run(explore(session, model, "chr:subject:test", "test-model"))
        self.assertEqual(report["status"], "needs-review")
        self.assertEqual([call["name"] for call in report["toolCalls"]], ["get_subject", "get_entity"])
        self.assertEqual(report["toolCalls"][1]["result"]["status"], "proposed")
        self.assertEqual(report["usage"], {"inputTokens": 20, "outputTokens": 10})
        self.assertEqual(model.messages.create.call_count, 2)
        self.assertEqual(model.messages.create.call_args.kwargs["max_tokens"], MAX_OUTPUT_TOKENS)
        self.assertEqual(report["limits"]["maxOutputTokensPerCall"], MAX_OUTPUT_TOKENS)
        self.assertIn("not automatically used", report["limitations"][-1])

    def test_disallowed_tool_fails(self):
        model = client(response("tool_use", [Request("execute_cypher")]))
        with self.assertRaisesRegex(ValueError, "disallowed"):
            asyncio.run(explore(Session(), model, "chr:subject:test", "test"))

    def test_budget_is_enforced_before_calls(self):
        model = client(response("tool_use", [Request(identifier=str(i)) for i in range(MAX_TOOL_CALLS)]))
        session = Session()
        with self.assertRaisesRegex(RuntimeError, "MCP limit"):
            asyncio.run(explore(session, model, "chr:subject:test", "test"))
        self.assertEqual(len(session.calls), 1)

    def test_tool_error_is_not_treated_as_success(self):
        session = Session()
        session.fail = True
        with self.assertRaisesRegex(RuntimeError, "MCP tool get_subject failed"):
            asyncio.run(explore(session, client(), "chr:subject:test", "test"))

    def test_refusal_is_not_saved_as_review(self):
        with self.assertRaisesRegex(RuntimeError, "without a review"):
            asyncio.run(explore(Session(), client(response("refusal", [])), "chr:subject:test", "test"))

    def test_summary_without_inspecting_focus_is_refused(self):
        model = client(response("end_turn", [SimpleNamespace(type="text", text="Summary")]))
        with self.assertRaisesRegex(RuntimeError, "did not inspect every Subject focus"):
            asyncio.run(explore(Session(), model, "chr:subject:test", "test"))


if __name__ == "__main__":
    unittest.main()
