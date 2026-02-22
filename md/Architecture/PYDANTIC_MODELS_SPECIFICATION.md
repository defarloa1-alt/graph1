# Pydantic Models Specification: Entity and Claim Validation

**Created:** February 22, 2026  
**Status:** Canonical Reference  
**Revision:** 1.0  
**Related:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md, CLAIM_ID_ARCHITECTURE.md, NEO4J_SCHEMA_DDL_COMPLETE.md

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Entity Type Models](#entity-type-models)
3. [Claim Type Models](#claim-type-models)
4. [Facet Models](#facet-models)
5. [Temporal Models](#temporal-models)
6. [Complete Implementation](#complete-implementation)

---

## Design Principles

### Pydantic v2 Features Used

1. **Discriminated Unions** — Type-safe polymorphism for entity types and claim types
2. **Field Validation** — Enforce constraints at validation layer before Neo4j writes
3. **JSON Schema Generation** — Auto-generate OpenAPI-compliant schemas for documentation
4. **Strict Mode** — Fail fast on type mismatches (no coercion)

### Architecture Pattern: Belt and Suspenders

**Validation occurs at TWO layers:**

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **Application Layer** | Pydantic models | Type-safe validation, catch errors early in Python |
| **Database Layer** | Neo4j constraints | Database-level enforcement, prevent corrupt writes |

**Rationale:** Pydantic catches errors before expensive Cypher operations; Neo4j constraints provide final safety net if Pydantic is bypassed.

### Import Strategy

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Union, Optional
from datetime import datetime
```

---

## Entity Type Models

### Base Entity Model

```python
class BaseEntity(BaseModel):
    """Base model for all entity types with shared fields."""
    
    # Tier 1 cipher (required)
    entity_cipher: str = Field(
        ...,
        pattern=r"^ent_[a-z]{3}_[A-Z0-9:]+$",
        description="Tier 1 entity cipher (cross-subgraph join key)"
    )
    
    # Entity type discriminator (required)
    entity_type: str = Field(
        ...,
        description="Canonical entity type (PERSON, EVENT, PLACE, etc.)"
    )
    
    # Wikidata QID (optional, but strongly recommended)
    qid: Optional[str] = Field(
        None,
        pattern=r"^Q\d+$",
        description="Wikidata QID (if available)"
    )
    
    # Namespace (required)
    namespace: Literal["wd", "bn", "crys"] = Field(
        ...,
        description="Authority source: wd (Wikidata), bn (BabelNet), crys (Chrystallum synthetic)"
    )
    
    # Labels (required)
    label_en: str = Field(
        ...,
        min_length=1,
        description="English label (primary display name)"
    )
    
    # Temporal anchor properties (optional)
    is_temporal_anchor: Optional[bool] = Field(
        None,
        description="Flag: entity defines a temporal period"
    )
    
    temporal_scope: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}/-?\d{4}$",
        description="ISO 8601 interval (e.g., '-0509/-0027')"
    )
    
    temporal_start_year: Optional[int] = Field(
        None,
        ge=-10000,
        le=3000,
        description="Start year (integer for range queries)"
    )
    
    temporal_end_year: Optional[int] = Field(
        None,
        ge=-10000,
        le=3000,
        description="End year (integer for range queries)"
    )
    
    temporal_calendar: Optional[Literal["julian", "gregorian", "gregorian_approx"]] = Field(
        None,
        description="Calendar system for temporal bounds"
    )
    
    # Metadata
    created_at: Optional[datetime] = None
    created_by_agent: Optional[str] = None
    
    @field_validator('temporal_end_year')
    @classmethod
    def validate_temporal_end_after_start(cls, v, info):
        """Ensure temporal_end_year >= temporal_start_year."""
        if v is not None and info.data.get('temporal_start_year') is not None:
            if v < info.data['temporal_start_year']:
                raise ValueError(
                    f"temporal_end_year ({v}) must be >= temporal_start_year ({info.data['temporal_start_year']})"
                )
        return v
    
    @field_validator('is_temporal_anchor')
    @classmethod
    def validate_temporal_anchor_properties(cls, v, info):
        """If is_temporal_anchor=True, require temporal properties."""
        if v is True:
            required_fields = ['temporal_scope', 'temporal_start_year', 'temporal_end_year']
            for field in required_fields:
                if info.data.get(field) is None:
                    raise ValueError(
                        f"is_temporal_anchor=True requires {field} to be set"
                    )
        return v
```

### Discriminated Entity Type Models

```python
class PersonEntity(BaseEntity):
    """Person entity (Q5 - human)."""
    entity_type: Literal["PERSON"]
    
    # Person-specific fields
    birth_date: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}-\d{2}-\d{2}$",
        description="Birth date (ISO 8601)"
    )
    
    death_date: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}-\d{2}-\d{2}$",
        description="Death date (ISO 8601)"
    )
    
    occupation: Optional[list[str]] = Field(
        None,
        description="Wikidata P106 values (occupation QIDs)"
    )


