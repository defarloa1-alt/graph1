# ADR-012: Pattern-Centric Tier 3 Ciphers (Source Exclusion)

**Date:** February 22, 2026  
**Status:** PROPOSED (Breaking Change)  
**Supersedes:** Partial revision of ADR-001 (Claim Identity Ciphers)  
**Related:** TIER_3_CLAIM_CIPHER_ADDENDUM.md, ENTITY_CIPHER_FOR_VERTEX_JUMPS.md

---

## Context

The current Tier 3 claim cipher formula includes `source_qid` and `passage_locator` in the hash input:

```python
# Current (v1.0):
hash_input = (
    f"{subject_qid}|{property_pid}|{object_qid}|{facet_id}|"
    f"{temporal_scope}|{qualifier_string}|"
    f"{source_qid}|{passage_locator}"  # ← Source in cipher
)
```

**Consequence:** Same assertion from different sources produces different ciphers.

**Example:**
- Plutarch: "Caesar was consul in 59 BCE" → `fclaim_pol_abc123...`
- Suetonius: "Caesar was consul in 59 BCE" → `fclaim_pol_xyz789...`
- **Different ciphers for same fact!**

**Problem:** Cannot detect cross-source corroboration automatically.

---

## Decision

**Tier 3 cipher uses COMPOUND STRUCTURE: pattern prefix (canonical) + attestation suffix (source-specific)**

### **Compound Cipher Format:**

```
fclaim_{facet}_{pattern_hash}:{source_qid}:{passage_hash}

Example:
fclaim_pol_a1b2c3d4e5f6g7h8:Q193291:c4e5
└─────── pattern ──────────┘└─ source ┘└─┘
                                      passage
```

**Components:**

| Component | Source | Example | Mutability |
|-----------|--------|---------|------------|
| **Pattern Prefix** | Hash(subject\|property\|object\|facet\|temporal\|qualifiers) | `fclaim_pol_a1b2c3d4e5f6g7h8` | Immutable |
| **Source QID** | Wikidata QID of source work | `:Q193291` | Immutable |
| **Passage Hash** | Hash(passage_locator)[:4] | `:c4e5` | Immutable |

**Full Cipher:** `fclaim_pol_a1b2c3d4e5f6g7h8:Q193291:c4e5` (unique per attestation)

---

### **Pattern Prefix Formula:**

```python
def build_pattern_prefix(
    subject_qid: str,
    property_pid: str,
    object_qid: str,
    facet_id: str,
    temporal_scope: str = "",
    qualifiers: dict = None
) -> str:
    """
    Build pattern prefix (canonical, source-agnostic).
    
    Same pattern from any source = same prefix.
    Multiple sources share this prefix.
    
    Returns:
        Pattern prefix (e.g., "fclaim_pol_a1b2c3d4e5f6g7h8")
    """
    import hashlib
    
    CIPHER_ELIGIBLE_QUALIFIERS = {"P276", "P1545"}
    
    # Extract and normalize qualifiers
    eligible = {}
    if qualifiers:
        for pid, value in qualifiers.items():
            if pid in CIPHER_ELIGIBLE_QUALIFIERS:
                eligible[pid] = normalize_qualifier_value(pid, value)
    
    # Sort qualifiers deterministically
    qualifier_string = "|".join(
        f"{pid}:{eligible[pid]}"
        for pid in sorted(eligible.keys())
    )
    
    # Pattern hash (NO source, NO passage, NO confidence, NO agent, NO timestamp)
    pattern_data = (
        f"{subject_qid}|"
        f"{property_pid}|"
        f"{object_qid}|"
        f"{facet_id.upper()}|"
        f"{temporal_scope}|"
        f"{qualifier_string}"
    )
    
    hash_value = hashlib.sha256(pattern_data.encode()).hexdigest()
    facet_prefix = FACET_PREFIXES[facet_id.upper()]
    
    return f"fclaim_{facet_prefix}_{hash_value[:16]}"


def build_compound_cipher(
    pattern_prefix: str,
    source_qid: str,
    passage_locator: str
) -> str:
    """
    Build full compound cipher (pattern + attestation).
    
    Returns:
        Full cipher (e.g., "fclaim_pol_a1b2...:Q193291:c4e5")
    """
    import hashlib
    
    # Hash passage to 4-char suffix
    passage_hash = hashlib.sha256(passage_locator.encode()).hexdigest()[:4]
    
    return f"{pattern_prefix}:{source_qid}:{passage_hash}"


def build_tier3_cipher_complete(
    subject_qid: str,
    property_pid: str,
    object_qid: str,
    facet_id: str,
    temporal_scope: str,
    qualifiers: dict,
    source_qid: str,
    passage_locator: str
) -> tuple[str, str]:
    """
    Build both pattern prefix and full compound cipher.
    
    Returns:
        (pattern_prefix, full_cipher) tuple
    """
    pattern_prefix = build_pattern_prefix(
        subject_qid, property_pid, object_qid, facet_id,
        temporal_scope, qualifiers
    )
    
    full_cipher = build_compound_cipher(
        pattern_prefix, source_qid, passage_locator
    )
    
    return pattern_prefix, full_cipher
```

