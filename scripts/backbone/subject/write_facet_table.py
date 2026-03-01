#!/usr/bin/env python3
"""
Generate facet weights markdown table and CSV from subject_characterization_results.json.

For subclass-only runs: outputs Subclass | Label | Parent class | Parent label | facet columns.
Section headers include group label (e.g. ## DG21-190 — Ancient Rome (General)).

Usage:
  python scripts/backbone/subject/write_facet_table.py
  python scripts/backbone/subject/write_facet_table.py --input path/to/results.json --output path/to/table.md --csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path

_PROJECT = Path(__file__).resolve().parents[3]
DEFAULT_LCC = _PROJECT / "output" / "nodes" / "lcc_roman_republic.csv"
if str(_PROJECT) not in sys.path:
    sys.path.insert(0, str(_PROJECT))

FACET_ABBREV = {
    "ARCHAEOLOGICAL": "ARCH", "ARTISTIC": "ARTI", "BIOGRAPHIC": "BIOG",
    "COMMUNICATION": "COMM", "CULTURAL": "CULT", "DEMOGRAPHIC": "DEMO",
    "DIPLOMATIC": "DIPL", "ECONOMIC": "ECON", "ENVIRONMENTAL": "ENVI",
    "GEOGRAPHIC": "GEOG", "INTELLECTUAL": "INTE", "LINGUISTIC": "LING",
    "MILITARY": "MILI", "POLITICAL": "POLI", "RELIGIOUS": "RELI",
    "SCIENTIFIC": "SCIE", "SOCIAL": "SOCI", "TECHNOLOGICAL": "TECH",
}

FACET_ORDER = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION", "CULTURAL",
    "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC", "ENVIRONMENTAL", "GEOGRAPHIC",
    "INTELLECTUAL", "LINGUISTIC", "MILITARY", "POLITICAL", "RELIGIOUS",
    "SCIENTIFIC", "SOCIAL", "TECHNOLOGICAL",
]


def main():
    parser = argparse.ArgumentParser(description="Write facet weights table from characterization results")
    parser.add_argument("--input", type=Path,
        default=_PROJECT / "output" / "subject_concepts" / "subject_characterization_results.json",
        help="Path to subject_characterization_results.json")
    parser.add_argument("--output", type=Path,
        default=None,
        help="Output path (default: facet_weights_table_subclass.md when subclass_only, else facet_weights_table.md)")
    parser.add_argument("--subclass-only", action="store_true", default=None,
        help="Force subclass table (Parent class column). Default: infer from JSON subclass_only")
    parser.add_argument("--csv", action="store_true", help="Also write CSV output (default for subclass)")
    parser.add_argument("--lcc-csv", type=Path, default=None,
        help="LCC CSV for parent labels (default: output/nodes/lcc_roman_republic.csv or from source)")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    contexts = {c["identifier"]: c for c in data.get("contexts", [])}
    subclass_only = args.subclass_only if args.subclass_only is not None else data.get("subclass_only", False)

    # Load parent labels from LCC CSV (id -> label for ranges like DG11-16, DG21-190)
    parent_labels = {}
    lcc_path = args.lcc_csv or DEFAULT_LCC
    if lcc_path.exists():
        with open(lcc_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                parent_labels[r["id"]] = r.get("label", "")

    if not results:
        print("No results to write.", file=sys.stderr)
        sys.exit(1)

    # Build weight map per result; handle both {"facet": "X", "weight": n} and alternate keys
    def get_weights(r):
        w = {}
        for f in r.get("facets", []):
            if isinstance(f, dict):
                facet = f.get("facet")
                weight = f.get("weight", f.get("score", 0.0))
                if facet:
                    w[facet] = weight
        return w

    abbrevs = [FACET_ABBREV.get(f, f[:4]) for f in FACET_ORDER]

    if subclass_only:
        # Subclass table: Subclass | Label | Parent class | Parent label | ARCH | ARTI | ...
        cols = ["Subclass", "Label", "Parent class", "Parent label"] + abbrevs
        rows = []
        for r in results:
            ident = r.get("identifier", "")
            label = (contexts.get(ident) or {}).get("lcc_label", r.get("label", ident))
            parent = r.get("parent_class", "")
            parent_label = parent_labels.get(parent, parent)
            w = get_weights(r)
            vals = [ident, label, parent, parent_label]
            for facet in FACET_ORDER:
                vals.append(w.get(facet, 0.0))
            rows.append(vals)
        out_path = args.output or (_PROJECT / "output" / "subject_concepts" / "facet_weights_table_subclass.md")
    else:
        # Class table: DG # | Label | ARCH | ARTI | ...
        cols = ["DG #", "Label"] + abbrevs
        rows = []
        for r in results:
            ident = r.get("identifier", "")
            label = (contexts.get(ident) or {}).get("lcc_label", r.get("label", ident))
            w = get_weights(r)
            vals = [ident, label]
            for facet in FACET_ORDER:
                vals.append(w.get(facet, 0.0))
            rows.append(vals)
        out_path = args.output or (_PROJECT / "output" / "subject_concepts" / "facet_weights_table.md")

    # Format table
    def fmt_weight(v):
        if isinstance(v, float):
            return f"{v:.1f}" if v != int(v) else f"{int(v):.1f}"
        return str(v)

    n_facet = len(abbrevs)
    n_meta = len(cols) - n_facet  # Subclass, Label, [Parent class]

    lines = []
    lines.append("# Subject Concept Facet Weights (Subclass Level)" if subclass_only else "# Subject Concept Facet Weights")
    lines.append("")
    lines.append("*Weights 0.0–1.0. Facets: ARCH, ARTI, BIOG, COMM, CULT, DEMO, DIPL, ECON, ENVI, GEOG, INTE, LING, MILI, POLI, RELI, SCIE, SOCI, TECH*")
    lines.append("")

    # Alignment: left for meta cols, right for facet weights
    align = "|".join([":---"] * n_meta + ["---:"] * n_facet)

    if subclass_only:
        # Group by parent class; each parent gets its own table with Parent class + Parent label in each row
        by_parent = {}
        for row in rows:
            parent = row[2]  # Parent class
            by_parent.setdefault(parent, []).append(row)

        sub_cols = ["Subclass", "Label", "Parent class", "Parent label"] + abbrevs
        sub_align = "|".join([":---"] * 4 + ["---:"] * n_facet)

        for parent in sorted(by_parent.keys()):
            parent_rows = by_parent[parent]
            parent_label = parent_labels.get(parent, "")
            header = f"## {parent} — {parent_label}" if parent_label else f"## {parent}"
            lines.append(header)
            lines.append("")
            lines.append("| " + " | ".join(sub_cols) + " |")
            lines.append("|" + sub_align + "|")
            for row in parent_rows:
                meta = [str(row[0]), str(row[1]), str(row[2]), str(row[3])]
                weights = [fmt_weight(x) for x in row[n_meta:]]
                lines.append("| " + " | ".join(meta + weights) + " |")
            lines.append("")
    else:
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("|" + align + "|")
        for row in rows:
            meta = [str(x) for x in row[:n_meta]]
            weights = [fmt_weight(x) for x in row[n_meta:]]
            lines.append("| " + " | ".join(meta + weights) + " |")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {out_path} ({len(rows)} rows)")

    if args.csv or subclass_only:
        csv_path = out_path.with_suffix(".csv")
        csv_cols = cols if subclass_only else ["DG #", "Label"] + abbrevs
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(csv_cols)
            for row in rows:
                w.writerow([str(x) for x in row])
        print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
