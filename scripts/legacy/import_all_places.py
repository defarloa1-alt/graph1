#!/usr/bin/env python3
"""Import all Pleiades places with proper qid handling"""
import csv
from pathlib import Path
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
DATABASE = "neo4j"

PROJECT_ROOT = Path(__file__).parent
PLACES_CSV = PROJECT_ROOT / "Geographic" / "pleiades_places.csv"
NAMES_CSV = PROJECT_ROOT / "Geographic" / "pleiades_names.csv"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def import_places_batch(tx, batch):
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
    WITH p, row
    WHERE row.wikidata_qid IS NOT NULL
    SET p.qid = row.wikidata_qid
    """
    tx.run(query, batch=batch)

def import_names_batch(tx, batch):
    query = """
    UNWIND $batch AS row
    MATCH (p:Place {pleiades_id: row.pleiades_id})
    MERGE (n:PlaceName {name_id: row.name_id})
    SET n.name_attested = row.name_attested,
        n.label = row.name_attested,
        n.language = row.language,
        n.name_type = row.name_type,
        n.romanized = row.romanized
    MERGE (p)-[:HAS_NAME]->(n)
    """
    tx.run(query, batch=batch)

print("=== FULL PLEIADES IMPORT ===\n")

# Import places
print("[1/2] Importing all places...")
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
        
        if len(batch) >= batch_size:
            with driver.session(database=DATABASE) as session:
                session.execute_write(import_places_batch, batch)
            print(f"  Imported {count} places...")
            batch = []

# Final batch
if batch:
    with driver.session(database=DATABASE) as session:
        session.execute_write(import_places_batch, batch)

print(f"  Places import complete: {count} total\n")

# Import names
print("[2/2] Importing place names...")
count_names = 0
batch = []

with open(NAMES_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        if not row.get('pleiades_id') or not row.get('name_id'):
            continue
        
        name_data = {
            'pleiades_id': row['pleiades_id'],
            'name_id': row['name_id'],
            'name_attested': row.get('name_attested', ''),
            'language': row.get('language', ''),
            'name_type': row.get('name_type', ''),
            'romanized': row.get('romanized', '')
        }
        
        batch.append(name_data)
        count_names += 1
        
        if len(batch) >= batch_size:
            with driver.session(database=DATABASE) as session:
                session.execute_write(import_names_batch, batch)
            print(f"  Imported {count_names} names...")
            batch = []

# Final batch
if batch:
    with driver.session(database=DATABASE) as session:
        session.execute_write(import_names_batch, batch)

print(f"  Names import complete: {count_names} total\n")

# Final verification
print("=== FINAL VERIFICATION ===")
with driver.session(database=DATABASE) as session:
    result = session.run("MATCH (p:Place) RETURN count(p) AS count")
    place_count = result.single()["count"]
    
    result = session.run("MATCH (n:PlaceName) RETURN count(n) AS count")
    name_count = result.single()["count"]
    
    result = session.run("MATCH ()-[r:HAS_NAME]->() RETURN count(r) AS count")
    name_rels = result.single()["count"]
    
    print(f"  Places: {place_count}")
    print(f"  Place Names: {name_count}")
    print(f"  HAS_NAME relationships: {name_rels}")
    
    if place_count > 0:
        result = session.run("MATCH (p:Place) RETURN p.label AS label LIMIT 5")
        print("\n  Sample places:")
        for record in result:
            print(f"    - {record['label']}")

driver.close()

print("\nGEOGRAPHIC IMPORT COMPLETE!")

