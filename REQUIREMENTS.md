# Chrystallum Requirements Document

**Document Owner:** Requirements Analyst Agent  
**Created:** February 21, 2026  
**Status:** Living Document  
**Version:** 1.0

---

## Introduction

### Purpose
This document captures all business and technical requirements for the Chrystallum knowledge graph system. Requirements flow from business stakeholders through requirements analysis to development and QA agents.

### Scope
- Functional requirements (use cases, user stories)
- Non-functional requirements (performance, scalability, reliability)
- Data requirements (entities, attributes, relationships)
- Interface requirements (agent handoffs, APIs)
- Business rules and constraints

### Document Conventions

**Requirement ID Format:** `REQ-{Category}-{Number}`
- Categories: FUNC (functional), PERF (performance), DATA (data), INTF (interface), RULE (business rule)
- Example: `REQ-FUNC-001`, `REQ-PERF-015`

**Status Values:**
- `PROPOSED` - Initial requirement, awaiting approval
- `APPROVED` - Approved by stakeholder, ready for implementation
- `IN_PROGRESS` - Currently being implemented
- `COMPLETED` - Implementation complete, in QA
- `VERIFIED` - QA verified, deployed
- `DEFERRED` - Postponed to future release
- `REJECTED` - Not approved

**Priority Levels:**
- `CRITICAL` - System cannot function without this
- `HIGH` - Major feature or quality attribute
- `MEDIUM` - Important but not blocking
- `LOW` - Nice to have, future enhancement

---

## Requirements Workflow

```
Business Stakeholder
    ↓ (business requirement)
Requirements Analyst Agent (this role)
    ↓ (analyzes, documents, suggests solution)
Stakeholder Review
    ↓ (approves/rejects/modifies)
Requirements Analyst Agent
    ↓ (status: PROPOSED → APPROVED)
    ├─→ Dev Agent (implementation)
    └─→ QA Agent (test planning in parallel)
         ↓
    Dev Agent completes
         ↓ (status: APPROVED → COMPLETED)
    QA Agent verifies
         ↓ (status: COMPLETED → VERIFIED)
```

---

## Active Requirements

### Functional Requirements

#### REQ-FUNC-001: Idempotent Entity Import (Prevent Duplicates)

**Status:** VERIFIED ✅  
**Priority:** CRITICAL  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Completed:** 2026-02-21  
**Verified:** 2026-02-21  
**Submitted By:** Requirements Analyst Agent (from QA finding)  
**Approved By:** Stakeholder  
**Implemented By:** Dev Agent  
**Verified By:** QA Agent  

**Business Requirement:**
Entity import process must be idempotent - running the import multiple times with the same data should not create duplicate entity nodes. Currently, import creates duplicates when run twice (QA found 50 duplicate nodes from 20 QIDs).

**Business Value:**
- **Data Quality:** Eliminate duplicate entities in the graph
- **Reliability:** Ensure queries return accurate results
- **Performance:** Reduce storage overhead from redundant nodes
- **Operational Safety:** Allow re-running imports without data corruption

**Current State:**
- Import script uses `CREATE` statements
- No uniqueness constraints on `qid` or `entity_cipher`
- Running import twice creates duplicate nodes (QA Test: 350 nodes from 300 unique entities)

**Desired State:**
- Import script uses `MERGE` statements
- Uniqueness constraints enforce one node per `entity_cipher` and `qid`
- Running import multiple times produces identical result (300 nodes)
- Duplicate detection with automatic rollback

**Affected Components:**
- `scripts/neo4j/auto_import.py` - Import script
- `scripts/integration/prepare_neo4j_with_ciphers.py` - Import preparation
- Neo4j schema - Constraint definitions
- All `output/neo4j/import_*.cypher` files - Generated import scripts

**Use Case:**

```
UC-001: Import Entities Without Duplicates

Actor: Neo4j Import Script
Preconditions: 
  - Neo4j database accessible
  - Uniqueness constraints in place
  - Entity data prepared with ciphers

Main Success Scenario:
  1. Import script reads entity data (300 entities)
  2. For each entity:
     a. Script executes MERGE on entity_cipher
     b. If entity exists: Update properties
     c. If entity new: Create node with all properties
  3. Import completes successfully
  4. Verification query confirms 300 unique entities
  5. No duplicates exist (one node per entity_cipher, one per qid)

Postconditions:
  - Exactly 300 Entity nodes in database
  - All entity_cipher values unique
  - All qid values unique (for namespace = "wd")
  - Import can be re-run safely

Extensions:
  2a. Duplicate detected during import:
      - Transaction rolls back
      - Error logged with QID and entity_cipher
      - Import halts, returns error code
      
  4a. Verification finds duplicates:
      - List all duplicate QIDs
      - Raise validation error
      - Do not mark import as successful

Alternative Scenario (Re-Import):
  Given: 300 entities already imported
  When: Import runs again with same 300 entities
  Then: 
    - 300 entities remain (no new nodes created)
    - Properties updated if source data changed
    - Import completes successfully
```

**Business Rules:**

```
BR-IMP-01: Entity Cipher Uniqueness
  CONSTRAINT: ONE entity node per entity_cipher value
  VALIDATION: Neo4j unique constraint on Entity.entity_cipher
  SEVERITY: CRITICAL
  IMPLEMENTATION: CREATE CONSTRAINT entity_cipher_unique

BR-IMP-02: QID Uniqueness (Wikidata Entities)
  CONSTRAINT: ONE entity node per qid (where namespace = "wd")
  VALIDATION: Neo4j unique constraint on Entity.qid
  SEVERITY: CRITICAL  
  IMPLEMENTATION: CREATE CONSTRAINT entity_qid_unique

BR-IMP-03: Idempotent Import Operation
  CONSTRAINT: Import(data) = Import(Import(data))
  VALIDATION: Post-import duplicate check
  SEVERITY: CRITICAL
  IMPLEMENTATION: MERGE instead of CREATE

BR-IMP-04: Import Atomicity
  CONSTRAINT: Import succeeds completely or rolls back completely
  VALIDATION: Neo4j transaction
  SEVERITY: HIGH
  IMPLEMENTATION: Wrap import in BEGIN/COMMIT transaction
```

**Acceptance Criteria (BDD):**

```gherkin
Feature: Idempotent Entity Import
  As a system operator
  I want entity imports to be idempotent
  So that re-running imports doesn't create duplicates

  Background:
    Given Neo4j database is empty
    And uniqueness constraints are in place
    And entity data file contains 300 entities

  Scenario: First import creates all entities
    When I run the import script
    Then 300 Entity nodes are created
    And each entity has unique entity_cipher
    And each entity has unique qid
    And import status is SUCCESS

  Scenario: Re-running import is idempotent (no duplicates)
    Given 300 entities already imported
    When I run the import script again with same data
    Then still exactly 300 Entity nodes exist
    And no duplicate entity_cipher values exist
    And no duplicate qid values exist
    And import status is SUCCESS

  Scenario: Import updates existing entities
    Given entity Q1048 exists with label "Julius Caesar"
    When I import same entity with updated label "Gaius Julius Caesar"
    Then still exactly 1 entity node with qid "Q1048" exists
    And entity label is updated to "Gaius Julius Caesar"
    And import status is SUCCESS

  Scenario: Import detects pre-existing duplicates
    Given 2 entity nodes exist with qid "Q1048" (legacy duplicates)
    When I run import validation
    Then validation error is raised
    And error message contains "Duplicate QID: Q1048"
    And import does not proceed

  Scenario: Import rollback on duplicate creation attempt
    Given 300 entities imported
    And import script accidentally uses CREATE instead of MERGE
    When import runs
    Then Neo4j constraint violation occurs
    And transaction is rolled back
    And still exactly 300 entities exist (no partial import)
    And import status is FAILED

  Scenario: Verify uniqueness constraints exist
    When I query Neo4j constraints
    Then constraint "entity_cipher_unique" exists on Entity.entity_cipher
    And constraint "entity_qid_unique" exists on Entity.qid
```

