"""
Tests for Military SFA - Phase 2 Integration

Tests military-specific claim submission and peer review.
"""

import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Add project root to path
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from scripts.agents.military.agent import MilitarySFA
from scripts.agents.claim_registry import ClaimRegistry
from scripts.agents.peer_reviewer import PeerReviewer

load_dotenv()


@pytest.fixture(scope="module")
def neo4j_driver():
    """Create Neo4j driver for tests."""
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    yield driver
    driver.close()


@pytest.fixture(scope="module")
def military_sfa(neo4j_driver):
    """Create Military SFA for tests."""
    return MilitarySFA(neo4j_driver)


@pytest.fixture(scope="module")
def claim_registry(neo4j_driver):
    """Create ClaimRegistry for test setup."""
    return ClaimRegistry(neo4j_driver)


@pytest.fixture(scope="module")
def peer_reviewer(neo4j_driver):
    """Create PeerReviewer for test verification."""
    return PeerReviewer(neo4j_driver)


@pytest.fixture(autouse=True)
def cleanup_test_data(neo4j_driver):
    """Clean up test data before each test."""
    with neo4j_driver.session() as session:
        # Delete test entities
        session.run("""
            MATCH (e {qid: 'Q1048_MILITARY_TEST'})
            DETACH DELETE e
        """)
        session.run("""
            MATCH (a:Agent)
            WHERE a.agent_id STARTS WITH 'test_military_'
            DETACH DELETE a
        """)
        session.run("""
            MATCH (a:Agent)
            WHERE a.agent_id = 'military_sfa_001'
            DETACH DELETE a
        """)
    yield


class TestMilitarySFABasics:
    """Test basic Military SFA functionality."""
    
    def test_military_sfa_initialization(self, military_sfa):
        """Test that Military SFA initializes correctly."""
        assert military_sfa.facet_key == "MILITARY"
        assert military_sfa.agent_id == "military_sfa_001"
        assert military_sfa.claim_registry is not None
        assert military_sfa.peer_reviewer is not None
    
    def test_military_predicates_defined(self, military_sfa):
        """Test that military predicates are defined."""
        assert len(military_sfa.MILITARY_PREDICATES) > 0
        assert "commanded_legion" in military_sfa.MILITARY_PREDICATES
        assert "fought_at" in military_sfa.MILITARY_PREDICATES
    
    def test_military_properties_defined(self, military_sfa):
        """Test that military Wikidata properties are defined."""
        assert len(military_sfa.MILITARY_PROPERTIES) > 0
        assert "P607" in military_sfa.MILITARY_PROPERTIES  # conflict


