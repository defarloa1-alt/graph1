# Tier 3 Claim Cipher Architecture: Qualifier Integration Addendum

**Created:** February 22, 2026  
**Status:** Canonical Reference - Addendum to NEO4J_SCHEMA_DDL_COMPLETE.md  
**Revision:** 1.0  
**Related:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md, CLAIM_ID_ARCHITECTURE.md, REQ-DATA-003

---

## Purpose

This document addresses 4 architectural gaps identified between REQ-DATA-003 (Cipher-Eligible Qualifiers Registry) and the initial DDL/Pydantic specifications. It provides:

1. **Tier 3 claim cipher constraints** (missing from NEO4J_SCHEMA_DDL_COMPLETE.md)
2. **Qualifier validation models** (missing from PYDANTIC_MODELS_SPECIFICATION.md)
3. **ADR-003: Temporal Scope Derivation** (resolves confusion between qualifiers and temporal_scope)
4. **Qualifier normalization specification** (canonical algorithm)

---

## Table of Contents

1. [ADR-003: Temporal Scope Derivation from Qualifiers](#adr-003-temporal-scope-derivation-from-qualifiers)
2. [Tier 3 Claim Schema with Qualifiers](#tier-3-claim-schema-with-qualifiers)
3. [Neo4j Constraints and Indexes](#neo4j-constraints-and-indexes)
4. [Pydantic Qualifier Validation Models](#pydantic-qualifier-validation-models)
5. [Qualifier Normalization Algorithm](#qualifier-normalization-algorithm)
6. [Complete DDL Addendum](#complete-ddl-addendum)

---

## ADR-003: Temporal Scope Derivation from Qualifiers

**Status:** Accepted (February 22, 2026)

### Context

Three conflicting temporal patterns exist:

| Source | Pattern |
|--------|---------|
| **REQ-DATA-003** | Wikidata qualifiers P580/P582/P585 included in Tier 3 cipher |
| **CLAIM_ID_ARCHITECTURE.md** | `temporal_scope` field in cipher formula |
| **ADR-002 (TemporalAnchor)** | Entity-level `temporal_scope` + integer year fields |

**Confusion:**
- Are Wikidata qualifiers **synonymous with** claim-level `temporal_scope`?
- Or are they **separate** concepts?
- How do we avoid redundancy?

### Decision

**Wikidata qualifiers ARE THE SOURCE for claim-level `temporal_scope`.**

**Derivation Rule:**
```python
# Tier 3 FacetClaim temporal_scope DERIVED FROM qualifiers:
if qualifier_p580 and qualifier_p582:
    temporal_scope = f"{qualifier_p580}/{qualifier_p582}"  # Interval
elif qualifier_p585:
    temporal_scope = qualifier_p585  # Point in time
else:
    temporal_scope = None  # No temporal bounds

# Example:
# P580=-59, P582=-58 → temporal_scope="-0059/-0058"
# P585=-44-03-15 → temporal_scope="-0044-03-15"
```

**Cipher Inclusion:**
- Include `temporal_scope` (derived field) in cipher hash
- Do NOT include raw qualifiers P580/P582/P585 separately
- Store raw qualifiers as properties for provenance

**Rationale:**
1. **Single Source of Truth:** Qualifiers are authoritative (from Wikidata)
2. **Canonical Format:** `temporal_scope` normalizes different qualifier patterns
3. **Backward Compatibility:** Matches CLAIM_ID_ARCHITECTURE.md cipher formula
4. **Deduplication:** Two claims with same temporal bounds → same `temporal_scope` → same cipher

### Consequences

**Benefits:**
- ✅ Resolves qualifier vs temporal_scope confusion
- ✅ Maintains compatibility with CLAIM_ID_ARCHITECTURE.md
- ✅ Enables temporal range queries via derived field
- ✅ Preserves Wikidata qualifiers for provenance

**Constraints:**
- All FacetClaim nodes MUST derive `temporal_scope` from qualifiers if present
- Pydantic validators MUST enforce derivation logic
- SCA/SFA agents MUST populate qualifiers from Wikidata before deriving `temporal_scope`

**Migration:**
- Existing claims without qualifiers: keep existing `temporal_scope` (manually set)
- New claims from Wikidata: MUST derive `temporal_scope` from P580/P582/P585

---

## Tier 3 Claim Schema with Qualifiers

### Critical Architectural Decision: Cipher vs Content Hash

**Issue:** Current Tier 3 cipher includes `source_qid` and `passage_locator` in hash input.

**Consequence:** Same assertion from different sources = different ciphers

**Example:**
```
Plutarch: "Caesar was consul in 59 BCE"
  → cipher: fclaim_pol_abc123... (includes source_qid=Q193291)

Suetonius: "Caesar was consul in 59 BCE"
  → cipher: fclaim_pol_xyz789... (includes source_qid=Q1385)

Problem: Same fact, different ciphers — can't detect cross-source corroboration!
```

**Solution:** Add `content_hash` field (source-agnostic) alongside `cipher` (source-specific)

```python
def build_content_hash(subject_qid, property_pid, object_qid, facet_id, temporal_scope, qualifiers):
    """
    Content hash for cross-source corroboration detection.
    Excludes source_qid and passage_locator.
    """
    data = f"{subject_qid}|{property_pid}|{object_qid}|{facet_id}|{temporal_scope}|{qualifiers}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def build_claim_with_dual_identity(subject, property, object, facet, temporal, qualifiers, source, passage):
    """Build claim with both cipher (source-specific) and content_hash (source-agnostic)"""
    
    # Cipher: Unique per source (provenance distinct)
    cipher = build_claim_cipher_with_qualifiers(
        subject, property, object, facet, qualifiers, source, passage
    )
    
    # Content hash: Same for corroborating sources
    content_hash = build_content_hash(
        subject, property, object, facet, temporal, qualifiers
    )
    
    return {
        "cipher": cipher,                    # Unique claim ID (provenance)
        "content_hash": content_hash,        # Assertion identity (corroboration)
        "subject_qid": subject,
        "property_pid": property,
        "object_qid": object,
        # ... other properties
    }
```

**Usage:**
```cypher
// Find all sources that corroborate same assertion
MATCH (c:FacetClaim {content_hash: "a1b2c3d4e5f6g7h8"})
RETURN c.source_qid, c.cipher, c.confidence
// Returns: Plutarch (0.85), Suetonius (0.90), Cassius Dio (0.75)
// → Aggregate confidence: 0.95 (3 sources agree)
```

**Dual Identity Pattern:**
- `cipher` = unique claim ID (includes source) → provenance tracking
- `content_hash` = assertion ID (excludes source) → corroboration detection

---

### FacetClaim Node Schema (Complete with Dual Identity)

```cypher
(:FacetClaim {
  // ──────────────────────────────────────────────
  // DUAL IDENTITY (Provenance + Corroboration)
  // ──────────────────────────────────────────────
  cipher: "fclaim_pol_a1b2c3d4e5f6g7h8",           // PRIMARY KEY (source-specific)
  content_hash: "x9y8z7w6v5u4t3s2",                 // Assertion ID (source-agnostic)
  
  // ──────────────────────────────────────────────
  // CORE ASSERTION (TRIPLE)
  // ──────────────────────────────────────────────
  subject_entity_cipher: "ent_per_Q1048",        // Tier 1 join key
  wikidata_pid: "P39",                            // Wikidata property
  object_qid: "Q39686",                           // Object entity QID
  
  // ──────────────────────────────────────────────
  // CONTEXT DIMENSIONS
  // ──────────────────────────────────────────────
  facet_id: "POLITICAL",                          // 1 of 18 facets
  subjectconcept_cipher: "ent_sub_Q17167",       // Anchoring SubjectConcept
  
  // ──────────────────────────────────────────────
  // TEMPORAL SCOPE (DERIVED FROM QUALIFIERS)
  // ──────────────────────────────────────────────
  temporal_scope: "-0059/-0058",                  // Canonical ISO interval (in cipher)
  
  // ──────────────────────────────────────────────
  // CIPHER-ELIGIBLE QUALIFIERS (5 PIDs)
  // Stored for provenance, normalized values
  // ──────────────────────────────────────────────
  qualifier_p580_normalized: "+00-59",            // Start time (ISO normalized)
  qualifier_p582_normalized: "+00-58",            // End time (ISO normalized)
  qualifier_p585_normalized: null,                // Point in time (if used)
  qualifier_p276_qid: null,                       // Location QID
  qualifier_p1545_ordinal: 1,                     // Series ordinal (zero-padded)
  
  // ──────────────────────────────────────────────
  // METADATA QUALIFIERS (EXCLUDED FROM CIPHER)
  // Stored as JSON for flexibility
  // ──────────────────────────────────────────────
  metadata_qualifiers: {
    "P1480": "inferred",                          // Sourcing circumstances
    "P459": "reasoned from evidence",             // Determination method
    "P3831": "consul",                            // Object role
    "P1810": "Gaius Iulius Caesar"               // Subject named as
  },
  
  // ──────────────────────────────────────────────
  // SOURCE PROVENANCE (IN CIPHER)
  // ──────────────────────────────────────────────
  source_work_qid: "Q47461",                      // Polybius
  passage_locator: "Hist.2.14",                   // Citation
  
  // ──────────────────────────────────────────────
  // ANALYSIS LAYER
  // ──────────────────────────────────────────────
  analysis_layer: "in_situ",                      // or "retrospective"
  
  // ──────────────────────────────────────────────
  // MUTABLE METADATA (NOT IN CIPHER)
  // ──────────────────────────────────────────────
  confidence: 0.92,                               // Evidence strength
  created_at: "2026-02-22T10:00:00Z",
  created_by_agent: "political_sfa_001"
})
```

### Property Specifications

| Property | Type | In Cipher? | Purpose |
|----------|------|------------|---------|
| `cipher` | String | N/A (IS cipher) | Tier 3 primary key |
| `subject_entity_cipher` | String | ✅ Yes | Subject of assertion |
| `wikidata_pid` | String | ✅ Yes | Wikidata property (relationship type) |
| `object_qid` | String | ✅ Yes | Object of assertion |
| `facet_id` | String | ✅ Yes | Facet dimension |
| `subjectconcept_cipher` | String | ❌ No | Anchoring context (not identity) |
| `temporal_scope` | String | ✅ Yes | **Derived from qualifiers** |
| `qualifier_p580_normalized` | String | ❌ No (used to derive temporal_scope) | Start time (ISO) |
| `qualifier_p582_normalized` | String | ❌ No (used to derive temporal_scope) | End time (ISO) |
| `qualifier_p585_normalized` | String | ❌ No (used to derive temporal_scope) | Point in time (ISO) |
| `qualifier_p276_qid` | String | ✅ Yes (if location identity) | Location qualifier |
| `qualifier_p1545_ordinal` | Integer | ✅ Yes (if series identity) | Ordinal (1st, 2nd, 3rd) |
| `metadata_qualifiers` | JSON | ❌ No | Non-identity qualifiers |
| `source_work_qid` | String | ✅ Yes | Source document |
| `passage_locator` | String | ✅ Yes | Citation within source |
| `analysis_layer` | String | ❌ No | Claim type classification |
| `confidence` | Float | ❌ No | Mutable evidence strength |

---

## Neo4j Constraints and Indexes

### Additional Constraints (Addendum to NEO4J_SCHEMA_DDL_COMPLETE.md)

```cypher
// ═══════════════════════════════════════════════════════════════
// TIER 3 QUALIFIER CONSTRAINTS (REQ-DATA-003)
// ═══════════════════════════════════════════════════════════════

// Note: Qualifiers are OPTIONAL (not all claims have qualifiers)
// Constraints focus on format when present

// No database-level regex constraints (handled in Pydantic)
// Neo4j 5.x constraint syntax doesn't support regex patterns
```

### Additional Indexes (Addendum)

```cypher
// ═══════════════════════════════════════════════════════════════
// TIER 3 QUALIFIER INDEXES
// ═══════════════════════════════════════════════════════════════

// Wikidata triple pattern queries
CREATE INDEX claim_wikidata_triple_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subject_entity_cipher, c.wikidata_pid, c.object_qid);

// Temporal qualifier queries (start time)
CREATE INDEX claim_temporal_start_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p580_normalized);

// Temporal qualifier queries (end time)
CREATE INDEX claim_temporal_end_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p582_normalized);

// Location qualifier queries
CREATE INDEX claim_location_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p276_qid);

// Series ordinal queries (1st vs 2nd consulship)
CREATE INDEX claim_ordinal_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p1545_ordinal);

// Temporal scope queries (derived field)
CREATE INDEX claim_temporal_scope_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.temporal_scope);
```

**Index Rationale:**
- `claim_wikidata_triple_idx`: Find all claims for a specific Wikidata relationship
- `claim_temporal_*_idx`: Enable range queries on temporal qualifiers
- `claim_location_idx`: Find claims at specific locations
- `claim_ordinal_idx`: Distinguish repeated relationships (1st, 2nd consulship)
- `claim_temporal_scope_idx`: Query by derived temporal interval

---

## Pydantic Qualifier Validation Models

### Updated InSituClaim Model

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import datetime
import re


class InSituClaim(BaseFacetClaim):
    """
    In-situ claim with Wikidata qualifier support (REQ-DATA-003).
    """
    
    # Analysis layer discriminator
    analysis_layer: Literal["in_situ"]
    
    # ──────────────────────────────────────────────────────────
    # CIPHER-ELIGIBLE QUALIFIERS (5 PIDs - OPTIONAL)
    # ──────────────────────────────────────────────────────────
    
    # Temporal qualifiers (P580, P582, P585)
    qualifier_p580_normalized: Optional[str] = Field(
        None,
        pattern=r"^[+-]\d{5}(-\d{2}(-\d{2})?)?$",
        description="Start time (ISO 8601, normalized: +00-59 format)"
    )
    
    qualifier_p582_normalized: Optional[str] = Field(
        None,
        pattern=r"^[+-]\d{5}(-\d{2}(-\d{2})?)?$",
        description="End time (ISO 8601, normalized)"
    )
    
    qualifier_p585_normalized: Optional[str] = Field(
        None,
        pattern=r"^[+-]\d{5}(-\d{2}(-\d{2})?)?$",
        description="Point in time (ISO 8601, normalized)"
    )
    
    # Location qualifier (P276)
    qualifier_p276_qid: Optional[str] = Field(
        None,
        pattern=r"^Q\d+$",
        description="Location (Wikidata QID)"
    )
    
    # Series ordinal (P1545)
    qualifier_p1545_ordinal: Optional[int] = Field(
        None,
        ge=1,
        le=999,
        description="Series ordinal (1st, 2nd, 3rd, etc.)"
    )
    
    # ──────────────────────────────────────────────────────────
    # TEMPORAL SCOPE (DERIVED FROM QUALIFIERS)
    # ──────────────────────────────────────────────────────────
    
    temporal_scope: Optional[str] = Field(
        None,
        description="Derived from qualifiers P580/P582/P585 (auto-populated)"
    )
    
    # ──────────────────────────────────────────────────────────
    # METADATA QUALIFIERS (EXCLUDED FROM CIPHER)
    # ──────────────────────────────────────────────────────────
    
    metadata_qualifiers: Optional[dict] = Field(
        None,
        description="Non-cipher qualifiers (P1480, P459, P3831, etc.)"
    )
    
    # ──────────────────────────────────────────────────────────
    # VALIDATORS
    # ──────────────────────────────────────────────────────────
    
    @model_validator(mode='after')
    def derive_temporal_scope(self):
        """
        ADR-003: Derive temporal_scope from qualifiers.
        
        Rules:
        - P580 + P582 → interval format: "-0059/-0058"
        - P585 alone → point format: "-0044-03-15"
        - No temporal qualifiers → temporal_scope = None
        """
        if self.qualifier_p580_normalized and self.qualifier_p582_normalized:
            # Interval: start/end
            self.temporal_scope = f"{self.qualifier_p580_normalized}/{self.qualifier_p582_normalized}"
        
        elif self.qualifier_p585_normalized:
            # Point in time
            self.temporal_scope = self.qualifier_p585_normalized
        
        # If temporal_scope manually set but qualifiers missing, keep it
        # (backward compatibility for non-Wikidata claims)
        
        return self
    
    @field_validator('qualifier_p580_normalized', 'qualifier_p582_normalized', 'qualifier_p585_normalized')
    @classmethod
    def validate_iso_format(cls, v):
        """Ensure temporal qualifiers are ISO 8601 normalized."""
        if v is None:
            return v
        
        # Pattern: +00-59 or -0044-03-15
        pattern = r"^[+-]\d{5}(-\d{2}(-\d{2})?)?$"
        if not re.match(pattern, v):
            raise ValueError(
                f"Temporal qualifier must be ISO 8601 normalized: {v}. "
                f"Expected format: +00-59 or -0044-03-15"
            )
        return v
    
    @field_validator('metadata_qualifiers')
    @classmethod
    def validate_metadata_pids(cls, v):
        """Ensure metadata qualifiers don't include cipher-eligible PIDs."""
        if v is None:
            return v
        
        CIPHER_ELIGIBLE = {"P580", "P582", "P585", "P276", "P1545"}
        for pid in v.keys():
            if pid in CIPHER_ELIGIBLE:
                raise ValueError(
                    f"Qualifier {pid} is cipher-eligible. "
                    f"Use qualifier_{pid.lower()}_* field instead of metadata_qualifiers."
                )
        return v


class RetrospectiveClaim(BaseFacetClaim):
    """
    Retrospective claim (modern scholarship).
    
    Note: Retrospective claims typically don't have Wikidata qualifiers
    (they're interpretations, not Wikidata statements).
    """
    
    analysis_layer: Literal["retrospective"]
    
    # No qualifier fields (retrospective claims are interpretations)
    # If needed in future, add similar structure to InSituClaim
```

---

## Qualifier Normalization Algorithm

### Canonical Normalization Function

```python
def normalize_qualifier_value(pid: str, value) -> str:
    """
    Normalize qualifier values to canonical form before hashing (REQ-DATA-003 BR-QUAL-03).
    
    Args:
        pid: Wikidata property ID (P580, P582, P585, P276, P1545)
        value: Raw qualifier value (int, str, or date object)
        
    Returns:
        Normalized string for cipher inclusion
        
    Raises:
        ValueError: If value cannot be normalized for the given PID
    """
    
    # ──────────────────────────────────────────────────────────
    # TEMPORAL QUALIFIERS (P580, P582, P585)
    # ──────────────────────────────────────────────────────────
    if pid in ("P580", "P582", "P585"):
        # Input: -59 (int), "-0044-03-15" (str), date object
        # Output: "+00-59" or "-0044-03-15" (ISO 8601, 5-digit year)
        
        if isinstance(value, int):
            # Year only: normalize to +00-59 format
            return f"{value:+06d}"  # -59 → "+00-59", 100 → "+00100"
        
        elif isinstance(value, str):
            # Already ISO formatted, validate and return
            if re.match(r"^[+-]\d{5}(-\d{2}(-\d{2})?)?$", value):
                return value
            else:
                raise ValueError(
                    f"Temporal qualifier {pid} must be ISO 8601: {value}"
                )
        
        else:
            raise ValueError(
                f"Temporal qualifier {pid} must be int or str: {type(value)}"
            )
    
    # ──────────────────────────────────────────────────────────
    # LOCATION QUALIFIER (P276)
    # ──────────────────────────────────────────────────────────
    elif pid == "P276":
        # Input: "Q220" (str), Q220 (int if parsed)
        # Output: "Q220"
        
        if isinstance(value, str) and value.startswith("Q"):
            return value
        elif isinstance(value, int):
            return f"Q{value}"
        else:
            raise ValueError(
                f"Location qualifier {pid} must be QID: {value}"
            )
    
    # ──────────────────────────────────────────────────────────
    # SERIES ORDINAL (P1545)
    # ──────────────────────────────────────────────────────────
    elif pid == "P1545":
        # Input: 1 (int), "1" (str)
        # Output: "001" (zero-padded to 3 digits)
        
        try:
            ordinal = int(value)
            if ordinal < 1 or ordinal > 999:
                raise ValueError(
                    f"Series ordinal {pid} must be 1-999: {ordinal}"
                )
            return f"{ordinal:03d}"  # 1 → "001", 42 → "042"
        except (ValueError, TypeError):
            raise ValueError(
                f"Series ordinal {pid} must be integer: {value}"
            )
    
    # ──────────────────────────────────────────────────────────
    # UNKNOWN PID
    # ──────────────────────────────────────────────────────────
    else:
        raise ValueError(
            f"Unknown cipher-eligible qualifier: {pid}. "
            f"Expected: P580, P582, P585, P276, P1545"
        )


def build_claim_cipher_with_qualifiers(
    subject_qid: str,
    property_pid: str,
    object_qid: str,
    facet_id: str,
    qualifiers: dict,
    source_qid: str,
    passage_locator: str
) -> str:
    """
    Build Tier 3 claim cipher including cipher-eligible qualifiers.
    
    Only qualifiers in CIPHER_ELIGIBLE_QUALIFIERS are included in hash.
    Others stored as metadata_qualifiers (excluded from cipher).
    
    Args:
        subject_qid: Subject entity QID
        property_pid: Wikidata property (relationship type)
        object_qid: Object entity QID
        facet_id: One of 18 canonical facets
        qualifiers: Dict of Wikidata qualifiers (PIDs → values)
        source_qid: Source work QID
        passage_locator: Citation within source
        
    Returns:
        Claim cipher string (e.g., "fclaim_pol_a1b2c3d4e5f6g7h8")
    """
    import hashlib
    
    CIPHER_ELIGIBLE_QUALIFIERS = {"P580", "P582", "P585", "P276", "P1545"}
    
    # ──────────────────────────────────────────────────────────
    # 1. Extract and normalize cipher-eligible qualifiers
    # ──────────────────────────────────────────────────────────
    eligible = {}
    for pid, value in qualifiers.items():
        if pid in CIPHER_ELIGIBLE_QUALIFIERS:
            eligible[pid] = normalize_qualifier_value(pid, value)
    
    # ──────────────────────────────────────────────────────────
    # 2. Derive temporal_scope from temporal qualifiers (ADR-003)
    # ──────────────────────────────────────────────────────────
    if "P580" in eligible and "P582" in eligible:
        temporal_scope = f"{eligible['P580']}/{eligible['P582']}"
    elif "P585" in eligible:
        temporal_scope = eligible["P585"]
    else:
        temporal_scope = ""
    
    # ──────────────────────────────────────────────────────────
    # 3. Build qualifier string (sorted by PID, deterministic)
    # ──────────────────────────────────────────────────────────
    # Include location and ordinal (NOT temporal, already in temporal_scope)
    cipher_qualifiers = {
        pid: val for pid, val in eligible.items()
        if pid not in ("P580", "P582", "P585")  # Exclude temporal (use temporal_scope)
    }
    
    qualifier_string = "|".join(
        f"{pid}:{cipher_qualifiers[pid]}"
        for pid in sorted(cipher_qualifiers.keys())
    )
    
    # ──────────────────────────────────────────────────────────
    # 4. Build cipher input (matches CLAIM_ID_ARCHITECTURE.md)
    # ──────────────────────────────────────────────────────────
    data = (
        f"{subject_qid}|"
        f"{property_pid}|"
        f"{object_qid}|"
        f"{facet_id.upper()}|"
        f"{temporal_scope}|"          # Derived from P580/P582/P585
        f"{qualifier_string}|"         # P276, P1545 (if present)
        f"{source_qid}|"
        f"{passage_locator}"
    )
    
    # ──────────────────────────────────────────────────────────
    # 5. Hash and format cipher
    # ──────────────────────────────────────────────────────────
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    facet_prefix = FACET_PREFIXES[facet_id.upper()]
    
    return f"fclaim_{facet_prefix}_{hash_value[:16]}"
```

---

## Complete DDL Addendum

### Executable Cypher Script (Add to NEO4J_SCHEMA_DDL_COMPLETE.md)

```cypher
// ═══════════════════════════════════════════════════════════════
// TIER 3 QUALIFIER ADDENDUM (REQ-DATA-003)
// Version: 1.0
// Date: February 22, 2026
// Purpose: Qualifier support for Tier 3 claim ciphers
// ═══════════════════════════════════════════════════════════════

// ───────────────────────────────────────────────────────────────
// ADDITIONAL INDEXES FOR QUALIFIER QUERIES
// ───────────────────────────────────────────────────────────────

// Wikidata triple pattern (subject + predicate + object)
CREATE INDEX claim_wikidata_triple_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subject_entity_cipher, c.wikidata_pid, c.object_qid);

// Temporal qualifiers (start time)
CREATE INDEX claim_temporal_start_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p580_normalized);

// Temporal qualifiers (end time)
CREATE INDEX claim_temporal_end_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p582_normalized);

// Temporal qualifiers (point in time)
CREATE INDEX claim_temporal_point_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p585_normalized);

// Location qualifier
CREATE INDEX claim_location_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p276_qid);

// Series ordinal
CREATE INDEX claim_ordinal_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p1545_ordinal);