**Implementation Guidance:**

```python
# BEFORE (Creates Duplicates):
cypher_create = f"""
CREATE (e:Entity {{
  entity_cipher: '{cipher}',
  qid: '{qid}',
  ...
}})
"""

# AFTER (Idempotent):
cypher_merge = f"""
MERGE (e:Entity {{entity_cipher: '{cipher}'}})
ON CREATE SET
  e.qid = '{qid}',
  e.created_at = datetime(),
  ...
ON MATCH SET
  e.updated_at = datetime(),
  e.label_en = '{label}',  // Update mutable properties
  ...
"""
```

**Constraints (One-time setup):**

```cypher
// Add these to schema initialization
CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
  FOR (e:Entity) REQUIRE e.entity_cipher IS UNIQUE;

CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS
  FOR (e:Entity) REQUIRE e.qid IS UNIQUE;
```

**Verification Query:**

```cypher
// Run after import to detect duplicates
MATCH (e:Entity)
WITH e.qid AS qid, count(*) AS node_count
WHERE node_count > 1
RETURN qid, node_count
ORDER BY node_count DESC;

// Expected result: 0 rows (no duplicates)
```

**Related Requirements:** REQ-FUNC-002 (Tier 1 Cipher Generation), REQ-FUNC-003 (Tier 2 Cipher Generation), REQ-DATA-001 (Entity Type Registry)

**Dependencies:**
- Neo4j 4.x+ (supports MERGE and constraints)
- Existing entity cipher implementation (Tier 1 ciphers)

**Estimated Effort:**
- Dev: 4 hours (update import scripts, add constraints, test)
- QA: 2 hours (run test suite, verify scenarios)

**Notes:**
- QA already created cleanup script (`cleanup_duplicates.cypher`) to remove existing 50 duplicates
- Run cleanup BEFORE adding constraints (constraints will fail if duplicates exist)
- Sequence: Cleanup → Add Constraints → Update Import Script → Re-test

---

#### REQ-FUNC-002: Tier 1 Entity Cipher Generation

**Status:** APPROVED  
**Priority:** CRITICAL  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §2  
**Submitted By:** Requirements Analyst Agent (architecture backfill)  
**Approved By:** Stakeholder (QA confirmed)

**Business Requirement:**
Every entity in Chrystallum must have a deterministic Tier 1 cipher that serves as the cross-subgraph join key, enabling O(1) lookup instead of expensive graph traversal.

**Business Value:**
- **Performance:** Direct index seeks instead of pattern matching traversal
- **Determinism:** Same entity always produces same cipher
- **Multilingual:** Language-neutral identifier (QID-based)
- **Scalability:** Enables efficient queries across millions of entities

**Formula:**
```python
entity_cipher = f"ent_{type_prefix}_{resolved_id}"
# Example: "ent_per_Q1048" (Julius Caesar)
```

**Components:**
- `ent_` - Fixed prefix (entity namespace)
- `type_prefix` - 3-char entity type code (see REQ-DATA-001)
- `resolved_id` - QID, BabelNet synset, or Chrystallum synthetic

**Business Rules:**
```
BR-EC1-01: Deterministic Generation
  Same (resolved_id, entity_type) MUST produce same entity_cipher
  Severity: CRITICAL

BR-EC1-02: Prefix Format
  type_prefix MUST be exactly 3 characters, lowercase
  Severity: CRITICAL

BR-EC1-03: Registry Constraint
  entity_type MUST be in ENTITY_TYPE_PREFIXES registry
  Severity: CRITICAL

BR-EC1-04: Index Requirement
  entity_cipher MUST be indexed for O(1) lookup
  Severity: HIGH
```

**Acceptance Criteria:**
```gherkin
Scenario: Generate Tier 1 cipher for Person
  Given entity type "PERSON" and QID "Q1048"
  When generate_entity_cipher() is called
  Then cipher equals "ent_per_Q1048"
  And cipher is deterministic (always same result)

Scenario: Reject invalid entity type
  Given entity type "INVALID" and QID "Q1048"
  When generate_entity_cipher() is called
  Then ValueError is raised
  And error message lists valid entity types
```

**Implementation:**
- Function: `generate_entity_cipher()` in `scripts/tools/entity_cipher.py`
- Already implemented (backfilling requirement)

**Related Requirements:** REQ-DATA-001 (Entity Type Registry), REQ-PERF-001 (O(1) Lookup)

---

#### REQ-FUNC-003: Tier 2 Faceted Entity Cipher Generation

**Status:** APPROVED  
**Priority:** CRITICAL  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §3  
**Submitted By:** Requirements Analyst Agent (architecture backfill)  
**Approved By:** Stakeholder (QA confirmed)

**Business Requirement:**
Every entity must have Tier 2 faceted ciphers (one per applicable facet) that enable direct cross-facet navigation without graph traversal.

**Business Value:**
- **Vertex Jumps:** Cross-facet navigation in O(1) time
- **Subgraph Addressing:** Direct access to entity in specific facet context
- **Agent Routing:** Enables facet-specific agent processing

**Formula:**
```python
faceted_cipher = f"fent_{facet_prefix}_{base_qid}_{subjectconcept_id}"
# Example: "fent_pol_Q1048_Q17167" (Caesar in POLITICAL facet, Roman Republic context)
```

**Components:**
- `fent_` - Fixed prefix (faceted entity namespace)
- `facet_prefix` - 3-char facet code (see REQ-DATA-002)
- `base_qid` - Entity QID from Tier 1 cipher
- `subjectconcept_id` - Anchoring SubjectConcept QID

**Business Rules:**
```
BR-EC2-01: All 18 Facets Generated
  MUST generate faceted_cipher for all 18 canonical facets
  Severity: HIGH

BR-EC2-02: Facet Registry Constraint
  facet_id MUST be in CANONICAL_FACETS (18 facets)
  Severity: CRITICAL

BR-EC2-03: Unique Combination
  Combination (entity_cipher, facet_id, subjectconcept_id) MUST be unique
  Severity: CRITICAL

BR-EC2-04: Materialized Hub Nodes
  FacetedEntity hub nodes MUST be created for active facets
  Severity: HIGH
```

**Acceptance Criteria:**
```gherkin
Scenario: Generate all 18 faceted ciphers
  Given entity cipher "ent_per_Q1048" and SubjectConcept "Q17167"
  When generate_all_faceted_ciphers() is called
  Then 18 faceted ciphers are returned
  And each facet has unique cipher
  And all facet IDs are in CANONICAL_FACETS

Scenario: Vertex jump computation (no DB query)
  Given entity cipher "ent_per_Q1048"
  When vertex_jump(from="MILITARY", to="POLITICAL", subject="Q17167")
  Then returns "fent_pol_Q1048_Q17167"
  And no database query executed (pure computation)
```

**Implementation:**
- Functions: `generate_faceted_cipher()`, `generate_all_faceted_ciphers()`, `vertex_jump()`
- File: `scripts/tools/entity_cipher.py`
- Already implemented (backfilling requirement)

**Related Requirements:** REQ-DATA-002 (Facet Registry), REQ-FUNC-002 (Tier 1 Cipher)

---

#### REQ-FUNC-004: Authority Cascade Entity Resolution

**Status:** APPROVED  
**Priority:** HIGH  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §5  
**Submitted By:** Requirements Analyst Agent (architecture backfill)  
**Approved By:** Stakeholder (QA confirmed)

**Business Requirement:**
System must resolve entities without Wikidata QIDs using a three-tier authority cascade: Wikidata QID → BabelNet synset → Chrystallum synthetic ID.

**Business Value:**
- **Coverage:** Support entities without QIDs (obscure historical figures)
- **Multilingual:** BabelNet provides 500+ language coverage
- **Determinism:** Synthetic IDs are deterministic (same name → same ID)
- **Reconciliation:** Synthetic IDs can be upgraded to QIDs later

