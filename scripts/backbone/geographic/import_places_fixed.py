#!/usr/bin/env python3
"""
Fixed Pleiades Import with Explicit Transactions
"""
import csv
from pathlib import Path
from neo4j import GraphDatabase

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
GEOGRAPHIC_DIR = PROJECT_ROOT / "Geographic"
PLACES_CSV = GEOGRAPHIC_DIR / "pleiades_places.csv"
NAMES_CSV = GEOGRAPHIC_DIR / "pleiades_names.csv"

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
DATABASE = "neo4j"

def import_places_batch(tx, batch):
    """Import a batch of places using explicit transaction."""
    query = """
    UNWIND $batch AS row
    MERGE (p:Place {pleiades_id: row.pleiades_id})
    SET p.label = row.label,
        p.description = row.description,
        p.place_type = row.place_type,
        p.lat = row.lat,
        p.long = row.long,
        p.uri = row.uri,
        p.wikidata_qid = row.wikidata_qid,
        p.place_id = row.place_id
    RETURN count(p) AS imported
    """
    result = tx.run(query, batch=batch)
    return result.single()["imported"]

print("=== FIXED PLEIADES IMPORT ===")
print(f"URI: {URI}")
print(f"Database: {DATABASE}")
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Import places
print("[1/2] Importing places...")
count = 0
batch_size = 500
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
            'wikidata_qid': row.get('wikidata_qid') or row.get('qid')
        }
        
        batch.append(place_data)
        count += 1
        
        if len(batch) >= batch_size:
            # Use execute_write for guaranteed commit
            with driver.session(database=DATABASE) as session:
                imported = session.execute_write(import_places_batch, batch)
                print(f"  Imported {count} places (batch committed)")
            batch = []
        
        if count >= 100:  # Test with 100
            break

# Import remaining batch
if batch:
    with driver.session(database=DATABASE) as session:
        imported = session.execute_write(import_places_batch, batch)
        print(f"  Final batch: {count} total places imported")

print(f"\n✓ Import complete: {count} places")

# Verify
print("\n[2/2] Verification...")
with driver.session(database=DATABASE) as session:
    result = session.run("MATCH (p:Place) RETURN count(p) AS count")
    place_count = result.single()["count"]
    print(f"  Places in database: {place_count}")
    
    if place_count > 0:
        result = session.run("MATCH (p:Place) RETURN p.label AS label LIMIT 5")
        print("\n  Sample places:")
        for record in result:
            print(f"    - {record['label']}")

driver.close()

print("\n✓ Done!")

