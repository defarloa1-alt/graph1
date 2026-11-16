"""Registry v15 bounds: an inception and a dissolution each evidence one end of a span (offline)."""

import unittest

from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, TimeQualifier
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.tests.test_proposals_offline import FakeReader, entity, observation

STATE = entity("chr:entity:test-state", "Polity", "Q1")


def dated(observation_id, pid, edtf):
    return {**observation(observation_id, "Q1", pid, None), "statementTimeEdtf": edtf,
            "statementTimeCalendar": "julian", "statementTimeMode": "during", "statementQualifiers": "{}"}


BEGAN = dated("chr:observation:began", "P571", "-0508")
ENDED = dated("chr:observation:ended", "P576", "-0026-01-16")
DECADE = dated("chr:observation:decade", "P576", "-0039/-0030")


def span(edtf, *observations):
    return ProposalDraft(
        predicate="occurred", subject_id=STATE["id"], observation_ids=tuple(o["id"] for o in observations),
        time=TimeQualifier(source_expression="inception; dissolved (Wikidata)", edtf=edtf,
                           calendar="julian", normalization_basis="source"),
        rationale="Wikidata's inception and dissolution, the best-ranked values.", proposed_by="test")


class SpanBoundTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.reader = FakeReader([STATE], [BEGAN, ENDED, DECADE])

    def outcome(self, draft):
        return validate(draft, self.reader, self.registry)

    def test_two_statements_evidence_the_two_ends_of_one_span(self):
        result = self.outcome(span("-0508/-0026-01-16", BEGAN, ENDED))
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)

    def test_each_end_must_match_its_statement(self):
        result = self.outcome(span("-0507/-0026-01-16", BEGAN, ENDED))
        self.assertEqual(result.outcome, Outcome.INVALID)
        self.assertTrue(any("start is not the time chr:observation:began" in r for r in result.reasons), result.reasons)
        result = self.outcome(span("-0508/-0025", BEGAN, ENDED))
        self.assertTrue(any("end is not the time chr:observation:ended" in r for r in result.reasons), result.reasons)

    def test_a_decade_end_is_compared_by_its_outer_year(self):
        self.assertEqual(self.outcome(span("-0508/-0030", BEGAN, DECADE)).outcome, Outcome.VALID)

    def test_the_proposer_never_drafts_a_span_from_one_end(self):
        result = drafts_from_observation(BEGAN, self.reader, self.registry)
        self.assertEqual(result.drafts, ())
        self.assertTrue(any("no registered predicate" in u for u in result.unresolved))


if __name__ == "__main__":
    unittest.main()
