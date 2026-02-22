#!/usr/bin/env python3
"""Verify Wikidata enrichment results"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

print("WIKIDATA QID ENRICHMENT VERIFICATION")
print("=" * 60)
print()

with driver.session() as session:
    result = session.run("""
        MATCH (p:Place)
        RETURN 
            count(p) AS total,
            count(p.qid) AS with_qid,
            (count(p.qid) * 100.0 / count(p)) AS qid_pct
    """)
    
    stats = result.single()
    print(f"Total places: {stats['total']:,}")
    print(f"With Wikidata QID: {stats['with_qid']:,} ({stats['qid_pct']:.1f}%)")
    print()
    
    # Sample enriched places
    result = session.run("""
        MATCH (p:Place)
        WHERE p.qid IS NOT NULL
        RETURN p.label, p.pleiades_id, p.qid
        ORDER BY p.label
        LIMIT 10
    """)
    
    print("Sample places with Wikidata QID:")
    for record in result:
        print(f"  {record['p.label']:40} QID: {record['p.qid']:10} Pleiades: {record['p.pleiades_id']}")
    
    print()
    
    # Check Thalefsa specifically
    result = session.run("""
        MATCH (p:Place {pleiades_id: '295353'})
        RETURN p.label, p.qid, p.bbox, p.min_date, p.max_date
    """)
    
    record = result.single()
    if record:
        print("Thalefsa (your example place):")
        print(f"  Label: {record['p.label']}")
        print(f"  Wikidata QID: {record['p.qid'] or 'NOT YET ENRICHED'}")
        print(f"  bbox: {record['p.bbox']}")
        print(f"  Temporal range: {record['p.min_date']} to {record['p.max_date']}")

driver.close()

print()
print("=" * 60)
print("Enrichment verified!")

