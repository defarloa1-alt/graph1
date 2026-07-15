#!/usr/bin/env python3
"""
Fix inverted biographic claim directions (person-as-agent edges).

Repairs label, description, and ProposedEdge FROM/TO for claims where the
person anchor should be the edge source (RAISED_LEGION, PARTICIPATED_IN, etc.).

Usage:
  python -m scripts.agents.biographic.fix_claim_direction --dry
  python -m scripts.agents.biographic.fix_claim_direction --write
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

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

from .claim_direction import (
    AGENT_ANCHOR_EDGE_TYPES,
    agent_anchor_edge,
    build_claim_description,
    build_claim_label,
)


def fetch_inverted(session: Any) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (cl:Claim {source_agent: 'sfa_biographic'})
              -[:ASSERTS_EDGE]->(pe:ProposedEdge)
              -[:FROM]->(src),
              (pe)-[:TO]->(tgt)
        WHERE pe.relationship_type IN $types
          AND coalesce(cl.direction_corrected, false) = false
          AND cl.subject_qid = tgt.qid
          AND src.qid <> cl.subject_qid
        RETURN cl.claim_id AS claim_id,
               cl.subject_qid AS person_qid,
               pe.relationship_type AS rel,
               pe.edge_id AS edge_id,
               src.qid AS src_qid,
               coalesce(src.label, src.qid) AS src_label,
               coalesce(src.entity_id, 'entity_' + src.qid) AS src_entity_id,
               tgt.qid AS tgt_qid,
               coalesce(tgt.label, tgt.qid) AS tgt_label,
               coalesce(tgt.entity_id, 'person_' + toLower(tgt.qid)) AS tgt_entity_id
        """,
        types=list(AGENT_ANCHOR_EDGE_TYPES),
    ).data()


def repair_one(session: Any, row: dict[str, Any], *, dry_run: bool) -> None:
    import json as json_mod

    person_label = row["tgt_label"]
    person_qid = row["tgt_qid"]
    candidate_label = row["src_label"]
    candidate_qid = row["src_qid"]
    rel = row["rel"]

    claim_row = session.run(
        """
        MATCH (cl:Claim {claim_id: $claim_id})
        RETURN cl.authority_ids AS authority_ids
        """,
        claim_id=row["claim_id"],
    ).single()
    auth_raw = claim_row["authority_ids"] if claim_row else None
    pred_pid = ""
    source = "wikidata_backlink"
    if auth_raw:
        try:
            auth = json_mod.loads(auth_raw) if isinstance(auth_raw, str) else auth_raw
            if isinstance(auth, dict):
                pred_pid = auth.get("pred_pid") or ""
        except json_mod.JSONDecodeError:
            pass

    label = build_claim_label(
        person_label, candidate_label, rel, agent_is_person=True
    )
    description = build_claim_description(
        person_label=person_label,
        person_qid=person_qid,
        candidate_label=candidate_label,
        candidate_qid=candidate_qid,
        relationship_type=rel,
        pred_pid=pred_pid,
        source=source,
        agent_is_person=True,
    )

    if dry_run:
        return

    session.run(
        """
        MATCH (cl:Claim {claim_id: $claim_id})-[:ASSERTS_EDGE]->(pe:ProposedEdge {edge_id: $edge_id})
        MATCH (person {qid: $person_qid})
        MATCH (candidate {qid: $candidate_qid})
        SET cl.label = $label,
            cl.text = $label,
            cl.description = $description,
            cl.direction_corrected = true,
            pe.source_entity_id = person.entity_id,
            pe.target_entity_id = candidate.entity_id,
            pe.direction_corrected = true
        WITH pe, person, candidate
        OPTIONAL MATCH (pe)-[old_from:FROM]->()
        OPTIONAL MATCH (pe)-[old_to:TO]->()
        DELETE old_from, old_to
        WITH pe, person, candidate
        MERGE (pe)-[:FROM]->(person)
        MERGE (pe)-[:TO]->(candidate)
        WITH pe, person, candidate
        MATCH (cl:Claim {claim_id: $claim_id})
        MERGE (cl)-[:ASSERTS]->(person)
        MERGE (cl)-[:ASSERTS]->(candidate)
        """,
        claim_id=row["claim_id"],
        edge_id=row["edge_id"],
        person_qid=person_qid,
        candidate_qid=candidate_qid,
        label=label,
        description=description,
        rel=rel,
    )


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