class EventEntity(BaseEntity):
    """Event entity (Q1656682 - event)."""
    entity_type: Literal["EVENT"]
    
    # Event-specific fields
    event_date: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}-\d{2}-\d{2}$",
        description="Event date (ISO 8601)"
    )
    
    location_qid: Optional[str] = Field(
        None,
        pattern=r"^Q\d+$",
        description="Location where event occurred (Wikidata QID)"
    )


class PlaceEntity(BaseEntity):
    """Place entity (Q618123 - geographical object)."""
    entity_type: Literal["PLACE"]
    
    # Place-specific fields
    pleiades_id: Optional[str] = Field(
        None,
        pattern=r"^\d+$",
        description="Pleiades gazetteer ID (ancient geography)"
    )
    
    tgn_id: Optional[str] = Field(
        None,
        pattern=r"^\d+$",
        description="Getty Thesaurus of Geographic Names ID"
    )
    
    coordinates: Optional[tuple[float, float]] = Field(
        None,
        description="(latitude, longitude) coordinates"
    )


class SubjectConceptEntity(BaseEntity):
    """SubjectConcept entity (thematic research anchor)."""
    entity_type: Literal["SUBJECTCONCEPT"]
    
    # SubjectConcept-specific fields
    backbone_lcc: Optional[str] = Field(
        None,
        description="Library of Congress Classification code"
    )
    
    backbone_fast: Optional[list[str]] = Field(
        None,
        description="FAST subject heading IDs"
    )
    
    backbone_lcsh: Optional[list[str]] = Field(
        None,
        description="Library of Congress Subject Headings"
    )


class OrganizationEntity(BaseEntity):
    """Organization entity (Q43229 - organization)."""
    entity_type: Literal["ORGANIZATION"]
    
    # Organization-specific fields
    founding_date: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}-\d{2}-\d{2}$",
        description="Founding/inception date"
    )
    
    dissolution_date: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}-\d{2}-\d{2}$",
        description="Dissolution/end date"
    )


class PeriodEntity(BaseEntity):
    """Period entity (Q11514315 - historical period)."""
    entity_type: Literal["PERIOD"]
    
    # Period entities ALWAYS have temporal anchor properties
    is_temporal_anchor: Literal[True] = True  # Override: always True
    
    periodo_id: Optional[str] = Field(
        None,
        description="PeriodO authority identifier"
    )


class WorkEntity(BaseEntity):
    """Work entity (Q386724 - work)."""
    entity_type: Literal["WORK"]
    
    # Work-specific fields
    author_qid: Optional[str] = Field(
        None,
        pattern=r"^Q\d+$",
        description="Author Wikidata QID"
    )
    
    publication_date: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}$",
        description="Publication/composition date (year)"
    )


