#!/usr/bin/env python3
"""Delete all existing SubjectConcept nodes to reload with canonical IDs"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum'))
session = driver.session()

try:
    # Delete all relationships first
    result = session.run("""
        MATCH (subj:SubjectConcept)-[r]-()
        DELETE r
        RETURN count(*) AS rels_deleted
    """)
    rels_deleted = result.single()['rels_deleted']
    print(f'Deleted {rels_deleted} relationships')
    
    # Delete all SubjectConcept nodes
    result = session.run("""
        MATCH (subj:SubjectConcept)
        DELETE subj
        RETURN count(*) AS nodes_deleted
    """)
    nodes_deleted = result.single()['nodes_deleted']
    print(f'Deleted {nodes_deleted} SubjectConcept nodes')
    
    # Delete all SubjectConceptRegistry nodes
    result = session.run("""
        MATCH (reg:SubjectConceptRegistry)
        DELETE reg
        RETURN count(*) AS regs_deleted
    """)
    regs_deleted = result.single()['regs_deleted']
    print(f'Deleted {regs_deleted} SubjectConceptRegistry nodes')
    
    print('\n✓ Ready to reload with canonical subject_ids')
    
finally:
    session.close()
    driver.close()
