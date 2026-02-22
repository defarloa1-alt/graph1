#!/usr/bin/env python3
"""
Federation Scorer - What+When+Where Subgraph Pattern

Scores entities based on federation completeness and generates
cipher keys for vertex jump navigation.

Design: Cipher = primary key to what+when+where subgraph concept
Purpose: Enable agent vertex jumping across Place→Period→Place dimensions
"""

import hashlib
from typing import Dict, Optional


class FederationScorer:
    """Score federation completeness for vertex jump patterns"""
    
    # Scoring weights (total = 100)
    WEIGHTS = {
        'place_qid': 30,        # What: Place federated to Wikidata
        'period_qid': 30,       # When: Period federated to Wikidata  
        'geo_context_qid': 20,  # Where: Geographic context federated
        'temporal_bounds': 15,  # Temporal signal present
        'relationships': 5      # Vertex jump edges exist
    }
    
    # Federation states
    STATES = {
        'FS0_UNFEDERATED': (0, 39),
        'FS1_BASE': (40, 59),
        'FS2_FEDERATED': (60, 79),
        'FS3_WELL_FEDERATED': (80, 100)
    }
    
    def score_place_period_subgraph(
        self,
        place_node: Dict,
        period_node: Optional[Dict] = None,
        geo_context_node: Optional[Dict] = None
    ) -> Dict:
        """
        Score a what+when+where subgraph.
        
        Args:
            place_node: Place dict with properties (WHAT)
            period_node: Period dict with properties (WHEN) - optional
            geo_context_node: Parent Place dict (WHERE) - optional
        
        Returns:
            {
                'federation_score': int (0-100),
                'federation_state': str,
                'federation_cipher_key': str,
                'vertex_jump_enabled': bool,
                'what_qid': str or None,
                'when_qid': str or None,
                'where_qid': str or None
            }
        """
        score = 0
        
        # WHAT: Place has QID?
        what_qid = place_node.get('qid')
        if what_qid:
            score += self.WEIGHTS['place_qid']
        
        # WHEN: Period has QID?
        when_qid = period_node.get('qid') if period_node else None
        when_periodo = period_node.get('periodo_id') if period_node else None
        if when_qid:
            score += self.WEIGHTS['period_qid']
        elif when_periodo:
            score += self.WEIGHTS['period_qid'] // 2  # Half credit for periodo without qid
        
        # WHERE: Geographic context has QID?
        where_qid = geo_context_node.get('qid') if geo_context_node else None
        if where_qid:
            score += self.WEIGHTS['geo_context_qid']
        
        # Temporal bounds present?
        has_temporal = bool(
            place_node.get('min_date') or place_node.get('max_date') or
            (period_node and (period_node.get('start_year') or period_node.get('start')))
        )
        if has_temporal:
            score += self.WEIGHTS['temporal_bounds']
        
        # Relationships exist? (can we vertex jump?)
        has_relationships = bool(period_node and geo_context_node)
        if has_relationships:
            score += self.WEIGHTS['relationships']
        
        # Determine state
        state = self._get_state(score)
        
        # Generate cipher (subgraph primary key)
        cipher = self._generate_cipher(
            what_qid or place_node.get('pleiades_id'),
            when_qid or when_periodo,
            where_qid
        )
        
        # Can agents vertex jump?
        vertex_jump_enabled = bool(what_qid and (when_qid or when_periodo))
        
        return {
            'federation_score': score,
            'federation_state': state,
            'federation_cipher_key': cipher,
            'vertex_jump_enabled': vertex_jump_enabled,
            'what_qid': what_qid,
            'when_qid': when_qid,
            'where_qid': where_qid,
            'has_temporal': has_temporal,
            'has_relationships': has_relationships
        }
    
    def score_place_simple(self, place_node: Dict) -> Dict:
        """
        Score a standalone Place (no period/context yet).
        
        This is for initial place loading before relationships exist.
        """
        score = 0
        
        # Has Pleiades ID? (always yes for our data)
        if place_node.get('pleiades_id'):
            score += 20
        
        # Has Wikidata QID?
        has_qid = bool(place_node.get('qid'))
        if has_qid:
            score += 50
        
        # Has temporal bounds?
        has_temporal = bool(place_node.get('min_date') or place_node.get('max_date'))
        if has_temporal:
            score += 20
        
        # Has coordinates?
        has_coords = bool(place_node.get('lat') and place_node.get('long'))
        if has_coords:
            score += 10
        
        state = self._get_state(score)
        
        # Simple cipher (just the place)
        pleiades = place_node.get('pleiades_id') or 'NULL'
        qid = place_node.get('qid') or 'NULL'
        cipher = f"place|{qid}|{pleiades}"
        
        return {
            'federation_score': score,
            'federation_state': state,
            'federation_cipher_key': cipher,
            'vertex_jump_enabled': has_qid,  # Can jump if has QID
            'has_qid': has_qid,
            'has_temporal': has_temporal,
            'has_coords': has_coords
        }
    
    def score_period_simple(self, period_node: Dict) -> Dict:
        """Score a standalone Period."""
        score = 0
        
        # Has PeriodO ID? (always yes for our data)
        if period_node.get('authority') == 'PeriodO' or period_node.get('periodo_id'):
            score += 30
        
        # Has Wikidata QID?
        has_qid = bool(period_node.get('qid'))
        if has_qid:
            score += 50
        
        # Has temporal bounds?
        has_temporal = bool(
            period_node.get('start_year') or period_node.get('start') or
            period_node.get('end_year') or period_node.get('end')
        )
        if has_temporal:
            score += 20
        
        state = self._get_state(score)
        
        # Simple cipher
        periodo = period_node.get('periodo_id') or period_node.get('authority_uri') or 'NULL'
        qid = period_node.get('qid') or 'NULL'
        cipher = f"period|{qid}|{periodo}"
        
        return {
            'federation_score': score,
            'federation_state': state,
            'federation_cipher_key': cipher,
            'vertex_jump_enabled': has_qid,
            'has_qid': has_qid,
            'has_temporal': has_temporal
        }
    
    def _get_state(self, score: int) -> str:
        """Map score to federation state."""
        for state_name, (min_score, max_score) in self.STATES.items():
            if min_score <= score <= max_score:
                return state_name
        return 'FS0_UNFEDERATED'
    
    def _generate_cipher(self, what_id, when_id, where_id) -> str:
        """
        Generate federation cipher for subgraph.
        
        Cipher = primary key to what+when+where concept subgraph
        Format: <what>|<when>|<where>
        """
        what = what_id or 'NULL'
        when = when_id or 'NULL'
        where = where_id or 'NULL'
        
        # Raw cipher
        raw = f"{what}|{when}|{where}"
        
        # Hash for deterministic short key
        hash_key = hashlib.sha256(raw.encode()).hexdigest()[:16]
        
        return f"fed_{hash_key}"  # Short deterministic key
    
    def score_subject_concept(self, concept_node: Dict) -> Dict:
        """
        Score a SubjectConcept node based on library authority federation.
        
        Args:
            concept_node: SubjectConcept dict with properties
        
        Returns:
            {
                'authority_federation_score': int (0-100),
                'authority_federation_state': str,
                'authority_federation_cipher': str,
                'authority_jump_enabled': bool,
                'has_lcsh': bool,
                'has_fast': bool,
                'has_lcc': bool,
                'has_qid': bool
            }
        """
        score = 0
        
        # LCSH (Library of Congress Subject Headings)
        has_lcsh = bool(concept_node.get('lcsh_id'))
        if has_lcsh:
            score += 30
        
        # FAST (Faceted Application of Subject Terminology)
        has_fast = bool(concept_node.get('fast_id'))
        if has_fast:
            score += 30
        
        # LCC (Library of Congress Classification)
        has_lcc = bool(concept_node.get('lcc_class'))
        if has_lcc:
            score += 20
        
        # Wikidata QID
        has_qid = bool(concept_node.get('qid'))
        if has_qid:
            score += 20
        
        # Determine state
        state = self._get_state(score)
        
        # Generate authority cipher
        lcsh = concept_node.get('lcsh_id') or 'NULL'
        fast = concept_node.get('fast_id') or 'NULL'
        lcc = concept_node.get('lcc_class') or 'NULL'
        qid = concept_node.get('qid') or 'NULL'
        
        raw_cipher = f"auth|{lcsh}|{fast}|{lcc}|{qid}"
        hash_key = hashlib.sha256(raw_cipher.encode()).hexdigest()[:16]
        cipher = f"auth_fed_{hash_key}"
        
        # Can jump to library authorities if has LCSH or FAST
        authority_jump = has_lcsh or has_fast
        
        return {
            'authority_federation_score': score,
            'authority_federation_state': state,
            'authority_federation_cipher': cipher,
            'authority_jump_enabled': authority_jump,
            'has_lcsh': has_lcsh,
            'has_fast': has_fast,
            'has_lcc': has_lcc,
            'has_qid': has_qid
        }


