#!/usr/bin/env python3
"""
SCA Complete Domain Builder - Command Line with Progress

Shows real-time progress in terminal with throttling
"""

import sys
from pathlib import Path
import time
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.agents.wikidata_full_fetch_enhanced import WikidataEnhancedFetcher


def build_complete_domain(seed_qid: str, throttle: float = 1.0):
    """Build complete domain with progress"""
    
    print(f"\n{'='*80}")
    print(f"SCA COMPLETE DOMAIN BUILDER")
    print(f"{'='*80}\n")
    print(f"Seed: {seed_qid}")
    print(f"Throttle: {throttle}s between requests")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")
    
    fetcher = WikidataEnhancedFetcher()
    entities_collected = {}
    
    # PHASE 1: Fetch seed
    print(f"{'#'*80}")
    print(f"PHASE 1: SEED ENTITY")
    print(f"{'#'*80}\n")
    
    print(f"Fetching {seed_qid}...")
    seed_data = fetcher.fetch_entity_with_labels(seed_qid)
    
    seed_label = seed_data['labels']['en']
    props = seed_data['statistics']['total_properties']
    
    print(f"SUCCESS: {seed_label}")
    print(f"  Properties: {props}")
    print(f"  Labels resolved: {len(fetcher.label_cache)}\n")
    
    entities_collected[seed_qid] = seed_data
    time.sleep(throttle)
    
    # PHASE 2: Extract relationships
    print(f"{'#'*80}")
    print(f"PHASE 2: RELATIONSHIPS")
    print(f"{'#'*80}\n")
    
    claims = seed_data['claims_with_labels']
    
    # Get all QID references
    parents = []
    children = []
    lateral = []
    
    # Parents
    for prop in ['P31', 'P279', 'P361']:
        if prop in claims:
            for stmt in claims[prop]['statements']:
                if stmt['value'].startswith('Q'):
                    parents.append({
                        'qid': stmt['value'],
                        'label': stmt['value_label'],
                        'prop': prop
                    })
    
    # Children
    if 'P527' in claims:
        for stmt in claims['P527']['statements']:
            if stmt['value'].startswith('Q'):
                children.append({
                    'qid': stmt['value'],
                    'label': stmt['value_label']
                })
    
    # Lateral
    for prop, ptype in [('P36', 'place'), ('P793', 'event'), 
                        ('P194', 'org'), ('P38', 'object')]:
        if prop in claims:
            for stmt in claims[prop]['statements']:
                val = stmt['value']
                if isinstance(val, str) and val.startswith('Q'):
                    lateral.append({
                        'qid': val,
                        'label': stmt['value_label'],
                        'type': ptype,
                        'prop': prop
                    })
    
    print(f"Found:")
    print(f"  Parents: {len(parents)}")
    print(f"  Children: {len(children)}")
    print(f"  Lateral: {len(lateral)}\n")
    
    # PHASE 3: Fetch lateral (these are domain entities)
    print(f"{'#'*80}")
    print(f"PHASE 3: LATERAL ENTITIES")
    print(f"{'#'*80}\n")
    
    authorities = []
    
    for i, ent in enumerate(lateral):
        print(f"[{i+1}/{len(lateral)}] {ent['qid']} ({ent['label']}) [{ent['type']}]...")
        
        try:
            ent_data = fetcher.fetch_entity_with_labels(ent['qid'])
            entities_collected[ent['qid']] = ent_data
            
            # Check authorities
            ent_claims = ent_data['claims_with_labels']
            found_auths = {}
            
            if 'P244' in ent_claims:
                found_auths['LCSH'] = ent_claims['P244']['statements'][0]['value']
            if 'P1584' in ent_claims:
                found_auths['Pleiades'] = ent_claims['P1584']['statements'][0]['value']
            if 'P2163' in ent_claims:
                found_auths['FAST'] = ent_claims['P2163']['statements'][0]['value']
            if 'P1667' in ent_claims:
                found_auths['TGN'] = ent_claims['P1667']['statements'][0]['value']
            
            if found_auths:
                print(f"  SUCCESS - Authorities: {found_auths}")
                authorities.append({
                    'qid': ent['qid'],
                    'label': ent['label'],
                    'authorities': found_auths
                })
            else:
                print(f"  OK - No authorities")
            
            time.sleep(throttle)
            
        except Exception as e:
            print(f"  FAILED: {e}")
    
    print()
    
    # FINAL SUMMARY
    print(f"{'='*80}")
    print(f"DOMAIN BUILDING COMPLETE")
    print(f"{'='*80}\n")
    
    print(f"Seed: {seed_qid} ({seed_label})")
    print(f"Total entities: {len(entities_collected)}")
    print(f"With authorities: {len(authorities)}\n")
    
    if authorities:
        print(f"ENTITIES WITH AUTHORITY IDs:\n")
        for auth in authorities:
            print(f"{auth['qid']} - {auth['label']}")
            for auth_type, auth_id in auth['authorities'].items():
                print(f"  {auth_type}: {auth_id}")
            print()
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"output/sca_complete/{seed_qid}_domain_{timestamp}.json"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    summary = {
        'seed_qid': seed_qid,
        'seed_label': seed_label,
        'total_entities': len(entities_collected),
        'entities_with_authorities': len(authorities),
        'authorities': authorities,
        'timestamp': timestamp
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"Saved: {output_path}\n")
    
    return summary


if __name__ == "__main__":
    seed = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    throttle = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    
    build_complete_domain(seed, throttle)