---

## Rationale

### **1. Enables Cross-Source Corroboration**

**Before (source in cipher):**
```
Plutarch → cipher_ABC (confidence: 0.85)
Suetonius → cipher_XYZ (confidence: 0.90)
Claims Manager: 2 different claims, no corroboration detected
```

**After (source as attestation):**
```
Pattern cipher_123:
  ← Plutarch (confidence: 0.85)
  ← Suetonius (confidence: 0.90)
Claims Manager: Same pattern, 2 attestations → aggregate confidence: 0.95
```

---

### **2. Restores Original Vision**

**Original Concept:**
> "Cipher as the unique fingerprint of a constellation of entities converging at a point in space-time."

**What Got Lost:**
- Source was added to cipher hash
- Turned pattern signature into provenance-specific claim ID
- Prevented corroboration detection

**What's Restored:**
- Cipher = pattern identity (who × what × where × when)
- Source = attestation (evidence pointing to pattern)
- Multiple sources → one pattern, many attestations

---

### **3. Cleaner Separation of Concerns**

| Concern | Where It Lives | Mutability |
|---------|---------------|------------|
| **Pattern** | FacetClaim node (cipher) | Immutable |
| **Provenance** | ATTESTATION relationship | Accumulates |
| **Confidence** | ATTESTATION properties | Mutable per source |
| **Analysis Layer** | ATTESTATION properties | Per source (Plutarch = in_situ) |

**Pattern is immutable.** Evidence accumulates around it.

---

### **4. Simpler Claims Manager Logic**

**Current (source in cipher):**
```python
# Manual corroboration detection
plutarch_claim = get_claim("cipher_ABC")
suetonius_claim = get_claim("cipher_XYZ")
# How to know they're about same pattern? Complex matching logic!
```

**Revised (source as attestation):**
```python
# Automatic corroboration
pattern = get_pattern("cipher_123")
attestations = get_attestations(pattern.cipher)
aggregate_confidence = avg([att.confidence for att in attestations])
source_count = len(attestations)

if source_count >= 2:
    confidence_boost = 0.10  # Multiple independent sources
    final_confidence = min(aggregate_confidence + confidence_boost, 1.0)
```

---

## Consequences

### **Benefits:**
- ✅ Cross-source corroboration (automatic)
- ✅ Aggregate confidence (multiple attestations)
- ✅ Cleaner ontology (pattern vs evidence)
- ✅ Restores original vision
- ✅ Enables source disagreement detection
- ✅ Simplifies Claims Manager

### **Costs:**
- ⚠️ Breaking change (existing Tier 3 ciphers invalid)
- ⚠️ Migration required (regenerate ciphers for existing claims)
- ⚠️ New relationship type (ATTESTATION)
- ⚠️ Schema change (FacetClaim node properties shift to ATTESTATION edge)

### **Migration Impact:**
- Current: 0 FacetClaim nodes (not implemented yet)
- **Good timing!** No existing data to migrate.
- Can implement correctly from the start.

---

## Implementation

### **Updated FacetClaim Node Schema**

