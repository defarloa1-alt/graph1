"""The passage finder's name step, without a model call or the graph."""

import unittest

from GraphRevised.discovery.passage_finder import event_terms, name_candidates
from GraphRevised.proposals.passage_reader import Inquiry
from GraphRevised.discovery.passage_finder import actor_terms

TEXTS = {
    "1.1": "The general marched north in spring.",
    "1.2": "Before the fight the fleets lay idle.",
    "1.3": "So came the Pharsalian day, long remembered.",
    "1.4": "Afterwards the survivors scattered.",
    "1.5": "Marcellus wrote to Fabius about the harvest.",
    "1.6": "Marcellus dined alone.",
}


def inquiry(scope):
    return Inquiry(id="chr:inquiry:test", version=1, label="Test", subject={"id": "s", "label": "s"}, focus=[],
                   scope=scope, guidance=[], source={}, work_id="chr:entity:test-work", narrative_event_id=None)


class NameStepTests(unittest.TestCase):
    def test_the_event_its_neighbours_and_two_actors_are_candidates(self):
        actors = actor_terms(inquiry([
            {"id": "chr:entity:a", "kind": "Person", "label": "Marcus Claudius Marcellus"},
            {"id": "chr:entity:b", "kind": "Person", "label": "Quintus Fabius", "aliases": ["Cunctator"]},
            {"id": "chr:entity:place", "kind": "Place", "label": "Pharsalus"},
            {"id": "chr:entity:depicted:x", "kind": "Event", "label": "Marcellus sails"},
        ]))
        found = name_candidates(TEXTS, event_terms("Battle of Pharsalus"), actors)
        self.assertEqual(found, {"1.3": "names the event", "1.2": "next to a passage naming the event",
                                 "1.4": "next to a passage naming the event", "1.5": "names 2 in-scope actors"})

    def test_generic_words_of_the_label_are_not_the_event(self):
        self.assertTrue(any(p.search("by Lake Trasimene") for p in event_terms("Battle of Lake Trasimene")))
        self.assertFalse(any(p.search("The battle began.") for p in event_terms("Battle of Pharsalus")))


class FakeSource:
    def refs(self, selection):
        return list(TEXTS)

    def observation(self, ref):
        return {"passageText": TEXTS[ref]}


class FakeClient:
    """Answers every batch as the model does, refs wrapped in brackets; the first passage is not relevant."""

    def __init__(self):
        self.beta = self
        self.messages = self

    def parse(self, *, messages, **_):
        from types import SimpleNamespace
        from GraphRevised.discovery.passage_finder import FinderOutput, Verdict
        refs = [line.split("]")[0] + "]" for line in messages[0]["content"].split("\n") if line.startswith("[")]
        verdicts = [Verdict(ref=r, relevant=i > 0, why="test") for i, r in enumerate(refs)]
        return SimpleNamespace(model="fake", stop_reason="end_turn", parsed_output=FinderOutput(verdicts=verdicts),
                               usage=SimpleNamespace(input_tokens=1, output_tokens=1))


class ScreenTests(unittest.TestCase):
    def test_bracketed_refs_are_matched_and_verdicts_kept(self):
        from GraphRevised.discovery.passage_finder import find
        found = find(FakeClient(), "fake", inquiry([]), FakeSource(), {"label": "Battle of Pharsalus"}, batch_size=20)
        self.assertEqual(found["selected"], ["1.3", "1.4"])
        self.assertEqual(found["verdicts"]["1.2"]["why"], "test")


if __name__ == "__main__":
    unittest.main()
