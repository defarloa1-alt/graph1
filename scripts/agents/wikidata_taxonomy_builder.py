#!/usr/bin/env python3
"""
Wikidata Taxonomy Builder

Extracts structural relationships from any QID:
- Parents (P31 instance of, P279 subclass of, P361 part of)
- Main subject (P921)
- Field of study (P2579, P101)
- Academic discipline (P101)
- Practiced by (P3095)
- Facets (P1269, P910)
- Parts/Children (P527 has parts, P150 contains)

ALWAYS includes labels for structural analysis.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.agents.wikidata_full_fetch_enhanced import WikidataEnhancedFetcher
import json
from typing import Dict, List, Tuple


class WikidataTaxonomyBuilder:
    """Build taxonomy from Wikidata entity"""
    
    # Key properties for taxonomy
    TAXONOMY_PROPERTIES = {
        # Parents/Classification
        'P31': 'instance of',
        'P279': 'subclass of', 
        'P361': 'part of',
        'P1269': 'facet of',
        
        # Context/Subject
        'P921': 'main subject',
        'P2348': 'time period',
        
        # Academic/Study
        'P2579': 'studied by',
        'P101': 'field of work',
        'P425': 'field of this occupation',
        'P2578': 'studies',
        
        # Practice/Use
        'P3095': 'practiced by',
        'P366': 'use',
        
        # Children/Parts
        'P527': 'has part(s)',
        'P150': 'contains administrative territorial entity',
        'P1269': 'facet of',
        
        # Categories
        'P910': "topic's main category",
        'P1792': 'category of associated people',
        'P1464': 'category for people born here',
        
        # Related
        'P155': 'follows',
        'P156': 'followed by',
        'P1366': 'replaced by',
        'P1365': 'replaces',
    }
    
    def __init__(self):
        self.fetcher = WikidataEnhancedFetcher()
    
    def build_taxonomy(self, qid: str) -> Dict:
        """
        Build complete taxonomy for a QID
        
        Returns structured taxonomy with all labels
        """
        print(f"\n{'='*80}")
        print(f"BUILDING TAXONOMY FOR: {qid}")
        print(f"{'='*80}\n")
        
        # Fetch enhanced data
        data = self.fetcher.fetch_entity_with_labels(qid)
        
        taxonomy = {
            'qid': qid,
            'label': data['labels'].get('en', qid),
            'description': data['descriptions'].get('en', ''),
            
            # Parents/Classification
            'parents': {
                'instance_of': [],      # P31
                'subclass_of': [],      # P279
                'part_of': [],          # P361
                'facet_of': [],         # P1269
            },
            
            # Context
            'context': {
                'main_subject': [],     # P921
                'time_period': [],      # P2348
            },
            
            # Academic/Study
            'academic': {
                'studied_by': [],       # P2579
                'field_of_work': [],    # P101
                'field_of_occupation': [], # P425
                'studies': [],          # P2578
            },
            
            # Practice
            'practice': {
                'practiced_by': [],     # P3095
                'use': [],              # P366
            },
            
            # Children/Parts
            'children': {
                'has_parts': [],        # P527
                'contains': [],         # P150
            },
            
            # Categories
            'categories': {
                'main_category': [],    # P910
                'people_category': [],  # P1792
            },
            
            # Related/Succession
            'related': {
                'follows': [],          # P155
                'followed_by': [],      # P156
                'replaced_by': [],      # P1366
                'replaces': [],         # P1365
            },
            
            # All other properties
            'other_properties': []
        }
        
        # Extract from enhanced claims
        claims = data.get('claims_with_labels', {})
        
        for prop_id, prop_data in claims.items():
            prop_label = prop_data['property_label']
            
            # Process each statement
            for stmt in prop_data['statements']:
                value = stmt.get('value')
                value_label = stmt.get('value_label', value)
                
                # Create entry with both ID and label
                entry = {
                    'id': value,
                    'label': value_label,
                    'rank': stmt.get('rank', 'normal'),
                    'qualifiers': self._extract_qualifiers(stmt)
                }
                
                # Categorize by property
                if prop_id == 'P31':
                    taxonomy['parents']['instance_of'].append(entry)
                elif prop_id == 'P279':
                    taxonomy['parents']['subclass_of'].append(entry)
                elif prop_id == 'P361':
                    taxonomy['parents']['part_of'].append(entry)
                elif prop_id == 'P1269':
                    taxonomy['parents']['facet_of'].append(entry)
                    
                elif prop_id == 'P921':
                    taxonomy['context']['main_subject'].append(entry)
                elif prop_id == 'P2348':
                    taxonomy['context']['time_period'].append(entry)
                    
                elif prop_id == 'P2579':
                    taxonomy['academic']['studied_by'].append(entry)
                elif prop_id == 'P101':
                    taxonomy['academic']['field_of_work'].append(entry)
                elif prop_id == 'P425':
                    taxonomy['academic']['field_of_occupation'].append(entry)
                elif prop_id == 'P2578':
                    taxonomy['academic']['studies'].append(entry)
                    
                elif prop_id == 'P3095':
                    taxonomy['practice']['practiced_by'].append(entry)
                elif prop_id == 'P366':
                    taxonomy['practice']['use'].append(entry)
                    
                elif prop_id == 'P527':
                    taxonomy['children']['has_parts'].append(entry)
                elif prop_id == 'P150':
                    taxonomy['children']['contains'].append(entry)
                    
                elif prop_id == 'P910':
                    taxonomy['categories']['main_category'].append(entry)
                elif prop_id == 'P1792':
                    taxonomy['categories']['people_category'].append(entry)
                    
                elif prop_id == 'P155':
                    taxonomy['related']['follows'].append(entry)
                elif prop_id == 'P156':
                    taxonomy['related']['followed_by'].append(entry)
                elif prop_id == 'P1366':
                    taxonomy['related']['replaced_by'].append(entry)
                elif prop_id == 'P1365':
                    taxonomy['related']['replaces'].append(entry)
                    
                else:
                    # Store other properties
                    taxonomy['other_properties'].append({
                        'property_id': prop_id,
                        'property_label': prop_label,
                        'value': entry
                    })
        
        return taxonomy
    
    def _extract_qualifiers(self, stmt: Dict) -> List[Dict]:
        """Extract qualifiers with labels"""
        qualifiers = []
        
        quals_with_labels = stmt.get('qualifiers_with_labels', {})
        for qual_prop, qual_data in quals_with_labels.items():
            qual_label = qual_data['property_label']
            
            for val_info in qual_data['values']:
                qualifiers.append({
                    'property_id': qual_prop,
                    'property_label': qual_label,
                    'value': val_info.get('value'),
                    'value_label': val_info.get('label', val_info.get('value'))
                })
        
        return qualifiers
    
    def print_taxonomy_tables(self, taxonomy: Dict):
        """Print taxonomy as structured tables"""
        
        qid = taxonomy['qid']
        label = taxonomy['label']
        desc = taxonomy['description']
        
        print(f"\n{'='*80}")
        print(f"STRUCTURAL TAXONOMY: {qid}")
        print(f"{'='*80}\n")
        
        print(f"ENTITY: {label}")
        print(f"DESCRIPTION: {desc}\n")
        
        # PARENTS TABLE
        print(f"\n{'='*80}")
        print("PARENTS / CLASSIFICATION")
        print(f"{'='*80}\n")
        
        self._print_relationship_table(
            "Instance Of (P31)",
            taxonomy['parents']['instance_of']
        )
        
        self._print_relationship_table(
            "Subclass Of (P279)",
            taxonomy['parents']['subclass_of']
        )
        
        self._print_relationship_table(
            "Part Of (P361)",
            taxonomy['parents']['part_of']
        )
        
        self._print_relationship_table(
            "Facet Of (P1269)",
            taxonomy['parents']['facet_of']
        )
        
        # CONTEXT TABLE
        print(f"\n{'='*80}")
        print("CONTEXT / SUBJECT")
        print(f"{'='*80}\n")
        
        self._print_relationship_table(
            "Main Subject (P921)",
            taxonomy['context']['main_subject']
        )
        
        self._print_relationship_table(
            "Time Period (P2348)",
            taxonomy['context']['time_period']
        )
        
        # ACADEMIC TABLE
        print(f"\n{'='*80}")
        print("ACADEMIC / FIELD OF STUDY")
        print(f"{'='*80}\n")
        
        self._print_relationship_table(
            "Studied By (P2579)",
            taxonomy['academic']['studied_by']
        )
        
        self._print_relationship_table(
            "Field of Work (P101)",
            taxonomy['academic']['field_of_work']
        )
        
        self._print_relationship_table(
            "Field of Occupation (P425)",
            taxonomy['academic']['field_of_occupation']
        )
        
        self._print_relationship_table(
            "Studies (P2578)",
            taxonomy['academic']['studies']
        )
        
        # PRACTICE TABLE
        print(f"\n{'='*80}")
        print("PRACTICE / USE")
        print(f"{'='*80}\n")
        
        self._print_relationship_table(
            "Practiced By (P3095)",
            taxonomy['practice']['practiced_by']
        )
        
        self._print_relationship_table(
            "Use (P366)",
            taxonomy['practice']['use']
        )
        
        # CHILDREN TABLE
        print(f"\n{'='*80}")
        print("CHILDREN / PARTS")
        print(f"{'='*80}\n")
        
        self._print_relationship_table(
            "Has Parts (P527)",
            taxonomy['children']['has_parts']
        )
        
        self._print_relationship_table(
            "Contains (P150)",
            taxonomy['children']['contains']
        )
        
        # SUCCESSION TABLE
        print(f"\n{'='*80}")
        print("SUCCESSION / RELATED")
        print(f"{'='*80}\n")
        
        self._print_relationship_table(
            "Follows (P155)",
            taxonomy['related']['follows']
        )
        
        self._print_relationship_table(
            "Followed By (P156)",
            taxonomy['related']['followed_by']
        )
        
        self._print_relationship_table(
            "Replaced By (P1366)",
            taxonomy['related']['replaced_by']
        )
        
        self._print_relationship_table(
            "Replaces (P1365)",
            taxonomy['related']['replaces']
        )
        
        # SUMMARY TABLE
        print(f"\n{'='*80}")
        print("TAXONOMY SUMMARY")
        print(f"{'='*80}\n")
        
        summary = {
            'Parents (Classification)': (
                len(taxonomy['parents']['instance_of']) +
                len(taxonomy['parents']['subclass_of']) +
                len(taxonomy['parents']['part_of']) +
                len(taxonomy['parents']['facet_of'])
            ),
            'Context': (
                len(taxonomy['context']['main_subject']) +
                len(taxonomy['context']['time_period'])
            ),
            'Academic': (
                len(taxonomy['academic']['studied_by']) +
                len(taxonomy['academic']['field_of_work']) +
                len(taxonomy['academic']['field_of_occupation']) +
                len(taxonomy['academic']['studies'])
            ),
            'Practice': (
                len(taxonomy['practice']['practiced_by']) +
                len(taxonomy['practice']['use'])
            ),
            'Children': (
                len(taxonomy['children']['has_parts']) +
                len(taxonomy['children']['contains'])
            ),
            'Related': (
                len(taxonomy['related']['follows']) +
                len(taxonomy['related']['followed_by']) +
                len(taxonomy['related']['replaced_by']) +
                len(taxonomy['related']['replaces'])
            )
        }
        
        for category, count in summary.items():
            status = "FOUND" if count > 0 else "NOT FOUND"
            print(f"{category:30s}: {count:3d} relationships - {status}")
        
        print(f"\n{'='*80}\n")
    
    def _print_relationship_table(self, title: str, items: List[Dict]):
        """Print a relationship table"""
        
        if not items:
            print(f"{title}: NONE\n")
            return
        
        print(f"{title}:")
        print(f"{'-'*80}")
        print(f"{'QID':<15} {'Label':<40} {'Rank':<10}")
        print(f"{'-'*80}")
        
        for item in items:
            qid = item['id'] if isinstance(item['id'], str) else str(item['id'])
            label = item['label'][:38] if len(item['label']) > 38 else item['label']
            rank = item['rank']
            
            print(f"{qid:<15} {label:<40} {rank:<10}")
            
            # Print qualifiers if any
            if item.get('qualifiers'):
                for qual in item['qualifiers'][:2]:  # Show first 2 qualifiers
                    q_label = qual['property_label'][:20]
                    q_val_label = qual.get('value_label', qual['value'])
                    if isinstance(q_val_label, str) and len(q_val_label) > 30:
                        q_val_label = q_val_label[:27] + "..."
                    print(f"  + {q_label}: {q_val_label}")
        
        print()
    
    def save_taxonomy(self, taxonomy: Dict, filename: str = None):
        """Save taxonomy to JSON"""
        
        if not filename:
            qid = taxonomy['qid']
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"output/taxonomy/{qid}_taxonomy_{timestamp}.json"
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(taxonomy, f, indent=2, ensure_ascii=False)
        
        print(f"TAXONOMY SAVED: {filename}\n")
        
        return filename


# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_taxonomy_builder(qid: str):
    """Test taxonomy builder"""
    
    builder = WikidataTaxonomyBuilder()
    
    try:
        # Build taxonomy
        taxonomy = builder.build_taxonomy(qid)
        
        # Print tables
        builder.print_taxonomy_tables(taxonomy)
        
        # Save to JSON
        builder.save_taxonomy(taxonomy)
        
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
    
    print(f"Building taxonomy for: {qid}")
    
    test_taxonomy_builder(qid)
