"""Parsing an article's ancient citations into leads (harvest/article_citations.py). Offline."""
import unittest

from GraphRevised.harvest.article_citations import citations, expand, resolve

TABLE = {"works": {"w:dio": ["Cass. Dio"], "w:plut": ["Plut. Vit. Ant.", "Plut. Fit. Ant."]},
         "notHeld": ["Oros."], "locatorDepth": {"w:dio": 3, "w:plut": 2}}


class ExpandTests(unittest.TestCase):
    def test_a_shorter_locator_borrows_the_book(self):
        self.assertEqual([(s, e) for _, s, e in expand("50.15, 30.3-4", 3)],
                         [((50, 15), (50, 15)), ((50, 30, 3), (50, 30, 4))])

    def test_two_part_works_do_not_borrow(self):
        self.assertEqual([s for _, s, _ in expand("67.7, 68.4-5", 2)], [(67, 7), (68, 4)])

    def test_an_abbreviated_range_end_is_filled(self):
        self.assertEqual(expand("50.33-4", 3)[0][2], (50, 34))

    def test_a_note_number_run_into_a_range_is_dropped(self):
        self.assertEqual(expand("50.33-4.67", 3)[0][2], (50, 34))


class CitationTests(unittest.TestCase):
    def test_held_fetch_acquire_and_unresolved(self):
        pages = [(608, "the queen fled (Cass. Dio 50.15, 30.3-4; Plut. Fit. Ant. 63.3); cf. Oros. 6.19.6 and "
                       "Cass. Dio 41 Plutarch's sources")]
        found = citations(pages, TABLE)
        resolve(found, {"w:dio": [((50, 15, 1), "o:dio-50.15.1")], "w:plut": [((63, 3), "o:plut-63.3")]})
        self.assertEqual([(c["cited"], c["kind"]) for c in found], [
            ("Cass. Dio 50.15", "held, passage held"), ("Cass. Dio 50.30.3-4", "held, passage not held"),
            ("Plut. Fit. Ant. 63.3", "held, passage held"), ("Oros. 6.19.6", "not held"),
            ("Cass. Dio 41", "unresolved")])
        self.assertEqual(found[0]["passages"], ["o:dio-50.15.1"])


if __name__ == "__main__":
    unittest.main()
