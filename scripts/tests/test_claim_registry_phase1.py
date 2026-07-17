"""
Integration tests for Claim Registry Phase 1 (ADR 022)

Tests:
1. Entity deduplication (2 SFAs → 1 entity)
2. Claim submission with metadata
3. Cross-facet claims on same entity
4. Claim retrieval by facet/status
5. Status updates
"""

import pytest
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

from scripts.agents.claim_registry import ClaimRegistry, create_claim_registry

load_dotenv()


@pytest.fixture(scope="module")
def registry():
    """Create ClaimRegistry instance for tests."""
    reg = create_claim_registry(
        neo4j_uri=os.getenv('NEO4J_URI'),
        neo4j_user=os.getenv('NEO4J_USERNAME'),
        neo4j_password=os.getenv('NEO4J_PASSWORD')
    )
    yield reg
    reg.driver.close()


@pytest.fixture(scope="module")
def neo4j_driver():
    """Create Neo4j driver for direct queries."""
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    yield driver
    driver.close()


@pytest.fixture(autouse=True)
def cleanup_test_data(neo4j_driver):
    """Clean up test data before each test."""
    with neo4j_driver.session() as session:
        # Delete test entities and claims
        session.run("""
            MATCH (e {qid: 'Q40979_TEST'})
            DETACH DELETE e
        """)
        session.run("""
            MATCH (a:Agent)
            WHERE a.agent_id STARTS WITH 'test_'
            DETACH DELETE a
        """)
    yield


class TestEntityDeduplication:
    """Test that entity deduplication prevents fragmentation."""
    
    def test_two_sfas_one_entity(self, registry, neo4j_driver):
        """Two SFAs submitting same entity should create 1 node, 2 claims."""
        # Setup entity
        entity = {
            'type': 'EVENT',
            'qid': 'Q40979_TEST',
            'label': 'Caesar crossing Rubicon (test)',
            'date': '-49-01-10'
        }
        
        # Military SFA submits claim
        claim_id_1 = registry.submit_claim(
            entity=entity,
            predicate='military_escalation',
            facet='MILITARY',
            agent_id='test_military_sfa_001',
            confidence=0.90
        )
        
        # Bio SFA submits claim (SAME entity)
        claim_id_2 = registry.submit_claim(
            entity=entity,  # Same entity!
            predicate='career_defining_act',
            facet='BIOGRAPHIC',
            agent_id='test_bio_sfa_001',
            confidence=0.95
        )
        
        # Verify: 1 entity node
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (e {qid: 'Q40979_TEST'})
                RETURN count(e) as entity_count
            """)
            count = result.single()['entity_count']
            assert count == 1, f"Expected 1 entity, got {count}"
        
        # Verify: 2 claims
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (e {qid: 'Q40979_TEST'})<-[c:ASSERTS]-()
                RETURN count(c) as claim_count
            """)
            count = result.single()['claim_count']
            assert count == 2, f"Expected 2 claims, got {count}"
        
        # Verify: Claims from different facets
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (e {qid: 'Q40979_TEST'})<-[c:ASSERTS]-()
                RETURN collect(DISTINCT c.facet) as facets
            """)
            facets = result.single()['facets']
            assert set(facets) == {'MILITARY', 'BIOGRAPHIC'}
    
    def test_entity_cipher_deduplication(self, registry, neo4j_driver):
        """Entities with same cipher should deduplicate even without QID."""
        # Entity without QID (content-hash)
        entity = {
            'type': 'EVENT',
            'label': 'Test event without QID',
            'canonical_properties': {
                'name': 'Test event',
                'date': '-50',
                'location': 'Rome',
                'participants': 'Caesar'
            }
        }
        
        # First SFA
        claim_id_1 = registry.submit_claim(
            entity=entity,
            predicate='test_pred_1',
            facet='MILITARY',
            agent_id='test_sfa_1',
            confidence=0.80
        )
        
        # Second SFA (same canonical properties)
        claim_id_2 = registry.submit_claim(
            entity=entity,  # Same properties!
            predicate='test_pred_2',
            facet='POLITICAL',
            agent_id='test_sfa_2',
            confidence=0.85
        )
        
        # Extract cipher from first claim_id (format: agent_cipher_facet)
        entity_cipher = claim_id_1.split('_', 2)[1] + '_' + claim_id_1.split('_', 2)[2].rsplit('_', 1)[0]
        
        # Verify: 1 entity with that cipher
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (e)
                WHERE e.entity_cipher STARTS WITH 'ent_evt_'
                  AND e.label = 'Test event without QID'
                RETURN count(e) as count
            """)
            count = result.single()['count']
            assert count == 1, "Content-hash deduplication failed"


