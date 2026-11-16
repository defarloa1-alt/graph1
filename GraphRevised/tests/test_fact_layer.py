"""The derived fact layer: one direct edge per fact, Year edges, and node summaries (offline)."""

import unittest

from GraphRevised.export.fact_layer import MARK, plan, relationship_type, source_names, summarise


def node(id_, label, full=None, facts=()):
    return {"data": {"id": id_, "label": label, "fullLabel": full or label, "facts": list(facts)}}


def voice(claim, status="proposed", according=None, time=None, role=None):
    return {"claimId": claim, "status": status, "accordingTo": according, "time": time, "role": role}


def fact(source, target, predicate, voices, status="proposed", times=()):
    return {"data": {"source": source, "target": target, "predicate": predicate, "status": status,
                     "mode": "attributed", "category": "factual", "attestation": "attested (1 author)",
                     "sentence": f"{source} {predicate} {target}", "times": list(times), "voices": voices}}


WORK = "The Life and Times of Cleopatra"
VIEW = {"elements": {
    "nodes": [
        node("event", "Enters Alexandria", facts=[{"predicate": "occurred", "voices": [
            voice("c1", according=WORK, time="c. end of September 31 BCE"),
            voice("c0", status="rejected", time="30 BCE")]}]),
        node("alexandria", "Alexandria"),
        node("phase", "Antony follows Cleopatra"),
        node("cleopatra", "Cleopatra"),
        node("work", "Life and Times", full=WORK),
        node("weigall", "Weigall"),
    ],
    "edges": [
        fact("event", "alexandria", "occurredAt", [voice("c2", according=WORK)]),
        fact("event", "phase", "partOf", [voice("c3")]),
        fact("cleopatra", "event", "participatedIn", [voice("c4", according=WORK, role="queen")]),
    ]}}
YEARS = [
    {"entity": "event", "predicate": "occurred", "year": -31, "as": "during", "status": "proposed",
     "claim": "c1", "according": WORK},
    {"entity": "event", "predicate": "occurred", "year": -31, "as": "during", "status": "accepted",
     "claim": "c5", "according": None},
]


class FactLayerTests(unittest.TestCase):
    def setUp(self):
        self.layer = plan(VIEW, YEARS, {"work": "weigall"})

    def test_relationship_names_follow_the_predicate(self):
        self.assertEqual(relationship_type("occurredAt"), "OCCURRED_AT")
        self.assertEqual(relationship_type("partOf"), "PART_OF")
        self.assertEqual(relationship_type("occurred"), "OCCURRED")
        with self.assertRaises(ValueError):
            relationship_type("x]->(y) DELETE y //")

    def test_one_marked_edge_per_fact(self):
        edges = {e["type"]: e for e in self.layer["edges"]}
        self.assertEqual(set(edges), {"OCCURRED_AT", "PART_OF", "PARTICIPATED_IN"})
        self.assertTrue(all(e["properties"]["derived"] == MARK for e in self.layer["edges"]))
        participated = edges["PARTICIPATED_IN"]
        self.assertEqual((participated["source"], participated["target"]), ("cleopatra", "event"))
        self.assertEqual(participated["properties"]["accordingTo"], ["Weigall"])
        self.assertEqual(participated["properties"]["role"], ["queen"])
        self.assertEqual(edges["PART_OF"]["properties"]["accordingTo"], ["Chrystallum"])
        self.assertNotIn("when", edges["PART_OF"]["properties"])

    def test_year_edges_merge_voices(self):
        [year] = self.layer["years"]
        self.assertEqual((year["entity"], year["year"], year["type"]), ("event", -31, "OCCURRED"))
        self.assertEqual(year["properties"]["status"], "accepted")
        self.assertEqual(year["properties"]["accordingTo"], ["Chrystallum", "Weigall"])
        self.assertEqual(year["properties"]["assertions"], ["c1", "c5"])

    def test_summary_names_who_says_it_and_skips_dead_claims(self):
        [summary] = self.layer["summary"]
        self.assertEqual(summary["id"], "event")
        self.assertEqual(summary["properties"], {
            "where": "Alexandria (Weigall)", "partOf": "Antony follows Cleopatra",
            "when": "c. end of September 31 BCE (Weigall)"})

    def test_one_answer_ours_then_accepted_then_proposed(self):
        self.assertEqual(summarise([(2, "Actium", "Hale"), (0, "Actium", ""), (0, "Ionian Sea", "")]),
                         "Actium; Ionian Sea")
        self.assertEqual(summarise([(2, "2 September 31 BCE", "Hale"), (3, "on the second of September", "Dio"),
                                    (4, "2 September 31 BCE", "Wikipedia")]), "2 September 31 BCE (Hale)")
        self.assertEqual(summarise([(4, "31 BCE", "A"), (4, "31 BCE", "B")]), "31 BCE (A, B)")

    def test_sources_are_named_by_author(self):
        nodes = {"w1": {"label": "Life and Times of Cleopatra", "fullLabel": "Weigall, The Life and Times of Cleopatra"},
                 "w2": {"label": "Armenian Soviet Encyclopedia, vol. 1", "fullLabel": "Armenian Soviet Encyclopedia, vol. 1"},
                 "w3": {"label": "Roman History", "fullLabel": "Cassius Dio, Roman History"},
                 "dio": {"label": "Dio", "fullLabel": "Cassius Dio"}}
        names = source_names(nodes, {"w3": "dio"})
        self.assertEqual(names["Weigall, The Life and Times of Cleopatra"], "Weigall")
        self.assertEqual(names["Armenian Soviet Encyclopedia, vol. 1"], "Armenian Soviet Encyclopedia, vol. 1")
        self.assertEqual(names["Cassius Dio, Roman History"], "Dio")


if __name__ == "__main__":
    unittest.main()