// Temporal scope (derived field)
CREATE INDEX claim_temporal_scope_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.temporal_scope);

// ═══════════════════════════════════════════════════════════════
// END OF QUALIFIER ADDENDUM
// ═══════════════════════════════════════════════════════════════
```

---

## Validation Queries

### Verify Qualifier Normalization

```cypher
// Find claims with temporal qualifiers
MATCH (c:FacetClaim)
WHERE c.qualifier_p580_normalized IS NOT NULL
  AND c.qualifier_p582_normalized IS NOT NULL
RETURN 
  c.cipher,
  c.qualifier_p580_normalized,
  c.qualifier_p582_normalized,
  c.temporal_scope
LIMIT 10;

// Verify temporal_scope derivation (should match qualifiers)
MATCH (c:FacetClaim)
WHERE c.qualifier_p580_normalized IS NOT NULL
  AND c.qualifier_p582_normalized IS NOT NULL
  AND c.temporal_scope <> c.qualifier_p580_normalized + '/' + c.qualifier_p582_normalized
RETURN c.cipher, c.temporal_scope, c.qualifier_p580_normalized, c.qualifier_p582_normalized;
// Should return 0 rows (all derived correctly)
```

### Find Claims by Qualifier

```cypher
// Find all claims with series ordinal (e.g., 1st vs 2nd consulship)
MATCH (c:FacetClaim)
WHERE c.qualifier_p1545_ordinal = 1
RETURN c.cipher, c.subject_entity_cipher, c.wikidata_pid, c.object_qid;

