"""Store validated drafts and review stored Proposals through Phase 3 operations.

Every function takes an open Neo4j transaction; the caller commits or rolls
back. Validation always runs again inside the write transaction.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from GraphRevised.operations import run_write

from .registry import PredicateRegistry, proposal_id
from .schema import ProposalDraft, Quotation
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
            RETURN entity {.id, .label, .shortLabel, .kind, .description} AS entity,
                   collect(record.identifier) AS wikidataIds
            """,
            id=entity_id,
        ).single()
        if record is None:
            return None
        return {**record["entity"], "wikidataIds": record["wikidataIds"]}

    def entities(self) -> list[dict[str, Any]]:
        return self._tx.run(
            "MATCH (entity:Entity) RETURN entity {.id, .label, .kind, .description} AS entity ORDER BY entity.id"
        ).value("entity")

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

    def proposal_exists(self, proposal_id: str) -> bool:
        return self._tx.run(
            "MATCH (proposal:Proposal {id: $id}) RETURN count(proposal) > 0 AS exists", id=proposal_id
        ).single()["exists"]

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
    """Validate a draft and store what it validly proposes.

    `valid` stores a proposed Assertion with its evidence and a submitted
    `create` Proposal. `adds_evidence` stores a submitted `addEvidence`
    Proposal whose evidence waits until acceptance. Anything else stores
    nothing. Re-submitting an already stored proposal writes nothing.
    """
    result = validate(draft, Neo4jReader(tx), registry)
    if result.outcome not in (Outcome.VALID, Outcome.ADDS_EVIDENCE):
        return SubmissionResult(result, stored=False)

    definition = registry.get(result.draft.predicate)
    subject, obj = result.subject, result.object
    label = f"{subject['label']} {definition.display} {obj['label']}"
    short_label = f"{subject.get('shortLabel') or subject['label']} -> {obj.get('shortLabel') or obj['label']}"
    quotations = {quotation.observation_id: quotation.text for quotation in result.draft.quotations}
    provenance = {
        "createdBy": result.draft.proposed_by,
        "rationale": result.draft.rationale,
        "draftSchemaVersion": result.draft.schema_version,
        "predicateRegistryVersion": registry.version,
        "promptVersion": result.draft.prompt_version,
        "modelId": result.draft.model_id,
    }

    if result.outcome is Outcome.ADDS_EVIDENCE:
        evidence_draft = result.draft.model_copy(update={"observation_ids": result.new_observation_ids})
        result = replace(result, proposal_id=proposal_id(evidence_draft, result.assertion_id))
        if Neo4jReader(tx).proposal_exists(result.proposal_id):
            return SubmissionResult(result, stored=False)
        for observation_id in result.new_observation_ids:
            run_write(tx, operations, "upsert_evidence_proposal", {
                "id": result.proposal_id,
                "assertionId": result.assertion_id,
                "observationId": observation_id,
                "quotation": quotations.get(observation_id),
                "label": f"Proposal to add evidence: {label}",
                "shortLabel": f"+evidence: {short_label}",
                **provenance,
            })
        return SubmissionResult(result, stored=True)

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
            "quotation": quotations.get(observation_id),
        })
    run_write(tx, operations, "upsert_proposal", {
        "id": result.proposal_id,
        "assertionId": result.assertion_id,
        "label": f"Proposal to accept: {label}",
        "shortLabel": short_label,
        "operation": "create",
        **provenance,
    })
    return SubmissionResult(result, stored=True)


