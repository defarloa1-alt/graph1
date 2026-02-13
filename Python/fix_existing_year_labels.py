#!/usr/bin/env python3
"""
Fix existing Year nodes - copy name to label so they display in graph
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def fix_year_labels(uri="bolt://127.0.0.1:7687", user="neo4j", password="Chrystallum"):
    """
    Fix existing Year nodes - set label property from name or year_value
    """
    print("="*80)
    print("FIX YEAR NODE LABELS")
    print("="*80)
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Check current state
            print("\n[STEP 1] Checking current state...")
            result = session.run("""
                MATCH (y:Year)
                RETURN count(y) as total,
                       count(y.label) as with_label,
                       count(y.name) as with_name
            """)
            stats = result.single()
            
            print(f"  Total Year nodes: {stats['total']}")
            print(f"  With 'label' property: {stats['with_label']}")
            print(f"  With 'name' property: {stats['with_name']}")
            
            if stats['total'] == 0:
                print("\n  No Year nodes found!")
                return False
            
            # Sample before fix
            print("\n[STEP 2] Sample Year nodes before fix...")
            result = session.run("""
                MATCH (y:Year)
                RETURN y.year_value as year, y.label as label, y.name as name
                ORDER BY y.year_value
                LIMIT 3
            """)
            
            for record in result:
                print(f"  Year {record['year']}: label='{record['label']}', name='{record['name']}'")
            
            # Fix: Copy name to label, or generate from year_value
            print("\n[STEP 3] Fixing labels...")
            
            # Strategy 1: If name exists, copy to label
            result = session.run("""
                MATCH (y:Year)
                WHERE y.name IS NOT NULL AND y.name <> ''
                SET y.label = y.name
                RETURN count(y) as updated
            """)
            from_name = result.single()['updated']
            print(f"  Set label from name: {from_name} nodes")
            
            # Strategy 2: If no name, generate from year_value
            result = session.run("""
                MATCH (y:Year)
                WHERE (y.label IS NULL OR y.label = '')
                  AND y.year_value IS NOT NULL
                SET y.label = CASE 
                    WHEN y.year_value < 0 THEN toString(abs(y.year_value)) + ' BCE'
                    ELSE toString(y.year_value) + ' CE'
                END,
                y.name = y.label,
                y.cidoc_crm_class = 'E52_Time-Span',
                y.unique_id = 'YEAR_' + toString(y.year_value)
                RETURN count(y) as updated
            """)
            from_year = result.single()['updated']
            print(f"  Generated label from year_value: {from_year} nodes")
            
            # Verify
            print("\n[STEP 4] Verification...")
            result = session.run("""
                MATCH (y:Year)
                RETURN count(y) as total,
                       count(y.label) as with_label,
                       count(CASE WHEN y.label IS NOT NULL AND y.label <> '' THEN 1 END) as non_empty_label
            """)
            final = result.single()
            
            print(f"  Total Year nodes: {final['total']}")
            print(f"  With label property: {final['with_label']}")
            print(f"  With non-empty label: {final['non_empty_label']}")
            
            # Sample after fix
            print("\n[STEP 5] Sample Year nodes after fix...")
            result = session.run("""
                MATCH (y:Year)
                RETURN y.year_value as year, y.label as label, y.name as name
                ORDER BY y.year_value
                LIMIT 5
            """)
            
            for record in result:
                print(f"  Year {record['year']}: label='{record['label']}', name='{record['name']}'")
            
            print("\n" + "="*80)
            print("LABELS FIXED")
            print("="*80)
            
            if final['non_empty_label'] == final['total']:
                print("[SUCCESS] All Year nodes now have labels for display!")
            else:
                missing = final['total'] - final['non_empty_label']
                print(f"[WARNING] {missing} Year nodes still missing labels")
            
    finally:
        driver.close()
    
    return True

if __name__ == "__main__":
    fix_year_labels()

