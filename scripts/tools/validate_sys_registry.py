#!/usr/bin/env python3
"""
Audit SYS_* nodes vs relationship_types_registry_master.csv.

Usage:
  python -m scripts.tools.validate_sys_registry
  python -m scripts.tools.validate_sys_registry --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

from scripts.tools.sys_registry import audit_sys_registry  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate SYS registry vs CSV master")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD not configured", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            audit = audit_sys_registry(session)
    finally:
        driver.close()

    if args.json:
        print(json.dumps(audit.__dict__, indent=2))
        return 0

    print("=== SYS registry audit ===\n")
    print(f"CSV total: {audit.csv_total}  implemented: {audit.csv_implemented}  candidate: {audit.csv_candidate}")
    print(f"Graph SYS_RelationshipType keys: {audit.graph_rel_types}")
    print(f"BacklinkRouting edge types ({len(audit.backlink_edge_types)}): {', '.join(audit.backlink_edge_types)}")

    if audit.backlink_not_in_csv:
        print(f"\nBacklink NOT in CSV: {', '.join(audit.backlink_not_in_csv)}")
    if audit.backlink_not_implemented:
        print(f"Backlink not implemented in CSV: {', '.join(audit.backlink_not_implemented)}")
    if audit.csv_impl_missing_in_graph:
        print(f"\nImplemented CSV missing in graph (first 20): {', '.join(audit.csv_impl_missing_in_graph[:20])}")
    if audit.graph_not_in_csv:
        print(f"Graph types not in CSV (first 20): {', '.join(audit.graph_not_in_csv[:20])}")

    print("\n=== SYS label counts ===")
    for lab, c in audit.sys_label_counts.items():
        print(f"  {lab}: {c}")

    if audit.warnings:
        print("\n=== Warnings ===")
        for w in audit.warnings:
            print(f"  - {w}")
        print("\nFix: python -m scripts.tools.sync_relationship_registry_to_graph --write --wire-schema")
        return 1
    if audit.notes:
        print("\n=== Notes ===")
        for n in audit.notes:
            print(f"  - {n}")
    print("\nRegistry sync OK (no critical gaps).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
