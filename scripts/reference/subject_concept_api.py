#!/usr/bin/env python3
"""
SUBJECT CONCEPT API
===================

Provides programmatic interface for agents to create and manage SubjectConcepts.

Usage (from within an agent):
    from subject_concept_api import SubjectConceptAPI
    
    api = SubjectConceptAPI(uri, username, password)
    
    concept = api.claim_new_concept(
        label="Caesar's Gallic Wars",
        parent_id="subj_roman_republic_q17167",
        wikidata_qid="Q181098",
        confidence=0.92,
        evidence="Caesar's Commentarii de Bello Gallico"
    )
    
    # Create facet claims for this concept
    claim = api.create_facet_claim(
        concept_id=concept["concept_id"],
        text="Caesar used legionary tactics for conquest",
        primary_facet="Military",
        related_facets=["Political", "Technological"],
        confidence=0.95,
        evidence="Caesar's Commentarii"
    )

"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid
import warnings

from neo4j import GraphDatabase


class ValidationError(Exception):
    """Raised when concept creation violates validation rules"""
    pass


class SubjectConceptAPI:
    """Agent interface to SubjectConcept registry"""
    
    VALIDATION_THRESHOLD = 0.75       # Minimum confidence to create concept
    AUTO_APPROVAL_THRESHOLD = 0.90    # Auto-approve if confidence >= this
    FACETS = [
        "Military", "Political", "Social", "Economic", 
        "Diplomatic", "Religious", "Legal", "Literary",
        "Cultural", "Technological", "Artistic", "Philosophical",
        "Scientific", "Geographic", "Biographical", "Demographic",
        "Architectural", "Communication"  # 17 + 1 meta-facet
    ]
    
    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.batch_mode = False
        self.pending_creates = []
    
    def close(self):
        """Close driver"""
        self.driver.close()
    
    def concept_exists(self, label: str, parent_id: str = None) -> Optional[Dict]:
        """
        Check if concept already exists in registry.
        
        Returns:
            Concept dict if exists, None otherwise
        """
        cypher = """
        MATCH (subj:SubjectConcept {label: $label})
        WHERE ($parent_id IS NULL OR subj.parent_concept_id = $parent_id)
        RETURN {
            concept_id: subj.concept_id,
            label: subj.label,
            wikidata_qid: subj.wikidata_qid,
            confidence: subj.confidence,
            validation_status: subj.validation_status
        } AS concept
        """
        
        with self.driver.session() as session:
            result = session.run(cypher, label=label, parent_id=parent_id).single()
            return result["concept"] if result else None
    
    def claim_new_concept(self,
                         label: str,
                         parent_id: str = None,
                         wikidata_qid: str = None,
                         confidence: float = None,
                         evidence: str = None,
                         description: str = None,
                         period_start: int = None,
                         period_end: int = None,
                         agent_name: str = "GPT_PHASE_2A+2B") -> Dict:
        """
        Agent claims a new, more granular SubjectConcept.
        
        Args:
            label: Concept name (e.g., "Caesar's Gallic Wars")
            parent_id: Parent concept ID for hierarchy (optional)
            wikidata_qid: Wikidata Q-identifier (optional)
            confidence: Agent's confidence (0.0-1.0). Must be >= 0.75
            evidence: Justification for creating concept
            description: Detailed description
            period_start: Start year (BCE negated, CE positive)
            period_end: End year
            agent_name: Which agent is creating this? (for audit trail)
        
        Returns:
            Created SubjectConcept dict
        
        Raises:
            ValidationError: If confidence < 0.75 or concept exists
        """
        
        # Validation: Confidence threshold
        if confidence is not None and confidence < self.VALIDATION_THRESHOLD:
            raise ValidationError(
                f"Confidence {confidence} below minimum {self.VALIDATION_THRESHOLD}"
            )
        
        # Validation: Concept doesn't already exist
        existing = self.concept_exists(label, parent_id)
        if existing:
            warnings.warn(f"Concept '{label}' already exists (ID: {existing['concept_id']})")
            return existing
        
        # Validation: Parent exists if specified
        if parent_id:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (p:SubjectConcept {concept_id: $parent_id}) RETURN p.concept_id",
                    parent_id=parent_id
                ).single()
                if not result:
                    raise ValidationError(f"Parent concept {parent_id} not found")
        
        # Generate concept ID
        concept_id = self._generate_concept_id(label, wikidata_qid)
        
        # Determine validation status
        validation_status = "auto_approved" if (confidence and confidence >= self.AUTO_APPROVAL_THRESHOLD) else "pending_review"
        
        # Create in Neo4j
        cypher = """
        CREATE (subj:SubjectConcept {
            concept_id: $concept_id,
            label: $label,
            wikidata_qid: $wikidata_qid,
            parent_concept_id: $parent_id,
            source_agent: $agent_name,
            confidence: $confidence,
            description: $description,
            period_start: $period_start,
            period_end: $period_end,
            evidence: $evidence,
            validation_status: $validation_status,
            is_canonical: false,
            is_agent_created: true,
            creation_timestamp: $creation_timestamp,
            facet_claims_count: 0,
            child_concept_count: 0,
            concept_depth: CASE WHEN $parent_id IS NULL THEN 0 ELSE 1 END
        })
        
        // Link to registry if parent exists
        OPTIONAL MATCH (registry:SubjectConceptRegistry)-[:CONTAINS]->(parent:SubjectConcept {concept_id: $parent_id})
        FOREACH (r IN CASE WHEN registry IS NOT NULL THEN [registry] ELSE [] END |
            CREATE (r)-[:CONTAINS]->(subj)
        )
        
        // Link to parent concept
        OPTIONAL MATCH (parent:SubjectConcept {concept_id: $parent_id})
        FOREACH (p IN CASE WHEN parent IS NOT NULL THEN [parent] ELSE [] END |
            CREATE (p)-[:HAS_CHILD_CONCEPT]->(subj)
        )
        
        RETURN {
            concept_id: subj.concept_id,
            label: subj.label,
            wikidata_qid: subj.wikidata_qid,
            confidence: subj.confidence,
            validation_status: subj.validation_status,
            is_agent_created: subj.is_agent_created,
            created_by_agent: subj.source_agent
        } AS concept
        """
        
        with self.driver.session() as session:
            result = session.run(
                cypher,
                concept_id=concept_id,
                label=label,
                wikidata_qid=wikidata_qid,
                parent_id=parent_id,
                agent_name=agent_name,
                confidence=confidence,
                description=description,
                period_start=period_start,
                period_end=period_end,
                evidence=evidence,
                validation_status=validation_status,
                creation_timestamp=datetime.now().isoformat()
            ).single()
        
        concept = result["concept"]
        
        # Log creation
        status_display = "✓ Auto-approved" if validation_status == "auto_approved" else "⏳ Pending review"
        print(f"[{agent_name}] Created concept: '{label}' ({concept_id}) - {status_display}")
        
        return concept
    
    def create_facet_claim(self,
                          concept_id: str,
                          text: str,
                          primary_facet: str,
                          related_facets: List[str] = None,
                          confidence: float = 0.8,
                          evidence: str = None,
                          authority: Dict = None,
                          temporal_start: int = None,
                          temporal_end: int = None,
                          communication_metadata: Dict = None,
                          source_agent: str = "GPT_PHASE_2A+2B") -> Dict:
        """
        Create a facet claim for a SubjectConcept.
        
        Args:
            concept_id: Target SubjectConcept ID
            text: Claim text (e.g., "Caesar used legionary tactics")
            primary_facet: Main facet (one of FACETS)
            related_facets: Secondary facets (0-3 others)
            confidence: Confidence in claim (0.0-1.0)
            evidence: Citation/evidence
            authority: Authority reference (e.g., {type: "LCSH", id: "sh85114436"})
            temporal_start: Claim validity start year
            temporal_end: Claim validity end year
            communication_metadata: If facet is Communication, include:
                {medium: ["written", "oral"], purpose: ["propaganda"], audience: [], strategy: []}
            source_agent: Which agent created this claim
        
        Returns:
            Created Claim dict
        """
        
        # Validation: Primary facet is valid
        if primary_facet not in self.FACETS:
            raise ValidationError(f"Unknown facet: {primary_facet}. Valid: {self.FACETS}")
        
        # Validation: Related facets are valid
        if related_facets:
            for facet in related_facets:
                if facet not in self.FACETS:
                    raise ValidationError(f"Unknown facet in related_facets: {facet}")
            if len(related_facets) > 3:
                related_facets = related_facets[:3]
        else:
            related_facets = []
        
        # Generate claim ID
        claim_id = f"claim_{concept_id}_{primary_facet.lower()}_{uuid.uuid4().hex[:8]}"
        
        # Create Claim node
        cypher = """
        MATCH (subj:SubjectConcept {concept_id: $concept_id})
        
        CREATE (claim:Claim {
            claim_id: $claim_id,
            text: $text,
            primary_facet: $primary_facet,
            related_facets: $related_facets,
            confidence: $confidence,
            evidence: $evidence,
            authority: $authority,
            temporal_start: $temporal_start,
            temporal_end: $temporal_end,
            communication_metadata: $communication_metadata,
            source_agent: $source_agent,
            creation_timestamp: $creation_timestamp
        })
        
        CREATE (subj)-[:HAS_FACET_CLAIM]->(claim)
        
        // Update SubjectConcept facet claim count
        SET subj.facet_claims_count = subj.facet_claims_count + 1
        
        // Update related facet facet_primaries
        SET subj.facet_primaries = 
            CASE 
                WHEN $primary_facet IN coalesce(subj.facet_primaries, []) 
                THEN subj.facet_primaries
                ELSE coalesce(subj.facet_primaries, []) + [$primary_facet]
            END
        
        RETURN {
            claim_id: claim.claim_id,
            primary_facet: claim.primary_facet,
            related_facets: claim.related_facets,
            confidence: claim.confidence,
            source_agent: claim.source_agent
        } AS claim
        """
        
        with self.driver.session() as session:
            result = session.run(
                cypher,
                claim_id=claim_id,
                concept_id=concept_id,
                text=text,
                primary_facet=primary_facet,
                related_facets=related_facets,
                confidence=confidence,
                evidence=evidence,
                authority=authority,
                temporal_start=temporal_start,
                temporal_end=temporal_end,
                communication_metadata=communication_metadata,
                source_agent=source_agent,
                creation_timestamp=datetime.now().isoformat()
            ).single()
        
        return result["claim"]
    
    def get_concept_facet_profile(self, concept_id: str) -> Dict:
        """
        Get facet distribution for a SubjectConcept.
        Shows which facets have claims and at what confidence.
        
        Returns:
            {
                "Military": {"claim_count": 8, "avg_confidence": 0.93},
                "Political": {"claim_count": 6, "avg_confidence": 0.91},
                ...
            }
        """
        
        cypher = """
        MATCH (subj:SubjectConcept {concept_id: $concept_id})-[:HAS_FACET_CLAIM]->(claim:Claim)
        WITH claim.primary_facet AS facet,
             count(*) AS claim_count,
             avg(claim.confidence) AS avg_confidence
        RETURN facet, claim_count, avg_confidence
        ORDER BY claim_count DESC
        """
        
        with self.driver.session() as session:
            results = session.run(cypher, concept_id=concept_id).records()
            
            profile = {}
            for record in results:
                facet = record["facet"]
                profile[facet] = {
                    "claim_count": record["claim_count"],
                    "avg_confidence": round(record["avg_confidence"], 2)
                }
            
            return profile
    
    def _generate_concept_id(self, label: str, wikidata_qid: str = None) -> str:
        """Generate unique concept ID from label and Wikidata QID"""
        safe_label = label.lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "")[:30]
        
        if wikidata_qid:
            return f"subj_{safe_label}_{wikidata_qid}"
        else:
            unique_suffix = uuid.uuid4().hex[:8]
            return f"subj_{safe_label}_{unique_suffix}"


if __name__ == "__main__":
    # Example usage
    import sys
    
    api = SubjectConceptAPI("bolt://localhost:7687", "neo4j", sys.argv[1])
    
    try:
        # Create a new concept
        concept = api.claim_new_concept(
            label="Caesar's Conquest of Gaul",
            parent_id="subj_roman_republic_q17167",
            wikidata_qid="Q181098",
            confidence=0.92,
            evidence="Caesar's Commentarii de Bello Gallico",
            period_start=-58,
            period_end=-50
        )
        print(f"Created: {concept}")
        
        # Add facet claims
        claim1 = api.create_facet_claim(
            concept_id=concept["concept_id"],
            text="Caesar used superior legionary tactics against Gallic forces",
            primary_facet="Military",
            related_facets=["Political", "Technological"],
            confidence=0.95,
            evidence="Commentarii de Bello Gallico"
        )
        print(f"Created claim: {claim1}")
        
        # Get facet profile
        profile = api.get_concept_facet_profile(concept["concept_id"])
        print(f"Facet profile: {profile}")
    
    finally:
        api.close()
