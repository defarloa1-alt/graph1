#!/usr/bin/env python3
"""
Check Temporal Properties in Failed Periods

For the 12 periods that failed enrichment, fetch their temporal properties:
- P580 (start time)
- P582 (end time)  
- P571 (inception)
- P576 (dissolved)
- P585 (point in time)
- P2348 (time period)

Show ALL temporal values with labels.
"""

import sys
from pathlib import Path
import json
import requests
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


FAILED_PERIODS = [
    {'qid': 'Q185063', 'label': 'Warring States period'},
    {'qid': 'Q27837', 'label': "Twenty Years' Anarchy"},
    {'qid': 'Q185852', 'label': 'Edwardian era'},
    {'qid': 'Q16410', 'label': 'Hungarian People\'s Republic'},
    {'qid': 'Q187979', 'label': 'Early Dynastic Period of Egypt'},
    {'qid': 'Q49696', 'label': 'Northern and Southern dynasties'},
    {'qid': 'Q189297', 'label': 'Zemene Mesafint'},
    {'qid': 'Q75207', 'label': 'Pax Romana'},
    {'qid': 'Q190882', 'label': 'Phoney War'},
    {'qid': 'Q148499', 'label': 'Margraviate of Brandenburg'},
    {'qid': 'Q191324', 'label': 'Middle Kingdom of Egypt'},
    {'qid': 'Q8951', 'label': 'Third Republic of Venezuela'}
]

TEMPORAL_PROPERTIES = {
    'P580': 'start time',
    'P582': 'end time',
    'P571': 'inception',
    'P576': 'dissolved, abolished or demolished date',
    'P585': 'point in time',
    'P2348': 'time period'
}


class TemporalChecker:
    """Check temporal properties in failed periods"""
    
    def __init__(self):
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        self.api_url = "https://www.wikidata.org/w/api.php"
        
    def check_all_failed(self):
        """Check temporal properties for all failed periods"""
        
        print(f"\n{'='*80}")
        print(f"CHECKING TEMPORAL PROPERTIES IN 12 FAILED PERIODS")
        print(f"{'='*80}\n")
        
        results = []
        
        for i, period in enumerate(FAILED_PERIODS):
            qid = period['qid']
            label = period['label']
            
            print(f"[{i+1}/12] {qid} ({label})...")
            
            # Wait between requests to avoid rate limit
            if i > 0:
                time.sleep(2)
            
            try:
                temporal_data = self._fetch_temporal_properties(qid)
                
                results.append({
                    **period,
                    'temporal_properties': temporal_data,
                    'has_start_end': self._has_start_and_end(temporal_data)
                })
                
                # Show summary
                has_se = "YES" if self._has_start_and_end(temporal_data) else "NO"
                prop_count = len([p for p in temporal_data.values() if p])
                print(f"  Temporal props: {prop_count}, Start+End: {has_se}")
                
            except Exception as e:
                print(f"  FAILED: {e}")
                results.append({
                    **period,
                    'error': str(e),
                    'has_start_end': False
                })
        
        return results
    
    def _fetch_temporal_properties(self, qid: str) -> dict:
        """Fetch temporal properties for a QID"""
        
        url = self.entity_url.format(qid=qid)
        
        response = requests.get(url, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        entity = data.get('entities', {}).get(qid, {})
        claims = entity.get('claims', {})
        
        # Extract temporal properties
        temporal = {}
        all_qids = set()
        
        for prop_id, prop_label in TEMPORAL_PROPERTIES.items():
            if prop_id in claims:
                values = []
                for claim in claims[prop_id]:
                    datavalue = claim.get('mainsnak', {}).get('datavalue', {})
                    
                    if datavalue.get('type') == 'time':
                        time_val = datavalue.get('value', {}).get('time', '')
                        values.append({'type': 'time', 'value': time_val})
                    elif datavalue.get('type') == 'wikibase-entityid':
                        qid_val = datavalue.get('value', {}).get('id', '')
                        values.append({'type': 'qid', 'value': qid_val})
                        all_qids.add(qid_val)
                
                temporal[prop_id] = values if values else None
            else:
                temporal[prop_id] = None
        
        # Fetch labels for QIDs
        if all_qids:
            labels = self._fetch_labels(list(all_qids))
            # Add labels to values
            for prop_values in temporal.values():
                if prop_values:
                    for val in prop_values:
                        if val['type'] == 'qid':
                            val['label'] = labels.get(val['value'], val['value'])
        
        return temporal
    
    def _fetch_labels(self, qids: list) -> dict:
        """Fetch labels for QIDs"""
        
        if not qids:
            return {}
        
        params = {
            'action': 'wbgetentities',
            'ids': '|'.join(qids[:50]),
            'props': 'labels',
            'languages': 'en',
            'format': 'json'
        }
        
        response = requests.get(self.api_url, params=params, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        
        labels = {}
        for entity_id, entity in data.get('entities', {}).items():
            label = entity.get('labels', {}).get('en', {}).get('value', entity_id)
            labels[entity_id] = label
        
        return labels
    
    def _has_start_and_end(self, temporal_data: dict) -> bool:
        """Check if entity has both start and end dates"""
        
        has_start = (temporal_data.get('P580') or temporal_data.get('P571'))
        has_end = (temporal_data.get('P582') or temporal_data.get('P576'))
        
        return bool(has_start and has_end)
    
    def print_results(self, results: list):
        """Print detailed results"""
        
        print(f"\n{'='*80}")
        print(f"TEMPORAL ANALYSIS RESULTS")
        print(f"{'='*80}\n")
        
        with_start_end = [r for r in results if r.get('has_start_end')]
        without_start_end = [r for r in results if not r.get('has_start_end')]
        
        print(f"Periods WITH start+end dates: {len(with_start_end)}")
        print(f"Periods WITHOUT complete dates: {len(without_start_end)}")
        print()
        
        # Show periods with start+end
        if with_start_end:
            print(f"{'='*80}")
            print(f"PERIODS WITH START+END DATES ({len(with_start_end)})")
            print(f"{'='*80}\n")
            
            for r in with_start_end:
                print(f"{r['qid']} - {r['label']}")
                print(f"{'-'*80}")
                
                temporal = r.get('temporal_properties', {})
                
                for prop_id, prop_label in TEMPORAL_PROPERTIES.items():
                    values = temporal.get(prop_id)
                    if values:
                        print(f"  {prop_id} ({prop_label}):")
                        for val in values:
                            if val['type'] == 'time':
                                print(f"    - {val['value']}")
                            elif val['type'] == 'qid':
                                label = val.get('label', val['value'])
                                print(f"    - {val['value']} ({label})")
                
                print()
        
        # Show periods without
        if without_start_end:
            print(f"{'='*80}")
            print(f"PERIODS WITHOUT COMPLETE DATES ({len(without_start_end)})")
            print(f"{'='*80}\n")
            
            for r in without_start_end:
                print(f"  {r['qid']} - {r['label']}")
                if r.get('error'):
                    print(f"    Error: {r['error']}")
            print()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    checker = TemporalChecker()
    results = checker.check_all_failed()
    checker.print_results(results)


if __name__ == "__main__":
    main()
