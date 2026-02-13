#!/usr/bin/env python3
"""Fix Period node QIDs from URI format to simple string format"""

import re
from neo4j import GraphDatabase

def extract_qid(uri):
    """Extract QID from URI or return as-is if already a QID"""
    if not uri:
        return None
    # Extract Q followed by digits
    match = re.search(r'Q\d+', str(uri))
    if match:
        return match.group(0)
    return None

uri = 'bolt://127.0.0.1:7687'
username = 'neo4j'
password = 'Chrystallum'

driver = GraphDatabase.driver(uri, auth=(username, password))

print("=" * 70)
print("FIXING PERIOD QIDs: URI FORMAT -> STRING FORMAT")
print("=" * 70)

try:
    with driver.session() as session:
        # Check current QID format
        print("\n[STEP 1] Checking current QID format...")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid IS NOT NULL
            RETURN p.qid as qid_raw
            LIMIT 5
        """)
        
        print("  Sample QIDs:")
        for record in result:
            qid_raw = record['qid_raw']
            qid_clean = extract_qid(qid_raw)
            print(f"    {qid_raw} -> {qid_clean}")
        
        # Count periods needing fixes
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid CONTAINS 'http://www.wikidata.org/entity/'
               OR p.qid STARTS WITH '<'
            RETURN count(p) as needs_fix
        """)
        needs_fix = result.single()['needs_fix']
        
        result = session.run("MATCH (p:Period) RETURN count(p) as total")
        total = result.single()['total']
        
        print(f"\n  Periods needing QID fix: {needs_fix}/{total}")
        
        if needs_fix == 0:
            print("\n[SUCCESS] All Period QIDs are already in correct format!")
            driver.close()
            exit(0)
        
        # Fix QIDs
        print(f"\n[STEP 2] Fixing {needs_fix} Period QIDs...")
        
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid IS NOT NULL
            RETURN p.qid as qid_raw, elementId(p) as id
        """)
        
        periods = list(result)
        updated = 0
        errors = 0
        
        for period in periods:
            qid_raw = period['qid_raw']
            qid_clean = extract_qid(qid_raw)
            
            if qid_clean and qid_clean != qid_raw:
                try:
                    session.run("""
                        MATCH (p:Period)
                        WHERE elementId(p) = $id
                        SET p.qid = $qid_clean
                    """, id=period['id'], qid_clean=qid_clean)
                    updated += 1
                    
                    if updated % 10 == 0:
                        print(f"  Progress: {updated}/{needs_fix}...")
                except Exception as e:
                    errors += 1
                    print(f"  Error fixing {qid_raw}: {e}")
        
        print(f"\n  Updated: {updated} Period QIDs")
        print(f"  Errors: {errors}")
        
        # Verify
        print("\n[STEP 3] Verification...")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid CONTAINS 'http'
               OR p.qid STARTS WITH '<'
            RETURN count(p) as still_uri_format
        """)
        
        still_bad = result.single()['still_uri_format']
        
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid STARTS WITH 'Q'
            RETURN count(p) as correct_format
        """)
        
        correct = result.single()['correct_format']
        
        print(f"  Periods with correct QID format: {correct}/{total}")
        print(f"  Periods still in URI format: {still_bad}")
        
        # Sample after fix
        print("\n[STEP 4] Sample Period QIDs after fix...")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid IS NOT NULL
            RETURN p.qid as qid, p.label as label
            ORDER BY p.label
            LIMIT 5
        """)
        
        for record in result:
            print(f"  {record['qid']}: {record['label']}")
        
        print("\n" + "=" * 70)
        print("QID FIX COMPLETE")
        print("=" * 70)
        
        if still_bad == 0:
            print("[SUCCESS] All Period QIDs are now in correct format!")
        else:
            print(f"[WARNING] {still_bad} Period QIDs still need fixing")

finally:
    driver.close()

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)

