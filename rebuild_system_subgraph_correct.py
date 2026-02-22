#!/usr/bin/env python3
"""
Rebuild Chrystallum System Subgraph - CORRECT Structure

Federation = Authority Source (same thing!)
Facets use one-to-many Federations
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("REBUILDING SYSTEM SUBGRAPH - CORRECT STRUCTURE")
print("=" * 80)
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    
    # STEP 1: Clear old structure
    print("[STEP 1] Clearing old system subgraph...")
    session.run("""
        MATCH (n)
        WHERE n:Chrystallum OR n:FederationRoot OR n:FacetRoot
           OR n:Federation OR n:FederationType OR n:AuthoritySource
        DETACH DELETE n
    """)
    print("  [OK] Cleared old structure")
    print()
    
    # STEP 2: Create Chrystallum root
    print("[STEP 2] Creating Chrystallum (center node)...")
    session.run("""
        CREATE (sys:Chrystallum {
          name: 'Chrystallum Knowledge Graph',
          version: '1.0',
          created: datetime()
        })
    """)
    print("  [OK] Created Chrystallum")
    print()
    
    # STEP 3: Create FederationRoot + 10 federation nodes
    print("[STEP 3] Creating FederationRoot + 10 federations...")
    session.run("""
        MATCH (sys:Chrystallum)
        
        CREATE (fed_root:FederationRoot {name: 'Federations'})
        CREATE (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        
        // 10 Federations (which are the authorities)
        CREATE (pleiades:Federation {
          name: 'Pleiades',
          mode: 'local',
          file_path: 'Geographic/pleiades_places.csv',
          type: 'geographic'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(pleiades)
        
        CREATE (periodo:Federation {
          name: 'PeriodO',
          mode: 'local',
          file_path: 'Temporal/periodo-dataset.csv',
          type: 'temporal'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(periodo)
        
        CREATE (wikidata:Federation {
          name: 'Wikidata',
          mode: 'hub_api',
          api_endpoint: 'https://query.wikidata.org/sparql',
          type: 'universal'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(wikidata)
        
        CREATE (geonames:Federation {
          name: 'GeoNames',
          mode: 'hybrid',
          type: 'geographic'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(geonames)
        
        CREATE (babelnet:Federation {
          name: 'BabelNet',
          mode: 'api',
          type: 'linguistic'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(babelnet)
        
        CREATE (worldcat:Federation {
          name: 'WorldCat',
          mode: 'api',
          type: 'bibliographic'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(worldcat)
        
        CREATE (lcsh:Federation {
          name: 'LCSH',
          mode: 'local',
          file_path: 'LCSH/skos_subjects/',
          type: 'conceptual'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(lcsh)
        
        CREATE (fast:Federation {
          name: 'FAST',
          mode: 'local',
          file_path: 'Python/fast/key/FASTTopical_parsed.csv',
          type: 'topical'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(fast)
        
        CREATE (lcc:Federation {
          name: 'LCC',
          mode: 'local',
          file_path: 'Subjects/lcc_flat.csv',
          type: 'classification'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(lcc)
        
        CREATE (marc:Federation {
          name: 'MARC',
          mode: 'local',
          type: 'bibliographic'
        })
        CREATE (fed_root)-[:HAS_FEDERATION]->(marc)
    """)
    print("  [OK] Created 10 Federation nodes under FederationRoot")
    print()
    
    # STEP 4: Create FacetRoot + 18 facets
    print("[STEP 4] Creating FacetRoot + 18 facets...")
    
    facets = [
        'ARCHAEOLOGICAL', 'ARTISTIC', 'BIOGRAPHIC', 'COMMUNICATION',
        'CULTURAL', 'DEMOGRAPHIC', 'DIPLOMATIC', 'ECONOMIC',
        'ENVIRONMENTAL', 'GEOGRAPHIC', 'INTELLECTUAL', 'LINGUISTIC',
        'MILITARY', 'POLITICAL', 'RELIGIOUS', 'SCIENTIFIC',
        'SOCIAL', 'TECHNOLOGICAL'
    ]
    
    session.run("""
        MATCH (sys:Chrystallum)
        CREATE (facet_root:FacetRoot {name: 'Canonical Facets', count: 18})
        CREATE (sys)-[:HAS_FACET_ROOT]->(facet_root)
    """)
    
    for facet_key in facets:
        session.run("""
            MATCH (facet_root:FacetRoot)
            CREATE (f:Facet {key: $key, label: $label})
            CREATE (facet_root)-[:HAS_FACET]->(f)
        """, key=facet_key, label=facet_key.title())
    
    print(f"  [OK] Created 18 Facet nodes under FacetRoot")
    print()
    
    # STEP 5: Link Facets to Federations (facets use federations)
    print("[STEP 5] Linking Facets to Federations (which federations each facet uses)...")
    
    # GEOGRAPHIC facet uses Pleiades, Wikidata, GeoNames
    session.run("""
        MATCH (geo:Facet {key: 'GEOGRAPHIC'})
        MATCH (pleiades:Federation {name: 'Pleiades'})
        MATCH (wikidata:Federation {name: 'Wikidata'})
        MATCH (geonames:Federation {name: 'GeoNames'})
        CREATE (geo)-[:USES_FEDERATION]->(pleiades)
        CREATE (geo)-[:USES_FEDERATION]->(wikidata)
        CREATE (geo)-[:USES_FEDERATION]->(geonames)
    """)
    print("  [OK] GEOGRAPHIC uses: Pleiades, Wikidata, GeoNames")
    
    # POLITICAL facet uses LCSH, FAST, LCC, WorldCat, Wikidata
    session.run("""
        MATCH (pol:Facet {key: 'POLITICAL'})
        MATCH (lcsh:Federation {name: 'LCSH'})
        MATCH (fast:Federation {name: 'FAST'})
        MATCH (lcc:Federation {name: 'LCC'})
        MATCH (worldcat:Federation {name: 'WorldCat'})
        MATCH (wikidata:Federation {name: 'Wikidata'})
        CREATE (pol)-[:USES_FEDERATION]->(lcsh)
        CREATE (pol)-[:USES_FEDERATION]->(fast)
        CREATE (pol)-[:USES_FEDERATION]->(lcc)
        CREATE (pol)-[:USES_FEDERATION]->(worldcat)
        CREATE (pol)-[:USES_FEDERATION]->(wikidata)
    """)
    print("  [OK] POLITICAL uses: LCSH, FAST, LCC, WorldCat, Wikidata")
    
    # Link all other facets to Wikidata (universal) + LCSH/FAST
    session.run("""
        MATCH (facet:Facet)
        WHERE NOT facet.key IN ['GEOGRAPHIC', 'POLITICAL']
        MATCH (lcsh:Federation {name: 'LCSH'})
        MATCH (fast:Federation {name: 'FAST'})
        MATCH (wikidata:Federation {name: 'Wikidata'})
        CREATE (facet)-[:USES_FEDERATION]->(lcsh)
        CREATE (facet)-[:USES_FEDERATION]->(fast)
        CREATE (facet)-[:USES_FEDERATION]->(wikidata)
    """)
    print("  [OK] All other facets use: LCSH, FAST, Wikidata (baseline)")
    print()
    
    # STEP 6: Visualize
    print("[STEP 6] Visualizing final structure...")
    print()
    
    result = session.run("""
        MATCH (sys:Chrystallum)
        MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)
        MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
        MATCH (fed_root)-[:HAS_FEDERATION]->(fed)
        MATCH (facet_root)-[:HAS_FACET]->(facet)
        RETURN 
          count(DISTINCT fed) AS federation_count,
          count(DISTINCT facet) AS facet_count
    """)
    
    stats = result.single()
    
    print("STRUCTURE:")
    print(f"  Chrystallum (center)")
    print(f"    |-- FederationRoot")
    print(f"    |   +-- {stats['federation_count']} Federations (Pleiades, PeriodO, Wikidata, etc.)")
    print(f"    +-- FacetRoot")
    print(f"        +-- {stats['facet_count']} Facets")
    print()
    
    # Show which federations each facet uses
    result = session.run("""
        MATCH (facet:Facet)-[:USES_FEDERATION]->(fed:Federation)
        WITH facet, collect(fed.name) AS federations
        RETURN facet.key AS facet, federations
        ORDER BY facet
        LIMIT 5
    """)
    
    print("FACET -> FEDERATION USAGE (sample):")
    for record in result:
        print(f"  {record['facet']:20} uses: {', '.join(record['federations'])}")

driver.close()

print()
print("=" * 80)
print("CORRECT STRUCTURE BUILT!")
print("=" * 80)
print()
print("Key insight: Federation = Authority Source (same thing!)")
print("Facets use one-to-many federations")
print()
print("Visualize:")
print("  MATCH path = (sys:Chrystallum)-[*..3]->(n) RETURN path")

