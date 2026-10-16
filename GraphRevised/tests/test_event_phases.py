"""The event-phases agent's deterministic parts, without a model call or the graph."""

import unittest
from types import SimpleNamespace

from GraphRevised.discovery.event_phases import (
    PlacementOutput, Placement, drafts, exemplars, phase_id, place,
)

EVENT = "chr:entity:battle-of-test"
SPINE = {"decidedBy": "Curator", "decidedAt": "2026-01-01", "phases": [
    {"key": "before", "label": "Before", "scope": "What came before."},
    {"key": "during", "label": "During", "scope": "The fighting."},
    {"key": "empty", "label": "Empty", "scope": "Nothing is placed here."},
]}


def depicted(n, work):
    return {"id": f"chr:entity:depicted:{work}:e{n}", "label": f"event {n}", "workId": f"chr:entity:{work}",
            "work": work, "form": "history", "observationId": f"chr:observation:{work}:{n}",
            "quotation": f"the words of event {n} in {work}"}


class FakeClient:
    """Places the first event in 'before', the second in an unknown phase, and returns nothing for the rest."""

    def __init__(self):
        self.beta = self
        self.messages = self

    def parse(self, **_):
        output = PlacementOutput(placements=[Placement(ref="[e1]", phase="before", why="test"),
                                             Placement(ref="e2", phase="nowhere", why="test")])
        return SimpleNamespace(model="fake", stop_reason="end_turn", parsed_output=output,
                               usage=SimpleNamespace(input_tokens=1, output_tokens=1))


class PhaseTests(unittest.TestCase):
    def test_placements_are_checked_against_the_spine(self):
        events = [depicted(1, "a"), depicted(2, "a"), depicted(3, "a")]
        placed, calls = place(FakeClient(), "fake", {"label": "Battle of Test"}, SPINE, "a", events)
        self.assertEqual(placed[events[0]["id"]], {"phase": "before", "why": "test"})
        self.assertIsNone(placed[events[1]["id"]]["phase"])
        self.assertIn("unknown phase", placed[events[1]["id"]]["why"])
        self.assertEqual(placed[events[2]["id"]]["why"], "unplaced: no placement returned")
        self.assertEqual(len(calls), 1)

    def test_a_phase_rests_on_the_first_event_of_each_work_most_placed_first(self):
        members = [depicted(1, "a"), depicted(2, "b"), depicted(3, "b"), depicted(4, "c")]
        self.assertEqual([m["id"] for m in exemplars(members, limit=2)],
                         ["chr:entity:depicted:b:e2", "chr:entity:depicted:a:e1"])

    def test_drafts_are_asserted_part_of_claims_with_the_depicting_words(self):
        events = {e["id"]: e for e in [depicted(1, "a"), depicted(2, "b"), depicted(3, "b")]}
        placed = {"chr:entity:depicted:a:e1": {"phase": "during", "why": "a fight"},
                  "chr:entity:depicted:b:e2": {"phase": "during", "why": "a fight"},
                  "chr:entity:depicted:b:e3": {"phase": None, "why": "outside"}}
        out, members = drafts(EVENT, SPINE, "chr:inquiry:test", placed, events, "fake")
        self.assertEqual(members["empty"], [])
        keys = [k for k, _ in out]
        self.assertEqual(keys, ["during", "chr:entity:depicted:a:e1", "chr:entity:depicted:b:e2"])
        phase_draft = out[0][1]
        self.assertEqual((phase_draft.subject_id, phase_draft.object_id), (phase_id(EVENT, "during"), EVENT))
        self.assertEqual(phase_draft.mode, "asserted")
        self.assertEqual(len(phase_draft.observation_ids), 2)
        member_draft = out[1][1]
        self.assertEqual(member_draft.object_id, "chr:entity:phase:battle-of-test:during")
        self.assertEqual(member_draft.quotations[0].text, "the words of event 1 in a")


if __name__ == "__main__":
    unittest.main()
