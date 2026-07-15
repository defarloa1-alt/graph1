#!/usr/bin/env python3
"""
Filter and sync SubjectDomain USES_TYPE edges.

SCA traversal discovers many Wikidata types via global backlink expansion
(Chinese dynasty, German Confederation states, etc.). Only seed-asserted
P31/P279 types belong on SubjectDomain -[:USES_TYPE]-> WikidataType.

Usage:
  python scripts/sca/sync_subject_domain_types.py --seed Q17167
  python scripts/sca/sync_subject_domain_types.py --seed Q17167 --from-json output/sca/Q17167_domain.json
  python scripts/sca/sync_subject_domain_types.py --seed Q17167 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "scripts"))
sys.path.insert(0, str(_root / "scripts" / "sca"))


def domain_types_from_payload(data: dict) -> list[dict]:
    """Return only types that should be wired as USES_TYPE."""
    types = data.get("types") or []
    filtered = [
        t for t in types
        if t.get("from_seed") or t.get("source") in ("P31", "P279")
    ]
    if filtered:
        return filtered
    # Legacy JSON without from_seed: depth-1 seed assertions only
    return [t for t in types if t.get("depth", 99) <= 1 and t.get("source") in ("P31", "P279")]


def fetch_seed_types(seed_qid: str) -> list[dict]:
    from sca_traversal_engine import get_p31_p279

    p31, p279 = get_p31_p279(seed_qid)
    out: list[dict] = []
    seen: set[str] = set()
    for qid, label in p31 + p279:
        if qid in seen:
            continue
        seen.add(qid)
        out.append({
            "qid": qid,
            "label": label,
            "depth": 1,
            "source": "P31" if (qid, label) in p31 else "P279",
            "from_seed": True,
        })
    return out


def get_driver():
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def sync_types(
    seed_qid: str,
    types: list[dict],
    *,
    dry_run: bool = False,
) -> dict:
    keep_qids = sorted({t["qid"] for t in types if t.get("qid")})
    stats = {"keep": len(keep_qids), "removed": 0, "added": 0, "kept_labels": []}

    if dry_run:
        driver = get_driver()
        try:
            with driver.session() as session:
                rows = session.run(
                    """
                    MATCH (d:SubjectDomain {seed_qid: $seed_qid})-[r:USES_TYPE]->(w:WikidataType)
                    RETURN w.qid AS qid, w.label AS label
                    ORDER BY w.label
                    """,
                    seed_qid=seed_qid,
                )
                current = [dict(r) for r in rows]
        finally:
            driver.close()
        stats["current"] = current
        stats["removed"] = len([r for r in current if r["qid"] not in keep_qids])
        stats["added"] = len([q for q in keep_qids if q not in {r["qid"] for r in current}])
        stats["kept_labels"] = [t.get("label", q) for t in types for q in [t.get("qid")] if q in keep_qids]
        return stats

    driver = get_driver()
    try:
        with driver.session() as session:
            removed = session.run(
                """
                MATCH (d:SubjectDomain {seed_qid: $seed_qid})-[r:USES_TYPE]->(w:WikidataType)
                WHERE NOT w.qid IN $keep_qids
                DELETE r
                RETURN count(*) AS deleted
                """,
                seed_qid=seed_qid,
                keep_qids=keep_qids,
            ).single()
            stats["removed"] = removed["deleted"] if removed else 0

            for t in types:
                qid = t.get("qid")
                if not qid:
                    continue
                session.run(
                    """
                    MERGE (w:WikidataType {qid: $qid})
                    SET w.label = $label,
                        w.tier = coalesce(w.tier, 'primary'),
                        w.depth = coalesce(w.depth, $depth),
                        w.updated_by = 'sync_subject_domain_types'
                    WITH w
                    MATCH (d:SubjectDomain {seed_qid: $seed_qid})
                    MERGE (d)-[:USES_TYPE]->(w)
                    """,
                    qid=qid,
                    label=t.get("label", qid),
                    depth=int(t.get("depth") or 1),
                    seed_qid=seed_qid,
                )
                stats["added"] += 1
                stats["kept_labels"].append(t.get("label", qid))

            session.run(
                """
                MATCH (d:SubjectDomain {seed_qid: $seed_qid})
                SET d.types_count = $types_count,
                    d.updated_by = 'sync_subject_domain_types'
                """,
                seed_qid=seed_qid,
                types_count=len(keep_qids),
            )
    finally:
        driver.close()

    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync SubjectDomain USES_TYPE to seed types only")
    ap.add_argument("--seed", default="Q17167")
    ap.add_argument("--from-json", type=Path, default=None, help="Optional SCA domain JSON")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    seed_qid = args.seed.strip().upper()
    if args.from_json:
        data = json.loads(args.from_json.read_text(encoding="utf-8"))
        types = domain_types_from_payload(data)
        if not types:
            print(f"No domain types in {args.from_json}; fetching seed P31/P279 from Wikidata")
            types = fetch_seed_types(seed_qid)
    else:
        types = fetch_seed_types(seed_qid)

    print(f"Seed {seed_qid}: {len(types)} domain types to keep")
    for t in types:
        print(f"  {t.get('qid')}  {t.get('label')}  ({t.get('source', '?')})")

    stats = sync_types(seed_qid, types, dry_run=args.dry_run)
    if args.dry_run:
        print(f"\n[DRY RUN] would remove {stats['removed']}, ensure {stats['keep']} types")
        if stats.get("current"):
            junk = [r for r in stats["current"] if r["qid"] not in {t["qid"] for t in types}]
            if junk:
                print("\nJunk to remove:")
                for r in junk:
                    print(f"  {r['qid']}  {r['label']}")
    else:
        print(f"\nRemoved {stats['removed']} junk USES_TYPE edges; synced {stats['keep']} seed types")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
