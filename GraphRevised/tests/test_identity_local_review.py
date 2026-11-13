"""Offline tests for local-first unresolved-mention review."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from GraphRevised.identity.queue import local_review


class Result:
    def __init__(self, rows):
        self.rows = rows

    def data(self):
        return self.rows


class Transaction:
    def run(self, query, *, ids):
        return Result([{"id": item, "status": "provisional", "description": None,
                        "authorities": [{"system": "Wikidata", "identifier": "Q1", "status": "accepted"}]}
                       for item in ids])


class LocalReviewTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.inquiry = self.root / "inquiry.json"
        self.inquiry.write_text(json.dumps({"id": "test", "version": 1,
                                            "sources": [{"workId": "work1"}, {"workId": "work2"}]}),
                                encoding="utf-8")

    def run_file(self, filename, work, name="Octavius", version=1, **record):
        path = self.root / filename
        header = {"inquiry": "test", "inquiryVersion": version, "workId": work}
        passage = {"ref": "1.1", "observationId": f"obs:{work}",
                   "unresolvedMentions": [{"name": name, "quotation": "Octavius came", "note": "reader lead"}]}
        passage.update(record)
        path.write_text(json.dumps(header) + "\n" + json.dumps(passage) + "\n", encoding="utf-8")
        return path

    @patch("GraphRevised.identity.queue.local_candidates")
    def test_multiple_runs_preserve_context_and_local_identity_leads(self, search):
        search.return_value = [
            {"id": "chr:entity:augustus", "label": "Augustus", "kind": "Person",
             "score": 0.8, "matched": "Octavius Caesar"},
            {"id": "chr:entity:father", "label": "Gaius Octavius", "kind": "Person",
             "score": 0.8, "matched": "Gaius Octavius"},
            {"id": "chr:entity:depicted:other", "label": "Octavius", "kind": "Event",
             "score": 1.0, "matched": "Octavius"},
        ]
        runs = [self.run_file("first.jsonl", "work1"), self.run_file("second.jsonl", "work2")]
        report = local_review(self.inquiry, runs, Transaction(), limit_per_kind=1)
        entry = report["entries"][0]
        self.assertEqual(len(entry["occurrences"]), 2)
        self.assertEqual({o["workId"] for o in entry["occurrences"]}, {"work1", "work2"})
        self.assertEqual(entry["occurrences"][0]["readerNote"], "reader lead")
        self.assertEqual(entry["candidateCountsByKind"], {"Person": 2})
        self.assertEqual(entry["truncatedKinds"], ["Person"])
        self.assertEqual(entry["candidates"][0]["authorities"][0]["status"], "accepted")
        self.assertEqual(report["status"], "needs-review")
        self.assertEqual(len(report["runs"][0]["sha256"]), 64)
        self.assertEqual(search.call_count, 1)
        self.assertEqual(search.call_args.kwargs, {"threshold": 0.5, "limit": None})

    def test_wrong_version_source_failed_passage_and_duplicate_runs_refused(self):
        for path in (self.run_file("version.jsonl", "work1", version=2),
                     self.run_file("source.jsonl", "unknown"),
                     self.run_file("error.jsonl", "work1", error="no parsed output")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                local_review(self.inquiry, [path], Transaction())
        path = self.run_file("duplicate.jsonl", "work1")
        with self.assertRaises(ValueError):
            local_review(self.inquiry, [path, path], Transaction())

    def test_incomplete_passage_and_header_only_run_refused(self):
        incomplete = self.run_file("incomplete.jsonl", "work1", unresolvedMentions=None)
        with self.assertRaises(ValueError):
            local_review(self.inquiry, [incomplete], Transaction())
        empty = self.root / "empty.jsonl"
        empty.write_text('{"inquiry":"test","inquiryVersion":1,"workId":"work1"}\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            local_review(self.inquiry, [empty], Transaction())
