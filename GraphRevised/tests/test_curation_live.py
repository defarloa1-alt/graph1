"""Curation manifests applied in rolled-back transactions; the database never changes."""

import os
import unittest

from GraphRevised.operations import load_operations
from GraphRevised.proposals.registry import load_registry
from GraphRevised.slices.apply_curation import SNAPSHOT, apply_manifest

MANIFEST = {
    "localEntities": [
        {"id": "chr:entity:test-curation-fleet", "kind": "Group", "label": "Test fleet",
         "description": "Local analytical entity for a curation test."},
        {"id": "chr:entity:test-curation-wing", "kind": "Group", "label": "Test wing",
         "description": "Local analytical entity for a curation test."},
    ],
}


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class CurationLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations, cls.registry = load_operations(), load_registry()
        cls.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
            notifications_min_severity="OFF",
        )
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()

    def tearDown(self):
        self.tx.rollback()

    def test_a_manifest_applies_once(self):
        summary = apply_manifest(self.tx, MANIFEST, self.operations, self.registry)
        self.assertEqual(summary["localEntities"], 2)
        labels = self.tx.run("MATCH (e:Entity) WHERE e.id STARTS WITH 'chr:entity:test-curation-' "
                             "RETURN collect(e.label) AS labels").single()["labels"]
        self.assertEqual(sorted(labels), ["Test fleet", "Test wing"])
        before = self.tx.run(SNAPSHOT).single().data()
        apply_manifest(self.tx, MANIFEST, self.operations, self.registry)
        after = self.tx.run(SNAPSHOT).single().data()
        self.assertCountEqual(after["nodes"], before["nodes"])
        self.assertCountEqual(after["relationships"], before["relationships"])


if __name__ == "__main__":
    unittest.main()
