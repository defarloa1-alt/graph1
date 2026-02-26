#!/usr/bin/env python3
"""Audit relationships: Registry vs Database Reality"""

from neo4j import GraphDatabase
import csv

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

output = []

def log(msg):
    output.append(msg)
    print(msg)

# Load relationship registry
registry = {}
with open('Relationships/relationship_types_registry_master.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rel_type = row['relationship_type']
        registry[rel_type] = {
            'wikidata_property': row.get('wikidata_property', ''),
            'cidoc_crm_code': row.get('cidoc_crm_code', ''),
            'lifecycle_status': row.get('lifecycle_status', '')
        }

log("="*80)
log("RELATIONSHIP AUDIT: Registry vs Database")
log("="*80)
log(f"Date: 2026-02-22")
log(f"Registry: {len(registry)} relationship types defined")
log("")

with driver.session() as session:
    # Get all relationship types in database
    result = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        RETURN relationshipType
        ORDER BY relationshipType
    """)
    
    db_rel_types = [r['relationshipType'] for r in result]
    
    log(f"Database: {len(db_rel_types)} relationship types in use")
    log("")
    
    # Count relationships
    log("RELATIONSHIP COUNTS:")
    log("-"*80)
    
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    db_counts = {}
    total_rels = 0
    for r in result:
        rel_type = r['rel_type']
        count = r['count']
        db_counts[rel_type] = count
        total_rels += count
        
        # Check if in registry
        in_registry = "[+]" if rel_type in registry else "[-]"
        log(f"  {in_registry} {rel_type}: {count:,}")
    
    log("")
    log(f"Total relationships in database: {total_rels:,}")
    log("")
    
    # Analysis
    log("COVERAGE ANALYSIS:")
    log("-"*80)
    
    in_registry = sum(1 for rt in db_rel_types if rt in registry)
    not_in_registry = sum(1 for rt in db_rel_types if rt not in registry)
    
    log(f"  Relationship types in database: {len(db_rel_types)}")
    log(f"  In registry: {in_registry} ({in_registry/len(db_rel_types)*100:.1f}%)")
    log(f"  NOT in registry: {not_in_registry} ({not_in_registry/len(db_rel_types)*100:.1f}%)")
    log("")
    
    # Registry coverage
    defined = len(registry)
    implemented_in_db = in_registry
    unused = defined - implemented_in_db
    
    log(f"  Registry contains: {defined} types")
    log(f"  Used in database: {implemented_in_db} ({implemented_in_db/defined*100:.1f}%)")
    log(f"  Defined but unused: {unused} ({unused/defined*100:.1f}%)")
    log("")
    
    # Wikidata crosswalk
    log("WIKIDATA CROSSWALK:")
    log("-"*80)
    
    rels_with_wd_in_db = 0
    for rel_type in db_rel_types:
        if rel_type in registry and registry[rel_type]['wikidata_property']:
            rels_with_wd_in_db += 1
    
    log(f"  DB relationship types with Wikidata PID: {rels_with_wd_in_db}/{len(db_rel_types)} ({rels_with_wd_in_db/len(db_rel_types)*100:.1f}%)")
    log("")
    
    # Entity-to-entity relationships
    log("ENTITY-TO-ENTITY RELATIONSHIPS:")
    log("-"*80)
    
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        LIMIT 20
    """)
    
    entity_rels = 0
    for r in result:
        count = r['count']
        entity_rels += count
        log(f"  {r['rel_type']}: {count}")
    
    log("")
    log(f"Total Entity-to-Entity relationships: {entity_rels}")
    log(f"Entities: 2,600")
    log(f"Avg relationships per entity: {entity_rels/2600:.2f}")
    log("")
    
    # Recommendations
    log("="*80)
    log("RECOMMENDATIONS")
    log("="*80)
    log("")
    log("PRIORITY 1: Import Core Hierarchical Relationships")
    log("  Target relationships:")
    log("    - INSTANCE_OF (P31) - Type classification")
    log("    - SUBCLASS_OF (P279) - Class hierarchy")
    log("    - PART_OF (P361) - Mereological structure")
    log("    - HAS_PART (P527) - Inverse of PART_OF")
    log(f"  Current: {db_counts.get('INSTANCE_OF', 0) + db_counts.get('SUBCLASS_OF', 0) + db_counts.get('PART_OF', 0)}")
    log("  Target: 5,000-8,000 edges")
    log("")
    log("PRIORITY 2: Import Temporal Relationships")
    log("  Target relationships:")
    log("    - BROADER_THAN - Period nesting")
    log("    - SUB_PERIOD_OF - Period hierarchy")
    log(f"  Current: {db_counts.get('BROADER_THAN', 0) + db_counts.get('SUB_PERIOD_OF', 0)}")
    log("  Target: 500-1,000 edges")
    log("")
    log("PRIORITY 3: Import Participatory Relationships")
    log("  Target relationships:")
    log("    - PARTICIPATED_IN (P1344) - Event participation")
    log("    - POSITION_HELD (P39) - Political offices")
    log(f"  Current: Unknown (need to query)")
    log("  Target: 2,000-4,000 edges")
    log("")
    log(f"TOTAL TARGET: 7,500-13,000 edges (vs current {entity_rels})")
    log(f"Ratio target: 3-5 relationships per entity")
    log("")

driver.close()

# Save
with open('output/RELATIONSHIP_AUDIT_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("\n[OK] Relationship audit complete")
print("     Report: output/RELATIONSHIP_AUDIT_REPORT.txt")
