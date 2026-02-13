#!/usr/bin/env python3
"""
Import Year Nodes to Neo4j

Creates:
- Year nodes for specified range
- FOLLOWED_BY/PRECEDED_BY chains between years

"""
import sys
import io
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ ERROR: neo4j driver not installed")
    print("   Run: pip install neo4j")
    sys.exit(1)

def import_year_nodes(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum", start_year=-2000, end_year=2025):
    """
    Import Year nodes and create temporal backbone.
    Args:
        uri: Neo4j connection URI
        user: Neo4j username
        password: Neo4j password
        start_year: First year to import
        end_year: Last year to import
    """
    print("="*80)
    print("IMPORT YEAR NODES AND TEMPORAL BACKBONE")
    print("="*80)
    print(f"URI: {uri}")
    print(f"Range: {start_year} to {end_year} ({end_year - start_year + 1} years)")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Step 1: Create Year nodes
        print("📊 Step 1: Creating Year nodes...")
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
            
            result = session.run("""
                MERGE (y:Year {year: $year})
                ON CREATE SET
                    y.year_value = $year,
                    y.label = $label,
                    y.iso8601_start = $iso_start,
                    y.iso8601_end = $iso_end,
                    y.temporal_backbone = true,
                    y.created = datetime()
                ON MATCH SET
                    y.year_value = coalesce(y.year_value, $year)
                RETURN y.year as year
            """, {
                'year': year,
                'label': label,
                'iso_start': iso_start,
                'iso_end': iso_end
            })
            
            if result.single():
                created_years += 1
            
            if created_years % 100 == 0:
                print(f"   Created {created_years} years...")
        
        print(f"✅ Created {created_years} Year nodes")
        print()
        
        # Step 2: Create year chain (FOLLOWED_BY/PRECEDED_BY)
        print("📊 Step 2: Creating year chain relationships...")
        
        result = session.run("""
            MATCH (y1:Year), (y2:Year)
            WHERE y2.year = y1.year + 1
            MERGE (y1)-[r1:FOLLOWED_BY]->(y2)
            MERGE (y2)-[r2:PRECEDED_BY]->(y1)
            ON CREATE SET 
                r1.created = datetime(),
                r2.created = datetime()
            RETURN count(r1) as count
        """)
        
        chain_count = result.single()['count']
        print(f"✅ Created {chain_count} year chain relationships")
        print()
        
        # Verify
        result = session.run("""
            MATCH (y:Year)
            RETURN count(y) as total_years
        """)
        total_years = result.single()['total_years']

        result = session.run("""
            MATCH (y:Year)-[:FOLLOWED_BY]->()
            RETURN count(y) as chain_length
        """)
        chain_length = result.single()['chain_length']

        print("="*80)
        print("✅ YEAR IMPORT COMPLETE")
        print("="*80)
        print(f"   Total Year nodes: {total_years}")
        print(f"   Year chain length: {chain_length}")
        print()
        
    driver.close()
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import year nodes and temporal backbone')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j URI')
    parser.add_argument('--user', default='neo4j', help='Neo4j username')
    parser.add_argument('--password', default='Chrystallum', help='Neo4j password')
    parser.add_argument('--start', type=int, default=-2000, help='Start year (negative for BCE)')
    parser.add_argument('--end', type=int, default=2226, help='End year')
    
    args = parser.parse_args()
    
    success = import_year_nodes(
        uri=args.uri,
        user=args.user,
        password=args.password,
        start_year=args.start,
        end_year=args.end
    )
    sys.exit(0 if success else 1)
