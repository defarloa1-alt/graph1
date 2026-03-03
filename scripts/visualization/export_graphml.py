#!/usr/bin/env python3
"""
Chrystallum GraphML Exporter

Exports Neo4j subgraphs to GraphML format for Cytoscape Desktop and cytoscape.js.
Produces filtered views per ADR-007 person schema:
  - chrystallum_persons_network.graphml   : Person + family/political rels
  - chrystallum_persons_onomastic.graphml : Person + Gens/Praenomen/Nomen/Cognomen/Tribe
  - chrystallum_persons_offices.graphml   : Person + Position + POSITION_HELD
  - chrystallum_geo_roman_republic.graphml: Roman Republic-scoped places
  - chrystallum_full.graphml              : Full graph (streaming, chunked)

Node labels exported as comma-separated string (e.g. "Entity,Person") since
GraphML has no native multi-label support.  The Cytoscape style file maps on
these strings.

Usage:
    python scripts/visualization/export_graphml.py [--filter persons|onomastic|offices|geo|full|all]
"""

import sys
import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "scripts"))

# Load .env from project root (NEO4J_URI, NEO4J_PASSWORD, etc.)
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass  # python-dotenv optional; env vars or config.py still work

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

from neo4j import GraphDatabase

# ---------------------------------------------------------------------------
# GraphML attribute definitions (declared once in <graphml> header)
# ---------------------------------------------------------------------------

NODE_ATTRS = {
    "node_labels":   ("string",  "Labels"),
    "entity_id":     ("string",  "Entity ID"),
    "qid":           ("string",  "Wikidata QID"),
    "label":         ("string",  "Display Label"),
    "label_latin":   ("string",  "Latin Name"),
    "label_dprr":    ("string",  "DPRR Label"),
    "dprr_id":       ("string",  "DPRR ID"),
    "dprr_uri":      ("string",  "DPRR URI"),
    "entity_type":   ("string",  "Entity Type"),
    "entity_cipher": ("string",  "Entity Cipher"),
    "gender":        ("string",  "Gender"),
    "gens_prefix":   ("string",  "Gens Prefix"),
    "abbreviation":  ("string",  "Abbreviation"),
    "label_sort":    ("string",  "Sort Label"),
    "label_en":      ("string",  "English Label"),
    "mythological":  ("boolean", "Mythological"),
    "viaf_id":       ("string",  "VIAF ID"),
    "fast_id":       ("string",  "FAST ID"),
    "lc_id":         ("string",  "LC ID"),
    "nomisma_id":    ("string",  "Nomisma ID"),
    "pleiades_id":   ("string",  "Pleiades ID"),
}

EDGE_ATTRS = {
    "rel_type":             ("string",  "Relationship Type"),
    "source_authority":     ("string",  "Source"),
    "dprr_assertion_uri":   ("string",  "DPRR Assertion URI"),
    "start_year":           ("int",     "Start Year"),
    "end_year":             ("int",     "End Year"),
    "year":                 ("int",     "Year"),
    "year_start":           ("int",     "Year Start"),
    "year_end":             ("int",     "Year End"),
    "secondary_source":     ("string",  "Secondary Source"),
    "confidence":           ("double",  "Confidence"),
}


def _driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


# ---------------------------------------------------------------------------
# Cypher queries for each filtered export
# ---------------------------------------------------------------------------

QUERIES = {
    "persons": {
        "description": "Person network — family, political, civic relations",
        "nodes": """
            MATCH (p:Person)
            OPTIONAL MATCH (p)-[:MEMBER_OF_GENS]->(g:Gens)
            WITH p, g.gens_prefix AS gp
            RETURN p, gp
        """,
        "edges": """
            MATCH (a:Person)-[r]->(b:Person)
            WHERE type(r) IN [
                'FATHER_OF','MOTHER_OF','SIBLING_OF','SPOUSE_OF','CHILD_OF'
            ]
            RETURN a.entity_id AS src, b.entity_id AS tgt, type(r) AS rel,
                   properties(r) AS props
        """,
    },
    "onomastic": {
        "description": "Person + onomastic nodes (Gens, Praenomen, Nomen, Cognomen, Tribe)",
        "nodes": """
            MATCH (n)
            WHERE n:Person OR n:Gens OR n:Praenomen OR n:Nomen
                  OR n:Cognomen OR n:Tribe
            RETURN n
        """,
        "edges": """
            MATCH (a)-[r]->(b)
            WHERE type(r) IN [
                'MEMBER_OF_GENS','HAS_PRAENOMEN','HAS_NOMEN',
                'HAS_COGNOMEN','MEMBER_OF_TRIBE'
            ]
            RETURN a.entity_id AS src,
                   COALESCE(b.entity_id, b.gens_id, b.praenomen_id,
                            b.nomen_id, b.cognomen_id, b.tribe_id) AS tgt,
                   type(r) AS rel, properties(r) AS props
        """,
    },
    "offices": {
        "description": "Person + Position + POSITION_HELD (with temporal properties)",
        "nodes": """
            MATCH (n)
            WHERE n:Person OR n:Position
            RETURN n
        """,
        "edges": """
            MATCH (a:Person)-[r:POSITION_HELD]->(b:Position)
            RETURN a.entity_id AS src, b.entity_id AS tgt,
                   'POSITION_HELD' AS rel, properties(r) AS props
        """,
    },
    "geo": {
        "description": "Roman Republic-scoped places (Place + Pleiades within LOCATED_IN chains)",
        "nodes": """
            MATCH (p:Place)
            WHERE EXISTS { (p)<-[:LOCATED_IN*0..3]-(:Place) }
            RETURN p
            LIMIT 5000
        """,
        "edges": """
            MATCH (a:Place)-[r:LOCATED_IN]->(b:Place)
            RETURN a.entity_id AS src, b.entity_id AS tgt,
                   'LOCATED_IN' AS rel, properties(r) AS props
            LIMIT 10000
        """,
    },
}


