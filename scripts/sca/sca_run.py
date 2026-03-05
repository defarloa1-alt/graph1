#!/usr/bin/env python3
"""
SCA Run — traverse + persist in one command.

Runs sca_traversal_engine then sca_persist. Use for a full SCA cycle.

Usage:
  python scripts/sca/sca_run.py --qid Q17167
  python scripts/sca/sca_run.py --qid Q17167 --max-depth 3 --no-persist  # traverse only
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))


def main() -> int:
    ap = argparse.ArgumentParser(description="SCA: traverse + persist")
    ap.add_argument("--qid", required=True, help="Seed QID (e.g. Q17167)")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-backlinks", type=int, default=50)
    ap.add_argument("--max-types", type=int, default=20)
    ap.add_argument("--no-persist", action="store_true", help="Only traverse, do not persist to Neo4j")
    args = ap.parse_args()

    qid = args.qid.strip().upper()
    out_dir = _root / "output" / "sca"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{qid}_domain.json"

    # 1. Traverse
    cmd = [
        sys.executable,
        str(_root / "scripts" / "sca" / "sca_traversal_engine.py"),
        "--qid", qid,
        "--max-depth", str(args.max_depth),
        "--max-backlinks", str(args.max_backlinks),
        "--max-types", str(args.max_types),
        "-o", str(out_file),
    ]
    r = subprocess.run(cmd, cwd=str(_root))
    if r.returncode != 0:
        return r.returncode

    if args.no_persist:
        print("Skipping persist (--no-persist)")
        return 0

    # 2. Persist
    cmd2 = [
        sys.executable,
        str(_root / "scripts" / "sca" / "sca_persist.py"),
        "-i", str(out_file),
    ]
    r2 = subprocess.run(cmd2, cwd=str(_root))
    return r2.returncode


if __name__ == "__main__":
    sys.exit(main())
