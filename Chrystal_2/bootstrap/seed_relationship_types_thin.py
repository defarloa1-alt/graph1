#!/usr/bin/env python3
"""Seed thin SYS_RelationshipType set for Chrystal 2 bootstrap.

Loads matching rows from relationship_types_registry_master.csv plus
minimal stubs for system/temporal/authority edges missing from the CSV.

Refuses unless NEO4J_URI hosts 7fe339d2.

Usage (repo root):
  python chrystal_2/bootstrap/seed_relationship_types_thin.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

CSV_PATH = ROOT / "Relationships" / "relationship_types_registry_master.csv"

# Curated allowlist — Domain WD landing + schema spine (not full 600+)
ALLOWLIST: set[str] = {
    # Typing / structure
    "INSTANCE_OF",
    "TYPE_OF",
    "PART_OF",
    "HAS_PART",
    "DIFFERENT_FROM",
    "DESCRIBED_BY_SOURCE",
    # Polity / succession (Republic seed)
    "FOLLOWS",
    "FOLLOWED_BY",
    "REPLACES",
    "REPLACED_BY",
    "SUCCEEDED_BY",
    "SUCCESSOR_OF",
    "HAS_CAPITAL",
    "CAPITAL",
    "CITIZEN_OF",
    "HAS_OFFICIAL_LANGUAGE",
    "HAS_OFFICIAL_RELIGION",
    "HAS_CURRENCY",
    "HAS_LEGISLATIVE_BODY",
    "BASIC_FORM_OF_GOVERNMENT",
    "SIGNIFICANT_EVENT",
    "TIME_PERIOD",
    # Temporal
    "STARTS_IN_YEAR",
    "ENDS_IN_YEAR",
    "BORN_IN_YEAR",
    "DIED_IN_YEAR",
    "OCCURS_DURING",
    "IN_PERIOD",
    # Geo
    "BORN_IN_PLACE",
    "DIED_IN_PLACE",
    "LOCATED_IN",
    "ON_CONTINENT",
    # Familia / career / onomastics
    "CHILD_OF",
    "FATHER_OF",
    "MOTHER_OF",
    "SPOUSE_OF",
    "SIBLING_OF",
    "POSITION_HELD",
    "PARTICIPATED_IN",
    "MEMBER_OF_GENS",
    "HAS_PRAENOMEN",
    "HAS_COGNOMEN",
    "MEMBER_OF",
    # Authority / identity
    "HAS_VIAF",
    "HAS_GND",
    "HAS_LCNAF",
    "HAS_FAST",
    "HAS_FAST_AUTHORITY",
    "HAS_LCSH_AUTHORITY",
    "ALIGNED_WITH_LCC",
    "SAME_AS",
    # Claims track
    "ASSERTS_EDGE",
    "IN_SCOPE",
    "FROM",
    "TO",
    # Schema / catalog
    "CONTAINS",
    "HAS_NODE_TYPE",
    "HAS_RELATIONSHIP_TYPE",
    "HAS_AGENT_TYPE",
    "HAS_FACET",
    "SEED_FOR",
}

# Stubs when CSV has no row (system / temporal / authority)
STUBS: dict[str, dict[str, str]] = {
    "FOLLOWED_BY": {
        "category": "Temporal",
        "description": "Year sequence / polity succession (context-dependent)",
        "lifecycle_status": "implemented",
    },
    "STARTS_IN_YEAR": {
        "category": "Temporal",
        "description": "Entity or period starts in Year",
        "lifecycle_status": "implemented",
    },
    "ENDS_IN_YEAR": {
        "category": "Temporal",
        "description": "Entity or period ends in Year",
        "lifecycle_status": "implemented",
    },
    "BORN_IN_YEAR": {
        "category": "Temporal",
        "description": "Person born in Year",
        "lifecycle_status": "implemented",
    },
    "DIED_IN_YEAR": {
        "category": "Temporal",
        "description": "Person died in Year",
        "lifecycle_status": "implemented",
    },
    "OCCURS_DURING": {
        "category": "Temporal",
        "description": "SubjectDomain or entity occurs during Period",
        "lifecycle_status": "implemented",
    },
    "IN_PERIOD": {
        "category": "Temporal",
        "description": "Place/event situated in Period (not Person membership)",
        "lifecycle_status": "implemented",
    },
    "HAS_VIAF": {
        "category": "Authority",
        "description": "Person/entity has VIAF id node",
        "wikidata_property": "P214",
        "lifecycle_status": "implemented",
    },
    "HAS_GND": {
        "category": "Authority",
        "description": "Has GND id node",
        "wikidata_property": "P227",
        "lifecycle_status": "implemented",
    },
    "HAS_LCNAF": {
        "category": "Authority",
        "description": "Has LCNAF id node",
        "wikidata_property": "P244",
        "lifecycle_status": "implemented",
    },
    "HAS_FAST": {
        "category": "Authority",
        "description": "Person identity FAST heading",
        "wikidata_property": "P2163",
        "lifecycle_status": "implemented",
    },
    "HAS_FAST_AUTHORITY": {
        "category": "Authority",
        "description": "SubjectDomain or SubjectConcept aboutness FAST tether (may be soft facet)",
        "lifecycle_status": "implemented",
    },
    "HAS_LCSH_AUTHORITY": {
        "category": "Authority",
        "description": "SubjectDomain or SubjectConcept aboutness LCSH tether",
        "lifecycle_status": "implemented",
    },
    "ALIGNED_WITH_LCC": {
        "category": "Authority",
        "description": "Domain or SC aligned with LCC class",
        "lifecycle_status": "implemented",
    },
    "SAME_AS": {
        "category": "Authority",
        "description": "Identity alignment between authority nodes",
        "lifecycle_status": "implemented",
    },
    "ASSERTS_EDGE": {
        "category": "Claims",
        "description": "Claim asserts a ProposedEdge",
        "lifecycle_status": "implemented",
    },
    "IN_SCOPE": {
        "category": "Claims",
        "description": "Claim scoped to SubjectConcept",
        "lifecycle_status": "implemented",
    },
    "FROM": {
        "category": "Claims",
        "description": "ProposedEdge source endpoint",
        "lifecycle_status": "implemented",
    },
    "TO": {
        "category": "Claims",
        "description": "ProposedEdge target endpoint",
        "lifecycle_status": "implemented",
    },
    "CONTAINS": {
        "category": "System",
        "description": "Registry or parent contains child",
        "lifecycle_status": "implemented",
    },
    "HAS_NODE_TYPE": {
        "category": "System",
        "description": "SchemaRegistry → SYS_NodeType",
        "lifecycle_status": "implemented",
    },
    "HAS_RELATIONSHIP_TYPE": {
        "category": "System",
        "description": "SchemaRegistry → SYS_RelationshipType",
        "lifecycle_status": "implemented",
    },
    "HAS_AGENT_TYPE": {
        "category": "System",
        "description": "SchemaRegistry → SYS_AgentType",
        "lifecycle_status": "implemented",
    },
    "HAS_FACET": {
        "category": "System",
        "description": "Entity or assessment linked to Facet",
        "lifecycle_status": "implemented",
    },
    "SEED_FOR": {
        "category": "System",
        "description": "SubjectDomain seed link to versioned Domain",
        "lifecycle_status": "implemented",
    },
}


def load_csv_rows() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rt = (row.get("relationship_type") or "").strip()
            if rt in ALLOWLIST and rt not in out:
                out[rt] = row
    return out


def main() -> int:
    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}")
        return 2
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}")
        return 2

    from_csv = load_csv_rows()
    print(f"From CSV: {len(from_csv)}; stubs needed: {len(ALLOWLIST - set(from_csv))}")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            session.run(
                """
                MERGE (sr:SYS_SchemaRegistry {system: true})
                SET sr.label = coalesce(sr.label, 'SchemaRegistry')
                """
            )

            for rt in sorted(ALLOWLIST):
                if rt in from_csv:
                    row = from_csv[rt]
                    session.run(
                        """
                        MERGE (n:SYS_RelationshipType {rel_type: $rt})
                        SET n.name = $rt,
                            n.category = $category,
                            n.description = $description,
                            n.wikidata_property = $pid,
                            n.directionality = $directionality,
                            n.status = $status,
                            n.lifecycle_status = $lifecycle,
                            n.ship_set = 'chrystal_2_thin',
                            n.source = 'relationship_types_registry_master.csv'
                        WITH n
                        MATCH (sr:SYS_SchemaRegistry {system: true})
                        MERGE (sr)-[:HAS_RELATIONSHIP_TYPE]->(n)
                        """,
                        rt=rt,
                        category=(row.get("category") or "").strip() or None,
                        description=(row.get("description") or "").strip() or None,
                        pid=(row.get("wikidata_property") or "").strip() or None,
                        directionality=(row.get("directionality") or "").strip() or None,
                        status=(row.get("status") or "active").strip(),
                        lifecycle=(row.get("lifecycle_status") or "implemented").strip(),
                    )
                    src = "csv"
                else:
                    stub = STUBS.get(rt, {})
                    session.run(
                        """
                        MERGE (n:SYS_RelationshipType {rel_type: $rt})
                        SET n.name = $rt,
                            n.category = $category,
                            n.description = $description,
                            n.wikidata_property = $pid,
                            n.status = 'active',
                            n.lifecycle_status = $lifecycle,
                            n.ship_set = 'chrystal_2_thin',
                            n.source = 'chrystal_2_stub'
                        WITH n
                        MATCH (sr:SYS_SchemaRegistry {system: true})
                        MERGE (sr)-[:HAS_RELATIONSHIP_TYPE]->(n)
                        """,
                        rt=rt,
                        category=stub.get("category"),
                        description=stub.get("description"),
                        pid=stub.get("wikidata_property"),
                        lifecycle=stub.get("lifecycle_status", "implemented"),
                    )
                    src = "stub"
                print(f"  + {rt:28} [{src}]")

            n = session.run(
                "MATCH (n:SYS_RelationshipType) RETURN count(n) AS c"
            ).single()["c"]
            wired = session.run(
                """
                MATCH (:SYS_SchemaRegistry)-[:HAS_RELATIONSHIP_TYPE]->(n:SYS_RelationshipType)
                RETURN count(n) AS c
                """
            ).single()["c"]
            print(f"SYS_RelationshipType: {n}; HAS_RELATIONSHIP_TYPE: {wired}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
