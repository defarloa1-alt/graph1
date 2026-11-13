"""retire_entity_identity: a Wikidata identity naming the wrong thing is retired and the right one linked (live, rolled back)."""

import os
import unittest
from datetime import datetime, timezone
from unittest import mock

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals import review
from GraphRevised.proposals.review import ReviewError, set_entity_identity

ENTITY = "chr:entity:test-misidentified-place"
WRONG, RIGHT = "QTEST1", "QTEST2"
DECISION = {"decided_by": "test", "decision_basis": "the precinct, not the city",
            "decided_at": datetime.now(timezone.utc).isoformat()}
METADATA = {"entityLabel": "Right place", "entityDescription": "the city meant", "retrievedAt": "2026-11-12T00:00:00Z",
            "sourceUri": "https://www.wikidata.org/wiki/QTEST2", "revision": 1, "contentHash": "sha256:test"}


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs the local Neo4j")
class EntityIdentityLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase
        cls.operations = load_operations()
        cls.driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                          auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                          notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        run_write(self.tx, self.operations, "upsert_entity", {"id": ENTITY, "kind": "Place", "label": "Test Place",
                                                              "description": "the precinct", "status": "proposed",
                                                              "shortLabel": "Test Place"})
        run_write(self.tx, self.operations, "upsert_authority", {
            "entityId": ENTITY, "id": f"chr:authority:wikidata:{WRONG}", "system": "Wikidata", "identifier": WRONG,
            "label": "Wikidata record: precinct", "shortLabel": None, "description": None, "retrievedAt": None,
            "sourceUri": None, "sourceRevision": None, "contentHash": None, "rawPayloadUri": None,
            "role": "entity_identity", "relation": "closeMatch", "linkStatus": "accepted"})
        payload = review.__file__  # any file under the repository stands in for the preserved payload
        from pathlib import Path
        self.patch = mock.patch("GraphRevised.slices.add_entity.preserved_identity_payload",
                                return_value=(Path(payload), METADATA))
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tx.rollback()

    def links(self):
        return {r["q"]: r["s"] for r in self.tx.run(
            "MATCH (:Entity {id: $id})-[l:HAS_AUTHORITY_RECORD {role: 'entity_identity'}]->(a) "
            "RETURN a.identifier AS q, l.status AS s", id=ENTITY)}

    def test_the_wrong_identity_is_kept_rejected_and_the_right_one_linked(self):
        entity = set_entity_identity(self.tx, self.operations, ENTITY, WRONG, RIGHT, **DECISION)
        self.assertEqual(self.links(), {WRONG: "rejected", RIGHT: "accepted"})
        self.assertEqual((entity["label"], entity["status"], entity["description"]),
                         ("Test Place", "proposed", "the city meant"))
        basis = self.tx.run("MATCH (:Entity {id: $id})-[l]->(:AuthorityRecord {identifier: $q}) RETURN l.decisionBasis AS b",
                            id=ENTITY, q=WRONG).single()["b"]
        self.assertEqual(basis, "the precinct, not the city")
        set_entity_identity(self.tx, self.operations, ENTITY, WRONG, RIGHT, **DECISION)  # a retry changes nothing
        self.assertEqual(self.links(), {WRONG: "rejected", RIGHT: "accepted"})

    def test_an_identity_the_entity_does_not_hold_is_refused(self):
        with self.assertRaises(ReviewError):
            set_entity_identity(self.tx, self.operations, ENTITY, "QTEST9", RIGHT, **DECISION)
        with self.assertRaises(ReviewError):
            set_entity_identity(self.tx, self.operations, ENTITY, WRONG, WRONG, **DECISION)


if __name__ == "__main__":
    unittest.main()
