"""Registry v17 and draft v8 (44, D-153): Questions, Positions, and who held them. Offline."""
import typing
import unittest

from GraphRevised.proposals.registry import REGISTRY_PATH, assertion_id, load_registry, qualifier_signature
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.tests.test_proposals_offline import FakeReader, entity

QUESTION = entity("chr:entity:test-question", "Question")
POSITION = entity("chr:entity:test-position", "Position")
BATTLE = entity("chr:entity:test-battle", "Event")
REPORTER = entity("chr:entity:test-reconsideration", "Work") | {"form": "history"}
HOLDER = entity("chr:entity:test-campaign-study", "Work") | {"form": "history"}
TEXT = ("Kromayer revived the view that Antony meant to break out in 1899, and it has been the dominant view "
        "ever since; Tarn rejected it.")
PASSAGE = {"id": "chr:observation:test-reconsideration-p608", "observationKind": "passage", "status": "observed",
           "sourceSystem": "Test", "workId": REPORTER["id"], "editorialNotes": [], "passageText": TEXT}


def draft(predicate, subject, obj=None, **extra):
    return ProposalDraft(
        predicate=predicate, subject_id=subject["id"], object_id=obj["id"] if obj else None,
        observation_ids=(PASSAGE["id"],), quotations=(Quotation(observation_id=PASSAGE["id"], text=TEXT),),
        rationale="historiography test draft", proposed_by="test", mode="attributed",
        attributed_to=REPORTER["id"], **extra)


def quote(supports, text):
    return QualifierQuotation(observation_id=PASSAGE["id"], supports=supports, text=text)


SINCE_1899 = TimeQualifier(source_expression="1899", edtf="1899/..", calendar="gregorian", normalization_basis="source")


class RegistryV17Tests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry(REGISTRY_PATH.with_name("predicates.v17.json"))
        self.reader = FakeReader([QUESTION, POSITION, BATTLE, REPORTER, HOLDER], [PASSAGE])

    def check(self, d):
        return validate(d, self.reader, self.registry)

    def test_the_kinds_and_predicates(self):
        self.assertEqual(self.registry.version, "predicates-v17")
        self.assertTrue({"Question", "Position"} <= set(self.registry.entity_kinds))
        for name in ("about", "answers", "holds", "rejects", "hadReception"):
            self.assertEqual(self.registry.get(name).category, "interpretive", name)
        for name in ("holds", "rejects", "hadReception"):  # always a voice's claim, never ours
            self.assertEqual(self.registry.get(name).modes, frozenset({"attributed"}), name)
        self.assertTrue(self.registry.get("hadReception").unary)
        self.assertEqual(self.registry.get("holds").subject_kinds, frozenset({"Work"}))

    def test_the_registry_values_match_the_draft_schema(self):
        hints = typing.get_type_hints(ProposalDraft)
        self.assertEqual(set(typing.get_args(typing.get_args(hints["stance"])[0])), set(self.registry.stances))
        self.assertEqual(set(typing.get_args(typing.get_args(hints["reception"])[0])), set(self.registry.receptions))

    def test_a_reported_holder_with_its_stance_validates(self):
        d = draft("holds", HOLDER, POSITION, stance="adopts", time=TimeQualifier(
            source_expression="1899", edtf="1899", calendar="gregorian", normalization_basis="source"),
            qualifier_quotations=(quote("stance", "Kromayer revived the view"), quote("time", "in 1899")))
        result = self.check(d)
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)

    def test_a_stance_needs_its_quotation_and_only_holds_takes_one(self):
        self.assertIn("a stance drawn from a passage needs a stance quotation",
                      self.check(draft("holds", HOLDER, POSITION, stance="originates")).reasons)
        self.assertIn("rejects takes no stance", self.check(draft("rejects", HOLDER, POSITION, stance="adopts")).reasons)

    def test_holds_is_never_our_own_statement(self):
        d = ProposalDraft(predicate="holds", subject_id=HOLDER["id"], object_id=POSITION["id"],
                          observation_ids=(PASSAGE["id"],),
                          quotations=(Quotation(observation_id=PASSAGE["id"], text=TEXT),),
                          rationale="historiography test draft", proposed_by="test")
        self.assertIn("holds does not allow mode asserted", self.check(d).reasons)

    def test_a_question_is_about_an_event_and_a_position_answers_it(self):
        self.assertEqual(self.check(draft("about", QUESTION, BATTLE)).outcome, Outcome.VALID)
        self.assertEqual(self.check(draft("answers", POSITION, QUESTION)).outcome, Outcome.VALID)
        self.assertNotEqual(self.check(draft("about", QUESTION, HOLDER)).outcome, Outcome.VALID)
        self.assertNotEqual(self.check(draft("holds", BATTLE, POSITION)).outcome, Outcome.VALID)

    def test_reception_is_the_claim_and_stance_is_not(self):
        dominant = draft("hadReception", POSITION, time=SINCE_1899, reception="dominant",
                         qualifier_quotations=(quote("time", "1899"), quote("reception", "the dominant view")))
        result = self.check(dominant)
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)
        minority = dominant.model_copy(update={"reception": "minority"})
        ids = {assertion_id(d.predicate, d.subject_id, None, qualifier_signature(d)) for d in (dominant, minority)}
        self.assertEqual(len(ids), 2)
        adopts = draft("holds", HOLDER, POSITION, stance="adopts")
        originates = adopts.model_copy(update={"stance": "originates"})
        self.assertEqual(qualifier_signature(adopts), qualifier_signature(originates))

    def test_a_reception_drawn_from_a_passage_needs_its_quotation(self):
        d = draft("hadReception", POSITION, time=SINCE_1899, reception="dominant",
                  qualifier_quotations=(quote("time", "1899"),))
        self.assertIn("a reception drawn from a passage needs a reception quotation", self.check(d).reasons)


if __name__ == "__main__":
    unittest.main()
