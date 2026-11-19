"""set_type_category: a Type's category comes from the registry, with who set it and why (live, rolled back)."""

import os
import unittest

from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.registry import load_registry

TYPE = "chr:entity:test-type-category"


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs the local Neo4j")
class TypeCategoryLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase
        cls.operations, cls.registry = load_operations(), load_registry()
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
        run_write(self.tx, self.operations, "upsert_entity", {"id": TYPE, "kind": "Type", "label": "test type",
                                                              "description": None, "status": "proposed", "shortLabel": None})

    def tearDown(self):
        self.tx.rollback()

    def set(self, category, entity=TYPE, at="2026-11-13T00:00:00Z", basis="a test"):
        return run_write(self.tx, self.operations, "set_type_category", {
            "id": entity, "category": category, "allowedCategories": sorted(self.registry.type_categories),
            "decidedAt": at, "decidedBy": "test", "decisionBasis": basis})[0]["type"]

    def test_the_registry_lists_the_categories(self):
        self.assertEqual(self.registry.type_categories,
                         {"role", "unit type", "organizational pattern", "power", "status", "ship type", "naval fitting",
                          # registry v18-v19 (45, D-160): natural kinds and materials
                          "material", "denomination", "product", "taxon", "colour"})

    def test_an_unknown_category_or_a_non_type_is_refused(self):
        with self.assertRaises(RefusedWrite):
            self.set("rumour")
        self.tx.run("CREATE (:Entity:Office {id: 'chr:entity:test-not-a-type', kind: 'Office'})")
        with self.assertRaises(RefusedWrite):
            self.set("role", entity="chr:entity:test-not-a-type")

    def test_a_change_keeps_what_it_replaced_and_a_retry_changes_nothing(self):
        first = self.set("role")
        self.assertEqual((first["typeCategory"], first["typeCategorySetBy"]), ("role", "test"))
        self.assertIsNone(first.get("typeCategoryPrevious"))
        changed = self.set("status", at="2026-11-14T00:00:00Z", basis="a standing, not a part played")
        self.assertEqual((changed["typeCategory"], changed["typeCategoryPrevious"]), ("status", "role"))
        retry = self.set("status", at="2026-11-15T00:00:00Z", basis="again")
        self.assertEqual((retry["typeCategorySetAt"], retry["typeCategoryBasis"]),
                         ("2026-11-14T00:00:00Z", "a standing, not a part played"))


if __name__ == "__main__":
    unittest.main()
