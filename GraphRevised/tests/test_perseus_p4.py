"""Older Perseus files: undeclared HTML entities and TEI P4 (45 §5.2, Pliny). Offline."""
import unittest
import xml.etree.ElementTree as ET

from GraphRevised.adapters.perseus_passages import TEI, from_tei_p4, resolve_entities

P4 = b"""<?xml version="1.0"?><TEI.2><teiHeader><fileDesc><titleStmt><title>The Natural History</title>
<editor>John Bostock</editor></titleStmt></fileDesc></teiHeader><text lang="en"><body>
<div1 type="book" n="19"><div2 type="chapter" n="5"><p>sails of purple&mdash;87&cdot;9 &amp; more</p></div2></div1>
</body></text></TEI.2>"""


class PerseusP4Tests(unittest.TestCase):
    def test_entities_are_resolved_and_xml_s_own_kept(self):
        payload, replaced = resolve_entities(P4)
        self.assertEqual(replaced, ["cdot", "mdash"])
        self.assertIn("purple—879".replace("879", "87·9"), payload.decode("utf-8"))  # cdot is a decimal point
        self.assertIn("&amp;", payload.decode("utf-8"))

    def test_p4_becomes_the_p5_shape(self):
        root = ET.fromstring(from_tei_p4(resolve_entities(P4)[0], "urn:cts:latinLit:phi0978.phi001.perseus-eng1"))
        edition = root.find(f".//{TEI}body/{TEI}div")
        self.assertEqual(edition.get("n"), "urn:cts:latinLit:phi0978.phi001.perseus-eng1")
        self.assertEqual([d.get("n") for d in edition.iter(f"{TEI}div")], ["urn:cts:latinLit:phi0978.phi001.perseus-eng1", "19", "5"])
        self.assertEqual(root.find(f".//{TEI}titleStmt/{TEI}editor").get("role"), "translator")
        self.assertEqual(root.find(f".//{TEI}text").get("{http://www.w3.org/XML/1998/namespace}lang"), "en")

    def test_a_p5_file_is_left_alone(self):
        self.assertIsNone(from_tei_p4(b'<TEI xmlns="http://www.tei-c.org/ns/1.0"/>', "urn:x"))


if __name__ == "__main__":
    unittest.main()
