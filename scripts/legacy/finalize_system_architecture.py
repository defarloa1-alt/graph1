#!/usr/bin/env python3
"""
Finalize System Architecture

1. Remove TEMPORAL facet node
2. Add SubjectConceptRegistry
3. Verify complete structure
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("FINALIZING SYSTEM ARCHITECTURE")
print("=" * 80)
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    
    # Step 1: Remove TEMPORAL facet node
    print("[1/2] Removing TEMPORAL facet node...")
    result = session.run("""
        MATCH (temporal:SubjectConcept)
        WHERE temporal.primary_facet = 'TEMPORAL'
        DETACH DELETE temporal
        RETURN count(temporal) AS deleted
    """)
    deleted = result.single()['deleted']
    print(f"  [OK] Deleted {deleted} TEMPORAL facet node(s)")
    print()
    
    # Step 2: Add SubjectConceptRegistry
    print("[2/2] Adding SubjectConceptRegistry...")
    session.run("""
        MATCH (sc_root:SubjectConceptRoot)
        
        CREATE (sc_registry:SubjectConceptRegistry {
          name: 'Subject Concept Registry',
          description: 'Registry of all created SubjectConcepts'
        })
        CREATE (sc_root)-[:HAS_SUBJECT_REGISTRY]->(sc_registry)
        
        WITH sc_registry
        
        // Link all existing SubjectConcepts to registry
        MATCH (sc:SubjectConcept)
        CREATE (sc_registry)-[:CONTAINS]->(sc)
    """)
    
    # Count SubjectConcepts
    result = session.run("MATCH (sc:SubjectConcept) RETURN count(sc) AS total")
    sc_count = result.single()['total']
    
    print(f"  [OK] Created SubjectConceptRegistry")
    print(f"  [OK] Linked {sc_count} SubjectConcepts to registry")
    print()
    
    # Verification
    print("=" * 80)
    print("COMPLETE SYSTEM VERIFICATION")
    print("=" * 80)
    print()
    
    result = session.run("""
        MATCH (sys:Chrystallum)
        
        // Count each branch
        OPTIONAL MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        OPTIONAL MATCH (fed_root)-[:HAS_FEDERATION]->(fed)
        
        OPTIONAL MATCH (sys)-[:HAS_ENTITY_ROOT]->(entity_root)
        OPTIONAL MATCH (entity_root)-[:HAS_ENTITY_TYPE]->(et)
        
        OPTIONAL MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
        OPTIONAL MATCH (facet_root)-[:HAS_FACET]->(facet)
        
        OPTIONAL MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
        OPTIONAL MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)
        OPTIONAL MATCH (agent_reg)-[:HAS_AGENT]->(agent)
        OPTIONAL MATCH (sc_root)-[:HAS_SUBJECT_REGISTRY]->(sc_registry)
        OPTIONAL MATCH (sc_registry)-[:CONTAINS]->(sc)
        
        RETURN 
          count(DISTINCT fed) AS federations,
          count(DISTINCT et) AS entity_types,
          count(DISTINCT facet) AS facets,
          count(DISTINCT agent) AS agents,
          count(DISTINCT sc) AS subject_concepts
    """)
    
    stats = result.single()
    
    print("CHRYSTALLUM SYSTEM:")
    print()
    print(f"  Chrystallum (root)")
    print(f"    |")
    print(f"    |-- FederationRoot")
    print(f"    |   +-- {stats['federations']} Federations")
    print(f"    |       (Pleiades, PeriodO, Wikidata, GeoNames, BabelNet,")
    print(f"    |        WorldCat, LCSH, FAST, LCC, MARC)")
    print(f"    |")
    print(f"    |-- EntityRoot")
    print(f"    |   +-- {stats['entity_types']} Entity Types")
    print(f"    |       (Year->Decade->Century->Millennium,")
    print(f"    |        Place->PlaceType, Period->PeriodCandidate,")
    print(f"    |        Human, Event, Organization, SubjectConcept, Work, Claim)")
    print(f"    |")
    print(f"    |-- FacetRoot")
    print(f"    |   +-- {stats['facets']} Canonical Facets")
    print(f"    |       (ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, ...)")
    print(f"    |")
    print(f"    +-- SubjectConceptRoot")
    print(f"        |-- AgentRegistry")
    print(f"        |   +-- {stats['agents']} Agents")
    print(f"        |       (SFA_POLITICAL_RR, SFA_MILITARY_RR, SFA_SOCIAL_RR)")
    print(f"        |")
    print(f"        +-- SubjectConceptRegistry")
    print(f"            +-- {stats['subject_concepts']} SubjectConcepts")
    print(f"                (Roman Republic ontology)")
    print()
    
    # Check for forbidden facets
    result = session.run("""
        MATCH (sc:SubjectConcept)
        WHERE sc.primary_facet IN ['TEMPORAL', 'CLASSIFICATION', 'PATRONAGE', 'GENEALOGICAL']
        RETURN sc.subject_id AS id, sc.primary_facet AS forbidden_facet
    """)
    
    forbidden = list(result)
    if forbidden:
        print("WARNING: Forbidden facets found:")
        for record in forbidden:
            print(f"  {record['id']}: {record['forbidden_facet']}")
    else:
        print("VALIDATION: No forbidden facets found (GOOD!)")
    print()
    
    # Sample agent assignments
    result = session.run("""
        MATCH (agent:Agent)
        MATCH (agent)-[:ASSIGNED_TO_FACET]->(facet:Facet)
        MATCH (agent)-[:ASSIGNED_TO_SUBJECT]->(subject:SubjectConcept)
        RETURN 
          agent.id AS agent,
          facet.key AS facet,
          subject.label AS subject
        LIMIT 5
    """)
    
    print("SAMPLE AGENT ASSIGNMENTS:")
    for record in result:
        print(f"  {record['agent']:25} -> {record['facet']:12} -> {record['subject']}")

driver.close()

print()
print("=" * 80)
print("SYSTEM ARCHITECTURE FINALIZED!")
print("=" * 80)
print()
print("Visualize in Neo4j Browser:")
print("  MATCH path = (sys:Chrystallum)-[*..4]->(n)")
print("  RETURN path")

