"""
Peer Review Agent - Cross-Facet Claim Validation (Phase 2)

This agent implements the "Phase 2: Peer Review" workflow from ADR 022.
It validates claims from other facets and maintains agreement scores.

Two-Phase SFA Model:
- Phase 1 (Knowledge Acquisition): SFAs submit claims (status: TBD)
- Phase 2 (Peer Review): SFAs review peer claims, update status

Usage:
    from scripts.agents.peer_reviewer import PeerReviewer
    
    reviewer = PeerReviewer(neo4j_driver)
    
    # Review all pending claims for an entity
    reviews = reviewer.review_entity_claims(
        entity_cipher='ent_per_Q1048',
        reviewing_facet='POLITICAL',
        reviewing_agent='political_sfa_001'
    )
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from neo4j import Driver
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeerReviewer:
    """
    Peer Review Agent - validates claims from other facets.
    
    Core workflow:
    1. Find claims from other facets about shared entities
    2. Evaluate agreement from this facet's perspective
    3. Write :REVIEWED edges with agreement/disagreement
    4. Update claim status based on consensus
    """
    
    # Promotion thresholds (configurable)
    CONFIDENCE_THRESHOLD_PROPOSED = 0.70
    AGREEMENT_THRESHOLD_CONFIRMED = 0.80
    MIN_REVIEW_COUNT = 2  # Minimum reviews before promotion
    DISAGREEMENT_THRESHOLD_CONTESTED = 0.40  # Below this = contested
    
    def __init__(self, neo4j_driver: Driver):
        """
        Initialize Peer Reviewer.
        
        Args:
            neo4j_driver: Neo4j driver instance
        """
        self.driver = neo4j_driver
    
    def review_entity_claims(
        self,
        entity_cipher: str,
        reviewing_facet: str,
        reviewing_agent: str,
        subjectconcept_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Review all claims from other facets about a specific entity.
        
        Args:
            entity_cipher: Entity to review claims for
            reviewing_facet: Facet conducting the review
            reviewing_agent: Agent ID conducting review
            subjectconcept_id: Optional SubjectConcept filter
        
        Returns:
            List of review results
        """
        # Get claims from OTHER facets
        peer_claims = self._get_peer_claims(
            entity_cipher,
            reviewing_facet,
            subjectconcept_id
        )
        
        if not peer_claims:
            logger.info(f"No peer claims found for {entity_cipher} from {reviewing_facet}")
            return []
        
        logger.info(f"Found {len(peer_claims)} peer claims to review for {entity_cipher}")
        
        reviews = []
        for claim in peer_claims:
            review = self._evaluate_claim(
                claim,
                reviewing_facet,
                reviewing_agent
            )
            reviews.append(review)
            
            # Write review to graph
            self._submit_review(review)
            
            # Update claim status if thresholds met
            self._update_claim_status_if_ready(claim)
        
        return reviews
    
    def get_agreement_score(
        self,
        entity_cipher: str,
        claim_predicate: str,
        facet: str
    ) -> float:
        """
        Calculate agreement score for a specific claim.
        
        Agreement score = (agrees - disagrees) / total_reviews
        Range: -1.0 (all disagree) to +1.0 (all agree)
        
        Args:
            entity_cipher: Entity the claim is about
            claim_predicate: Predicate being claimed
            facet: Facet that made the claim
        
        Returns:
            Agreement score [-1.0, +1.0]
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e {entity_cipher: $cipher})
                OPTIONAL MATCH (e)<-[r:REVIEWED {
                    reviewed_facet: $facet,
                    reviewed_predicate: $predicate
                }]-()
                WITH count(r) as total_reviews,
                     sum(CASE WHEN r.agrees = true THEN 1 ELSE 0 END) as agrees,
                     sum(CASE WHEN r.agrees = false THEN 1 ELSE 0 END) as disagrees
                RETURN 
                    total_reviews,
                    agrees,
                    disagrees,
                    CASE 
                        WHEN total_reviews = 0 THEN 0.0
                        ELSE toFloat(agrees - disagrees) / total_reviews
                    END as agreement_score
            """, cipher=entity_cipher, predicate=claim_predicate, facet=facet)
            
            record = result.single()
            if record:
                return record['agreement_score']
            return 0.0
    
    def find_contested_claims(
        self,
        min_reviews: int = 2,
        max_agreement: float = 0.40
    ) -> List[Dict]:
        """
        Find claims with low agreement scores (contested).
        
        Args:
            min_reviews: Minimum number of reviews required
            max_agreement: Maximum agreement score to be considered contested
        
        Returns:
            List of contested claims with details
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)<-[c:ASSERTS]-(a:Agent)
                WHERE c.status = 'PROPOSED' OR c.status = 'TBD'
                OPTIONAL MATCH (e)<-[r:REVIEWED {
                    reviewed_facet: c.facet,
                    reviewed_predicate: c.predicate
                }]-()
                WITH e, c, a,
                     count(r) as review_count,
                     sum(CASE WHEN r.agrees = true THEN 1 ELSE 0 END) as agrees,
                     sum(CASE WHEN r.agrees = false THEN 1 ELSE 0 END) as disagrees
                WHERE review_count >= $min_reviews
                WITH e, c, a, review_count, agrees, disagrees,
                     toFloat(agrees - disagrees) / review_count as agreement_score
                WHERE agreement_score <= $max_agreement
                RETURN 
                    e.entity_cipher as entity_cipher,
                    e.label as entity_label,
                    c.facet as facet,
                    c.predicate as predicate,
                    c.confidence as confidence,
                    a.agent_id as agent_id,
                    review_count,
                    agrees,
                    disagrees,
                    agreement_score
                ORDER BY agreement_score ASC, review_count DESC
            """, min_reviews=min_reviews, max_agreement=max_agreement)
            
            return [dict(record) for record in result]
    
    def promote_high_agreement_claims(
        self,
        min_agreement: float = 0.80,
        min_reviews: int = 2
    ) -> int:
        """
        Promote claims with high agreement to CONFIRMED status.
        
        Args:
            min_agreement: Minimum agreement score for promotion
            min_reviews: Minimum number of reviews required
        
        Returns:
            Number of claims promoted
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)<-[c:ASSERTS]-(a:Agent)
                WHERE c.status = 'PROPOSED' OR c.status = 'TBD'
                OPTIONAL MATCH (e)<-[r:REVIEWED {
                    reviewed_facet: c.facet,
                    reviewed_predicate: c.predicate
                }]-()
                WITH c,
                     count(r) as review_count,
                     sum(CASE WHEN r.agrees = true THEN 1 ELSE 0 END) as agrees,
                     sum(CASE WHEN r.agrees = false THEN 1 ELSE 0 END) as disagrees
                WHERE review_count >= $min_reviews
                WITH c, review_count, agrees, disagrees,
                     toFloat(agrees - disagrees) / review_count as agreement_score
                WHERE agreement_score >= $min_agreement
                SET c.status = 'CONFIRMED',
                    c.agreement_score = agreement_score,
                    c.review_count = review_count,
                    c.promoted_at = datetime()
                RETURN count(c) as promoted_count
            """, min_agreement=min_agreement, min_reviews=min_reviews)
            
            record = result.single()
            count = record['promoted_count'] if record else 0
            
            if count > 0:
                logger.info(f"Promoted {count} claims to CONFIRMED")
            
            return count
    
    def flag_contested_claims(
        self,
        max_agreement: float = 0.40,
        min_reviews: int = 2
    ) -> int:
        """
        Flag claims with low agreement as CONTESTED.
        
        Args:
            max_agreement: Maximum agreement score to flag as contested
            min_reviews: Minimum number of reviews required
        
        Returns:
            Number of claims flagged
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)<-[c:ASSERTS]-(a:Agent)
                WHERE c.status = 'PROPOSED' OR c.status = 'TBD'
                OPTIONAL MATCH (e)<-[r:REVIEWED {
                    reviewed_facet: c.facet,
                    reviewed_predicate: c.predicate
                }]-()
                WITH c,
                     count(r) as review_count,
                     sum(CASE WHEN r.agrees = true THEN 1 ELSE 0 END) as agrees,
                     sum(CASE WHEN r.agrees = false THEN 1 ELSE 0 END) as disagrees
                WHERE review_count >= $min_reviews
                WITH c, review_count, agrees, disagrees,
                     toFloat(agrees - disagrees) / review_count as agreement_score
                WHERE agreement_score <= $max_agreement
                SET c.status = 'CONTESTED',
                    c.agreement_score = agreement_score,
                    c.review_count = review_count,
                    c.contested_at = datetime()
                RETURN count(c) as contested_count
            """, max_agreement=max_agreement, min_reviews=min_reviews)
            
            record = result.single()
            count = record['contested_count'] if record else 0
            
            if count > 0:
                logger.info(f"Flagged {count} claims as CONTESTED")
            
            return count
    
    # ─────────────────────────────────────────────────────
    # Private Helper Methods
    # ─────────────────────────────────────────────────────
    
    def _get_peer_claims(
        self,
        entity_cipher: str,
        reviewing_facet: str,
        subjectconcept_id: Optional[str]
    ) -> List[Dict]:
        """Get claims from other facets about this entity."""
        with self.driver.session() as session:
            query = """
                MATCH (e {entity_cipher: $cipher})<-[c:ASSERTS]-(a:Agent)
                WHERE c.facet <> $reviewing_facet
                  AND (c.status = 'TBD' OR c.status = 'PROPOSED')
                  AND ($sc_id IS NULL OR c.subjectconcept_id = $sc_id)
                RETURN 
                    e.entity_cipher as entity_cipher,
                    e.label as entity_label,
                    c.facet as facet,
                    c.predicate as predicate,
                    c.confidence as confidence,
                    c.status as status,
                    a.agent_id as agent_id,
                    c.source_qid as source_qid,
                    c.submitted_at as submitted_at,
                    id(c) as claim_id
            """
            
            result = session.run(
                query,
                cipher=entity_cipher,
                reviewing_facet=reviewing_facet,
                sc_id=subjectconcept_id
            )
            
            return [dict(record) for record in result]
    
    def _evaluate_claim(
        self,
        claim: Dict,
        reviewing_facet: str,
        reviewing_agent: str
    ) -> Dict:
        """
        Evaluate whether to agree/disagree with a peer's claim.
        
        Evaluation logic (can be customized per facet):
        - High confidence claims (>0.85): likely agree
        - Medium confidence (0.70-0.85): cautious agree
        - Low confidence (<0.70): likely disagree
        - Cross-facet consistency checks (future enhancement)
        
        Args:
            claim: Claim dict from peer facet
            reviewing_facet: Facet conducting review
            reviewing_agent: Agent ID
        
        Returns:
            Review dict with agreement decision
        """
        # Simple confidence-based evaluation
        # (In production, this would be facet-specific logic)
        confidence = claim['confidence']
        
        # Evaluate agreement
        if confidence >= 0.85:
            agrees = True
            review_confidence = 0.90
            note = f"High confidence claim from {claim['facet']}"
        elif confidence >= 0.70:
            agrees = True
            review_confidence = 0.75
            note = f"Moderate confidence claim from {claim['facet']}"
        else:
            agrees = False
            review_confidence = 0.60
            note = f"Low confidence claim from {claim['facet']}, needs verification"
        
        return {
            'claim_id': claim['claim_id'],
            'entity_cipher': claim['entity_cipher'],
            'reviewed_facet': claim['facet'],
            'reviewed_predicate': claim['predicate'],
            'reviewing_facet': reviewing_facet,
            'reviewing_agent': reviewing_agent,
            'agrees': agrees,
            'review_confidence': review_confidence,
            'note': note,
            'reviewed_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _submit_review(self, review: Dict):
        """Write review to graph as :REVIEWED edge pointing to entity with claim metadata."""
        with self.driver.session() as session:
            # Get or create reviewing agent
            session.run("""
                MERGE (reviewer:Agent {agent_id: $agent_id})
                ON CREATE SET 
                    reviewer.facet = $facet,
                    reviewer.created_at = datetime()
            """, agent_id=review['reviewing_agent'], facet=review['reviewing_facet'])
            
            # Create REVIEWED relationship to entity (not to claim relationship)
            # Include claim facet/predicate to identify which claim was reviewed
            session.run("""
                MATCH (e {entity_cipher: $entity_cipher})
                MATCH (reviewer:Agent {agent_id: $reviewer_id})
                CREATE (reviewer)-[r:REVIEWED {
                    reviewed_facet: $reviewed_facet,
                    reviewed_predicate: $reviewed_predicate,
                    agrees: $agrees,
                    confidence: $confidence,
                    note: $note,
                    reviewed_at: $reviewed_at
                }]->(e)
            """, 
                entity_cipher=review['entity_cipher'],
                reviewer_id=review['reviewing_agent'],
                reviewed_facet=review['reviewed_facet'],
                reviewed_predicate=review['reviewed_predicate'],
                agrees=review['agrees'],
                confidence=review['review_confidence'],
                note=review['note'],
                reviewed_at=review['reviewed_at']
            )
            
            logger.info(
                f"{review['reviewing_facet']} reviewed {review['reviewed_facet']} claim: "
                f"{'AGREES' if review['agrees'] else 'DISAGREES'}"
            )
    
    def _update_claim_status_if_ready(self, claim: Dict):
        """
        Update claim status if it has enough reviews.
        
        Status transitions:
        - TBD → PROPOSED (if confidence >= threshold)
        - PROPOSED → CONFIRMED (if agreement_score >= threshold AND review_count >= min)
        - PROPOSED → CONTESTED (if agreement_score <= threshold AND review_count >= min)
        """
        entity_cipher = claim['entity_cipher']
        predicate = claim['predicate']
        facet = claim['facet']
        
        # Get current review stats
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e {entity_cipher: $cipher})<-[c:ASSERTS {
                    predicate: $predicate,
                    facet: $facet
                }]-(a:Agent)
                OPTIONAL MATCH (e)<-[r:REVIEWED {
                    reviewed_facet: c.facet,
                    reviewed_predicate: c.predicate
                }]-()
                WITH c,
                     count(r) as review_count,
                     sum(CASE WHEN r.agrees = true THEN 1 ELSE 0 END) as agrees,
                     sum(CASE WHEN r.agrees = false THEN 1 ELSE 0 END) as disagrees
                RETURN 
                    c.status as current_status,
                    c.confidence as confidence,
                    review_count,
                    agrees,
                    disagrees,
                    CASE 
                        WHEN review_count = 0 THEN 0.0
                        ELSE toFloat(agrees - disagrees) / review_count
                    END as agreement_score
            """, cipher=entity_cipher, predicate=predicate, facet=facet)
            
            record = result.single()
            if not record:
                return
            
            current_status = record['current_status']
            confidence = record['confidence']
            review_count = record['review_count']
            agreement_score = record['agreement_score']
            
            new_status = None
            
            # TBD → PROPOSED (confidence-based)
            if current_status == 'TBD' and confidence >= self.CONFIDENCE_THRESHOLD_PROPOSED:
                new_status = 'PROPOSED'
            
            # PROPOSED → CONFIRMED (consensus-based)
            elif (current_status == 'PROPOSED' and 
                  review_count >= self.MIN_REVIEW_COUNT and
                  agreement_score >= self.AGREEMENT_THRESHOLD_CONFIRMED):
                new_status = 'CONFIRMED'
            
            # PROPOSED → CONTESTED (disagreement-based)
            elif (current_status == 'PROPOSED' and
                  review_count >= self.MIN_REVIEW_COUNT and
                  agreement_score <= self.DISAGREEMENT_THRESHOLD_CONTESTED):
                new_status = 'CONTESTED'
            
            # Update status if transition warranted
            if new_status:
                session.run("""
                    MATCH (e {entity_cipher: $cipher})<-[c:ASSERTS {
                        predicate: $predicate,
                        facet: $facet
                    }]-()
                    SET c.status = $new_status,
                        c.agreement_score = $agreement_score,
                        c.review_count = $review_count,
                        c.status_updated_at = datetime()
                """, 
                    cipher=entity_cipher,
                    predicate=predicate,
                    facet=facet,
                    new_status=new_status,
                    agreement_score=agreement_score,
                    review_count=review_count
                )
                
                logger.info(
                    f"Status updated: {current_status} → {new_status} "
                    f"(agreement: {agreement_score:.2f}, reviews: {review_count})"
                )


# ─────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────

def create_peer_reviewer(neo4j_uri: str, neo4j_user: str, neo4j_password: str) -> PeerReviewer:
    """
    Create PeerReviewer instance with Neo4j connection.
    
    Args:
        neo4j_uri: Neo4j connection URI
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
    
    Returns:
        PeerReviewer instance
    """
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    return PeerReviewer(driver)


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    reviewer = create_peer_reviewer(
        neo4j_uri=os.getenv('NEO4J_URI'),
        neo4j_user=os.getenv('NEO4J_USERNAME'),
        neo4j_password=os.getenv('NEO4J_PASSWORD')
    )
    
    # Example: Political SFA reviews claims about Caesar
    print("Example: Political SFA reviews peer claims about Caesar\n")
    
    reviews = reviewer.review_entity_claims(
        entity_cipher='ent_per_Q1048',
        reviewing_facet='POLITICAL',
        reviewing_agent='political_sfa_001'
    )
    
    print(f"\nReviewed {len(reviews)} claims")
    
    # Promote high-agreement claims
    promoted = reviewer.promote_high_agreement_claims(min_agreement=0.80, min_reviews=2)
    print(f"Promoted {promoted} claims to CONFIRMED")
    
    # Flag contested claims
    contested = reviewer.flag_contested_claims(max_agreement=0.40, min_reviews=2)
    print(f"Flagged {contested} claims as CONTESTED")
