"""The predicate-needs queue and its precedents (39 §7), offline."""

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from GraphRevised.proposals.lens import lens_text, load_lens
from GraphRevised.proposals.predicate_needs import (
    load_queue, merge, needs_from_run, open_requests_text, precedents, set_shape, words,
)
from GraphRevised.proposals.registry import load_registry

REGISTRY = load_registry()


def need(name="defectedTo", definition="A person changed sides, going over to the enemy.",
         specialist="lens-specialist:military/roman-republic", quotation="Dellius deserted to Caesar"):
    return {"name": name, "definition": definition, "subjectKinds": ["Person"], "objectKinds": ["Person"],
            "specialist": specialist, "evidence": {"observationId": "chr:observation:x", "quotation": quotation}}


class WordsTests(unittest.TestCase):
    def test_names_and_prose_share_stems(self):
        self.assertIn("defect", words("defectedTo"))
        self.assertIn("defect", words("DEFECTED_TO"))
        self.assertIn("defect", words("the fleet defected"))
        self.assertNotIn("the", words("the fleet"))


class PrecedentTests(unittest.TestCase):
    def test_a_need_finds_its_legacy_relationship(self):
        found = precedents(need(), REGISTRY)
        self.assertIn("DEFECTED_TO", [row["name"] for row in found["legacy"]])

    def test_a_need_close_to_an_active_predicate_finds_it(self):
        found = precedents(need("deprivedOfPosition", "A person was deprived of a position held."), REGISTRY)
        self.assertIn("heldPosition", [row["id"] for row in found["registry"]])

    def test_an_unrelated_need_finds_little(self):
        found = precedents(need("reportsOmen", "A Work reports an omen or portent."), REGISTRY)
        self.assertEqual(found["registry"], [])


class QueueTests(unittest.TestCase):
    def test_same_name_merges_and_keeps_every_voice(self):
        queue = {"requests": []}
        counts = merge(queue, [need(), need(specialist="lens-specialist:political/roman-republic",
                                            quotation="Amyntas went over to Caesar")], REGISTRY)
        self.assertEqual(counts, {"new": 1, "merged": 1, "known": 0})
        (request,) = queue["requests"]
        self.assertEqual(len(request["requestedBy"]), 2)
        self.assertEqual(len(request["evidence"]), 2)
        self.assertEqual(request["status"], "open")

    def test_similar_names_are_listed_not_merged(self):
        queue = {"requests": []}
        merge(queue, [need(), need("wentOverTo", "A force or its members defected or surrendered to another.")],
              REGISTRY)
        by_name = {request["name"]: request for request in queue["requests"]}
        self.assertEqual(set(by_name), {"defectedTo", "wentOverTo"})
        self.assertIn("defectedTo", by_name["wentOverTo"]["similarRequests"])

    def test_a_need_the_registry_already_has_is_not_queued(self):
        queue = {"requests": []}
        self.assertEqual(merge(queue, [need("commanded", "exercised command")], REGISTRY)["known"], 1)
        self.assertEqual(queue["requests"], [])

    def test_open_requests_reach_the_lens_packet(self):
        queue = {"requests": []}
        merge(queue, [need()], REGISTRY)
        text = open_requests_text(queue)
        self.assertIn("- defectedTo: A person changed sides", text)
        lens = replace(load_lens("military", "roman-republic"), requested=text)
        self.assertIn("reuse one of these names", lens_text(lens))

    def test_no_queue_file_is_an_empty_queue(self):
        self.assertEqual(load_queue(Path(tempfile.gettempdir()) / "no-such-queue.json")["requests"], [])
        self.assertEqual(open_requests_text({"requests": []}), "")


class ShapeTests(unittest.TestCase):
    def queue(self):
        queue = {"requests": []}
        merge(queue, [need(), need("captured", "A force took enemy ships in an engagement."),
                      need("delegatedCommandTo", "A holder of authority gave command to a deputy.")], REGISTRY)
        return queue

    def test_acts_are_told_to_be_depicted_and_states_offered_for_reuse(self):
        queue = self.queue()
        set_shape(queue, "captured", "event", "A capture happens at a moment.", "test")
        set_shape(queue, "delegatedCommandTo", "state", "Holds over time.", "test")
        text = open_requests_text(queue)
        self.assertIn("- delegatedCommandTo:", text)
        self.assertIn("- defectedTo:", text)  # unclassified requests are still offered
        self.assertNotIn("- captured:", text)
        self.assertIn("Acts ruled events, never predicates (depict them; do not request them): captured.", text)

    def test_a_shape_records_who_and_why_and_must_be_known(self):
        queue = self.queue()
        request = set_shape(queue, "captured", "event", "A capture happens at a moment.", "curator")
        self.assertEqual(request["shape"]["by"], "curator")
        with self.assertRaisesRegex(ValueError, "a shape is one of"):
            set_shape(queue, "captured", "relationship", "x", "curator")
        with self.assertRaisesRegex(ValueError, "no request named"):
            set_shape(queue, "pillaged", "event", "x", "curator")

    def test_shapes_survive_a_later_merge(self):
        queue = self.queue()
        set_shape(queue, "captured", "event", "A moment.", "test")
        merge(queue, [need("captured", "Ships were taken.")], REGISTRY)
        (request,) = [r for r in queue["requests"] if r["name"] == "captured"]
        self.assertEqual(request["shape"]["value"], "event")


class RunTests(unittest.TestCase):
    def test_needs_from_a_lens_reading_log(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "lens-reader-military-roman-republic-x.jsonl")
            path.write_text("\n".join(json.dumps(line) for line in [
                {"lens": {"specialist": "lens-specialist:military/roman-republic"}},
                {"ref": "68.3", "predicateNeeds": [{"name": "wentOverTo", "definition": "defected",
                                                    "subject_kinds": ["Group"], "object_kinds": ["Person"],
                                                    "quotation": "went over to Caesar", "observationId": "o"}]},
            ]), encoding="utf-8")
            (found,) = needs_from_run(path)
        self.assertEqual(found["specialist"], "lens-specialist:military/roman-republic")
        self.assertEqual(found["evidence"]["ref"], "68.3")

    def test_needs_from_a_lens_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "lens-x.json")
            path.write_text(json.dumps({"polity": "Roman Republic", "readings": {"religious": {"predicate_needs": [
                {"name": "dedicatedTo", "definition": "dedicated to a god", "subject_kinds": ["Person"],
                 "object_kinds": ["Concept"], "example": "ships to Apollo"}]}}, "general": {}}), encoding="utf-8")
            (found,) = needs_from_run(path)
        self.assertEqual(found["specialist"], "lens-analyst:religious/roman-republic")


if __name__ == "__main__":
    unittest.main()
