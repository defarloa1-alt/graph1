"""Registry v22: commemorates and depicts (D-180, doc 49). Offline."""
import unittest

from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry


class RegistryV22Tests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.old = load_registry(REGISTRY_PATH.with_name("predicates.v21.json"))

    def test_only_the_two_memory_predicates_are_new(self):
        self.assertEqual(self.registry.version, "predicates-v22")
        self.assertEqual(set(self.registry.predicates) - set(self.old.predicates), {"commemorates", "depicts"})
        self.assertEqual(set(self.registry.entity_kinds), set(self.old.entity_kinds))
        for name, definition in self.old.predicates.items():
            self.assertEqual(self.registry.get(name), definition)

    def test_commemorates_reaches_events_and_people_from_things_of_their_time(self):
        c = self.registry.get("commemorates")
        self.assertTrue(c.allows_kinds("Object", "Event"))  # a relief, a gem, a monument
        self.assertTrue(c.allows_kinds("Work", "Event"))  # a coinage
        self.assertTrue(c.allows_kinds("Event", "Person"))  # games founded in someone's honour
        self.assertFalse(c.allows_kinds("Person", "Event"))
        self.assertEqual(c.category, "interpretive")
        self.assertEqual([w.pid for w in c.wikidata], ["P547"])

    def test_depicts_says_what_a_work_shows_and_vouches_for_nothing(self):
        d = self.registry.get("depicts")
        self.assertTrue(d.allows_kinds("Work", "Event"))
        self.assertTrue(d.allows_kinds("Object", "Person"))
        self.assertFalse(d.allows_kinds("Event", "Event"))
        self.assertEqual(d.category, "interpretive")
        self.assertEqual([w.pid for w in d.wikidata], ["P180"])

    def test_a_painting_stays_imaginative_and_an_object_is_not_a_creative_form(self):
        self.assertIn("painting", self.registry.creative_forms)
        self.assertEqual(self.registry.creative_forms, self.old.creative_forms)


if __name__ == "__main__":
    unittest.main()
