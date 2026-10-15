"""Wikipedia as a source (29-EVENT-CENTRED-INQUIRY.md §5): an article's body as passages, its links
kept with the passage's own words, the apparatus left out, and the link-to-item map reused once
preserved. Offline."""

import json
import tempfile
import unittest
from pathlib import Path

from GraphRevised.adapters.wikipedia_passages import parse_html, resolve_qids

HTML = """
<div class="mw-parser-output">
<div class="hatnote">For other uses, see <a href="/wiki/Actium_(disambiguation)">Actium</a>.</div>
<table class="infobox"><tr><td><a href="/wiki/Mark_Antony">Mark Antony</a>
  <a href="/wiki/File:Map.png">map</a></td></tr></table>
<p>The battle was fought between <a href="/wiki/Octavian">Octavian</a>'s fleet and the fleets of
  <a href="/wiki/Mark_Antony">Antony</a>.<sup class="reference">[1]</sup></p>
<h2>Background<span class="mw-editsection">[edit]</span></h2>
<p>Antony wintered at <a href="/wiki/Patras">Patrae</a> with his fleet and army.</p>
<ul><li>A list item long enough to be a passage of the body.</li></ul>
<div class="navbox"><p>A navigation box paragraph that must never be read.</p></div>
<h2>References</h2>
<p>A reference paragraph that ends the body and is not a passage.</p>
</div>
"""


class WikipediaArticleTests(unittest.TestCase):
    def setUp(self):
        self.passages, self.infobox = parse_html(HTML)

    def test_body_paragraphs_by_section(self):
        self.assertEqual(list(self.passages), ["0.1", "1.1", "1.2"])
        self.assertEqual(self.passages["1.1"].section, "Background")

    def test_citation_markers_and_apparatus_are_left_out(self):
        lead = self.passages["0.1"].text
        self.assertNotIn("[1]", lead)
        self.assertIn("Octavian's fleet", lead)  # the article's own spacing, so quotations match
        texts = " ".join(p.text for p in self.passages.values())
        self.assertNotIn("navigation box", texts)
        self.assertNotIn("reference paragraph", texts)
        self.assertNotIn("For other uses", texts)

    def test_links_keep_the_passage_words(self):
        self.assertEqual(self.passages["0.1"].links, (("Octavian", "Octavian"), ("Mark Antony", "Antony")))
        self.assertEqual(self.passages["1.1"].links, (("Patras", "Patrae"),))

    def test_infobox_links_are_kept_apart_and_files_dropped(self):
        self.assertEqual(self.infobox, ("Mark Antony",))

    def test_a_preserved_link_map_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wikipedia-en-test-r1-qids.json"
            path.write_text(json.dumps({"retrievedAt": "2026-10-15", "qids": {"Patras": "Q133123"}}), encoding="utf-8")
            self.assertEqual(resolve_qids(["Patras"], Path(directory), "wikipedia-en-test-r1"), {"Patras": "Q133123"})


if __name__ == "__main__":
    unittest.main()
