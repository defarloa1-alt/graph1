"""Source discovery without a model call or the network: citations, catalogue checks, ranking."""

import unittest

from GraphRevised.adapters.scaife_catalog import parse_catalog
from GraphRevised.discovery.source_plan import SourceCandidate, check_catalog, cited_sources, rank

CATALOG = parse_catalog({
    "text_groups": [{"urn": "urn:cts:latinLit:phi9001", "label": "Poeta, Quintus"},
                    {"urn": "urn:cts:greekLit:tlg9002", "label": "Historicus Graecus"}],
    "works": [{"urn": "urn:cts:latinLit:phi9001.phi001", "label": "Carmina"},
              {"urn": "urn:cts:latinLit:phi9001.phi002", "label": "Epodon liber"},
              {"urn": "urn:cts:greekLit:tlg9002.tlg001", "label": "Historia Romana"}],
    "texts": [{"urn": "urn:cts:latinLit:phi9001.phi001.perseus-lat2"},
              {"urn": "urn:cts:latinLit:phi9001.phi001.perseus-eng2"},
              {"urn": "urn:cts:latinLit:phi9001.phi002.perseus-lat2"},
              {"urn": "urn:cts:greekLit:tlg9002.tlg001.perseus-grc2"}],
}, retrieved_at="2026-10-12T00:00:00Z", content_hash="test")


def candidate(**extra):
    fields = dict(author="Quintus Poeta", work="Odes", locator="1.37", cts_work_urn=None, composition="c. 30 BCE",
                  composition_year=-30, genre="lyric poetry", relation="contemporary", depends_on=[],
                  coverage="A victory ode.", confidence="high")
    return SourceCandidate(**(fields | extra))


class CitationTests(unittest.TestCase):
    def test_citations_of_other_accounts_are_found(self):
        found = cited_sources([{"locator": "68.1", "passageText": "three hundred ships were captured, as Caesar himself has written."}])
        self.assertEqual([(c["locator"], c["who"]) for c in found], [("68.1", "Caesar")])
        according = cited_sources([{"locator": "1", "passageText": "The fleet, according to Livy, was larger."}])
        self.assertEqual([c["who"] for c in according], ["Livy"])

    def test_temporal_as_is_not_a_citation(self):
        self.assertEqual(cited_sources([{"locator": "1", "passageText": "As Antony fled, Caesar pursued."}]), [])


class CatalogTests(unittest.TestCase):
    def test_a_known_urn_reports_its_languages(self):
        result = check_catalog(candidate(cts_work_urn="urn:cts:latinLit:phi9001.phi001"), CATALOG)
        self.assertEqual((result["status"], result["languages"]), ("work found", ["eng", "lat"]))

    def test_titles_meet_across_languages_and_are_flagged(self):
        result = check_catalog(candidate(work="Epodes"), CATALOG)
        self.assertEqual(result["status"], "work matched by title (verify)")
        self.assertEqual(result["workUrn"], "urn:cts:latinLit:phi9001.phi002")

    def test_unknown_works_and_authors_are_reported(self):
        self.assertEqual(check_catalog(candidate(work="Satires"), CATALOG)["status"], "author found, work not matched")
        missing = check_catalog(candidate(author="Velleius", cts_work_urn="urn:cts:latinLit:phi9999.phi001"), CATALOG)
        self.assertTrue(missing["status"].startswith("not in catalogue (proposed URN"))


class RankTests(unittest.TestCase):
    def test_earliest_and_most_direct_first(self):
        plan = rank([
            candidate(author="Late", relation="later", composition_year=220).model_dump(),
            candidate(author="Undated", relation="contemporary", composition_year=None).model_dump(),
            candidate(author="Poet", relation="contemporary", composition_year=-30).model_dump(),
            candidate(author="Near", relation="near-contemporary", composition_year=30).model_dump(),
        ])
        self.assertEqual([c["author"] for c in plan], ["Poet", "Undated", "Near", "Late"])


if __name__ == "__main__":
    unittest.main()
