"""
LCC-FAST Crosswalk Builder
=========================

Creates mappings between Library of Congress Classification (LCC) codes
and FAST (Faceted Application of Subject Terminology) identifiers.
Supports both automated matching and manual mapping configuration.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass

from enhanced_taxonomy_manager import EnhancedTaxonomyManager
from fast_database_schema import FASTFacetType, LCCFASTCrosswalk

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CrosswalkMapping:
    """Data class for crosswalk mapping configurations."""
    lcc_code: str
    fast_id: str
    mapping_type: str  # 'direct', 'approximate', 'manual'
    confidence_level: int  # 0-100
    mapping_source: str
    facet_relevance: Dict[str, int]  # Facet importance scores
    scope_notes: str = ""
    verified: bool = False

class LCCFASTCrosswalkBuilder:
    """
    Builds crosswalk mappings between LCC classification codes and FAST subjects.
    """
    
    def __init__(self, database_manager: Optional[EnhancedTaxonomyManager] = None):
        """
        Initialize crosswalk builder.
        
        Args:
            database_manager: Database manager for accessing LCC and FAST data
        """
        self.db_manager = database_manager or EnhancedTaxonomyManager()
        
        # Statistics
        self.stats = {
            'total_lcc_codes': 0,
            'total_fast_subjects': 0,
            'mappings_created': 0,
            'direct_matches': 0,
            'approximate_matches': 0,
            'manual_mappings': 0,
            'errors': []
        }
        
        # Predefined mappings for key domains
        self.manual_mappings = self._load_manual_mappings()
        
        # Subject area mapping patterns
        self.subject_patterns = self._initialize_subject_patterns()
    
    def _load_manual_mappings(self) -> Dict[str, List[CrosswalkMapping]]:
        """
        Load manually curated LCC-FAST mappings for key domains.
        
        Returns:
            Dictionary of LCC codes to FAST mappings
        """
        manual_mappings = {
            # Computer Science (QA76)
            'QA76': [
                CrosswalkMapping(
                    lcc_code='QA76',
                    fast_id='fst00001001',  # Computer science
                    mapping_type='direct',
                    confidence_level=95,
                    mapping_source='manual_expert',
                    facet_relevance={'topical': 100},
                    scope_notes='Core computer science classification',
                    verified=True
                )
            ],
            
            # History (D)
            'D': [
                CrosswalkMapping(
                    lcc_code='D',
                    fast_id='fst00001005',  # History
                    mapping_type='direct',
                    confidence_level=90,
                    mapping_source='manual_expert',
                    facet_relevance={'topical': 100},
                    scope_notes='General history classification',
                    verified=True
                )
            ],
            
            # World War II (D731-838)
            'D731-838': [
                CrosswalkMapping(
                    lcc_code='D731-838',
                    fast_id='fst00001006',  # World War, 1939-1945
                    mapping_type='direct',
                    confidence_level=95,
                    mapping_source='manual_expert',
                    facet_relevance={'topical': 90, 'chronological': 80},
                    scope_notes='World War II period and events',
                    verified=True
                )
            ],
            
            # Mathematics (QA)
            'QA': [
                CrosswalkMapping(
                    lcc_code='QA',
                    fast_id='fst00001008',  # Mathematics
                    mapping_type='direct',
                    confidence_level=95,
                    mapping_source='manual_expert',
                    facet_relevance={'topical': 100},
                    scope_notes='Pure and applied mathematics',
                    verified=True
                )
            ],
            
            # Literature (P, PN, PR, PS, etc.)
            'P': [
                CrosswalkMapping(
                    lcc_code='P',
                    fast_id='fst00001010',  # Literature
                    mapping_type='approximate',
                    confidence_level=80,
                    mapping_source='manual_expert',
                    facet_relevance={'topical': 100, 'form_genre': 70},
                    scope_notes='Language and literature classification',
                    verified=True
                )
            ]
        }
        
        return manual_mappings
    
    def _initialize_subject_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize patterns for automated subject area matching.
        
        Returns:
            Dictionary of subject patterns with matching rules
        """
        patterns = {
            'computer_science': {
                'lcc_patterns': [r'^QA76', r'^T385', r'^TK5105'],
                'fast_keywords': ['computer', 'software', 'programming', 'artificial intelligence'],
                'primary_facets': ['topical'],
                'confidence_base': 85
            },
            'history': {
                'lcc_patterns': [r'^D[0-9]', r'^E[0-9]', r'^F[0-9]'],
                'fast_keywords': ['history', 'historical', 'war', 'revolution', 'era'],
                'primary_facets': ['topical', 'geographic', 'chronological'],
                'confidence_base': 80
            },
            'mathematics': {
                'lcc_patterns': [r'^QA[0-9]', r'^QA1[0-9][0-9]'],
                'fast_keywords': ['mathematics', 'algebra', 'calculus', 'geometry', 'statistics'],
                'primary_facets': ['topical'],
                'confidence_base': 90
            },
            'geography': {
                'lcc_patterns': [r'^G[0-9]', r'^GB[0-9]', r'^GC[0-9]'],
                'fast_keywords': ['geography', 'location', 'place', 'region'],
                'primary_facets': ['topical', 'geographic'],
                'confidence_base': 85
            },
            'literature': {
                'lcc_patterns': [r'^P[A-Z][0-9]', r'^PN[0-9]'],
                'fast_keywords': ['literature', 'poetry', 'novel', 'drama', 'fiction'],
                'primary_facets': ['topical', 'form_genre'],
                'confidence_base': 80
            }
        }
        
        return patterns
    
    def analyze_existing_data(self) -> Dict[str, Any]:
        """
        Analyze existing LCC and FAST data to understand mapping potential.
        
        Returns:
            Analysis results and statistics
        """
        logger.info("Analyzing existing LCC and FAST data...")
        
        # Get LCC nodes
        lcc_nodes = []
        with self.db_manager.get_session() as session:
            from lcc_database_schema import SubjectNode
            lcc_nodes = session.query(SubjectNode).all()
        
        # Get FAST subjects
        fast_subjects = []
        with self.db_manager.get_session() as session:
            from fast_database_schema import FASTSubject
            fast_subjects = session.query(FASTSubject).all()
        
        self.stats['total_lcc_codes'] = len(lcc_nodes)
        self.stats['total_fast_subjects'] = len(fast_subjects)
        
        # Analyze LCC code patterns
        lcc_patterns = {}
        for node in lcc_nodes:
            # Extract main class letter(s)
            main_class = re.match(r'^([A-Z]+)', node.class_code)
            if main_class:
                main_class_str = main_class.group(1)
                if main_class_str not in lcc_patterns:
                    lcc_patterns[main_class_str] = []
                lcc_patterns[main_class_str].append(node.class_code)
        
        # Analyze FAST facet distribution
        fast_facets = {}
        for subject in fast_subjects:
            facet = subject.facet_type.value
            if facet not in fast_facets:
                fast_facets[facet] = 0
            fast_facets[facet] += 1
        
        analysis = {
            'lcc_main_classes': {k: len(v) for k, v in lcc_patterns.items()},
            'fast_facet_distribution': fast_facets,
            'potential_mappings': len(lcc_nodes) * len(fast_subjects),  # Theoretical maximum
            'recommended_approach': self._recommend_mapping_approach(lcc_patterns, fast_facets)
        }
        
        logger.info(f"Analysis complete: {len(lcc_nodes)} LCC codes, {len(fast_subjects)} FAST subjects")
        return analysis
    
    def _recommend_mapping_approach(self, lcc_patterns: Dict, fast_facets: Dict) -> List[str]:
        """Recommend mapping approach based on data analysis."""
        recommendations = []
        
        # Check data size
        if self.stats['total_lcc_codes'] < 100:
            recommendations.append("Use manual mapping for small LCC dataset")
        elif self.stats['total_lcc_codes'] > 10000:
            recommendations.append("Implement automated text matching for large dataset")
        else:
            recommendations.append("Use hybrid approach: automated + manual verification")
        
        # Check FAST facet diversity
        if len(fast_facets) > 5:
            recommendations.append("Leverage multiple FAST facets for rich mappings")
        
        # Check for common subject areas
        if 'QA' in lcc_patterns or 'Q' in lcc_patterns:
            recommendations.append("Prioritize science/technology mappings")
        if 'D' in lcc_patterns or 'E' in lcc_patterns:
            recommendations.append("Focus on historical subject mappings")
        
        return recommendations
    
    def create_automated_mappings(self, confidence_threshold: int = 70) -> List[CrosswalkMapping]:
        """
        Create automated mappings using pattern matching and text analysis.
        
        Args:
            confidence_threshold: Minimum confidence level for automated mappings
            
        Returns:
            List of automated crosswalk mappings
        """
        logger.info("Creating automated LCC-FAST mappings...")
        automated_mappings = []
        
        # Get all LCC nodes and FAST subjects
        with self.db_manager.get_session() as session:
            from lcc_database_schema import SubjectNode
            from fast_database_schema import FASTSubject
            
            lcc_nodes = session.query(SubjectNode).all()
            fast_subjects = session.query(FASTSubject).all()
        
        # Create lookup dictionaries for efficiency
        fast_by_heading = {subject.heading.lower(): subject for subject in fast_subjects}
        fast_keywords = set()
        for subject in fast_subjects:
            fast_keywords.update(subject.heading.lower().split())
        
        for lcc_node in lcc_nodes:
            lcc_mappings = self._find_automated_matches(
                lcc_node, fast_subjects, fast_by_heading, fast_keywords, confidence_threshold
            )
            automated_mappings.extend(lcc_mappings)
        
        logger.info(f"Created {len(automated_mappings)} automated mappings")
        return automated_mappings
    
    def _find_automated_matches(self, lcc_node, fast_subjects: List, fast_by_heading: Dict,
                               fast_keywords: Set, confidence_threshold: int) -> List[CrosswalkMapping]:
        """Find automated matches for a single LCC node."""
        matches = []
        
        lcc_code = lcc_node.class_code
        lcc_label = lcc_node.label.lower() if lcc_node.label else ""
        
        # Method 1: Direct label matching
        if lcc_label in fast_by_heading:
            fast_subject = fast_by_heading[lcc_label]
            matches.append(CrosswalkMapping(
                lcc_code=lcc_code,
                fast_id=fast_subject.fast_id,
                mapping_type='direct',
                confidence_level=95,
                mapping_source='automated_direct_match',
                facet_relevance={fast_subject.facet_type.value: 100},
                scope_notes=f"Direct label match: '{lcc_label}'"
            ))
        
        # Method 2: Keyword overlap scoring
        lcc_keywords = set(lcc_label.split())
        for fast_subject in fast_subjects:
            fast_heading_words = set(fast_subject.heading.lower().split())
            
            # Calculate overlap score
            overlap = lcc_keywords.intersection(fast_heading_words)
            if overlap:
                overlap_score = len(overlap) / max(len(lcc_keywords), len(fast_heading_words))
                confidence = min(int(overlap_score * 100), 90)  # Cap at 90 for automated
                
                if confidence >= confidence_threshold:
                    matches.append(CrosswalkMapping(
                        lcc_code=lcc_code,
                        fast_id=fast_subject.fast_id,
                        mapping_type='approximate',
                        confidence_level=confidence,
                        mapping_source='automated_keyword_match',
                        facet_relevance={fast_subject.facet_type.value: confidence},
                        scope_notes=f"Keyword overlap: {', '.join(overlap)}"
                    ))
        
        # Method 3: Subject pattern matching
        for pattern_name, pattern_info in self.subject_patterns.items():
            for lcc_pattern in pattern_info['lcc_patterns']:
                if re.match(lcc_pattern, lcc_code):
                    # Find FAST subjects matching keywords
                    for keyword in pattern_info['fast_keywords']:
                        for fast_subject in fast_subjects:
                            if keyword in fast_subject.heading.lower():
                                confidence = pattern_info['confidence_base']
                                if fast_subject.facet_type.value in pattern_info['primary_facets']:
                                    confidence += 5
                                
                                matches.append(CrosswalkMapping(
                                    lcc_code=lcc_code,
                                    fast_id=fast_subject.fast_id,
                                    mapping_type='approximate',
                                    confidence_level=min(confidence, 90),
                                    mapping_source=f'automated_pattern_{pattern_name}',
                                    facet_relevance={fast_subject.facet_type.value: confidence},
                                    scope_notes=f"Pattern match: {pattern_name} -> {keyword}"
                                ))
        
        # Remove duplicates and sort by confidence
        unique_matches = {}
        for match in matches:
            key = (match.lcc_code, match.fast_id)
            if key not in unique_matches or match.confidence_level > unique_matches[key].confidence_level:
                unique_matches[key] = match
        
        return list(unique_matches.values())
    
    def load_manual_mappings(self) -> List[CrosswalkMapping]:
        """
        Load manual mappings from the predefined mapping dictionary.
        
        Returns:
            List of manual crosswalk mappings
        """
        logger.info("Loading manual LCC-FAST mappings...")
        manual_mappings = []
        
        for lcc_code, mappings in self.manual_mappings.items():
            manual_mappings.extend(mappings)
        
        logger.info(f"Loaded {len(manual_mappings)} manual mappings")
        return manual_mappings
    
    def save_mappings_to_database(self, mappings: List[CrosswalkMapping]) -> int:
        """
        Save crosswalk mappings to the database.
        
        Args:
            mappings: List of crosswalk mappings to save
            
        Returns:
            Number of mappings successfully saved
        """
        saved_count = 0
        
        with self.db_manager.get_session() as session:
            for mapping in mappings:
                try:
                    crosswalk = self.db_manager.create_crosswalk_mapping(
                        lcc_code=mapping.lcc_code,
                        fast_id=mapping.fast_id,
                        mapping_type=mapping.mapping_type,
                        confidence_level=mapping.confidence_level,
                        mapping_source=mapping.mapping_source,
                        facet_relevance=mapping.facet_relevance,
                        scope_notes=mapping.scope_notes,
                        verified=mapping.verified
                    )
                    
                    if crosswalk:
                        saved_count += 1
                        if saved_count % 100 == 0:
                            logger.info(f"Saved {saved_count} crosswalk mappings...")
                
                except Exception as e:
                    error_msg = f"Failed to save mapping {mapping.lcc_code} -> {mapping.fast_id}: {str(e)}"
                    logger.warning(error_msg)
                    self.stats['errors'].append(error_msg)
        
        return saved_count
    
    def export_mappings_to_file(self, mappings: List[CrosswalkMapping], file_path: str):
        """
        Export crosswalk mappings to a JSON file for review and editing.
        
        Args:
            mappings: List of crosswalk mappings
            file_path: Path to save the JSON file
        """
        export_data = []
        
        for mapping in mappings:
            export_data.append({
                'lcc_code': mapping.lcc_code,
                'fast_id': mapping.fast_id,
                'mapping_type': mapping.mapping_type,
                'confidence_level': mapping.confidence_level,
                'mapping_source': mapping.mapping_source,
                'facet_relevance': mapping.facet_relevance,
                'scope_notes': mapping.scope_notes,
                'verified': mapping.verified,
                'created_at': datetime.now().isoformat()
            })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(export_data)} mappings to {file_path}")
    
    def run_full_crosswalk_build(self, confidence_threshold: int = 70,
                                export_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete crosswalk building process.
        
        Args:
            confidence_threshold: Minimum confidence for automated mappings
            export_file: Optional file path to export mappings
            
        Returns:
            Crosswalk building results and statistics
        """
        logger.info("Starting LCC-FAST crosswalk building...")
        start_time = datetime.now()
        
        try:
            # Step 1: Analyze existing data
            analysis = self.analyze_existing_data()
            
            # Step 2: Load manual mappings
            manual_mappings = self.load_manual_mappings()
            self.stats['manual_mappings'] = len(manual_mappings)
            
            # Step 3: Create automated mappings
            automated_mappings = self.create_automated_mappings(confidence_threshold)
            
            # Count mapping types
            for mapping in automated_mappings:
                if mapping.mapping_type == 'direct':
                    self.stats['direct_matches'] += 1
                elif mapping.mapping_type == 'approximate':
                    self.stats['approximate_matches'] += 1
            
            # Step 4: Combine all mappings
            all_mappings = manual_mappings + automated_mappings
            
            # Step 5: Save to database
            saved_count = self.save_mappings_to_database(all_mappings)
            self.stats['mappings_created'] = saved_count
            
            # Step 6: Export to file if requested
            if export_file:
                self.export_mappings_to_file(all_mappings, export_file)
            
            # Final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results = {
                'analysis': analysis,
                'statistics': self.stats,
                'total_mappings': len(all_mappings),
                'saved_mappings': saved_count,
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'success': True
            }
            
            logger.info(f"Crosswalk building completed in {duration:.2f} seconds")
            logger.info(f"Created {saved_count} mappings: {self.stats['manual_mappings']} manual, "
                       f"{self.stats['direct_matches']} direct, {self.stats['approximate_matches']} approximate")
            
            return results
            
        except Exception as e:
            error_msg = f"Crosswalk building failed: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            
            return {
                'statistics': self.stats,
                'success': False,
                'error': error_msg
            }

def main():
    """Main function for running crosswalk building."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build LCC-FAST crosswalk mappings')
    parser.add_argument('--confidence-threshold', type=int, default=70,
                       help='Minimum confidence level for automated mappings')
    parser.add_argument('--export-file', 
                       help='Export mappings to JSON file for review')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze data without creating mappings')
    
    args = parser.parse_args()
    
    # Initialize crosswalk builder
    builder = LCCFASTCrosswalkBuilder()
    
    if args.analyze_only:
        # Run analysis only
        analysis = builder.analyze_existing_data()
        print("\nLCC-FAST Data Analysis:")
        print("=" * 50)
        print(f"LCC Main Classes: {analysis['lcc_main_classes']}")
        print(f"FAST Facet Distribution: {analysis['fast_facet_distribution']}")
        print(f"Recommendations: {analysis['recommended_approach']}")
    else:
        # Run full crosswalk building
        results = builder.run_full_crosswalk_build(
            confidence_threshold=args.confidence_threshold,
            export_file=args.export_file
        )
        
        # Print results
        print("\nLCC-FAST Crosswalk Building Results:")
        print("=" * 50)
        print(f"Success: {results.get('success', False)}")
        print(f"Total Mappings Created: {results.get('total_mappings', 0)}")
        print(f"Saved to Database: {results.get('saved_mappings', 0)}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
        
        if results.get('statistics'):
            stats = results['statistics']
            print(f"\nMapping Types:")
            print(f"  Manual: {stats.get('manual_mappings', 0)}")
            print(f"  Direct: {stats.get('direct_matches', 0)}")
            print(f"  Approximate: {stats.get('approximate_matches', 0)}")
            
            if stats.get('errors'):
                print(f"\nErrors: {len(stats['errors'])}")
                for error in stats['errors'][:3]:
                    print(f"  • {error}")

if __name__ == "__main__":
    main()