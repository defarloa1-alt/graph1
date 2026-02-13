#!/usr/bin/env python3
"""
Rebuild Year backbone in Neo4j
Creates Year nodes and FOLLOWED_BY/PRECEDED_BY chains
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def rebuild_year_backbone(uri="bolt://127.0.0.1:7687", user="neo4j", password="Chrystallum", 
                         start_year=-753, end_year=-82):
    """
    Rebuild Year nodes and create temporal backbone.
    
    Args:
        uri: Neo4j connection URI
        user: Neo4j username
        password: Neo4j password
        start_year: First year to import (negative for BCE)
        end_year: Last year to import
    """
    print("="*80)
    print("REBUILD YEAR BACKBONE")
    print("="*80)
    print(f"URI: {uri}")
    print(f"Range: {start_year} to {end_year} ({end_year - start_year + 1} years)")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Check existing Years
            print("[STEP 0] Checking existing Year nodes...")
            result = session.run("MATCH (y:Year) RETURN count(y) as total")
            existing = result.single()['total']
            print(f"  Existing Year nodes: {existing}")
            
            if existing > 0:
                response = input(f"\n  Delete {existing} existing Year nodes? (yes/no): ")
                if response.lower() == 'yes':
                    session.run("MATCH (y:Year) DETACH DELETE y")
                    print(f"  Deleted {existing} Year nodes")
                else:
                    print("  Keeping existing Years, will merge with new")
            
            # Step 1: Create Year nodes
            print("\n[STEP 1] Creating Year nodes...")
            created_years = 0
            
            for year in range(start_year, end_year + 1):
                # Format ISO 8601 dates
                if year < 0:
                    year_str = f"{abs(year):04d}"
                    iso_start = f"-{year_str}-01-01"
                    iso_end = f"-{year_str}-12-31"
                    label = f"{abs(year)} BCE"
                else:
                    year_str = f"{year:04d}"
                    iso_start = f"{year_str}-01-01"
                    iso_end = f"{year_str}-12-31"
                    label = f"{year} CE"
                
                session.run("""
                    MERGE (y:Year {year_value: $year_value})
                    ON CREATE SET
                        y.label = $label,
                        y.name = $label,
                        y.iso8601_start = $iso_start,
                        y.iso8601_end = $iso_end,
                        y.cidoc_crm_class = 'E52_Time-Span',
                        y.unique_id = 'YEAR_' + toString($year_value),
                        y.temporal_backbone = true,
                        y.created = datetime()
                    ON MATCH SET
                        y.label = $label,
                        y.name = $label,
                        y.iso8601_start = $iso_start,
                        y.iso8601_end = $iso_end,
                        y.cidoc_crm_class = 'E52_Time-Span'
                """, {
                    'year_value': year,
                    'label': label,
                    'iso_start': iso_start,
                    'iso_end': iso_end
                })
                
                created_years += 1
                
                if created_years % 100 == 0:
                    print(f"   Progress: {created_years}/{end_year - start_year + 1}...")
            
            print(f"  ✅ Created/updated {created_years} Year nodes")
            
            # Step 2: Create year chain (FOLLOWED_BY/PRECEDED_BY)
            print("\n[STEP 2] Creating year chain relationships...")
            
            result = session.run("""
                MATCH (y1:Year), (y2:Year)
                WHERE y2.year_value = y1.year_value + 1
                MERGE (y1)-[r1:FOLLOWED_BY]->(y2)
                MERGE (y2)-[r2:PRECEDED_BY]->(y1)
                RETURN count(r1) as count
            """)
            
            chain_count = result.single()['count']
            print(f"  ✅ Created {chain_count} year chain relationships")
            
            # Step 3: Verify
            print("\n[STEP 3] Verification...")
            result = session.run("""
                MATCH (y:Year)
                RETURN count(y) as total_years,
                       min(y.year_value) as min_year,
                       max(y.year_value) as max_year
            """)
            stats = result.single()
            
            result = session.run("""
                MATCH (y:Year)-[:FOLLOWED_BY]->()
                RETURN count(y) as chain_length
            """)
            chain_length = result.single()['chain_length']
            
            print(f"  Total Year nodes: {stats['total_years']}")
            print(f"  Year range: {stats['min_year']} to {stats['max_year']}")
            print(f"  Chain length: {chain_length}")
            
            # Check for gaps
            expected_chain = stats['max_year'] - stats['min_year']
            if chain_length == expected_chain:
                print(f"  ✅ No gaps in year chain")
            else:
                print(f"  ⚠️  Gap detected: expected {expected_chain}, got {chain_length}")
            
            print("\n" + "="*80)
            print("YEAR BACKBONE REBUILT SUCCESSFULLY")
            print("="*80)
            
    finally:
        driver.close()
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Rebuild year backbone')
    parser.add_argument('--start', type=int, default=-753, help='Start year (negative for BCE)')
    parser.add_argument('--end', type=int, default=-82, help='End year')
    
    args = parser.parse_args()
    
    rebuild_year_backbone(start_year=args.start, end_year=args.end)

