#!/usr/bin/env python3
"""
Remove WIKIDATA_ Prefix from Relationship Types

Renames: WIKIDATA_P31 → P31, WIKIDATA_P361 → P361, etc.
Preserves all edge properties.
Processes in batches for performance.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from neo4j import GraphDatabase
from datetime import datetime

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", os.environ.get("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

if not NEO4J_PASSWORD:
    print("Error: NEO4J_PASSWORD not set. Use .env or config_loader.")
    sys.exit(1)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

print("="*80)
print("REMOVE WIKIDATA_ PREFIX FROM EDGES")
print("="*80)
print(f"Start: {datetime.now()}")
print()

# Get all WIKIDATA_P* relationship types
with driver.session() as session:
    result = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        WHERE relationshipType STARTS WITH 'WIKIDATA_P'
        RETURN relationshipType as old_type
        ORDER BY old_type
    """)
    
    wikidata_rel_types = [r['old_type'] for r in result]

print(f"Relationship types to rename: {len(wikidata_rel_types)}")
print()

total_renamed = 0

for old_type in wikidata_rel_types:
    new_type = old_type.replace('WIKIDATA_', '')
    
    print(f"Renaming: {old_type} -> {new_type}...")
    
    # Process in batches (Neo4j can't rename relationship types directly)
    with driver.session() as session:
        # Count edges to rename
        result = session.run(f"""
            MATCH ()-[r:{old_type}]->()
            RETURN count(r) as total
        """)
        total = result.single()['total']
        
        if total == 0:
            print(f"  No edges found")
            continue

        # Rename in batches until none remain (handles >10k edges per type)
        type_renamed = 0
        while True:
            result = session.run(f"""
                MATCH (a)-[old:{old_type}]->(b)
                WITH a, old, b, properties(old) as props
                LIMIT 10000
                CALL apoc.create.relationship(a, '{new_type}', props, b)
                YIELD rel
                DELETE old
                RETURN count(rel) as renamed
            """)
            renamed = result.single()['renamed']
            type_renamed += renamed
            if renamed == 0:
                break
        total_renamed += type_renamed
        print(f"  Renamed: {type_renamed:,} edges")

driver.close()

print()
print("="*80)
print("CLEANUP COMPLETE")
print("="*80)
print(f"End: {datetime.now()}")
print()
print(f"Total edges renamed: {total_renamed:,}")
print()
print("Verification:")
print("  MATCH ()-[r]->() WHERE type(r) STARTS WITH 'WIKIDATA_'")
print("  RETURN count(r)")
print("  // Should return 0")
print()
print("New edge types:")
print("  :P31, :P361, :P39, :P279, :P607, etc.")
print()