```cypher
(:FacetClaim {
  // ═══════════════════════════════════════════════
  // PATTERN IDENTITY (Immutable)
  // ═══════════════════════════════════════════════
  cipher: "fclaim_pol_a1b2c3d4e5f6g7h8",      // Pattern signature
  
  // ═══════════════════════════════════════════════
  // PATTERN COMPONENTS (Who × What × Where × When)
  // ═══════════════════════════════════════════════
  subject_entity_cipher: "ent_per_Q1048",     // Who (Caesar)
  property_pid: "P39",                         // What (position held)
  object_qid: "Q39686",                        // To what (consul)
  facet_id: "POLITICAL",                       // Analytical lens
  
  // Temporal (When)
  temporal_scope: "-0059/-0058",
  temporal_start_year: -59,
  temporal_end_year: -58,
  temporal_calendar: "julian",
  
  // Spatial (Where) - from P276 qualifier
  location_qid: "Q220",                        // Rome
  
  // Ordinal (Which) - from P1545 qualifier
  ordinal: 1,                                  // First consulship
  
  // ═══════════════════════════════════════════════
  // AGGREGATE METADATA (Computed from Attestations)
  // ═══════════════════════════════════════════════
  attestation_count: 2,                        // How many sources
  aggregate_confidence: 0.875,                 // Avg across attestations
  max_confidence: 0.90,                        // Highest single source
  min_confidence: 0.85,                        // Lowest single source
  consensus_level: "HIGH",                     // 2+ sources agree
  
  // ═══════════════════════════════════════════════
  // NO SOURCE PROPERTIES HERE (Moved to ATTESTATION)
  // ═══════════════════════════════════════════════
  // source_qid: REMOVED (now on ATTESTATION edge)
  // passage_locator: REMOVED (now on ATTESTATION edge)
  // confidence: REMOVED (now on ATTESTATION edge)
})
```

---

### **ATTESTATION Relationship Schema**

```cypher
(:FacetClaim {cipher: "fclaim_pol_a1b2..."})
  <-[:ATTESTED_BY {
    // ═══════════════════════════════════════════════
    // PROVENANCE (Who Says It)
    // ═══════════════════════════════════════════════
    source_qid: "Q193291",                   // Plutarch
    passage_locator: "Lives.Caesar.11",      // Where in source
    
    // ═══════════════════════════════════════════════
    // EVIDENCE QUALITY (How Confident)
    // ═══════════════════════════════════════════════
    confidence: 0.85,                        // This source's confidence
    analysis_layer: "in_situ",               // Ancient vs modern
    
    // ═══════════════════════════════════════════════
    // EXTRACTION METADATA (Who Extracted, When)
    // ═══════════════════════════════════════════════
    extracted_by_agent: "SFA_POLITICAL_RR",
    extracted_at: "2026-02-21T10:00:00Z",
    
    // ═══════════════════════════════════════════════
    // DETERMINATION (How We Know)
    // ═══════════════════════════════════════════════
    determination_method: "stated",          // P459 (stated vs inferred)
    sourcing_circumstances: "primary"        // P1480
  }]-
(:Entity {entity_cipher: "ent_wrk_Q193291"})  // Source work
```

---

### **Query Patterns (Index Seeks, Not Traversal)**

**Find all attestations for a pattern (O(1) prefix match):**
```cypher
// All sources attesting to same pattern
MATCH (c:FacetClaim)
WHERE c.pattern_cipher = "fclaim_pol_a1b2c3d4e5f6g7h8"
  // OR: c.cipher STARTS WITH "fclaim_pol_a1b2c3d4e5f6g7h8:"
RETURN 
  c.cipher as full_cipher,
  c.source_qid as source,
  c.passage_locator as citation,
  c.confidence as confidence
ORDER BY c.confidence DESC

// Returns:
// fclaim_pol_a1b2...:Q211146:f7a2 | Q211146 (Suetonius) | Jul.20 | 0.90
// fclaim_pol_a1b2...:Q193291:c4e5 | Q193291 (Plutarch) | Caes.11 | 0.85
// fclaim_pol_a1b2...:Q151055:81d3 | Q151055 (Appian) | BC.2.10 | 0.82
```

**Detect corroboration (aggregate confidence):**
```cypher
// Patterns with 2+ independent sources
MATCH (c:FacetClaim)
WITH c.pattern_cipher as pattern,
     count(c) as source_count,
     avg(c.confidence) as avg_confidence,
     collect(c.source_qid) as sources
WHERE source_count >= 2
RETURN 
  pattern,
  source_count,
  avg_confidence,
  sources
ORDER BY source_count DESC, avg_confidence DESC
```

