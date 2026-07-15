#!/usr/bin/env python3
"""
Biographic familial reconciliation.

1. Dedupe CHILD_OF — one edge per (child, parent) QID pair
2. Resolve parent_type conflicts — DPRR FATHER_OF/MOTHER_OF is authoritative
3. Promote Wikidata biographic claims — fill gaps only; DPRR wins for elite persons

Usage:
  python -m scripts.agents.biographic.reconcile_familial --dry
  python -m scripts.agents.biographic.reconcile_familial --write
  python -m scripts.agents.biographic.reconcile_familial --write --dedup-only
  python -m scripts.agents.biographic.reconcile_familial --write --promote-only
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

FAMILIAL_CLAIM_RELS = frozenset(
    {
        "CHILD_OF",
        "PARENT_OF",
        "SIBLING_OF",
        "SPOUSE_OF",
        "HALF_SIBLING_OF",
        "STEPPARENT_OF",
    }
)


def _load_pair_sets(session: Any) -> tuple[set[tuple[str, str]], set[tuple[str, str]], set[tuple[str, str]]]:
    """Preload canonical child-parent pairs, DPRR-covered pairs, and spouse/sibling pairs."""
    canonical_child: set[tuple[str, str]] = set()
    for row in session.run(
        """
        MATCH (c:Person)-[:CHILD_OF]->(p)
        WHERE c.qid IS NOT NULL AND p.qid IS NOT NULL
        RETURN c.qid AS cq, p.qid AS pq
        UNION
        MATCH (p)-[:FATHER_OF|MOTHER_OF|PARENT_OF]->(c:Person)
        WHERE c.qid IS NOT NULL AND p.qid IS NOT NULL
        RETURN c.qid AS cq, p.qid AS pq
        """
    ):
        canonical_child.add((row["cq"], row["pq"]))

    dprr_child: set[tuple[str, str]] = set()
    for row in session.run(
        """
        MATCH (parent)-[r:FATHER_OF|MOTHER_OF]->(c:Person)
        WHERE c.qid IS NOT NULL AND parent.qid IS NOT NULL
          AND c.dprr_id IS NOT NULL
          AND coalesce(r.source, 'dprr') = 'dprr'
        RETURN c.qid AS cq, parent.qid AS pq
        """
    ):
        dprr_child.add((row["cq"], row["pq"]))

    undirected_pairs: set[tuple[str, str]] = set()
    for rel in ("SPOUSE_OF", "SIBLING_OF"):
        for row in session.run(
            f"""
            MATCH (a:Person)-[:{rel}]->(b:Person)
            WHERE a.qid IS NOT NULL AND b.qid IS NOT NULL
            RETURN a.qid AS aq, b.qid AS bq
            """
        ):
            pair = tuple(sorted((row["aq"], row["bq"])))
            undirected_pairs.add((rel, pair[0], pair[1]))

    return canonical_child, dprr_child, undirected_pairs


def _dprr_parent_type(session: Any, child_qid: str, parent_qid: str) -> str | None:
    row = session.run(
        """
        OPTIONAL MATCH (p {qid: $parent_qid})-[fo:FATHER_OF]->(c:Person {qid: $child_qid})
        WITH count(fo) > 0 AS is_father
        OPTIONAL MATCH (p2 {qid: $parent_qid})-[mo:MOTHER_OF]->(c2:Person {qid: $child_qid})
        RETURN is_father, count(mo) > 0 AS is_mother
        """,
        child_qid=child_qid,
        parent_qid=parent_qid,
    ).single()
    if not row:
        return None
    if row["is_father"]:
        return "father"
    if row["is_mother"]:
        return "mother"
    return None


def dedupe_child_of(session: Any, *, dry_run: bool) -> dict[str, int]:
    stats = {"groups": 0, "removed": 0, "kept": 0, "retyped": 0}
    groups = session.run(
        """
        MATCH (child:Person)-[r:CHILD_OF]->(parent)
        WHERE child.qid IS NOT NULL AND parent.qid IS NOT NULL
        WITH child.qid AS child_qid, parent.qid AS parent_qid,
             collect({eid: elementId(r), ptype: coalesce(r.parent_type, 'unknown')}) AS rels
        WHERE size(rels) > 1
        RETURN child_qid, parent_qid, rels
        """
    ).data()

    for group in groups:
        stats["groups"] += 1
        child_qid = group["child_qid"]
        parent_qid = group["parent_qid"]
        rels = group["rels"]
        ptypes = {r["ptype"] for r in rels if r["ptype"] != "unknown"}
        dprr_type = _dprr_parent_type(session, child_qid, parent_qid)
        has_father = session.run(
            """
            MATCH (p {qid: $parent_qid})-[:FATHER_OF]->(c:Person {qid: $child_qid})
            RETURN count(*) > 0 AS yes
            """,
            child_qid=child_qid,
            parent_qid=parent_qid,
        ).single()["yes"]
        has_mother = session.run(
            """
            MATCH (p {qid: $parent_qid})-[:MOTHER_OF]->(c:Person {qid: $child_qid})
            RETURN count(*) > 0 AS yes
            """,
            child_qid=child_qid,
            parent_qid=parent_qid,
        ).single()["yes"]
        if has_father and has_mother:
            keep_type = "father"
            stats["retyped"] += 1
        elif dprr_type:
            keep_type = dprr_type
        elif ptypes == {"mother"}:
            keep_type = "mother"
        elif "father" in ptypes:
            keep_type = "father"
        elif ptypes == {"father"} or not ptypes:
            keep_type = "father"
        else:
            keep_type = "father"
            stats["retyped"] += 1

        keeper_eid = None
        for rel in rels:
            if rel["ptype"] == keep_type:
                keeper_eid = rel["eid"]
                break
        if keeper_eid is None:
            keeper_eid = rels[0]["eid"]

        to_delete = [r["eid"] for r in rels if r["eid"] != keeper_eid]
        stats["kept"] += 1
        stats["removed"] += len(to_delete)

        if dry_run:
            continue

        session.run(
            """
            MATCH ()-[r:CHILD_OF]->()
            WHERE elementId(r) = $keeper_eid
            SET r.parent_type = $keep_type,
                r.source = coalesce(r.source, 'reconciled_dedup'),
                r.reconciled_at = datetime()
            """,
            keeper_eid=keeper_eid,
            keep_type=keep_type,
        )
        for eid in to_delete:
            session.run(
                "MATCH ()-[r:CHILD_OF]->() WHERE elementId(r) = $eid DELETE r",
                eid=eid,
            )

    return stats


def sync_child_of_from_dprr(session: Any, *, dry_run: bool) -> dict[str, int]:
    stats = {"father_synced": 0, "mother_synced": 0, "pairs_synced": 0}
    rows = session.run(
        """
        MATCH (parent)-[r:FATHER_OF]->(child:Person)
        WHERE child.qid IS NOT NULL AND parent.qid IS NOT NULL
          AND coalesce(r.source, 'dprr') = 'dprr'
        RETURN child.qid AS child_qid, parent.qid AS parent_qid, 'father' AS ptype
        UNION
        MATCH (parent)-[r:MOTHER_OF]->(child:Person)
        WHERE child.qid IS NOT NULL AND parent.qid IS NOT NULL
          AND coalesce(r.source, 'dprr') = 'dprr'
        RETURN child.qid AS child_qid, parent.qid AS parent_qid, 'mother' AS ptype
        """
    ).data()

    pair_types: dict[tuple[str, str], str] = {}
    for row in rows:
        key = (row["child_qid"], row["parent_qid"])
        ptype = row["ptype"]
        if key not in pair_types:
            pair_types[key] = ptype
        elif ptype == "father":
            pair_types[key] = "father"
        if ptype == "father":
            stats["father_synced"] += 1
        else:
            stats["mother_synced"] += 1

    stats["pairs_synced"] = len(pair_types)
    for (child_qid, parent_qid), ptype in pair_types.items():
        if dry_run:
            continue
        session.run(
            """
            MATCH (child:Person {qid: $child_qid})
            MATCH (parent {qid: $parent_qid})
            MERGE (child)-[co:CHILD_OF]->(parent)
            SET co.parent_type = $ptype,
                co.source = 'dprr_inverse',
                co.reconciled_at = datetime()
            """,
            child_qid=child_qid,
            parent_qid=parent_qid,
            ptype=ptype,
        )

    return stats


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


def _ensure_person(session: Any, qid: str, entity_id: str | None) -> None:
    session.run(
        """
        MERGE (e:Entity {qid: $qid})
        ON CREATE SET e.entity_id = coalesce($entity_id, 'person_' + toLower($qid)),
                      e.label = $qid,
                      e.entity_type = 'PERSON'
        SET e:Person,
            e.entity_id = coalesce(e.entity_id, $entity_id, 'person_' + toLower($qid)),
            e.entity_type = coalesce(e.entity_type, 'PERSON')
        """,
        qid=qid,
        entity_id=entity_id,
    )


def fetch_familial_claims(session: Any, *, limit: int | None) -> list[dict[str, Any]]:
    cypher = """
        MATCH (cl:Claim {source_agent: 'sfa_biographic'})
        WHERE cl.promoted = false
        MATCH (cl)-[:ASSERTS_EDGE]->(pe:ProposedEdge)
        WHERE pe.relationship_type IN $rels
        MATCH (pe)-[:FROM]->(src)
        MATCH (pe)-[:TO]->(tgt)
        RETURN cl.claim_id AS claim_id,
               cl.label AS label,
               cl.authority_ids AS authority_ids,
               pe.relationship_type AS rel,
               src.qid AS src_qid,
               src.entity_id AS src_entity_id,
               tgt.qid AS tgt_qid,
               tgt.entity_id AS tgt_entity_id,
               tgt.dprr_id AS tgt_dprr_id,
               src.dprr_id AS src_dprr_id
        ORDER BY cl.claim_id
    """
    params: dict[str, Any] = {"rels": list(FAMILIAL_CLAIM_RELS)}
    if limit:
        cypher += " LIMIT $limit"
        params["limit"] = limit
    return session.run(cypher, **params).data()


def promote_familial_claims(session: Any, *, dry_run: bool, limit: int | None) -> dict[str, int]:
    stats = {
        "processed": 0,
        "promoted": 0,
        "skipped_dprr": 0,
        "skipped_exists": 0,
        "skipped_non_person": 0,
        "skipped_unmapped": 0,
    }

    canonical_child, dprr_child, undirected_pairs = _load_pair_sets(session)
    claims = fetch_familial_claims(session, limit=limit)
    print(f"  Loaded {len(claims)} familial claims; {len(canonical_child)} canonical child-parent pairs")

    for row in claims:
        stats["processed"] += 1
        rel = row["rel"]
        claim_id = row["claim_id"]
        src_qid = row["src_qid"]
        tgt_qid = row["tgt_qid"]

        if not src_qid or not tgt_qid:
            stats["skipped_non_person"] += 1
            continue

        if rel in ("CHILD_OF", "PARENT_OF"):
            if rel == "CHILD_OF":
                child_qid, parent_qid = src_qid, tgt_qid
            else:
                child_qid, parent_qid = tgt_qid, src_qid

            pair = (child_qid, parent_qid)
            if pair in dprr_child:
                stats["skipped_dprr"] += 1
                if not dry_run:
                    _mark_claim_superseded(session, claim_id, "dprr_authoritative")
                continue

            if pair in canonical_child:
                stats["skipped_exists"] += 1
                if not dry_run:
                    _mark_claim_superseded(session, claim_id, "canonical_exists")
                continue

            ptype = _dprr_parent_type(session, child_qid, parent_qid)
            if not ptype:
                auth = _parse_authority_ids(row.get("authority_ids"))
                pid = auth.get("pred_pid", "")
                if pid == "P22":
                    ptype = "father"
                elif pid == "P25":
                    ptype = "mother"
                else:
                    ptype = "parent"

            stats["promoted"] += 1
            canonical_child.add(pair)
            if dry_run:
                continue

            _ensure_person(session, child_qid, row["src_entity_id"] if rel == "CHILD_OF" else row["tgt_entity_id"])
            _ensure_person(session, parent_qid, row["tgt_entity_id"] if rel == "CHILD_OF" else row["src_entity_id"])
            session.run(
                """
                MATCH (child:Person {qid: $child_qid})
                MATCH (parent {qid: $parent_qid})
                MERGE (child)-[r:CHILD_OF]->(parent)
                SET r.parent_type = $ptype,
                    r.source = 'wikidata_backlink',
                    r.promoted_from_claim_id = $claim_id,
                    r.reconciled_at = datetime()
                """,
                child_qid=child_qid,
                parent_qid=parent_qid,
                ptype=ptype,
                claim_id=claim_id,
            )
            _mark_claim_promoted(session, claim_id)
            continue

        if rel in ("SPOUSE_OF", "SIBLING_OF"):
            a_qid, b_qid = src_qid, tgt_qid
            pair_key = (rel, *sorted((a_qid, b_qid)))
            if pair_key in undirected_pairs:
                stats["skipped_exists"] += 1
                if not dry_run:
                    _mark_claim_superseded(session, claim_id, "canonical_exists")
                continue
            stats["promoted"] += 1
            undirected_pairs.add(pair_key)
            if dry_run:
                continue
            _ensure_person(session, a_qid, row["src_entity_id"])
            _ensure_person(session, b_qid, row["tgt_entity_id"])
            session.run(
                f"""
                MATCH (a:Person {{qid: $a_qid}})
                MATCH (b:Person {{qid: $b_qid}})
                MERGE (a)-[r:{rel}]->(b)
                SET r.source = coalesce(r.source, 'wikidata_backlink'),
                    r.promoted_from_claim_id = $claim_id,
                    r.reconciled_at = datetime()
                """,
                a_qid=a_qid,
                b_qid=b_qid,
                claim_id=claim_id,
            )
            _mark_claim_promoted(session, claim_id)
            continue

        stats["skipped_unmapped"] += 1

    return stats


def _mark_claim_promoted(session: Any, claim_id: str) -> None:
    session.run(
        """
        MATCH (cl:Claim {claim_id: $claim_id})
        SET cl.promoted = true,
            cl.status = 'validated',
            cl.promotion_date = $ts,
            cl.reconciliation_status = 'promoted_gap_fill'
        """,
        claim_id=claim_id,
        ts=datetime.utcnow().isoformat(),
    )


def _mark_claim_superseded(session: Any, claim_id: str, reason: str) -> None:
    session.run(
        """
        MATCH (cl:Claim {claim_id: $claim_id})
        SET cl.reconciliation_status = $reason,
            cl.reconciled_at = datetime()
        """,
        claim_id=claim_id,
        reason=reason,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Reconcile biographic familial edges and promote gap-filling claims")
    ap.add_argument("--dry", action="store_true", help="Preview changes")
    ap.add_argument("--write", action="store_true", help="Apply changes")
    ap.add_argument("--dedup-only", action="store_true")
    ap.add_argument("--promote-only", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="Limit claims processed in promote phase")
    args = ap.parse_args()

    if not args.dry and not args.write:
        print("Specify --dry or --write")
        return 1

    dry_run = args.dry
    run_dedup = not args.promote_only
    run_promote = not args.dedup_only

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    summary: dict[str, Any] = {"dry_run": dry_run}

    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            if run_dedup:
                print("Phase 1: sync CHILD_OF from DPRR FATHER_OF/MOTHER_OF")
                summary["dprr_sync"] = sync_child_of_from_dprr(session, dry_run=dry_run)
                print("Phase 2: dedupe CHILD_OF")
                summary["dedupe"] = dedupe_child_of(session, dry_run=dry_run)
            if run_promote:
                print("Phase 3: promote familial claims (gap-fill, DPRR precedence)")
                summary["promote"] = promote_familial_claims(session, dry_run=dry_run, limit=args.limit)
    finally:
        driver.close()

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
