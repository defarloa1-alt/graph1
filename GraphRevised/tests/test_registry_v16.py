"""Registry v16 and draft v7 (43 §5): the military predicates and a quantity's precision. Offline."""
import unittest

from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import QuantityQualifier


class RegistryV16Tests(unittest.TestCase):
    def test_the_military_predicates(self):
        registry = load_registry()
        strength = registry.get("hadStrength")
        self.assertTrue(strength.unary)
        self.assertEqual((strength.qualifiers.quantity, strength.qualifiers.time, strength.qualifiers.role),
                         ("required", "required", "optional"))
        self.assertEqual(registry.role_kinds(strength), frozenset({"Type"}))
        for name in ("captured", "surrenderedTo", "defectedTo"):
            self.assertEqual(registry.get(name).qualifiers.time, "required")
        self.assertTrue({"ship type", "naval fitting"} <= registry.type_categories)
        self.assertIn("coinage", registry.work_forms)
        self.assertNotIn("coinage", registry.creative_forms)

    def test_precision_is_kept_or_flagged_round_and_never_changes_the_claim(self):
        self.assertEqual(QuantityQualifier(source_expression="sixty ships", typical=60).stored_precision(), "round")
        self.assertIsNone(QuantityQualifier(source_expression="seven", typical=7).stored_precision())
        about = QuantityQualifier(source_expression="about 230", typical=230, precision="approximate")
        self.assertEqual(about.stored_precision(), "approximate")
        self.assertEqual(about.signature(), QuantityQualifier(source_expression="230", typical=230).signature())
        with self.assertRaises(ValueError):
            QuantityQualifier(source_expression="x", typical=3, precision="certain")


if __name__ == "__main__":
    unittest.main()
