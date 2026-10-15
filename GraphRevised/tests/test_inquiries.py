"""Inquiry files: the reader must locate passages itself, so guidance carries no cues.

Guidance may state a source's conventions and the rules of predicates. It may
not point at passages (locators such as 65.1 or 50.16-30) or quote the
source's own words, which would steer the reader to what it is meant to find.
"""

import json
import unittest
from pathlib import Path

from GraphRevised.adapters.sources import open_source
from GraphRevised.proposals.passage_reader import inquiry_sources
from GraphRevised.proposals.reading_rules import brief_guidance, load_brief, load_reading_rules, normalize, steering

GRAPH_REVISED = Path(__file__).resolve().parents[1]
INQUIRIES = sorted((GRAPH_REVISED / "inquiries").glob("*.json"))
RULES = load_reading_rules()
SHARED = [*RULES.general, *RULES.event_inquiry, *RULES.predicates.values(),
          *(line for lines in RULES.by_form.values() for line in lines)]


class InquiryGuidanceTests(unittest.TestCase):
    def test_there_are_inquiries(self):
        self.assertTrue(INQUIRIES)

    def test_guidance_has_no_locators_or_source_quotations(self):
        for path in INQUIRIES:
            data = json.loads(path.read_text(encoding="utf-8"))
            # An event inquiry's shared guidance is checked against every source it reads.
            # So are the shared rules and the source's brief, which the reader also sees.
            for config in inquiry_sources(data):
                source = open_source(config, GRAPH_REVISED)
                text = normalize(" ".join(source.observation(ref)["passageText"] for ref in source.refs(None)))
                lines = (data.get("guidance", []) + config.get("guidance", []) + SHARED
                         + brief_guidance(load_brief(config["workId"])))
                for line in lines:
                    with self.subTest(inquiry=path.name, source=config["workId"], guidance=line[:60]):
                        self.assertIsNone(steering(line, text))

    def test_inquiries_read_whole_works(self):
        for path in INQUIRIES:
            for config in inquiry_sources(json.loads(path.read_text(encoding="utf-8"))):
                with self.subTest(inquiry=path.name, source=config["workId"]):
                    self.assertNotIn("chapters", config)


if __name__ == "__main__":
    unittest.main()
