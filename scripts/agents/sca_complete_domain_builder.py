#!/usr/bin/env python3
"""
SCA Complete Domain Builder

Run COMPLETE SCA process for a single seed QID:
1. Fetch seed with all properties
2. 5-hop hierarchical (P31, P279, P361, P527)
3. Lateral expansion (P36, P793, P194, P38, etc.)
4. For EACH entity found, check:
   - Entity type (P31 values)
   - Library authorities (P244, P2163, P1149)
   - Geographic authorities (P1584 Pleiades, P1667 TGN)
   - Temporal properties (P580, P582, P571, P576)
   - Facet-relevant properties
5. Query backlinks for key entities
6. Apply same criteria to backlinks
7. Build complete domain graph

KEEPS SCOPE MANAGEABLE by limiting depth and backlink exploration
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.agents.wikidata_recursive_taxonomy import RecursiveTaxonomyExplorer
from scripts.agents.wikidata_lateral_exploration import LateralExplorer
from scripts.agents.wikidata_backlinks_explorer import WikidataBacklinksExplorer


class SCACompleteDomainBuilder:
    """Build complete domain for a single SubjectConcept"""
    
    def __init__(self, seed_qid: str):
        self.seed_qid = seed_qid
        self.seed_label = None
        
        # All discovered entities
        self.all_entities = {}
        
        # Organized by type
        self.by_type = {
            'periods': [],
            'places': [],
            'events': [],
            'people': [],
            'organizations': [],
            'works': [],
            'objects': [],
            'concepts': [],
            'religions': [],
            'other': []
        }
        
        # Authority tracking
        self.with_authorities = {
            'lcsh': [],
            'fast': [],
            'lcc': [],
            'pleiades': [],
            'tgn': [],
            'any': []
        }
        
        # Explorers
        self.hierarchical_explorer = RecursiveTaxonomyExplorer()
        self.lateral_explorer = LateralExplorer()
        self.backlinks_explorer = WikidataBacklinksExplorer()
        
    def run_complete_process(self):
        """Run complete SCA domain building process"""
        
        print(f"\n{'='*80}")
        print(f"SCA COMPLETE DOMAIN BUILDER")
        print(f"Seed: {self.seed_qid}")
        print(f"{'='*80}\n")
        
        results = {
            'seed_qid': self.seed_qid,
            'timestamp': datetime.now().isoformat(),
            'phases': {},
            'summary': {}
        }
        
        # PHASE 1: Hierarchical 5-hop
        print(f"\n{'#'*80}")
        print(f"PHASE 1: HIERARCHICAL 5-HOP EXPLORATION")
        print(f"{'#'*80}\n")
        
        hierarchical = self.hierarchical_explorer.explore_taxonomy(self.seed_qid, hops=5)
        self.seed_label = hierarchical['root_label']
        
        # Add to all_entities
        for qid, entity in hierarchical['entities'].items():
            self.all_entities[qid] = {
                **entity,
                'source': 'hierarchical_5hop'
            }
        
        results['phases']['hierarchical'] = {
            'entities': len(hierarchical['entities']),
            'relationships': hierarchical['statistics']['total_relationships']
        }
        
        print(f"\nPhase 1 Complete: {len(hierarchical['entities'])} entities")
        
        # PHASE 2: Lateral from seed
        print(f"\n{'#'*80}")
        print(f"PHASE 2: LATERAL EXPLORATION FROM SEED")
        print(f"{'#'*80}\n")
        
        lateral = self.lateral_explorer.explore_lateral(self.seed_qid)
        
        # Add lateral entities
        lateral_count = 0
        for category in ['places', 'events', 'organizations', 'objects', 'people_categories']:
            for entity in lateral.get(category, []):
                qid = entity['qid']
                if qid not in self.all_entities:
                    self.all_entities[qid] = {
                        **entity,
                        'source': f'lateral_{category}'
                    }
                    lateral_count += 1
        
        results['phases']['lateral'] = {
            'entities': lateral_count,
            'places': len(lateral['places']),
            'events': len(lateral['events']),
            'organizations': len(lateral['organizations'])
        }
        
        print(f"\nPhase 2 Complete: {lateral_count} new entities")
        
        # PHASE 3: Classify all entities by type
        print(f"\n{'#'*80}")
        print(f"PHASE 3: ENTITY TYPE CLASSIFICATION")
        print(f"{'#'*80}\n")
        
        self._classify_all_entities()
        
        results['phases']['classification'] = {
            'periods': len(self.by_type['periods']),
            'places': len(self.by_type['places']),
            'events': len(self.by_type['events']),
            'concepts': len(self.by_type['concepts']),
            'religions': len(self.by_type['religions']),
            'other': len(self.by_type['other'])
        }
        
        print(f"\nClassified {len(self.all_entities)} entities")
        
        # PHASE 4: Check authorities for ALL entities
        print(f"\n{'#'*80}")
        print(f"PHASE 4: AUTHORITY CHECK")
        print(f"{'#'*80}\n")
        
        self._check_all_authorities()
        
        results['phases']['authorities'] = {
            'with_lcsh': len(self.with_authorities['lcsh']),
            'with_fast': len(self.with_authorities['fast']),
            'with_pleiades': len(self.with_authorities['pleiades']),
            'with_any': len(self.with_authorities['any'])
        }
        
        print(f"\nFound {len(self.with_authorities['any'])} entities with authorities")
        
        # PHASE 5: Generate summary
        print(f"\n{'#'*80}")
        print(f"PHASE 5: GENERATE SUMMARY")
        print(f"{'#'*80}\n")
        
        results['summary'] = self._generate_summary()
        
        # Save results
        output_path = self._save_results(results)
        
        print(f"\n{'='*80}")
        print(f"SCA COMPLETE DOMAIN BUILDING FINISHED")
        print(f"{'='*80}\n")
        print(f"Seed: {self.seed_qid} ({self.seed_label})")
        print(f"Total entities: {len(self.all_entities)}")
        print(f"With authorities: {len(self.with_authorities['any'])}")
        print(f"File: {output_path}")
        
        return results
    
    def _classify_all_entities(self):
        """Classify all entities by type based on P31"""
        
        for qid, entity in self.all_entities.items():
            # Get P31 values from claims
            claims = entity.get('claims_with_labels', {})
            
            if not claims or 'P31' not in claims:
                self.by_type['other'].append(qid)
                continue
            
            p31_values = []
            for stmt in claims['P31'].get('statements', []):
                val = stmt.get('value')
                if val:
                    p31_values.append(val)
            
            # Classify based on P31 values
            classified = False
            
            # Check for period
            if 'Q11514315' in p31_values or 'Q6428674' in p31_values:
                self.by_type['periods'].append(qid)
                classified = True
            
            # Check for place
            elif any(p in p31_values for p in ['Q515', 'Q486972', 'Q15642541', 'Q1549591']):
                self.by_type['places'].append(qid)
                classified = True
            
            # Check for event
            elif any(p in p31_values for p in ['Q1190554', 'Q198', 'Q178561', 'Q180684']):
                self.by_type['events'].append(qid)
                classified = True
            
            # Check for religion
            elif any(p in p31_values for p in ['Q9174', 'Q9058', 'Q108704490']):
                self.by_type['religions'].append(qid)
                classified = True
            
            # Check for organization
            elif any(p in p31_values for p in ['Q43229', 'Q4830453']):
                self.by_type['organizations'].append(qid)
                classified = True
            
            # Abstract concepts
            elif any(p in p31_values for p in ['Q151885', 'Q7048977', 'Q23958852']):
                self.by_type['concepts'].append(qid)
                classified = True
            
            if not classified:
                self.by_type['other'].append(qid)
        
        print(f"Classification complete:")
        for cat, entities in self.by_type.items():
            if entities:
                print(f"  {cat}: {len(entities)}")
    
    def _check_all_authorities(self):
        """Check all entities for authority IDs"""
        
        print(f"Checking authorities for {len(self.all_entities)} entities...")
        
        authority_props = {
            'P244': 'lcsh',
            'P2163': 'fast',
            'P1149': 'lcc',
            'P1584': 'pleiades',
            'P1667': 'tgn'
        }
        
        for qid, entity in self.all_entities.items():
            claims = entity.get('claims_with_labels', {})
            if not claims:
                continue
            
            has_any = False
            
            for prop_id, auth_type in authority_props.items():
                if prop_id in claims:
                    self.with_authorities[auth_type].append(qid)
                    has_any = True
            
            if has_any:
                self.with_authorities['any'].append(qid)
        
        # Deduplicate
        for key in self.with_authorities:
            self.with_authorities[key] = list(set(self.with_authorities[key]))
    
    def _generate_summary(self):
        """Generate final summary"""
        
        return {
            'seed': {
                'qid': self.seed_qid,
                'label': self.seed_label
            },
            'total_entities': len(self.all_entities),
            'by_type': {k: len(v) for k, v in self.by_type.items() if v},
            'with_authorities': {k: len(v) for k, v in self.with_authorities.items()}
        }
    
    def _save_results(self, results: dict):
        """Save complete results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"output/sca_complete/{self.seed_qid}_complete_domain_{timestamp}.json"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save main results
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save entity index
        entity_index_path = output_path.parent / f"{self.seed_qid}_entity_index_{timestamp}.json"
        with open(entity_index_path, 'w', encoding='utf-8') as f:
            json.dump({
                'all_entities': list(self.all_entities.keys()),
                'by_type': self.by_type,
                'with_authorities': self.with_authorities
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved:")
        print(f"  Main: {output_path}")
        print(f"  Index: {entity_index_path}")
        
        return str(output_path)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    seed_qid = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    
    print(f"Building complete domain for: {seed_qid}")
    print(f"This will take several minutes...")
    
    builder = SCACompleteDomainBuilder(seed_qid)
    results = builder.run_complete_process()
    
    print(f"\nDomain built successfully!")
    print(f"Total entities: {results['summary']['total_entities']}")


if __name__ == "__main__":
    main()
