"""The period survey: PeriodO definitions matched by name and time, stored as attributed evidence."""

import os
import unittest
from dataclasses import replace

from GraphRevised.adapters.periodo import PeriodDataset, PeriodDefinition, PeriodSource, parse_definitions
from GraphRevised.discovery.period_survey import (
    Match, definition_draft, definition_edtf, load_config, match_definitions, record_text, store_evidence, work_label,
)

IGNORED = set(load_config()["periodo"]["ignoredWords"])
LCSH = PeriodSource(authority_id="lcsh", title="Library of Congress Subject Headings", creators=("Library of Congress",),
                    year="2015", citation=None, url=None, part_of=None, locator=None)
BOOK = PeriodSource(authority_id="book", title="Art history", creators=("Stokstad, Marilyn",), year="2011",
                    citation=None, url=None, part_of=None, locator=None)


def definition(id, label, start, stop, *, places=(), source=LCSH, labels=None, start_label="510 B.C.",
               stop_label="30 B.C.", description=None):
    return PeriodDefinition(
        id=id, uri=f"http://n2t.net/ark:/99152/{id}", label=label, labels=labels or (label,), language="en",
        start_label=start_label, stop_label=stop_label, start_years=start, stop_years=stop, places=places,
        place_description=description, editorial_note=None, broader=(), narrower=(), source=source, page=None)


REPUBLIC = definition("p1", "Republic, 510-30 B.C", (-509, -509), (-29, -29), places=(("Q17167", "Roman Republic"),),
                      description="Rome")
EARLY = definition("p2", "Republic, 265-30 B.C", (-264, -264), (-29, -29), places=(("Q17167", "Roman Republic"),))
LATE = definition("p3", "Late Roman Republic", (-145, -145), (-26, -26), source=BOOK)
CZECH = definition("p4", "doba římská", (-30, -30), (400, 400), places=(("Q213", "Czech Republic"),),
                   labels=("doba římská", "Roman period"), source=BOOK)
RUSSIAN = definition("p5", "Russian Empire", (1721, 1721), (1917, 1917), source=BOOK)
EMPIRE = definition("p6", "Empire, 30 B.C.-476 A.D", (-29, -29), (476, 476), places=(("Q2277", "Roman Empire"),),
                    start_label="30 B.C.", stop_label="476 A.D.")
COMBINED = definition("p7", "Hellenistic Greek, Roman Republic (330 BC-30 BC)", (-330, -330), (-30, -30), source=BOOK)
ACTIUM = (-31, -30)


def fits(names, definitions, window=ACTIUM):
    return {m.definition.id: m.fit for m in match_definitions(names, definitions, window, near_years=50, ignored=IGNORED)}


class MatchingTests(unittest.TestCase):
    def test_a_region_supplies_qualifiers_but_not_the_period_noun(self):
        found = fits(["Roman Republic"], (REPUBLIC, LATE, CZECH))
        self.assertEqual(found["p1"], "same")  # "Republic" in the Roman Republic
        self.assertEqual(found["p3"], "related")  # a phase: "Late" adds to the name
        self.assertNotEqual(found.get("p4"), "same")  # "Republic" only from the Czech Republic

    def test_one_source_defining_a_period_twice_keeps_its_widest_span(self):
        matches = match_definitions(["Roman Republic"], (REPUBLIC, EARLY), ACTIUM, near_years=50, ignored=IGNORED)
        by_id = {m.definition.id: m for m in matches}
        self.assertEqual(by_id["p1"].fit, "same")
        self.assertEqual(by_id["p2"].fit, "related")
        self.assertIn("same source", by_id["p2"].note)

    def test_the_reading_time_separates_empires(self):
        self.assertEqual(fits(["Empire"], (EMPIRE, RUSSIAN)), {"p6": "same"})
        self.assertEqual(fits(["Empire"], (EMPIRE,), window=None), {})  # no time context, no matches

    def test_a_combined_period_is_not_its_parts(self):
        self.assertNotEqual(fits(["Roman Republic"], (COMBINED,)).get("p7"), "same")

    def test_same_language_variants_are_not_names_of_the_definition(self):
        data = {"authorities": {"a": {"source": {"title": "Pleiades"}, "periods": {"p": {
            "label": "Hellenistic Greek, Roman Republic", "languageTag": "en",
            "localizedLabels": {"en": ["Roman Republic"], "it": ["Ellenistico, Repubblica romana"]},
            "start": {"in": {"year": "-0329"}}, "stop": {"in": {"year": "-0029"}}}}}}}
        self.assertEqual(parse_definitions(data)[0].labels,
                         ("Hellenistic Greek, Roman Republic", "Ellenistico, Repubblica romana"))


