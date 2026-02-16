"""
Chrystallum Models Package

Provides Pydantic validation models and Neo4j constraint generation for:
- Facet assignments and assessments
- Relationship types and assertions
- Claims with cryptographic identity

Usage:
    from chrystallum.models import (
        initialize_registry,
        Claim,
        FacetAssignment,
        RelationshipAssertion,
    )
    
    # Initialize once at app startup
    initialize_registry(
        facet_json_path,
        relationship_csv_path
    )
    
    # Use in your code
    claim = Claim(
        claim_id="claim_001",
        cipher="abc123...",
        content="...",
        source_id="source_001",
        facets=[FacetAssignment(facet="diplomatic", confidence=0.85)],
        created_by="seed_agent"
    )
"""

from .registry_loader import RegistryLoader, FacetConfig, RelationshipConfig
from .validation_models import (
    Claim,
    FacetAssignment,
    FacetAssessment,
    RelationshipAssertion,
    V1KernelAssertion,
    RelationshipEdge,
    LifecycleStatus,
    DirectionalityType,
    ImplementationStatus,
    V1_KERNEL_RELATIONSHIPS,
    initialize_registry,
    get_registry_loader,
    is_registry_initialized,
)
from .neo4j_constraints import Neo4jConstraintGenerator
from .canonicalization import (
    normalize_unicode,
    normalize_whitespace,
    normalize_datetime,
    normalize_float,
    canonicalize_dict,
    to_canonical_json,
    canonicalize_claim_content,
    compute_cipher,
    compute_claim_cipher,
)

__all__ = [
    # Registry
    "RegistryLoader",
    "FacetConfig",
    "RelationshipConfig",
    # Validation Models
    "Claim",
    "FacetAssignment",
    "FacetAssessment",
    "RelationshipAssertion",
    "V1KernelAssertion",
    "RelationshipEdge",
    # Enums
    "LifecycleStatus",
    "DirectionalityType",
    "ImplementationStatus",
    # V1 Kernel
    "V1_KERNEL_RELATIONSHIPS",
    # Registry Management
    "initialize_registry",
    "get_registry_loader",
    "is_registry_initialized",
    # Neo4j
    "Neo4jConstraintGenerator",
    # Canonicalization
    "normalize_unicode",
    "normalize_whitespace",
    "normalize_datetime",
    "normalize_float",
    "canonicalize_dict",
    "to_canonical_json",
    "canonicalize_claim_content",
    "compute_cipher",
    "compute_claim_cipher",
]

__version__ = "0.1.0"
