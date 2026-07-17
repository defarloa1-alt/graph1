"""
Military Subject Facet Agent (Enhanced) — DEPRECATED for training writes.

DO NOT use discover_theory_from_source / THEORY_PREDICATES / snake_case predicates
against the live graph. Those paths created unregistered MilitaryPrinciple nodes
and demo pollution (purged 2026-07-16).

Use instead:
  - docs/FACET_TRAINING_CONTRACT.md
  - scripts/agents/military/agent.py (registry-backed)
  - scripts/agents/military/training_pilot.py (Claims-track pilot)

This module is retained only for source-tier helpers and historical reference.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from neo4j import GraphDatabase
from scripts.agents.claim_registry import ClaimRegistry
from scripts.agents.peer_reviewer import PeerReviewer

# Import base SFA class
try:
    from scripts.agents.subject_concept_facet_agents import SubjectConceptFacetAgent
except ImportError:
    # Fallback if base class not available
    class SubjectConceptFacetAgent:
        def __init__(self, facet_key, facet_label, neo4j_driver, **kwargs):
            self.facet_key = facet_key
            self.facet_label = facet_label
            self.driver = neo4j_driver
            self.agent_id = f"{facet_key.lower()}_sfa_001"


class MilitarySFAEnhanced(SubjectConceptFacetAgent):
    """
    Military Subject Facet Agent (Enhanced)
    
    Analyzes entities from military perspective with scholarly grounding.
    
    Source Hierarchy (3-tier):
    - Tier 1: Roman primary sources (Polybius, Caesar, Livy, etc.)
    - Tier 2: Classical military theory (Sun Tzu, Thucydides)
    - Tier 3: Modern scholarship
    
    Predicate Categories:
    - Strategic: conflict triggers, strategic outcomes, reforms
    - Tactical: specific tactics, campaigns, operations
    - Doctrinal: doctrine, organization, conventions
    - Leadership: command qualities
    - Operational: battles, sieges, training (legacy)
    
    Integrates with Phase 2:
    - ClaimRegistry for entity deduplication
    - PeerReviewer for cross-facet validation
    - Anachronism risk flagging
    """
    
    # === PREDICATES (Hierarchical) ===
    
    # Strategic Level (Perplexity)
    STRATEGIC_PREDICATES = [
        'triggered_conflict',
        'escalated_conflict',
        'resulted_in_strategic_outcome',
        'caused_military_reform',
        'shifted_balance_of_power'
    ]
    
    # Tactical Level (Perplexity + Original)
    TACTICAL_PREDICATES = [
        'employed_tactic',
        'commanded_campaign',
        'siege_operation',
        'naval_engagement',
        'ambush_operation',
        'feigned_retreat',
        'double_envelopment',
        'frontal_assault',
        'flanking_maneuver'
    ]
    
    # Doctrinal Level (Perplexity)
    DOCTRINAL_PREDICATES = [
        'illustrates_military_doctrine',
        'reflects_organizational_structure',
        'violated_military_convention',
        'established_precedent'
    ]
    
    # Leadership Level (Perplexity)
    LEADERSHIP_PREDICATES = [
        'demonstrated_command_quality',
        'showed_tactical_innovation',
        'displayed_strategic_vision',
        'managed_logistics',
        'maintained_discipline'
    ]
    
    # Operational Level (Original - Legacy)
    OPERATIONAL_PREDICATES = [
        'participated_in_battle',
        'military_training',
        'commanded_legion',
        'conducted_march',
        'fortification_construction',
        'crossed_rubicon',
        'fought_at',
        'besieged',
        'fortified',
        'retreated_from',
        'advanced_to'
    ]
    
    # === THEORY PREDICATES (for MILITARY_THEORY SubjectConcept) ===
    
    THEORY_PREDICATES = [
        'defines_principle',        # Defines a military principle
        'establishes_framework',    # Establishes analytical framework
        'codifies_doctrine',        # Codifies military doctrine
        'identifies_pattern',       # Identifies recurring pattern
        'contradicts_theory',       # Contradicts another theory
        'refines_concept',          # Refines existing concept
        'synthesizes_principles'    # Synthesizes multiple principles
    ]
    
    # === LINKING PREDICATES (cross-SubjectConcept) ===
    
    LINKING_PREDICATES = [
        'exemplifies_principle',    # Historical event exemplifies theory
        'validates_theory',         # Historical evidence validates theory
        'challenges_theory',        # Historical case challenges theory
        'applies_framework'         # Applies theoretical framework
    ]
    
    # === SOURCE TIERS ===
    
    SOURCE_TIERS = {
        # Tier 1 - Roman Primary Sources
        'polybius': {
            'tier': 1,
            'weight': 1.0,
            'anachronism_risk': False,
            'period': '200-118 BCE',
            'specialty': 'Legion organization, maniple structure'
        },
        'caesar': {
            'tier': 1,
            'weight': 1.0,
            'anachronism_risk': False,
            'period': '58-44 BCE',
            'specialty': 'Operational accounts, tactical improvisation'
        },
        'sallust': {
            'tier': 1,
            'weight': 0.95,
            'anachronism_risk': False,
            'period': '86-35 BCE',
            'specialty': 'Marian reforms, military-political interface'
        },
        'livy': {
            'tier': 1,
            'weight': 0.90,
            'anachronism_risk': False,
            'period': '59 BCE-17 CE',
            'specialty': 'Campaign narratives, battle descriptions'
        },
        'frontinus': {
            'tier': 1,
            'weight': 0.90,
            'anachronism_risk': False,
            'period': '40-103 CE',
            'specialty': '500+ stratagems, tactical catalog'
        },
        'vegetius': {
            'tier': 1,
            'weight': 0.75,
            'anachronism_risk': True,  # 4th c. AD idealizing Republican past
            'period': '390-450 CE',
            'specialty': 'Roman military doctrine (LATE, idealizes earlier practice)'
        },
        'onasander': {
            'tier': 1,
            'weight': 0.85,
            'anachronism_risk': False,
            'period': '1st c. CE',
            'specialty': 'Command ethics, general conduct'
        },
        
        # Tier 2 - Classical Theory
        'sun tzu': {
            'tier': 2,
            'weight': 0.75,
            'anachronism_risk': False,
            'period': '5th c. BCE',
            'specialty': 'Universal strategic principles'
        },
        'thucydides': {
            'tier': 2,
            'weight': 0.75,
            'anachronism_risk': False,
            'period': '460-400 BCE',
            'specialty': 'Strategy under uncertainty, siege warfare'
        },
        
        # Tier 3 - Modern Scholarship
        'goldsworthy': {
            'tier': 3,
            'weight': 0.70,
            'anachronism_risk': False,
            'period': 'modern',
            'specialty': 'Caesar, Roman Army at War'
        },
        'cambridge': {
            'tier': 3,
            'weight': 0.70,
            'anachronism_risk': False,
            'period': 'modern',
            'specialty': 'Greek and Roman Warfare'
        },
        'modern': {
            'tier': 3,
            'weight': 0.65,
            'anachronism_risk': False,
            'period': 'modern',
            'specialty': 'Contemporary scholarship'
        },
    }
    
    # Wikidata properties for military context
    MILITARY_PROPERTIES = [
        'P607',  # conflict
        'P241',  # military branch
        'P598',  # commander of
        'P642',  # of (qualifier)
        'P793',  # significant event
        'P276',  # location
        'P585',  # point in time
        'P580',  # start time
        'P582',  # end time
        'P1344', # participant in
        'P710',  # participant
        'P828',  # has cause
        'P1542', # has effect
        'P361',  # part of
        'P1120', # number of deaths
        'P1590', # number of injured
    ]
    
    def __init__(self, neo4j_driver, anthropic_api_key: Optional[str] = None, **kwargs):
        """
        Initialize Enhanced Military SFA.
        
        Args:
            neo4j_driver: Neo4j driver instance
            anthropic_api_key: Optional Claude API key
        """
        super().__init__(
            facet_key="MILITARY",
            facet_label="Military",
            neo4j_driver=neo4j_driver,
            anthropic_api_key=anthropic_api_key,
            **kwargs
        )
        
        # Override agent_id to match Phase 2 convention
        self.agent_id = "military_sfa_001_enhanced"
        
        # Initialize Phase 2 services
        self.claim_registry = ClaimRegistry(neo4j_driver)
        self.peer_reviewer = PeerReviewer(neo4j_driver)
        
        # Initialize Anthropic client for discovery
        try:
            import anthropic
            api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            else:
                self.anthropic_client = None
                print("[WARN] ANTHROPIC_API_KEY not set - discovery will be disabled")
        except ImportError:
            self.anthropic_client = None
            print("[WARN] anthropic package not installed - discovery will be disabled")
    
    # ─────────────────────────────────────────────────────
    # Enhanced Methods
    # ─────────────────────────────────────────────────────
    
    def get_all_predicates(self) -> List[str]:
        """Get all military predicates (all categories)."""
        return (
            self.STRATEGIC_PREDICATES +
            self.TACTICAL_PREDICATES +
            self.DOCTRINAL_PREDICATES +
            self.LEADERSHIP_PREDICATES +
            self.OPERATIONAL_PREDICATES
        )
    
    def get_predicate_category(self, predicate: str) -> Optional[str]:
        """Determine which category a predicate belongs to."""
        if predicate in self.STRATEGIC_PREDICATES:
            return 'strategic'
        elif predicate in self.TACTICAL_PREDICATES:
            return 'tactical'
        elif predicate in self.DOCTRINAL_PREDICATES:
            return 'doctrinal'
        elif predicate in self.LEADERSHIP_PREDICATES:
            return 'leadership'
        elif predicate in self.OPERATIONAL_PREDICATES:
            return 'operational'
        return None
    
    def evaluate_source_quality(self, source_ref: str) -> Tuple[float, bool, str, Dict]:
        """
        Evaluate source quality and anachronism risk.
        
        Args:
            source_ref: Source reference string (e.g., "Polybius 6.19-42")
        
        Returns:
            (confidence_weight, anachronism_risk, tier_description, source_info)
        """
        if not source_ref:
            return (0.65, False, 'tier3_unspecified', {})
        
        source_lower = source_ref.lower()
        
        # Check against known sources
        for source_key, source_info in self.SOURCE_TIERS.items():
            if source_key in source_lower:
                tier = source_info['tier']
                tier_name = f"tier{tier}_{source_key.replace(' ', '_')}"
                return (
                    source_info['weight'],
                    source_info['anachronism_risk'],
                    tier_name,
                    source_info
                )
        
        # Default: assume modern secondary source
        return (0.65, False, 'tier3_modern', self.SOURCE_TIERS['modern'])
    
    def submit_military_claim(
        self,
        entity: Dict,
        predicate: str,
        confidence: float,
        source_ref: Optional[str] = None,
        source_qid: Optional[str] = None,
        igar_chain: Optional[Dict] = None,
        apply_source_weighting: bool = True,
        **kwargs
    ) -> str:
        """DISABLED — use registry-backed MilitarySFA or training_pilot."""
        raise RuntimeError(
            "MilitarySFAEnhanced.submit_military_claim is disabled for training. "
            "Use scripts.agents.military.agent.MilitarySFA with registry types "
            "(FOUGHT_IN, SERVED_UNDER, …) or scripts.agents.military.training_pilot. "
            f"Rejected predicate={predicate!r}."
        )
    
    def get_source_tier_explanation(self, source_ref: str) -> str:
        """
        Get human-readable explanation of source tier and weighting.
        
        Args:
            source_ref: Source reference string
        
        Returns:
            Explanation string
        """
        weight, risk, tier, info = self.evaluate_source_quality(source_ref)
        
        explanation = f"Source: {source_ref}\n"
        explanation += f"Tier: {tier}\n"
        explanation += f"Weight: {weight}\n"
        
        if info:
            explanation += f"Period: {info.get('period', 'unknown')}\n"
            explanation += f"Specialty: {info.get('specialty', 'general')}\n"
        
        if risk:
            explanation += "[!] ANACHRONISM RISK: This source is from a later period and may idealize earlier practice.\n"
        
        return explanation
    
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        """
        Build enhanced analysis prompt with Perplexity's source context.
        
        Override of base class method to add military-specific grounding.
        """
        label = subject_concept.get('label', 'Unknown')
        qid = subject_concept.get('qid', 'Unknown')
        
        return f"""
