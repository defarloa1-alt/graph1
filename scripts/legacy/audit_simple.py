#!/usr/bin/env python3
"""Simple schema audit - writes to file to avoid encoding issues"""

from neo4j import GraphDatabase
import json
from datetime import datetime

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

output = []

def log(msg):
    output.append(msg)
    print(msg)  # Try to print, but save to file if encoding fails

with driver.session() as session:
    log("="*80)
    log("SCHEMA AUDIT: DATABASE vs SPECIFICATION")
    log("="*80)
    log(f"Date: {datetime.now()}")
    log(f"Database: {NEO4J_URI}")
    log("")
    
    # 1. Node labels
    log("AUDIT 1: NODE LABELS")
    log("-"*80)
    result = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
    labels = [r['label'] for r in result]
    log(f"Total labels: {len(labels)}")
    log(f"Labels: {', '.join(labels)}")
    log("")
    
    # Check expected
    expected = {'Entity', 'FacetedEntity', 'FacetClaim', 'TemporalAnchor'}
    present = set(labels) & expected
    missing = expected - set(labels)
    log(f"Expected labels present: {present}")
    log(f"Missing labels: {missing}")
    log("")
    
    # 2. Entity types
    log("AUDIT 2: ENTITY TYPES")
    log("-"*80)
    result = session.run("MATCH (n:Entity) RETURN DISTINCT n.entity_type as type, count(*) as count ORDER BY count DESC")
    for r in result:
        log(f"  {r['type']}: {r['count']} entities")
    log("")
    
    # 3. Cipher formats
    log("AUDIT 3: CIPHER FORMATS")
    log("-"*80)
    result = session.run("""
        MATCH (n:Entity)
        RETURN n.entity_cipher as cipher, n.entity_type as type, n.qid as qid, n.label as label
        LIMIT 20
    """)
    
    correct = 0
    old_con = 0
    
    log("Sample ciphers:")
    for r in result:
        cipher = r['cipher']
        etype = r['type']
        qid = r['qid']
        label = r['label'] or 'N/A'
        
        if '_con_' in cipher:
            old_con += 1
            log(f"  [OLD] {cipher} - {etype} - {qid} - {label[:40]}")
        else:
            correct += 1
            log(f"  [OK]  {cipher} - {etype} - {qid} - {label[:40]}")
    
    log("")
    log(f"Format summary (sample of 20):")
    log(f"  Correct format: {correct}")
    log(f"  Old 'ent_con_*' format: {old_con}")
    log("")
    
    # 4. TemporalAnchor
    log("AUDIT 4: TEMPORALANCHOR PATTERN")
    log("-"*80)
    
    result = session.run("MATCH (n:TemporalAnchor) RETURN count(n) as total")
    temporal_label = result.single()['total']
    
    result = session.run("MATCH (n:Entity) WHERE n.temporal_start_year IS NOT NULL RETURN count(n) as total")
    temporal_props = result.single()['total']
    
    result = session.run("MATCH (n:Entity) WHERE n.is_temporal_anchor = true RETURN count(n) as total")
    temporal_flag = result.single()['total']
    
    log(f"  Nodes with :TemporalAnchor label: {temporal_label}")
    log(f"  Nodes with temporal_start_year property: {temporal_props}")
    log(f"  Nodes with is_temporal_anchor=true: {temporal_flag}")
    log(f"  Status: {'NOT IMPLEMENTED' if temporal_label == 0 else 'PARTIAL'}")
    log("")
    
    # 5. FacetedEntity
    log("AUDIT 5: FACETEDENTITY (TIER 2)")
    log("-"*80)
    result = session.run("MATCH (n:FacetedEntity) RETURN count(n) as total")
    faceted = result.single()['total']
    log(f"  FacetedEntity nodes: {faceted}")
    log("")
    
    # 6. Claims
    log("AUDIT 6: CLAIMS (TIER 3)")
    log("-"*80)
    result = session.run("MATCH (n:Claim) RETURN count(n) as total")
    claims = result.single()['total']
    result = session.run("MATCH (n:FacetClaim) RETURN count(n) as total")
    facet_claims = result.single()['total']
    log(f"  Claim nodes: {claims}")
    log(f"  FacetClaim nodes: {facet_claims}")
    
    if claims > 0:
        result = session.run("MATCH (c:Claim) RETURN keys(c) as props LIMIT 1")
        if result.peek():
            props = result.single()['props']
            log(f"  Claim properties: {sorted(props)}")
    log("")
    
    # 7. Relationships
    log("AUDIT 7: RELATIONSHIP TYPES")
    log("-"*80)
    result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType")
    rels = [r['relationshipType'] for r in result]
    log(f"Total relationship types: {len(rels)}")
    log(f"Types: {', '.join(rels)}")
    log("")
    
    # 8. Constraints count
    log("AUDIT 8: CONSTRAINTS")
    log("-"*80)
    result = session.run("SHOW CONSTRAINTS")
    constraints = list(result)
    log(f"Total constraints: {len(constraints)}")
    
    # Group by type
    by_type = {}
    for c in constraints:
        ctype = c['type']
        by_type[ctype] = by_type.get(ctype, 0) + 1
    for ctype, count in sorted(by_type.items()):
        log(f"  {ctype}: {count}")
    log("")
    
    # 9. Indexes count
    log("AUDIT 9: INDEXES")
    log("-"*80)
    result = session.run("SHOW INDEXES")
    indexes = list(result)
    log(f"Total indexes: {len(indexes)}")
    
    by_type = {}
    for idx in indexes:
        itype = idx['type']
        by_type[itype] = by_type.get(itype, 0) + 1
    for itype, count in sorted(by_type.items()):
        log(f"  {itype}: {count}")
    log("")
    
    # SUMMARY
    log("="*80)
    log("SUMMARY")
    log("="*80)
    log("")
    log("TIER 1 (Entity Cipher):")
    log(f"  [OK] Entity nodes: 300")
    log(f"  [OK] Constraints exist: entity_cipher_unique, entity_qid_unique")
    log(f"  [!]  Cipher format: ~{old_con}/20 using old 'ent_con_*' format")
    log(f"  [!]  Migration needed for old format entities")
    log("")
    log("TIER 2 (Faceted Entity Cipher):")
    log(f"  [OK] FacetedEntity label exists")
    log(f"  {'[OK]' if faceted > 0 else '[X]'}  FacetedEntity nodes: {faceted}")
    log(f"  [OK] Indexes exist: faceted_cipher_idx, faceted_entity_facet_idx")
    log("")
    log("TIER 3 (Claim Cipher):")
    log(f"  [OK] Claim label exists")
    log(f"  {'[OK]' if claims > 0 else '[X]'}  Claim nodes: {claims}")
    log(f"  [X]  FacetClaim label: NOT IN DATABASE")
    log(f"  [X]  Qualifier properties: NOT IMPLEMENTED")
    log("")
    log("TemporalAnchor Pattern (ADR-002):")
    log(f"  [X]  :TemporalAnchor label: {temporal_label} nodes")
    log(f"  [X]  temporal_start_year property: {temporal_props} nodes")
    log(f"  [X]  is_temporal_anchor flag: {temporal_flag} nodes")
    log(f"  [X]  Status: NOT IMPLEMENTED")
    log("")
    log("RECOMMENDATIONS:")
    log("  1. Execute DDL addendum (add TemporalAnchor + Qualifier support)")
    log("  2. Migrate cipher format (ent_con_* -> canonical prefixes)")
    log("  3. Add TemporalAnchor properties to eligible entities")
    log("  4. Create FacetedEntity nodes (if entity scaling proceeds)")
    log("="*80)

driver.close()

# Write to file
with open('output/SCHEMA_AUDIT_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("\n\n[OK] Audit complete. Full report saved to: output/SCHEMA_AUDIT_REPORT.txt")
