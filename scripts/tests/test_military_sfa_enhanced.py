"""
Tests for Enhanced Military SFA with Perplexity Source Tiering

Tests:
- Source tier evaluation
- Anachronism risk flagging
- Confidence weighting by source quality
- Hierarchical predicate validation
- Enhanced claim metadata
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

from scripts.agents.military.agent_enhanced import MilitarySFAEnhanced


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
    """Create enhanced MilitarySFA instance."""
    return MilitarySFAEnhanced(neo4j_driver)


@pytest.fixture(scope="function")
def cleanup_test_data(neo4j_driver):
    """Clean up test data after each test."""
    yield
    
    with neo4j_driver.session() as session:
        # Clean up test entities
        session.run("""
            MATCH (e)
            WHERE e.qid CONTAINS '_ENHANCED_TEST'
            DETACH DELETE e
        """)
        
        session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e)
            WHERE e.qid CONTAINS '_ENHANCED_TEST'
            DELETE c
        """)


# ─────────────────────────────────────────────────────
# Source Tier Evaluation Tests
# ─────────────────────────────────────────────────────

def test_source_tier_polybius(military_sfa):
    """Test Polybius recognized as Tier 1, weight 1.0."""
    weight, risk, tier, info = military_sfa.evaluate_source_quality("Polybius 6.19-42")
    
    assert weight == 1.0
    assert risk == False
    assert 'tier1' in tier
    assert 'polybius' in tier
    assert info['specialty'] == 'Legion organization, maniple structure'


def test_source_tier_vegetius_anachronism(military_sfa):
    """Test Vegetius flagged for anachronism risk."""
    weight, risk, tier, info = military_sfa.evaluate_source_quality("Vegetius, Epitoma 2.1")
    
    assert weight == 0.75  # Lower weight due to late date
    assert risk == True  # ANACHRONISM RISK flagged
    assert 'tier1' in tier
    assert 'vegetius' in tier


def test_source_tier_sun_tzu(military_sfa):
    """Test Sun Tzu recognized as Tier 2."""
    weight, risk, tier, info = military_sfa.evaluate_source_quality("Sun Tzu, Art of War 3")
    
    assert weight == 0.75
    assert risk == False
    assert 'tier2' in tier


def test_source_tier_modern(military_sfa):
    """Test modern scholarship as Tier 3."""
    weight, risk, tier, info = military_sfa.evaluate_source_quality("Goldsworthy, Roman Army at War, p. 123")
    
    assert weight == 0.70
    assert risk == False
    assert 'tier3' in tier


def test_source_tier_unknown(military_sfa):
    """Test unknown source defaults to Tier 3."""
    weight, risk, tier, info = military_sfa.evaluate_source_quality("Unknown source")
    
    assert weight == 0.65
    assert risk == False
    assert 'tier3' in tier


# ─────────────────────────────────────────────────────
# Predicate Hierarchy Tests
# ─────────────────────────────────────────────────────

def test_all_predicates(military_sfa):
    """Test all predicates returned correctly."""
    predicates = military_sfa.get_all_predicates()
    
    # Should include all categories
    assert 'triggered_conflict' in predicates  # Strategic
    assert 'employed_tactic' in predicates     # Tactical
    assert 'illustrates_military_doctrine' in predicates  # Doctrinal
    assert 'demonstrated_command_quality' in predicates   # Leadership
    assert 'participated_in_battle' in predicates        # Operational
    
    # Total should be 30+
    assert len(predicates) >= 30


def test_predicate_categorization(military_sfa):
    """Test predicate category detection."""
    assert military_sfa.get_predicate_category('triggered_conflict') == 'strategic'
    assert military_sfa.get_predicate_category('employed_tactic') == 'tactical'
    assert military_sfa.get_predicate_category('illustrates_military_doctrine') == 'doctrinal'
    assert military_sfa.get_predicate_category('demonstrated_command_quality') == 'leadership'
    assert military_sfa.get_predicate_category('participated_in_battle') == 'operational'


def test_invalid_predicate_rejected(military_sfa, cleanup_test_data):
    """Test invalid predicates are rejected."""
    with pytest.raises(ValueError) as exc_info:
        military_sfa.submit_military_claim(
            entity={'type': 'EVENT', 'qid': 'Q_TEST', 'label': 'Test'},
            predicate='invalid_predicate',
            confidence=0.8
        )
    
    assert 'Unknown military predicate' in str(exc_info.value)


# ─────────────────────────────────────────────────────
# Confidence Weighting Tests
# ─────────────────────────────────────────────────────

