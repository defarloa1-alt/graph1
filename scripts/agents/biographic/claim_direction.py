"""Direction and labeling helpers for biographic backlink claims."""

from __future__ import annotations

from typing import Any

# Person anchor is semantic agent — swap (candidate)→(person) to (person)→(candidate)
AGENT_ANCHOR_EDGE_TYPES = frozenset(
    {
        "RAISED_LEGION",
        "FOUNDED",
        "PARTICIPATED_IN",
        "ORGANIZED",
        "COMMISSIONED",
        "HEADED",
        "CHAIRED",
        "HAD_ROLE",
    }
)

PREDICATE_HINTS: dict[str, str] = {
    "P22": "father (P22)",
    "P25": "mother (P25)",
    "P26": "spouse (P26)",
    "P40": "child (P40)",
    "P112": "founded by (P112)",
    "P138": "named after (P138)",
    "P176": "manufacturer / commissioner (P176)",
    "P3373": "sibling (P3373)",
    "P607": "conflict participant (P607)",
    "P664": "organizer (P664)",
    "P710": "participant (P710)",
    "P793": "significant event (P793)",
    "P1038": "relative (P1038)",
    "P1344": "participant in (P1344)",
}


def agent_anchor_edge(edge_type: str) -> bool:
    return (edge_type or "").upper() in AGENT_ANCHOR_EDGE_TYPES


def _rel_phrase(rel: str) -> str:
    return (rel or "related").replace("_", " ").lower()


def build_claim_label(
    person_label: str,
    candidate_label: str,
    relationship_type: str,
    *,
    agent_is_person: bool,
) -> str:
    rel = _rel_phrase(relationship_type)
    if agent_is_person:
        return f"{person_label} — {rel} — {candidate_label}"
    return f"{candidate_label} — {rel} — {person_label}"


def build_claim_description(
    *,
    person_label: str,
    person_qid: str,
    candidate_label: str,
    candidate_qid: str,
    relationship_type: str,
    pred_pid: str,
    source: str,
    agent_is_person: bool,
) -> str:
    pid_hint = PREDICATE_HINTS.get(pred_pid, pred_pid)
    rel = relationship_type.upper()
    if agent_is_person:
        return (
            f"Wikidata backlink harvest: {candidate_label} ({candidate_qid}) carries "
            f"{pid_hint} pointing at person anchor {person_label} ({person_qid}). "
            f"Canonical reading: {person_label} { _rel_phrase(rel) } {candidate_label}. "
            f"Proposed edge: ({person_label})-[:{rel}]->({candidate_label}). "
            f"Harvest source: {source}."
        )
    return (
        f"Wikidata backlink harvest: {candidate_label} ({candidate_qid}) carries "
        f"{pid_hint} pointing at {person_label} ({person_qid}). "
        f"Proposed edge: ({candidate_label})-[:{rel}]->({person_label}). "
        f"Harvest source: {source}."
    )


def resolve_claim_endpoints(
    row: dict[str, Any],
    relationship_type: str,
    *,
    normalize_entity_id,
) -> dict[str, Any]:
    """Return ingest entity_id, target_id, and metadata for a bio candidate row."""
    edge_type = relationship_type.upper()
    agent_is_person = agent_anchor_edge(edge_type)
    candidate_qid = row["candidate_qid"]
    person_qid = row["person_qid"]
    candidate_eid = normalize_entity_id(row.get("candidate_entity_id"), candidate_qid)
    person_eid = normalize_entity_id(row.get("person_entity_id"), person_qid)

    if agent_is_person:
        entity_id = person_eid
        target_id = candidate_eid
    else:
        entity_id = candidate_eid
        target_id = person_eid

    return {
        "entity_id": entity_id,
        "target_id": target_id,
        "agent_is_person": agent_is_person,
        "candidate_qid": candidate_qid,
        "person_qid": person_qid,
    }
