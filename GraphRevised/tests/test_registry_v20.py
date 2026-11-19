"""Registry v20 (46, D-166): the gens as a Group category, ofGens, and an object's category. Offline."""
import unittest

from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.validator import Outcome, validate

PERSON, GENS, LEGION = "chr:entity:test-person", "chr:entity:test-gens", "chr:entity:test-legion"
PASSAGE = "chr:observation:test:passage"


class FakeReader:
    """Just enough of Neo4jReader for the endpoint checks."""

    entities = {
        PERSON: {"id": PERSON, "label": "Lucius Testus", "kind": "Person", "category": None, "wikidataIds": []},
        GENS: {"id": GENS, "label": "gens Testia", "kind": "Group", "category": "gens", "wikidataIds": []},
        LEGION: {"id": LEGION, "label": "Test legion", "kind": "Group", "category": None, "wikidataIds": []},
    }

    def entity(self, entity_id):
        return self.entities.get(entity_id)

    def __getattr__(self, name):  # anything else: nothing stored
        return lambda *args, **kwargs: None


class RegistryV20Tests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.old = load_registry(REGISTRY_PATH.with_name("predicates.v19.json"))

    def test_the_gens(self):
        self.assertEqual(self.registry.version, "predicates-v20")
        self.assertEqual(self.registry.group_categories, frozenset({"gens"}))
        of_gens = self.registry.get("ofGens")
        self.assertTrue(of_gens.allows_kinds("Person", "Group"))
        self.assertEqual(of_gens.object_categories, frozenset({"gens"}))
        self.assertEqual(of_gens.qualifiers.time, "none")  # for life, unlike memberOf
        self.assertEqual([(m.pid, m.direction) for m in of_gens.wikidata], [("P5025", "forward")])
        self.assertEqual(self.registry.get("memberOf").qualifiers.time, "required")

    def test_only_of_gens_is_new(self):
        self.assertEqual(set(self.registry.predicates) - set(self.old.predicates), {"ofGens"})
        for name, definition in self.old.predicates.items():
            self.assertEqual(self.registry.get(name), definition, name)

    def endpoint_reasons(self, object_id):
        draft = ProposalDraft(predicate="ofGens", subject_id=PERSON, object_id=object_id,
                              observation_ids=(PASSAGE,),
                              quotations=(Quotation(observation_id=PASSAGE, text="a test passage of the gens"),),
                              rationale="a test of the gens check", proposed_by="test")
        return [r for r in validate(draft, FakeReader(), self.registry).reasons if "category" in r]

    def test_of_gens_needs_a_group_of_category_gens(self):
        self.assertEqual(self.endpoint_reasons(GENS), [])
        self.assertEqual(self.endpoint_reasons(LEGION),
                         ["ofGens object must be of category ['gens'], not none"])


if __name__ == "__main__":
    unittest.main()