class TestClaimMetadata:
    """Test that claim metadata is properly stored."""
    
    def test_claim_has_required_metadata(self, registry, neo4j_driver):
        """Claim should have all required provenance fields."""
        entity = {
            'type': 'EVENT',
            'qid': 'Q40979_TEST',
            'label': 'Test event'
        }
        
        registry.submit_claim(
            entity=entity,
            predicate='test_predicate',
            facet='MILITARY',
            agent_id='test_agent_metadata',
            confidence=0.92,
            source_qid='Q123456',
            passage_locator='Plutarch, Caesar 32'
        )
        
        # Verify metadata
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (e {qid: 'Q40979_TEST'})<-[c:ASSERTS]-(a {agent_id: 'test_agent_metadata'})
                RETURN c
            """)
            claim = dict(result.single()['c'])
            
            assert claim['facet'] == 'MILITARY'
            assert claim['predicate'] == 'test_predicate'
            assert claim['confidence'] == 0.92
            assert claim['status'] == 'TBD'  # Default status
            assert claim['source_qid'] == 'Q123456'
            assert claim['passage_locator'] == 'Plutarch, Caesar 32'
            assert 'submitted_at' in claim
            assert claim['review_count'] == 0
    
    def test_igar_chain_stored(self, registry, neo4j_driver):
        """IGAR chain should be stored as metadata."""
        entity = {'type': 'EVENT', 'qid': 'Q40979_TEST', 'label': 'Test'}
        
        igar_chain = {
            'input': 'Test input',
            'goal': 'Test goal',
            'action': 'Test action',
            'result': 'Test result'
        }
        
        registry.submit_claim(
            entity=entity,
            predicate='test',
            facet='MILITARY',
            agent_id='test_igar_agent',
            confidence=0.85,
            igar_chain=igar_chain
        )
        
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (e {qid: 'Q40979_TEST'})<-[c:ASSERTS]-(a {agent_id: 'test_igar_agent'})
                RETURN c.igar_chain as igar
            """)
            stored_igar = result.single()['igar']
            assert stored_igar is not None
            assert 'input' in stored_igar


class TestClaimRetrieval:
    """Test claim retrieval and filtering."""
    
    def test_get_claims_for_entity(self, registry):
        """Should retrieve all claims for an entity."""
        entity = {'type': 'EVENT', 'qid': 'Q40979_TEST', 'label': 'Test'}
        
        # Submit 3 claims
        for i, facet in enumerate(['MILITARY', 'POLITICAL', 'BIOGRAPHIC']):
            registry.submit_claim(
                entity=entity,
                predicate=f'test_pred_{i}',
                facet=facet,
                agent_id=f'test_agent_{i}',
                confidence=0.80 + i*0.05
            )
        
        # Retrieve all claims
        claims = registry.get_claims_for_entity('ent_evt_Q40979_TEST')
        assert len(claims) == 3
        
        # Verify facets
        facets = {c['facet'] for c in claims}
        assert facets == {'MILITARY', 'POLITICAL', 'BIOGRAPHIC'}
    
    def test_filter_claims_by_facet(self, registry):
        """Should filter claims by specific facet."""
        entity = {'type': 'EVENT', 'qid': 'Q40979_TEST', 'label': 'Test'}
        
        registry.submit_claim(entity=entity, predicate='mil', facet='MILITARY', agent_id='test_m', confidence=0.9)
        registry.submit_claim(entity=entity, predicate='pol', facet='POLITICAL', agent_id='test_p', confidence=0.85)
        
        # Filter by MILITARY
        claims = registry.get_claims_for_entity('ent_evt_Q40979_TEST', facet='MILITARY')
        assert len(claims) == 1
        assert claims[0]['facet'] == 'MILITARY'


class TestStatusManagement:
    """Test claim status lifecycle."""
    
    def test_default_status_is_tbd(self, registry, neo4j_driver):
        """New claims should have status TBD."""
        entity = {'type': 'EVENT', 'qid': 'Q40979_TEST', 'label': 'Test'}
        
        registry.submit_claim(
            entity=entity,
            predicate='test',
            facet='MILITARY',
            agent_id='test_status_agent',
            confidence=0.90
        )
        
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH ()-[c:ASSERTS]->({qid: 'Q40979_TEST'})
                RETURN c.status as status
            """)
            status = result.single()['status']
            assert status == 'TBD'
    
    def test_update_claim_status(self, registry):
        """Should be able to update claim status."""
        entity = {'type': 'EVENT', 'qid': 'Q40979_TEST', 'label': 'Test'}
        
        registry.submit_claim(
            entity=entity,
            predicate='test',
            facet='MILITARY',
            agent_id='test_update_agent',
            confidence=0.90
        )
        
        # Update status
        success = registry.update_claim_status(
            entity_cipher='ent_evt_Q40979_TEST',
            agent_id='test_update_agent',
            new_status='CONFIRMED'
        )
        
        assert success is True
        
        # Verify update
        claims = registry.get_claims_for_entity('ent_evt_Q40979_TEST')
        assert claims[0]['status'] == 'CONFIRMED'


class TestErrorHandling:
    """Test error conditions."""
    
    def test_invalid_confidence(self, registry):
        """Should reject invalid confidence scores."""
        entity = {'type': 'EVENT', 'qid': 'Q40979_TEST', 'label': 'Test'}
        
        with pytest.raises(ValueError, match="Confidence must be 0.0-1.0"):
            registry.submit_claim(
                entity=entity,
                predicate='test',
                facet='MILITARY',
                agent_id='test',
                confidence=1.5  # Invalid!
            )
    
    def test_invalid_facet(self, registry):
        """Should reject unknown facets."""
        entity = {'type': 'EVENT', 'qid': 'Q40979_TEST', 'label': 'Test'}
        
        with pytest.raises(ValueError, match="Unknown facet"):
            registry.submit_claim(
                entity=entity,
                predicate='test',
                facet='INVALID_FACET',
                agent_id='test',
                confidence=0.90
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
