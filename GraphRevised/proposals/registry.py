"""Versioned predicate registry and deterministic assertion/proposal IDs."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .schema import ProposalDraft

REGISTRY_PATH = Path(__file__).resolve().parent / "predicates.v6.json"

Requirement = Literal["none", "optional", "required"]
TimeRequirement = Literal["none", "optional", "required", "withRole"]


@dataclass(frozen=True)
class WikidataMapping:
    pid: str
    direction: Literal["forward", "inverse"]


@dataclass(frozen=True)
class Qualifiers:
    """Which qualifiers a predicate allows or requires. `withRole`: time is
    required when the claim has a role and allowed otherwise."""

    context: Requirement = "none"
    role: Requirement = "none"
    time: TimeRequirement = "none"


@dataclass(frozen=True)
class PredicateDefinition:
    id: str
    display: str
    subject_kinds: frozenset[str]
    object_kinds: frozenset[str]
    symmetric: bool
    wikidata: tuple[WikidataMapping, ...]
    definition: str | None = None
    qualifiers: Qualifiers = Qualifiers()
    modes: frozenset[str] = frozenset({"asserted"})
    category: Literal["factual", "interpretive"] = "factual"

    @property
    def unary(self) -> bool:
        """A unary predicate has no object: its content is its qualifiers."""
        return not self.object_kinds


@dataclass(frozen=True)
class PredicateRegistry:
    version: str
    temporal_qualifier_pids: frozenset[str]
    role_qualifier_pids: frozenset[str]
    predicates: dict[str, PredicateDefinition]
    entity_kinds: tuple[str, ...] = ()
    role_kind: str = "Other"

    def get(self, predicate_id: str) -> PredicateDefinition | None:
        return self.predicates.get(predicate_id)

    def for_wikidata(self, pid: str) -> list[tuple[PredicateDefinition, WikidataMapping]]:
        return [
            (definition, mapping)
            for definition in self.predicates.values()
            for mapping in definition.wikidata
            if mapping.pid == pid
        ]


def load_registry(path: Path = REGISTRY_PATH) -> PredicateRegistry:
    data = json.loads(path.read_text(encoding="utf-8"))
    predicates = {
        item["id"]: PredicateDefinition(
            id=item["id"],
            display=item["display"],
            subject_kinds=frozenset(item["subjectKinds"]),
            object_kinds=frozenset(item["objectKinds"]),
            symmetric=item["symmetric"],
            wikidata=tuple(WikidataMapping(**mapping) for mapping in item["wikidata"]),
            definition=item.get("definition"),
            qualifiers=Qualifiers(**item.get("qualifiers", {})),
            modes=frozenset(item.get("modes", ["asserted"])),
            category=item.get("category", "factual"),
        )
        for item in data["predicates"]
    }
    return PredicateRegistry(
        version=data["version"],
        temporal_qualifier_pids=frozenset(data["temporalQualifierPropertyIds"]),
        role_qualifier_pids=frozenset(data.get("roleQualifierPropertyIds", [])),
        predicates=predicates,
        entity_kinds=tuple(data.get("entityKinds", ())),
        role_kind=data.get("roleKind", "Other"),
    )


def canonical_endpoints(
    definition: PredicateDefinition, subject_id: str, object_id: str | None
) -> tuple[str, str | None]:
    """Symmetric predicates store their endpoints in sorted order."""
    if definition.symmetric and object_id is not None:
        return tuple(sorted((subject_id, object_id)))  # type: ignore[return-value]
    return subject_id, object_id


def qualifier_signature(draft: ProposalDraft) -> dict[str, Any]:
    """The identity-defining qualifiers of a draft, in canonical form. Empty
    for an unqualified asserted claim, whose ID then has no qualifier suffix."""
    signature: dict[str, Any] = {}
    if draft.mode != "asserted":
        signature["mode"] = draft.mode
        signature["attributedTo"] = draft.attributed_to
    if draft.context_id:
        signature["context"] = draft.context_id
    if draft.role_id:
        signature["role"] = draft.role_id
    if draft.time is not None:
        time = draft.time
        if time.edtf:
            signature["time"] = {"edtf": time.edtf, "calendar": time.calendar}
        elif time.relative_offset:
            signature["time"] = {"relativeOffset": time.relative_offset}
        else:
            signature["time"] = {"sourceExpression": time.source_expression}
    return signature


def assertion_id(
    predicate_id: str,
    subject_id: str,
    object_id: str | None,
    qualifiers: dict[str, Any] | None = None,
) -> str:
    """chr:assertion:<subject slug>:<predicate-kebab>[:<object slug>][:q<digest>].

    Unqualified claims keep the original form; qualifiers append a digest of
    their canonical serialization, so differently qualified claims differ."""
    predicate_slug = re.sub(r"(?<!^)(?=[A-Z])", "-", predicate_id).lower()
    identifier = f"chr:assertion:{_slug(subject_id)}:{predicate_slug}"
    if object_id is not None:
        identifier += f":{_slug(object_id)}"
    if qualifiers:
        canonical = json.dumps(qualifiers, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        identifier += ":q" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:10]
    return identifier


def proposal_id(draft: ProposalDraft, canonical_assertion_id: str) -> str:
    """Same assertion and same evidence set always yield the same proposal ID."""
    normalized = json.dumps(
        {
            "schema": draft.schema_version,
            "assertion": canonical_assertion_id,
            "observations": sorted(draft.observation_ids),
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"chr:proposal:{canonical_assertion_id.removeprefix('chr:assertion:')}:{digest}"


def _slug(local_id: str) -> str:
    return local_id.split(":", 2)[2]