Analyze this subject concept from a MILITARY perspective:

Subject: {label} (Wikidata {qid})

## Your Identity and Role
You are a WITNESS, not an owner. Canonical entities exist independently in the graph.
Your role is to assert MILITARY-facet claims about those entities — what they mean,
caused, or represented from a military perspective.

## Primary Sources (Tiered by Authority)

### Tier 1 — Roman Military Primary Sources (highest weight)
- **Polybius, Histories (esp. Book VI)**: Legion organization, maniple structure.
  The foundational description of the mid-Republican manipular army.
- **Julius Caesar, Commentarii**: First-person operational accounts of march, siege,
  tactical improvisation, and command decision. Gold standard for Late Republican
  field command.
- **Sallust**: Roman military command under political pressure; Marian reforms in context.
- **Livy, Ab Urbe Condita**: Campaign narratives, battle descriptions, commander behavior.
- **Frontinus, Strategemata**: 500+ stratagems organized by type. Use for identifying
  recurring strategic patterns.
- **Vegetius, Epitoma Rei Militaris**: Roman military manual. ⚠️  4th century AD,
  idealizes earlier practice — flag anachronism risk when applying to Republic.
- **Onasander, Strategikos**: Command ethics, general conduct in battle.

### Tier 2 — Classical Theory (cross-cultural strategic principles)
- **Sun Tzu, The Art of War**: Deception, terrain, speed, intelligence, force economy.
- **Thucydides**: Strategy under uncertainty, democratic military decision-making, siegecraft.

