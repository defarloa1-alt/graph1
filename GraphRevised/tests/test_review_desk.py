"""The review desk's reads and decisions (live, rolled back; synthetic fixtures)."""

import os
import unittest

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import ReviewError, submit
from GraphRevised.review_desk.app import claims, decide, detail, entity, find, parts, render_detail, render_entity, table

BATTLE = ("chr:entity:test-desk-battle", "Event", "Test desk battle")
MOMENT = ("chr:entity:test-desk-moment", "Event", "Test desk moment")
LEADER = ("chr:entity:test-desk-leader", "Person", "Test desk leader")
PASSAGE = "chr:observation:test:desk-passage"
TEXT = "In the test desk moment of the battle the leader held the right wing."


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class ReviewDeskLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations, cls.registry = load_operations(), load_registry()
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
        self.addCleanup(self.tx.rollback)
        for entity_id, kind, label in (BATTLE, MOMENT, LEADER):
            run_write(self.tx, self.operations, "upsert_entity", {
                "id": entity_id, "kind": kind, "label": label, "description": None,
                "status": "provisional", "shortLabel": None})
        run_write(self.tx, self.operations, "upsert_passage_observation", {
            "id": PASSAGE, "label": "Test desk passage", "shortLabel": "Desk 1", "sourceSystem": "Test",
            "locator": "test:desk:1", "passageText": TEXT, "passageHash": "test", "editorialNotes": [],
            "language": "en", "workTitle": "Test", "author": "Test", "translator": None, "editionCitation": "Test",
            "rights": "test", "sourceUri": "test", "sourceRevision": "test", "retrievedAt": "2026-11-13T00:00:00Z",
            "contentHash": "test", "rawPayloadUri": None, "status": "observed"})
        self.part = self.propose("partOf", MOMENT[0], BATTLE[0], "test desk moment of the battle")
        self.took_part = self.propose("participatedIn", LEADER[0], MOMENT[0], "the leader held the right wing")

    def propose(self, predicate, subject, obj, quote):
        draft = ProposalDraft(predicate=predicate, subject_id=subject, object_id=obj, observation_ids=(PASSAGE,),
                              quotations=(Quotation(observation_id=PASSAGE, text=quote),),
                              rationale="a synthetic review desk claim", proposed_by="test-desk")
        return submit(self.tx, draft, self.registry, self.operations).validation

    def test_reads_an_entity_its_claims_and_its_parts(self):
        self.assertIn(MOMENT[0], [row["id"] for row in find(self.tx, "test desk moment")])
        rows = claims(self.tx, MOMENT[0])
        self.assertEqual({(r["predicate"], r["otherId"], r["outgoing"]) for r in rows},
                         {("partOf", BATTLE[0], True), ("participatedIn", LEADER[0], False)})
        self.assertTrue(all(len(r["open"]) == 1 for r in rows))
        self.assertEqual(len(table(rows)), 2)
        self.assertIn("2 live claims · 2 open proposals", render_entity(entity(self.tx, MOMENT[0]), rows))
        self.assertEqual([(p["id"], p["open"]) for p in parts(self.tx, BATTLE[0])], [(MOMENT[0], 2)])
        shown = render_detail(detail(self.tx, self.took_part.assertion_id))
        self.assertIn("“the leader held the right wing”", shown)
        self.assertIn(self.took_part.proposal_id, shown)

    def test_accept_then_reject_rebuild_the_fact_layer(self):
        _, counts = decide(self.tx, self.part.proposal_id, "accept", by="test-curator", basis="test")
        self.assertGreater(counts["factEdges"], 0)
        edge = self.tx.run("MATCH (:Entity {id: $s})-[r:PART_OF {derived: 'fact-layer'}]->(:Entity {id: $o}) "
                           "RETURN r.status AS status", s=MOMENT[0], o=BATTLE[0]).single()
        self.assertEqual(edge["status"], "accepted")

        decide(self.tx, self.took_part.proposal_id, "reject", by="test-curator", basis="test",
               reason="unsupported", reject_claim=True)
        gone = self.tx.run("MATCH (:Entity {id: $s})-[r:PARTICIPATED_IN {derived: 'fact-layer'}]->() RETURN count(r) AS n",
                           s=LEADER[0]).single()["n"]
        self.assertEqual(gone, 0)
        self.assertEqual(parts(self.tx, BATTLE[0])[0]["open"], 0)

    def test_a_decision_needs_who_and_why(self):
        with self.assertRaises(ReviewError):
            decide(self.tx, self.part.proposal_id, "accept", by="", basis="test")
        with self.assertRaises(ReviewError):
            decide(self.tx, self.part.proposal_id, "reject", by="test-curator", basis="test", reason="nope")


if __name__ == "__main__":
    unittest.main()
