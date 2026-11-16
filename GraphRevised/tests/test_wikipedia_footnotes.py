"""Following a Wikipedia footnote to the passage it cites (D-148). Offline."""
import unittest

from GraphRevised.adapters.wikipedia_passages import footnote_positions, footnotes, parse_html
from GraphRevised.harvest.wikipedia_footnotes import citations, supporting, within

ALIASES = {"w:hist": ["Test Historian", "Historian, Test"], "w:life": ["Biographer, Life"]}
HTML = """<div class="mw-parser-output"><p>The fleet sailed at dawn after long delay.<sup class="reference">
<a href="#cite_note-a-1">[1]</a></sup><sup class="reference"><a href="#cite_note-b-2">[2]</a></sup> Then the
wind rose and the ships turned back to the harbour.<sup class="reference"><a href="#cite_note-c-3">[3]</a></sup></p>
<ol class="references"><li id="cite_note-a-1"><span class="reference-text">Test Historian 50.31.</span></li>
<li id="cite_note-b-2"><span class="reference-text">Biographer, Life 65–66; Modern 1999, p. 4.</span></li>
<li id="cite_note-c-3"><span class="reference-text">Lost Chronicle 3.</span></li></ol></div>"""


class FootnoteTests(unittest.TestCase):
    def test_citations_parse_works_locators_and_the_rest(self):
        found = citations("Test Historian 50.23.1–3; Biographer, Life ii.85; Lost Chronicle 3; Modern 1999, p. 4",
                          ALIASES, ["Lost Chronicle"])
        self.assertEqual([(c["kind"], c.get("start"), c.get("end")) for c in found],
                         [("held", (50, 23, 1), (50, 23, 3)), ("held", (2, 85), (2, 85)),
                          ("ancient not held", None, None), ("modern", None, None)])

    def test_a_range_covers_its_sections(self):
        self.assertTrue(within((65, 3), (65,), (66,)))
        self.assertTrue(within((66, 5), (65,), (66,)))
        self.assertFalse(within((67, 1), (65,), (66,)))
        self.assertFalse(within((50, 23, 4), (50, 23, 1), (50, 23, 3)))

    def test_the_footnote_after_the_quotation_in_its_sentence(self):
        passages, _ = parse_html(HTML)
        positions, notes = footnote_positions(HTML), footnotes(HTML)
        text = passages["0.1"].text
        self.assertEqual(text, "The fleet sailed at dawn after long delay. Then the wind rose and the ships turned "
                               "back to the harbour.")
        self.assertEqual(supporting(text, "sailed at dawn", positions["0.1"]), ["cite_note-a-1", "cite_note-b-2"])
        self.assertEqual(supporting(text, "the ships turned back", positions["0.1"]), ["cite_note-c-3"])
        self.assertEqual(notes["cite_note-a-1"], "Test Historian 50.31.")
        self.assertEqual(supporting(text, "not in the passage", positions["0.1"]), [])


if __name__ == "__main__":
    unittest.main()
