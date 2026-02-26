#!/usr/bin/env python3
"""
Analyze harvest reports per advisor recommendations.

1. Q182547: Check if Pleiades (P1584) entities were dropped by node_budget_exceeded.
   Rejected entities weren't fetched, so we query Wikidata SPARQL for P1584.

2. Q337547: Unscoped breakdown by property — if P361 dominates, remove from allowlist.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

import requests

ROOT = Path(__file__).resolve().parents[2]
SPARQL_URL = "https://query.wikidata.org/sparql"


def check_q182547_pleiades_dropped(report_path: Path) -> dict:
    """Check if any node_budget_exceeded rejections have P1584 (Pleiades)."""
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    rejected = [r for r in report.get("rejected", []) if r.get("reason") == "node_budget_exceeded"]
    qids = [r["qid"] for r in rejected]
    if not qids:
        return {"rejected_count": 0, "pleiades_dropped": 0, "qids_with_pleiades": [], "recommendation": "No budget-cap rejections; anchor complete"}

    # SPARQL: which of these QIDs have P1584?
    values = " ".join(f"wd:{q}" for q in qids)
    query = f"""
    SELECT ?item WHERE {{
      VALUES ?item {{ {values} }}
      ?item wdt:P1584 ?pleiades .
    }}
    """
    try:
        r = requests.get(
            SPARQL_URL,
            params={"query": query, "format": "json"},
            headers={"User-Agent": "ChrystallumHarvestAnalysis/1.0"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        bindings = data.get("results", {}).get("bindings", [])
        pleiades_qids = []
        for b in bindings:
            uri = b.get("item", {}).get("value", "")
            if "/entity/" in uri:
                pleiades_qids.append(uri.split("/")[-1])
    except Exception as e:
        return {"count": len(qids), "error": str(e), "pleiades_dropped": None}

    return {
        "rejected_count": len(qids),
        "pleiades_dropped": len(pleiades_qids),
        "qids_with_pleiades": pleiades_qids,
        "recommendation": "Re-run with --max-new-nodes-per-seed 200" if pleiades_qids else "No Pleiades entities dropped; budget OK",
    }


def check_q337547_unscoped_by_property(report_path: Path) -> dict:
    """Break down unscoped entities by which property brought them in."""
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    accepted = report.get("accepted", [])
    unscoped = [a for a in accepted if a.get("scoping_status") == "unscoped"]
    by_property = defaultdict(list)
    for u in unscoped:
        props = tuple(sorted(u.get("properties", [])))
        by_property[props].append(u["qid"])

    counts = {", ".join(k): len(v) for k, v in sorted(by_property.items(), key=lambda x: -len(x[1]))}
    p361_only = sum(len(v) for k, v in by_property.items() if k == ("P361",))
    p140_p101 = sum(len(v) for k, v in by_property.items() if "P361" not in k)

    recommendation = (
        "Remove P361 from allowlist; re-run with P140, P101 only"
        if p361_only > len(unscoped) * 0.5
        else "Unscoped spread across properties; 46% is genuine signal quality for this anchor"
    )

    return {
        "unscoped_count": len(unscoped),
        "by_property": counts,
        "p361_only_count": p361_only,
        "p140_p101_count": p140_p101,
        "recommendation": recommendation,
    }


def main():
    backlinks = ROOT / "output" / "backlinks"
    q182547 = backlinks / "Q182547_report.json"
    q337547 = backlinks / "Q337547_report.json"

    print("=" * 70)
    print("HARVEST REPORT ANALYSIS")
    print("=" * 70)

    if q182547.exists():
        print("\n--- Q182547 (Provinces) — Pleiades in budget-cap rejections ---")
        r = check_q182547_pleiades_dropped(q182547)
        for k, v in r.items():
            print(f"  {k}: {v}")
    else:
        print(f"\nQ182547 report not found: {q182547}")

    if q337547.exists():
        print("\n--- Q337547 (Public ritual) — Unscoped by property ---")
        r = check_q337547_unscoped_by_property(q337547)
        for k, v in r.items():
            print(f"  {k}: {v}")
    else:
        print(f"\nQ337547 report not found: {q337547}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
