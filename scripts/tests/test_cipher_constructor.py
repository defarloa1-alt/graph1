"""
Tests for CipherConstructor - LLM-Friendly Natural Language Interface

Tests the Phase 1.5 enhancement that enables LLMs to construct ciphers
from natural language queries without knowing cipher internals.
"""

import pytest
from unittest.mock import patch, MagicMock

from scripts.tools.entity_cipher import (
    construct_cipher_from_text,
    construct_vertex_jump,
    _normalize_facet_hint,
    _resolve_entity_name_to_qid,
    _infer_entity_type_from_qid
)


class TestFacetNormalization:
    """Test natural language facet hint normalization."""
    
    def test_direct_facet_match(self):
        assert _normalize_facet_hint("political") == "POLITICAL"
        assert _normalize_facet_hint("military") == "MILITARY"
        assert _normalize_facet_hint("economic") == "ECONOMIC"
    
    def test_case_insensitive(self):
        assert _normalize_facet_hint("POLITICAL") == "POLITICAL"
        assert _normalize_facet_hint("Political") == "POLITICAL"
        assert _normalize_facet_hint("PoLiTiCaL") == "POLITICAL"
    
    def test_synonyms(self):
        assert _normalize_facet_hint("politics") == "POLITICAL"
        assert _normalize_facet_hint("warfare") == "MILITARY"
        assert _normalize_facet_hint("war") == "MILITARY"
        assert _normalize_facet_hint("economy") == "ECONOMIC"
        assert _normalize_facet_hint("geography") == "GEOGRAPHIC"
        assert _normalize_facet_hint("geo") == "GEOGRAPHIC"
    
    def test_whitespace_handling(self):
        assert _normalize_facet_hint("  political  ") == "POLITICAL"
        assert _normalize_facet_hint("\teconomic\n") == "ECONOMIC"
    
    def test_invalid_facet(self):
        assert _normalize_facet_hint("invalid_facet") is None
        assert _normalize_facet_hint("temporal") is None
        assert _normalize_facet_hint("") is None


class TestWikidataResolution:
    """Test Wikidata entity name resolution."""
    
    @patch('scripts.tools.entity_cipher.requests.get')
    def test_resolve_julius_caesar(self, mock_get):
        # Mock Wikidata API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'search': [
                {'id': 'Q1048', 'label': 'Julius Caesar'}
            ]
        }
        mock_get.return_value = mock_response
        
        qid = _resolve_entity_name_to_qid("Julius Caesar")
        assert qid == "Q1048"
    
    @patch('scripts.tools.entity_cipher.requests.get')
    def test_resolve_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'search': []}
        mock_get.return_value = mock_response
        
        qid = _resolve_entity_name_to_qid("NonexistentEntity12345")
        assert qid is None
    
    @patch('scripts.tools.entity_cipher.requests.get')
    def test_resolve_api_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        
        qid = _resolve_entity_name_to_qid("Julius Caesar")
        assert qid is None


