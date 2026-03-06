#!/usr/bin/env python3
"""Add bbox property to existing Place nodes"""
import csv
from pathlib import Path
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

PROJECT_ROOT = Path(__file__).parent
PLACES_CSV = PROJECT_ROOT / "Geographic" / "pleiades_places.csv"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def update_batch(tx, batch):
    query = """
    UNWIND $batch AS row
    MATCH (p:Place {pleiades_id: row.pleiades_id})
    SET p.bbox = row.bbox,
        p.min_date = row.min_date,
        p.max_date = row.max_date,
        p.created = row.created,
        p.modified = row.modified
    """
    tx.run(query, batch=batch)

print("Adding bbox and temporal properties to Place nodes...")
print()

count = 0
batch = []
batch_size = 500

with open(PLACES_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if not row.get('pleiades_id'):
            continue
        
        place_data = {
            'pleiades_id': row['pleiades_id'],
            'bbox': row.get('bbox', ''),
            'min_date': int(row['min_date']) if row.get('min_date') else None,
            'max_date': int(row['max_date']) if row.get('max_date') else None,
            'created': row.get('created', ''),
            'modified': row.get('modified', '')
        }
        
        batch.append(place_data)
        count += 1
        
        if len(batch) >= batch_size:
            with driver.session() as session:
                session.execute_write(update_batch, batch)
            print(f"  Updated {count} places...")
            batch = []

# Final batch
if batch:
    with driver.session() as session:
        session.execute_write(update_batch, batch)

print(f"\nUpdate complete: {count} places updated with bbox, min_date, max_date")

# Verify
with driver.session() as session:
    result = session.run("""
        MATCH (p:Place) 
        WHERE p.bbox IS NOT NULL
        RETURN count(p) AS with_bbox
    """)
    bbox_count = result.single()["with_bbox"]
    print(f"Places with bbox: {bbox_count}")
    
    # Check Thalefsa
    result = session.run("""
        MATCH (p:Place {pleiades_id: '295353'})
        RETURN p.bbox AS bbox, p.min_date AS min_date, p.max_date AS max_date
    """)
    record = result.single()
    if record:
        print(f"\nThalefsa updated:")
        print(f"  bbox: {record['bbox']}")
        print(f"  min_date: {record['min_date']}")
        print(f"  max_date: {record['max_date']}")

driver.close()
print("\n[OK] bbox properties added!")