**Detect source disagreement:**
```cypher
// Patterns where sources disagree (>20% confidence variance)
MATCH (c:FacetClaim)
WITH c.pattern_cipher as pattern,
     max(c.confidence) as max_conf,
     min(c.confidence) as min_conf,
     count(c) as source_count
WHERE source_count >= 2
  AND max_conf - min_conf > 0.20
RETURN 
  pattern,
  "Sources disagree!" as alert,
  source_count,
  max_conf - min_conf as variance
ORDER BY variance DESC
```

**Get best attestation for a pattern:**
```cypher
// Highest-confidence source for this pattern
MATCH (c:FacetClaim {pattern_cipher: "fclaim_pol_a1b2..."})
RETURN c
ORDER BY c.confidence DESC
LIMIT 1
```

**Timeline convergence (all patterns at intersection):**
```cypher
// Everything about Caesar in Rome in 59 BCE (all facets, all sources)
MATCH (c:FacetClaim)
WHERE c.subject_entity_cipher = "ent_per_Q1048"
  AND c.location_qid = "Q220"
  AND c.temporal_scope CONTAINS "-0059"
RETURN 
  c.pattern_cipher,
  c.facet_id,
  c.property_pid,
  count(*) as attestation_count
ORDER BY c.facet_id
```

---

## Three-Layer Pattern Architecture

### **Layer 0: Core Pattern** (Person × Place × Time)

**Purpose:** Base convergence — shared by all claims about this intersection

```python
core_pattern_hash = sha256(
    f"{subject_qid}|{location_qid}|{temporal_scope}"
).hexdigest()[:16]

# Example:
# Q1048 × Q220 × -0059 = "Caesar in Rome, 59 BCE"
```

**Use Case:** Timeline UI — click convergence point, see all facets

**Query:**
```cypher
// All patterns at Caesar × Rome × 59 BCE
MATCH (p:FacetClaim)
WHERE p.subject_entity_cipher = "ent_per_Q1048"
  AND p.location_qid = "Q220"
  AND p.temporal_scope CONTAINS "-0059"
RETURN p.cipher, p.facet_id, p.property_pid
```

---

### **Layer 1: Enriched Pattern** (Person × Role × Place × Time)

**Purpose:** Specific action/relationship at the convergence

```python
enriched_pattern_cipher = f"fclaim_{facet_prefix}_{hash[:16]}"

hash_input = (
    f"{subject_qid}|"        # Who
    f"{property_pid}|"        # What relationship
    f"{object_qid}|"          # To whom/what
    f"{facet_id}|"            # Analytical lens
    f"{temporal_scope}|"      # When
    f"{qualifier_string}"     # Where (P276), which (P1545)
    # NO source!
)
```

**Distinguishes:**
- "Caesar as consul in Rome" vs "Caesar as debtor in Rome"
- Same core pattern, different enrichments

---

### **Layer 2: Faceted Evaluation** (Pattern × Lens)

**Purpose:** Same pattern, different analytical perspectives

```
Pattern: Caesar held consulship in Rome, 59 BCE

× POLITICAL facet → "What power did this confer?"
× ECONOMIC facet → "What fiscal authority?"
× MILITARY facet → "What command?"

Same pattern, different questions.
```

**Each facet produces its own cipher:**
- `fclaim_pol_a1b2...` (political analysis)
- `fclaim_eco_c3d4...` (economic analysis)
- `fclaim_mil_e5f6...` (military analysis)

---

## Compound Cipher Structure (Pattern + Attestation)

### **Design: Structure in the String**

**Instead of:** Pattern node + ATTESTATION edges (requires traversal)  
**Use:** Compound cipher with visible pattern prefix (index seek)

```
Pattern Prefix (Canonical): fclaim_pol_a1b2c3d4e5f6g7h8
Full Cipher 1: fclaim_pol_a1b2c3d4e5f6g7h8:Q193291:c4e5 (Plutarch)
Full Cipher 2: fclaim_pol_a1b2c3d4e5f6g7h8:Q211146:f7a2 (Suetonius)
Full Cipher 3: fclaim_pol_a1b2c3d4e5f6g7h8:Q151055:81d3 (Appian)
```

**Delimiter:** `:` (consistent with Wikidata statement addressing)

---

### **Graph Structure (Multiple FacetClaim Nodes):**