class MaterialEntity(BaseEntity):
    """Material entity (Q214609 - material)."""
    entity_type: Literal["MATERIAL"]


class ObjectEntity(BaseEntity):
    """Object entity (Q488383 - object)."""
    entity_type: Literal["OBJECT"]


# Discriminated union for all entity types
class Entity(BaseModel):
    """Polymorphic entity model using discriminated union."""
    entity: Union[
        PersonEntity,
        EventEntity,
        PlaceEntity,
        SubjectConceptEntity,
        OrganizationEntity,
        PeriodEntity,
        WorkEntity,
        MaterialEntity,
        ObjectEntity
    ] = Field(
        ...,
        discriminator='entity_type',
        description="Entity with type-specific validation"
    )
```

---

## Claim Type Models

### Base Claim Model

```python
class BaseFacetClaim(BaseModel):
    """Base model for all claim types with shared fields."""
    
    # Tier 3 cipher (required)
    cipher: str = Field(
        ...,
        pattern=r"^fclaim_[a-z]{3}_[a-f0-9]{16}$",
        description="Tier 3 claim cipher (assertion identity)"
    )
    
    # Subject entity cipher (required)
    subject_entity_cipher: str = Field(
        ...,
        pattern=r"^ent_[a-z]{3}_[A-Z0-9:]+$",
        description="Tier 1 cipher of the subject entity"
    )
    
    # Facet (required)
    facet_id: Literal[
        "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
        "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
        "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
        "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
        "SOCIAL", "TECHNOLOGICAL"
    ] = Field(
        ...,
        description="One of 18 canonical facets"
    )
    
    # SubjectConcept cipher (required)
    subjectconcept_cipher: str = Field(
        ...,
        pattern=r"^ent_sub_[A-Z0-9:]+$",
        description="Tier 1 cipher of the anchoring SubjectConcept"
    )
    
    # Analysis layer discriminator (required)
    analysis_layer: str = Field(
        ...,
        description="Claim type: in_situ or retrospective"
    )
    
    # Confidence (required)
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )
    
    # Temporal scope (optional)
    temporal_scope: Optional[str] = Field(
        None,
        pattern=r"^-?\d{4}/-?\d{4}$",
        description="Temporal bounds for this claim"
    )
    
    # Wikidata triple (optional)
    wikidata_pid: Optional[str] = Field(
        None,
        pattern=r"^P\d+$",
        description="Wikidata property ID (if claim from Wikidata)"
    )
    
    object_qid: Optional[str] = Field(
        None,
        pattern=r"^Q\d+$",
        description="Wikidata object QID (if claim from Wikidata)"
    )
    
    # Metadata
    created_at: Optional[datetime] = None
    created_by_agent: Optional[str] = None
```

### In-Situ Claim Model

```python
class InSituClaim(BaseFacetClaim):
    """
    In-situ claim: assertion made within ancient/historical sources
    using only concepts and frameworks available at the time.
    """
    
    # Analysis layer discriminator
    analysis_layer: Literal["in_situ"]
    
    # Source family (ancient sources only)
    source_family: Literal["ancient_primary", "ancient_near_contemporary"] = Field(
        ...,
        description="Source type: primary (eyewitness) or near-contemporary (< 50 years)"
    )
    
    # Modern theory flag (always False for in-situ)
    uses_modern_theory: Literal[False] = False
    
    # Claim role in narrative structure
    claim_role: Literal[
        "goal",
        "constraint",
        "belief",
        "action",
        "observed_outcome"
    ] = Field(
        ...,
        description="Role in action structure (from ancient perspective)"
    )
    
    # Source work
    source_work_qid: str = Field(
        ...,
        pattern=r"^Q\d+$",
        description="Wikidata QID of source work (e.g., Q47461 for Polybius)"
    )
    
    # Passage locator
    passage_locator: str = Field(
        ...,
        min_length=1,
        description="Citation within source (e.g., 'Hist.2.14')"
    )
    
    # Ancient agent attribution
    ancient_agent_qid: Optional[str] = Field(
        None,
        pattern=r"^Q\d+$",
        description="Ancient author/observer who made the claim"
    )


