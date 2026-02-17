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
from typing import Optional, Dict, Any, List, Tuple, Callable, Union
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from pathlib import Path
import hashlib
from neo4j import GraphDatabase, Driver
from openai import OpenAI

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


# ================================================================
# STEP 5: OPERATIONAL MODES & LOGGING FRAMEWORK
# ================================================================

class AgentOperationalMode(Enum):
    """Operational modes for agent workflows"""
    INITIALIZE = "initialize"
    TRAINING = "training"
    SCHEMA_QUERY = "schema_query"
    DATA_QUERY = "data_query"


class AgentLogger:
    """
    Verbose logging system for agent operations
    Logs to file and optionally streams to UI
    """
    
    def __init__(
        self, 
        agent_id: str, 
        mode: str, 
        session_id: str,
        log_to_file: bool = True,
        log_to_ui: bool = True
    ):
        """
        Initialize agent logger
        
        Args:
            agent_id: Identifier for the agent (e.g., 'military_agent')
            mode: Operational mode (initialize, training, etc.)
            session_id: Unique session identifier
            log_to_file: Whether to write to log file
            log_to_ui: Whether to stream to UI callback
        """
        self.agent_id = agent_id
        self.mode = mode
        self.session_id = session_id
        self.log_to_file = log_to_file
        self.log_to_ui = log_to_ui
        
        # Create logs directory if needed
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Log file path
        self.log_file = self.logs_dir / f"{agent_id}_{session_id}_{mode}.log"
        
        # UI callback for streaming
        self.ui_callback: Optional[Callable] = None
        
        # Session start time
        self.start_time = datetime.utcnow()
        
        # Metrics tracking
        self.metrics = {
            'actions': 0,
            'reasoning_steps': 0,
            'queries': 0,
            'errors': 0,
            'claims_proposed': 0,
            'nodes_created': 0
        }
        
        # Initialize log file
        if self.log_to_file:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"# Agent Log: {agent_id}\n")
                f.write(f"# Mode: {mode}\n")
                f.write(f"# Session: {session_id}\n")
                f.write(f"# Started: {self.start_time.isoformat()}\n")
                f.write("=" * 80 + "\n\n")
    
    def set_ui_callback(self, callback_fn: Callable[[str], None]):
        """Set callback function for streaming to UI"""
        self.ui_callback = callback_fn
    
    def _format_message(self, level: str, category: str, message: str) -> str:
        """Format log message with timestamp and metadata"""
        timestamp = datetime.utcnow().isoformat()
        return f"[{timestamp}] [{level}] [{category}] {message}"
    
    def _write(self, formatted_message: str):
        """Write to file and/or UI"""
        if self.log_to_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message + "\n")
        
        if self.log_to_ui and self.ui_callback:
            self.ui_callback(formatted_message)
    
    def log_action(self, action: str, details: Dict[str, Any], level: str = "INFO"):
        """
        Log an action with structured details
        
        Args:
            action: Action name (e.g., 'FETCH_WIKIDATA', 'BOOTSTRAP_START')
            details: Dictionary of action details
            level: Log level (INFO, WARNING, ERROR)
        """
        self.metrics['actions'] += 1
        
        # Format details
        details_str = ", ".join([f"{k}={v}" for k, v in details.items()])
        message = f"{action}: {details_str}"
        
        formatted = self._format_message(level, self.mode.upper(), message)
        self._write(formatted)
    
    def log_reasoning(self, decision: str, rationale: str, confidence: float, level: str = "INFO"):
        """
        Log reasoning behind a decision
        
        Args:
            decision: Decision made (e.g., 'PROPOSE_CLAIM', 'REJECT_ENTITY')
            rationale: Explanation for decision
            confidence: Confidence score (0.0-1.0)
            level: Log level
        """
        self.metrics['reasoning_steps'] += 1
        
        message = f"{decision}: {rationale} (confidence={confidence:.2f})"
        formatted = self._format_message(level, "REASONING", message)
        self._write(formatted)
    
    def log_query(self, query_type: str, query: str, result: Dict[str, Any], level: str = "INFO"):
        """
        Log a query execution
        
        Args:
            query_type: Type of query (DATA_QUERY, SCHEMA_QUERY, etc.)
            query: The query string (Cypher, natural language, etc.)
            result: Query result metadata
            level: Log level
        """
        self.metrics['queries'] += 1
        
        result_str = ", ".join([f"{k}={v}" for k, v in result.items()])
        message = f"{query_type}: {query[:100]}... → {result_str}"
        
        formatted = self._format_message(level, "QUERY", message)
        self._write(formatted)
    
    def log_error(self, error: str, context: Dict[str, Any], level: str = "ERROR"):
        """
        Log an error with context
        
        Args:
            error: Error message
            context: Context dictionary
            level: Log level (ERROR, WARNING)
        """
        self.metrics['errors'] += 1
        
        context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
        message = f"ERROR: {error} | Context: {context_str}"
        
        formatted = self._format_message(level, "ERROR", message)
        self._write(formatted)
    
    def log_claim_proposed(self, claim_id: str, label: str, confidence: float):
        """Track claim proposal"""
        self.metrics['claims_proposed'] += 1
        self.log_action("CLAIM_PROPOSED", {
            'claim_id': claim_id,
            'label': label[:80],
            'confidence': confidence
        })
    
    def log_node_created(self, node_id: str, node_label: str, node_type: str):
        """Track node creation"""
        self.metrics['nodes_created'] += 1
        self.log_action("NODE_CREATED", {
            'node_id': node_id,
            'label': node_label[:50],
            'type': node_type
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get session summary statistics
        
        Returns:
            Dictionary with metrics and metadata
        """
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'agent_id': self.agent_id,
            'mode': self.mode,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'duration_seconds': duration,
            'log_file': str(self.log_file),
            'metrics': self.metrics
        }
    
    def close(self):
        """Close logger and write summary"""
        summary = self.get_summary()
        
        if self.log_to_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write("# SESSION SUMMARY\n")
                f.write(f"# Duration: {summary['duration_seconds']:.1f}s\n")
                f.write(f"# Actions: {self.metrics['actions']}\n")
                f.write(f"# Reasoning steps: {self.metrics['reasoning_steps']}\n")
                f.write(f"# Queries: {self.metrics['queries']}\n")
                f.write(f"# Errors: {self.metrics['errors']}\n")
                f.write(f"# Claims proposed: {self.metrics['claims_proposed']}\n")
                f.write(f"# Nodes created: {self.metrics['nodes_created']}\n")
                f.write("=" * 80 + "\n")


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

        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

        # Initialize claim pipeline
        self.pipeline = ClaimIngestionPipeline(self.driver, database=NEO4J_DATABASE)

        # Step 5: Operational mode tracking
        self.current_mode: AgentOperationalMode = AgentOperationalMode.SCHEMA_QUERY  # Default mode
        self.session_id: str = self._generate_session_id()
        self.logger: Optional[AgentLogger] = None  # Initialized when mode is set
        
        # Cache for frequently loaded data
        self._cached_cidoc_crosswalk: Optional[Dict] = None
        self._cached_property_patterns: Optional[Dict] = None

        # Discover schema on init
        self.schema = self._discover_schema()
        print(f"✓ Initialized {self.facet_label} Agent")
        print(f"  Schema: {len(self.schema['labels'])} labels, {len(self.schema['relationship_types'])} relationships")
        print(f"  Session ID: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{self.facet_key}_{timestamp}"

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
        
        # Enrich with CIDOC-CRM ontology alignment (Step 4)
        entity = self.enrich_with_ontology_alignment(entity)
        
        # Extract CIDOC class for storage
        cidoc_class = entity.get('ontology_alignment', {}).get('cidoc_crm_class')
        cidoc_confidence = entity.get('ontology_alignment', {}).get('cidoc_crm_confidence')
        
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
            n.cidoc_crm_class = $cidoc_class,
            n.cidoc_crm_confidence = $cidoc_confidence,
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
            "timestamp": datetime.utcnow().isoformat(),
            "cidoc_class": cidoc_class,
            "cidoc_confidence": cidoc_confidence
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
            
            # Enrich claim with CRMinf ontology alignment (Step 4)
            claim = self.enrich_claim_with_crminf(claim, belief_value=0.90)
            
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
        auto_submit_claims: bool = False,
        validate_completeness: bool = True,
        min_completeness: float = 0.6
    ) -> Dict[str, Any]:
        """
        Bootstrap agent knowledge from a Wikidata QID
        
        Use this when agent is first instantiated on a new topic.
        
        Process:
        1. Fetch Wikidata entity
        2. (Optional) Validate entity completeness against empirical patterns
        3. Create SubjectConcept node
        4. Discover hierarchy (configurable depth)
        5. Generate claims for all discovered relationships
        6. Optionally auto-submit high-confidence claims
        
        Args:
            qid: Wikidata QID (e.g., 'Q17167' for Roman Republic)
            depth: Hierarchy traversal depth (1-3 recommended)
            auto_submit_claims: If True, submit claims >= 0.90 confidence
            validate_completeness: If True, check entity against property patterns
            min_completeness: Minimum completeness score (0.0-1.0) to proceed
            
        Returns:
            {
                'status': 'success' | 'rejected' | 'error',
                'root_qid': qid,
                'validation': completeness validation results,
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
        
        # Validate completeness if enabled
        validation = None
        if validate_completeness:
            print(f"🔍 Validating entity completeness...")
            validation = self.validate_entity_completeness(qid, entity_data=entity)
            
            completeness = validation.get('completeness_score', 0.0)
            recommendation = validation.get('recommendation', 'manual_review')
            
            print(f"  Completeness: {completeness:.1%} ({validation.get('status', 'unknown')})")
            print(f"  Type: {validation.get('entity_type_label', 'unknown')} (n={validation.get('sample_size', 0)})")
            print(f"  Recommendation: {recommendation}")
            
            if validation.get('missing_mandatory'):
                print(f"  ⚠ Missing mandatory properties: {', '.join(validation['missing_mandatory'][:5])}")
            
            # Check if we should proceed
            if completeness < min_completeness:
                print(f"✗ Entity completeness ({completeness:.1%}) below threshold ({min_completeness:.1%})")
                return {
                    'status': 'rejected',
                    'reason': f'Completeness {completeness:.1%} < {min_completeness:.1%}',
                    'root_qid': qid,
                    'root_label': entity['label'],
                    'validation': validation,
                    'nodes_created': 0,
                    'relationships_discovered': 0,
                    'claims_generated': 0,
                    'claims_submitted': 0
                }
            
            print(f"✓ Entity completeness acceptable, proceeding with bootstrap")
        
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
            'validation': validation,
            'nodes_created': hierarchy['total_discovered'],
            'relationships_discovered': len(hierarchy['discovered_relationships']),
            'claims_generated': len(result['claims_generated']),
            'claims_submitted': result['claims_submitted'],
            'hierarchy_data': hierarchy,
            'claims': result['claims_generated']
        }
    
    def _load_property_patterns(self) -> Dict[str, Any]:
        """
        Load empirically-derived property patterns from mined data
        
        Returns dictionary of type signatures: type_qid -> {mandatory, common, optional properties}
        Caches result for performance
        """
        if hasattr(self, '_cached_patterns'):
            return self._cached_patterns
        
        # Look for most recent property patterns file
        import glob
        pattern_files = glob.glob('property_patterns_large_sample_*.json')
        
        if not pattern_files:
            print("⚠ No property pattern files found, completeness validation disabled")
            self._cached_patterns = {}
            return {}
        
        # Use most recent
        latest_file = sorted(pattern_files)[-1]
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cached_patterns = data.get('signatures', {})
                print(f"✓ Loaded property patterns from {latest_file} ({len(self._cached_patterns)} types)")
                return self._cached_patterns
        except Exception as e:
            print(f"⚠ Error loading property patterns: {e}")
            self._cached_patterns = {}
            return {}
    
    def validate_entity_completeness(
        self,
        qid: str,
        entity_type: Optional[str] = None,
        entity_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Validate entity completeness against empirical property patterns
        
        Checks if entity has expected mandatory/common properties for its type.
        Uses patterns mined from 800+ Wikidata entities.
        
        Args:
            qid: Wikidata QID to validate
            entity_type: Expected type QID (e.g., 'Q178561' for battle). If None, auto-infers.
            entity_data: Pre-fetched entity data. If None, fetches from Wikidata.
        
        Returns:
            {
                'status': 'validated' | 'incomplete' | 'unknown_type',
                'completeness_score': 0.0-1.0,  # Weighted: 70% mandatory, 30% common
                'entity_type': inferred or provided type,
                'entity_type_label': human-readable type name,
                'missing_mandatory': [property IDs],
                'missing_common': [property IDs],
                'present_mandatory': [property IDs],
                'present_common': [property IDs],
                'recommendation': 'bootstrap' | 'manual_review' | 'reject',
                'sample_size': number of entities pattern is based on
            }
        """
        # Fetch entity if not provided
        if entity_data is None:
            entity_data = self.fetch_wikidata_entity(qid)
            if not entity_data:
                return {
                    'status': 'error',
                    'error': f'QID {qid} not found',
                    'completeness_score': 0.0
                }
        
        entity_props = set(entity_data.get('claims', {}).keys())
        
        # Load property patterns
        signatures = self._load_property_patterns()
        
        # Infer type if not provided
        if entity_type is None:
            # Extract P31 (instance of) from entity
            types = []
            if 'P31' in entity_data.get('claims', {}):
                for claim in entity_data['claims']['P31']:
                    if isinstance(claim, dict) and 'value' in claim:
                        types.append(claim['value'])
            
            # Use first type that has a signature
            entity_type = next((t for t in types if t in signatures), None)
            
            if not entity_type:
                return {
                    'status': 'unknown_type',
                    'entity_types_found': types,
                    'completeness_score': 0.5,
                    'recommendation': 'manual_review'
                }
        
        # Check if we have patterns for this type
        if entity_type not in signatures:
            return {
                'status': 'unknown_type',
                'entity_type': entity_type,
                'completeness_score': 0.5,
                'recommendation': 'manual_review',
                'note': f'No empirical patterns available for type {entity_type}'
            }
        
        # Get type signature
        type_sig = signatures[entity_type]
        mandatory_props = set(type_sig['mandatory']['properties'])
        common_props = set(type_sig['common']['properties'])
        
        # Calculate which properties are present/missing
        present_mandatory = mandatory_props & entity_props
        missing_mandatory = mandatory_props - entity_props
        present_common = common_props & entity_props
        missing_common = common_props - entity_props
        
        # Calculate completeness score (70% weight on mandatory, 30% on common)
        mandatory_coverage = len(present_mandatory) / len(mandatory_props) if mandatory_props else 1.0
        common_coverage = len(present_common) / len(common_props) if common_props else 1.0
        
        completeness_score = (mandatory_coverage * 0.7) + (common_coverage * 0.3)
        
        # Generate recommendation
        if completeness_score >= 0.8:
            recommendation = 'bootstrap'
        elif completeness_score >= 0.6:
            recommendation = 'manual_review'
        else:
            recommendation = 'reject'
        
        # Determine status
        if missing_mandatory:
            status = 'incomplete'
        else:
            status = 'validated'
        
        return {
            'status': status,
            'completeness_score': completeness_score,
            'entity_type': entity_type,
            'entity_type_label': type_sig.get('type_label', entity_type),
            'sample_size': type_sig.get('sample_size', 0),
            'mandatory_coverage': mandatory_coverage,
            'common_coverage': common_coverage,
            'missing_mandatory': list(missing_mandatory),
            'present_mandatory': list(present_mandatory),
            'missing_common': list(missing_common),
            'present_common': list(present_common),
            'recommendation': recommendation
        }
    
    # ================================================================
    # STEP 4: SEMANTIC ENRICHMENT & ONTOLOGY ALIGNMENT
    # ================================================================
    
    def _load_cidoc_crosswalk(self) -> Dict[str, Any]:
        """
        Load CIDOC-CRM / CRMinf / Wikidata crosswalk mappings
        
        Returns dictionary with mappings:
        - cidoc_by_qid: QID -> CIDOC class
        - cidoc_by_property: Wikidata P-code -> CIDOC property
        - crminf_mappings: CRMinf classes/properties
        """
        if hasattr(self, '_cached_cidoc_crosswalk'):
            return self._cached_cidoc_crosswalk
        
        crosswalk_file = 'CIDOC/cidoc_wikidata_mapping_validated.csv'
        
        if not os.path.exists(crosswalk_file):
            print(f"⚠ CIDOC crosswalk not found: {crosswalk_file}")
            self._cached_cidoc_crosswalk = {'cidoc_by_qid': {}, 'cidoc_by_property': {}, 'crminf_mappings': {}}
            return self._cached_cidoc_crosswalk
        
        import csv
        
        cidoc_by_qid = {}
        cidoc_by_property = {}
        crminf_mappings = {}
        
        try:
            with open(crosswalk_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cidoc_class = row.get('cidoc_class', '')
                    qid = row.get('wikidata_qid', '')
                    prop = row.get('wikidata_property', '')
                    confidence = row.get('confidence', '')
                    fallback = row.get('chrystallum_fallback', '')
                    
                    # Map QID -> CIDOC class
                    if qid and cidoc_class:
                        cidoc_by_qid[qid] = {
                            'cidoc_class': cidoc_class,
                            'confidence': confidence,
                            'chrystallum_fallback': fallback
                        }
                    
                    # Map property -> CIDOC property
                    if prop and cidoc_class:
                        # Property might be composite (P580+P582)
                        props = prop.replace('+', '|').split('|')
                        for p in props:
                            p = p.strip()
                            if p:
                                cidoc_by_property[p] = {
                                    'cidoc_property': cidoc_class,
                                    'confidence': confidence
                                }
                    
                    # Track CRMinf mappings
                    if cidoc_class.startswith('I') or cidoc_class.startswith('J'):
                        crminf_mappings[cidoc_class] = {
                            'wikidata_qid': qid,
                            'wikidata_property': prop,
                            'chrystallum_fallback': fallback
                        }
            
            self._cached_cidoc_crosswalk = {
                'cidoc_by_qid': cidoc_by_qid,
                'cidoc_by_property': cidoc_by_property,
                'crminf_mappings': crminf_mappings
            }
            
            print(f"✓ Loaded CIDOC crosswalk: {len(cidoc_by_qid)} QID mappings, {len(cidoc_by_property)} property mappings, {len(crminf_mappings)} CRMinf mappings")
            
        except Exception as e:
            print(f"⚠ Error loading CIDOC crosswalk: {e}")
            self._cached_cidoc_crosswalk = {'cidoc_by_qid': {}, 'cidoc_by_property': {}, 'crminf_mappings': {}}
        
        return self._cached_cidoc_crosswalk
    
    def enrich_with_ontology_alignment(
        self,
        entity_data: Dict[str, Any],
        entity_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich entity data with CIDOC-CRM and CRMinf ontology alignments
        
        Takes Wikidata entity and adds:
        - cidoc_crm_class: CIDOC-CRM class (e.g., E21_Person)
        - cidoc_crm_properties: Mapped properties
        - semantic_triples: Full QID + Property + Value + CIDOC alignment
        
        Args:
            entity_data: Entity from fetch_wikidata_entity() or similar
            entity_type: Optional type QID for classification
            
        Returns:
            Enriched entity with ontology_alignment section
        """
        crosswalk = self._load_cidoc_crosswalk()
        
        qid = entity_data.get('qid')
        claims = entity_data.get('claims', {})
        
        # Determine CIDOC class from QID or P31 (instance of)
        cidoc_class = None
        confidence = 'Unknown'
        
        if entity_type and entity_type in crosswalk['cidoc_by_qid']:
            mapping = crosswalk['cidoc_by_qid'][entity_type]
            cidoc_class = mapping['cidoc_class']
            confidence = mapping['confidence']
        elif 'P31' in claims:
            # Try to infer from instance-of
            for instance in claims.get('P31', []):
                instance_qid = instance.get('value') if isinstance(instance, dict) else None
                if instance_qid and instance_qid in crosswalk['cidoc_by_qid']:
                    mapping = crosswalk['cidoc_by_qid'][instance_qid]
                    cidoc_class = mapping['cidoc_class']
                    confidence = mapping['confidence']
                    break
        
        # Map properties to CIDOC properties
        cidoc_properties = {}
        semantic_triples = []
        
        for prop_id, prop_values in claims.items():
            # Check if this property has a CIDOC mapping
            if prop_id in crosswalk['cidoc_by_property']:
                cidoc_prop_info = crosswalk['cidoc_by_property'][prop_id]
                cidoc_properties[prop_id] = cidoc_prop_info['cidoc_property']
            
            # Generate semantic triples
            for value in prop_values if isinstance(prop_values, list) else [prop_values]:
                if isinstance(value, dict):
                    triple = {
                        'subject': qid,
                        'subject_label': entity_data.get('label'),
                        'property': prop_id,
                        'property_cidoc': cidoc_properties.get(prop_id),
                        'value': value.get('value'),
                        'value_label': value.get('label')
                    }
                    semantic_triples.append(triple)
        
        # Add ontology alignment to entity
        entity_data['ontology_alignment'] = {
            'cidoc_crm_class': cidoc_class,
            'cidoc_crm_confidence': confidence,
            'cidoc_properties': cidoc_properties,
            'semantic_triples': semantic_triples[:20],  # Limit to first 20
            'total_triples': len(semantic_triples)
        }
        
        return entity_data
    
    def enrich_claim_with_crminf(
        self,
        claim: Dict[str, Any],
        belief_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Enrich claim with CRMinf (CIDOC-CRM Argumentation) ontology alignment
        
        CRMinf models beliefs, inferences, and argumentation:
        - I2_Belief: A belief held by an agent
        - I4_Proposition_Set: Multiple related beliefs
        - I5_Inference_Making: Reasoning process
        - I6_Belief_Value: Confidence score
        - J5_holds_to_be: Belief adoption
        
        Maps Chrystallum Claim to CRMinf structure.
        
        Args:
            claim: Claim dictionary from generate_claims_from_wikidata() or similar
            belief_value: Optional confidence override
            
        Returns:
            Enriched claim with crminf_alignment section
        """
        crosswalk = self._load_cidoc_crosswalk()
        crminf = crosswalk.get('crminf_mappings', {})
        
        # Map Claim to I2_Belief (CRMinf core class)
        crminf_alignment = {
            'crminf_class': 'I2_Belief',
            'crminf_properties': {
                'J4_that': claim.get('label'),  # The proposition itself
                'J5_holds_to_be': belief_value or claim.get('confidence', 0.0),  # Belief value
            },
            'argumentation': {
                'source_agent': claim.get('agent_id', self.facet_key),
                'facet': claim.get('facet', self.facet_key),
                'rationale': claim.get('rationale', ''),
                'authority_source': claim.get('authority_source'),
                'inference_method': 'wikidata_federation' if claim.get('authority_source') == 'Wikidata' else 'agent_reasoning'
            }
        }
        
        # If this claim is part of multi-agent debate, mark as I4_Proposition_Set
        if claim.get('related_claims') or claim.get('debate_context'):
            crminf_alignment['proposition_set'] = 'I4_Proposition_Set'
            crminf_alignment['related_claims'] = claim.get('related_claims', [])
        
        # If confidence comes from inference, mark as I5_Inference_Making
        if claim.get('posterior_probability') or claim.get('bayesian_update'):
            crminf_alignment['inference_making'] = {
                'crminf_class': 'I5_Inference_Making',
                'prior': claim.get('prior_probability'),
                'likelihood': claim.get('likelihood'),
                'posterior': claim.get('posterior_probability')
            }
        
        claim['crminf_alignment'] = crminf_alignment
        
        return claim
    
    def generate_semantic_triples(
        self,
        entity_qid: str,
        include_cidoc: bool = True,
        include_crminf: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate complete semantic triples for an entity
        
        Each triple contains:
        - subject: QID
        - subject_label: Human-readable label
        - subject_cidoc: CIDOC class
        - property: Wikidata property (P-code)
        - property_cidoc: CIDOC property
        - value: QID or literal
        - value_label: Human-readable value
        - value_cidoc: CIDOC class (if value is entity)
        
        Args:
            entity_qid: Wikidata QID
            include_cidoc: Add CIDOC-CRM alignments
            include_crminf: Add CRMinf belief tracking
            
        Returns:
            List of semantic triples with full ontology alignment
        """
        # Fetch entity
        entity = self.fetch_wikidata_entity(entity_qid)
        if not entity:
            return []
        
        # Enrich with CIDOC
        if include_cidoc:
            entity = self.enrich_with_ontology_alignment(entity)
        
        triples = []
        
        for prop_id, values in entity.get('claims', {}).items():
            if not isinstance(values, list):
                values = [values]
            
            for value in values:
                if not isinstance(value, dict):
                    continue
                
                triple = {
                    'subject': entity_qid,
                    'subject_label': entity.get('label'),
                    'property': prop_id,
                    'value': value.get('value'),
                    'value_label': value.get('label')
                }
                
                # Add CIDOC alignment
                if include_cidoc and 'ontology_alignment' in entity:
                    alignment = entity['ontology_alignment']
                    triple['subject_cidoc'] = alignment.get('cidoc_crm_class')
                    triple['property_cidoc'] = alignment.get('cidoc_properties', {}).get(prop_id)
                    
                    # If value is a QID, try to get its CIDOC class
                    value_qid = value.get('value')
                    if value_qid and value_qid.startswith('Q'):
                        crosswalk = self._load_cidoc_crosswalk()
                        if value_qid in crosswalk['cidoc_by_qid']:
                            triple['value_cidoc'] = crosswalk['cidoc_by_qid'][value_qid]['cidoc_class']
                
                # Add CRMinf belief tracking
                if include_crminf:
                    triple['crminf_belief'] = {
                        'class': 'I2_Belief',
                        'confidence': 0.90,  # High confidence for Wikidata
                        'source': 'Wikidata',
                        'agent': self.facet_key
                    }
                
                triples.append(triple)
        
        return triples

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

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt_with_schema},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=500
        )

        cypher = (response.choices[0].message.content or "").strip()

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

    # ================================================================
    # STEP 5: OPERATIONAL MODE METHODS
    # Purpose: Execute workflows for Initialize, Training, Query modes
    # ================================================================

    def set_mode(self, mode: AgentOperationalMode, create_logger: bool = True):
        """
        Switch operational mode
        
        Args:
            mode: New operational mode
            create_logger: Whether to create a new logger for this mode
        """
        self.current_mode = mode
        
        if create_logger:
            # Close existing logger if any
            if self.logger:
                self.logger.close()
            
            # Create new logger for this mode
            self.logger = AgentLogger(
                agent_id=f"{self.facet_key}_agent",
                mode=mode.value,
                session_id=self.session_id,
                log_to_file=True,
                log_to_ui=True
            )
            
            self.logger.log_action("MODE_SWITCHED", {
                'mode': mode.value,
                'session_id': self.session_id
            })
        
        print(f"✓ {self.facet_label} Agent switched to {mode.value} mode")
    
    def get_mode(self) -> AgentOperationalMode:
        """Get current operational mode"""
        return self.current_mode
    
    def execute_initialize_mode(
        self, 
        anchor_qid: str, 
        depth: int = 2,
        auto_submit_claims: bool = False,
        ui_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        INITIALIZE MODE: Bootstrap new domain from scratch
        
        Workflow:
        1. Generate unique session ID
        2. Bootstrap from Wikidata QID anchor
        3. Validate completeness (Step 3.5)
        4. Enrich with CIDOC-CRM (Step 4)
        5. Discover hierarchy (Step 3)
        6. Build SubjectConcept structure
        7. Generate foundational claims
        8. Log all actions verbosely
        
        Args:
            anchor_qid: Starting Wikidata QID (e.g., 'Q17167' for Roman Republic)
            depth: Hierarchy traversal depth (1-3, default 2)
            auto_submit_claims: Whether to automatically submit high-confidence claims
            ui_callback: Optional callback for streaming log to UI
            
        Returns:
            {
                'session_id': str,
                'anchor_qid': str,
                'nodes_created': int,
                'relationships_discovered': int,
                'claims_generated': int,
                'claims_submitted': int,
                'completeness_score': float,
                'cidoc_crm_class': str,
                'duration_seconds': float,
                'status': str,
                'log_file': str
            }
        """
        start_time = datetime.utcnow()
        
        # Switch to initialize mode
        self.set_mode(AgentOperationalMode.INITIALIZE, create_logger=True)
        
        if ui_callback and self.logger:
            self.logger.set_ui_callback(ui_callback)
        
        self.logger.log_action("INITIALIZE_START", {
            'anchor_qid': anchor_qid,
            'depth': depth,
            'facet': self.facet_key,
            'auto_submit': auto_submit_claims
        })
        
        try:
            # Step 1: Fetch and validate anchor entity
            self.logger.log_action("FETCH_ANCHOR", {'qid': anchor_qid})
            entity = self.fetch_wikidata_entity(anchor_qid)
            
            if not entity:
                self.logger.log_error("Failed to fetch anchor entity", {'qid': anchor_qid})
                return {
                    'status': 'ERROR',
                    'error': f'Could not fetch Wikidata entity {anchor_qid}',
                    'log_file': str(self.logger.log_file)
                }
            
            self.logger.log_action("FETCH_COMPLETE", {
                'label': entity.get('label', 'Unknown'),
                'statements': entity.get('statement_count', 0)
            })
            
            # Step 2: Validate completeness
            entity_type = entity.get('claims', {}).get('P31', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
            
            completeness = self.validate_entity_completeness(entity, entity_type) if entity_type else {'score': 1.0, 'found_count': 0, 'expected_count': 0}
            
            self.logger.log_reasoning(
                decision="COMPLETENESS_VALIDATION",
                rationale=f"Found {completeness['found_count']}/{completeness['expected_count']} expected properties",
                confidence=completeness['score']
            )
            
            if completeness['score'] < 0.60:
                self.logger.log_reasoning(
                    decision="REJECT_ANCHOR",
                    rationale="Completeness score below 0.60 threshold",
                    confidence=completeness['score'],
                    level="WARNING"
                )
                return {
                    'status': 'REJECTED',
                    'reason': 'Low completeness score',
                    'completeness_score': completeness['score'],
                    'log_file': str(self.logger.log_file)
                }
            
            # Step 3: Enrich with CIDOC-CRM
            self.logger.log_action("CIDOC_ENRICHMENT", {'qid': anchor_qid})
            entity_enriched = self.enrich_with_ontology_alignment(entity)
            cidoc_class = entity_enriched.get('ontology_alignment', {}).get('cidoc_crm_class', 'Unknown')
            cidoc_confidence = entity_enriched.get('ontology_alignment', {}).get('cidoc_crm_confidence', 'Unknown')
            
            self.logger.log_action("CIDOC_COMPLETE", {
                'cidoc_class': cidoc_class,
                'confidence': cidoc_confidence
            })
            
            # Step 4: Bootstrap (creates nodes and discovers hierarchy)
            self.logger.log_action("BOOTSTRAP_START", {
                'qid': anchor_qid,
                'depth': depth
            })
            
            bootstrap_result = self.bootstrap_from_qid(
                qid=anchor_qid,
                depth=depth,
                auto_submit_claims=False  # Always review in initialize mode
            )
            
            self.logger.log_action("BOOTSTRAP_COMPLETE", {
                'nodes_created': bootstrap_result.get('nodes_created', 0),
                'relationships': bootstrap_result.get('relationships_discovered', 0),
                'claims_generated': bootstrap_result.get('claims_generated', 0)
            })
            
            # Step 5: Submit claims if requested
            claims_submitted = 0
            if auto_submit_claims and 'claims' in bootstrap_result:
                self.logger.log_action("CLAIM_SUBMISSION_START", {
                    'total_claims': len(bootstrap_result['claims'])
                })
                
                for claim in bootstrap_result['claims']:
                    if claim.get('confidence', 0) >= 0.90:
                        try:
                            self.pipeline.ingest_claim(claim)
                            claims_submitted += 1
                            self.logger.log_claim_proposed(
                                claim_id=claim.get('claim_id', 'unknown'),
                                label=claim.get('label', 'Unknown claim'),
                                confidence=claim.get('confidence', 0)
                            )
                        except Exception as e:
                            self.logger.log_error(f"Claim submission failed: {str(e)}", {
                                'claim_id': claim.get('claim_id', 'unknown')
                            })
                
                self.logger.log_action("CLAIM_SUBMISSION_COMPLETE", {
                    'submitted': claims_submitted,
                    'total': len(bootstrap_result['claims'])
                })
            
            # Step 6: Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Step 7: Prepare result
            result = {
                'status': 'INITIALIZED',
                'session_id': self.session_id,
                'anchor_qid': anchor_qid,
                'anchor_label': entity.get('label', 'Unknown'),
                'nodes_created': bootstrap_result.get('nodes_created', 0),
                'relationships_discovered': bootstrap_result.get('relationships_discovered', 0),
                'claims_generated': bootstrap_result.get('claims_generated', 0),
                'claims_submitted': claims_submitted,
                'completeness_score': completeness['score'],
                'cidoc_crm_class': cidoc_class,
                'cidoc_crm_confidence': cidoc_confidence,
                'duration_seconds': duration,
                'log_file': str(self.logger.log_file)
            }
            
            self.logger.log_action("INITIALIZE_COMPLETE", {
                'status': 'SUCCESS',
                'duration': f"{duration:.1f}s"
            })
            
            return result
            
        except Exception as e:
            self.logger.log_error(f"Initialize mode failed: {str(e)}", {
                'anchor_qid': anchor_qid,
                'depth': depth
            })
            
            return {
                'status': 'ERROR',
                'error': str(e),
                'session_id': self.session_id,
                'log_file': str(self.logger.log_file)
            }
    
    def execute_training_mode(
        self,
        max_iterations: int = 100,
        target_claims: int = 500,
        min_confidence: float = 0.80,
        auto_submit_high_confidence: bool = False,
        ui_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        TRAINING MODE: Extended iterative claim generation
        
        Workflow:
        1. Load session context (Step 2)
        2. Iterate through SubjectConcept nodes
        3. For each node:
           - Fetch Wikidata enrichment (if has QID)
           - Validate completeness (Step 3.5)
           - Enrich with CIDOC-CRM (Step 4)
           - Generate claims from statements (Step 3)
           - Enrich claims with CRMinf (Step 4)
           - Log reasoning for each decision
        4. Track metrics (claims/hour, promotion rate)
        5. Stop when target reached or iterations exhausted
        
        Args:
            max_iterations: Maximum nodes to process
            target_claims: Stop after generating this many claims
            min_confidence: Minimum confidence for claim proposals
            auto_submit_high_confidence: Auto-submit claims ≥0.90 confidence
            ui_callback: Optional callback for streaming log to UI
            
        Returns:
            {
                'session_id': str,
                'iterations': int,
                'nodes_processed': int,
                'claims_proposed': int,
                'claims_submitted': int,
                'avg_confidence': float,
                'completeness_scores': list,
                'duration_seconds': float,
                'claims_per_second': float,
                'status': str,
                'log_file': str
            }
        """
        start_time = datetime.utcnow()
        
        # Switch to training mode
        self.set_mode(AgentOperationalMode.TRAINING, create_logger=True)
        
        if ui_callback and self.logger:
            self.logger.set_ui_callback(ui_callback)
        
        self.logger.log_action("TRAINING_START", {
            'max_iterations': max_iterations,
            'target_claims': target_claims,
            'min_confidence': min_confidence,
            'auto_submit': auto_submit_high_confidence
        })
        
        try:
            # Step 1: Load session context
            self.logger.log_action("LOAD_CONTEXT", {})
            context = self.get_session_context()
            
            existing_nodes = context.get('subgraph_sample', {}).get('nodes', [])
            pending_claims = context.get('pending_claims', [])
            
            self.logger.log_action("CONTEXT_LOADED", {
                'existing_nodes': len(existing_nodes),
                'pending_claims': len(pending_claims)
            })
            
            # Metrics tracking
            claims_proposed = 0
            claims_submitted = 0
            nodes_processed = 0
            confidence_scores = []
            completeness_scores = []
            
            # Step 2: Iterate through nodes
            for i, node in enumerate(existing_nodes[:max_iterations]):
                nodes_processed += 1
                
                self.logger.log_action("ITERATION_START", {
                    'iteration': i + 1,
                    'total': min(max_iterations, len(existing_nodes)),
                    'node_id': node.get('id_hash', 'unknown'),
                    'node_label': node.get('label', 'Unknown')[:50]
                })
                
                # Check if node has Wikidata QID
                wikidata_qid = node.get('wikidata_qid')
                
                if not wikidata_qid:
                    self.logger.log_reasoning(
                        decision="SKIP_NODE",
                        rationale="No Wikidata QID available for enrichment",
                        confidence=0.0,
                        level="WARNING"
                    )
                    continue
                
                try:
                    # Fetch Wikidata entity
                    self.logger.log_action("FETCH_WIKIDATA", {'qid': wikidata_qid})
                    entity = self.fetch_wikidata_entity(wikidata_qid)
                    
                    if not entity:
                        self.logger.log_reasoning(
                            decision="SKIP_NODE",
                            rationale=f"Could not fetch Wikidata entity {wikidata_qid}",
                            confidence=0.0,
                            level="WARNING"
                        )
                        continue
                    
                    # Validate completeness
                    entity_type = entity.get('claims', {}).get('P31', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
                    completeness = self.validate_entity_completeness(entity, entity_type) if entity_type else {'score': 1.0}
                    
                    completeness_scores.append(completeness['score'])
                    
                    self.logger.log_reasoning(
                        decision="COMPLETENESS_VALIDATED",
                        rationale=f"{completeness.get('found_count', 0)}/{completeness.get('expected_count', 0)} properties",
                        confidence=completeness['score']
                    )
                    
                    # Generate claims
                    self.logger.log_action("GENERATE_CLAIMS", {'qid': wikidata_qid})
                    claims_result = self.generate_claims_from_wikidata(
                        qid=wikidata_qid,
                        create_nodes=False,  # Don't create new nodes in training mode
                        auto_submit=False
                    )
                    
                    generated_claims = claims_result.get('claims', [])
                    
                    self.logger.log_action("CLAIMS_GENERATED", {
                        'count': len(generated_claims),
                        'qid': wikidata_qid
                    })
                    
                    # Process each claim
                    for claim in generated_claims:
                        claim_confidence = claim.get('confidence', 0.0)
                        confidence_scores.append(claim_confidence)
                        
                        if claim_confidence >= min_confidence:
                            claims_proposed += 1
                            
                            self.logger.log_claim_proposed(
                                claim_id=claim.get('claim_id', f"claim_{claims_proposed}"),
                                label=claim.get('label', 'Unknown'),
                                confidence=claim_confidence
                            )
                            
                            # Auto-submit if confidence is high enough
                            if auto_submit_high_confidence and claim_confidence >= 0.90:
                                try:
                                    self.pipeline.ingest_claim(claim)
                                    claims_submitted += 1
                                    
                                    self.logger.log_action("CLAIM_SUBMITTED", {
                                        'claim_id': claim.get('claim_id', 'unknown'),
                                        'confidence': claim_confidence
                                    })
                                except Exception as e:
                                    self.logger.log_error(f"Claim submission failed: {str(e)}", {
                                        'claim_id': claim.get('claim_id', 'unknown')
                                    })
                    
                    self.logger.log_action("ITERATION_COMPLETE", {
                        'iteration': i + 1,
                        'claims_this_node': len(generated_claims),
                        'total_proposed': claims_proposed
                    })
                    
                    # Check if target reached
                    if claims_proposed >= target_claims:
                        self.logger.log_reasoning(
                            decision="TARGET_REACHED",
                            rationale=f"Reached target of {target_claims} claims",
                            confidence=1.0
                        )
                        break
                        
                except Exception as e:
                    self.logger.log_error(f"Node processing failed: {str(e)}", {
                        'node_id': node.get('id_hash', 'unknown'),
                        'qid': wikidata_qid
                    })
                    continue
            
            # Calculate metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            claims_per_second = claims_proposed / duration if duration > 0 else 0
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
            
            result = {
                'status': 'TRAINING_COMPLETE',
                'session_id': self.session_id,
                'iterations': nodes_processed,
                'nodes_processed': nodes_processed,
                'claims_proposed': claims_proposed,
                'claims_submitted': claims_submitted,
                'avg_confidence': avg_confidence,
                'avg_completeness': avg_completeness,
                'duration_seconds': duration,
                'claims_per_second': claims_per_second,
                'log_file': str(self.logger.log_file)
            }
            
            self.logger.log_action("TRAINING_COMPLETE", {
                'status': 'SUCCESS',
                'nodes_processed': nodes_processed,
                'claims_proposed': claims_proposed,
                'duration': f"{duration:.1f}s",
                'claims_per_second': f"{claims_per_second:.2f}"
            })
            
            return result
            
        except Exception as e:
            self.logger.log_error(f"Training mode failed: {str(e)}", {
                'max_iterations': max_iterations,
                'target_claims': target_claims
            })
            
            return {
                'status': 'ERROR',
                'error': str(e),
                'session_id': self.session_id,
                'log_file': str(self.logger.log_file)
            }

    # ================================================================
    # SUBJECT ONTOLOGY PROPOSAL: Bridge between Initialize and Training
    # ================================================================
    
    def propose_subject_ontology(
        self,
        ui_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        SUBJECT ONTOLOGY PROPOSAL: Examine hierarchical type properties
        
        After Initialize mode creates nodes, this step analyzes the discovered
        hierarchical type properties (P31 instance_of, P279 subclass_of, P361 part_of)
        to propose a coherent subject ontology structure for the facet.
        
        This ontology becomes the frame for Training mode claim generation.
        
        Workflow:
        1. Load initialized nodes and their type relationships
        2. Build type hierarchy (P31/P279 chains)
        3. Identify conceptual clusters
        4. Propose subject ontology with classes and relationships
        5. Generate ontology-scoped claim templates
        6. Recommend validation rules for Training mode
        
        Args:
            ui_callback: Optional callback for streaming log to UI
            
        Returns:
            {
                'status': str,
                'ontology_classes': List[Dict] - Proposed subject classes
                'hierarchy_depth': int - Deepest hierarchy level
                'clusters': List[Dict] - Identified conceptual clusters
                'relationships': List[Dict] - Ontology relationships
                'claim_templates': List[Dict] - Claim patterns for Training mode
                'validation_rules': List[Dict] - Rules for claim validation
                'strength_score': float - Confidence in proposed ontology (0-1)
                'reasoning': str - LLM reasoning about the ontology
                'log_file': str,
                'duration_seconds': float
            }
        """
        start_time = datetime.utcnow()
        
        # Use existing logger or create new one
        if not self.logger or self.current_mode != AgentOperationalMode.INITIALIZE:
            # Set temporary mode for logging
            self.set_mode(AgentOperationalMode.SCHEMA_QUERY, create_logger=True)
        
        if ui_callback and self.logger:
            self.logger.set_ui_callback(ui_callback)
        
        self.logger.log_action("ONTOLOGY_PROPOSAL_START", {
            'facet': self.facet_key,
            'session_id': self.session_id
        })
        
        try:
            # Step 1: Load initialized nodes with their hierarchical properties
            self.logger.log_action("LOAD_INITIALIZED_NODES", {})
            context = self.get_session_context()
            nodes = context.get('subgraph_sample', {}).get('nodes', [])
            
            self.logger.log_action("NODES_LOADED", {
                'count': len(nodes)
            })
            
            if not nodes:
                self.logger.log_reasoning(
                    decision="NO_NODES_TO_ANALYZE",
                    rationale="Initialize mode must run first to create nodes",
                    confidence=0.0
                )
                return {
                    'status': 'SKIPPED',
                    'reason': 'No initialized nodes found. Run Initialize mode first.',
                    'log_file': str(self.logger.log_file) if self.logger else 'N/A'
                }
            
            # Step 2: Extract type hierarchies (P31=instance_of, P279=subclass_of)
            self.logger.log_action("ANALYZE_TYPE_HIERARCHIES", {})
            
            type_hierarchies = {}
            for node in nodes:
                node_id = node.get('id_hash', node.get('label', 'unknown'))
                qid = node.get('wikidata_qid')
                
                if qid:
                    # Fetch full entity to get P31/P279 chains
                    try:
                        entity = self.fetch_wikidata_entity(qid)
                        
                        # Extract P31 (instance_of) claims
                        instance_of = entity.get('claims', {}).get('P31', [])
                        subclass_of = entity.get('claims', {}).get('P279', [])
                        part_of = entity.get('claims', {}).get('P361', [])
                        
                        type_hierarchies[node_id] = {
                            'node_label': node.get('label'),
                            'qid': qid,
                            'instance_of': [self._extract_qid_from_claim(c) for c in instance_of],
                            'subclass_of': [self._extract_qid_from_claim(c) for c in subclass_of],
                            'part_of': [self._extract_qid_from_claim(c) for c in part_of],
                            'depth': max(len(instance_of), len(subclass_of), len(part_of))
                        }
                        
                        self.logger.log_reasoning(
                            decision=f"ANALYZED_HIERARCHY",
                            rationale=f"Found {len(instance_of)} instance_of, {len(subclass_of)} subclass_of, {len(part_of)} part_of",
                            confidence=0.95
                        )
                    except Exception as e:
                        self.logger.log_error(f"Failed to analyze {node_id}: {str(e)}", {'qid': qid})
                        continue
            
            self.logger.log_action("TYPE_HIERARCHIES_COMPLETE", {
                'nodes_analyzed': len(type_hierarchies)
            })
            
            # Step 3: Identify conceptual clusters using LLM
            self.logger.log_action("IDENTIFY_CLUSTERS", {})
            
            # Build cluster analysis prompt
            cluster_prompt = f"""Analyze these {len(type_hierarchies)} entities from the {self.facet_label} domain:

"""
            for node_id, hierarchy in list(type_hierarchies.items())[:10]:  # Show first 10
                types_str = ', '.join(hierarchy['instance_of'][:3]) if hierarchy['instance_of'] else 'untyped'
                cluster_prompt += f"- {hierarchy['node_label']} (types: {types_str})\n"
            
            cluster_prompt += f"""
Based on their hierarchical types (instance_of, subclass_of, part_of), identify:
1. Natural conceptual clusters in this domain
2. The main categories/classes
3. How they relate to each other
4. Characteristic properties for each cluster

Return JSON:
{{
  "clusters": [
    {{
      "name": "Cluster name",
      "concept_count": number,
      "examples": ["label1", "label2"],
      "characteristics": ["property1", "property2"],
      "parent_cluster": "name or null"
    }}
  ],
  "hierarchy_depth": max_depth,
  "reasoning": "Why these clusters make sense for this domain"
}}"""
            
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are analyzing {self.facet_label} domain structure."},
                        {"role": "user", "content": cluster_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                
                cluster_analysis = json.loads(response.choices[0].message.content or "{}")
                clusters = cluster_analysis.get('clusters', [])
                hierarchy_depth = cluster_analysis.get('hierarchy_depth', max(h['depth'] for h in type_hierarchies.values()))
                ontology_reasoning = cluster_analysis.get('reasoning', 'Analysis complete')
                
                self.logger.log_action("CLUSTERS_IDENTIFIED", {
                    'cluster_count': len(clusters),
                    'hierarchy_depth': hierarchy_depth
                })
                
            except Exception as e:
                self.logger.log_error(f"Cluster analysis failed: {str(e)}", {})
                clusters = []
                hierarchy_depth = max(h['depth'] for h in type_hierarchies.values()) if type_hierarchies else 0
                ontology_reasoning = "Cluster analysis failed, using hierarchical depth only"
            
            # Step 4: Propose ontology classes and relationships
            self.logger.log_action("PROPOSE_ONTOLOGY", {})
            
            ontology_classes = []
            for cluster in clusters:
                ontology_classes.append({
                    'class_name': cluster.get('name'),
                    'parent_class': cluster.get('parent_cluster'),
                    'member_count': cluster.get('concept_count', 0),
                    'characteristics': cluster.get('characteristics', []),
                    'examples': cluster.get('examples', [])[:3]
                })
            
            # Extract relationships between classes
            relationships = []
            for i, cls1 in enumerate(ontology_classes):
                for cls2 in ontology_classes[i+1:]:
                    if cls1['parent_class'] == cls2['class_name']:
                        relationships.append({
                            'source': cls2['class_name'],
                            'target': cls1['class_name'],
                            'relationship_type': 'subclass_of',
                            'confidence': 0.85
                        })
            
            self.logger.log_action("ONTOLOGY_PROPOSED", {
                'class_count': len(ontology_classes),
                'relationship_count': len(relationships)
            })
            
            # Step 5: Generate claim templates for Training mode
            self.logger.log_action("GENERATE_CLAIM_TEMPLATES", {})
            
            claim_templates = []
            for cls in ontology_classes:
                # Properties typically claimed for each class
                properties = cls.get('characteristics', [])[:5]
                
                for prop in properties:
                    claim_templates.append({
                        'claim_class': cls['class_name'],
                        'property': prop,
                        'template': f"All {{subject}} in {cls['class_name']} {{verb}} {{value}}",
                        'validation': f"Check if {{value}} is a valid {prop}",
                        'expected_confidence': 0.85
                    })
            
            self.logger.log_action("CLAIM_TEMPLATES_GENERATED", {
                'template_count': len(claim_templates)
            })
            
            # Step 6: Recommend validation rules
            self.logger.log_action("DEFINE_VALIDATION_RULES", {})
            
            validation_rules = [
                {
                    'rule': 'Within_ontology_class',
                    'description': 'Subject must be instance of ontology class',
                    'importance': 'HIGH'
                },
                {
                    'rule': 'Property_cardinality',
                    'description': 'Property values must match class characteristic cardinality',
                    'importance': 'MEDIUM'
                },
                {
                    'rule': 'Temporal_consistency',
                    'description': 'Claims must be temporally consistent with entity dates',
                    'importance': 'MEDIUM'
                },
                {
                    'rule': 'Cross_facet_alignment',
                    'description': 'Property values should align with related facets',
                    'importance': 'LOW'
                }
            ]
            
            # Calculate strength score (0-1)
            strength_score = min(1.0, (len(ontology_classes) / 10) * (hierarchy_depth / 5) * 0.9)
            
            self.logger.log_reasoning(
                decision="ONTOLOGY_STRENGTH",
                rationale=f"Based on {len(ontology_classes)} classes and hierarchy depth {hierarchy_depth}",
                confidence=strength_score
            )
            
            # Duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                'status': 'ONTOLOGY_PROPOSED',
                'session_id': self.session_id,
                'facet': self.facet_key,
                'ontology_classes': ontology_classes,
                'hierarchy_depth': hierarchy_depth,
                'clusters': clusters,
                'relationships': relationships,
                'claim_templates': claim_templates,
                'validation_rules': validation_rules,
                'strength_score': strength_score,
                'reasoning': ontology_reasoning,
                'duration_seconds': duration,
                'log_file': str(self.logger.log_file) if self.logger else 'N/A'
            }
            
            self.logger.log_action("ONTOLOGY_PROPOSAL_COMPLETE", {
                'status': 'SUCCESS',
                'classes': len(ontology_classes),
                'strength': f"{strength_score:.2f}",
                'duration': f"{duration:.1f}s"
            })
            
            return result
            
        except Exception as e:
            self.logger.log_error(f"Subject ontology proposal failed: {str(e)}", {
                'facet': self.facet_key
            })
            
            return {
                'status': 'ERROR',
                'error': str(e),
                'session_id': self.session_id,
                'log_file': str(self.logger.log_file) if self.logger else 'N/A'
            }
    
    def _extract_qid_from_claim(self, claim: Dict) -> str:
        """Extract QID from Wikidata claim structure"""
        try:
            return claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
        except:
            return ''

    # ================================================================
    # END STEP 5 OPERATIONAL MODE METHODS
    # ================================================================

    def close(self):
        """Close Neo4j driver connection and logger"""
        if self.logger:
            self.logger.close()
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
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

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

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3,
            max_tokens=200
        )

        try:
            result = json.loads(response.choices[0].message.content or "{}")
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


# ================================================================
# SUBJECT CONCEPT AGENT (SCA) - MASTER COORDINATOR
# ================================================================

class SubjectConceptAgent:
    """
    Master coordinator agent that orchestrates multiple SubjectFacetAgents (SFAs)
    
    Capabilities:
    - Cross-domain query orchestration
    - Facet classification for queries
    - Multi-agent claim routing
    - Result synthesis across domains
    
    This enables queries like "What is the relationship between a Roman senator and a mollusk?"
    which requires coordination between political, biology, and material_culture facets.
    """
    
    def __init__(self, factory: 'FacetAgentFactory' = None, driver: Driver = None):
        """
        Initialize SubjectConceptAgent
        
        Args:
            factory: Optional FacetAgentFactory (creates one if not provided)
            driver: Optional Neo4j driver (uses default if not provided)
        """
        self.factory = factory or FacetAgentFactory()
        self.driver = driver or GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.active_agents = {}  # Cache of spawned agents: facet_key → agent
        self.openai_api_key = OPENAI_API_KEY
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        print("✓ SubjectConceptAgent (SCA) initialized - Master Coordinator ready")
    
    def classify_facets(self, query: str, max_facets: int = 3) -> Dict[str, Any]:
        """
        Use LLM to determine which facets are relevant for a query
        
        Args:
            query: Natural language query
            max_facets: Maximum number of facets to return (default 3)
            
        Returns:
            Dict with 'facets' (list of keys), 'reasoning' (str), 'cross_domain' (bool)
        """
        classification_prompt = """You are a facet classifier for the Chrystallum historical knowledge graph.

Available facets (17 total):
1. archaeological - Material cultures, site phases, stratigraphic horizons, excavations
2. artistic - Visual arts, sculpture, architecture, aesthetics, artistic movements  
3. cultural - Social customs, traditions, practices, cultural identity, festivals
4. demographic - Population, census, migration, settlement patterns, urbanization
5. diplomatic - Treaties, alliances, embassies, negotiations, international relations
6. economic - Trade, commerce, markets, taxation, currency, fiscal policy
7. environmental - Climate, natural disasters, ecology, agriculture, resources
8. geographic - Places, regions, territories, boundaries, physical features
9. intellectual - Philosophy, ideas, education, scholarship, intellectual movements
10. linguistic - Languages, writing systems, etymology, translation, scripts
11. military - Warfare, battles, campaigns, fortifications, armies, tactics
12. political - Governance, offices, succession, law, political structures, administration
13. religious - Religion, deities, temples, clergy, rituals, theology, beliefs
14. scientific - Science, discoveries, natural philosophy, mathematics, astronomy
15. social - Social structures, class, family, gender, daily life, social movements
16. technological - Technology, inventions, engineering, infrastructure, construction
17. communication - Writing, printing, roads, messengers, postal systems, media

Analyze the query and return JSON:
{
  "facets": ["facet_key1", "facet_key2"],
  "reasoning": "Brief explanation of why these facets",
  "cross_domain": true/false,
  "bridge_concepts": ["concept that links domains"]
}

Rules:
- Return 1-3 most relevant facets
- Set cross_domain=true if query spans multiple domains
- Identify bridge concepts for cross-domain queries
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": classification_prompt},
                    {"role": "user", "content": f"Query: {query}"}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content or "{}")
            
            # Limit to max_facets
            if len(result['facets']) > max_facets:
                result['facets'] = result['facets'][:max_facets]
            
            return result
        
        except Exception as e:
            print(f"⚠ Facet classification failed: {e}")
            # Default fallback
            return {
                'facets': ['political', 'military'],
                'reasoning': 'Default classification due to error',
                'cross_domain': False,
                'bridge_concepts': []
            }
    
    def spawn_agent(self, facet_key: str, mode: str = 'real') -> Union[FacetAgent, Dict[str, Any]]:
        """
        Spawn a SubjectFacetAgent (real or simulated)
        
        Args:
            facet_key: Facet identifier (e.g., 'military', 'political')
            mode: 'real' (default) or 'simulated'
                  - real: Spawns actual FacetAgent with LLM integration
                  - simulated: Returns mock stub for testing orchestration
            
        Returns:
            FacetAgent instance (mode='real') or Dict stub (mode='simulated')
        """
        if facet_key in self.active_agents:
            return self.active_agents[facet_key]
        
        # Validate facet exists
        valid_facets = ['archaeological', 'artistic', 'cultural', 'demographic', 'diplomatic',
                       'economic', 'environmental', 'geographic', 'intellectual', 'linguistic',
                       'military', 'political', 'religious', 'scientific', 'social',
                       'technological', 'communication']
        
        if facet_key not in valid_facets:
            raise ValueError(f"Unknown facet: {facet_key}. Must be one of {valid_facets}")
        
        # Simulated mode (legacy for testing orchestration)
        if mode == 'simulated':
            return self._spawn_simulated_agent(facet_key)
        
        # Real mode: Create actual FacetAgent
        return self._spawn_real_agent(facet_key)
    
    def _spawn_simulated_agent(self, facet_key: str) -> Dict[str, Any]:
        """
        Create simulated agent stub for testing orchestration logic
        
        Args:
            facet_key: Facet identifier
            
        Returns:
            Dict with simulated agent interface
        """
        simulated_agent = {
            'facet_key': facet_key,
            'facet_label': facet_key.capitalize(),
            'type': 'SIMULATED',
            'query_method': self._simulate_facet_query
        }
        
        self.active_agents[facet_key] = simulated_agent
        print(f"✓ Simulated SubjectFacetAgent: {facet_key.capitalize()} (smoke test mode)")
        return simulated_agent
    
    def _spawn_real_agent(self, facet_key: str) -> FacetAgent:
        """
        Create real FacetAgent instance with LLM integration
        
        Args:
            facet_key: Facet identifier
            
        Returns:
            FacetAgent instance
        """
        # Load system prompts from JSON
        prompts_file = os.path.join(os.path.dirname(__file__), '..', '..', 
                                   'facet_agent_system_prompts.json')
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts_registry = json.load(f)
        
        # Find facet config
        facet_config = next(
            (f for f in prompts_registry['facets'] if f['key'] == facet_key),
            None
        )
        
        if not facet_config:
            raise ValueError(f"No system prompt found for facet: {facet_key}")
        
        # Create real agent using FacetAgentFactory
        agent = FacetAgentFactory.create_agent(
            facet_key=facet_config['key'],
            facet_label=facet_config['label'],
            system_prompt=facet_config['system_prompt']
        )
        
        # Cache it
        self.active_agents[facet_key] = agent
        
        print(f"✓ Spawned REAL SubjectFacetAgent: {facet_key.capitalize()} (LLM-enabled)")
        return agent
    
    def _execute_real_agent_query(self, agent: FacetAgent, query: str) -> Dict[str, Any]:
        """
        Execute query on real FacetAgent instance
        
        For now, this constructs a Neo4j query filtered by the agent's facet.
        In future, agents could have more sophisticated query methods.
        
        Args:
            agent: Real FacetAgent instance
            query: Natural language query
            
        Returns:
            Dict with nodes, edges, and analysis from agent's perspective
        """
        # Extract key terms from query for Neo4j search
        # This is a simple implementation - agents could have better query understanding
        search_terms = [term.strip().lower() for term in query.split() 
                       if len(term) > 3 and term.lower() not in 
                       ['what', 'how', 'when', 'where', 'the', 'and', 'between']]
        
        nodes = []
        edges = []
        
        # Query Neo4j for nodes matching search terms and agent's facet
        if search_terms and agent.driver:
            try:
                with agent.driver.session() as session:
                    # Search for SubjectConcept nodes
                    cypher = """
                    MATCH (sc:SubjectConcept)
                    WHERE toLower(sc.label) CONTAINS $term
                    RETURN sc.qid as qid, sc.label as label, 
                           sc.facet as facet, id(sc) as node_id
                    LIMIT 10
                    """
                    
                    for term in search_terms[:3]:  # Limit to first 3 terms
                        result = session.run(cypher, term=term)
                        for record in result:
                            nodes.append({
                                'id': f"node_{agent.facet_key}_{record['node_id']}",
                                'qid': record['qid'],
                                'label': record['label'],
                                'facet': agent.facet_key
                            })
            except Exception as e:
                print(f"    ⚠ Neo4j query failed: {e}")
        
        # If no results from Neo4j, return empty result
        if not nodes:
            nodes = [{
                'id': f'node_{agent.facet_key}_placeholder',
                'label': f'{query} ({agent.facet_key} perspective)',
                'facet': agent.facet_key
            }]
        
        return {
            'status': 'SUCCESS',
            'facet': agent.facet_key,
            'query': query,
            'nodes': nodes,
            'edges': edges,
            'agent_type': 'REAL',
            'reasoning': f'Analyzed from {agent.facet_key} domain perspective'
        }
    
    def execute_cross_domain_query(self, query: str, auto_classify: bool = True, 
                                   facets: List[str] = None) -> Dict[str, Any]:
        """
        Execute a query across multiple facets and synthesize results
        
        Args:
            query: Natural language query
            auto_classify: Whether to auto-classify facets (default True)
            facets: Optional explicit list of facet keys (overrides auto_classify)
            
        Returns:
            Dict with orchestrated results from all facets
        """
        print(f"\n{'='*60}")
        print(f"SCA CROSS-DOMAIN QUERY: {query}")
        print(f"{'='*60}")
        
        # Step 1: Classify facets
        if not facets:
            classification = self.classify_facets(query)
            facets = classification['facets']
            cross_domain = classification['cross_domain']
            bridge_concepts = classification.get('bridge_concepts', [])
            reasoning = classification['reasoning']
            
            print(f"\n→ Facet Classification:")
            print(f"  Facets: {', '.join(facets)}")
            print(f"  Cross-domain: {cross_domain}")
            print(f"  Reasoning: {reasoning}")
            if bridge_concepts:
                print(f"  Bridge concepts: {', '.join(bridge_concepts)}")
        else:
            cross_domain = len(facets) > 1
            bridge_concepts = []
            reasoning = "Explicit facets provided"
        
        # Step 2: Spawn sub-agents
        print(f"\n→ Spawning SubjectFacetAgents...")
        agents = {}
        for facet_key in facets:
            try:
                agents[facet_key] = self.spawn_agent(facet_key, mode='real')
            except Exception as e:
                print(f"⚠ Failed to spawn {facet_key} agent: {e}")
        
        if not agents:
            return {
                'status': 'ERROR',
                'error': 'No agents could be spawned',
                'query': query
            }
        
        # Step 3: Execute domain queries
        print(f"\n→ Executing domain queries...")
        facet_results = {}
        for facet_key, agent in agents.items():
            try:
                # Determine if real agent or simulated
                if isinstance(agent, FacetAgent):
                    print(f"  Querying REAL {facet_key} agent...")
                    # Use real agent's data query method
                    result = self._execute_real_agent_query(agent, query)
                    facet_results[facet_key] = result
                    print(f"  ✓ {facet_key}: {len(result.get('nodes', []))} nodes")
                else:
                    # Simulated agent (legacy)
                    print(f"  Simulating {facet_key} agent query...")
                    result = agent['query_method'](facet_key, query)
                    facet_results[facet_key] = result
                    print(f"  ✓ {facet_key}: {len(result.get('nodes', []))} simulated nodes")
            
            except Exception as e:
                print(f"  ⚠ {facet_key} query failed: {e}")
                facet_results[facet_key] = {'status': 'ERROR', 'error': str(e)}
        
        # Step 4: Generate bridge claims (if cross-domain)
        bridge_claims = []
        if cross_domain and len(facet_results) > 1:
            print(f"\n→ Generating bridge claims...")
            bridge_claims = self._find_conceptual_bridges(facet_results, bridge_concepts)
            print(f"  ✓ Generated {len(bridge_claims)} bridge claims (node/edge creation)")
        
        # Step 5: Synthesize integrated response
        print(f"\n→ Synthesizing cross-domain response...")
        synthesized = self._synthesize_response(query, facet_results, bridge_claims, cross_domain)
        
        # Step 6: Return orchestrated result
        result = {
            'status': 'SUCCESS',
            'query': query,
            'classification': {
                'facets': facets,
                'cross_domain': cross_domain,
                'reasoning': reasoning,
                'bridge_concepts': bridge_concepts
            },
            'facet_results': facet_results,
            'bridge_claims': bridge_claims,
            'synthesized_response': synthesized,
            'total_nodes': sum(len(r.get('nodes', [])) for r in facet_results.values() if isinstance(r, dict)),
            'total_claims': sum(len(r.get('claims', [])) for r in facet_results.values() if isinstance(r, dict)),
            'bridge_claim_count': len(bridge_claims)
        }
        
        print(f"\n{'='*60}")
        print(f"✓ Cross-domain query complete")
        print(f"  Facets queried: {len(facet_results)}")
        print(f"  Total nodes: {result['total_nodes']}")
        print(f"  Bridge claims generated: {len(bridge_claims)}")
        print(f"{'='*60}\n")
        
        return result
    
    def query_within_facet(self, query: str, facet_key: str) -> Dict[str, Any]:
        """
        Execute a single-facet query (convenience method)
        
        Args:
            query: Natural language query
            facet_key: Specific facet to query
            
        Returns:
            Query results from that facet
        """
        agent = self.spawn_agent(facet_key)
        
        if hasattr(agent, 'execute_data_query'):
            return agent.execute_data_query(query)
        else:
            # Fallback: use session context
            context = agent.get_session_context()
            return {
                'status': 'SUCCESS',
                'facet': facet_key,
                'nodes': context['subgraph_sample']['nodes'][:10],
                'note': 'Using session context (data_query mode not implemented)'
            }
    
    def route_claim(self, claim: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Tag a claim with relevant facets and route to multiple SFAs
        
        Args:
            claim: Claim dict with subject, predicate, object
            
        Returns:
            Dict with 'routed_to' (list of facet keys) and 'reasoning'
        """
        # Analyze claim to determine facets
        claim_text = f"{claim.get('subject', '')} {claim.get('predicate', '')} {claim.get('object', '')}"
        classification = self.classify_facets(claim_text, max_facets=5)
        
        facets = classification['facets']
        
        print(f"\n→ Routing claim to {len(facets)} facet(s): {', '.join(facets)}")
        print(f"  Claim: {claim.get('label', claim_text[:60])}")
        
        # Route to each facet's agent
        routed = []
        for facet_key in facets:
            try:
                agent = self.spawn_agent(facet_key)
                
                # Add facet tag to claim
                if 'facets' not in claim:
                    claim['facets'] = []
                if facet_key not in claim['facets']:
                    claim['facets'].append(facet_key)
                
                # Ingest claim through agent's pipeline
                if hasattr(agent, 'pipeline'):
                    agent.pipeline.ingest_claim(claim)
                    routed.append(facet_key)
                    print(f"  ✓ Ingested to {facet_key}")
                else:
                    print(f"  ⚠ {facet_key} agent has no pipeline")
            
            except Exception as e:
                print(f"  ⚠ Failed to route to {facet_key}: {e}")
        
        return {
            'routed_to': routed,
            'reasoning': classification['reasoning'],
            'cross_domain': len(routed) > 1
        }
    
    def _find_conceptual_bridges(self, facet_results: Dict[str, Any], 
                                 suggested_bridges: List[str]) -> List[Dict[str, Any]]:
        """
        Generate bridge claims connecting concepts across domains
        
        Bridge discovery creates node/edge claims that link concepts from different facets.
        Example: "Tyrian purple" bridges political (toga), biology (murex), material_culture (dye)
        → Generates claims: CREATE nodes for bridge concept, CREATE edges to related nodes
        
        Args:
            facet_results: Results from each facet
            suggested_bridges: LLM-suggested bridge concepts
            
        Returns:
            List of bridge claim dicts (node creation or edge creation claims)
        """
        bridge_claims = []
        
        # Extract all node labels from each facet
        facet_nodes = {}
        for facet_key, result in facet_results.items():
            if isinstance(result, dict) and 'nodes' in result:
                facet_nodes[facet_key] = result['nodes']
        
        # Find label intersections (concepts appearing in multiple facets)
        # These become NODE CREATION claims for the bridge concept
        if len(facet_nodes) >= 2:
            facet_keys = list(facet_nodes.keys())
            for i in range(len(facet_keys)):
                for j in range(i+1, len(facet_keys)):
                    f1, f2 = facet_keys[i], facet_keys[j]
                    
                    # Find nodes with matching labels
                    labels_f1 = {node.get('label', ''): node for node in facet_nodes[f1]}
                    labels_f2 = {node.get('label', ''): node for node in facet_nodes[f2]}
                    
                    intersection = set(labels_f1.keys()) & set(labels_f2.keys())
                    
                    for label in intersection:
                        if not label:
                            continue
                        
                        # Generate NODE CREATION claim for bridge concept
                        node_claim = {
                            'claim_type': 'NODE_CREATION',
                            'label': label,
                            'node_type': 'SubjectConcept',
                            'facets': [f1, f2],  # Multi-facet claim
                            'properties': {
                                'bridge_type': 'label_intersection',
                                'source_facets': [f1, f2]
                            },
                            'confidence': 0.85,
                            'reasoning': f'Concept "{label}" appears in both {f1} and {f2} domains'
                        }
                        bridge_claims.append(node_claim)
                        
                        # Generate EDGE CREATION claims linking to source nodes
                        edge_claim_f1 = {
                            'claim_type': 'EDGE_CREATION',
                            'source_node': labels_f1[label].get('id'),
                            'target_node': label,  # Bridge node
                            'relationship_type': 'RELATES_TO',
                            'facet': f1,
                            'confidence': 0.85,
                            'reasoning': f'Bridge connection from {f1} domain'
                        }
                        bridge_claims.append(edge_claim_f1)
                        
                        edge_claim_f2 = {
                            'claim_type': 'EDGE_CREATION',
                            'source_node': labels_f2[label].get('id'),
                            'target_node': label,  # Bridge node
                            'relationship_type': 'RELATES_TO',
                            'facet': f2,
                            'confidence': 0.85,
                            'reasoning': f'Bridge connection from {f2} domain'
                        }
                        bridge_claims.append(edge_claim_f2)
        
        # Process suggested bridges - generate NODE MODIFICATION claims
        for bridge_concept in suggested_bridges:
            matching_nodes = []
            for facet_key, nodes in facet_nodes.items():
                for node in nodes:
                    if bridge_concept.lower() in node.get('label', '').lower():
                        matching_nodes.append((facet_key, node))
            
            if matching_nodes:
                # Generate NODE MODIFICATION claim to add bridge properties
                facets_found = list(set(f for f, _ in matching_nodes))
                mod_claim = {
                    'claim_type': 'NODE_MODIFICATION',
                    'label': bridge_concept,
                    'node_id': matching_nodes[0][1].get('id'),
                    'modifications': {
                        'add_facets': facets_found,
                        'add_property': {
                            'key': 'bridge_concept',
                            'value': True
                        }
                    },
                    'confidence': 0.80,
                    'reasoning': f'Suggested bridge "{bridge_concept}" found in {len(facets_found)} domain(s)'
                }
                bridge_claims.append(mod_claim)
        
        return bridge_claims
    
    def _simulate_facet_query(self, facet_key: str, query: str) -> Dict[str, Any]:
        """
        Simulate a facet agent query (smoke test mock)
        
        Args:
            facet_key: Facet being queried
            query: Natural language query
            
        Returns:
            Simulated result dict with mock nodes
        """
        # Generate mock nodes relevant to the facet and query
        mock_nodes = []
        
        # Example: senator & mollusk query
        if 'senator' in query.lower() and facet_key == 'political':
            mock_nodes = [
                {'id': 'node_pol_1', 'label': 'Roman senator', 'facet': 'political'},
                {'id': 'node_pol_2', 'label': 'toga praetexta', 'facet': 'political'},
                {'id': 'node_pol_3', 'label': 'Tyrian purple', 'facet': 'political'}  # Bridge candidate
            ]
        elif 'mollusk' in query.lower() and facet_key == 'scientific':
            mock_nodes = [
                {'id': 'node_sci_1', 'label': 'mollusk', 'facet': 'scientific'},
                {'id': 'node_sci_2', 'label': 'murex snail', 'facet': 'scientific'},
                {'id': 'node_sci_3', 'label': 'Tyrian purple', 'facet': 'scientific'}  # Bridge candidate
            ]
        elif 'mollusk' in query.lower() and facet_key == 'cultural':
            mock_nodes = [
                {'id': 'node_cul_1', 'label': 'textile dyeing', 'facet': 'cultural'},
                {'id': 'node_cul_2', 'label': 'Tyrian purple', 'facet': 'cultural'},  # Bridge candidate
                {'id': 'node_cul_3', 'label': 'luxury goods', 'facet': 'cultural'}
            ]
        
        return {
            'status': 'SIMULATED',
            'facet': facet_key,
            'query': query,
            'nodes': mock_nodes,
            'claims': [],
            'note': 'Simulated results for smoke test validation'
        }
    
    def _synthesize_response(self, query: str, facet_results: Dict[str, Any], 
                            bridge_claims: List[Dict[str, Any]], cross_domain: bool) -> str:
        """
        Use LLM to synthesize a coherent answer from multi-facet results
        
        Args:
            query: Original query
            facet_results: Results from each facet
            bridge_claims: Bridge claims generated (node/edge creation)
            cross_domain: Whether query spans domains
            
        Returns:
            Synthesized natural language response
        """
        synthesis_prompt = """You are synthesizing results from multiple domain experts to answer a cross-domain historical query.

You will receive:
1. The original query
2. Results from multiple facet experts (each with specific domain knowledge)
3. Bridge concepts that connect the domains

Your task:
- Integrate findings from all facets into a coherent narrative
- Explain how bridge concepts connect the domains
- Cite which facet provided which information
- Be concise but comprehensive

Return a natural language answer."""
        
        # Prepare facet summaries
        facet_summaries = []
        for facet_key, result in facet_results.items():
            if isinstance(result, dict):
                node_count = len(result.get('nodes', []))
                facet_summaries.append(f"{facet_key}: {node_count} relevant concepts found")
        
        # Extract bridge labels from claims
        bridge_labels = []
        for claim in bridge_claims:
            if claim.get('claim_type') == 'NODE_CREATION':
                bridge_labels.append(claim.get('label', ''))
        bridge_text = ", ".join(bridge_labels) if bridge_labels else "None identified"
        
        context = f"""Query: {query}

Facet Results:
{chr(10).join(facet_summaries)}

Bridge Concepts: {bridge_text}

Cross-domain: {cross_domain}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": synthesis_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            return response.choices[0].message.content or ""
        
        except Exception as e:
            # Fallback to simple summary
            bridge_count = sum(1 for c in bridge_claims if c.get('claim_type') == 'NODE_CREATION')
            return f"Cross-domain query processed across {len(facet_results)} facets. Generated {len(bridge_claims)} bridge claims ({bridge_count} node creations). See facet_results for details."
    
    def close(self):
        """Close all spawned/simulated agents and driver"""
        print("\n→ Closing SubjectConceptAgent...")
        
        for facet_key, agent_stub in self.active_agents.items():
            try:
                # Simulated agents are just dicts, no close needed
                if isinstance(agent_stub, dict) and agent_stub.get('type') == 'SIMULATED':
                    print(f"  ✓ Cleared simulated {facet_key} agent")
                else:
                    # Real agent has close() method
                    agent_stub.close()
                    print(f"  ✓ Closed {facet_key} agent")
            except Exception as e:
                print(f"  ⚠ Error closing {facet_key}: {e}")
        
        self.active_agents.clear()
        self.driver.close()
        
        print("✓ SubjectConceptAgent closed")


# Test script
if __name__ == "__main__":
    print("Chrystallum Multi-Agent Facet Framework")
    print("=" * 60)
    print("\nTest Options:")
    print("1. Single Facet Agent (SFA)")
    print("2. SubjectConceptAgent (SCA) - Cross-Domain Orchestration")
    print("3. Claim Routing Demo")
    
    test_mode = input("\nSelect test mode (1/2/3): ").strip()
    
    if test_mode == "1":
        # Test single FacetAgent
        print("\n" + "="*60)
        print("TEST MODE 1: Single Facet Agent")
        print("="*60)
        
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

        print("\n→ Testing initialize mode...")
        result = agent.execute_initialize_mode(
            anchor_qid="Q47314",  # Battle of Actium
            depth=1,
            auto_submit_claims=False
        )
        
        print(f"\n✓ Initialize complete:")
        print(f"  Nodes created: {result.get('nodes_created', 0)}")
        print(f"  Claims generated: {result.get('claims_generated', 0)}")

        agent.close()
        print("\n✓ Single agent test complete")
    
    elif test_mode == "2":
        # Test SubjectConceptAgent cross-domain
        print("\n" + "="*60)
        print("TEST MODE 2: SubjectConceptAgent (Cross-Domain)")
        print("="*60)
        
        print("\n→ Initializing SubjectConceptAgent...")
        sca = SubjectConceptAgent()
        
        print("\n→ Testing cross-domain query...")
        print("   Query: 'What is the relationship between a Roman senator and a mollusk?'")
        
        result = sca.execute_cross_domain_query(
            query="What is the relationship between a Roman senator and a mollusk?"
        )
        
        print(f"\n✓ Cross-domain query complete:")
        print(f"  Facets queried: {', '.join(result['classification']['facets'])}")
        print(f"  Cross-domain: {result['classification']['cross_domain']}")
        print(f"  Bridge concepts: {len(result['bridges'])}")
        print(f"  Total nodes: {result['total_nodes']}")
        
        if result['synthesized_response']:
            print(f"\n→ Synthesized Answer:")
            print(f"  {result['synthesized_response']}")
        
        sca.close()
        print("\n✓ Cross-domain test complete")
    
    elif test_mode == "3":
        # Test claim routing
        print("\n" + "="*60)
        print("TEST MODE 3: Claim Routing")
        print("="*60)
        
        print("\n→ Initializing SubjectConceptAgent...")
        sca = SubjectConceptAgent()
        
        # Create a test claim about purple dye
        test_claim = {
            'subject': 'Roman senator',
            'predicate': 'wore garment dyed with',
            'object': 'Tyrian purple from murex mollusk',
            'label': 'Roman senators wore togas dyed with Tyrian purple extracted from murex mollusks',
            'confidence': 0.92,
            'source': 'test'
        }
        
        print("\n→ Routing claim across facets...")
        routing_result = sca.route_claim(test_claim)
        
        print(f"\n✓ Claim routing complete:")
        print(f"  Routed to: {', '.join(routing_result['routed_to'])}")
        print(f"  Cross-domain: {routing_result['cross_domain']}")
        print(f"  Reasoning: {routing_result['reasoning']}")
        
        sca.close()
        print("\n✓ Claim routing test complete")
    
    else:
        print("Invalid selection. Exiting.")
    
    print("\n" + "="*60)
    print("✓ Framework test complete")
    print("="*60)
