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
# FACET MODELS
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
    """Represents a facet specialist's assessment of a claim."""
    
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
