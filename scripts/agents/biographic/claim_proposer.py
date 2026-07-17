#!/usr/bin/env python3
"""
Biographic claim proposer — promote BIO_CANDIDATE_REL stubs to Claim nodes.

Reads harvested Wikidata backlink candidates, runs Fischer lint via
ClaimIngestionPipeline, and marks edges agent_reviewed.

Usage:
  python -m scripts.agents.biographic.claim_proposer --limit 25 --dry
  python -m scripts.agents.biographic.claim_proposer --limit 25 --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "tools"))

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

from claim_ingestion_pipeline import ClaimIngestionPipeline  # noqa: E402
from scripts.agents.biographic.claim_direction import (  # noqa: E402
    build_claim_description,
    build_claim_label,
    resolve_claim_endpoints,
)
from scripts.tools.sys_registry import validate_relationship_type  # noqa: E402

EDGE_TO_REL: dict[str, str] = {
    "PARENT_OF": "PARENT_OF",
    "CHILD_OF": "CHILD_OF",
    "SPOUSE_OF": "SPOUSE_OF",
    "SIBLING_OF": "SIBLING_OF",
    "HALF_SIBLING_OF": "HALF_SIBLING_OF",
    "POSITION_HELD": "POSITION_HELD",
}


def _normalize_entity_id(raw: str | None, qid: str) -> str:
    if raw:
        return raw
    q = qid.replace(":", "_")
    return f"person_{q.lower()}" if q.startswith("Q") else f"entity_{q}"


def fetch_candidates(session: Any, *, limit: int) -> list[dict[str, Any]]:
    rows = session.run(
        """
        MATCH (c)-[r:BIO_CANDIDATE_REL]->(p:Person)
        WHERE coalesce(r.agent_reviewed, false) = false
          AND r.edge_type IS NOT NULL
          AND p.qid IS NOT NULL
          AND c.qid IS NOT NULL
        RETURN
          c.qid AS candidate_qid,
          coalesce(c.entity_id, 'entity_' + c.qid) AS candidate_entity_id,
          coalesce(c.label, r.item_label, c.qid) AS candidate_label,
          p.qid AS person_qid,
          coalesce(p.entity_id, 'person_' + toLower(p.qid)) AS person_entity_id,
          coalesce(p.label, p.qid) AS person_label,
          r.edge_type AS edge_type,
          r.pred_pid AS pred_pid,
          r.item_label AS item_label,
          r.source AS source
        ORDER BY r.harvested_at DESC
        LIMIT $limit
        """,
        limit=limit,
    )
    return [dict(row) for row in rows]


def propose_one(
    pipeline: ClaimIngestionPipeline,
    row: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    edge_type = (row.get("edge_type") or "").upper()
    rel = EDGE_TO_REL.get(edge_type, edge_type)
    pred_pid = row.get("pred_pid") or edge_type
    candidate_label = row.get("candidate_label") or row["candidate_qid"]
    person_label = row.get("person_label") or row["person_qid"]
    source = row.get("source") or "wikidata_backlink"

    endpoints = resolve_claim_endpoints(row, rel, normalize_entity_id=_normalize_entity_id)
    reg = validate_relationship_type(rel, pred_pid=pred_pid)
    if not reg.valid:
        return {
            "status": "registry_rejected",
            "error": reg.message,
            "relationship_type": rel,
            "person_qid": endpoints["person_qid"],
            "candidate_qid": endpoints["candidate_qid"],
        }
    rel = reg.normalized
    label = build_claim_label(
        person_label,
        candidate_label,
        rel,
        agent_is_person=endpoints["agent_is_person"],
    )
    description = build_claim_description(
        person_label=person_label,
        person_qid=endpoints["person_qid"],
        candidate_label=candidate_label,
        candidate_qid=endpoints["candidate_qid"],
        relationship_type=rel,
        pred_pid=pred_pid,
        source=source,
        agent_is_person=endpoints["agent_is_person"],
    )
    claim_signature = {
        "qid": endpoints["person_qid"],
        "pvalues": [pred_pid],
        "values": {pred_pid: endpoints["candidate_qid"]},
    }

    if dry_run:
        return {
            "status": "dry_run",
            "label": label,
            "description": description,
            "relationship_type": rel,
            "person_qid": endpoints["person_qid"],
            "candidate_qid": endpoints["candidate_qid"],
            "agent_is_person": endpoints["agent_is_person"],
        }

    result = pipeline.ingest_claim(
        entity_id=endpoints["entity_id"],
        relationship_type=rel,
        target_id=endpoints["target_id"],
        confidence=0.82,
        label=label,
        description=description,
        subject_qid=endpoints["person_qid"],
        retrieval_source=source,
        reasoning_notes=description,
        facet="biographic",
        claim_signature=claim_signature,
        claim_type="documentary",
        source_agent="sfa_biographic",
        authority_source="wikidata",
        authority_ids={
            "person_qid": endpoints["person_qid"],
            "candidate_qid": endpoints["candidate_qid"],
            "pred_pid": pred_pid,
        },
        pred_pid=pred_pid,
    )
    result["registry_status"] = reg.registry_status
    result["label"] = label
    result["description"] = description
    result["person_qid"] = endpoints["person_qid"]
    result["candidate_qid"] = endpoints["candidate_qid"]
    return result


def mark_reviewed(session: Any, person_qid: str, candidate_qid: str, pred_pid: str, claim_id: str | None) -> None:
    session.run(
        """
        MATCH (c {qid: $candidate_qid})-[r:BIO_CANDIDATE_REL]->(p:Person {qid: $person_qid})
        WHERE r.pred_pid = $pred_pid
        SET r.agent_reviewed = true,
            r.claim_id = coalesce($claim_id, r.claim_id),
            r.reviewed_at = datetime()
        """,
        person_qid=person_qid,
        candidate_qid=candidate_qid,
        pred_pid=pred_pid,
        claim_id=claim_id,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote BIO_CANDIDATE_REL to Claim nodes (Fischer linted)")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--dry", action="store_true", help="Preview only")
    ap.add_argument("--write", action="store_true", help="Create Claim nodes")
    args = ap.parse_args()

    if not args.dry and not args.write:
        print("Specify --dry or --write")
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    pipeline = ClaimIngestionPipeline(driver, database=NEO4J_DATABASE or "neo4j")
    stats = {"processed": 0, "created": 0, "promoted": 0, "flagged": 0, "errors": 0, "skipped_fischer": 0}

    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            candidates = fetch_candidates(session, limit=args.limit)
            print(f"Biographic claim proposer — {len(candidates)} candidates (limit={args.limit})")

            for row in candidates:
                stats["processed"] += 1
                result = propose_one(pipeline, row, dry_run=args.dry)
                status = result.get("status")
                if status == "dry_run":
                    print(f"  [DRY] {result['label'][:90]}")
                    continue
                if status == "error":
                    stats["errors"] += 1
                    print(f"  [ERR] {result.get('error')} — {result.get('label', '')[:70]}")
                    continue

                stats["created"] += 1
                if result.get("promoted"):
                    stats["promoted"] += 1
                fischer_status = result.get("fischer_status", "skipped")
                if fischer_status == "skipped":
                    stats["skipped_fischer"] += 1
                elif result.get("fischer_hits") or result.get("fallacies_detected"):
                    stats["flagged"] += 1

                mark_reviewed(
                    session,
                    row["person_qid"],
                    row["candidate_qid"],
                    row.get("pred_pid") or row.get("edge_type"),
                    result.get("claim_id"),
                )
                flag_note = ""
                if result.get("fischer_hits"):
                    flag_note = f" Fischer: {result['fischer_hits']}"
                elif fischer_status == "skipped":
                    flag_note = " Fischer: skipped (documentary)"
                print(
                    f"  [{status}] {result.get('claim_id', '?')[:24]} "
                    f"promoted={result.get('promoted')}{flag_note}"
                )
    finally:
        driver.close()

    print(json.dumps(stats, indent=2))
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
