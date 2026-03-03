#!/usr/bin/env python3
"""
Chrystallum Graph Census — automated snapshot of graph state.

Queries Neo4j for all SYS_* types, domain entity labels, relationship
counts, and federation source statuses. Outputs a markdown report that
can replace manual block-catalog count maintenance.

Usage:
  python -m scripts.tools.graph_census                 # stdout
  python -m scripts.tools.graph_census -o census.md    # file output
  python -m scripts.tools.graph_census --json           # JSON output

Requires: neo4j driver, config_loader (or NEO4J_* env vars)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


# ── Query definitions ───────────────────────────────────────────────

# 1. Total node and edge counts
Q_TOTALS = """
MATCH (n)
WITH count(n) AS nodes
MATCH ()-[r]->()
RETURN nodes, count(r) AS edges
"""

# 2. Relationship type count
Q_REL_TYPE_COUNT = """
MATCH ()-[r]->()
WITH type(r) AS t
RETURN count(DISTINCT t) AS rel_types
"""

# 3. All labels with counts (sorted descending)
Q_LABEL_COUNTS = """
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) AS cnt', {})
YIELD value
RETURN label, value.cnt AS count
ORDER BY value.cnt DESC
"""

# Fallback if APOC is unavailable — uses the built-in procedure
Q_LABEL_COUNTS_FALLBACK = """
CALL db.labels() YIELD label
RETURN label
ORDER BY label
"""

# For each label returned by fallback, we query individually:
Q_COUNT_LABEL = "MATCH (n:`{label}`) RETURN count(n) AS cnt"

# 4. SYS_* label counts (subset of label counts; captured from the full list)
# (no separate query needed — filtered from Q_LABEL_COUNTS results)

# 5. Federation sources with status
Q_FEDERATION_SOURCES = """
MATCH (s:SYS_FederationSource)
RETURN s.name AS name, s.pid AS pid, s.status AS status,
       s.scoping_weight AS scoping_weight
