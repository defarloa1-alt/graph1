"""
Claim Registry - Multi-Agent Entity Deduplication and Claim Submission

This service implements the "Claim Registry" control shell from ADR 022.
It prevents entity fragmentation by checking for existing canonical entities
before allowing writes, and manages claim metadata.

Usage:
    from scripts.agents.claim_registry import ClaimRegistry
    
    registry = ClaimRegistry(neo4j_driver)
    
    # Submit a claim (handles deduplication)
    claim_id = registry.submit_claim(
        entity={'type': 'EVENT', 'qid': 'Q40979', 'label': 'Caesar crossing Rubicon'},
        predicate='military_escalation',
        facet='MILITARY',
        agent_id='military_sfa_001',
        confidence=0.90
    )
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from neo4j import GraphDatabase, Driver
import logging

from scripts.tools.entity_cipher import generate_entity_cipher
from scripts.tools.sys_registry import validate_relationship_type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaimRegistry:
    """
    Claim Registry - prevents entity fragmentation, manages claim lifecycle.
    
    Core functions:
    1. Entity deduplication via cipher lookups
    2. Canonical entity creation/retrieval
    3. Claim submission with full provenance
    4. Status management (TBD → PROPOSED → CONFIRMED → CONTESTED)
    """
    
    def __init__(self, neo4j_driver: Driver):
        """
        Initialize Claim Registry.
        
        Args:
            neo4j_driver: Neo4j driver instance
        """
        self.driver = neo4j_driver
    
    def check_entity_exists(
        self, 
        entity_cipher: str, 
        qid: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Check if canonical entity already exists in graph.
        
        Lookup priority:
        1. entity_cipher (guaranteed unique via constraint)
        2. qid (if provided)
        
        Args:
            entity_cipher: Tier 1 entity cipher
            qid: Wikidata QID (optional fallback)
        
        Returns:
            Entity node properties if found, None otherwise
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)
                WHERE e.entity_cipher = $cipher
                   OR (e.qid IS NOT NULL AND e.qid = $qid)
                RETURN e
                LIMIT 1
            """, cipher=entity_cipher, qid=qid)
            
            record = result.single()
            if record:
                node = record['e']
                return dict(node)
            return None
    
    def create_canonical_entity(
        self,
        entity: Dict,
        entity_cipher: str
    ) -> str:
        """
        Create canonical entity node in graph.
        
        Args:
            entity: Entity data dict (type, qid, label, etc.)
            entity_cipher: Tier 1 entity cipher
        
        Returns:
            Entity cipher of created node
        """
        with self.driver.session() as session:
            # Extract entity properties
            entity_type = entity.get('type', 'CONCEPT').upper()
            qid = entity.get('qid')
            label = entity.get('label', 'Unknown')
            description = entity.get('description')
            
            # Build property dict
            props = {
                'entity_cipher': entity_cipher,
                'entity_type': entity_type,
                'label': label,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            if qid:
                props['qid'] = qid
            if description:
                props['description'] = description
            
            # Add type-specific properties
            for key, value in entity.items():
                if key not in ['type', 'qid', 'label', 'description', 'canonical_properties']:
                    props[key] = value
            
            # Create node with appropriate label based on type
            session.run(f"""
                CREATE (e:{entity_type} $props)
            """, props=props)
            
            logger.info(f"Created canonical entity: {entity_cipher} ({label})")
            return entity_cipher
    
    def submit_claim(
        self,
        entity: Dict,
        predicate: str,
        facet: str,
        agent_id: str,
        confidence: float,
        source_qid: Optional[str] = None,
        source_uri: Optional[str] = None,
        passage_locator: Optional[str] = None,
        passage_text_hash: Optional[str] = None,
        igar_chain: Optional[Dict] = None,
        relationship_type: Optional[str] = None,
        **kwargs  # Additional metadata (e.g., source_tier, anachronism_risk)
    ) -> str:
        """
        Submit a claim about an entity.
        
        Process:
        1. Generate entity cipher
        2. Check if canonical entity exists (deduplication)
        3. Create entity if new, or get existing
        4. Create :ASSERTS edge with full metadata
        5. Return claim_id
        
        Args:
            entity: Entity dict with type, qid/canonical_properties, label
            predicate: Semantic interpretation (e.g., 'military_escalation')
            facet: Facet ID (one of 18 canonical facets)
            agent_id: Unique agent identifier
            confidence: Confidence score [0.0-1.0]
            source_qid: Wikidata QID of source work (IGAR requirement)
            source_uri: External source URI
            passage_locator: Specific passage reference (IGAR requirement)
            passage_text_hash: Hash of passage text
            igar_chain: IGAR chain dict (for actor-centric events)
            relationship_type: Canonical relationship type
            **kwargs: Additional claim metadata (e.g., source_tier, anachronism_risk, predicate_category)
        
        Returns:
            Claim ID (entity_cipher for now, will be claim cipher in Phase 3)
        
        Raises:
            ValueError: If required fields missing or invalid
        """
        # Validate inputs
        if confidence < 0.0 or confidence > 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        
        facet_upper = facet.upper()
        if facet_upper not in self._get_canonical_facets():
            raise ValueError(f"Unknown facet: {facet}. Valid: {self._get_canonical_facets()}")

        # Registry gate (FACET_TRAINING_CONTRACT): relationship_type is mandatory law.
        # `predicate` may be a facet gloss; if relationship_type omitted, predicate is
        # treated as the candidate type (must be UPPER registry form).
        candidate_type = relationship_type or predicate
        registry_check = validate_relationship_type(candidate_type)
        if not registry_check.valid:
            raise ValueError(
                f"Unregistered relationship type: {candidate_type}. "
                f"{registry_check.message}. "
                "Add to relationship_types_registry_master.csv as candidate first."
            )
        relationship_type = registry_check.normalized
        # Keep predicate as gloss if it differs; otherwise align to registry type
        if predicate and predicate.upper().replace(" ", "_") != relationship_type:
            kwargs.setdefault("predicate_gloss", predicate)
            predicate = relationship_type
        else:
            predicate = relationship_type
        kwargs["registry_status"] = registry_check.registry_status
        kwargs["registry_validated"] = True
        
        # Generate entity cipher
        entity_cipher = self._generate_cipher_for_entity(entity)
        
        # Check for existing canonical entity
        existing = self.check_entity_exists(entity_cipher, entity.get('qid'))
        
        if existing:
            # Use the EXISTING entity's cipher, not the generated one
            entity_cipher = existing['entity_cipher']
            logger.info(f"Found existing entity: {entity_cipher}")
        else:
            # Create canonical entity
            entity_cipher = self.create_canonical_entity(entity, entity_cipher)
        
        # Create or retrieve agent node
        self._ensure_agent_exists(agent_id, facet_upper)
        
        # Create :ASSERTS claim (pass through all additional kwargs)
        claim_id = self._create_claim(
            entity_cipher=entity_cipher,
            agent_id=agent_id,
            facet=facet_upper,
            predicate=predicate,
            confidence=confidence,
            source_qid=source_qid,
            source_uri=source_uri,
            passage_locator=passage_locator,
            passage_text_hash=passage_text_hash,
            igar_chain=igar_chain,
            relationship_type=relationship_type,
            **kwargs  # Pass through additional metadata
        )
        
        return claim_id
    
    def get_claims_for_entity(
        self,
        entity_cipher: str,
        facet: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve all claims for an entity across facets.
        
        Args:
            entity_cipher: Entity cipher
            facet: Filter by specific facet (optional)
            status: Filter by claim status (optional)
        
        Returns:
            List of claim dicts with provenance
        """
        with self.driver.session() as session:
            query = """
                MATCH (e {entity_cipher: $cipher})<-[c:ASSERTS]-(a:Agent)
                WHERE ($facet IS NULL OR c.facet = $facet)
                  AND ($status IS NULL OR c.status = $status)
                RETURN 
                    c.facet as facet,
                    a.agent_id as agent_id,
                    c.predicate as predicate,
                    c.confidence as confidence,
                    c.status as status,
                    c.submitted_at as submitted_at,
                    c.source_qid as source_qid,
                    c.igar_chain as igar_chain
                ORDER BY c.submitted_at DESC
            """
            
            result = session.run(query, 
                cipher=entity_cipher,
                facet=facet,
                status=status
            )
            
            return [dict(record) for record in result]
    
    def update_claim_status(
        self,
        entity_cipher: str,
        agent_id: str,
        new_status: str
    ) -> bool:
        """
        Update claim status (TBD → PROPOSED → CONFIRMED/CONTESTED).
        
        Args:
            entity_cipher: Entity cipher
            agent_id: Agent who made the claim
            new_status: New status (PROPOSED, CONFIRMED, CONTESTED, DEPRECATED)
        
        Returns:
            True if updated, False if claim not found
        """
        valid_statuses = ['TBD', 'PROPOSED', 'CONFIRMED', 'CONTESTED', 'DEPRECATED']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}. Valid: {valid_statuses}")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e {entity_cipher: $cipher})<-[c:ASSERTS]-(a:Agent {agent_id: $agent_id})
                SET c.status = $status,
                    c.reviewed_at = datetime()
                RETURN c
            """, cipher=entity_cipher, agent_id=agent_id, status=new_status)
            
            return result.single() is not None
    
    # ─────────────────────────────────────────────────────
    # Private Helper Methods
    # ─────────────────────────────────────────────────────
    
    def _generate_cipher_for_entity(self, entity: Dict) -> str:
        """Generate entity cipher from entity dict."""
        entity_type = entity.get('type', 'CONCEPT').upper()
        qid = entity.get('qid')
        canonical_properties = entity.get('canonical_properties')
        
        return generate_entity_cipher(
            entity_type=entity_type,
            qid=qid,
            canonical_properties=canonical_properties
        )
    
    def _ensure_agent_exists(self, agent_id: str, facet: str):
        """Create agent node if it doesn't exist."""
        with self.driver.session() as session:
            session.run("""
                MERGE (a:Agent {agent_id: $agent_id})
                ON CREATE SET 
                    a.facet = $facet,
                    a.created_at = datetime()
            """, agent_id=agent_id, facet=facet)
    
    def _create_claim(
        self,
        entity_cipher: str,
        agent_id: str,
        facet: str,
        predicate: str,
        confidence: float,
        source_qid: Optional[str],
        source_uri: Optional[str],
        passage_locator: Optional[str],
        passage_text_hash: Optional[str],
        igar_chain: Optional[Dict],
        relationship_type: Optional[str],
        **kwargs  # Additional metadata
    ) -> str:
        """Create :ASSERTS claim relationship with full metadata."""
        with self.driver.session() as session:
            # Build claim properties
            props = {
                'facet': facet,
                'predicate': predicate,
                'confidence': confidence,
                'status': 'TBD',  # Default status
                'submitted_at': datetime.now(timezone.utc).isoformat(),
                'review_count': 0,
                'agreement_score': 0.0
            }

            if source_qid:
                props['source_qid'] = source_qid
            if source_uri:
                props['source_uri'] = source_uri
            if passage_locator:
                props['passage_locator'] = passage_locator
            if passage_text_hash:
                props['passage_text_hash'] = passage_text_hash
            if igar_chain:
                props['igar_chain'] = str(igar_chain)  # Serialize to string for Neo4j
            if relationship_type:
                props['relationship_type'] = relationship_type
            
            # Add all additional kwargs to props (e.g., source_tier, anachronism_risk, etc.)
            for key, value in kwargs.items():
                if value is not None:
                    props[key] = value
            
            # Create claim edge
            session.run("""
                MATCH (e {entity_cipher: $cipher})
                MATCH (a:Agent {agent_id: $agent_id})
                CREATE (a)-[c:ASSERTS $props]->(e)
            """, cipher=entity_cipher, agent_id=agent_id, props=props)
            
            logger.info(f"Created claim: {facet} agent asserts {predicate} about {entity_cipher}")
            
            # Return claim_id (for now, entity_cipher; will be proper claim cipher in Phase 3)
            return f"{agent_id}_{entity_cipher}_{facet}"
    
    def _get_canonical_facets(self) -> List[str]:
        """Get list of canonical facets."""
        return [
            'ARCHAEOLOGICAL', 'ARTISTIC', 'BIOGRAPHIC', 'COMMUNICATION',
            'CULTURAL', 'DEMOGRAPHIC', 'DIPLOMATIC', 'ECONOMIC',
            'ENVIRONMENTAL', 'GEOGRAPHIC', 'INTELLECTUAL', 'LINGUISTIC',
            'MILITARY', 'POLITICAL', 'RELIGIOUS', 'SCIENTIFIC',
            'SOCIAL', 'TECHNOLOGICAL'
        ]


# ─────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────

def create_claim_registry(neo4j_uri: str, neo4j_user: str, neo4j_password: str) -> ClaimRegistry:
    """
    Create ClaimRegistry instance with Neo4j connection.
    
    Args:
        neo4j_uri: Neo4j connection URI
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
    
    Returns:
        ClaimRegistry instance
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    return ClaimRegistry(driver)


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Create registry
    registry = create_claim_registry(
        neo4j_uri=os.getenv('NEO4J_URI'),
        neo4j_user=os.getenv('NEO4J_USERNAME'),
        neo4j_password=os.getenv('NEO4J_PASSWORD')
    )
    
    # Example: Military SFA submits claim about Caesar crossing Rubicon
    entity = {
        'type': 'EVENT',
        'qid': 'Q40979',
        'label': 'Caesar crossing the Rubicon',
        'date': '-49-01-10',
        'location': 'Rubicon River'
    }
    
    claim_id = registry.submit_claim(
        entity=entity,
        predicate='military_escalation',
        facet='MILITARY',
        agent_id='military_sfa_001',
        confidence=0.90,
        source_qid='Q123456',
        igar_chain={
            'input': 'Legion stationed in Gaul',
            'goal': 'Maintain command',
            'action': 'Cross Rubicon with troops',
            'result': 'Declaration of war'
        }
    )
    
    print(f"Created claim: {claim_id}")
    
    # Example: Bio SFA submits claim about SAME event
    claim_id_2 = registry.submit_claim(
        entity=entity,  # Same entity!
        predicate='career_defining_act',
        facet='BIOGRAPHIC',
        agent_id='bio_sfa_001',
        confidence=0.95,
        source_qid='Q789012',
        igar_chain={
            'input': 'Senate refuses demands',
            'goal': 'Maintain dignitas',
            'action': 'Cross Rubicon',
            'result': 'Point of no return'
        }
    )
    
    print(f"Created claim: {claim_id_2}")
    print("\nResult: 1 canonical entity, 2 facet-specific claims ✓")
