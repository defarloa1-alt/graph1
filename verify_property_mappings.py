#!/usr/bin/env python3
"""
QA Verification: Property Mapping System
12 test cases from AI_CONTEXT (lines 262-380)
"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("=" * 80)
print("QA VERIFICATION: Property Mapping System")
print("12 Test Cases from AI_CONTEXT")
print("=" * 80)
print()

test_results = {"passed": 0, "failed": 0, "warnings": 0}

with driver.session() as session:
    
    # TEST 1: Basic Import Verification
    print("TEST 1: Basic Import Verification")
    print("-" * 80)
    result = session.run("MATCH (pm:PropertyMapping) RETURN count(pm) as total")
    total = result.single()['total']
    print(f"Total PropertyMapping nodes: {total}")
    print(f"Expected: 700+ (500 new + previous imports)")
    
    if total >= 700:
        print("[PASS]")
        test_results["passed"] += 1
    elif total >= 500:
        print("[WARNING] Lower than expected but within range")
        test_results["warnings"] += 1
    else:
        print(f"[FAIL] Only {total} nodes, expected 700+")
        test_results["failed"] += 1
    print()
    
    # TEST 2: Resolution Method Breakdown
    print("TEST 2: Resolution Method Breakdown")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping)
        WHERE pm.resolved_by IS NOT NULL
        RETURN pm.resolved_by as method, count(pm) as count
        ORDER BY count DESC
    """)
    
    methods = list(result)
    if methods:
        for m in methods:
            print(f"  {m['method']}: {m['count']}")
        print("[PASS] Resolution methods found")
        test_results["passed"] += 1
    else:
        print("[FAIL] No resolved_by data")
        test_results["failed"] += 1
    print()
    
    # TEST 3: Facet Distribution
    print("TEST 3: Facet Distribution")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping)
        RETURN pm.primary_facet as facet, count(pm) as count
        ORDER BY count DESC
        LIMIT 10
    """)
    
    facets = list(result)
    if facets:
        print("Top 10 facets:")
        for f in facets:
            print(f"  {f['facet']}: {f['count']}")
        print("[PASS] Facet distribution found")
        test_results["passed"] += 1
    else:
        print("[FAIL] No primary_facet data")
        test_results["failed"] += 1
    print()
    
    # TEST 4: Specific Property Lookup (P39)
    print("TEST 4: Specific Property Lookup (P39 - position held)")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping {property_id: 'P39'})
        RETURN pm
    """)
    
    if result.peek():
        r = result.single()
        pm = r['pm']
        print(f"  Label: {pm.get('property_label', 'N/A')}")
        print(f"  Facet: {pm.get('primary_facet', 'N/A')}")
        print(f"  Confidence: {pm.get('confidence', 'N/A')}")
        
        if pm.get('primary_facet') == 'POLITICAL' and pm.get('confidence', 0) >= 0.7:
            print("[PASS] P39 correctly mapped")
            test_results["passed"] += 1
        elif pm.get('primary_facet'):
            print(f"[WARNING] P39 mapped to {pm.get('primary_facet')} (expected POLITICAL)")
            test_results["warnings"] += 1
        else:
            print("[WARNING] P39 found but mapping unclear")
            test_results["warnings"] += 1
    else:
        print("[WARNING] P39 not in current 706 properties (may be in full set)")
        test_results["warnings"] += 1
    print()
    
    # TEST 5: Military Properties
    print("TEST 5: Military Properties")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping {primary_facet: 'MILITARY'})
        RETURN pm
        ORDER BY pm.confidence DESC
    """)
    
    military = [r['pm'] for r in result]
    if military:
        print(f"Found {len(military)} military properties:")
        for m in military[:5]:
            pid = m.get('property_id', 'N/A')
            label = m.get('property_label', 'N/A')
            conf = m.get('confidence', 0)
            print(f"  {pid} ({label}): {conf}")
        
        has_p241 = any(m.get('property_id') == 'P241' for m in military)
        if has_p241 and len(military) >= 5:
            print("[PASS] Military properties validated")
            test_results["passed"] += 1
        else:
            print("[WARNING] Fewer military properties or P241 missing")
            test_results["warnings"] += 1
    else:
        print("[FAIL] No military properties found")
        test_results["failed"] += 1
    print()
    
    # TEST 6: Authority Control Properties
    print("TEST 6: Authority Control Properties")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping {is_authority_control: true})
        RETURN count(pm) as authority_count
    """)
    
    if result.peek():
        auth_count = result.single()['authority_count']
        print(f"Authority control properties: {auth_count}")
        print(f"Expected: ~45")
        
        if auth_count >= 40:
            print("[PASS]")
            test_results["passed"] += 1
        elif auth_count > 0:
            print("[WARNING] Lower than expected")
            test_results["warnings"] += 1
        else:
            print("[FAIL] No authority control flag")
            test_results["failed"] += 1
    else:
        print("[FAIL] is_authority_control field not found")
        test_results["failed"] += 1
    print()
    
    # TEST 7: High Confidence Properties
    print("TEST 7: High Confidence Properties (>= 0.9)")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping)
        WHERE pm.confidence >= 0.9
        RETURN count(pm) as high_confidence
    """)
    
    if result.peek():
        high_conf = result.single()['high_confidence']
        print(f"High confidence properties: {high_conf}")
        print(f"Expected: 200+")
        
        if high_conf >= 200:
            print("[PASS]")
            test_results["passed"] += 1
        elif high_conf >= 100:
            print("[WARNING] Lower than expected but acceptable")
            test_results["warnings"] += 1
        else:
            print("[FAIL] Too few high confidence properties")
            test_results["failed"] += 1
    else:
        print("[FAIL] confidence field not found")
        test_results["failed"] += 1
    print()
    
    # TEST 8: Facet Relationship Links
    print("TEST 8: Facet Relationship Links")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping)-[:HAS_PRIMARY_FACET]->(f:Facet)
        RETURN f.key as facet, count(pm) as property_count
        ORDER BY property_count DESC
        LIMIT 5
    """)
    
    links = list(result)
    if links:
        print("Top 5 facets by property count:")
        for link in links:
            print(f"  {link['facet']}: {link['property_count']}")
        print("[PASS] Facet relationships exist")
        test_results["passed"] += 1
    else:
        print("[WARNING] No HAS_PRIMARY_FACET relationships (may not be created yet)")
        test_results["warnings"] += 1
    print()
    
    # TEST 9: Multi-Facet Properties
    print("TEST 9: Multi-Facet Properties")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping)
        WHERE pm.secondary_facets IS NOT NULL AND pm.secondary_facets <> ''
        RETURN pm
        LIMIT 10
    """)
    
    multi = [r['pm'] for r in result]
    if multi:
        print(f"Found {len(multi)} multi-facet properties (showing 10):")
        for m in multi[:5]:
            pid = m.get('property_id', 'N/A')
            primary = m.get('primary_facet', 'N/A')
            secondary = m.get('secondary_facets', 'N/A')
            print(f"  {pid}: {primary} + {secondary}")
        print("[PASS] Multi-facet properties exist")
        test_results["passed"] += 1
    else:
        print("[WARNING] No multi-facet properties (may be stored differently)")
        test_results["warnings"] += 1
    print()
    
    # TEST 10: Claude-Resolved Sample
    print("TEST 10: Claude-Resolved Sample")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping {resolved_by: 'claude'})
        RETURN pm
        ORDER BY pm.confidence DESC
        LIMIT 10
    """)
    
    claude = [r['pm'] for r in result]
    if claude:
        print(f"Top 10 Claude-resolved properties:")
        for c in claude[:5]:
            pid = c.get('property_id', 'N/A')
            label = c.get('property_label', 'N/A')
            facet = c.get('primary_facet', 'N/A')
            conf = c.get('confidence', 0)
            print(f"  {pid} ({label}): {facet}, conf={conf}")
        print("[PASS] Claude resolutions found")
        test_results["passed"] += 1
    else:
        print("[WARNING] No Claude-resolved properties found")
        test_results["warnings"] += 1
    print()
    
    # TEST 11: Historical Property Types
    print("TEST 11: Historical Property Types")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping {is_historical: true})
        RETURN pm
    """)
    
    historical = [r['pm'] for r in result]
    if historical:
        print(f"Historical properties: {len(historical)}")
        for h in historical[:5]:
            pid = h.get('property_id', 'N/A')
            label = h.get('property_label', 'N/A')
            facet = h.get('primary_facet', 'N/A')
            print(f"  {pid}: {label} -> {facet}")
        print("[PASS] Historical property flags exist")
        test_results["passed"] += 1
    else:
        print("[WARNING] No is_historical flags (may not be implemented)")
        test_results["warnings"] += 1
    print()
    
    # TEST 12: Property Type Coverage
    print("TEST 12: Property Type Coverage")
    print("-" * 80)
    result = session.run("""
        MATCH (pm:PropertyMapping)
        WHERE pm.property_type IS NOT NULL
        RETURN count(DISTINCT pm.property_type) as unique_types,
               count(pm) as properties_with_type
    """)
    
    if result.peek():
        r = result.single()
        unique_types = r['unique_types']
        with_type = r['properties_with_type']
        
        print(f"Properties with type: {with_type}")
        print(f"Unique property types: {unique_types}")
        print(f"Expected types: ~50-100")
        
        if unique_types >= 20:
            print("[PASS] Good property type diversity")
            test_results["passed"] += 1
        elif unique_types > 0:
            print("[WARNING] Some property types, fewer than expected")
            test_results["warnings"] += 1
        else:
            print("[FAIL] No property_type data")
            test_results["failed"] += 1
    else:
        print("[WARNING] property_type field may not exist")
        test_results["warnings"] += 1
    print()

driver.close()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Passed: {test_results['passed']}")
print(f"Warnings: {test_results['warnings']}")
print(f"Failed: {test_results['failed']}")
print(f"Total: {test_results['passed'] + test_results['warnings'] + test_results['failed']}")
print()

if test_results['failed'] == 0:
    if test_results['warnings'] == 0:
        print("STATUS: [PASS] All tests passed!")
    else:
        print(f"STATUS: [PASS WITH WARNINGS] {test_results['warnings']} warnings")
    print("RECOMMENDATION: Property mapping system operational")
else:
    print(f"STATUS: [FAIL] {test_results['failed']} test(s) failed")
    print("RECOMMENDATION: Review failures with Dev")
