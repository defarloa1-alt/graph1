#!/usr/bin/env python3
"""
Build Chrystallum System Subgraph - Step by Step

Creates the governance/metadata structure so you can visualize.
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

print("=" * 80)
print("BUILDING CHRYSTALLUM SYSTEM SUBGRAPH - STEP BY STEP")
print("=" * 80)
print()

with driver.session() as session:
    
    # STEP 1: Create Chrystallum root (center)
    print("[STEP 1] Creating Chrystallum system root (center node)...")
    session.run("""
        MERGE (sys:Chrystallum {name: 'Chrystallum Knowledge Graph'})
        SET sys.version = '1.0',
            sys.created = datetime()
    """)
    print("  [OK] Created Chrystallum node (center)")
    print()
    
    # STEP 2: Create two root children (Federation and Facets)
    print("[STEP 2] Creating 2 root children...")
    session.run("""
        MATCH (sys:Chrystallum)
        
        MERGE (fed_root:FederationRoot {name: 'Federation'})
        MERGE (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        
        MERGE (facet_root:FacetRoot {name: 'Canonical Facets', count: 18})
        MERGE (sys)-[:HAS_FACET_ROOT]->(facet_root)
    """)
    print("  [OK] Created FederationRoot")
    print("  [OK] Created FacetRoot")
    print("  [OK] Linked both to Chrystallum")
    print()
    
    # STEP 3: Create Federation children (3 federation types)
    print("[STEP 3] Creating Federation children (3 types)...")
    session.run("""
        MATCH (fed_root:FederationRoot)
        
        MERGE (place_fed:Federation {name: 'Place'})
        SET place_fed.scope = 'geographic',
            place_fed.node_label = 'Place',
            place_fed.count = 41993
        MERGE (fed_root)-[:HAS_FEDERATION]->(place_fed)
        
        MERGE (period_fed:Federation {name: 'Period'})
        SET period_fed.scope = 'temporal',
            period_fed.node_label = 'Period',
            period_fed.count = 1077
        MERGE (fed_root)-[:HAS_FEDERATION]->(period_fed)
        
        MERGE (subject_fed:Federation {name: 'SubjectConcept'})
        SET subject_fed.scope = 'semantic',
            subject_fed.node_label = 'SubjectConcept',
            subject_fed.count = 87
        MERGE (fed_root)-[:HAS_FEDERATION]->(subject_fed)
    """)
    print("  [OK] Created Federation: Place")
    print("  [OK] Created Federation: Period")
    print("  [OK] Created Federation: SubjectConcept")
    print()
    
    # STEP 4: Create Facet children (18 facets)
    print("[STEP 4] Creating Facet children (18 facets)...")
    
    facets = [
        'ARCHAEOLOGICAL', 'ARTISTIC', 'BIOGRAPHIC', 'COMMUNICATION',
        'CULTURAL', 'DEMOGRAPHIC', 'DIPLOMATIC', 'ECONOMIC',
        'ENVIRONMENTAL', 'GEOGRAPHIC', 'INTELLECTUAL', 'LINGUISTIC',
        'MILITARY', 'POLITICAL', 'RELIGIOUS', 'SCIENTIFIC',
        'SOCIAL', 'TECHNOLOGICAL'
    ]
    
    for facet_key in facets:
        session.run("""
            MATCH (facet_root:FacetRoot)
            MERGE (f:Facet {key: $key})
            SET f.label = $label
            MERGE (facet_root)-[:HAS_FACET]->(f)
        """, key=facet_key, label=facet_key.title())
    
    print(f"  [OK] Created {len(facets)} Facet nodes")
    print()
    
    # STEP 5: Create Authority Sources
    print("[STEP 5] Creating Authority Sources...")
    session.run("""
        MERGE (pleiades:AuthoritySource {name: 'Pleiades'})
        SET pleiades.mode = 'local',
            pleiades.file_path = 'Geographic/pleiades_places.csv'
        
        MERGE (periodo:AuthoritySource {name: 'PeriodO'})
        SET periodo.mode = 'local',
            periodo.file_path = 'Temporal/periodo-dataset.csv'
        
        MERGE (lcsh:AuthoritySource {name: 'LCSH'})
        SET lcsh.mode = 'local'
        
        MERGE (fast:AuthoritySource {name: 'FAST'})
        SET fast.mode = 'local'
        
        MERGE (lcc:AuthoritySource {name: 'LCC'})
        SET lcc.mode = 'local'
        
        MERGE (wikidata:AuthoritySource {name: 'Wikidata'})
        SET wikidata.mode = 'hub_api',
            wikidata.role = 'enrichment_hub'
    """)
    print("  [OK] Created 6 AuthoritySource nodes")
    print()
    
    # STEP 6: Link Federations to Authority Sources
    print("[STEP 6] Linking Federations to Authority Sources...")
    session.run("""
        MATCH (place:Federation {name: 'Place'})
        MATCH (period:Federation {name: 'Period'})
        MATCH (subject:Federation {name: 'SubjectConcept'})
        
        MATCH (pleiades:AuthoritySource {name: 'Pleiades'})
        MATCH (periodo:AuthoritySource {name: 'PeriodO'})
        MATCH (lcsh:AuthoritySource {name: 'LCSH'})
        MATCH (fast:AuthoritySource {name: 'FAST'})
        MATCH (lcc:AuthoritySource {name: 'LCC'})
        MATCH (wikidata:AuthoritySource {name: 'Wikidata'})
        
        // Place uses Pleiades + Wikidata
        MERGE (place)-[:MAPS_TO {weight: 20}]->(pleiades)
        MERGE (place)-[:MAPS_TO {weight: 50}]->(wikidata)
        
        // Period uses PeriodO + Wikidata
        MERGE (period)-[:MAPS_TO {weight: 30}]->(periodo)
        MERGE (period)-[:MAPS_TO {weight: 50}]->(wikidata)
        
        // SubjectConcept uses LCSH + FAST + LCC + Wikidata
        MERGE (subject)-[:MAPS_TO {weight: 30}]->(lcsh)
        MERGE (subject)-[:MAPS_TO {weight: 30}]->(fast)
        MERGE (subject)-[:MAPS_TO {weight: 20}]->(lcc)
        MERGE (subject)-[:MAPS_TO {weight: 20}]->(wikidata)
    """)
    print("  [OK] Linked Place to Pleiades, Wikidata")
    print("  [OK] Linked Period to PeriodO, Wikidata")
    print("  [OK] Linked SubjectConcept to LCSH, FAST, LCC, Wikidata")
    print()
    
    # STEP 7: Link Facets to Federations (which federations use which facets)
    print("[STEP 7] Linking Facets to Federations...")
    
    # Link GEOGRAPHIC facet to Place
    session.run("""
        MATCH (place:Federation {name: 'Place'})
        MATCH (geo:Facet {key: 'GEOGRAPHIC'})
        MERGE (geo)-[:APPLIES_TO]->(place)
    """)
    
    # Link all 18 facets to SubjectConcept
    session.run("""
        MATCH (subject:Federation {name: 'SubjectConcept'})
        MATCH (facet:Facet)
        MERGE (facet)-[:APPLIES_TO]->(subject)
    """)
    print("  [OK] Linked GEOGRAPHIC facet to Place federation")
    print("  [OK] Linked all 18 facets to SubjectConcept federation")
    print()
    
    # STEP 8: Visualize structure
    print("[STEP 8] Visualizing structure...")
    print()
    
    result = session.run("""
        MATCH (sys:Chrystallum)
        OPTIONAL MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        OPTIONAL MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
        OPTIONAL MATCH (fed_root)-[:HAS_FEDERATION]->(fed)
        OPTIONAL MATCH (facet_root)-[:HAS_FACET]->(facet)
        RETURN 
            sys.name AS system,
            fed_root.name AS federation_root,
            facet_root.name AS facet_root,
            count(DISTINCT fed) AS federation_count,
            count(DISTINCT facet) AS facet_count
    """)
    
    stats = result.single()
    print("STRUCTURE:")
    print(f"  Chrystallum: {stats['system']}")
    print(f"    |-- FederationRoot: {stats['federation_root']}")
    print(f"    |   +-- Federations: {stats['federation_count']}")
    print(f"    +-- FacetRoot: {stats['facet_root']}")
    print(f"        +-- Facets: {stats['facet_count']}")
    print()
    
    # Show authority mappings
    result = session.run("""
        MATCH (fed:Federation)-[:MAPS_TO]->(auth:AuthoritySource)
        RETURN fed.name AS federation, collect(auth.name) AS authorities
        ORDER BY federation
    """)
    
    print("AUTHORITY MAPPINGS:")
    for record in result:
        print(f"  {record['federation']:20} --> {', '.join(record['authorities'])}")
    print()
    
    # Show facet usage
    result = session.run("""
        MATCH (facet:Facet)-[:APPLIES_TO]->(fed:Federation)
        WITH fed, count(facet) AS facet_count
        RETURN fed.name AS federation, facet_count
        ORDER BY facet_count DESC
    """)
    
    print("FACET USAGE:")
    for record in result:
        print(f"  {record['federation']:20} uses {record['facet_count']} facets")

driver.close()

print()
print("=" * 80)
print("SYSTEM SUBGRAPH BUILT!")
print("=" * 80)
print()
print("Visualize in Neo4j Browser:")
print("  MATCH path = (sys:Chrystallum)-[*..3]->(n)")
print("  RETURN path")