### Tier 3 — Modern Military Scholarship (analytical framework)
- Cambridge History of Greek and Roman Warfare
- Adrian Goldsworthy on Caesar and the Roman Army

## Analysis Framework

When asserting military claims, structure using these predicates:

**Strategic Level:**
- triggered_conflict, escalated_conflict, resulted_in_strategic_outcome
- caused_military_reform, shifted_balance_of_power

**Tactical Level:**
- employed_tactic, commanded_campaign, siege_operation, naval_engagement
- ambush_operation, feigned_retreat, double_envelopment, flanking_maneuver

**Doctrinal Level:**
- illustrates_military_doctrine, reflects_organizational_structure
- violated_military_convention, established_precedent

**Leadership Level:**
- demonstrated_command_quality, showed_tactical_innovation
- displayed_strategic_vision, managed_logistics, maintained_discipline

**Operational Level:**
- participated_in_battle, military_training, commanded_legion
- conducted_march, fortification_construction

## IGAR Anti-Presentism Rule
Never evaluate Roman military actors against modern ethical or political standards.
Assess commanders against the norms, expectations, and constraints of their own time
and Roman military culture. A general who massacred a garrison acted within accepted
Roman conventions; classify by Roman military standards, not modern ones.

## Questions to Answer

1. What are the key **military aspects** of this subject?
2. What **strategic level** claims can be made? (triggers, outcomes, reforms)
3. What **tactical methods** were employed? (specific tactics, innovations)
4. What **doctrinal principles** are illustrated? (organization, doctrine, conventions)
5. What **command qualities** are demonstrated? (leadership, innovation, vision)
6. What **primary sources** support these claims? (cite with confidence weighting)
7. Any **anachronism risks** if using Vegetius or later sources on Republic?
8. Confidence in military facet being relevant (0-1)?

