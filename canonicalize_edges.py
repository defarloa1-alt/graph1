#!/usr/bin/env python3
"""
Canonicalize PID Edges - Add Semantic Properties

Stamp canonical properties on existing PID edges:
- canonical_type (INSTANCE_OF, PART_OF, etc.)
- canonical_category (Hierarchical, Temporal, etc.)
- cidoc_crm_property
- in_registry flag

Preserves Wikidata structure (PIDs remain as edge types).
Adds our semantic interpretation layer as properties.
"""

import csv
from neo4j import GraphDatabase
from datetime import datetime

# Neo4j connection
driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

print("="*80)
print("EDGE CANONICALIZATION - Add Semantic Properties")
print("="*80)
print(f"Start: {datetime.now()}")
print()

# Load relationship registry
print("Loading relationship registry...")
registry = {}

with open('Relationships/relationship_types_registry_master.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row.get('wikidata_property', '').strip()
        if not pid:
            continue
        
        registry[pid] = {
            'canonical_type': row.get('relationship_type', '').strip(),
            'category': row.get('category', '').strip(),
            'cidoc_crm': row.get('cidoc_crm_code', '').strip(),
            'lifecycle': row.get('lifecycle_status', '').strip()
        }

print(f"  Registry loaded: {len(registry)} PID mappings")
print()

# Get all PID edge types in database
print("Querying edge types in database...")
with driver.session() as session:
    result = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        WHERE relationshipType STARTS WITH 'P'
        RETURN relationshipType as pid
        ORDER BY pid
    """)
    
    db_pids = [r['pid'] for r in result]

print(f"  PID edge types in database: {len(db_pids)}")
print()

# Canonicalize each PID
print("Stamping canonical properties on edges...")
print()

stamped = 0
skipped = 0

for pid in db_pids:
    if pid in registry:
        mapping = registry[pid]
        
        with driver.session() as session:
            result = session.run(f"""
                MATCH ()-[r:{pid}]->()
                SET r.canonical_type = $canonical_type,
                    r.canonical_category = $category,
                    r.cidoc_crm_property = $cidoc_crm,
                    r.in_registry = true,
                    r.canonicalized_at = datetime()
                RETURN count(r) as updated
            """, 
            canonical_type=mapping['canonical_type'],
            category=mapping['category'],
            cidoc_crm=mapping['cidoc_crm'])
            
            count = result.single()['updated']
            stamped += count
            
            if (db_pids.index(pid) + 1) % 50 == 0:
                print(f"  Progress: {db_pids.index(pid) + 1}/{len(db_pids)} PIDs processed, {stamped:,} edges stamped")
    else:
        # Not in registry - mark as unmapped
        with driver.session() as session:
            result = session.run(f"""
                MATCH ()-[r:{pid}]->()
                SET r.in_registry = false,
                    r.needs_mapping = true
                RETURN count(r) as updated
            """)
            
            count = result.single()['updated']
            skipped += count

driver.close()

print()
print("="*80)
print("CANONICALIZATION COMPLETE")
print("="*80)
print(f"End: {datetime.now()}")
print()
print(f"Edges stamped with canonical properties: {stamped:,}")
print(f"Edges marked unmapped: {skipped:,}")
print(f"Total edges processed: {stamped + skipped:,}")
print()
print("Canonical properties added:")
print("  - canonical_type (INSTANCE_OF, PART_OF, etc.)")
print("  - canonical_category (Hierarchical, Temporal, etc.)")
print("  - cidoc_crm_property")
print("  - in_registry (true/false)")
print()
print("Query example:")
print("  MATCH ()-[r]->() WHERE r.canonical_type = 'INSTANCE_OF' RETURN count(r)")
print()
