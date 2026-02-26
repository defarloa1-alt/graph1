#!/usr/bin/env python3
"""
Full 61-Anchor Production Re-harvest

Runs harvest_all_anchors with production mode, class gating, and schema.
Uses anchor_to_property_allowlist where defined (Q182547, Q337547);
others use schema/default property allowlist.
Q4167836 (Wikimedia category) is in DEFAULT_P31_DENYLIST.
P6104, P5008, P6216 are in PROPERTY_DENYLIST.

Usage:
    python scripts/backbone/subject/run_full_61_production_reharvest.py
    python scripts/backbone/subject/run_full_61_production_reharvest.py --dry-run
    python scripts/backbone/subject/run_full_61_production_reharvest.py --resume
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANCHORS = ROOT / "output" / "subject_concepts" / "subject_concept_anchors_qid_canonical.json"
HARVEST_ALL = ROOT / "scripts" / "backbone" / "subject" / "harvest_all_anchors.py"
HARVESTER = ROOT / "scripts" / "tools" / "wikidata_backlink_harvest.py"
OUTPUT_DIR = ROOT / "output" / "backlinks"


def main():
    if not ANCHORS.exists():
        print(f"Error: Anchors file not found: {ANCHORS}")
        sys.exit(1)

    cmd = [
        sys.executable,
        str(HARVEST_ALL),
        "--anchors", str(ANCHORS),
        "--harvester", str(HARVESTER),
        "--output-dir", str(OUTPUT_DIR),
        "--mode", "production",
        "--max-sources", "200",
        "--max-new-nodes", "200",
        "--use-schema-relationship-properties",
        "--class-allowlist-mode", "schema",
    ]

    if "--dry-run" in sys.argv:
        cmd.append("--dry-run")
    if "--resume" in sys.argv:
        cmd.append("--resume")

    print("=" * 70)
    print("FULL 61-ANCHOR PRODUCTION RE-HARVEST")
    print("=" * 70)
    print(f"  Mode: production")
    print(f"  Class gating: schema")
    print(f"  P31 denylist: Q4167836 (Wikimedia category)")
    print(f"  Property denylist: P6104, P5008, P6216")
    print("=" * 70)

    result = subprocess.run(cmd, cwd=str(ROOT))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
