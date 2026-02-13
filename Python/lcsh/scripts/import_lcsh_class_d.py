#!/usr/bin/env python3
"""
Import LCSH Class D subjects into Neo4j (replaces existing subjects)
"""

import sys
import io
import csv
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chrystallum"
INPUT_FILE = "../output/lcsh_class_d_complete.csv"

def clear_existing_subjects(driver):
    """Remove all existing Subject nodes"""
    print("\n[STEP 1] Clearing existing Subject nodes...")
    
    with driver.session() as session:
        result = session.run("MATCH (s:Subject) RETURN count(s) as total")
        old_count = result.single()['total']
        
        print(f"  Found {old_count} existing subjects")
        
        if old_count > 0:
            # Delete subjects and their relationships
            session.run("MATCH (s:Subject) DETACH DELETE s")
            print(f"  Deleted {old_count} subjects")

def create_constraints_and_indexes(driver):
    """Create constraints and indexes"""
    print("\n[STEP 2] Creating constraints and indexes...")
    
    with driver.session() as session:
        # Unique constraint on lcsh_id
        try:
            session.run("CREATE CONSTRAINT subject_lcsh_id IF NOT EXISTS FOR (s:Subject) REQUIRE s.lcsh_id IS UNIQUE")
            print("  Created unique constraint on Subject.lcsh_id")
        except:
            print("  Constraint already exists")
        
        # Index on label
        try:
            session.run("CREATE INDEX subject_label IF NOT EXISTS FOR (s:Subject) ON (s.label)")
            print("  Created index on Subject.label")
        except:
            print("  Index already exists")
        
        # Index on lcc_code
        try:
            session.run("CREATE INDEX subject_lcc IF NOT EXISTS FOR (s:Subject) ON (s.lcc_code)")
            print("  Created index on Subject.lcc_code")
        except:
            print("  Index already exists")

def import_subjects(driver, csv_file):
    """Import subjects from CSV"""
    print("\n[STEP 3] Importing subjects from CSV...")
    
    subjects = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        subjects = list(reader)
    
    print(f"  Read {len(subjects)} subjects from CSV")
    
    with driver.session() as session:
        imported = 0
        for subject in subjects:
            # Clean empty strings to None
            dewey = subject['dewey_decimal'] if subject['dewey_decimal'] else None
            fast = subject['fast_id'] if subject['fast_id'] else None
            broader = subject['broader_lcsh'] if subject['broader_lcsh'] else None
            
            session.run("""
                MERGE (s:Subject {lcsh_id: $lcsh_id})
                SET s.label = $label,
                    s.lcc_code = $lcc_code,
                    s.dewey_decimal = $dewey,
                    s.fast_id = $fast,
                    s.broader_lcsh = $broader,
                    s.unique_id = 'lcsh:' + $lcsh_id,
                    s.source = 'wikidata'
            """,
                lcsh_id=subject['lcsh_id'],
                label=subject['label'],
                lcc_code=subject['lcc_code'],
                dewey=dewey,
                fast=fast,
                broader=broader
            )
            
            imported += 1
            if imported % 50 == 0:
                print(f"  Progress: {imported}/{len(subjects)}...")
    
    print(f"  Imported {imported} subjects")
    return imported

def create_hierarchy(driver):
    """Create BROADER_THAN relationships"""
    print("\n[STEP 4] Creating hierarchy relationships...")
    
    with driver.session() as session:
        result = session.run("""
            MATCH (child:Subject)
            WHERE child.broader_lcsh IS NOT NULL
            MATCH (parent:Subject {lcsh_id: child.broader_lcsh})
            MERGE (parent)-[r:BROADER_THAN]->(child)
            RETURN count(r) as total
        """)
        
        count = result.single()['total']
        print(f"  Created {count} BROADER_THAN relationships")
        return count

def verify_import(driver):
    """Verify the import"""
    print("\n[STEP 5] Verifying import...")
    
    with driver.session() as session:
        # Total count
        result = session.run("MATCH (s:Subject) RETURN count(s) as total")
        total = result.single()['total']
        
        # Coverage stats
        result = session.run("""
            MATCH (s:Subject)
            RETURN 
                count(s) as total,
                count(s.lcc_code) as with_lcc,
                count(s.dewey_decimal) as with_dewey,
                count(s.fast_id) as with_fast,
                count(s.broader_lcsh) as with_broader
        """)
        
        stats = result.single()
        
        print(f"\n  Total Subjects:     {stats['total']}")
        print(f"  With LCC:           {stats['with_lcc']} (100%)")
        print(f"  With Dewey:         {stats['with_dewey']} ({stats['with_dewey']/stats['total']*100:.1f}%)")
        print(f"  With FAST:          {stats['with_fast']} ({stats['with_fast']/stats['total']*100:.1f}%)")
        print(f"  With Broader Link:  {stats['with_broader']} ({stats['with_broader']/stats['total']*100:.1f}%)")
        
        # Sample Rome subjects
        print("\n  Sample Rome subjects:")
        result = session.run("""
            MATCH (s:Subject)
            WHERE s.label CONTAINS 'Rome'
            RETURN s.lcsh_id, s.label, s.lcc_code, s.dewey_decimal
            ORDER BY size(s.label) DESC
            LIMIT 5
        """)
        
        for r in result:
            print(f"\n    {r['s.lcsh_id']}: {r['s.label']}")
            print(f"      LCC:   {r['s.lcc_code']}")
            print(f"      Dewey: {r['s.dewey_decimal'] or 'N/A'}")

def main():
    print("="*80)
    print("IMPORT LCSH CLASS D SUBJECTS TO NEO4J")
    print("="*80)
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        clear_existing_subjects(driver)
        create_constraints_and_indexes(driver)
        import_subjects(driver, INPUT_FILE)
        create_hierarchy(driver)
        verify_import(driver)
        
        print("\n" + "="*80)
        print("[SUCCESS] Import complete!")
        print("="*80)
        
    finally:
        driver.close()

if __name__ == "__main__":
    main()

