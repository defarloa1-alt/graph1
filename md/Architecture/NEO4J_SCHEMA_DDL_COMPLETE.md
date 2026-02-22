# Neo4j Schema DDL: Complete Specification

**Created:** February 22, 2026  
**Status:** Canonical Reference  
**Revision:** 1.0  
**Related:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md, CLAIM_ID_ARCHITECTURE.md

---

## Table of Contents

1. [ADR-002: TemporalAnchor Multi-Label Pattern](#adr-002-temporalanchor-multi-label-pattern)
2. [Temporal Data Strategy](#temporal-data-strategy)
3. [Constraints](#constraints)
4. [Indexes](#indexes)
5. [MERGE + Label Interaction Warning](#merge--label-interaction-warning)
6. [Complete DDL Script](#complete-ddl-script)

---

## ADR-002: TemporalAnchor Multi-Label Pattern

**Status:** Accepted (February 22, 2026)

### Context

The "Period Problem" identified in `md/Architecture/perplexity-on-periods.md` stems from entities like Q17167 (Roman Republic) being simultaneously:
- A temporal anchor (defines a time span: 509-27 BCE)
- An organization/polity (has government, territory, institutions)
- A SubjectConcept (thematic research anchor)

The initial design attempted to classify these as a single `PERIOD` entity type, creating ambiguity and classification failures in the SCA.

### Decision

**Separate temporal anchoring (a capability) from entity classification (the type).**

Use **multi-label nodes** to express that an entity can serve multiple roles:

```cypher
// Roman Republic: organization that ALSO defines a temporal scope
(:Entity:Organization:TemporalAnchor {
  entity_cipher: "ent_org_Q17167",
  entity_type: "ORGANIZATION",          // Primary classification
  qid: "Q17167",
  
  // Temporal anchor properties
  is_temporal_anchor: true,              // Application-layer flag
  temporal_scope: "-0509/-0027",         // ISO 8601 interval (canonical)
  temporal_start_year: -509,             // Integer for range queries
  temporal_end_year: -27,                // Integer for range queries
  temporal_calendar: "julian",           // Calendar system metadata
  
  // Standard entity properties
  label_en: "Roman Republic",
  namespace: "wd"
})

// Stone Age: purely a temporal designation (not an institution)
(:Entity:Period:TemporalAnchor {
  entity_cipher: "ent_prd_Q6813",
  entity_type: "PERIOD",                 // Primary classification
  qid: "Q6813",
  
  is_temporal_anchor: true,
  temporal_scope: "-3300/-1200",
  temporal_start_year: -3300,
  temporal_end_year: -1200,
  temporal_calendar: "gregorian_approx"
})
```

### Multi-Label Pattern

**Use BOTH label and property for `is_temporal_anchor`:**

| Mechanism | Purpose | Used By |
|-----------|---------|---------|
| `:TemporalAnchor` label | Fast label-scan queries in Neo4j | Cypher queries, graph traversal |
| `is_temporal_anchor: true` property | Conditional logic in application code | Pydantic models, SCA classification, agent routing |

**Rationale for Redundancy:**
- **Label**: Neo4j-native optimization (enables `MATCH (n:TemporalAnchor)` with O(1) label scan)
- **Property**: Application-layer field (enables Pydantic validation, agent decision logic)
- Intentionally redundant for separation of concerns between database and application layers

### Neo4j 5.18+ Label Intersection Syntax

Query entities that are BOTH organizations AND temporal anchors:

```cypher
// Traditional syntax
MATCH (n:Entity:Organization:TemporalAnchor)
RETURN n;

// Neo4j 5.18+ ampersand syntax (label intersection)
MATCH (n:Entity&Organization&TemporalAnchor)
RETURN n;
```

### Consequences

**Benefits:**
- ✅ Resolves period vs polity classification ambiguity
- ✅ Enables queries like "all organizations that define temporal periods"
- ✅ Aligns with Neo4j best practices (labels for frequently-queried characteristics)
- ✅ Supports multiple temporal anchors per entity (e.g., Byzantine Empire as both polity and period)

**Constraints:**
- All nodes with `:TemporalAnchor` label MUST have `temporal_start_year` and `temporal_end_year` properties
- SCA must add `:TemporalAnchor` label when temporal properties are present
- Dev agent must handle label addition in MERGE operations (see §5)

**Migration:**
- Backfill `:TemporalAnchor` label for existing entities with temporal properties
- Update SCA classification rules to detect temporal anchor eligibility

---

## Temporal Data Strategy

### The Calendar System Problem

**Critical Issue:** Neo4j's native `DATE` type uses the **proleptic Gregorian calendar**, which diverges from the Julian calendar used in ancient Rome.

**Impact:**
- `DATE('-0044-03-15')` in Neo4j represents March 15, 44 BCE in **Gregorian calendar**
- The actual Ides of March (Julius Caesar's assassination) occurred in **Julian calendar**
- These are **different days** (approximately 2 days offset in 44 BCE)

**Consequence:** Using native `DATE` for BCE dates causes **data integrity failures** — the stored date does not represent the historical event accurately.

### Solution: Hybrid Schema

Store dates in **three representations** for different use cases:

```cypher
(:Entity:TemporalAnchor {
  // ISO 8601 interval string (canonical, human-readable)
  temporal_scope: "-0509/-0027",
  
  // Integer year fields (fast range queries)
  temporal_start_year: -509,
  temporal_end_year: -27,
  
  // Calendar system metadata (data quality)
  temporal_calendar: "julian",
  
  // Optional: precision metadata
  temporal_precision: "year",          // "year" | "month" | "day" | "circa"
  temporal_uncertainty: false           // Flag uncertain dates
})
```

### Field Specifications

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `temporal_scope` | String | Canonical ISO 8601 interval, used for cipher computation and display | `"-0509/-0027"` |
| `temporal_start_year` | Integer | Fast range queries, timeline ordering | `-509` |
| `temporal_end_year` | Integer | Fast range queries, period nesting | `-27` |
| `temporal_calendar` | String | Metadata: which calendar system the dates represent | `"julian"`, `"gregorian"`, `"gregorian_approx"` |
| `temporal_precision` | String (optional) | Granularity of date knowledge | `"year"`, `"month"`, `"day"`, `"circa"` |
| `temporal_uncertainty` | Boolean (optional) | Flag for contested or uncertain dates | `true` if disputed |

### Index Strategy

```cypher
// Range query index (most common temporal query pattern)
CREATE INDEX temporal_range_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_start_year, n.temporal_end_year);

// Period nesting queries (find periods contained within another period)
CREATE INDEX temporal_nesting_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_start_year);
```

**Property Ordering Rationale:**
- `temporal_start_year` is more selective than `temporal_end_year` (many periods can end in the same year, fewer start in the same year)
- Neo4j composite indexes perform best when most selective property comes first

### Query Patterns

**Find all entities active in 100 BCE:**
```cypher
MATCH (n:TemporalAnchor)
WHERE n.temporal_start_year <= -100 
  AND n.temporal_end_year >= -100
RETURN n.entity_cipher, n.label_en, n.temporal_scope;
```

**Find periods nested within Roman Republic:**
```cypher
MATCH (parent:TemporalAnchor {qid: "Q17167"})
MATCH (child:TemporalAnchor)
WHERE child.temporal_start_year >= parent.temporal_start_year
  AND child.temporal_end_year <= parent.temporal_end_year
  AND child.entity_cipher <> parent.entity_cipher
RETURN child.entity_cipher, child.label_en;
```

---

## Constraints

### Design Principles

1. **Uniqueness constraints auto-create indexes** — No need for separate `CREATE INDEX` on fields with `REQUIRE ... IS UNIQUE`
2. **Multi-property constraints** enforce combination uniqueness, not individual value uniqueness
3. **Constraints enable MERGE idempotency** — Critical for REQ-FUNC-001 verified pattern

### Tier 1: Entity Cipher Constraints

```cypher
// Entity cipher uniqueness (PRIMARY KEY equivalent)
CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.entity_cipher IS UNIQUE;

// QID uniqueness (prevent duplicate Wikidata entities)
CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.qid IS UNIQUE;

// Existence constraint: entity_cipher required on all Entity nodes
CREATE CONSTRAINT entity_cipher_exists IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.entity_cipher IS NOT NULL;

// Existence constraint: entity_type required for classification
CREATE CONSTRAINT entity_type_exists IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.entity_type IS NOT NULL;
```

### Tier 2: Faceted Entity Cipher Constraints

```cypher
// Faceted cipher uniqueness (PRIMARY KEY for subgraph addresses)
CREATE CONSTRAINT faceted_cipher_unique IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.faceted_cipher IS UNIQUE;

// Composite constraint: entity + facet + subjectconcept uniqueness
// (Ensures one FacetedEntity per entity-facet-subject combination)
CREATE CONSTRAINT faceted_composite_unique IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE (n.entity_cipher, n.facet_id, n.subjectconcept_id) IS UNIQUE;

// Existence constraints
CREATE CONSTRAINT faceted_entity_cipher_exists IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.entity_cipher IS NOT NULL;

CREATE CONSTRAINT faceted_facet_id_exists IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.facet_id IS NOT NULL;

CREATE CONSTRAINT faceted_subjectconcept_exists IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.subjectconcept_id IS NOT NULL;
```

### Tier 3: Claim Cipher Constraints

```cypher
// Claim cipher uniqueness (PRIMARY KEY for assertions)
CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.cipher IS UNIQUE;

// Subject entity cipher existence (all claims must have a subject)
CREATE CONSTRAINT claim_subject_exists IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.subject_entity_cipher IS NOT NULL;

// Facet ID existence (all claims belong to a facet)
CREATE CONSTRAINT claim_facet_exists IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.facet_id IS NOT NULL;

// Analysis layer existence (in_situ vs retrospective)
CREATE CONSTRAINT claim_analysis_layer_exists IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.analysis_layer IS NOT NULL;
```

### TemporalAnchor Constraints

```cypher
// Existence: All TemporalAnchor nodes must have start year
CREATE CONSTRAINT temporal_start_year_exists IF NOT EXISTS
FOR (n:TemporalAnchor)
REQUIRE n.temporal_start_year IS NOT NULL;

// Existence: All TemporalAnchor nodes must have end year
CREATE CONSTRAINT temporal_end_year_exists IF NOT EXISTS
FOR (n:TemporalAnchor)
REQUIRE n.temporal_end_year IS NOT NULL;

// Existence: All TemporalAnchor nodes must have temporal scope string
CREATE CONSTRAINT temporal_scope_exists IF NOT EXISTS
FOR (n:TemporalAnchor)
REQUIRE n.temporal_scope IS NOT NULL;
```

---

## Indexes

### Tier 1: Entity Indexes

```cypher
// QID lookup (already has uniqueness constraint, auto-indexed)
// No explicit CREATE INDEX needed

// Entity type + cipher composite (for type-scoped queries)
CREATE INDEX entity_type_cipher_idx IF NOT EXISTS
FOR (n:Entity)
ON (n.entity_type, n.entity_cipher);

// Namespace lookup (for authority cascade queries)
CREATE INDEX entity_namespace_idx IF NOT EXISTS
FOR (n:Entity)
ON (n.namespace);
```

**Property Ordering Rationale:**
- `entity_type` before `entity_cipher`: entity_type is more selective (9 types) than cipher (unique)
- Enables queries like "all PERSON entities" without full cipher scan

### Tier 2: Faceted Entity Indexes

```cypher
// Faceted cipher (already has uniqueness constraint, auto-indexed)
// No explicit CREATE INDEX needed

// Composite constraint (entity_cipher, facet_id, subjectconcept_id) auto-indexed
// No explicit CREATE INDEX needed

// Cross-facet jump index (entity + facet)
CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS
FOR (n:FacetedEntity)
ON (n.entity_cipher, n.facet_id);

// SubjectConcept-scoped facet lookup
CREATE INDEX faceted_subj_facet_idx IF NOT EXISTS
FOR (n:FacetedEntity)
ON (n.subjectconcept_id, n.facet_id);

// All facets for a SubjectConcept
CREATE INDEX faceted_subj_idx IF NOT EXISTS
FOR (n:FacetedEntity)
ON (n.subjectconcept_id);
```

**Property Ordering Rationale:**
- `entity_cipher` before `facet_id`: entity_cipher is unique (most selective), facet_id has only 18 values
- `subjectconcept_id` before `facet_id`: subjectconcept_id is more selective (thousands of values) than facet_id

### Tier 3: Claim Indexes

```cypher
// Claim cipher (already has uniqueness constraint, auto-indexed)
// No explicit CREATE INDEX needed

// Pattern matching: all claims for an entity
CREATE INDEX claim_entity_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subject_entity_cipher);

// Pattern matching: all claims for entity in a facet
CREATE INDEX claim_entity_facet_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subject_entity_cipher, c.facet_id);

// Pattern matching: all claims in a SubjectConcept
CREATE INDEX claim_subj_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subjectconcept_cipher);

// Analysis layer filtering (in_situ vs retrospective)
CREATE INDEX claim_analysis_layer_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.analysis_layer);

// Confidence-based queries
CREATE INDEX claim_confidence_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.confidence);
```

### TemporalAnchor Indexes

```cypher
// Range query index (most common temporal query pattern)
CREATE INDEX temporal_range_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_start_year, n.temporal_end_year);

// Period nesting queries
CREATE INDEX temporal_nesting_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_start_year);

// Calendar system lookup (for data quality queries)
CREATE INDEX temporal_calendar_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_calendar);
```

---

## MERGE + Label Interaction Warning

### ⚠️ CRITICAL: Labels Are NOT Updated by MERGE ON MATCH

**Problem:** When using `MERGE` to update existing entities, Neo4j **does not automatically update labels** on `ON MATCH` — only properties are updated.

**Impact:** If an entity gains temporal properties (e.g., new data from Wikidata provides start/end dates), the `:TemporalAnchor` label will NOT be added unless explicitly handled.

### Incorrect Pattern (Will Fail)

```cypher
// ❌ WRONG: Label not added on MATCH
MERGE (n:Entity {entity_cipher: $cipher})
ON CREATE SET n += $properties, n:TemporalAnchor
ON MATCH SET n += $properties
// If node exists, temporal properties updated but label NOT added!
```

### Correct Pattern (Explicitly Add Label)

```cypher
// ✅ CORRECT: Explicitly handle label addition
MERGE (n:Entity {entity_cipher: $cipher})
ON CREATE SET n += $properties
ON MATCH SET n += $properties

// Conditional label addition based on temporal properties
WITH n
WHERE n.temporal_start_year IS NOT NULL 
  AND n.temporal_end_year IS NOT NULL
  AND NOT n:TemporalAnchor
SET n:TemporalAnchor

RETURN n;
```

### Alternative Pattern (Set Label on Create and Conditionally on Match)

```cypher
// ✅ CORRECT: Label set during CREATE, checked during MATCH
MERGE (n:Entity {entity_cipher: $cipher})
ON CREATE SET 
  n += $properties,
  n:TemporalAnchor  // Safe: always add if temporal properties present
ON MATCH SET n += $properties

// Post-MERGE: Add label if temporal properties now present
WITH n
WHERE n.temporal_start_year IS NOT NULL 
  AND n.temporal_end_year IS NOT NULL
  AND NOT n:TemporalAnchor
SET n:TemporalAnchor

RETURN n;
```

### Flag for Dev Agent

**When implementing REQ-FUNC-001 entity import patterns:**

1. **Check for temporal properties** in the entity payload before MERGE
2. **Add `:TemporalAnchor` label** if `temporal_start_year` and `temporal_end_year` are present
3. **Use conditional SET** after MERGE to add label if it's missing
4. **Test both CREATE and MATCH** code paths to ensure label is applied correctly

**Test Case:**
```python
# First import: Entity without temporal data
entity_v1 = {
    "entity_cipher": "ent_org_Q17167",
    "qid": "Q17167",
    "label_en": "Roman Republic"
}
# Should create (:Entity) WITHOUT :TemporalAnchor label

# Second import: Same entity, now with temporal data
entity_v2 = {
    "entity_cipher": "ent_org_Q17167",
    "qid": "Q17167",
    "label_en": "Roman Republic",
    "temporal_start_year": -509,
    "temporal_end_year": -27
}
# Should update to (:Entity:TemporalAnchor) WITH label
```

---

## Complete DDL Script

```cypher
// ═══════════════════════════════════════════════════════════════
// CHRYSTALLUM NEO4J SCHEMA DDL
// Version: 1.0
// Date: February 22, 2026
// Purpose: Complete schema definition for three-tier cipher model
// ═══════════════════════════════════════════════════════════════

// ───────────────────────────────────────────────────────────────
// SECTION 1: TIER 1 CONSTRAINTS (Entity)
// ───────────────────────────────────────────────────────────────

// Primary key: entity_cipher uniqueness
CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.entity_cipher IS UNIQUE;

// Wikidata QID uniqueness (prevent duplicates)
CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.qid IS UNIQUE;

// Required fields
CREATE CONSTRAINT entity_cipher_exists IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.entity_cipher IS NOT NULL;

CREATE CONSTRAINT entity_type_exists IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.entity_type IS NOT NULL;

// ───────────────────────────────────────────────────────────────
// SECTION 2: TIER 1 INDEXES (Entity)
// ───────────────────────────────────────────────────────────────

// Type-scoped queries (entity_type is more selective)
CREATE INDEX entity_type_cipher_idx IF NOT EXISTS
FOR (n:Entity)
ON (n.entity_type, n.entity_cipher);

// Authority cascade queries
CREATE INDEX entity_namespace_idx IF NOT EXISTS
FOR (n:Entity)
ON (n.namespace);

// ───────────────────────────────────────────────────────────────
// SECTION 3: TIER 2 CONSTRAINTS (FacetedEntity)
// ───────────────────────────────────────────────────────────────

// Primary key: faceted_cipher uniqueness
CREATE CONSTRAINT faceted_cipher_unique IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.faceted_cipher IS UNIQUE;

// Composite uniqueness: one FacetedEntity per combination
CREATE CONSTRAINT faceted_composite_unique IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE (n.entity_cipher, n.facet_id, n.subjectconcept_id) IS UNIQUE;

// Required fields
CREATE CONSTRAINT faceted_entity_cipher_exists IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.entity_cipher IS NOT NULL;

CREATE CONSTRAINT faceted_facet_id_exists IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.facet_id IS NOT NULL;

CREATE CONSTRAINT faceted_subjectconcept_exists IF NOT EXISTS
FOR (n:FacetedEntity)
REQUIRE n.subjectconcept_id IS NOT NULL;

// ───────────────────────────────────────────────────────────────
// SECTION 4: TIER 2 INDEXES (FacetedEntity)
// ───────────────────────────────────────────────────────────────

// Cross-facet jump (entity_cipher is most selective)
CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS
FOR (n:FacetedEntity)
ON (n.entity_cipher, n.facet_id);

// SubjectConcept-facet queries
CREATE INDEX faceted_subj_facet_idx IF NOT EXISTS
FOR (n:FacetedEntity)
ON (n.subjectconcept_id, n.facet_id);

// All facets for a SubjectConcept
CREATE INDEX faceted_subj_idx IF NOT EXISTS
FOR (n:FacetedEntity)
ON (n.subjectconcept_id);

// ───────────────────────────────────────────────────────────────
// SECTION 5: TIER 3 CONSTRAINTS (FacetClaim)
// ───────────────────────────────────────────────────────────────

// Primary key: claim cipher uniqueness
CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.cipher IS UNIQUE;

// Required fields
CREATE CONSTRAINT claim_subject_exists IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.subject_entity_cipher IS NOT NULL;

CREATE CONSTRAINT claim_facet_exists IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.facet_id IS NOT NULL;

CREATE CONSTRAINT claim_analysis_layer_exists IF NOT EXISTS
FOR (c:FacetClaim)
REQUIRE c.analysis_layer IS NOT NULL;

// ───────────────────────────────────────────────────────────────
// SECTION 6: TIER 3 INDEXES (FacetClaim)
// ───────────────────────────────────────────────────────────────

// All claims for an entity
CREATE INDEX claim_entity_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subject_entity_cipher);

// All claims for entity in a facet
CREATE INDEX claim_entity_facet_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subject_entity_cipher, c.facet_id);

// All claims in a SubjectConcept
CREATE INDEX claim_subj_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.subjectconcept_cipher);

// Analysis layer filtering
CREATE INDEX claim_analysis_layer_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.analysis_layer);

// Confidence-based queries
CREATE INDEX claim_confidence_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.confidence);

// Qualifier-based queries (Wikidata triple pattern)
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

// Series ordinal queries
CREATE INDEX claim_ordinal_idx IF NOT EXISTS
FOR (c:FacetClaim)
ON (c.qualifier_p1545_ordinal);

// ───────────────────────────────────────────────────────────────
// SECTION 7: TEMPORAL ANCHOR CONSTRAINTS
// ───────────────────────────────────────────────────────────────

// Required temporal fields
CREATE CONSTRAINT temporal_start_year_exists IF NOT EXISTS
FOR (n:TemporalAnchor)
REQUIRE n.temporal_start_year IS NOT NULL;

CREATE CONSTRAINT temporal_end_year_exists IF NOT EXISTS
FOR (n:TemporalAnchor)
REQUIRE n.temporal_end_year IS NOT NULL;

CREATE CONSTRAINT temporal_scope_exists IF NOT EXISTS
FOR (n:TemporalAnchor)
REQUIRE n.temporal_scope IS NOT NULL;

// ───────────────────────────────────────────────────────────────
// SECTION 8: TEMPORAL ANCHOR INDEXES
// ───────────────────────────────────────────────────────────────

// Range queries (temporal_start_year is most selective)
CREATE INDEX temporal_range_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_start_year, n.temporal_end_year);

// Period nesting queries
CREATE INDEX temporal_nesting_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_start_year);

// Calendar system lookup
CREATE INDEX temporal_calendar_idx IF NOT EXISTS
FOR (n:TemporalAnchor)
ON (n.temporal_calendar);

// ═══════════════════════════════════════════════════════════════
// END OF SCHEMA DDL
// ═══════════════════════════════════════════════════════════════
```

---

## Validation Queries

### Verify Constraints

```cypher
// List all constraints
SHOW CONSTRAINTS;

// Verify constraint count (should be 17 total)
SHOW CONSTRAINTS YIELD name, entityType, labelsOrTypes, properties
RETURN count(*) AS total_constraints;
```

### Verify Indexes

```cypher
// List all indexes
SHOW INDEXES;

// Verify index count (should be 15 non-constraint indexes + constraint auto-indexes)
SHOW INDEXES YIELD name, labelsOrTypes, properties, type
RETURN count(*) AS total_indexes;
```

### Test TemporalAnchor Label Detection

```cypher
// Find all entities that should have TemporalAnchor label but don't
MATCH (n:Entity)
WHERE n.temporal_start_year IS NOT NULL
  AND n.temporal_end_year IS NOT NULL
  AND NOT n:TemporalAnchor
RETURN n.entity_cipher, n.label_en, n.temporal_scope
LIMIT 10;
```

---

## References

### Internal Documents
- **ENTITY_CIPHER_FOR_VERTEX_JUMPS.md** — Three-tier cipher model specification
- **CLAIM_ID_ARCHITECTURE.md** — Tier 3 claim cipher details
- **md/Architecture/perplexity-on-periods.md** — Period problem analysis
- **REQUIREMENTS.md** — REQ-FUNC-001 (Entity Import with MERGE pattern)

### Neo4j Documentation
- [Constraints Syntax (Neo4j 5.x)](https://neo4j.com/docs/cypher-manual/5/constraints/syntax/)
- [Indexes for Search Performance](https://neo4j.com/docs/cypher-manual/current/indexes/search-performance-indexes/)
- [Composite Indexes Performance](https://maxdemarzi.com/2020/02/19/composite-indexes-in-neo4j-4-0/)
- [Multi-Label Nodes Best Practices](https://neo4j.com/graphacademy/training-gdm-40/05-refactoring-model/)
- [Temporal Values](https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| **Feb 22, 2026** | **1.0** | **Initial DDL specification with ADR-002 TemporalAnchor pattern, complete constraints/indexes, MERGE interaction warning** |

---

**Document Status:** ✅ Canonical Reference (Feb 2026)  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026
