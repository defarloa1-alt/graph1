#!/usr/bin/env python3
"""
Consolidate discipline taxonomy and academic majors (with backbone IDs) into one list.

Merges:
  - discipline_taxonomy_backbone.csv (disciplines)
  - academic_majors_not_in_disciplines_backbone.csv (majors not in disciplines)

Output: discipline_majors_consolidated.csv with source column (discipline|major).

Usage:
  python scripts/backbone/subject/consolidate_discipline_majors.py
"""

import argparse
import csv
from pathlib import Path

_PROJECT = Path(__file__).resolve().parents[3]

DISCIPLINE_COLS = (
    "qid", "label", "subclass_of", "subclass_of_label", "part_of", "part_of_label",
    "has_parts", "has_parts_label", "fast_id", "gnd_id", "lcsh_id", "ddc", "aat_id",
    "babelnet_id", "kbpedia_id", "world_history_id", "lcc"
)
MAJOR_COLS = ("qid", "label", "fast_id", "gnd_id", "lcsh_id", "ddc", "aat_id", "lcc")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--disciplines", type=Path, default=_PROJECT / "output" / "discipline_taxonomy_backbone.csv")
    parser.add_argument("--majors", type=Path, default=_PROJECT / "output" / "academic_majors_not_in_disciplines_backbone.csv")
    parser.add_argument("-o", "--output", type=Path, default=_PROJECT / "output" / "discipline_majors_consolidated.csv")
    args = parser.parse_args()

    seen = set()
    rows = []

    # Load disciplines
    if args.disciplines.exists():
        with open(args.disciplines, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                qid = (r.get("qid") or "").strip()
                if qid and qid not in seen:
                    seen.add(qid)
                    row = {c: r.get(c, "") for c in DISCIPLINE_COLS}
                    row["source"] = "discipline"
                    rows.append(row)
        print(f"  Loaded {len(rows)} disciplines")

    # Load majors (not in disciplines)
    if args.majors.exists():
        added = 0
        with open(args.majors, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                qid = (r.get("qid") or "").strip()
                if qid and qid not in seen:
                    seen.add(qid)
                    added += 1
                    row = {c: "" for c in DISCIPLINE_COLS}
                    row["qid"] = qid
                    row["label"] = r.get("label", "")
                    for c in ("fast_id", "gnd_id", "lcsh_id", "ddc", "aat_id", "lcc"):
                        row[c] = r.get(c, "")
                    row["source"] = "major"
                    rows.append(row)
        print(f"  Added {added} majors")
    else:
        print(f"  Majors file not found: {args.majors}")

    rows.sort(key=lambda r: (r.get("label") or r.get("qid", "")))

    fieldnames = list(DISCIPLINE_COLS) + ["source"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"Consolidated {len(rows)} items -> {args.output}")


if __name__ == "__main__":
    main()
