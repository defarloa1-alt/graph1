#!/usr/bin/env python3
"""
Find all entities that USE a specific property

Different from backlinks - this finds entities that HAVE the property,
not entities that the property points to.

Example: Find all entities that have P2184 (history of topic)
"""

import sys
import requests
import json
from datetime import datetime
from pathlib import Path


class PropertyUsersExplorer:
    """Find entities that use a specific property"""
    
    def __init__(self):
        self.wikidata_endpoint = "https://query.wikidata.org/sparql"
        
    def find_property_users(self, property_id: str, limit: int = 100) -> list:
        """
        Find all entities that have a specific property
        
        Args:
            property_id: Property to search for (e.g., 'P2184')
            limit: Max results
        
        Returns:
            List of entities with this property
        """
        
        print(f"\n{'='*80}")
        print(f"FINDING ENTITIES THAT USE: {property_id}")
        print(f"Limit: {limit}")
        print(f"{'='*80}\n")
        
        # SPARQL: Find entities that have this property with any value
        sparql = f"""
        SELECT DISTINCT ?item ?itemLabel ?value ?valueLabel
        WHERE {{
          ?item wdt:{property_id} ?value .
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
        
        print(f"  Found {len(bindings)} results\n")
        
        results = []
        for binding in bindings:
            item_qid = binding['item']['value'].split('/')[-1]
            value_qid = binding.get('value', {}).get('value', '').split('/')[-1] if binding.get('value') else None
            
            results.append({
                'qid': item_qid,
                'label': binding.get('itemLabel', {}).get('value', item_qid),
                'property': property_id,
                'value': value_qid if value_qid and value_qid.startswith('Q') else binding.get('value', {}).get('value', ''),
                'value_label': binding.get('valueLabel', {}).get('value', '')
            })
        
        return results
    
    def print_results(self, results: list, property_id: str):
        """Print results"""
        
        print(f"{'='*80}")
        print(f"ENTITIES USING {property_id} ({len(results)})")
        print(f"{'='*80}\n")
        
        for r in results:
            print(f"{r['qid']} - {r['label']}")
            print(f"  {property_id} -> {r['value']} ({r['value_label']})")
            print()
    
    def save_results(self, results: list, property_id: str):
        """Save results to JSON"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"output/property_users/{property_id}_users_{timestamp}.json"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {output_path}\n")
        
        return str(output_path)
    
    def run_exploration(self, property_id: str, limit: int = 100):
        """Run complete exploration"""
        
        results = self.find_property_users(property_id, limit)
        self.print_results(results, property_id)
        json_path = self.save_results(results, property_id)
        
        return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    property_id = sys.argv[1] if len(sys.argv) > 1 else 'P2184'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    explorer = PropertyUsersExplorer()
    results = explorer.run_exploration(property_id, limit)
    
    print(f"Found {len(results)} entities using {property_id}")


if __name__ == "__main__":
    main()
