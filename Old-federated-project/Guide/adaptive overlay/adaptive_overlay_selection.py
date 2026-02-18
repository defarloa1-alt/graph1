#!/usr/bin/env python3
"""
Adaptive Overlay Selection Implementation
========================================

This module implements the f_k^adaptive overlay selection logic described in
formula_enrichment_analysis.md, providing explicit selection criteria and
computational efficiency optimization.

Author: Enhanced Federated Graph Framework
Date: 2025-10-01
"""

from typing import List, Dict, Set, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class InquiryType(Enum):
    FACT_SEEKING = "fact_seeking"
    ASSISTANCE = "assistance"
    ANALYSIS = "analysis"
    PREDICTION = "prediction"


class Urgency(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OverlayFunction(Enum):
    """The 17 framework overlay functions"""
    SPATIAL_ANALYSIS = "f1_spatial"
    TEMPORAL_PATTERNS = "f2_temporal"
    SEMANTIC_ANALYSIS = "f3_semantic"
    SYNTACTIC_PARSING = "f4_syntactic"
    PRAGMATIC_CONTEXT = "f5_pragmatic"
    DOMAIN_CLASSIFICATION = "f6_domain"
    RELATIONSHIP_MAPPING = "f7_relationship"
    KNOWLEDGE_INTEGRATION = "f8_knowledge"
    CONFLICT_RESOLUTION = "f9_conflict"
    CONSENSUS_TRACKING = "f10_consensus"
    AUTHORITY_VALIDATION = "f11_authority"
    RISK_ASSESSMENT = "f12_risk"
    IMPLEMENTATION_ANALYSIS = "f13_implementation"
    COMPARATIVE_ANALYSIS = "f14_comparative"
    TREND_ANALYSIS = "f15_trend"
    FEASIBILITY_ANALYSIS = "f16_feasibility"
    PREDICTIVE_MODELING = "f17_predictive"


@dataclass
class OverlaySelectionResult:
    """Result of overlay selection process"""
    selected_overlays: Set[OverlayFunction]
    computation_reduction: float
    selection_rationale: str
    urgency_applied: bool
    coverage_score: float


class AdaptiveOverlaySelector:
    """Implements the adaptive overlay selection algorithm"""
    
    def __init__(self):
        self.overlay_mappings = self._initialize_overlay_mappings()
        self.baseline_set = set(OverlayFunction)  # All 17 overlays
        
    def select_overlays(self, inquiry_type: InquiryType, urgency: Urgency = Urgency.MEDIUM) -> OverlaySelectionResult:
        """
        Select appropriate f_k overlays based on inquiry type and urgency.
        
        Implements the algorithm from formula_enrichment_analysis.md ensuring
        essential overlays are never dropped while optimizing computation.
        
        Args:
            inquiry_type: The type of inquiry being processed
            urgency: The urgency level of the inquiry
            
        Returns:
            OverlaySelectionResult with selected overlays and metadata
        """
        logger.info(f"Selecting overlays for {inquiry_type.value} with urgency {urgency.value}")
        
        mapping = self.overlay_mappings[inquiry_type]
        
        # Always include core overlays - these are essential for convergence
        selected = set(mapping['core'])
        rationale_parts = [f"Core overlays for {inquiry_type.value}: {len(mapping['core'])} functions"]
        
        # Apply urgency-based selection for optional overlays
        urgency_applied = False
        if urgency in [Urgency.CRITICAL, Urgency.HIGH]:
            # High urgency: core only for speed
            rationale_parts.append("High urgency: core overlays only")
            urgency_applied = True
        elif urgency == Urgency.MEDIUM:
            # Medium urgency: core + selected optional
            optional_subset = mapping['optional'][:2]  # First 2 optional
            selected.update(optional_subset)
            rationale_parts.append(f"Medium urgency: added {len(optional_subset)} optional overlays")
            urgency_applied = True
        else:
            # Low urgency: comprehensive analysis with all relevant overlays
            selected.update(mapping['optional'])
            rationale_parts.append(f"Low urgency: added all {len(mapping['optional'])} optional overlays")
        
        # Calculate computational reduction
        total_overlays = len(self.baseline_set)
        selected_count = len(selected)
        computation_reduction = 1.0 - (selected_count / total_overlays)
        
        # Calculate coverage score (simplified heuristic)
        coverage_score = self._calculate_coverage_score(selected, inquiry_type)
        
        rationale = "; ".join(rationale_parts)
        rationale += f" (Reduction: {computation_reduction:.1%}, Coverage: {coverage_score:.2f})"
        
        result = OverlaySelectionResult(
            selected_overlays=selected,
            computation_reduction=computation_reduction,
            selection_rationale=rationale,
            urgency_applied=urgency_applied,
            coverage_score=coverage_score
        )
        
        logger.info(f"Selected {selected_count}/{total_overlays} overlays ({computation_reduction:.1%} reduction)")
        self._validate_selection(result, inquiry_type)
        
        return result
    
    def _initialize_overlay_mappings(self) -> Dict[InquiryType, Dict[str, List[OverlayFunction]]]:
        """Initialize the inquiry-type to overlay mappings"""
        
        return {
            InquiryType.FACT_SEEKING: {
                'core': [
                    OverlayFunction.SEMANTIC_ANALYSIS,      # f3: Extract meaning
                    OverlayFunction.DOMAIN_CLASSIFICATION,  # f6: Identify domain
                    OverlayFunction.AUTHORITY_VALIDATION,   # f11: Validate sources
                ],
                'optional': [
                    OverlayFunction.SYNTACTIC_PARSING,      # f4: Parse structure
                    OverlayFunction.KNOWLEDGE_INTEGRATION,  # f8: Integrate knowledge
                ]
            },
            
            InquiryType.ASSISTANCE: {
                'core': [
                    OverlayFunction.DOMAIN_CLASSIFICATION,   # f6: Identify domain
                    OverlayFunction.RISK_ASSESSMENT,        # f12: Assess risks
                    OverlayFunction.IMPLEMENTATION_ANALYSIS, # f13: Implementation details
                    OverlayFunction.FEASIBILITY_ANALYSIS,   # f16: Check feasibility
                ],
                'optional': [
                    OverlayFunction.SPATIAL_ANALYSIS,       # f1: Geographic context
                    OverlayFunction.TEMPORAL_PATTERNS,      # f2: Timing considerations
                    OverlayFunction.PRAGMATIC_CONTEXT,      # f5: Practical context
                    OverlayFunction.KNOWLEDGE_INTEGRATION,  # f8: Integrate knowledge
                ]
            },
            
            InquiryType.ANALYSIS: {
                'core': [
                    OverlayFunction.SEMANTIC_ANALYSIS,      # f3: Extract meaning
                    OverlayFunction.DOMAIN_CLASSIFICATION,  # f6: Identify domain
                    OverlayFunction.COMPARATIVE_ANALYSIS,   # f14: Compare options
                    OverlayFunction.CONFLICT_RESOLUTION,    # f9: Resolve conflicts
                ],
                'optional': [
                    OverlayFunction.RELATIONSHIP_MAPPING,   # f7: Map relationships
                    OverlayFunction.KNOWLEDGE_INTEGRATION,  # f8: Integrate knowledge
                    OverlayFunction.CONSENSUS_TRACKING,     # f10: Track consensus
                    OverlayFunction.RISK_ASSESSMENT,        # f12: Assess risks
                    OverlayFunction.FEASIBILITY_ANALYSIS,   # f16: Check feasibility
                ]
            },
            
            InquiryType.PREDICTION: {
                'core': [
                    OverlayFunction.TEMPORAL_PATTERNS,      # f2: Time patterns
                    OverlayFunction.DOMAIN_CLASSIFICATION,  # f6: Identify domain
                    OverlayFunction.TREND_ANALYSIS,         # f15: Analyze trends
                    OverlayFunction.PREDICTIVE_MODELING,    # f17: Build models
                ],
                'optional': [
                    OverlayFunction.SPATIAL_ANALYSIS,       # f1: Geographic patterns
                    OverlayFunction.KNOWLEDGE_INTEGRATION,  # f8: Integrate knowledge
                    OverlayFunction.CONSENSUS_TRACKING,     # f10: Track consensus
                    OverlayFunction.RISK_ASSESSMENT,        # f12: Assess risks
                ]
            }
        }
    
    def _calculate_coverage_score(self, selected: Set[OverlayFunction], inquiry_type: InquiryType) -> float:
        """
        Calculate coverage score for selected overlays.
        
        This is a simplified heuristic - in production, this should be based on
        empirical analysis of overlay effectiveness for different inquiry types.
        """
        mapping = self.overlay_mappings[inquiry_type]
        
        # Core overlays are essential (weight = 1.0)
        core_coverage = len(set(mapping['core']).intersection(selected)) / len(mapping['core'])
        
        # Optional overlays add incremental value (weight = 0.5)
        optional_coverage = len(set(mapping['optional']).intersection(selected)) / len(mapping['optional'])
        
        # Weighted average with core overlays having higher importance
        coverage_score = (core_coverage * 0.8) + (optional_coverage * 0.2)
        
        return coverage_score
    
    def _validate_selection(self, result: OverlaySelectionResult, inquiry_type: InquiryType) -> None:
        """Validate that the selection maintains minimum requirements"""
        
        mapping = self.overlay_mappings[inquiry_type]
        core_overlays = set(mapping['core'])
        selected_overlays = result.selected_overlays
        
        # Ensure all core overlays are included
        missing_core = core_overlays - selected_overlays
        if missing_core:
            raise ValueError(f"Missing essential core overlays for {inquiry_type.value}: {missing_core}")
        
        # Ensure minimum coverage score
        min_coverage = 0.8  # 80% minimum coverage
        if result.coverage_score < min_coverage:
            logger.warning(f"Coverage score {result.coverage_score:.2f} below minimum {min_coverage}")
        
        logger.debug(f"Selection validation passed for {inquiry_type.value}")
    
    def get_overlay_reduction_stats(self) -> Dict[InquiryType, Dict[str, float]]:
        """Get statistical summary of overlay reduction by inquiry type"""
        
        stats = {}
        
        for inquiry_type in InquiryType:
            # Calculate for medium urgency (typical case)
            result = self.select_overlays(inquiry_type, Urgency.MEDIUM)
            
            stats[inquiry_type] = {
                'selected_count': len(result.selected_overlays),
                'total_count': len(self.baseline_set),
                'reduction_percentage': result.computation_reduction * 100,
                'coverage_score': result.coverage_score,
            }
        
        return stats
    
    def validate_all_inquiry_types(self) -> bool:
        """Validate overlay selection for all inquiry types and urgency levels"""
        
        try:
            for inquiry_type in InquiryType:
                for urgency in Urgency:
                    result = self.select_overlays(inquiry_type, urgency)
                    logger.debug(f"Validated {inquiry_type.value} + {urgency.value}: "
                               f"{len(result.selected_overlays)} overlays, "
                               f"{result.computation_reduction:.1%} reduction")
            
            logger.info("All inquiry type + urgency combinations validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False


def demonstrate_overlay_selection():
    """Demonstrate the adaptive overlay selection system"""
    
    print("ADAPTIVE OVERLAY SELECTION DEMONSTRATION")
    print("=" * 60)
    print()
    
    selector = AdaptiveOverlaySelector()
    
    # Test all inquiry types with medium urgency
    for inquiry_type in InquiryType:
        print(f"INQUIRY TYPE: {inquiry_type.value.upper()}")
        print("-" * 40)
        
        result = selector.select_overlays(inquiry_type, Urgency.MEDIUM)
        
        print(f"Selected overlays: {len(result.selected_overlays)}/17")
        print(f"Computation reduction: {result.computation_reduction:.1%}")
        print(f"Coverage score: {result.coverage_score:.2f}")
        print(f"Rationale: {result.selection_rationale}")
        
        print("Core overlays:")
        core_overlays = selector.overlay_mappings[inquiry_type]['core']
        for overlay in core_overlays:
            print(f"  • {overlay.value}")
        
        print()
    
    # Show reduction statistics
    print("REDUCTION STATISTICS")
    print("=" * 30)
    stats = selector.get_overlay_reduction_stats()
    
    for inquiry_type, stat in stats.items():
        print(f"{inquiry_type.value:12}: {stat['selected_count']:2d}/17 overlays "
              f"({stat['reduction_percentage']:4.1f}% reduction, "
              f"coverage: {stat['coverage_score']:.2f})")
    
    print()
    
    # Validate all combinations
    print("VALIDATION TEST")
    print("=" * 20)
    if selector.validate_all_inquiry_types():
        print("✓ All inquiry type + urgency combinations validated")
    else:
        print("✗ Validation failed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstration
    demonstrate_overlay_selection()