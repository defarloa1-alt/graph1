#!/usr/bin/env python3
"""
Enrich Place nodes with Wikidata QIDs from Pleiades-GeoNames-Wikidata crosswalk

DEPRECATED: Use scripts/backbone/geographic/enrich_places_from_crosswalk.py instead.
That script uses config_loader, adds geonames_id/tgn_id, and normalizes pleiades_id matching.
"""
import csv
import os
from pathlib import Path
from neo4j import GraphDatabase

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_PROJECT_ROOT))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

URI = NEO4J_URI
USERNAME = NEO4J_USERNAME
PASSWORD = NEO4J_PASSWORD
DATABASE = "neo4j"

CROSSWALK_CSV = _PROJECT_ROOT / "CSV" / "geographic" / "pleiades_geonames_wikidata_tgn_crosswalk_v1.csv"

print("=" * 80)
print("WIKIDATA QID ENRICHMENT FOR PLACES")
print("=" * 80)
print(f"\nSource: {CROSSWALK_CSV.name}")
print()

# Load crosswalk mappings
pleiades_to_qid = {}
pleiades_to_tgn = {}

with open(CROSSWALK_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pleiades_id = row.get('pleiades_id')
        wikidata_qid = row.get('wikidata_qid')
        tgn_id = row.get('tgn_id')
        
        if pleiades_id and wikidata_qid and wikidata_qid.strip():
            # Keep first QID for each pleiades_id (could be multiple rows)
            if pleiades_id not in pleiades_to_qid:
                pleiades_to_qid[pleiades_id] = wikidata_qid
        
        if pleiades_id and tgn_id and tgn_id.strip():
            if pleiades_id not in pleiades_to_tgn:
                pleiades_to_tgn[pleiades_id] = tgn_id

print(f"Loaded mappings:")
print(f"  Pleiades to Wikidata: {len(pleiades_to_qid):,} mappings")
print(f"  Pleiades to TGN: {len(pleiades_to_tgn):,} mappings")
print()

# Connect to Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def enrich_batch(tx, batch):
    """Enrich places with QID (skip TGN due to uniqueness conflicts)"""
    query = """
    UNWIND $batch AS row
    MATCH (p:Place {pleiades_id: row.pleiades_id})
    SET p.qid = row.qid
    """
    tx.run(query, batch=batch)

# Build enrichment batches
print("Enriching Place nodes with Wikidata QIDs and TGN IDs...")
batch = []
batch_size = 500
count_qid = 0
count_tgn = 0

for pleiades_id in pleiades_to_qid.keys():
    enrichment = {
        'pleiades_id': pleiades_id,
        'qid': pleiades_to_qid.get(pleiades_id)
    }
    
    batch.append(enrichment)
    
    if enrichment['qid']:
        count_qid += 1
    
    if len(batch) >= batch_size:
        with driver.session(database=DATABASE) as session:
            session.execute_write(enrich_batch, batch)
        print(f"  Enriched {len(batch)} places (total QIDs added: {count_qid})")
        batch = []

# Final batch
if batch:
    with driver.session(database=DATABASE) as session:
        session.execute_write(enrich_batch, batch)

print(f"\nEnrichment complete:")
print(f"  Places with QID added: {count_qid:,}")
print(f"  (TGN skipped due to uniqueness constraints - multiple Pleiades to same TGN)")
print()

# Verify
print("Verification:")
with driver.session(database=DATABASE) as session:
    result = session.run("""
        MATCH (p:Place)
        RETURN 
            count(p) AS total,
            count(p.qid) AS with_qid,
            count(p.tgn_id) AS with_tgn,
            (count(p.qid) * 100.0 / count(p)) AS qid_pct,
            (count(p.tgn_id) * 100.0 / count(p)) AS tgn_pct
    """)
    
    stats = result.single()
    print(f"  Total places: {stats['total']:,}")
    print(f"  With Wikidata QID: {stats['with_qid']:,} ({stats['qid_pct']:.1f}%)")
    print(f"  With TGN ID: {stats['with_tgn']:,} ({stats['tgn_pct']:.1f}%)")
    print()
    
    # Sample enriched places
    result = session.run("""
        MATCH (p:Place)
        WHERE p.qid IS NOT NULL
        RETURN p.label, p.pleiades_id, p.qid, p.tgn_id
        LIMIT 5
    """)
    
    print("Sample enriched places:")
    for record in result:
        tgn_info = f", TGN: {record['p.tgn_id']}" if record['p.tgn_id'] else ""
        print(f"  {record['p.label']} (Pleiades: {record['p.pleiades_id']}, QID: {record['p.qid']}{tgn_info})")

driver.close()

print()
print("=" * 80)
print("WIKIDATA ENRICHMENT COMPLETE!")
print("=" * 80)