def list_proposals(tx: Any, status: str | None = None) -> list[dict[str, Any]]:
    return tx.run(
        """
        MATCH (proposal:Proposal)-[:PROPOSES]->(assertion:Assertion)
        WHERE $status IS NULL OR proposal.status = $status
        OPTIONAL MATCH (proposal)-[pending:PROPOSES_EVIDENCE]->(pendingObservation:SourceObservation)
        WITH proposal, assertion,
             [item IN collect({observation: coalesce(pendingObservation.label, pendingObservation.id),
                               locator: pendingObservation.locator, passage: pendingObservation.passageText,
                               quotation: pending.quotation})
              WHERE item.observation IS NOT NULL] AS pendingEvidence
        OPTIONAL MATCH (assertion)-[support:SUPPORTED_BY]->(observation:SourceObservation)
        WITH proposal, assertion, pendingEvidence,
             [item IN collect({observation: coalesce(observation.label, observation.id),
                               locator: observation.locator, passage: observation.passageText,
                               quotation: support.quotation})
              WHERE item.observation IS NOT NULL] AS support
        RETURN proposal.id AS id, proposal.status AS status, proposal.operation AS operation,
               assertion.label AS assertion, proposal.createdBy AS createdBy,
               proposal.rationale AS rationale,
               CASE WHEN proposal.operation = "addEvidence" THEN pendingEvidence ELSE support END AS evidence
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
    """Re-validate a Proposal's evidence, move it through validating to accepted,
    and for an addEvidence Proposal attach the evidence."""
    stored = _stored_proposal(tx, proposal_id)
    if stored["status"] not in ("submitted", "validating", "deferred"):
        raise ReviewError(f"{proposal_id} is {stored['status']}; only open proposals can be accepted")
    evidence = [item for item in stored["evidence"] if item["observationId"] is not None]
    if not evidence:
        raise ReviewError(f"{proposal_id} has no evidence")
    draft = ProposalDraft(
        predicate=stored["predicate"],
        subject_id=stored["subjectId"],
        object_id=stored["objectId"],
        observation_ids=tuple(item["observationId"] for item in evidence),
        quotations=tuple(
            Quotation(observation_id=item["observationId"], text=item["quotation"])
            for item in evidence
            if item["quotation"]
        ),
        rationale=stored["rationale"] or "stored proposal without rationale",
        proposed_by=stored["createdBy"] or "unknown",
    )
    result = validate(draft, Neo4jReader(tx), registry, existing_assertion_ok=True)
    if result.outcome is not Outcome.VALID:
        raise ReviewError(f"{proposal_id} failed re-validation ({result.outcome.value}): {list(result.reasons)}")
    decision = {"decidedAt": decided_at, "decidedBy": decided_by, "decisionBasis": decision_basis}
    if stored["status"] != "validating":
        run_write(tx, operations, "decide_proposal", {"proposalId": proposal_id, "proposalStatus": "validating", **decision})
    decided = run_write(tx, operations, "decide_proposal", {"proposalId": proposal_id, "proposalStatus": "accepted", **decision})[0]
    if stored["operation"] == "addEvidence":
        run_write(tx, operations, "apply_accepted_evidence", {"proposalId": proposal_id})
    return decided


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
    """A stored Proposal with the evidence it puts forward: its pending evidence
    for addEvidence, the Assertion's evidence otherwise."""
    record = tx.run(
        """
        MATCH (proposal:Proposal {id: $id})-[:PROPOSES]->(assertion:Assertion)
        MATCH (assertion)-[:ASSERTION_SUBJECT]->(subject)
        MATCH (assertion)-[:ASSERTION_OBJECT]->(object)
        OPTIONAL MATCH (proposal)-[pending:PROPOSES_EVIDENCE]->(pendingObservation:SourceObservation)
        WITH proposal, assertion, subject, object,
             collect({observationId: pendingObservation.id, quotation: pending.quotation}) AS pendingEvidence
        OPTIONAL MATCH (assertion)-[support:SUPPORTED_BY]->(observation:SourceObservation)
        WITH proposal, assertion, subject, object, pendingEvidence,
             collect({observationId: observation.id, quotation: support.quotation}) AS support
        RETURN proposal.status AS status, proposal.operation AS operation,
               proposal.rationale AS rationale, proposal.createdBy AS createdBy,
               assertion.predicate AS predicate, subject.id AS subjectId, object.id AS objectId,
               CASE WHEN proposal.operation = "addEvidence" THEN pendingEvidence ELSE support END AS evidence
        """,
        id=proposal_id,
    ).single()
    if record is None:
        raise ReviewError(f"{proposal_id} does not exist")
    return record.data()
