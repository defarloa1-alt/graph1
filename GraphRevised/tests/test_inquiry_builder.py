"""The inquiry builder's and the generalised adapters' rules, without the network or the graph."""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from GraphRevised.adapters import perseus_passages
from GraphRevised.adapters.lacuscurtius_passages import REPRODUCES, REPRODUCES_UNSIGNED
from GraphRevised.discovery.inquiry_builder import build, text_pages, voice

HOME = "https://example.org/Thayer/E/Roman/Texts/Historicus/home.html"
TEI = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><titleStmt><title>Carmen</title>
<author>Poeta</author><editor role="translator">T. Translator</editor></titleStmt><sourceDesc><biblStruct><monogr>
<title>The Carmen</title><imprint><publisher>Press</publisher><date>1910</date></imprint></monogr></biblStruct>
</sourceDesc></fileDesc></teiHeader><text xml:lang="eng"><body><div type="edition">
<div n="front"><div n="1"><p>A translator's preface.</p></div></div>
<div n="1"><div n="1"><div n="1"><p>First <note>an editor's note</note>words.</p></div><div n="2"><p>Second.</p></div></div></div>
<div n="2"><div n="1"><div n="1"><p>Third.</p></div></div></div>
</div></body></text></TEI>"""


class PerseusDepthTests(unittest.TestCase):
    def edition(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "edition.xml"
        path.write_text(TEI, encoding="utf-8")
        return perseus_passages.load_edition(path, source_commit="0" * 40, cts_urn="urn:cts:latinLit:test.test.eng1")

    def test_passages_are_the_deepest_numbered_divisions(self):
        edition = self.edition()
        self.assertEqual([ref for ref, _ in perseus_passages.passages(edition)], ["1.1.1", "1.1.2", "2.1.1"])
        self.assertEqual(perseus_passages.section_refs(edition, range(2, 3)), ["2.1.1"])

    def test_the_urn_comes_from_the_metadata_when_the_edition_has_none(self):
        self.assertEqual(self.edition().cts_urn, "urn:cts:latinLit:test.test.eng1")

    def test_notes_stay_out_of_the_text(self):
        section = perseus_passages._index(self.edition())["1.1.1"]
        self.assertEqual(perseus_passages._section_text(section), ("First words.", ["an editor's note"]))

    def test_public_domain_follows_the_publication_year(self):
        today = datetime(2026, 10, 15, tzinfo=timezone.utc)
        self.assertTrue(perseus_passages.public_domain_in_us(1930, today))
        self.assertFalse(perseus_passages.public_domain_in_us(1931, today))


class LacusCurtiusTests(unittest.TestCase):
    def test_text_pages_are_numbered_public_domain_pages_of_the_work(self):
        page = ('<BASE HREF="https://example.org/Thayer/">'
                '<A HREF="\nE/Roman/Texts/Historicus/1*.html\n">Book I</A>'
                '<A HREF="E/Roman/Texts/Historicus/2A*.html">II</A>'
                '<A HREF="L/Roman/Texts/Historicus/1*.html">Liber I</A>'
                '<A HREF="E/Roman/Texts/Historicus/Introduction*.html">Introduction</A>'
                '<A HREF="E/Roman/Texts/Historicus/3**.html">Notes</A>')
        self.assertEqual(text_pages(page, HOME), ["https://example.org/Thayer/E/Roman/Texts/Historicus/1*.html",
                                                  "https://example.org/Thayer/E/Roman/Texts/Historicus/2A*.html"])

    def test_a_statement_without_an_author_is_still_read(self):
        text = ("This webpage reproduces a section of The Deeds of the Victor as published in the Loeb "
                "Classical Library, 1924 The text is in the public domain.")
        self.assertIsNone(REPRODUCES.search(text))
        match = REPRODUCES_UNSIGNED.search(text)
        self.assertEqual((match["title"], match["publication"]), ("The Deeds of the Victor", "the Loeb Classical Library, 1924"))


class BuildTests(unittest.TestCase):
    def test_a_dry_run_lists_chosen_sources_and_writes_nothing(self):
        plan = {"candidates": [
            {"status": "chosen", "author": "Poeta, Quintus", "work": "Carmen", "chosenCopy": 0, "reason": "a voice",
             "form": "poem", "composition": "c. 20 BCE", "copies": [{"label": "Perseus test", "system": "perseus"}]},
            {"status": "located", "author": "Other", "work": "Other", "copies": []}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inquiry.json"
            path.write_text('{"id": "chr:inquiry:test", "version": 1, "sources": []}', encoding="utf-8")
            report = build(path, plan, apply=False)
            self.assertEqual(path.read_text(encoding="utf-8"), '{"id": "chr:inquiry:test", "version": 1, "sources": []}')
        self.assertEqual([a["work"] for a in report["added"]], ["Poeta, Carmen"])
        self.assertEqual(voice("Poeta, Quintus"), "Poeta")


if __name__ == "__main__":
    unittest.main()
