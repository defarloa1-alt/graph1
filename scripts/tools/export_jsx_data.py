#!/usr/bin/env python3
"""
Chrystallum JSX Architecture Data Export.

Queries Neo4j and writes a JSON payload suitable for consumption by the
JSX architecture diagram / dashboard.  The JSX layout itself remains
hand-crafted; this script provides graph-backed numbers so counts and
statuses stay in sync with the live graph.

Usage:
  python -m scripts.tools.export_jsx_data                          # stdout
  python -m scripts.tools.export_jsx_data -o output/jsx_data.json  # file
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from neo4j import GraphDatabase

# ── Config ──────────────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", os.getenv("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


# ── Queries ─────────────────────────────────────────────────────────

Q_TOTALS = """
MATCH (n)
WITH count(n) AS nodes
MATCH ()-[r]->()
RETURN nodes, count(r) AS edges
"""

Q_SYS_COUNTS = """
CALL db.labels() YIELD label
WHERE label STARTS WITH 'SYS_'
RETURN label
ORDER BY label
"""

Q_SYS_COUNT_LABEL = "MATCH (n:`{label}`) RETURN count(n) AS cnt"

Q_DOMAIN_COUNTS = """
CALL db.labels() YIELD label
WHERE NOT label STARTS WITH 'SYS_'
RETURN label
ORDER BY label
"""

Q_FEDERATION_SOURCES = """
MATCH (s:SYS_FederationSource)
RETURN s.name AS name, s.pid AS pid, s.status AS status,
       s.scoping_weight AS scoping_weight
ORDER BY s.status, s.name
"""

Q_DECISION_TABLES = """
MATCH (dt:SYS_DecisionTable)
OPTIONAL MATCH (dt)-[:HAS_ROW]->(dr:SYS_DecisionRow)
RETURN dt.table_id AS table_id, dt.name AS name, count(dr) AS row_count
ORDER BY dt.table_id
"""

Q_REL_TYPE_COUNT = """
MATCH ()-[r]->()
WITH type(r) AS t
RETURN count(DISTINCT t) AS rel_types
"""

Q_POLICIES = """
MATCH (p:SYS_Policy)
RETURN p.name AS name, p.active AS active
ORDER BY p.name
"""

Q_THRESHOLDS = """
MATCH (t:SYS_Threshold)
RETURN t.name AS name, t.value AS value, t.unit AS unit
ORDER BY t.name
"""

Q_ADRS = """
MATCH (a:SYS_ADR)
RETURN a.adr_id AS adr_id, a.title AS title, a.status AS status
ORDER BY a.adr_id
"""


# ── Runner ──────────────────────────────────────────────────────────

class JSXDataExporter:
    def __init__(self, uri: str, user: str, password: str, database: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def _run(self, query: str, **params) -> List[Dict[str, Any]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(query, **params)
            return [dict(r) for r in result]

    def _count_label(self, label: str) -> int:
        rows = self._run(Q_SYS_COUNT_LABEL.format(label=label.replace("`", "``")))
        return rows[0]["cnt"] if rows else 0

    def export(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        data["generated"] = datetime.now(timezone.utc).isoformat()

        # Totals
        totals = self._run(Q_TOTALS)
        if totals:
            data["total_nodes"] = totals[0]["nodes"]
            data["total_edges"] = totals[0]["edges"]
        else:
            data["total_nodes"] = 0
            data["total_edges"] = 0

        # Rel type count
        rtc = self._run(Q_REL_TYPE_COUNT)
        data["rel_type_count"] = rtc[0]["rel_types"] if rtc else 0

        # SYS label counts
        sys_labels = self._run(Q_SYS_COUNTS)
        sys_counts = {}
        for row in sys_labels:
            lbl = row["label"]
            sys_counts[lbl] = self._count_label(lbl)
        data["sys_label_counts"] = sys_counts
        data["sys_label_type_count"] = len(sys_counts)

        # Domain label counts
        domain_labels = self._run(Q_DOMAIN_COUNTS)
        domain_counts = {}
        for row in domain_labels:
            lbl = row["label"]
            domain_counts[lbl] = self._count_label(lbl)
        data["domain_label_counts"] = domain_counts
        data["domain_label_type_count"] = len(domain_counts)

        # Federation sources
        data["federation_sources"] = self._run(Q_FEDERATION_SOURCES)
        status_summary: Dict[str, int] = {}
        for s in data["federation_sources"]:
            st = s["status"]
            status_summary[st] = status_summary.get(st, 0) + 1
        data["federation_status_summary"] = status_summary

        # Decision tables
        data["decision_tables"] = self._run(Q_DECISION_TABLES)

        # Policies & thresholds
        data["policies"] = self._run(Q_POLICIES)
        data["thresholds"] = self._run(Q_THRESHOLDS)

        # ADRs
        data["adrs"] = self._run(Q_ADRS)

        return data


# ── JSON encoder ────────────────────────────────────────────────────

class _Encoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return super().default(o)


# ── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Export JSX architecture data from graph")
    parser.add_argument("--uri", default=NEO4J_URI, help="Neo4j URI")
    parser.add_argument("--user", default=NEO4J_USERNAME, help="Neo4j user")
    parser.add_argument("--password", default=NEO4J_PASSWORD, help="Neo4j password")
    parser.add_argument("--database", default=NEO4J_DATABASE, help="Neo4j database")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    if not args.password:
        print("Error: NEO4J_PASSWORD not set. Use .env, config_loader, or --password.",
              file=sys.stderr)
        sys.exit(1)

    exporter = JSXDataExporter(args.uri, args.user, args.password, args.database)
    try:
        data = exporter.export()
    finally:
        exporter.close()

    output = json.dumps(data, indent=2, cls=_Encoder)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"JSX data written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
