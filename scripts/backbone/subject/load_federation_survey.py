#!/usr/bin/env python3
"""
Load federation survey nodes to Neo4j (Pleiades, Periodo, DPRR, WorldCat).

Reads FederationSurvey JSON, creates federation-specific nodes with semantic_facet.
For LCSH use load_lcsh_survey.py; for LCC use load_lcc_nodes.py.

Node types:
  Pleiades  -> Pleiades_Place {pleiades_id, label, uri, ...}
  Periodo   -> Periodo_Period {periodo_id, label, uri, ...}
  DPRR      -> DPRR_Office {dprr_id, label, uri, ...}
  WorldCat  -> WorldCat_Work {worldcat_id, label, uri, ...}

Usage:
  python scripts/backbone/subject/load_federation_survey.py --survey output/nodes/pleiades_roman_republic.json
  python scripts/backbone/subject/load_federation_survey.py --survey output/nodes/periodo_roman_republic.json --cypher-out output/neo4j/periodo_load.cypher
  python scripts/backbone/subject/load_federation_survey.py --survey output/nodes/dprr_roman_republic.json
  python scripts/backbone/subject/load_federation_survey.py --survey output/nodes/worldcat_roman_republic.json --dry-run

Config: config_loader (.env) or NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD.
"""
import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

FEDERATION_CONFIG = {
    "pleiades": {"node_label": "Pleiades_Place", "id_key": "pleiades_id"},
    "periodo": {"node_label": "Periodo_Period", "id_key": "periodo_id"},
    "dprr": {"node_label": "DPRR_Office", "id_key": "dprr_id"},
    "worldcat": {"node_label": "WorldCat_Work", "id_key": "worldcat_id"},
}

BATCH_SIZE = 100


def _to_cypher_map(obj: dict) -> str:
    """Convert dict to Cypher map literal (single-quoted strings, unquoted keys)."""
    parts = []
    for k, v in obj.items():
        if v is None:
            parts.append(f"{k}: null")
        elif isinstance(v, bool):
            parts.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            parts.append(f"{k}: {v}")
        else:
            escaped = str(v).replace("\\", "\\\\").replace("'", "\\'")
            parts.append(f"{k}: '{escaped}'")
    return "{" + ", ".join(parts) + "}"


def load_survey(path: Path, federation: str) -> tuple[list[dict], str, str]:
    """Load nodes from FederationSurvey JSON. Returns (nodes, node_label, id_key)."""
    cfg = FEDERATION_CONFIG.get(federation)
    if not cfg:
        raise ValueError(f"Unsupported federation: {federation}. Use load_lcsh_survey or load_lcc_nodes.")
    node_label = cfg["node_label"]
    id_key = cfg["id_key"]

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    nodes_raw = data.get("nodes", [])
    federation_from_file = data.get("federation", federation)

    out = []
    for n in nodes_raw:
        nid = n.get("id", "")
        label = n.get("label", "")
        uri = n.get("uri", "")
        domain = n.get("domain", "")
        concept_ref = n.get("concept_ref")
        spatial_anchor = n.get("spatial_anchor")
        props = n.get("properties", {})
        semantic_facet = props.get("semantic_facet") or n.get("_semantic_facet")
        tr = n.get("temporal_range")
        temporal_start = tr[0] if isinstance(tr, (list, tuple)) and len(tr) >= 1 else None
        temporal_end = tr[1] if isinstance(tr, (list, tuple)) and len(tr) >= 2 else None
        out.append({
            "id": nid,
            "label": label,
            "uri": uri,
            "domain": domain or "",
            "concept_ref": concept_ref or "",
            "spatial_anchor": spatial_anchor or "",
            "semantic_facet": semantic_facet,
            "temporal_start": temporal_start,
            "temporal_end": temporal_end,
            "survey_depth": n.get("survey_depth", 0),
            "is_seed": n.get("is_seed", False),
        })
    return out, node_label, id_key


