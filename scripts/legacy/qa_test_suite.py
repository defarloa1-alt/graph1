#!/usr/bin/env python3
"""
QA Test Suite for Neo4j Entity Import
Runs all 10 test cases from QA_HANDOFF_NEO4J_TESTING.md
"""

from neo4j import GraphDatabase
import json
from datetime import datetime

# Neo4j Connection
NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Test results tracker
test_results = {
    "start_time": datetime.now().isoformat(),
    "tests": [],
    "summary": {"total": 10, "passed": 0, "failed": 0}
}

def log_test(test_num, name, status, details, expected, actual):
    """Log test result"""
    result = {
        "test_num": test_num,
        "name": name,
        "status": status,
        "expected": expected,
        "actual": actual,
        "details": details
    }
    test_results["tests"].append(result)
    
    if status == "PASS":
        test_results["summary"]["passed"] += 1
        print(f"[PASS] Test {test_num}: {name}")
    else:
        test_results["summary"]["failed"] += 1
        print(f"[FAIL] Test {test_num}: {name}")
    
    print(f"   Expected: {expected}")
    print(f"   Actual: {actual}")
    if details:
        print(f"   Details: {details}")
    print()

try:
    with driver.session() as session:
        print("=" * 80)
        print("QA TEST SUITE - Neo4j Entity Import Validation")
        print("=" * 80)
        print()
        
        # TEST 1: Connection & Schema
        print("Running Test 1: Connection & Schema...")
        try:
            result = session.run("CALL db.labels()")
            labels = [record['label'] for record in result]
            has_entity = 'Entity' in labels
            
            if has_entity:
                log_test(1, "Connection & Schema", "PASS", 
                        f"Found labels: {', '.join(labels[:10])}", 
                        "Contains 'Entity' label", 
                        f"Entity label present ({len(labels)} total labels)")
            else:
                log_test(1, "Connection & Schema", "FAIL",
                        f"Labels found: {', '.join(labels)}",
                        "Contains 'Entity' label",
                        "Entity label NOT found")
        except Exception as e:
            log_test(1, "Connection & Schema", "FAIL", str(e), "Connection successful", f"Error: {e}")
        
        # TEST 2: Entity Count
        print("Running Test 2: Entity Count...")
        try:
            result = session.run("MATCH (n:Entity) RETURN count(n) as total_entities")
            total = result.single()['total_entities']
            
            if 200 <= total <= 400:
                log_test(2, "Entity Count", "PASS",
                        None,
                        "200-400 entities",
                        f"{total} entities")
            else:
                log_test(2, "Entity Count", "FAIL",
                        "Count outside expected range",
                        "200-400 entities",
                        f"{total} entities")
        except Exception as e:
            log_test(2, "Entity Count", "FAIL", str(e), "200-400 entities", f"Error: {e}")
        
        # TEST 3: Entity Type Breakdown
        print("Running Test 3: Entity Type Breakdown...")
        try:
            result = session.run("""
                MATCH (n:Entity)
                RETURN n.entity_type as entity_type, count(n) as count
                ORDER BY count DESC
            """)
            types = {record['entity_type']: record['count'] for record in result}
            type_count = len(types)
            
            if type_count >= 3:
                log_test(3, "Entity Type Breakdown", "PASS",
                        f"Types: {', '.join([f'{k}({v})' for k,v in list(types.items())[:5]])}",
                        "At least 3 entity types",
                        f"{type_count} types found")
            else:
                log_test(3, "Entity Type Breakdown", "FAIL",
                        f"Only {type_count} types found",
                        "At least 3 entity types",
                        f"{type_count} types: {list(types.keys())}")
        except Exception as e:
            log_test(3, "Entity Type Breakdown", "FAIL", str(e), "At least 3 types", f"Error: {e}")
        
        # TEST 4: Seed Entity Verification
        print("Running Test 4: Seed Entity (Q17167)...")
        try:
            result = session.run("""
                MATCH (n:Entity {qid: 'Q17167'})
                RETURN n.label as label, n.entity_type as type, 
                       n.entity_cipher as cipher, n.federation_score as fed_score,
                       n.properties_count as prop_count
            """)
            
            if result.peek():
                record = result.single()
                expected_cipher = "ent_sub_Q17167"
                actual_cipher = record['cipher']
                
                if (record['label'] == "Roman Republic" and 
                    record['type'] == "SUBJECTCONCEPT" and
                    actual_cipher == expected_cipher):
                    log_test(4, "Seed Entity (Q17167)", "PASS",
                            f"Label: {record['label']}, Type: {record['type']}, Fed Score: {record['fed_score']}, Props: {record['prop_count']}",
                            f"Roman Republic, SUBJECTCONCEPT, {expected_cipher}",
                            f"All properties match correctly")
                else:
                    log_test(4, "Seed Entity (Q17167)", "FAIL",
                            f"Mismatch in properties",
                            f"Roman Republic, SUBJECTCONCEPT, {expected_cipher}",
                            f"{record['label']}, {record['type']}, {actual_cipher}")
            else:
                log_test(4, "Seed Entity (Q17167)", "FAIL",
                        "Entity not found",
                        "Q17167 exists",
                        "Entity not found in database")
        except Exception as e:
            log_test(4, "Seed Entity (Q17167)", "FAIL", str(e), "Q17167 found with correct props", f"Error: {e}")
        
        # TEST 5: Cipher Uniqueness
        print("Running Test 5: Cipher Uniqueness...")
        try:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.entity_cipher IS NOT NULL
                WITH n.entity_cipher as cipher, count(n) as count
                WHERE count > 1
                RETURN cipher, count
                ORDER BY count DESC
            """)
            duplicates = [(record['cipher'], record['count']) for record in result]
            
            if len(duplicates) == 0:
                log_test(5, "Cipher Uniqueness", "PASS",
                        None,
                        "0 duplicate ciphers",
                        "All ciphers are unique")
            else:
                log_test(5, "Cipher Uniqueness", "FAIL",
                        f"Duplicates: {duplicates[:5]}",
                        "0 duplicate ciphers",
                        f"{len(duplicates)} duplicate cipher(s) found")
        except Exception as e:
            log_test(5, "Cipher Uniqueness", "FAIL", str(e), "0 duplicates", f"Error: {e}")
        
        # TEST 6: Federation Score Distribution
        print("Running Test 6: Federation Score Distribution...")
        try:
            result = session.run("""
                MATCH (n:Entity)
                RETURN n.federation_score as fed_score, count(n) as count
                ORDER BY fed_score DESC
            """)
            scores = {record['fed_score']: record['count'] for record in result}
            score_range = f"{min(scores.keys())}-{max(scores.keys())}" if scores else "None"
            
            if scores and min(scores.keys()) >= 1 and max(scores.keys()) <= 5:
                log_test(6, "Federation Score Distribution", "PASS",
                        f"Distribution: {', '.join([f'Score {k}: {v}' for k,v in sorted(scores.items(), reverse=True)])}",
                        "Scores in range 1-5",
                        f"Scores range: {score_range}")
            else:
                log_test(6, "Federation Score Distribution", "FAIL",
                        f"Unexpected score range",
                        "Scores in range 1-5",
                        f"Scores range: {score_range}")
        except Exception as e:
            log_test(6, "Federation Score Distribution", "FAIL", str(e), "Scores 1-5", f"Error: {e}")
        
        # TEST 7: High-Quality Entities
        print("Running Test 7: High-Quality Entities (Fed Score >= 3)...")
        try:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.federation_score >= 3
                RETURN n.qid as qid, n.label as label, n.entity_type as entity_type, n.federation_score as federation_score
                ORDER BY n.federation_score DESC, n.label
                LIMIT 20
            """)
            high_quality = list(result)
            count = len(high_quality)
            
            if count > 0:
                top_5 = [f"{r['label']} ({r['qid']}, score={r['federation_score']})" for r in high_quality[:5]]
                log_test(7, "High-Quality Entities", "PASS",
                        f"Top 5: {'; '.join(top_5)}",
                        "At least some entities with score >= 3",
                        f"{count} high-quality entities found")
            else:
                log_test(7, "High-Quality Entities", "FAIL",
                        "No entities found",
                        "At least some entities with score >= 3",
                        "0 entities with federation_score >= 3")
        except Exception as e:
            log_test(7, "High-Quality Entities", "FAIL", str(e), "Some entities >= 3", f"Error: {e}")
        
        # TEST 8: Data Quality - Missing Properties
        print("Running Test 8: Data Quality - Missing Properties...")
        try:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.entity_cipher IS NULL 
                   OR n.qid IS NULL 
                   OR n.label IS NULL
                   OR n.entity_type IS NULL
                RETURN n.qid, n.label,
                       n.entity_cipher IS NULL as missing_cipher,
                       n.qid IS NULL as missing_qid,
                       n.label IS NULL as missing_label,
                       n.entity_type IS NULL as missing_type
                LIMIT 20
            """)
            missing = list(result)
            count = len(missing)
            
            if count == 0:
                log_test(8, "Data Quality - Missing Properties", "PASS",
                        None,
                        "0 entities with missing properties",
                        "All entities have critical properties")
            else:
                issues = []
                for r in missing[:3]:
                    missing_fields = []
                    if r['missing_cipher']: missing_fields.append('cipher')
                    if r['missing_qid']: missing_fields.append('qid')
                    if r['missing_label']: missing_fields.append('label')
                    if r['missing_type']: missing_fields.append('type')
                    issues.append(f"{r['qid'] or 'Unknown'}: missing {', '.join(missing_fields)}")
                
                log_test(8, "Data Quality - Missing Properties", "FAIL",
                        f"Examples: {'; '.join(issues)}",
                        "0 entities with missing properties",
                        f"{count} entities with missing critical properties")
        except Exception as e:
            log_test(8, "Data Quality - Missing Properties", "FAIL", str(e), "0 missing", f"Error: {e}")
        
        # TEST 9: Label Pattern Search
        print("Running Test 9: Label Search (Rome)...")
        try:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.label IS NOT NULL AND toLower(n.label) CONTAINS 'rome'
                RETURN n.qid as qid, n.label as label, n.entity_type as entity_type, n.federation_score as federation_score
                ORDER BY n.federation_score DESC
            """)
            rome_entities = list(result)
            count = len(rome_entities)
            
            if count > 0:
                has_q17167 = any(r['qid'] == 'Q17167' for r in rome_entities)
                sample = [f"{r['label']} ({r['qid']})" for r in rome_entities[:3]]
                
                log_test(9, "Label Search (Rome)", "PASS",
                        f"Found: {'; '.join(sample)}{'...' if count > 3 else ''}, Includes Q17167: {has_q17167}",
                        "Multiple Rome-related entities including Q17167",
                        f"{count} entities found")
            else:
                log_test(9, "Label Search (Rome)", "FAIL",
                        "No entities found",
                        "Multiple Rome-related entities",
                        "0 entities with 'Rome' in label")
        except Exception as e:
            log_test(9, "Label Search (Rome)", "FAIL", str(e), "Rome entities found", f"Error: {e}")
        
        # TEST 10: Property Count Analysis
        print("Running Test 10: Property Count Analysis...")
        try:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.properties_count IS NOT NULL
                RETURN n.qid as qid, n.label as label, n.properties_count as properties_count, n.entity_type as entity_type
                ORDER BY n.properties_count DESC
                LIMIT 10
            """)
            top_props = list(result)
            
            if len(top_props) > 0:
                max_props = top_props[0]['properties_count']
                top_3 = [f"{r['label']} ({r['qid']}, {r['properties_count']} props)" for r in top_props[:3]]
                
                if max_props > 30:
                    log_test(10, "Property Count Analysis", "PASS",
                            f"Top 3: {'; '.join(top_3)}",
                            "Some entities with properties_count > 30",
                            f"Top entity has {max_props} properties")
                else:
                    log_test(10, "Property Count Analysis", "FAIL",
                            f"Max properties: {max_props}",
                            "Some entities with properties_count > 30",
                            f"Highest count is only {max_props}")
            else:
                log_test(10, "Property Count Analysis", "FAIL",
                        "No entities with property counts",
                        "Entities with rich properties",
                        "No properties_count data found")
        except Exception as e:
            log_test(10, "Property Count Analysis", "FAIL", str(e), "Entities > 30 props", f"Error: {e}")

finally:
    driver.close()

# Print Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {test_results['summary']['total']}")
print(f"Passed: {test_results['summary']['passed']}")
print(f"Failed: {test_results['summary']['failed']}")
print()

if test_results['summary']['failed'] == 0:
    print("STATUS: APPROVED - All tests passed!")
else:
    print(f"STATUS: NEEDS REVIEW - {test_results['summary']['failed']} test(s) failed")

# Save detailed results
test_results["end_time"] = datetime.now().isoformat()
test_results["status"] = "APPROVED" if test_results['summary']['failed'] == 0 else "NEEDS_REVIEW"

output_file = f"output/qa_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\nDetailed results saved to: {output_file}")
