#!/usr/bin/env python3
"""Check why we need PlaceName and qid status"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    print("=" * 80)
    print("PLACENAME ANALYSIS")
    print("=" * 80)
    print()
    
    # Check PlaceName diversity
    result = session.run("""
        MATCH (p:Place)-[:HAS_NAME]->(n:PlaceName)
        RETURN 
            count(DISTINCT p) AS places_with_names,
            count(n) AS total_names,
            count(DISTINCT n.language) AS languages
    """)
    stats = result.single()
    
    print(f"PlaceName Statistics:")
    print(f"  Places with names: {stats['places_with_names']:,}")
    print(f"  Total PlaceName nodes: {stats['total_names']:,}")
    print(f"  Distinct languages: {stats['languages']}")
    print()
    
    # Check language distribution
    result = session.run("""
        MATCH (n:PlaceName)
        WHERE n.language IS NOT NULL AND n.language <> ''
        RETURN n.language AS lang, count(n) AS count
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("Top languages in PlaceNames:")
    for record in result:
        print(f"  {record['lang']:10} {record['count']:>6,} names")
    print()
    
    # Sample: Place with multiple names
    result = session.run("""
        MATCH (p:Place)-[:HAS_NAME]->(n:PlaceName)
        WITH p, count(n) AS name_count
        WHERE name_count > 1
        MATCH (p)-[:HAS_NAME]->(n)
        RETURN p.label AS place, 
               collect({name: n.name_attested, lang: n.language}) AS names
        LIMIT 3
    """)
    
    print("Sample places with multiple names:")
    for record in result:
        print(f"  {record['place']}:")
        for name in record['names'][:5]:  # Show first 5
            print(f"    - {name['name']} ({name['lang']})")
    print()
    
    print("=" * 80)
    print("QID (WIKIDATA) ANALYSIS")
    print("=" * 80)
    print()
    
    # Check qid property
    result = session.run("""
        MATCH (p:Place)
        RETURN 
            count(p) AS total_places,
            count(p.qid) AS places_with_qid,
            (count(p.qid) * 100.0 / count(p)) AS qid_percentage
    """)
    
    stats = result.single()
    print(f"Wikidata QID Coverage:")
    print(f"  Total places: {stats['total_places']:,}")
    print(f"  Places with qid: {stats['places_with_qid']:,}")
    print(f"  Coverage: {stats['qid_percentage']:.1f}%")
    print()
    
    if stats['places_with_qid'] > 0:
        result = session.run("""
            MATCH (p:Place)
            WHERE p.qid IS NOT NULL
            RETURN p.label, p.qid, p.pleiades_id
            LIMIT 5
        """)
        print("Sample places with Wikidata QID:")
        for record in result:
            print(f"  {record['p.label']} (QID: {record['p.qid']}, Pleiades: {record['p.pleiades_id']})")
    else:
        print("  NO PLACES HAVE WIKIDATA QID YET")
        print("  Need to run Wikidata enrichment to add QIDs")
    print()
    
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print()
    print("PlaceName Nodes:")
    print("  PURPOSE: Store alternate names in different languages")
    print("  VALUE: Enables multi-language search, historical name variants")
    print("  VERDICT: KEEP - valuable for scholarly citations and search")
    print()
    print("Wikidata QID Property:")
    print("  STATUS: 0% coverage (not yet enriched)")
    print("  NEEDED: For federation and cross-referencing with Wikidata")
    print("  ACTION: Run Wikidata enrichment script to add QIDs")
    print()

driver.close()