class EvidenceTests(unittest.TestCase):
    def test_dates_and_wording(self):
        self.assertEqual(definition_edtf(REPUBLIC), "-0509/-0029")
        ranged = replace(REPUBLIC, start_years=(-550, -500))
        self.assertEqual(definition_edtf(ranged), "-0550~/-0029")
        self.assertEqual(record_text(REPUBLIC), "Republic, 510-30 B.C\n510 B.C.\n30 B.C.\nRome")
        self.assertEqual(work_label(REPUBLIC), "Library of Congress Subject Headings")
        self.assertEqual(work_label(LATE), "Stokstad, Art history")

    def test_the_draft_quotes_the_record(self):
        draft = definition_draft(Match(REPUBLIC, "same", "Roman Republic", REPUBLIC.label), "chr:entity:x",
                                 "chr:observation:periodo:p1:v1", "chr:entity:work", "gregorian")
        text = record_text(REPUBLIC)
        self.assertIn(draft.quotations[0].text, text)
        self.assertIn(draft.qualifier_quotations[0].text, text)
        self.assertEqual((draft.mode, draft.attributed_to, draft.time.edtf), ("attributed", "chr:entity:work",
                                                                              "-0509/-0029"))
        self.assertIsNone(definition_draft(Match(replace(REPUBLIC, stop_label=None), "same", "x", "x"),
                                           "e", "o", "w", "gregorian"))


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class StoreEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        from GraphRevised.operations import load_operations
        from GraphRevised.proposals.registry import load_registry

        cls.operations, cls.registry = load_operations(), load_registry()
        cls.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
            notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        from GraphRevised.operations import run_write

        self.tx = self.session.begin_transaction()
        run_write(self.tx, self.operations, "upsert_entity", {"id": "chr:entity:test-survey-period", "kind": "Period",
                                                              "label": "Test Republic", "description": None,
                                                              "status": "proposed", "shortLabel": None})

    def tearDown(self):
        self.tx.rollback()

    def test_a_definition_becomes_a_work_a_record_and_an_attributed_claim(self):
        source = replace(LCSH, authority_id="test-authority", title="Test Subject Headings For Periods")
        dataset = PeriodDataset(definitions=(), version="test-1", retrieved_at="2026-10-12T00:00:00Z",
                                content_hash="0" * 64, source_uri="https://example.org/periodo-test.json")
        match = Match(replace(REPUBLIC, id="ptest1", source=source), "same", "Test Republic", REPUBLIC.label)
        entry = store_evidence(self.tx, self.operations, self.registry, dataset, match, "chr:entity:test-survey-period",
                               "gregorian")
        self.assertTrue(entry["workCreated"])
        self.assertEqual(entry["claim"]["outcome"], "valid", entry["claim"]["reasons"])
        record = self.tx.run("MATCH (o:SourceObservation {id: $id})-[:IN_WORK]->(w) RETURN o.observationKind AS kind, "
                             "w.status AS status", id=entry["observation"]).single()
        self.assertEqual((record["kind"], record["status"]), ("record", "proposed"))
        again = store_evidence(self.tx, self.operations, self.registry, dataset, match,
                               "chr:entity:test-survey-period", "gregorian")
        self.assertEqual(again["work"], entry["work"])  # the Work is reused
        self.assertEqual(again["claim"]["outcome"], "duplicate")


if __name__ == "__main__":
    unittest.main()
