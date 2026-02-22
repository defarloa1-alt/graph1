#!/usr/bin/env python3
"""
Wikidata Recursive Taxonomy Explorer

Fetches taxonomy 2 hops up and down from a starting QID:

UP (Parents):
  Starting QID → Parents (P31, P361) → Grandparents

DOWN (Children):
  Starting QID → Children (P527) → Grandchildren

For EACH entity found, fetches:
- QID
- Label
- Description
- ALL properties
- ALL values with labels
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.agents.wikidata_full_fetch_enhanced import WikidataEnhancedFetcher
import json
from datetime import datetime
from typing import Dict, List, Set


class RecursiveTaxonomyExplorer:
    """Explore taxonomy recursively with 2 hops up and down"""
    
    def __init__(self):
        self.fetcher = WikidataEnhancedFetcher()
        self.cache = {}  # Cache fetched entities to avoid duplicates
        
    def explore_taxonomy(self, root_qid: str, hops: int = 2) -> Dict:
        """
        Explore taxonomy N hops up and down
        
        Args:
            root_qid: Starting QID
            hops: Number of hops (default 2)
        
        Returns:
            Complete taxonomy with all entities and relationships
        """
        print(f"\n{'='*80}")
        print(f"RECURSIVE TAXONOMY EXPLORATION: {root_qid}")
        print(f"Hops: {hops} up and {hops} down")
        print(f"{'='*80}\n")
        
        taxonomy = {
            'root_qid': root_qid,
            'hops': hops,
            'timestamp': datetime.now().isoformat(),
            'entities': {},
            'relationships': {
                'upward': [],    # Parents, grandparents
                'downward': [],  # Children, grandchildren
                'succession': [] # Follows, followed by
            },
            'statistics': {}
        }
        
        # Fetch root entity
        print(f"[ROOT] Fetching root entity: {root_qid}")
        root_data = self._fetch_and_cache(root_qid)
        
        if not root_data:
            raise ValueError(f"Failed to fetch root QID: {root_qid}")
        
        taxonomy['root_label'] = root_data['labels'].get('en', root_qid)
        
        # Explore UPWARD (parents, grandparents)
        print(f"\n{'='*80}")
        print(f"EXPLORING UPWARD (Parents & Grandparents)")
        print(f"{'='*80}\n")
        self._explore_upward(root_qid, taxonomy, current_hop=0, max_hops=hops)
        
        # Explore DOWNWARD (children, grandchildren)
        print(f"\n{'='*80}")
        print(f"EXPLORING DOWNWARD (Children & Grandchildren)")
        print(f"{'='*80}\n")
        self._explore_downward(root_qid, taxonomy, current_hop=0, max_hops=hops)
        
        # Explore SUCCESSION (follows, followed by)
        print(f"\n{'='*80}")
        print(f"EXPLORING SUCCESSION (Timeline)")
        print(f"{'='*80}\n")
        self._explore_succession(root_qid, taxonomy)
        
        # Add all cached entities to taxonomy
        taxonomy['entities'] = self.cache
        
        # Calculate statistics
        taxonomy['statistics'] = self._calculate_statistics(taxonomy)
        
        return taxonomy
    
    def _fetch_and_cache(self, qid: str) -> Dict:
        """Fetch entity and cache it"""
        
        if qid in self.cache:
            print(f"  [CACHED] {qid}")
            return self.cache[qid]
        
        try:
            print(f"  [FETCH] {qid}...", end=" ")
            data = self.fetcher.fetch_entity_with_labels(qid)
            
            # Simplify for storage
            simplified = {
                'qid': qid,
                'label': data.get('labels', {}).get('en', qid),
                'description': data.get('descriptions', {}).get('en', ''),
                'labels': data.get('labels', {}),
                'descriptions': data.get('descriptions', {}),
                'claims_with_labels': data.get('claims_with_labels', {}),
                'statistics': data.get('statistics', {})
            }
            
            self.cache[qid] = simplified
            print(f"OK - {simplified['label']}")
            return simplified
            
        except Exception as e:
            print(f"FAILED - {e}")
            return None
    
    def _explore_upward(self, qid: str, taxonomy: Dict, current_hop: int, max_hops: int):
        """Explore upward (parents, grandparents)"""
        
        if current_hop >= max_hops:
            return
        
        entity = self.cache.get(qid)
        if not entity:
            entity = self._fetch_and_cache(qid)
        
        if not entity:
            return
        
        # Get parent relationships
        parents = []
        claims = entity.get('claims_with_labels', {})
        
        # P31 (instance of)
        if 'P31' in claims:
            for stmt in claims['P31']['statements']:
                parent_qid = stmt.get('value')
                if isinstance(parent_qid, str) and parent_qid.startswith('Q'):
                    parents.append({
                        'property': 'P31',
                        'property_label': 'instance of',
                        'parent_qid': parent_qid,
                        'parent_label': stmt.get('value_label', parent_qid)
                    })
        
        # P361 (part of)
        if 'P361' in claims:
            for stmt in claims['P361']['statements']:
                parent_qid = stmt.get('value')
                if isinstance(parent_qid, str) and parent_qid.startswith('Q'):
                    parents.append({
                        'property': 'P361',
                        'property_label': 'part of',
                        'parent_qid': parent_qid,
                        'parent_label': stmt.get('value_label', parent_qid)
                    })
        
        # P279 (subclass of)
        if 'P279' in claims:
            for stmt in claims['P279']['statements']:
                parent_qid = stmt.get('value')
                if isinstance(parent_qid, str) and parent_qid.startswith('Q'):
                    parents.append({
                        'property': 'P279',
                        'property_label': 'subclass of',
                        'parent_qid': parent_qid,
                        'parent_label': stmt.get('value_label', parent_qid)
                    })
        
        # Record relationships
        for parent in parents:
            taxonomy['relationships']['upward'].append({
                'from_qid': qid,
                'from_label': entity['label'],
                'to_qid': parent['parent_qid'],
                'to_label': parent['parent_label'],
                'property': parent['property'],
                'property_label': parent['property_label'],
                'hop': current_hop + 1
            })
        
        # Recursively explore parents
        print(f"\n[HOP {current_hop + 1} UP] Found {len(parents)} parents for {qid} ({entity['label']})")
        for parent in parents:
            parent_qid = parent['parent_qid']
            print(f"  -> {parent['property_label']}: {parent_qid} ({parent['parent_label']})")
            
            # Fetch parent and explore its parents
            self._explore_upward(parent_qid, taxonomy, current_hop + 1, max_hops)
    
    def _explore_downward(self, qid: str, taxonomy: Dict, current_hop: int, max_hops: int):
        """Explore downward (children, grandchildren)"""
        
        if current_hop >= max_hops:
            return
        
        entity = self.cache.get(qid)
        if not entity:
            entity = self._fetch_and_cache(qid)
        
        if not entity:
            return
        
        # Get child relationships
        children = []
        claims = entity.get('claims_with_labels', {})
        
        # P527 (has parts)
        if 'P527' in claims:
            for stmt in claims['P527']['statements']:
                child_qid = stmt.get('value')
                if isinstance(child_qid, str) and child_qid.startswith('Q'):
                    children.append({
                        'property': 'P527',
                        'property_label': 'has parts',
                        'child_qid': child_qid,
                        'child_label': stmt.get('value_label', child_qid)
                    })
        
        # P150 (contains)
        if 'P150' in claims:
            for stmt in claims['P150']['statements']:
                child_qid = stmt.get('value')
                if isinstance(child_qid, str) and child_qid.startswith('Q'):
                    children.append({
                        'property': 'P150',
                        'property_label': 'contains',
                        'child_qid': child_qid,
                        'child_label': stmt.get('value_label', child_qid)
                    })
        
        # Record relationships
        for child in children:
            taxonomy['relationships']['downward'].append({
                'from_qid': qid,
                'from_label': entity['label'],
                'to_qid': child['child_qid'],
                'to_label': child['child_label'],
                'property': child['property'],
                'property_label': child['property_label'],
                'hop': current_hop + 1
            })
        
        # Recursively explore children
        print(f"\n[HOP {current_hop + 1} DOWN] Found {len(children)} children for {qid} ({entity['label']})")
        for child in children:
            child_qid = child['child_qid']
            print(f"  -> {child['property_label']}: {child_qid} ({child['child_label']})")
            
            # Fetch child and explore its children
            self._explore_downward(child_qid, taxonomy, current_hop + 1, max_hops)
    
    def _explore_succession(self, qid: str, taxonomy: Dict):
        """Explore succession (follows, followed by)"""
        
        entity = self.cache.get(qid)
        if not entity:
            entity = self._fetch_and_cache(qid)
        
        if not entity:
            return
        
        claims = entity.get('claims_with_labels', {})
        
        # P155 (follows)
        if 'P155' in claims:
            for stmt in claims['P155']['statements']:
                predecessor_qid = stmt.get('value')
                if isinstance(predecessor_qid, str) and predecessor_qid.startswith('Q'):
                    taxonomy['relationships']['succession'].append({
                        'from_qid': predecessor_qid,
                        'from_label': stmt.get('value_label', predecessor_qid),
                        'to_qid': qid,
                        'to_label': entity['label'],
                        'property': 'P155',
                        'property_label': 'follows',
                        'direction': 'predecessor'
                    })
                    # Fetch predecessor
                    self._fetch_and_cache(predecessor_qid)
        
        # P156 (followed by)
        if 'P156' in claims:
            for stmt in claims['P156']['statements']:
                successor_qid = stmt.get('value')
                if isinstance(successor_qid, str) and successor_qid.startswith('Q'):
                    taxonomy['relationships']['succession'].append({
                        'from_qid': qid,
                        'from_label': entity['label'],
                        'to_qid': successor_qid,
                        'to_label': stmt.get('value_label', successor_qid),
                        'property': 'P156',
                        'property_label': 'followed by',
                        'direction': 'successor'
                    })
                    # Fetch successor
                    self._fetch_and_cache(successor_qid)
    
    def _calculate_statistics(self, taxonomy: Dict) -> Dict:
        """Calculate statistics"""
        
        return {
            'total_entities_fetched': len(taxonomy['entities']),
            'upward_relationships': len(taxonomy['relationships']['upward']),
            'downward_relationships': len(taxonomy['relationships']['downward']),
            'succession_relationships': len(taxonomy['relationships']['succession']),
            'total_relationships': (
                len(taxonomy['relationships']['upward']) +
                len(taxonomy['relationships']['downward']) +
                len(taxonomy['relationships']['succession'])
            ),
            'entities_by_hop': self._count_by_hop(taxonomy)
        }
    
    def _count_by_hop(self, taxonomy: Dict) -> Dict:
        """Count entities by hop distance"""
        
        hop_counts = {
            'root': 1,
            'hop_1_up': 0,
            'hop_2_up': 0,
            'hop_1_down': 0,
            'hop_2_down': 0,
            'succession': 0
        }
        
        # Count upward
        for rel in taxonomy['relationships']['upward']:
            if rel['hop'] == 1:
                hop_counts['hop_1_up'] += 1
            elif rel['hop'] == 2:
                hop_counts['hop_2_up'] += 1
        
        # Count downward
        for rel in taxonomy['relationships']['downward']:
            if rel['hop'] == 1:
                hop_counts['hop_1_down'] += 1
            elif rel['hop'] == 2:
                hop_counts['hop_2_down'] += 1
        
        # Count succession
        hop_counts['succession'] = len(taxonomy['relationships']['succession'])
        
        return hop_counts
    
    def print_summary(self, taxonomy: Dict):
        """Print taxonomy summary"""
        
        stats = taxonomy['statistics']
        
        print(f"\n{'='*80}")
        print(f"TAXONOMY EXPLORATION COMPLETE")
        print(f"{'='*80}\n")
        
        print(f"ROOT: {taxonomy['root_qid']} ({taxonomy['root_label']})")
        print(f"HOPS: {taxonomy['hops']} up and down\n")
        
        print(f"STATISTICS:")
        print(f"  Total entities fetched: {stats['total_entities_fetched']}")
        print(f"  Total relationships: {stats['total_relationships']}")
        print(f"    - Upward: {stats['upward_relationships']}")
        print(f"    - Downward: {stats['downward_relationships']}")
        print(f"    - Succession: {stats['succession_relationships']}")
        
        print(f"\nENTITIES BY HOP:")
        hop_counts = stats['entities_by_hop']
        print(f"  Root: {hop_counts['root']}")
        print(f"  Hop 1 Up (Parents): {hop_counts['hop_1_up']}")
        print(f"  Hop 2 Up (Grandparents): {hop_counts['hop_2_up']}")
        print(f"  Hop 1 Down (Children): {hop_counts['hop_1_down']}")
        print(f"  Hop 2 Down (Grandchildren): {hop_counts['hop_2_down']}")
        print(f"  Succession: {hop_counts['succession']}")
        
        # Print all entities found
        print(f"\n{'='*80}")
        print(f"ALL ENTITIES FETCHED ({len(taxonomy['entities'])})")
        print(f"{'='*80}\n")
        
        for qid, entity in sorted(taxonomy['entities'].items()):
            label = entity['label']
            desc = entity['description'][:60] if entity['description'] else 'No description'
            props = entity['statistics'].get('total_properties', 0)
            print(f"{qid:<12} {label:<35} ({props} props)")
            print(f"             {desc}")
            print()
        
        print(f"{'='*80}\n")
    
    def save_taxonomy(self, taxonomy: Dict, filename: str = None):
        """Save taxonomy to JSON"""
        
        if not filename:
            qid = taxonomy['root_qid']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"output/taxonomy_recursive/{qid}_recursive_{timestamp}.json"
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(taxonomy, f, indent=2, ensure_ascii=False)
        
        print(f"SAVED: {filename}\n")
        
        return filename


# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_recursive_taxonomy(qid: str, hops: int = 2):
    """Test recursive taxonomy exploration"""
    
    explorer = RecursiveTaxonomyExplorer()
    
    try:
        # Explore taxonomy
        taxonomy = explorer.explore_taxonomy(qid, hops=hops)
        
        # Print summary
        explorer.print_summary(taxonomy)
        
        # Save to JSON
        explorer.save_taxonomy(taxonomy)
        
        return taxonomy
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    qid = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    hops = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    print(f"Exploring recursive taxonomy for: {qid} ({hops} hops)")
    
    test_recursive_taxonomy(qid, hops)
