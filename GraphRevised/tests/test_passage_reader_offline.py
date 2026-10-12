"""Reader output to drafts (prompt v8), without a model call or a database."""

import unittest

from GraphRevised.proposals.passage_reader import Inquiry, ReaderClaim, ReaderOutput, predicate_guide, to_drafts
from GraphRevised.proposals.registry import load_registry

OBSERVATION = "chr:observation:test:passage"
INQUIRY = Inquiry(
    id="chr:inquiry:test", version=1, label="Test inquiry", subject={"id": "chr:subject:test", "label": "Test"},
    focus=[], scope=[], guidance=[], source={"type": "perseus-tei", "edition": "none.xml", "chapters": "1-2"},
    work_id="chr:entity:test-work", narrative_event_id="chr:entity:test-battle",
)


def claim(**extra):
    fields = dict(
        predicate="commanded", subject_id="chr:entity:test-admiral", object_id="chr:entity:test-wing",
        quotation="the admiral, as legate, held the left wing", rationale="The passage names his wing.",
        relevance="He led part of the fleet in the battle.", ambiguities=[], role_id=None, role_quotation=None,
        time_source_expression=None, time_quotation=None, time_edtf=None, context_id=None, context_quotation=None,
    )
    return ReaderClaim(**(fields | extra))


def drafts(*claims):
    return to_drafts(ReaderOutput(claims=list(claims), unresolved_mentions=[]), OBSERVATION, "test-model", INQUIRY)


class ReaderDraftTests(unittest.TestCase):
    def test_claims_are_attributed_to_the_inquiry_work(self):
        (draft,), malformed = drafts(claim())
        self.assertEqual(malformed, [])
        self.assertEqual((draft.mode, draft.attributed_to), ("attributed", "chr:entity:test-work"))

    def test_qualifiers_carry_their_own_quotations(self):
        (draft,), _ = drafts(claim(
            role_id="chr:entity:test-legatus", role_quotation="as legate",
            time_source_expression="the sixth hour", time_quotation="it was now the sixth hour",
            context_id="chr:entity:test-battle",
        ))
        self.assertEqual({(q.supports, q.text) for q in draft.qualifier_quotations},
                         {("role", "as legate"), ("time", "it was now the sixth hour")})
        self.assertEqual(draft.time.source_expression, "the sixth hour")
        self.assertIsNone(draft.time.edtf)
        self.assertEqual(draft.context_basis, "inquiry")

    def test_a_stated_date_is_normalized_as_the_source_gives_it(self):
        (draft,), _ = drafts(claim(time_source_expression="in the year 31", time_quotation="in the year 31 they fought",
                                   time_edtf="-0030"))
        self.assertEqual((draft.time.calendar, draft.time.normalization_basis), ("julian", "source"))

    def test_qualifiers_without_their_spans_are_malformed(self):
        cases = (
            claim(role_id="chr:entity:test-legatus"),
            claim(time_source_expression="the sixth hour"),
            claim(context_id="chr:entity:other-event"),
        )
        produced, malformed = drafts(*cases)
        self.assertEqual(produced, [])
        self.assertEqual(len(malformed), 3)

    def test_another_event_as_context_needs_a_quotation(self):
        (draft,), _ = drafts(claim(context_id="chr:entity:other-event", context_quotation="at the other battle"))
        self.assertEqual(draft.context_basis, "quotation")

    def test_unary_claims_have_no_object(self):
        (draft,), _ = drafts(claim(predicate="occurred", subject_id="chr:entity:test-battle", object_id=None,
                                   time_source_expression="on the fifth", time_quotation="but on the fifth"))
        self.assertIsNone(draft.object_id)

    def test_guide_shows_qualifiers_and_unary_predicates(self):
        guide = predicate_guide(load_registry())
        self.assertIn("occurred (occurred): Event -> no object [time: required]", guide)
        self.assertIn("time: required with a role", guide)


if __name__ == "__main__":
    unittest.main()
