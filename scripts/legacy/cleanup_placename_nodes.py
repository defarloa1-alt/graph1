#!/usr/bin/env python3
"""
Delete PlaceName nodes - Simplify to canonical federated model
Design rule: Keep to canonical federated foreign keys (QIDs only)
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

print("=" * 80)
print("CLEANUP: Deleting PlaceName Nodes - Canonical Federated Model")
print("=" * 80)
print()

with driver.session() as session:
    # Count before
    result = session.run("MATCH (n:PlaceName) RETURN count(n) AS count")
    before_nodes = result.single()["count"]
    
    result = session.run("MATCH ()-[r:HAS_NAME]->(:PlaceName) RETURN count(r) AS count")
    before_rels = result.single()["count"]
    
    print(f"Before cleanup:")
    print(f"  PlaceName nodes: {before_nodes:,}")
    print(f"  HAS_NAME relationships: {before_rels:,}")
    print()
    
    # Delete relationships first
    print("Step 1: Deleting HAS_NAME relationships...")
    result = session.run("""
        MATCH (:Place)-[r:HAS_NAME]->(:PlaceName)
        DELETE r
        RETURN count(r) AS deleted
    """)
    deleted_rels = result.single()["deleted"]
    print(f"  Deleted: {deleted_rels:,} relationships")
    print()
    
    # Delete nodes
    print("Step 2: Deleting PlaceName nodes...")
    result = session.run("""
        MATCH (n:PlaceName)
        DELETE n
        RETURN count(n) AS deleted
    """)
    deleted_nodes = result.single()["deleted"]
    print(f"  Deleted: {deleted_nodes:,} nodes")
    print()
    
    # Verify
    result = session.run("MATCH (n:PlaceName) RETURN count(n) AS count")
    after_nodes = result.single()["count"]
    
    result = session.run("MATCH ()-[r:HAS_NAME]->() RETURN count(r) AS count")
    after_rels = result.single()["count"]
    
    print("After cleanup:")
    print(f"  PlaceName nodes: {after_nodes:,}")
    print(f"  HAS_NAME relationships: {after_rels:,}")
    print()
    
    # Final node count
    result = session.run("MATCH (n) RETURN count(n) AS total_nodes")
    total_nodes = result.single()["total_nodes"]
    
    result = session.run("MATCH ()-[r]->() RETURN count(r) AS total_rels")
    total_rels = result.single()["total_rels"]
    
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print()
    print(f"New database size:")
    print(f"  Total nodes: {total_nodes:,}")
    print(f"  Total relationships: {total_rels:,}")
    print()
    print("Simplified canonical model:")
    print("  Place nodes with qid for federation")
    print("  Multilingual labels via Wikidata API (not stored)")
    print()

driver.close()

