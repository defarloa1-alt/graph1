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
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from neo4j import Driver, Session
try:
    from historian_logic_engine import HistorianLogicEngine
except ModuleNotFoundError:  # pragma: no cover
    from .historian_logic_engine import HistorianLogicEngine


class ClaimIngestionPipeline:
    """Ingestion pipeline for claims into Chrystallum"""

    # =========================================================================
    # FALLACY FLAGGING: Categorize fallacies for downstream consumption
    # =========================================================================
    # All fallacies are detected and flagged. Promotion is based purely on
    # confidence + posterior probability metrics. Fallacy categorization helps
    # downstream systems (human reviewers, other agents) prioritize review.
    # =========================================================================
    
    # Interpretive claim types: fallacies warrant closer review upstream
    INTERPRETIVE_CLAIM_TYPES = {
        "causal",           # Claims about causation/causality
        "interpretive",     # Claims about meaning/interpretation
        "motivational",     # Claims about motivations/intents
        "narrative"         # Claims about narratives/framing
    }
    
    # Interpretive facets: fallacies warrant closer review upstream
    INTERPRETIVE_FACETS = {
        "political",       # Political analysis/commentary
        "diplomatic",      # Diplomatic interpretation
        "religious",       # Religious interpretation
        "social",          # Social interpretation
        "communication",   # Communication/messaging
        "intellectual",    # Intellectual movements
        "military",        # Military strategy/motivation
        "cultural",        # Cultural interpretation
        "economic"         # Economic analysis
    }
    
    # Descriptive claim types: fallacies are lower risk
    DESCRIPTIVE_CLAIM_TYPES = {
        "temporal",        # When something happened
        "locational",      # Where something happened
        "taxonomic",       # Classification
        "identity"         # Identity/naming
    }
    
    # Descriptive facets: fallacies are lower risk
    DESCRIPTIVE_FACETS = {
        "geographic",      # Geographic/location facts
        "environmental",   # Environmental facts
        "archaeological",  # Archaeological data
        "scientific",      # Scientific facts
        "technological",   # Technological facts
        "demographic",     # Demographic data
        "linguistic",      # Linguistic facts
        "artistic"         # Artistic facts
    }

    def __init__(self, driver: Driver, database: str = "neo4j"):
        """
        Initialize pipeline with Neo4j driver
        
        Args:
            driver: Neo4j driver instance
            database: Target database name
        """
        self.driver = driver
        self.database = database
        self.reasoning_engine = HistorianLogicEngine()

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
        facet: Optional[str] = None,
        claim_signature: Optional[Any] = None,
        authority_source: Optional[str] = None,
        authority_ids: Optional[Any] = None,
        claim_type: str = "relational",
        source_agent: str = "agent_claim_ingestion_pipeline"
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
            facet: Domain facet (lowercase registry key)
            claim_signature: Deterministic signature (QID + full statement signature)
            authority_source: Authority system name (e.g., wikidata, lcsh)
            authority_ids: Authority identifiers map or list
            claim_type: Claim type label (e.g., relational, factual, temporal)
            source_agent: Agent identifier used for claim provenance
            
        Returns:
            {
                "status": "created" | "promoted" | "error",
                "claim_id": str,
                "cipher": str,
                "promoted": bool,
                "posterior_probability": float,
                "fallacies_detected": list[str],
                "critical_fallacy": bool,
                "error": str (if error)
            }
        """
        try:
            facet = facet.strip().lower() if facet else ""
            claim_type = claim_type.strip().lower() if claim_type else "relational"
            source_agent = source_agent.strip() if source_agent else "agent_claim_ingestion_pipeline"
            if not facet:
                raise ValueError("facet is required (lowercase registry key)")
            if not subject_qid:
                raise ValueError("subject_qid is required for claim_id signature")
            if claim_signature is None:
                raise ValueError("claim_signature is required for deterministic claim_id")
            signature_text = self._normalize_claim_signature(claim_signature, subject_qid)
            authority_source = authority_source.strip() if authority_source else ""
            authority_ids = self._normalize_authority_ids(authority_ids)
            # 1. Validate inputs
            self._validate_claim_data(
                entity_id, relationship_type, target_id, confidence, label
            )
            
            # 2. Generate identifiers
            claim_id = self._generate_claim_id(subject_qid, signature_text)
            cipher = self._calculate_cipher(claim_id, label, confidence, source_agent)
            reasoning_eval = self.reasoning_engine.evaluate(label, reasoning_notes, confidence)
            
            # 3. Create claim and intermediaries
            self._create_claim_node(
                claim_id=claim_id,
                cipher=cipher,
                label=label,
                text=label,
                claim_type=claim_type,
                source_agent=source_agent,
                confidence=confidence,
                subject_qid=subject_qid,
                facet=facet,
                reasoning_eval=reasoning_eval,
                authority_source=authority_source,
                authority_ids=authority_ids
            )
            
            # 4. Create context and analysis nodes
            retrieval_context_id = self._create_retrieval_context(
                claim_id, retrieval_source, source_agent, authority_source, authority_ids
            )
            analysis_run_id = self._create_analysis_run(
                claim_id, reasoning_notes
            )
            facet_assessment_id = self._create_facet_assessment(
                claim_id, facet, reasoning_eval["posterior_probability"]
            )
            
            # 5. Link claim to entities
            self._link_claim_to_entities(
                claim_id, entity_id, relationship_type, target_id
            )
            
            # 6. Check promotion eligibility
            # Promotion is based purely on scientific metrics: confidence + posterior
            # Fallacies are always detected and flagged but never block promotion
            promoted = False
            if (
                confidence >= 0.90
                and reasoning_eval["posterior_probability"] >= 0.90
            ):
                promoted = self._promote_claim(
                    claim_id, entity_id, relationship_type, target_id
                )
            
            # Determine fallacy flag intensity for downstream consumption
            fallacy_flag_intensity = self._determine_fallacy_flag_intensity(
                reasoning_eval["critical_fallacy"], claim_type, facet
            )
            
            return {
                "status": "promoted" if promoted else "created",
                "claim_id": claim_id,
                "cipher": cipher,
                "promoted": promoted,
                "fallacy_flag_intensity": fallacy_flag_intensity,
                "posterior_probability": reasoning_eval["posterior_probability"],
                "fallacies_detected": reasoning_eval["fallacies_detected"],
                "critical_fallacy": reasoning_eval["critical_fallacy"],
                "error": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "claim_id": None,
                "cipher": None,
                "promoted": False,
                "posterior_probability": None,
                "fallacies_detected": [],
                "critical_fallacy": None,
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
        if not re.match(r"^[A-Z][A-Z0-9_]*$", relationship_type):
            raise ValueError("relationship_type must use uppercase Cypher relationship token format")
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

    def _determine_fallacy_flag_intensity(self, critical_fallacy: bool, claim_type: str, facet: str) -> str:
        """
        Determine fallacy flag intensity for downstream consumption.
        
        Args:
            critical_fallacy: Whether a critical fallacy was detected
            claim_type: Claim type (e.g., 'causal', 'temporal', 'narrative')
            facet: Domain facet (e.g., 'political', 'geographic')
            
        Returns:
            'none': No fallacies detected
            'low': Fallacies detected in descriptive claims (lower concern)
            'high': Fallacies detected in interpretive claims (warrant review)
        
        RATIONALE:
        - All fallacies are always flagged and returned in response
        - Flag intensity helps downstream systems prioritize human review
        - Promotion decisions are based purely on confidence + posterior metrics
        """
        if not critical_fallacy:
            return "none"
        
        is_interpretive_type = claim_type.lower() in self.INTERPRETIVE_CLAIM_TYPES
        is_interpretive_facet = facet.lower() in self.INTERPRETIVE_FACETS
        
        # High intensity if interpretive claim type or facet
        if is_interpretive_type or is_interpretive_facet:
            return "high"
        
        # Low intensity for descriptive profiles
        return "low"

    def _normalize_claim_signature(self, claim_signature: Any, subject_qid: str) -> str:
        """Normalize claim signature to a stable string"""
        if isinstance(claim_signature, str):
            normalized = claim_signature.strip()
            if not normalized:
                raise ValueError("claim_signature cannot be empty")
            raise ValueError("claim_signature must be a structured object, not a string")
        if not isinstance(claim_signature, dict):
            raise ValueError("claim_signature must be a dict with qid, pvalues, and values")

        qid = claim_signature.get("qid")
        pvalues = claim_signature.get("pvalues")
        values = claim_signature.get("values")

        if not qid or not isinstance(qid, str):
            raise ValueError("claim_signature.qid must be a non-empty string")
        if qid != subject_qid:
            raise ValueError("claim_signature.qid must match subject_qid")
        if not isinstance(pvalues, list) or not pvalues:
            raise ValueError("claim_signature.pvalues must be a non-empty list")
        if not all(isinstance(p, str) and p.startswith("P") for p in pvalues):
            raise ValueError("claim_signature.pvalues must contain P-IDs")
        if not isinstance(values, dict) or not values:
            raise ValueError("claim_signature.values must be a non-empty dict")
        if not all(isinstance(k, str) and k.startswith("P") for k in values.keys()):
            raise ValueError("claim_signature.values keys must be P-IDs")

        normalized_pvalues = sorted(set(pvalues))
        missing_keys = [k for k in normalized_pvalues if k not in values]
        if missing_keys:
            raise ValueError(f"claim_signature.values missing keys: {missing_keys}")

        normalized_values = {key: self._normalize_signature_value(values[key]) for key in normalized_pvalues}
        normalized = {
            "qid": qid,
            "pvalues": normalized_pvalues,
            "values": normalized_values
        }
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"))

    def _normalize_signature_value(self, value: Any) -> Any:
        """Normalize signature values for deterministic hashing"""
        if isinstance(value, dict):
            return {key: self._normalize_signature_value(value[key]) for key in sorted(value.keys())}
        if isinstance(value, list):
            normalized_list = [self._normalize_signature_value(item) for item in value]
            try:
                return sorted(normalized_list)
            except TypeError:
                return sorted(normalized_list, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
        return value

    def _normalize_authority_ids(self, authority_ids: Optional[Any]) -> Optional[Any]:
        """Normalize authority identifiers for storage"""
        if authority_ids is None:
            return None
        if isinstance(authority_ids, str):
            value = authority_ids.strip()
            if not value:
                return None
            return {"value": value}
        if isinstance(authority_ids, (dict, list)):
            return authority_ids
        raise ValueError("authority_ids must be a string, dict, list, or None")

    def _generate_claim_id(self, subject_qid: str, signature_text: str) -> str:
        """Generate deterministic claim ID from QID + full statement signature"""
        base = f"{subject_qid}|{signature_text}"
        return f"claim_{hashlib.sha256(base.encode()).hexdigest()[:12]}"

    def _calculate_cipher(
        self, claim_id: str, label: str, confidence: float, source_agent: str
    ) -> str:
        """Calculate SHA256 cipher for claim integrity"""
        data = f"{claim_id}|{label}|{confidence}|{source_agent}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _create_claim_node(
        self,
        claim_id: str,
        cipher: str,
        label: str,
        text: str,
        claim_type: str,
        source_agent: str,
        confidence: float,
        subject_qid: Optional[str],
        facet: str,
        reasoning_eval: Dict[str, Any],
        authority_source: str,
        authority_ids: Optional[Any]
    ) -> None:
        """Create Claim node with required properties"""
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                CREATE (c:Claim {
                    claim_id: $claim_id,
                    cipher: $cipher,
                    label: $label,
                    text: $text,
                    claim_type: $claim_type,
                    source_agent: $source_agent,
                    timestamp: $timestamp,
                    confidence: $confidence,
                    status: 'proposed',
                    promoted: false,
                    subject_qid: $subject_qid,
                    facet: $facet,
                    authority_source: $authority_source,
                    authority_ids: $authority_ids,
                    prior_probability: $prior_probability,
                    likelihood: $likelihood,
                    posterior_probability: $posterior_probability,
                    bayesian_score: $posterior_probability,
                    evidence_score: $evidence_score,
                    fallacies_detected: $fallacies_detected,
                    fallacy_penalty: $fallacy_penalty,
                    critical_fallacy: $critical_fallacy
                })
                RETURN c
                """,
                {
                    "claim_id": claim_id,
                    "cipher": cipher,
                    "label": label,
                    "text": text,
                    "claim_type": claim_type,
                    "source_agent": source_agent,
                    "timestamp": datetime.utcnow().isoformat(),
                    "confidence": confidence,
                    "subject_qid": subject_qid,
                    "facet": facet,
                    "authority_source": authority_source or None,
                    "authority_ids": authority_ids,
                    "prior_probability": reasoning_eval["prior_probability"],
                    "likelihood": reasoning_eval["likelihood"],
                    "posterior_probability": reasoning_eval["posterior_probability"],
                    "evidence_score": reasoning_eval["evidence_score"],
                    "fallacies_detected": reasoning_eval["fallacies_detected"],
                    "fallacy_penalty": reasoning_eval["fallacy_penalty"],
                    "critical_fallacy": reasoning_eval["critical_fallacy"],
                }
            )

    def _create_retrieval_context(
        self, claim_id: str, source: str, agent_id: str, authority_source: str, authority_ids: Optional[Any]
    ) -> str:
        """Create RetrievalContext node and link to claim"""
        retrieval_id = f"retr_{claim_id[:8]}"
        
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                CREATE (rc:RetrievalContext {
                    retrieval_id: $retrieval_id,
                    agent_id: $agent_id,
                    source: $source,
                    authority_source: $authority_source,
                    authority_ids: $authority_ids,
                    timestamp: $timestamp
                })
                CREATE (c)-[:USED_CONTEXT]->(rc)
                RETURN rc
                """,
                {
                    "claim_id": claim_id,
                    "retrieval_id": retrieval_id,
                    "agent_id": agent_id,
                    "source": source,
                    "authority_source": authority_source or None,
                    "authority_ids": authority_ids,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return retrieval_id

    def _create_analysis_run(self, claim_id: str, reasoning: str) -> str:
        """Create AnalysisRun node and link to claim"""
        run_id = f"run_{claim_id[:8]}"
        
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                CREATE (ar:AnalysisRun {
                    run_id: $run_id,
                    pipeline_version: 'claim_ingestion_pipeline_v1',
                    reasoning: $reasoning,
                    run_date: $run_date,
                    status: 'complete'
                })
                CREATE (c)-[:HAS_ANALYSIS_RUN]->(ar)
                RETURN ar
                """,
                {
                    "claim_id": claim_id,
                    "run_id": run_id,
                    "reasoning": reasoning,
                    "run_date": datetime.utcnow().isoformat()
                }
            )
        
        return run_id

    def _create_facet_assessment(self, claim_id: str, facet: str, score: float) -> str:
        """Create FacetAssessment node and link to claim"""
        assessment_id = f"fa_{claim_id[:8]}"
        
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                CREATE (fa:FacetAssessment {
                    assessment_id: $assessment_id,
                    facet: $facet,
                    score: $score,
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
                    "score": score,
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
