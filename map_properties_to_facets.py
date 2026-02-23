#!/usr/bin/env python3
"""
Automatic Property → Facet Mapping

Takes Wikidata properties and automatically maps them to Chrystallum facets
by querying their P31 (instance of) classifications.

Input: List of property IDs (P31, P39, P580, etc.)
Output: CSV with property → facet mappings

Usage:
    python map_properties_to_facets.py
    python map_properties_to_facets.py --input CSV/wikiPvalues.csv
"""

import csv
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import requests

# Configuration
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Chrystallum/1.0 (property facet mapper)"
REQUEST_DELAY = 0.5

# Load property type classifications
PROPERTY_TYPES_FILE = Path("CSV/backlinks/Q107649491_property_types_CLEAN.csv")

# Output
OUTPUT_DIR = Path("CSV/property_mappings")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Facet mapping rules (based on property type QIDs)
FACET_RULES = {
    'MILITARY': {
        'Q22964288',  # property for items about military
        'Q51089849',  # weapons and military equipment
    },
    'POLITICAL': {
        'Q22984475',  # related to politics
        'Q22997934',  # government and state
        'Q93433126',  # authority control for politicians
        'Q56457408',  # items about positions
    },
    'RELIGIOUS': {
        'Q22983697',  # religions and beliefs
        'Q64263681',  # Catholicism
        'Q64264420',  # Christianity
        'Q64289010',  # Buddhism
        'Q64348848',  # Judaism
        'Q64349017',  # Eastern Orthodox
        'Q73688627',  # Islam
        'Q64295974',  # Greek mythology
    },
    'GEOGRAPHIC': {
        'Q18615777',  # indicate a location
        'Q18635217',  # location of an event
        'Q19829908',  # authority control for places
        'Q19829914',  # related to places
        'Q52511956',  # related to geography
    },
    'INTELLECTUAL': {
        'Q18618644',  # creative works
        'Q19833377',  # authority control for works
        'Q29546443',  # items about books
        'Q29548341',  # scholarly articles
        'Q29561722',  # literature
        'Q54835335',  # philosophy
        'Q55192982',  # historiography
    },
    'ARTISTIC': {
        'Q27918607',  # related to art
        'Q44847669',  # identify artworks
        'Q45312863',  # sculpture
        'Q56216473',  # authority control for architects
        'Q43831109',  # architecture
    },
    'ARCHAEOLOGICAL': {
        'Q46246642',  # archaeology
        'Q107156662', # numismatics
        'Q51122237', # burials, graves, memorials
    },
    'ECONOMIC': {
        'Q21451178',  # economics
        'Q51326087',  # banking
        'Q106035765', # identify businesses
    },
    'DEMOGRAPHIC': {
        'Q22984494',  # demography
        'Q18608871',  # items about people
        'Q52514469',  # personal life
    },
    'CULTURAL': {
        'Q18618628',  # cultural heritage
        'Q23038310',  # food and eating
        'Q41804262',  # gastronomy
        'Q105999586', # ethnic groups
    },
    'SCIENTIFIC': {
        'Q21294996',  # chemistry
        'Q21451142',  # astronomical objects
        'Q22981316',  # physics
        'Q42752243',  # anatomy
        'Q61058429',  # science
        'Q52425722',  # natural science
    },
    'LINGUISTIC': {
        'Q18616084',  # indicate a language
        'Q20824104',  # items about languages
        'Q29887391',  # linguistics
        'Q51092639',  # phonetics
        'Q54076056',  # lexicographical data
    },
    'BIOGRAPHIC': {
        'Q18608756',  # birth or death
        'Q18636233',  # person-related event
        'Q19595382',  # authority control for people
        'Q56249073',  # genealogy
        'Q97584729',  # biographical dictionaries
    },
    'DIPLOMATIC': {
        'Q22984026',  # law and justice
        'Q29642812',  # United Nations
    },
    'TECHNOLOGICAL': {
        'Q21126229',  # software
        'Q47512165',  # computing
    },
    'ENVIRONMENTAL': {
        'Q52431918',  # seismology
        'Q22969167',  # climate
    },
    'SOCIAL': {
        'Q96533552',  # social science
    },
}

