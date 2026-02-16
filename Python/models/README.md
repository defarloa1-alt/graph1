# Chrystallum Models Package

**Registry-Backed Validation for Claims, Facets, and Relationships**

## Overview

The `chrystallum.models` package provides:

1. **Registry-driven validation**: Pydantic models that validate against canonical facet and relationship registries
2. **Type safety**: Enforces facet keys and relationship types at application level
3. **Neo4j constraints**: Generates Cypher statements for database-level enforcement
4. **Extensibility**: Easy to add new validators and constraint types

## Quick Start

### 1. Initialize the Registry

```python
from pathlib import Path
from chrystallum.models import initialize_registry

# Call once at application startup
facet_path = Path("Facets/facet_registry_master.json")
rel_path = Path("Relationships/relationship_types_registry_master.csv")
initialize_registry(facet_path, rel_path)
```

### 2. Create and Validate Models

```python
from chrystallum.models import Claim, FacetAssignment, RelationshipAssertion

# Create a claim with facets and relationships
claim = Claim(
    claim_id="claim_00001",
    cipher="sha256_abc123def456...",
    content="Julius Caesar commanded legions during the conquest of Gaul",
    source_id="source_001_plb_001",
    facets=[
        FacetAssignment(facet="military", confidence=0.95),
        FacetAssignment(facet="political", confidence=0.85),
    ],
    relationships=[
        RelationshipAssertion(
            rel_type="COMMANDED",
            subject_id="Q1048",      # Julius Caesar
            object_id="Q123456",     # Military unit
            confidence=0.92,
            temporal_scope="49-48 BCE"
        )
    ],
    created_by="seed_agent_001"
)

# Valid! Created automatically
print(f"✓ Claim {claim.claim_id} with cipher {claim.cipher[:30]}...")
```

### 3. Invalid Data is Rejected

```python
# This raises ValidationError - invalid facet
try:
    bad_claim = Claim(
        claim_id="claim_bad",
        cipher="...",
        facets=[FacetAssignment(facet="INVALID_FACET", confidence=0.5)],
        ...
    )
except Exception as e:
    print(f"✗ Validation error: {e}")
    # Output: "Invalid facet 'INVALID_FACET'. Must be one of: archaeological, artistic, ..."
```

## Components

### 1. Registry Loader (`registry_loader.py`)

Loads and caches canonical facet and relationship registries:

```python
from chrystallum.models import RegistryLoader

loader = RegistryLoader(facet_json_path, relationship_csv_path)

# Query registries
facets = loader.get_canonical_facet_keys()  # Set of 18 facet keys
relationships = loader.get_canonical_relationship_types()  # Set of 310 types

# Validate
is_valid_facet = loader.is_valid_facet_key("military")  # True
is_valid_rel = loader.is_valid_relationship_type("COMMANDED")  # True

# Statistics
summary = loader.get_summary()
print(f"18 facets, 310 relationships")
```

### 2. Pydantic Models (`validation_models.py`)

#### FacetAssignment

Represents a facet classification on a claim:

```python
facet = FacetAssignment(
    facet="diplomatic",          # Must be canonical (case-insensitive)
    confidence=0.85,             # 0.0-1.0
    rationale="Treaty negotiation mentioned",
    assigned_by="facet_specialist_diplomatic_01"
)
```

#### FacetAssessment

Detailed assessment by a facet specialist:

```python
assessment = FacetAssessment(
    assessment_id="assess_001_00001",
    facet="diplomatic",
    claim_id="claim_00001",
    score=0.85,
    rationale="Clear diplomatic negotiation between Rome and Carthage",
    evaluated_by="facet_specialist_diplomatic_01"
)
```

#### RelationshipAssertion

A relationship extracted from a claim:

```python
rel = RelationshipAssertion(
    rel_type="COMMANDED",        # Must be canonical (uppercase)
    subject_id="Q1048",
    object_id="Q123456",
    confidence=0.92,
    temporal_scope="49-48 BCE",
    geographic_scope="Rome",
    source_id="source_001_plb_001"
)
```

#### RelationshipEdge

An edge for Neo4j ingestion:

```python
edge = RelationshipEdge(
    edge_id="edge_001_00001",
    rel_type="COMMANDED",
    source_node_id="Q1048",
    target_node_id="Q123456",
    confidence=0.92,
    cipher="sha256_xyz789...",  # Optional
    version="1.0"
)
```

#### Claim

A complete claim with facets and relationships:

```python
claim = Claim(
    claim_id="claim_00001",
    cipher="sha256_abc123...",           # Content-addressable ID
    content="The main claim text",
    source_id="source_001_plb_001",
    facets=[...],                        # List of FacetAssignment
    relationships=[...],                 # List of RelationshipAssertion
    confidence=0.85,
    status=LifecycleStatus.DRAFT,
    created_by="seed_agent_001"
)
```

### 3. Neo4j Constraints (`neo4j_constraints.py`)

Generates Cypher statements for database enforcement:

```python
from chrystallum.models import RegistryLoader, Neo4jConstraintGenerator

loader = RegistryLoader(facet_path, rel_path)
generator = Neo4jConstraintGenerator(loader)

# Full constraints document
constraints_cypher = generator.generate_all_constraints()

# Validation queries (audit existing data)
validation_cypher = generator.generate_validation_cypher()

# Migration script (for schema updates)
migration_cypher = generator.generate_migration_script("2026-02-12", "2026-02-16")

# Individual statements
for stmt in generator.get_constraint_statements():
    session.run(stmt)  # Execute in Neo4j
```

