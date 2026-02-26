#!/usr/bin/env python3
"""
Backlink P31 (instance_of) Distribution

Aggregates entity types across all harvest reports — globally and per anchor.
Shows distribution: people (Q5), events (Q1190554), streets (Q79007), etc.

Per-anchor breakdown reveals anchor quality: junk anchors (e.g. Plauen) show
street-heavy distributions; good anchors (e.g. Families) show domain-coherent types.

Usage:
    python scripts/analysis/backlink_p31_distribution.py
    python scripts/analysis/backlink_p31_distribution.py --output output/analysis/backlink_p31_distribution.json
"""
import argparse
import json
import time
from collections import Counter
from pathlib import Path

import requests

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1P31Distribution/1.0"

# Common P31 QIDs for quick reference (will fetch labels for top N)
COMMON_P31 = {
    "Q5": "human",
    "Q1190554": "occurrence",
    "Q56061": "place",
    "Q386724": "work",
    "Q4167836": "Wikimedia category",
    "Q4167410": "Wikipedia disambiguation",
    "Q79007": "street",
    "Q13442814": "scholarly article",
    "Q571": "book",
    "Q3305213": "painting",
    "Q838948": "work of art",
    "Q23442": "organization",
    "Q101352": "family name",
    "Q8436": "family",
}


def fetch_labels(qids: list[str]) -> dict[str, str]:
    """Fetch English labels for QIDs from Wikidata API."""
    if not qids:
        return {}
    qids = list(set(qids))[:50]  # API limit
    resp = requests.get(
        WIKIDATA_API,
        params={
            "action": "wbgetentities",
            "ids": "|".join(qids),
            "props": "labels",
            "languages": "en",
            "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    out = {}
    for qid, ent in (resp.json().get("entities") or {}).items():
        en = (ent.get("labels") or {}).get("en")
        out[qid] = en["value"] if en else qid
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--harvest-dir",
        default="output/backlinks",
        help="Directory with *_report.json files",
    )
    parser.add_argument(
        "--output",
        default="output/analysis/backlink_p31_distribution.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="Fetch labels for top N P31s (default 50)",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    harvest_dir = root / args.harvest_dir

    p31_counts: Counter[str] = Counter()
    per_anchor: dict[str, Counter[str]] = {}
    entity_count = 0
    reports_processed = 0

    for path in harvest_dir.glob("*_report.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        seed_qid = data.get("seed_qid", "unknown")
        reports_processed += 1
        anchor_counts = per_anchor.setdefault(seed_qid, Counter())
        for section in ("accepted", "rejected"):
            for row in data.get(section, []):
                for qid in row.get("p31", []):
                    if qid and qid.startswith("Q"):
                        p31_counts[qid] += 1
                        anchor_counts[qid] += 1
                entity_count += 1 if row.get("p31") else 0

    # Load anchor labels
    anchors_path = root / "output/subject_concepts/subject_concept_anchors_qid_canonical.json"
    anchor_labels: dict[str, str] = {}
    if anchors_path.exists():
        anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
        if isinstance(anchors, dict) and "anchors" in anchors:
            anchors = anchors["anchors"]
        anchor_labels = {a["qid"]: a.get("label", a["qid"])[:40] for a in anchors if a.get("qid")}

    # Build per-anchor distributions — collect P31s we need labels for
    label_qids = set()
    for ac in per_anchor.values():
        for q, _ in ac.most_common(5):
            label_qids.add(q)
    for q, _ in p31_counts.most_common(args.top):
        label_qids.add(q)
    labels = {q: COMMON_P31.get(q, q) for q in label_qids}
    fetched = fetch_labels([q for q in label_qids if q not in COMMON_P31])
    labels.update(fetched)
    time.sleep(0.3)

    per_anchor_rows = []
    for seed_qid in sorted(per_anchor.keys()):
        ac = per_anchor[seed_qid]
        total = sum(ac.values())
        if total == 0:
            continue
        top5 = ac.most_common(5)
        per_anchor_rows.append({
            "seed_qid": seed_qid,
            "anchor_label": anchor_labels.get(seed_qid, seed_qid),
            "entity_count": total,
            "top_p31s": [
                {"p31": q, "label": labels.get(q, q), "count": c, "pct": round(100 * c / total, 1)}
                for q, c in top5
            ],
        })

    # Build global distribution
    total_p31_mentions = sum(p31_counts.values())
    top_p31s = p31_counts.most_common(args.top)
    top_qids = [q for q, _ in top_p31s]

    rows = []
    for qid, count in top_p31s:
        pct = 100 * count / total_p31_mentions if total_p31_mentions else 0
        rows.append({
            "p31_qid": qid,
            "label": labels.get(qid, qid),
            "count": count,
            "pct": round(pct, 2),
        })

    report = {
        "summary": {
            "reports_processed": reports_processed,
            "entities_with_p31": entity_count,
            "total_p31_mentions": total_p31_mentions,
            "unique_p31_types": len(p31_counts),
        },
        "distribution": rows,
        "per_anchor": per_anchor_rows,
    }

    out_path = root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 70)
    print("BACKLINK P31 (instance_of) DISTRIBUTION")
    print("=" * 70)
    print(f"Reports: {reports_processed}  |  Entities: {entity_count}  |  Unique P31 types: {len(p31_counts)}")
    print("-" * 70)
    print(f"{'P31':<12} {'Count':>8} {'Pct':>6}  Label")
    print("-" * 70)
    for r in rows[:30]:
        print(f"{r['p31_qid']:<12} {r['count']:>8} {r['pct']:>5.1f}%  {r['label'][:45]}")
    print("-" * 70)
    print("\nPER-ANCHOR TOP 5 P31s (sample)")
    print("-" * 70)
    for a in per_anchor_rows[:12]:
        lbl = (a["anchor_label"] or a["seed_qid"])[:35]
        top = ", ".join(f"{t['label'][:12]}({t['pct']}%)" for t in a["top_p31s"])
        print(f"  {a['seed_qid']} {lbl}")
        print(f"    -> {top}")
    print("-" * 70)
    print(f"Report: {out_path}")


if __name__ == "__main__":
    main()
