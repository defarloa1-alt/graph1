"""set_entity_kind: an entity filed under the wrong kind moves to another (live, rolled back)."""

import os
import unittest
from datetime import datetime, timezone

from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.review import ReviewError, set_entity_kind
from GraphRevised import localdb

ENTITY = "chr:entity:test-misfiled-status"
DECISION = {"decided_by": "test", "decision_basis": "a status, not a post",
            "decided_at": datetime.now(timezone.utc).isoformat()}


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs the local Neo4j")
class EntityKindLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase
        cls.operations = load_operations()
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
        run_write(self.tx, self.operations, "upsert_entity", {"id": ENTITY, "kind": "Office", "label": "test status",
                                                              "description": None, "status": "proposed", "shortLabel": None})

    def tearDown(self):
        self.tx.rollback()

    def labels(self):
        return set(self.tx.run("MATCH (e:Entity {id: $id}) RETURN labels(e) AS l", id=ENTITY).single()["l"])

    def test_the_kind_moves_and_the_old_kind_is_recorded(self):
        entity = set_entity_kind(self.tx, self.operations, ENTITY, "Office", "Type", **DECISION)
        self.assertEqual(self.labels(), {"Entity", "Type"})
        self.assertEqual((entity["previousKind"], entity["kindChangedBy"]), ("Office", "test"))
        set_entity_kind(self.tx, self.operations, ENTITY, "Office", "Type", **DECISION)  # a retry changes nothing
        self.assertEqual(self.labels(), {"Entity", "Type"})

    def test_a_cited_work_stays_a_work(self):
        work = "chr:entity:test-cited-work"
        run_write(self.tx, self.operations, "upsert_entity", {"id": work, "kind": "Work", "label": "test thesaurus",
                                                              "description": None, "status": "proposed", "shortLabel": None})
        self.tx.run("MATCH (w:Entity {id: $id}) CREATE (:SourceObservation {id: 'chr:observation:test-cited'})-[:IN_WORK]->(w)",
                    id=work)
        with self.assertRaises(ReviewError):
            set_entity_kind(self.tx, self.operations, work, "Work", "Group", **DECISION)
        set_entity_kind(self.tx, self.operations, ENTITY, "Office", "Work", **DECISION)  # moving to Work is allowed
        self.assertEqual(self.labels(), {"Entity", "Work"})

    def test_a_wrong_expected_kind_is_refused(self):
        with self.assertRaises(ReviewError):
            set_entity_kind(self.tx, self.operations, ENTITY, "Person", "Type", **DECISION)
        self.assertEqual(self.labels(), {"Entity", "Office"})

    def test_an_open_claim_blocks_the_move(self):
        self.tx.run("MATCH (e:Entity {id: $id}) CREATE (:Assertion {id: 'chr:assertion:test-open', status: 'proposed'})"
                    "-[:ASSERTION_OBJECT]->(e)", id=ENTITY)
        with self.assertRaises(ReviewError):
            set_entity_kind(self.tx, self.operations, ENTITY, "Office", "Type", **DECISION)
        self.tx.run("MATCH (a:Assertion) WHERE a.id STARTS WITH 'chr:assertion:test-open' SET a.status = 'rejected'")
        set_entity_kind(self.tx, self.operations, ENTITY, "Office", "Type", **DECISION)
        self.assertEqual(self.labels(), {"Entity", "Type"})

    def test_upsert_cannot_quietly_file_it_back(self):
        set_entity_kind(self.tx, self.operations, ENTITY, "Office", "Type", **DECISION)
        with self.assertRaises(RefusedWrite):
            run_write(self.tx, self.operations, "upsert_entity", {"id": ENTITY, "kind": "Office", "label": None,
                                                                  "description": None, "status": None, "shortLabel": None})


if __name__ == "__main__":
    unittest.main()
