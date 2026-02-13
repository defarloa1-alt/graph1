#!/usr/bin/env python3
"""
Import LCSH Subjects to Neo4j
Step 3: Create Subject nodes and BROADER_THAN relationships
"""

import csv
import sys
import io
from pathlib import Path
from neo4j import GraphDatabase
import argparse

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def import_lcsh_subjects(uri: str, user: str, password: str, csv_path: Path):
    """Import LCSH subjects from CSV to Neo4j."""
    print("="*80)
    print("IMPORT LCSH SUBJECTS TO NEO4J")
    print("="*80)
    print(f"URI: {uri}")
    print(f"CSV: {csv_path}")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    # Read CSV
    subjects = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        subjects = list(reader)
    
    print(f"[LOADED] {len(subjects)} subjects from CSV")
    print()
    
    with driver.session() as session:
        # Step 1: Create Subject nodes
        print("[STEP 1] Creating Subject nodes...")
        
        created = 0
        for i, subject in enumerate(subjects, 1):
            session.run("""
                MERGE (s:Subject {lcsh_id: $lcsh_id})
                SET s.unique_id = 'SUBJECT_LCSH_' + $lcsh_id,
                    s.label = $label,
                    s.lcsh_heading = $label,
                    s.dewey_decimal = $dewey_decimal,
                    s.lcc_code = $lcc_code,
                    s.fast_id = $fast_id,
                    s.scope_note = $scope_note,
                    s.uri = $uri,
                    s.source = 'LCSH',
                    s.created = datetime()
            """, 
                lcsh_id=subject['lcsh_id'],
                label=subject['label'],
                dewey_decimal=subject['dewey_decimal'] or None,
                lcc_code=subject['lcc_code'] or None,
                fast_id=subject['fast_id'] or None,
                scope_note=subject['scope_note'] or None,
                uri=subject['uri']
            )
            created += 1
            
            if i % 100 == 0:
                print(f"  Created {i}/{len(subjects)} nodes...")
        
        print(f"[OK] Created {created} Subject nodes")
        print()
        
        # Step 2: Create BROADER_THAN relationships
        print("[STEP 2] Creating BROADER_THAN relationships...")
        
        rel_count = 0
        for subject in subjects:
            if subject['broader_lcsh']:
                session.run("""
                    MATCH (child:Subject {lcsh_id: $child_id})
                    MATCH (parent:Subject {lcsh_id: $parent_id})
                    MERGE (parent)-[r:BROADER_THAN]->(child)
                    SET r.created = datetime()
                """,
                    child_id=subject['lcsh_id'],
                    parent_id=subject['broader_lcsh']
                )
                rel_count += 1
        
        print(f"[OK] Created {rel_count} BROADER_THAN relationships")
        print()
        
        # Step 3: Create indexes
        print("[STEP 3] Creating indexes...")
        
        session.run("CREATE INDEX subject_lcsh_id IF NOT EXISTS FOR (s:Subject) ON (s.lcsh_id)")
        session.run("CREATE INDEX subject_dewey IF NOT EXISTS FOR (s:Subject) ON (s.dewey_decimal)")
        session.run("CREATE INDEX subject_label IF NOT EXISTS FOR (s:Subject) ON (s.label)")
        
        print("[OK] Indexes created")
        print()
        
        # Summary statistics
        print("="*80)
        print("DATABASE SUMMARY")
        print("="*80)
        
        result = session.run("MATCH (s:Subject) RETURN count(s) as total")
        total = result.single()['total']
        
        result = session.run("MATCH ()-[r:BROADER_THAN]->() RETURN count(r) as total")
        rel_total = result.single()['total']
        
        result = session.run("MATCH (s:Subject) WHERE s.dewey_decimal IS NOT NULL RETURN count(s) as total")
        with_dewey = result.single()['total']
        
        result = session.run("MATCH (s:Subject) WHERE s.lcc_code IS NOT NULL RETURN count(s) as total")
        with_lcc = result.single()['total']
        
        result = session.run("MATCH (s:Subject) WHERE s.fast_id IS NOT NULL RETURN count(s) as total")
        with_fast = result.single()['total']
        
        print(f"\nTotal Subject nodes:     {total:>6,}")
        print(f"BROADER_THAN relationships: {rel_total:>6,}")
        print(f"\nWith Dewey codes:        {with_dewey:>6,} ({with_dewey/total*100:.1f}%)")
        print(f"With LCC codes:          {with_lcc:>6,} ({with_lcc/total*100:.1f}%)")
        print(f"With FAST IDs:           {with_fast:>6,} ({with_fast/total*100:.1f}%)")
        print()
        
        # Sample subjects
        print("[SAMPLE SUBJECTS]")
        result = session.run("""
            MATCH (s:Subject)
            WHERE s.dewey_decimal IS NOT NULL
            RETURN s.label, s.lcsh_id, s.dewey_decimal
            ORDER BY s.dewey_decimal
            LIMIT 10
        """)
        
        for record in result:
            print(f"  {record['s.dewey_decimal']:10s} | {record['s.lcsh_id']:12s} | {record['s.label'][:50]}")
        
        print()
        print("="*80)
    
    driver.close()

def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Import LCSH subjects to Neo4j')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j URI')
    parser.add_argument('--user', default='neo4j', help='Neo4j username')
    parser.add_argument('--password', default='Chrystallum', help='Neo4j password')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / "output" / "lcsh_subjects_complete.csv"
    
    if not csv_path.exists():
        print(f"[ERROR] CSV not found: {csv_path}")
        print("Run retrieve_lcsh_details.py first.")
        sys.exit(1)
    
    import_lcsh_subjects(args.uri, args.user, args.password, csv_path)
    
    print("[SUCCESS] LCSH subject backbone is now in Neo4j!")
    print()
    print("[TEST QUERY]")
    print("  MATCH (s:Subject) WHERE s.dewey_decimal STARTS WITH '937' RETURN s LIMIT 10;")

if __name__ == "__main__":
    main()


