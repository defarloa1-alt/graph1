"""Coverage report against "done" (41 §4): the offline parts. No graph, no model."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from GraphRevised.discovery import coverage_report as cr


class CoverageReportTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.lenses = self.dir / "lenses.json"
        self.lenses.write_text(json.dumps({"lenses": [
            {"id": "general", "questions": ["Why does it matter, and to whom: contemporaries, later writers?"]},
            {"id": "military", "questions": ["Which forces took part?", "What happened to the forces afterwards: discharge, settlement?"]},
        ]}))
        patches = [mock.patch.object(cr, "RUNS", self.dir), mock.patch.object(cr, "LENSES", self.lenses)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def write_run(self, name, lines):
        (self.dir / name).write_text("\n".join(json.dumps(line) for line in lines))

    def test_lens_questions_are_matched_even_when_restated(self):
        (self.dir / "lens-x.json").write_text(json.dumps({
            "entity": {"id": "e"}, "createdAt": "2026-01-01",
            "readings": {"military": {"findings": [
                {"question": "Which forces took part?", "strength": "thin"},
                {"question": "What happened to the forces afterwards?", "strength": "absent"}], "gaps": [1]}},
            "general": {"findings": [], "gaps": []}}))
        result = cr.lens_questions("e")
        self.assertEqual(result["lenses"]["military"], {"questions": 2, "thin": 1, "open": 1, "gaps": 1})
        self.assertEqual(result["lenses"]["general"]["unmarked"], 1)
        self.assertFalse(result["met"])

    def test_no_analysis_is_not_met(self):
        self.assertEqual(cr.lens_questions("e"), {"analysis": None, "lenses": {}, "met": False})

    def test_reads_count_by_reader_and_dry_runs_do_not(self):
        inquiry = {"id": "inq", "narrativeEventId": "e", "sources": [{"workId": "w", "voice": "W"}]}
        self.write_run("passage-reader-1.jsonl", [{"inquiry": "inq", "workId": "w", "lens": None, "submit": True},
                                                  {"ref": "1"}, {"ref": "2"}])
        self.write_run("lens-reader-military-1.jsonl", [{"inquiry": "inq", "workId": "w", "lens": {"id": "military"},
                                                         "submit": False}, {"ref": "1"}])
        self.write_run("passage-reader-2.jsonl", [{"inquiry": "other", "narrativeEventId": "f", "workId": "w"}, {"ref": "3"}])
        with mock.patch.object(cr, "assigned", return_value=(["1", "2", "3"], "passage finder")):
            result = cr.reading(inquiry, ["military"])
        readers = result["sources"][0]["readers"]
        self.assertEqual(readers["general"], {"read": 2, "dryOnly": 0})
        self.assertEqual(readers["military"], {"read": 0, "dryOnly": 1})
        self.assertFalse(result["met"])


if __name__ == "__main__":
    unittest.main()
