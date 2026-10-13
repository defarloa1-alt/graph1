"""The exploration export shows everything found at once, one edge per fact, labelled by status and source
(25 §2, L1; 26-UI-DATA-CONTRACT.md).

Every test is rolled back; the fixtures are synthetic and the assertions look
only at them, so the tests do not depend on what the live graph contains.
"""

import os
import unittest

from GraphRevised.export.cytoscape import projection

FIXTURES = """
CREATE (leader:Entity {id: "chr:entity:test-x-leader", kind: "Person", label: "Test leader", status: "provisional"})
CREATE (battle:Entity {id: "chr:entity:test-x-battle", kind: "Event", label: "Test battle", status: "provisional"})
CREATE (period:Entity {id: "chr:entity:test-x-period", kind: "Period", label: "Test era", status: "proposed"})
CREATE (:Entity {id: "chr:entity:test-x-lonely", kind: "Work", label: "Test catalogue", status: "proposed"})
CREATE (:Entity {id: "chr:entity:test-x-gone", kind: "Person", label: "Test duplicate", status: "deprecated"})
CREATE (work:Entity {id: "chr:entity:test-x-work", kind: "Work", label: "Test author, Test history", status: "provisional"})
CREATE (passage:SourceObservation {id: "chr:observation:test-x:1", shortLabel: "Test 1.1"})-[:IN_WORK]->(work)
CREATE (fought:Assertion {id: "chr:assertion:test-x-fought", label: "Test leader fought at Test battle",
                          predicate: "participatedIn", status: "proposed", category: "factual"})
CREATE (fought)-[:ASSERTION_SUBJECT]->(leader), (fought)-[:ASSERTION_OBJECT]->(battle)
CREATE (proposal:Proposal {id: "chr:proposal:test-x-fought", status: "submitted"})-[:PROPOSES]->(fought)
CREATE (proposal)-[:PROPOSES_EVIDENCE {quotation: "Test leader fought"}]->(passage)
CREATE (says:Assertion {id: "chr:assertion:test-x-fought:q0123456789", label: "According to the work: fought",
                        predicate: "participatedIn", status: "proposed", mode: "attributed", category: "factual"})
CREATE (says)-[:ASSERTION_SUBJECT]->(leader), (says)-[:ASSERTION_OBJECT]->(battle), (says)-[:ATTRIBUTED_TO]->(work)
CREATE (play:Entity {id: "chr:entity:test-x-play", kind: "Work", label: "Test playwright, Test play", form: "play"})
CREATE (staged:Assertion {id: "chr:assertion:test-x-fought:qabcdefabcd", label: "In the play: fought",
                          predicate: "participatedIn", status: "proposed", mode: "attributed", category: "imaginative"})
CREATE (staged)-[:ASSERTION_SUBJECT]->(leader), (staged)-[:ASSERTION_OBJECT]->(battle), (staged)-[:ATTRIBUTED_TO]->(play)
CREATE (era:Assertion {id: "chr:assertion:test-x-era", label: "Test era occurred", predicate: "occurred",
                       status: "proposed", mode: "attributed", category: "factual"})
CREATE (era)-[:ASSERTION_SUBJECT]->(period), (era)-[:ATTRIBUTED_TO]->(work)
CREATE (wrong:Assertion {id: "chr:assertion:test-x-wrong", label: "Test leader fought at Test era",
                         predicate: "participatedIn", status: "rejected", category: "factual"})
CREATE (wrong)-[:ASSERTION_SUBJECT]->(leader), (wrong)-[:ASSERTION_OBJECT]->(battle)
CREATE (note:Annotation {id: "chr:annotation:test-x-note", kind: "passage-of-note", noteType: "motive",
                         note: "Test motive", status: "flagged"})-[:ANNOTATES]->(passage)
CREATE (note)-[:CONCERNS]->(leader)
CREATE (dismissed:Annotation {id: "chr:annotation:test-x-dismissed", kind: "passage-of-note", noteType: "detail",
                              note: "Test dismissed", status: "dismissed"})-[:ANNOTATES]->(passage)
CREATE (dismissed)-[:CONCERNS]->(leader)
"""


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class ExplorationExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
            notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        self.tx.run(FIXTURES)

    def tearDown(self):
        self.tx.rollback()

    def view(self, audit=False):
        elements = projection(self.tx, audit)["elements"]
        nodes = {n["data"]["id"]: n["data"] for n in elements["nodes"] if "test-x" in n["data"]["id"]}
        edges = {e["data"]["id"]: e["data"] for e in elements["edges"] if "test-x" in e["data"]["id"]}
        return nodes, edges

    def test_one_edge_per_fact_with_its_voices(self):
        nodes, edges = self.view()
        fought = edges["chr:assertion:test-x-fought#factual"]
        self.assertEqual(fought["sentence"], "Test leader participated in Test battle")
        self.assertEqual((fought["status"], fought["mode"]), ("proposed", "asserted"))
        self.assertEqual(fought["attestation"], "attested (1 author)")  # the work twice is one author
        own, says = fought["voices"]
        self.assertIsNone(own["accordingTo"])
        self.assertEqual(own["quotes"], [{"source": "Test author, Test history", "locator": "Test 1.1",
                                          "quotation": "Test leader fought", "pending": True}])
        self.assertEqual(says["accordingTo"], "Test author, Test history")
        self.assertEqual([p["status"] for p in own["review"]], ["submitted"])

    def test_imagined_versions_are_their_own_line(self):
        _, edges = self.view()
        staged = edges["chr:assertion:test-x-fought#imaginative"]
        self.assertEqual((staged["attestation"], staged["mode"]), ("imagined", "attributed"))
        self.assertEqual([v["accordingTo"] for v in staged["voices"]], ["Test playwright, Test play"])

    def test_unary_facts_sit_on_their_node(self):
        nodes, _ = self.view()
        period = nodes["chr:entity:test-x-period"]
        self.assertEqual(period["status"], "proposed")
        self.assertEqual(period["factLines"], ["Test era occurred (undated) — attested (1 author)"])
        self.assertEqual(period["facts"][0]["voices"][0]["accordingTo"], "Test author, Test history")

    def test_entities_without_claims_are_shown(self):
        nodes, _ = self.view()
        self.assertIn("chr:entity:test-x-lonely", nodes)

    def test_notes_are_listed_on_the_entity(self):
        nodes, _ = self.view()
        self.assertEqual(nodes["chr:entity:test-x-leader"]["notes"], ["motive: Test motive (Test 1.1, flagged)"])

    def test_rejected_deprecated_and_dismissed_only_in_audit(self):
        nodes, edges = self.view()
        self.assertNotIn("chr:assertion:test-x-wrong#factual", edges)
        self.assertNotIn("chr:entity:test-x-gone", nodes)
        nodes, edges = self.view(audit=True)
        self.assertEqual(edges["chr:assertion:test-x-wrong#factual"]["status"], "rejected")
        self.assertIn("chr:entity:test-x-gone", nodes)
        self.assertEqual(len(nodes["chr:entity:test-x-leader"]["notes"]), 2)


if __name__ == "__main__":
    unittest.main()
