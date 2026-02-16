"""
Pydantic Validation Models for Chrystallum

Defines domain models for claims, facets, relationships with registry-backed validation.
Enforces canonical keys, valid enums, and schema constraints at write-time.

Usage:
    loader = RegistryLoader(...)
    
    facet = FacetAssignment(facet="DIPLOMATIC", confidence=0.85)
    # raises ValidationError if facet is not canonical
    
    rel = RelationshipAssertion(
        rel_type="COMMANDED_MILITARY_UNIT",
        subject_id="Q1048",
        object_id="Q123456"
    )
    # raises ValidationError if rel_type is not in registry
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator

import sys
from pathlib import Path

# For local imports
sys.path.insert(0, str(Path(__file__).parent))
from registry_loader import RegistryLoader


# Lifecycle status enum (shared across all entities)
class LifecycleStatus(str, Enum):
    """Valid lifecycle statuses for claims, relationships, facets."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DRAFT = "draft"


class DirectionalityType(str, Enum):
    """Valid directionality types for relationships."""
    FORWARD = "forward"
    INVERSE = "inverse"
    BIDIRECTIONAL = "bidirectional"
    UNIDIRECTIONAL = "unidirectional"


class ImplementationStatus(str, Enum):
    """Valid implementation statuses for relationships."""
    IMPLEMENTED = "implemented"
    CANDIDATE = "candidate"
    DEPRECATED = "deprecated"


# ============================================================================
# V1 KERNEL RELATIONSHIPS (Strategic 30-Type Foundation)
# ============================================================================
# Expanded from 25 → 30 types based on Priority 10 analysis:
# - Added PARTICIPATED_IN/HAD_PARTICIPANT (covers P710: 65 instances)
# - Added ABOUT as inverse of SUBJECT_OF (covers P921: 23 instances)
# - Added FIELD_OF_STUDY/STUDIED_BY (covers P101: 5 instances)
# Coverage increase: 37% → 70% of Wikidata claims

V1_KERNEL_RELATIONSHIPS = {
    # Identity & Entity Recognition (5)
    "SAME_AS",           # A is identical to B
    "TYPE_OF",           # A is a type of B
    "INSTANCE_OF",       # A is instance of type B
    "NAME",              # Entity has name
    "ALIAS_OF",          # Alternative name/form of
    
    # Spatial & Structural (5)
    "LOCATED_IN",        # A is located in B
    "PART_OF",           # A is part of B
    "BORDERS",           # A borders B
    "CAPITAL_OF",        # A is capital of B
    "CONTAINED_BY",      # A region contained by B
    
    # Temporal & Event (6)
    "OCCURRED_AT",       # Event occurred at location
    "OCCURS_DURING",     # Event occurs in period
    "HAPPENED_BEFORE",   # Event A before Event B
    "CONTEMPORARY_WITH", # A and B overlap temporally
    "PARTICIPATED_IN",   # Entity participated in event (P710)
    "HAD_PARTICIPANT",   # Event had participant (inverse)
    
    # Provenance & Attribution (7)
    "CITES",             # Work A cites Work B
    "DERIVES_FROM",      # Entity A derived from B
    "EXTRACTED_FROM",    # Claim extracted from source
    "AUTHOR",            # Creator of work
    "ATTRIBUTED_TO",     # Claim/statement attributed to agent
    "DESCRIBES",         # Work/claim describes entity
    "FIELD_OF_STUDY",    # Entity's primary field of study (P101)
    
    # Conceptual & Semantic (7)
    "SUBJECT_OF",        # Entity is subject of work/claim (P921)
    "ABOUT",             # Work/claim is about entity (inverse of SUBJECT_OF)
    "STUDIED_BY",        # Work studied the field (inverse of FIELD_OF_STUDY)
    "CAUSED",            # Event A caused Event B
    "CONTRADICTS",       # Claim A contradicts B
    "SUPPORTS",          # Claim A supports claim B
    "RELATED_TO",        # General semantic relationship
}


