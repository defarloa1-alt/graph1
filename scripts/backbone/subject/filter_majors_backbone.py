#!/usr/bin/env python3
"""
Filter academic_majors_not_in_disciplines to items with federation/authority IDs.

Keeps rows that have at least one of: fast_id, lcsh_id, ddc, lcc, gnd_id, aat_id.

Usage:
  python scripts/backbone/subject/filter_majors_backbone.py
"""

import argparse
import csv
from pathlib import Path

BACKBONE_COLS = ("fast_id", "lcsh_id", "ddc", "lcc", "gnd_id", "aat_id")


def main():
    p = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=p / "output" / "academic_majors_not_in_disciplines.csv")
    parser.add_argument("-o", "--output", type=Path, default=p / "output" / "academic_majors_not_in_disciplines_backbone.csv")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        print("Run: python scripts/backbone/subject/fetch_academic_majors.py")
        return

    with open(args.input, encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
        fieldnames = r.fieldnames

    kept = [row for row in rows if any((row.get(col) or "").strip() for col in BACKBONE_COLS)]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(kept, key=lambda r: (r.get("label") or r.get("qid", ""))))

    print(f"Kept {len(kept)} / {len(rows)} majors with federation/authority IDs")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
