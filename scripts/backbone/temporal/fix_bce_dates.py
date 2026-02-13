#!/usr/bin/env python3
"""
Fix BCE date issues in Period nodes.
- Convert positive BCE years to negative
- Fix periods where end_year < start_year (BCE dates)
"""
import sys
import io
from neo4j import GraphDatabase
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def fix_bce_dates(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """Fix BCE date issues."""
    
    print("="*80)
    print("Fixing BCE Date Issues in Period Nodes")
    print("="*80)
    print(f"Neo4j: {uri}")
    print()
    
    current_year = datetime.now().year
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Fix 1: Periods with future end dates (these are BCE years recorded as positive)
        print("[FIX 1] Converting future dates to BCE (negative)...")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.end_year > $current_year
            RETURN p.label, p.start_year, p.end_year
            ORDER BY p.end_year DESC
        """, current_year=current_year)
        
        future_periods = list(result)
        print(f"   Found {len(future_periods)} periods with future end dates")
        
        for record in future_periods:
            label = record['p.label']
            start = record['p.start_year']
            end = record['p.end_year']
            
            # Convert to negative (BCE)
            new_start = -start if start else None
            new_end = -end if end else None
            
            print(f"   Fixing: {label}")
            print(f"      Before: {start} to {end}")
            print(f"      After:  {new_start} to {new_end} (BCE)")
            
            session.run("""
                MATCH (p:Period {label: $label})
                SET p.start_year = $new_start, p.end_year = $new_end
            """, label=label, new_start=new_start, new_end=new_end)
        
        print()
        
        # Fix 2: Periods where end_year < start_year (inverted BCE dates)
        print("[FIX 2] Fixing inverted date ranges (BCE conversion)...")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.start_year IS NOT NULL AND p.end_year IS NOT NULL
              AND p.end_year < p.start_year
              AND p.start_year < 2026
            RETURN p.label, p.start_year, p.end_year
        """)
        
        inverted_periods = list(result)
        print(f"   Found {len(inverted_periods)} periods with inverted dates")
        
        for record in inverted_periods:
            label = record['p.label']
            start = record['p.start_year']
            end = record['p.end_year']
            
            # Convert both to negative (BCE)
            new_start = -start
            new_end = -end
            
            print(f"   Fixing: {label}")
            print(f"      Before: {start} to {end}")
            print(f"      After:  {new_start} to {new_end} (BCE)")
            
            session.run("""
                MATCH (p:Period {label: $label})
                SET p.start_year = $new_start, p.end_year = $new_end
            """, label=label, new_start=new_start, new_end=new_end)
        
        print()
        
        # Verification
        print("="*80)
        print("Verification After Fixes")
        print("="*80)
        
        # Check dates are valid
        result = session.run("""
            MATCH (p:Period)
            WHERE p.start_year IS NOT NULL AND p.end_year IS NOT NULL
              AND p.end_year <= p.start_year
            RETURN count(p) as count
        """)
        still_invalid = result.single()['count']
        
        result = session.run("""
            MATCH (p:Period)
            WHERE p.end_year > $current_year
            RETURN count(p) as count
        """, current_year=current_year)
        still_future = result.single()['count']
        
        print(f"Periods with end_year <= start_year: {still_invalid}")
        print(f"Periods with future end_year: {still_future}")
        
        if still_invalid == 0 and still_future == 0:
            print("\n✅ ALL DATE ISSUES FIXED!")
        else:
            print(f"\n⚠️  Some issues remain:")
            if still_invalid > 0:
                print(f"   - {still_invalid} periods still have invalid ranges")
            if still_future > 0:
                print(f"   - {still_future} periods still have future dates")
        
        # Show sample fixed periods
        print("\n[SAMPLE] Fixed periods:")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.start_year < 0
            RETURN p.label, p.start_year, p.end_year
            ORDER BY p.start_year
            LIMIT 5
        """)
        for record in result:
            print(f"  {record['p.label']}: {record['p.start_year']} to {record['p.end_year']}")
        
        print("\n" + "="*80)
        print("BCE Date Fixes Complete!")
        print("="*80)
    
    driver.close()

if __name__ == "__main__":
    fix_bce_dates()

