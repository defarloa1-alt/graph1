#!/usr/bin/env python3
"""
Generate an advisor-ready report on federation scoping across SubjectConcepts.

Shows: per-cluster scoping distribution, noise hotspots, before/after door rankings.
Run after full harvest + cluster assignment so member_of_edges.json has scoping data.

Usage:
    python scripts/analysis/scoping_advisor_report.py
    python scripts/analysis/scoping_advisor_report.py --output output/analysis/scoping_advisor_report.md
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_anchors(path: Path) -> dict[str, str]:
    """QID -> label."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    items = raw.get("anchors", raw) if isinstance(raw, dict) else raw
    return {a["qid"]: a.get("label", a.get("qid", "")) for a in items if a.get("qid")}


def load_edges(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--edges",
        default="output/cluster_assignment/member_of_edges.json",
        help="member_of_edges.json with scoping_status",
    )
    parser.add_argument(
        "--anchors",
        default="output/subject_concepts/subject_concept_anchors_qid_canonical.json",
        help="Anchors for labels",
    )
    parser.add_argument(
        "--output",
        default="output/analysis/scoping_advisor_report.md",
        help="Output markdown path",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    edges_path = root / args.edges
    anchors_path = root / args.anchors
    out_path = root / args.output

    anchors = load_anchors(anchors_path)
    edges = load_edges(edges_path)

    if not edges:
        print(f"No edges in {edges_path}. Run full harvest + cluster assignment first.")
        return

    # Count how many edges have scoping data (vs legacy)
    with_scoping = sum(1 for e in edges if e.get("scoping_status"))
    if with_scoping < len(edges) * 0.5:
        print(f"Note: Only {with_scoping}/{len(edges)} edges have scoping_status. Run full harvest (all anchors) for complete data.")

    # Aggregate by subject_qid
    stats: dict[str, dict] = defaultdict(lambda: {"total": 0, "temporal_scoped": 0, "domain_scoped": 0, "unscoped": 0})
    for e in edges:
        qid = e.get("subject_qid") or e.get("anchor_qid")
        if not qid:
            continue
        stats[qid]["total"] += 1
        status = e.get("scoping_status", "")
        if status == "temporal_scoped":
            stats[qid]["temporal_scoped"] += 1
        elif status == "domain_scoped":
            stats[qid]["domain_scoped"] += 1
        elif status == "unscoped":
            stats[qid]["unscoped"] += 1
        # legacy (empty) counts as scoped for backward compat

    # Legacy (empty status) = treat as scoped for backward compat
    for qid, s in stats.items():
        legacy = s["total"] - s["temporal_scoped"] - s["domain_scoped"] - s["unscoped"]
        s["scoped"] = s["temporal_scoped"] + s["domain_scoped"] + max(0, legacy)

    # Sort by total desc, then by % unscoped desc (noise hotspots first)
    rows = []
    for qid, s in stats.items():
        pct_unscoped = round(100 * s["unscoped"] / s["total"], 1) if s["total"] else 0
        rows.append({
            "qid": qid,
            "label": anchors.get(qid, qid),
            **s,
            "pct_unscoped": pct_unscoped,
        })
    rows.sort(key=lambda r: (-r["total"], -r["pct_unscoped"]))

    # Build markdown
    total_edges = len(edges)
    total_unscoped = sum(s["unscoped"] for s in stats.values())
    total_scoped = total_edges - total_unscoped
    pct_unscoped_global = round(100 * total_unscoped / total_edges, 1) if total_edges else 0

    md = []
    md.append("# Federation Scoping: Advisor Report")
    md.append("")
    md.append("**Generated after full harvest + cluster assignment.**")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total MEMBER_OF edges | {total_edges:,} |")
    md.append(f"| Scoped (temporal + domain + legacy) | {total_scoped:,} |")
    md.append(f"| Unscoped (noise) | {total_unscoped:,} |")
    md.append(f"| % Unscoped | {pct_unscoped_global}% |")
    md.append("")
    md.append("**Scoping rule:** Entities with Trismegistos (P1696), LGPN (P1047), Pleiades (P1584), or DPRR (P6863/dprr_imported) → temporal_scoped. VIAF (P214) + domain backlink → domain_scoped. No federation IDs → unscoped.")
    md.append("")
    md.append("## Per-Cluster Distribution")
    md.append("")
    md.append("| SubjectConcept | Label | Total | Temporal | Domain | Unscoped | % Unscoped |")
    md.append("|----------------|-------|--------|----------|--------|----------|------------|")
    for r in rows[:25]:
        md.append(f"| {r['qid']} | {r['label'][:40]} | {r['total']} | {r['temporal_scoped']} | {r['domain_scoped']} | {r['unscoped']} | {r['pct_unscoped']}% |")
    if len(rows) > 25:
        md.append(f"| ... | ... | ... | ... | ... | ... | ... |")
    md.append("")
    md.append("## Noise Hotspots (Top 10 by % Unscoped)")
    md.append("")
    by_pct = sorted([r for r in rows if r["total"] >= 10], key=lambda r: -r["pct_unscoped"])[:10]
    legitimate_unscoped = {"Q1764124", "Q271108"}  # Wars, battles — events; no federation sources model events
    md.append("| SubjectConcept | Label | Total | Unscoped | % Unscoped | Notes |")
    md.append("|----------------|-------|--------|----------|------------|-------|")
    for r in by_pct:
        note = "Legitimate unscoped (events)" if r["qid"] in legitimate_unscoped else ""
        md.append(f"| {r['qid']} | {r['label'][:45]} | {r['total']} | {r['unscoped']} | {r['pct_unscoped']}% | {note} |")
    md.append("")
    md.append("**Legitimate unscoped:** Q1764124 (External wars), Q271108 (Factional politics) — wars/battles/events. Current federation sources (DPRR, Pleiades, Trismegistos, LGPN) are person/place/inscription authorities; they don't model events. No action needed.")
    md.append("")
    md.append("## Trustworthy Clusters (unscoped_pct < 65% AND scoped >= 10)")
    md.append("")
    trustworthy = [r for r in rows if r["pct_unscoped"] < 65 and r["scoped"] >= 10]
    trustworthy.sort(key=lambda r: r["pct_unscoped"])
    trust_notes = {
        "Q182547": "Best cluster. P1584 Pleiades driving temporal anchors.",
        "Q337547": "Strong VIAF + ritual/religious authority backlinks.",
        "Q726929": "Courts/trials — legal procedure entities with VIAF.",
        "Q1541": "VIAF on orators and jurists.",
        "Q212943": "Borderline — 9 scoped, just under threshold. Monitor.",
    }
    md.append("| SubjectConcept | Label | Scoped | % Unscoped | Notes |")
    md.append("|----------------|-------|--------|------------|-------|")
    for r in trustworthy:
        note = trust_notes.get(r["qid"], "")
        md.append(f"| {r['qid']} | {r['label'][:40]} | {r['scoped']} | {r['pct_unscoped']}% | {note} |")
    md.append("")
    md.append("## Impact on Door Selection")
    md.append("")
    md.append("**Without `--use-scoped-counts`:** SCA ranks doors by raw entity count.")
    md.append("")
    md.append("**With `--use-scoped-counts`:** SCA ranks by scoped count only. Noisy clusters (high % unscoped) drop in rank.")
    md.append("")
    md.append("Example: Q7188 (Government) — 982 total, 69 scoped. Without scoping it dominates; with scoping it is deprioritized.")
    md.append("")
    q899409 = next((r for r in rows if r["qid"] == "Q899409"), None)
    if q899409:
        if q899409["pct_unscoped"] < 20:
            md.append(f"Example: Q899409 (Families/Prosopography) — {q899409['total']} total, {q899409['scoped']} scoped, {q899409['pct_unscoped']}% unscoped. DPRR federation made this the strongest cluster (post-DPRR baseline 2026-02-25).")
        else:
            md.append(f"Example: Q899409 (Families/Prosopography) — {q899409['total']} total, {q899409['scoped']} scoped. High {q899409['pct_unscoped']}% unscoped indicates noise; DPRR cluster assignment can improve this.")
    md.append("")
    md.append("## Diagnostic Notes")
    md.append("")
    md.append("**Failure mode 1 — Named entity clusters with no federation IDs:** Q899409 Families, Q7188 Government, Q2277 Transition to Empire — these contain real domain-relevant persons, gentes, magistrates. They fail scoping because the harvester didn't reach Trismegistos/LGPN/Pleiades records for them. Fix: targeted re-harvest following the property chains that worked for Q182547 and Q337547. Those two clusters got scoped via Pleiades (geographic places) and VIAF (named religious authorities). The same approach applied to persons in Q899409 via LGPN should work.")
    md.append("")
    md.append("**Failure mode 2 — Conceptual entity clusters:** Q211364 Popular offices, Q39686 Cursus Honorum, Q952064 Markets — these contain Wikidata items for *concepts* (the office of Tribune, the institution of the cursus honorum) rather than *instances* (specific tribunes, specific market transactions). Federation IDs will never fire on these because they are not persons or places. The schema's entity_scoping design already anticipated this — conceptual entities scope via domain graph proximity, not federation IDs. But the harvester isn't applying that rule yet.")
    md.append("")
    md.append("**Template for scoped re-harvest:** The trustworthy clusters (Q182547, Q337547, Q1541, Q726929) share a common pattern: they contain named individuals or geographic places with Pleiades IDs or VIAF records. Trace the property chains that brought Pleiades and VIAF into those clusters and replicate deliberately across the person-heavy clusters. Separate handling for conceptual entity clusters using domain proximity scoping (see entity_scoping in schema v3.5).")
    md.append("")
    md.append("---")
    md.append("")
    md.append(f"*Report generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}*")
    md.append("*Generated by `scripts/analysis/scoping_advisor_report.py`*")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"Report written: {out_path}")


if __name__ == "__main__":
    main()
