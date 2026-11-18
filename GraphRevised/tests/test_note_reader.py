"""The note reader's triage, offline: checked picks, the request, and the write-back into the note."""
import tempfile
import unittest
from pathlib import Path

import yaml

from GraphRevised.capture.note_reader import (NoteTriage, PickedEntity, PickedLens, checked_triage,
                                              triage_request, unfilled, write_triage)
from GraphRevised.capture.notes import read_note

NOTE = """---\r
chrystallum: note\r
id:\r
noteType: excerpt\r
page: 148\r
work: chr:entity:a-book\r
concerns:\r
  - chr:entity:replace-me\r
related:\r
tags:\r
---\r
\r
> [!quote]\r
> The promontory lacked fresh water.[^1]\r
\r
[^1]: Dio 50.12.7.\r
\r
Geography mattered.\r
"""

CANDIDATES = [{"id": "chr:entity:promontory", "label": "Actium promontory", "kind": "Place", "status": "provisional"},
              {"id": "chr:entity:cleopatra-v", "label": "Cleopatra V", "kind": "Person", "status": "proposed"}]
LENSES = [{"id": "military", "label": "Military", "purpose": "Armed force and supply."}]


class TriageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "Note.md"
        self.path.write_bytes(NOTE.encode("utf-8"))

    def tearDown(self):
        self.directory.cleanup()

    def test_only_candidates_and_catalogued_lenses_are_kept(self):
        triage = NoteTriage(concerns=[PickedEntity(id="chr:entity:promontory", reason="the place described"),
                                      PickedEntity(id="chr:entity:invented", reason="x")],
                            lenses=[PickedLens(id="military", reason="supply"), PickedLens(id="geography", reason="x")],
                            missing_lens="geography")
        concerns, lenses, dropped = checked_triage(triage, CANDIDATES, LENSES)
        self.assertEqual([c["id"] for c in concerns], ["chr:entity:promontory"])
        self.assertEqual([l["id"] for l in lenses], ["military"])
        self.assertEqual(len(dropped), 2)

    def test_the_request_carries_quote_footnotes_and_curator_text_but_no_placeholder(self):
        note = read_note(self.path)
        self.assertTrue(unfilled(note))
        request = triage_request("claude-sonnet-5-5", note, CANDIDATES, LENSES, {"chr:entity:cleopatra-v": "a queen"})
        user = request["messages"][0]["content"]
        for part in ("lacked fresh water.", "[1] Dio 50.12.7.", "Geography mattered.", "Cleopatra V | Person | a queen"):
            self.assertIn(part, user)
        self.assertNotIn("[^1]", user)

    def test_write_back_replaces_the_placeholder_and_adds_lens_tags_only(self):
        write_triage(self.path, [{"id": "chr:entity:promontory", "label": "Actium promontory", "reason": "the place"}],
                     [{"id": "military", "reason": "supply"}])
        raw = self.path.read_bytes().decode("utf-8")
        self.assertIn("\r\n", raw)
        self.assertNotIn("replace-me", raw)
        self.assertIn("  - chr:entity:promontory  # suggested: Actium promontory (the place)", raw)
        note = read_note(self.path)
        self.assertEqual(note.ids("concerns"), ["chr:entity:promontory"])
        self.assertEqual(note.ids("tags"), ["lens/military"])
        self.assertEqual(note.text, "Geography mattered.")
        self.assertEqual(raw.split("---", 2)[2], NOTE.split("---", 2)[2])  # the body is untouched
        front = yaml.safe_load(raw.split("---", 2)[1])
        self.assertIsNone(front["related"])


if __name__ == "__main__":
    unittest.main()