class RetrospectiveClaim(BaseFacetClaim):
    """
    Retrospective claim: modern scholarly interpretation
    that applies modern theoretical frameworks to ancient events.
    """
    
    # Analysis layer discriminator
    analysis_layer: Literal["retrospective"]
    
    # Source family (modern scholarship only)
    source_family: Literal["modern_scholarship"] = "modern_scholarship"
    
    # Modern theory flag (always True for retrospective)
    uses_modern_theory: Literal[True] = True
    
    # Target in-situ claims (required)
    target_claim_ciphers: list[str] = Field(
        ...,
        min_length=1,
        description="List of in-situ claim ciphers this retrospective claim interprets"
    )
    
    # Scholarly methodology
    methodology: str = Field(
        ...,
        min_length=1,
        description="Modern theoretical framework applied (e.g., 'principal-agent theory')"
    )
    
    # Modern source work
    source_work_qid: str = Field(
        ...,
        pattern=r"^Q\d+$",
        description="Wikidata QID of modern scholarly work"
    )
    
    # Scholar attribution
    scholar_qid: Optional[str] = Field(
        None,
        pattern=r"^Q\d+$",
        description="Modern scholar who proposed this interpretation"
    )
    
    @field_validator('target_claim_ciphers')
    @classmethod
    def validate_target_ciphers(cls, v):
        """Ensure all target ciphers are valid Tier 3 ciphers."""
        pattern = r"^fclaim_[a-z]{3}_[a-f0-9]{16}$"
        for cipher in v:
            if not re.match(pattern, cipher):
                raise ValueError(
                    f"Invalid target claim cipher: {cipher}. "
                    f"Must match pattern: {pattern}"
                )
        return v


# Discriminated union for claim types
class FacetClaim(BaseModel):
    """Polymorphic claim model using discriminated union."""
    claim: Union[InSituClaim, RetrospectiveClaim] = Field(
        ...,
        discriminator='analysis_layer',
        description="Claim with analysis-layer-specific validation"
    )
```

---

## Facet Models

### Faceted Entity Cipher Model

```python
class FacetedEntityCipher(BaseModel):
    """Tier 2 faceted entity cipher model."""
    
    # Tier 2 cipher (required)
    faceted_cipher: str = Field(
        ...,
        pattern=r"^fent_[a-z]{3}_[A-Z0-9:]+_[A-Z0-9:]+$",
        description="Tier 2 faceted entity cipher (subgraph address)"
    )
    
    # Tier 1 cipher (join key)
    entity_cipher: str = Field(
        ...,
        pattern=r"^ent_[a-z]{3}_[A-Z0-9:]+$",
        description="Tier 1 entity cipher (cross-subgraph join key)"
    )
    
    # Facet dimension
    facet_id: Literal[
        "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
        "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
        "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
        "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
        "SOCIAL", "TECHNOLOGICAL"
    ] = Field(
        ...,
        description="One of 18 canonical facets"
    )
    
    # Anchoring SubjectConcept
    subjectconcept_id: str = Field(
        ...,
        pattern=r"^Q\d+$",
        description="QID of the anchoring SubjectConcept"
    )
    
    # Aggregate metadata
    claim_count: int = Field(
        0,
        ge=0,
        description="Number of claims in this faceted context"
    )
    
    avg_confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Average confidence across all claims"
    )
    
    # Metadata
    last_updated: Optional[datetime] = None
    evaluated_by_agent: Optional[str] = None
