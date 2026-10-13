"""Deterministic baseline proposer: Wikidata statement observation -> drafts.

It maps a statement through the predicate registry and resolves QIDs only to
existing local Entities with an accepted Wikidata identity link. It never
creates entities; unresolved QIDs are reported instead. When one property maps
to several predicates (P361 "part of": partOf, subperiodOf, memberOf), only
those whose kinds fit the endpoints are drafted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .registry import PredicateRegistry
from .schema import ProposalDraft, TimeQualifier

PROPOSER_ID = "wikidata-statement-proposer-v1"


class IdentityReader(Protocol):
    def entity_ids_for_wikidata(self, qid: str) -> list[str]: ...

    def entity(self, entity_id: str) -> dict[str, Any] | None: ...


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
    value_qid = observation.get("objectExternalId")  # absent for a time statement (Neo4j stores no nulls)
    stated = observation.get("statementTimeEdtf")

    drafts: list[ProposalDraft] = []
    unresolved: list[str] = []
    misfits: list[str] = []
    mappings = registry.for_wikidata(pid)
    if not mappings:
        unresolved.append(f"{pid} has no registered predicate")

    for definition, mapping in mappings:
        if definition.unary != (value_qid is None):
            continue  # a dated unary claim comes from a time statement, a link from an item statement
        holder_qid, target_qid = (source_qid, value_qid) if mapping.direction == "forward" else (value_qid, source_qid)
        endpoints = []
        for qid in (holder_qid, target_qid) if target_qid is not None else (holder_qid,):
            local_ids = reader.entity_ids_for_wikidata(qid)
            if len(local_ids) != 1:
                problem = "no local Entity" if not local_ids else f"{len(local_ids)} local Entities"
                unresolved.append(f"{qid} has {problem}")
            endpoints.append(local_ids[0] if len(local_ids) == 1 else None)
        if None in endpoints:
            continue
        kinds = [(reader.entity(endpoint) or {}).get("kind") for endpoint in endpoints]
        if not definition.allows_kinds(kinds[0], kinds[1] if len(kinds) > 1 else None):
            misfits.append(f"{definition.id} does not relate a {kinds[0]}" + (f" to a {kinds[1]}" if len(kinds) > 1 else ""))
            continue
        time = None
        if stated and definition.qualifiers.time != "none":
            time = TimeQualifier(
                source_expression=f"{observation.get('statementTimeDisplay') or stated} (Wikidata)",
                edtf=stated, calendar=observation["statementTimeCalendar"], normalization_basis="source",
                mode=observation.get("statementTimeMode") or "during")
        drafts.append(
            ProposalDraft(
                predicate=definition.id,
                subject_id=endpoints[0],
                object_id=endpoints[1] if len(endpoints) > 1 else None,
                time=time,
                observation_ids=(observation["id"],),
                rationale=(
                    f"Wikidata statement {observation['externalStatementId']} at revision "
                    f"{observation['sourceRevision']}: {source_qid} {pid} {value_qid or stated}."
                ),
                proposed_by=PROPOSER_ID,
            )
        )
    if not drafts and misfits and not unresolved:
        unresolved.append(f"{pid} fits no registered predicate here: " + "; ".join(misfits))
    return ProposerResult(tuple(drafts), tuple(dict.fromkeys(unresolved)))
