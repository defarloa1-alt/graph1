#!/usr/bin/env python3
"""Prefix Period labels with their location (e.g., 'China: Spring and Autumn')"""

from neo4j import GraphDatabase

uri = 'bolt://127.0.0.1:7687'
username = 'neo4j'
password = 'Chrystallum'

driver = GraphDatabase.driver(uri, auth=(username, password))

print("=" * 70)
print("PREFIXING PERIOD LABELS WITH LOCATION")
print("=" * 70)

try:
    with driver.session() as session:
        # Check current state
        print("\n[STEP 1] Checking Period-Place linkage...")
        result = session.run("""
            MATCH (p:Period)-[:LOCATED_IN]->(pl:Place)
            RETURN count(DISTINCT p) as periods_with_location
        """)
        
        linked = result.single()['periods_with_location']
        
        result = session.run("MATCH (p:Period) RETURN count(p) as total")
        total = result.single()['total']
        
        print(f"  Periods linked to Places: {linked}/{total}")
        
        if linked == 0:
            print("\n  [WARNING] No Period-Place relationships found!")
            print("  Cannot prefix labels without location data")
            driver.close()
            exit(0)
        
        # Sample current labels
        print("\n[STEP 2] Sample current labels...")
        result = session.run("""
            MATCH (p:Period)-[:LOCATED_IN]->(pl:Place)
            RETURN p.label as current_label, pl.label as location
            LIMIT 5
        """)
        
        for record in result:
            print(f"  '{record['current_label']}' (location: {record['location']})")
        
        # Update labels with location prefix
        print("\n[STEP 3] Adding location prefix to Period labels...")
        
        result = session.run("""
            MATCH (p:Period)-[:LOCATED_IN]->(pl:Place)
            WHERE pl.label IS NOT NULL 
              AND NOT p.label STARTS WITH pl.label + ':'
            WITH p, pl
            SET p.label = pl.label + ': ' + p.label
            RETURN count(p) as updated
        """)
        
        updated = result.single()['updated']
        print(f"  Updated: {updated} Period labels")
        
        # Verify
        print("\n[STEP 4] Sample updated labels...")
        result = session.run("""
            MATCH (p:Period)-[:LOCATED_IN]->(pl:Place)
            WHERE p.label CONTAINS ':'
            RETURN p.label as new_label, pl.label as location
            ORDER BY p.label
            LIMIT 10
        """)
        
        for record in result:
            print(f"  '{record['new_label']}'")
        
        # Check for periods without location
        result = session.run("""
            MATCH (p:Period)
            WHERE NOT (p)-[:LOCATED_IN]->()
            RETURN count(p) as without_location
        """)
        
        without = result.single()['without_location']
        if without > 0:
            print(f"\n[INFO] {without} periods have no location link (labels unchanged)")
        
        # Summary
        print("\n" + "=" * 70)
        print("LABEL PREFIX COMPLETE")
        print("=" * 70)
        print(f"Updated: {updated} Period labels")
        print(f"Format: 'Location: Period Name'")
        
        if updated > 0:
            print("\n[SUCCESS] Period labels now include geographic context!")

finally:
    driver.close()

