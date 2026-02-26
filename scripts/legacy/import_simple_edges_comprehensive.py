#!/usr/bin/env python3
"""
Import Simple Entity-to-Entity Edges (Bucket 2)

Import 114,292 simple edges from checkpoint using mechanical classification.
Uses Wikidata PIDs as relationship types (WIKIDATA_P31, WIKIDATA_P361, etc.)

Expected improvement: 784 → 114,292 edges (145x)
"""

import json
from neo4j import GraphDatabase
from datetime import datetime

# Cipher-eligible qualifiers
CIPHER_ELIGIBLE_QUALIFIERS = {"P580", "P582", "P585", "P276", "P1545"}

# Neo4j connection
NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("="*80)
print("COMPREHENSIVE SIMPLE EDGE IMPORT")
print("="*80)
print(f"Start: {datetime.now()}")
print()

# Load checkpoint
checkpoint_file = 'output/checkpoints/QQ17167_checkpoint_20260221_061318.json'
print(f"Loading: {checkpoint_file}")

with open(checkpoint_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

entities = data.get('entities', {})
all_qids = set(entities.keys())

print(f"Entities: {len(entities):,}")
print(f"QID set: {len(all_qids):,}")
print()

# Collect edges
edges = []
skipped_no_target = 0
skipped_has_qualifiers = 0
skipped_not_entityid = 0

print("Classifying claims...")
for qid_from, entity in entities.items():
    claims = entity.get('claims', {})
    
    for prop_id, prop_claims in claims.items():
        for claim in prop_claims:
            mainsnak = claim.get('mainsnak', {})
            datavalue = mainsnak.get('datavalue', {})
            datatype = datavalue.get('type', '')
            
            # Only wikibase-entityid (entity-to-entity)
            if datatype != 'wikibase-entityid':
                skipped_not_entityid += 1
                continue
            
            qid_to = datavalue.get('value', {}).get('id', '')
            
            # Only if target exists in our dataset
            if not qid_to or qid_to not in all_qids:
                skipped_no_target += 1
                continue
            
            # Only simple edges (no cipher-eligible qualifiers)
            qualifiers = set(claim.get('qualifiers', {}).keys())
            if qualifiers & CIPHER_ELIGIBLE_QUALIFIERS:
                skipped_has_qualifiers += 1
                continue
            
            # This is a simple edge!
            edges.append({
                'from_qid': qid_from,
                'to_qid': qid_to,
                'pid': prop_id
            })

print(f"Classification complete:")
print(f"  Simple edges found: {len(edges):,}")
print(f"  Skipped (not entityid): {skipped_not_entityid:,}")
print(f"  Skipped (no target in dataset): {skipped_no_target:,}")
print(f"  Skipped (has qualifiers - node candidate): {skipped_has_qualifiers:,}")
print()

# Import in batches
BATCH_SIZE = 1000
total_batches = (len(edges) + BATCH_SIZE - 1) // BATCH_SIZE

print(f"Importing {len(edges):,} edges in {total_batches} batches...")
print()

imported = 0
for i in range(0, len(edges), BATCH_SIZE):
    batch = edges[i:i+BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    
    with driver.session() as session:
        result = session.run("""
            UNWIND $edges as edge
            MATCH (from:Entity {qid: edge.from_qid})
            MATCH (to:Entity {qid: edge.to_qid})
            
            // Create relationship with PID as type (no WIKIDATA_ prefix)
            CALL apoc.create.relationship(
                from,
                edge.pid,
                {
                    wikidata_pid: edge.pid,
                    imported_at: datetime(),
                    source: 'wikidata_raw'
                },
                to
            ) YIELD rel
            RETURN count(rel) as created
        """, edges=batch)
        
        created = result.single()['created']
        imported += created
        
        if batch_num % 10 == 0 or batch_num == total_batches:
            print(f"  Batch {batch_num}/{total_batches}: {imported:,} edges imported")

driver.close()

print()
print("="*80)
print("IMPORT COMPLETE")
print("="*80)
print(f"End: {datetime.now()}")
print()
print(f"Edges imported: {imported:,}")
print(f"Previous: 784")
print(f"Improvement: {imported/784:.1f}x")
print()
print(f"Avg edges per entity:")
print(f"  Before: 0.30")
print(f"  After: {imported/len(all_qids):.2f}")
print()
print("Validation query:")
print("  MATCH (e:Entity)")
print("  OPTIONAL MATCH (e)-[r]-()")
print("  RETURN avg(count(r)) as avg_degree")
print()