def fetch_for_backfill(session: Any) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (cl:Claim {source_agent: 'sfa_biographic'})
              -[:ASSERTS_EDGE]->(pe:ProposedEdge)
              -[:FROM]->(src),
              (pe)-[:TO]->(tgt)
        RETURN cl.claim_id AS claim_id,
               cl.subject_qid AS subject_qid,
               cl.authority_ids AS authority_ids,
               cl.description AS description,
               pe.relationship_type AS rel,
               src.qid AS from_qid,
               coalesce(src.label, src.qid) AS from_label,
               tgt.qid AS to_qid,
               coalesce(tgt.label, tgt.qid) AS to_label
        """,
    ).data()


def backfill_one(session: Any, row: dict[str, Any], *, dry_run: bool) -> bool:
    """Set description (and label when missing) from harvest metadata. Returns True if updated."""
    if row.get("description"):
        return False

    auth = _parse_authority_ids(row.get("authority_ids"))
    person_qid = auth.get("person_qid") or row.get("subject_qid") or ""
    candidate_qid = auth.get("candidate_qid") or ""
    if not candidate_qid:
        if row["from_qid"] == person_qid:
            candidate_qid = row["to_qid"]
        else:
            candidate_qid = row["from_qid"]

    if row["from_qid"] == person_qid:
        person_label, candidate_label = row["from_label"], row["to_label"]
    elif row["to_qid"] == person_qid:
        person_label, candidate_label = row["to_label"], row["from_label"]
    else:
        person_label = row.get("to_label") or person_qid
        candidate_label = row.get("from_label") or candidate_qid

    rel = row["rel"] or ""
    pred_pid = auth.get("pred_pid") or rel
    agent_is_person = agent_anchor_edge(rel)

    label = build_claim_label(
        person_label, candidate_label, rel, agent_is_person=agent_is_person
    )
    description = build_claim_description(
        person_label=person_label,
        person_qid=person_qid,
        candidate_label=candidate_label,
        candidate_qid=candidate_qid,
        relationship_type=rel,
        pred_pid=pred_pid,
        source="wikidata_backlink",
        agent_is_person=agent_is_person,
    )

    if dry_run:
        return True

    session.run(
        """
        MATCH (cl:Claim {claim_id: $claim_id})
        SET cl.description = $description,
            cl.label = $label,
            cl.text = $label
        """,
        claim_id=row["claim_id"],
        description=description,
        label=label,
    )
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Fix inverted biographic claim edge directions")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument(
        "--backfill-descriptions",
        action="store_true",
        default=None,
        help="Set description on claims missing it (default: on with --write)",
    )
    ap.add_argument(
        "--skip-direction",
        action="store_true",
        help="Only backfill descriptions (skip inverted edge repair)",
    )
    args = ap.parse_args()
    if not args.dry and not args.write:
        print("Specify --dry or --write")
        return 1
    if args.backfill_descriptions is None:
        args.backfill_descriptions = bool(args.write or args.skip_direction)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    stats = {"inverted_found": 0, "inverted_fixed": 0, "descriptions_backfilled": 0}
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            if not args.skip_direction:
                rows = fetch_inverted(session)
                stats["inverted_found"] = len(rows)
                print(f"Inverted agent-anchor claims: {len(rows)}")
                for row in rows[:5]:
                    label = build_claim_label(
                        row["tgt_label"],
                        row["src_label"],
                        row["rel"],
                        agent_is_person=True,
                    )
                    print(f"  {row['claim_id']}: {label[:90]}")
                if len(rows) > 5:
                    print(f"  ... and {len(rows) - 5} more")
                for row in rows:
                    repair_one(session, row, dry_run=args.dry)
                    stats["inverted_fixed"] += 1

            if args.backfill_descriptions or args.skip_direction:
                backfill_rows = fetch_for_backfill(session)
                missing = [r for r in backfill_rows if not r.get("description")]
                print(f"Claims missing description: {len(missing)} / {len(backfill_rows)}")
                for row in missing[:3]:
                    if backfill_one(session, row, dry_run=args.dry):
                        preview = build_claim_description(
                            person_label=row["from_label"],
                            person_qid=row["from_qid"],
                            candidate_label=row["to_label"],
                            candidate_qid=row["to_qid"],
                            relationship_type=row["rel"],
                            pred_pid=_parse_authority_ids(row.get("authority_ids")).get("pred_pid", ""),
                            source="wikidata_backlink",
                            agent_is_person=agent_anchor_edge(row["rel"]),
                        )
                        print(f"  {row['claim_id']}: {preview[:100]}...")
                if len(missing) > 3:
                    print(f"  ... and {len(missing) - 3} more")
                for row in missing:
                    if backfill_one(session, row, dry_run=args.dry):
                        stats["descriptions_backfilled"] += 1
    finally:
        driver.close()

    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
