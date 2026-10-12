"""Deterministic validation of ProposalDrafts. No model calls, no writes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from .registry import (
    PredicateDefinition,
    PredicateRegistry,
    assertion_id,
    canonical_endpoints,
    proposal_id,
    qualifier_signature,
)
from .schema import ProposalDraft
from .temporal import TimeBounds, TimeValueError, parse_edtf


class Outcome(str, Enum):
    VALID = "valid"  # may be stored as a new proposed Assertion and submitted Proposal
    ADDS_EVIDENCE = "adds_evidence"  # the Assertion exists; the draft brings new evidence for it
    DUPLICATE = "duplicate"  # nothing new to store
    DEFERRED = "deferred"  # needs a capability not built yet, or a required qualifier
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
    new_observation_ids: tuple[str, ...] = ()
    qualifier_entities: dict[str, dict[str, Any]] | None = None  # context, role, attributedTo
    time_bounds: TimeBounds | None = None


class GraphReader(Protocol):
    def entity(self, entity_id: str) -> dict[str, Any] | None:
        """{id, label, shortLabel, kind, wikidataIds} or None."""

    def observation(self, observation_id: str) -> dict[str, Any] | None:
        """SourceObservation properties, plus workId for a passage in a Work, or None."""

    def assertion(self, assertion_id: str) -> dict[str, Any] | None:
        """{id, status, predicate, observationIds} or None."""


QUALIFIER_KINDS = {"context_id": ("context", "Event"), "role_id": ("role", "Other"), "attributed_to": ("attributedTo", "Work")}


def validate(
    draft: ProposalDraft,
    reader: GraphReader,
    registry: PredicateRegistry,
    *,
    existing_assertion_ok: bool = False,
) -> ValidationResult:
    """Validate a draft.

    `existing_assertion_ok` is used when re-validating a stored Proposal at
    review time, where its own Assertion already exists.
    """
    definition = registry.get(draft.predicate)
    if definition is None:
        return ValidationResult(Outcome.INVALID, (f"unregistered predicate {draft.predicate!r}",), draft)

    subject_id, object_id = canonical_endpoints(definition, draft.subject_id, draft.object_id)
    if (subject_id, object_id) != (draft.subject_id, draft.object_id):
        draft = draft.model_copy(update={"subject_id": subject_id, "object_id": object_id})

    reasons: list[str] = []
    subject = reader.entity(subject_id)
    obj = reader.entity(object_id) if object_id is not None else None
    if subject is None:
        reasons.append(f"subject {subject_id} is not an existing Entity")
    elif subject["kind"] not in definition.subject_kinds:
        reasons.append(f"{definition.id} subject must be {sorted(definition.subject_kinds)}, not {subject['kind']}")
    if definition.unary:
        if object_id is not None:
            reasons.append(f"{definition.id} is unary and takes no object")
    elif object_id is None:
        reasons.append(f"{definition.id} needs an object")
    elif obj is None:
        reasons.append(f"object {object_id} is not an existing Entity")
    elif obj["kind"] not in definition.object_kinds:
        reasons.append(f"{definition.id} object must be {sorted(definition.object_kinds)}, not {obj['kind']}")
    if subject_id == object_id:
        reasons.append("subject and object must differ")

    reasons.extend(_check_qualifier_rules(draft, definition))
    qualifier_entities: dict[str, dict[str, Any]] = {}
    for field, (name, kind) in QUALIFIER_KINDS.items():
        target = getattr(draft, field)
        if target is None:
            continue
        found = reader.entity(target)
        if found is None:
            reasons.append(f"{name} {target} is not an existing Entity")
        elif found["kind"] != kind:
            reasons.append(f"{name} must be an Entity of kind {kind}, not {found['kind']}")
        else:
            qualifier_entities[name] = found

    time_bounds = None
    if draft.time is not None and draft.time.edtf is not None:
        try:
            time_bounds = parse_edtf(draft.time.edtf, draft.time.calendar)
            if time_bounds.earliest_year is not None and time_bounds.latest_year is not None:
                time_bounds.years()
        except TimeValueError as error:
            reasons.append(f"time: {error}")

    quotations = {quotation.observation_id: quotation.text for quotation in draft.quotations}
    for quoted_id in quotations.keys() - set(draft.observation_ids):
        reasons.append(f"quotation cites {quoted_id}, which is not among the draft's observations")

    statements, passages = [], []
    for observation_id in draft.observation_ids:
        observation = reader.observation(observation_id)
        if observation is None:
            reasons.append(f"observation {observation_id} does not exist")
        elif observation.get("status") != "observed":
            reasons.append(f"observation {observation_id} is {observation.get('status')}, not observed")
        elif observation.get("observationKind") == "passage":
            reasons.extend(_check_passage(observation, quotations.get(observation_id)))
            passages.append(observation)
        elif observation.get("sourceSystem") == "Wikidata" and observation.get("externalStatementId"):
            statements.append(observation)
        else:
            reasons.append(f"observation {observation_id} is neither a Wikidata statement nor a passage")

    reasons.extend(_check_qualifier_evidence(draft, passages, statements))

    if subject is not None and (obj is not None or definition.unary):
        for observation in statements:
            if not _evidences(definition, observation, subject, obj):
                reasons.append(
                    f"observation {observation['id']} does not state {definition.id} "
                    f"between {subject_id} and {object_id}"
                )

    if reasons:
        return ValidationResult(Outcome.INVALID, tuple(reasons), draft)

    deferrals = _deferrals(draft, definition, registry, statements)
    canonical_assertion = assertion_id(definition.id, subject_id, object_id, qualifier_signature(draft))
    result = dict(
        draft=draft,
        assertion_id=canonical_assertion,
        proposal_id=proposal_id(draft, canonical_assertion),
        subject=subject,
        object=obj,
        qualifier_entities=qualifier_entities,
        time_bounds=time_bounds,
    )
    if deferrals:
        return ValidationResult(Outcome.DEFERRED, tuple(deferrals), **result)

    existing = reader.assertion(canonical_assertion)
    if existing is None or existing_assertion_ok:
        return ValidationResult(Outcome.VALID, (), **result)

    pending = set(existing.get("pendingObservationIds") or [])
    new_observations = tuple(
        observation_id for observation_id in draft.observation_ids
        if observation_id not in existing["observationIds"] and observation_id not in pending
    )
    if not new_observations and pending & set(draft.observation_ids):
        return ValidationResult(
            Outcome.DUPLICATE,
            (f"this evidence for {canonical_assertion} is already proposed and awaiting review",),
            already_supported=False,
            **result,
        )
    if not new_observations:
        return ValidationResult(
            Outcome.DUPLICATE,
            (f"{canonical_assertion} already exists ({existing['status']}) with this evidence",),
            already_supported=True,
            **result,
        )
    if existing["status"] not in ("proposed", "accepted"):
        return ValidationResult(
            Outcome.DUPLICATE,
            (f"{canonical_assertion} exists but is {existing['status']}; evidence cannot be added",),
            already_supported=False,
            **result,
        )
    return ValidationResult(
        Outcome.ADDS_EVIDENCE,
        (f"{canonical_assertion} exists ({existing['status']}); {len(new_observations)} new observation(s)",),
        already_supported=False,
        new_observation_ids=new_observations,
        **result,
    )


def _check_qualifier_rules(draft: ProposalDraft, definition: PredicateDefinition) -> list[str]:
    """Each qualifier the draft carries must be allowed by the predicate."""
    reasons = []
    allowed = definition.qualifiers
    if draft.mode not in definition.modes:
        reasons.append(f"{definition.id} does not allow mode {draft.mode}")
    if draft.context_id and allowed.context == "none":
        reasons.append(f"{definition.id} takes no context")
    if draft.role_id and allowed.role == "none":
        reasons.append(f"{definition.id} takes no role")
    if draft.time is not None and allowed.time == "none":
        reasons.append(f"{definition.id} takes no time qualifier")
    if draft.context_basis == "inquiry" and not draft.inquiry_id:
        reasons.append("a context resting on the inquiry needs the draft's inquiry_id")
    if draft.time is not None and draft.time.relative_offset and not draft.context_id:
        reasons.append("a relative time needs a context event to be relative to")
    return reasons


def _check_qualifier_evidence(
    draft: ProposalDraft, passages: list[dict[str, Any]], statements: list[dict[str, Any]]
) -> list[str]:
    """Attributed claims cite their Work only; qualifiers drawn from passages
    are shown by verbatim spans."""
    reasons = []
    if draft.mode == "attributed":
        if statements:
            reasons.append("an attributed claim cites passages of its Work, not Wikidata statements")
        for passage in passages:
            if passage.get("workId") != draft.attributed_to:
                reasons.append(f"{passage['id']} is not a passage of {draft.attributed_to}")

    passage_texts = {passage["id"]: passage.get("passageText") or "" for passage in passages}
    shown: dict[str, list[str]] = {"role": [], "time": [], "context": []}
    for quotation in draft.qualifier_quotations:
        if quotation.observation_id not in passage_texts:
            reasons.append(f"{quotation.supports} quotation cites {quotation.observation_id}, which is not a cited passage")
        elif normalize(quotation.text) not in normalize(passage_texts[quotation.observation_id]):
            reasons.append(f"{quotation.supports} quotation does not appear verbatim in {quotation.observation_id}")
        else:
            shown[quotation.supports].append(normalize(quotation.text))

    if passages and not statements:
        if draft.role_id and not shown["role"]:
            reasons.append("a role drawn from a passage needs a role quotation")
        if draft.time is not None:
            if not shown["time"]:
                reasons.append("a time drawn from a passage needs a time quotation")
            elif not any(normalize(draft.time.source_expression) in text for text in shown["time"]):
                reasons.append("the time's source expression must appear in its time quotation")
        if draft.context_basis == "quotation" and not shown["context"]:
            reasons.append("a context resting on a quotation needs a context quotation")
    return reasons


def _deferrals(
    draft: ProposalDraft,
    definition: PredicateDefinition,
    registry: PredicateRegistry,
    statements: list[dict[str, Any]],
) -> list[str]:
    """Qualifiers a predicate requires but the draft lacks, and Wikidata
    qualifiers that would otherwise be flattened."""
    deferrals = []
    required = definition.qualifiers
    if required.context == "required" and not draft.context_id:
        deferrals.append(f"{definition.id} requires a context event")
    if required.role == "required" and not draft.role_id:
        deferrals.append(f"{definition.id} requires a role")
    time_required = required.time == "required" or (required.time == "withRole" and draft.role_id is not None)
    if time_required and draft.time is None:
        deferrals.append(f"{definition.id} {'with a role ' if required.time == 'withRole' else ''}requires a time qualifier")

    for observation in statements:
        qualifiers = observation.get("qualifierPropertyIds")
        if draft.time is not None or draft.role_id is not None:
            deferrals.append(f"qualifier values of {observation['id']} are not compared with the claim's yet")
        elif qualifiers is None and required.time != "none":
            # Observations stored before qualifiers were recorded; role
            # qualifiers are checked only where recorded.
            deferrals.append(f"qualifiers of {observation['id']} were not recorded")
        elif qualifiers is not None and (
            (required.time != "none" and registry.temporal_qualifier_pids & set(qualifiers))
            or (required.role != "none" and registry.role_qualifier_pids & set(qualifiers))
        ):
            deferrals.append(f"{observation['id']} carries qualifiers the claim would flatten")
    return deferrals


TYPOGRAPHIC_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def normalize(text: str) -> str:
    """Text used for quote matching: whitespace collapsed and typographic quotes
    made plain, so a faithful quotation is not refused over apostrophe style.
    Nothing else is relaxed."""
    return re.sub(r"\s+", " ", text.translate(TYPOGRAPHIC_QUOTES)).strip()


def _check_passage(observation: dict[str, Any], quotation: str | None) -> list[str]:
    if quotation is None:
        return [f"passage observation {observation['id']} needs a verbatim quotation"]
    quote = normalize(quotation)
    if quote in normalize(observation.get("passageText") or ""):
        return []
    if any(quote in normalize(note) for note in observation.get("editorialNotes") or []):
        return [f"quotation from {observation['id']} is an editorial note, not the source text"]
    return [f"quotation does not appear verbatim in {observation['id']}"]


def _evidences(
    definition: PredicateDefinition,
    observation: dict[str, Any],
    subject: dict[str, Any],
    obj: dict[str, Any] | None,
) -> bool:
    """True when a Wikidata statement observation states this relationship."""
    if obj is None:
        return False
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
