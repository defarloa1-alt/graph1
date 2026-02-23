#!/usr/bin/env python3
"""
Comprehensive Neo4j Schema Audit

Find:
1. Legacy node types (should be migrated/removed)
2. Legacy relationship types (no longer needed)
3. Thin/incorrect node attributes
4. Thin/incorrect relationship attributes
"""

from neo4j import GraphDatabase
from collections import Counter, defaultdict

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

output = []

def log(msg):
    output.append(msg)
    print(msg)

log("="*80)
log("NEO4J SCHEMA AUDIT - Legacy & Thin Attributes")
log("="*80)
log("")

with driver.session() as session:
    # 1. All node labels
    log("1. NODE LABELS (All types)")
    log("-"*80)
    result = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
    all_labels = [r['label'] for r in result]
    log(f"Total labels: {len(all_labels)}")
    log("")
    
    # Categorize labels
    domain_labels = ['Entity', 'FacetedEntity', 'FacetClaim']
    legacy_entity_labels = ['Human', 'Organization', 'Period', 'Place', 'Event', 'Work', 'Material', 'Object']
    meta_labels = ['Chrystallum', 'Federation', 'EntityType', 'Facet', 'SubjectConcept', 'Agent', 'Schema']
    infrastructure_labels = ['Year', 'Decade', 'Century', 'Millennium']
    
    log("DOMAIN LABELS (Current architecture):")
    for label in domain_labels:
        if label in all_labels:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = result.single()['count']
            log(f"  {label}: {count:,} nodes")
    log("")
    
    log("LEGACY ENTITY LABELS (Should be migrated to :Entity?):")
    for label in legacy_entity_labels:
        if label in all_labels:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = result.single()['count']
            if count > 0:
                log(f"  {label}: {count:,} nodes [LEGACY]")
    log("")
    
    log("META-MODEL LABELS (System structure):")
    for label in meta_labels:
        if label in all_labels:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = result.single()['count']
            log(f"  {label}: {count:,} nodes")
    log("")
    
    # 2. Node attribute analysis
    log("2. ENTITY NODE ATTRIBUTES")
    log("-"*80)
    result = session.run("""
        MATCH (e:Entity)
        WITH keys(e) as props, count(*) as node_count
        RETURN props, node_count
        ORDER BY node_count DESC
        LIMIT 10
    """)
    
    log("Most common Entity property sets (top 10):")
    for r in result:
        props = sorted(r['props'])
        count = r['node_count']
        log(f"  {count:,} nodes with properties: {props[:10]}...")
    log("")
    
    # Check for required properties
    log("Required property coverage:")
    for prop in ['qid', 'entity_cipher', 'entity_type', 'label']:
        result = session.run(f"""
            MATCH (e:Entity)
            WITH count(e) as total,
                 count(e.{prop}) as has_prop
            RETURN total, has_prop, (has_prop * 100.0 / total) as coverage
        """)
        r = result.single()
        log(f"  {prop}: {r['has_prop']:,}/{r['total']:,} ({r['coverage']:.1f}%)")
    log("")
    
    # 3. Relationship attribute analysis
    log("3. RELATIONSHIP ATTRIBUTES")
    log("-"*80)
    
    # Sample P-type edges
    result = session.run("""
        MATCH ()-[r:P31]->()
        WITH keys(r) as props
        RETURN DISTINCT props
        LIMIT 1
    """)
    
    if result.peek():
        p31_props = result.single()['props']
        log(f"P31 edge properties: {p31_props}")
    else:
        log("P31 edge properties: (no edges found)")
    
    # Sample other edges
    result = session.run("""
        MATCH ()-[r:WIKIDATA_P31]->()
        WITH keys(r) as props  
        RETURN DISTINCT props
        LIMIT 1
    """)
    
    if result.peek():
        wiki_p31_props = result.single()['props']
        log(f"WIKIDATA_P31 edge properties: {wiki_p31_props}")
    else:
        log("WIKIDATA_P31: (no edges found)")
    log("")
    
    # 4. Orphaned/unused labels
    log("4. LABELS WITH ZERO NODES (Orphaned)")
    log("-"*80)
    orphaned = []
    for label in all_labels:
        result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
        count = result.single()['count']
        if count == 0:
            orphaned.append(label)
    
    if orphaned:
        log(f"Found {len(orphaned)} orphaned labels:")
        for label in orphaned[:20]:
            log(f"  {label}")
        if len(orphaned) > 20:
            log(f"  ... and {len(orphaned) - 20} more")
    else:
        log("No orphaned labels found")
    log("")
    
    # 5. Relationship types categorization
    log("5. RELATIONSHIP TYPE CATEGORIES")
    log("-"*80)
    result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
    all_rel_types = [r['relationshipType'] for r in result]
    
    wikidata_p = [t for t in all_rel_types if t.startswith('WIKIDATA_P')]
    clean_p = [t for t in all_rel_types if t.startswith('P') and t[1:2].isdigit() and not t.startswith('WIKIDATA')]
    meta = [t for t in all_rel_types if t.startswith('HAS_')]
    canonical = [t for t in all_rel_types if t in ['INSTANCE_OF', 'SUBCLASS_OF', 'PART_OF', 'HAS_PART']]
    other = [t for t in all_rel_types if t not in wikidata_p + clean_p + meta + canonical]
    
    log(f"WIKIDATA_P* (with prefix): {len(wikidata_p)}")
    if wikidata_p:
        log(f"  Sample: {wikidata_p[:5]}")
    
    log(f"Clean P* (no prefix): {len(clean_p)}")
    if clean_p:
        log(f"  Sample: {clean_p[:5]}")
    
    log(f"Meta-model (HAS_*): {len(meta)}")
    log(f"Canonical (renamed): {len(canonical)}")
    log(f"Other: {len(other)}")
    if other:
        log(f"  Sample: {other[:10]}")
    log("")

driver.close()

# Save
with open('output/schema_audit_cleanup.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print()
print("="*80)
print("Saved: output/schema_audit_cleanup.txt")
print("="*80)
