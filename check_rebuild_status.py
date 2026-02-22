#!/usr/bin/env python3
"""Check current rebuild status"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("Checking Chrystallum rebuild status...")
print()

try:
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    
    with driver.session() as session:
        # Node counts
        result = session.run("""
            RETURN
                count { MATCH (:Year) } AS years,
                count { MATCH (:Period) } AS periods,
                count { MATCH (:PeriodCandidate) } AS period_candidates,
                count { MATCH (:Place) } AS places,
                count { MATCH (:PlaceName) } AS place_names,
                count { MATCH (:PlaceType) } AS place_types
        """)
        stats = result.single()
        
        print("=== NODE COUNTS ===")
        print(f"  Years: {stats['years']}")
        print(f"  Periods: {stats['periods']}")
        print(f"  Period Candidates: {stats['period_candidates']}")
        print(f"  Places: {stats['places']}")
        print(f"  Place Names: {stats['place_names']}")
        print(f"  Place Types: {stats['place_types']}")
        print()
        
        # Relationship counts
        result = session.run("MATCH ()-[r]->() RETURN count(r) AS total_rels")
        total_rels = result.single()["total_rels"]
        print(f"=== TOTAL RELATIONSHIPS: {total_rels} ===")
        print()
        
        # Current status
        print("=== STATUS ===")
        if stats['years'] > 0:
            print("  ✓ Stage 2: Temporal backbone (Years) - COMPLETE")
        else:
            print("  ✗ Stage 2: Temporal backbone - NOT STARTED")
            
        if stats['periods'] > 0:
            print("  ✓ Stage 3: Periods - COMPLETE")
        else:
            print("  ✗ Stage 3: Periods - NOT STARTED")
            
        if stats['places'] > 0:
            print(f"  ⏳ Stage 4: Geographic - IN PROGRESS ({stats['places']} places loaded)")
        else:
            print("  ✗ Stage 4: Geographic - NOT STARTED")
            
        if stats['place_types'] > 0:
            print("  ✓ Stage 5: Geographic types - COMPLETE")
        else:
            print("  ○ Stage 5: Geographic types - PENDING")
        
        print()
        print(f"NEXT: Continue with Stage 4 (Geographic) if needed")
    
    driver.close()
    
except Exception as e:
    print(f"ERROR: {e}")

