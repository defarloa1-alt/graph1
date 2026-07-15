#!/usr/bin/env python3
"""
Enrich biographic Claim nodes with Wikidata statement qualifiers (P580/P582/P585).

Backlink harvest stores predicate links only. This pass re-fetches the Wikidata
statement and writes temporal fields on the Claim before human review.

Usage:
  python -m scripts.agents.biographic.enrich_claims --limit 25 --dry
  python -m scripts.agents.biographic.enrich_claims --limit 500 --write
  python -m scripts.agents.biographic.enrich_claims --claim-id claim_bba33f403591 --write
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

from scripts.agents.biographic.agent import fetch_entity_api, parse_year  # noqa: E402

DATE_SENSITIVE_RELS = frozenset(
    {
        "SPOUSE_OF",
        "POSITION_HELD",
        "HAD_ROLE",
        "PARTICIPATED_IN",
        "ORGANIZED",
        "FOUNDED",
        "RAISED_LEGION",
        "COMMISSIONED",
        "HEADED",
        "CHAIRED",
    }
)

SLEEP_SEC = 0.5


def _parse_authority_ids(raw: Any) -> dict[str, str]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}


def _qualifier_time(qualifiers: dict, pid: str) -> str | None:
    items = qualifiers.get(pid) or []
    if not items:
        return None
    val = items[0].get("datavalue", {}).get("value", {})
    if isinstance(val, dict):
        return val.get("time")
    return None


def _statement_value_id(mainsnak: dict) -> str | None:
    val = mainsnak.get("datavalue", {}).get("value", {})
    if isinstance(val, dict):
        vid = val.get("id")
        if vid and str(vid).startswith("Q"):
            return str(vid)
    return None


def find_statement_qualifiers(
    *,
    person_qid: str,
    candidate_qid: str,
    pred_pid: str,
) -> dict[str, Any]:
    """Locate the Wikidata statement and extract temporal qualifiers."""
    entities: dict[str, Any] = {}
    for subject_qid in (candidate_qid, person_qid):
        if subject_qid in entities:
            continue
        time.sleep(SLEEP_SEC)
        entities.update(fetch_entity_api(subject_qid))

    other_qid = person_qid
    matched_on: str | None = None
    qualifiers: dict[str, Any] = {}

    for subject_qid, target_qid in (
        (candidate_qid, person_qid),
        (person_qid, candidate_qid),
    ):
        entity = entities.get(subject_qid) or {}
        for stmt in entity.get("claims", {}).get(pred_pid, []):
            if stmt.get("mainsnak", {}).get("snaktype") != "value":
                continue
            if _statement_value_id(stmt.get("mainsnak", {})) != target_qid:
                continue
            matched_on = subject_qid
            q = stmt.get("qualifiers") or {}
            qualifiers = {
                "start_year": parse_year(_qualifier_time(q, "P580") or ""),
                "end_year": parse_year(_qualifier_time(q, "P582") or ""),
                "point_year": parse_year(_qualifier_time(q, "P585") or ""),
            }
            break
        if matched_on:
            break

    return {
        "matched_on": matched_on,
        "start_year": qualifiers.get("start_year"),
        "end_year": qualifiers.get("end_year"),
        "point_year": qualifiers.get("point_year"),
    }


def classify_enrichment(
    *,
    relationship_type: str,
    start_year: int | None,
    end_year: int | None,
    point_year: int | None,
    matched_on: str | None,
) -> tuple[str, str]:
    rel = (relationship_type or "").upper()
    has_dates = any(v is not None for v in (start_year, end_year, point_year))

    if not matched_on:
        return "missing", "Wikidata statement not found for predicate + endpoints"

    if has_dates:
        return "complete", "Temporal qualifiers harvested from Wikidata"

    if rel in DATE_SENSITIVE_RELS:
        return "partial", "Statement found but no P580/P582/P585 qualifiers on Wikidata"

    return "not_applicable", "Relationship type typically lacks statement dates"


def fetch_claims(session: Any, *, limit: int, claim_id: str | None) -> list[dict[str, Any]]:
    if claim_id:
        where = "cl.claim_id = $claim_id"
        params: dict[str, Any] = {"claim_id": claim_id}
    else:
        where = (
            "cl.source_agent = 'sfa_biographic' "
            "AND coalesce(cl.enrichment_status, 'pending') IN ['pending', 'missing', 'partial']"
        )
        params = {"limit": limit}

    query = f"""
        MATCH (cl:Claim)
        WHERE {where}
        OPTIONAL MATCH (cl)-[:ASSERTS_EDGE]->(pe:ProposedEdge)
        RETURN cl.claim_id AS claim_id,
               cl.authority_ids AS authority_ids,
               cl.enrichment_status AS enrichment_status,
               pe.relationship_type AS relationship_type
        ORDER BY cl.timestamp DESC
    """
    if not claim_id:
        query += "\n        LIMIT $limit"
    return [dict(r) for r in session.run(query, params)]


def enrich_one(row: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    auth = _parse_authority_ids(row.get("authority_ids"))
    person_qid = auth.get("person_qid") or ""
    candidate_qid = auth.get("candidate_qid") or ""
    pred_pid = auth.get("pred_pid") or ""
    rel = row.get("relationship_type") or ""

    if not person_qid or not candidate_qid or not pred_pid:
        return {
            "claim_id": row["claim_id"],
            "status": "skipped",
            "reason": "missing authority_ids",
        }

    qual = find_statement_qualifiers(
        person_qid=person_qid,
        candidate_qid=candidate_qid,
        pred_pid=pred_pid,
    )
    enrichment_status, enrichment_notes = classify_enrichment(
        relationship_type=rel,
        start_year=qual["start_year"],
        end_year=qual["end_year"],
        point_year=qual["point_year"],
        matched_on=qual["matched_on"],
    )

    result = {
        "claim_id": row["claim_id"],
        "status": enrichment_status,
        "enrichment_notes": enrichment_notes,
        "matched_on": qual["matched_on"],
        "start_year": qual["start_year"],
        "end_year": qual["end_year"],
        "point_year": qual["point_year"],
    }

    if dry_run:
        result["dry_run"] = True
        return result

    return result


def write_enrichment(session: Any, result: dict[str, Any]) -> None:
    session.run(
        """
        MATCH (cl:Claim {claim_id: $claim_id})
        SET cl.start_year = $start_year,
            cl.end_year = $end_year,
            cl.point_year = $point_year,
            cl.enrichment_status = $enrichment_status,
            cl.enrichment_notes = $enrichment_notes,
            cl.enriched_at = $enriched_at,
            cl.enrichment_source = 'wikidata_qualifiers'
        """,
        claim_id=result["claim_id"],
        start_year=result.get("start_year"),
        end_year=result.get("end_year"),
        point_year=result.get("point_year"),
        enrichment_status=result.get("status"),
        enrichment_notes=result.get("enrichment_notes"),
        enriched_at=datetime.now(timezone.utc).isoformat(),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Enrich biographic claims with Wikidata qualifiers")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--claim-id", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if not args.dry and not args.write:
        print("Specify --dry or --write")
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    stats: dict[str, int] = {
        "processed": 0,
        "complete": 0,
        "partial": 0,
        "missing": 0,
        "not_applicable": 0,
        "skipped": 0,
    }

    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            rows = fetch_claims(session, limit=args.limit, claim_id=args.claim_id)
            print(f"Enriching {len(rows)} claim(s)")
            for row in rows:
                stats["processed"] += 1
                result = enrich_one(row, dry_run=args.dry)
                key = result.get("status", "skipped")
                stats[key] = stats.get(key, 0) + 1
                print(
                    f"  {result['claim_id']}: {result.get('status')} "
                    f"{result.get('start_year') or '?'}-{result.get('end_year') or '?'} "
                    f"({result.get('enrichment_notes', '')[:60]})"
                )
                if args.write and result.get("status") != "skipped":
                    write_enrichment(session, result)
    finally:
        driver.close()

    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