**Authority Cascade (Priority Order):**
```
Priority 1: Wikidata QID (if available)
  └─> namespace: "wd", Example: Q1048

Priority 2: BabelNet Synset (API lookup)
  └─> namespace: "bn", Example: bn:14792761n

Priority 3: Chrystallum Synthetic (deterministic hash)
  └─> namespace: "crys", Example: crys:PERSON:a4f8c2d1
```

**Business Rules:**
```
BR-AC-01: Priority Order Enforcement
  MUST attempt QID first, then BabelNet, then synthetic
  Severity: HIGH

BR-AC-02: Deterministic Synthetic IDs
  Same (canonical_name, entity_type, temporal) MUST produce same synthetic ID
  Severity: CRITICAL

BR-AC-03: Namespace Tagging
  Entity MUST have namespace property: "wd" | "bn" | "crys"
  Severity: HIGH

BR-AC-04: Reconciliation Support
  Synthetic IDs can be reconciled to QIDs when discovered
  Severity: MEDIUM
```

**Acceptance Criteria:**
```gherkin
Scenario: Resolve entity with QID
  Given entity has QID "Q1048"
  When resolve_entity_id() is called
  Then resolved_id is "Q1048"
  And namespace is "wd"

Scenario: Fallback to BabelNet
  Given entity has no QID
  And BabelNet API returns synset "bn:14792761n"
  When resolve_entity_id() is called
  Then resolved_id is "bn:14792761n"
  And namespace is "bn"

Scenario: Fallback to synthetic ID
  Given entity has no QID
  And BabelNet API returns no results
  When resolve_entity_id("Lucius Merula", "PERSON", temporal="-87")
  Then resolved_id starts with "crys:PERSON:"
  And namespace is "crys"
  And result is deterministic (same inputs = same ID)
```

**Implementation:**
- Function: `resolve_entity_id()` in `scripts/tools/entity_cipher.py`
- Already implemented (backfilling requirement)

**Related Requirements:** REQ-FUNC-002 (Tier 1 Cipher)

---

#### REQ-FUNC-005: Temporal Anchor Pattern Implementation (REVISED)

**Status:** APPROVED  
**Priority:** CRITICAL  
**Submitted:** 2026-02-21  
**Revised:** 2026-02-21 (architectural refinement per perplexity-on-periods.md)  
**Approved:** 2026-02-21  
**Source:** md/Architecture/perplexity-on-periods.md  
**Submitted By:** Requirements Analyst Agent  
**Approved By:** Stakeholder  
**Assigned To:** Dev Agent, SCA Agent

**Business Requirement:**
Implement temporal anchor pattern: tag existing entities that define time periods with `is_temporal_anchor: true` and `temporal_scope` property, enabling faceted timeline queries without creating monolithic "Period" entity type.

