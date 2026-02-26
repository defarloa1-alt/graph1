#!/usr/bin/env python3
"""
SCA Enhanced Traversal - Complete Details

Shows for EACH entity:
- QID (Label)
- Hierarchy: Parents (P31, P279, P361) with labels
- Hierarchy: Children (P527) with labels  
- External IDs: LCSH, FAST, Pleiades, TGN with labels
- Key Properties: Top properties with labels
- ALL with labels on everything!
"""

import sys
from pathlib import Path
import time
from datetime import datetime
from collections import deque
import json
import requests

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


class EnhancedTraversal:
    """Traversal with complete details and labels"""
    
    def __init__(self, seed_qid, max_entities=5000, throttle=1.0):
        self.seed_qid = seed_qid
        self.max_entities = max_entities
        self.throttle = throttle
        
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        
        self.visited = set()
        self.queue = deque()
        self.entities = {}
        self.label_cache = {}
        
    def fetch_with_details(self, qid):
        """Fetch entity and extract detailed info"""
        
        # Fetch entity
        url = self.entity_url.format(qid=qid)
        response = requests.get(url, headers={'User-Agent': 'Chrystallum/1.0'})
        response.raise_for_status()
        
        data = response.json()
        entity = data.get('entities', {}).get(qid, {})
        
        # Extract info
        label = entity.get('labels', {}).get('en', {}).get('value', qid)
        claims = entity.get('claims', {})
        
        # Collect QIDs for label resolution
        all_qids = set()
        
        # Hierarchy
        hierarchy = {
            'parents': [],
            'children': []
        }
        
        # Parents
        for prop in ['P31', 'P279', 'P361']:
            if prop in claims:
                for claim in claims[prop]:
                    val_id = self._extract_entity_id(claim)
                    if val_id:
                        hierarchy['parents'].append({'prop': prop, 'qid': val_id})
                        all_qids.add(val_id)
        
        # Children
        for prop in ['P527', 'P150']:
            if prop in claims:
                for claim in claims[prop]:
                    val_id = self._extract_entity_id(claim)
                    if val_id:
                        hierarchy['children'].append({'prop': prop, 'qid': val_id})
                        all_qids.add(val_id)
        
        # External IDs
        external_ids = {}
        
        if 'P244' in claims:  # LCSH
            external_ids['LCSH'] = claims['P244'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
        if 'P2163' in claims:  # FAST
            external_ids['FAST'] = claims['P2163'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
        if 'P1149' in claims:  # LCC
            external_ids['LCC'] = claims['P1149'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
        if 'P1584' in claims:  # Pleiades
            external_ids['Pleiades'] = claims['P1584'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
        if 'P1667' in claims:  # Getty TGN
            external_ids['TGN'] = claims['P1667'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
        
        # Key properties (first 10)
        key_props = []
        for prop_id in list(claims.keys())[:10]:
            all_qids.add(prop_id)
            # Get first value
            first_claim = claims[prop_id][0]
            val_id = self._extract_entity_id(first_claim)
            if val_id:
                all_qids.add(val_id)
                key_props.append({'prop': prop_id, 'value': val_id})
        
        # Fetch labels for all collected QIDs
        if all_qids:
            self._fetch_labels_batch(all_qids)
        
        # Build result with labels
        result = {
            'qid': qid,
            'label': label,
            'properties_count': len(claims),
            'hierarchy': {
                'parents': [
                    {
                        'prop': p['prop'],
                        'prop_label': self._get_prop_label(p['prop']),
                        'qid': p['qid'],
                        'label': self.label_cache.get(p['qid'], p['qid'])
                    } for p in hierarchy['parents']
                ],
                'children': [
                    {
                        'prop': c['prop'],
                        'prop_label': self._get_prop_label(c['prop']),
                        'qid': c['qid'],
                        'label': self.label_cache.get(c['qid'], c['qid'])
                    } for c in hierarchy['children']
                ]
            },
            'external_ids': external_ids,
            'key_properties': [
                {
                    'prop': p['prop'],
                    'prop_label': self.label_cache.get(p['prop'], p['prop']),
                    'value': p['value'],
                    'value_label': self.label_cache.get(p['value'], p['value'])
                } for p in key_props
            ],
            'claims': claims
        }
        
        return result
    
    def _extract_entity_id(self, claim):
        """Extract QID from claim"""
        datavalue = claim.get('mainsnak', {}).get('datavalue', {})
        if datavalue.get('type') == 'wikibase-entityid':
            return datavalue.get('value', {}).get('id', '')
        return None
    
    def _get_prop_label(self, prop_id):
        """Get property label"""
        prop_labels = {
            'P31': 'instance of',
            'P279': 'subclass of',
            'P361': 'part of',
            'P527': 'has parts',
            'P150': 'contains'
        }
        return prop_labels.get(prop_id, self.label_cache.get(prop_id, prop_id))
    
    def _fetch_labels_batch(self, qids):
        """Fetch labels for QIDs"""
        qid_list = [q for q in qids if q not in self.label_cache and q.startswith('Q') or q.startswith('P')]
        
        for i in range(0, len(qid_list), 50):
            batch = qid_list[i:i+50]
            
            params = {
                'action': 'wbgetentities',
                'ids': '|'.join(batch),
                'props': 'labels',
                'languages': 'en',
                'format': 'json'
            }
            
            response = requests.get(self.api_url, params=params, headers={'User-Agent': 'Chrystallum/1.0'})
            response.raise_for_status()
            
            result = response.json()
            for eid, edata in result.get('entities', {}).items():
                self.label_cache[eid] = edata.get('labels', {}).get('en', {}).get('value', eid)
    
    def print_entity_details(self, entity_data, index, max_total):
        """Print complete entity details with all labels"""
        
        qid = entity_data['qid']
        label = entity_data['label']
        props = entity_data['properties_count']
        
        # Get entity types from P31 (instance of)
        types = [p['label'] for p in entity_data['hierarchy']['parents'] if p['prop'] == 'P31']
        type_str = ", ".join(types[:3]) if types else "Unknown"
        
        print(f"\n[{index}/{max_total}] {qid} ({label}) - TYPE: {type_str} - {props} props")
        print(f"{'='*80}")
        
        # Parents
        if entity_data['hierarchy']['parents']:
            print(f"\nPARENTS:")
            for p in entity_data['hierarchy']['parents'][:5]:
                print(f"  {p['prop']} ({p['prop_label']}): {p['qid']} ({p['label']})")
        
        # Children
        if entity_data['hierarchy']['children']:
            print(f"\nCHILDREN:")
            for c in entity_data['hierarchy']['children']:
                print(f"  {c['prop']} ({c['prop_label']}): {c['qid']} ({c['label']})")
        
        # External IDs
        if entity_data['external_ids']:
            print(f"\nEXTERNAL IDs:")
            for id_type, id_val in entity_data['external_ids'].items():
                print(f"  {id_type}: {id_val}")
        
        # Top properties
        if entity_data['key_properties']:
            print(f"\nKEY PROPERTIES (first 10):")
            for kp in entity_data['key_properties'][:10]:
                print(f"  {kp['prop']} ({kp['prop_label']}): {kp['value']} ({kp['value_label']})")
        
        print()
    
    def traverse(self):
        """Run enhanced traversal"""
        
        print(f"\n{'='*80}")
        print(f"SCA ENHANCED TRAVERSAL - COMPLETE DETAILS")
        print(f"{'='*80}\n")
        print(f"Seed: {self.seed_qid}")
        print(f"Max: {self.max_entities}")
        print(f"Shows: Hierarchy, Properties, External IDs - ALL WITH LABELS\n")
        
        # Initialize
        self.queue.append({'qid': self.seed_qid, 'depth': 0})
        
        # Process
        while self.queue and len(self.visited) < self.max_entities:
            item = self.queue.popleft()
            qid = item['qid']
            depth = item['depth']
            
            if qid in self.visited or depth > 3:
                continue
            
            try:
                # Fetch with details
                entity_data = self.fetch_with_details(qid)
                
                self.visited.add(qid)
                self.entities[qid] = entity_data
                
                # Print details
                self.print_entity_details(entity_data, len(self.visited), self.max_entities)
                
                # Add new QIDs to queue
                if depth < 3:
                    for parent in entity_data['hierarchy']['parents']:
                        if parent['qid'] not in self.visited:
                            self.queue.append({'qid': parent['qid'], 'depth': depth+1})
                    
                    for child in entity_data['hierarchy']['children']:
                        if child['qid'] not in self.visited:
                            self.queue.append({'qid': child['qid'], 'depth': depth+1})
                
                time.sleep(self.throttle)
                
            except Exception as e:
                print(f"[{len(self.visited)+1}] {qid} - FAILED: {e}\n")
        
        print(f"\n{'='*80}")
        print(f"COMPLETE: {len(self.visited)} entities")
        print(f"{'='*80}\n")
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/enhanced/{self.seed_qid}_enhanced_{timestamp}.json"
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.entities, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {output_file}\n")


if __name__ == "__main__":
    seed = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    max_ent = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    throttle = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    
    traversal = EnhancedTraversal(seed, max_ent, throttle)
    traversal.traverse()