class TestEntityTypeInference:
    """Test entity type inference from QID."""
    
    @patch('scripts.tools.entity_cipher.requests.get')
    def test_infer_person_type(self, mock_get):
        # Mock SPARQL response for Person (P31: Q5)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': {
                'bindings': [
                    {'type': {'value': 'http://www.wikidata.org/entity/Q5'}}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        entity_type = _infer_entity_type_from_qid("Q1048")
        assert entity_type == "PERSON"
    
    @patch('scripts.tools.entity_cipher.requests.get')
    def test_infer_fallback_on_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        
        entity_type = _infer_entity_type_from_qid("Q999999")
        assert entity_type == "CONCEPT"  # Default fallback


class TestConstructCipherFromText:
    """Test main LLM-friendly cipher construction interface."""
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_simple_entity_lookup(self, mock_resolve):
        mock_resolve.return_value = "Q1048"
        
        result = construct_cipher_from_text("Julius Caesar")
        
        assert result['success'] is True
        assert result['qid'] == "Q1048"
        assert result['entity_cipher'] == "ent_per_Q1048"
        assert 'tier1_cypher' in result
        assert 'MATCH (n {entity_cipher: "ent_per_Q1048"})' in result['tier1_cypher']
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_entity_not_found(self, mock_resolve):
        mock_resolve.return_value = None
        
        result = construct_cipher_from_text("NonexistentEntity")
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Could not resolve' in result['error']
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_faceted_lookup(self, mock_resolve):
        mock_resolve.return_value = "Q1048"
        
        result = construct_cipher_from_text(
            "Julius Caesar",
            facet_hint="political",
            subjectconcept_id="Q17167"
        )
        
        assert result['success'] is True
        assert result['faceted_cipher'] == "fent_pol_Q1048_Q17167"
        assert result['facet'] == "POLITICAL"
        assert result['subjectconcept_id'] == "Q17167"
        assert 'tier2_cypher' in result
        assert 'faceted_cipher: "fent_pol_Q1048_Q17167"' in result['tier2_cypher']
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_facet_with_synonym(self, mock_resolve):
        mock_resolve.return_value = "Q1048"
        
        result = construct_cipher_from_text(
            "Julius Caesar",
            facet_hint="warfare",  # Synonym for MILITARY
            subjectconcept_id="Q17167"
        )
        
        assert result['facet'] == "MILITARY"
        assert result['faceted_cipher'] == "fent_mil_Q1048_Q17167"
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_invalid_facet_hint(self, mock_resolve):
        mock_resolve.return_value = "Q1048"
        
        result = construct_cipher_from_text(
            "Julius Caesar",
            facet_hint="invalid_facet",
            subjectconcept_id="Q17167"
        )
        
        assert result['success'] is True
        assert 'facet_warning' in result
        assert 'Could not normalize' in result['facet_warning']
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_recommended_query_tier1(self, mock_resolve):
        mock_resolve.return_value = "Q1048"
        
        result = construct_cipher_from_text("Julius Caesar")
        
        # Without facet context, should recommend Tier 1 query
        assert result['recommended_query'] == result['tier1_cypher']
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_recommended_query_tier2(self, mock_resolve):
        mock_resolve.return_value = "Q1048"
        
        result = construct_cipher_from_text(
            "Julius Caesar",
            facet_hint="political",
            subjectconcept_id="Q17167"
        )
        
        # With facet context, should recommend Tier 2 query
        assert result['recommended_query'] == result['tier2_cypher']


class TestConstructVertexJump:
    """Test cross-entity vertex jump construction."""
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_simple_vertex_jump(self, mock_resolve):
        # Mock resolution for both entities
        mock_resolve.side_effect = ["Q1048", "Q168811"]  # Caesar, Pompey
        
        result = construct_vertex_jump(
            "Julius Caesar",
            "Pompey",
            "political",
            "Q17167"
        )
        
        assert result['success'] is True
        assert result['from_cipher'] == "fent_pol_Q1048_Q17167"
        assert result['to_cipher'] == "fent_pol_Q168811_Q17167"
        assert result['facet'] == "POLITICAL"
        assert 'MATCH (from {faceted_cipher: "fent_pol_Q1048_Q17167"})' in result['cypher_query']
        assert 'to {faceted_cipher: "fent_pol_Q168811_Q17167"}' in result['cypher_query']
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_vertex_jump_entity_not_found(self, mock_resolve):
        mock_resolve.side_effect = ["Q1048", None]  # Caesar found, second entity not found
        
        result = construct_vertex_jump(
            "Julius Caesar",
            "NonexistentPerson",
            "political",
            "Q17167"
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_vertex_jump_different_facets(self, mock_resolve):
        # Each construct_vertex_jump calls _resolve twice (from + to entity)
        # So we need 4 values for 2 calls
        mock_resolve.side_effect = ["Q1048", "Q168811", "Q1048", "Q168811"]
        
        # Test different facet keywords
        result_mil = construct_vertex_jump(
            "Julius Caesar", "Pompey", "military", "Q17167"
        )
        result_pol = construct_vertex_jump(
            "Julius Caesar", "Pompey", "political", "Q17167"
        )
        
        assert result_mil['facet'] == "MILITARY"
        assert result_pol['facet'] == "POLITICAL"
        assert result_mil['from_cipher'] != result_pol['from_cipher']


class TestIntegration:
    """Integration tests for LLM usage patterns."""
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_llm_workflow_simple_query(self, mock_resolve):
        """
        Simulate LLM workflow:
        User: "Show me information about Julius Caesar"
        LLM: construct cipher → execute query
        """
        mock_resolve.return_value = "Q1048"
        
        # LLM constructs cipher
        result = construct_cipher_from_text("Julius Caesar")
        
        # LLM gets ready-to-use query
        assert result['success'] is True
        query = result['recommended_query']
        assert 'MATCH' in query
        assert 'ent_per_Q1048' in query
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_llm_workflow_faceted_query(self, mock_resolve):
        """
        Simulate LLM workflow:
        User: "Show me Caesar's political activities in the Roman Republic"
        LLM: extract entities, facet, context → construct cipher → execute query
        """
        mock_resolve.return_value = "Q1048"
        
        # LLM parses query
        entity = "Julius Caesar"
        facet = "political"
        context = "Q17167"  # Roman Republic
        
        # LLM constructs faceted cipher
        result = construct_cipher_from_text(entity, facet, context)
        
        # LLM gets Tier 2 query for precise lookup
        assert result['success'] is True
        assert result['faceted_cipher'] == "fent_pol_Q1048_Q17167"
        assert 'faceted_cipher' in result['recommended_query']
    
    @patch('scripts.tools.entity_cipher._resolve_entity_name_to_qid')
    def test_llm_workflow_relationship_query(self, mock_resolve):
        """
        Simulate LLM workflow:
        User: "What is the relationship between Caesar and Pompey politically?"
        LLM: extract entities → construct vertex jump → execute query
        """
        mock_resolve.side_effect = ["Q1048", "Q168811"]
        
        # LLM constructs vertex jump
        result = construct_vertex_jump(
            "Julius Caesar",
            "Pompey",
            "political",
            "Q17167"
        )
        
        # LLM gets relationship query
        assert result['success'] is True
        query = result['cypher_query']
        assert 'MATCH (from' in query
        assert '-[r]-(to' in query
        assert 'RETURN from, r, to' in query


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
