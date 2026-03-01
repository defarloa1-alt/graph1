#!/usr/bin/env python3
"""
Fetch sample QIDs by type using SPARQL for larger pattern mining
Focuses on historically relevant entity types
"""

import requests
import time
from typing import List, Dict

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "Graph1PropertyPatternMiner/1.0 (Chrystallum Knowledge Graph)"

# Historically relevant types for Chrystallum
HISTORICAL_TYPES = {
    'Q5': {'label': 'human', 'sample_size': 100},
    'Q6256': {'label': 'country', 'sample_size': 100},
    'Q178561': {'label': 'battle', 'sample_size': 100},
    'Q515': {'label': 'city', 'sample_size': 100},
    'Q82794': {'label': 'geographic region', 'sample_size': 80},
    'Q4830453': {'label': 'business', 'sample_size': 50},
    'Q43229': {'label': 'organization', 'sample_size': 80},
    'Q7275': {'label': 'state', 'sample_size': 80},
    'Q151885': {'label': 'concept', 'sample_size': 50},
    'Q8502': {'label': 'mountain', 'sample_size': 50},
    'Q4022': {'label': 'river', 'sample_size': 50},
    'Q12731': {'label': 'empire', 'sample_size': 50},
    'Q12060225': {'label': 'historical country', 'sample_size': 60},
}

def fetch_samples_for_type(type_qid: str, limit: int = 100) -> List[str]:
    """Fetch sample QIDs of a given type using SPARQL"""
    query = f"""
    SELECT DISTINCT ?item WHERE {{
      ?item wdt:P31 wd:{type_qid} .
    }}
    LIMIT {limit}
    """
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/sparql-results+json'
    }
    
    try:
        response = requests.get(
            SPARQL_ENDPOINT,
            params={'query': query, 'format': 'json'},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        results = response.json()
        qids = []
        
        for binding in results.get('results', {}).get('bindings', []):
            uri = binding.get('item', {}).get('value', '')
            if uri.startswith('http://www.wikidata.org/entity/'):
                qid = uri.split('/')[-1]
                qids.append(qid)
        
        return qids
    
    except Exception as e:
        print(f"  ❌ Error fetching {type_qid}: {e}")
        return []

def main():
    print("="*80)
    print("Wikidata Sample Fetcher for Property Pattern Mining")
    print("="*80)
    print(f"Fetching samples for {len(HISTORICAL_TYPES)} entity types\n")
    
    all_qids = []
    type_mapping = {}  # qid -> type info
    
    for type_qid, info in HISTORICAL_TYPES.items():
        print(f"Fetching {info['label']} ({type_qid})... ", end='', flush=True)
        
        qids = fetch_samples_for_type(type_qid, info['sample_size'])
        
        if qids:
            print(f"✓ {len(qids)} items")
            all_qids.extend(qids)
            
            # Track which type each QID belongs to
            for qid in qids:
                if qid not in type_mapping:
                    type_mapping[qid] = []
                type_mapping[qid].append({
                    'type_qid': type_qid,
                    'type_label': info['label']
                })
        else:
            print(f"✗ No results")
        
        time.sleep(1)  # Rate limiting
    
    # Remove duplicates while preserving type mapping
    unique_qids = list(set(all_qids))
    
    print(f"\n{'='*80}")
    print(f"✅ Fetched {len(unique_qids)} unique QIDs (from {len(all_qids)} total)")
    print(f"{'='*80}\n")
    
    # Save to file
    output_file = 'historical_entity_samples.txt'
    with open(output_file, 'w') as f:
        f.write('\n'.join(unique_qids))
    
    print(f"💾 Saved to: {output_file}")
    print(f"\n💡 Next: Run property pattern miner with these QIDs:")
    print(f"   python Python/wikidata_property_pattern_miner.py --qids $(cat {output_file} | tr '\\n' ',')")
    
    # Also save mapping
    import json
    mapping_file = 'config/historical_entity_type_mapping.json'
    with open(mapping_file, 'w') as f:
        json.dump(type_mapping, f, indent=2)
    print(f"💾 Type mapping saved to: {mapping_file}")

if __name__ == '__main__':
    main()
