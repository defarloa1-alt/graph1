"""The Library of Congress catalog adapter, without the network: identifiers and a MARCXML record read."""

import unittest

from GraphRevised.adapters.lc_catalog import CatalogError, isbn_valid, normalize_lccn, parse_record

# A synthetic record in LC's shape (an SRU response around one MARCXML record); not a real book.
SRU = b"""<?xml version="1.0"?>
<zs:searchRetrieveResponse xmlns:zs="http://www.loc.gov/zing/srw/"><zs:numberOfRecords>1</zs:numberOfRecords>
<zs:records><zs:record><zs:recordData><record xmlns="http://www.loc.gov/MARC21/slim">
  <controlfield tag="001">99999999</controlfield>
  <controlfield tag="005">20250101000000.0</controlfield>
  <controlfield tag="008">210101s2022    nyua     b    001 0deng  </controlfield>
  <datafield tag="010" ind1=" " ind2=" "><subfield code="a">  2099000001</subfield></datafield>
  <datafield tag="020" ind1=" " ind2=" "><subfield code="a">9780306406157</subfield><subfield code="q">(hardcover)</subfield></datafield>
  <datafield tag="020" ind1=" " ind2=" "><subfield code="z">9780000000002</subfield><subfield code="q">(ebook)</subfield></datafield>
  <datafield tag="050" ind1="0" ind2="0"><subfield code="a">DG999</subfield><subfield code="b">.T47 2022</subfield></datafield>
  <datafield tag="082" ind1="0" ind2="0"><subfield code="a">937/.99</subfield><subfield code="2">23</subfield></datafield>
  <datafield tag="100" ind1="1" ind2=" "><subfield code="a">Tester, Ann B.,</subfield><subfield code="e">author.</subfield></datafield>
  <datafield tag="245" ind1="1" ind2="4"><subfield code="a">The test of a war :</subfield><subfield code="b">a history /</subfield><subfield code="c">by Ann Tester.</subfield></datafield>
  <datafield tag="250" ind1=" " ind2=" "><subfield code="a">First edition.</subfield></datafield>
  <datafield tag="264" ind1=" " ind2="1"><subfield code="a">New York :</subfield><subfield code="b">Test House,</subfield><subfield code="c">2022.</subfield></datafield>
  <datafield tag="300" ind1=" " ind2=" "><subfield code="a">300 pages :</subfield><subfield code="b">illustrations ;</subfield><subfield code="c">24 cm</subfield></datafield>
  <datafield tag="504" ind1=" " ind2=" "><subfield code="a">Includes bibliographical references (pages 280-290) and index.</subfield></datafield>
  <datafield tag="505" ind1="0" ind2=" "><subfield code="a">The Start -- The Middle -- "A Quoted Title" -- The End.</subfield></datafield>
  <datafield tag="520" ind1=" " ind2=" "><subfield code="a">"A gripping story."</subfield><subfield code="c">Provided by publisher.</subfield></datafield>
  <datafield tag="600" ind1="1" ind2="0"><subfield code="a">Testus, Marcus,</subfield><subfield code="d">83 B.C.?-30 B.C.</subfield></datafield>
  <datafield tag="650" ind1=" " ind2="0"><subfield code="a">Testium, Battle of, 31 B.C.</subfield></datafield>
  <datafield tag="651" ind1=" " ind2="0"><subfield code="a">Testland</subfield><subfield code="x">History</subfield><subfield code="y">Civil War, 43-31 B.C.</subfield></datafield>
  <datafield tag="650" ind1=" " ind2="7"><subfield code="a">Naval battles</subfield><subfield code="2">fast</subfield></datafield>
</record></zs:recordData></zs:record></zs:records></zs:searchRetrieveResponse>"""


class IdentifierTests(unittest.TestCase):
    def test_isbn_check_digits(self):
        self.assertTrue(isbn_valid("978-0-306-40615-7"))
        self.assertTrue(isbn_valid("978-03064-0615-7"))  # hyphens anywhere
        self.assertFalse(isbn_valid("978-0-306-40615-8"))
        self.assertTrue(isbn_valid("0-306-40615-2"))
        self.assertFalse(isbn_valid("12345"))

    def test_lccn_normalization(self):
        self.assertEqual(normalize_lccn("  2021007113 "), "2021007113")
        self.assertEqual(normalize_lccn("2021-7113"), "2021007113")
        self.assertEqual(normalize_lccn("n78-890351/rev"), "n78890351")
        with self.assertRaises(CatalogError):
            normalize_lccn("not an lccn")


class RecordTests(unittest.TestCase):
    record = parse_record(SRU)

    def test_identifiers_and_call_numbers(self):
        r = self.record
        self.assertEqual((r.lccn, r.lcc, r.ddc, r.ddc_edition), ("2099000001", "DG999 .T47 2022", "937/.99", "23"))
        self.assertEqual(r.isbn_qualifier("978-0-306-40615-7"), "(hardcover)")
        self.assertEqual(r.isbns[1], ("9780000000002", "(ebook)", True))  # $z: an ISBN given as cancelled or invalid

    def test_title_author_and_publication(self):
        r = self.record
        self.assertEqual(r.title, "The test of a war : a history")
        self.assertEqual(r.responsibility, "by Ann Tester")
        self.assertEqual((r.names[0].text, r.names[0].relator), ("Tester, Ann B.", "author"))
        self.assertEqual(r.publication, "New York : Test House, 2022")
        self.assertEqual(r.edition, "First edition")

    def test_headings_in_lc_display_form(self):
        lcsh = [(s.tag, s.text, s.dates) for s in self.record.subjects if s.thesaurus == "lcsh"]
        self.assertEqual(lcsh, [("600", "Testus, Marcus, 83 B.C.?-30 B.C.", "83 B.C.?-30 B.C."),
                                ("650", "Testium, Battle of, 31 B.C.", None),
                                ("651", "Testland--History--Civil War, 43-31 B.C.", None)])
        self.assertEqual([s.thesaurus for s in self.record.subjects if s.thesaurus != "lcsh"], ["fast"])

    def test_contents_notes_and_the_publishers_words_kept_apart(self):
        r = self.record
        self.assertEqual(r.contents, ("The Start", "The Middle", '"A Quoted Title"', "The End"))
        self.assertTrue(r.has_index)
        self.assertEqual(r.language, "eng")
        self.assertIn("280-290", r.bibliography_note)
        self.assertEqual(r.publisher_summary, '"A gripping story."')

    def test_a_record_without_an_lccn_is_refused(self):
        with self.assertRaises(CatalogError):
            parse_record(SRU.replace(b'<subfield code="a">  2099000001</subfield>', b""))


if __name__ == "__main__":
    unittest.main()
