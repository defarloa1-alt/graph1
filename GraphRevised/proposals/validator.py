"""Deterministic validation of ProposalDrafts. No model calls, no writes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from .registry import (
    PredicateDefinition,
    PredicateRegistry,
    assertion_id,
    canonical_endpoints,
    proposal_id,
)
from .schema import ProposalDraft


class Outcome(str, Enum):
    VALID = "valid"  # may be stored as a submitted Proposal
    DUPLICATE = "duplicate"  # the Assertion already exists; nothing to store
    DEFERRED = "deferred"  # needs a capability not built yet (qualification, clarification)
    INVALID = "invalid"  # refused


@dataclass(frozen=True)
class ValidationResult:
    outcome: Outcome
    reasons: tuple[str, ...]
    draft: ProposalDraft
    assertion_id: str | None = None
    proposal_id: str | None = None
    subject: dict[str, Any] | None = None
    object: dict[str, Any] | None = None
    already_supported: bool | None = None


class GraphReader(Protocol):
    def entity(self, entity_id: str) -> dict[str, Any] | None:
        """{id, label, shortLabel, kind, wikidataIds} or None."""

    def observation(self, observation_id: str) -> dict[str, Any] | None:
        """SourceObservation properties or None."""

    def assertion(self, assertion_id: str) -> dict[str, Any] | None:
        """{id, status, predicate, observationIds} or None."""


def validate(
    draft: ProposalDraft,
    reader: GraphReader,
    registry: PredicateRegistry,
    *,
    existing_assertion_ok: bool = False,
) -> ValidationResult:
    """Validate a draft.

    `existing_assertion_ok` is used when re-validating a stored Proposal at
    review time, where its own `proposed` Assertion already exists.
    """
    definition = registry.get(draft.predicate)
    if definition is None:
        return ValidationResult(Outcome.INVALID, (f"unregistered predicate {draft.predicate!r}",), draft)

    subject_id, object_id = canonical_endpoints(definition, draft.subject_id, draft.object_id)
    if (subject_id, object_id) != (draft.subject_id, draft.object_id):
        draft = draft.model_copy(update={"subject_id": subject_id, "object_id": object_id})

    reasons: list[str] = []
    subject = reader.entity(subject_id)
    obj = reader.entity(object_id)
    if subject is None:
        reasons.append(f"subject {subject_id} is not an existing Entity")
    elif subject["kind"] not in definition.subject_kinds:
        reasons.append(f"{definition.id} subject must be {sorted(definition.subject_kinds)}, not {subject['kind']}")
    if obj is None:
        reasons.append(f"object {object_id} is not an existing Entity")
    elif obj["kind"] not in definition.object_kinds:
        reasons.append(f"{definition.id} object must be {sorted(definition.object_kinds)}, not {obj['kind']}")
    if subject_id == object_id:
        reasons.append("subject and object must differ")

    observations = []
    for observation_id in draft.observation_ids:
        observation = reader.observation(observation_id)
        if observation is None:
            reasons.append(f"observation {observation_id} does not exist")
        elif observation.get("status") != "observed":
            reasons.append(f"observation {observation_id} is {observation.get('status')}, not observed")
        elif observation.get("sourceSystem") != "Wikidata" or not observation.get("externalStatementId"):
            reasons.append(f"observation {observation_id} is not a Wikidata statement observation")
        else:
            observations.append(observation)

    if subject is not None and obj is not None:
        for observation in observations:
            if not _evidences(definition, observation, subject, obj):
                reasons.append(
                    f"observation {observation['id']} does not state {definition.id} "
                    f"between {subject_id} and {object_id}"
                )

    if reasons:
        return ValidationResult(Outcome.INVALID, tuple(reasons), draft)

    deferrals: list[str] = []
    if definition.temporal_qualification == "required":
        deferrals.append(f"{definition.id} requires temporal qualification (Phase 7)")
    elif definition.temporal_qualification == "whenPresent":
        for observation in observations:
            qualifiers = observation.get("qualifierPropertyIds")
            if qualifiers is None:
                deferrals.append(f"qualifiers of {observation['id']} were not recorded")
            elif registry.temporal_qualifier_pids & set(qualifiers):
                deferrals.append(f"{observation['id']} carries temporal qualifiers (Phase 7)")
    deferrals.extend(f"ambiguity: {item}" for item in draft.ambiguities)

    canonical_assertion = assertion_id(definition.id, subject_id, object_id)
    result = dict(
        draft=draft,
        assertion_id=canonical_assertion,
        proposal_id=proposal_id(draft, canonical_assertion),
        subject=subject,
        object=obj,
    )
    if deferrals:
        return ValidationResult(Outcome.DEFERRED, tuple(deferrals), **result)

    existing = reader.assertion(canonical_assertion)
    if existing is not None and not existing_assertion_ok:
        supported = set(draft.observation_ids) <= set(existing["observationIds"])
        return ValidationResult(
            Outcome.DUPLICATE,
            (f"{canonical_assertion} already exists with status {existing['status']}",),
            already_supported=supported,
            **result,
        )
    return ValidationResult(Outcome.VALID, (), **result)


def _evidences(
    definition: PredicateDefinition,
    observation: dict[str, Any],
    subject: dict[str, Any],
    obj: dict[str, Any],
) -> bool:
    """True when a Wikidata statement observation states this relationship."""
    source = observation.get("sourceEntityId")
    value = observation.get("objectExternalId")
    for mapping in definition.wikidata:
        if mapping.pid != observation.get("predicateExternalId"):
            continue
        holder, target = (subject, obj) if mapping.direction == "forward" else (obj, subject)
        orientations = [(holder, target), (target, holder)] if definition.symmetric else [(holder, target)]
        for statement_entity, statement_value in orientations:
            if source in statement_entity["wikidataIds"] and value in statement_value["wikidataIds"]:
                return True
    return False