```

---

## Temporal Models

### Temporal Anchor Model

```python
class TemporalAnchor(BaseModel):
    """Temporal anchor properties for entities that define periods."""
    
    # Canonical ISO 8601 interval
    temporal_scope: str = Field(
        ...,
        pattern=r"^-?\d{4}/-?\d{4}$",
        description="ISO 8601 interval (e.g., '-0509/-0027')"
    )
    
    # Integer year fields for range queries
    temporal_start_year: int = Field(
        ...,
        ge=-10000,
        le=3000,
        description="Start year (integer for range queries)"
    )
    
    temporal_end_year: int = Field(
        ...,
        ge=-10000,
        le=3000,
        description="End year (integer for range queries)"
    )
    
    # Calendar system metadata
    temporal_calendar: Literal["julian", "gregorian", "gregorian_approx"] = Field(
        ...,
        description="Calendar system for temporal bounds"
    )
    
    # Optional precision metadata
    temporal_precision: Optional[Literal["year", "month", "day", "circa"]] = Field(
        None,
        description="Granularity of temporal knowledge"
    )
    
    temporal_uncertainty: Optional[bool] = Field(
        None,
        description="Flag for contested or uncertain dates"
    )
    
    @field_validator('temporal_end_year')
    @classmethod
    def validate_end_after_start(cls, v, info):
        """Ensure temporal_end_year >= temporal_start_year."""
        if v < info.data['temporal_start_year']:
            raise ValueError(
                f"temporal_end_year ({v}) must be >= temporal_start_year ({info.data['temporal_start_year']})"
            )
        return v
```

---

## Complete Implementation

### File: `scripts/models/entities.py`

```python
"""
Pydantic models for Chrystallum entity validation.

Three-tier cipher model:
  - Tier 1: Entity (cross-subgraph join key)
  - Tier 2: FacetedEntity (subgraph address)
  - Tier 3: FacetClaim (assertion identity)

Usage:
  from scripts.models.entities import Entity, PersonEntity, validate_entity_batch
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Union, Optional
from datetime import datetime
import re


# ──────────────────────────────────────────────────────────────
# BASE MODELS
# ──────────────────────────────────────────────────────────────

class BaseEntity(BaseModel):
    """Base model for all entity types."""
    # [Include full BaseEntity definition from above]
    pass


# ──────────────────────────────────────────────────────────────
# ENTITY TYPE MODELS (Discriminated Union)
# ──────────────────────────────────────────────────────────────

class PersonEntity(BaseEntity):
    # [Include full PersonEntity definition from above]
    pass

class EventEntity(BaseEntity):
    # [Include full EventEntity definition from above]
    pass

# [Include all other entity type models]


class Entity(BaseModel):
    """Polymorphic entity model using discriminated union."""
    entity: Union[
        PersonEntity,
        EventEntity,
        PlaceEntity,
        SubjectConceptEntity,
        OrganizationEntity,
        PeriodEntity,
        WorkEntity,
        MaterialEntity,
        ObjectEntity
    ] = Field(
        ...,
        discriminator='entity_type',
        description="Entity with type-specific validation"
    )


# ──────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────

def validate_entity(entity_data: dict) -> Entity:
    """
    Validate a single entity against Pydantic schema.
    
    Args:
        entity_data: Dictionary with entity properties
        
    Returns:
        Validated Entity model
        
    Raises:
        ValidationError: If entity fails validation
    """
    return Entity(**entity_data)


def validate_entity_batch(entities: list[dict]) -> tuple[list[Entity], list[dict]]:
    """
    Validate a batch of entities, separating valid from invalid.
    
    Args:
        entities: List of entity dictionaries
        
    Returns:
        Tuple of (valid_entities, validation_errors)
    """
    valid = []
    errors = []
    
    for i, entity_data in enumerate(entities):
        try:
            validated = validate_entity(entity_data)
            valid.append(validated)
        except Exception as e:
            errors.append({
                "index": i,
                "entity_cipher": entity_data.get("entity_cipher", "UNKNOWN"),
                "error": str(e)
            })
    
    return valid, errors


# ──────────────────────────────────────────────────────────────
# JSON SCHEMA GENERATION
# ──────────────────────────────────────────────────────────────

def generate_entity_schema() -> dict:
    """Generate OpenAPI-compliant JSON schema for all entity types."""
    return Entity.model_json_schema()


if __name__ == "__main__":
    # Example usage
    schema = generate_entity_schema()
    print(f"Generated schema for {len(schema['$defs'])} entity types")
```

### File: `scripts/models/claims.py`

```python
"""
Pydantic models for Chrystallum claim validation.