Provide structured analysis with source citations.
"""
    
    # ─────────────────────────────────────────────────────
    # Theory Discovery Methods (MILITARY_THEORY SubjectConcept)
    # ─────────────────────────────────────────────────────
    
    def discover_theory_from_source(
        self,
        source_ref: str,
        passage_text: str,
        theorist: Optional[str] = None
    ) -> List[Dict]:
        """DISABLED — created unregistered :MilitaryPrinciple nodes (purged)."""
        raise RuntimeError(
            "discover_theory_from_source is disabled (FACET_TRAINING_CONTRACT). "
            "Do not invent MilitaryPrinciple nodes. "
            f"source_ref={source_ref!r} theorist={theorist!r} "
            f"passage_len={len(passage_text or '')}."
        )
        # Unreachable legacy body retained below for reference only
        prompt = f"""
You are reading military theoretical literature to discover universal principles.

**Source**: {source_ref}

**Passage**:
{passage_text}

**Your Task**:
Extract any military theories, principles, frameworks, or concepts from this passage.
For each one you find:

1. **label**: Short name (2-5 words)
2. **statement**: What it says (1-2 sentences, clear and concise)
3. **category**: Type of principle - choose from:
   - strategic_framework
   - tactical_principle  
   - command_doctrine
   - decision_cycle
   - force_employment
   - operational_concept
