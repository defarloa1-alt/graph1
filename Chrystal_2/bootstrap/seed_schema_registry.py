#!/usr/bin/env python3
"""Seed SYS_SchemaRegistry + core SYS_NodeType on Chrystal 2.

Thin ship set only — not the full production NodeType dump.
Refuses unless NEO4J_URI hosts 7fe339d2.

Usage (repo root):
  python chrystal_2/bootstrap/seed_schema_registry.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

# (name, domain, description)
CORE_NODE_TYPES: list[tuple[str, str, str]] = [
    # Temporal / facet catalog (already have instances)
    ("Year", "temporal", "Temporal year node (historical backbone; no year 0)"),
    ("Facet", "schema", "Canonical analytical facet (18 keys)"),
    ("FacetRegistry", "schema", "Registry root for the facet catalog"),
    # Domain bootstrap (not instantiated yet)
    ("SubjectDomain", "schema", "The pack: owns bounds, schema, federations, SFA slots (e.g. roman_republic)"),
    ("Domain", "schema", "DEPRECATED in Chrystal 2 — use SubjectDomain only (see TERMINOLOGY.md)"),
    ("SubjectConcept", "schema", "Subject concept / scope under a domain or facet"),
    # Core entity kinds schema specialist may create from WD
    ("Person", "entity", "Prosopographic person"),
    ("Place", "geo", "Geographic location"),
    ("Period", "temporal", "Historical period / polity frame"),
    ("Event", "entity", "Historical event"),
    ("Position", "entity", "Office or magistracy"),
    ("Claim", "claims", "Proposed or promoted claim"),
    ("ProposedEdge", "claims", "Staged edge asserted by a Claim"),
    # Authority / biblio (Librarian)
    ("LCC_Class", "authority", "Library of Congress Classification class"),
    ("LCSH_Heading", "authority", "LCSH subject heading"),
    ("FAST_Heading", "authority", "FAST heading"),
    ("CorpusWork", "bibliography", "Corpus / bibliographic work"),
    # Federation
    ("SYS_FederationRegistry", "infrastructure", "Root registry for federation sources"),
    ("SYS_FederationSource", "infrastructure", "External federation data source"),
    # Self-describing SYS
    ("SYS_SchemaRegistry", "infrastructure", "Root schema registry"),
    ("SYS_NodeType", "infrastructure", "Node type registry entry"),
    ("SYS_RelationshipType", "infrastructure", "Relationship type registry entry"),
    ("SYS_AgentType", "infrastructure", "Agent type classification"),
]


def main() -> int:
    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}")
        return 2

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            session.run(
                """
                MERGE (sr:SYS_SchemaRegistry {system: true})
                SET sr.label = 'SchemaRegistry',
                    sr.instance = 'chrystal_2',
                    sr.version = '0.1',
                    sr.description = $desc
                """,
                desc=(
                    "Chrystal 2 schema registry — node/relationship types allowed "
                    "before and during Domain WD landing."
                ),
            )
            print("SYS_SchemaRegistry: ok")

            for name, domain, desc in CORE_NODE_TYPES:
                session.run(
                    """
                    MERGE (n:SYS_NodeType {name: $name})
                    SET n.domain = $domain,
                        n.description = $desc,
                        n.system = true,
                        n.ship_set = 'chrystal_2_core'
                    WITH n
                    MATCH (sr:SYS_SchemaRegistry {system: true})
                    MERGE (sr)-[:HAS_NODE_TYPE]->(n)
                    """,
                    name=name,
                    domain=domain,
                    desc=desc,
                )
                print(f"  + {name}")

            n_types = session.run("MATCH (n:SYS_NodeType) RETURN count(n) AS c").single()["c"]
            wired = session.run(
                """
                MATCH (:SYS_SchemaRegistry)-[:HAS_NODE_TYPE]->(n:SYS_NodeType)
                RETURN count(n) AS c
                """
            ).single()["c"]
            print(f"SYS_NodeType: {n_types}; HAS_NODE_TYPE: {wired}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
