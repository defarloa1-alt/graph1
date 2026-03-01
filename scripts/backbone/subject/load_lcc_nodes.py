#!/usr/bin/env python3
"""
Load LCC classes as Neo4j nodes with hierarchy and facet mapping.

Reads LCC survey JSON (or stubs + lcc_flat), infers parent from range containment,
assigns facets via keyword heuristic, creates LCC_Class nodes with BROADER_THAN
and MAPS_TO_FACET edges.

Schema:
  (:LCC_Class {code, label, prefix, start, end, uri})
  (broader)-[:BROADER_THAN]->(narrower)   // matches LCSH/Period convention
  (lcc)-[:MAPS_TO_FACET {weight}]->(:Facet)

Usage:
  python scripts/backbone/subject/survey_lcc.py --prefix all --out output/nodes/lcc_full.json
  python scripts/backbone/subject/load_lcc_nodes.py --survey output/nodes/lcc_full.json
  python scripts/backbone/subject/load_lcc_nodes.py --cypher-out output/neo4j/lcc_load.cypher  # MCP/cypher-shell
  python scripts/backbone/subject/load_lcc_nodes.py --dry-run

Config: config_loader (.env) or NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD.
"""
import argparse
import json
import os
import re
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

# 18 canonical facets (ADR-004); keyword heuristic for LCC→facet mapping
FACET_KEYWORDS = {
    "ARCHAEOLOGICAL": ["archaeolog", "excavat", "antiquit", "artifact", "inscription"],
    "ARTISTIC": ["art", "sculpture", "painting", "architecture", "literature", "poetry"],
    "BIOGRAPHIC": ["biograph", "person", "family", "gens", "prosopograph"],
    "COMMUNICATION": ["rhetoric", "oratory", "speech", "propaganda", "communication"],
    "CULTURAL": ["culture", "custom", "identity", "romanitas", "ideology", "period", "epoch", "hellenistic"],
    "DEMOGRAPHIC": ["population", "demograph", "census", "migration"],
    "DIPLOMATIC": ["diplomac", "treaty", "embassy", "international", "alliance"],
    "ECONOMIC": ["economic", "trade", "commerce", "agriculture", "land", "finance", "tax"],
    "ENVIRONMENTAL": ["environment", "climate", "geography", "natural"],
    "GEOGRAPHIC": ["geograph", "province", "region", "place", "territory", "expansion"],
    "INTELLECTUAL": ["philosoph", "historiograph", "intellectual", "constitution", "law", "history"],
    "LINGUISTIC": ["language", "latin", "greek", "linguistic"],
    "MILITARY": ["military", "war", "battle", "army", "navy", "campaign", "legion"],
    "POLITICAL": ["politic", "government", "senate", "magistrate", "constitution", "republic", "empire", "regal"],
    "RELIGIOUS": ["religion", "cult", "priest", "ritual", "augur", "temple"],
    "SCIENTIFIC": ["science", "medicine", "astronomy", "mathematic"],
    "SOCIAL": ["social", "society", "patronage", "slavery", "class", "plebeian", "patrician"],
    "TECHNOLOGICAL": ["technology", "engineering", "construction"],
}

LCC_BASE_URI = "https://id.loc.gov/authorities/classification"


def _parse_float(val):
    if val is None or (isinstance(val, str) and not str(val).strip()):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def assign_facets(label: str) -> list[tuple[str, float]]:
    """Return list of (facet_key, weight) from label. Many-to-many."""
    label_lower = (label or "").lower()
    scores = {}
    for facet, keywords in FACET_KEYWORDS.items():
        hits = sum(1 for k in keywords if k in label_lower)
        if hits > 0:
            scores[facet] = min(hits / 3.0, 1.0)  # cap weight
    if not scores:
        return [("INTELLECTUAL", 0.5)]  # LCC default
    total = sum(scores.values())
    return [(f, round(s / total, 2)) for f, s in sorted(scores.items(), key=lambda x: -x[1])]


