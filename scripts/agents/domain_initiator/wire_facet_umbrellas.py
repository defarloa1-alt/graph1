#!/usr/bin/env python3
"""
Wire facet umbrella SubjectConcepts under SubjectDomain for a seed.

Usage:
  python scripts/agents/domain_initiator/wire_facet_umbrellas.py --seed Q17167 --dry-run
  python scripts/agents/domain_initiator/wire_facet_umbrellas.py --seed Q17167 --write
  python scripts/agents/domain_initiator/wire_facet_umbrellas.py \\
    --write-from output/di_proposals/Q17167_proposals_enriched.json --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "domain_initiator"))

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
from facet_umbrella import (
    collect_facet_keys,
    facet_umbrella_subject_id,
    fetch_training_facet_keys,
    wire_facet_hierarchy,
)
from neo4j import GraphDatabase
from proposal_backbone import load_proposals_document, normalize_proposal_for_write


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire facet umbrella hierarchy under SubjectDomain")
    ap.add_argument("--seed", default="Q17167")
    ap.add_argument("--seed-label", default="Roman Republic")
    ap.add_argument("--write-from", type=Path, default=None)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    seed_qid = args.seed.strip().upper()
    decompositions: list[dict] = []
    seed_label = args.seed_label

    if args.write_from:
        doc = load_proposals_document(args.write_from)
        seed_qid = doc.get("seed_qid", seed_qid)
        seed_label = doc.get("seed_label", seed_label)
        decompositions = [
            normalize_proposal_for_write(p)
            for p in doc.get("proposals", [])
            if p.get("status") == "approved"
        ]
    else:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                rows = session.run(
                    """
                    MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: $seed_qid})
                    RETURN sc.subject_id AS subject_id, sc.source_facet AS source_facet,
                           sc.scope_key AS scope_key
                    ORDER BY sc.subject_id
                    """,
                    seed_qid=seed_qid,
                )
                decompositions = [dict(r) for r in rows]
        finally:
            driver.close()

    if not decompositions:
        print(f"No approved decomposition SubjectConcepts for {seed_qid}")
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            training_facets = fetch_training_facet_keys(session, seed_qid)
            facet_keys = collect_facet_keys(decompositions, training_facets)
            print(f"Facet umbrellas: {len(facet_keys)}")
            for fk in facet_keys:
                print(f"  {facet_umbrella_subject_id(seed_qid, fk)}  ({fk})")
            print(f"Decompositions to rewire: {len(decompositions)}")

            stats = wire_facet_hierarchy(
                session,
                seed_qid,
                seed_label,
                facet_keys,
                decompositions,
                dry_run=args.dry_run or not args.write,
            )
    finally:
        driver.close()

    if stats.get("error"):
        print(f"ERROR: {stats['error']}")
        return 1

    prefix = "[DRY RUN] " if (args.dry_run or not args.write) else ""
    print(f"\n{prefix}Facet hierarchy wiring complete")
    print(json.dumps(stats, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
