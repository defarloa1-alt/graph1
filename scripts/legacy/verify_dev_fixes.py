#!/usr/bin/env python3
"""QA Verification: Test Dev's REQ-FUNC-001 Implementation"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("=" * 80)
print("QA VERIFICATION: Testing Dev's REQ-FUNC-001 Implementation")
print("=" * 80)
print()

test_results = {"passed": 0, "failed": 0}

with driver.session() as session:
    # TEST 1: Verify Duplicates Removed
    print("TEST 1: Verify Duplicates Removed")
    print("-" * 80)
    
    total = session.run('MATCH (n:Entity) RETURN count(n) as count').single()['count']
    unique_qids = session.run('MATCH (n:Entity) RETURN count(DISTINCT n.qid) as count').single()['count']
    unique_ciphers = session.run('MATCH (n:Entity) WHERE n.entity_cipher IS NOT NULL RETURN count(DISTINCT n.entity_cipher) as count').single()['count']
    
    print(f'Total Entity nodes: {total}')
    print(f'Unique QIDs: {unique_qids}')
    print(f'Unique Ciphers: {unique_ciphers}')
    print(f'Expected: 300')
    
    if total == 300 and unique_qids == 300 and unique_ciphers == 300:
        print("[PASS] All counts match expected (300)")
        test_results["passed"] += 1
    else:
        print(f"[FAIL] Count mismatch - Total:{total}, QIDs:{unique_qids}, Ciphers:{unique_ciphers}")
        test_results["failed"] += 1
    print()
    
    # TEST 2: Verify No Duplicate Ciphers
    print("TEST 2: Verify No Duplicate Ciphers (Original Test 5)")
    print("-" * 80)
    
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.entity_cipher IS NOT NULL
        WITH n.entity_cipher as cipher, count(n) as count
        WHERE count > 1
        RETURN cipher, count
        ORDER BY count DESC
    """)
    duplicates = list(result)
    
    if len(duplicates) == 0:
        print("[PASS] No duplicate ciphers found!")
        test_results["passed"] += 1
    else:
        print(f"[FAIL] Found {len(duplicates)} duplicate ciphers:")
        for dup in duplicates[:5]:
            print(f"  {dup['cipher']}: {dup['count']} instances")
        test_results["failed"] += 1
    print()
    
    # TEST 3: Verify No Duplicate QIDs
    print("TEST 3: Verify No Duplicate QIDs")
    print("-" * 80)
    
    result = session.run("""
        MATCH (n:Entity)
        WITH n.qid as qid, count(n) as count
        WHERE count > 1
        RETURN qid, count
        ORDER BY count DESC
    """)
    dup_qids = list(result)
    
    if len(dup_qids) == 0:
        print("[PASS] No duplicate QIDs found!")
        test_results["passed"] += 1
    else:
        print(f"[FAIL] Found {len(dup_qids)} duplicate QIDs:")
        for dup in dup_qids[:5]:
            print(f"  QID {dup['qid']}: {dup['count']} instances")
        test_results["failed"] += 1
    print()
    
    # TEST 4: Verify Seed Entity Still Exists
    print("TEST 4: Verify Seed Entity (Q17167) Integrity")
    print("-" * 80)
    
    result = session.run("""
        MATCH (n:Entity {qid: 'Q17167'})
        RETURN n.label as label, n.entity_type as type, 
               n.entity_cipher as cipher, count(n) as count
    """)
    
    if result.peek():
        record = result.single()
        if (record['count'] == 1 and 
            record['label'] == 'Roman Republic' and
            record['cipher'] == 'ent_sub_Q17167'):
            print(f"[PASS] Q17167 exists and is unique")
            print(f"  Label: {record['label']}")
            print(f"  Type: {record['type']}")
            print(f"  Cipher: {record['cipher']}")
            test_results["passed"] += 1
        else:
            print(f"[FAIL] Q17167 integrity issue")
            print(f"  Count: {record['count']} (expected 1)")
            test_results["failed"] += 1
    else:
        print("[FAIL] Q17167 (Roman Republic) not found!")
        test_results["failed"] += 1
    print()
    
    # TEST 5: Check if Constraints Exist
    print("TEST 5: Verify Uniqueness Constraints")
    print("-" * 80)
    
    try:
        result = session.run("SHOW CONSTRAINTS")
        constraints = list(result)
        
        entity_constraints = [c for c in constraints if 'Entity' in str(c.get('labelsOrTypes', ''))]
        
        print(f"Found {len(entity_constraints)} constraints on Entity label:")
        for c in entity_constraints:
            print(f"  - {c.get('name', 'N/A')}")
        
        # Check for specific constraints
        has_cipher = any('cipher' in str(c.get('name', '')).lower() for c in entity_constraints)
        has_qid = any('qid' in str(c.get('name', '')).lower() for c in entity_constraints)
        
        if has_cipher and has_qid:
            print("[PASS] Uniqueness constraints found")
            test_results["passed"] += 1
        else:
            print("[WARNING] Some constraints may be missing")
            print(f"  entity_cipher constraint: {has_cipher}")
            print(f"  qid constraint: {has_qid}")
            test_results["failed"] += 1
    except Exception as e:
        print(f"[WARNING] Could not verify constraints: {e}")
        test_results["failed"] += 1
    print()

driver.close()

# Final Summary
print("=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print(f"Tests Passed: {test_results['passed']}")
print(f"Tests Failed: {test_results['failed']}")
print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
print()

if test_results['failed'] == 0:
    print("STATUS: [PASS] All verification tests passed!")
    print("RECOMMENDATION: Update REQ-FUNC-001 status to VERIFIED")
else:
    print(f"STATUS: [FAIL] {test_results['failed']} test(s) failed")
    print("RECOMMENDATION: Return to Dev for fixes")