```cypher
// Plutarch's attestation (full cipher unique)
(claim1:FacetClaim {
  cipher: "fclaim_pol_a1b2c3d4e5f6g7h8:Q193291:c4e5",  // Unique per source
  pattern_cipher: "fclaim_pol_a1b2c3d4e5f6g7h8",        // Shared prefix
  
  // Pattern fields (define the prefix)
  subject_entity_cipher: "ent_per_Q1048",
  property_pid: "P39",
  object_qid: "Q39686",
  facet_id: "POLITICAL",
  temporal_scope: "-0059/-0058",
  location_qid: "Q220",
  ordinal: 1,
  
  // Attestation fields (define the suffix)
  source_qid: "Q193291",                               // Plutarch
  passage_locator: "Lives.Caesar.11",
  passage_hash: "c4e5",
  
  // Mutable (never in cipher)
  confidence: 0.85,
  analysis_layer: "in_situ",
  extracted_by: "SFA_POLITICAL_RR",
  extracted_at: "2026-02-21T10:00:00Z"
})

// Suetonius's attestation (same pattern, different source)
(claim2:FacetClaim {
  cipher: "fclaim_pol_a1b2c3d4e5f6g7h8:Q211146:f7a2",  // Different suffix
  pattern_cipher: "fclaim_pol_a1b2c3d4e5f6g7h8",        // SAME prefix!
  
  // Pattern fields (IDENTICAL to claim1)
  subject_entity_cipher: "ent_per_Q1048",
  property_pid: "P39",
  object_qid: "Q39686",
  facet_id: "POLITICAL",
  temporal_scope: "-0059/-0058",
  location_qid: "Q220",
  ordinal: 1,
  
  // Attestation fields (DIFFERENT from claim1)
  source_qid: "Q211146",                               // Suetonius
  passage_locator: "Jul.20",
  passage_hash: "f7a2",
  
  // Mutable
  confidence: 0.90,
  analysis_layer: "in_situ",
  extracted_by: "SFA_POLITICAL_RR",
  extracted_at: "2026-02-21T12:30:00Z"
})

// Appian's attestation (same pattern, third source)
(claim3:FacetClaim {
  cipher: "fclaim_pol_a1b2c3d4e5f6g7h8:Q151055:81d3",
  pattern_cipher: "fclaim_pol_a1b2c3d4e5f6g7h8",        // SAME prefix!
  
  // Pattern fields (IDENTICAL)
  subject_entity_cipher: "ent_per_Q1048",
  property_pid: "P39",
  object_qid: "Q39686",
  facet_id: "POLITICAL",
  temporal_scope: "-0059/-0058",
  location_qid: "Q220",
  ordinal: 1,
  
  // Attestation fields (DIFFERENT)
  source_qid: "Q151055",                               // Appian
  passage_locator: "BC.2.10",
  passage_hash: "81d3",
  
  // Mutable
  confidence: 0.82,
  analysis_layer: "in_situ",
  extracted_by: "SFA_POLITICAL_RR",
  extracted_at: "2026-02-21T14:00:00Z"
})
```

**Structure:**
- 3 separate FacetClaim nodes (one per source)
- All share `pattern_cipher` (visible pattern identity)
- Each has unique `cipher` (provenance distinct)
- No edges needed! (corroboration via prefix match)

---

## Comparison: Three Approaches

### **Approach 1: Source in Hash (Current v1.0)**

```
Plutarch → fclaim_pol_xyz789...
Suetonius → fclaim_pol_abc123...
(opaque hashes, no visible shared pattern)
```

**Advantages:**
- Simple: one claim per extraction
- Provenance embedded

**Disadvantages:**
- ❌ Can't see pattern commonality
- ❌ No corroboration detection
- ❌ Violates original vision

---

### **Approach 2: ATTESTATION Edges (Graph Architect's First Revision)**

```
(Pattern {cipher: "fclaim_pol_a1b2..."})
  <-[:ATTESTED_BY {source, passage, confidence}]-
(Source)
```

**Advantages:**
- ✅ Pattern visible (one node)
- ✅ Corroboration works
- ✅ Aggregate confidence

**Disadvantages:**
- ⚠️ Requires graph traversal (walk ATTESTATION edges)
- ⚠️ More complex schema (pattern nodes + attestation edges)
- ⚠️ Inconsistent with vertex-jump philosophy (not O(1))

---

### **Approach 3: Compound Cipher (BEST — Advisor's Synthesis)**

