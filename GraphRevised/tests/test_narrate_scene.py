"""The narrator rewrites only the steps that changed (narrative/narrate_scene.py): offline, with a fake client."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from GraphRevised.narrative import narrate_scene as ns


def scene(step2_text="He besieges the city."):
    steps = [
        {"id": "chr:scene:t#1", "order": 1, "title": "March", "timeWords": "spring",
         "statements": [{"id": "chr:scene:t#1.1", "text": "He marches to the city.", "basis": "sourced",
                         "voices": [{"accordingTo": "Annals", "locator": "Annals 1.1", "quotation": "marched to the city"}]}]},
        {"id": "chr:scene:t#2", "order": 2, "title": "Siege", "timeWords": "summer",
         "statements": [{"id": "chr:scene:t#2.1", "text": step2_text, "basis": "sourced",
                         "voices": [{"accordingTo": "Annals", "locator": "Annals 1.2", "quotation": "laid siege to the city"}]}]},
    ]
    s = {"id": "chr:scene:t", "steps": steps, "scope": "t", "status": "proposed", "bases": {}, "subject": "T"}
    s["contentHash"] = json.dumps(steps, sort_keys=True)[:40]
    return s


def line(step, n, text, key):
    return {"id": f"n{step}.{n}", "kind": "narration", "text": text, "keys": [key], "basis": "sourced", "voice": None,
            "estSeconds": 2.0}


class FakeClient:
    """Answers with a narration of whatever steps the request carries, and records what it was sent."""

    def __init__(self):
        self.sent = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(parse=self.parse))

    def parse(self, **req):
        given = json.loads(req["messages"][0]["content"].split("The scene (narration input):\n", 1)[1].split("\n\nThis is part", 1)[0])
        self.sent.append([st["id"] for st in given["steps"]])
        steps = [ns.Step(stepId=st["id"], lines=[ns.Line(**line(st["order"], 1, st["statements"][0]["text"], st["statements"][0]["id"]))])
                 for st in given["steps"]]
        return SimpleNamespace(model="fake", stop_reason="end_turn", _request_id="r",
                               usage=SimpleNamespace(input_tokens=1, output_tokens=1), parsed_output=ns.Narration(steps=steps))


class NarrateOnlyWhatChangedTests(unittest.TestCase):
    def run_main(self, folder, sc, *extra):
        path = Path(folder, "t.narration-input.json")
        path.write_text(json.dumps(sc), encoding="utf-8")
        client = FakeClient()
        with mock.patch("GraphRevised.proposals.passage_reader.anthropic_client", return_value=client), \
                mock.patch.object(ns, "check", return_value={"problems": [], "warnings": []}):
            code = ns.main([str(path), *extra])
        out = Path(folder, "t.narration.browser.json")
        return code, client.sent, (json.loads(out.read_text(encoding="utf-8")) if out.exists() else None)

    def test_a_fingerprint_changes_only_with_its_step(self):
        a, b = ns.step_hashes(scene()), ns.step_hashes(scene("He storms the city."))
        self.assertEqual(a["chr:scene:t#1"], b["chr:scene:t#1"])
        self.assertNotEqual(a["chr:scene:t#2"], b["chr:scene:t#2"])

    def test_only_the_changed_step_goes_to_the_model_and_the_rest_is_kept_word_for_word(self):
        with tempfile.TemporaryDirectory() as folder:
            code, sent, first = self.run_main(folder, scene())
            self.assertEqual((code, sent), (0, [["chr:scene:t#1", "chr:scene:t#2"]]))  # first time: every step
            kept_lines = first["steps"][0]["lines"]
            code, sent, second = self.run_main(folder, scene("He storms the city."))
            self.assertEqual(sent, [["chr:scene:t#2"]])
            self.assertEqual(second["steps"][0]["lines"], kept_lines)
            self.assertEqual(second["steps"][1]["lines"][0]["text"], "He storms the city.")
            self.assertEqual((second["rewritten"], second["kept"]), (["chr:scene:t#2"], ["chr:scene:t#1"]))

    def test_nothing_changed_calls_nothing_and_fresh_rewrites_all(self):
        with tempfile.TemporaryDirectory() as folder:
            self.run_main(folder, scene())
            code, sent, _ = self.run_main(folder, scene())
            self.assertEqual((code, sent), (0, []))
            code, sent, _ = self.run_main(folder, scene(), "--fresh")
            self.assertEqual(sent, [["chr:scene:t#1", "chr:scene:t#2"]])


if __name__ == "__main__":
    unittest.main()
