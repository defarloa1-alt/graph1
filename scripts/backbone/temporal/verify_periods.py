#!/usr/bin/env python3
"""Verify all periods meet data quality requirements."""
import sys
import io
from neo4j import GraphDatabase
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def verify_periods(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """Verify all periods meet requirements."""
    
    print("="*80)
    print("Period Data Quality Verification")
    print("="*80)
    print(f"Neo4j: {uri}")
    print()
    
    current_year = datetime.now().year  # 2026
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Check 1: Total periods
        result = session.run("MATCH (p:Period) RETURN count(p) as total")
        total_periods = result.single()['total']
        print(f"[CHECK 1] Total Period nodes: {total_periods}")
        print()
        
        # Check 2: Periods with BOTH start and end dates
        result = session.run("""
            MATCH (p:Period)
            WHERE p.start_year IS NOT NULL AND p.end_year IS NOT NULL
            RETURN count(p) as count
        """)
        with_both_dates = result.single()['count']
        print(f"[CHECK 2] Periods with BOTH start_year AND end_year: {with_both_dates}")
        if with_both_dates == total_periods:
            print("  ✅ PASS: All periods have both dates")
        else:
            missing = total_periods - with_both_dates
            print(f"  ❌ FAIL: {missing} periods missing dates")
            
            # Show which ones are missing
            result = session.run("""
                MATCH (p:Period)
                WHERE p.start_year IS NULL OR p.end_year IS NULL
                RETURN p.label, p.start_year, p.end_year
                LIMIT 10
            """)
            for record in result:
                print(f"     - {record['p.label']}: start={record['p.start_year']}, end={record['p.end_year']}")
        print()
        
        # Check 3: Periods with at least one location
        result = session.run("""
            MATCH (p:Period)-[:LOCATED_IN]->(:Place)
            RETURN count(DISTINCT p) as count
        """)
        with_location = result.single()['count']
        print(f"[CHECK 3] Periods with at least one LOCATED_IN edge: {with_location}")
        if with_location == total_periods:
            print("  ✅ PASS: All periods have location")
        else:
            missing = total_periods - with_location
            print(f"  ❌ FAIL: {missing} periods missing location")
            
            # Show which ones are missing
            result = session.run("""
                MATCH (p:Period)
                WHERE NOT EXISTS((p)-[:LOCATED_IN]->(:Place))
                RETURN p.label, p.start_year, p.end_year
                LIMIT 10
            """)
            for record in result:
                print(f"     - {record['p.label']} ({record['p.start_year']}-{record['p.end_year']})")
        print()
        
        # Check 4: End date after start date
        result = session.run("""
            MATCH (p:Period)
            WHERE p.start_year IS NOT NULL AND p.end_year IS NOT NULL
              AND p.end_year <= p.start_year
            RETURN p.label, p.start_year, p.end_year
        """)
        invalid_range = []
        for record in result:
            invalid_range.append(record)
        
        print(f"[CHECK 4] Periods with end_year <= start_year: {len(invalid_range)}")
        if len(invalid_range) == 0:
            print("  ✅ PASS: All periods have end_year > start_year")
        else:
            print(f"  ❌ FAIL: {len(invalid_range)} periods have invalid date ranges")
            for record in invalid_range[:10]:
                print(f"     - {record['p.label']}: {record['p.start_year']} to {record['p.end_year']}")
        print()
        
        # Check 5: End date not in future
        result = session.run("""
            MATCH (p:Period)
            WHERE p.end_year IS NOT NULL AND p.end_year > $current_year
            RETURN p.label, p.start_year, p.end_year
        """, current_year=current_year)
        future_dates = []
        for record in result:
            future_dates.append(record)
        
        print(f"[CHECK 5] Periods with end_year > {current_year}: {len(future_dates)}")
        if len(future_dates) == 0:
            print(f"  ✅ PASS: No periods end in the future")
        else:
            print(f"  ❌ FAIL: {len(future_dates)} periods have future end dates")
            for record in future_dates[:10]:
                print(f"     - {record['p.label']}: {record['p.start_year']} to {record['p.end_year']}")
        print()
        
        # Summary
        print("="*80)
        print("Summary")
        print("="*80)
        all_checks_pass = (
            with_both_dates == total_periods and
            with_location == total_periods and
            len(invalid_range) == 0 and
            len(future_dates) == 0
        )
        
        if all_checks_pass:
            print("✅ ALL CHECKS PASSED")
            print(f"   {total_periods} periods are fully valid")
        else:
            print("⚠️  SOME CHECKS FAILED")
            print(f"   Valid periods: {total_periods - missing if 'missing' in locals() else total_periods}")
            print(f"   Issues found:")
            if with_both_dates != total_periods:
                print(f"     - {total_periods - with_both_dates} missing dates")
            if with_location != total_periods:
                print(f"     - {total_periods - with_location} missing location")
            if len(invalid_range) > 0:
                print(f"     - {len(invalid_range)} invalid date ranges")
            if len(future_dates) > 0:
                print(f"     - {len(future_dates)} future end dates")
        
        # Bonus: Show location distribution
        print()
        print("[BONUS] Location distribution:")
        result = session.run("""
            MATCH (p:Period)-[:LOCATED_IN]->(place:Place)
            WITH p, count(place) as location_count
            WITH location_count, count(p) as period_count
            RETURN location_count, period_count
            ORDER BY location_count DESC
        """)
        for record in result:
            print(f"  {record['period_count']} periods have {record['location_count']} location(s)")
        
        print("="*80)
    
    driver.close()

if __name__ == "__main__":
    verify_periods()