Discriminated union for claim analysis layers:
  - InSituClaim: Ancient/historical assertions
  - RetrospectiveClaim: Modern scholarly interpretations

Usage:
  from scripts.models.claims import FacetClaim, InSituClaim, RetrospectiveClaim
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Union, Optional
from datetime import datetime
import re


# ──────────────────────────────────────────────────────────────
# BASE CLAIM MODEL
# ──────────────────────────────────────────────────────────────

class BaseFacetClaim(BaseModel):
    """Base model for all claim types."""
    # [Include full BaseFacetClaim definition from above]
    pass


# ──────────────────────────────────────────────────────────────
# CLAIM TYPE MODELS (Discriminated Union)
# ──────────────────────────────────────────────────────────────

class InSituClaim(BaseFacetClaim):
    # [Include full InSituClaim definition from above]
    pass


class RetrospectiveClaim(BaseFacetClaim):
    # [Include full RetrospectiveClaim definition from above]
    pass


class FacetClaim(BaseModel):
    """Polymorphic claim model using discriminated union."""
    claim: Union[InSituClaim, RetrospectiveClaim] = Field(
        ...,
        discriminator='analysis_layer',
        description="Claim with analysis-layer-specific validation"
    )


# ──────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────

def validate_claim(claim_data: dict) -> FacetClaim:
    """Validate a single claim against Pydantic schema."""
    return FacetClaim(**claim_data)


def validate_claim_batch(claims: list[dict]) -> tuple[list[FacetClaim], list[dict]]:
    """Validate a batch of claims, separating valid from invalid."""
    valid = []
    errors = []
    
    for i, claim_data in enumerate(claims):
        try:
            validated = validate_claim(claim_data)
            valid.append(validated)
        except Exception as e:
            errors.append({
                "index": i,
                "cipher": claim_data.get("cipher", "UNKNOWN"),
                "error": str(e)
            })
    
    return valid, errors
```

---

## Usage Examples

### Validate Entity Before Neo4j Write

```python
from scripts.models.entities import Entity, PersonEntity

# Entity data from SCA
entity_data = {
    "entity_type": "PERSON",
    "entity_cipher": "ent_per_Q1048",
    "qid": "Q1048",
    "namespace": "wd",
    "label_en": "Julius Caesar",
    "birth_date": "-0100-07-12",
    "death_date": "-0044-03-15",
    "occupation": ["Q82955", "Q19546"],  # Politician, General
    "is_temporal_anchor": False
}

try:
    # Validate before write
    validated_entity = Entity(**entity_data)
    
    # If validation passes, write to Neo4j
    # neo4j_driver.write_entity(validated_entity.entity)
    
except Exception as e:
    print(f"Validation failed: {e}")
    # Log error, don't write to Neo4j
```

### Validate TemporalAnchor Entity

```python
from scripts.models.entities import OrganizationEntity

# Roman Republic with temporal properties
entity_data = {
    "entity_type": "ORGANIZATION",
    "entity_cipher": "ent_org_Q17167",
    "qid": "Q17167",
    "namespace": "wd",
    "label_en": "Roman Republic",
    "is_temporal_anchor": True,
    "temporal_scope": "-0509/-0027",
    "temporal_start_year": -509,
    "temporal_end_year": -27,
    "temporal_calendar": "julian"
}

try:
    validated = OrganizationEntity(**entity_data)
    print(f"✅ Validated: {validated.label_en} (temporal anchor)")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

