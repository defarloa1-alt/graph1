"""The MCP connector exposes typed, read-only lookups and never a general Cypher tool (05 §7).

Offline: no Neo4j. The live tools are checked against the graph by hand (connector/CONNECTOR.md).
"""

import asyncio
import unittest
from unittest import mock

from GraphRevised.connector import ontology
from GraphRevised.connector.server import build_server, name_score


class NameScoreTests(unittest.TestCase):
    def test_the_same_words_score_one(self):
        self.assertEqual(name_score("Battle of Actium", "the battle of Actium"), 1.0)

    def test_a_word_prefix_finds_an_alias(self):
        self.assertGreaterEqual(name_score("Octavian", "Caesar Octavianus"), 0.5)

    def test_a_short_name_outranks_a_long_title_that_mentions_it(self):
        self.assertGreater(name_score("Actium", "Battle of Actium"),
                           name_score("Actium", "Antony camps at Actium; Cleopatra joins (Weigall)"))

    def test_short_prefixes_do_not_match(self):
        self.assertEqual(name_score("Ant", "Antony"), 0.0)

    def test_unrelated_names_score_zero(self):
        self.assertEqual(name_score("Cleopatra", "Marcus Vipsanius Agrippa"), 0.0)


class ToolBoundaryTests(unittest.TestCase):
    def test_only_the_typed_lookups_are_exposed(self):
        tools = asyncio.run(build_server(graph=None).list_tools())
        self.assertEqual({tool.name for tool in tools}, {
            "find_entities", "lookup_authority", "get_entity", "get_fact", "event_overview", "review_queue",
            "graph_status", "get_subject", "describe_schema", "get_predicate", "get_subgraph"})

    def test_no_tool_takes_a_query(self):
        for tool in asyncio.run(build_server(graph=None).list_tools()):
            self.assertFalse({"query", "cypher"} & set(tool.inputSchema.get("properties", {})), tool.name)


class OntologyTests(unittest.TestCase):
    class Result:
        def __init__(self, rows):
            self.rows = rows

        def single(self):
            return self.rows[0] if self.rows else None

        def data(self):
            return self.rows

    class Transaction:
        def __init__(self, edges):
            self.edges = edges
            self.calls = []

        def run(self, query, **params):
            self.calls.append((query, params))
            if query == ontology.ENTITY_QUERY:
                return OntologyTests.Result([{"id": "root", "label": "Root", "status": "proposed", "kinds": ["Person"]}]
                                           if params["id"] == "root" else [])
            if query == ontology.NEIGHBOR_QUERY:
                rows = [dict(edge) for edge in self.edges
                        if edge["id"] not in params["seen"] and
                        (edge["subject"]["id"] in params["frontier"] or
                         (edge["object"] and edge["object"]["id"] in params["frontier"]))]
                return OntologyTests.Result(sorted(rows, key=lambda row: row["id"])[:params["limit"]])
            if query == ontology.EVIDENCE_QUERY:
                return OntologyTests.Result([
                    {"assertionId": edge_id, "evidence": [{"observationId": "obs", "state": "proposal",
                      "proposalStatus": "submitted"}], "truncated": True}
                    for edge_id in params["ids"] if edge_id == "a"
                ])
            raise AssertionError("Unexpected query")

    @staticmethod
    def edge(edge_id, subject, obj):
        def node(node_id):
            return {"id": node_id, "label": node_id, "status": "proposed", "kinds": ["Person"]}
        return {"id": edge_id, "predicate": "participatedIn", "status": "proposed", "mode": "asserted",
                "category": "factual", "subject": node(subject), "object": node(obj) if obj else None,
                "timeEdtf": None, "timeExpression": None}

    def test_predicate_rules_and_unknown_predicate(self):
        predicate = ontology.get_predicate("describedBy")
        self.assertIn("Work", predicate["objectKinds"])
        self.assertTrue(any(mapping["pid"] == "P1343" for mapping in predicate["wikidata"]))
        self.assertIn("error", ontology.get_predicate("not-a-predicate"))

    def test_schema_lists_bounded_observed_tokens(self):
        class SchemaResult:
            def value(self, field):
                return [f"{field}-{index:03}" for index in range(201)]

        class SchemaTransaction:
            def run(self, query, **params):
                self_query_limit = params["limit"]
                if self_query_limit != 201 or "CALL db." not in query:
                    raise AssertionError("Unexpected schema query")
                return SchemaResult()

        result = ontology.describe_schema(SchemaTransaction())
        for key in ("labels", "relationshipTypes", "propertyKeys"):
            self.assertEqual(len(result[key]), 200)
            self.assertTrue(result[key + "Truncated"])
        self.assertIn("Work", result["entitySubtypes"])

    def test_predicate_tool_returns_registry_data(self):
        _, result = asyncio.run(build_server(graph=None).call_tool("get_predicate", {"predicate_id": "describedBy"}))
        self.assertEqual(result["id"], "describedBy")

    def test_traversal_depth_pagination_direction_and_evidence(self):
        tx = self.Transaction([self.edge("a", "root", "b"), self.edge("b", "c", "b"),
                               self.edge("c", "b", None)])
        first = ontology.get_subgraph(tx, "root", 2, 0, 1)
        self.assertEqual(first["nextOffset"], 1)
        self.assertEqual(first["assertions"][0]["subject"]["id"], "root")
        self.assertEqual(first["assertions"][0]["object"]["id"], "b")
        self.assertEqual(first["assertions"][0]["evidence"][0]["proposalStatus"], "submitted")
        self.assertTrue(first["assertions"][0]["evidenceTruncated"])
        second = ontology.get_subgraph(tx, "root", 2, 1, 2)
        self.assertEqual([edge["id"] for edge in second["assertions"]], ["b", "c"])
        self.assertEqual(second["assertions"][0]["distance"], 2)
        self.assertEqual(second["assertions"][0]["subject"]["id"], "c")
        self.assertIsNone(second["assertions"][1]["object"])
        self.assertIsNone(second["nextOffset"])
        self.assertFalse(second["traversalTruncated"])

    def test_traversal_cap_and_invalid_inputs(self):
        tx = self.Transaction([self.edge(f"{i:03}", "root", f"n{i}") for i in range(4)])
        with mock.patch.object(ontology, "MAX_EDGES", 3):
            result = ontology.get_subgraph(tx, "root", 2, 0, 2)
            self.assertTrue(result["traversalTruncated"])
            self.assertEqual(result["nextOffset"], 2)
        for args in (("", 1, 0, 1), ("root", 3, 0, 1), ("root", 1, -1, 1), ("root", 1, 0, 51)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                ontology.get_subgraph(tx, *args)
        self.assertIn("error", ontology.get_subgraph(tx, "missing", 1, 0, 1))


if __name__ == "__main__":
    unittest.main()
