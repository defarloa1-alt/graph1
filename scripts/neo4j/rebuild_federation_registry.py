#!/usr/bin/env python3
"""
Rebuild FederationRegistry — Replace stale Federation/FederationRoot with SYS_FederationRegistry/SYS_FederationSource.

Run after updating scripts (generate_system_description, sca_agent, validate_changes.cypher).
Spec: docs/FEDERATION_REGISTRY_REBUILD_SPEC.md

Usage:
    python scripts/neo4j/rebuild_federation_registry.py
    python scripts/neo4j/rebuild_federation_registry.py --dry-run
"""

import argparse
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    NEO4J_URI = NEO4J_USERNAME = NEO4J_PASSWORD = NEO4J_DATABASE = None

FEDERATION_SOURCES = [
    {"name": "Wikidata", "status": "operational", "confidence": 0.90, "scoping_role": "discovery_hub", "wikidata_property": "", "license": "CC0", "phase1": True, "phase2": True},
    {"name": "DPRR", "status": "operational", "confidence": 0.85, "scoping_role": "persons", "wikidata_property": "P6863", "license": "CC-BY", "phase1": True, "phase2": True},
    {"name": "Pleiades", "status": "operational", "confidence": 0.92, "scoping_role": "places", "wikidata_property": "P1584", "license": "CC-BY", "phase1": True, "phase2": False},
    {"name": "Trismegistos", "status": "operational", "confidence": 0.95, "scoping_role": "persons/inscriptions", "wikidata_property": "P1696/P4230", "license": "custom", "phase1": True, "phase2": False},
    {"name": "LGPN", "status": "operational", "confidence": 0.93, "scoping_role": "persons", "wikidata_property": "P1047", "license": "custom", "phase1": True, "phase2": False},
    {"name": "PeriodO", "status": "operational", "confidence": 0.85, "scoping_role": "temporal", "wikidata_property": "", "license": "CC0", "phase1": True, "phase2": False},
    {"name": "LCSH/FAST/LCC", "status": "operational", "confidence": 0.90, "scoping_role": "subject_classification", "wikidata_property": "P244/P1014", "license": "CC0", "phase1": True, "phase2": True},
    {"name": "CHRR", "status": "planned", "confidence": None, "scoping_role": "material_evidence", "wikidata_property": "", "license": "ODbL", "phase1": False, "phase2": False},
    {"name": "CRRO", "status": "planned", "confidence": None, "scoping_role": "material_evidence", "wikidata_property": "", "license": "CC-BY", "phase1": False, "phase2": False},
    {"name": "OCD", "status": "planned", "confidence": None, "scoping_role": "taxonomy/grounding", "wikidata_property": "P9106", "license": "public_domain", "phase1": False, "phase2": False},
    {"name": "EDH", "status": "planned", "confidence": None, "scoping_role": "inscriptions", "wikidata_property": "P2192", "license": "CC-BY", "phase1": False, "phase2": False},
    {"name": "VIAF", "status": "partial", "confidence": 0.85, "scoping_role": "persons", "wikidata_property": "P214", "license": "CC0", "phase1": False, "phase2": False},
    {"name": "Getty AAT", "status": "partial", "confidence": 0.90, "scoping_role": "concepts", "wikidata_property": "P1014", "license": "CC-BY", "phase1": False, "phase2": False},
]


def main():
    ap = argparse.ArgumentParser(description="Rebuild FederationRegistry (SYS_FederationRegistry + SYS_FederationSource)")
    ap.add_argument("--dry-run", action="store_true", help="Print queries only, no Neo4j write")
    args = ap.parse_args()

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("NEO4J_URI and NEO4J_PASSWORD required. Set in .env", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("DRY RUN — would execute:")
        print("  Step 1: DETACH DELETE Federation, FederationRoot")
        print("  Step 2: CREATE SYS_FederationRegistry, MERGE Chrystallum-HAS_FEDERATION->registry")
        print(f"  Step 3-4: CREATE {len(FEDERATION_SOURCES)} SYS_FederationSource, MERGE CONTAINS")
        print("  Step 5: SCOPES edges (skipped — EntityType may not exist)")
        return

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"

    with driver.session(database=db) as session:
        # Step 1: Clear stale
        print("[Step 1] Clearing stale Federation and FederationRoot...")
        session.run("MATCH (f:Federation) DETACH DELETE f")
        session.run("MATCH (fr:FederationRoot) DETACH DELETE fr")
        print("  Done.")

        # Step 2: Registry root (use canonical id to avoid duplicate Chrystallum nodes; see docs/CHRYSTALLUM_SUBGRAPH_SPEC.md)
        print("[Step 2] Creating SYS_FederationRegistry...")
        session.run("""
            MERGE (sys:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
            SET sys.label = 'Chrystallum',
                sys.name = 'Chrystallum Knowledge Graph'
            MERGE (fr:SYS_FederationRegistry {system: true, label: "FederationRegistry"})
            MERGE (sys)-[:HAS_FEDERATION]->(fr)
        """)
        print("  Done.")

        # Step 3-4: Create sources and wire
        print(f"[Step 3-4] Creating {len(FEDERATION_SOURCES)} SYS_FederationSource nodes...")
        for fs in FEDERATION_SOURCES:
            session.run("""
                MERGE (fr:SYS_FederationRegistry)
                CREATE (f:SYS_FederationSource {
                    name: $name,
                    status: $status,
                    confidence: $confidence,
                    scoping_role: $scoping_role,
                    wikidata_property: $wikidata_property,
                    license: $license,
                    access_pattern: "api",
                    phase1_complete: $phase1,
                    phase2_complete: $phase2,
                    system: true
                })
                MERGE (fr)-[:CONTAINS]->(f)
            """, **fs)
        print("  Done.")

        # Step 5: SCOPES edges — optional, EntityType may not exist
        # Skip for now; can add later if EntityType nodes exist

        # Validation
        print("\n[Validation]")
        result = session.run("""
            MATCH (sys:Chrystallum)-[:HAS_FEDERATION]->(fr:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
            RETURN f.name AS name, f.status AS status, f.phase1_complete AS phase1
            ORDER BY f.status, f.name
        """)
        rows = result.data()
        print(f"  Rows: {len(rows)}")
        for r in rows[:5]:
            print(f"    {r['name']}: {r['status']}, phase1={r['phase1']}")
        if len(rows) > 5:
            print(f"    ... and {len(rows) - 5} more")

    driver.close()
    print("\nFederationRegistry rebuild complete.")


if __name__ == "__main__":
    main()
