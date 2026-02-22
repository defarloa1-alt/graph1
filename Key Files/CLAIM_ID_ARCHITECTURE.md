# Claim ID Architecture: Content-Addressable Assertion Graphs

**Created:** February 16, 2026  
**Status:** Canonical Reference  
**Revision:** 2.0 (Nanopublication-Aligned)

---

## 1. Core Principle: Claim Identity ≠ Entity Identity

### 1.1 Two Separate Identity Spaces

**Entity/Node IDs:**
- Identify **things** (people, places, events, concepts)
- Examples: `Q1048` (Julius Caesar), `Q644312` (Plutarch's work)
- Can be opaque identifiers (QIDs, UUIDs, composite keys)
- May evolve with entity knowledge (properties change, confidence updates)

**Claim IDs (Ciphers):**
- Identify **assertions/statements** about things
- Examples: `fclaim_pol_abc123...` (political facet claim)
- Content-addressable: derived from **what is being asserted**, not who/when/confidence
- Stable across provenance changes (agent, timestamp, confidence)

### 1.2 Why Separate?

**Problem:** Early implementations concatenated all node IDs + provenance into cipher:
```python
# ❌ UNSTABLE FORMULA (Jan 2026 - Deprecated)
claim_cipher = Hash(
    subject_qid + object_qid + relationship +
    confidence_score +           # ❌ Evidence update → new ID
    extractor_agent_id +         # ❌ Different agent → new ID
    extraction_timestamp         # ❌ Different time → new ID
)
```

**Issues:**
1. **Breaks Deduplication:** Two agents discovering same fact at different times → different ciphers
2. **Creates Instability:** Evidence improvement (0.85 → 0.95 confidence) → new cipher
3. **Conflates Concerns:** Provenance metadata treated as logical content
4. **Prevents Citation Stability:** Cipher changes when confidence updates

**Solution:** Treat claim as **minimal assertion graph** (nanopublication pattern):
- Cipher derived from **stable logical content** only
- Provenance stored as **separate mutable metadata**
- Enables proper deduplication and citation stability

---

## 2. Facet-Level Claim Signature (Stable Formula)

### 2.1 Core Components

**Revised Cipher Formula (Feb 2026):**
```python
facet_claim_cipher = Hash(
    # Core assertion (minimal triple)
    subject_node_id +            # Q1048 (Julius Caesar)
    property_path_id +           # "CHALLENGED_AUTHORITY_OF"
    object_node_id +             # Q1747689 (Roman Senate)
    
    # Context/Facet dimension
    facet_id +                   # "political" (essential!)
    temporal_scope +             # "-0049-01-10" (when assertion holds)
    
    # Source provenance (for per-source granularity)
    source_document_id +         # Q644312 (Plutarch, Life of Caesar)
    passage_locator              # "Caesar.32" (specific citation)
)

# Result: "fclaim_pol_b22020c0e271b7d8..." (stable cipher)
```

### 2.2 What Changed?

**✅ ADDED:**
- `facet_id` - Explicit facet dimension (political, military, economic, etc.)
- `property_path_id` - Normalized predicate (supports CIDOC-CRM alignment)
- Facet prefix - Human-readable prefix (e.g., `fclaim_pol_`, `fclaim_mil_`)

**❌ REMOVED:**
- `confidence_score` - Now separate mutable property (can update without changing ID)
- `extractor_agent_id` - Provenance metadata, not logical content
- `extraction_timestamp` - Lifecycle tracking, not identity

### 2.3 Benefits

| Benefit | Description |
|---------|-------------|
| **Deduplication** | Two agents at different times → same cipher → single claim node |
| **Citation Stability** | Cipher unchanged when confidence updates (scholars can cite reliably) |
| **Evidence Accumulation** | Multiple agents → same claim → higher consensus, not duplicates |
| **Provenance Separation** | Who/when/confidence tracked separately from what is asserted |
| **Facet Clarity** | Different facets = different claims (not just perspectives) |

---

## 3. Hierarchical Facet Claims: Sibling/Parent Model

### 3.1 Conceptual Framework

**Key Insight:** Complex historical assertions have multiple facet-specific dimensions.

**Example Statement:** "Scipio commanded at Battle of Zama in 202 BCE"

**Facet-Level Claims (Siblings, First-Class):**
- **Military Facet:** "Scipio commanded legion at Zama"
- **Chronology Facet:** "Battle occurred in October 202 BCE"
- **Geographic Facet:** "Battle near Naraggara"

Each facet claim:
- Has its **own cipher** (content-addressable)
- Is a **first-class assertion** (not dependent on others)
- Can be validated **independently**
- References **different property paths** (COMMANDED_AT, OCCURRED_ON, LOCATED_NEAR)

**Composite Claim (Parent, Higher-Order):**
- References **set of facet claim ciphers** (not raw node IDs)
- Represents "participation event bundle"
- Cipher computed from **facet claim IDs**, not entire raw subgraph

### 3.2 Graph Structure

```cypher
// Facet-Level Claims (Siblings)
(C1:FacetClaim {
  cipher: "fclaim_mil_abc123...",
  facet: "military",
  subject_id: "Q127978",            // Scipio
  property_path: "COMMANDED_AT",
  object_id: "Q48314",              // Battle of Zama
  temporal: "-0202",
  source: "Q47461"                  // Polybius
})

(C2:FacetClaim {
  cipher: "fclaim_chr_def456...",
  facet: "chronology",
  subject_id: "Q48314",             // Battle of Zama
  property_path: "OCCURRED_ON",
  object_value: "-0202-10",
  source: "Q47461"
})

(C3:FacetClaim {
  cipher: "fclaim_geo_ghi789...",
  facet: "geographic",
  subject_id: "Q48314",
  property_path: "LOCATED_NEAR",
  object_id: "Q?????",              // Naraggara
  source: "Q47461"
})

// Composite Claim (Parent)
(C_all:CompositeClaim {
  cipher: "composite_jkl012...",    // Hash of sorted facet claim IDs
  claim_type: "participation_event_bundle",
  facet_claim_ids: [
    "fclaim_mil_abc123...",
    "fclaim_chr_def456...",
    "fclaim_geo_ghi789..."
  ],
  source: "Q47461"
})

// Hierarchical Relationships
(C_all)-[:HAS_FACET_CLAIM]->(C1)
(C_all)-[:HAS_FACET_CLAIM]->(C2)
(C_all)-[:HAS_FACET_CLAIM]->(C3)
```

### 3.3 Composite Claim Cipher Formula

```python
# Composite claim references facet claim ciphers, NOT raw nodes
composite_cipher = Hash(
    sorted([
        "fclaim_mil_abc123...",      # Military facet claim
        "fclaim_chr_def456...",      # Chronology facet claim
        "fclaim_geo_ghi789..."       # Geographic facet claim
    ]) +                              # Sorted for determinism
    composite_facet_type +            # "participation_event_bundle"
    source_document_id                # Q47461 (Polybius)
)
# Result: "composite_jkl012..." (stable composite cipher)
```

**Why NOT concatenate raw node IDs?**
- Entity evolution (new properties added to Caesar node) ≠ claim identity change
- Prevents instability from unrelated entity updates
- Maintains separation: entity identity vs assertion identity

### 3.4 Benefits

| Pattern | Benefit |
|---------|---------|
| **Sibling Claims** | Independent validation per facet |
| **Composite References Ciphers** | Stable even when entities evolve |
| **Facet-Specific Confidence** | Military facet 0.9, Political facet 0.7 (separate tracking) |
| **Selective Querying** | "Show all military claims" without loading chronology data |
| **Incremental Construction** | Add geographic facet later without invalidating existing claims |

---

## 4. Normalization Rules and Data Format Requirements

**CRITICAL:** All cipher components must be normalized to canonical form BEFORE hashing to ensure deterministic, collision-free claim IDs.

### 4.1 Literal Value Normalization (Non-Node Objects)

**Problem:** When object_node_id is a literal value (not a Wikidata QID), inconsistent formatting creates different ciphers for identical facts.

**Solution:** Normalize literals using XSD datatype prefix convention:

```python
def normalize_literal(value, datatype="xsd:string"):
    """Ensure literals use canonical format before hashing."""
    if datatype == "xsd:gYear":
        # Historical year: zero-padded to 5 digits, negative for BCE
        year = int(value)
        return f"lit_xsd:gYear_{year:+06d}"  # "-00049" for 49 BCE
    
    elif datatype == "xsd:gYearMonth":
        # ISO 8601 YYYY-MM: zero-padded, negative for BCE
        return f"lit_xsd:gYearMonth_{value}"  # "-0049-01"
    
    elif datatype == "xsd:date":
        # ISO 8601 YYYY-MM-DD: zero-padded
        return f"lit_xsd:date_{value}"  # "-0049-01-10"
    
    elif datatype == "xsd:string":
        # Lowercase, trim whitespace, normalize unicode
        return f"lit_xsd:string_{value.lower().strip()}"
    
    else:
        return f"lit_{datatype}_{value}"

# Examples
normalize_literal(100, "xsd:gYear")           # "lit_xsd:gYear_+00100"
normalize_literal(-49, "xsd:gYear")           # "lit_xsd:gYear_-00049"
normalize_literal("-0049-01-10", "xsd:date")  # "lit_xsd:date_-0049-01-10"
normalize_literal("SENATE", "xsd:string")     # "lit_xsd:string_senate"
```

**Usage in cipher:**
```python
facet_claim_cipher = Hash(
    subject_node_id +          # "Q1048" (QID)
    property_path_id +         # "CHALLENGED_AUTHORITY_OF"
    normalize_literal("-0049-01-10", "xsd:date") +  # "lit_xsd:date_-0049-01-10"
    facet_id +                 # "political"
    ...
)
```

### 4.2 Temporal Scope Normalization (ISO 8601 + Uncertainty Flags)

**Rule 1: ISO 8601 Format with Zero-Padding**

All historical year values must use ISO 8601 format with 5-digit zero-padded years (BCE as negative):

```python
def normalize_temporal_scope(date_value, circa=False, precision="year"):
    """
    Normalize temporal scope to ISO 8601 + uncertainty flag.
    
    Args:
        date_value: int (BCE/CE year) or str (ISO 8601)
        circa: bool, True if date is approximate ("circa X BCE")
        precision: "year" | "month" | "day"
    
    Returns: Canonical ISO 8601 string + circa flag stored separately
    """
    if isinstance(date_value, int):
        year = date_value
    else:
        year = int(date_value[:4])  # Extract year from ISO string
    
    # ISO 8601 formatting: 5-digit zero-padded year
    if precision == "year":
        canonical = f"{year:+06d}"  # "+00100" or "-00049"
    elif precision == "month":
        canonical = f"{year:+06d}-01"  # Defaults to January if only year given
    elif precision == "day":
        canonical = f"{year:+06d}-01-01"  # Defaults to Jan 1
    
    return canonical

# Examples
normalize_temporal_scope(-49, circa=False)     # "-00049"
normalize_temporal_scope(100, circa=False)     # "+00100"
normalize_temporal_scope(-49, circa=True)      # "-00049" (circa flag separate)
```

**Rule 2: Uncertainty Handling via Separate `circa_flag`**

Approximate dates are handled via metadata, NOT embedded in the normalized value:

```cypher
// Cipher uses normalized DATE ONLY
cipher_component = "-00049"

// Node stores uncertainty separately
(claim:FacetClaim {
  temporal_scope: "-00049",
  temporal_scope_circa: true,  // Flag for "circa 49 BCE"
  temporal_scope_precision: "year"
})
```

**Rule 3: Date Range Formatting (Start-End Temporal Scope)**

For claims spanning time intervals (e.g., marriage duration):

```python
def normalize_temporal_range(start_date, end_date):
    """Normalize date ranges to canonical format."""
    norm_start = normalize_temporal_scope(start_date)
    norm_end = normalize_temporal_scope(end_date)
    
    # Store as separate claims or as range in cipher
    # Preferred: Two separate edges (start_temporal + end_temporal)
    # Alternative: Single ranged format "[START TO END]"
    
    return {
        "start_temporal_scope": norm_start,
        "end_temporal_scope": norm_end
    }

# Example: Caesar's marriage 84-69 BCE
normalize_temporal_range(-84, -69)
# {
#   "start_temporal_scope": "-00084",
#   "end_temporal_scope": "-00069"
# }
```

### 4.3 Property Path Registry Validation (Flexible with Custom Predicates)

**Rule:** property_path_id values must follow canonical naming conventions and reference registry entries with authority mappings.

**Locked Keys (From CANONICAL_RELATIONSHIP_TYPES.md):**
```python
CANONICAL_PREDICATES = {
    "MARRIED": {"wikidata": "P26", "cidoc_crm": "P14_carried_out_by"},
    "PARENT_OF": {"wikidata": "P25", "cidoc_crm": "P108_produced"},
    "POLITICAL_ALLY_OF": {"wikidata": "P1318", "cidoc_crm": "P11_had_participant"},
    # ... (all relationships from CANONICAL_RELATIONSHIP_TYPES.md)
}
```

**Custom Predicates Allowed:**
For domain-specific relationships not yet in registry, use format: `{domain}:{predicate_name}`

```python
# Valid custom predicates
"military:led_battle"           # Military domain
"economic:controlled_trade"     # Economic domain
"cultural:patron_of_arts"       # Cultural domain

# INVALID (free-text forbidden)
"led_a_battle"                  # ❌ No domain prefix
"MILITARY_LEADERSHIP"           # ❌ No colon separator
"custom_relationship_xyz"       # ❌ Ambiguous domain
```

**Registry Link Rule:**
```cypher
// Before hashing, validate
property_path_id_normalized = property_path_id.upper()  // Uppercase

// Verify in registry
IF property_path_id_normalized IN CANONICAL_PREDICATES:
    // Proceed with canonical key
    hash_input = property_path_id_normalized
ELSE_IF ":" IN property_path_id_normalized:
    // Custom predicate format validated
    hash_input = property_path_id_normalized
ELSE:
    // ❌ REJECTION: Free-text forbidden
    RAISE("property_path_id invalid format")
```

### 4.4 Facet ID Normalization (Uppercase Required)

**Rule:** All facet_id values must be uppercase to prevent case-collision bugs.

```python
def normalize_facet_id(facet_input):
    """Ensure facet IDs are uppercase and canonicalized."""
    facet_canonical = facet_input.upper()
    
    # Valid facet IDs (17 facets)
    VALID_FACETS = {
        "BIOGRAPHIC", "POLITICAL", "MILITARY", "ECONOMIC",
        "RELIGIOUS", "SOCIAL", "CULTURAL", "ARTISTIC",
        "INTELLECTUAL", "LINGUISTIC", "GEOGRAPHIC", "ENVIRONMENTAL",
        "TECHNOLOGICAL", "DEMOGRAPHIC", "DIPLOMATIC", "SCIENTIFIC",
        "ARCHAEOLOGICAL", "COMMUNICATION"  # Communication is facet-only
    }
    
    if facet_canonical not in VALID_FACETS:
        raise ValueError(f"Invalid facet_id: {facet_input}. Must be one of {VALID_FACETS}")
    
    return facet_canonical

# Examples
normalize_facet_id("political")     # "POLITICAL"
normalize_facet_id("Political")     # "POLITICAL"
normalize_facet_id("POLITICAL")     # "POLITICAL"
normalize_facet_id("military")      # "MILITARY"
normalize_facet_id("invalid_facet") # ❌ RAISES ValueError
```

**Why uppercase?**
- Prevents case-collision: `political` vs `Political` vs `POLITICAL` → one cipher ID
- Explicit canonical format for all facet keys
- Consistent with Facets/facet_registry_master.csv

### 4.5 Claim Node Type Compatibility: FacetClaim vs CompositeClaim

**Architecture Decision (Option A: Supertype + Subtype Model)**

FacetClaim and CompositeClaim are Cypher node labels representing a type hierarchy:

```cypher
// FacetClaim: First-class single-facet assertion
(:Claim:FacetClaim {
  cipher: "fclaim_pol_abc123...",
  facet_id: "POLITICAL",
  subject_node_id: "Q1048",
  property_path_id: "CHALLENGED_AUTHORITY_OF",
  object_node_id: "Q1747689"
})

// CompositeClaim: Aggregation of sibling FacetClaims
(:Claim:CompositeClaim {
  cipher: "composite_jkl789...",
  facet_claim_ids: ["fclaim_pol_...", "fclaim_mil_...", "fclaim_geo_..."],
  composite_type: "participation_event_bundle"
})

// Label inheritance
(fclaim:Claim:FacetClaim) means:
  - Matches (:Claim) queries
  - Matches (:FacetClaim) queries
  - Distinguishable from (:CompositeClaim)
```

**Query Implications:**
```cypher
// Query all claims (both facet-level and composite)
MATCH (c:Claim)
RETURN c

// Query only facet-level claims
MATCH (c:Claim:FacetClaim)
RETURN c

// Query only composite bundles
MATCH (c:Claim:CompositeClaim)
RETURN c

// Query single facet's claims
MATCH (c:Claim:FacetClaim {facet_id: "POLITICAL"})
RETURN c
```

**Cipher Formula Consistency:**
```python
# FacetClaim cipher (minimal triple + facet + temporal)
fclaim_cipher = Hash(
    subject_node_id + property_path_id + object_node_id +
    facet_id + temporal_scope + source_document_id + passage_locator
)

# CompositeClaim cipher (sorted facet claim IDs)
composite_cipher = Hash(
    sorted(facet_claim_ids) + composite_type + source_document_id
)

# Both use normalized components; no confidence/agent metadata in cipher
```

---

## 5. Neo4j Schema: Facet Claim Nodes

### 5.1 FacetClaim Node Type

```cypher
CREATE (claim:FacetClaim {
  // PRIMARY IDENTITY (content-addressable, stable)
  cipher: "fclaim_pol_b22020c0e271b7d8",  // SHA256 hash (facet-prefixed)
  
  // INTERNAL ID (convenience, non-canonical)
  claim_id: "claim_00123",                // Sequential ID for debugging
  
  // CIPHER COMPONENTS (stable, logical content)
  subject_node_id: "Q1048",               // Caesar
  property_path_id: "CHALLENGED_AUTHORITY_OF",
  object_node_id: "Q1747689",             // Roman Senate
  facet_id: "political",                  // Facet dimension
  temporal_scope: "-0049-01-10",          // When assertion holds
  source_document_id: "Q644312",          // Plutarch
  passage_locator: "Caesar.32",           // Citation reference
  
  // DERIVED SEMANTICS
  assertion_text: "Caesar challenged Senate authority by crossing Rubicon",
  cidoc_crm_property: "P17_was_motivated_by",  // Ontology alignment
  
  // PROVENANCE METADATA (separate from cipher, mutable)
  confidence: 0.85,                       // Can update → 0.95 without changing cipher
  extracting_agents: [                    // Multiple agents = evidence accumulation
    "political_sfa_001",
    "military_sfa_001"                    // Added via deduplication
  ],
  extraction_timestamps: [
    "2026-02-12T10:00:00Z",
    "2026-02-12T14:00:00Z"
  ],
  created_by_agent: "political_sfa_001",  // Original extractor
  last_updated: "2026-02-12T14:00:00Z",
  
  // STATUS & VALIDATION (lifecycle, not identity)
  status: "validated",                    // proposed → under_review → validated
  review_count: 2,
  consensus_score: 0.91,
  validation_timestamp: "2026-02-12T15:00:00Z"
})

// Required Indexes
CREATE INDEX facet_claim_cipher_idx FOR (c:FacetClaim) ON (c.cipher);
CREATE INDEX facet_claim_facet_idx FOR (c:FacetClaim) ON (c.facet_id);
CREATE INDEX facet_claim_subject_idx FOR (c:FacetClaim) ON (c.subject_node_id);
```

### 4.2 CompositeClaim Node Type

```cypher
CREATE (comp:CompositeClaim {
  cipher: "composite_jkl012...",          // Hash of facet claim IDs + type
  claim_type: "participation_event_bundle",
  facet_claim_ids: [
    "fclaim_mil_abc123...",
    "fclaim_chr_def456...",
    "fclaim_geo_ghi789..."
  ],
  source_document_id: "Q47461",           // Polybius
  confidence: 0.88,                       // Aggregate confidence
  created_at: "2026-02-12T15:00:00Z"
})

// Relationships
CREATE (comp)-[:HAS_FACET_CLAIM]->(facet_claim_1)
CREATE (comp)-[:HAS_FACET_CLAIM]->(facet_claim_2)
CREATE (comp)-[:HAS_FACET_CLAIM]->(facet_claim_3)
```

### 4.3 Key Differences: FacetClaim vs CompositeClaim

| Aspect | FacetClaim | CompositeClaim |
|--------|------------|----------------|
| **Scope** | Single facet dimension | Multi-facet bundle |
| **Cipher Basis** | Subject + property + object + facet + temporal | Sorted list of facet claim ciphers |
| **Validation** | Independent per facet | Requires all facet claims validated |
| **Query Target** | Facet-specific analysis | Holistic event reconstruction |
| **Relationships** | (Subject)-[Property]->(Object) | (Composite)-[:HAS_FACET_CLAIM]->(FacetClaim) |

---

## 5. Nanopublication Alignment

### 5.1 Standards References

**Nanopublication Framework:**
- [Framework for Citing Nanopublications](https://research.vu.nl) - VU Amsterdam
- [Nanopublication Assertion Graphs](https://pmc.ncbi.nlm.nih.gov/articles/PMC7959622/) - NIH/NLM
- [Named Graph Usage](https://cidoc-crm.org) - CIDOC-CRM recommendations

**Core Principle:** "A nanopublication is the smallest unit of publishable information: an assertion about something, attributed to a source, with provenance metadata."

### 5.2 Mapping to Chrystallum

| Nanopublication Component | Chrystallum Implementation |
|---------------------------|----------------------------|
| **Assertion Graph** | FacetClaim node (subject + property + object) |
| **Publication Info** | Provenance metadata (agent, timestamp, confidence) |
| **Provenance Graph** | Extract relationships (Work → Agent → Claim) |
| **Named Graph URI** | Claim cipher (content-addressable ID) |
| **Trusty URI** | Cipher as cryptographic fingerprint |

### 5.3 Named Graph Pattern

```turtle
# Named graph using cipher as URI
<fclaim:pol:b22020c0e271b7d8...> {
    # Assertion (minimal triple)
    wikidata:Q1048 cidoc:P17_was_motivated_by wikidata:Q1747689 .
    
    # Temporal scope
    [] cidoc:P4_has_time-span [
        cidoc:P82a_begin_of_the_begin "-0049-01-10"^^xsd:date
    ] .
}

# Publication info (separate graph)
<fclaim:pol:b22020c0e271b7d8...#pubinfo> {
    <fclaim:pol:b22020c0e271b7d8...> 
        dcterms:created "2026-02-12T10:00:00Z"^^xsd:dateTime ;
        dcterms:creator <agent:political_sfa_001> ;
        prov:wasDerivedFrom wikidata:Q644312 ;
        chrystallum:confidence "0.85"^^xsd:float .
}

# Provenance (separate graph)
<fclaim:pol:b22020c0e271b7d8...#provenance> {
    <agent:political_sfa_001> a prov:SoftwareAgent ;
        rdfs:label "Political Subject Facet Agent" ;
        prov:actedOnBehalfOf <org:university_rome> .
}
```

### 5.4 Benefits of Alignment

| Benefit | Description |
|---------|-------------|
| **Interoperability** | Compatible with RDF/nanopub tools |
| **Citation Standards** | Follows academic citation practices |
| **Provenance Tracking** | Aligns with W3C PROV-O ontology |
| **Distributed Publishing** | Named graphs enable federated knowledge networks |
| **Cryptographic Verification** | Trusty URIs enable integrity checking |

---

## 6. Deduplication & Verification Patterns

### 6.1 Deduplication Query

**Check if claim already exists before creating:**
```cypher
// Compute cipher from incoming claim data
WITH 
  $subject_id + $property_path + $object_id + 
  $facet_id + $temporal + $source_id + $passage
  AS content_signature,
  SHA256(content_signature) AS computed_cipher

// Check if this content already exists
MATCH (existing:FacetClaim {cipher: computed_cipher})
RETURN existing

// If found: Add supporting agent (not duplicate)
MERGE (existing:FacetClaim {cipher: computed_cipher})
ON MATCH SET 
  existing.extracting_agents = existing.extracting_agents + $new_agent_id,
  existing.extraction_timestamps = existing.extraction_timestamps + $new_timestamp,
  existing.review_count = existing.review_count + 1,
  existing.confidence = (existing.confidence + $new_confidence) / 2  // Average
  // NOTE: Cipher UNCHANGED! Only provenance metadata updated

// If not found: Create new claim
ON CREATE SET
  existing.created_by_agent = $new_agent_id,
  existing.created_at = $new_timestamp,
  existing.confidence = $new_confidence
```

### 6.2 Integrity Verification Query

**Verify claim hasn't been tampered with:**
```cypher
MATCH (c:FacetClaim {cipher: $claimed_cipher})
WITH c, 
  SHA256(
    c.subject_node_id + 
    c.property_path_id + 
    c.object_node_id +
    c.facet_id +
    c.temporal_scope +
    c.source_document_id +
    c.passage_locator
    // NOTE: NO confidence, NO agent, NO timestamp!
  ) AS recomputed_cipher
RETURN 
  c.cipher = recomputed_cipher AS integrity_verified,
  c.cipher AS original_cipher,
  recomputed_cipher AS computed_cipher,
  CASE 
    WHEN c.cipher = recomputed_cipher THEN "✅ Claim identity verified"
    ELSE "❌ Cipher mismatch - possible tampering"
  END AS verification_status
```

### 6.3 Find Potential Duplicates

**Detect deduplication failures (same content, different ciphers):**
```cypher
// This query should return ZERO results if deduplication works
MATCH (c1:FacetClaim), (c2:FacetClaim)
WHERE c1.subject_node_id = c2.subject_node_id
  AND c1.property_path_id = c2.property_path_id
  AND c1.object_node_id = c2.object_node_id
  AND c1.facet_id = c2.facet_id
  AND c1.temporal_scope = c2.temporal_scope
  AND c1.source_document_id = c2.source_document_id
  AND c1.cipher <> c2.cipher  // Different ciphers despite same content!
RETURN c1.cipher, c2.cipher, 
       "⚠️ Deduplication failure detected" AS status,
       c1.extracting_agents AS agents1,
       c2.extracting_agents AS agents2
```

---

## 7. Implementation Guide

### 7.1 Python Implementation

**File:** `scripts/tools/claim_ingestion_pipeline.py`

```python
import hashlib
from typing import Dict, List, Optional

def calculate_facet_claim_cipher(
    subject_node_id: str,
    property_path_id: str,
    object_node_id: str,
    facet_id: str,
    temporal_scope: str,
    source_document_id: str,
    passage_locator: str
) -> str:
    """
    Calculate SHA256 cipher for facet-level claim (content-addressable ID).
    
    REVISED FORMULA (Feb 2026): Stable, content-based cipher that excludes
    provenance metadata (confidence, agent, timestamp) to enable proper
    deduplication across agents and time.
    
    Aligned with nanopublication assertion graph patterns.
    
    Args:
        subject_node_id: Q-ID of subject entity (e.g., "Q1048" for Caesar)
        property_path_id: Normalized relationship (e.g., "CHALLENGED_AUTHORITY_OF")
        object_node_id: Q-ID of object entity (e.g., "Q1747689" for Roman Senate)
        facet_id: Facet dimension (e.g., "political", "military")
        temporal_scope: When assertion holds (e.g., "-0049-01-10")
        source_document_id: Source Q-ID (e.g., "Q644312" for Plutarch)
        passage_locator: Passage reference (e.g., "Caesar.32")
    
    Returns:
        SHA256 cipher prefixed with facet (e.g., "fclaim_pol_abc123...")
    
    Note: Confidence, extractor_agent_id, and extraction_timestamp are
    stored as separate mutable properties, NOT included in cipher.
    """
    # Construct stable content signature
    data = (
        f"{subject_node_id}|"
        f"{property_path_id}|"
        f"{object_node_id}|"
        f"{facet_id}|"
        f"{temporal_scope}|"
        f"{source_document_id}|"
        f"{passage_locator}"
    )
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    
    # Prefix with facet for human readability
    return f"fclaim_{facet_id[:3]}_{hash_value[:16]}"


def calculate_composite_claim_cipher(
    facet_claim_ciphers: List[str],
    composite_type: str,
    source_document_id: str
) -> str:
    """
    Calculate cipher for composite claim (references facet claim ciphers).
    
    Args:
        facet_claim_ciphers: List of facet claim ciphers (sorted for determinism)
        composite_type: Type of composite (e.g., "participation_event_bundle")
        source_document_id: Source Q-ID
    
    Returns:
        SHA256 cipher prefixed with "composite_"
    """
    # Sort for deterministic ordering
    sorted_ciphers = sorted(facet_claim_ciphers)
    
    data = (
        "|".join(sorted_ciphers) + "|" +
        composite_type + "|" +
        source_document_id
    )
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    
    return f"composite_{hash_value[:16]}"
```

### 7.2 Usage Example

```python
# Political SFA extracts claim at 10:00 AM
cipher_A = calculate_facet_claim_cipher(
    subject_node_id="Q1048",           # Caesar
    property_path_id="CHALLENGED_AUTHORITY_OF",
    object_node_id="Q1747689",         # Roman Senate
    facet_id="political",
    temporal_scope="-0049-01-10",
    source_document_id="Q644312",      # Plutarch
    passage_locator="Caesar.32"
)
# Result: "fclaim_pol_b22020c0e271b7d8"

# Military SFA discovers SAME political dimension at 2:00 PM
cipher_B = calculate_facet_claim_cipher(
    subject_node_id="Q1048",           # SAME content
    property_path_id="CHALLENGED_AUTHORITY_OF",
    object_node_id="Q1747689",
    facet_id="political",              # SAME facet
    temporal_scope="-0049-01-10",
    source_document_id="Q644312",
    passage_locator="Caesar.32"
)
# Result: "fclaim_pol_b22020c0e271b7d8" (SAME CIPHER!)

assert cipher_A == cipher_B  # ✅ Automatic deduplication

# Create composite claim from multiple facets
composite_cipher = calculate_composite_claim_cipher(
    facet_claim_ciphers=[
        "fclaim_mil_abc123...",        # Military facet
        "fclaim_pol_b22020c0e271b7d8",  # Political facet
        "fclaim_geo_ghi789..."         # Geographic facet
    ],
    composite_type="participation_event_bundle",
    source_document_id="Q644312"
)
# Result: "composite_jkl012..."
```

---

## 8. Migration from Old Formula

### 8.1 Deprecated Formula (Jan 2026)

```python
# ❌ OLD FORMULA (unstable, breaks deduplication)
old_cipher = Hash(
    source_work_qid +
    passage_text_hash +
    subject_entity_qid +
    object_entity_qid +
    relationship_type +
    action_structure +
    temporal_data +
    confidence_score +           # ❌ Creates instability
    extractor_agent_id +         # ❌ Prevents deduplication
    extraction_timestamp         # ❌ Different times = different IDs
)
```

### 8.2 Migration Strategy

**Phase 1: Identify Affected Claims**
```cypher
// Find all claims with old cipher format
MATCH (c:Claim)
WHERE NOT c.cipher STARTS WITH "fclaim_"
  AND NOT c.cipher STARTS WITH "composite_"
RETURN count(c) AS claims_needing_migration
```

**Phase 2: Recompute Ciphers**
```python
# For each old claim:
# 1. Extract stable components (subject, property, object, facet, temporal, source)
# 2. Recompute cipher using new formula (exclude confidence, agent, timestamp)
# 3. Check if new cipher already exists (merge if duplicate)
# 4. Update relationships to use new cipher
# 5. Archive old cipher for historical reference
```

**Phase 3: Merge Duplicates**
```cypher
// Find claims that should have been deduplicated
MATCH (c1:Claim), (c2:Claim)
WHERE c1.subject_node_id = c2.subject_node_id
  AND c1.property_path_id = c2.property_path_id
  AND c1.facet_id = c2.facet_id
  AND c1.cipher < c2.cipher  // Keep lexically earlier cipher
WITH c1, c2
// Merge provenance metadata
SET c1.extracting_agents = c1.extracting_agents + c2.extracting_agents,
    c1.confidence = (c1.confidence + c2.confidence) / 2
// Redirect relationships
MATCH (c2)-[r]->(other)
CREATE (c1)-[r2:SAME_TYPE(r)]->(other)
SET r2 = properties(r)
// Archive duplicate
SET c2:ArchivedClaim, c2.superseded_by = c1.cipher
DETACH DELETE c2
```

---

## 9. Testing & Validation

### 9.1 Test Suite

**File:** `tests/test_claim_cipher_stability.py`

```python
import pytest
from scripts.tools.claim_ingestion_pipeline import calculate_facet_claim_cipher

def test_same_content_same_cipher():
    """Test: Same content at different times → Same cipher"""
    cipher_1 = calculate_facet_claim_cipher(
        subject_node_id="Q1048",
        property_path_id="CROSSED",
        object_node_id="Q644312",
        facet_id="military",
        temporal_scope="-0049-01-10",
        source_document_id="Q644312",
        passage_locator="Caesar.32"
    )
    
    cipher_2 = calculate_facet_claim_cipher(
        subject_node_id="Q1048",
        property_path_id="CROSSED",
        object_node_id="Q644312",
        facet_id="military",
        temporal_scope="-0049-01-10",
        source_document_id="Q644312",
        passage_locator="Caesar.32"
    )
    
    assert cipher_1 == cipher_2  # ✅ Deduplication works

def test_different_facets_different_ciphers():
    """Test: Same event, different facets → Different ciphers"""
    cipher_mil = calculate_facet_claim_cipher(
        subject_node_id="Q1048",
        property_path_id="COMMANDED",
        object_node_id="Q644312",
        facet_id="military",  # Military facet
        temporal_scope="-0049-01-10",
        source_document_id="Q644312",
        passage_locator="Caesar.32"
    )
    
    cipher_pol = calculate_facet_claim_cipher(
        subject_node_id="Q1048",
        property_path_id="CHALLENGED_AUTHORITY_OF",
        object_node_id="Q1747689",
        facet_id="political",  # Political facet
        temporal_scope="-0049-01-10",
        source_document_id="Q644312",
        passage_locator="Caesar.32"
    )
    
    assert cipher_mil != cipher_pol  # ✅ Different facets = different claims

def test_confidence_doesnt_affect_cipher():
    """Test: Confidence updates don't change cipher"""
    cipher_low = calculate_facet_claim_cipher(
        subject_node_id="Q1048",
        property_path_id="CROSSED",
        object_node_id="Q644312",
        facet_id="military",
        temporal_scope="-0049-01-10",
        source_document_id="Q644312",
        passage_locator="Caesar.32"
    )
    # Note: confidence NOT in cipher formula!
    
    # Later: confidence improves 0.85 → 0.95
    cipher_high = calculate_facet_claim_cipher(
        subject_node_id="Q1048",
        property_path_id="CROSSED",
        object_node_id="Q644312",
        facet_id="military",
        temporal_scope="-0049-01-10",
        source_document_id="Q644312",
        passage_locator="Caesar.32"
    )
    
    assert cipher_low == cipher_high  # ✅ Cipher stable despite confidence change
```

---

## 10. Summary & References

### 10.1 Key Takeaways

1. **Claim IDs are assertion identifiers, not entity identifiers**
2. **Cipher based on stable logical content only (no provenance)**
3. **Enables automatic deduplication across agents and time**
4. **Aligned with nanopublication assertion graph standards**
5. **Hierarchical facet claims: siblings (facet-level) + parent (composite)**
6. **Composite claims reference facet cipher IDs, not raw nodes**
7. **Provenance metadata separate and mutable (confidence, agent, timestamp)**

### 10.2 Architecture Documents

- **CONSOLIDATED.md** - Section 6.4: Content-Addressable Claim Identification
- **SCA_SFA_ROLES_DISCUSSION.md** - Claim cipher in SCA ↔ SFA coordination
- **SCA_SFA_ARCHITECTURE_PACKAGE.md** - Implementation summary
- **claim_ingestion_pipeline.py** - Python implementation

### 10.3 External Standards

- [VU Amsterdam: Framework for Citing Nanopublications](https://research.vu.nl)
- [NIH/NLM: Nanopublication Assertion Graphs](https://pmc.ncbi.nlm.nih.gov/articles/PMC7959622/)
- [CIDOC-CRM: Named Graph Usage Recommendations](https://cidoc-crm.org)
- [W3C PROV-O: Provenance Ontology](https://www.w3.org/TR/prov-o/)

### 10.4 Revision History

| Date | Version | Changes |
|------|---------|---------|
| Jan 15, 2026 | 1.0 | Initial cipher formula (9 components) |
| Feb 15, 2026 | 1.5 | SCA ↔ SFA coordination documented |
| **Feb 16, 2026** | **2.0** | **Revised formula: removed confidence/agent/timestamp, added facet_id, hierarchical facet claims, nanopublication alignment** |

---

**Document Status:** ✅ Canonical Reference (Feb 2026)  
**Maintainers:** Chrystallum Architecture Team  
**Last Updated:** February 16, 2026
