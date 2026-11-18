"""Registry v18 (45, D-160): animals, plants, metals and materials as Types. Offline."""
import unittest

from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.tests.test_proposals_offline import FakeReader, entity

SILVER = entity("chr:entity:test-silver", "Type")
METAL = entity("chr:entity:test-nonferrous-metal", "Type")
DENARIUS = entity("chr:entity:test-denarius", "Type")
TYRE = entity("chr:entity:test-tyre", "Place")
AAT = entity("chr:entity:test-aat", "Work") | {"form": "reference"}
COINAGE = entity("chr:entity:test-coinage", "Work") | {"form": "coinage"}
TEXT = "silver (metal) (AAT 300011029)\nBroader: nonferrous metal (AAT 300011014)"
RECORD = {"id": "chr:observation:test-aat-silver", "observationKind": "record", "status": "observed",
          "sourceSystem": "Getty Art & Architecture Thesaurus", "workId": AAT["id"], "editorialNotes": [],
          "passageText": TEXT}


def draft(predicate, subject, obj, mode="attributed", by=AAT):
    return ProposalDraft(predicate=predicate, subject_id=subject["id"], object_id=obj["id"],
                         observation_ids=(RECORD["id"],),
                         quotations=(Quotation(observation_id=RECORD["id"], text="Broader: nonferrous metal (AAT 300011014)"),),
                         rationale="v18 test draft", proposed_by="test", mode=mode,
                         attributed_to=by["id"] if mode == "attributed" else None)


class RegistryV18Tests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry(REGISTRY_PATH.with_name("predicates.v18.json"))
        self.reader = FakeReader([SILVER, METAL, DENARIUS, TYRE, AAT, COINAGE], [RECORD])

    def test_the_categories_and_predicates(self):
        self.assertEqual(self.registry.version, "predicates-v18")
        self.assertTrue({"taxon", "material", "product", "denomination"} <= self.registry.type_categories)
        self.assertEqual(self.registry.get("subtypeOf").modes, frozenset({"attributed"}))  # always the authority's voice
        self.assertTrue(self.registry.get("madeOf").allows_kinds("Object", "Type"))
        self.assertTrue(self.registry.get("struckIn").allows_kinds("Work", "Type"))
        self.assertTrue(self.registry.get("producedAt").allows_kinds("Type", "Place"))
        self.assertFalse(self.registry.get("madeFrom").allows_kinds("Type", "Place"))

    def test_the_v17_predicates_are_unchanged(self):
        old = load_registry(REGISTRY_PATH.with_name("predicates.v17.json"))
        for name, definition in old.predicates.items():
            self.assertEqual(self.registry.get(name), definition, name)

    def test_an_authority_hierarchy_link_validates(self):
        self.assertEqual(validate(draft("subtypeOf", SILVER, METAL), self.reader, self.registry).outcome, Outcome.VALID)

    def test_a_hierarchy_link_in_our_own_voice_is_refused(self):
        result = validate(draft("subtypeOf", SILVER, METAL, mode="asserted"), self.reader, self.registry)
        self.assertNotEqual(result.outcome, Outcome.VALID)

    def test_a_material_is_not_a_place(self):
        self.assertNotEqual(validate(draft("madeOf", DENARIUS, TYRE), self.reader, self.registry).outcome, Outcome.VALID)


if __name__ == "__main__":
    unittest.main()
