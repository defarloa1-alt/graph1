"""Entities proposed by an agent: kinds an inquiry allows (periods, depicted events).

An agent may not decide identity, but some entities are the sources' own
units: a period an author names, an action a narrative depicts. These may be
proposed. A proposed Entity has `status: proposed`, is shown in exploration
at once with that status, and waits for the curator to accept it (with a Wikidata identity
where one exists) or reject it. Before one is created, local candidates of
the same kind are checked: an exact match is reused instead. Each mention is
recorded as an Annotation of kind `entity-mention` on the passage, so the
curator sees where and how the entity was named.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from GraphRevised.capture.core import annotation_id
from GraphRevised.identity.local_candidates import candidates
from GraphRevised.operations import run_write


def proposed_entity_id(kind: str, label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"chr:entity:proposed-{kind.lower()}-{slug}"


def propose_entity(
    tx: Any,
    operations: dict[str, str],
    *,
    kind: str,
    label: str,
    proposed_by: str,
    observation_id: str,
    quotation: str,
    note: str | None = None,
) -> dict[str, Any]:
    """Reuse an existing entity with the same name and kind, or create a proposed one;
    record the mention either way. Returns {id, created, reused, candidates}."""
    label = " ".join(label.split())
    exact = [c for c in candidates(tx, label, kind, threshold=1.0) if c["score"] >= 1.0]
    live = [c for c in exact if (tx.run("MATCH (e:Entity {id: $id}) RETURN e.status AS s", id=c["id"]).single()["s"]
                                 != "deprecated")]
    if live:
        entity_id, created = live[0]["id"], False
    else:
        entity_id = proposed_entity_id(kind, label)
        existing = tx.run("MATCH (e:Entity {id: $id}) RETURN e.kind AS kind", id=entity_id).single()
        created = existing is None
        if created:
            run_write(tx, operations, "upsert_entity", {
                "id": entity_id, "kind": kind, "label": label, "description": None,
                "status": "proposed", "shortLabel": None,
            })
    mention_note = note or f"{kind} named as \"{label}\""
    run_write(tx, operations, "upsert_annotation", {
        "id": annotation_id(proposed_by, observation_id, mention_note, [entity_id]),
        "label": mention_note[:120], "kind": "entity-mention", "noteType": "detail", "note": mention_note,
        "author": proposed_by, "visibility": "private", "createdAt": datetime.now(timezone.utc).isoformat(),
        "observationId": observation_id, "quotation": quotation, "concerns": [entity_id],
    })
    nearby = [c for c in candidates(tx, label, kind, exclude=entity_id) if c["score"] < 1.0]
    return {"id": entity_id, "created": created, "reused": not created and bool(live), "candidates": nearby}


def proposed_entities(tx: Any) -> list[dict[str, Any]]:
    """Proposed entities with their mentions, for review."""
    return tx.run(
        """
        MATCH (entity:Entity {status: "proposed"})
        OPTIONAL MATCH (mention:Annotation {kind: "entity-mention"})-[:CONCERNS]->(entity)
        OPTIONAL MATCH (mention)-[link:ANNOTATES]->(observation:SourceObservation)
        OPTIONAL MATCH (observation)-[:IN_WORK]->(work:Entity)
        OPTIONAL MATCH (claim:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(entity)
        RETURN entity.id AS id, entity.kind AS kind, entity.label AS label,
               collect(DISTINCT {work: work.label, locator: observation.locator, quotation: link.quotation}) AS mentions,
               collect(DISTINCT claim.label) AS claims
        ORDER BY kind, label
        """
    ).data()