# Historical period types (get priority scoring)
HISTORICAL_TYPES = {
    'Q56248884',  # Ancient World
    'Q56248867',  # Middle Ages
    'Q56248906',  # Early Modern period
    'Q106827312', # Renaissance
}

# Authority control (get priority scoring)
AUTHORITY_CONTROL_TYPES = {
    'Q18614948',  # general authority control
    'Q19595382',  # for people
    'Q19829908',  # for places
    'Q19833377',  # for works
}


def load_property_types() -> dict:
    """Load property type classifications from CSV"""
    if not PROPERTY_TYPES_FILE.exists():
        print(f"Warning: {PROPERTY_TYPES_FILE} not found")
        return {}
    
    types = {}
    with open(PROPERTY_TYPES_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            types[row['qid']] = {
                'label': row['label'],
                'description': row['description']
            }
    
    return types


def get_property_classifications(property_id: str) -> dict:
    """Get P31 (instance of) classifications for a property"""
    params = {
        "action": "wbgetentities",
        "ids": property_id,
        "format": "json",
        "props": "labels|descriptions|claims",
        "languages": "en"
    }
    
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(WIKIDATA_API, headers=headers, params=params)
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    entity = data.get("entities", {}).get(property_id, {})
    
    label = entity.get("labels", {}).get("en", {}).get("value", property_id)
    description = entity.get("descriptions", {}).get("en", {}).get("value", "")
    
    # Get P31 classifications
    claims = entity.get("claims", {})
    p31_claims = claims.get("P31", [])
    
    type_qids = []
    for claim in p31_claims:
        try:
            qid = claim["mainsnak"]["datavalue"]["value"]["id"]
            type_qids.append(qid)
        except (KeyError, TypeError):
            pass
    
    return {
        "property_id": property_id,
        "label": label,
        "description": description,
        "type_qids": type_qids
    }


def map_to_facets(type_qids: list) -> dict:
    """
    Map property type QIDs to Chrystallum facets
    
    Returns:
        {
            'primary_facet': 'MILITARY',
            'secondary_facets': ['POLITICAL', 'BIOGRAPHIC'],
            'is_historical': True/False,
            'is_authority_control': True/False,
            'confidence': 0.0-1.0
        }
    """
    matched_facets = []
    
    # Check each facet's rules
    for facet, type_set in FACET_RULES.items():
        if any(t in type_set for t in type_qids):
            matched_facets.append(facet)
    
    # Check special categories
    is_historical = any(t in HISTORICAL_TYPES for t in type_qids)
    is_authority = any(t in AUTHORITY_CONTROL_TYPES for t in type_qids)
    
    # Determine confidence based on matches
    confidence = 0.5  # Base
    if matched_facets:
        confidence = 0.8
    if is_historical or is_authority:
        confidence = min(confidence + 0.2, 1.0)
    
    return {
        'primary_facet': matched_facets[0] if matched_facets else 'UNKNOWN',
        'secondary_facets': matched_facets[1:] if len(matched_facets) > 1 else [],
        'all_facets': matched_facets,
        'is_historical': is_historical,
        'is_authority_control': is_authority,
        'confidence': confidence,
        'type_count': len(type_qids)
    }


def process_properties(property_ids: list, property_types: dict) -> list:
    """Process a list of properties and map to facets"""
    
    results = []
    
    print(f"\nProcessing {len(property_ids)} properties...")
    print()
    
    for i, prop_id in enumerate(property_ids, 1):
        print(f"[{i}/{len(property_ids)}] {prop_id}...", end=" ", flush=True)
        
        try:
            # Get property classifications
            prop_data = get_property_classifications(prop_id)
            
            if not prop_data:
                print("FAILED")
                continue
            
            # Map to facets
            facet_mapping = map_to_facets(prop_data['type_qids'])
            
            # Get type labels
            type_labels = []
            for type_qid in prop_data['type_qids']:
                type_info = property_types.get(type_qid, {})
                type_labels.append(type_info.get('label', type_qid))
            
            result = {
                'property_id': prop_id,
                'property_label': prop_data['label'],
                'property_description': prop_data['description'],
                'type_qids': ','.join(prop_data['type_qids']),
                'type_labels': ' | '.join(type_labels),
                'primary_facet': facet_mapping['primary_facet'],
                'secondary_facets': ','.join(facet_mapping['secondary_facets']),
                'all_facets': ','.join(facet_mapping['all_facets']),
                'is_historical': facet_mapping['is_historical'],
                'is_authority_control': facet_mapping['is_authority_control'],
                'confidence': facet_mapping['confidence'],
                'type_count': facet_mapping['type_count']
            }
            
            results.append(result)
            
            print(f"OK - {facet_mapping['primary_facet']} (conf: {facet_mapping['confidence']:.2f})")
            
            time.sleep(REQUEST_DELAY)
            
        except Exception as e:
            print(f"ERROR: {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Map Wikidata properties to Chrystallum facets")
    parser.add_argument('--input', help='CSV file with property IDs (column: property_id or pid)')
    parser.add_argument('--properties', nargs='+', help='Space-separated property IDs (e.g., P31 P39 P580)')
    parser.add_argument('--limit', type=int, default=100, help='Max properties to process')
    
    args = parser.parse_args()
    
    print("="*80)
    print("AUTOMATIC PROPERTY TO FACET MAPPING")
    print("="*80)
    
    # Load property types reference
    print("\nLoading property type classifications...")
    property_types = load_property_types()
    print(f"  Loaded {len(property_types)} property types")
    
    # Get properties to process
    properties = []
    
    if args.properties:
        # From command line
        properties = args.properties
        print(f"\nProcessing {len(properties)} properties from command line")
    
    elif args.input:
        # From CSV file
        print(f"\nReading properties from: {args.input}")
        with open(args.input, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prop_id = row.get('property_id') or row.get('pid') or row.get('property')
                
                # Extract PID from URI if needed
                if prop_id and 'wikidata.org/entity/P' in prop_id:
                    # Extract P123 from http://www.wikidata.org/entity/P123
                    prop_id = prop_id.split('/')[-1]
                
                if prop_id and prop_id.startswith('P'):
                    properties.append(prop_id)
        print(f"  Found {len(properties)} properties")
    
    else:
        # Default: test set
        print("\nNo input specified. Using test set:")
        properties = [
            "P31", "P39", "P279", "P625", "P17", "P580", "P582",
            "P106", "P27", "P19", "P20", "P569", "P570",
            "P710", "P361", "P131", "P276", "P585"
        ]
        print(f"  {len(properties)} test properties")
    
    # Limit
    if len(properties) > args.limit:
        print(f"\nLimiting to first {args.limit} properties")
        properties = properties[:args.limit]
    
    # Process
    results = process_properties(properties, property_types)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"property_facet_mapping_{timestamp}.csv"
    
    print(f"\nWriting results to: {output_file}")
    
    fieldnames = [
        'property_id', 'property_label', 'property_description',
        'type_qids', 'type_labels',
        'primary_facet', 'secondary_facets', 'all_facets',
        'is_historical', 'is_authority_control', 'confidence', 'type_count'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"  Written {len(results)} rows")
    
    # Statistics
    print("\n" + "="*80)
    print("MAPPING STATISTICS")
    print("="*80)
    print()
    
    facet_counts = defaultdict(int)
    for r in results:
        facet_counts[r['primary_facet']] += 1
    
    print("Properties by primary facet:")
    for facet in sorted(facet_counts.keys()):
        count = facet_counts[facet]
        print(f"  {facet:20} {count:>4}")
    print()
    
    # Historical properties
    historical = [r for r in results if r['is_historical']]
    print(f"Historical properties: {len(historical)}")
    
    # Authority control
    authority = [r for r in results if r['is_authority_control']]
    print(f"Authority control properties: {len(authority)}")
    
    # High confidence
    high_conf = [r for r in results if r['confidence'] >= 0.8]
    print(f"High confidence mappings (>=0.8): {len(high_conf)}")
    print()
    
    # Sample
    print("Sample mappings:")
    for r in results[:10]:
        facets = r['all_facets'] if r['all_facets'] else 'UNKNOWN'
        print(f"  {r['property_id']:6} {r['property_label'][:35]:35} -> {facets}")
    print()
    
    print("="*80)
    print("COMPLETE!")
    print("="*80)
    print()
    print("Next steps:")
    print(f"  1. Review: {output_file}")
    print(f"  2. Validate facet mappings")
    print(f"  3. Import to Neo4j for property routing")


if __name__ == "__main__":
    main()
