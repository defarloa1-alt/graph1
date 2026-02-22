"""
LCC to Chrystallum Facet Mapper

Uses local LCSH and LCC datasets to map subjects to Chrystallum's 16 domain facets
plus Communication meta-facet.

Architecture:
- 16 Domain Facets: Military, Political, Social, etc.
- 1 Meta-Facet: Communication (cross-cutting dimension)

Data sources:
- FAST: MARCXML (/fast)
- LCSH: JSON-LD chunks (/lcsh/skos_subjects/chunks)
- LCC: JSON files (/subjects/lcc)

Author: Chrystallum Project
Date: 2026-02-15
Version: 1.1.0 (Meta-facet architecture)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class LCCFacetMapper:
    """
    Maps Library of Congress Classification codes to Chrystallum domain facets
    and detects Communication meta-facet dimension
    
    Architecture:
    - 16 Domain Facets (Military, Political, Social, etc.)
    - 1 Meta-Facet (Communication - cross-cutting dimension)
    """
    
    # Communication detection constants
    COMMUNICATION_KEYWORDS = {
        'direct_terms': [
            'rhetoric', 'oratory', 'propaganda', 'persuasion',
            'speech', 'oration', 'discourse', 'communication',
            'rhetoric', 'oratorical', 'persuade', 'incite'
        ],
        'medium_terms': [
            'oral', 'written', 'visual', 'inscription', 
            'letter', 'edict', 'proclamation', 'coin', 
            'monument', 'statue', 'ritual', 'ceremony'
        ],
        'purpose_terms': [
            'propaganda', 'incite', 'persuade', 'legitimize',
            'justify', 'denounce', 'praise', 'promote', 
            'condemn', 'commemorate', 'mobilize'
        ],
        'strategy_terms': [
            'ethos', 'pathos', 'logos', 'invective', 
            'exemplum', 'spectacle', 'display', 'appeal'
        ]
    }
    
    # LCC ranges with high communication primacy
    DIRECT_COMMUNICATION_LCC = {
        'PN4001-PN4355': 1.0,   # Oratory - pure communication
        'PN4400-PN4500': 1.0,   # Journalism - pure communication
        'PA6087-PA6099': 1.0,   # Latin rhetoric - pure communication
        'HM1206-HM1211': 0.95,  # Social influence - communication-heavy
        'JF1525.P8': 0.95,      # Public opinion - communication-heavy
        'JF2112': 0.95,         # Political campaigns - communication-heavy
    }
    
    # LCC ranges with moderate communication dimension
    COMMUNICATION_DIMENSION_LCC = {
        'DG341-DG345': 0.70,  # Intellectual life - has communication dimension
        'DG346-DG350': 0.60,  # Religion - ritual communication
        'DG351-DG355': 0.65,  # Art - visual messaging
        'PA8001-PA8595': 0.50, # Latin literature - has communication purpose
        'CJ': 0.60,           # Numismatics - coin messaging
        'NA': 0.55,           # Architecture - spatial communication
    }
    
    def __init__(self, mapping_file: str = "lcc_to_chrystallum_facets.json"):
        """
        Initialize mapper with LCC → Facet mapping file
        
        Args:
            mapping_file: Path to JSON mapping file
        """
        with open(mapping_file, 'r') as f:
            self.mapping_data = json.load(f)
        
        self.mappings = self.mapping_data['mappings']
        self.facets = self.mapping_data['metadata']['facets']
    
    def get_facets_from_lcc(self, lcc: str, label: str = "") -> Dict[str, any]:
        """
        Get Chrystallum domain facets and communication dimension for a given LCC code
        
        Args:
            lcc: LCC code (e.g., "DG247", "KJA500")
            label: Subject label for communication detection (optional)
        
        Returns:
            {
                'domain_facets': List[str],  # Original 16 facets
                'confidence': float,
                'lcc_range': str,
                'label': str,
                'method': str,
                'communication': {  # Meta-facet dimension
                    'has_dimension': bool,
                    'primacy': float (0-1),
                    'medium': List[str],
                    'purpose': List[str],
                    'audience': List[str],
                    'strategy': List[str]
                }
            }
        """
        
        if not lcc:
            return self._fallback_result("No LCC provided")
        
        # Extract LCC prefix and number
        lcc_prefix = ''.join([c for c in lcc if c.isalpha()])
        lcc_number = ''.join([c for c in lcc if c.isdigit()])
        lcc_num = int(lcc_number) if lcc_number else 0
        
        # Check if prefix exists in mappings
        if lcc_prefix not in self.mappings:
            result = self._fallback_result(f"LCC prefix '{lcc_prefix}' not in mapping")
        else:
            mapping = self.mappings[lcc_prefix]
            
            # Check for specific range matches (highest priority)
            if 'ranges' in mapping:
                range_match = self._find_matching_range(lcc, lcc_prefix, lcc_num, mapping['ranges'])
                if range_match:
                    result = range_match
                else:
                    # Use default facets for this prefix
                    result = {
                        'domain_facets': mapping['default_facets'],
                        'confidence': 0.85,
                        'lcc_range': lcc_prefix,
                        'label': mapping.get('label', lcc_prefix),
                        'method': 'lcc_prefix'
                    }
            else:
                # Use default facets for this prefix
                result = {
                    'domain_facets': mapping['default_facets'],
                    'confidence': 0.85,
                    'lcc_range': lcc_prefix,
                    'label': mapping.get('label', lcc_prefix),
                    'method': 'lcc_prefix'
                }
        
        # Detect communication dimension
        communication = self.detect_communication_dimension(lcc, label)
        result['communication'] = communication
        
        return result
    
    def _find_matching_range(self, lcc: str, lcc_prefix: str, lcc_num: int, ranges: Dict) -> Optional[Dict]:
        """
        Find the most specific matching LCC range
        
        Args:
            lcc: Full LCC code
            lcc_prefix: Letter prefix
            lcc_num: Numeric portion
            ranges: Dictionary of LCC ranges
        
        Returns:
            Matching facet assignment or None
        """
        
        # Sort ranges by specificity (more specific = longer range string)
        sorted_ranges = sorted(ranges.items(), key=lambda x: len(x[0]), reverse=True)
        
        for range_key, range_data in sorted_ranges:
            if self._lcc_in_range(lcc, lcc_prefix, lcc_num, range_key):
                return {
                    'domain_facets': range_data['facets'],
                    'confidence': range_data.get('confidence', 0.95),
                    'lcc_range': range_key,
                    'label': range_data.get('label', range_key),
                    'method': 'lcc_range_specific'
                }
        
        return None
    
    def _lcc_in_range(self, lcc: str, lcc_prefix: str, lcc_num: int, range_key: str) -> bool:
        """
        Check if LCC falls within a specified range
        
        Args:
            lcc: Full LCC code (e.g., "DG247")
            lcc_prefix: Letter prefix (e.g., "DG")
            lcc_num: Numeric portion (e.g., 247)
            range_key: Range specification (e.g., "DG231-DG248" or "DG247")
        
        Returns:
            True if LCC is in range, False otherwise
        """
        
        # Handle exact match (e.g., "DG247")
        if range_key == lcc:
            return True
        
        # Handle single LCC code (no range)
        if '-' not in range_key:
            return lcc == range_key
        
        # Handle range (e.g., "DG231-DG248")
        start_str, end_str = range_key.split('-')
        
        # Extract components
        start_prefix = ''.join([c for c in start_str if c.isalpha()])
        start_num = int(''.join([c for c in start_str if c.isdigit()]) or 0)
        
        end_prefix = ''.join([c for c in end_str if c.isalpha()])
        end_num = int(''.join([c for c in end_str if c.isdigit()]) or 0)
        
        # Check prefix matches
        if lcc_prefix != start_prefix or lcc_prefix != end_prefix:
            return False
        
        # Check numeric range
        return start_num <= lcc_num <= end_num
    
    def _fallback_result(self, reason: str) -> Dict:
        """
        Return fallback facet assignment
        """
        return {
            'domain_facets': ['Social'],  # Default fallback
            'confidence': 0.50,
            'lcc_range': 'unknown',
            'label': 'Unknown classification',
            'method': 'fallback',
            'reason': reason,
            'communication': {
                'has_dimension': False,
                'primacy': 0.0,
                'medium': [],
                'purpose': [],
                'audience': [],
                'strategy': []
            }
        }
    
    def detect_communication_dimension(self, lcc: str, label: str) -> Dict:
        """
        Detect communication meta-facet dimension
        
        Args:
            lcc: LCC code
            label: Subject label
        
        Returns:
            {
                'has_dimension': bool,
                'primacy': float (0-1),
                'medium': List[str],
                'purpose': List[str],
                'audience': List[str],
                'strategy': List[str]
            }
        """
        
        primacy_score = 0.0
        
        # Signal 1: LCC-based detection (40% weight)
        lcc_score = self._lcc_communication_score(lcc)
        primacy_score += lcc_score * 0.40
        
        # Signal 2: Keyword detection (30% weight)
        if label:
            keyword_score = self._keyword_communication_score(label)
            primacy_score += keyword_score * 0.30
        
        # Signal 3: Medium + Purpose pattern (30% weight)
        if label:
            pattern_score = self._pattern_communication_score(label)
            primacy_score += pattern_score * 0.30
        
        # Normalize to 0-1
        primacy = min(primacy_score, 1.0)
        
        # Extract dimensions if communication is present
        if primacy >= 0.5:
            medium = self._detect_medium(lcc, label)
            purpose = self._detect_purpose(label)
            audience = self._infer_audience(label)
            strategy = self._detect_strategy(label)
            
            return {
                'has_dimension': True,
                'primacy': round(primacy, 2),
                'medium': medium,
                'purpose': purpose,
                'audience': audience,
                'strategy': strategy
            }
        else:
            return {
                'has_dimension': False,
                'primacy': round(primacy, 2),
                'medium': [],
                'purpose': [],
                'audience': [],
                'strategy': []
            }
    
    def _lcc_communication_score(self, lcc: str) -> float:
        """
        Score communication primacy based on LCC
        
        Returns: 0.0-1.0 score
        """
        
        # Check direct communication ranges
        for lcc_range, score in self.DIRECT_COMMUNICATION_LCC.items():
            if self._matches_lcc_pattern(lcc, lcc_range):
                return score
        
        # Check communication dimension ranges
        for lcc_range, score in self.COMMUNICATION_DIMENSION_LCC.items():
            if self._matches_lcc_pattern(lcc, lcc_range):
                return score
        
        return 0.0
    
    def _keyword_communication_score(self, label: str) -> float:
        """
        Score communication primacy based on keywords
        
        Returns: 0.0-1.0 score
        """
        
        label_lower = label.lower()
        
        # Direct communication terms → high score
        for term in self.COMMUNICATION_KEYWORDS['direct_terms']:
            if term in label_lower:
                return 1.0
        
        return 0.0
    
    def _pattern_communication_score(self, label: str) -> float:
        """
        Score based on medium + purpose patterns
        
        Returns: 0.0-1.0 score
        """
        
        label_lower = label.lower()
        
        has_medium = any(term in label_lower 
                        for term in self.COMMUNICATION_KEYWORDS['medium_terms'])
        has_purpose = any(term in label_lower 
                         for term in self.COMMUNICATION_KEYWORDS['purpose_terms'])
        
        if has_medium and has_purpose:
            return 0.80
        elif has_medium:
            return 0.40
        elif has_purpose:
            return 0.50
        
        return 0.0
    
    def _detect_medium(self, lcc: str, label: str) -> List[str]:
        """
        Detect communication medium
        """
        media = []
        
        if label:
            label_lower = label.lower()
            
            medium_patterns = {
                'oral': ['speech', 'oration', 'oratory', 'oral', 'spoken', 'rumor', 'fama'],
                'written': ['letter', 'edict', 'inscription', 'text', 'written', 'commentari'],
                'visual': ['coin', 'monument', 'statue', 'relief', 'image', 'visual', 'triumph'],
                'performative': ['ritual', 'ceremony', 'spectacle', 'theater', 'game', 'performance'],
                'architectural': ['building', 'temple', 'forum', 'arch', 'column', 'structure']
            }
            
            for medium, keywords in medium_patterns.items():
                if any(kw in label_lower for kw in keywords):
                    media.append(medium)
        
        # Fallback: infer from LCC if no label match
        if not media and lcc:
            lcc_prefix = ''.join([c for c in lcc if c.isalpha()])
            
            if lcc_prefix.startswith('PN4'):  # Oratory
                media.append('oral')
            elif lcc_prefix.startswith('PA'):  # Literature
                media.append('written')
            elif lcc_prefix == 'CJ':  # Numismatics
                media.append('visual')
            elif lcc_prefix == 'NA':  # Architecture
                media.append('architectural')
        
        return media
    
    def _detect_purpose(self, label: str) -> List[str]:
        """
        Detect communication purpose
        """
        if not label:
            return []
        
        purposes = []
        label_lower = label.lower()
        
        purpose_keywords = {
            'propaganda': ['propaganda', 'promote', 'glorify', 'celebrate'],
            'persuasion': ['persuade', 'convince', 'argue', 'debate'],
            'incitement': ['incite', 'provoke', 'rouse', 'mobilize'],
            'legitimation': ['legitimize', 'justify', 'authorize', 'validate'],
            'information': ['inform', 'report', 'announce', 'communicate'],
            'memory': ['commemorate', 'memorialize', 'remember', 'preserve'],
            'ideology': ['ideology', 'belief', 'doctrine', 'worldview']
        }
        
        for purpose, keywords in purpose_keywords.items():
            if any(kw in label_lower for kw in keywords):
                purposes.append(purpose)
        
        return purposes
    
    def _infer_audience(self, label: str) -> List[str]:
        """
        Infer intended audience
        """
        if not label:
            return []
        
        audiences = []
        label_lower = label.lower()
        
        audience_indicators = {
            'Senate': ['senate', 'senatorial', 'senator'],
            'Roman people': ['people', 'popular', 'public', 'citizen', 'contio'],
            'Military': ['army', 'legion', 'soldier', 'troop', 'veteran'],
            'Posterity': ['monument', 'inscription', 'commemorate', 'memory']
        }
        
        for audience, keywords in audience_indicators.items():
            if any(kw in label_lower for kw in keywords):
                audiences.append(audience)
        
        return audiences
    
    def _detect_strategy(self, label: str) -> List[str]:
        """
        Detect rhetorical/communicative strategy
        """
        if not label:
            return []
        
        strategies = []
        label_lower = label.lower()
        
        strategy_keywords = {
            'ethos': ['authority', 'credibility', 'character', 'reputation'],
            'pathos': ['emotion', 'fear', 'pity', 'anger', 'grief'],
            'logos': ['argument', 'logic', 'reason', 'evidence', 'proof'],
            'invective': ['attack', 'denounce', 'condemn', 'abuse', 'mock'],
            'exemplarity': ['example', 'precedent', 'ancestor', 'model'],
            'spectacle': ['display', 'show', 'spectacle', 'triumph', 'ceremony']
        }
        
        for strategy, keywords in strategy_keywords.items():
            if any(kw in label_lower for kw in keywords):
                strategies.append(strategy)
        
        return strategies
    
    def _matches_lcc_pattern(self, lcc: str, pattern: str) -> bool:
        """
        Check if LCC matches a pattern (exact or range)
        """
        if '-' in pattern:
            # Range pattern
            parts = pattern.split('-')
            if len(parts) == 2:
                start, end = parts
                lcc_prefix = ''.join([c for c in lcc if c.isalpha()])
                lcc_num = int(''.join([c for c in lcc if c.isdigit()]) or 0)
                return self._lcc_in_range(lcc, lcc_prefix, lcc_num, pattern)
        else:
            # Exact or prefix match
            return lcc.startswith(pattern)
        
        return False
    
    def batch_lookup(self, lcc_codes: List[str]) -> Dict[str, Dict]:
        """
        Batch lookup for multiple LCC codes
        
        Args:
            lcc_codes: List of LCC codes
        
        Returns:
            Dictionary mapping LCC code to facet assignment
        """
        results = {}
        for lcc in lcc_codes:
            results[lcc] = self.get_facets_from_lcc(lcc)
        return results


class LocalDatasetIntegrator:
    """
    Integrates local FAST, LCSH, and LCC datasets
    """
    
    def __init__(self, 
                 fast_dir: str = "/fast",
                 lcsh_dir: str = "/lcsh/skos_subjects/chunks",
                 lcc_dir: str = "/subjects/lcc"):
        """
        Initialize with local dataset directories
        """
        self.fast_dir = Path(fast_dir)
        self.lcsh_dir = Path(lcsh_dir)
        self.lcc_dir = Path(lcc_dir)
        
        self.facet_mapper = LCCFacetMapper()
    
    def load_lcsh_chunks(self) -> Dict:
        """
        Load LCSH JSON-LD chunks from local directory
        
        Returns:
            Dictionary mapping LCSH ID to record
        """
        lcsh_data = {}
        
        if not self.lcsh_dir.exists():
            print(f"Warning: LCSH directory not found: {self.lcsh_dir}")
            return lcsh_data
        
        # Load all JSON-LD chunk files
        for chunk_file in self.lcsh_dir.glob("*.jsonld"):
            try:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    
                    # Process JSON-LD format
                    if isinstance(chunk_data, list):
                        for item in chunk_data:
                            lcsh_id = self._extract_lcsh_id(item)
                            if lcsh_id:
                                lcsh_data[lcsh_id] = item
                    elif isinstance(chunk_data, dict):
                        lcsh_id = self._extract_lcsh_id(chunk_data)
                        if lcsh_id:
                            lcsh_data[lcsh_id] = chunk_data
            
            except Exception as e:
                print(f"Error loading {chunk_file}: {e}")
        
        print(f"Loaded {len(lcsh_data)} LCSH records from {self.lcsh_dir}")
        return lcsh_data
    
    def load_lcc_data(self) -> Dict:
        """
        Load LCC JSON files from local directory
        
        Returns:
            Dictionary mapping LCC code to metadata
        """
        lcc_data = {}
        
        if not self.lcc_dir.exists():
            print(f"Warning: LCC directory not found: {self.lcc_dir}")
            return lcc_data
        
        # Load all JSON files
        for lcc_file in self.lcc_dir.glob("*.json"):
            try:
                with open(lcc_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle different JSON structures
                    if isinstance(data, dict):
                        lcc_code = data.get('lcc') or data.get('classification')
                        if lcc_code:
                            lcc_data[lcc_code] = data
                    elif isinstance(data, list):
                        for item in data:
                            lcc_code = item.get('lcc') or item.get('classification')
                            if lcc_code:
                                lcc_data[lcc_code] = item
            
            except Exception as e:
                print(f"Error loading {lcc_file}: {e}")
        
        print(f"Loaded {len(lcc_data)} LCC records from {self.lcc_dir}")
        return lcc_data
    
    def _extract_lcsh_id(self, item: Dict) -> Optional[str]:
        """
        Extract LCSH ID from JSON-LD record
        
        Common formats:
        - "@id": "http://id.loc.gov/authorities/subjects/sh85109214"
        - "id": "sh85109214"
        """
        
        # Try @id field (JSON-LD standard)
        if '@id' in item:
            uri = item['@id']
            if 'subjects/' in uri:
                return uri.split('subjects/')[-1]
        
        # Try direct id field
        if 'id' in item:
            return item['id']
        
        # Try identifier field
        if 'identifier' in item:
            return item['identifier']
        
        return None
    
    def enrich_subject_with_facets(self, lcsh_id: str, lcsh_data: Dict) -> Dict:
        """
        Enrich LCSH subject with Chrystallum facets
        
        Args:
            lcsh_id: LCSH identifier (e.g., "sh85109214")
            lcsh_data: Dictionary of loaded LCSH records
        
        Returns:
            Enriched subject record with facets
        """
        
        if lcsh_id not in lcsh_data:
            return {
                'lcsh_id': lcsh_id,
                'error': 'LCSH ID not found in local data'
            }
        
        lcsh_record = lcsh_data[lcsh_id]
        
        # Extract LCC from LCSH record
        lcc = self._extract_lcc_from_lcsh(lcsh_record)
        
        # Get facets from LCC
        facet_assignment = self.facet_mapper.get_facets_from_lcc(lcc)
        
        # Build enriched record
        enriched = {
            'lcsh_id': lcsh_id,
            'lcc': lcc,
            'label': self._extract_label(lcsh_record),
            'chrystallum_facets': facet_assignment['facets'],
            'facet_confidence': facet_assignment['confidence'],
            'lcc_range': facet_assignment['lcc_range'],
            'lcc_range_label': facet_assignment['label'],
            'mapping_method': facet_assignment['method']
        }
        
        return enriched
    
    def _extract_lcc_from_lcsh(self, lcsh_record: Dict) -> Optional[str]:
        """
        Extract LCC classification from LCSH JSON-LD record
        
        Common fields:
        - "classification": "DG247"
        - "lcc": "DG247"
        - "skos:notation": "DG247"
        """
        
        # Try direct fields
        for field in ['classification', 'lcc', 'Classification']:
            if field in lcsh_record:
                return lcsh_record[field]
        
        # Try SKOS notation
        if 'skos:notation' in lcsh_record:
            return lcsh_record['skos:notation']
        
        # Try nested structures
        if 'hasClassification' in lcsh_record:
            classifications = lcsh_record['hasClassification']
            if isinstance(classifications, list) and classifications:
                return classifications[0]
            elif isinstance(classifications, str):
                return classifications
        
        return None
    
    def _extract_label(self, lcsh_record: Dict) -> str:
        """
        Extract human-readable label from LCSH record
        """
        
        # Try common label fields
        for field in ['label', 'prefLabel', 'skos:prefLabel', 'title', 'heading']:
            if field in lcsh_record:
                label = lcsh_record[field]
                if isinstance(label, list):
                    return label[0]
                return label
        
        # Try @value in JSON-LD
        if 'rdfs:label' in lcsh_record:
            label_obj = lcsh_record['rdfs:label']
            if isinstance(label_obj, dict) and '@value' in label_obj:
                return label_obj['@value']
        
        return "Unknown"


# ============================================================
# USAGE EXAMPLES
# ============================================================

if __name__ == "__main__":
    
    # Example 1: Direct LCC to Facet mapping
    print("=" * 60)
    print("Example 1: LCC to Facet Mapping")
    print("=" * 60)
    
    mapper = LCCFacetMapper()
    
    test_lcc_codes = [
        "DG247",     # Punic Wars
        "DG247.3",   # Second Punic War
        "DG233",     # Roman Republic constitution
        "KJA500",    # Roman law - persons
        "PA8001",    # Latin literature
        "BL820",     # Roman religion
        "NA310",     # Roman architecture
    ]
    
    for lcc in test_lcc_codes:
        result = mapper.get_facets_from_lcc(lcc)
        print(f"\n{lcc}: {result['label']}")
        print(f"  Facets: {', '.join(result['facets'])}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Method: {result['method']}")
    
    # Example 2: Batch lookup
    print("\n" + "=" * 60)
    print("Example 2: Batch Lookup")
    print("=" * 60)
    
    batch_results = mapper.batch_lookup(test_lcc_codes)
    
    # Group by facet
    facet_groups = {}
    for lcc, result in batch_results.items():
        for facet in result['facets']:
            if facet not in facet_groups:
                facet_groups[facet] = []
            facet_groups[facet].append(lcc)
    
    print("\nLCC codes grouped by Chrystallum facet:")
    for facet, lcc_codes in sorted(facet_groups.items()):
        print(f"\n{facet}:")
        for lcc in lcc_codes:
            print(f"  - {lcc}: {batch_results[lcc]['label']}")
    
    # Example 3: Integration with local datasets (if available)
    print("\n" + "=" * 60)
    print("Example 3: Local Dataset Integration")
    print("=" * 60)
    
    try:
        integrator = LocalDatasetIntegrator()
        
        # Load local data
        lcsh_data = integrator.load_lcsh_chunks()
        lcc_data = integrator.load_lcc_data()
        
        # Example enrichment
        if lcsh_data:
            sample_lcsh_id = list(lcsh_data.keys())[0]
            enriched = integrator.enrich_subject_with_facets(sample_lcsh_id, lcsh_data)
            
            print(f"\nEnriched subject example:")
            print(json.dumps(enriched, indent=2))
    
    except Exception as e:
        print(f"\nLocal datasets not available: {e}")
        print("To use local integration, ensure datasets are in:")
        print("  - /fast (MARCXML)")
        print("  - /lcsh/skos_subjects/chunks (JSON-LD)")
        print("  - /subjects/lcc (JSON)")
