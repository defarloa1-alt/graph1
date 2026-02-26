#!/usr/bin/env python3
"""
Extract Wikidata Backlinks (Topology Only)

For each entity in our graph:
1. Query Wikidata: "What items point to this QID?"
2. Get: Source QID + Source entity type (from P31)
3. Store: Backlink topology (QID + Type pairs)

Focus: WHAT connects (topology), not HOW (semantics)
"""

import requests
import json
import time
from datetime import datetime

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def get_backlinks_for_qid(qid: str, limit: int = 1000) -> list:
    """
    Query Wikidata for backlinks to a QID.
    
    Returns list of (source_qid, source_type) tuples
    """
    
    query = f"""
    SELECT ?item ?itemLabel ?instanceOf ?instanceOfLabel WHERE {{
      ?item ?prop wd:{qid} .
      OPTIONAL {{ ?item wdt:P31 ?instanceOf }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }}
    LIMIT {limit}
    """
    
    response = requests.get(
        SPARQL_ENDPOINT,
        params={'query': query, 'format': 'json'},
        headers={'User-Agent': 'Chrystallum/1.0'}
    )
    
    if response.status_code != 200:
        print(f"  Error querying {qid}: {response.status_code}")
        return []
    
    results = response.json().get('results', {}).get('bindings', [])
    
    backlinks = []
    for result in results:
        source_qid = result.get('item', {}).get('value', '').split('/')[-1]
        instance_of_qid = result.get('instanceOf', {}).get('value', '').split('/')[-1] if 'instanceOf' in result else None
        instance_of_label = result.get('instanceOfLabel', {}).get('value', '') if 'instanceOfLabel' in result else None
        
        if source_qid and source_qid.startswith('Q'):
            backlinks.append({
                'source_qid': source_qid,
                'instance_of_qid': instance_of_qid,
                'instance_of_label': instance_of_label
            })
    
    return backlinks


print("="*80)
print("WIKIDATA BACKLINK EXTRACTION")
print("="*80)
print(f"Start: {datetime.now()}")
print()

# Load our entities
print("Loading entities from Neo4j...")
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    result = session.run("MATCH (e:Entity) RETURN e.qid as qid, e.label as label ORDER BY e.qid")
    our_entities = [(r['qid'], r['label']) for r in result]

driver.close()

print(f"  Entities to query: {len(our_entities):,}")
print()

# Extract backlinks for each - INCREMENTAL WRITE
backlink_data = {}
total_backlinks = 0
output_file = f'output/wikidata_backlinks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

print("Querying Wikidata for backlinks...")
print(f"Output file: {output_file}")
print("(Writing incrementally - safe if interrupted)")
print()

# Initialize output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('{\n')

for i, (qid, label) in enumerate(our_entities, 1):
    if i % 10 == 0:
        print(f"  Progress: {i}/{len(our_entities)} ({i/len(our_entities)*100:.1f}%) - {total_backlinks:,} backlinks found")
    
    # Query Wikidata
    backlinks = get_backlinks_for_qid(qid, limit=1000)
    
    entity_data = {
        'label': label,
        'backlink_count': len(backlinks),
        'backlinks': backlinks
    }
    
    backlink_data[qid] = entity_data
    total_backlinks += len(backlinks)
    
    # Write incrementally (append to file)
    with open(output_file, 'a', encoding='utf-8') as f:
        comma = ',' if i < len(our_entities) else ''
        f.write(f'  "{qid}": {json.dumps(entity_data, indent=4)}{comma}\n')
    
    # Checkpoint every 100 entities
    if i % 100 == 0:
        print(f"  Checkpoint: {i} entities processed, {total_backlinks:,} backlinks")
    
    # Rate limit
    time.sleep(0.1)  # Be nice to Wikidata

# Close JSON
with open(output_file, 'a', encoding='utf-8') as f:
    f.write('}\n')

print()
print(f"Extraction complete!")
print(f"  Total backlinks: {total_backlinks:,}")
print(f"  Avg per entity: {total_backlinks/len(our_entities):.1f}")
print()

print(f"Saved: {output_file}")
print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)

# Top 10 by backlink count
sorted_entities = sorted(backlink_data.items(), key=lambda x: x[1]['backlink_count'], reverse=True)
print("\nTop 10 entities by Wikidata backlink count:")
for qid, data in sorted_entities[:10]:
    print(f"  {qid} ({data['label']}): {data['backlink_count']:,} backlinks")

print()
print(f"Extraction complete: {datetime.now()}")
print("="*80)
