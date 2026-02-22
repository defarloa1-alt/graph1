#!/usr/bin/env python3
"""
SCA Traversal - CLEAN OUTPUT WITH LABELS ALWAYS

SHOWS ONLY: [#] QID (LABEL) - properties
NO intermediate fetching messages
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


class CleanTraversal:
    """Clean traversal with labels always shown"""
    
    def __init__(self, seed_qid, max_entities=5000, max_depth=3, throttle=1.0):
        self.seed_qid = seed_qid
        self.max_entities = max_entities
        self.max_depth = max_depth
        self.throttle = throttle
        
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        
        self.visited = set()
        self.queue = deque()
        self.entities = {}
        
    def fetch_entity_silent(self, qid):
        """Fetch entity WITHOUT intermediate messages"""
        
        # Fetch entity data
        url = self.entity_url.format(qid=qid)
        response = requests.get(url, headers={'User-Agent': 'Chrystallum/1.0'})
        response.raise_for_status()
        
        data = response.json()
        entity = data.get('entities', {}).get(qid, {})
        
        # Get label
        label = entity.get('labels', {}).get('en', {}).get('value', qid)
        
        # Count properties
        claims = entity.get('claims', {})
        props_count = len(claims)
        
        # Get entity types from P31 (instance of)
        types = []
        if 'P31' in claims:
            for claim in claims['P31'][:3]:  # First 3 types
                type_qid = claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
                if type_qid:
                    # Fetch type label
                    type_label = self._get_label(type_qid)
                    types.append(type_label)
        
        # Check if this is a period
        is_period = any(t in ['Q11514315', 'Q6428674', 'Q186081'] for t in 
                       [c.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '') 
                        for c in claims.get('P31', [])])
        
        # Check temporal bounds - IGNORE if ends before -2000 OR if period with no end
        end_date = None
        if 'P582' in claims:  # end time
            time_val = claims['P582'][0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time', '')
            if time_val:
                # Extract year from "+YYYY-MM-DD" or "-YYYY-MM-DD" format
                year_str = time_val[1:5] if len(time_val) > 5 else None
                if year_str and time_val.startswith('-'):
                    end_date = -int(year_str)
                elif year_str:
                    end_date = int(year_str)
        
        elif 'P576' in claims:  # dissolved
            time_val = claims['P576'][0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time', '')
            if time_val:
                year_str = time_val[1:5] if len(time_val) > 5 else None
                if year_str and time_val.startswith('-'):
                    end_date = -int(year_str)
                elif year_str:
                    end_date = int(year_str)
        
        # Filter 1: Skip if ends before -2000
        if end_date and end_date < -2000:
            return None  # SKIP - outside Year backbone (-2000 to 2025)
        
        # Filter 2: Skip periods with NO end date (can't tether)
        if is_period and end_date is None:
            return None  # SKIP - period must have end date for Year backbone
        
        # Calculate federation score
        fed_score = 1  # Wikidata always
        if 'P244' in claims: fed_score += 1  # LCSH
        if 'P2163' in claims: fed_score += 1  # FAST
        if 'P1149' in claims: fed_score += 1  # LCC
        if 'P1584' in claims: fed_score += 1  # Pleiades
        if 'P1667' in claims: fed_score += 1  # TGN
        
        return {
            'label': label,
            'properties_count': props_count,
            'types': types,
            'claims': claims,
            'end_date': end_date,
            'federation_score': fed_score
        }
    
    def _get_label(self, qid):
        """Quick label fetch"""
        try:
            params = {'action': 'wbgetentities', 'ids': qid, 'props': 'labels', 'languages': 'en', 'format': 'json'}
            resp = requests.get(self.api_url, params=params, headers={'User-Agent': 'Chrystallum/1.0'})
            data = resp.json()
            return data.get('entities', {}).get(qid, {}).get('labels', {}).get('en', {}).get('value', qid)
        except:
            return qid
    
    def traverse(self):
        """Run clean traversal"""
        
        print(f"{'='*80}")
        print(f"SCA TRAVERSAL - QID (LABEL) FORMAT")
        print(f"{'='*80}\n")
        print(f"Seed: {self.seed_qid}")
        print(f"Max: {self.max_entities} entities")
        print(f"Depth: {self.max_depth} hops")
        print(f"Throttle: {self.throttle}s\n")
        
        # Initialize
        self.queue.append({'qid': self.seed_qid, 'depth': 0})
        
        # Process
        while self.queue and len(self.visited) < self.max_entities:
            item = self.queue.popleft()
            qid = item['qid']
            depth = item['depth']
            
            if qid in self.visited or depth > self.max_depth:
                continue
            
            try:
                # Fetch (silent - no intermediate output)
                entity = self.fetch_entity_silent(qid)
                
                # Skip if None (filtered out - ends before -2000)
                if entity is None:
                    print(f"[SKIP] {qid} - ends before -2000 BC (outside Year backbone)")
                    self.visited.add(qid)  # Mark as visited so we don't retry
                    continue
                
                self.visited.add(qid)
                self.entities[qid] = entity
                
                # SHOW with QID (LABEL), TYPE, and Federation Score
                type_str = ", ".join(entity['types'][:2]) if entity['types'] else "Unknown"
                fed_score = entity.get('federation_score', 1)
                props_count = entity['properties_count']
                
                print(f"\n[{len(self.visited)}/{self.max_entities}] Depth {depth}")
                print(f"  QID: {qid}")
                print(f"  Label: {entity['label']}")
                print(f"  TYPE: {type_str}")
                print(f"  Federation Score: {fed_score}")
                print(f"  PROPERTIES ({props_count}):")
                
                # List ALL properties with values
                for prop_id in entity['claims'].keys():
                    prop_label = self._get_label(prop_id)
                    
                    # Get values
                    values = []
                    for claim in entity['claims'][prop_id][:3]:  # First 3 values per property
                        datavalue = claim.get('mainsnak', {}).get('datavalue', {})
                        
                        if datavalue.get('type') == 'wikibase-entityid':
                            val_qid = datavalue.get('value', {}).get('id', '')
                            val_label = self._get_label(val_qid)
                            values.append(f"{val_qid} ({val_label})")
                        elif datavalue.get('type') == 'time':
                            time_val = datavalue.get('value', {}).get('time', '')
                            values.append(time_val)
                        elif datavalue.get('type') == 'string':
                            str_val = datavalue.get('value', '')
                            values.append(str_val)
                        elif datavalue.get('type') == 'quantity':
                            qty_val = datavalue.get('value', {}).get('amount', '')
                            values.append(qty_val)
                        elif datavalue.get('type') == 'globecoordinate':
                            coord = datavalue.get('value', {})
                            values.append(f"{coord.get('latitude', '')}, {coord.get('longitude', '')}")
                        else:
                            values.append(str(datavalue.get('value', '')))
                    
                    # Show property with values
                    values_str = " | ".join(values)
                    if len(entity['claims'][prop_id]) > 3:
                        values_str += f" ... (+{len(entity['claims'][prop_id])-3} more)"
                    
                    print(f"    {prop_id} ({prop_label}): {values_str}")
                
                print()
                
                # Extract QIDs for next hop
                if depth < self.max_depth:
                    new_count = 0
                    for prop_claims in entity['claims'].values():
                        for claim in prop_claims:
                            datavalue = claim.get('mainsnak', {}).get('datavalue', {})
                            if datavalue.get('type') == 'wikibase-entityid':
                                val_qid = datavalue.get('value', {}).get('id', '')
                                if val_qid and val_qid not in self.visited:
                                    self.queue.append({'qid': val_qid, 'depth': depth+1})
                                    new_count += 1
                    
                    if new_count > 0:
                        print(f"     -> +{new_count} to queue (total: {len(self.queue)})")
                
                time.sleep(self.throttle)
                
            except Exception as e:
                print(f"[{len(self.visited)+1}] {qid} - FAILED: {e}")
        
        print(f"\n{'='*80}")
        print(f"COMPLETE: {len(self.visited)} entities")
        print(f"{'='*80}\n")
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/traversal/{self.seed_qid}_clean_{timestamp}.json"
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'seed': self.seed_qid,
                'total': len(self.visited),
                'entities': {qid: {
                    'label': data['label'],
                    'properties_count': data['properties_count'],
                    'types': data.get('types', []),
                    'federation_score': data.get('federation_score', 1),
                    'end_date': data.get('end_date'),
                    'claims': data['claims']  # SAVE COMPLETE CLAIMS!
                } for qid, data in self.entities.items()}
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {output_file}\n")
        
        return output_file


if __name__ == "__main__":
    seed = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    max_ent = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    throttle = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    
    traversal = CleanTraversal(seed, max_ent, throttle=throttle)
    traversal.traverse()
