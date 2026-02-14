#!/usr/bin/env python3
"""
Chrystallum Claim Ingestion Pipeline

Handles complete claim lifecycle:
1. Validation
2. Cipher calculation
3. Intermediary node creation
4. Entity linking
5. Promotion workflow
6. Traceability logging

Date: February 14, 2026
"""

import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from neo4j import Driver, Session


class ClaimIngestionPipeline:
    """Ingestion pipeline for claims into Chrystallum"""

    def __init__(self, driver: Driver, database: str = "neo4j"):
        """
        Initialize pipeline with Neo4j driver
        
        Args:
            driver: Neo4j driver instance
            database: Target database name
        """
        self.driver = driver
        self.database = database

    def ingest_claim(
        self,
        entity_id: str,
        relationship_type: str,
        target_id: str,
        confidence: float,
        label: str,
        subject_qid: Optional[str] = None,
        retrieval_source: str = "agent_extraction",
        reasoning_notes: str = "",
        facet: str = "general"
    ) -> Dict[str, Any]:
        """
        Complete claim ingestion workflow
        
        Args:
            entity_id: Source entity (e.g., 'evt_battle_of_actium_q193304')
            relationship_type: Edge type (e.g., 'OCCURRED_DURING')
            target_id: Target entity (e.g., 'prd_roman_republic_q17167')
            confidence: Confidence score 0.0-1.0
            label: Human-readable claim label
            subject_qid: Optional subject Wikidata QID
            retrieval_source: Where claim came from
            reasoning_notes: Agent reasoning text
            facet: Domain facet
            
        Returns:
            {
                "status": "created" | "promoted" | "error",
                "claim_id": str,
                "cipher": str,
                "promoted": bool,
                "error": str (if error)
            }
        """
        try:
            # 1. Validate inputs
            self._validate_claim_data(
                entity_id, relationship_type, target_id, confidence, label
            )
            
            # 2. Generate identifiers
            claim_id = self._generate_claim_id(entity_id, target_id, confidence)
            cipher = self._calculate_cipher(claim_id, label, confidence)
            
            # 3. Create claim and intermediaries
            self._create_claim_node(
                claim_id=claim_id,
                cipher=cipher,
                label=label,
                confidence=confidence,
                subject_qid=subject_qid,
                facet=facet
            )
            
            # 4. Create context and analysis nodes
            retrieval_context_id = self._create_retrieval_context(
                claim_id, retrieval_source
            )
            analysis_run_id = self._create_analysis_run(
                claim_id, reasoning_notes
            )
            facet_assessment_id = self._create_facet_assessment(
                claim_id, facet
            )
            
            # 5. Link claim to entities
            self._link_claim_to_entities(
                claim_id, entity_id, relationship_type, target_id
            )
            
            # 6. Check promotion eligibility
            promoted = False
            if confidence >= 0.90:
                promoted = self._promote_claim(
                    claim_id, entity_id, relationship_type, target_id
                )
            
            return {
                "status": "promoted" if promoted else "created",
                "claim_id": claim_id,
                "cipher": cipher,
                "promoted": promoted,
                "error": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "claim_id": None,
                "cipher": None,
                "promoted": False,
                "error": str(e)
            }

    def _validate_claim_data(
        self,
        entity_id: str,
        relationship_type: str,
        target_id: str,
        confidence: float,
        label: str
    ) -> None:
        """Validate claim data before processing"""
        # Required fields
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError("entity_id must be non-empty string")
        if not relationship_type or not isinstance(relationship_type, str):
            raise ValueError("relationship_type must be non-empty string")
        if not target_id or not isinstance(target_id, str):
            raise ValueError("target_id must be non-empty string")
        if not label or not isinstance(label, str):
            raise ValueError("label must be non-empty string")
        
        # Confidence range
        if not isinstance(confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        
        # Entities must exist
        with self.driver.session(database=self.database) as session:
            source_result = session.run(
                "MATCH (n {entity_id: $id}) RETURN n LIMIT 1",
                {"id": entity_id}
            )
            if not source_result.peek():
                raise ValueError(f"Source entity not found: {entity_id}")
            
            target_result = session.run(
                "MATCH (n {entity_id: $id}) RETURN n LIMIT 1",
                {"id": target_id}
            )
            if not target_result.peek():
                raise ValueError(f"Target entity not found: {target_id}")

    def _generate_claim_id(
        self, entity_id: str, target_id: str, confidence: float
    ) -> str:
        """Generate unique, deterministic claim ID"""
        base = f"{entity_id}_{target_id}_{confidence:.2f}_{uuid.uuid4().hex[:8]}"
        return f"claim_{hashlib.md5(base.encode()).hexdigest()[:12]}"

    def _calculate_cipher(
        self, claim_id: str, label: str, confidence: float
    ) -> str:
        """Calculate SHA256 cipher for claim integrity"""
        data = f"{claim_id}|{label}|{confidence}|{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _create_claim_node(
        self,
        claim_id: str,
        cipher: str,
        label: str,
        confidence: float,
        subject_qid: Optional[str],
        facet: str
    ) -> None:
        """Create Claim node with required properties"""
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                CREATE (c:Claim {
                    claim_id: $claim_id,
                    cipher: $cipher,
                    label: $label,
                    confidence: $confidence,
                    status: 'proposed',
                    created_date: $created_date,
                    promoted: false,
                    subject_qid: $subject_qid,
                    facet: $facet
                })
                RETURN c
                """,
                {
                    "claim_id": claim_id,
                    "cipher": cipher,
                    "label": label,
                    "confidence": confidence,
                    "created_date": datetime.utcnow().isoformat(),
                    "subject_qid": subject_qid,
                    "facet": facet
                }
            )

    def _create_retrieval_context(
        self, claim_id: str, source: str
    ) -> str:
        """Create RetrievalContext node and link to claim"""
        context_id = f"rc_{claim_id[:8]}"
        
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                CREATE (rc:RetrievalContext {
                    context_id: $context_id,
                    source: $source,
                    retrieved_date: $retrieved_date
                })
                CREATE (c)-[:USED_CONTEXT]->(rc)
                RETURN rc
                """,
                {
                    "claim_id": claim_id,
                    "context_id": context_id,
                    "source": source,
                    "retrieved_date": datetime.utcnow().isoformat()
                }
            )
        
        return context_id

    def _create_analysis_run(self, claim_id: str, reasoning: str) -> str:
        """Create AnalysisRun node and link to claim"""
        analysis_id = f"ar_{claim_id[:8]}"
        
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                CREATE (ar:AnalysisRun {
                    analysis_id: $analysis_id,
                    reasoning: $reasoning,
                    run_date: $run_date,
                    status: 'complete'
                })
                CREATE (c)-[:HAS_ANALYSIS_RUN]->(ar)
                RETURN ar
                """,
                {
                    "claim_id": claim_id,
                    "analysis_id": analysis_id,
                    "reasoning": reasoning,
                    "run_date": datetime.utcnow().isoformat()
                }
            )
        
        return analysis_id

    def _create_facet_assessment(self, claim_id: str, facet: str) -> str:
        """Create FacetAssessment node and link to claim"""
        assessment_id = f"fa_{claim_id[:8]}"
        
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                CREATE (fa:FacetAssessment {
                    assessment_id: $assessment_id,
                    facet: $facet,
                    assessment_date: $assessment_date,
                    status: 'evaluated'
                })
                CREATE (c)-[:HAS_FACET_ASSESSMENT]->(fa)
                RETURN fa
                """,
                {
                    "claim_id": claim_id,
                    "assessment_id": assessment_id,
                    "facet": facet,
                    "assessment_date": datetime.utcnow().isoformat()
                }
            )
        
        return assessment_id

    def _link_claim_to_entities(
        self,
        claim_id: str,
        entity_id: str,
        relationship_type: str,
        target_id: str
    ) -> None:
        """Link claim to source and target entities"""
        with self.driver.session(database=self.database) as session:
            # Link to source entity
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                MATCH (source {entity_id: $source_id})
                MERGE (c)-[:ASSERTS]->(source)
                """,
                {"claim_id": claim_id, "source_id": entity_id}
            )
            
            # Link to target entity
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                MATCH (target {entity_id: $target_id})
                MERGE (c)-[:ASSERTS]->(target)
                """,
                {"claim_id": claim_id, "target_id": target_id}
            )

    def _promote_claim(
        self,
        claim_id: str,
        entity_id: str,
        relationship_type: str,
        target_id: str
    ) -> bool:
        """
        Promote validated claim to canonical state
        
        Returns: True if promoted, False otherwise
        """
        try:
            with self.driver.session(database=self.database) as session:
                # 1. Update claim status
                session.run(
                    """
                    MATCH (c:Claim {claim_id: $claim_id})
                    SET c.status = 'validated',
                        c.promotion_date = $promotion_date,
                        c.promoted = true
                    """,
                    {
                        "claim_id": claim_id,
                        "promotion_date": datetime.utcnow().isoformat()
                    }
                )
                
                # 2. Create or merge canonical relationship
                session.run(
                    f"""
                    MATCH (source {{entity_id: $source_id}})
                    MATCH (target {{entity_id: $target_id}})
                    MERGE (source)-[r:{relationship_type}]->(target)
                    SET r.promoted_from_claim_id = $claim_id,
                        r.promotion_date = $promotion_date,
                        r.promotion_status = 'canonical'
                    """,
                    {
                        "source_id": entity_id,
                        "target_id": target_id,
                        "claim_id": claim_id,
                        "promotion_date": datetime.utcnow().isoformat()
                    }
                )
                
                # 3. Create SUPPORTED_BY traceability
                session.run(
                    """
                    MATCH (source {entity_id: $source_id})
                    MATCH (c:Claim {claim_id: $claim_id})
                    MERGE (source)-[sb:SUPPORTED_BY]->(c)
                    SET sb.claim_id = $claim_id,
                        sb.promotion_date = $promotion_date
                    """,
                    {
                        "source_id": entity_id,
                        "claim_id": claim_id,
                        "promotion_date": datetime.utcnow().isoformat()
                    }
                )
                
                session.run(
                    """
                    MATCH (target {entity_id: $target_id})
                    MATCH (c:Claim {claim_id: $claim_id})
                    MERGE (target)-[sb:SUPPORTED_BY]->(c)
                    SET sb.claim_id = $claim_id,
                        sb.promotion_date = $promotion_date
                    """,
                    {
                        "target_id": target_id,
                        "claim_id": claim_id,
                        "promotion_date": datetime.utcnow().isoformat()
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"Promotion failed for {claim_id}: {str(e)}")
            return False
