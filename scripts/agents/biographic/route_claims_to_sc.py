#!/usr/bin/env python3
"""
Route biographic claims to DI SubjectConcept scope (ADR-021).

Creates (Claim)-[:IN_SCOPE]->(SubjectConcept) and denormalized routing fields.

Usage:
  python -m scripts.agents.biographic.route_claims_to_sc --dry
  python -m scripts.agents.biographic.route_claims_to_sc --write --limit 6000
  python -m scripts.agents.biographic.route_claims_to_sc --write --claim-id <id>
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

from scripts.agents.biographic.claim_sc_routing import (  # noqa: E402
    load_biographic_scopes,
    route_biographic_claim,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_claims(session: Any, *, limit: int, claim_id: str | None) -> list[dict[str, Any]]:
    if claim_id:
        where = "cl.claim_id = $claim_id"
        params: dict[str, Any] = {"claim_id": claim_id}
    else:
        where = "cl.source_agent = 'sfa_biographic'"
        params = {"limit": limit}

    rows = session.run(
        f"""
        MATCH (cl:Claim)
        WHERE {where}
        OPTIONAL MATCH (cl)-[:ASSERTS_EDGE]->(pe:ProposedEdge)
        OPTIONAL MATCH (pe)-[:FROM]->(src)
        OPTIONAL MATCH (pe)-[:TO]->(tgt)
        OPTIONAL MATCH (cl)-[:IN_SCOPE]->(existing:SubjectConcept)
        RETURN
          cl.claim_id AS claim_id,
          cl.subject_qid AS subject_qid,
          coalesce(cl.routed_subject_id, existing.subject_id) AS current_scope,
          pe.relationship_type AS relationship_type,
          src.qid AS from_qid,
          tgt.qid AS to_qid,
          coalesce(src.label, tgt.label) AS endpoint_label,
          cl.authority_ids AS authority_ids
        ORDER BY cl.timestamp DESC
        {"LIMIT $limit" if not claim_id else ""}
        """,
        params,
    )
    return [dict(r) for r in rows]


def _person_and_candidate(row: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    import json

    person_qid = row.get("subject_qid")
    from_qid = row.get("from_qid")
    to_qid = row.get("to_qid")
    auth = row.get("authority_ids")
    if isinstance(auth, str):
        try:
            auth = json.loads(auth)
        except json.JSONDecodeError:
            auth = {}
    if isinstance(auth, dict):
        person_qid = person_qid or auth.get("person_qid")
        cand_qid = auth.get("candidate_qid")
        if cand_qid:
            return person_qid, cand_qid, auth.get("pred_pid")
    if person_qid and from_qid and to_qid:
        if from_qid == person_qid:
            return person_qid, to_qid, None
        if to_qid == person_qid:
            return person_qid, from_qid, None
    return person_qid, to_qid or from_qid, None


def write_routing(session: Any, row: dict[str, Any], routing: Any, *, dry: bool) -> bool:
    if dry:
        return True
    session.run(
        """
        MATCH (cl:Claim {claim_id: $claim_id})
        MATCH (sc:SubjectConcept {subject_id: $subject_id})
        OPTIONAL MATCH (cl)-[old:IN_SCOPE]->(:SubjectConcept)
        DELETE old
        MERGE (cl)-[r:IN_SCOPE]->(sc)
        SET r.routing_score = $score,
            r.routing_method = $method,
            r.routing_reason = $reason,
            r.routed_at = datetime($routed_at),
            cl.routed_subject_id = $subject_id,
            cl.routed_subject_label = $label,
            cl.routing_score = $score,
            cl.routing_method = $method
        """,
        claim_id=row["claim_id"],
        subject_id=routing.subject_id,
        label=routing.label,
        score=routing.score,
        method=routing.method,
        reason=routing.reason,
        routed_at=_utc_now_iso(),
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Route biographic claims to SubjectConcept scope")
    parser.add_argument("--write", action="store_true", help="Persist IN_SCOPE edges to Neo4j")
    parser.add_argument("--dry", action="store_true", help="Preview routing only (default)")
    parser.add_argument("--limit", type=int, default=500, help="Max claims to process")
    parser.add_argument("--claim-id", type=str, default=None, help="Route a single claim")
    parser.add_argument(
        "--proposals",
        type=Path,
        default=ROOT / "output" / "di_proposals" / "Q17167_proposals_enriched.json",
        help="DI proposals JSON for SC labels",
    )
    args = parser.parse_args()
    dry = not args.write

    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD not configured", file=sys.stderr)
        return 1

    scopes = load_biographic_scopes(args.proposals)
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    routed = 0
    skipped = 0
    by_scope: dict[str, int] = {}

    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            claims = fetch_claims(session, limit=args.limit, claim_id=args.claim_id)
            print(f"Claims to route: {len(claims)}  dry={dry}")

            for row in claims:
                person_qid, candidate_qid, pred_pid = _person_and_candidate(row)
                routing = route_biographic_claim(
                    person_qid=person_qid,
                    candidate_qid=candidate_qid,
                    relationship_type=row.get("relationship_type"),
                    pred_pid=pred_pid,
                    candidate_label=row.get("endpoint_label"),
                    scopes=scopes,
                )
                if (
                    row.get("current_scope") == routing.subject_id
                    and not args.claim_id
                ):
                    skipped += 1
                    continue

                write_routing(session, row, routing, dry=dry)
                routed += 1
                by_scope[routing.scope_key] = by_scope.get(routing.scope_key, 0) + 1

                if routed <= 15 or args.claim_id:
                    print(
                        f"  {row['claim_id'][:48]:48s}  ->  {routing.label[:40]:40s}  "
                        f"({routing.score:.2f} {routing.method})"
                    )

    finally:
        driver.close()

    print(f"\nRouted: {routed}  skipped (unchanged): {skipped}")
    if by_scope:
        print("By scope:")
        for key, n in sorted(by_scope.items(), key=lambda x: -x[1]):
            print(f"  {key:32s}  {n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
