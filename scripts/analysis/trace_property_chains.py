#!/usr/bin/env python3
"""
Trace Property Chains for Federation Scoping

For trustworthy clusters (Q182547 Provinces, Q337547 Public ritual), analyzes
which backlink properties bring in entities that have Pleiades (P1584), VIAF (P214),
LGPN (P1047), or Trismegistos (P1696). Informs targeted re-harvest and property
allowlist tuning.

Usage:
    python scripts/analysis/trace_property_chains.py
    python scripts/analysis/trace_property_chains.py --reports output/backlinks/Q182547_report.json output/backlinks/Q337547_report.json --output output/analysis/property_chain_trace.md
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

FEDERATION_PIDS = {"P1584": "Pleiades", "P1696": "Trismegistos", "P1047": "LGPN", "P214": "VIAF"}


def load_report(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def trace_report(report: dict, seed_qid: str) -> dict:
    """Extract property chain stats for scoped entities."""
    entities = report.get("entities", report.get("accepted", []))
    if not entities and "accepted" in report:
        entities = report["accepted"]

    by_property: dict[str, dict] = defaultdict(lambda: {"temporal": 0, "domain": 0, "unscoped": 0, "federation_counts": Counter()})
    federation_by_prop: dict[str, Counter] = defaultdict(Counter)

    for ent in entities:
        status = ent.get("scoping_status", "unscoped")
        ext = ent.get("external_ids") or {}
        props = ent.get("properties") or []

        for pid in props:
            by_property[pid][status] = by_property[pid].get(status, 0) + 1
            for fed_pid, fed_name in FEDERATION_PIDS.items():
                if ext.get(fed_pid):
                    by_property[pid]["federation_counts"][fed_pid] += 1
                    federation_by_prop[pid][fed_pid] += 1

    return {
        "seed_qid": seed_qid,
        "total_entities": len(entities),
        "by_property": dict(by_property),
        "scoping_summary": report.get("scoping", {}),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", nargs="+",
                        default=[
                            "output/backlinks/Q182547_report.json",
                            "output/backlinks/Q337547_report.json",
                        ],
                        help="Harvest report paths")
    parser.add_argument("--output", default="output/analysis/property_chain_trace.md",
                        help="Output markdown path")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    out_path = root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Property Chain Trace: Federation Scoping",
        "",
        "Which backlink properties bring in entities with Pleiades, VIAF, LGPN, or Trismegistos?",
        "",
        "**Trustworthy clusters:** Q182547 (Provinces), Q337547 (Public ritual)",
        "",
        "---",
        "",
    ]

    for report_path in args.reports:
        path = root / report_path
        if not path.exists():
            lines.append(f"## {path.name}\n\n*Report not found*\n")
            continue

        report = load_report(path)
        seed = report.get("seed_qid", path.stem.replace("_report", "").replace("_", " "))
        trace = trace_report(report, seed)

        scoping = trace.get("scoping_summary", {})
        lines.append(f"## {seed}")
        lines.append("")
        lines.append(f"**Scoping:** temporal={scoping.get('temporal_scoped', 0)}, domain={scoping.get('domain_scoped', 0)}, unscoped={scoping.get('unscoped', 0)}")
        lines.append("")
        lines.append("### Properties bringing in scoped entities")
        lines.append("")
        lines.append("| Property | Temporal | Domain | Unscoped | P1584 | P214 | P1047 | P1696 |")
        lines.append("|----------|----------|--------|----------|-------|------|-------|-------|")

        by_prop = trace.get("by_property", {})
        for pid in sorted(by_prop.keys(), key=lambda p: (-by_prop[p].get("temporal_scoped", 0) - by_prop[p].get("domain_scoped", 0), p)):
            row = by_prop[pid]
            fc = row.get("federation_counts", Counter())
            lines.append(f"| {pid} | {row.get('temporal_scoped', 0)} | {row.get('domain_scoped', 0)} | {row.get('unscoped', 0)} | "
                        f"{fc.get('P1584', 0)} | {fc.get('P214', 0)} | {fc.get('P1838', 0)} | {fc.get('P1696', 0)} |")

        lines.append("")
        lines.append("**Key:** P1584=Pleiades, P214=VIAF, P1047=LGPN, P1696=Trismegistos")
        lines.append("")
        lines.append("---")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {out_path}")


if __name__ == "__main__":
    main()
