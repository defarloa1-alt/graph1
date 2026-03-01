#!/usr/bin/env python3
"""
Build master discipline registry and map disciplines/majors to it.

Master key priority: lcsh_id > fast_id > ddc > lcc > gnd_id > aat_id > qid
Items sharing the same authority ID map to the same master.

Output:
  - output/master_discipline_registry.csv (canonical master list)
  - output/discipline_majors_mapped.csv (consolidated with master_id, master_label)

Usage:
  python scripts/backbone/subject/build_master_discipline_registry.py
"""

import argparse
import csv
from pathlib import Path

_PROJECT = Path(__file__).resolve().parents[3]

# Priority order for master key (first non-empty wins)
MASTER_KEY_COLS = ("lcsh_id", "fast_id", "ddc", "lcc", "gnd_id", "aat_id")


def _first_val(row: dict, col: str) -> str:
    v = (row.get(col) or "").strip()
    return v.split("|")[0].strip() if v else ""


def _master_key(row: dict) -> tuple[str, str]:
    """Return (master_id, master_id_type)."""
    for col in MASTER_KEY_COLS:
        v = _first_val(row, col)
        if v:
            return (v, col)
    return (row.get("qid", ""), "qid")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=_PROJECT / "output" / "discipline_majors_consolidated.csv")
    parser.add_argument("-o", "--output-dir", type=Path, default=_PROJECT / "output")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        print("Run: python scripts/backbone/subject/consolidate_discipline_majors.py")
        return

    rows = []
    with open(args.input, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("qid") or "").strip():
                rows.append(r)

    # Build master_id for each row
    master_to_items: dict[str, list[dict]] = {}
    for row in rows:
        mid, mtype = _master_key(row)
        row["master_id"] = mid
        row["master_id_type"] = mtype
        master_to_items.setdefault(mid, []).append(row)

    # Build master registry: one row per master
    masters = []
    for master_id, items in master_to_items.items():
        # Prefer label from discipline source; else first item
        labels = [r["label"] for r in items if r.get("source") == "discipline" and r.get("label")]
        if not labels:
            labels = [r["label"] for r in items if r.get("label")]
        master_label = labels[0] if labels else master_id
        master_type = items[0]["master_id_type"]
        masters.append({
            "master_id": master_id,
            "master_id_type": master_type,
            "master_label": master_label,
            "item_count": len(items),
            "discipline_count": sum(1 for r in items if r.get("source") == "discipline"),
            "major_count": sum(1 for r in items if r.get("source") == "major"),
        })
    masters.sort(key=lambda m: (m["master_label"], m["master_id"]))

    # Write master registry
    master_path = args.output_dir / "master_discipline_registry.csv"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with open(master_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["master_id", "master_id_type", "master_label", "item_count", "discipline_count", "major_count"])
        w.writeheader()
        w.writerows(masters)
    print(f"Wrote {master_path} ({len(masters)} masters)")

    # Add master_label to rows
    master_labels = {m["master_id"]: m["master_label"] for m in masters}
    for row in rows:
        row["master_label"] = master_labels.get(row["master_id"], row["label"])

    # Write mapped consolidated
    mapped_path = args.output_dir / "discipline_majors_mapped.csv"
    in_fieldnames = list(rows[0].keys()) if rows else []
    out_cols = ["qid", "label", "master_id", "master_id_type", "master_label", "source"] + [
        c for c in ("subclass_of", "subclass_of_label", "part_of", "part_of_label", "has_parts", "has_parts_label",
                   "fast_id", "gnd_id", "lcsh_id", "ddc", "aat_id", "babelnet_id", "kbpedia_id", "world_history_id", "lcc")
        if c in in_fieldnames
    ]
    with open(mapped_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r.get("master_label", ""), r.get("label", ""))))
    print(f"Wrote {mapped_path} ({len(rows)} items mapped to {len(masters)} masters)")

    # Summary
    by_type = {}
    for m in masters:
        t = m["master_id_type"]
        by_type[t] = by_type.get(t, 0) + 1
    print("\nMaster key types:")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")


if __name__ == "__main__":
    main()
