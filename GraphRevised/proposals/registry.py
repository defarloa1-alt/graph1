"""Versioned predicate registry and deterministic assertion/proposal IDs."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .schema import ProposalDraft

REGISTRY_PATH = Path(__file__).resolve().parent / "predicates.v3.json"


@dataclass(frozen=True)
class WikidataMapping:
    pid: str
    direction: Literal["forward", "inverse"]


@dataclass(frozen=True)
class PredicateDefinition:
    id: str
    display: str
    subject_kinds: frozenset[str]
    object_kinds: frozenset[str]
    symmetric: bool
    temporal_qualification: Literal["none", "whenPresent", "required"]
    wikidata: tuple[WikidataMapping, ...]
    definition: str | None = None


@dataclass(frozen=True)
class PredicateRegistry:
    version: str
    temporal_qualifier_pids: frozenset[str]
    predicates: dict[str, PredicateDefinition]

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
            temporal_qualification=item["temporalQualification"],
            wikidata=tuple(WikidataMapping(**mapping) for mapping in item["wikidata"]),
            definition=item.get("definition"),
        )
        for item in data["predicates"]
    }
    return PredicateRegistry(
        version=data["version"],
        temporal_qualifier_pids=frozenset(data["temporalQualifierPropertyIds"]),
        predicates=predicates,
    )


def canonical_endpoints(definition: PredicateDefinition, subject_id: str, object_id: str) -> tuple[str, str]:
    """Symmetric predicates store their endpoints in sorted order."""
    if definition.symmetric:
        return tuple(sorted((subject_id, object_id)))  # type: ignore[return-value]
    return subject_id, object_id


def assertion_id(predicate_id: str, subject_id: str, object_id: str) -> str:
    """chr:assertion:<subject slug>:<predicate-kebab>:<object slug>."""
    predicate_slug = re.sub(r"(?<!^)(?=[A-Z])", "-", predicate_id).lower()
    return f"chr:assertion:{_slug(subject_id)}:{predicate_slug}:{_slug(object_id)}"


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
