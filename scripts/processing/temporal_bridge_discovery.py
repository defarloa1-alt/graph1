"""
Temporal Bridge Discovery System
February 14, 2026

Two-track temporal validation:
  Track 1: Direct Historical Claims (strict contemporaneity)
  Track 2: Bridging Claims (cross-temporal evidence/interpretation)

Silver lining: Large temporal gaps in bridging claims are GOLD, not noise.
They represent modern validation, reinterpretation, or precedent citation of ancient history.
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
from datetime import datetime


class ClaimTrack(Enum):
    """Claim validation tracks"""
    DIRECT_HISTORICAL = "direct_historical"      # Contemporaneous interaction
    BRIDGING_DISCOVERY = "bridging_discovery"    # Cross-temporal evidential/interpretive
    UNKNOWN = "unknown"


class BridgeType(Enum):
    """Types of temporal bridges"""
    ARCHAEOLOGICAL = "archaeological_discovery"
    HISTORIOGRAPHIC = "modern_historiographic_revision"
    PRECEDENT = "legal_political_precedent"
    CULTURAL = "modern_cultural_representation"
    SCIENTIFIC = "modern_scientific_validation"


@dataclass
class TemporalBridgeResult:
    """Result of temporal bridge validation"""
    valid: bool
    track: ClaimTrack
    confidence: float
    reason: str
    bridge_type: Optional[BridgeType] = None
    temporal_gap: int = 0
    priority: str = "MEDIUM"
    significance: str = ""
    requires_review: bool = False
    metadata: Dict = None


class TemporalBridgeValidator:
    """
    Enhanced temporal validator that discovers cross-temporal bridges
    rather than filtering them out as noise.
    """
    
    # Track 1: Direct historical claims (strict validation)
    DIRECT_CLAIM_TYPES = {
        'FOUGHT_ALONGSIDE',
        'MARRIED_TO',
        'PARENT_OF',
        'TAUGHT',
        'MET_WITH',
        'DEFEATED_IN_BATTLE',
        'NEGOTIATED_WITH',
        'ALLIED_WITH',
        'BETRAYED',
        'COMPETED_WITH',
        'ADVISED'
    }
    
    # Track 2: Bridging claims (discovery mode - temporal gap OK!)
    BRIDGING_CLAIM_TYPES = {
        'DISCOVERED_EVIDENCE_FOR',
        'EXCAVATED_REMAINS_OF',
        'REINTERPRETED',
        'CHALLENGED_NARRATIVE_OF',
        'PROVIDED_NEW_EVIDENCE_FOR',
        'REFUTED_CLAIM_ABOUT',
        'CITED_HISTORICAL_PRECEDENT',
        'MODELED_ON',
        'DREW_INSPIRATION_FROM',
        'EXPLICITLY_REFERENCED',
        'DRAMATIZED',
        'DEPICTED',
        'ADAPTED',
        'COMMEMORATED',
        'PORTRAYED',
        'VALIDATED_CLAIM_ABOUT',
        'DISPROVED_CLAIM_ABOUT',
        'DATED_ARTIFACT_FROM',
        'ANALYZED_DNA_FROM',
        'ISOTOPE_ANALYSIS_SHOWED',
        'CARBON_DATED',
        'ANALYZED_ARTIFACT_FROM',
        'INSPIRED_BY',
        'COMPARED_TO_BY',
        'TRANSLATED_WORK_OF'
    }
    
    # Archaeological bridge patterns
    GOLD_PATTERN_1 = {
        'name': 'modern_archaeological_discovery',
        'source_date_min': 1800,
        'target_date_max': 500,
        'relationship_types': {
            'DISCOVERED_EVIDENCE_FOR',
            'EXCAVATED_REMAINS_OF',
            'CARBON_DATED',
            'ANALYZED_ARTIFACT_FROM'
        },
        'facets': {'archaeological', 'scientific'},
        'priority': 'HIGH'
    }
    
    # Historiographic reinterpretation patterns
    GOLD_PATTERN_2 = {
        'name': 'modern_historiographic_revision',
        'source_type': 'Human',
        'source_occupation': 'historian',
        'relationship_types': {
            'REINTERPRETED',
            'CHALLENGED_NARRATIVE_OF',
            'PROVIDED_NEW_EVIDENCE_FOR',
            'REFUTED_CLAIM_ABOUT'
        },
        'facets': {'intellectual', 'communication'},
        'priority': 'HIGH'
    }
    
    # Political/legal precedent patterns
    GOLD_PATTERN_3 = {
        'name': 'modern_institutional_reference',
        'source_date_min': 1600,  # Modern republics onwards
        'source_type': 'CreativeWork|Institution|Event',
        'relationship_types': {
            'CITED_HISTORICAL_PRECEDENT',
            'MODELED_ON',
            'DREW_INSPIRATION_FROM',
            'EXPLICITLY_REFERENCED'
        },
        'facets': {'political', 'communication', 'intellectual'},
        'priority': 'HIGH'
    }
    
    # Cultural/artistic reception patterns
    GOLD_PATTERN_4 = {
        'name': 'modern_cultural_representation',
        'source_date_min': 1900,
        'source_type': 'CreativeWork',
        'relationship_types': {
            'DRAMATIZED',
            'DEPICTED',
            'ADAPTED',
            'COMMEMORATED',
            'PORTRAYED'
        },
        'facets': {'cultural', 'communication', 'artistic'},
        'priority': 'MEDIUM'
    }
    
    # Scientific analysis patterns
    GOLD_PATTERN_5 = {
        'name': 'modern_scientific_validation',
        'source_date_min': 1950,
        'source_type': 'ScientificStudy|Event',
        'relationship_types': {
            'VALIDATED_CLAIM_ABOUT',
            'DISPROVED_CLAIM_ABOUT',
            'DATED_ARTIFACT_FROM',
            'ANALYZED_DNA_FROM',
            'ISOTOPE_ANALYSIS_SHOWED'
        },
        'facets': {'scientific', 'archaeological'},
        'priority': 'HIGH'
    }
    
    # Evidential markers that signal cross-temporal bridges
    EVIDENTIAL_MARKERS = [
        'discovered', 'excavated', 'found', 'proved', 'validated', 'confirmed',
        'recent study', 'modern analysis', 'archaeologists', 'groundbreaking',
        'carbon dating', 'dna analysis', 'isotope', 'satellite imagery',
        'ground-penetrating radar', 'radiocarbon',
        'reinterpreted', 'challenged', 'revised', 'reassessed',
        'inspired by', 'modeled on', 'drew from', 'referenced',
        'influenced', 'drawn from', 'adaptation of', 'tribute to',
        'scholarship', 'historians argue', 'contemporary analysis'
    ]
    
    def __init__(self, period_qid='Q17167', period_start=-509, period_end=-27):
        """
        Initialize validator for a specific historical period.
        
        Args:
            period_qid: Wikidata ID for the period (e.g., Q17167 = Roman Republic)
            period_start: Start year (BCE = negative)
            period_end: End year (BCE = negative)
        """
        self.period_qid = period_qid
        self.period_start = period_start
        self.period_end = period_end
        self.bridge_count = 0
        self.direct_count = 0
        self.bridge_statistics = {
            'archaeological': 0,
            'historiographic': 0,
            'precedent': 0,
            'cultural': 0,
            'scientific': 0
        }
    
    def validate_temporal_coherence(self, claim: Dict) -> TemporalBridgeResult:
        """
        Two-track validation:
        1. Direct claims: Require contemporaneity
        2. Bridging claims: Celebrate cross-temporal gaps
        """
        
        source = claim.get('source_entity', {})
        target = claim.get('target_entity', {})
        rel_type = claim.get('relationship_type', '')
        evidence_text = claim.get('evidence_text', '')
        
        source_date = self._extract_date(source)
        target_date = self._extract_date(target)
        temporal_gap = abs(source_date - target_date) if source_date and target_date else 0
        
        # Determine which track
        track = self._determine_track(rel_type)
        
        if track == ClaimTrack.DIRECT_HISTORICAL:
            return self._validate_direct_claim(
                source, target, rel_type, source_date, target_date, temporal_gap
            )
        
        elif track == ClaimTrack.BRIDGING_DISCOVERY:
            return self._validate_bridging_claim(
                source, target, rel_type, source_date, target_date, 
                temporal_gap, evidence_text
            )
        
        else:  # UNKNOWN - use evidential markers to route
            if self._has_evidential_markers(evidence_text):
                return self._validate_bridging_claim(
                    source, target, rel_type, source_date, target_date,
                    temporal_gap, evidence_text
                )
            else:
                return TemporalBridgeResult(
                    valid=False,
                    track=ClaimTrack.UNKNOWN,
                    confidence=0.0,
                    reason='unknown_relationship_type_and_no_evidential_markers'
                )
    
    def _determine_track(self, rel_type: str) -> ClaimTrack:
        """Route relationship type to appropriate validation track"""
        if rel_type in self.DIRECT_CLAIM_TYPES:
            return ClaimTrack.DIRECT_HISTORICAL
        elif rel_type in self.BRIDGING_CLAIM_TYPES:
            return ClaimTrack.BRIDGING_DISCOVERY
        else:
            return ClaimTrack.UNKNOWN
    
    def _validate_direct_claim(
        self, source: Dict, target: Dict, rel_type: str,
        source_date: int, target_date: int, temporal_gap: int
    ) -> TemporalBridgeResult:
        """
        Track 1: Direct historical claim validation
        
        STRICT: Requires reasonable contemporaneity
        - If neither entity dated: Accept (assume contemporary)
        - If both dated: Must have significant overlap
        - If only one dated: More lenient (one date may be unknown)
        """
        
        self.direct_count += 1
        
        # No dates available: Assume contemporary (neutral)
        if not source_date or not target_date:
            return TemporalBridgeResult(
                valid=True,
                track=ClaimTrack.DIRECT_HISTORICAL,
                confidence=0.75,  # Penalize lack of dates
                reason='no_temporal_data_available',
                temporal_gap=temporal_gap
            )
        
        # Large gap makes contemporaneous interaction implausible
        if temporal_gap > 150:  # Allow ~3 generations buffer
            return TemporalBridgeResult(
                valid=False,
                track=ClaimTrack.DIRECT_HISTORICAL,
                confidence=0.1,
                reason='temporal_impossibility_direct_claim',
                temporal_gap=temporal_gap,
                significance=f"Gap of {temporal_gap} years precludes direct interaction"
            )
        
        # Consider lifespan overlap for human entities
        if source.get('type') == 'Human' and target.get('type') == 'Human':
            source_life = self._get_lifespan(source)
            target_life = self._get_lifespan(target)
            
            if source_life and target_life:
                source_death, target_birth = source_life[1], target_life[0]
                if source_death < target_birth:  # Source died before target born
                    return TemporalBridgeResult(
                        valid=False,
                        track=ClaimTrack.DIRECT_HISTORICAL,
                        confidence=0.0,
                        reason='lifespan_no_overlap',
                        temporal_gap=temporal_gap
                    )
        
        # All checks passed
        return TemporalBridgeResult(
            valid=True,
            track=ClaimTrack.DIRECT_HISTORICAL,
            confidence=0.90,
            reason='valid_direct_historical_claim',
            temporal_gap=temporal_gap
        )
    
    def _validate_bridging_claim(
        self, source: Dict, target: Dict, rel_type: str,
        source_date: int, target_date: int, temporal_gap: int,
        evidence_text: str
    ) -> TemporalBridgeResult:
        """
        Track 2: Bridging discovery validation
        
        DISCOVERY MODE: Large temporal gaps are GOLD!
        - Large gap with evidential relationship = High priority
        - Connects modern scholarship to ancient history
        - Source must be after period, target within period
        """
        
        self.bridge_count += 1
        
        # Identify specific bridge type
        bridge_type = self._identify_bridge_type(source, target, rel_type, evidence_text)
        
        # Bridge must connect to target period
        if target_date and (target_date < self.period_start or target_date > self.period_end):
            if not (source_date and source_date > 1500):  # Unless source is modern
                return TemporalBridgeResult(
                    valid=False,
                    track=ClaimTrack.BRIDGING_DISCOVERY,
                    confidence=0.0,
                    reason='target_outside_period',
                    bridge_type=bridge_type
                )
        
        # Bridge source should typically be modern (after 1800 for most bridges)
        if source_date and source_date < 1500 and rel_type not in ['REINTERPRETED']:
            return TemporalBridgeResult(
                valid=False,
                track=ClaimTrack.BRIDGING_DISCOVERY,
                confidence=0.0,
                reason='bridge_source_too_ancient',
                bridge_type=bridge_type
            )
        
        # Evidential markers boost confidence
        has_evidence = self._has_evidential_markers(evidence_text)
        
        # Calculate base confidence by bridge type
        base_confidence = self._get_base_confidence_for_bridge(bridge_type)
        
        # Large gap = discovery bonus!
        gap_bonus = min(0.15, temporal_gap / 1000)  # Cap at +0.15
        final_confidence = min(0.98, base_confidence + gap_bonus)
        
        # Mark for human review if confidence is uncertain
        requires_review = final_confidence < 0.75 or not has_evidence
        
        priority = 'HIGH' if temporal_gap > 500 else 'MEDIUM'
        
        self.bridge_statistics[bridge_type.value.split('_')[0]] += 1
        
        return TemporalBridgeResult(
            valid=True,
            track=ClaimTrack.BRIDGING_DISCOVERY,
            confidence=final_confidence,
            reason='cross_temporal_bridge_discovery',
            bridge_type=bridge_type,
            temporal_gap=temporal_gap,
            priority=priority,
            significance=f"Connects modern {bridge_type.value} to ancient period ({temporal_gap} years)",
            requires_review=requires_review,
            metadata={
                'has_evidential_markers': has_evidence,
                'gap_bonus': gap_bonus,
                'bridge_type': bridge_type.value
            }
        )
    
    def _identify_bridge_type(
        self, source: Dict, target: Dict, rel_type: str, evidence_text: str
    ) -> BridgeType:
        """Identify which type of bridge this claim represents"""
        
        source_date = self._extract_date(source)
        
        # Archaeological (recent excavation/analysis)
        if rel_type in self.GOLD_PATTERN_1['relationship_types'] and source_date and source_date > 1800:
            if any(marker in evidence_text.lower() for marker in [
                'excavated', 'discovered', 'carbon dating', 'ground-penetrating radar',
                'satellite imagery', 'archaeologists'
            ]):
                return BridgeType.ARCHAEOLOGICAL
        
        # Historiographic (modern scholar reinterpreting)
        if rel_type in self.GOLD_PATTERN_2['relationship_types']:
            if any(marker in evidence_text.lower() for marker in [
                'historians', 'scholarship', 'reinterpreted', 'modern analysis', 'recent study'
            ]):
                return BridgeType.HISTORIOGRAPHIC
        
        # Precedent (modern institution citing ancient example)
        if rel_type in self.GOLD_PATTERN_3['relationship_types']:
            if any(marker in evidence_text.lower() for marker in [
                'constitution', 'inspired by', 'modeled on', 'drew from', 'founded on'
            ]):
                return BridgeType.PRECEDENT
        
        # Cultural (modern creative work depicting ancient)
        if rel_type in self.GOLD_PATTERN_4['relationship_types']:
            if any(marker in evidence_text.lower() for marker in [
                'film', 'book', 'novel', 'dramatized', 'adaptation', 'depicted', 'portrayed'
            ]):
                return BridgeType.CULTURAL
        
        # Scientific (modern analysis of ancient evidence)
        if rel_type in self.GOLD_PATTERN_5['relationship_types']:
            if any(marker in evidence_text.lower() for marker in [
                'dna', 'isotope', 'analysis', 'study', 'research', 'scientific'
            ]):
                return BridgeType.SCIENTIFIC
        
        # Default
        return BridgeType.HISTORIOGRAPHIC
    
    def _has_evidential_markers(self, text: str) -> bool:
        """Detect language suggesting cross-temporal connection"""
        if not text:
            return False
        text_lower = text.lower()
        return any(marker in text_lower for marker in self.EVIDENTIAL_MARKERS)
    
    def _get_base_confidence_for_bridge(self, bridge_type: BridgeType) -> float:
        """Base confidence for different bridge types"""
        confidence_map = {
            BridgeType.ARCHAEOLOGICAL: 0.92,      # High certainty
            BridgeType.HISTORIOGRAPHIC: 0.85,     # Good but interpretive
            BridgeType.PRECEDENT: 0.90,           # Usually explicit
            BridgeType.CULTURAL: 0.70,            # Lower (creative liberty)
            BridgeType.SCIENTIFIC: 0.92            # High certainty
        }
        return confidence_map.get(bridge_type, 0.75)
    
    def _extract_date(self, entity: Dict) -> Optional[int]:
        """Extract date from entity (handles various date fields)"""
        for field in ['date', 'date_of_birth', 'birth_year', 'event_date', 'point_in_time']:
            if field in entity and entity[field]:
                try:
                    return int(entity[field])
                except (ValueError, TypeError):
                    continue
        return None
    
    def _get_lifespan(self, human_entity: Dict) -> Optional[Tuple[int, int]]:
        """Get birth-death range for a human entity"""
        birth = None
        death = None
        
        for field in ['birth', 'birth_year', 'date_of_birth']:
            if field in human_entity:
                try:
                    birth = int(human_entity[field])
                    break
                except (ValueError, TypeError):
                    pass
        
        for field in ['death', 'death_year', 'date_of_death']:
            if field in human_entity:
                try:
                    death = int(human_entity[field])
                    break
                except (ValueError, TypeError):
                    pass
        
        if birth is not None and death is not None:
            return (birth, death)
        return None
    
    def get_statistics(self) -> Dict:
        """Get validation statistics"""
        total_claims = self.direct_count + self.bridge_count
        return {
            'total_claims_validated': total_claims,
            'direct_historical_claims': self.direct_count,
            'bridging_discovery_claims': self.bridge_count,
            'bridge_percentage': round(
                (self.bridge_count / total_claims * 100) if total_claims > 0 else 0, 1
            ),
            'bridge_types': self.bridge_statistics
        }


# Example usage
if __name__ == "__main__":
    validator = TemporalBridgeValidator(period_qid='Q17167')
    
    # Example 1: Archaeological bridge (GOLD!)
    archaeological_claim = {
        'source_entity': {
            'type': 'Event',
            'label': '2018 Philippi battlefield survey',
            'date': 2018
        },
        'target_entity': {
            'type': 'Event',
            'label': 'Battle of Philippi',
            'date': -42
        },
        'relationship_type': 'DISCOVERED_EVIDENCE_FOR',
        'evidence_text': 'In 2018, Greek and French archaeologists used ground-penetrating radar to map the battlefield at Philippi, confirming the location of Brutus camp from the ancient sources.'
    }
    
    result = validator.validate_temporal_coherence(archaeological_claim)
    print(f"\n--- Archaeological Bridge Example ---")
    print(f"Valid: {result.valid}")
    print(f"Track: {result.track.value}")
    print(f"Bridge Type: {result.bridge_type.value if result.bridge_type else 'N/A'}")
    print(f"Confidence: {result.confidence}")
    print(f"Priority: {result.priority}")
    print(f"Gap (years): {result.temporal_gap}")
    print(f"Significance: {result.significance}")
    
    # Example 2: Direct historical claim (strict validation)
    direct_claim = {
        'source_entity': {
            'type': 'Human',
            'label': 'Julius Caesar',
            'birth': -100,
            'death': -44
        },
        'target_entity': {
            'type': 'Human',
            'label': 'Pompey',
            'birth': -106,
            'death': -48
        },
        'relationship_type': 'DEFEATED_IN_BATTLE',
        'evidence_text': 'Caesar defeated Pompey at the Battle of Pharsalus in 48 BC.'
    }
    
    result = validator.validate_temporal_coherence(direct_claim)
    print(f"\n--- Direct Historical Claim Example ---")
    print(f"Valid: {result.valid}")
    print(f"Track: {result.track.value}")
    print(f"Confidence: {result.confidence}")
    print(f"Reason: {result.reason}")
    
    # Example 3: Modern precedent (political bridge)
    precedent_claim = {
        'source_entity': {
            'type': 'CreativeWork',
            'label': 'US Constitution',
            'date': 1787
        },
        'target_entity': {
            'type': 'Institution',
            'label': 'Roman Senate',
            'date': -200  # Approximate
        },
        'relationship_type': 'DREW_INSPIRATION_FROM',
        'evidence_text': 'The Founding Fathers drew inspiration from Roman Republican institutions, particularly the mixed constitution model of consuls, senate, and assemblies.'
    }
    
    result = validator.validate_temporal_coherence(precedent_claim)
    print(f"\n--- Political Precedent Bridge Example ---")
    print(f"Valid: {result.valid}")
    print(f"Track: {result.track.value}")
    print(f"Bridge Type: {result.bridge_type.value if result.bridge_type else 'N/A'}")
    print(f"Confidence: {result.confidence}")
    print(f"Priority: {result.priority}")
    print(f"Gap (years): {result.temporal_gap}")
    
    print(f"\n--- Statistics ---")
    stats = validator.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