## Enforcement Layers

### Layer 1: Application Validation (Pydantic)

✓ Fastest  
✓ Best error messages  
✓ Prevents invalid data creation

```python
claim = Claim(...)  # Raises ValidationError immediately if invalid
```

### Layer 2: Database Constraints (Neo4j)

✓ Backup enforcement  
✓ Prevents circumvention via direct DB access  
✓ Generates warnings for duplicate keys

```cypher
// In Neo4j
CREATE CONSTRAINT facet_key_unique IF NOT EXISTS
FOR (f:FacetCategory) REQUIRE f.key IS UNIQUE;

CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.cipher IS UNIQUE;
```

### Layer 3: Audit & Validation

✓ Periodic checks  
✓ Data migration validation  
✓ Compliance reporting

```cypher
// Check for invalid facet keys
MATCH (fa:FacetAssessment) 
WHERE NOT fa.facet IN ['archaeological', 'artistic', ...]
RETURN fa.assessment_id, fa.facet;
```

## Enums

```python
from chrystallum.models import LifecycleStatus, DirectionalityType, ImplementationStatus

# Claim/Assessment status
LifecycleStatus.ACTIVE
LifecycleStatus.DEPRECATED
LifecycleStatus.ARCHIVED
LifecycleStatus.DRAFT

# Relationship directionality (informational, for docs)
DirectionalityType.FORWARD
DirectionalityType.INVERSE
DirectionalityType.BIDIRECTIONAL
DirectionalityType.UNIDIRECTIONAL

# Relationship implementation status
ImplementationStatus.IMPLEMENTED
ImplementationStatus.CANDIDATE
ImplementationStatus.DEPRECATED
```

## Running Tests

```bash
# From project root
python Python/models/test_models.py
```

Output:
```
======================================================================
TEST SUMMARY
======================================================================
✓ PASS: Registry Loading
✓ PASS: Facet Validation
✓ PASS: Relationship Validation
✓ PASS: Claim Validation
✓ PASS: Facet Assessment
✓ PASS: Neo4j Constraints

Total: 6/6 tests passed
```

## Generated Files

Running the tests auto-generates validation and constraint files:

```
Cypher/schema/
  ├── constraints_chrystallum_generated.cypher
  │   └── CREATE CONSTRAINT statements for Neo4j
  ├── validation_chrystallum_generated.cypher
  │   └── Audit queries to check existing data
  └── migration_2026_02_12_to_2026_02_16.cypher
      └── Migration script for schema updates
```

## Integration Example

### Flask/Fastapi Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from chrystallum.models import initialize_registry, Claim

app = FastAPI()

# Startup
@app.on_event("startup")
async def startup():
    initialize_registry(facet_path, rel_path)

# Endpoint
@app.post("/claims/")
async def create_claim(claim_data: dict):
    try:
        claim = Claim(**claim_data)
        # Persist to Neo4j
        db.save_claim(claim)
        return {"claim_id": claim.claim_id, "cipher": claim.cipher}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

### CLI Tool

```python
#!/usr/bin/env python
# claims_validator.py

from pathlib import Path
import json
from chrystallum.models import initialize_registry, Claim

def validate_claim_file(filepath):
    """Validate a JSON claim against schema."""
    initialize_registry(
        Path("Facets/facet_registry_master.json"),
        Path("Relationships/relationship_types_registry_master.csv")
    )
    
    with open(filepath) as f:
        data = json.load(f)
    
    try:
        claim = Claim(**data)
        print(f"✓ Valid: {claim.claim_id}")
        return True
    except Exception as e:
        print(f"✗ Invalid: {e}")
        return False

if __name__ == "__main__":
    import sys
    validate_claim_file(sys.argv[1])
```

## Architecture

```
chrystallum.models/
├── __init__.py                 # Public API
├── registry_loader.py          # Loads JSON/CSV registries
├── validation_models.py        # Pydantic models + registry linkage
├── neo4j_constraints.py        # Generates Cypher constraints
└── test_models.py              # Comprehensive test suite
```

## Design Principles

1. **Registry as Source of Truth**: All validation references the canonical registries
2. **Fail Fast**: Invalid data rejected at creation time, not later
3. **Audit Trail**: All validation errors include descriptive messages
4. **Multi-Layer Enforcement**: Pydantic + Neo4j + periodic validation
5. **Extensible**: Easy to add new validators without changing core logic

## Future Enhancements

- [ ] JSON Schema export for OpenAPI/Swagger
- [ ] GraphQL schema generation
- [ ] Bulk validation CLI tool
- [ ] Registry diffing (detect changes between versions)
- [ ] Automatic Neo4j constraint application
- [ ] Web UI for registry browser/validator

## References

- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Neo4j Constraints](https://neo4j.com/docs/cypher-manual/current/administration/constraints/)
- [Chrystallum Architecture](../Key%20Files/2-12-26%20Chrystallum%20Architecture%20-%20CONSOLIDATED.md)
  - Section 3.3: Facets  
  - Section 7: Relationships  
  - ADR-001: Claim Identity (Appendix U)  
  - ADR-004: Facet Canonicalization (Appendix W)  
  - ADR-005: Federated Claims Signing (Appendix X)

---

**Version**: 0.1.0  
**Status**: Operational (Priority 1 Complete)  
**Last Updated**: 2026-02-16
