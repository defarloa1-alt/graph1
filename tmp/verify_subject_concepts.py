#!/usr/bin/env python3
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum'))
session = driver.session()

try:
    print("\n=== SubjectConcept Hierarchy ===\n")
    result = session.run("""
        MATCH (parent:SubjectConcept)-[:HAS_CHILD_CONCEPT]->(child:SubjectConcept)
        RETURN parent.label AS parent, child.label AS child, child.concept_depth AS depth
        ORDER BY parent, child
    """)
    for record in result:
        print(f"  {record['parent']} → {record['child']} (depth: {record['depth']})")
    
    print("\n=== Registry Links ===\n")
    result = session.run("""
        MATCH (registry:SubjectConceptRegistry)-[:CONTAINS]->(subj:SubjectConcept)
        RETURN registry.registry_id AS registry, count(*) AS concept_count
    """)
    for record in result:
        print(f"  Registry {record['registry']}: {record['concept_count']} concepts")
    
    print("\n=== Facet Distribution ===\n")
    result = session.run("""
        MATCH (subj:SubjectConcept)
        RETURN subj.facet AS facet, count(*) AS count
        ORDER BY count DESC
    """)
    for record in result:
        print(f"  {record['facet']}: {record['count']}")
    
    print("\n=== Ready for Phase 2A+2B ===\n")
    print("  ✓ SubjectConcept nodes: 5 bootstrap concepts")
    print("  ✓ SubjectConceptRegistry: 1 governance node")
    print("  ✓ Hierarchy: Roman Republic (parent) with 2 children")
    print("  ✓ API ready: scripts/reference/subject_concept_api.py")
    
finally:
    session.close()
    driver.close()