// Find claims at specific location
MATCH (c:FacetClaim)
WHERE c.qualifier_p276_qid = "Q220"  // Rome
RETURN c.cipher, c.subject_entity_cipher, c.facet_id;

// Find claims in temporal range
MATCH (c:FacetClaim)
WHERE c.qualifier_p580_normalized >= "+00-50"
  AND c.qualifier_p582_normalized <= "+00-40"
RETURN c.cipher, c.temporal_scope;
```

---

## Summary of Resolutions

| Gap Identified | Resolution |
|----------------|------------|
| **Gap 1: Missing Tier 3 Constraints** | Added 7 qualifier indexes to DDL (no additional constraints needed) |
| **Gap 2: Pydantic Qualifier Validation** | Extended `InSituClaim` with 5 qualifier fields + validators |
| **Gap 3: Temporal Scope Confusion** | **ADR-003:** `temporal_scope` DERIVED from qualifiers P580/P582/P585 |
| **Gap 4: No Normalization Spec** | Canonical `normalize_qualifier_value()` algorithm specified |

---

## References

### Internal Documents
- **ENTITY_CIPHER_FOR_VERTEX_JUMPS.md** — Three-tier cipher model
- **CLAIM_ID_ARCHITECTURE.md** — Tier 3 claim cipher formula
- **NEO4J_SCHEMA_DDL_COMPLETE.md** — Base DDL specification (this is addendum)
- **PYDANTIC_MODELS_SPECIFICATION.md** — Base Pydantic models (extend with qualifiers)
- **REQUIREMENTS.md REQ-DATA-003** — Cipher-eligible qualifiers requirement

### Wikidata Documentation
- [Wikidata Qualifiers](https://www.wikidata.org/wiki/Help:Qualifiers)
- [P580 - Start Time](https://www.wikidata.org/wiki/Property:P580)
- [P582 - End Time](https://www.wikidata.org/wiki/Property:P582)
- [P585 - Point in Time](https://www.wikidata.org/wiki/Property:P585)
- [P276 - Location](https://www.wikidata.org/wiki/Property:P276)
- [P1545 - Series Ordinal](https://www.wikidata.org/wiki/Property:P1545)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| **Feb 22, 2026** | **1.0** | **Initial addendum: ADR-003, qualifier schema, normalization algorithm, Pydantic validators, DDL indexes** |

---

**Document Status:** ✅ Canonical Reference Addendum (Feb 2026)  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026
