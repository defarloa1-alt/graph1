#!/usr/bin/env python3
"""
Harvest Penetration Analysis

For SubjectConcepts that hit the 500-entity cap, shows what the max count
would be without the limit (accepted_before_node_budget from harvest reports).

Usage:
    python scripts/analysis/harvest_penetration_analysis.py
    python scripts/analysis/harvest_penetration_analysis.py --output output/analysis/harvest_penetration.json
"""
import argparse
import json
from pathlib import Path


def load_labels(anchors_path: Path) -> dict[str, str]:
    """QID -> label from canonical anchors."""
    with open(anchors_path, encoding="utf-8") as f:
        anchors = json.load(f)
    return {a["qid"]: a.get("label", a["qid"]) for a in anchors}


def main():
    parser = argparse.ArgumentParser(description="Harvest penetration analysis")
    parser.add_argument(
        "--harvest-dir",
        default="output/backlinks",
        help="Directory with *_report.json files",
    )
    parser.add_argument(
        "--anchors",
        default="output/subject_concepts/subject_concept_anchors_qid_canonical.json",
        help="Anchors file for QID->label mapping",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional: write JSON report",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    harvest_dir = project_root / args.harvest_dir
    anchors_path = project_root / args.anchors

    labels = load_labels(anchors_path) if anchors_path.exists() else {}

    rows = []
    for report_path in harvest_dir.glob("*_report.json"):
        with open(report_path, encoding="utf-8") as f:
            data = json.load(f)
        seed_qid = data.get("seed_qid")
        counts = data.get("counts", {})
        accepted = counts.get("accepted", 0)
        accepted_before = counts.get("accepted_before_node_budget", accepted)
        backlink_rows = counts.get("backlink_rows", 0)

        capped = accepted_before > accepted
        rows.append({
            "qid": seed_qid,
            "label": labels.get(seed_qid, seed_qid)[:60],
            "imported": accepted,
            "would_be": accepted_before,
            "backlink_rows": backlink_rows,
            "capped": capped,
            "left_behind": accepted_before - accepted if capped else 0,
        })

    rows.sort(key=lambda r: (-r["would_be"], r["qid"]))

    # Print table
    print("=" * 95)
    print("HARVEST PENETRATION (would-be counts without 500 cap)")
    print("=" * 95)
    print(f"{'QID':<12} {'Imported':>8} {'Would be':>10} {'Left behind':>12} {'Capped':>6}  Label")
    print("-" * 95)

    for r in rows:
        cap = "yes" if r["capped"] else ""
        print(f"{r['qid']:<12} {r['imported']:>8} {r['would_be']:>10} {r['left_behind']:>12} {cap:>6}  {r['label']}")

    capped_count = sum(1 for r in rows if r["capped"])
    total_left = sum(r["left_behind"] for r in rows if r["capped"])
    print("-" * 95)
    print(f"Capped anchors: {capped_count}  |  Total entities left behind: {total_left}")

    if args.output:
        out_path = project_root / args.output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"rows": rows, "capped_count": capped_count, "total_left_behind": total_left}, f, indent=2)
        print(f"\nReport written: {out_path}")


if __name__ == "__main__":
    main()