```
fclaim_pol_a1b2c3d4e5f6g7h8:Q193291:c4e5  (Plutarch)
fclaim_pol_a1b2c3d4e5f6g7h8:Q211146:f7a2  (Suetonius)
fclaim_pol_a1b2c3d4e5f6g7h8:Q151055:81d3  (Appian)
└─────── pattern ──────────┘
  Pattern visible! Corroboration = prefix match
```

**Advantages:**
- ✅ Pattern visible in string (self-documenting)
- ✅ Corroboration = index seek (`STARTS WITH` or `pattern_cipher =`)
- ✅ No graph traversal (O(1) like vertex jumps)
- ✅ Simpler schema (just nodes, no special edges)
- ✅ Restores original vision
- ✅ Consistent with cipher philosophy

**Disadvantages:**
- ⚠️ Longer cipher string (but still deterministic)
- ⚠️ Need `pattern_cipher` property (redundant with prefix, but indexed for speed)

**Winner:** Approach 3 — Compound cipher combines elegance of pattern visibility with O(1) performance.

---

## Why Compound Cipher is Architecturally Superior

### **1. Structure in the String (Self-Documenting)**

```
fclaim_pol_a1b2c3d4e5f6g7h8:Q193291:c4e5

Human reads this:
  - Political facet (pol)
  - Pattern hash a1b2...
  - Source: Q193291 (Plutarch)
  - Passage: c4e5 hash

No graph query needed to understand it!
```

---

### **2. O(1) Corroboration (Index Seek, Not Traversal)**

```cypher
// Find all attestations (prefix match on indexed property)
MATCH (c:FacetClaim {pattern_cipher: "fclaim_pol_a1b2..."})
RETURN c

// O(1) index seek, not O(n) edge traversal
// Consistent with vertex-jump philosophy
```

**vs ATTESTATION edge approach:**
```cypher
// Requires traversal
MATCH (pattern)<-[:ATTESTED_BY]-()
// O(n) where n = number of attestations
```

---

### **3. Aggregate Metrics (Optional Pre-Computation)**

```cypher
// Compute once, store on any claim with this pattern_cipher
MATCH (c:FacetClaim {pattern_cipher: "fclaim_pol_a1b2..."})
WITH c.pattern_cipher as pattern,
     count(c) as attestation_count,
     avg(c.confidence) as aggregate_conf,
     collect(c.source_qid) as sources

// Update all claims with this pattern (denormalized for speed)
MATCH (c2:FacetClaim {pattern_cipher: pattern})
SET c2.attestation_count = attestation_count,
    c2.aggregate_confidence = aggregate_conf,
    c2.consensus_level = CASE
      WHEN attestation_count >= 3 THEN "HIGH"
      WHEN attestation_count = 2 THEN "MEDIUM"
      ELSE "LOW"
    END

RETURN pattern, attestation_count, aggregate_conf
```

**Optional:** Store aggregate metrics on each claim (denormalized)  
**Benefit:** Query performance (no recomputation needed)

---

### **4. No Special Relationship Type**

**Compound cipher uses:**
- Standard FacetClaim nodes
- Standard properties (cipher, pattern_cipher, source_qid)
- Standard indexes (cipher unique, pattern_cipher composite)

**No need for:**
- ❌ ATTESTATION relationship type
- ❌ Edge property schema for ATTESTATION
- ❌ Edge traversal queries

**Simpler overall architecture.**

---

## Migration Plan

### **Current State:**
- FacetClaim nodes: 0 (not implemented yet)
- **Perfect timing** — can implement correctly from the start!

### **If FacetClaims existed:**

```cypher
// Step 1: Regenerate ciphers (remove source from hash)
MATCH (old:FacetClaim)
WITH old,
  // Recompute cipher without source
  fclaim_pol_ + sha256(
    old.subject_entity_cipher + "|" +
    old.property_pid + "|" +
    old.object_qid + "|" +
    old.facet_id + "|" +
    old.temporal_scope + "|" +
    coalesce(old.qualifier_string, "")
  )[:16] as new_cipher

// Step 2: Merge patterns (same new_cipher → one pattern)
MERGE (pattern:FacetClaim {cipher: new_cipher})
ON CREATE SET 
  pattern = old,
  pattern.attestation_count = 1
ON MATCH SET
  pattern.attestation_count = pattern.attestation_count + 1

// Step 3: Create attestation
CREATE (pattern)<-[:ATTESTED_BY {
  source_qid: old.source_qid,
  passage_locator: old.passage_locator,
  confidence: old.confidence,
  extracted_by: old.created_by_agent,
  extracted_at: old.created_at
}]-(source:Entity {qid: old.source_qid})

// Step 4: Delete old claim
DELETE old
```

