#!/usr/bin/env python3
"""
Roman Republic Backlinks vs Canonical Schema Distribution

Maps all backlink entities (from harvest reports) to canonical entity types
from chrystallum_schema.json. Reports:
- How many backlinks match Human, Battle, Place, etc. (on-schema)
- How many are off-schema (P31 not in canonical types)
- Per-anchor breakdown for anchor quality checks

Usage:
    python scripts/analysis/backlink_canonical_distribution.py
    python scripts/analysis/backlink_canonical_distribution.py --domain Q17167 --output output/analysis/backlink_canonical_distribution.json
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--harvest-dir",
        default="output/backlinks",
        help="Directory with *_report.json files",
    )
    parser.add_argument(
        "--schema",
        default="JSON/chrystallum_schema.json",
        help="Schema path for canonical types",
    )
    parser.add_argument(
        "--domain-qid",
        default="Q17167",
        help="Domain QID to filter (Q17167 = Roman Republic); use empty to include all",
    )
    parser.add_argument(
        "--output",
        default="output/analysis/backlink_canonical_distribution.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    harvest_dir = root / args.harvest_dir

    # Load canonical schema
    schema_path = root / args.schema
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    types = data.get("entities", {}).get("types", [])
    qid_to_schema: dict[str, dict] = {
        t["wikidata_qid"]: {"type": t["type"], "category": t["category"]}
        for t in types
        if t.get("wikidata_qid")
    }

    # Load anchor labels (for per-anchor report)
    anchors_path = root / "output/subject_concepts/subject_concept_anchors_qid_canonical.json"
    anchor_labels: dict[str, str] = {}
    anchors: list = []
    if anchors_path.exists():
        raw = json.loads(anchors_path.read_text(encoding="utf-8"))
        anchors = raw["anchors"] if isinstance(raw, dict) and "anchors" in raw else (raw if isinstance(raw, list) else [])
        for a in anchors:
            if isinstance(a, dict) and a.get("qid"):
                anchor_labels[a["qid"]] = a.get("label", a["qid"])[:50]

    # Optional domain filter: only anchors with this domain
    domain_anchors: set[str] | None = None
    if args.domain_qid:
        domain_anchors = {
            a["qid"] for a in anchors
            if isinstance(a, dict) and a.get("domain_qid") == args.domain_qid
        }
        if not domain_anchors:
            domain_anchors = None  # no filter if none match

    # Aggregate
    by_type: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    off_schema_p31: Counter[str] = Counter()
    off_schema_entity_count = 0
    no_p31_count = 0
    per_anchor: dict[str, dict] = defaultdict(lambda: {"by_type": Counter(), "by_category": Counter(), "off_schema_p31": Counter(), "off_schema_entities": 0, "no_p31": 0})
    reports_processed = 0
    total_entities = 0

    for path in harvest_dir.glob("*_report.json"):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        seed_qid = report.get("seed_qid", "unknown")
        if domain_anchors is not None and seed_qid not in domain_anchors:
            continue
        reports_processed += 1
        pa = per_anchor[seed_qid]

        for section in ("accepted", "rejected"):
            for row in report.get(section, []):
                total_entities += 1
                p31s = row.get("p31") or []
                p31s = [q for q in p31s if q and isinstance(q, str) and q.startswith("Q")]

                if not p31s:
                    no_p31_count += 1
                    pa["no_p31"] += 1
                    continue

                matched = False
                for q in p31s:
                    if q in qid_to_schema:
                        info = qid_to_schema[q]
                        t = info["type"]
                        c = info["category"]
                        by_type[t] += 1
                        by_category[c] += 1
                        pa["by_type"][t] += 1
                        pa["by_category"][c] += 1
                        matched = True
                        break
                if not matched:
                    off_schema_entity_count += 1
                    pa["off_schema_entities"] += 1
                    for q in p31s:
                        off_schema_p31[q] += 1
                        pa["off_schema_p31"][q] += 1

    # Build output
    total_mapped = sum(by_type.values())
    total_with_p31 = total_entities - no_p31_count

    by_type_rows = [
        {"type": t, "count": c, "pct": round(100 * c / total_mapped, 2) if total_mapped else 0}
        for t, c in by_type.most_common()
    ]
    by_category_rows = [
        {"category": c, "count": n, "pct": round(100 * n / total_mapped, 2) if total_mapped else 0}
        for c, n in by_category.most_common()
    ]
    off_schema_top = [
        {"p31_qid": q, "count": c}
        for q, c in off_schema_p31.most_common(30)
    ]

    per_anchor_rows = []
    for seed_qid in sorted(per_anchor.keys()):
        pa = per_anchor[seed_qid]
        pt = pa["by_type"]
        pc = pa["by_category"]
        total_pa = sum(pt.values()) + pa["off_schema_entities"] + pa["no_p31"]
        if total_pa == 0:
            continue
        mapped_pa = sum(pt.values())
        per_anchor_rows.append({
            "seed_qid": seed_qid,
            "anchor_label": anchor_labels.get(seed_qid, seed_qid),
            "total_entities": total_pa,
            "mapped_to_schema": mapped_pa,
            "off_schema_entities": pa["off_schema_entities"],
            "no_p31": pa["no_p31"],
            "pct_on_schema": round(100 * mapped_pa / total_pa, 1) if total_pa else 0,
            "top_types": [{"type": t, "count": c} for t, c in pt.most_common(5)],
            "top_categories": [{"category": c, "count": n} for c, n in pc.most_common(3)],
        })

    report_data = {
        "domain_qid": args.domain_qid or "all",
        "summary": {
            "reports_processed": reports_processed,
            "total_entities": total_entities,
            "entities_with_p31": total_with_p31,
            "no_p31": no_p31_count,
            "mapped_to_canonical": total_mapped,
            "off_schema_entities": off_schema_entity_count,
            "pct_on_schema": round(100 * total_mapped / total_with_p31, 2) if total_with_p31 else 0,
            "canonical_types_count": len(qid_to_schema),
        },
        "by_canonical_type": by_type_rows,
        "by_category": by_category_rows,
        "off_schema_top_p31s": off_schema_top,
        "per_anchor": per_anchor_rows,
    }

    out_path = root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

    # Print summary
    print("=" * 72)
    print("ROMAN REPUBLIC BACKLINKS vs CANONICAL SCHEMA")
    print("=" * 72)
    print(f"Domain: {args.domain_qid}  |  Reports: {reports_processed}  |  Entities: {total_entities}")
    print(f"Mapped to canonical: {total_mapped}  |  Off-schema entities: {off_schema_entity_count}  |  No P31: {no_p31_count}")
    pct = 100 * total_mapped / total_with_p31 if total_with_p31 else 0
    print(f"On-schema rate: {pct:.1f}% (of entities with P31)")
    print("-" * 72)
    print("BY CANONICAL TYPE (top 20)")
    print("-" * 72)
    print(f"{'Type':<30} {'Count':>8} {'Pct':>6}")
    print("-" * 72)
    for r in by_type_rows[:20]:
        print(f"{r['type']:<30} {r['count']:>8} {r['pct']:>5.1f}%")
    print("-" * 72)
    print("BY CATEGORY")
    print("-" * 72)
    for r in by_category_rows:
        print(f"  {r['category']:<28} {r['count']:>8} {r['pct']:>5.1f}%")
    print("-" * 72)
    print("OFF-SCHEMA TOP P31s (unmapped)")
    print("-" * 72)
    for r in off_schema_top[:15]:
        print(f"  {r['p31_qid']:<12} {r['count']:>8}")
    print("-" * 72)
    print("PER-ANCHOR ON-SCHEMA RATE (sample)")
    print("-" * 72)
    for a in sorted(per_anchor_rows, key=lambda x: -x["pct_on_schema"])[:15]:
        lbl = (a["anchor_label"] or a["seed_qid"])[:40]
        print(f"  {a['seed_qid']} {a['pct_on_schema']:>5.1f}%  {lbl}")
    print("-" * 72)
    print(f"Report: {out_path}")


if __name__ == "__main__":
    main()
