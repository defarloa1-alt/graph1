"""Inquiry files: the reader must locate passages itself, so guidance carries no cues.

Guidance may state a source's conventions and the rules of predicates. It may
not point at passages (locators such as 65.1 or 50.16-30) or quote the
source's own words, which would steer the reader to what it is meant to find.
"""

import json
import re
import unittest
from pathlib import Path

from GraphRevised.adapters.sources import open_source

GRAPH_REVISED = Path(__file__).resolve().parents[1]
INQUIRIES = sorted((GRAPH_REVISED / "inquiries").glob("*.json"))
QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")
LOCATOR = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("’", "'")).strip().lower()


class InquiryGuidanceTests(unittest.TestCase):
    def test_there_are_inquiries(self):
        self.assertTrue(INQUIRIES)

    def test_guidance_has_no_locators_or_source_quotations(self):
        for path in INQUIRIES:
            data = json.loads(path.read_text(encoding="utf-8"))
            source = open_source(data["source"], GRAPH_REVISED)
            text = normalize(" ".join(source.observation(ref)["passageText"] for ref in source.refs(None)))
            for line in data["guidance"]:
                with self.subTest(inquiry=path.name, guidance=line[:60]):
                    self.assertIsNone(LOCATOR.search(line), "guidance points at a passage")
                    for quoted in QUOTED.findall(line):
                        if len(quoted.split()) >= 2:
                            self.assertNotIn(normalize(quoted), text, "guidance quotes the source")

    def test_inquiries_read_whole_works(self):
        for path in INQUIRIES:
            with self.subTest(inquiry=path.name):
                self.assertNotIn("chapters", json.loads(path.read_text(encoding="utf-8"))["source"])


if __name__ == "__main__":
    unittest.main()
