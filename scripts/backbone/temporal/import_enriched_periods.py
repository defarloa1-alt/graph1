#!/usr/bin/env python3
"""
Import enriched periods to Neo4j.
Executes each period block as a single transaction.
"""
import sys
import io
import re
from pathlib import Path
from neo4j import GraphDatabase

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def import_periods(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """Import periods from enriched Cypher file."""
    
    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    
    input_file = project_root / "Subjects" / "periods_import_multi_facet.cypher"
    
    print("="*80)
    print("Importing Enriched Periods to Neo4j")
    print("="*80)
    print(f"Input: {input_file}")
    print(f"Neo4j: {uri}")
    print()
    
    # Verify file exists
    if not input_file.exists():
        print(f"❌ ERROR: File not found: {input_file}")
        sys.exit(1)
    
    # Read file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into period blocks (separated by blank lines)
    blocks = [b.strip() for b in re.split(r'\n\s*\n+', content.strip()) if b.strip()]
    
    print(f"Found {len(blocks)} period blocks to import")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        successful = 0
        failed = 0
        
        for i, block in enumerate(blocks, 1):
            # Remove trailing semicolon if present
            block = block.rstrip(';').strip()
            
            if not block:
                continue
            
            try:
                # Execute as single transaction
                result = session.run(block)
                list(result)  # Consume result
                successful += 1
                
                if i % 50 == 0:
                    print(f"  Imported {i}/{len(blocks)} periods...")
                
            except Exception as e:
                failed += 1
                if failed <= 5:  # Show first 5 errors
                    print(f"\n❌ Error in period {i}:")
                    print(f"   {str(e)[:150]}")
                    print(f"   Block preview: {block[:100]}...")
                continue
        
        print(f"\n✅ Successfully imported: {successful} periods")
        if failed > 0:
            print(f"❌ Failed: {failed} periods")
        
        # Verify import
        print("\n" + "="*80)
        print("Verification")
        print("="*80)
        
        result = session.run("MATCH (p:Period) RETURN count(p) as count")
        total = result.single()['count']
        print(f"Total Period nodes: {total}")
        
        result = session.run("MATCH (p:Period)-[r]->() RETURN type(r), count(*) as count ORDER BY count DESC")
        print("\nRelationships from Period nodes:")
        for record in result:
            print(f"  {record['type(r)']:30s}: {record['count']:>5}")
        
        result = session.run("MATCH (p:Period) WHERE p.label IS NOT NULL AND p.start_year IS NOT NULL RETURN count(p) as count")
        complete = result.single()['count']
        print(f"\nPeriods with label and dates: {complete}")
        
        print("\nSample periods:")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.label IS NOT NULL
            RETURN p.label, p.start_year, p.end_year
            ORDER BY p.start_year
            LIMIT 5
        """)
        for record in result:
            print(f"  - {record['p.label']} ({record['p.start_year']} to {record['p.end_year']})")
    
    driver.close()
    print("\n" + "="*80)
    print("Import complete!")
    print("="*80)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Import enriched periods to Neo4j')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j URI')
    parser.add_argument('--user', default='neo4j', help='Neo4j username')
    parser.add_argument('--password', default='Chrystallum', help='Neo4j password')
    
    args = parser.parse_args()
    
    import_periods(
        uri=args.uri,
        user=args.user,
        password=args.password
    )