def write_cypher_file(nodes: list[dict], node_label: str, id_key: str, out_path: Path) -> None:
    """Generate .cypher file."""
    lines = [
        f"// {node_label} nodes from FederationSurvey",
        "// Run via MCP run_cypher_mutation or: cypher-shell -f <file>",
        "",
    ]
    for i in range(0, len(nodes), BATCH_SIZE):
        batch = nodes[i : i + BATCH_SIZE]
        rows = [
            {
                id_key: n["id"],
                "label": n["label"],
                "uri": n["uri"],
                "domain": n["domain"],
                "concept_ref": n["concept_ref"],
                "spatial_anchor": n["spatial_anchor"],
                "semantic_facet": n.get("semantic_facet") or "",
                "temporal_start": n.get("temporal_start"),
                "temporal_end": n.get("temporal_end"),
                "survey_depth": n.get("survey_depth", 0),
                "is_seed": n.get("is_seed", False),
            }
            for n in batch
        ]
        cypher_list = "[" + ", ".join(_to_cypher_map(r) for r in rows) + "]"
        lines.append(f"UNWIND {cypher_list} AS row")
        lines.append(f"MERGE (n:{node_label} {{{id_key}: row.{id_key}}})")
        lines.append("SET n.label = row.label, n.uri = row.uri, n.domain = row.domain,")
        lines.append("    n.concept_ref = row.concept_ref, n.spatial_anchor = row.spatial_anchor,")
        lines.append("    n.semantic_facet = row.semantic_facet,")
        lines.append("    n.temporal_start = row.temporal_start, n.temporal_end = row.temporal_end,")
        lines.append("    n.survey_depth = row.survey_depth, n.is_seed = row.is_seed;")
        lines.append("")

    facet_rows = [{"id": n["id"], "facet_key": n["semantic_facet"]}
                 for n in nodes if n.get("semantic_facet")]
    if facet_rows:
        for i in range(0, len(facet_rows), BATCH_SIZE):
            batch = facet_rows[i : i + BATCH_SIZE]
            rows = [{id_key: r["id"], "facet_key": r["facet_key"]} for r in batch]
            cypher_list = "[" + ", ".join(_to_cypher_map(r) for r in rows) + "]"
            lines.append(f"UNWIND {cypher_list} AS row")
            lines.append(f"MATCH (n:{node_label} {{{id_key}: row.{id_key}}})")
            lines.append("MATCH (f:CanonicalFacet {key: row.facet_key})")
            lines.append("MERGE (n)-[r:MAPS_TO_FACET]->(f)")
            lines.append("SET r.weight = 1.0;")
            lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[{node_label}] Wrote Cypher to {out_path} ({len(nodes)} nodes)")


def run_load(survey_path: Path, federation: str, uri: str, user: str, password: str,
             dry_run: bool, cypher_out: Path | None) -> int:
    if not GraphDatabase:
        print("ERROR: neo4j package required. pip install neo4j")
        return 1

    try:
        nodes, node_label, id_key = load_survey(survey_path, federation)
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1

    if not nodes:
        print("ERROR: No nodes in survey")
        return 1

    if dry_run:
        print(f"DRY RUN — would create {len(nodes)} {node_label} nodes:")
        for n in nodes[:5]:
            print(f"  {n['id']}: {n['label'][:45]} facet={n.get('semantic_facet')}")
        print(f"  ... and {len(nodes) - 5} more")
        return 0

    if cypher_out:
        write_cypher_file(nodes, node_label, id_key, cypher_out)
        print(f"[{node_label}] {len(nodes)} nodes -> Cypher file")
        return 0

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        for n in nodes:
            session.run(f"""
                MERGE (n:{node_label} {{{id_key}: $id}})
                SET n.label = $label,
                    n.uri = $uri,
                    n.domain = $domain,
                    n.concept_ref = $concept_ref,
                    n.spatial_anchor = $spatial_anchor,
                    n.semantic_facet = $semantic_facet,
                    n.temporal_start = $temporal_start,
                    n.temporal_end = $temporal_end,
                    n.survey_depth = $survey_depth,
                    n.is_seed = $is_seed
            """, {
                "id": n["id"],
                "label": n["label"],
                "uri": n["uri"],
                "domain": n["domain"],
                "concept_ref": n["concept_ref"] or None,
                "spatial_anchor": n["spatial_anchor"] or None,
                "semantic_facet": n.get("semantic_facet") or None,
                "temporal_start": n.get("temporal_start"),
                "temporal_end": n.get("temporal_end"),
                "survey_depth": n.get("survey_depth", 0),
                "is_seed": n.get("is_seed", False),
            })

        for n in nodes:
            facet = n.get("semantic_facet")
            if facet:
                session.run(f"""
                    MATCH (n:{node_label} {{{id_key}: $id}})
                    MATCH (f:CanonicalFacet {{key: $facet_key}})
                    MERGE (n)-[r:MAPS_TO_FACET]->(f)
                    SET r.weight = 1.0
                """, {"id": n["id"], "facet_key": facet})

    driver.close()
    print(f"[{node_label}] Loaded {len(nodes)} nodes")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Load federation survey to Neo4j (Pleiades, Periodo, DPRR, WorldCat)")
    parser.add_argument("--survey", type=Path, required=True)
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cypher-out", type=Path)
    args = parser.parse_args()

    survey_path = args.survey if args.survey.is_absolute() else Path(__file__).resolve().parents[3] / args.survey
    if not survey_path.exists():
        print(f"ERROR: Survey not found: {survey_path}")
        return 1

    with open(survey_path, encoding="utf-8") as f:
        federation = json.load(f).get("federation", "")
    if federation not in FEDERATION_CONFIG:
        print(f"ERROR: Use load_lcsh_survey.py for LCSH, load_lcc_nodes.py for LCC")
        print(f"  Supported: {list(FEDERATION_CONFIG.keys())}")
        return 1

    cypher_out = None
    if args.cypher_out:
        cypher_out = args.cypher_out if args.cypher_out.is_absolute() else Path(__file__).resolve().parents[3] / args.cypher_out

    return run_load(survey_path, federation, args.uri, args.user, args.password, args.dry_run, cypher_out)


if __name__ == "__main__":
    sys.exit(main())
