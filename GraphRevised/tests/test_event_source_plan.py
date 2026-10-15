"""The event source plan's deterministic steps, without a model call, the network, or the graph."""

import unittest

from GraphRevised.adapters.scaife_catalog import parse_catalog
from GraphRevised.adapters.text_catalogues import (GutenbergCatalog, LacusCurtiusIndex, Snapshot,
                                                   parse_lacuscurtius_index, title_match)
from GraphRevised.discovery.event_source_plan import EventCandidate, already_read, locate, rank_key

SNAPSHOT = Snapshot("test", "2026-10-15T00:00:00Z", "test", b"")
SCAIFE = parse_catalog({
    "text_groups": [{"urn": "urn:cts:latinLit:phi9001", "label": "Poeta, Quintus"}],
    "works": [{"urn": "urn:cts:latinLit:phi9001.phi001", "label": "Carmina"}],
    "texts": [{"urn": "urn:cts:latinLit:phi9001.phi001.perseus-lat2"},
              {"urn": "urn:cts:latinLit:phi9001.phi001.perseus-eng2"}],
}, retrieved_at="2026-10-15T00:00:00Z", content_hash="test")


def book(number, title, authors, language="en"):
    return {"Text#": number, "Type": "Text", "Title": title, "Authors": authors, "Language": language}


GUTENBERG = GutenbergCatalog([
    book("1", "The Odes of Poeta", "Poeta, 60 BCE-8 BCE; Translator, Some [Translator]"),
    book("2", "Letters of Poeta Walker", "Walker, Poeta, 1717-1797"),
    book("3", "Verses of a Child's World", "Rome, Ancient, 1900-1950"),
    book("4", "Tales Told Anew", "Anonymous"),
    book("5", "The Tragedy of Marcus and Livia", "Dramatist, William, 1564-1616"),
], SNAPSHOT)
LACUS = LacusCurtiusIndex([{"url": "https://example.org/Thayer/E/Roman/Texts/Historicus/home.html",
                            "label": "Historicus"}], SNAPSHOT)
SYSTEMS = {"perseus": "perseus-tei", "gutenberg": "gutenberg-html", "lacuscurtius": "lacuscurtius-html"}


def candidate(author, work, form="history", **extra):
    fields = dict(author=author, work=work, locator="", cts_work_urn="", composition="", composition_year=None,
                  form=form, relation="later", depends_on=[], coverage="", channels=["agent"], certainty="")
    return EventCandidate(**(fields | extra))


class CatalogueMatchTests(unittest.TestCase):
    def test_a_single_name_matches_the_surname_only(self):
        self.assertEqual([b["Text#"] for b in GUTENBERG.by_author("Poeta")], ["1"])

    def test_a_catalogue_style_name_matches_by_its_surname(self):
        self.assertEqual([b["Text#"] for b in GUTENBERG.by_author("Dramatist, William")], ["5"])

    def test_anonymous_matches_nothing(self):
        self.assertEqual(GUTENBERG.by_author("Anonymous"), [])

    def test_one_common_word_is_not_a_title_match(self):
        self.assertFalse(title_match("Rome in the Ancient World", "Verses of a Child's World"))
        self.assertTrue(title_match("Odes", "The Odes of Poeta"))
        self.assertTrue(title_match("Marcus and Livia", "The Tragedy of Marcus and Livia"))

    def test_lacuscurtius_links_wrapped_in_newlines_are_read(self):
        page = '<BASE HREF="https://example.org/Thayer/"><A HREF="\nE/Roman/Texts/Historicus/home.html\n">Historicus:</A>'
        self.assertEqual(parse_lacuscurtius_index(page)[0]["url"], "https://example.org/Thayer/E/Roman/Texts/Historicus/home.html")


class LocateTests(unittest.TestCase):
    def test_copies_are_found_in_each_catalogue(self):
        found = locate(candidate("Quintus Poeta", "Odes", "poem", cts_work_urn="urn:cts:latinLit:phi9001.phi001"),
                       SCAIFE, GUTENBERG, LACUS, SYSTEMS)
        self.assertEqual(found["status"], "located")
        self.assertEqual([(c["system"], c["language"]) for c in found["copies"]],
                         [("perseus", "lat"), ("perseus", "eng"), ("gutenberg", "en")])

    def test_a_lost_work_is_never_located(self):
        found = locate(candidate("Historicus", "Memoirs", "lost"), SCAIFE, GUTENBERG, LACUS, SYSTEMS)
        self.assertEqual((found["status"], found["copies"]), ("identified", []))

    def test_an_unmatched_work_is_only_found(self):
        found = locate(candidate("Potter, D. S.", "Rome in the Ancient World"), SCAIFE, GUTENBERG, LACUS, SYSTEMS)
        self.assertEqual(found["status"], "found")

    def test_a_system_the_registry_cannot_read_gives_no_copy(self):
        found = locate(candidate("Historicus", "Histories"), SCAIFE, GUTENBERG, LACUS, {"perseus": "perseus-tei"})
        self.assertEqual(found["copies"], [])

    def test_works_already_read_are_recognised(self):
        read = [{"id": "chr:entity:test-work", "label": "Quintus Poeta, Odes"}]
        self.assertEqual(already_read(candidate("Quintus Poeta", "The Odes"), read), "chr:entity:test-work")
        self.assertIsNone(already_read(candidate("Quintus Poeta", "Satires"), read))

    def test_ranking_puts_status_then_relation_then_year_first(self):
        rows = [{"status": s, "relation": r, "composition_year": y}
                for s, r, y in [("found", "contemporary", -30), ("chosen", "later", 120), ("chosen", "contemporary", -20)]]
        self.assertEqual([(r["status"], r["relation"]) for r in sorted(rows, key=rank_key)],
                         [("chosen", "contemporary"), ("chosen", "later"), ("found", "contemporary")])


if __name__ == "__main__":
    unittest.main()