# ============================================================================
# FACET MODELS
# ============================================================================
#
# FACET OPINION ARCHITECTURE (ArchReview2 Issue B - Clarified Division)
# -----------------------------------------------------------------------
#
# This system uses TWO distinct models for facet-specific information:
#
# 1. FacetPerspective (DURABLE, CLAIM-ATTACHED)
#    - Purpose: Multi-facet enrichment and consensus tracking
#    - Lifecycle: Created once per facet per claim, updated over time
#    - Storage: Attached to Claim via PERSPECTIVE_ON relationship
#    - Use case: Cross-facet consensus (e.g., political + military + geographic
#                perspectives on "Caesar crossed Rubicon" → aggregate confidence)
#    - Graph pattern:
#        (claim:Claim)<-[:PERSPECTIVE_ON]-(fp:FacetPerspective)-[:EVALUATED_BY]->(agent)
#
# 2. FacetAssessment (EPHEMERAL, RUN-ATTACHED)
#    - Purpose: UI tabbed presentation and A/B testing
#    - Lifecycle: Created per AnalysisRun, versioned, not updated
#    - Storage: Attached to AnalysisRun via HAS_FACET_ASSESSMENT
#    - Use case: Compare "model v1" vs "model v2" assessments, show facet tabs in UI
#    - Graph pattern:
#        (run:AnalysisRun)-[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)-[:ASSESSES_FACET]->(facet)
#
# WHY TWO MODELS?
# - FacetPerspective: "What does the political facet think about this claim?" (evolves)
# - FacetAssessment: "What did run #42 assess for the political facet?" (static snapshot)
#
# CONSENSUS CALCULATION USES: FacetPerspective (durable cross-facet agreement)
# UI TABS/COMPARISON USES: FacetAssessment (ephemeral run outputs)
#
# ============================================================================


class FacetAssignment(BaseModel):
    """Represents a facet assignment to a claim."""
    
    facet: str = Field(
        ...,
        description="Canonical facet key (lowercase). Must be in facet_registry_master.json"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence level for facet assignment (0.0-1.0)"
    )
    rationale: Optional[str] = Field(
        default=None,
        description="Human-readable explanation for facet assignment"
    )
    assigned_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of facet assignment"
    )
    assigned_by: Optional[str] = Field(
        default=None,
        description="Agent ID that performed assignment (e.g., facet_specialist_01)"
    )

    @field_validator("facet", mode="before")
    @classmethod
    def validate_facet_is_canonical(cls, v: str) -> str:
        """Validate facet is canonical and normalize to lowercase."""
        # Get global loader instance (initialized later)
        loader = get_registry_loader()
        if loader is None:
            raise ValueError("Registry loader not initialized")
        return loader.validate_and_normalize_facet(v)

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "facet": "diplomatic",
                "confidence": 0.92,
                "rationale": "Treaty negotiation mentioned explicitly",
                "assigned_by": "facet_specialist_diplomatic_01"
            }
        }


class FacetAssessment(BaseModel):
    """
    Represents a facet specialist's assessment of a claim within an AnalysisRun.
    
    ROLE DISTINCTION (ArchReview2 Issue B):
    - FacetAssessment = EPHEMERAL/VERSIONED run output for UI/tabbed presentation
    - FacetPerspective = DURABLE claim-attached provenance for consensus tracking
    
    FacetAssessment is part of the AnalysisRun star pattern, used for:
    - A/B testing: compare "run v1" vs "run v2" for same claim
    - UI tabbed views: "Political view" | "Military view" | "Economic view"
    - Pipeline versioning: track how assessments change with model updates
    - Agent specialization: political expert only evaluates political facets
    
    For durable, claim-attached facet confidence that accumulates over time,
    use FacetPerspective instead.
    
    Graph Pattern:
        (run:AnalysisRun)-[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
            -[:ASSESSES_FACET]->(facet:Facet)
            -[:EVALUATED_BY]->(agent:Agent)
    """
    
    assessment_id: str = Field(
        ...,
        description="Unique assessment identifier (e.g., assess_001_00123)"
    )
    facet: str = Field(
        ...,
        description="Canonical facet key being assessed"
    )
    claim_id: str = Field(
        ...,
        description="ID of claim being assessed"
    )
    score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Assessment score for this facet (0.0-1.0)"
    )
    status: LifecycleStatus = Field(
        default=LifecycleStatus.ACTIVE,
        description="Assessment status (active, deprecated, archived)"
    )
    rationale: str = Field(
        ...,
        description="Detailed explanation of facet assessment and score"
    )
    evaluated_by: str = Field(
        ...,
        description="Facet specialist agent ID that performed assessment"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of assessment creation"
    )

    @field_validator("facet", mode="before")
    @classmethod
    def validate_facet(cls, v: str) -> str:
        loader = get_registry_loader()
        if loader is None:
            raise ValueError("Registry loader not initialized")
        return loader.validate_and_normalize_facet(v)

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "assessment_id": "assess_001_00123",
                "facet": "diplomatic",
                "claim_id": "claim_00123",
                "score": 0.85,
                "status": "active",
                "rationale": "Treaty negotiation is central to diplomatic facet; Rome-Carthage relations",
                "evaluated_by": "facet_specialist_diplomatic_01"
            }
        }


