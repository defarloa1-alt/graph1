#!/usr/bin/env python3
"""
Retrieve ALL LCSH subjects with LCC Class D (History) from Wikidata
"""

import sys
import io
import time
import csv
import requests

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
OUTPUT_FILE = "../output/lcsh_class_d_complete.csv"

def query_wikidata_class_d():
    """
    Query Wikidata for ALL entities with LCC Class D (History)
    """
    query = """
    SELECT DISTINCT ?lcsh ?label ?lcc ?dewey ?fast ?broader WHERE {
      ?item wdt:P1149 ?lcc .
      FILTER(STRSTARTS(?lcc, "D"))
      
      ?item wdt:P244 ?lcsh .
      ?item rdfs:label ?label .
      FILTER(LANG(?label) = "en")
      
      OPTIONAL { ?item wdt:P1036 ?dewey . }
      OPTIONAL { ?item wdt:P2163 ?fast . }
      
      # Get broader subject if exists
      OPTIONAL {
        ?item skos:broader ?broaderItem .
        ?broaderItem wdt:P244 ?broader .
      }
    }
    ORDER BY ?lcc
    """
    
    headers = {
        'User-Agent': 'ChrystallumGraphBuilder/1.0',
        'Accept': 'application/json'
    }
    
    print("[QUERY] Fetching ALL LCC Class D subjects from Wikidata...")
    print("This may take 60-120 seconds...")
    
    try:
        response = requests.get(
            WIKIDATA_ENDPOINT,
            params={'query': query, 'format': 'json'},
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for binding in data['results']['bindings']:
            results.append({
                'lcsh_id': binding['lcsh']['value'],
                'label': binding['label']['value'],
                'lcc_code': binding['lcc']['value'],
                'dewey_decimal': binding.get('dewey', {}).get('value', ''),
                'fast_id': binding.get('fast', {}).get('value', ''),
                'broader_lcsh': binding.get('broader', {}).get('value', '')
            })
        
        return results
    
    except Exception as e:
        print(f"[ERROR] Wikidata query failed: {e}")
        return []

def write_csv(results, filename):
    """Write results to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'lcsh_id', 'label', 'lcc_code', 'dewey_decimal', 'fast_id', 'broader_lcsh'
        ])
        writer.writeheader()
        writer.writerows(results)

def main():
    print("="*80)
    print("RETRIEVE ALL LCC CLASS D (HISTORY) SUBJECTS")
    print("="*80)
    
    # Query Wikidata
    results = query_wikidata_class_d()
    
    if not results:
        print("[ERROR] No results retrieved!")
        return
    
    print(f"\n[SUCCESS] Found {len(results)} Class D subjects")
    
    # Statistics
    with_dewey = sum(1 for x in results if x['dewey_decimal'])
    with_fast = sum(1 for x in results if x['fast_id'])
    with_broader = sum(1 for x in results if x['broader_lcsh'])
    
    print(f"\n[COVERAGE]")
    print(f"  LCSH IDs:        {len(results)} (100%)")
    print(f"  LCC Codes:       {len(results)} (100%)")
    print(f"  Dewey Decimals:  {with_dewey} ({with_dewey/len(results)*100:.1f}%)")
    print(f"  FAST IDs:        {with_fast} ({with_fast/len(results)*100:.1f}%)")
    print(f"  Broader links:   {with_broader} ({with_broader/len(results)*100:.1f}%)")
    
    # Sample
    print(f"\n[SAMPLE] First 5 results:")
    for item in results[:5]:
        print(f"\n  {item['lcsh_id']}: {item['label']}")
        print(f"    LCC:     {item['lcc_code']}")
        print(f"    Dewey:   {item['dewey_decimal'] or 'N/A'}")
        print(f"    FAST:    {item['fast_id'] or 'N/A'}")
        print(f"    Broader: {item['broader_lcsh'] or 'N/A'}")
    
    # Write CSV
    write_csv(results, OUTPUT_FILE)
    print(f"\n[SUCCESS] Wrote {len(results)} subjects to: {OUTPUT_FILE}")
    
    print("\n" + "="*80)
    print("[NEXT STEP] Run: python .\\Python\\lcsh\\scripts\\import_lcsh_class_d.py")
    print("="*80)

if __name__ == "__main__":
    main()

