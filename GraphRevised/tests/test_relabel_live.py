"""Renaming an entity rebuilds the labels of the claims that name it (live, rolled back)."""

import os
import unittest

from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.relabel import refresh_claim_labels, rename_entity
from GraphRevised.proposals.store import ReviewError
from GraphRevised import localdb

PERSON = "chr:entity:test-relabel-person"
EVENT = "chr:entity:test-relabel-event"
CLAIM = "chr:assertion:test-relabel:participated-in"
PROPOSAL = "chr:proposal:test-relabel:participated-in:1"
DECISION = {"decided_by": "test", "decision_basis": "a test", "decided_at": "2026-11-19T00:00:00Z"}


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs the local Neo4j")
class RelabelLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase
        cls.operations, cls.registry = load_operations(), load_registry()
        cls.driver = GraphDatabase.driver(localdb.uri(),
                                          auth=localdb.auth(),
                                          notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=localdb.database())

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        for id_, kind, label, short in ((PERSON, "Person", "Lucius Testus", "Lucius Testus"),
                                        (EVENT, "Event", "Test battle", None)):
            run_write(self.tx, self.operations, "upsert_entity", {"id": id_, "kind": kind, "label": label,
                                                                  "description": None, "status": "proposed",
                                                                  "shortLabel": short})
        run_write(self.tx, self.operations, "upsert_assertion", {
            "id": CLAIM, "label": "Lucius Testus participated in Test battle", "shortLabel": "Lucius Testus -> Test battle",
            "predicate": "participatedIn", "category": "test", "assertedBy": "test",
            "subjectId": PERSON, "objectId": EVENT})
        self.tx.run("""MATCH (a:Assertion {id: $claim})
                       CREATE (:Proposal {id: $id, operation: 'create', label: 'Proposal to accept: old', status: 'submitted',
                                          createdBy: 'test', rationale: 'test', draftSchemaVersion: 'test',
                                          predicateRegistryVersion: 'test', shortLabel: 'old'})-[:PROPOSES]->(a)""",
                    claim=CLAIM, id=PROPOSAL)

    def tearDown(self):
        self.tx.rollback()

    def claim(self):
        return self.tx.run("""MATCH (p:Proposal)-[:PROPOSES]->(a:Assertion {id: $id})
                              RETURN a.label AS label, a.shortLabel AS short, p.label AS proposal""", id=CLAIM).single()

    def test_a_rename_rebuilds_its_claims_labels_without_doubling_a_kept_name(self):
        report = rename_entity(self.tx, self.operations, self.registry, PERSON,
                               label="Lucius Testus Scarpus", short_label="Testus Scarpus", **DECISION)
        self.assertTrue(report["renamed"])
        self.assertEqual([c["id"] for c in report["relabelled"]], [CLAIM])
        claim = self.claim()
        self.assertEqual(claim["label"], "Lucius Testus Scarpus participated in Test battle")
        self.assertEqual(claim["short"], "Testus Scarpus -> Test battle")
        self.assertEqual(claim["proposal"], "Proposal to accept: Lucius Testus Scarpus participated in Test battle")

        # The old name is part of the new: a second refresh changes nothing (no "Scarpus Scarpus").
        self.assertEqual(refresh_claim_labels(self.tx, self.operations, self.registry, [CLAIM])["relabelled"], [])
        history = self.tx.run("MATCH (e:Entity {id: $id}) RETURN e.labelHistory AS h", id=PERSON).single()["h"]
        self.assertEqual(len(history), 1)
        self.assertIn("Lucius Testus (Lucius Testus) -> Lucius Testus Scarpus (Testus Scarpus) | a test", history[0])

    def test_a_retry_records_nothing_new(self):
        rename_entity(self.tx, self.operations, self.registry, PERSON, short_label="Testus", **DECISION)
        again = rename_entity(self.tx, self.operations, self.registry, PERSON, short_label="Testus", **DECISION)
        self.assertFalse(again["renamed"])
        history = self.tx.run("MATCH (e:Entity {id: $id}) RETURN e.labelHistory AS h", id=PERSON).single()["h"]
        self.assertEqual(len(history), 1)

    def test_a_rename_needs_a_name_and_a_basis(self):
        with self.assertRaises(ReviewError):
            rename_entity(self.tx, self.operations, self.registry, PERSON, **DECISION)
        with self.assertRaises(RefusedWrite):
            rename_entity(self.tx, self.operations, self.registry, PERSON, label="X",
                          **(DECISION | {"decision_basis": " "}))


if __name__ == "__main__":
    unittest.main()