def test_confidence_weighting_tier1(military_sfa, neo4j_driver, cleanup_test_data):
    """Test confidence weighted by Tier 1 source."""
    claim_id = military_sfa.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q36456_ENHANCED_TEST', 'label': 'Battle of Cannae'},
        predicate='employed_tactic',
        confidence=0.90,
        source_ref='Polybius 3.107-117',  # weight 1.0
        apply_source_weighting=True
    )
    
    # Verify claim created with weighted confidence
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q36456_ENHANCED_TEST'})
            RETURN c.confidence as confidence, c.source_tier as tier
        """)
        
        record = result.single()
        assert record is not None
        # 0.90 * 1.0 = 0.90
        assert abs(record['confidence'] - 0.90) < 0.01
        assert 'tier1_polybius' in record['tier']


def test_confidence_weighting_vegetius(military_sfa, neo4j_driver, cleanup_test_data):
    """Test confidence weighted down by Vegetius (anachronism risk)."""
    claim_id = military_sfa.submit_military_claim(
        entity={'type': 'CONCEPT', 'qid': 'Q170134_ENHANCED_TEST', 'label': 'Roman legion'},
        predicate='reflects_organizational_structure',
        confidence=0.90,
        source_ref='Vegetius 2.1-15',  # weight 0.75, anachronism risk
        apply_source_weighting=True
    )
    
    # Verify weighted confidence and anachronism flag
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q170134_ENHANCED_TEST'})
            RETURN 
                c.confidence as confidence,
                c.anachronism_risk as risk,
                c.source_tier as tier
        """)
        
        record = result.single()
        assert record is not None
        # 0.90 * 0.75 = 0.675
        assert abs(record['confidence'] - 0.675) < 0.01
        assert record['risk'] == True  # Anachronism risk flagged
        assert 'tier1_vegetius' in record['tier']


def test_confidence_no_weighting(military_sfa, neo4j_driver, cleanup_test_data):
    """Test confidence not weighted when apply_source_weighting=False."""
    claim_id = military_sfa.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q_TEST_NO_WEIGHT', 'label': 'Test Event'},
        predicate='employed_tactic',
        confidence=0.90,
        source_ref='Polybius 3.107',
        apply_source_weighting=False  # Disable weighting
    )
    
    # Verify confidence unchanged
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q_TEST_NO_WEIGHT'})
            RETURN c.confidence as confidence, c.source_weight_applied as weight_applied
        """)
        
        record = result.single()
        assert record is not None
        assert abs(record['confidence'] - 0.90) < 0.01  # Unchanged
        assert record['weight_applied'] == 1.0


# ─────────────────────────────────────────────────────
# Enhanced Metadata Tests
# ─────────────────────────────────────────────────────

def test_enhanced_metadata(military_sfa, neo4j_driver, cleanup_test_data):
    """Test enhanced metadata added to claims."""
    claim_id = military_sfa.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q_METADATA_TEST', 'label': 'Test Battle'},
        predicate='triggered_conflict',
        confidence=0.85,
        source_ref='Caesar, BGC 1.7-8'
    )
    
    # Verify all enhanced metadata present
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q_METADATA_TEST'})
            RETURN 
                c.source_tier as tier,
                c.anachronism_risk as risk,
                c.predicate_category as category,
                c.source_weight_applied as weight,
                c.source_specialty as specialty
        """)
        
        record = result.single()
        assert record is not None
        assert 'tier1' in record['tier']
        assert record['risk'] == False
        assert record['category'] == 'strategic'
        assert record['weight'] == 1.0
        assert 'Operational accounts' in record['specialty']


# ─────────────────────────────────────────────────────
# Source Explanation Tests
# ─────────────────────────────────────────────────────

def test_source_explanation(military_sfa):
    """Test source tier explanation generation."""
    explanation = military_sfa.get_source_tier_explanation('Polybius 6.19-42')
    
    assert 'Polybius 6.19-42' in explanation
    assert 'Tier: tier1_polybius' in explanation
    assert 'Weight: 1.0' in explanation
    assert '200-118 BCE' in explanation


def test_source_explanation_anachronism(military_sfa):
    """Test anachronism warning in explanation."""
    explanation = military_sfa.get_source_tier_explanation('Vegetius 2.1')
    
    assert 'ANACHRONISM RISK' in explanation
    assert 'later period' in explanation.lower()


# ─────────────────────────────────────────────────────
# Integration Test
# ─────────────────────────────────────────────────────

def test_full_enhanced_workflow(military_sfa, neo4j_driver, cleanup_test_data):
    """Test complete enhanced workflow."""
    # 1. Submit claim with Tier 1 source
    claim1 = military_sfa.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q_WORKFLOW_TEST', 'label': 'Battle of Zama'},
        predicate='resulted_in_strategic_outcome',
        confidence=0.92,
        source_ref='Polybius 15.9-16',
        source_qid='Q1747689'
    )
    
    # 2. Submit claim with Vegetius (anachronism risk)
    claim2 = military_sfa.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q_WORKFLOW_TEST', 'label': 'Battle of Zama'},
        predicate='illustrates_military_doctrine',
        confidence=0.80,
        source_ref='Vegetius 3.14'
    )
    
    # 3. Verify both claims created with correct metadata
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q_WORKFLOW_TEST'})
            RETURN 
                c.predicate as predicate,
                c.confidence as confidence,
                c.anachronism_risk as risk,
                c.predicate_category as category
            ORDER BY c.confidence DESC
        """)
        
        records = list(result)
        assert len(records) == 2
        
        # First claim (Polybius, high confidence)
        assert records[0]['predicate'] == 'resulted_in_strategic_outcome'
        assert abs(records[0]['confidence'] - 0.92) < 0.01
        assert records[0]['risk'] == False
        assert records[0]['category'] == 'strategic'
        
        # Second claim (Vegetius, lower confidence, anachronism)
        assert records[1]['predicate'] == 'illustrates_military_doctrine'
        assert abs(records[1]['confidence'] - 0.60) < 0.01  # 0.80 * 0.75
        assert records[1]['risk'] == True
        assert records[1]['category'] == 'doctrinal'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
