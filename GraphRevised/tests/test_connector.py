"""The MCP connector exposes typed, read-only lookups and never a general Cypher tool (05 §7).

Offline: no Neo4j. The live tools are checked against the graph by hand (connector/CONNECTOR.md).
"""

import asyncio
import unittest

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
            "graph_status"})

    def test_no_tool_takes_a_query(self):
        for tool in asyncio.run(build_server(graph=None).list_tools()):
            self.assertFalse({"query", "cypher"} & set(tool.inputSchema.get("properties", {})), tool.name)


if __name__ == "__main__":
    unittest.main()
