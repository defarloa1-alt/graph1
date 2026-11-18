"""Reading a Getty AAT chain of broader concepts (45, D-160). Offline."""
import unittest

from GraphRevised.harvest.getty_aat import chain, record_text, type_id

C, G, H = ("http://vocab.getty.edu/ontology#Concept", "http://vocab.getty.edu/ontology#GuideTerm",
           "http://vocab.getty.edu/ontology#Hierarchy")


def row(c, label, kind, parent=None, note=None):
    b = {"c": {"value": f"http://vocab.getty.edu/aat/{c}"}, "label": {"value": label}, "type": {"value": kind}}
    if parent:
        b["parent"] = {"value": f"http://vocab.getty.edu/aat/{parent}"}
    if note:
        b["note"] = {"value": note}
    return b


SILVER = [row("1", "silver (metal)", C, "2", "Pure metallic element"), row("2", "<silver, silver compounds, alloys>", G, "3"),
          row("3", "nonferrous metal", C, "4"), row("4", "Materials (hierarchy name)", H, "5")]


class AatChainTests(unittest.TestCase):
    def test_guide_terms_are_passed_over_and_the_hierarchy_ends_the_chain(self):
        found = chain(SILVER, "1")
        self.assertEqual([c["id"] for c in found], ["1", "3"])
        self.assertEqual(found[0]["broader"], "3")
        self.assertEqual(found[0]["through"], ["<silver, silver compounds, alloys>"])
        self.assertIsNone(found[1]["broader"])

    def test_the_broader_line_names_the_heading_passed_over(self):
        text, broader = record_text(chain(SILVER, "1")[0])
        self.assertEqual(broader, "Broader: nonferrous metal (AAT 3) (under the heading <silver, silver compounds, alloys>)")
        self.assertIn(broader, text)
        self.assertIsNone(record_text(chain(SILVER, "1")[1])[1])

    def test_type_ids(self):
        self.assertEqual(type_id("coins (money)"), "chr:entity:type-coins-money")


if __name__ == "__main__":
    unittest.main()