4. **applicability**: universal, period-specific, or culture-specific
5. **confidence**: How clearly stated? (0.7-1.0)

Return ONLY a JSON array. If no clear principles, return [].

Example:
[
  {{
    "label": "Economy of Force",
    "statement": "Allocate minimum combat power to secondary efforts to maximize power at decisive point",
    "category": "force_employment",
    "applicability": "universal",
    "confidence": 0.92
  }}
]

Discover what THIS passage actually says. Do NOT impose pre-conceived frameworks.
"""
        
        # Use Claude to discover principles from text
        principles = []
        
        try:
            # Call Claude via base class method (if available)
            if hasattr(self, 'anthropic_client') and self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",  # Claude 3 Sonnet (base model)
                    max_tokens=2000,
                    system="You are a military theory analyst extracting universal principles from literature. Return ONLY valid JSON array.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse response
                import json
                response_text = response.content[0].text
                
                # Extract JSON from response (might have markdown formatting)
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0].strip()
                
                principles = json.loads(response_text)
                
                if not isinstance(principles, list):
                    principles = []
            else:
                print("[WARN] Claude API not configured - no principles discovered")
                
        except Exception as e:
            print(f"[WARN] Theory discovery error: {e}")
            principles = []
        
        # Create discovered principles
        created_principles = []
        for principle in principles:
            principle_id = self._create_theory_principle(
                principle=principle,
                source_ref=source_ref,
                theorist=theorist
            )
            
            # Submit claim about discovery
            self.submit_theory_claim(
                principle_id=principle_id,
                predicate='defines_principle',
                confidence=principle['confidence'],
                source_ref=source_ref
            )
            
            created_principles.append({
                'principle_id': principle_id,
                'label': principle['label']
            })
        
        return created_principles
    
    def _create_theory_principle(
        self,
        principle: Dict,
        source_ref: str,
        theorist: Optional[str] = None
    ) -> str:
        """
        Create MilitaryPrinciple node for discovered theory.
        
        Args:
            principle: Dict with label, statement, category, applicability
            source_ref: Source citation
            theorist: Author name
        
        Returns:
            principle_id
        """
        import hashlib
        
        # Generate ID from category + label
        content = f"{principle['category']}_{principle['label']}"
        principle_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        principle_id = f"mt_{principle['category']}_{principle_hash}"
        
        with self.driver.session() as session:
            session.run("""
                MERGE (mp:MilitaryPrinciple {principle_id: $principle_id})
                SET mp.label = $label,
                    mp.statement = $statement,
                    mp.category = $category,
                    mp.applicability = $applicability,
                    mp.subject = 'military_theory',
                    mp.discovered_from = $source_ref,
                    mp.discovered_by = $agent_id,
                    mp.theorist = $theorist,
                    mp.discovered_at = datetime()
            """,
            principle_id=principle_id,
            label=principle['label'],
            statement=principle['statement'],
            category=principle['category'],
            applicability=principle['applicability'],
            source_ref=source_ref,
            agent_id=self.agent_id,
            theorist=theorist
            )
        
        return principle_id
    
    def submit_theory_claim(
        self,
        principle_id: str,
        predicate: str,
        confidence: float,
        source_ref: str,
        **kwargs
    ) -> str:
        """
        Submit claim about a military theory principle.
        
        Args:
            principle_id: The MilitaryPrinciple node ID
            predicate: One of THEORY_PREDICATES
            confidence: [0.0-1.0]
            source_ref: Citation
            **kwargs: Additional metadata
        
        Returns:
            Claim ID
        """
        if predicate not in self.THEORY_PREDICATES:
            raise ValueError(f"Unknown theory predicate: {predicate}. Valid: {self.THEORY_PREDICATES}")
        
        # Create claim relationship
        with self.driver.session() as session:
            session.run("""
                MATCH (mp:MilitaryPrinciple {principle_id: $principle_id})
                MERGE (a:Agent {agent_id: $agent_id})
                MERGE (a)-[c:ASSERTS {
                    predicate: $predicate,
                    facet: 'MILITARY',
                    confidence: $confidence,
                    source_ref: $source_ref,
                    target_subject: 'military_theory',
                    submitted_at: datetime()
                }]->(mp)
            """,
            principle_id=principle_id,
            agent_id=self.agent_id,
            predicate=predicate,
            confidence=confidence,
            source_ref=source_ref
            )
        
        return f"{self.agent_id}_{principle_id}_MILITARY"
    
    def link_event_to_theory(
        self,
        event_qid: str,
        principle_id: str,
        predicate: str,
        confidence: float,
        analysis: str,
        source_ref: str,
        **kwargs
    ) -> str:
        """
        Link historical event to theoretical principle.
        
        Cross-SubjectConcept claim: ROMAN_REPUBLIC event → MILITARY_THEORY principle
        
        Args:
            event_qid: Wikidata QID of historical event
            principle_id: MilitaryPrinciple ID
            predicate: One of LINKING_PREDICATES
            confidence: [0.0-1.0]
            analysis: How the event relates to the theory
            source_ref: Citation for the link
        
        Returns:
            Claim ID
        """
        if predicate not in self.LINKING_PREDICATES:
            raise ValueError(f"Unknown linking predicate: {predicate}. Valid: {self.LINKING_PREDICATES}")
        
        return self.claim_registry.submit_claim(
            entity={'type': 'EVENT', 'qid': event_qid},
            predicate=predicate,
            facet='MILITARY',
            agent_id=self.agent_id,
            confidence=confidence,
            source_ref=source_ref,
            principle_applied=principle_id,
            cross_subject_link=True,
            framework_analysis=analysis,
            **kwargs
        )


# ─────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────

def create_military_sfa_enhanced(driver) -> MilitarySFAEnhanced:
    """
    Create enhanced MilitarySFA instance.
    
    Args:
        driver: Neo4j driver instance
    
    Returns:
        MilitarySFAEnhanced instance
    """
    return MilitarySFAEnhanced(driver)


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    
    load_dotenv()
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    # Create enhanced Military SFA
    military = MilitarySFAEnhanced(driver)
    
    # Example: Submit claim with source weighting
    claim_id = military.submit_military_claim(
        entity={
            'type': 'EVENT',
            'qid': 'Q36456',  # Battle of Cannae
            'label': 'Battle of Cannae'
        },
        predicate='employed_tactic',
        confidence=0.95,
        source_ref='Polybius 3.107-117'  # Tier 1, weight 1.0
    )
    
    print(f"Submitted claim: {claim_id}")
    print(military.get_source_tier_explanation('Polybius 3.107-117'))
    
    # Example with anachronism risk
    claim_id2 = military.submit_military_claim(
        entity={
            'type': 'CONCEPT',
            'qid': 'Q170134',  # Roman legion
            'label': 'Roman legion'
        },
        predicate='reflects_organizational_structure',
        confidence=0.85,
        source_ref='Vegetius, Epitoma 2.1-15'  # Tier 1, but anachronism risk!
    )
    
    print(f"\nSubmitted claim: {claim_id2}")
    print(military.get_source_tier_explanation('Vegetius, Epitoma 2.1-15'))
    
    driver.close()
