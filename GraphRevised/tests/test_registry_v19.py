"""Registry v19 (45, D-160): colour, and a Question about a Type. Offline."""
import unittest

from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry


class RegistryV19Tests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.old = load_registry(REGISTRY_PATH.with_name("predicates.v18.json"))

    def test_colour(self):
        self.assertEqual(self.registry.version, "predicates-v19")
        self.assertIn("colour", self.registry.type_categories)
        self.assertTrue(self.registry.get("hadColour").allows_kinds("Object", "Type"))
        self.assertFalse(self.registry.get("hadColour").allows_kinds("Type", "Type"))  # an object's, not a kind's

    def test_a_question_may_be_about_a_type(self):
        self.assertTrue(self.registry.get("about").allows_kinds("Question", "Type"))
        self.assertFalse(self.old.get("about").allows_kinds("Question", "Type"))

    def test_only_about_changed(self):
        for name, definition in self.old.predicates.items():
            if name != "about":
                self.assertEqual(self.registry.get(name), definition, name)


if __name__ == "__main__":
    unittest.main()