### Validate In-Situ Claim

```python
from scripts.models.claims import InSituClaim

claim_data = {
    "cipher": "fclaim_pol_a1b2c3d4e5f6g7h8",
    "subject_entity_cipher": "ent_per_Q1048",
    "facet_id": "POLITICAL",
    "subjectconcept_cipher": "ent_sub_Q17167",
    "analysis_layer": "in_situ",
    "source_family": "ancient_primary",
    "uses_modern_theory": False,
    "claim_role": "action",
    "source_work_qid": "Q47461",  # Polybius
    "passage_locator": "Hist.2.14",
    "confidence": 0.92
}

try:
    validated = InSituClaim(**claim_data)
    print(f"✅ Validated in-situ claim: {validated.cipher}")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

### Validate Retrospective Claim

```python
from scripts.models.claims import RetrospectiveClaim

claim_data = {
    "cipher": "fclaim_pol_x9y8z7w6v5u4t3s2",
    "subject_entity_cipher": "ent_per_Q1048",
    "facet_id": "POLITICAL",
    "subjectconcept_cipher": "ent_sub_Q17167",
    "analysis_layer": "retrospective",
    "source_family": "modern_scholarship",
    "uses_modern_theory": True,
    "target_claim_ciphers": [
        "fclaim_pol_a1b2c3d4e5f6g7h8",  # In-situ claim being interpreted
        "fclaim_pol_b2c3d4e5f6g7h8i9"
    ],
    "methodology": "principal-agent theory",
    "source_work_qid": "Q98765432",  # Modern scholarly work
    "scholar_qid": "Q12345678",
    "confidence": 0.75
}

try:
    validated = RetrospectiveClaim(**claim_data)
    print(f"✅ Validated retrospective claim: {validated.cipher}")
    print(f"   Interprets {len(validated.target_claim_ciphers)} in-situ claims")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

---

## Integration with Claims Manager

### Validation Gate Pattern

```python
from scripts.models.claims import FacetClaim, validate_claim_batch

def write_claims_to_neo4j(claims_data: list[dict]) -> dict:
    """
    Write claims to Neo4j with Pydantic validation gate.
    
    Returns:
        Statistics on valid/invalid claims
    """
    # Validation gate: Belt layer
    valid_claims, validation_errors = validate_claim_batch(claims_data)
    
    if validation_errors:
        log.warning(f"Validation rejected {len(validation_errors)} claims")
        for error in validation_errors:
            log.error(f"  Claim {error['cipher']}: {error['error']}")
    
    # Write valid claims to Neo4j: Suspenders layer (constraints enforce)
    written_count = 0
    for claim in valid_claims:
        try:
            neo4j_driver.write_claim(claim.claim)
            written_count += 1
        except Exception as e:
            log.error(f"Neo4j write failed for {claim.claim.cipher}: {e}")
    
    return {
        "total_submitted": len(claims_data),
        "validation_passed": len(valid_claims),
        "validation_failed": len(validation_errors),
        "neo4j_written": written_count,
        "neo4j_failed": len(valid_claims) - written_count
    }
```

---

## References

### Internal Documents
- **ENTITY_CIPHER_FOR_VERTEX_JUMPS.md** — Three-tier cipher model
- **CLAIM_ID_ARCHITECTURE.md** — Tier 3 claim cipher specification
- **NEO4J_SCHEMA_DDL_COMPLETE.md** — Database constraints (suspenders layer)

### Pydantic Documentation
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest)
- [Discriminated Unions](https://docs.pydantic.dev/2.0/usage/types/unions/)
- [Field Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [JSON Schema Generation](https://docs.pydantic.dev/latest/concepts/json_schema/)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| **Feb 22, 2026** | **1.0** | **Initial specification with entity and claim discriminated unions, temporal anchor validation, belt-and-suspenders pattern** |

---

**Document Status:** ✅ Canonical Reference (Feb 2026)  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026
