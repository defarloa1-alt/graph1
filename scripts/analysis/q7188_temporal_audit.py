#!/usr/bin/env python3
"""
Q7188 (Government) temporal audit.

Of the 982 entities under Government, how many have temporal properties
(P585, P580, P582) vs unscoped? temporal_anchor in statement_profile
means the entity has at least one statement with a time value at year precision.

Note: temporal_anchor does NOT filter by Republican period — it only indicates
presence of temporal data. A 20th-century government has temporal_anchor.
True Republican-period filtering would require parsing actual date values.

Usage:
    python scripts/analysis/q7188_temporal_audit.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "output/backlinks/Q7188_report.json"


def main():
    with open(REPORT, encoding="utf-8") as f:
        report = json.load(f)

    accepted = report.get("accepted", [])
    total = len(accepted)

    with_temporal = 0
    without_temporal = 0
    samples_no_temporal = []
    samples_with_temporal = []

    for e in accepted:
        prof = e.get("statement_profile") or {}
        routes = prof.get("route_counts") or {}
        ta = routes.get("temporal_anchor", 0) or 0
        if ta >= 1:
            with_temporal += 1
            if len(samples_with_temporal) < 5:
                samples_with_temporal.append((e.get("qid"), (e.get("label") or "")[:50], ta))
        else:
            without_temporal += 1
            if len(samples_no_temporal) < 10:
                samples_no_temporal.append((e.get("qid"), (e.get("label") or "")[:50]))

    print("Q7188 (Government) temporal audit")
    print("=" * 60)
    print(f"Total entities: {total}")
    print(f"With temporal_anchor >= 1: {with_temporal} ({100*with_temporal/total:.1f}%)")
    print(f"Unscoped (no temporal): {without_temporal} ({100*without_temporal/total:.1f}%)")
    print()
    print("Sample WITH temporal (has P585/P580/P582 — any period):")
    for q, lbl, ta in samples_with_temporal:
        print(f"  {q}  ta={ta}  {lbl}")
    print()
    print("Sample WITHOUT temporal (unscoped):")
    for q, lbl in samples_no_temporal:
        print(f"  {q}  {lbl}")
    print()
    print("Note: temporal_anchor = has time statement, not Republican-period filter.")


if __name__ == "__main__":
    main()
