"""Work containment in the versioned predicate registry."""

import unittest

from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.tests.test_proposals_offline import FakeReader, entity, observation

LIFE = entity("chr:entity:test-life", "Work", "Q900010")
COLLECTION = entity("chr:entity:test-collection", "Work", "Q900011")
EVENT = entity("chr:entity:test-event", "Event")
P361 = observation("chr:observation:test-part-of", "Q900010", "P361", "Q900011")
PASSAGE = {
    "id": "chr:observation:test-collection",
    "observationKind": "passage",
    "status": "observed",
    "sourceSystem": "Test",
    "workId": COLLECTION["id"],
    "editorialNotes": [],
    "passageText": "This biography is part of the collection.",
}


class WorkContainmentTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry(REGISTRY_PATH.with_name("predicates.v12.json"))
        self.reader = FakeReader([LIFE, COLLECTION, EVENT], [P361, PASSAGE])

    def test_only_the_new_same_kind_pair_is_added(self):
        old = load_registry(REGISTRY_PATH.with_name("predicates.v11.json"))
        part = self.registry.get("partOf")
        previous = old.get("partOf")
        self.assertEqual(self.registry.version, "predicates-v12")
        self.assertFalse(previous.allows_kinds("Work", "Work"))
        for subject in self.registry.entity_kinds:
            for obj in self.registry.entity_kinds:
                with self.subTest(subject=subject, obj=obj):
                    self.assertEqual(
                        part.allows_kinds(subject, obj),
                        previous.allows_kinds(subject, obj) or (subject, obj) == ("Work", "Work"),
                    )

    def test_passage_evidenced_work_containment_validates(self):
        draft = ProposalDraft(
            predicate="partOf", subject_id=LIFE["id"], object_id=COLLECTION["id"],
            observation_ids=(PASSAGE["id"],),
            quotations=(Quotation(observation_id=PASSAGE["id"], text=PASSAGE["passageText"]),),
            rationale="Work containment test", proposed_by="test",
        )
        result = validate(draft, self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)

    def test_wikidata_part_of_is_proposed_for_two_works(self):
        result = drafts_from_observation(P361, self.reader, self.registry)
        self.assertEqual([draft.predicate for draft in result.drafts], ["partOf"])
        self.assertEqual((result.drafts[0].subject_id, result.drafts[0].object_id),
                         (LIFE["id"], COLLECTION["id"]))
        checked = validate(result.drafts[0], self.reader, self.registry)
        self.assertEqual(checked.outcome, Outcome.VALID, checked.reasons)


if __name__ == "__main__":
    unittest.main()
