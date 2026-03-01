#!/usr/bin/env python3
"""
Load LCSH survey nodes to Neo4j.

Reads FederationSurvey JSON (e.g. output/nodes/lcsh_roman_republic.json),
creates LCSH_Heading nodes with semantic_facet, optionally MAPS_TO_FACET edges.

Schema:
  (:LCSH_Heading {lcsh_id, label, uri, domain, concept_ref, semantic_facet, ...})
  (l)-[:MAPS_TO_FACET {weight: 1.0}]->(:CanonicalFacet)  when semantic_facet present

Usage:
  python scripts/backbone/subject/load_lcsh_survey.py
  python scripts/backbone/subject/load_lcsh_survey.py --survey output/nodes/lcsh_roman_republic.json
  python scripts/backbone/subject/load_lcsh_survey.py --dry-run
  python scripts/backbone/subject/load_lcsh_survey.py --cypher-out output/neo4j/lcsh_load.cypher

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

BATCH_SIZE = 50


def load_survey(path: Path) -> list[dict]:
    """Load LCSH nodes from FederationSurvey JSON."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    out = []
    for n in nodes:
        lcsh_id = n.get("id", "")
        label = n.get("label", "")
        uri = n.get("uri") or (f"https://id.loc.gov/authorities/subjects/{lcsh_id}" if lcsh_id else "")
        domain = n.get("domain", "")
        concept_ref = n.get("concept_ref") or uri
        props = n.get("properties", {})
        semantic_facet = props.get("semantic_facet") or n.get("_semantic_facet")
        tr = n.get("temporal_range")
        temporal_start = tr[0] if isinstance(tr, (list, tuple)) and len(tr) >= 1 else None
        temporal_end = tr[1] if isinstance(tr, (list, tuple)) and len(tr) >= 2 else None
        out.append({
            "lcsh_id": lcsh_id,
            "label": label,
            "uri": uri,
            "domain": domain,
            "concept_ref": concept_ref,
            "semantic_facet": semantic_facet,
            "temporal_start": temporal_start,
            "temporal_end": temporal_end,
            "survey_depth": n.get("survey_depth", 0),
            "is_seed": n.get("is_seed", False),
        })
    return out


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


