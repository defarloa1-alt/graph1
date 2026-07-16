#!/usr/bin/env python3
"""
Backfill agent provenance + bibliography on existing di_proposal SubjectConcepts.

Reads the enriched review JSON (same shape as Review Queue) and wires:
  - proposed_by, scholarly_overview
  - (SubjectConcept)-[:PROPOSED_BY]->(Agent)
  - (SubjectConcept)-[:HAS_BIBLIO {rank}]->(CorpusWork)

Usage:
  python scripts/agents/domain_initiator/backfill_proposal_provenance.py --dry-run
  python scripts/agents/domain_initiator/backfill_proposal_provenance.py --write
  python scripts/agents/domain_initiator/backfill_proposal_provenance.py --write --status approved
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

from proposal_provenance import write_proposal_provenance  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill SC agent provenance + HAS_BIBLIO")
    ap.add_argument("--seed", default="Q17167")
    ap.add_argument(
        "--json",
        type=Path,
        default=ROOT / "output" / "di_proposals" / "Q17167_proposals_enriched.json",
    )
    ap.add_argument("--status", default="approved", help="Only proposals with this status")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.json.exists():
        print(f"Not found: {args.json}")
        return 1

    with open(args.json, encoding="utf-8") as f:
        doc = json.load(f)

    seed_qid = doc.get("seed_qid", args.seed).upper()
    targets = [
        p
        for p in doc.get("proposals", [])
        if p.get("proposal_type") == "decomposition"
        and (not args.status or p.get("status") == args.status)
    ]

    print(f"Backfill {len(targets)} proposals from {args.json.name} (status={args.status})")

    if args.dry_run or not args.write:
        works = sum(len(p.get("supporting_works") or []) for p in targets)
        print(f"[DRY RUN] Would wire PROPOSED_BY on {len(targets)} SCs, {works} HAS_BIBLIO edges")
        return 0

    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD  # noqa: E402
    from neo4j import GraphDatabase  # noqa: E402

    stats: dict = {"proposed_by": 0, "has_biblio": 0}
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            for p in targets:
                if not p.get("subject_id"):
                    continue
                write_proposal_provenance(session, p, seed_qid=seed_qid, stats=stats)
    finally:
        driver.close()

    print(f"Done. PROPOSED_BY={stats['proposed_by']}  HAS_BIBLIO={stats['has_biblio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
