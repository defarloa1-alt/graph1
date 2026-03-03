#!/usr/bin/env python3
"""
Graph Census — Query Neo4j for SYS_* types, domain labels, relationship counts.

Outputs markdown (default) or JSON. Run instead of hand-maintaining BLOCK_CATALOG_RECONCILED.md.
One command, always current, never stale.

Usage:
  python -m scripts.tools.graph_census
  python -m scripts.tools.graph_census -o census.md
  python -m scripts.tools.graph_census --json -o census.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    NEO4J_URI = NEO4J_USERNAME = NEO4J_PASSWORD = NEO4J_DATABASE = None


def _run(session, query: str, **params):
    r = session.run(query, params or {})
    return [dict(rec) for rec in r]


def run_census(uri: str, user: str, password: str, database: str) -> dict:
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user or "neo4j", password))
    out = {}

    with driver.session(database=database) as session:
        # Totals
        r = _run(session, "MATCH (n) RETURN count(n) AS total_nodes")[0]
        out["total_nodes"] = r["total_nodes"]

        r = _run(session, "MATCH ()-[r]->() RETURN count(r) AS total_rels")[0]
        out["total_rels"] = r["total_rels"]

        # Label counts (APOC if available, else fallback)
        try:
            rows = _run(session, "CALL db.labels() YIELD label RETURN label")
            labels = [row["label"] for row in rows]
        except Exception:
            rows = _run(session, "MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label")
            labels = [row["label"] for row in rows]

        label_counts = {}
        for lbl in labels:
            r = _run(session, f"MATCH (n:`{lbl}`) RETURN count(n) AS c")[0]
            label_counts[lbl] = r["c"]
        out["label_counts"] = dict(sorted(label_counts.items(), key=lambda x: -x[1]))

        # Relationship type counts
        try:
            rows = _run(session, "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType AS type")
            rel_types = [row["type"] for row in rows]
        except Exception:
            rows = _run(session, "MATCH ()-[r]->() RETURN DISTINCT type(r) AS type")
            rel_types = [row["type"] for row in rows]

        rel_counts = {}
        for rt in rel_types:
            r = _run(session, f"MATCH ()-[r:`{rt}`]->() RETURN count(r) AS c")[0]
            rel_counts[rt] = r["c"]
        out["rel_type_counts"] = dict(sorted(rel_counts.items(), key=lambda x: -x[1]))

        # SYS_ labels
        sys_labels = {k: v for k, v in label_counts.items() if k.startswith("SYS_")}
        out["sys_labels"] = dict(sorted(sys_labels.items(), key=lambda x: -x[1]))

        # Federation sources
        rows = _run(session, """
            MATCH (fr:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
            RETURN f.name AS name, f.status AS status
            ORDER BY f.name
        """)
        out["federation_sources"] = rows

        # Decision tables
        rows = _run(session, """
            MATCH (dt:SYS_DecisionTable)
            OPTIONAL MATCH (dt)-[:HAS_ROW]->(r:SYS_DecisionRow)
            WITH dt, count(r) AS rows
            RETURN dt.table_id AS table_id, rows
            ORDER BY dt.table_id
        """)
        out["decision_tables"] = rows

        # Thresholds
        r = _run(session, "MATCH (n:SYS_Threshold) RETURN count(n) AS c")[0]
        out["sys_threshold_count"] = r["c"]

        # Policies
        r = _run(session, "MATCH (n:SYS_Policy) RETURN count(n) AS c")[0]
        out["sys_policy_count"] = r["c"]

        # ADRs
        rows = _run(session, "MATCH (n:SYS_ADR) RETURN n.adr_id AS adr_id ORDER BY n.adr_id")
        out["sys_adr_ids"] = [r["adr_id"] for r in rows if r.get("adr_id")]

        # Onboarding steps
        r = _run(session, "MATCH (n:SYS_OnboardingStep) RETURN count(n) AS c")[0]
        out["onboarding_step_count"] = r["c"]

        # Authority tiers
        r = _run(session, "MATCH (n:SYS_AuthorityTier) RETURN count(n) AS c")[0]
        out["authority_tier_count"] = r["c"]

        # Confidence tiers
        r = _run(session, "MATCH (n:SYS_ConfidenceTier) RETURN count(n) AS c")[0]
        out["confidence_tier_count"] = r["c"]

        # Node types
        r = _run(session, "MATCH (n:SYS_NodeType) RETURN count(n) AS c")[0]
        out["node_type_count"] = r["c"]

        # Relationship types (registry)
        r = _run(session, "MATCH (n:SYS_RelationshipType) RETURN count(n) AS c")[0]
        out["rel_type_registry_count"] = r["c"]

    driver.close()
    return out


def to_markdown(data: dict) -> str:
    lines = [
        "# Graph Census",
        "",
        f"**Generated:** {data.get('_timestamp', '')}",
        "",
        "## Totals",
        f"- Nodes: {data.get('total_nodes', 0):,}",
        f"- Relationships: {data.get('total_rels', 0):,}",
        f"- Relationship types: {len(data.get('rel_type_counts', {}))}",
        "",
        "## SYS_ Layer",
    ]
    for k, v in (data.get("sys_labels") or {}).items():
        lines.append(f"- {k}: {v:,}")
    lines.extend([
        "",
        "## Federation Sources",
    ])
    for fs in data.get("federation_sources") or []:
        lines.append(f"- {fs.get('name', '')}: {fs.get('status', '')}")
    lines.extend([
        "",
        "## Decision Tables",
    ])
    for dt in data.get("decision_tables") or []:
        lines.append(f"- {dt.get('table_id', '')}: {dt.get('rows', 0)} rows")
    lines.extend([
        "",
        "## Domain Labels (top 30)",
    ])
    domain = {k: v for k, v in (data.get("label_counts") or {}).items() if not k.startswith("SYS_")}
    for i, (k, v) in enumerate(list(domain.items())[:30]):
        lines.append(f"- {k}: {v:,}")
    lines.extend([
        "",
        "## Relationship Types (top 30)",
    ])
    for i, (k, v) in enumerate(list((data.get("rel_type_counts") or {}).items())[:30]):
        lines.append(f"- {k}: {v:,}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Graph census — SYS_* and domain counts")
    ap.add_argument("-o", "--output", help="Output file (default: stdout)")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    args = ap.parse_args()

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("NEO4J_URI and NEO4J_PASSWORD required (.env)", file=sys.stderr)
        return 1

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        return 1

    from datetime import datetime, timezone
    data = run_census(
        NEO4J_URI,
        NEO4J_USERNAME or "neo4j",
        NEO4J_PASSWORD,
        NEO4J_DATABASE or "neo4j",
    )
    data["_timestamp"] = datetime.now(timezone.utc).isoformat()

    if args.json:
        out = json.dumps(data, indent=2)
    else:
        out = to_markdown(data)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
