"""Store validated drafts and review stored Proposals through Phase 3 operations.

Every function takes an open Neo4j transaction; the caller commits or rolls
back. Validation always runs again inside the write transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from GraphRevised.operations import run_write

from .registry import PredicateRegistry
from .schema import ProposalDraft
from .validator import Outcome, ValidationResult, validate


class ReviewError(RuntimeError):
    """A review action was refused."""


class Neo4jReader:
    """Read-only GraphReader over an open transaction."""

    def __init__(self, tx: Any) -> None:
        self._tx = tx

    def entity(self, entity_id: str) -> dict[str, Any] | None:
        record = self._tx.run(
            """
            MATCH (entity:Entity {id: $id})
            OPTIONAL MATCH (entity)-[link:HAS_AUTHORITY_RECORD]->(record:AuthorityRecord {system: "Wikidata"})
            WHERE link.role = "entity_identity" AND link.status = "accepted"
            RETURN entity {.id, .label, .shortLabel, .kind} AS entity,
                   collect(record.identifier) AS wikidataIds
            """,
            id=entity_id,
        ).single()
        if record is None:
            return None
        return {**record["entity"], "wikidataIds": record["wikidataIds"]}

    def entity_ids_for_wikidata(self, qid: str) -> list[str]:
        return self._tx.run(
            """
            MATCH (entity:Entity)-[link:HAS_AUTHORITY_RECORD]->
                  (:AuthorityRecord {system: "Wikidata", identifier: $qid})
            WHERE link.role = "entity_identity" AND link.status = "accepted"
            RETURN entity.id AS id ORDER BY id
            """,
            qid=qid,
        ).value("id")

    def observation(self, observation_id: str) -> dict[str, Any] | None:
        record = self._tx.run(
            "MATCH (observation:SourceObservation {id: $id}) RETURN properties(observation) AS p",
            id=observation_id,
        ).single()
        return None if record is None else record["p"]

    def assertion(self, assertion_id: str) -> dict[str, Any] | None:
        record = self._tx.run(
            """
            MATCH (assertion:Assertion {id: $id})
            OPTIONAL MATCH (assertion)-[:SUPPORTED_BY]->(observation:SourceObservation)
            RETURN assertion {.id, .status, .predicate} AS assertion,
                   collect(observation.id) AS observationIds
            """,
            id=assertion_id,
        ).single()
        if record is None:
            return None
        return {**record["assertion"], "observationIds": record["observationIds"]}


@dataclass(frozen=True)
class SubmissionResult:
    validation: ValidationResult
    stored: bool


def submit(
    tx: Any,
    draft: ProposalDraft,
    registry: PredicateRegistry,
    operations: dict[str, str],
) -> SubmissionResult:
    """Validate a draft and, when valid, store a proposed Assertion and a submitted Proposal."""
    result = validate(draft, Neo4jReader(tx), registry)
    if result.outcome is not Outcome.VALID:
        return SubmissionResult(result, stored=False)

    definition = registry.get(result.draft.predicate)
    subject, obj = result.subject, result.object
    label = f"{subject['label']} {definition.display} {obj['label']}"
    short_label = f"{subject.get('shortLabel') or subject['label']} -> {obj.get('shortLabel') or obj['label']}"

    run_write(tx, operations, "upsert_assertion", {
        "id": result.assertion_id,
        "label": label,
        "shortLabel": short_label,
        "predicate": definition.id,
        "assertedBy": result.draft.proposed_by,
        "subjectId": result.draft.subject_id,
        "objectId": result.draft.object_id,
    })
    for observation_id in result.draft.observation_ids:
        run_write(tx, operations, "link_support", {
            "assertionId": result.assertion_id,
            "observationId": observation_id,
        })
    run_write(tx, operations, "upsert_proposal", {
        "id": result.proposal_id,
        "assertionId": result.assertion_id,
        "label": f"Proposal to accept: {label}",
        "shortLabel": short_label,
        "operation": "create",
        "createdBy": result.draft.proposed_by,
        "rationale": result.draft.rationale,
        "draftSchemaVersion": result.draft.schema_version,
        "predicateRegistryVersion": registry.version,
        "promptVersion": result.draft.prompt_version,
        "modelId": result.draft.model_id,
    })
    return SubmissionResult(result, stored=True)


def list_proposals(tx: Any, status: str | None = None) -> list[dict[str, Any]]:
    return tx.run(
        """
        MATCH (proposal:Proposal)-[:PROPOSES]->(assertion:Assertion)
        WHERE $status IS NULL OR proposal.status = $status
        RETURN proposal.id AS id, proposal.status AS status, assertion.label AS assertion,
               proposal.createdBy AS createdBy, proposal.rationale AS rationale
        ORDER BY id
        """,
        status=status,
    ).data()


def accept(
    tx: Any,
    proposal_id: str,
    *,
    decided_by: str,
    decision_basis: str,
    decided_at: str,
    registry: PredicateRegistry,
    operations: dict[str, str],
) -> dict[str, Any]:
    """Re-validate a Proposal's evidence, then move it through validating to accepted."""
    stored = _stored_proposal(tx, proposal_id)
    if stored["status"] not in ("submitted", "validating", "deferred"):
        raise ReviewError(f"{proposal_id} is {stored['status']}; only open proposals can be accepted")
    draft = ProposalDraft(
        predicate=stored["predicate"],
        subject_id=stored["subjectId"],
        object_id=stored["objectId"],
        observation_ids=tuple(stored["observationIds"]),
        rationale=stored["rationale"] or "stored proposal without rationale",
        proposed_by=stored["createdBy"] or "unknown",
    )
    result = validate(draft, Neo4jReader(tx), registry, existing_assertion_ok=True)
    if result.outcome is not Outcome.VALID:
        raise ReviewError(f"{proposal_id} failed re-validation ({result.outcome.value}): {list(result.reasons)}")
    decision = {"decidedAt": decided_at, "decidedBy": decided_by, "decisionBasis": decision_basis}
    if stored["status"] != "validating":
        run_write(tx, operations, "decide_proposal", {"proposalId": proposal_id, "proposalStatus": "validating", **decision})
    return run_write(tx, operations, "decide_proposal", {"proposalId": proposal_id, "proposalStatus": "accepted", **decision})[0]