class FacetPerspective(BaseModel):
    """
    Represents a durable, facet-specific interpretation of a claim.
    
    ROLE DISTINCTION (ArchReview2 Issue B):
    - FacetAssessment = EPHEMERAL/VERSIONED run output for UI/tabbed presentation
    - FacetPerspective = DURABLE claim-attached provenance for consensus tracking
    
    FacetPerspective is used for:
    - Cross-facet consensus: Multiple perspectives on same claim (via AssertionCipher)
    - Confidence evolution: How a facet's view changes over time
    - Provenance tracking: Who interpreted the claim and how
    - Multi-facet enrichment: Different analytical angles on same base assertion
    
    For ephemeral run-based assessments used in UI tabbed views, use FacetAssessment.
    
    Graph Pattern:
        (claim:Claim {cipher: "assertion_cipher"})<-[:PERSPECTIVE_ON]-(fp:FacetPerspective)
            -[:EVALUATED_BY]->(agent:Agent)
    
    Example:
        Base claim: "Caesar crossed the Rubicon in 49 BCE"
        Political perspective: "Caesar challenged Senate authority" (confidence: 0.95)
        Military perspective: "Caesar led legion across provincial boundary" (confidence: 0.92)
        Geographic perspective: "Crossing occurred at Rubicon River" (confidence: 0.98)
    """
    
    perspective_id: str = Field(
        ...,
        description="Unique perspective identifier (e.g., persp_pol_00123)"
    )
    facet: str = Field(
        ...,
        description="Canonical facet key for this perspective"
    )
    parent_claim_cipher: str = Field(
        ...,
        description="AssertionCipher of the claim this perspective interprets"
    )
    facet_claim_text: str = Field(
        ...,
        description="Facet-specific interpretation/framing of the claim"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in this facet's interpretation (0.0-1.0)"
    )
    source_agent_id: str = Field(
        ...,
        description="Agent ID that created this perspective"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Explanation of facet-specific interpretation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of perspective creation"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last update (for confidence evolution)"
    )

    @field_validator("facet", mode="before")
    @classmethod
    def validate_facet(cls, v: str) -> str:
        loader = get_registry_loader()
        if loader is None:
            raise ValueError("Registry loader not initialized")
        return loader.validate_and_normalize_facet(v)

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "perspective_id": "persp_pol_00123",
                "facet": "political",
                "parent_claim_cipher": "0fabdba02d7dac85c005df4086511bdf...",
                "facet_claim_text": "Caesar challenged Senate authority by crossing the Rubicon",
                "confidence": 0.95,
                "source_agent_id": "political_sfa_001",
                "reasoning": "Dictatorship violated Republican constitutional norms",
                "created_at": "2026-02-15T10:00:00Z"
            }
        }


# ============================================================================
# RELATIONSHIP MODELS
# ============================================================================


