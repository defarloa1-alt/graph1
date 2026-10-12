"""Entities proposed by the reader: created proposed, reused when they exist, decided by the curator."""

import os
import unittest

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import proposed_entities, proposed_entity_id, propose_entity
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.review import decide_entity
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
from GraphRevised.proposals.store import ReviewError, submit
from GraphRevised.proposals.validator import Outcome

PASSAGE = "chr:observation:test:period-passage"
TEXT = "Thus ended the Test Commonwealth, which had lasted from 509 to 27 B.C., and a new order began."
DECISION = {"decided_by": "test-curator", "decision_basis": "test", "decided_at": "2026-10-12T00:00:00Z"}


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class ProposedEntityTests(unittest.TestCase):
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
        run_write(self.tx, self.operations, "upsert_entity", {"id": "chr:entity:test-work", "kind": "Work",
                                                              "label": "Test work", "description": None,
                                                              "status": "provisional", "shortLabel": None})
        run_write(self.tx, self.operations, "upsert_passage_observation", {
            "id": PASSAGE, "label": "Test passage", "shortLabel": None, "sourceSystem": "Test", "locator": "t:1",
            "passageText": TEXT, "passageHash": "t", "editorialNotes": [], "language": "en", "workTitle": "Test",
            "author": "Test", "translator": None, "editionCitation": "Test", "rights": "test", "sourceUri": "test",
            "sourceRevision": "t", "retrievedAt": "2026-10-12T00:00:00Z", "contentHash": "t", "rawPayloadUri": None,
            "status": "observed"})
        run_write(self.tx, self.operations, "link_observation_work", {"observationId": PASSAGE,
                                                                      "workId": "chr:entity:test-work"})

    def tearDown(self):
        self.tx.rollback()

    def propose(self, label="Test Commonwealth"):
        return propose_entity(self.tx, self.operations, kind="Period", label=label, proposed_by="test",
                              observation_id=PASSAGE, quotation="Thus ended the Test Commonwealth")

    def test_a_period_is_proposed_once_and_its_mentions_recorded(self):
        first = self.propose()
        self.assertTrue(first["created"])
        self.assertEqual(first["id"], proposed_entity_id("Period", "Test Commonwealth"))
        again = self.propose()
        self.assertFalse(again["created"])
        self.assertEqual(again["id"], first["id"])
        listed = [row for row in proposed_entities(self.tx) if row["id"] == first["id"]][0]
        self.assertEqual(listed["kind"], "Period")
        self.assertTrue(any(m["quotation"] == "Thus ended the Test Commonwealth" for m in listed["mentions"]))

    def test_an_existing_entity_with_the_same_name_is_reused(self):
        run_write(self.tx, self.operations, "upsert_entity", {"id": "chr:entity:test-commonwealth-period",
                                                              "kind": "Period", "label": "Test Commonwealth",
                                                              "description": None, "status": "provisional",
                                                              "shortLabel": None})
        proposed = self.propose()
        self.assertEqual(proposed["id"], "chr:entity:test-commonwealth-period")
        self.assertTrue(proposed["reused"])

    def test_the_source_bounds_are_an_attributed_claim(self):
        period = self.propose()["id"]
        draft = ProposalDraft(
            predicate="occurred", subject_id=period, object_id=None, observation_ids=(PASSAGE,),
            quotations=(Quotation(observation_id=PASSAGE, text="Thus ended the Test Commonwealth"),),
            qualifier_quotations=(QualifierQuotation(observation_id=PASSAGE, supports="time",
                                                     text="which had lasted from 509 to 27 B.C."),),
            time=TimeQualifier(source_expression="from 509 to 27 B.C.", edtf="-0508/-0026", calendar="julian",
                               normalization_basis="source"),
            mode="attributed", attributed_to="chr:entity:test-work",
            rationale="The passage gives the period's bounds.", proposed_by="test")
        submission = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.VALID, submission.validation.reasons)
        self.assertIn("long span: stored with its bounds, not linked to each Year", submission.validation.notes)
        stored = self.tx.run(
            "MATCH (a:Assertion {id: $id}) RETURN a.startEarliestJdn AS start, a.endLatestJdn AS end, "
            "COUNT { (a)-[:IN_YEAR]->() } AS links", id=submission.validation.assertion_id).single()
        self.assertEqual(stored["links"], 0)
        self.assertLess(stored["start"], stored["end"])

    def test_the_curator_accepts_or_rejects(self):
        period = self.propose()["id"]
        accepted = decide_entity(self.tx, self.operations, period, "provisional", None, **DECISION)
        self.assertEqual((accepted["status"], accepted["decidedBy"]), ("provisional", "test-curator"))
        with self.assertRaises(ReviewError):  # no longer proposed
            decide_entity(self.tx, self.operations, period, "deprecated", None, **DECISION)
        other = self.propose("Test Second Order")["id"]
        rejected = decide_entity(self.tx, self.operations, other, "deprecated", None, **DECISION)
        self.assertEqual(rejected["status"], "deprecated")


if __name__ == "__main__":
    unittest.main()
