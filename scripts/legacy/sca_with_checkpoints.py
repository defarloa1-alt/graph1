#!/usr/bin/env python3
"""
SCA with Checkpoints - Saves every 100 entities

Can stop anytime and have partial data saved
"""

import sys
from pathlib import Path
import time
from datetime import datetime
import json
import requests
from collections import deque

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


class CheckpointTraversal:
    """Traversal with automatic checkpointing"""
    
    def __init__(self, seed_qid, max_entities=5000, throttle=1.0, checkpoint_every=100):
        self.seed_qid = seed_qid
        self.max_entities = max_entities
        self.throttle = throttle
        self.checkpoint_every = checkpoint_every
        
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        
        self.visited = set()
        self.queue = deque()
        self.entities = {}
        
        # Output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_file = f"output/checkpoints/Q{seed_qid}_checkpoint_{timestamp}.json"
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self):
        """Save current state to file"""
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'seed': self.seed_qid,
                'total': len(self.visited),
                'checkpoint_at': datetime.now().isoformat(),
                'entities': {qid: {
                    'label': data['label'],
                    'properties_count': data['properties_count'],
                    'types': data.get('types', []),
                    'federation_score': data.get('federation_score', 1),
                    'claims': data['claims']
                } for qid, data in self.entities.items()}
            }, f, indent=2, ensure_ascii=False)
    
    def fetch_entity_silent(self, qid):
        """Fetch entity (same as clean version)"""
        
        url = self.entity_url.format(qid=qid)
        response = requests.get(url, headers={'User-Agent': 'Chrystallum/1.0'})
        response.raise_for_status()
        
        data = response.json()
        entity = data.get('entities', {}).get(qid, {})
        
        label = entity.get('labels', {}).get('en', {}).get('value', qid)
        claims = entity.get('claims', {})
        props_count = len(claims)
        
        # Get types
        types = []
        if 'P31' in claims:
            for claim in claims['P31'][:3]:
                type_qid = claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
                if type_qid:
                    type_label = self._get_label(type_qid)
                    types.append(type_label)
        
        # Check temporal (same filters as before)
        # ... (add temporal filtering code)
        
        # Federation score
        fed_score = 1
        if 'P244' in claims: fed_score += 1
        if 'P2163' in claims: fed_score += 1
        if 'P1149' in claims: fed_score += 1
        if 'P1584' in claims: fed_score += 1
        if 'P1667' in claims: fed_score += 1
        
        return {
            'label': label,
            'properties_count': props_count,
            'types': types,
            'federation_score': fed_score,
            'claims': claims
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
        """Traverse with checkpoints"""
        
        print(f"SCA TRAVERSAL WITH CHECKPOINTS", flush=True)
        print(f"Saves every {self.checkpoint_every} entities to:", flush=True)
        print(f"  {self.output_file}\n", flush=True)
        
        self.queue.append({'qid': self.seed_qid, 'depth': 0})
        
        while self.queue and len(self.visited) < self.max_entities:
            item = self.queue.popleft()
            qid = item['qid']
            depth = item['depth']
            
            if qid in self.visited or depth > 3:
                continue
            
            try:
                entity = self.fetch_entity_silent(qid)
                
                if entity is None:
                    print(f"[SKIP] {qid}")
                    self.visited.add(qid)
                    continue
                
                self.visited.add(qid)
                self.entities[qid] = entity
                
                type_str = ", ".join(entity['types'][:2]) if entity['types'] else "Unknown"
                fed = entity['federation_score']
                props = entity['properties_count']
                
                # CONCISE output for speed (full data still saved to file)
                # NO TRUNCATION - show complete labels and types
                print(f"[{len(self.visited)}/{self.max_entities}] D{depth}: {qid} ({entity['label']}) T:{type_str} Fed:{fed} P:{props}", flush=True)
                
                # Extract QIDs for queue
                if depth < 3:
                    new_count = 0
                    for claims_list in entity['claims'].values():
                        if not isinstance(claims_list, list):
                            continue
                        for claim in claims_list:
                            if not isinstance(claim, dict):
                                continue
                            mainsnak = claim.get('mainsnak', {})
                            if not isinstance(mainsnak, dict):
                                continue
                            datavalue = mainsnak.get('datavalue', {})
                            if not isinstance(datavalue, dict):
                                continue
                            value = datavalue.get('value', {})
                            if isinstance(value, dict):
                                val_qid = value.get('id', '')
                            else:
                                val_qid = ''
                            
                            if val_qid and val_qid.startswith('Q') and val_qid not in self.visited:
                                self.queue.append({'qid': val_qid, 'depth': depth+1})
                                new_count += 1
                    
                    if new_count > 0:
                        print(f"  +{new_count} to queue (total: {len(self.queue)})")
                
                # CHECKPOINT every N entities
                if len(self.visited) % self.checkpoint_every == 0:
                    self.save_checkpoint()
                    print(f"  [CHECKPOINT] Saved {len(self.visited)} entities\n")
                
                time.sleep(self.throttle)
                
            except Exception as e:
                print(f"[{len(self.visited)+1}] {qid} FAILED: {e}")
        
        # Final save
        self.save_checkpoint()
        print(f"\n[FINAL] Saved {len(self.visited)} entities")
        print(f"File: {self.output_file}\n")


if __name__ == "__main__":
    seed = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    max_ent = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    throttle = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    
    traversal = CheckpointTraversal(seed, max_ent, throttle, checkpoint_every=100)
    traversal.traverse()
