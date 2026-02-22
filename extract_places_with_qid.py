#!/usr/bin/env python3
"""Extract all Place nodes that have Wikidata QID"""
import csv
from pathlib import Path
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

OUTPUT_CSV = Path("CSV/geographic/places_with_wikidata_qid_2026-02-19.csv")
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

print("Extracting places with Wikidata QID...")
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    # Get all places with qid
    result = session.run("""
        MATCH (p:Place)
        WHERE p.qid IS NOT NULL
        RETURN 
            p.place_id AS place_id,
            p.pleiades_id AS pleiades_id,
            p.qid AS wikidata_qid,
            p.label AS label,
            p.place_type AS place_type,
            p.lat AS latitude,
            p.long AS longitude,
            p.bbox AS bbox,
            p.min_date AS min_date,
            p.max_date AS max_date,
            p.description AS description,
            p.uri AS pleiades_uri,
            p.created AS created,
            p.modified AS modified
        ORDER BY p.label
    """)
    
    records = list(result)
    
    print(f"Found {len(records):,} places with Wikidata QID")
    print()
    
    # Write to CSV
    if records:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'place_id', 'pleiades_id', 'wikidata_qid', 'label', 'place_type',
                'latitude', 'longitude', 'bbox', 'min_date', 'max_date',
                'description', 'pleiades_uri', 'created', 'modified'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                writer.writerow(dict(record))
        
        print(f"Written to: {OUTPUT_CSV}")
        print()
    
    # Statistics
    result = session.run("""
        MATCH (p:Place)
        WHERE p.qid IS NOT NULL
        RETURN 
            count(p) AS total_with_qid,
            count(DISTINCT p.place_type) AS distinct_types,
            min(p.min_date) AS earliest_date,
            max(p.max_date) AS latest_date
    """)
    
    stats = result.single()
    
    print("Statistics:")
    print(f"  Total places with QID: {stats['total_with_qid']:,}")
    print(f"  Distinct place types: {stats['distinct_types']}")
    print(f"  Temporal range: {stats['earliest_date']} to {stats['latest_date']}")
    print()
    
    # Type breakdown
    result = session.run("""
        MATCH (p:Place)
        WHERE p.qid IS NOT NULL AND p.place_type IS NOT NULL
        RETURN p.place_type AS type, count(p) AS count
        ORDER BY count DESC
        LIMIT 20
    """)
    
    print("Place types (top 20):")
    for record in result:
        print(f"  {record['type']:30} {record['count']:>6,}")
    print()
    
    # Sample
    print("Sample places (first 10):")
    for i, record in enumerate(records[:10], 1):
        print(f"  {i}. {record['label']:40} QID: {record['wikidata_qid']:12} Type: {record['place_type']}")

driver.close()

print()
print(f"Export complete: {OUTPUT_CSV}")
print()
print("Next steps:")
print("  1. Review CSV for federation quality")
print("  2. Use as baseline for federation scoring")
print("  3. Identify gaps (places without QIDs)")

