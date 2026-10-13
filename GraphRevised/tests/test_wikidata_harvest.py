"""First-contact harvest, increment 1: Wikidata dates by precision, statement classes, Year tethers. Offline."""

import json
import unittest
from pathlib import Path

from GraphRevised.harvest.wikidata_harvest import classify, load_rules, tether
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.temporal import TimeValueError, wikidata_time

JULIAN = "http://www.wikidata.org/entity/Q1985786"
PAYLOAD = Path(__file__).resolve().parents[1] / "phase-5-source" / "wikidata-Q51673-r2553883228.json"


def time(value, precision):
    return {"time": value, "precision": precision, "calendarmodel": JULIAN}


class WikidataTimeTests(unittest.TestCase):
    def test_bce_years_are_historical_and_become_astronomical(self):
        self.assertEqual(wikidata_time(time("-0083-00-00T00:00:00Z", 9)), ("-0082", "julian"))
        self.assertEqual(wikidata_time(time("-0083-01-14T00:00:00Z", 11)), ("-0082-01-14", "julian"))
        self.assertEqual(wikidata_time(time("+0014-08-00T00:00:00Z", 10)), ("0014-08", "julian"))

    def test_decades_and_centuries_become_the_years_they_cover(self):
        self.assertEqual(wikidata_time(time("-0050-00-00T00:00:00Z", 8)), ("-0058/-0049", "julian"))  # 59-50 BCE
        self.assertEqual(wikidata_time(time("-0044-00-00T00:00:00Z", 8)), ("-0048/-0039", "julian"))  # not -50..-41
        self.assertEqual(wikidata_time(time("-0083-00-00T00:00:00Z", 7)), ("-0099/0000", "julian"))   # 100-1 BCE
        self.assertEqual(wikidata_time(time("+0014-00-00T00:00:00Z", 7)), ("0001/0100", "julian"))

    def test_coarse_or_impossible_values_are_refused(self):
        with self.assertRaises(TimeValueError):
            wikidata_time(time("-0500-00-00T00:00:00Z", 6))
        with self.assertRaises(TimeValueError):
            wikidata_time(time("+0000-00-00T00:00:00Z", 9))
        with self.assertRaises(TimeValueError):
            wikidata_time({"time": "-0083-00-00T00:00:00Z", "precision": 9, "calendarmodel": "Q0"})


class TetherTests(unittest.TestCase):
    def test_a_point_or_span_is_during_and_a_window_is_within(self):
        self.assertEqual(tether("-0039/-0031", "julian", "during"), {"how": "during", "years": [-40, -32], "count": 9})
        self.assertEqual(tether("-0067/-0049", "julian", "within"), {"how": "within", "years": [-68, -50]})

    def test_long_spans_tether_by_their_ends_and_outside_dates_are_flagged(self):
        self.assertEqual(tether("-0508/-0026", "julian", "during")["how"], "start and end")
        self.assertEqual(tether("-2999", "julian", "during"), {"how": "outside the backbone", "years": [-3000]})
        self.assertEqual(tether("-0063/..", "julian", "during"), {"how": "start only", "years": [-64]})


class ClassifyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        entity = json.loads(PAYLOAD.read_bytes())["entities"]["Q51673"]
        cls.statements, cls.deprecated = classify(entity, load_rules(), load_registry())

    def pick(self, pid):
        return [s for s in self.statements if s.pid == pid]

    def test_every_statement_has_a_kind_and_deprecated_ones_are_left_out(self):
        kinds = {s.kind for s in self.statements}
        self.assertLessEqual(kinds, {"identifier", "attribute", "dated", "relationship", "housekeeping"})
        self.assertGreater(self.deprecated, 0)
        self.assertTrue(all(s.rank != "deprecated" for s in self.statements))

    def test_dates_are_dated_claims_not_attributes(self):
        born = self.pick("P569")
        self.assertTrue(born and all(s.kind == "dated" and s.event == "born" for s in born))
        self.assertIn("preferred", {s.rank for s in born})

    def test_classifying_items_are_attributes_and_identifiers_are_crosswalk(self):
        self.assertEqual({s.kind for s in self.pick("P21")}, {"attribute"})
        self.assertEqual({s.kind for s in self.pick("P6863")}, {"identifier"})
        self.assertEqual({s.kind for s in self.pick("P373")}, {"housekeeping"})

    def test_relationships_carry_mapped_qualifiers(self):
        spouses = self.pick("P26")
        self.assertTrue(all(s.kind == "relationship" and s.predicates == [("spouseOf", "forward")] for s in spouses))
        windows = [s for s in spouses if s.time and s.time["mode"] == "within"]
        self.assertTrue(windows, "an earliest/latest pair is an uncertain window")
        self.assertTrue(any("P1545" in s.carried and "P1534" in s.carried for s in spouses))
        offices = [s for s in self.pick("P39") if s.carried.get("P1706")]
        self.assertTrue(offices, "a colleague (together with) is carried")


if __name__ == "__main__":
    unittest.main()
