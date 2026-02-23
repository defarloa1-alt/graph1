#!/usr/bin/env python3
"""
Validate Property Facet Assignments by Analyzing Backlinks

Checks what entity types actually USE a property to validate
facet assignment quality.

Sample properties to validate:
- P241 (military branch) → Should be used by military people
- P509 (cause of death) → Should be used by people
- P112 (founded by) → Should be used by organizations
"""

import requests
import time
from bs4 import BeautifulSoup
from collections import Counter
import re

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_BASE = "https://www.wikidata.org"
USER_AGENT = "Chrystallum/1.0"

# Properties to validate
VALIDATION_SAMPLE = [
    ("P241", "military branch", "MILITARY"),
    ("P410", "military rank", "MILITARY"),
    ("P19", "place of birth", "BIOGRAPHIC"),
    ("P20", "place of death", "BIOGRAPHIC"),
    ("P509", "cause of death", "BIOGRAPHIC"),
    ("P112", "founded by", "BIOGRAPHIC"),
    ("P166", "award received", "INTELLECTUAL"),
    ("P607", "conflict", "MILITARY"),
]


def get_backlink_sample(property_id: str, limit: int = 50) -> list:
    """Get sample of entities that use this property"""
    url = f"{WIKIDATA_BASE}/w/index.php"
    params = {
        "title": f"Special:WhatLinksHere/Property:{property_id}",
        "limit": limit
    }
    
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    results_list = soup.find('ul', id='mw-whatlinkshere-list')
    
    entities = []
    if results_list:
        for li in results_list.find_all('li', recursive=False):
            link = li.find('a', href=re.compile(r'/wiki/Q\d+'))
            if link:
                href = link.get('href', '')
                qid_match = re.search(r'Q\d+', href)
                if qid_match:
                    qid = qid_match.group(0)
                    label = link.get_text(strip=True)
                    entities.append({'qid': qid, 'label': label})
    
    return entities


def get_entity_types(qids: list) -> dict:
    """Get P31 (instance of) for entities"""
    if not qids:
        return {}
    
    entity_types = {}
    
    # Batch in groups of 50
    for i in range(0, len(qids), 50):
        batch = qids[i:i+50]
        qid_str = "|".join(batch)
        
        params = {
            "action": "wbgetentities",
            "ids": qid_str,
            "format": "json",
            "props": "claims",
            "languages": "en"
        }
        
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(WIKIDATA_API, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for qid, entity in data.get("entities", {}).items():
                p31_claims = entity.get("claims", {}).get("P31", [])
                types = []
                for claim in p31_claims[:3]:
                    try:
                        type_qid = claim["mainsnak"]["datavalue"]["value"]["id"]
                        types.append(type_qid)
                    except (KeyError, TypeError):
                        pass
                entity_types[qid] = types
        
        time.sleep(1)
    
    return entity_types


# Known entity type classifications
ENTITY_TYPE_NAMES = {
    'Q5': 'human',
    'Q43229': 'organization',
    'Q1190554': 'event',
    'Q515': 'city',
    'Q486972': 'settlement',
    'Q11514315': 'historical period',
    'Q1048835': 'political entity',
    'Q8425': 'society',
    'Q43229': 'organization',
}


def classify_entity_type(p31_values: list) -> str:
    """Classify entity based on P31 values"""
    for p31 in p31_values:
        if p31 in ENTITY_TYPE_NAMES:
            return ENTITY_TYPE_NAMES[p31]
    
    # Fallback: return first P31
    return p31_values[0] if p31_values else 'unknown'


def validate_property(property_id: str, property_label: str, assigned_facet: str):
    """Validate property assignment by checking backlinks"""
    
    print(f"\n{'='*80}")
    print(f"Property: {property_id} - {property_label}")
    print(f"Assigned Facet: {assigned_facet}")
    print('='*80)
    
    # Get backlink sample
    print("Fetching backlinks (first 50)...", end=" ", flush=True)
    backlinks = get_backlink_sample(property_id, limit=50)
    print(f"Found {len(backlinks)}")
    
    if not backlinks:
        print("  No backlinks found")
        return
    
    # Get entity types
    print("Analyzing entity types...", end=" ", flush=True)
    qids = [e['qid'] for e in backlinks]
    entity_types = get_entity_types(qids)
    print("Done")
    
    # Classify
    type_counts = Counter()
    for qid in qids:
        p31_values = entity_types.get(qid, [])
        entity_type = classify_entity_type(p31_values)
        type_counts[entity_type] += 1
    
    # Display results
    print(f"\nEntity Type Distribution (out of {len(backlinks)} sampled):")
    for entity_type, count in type_counts.most_common(10):
        pct = (count / len(backlinks)) * 100
        print(f"  {entity_type:25} {count:>3} ({pct:>5.1f}%)")
    
    # Validation
    print(f"\nValidation:")
    if assigned_facet == "MILITARY" and type_counts.get('human', 0) > len(backlinks) * 0.5:
        print("  [OK] VALID - Military property used primarily on humans (soldiers, commanders)")
    elif assigned_facet == "BIOGRAPHIC" and type_counts.get('human', 0) > len(backlinks) * 0.7:
        print("  [OK] VALID - Biographical property used primarily on humans")
    elif assigned_facet == "POLITICAL" and (type_counts.get('human', 0) + type_counts.get('organization', 0)) > len(backlinks) * 0.5:
        print("  [OK] VALID - Political property used on humans and organizations")
    else:
        print(f"  [CHECK] Usage pattern may not match assigned facet")
    
    # Sample entities
    print(f"\nSample entities using this property:")
    for i, entity in enumerate(backlinks[:10], 1):
        qid = entity['qid']
        label = entity['label'][:60]
        types = entity_types.get(qid, [])
        type_name = classify_entity_type(types)
        print(f"  {i:2}. {label:60} ({type_name})")


def main():
    print("="*80)
    print("PROPERTY FACET VALIDATION VIA BACKLINK ANALYSIS")
    print("="*80)
    print()
    print("Validating sample properties by checking what entities actually use them")
    print()
    
    for property_id, property_label, assigned_facet in VALIDATION_SAMPLE:
        validate_property(property_id, property_label, assigned_facet)
        time.sleep(2)  # Rate limiting
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