**Business Value:**
- **Multi-dimensional Periodization:** Support overlapping periods across 18 facets (POLITICAL, CULTURAL, MILITARY timelines don't align)
- **Emergent Facet Salience:** Periods appear in facet swimlanes based on claim count (not manual assignment)
- **Zero Harvesting Cost:** Use existing 300+ entities (many already have temporal bounds)
- **Architectural Simplicity:** Multi-label pattern (Organization + TemporalAnchor) instead of separate Period nodes
- **Cross-Cultural Comparison:** Stack Egyptian, Greek, Roman timelines at same time point

**Architectural Principle:**
"Period" is overloaded - it's simultaneously temporal container, entity, SubjectConcept, geographic scope, and classification label. **Solution:** Separate these roles via multi-label pattern and property flags.

**Multi-Label Pattern:**
```cypher
// Roman Republic: Organization that ALSO defines a period
(:Entity:Organization:TemporalAnchor {
  entity_cipher: "ent_org_Q17167",
  entity_type: "ORGANIZATION",        // Primary classification
  is_temporal_anchor: true,           // Flag: defines time span
  temporal_scope: "-0509/-0027",      // ISO 8601 interval
  temporal_start: -509,               // Indexed integer for range queries
  temporal_end: -27,                  // Indexed integer for range queries
  qid: "Q17167"
})

// Hellenistic Period: Pure temporal designation
(:Entity:Period:TemporalAnchor {
  entity_cipher: "ent_prd_Q6813",
  entity_type: "PERIOD",              // Primary: IS a period
  is_temporal_anchor: true,
  temporal_scope: "-0323/-0031",
  temporal_start: -323,
  temporal_end: -31,
  qid: "Q6813"
})
```

**4-Phase Workflow:**

**Phase 1: Tag Existing Entities (1 hour)**
```
Action: Add temporal_anchor flag to entities with temporal bounds
Query: Find entities with (P580+P582) OR (P571+P576)
Process:
  - SET is_temporal_anchor = true
  - SET temporal_scope = "{P580}/{P582}"
  - SET temporal_start = year(P580)
  - SET temporal_end = year(P582)
Result: ~100-200 of existing 300 entities tagged
Cost: Zero (no API calls, property updates only)
```

**Phase 2: Harvest Pure Periods (2 hours)**
```
Action: SPARQL harvest for entities that are ONLY temporal designations
Criteria: P31 = Q11514315 AND NOT (organization, country, state, polity)
Examples: "Iron Age", "Archaic Greece", "Hellenistic period", "Stone Age"
Target: 100-200 pure period entities
Result: High-quality temporal designations (no institutional confusion)
```

**Phase 3: PeriodO Temporal Alignment (1 hour)**
```
Action: Match temporal_scope intervals to PeriodO entries
Method: Fuzzy match (±5 year tolerance on start/end dates)
Result: Add periodo_id as authority identifier (like pleiades_id)
Note: PeriodO aligns temporal definitions, not entity classification
```

**Phase 4: Hierarchical Nesting (1 hour)**
```
Action: Create BROADER_THAN edges for temporal containment
Logic: IF temporal_scope_A contains temporal_scope_B
       THEN (A)-[:BROADER_THAN]->(B)
Example: Byzantine Empire (330-1453) BROADER_THAN Iconoclasm (726-843)
Check: Cycle detection (no circular hierarchies)
```

**Business Rules:**
```
BR-TA-01: Temporal Bounds Required
  IF is_temporal_anchor = true THEN (temporal_start AND temporal_end) MUST exist
  Severity: CRITICAL

BR-TA-02: Multi-Label Support
  Entities CAN have multiple labels (e.g., :Organization:TemporalAnchor)
  Severity: CRITICAL

BR-TA-03: Facet Salience is Emergent
  Period appears in facet swimlane IF fe.claim_count > 0 for that facet
  NOT manually assigned
  Severity: HIGH

BR-TA-04: Temporal Scope Normalization
  Both P580/P582 AND P571/P576 MUST normalize to temporal_scope
  Severity: HIGH

BR-TA-05: PeriodO Authority Optional
  periodo_id is optional authority identifier (not all periods match)
  Severity: MEDIUM
```

**Acceptance Criteria:**
```gherkin
Scenario: Tag existing entity as temporal anchor
  Given entity Q17167 with P580=-509 and P582=-27
  When temporal anchor tagging runs
  Then is_temporal_anchor = true
  And temporal_scope = "-0509/-0027"
  And temporal_start = -509
  And temporal_end = -27
  And entity keeps existing classification (ORGANIZATION)

Scenario: Multi-label entity (organization + temporal anchor)
  Given entity Q17167 classified as ORGANIZATION
  When temporal anchor flag added
  Then entity has labels [:Entity:Organization:TemporalAnchor]
  And entity_type remains "ORGANIZATION"
  And is_temporal_anchor = true

Scenario: Faceted timeline query (stacked swimlanes)
  Given 5 entities with is_temporal_anchor = true
  And temporal range overlapping -200 BCE
  When faceted timeline query runs for POLITICAL and CULTURAL facets
  Then entities with POLITICAL claims appear in POLITICAL swimlane
  And entities with CULTURAL claims appear in CULTURAL swimlane
  And same entity can appear in multiple swimlanes
  And entities ordered by temporal_start

Scenario: Cross-geographic temporal comparison
  Given temporal anchors for Rome, Egypt, Greece
  When query for entities active in -200 BCE
  Then returns Roman Republic, Ptolemaic Egypt, Antigonid Macedonia
  And each shows geographic coverage
  And all exist simultaneously (parallel timelines)

Scenario: Emergent facet salience
  Given Hellenistic period with 198 CULTURAL claims and 145 ARTISTIC claims
  When timeline renders
  Then Hellenistic appears in both CULTURAL and ARTISTIC swimlanes
  And bar thickness/opacity reflects claim count (salience)
```

**Implementation:**

**Phase 1: Entity Property Updates**
```python
# Tag existing entities
MATCH (e:Entity)
WHERE (e.P580 IS NOT NULL AND e.P582 IS NOT NULL)
   OR (e.P571 IS NOT NULL AND e.P576 IS NOT NULL)
SET e.is_temporal_anchor = true,
    e.temporal_scope = CASE 
      WHEN e.P580 IS NOT NULL THEN e.P580 + "/" + e.P582
      ELSE e.P571 + "/" + e.P576
    END,
    e.temporal_start = year(coalesce(e.P580, e.P571)),
    e.temporal_end = year(coalesce(e.P582, e.P576))
```

**Phase 2: Pure Period Harvest**
```python
# SPARQL query for pure periods
SELECT ?item ?itemLabel ?start ?end WHERE {
  ?item wdt:P31 wd:Q11514315 .        # historical period
  ?item wdt:P580 ?start .
  ?item wdt:P582 ?end .
  FILTER NOT EXISTS {
    ?item wdt:P31 ?type .
    FILTER (?type IN (wd:Q43229, wd:Q6256, wd:Q3024240))  # organization, country, state
  }
}
LIMIT 200
```

**Phase 3 & 4:** PeriodO matching and hierarchy building

**Dependencies:**
- REQ-FUNC-002 (Entity cipher) - APPROVED
- REQ-DATA-001 (Entity types including PERIOD) - APPROVED

**Estimated Effort:** 5 hours (down from 12 hours)
- Phase 1: 1 hour (property updates)
- Phase 2: 2 hours (harvest 100-200 pure periods)
- Phase 3: 1 hour (PeriodO matching)
- Phase 4: 1 hour (hierarchy building)

**Related Requirements:** REQ-UI-001 (Faceted Timeline Visualization), REQ-FUNC-009 (Geographic Coverage Claims)

---

#### REQ-UI-001: Faceted Timeline Visualization (Swimlane View)

**Status:** APPROVED  
**Priority:** HIGH  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** md/Architecture/perplexity-on-periods.md (Multi-layered timeline section)  
**Submitted By:** Requirements Analyst Agent  
**Approved By:** Stakeholder  
**Assigned To:** Frontend Dev Agent

**Business Requirement:**
Provide faceted timeline visualization with swimlane views, where temporal anchors display as horizontal bars stacked by facet, enabling users to explore overlapping periodizations across political, cultural, military, and other dimensions.

**Business Value:**
- **Multi-dimensional Periodization:** Show that POLITICAL, CULTURAL, MILITARY timelines don't align perfectly
- **Emergent Salience:** Periods automatically appear in facet swimlanes based on claim count (not manual curation)
- **Cross-Cultural Comparison:** Stack Egyptian, Greek, Roman periods side-by-side at same time point
- **Historical Research:** Enables queries like "What was happening politically in Mediterranean in 200 BCE?"

**User Interface Concept:**
```
Facet Swimlanes (horizontal bars = temporal anchors):

POLITICAL  ╠══ Roman Kingdom ══╣╠════ Roman Republic ════════╣╠═ Empire ═
MILITARY                           ╠═ Punic Wars ═╣  ╠═ Marian ═══╣
CULTURAL      ╠═ Archaic ═══╣╠══ Classical ══╣╠═══ Hellenistic ════╣
RELIGIOUS  ╠═══════════ Polytheistic Roman ════════════════════════════
ARTISTIC      ╠═ Etruscan ══╣╠══ Greek Inf. ═╣╠═══ Hellenistic ════╣
           ───┼──────────────┼───────────────┼──────────────────┼─────
             -753          -509             -323              -27    
```

**User Interactions:**
1. **Toggle swimlanes** - Show/hide facets (e.g., POLITICAL + MILITARY only)
2. **Click bar** - Drill into all claims within that temporal anchor + facet
3. **Zoom into overlap** - Where Hellenistic (CULTURAL) and Late Republic (POLITICAL) overlap
4. **Filter by geography** - Show only temporal anchors with claims in eastern Mediterranean
5. **Compare cultures** - Stack Egyptian, Greek, Roman POLITICAL periods side-by-side

**Query Pattern:**
```cypher
// Faceted timeline for specific range and facets
WITH -500 AS range_start, -1 AS range_end
MATCH (e:Entity)
WHERE e.is_temporal_anchor = true
  AND e.temporal_start <= range_end
  AND e.temporal_end >= range_start

MATCH (e)-[:HAS_FACETED_VIEW]->(fe:FacetedEntity)
WHERE fe.facet_id IN ["POLITICAL", "CULTURAL", "MILITARY"]
  AND fe.claim_count > 0

OPTIONAL MATCH (e)-[:HAS_GEO_COVERAGE]->(place:Entity)

RETURN e.label_en AS period,
       e.temporal_start AS start_year,
       e.temporal_end AS end_year,
       fe.facet_id AS swimlane,
       fe.claim_count AS bar_weight,
       collect(DISTINCT place.label_en) AS geography
ORDER BY fe.facet_id, e.temporal_start
```

**Business Rules:**
```
BR-UI-01: Emergent Salience Display
  Period appears in facet swimlane IF fe.claim_count > 0
  Bar thickness/opacity SHOULD reflect claim_count (visual weight)
  Severity: HIGH

BR-UI-02: Temporal Overlap Rendering
  Overlapping periods MUST be stacked vertically within swimlane
  Severity: MEDIUM

BR-UI-03: Same Entity, Multiple Swimlanes
  Entity CAN appear in multiple facet swimlanes simultaneously
  Example: Hellenistic in CULTURAL + ARTISTIC
  Severity: HIGH

BR-UI-04: Live View Principle
  Timeline is LIVE view of graph (not curated exhibit)
  New claims → period automatically appears in new facet
  Severity: HIGH
```

**Acceptance Criteria:**
```gherkin
Scenario: Display faceted timeline
  Given 10 temporal anchors spanning -500 to -1 CE
  And entities have claims across POLITICAL, CULTURAL, MILITARY facets
  When user opens timeline view
  Then swimlanes displayed for each facet
  And temporal anchors render as horizontal bars
  And bars positioned by temporal_start and temporal_end

Scenario: Emergent facet salience
  Given Hellenistic period with 198 CULTURAL claims and 145 ARTISTIC claims
  When timeline renders
  Then Hellenistic bar appears in CULTURAL swimlane
  And Hellenistic bar appears in ARTISTIC swimlane
  And bar weight reflects claim count (thicker in CULTURAL)

Scenario: Cross-geographic comparison
  Given temporal anchors for Rome, Egypt, Greece active in -200 BCE
  When user queries "What was happening politically in -200 BCE?"
  Then POLITICAL swimlane shows Roman Republic, Ptolemaic Egypt, Antigonid Macedonia
  And all displayed in parallel (stacked view)
  And each shows geographic coverage

Scenario: Toggle swimlanes
  Given timeline with all 18 facet swimlanes
  When user toggles off all except POLITICAL and MILITARY
  Then only POLITICAL and MILITARY swimlanes display
  And temporal anchors without claims in those facets hidden

Scenario: Drill into temporal anchor
  Given user clicks Roman Republic bar in POLITICAL swimlane
  When drill-down triggers
  Then display all FacetClaims where facet_id="POLITICAL" and temporal_scope overlaps Roman Republic
```

**Technology:**
- Frontend: React + Cytoscape.js OR vis-timeline library
- Backend: Neo4j Cypher queries (temporal range + facet filtering)
- Data Model: Existing (is_temporal_anchor flag, FacetedEntity.claim_count)

**Dependencies:**
- REQ-FUNC-005 (Temporal Anchor Pattern) - Implementation of data model
- REQ-DATA-002 (18 facets) - APPROVED

**Estimated Effort:** 
- Backend queries: 4 hours
- Frontend timeline component: 16 hours
- Integration: 4 hours
- Total: 24 hours (3 days)

**Related Requirements:** REQ-FUNC-005 (Temporal Anchor Pattern), REQ-FUNC-009 (Geographic Coverage)

---

#### REQ-FUNC-009: Geographic Coverage Claims (Time-Stamped)

**Status:** APPROVED  
**Priority:** MEDIUM  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** md/Architecture/perplexity-on-periods.md (Role 4: Geographic Scope)  
**Submitted By:** Requirements Analyst Agent  
**Approved By:** Stakeholder  
**Assigned To:** SFA Dev (GEOGRAPHIC_SFA)

**Business Requirement:**
Geographic coverage of temporal anchors must be represented as time-stamped claims produced by GEOGRAPHIC_SFA, not static properties, because boundaries change over time.

**Business Value:**
- **Temporal Evolution:** Capture that Roman Republic in 300 BCE ≠ 100 BCE ≠ 50 BCE geographically
- **Facet-Specific Claims:** Geographic coverage is a type of claim (produced by GEOGRAPHIC_SFA)
- **Historical Accuracy:** Reflect that empires expand and contract
- **Cross-Geographic Queries:** "Which polities controlled North Africa in 200 BCE?"

**Data Pattern:**
```cypher
// Roman Republic's geographic coverage evolves
(rr:Entity {qid: "Q17167"})
  -[:HAS_GEO_COVERAGE {temporal_scope: "-0509/-0264"}]->(italy:Entity {qid: "Q38"})
  -[:HAS_GEO_COVERAGE {temporal_scope: "-0264/-0146"}]->(italy, sicily, sardinia)
  -[:HAS_GEO_COVERAGE {temporal_scope: "-0146/-0027"}]->(italy, iberia, gaul, north_africa)

// Query: "What did Roman Republic control in -200 BCE?"
MATCH (rr {qid: "Q17167"})-[r:HAS_GEO_COVERAGE]->(place)
WHERE r.temporal_start <= -200 AND r.temporal_end >= -200
RETURN place.label_en
// Result: Italy, Spain, North Africa, Greece (Mediterranean empire)
```

**Business Rules:**
```
BR-GEO-01: Time-Stamped Coverage
  HAS_GEO_COVERAGE edges MUST have temporal_scope qualifier
  Severity: HIGH

BR-GEO-02: Produced by GEOGRAPHIC_SFA
  Geographic coverage claims MUST be produced by GEOGRAPHIC_SFA (not manual)
  Severity: MEDIUM

BR-GEO-03: Overlapping Coverage Allowed
  Multiple temporal_scope ranges for same entity → place allowed
  (Territory gained and lost over time)
  Severity: MEDIUM
```

**Acceptance Criteria:**
```gherkin
Scenario: Geographic coverage evolves over time
  Given Roman Republic with 3 temporal_scope ranges
  When query for coverage in -300 BCE
  Then returns Italy only
  When query for coverage in -100 BCE
  Then returns Italy, Spain, North Africa, Greece

Scenario: Multiple polities control same place
  Given Sicily with HAS_GEO_COVERAGE from Carthage (-650/-241)
  And Sicily with HAS_GEO_COVERAGE from Rome (-241/-27)
  When query "Who controlled Sicily in -300 BCE?"
  Then returns Carthage only
  When query "Who controlled Sicily in -100 BCE?"
  Then returns Rome only
```

**Dependencies:** REQ-FUNC-005 (Temporal Anchor Pattern)

**Estimated Effort:** 8 hours (GEOGRAPHIC_SFA claim generation)

---

#### REQ-FUNC-010: Entity Relationship Import (from Wikidata)

**Status:** VERIFIED ✅
**Priority:** HIGH
**Verified:** 2026-02-21
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** QA Agent finding (300 entities isolated with 0 relationships)  
**Submitted By:** Requirements Analyst Agent (from QA recommendation)  
**Approved By:** Stakeholder  
**Assigned To:** Dev Agent, QA Agent

**Business Requirement:**
Import entity-to-entity relationships from Wikidata to connect 300 isolated Entity nodes, enabling graph queries and completing knowledge graph structure.

**Business Value:**
- **Graph Functionality:** Enable relationship queries and traversal
- **Discovery:** Find entities via connections
- **Completeness:** Transform isolated nodes into connected graph
- **Research Capability:** Support historical workflows

**Current State:**
- Entity nodes: 300 (with properties)
- Entity relationships: 0 (isolated)
- Backbone relationships: 13,212 (working)

**Desired State:**
- Entity relationships: 1,500-3,000
- Connectivity: 90%+ entities
- Graph queries: Functional

**Relationship Types:**
- Hierarchical: P31 (instance of), P279 (subclass), P361 (part of), P527 (has part)
- Temporal: STARTED_IN, ENDED_IN (to Year backbone)
- Geographic: LOCATED_IN (to Place backbone)
- Subject: CLASSIFIED_BY (to SubjectConcept)

**Business Rules:**
```
BR-REL-01: Both entities must exist (CRITICAL)
BR-REL-02: Idempotent import via MERGE (CRITICAL)
BR-REL-03: Store wikidata_pid on relationships (HIGH)
BR-REL-04: No duplicate relationships (CRITICAL)
BR-REL-05: Temporal tethering for temporal anchors (HIGH)
```

**Acceptance Criteria:**
```gherkin
Scenario: Import relationships
  When import runs
  Then 1,500-3,000 relationships created
  And 90%+ entities have at least 1 relationship

Scenario: Idempotent re-import
  Given relationships already imported
  When import runs again
  Then no duplicates created

Scenario: Handle missing entities
  Given relationship to non-existent entity
  Then relationship skipped
  And warning logged
```

**Dependencies:** REQ-FUNC-001 (VERIFIED), REQ-FUNC-002 (APPROVED)

**Estimated Effort:** 6-8 hours (Dev) + 3-4 hours (QA)

**Related Requirements:** REQ-FUNC-005 (Temporal tethering)

---

#### REQ-FUNC-006: Entity Scaling to 10,000

**Status:** PROPOSED  
**Priority:** HIGH  
**Submitted:** 2026-02-21  
**Source:** PM_COMPREHENSIVE_PLAN_2026-02-20.md (Phase 2)  
**Submitted By:** Requirements Analyst Agent (PM plan analysis)

**Business Requirement:**
Scale entity count from 300 to 10,000 across 5 historical domains (Roman, Greek, Egyptian, Medieval, Hellenistic).

**Business Value:**
- Critical mass for multi-domain analysis
- 98% of Phase 2 goal
- Enable cross-domain queries

**Target Distribution:**
- Roman: 2,500 entities (25%)
- Greek: 2,500 entities (25%)
- Egyptian: 2,000 entities (20%)
- Medieval: 2,000 entities (20%)
- Hellenistic: 1,000 entities (10%)

**Business Rules:**
```
BR-SCALE-01: Minimum federation_score >= 2
BR-SCALE-02: All entities must have ciphers
BR-SCALE-03: MERGE pattern (idempotent import)
BR-SCALE-04: CONCEPT Migration During Scaling
  During entity scaling, CONCEPT entities MUST be reclassified to canonical types
  Target: 0 CONCEPT entities by 10,000 entity milestone
  Severity: MEDIUM
  References: REQ-DATA-004
```

**Acceptance Criteria:**
```gherkin
Scenario: Scale to 10,000 entities across 5 domains
  Given 300 entities (Roman Republic)
  When entity scaling completes
  Then total entities >= 10,000
  And distribution matches targets (Roman 25%, Greek 25%, etc.)
  And all entities have entity_cipher and faceted_ciphers

Scenario: Migrate legacy CONCEPT entities during scaling
  Given 258 entities with entity_type="CONCEPT" at start
  When entity scaling from 300 to 10,000
  Then CONCEPT entities reclassified incrementally
  And CONCEPT count decreases per domain
  And 0 CONCEPT entities at 10,000 milestone
  And all migrated entities have correct cipher format (not ent_con_*)

Scenario: Maintain data quality at scale
  Given 10,000 entities imported
  When federation scoring runs
  Then average federation_score >= 2.0
  And no duplicate entity_cipher values
  And no duplicate QID values
```

**Estimated Effort:** 33 hours (7 hours × 5 domains)

**Dependencies:** 
- REQ-FUNC-001 (VERIFIED) - Idempotent import
- REQ-DATA-004 (APPROVED) - CONCEPT migration strategy

**Related Requirements:** REQ-FUNC-005 (Period Discovery - parallel), REQ-DATA-004 (CONCEPT Migration)

---

#### REQ-FUNC-007: SFA Prompt Library Completion

**Status:** PROPOSED  
**Priority:** MEDIUM  
**Submitted:** 2026-02-21  
**Source:** PM_COMPREHENSIVE_PLAN_2026-02-20.md (Workstream 4)  
**Submitted By:** Requirements Analyst Agent (PM plan analysis)

**Business Requirement:**
Complete SFA prompt library from 3/18 to 18/18, providing specialist prompts for all canonical facets.

**Business Value:**
- Enable claim extraction across all 18 facets
- Specialist domain expertise per facet
- Prerequisite for Claims Architecture

**Current State:**
- Complete: 3/18 (MILITARY, BIOGRAPHIC, COMMUNICATION)
- Missing: 15 prompts
- Coverage: 17%

**Workflow:**
1. Create template (1h)
2. Generate 15 prompts (8h)
3. Test existing 3 (2h)
4. Document (2h)

**Estimated Effort:** 13 hours (2 days)

**Dependencies:** REQ-DATA-002 (18 facets defined)

**Related Requirements:** REQ-FUNC-008 (Claims Architecture)

---

### Performance Requirements

#### REQ-PERF-001: O(1) Index Seek Performance

**Status:** APPROVED  
**Priority:** CRITICAL  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §1.1  
**Submitted By:** Requirements Analyst Agent (architecture backfill)  
**Approved By:** Stakeholder (QA confirmed)

**Business Requirement:**
All entity and faceted entity lookups must execute as direct index seeks (O(1) complexity) rather than graph traversal (O(n) complexity).

**Business Value:**
- **Performance:** Sub-50ms query response for single entity lookup
- **Scalability:** Performance independent of graph size (1K or 1M entities)
- **Predictability:** Consistent query times regardless of data volume

**Performance Targets:**
- Single entity lookup by entity_cipher: < 10ms
- Faceted entity lookup by faceted_cipher: < 10ms
- Vertex jump (facet-to-facet): < 20ms (2 index seeks)
- Cross-SubjectConcept navigation: < 20ms (2 index seeks)

**Business Rules:**
```
BR-PERF-01: Index Requirement
  ALL cipher fields MUST have Neo4j indexes
  Severity: CRITICAL

BR-PERF-02: No Pattern Matching
  Queries MUST use direct cipher lookup, NOT pattern matching
  Severity: HIGH

BR-PERF-03: Composite Indexes
  Multi-property queries MUST have composite indexes
  Severity: HIGH
```

**Acceptance Criteria:**
```gherkin
Scenario: Single entity lookup performance
  Given database with 10,000 entities
  When query entity by entity_cipher
  Then response time < 10ms
  And query plan shows index seek (not scan)

Scenario: Performance independent of scale
  Given database scales from 1K to 100K entities
  When query same entity_cipher
  Then response time remains < 10ms (no degradation)

Scenario: Vertex jump performance
  Given entity with 18 faceted views
  When vertex_jump from MILITARY to POLITICAL
  Then computation time < 1ms (pure Python)
  And Neo4j lookup time < 10ms (index seek)
  And total time < 20ms
```

**Implementation:**
- 12+ Neo4j indexes on cipher fields
- Already implemented (backfilling requirement)

**Related Requirements:** REQ-FUNC-002, REQ-FUNC-003

---

### Data Requirements

#### REQ-DATA-001: Entity Type Registry (Locked List)

**Status:** APPROVED  
**Priority:** CRITICAL  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §2.3  
**Submitted By:** Requirements Analyst Agent (architecture backfill)  
**Approved By:** Stakeholder (QA confirmed)

**Business Requirement:**
System must maintain a locked registry of 9 canonical entity types with 3-character prefixes for Tier 1 cipher generation.

**Scope Clarification:**
- **Included:** Domain entity types only (entities that can be subjects of claims)
- **Count:** 9 canonical types (PERSON through OBJECT)
- **Excluded:** Infrastructure types (Year, Decade, Century, Millennium - temporal backbone)
- **Excluded:** Support types (PlaceType, PeriodCandidate - structural helpers)
- **Excluded:** CONCEPT (DEPRECATED legacy type per REQ-DATA-004)

**Business Value:**
- **Consistency:** All domain entities use same type classification
- **Governance:** Changes require architecture approval (ADR)
- **Determinism:** Stable prefixes ensure cipher stability
- **Clarity:** Separates domain entities from infrastructure

**Entity Type Registry (9 Canonical Types):**
| Entity Type | Prefix | Example |
|-------------|--------|---------|
| PERSON | per | ent_per_Q1048 |
| EVENT | evt | ent_evt_Q25238182 |
| PLACE | plc | ent_plc_Q220 |
| SUBJECTCONCEPT | sub | ent_sub_Q17167 |
| WORK | wrk | ent_wrk_Q644312 |
| ORGANIZATION | org | ent_org_Q193236 |
| PERIOD | prd | ent_prd_Q17167 |
| MATERIAL | mat | ent_mat_Q753 |
| OBJECT | obj | ent_obj_Q34379 |

**Business Rules:**
```
BR-REG-01: Registry Lock
  Entity types are LOCKED - changes require ADR
  Severity: CRITICAL

BR-REG-02: Prefix Format
  Prefix MUST be exactly 3 characters, lowercase
  Severity: CRITICAL

BR-REG-03: No Duplicates
  Each entity type MUST have unique prefix
  Severity: CRITICAL

BR-REG-04: Addition Process
  New entity types require: ADR + Registry Update + DMN Update + Tests
  Severity: HIGH
```

**Acceptance Criteria:**
```gherkin
Scenario: Validate registry completeness
  When system loads ENTITY_TYPE_PREFIXES
  Then registry contains exactly 9 entity types
  And all prefixes are 3 characters
  And all prefixes are lowercase
  And no duplicate prefixes exist

Scenario: Reject invalid entity type
  When entity classified as type not in registry
  Then ValueError is raised
  And error lists valid entity types
```

**Implementation:**
- Registry: `ENTITY_TYPE_PREFIXES` in `scripts/tools/entity_cipher.py`
- Already implemented (backfilling requirement)

**Related Requirements:** REQ-FUNC-002 (Tier 1 Cipher)

---

#### REQ-DATA-002: Facet Registry (18 Canonical Facets)

**Status:** APPROVED  
**Priority:** CRITICAL  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §3.3  
**Submitted By:** Requirements Analyst Agent (architecture backfill)  
**Approved By:** Stakeholder (QA confirmed)

**Business Requirement:**
System must maintain a locked registry of 18 canonical facets with 3-character prefixes for Tier 2 cipher generation and agent routing.

**Business Value:**
- **Multi-dimensional Analysis:** 18 analytical perspectives on each entity
- **Agent Specialization:** Each facet has specialist agent
- **Consistent Coverage:** All entities evaluated across same facet dimensions

**Facet Registry (18 Facets):**
| Facet | Prefix | Example |
|-------|--------|---------|
| ARCHAEOLOGICAL | arc | fent_arc_Q1048_Q17167 |
| ARTISTIC | art | fent_art_Q1048_Q17167 |
| BIOGRAPHIC | bio | fent_bio_Q1048_Q17167 |
| COMMUNICATION | com | fent_com_Q1048_Q17167 |
| CULTURAL | cul | fent_cul_Q1048_Q17167 |
| DEMOGRAPHIC | dem | fent_dem_Q1048_Q17167 |
| DIPLOMATIC | dip | fent_dip_Q1048_Q17167 |
| ECONOMIC | eco | fent_eco_Q1048_Q17167 |
| ENVIRONMENTAL | env | fent_env_Q1048_Q17167 |
| GEOGRAPHIC | geo | fent_geo_Q1048_Q17167 |
| INTELLECTUAL | int | fent_int_Q1048_Q17167 |
| LINGUISTIC | lin | fent_lin_Q1048_Q17167 |
| MILITARY | mil | fent_mil_Q1048_Q17167 |
| POLITICAL | pol | fent_pol_Q1048_Q17167 |
| RELIGIOUS | rel | fent_rel_Q1048_Q17167 |
| SCIENTIFIC | sci | fent_sci_Q1048_Q17167 |
| SOCIAL | soc | fent_soc_Q1048_Q17167 |
| TECHNOLOGICAL | tec | fent_tec_Q1048_Q17167 |

**Business Rules:**
```
BR-FACET-01: Registry Lock
  Facets are LOCKED - 18 canonical facets, no additions
  Severity: CRITICAL

BR-FACET-02: Forbidden Facets
  NEVER use: TEMPORAL, CLASSIFICATION, PATRONAGE, GENEALOGICAL
  Severity: CRITICAL
  Rationale: Removed per architecture decision

BR-FACET-03: All 18 Generated
  Each entity MUST have faceted ciphers for all 18 facets
  Severity: HIGH

BR-FACET-04: Prefix Uniqueness
  Each facet MUST have unique 3-char lowercase prefix
  Severity: CRITICAL
```

**Acceptance Criteria:**
```gherkin
Scenario: Validate facet registry completeness
  When system loads CANONICAL_FACETS
  Then registry contains exactly 18 facets
  And all prefixes are 3 characters
  And all prefixes are lowercase
  And no duplicate prefixes exist

Scenario: Generate all 18 faceted ciphers
  Given entity cipher "ent_per_Q1048"
  When generate_all_faceted_ciphers() called
  Then 18 faceted ciphers returned
  And each facet ID is in CANONICAL_FACETS
  And all ciphers are unique

Scenario: Reject forbidden facets
  When facet "TEMPORAL" is used
  Then error raised
  And message explains facet is forbidden
```

**Implementation:**
- Registries: `FACET_PREFIXES`, `CANONICAL_FACETS` in `scripts/tools/entity_cipher.py`
- Already implemented (backfilling requirement)

**Related Requirements:** REQ-FUNC-003 (Tier 2 Cipher)

---

#### REQ-DATA-003: Cipher-Eligible Qualifiers Registry

**Status:** APPROVED  
**Priority:** HIGH  
**Submitted:** 2026-02-21  
**Approved:** 2026-02-21  
**Source:** ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §4.2  
**Submitted By:** Requirements Analyst Agent (architecture backfill)  
**Approved By:** Stakeholder (QA confirmed)

**Business Requirement:**
System must maintain a locked registry of 5 cipher-eligible Wikidata qualifier PIDs that define assertion identity (included in Tier 3 claim cipher hash).

**Business Value:**
- **Identity Distinction:** Distinguishes 1st vs 2nd consulship, same battle at different locations
- **Cipher Stability:** Only identity-defining qualifiers in hash (metadata excluded)
- **Determinism:** Same assertion → same cipher

**Cipher-Eligible Qualifiers (5 PIDs):**
| PID | Label | W5H1 | Why Eligible |
|-----|-------|------|--------------|
| P580 | start time | WHEN | Distinguishes repeated relationships |
| P582 | end time | WHEN | Temporal bounds |
| P585 | point in time | WHEN | Specific date |
| P276 | location | WHERE | Spatial identity |
| P1545 | series ordinal | WHICH | Instance identity (1st, 2nd, 3rd) |

**Excluded Qualifiers (Metadata):**
| PID | Label | Why Excluded |
|-----|-------|-------------|
| P1480 | sourcing circumstances | Provenance metadata |
| P459 | determination method | How we know |
| P3831 | object has role | Contextual role |
| P1810 | subject named as | Language-dependent |
| P2241 | reason for deprecated rank | Wikidata lifecycle |
| P1932 | object stated as | Language-dependent |

**Business Rules:**
```
BR-QUAL-01: Only Eligible in Cipher
  Tier 3 claim cipher MUST include only qualifiers in CIPHER_ELIGIBLE_QUALIFIERS
  Severity: CRITICAL

BR-QUAL-02: Metadata Stored Separately
  Non-eligible qualifiers MUST be stored as mutable properties (not in cipher)
  Severity: HIGH

BR-QUAL-03: Normalized Values
  Qualifier values MUST be normalized before hashing
  Severity: CRITICAL
  Examples: P580=-59 → "+00-59", P1545=1 → "001"

BR-QUAL-04: Deterministic Ordering
  Qualifiers MUST be sorted by PID before hashing
  Severity: CRITICAL
```

**Acceptance Criteria:**
```gherkin
Scenario: Include eligible qualifiers in cipher
  Given claim with qualifiers P580=-59, P582=-58, P1545=1
  When build_claim_cipher() is called
  Then cipher includes all 3 qualifiers
  And qualifiers are normalized
  And qualifiers are sorted by PID

Scenario: Exclude metadata qualifiers from cipher
  Given claim with qualifiers P580=-59, P1480="inferred"
  When build_claim_cipher() is called
  Then cipher includes only P580
  And P1480 stored as separate property

Scenario: Distinguish consulships by qualifiers
  Given Caesar's 1st consulship (P580=-59, P1545=1)
  And Caesar's 2nd consulship (P580=-48, P1545=2)
  When build_claim_cipher() for each
  Then two different ciphers produced
```

**Implementation:**
- Registry: `CIPHER_ELIGIBLE_QUALIFIERS` in `scripts/tools/entity_cipher.py`
- Function: `build_claim_cipher_with_qualifiers()`
- Already implemented (backfilling requirement)

**Related Requirements:** REQ-FUNC-003 (Tier 2 Cipher), CLAIM_ID_ARCHITECTURE.md (Tier 3)

---

#### REQ-DATA-004: Legacy CONCEPT Type Migration

**Status:** APPROVED  
**Priority:** HIGH  
**Submitted:** 2026-02-22  
**Approved:** 2026-02-22  
**Source:** Graph Architect schema audit finding  
**Submitted By:** Requirements Analyst Agent  
**Approved By:** Stakeholder  
**Assigned To:** Dev Agent, SCA Agent

**Business Requirement:**
Add "CONCEPT" to entity type registry as DEPRECATED type, then migrate 258 CONCEPT entities (86% of database) to canonical types.

**Business Value:**
- **Data Quality:** Proper semantic classification
- **Cipher Integrity:** Correct prefixes (not deprecated con_)
- **Compliance:** Match canonical 9-type registry

**Current State:**
- CONCEPT entities: 258 (86%) - NOT in canonical registry
- Using deprecated cipher: `ent_con_*`
- Issue: Violates REQ-DATA-001 specification

**3-Phase Migration:**

**Phase 1: Registry Update (5 min)**
```python
# Add CONCEPT as DEPRECATED in entity_cipher.py
"CONCEPT": "con",  # DEPRECATED - migrate to canonical
```

**Phase 2: Reclassify (10 hours during entity scaling)**
- Expand P31 decision table (8 → 20+ rules)
- Batch reclassify 258 entities
- Update entity_type + regenerate ciphers
- Create SAME_AS edges (preserve references)

**Phase 3: Remove CONCEPT (when count = 0)**
- Delete from registry
- Final verification

**Business Rules:**
```
BR-CONCEPT-01: CONCEPT is Deprecated (HIGH)
BR-CONCEPT-02: Migration target 0 by 10K milestone (MEDIUM)
BR-CONCEPT-03: No new CONCEPT entities (HIGH)
BR-CONCEPT-04: Cipher migration with SAME_AS edges (HIGH)
```

**Examples:**
```
ent_con_Q11514315 → ent_prd_Q11514315 (PERIOD)
ent_con_Q130614 → ent_org_Q130614 (ORGANIZATION)
```

**Dependencies:** REQ-DATA-001 (Entity Type Registry)

**Estimated Effort:** 15 hours (5min + 2h + 10h + 3h)

**Related Requirements:** REQ-DATA-001, REQ-FUNC-002

---

#### REQ-DATA-005: Meta-Model Entity Type Name Alignment

**Status:** APPROVED  
**Priority:** MEDIUM  
**Submitted:** 2026-02-22  
**Approved:** 2026-02-22  
**Source:** Graph Architect meta-model discovery  
**Submitted By:** Requirements Analyst Agent  
**Approved By:** Stakeholder  
**Assigned To:** Dev Agent

**Business Requirement:**
Align EntityType node names in self-describing meta-model from legacy to canonical names for consistency.

**Name Mapping:**
- "Human" → "PERSON" (rename)
- "Organization", "Period", "Event", "Place", "Work" → No change ✅
- Add: "MATERIAL", "OBJECT" if missing

**Implementation:**
```cypher
MATCH (et:EntityType {name: "Human"})
SET et.name = "PERSON", et.cipher_prefix = "per"

MERGE (mt:EntityType {name: "MATERIAL"})
SET mt.cipher_prefix = "mat"

MERGE (ot:EntityType {name: "OBJECT"})
SET ot.cipher_prefix = "obj"
```

**Business Rules:**
- BR-META-01: Names must match ENTITY_TYPE_PREFIXES (MEDIUM)
- BR-META-02: All 9 types must exist (MEDIUM)

**Effort:** 30 minutes

**Dependencies:** REQ-DATA-001

---

See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for complete data model documentation.

---

### Interface Requirements

**None yet** - This section will be populated as business requirements are received.

---

### Business Rules

**None yet** - This section will be populated as business requirements are received.

---

## Requirements Traceability Matrix

| Req ID | Requirement | Status | Priority | Architecture Doc | Implementation | Tests | Assigned To | Notes |
|--------|-------------|--------|----------|------------------|----------------|-------|-------------|-------|
| REQ-FUNC-001 | Idempotent Entity Import | VERIFIED ✅ | CRITICAL | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §2.1 | scripts/integration/prepare_neo4j_with_ciphers.py<br>fix_duplicates.py | qa_test_suite.py (10/10 PASS)<br>verify_dev_fixes.py (5/5 PASS) | Dev Agent<br>QA Agent | Verified 2026-02-21<br>All acceptance criteria met |
| REQ-FUNC-002 | Tier 1 Entity Cipher Generation | APPROVED ✅ | CRITICAL | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §2 | scripts/tools/entity_cipher.py | (existing impl) | - | Approved 2026-02-21<br>Backfilled from architecture |
| REQ-FUNC-003 | Tier 2 Faceted Cipher Generation | APPROVED ✅ | CRITICAL | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §3 | scripts/tools/entity_cipher.py | (existing impl) | - | Approved 2026-02-21<br>Backfilled from architecture |
| REQ-FUNC-004 | Authority Cascade Resolution | APPROVED ✅ | HIGH | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §5 | scripts/tools/entity_cipher.py | (existing impl) | - | Approved 2026-02-21<br>Backfilled from architecture |
| REQ-PERF-001 | O(1) Index Seek Performance | APPROVED ✅ | CRITICAL | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §1.1 | Neo4j indexes (12+) | (existing impl) | - | Approved 2026-02-21<br>Backfilled from architecture |
| REQ-DATA-001 | Entity Type Registry (9 types) | APPROVED ✅ | CRITICAL | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §2.3 | ENTITY_TYPE_PREFIXES | (existing impl) | - | Approved 2026-02-21<br>Backfilled from architecture |
| REQ-DATA-002 | Facet Registry (18 facets) | APPROVED ✅ | CRITICAL | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §3.3 | CANONICAL_FACETS | (existing impl) | - | Approved 2026-02-21<br>Backfilled from architecture |
| REQ-DATA-003 | Cipher-Eligible Qualifiers (5 PIDs) | APPROVED ✅ | HIGH | ENTITY_CIPHER_FOR_VERTEX_JUMPS.md §4.2 | CIPHER_ELIGIBLE_QUALIFIERS | (existing impl) | - | Approved 2026-02-21<br>Backfilled from architecture |
| REQ-DATA-004 | Legacy CONCEPT Type Migration | APPROVED ✅ | HIGH | Graph Arch schema audit | entity_cipher.py<br>reclassify_concepts.py | (15h) | Dev Agent<br>SCA Agent | Approved 2026-02-22<br>258 entities (86%) |
| REQ-DATA-005 | Meta-Model Name Alignment | APPROVED ✅ | MEDIUM | Meta-model discovery | EntityType nodes update | (30min) | Dev Agent | Approved 2026-02-22<br>Human→PERSON |
| REQ-FUNC-005 | Temporal Anchor Pattern (REVISED) | APPROVED ✅ | CRITICAL | perplexity-on-periods.md | Entity property updates<br>Pure period harvest | (4 phases, 5h) | Dev Agent<br>SCA Agent | Approved 2026-02-21<br>Multi-label pattern |
| REQ-UI-001 | Faceted Timeline Visualization | APPROVED ✅ | HIGH | perplexity-on-periods.md | React + vis-timeline | (24h) | Frontend Dev | Approved 2026-02-21<br>Swimlane + emergent |
| REQ-FUNC-009 | Geographic Coverage Claims | APPROVED ✅ | MEDIUM | perplexity-on-periods.md | GEOGRAPHIC_SFA | (8h) | SFA Dev | Approved 2026-02-21<br>Time-stamped |
| REQ-FUNC-010 | Entity Relationship Import | VERIFIED ✅ | HIGH | QA Agent finding | Relationship import script | verify_req_func_010.py (6/6 PASS) | Dev Agent<br>QA Agent | Verified 2026-02-21<br>1,568 rels, 81.7% connected |
| REQ-FUNC-006 | Entity Scaling to 10,000 | PROPOSED | HIGH | PM_COMPREHENSIVE_PLAN §Phase2 | SCA traversal + import | (to be created) | (awaiting approval) | From PM plan<br>5 domains |
| REQ-FUNC-007 | SFA Prompt Library (18/18) | PROPOSED | MEDIUM | PM_COMPREHENSIVE_PLAN §Workstream4 | md/Agents/SFA/ | (to be created) | (awaiting approval) | From PM plan<br>15 missing prompts |

---

## Deferred Requirements

**None yet**

---

## Rejected Requirements

**None yet**

---

## Change History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-02-21 | 1.0 | Initial document creation | Requirements Analyst Agent |

---

## Notes for Users

### How to Submit a Business Requirement

Provide me with:
1. **What you want to achieve** (business goal)
2. **Why it's needed** (business value)
3. **Any constraints** (must work with X, must be done by Y)

I will:
1. Analyze the requirement
2. Suggest a solution approach (use cases, process, rules, data)
3. Document it with full specifications
4. Create requirement with status `PROPOSED`
5. Wait for your approval
6. Update status to `APPROVED` when you confirm
7. Coordinate with Dev and QA agents

### Integration with Other Documents

- **DATA_DICTIONARY.md** - Detailed data model (referenced by DATA requirements)
- **PROCESS_MODELS.md** - BPMN workflows (referenced by FUNC requirements)
- **DECISION_MODELS.md** - DMN decision tables (referenced by RULE requirements)
- **AI_CONTEXT.md** - Updated whenever requirements change status
- **Key Files/** - Architecture documents (requirements trace back to these)

---

**Document maintained by:** Requirements Analyst Agent  
**Last updated:** February 21, 2026

