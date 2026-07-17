"""
Tests for Diplomatic Subject Facet Agent

Verifies:
- Initialization and Phase 2 integration
- Claim submission via ClaimRegistry
- Peer review via PeerReviewer
- Diplomatic evaluation logic
- Wikidata integration
"""

import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

load_dotenv()

from scripts.agents.diplomatic.agent import DiplomaticSFA


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
def diplomatic_sfa(neo4j_driver):
    """Create DiplomaticSFA instance."""
    return DiplomaticSFA(neo4j_driver)


@pytest.fixture(scope="function")
def cleanup_test_data(neo4j_driver):
    """Clean up test data after each test."""
    yield
    
    with neo4j_driver.session() as session:
        # Clean up test entities and claims
        session.run("""
            MATCH (e)
            WHERE e.qid IN ['Q170185_DIPLOMATIC_TEST', 'Q1048_DIPLOMATIC_TEST']
            DETACH DELETE e
        """)
        
        session.run("""
            MATCH (a:Agent {agent_id: 'diplomatic_sfa_001'})
                  -[c:ASSERTS]->
                  (e)
            WHERE e.qid CONTAINS '_DIPLOMATIC_TEST'
            DELETE c
        """)


# ─────────────────────────────────────────────────────
# Initialization Tests
# ─────────────────────────────────────────────────────

def test_diplomatic_sfa_initialization(diplomatic_sfa):
    """Test DiplomaticSFA initializes correctly."""
    assert diplomatic_sfa.agent_id == "diplomatic_sfa_001"
    assert diplomatic_sfa.facet_label == "Diplomatic"
    assert diplomatic_sfa.claim_registry is not None
    assert diplomatic_sfa.peer_reviewer is not None


def test_diplomatic_predicates_defined(diplomatic_sfa):
    """Test diplomatic predicates are defined."""
    assert len(diplomatic_sfa.DIPLOMATIC_PREDICATES) > 0
    assert 'signed_treaty' in diplomatic_sfa.DIPLOMATIC_PREDICATES
    assert 'formed_alliance' in diplomatic_sfa.DIPLOMATIC_PREDICATES
    assert 'declared_war' in diplomatic_sfa.DIPLOMATIC_PREDICATES
    assert 'state_visit' in diplomatic_sfa.DIPLOMATIC_PREDICATES


# ─────────────────────────────────────────────────────
# Claim Submission Tests
# ─────────────────────────────────────────────────────

def test_submit_diplomatic_claim(diplomatic_sfa, cleanup_test_data):
    """Test submitting a diplomatic claim."""
    claim_id = diplomatic_sfa.submit_diplomatic_claim(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185_DIPLOMATIC_TEST',
            'label': 'Treaty of Rome (Test)'
        },
        predicate='signed_treaty',
        confidence=0.92
    )
    
    # Verify claim_id format
    assert claim_id.startswith('diplomatic_sfa_001_')
    assert '_DIPLOMATIC' in claim_id


def test_submit_claim_with_source(diplomatic_sfa, cleanup_test_data):
    """Test claim submission with source metadata."""
    claim_id = diplomatic_sfa.submit_diplomatic_claim(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185_DIPLOMATIC_TEST',
            'label': 'Treaty of Rome (Test)'
        },
        predicate='signed_treaty',
        confidence=0.95,
        source_qid='Q123456',
        passage_locator='Chapter 3, Page 45'
    )
    
    assert claim_id is not None


def test_invalid_predicate_raises_error(diplomatic_sfa):
    """Test that invalid predicates raise ValueError."""
    with pytest.raises(ValueError) as exc_info:
        diplomatic_sfa.submit_diplomatic_claim(
            entity={
                'type': 'EVENT',
                'qid': 'Q170185_DIPLOMATIC_TEST',
                'label': 'Test'
            },
            predicate='invalid_predicate',
            confidence=0.8
        )
    
    assert 'Unknown diplomatic predicate' in str(exc_info.value)


# ─────────────────────────────────────────────────────
# Facet Verification Tests
# ─────────────────────────────────────────────────────

def test_diplomatic_claim_has_correct_facet(diplomatic_sfa, neo4j_driver, cleanup_test_data):
    """Test that submitted claims have DIPLOMATIC facet."""
    diplomatic_sfa.submit_diplomatic_claim(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185_DIPLOMATIC_TEST',
            'label': 'Treaty of Rome (Test)'
        },
        predicate='signed_treaty',
        confidence=0.93
    )
    
    # Query for the claim
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'diplomatic_sfa_001'})
                  -[c:ASSERTS]->
                  (e)
            WHERE c.predicate = 'signed_treaty'
              AND e.qid = 'Q170185_DIPLOMATIC_TEST'
            RETURN c.facet as facet
        """)
        
        record = result.single()
        assert record is not None
        assert record['facet'] == 'DIPLOMATIC'


# ─────────────────────────────────────────────────────
# Peer Review Tests
# ─────────────────────────────────────────────────────

def test_review_peer_claims(diplomatic_sfa, neo4j_driver, cleanup_test_data):
    """Test peer review functionality."""
    # Submit a claim
    diplomatic_sfa.submit_diplomatic_claim(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185_DIPLOMATIC_TEST',
            'label': 'Treaty of Rome (Test)'
        },
        predicate='signed_treaty',
        confidence=0.9
    )
    
    # Get the entity cipher
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (e {qid: 'Q170185_DIPLOMATIC_TEST'})
            RETURN e.entity_cipher as cipher
        """)
        record = result.single()
        entity_cipher = record['cipher']
    
    # Review the claims
    review = diplomatic_sfa.review_peer_claims(entity_cipher)
    
    assert review['entity_cipher'] == entity_cipher
    assert review['reviewer'] == 'diplomatic_sfa_001'
    assert 'reviews_submitted' in review
    assert 'contested_count' in review


