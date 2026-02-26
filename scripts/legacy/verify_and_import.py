#!/usr/bin/env python3
"""Verify constraints dropped and import places"""
import csv
from pathlib import Path
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
DATABASE = "neo4j"

PROJECT_ROOT = Path(__file__).parent
PLACES_CSV = PROJECT_ROOT / "Geographic" / "pleiades_places.csv"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Check constraints
print("Checking Place constraints...")
with driver.session() as session:
    result = session.run("SHOW CONSTRAINTS YIELD name, labelsOrTypes, properties")
    all_constraints = list(result)
    
    place_constraints = [c for c in all_constraints if 'Place' in c['labelsOrTypes']]
    print(f"  Place constraints: {len(place_constraints)}")
    for c in place_constraints:
        if 'qid' in str(c['properties']):
            print(f"  WARNING: Still has qid constraint: {c['name']}")

print()

# Import with proper qid handling
print("Importing places (handling missing qid)...")

def import_batch(tx, batch):
    query = """
    UNWIND $batch AS row
    MERGE (p:Place {pleiades_id: row.pleiades_id})
    SET p.label = row.label,
        p.place_id = row.place_id,
        p.description = row.description,
        p.place_type = row.place_type,
        p.lat = row.lat,
        p.long = row.long,
        p.uri = row.uri
    // Only set qid if it exists
    WITH p, row
    WHERE row.wikidata_qid IS NOT NULL
    SET p.qid = row.wikidata_qid
    """
    tx.run(query, batch=batch)

count = 0
batch = []

with open(PLACES_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if not row.get('pleiades_id'):
            continue
        
        place_data = {
            'pleiades_id': row['pleiades_id'],
            'place_id': f"plc_{row['pleiades_id']}",
            'label': row['label'],
            'description': row.get('description', ''),
            'place_type': row.get('place_type', ''),
            'lat': float(row['lat']) if row.get('lat') else None,
            'long': float(row['long']) if row.get('long') else None,
            'uri': row.get('uri', ''),
            'wikidata_qid': row.get('wikidata_qid') or row.get('qid') or None
        }
        
        batch.append(place_data)
        count += 1
        
        if len(batch) >= 100:
            with driver.session(database=DATABASE) as session:
                session.execute_write(import_batch, batch)
            print(f"  Imported {count} places...")
            batch = []
        
        if count >= 100:  # Test limit
            break

# Final batch
if batch:
    with driver.session(database=DATABASE) as session:
        session.execute_write(import_batch, batch)

print(f"Import complete: {count} places processed")

# Verify
print("\nVerifying...")
with driver.session(database=DATABASE) as session:
    result = session.run("MATCH (p:Place) RETURN count(p) AS count")
    place_count = result.single()["count"]
    print(f"  Places in database: {place_count}")

driver.close()

