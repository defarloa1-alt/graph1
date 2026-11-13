"""Gutenberg HTML books to passage observations, on a synthetic book (no network)."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from GraphRevised.adapters import gutenberg_passages as gb
from GraphRevised.adapters.sources import open_source

BOOK = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" />
<title>The Project Gutenberg eBook of A Test History, by Ann Author.</title></head><body>
<h1>A TEST HISTORY</h1><p>Front matter that is not a passage.</p>
<p><span class="pagenum"><a id="Page_24">24</a></span></p>
<h2><a id="CHAPTER_I"></a>CHAPTER I.<br /><span class="subhead">THE FIRST WAR.</span></h2>
<p>It began in spring.<a id="FNanchor_1" href="#Footnote_1" class="fnanchor">1</a> The fleets met at dawn and the
battle lasted until the tenth hour, when<span class="pagenum"><a id="Page_25">25</a></span> the left gave way.</p>
<p class="caption center">A plan of the battle</p>
<p>Afterwards the victor went east.</p>
<h2><a id="CHAPTER_II"></a>CHAPTER II</h2>
<p class="title">THE SECOND<br />WAR</p>
<p>A second war followed.</p>
<h2>INDEX</h2><p>Battle, 24, 25</p>
<div class="footnotes"><h2>FOOTNOTES</h2>
<div class="footnote"><p class="fn1"><a id="Footnote_1" href="#FNanchor_1" class="fnanchor">1</a> The author's own note.</p></div></div>
</body></html>"""


class GutenbergTests(unittest.TestCase):
    def setUp(self):
        cache = Path(__file__).resolve().parents[1] / "cache"
        cache.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=cache)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        payload = BOOK.encode("utf-8")
        self.path = self.directory / "gutenberg-99999-test.htm"
        self.path.write_bytes(payload)
        header = gb._header(BOOK)
        self.path.with_suffix(".metadata.json").write_text(json.dumps({
            "sourceSystem": "Project Gutenberg", "sourceUri": "https://www.gutenberg.org/files/99999/99999-h/99999-h.htm",
            "ebook": "99999", "retrievedAt": "2026-10-12T00:00:00Z", "contentHash": hashlib.sha256(payload).hexdigest(),
            **header, "rights": "Project Gutenberg catalogue: Public domain in the USA."}), encoding="utf-8")
        self.edition = gb.load_edition(self.path, edition="Test Press, 1911")

    def test_header_falls_back_to_title_and_language(self):
        header = gb._header(BOOK)
        self.assertEqual((header["title"], header["author"], header["language"]), ("A Test History", "Ann Author", "en"))

    def test_chapters_and_paragraphs_only(self):
        self.assertEqual(self.edition.all_refs(), ["1.1", "1.2", "2.1"])
        self.assertEqual(self.edition.passages["1.1"].chapter_title, "THE FIRST WAR")
        self.assertEqual(self.edition.passages["2.1"].chapter_title, "THE SECOND WAR")

    def test_pages_and_notes_kept_apart_from_the_text(self):
        passage = self.edition.passages["1.1"]
        self.assertEqual(passage.text, "It began in spring. The fleets met at dawn and the battle lasted until the "
                                       "tenth hour, when the left gave way.")
        self.assertEqual(passage.pages, ("24", "25"))
        self.assertEqual(passage.notes, ("The author's own note.",))
        observation = gb.passage_observation(self.edition, "1.1")
        self.assertTrue(observation["locator"].endswith("#Page_24 (ch. 1, para. 1, p. 24-25)"))
        self.assertIn("Test Press, 1911", observation["editionCitation"])

    def test_roman_numerals(self):
        self.assertEqual([gb._roman(n) for n in ("I", "IV", "IX", "XVII", "XL")], [1, 4, 9, 17, 40])

    def test_catalogue_authors_compare_by_surname(self):
        self.assertEqual(gb._surname("Hale, John Richard, 1876-"), gb._surname("John Richard Hale"))
        self.assertNotEqual(gb._surname("Atteridge, A. Hilliard"), gb._surname("John Richard Hale"))

    def test_source_interface(self):
        source = open_source({"type": "gutenberg-html", "book": self.path.name, "edition": "Test Press, 1911"},
                             self.directory)
        self.assertEqual(source.refs("2-2"), ["2.1"])
        self.assertEqual(len(source.refs(None)), 3)

    def test_explicit_heading_section_has_distinct_unambiguous_locators(self):
        html = ('<html lang="en"><h2 id="start">Epistle II</h2><h5>Title</h5>'
                '<p>First line.<br>Second line.</p><p>Another verse.</p><h2 id="end">Next work</h2></html>')
        payload = html.encode("utf-8")
        self.path.write_bytes(payload)
        metadata_path = self.path.with_suffix(".metadata.json")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["contentHash"] = hashlib.sha256(payload).hexdigest()
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        section = {"start": "start", "end": "end", "label": "Book II, Epistle II"}
        source = open_source({"type": "gutenberg-html", "book": self.path.name, "section": section}, self.directory)
        self.assertEqual(source.refs(None), ["1.1", "1.2"])
        obs = source.observation("1.1")
        self.assertEqual(obs["passageText"], "First line. Second line.")
        self.assertIn("#start (selected section Book II, Epistle II, para. 1)", obs["locator"])
        self.assertNotEqual(obs["id"], f"chr:observation:gutenberg:99999:1.1:{metadata['contentHash'][:8]}")

    def test_section_rejects_missing_end_intermediate_headings_and_notes(self):
        section = {"start": "s", "end": "e", "label": "test"}
        for html in ('<h2 id="s">S</h2><p>Text</p>', '<h2 id="s">S</h2><h2>Other</h2><p>Text</p><h2 id="e">E</h2>',
                     '<h2 id="s">S</h2><p>Text <a class="fnanchor">1</a></p><h2 id="e">E</h2>',
                     '<h2 id="s">S</h2><div class="footnotes"><p>Note</p></div><h2 id="e">E</h2>'):
            with self.subTest(html=html), self.assertRaises(ValueError):
                gb._section_passages(html, section)

    def test_missing_legacy_html_uses_gutenberg_current_html(self):
        old = mock.Mock(status_code=404)
        current = mock.Mock(status_code=200, content=BOOK.encode("utf-8"))
        current.raise_for_status.return_value = None
        with mock.patch.object(gb.requests, "get", side_effect=[old, current]), \
                mock.patch.object(gb, "_catalog", return_value={"copyrightStatus": "Public domain in the USA."}):
            path = gb.preserve_book(1234, self.directory)
        metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["sourceUri"], "https://www.gutenberg.org/cache/epub/1234/pg1234-images.html")


if __name__ == "__main__":
    unittest.main()
