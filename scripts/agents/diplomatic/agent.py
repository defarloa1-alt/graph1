"""
Diplomatic Subject Facet Agent

Specialized SFA for diplomatic aspects:
- Treaties, alliances, peace agreements
- Diplomatic missions, embassies, envoys
- International relations, negotiations
- Declarations of war/peace
- State visits, summits, diplomatic correspondence
- Territorial exchanges, border agreements

Integrates with Phase 2 architecture:
- ClaimRegistry for entity deduplication and claim submission
- PeerReviewer for cross-facet validation
"""

from typing import Dict, Optional, List
from neo4j import Driver
import logging

from scripts.agents.subject_concept_facet_agents import SubjectConceptFacetAgent
from scripts.agents.claim_registry import ClaimRegistry
from scripts.agents.peer_reviewer import PeerReviewer

logger = logging.getLogger(__name__)


class DiplomaticSFA(SubjectConceptFacetAgent):
    """
    Subject Facet Agent for Diplomatic aspects.
    
    Evaluates diplomatic significance:
    - Treaty importance (bilateral vs multilateral, scope, duration)
    - Diplomatic innovation (new protocols, precedents)
    - Impact on international relations (alliance shifts, power balance)
    - Historical precedent (first of its kind, revolutionary)
    
    Integration:
    - Uses ClaimRegistry for canonical entity creation and claim submission
    - Uses PeerReviewer for cross-facet claim validation
    - Consults Wikidata for diplomatic event enrichment
    """
    
    # Diplomatic-specific predicates
    DIPLOMATIC_PREDICATES = [
        'signed_treaty',
        'formed_alliance',
        'declared_war',
        'declared_peace',
        'sent_envoy',
        'received_embassy',
        'negotiated_agreement',
        'territorial_exchange',
        'border_agreement',
        'diplomatic_recognition',
        'diplomatic_mission',
        'state_visit',
        'summit_participation',
        'diplomatic_correspondence',
        'treaty_violation',
        'diplomatic_incident',
        'mediation_effort',
        'peace_conference',
        'non_aggression_pact',
        'trade_agreement'
    ]
    
    # Properties relevant to diplomatic evaluation
    DIPLOMATIC_PROPERTIES = [
        'P793',   # significant event
        'P710',   # participant
        'P361',   # part of (larger diplomatic context)
        'P1343',  # described by source
        'P585',   # point in time
        'P580',   # start time
        'P582',   # end time
        'P276',   # location
        'P1056',  # product or material produced (treaty documents)
        'P2868',  # subject has role
        'P1399',  # convicted of (treaty violations)
        'P828',   # has cause
        'P1542',  # has effect
        'P2512',  # series ordinal (treaty/agreement sequence)
        'P825',   # dedicated to
    ]
    
    def __init__(self, driver: Driver):
        """
        Initialize Diplomatic SFA.
        
        Args:
            driver: Neo4j driver instance
        """
        super().__init__(
            facet_key="DIPLOMATIC",
            facet_label="Diplomatic",
            neo4j_driver=driver
        )
        
        # Override agent_id to match expected format
        self.agent_id = "diplomatic_sfa_001"
        
        # Initialize Phase 2 components
        self.claim_registry = ClaimRegistry(driver)
        self.peer_reviewer = PeerReviewer(driver)
        
        logger.info(f"Initialized {self.agent_id} with facet {self.facet_label}")
    
    def submit_diplomatic_claim(
        self,
        entity: Dict,
        predicate: str,
        confidence: float,
        source_qid: Optional[str] = None,
        source_uri: Optional[str] = None,
        passage_locator: Optional[str] = None,
        igar_chain: Optional[Dict] = None
    ) -> str:
        """
        Submit a diplomatic claim via ClaimRegistry.
        
        Args:
            entity: Entity dict with type, qid, label
            predicate: One of DIPLOMATIC_PREDICATES
            confidence: Confidence score [0.0-1.0]
            source_qid: Wikidata QID of source work
            source_uri: External source URI
            passage_locator: Specific passage reference
            igar_chain: IGAR chain dict (for actor-centric events)
        
        Returns:
            Claim ID from ClaimRegistry
        
        Raises:
            ValueError: If predicate is not in DIPLOMATIC_PREDICATES
        """
        if predicate not in self.DIPLOMATIC_PREDICATES:
            raise ValueError(
                f"Unknown diplomatic predicate: {predicate}. "
                f"Valid: {self.DIPLOMATIC_PREDICATES}"
            )
        
        return self.claim_registry.submit_claim(
            entity=entity,
            predicate=predicate,
            facet=self.facet_label,
            agent_id=self.agent_id,
            confidence=confidence,
            source_qid=source_qid,
            source_uri=source_uri,
            passage_locator=passage_locator,
            igar_chain=igar_chain
        )
    
    def review_peer_claims(
        self,
        entity_cipher: str,
        reviewer_agent_id: Optional[str] = None
    ) -> Dict:
        """
        Review claims about an entity from other SFAs.
        
        Args:
            entity_cipher: Entity to review claims for
            reviewer_agent_id: Override reviewer ID (defaults to this agent)
        
        Returns:
            Review summary dict with reviews submitted
        """
        reviewer_id = reviewer_agent_id or self.agent_id
        
        # Submit review via PeerReviewer
        reviews = self.peer_reviewer.review_entity_claims(
            entity_cipher=entity_cipher,
            reviewing_agent=reviewer_id,
            reviewing_facet=self.facet_label
        )
        
        # Find contested claims
        contested = self.peer_reviewer.find_contested_claims(entity_cipher)
        
        return {
            'entity_cipher': entity_cipher,
            'reviewer': reviewer_id,
            'reviews_submitted': len(reviews),
            'contested_count': len(contested),
            'contested_claims': contested
        }
    
    def evaluate_diplomatic_significance(
        self,
        entity: Dict,
        wikidata_props: Optional[Dict] = None
    ) -> Dict:
        """
        Evaluate the diplomatic significance of an entity/event.
        
        Scoring factors:
        - Treaty scope (bilateral=0.5, multilateral=0.8, universal=1.0)
        - Diplomatic innovation (new precedents=+0.2)
        - Historical impact (lasting effect=+0.2)
        - Parties involved (major powers=+0.1)
        
        Args:
            entity: Entity dict with type, qid, label
            wikidata_props: Optional Wikidata properties for enrichment
        
        Returns:
            Dict with confidence score and reasoning
        """
        confidence = 0.5  # Base confidence
        factors = []
        
        # Check for treaty/agreement scope
        if wikidata_props:
            participants = wikidata_props.get('P710', [])
            num_participants = len(participants)
            
            if num_participants >= 10:
                confidence += 0.3
                factors.append(f"Multilateral ({num_participants} parties)")
            elif num_participants >= 3:
                confidence += 0.2
                factors.append(f"Multiple parties ({num_participants})")
            elif num_participants == 2:
                confidence += 0.1
                factors.append("Bilateral agreement")
            
            # Check for historical significance markers
            if 'P793' in wikidata_props:  # significant event
                confidence += 0.15
                factors.append("Marked as significant event")
            
            # Check for lasting effects
            if 'P1542' in wikidata_props:  # has effect
                confidence += 0.1
                factors.append("Documented lasting effects")
            
            # Check for diplomatic incidents/violations
            if 'P1399' in wikidata_props:  # convicted of / violations
                confidence += 0.1
                factors.append("Diplomatic incident/violation")
        
        # Entity type-based adjustments
        entity_type = entity.get('type', '').upper()
        if entity_type == 'EVENT':
            confidence += 0.1
            factors.append("Event entity (likely diplomatic action)")
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        return {
            'confidence': confidence,
            'factors': factors,
            'suggested_predicates': self._suggest_predicates(entity, wikidata_props)
        }
    
    def _suggest_predicates(
        self,
        entity: Dict,
        wikidata_props: Optional[Dict]
    ) -> List[str]:
        """
        Suggest appropriate diplomatic predicates based on entity/properties.
        
        Args:
            entity: Entity dict
            wikidata_props: Wikidata properties
        
        Returns:
            List of suggested predicate strings
        """
        suggestions = []
        
        if not wikidata_props:
            return ['diplomatic_mission']  # Generic fallback
        
        # Check for treaty/agreement indicators
        if 'P1056' in wikidata_props:  # produced document
            suggestions.append('signed_treaty')
        
        # Check for alliance formation
        if 'P710' in wikidata_props:  # participants
            participants = wikidata_props['P710']
            if len(participants) >= 2:
                suggestions.append('formed_alliance')
        
        # Check for war/peace declarations
        label = entity.get('label', '').lower()
        if 'war' in label:
            suggestions.append('declared_war')
        elif 'peace' in label or 'treaty' in label:
            suggestions.append('declared_peace')
            suggestions.append('signed_treaty')
        elif 'alliance' in label:
            suggestions.append('formed_alliance')
        elif 'embassy' in label or 'envoy' in label:
            suggestions.append('sent_envoy')
        elif 'visit' in label:
            suggestions.append('state_visit')
        elif 'summit' in label or 'conference' in label:
            suggestions.append('summit_participation')
        
        return suggestions or ['diplomatic_mission']
    
    def enrich_from_wikidata(self, qid: str) -> Optional[Dict]:
        """
        Fetch diplomatic-relevant properties from Wikidata.
        
        Args:
            qid: Wikidata QID
        
        Returns:
            Dict of property_id -> values, or None if fetch fails
        """
        try:
            import requests
            
            url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Wikidata fetch failed for {qid}: {response.status_code}")
                return None
            
            data = response.json()
            entity_data = data.get('entities', {}).get(qid, {})
            claims = entity_data.get('claims', {})
            
            # Extract diplomatic-relevant properties
            relevant = {}
            for prop in self.DIPLOMATIC_PROPERTIES:
                if prop in claims:
                    relevant[prop] = claims[prop]
            
            return relevant
            
        except Exception as e:
            logger.error(f"Error fetching Wikidata for {qid}: {e}")
            return None


# ─────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────

def create_diplomatic_sfa(driver: Driver) -> DiplomaticSFA:
    """
    Create DiplomaticSFA instance.
    
    Args:
        driver: Neo4j driver instance
    
    Returns:
        DiplomaticSFA instance
    """
    return DiplomaticSFA(driver)


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    from neo4j import GraphDatabase
    
    load_dotenv()
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    # Create Diplomatic SFA
    diplomatic = DiplomaticSFA(driver)
    
    # Example: Submit claim about Treaty of Rome
    claim_id = diplomatic.submit_diplomatic_claim(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185',  # Treaty of Rome
            'label': 'Treaty of Rome'
        },
        predicate='signed_treaty',
        confidence=0.95
    )
    
    print(f"Submitted claim: {claim_id}")
    
    driver.close()
