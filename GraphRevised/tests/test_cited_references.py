"""Wikidata references as voices, and LC heading neighbours (2026-11-16). Offline."""
import unittest

from GraphRevised.harvest.lc_subjects import neighbours
from GraphRevised.harvest.wikidata_references import reference_text, references
from GraphRevised.proposals.schema import ProposalDraft
from GraphRevised.proposals.validator import _check_qualifier_evidence

STATEMENT = {"id": "Q1$abc", "references": [
    {"snaks": {"P248": [{"datavalue": {"value": {"id": "Q100166489"}}}],
               "P304": [{"datavalue": {"value": "412"}}]}},
    {"snaks": {"P143": [{"datavalue": {"value": {"id": "Q328"}}}]}}]}
PAYLOAD = {"entities": {"Q1": {"claims": {"P22": [STATEMENT]}}}}


def draft(attributed_to):
    # Only the fields the evidence rule reads; the full draft schema is tested elsewhere.
    return ProposalDraft.model_construct(predicate="childOf", subject_id="a", object_id="b", mode="attributed",
                                         attributed_to=attributed_to, observation_ids=("o",), quotations=(),
                                         qualifier_quotations=(), time=None)


class WikidataReferenceTests(unittest.TestCase):
    def test_stated_in_is_read_and_imported_from_is_not_a_source(self):
        refs = references(PAYLOAD, "Q1$abc")
        self.assertEqual(refs[0]["statedIn"], ["Q100166489"])
        self.assertEqual(refs[0]["page"], "412")
        self.assertEqual(refs[1]["statedIn"], [])  # "imported from Wikimedia project" names no source
        self.assertEqual(reference_text("DPRR", refs[0]), "DPRR, p. 412")

    def test_a_statement_supports_only_wikidata_or_a_work_it_cites(self):
        statements = [{"id": "o", "sourceSystem": "Wikidata", "externalStatementId": "Q1$abc"}]
        self.assertEqual(_check_qualifier_evidence(draft("chr:entity:wikidata"), [], statements), [])
        self.assertEqual(_check_qualifier_evidence(draft("w:dprr"), [], statements, [{"w:dprr"}]), [])
        self.assertTrue(_check_qualifier_evidence(draft("w:other"), [], statements, [{"w:dprr"}]))
        self.assertTrue(_check_qualifier_evidence(draft("w:dprr"), [], statements))


class HeadingNeighbourTests(unittest.TestCase):
    def test_broader_narrower_related_and_wikidata_match(self):
        sh = "http://id.loc.gov/authorities/subjects/"
        payload = [
            {"@id": f"{sh}sh1", "http://www.w3.org/2004/02/skos/core#broader": [{"@id": f"{sh}sh2"}],
             "http://www.w3.org/2004/02/skos/core#narrower": [{"@id": f"{sh}sh3"}],
             "http://www.w3.org/2004/02/skos/core#related": [{"@id": f"{sh}sh4"}],
             "http://www.w3.org/2004/02/skos/core#closeMatch": [{"@id": "http://www.wikidata.org/entity/Q9"},
                                                              {"@id": "http://id.worldcat.org/fast/1"}]},
            {"@id": f"{sh}sh2", "http://www.w3.org/2004/02/skos/core#prefLabel": [{"@value": "Broader"}]},
            {"@id": "http://www.wikidata.org/entity/Q9", "http://www.w3.org/2004/02/skos/core#prefLabel": [{"@value": "Nine"}]}]
        found = neighbours(payload, "sh1")
        self.assertEqual(found["broader"], [("sh2", "Broader")])
        self.assertEqual(found["narrower"], [("sh3", None)])
        self.assertEqual(found["related"], [("sh4", None)])
        self.assertEqual(found["wikidata"], [("Q9", "Nine")])


if __name__ == "__main__":
    unittest.main()
