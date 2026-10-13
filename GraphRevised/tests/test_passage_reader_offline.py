"""Reader output to drafts (prompt v8), without a model call or a database."""

import unittest

from GraphRevised.proposals.passage_reader import (
    Inquiry, ReaderClaim, ReaderNote, ReaderOutput, ReaderPeriod, predicate_guide, to_drafts, to_notes,
    to_periods,
)
from GraphRevised.proposals.registry import load_registry

OBSERVATION = "chr:observation:test:passage"
INQUIRY = Inquiry(
    id="chr:inquiry:test", version=1, label="Test inquiry", subject={"id": "chr:subject:test", "label": "Test"},
    focus=[], scope=[], guidance=[], source={"type": "perseus-tei", "edition": "none.xml", "chapters": "1-2"},
    work_id="chr:entity:test-work", narrative_event_id="chr:entity:test-battle", calendar="julian",
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
    return to_drafts(ReaderOutput(claims=list(claims), unresolved_mentions=[], notes=[], periods=[]), OBSERVATION, "test-model", INQUIRY)


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

    def test_a_normalized_date_needs_the_inquiry_calendar(self):
        from dataclasses import replace

        output = ReaderOutput(claims=[claim(time_source_expression="in the year 31", time_quotation="in the year 31",
                                            time_edtf="-0030")], unresolved_mentions=[], notes=[], periods=[])
        produced, malformed = to_drafts(output, OBSERVATION, "test-model", replace(INQUIRY, calendar=None))
        self.assertEqual((produced, len(malformed)), ([], 1))

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

    def test_passages_of_note(self):
        passage = {"passageText": "He sat alone at the prow, his head in his hands, and spoke to no one."}
        output = ReaderOutput(claims=[], unresolved_mentions=[], periods=[], notes=[
            ReaderNote(note_type="characterization", note="Antony's despair after the flight",
                       quotation="sat alone at the prow, his head in his hands", concerns=["chr:entity:test-admiral"]),
            ReaderNote(note_type="mood", note="x", quotation="sat alone at the prow", concerns=["chr:entity:test-admiral"]),
            ReaderNote(note_type="detail", note="paraphrased", quotation="he sat by himself at the bow",
                       concerns=["chr:entity:test-admiral"]),
            ReaderNote(note_type="detail", note="outside scope", quotation="spoke to no one at all",
                       concerns=["chr:entity:elsewhere"]),
        ])
        notes, refused = to_notes(output, passage, {"chr:entity:test-admiral"})
        self.assertEqual([n["noteType"] for n in notes], ["characterization"])
        self.assertEqual(len(refused), 3)

    def test_periods_named_by_the_source(self):
        from dataclasses import replace

        passage = {"passageText": "Thus ended the Republic, which had lasted from 509 to 27 B.C., and the Empire began."}
        named = ReaderPeriod(name="the Republic", quotation="Thus ended the Republic, which had lasted",
                             time_expression="from 509 to 27 B.C.",
                             time_quotation="which had lasted from 509 to 27 B.C.", time_edtf="-0508/-0026")
        undated = ReaderPeriod(name="the Empire", quotation="27 B.C., and the Empire began", time_expression=None,
                               time_quotation=None, time_edtf=None)
        loose = ReaderPeriod(name="the Republic", quotation="Thus ended the Republic, which had lasted",
                             time_expression="for five centuries", time_quotation="which had lasted from 509",
                             time_edtf=None)
        output = ReaderOutput(claims=[], unresolved_mentions=[], notes=[], periods=[named, undated, loose])
        allowed = replace(INQUIRY, proposable_kinds=("Period",))
        periods, refused = to_periods(output, passage, allowed)
        self.assertEqual([p["name"] for p in periods], ["the Republic", "the Empire"])
        self.assertEqual(len(refused), 1)
        none, refused_all = to_periods(output, passage, INQUIRY)  # the inquiry allows no proposals
        self.assertEqual((none, len(refused_all)), ([], 3))

    def test_guide_shows_qualifiers_and_unary_predicates(self):
        guide = predicate_guide(load_registry())
        self.assertIn("occurred (occurred): Event/Period/Polity -> no object [time: required]", guide)
        self.assertIn("time: required with a role", guide)


if __name__ == "__main__":
    unittest.main()
