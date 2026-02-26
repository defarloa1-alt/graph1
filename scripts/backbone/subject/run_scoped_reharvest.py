#!/usr/bin/env python3
"""
Production Scoped Re-harvest for Allowlist Anchors

Re-harvests Q182547 and Q337547 with anchor_to_property_allowlist
(P31 only for Provinces; P140, P101, P361 for Public ritual).
Overwrites their reports; leaves harvest_run_summary.json unchanged
so cluster_assignment still has all 61 anchors.

Usage:
    python scripts/backbone/subject/run_scoped_reharvest.py
    python scripts/backbone/subject/run_scoped_reharvest.py --dry-run
    python scripts/backbone/subject/run_scoped_reharvest.py --cluster-assignment --write
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HARVESTER = ROOT / "scripts" / "tools" / "wikidata_backlink_harvest.py"
OUTPUT_DIR = ROOT / "output" / "backlinks"
SUMMARY = OUTPUT_DIR / "harvest_run_summary.json"

ALLOWLIST_ANCHORS = ["Q182547", "Q337547"]


def main():
    parser = argparse.ArgumentParser(description="Re-harvest allowlist anchors, optionally run cluster assignment")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only")
    parser.add_argument("--cluster-assignment", action="store_true", help="Run cluster_assignment after harvest")
    parser.add_argument("--write", action="store_true", help="Write MEMBER_OF edges to Neo4j (with --cluster-assignment)")
    parser.add_argument("--max-sources", type=int, default=200, help="Max sources per seed (default 200)")
    parser.add_argument("--max-nodes", type=int, default=200, help="Max new nodes per seed (default 200; Q182547 had 30 Pleiades dropped at 100)")
    args = parser.parse_args()

    if not HARVESTER.exists():
        print(f"Error: harvester not found: {HARVESTER}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SCOPED RE-HARVEST (Allowlist Anchors)")
    print("=" * 70)
    print(f"Anchors: {ALLOWLIST_ANCHORS}")
    print(f"  Q182547 (Provinces) -> P31 only")
    print(f"  Q337547 (Public ritual) -> P140, P101, P361")
    print(f"Output: {OUTPUT_DIR}")
    if args.dry_run:
        print("[DRY RUN]")
    print("=" * 70)

    for qid in ALLOWLIST_ANCHORS:
        report_path = OUTPUT_DIR / f"{qid}_report.json"
        cmd = [
            sys.executable,
            str(HARVESTER),
            "--seed-qid", qid,
            "--mode", "production",
            "--report-path", str(report_path),
            "--max-sources-per-seed", str(args.max_sources),
            "--max-new-nodes-per-seed", str(args.max_nodes),
        ]
        print(f"\n{qid}: {' '.join(cmd)}")
        if not args.dry_run:
            result = subprocess.run(cmd, cwd=str(ROOT))
            if result.returncode != 0:
                print(f"Harvest failed for {qid}", file=sys.stderr)
                sys.exit(1)
            print(f"  -> {report_path.name}")

    if args.cluster_assignment and not args.dry_run:
        cluster_script = ROOT / "scripts" / "backbone" / "subject" / "cluster_assignment.py"
        if not cluster_script.exists():
            print(f"Error: cluster_assignment not found: {cluster_script}", file=sys.stderr)
            sys.exit(1)

        if not SUMMARY.exists():
            print(f"Error: harvest_run_summary.json not found. Run full harvest first.", file=sys.stderr)
            sys.exit(1)

        cmd = [
            sys.executable,
            str(cluster_script),
            "--harvest-dir", str(OUTPUT_DIR),
            "--summary", str(SUMMARY),
            "--cypher",
        ]
        if args.write:
            cmd.append("--write")
        print(f"\nCluster assignment: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(ROOT))
        if result.returncode != 0:
            sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