class RelationshipAssertion(BaseModel):
    """Represents a relationship assertion (edge) in a claim."""
    
    rel_type: str = Field(
        ...,
        description="Canonical relationship type (uppercase). Must be in relationship_types_registry_master.csv"
    )
    subject_id: str = Field(
        ...,
        description="Node ID of relationship subject (e.g., Q1048 for Julius Caesar)"
    )
    object_id: str = Field(
        ...,
        description="Node ID of relationship object (e.g., Q123 for entity)"
    )
    temporal_scope: Optional[str] = Field(
        default=None,
        description="Temporal scope of relationship (e.g., '27-79 CE' or 'ISO year range')"
    )
    geographic_scope: Optional[str] = Field(
        default=None,
        description="Geographic scope of relationship (e.g., 'Rome', 'Q220')"
    )
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence level for relationship assertion (0.0-1.0)"
    )
    source_id: Optional[str] = Field(
        default=None,
        description="Source passage ID (e.g., source_001_plb_001)"
    )
    
    @field_validator("rel_type", mode="before")
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        """Validate relationship type is canonical and normalize to uppercase."""
        loader = get_registry_loader()
        if loader is None:
            raise ValueError("Registry loader not initialized")
        return loader.validate_and_normalize_relationship_type(v)

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "rel_type": "COMMANDED_MILITARY_UNIT",
                "subject_id": "Q1048",
                "object_id": "Q123456",
                "temporal_scope": "49-48 BCE",
                "geographic_scope": "Rome",
                "confidence": 0.92,
                "source_id": "source_001_plb_001"
            }
        }


class V1KernelAssertion(RelationshipAssertion):
    """Relationship assertion restricted to v1 kernel (30 core relationships).
    
    Usage:
        # Use this for v1 federation testing
        assertion = V1KernelAssertion(
            rel_type="SAME_AS",
            subject_id="Q1048",
            object_id="Q87",
            confidence=0.95
        )
    
    This model enforces strict v1 kernel validation without requiring
    the full registry to be initialized.
    """
    
    @field_validator("rel_type", mode="wrap")
    @classmethod
    def validate_v1_kernel(cls, v: str, handler) -> str:
        """Validate relationship type is in v1 kernel (expanded 30-type foundation).  """
        if not isinstance(v, str):
            v = str(v)
        
        normalized = v.upper().strip()
        
        if normalized not in V1_KERNEL_RELATIONSHIPS:
            valid_types = sorted(V1_KERNEL_RELATIONSHIPS)
            raise ValueError(
                f"'{v}' not in v1 kernel. Valid v1 relationships:\n"
                f"  Identity (5): {', '.join(sorted(valid_types)[:5])}\n"
                f"  Spatial (5): {', '.join(sorted(valid_types)[5:10])}\n"
                f"  Temporal (4): {', '.join(sorted(valid_types)[10:14])}\n"
                f"  Provenance (6): {', '.join(sorted(valid_types)[14:20])}\n"
                f"  Assertion (5): {', '.join(sorted(valid_types)[20:25])}"
            )
        
        # Don't call handler - this skips parent validators
        return normalized


