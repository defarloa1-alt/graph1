#!/usr/bin/env python3
"""
Wikidata Backlinks Explorer

Finds all entities that link TO a target QID (e.g., historical period Q11514315)
Then triages them using the same analysis as the root entity.

For each backlink:
- Fetch QID + Label
- Fetch key properties (P31, P279, P361, P527, P2348, P580, P582)
- Determine if it's a period, event, concept, etc.
- Map to facets
"""

import sys
from pathlib import Path
import requests
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class WikidataBacklinksExplorer:
    """Explore entities that link TO a target QID"""
    
    def __init__(self):
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        self.api_url = "https://www.wikidata.org/w/api.php"
        
    def get_backlinks(self, target_qid: str, property_id: str = "P31", limit: int = 100) -> list:
        """
        Get all entities that have property pointing to target QID
        
        Args:
            target_qid: Target QID (e.g., Q11514315 for historical period)
            property_id: Property to check (default P31 = instance of)
            limit: Max results
        
        Returns:
            List of backlink entities
        """
        
        print(f"\n{'='*80}")
        print(f"QUERYING BACKLINKS TO: {target_qid}")
        print(f"Property: {property_id}")
        print(f"Limit: {limit}")
        print(f"{'='*80}\n")
        
        # SPARQL query for backlinks
        sparql = f"""
        SELECT DISTINCT ?item ?itemLabel ?itemDescription
        WHERE {{
          ?item wdt:{property_id} wd:{target_qid} .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """
        
        headers = {
            'User-Agent': 'Chrystallum/1.0 (research project)',
            'Accept': 'application/sparql-results+json'
        }
        
        print(f"Executing SPARQL query...")
        
        response = requests.get(
            self.wikidata_endpoint,
            params={'query': sparql, 'format': 'json'},
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        bindings = data['results']['bindings']
        
        print(f"  Found {len(bindings)} backlinks\n")
        
        backlinks = []
        for binding in bindings:
            item_qid = binding['item']['value'].split('/')[-1]
            backlinks.append({
                'qid': item_qid,
                'label': binding.get('itemLabel', {}).get('value', item_qid),
                'description': binding.get('itemDescription', {}).get('value', '')
            })
        
        return backlinks
    
    def triage_backlinks(self, backlinks: list) -> dict:
        """
        Triage backlinks - get key properties for each
        
        Args:
            backlinks: List of backlink dicts
        
        Returns:
            Triaged data with classifications
        """
        
        print(f"\n{'='*80}")
        print(f"TRIAGING {len(backlinks)} BACKLINKS")
        print(f"{'='*80}\n")
        
        triaged = {
            'total': len(backlinks),
            'periods': [],
            'events': [],
            'concepts': [],
            'other': [],
            'failed': []
        }
        
        for i, backlink in enumerate(backlinks):
            qid = backlink['qid']
            label = backlink['label']
            
            print(f"[{i+1}/{len(backlinks)}] {qid} ({label})...", end=" ")
            
            try:
                # Get key properties for this entity
                key_props = self._get_key_properties(qid)
                
                # Classify
                classification = self._classify_entity(key_props)
                
                entry = {
                    **backlink,
                    'key_properties': key_props,
                    'classification': classification
                }
                
                # Categorize
                if classification == 'period':
                    triaged['periods'].append(entry)
                    print("PERIOD")
                elif classification == 'event':
                    triaged['events'].append(entry)
                    print("EVENT")
                elif classification == 'concept':
                    triaged['concepts'].append(entry)
                    print("CONCEPT")
                else:
                    triaged['other'].append(entry)
                    print(f"OTHER ({classification})")
                    
            except Exception as e:
                triaged['failed'].append({**backlink, 'error': str(e)})
                print(f"FAILED - {e}")
        
        print(f"\n{'='*80}")
        print(f"TRIAGE COMPLETE")
        print(f"{'='*80}\n")
        print(f"  Periods: {len(triaged['periods'])}")
        print(f"  Events: {len(triaged['events'])}")
        print(f"  Concepts: {len(triaged['concepts'])}")
        print(f"  Other: {len(triaged['other'])}")
        print(f"  Failed: {len(triaged['failed'])}")
        
        return triaged
    
    def _get_key_properties(self, qid: str) -> dict:
        """Get key properties for classification"""
        
        # Use Wikidata API to get specific properties
        params = {
            'action': 'wbgetentities',
            'ids': qid,
            'props': 'claims',
            'format': 'json'
        }
        
        response = requests.get(self.api_url, params=params, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        entity = data.get('entities', {}).get(qid, {})
        claims = entity.get('claims', {})
        
        # Extract key property values
        key_props = {
            'has_P31': 'P31' in claims,  # instance of
            'has_P279': 'P279' in claims,  # subclass of
            'has_P580': 'P580' in claims,  # start time
            'has_P582': 'P582' in claims,  # end time
            'has_P571': 'P571' in claims,  # inception
            'has_P576': 'P576' in claims,  # dissolved
            'has_P585': 'P585' in claims,  # point in time
            'has_P527': 'P527' in claims,  # has parts
            'P31_count': len(claims.get('P31', [])),
            'P279_count': len(claims.get('P279', []))
        }
        
        return key_props
    
    def _classify_entity(self, key_props: dict) -> str:
        """Classify entity based on key properties"""
        
        # Period: has start/end time or inception/dissolved
        if (key_props['has_P580'] and key_props['has_P582']) or \
           (key_props['has_P571'] and key_props['has_P576']):
            return 'period'
        
        # Event: has point in time
        if key_props['has_P585']:
            return 'event'
        
        # Concept: has subclass of but no temporal properties
        if key_props['has_P279'] and not key_props['has_P580']:
            return 'concept'
        
        # Other
        return 'other'
    
    def save_triage_results(self, triaged: dict, output_filename: str = None):
        """Save triage results to JSON"""
        
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"output/backlinks/backlinks_triage_{timestamp}.json"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(triaged, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved: {output_path}")
        
        return str(output_path)
    
    def print_triage_summary(self, triaged: dict):
        """Print summary of triaged backlinks"""
        
        print(f"\n{'='*80}")
        print(f"BACKLINK TRIAGE SUMMARY")
        print(f"{'='*80}\n")
        
        # Periods
        if triaged['periods']:
            print(f"PERIODS ({len(triaged['periods'])}):")
            print(f"{'-'*80}")
            for p in triaged['periods'][:20]:
                print(f"  {p['qid']:<12} {p['label'][:50]}")
            if len(triaged['periods']) > 20:
                print(f"  ... and {len(triaged['periods']) - 20} more")
            print()
        
        # Events
        if triaged['events']:
            print(f"EVENTS ({len(triaged['events'])}):")
            print(f"{'-'*80}")
            for e in triaged['events'][:10]:
                print(f"  {e['qid']:<12} {e['label'][:50]}")
            if len(triaged['events']) > 10:
                print(f"  ... and {len(triaged['events']) - 10} more")
            print()
        
        # Concepts
        if triaged['concepts']:
            print(f"CONCEPTS ({len(triaged['concepts'])}):")
            print(f"{'-'*80}")
            for c in triaged['concepts'][:10]:
                print(f"  {c['qid']:<12} {c['label'][:50]}")
            if len(triaged['concepts']) > 10:
                print(f"  ... and {len(triaged['concepts']) - 10} more")
            print()
    
    def run_exploration(self, target_qid: str, property_id: str = "P31", limit: int = 100):
        """Run complete backlinks exploration"""
        
        print(f"\n{'='*80}")
        print(f"WIKIDATA BACKLINKS EXPLORATION")
        print(f"{'='*80}")
        
        # Get backlinks
        backlinks = self.get_backlinks(target_qid, property_id, limit)
        
        # Triage
        triaged = self.triage_backlinks(backlinks)
        
        # Print summary
        self.print_triage_summary(triaged)
        
        # Save
        output_path = self.save_triage_results(triaged)
        
        print(f"\n{'='*80}")
        print(f"EXPLORATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"File: {output_path}")
        print(f"Total backlinks: {triaged['total']}")
        
        return triaged


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    # Default: Get backlinks to Q11514315 (historical period)
    target_qid = sys.argv[1] if len(sys.argv) > 1 else 'Q11514315'
    property_id = sys.argv[2] if len(sys.argv) > 2 else 'P31'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    explorer = WikidataBacklinksExplorer()
    triaged = explorer.run_exploration(target_qid, property_id, limit)
    
    print(f"\nPERIODS found: {len(triaged['periods'])}")
    print(f"These are SubjectConcept candidates!")


if __name__ == "__main__":
    main()
