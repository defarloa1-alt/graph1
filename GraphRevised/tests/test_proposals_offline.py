"""Validator, registry, proposer, and statement-observation checks without Neo4j."""

import unittest
from pathlib import Path

from pydantic import ValidationError

from GraphRevised.adapters.wikidata_statements import StatementNotFound, statement_observation
from GraphRevised.proposals.registry import assertion_id, load_registry
from GraphRevised.proposals.schema import ProposalDraft
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation

PAYLOAD = Path(__file__).resolve().parents[1] / "phase-2-source" / "wikidata-Q160387-r2555342002.json"
AGRIPPA_STATEMENT = "Q160387$32bdfa2f-497d-fb83-169f-f9567f3152ec"


def entity(entity_id, kind, *qids):
    return {"id": entity_id, "label": entity_id.rsplit(":", 1)[-1], "shortLabel": None, "kind": kind, "wikidataIds": list(qids)}


def observation(observation_id, source, pid, value, qualifiers=()):
    return {
        "id": observation_id,
        "status": "observed",
        "sourceSystem": "Wikidata",
        "externalStatementId": f"{source}$x",
        "sourceEntityId": source,
        "predicateExternalId": pid,
        "objectExternalId": value,
        "qualifierPropertyIds": list(qualifiers),
        "sourceRevision": 1,
    }


class FakeReader:
    def __init__(self, entities=(), observations=(), assertions=()):
        self.entities = {item["id"]: item for item in entities}
        self.observations = {item["id"]: item for item in observations}
        self.assertions = {item["id"]: item for item in assertions}

    def entity(self, entity_id):
        return self.entities.get(entity_id)

    def observation(self, observation_id):
        return self.observations.get(observation_id)

    def assertion(self, assertion_id):
        return self.assertions.get(assertion_id)

    def entity_ids_for_wikidata(self, qid):
        return sorted(e["id"] for e in self.entities.values() if qid in e["wikidataIds"])


ACTIUM = entity("chr:entity:battle-of-actium", "Event", "Q160387")
AGRIPPA = entity("chr:entity:marcus-vipsanius-agrippa", "Person", "Q48174")
JULIA = entity("chr:entity:julia", "Person", "Q2259")
P710 = observation("chr:observation:p710", "Q160387", "P710", "Q48174")
P26 = observation("chr:observation:p26", "Q48174", "P26", "Q2259", qualifiers=("P580", "P582"))
P26_UNQUALIFIED = observation("chr:observation:p26-plain", "Q48174", "P26", "Q2259")