---

## Neo4j Schema Changes

### **New Constraint:**
```cypher
// Attestations must be unique per source + pattern
CREATE CONSTRAINT attestation_unique IF NOT EXISTS
FOR ()-[a:ATTESTED_BY]-()
REQUIRE (a.source_qid, a.pattern_cipher) IS UNIQUE;
```

### **New Indexes:**
```cypher
// Query by source
CREATE INDEX attestation_source_idx IF NOT EXISTS
FOR ()-[a:ATTESTED_BY]-()
ON (a.source_qid);

// Query by confidence
CREATE INDEX attestation_confidence_idx IF NOT EXISTS
FOR ()-[a:ATTESTED_BY]-()
ON (a.confidence);

// Query by extraction date
CREATE INDEX attestation_date_idx IF NOT EXISTS
FOR ()-[a:ATTESTED_BY]-()
ON (a.extracted_at);
```

---

## Updated Pydantic Models

```python
class FacetClaimPattern(BaseModel):
    """Pattern-centric claim (source-agnostic)"""
    
    # Pattern identity
    cipher: str = Field(..., pattern=r"^fclaim_[a-z]{3}_[a-f0-9]{16}$")
    
    # Pattern components (NO source!)
    subject_entity_cipher: str
    property_pid: str
    object_qid: str
    facet_id: Literal[...]  # 18 canonical facets
    temporal_scope: Optional[str]
    location_qid: Optional[str]
    ordinal: Optional[int]
    
    # Aggregate metrics (computed from attestations)
    attestation_count: int = Field(0, ge=0)
    aggregate_confidence: float = Field(0.0, ge=0.0, le=1.0)
    consensus_level: Literal["NONE", "LOW", "MEDIUM", "HIGH"]


class Attestation(BaseModel):
    """Source attestation of a pattern"""
    
    # Provenance (source-specific)
    source_qid: str = Field(..., pattern=r"^Q\d+$")
    passage_locator: str
    
    # Evidence quality
    confidence: float = Field(..., ge=0.0, le=1.0)
    analysis_layer: Literal["in_situ", "retrospective"]
    
    # Extraction metadata
    extracted_by_agent: str
    extracted_at: datetime
    
    # Determination
    determination_method: Optional[str]
    sourcing_circumstances: Optional[str]
```

---

## Validation

### **Check Pattern Uniqueness:**
```cypher
// No duplicate patterns
MATCH (p:FacetClaim)
WITH p.cipher, count(*) as dupe_count
WHERE dupe_count > 1
RETURN p.cipher, dupe_count
// Should return: 0 rows
```

### **Check Attestation Integrity:**
```cypher
// All patterns have at least 1 attestation
MATCH (p:FacetClaim)
WHERE NOT (p)<-[:ATTESTED_BY]-()
RETURN p.cipher, "Missing attestation!" as error
// Should return: 0 rows
```

### **Check Aggregate Confidence:**
```cypher
// Verify aggregate = avg of attestations
MATCH (p:FacetClaim)<-[att:ATTESTED_BY]-()
WITH p, 
     avg(att.confidence) as calc_avg,
     p.aggregate_confidence as stored_avg
WHERE abs(calc_avg - stored_avg) > 0.01
RETURN p.cipher, calc_avg, stored_avg, "Mismatch!" as error
// Should return: 0 rows
```

---

## References

- **ADR-001:** Claim Identity Ciphers (confidence/agent/timestamp exclusion)
- **ADR-012:** Pattern-Centric Ciphers (source exclusion) — THIS DOCUMENT
- **ENTITY_CIPHER_FOR_VERTEX_JUMPS.md:** Three-tier cipher system
- **TIER_3_CLAIM_CIPHER_ADDENDUM.md:** Qualifier integration

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| **Feb 22, 2026** | **1.0** | **Proposed: Pattern-centric Tier 3 ciphers, source as attestation, breaking change specification** |

---

**Document Status:** ✅ PROPOSED (Awaiting Approval)  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026  
**Impact:** Breaking change to Tier 3 — but perfect timing (no existing claims to migrate)