# Example usage
if __name__ == "__main__":
    scorer = FederationScorer()
    
    # Example: Rome during Roman Republic in Italy
    place = {
        'qid': 'Q220',
        'pleiades_id': '423025',
        'label': 'Rome',
        'min_date': -753,
        'max_date': 2025,
        'lat': 41.89,
        'long': 12.51
    }
    
    period = {
        'qid': 'Q17167',
        'periodo_id': 'romano.roman_republic.1',
        'label': 'Roman Republic',
        'start_year': -509,
        'end_year': -27
    }
    
    geo_context = {
        'qid': 'Q1263',
        'label': 'Italy'
    }
    
    # Score the complete subgraph
    result = scorer.score_place_period_subgraph(place, period, geo_context)
    
    print("Subgraph: Rome during Roman Republic in Italy")
    print(f"  Federation score: {result['federation_score']}")
    print(f"  State: {result['federation_state']}")
    print(f"  Cipher: {result['federation_cipher_key']}")
    print(f"  Vertex jump enabled: {result['vertex_jump_enabled']}")
    print(f"  What (Place): {result['what_qid']}")
    print(f"  When (Period): {result['when_qid']}")
    print(f"  Where (Context): {result['where_qid']}")
    
    print("\n" + "=" * 60)
    print("Example 2: SubjectConcept with library authorities")
    print("=" * 60)
    
    # Example: SubjectConcept with full authority federation
    concept = {
        'subject_id': 'subj_rr_governance',
        'label': 'Government and Constitutional Structure',
        'lcsh_id': 'sh85115055',
        'fast_id': 'fst01204885',
        'lcc_class': 'DG254',
        'qid': 'Q17167'
    }
    
    result = scorer.score_subject_concept(concept)
    
    print("Concept: Government and Constitutional Structure")
    print(f"  Authority federation score: {result['authority_federation_score']}")
    print(f"  State: {result['authority_federation_state']}")
    print(f"  Cipher: {result['authority_federation_cipher']}")
    print(f"  Authority jump enabled: {result['authority_jump_enabled']}")
    print(f"  Has LCSH: {result['has_lcsh']}")
    print(f"  Has FAST: {result['has_fast']}")
    print(f"  Has LCC: {result['has_lcc']}")
    print(f"  Has QID: {result['has_qid']}")

