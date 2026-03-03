#!/usr/bin/env python3
"""
Export JSX Data — Dump JSON from graph for chrystallum_architecture.jsx to import.

Federation sources, SYS counts, domain counts come from graph. JSX layout stays hand-crafted.
Run before build: python -m scripts.tools.export_jsx_data -o output/jsx_architecture_data.json

Usage:
  python -m scripts.tools.export_jsx_data
  python -m scripts.tools.export_jsx_data -o output/jsx_architecture_data.json
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

# JSX display order and id mapping (graph name may differ)
JSX_FEDERATION_ORDER = [
    ("Wikidata", "Wikidata"),
    ("DPRR", "DPRR"),
    ("Pleiades", "Pleiades"),
    ("PeriodO", "PeriodO"),
    ("LCSH/FAST", "LCSH/FAST"),  # graph: LCSH/FAST/LCC
    ("Trismegistos", "Trismegistos"),
    ("LGPN", "LGPN"),
    ("VIAF", "VIAF"),
    ("Getty AAT", "Getty AAT"),
    ("Nomisma", "Nomisma"),  # may not be in graph -> future
    ("OCD", "OCD"),
    ("OpenAlex", "OpenAlex"),
]


def _run(session, query: str, **params):
    r = session.run(query, params or {})
    return [dict(rec) for rec in r]


def export_data(uri: str, user: str, password: str, database: str) -> dict:
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user or "neo4j", password))
    out = {}

    with driver.session(database=database) as session:
        # Federation sources
        rows = _run(session, """
            MATCH (fr:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
            RETURN f.name AS name, f.status AS status
        """)
        status_by_name = {r["name"]: r["status"] for r in rows}
        # Normalize LCSH/FAST/LCC -> LCSH/FAST for JSX
        if "LCSH/FAST/LCC" in status_by_name:
            status_by_name["LCSH/FAST"] = status_by_name["LCSH/FAST/LCC"]

        federation_sources = []
        for i, (jsx_id, lookup_name) in enumerate(JSX_FEDERATION_ORDER):
            status = status_by_name.get(lookup_name) or status_by_name.get(jsx_id)
            if status is None and jsx_id == "Nomisma":
                status = "future"
            elif status is None:
                status = "planned"
            federation_sources.append({
                "id": jsx_id,
                "status": status or "planned",
                "x": 30 + i * 85,  # approximate; JSX can override
            })
        out["federationSources"] = federation_sources

        # Counts by status
        op = sum(1 for s in federation_sources if s["status"] == "operational")
        part = sum(1 for s in federation_sources if s["status"] == "partial")
        block = sum(1 for s in federation_sources if s["status"] == "blocked")
        plan = sum(1 for s in federation_sources if s["status"] == "planned")
        future = sum(1 for s in federation_sources if s["status"] == "future")
        out["federationSummary"] = {
            "registered": len(rows),
            "operational": op,
            "partial": part,
            "blocked": block,
            "planned": plan,
            "future": future,
        }

        # Totals
        r = _run(session, "MATCH (n) RETURN count(n) AS c")[0]
        out["total_nodes"] = r["c"]
        r = _run(session, "MATCH (n:SYS_RelationshipType) RETURN count(n) AS c")[0]
        out["rel_type_count"] = r["c"]

        # Domain counts for Person cluster
        person_counts = {}
        for lbl in ["Person", "MythologicalPerson", "Gens", "Nomen", "Cognomen", "Praenomen", "Tribe", "HistoricalPolity"]:
            r = _run(session, f"MATCH (n:`{lbl}`) RETURN count(n) AS c")[0]
            person_counts[lbl] = r["c"]
        out["personCluster"] = person_counts

        # Place cluster
        place_counts = {}
        for lbl in ["Place", "Pleiades_Place", "HistoricalPolity"]:
            r = _run(session, f"MATCH (n:`{lbl}`) RETURN count(n) AS c")[0]
            place_counts[lbl] = r["c"]
        out["placeCluster"] = place_counts

        # Knowledge cluster
        knowledge_counts = {}
        for lbl in ["Discipline", "LCC_Class", "Periodo_Period", "LCSH_Heading", "WorldCat_Work", "Year", "Position", "Facet"]:
            r = _run(session, f"MATCH (n:`{lbl}`) RETURN count(n) AS c")[0]
            knowledge_counts[lbl] = r["c"]
        out["knowledgeCluster"] = knowledge_counts

        # SYS layer
        sys_counts = {}
        for lbl in ["SYS_FederationSource", "SYS_AuthorityTier", "SYS_ConfidenceTier", "SYS_DecisionTable", "SYS_DecisionRow",
                    "SYS_Policy", "SYS_Threshold", "SYS_RelationshipType", "SYS_NodeType", "SYS_PropertyMapping",
                    "SYS_ADR", "SYS_OnboardingProtocol"]:
            r = _run(session, f"MATCH (n:`{lbl}`) RETURN count(n) AS c")[0]
            sys_counts[lbl] = r["c"]
        out["sysLayer"] = sys_counts

        # Metrics bar
        r = _run(session, "MATCH (p:Person) WHERE p.dprr_id IS NOT NULL OR p.dprr_uri IS NOT NULL RETURN count(p) AS c")[0]
        dprr_persons = r["c"]
        r = _run(session, "MATCH ()-[r:POSITION_HELD]->() RETURN count(r) AS c")[0]
        position_held = r["c"]
        out["metrics"] = {
            "total_nodes": out["total_nodes"],
            "rel_types": out["rel_type_count"],
            "dprr_persons": dprr_persons,
            "position_held": position_held,
            "place_count": place_counts.get("Place", 0),
            "pleiades_count": place_counts.get("Pleiades_Place", 0),
            "discipline_count": knowledge_counts.get("Discipline", 0),
            "federation_sources": len(rows),
            "confidence_thresholds": "0.75 / 0.90",
        }

    driver.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Export graph data for JSX architecture diagram")
    ap.add_argument("-o", "--output", default="output/jsx_architecture_data.json", help="Output JSON file")
    args = ap.parse_args()

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("NEO4J_URI and NEO4J_PASSWORD required (.env)", file=sys.stderr)
        return 1

    try:
        data = export_data(
            NEO4J_URI,
            NEO4J_USERNAME or "neo4j",
            NEO4J_PASSWORD,
            NEO4J_DATABASE or "neo4j",
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