class RelationshipEdge(BaseModel):
    """Represents a relationship edge for Neo4j ingestion."""
    
    edge_id: str = Field(
        ...,
        description="Unique edge identifier (e.g., edge_001_00123)"
    )
    rel_type: str = Field(
        ...,
        description="Canonical relationship type (uppercase)"
    )
    source_node_id: str = Field(
        ...,
        description="Source node ID for the edge"
    )
    target_node_id: str = Field(
        ...,
        description="Target node ID for the edge"
    )
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0
    )
    cipher: Optional[str] = Field(
        default=None,
        description="Content-addressable cipher (SHA256 hash) if this edge is part of a versioned claim"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    version: str = Field(
        default="1.0",
        description="Schema version for this edge"
    )

    @field_validator("rel_type", mode="before")
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        loader = get_registry_loader()
        if loader is None:
            raise ValueError("Registry loader not initialized")
        return loader.validate_and_normalize_relationship_type(v)

    class Config:
        use_enum_values = True


# ============================================================================
# CLAIM MODELS
# ============================================================================


class Claim(BaseModel):
    """
    Represents a claim with cryptographic identity and facet assignments.
    
    A claim is identified by its cipher (content hash), contains multiple facet
    assessments, and may have multiple relationship assertions.
    """
    
    claim_id: str = Field(
        ...,
        description="Claim identifier (e.g., claim_00123)"
    )
    cipher: str = Field(
        ...,
        description="Content-addressable cipher (SHA256 of claim content)"
    )
    content: str = Field(
        ...,
        description="Main claim text/assertion"
    )
    source_id: str = Field(
        ...,
        description="Source document ID"
    )
    facets: List[FacetAssignment] = Field(
        default_factory=list,
        description="Facet classifications for this claim"
    )
    relationships: List[RelationshipAssertion] = Field(
        default_factory=list,
        description="Relationship assertions extracted from claim"
    )
    confidence: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Overall confidence level for claim"
    )
    status: LifecycleStatus = Field(
        default=LifecycleStatus.DRAFT,
        description="Claim lifecycle status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    created_by: str = Field(
        ...,
        description="Agent that created claim (e.g., seed_claim_agent_001)"
    )

    @field_validator("facets", mode="before")
    @classmethod
    def validate_facets(cls, v: List[Dict]) -> List[FacetAssignment]:
        """Convert raw dict facets to FacetAssignment models."""
        if isinstance(v, list):
            return [FacetAssignment(**f) if isinstance(f, dict) else f for f in v]
        return v

    @field_validator("relationships", mode="before")
    @classmethod
    def validate_relationships(cls, v: List[Dict]) -> List[RelationshipAssertion]:
        """Convert raw dict relationships to RelationshipAssertion models."""
        if isinstance(v, list):
            return [RelationshipAssertion(**r) if isinstance(r, dict) else r for r in v]
        return v

    def compute_assertion_cipher(self, algorithm: str = "sha256") -> str:
        """
        Compute facet-agnostic AssertionCipher for cross-facet deduplication.
        
        AssertionCipher EXCLUDES facet assignments to enable consensus:
        - Different facets discovering the same claim → same AssertionCipher
        - Enables cross-facet deduplication and agreement scoring
        
        Included in hash (facet-agnostic content):
        - content (main claim text)
        - source_id (source document)
        - relationships (subject/predicate/object triples)
        
        EXCLUDED from hash (facet-specific):
        - facets (different facets can assess the same claim)
        - created_by (agent identity)
        - confidence (subjective assessment)
        - timestamps (when discovered doesn't change what was discovered)
        
        This ensures reproducible ciphers across systems by normalizing:
        - Unicode representation
        - Whitespace
        - Floating point precision
        - Key ordering
        
        Args:
            algorithm: Hash algorithm (sha256, sha512, sha3_256)
        
        Returns:
            AssertionCipher (facet-agnostic, hex-encoded hash)
        
        Example:
            >>> claim_military = Claim(..., facets=[...facet="military"...])
            >>> claim_political = Claim(..., facets=[...facet="political"...])
            >>> # Same content → same AssertionCipher even with different facets
            >>> assert claim_military.compute_assertion_cipher() == claim_political.compute_assertion_cipher()
        """
        from canonicalization import compute_claim_cipher
        
        # FACET-AGNOSTIC metadata (enables cross-facet consensus)
        # Per ADR-001 as clarified in 2-16-26-ArchReview2:
        # AssertionCipher = hash(subject/object/predicate/temporal/source/passage)
        metadata = {
            "source_id": self.source_id,
            # NOTE: facets intentionally EXCLUDED for cross-facet dedup
            "relationships": sorted([
                {"type": r.rel_type, "subject": r.subject_id, "object": r.object_id}
                for r in self.relationships
            ], key=lambda x: (x["type"], x["subject"], x["object"]))
        }
        
        return compute_claim_cipher(self.content, metadata=metadata, algorithm=algorithm)
    
    def compute_perspective_id(self, algorithm: str = "sha256") -> str:
        """
        Compute facet-specific PerspectiveID for provenance tracking.
        
        PerspectiveID = AssertionCipher + facet_key + agent_id
        
        Use cases:
        - Track how different facets interpret the same assertion
        - Maintain stable per-agent perspectives
        - Enable facet-specific confidence evolution
        
        Args:
            algorithm: Hash algorithm (sha256, sha512, sha3_256)
        
        Returns:
            PerspectiveID (facet-specific, hex-encoded hash)
        
        Example:
            >>> claim = Claim(..., facets=[FacetAssignment(facet="military")], created_by="agent_001")
            >>> perspective_id = claim.compute_perspective_id()
            >>> # Different from AssertionCipher - includes facet + agent context
        """
        from canonicalization import compute_claim_cipher
        
        # FACET-SPECIFIC metadata (preserves perspective provenance)
        # Per 2-16-26-ArchReview2:
        # PerspectiveID = AssertionCipher + facet_key + agent_id
        metadata = {
            "source_id": self.source_id,
            "facets": sorted([f.facet for f in self.facets]),  # NOW included for perspective tracking
            "agent": self.created_by,  # Agent context for stable perspectives
            "relationships": sorted([
                {"type": r.rel_type, "subject": r.subject_id, "object": r.object_id}
                for r in self.relationships
            ], key=lambda x: (x["type"], x["subject"], x["object"]))
        }
        
        return compute_claim_cipher(self.content, metadata=metadata, algorithm=algorithm)
    
    def compute_canonical_cipher(self, algorithm: str = "sha256") -> str:
        """
        DEPRECATED: Use compute_assertion_cipher() or compute_perspective_id().
        
        Maintained for backward compatibility - defaults to AssertionCipher.
        """
        return self.compute_assertion_cipher(algorithm=algorithm)
    
    def verify_cipher(self, algorithm: str = "sha256", cipher_type: str = "assertion") -> bool:
        """
        Verify that stored cipher matches computed cipher.
        
        Args:
            algorithm: Hash algorithm (sha256, sha512, sha3_256)
            cipher_type: Which cipher to verify - "assertion" (default) or "perspective"
        
        Returns:
            True if cipher is valid, False otherwise
        
        Example:
            >>> claim = Claim(...)
            >>> assert claim.verify_cipher()  # Verify AssertionCipher
            >>> assert claim.verify_cipher(cipher_type="perspective")  # Verify PerspectiveID
        """
        if cipher_type == "assertion":
            computed = self.compute_assertion_cipher(algorithm=algorithm)
        elif cipher_type == "perspective":
            computed = self.compute_perspective_id(algorithm=algorithm)
        else:
            raise ValueError(f"Unknown cipher_type: {cipher_type}. Use 'assertion' or 'perspective'")
        
        return computed == self.cipher
    
    @classmethod
    def create_with_cipher(
        cls,
        claim_id: str,
        content: str,
        source_id: str,
        created_by: str,
        facets: List[FacetAssignment] = None,
        relationships: List[RelationshipAssertion] = None,
        confidence: float = 0.70,
        status: LifecycleStatus = LifecycleStatus.DRAFT,
        cipher_type: str = "assertion",
        algorithm: str = "sha256"
    ) -> "Claim":
        """
        Create a new Claim with automatically computed cipher.
        
        This is the recommended way to create claims - ensures cipher is
        correct and reproducible from the start.
        
        Default behavior (cipher_type="assertion"):
        - Computes facet-agnostic AssertionCipher for cross-facet deduplication
        - Same content from different facets → same cipher → consensus possible
        
        Alternative (cipher_type="perspective"):
        - Computes facet-specific PerspectiveID for provenance tracking
        - Includes facet + agent context for stable per-agent perspectives
        
        Args:
            claim_id: Unique claim identifier
            content: Main claim text
            source_id: Source document ID
            created_by: Agent that created the claim
            facets: Optional facet assignments
            relationships: Optional relationship assertions
            confidence: Overall confidence (default: 0.70)
            status: Lifecycle status (default: DRAFT)
            cipher_type: "assertion" (default, facet-agnostic) or "perspective" (facet-specific)
            algorithm: Hash algorithm (default: sha256)
        
        Returns:
            New Claim instance with cipher
        
        Example (AssertionCipher - recommended for deduplication):
            >>> claim = Claim.create_with_cipher(
            ...     claim_id="claim_001",
            ...     content="Julius Caesar crossed the Rubicon",
            ...     source_id="source_001",
            ...     created_by="agent_001",
            ...     facets=[FacetAssignment(facet="military", confidence=0.95)]
            ... )
            >>> assert claim.verify_cipher()  # Cipher is guaranteed valid
        
        Example (PerspectiveID - for facet-specific provenance):
            >>> claim = Claim.create_with_cipher(
            ...     claim_id="claim_001",
            ...     content="Julius Caesar crossed the Rubicon",
            ...     source_id="source_001",
            ...     created_by="agent_001",
            ...     facets=[FacetAssignment(facet="military", confidence=0.95)],
            ...     cipher_type="perspective"
            ... )
        """
        from canonicalization import compute_claim_cipher
        
        facets = facets or []
        relationships = relationships or []
        
        # Compute cipher based on type
        if cipher_type == "assertion":
            # FACET-AGNOSTIC (enables cross-facet consensus)
            # Per 2-16-26-ArchReview2: AssertionCipher excludes facet_id
            metadata = {
                "source_id": source_id,
                # facets intentionally EXCLUDED
                "relationships": sorted([
                    {"type": r.rel_type, "subject": r.subject_id, "object": r.object_id}
                    for r in relationships
                ], key=lambda x: (x["type"], x["subject"], x["object"]))
            }
        elif cipher_type == "perspective":
            # FACET-SPECIFIC (preserves perspective provenance)
            # Per 2-16-26-ArchReview2: PerspectiveID = AssertionCipher + facet_key + agent_id  
            metadata = {
                "source_id": source_id,
                "facets": sorted([f.facet for f in facets]),  # NOW included
                "agent": created_by,  # Agent context
                "relationships": sorted([
                    {"type": r.rel_type, "subject": r.subject_id, "object": r.object_id}
                    for r in relationships
                ], key=lambda x: (x["type"], x["subject"], x["object"]))
            }
        else:
            raise ValueError(f"Unknown cipher_type: {cipher_type}. Use 'assertion' or 'perspective'")
        
        cipher = compute_claim_cipher(content, metadata=metadata, algorithm=algorithm)
        
        # Create claim instance
        return cls(
            claim_id=claim_id,
            cipher=cipher,
            content=content,
            source_id=source_id,
            facets=facets,
            relationships=relationships,
            confidence=confidence,
            status=status,
            created_by=created_by
        )

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "claim_id": "claim_00123",
                "cipher": "abc123def456...",
                "content": "Julius Caesar commanded six legions during the conquest of Gaul",
                "source_id": "source_001_plb_001",
                "facets": [
                    {"facet": "military", "confidence": 0.95},
                    {"facet": "political", "confidence": 0.85}
                ],
                "relationships": [
                    {
                        "rel_type": "COMMANDED_MILITARY_UNIT",
                        "subject_id": "Q1048",
                        "object_id": "Q123456"
                    }
                ],
                "created_by": "seed_claim_agent_001"
            }
        }


# ============================================================================
# GLOBAL REGISTRY LOADER INSTANCE
# ============================================================================

_registry_loader: Optional[RegistryLoader] = None


def initialize_registry(
    facet_json_path: Path,
    relationship_csv_path: Path,
) -> RegistryLoader:
    """
    Initialize the global registry loader (call once at application startup).
    
    Args:
        facet_json_path: Path to facet_registry_master.json
        relationship_csv_path: Path to relationship_types_registry_master.csv
    
    Returns:
        Initialized RegistryLoader instance
    """
    global _registry_loader
    _registry_loader = RegistryLoader(facet_json_path, relationship_csv_path)
    return _registry_loader


def get_registry_loader() -> Optional[RegistryLoader]:
    """Get the global registry loader instance."""
    return _registry_loader


def is_registry_initialized() -> bool:
    """Check if registry loader has been initialized."""
    return _registry_loader is not None