def reject(
    tx: Any,
    proposal_id: str,
    *,
    decided_by: str,
    decision_basis: str,
    decided_at: str,
    operations: dict[str, str],
) -> dict[str, Any]:
    stored = _stored_proposal(tx, proposal_id)
    if stored["status"] not in ("submitted", "validating", "deferred", "rejected"):
        raise ReviewError(f"{proposal_id} is {stored['status']}; it cannot be rejected")
    return run_write(tx, operations, "decide_proposal", {
        "proposalId": proposal_id,
        "proposalStatus": "rejected",
        "decidedAt": decided_at,
        "decidedBy": decided_by,
        "decisionBasis": decision_basis,
    })[0]


def _stored_proposal(tx: Any, proposal_id: str) -> dict[str, Any]:
    record = tx.run(
        """
        MATCH (proposal:Proposal {id: $id})-[:PROPOSES]->(assertion:Assertion)
        MATCH (assertion)-[:ASSERTION_SUBJECT]->(subject)
        MATCH (assertion)-[:ASSERTION_OBJECT]->(object)
        OPTIONAL MATCH (assertion)-[:SUPPORTED_BY]->(observation:SourceObservation)
        RETURN proposal.status AS status, proposal.rationale AS rationale,
               proposal.createdBy AS createdBy, assertion.predicate AS predicate,
               subject.id AS subjectId, object.id AS objectId,
               collect(observation.id) AS observationIds
        """,
        id=proposal_id,
    ).single()
    if record is None:
        raise ReviewError(f"{proposal_id} does not exist")
    return record.data()