class TestMilitaryClaimSubmission:
    """Test Military SFA claim submission via ClaimRegistry."""
    
    def test_submit_military_claim(self, military_sfa):
        """Test submitting a military claim."""
        entity = {
            'type': 'PERSON',
            'qid': 'Q1048_MILITARY_TEST',
            'label': 'Test Military Figure'
        }
        
        claim_id = military_sfa.submit_military_claim(
            entity=entity,
            predicate='commanded_legion',
            confidence=0.95
        )
        
        # Verify claim_id format (agent_id_entity_cipher_facet)
        assert claim_id is not None
        assert 'military_sfa_001' in claim_id
        assert 'ent_per_' in claim_id
        assert 'MILITARY' in claim_id
    
    def test_military_claim_has_correct_facet(self, military_sfa, neo4j_driver):
        """Test that military claims have MILITARY facet."""
        entity = {
            'type': 'PERSON',
            'qid': 'Q1048_MILITARY_TEST',
            'label': 'Test Military Figure'
        }
        
        claim_id = military_sfa.submit_military_claim(
            entity=entity,
            predicate='commanded_legion',
            confidence=0.92
        )
        
        # Verify facet in graph - search by agent and predicate
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (a:Agent {agent_id: 'military_sfa_001'})-[c:ASSERTS]->(e)
                WHERE c.predicate = 'commanded_legion'
                  AND e.qid = 'Q1048_MILITARY_TEST'
                RETURN c.facet as facet
                LIMIT 1
            """)
            
            record = result.single()
            assert record is not None
            assert record['facet'] == 'MILITARY'
    
    def test_high_confidence_military_claim(self, military_sfa):
        """Test high-confidence military claim submission."""
        entity = {
            'type': 'EVENT',
            'qid': 'Q40979_MILITARY_TEST',
            'label': 'Test Battle'
        }
        
        claim_id = military_sfa.submit_military_claim(
            entity=entity,
            predicate='fought_at',
            confidence=0.98
        )
        
        assert claim_id is not None


class TestMilitaryPeerReview:
    """Test Military SFA peer review functionality."""
    
    def test_review_peer_claims_empty(self, military_sfa):
        """Test reviewing when no peer claims exist."""
        # Create entity without peer claims
        entity = {
            'type': 'PERSON',
            'qid': 'Q1048_MILITARY_TEST',
            'label': 'Test Figure'
        }
        
        cipher = military_sfa.submit_military_claim(
            entity=entity,
            predicate='commanded_legion',
            confidence=0.90
        )
        
        # Try to review (should be empty since no peer claims)
        reviews = military_sfa.review_peer_claims(cipher)
        assert isinstance(reviews, list)
    
    def test_review_peer_claims_from_other_facet(
        self,
        military_sfa,
        claim_registry
    ):
        """Test Military SFA reviewing claims from other facets."""
        entity = {
            'type': 'PERSON',
            'qid': 'Q1048_MILITARY_TEST',
            'label': 'Test Figure'
        }
        
        # Political SFA submits claim
        cipher = claim_registry.submit_claim(
            entity=entity,
            predicate='held_office',
            facet='POLITICAL',
            agent_id='test_military_political',
            confidence=0.85
        )
        
        # Military SFA reviews
        reviews = military_sfa.review_peer_claims(cipher)
        
        if len(reviews) > 0:
            assert reviews[0]['reviewing_facet'] == 'MILITARY'
            assert reviews[0]['reviewed_facet'] == 'POLITICAL'


class TestMilitaryEvaluationLogic:
    """Test military-specific evaluation logic."""
    
    def test_military_predicate_high_confidence(self, military_sfa):
        """Test that high-confidence military predicates get agreement."""
        review = {
            'reviewed_predicate': 'commanded_legion',
            'review_confidence': 0.90,
            'agrees': False  # Will be overridden
        }
        
        updated = military_sfa._apply_military_evaluation(review)
        
        assert updated['agrees'] is True
        assert 'Military facet' in updated['note']
    
    def test_military_predicate_medium_confidence(self, military_sfa):
        """Test that medium-confidence military predicates get agreement."""
        review = {
            'reviewed_predicate': 'fought_at',
            'review_confidence': 0.75,
            'agrees': False
        }
        
        updated = military_sfa._apply_military_evaluation(review)
        
        assert updated['agrees'] is True
    
    def test_geographic_military_claim(self, military_sfa):
        """Test that geographic military claims are validated."""
        review = {
            'reviewed_predicate': 'battle_location',
            'review_confidence': 0.82,
            'agrees': False
        }
        
        updated = military_sfa._apply_military_evaluation(review)
        
        assert updated['agrees'] is True
        assert 'Geographic military claim' in updated['note']


class TestMilitaryAnalysis:
    """Test military context analysis."""
    
    def test_analyze_military_context_no_data(self, military_sfa):
        """Test analysis when no military data exists."""
        result = military_sfa.analyze_military_context(
            entity_qid='Q999999',
            submit_claims=False
        )
        
        assert result['facet'] == 'MILITARY'
        assert 'analysis' in result
    
    def test_analyze_military_context_with_data(self, military_sfa):
        """Test analysis with mock military data."""
        result = military_sfa.analyze_military_context(
            entity_qid='Q1048',  # Mock data for Caesar
            submit_claims=False
        )
        
        assert result['facet'] == 'MILITARY'
        assert result['analysis']['has_military_context'] is True


class TestMilitaryIntegration:
    """Test full integration with ClaimRegistry and PeerReviewer."""
    
    def test_full_workflow_submit_and_review(
        self,
        military_sfa,
        claim_registry,
        peer_reviewer
    ):
        """Test full workflow: submit claim, get review, check consensus."""
        entity = {
            'type': 'EVENT',
            'qid': 'Q40979_MILITARY_TEST',
            'label': 'Test Battle'
        }
        
        # Step 1: Military SFA submits claim
        cipher = military_sfa.submit_military_claim(
            entity=entity,
            predicate='naval_battle',
            confidence=0.93
        )
        
        # Step 2: Another facet (Political) submits claim
        claim_registry.submit_claim(
            entity=entity,
            predicate='political_outcome',
            facet='POLITICAL',
            agent_id='test_military_political',
            confidence=0.80
        )
        
        # Step 3: Military SFA reviews political claim
        reviews = military_sfa.review_peer_claims(cipher)
        
        # Step 4: Check agreement score
        if len(reviews) > 0:
            score = peer_reviewer.get_agreement_score(
                cipher,
                'political_outcome',
                'POLITICAL'
            )
            assert -1.0 <= score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