def infer_parent(code: str, start: float, end: float, prefix: str, by_code: dict) -> str | None:
    """Find narrowest containing range (parent) within same prefix."""
    candidates = []
    for other_code, other in by_code.items():
        if other_code == code:
            continue
        if other.get("prefix", "").upper() != prefix.upper():
            continue
        os_ = other.get("start")
        oe_ = other.get("end")
        if os_ is None or oe_ is None:
            continue
        if os_ <= start and oe_ >= end:
            span = oe_ - os_
            candidates.append((other_code, span))
    if not candidates:
        return None
    # Narrowest containing = smallest span
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]


def load_survey(path: Path) -> list[dict]:
    """Load LCC nodes from FederationSurvey JSON."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    out = []
    for n in nodes:
        code = n.get("id", "")
        label = n.get("label", "")
        props = n.get("properties", {})
        start = _parse_float(props.get("start"))
        end = _parse_float(props.get("end"))
        if start is None and end is None:
            tr = n.get("temporal_range")
            if isinstance(tr, (list, tuple)) and len(tr) >= 2:
                start = _parse_float(tr[0])
                end = _parse_float(tr[1])
        prefix = props.get("prefix", "")
        if not prefix and code:
            m = re.match(r"^([A-Za-z]+)", code)
            prefix = m.group(1) if m else ""
        out.append({
            "code": code,
            "label": label,
            "prefix": prefix,
            "start": start,
            "end": end,
            "uri": n.get("uri") or (f"{LCC_BASE_URI}/{code}" if code else ""),
        })
    return out


BATCH_SIZE = 200  # For Cypher UNWIND and MCP-friendly chunks


def write_cypher_file(nodes: list[dict], by_code: dict, out_path: Path) -> None:
    """Generate .cypher file for MCP run_cypher_mutation or cypher-shell."""
    lines = [
        "// LCC_Class nodes + hierarchy + facet mapping",
        "// Run via MCP run_cypher_mutation or: cypher-shell -f <file>",
        "",
    ]
    # Batch nodes
    for i in range(0, len(nodes), BATCH_SIZE):
        batch = nodes[i : i + BATCH_SIZE]
        rows = [
            {
                "code": n["code"],
                "label": n["label"],
                "prefix": n.get("prefix", ""),
                "start": n.get("start"),
                "end": n.get("end"),
                "uri": n.get("uri", ""),
            }
            for n in batch
        ]
        param = json.dumps(rows)
        lines.append(f"UNWIND {param} AS row")
        lines.append("MERGE (l:LCC_Class {code: row.code})")
        lines.append("SET l.label = row.label, l.prefix = row.prefix, l.start = row.start, l.end = row.end, l.uri = row.uri;")
        lines.append("")

    # BROADER_THAN edges
    edges = [(n["code"], n["primary_parent"]) for n in nodes if n.get("primary_parent") and n["primary_parent"] in by_code]
    for i in range(0, len(edges), BATCH_SIZE):
        batch = edges[i : i + BATCH_SIZE]
        rows = [{"child": c, "parent": p} for c, p in batch]
        param = json.dumps(rows)
        lines.append(f"UNWIND {param} AS row")
        lines.append("MATCH (child:LCC_Class {code: row.child})")
        lines.append("MATCH (parent:LCC_Class {code: row.parent})")
        lines.append("MERGE (parent)-[:BROADER_THAN]->(child);")
        lines.append("")

    # MAPS_TO_FACET edges
    facet_edges = []
    for n in nodes:
        for fk, w in n.get("facets", []):
            facet_edges.append({"code": n["code"], "facet_key": fk, "weight": w})
    for i in range(0, len(facet_edges), BATCH_SIZE):
        batch = facet_edges[i : i + BATCH_SIZE]
        rows = batch
        param = json.dumps(rows)
        lines.append(f"UNWIND {param} AS row")
        lines.append("MATCH (l:LCC_Class {code: row.code})")
        lines.append("MATCH (f:CanonicalFacet {key: row.facet_key})")
        lines.append("MERGE (l)-[r:MAPS_TO_FACET]->(f)")
        lines.append("SET r.weight = row.weight;")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[LCC] Wrote Cypher to {out_path} ({len(nodes)} nodes, batched)")


def run_load(survey_path: Path, uri: str, user: str, password: str, dry_run: bool, cypher_out: Path | None) -> int:
    if not GraphDatabase:
        print("ERROR: neo4j package required. pip install neo4j")
        return 1

    nodes = load_survey(survey_path)
    if not nodes:
        print("ERROR: No nodes in survey")
        return 1

    by_code = {n["code"]: n for n in nodes}
    for n in nodes:
        parent = infer_parent(
            n["code"], n.get("start") or 0, n.get("end") or 0,
            n.get("prefix", ""), by_code
        )
        n["primary_parent"] = parent
        n["facets"] = assign_facets(n["label"])

    if dry_run:
        print("DRY RUN — would create:")
        for n in nodes[:10]:
            print(f"  {n['code']}: parent={n['primary_parent']} facets={[f[0] for f in n['facets'][:3]]}")
        print(f"  ... and {len(nodes) - 10} more")
        return 0

    if cypher_out:
        write_cypher_file(nodes, by_code, cypher_out)
        print(f"[LCC] Loaded {len(nodes)} nodes -> Cypher file (run via MCP or cypher-shell)")
        return 0

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        # Ensure Facet nodes exist (match on key)
        facet_keys = set()
        for n in nodes:
            for fk, _ in n["facets"]:
                facet_keys.add(fk)

        created = 0
        for n in nodes:
            session.run("""
                MERGE (l:LCC_Class {code: $code})
                SET l.label = $label,
                    l.prefix = $prefix,
                    l.start = $start,
                    l.end = $end,
                    l.uri = $uri
            """, {
                "code": n["code"],
                "label": n["label"],
                "prefix": n.get("prefix", ""),
                "start": n.get("start"),
                "end": n.get("end"),
                "uri": n.get("uri", ""),
            })
            created += 1

        # BROADER_THAN edges: (broader)-[:BROADER_THAN]->(narrower), matches LCSH/Period convention
        for n in nodes:
            parent = n.get("primary_parent")
            if parent and parent in by_code:
                session.run("""
                    MATCH (child:LCC_Class {code: $child})
                    MATCH (parent:LCC_Class {code: $parent})
                    MERGE (parent)-[:BROADER_THAN]->(child)
                """, {"child": n["code"], "parent": parent})

        # MAPS_TO_FACET edges (link to canonical Facet by key)
        for n in nodes:
            for facet_key, weight in n["facets"]:
                session.run("""
                    MATCH (l:LCC_Class {code: $code})
                    MATCH (f:CanonicalFacet {key: $facet_key})
                    MERGE (l)-[r:MAPS_TO_FACET]->(f)
                    SET r.weight = $weight
                """, {"code": n["code"], "facet_key": facet_key, "weight": weight})

    driver.close()
    print(f"[LCC] Loaded {created} LCC_Class nodes with hierarchy and facet mapping")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Load LCC nodes to Neo4j with hierarchy and facets")
    parser.add_argument("--survey", type=Path, default=Path("output/nodes/lcc_roman_republic.json"))
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
        print("  Run: python scripts/backbone/subject/survey_lcc.py [--prefix all --out output/nodes/lcc_full.json]")
        return 1

    cypher_out = None
    if args.cypher_out:
        cypher_out = args.cypher_out if args.cypher_out.is_absolute() else Path(__file__).resolve().parents[3] / args.cypher_out

    return run_load(survey_path, args.uri, args.user, args.password, args.dry_run, cypher_out)


if __name__ == "__main__":
    raise SystemExit(main())
