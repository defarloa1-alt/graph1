#!/usr/bin/env python3
"""
Link Year nodes to Period nodes via WITHIN_TIMESPAN relationships
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def link_years_to_periods(uri="bolt://127.0.0.1:7687", user="neo4j", password="Chrystallum"):
    """
    Create WITHIN_TIMESPAN relationships between Years and Periods
    """
    print("="*80)
    print("LINK YEARS TO PERIODS")
    print("="*80)
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Check Years and Periods
            print("\n[STEP 1] Checking existing nodes...")
            result = session.run("MATCH (y:Year) RETURN count(y) as total")
            total_years = result.single()['total']
            
            result = session.run("MATCH (p:Period) RETURN count(p) as total")
            total_periods = result.single()['total']
            
            print(f"  Year nodes: {total_years}")
            print(f"  Period nodes: {total_periods}")
            
            if total_years == 0:
                print("\n  ❌ ERROR: No Year nodes found!")
                print("  Run: python rebuild_year_backbone.py")
                return False
            
            if total_periods == 0:
                print("\n  ❌ ERROR: No Period nodes found!")
                return False
            
            # Step 2: Link Years to Periods
            print("\n[STEP 2] Creating WITHIN_TIMESPAN relationships...")
            print("  Matching Years to Periods by date range...")
            
            result = session.run("""
                MATCH (y:Year), (p:Period)
                WHERE y.year_value >= p.start_year 
                  AND y.year_value <= p.end_year
                  AND p.start_year IS NOT NULL
                  AND p.end_year IS NOT NULL
                MERGE (y)-[r:WITHIN_TIMESPAN]->(p)
                ON CREATE SET r.created = datetime()
                RETURN count(r) as created
            """)
            
            created = result.single()['created']
            print(f"  ✅ Created {created} WITHIN_TIMESPAN relationships")
            
            # Step 3: Verify
            print("\n[STEP 3] Verification...")
            
            result = session.run("""
                MATCH (y:Year)-[:WITHIN_TIMESPAN]->(p:Period)
                RETURN count(DISTINCT y) as years_linked,
                       count(DISTINCT p) as periods_linked,
                       count(*) as total_links
            """)
            stats = result.single()
            
            print(f"  Years linked to periods: {stats['years_linked']}/{total_years}")
            print(f"  Periods linked to years: {stats['periods_linked']}/{total_periods}")
            print(f"  Total WITHIN_TIMESPAN links: {stats['total_links']}")
            
            # Show sample linkages
            print("\n[STEP 4] Sample linkages...")
            result = session.run("""
                MATCH (y:Year)-[:WITHIN_TIMESPAN]->(p:Period)
                RETURN y.year_value as year, y.label as year_label,
                       p.label as period, p.start_year as p_start, p.end_year as p_end
                ORDER BY y.year_value
                LIMIT 5
            """)
            
            for record in result:
                print(f"  {record['year']} ({record['year_label']}) -> {record['period']} ({record['p_start']} to {record['p_end']})")
            
            print("\n" + "="*80)
            print("LINKING COMPLETE")
            print("="*80)
            
    finally:
        driver.close()
    
    return True

if __name__ == "__main__":
    link_years_to_periods()

