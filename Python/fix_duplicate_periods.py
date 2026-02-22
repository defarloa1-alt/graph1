#!/usr/bin/env python3
"""Fix duplicate Period nodes with same QID"""

import re
from neo4j import GraphDatabase

def extract_qid(uri):
    """Extract QID from URI"""
    match = re.search(r'Q\d+', str(uri))
    if match:
        return match.group(0)
    return None

uri = 'bolt://127.0.0.1:7687'
username = 'neo4j'
password = 'Chrystallum'

driver = GraphDatabase.driver(uri, auth=(username, password))

print("=" * 70)
print("FIXING DUPLICATE PERIOD NODES")
print("=" * 70)

try:
    with driver.session() as session:
        # Find remaining URI-format QIDs
        print("\n[STEP 1] Finding remaining URI-format QIDs...")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid CONTAINS 'http'
            RETURN p.qid as qid_uri, p.label as label
        """)
        
        uri_periods = list(result)
        print(f"  Found {len(uri_periods)} Period nodes with URI-format QIDs")
        
        for period in uri_periods:
            qid_uri = period['qid_uri']
            label = period['label']
            qid_clean = extract_qid(qid_uri)
            print(f"    {qid_uri} ({label}) -> {qid_clean}")
        
        # Fix duplicates
        print("\n[STEP 2] Handling duplicates...")
        
        for period in uri_periods:
            qid_uri = period['qid_uri']
            qid_clean = extract_qid(qid_uri)
            
            # Check if clean version exists
            result = session.run("""
                MATCH (p_clean:Period {qid: $qid_clean})
                MATCH (p_uri:Period {qid: $qid_uri})
                RETURN p_clean, p_uri,
                       elementId(p_clean) as id_clean,
                       elementId(p_uri) as id_uri,
                       count(*) as count
            """, qid_clean=qid_clean, qid_uri=qid_uri)
            
            dup = result.single()
            if dup and dup['count'] > 0:
                print(f"\n  Duplicate found for {qid_clean}:")
                print(f"    URI version: {qid_uri}")
                print(f"    Clean version: {qid_clean}")
                
                # Compare properties
                p_uri = dup['p_uri']
                p_clean = dup['p_clean']
                
                # Delete URI version (clean version already exists)
                session.run("""
                    MATCH (p_uri:Period {qid: $qid_uri})
                    DETACH DELETE p_uri
                """, qid_uri=qid_uri)
                
                print(f"    Deleted duplicate URI version (keeping clean version)")
            else:
                # No duplicate, just update QID
                session.run("""
                    MATCH (p:Period {qid: $qid_uri})
                    SET p.qid = $qid_clean
                """, qid_uri=qid_uri, qid_clean=qid_clean)
                print(f"  Updated {qid_uri} -> {qid_clean}")
        
        # Verify
        print("\n[STEP 3] Final verification...")
        result = session.run("""
            MATCH (p:Period)
            WHERE p.qid CONTAINS 'http'
            RETURN count(p) as still_uri
        """)
        
        still_uri = result.single()['still_uri']
        
        result = session.run("MATCH (p:Period) RETURN count(p) as total")
        total = result.single()['total']
        
        print(f"  Total Period nodes: {total}")
        print(f"  Periods still in URI format: {still_uri}")
        
        if still_uri == 0:
            print("\n[SUCCESS] All Period QIDs are now clean!")
        else:
            print(f"\n[WARNING] {still_uri} Period QIDs still need fixing")

finally:
    driver.close()

