"""Deterministic baseline proposer: Wikidata statement observation -> drafts.

It maps a statement through the predicate registry and resolves QIDs only to
existing local Entities with an accepted Wikidata identity link. It never
creates entities; unresolved QIDs are reported instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .registry import PredicateRegistry
from .schema import ProposalDraft

PROPOSER_ID = "wikidata-statement-proposer-v1"


class IdentityReader(Protocol):
    def entity_ids_for_wikidata(self, qid: str) -> list[str]: ...


@dataclass(frozen=True)
class ProposerResult:
    drafts: tuple[ProposalDraft, ...]
    unresolved: tuple[str, ...]


def drafts_from_observation(
    observation: dict[str, Any],
    reader: IdentityReader,
    registry: PredicateRegistry,
) -> ProposerResult:
    pid = observation["predicateExternalId"]
    source_qid = observation["sourceEntityId"]
    value_qid = observation["objectExternalId"]

    drafts: list[ProposalDraft] = []
    unresolved: list[str] = []
    mappings = registry.for_wikidata(pid)
    if not mappings:
        unresolved.append(f"{pid} has no registered predicate")

    for definition, mapping in mappings:
        holder_qid, target_qid = (source_qid, value_qid) if mapping.direction == "forward" else (value_qid, source_qid)
        endpoints = []
        for qid in (holder_qid, target_qid):
            local_ids = reader.entity_ids_for_wikidata(qid)
            if len(local_ids) != 1:
                problem = "no local Entity" if not local_ids else f"{len(local_ids)} local Entities"
                unresolved.append(f"{qid} has {problem}")
            endpoints.append(local_ids[0] if len(local_ids) == 1 else None)
        if None in endpoints:
            continue
        drafts.append(
            ProposalDraft(
                predicate=definition.id,
                subject_id=endpoints[0],
                object_id=endpoints[1],
                observation_ids=(observation["id"],),
                rationale=(
                    f"Wikidata statement {observation['externalStatementId']} at revision "
                    f"{observation['sourceRevision']}: {source_qid} {pid} {value_qid}."
                ),
                proposed_by=PROPOSER_ID,
            )
        )
    return ProposerResult(tuple(drafts), tuple(dict.fromkeys(unresolved)))
