#!/usr/bin/env python3
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum'))
session = driver.session()

try:
    # Delete the duplicate Roman Republic (the one with concept_id: None)
    # First delete relationships
    result = session.run("""
        MATCH (subj:SubjectConcept {label: 'Roman Republic'})
        WHERE subj.concept_id IS NULL
        MATCH (subj)-[r]-()
        DELETE r
        RETURN count(*) AS rels_deleted
    """)
    
    rels_deleted = result.single()['rels_deleted']
    print(f'Deleted {rels_deleted} relationships from duplicate')
    
    # Now delete the node
    result = session.run("""
        MATCH (subj:SubjectConcept {label: 'Roman Republic'})
        WHERE subj.concept_id IS NULL
        DELETE subj
        RETURN count(*) AS deleted
    """)
    
    deleted = result.single()['deleted']
    print(f'Deleted {deleted} duplicate Roman Republic node(s)')
    
    # Verify only one Roman Republic remains
    result = session.run("""
        MATCH (subj:SubjectConcept {label: 'Roman Republic'})
        RETURN count(*) AS remaining
    """)
    remaining = result.single()['remaining']
    print(f'Roman Republic nodes remaining: {remaining}')
    
finally:
    session.close()
    driver.close()
