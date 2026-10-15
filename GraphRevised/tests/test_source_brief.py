"""The briefing agent's deterministic checks, without a model call or the graph."""

import unittest

from GraphRevised.discovery.source_brief import BriefOutput, Convention, Evidence, check
from GraphRevised.proposals.reading_rules import normalize, steering

SAMPLE = [("1.1", "The young heir, whom the narrative calls Caesar, sailed at dawn with his friends."),
          ("1.2", "Then the queen spoke to her council at length about the war.")]
RECORD = "Work: Test history\nForm: history\nA history written two centuries after the events."
TEXT = normalize(" ".join(text for _, text in SAMPLE))


def convention(rule: str, *evidence: tuple[str, str], kind: str = "naming") -> Convention:
    return Convention(kind=kind, rule=rule, why="test", evidence=[Evidence(ref=r, quotation=q) for r, q in evidence])


class BriefCheckTests(unittest.TestCase):
    def outcome(self, *conventions: Convention):
        return check(BriefOutput(conventions=list(conventions), notes=""), SAMPLE, RECORD, TEXT)

    def test_verbatim_evidence_is_kept(self):
        kept, rejected = self.outcome(convention("Caesar denotes the heir.", ("1.1", "whom the narrative calls Caesar")))
        self.assertEqual((len(kept), rejected), (1, []))

    def test_the_record_can_be_evidence(self):
        kept, _ = self.outcome(convention("A later historian.", ("record", "written two centuries after"), kind="stance"))
        self.assertEqual(len(kept), 1)

    def test_paraphrased_unknown_or_missing_evidence_is_rejected(self):
        _, rejected = self.outcome(
            convention("Paraphrase.", ("1.1", "the narrative names him Caesar")),
            convention("Unknown ref.", ("9.9", "whom the narrative calls Caesar")),
            convention("No evidence."),
        )
        self.assertEqual([r["reason"].split(":")[0] for r in rejected],
                         ["evidence not found verbatim", "evidence not found verbatim", "no evidence"])

    def test_a_rule_that_steers_is_rejected(self):
        _, rejected = self.outcome(
            convention("See 1.2 for the council.", ("1.2", "spoke to her council at length")),
            convention("Speeches such as 'spoke to her council' are rhetoric.", ("1.2", "spoke to her council at length")),
        )
        self.assertEqual([r["reason"] for r in rejected], ["points at a passage", "quotes the source"])

    def test_apostrophes_are_not_quotations(self):
        self.assertIsNone(steering("Antony's men and the queen's ships are named by side.", TEXT))


if __name__ == "__main__":
    unittest.main()
