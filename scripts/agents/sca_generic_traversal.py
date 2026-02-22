#!/usr/bin/env python3
"""
SCA Generic Graph Traversal Algorithm

INPUT: Single QID
OUTPUT: Complete network of ALL connected entities

ALGORITHM:
1. Start with seed QID
2. Fetch ALL properties and values
3. For EVERY property value that is a QID:
   - Add to exploration queue
   - Mark relationship (property + direction)
4. Fetch each queued entity
5. Repeat step 2-3 for each
6. Continue until depth limit OR entity count limit
7. Return thousands of entities with all relationships

NO HARDCODING except:
- Entity type definitions (Q11514315 = historical period) - Wikidata's schema
- Authority properties (P244 = LCSH) - Wikidata's schema  
- Stopping conditions (max depth, max entities)

EVERYTHING ELSE IS DISCOVERED
"""

import sys
from pathlib import Path
import time
from datetime import datetime
import json
from collections import deque

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.agents.wikidata_full_fetch_enhanced import WikidataEnhancedFetcher


class GenericGraphTraversal:
    """Generic algorithm to traverse complete Wikidata graph from seed"""
    
    def __init__(self, 
                 seed_qid: str,
                 max_depth: int = 3,
                 max_entities: int = 5000,
                 throttle: float = 1.0):
        """
        Initialize traversal
        
        Args:
            seed_qid: Starting QID
            max_depth: Maximum hops from seed (default 3)
            max_entities: Stop after N entities (default 1000)
            throttle: Seconds between requests (default 1.0)
        """
        self.seed_qid = seed_qid
        self.max_depth = max_depth
        self.max_entities = max_entities
        self.throttle = throttle
        
        # Fetcher
        self.fetcher = WikidataEnhancedFetcher()
        
        # Tracking
        self.visited = set()  # QIDs we've fetched
        self.queue = deque()  # QIDs to fetch
        self.entities = {}    # QID -> complete data
        self.relationships = []  # All edges
        
        # Statistics
        self.stats = {
            'total_fetched': 0,
            'total_qids_found': 0,
            'by_depth': {},
            'start_time': None,
            'end_time': None
        }
    
    def traverse(self):
        """Run complete traversal"""
        
        print(f"\n{'='*80}")
        print(f"GENERIC GRAPH TRAVERSAL")
        print(f"{'='*80}\n")
        print(f"Seed: {self.seed_qid}")
        print(f"Max depth: {self.max_depth}")
        print(f"Max entities: {self.max_entities}")
        print(f"Throttle: {self.throttle}s\n")
        
        self.stats['start_time'] = datetime.now().isoformat()
        
        # Initialize with seed
        self.queue.append({
            'qid': self.seed_qid,
            'depth': 0,
            'from_qid': None,
            'via_property': 'seed'
        })
        
        # Process queue
        while self.queue and len(self.visited) < self.max_entities:
            # Get next entity
            item = self.queue.popleft()
            qid = item['qid']
            depth = item['depth']
            
            # Skip if already visited
            if qid in self.visited:
                continue
            
            # Skip if beyond depth limit
            if depth > self.max_depth:
                continue
            
            # Fetch and process
            print(f"[{len(self.visited)+1}/{self.max_entities}] Depth {depth}: {qid}... ", end="", flush=True)
            
            try:
                # Fetch entity
                entity_data = self.fetcher.fetch_entity_with_labels(qid)
                
                # Mark as visited
                self.visited.add(qid)
                self.entities[qid] = {
                    'depth': depth,
                    'from': item['from_qid'],
                    'via': item['via_property'],
                    'data': entity_data
                }
                
                self.stats['total_fetched'] += 1
                self.stats['by_depth'][depth] = self.stats['by_depth'].get(depth, 0) + 1
                
                label = entity_data.get('labels', {}).get('en', qid)
                props = entity_data.get('statistics', {}).get('total_properties', 0)
                
                # Show QID (Label) on SAME line
                print(f"({label}) - {props} props")
                
                # Record relationship
                if item['from_qid']:
                    self.relationships.append({
                        'from': item['from_qid'],
                        'to': qid,
                        'property': item['via_property'],
                        'depth': depth
                    })
                
                # Extract ALL QID values and add to queue (if depth allows)
                if depth < self.max_depth:
                    new_qids = self._extract_all_qids(entity_data, qid, depth)
                    
                    self.stats['total_qids_found'] += len(new_qids)
                    
                    if new_qids:
                        print(f"  -> Found {len(new_qids)} more QIDs to explore")
                
                # Throttle
                time.sleep(self.throttle)
                
            except Exception as e:
                print(f"FAILED: {e}")
        
        self.stats['end_time'] = datetime.now().isoformat()
        
        # Final summary
        self._print_summary()
        
        # Save results
        output_path = self._save_results()
        
        return output_path
    
    def _extract_all_qids(self, entity_data: dict, from_qid: str, current_depth: int) -> list:
        """Extract ALL QID values from entity for exploration"""
        
        claims = entity_data.get('claims_with_labels', {})
        new_qids = []
        
        # Go through EVERY property
        for prop_id, prop_data in claims.items():
            statements = prop_data.get('statements', [])
            
            for stmt in statements:
                value = stmt.get('value')
                
                # If value is a QID, add to queue
                if isinstance(value, str) and value.startswith('Q') and value not in self.visited:
                    
                    # Add to queue
                    self.queue.append({
                        'qid': value,
                        'depth': current_depth + 1,
                        'from_qid': from_qid,
                        'via_property': prop_id
                    })
                    
                    new_qids.append(value)
        
        return new_qids
    
    def _print_summary(self):
        """Print traversal summary"""
        
        print(f"\n{'='*80}")
        print(f"TRAVERSAL COMPLETE")
        print(f"{'='*80}\n")
        
        print(f"Entities fetched: {self.stats['total_fetched']}")
        print(f"Relationships: {len(self.relationships)}")
        print(f"QIDs discovered: {self.stats['total_qids_found']}")
        print(f"Queue remaining: {len(self.queue)} (not fetched due to limits)\n")
        
        print(f"By depth:")
        for depth in sorted(self.stats['by_depth'].keys()):
            count = self.stats['by_depth'][depth]
            print(f"  Depth {depth}: {count} entities")
        
        print()
    
    def _save_results(self) -> str:
        """Save complete results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/traversal/{self.seed_qid}_traversal_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            'seed_qid': self.seed_qid,
            'parameters': {
                'max_depth': self.max_depth,
                'max_entities': self.max_entities,
                'throttle': self.throttle
            },
            'statistics': self.stats,
            'entities': {qid: {
                'depth': data['depth'],
                'from': data['from'],
                'via': data['via'],
                'label': data['data'].get('labels', {}).get('en', qid),
                'properties_count': data['data'].get('statistics', {}).get('total_properties', 0)
            } for qid, data in self.entities.items()},
            'relationships': self.relationships
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {output_path}\n")
        
        return str(output_path)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    seed = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    max_entities = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    throttle = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    
    print(f"Starting generic traversal...")
    print(f"  Seed: {seed}")
    print(f"  Max depth: {max_depth}")
    print(f"  Max entities: {max_entities}")
    print(f"  Throttle: {throttle}s\n")
    
    traversal = GenericGraphTraversal(seed, max_depth, max_entities, throttle)
    output_path = traversal.traverse()
    
    print(f"Complete! Results in: {output_path}")


if __name__ == "__main__":
    main()
