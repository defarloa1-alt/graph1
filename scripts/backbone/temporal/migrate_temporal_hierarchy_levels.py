#!/usr/bin/env python3
"""
Migrate Temporal Hierarchy Levels (Decade, Century, Millennium)
Creates calendrical hierarchy nodes and links them via PART_OF.
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def migrate_temporal_hierarchy(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """
    Create Decade, Century, Millennium nodes and link hierarchy.
    Year -> Decade -> Century -> Millennium
    """
    print("="*80)
    print("MIGRATE TEMPORAL HIERARCHY (DECADE/CENTURY/MILLENNIUM)")
    print("="*80)
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Step 1: Create Decades
        print("\n[STEP 1] Creating Decade nodes and linking Years...")
        session.run("""
            MATCH (y:Year)
            WHERE y.year IS NOT NULL
            WITH y, 
                 y.year - (y.year % 10) as decade_start
            
            MERGE (d:Decade {start_year: decade_start})
            ON CREATE SET 
                d.label = toString(decade_start) + 's',
                d.end_year = decade_start + 9,
                d.temporal_backbone = true
            
            MERGE (y)-[:PART_OF]->(d)
        """)
        print("  ✅ Decades created and Years linked")
        
        # Step 2: Create Centuries
        print("\n[STEP 2] Creating Century nodes and linking Decades...")
        session.run("""
            MATCH (d:Decade)
            WITH d,
                 d.start_year - (d.start_year % 100) as century_start
            
            MERGE (c:Century {start_year: century_start})
            ON CREATE SET
                c.label = toString(abs(century_start / 100) + 1) + 
                          CASE 
                            WHEN century_start < 0 THEN ' BCE'
                            ELSE ' CE'
                          END + ' Century',
                c.end_year = century_start + 99,
                c.temporal_backbone = true
            
            MERGE (d)-[:PART_OF]->(c)
        """)
        print("  ✅ Centuries created and Decades linked")
        
        # Step 3: Create Millenniums
        print("\n[STEP 3] Creating Millennium nodes and linking Centuries...")
        session.run("""
            MATCH (c:Century)
            WITH c,
                 c.start_year - (c.start_year % 1000) as millennium_start
            
            MERGE (m:Millennium {start_year: millennium_start})
            ON CREATE SET
                m.label = toString(abs(millennium_start / 1000) + 1) + 
                          CASE 
                            WHEN millennium_start < 0 THEN ' BCE'
                            ELSE ' CE'
                          END + ' Millennium',
                m.end_year = millennium_start + 999,
                m.temporal_backbone = true
            
            MERGE (c)-[:PART_OF]->(m)
        """)
        print("  ✅ Millenniums created and Centuries linked")
        
        # Verification
        print("\n[VERIFICATION]")
        stats = session.run("""
            MATCH (y:Year)-[:PART_OF]->(d:Decade)-[:PART_OF]->(c:Century)-[:PART_OF]->(m:Millennium)
            RETURN count(DISTINCT y) as years, 
                   count(DISTINCT d) as decades,
                   count(DISTINCT c) as centuries,
                   count(DISTINCT m) as millenniums
        """).single()
        
        print(f"  Hierarchy Complete: {stats['years']} Years -> {stats['decades']} Decades -> "
              f"{stats['centuries']} Centuries -> {stats['millenniums']} Millenniums")
              
    driver.close()
    print("\n" + "="*80)
    print("MIGRATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    migrate_temporal_hierarchy()
