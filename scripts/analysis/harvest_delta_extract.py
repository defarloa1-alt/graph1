#!/usr/bin/env python3
"""
Harvest Delta Extract

Extracts the entities dropped by the node budget cap (500) from harvest reports.
For each capped anchor, outputs the QIDs and labels of entities that would have
been accepted without the limit.

Usage:
    python scripts/analysis/harvest_delta_extract.py
    python scripts/analysis/harvest_delta_extract.py --output output/analysis/harvest_deltas.json
    python scripts/analysis/harvest_delta_extract.py --output output/analysis/harvest_deltas.json --csv output/analysis/harvest_deltas.csv
"""
import argparse
import csv
import json
from pathlib import Path


def load_labels(anchors_path: Path) -> dict[str, str]:
    """QID -> label from canonical anchors."""
    if not anchors_path.exists():
        return {}
    with open(anchors_path, encoding="utf-8") as f:
        anchors = json.load(f)
    if isinstance(anchors, dict) and "anchors" in anchors:
        anchors = anchors["anchors"]
    return {a["qid"]: a.get("label", a["qid"]) for a in anchors if a.get("qid")}


def main():
    parser = argparse.ArgumentParser(description="Extract delta entities (dropped by 500 cap)")
    parser.add_argument(
        "--harvest-dir",
        default="output/backlinks",
        help="Directory with *_report.json files",
    )
    parser.add_argument(
        "--anchors",
        default="output/subject_concepts/subject_concept_anchors_qid_canonical.json",
        help="Anchors file for seed QID->label mapping",
    )
    parser.add_argument(
        "--output",
        default="output/analysis/harvest_deltas.json",
        help="Output JSON path (default: output/analysis/harvest_deltas.json)",
    )
    parser.add_argument(
        "--csv",
        default=None,
        help="Optional: also write flat CSV (seed_qid, seed_label, delta_qid, delta_label, backlink_hits)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    harvest_dir = project_root / args.harvest_dir
    anchors_path = project_root / args.anchors

    labels = load_labels(anchors_path)

    deltas_by_anchor = []
    total_delta_count = 0

    for report_path in sorted(harvest_dir.glob("*_report.json")):
        with open(report_path, encoding="utf-8") as f:
            data = json.load(f)

        seed_qid = data.get("seed_qid")
        rejected = data.get("rejected", [])
        delta_rows = [r for r in rejected if r.get("reason") == "node_budget_exceeded"]

        if not delta_rows:
            continue

        delta_entities = [
            {
                "qid": r["qid"],
                "label": r.get("label", r["qid"]),
                "backlink_hits": r.get("backlink_hits", 0),
            }
            for r in delta_rows
        ]
        delta_qids = [e["qid"] for e in delta_entities]

        deltas_by_anchor.append({
            "seed_qid": seed_qid,
            "seed_label": labels.get(seed_qid, seed_qid),
            "delta_count": len(delta_entities),
            "delta_qids": delta_qids,
            "delta_entities": delta_entities,
        })
        total_delta_count += len(delta_entities)

    # Sort by delta count descending
    deltas_by_anchor.sort(key=lambda x: x["delta_count"], reverse=True)

    # Write JSON
    out_path = project_root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "summary": {
            "capped_anchors": len(deltas_by_anchor),
            "total_delta_entities": total_delta_count,
        },
        "deltas_by_anchor": deltas_by_anchor,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote {out_path} ({len(deltas_by_anchor)} anchors, {total_delta_count} delta entities)")

    # Write CSV if requested
    if args.csv:
        csv_path = project_root / args.csv
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["seed_qid", "seed_label", "delta_qid", "delta_label", "backlink_hits"])
            for anchor in deltas_by_anchor:
                for e in anchor["delta_entities"]:
                    w.writerow([
                        anchor["seed_qid"],
                        anchor["seed_label"],
                        e["qid"],
                        e["label"],
                        e["backlink_hits"],
                    ])
        print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
