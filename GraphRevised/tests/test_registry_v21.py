"""Registry v21: Law and Decree kinds, the assembly category, patronOf (D-171, 48 §4); adoptedBy and
heldPosition's role and context (D-170). Offline."""
import unittest

from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry

EXTENDED = {
    # predicate: (end, kinds added)
    "occurred": ("subject", {"Law", "Decree"}),
    "resultedIn": ("object", {"Law", "Decree"}),
    "involvedIn": ("subject", {"Law", "Decree"}),
    "instanceOf": ("subject", {"Decree"}),
    "about": ("object", {"Law", "Decree"}),
}


class RegistryV21Tests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry(REGISTRY_PATH.with_name("predicates.v21.json"))  # pinned: v22 is current (D-180)
        self.old = load_registry(REGISTRY_PATH.with_name("predicates.v20.json"))

    def test_kinds_and_categories(self):
        self.assertEqual(self.registry.version, "predicates-v21")
        self.assertEqual(set(self.registry.entity_kinds) - set(self.old.entity_kinds), {"Law", "Decree"})
        self.assertEqual(self.registry.group_categories, frozenset({"gens", "assembly"}))

    def test_patron_of(self):
        patron = self.registry.get("patronOf")
        self.assertTrue(patron.allows_kinds("Person", "Person"))
        self.assertTrue(patron.allows_kinds("Person", "Polity"))  # a town or community as client
        self.assertFalse(patron.allows_kinds("Group", "Person"))
        self.assertEqual(patron.qualifiers.time, "required")
        self.assertFalse(patron.symmetric)
        self.assertEqual(patron.wikidata, ())
        self.assertIsNone(self.registry.get("clientOf"))  # the same claim read from the object

    def test_only_patron_of_and_adopted_by_are_new(self):
        self.assertEqual(set(self.registry.predicates) - set(self.old.predicates), {"patronOf", "adoptedBy"})

    def test_adopted_by(self):
        adopted = self.registry.get("adoptedBy")
        self.assertTrue(adopted.allows_kinds("Person", "Person"))
        self.assertEqual((adopted.qualifiers.role, adopted.qualifiers.time), ("optional", "required"))
        self.assertEqual(self.registry.role_kinds(adopted), frozenset({"Type"}))  # adoptio, adrogatio, by will
        self.assertEqual(self.registry.get("childOf"), self.old.get("childOf"))  # birth stays childOf

    def test_held_position_takes_a_role_and_a_province(self):
        new, old = self.registry.get("heldPosition"), self.old.get("heldPosition")
        self.assertEqual((old.qualifiers.role, old.qualifiers.context), ("none", "none"))
        self.assertEqual((new.qualifiers.role, new.qualifiers.context, new.qualifiers.time),
                         ("optional", "optional", "required"))
        self.assertEqual(self.registry.role_kinds(new), frozenset({"Type"}))  # suffect, pro consule
        self.assertEqual(new.context_kinds, frozenset({"Place", "Polity"}))
        self.assertEqual((new.subject_kinds, new.object_kinds, new.wikidata),
                         (old.subject_kinds, old.object_kinds, old.wikidata))

    def test_extensions_only_add_kinds(self):
        for name, definition in self.old.predicates.items():
            new = self.registry.get(name)
            if name == "heldPosition":  # D-170, tested above
                continue
            if name not in EXTENDED:
                self.assertEqual(new, definition, name)
                continue
            end, added = EXTENDED[name]
            old_kinds, new_kinds = ((definition.subject_kinds, new.subject_kinds) if end == "subject"
                                    else (definition.object_kinds, new.object_kinds))
            self.assertEqual(new_kinds - old_kinds, added, name)
            self.assertEqual(new.qualifiers, definition.qualifiers, name)
            self.assertEqual(new.modes, definition.modes, name)

    def test_a_law_in_its_events(self):
        self.assertTrue(self.registry.get("occurred").allows_kinds("Law", None))  # its span in force
        self.assertTrue(self.registry.get("resultedIn").allows_kinds("Event", "Decree"))
        involved = self.registry.get("involvedIn")
        self.assertTrue(involved.allows_kinds("Law", "Event"))
        self.assertEqual(involved.qualifiers.role, "required")  # vetoed, repealed: a role, never bare
        self.assertFalse(self.registry.get("participatedIn").allows_kinds("Law", "Event"))  # agents only
        self.assertTrue(self.registry.get("instanceOf").allows_kinds("Decree", "Type"))
        self.assertFalse(self.registry.get("instanceOf").allows_kinds("Law", "Type"))


if __name__ == "__main__":
    unittest.main()
