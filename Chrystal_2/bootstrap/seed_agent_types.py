#!/usr/bin/env python3
"""Seed SYS_AgentType nodes for Chrystal 2 (minimal set).

Types: Domain, SchemaSpecialist, Librarian, SFA, Validation
No separate SCA agent — SubjectConcepts are graph nodes; Domain owns lifecycle.
Refuses unless NEO4J_URI hosts 7fe339d2.

Usage (repo root):
  python chrystal_2/bootstrap/seed_agent_types.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

# (name, label, description)
AGENT_TYPES: list[tuple[str, str, str]] = [
    (
        "DOMAIN",
        "Domain Agent",
        "Owns a SubjectDomain pack end-to-end: bootstrap (new-pack request, "
        "pack library, schema/Librarian handoff, federations, inert SFA slots) "
        "and ongoing lifecycle. SubjectConcepts are granular graph nodes under "
        "the pack — not a separate agent type.",
    ),
    (
        "SCHEMA_SPECIALIST",
        "Neo Schema Specialist",
        "Graph-design specialist: decides property on SubjectDomain vs "
        "first-class node+rel; writes only via SYS_NodeType / "
        "SYS_RelationshipType. Reusable across packs (Republic, Meiji, …).",
    ),
    (
        "LIBRARIAN",
        "Librarian",
        "Places a SubjectDomain in the bibliographic universe from external "
        "IDs (LCSH/FAST/LCC/VIAF). Owns aboutness tethers; subject backbone may "
        "be partial.",
    ),
    (
        "SFA",
        "Subject Facet Agent",
        "Facet specialist. Slot nodes created at SubjectDomain schema time; "
        "agents activate later under Domain lifecycle.",
    ),
    (
        "VALIDATION",
        "Validation Agent",
        "Runs SYS_ValidationRule / registry checks; reports integrity issues.",
    ),
]

# Removed from Chrystal 2 minimal set (revisit if needed)
REMOVED = ("SCA",)


def main() -> int:
    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}")
        return 2

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            for name in REMOVED:
                deleted = session.run(
                    """
                    OPTIONAL MATCH (a:SYS_AgentType {name: $name})
                    DETACH DELETE a
                    RETURN count(a) AS c
                    """,
                    name=name,
                ).single()["c"]
                if deleted:
                    print(f"  - removed {name}")

            for name, label, desc in AGENT_TYPES:
                session.run(
                    """
                    MERGE (a:SYS_AgentType {name: $name})
                    SET a.label = $label,
                        a.description = $desc,
                        a.system = true,
                        a.ship_set = 'chrystal_2_core',
                        a.instance = 'chrystal_2'
                    WITH a
                    OPTIONAL MATCH (sr:SYS_SchemaRegistry {system: true})
                    FOREACH (_ IN CASE WHEN sr IS NULL THEN [] ELSE [1] END |
                      MERGE (sr)-[:HAS_AGENT_TYPE]->(a)
                    )
                    """,
                    name=name,
                    label=label,
                    desc=desc,
                )
                print(f"  + {name} ({label})")

            n = session.run("MATCH (a:SYS_AgentType) RETURN count(a) AS c").single()["c"]
            names = session.run(
                """
                MATCH (a:SYS_AgentType)
                RETURN collect(a.name) AS names
                """
            ).single()["names"]
            print(f"SYS_AgentType: {n} → {sorted(names)}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
