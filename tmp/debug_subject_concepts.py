#!/usr/bin/env python3
from neo4j import GraphDatabase
import json

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum'))
session = driver.session()

try:
    print("\n=== ALL SubjectConcept NODES ===\n")
    result = session.run("""
        MATCH (subj:SubjectConcept)
        RETURN subj.label, subj.subject_id, subj.concept_id, subj.wikidata_qid, subj.facet
        ORDER BY subj.label
    """)
    for record in result:
        print(f"  Label: {record['subj.label']}")
        print(f"    subject_id: {record['subj.subject_id']}")
        print(f"    concept_id: {record['subj.concept_id']}")
        print(f"    wikidata_qid: {record['subj.wikidata_qid']}")
        print(f"    facet: {record['subj.facet']}")
        print()
    
    print("\n=== HIERARCHY EDGES ===\n")
    result = session.run("""
        MATCH (p:SubjectConcept)-[r:HAS_CHILD_CONCEPT]->(c:SubjectConcept)
        RETURN p.label AS parent, c.label AS child, type(r) AS rel_type
    """)
    rec_count = 0
    for record in result:
        print(f"  {record['parent']} -[:HAS_CHILD_CONCEPT]-> {record['child']}")
        rec_count += 1
    if rec_count == 0:
        print("  ⚠ NO HIERARCHY EDGES FOUND")
    
    print("\n=== REGISTRY ===\n")
    result = session.run("""
        MATCH (reg:SubjectConceptRegistry)-[r:CONTAINS]->(subj:SubjectConcept)
        RETURN reg.registry_id, count(*) AS concept_count
    """)
    for record in result:
        print(f"  Registry: {record['reg.registry_id']}")
        print(f"  Concepts linked: {record['concept_count']}")
    
finally:
    session.close()
    driver.close()
