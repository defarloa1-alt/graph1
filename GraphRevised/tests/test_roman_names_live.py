"""Registry v20 (46): a Group's category and a Person's name parts (live, rolled back)."""

import os
import unittest

from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised import localdb

PERSON, GROUP, AUTHORITY = "chr:entity:test-roman-person", "chr:entity:test-gens", "chr:authority:test-roman-names"
DECISION = {"decidedAt": "2026-11-19T00:00:00Z", "decidedBy": "test", "decisionBasis": "a test"}


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs the local Neo4j")
class RomanNamesLiveTests(unittest.TestCase):
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
        for id_, kind, label in ((PERSON, "Person", "Lucius Testus Scarpus"), (GROUP, "Group", "gens Testia")):
            run_write(self.tx, self.operations, "upsert_entity", {"id": id_, "kind": kind, "label": label,
                                                                  "description": None, "status": "proposed",
                                                                  "shortLabel": None})
        self.tx.run("""CREATE (:AuthorityRecord {id: $id, system: 'Wikidata', identifier: 'Q0', status: 'accepted',
                                                 label: 'Wikidata record: test (Q0)', sourceRevision: 42})""", id=AUTHORITY)

    def tearDown(self):
        self.tx.rollback()

    def category(self, category, entity=GROUP):
        return run_write(self.tx, self.operations, "set_group_category", {
            "id": entity, "category": category, "allowedCategories": sorted(self.registry.group_categories),
            **DECISION})[0]["group"]

    def test_a_group_is_a_gens_with_who_and_why(self):
        group = self.category("gens")
        self.assertEqual((group["groupCategory"], group["groupCategorySetBy"]), ("gens", "test"))
        with self.assertRaises(RefusedWrite):
            self.category("legion")  # not in the registry
        with self.assertRaises(RefusedWrite):
            self.category("gens", entity=PERSON)  # not a Group

    def test_name_parts_are_words_on_the_person_with_their_source(self):
        person = run_write(self.tx, self.operations, "set_name_parts", {
            "id": PERSON, "sourceId": AUTHORITY, "praenomen": "Lucius", "nomen": "Testus",
            "cognomen": "Scarpus", "agnomen": None, "decidedAt": DECISION["decidedAt"], "decidedBy": "rule"})[0]["person"]
        self.assertEqual((person["praenomen"], person["nomen"], person["cognomen"]), ("Lucius", "Testus", "Scarpus"))
        self.assertNotIn("agnomen", person)
        self.assertEqual(person["nameSource"], "Wikidata record: test (Q0) revision 42")
        with self.assertRaises(RefusedWrite):
            run_write(self.tx, self.operations, "set_name_parts", {
                "id": GROUP, "sourceId": AUTHORITY, "praenomen": "x", "nomen": None, "cognomen": None,
                "agnomen": None, "decidedAt": DECISION["decidedAt"], "decidedBy": "rule"})


if __name__ == "__main__":
    unittest.main()
