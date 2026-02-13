#!/usr/bin/env python3
"""
Enrich LCSH subjects with classification codes from Wikidata
Focus on LCC subclass DG (Italy/Roman history)
"""

import sys
import io
import time
import requests
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chrystallum"

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

# LCC prefix to focus on
LCC_PREFIX = "DG"  # Italy/Roman history

def query_wikidata_by_lcc_prefix(lcc_prefix):
    """
    Query Wikidata for all entities with LCC codes starting with prefix
    and retrieve their LCSH, Dewey, LCC, FAST codes
    """
    query = f"""
    SELECT DISTINCT ?lcsh ?dewey ?lcc ?fast ?label WHERE {{
      ?item wdt:P1149 ?lcc .
      FILTER(STRSTARTS(?lcc, "{lcc_prefix}"))
      
      ?item wdt:P244 ?lcsh .
      ?item rdfs:label ?label .
      FILTER(LANG(?label) = "en")
      
      OPTIONAL {{ ?item wdt:P1036 ?dewey . }}
      OPTIONAL {{ ?item wdt:P2163 ?fast . }}
    }}
    ORDER BY ?lcc
    """
    
    headers = {
        'User-Agent': 'ChrystallumGraphBuilder/1.0 (historical knowledge graph)',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            WIKIDATA_ENDPOINT,
            params={'query': query, 'format': 'json'},
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for binding in data['results']['bindings']:
            results.append({
                'lcsh_id': binding['lcsh']['value'],
                'lcc_code': binding['lcc']['value'],
                'dewey_decimal': binding.get('dewey', {}).get('value'),
                'fast_id': binding.get('fast', {}).get('value'),
                'label': binding['label']['value']
            })
        
        return results
    
    except Exception as e:
        print(f"[ERROR] Wikidata query failed: {e}")
        return []

def update_neo4j_subjects(driver, enriched_data):
    """
    Update existing LCSH subjects in Neo4j with classification codes
    """
    updated = 0
    matched = 0
    not_found = 0
    
    with driver.session() as session:
        for item in enriched_data:
            lcsh_id = item['lcsh_id']
            
            # Check if subject exists
            result = session.run(
                "MATCH (s:Subject {lcsh_id: $lcsh_id}) RETURN s",
                lcsh_id=lcsh_id
            )
            
            if result.single():
                matched += 1
                
                # Update with new classification codes
                session.run("""
                    MATCH (s:Subject {lcsh_id: $lcsh_id})
                    SET s.lcc_code = $lcc_code,
                        s.dewey_decimal = $dewey_decimal,
                        s.fast_id = $fast_id
                """, 
                    lcsh_id=lcsh_id,
                    lcc_code=item['lcc_code'],
                    dewey_decimal=item['dewey_decimal'],
                    fast_id=item['fast_id']
                )
                
                updated += 1
                
                if updated % 10 == 0:
                    print(f"  [PROGRESS] Updated {updated}/{matched} subjects...")
            else:
                not_found += 1
    
    return updated, matched, not_found

def main():
    print("=" * 80)
    print("ENRICH LCSH SUBJECTS FROM WIKIDATA")
    print(f"LCC Subclass: {LCC_PREFIX} (Italy/Roman History)")
    print("=" * 80)
    
    # Step 1: Query Wikidata
    print(f"\n[STEP 1] Querying Wikidata for LCC {LCC_PREFIX}...")
    print("This may take 30-60 seconds...")
    
    enriched_data = query_wikidata_by_lcc_prefix(LCC_PREFIX)
    
    if not enriched_data:
        print("[ERROR] No results from Wikidata!")
        return
    
    print(f"[SUCCESS] Found {len(enriched_data)} entities in Wikidata")
    
    # Show statistics
    with_dewey = sum(1 for x in enriched_data if x['dewey_decimal'])
    with_fast = sum(1 for x in enriched_data if x['fast_id'])
    
    print(f"\n[COVERAGE]")
    print(f"  LCSH IDs:        {len(enriched_data)} (100%)")
    print(f"  LCC Codes:       {len(enriched_data)} (100%)")
    print(f"  Dewey Decimals:  {with_dewey} ({with_dewey/len(enriched_data)*100:.1f}%)")
    print(f"  FAST IDs:        {with_fast} ({with_fast/len(enriched_data)*100:.1f}%)")
    
    # Show sample
    print(f"\n[SAMPLE] First 3 results:")
    for item in enriched_data[:3]:
        print(f"\n  {item['lcsh_id']}: {item['label']}")
        print(f"    LCC:   {item['lcc_code']}")
        print(f"    Dewey: {item['dewey_decimal'] or 'N/A'}")
        print(f"    FAST:  {item['fast_id'] or 'N/A'}")
    
    # Step 2: Update Neo4j
    print(f"\n[STEP 2] Updating Neo4j...")
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        updated, matched, not_found = update_neo4j_subjects(driver, enriched_data)
        
        print(f"\n[RESULTS]")
        print(f"  Matched in Neo4j:     {matched}")
        print(f"  Successfully updated: {updated}")
        print(f"  Not found in Neo4j:   {not_found}")
        
        if not_found > 0:
            print(f"\n[NOTE] {not_found} LCSH IDs from Wikidata don't exist in Neo4j yet.")
            print("  These may need to be imported first.")
    
    finally:
        driver.close()
    
    print("\n" + "=" * 80)
    print("[COMPLETE] Enrichment finished!")
    print("=" * 80)

if __name__ == "__main__":
    main()