def write_cypher_file(nodes: list[dict], out_path: Path) -> None:
    """Generate .cypher file for MCP run_cypher_mutation or cypher-shell."""
    lines = [
        "// LCSH_Heading nodes from FederationSurvey",
        "// Run via MCP run_cypher_mutation or: cypher-shell -f <file>",
        "",
    ]
    for i in range(0, len(nodes), BATCH_SIZE):
        batch = nodes[i : i + BATCH_SIZE]
        rows = [
            {
                "lcsh_id": n["lcsh_id"],
                "label": n["label"],
                "uri": n["uri"],
                "domain": n.get("domain", ""),
                "concept_ref": n.get("concept_ref", ""),
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
        lines.append("MERGE (l:LCSH_Heading {lcsh_id: row.lcsh_id})")
        lines.append("SET l.label = row.label, l.uri = row.uri, l.domain = row.domain,")
        lines.append("    l.concept_ref = row.concept_ref, l.semantic_facet = row.semantic_facet,")
        lines.append("    l.temporal_start = row.temporal_start, l.temporal_end = row.temporal_end,")
        lines.append("    l.survey_depth = row.survey_depth, l.is_seed = row.is_seed;")
        lines.append("")

    # MAPS_TO_FACET for nodes with semantic_facet
    facet_rows = [{"lcsh_id": n["lcsh_id"], "facet_key": n["semantic_facet"]}
                 for n in nodes if n.get("semantic_facet")]
    for i in range(0, len(facet_rows), BATCH_SIZE):
        batch = facet_rows[i : i + BATCH_SIZE]
        cypher_list = "[" + ", ".join(_to_cypher_map(r) for r in batch) + "]"
        lines.append(f"UNWIND {cypher_list} AS row")
        lines.append("MATCH (l:LCSH_Heading {lcsh_id: row.lcsh_id})")
        lines.append("MATCH (f:CanonicalFacet {key: row.facet_key})")
        lines.append("MERGE (l)-[r:MAPS_TO_FACET]->(f)")
        lines.append("SET r.weight = 1.0;")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[LCSH] Wrote Cypher to {out_path} ({len(nodes)} nodes)")


def run_load(survey_path: Path, uri: str, user: str, password: str, dry_run: bool, cypher_out: Path | None) -> int:
    if not GraphDatabase:
        print("ERROR: neo4j package required. pip install neo4j")
        return 1

    nodes = load_survey(survey_path)
    if not nodes:
        print("ERROR: No nodes in survey")
        return 1

    if dry_run:
        print("DRY RUN — would create:")
        for n in nodes[:10]:
            print(f"  {n['lcsh_id']}: {n['label'][:40]} facet={n.get('semantic_facet')}")
        print(f"  ... and {len(nodes) - 10} more")
        return 0

    if cypher_out:
        write_cypher_file(nodes, cypher_out)
        print(f"[LCSH] Loaded {len(nodes)} nodes -> Cypher file (run via MCP or cypher-shell)")
        return 0

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        created = 0
        for n in nodes:
            session.run("""
                MERGE (l:LCSH_Heading {lcsh_id: $lcsh_id})
                SET l.label = $label,
                    l.uri = $uri,
                    l.domain = $domain,
                    l.concept_ref = $concept_ref,
                    l.semantic_facet = $semantic_facet,
                    l.temporal_start = $temporal_start,
                    l.temporal_end = $temporal_end,
                    l.survey_depth = $survey_depth,
                    l.is_seed = $is_seed
            """, {
                "lcsh_id": n["lcsh_id"],
                "label": n["label"],
                "uri": n["uri"],
                "domain": n.get("domain", ""),
                "concept_ref": n.get("concept_ref", ""),
                "semantic_facet": n.get("semantic_facet") or None,
                "temporal_start": n.get("temporal_start"),
                "temporal_end": n.get("temporal_end"),
                "survey_depth": n.get("survey_depth", 0),
                "is_seed": n.get("is_seed", False),
            })
            created += 1

        # MAPS_TO_FACET edges
        for n in nodes:
            facet = n.get("semantic_facet")
            if facet:
                session.run("""
                    MATCH (l:LCSH_Heading {lcsh_id: $lcsh_id})
                    MATCH (f:CanonicalFacet {key: $facet_key})
                    MERGE (l)-[r:MAPS_TO_FACET]->(f)
                    SET r.weight = 1.0
                """, {"lcsh_id": n["lcsh_id"], "facet_key": facet})

    driver.close()
    print(f"[LCSH] Loaded {created} LCSH_Heading nodes with semantic_facet")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Load LCSH survey to Neo4j")
    parser.add_argument("--survey", type=Path, default=Path("output/nodes/lcsh_roman_republic.json"))
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--cypher-out",
        type=Path,
        help="Write Cypher to file (for MCP run_cypher_mutation or cypher-shell)",
    )
    args = parser.parse_args()

    survey_path = args.survey
    if not survey_path.is_absolute():
        survey_path = Path(__file__).resolve().parents[3] / survey_path
    if not survey_path.exists():
        print(f"ERROR: Survey not found: {survey_path}")
        print("  Run: python scripts/backbone/subject/survey_lcsh_domain.py --seed sh85115114")
        print("  Then: python scripts/backbone/subject/enrich_survey_facets_llm.py -i output/nodes/lcsh_roman_republic.json")
        return 1

    cypher_out = None
    if args.cypher_out:
        cypher_out = args.cypher_out if args.cypher_out.is_absolute() else Path(__file__).resolve().parents[3] / args.cypher_out

    return run_load(survey_path, args.uri, args.user, args.password, args.dry_run, cypher_out)


if __name__ == "__main__":
    sys.exit(main())
