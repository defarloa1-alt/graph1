#!/usr/bin/env python3
"""
Build Complete Chrystallum Architecture

Creates the full self-describing system subgraph with:
- 4 main branches
- Federations, Entity types, Facets, Agents
- All relationships and hierarchies
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("BUILDING COMPLETE CHRYSTALLUM ARCHITECTURE")
print("=" * 80)
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    
    # STEP 0: Clear everything
    print("[STEP 0] Clearing old system subgraph...")
    session.run("""
        MATCH (n)
        WHERE n:Chrystallum OR n:FederationRoot OR n:EntityRoot 
           OR n:FacetRoot OR n:SubjectConceptRoot
           OR n:Federation OR n:EntityType OR n:Facet 
           OR n:AgentRegistry OR n:Agent OR n:Schema
        DETACH DELETE n
    """)
    print("  [OK] Cleared old structure")
    print()
    
    # STEP 1: Create Chrystallum root
    print("[STEP 1] Creating Chrystallum system root...")
    session.run("""
        CREATE (:Chrystallum {
          name: 'Chrystallum Knowledge Graph',
          version: '1.0',
          created: datetime()
        })
    """)
    print("  [OK] Created Chrystallum")
    print()
    
    # STEP 2: Create 4 main branches
    print("[STEP 2] Creating 4 main branches...")
    session.run("""
        MATCH (sys:Chrystallum)
        
        CREATE (fed_root:FederationRoot {name: 'Federations', count: 10})
        CREATE (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        
        CREATE (entity_root:EntityRoot {name: 'Entity Types'})
        CREATE (sys)-[:HAS_ENTITY_ROOT]->(entity_root)
        
        CREATE (facet_root:FacetRoot {name: 'Canonical Facets', count: 18})
        CREATE (sys)-[:HAS_FACET_ROOT]->(facet_root)
        
        CREATE (subject_root:SubjectConceptRoot {name: 'Subject Concepts & Agents'})
        CREATE (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(subject_root)
    """)
    print("  [OK] Created 4 main branches")
    print()
    
    # STEP 3: Create 10 Federations
    print("[STEP 3] Creating 10 Federations...")
    
    federations = [
        ('Pleiades', 'local', 'geographic', 'Geographic/pleiades_places.csv', 41993),
        ('PeriodO', 'local', 'temporal', 'Temporal/periodo-dataset.csv', 8959),
        ('Wikidata', 'hub_api', 'universal', 'https://query.wikidata.org/sparql', None),
        ('GeoNames', 'hybrid', 'geographic', 'Via crosswalk + API', None),
        ('BabelNet', 'api', 'linguistic', 'External API', None),
        ('WorldCat', 'api', 'bibliographic', 'External API', None),
        ('LCSH', 'local', 'conceptual', 'LCSH/skos_subjects/', None),
        ('FAST', 'local', 'topical', 'Python/fast/key/FASTTopical_parsed.csv', None),
        ('LCC', 'local', 'classification', 'Subjects/lcc_flat.csv', None),
        ('MARC', 'local', 'bibliographic', 'MARC records', None)
    ]
    
    for name, mode, fed_type, source, coverage in federations:
        session.run("""
            MATCH (fed_root:FederationRoot)
            CREATE (fed:Federation {
              name: $name,
              mode: $mode,
              type: $type,
              source: $source,
              coverage: $coverage
            })
            CREATE (fed_root)-[:HAS_FEDERATION]->(fed)
        """, name=name, mode=mode, type=fed_type, source=source, coverage=coverage)
    
    print(f"  [OK] Created {len(federations)} Federations")
    print()
    
    # STEP 4: Create Entity Types with child hierarchies
    print("[STEP 4] Creating Entity Types with schemas and hierarchies...")
    
    # Year backbone
    session.run("""
        MATCH (entity_root:EntityRoot)
        
        CREATE (year:EntityType {name: 'Year', description: 'Atomic temporal nodes'})
        CREATE (entity_root)-[:HAS_ENTITY_TYPE]->(year)
        CREATE (year_schema:Schema {
          required_props: ['year', 'label', 'entity_id'],
          uses_federations: []
        })
        CREATE (year)-[:HAS_SCHEMA]->(year_schema)
        
        CREATE (decade:EntityType {name: 'Decade', description: 'Decade rollup'})
        CREATE (year)-[:HAS_CHILD_TYPE]->(decade)
        
        CREATE (century:EntityType {name: 'Century', description: 'Century rollup'})
        CREATE (decade)-[:HAS_CHILD_TYPE]->(century)
        
        CREATE (millennium:EntityType {name: 'Millennium', description: 'Millennium rollup'})
        CREATE (century)-[:HAS_CHILD_TYPE]->(millennium)
    """)
    print("  [OK] Year backbone: Year -> Decade -> Century -> Millennium")
    
    # Place hierarchy
    session.run("""
        MATCH (entity_root:EntityRoot)
        
        CREATE (place:EntityType {name: 'Place', description: 'Geographic locations'})
        CREATE (entity_root)-[:HAS_ENTITY_TYPE]->(place)
        CREATE (place_schema:Schema {
          required_props: ['place_id', 'pleiades_id'],
          optional_props: ['qid', 'lat', 'long', 'bbox'],
          uses_federations: ['Pleiades', 'Wikidata', 'GeoNames']
        })
        CREATE (place)-[:HAS_SCHEMA]->(place_schema)
        
        CREATE (place_type:EntityType {name: 'PlaceType', description: 'Place type taxonomy'})
        CREATE (place)-[:HAS_CHILD_TYPE]->(place_type)
    """)
    print("  [OK] Place hierarchy: Place -> PlaceType")
    
    # Period hierarchy
    session.run("""
        MATCH (entity_root:EntityRoot)
        
        CREATE (period:EntityType {name: 'Period', description: 'Historical periods'})
        CREATE (entity_root)-[:HAS_ENTITY_TYPE]->(period)
        CREATE (period_schema:Schema {
          required_props: ['period_id', 'start_year', 'end_year'],
          optional_props: ['qid', 'periodo_id'],
          uses_federations: ['PeriodO', 'Wikidata']
        })
        CREATE (period)-[:HAS_SCHEMA]->(period_schema)
        
        CREATE (period_candidate:EntityType {name: 'PeriodCandidate', description: 'Period validation candidates'})
        CREATE (period)-[:HAS_CHILD_TYPE]->(period_candidate)
    """)
    print("  [OK] Period hierarchy: Period -> PeriodCandidate")
    
    # Other entity types (no children yet)
    entity_types = [
        ('Human', 'People, historical figures', ['Wikidata', 'VIAF']),
        ('Event', 'Historical events, occurrences', ['Wikidata']),
        ('Organization', 'Political bodies, groups', ['Wikidata']),
        ('SubjectConcept', 'Thematic concepts, topics', ['LCSH', 'FAST', 'LCC', 'Wikidata']),
        ('Work', 'Texts, inscriptions, scholarship', ['WorldCat', 'Wikidata']),
        ('Claim', 'Evidence-based assertions', [])
    ]
    
    for name, desc, feds in entity_types:
        session.run("""
            MATCH (entity_root:EntityRoot)
            CREATE (et:EntityType {name: $name, description: $desc})
            CREATE (entity_root)-[:HAS_ENTITY_TYPE]->(et)
            CREATE (schema:Schema {uses_federations: $feds})
            CREATE (et)-[:HAS_SCHEMA]->(schema)
        """, name=name, desc=desc, feds=feds)
    
    print(f"  [OK] Created {len(entity_types)} additional entity types")
    print()
    
    # STEP 5: Create 18 Facets
    print("[STEP 5] Creating 18 Facets...")
    
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
            CREATE (f:Facet {key: $key, label: $label})
            CREATE (facet_root)-[:HAS_FACET]->(f)
        """, key=facet_key, label=facet_key.title())
    
    print(f"  [OK] Created {len(facets)} Facets")
    print()
    
    # STEP 6: Create AgentRegistry and sample agents
    print("[STEP 6] Creating AgentRegistry and agents...")
    
    session.run("""
        MATCH (subject_root:SubjectConceptRoot)
        
        CREATE (agent_reg:AgentRegistry {name: 'Agent Registry', count: 0})
        CREATE (subject_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)
    """)
    print("  [OK] Created AgentRegistry")
    
    # Create sample agents
    agents = [
        ('SFA_POLITICAL_RR', 'POLITICAL', 'subj_rr_governance'),
        ('SFA_MILITARY_RR', 'MILITARY', 'subj_rr_military'),
        ('SFA_SOCIAL_RR', 'SOCIAL', 'subj_rr_society')
    ]
    
    for agent_id, facet_key, subject_id in agents:
        session.run("""
            MATCH (agent_reg:AgentRegistry)
            MATCH (facet:Facet {key: $facet_key})
            MATCH (subject:SubjectConcept {subject_id: $subject_id})
            MATCH (fed_root:FederationRoot)
            
            CREATE (agent:Agent {
              id: $agent_id,
              name: $agent_id,
              status: 'active',
              created: datetime()
            })
            CREATE (agent_reg)-[:HAS_AGENT]->(agent)
            CREATE (agent)-[:ASSIGNED_TO_FACET]->(facet)
            CREATE (agent)-[:ASSIGNED_TO_SUBJECT]->(subject)
            CREATE (agent)-[:USES]->(fed_root)
        """, agent_id=agent_id, facet_key=facet_key, subject_id=subject_id)
    
    print(f"  [OK] Created {len(agents)} sample agents")
    print()
    
    # STEP 7: Verification and visualization
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print()
    
    result = session.run("""
        MATCH (sys:Chrystallum)
        OPTIONAL MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        OPTIONAL MATCH (sys)-[:HAS_ENTITY_ROOT]->(entity_root)
        OPTIONAL MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
        OPTIONAL MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(subject_root)
        
        OPTIONAL MATCH (fed_root)-[:HAS_FEDERATION]->(fed)
        OPTIONAL MATCH (entity_root)-[:HAS_ENTITY_TYPE]->(et)
        OPTIONAL MATCH (facet_root)-[:HAS_FACET]->(facet)
        OPTIONAL MATCH (subject_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)
        OPTIONAL MATCH (agent_reg)-[:HAS_AGENT]->(agent)
        
        RETURN 
          count(DISTINCT fed) AS federations,
          count(DISTINCT et) AS entity_types,
          count(DISTINCT facet) AS facets,
          count(DISTINCT agent) AS agents
    """)
    
    stats = result.single()
    
    print("STRUCTURE CREATED:")
    print(f"  Chrystallum (root)")
    print(f"    |-- FederationRoot: {stats['federations']} federations")
    print(f"    |-- EntityRoot: {stats['entity_types']} entity types")
    print(f"    |-- FacetRoot: {stats['facets']} facets")
    print(f"    +-- SubjectConceptRoot: {stats['agents']} agents")
    print()
    
    # Show entity type hierarchies
    result = session.run("""
        MATCH (parent:EntityType)-[:HAS_CHILD_TYPE]->(child:EntityType)
        RETURN parent.name AS parent, child.name AS child
        ORDER BY parent
    """)
    
    print("ENTITY TYPE HIERARCHIES (Backbones):")
    for record in result:
        print(f"  {record['parent']} -> {record['child']}")
    print()
    
    # Show agent assignments
    result = session.run("""
        MATCH (agent:Agent)
        OPTIONAL MATCH (agent)-[:ASSIGNED_TO_FACET]->(facet:Facet)
        OPTIONAL MATCH (agent)-[:ASSIGNED_TO_SUBJECT]->(subject:SubjectConcept)
        OPTIONAL MATCH (agent)-[:USES]->(fed_root:FederationRoot)
        RETURN 
          agent.id AS agent_id,
          facet.key AS facet,
          subject.subject_id AS subject,
          fed_root.name AS uses
    """)
    
    print("AGENT ASSIGNMENTS:")
    for record in result:
        print(f"  {record['agent_id']:25} Facet: {record['facet']:12} Subject: {record['subject']}")
        print(f"                              Uses: {record['uses']}")
    print()
    
    # Federation list
    result = session.run("""
        MATCH (:FederationRoot)-[:HAS_FEDERATION]->(fed:Federation)
        RETURN fed.name AS name, fed.mode AS mode, fed.type AS type
        ORDER BY name
    """)
    
    print("FEDERATIONS:")
    for record in result:
        print(f"  {record['name']:15} ({record['mode']:10}) - {record['type']}")

driver.close()

print()
print("=" * 80)
print("COMPLETE ARCHITECTURE BUILT!")
print("=" * 80)
print()
print("Visualize in Neo4j Browser:")
print("  MATCH path = (sys:Chrystallum)-[*..3]->(n)")
print("  RETURN path")
print()
print("Or focused views:")
print("  // Federation branch")
print("  MATCH path = (sys:Chrystallum)-[:HAS_FEDERATION_ROOT]->(fed_root)-[:HAS_FEDERATION]->(fed)")
print("  RETURN path")
print()
print("  // Entity branch")
print("  MATCH path = (sys:Chrystallum)-[:HAS_ENTITY_ROOT]->(entity_root)-[:HAS_ENTITY_TYPE]->(et)")
print("  OPTIONAL MATCH (et)-[:HAS_CHILD_TYPE*]->(child)")
print("  RETURN path")
print()
print("  // Agent branch")
print("  MATCH path = (sys:Chrystallum)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)")
print("  MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(reg)-[:HAS_AGENT]->(agent)")
print("  OPTIONAL MATCH (agent)-[r]->(target)")
print("  RETURN path, agent, r, target")

