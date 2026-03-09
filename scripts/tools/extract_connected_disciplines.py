#!/usr/bin/env python3
"""Extract the 615 connected disciplines (parent in set + authority IDs)."""
import csv
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
INPUT = PROJECT / "Disciplines" / "disciplines_with_authority.csv"
OUTPUT = PROJECT / "Disciplines" / "disciplines_connected.csv"

rows = []
with open(INPUT, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)

qid_set = set(r["qid"] for r in rows)

# Find items whose P279 parent is also in the 970
connected_qids = set()
for r in rows:
    parents = [p.strip() for p in (r["subclass_of"] or "").split("|") if p.strip()]
    for p in parents:
        if p in qid_set and p != r["qid"]:
            connected_qids.add(r["qid"])
            break

# Also include items that ARE parents of connected items (root nodes of subtrees)
for r in rows:
    parents = [p.strip() for p in (r["subclass_of"] or "").split("|") if p.strip()]
    for p in parents:
        if p in qid_set and p != r["qid"]:
            connected_qids.add(p)  # the parent is also connected

connected_rows = [r for r in rows if r["qid"] in connected_qids]
connected_rows.sort(key=lambda r: r["label"].lower())

fieldnames = ["qid", "label", "subclass_of", "subclass_of_label", "lcsh_id", "fast_id", "lcc", "ddc"]
with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(connected_rows)

print(f"Wrote {len(connected_rows)} connected disciplines to {OUTPUT}")
