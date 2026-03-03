#!/usr/bin/env python3
"""
Backfill ADR-007 four-label schema for existing Entity nodes.

Targets Entity nodes with dprr_id or label matching DPRR format (e.g. POMP1976 Cn. Pompeius...).
Derives label_latin, label_sort from parse; sets label_dprr; updates label to tria nomina.

Wikidata-only persons (no dprr_id, label not DPRR format) are skipped.

Usage:
  python scripts/maintenance/backfill_person_four_labels.py           # dry-run
  python scripts/maintenance/backfill_person_four_labels.py --execute # write to graph
  python scripts/maintenance/backfill_person_four_labels.py --limit 500
"""
import argparse
import re
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

_federation = _root / "scripts" / "federation"
sys.path.insert(0, str(_federation))
try:
    from dprr_layer1 import parse_dprr_label, derive_label_latin, derive_label_sort
except ImportError:
    parse_dprr_label = derive_label_latin = derive_label_sort = None

from neo4j import GraphDatabase
import os


def _is_dprr_format(label: str) -> bool:
    """True if label looks like DPRR string (e.g. POMP1976 Cn. Pompeius...)."""
    if not label or not isinstance(label, str):
        return False
    tokens = label.strip().split()
    if len(tokens) < 2:
        return False
    first = tokens[0]
    return len(first) >= 5 and first[:4].isalpha() and first[4:].isdigit()


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill ADR-007 four-label schema for Entity persons")
    ap.add_argument("--execute", action="store_true", help="Write to graph (default: dry-run)")
    ap.add_argument("--limit", type=int, default=0, help="Max entities to update (0 = all)")
    args = ap.parse_args()

    if not parse_dprr_label or not derive_label_latin or not derive_label_sort:
        print("Error: dprr_layer1 (parse_dprr_label, derive_label_latin, derive_label_sort) required")
        return 1

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    with driver.session(database=db) as session:
        # Find Entity nodes with dprr_id or label matching DPRR format
        r = session.run("""
            MATCH (e:Entity)
            WHERE e.entity_type = 'PERSON' OR e.dprr_id IS NOT NULL OR e.dprr_uri IS NOT NULL
            RETURN e.qid AS qid, e.dprr_id AS dprr_id, e.dprr_uri AS dprr_uri,
                   e.label AS label, e.label_dprr AS label_dprr, e.label_latin AS label_latin, e.label_sort AS label_sort,
                   elementId(e) AS elem_id
            ORDER BY e.dprr_id, e.qid
        """)
        rows = list(r)

    # Filter to those needing backfill: dprr_id present and (label_dprr missing or label looks like DPRR)
    candidates = []
    for row in rows:
        label = row.get("label") or ""
        label_dprr = row.get("label_dprr")
        label_latin = row.get("label_latin")
        label_sort = row.get("label_sort")
        dprr_id = row.get("dprr_id")
        dprr_uri = row.get("dprr_uri")

        # Skip if already fully populated
        if label_dprr and label_latin and label_sort:
            continue

        # Need DPRR string to parse
        dprr_str = label_dprr if label_dprr else (label if _is_dprr_format(label) else None)

        # Skip if no DPRR string and no dprr_id (Wikidata-only)
        if not dprr_str and not dprr_id:
            continue

        # If we have dprr_id but label is DPRR format, we can derive
        if dprr_str:
            parsed = parse_dprr_label(dprr_str)
            lat = derive_label_latin(parsed)
            srt = derive_label_sort(parsed)
            if lat or srt:
                candidates.append({
                    "qid": row.get("qid"),
                    "dprr_id": dprr_id,
                    "dprr_uri": dprr_uri,
                    "label_dprr": dprr_str,
                    "label_latin": lat or label_latin,
                    "label_sort": srt or label_sort,
                    "label": lat if _is_dprr_format(label) else label,  # Use tria nomina as display when label was DPRR
                    "elem_id": row.get("elem_id"),
                })
        elif dprr_id:
            # Has dprr_id but label is not DPRR format - could be from graph with old label. Skip derivation.
            pass

    if args.limit:
        candidates = candidates[: args.limit]

    print(f"Backfill ADR-007 four-label schema")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")
    if candidates and not args.execute:
        print(f"  Sample: {candidates[0].get('label_dprr', '')[:50]}... -> label_latin={candidates[0].get('label_latin')}")

    if not args.execute or not candidates:
        driver.close()
        return 0

    updated = 0
    with driver.session(database=db) as session:
        for c in candidates:
            qid = c.get("qid")
            dprr_id = c.get("dprr_id")
            dprr_uri = c.get("dprr_uri")
            if qid:
                session.run("""
                    MATCH (e:Entity {qid: $qid})
                    SET e.label = $label
                    SET e.label_dprr = $label_dprr
                    SET e.label_latin = $label_latin
                    SET e.label_sort = $label_sort
                """, qid=qid, label=c["label"], label_dprr=c["label_dprr"],
                     label_latin=c["label_latin"] or None, label_sort=c["label_sort"] or None)
            elif dprr_uri:
                session.run("""
                    MATCH (e:Entity {dprr_uri: $dprr_uri})
                    SET e.label = $label
                    SET e.label_dprr = $label_dprr
                    SET e.label_latin = $label_latin
                    SET e.label_sort = $label_sort
                """, dprr_uri=dprr_uri, label=c["label"], label_dprr=c["label_dprr"],
                     label_latin=c["label_latin"] or None, label_sort=c["label_sort"] or None)
            elif dprr_id:
                session.run("""
                    MATCH (e:Entity {dprr_id: $dprr_id})
                    SET e.label = $label
                    SET e.label_dprr = $label_dprr
                    SET e.label_latin = $label_latin
                    SET e.label_sort = $label_sort
                """, dprr_id=str(dprr_id), label=c["label"], label_dprr=c["label_dprr"],
                     label_latin=c["label_latin"] or None, label_sort=c["label_sort"] or None)
            else:
                continue
            updated += 1

    print(f"Updated {updated} Entity nodes.")
    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