# ─────────────────────────────────────────────────────
# Evaluation Logic Tests
# ─────────────────────────────────────────────────────

def test_evaluate_diplomatic_significance_base(diplomatic_sfa):
    """Test base diplomatic significance evaluation."""
    result = diplomatic_sfa.evaluate_diplomatic_significance(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185',
            'label': 'Treaty of Rome'
        }
    )
    
    assert 'confidence' in result
    assert 'factors' in result
    assert 'suggested_predicates' in result
    assert 0.0 <= result['confidence'] <= 1.0


def test_evaluate_with_wikidata_props(diplomatic_sfa):
    """Test evaluation with Wikidata properties."""
    result = diplomatic_sfa.evaluate_diplomatic_significance(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185',
            'label': 'Treaty of Rome'
        },
        wikidata_props={
            'P710': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],  # 5 participants
            'P793': ['Q123'],  # significant event
            'P1542': ['Q456']  # has effect
        }
    )
    
    assert result['confidence'] > 0.5  # Should be higher with significant properties
    assert len(result['factors']) > 0


def test_suggest_predicates_for_treaty(diplomatic_sfa):
    """Test predicate suggestions for treaty entities."""
    result = diplomatic_sfa.evaluate_diplomatic_significance(
        entity={
            'type': 'EVENT',
            'label': 'Treaty of Versailles'
        },
        wikidata_props={
            'P1056': ['Q789'],  # produced document
            'P710': ['Q1', 'Q2']  # 2 participants
        }
    )
    
    predicates = result['suggested_predicates']
    assert 'signed_treaty' in predicates or 'declared_peace' in predicates


def test_suggest_predicates_for_alliance(diplomatic_sfa):
    """Test predicate suggestions for alliance entities."""
    result = diplomatic_sfa.evaluate_diplomatic_significance(
        entity={
            'type': 'EVENT',
            'label': 'NATO Alliance'
        },
        wikidata_props={
            'P710': ['Q1', 'Q2', 'Q3']  # Multiple participants
        }
    )
    
    predicates = result['suggested_predicates']
    assert 'formed_alliance' in predicates


# ─────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────

def test_full_workflow(diplomatic_sfa, neo4j_driver, cleanup_test_data):
    """Test complete workflow: submit claim, verify, review."""
    # 1. Submit claim
    claim_id = diplomatic_sfa.submit_diplomatic_claim(
        entity={
            'type': 'EVENT',
            'qid': 'Q170185_DIPLOMATIC_TEST',
            'label': 'Treaty of Rome (Test)'
        },
        predicate='signed_treaty',
        confidence=0.95,
        source_qid='Q123456'
    )
    
    assert claim_id is not None
    
    # 2. Verify claim exists
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'diplomatic_sfa_001'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q170185_DIPLOMATIC_TEST'})
            RETURN 
                c.facet as facet,
                c.predicate as predicate,
                c.confidence as confidence,
                c.status as status
        """)
        
        record = result.single()
        assert record is not None
        assert record['facet'] == 'DIPLOMATIC'
        assert record['predicate'] == 'signed_treaty'
        assert record['confidence'] == 0.95
        assert record['status'] == 'TBD'
    
    # 3. Get entity cipher for review
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (e {qid: 'Q170185_DIPLOMATIC_TEST'})
            RETURN e.entity_cipher as cipher
        """)
        entity_cipher = result.single()['cipher']
    
    # 4. Review claims
    review = diplomatic_sfa.review_peer_claims(entity_cipher)
    assert review['entity_cipher'] == entity_cipher


def test_entity_deduplication(diplomatic_sfa, neo4j_driver, cleanup_test_data):
    """Test that submitting multiple claims about same entity doesn't duplicate."""
    entity = {
        'type': 'EVENT',
        'qid': 'Q1048_DIPLOMATIC_TEST',
        'label': 'Caesar Diplomatic Test'
    }
    
    # Submit two different claims about same entity
    claim1 = diplomatic_sfa.submit_diplomatic_claim(
        entity=entity,
        predicate='sent_envoy',
        confidence=0.85
    )
    
    claim2 = diplomatic_sfa.submit_diplomatic_claim(
        entity=entity,
        predicate='formed_alliance',
        confidence=0.90
    )
    
    # Verify only ONE entity node exists
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (e {qid: 'Q1048_DIPLOMATIC_TEST'})
            RETURN count(e) as count
        """)
        
        count = result.single()['count']
        assert count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