def _node_id(node):
    """Extract a stable ID from a Neo4j node."""
    props = dict(node)
    for key in ("entity_id", "gens_id", "praenomen_id", "nomen_id",
                "cognomen_id", "tribe_id", "polity_id"):
        if key in props and props[key]:
            return str(props[key])
    return str(node.element_id)


def _node_labels_str(node):
    """Comma-separated label string for GraphML."""
    return ",".join(sorted(node.labels))


def _safe(val):
    """Coerce value to string safe for GraphML."""
    if val is None:
        return ""
    return str(val)


# ---------------------------------------------------------------------------
# GraphML builder
# ---------------------------------------------------------------------------

class GraphMLBuilder:
    """Builds a GraphML XML document incrementally."""

    def __init__(self):
        self.ns = "http://graphml.graphstruct.org/xmlns"
        self.root = ET.Element("graphml", xmlns=self.ns)
        self._declare_attrs()
        self.graph = ET.SubElement(self.root, "graph",
                                   id="G", edgedefault="directed")
        self._seen_nodes = set()
        self._edge_count = 0

    def _declare_attrs(self):
        for attr_id, (atype, desc) in NODE_ATTRS.items():
            ET.SubElement(self.root, "key", {
                "id": attr_id, "for": "node",
                "attr.name": attr_id, "attr.type": atype,
            })
        for attr_id, (atype, desc) in EDGE_ATTRS.items():
            ET.SubElement(self.root, "key", {
                "id": f"e_{attr_id}", "for": "edge",
                "attr.name": attr_id, "attr.type": atype,
            })

    def add_node(self, node_id: str, labels: str, props: dict,
                 gens_prefix: str = None):
        if node_id in self._seen_nodes:
            return
        self._seen_nodes.add(node_id)
        n = ET.SubElement(self.graph, "node", id=node_id)
        # labels
        d = ET.SubElement(n, "data", key="node_labels")
        d.text = labels
        # properties
        for attr_id in NODE_ATTRS:
            if attr_id == "node_labels":
                continue
            val = props.get(attr_id, "")
            if attr_id == "gens_prefix" and gens_prefix:
                val = gens_prefix
            if val not in (None, ""):
                d = ET.SubElement(n, "data", key=attr_id)
                d.text = _safe(val)

    def add_edge(self, src: str, tgt: str, rel_type: str, props: dict = None):
        if not src or not tgt:
            return
        self._edge_count += 1
        eid = f"e{self._edge_count}"
        e = ET.SubElement(self.graph, "edge",
                          id=eid, source=src, target=tgt)
        d = ET.SubElement(e, "data", key="e_rel_type")
        d.text = rel_type
        if props:
            for attr_id in EDGE_ATTRS:
                if attr_id == "rel_type":
                    continue
                raw_key = attr_id
                # try edge prop keys: source → source_authority
                val = props.get(raw_key) or props.get(
                    "source" if raw_key == "source_authority" else raw_key)
                if val not in (None, ""):
                    d = ET.SubElement(e, "data", key=f"e_{attr_id}")
                    d.text = _safe(val)

    def write(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        rough = ET.tostring(self.root, encoding="unicode", xml_declaration=True)
        dom = minidom.parseString(rough)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(dom.toprettyxml(indent="  "))
        n_nodes = len(self._seen_nodes)
        n_edges = self._edge_count
        size_kb = filepath.stat().st_size / 1024
        print(f"  Written: {filepath}")
        print(f"  Nodes: {n_nodes:,}  Edges: {n_edges:,}  Size: {size_kb:,.0f} KB")


# ---------------------------------------------------------------------------
# Export runners
# ---------------------------------------------------------------------------

def _export_persons(driver, out_dir: Path):
    """Person network with gens_prefix for Compound Spring Embedder grouping."""
    print("\n--- Person Network ---")
    builder = GraphMLBuilder()
    with driver.session(database=NEO4J_DATABASE) as session:
        # Nodes — includes gens_prefix for CSE grouping
        result = session.run(QUERIES["persons"]["nodes"])
        for record in result:
            node = record["p"]
            gp = record.get("gp")
            nid = _node_id(node)
            builder.add_node(nid, _node_labels_str(node), dict(node),
                             gens_prefix=gp)
        # Edges
        result = session.run(QUERIES["persons"]["edges"])
        for record in result:
            builder.add_edge(record["src"], record["tgt"],
                             record["rel"], dict(record["props"] or {}))
    builder.write(out_dir / "chrystallum_persons_network.graphml")


def _export_onomastic(driver, out_dir: Path):
    """Person + onomastic layer."""
    print("\n--- Onomastic Network ---")
    builder = GraphMLBuilder()
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(QUERIES["onomastic"]["nodes"])
        for record in result:
            node = record["n"]
            nid = _node_id(node)
            builder.add_node(nid, _node_labels_str(node), dict(node))
        result = session.run(QUERIES["onomastic"]["edges"])
        for record in result:
            builder.add_edge(record["src"], record["tgt"],
                             record["rel"], dict(record["props"] or {}))
    builder.write(out_dir / "chrystallum_persons_onomastic.graphml")


def _export_offices(driver, out_dir: Path):
    """Person + offices with temporal edge properties."""
    print("\n--- Offices Network ---")
    builder = GraphMLBuilder()
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(QUERIES["offices"]["nodes"])
        for record in result:
            node = record["n"]
            nid = _node_id(node)
            builder.add_node(nid, _node_labels_str(node), dict(node))
        result = session.run(QUERIES["offices"]["edges"])
        for record in result:
            builder.add_edge(record["src"], record["tgt"],
                             record["rel"], dict(record["props"] or {}))
    builder.write(out_dir / "chrystallum_persons_offices.graphml")


def _export_geo(driver, out_dir: Path):
    """Roman Republic-scoped geographic backbone (capped at 5K nodes)."""
    print("\n--- Geo Backbone (Roman Republic scope) ---")
    builder = GraphMLBuilder()
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(QUERIES["geo"]["nodes"])
        for record in result:
            node = record["p"]
            nid = _node_id(node)
            builder.add_node(nid, _node_labels_str(node), dict(node))
        result = session.run(QUERIES["geo"]["edges"])
        for record in result:
            builder.add_edge(record["src"], record["tgt"],
                             record["rel"], dict(record["props"] or {}))
    builder.write(out_dir / "chrystallum_geo_roman_republic.graphml")


def _export_full(driver, out_dir: Path):
    """Full graph export — streamed in chunks to manage memory."""
    print("\n--- Full Graph (streaming) ---")
    builder = GraphMLBuilder()
    with driver.session(database=NEO4J_DATABASE) as session:
        # All nodes in chunks
        print("  Fetching nodes...")
        result = session.run(
            "MATCH (n) WHERE NOT n:SYS_PropertyMapping "
            "AND NOT n:SYS_DecisionRow AND NOT n:SYS_OnboardingStep "
            "RETURN n"
        )
        for record in result:
            node = record["n"]
            nid = _node_id(node)
            builder.add_node(nid, _node_labels_str(node), dict(node))
        # All edges in chunks
        print("  Fetching edges...")
        result = session.run(
            "MATCH (a)-[r]->(b) "
            "WHERE NOT a:SYS_PropertyMapping AND NOT b:SYS_PropertyMapping "
            "AND NOT a:SYS_DecisionRow AND NOT b:SYS_DecisionRow "
            "RETURN a.entity_id AS src_eid, "
            "       COALESCE(a.entity_id, a.gens_id, a.praenomen_id, "
            "                a.nomen_id, a.cognomen_id, a.tribe_id) AS src, "
            "       COALESCE(b.entity_id, b.gens_id, b.praenomen_id, "
            "                b.nomen_id, b.cognomen_id, b.tribe_id) AS tgt, "
            "       type(r) AS rel, properties(r) AS props"
        )
        for record in result:
            builder.add_edge(
                _safe(record["src"]), _safe(record["tgt"]),
                record["rel"], dict(record["props"] or {}),
            )
    builder.write(out_dir / "chrystallum_full.graphml")


EXPORTERS = {
    "persons":   _export_persons,
    "onomastic": _export_onomastic,
    "offices":   _export_offices,
    "geo":       _export_geo,
    "full":      _export_full,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Export Chrystallum graph subsets to GraphML")
    parser.add_argument(
        "--filter", "-f",
        choices=list(EXPORTERS.keys()) + ["all"],
        default="all",
        help="Which subgraph to export (default: all)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output/cytoscape",
        help="Output directory (default: output/cytoscape)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Chrystallum GraphML Exporter")
    print(f"{'='*60}")
    print(f"Output directory: {out_dir}")
    print(f"Filter: {args.filter}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    driver = _driver()
    try:
        if args.filter == "all":
            for name, fn in EXPORTERS.items():
                fn(driver, out_dir)
        else:
            EXPORTERS[args.filter](driver, out_dir)
    finally:
        driver.close()

    print(f"\n{'='*60}")
    print("Export complete.")


if __name__ == "__main__":
    main()