def draft(predicate="participatedIn", subject=AGRIPPA, obj=ACTIUM, observations=(P710,), **extra):
    return ProposalDraft(
        predicate=predicate,
        subject_id=subject["id"],
        object_id=obj["id"],
        observation_ids=tuple(o["id"] for o in observations),
        rationale="offline validator test",
        proposed_by="test",
        **extra,
    )


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.reader = FakeReader([ACTIUM, AGRIPPA, JULIA], [P710, P26, P26_UNQUALIFIED])

    def check(self, proposal, reader=None):
        return validate(proposal, reader or self.reader, self.registry)

    def test_valid_draft_gets_existing_style_assertion_id(self):
        result = self.check(draft())
        self.assertEqual(result.outcome, Outcome.VALID)
        self.assertEqual(
            result.assertion_id,
            "chr:assertion:marcus-vipsanius-agrippa:participated-in:battle-of-actium",
        )

    def test_proposal_id_is_deterministic(self):
        self.assertEqual(self.check(draft()).proposal_id, self.check(draft()).proposal_id)

    def test_unregistered_predicate_is_invalid(self):
        self.assertEqual(self.check(draft(predicate="caused")).outcome, Outcome.INVALID)

    def test_wrong_endpoint_kinds_are_invalid(self):
        result = self.check(draft(subject=ACTIUM, obj=AGRIPPA))
        self.assertEqual(result.outcome, Outcome.INVALID)
        self.assertTrue(any("subject must be" in reason for reason in result.reasons))

    def test_missing_entity_is_invalid(self):
        ghost = entity("chr:entity:ghost", "Person")
        self.assertEqual(self.check(draft(subject=ghost)).outcome, Outcome.INVALID)

    def test_evidence_for_a_different_relationship_is_invalid(self):
        # Julia did not participate at Actium according to this observation.
        result = self.check(draft(subject=JULIA))
        self.assertEqual(result.outcome, Outcome.INVALID)
        self.assertTrue(any("does not state participatedIn" in reason for reason in result.reasons))

    def test_evidence_with_wrong_property_is_invalid(self):
        self.assertEqual(self.check(draft(observations=(P26_UNQUALIFIED,))).outcome, Outcome.INVALID)

    def test_superseded_observation_is_invalid(self):
        reader = FakeReader([ACTIUM, AGRIPPA], [P710 | {"status": "superseded"}])
        self.assertEqual(self.check(draft(), reader).outcome, Outcome.INVALID)

    def test_temporally_qualified_spouse_is_deferred(self):
        result = self.check(draft("spouseOf", AGRIPPA, JULIA, (P26,)))
        self.assertEqual(result.outcome, Outcome.DEFERRED)

    def test_unqualified_spouse_is_valid_and_canonicalized(self):
        result = self.check(draft("spouseOf", JULIA, AGRIPPA, (P26_UNQUALIFIED,)))
        self.assertEqual(result.outcome, Outcome.VALID)
        self.assertEqual(result.draft.subject_id, "chr:entity:julia")
        self.assertEqual(
            result.assertion_id,
            self.check(draft("spouseOf", AGRIPPA, JULIA, (P26_UNQUALIFIED,))).assertion_id,
        )

    def test_unknown_qualifiers_defer_when_predicate_needs_them(self):
        reader = FakeReader([AGRIPPA, JULIA], [P26_UNQUALIFIED | {"qualifierPropertyIds": None}])
        self.assertEqual(self.check(draft("spouseOf", AGRIPPA, JULIA, (P26_UNQUALIFIED,)), reader).outcome, Outcome.DEFERRED)

    def test_required_qualification_is_deferred(self):
        position = entity("chr:entity:consul", "Other", "Q40779")
        p39 = observation("chr:observation:p39", "Q48174", "P39", "Q40779")
        reader = FakeReader([AGRIPPA, position], [p39])
        self.assertEqual(self.check(draft("heldPosition", AGRIPPA, position, (p39,)), reader).outcome, Outcome.DEFERRED)

    def test_ambiguity_is_deferred(self):
        self.assertEqual(self.check(draft(ambiguities=("which Agrippa?",))).outcome, Outcome.DEFERRED)

    def test_existing_assertion_is_duplicate(self):
        existing = {
            "id": "chr:assertion:marcus-vipsanius-agrippa:participated-in:battle-of-actium",
            "status": "accepted",
            "predicate": "participatedIn",
            "observationIds": [P710["id"]],
        }
        reader = FakeReader([ACTIUM, AGRIPPA], [P710], [existing])
        result = self.check(draft(), reader)
        self.assertEqual(result.outcome, Outcome.DUPLICATE)
        self.assertTrue(result.already_supported)

    def test_draft_rejects_extra_fields_and_bad_ids(self):
        with self.assertRaises(ValidationError):
            ProposalDraft.model_validate({**draft().model_dump(), "cypher": "MATCH (n) DETACH DELETE n"})
        with self.assertRaises(ValidationError):
            draft(subject=entity("Q48174", "Person"))


class RegistryAndProposerTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()

    def test_registry_kinds_are_known_entity_kinds(self):
        kinds = {"Person", "Event", "Place", "Group", "Object", "Work", "Period", "Other"}
        for definition in self.registry.predicates.values():
            self.assertLessEqual(definition.subject_kinds | definition.object_kinds, kinds, definition.id)

    def test_assertion_id_kebabs_predicate(self):
        self.assertEqual(assertion_id("heldPosition", "chr:entity:a", "chr:entity:b"), "chr:assertion:a:held-position:b")

    def test_proposer_maps_inverse_participant_statement(self):
        result = drafts_from_observation(P710, FakeReader([ACTIUM, AGRIPPA]), self.registry)
        self.assertEqual(len(result.drafts), 1)
        self.assertEqual((result.drafts[0].subject_id, result.drafts[0].object_id), (AGRIPPA["id"], ACTIUM["id"]))

    def test_proposer_reports_unresolved_entities_instead_of_creating_them(self):
        result = drafts_from_observation(P710, FakeReader([ACTIUM]), self.registry)
        self.assertEqual(result.drafts, ())
        self.assertEqual(result.unresolved, ("Q48174 has no local Entity",))

    def test_statement_observation_reproduces_phase_2_observation(self):
        params = statement_observation(PAYLOAD, AGRIPPA_STATEMENT, label="x", short_label="x")
        self.assertEqual(params["id"], "chr:observation:wikidata:Q160387:P710:32bdfa2f:r2555342002")
        self.assertEqual(params["contentHash"], "8523c2b5e440b6e35a12a6bca3e602c3697b0ddfb03644a09164cf0f978235db")
        self.assertEqual(params["rawPayloadUri"], "GraphRevised/phase-2-source/wikidata-Q160387-r2555342002.json")
        self.assertEqual(params["qualifierPropertyIds"], [])

    def test_unknown_statement_is_reported(self):
        with self.assertRaises(StatementNotFound):
            statement_observation(PAYLOAD, "Q160387$00000000-0000", label="x", short_label="x")


if __name__ == "__main__":
    unittest.main()
