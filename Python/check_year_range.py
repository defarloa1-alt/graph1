#!/usr/bin/env python3
"""Check the actual year range in Neo4j"""

from neo4j import GraphDatabase

uri = 'bolt://127.0.0.1:7687'
username = 'neo4j'
password = 'Chrystallum'

driver = GraphDatabase.driver(uri, auth=(username, password))

try:
    with driver.session() as session:
        # Get year range
        result = session.run("""
            MATCH (y:Year)
            RETURN count(y) as total,
                   min(y.year_value) as min_year,
                   max(y.year_value) as max_year
        """)
        
        stats = result.single()
        total = stats['total']
        min_year = stats['min_year']
        max_year = stats['max_year']
        
        print("=" * 70)
        print("YEAR NODES ANALYSIS")
        print("=" * 70)
        print(f"\nTotal Year nodes: {total}")
        print(f"Year range: {min_year} to {max_year}")
        print(f"Expected range: {max_year - min_year + 1} years")
        print(f"Actual nodes: {total}")
        
        if total != (max_year - min_year + 1):
            gap = (max_year - min_year + 1) - total
            print(f"\n[WARNING] Gap detected: {gap} years missing!")
        
        # Check years beyond 2025
        result = session.run("""
            MATCH (y:Year)
            WHERE y.year_value > 2025
            RETURN y.year_value as year, y.label as label, y.name as name
            ORDER BY y.year_value
        """)
        
        beyond_2025 = list(result)
        if beyond_2025:
            print(f"\n[ISSUE] Found {len(beyond_2025)} Year nodes beyond 2025:")
            for record in beyond_2025[:20]:
                print(f"  {record['year']}: label='{record['label']}', name='{record['name']}'")
            if len(beyond_2025) > 20:
                print(f"  ... and {len(beyond_2025) - 20} more")
            
            print(f"\n[ACTION] These {len(beyond_2025)} years should be deleted")
        else:
            print(f"\n[OK] No years beyond 2025")
        
        # Sample years at boundaries
        print("\n=== Sample Years at Boundaries ===")
        result = session.run("""
            MATCH (y:Year)
            WHERE y.year_value IN [-753, -509, -82, 1, 1000, 2024, 2025]
            RETURN y.year_value as year, y.label as label, y.name as name
            ORDER BY y.year_value
        """)
        
        for record in result:
            print(f"  {record['year']}: label='{record['label']}', name='{record['name']}'")

finally:
    driver.close()

