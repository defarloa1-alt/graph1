"""LacusCurtius pages to passage observations, on a synthetic page (no network)."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from GraphRevised.adapters import lacuscurtius_passages as lc
from GraphRevised.adapters.sources import open_source

URL = "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Test_Author/7*.html"
PAGE = """<HTML><BODY>
<P>This webpage reproduces a Book of Test History by Test Author published in Vol. I of the Loeb Classical
Library edition, 1917 The text is in the public domain. This text has not yet been proofread.</P>
<P CLASS="justify"><SPAN CLASS="pagenum"> p101 </SPAN>
<A CLASS="chapter" NAME="1">1</A>
The fleet sailed out at dawn<A CLASS="ref" ID="ref1" HREF=" E/x*.html#note1 ">1</A>⁠ and waited.
<A CLASS="sec" NAME="1.2">2</A> On the second of September they fought.
<P CLASS="justify"><A CLASS="chapter" NAME="2">2</A>
<A CLASS="sec" NAME="2.1">1</A> The admiral fled.
<HR CLASS="endnotes"><A ID="endnotes"></A><H2>The Loeb Editor's Notes:</H2>
<P CLASS="justify"><A CLASS="note" ID="note1" HREF=" E/x*.html#ref1 ">1</A> An editor's remark about dawn.
<P CLASS="ivy">x</P>
<P>Page updated: 17 Jun 11</P>
</BODY></HTML>"""


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        pass


class LacusCurtiusTests(unittest.TestCase):
    def setUp(self):
        # Observations record payload paths relative to the repository, so the
        # synthetic page lives in the git-ignored cache directory.
        cache = Path(__file__).resolve().parents[1] / "cache"
        cache.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=cache)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        with mock.patch.object(lc.requests, "get", return_value=FakeResponse(PAGE.encode("utf-8"))):
            self.path = lc.preserve_page(URL, self.directory)
        self.edition = lc.load_edition([self.path], translator="Test Translator")

    def test_page_is_preserved_with_rights_and_hash(self):
        metadata = json.loads(self.path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["contentHash"], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(metadata["publicDomainStatement"], "The text is in the public domain.")
        self.assertFalse(metadata["proofread"])
        self.assertEqual(metadata["pageUpdated"], "17 Jun 11")

    def test_only_public_domain_pages_are_fetched(self):
        with self.assertRaises(ValueError):
            lc.preserve_page(URL.replace("*", "**"), self.directory)

    def test_sections_exclude_page_numbers_markers_and_notes(self):
        self.assertEqual(self.edition.all_refs(), ["7.1.1", "7.1.2", "7.2.1"])
        first = lc.passage_observation(self.edition, "7.1.1")
        self.assertEqual(first["passageText"], "The fleet sailed out at dawn and waited.")
        self.assertEqual(first["editorialNotes"], ["An editor's remark about dawn."])
        self.assertEqual(first["locator"], URL + "#1.1")
        self.assertEqual(lc.passage_observation(self.edition, "7.2.1")["editorialNotes"], [])

    def test_citation_comes_from_the_page(self):
        self.assertEqual((self.edition.author, self.edition.title), ("Test Author", "Test History"))
        self.assertIn("trans. Test Translator", self.edition.citation)
        self.assertIn("1917", self.edition.citation)

    def test_selection_and_identity(self):
        self.assertEqual(lc.section_refs(self.edition, "7.2-7.2"), ["7.2.1"])
        observation = lc.passage_observation(self.edition, "7.1.2")
        self.assertTrue(observation["id"].startswith("chr:observation:lacuscurtius:test-author:7.1.2:"))
        with self.assertRaises(lc.PassageNotFound):
            lc.passage_observation(self.edition, "7.9.9")

    def test_a_changed_payload_is_refused(self):
        self.path.write_bytes(self.path.read_bytes() + b" ")
        with self.assertRaises(ValueError):
            lc.load_edition([self.path])

    def test_source_interface_selects_the_adapter(self):
        source = open_source({"type": "lacuscurtius-html", "pages": [self.path.name], "chapters": "7.1-7.1"},
                             self.directory)
        self.assertEqual(source.refs("7.1-7.1"), ["7.1.1", "7.1.2"])
        self.assertEqual(len(source.refs(None)), 3)
        self.assertEqual(source.refs("7.2-7.2, 7.1-7.1"), ["7.1.1", "7.1.2", "7.2.1"])
        with self.assertRaises(ValueError):
            open_source({"type": "unknown"}, self.directory)


if __name__ == "__main__":
    unittest.main()
