#!/usr/bin/env python3
"""Validate 2,600 entity import claimed by Dev"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("=" * 80)
print("QA VALIDATION: 2,600 Entity Import")
print("=" * 80)
print()

with driver.session() as session:
    # Total entities
    result = session.run("MATCH (n:Entity) RETURN count(n) as total")
    total = result.single()['total']
    
    # Unique QIDs
    result = session.run("MATCH (n:Entity) RETURN count(DISTINCT n.qid) as unique_qids")
    unique = result.single()['unique_qids']
    
    # Entity types
    result = session.run("""
        MATCH (n:Entity)
        RETURN n.entity_type as type, count(n) as count
        ORDER BY count DESC
    """)
    types = list(result)
    
    print("ENTITY COUNT:")
    print("-" * 80)
    print(f"Total Entity nodes: {total:,}")
    print(f"Unique QIDs: {unique:,}")
    print(f"Dev claimed: 2,600")
    print()
    
    if total == 2600:
        print("[PASS] Entity count matches Dev's claim exactly!")
    elif total > 2600:
        print(f"[ISSUE] More entities than expected: {total - 2600} extra")
    elif total < 2600:
        print(f"[ISSUE] Fewer entities than expected: {2600 - total} missing")
    print()
    
    print("ENTITY TYPE DISTRIBUTION:")
    print("-" * 80)
    for t in types:
        print(f"  {t['type']}: {t['count']:,}")
    print()
    
    # Check for duplicates
    result = session.run("""
        MATCH (n:Entity)
        WITH n.qid as qid, count(n) as count
        WHERE count > 1
        RETURN count(qid) as duplicate_qids
    """)
    dup_count = result.single()['duplicate_qids']
    
    print("DUPLICATE CHECK:")
    print("-" * 80)
    print(f"Duplicate QIDs: {dup_count}")
    if dup_count == 0:
        print("[PASS] No duplicates (idempotent import working)")
    else:
        print(f"[FAIL] {dup_count} QIDs have duplicate nodes")
    print()
    
    # Sample new entities
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.imported_at > datetime('2026-02-22T00:00:00Z')
        RETURN n.qid, n.label, n.entity_type
        ORDER BY n.imported_at DESC
        LIMIT 5
    """)
    
    recent = list(result)
    print("RECENTLY IMPORTED ENTITIES (sample):")
    print("-" * 80)
    for r in recent:
        label = (r['label'] or r['qid'])[:50]
        print(f"  {r['qid']} ({r['entity_type']}): {label}")

driver.close()

print()
print("=" * 80)
print("VALIDATION SUMMARY")
print("=" * 80)
if total == 2600 and unique == 2600 and dup_count == 0:
    print("[PASS] Dev's claim VERIFIED - 2,600 unique entities imported!")
else:
    print(f"[REVIEW] Total:{total}, Unique:{unique}, Duplicates:{dup_count}")
