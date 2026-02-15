#!/usr/bin/env python3
"""
Chrystallum Facet Agent Framework
Purpose: Multi-agent system with facet-specific expertise
Date: February 15, 2026
Status: Production ready

Architecture:
- FacetAgent: Base class extending ChromatogramQueryExecutor
- 17 specialized agents (one per facet)
- Router: Directs queries to appropriate agents
- Coordinator: Aggregates results, deduplicates claims
"""

import os
import json
import sys
from typing import Optional, Dict, Any, List, Tuple
from abc import ABC, abstractmethod
from neo4j import GraphDatabase, Driver
import openai

# Import configuration loader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config_loader import (
    OPENAI_API_KEY,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    NEO4J_DATABASE,
    validate_agent_config
)

# Import claim pipeline
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from claim_ingestion_pipeline import ClaimIngestionPipeline


class FacetAgent(ABC):
    """
    Base class for facet-specific agents
    Each agent understands domain-specific terminology, concepts, and relationships
    """

    def __init__(self, facet_key: str, facet_label: str, system_prompt: str):
        """
        Initialize facet agent
        
        Args:
            facet_key: Lowercase registry key (e.g., 'military')
            facet_label: Display label (e.g., 'Military')
            system_prompt: Facet-specific system prompt
        """
        # Validate configuration
        validate_agent_config(require_openai=True, require_neo4j=True)

        self.facet_key = facet_key
        self.facet_label = facet_label
        self.system_prompt = system_prompt

        self.driver: Driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

        openai.api_key = OPENAI_API_KEY

        # Initialize claim pipeline
        self.pipeline = ClaimIngestionPipeline(self.driver, database=NEO4J_DATABASE)

        # Discover schema on init
        self.schema = self._discover_schema()
        print(f"✓ Initialized {self.facet_label} Agent")
        print(f"  Schema: {len(self.schema['labels'])} labels, {len(self.schema['relationship_types'])} relationships")

    def _discover_schema(self) -> Dict[str, Any]:
        """Discover available labels and relationship types from Neo4j"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            labels_result = session.run("CALL db.labels()")
            labels = [record["label"] for record in labels_result]

            rel_result = session.run("CALL db.relationshipTypes()")
            relationship_types = [record["relationshipType"] for record in rel_result]

        return {
            "labels": labels,
            "relationship_types": relationship_types
        }

    # ================================================================
    # META-SCHEMA INTROSPECTION METHODS
    # Purpose: Query the _Schema meta-graph for architecture understanding
    # ================================================================

    def introspect_node_label(self, label_name: str) -> Optional[Dict[str, Any]]:
        """
        Query meta-graph for node label definition
        
        Args:
            label_name: Name of node label (e.g., 'SubjectConcept')
            
        Returns:
            Dict with label definition, tier, properties, etc.
            None if label not found in meta-graph
        """
        cypher = """
        MATCH (nl:_Schema:NodeLabel {name: $label_name})
        RETURN nl
        """
        
        results = self.query_neo4j(cypher, {"label_name": label_name})
        
        if results:
            return results[0].get('nl')
        return None

    def discover_relationships_between(self, source_label: str, target_label: str) -> List[Dict[str, Any]]:
        """
        Find valid relationship types between two node labels
        
        Args:
            source_label: Source node label (e.g., 'Human')
            target_label: Target node label (e.g., 'SubjectConcept')
            
        Returns:
            List of relationship type definitions
        """
        cypher = """
        MATCH (s:_Schema:NodeLabel {name: $source})-[:SOURCE_LABEL]-(r:_Schema:RelationshipType)-[:TARGET_LABEL]->(t:_Schema:NodeLabel {name: $target})
        RETURN r.name AS relationship_name, 
               r.description AS description,
               r.wikidata_property AS wikidata_property,
               r.semantic AS semantic,
               r.cardinality AS cardinality
        ORDER BY r.name
        """
        
        return self.query_neo4j(cypher, {"source": source_label, "target": target_label})

    def get_required_properties(self, label_name: str) -> List[str]:
        """
        Get required properties for a node label
        
        Args:
            label_name: Node label name
            
        Returns:
            List of required property names
        """
        cypher = """
        MATCH (nl:_Schema:NodeLabel {name: $label_name})-[:HAS_PROPERTY]->(p:_Schema:Property {required: true})
        RETURN p.name AS property_name
        ORDER BY p.name
        """
        
        results = self.query_neo4j(cypher, {"label_name": label_name})
        return [r['property_name'] for r in results]

    def get_authority_tier(self, tier: float) -> Optional[Dict[str, Any]]:
        """
        Get authority tier definition (5.5-layer stack)
        
        Args:
            tier: Tier number (1, 2, 2.5, 3, 4, 5)
            
        Returns:
            Dict with tier definition, gates, confidence floor, etc.
        """
        cypher = """
        MATCH (t:_Schema:AuthorityTier {tier: $tier})
        RETURN t
        """
        
        results = self.query_neo4j(cypher, {"tier": tier})
        
        if results:
            return results[0].get('t')
        return None

    def list_facets(self, filter_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available facets with anchors
        
        Args:
            filter_key: Optional filter by facet key (e.g., 'military')
            
        Returns:
            List of facet definitions with anchors
        """
        if filter_key:
            cypher = """
            MATCH (f:_Schema:FacetReference {key: $filter_key})
            RETURN f.key AS key, f.label AS label, f.definition AS definition, f.anchors AS anchors
            """
            return self.query_neo4j(cypher, {"filter_key": filter_key})
        else:
            cypher = """
            MATCH (f:_Schema:FacetReference)
            RETURN f.key AS key, f.label AS label, f.definition AS definition, f.anchors AS anchors
            ORDER BY f.key
            """
            return self.query_neo4j(cypher)

    def validate_claim_structure(self, claim_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a claim against meta-schema before proposal
        
        Args:
            claim_dict: Claim dictionary with 'cipher', 'confidence', 'facet', etc.
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []
        
        # Check required Claim properties
        required_props = self.get_required_properties('Claim')
        for prop in required_props:
            if prop not in claim_dict:
                errors.append(f"Missing required property: {prop}")
        
        # Validate confidence range
        if 'confidence' in claim_dict:
            conf = claim_dict['confidence']
            if not (0.0 <= conf <= 1.0):
                errors.append(f"Confidence must be 0.0-1.0, got {conf}")
        
        # Validate facet exists
        if 'facet' in claim_dict:
            facet_list = self.list_facets(filter_key=claim_dict['facet'])
            if not facet_list:
                errors.append(f"Invalid facet: {claim_dict['facet']}")
        
        return (len(errors) == 0, errors)

    def get_layer25_properties(self) -> List[str]:
        """
        Get Layer 2.5 Wikidata properties for semantic inference
        
        Returns:
            List of property codes (e.g., ['P31', 'P279', 'P361'])
        """
        tier = self.get_authority_tier(2.5)
        if tier and 'wikidata_properties' in tier:
            return tier['wikidata_properties']
        return []

    # ================================================================
    # CURRENT STATE INTROSPECTION METHODS (STEP 2)
    # Purpose: Query what exists NOW (nodes, edges, claims)
    # Critical: LLMs don't persist between sessions, need to reload state
    # ================================================================

    def get_subjectconcept_subgraph(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get snapshot of current SubjectConcept subgraph
        
        Args:
            limit: Maximum nodes to return (default 100)
            
        Returns:
            {
                'nodes': [list of SubjectConcept nodes],
                'relationships': [list of relationships],
                'count': total_count,
                'sampled': whether result is sampled
            }
        """
        cypher_nodes = """
        MATCH (n:SubjectConcept)
        RETURN n.id_hash AS id_hash,
               n.label AS label,
               n.description AS description,
               n.wikidata_qid AS wikidata_qid,
               n.lcsh_id AS lcsh_id,
               n.fast_id AS fast_id,
               n.status AS status,
               labels(n) AS labels
        LIMIT $limit
        """
        
        cypher_rels = """
        MATCH (source:SubjectConcept)-[r]->(target:SubjectConcept)
        RETURN source.id_hash AS source_id,
               type(r) AS relationship_type,
               target.id_hash AS target_id,
               properties(r) AS properties
        LIMIT $limit
        """
        
        cypher_count = """
        MATCH (n:SubjectConcept)
        RETURN count(n) AS total_count
        """
        
        nodes = self.query_neo4j(cypher_nodes, {"limit": limit})
        relationships = self.query_neo4j(cypher_rels, {"limit": limit})
        count_result = self.query_neo4j(cypher_count)
        
        total_count = count_result[0]['total_count'] if count_result else 0
        
        return {
            'nodes': nodes,
            'relationships': relationships,
            'count': total_count,
            'sampled': total_count > limit
        }

    def find_claims_for_node(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Find all claims that reference a specific node
        
        Args:
            node_id: Node identifier (id_hash or entity_id)
            
        Returns:
            List of claim records with status, confidence, agent, etc.
        """
        cypher = """
        MATCH (n {id_hash: $node_id})
        OPTIONAL MATCH (n)-[:SUPPORTED_BY]->(c:Claim)
        OPTIONAL MATCH (c2:Claim)-[:ASSERTS]->(n)
        WITH n, COALESCE(c, c2) AS claim
        WHERE claim IS NOT NULL
        RETURN DISTINCT
               claim.claim_id AS claim_id,
               claim.label AS label,
               claim.status AS status,
               claim.confidence AS confidence,
               claim.posterior_probability AS posterior,
               claim.source_agent AS source_agent,
               claim.facet AS facet,
               claim.timestamp AS timestamp,
               claim.promoted AS promoted
        ORDER BY claim.timestamp DESC
        """
        
        return self.query_neo4j(cypher, {"node_id": node_id})

    def find_claims_for_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        rel_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find claims about a specific relationship
        
        Args:
            source_id: Source node id_hash
            target_id: Target node id_hash
            rel_type: Optional relationship type filter
            
        Returns:
            List of claims proposing relationships between these nodes
        """
        if rel_type:
            cypher = """
            MATCH (source {id_hash: $source_id})
            MATCH (target {id_hash: $target_id})
            MATCH (source)-[r]->(target)
            WHERE type(r) = $rel_type AND r.promoted_from_claim_id IS NOT NULL
            MATCH (c:Claim {claim_id: r.promoted_from_claim_id})
            RETURN c.claim_id AS claim_id,
                   c.label AS label,
                   c.status AS status,
                   c.confidence AS confidence,
                   c.posterior_probability AS posterior,
                   c.source_agent AS source_agent,
                   c.facet AS facet,
                   c.timestamp AS timestamp,
                   type(r) AS relationship_type,
                   r.promoted_from_claim_id AS promoted_from_claim_id
            """
            params = {"source_id": source_id, "target_id": target_id, "rel_type": rel_type}
        else:
            cypher = """
            MATCH (source {id_hash: $source_id})
            MATCH (target {id_hash: $target_id})
            MATCH (source)-[r]->(target)
            WHERE r.promoted_from_claim_id IS NOT NULL
            MATCH (c:Claim {claim_id: r.promoted_from_claim_id})
            RETURN c.claim_id AS claim_id,
                   c.label AS label,
                   c.status AS status,
                   c.confidence AS confidence,
                   c.posterior_probability AS posterior,
                   c.source_agent AS source_agent,
                   c.facet AS facet,
                   c.timestamp AS timestamp,
                   type(r) AS relationship_type,
                   r.promoted_from_claim_id AS promoted_from_claim_id
            """
            params = {"source_id": source_id, "target_id": target_id}
        
        return self.query_neo4j(cypher, params)

    def get_node_provenance(self, node_id: str) -> Dict[str, Any]:
        """
        Get provenance: which claim(s) created/modified this node
        
        Args:
            node_id: Node id_hash or entity_id
            
        Returns:
            {
                'node_id': node_id,
                'created_by_claim': claim_id or None,
                'modified_by_claims': [list of claim_ids],
                'total_claims': count
            }
        """
        cypher = """
        MATCH (n {id_hash: $node_id})
        OPTIONAL MATCH (n)-[:SUPPORTED_BY]->(c:Claim)
        WITH n, COLLECT(c) AS claims
        RETURN n.id_hash AS node_id,
               [claim IN claims WHERE claim.status = 'validated' | claim.claim_id] AS validated_claims,
               [claim IN claims WHERE claim.status = 'proposed' | claim.claim_id] AS proposed_claims,
               size(claims) AS total_claims
        """
        
        result = self.query_neo4j(cypher, {"node_id": node_id})
        
        if not result:
            return {
                'node_id': node_id,
                'created_by_claim': None,
                'modified_by_claims': [],
                'total_claims': 0,
                'validated_claims': [],
                'proposed_claims': []
            }
        
        data = result[0]
        validated = data.get('validated_claims', [])
        proposed = data.get('proposed_claims', [])
        
        return {
            'node_id': node_id,
            'created_by_claim': validated[0] if validated else None,
            'modified_by_claims': validated[1:] if len(validated) > 1 else [],
            'total_claims': data.get('total_claims', 0),
            'validated_claims': validated,
            'proposed_claims': proposed
        }

    def list_pending_claims(
        self, 
        facet: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List claims awaiting validation
        
        Args:
            facet: Optional facet filter (e.g., 'military')
            min_confidence: Minimum confidence threshold
            limit: Maximum results
            
        Returns:
            List of pending claim records
        """
        if facet:
            cypher = """
            MATCH (c:Claim)
            WHERE c.status = 'proposed'
              AND c.facet = $facet
              AND c.confidence >= $min_confidence
            RETURN c.claim_id AS claim_id,
                   c.label AS label,
                   c.confidence AS confidence,
                   c.posterior_probability AS posterior,
                   c.source_agent AS source_agent,
                   c.facet AS facet,
                   c.timestamp AS timestamp,
                   c.text AS text
            ORDER BY c.posterior_probability DESC, c.confidence DESC
            LIMIT $limit
            """
            params = {"facet": facet, "min_confidence": min_confidence, "limit": limit}
        else:
            cypher = """
            MATCH (c:Claim)
            WHERE c.status = 'proposed'
              AND c.confidence >= $min_confidence
            RETURN c.claim_id AS claim_id,
                   c.label AS label,
                   c.confidence AS confidence,
                   c.posterior_probability AS posterior,
                   c.source_agent AS source_agent,
                   c.facet AS facet,
                   c.timestamp AS timestamp,
                   c.text AS text
            ORDER BY c.posterior_probability DESC, c.confidence DESC
            LIMIT $limit
            """
            params = {"min_confidence": min_confidence, "limit": limit}
        
        return self.query_neo4j(cypher, params)

    def get_claim_history(self, node_id: str) -> Dict[str, Any]:
        """
        Get full claim audit trail for a node
        
        Args:
            node_id: Node id_hash
            
        Returns:
            {
                'node_id': node_id,
                'node_label': label,
                'claim_timeline': [ordered list of claims],
                'agents_involved': [unique agent IDs],
                'facets_involved': [unique facets]
            }
        """
        cypher = """
        MATCH (n {id_hash: $node_id})
        OPTIONAL MATCH (n)-[:SUPPORTED_BY]->(c:Claim)
        WITH n, c
        ORDER BY c.timestamp ASC
        RETURN n.id_hash AS node_id,
               n.label AS node_label,
               COLLECT({
                   claim_id: c.claim_id,
                   label: c.label,
                   status: c.status,
                   confidence: c.confidence,
                   posterior: c.posterior_probability,
                   agent: c.source_agent,
                   facet: c.facet,
                   timestamp: c.timestamp,
                   promoted: c.promoted
               }) AS claim_timeline,
               COLLECT(DISTINCT c.source_agent) AS agents_involved,
               COLLECT(DISTINCT c.facet) AS facets_involved
        """
        
        result = self.query_neo4j(cypher, {"node_id": node_id})
        
        if not result or not result[0]['node_label']:
            return {
                'node_id': node_id,
                'node_label': None,
                'claim_timeline': [],
                'agents_involved': [],
                'facets_involved': []
            }
        
        return result[0]

    def find_agent_contributions(
        self, 
        agent_id: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Find what this agent (or all agents) has proposed
        
        Args:
            agent_id: Agent identifier (defaults to self.facet_key)
            limit: Maximum claims to return
            
        Returns:
            {
                'agent_id': agent_id,
                'total_claims': count,
                'promoted_claims': count,
                'pending_claims': count,
                'rejected_claims': count,
                'claims': [list of claim records]
            }
        """
        agent_id = agent_id or self.facet_key
        
        cypher = """
        MATCH (c:Claim)
        WHERE c.source_agent = $agent_id
        WITH c
        ORDER BY c.timestamp DESC
        LIMIT $limit
        RETURN c.claim_id AS claim_id,
               c.label AS label,
               c.status AS status,
               c.confidence AS confidence,
               c.posterior_probability AS posterior,
               c.facet AS facet,
               c.timestamp AS timestamp,
               c.promoted AS promoted
        """
        
        claims = self.query_neo4j(cypher, {"agent_id": agent_id, "limit": limit})
        
        cypher_stats = """
        MATCH (c:Claim)
        WHERE c.source_agent = $agent_id
        RETURN COUNT(c) AS total_claims,
               SUM(CASE WHEN c.promoted = true THEN 1 ELSE 0 END) AS promoted_claims,
               SUM(CASE WHEN c.status = 'proposed' THEN 1 ELSE 0 END) AS pending_claims,
               SUM(CASE WHEN c.status = 'rejected' THEN 1 ELSE 0 END) AS rejected_claims
        """
        
        stats = self.query_neo4j(cypher_stats, {"agent_id": agent_id})
        stats_data = stats[0] if stats else {}
        
        return {
            'agent_id': agent_id,
            'total_claims': stats_data.get('total_claims', 0),
            'promoted_claims': stats_data.get('promoted_claims', 0),
            'pending_claims': stats_data.get('pending_claims', 0),
            'rejected_claims': stats_data.get('rejected_claims', 0),
            'claims': claims
        }

    def get_session_context(self) -> Dict[str, Any]:
        """
        Initialize agent with current state snapshot
        Critical for non-persistent LLM sessions
        
        Returns:
            {
                'timestamp': ISO timestamp,
                'agent_id': self.facet_key,
                'subgraph_sample': SubjectConcept subgraph snapshot,
                'pending_claims': My pending claims,
                'recent_promotions': Recently promoted claims,
                'my_contributions': My claim statistics,
                'schema_version': Meta-schema stats
            }
        """
        from datetime import datetime
        
        # Get SubjectConcept snapshot
        subgraph = self.get_subjectconcept_subgraph(limit=50)
        
        # Get my pending claims
        pending = self.list_pending_claims(facet=self.facet_key, limit=20)
        
        # Get recently promoted claims (all facets)
        cypher_recent = """
        MATCH (c:Claim)
        WHERE c.promoted = true AND c.status = 'validated'
        WITH c
        ORDER BY c.promotion_date DESC
        LIMIT 10
        RETURN c.claim_id AS claim_id,
               c.label AS label,
               c.source_agent AS source_agent,
               c.facet AS facet,
               c.promotion_date AS promotion_date
        """
        recent_promotions = self.query_neo4j(cypher_recent)
        
        # Get my contributions
        my_contributions = self.find_agent_contributions(agent_id=self.facet_key, limit=10)
        
        # Schema version check
        cypher_schema = """
        MATCH (n:_Schema:NodeLabel)
        RETURN count(n) AS node_labels
        """
        schema_check = self.query_neo4j(cypher_schema)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.facet_key,
            'agent_label': self.facet_label,
            'subgraph_sample': subgraph,
            'pending_claims': pending,
            'recent_promotions': recent_promotions,
            'my_contributions': my_contributions,
            'schema_version': {
                'node_labels': schema_check[0]['node_labels'] if schema_check else 0
            }
        }

    # ================================================================
    # FEDERATION-DRIVEN DISCOVERY METHODS (STEP 3)
    # Purpose: Fetch Wikidata entities, traverse hierarchies, auto-generate claims
    # Critical: Layer 2 integration for authority alignment
    # ================================================================

    def fetch_wikidata_entity(self, qid: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full Wikidata entity with all properties and claims
        
        Args:
            qid: Wikidata QID (e.g., 'Q1048')
            
        Returns:
            {
                'qid': 'Q1048',
                'label': 'Julius Caesar',
                'description': 'Roman general and dictator',
                'statement_count': 150,
                'property_count': 45,
                'claims': {property: [list of claims]}
            }
            None if QID not found
        """
        import requests
        
        API_URL = "https://www.wikidata.org/w/api.php"
        
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": qid,
            "languages": "en",
            "props": "labels|descriptions|claims|aliases",
        }
        
        headers = {"User-Agent": "Chrystallum/1.0 (facet agent discovery)"}
        
        try:
            response = requests.get(API_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            payload = response.json()
            
            entities = payload.get("entities", {})
            entity = entities.get(qid)
            
            if not entity or "missing" in entity:
                return None
            
            # Parse claims
            claims = entity.get("claims", {})
            parsed_claims = {}
            total_statements = 0
            
            for prop, claim_list in claims.items():
                parsed_claims[prop] = claim_list
                total_statements += len(claim_list)
            
            return {
                "qid": qid,
                "label": entity.get("labels", {}).get("en", {}).get("value"),
                "description": entity.get("descriptions", {}).get("en", {}).get("value"),
                "aliases": [a.get("value") for a in entity.get("aliases", {}).get("en", [])],
                "statement_count": total_statements,
                "property_count": len(parsed_claims),
                "claims": parsed_claims
            }
            
        except Exception as e:
            print(f"Error fetching Wikidata entity {qid}: {e}")
            return None

    def enrich_node_from_wikidata(
        self, 
        node_id: str, 
        qid: str,
        create_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich existing node (or create new) with Wikidata properties
        
        Args:
            node_id: Node id_hash or entity_id
            qid: Wikidata QID
            create_if_missing: If True, create node if it doesn't exist
            
        Returns:
            {
                'status': 'enriched' | 'created' | 'not_found',
                'node_id': node_id,
                'qid': qid,
                'properties_added': count,
                'claims_generated': count
            }
        """
        # Fetch Wikidata entity
        entity = self.fetch_wikidata_entity(qid)
        if not entity:
            return {
                'status': 'error',
                'error': f'Wikidata entity {qid} not found'
            }
        
        # Check if node exists
        cypher_check = "MATCH (n {id_hash: $node_id}) RETURN n"
        existing = self.query_neo4j(cypher_check, {"node_id": node_id})
        
        if not existing and not create_if_missing:
            return {
                'status': 'not_found',
                'node_id': node_id,
                'message': 'Node not found and create_if_missing=False'
            }
        
        # Enrich or create node
        cypher_enrich = """
        MERGE (n:SubjectConcept {id_hash: $node_id})
        SET n.wikidata_qid = $qid,
            n.label = COALESCE(n.label, $label),
            n.description = COALESCE(n.description, $description),
            n.aliases = $aliases,
            n.wikidata_statement_count = $statement_count,
            n.wikidata_property_count = $property_count,
            n.wikidata_fetched_at = $timestamp,
            n.status = COALESCE(n.status, 'wikidata_enriched')
        RETURN n
        """
        
        from datetime import datetime
        
        self.query_neo4j(cypher_enrich, {
            "node_id": node_id,
            "qid": qid,
            "label": entity['label'],
            "description": entity['description'],
            "aliases": entity.get('aliases', []),
            "statement_count": entity['statement_count'],
            "property_count": entity['property_count'],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        status = 'created' if not existing else 'enriched'
        
        return {
            'status': status,
            'node_id': node_id,
            'qid': qid,
            'label': entity['label'],
            'properties_added': entity['property_count'],
            'entity_data': entity
        }

    def discover_hierarchy_from_entity(
        self, 
        qid: str,
        depth: int = 1,
        limit_per_property: int = 20
    ) -> Dict[str, Any]:
        """
        Discover related entities via Layer 2.5 hierarchy properties
        
        Uses P31 (instance of), P279 (subclass of), P361 (part of),
        P101 (field of work), P921 (main subject), etc.
        
        Args:
            qid: Starting Wikidata QID
            depth: How many levels deep to traverse (default 1)
            limit_per_property: Max entities per property (default 20)
            
        Returns:
            {
                'root_qid': qid,
                'discovered_entities': {qid: entity_data},
                'discovered_relationships': [list of triples],
                'hierarchy_levels': depth_reached,
                'total_discovered': count
            }
        """
        # Get Layer 2.5 properties
        layer25_props = self.get_layer25_properties()
        
        if not layer25_props:
            # Fallback to hardcoded Layer 2.5 properties
            layer25_props = ['P31', 'P279', 'P361', 'P101', 'P2578', 'P921', 'P1269']
        
        discovered_entities = {}
        discovered_relationships = []
        visited = set()
        queue = [(qid, 0)]  # (qid, current_depth)
        
        while queue:
            current_qid, current_depth = queue.pop(0)
            
            if current_qid in visited or current_depth >= depth:
                continue
            
            visited.add(current_qid)
            
            # Fetch entity
            entity = self.fetch_wikidata_entity(current_qid)
            if not entity:
                continue
            
            discovered_entities[current_qid] = entity
            
            # Extract hierarchy relationships
            claims = entity.get('claims', {})
            
            for prop in layer25_props:
                if prop not in claims:
                    continue
                
                prop_claims = claims[prop][:limit_per_property]
                
                for claim in prop_claims:
                    mainsnak = claim.get('mainsnak', {})
                    datavalue = mainsnak.get('datavalue', {})
                    value = datavalue.get('value', {})
                    
                    # Extract target QID
                    target_qid = None
                    if isinstance(value, dict):
                        entity_type = value.get('entity-type')
                        numeric_id = value.get('numeric-id')
                        if entity_type == 'item' and numeric_id:
                            target_qid = f"Q{numeric_id}"
                    elif isinstance(value, str) and value.startswith('Q'):
                        target_qid = value
                    
                    if target_qid:
                        discovered_relationships.append({
                            'source_qid': current_qid,
                            'property': prop,
                            'target_qid': target_qid,
                            'depth': current_depth
                        })
                        
                        # Add to queue for next level
                        if current_depth + 1 < depth:
                            queue.append((target_qid, current_depth + 1))
        
        return {
            'root_qid': qid,
            'discovered_entities': discovered_entities,
            'discovered_relationships': discovered_relationships,
            'hierarchy_levels': depth,
            'total_discovered': len(discovered_entities)
        }

    def generate_claims_from_wikidata(
        self,
        qid: str,
        create_nodes: bool = True,
        auto_submit: bool = False
    ) -> Dict[str, Any]:
        """
        Generate claims automatically from Wikidata entity
        
        Process:
        1. Fetch Wikidata entity
        2. Create/enrich SubjectConcept node
        3. Discover hierarchy (depth 1)
        4. Generate claims for discovered relationships
        5. Optionally auto-submit claims
        
        Args:
            qid: Wikidata QID to start from
            create_nodes: Create SubjectConcept nodes for discovered entities
            auto_submit: If True, submit claims immediately (vs return for review)
            
        Returns:
            {
                'root_qid': qid,
                'root_node_id': node_id,
                'discovered_count': count,
                'claims_generated': [list of claim dicts],
                'claims_submitted': count (if auto_submit=True)
            }
        """
        import hashlib
        
        # Fetch root entity
        entity = self.fetch_wikidata_entity(qid)
        if not entity:
            return {
                'status': 'error',
                'error': f'QID {qid} not found'
            }
        
        # Create/enrich root node
        root_node_id = hashlib.sha256(f"wikidata:{qid}".encode()).hexdigest()[:16]
        
        enrich_result = self.enrich_node_from_wikidata(
            node_id=root_node_id,
            qid=qid,
            create_if_missing=True
        )
        
        # Discover hierarchy
        hierarchy = self.discover_hierarchy_from_entity(qid, depth=1, limit_per_property=10)
        
        claims_generated = []
        
        # Generate claims for discovered relationships
        for rel in hierarchy['discovered_relationships']:
            source_qid = rel['source_qid']
            prop = rel['property']
            target_qid = rel['target_qid']
            
            # Get or create target node
            target_node_id = hashlib.sha256(f"wikidata:{target_qid}".encode()).hexdigest()[:16]
            
            if create_nodes:
                target_entity = hierarchy['discovered_entities'].get(target_qid)
                if target_entity:
                    self.enrich_node_from_wikidata(
                        node_id=target_node_id,
                        qid=target_qid,
                        create_if_missing=True
                    )
            
            # Map Wikidata property to relationship type
            rel_type = self._map_wikidata_property_to_relationship(prop)
            
            # Generate claim
            claim_label = f"{entity['label']} {rel_type.replace('_', ' ').lower()} {target_qid}"
            
            claim = {
                'entity_id': root_node_id,
                'relationship_type': rel_type,
                'target_id': target_node_id,
                'label': claim_label,
                'confidence': 0.90,  # High confidence from Wikidata
                'source_agent': self.facet_key,
                'facet': self.facet_key,
                'claim_type': 'federation_discovery',
                'authority_source': 'Wikidata',
                'authority_ids': {
                    'source_qid': source_qid,
                    'property': prop,
                    'target_qid': target_qid
                },
                'retrieval_source': f'Wikidata:{qid}',
                'reasoning_notes': f'Discovered via Layer 2.5 property {prop} from Wikidata'
            }
            
            claims_generated.append(claim)
        
        # Optionally auto-submit claims
        submitted_count = 0
        if auto_submit:
            for claim in claims_generated:
                try:
                    result = self.pipeline.ingest_claim(**claim)
                    if result['status'] in ['created', 'promoted']:
                        submitted_count += 1
                except Exception as e:
                    print(f"Error submitting claim: {e}")
        
        return {
            'status': 'success',
            'root_qid': qid,
            'root_node_id': root_node_id,
            'root_label': entity['label'],
            'discovered_count': hierarchy['total_discovered'],
            'claims_generated': claims_generated,
            'claims_submitted': submitted_count if auto_submit else None
        }

    def _map_wikidata_property_to_relationship(self, wikidata_property: str) -> str:
        """
        Map Wikidata property (P-code) to relationship type
        
        Args:
            wikidata_property: P31, P279, P361, etc.
            
        Returns:
            Relationship type (e.g., 'INSTANCE_OF', 'SUBCLASS_OF')
        """
        # Layer 2.5 core properties
        mapping = {
            'P31': 'INSTANCE_OF',
            'P279': 'SUBCLASS_OF',
            'P361': 'PART_OF',
            'P101': 'FIELD_OF_WORK',
            'P2578': 'STUDIES',
            'P921': 'MAIN_SUBJECT',
            'P1269': 'FACET_OF',
            
            # Common relationships
            'P50': 'AUTHOR',
            'P800': 'CREATED_WORK',
            'P607': 'PARTICIPATED_IN_CONFLICT',
            'P241': 'MILITARY_BRANCH',
            'P39': 'POSITION_HELD',
            'P106': 'OCCUPATION',
            'P27': 'COUNTRY_OF_CITIZENSHIP',
            'P19': 'PLACE_OF_BIRTH',
            'P20': 'PLACE_OF_DEATH',
            'P570': 'DATE_OF_DEATH',
            'P569': 'DATE_OF_BIRTH',
        }
        
        return mapping.get(wikidata_property, f'WIKIDATA_{wikidata_property}')

    def bootstrap_from_qid(
        self,
        qid: str,
        depth: int = 1,
        auto_submit_claims: bool = False
    ) -> Dict[str, Any]:
        """
        Bootstrap agent knowledge from a Wikidata QID
        
        Use this when agent is first instantiated on a new topic.
        
        Process:
        1. Fetch Wikidata entity
        2. Create SubjectConcept node
        3. Discover hierarchy (configurable depth)
        4. Generate claims for all discovered relationships
        5. Optionally auto-submit high-confidence claims
        
        Args:
            qid: Wikidata QID (e.g., 'Q17167' for Roman Republic)
            depth: Hierarchy traversal depth (1-3 recommended)
            auto_submit_claims: If True, submit claims >= 0.90 confidence
            
        Returns:
            {
                'status': 'success',
                'root_qid': qid,
                'nodes_created': count,
                'relationships_discovered': count,
                'claims_generated': count,
                'claims_submitted': count
            }
        """
        print(f"\n🚀 Bootstrapping from Wikidata: {qid}")
        
        # Fetch root entity
        entity = self.fetch_wikidata_entity(qid)
        if not entity:
            return {
                'status': 'error',
                'error': f'QID {qid} not found'
            }
        
        print(f"✓ Fetched: {entity['label']} ({entity['statement_count']} statements)")
        
        # Discover hierarchy
        print(f"🔍 Discovering hierarchy (depth {depth})...")
        hierarchy = self.discover_hierarchy_from_entity(qid, depth=depth)
        
        print(f"✓ Discovered {hierarchy['total_discovered']} entities, {len(hierarchy['discovered_relationships'])} relationships")
        
        # Generate claims
        result = self.generate_claims_from_wikidata(
            qid=qid,
            create_nodes=True,
            auto_submit=auto_submit_claims
        )
        
        print(f"✓ Generated {len(result['claims_generated'])} claims")
        if auto_submit_claims:
            print(f"✓ Submitted {result['claims_submitted']} claims")
        
        return {
            'status': 'success',
            'root_qid': qid,
            'root_label': entity['label'],
            'nodes_created': hierarchy['total_discovered'],
            'relationships_discovered': len(hierarchy['discovered_relationships']),
            'claims_generated': len(result['claims_generated']),
            'claims_submitted': result['claims_submitted'],
            'hierarchy_data': hierarchy,
            'claims': result['claims_generated']
        }

    # ================================================================

    def query_neo4j(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query against Neo4j"""
        params = params or {}

        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher, params)
            records = result.data()

        return records

    def generate_cypher(self, natural_language_query: str) -> str:
        """
        Use ChatGPT to generate Cypher from natural language
        Uses facet-specific system prompt for domain expertise
        """

        system_prompt_with_schema = f"""{self.system_prompt}

AVAILABLE LABELS (Node Types):
{json.dumps(self.schema['labels'], indent=2)}

AVAILABLE RELATIONSHIPS:
{json.dumps(self.schema['relationship_types'], indent=2)}

CRITICAL RULES:
1. Use ONLY the labels listed above
2. Use canonical labels: SubjectConcept (not Concept), Human (not Person), Event (not Activity), Place (not Location)
3. Always add LIMIT 10 unless asking for more
4. For dates, use ISO 8601 format (e.g., "-0049-01-10" for 49 BCE)
5. Return ONLY valid Cypher - no explanations, no markdown, no code blocks
6. Prioritize {self.facet_label} domain concepts when disambiguating

EXAMPLE VALID QUERIES:
MATCH (n:SubjectConcept) RETURN n LIMIT 10
MATCH (h:Human)-[r:PARTICIPATED_IN]->(e:Event) RETURN h, r, e LIMIT 10
MATCH (subject:SubjectConcept) WHERE subject.label CONTAINS 'Roman' MATCH (entity)-[:CLASSIFIED_BY]->(subject) RETURN entity LIMIT 20

Generate a single Cypher query for this request. Return ONLY the Cypher code, nothing else."""

        user_message = f"Generate a Cypher query for: {natural_language_query}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt_with_schema},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=500
        )

        cypher = response.choices[0].message.content.strip()

        # Clean up if ChatGPT wrapped in markdown code blocks
        if cypher.startswith("```"):
            cypher = cypher.split("```")[1]
            if cypher.startswith("cypher"):
                cypher = cypher[6:]
        cypher = cypher.strip()

        return cypher

    def format_results(self, records: List[Dict[str, Any]]) -> str:
        """Format query results for readable output"""
        if not records:
            return "No results found."

        if len(records) == 1 and len(records[0]) == 1:
            value = list(records[0].values())[0]
            return json.dumps(value, indent=2, default=str)

        output = f"Found {len(records)} result(s):\n\n"
        for i, record in enumerate(records, 1):
            output += f"{i}. "
            items = []
            for key, value in record.items():
                if isinstance(value, dict):
                    items.append(f"{key}: {json.dumps(value, indent=2, default=str)}")
                else:
                    items.append(f"{key}: {value}")
            output += " | ".join(items) + "\n"

        return output

    def query(self, user_query: str) -> str:
        """
        Main agent interface: Natural language query → Results
        
        Args:
            user_query: Natural language question about the graph
            
        Returns:
            Formatted results or error message
        """
        try:
            print(f"\n▶ [{self.facet_label}] User: {user_query}")

            print("  Generating Cypher...")
            cypher = self.generate_cypher(user_query)
            print(f"  Generated: {cypher[:80]}..." if len(cypher) > 80 else f"  Generated: {cypher}")

            print("  Executing query...")
            results = self.query_neo4j(cypher)

            formatted = self.format_results(results)
            print(f"\n✓ {formatted}")

            return formatted

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n✗ {error_msg}")
            return error_msg

    def propose_claim(
        self,
        entity_id: str,
        relationship_type: str,
        target_id: str,
        confidence: float,
        label: str,
        subject_qid: Optional[str] = None,
        retrieval_source: str = "agent_facet",
        reasoning_notes: str = "",
        authority_source: Optional[str] = None,
        authority_ids: Optional[Any] = None,
        claim_type: str = "relational",
        claim_signature: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Propose a claim via the ingestion pipeline
        Automatically assigns facet based on agent expertise
        
        Args:
            entity_id: Source entity ID
            relationship_type: Relationship type name
            target_id: Target entity ID
            confidence: Confidence score 0.0-1.0
            label: Human-readable claim label
            subject_qid: Wikidata subject QID
            retrieval_source: Data source
            reasoning_notes: Agent reasoning
            authority_source: Authority system
            authority_ids: Authority IDs
            claim_type: Claim type
            claim_signature: Deterministic signature
            
        Returns:
            Ingestion result dict
        """
        print(f"\n▶ [{self.facet_label}] Propose Claim: {label}")
        print(f"  Entity: {entity_id} -{relationship_type}-> {target_id}")
        print(f"  Confidence: {confidence:.2f}")

        result = self.pipeline.ingest_claim(
            entity_id=entity_id,
            relationship_type=relationship_type,
            target_id=target_id,
            confidence=confidence,
            label=label,
            subject_qid=subject_qid,
            retrieval_source=retrieval_source,
            reasoning_notes=reasoning_notes,
            facet=self.facet_key,  # Automatic facet assignment
            claim_signature=claim_signature,
            claim_type=claim_type,
            source_agent=f"agent_facet_{self.facet_key}",
            authority_source=authority_source,
            authority_ids=authority_ids
        )

        if result["status"] == "error":
            print(f"\n✗ Submission failed: {result['error']}")
        else:
            promoted = " (PROMOTED)" if result["promoted"] else ""
            print(f"\n✓ Claim created{promoted}: {result['claim_id']}")
            print(f"  Cipher: {result['cipher'][:16]}...")
            print(f"  Posterior: {result.get('posterior_probability')}")

        return result

    # ================================================================
    # SCHEMA INTROSPECTION METHODS (Meta-Graph Queries)
    # ================================================================
    # Enable agents to understand Chrystallum architecture
    # Sources: Neo4j/schema/06_meta_schema_graph.cypher

    def introspect_node_label(self, label: str) -> Dict[str, Any]:
        """
        Query meta-graph for node label definition
        
        Args:
            label: Node label name (e.g., 'SubjectConcept', 'Claim')
            
        Returns:
            Label definition with properties, tier, authority sources
            
        Example:
            >>> agent.introspect_node_label('SubjectConcept')
            {
              'name': 'SubjectConcept',
              'tier': 4,
              'definition': 'Authority-aligned subject/concept from LCSH/Wikidata/FAST',
              'required_properties': ['id_hash', 'label', 'description'],
              'optional_properties': ['wikidata_qid', 'lcsh_id'],
              'authority_sources': ['LCSH', 'Wikidata', 'FAST']
            }
        """
        query = """
        MATCH (nl:_Schema:NodeLabel {name: $label})
        OPTIONAL MATCH (nl)-[:HAS_REQUIRED_PROPERTY]->(req:_Schema:Property)
        OPTIONAL MATCH (nl)-[:HAS_OPTIONAL_PROPERTY]->(opt:_Schema:Property)
        RETURN nl {
            .*,
            required_properties: collect(DISTINCT req.name),
            optional_properties: collect(DISTINCT opt.name)
        } as label_info
        """
        results = self.query_neo4j(query, {"label": label})
        return results[0]["label_info"] if results else {}

    def discover_valid_relationships(
        self, 
        source_label: str, 
        target_label: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find valid relationship types between node labels
        
        Args:
            source_label: Source node label
            target_label: Optional target label filter
            
        Returns:
            List of valid relationship types with semantic info
            
        Example:
            >>> agent.discover_valid_relationships('SubjectConcept', 'SubjectConcept')
            [
              {'name': 'ALIGNED_WITH_LCSH', 'semantic': 'authority_alignment', 'tier': 1},
              {'name': 'INSTANCE_OF', 'semantic': 'classification', 'tier': 2.5}
            ]
        """
        if target_label:
            query = """
            MATCH (s:_Schema:NodeLabel {name: $source})
            <-[:SOURCE_LABEL]-(r:_Schema:RelationshipType)
            -[:TARGET_LABEL]->(t:_Schema:NodeLabel {name: $target})
            RETURN r {.*, source: s.name, target: t.name} as rel_info
            ORDER BY r.tier, r.name
            """
            params = {"source": source_label, "target": target_label}
        else:
            query = """
            MATCH (s:_Schema:NodeLabel {name: $source})
            <-[:SOURCE_LABEL]-(r:_Schema:RelationshipType)
            -[:TARGET_LABEL]->(t:_Schema:NodeLabel)
            RETURN r {.*, source: s.name, target: t.name} as rel_info
            ORDER BY r.tier, r.name
            """
            params = {"source": source_label}
        
        results = self.query_neo4j(query, params)
        return [r["rel_info"] for r in results]

    def introspect_authority_layers(self) -> List[Dict[str, Any]]:
        """
        Query 5.5-layer authority stack definition
        
        Returns:
            List of authority tiers with gates and confidence floors
            
        Example:
            >>> agent.introspect_authority_layers()
            [
              {'tier': 1, 'layer_name': 'Library Science Authority', 'gates': ['LCSH', 'LCC', 'FAST']},
              {'tier': 2, 'layer_name': 'Federation Authority', 'gates': ['Wikidata', 'Wikipedia']},
              ...
            ]
        """
        query = """
        MATCH (t:_Schema:AuthorityTier)
        RETURN t {.*} as tier_info
        ORDER BY t.tier
        """
        results = self.query_neo4j(query)
        return [r["tier_info"] for r in results]

    def discover_related_facets(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Find facets relevant to given keywords (for multi-facet routing)
        
        Args:
            keywords: List of search terms (e.g., ['warfare', 'battle', 'military'])
            
        Returns:
            List of matching facets with confidence scores
            
        Example:
            >>> agent.discover_related_facets(['warfare', 'battle'])
            [
              {'key': 'military', 'label': 'Military', 'match_score': 0.95},
              {'key': 'political', 'label': 'Political', 'match_score': 0.65}
            ]
        """
        query = """
        MATCH (f:_Schema:FacetReference)
        WHERE ANY(kw IN $keywords WHERE 
            toLower(f.definition) CONTAINS toLower(kw) OR
            toLower(f.label) CONTAINS toLower(kw)
        )
        RETURN f {.*} as facet_info
        ORDER BY f.key
        """
        results = self.query_neo4j(query, {"keywords": keywords})
        return [r["facet_info"] for r in results]

    def introspect_wikidata_properties(self, transitive_only: bool = False) -> List[Dict[str, Any]]:
        """
        Query Layer 2.5 Wikidata property definitions
        
        Args:
            transitive_only: Filter to only transitive properties (P279, P361)
            
        Returns:
            List of Wikidata properties with semantic info and usage patterns
            
        Example:
            >>> agent.introspect_wikidata_properties(transitive_only=True)
            [
              {'property': 'P279', 'label': 'subclass of', 'transitive': True, 'usage': '...'},
              {'property': 'P361', 'label': 'part of', 'transitive': True, 'usage': '...'}
            ]
        """
        if transitive_only:
            query = """
            MATCH (wp:_Schema:WikidataProperty)
            WHERE wp.transitive = true
            RETURN wp {.*} as prop_info
            ORDER BY wp.property
            """
        else:
            query = """
            MATCH (wp:_Schema:WikidataProperty)
            RETURN wp {.*} as prop_info
            ORDER BY wp.property
            """
        results = self.query_neo4j(query)
        return [r["prop_info"] for r in results]

    def validate_claim_schema(self, cipher: str) -> Dict[str, Any]:
        """
        Validate claim cipher format against schema rules
        
        Args:
            cipher: Proposed cipher string (e.g., 'Cannae-OCCURRED_IN-Year_-216')
            
        Returns:
            Validation result with errors and suggestions
            
        Example:
            >>> agent.validate_claim_schema('Cannae-OCCURRED_IN-Year_-216')
            {
              'valid': True,
              'relationship_valid': True,
              'source_label': 'Event',
              'target_label': 'Year',
              'tier': 4
            }
        """
        # Parse cipher (basic format: entity-relationship-target)
        parts = cipher.split('-', 2)
        if len(parts) != 3:
            return {"valid": False, "error": "Invalid cipher format (expected: entity-REL-target)"}
        
        entity_id, rel_type, target_id = parts
        
        # Query if this relationship type exists in meta-schema
        query = """
        MATCH (r:_Schema:RelationshipType {name: $rel_type})
        RETURN r {
            .*,
            valid: true
        } as validation
        """
        results = self.query_neo4j(query, {"rel_type": rel_type})
        
        if not results:
            return {
                "valid": False,
                "error": f"Relationship type '{rel_type}' not found in schema",
                "suggestion": "Use discover_valid_relationships() to find valid types"
            }
        
        return results[0]["validation"]

    def get_schema_statistics(self) -> Dict[str, Any]:
        """
        Get meta-graph statistics for agent planning
        
        Returns:
            Graph statistics (label counts, relationship counts, cardinalities)
            
        Example:
            >>> agent.get_schema_statistics()
            {
              'total_labels': 14,
              'total_relationship_types': 12,
              'total_facets': 17,
              'year_nodes': 4025,
              'year_range': [-2000, 2025]
            }
        """
        query = """
        MATCH (stats:_Schema:GraphStatistics)
        RETURN stats {.*} as statistics
        """
        results = self.query_neo4j(query)
        return results[0]["statistics"] if results else {}

    # ================================================================
    # END SCHEMA INTROSPECTION METHODS
    # ================================================================

    def close(self):
        """Close Neo4j driver connection"""
        self.driver.close()
        print(f"✓ Closed {self.facet_label} Agent")


class FacetAgentFactory:
    """Factory for creating facet agents with appropriate system prompts"""

    # 17 facet-specific system prompts (loaded from registry)
    FACET_PROMPTS = {}

    @staticmethod
    def load_facet_prompts(registry_path: str = "Facets/facet_registry_master.json"):
        """Load facet prompts from system prompt registry"""
        # To be populated from facet_agent_system_prompts.json
        pass

    @staticmethod
    def create_agent(facet_key: str, facet_label: str, system_prompt: str) -> FacetAgent:
        """
        Create a specialized facet agent
        
        Args:
            facet_key: Registry key (e.g., 'military')
            facet_label: Display label (e.g., 'Military')
            system_prompt: Facet-specific system prompt
            
        Returns:
            Instantiated FacetAgent subclass
        """
        # Create dynamic class inheriting from FacetAgent
        class SpecializedFacetAgent(FacetAgent):
            pass

        agent = SpecializedFacetAgent(facet_key, facet_label, system_prompt)
        return agent

    @staticmethod
    def create_all_agents() -> Dict[str, FacetAgent]:
        """
        Create all 17 facet agents
        
        Returns:
            Dict mapping facet_key → agent instance
        """
        agents = {}
        
        # Load prompts (to be populated from JSON)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'facet_agent_system_prompts.json')) as f:
            prompts_registry = json.load(f)

        for facet_config in prompts_registry['facets']:
            agent = FacetAgentFactory.create_agent(
                facet_key=facet_config['key'],
                facet_label=facet_config['label'],
                system_prompt=facet_config['system_prompt']
            )
            agents[facet_config['key']] = agent

        return agents


class MultiAgentRouter:
    """Routes queries to appropriate facet agents"""

    def __init__(self, agents: Dict[str, FacetAgent]):
        """
        Initialize router with agents
        
        Args:
            agents: Dict mapping facet_key → agent instance
        """
        self.agents = agents
        self.openai_api_key = OPENAI_API_KEY

    def route_query(self, user_query: str) -> Tuple[List[str], str]:
        """
        Determine which facet(s) a query should route to
        
        Args:
            user_query: Natural language query
            
        Returns:
            Tuple of (facet_keys, reasoning)
        """
        router_prompt = """You are a query router for a historical knowledge graph with these facets:
- archaeological, artistic, cultural, demographic, diplomatic, economic, environmental, geographic
- intellectual, linguistic, military, political, religious, scientific, social, technological, communication

Given a user query, identify which 1-3 facets are most relevant.

Return JSON with:
{
  "facets": ["facet_key1", "facet_key2"],
  "reasoning": "Why these facets"
}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3,
            max_tokens=200
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result["facets"], result["reasoning"]
        except:
            # Default to broader facets if parsing fails
            return ["political", "military"], "Default routing"

    def execute_multi_facet(self, user_query: str, facet_keys: List[str]) -> Dict[str, Any]:
        """
        Execute query across multiple facet agents
        Aggregate and deduplicate results
        
        Args:
            user_query: Query to execute
            facet_keys: List of facet keys to query
            
        Returns:
            Aggregated results dict
        """
        results = {
            "query": user_query,
            "facets": {},
            "aggregated": []
        }

        for facet_key in facet_keys:
            if facet_key not in self.agents:
                print(f"⚠ Facet '{facet_key}' not found")
                continue

            agent = self.agents[facet_key]
            facet_results = agent.query(user_query)
            results["facets"][facet_key] = facet_results

        return results

    def close_all(self):
        """Close all agent connections"""
        for agent in self.agents.values():
            agent.close()


# Test script
if __name__ == "__main__":
    print("Chrystallum Multi-Agent Facet Framework")
    print("=" * 60)

    # Example: Create a military facet agent
    military_prompt = """You are a Military History Expert Agent for the Chrystallum knowledge graph.
    
Your expertise:
- Warfare, battles, military campaigns, tactics, strategic operations
- Military leaders, commanders, generals, military institutions
- Armies, legions, military units, fortifications, weaponry
- Conflicts, wars, sieges, naval combat
- Military history, strategy, logistics, procurement

Key Wikidata Anchors:
Q8473 (military), Q198 (war), Q192781 (military history)

When querying:
1. Prioritize battles, military leaders, and warfare events
2. Look for Human nodes with military expertise (P101=military history)
3. Find Events classified as Q198 (wars)
4. Connect to tactical concepts and military strategies

Important: Distinguish between military operations and political outcomes."""

    print("\n→ Creating Military Facet Agent...")
    agent = FacetAgentFactory.create_agent(
        facet_key="military",
        facet_label="Military",
        system_prompt=military_prompt
    )

    print("\n→ Testing query...")
    result = agent.query("Show me battles in 31 BCE")

    print("\n→ Closing agent...")
    agent.close()

    print("\n✓ Framework test complete")