ORDER BY s.status, s.name
"""

# 6. Decision table index
Q_DECISION_TABLES = """
MATCH (dt:SYS_DecisionTable)
OPTIONAL MATCH (dt)-[:HAS_ROW]->(dr:SYS_DecisionRow)
RETURN dt.table_id AS table_id, dt.name AS name, count(dr) AS row_count
ORDER BY dt.table_id
"""

# 7. Thresholds
Q_THRESHOLDS = """
MATCH (t:SYS_Threshold)
RETURN t.name AS name, t.value AS value, t.unit AS unit
ORDER BY t.name
"""

# 8. Policies
Q_POLICIES = """
MATCH (p:SYS_Policy)
RETURN p.name AS name, p.active AS active
ORDER BY p.name
"""

# 9. Key relationship counts (top N by volume)
Q_REL_COUNTS = """
MATCH ()-[r]->()
WITH type(r) AS rel_type, count(*) AS cnt
RETURN rel_type, cnt
ORDER BY cnt DESC
"""

# 10. ADRs
Q_ADRS = """
MATCH (a:SYS_ADR)
RETURN a.adr_id AS adr_id, a.title AS title, a.status AS status
ORDER BY a.adr_id
"""

# 11. Onboarding steps
Q_ONBOARDING = """
MATCH (s:SYS_OnboardingStep)
RETURN count(s) AS step_count
"""

# 12. Authority and confidence tiers
Q_AUTHORITY_TIERS = """
MATCH (t:SYS_AuthorityTier)
RETURN t.name AS name, t.tier AS tier
ORDER BY t.tier
"""

Q_CONFIDENCE_TIERS = """
MATCH (t:SYS_ConfidenceTier)
RETURN t.name AS name, t.tier AS tier
ORDER BY t.tier
"""

# 13. Node types registered
Q_NODE_TYPES = """
MATCH (nt:SYS_NodeType)
RETURN nt.name AS name
ORDER BY nt.name
"""


# ── Query runner ────────────────────────────────────────────────────

class CensusRunner:
    def __init__(self, uri: str, user: str, password: str, database: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def _run(self, query: str, **params) -> List[Dict[str, Any]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(query, **params)
            return [dict(r) for r in result]

    def collect(self) -> Dict[str, Any]:
        """Run all census queries and return structured results."""
        census: Dict[str, Any] = {}
        census["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Totals
        totals = self._run(Q_TOTALS)
        if totals:
            census["total_nodes"] = totals[0]["nodes"]
            census["total_edges"] = totals[0]["edges"]
        else:
            census["total_nodes"] = 0
            census["total_edges"] = 0

        # Rel type count
        rtc = self._run(Q_REL_TYPE_COUNT)
        census["rel_type_count"] = rtc[0]["rel_types"] if rtc else 0

        # Label counts — try APOC first, fall back to individual queries
        label_counts: Dict[str, int] = {}
        try:
            rows = self._run(Q_LABEL_COUNTS)
            for r in rows:
                label_counts[r["label"]] = r["count"]
        except Exception:
            # APOC unavailable — query each label individually
            labels = self._run(Q_LABEL_COUNTS_FALLBACK)
            for r in labels:
                lbl = r["label"]
                cnt = self._run(Q_COUNT_LABEL.format(label=lbl.replace("`", "``")))
                label_counts[lbl] = cnt[0]["cnt"] if cnt else 0

        census["label_counts"] = dict(sorted(label_counts.items(), key=lambda x: -x[1]))

        # Split into SYS_* and domain labels
        sys_labels = {k: v for k, v in label_counts.items() if k.startswith("SYS_")}
        domain_labels = {k: v for k, v in label_counts.items() if not k.startswith("SYS_")}
        census["sys_label_counts"] = dict(sorted(sys_labels.items(), key=lambda x: -x[1]))
        census["domain_label_counts"] = dict(sorted(domain_labels.items(), key=lambda x: -x[1]))

        # Federation sources
        census["federation_sources"] = self._run(Q_FEDERATION_SOURCES)

        # Decision tables
        census["decision_tables"] = self._run(Q_DECISION_TABLES)

        # Thresholds
        census["thresholds"] = self._run(Q_THRESHOLDS)

        # Policies
        census["policies"] = self._run(Q_POLICIES)

        # Relationship counts
        census["relationship_counts"] = self._run(Q_REL_COUNTS)

        # ADRs
        census["adrs"] = self._run(Q_ADRS)

        # Onboarding
        ob = self._run(Q_ONBOARDING)
        census["onboarding_step_count"] = ob[0]["step_count"] if ob else 0

        # Authority tiers
        census["authority_tiers"] = self._run(Q_AUTHORITY_TIERS)

        # Confidence tiers
        census["confidence_tiers"] = self._run(Q_CONFIDENCE_TIERS)

        # Node types
        census["node_types"] = self._run(Q_NODE_TYPES)

        return census


# ── Markdown formatter ──────────────────────────────────────────────

def format_markdown(census: Dict[str, Any]) -> str:
    lines: List[str] = []
    w = lines.append

    w(f"# Chrystallum Graph Census")
    w(f"")
    w(f"**Generated:** {census['timestamp']}")
    w(f"")

    # ── Summary ──
    w(f"## Summary")
    w(f"")
    w(f"| Metric | Value |")
    w(f"|--------|-------|")
    w(f"| Total nodes | {census['total_nodes']:,} |")
    w(f"| Total edges | {census['total_edges']:,} |")
    w(f"| Relationship types | {census['rel_type_count']} |")
    w(f"| SYS_* label types | {len(census['sys_label_counts'])} |")
    w(f"| Domain label types | {len(census['domain_label_counts'])} |")
    w(f"| Federation sources | {len(census['federation_sources'])} |")
    w(f"| Decision tables | {len(census['decision_tables'])} |")
    w(f"| Thresholds | {len(census['thresholds'])} |")
    w(f"| Policies | {len(census['policies'])} |")
    w(f"| Onboarding steps | {census['onboarding_step_count']} |")
    w(f"")

    # ── SYS_* labels ──
    w(f"## SYS_* Label Counts")
    w(f"")
    w(f"| Label | Count |")
    w(f"|-------|-------|")
    for label, count in census["sys_label_counts"].items():
        w(f"| {label} | {count:,} |")
    w(f"")

    # ── Domain labels ──
    w(f"## Domain Label Counts")
    w(f"")
    w(f"| Label | Count |")
    w(f"|-------|-------|")
    for label, count in census["domain_label_counts"].items():
        w(f"| {label} | {count:,} |")
    w(f"")

    # ── Relationship counts ──
    w(f"## Relationship Counts (all types)")
    w(f"")
    w(f"| Relationship | Count |")
    w(f"|-------------|-------|")
    for r in census["relationship_counts"]:
        w(f"| {r['rel_type']} | {r['cnt']:,} |")
    w(f"")

    # ── Federation sources ──
    w(f"## Federation Sources")
    w(f"")
    w(f"| Name | PID | Status | Scoping Weight |")
    w(f"|------|-----|--------|----------------|")
    for s in census["federation_sources"]:
        weight = s.get("scoping_weight") or "—"
        w(f"| {s['name']} | {s.get('pid') or '—'} | {s['status']} | {weight} |")
    w(f"")

    # ── Federation status summary ──
    status_counts: Dict[str, int] = {}
    for s in census["federation_sources"]:
        st = s["status"]
        status_counts[st] = status_counts.get(st, 0) + 1
    w(f"**Status summary:** " + " · ".join(
        f"{count} {status}" for status, count in sorted(status_counts.items())
    ))
    w(f"")

    # ── Decision tables ──
    w(f"## Decision Tables")
    w(f"")
    w(f"| Table ID | Name | Rows |")
    w(f"|----------|------|------|")
    for dt in census["decision_tables"]:
        name = dt.get("name") or "—"
        w(f"| {dt['table_id']} | {name} | {dt['row_count']} |")
    w(f"")

    # ── Thresholds ──
    w(f"## Thresholds ({len(census['thresholds'])})")
    w(f"")
    w(f"| Name | Value | Unit |")
    w(f"|------|-------|------|")
    for t in census["thresholds"]:
        unit = t.get("unit") or "—"
        w(f"| {t['name']} | {t['value']} | {unit} |")
    w(f"")

    # ── Policies ──
    w(f"## Policies ({len(census['policies'])})")
    w(f"")
    w(f"| Name | Active |")
    w(f"|------|--------|")
    for p in census["policies"]:
        active = p.get("active")
        active_str = "yes" if active else ("no" if active is False else "—")
        w(f"| {p['name']} | {active_str} |")
    w(f"")

    # ── ADRs ──
    if census["adrs"]:
        w(f"## ADRs")
        w(f"")
        w(f"| ID | Title | Status |")
        w(f"|----|-------|--------|")
        for a in census["adrs"]:
            w(f"| {a['adr_id']} | {a.get('title') or '—'} | {a.get('status') or '—'} |")
        w(f"")

    # ── Authority tiers ──
    if census["authority_tiers"]:
        w(f"## Authority Tiers ({len(census['authority_tiers'])})")
        w(f"")
        w(f"| Tier | Name |")
        w(f"|------|------|")
        for t in census["authority_tiers"]:
            w(f"| {t.get('tier') or '—'} | {t.get('name') or '—'} |")
        w(f"")

    # ── Confidence tiers ──
    if census["confidence_tiers"]:
        w(f"## Confidence Tiers ({len(census['confidence_tiers'])})")
        w(f"")
        w(f"| Tier | Name |")
        w(f"|------|------|")
        for t in census["confidence_tiers"]:
            w(f"| {t.get('tier') or '—'} | {t.get('name') or '—'} |")
        w(f"")

    # ── Registered node types ──
    if census["node_types"]:
        w(f"## Registered Node Types (SYS_NodeType: {len(census['node_types'])})")
        w(f"")
        for nt in census["node_types"]:
            w(f"- {nt['name']}")
        w(f"")

    return "\n".join(lines)


# ── JSON formatter ──────────────────────────────────────────────────

class _CensusEncoder(json.JSONEncoder):
    """Handle any non-serializable types from Neo4j driver."""
    def default(self, o):
        # neo4j datetime / duration → string
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return super().default(o)


# ── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Chrystallum graph census")
    parser.add_argument("--uri", default=NEO4J_URI, help="Neo4j URI")
    parser.add_argument("--user", default=NEO4J_USERNAME, help="Neo4j user")
    parser.add_argument("--password", default=NEO4J_PASSWORD, help="Neo4j password")
    parser.add_argument("--database", default=NEO4J_DATABASE, help="Neo4j database")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    args = parser.parse_args()

    if not args.password:
        print("Error: NEO4J_PASSWORD not set. Use .env, config_loader, or --password.",
              file=sys.stderr)
        sys.exit(1)

    runner = CensusRunner(args.uri, args.user, args.password, args.database)
    try:
        census = runner.collect()
    finally:
        runner.close()

    if args.json:
        output = json.dumps(census, indent=2, cls=_CensusEncoder)
    else:
        output = format_markdown(census)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Census written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
