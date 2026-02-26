#!/usr/bin/env python3
"""
Rebuild System Subgraph - SIMPLE Structure

Federations and Facets are separate - no cross-links at metadata level.
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("REBUILDING SYSTEM SUBGRAPH - SIMPLE CLEAN STRUCTURE")
print("=" * 80)
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    
    # Clear and rebuild
    print("[1/3] Clearing old structure...")
    session.run("""
        MATCH (n)
        WHERE n:Chrystallum OR n:FederationRoot OR n:FacetRoot
           OR n:Federation OR n:Facet
        DETACH DELETE n
    """)
    print("  [OK] Cleared")
    print()
    
    # Create Chrystallum + 2 root children
    print("[2/3] Creating Chrystallum with FederationRoot + FacetRoot...")
    session.run("""
        CREATE (sys:Chrystallum {
          name: 'Chrystallum Knowledge Graph',
          version: '1.0',
          created: datetime()
        })
        
        CREATE (fed_root:FederationRoot {name: 'Federations'})
        CREATE (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        
        CREATE (facet_root:FacetRoot {name: 'Canonical Facets', count: 18})
        CREATE (sys)-[:HAS_FACET_ROOT]->(facet_root)
    """)
    print("  [OK] Created Chrystallum with 2 children")
    print()
    
    # Create 10 Federations under FederationRoot
    print("[3/3] Creating 10 Federations + 18 Facets...")
    
    federations = [
        ('Pleiades', 'local', 'geographic', 'Geographic/pleiades_places.csv'),
        ('PeriodO', 'local', 'temporal', 'Temporal/periodo-dataset.csv'),
        ('Wikidata', 'hub_api', 'universal', 'https://query.wikidata.org/sparql'),
        ('GeoNames', 'hybrid', 'geographic', None),
        ('BabelNet', 'api', 'linguistic', None),
        ('WorldCat', 'api', 'bibliographic', None),
        ('LCSH', 'local', 'conceptual', 'LCSH/skos_subjects/'),
        ('FAST', 'local', 'topical', 'Python/fast/key/FASTTopical_parsed.csv'),
        ('LCC', 'local', 'classification', 'Subjects/lcc_flat.csv'),
        ('MARC', 'local', 'bibliographic', None)
    ]
    
    for name, mode, fed_type, file_path in federations:
        session.run("""
            MATCH (fed_root:FederationRoot)
            CREATE (fed:Federation {
              name: $name,
              mode: $mode,
              type: $type,
              file_path: $file_path
            })
            CREATE (fed_root)-[:HAS_FEDERATION]->(fed)
        """, name=name, mode=mode, type=fed_type, file_path=file_path)
    
    print(f"  [OK] Created {len(federations)} Federation nodes")
    
    # Create 18 Facets under FacetRoot
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
    
    print(f"  [OK] Created {len(facets)} Facet nodes")
    print()
    
    # Verification
    print("=" * 80)
    print("FINAL STRUCTURE")
    print("=" * 80)
    
    result = session.run("""
        MATCH (sys:Chrystallum)
        MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
        MATCH (fed_root)-[:HAS_FEDERATION]->(fed)
        MATCH (facet_root)-[:HAS_FACET]->(facet)
        RETURN 
          count(DISTINCT fed) AS federations,
          count(DISTINCT facet) AS facets,
          collect(DISTINCT fed.name)[0..10] AS federation_list,
          collect(DISTINCT facet.key)[0..10] AS facet_list
    """)
    
    stats = result.single()
    
    print()
    print(f"Chrystallum (center)")
    print(f"  |-- FederationRoot: {stats['federations']} federations")
    for fed in stats['federation_list']:
        print(f"  |   +-- {fed}")
    print(f"  +-- FacetRoot: {stats['facets']} facets")
    for facet in stats['facet_list'][:5]:
        print(f"      +-- {facet}")
    print(f"      ... +{stats['facets'] - 5} more")
    print()
    
    print("NO cross-links between facets and federations at metadata level")
    print("(Cross-links happen at data level: Place uses Pleiades, etc.)")

driver.close()

print()
print("=" * 80)
print("CLEAN SIMPLE STRUCTURE BUILT!")
print("=" * 80)
print()
print("Visualize:")
print("  MATCH path = (sys:Chrystallum)-[*..2]->(n)")
print("  RETURN path")

