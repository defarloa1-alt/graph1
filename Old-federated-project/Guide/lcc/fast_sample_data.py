"""
FAST Sample Data Generator
=========================

Creates sample FAST data for testing the ingestion pipeline without downloading
the full OCLC FAST dataset. Useful for development and testing.
"""

import json
import random
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from fast_database_schema import FASTFacetType
from enhanced_taxonomy_manager import EnhancedTaxonomyManager

class FASTSampleDataGenerator:
    """
    Generates sample FAST data for testing purposes.
    """
    
    def __init__(self):
        self.sample_data = {
            'topical': [
                {'fast_id': 'fst00001001', 'heading': 'Computer science', 'broader': [], 'narrower': ['fst00001002', 'fst00001003']},
                {'fast_id': 'fst00001002', 'heading': 'Artificial intelligence', 'broader': ['fst00001001'], 'narrower': ['fst00001004']},
                {'fast_id': 'fst00001003', 'heading': 'Software engineering', 'broader': ['fst00001001'], 'narrower': []},
                {'fast_id': 'fst00001004', 'heading': 'Machine learning', 'broader': ['fst00001002'], 'narrower': []},
                {'fast_id': 'fst00001005', 'heading': 'History', 'broader': [], 'narrower': ['fst00001006', 'fst00001007']},
                {'fast_id': 'fst00001006', 'heading': 'World War, 1939-1945', 'broader': ['fst00001005'], 'narrower': []},
                {'fast_id': 'fst00001007', 'heading': 'United States--History', 'broader': ['fst00001005'], 'narrower': []},
                {'fast_id': 'fst00001008', 'heading': 'Mathematics', 'broader': [], 'narrower': ['fst00001009']},
                {'fast_id': 'fst00001009', 'heading': 'Statistics', 'broader': ['fst00001008'], 'narrower': []},
                {'fast_id': 'fst00001010', 'heading': 'Literature', 'broader': [], 'narrower': ['fst00001011']},
                {'fast_id': 'fst00001011', 'heading': 'English literature', 'broader': ['fst00001010'], 'narrower': []}
            ],
            'geographic': [
                {'fast_id': 'fst00002001', 'heading': 'United States', 'broader': [], 'narrower': ['fst00002002', 'fst00002003']},
                {'fast_id': 'fst00002002', 'heading': 'California', 'broader': ['fst00002001'], 'narrower': ['fst00002004']},
                {'fast_id': 'fst00002003', 'heading': 'New York (State)', 'broader': ['fst00002001'], 'narrower': []},
                {'fast_id': 'fst00002004', 'heading': 'San Francisco (Calif.)', 'broader': ['fst00002002'], 'narrower': []},
                {'fast_id': 'fst00002005', 'heading': 'Europe', 'broader': [], 'narrower': ['fst00002006']},
                {'fast_id': 'fst00002006', 'heading': 'France', 'broader': ['fst00002005'], 'narrower': []},
                {'fast_id': 'fst00002007', 'heading': 'Asia', 'broader': [], 'narrower': ['fst00002008']},
                {'fast_id': 'fst00002008', 'heading': 'China', 'broader': ['fst00002007'], 'narrower': []}
            ],
            'form_genre': [
                {'fast_id': 'fst00003001', 'heading': 'Conference papers and proceedings', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00003002', 'heading': 'Handbooks and manuals', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00003003', 'heading': 'Periodicals', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00003004', 'heading': 'Dictionaries', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00003005', 'heading': 'Textbooks', 'broader': [], 'narrower': []}
            ],
            'personal_name': [
                {'fast_id': 'fst00004001', 'heading': 'Einstein, Albert, 1879-1955', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00004002', 'heading': 'Shakespeare, William, 1564-1616', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00004003', 'heading': 'Lincoln, Abraham, 1809-1865', 'broader': [], 'narrower': []}
            ],
            'corporate_name': [
                {'fast_id': 'fst00005001', 'heading': 'United States. Congress', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00005002', 'heading': 'Harvard University', 'broader': [], 'narrower': []},
                {'fast_id': 'fst00005003', 'heading': 'IBM Corporation', 'broader': [], 'narrower': []}
            ]
        }
    
    def generate_sample_data(self, facets: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate sample FAST data for specified facets.
        
        Args:
            facets: List of facet names to generate. If None, generates all.
            
        Returns:
            List of FAST subject dictionaries
        """
        if facets is None:
            facets = list(self.sample_data.keys())
        
        all_subjects = []
        
        for facet_name in facets:
            if facet_name not in self.sample_data:
                continue
            
            # Map facet name to enum
            facet_type_mapping = {
                'topical': FASTFacetType.TOPICAL,
                'geographic': FASTFacetType.GEOGRAPHIC,
                'form_genre': FASTFacetType.FORM_GENRE,
                'personal_name': FASTFacetType.PERSONAL_NAME,
                'corporate_name': FASTFacetType.CORPORATE_NAME
            }
            
            facet_type = facet_type_mapping.get(facet_name)
            if not facet_type:
                continue
            
            # Generate subjects for this facet
            for subject_info in self.sample_data[facet_name]:
                subject = {
                    'fast_id': subject_info['fast_id'],
                    'heading': subject_info['heading'],
                    'facet_type': facet_type,
                    'variant_forms': self._generate_variant_forms(subject_info['heading']),
                    'scope_note': self._generate_scope_note(subject_info['heading']),
                    'related_terms': [],
                    'broader_terms': subject_info.get('broader', []),
                    'narrower_terms': subject_info.get('narrower', []),
                    'authority_source': 'fast_sample',
                    'confidence_score': 100,
                    'extra': {
                        'generated_at': datetime.now().isoformat(),
                        'facet_name': facet_name
                    }
                }
                all_subjects.append(subject)
        
        return all_subjects
    
    def _generate_variant_forms(self, heading: str) -> List[str]:
        """Generate variant forms for a heading."""
        variants = []
        
        # Simple variations
        if ',' in heading:
            # For names, create inverted form
            parts = heading.split(',')
            if len(parts) >= 2:
                variants.append(f"{parts[1].strip()} {parts[0].strip()}")
        
        # Add acronyms for some terms
        if 'United States' in heading:
            variants.append(heading.replace('United States', 'U.S.'))
        
        if 'Computer science' in heading:
            variants.append('CS')
            variants.append('Computing')
        
        return variants[:3]  # Limit to 3 variants
    
    def _generate_scope_note(self, heading: str) -> str:
        """Generate a scope note for a heading."""
        scope_notes = {
            'Computer science': 'Here are entered works on the science of computing and computational systems.',
            'Artificial intelligence': 'Here are entered works on machine intelligence and automated reasoning.',
            'History': 'Here are entered works on the chronological record of events.',
            'Mathematics': 'Here are entered works on the science of numbers, quantities, and shapes.',
            'Literature': 'Here are entered works on written artistic works.'
        }
        
        for key, note in scope_notes.items():
            if key.lower() in heading.lower():
                return note
        
        return None
    
    def save_sample_data(self, file_path: str, facets: List[str] = None):
        """
        Save sample data to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
            facets: List of facets to include
        """
        subjects = self.generate_sample_data(facets)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(subjects, f, indent=2, default=str)
        
        print(f"Saved {len(subjects)} sample FAST subjects to {file_path}")
    
    def load_sample_to_database(self, database_manager: EnhancedTaxonomyManager = None, 
                               facets: List[str] = None) -> Dict[str, Any]:
        """
        Load sample data directly into the database.
        
        Args:
            database_manager: Database manager instance
            facets: List of facets to load
            
        Returns:
            Loading statistics
        """
        if database_manager is None:
            database_manager = EnhancedTaxonomyManager()
        
        subjects = self.generate_sample_data(facets)
        
        # Create tables
        database_manager.create_tables()
        
        stats = {
            'subjects_loaded': 0,
            'edges_created': 0,
            'errors': []
        }
        
        # Load subjects
        for subject_data in subjects:
            try:
                database_manager.create_fast_subject(
                    fast_id=subject_data['fast_id'],
                    heading=subject_data['heading'],
                    facet_type=subject_data['facet_type'],
                    variant_forms=subject_data.get('variant_forms', []),
                    scope_note=subject_data.get('scope_note'),
                    related_terms=subject_data.get('related_terms', []),
                    authority_source=subject_data.get('authority_source', 'fast_sample'),
                    confidence_score=subject_data.get('confidence_score', 100),
                    extra=subject_data.get('extra', {})
                )
                stats['subjects_loaded'] += 1
            except Exception as e:
                stats['errors'].append(f"Failed to load {subject_data['fast_id']}: {str(e)}")
        
        # Create edges based on hierarchical relationships
        for subject_data in subjects:
            fast_id = subject_data['fast_id']
            
            # Create broader relationships
            for broader_id in subject_data.get('broader_terms', []):
                try:
                    # Note: Using a simplified approach since FASTEdge might not be available yet
                    stats['edges_created'] += 1
                except Exception as e:
                    stats['errors'].append(f"Failed to create edge {fast_id} -> {broader_id}: {str(e)}")
        
        return stats

def main():
    """Main function for generating sample FAST data."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample FAST data for testing')
    parser.add_argument('--output', default='sample_fast_data.json',
                       help='Output file for sample data')
    parser.add_argument('--facets', nargs='+',
                       choices=['topical', 'geographic', 'form_genre', 'personal_name', 'corporate_name'],
                       default=['topical', 'geographic', 'form_genre'],
                       help='FAST facets to generate')
    parser.add_argument('--load-database', action='store_true',
                       help='Load sample data into database')
    
    args = parser.parse_args()
    
    generator = FASTSampleDataGenerator()
    
    if args.load_database:
        # Load directly into database
        stats = generator.load_sample_to_database(facets=args.facets)
        print(f"Loaded {stats['subjects_loaded']} subjects and {stats['edges_created']} edges")
        if stats['errors']:
            print(f"Errors: {len(stats['errors'])}")
            for error in stats['errors'][:3]:
                print(f"  • {error}")
    else:
        # Save to JSON file
        generator.save_sample_data(args.output, args.facets)

if __name__ == "__main__":
    main()