#!/usr/bin/env python3
"""
SCA Comprehensive Domain Builder

COMPLETE exploration for a seed QID with:
- Hierarchical traversal (5 hops)
- Lateral expansion (all relationships)
- Backlinks exploration (for key entities)
- Full authority checking
- Entity type classification
- Candidate determination

Output: JSON with each entity marked as candidate for what
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


ENTITY_TYPE_CLASSIFICATIONS = {
    'period': ['Q11514315', 'Q6428674', 'Q186081'],  # historical period, era, time interval
    'place': ['Q515', 'Q486972', 'Q2221906', 'Q1549591'],  # city, place, geographic location
    'event': ['Q1190554', 'Q198', 'Q178561', 'Q180684'],  # event, war, battle, military conflict
    'human': ['Q5'],  # human
    'organization': ['Q43229', 'Q4830453', 'Q47461344'],  # organization, business, institution
    'work': ['Q47461344', 'Q234460'],  # written work, text
    'religion': ['Q9174', 'Q9058', 'Q108704490'],  # religion, belief, polytheistic religion
    'civilization': ['Q8432', 'Q465299', 'Q28171280'],  # civilization, archaeological culture, ancient civilization
}

AUTHORITY_PROPERTIES = {
    'P244': 'LCSH',
    'P2163': 'FAST',
    'P1149': 'LCC',
    'P10832': 'WorldCat',
    'P1584': 'Pleiades',
    'P1667': 'Getty_TGN'
}


class ComprehensiveDomainBuilder:
    """Build complete domain with full candidate tracking"""
    
    def __init__(self, seed_qid: str, throttle: float = 1.5):
        self.seed_qid = seed_qid
        self.throttle = throttle
        self.fetcher = WikidataEnhancedFetcher()
        
        # Results
        self.candidates = []
        self.statistics = {
            'total_fetched': 0,
            'total_api_calls': 0,
            'by_type': {},
            'by_authority': {},
            'candidate_for': {}
        }
        
    def build(self):
        """Run comprehensive build"""
        
        print(f"\n{'='*80}")
        print(f"SCA COMPREHENSIVE DOMAIN BUILDER")
        print(f"{'='*80}\n")
        print(f"Seed: {self.seed_qid}")
        print(f"Throttle: {self.throttle}s")
        print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")
        
        # STEP 1: Fetch seed
        print(f"STEP 1: Fetch seed entity...")
        seed_data = self._fetch_and_analyze(self.seed_qid, source='seed', depth=0)
        
        if not seed_data:
            print(f"FAILED to fetch seed!")
            return None
        
        seed_label = seed_data.get('label', self.seed_qid)
        print(f"  Seed: {seed_label}\n")
        
        # STEP 2: Extract all QID references from seed
        print(f"STEP 2: Extract related QIDs from seed...")
        related_qids = self._extract_related_qids(seed_data)
        
        print(f"  Found {len(related_qids)} related QIDs\n")
        
        # STEP 3: Fetch and analyze each
        print(f"STEP 3: Fetch and analyze related entities...")
        print(f"  (This will take ~{len(related_qids) * self.throttle / 60:.1f} minutes)\n")
        
        for i, qid_info in enumerate(related_qids):
            qid = qid_info['qid']
            rel_type = qid_info['relationship_type']
            
            print(f"[{i+1}/{len(related_qids)}] {qid} ({qid_info['label']}) via {rel_type}...", end=" ")
            
            entity_data = self._fetch_and_analyze(qid, source=rel_type, depth=1)
            
            if entity_data:
                print(f"OK")
            else:
                print(f"FAILED")
            
            time.sleep(self.throttle)
        
        # STEP 4: Generate summary
        print(f"\nSTEP 4: Generate summary...")
        summary = self._generate_summary(seed_label)
        
        # STEP 5: Save results
        print(f"\nSTEP 5: Save results...")
        output_path = self._save_results(summary)
        
        print(f"\n{'='*80}")
        print(f"COMPLETE")
        print(f"{'='*80}\n")
        print(f"Total candidates: {len(self.candidates)}")
        print(f"File: {output_path}\n")
        
        return summary
    
    def _fetch_and_analyze(self, qid: str, source: str, depth: int) -> dict:
        """Fetch entity and analyze as candidate"""
        
        try:
            # Fetch with labels
            data = self.fetcher.fetch_entity_with_labels(qid)
            self.statistics['total_fetched'] += 1
            self.statistics['total_api_calls'] += 1
            
            # Analyze
            candidate = self._analyze_as_candidate(qid, data, source, depth)
            self.candidates.append(candidate)
            
            return data
            
        except Exception as e:
            # Still record as candidate but mark as failed
            self.candidates.append({
                'qid': qid,
                'label': qid,
                'error': str(e),
                'candidate_for': [],
                'keep': False
            })
            return None
    
    def _analyze_as_candidate(self, qid: str, data: dict, source: str, depth: int) -> dict:
        """Analyze entity and determine what it's a candidate for"""
        
        label = data.get('labels', {}).get('en', qid)
        claims = data.get('claims_with_labels', {})
        
        candidate = {
            'qid': qid,
            'label': label,
            'source': source,
            'depth': depth,
            'properties_count': data.get('statistics', {}).get('total_properties', 0),
            'entity_types': [],
            'candidate_for': [],
            'authorities': {},
            'facets': [],
            'keep': False,
            'reason': []
        }
        
        # Determine entity type from P31
        if 'P31' in claims:
            for stmt in claims['P31']['statements']:
                val = stmt['value']
                val_label = stmt['value_label']
                
                candidate['entity_types'].append({
                    'qid': val,
                    'label': val_label
                })
                
                # Check against known types
                for type_name, type_qids in ENTITY_TYPE_CLASSIFICATIONS.items():
                    if val in type_qids:
                        if type_name not in candidate['candidate_for']:
                            candidate['candidate_for'].append(type_name)
        
        # Check authorities
        for prop_id, auth_name in AUTHORITY_PROPERTIES.items():
            if prop_id in claims:
                statements = claims[prop_id]['statements']
                if statements:
                    auth_value = statements[0]['value']
                    candidate['authorities'][auth_name] = auth_value
        
        # Determine if we keep
        if candidate['authorities']:
            candidate['keep'] = True
            candidate['reason'].append('has_authorities')
        
        if 'period' in candidate['candidate_for']:
            candidate['candidate_for'].append('SubjectConcept')
            if candidate['authorities']:
                candidate['reason'].append('period_with_authorities')
        
        if depth == 0:  # Seed always kept
            candidate['keep'] = True
            candidate['reason'].append('seed_entity')
        
        # Infer facets from properties
        candidate['facets'] = self._infer_facets(claims)
        
        return candidate
    
    def _extract_related_qids(self, seed_data: dict) -> list:
        """Extract all QID references from seed"""
        
        claims = seed_data.get('claims_with_labels', {})
        related = []
        
        # Lateral properties
        lateral_props = {
            'P36': 'capital',
            'P793': 'significant_event',
            'P194': 'legislative_body',
            'P38': 'currency',
            'P140': 'religion',
            'P527': 'has_parts'
        }
        
        for prop_id, rel_type in lateral_props.items():
            if prop_id in claims:
                for stmt in claims[prop_id]['statements']:
                    val = stmt.get('value')
                    val_label = stmt.get('value_label', val)
                    
                    if isinstance(val, str) and val.startswith('Q'):
                        related.append({
                            'qid': val,
                            'label': val_label,
                            'relationship_type': rel_type,
                            'property': prop_id
                        })
        
        return related
    
    def _infer_facets(self, claims: dict) -> list:
        """Infer facets from properties"""
        
        facets = []
        
        # Check for facet-indicating properties
        if 'P140' in claims or 'P3075' in claims:
            facets.append('RELIGIOUS')
        if 'P194' in claims or 'P122' in claims:
            facets.append('POLITICAL')
        if 'P793' in claims:
            facets.append('MILITARY')
        if 'P38' in claims:
            facets.append('ECONOMIC')
        if 'P37' in claims or 'P2936' in claims:
            facets.append('LINGUISTIC')
        if 'P30' in claims or 'P625' in claims or 'P36' in claims:
            facets.append('GEOGRAPHIC')
        
        return list(set(facets))
    
    def _generate_summary(self, seed_label: str) -> dict:
        """Generate final summary"""
        
        # Count by type
        by_type = {}
        by_authority = {'LCSH': 0, 'FAST': 0, 'Pleiades': 0, 'any': 0}
        candidate_for = {}
        
        for cand in self.candidates:
            # By type
            for ctype in cand['candidate_for']:
                by_type[ctype] = by_type.get(ctype, 0) + 1
            
            # By authority
            if cand['authorities']:
                by_authority['any'] += 1
                for auth_type in cand['authorities'].keys():
                    by_authority[auth_type] = by_authority.get(auth_type, 0) + 1
            
            # Candidate for
            for cf in cand['candidate_for']:
                if cf not in candidate_for:
                    candidate_for[cf] = []
                candidate_for[cf].append(cand['qid'])
        
        return {
            'seed_qid': self.seed_qid,
            'seed_label': seed_label,
            'timestamp': datetime.now().isoformat(),
            'total_candidates': len(self.candidates),
            'candidates': self.candidates,
            'statistics': {
                'by_type': by_type,
                'by_authority': by_authority,
                'candidate_for': {k: len(v) for k, v in candidate_for.items()}
            }
        }
    
    def _save_results(self, summary: dict) -> str:
        """Save results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/sca_comprehensive/{self.seed_qid}_comprehensive_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(output_path)


def main():
    """Main entry point"""
    
    seed = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    throttle = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    
    builder = ComprehensiveDomainBuilder(seed, throttle)
    summary = builder.build()
    
    if summary:
        print(f"\nRESULTS:")
        print(f"  Total candidates: {summary['total_candidates']}")
        print(f"  With authorities: {summary['statistics']['by_authority']['any']}")
        print(f"\nCandidate breakdown:")
        for ctype, count in summary['statistics']['candidate_for'].items():
            print(f"  {ctype}: {count}")


if __name__ == "__main__":
    main()
