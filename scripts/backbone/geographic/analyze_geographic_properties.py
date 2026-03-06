#!/usr/bin/env python3
"""
Analyze Geographic Properties in Historical Periods

Check which of the enriched periods have geographic properties:
- P30 (continent)
- P36 (capital)
- P625 (coordinate location)
- P276 (location)
- P17 (country)
- P706 (located in/on physical feature)
- P47 (shares border with)
- P1376 (capital of)
- P131 (located in administrative territorial entity)
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


GEO_PROPERTIES = {
    'P30': 'continent',
    'P36': 'capital',
    'P625': 'coordinate location',
    'P276': 'location',
    'P17': 'country',
    'P706': 'located in/on physical feature',
    'P47': 'shares border with',
    'P1376': 'capital of',
    'P131': 'located in administrative territorial entity'
}


class GeographicAnalyzer:
    """Analyze geographic properties across periods"""
    
    def __init__(self, taxonomy_json: str):
        self.json_path = Path(taxonomy_json)
        self.data = None
        self.entities = {}
        
    def load_data(self):
        """Load taxonomy data"""
        
        print(f"Loading: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.entities = self.data.get('entities', {})
        print(f"  Loaded {len(self.entities)} entities\n")
        
    def analyze_geographic_coverage(self):
        """Analyze which entities have geographic properties"""
        
        print(f"{'='*80}")
        print(f"GEOGRAPHIC PROPERTY ANALYSIS")
        print(f"{'='*80}\n")
        
        results = {
            'with_geo': [],
            'without_geo': [],
            'geo_property_stats': {prop: 0 for prop in GEO_PROPERTIES.keys()}
        }
        
        for qid, entity in self.entities.items():
            label = entity.get('label', qid)
            claims = entity.get('claims_with_labels', {})
            
            # Check for any geographic property
            geo_props_found = {}
            has_any_geo = False
            
            for prop_id, prop_label in GEO_PROPERTIES.items():
                if prop_id in claims:
                    statements = claims[prop_id].get('statements', [])
                    if statements:
                        has_any_geo = True
                        results['geo_property_stats'][prop_id] += 1
                        
                        # Get values with labels
                        values = []
                        for stmt in statements[:3]:  # First 3 values
                            value = stmt.get('value')
                            value_label = stmt.get('value_label', value)
                            if value_label and value_label != value:
                                values.append(f"{value} ({value_label})")
                            else:
                                values.append(str(value))
                        
                        geo_props_found[prop_id] = {
                            'label': prop_label,
                            'values': values,
                            'count': len(statements)
                        }
            
            # Categorize
            entry = {
                'qid': qid,
                'label': label,
                'geo_properties': geo_props_found,
                'geo_count': len(geo_props_found)
            }
            
            if has_any_geo:
                results['with_geo'].append(entry)
            else:
                results['without_geo'].append(entry)
        
        return results
    
    def print_results(self, results: dict):
        """Print analysis results"""
        
        total = len(results['with_geo']) + len(results['without_geo'])
        with_geo = len(results['with_geo'])
        without_geo = len(results['without_geo'])
        
        print(f"\n{'='*80}")
        print(f"RESULTS")
        print(f"{'='*80}\n")
        
        print(f"Total entities: {total}")
        print(f"WITH geographic properties: {with_geo} ({with_geo/total*100:.1f}%)")
        print(f"WITHOUT geographic properties: {without_geo} ({without_geo/total*100:.1f}%)")
        print()
        
        # Property statistics
        print(f"GEOGRAPHIC PROPERTY USAGE:\n")
        sorted_props = sorted(results['geo_property_stats'].items(), 
                            key=lambda x: x[1], reverse=True)
        
        for prop_id, count in sorted_props:
            prop_label = GEO_PROPERTIES[prop_id]
            if count > 0:
                print(f"  {prop_id} ({prop_label}): {count} entities")
        
        # Entities WITH geo properties
        print(f"\n{'='*80}")
        print(f"ENTITIES WITH GEOGRAPHIC PROPERTIES ({with_geo})")
        print(f"{'='*80}\n")
        
        for entry in sorted(results['with_geo'], key=lambda x: x['geo_count'], reverse=True):
            qid = entry['qid']
            label = entry['label']
            geo_count = entry['geo_count']
            
            print(f"{qid} - {label}")
            print(f"  Geographic properties: {geo_count}")
            
            for prop_id, prop_data in entry['geo_properties'].items():
                prop_label = prop_data['label']
                values = prop_data['values']
                print(f"    {prop_id} ({prop_label}): {', '.join(values[:2])}")
                if len(values) > 2:
                    print(f"      ... and {len(values)-2} more")
            print()
        
        # Entities WITHOUT geo properties
        print(f"\n{'='*80}")
        print(f"ENTITIES WITHOUT GEOGRAPHIC PROPERTIES ({without_geo})")
        print(f"{'='*80}\n")
        
        for entry in results['without_geo']:
            qid = entry['qid']
            label = entry['label']
            print(f"  {qid} - {label}")
        
        print()
    
    def save_results(self, results: dict, output_filename: str = None):
        """Save results to JSON"""
        
        if not output_filename:
            output_filename = "output/analysis/geographic_analysis.json"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {output_path}")
        
        return str(output_path)
    
    def run_analysis(self):
        """Run complete analysis"""
        
        self.load_data()
        results = self.analyze_geographic_coverage()
        self.print_results(results)
        json_path = self.save_results(results)
        
        return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "output/taxonomy_recursive/Q17167_recursive_20260220_135756.json"
    
    analyzer = GeographicAnalyzer(json_file)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
