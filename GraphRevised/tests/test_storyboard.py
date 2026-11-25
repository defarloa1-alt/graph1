"""The storyboard specialist's code check (26a §5a, D-179): offline, on a synthetic profile."""

import json
import unittest
from pathlib import Path

from GraphRevised.narrative.storyboard import CATALOGUE, check, plan_items

CAT = json.loads(CATALOGUE.read_text(encoding="utf-8"))
PROF = {"memory": {"commemorations": 0, "depictions": 0}, "stretches": [
    {"key": "march", "members": 10, "sources": 3, "locatedPlaces": ["A", "B", "C"], "movements": 3, "grain": "months",
     "extentKm": 400, "sceneSteps": [1], "statements": {"sourced": 4}},
    {"key": "fight", "members": 12, "sources": 4, "locatedPlaces": ["C"], "movements": 0, "units": 6, "grain": "hours",
     "extentKm": 10, "sceneSteps": [2, 3], "alternatives": ["ordersOfBattle"], "statements": {"sourced": 6}},
    {"key": "memory", "members": 2, "sources": 1, "locatedPlaces": [], "grain": None, "extentKm": 0}]}


def seg(stretches, kind, with_kinds=(), transition="open", why=("extent 400 km, 3 movements",), gaps=()):
    return {"stretches": list(stretches), "title": "t", "kind": kind, "with_kinds": list(with_kinds), "why": list(why),
            "transition": transition, "gaps": list(gaps)}


class StoryboardCheckTests(unittest.TestCase):
    def test_a_sound_storyboard_passes(self):
        sb = {"segments": [seg(["march"], "movement-scene"),
                           seg(["fight"], "battle-scene", ["order-of-battle", "disagreement"], "zoom-in", ["grain hours, 10 km, 6 units"]),
                           seg(["memory"], "timeline", why=["2 events, no located places"])]}
        result = check(sb, PROF, CAT)
        self.assertEqual(result["problems"], [])

    def test_a_kind_whose_needs_the_profile_does_not_meet_is_a_problem(self):
        sb = {"segments": [seg(["march"], "battle-scene"), seg(["fight"], "battle-scene"), seg(["memory"], "memory-reception")]}
        problems = " | ".join(check(sb, PROF, CAT)["problems"])
        self.assertIn("segment 1 (battle-scene): needs grain hours", problems)
        self.assertIn("segment 3 (memory-reception): needs any of", problems)

    def test_every_stretch_once_in_order_and_no_overlay_as_a_kind(self):
        sb = {"segments": [seg(["fight"], "narration"), seg(["march"], "movement-scene")]}
        problems = " | ".join(check(sb, PROF, CAT)["problems"])
        self.assertIn("an overlay", problems)
        self.assertIn("not covered: ['memory']", problems)
        self.assertIn("not in the timeline's order", problems)

    def test_a_disagreement_needs_two_versions(self):
        sb = {"segments": [seg(["march"], "movement-scene", ["disagreement"]), seg(["fight"], "battle-scene"),
                           seg(["memory"], "timeline", why=["2 events"])]}
        self.assertTrue(any("disagreement shown with it needs" in p for p in check(sb, PROF, CAT)["problems"]))

    def test_approved_segments_become_generate_items_and_gaps_become_items(self):
        sb = {"id": "chr:storyboard:t", "subject": {"id": "chr:entity:t"}, "segments": [
            {"order": 1, "status": "approved", "kind": "movement-scene", "why": ["3 movements"], "gaps": [
                {"what": "coins", "becomes": "source-task", "note": "commemorative issues", "source": "nomisma"},
                {"what": "a reading", "becomes": "question", "note": "open", "source": None}]},
            {"order": 2, "status": "proposed", "kind": "battle-scene", "why": ["x"], "gaps": []}]}
        sb["segments"].append({"order": 3, "status": "approved", "kind": "battle-scene", "why": ["x"], "gaps": []})
        items, held = plan_items(sb, Path("storyboards/t.storyboard.json"), None)
        self.assertEqual([(i["action"], i["target"]) for i in items], [("GENERATE", "chr:entity:t"), ("REGISTER", "nomisma")])
        self.assertEqual(items[0]["call"]["arguments"],
                         ["--kind", "scene-movement", "--storyboard", str(Path("storyboards/t.storyboard.json")), "--segment", "1"])
        self.assertEqual(items[1]["origin"], {"storyboard": "chr:storyboard:t", "segment": 1, "gap": 0})
        self.assertEqual(items[1]["call"]["worker"], "manual")
        self.assertTrue(any("no worker draws scene-battle" in h for h in held))  # battle scenes are not built


if __name__ == "__main__":
    unittest.main()
