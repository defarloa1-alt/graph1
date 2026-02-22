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

### 3. Canonicalization (`canonicalization.py`)

**NEW in Priority 4**: Ensures reproducible claim ciphers across federated systems.

#### Why Canonicalization?

Different systems may have variations in:
- Unicode representation: `café` (é as 1 char vs e+́ combining)
- Whitespace: spaces vs tabs vs NBSP
- Float precision: `0.95` vs `0.9500000001`
- Key ordering: `{"b":2,"a":1}` vs `{"a":1,"b":2}`

Without canonicalization, **identical claims produce different ciphers** → duplication, can't deduplicate.

#### Auto-Compute Claim Cipher (Recommended)

```python
from chrystallum.models import Claim

# Create claim with auto-computed canonical cipher
claim = Claim.create_with_cipher(
    claim_id="claim_001",
    content="Julius Caesar crossed the Rubicon in 49 BCE",
    source_id="plutarch_lives_caesar_ch32",
    created_by="extraction_agent_v1",
    facets=[
        FacetAssignment(facet="military", confidence=0.95),
        FacetAssignment(facet="geographic", confidence=0.90)
    ],
    confidence=0.92
)

# Cipher is automatically computed and guaranteed valid
assert claim.verify_cipher()  # ✅ Always True
print(f"Cipher: {claim.cipher}")
```

#### Verify Existing Cipher

```python
# Load claim from database
claim = Claim(**claim_data)

# Verify cipher integrity
if claim.verify_cipher():
    print("✓ Cipher is valid")
else:
    print("✗ WARNING: Cipher is invalid (tampering detected)")
```

#### Detect Duplicate Claims Across Systems

```python
# System A discovers a fact
claim_a = Claim.create_with_cipher(
    claim_id="system_a_claim_123",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_a"
)

# System B independently discovers the same fact
claim_b = Claim.create_with_cipher(
    claim_id="system_b_claim_456",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_b"
)

# Ciphers match → same logical claim
if claim_a.cipher == claim_b.cipher:
    print("✓ Duplicate claim detected - can merge/deduplicate")
```

#### Low-Level Canonicalization Functions

```python
from chrystallum.models import (
    normalize_unicode,
    normalize_whitespace,
    normalize_float,
    canonicalize_dict,
    compute_claim_cipher
)

# Normalize text
text1 = "café"  # é as single character
text2 = "café"  # é as e + combining accent
assert normalize_unicode(text1) == normalize_unicode(text2)  # ✅ Same

# Normalize whitespace
text = "  Hello   world  "
assert normalize_whitespace(text) == "Hello world"  # ✅ Collapsed

# Normalize float
assert normalize_float(0.95) == normalize_float(0.9500000001)  # ✅ Same

# Normalize dict (sorted keys)
dict1 = {"b": 2, "a": 1}
dict2 = {"a": 1, "b": 2}
assert canonicalize_dict(dict1) == canonicalize_dict(dict2)  # ✅ Same

# Compute cipher directly
cipher = compute_claim_cipher(
    content="Julius Caesar crossed the Rubicon",
    metadata={"source_id": "source_001", "facets": [], "relationships": []}
)
assert len(cipher) == 64  # SHA256 = 64 hex chars
```

#### Content-Addressable Design

**What's included in cipher**:
- `content`: Main claim text
- `source_id`: Source document identifier
- `facets`: List of facet keys (sorted)
- `relationships`: List of relationship assertions (sorted)

**What's excluded from cipher**:
- `claim_id`: Generated identifier (not content)
- `created_by`: Agent identifier (metadata)
- `created_at`: Timestamp (metadata)
- `confidence`: Assessment score (metadata)

**Rationale**: Two agents discovering the same fact from the same source should produce **identical ciphers**, regardless of when/who/how confident.

#### Cross-System Reproducibility

```python
# System 1: Clean input
claim1 = Claim.create_with_cipher(
    claim_id="system1_001",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_1"
)

# System 2: Extra whitespace, different key order
claim2 = Claim.create_with_cipher(
    claim_id="system2_001",
    content="  Julius   Caesar crossed the Rubicon  ",  # Extra spaces
    source_id="source_001",
    created_by="agent_2"
)

# Ciphers are IDENTICAL due to canonicalization
assert claim1.cipher == claim2.cipher  # ✅ True
print("✓ Federation-ready: reproducible ciphers across systems")
```

### 4. Neo4j Constraints (`neo4j_constraints.py`)

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

### Core Validation Tests

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

### Canonicalization Tests

```bash
python Python/models/test_canonicalization.py
```

Output:
```
======================================================================
CANONICALIZATION TEST SUITE
======================================================================
✓ PASS: Unicode Normalization
✓ PASS: Whitespace Normalization
✓ PASS: DateTime Normalization
✓ PASS: Float Normalization
✓ PASS: Dict Canonicalization
✓ PASS: Canonical JSON
✓ PASS: Claim Canonicalization
✓ PASS: Cipher Reproducibility
✓ PASS: Edge Cases
✓ PASS: Cross-System Reproducibility

RESULTS: 10 passed, 0 failed
✅ Ready for federation
```

### Claim Cipher Integration Tests

```bash
python Python/models/test_claim_cipher.py
```

Output:
```
======================================================================
CLAIM CIPHER INTEGRATION TEST SUITE
======================================================================
✓ PASS: Compute Canonical Cipher
✓ PASS: Verify Cipher
✓ PASS: Create With Cipher Factory Method
✓ PASS: Cipher Uniqueness

Total: 4/6 core tests passed (2 require registry files)
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

## Changelog

### v0.2.0 (2026-02-17) - Priority 4 Complete

**NEW**: Canonicalization framework for reproducible claim ciphers
- ✅ `canonicalization.py`: Normalize Unicode, whitespace, floats, dicts, dates
- ✅ `Claim.create_with_cipher()`: Factory method with auto-computed cipher
- ✅ `Claim.compute_canonical_cipher()`: Compute cipher from claim content
- ✅ `Claim.verify_cipher()`: Verify cipher integrity
- ✅ Cross-system reproducibility: Identical content → identical cipher
- ✅ Federation-ready: Content-addressable claim identity
- ✅ 10/10 canonicalization tests passing
- ✅ 4/6 integration tests passing (core functionality complete)

### v0.1.0 (2026-02-16) - Priority 1 & 2 Complete

**Initial implementation**:
- ✅ Registry-backed validation (Pydantic)
- ✅ Neo4j constraint generation
- ✅ V1 relationship kernel (25 baseline types)
- ✅ All 310 relationship types available immediately
- ✅ 6/6 validation tests passing

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

**Version**: 0.2.0  
**Status**: Operational (Priorities 1, 2, 4 Complete)  
**Last Updated**: 2026-02-17
