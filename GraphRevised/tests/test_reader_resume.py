"""--unread: a reading resumes where a stored run of the same source and lens stopped (D-175). Offline."""

import json
import tempfile
import unittest
from pathlib import Path

from GraphRevised.proposals.passage_reader import read_refs


def log(directory, name, head, refs):
    lines = [head] + [{"ref": r} if not r.startswith("!") else {"ref": r[1:], "error": "refusal"} for r in refs]
    Path(directory, name).write_text("\n".join(json.dumps(line) for line in lines) + "\n")


class ReaderResumeTests(unittest.TestCase):
    def test_only_stored_error_free_readings_of_the_same_source_and_lens_count(self):
        with tempfile.TemporaryDirectory() as d:
            head = {"inquiry": "chr:inquiry:t", "workId": "chr:entity:w", "submit": True, "lens": {"id": "military"}}
            log(d, "lens-reader-military-a.jsonl", head, ["1.1", "1.2", "!1.3"])
            log(d, "lens-reader-military-b.jsonl", head | {"submit": False}, ["1.4"])            # a dry run
            log(d, "lens-reader-political-c.jsonl", head | {"lens": {"id": "political"}}, ["1.5"])
            log(d, "passage-reader-d.jsonl", head | {"lens": None}, ["1.6"])                     # the general reader
            log(d, "lens-reader-military-e.jsonl", head | {"workId": "chr:entity:other"}, ["1.7"])
            log(d, "lens-reader-military-f.jsonl", head | {"lens": "military"}, ["1.8"])  # an older log's form
            self.assertEqual(read_refs("chr:inquiry:t", "chr:entity:w", "military", Path(d)), {"1.1", "1.2", "1.8"})
            self.assertEqual(read_refs("chr:inquiry:t", "chr:entity:w", None, Path(d)), {"1.6"})


if __name__ == "__main__":
    unittest.main()
