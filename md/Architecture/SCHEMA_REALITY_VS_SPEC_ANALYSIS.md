# Schema Reality vs Specification: Gap Analysis

**Date:** February 22, 2026  
**Status:** Architectural Analysis  
**Source:** Live Neo4j Aura database audit  
**Database:** neo4j+s://f7b612a3.databases.neo4j.io

---

## Executive Summary

**Audit Method:** Live database inspection comparing actual schema against:
- ENTITY_CIPHER_FOR_VERTEX_JUMPS.md
- NEO4J_SCHEMA_DDL_COMPLETE.md
- TIER_3_CLAIM_CIPHER_ADDENDUM.md

**Overall Assessment:** 🟡 **PARTIAL IMPLEMENTATION with SCHEMA DRIFT**

**Key Finding:** Database contains **legacy schema patterns** alongside new architecture. Migration is required, not greenfield deployment.

---

## Critical Findings

### 🔴 **CRITICAL: "CONCEPT" Entity Type Dominates (86% of entities)**

**Reality:**
```
CONCEPT: 258 entities (86.0%)
PLACE: 16 entities (5.3%)
SUBJECTCONCEPT: 12 entities (4.0%)
EVENT: 7 entities (2.3%)
PERSON: 6 entities (2.0%)
ORGANIZATION: 1 entity (0.3%)
```

**Specification (9 Canonical Types):**
```
PERSON, EVENT, PLACE, SUBJECTCONCEPT, WORK,
ORGANIZATION, PERIOD, MATERIAL, OBJECT
```

**Problem:**
- **"CONCEPT" is NOT in the canonical registry!**
- No entry in `ENTITY_TYPE_PREFIXES` for "CONCEPT"
- Uses deprecated cipher prefix `ent_con_*`
- Represents 258 entities that need reclassification

**Architectural Decision Needed:**

| Option | Approach | Impact |
|--------|----------|--------|
| **A: Migrate CONCEPT → Canonical Types** | Reclassify each entity to proper type (PERSON, ORGANIZATION, etc.) | HIGH effort, correct architecture |
| **B: Add CONCEPT to Registry (Deprecated)** | Add `"CONCEPT": "con"` to ENTITY_TYPE_PREFIXES as legacy type | LOW effort, perpetuates drift |
| **C: Hybrid (Recommended)** | Keep CONCEPT temporarily, migrate incrementally during entity scaling | MEDIUM effort, pragmatic |

**Recommendation:** **Option C** — Add CONCEPT as a transitional type with migration plan.

---

### 🟢 **POSITIVE: Tier 2 (FacetedEntity) Ahead of Expectations**

**Reality:**
- 360 FacetedEntity nodes exist
- Indexes in place: `faceted_cipher_idx`, `faceted_entity_facet_idx`
- Constraints functioning

**Specification:**
- Expected: 0 nodes (not yet implemented)
- Found: 360 nodes (20% more than Entity nodes!)

**Analysis:**
This suggests Tier 2 was already partially implemented in earlier work. Need to verify:
- Are these correctly formatted?
- Do they use canonical facet IDs?
- Are they linked to Entity nodes correctly?

**Action:** Audit FacetedEntity schema in detail (separate task).

---

### 🔴 **CRITICAL: TemporalAnchor Pattern (ADR-002) NOT Implemented**

**Reality:**
```
:TemporalAnchor labels: 0
temporal_start_year properties: 0
temporal_end_year properties: 0
is_temporal_anchor flags: 0
```

**Specification (ADR-002):**
- Entities with temporal bounds should have `:TemporalAnchor` label
- Must have `temporal_start_year`, `temporal_end_year`, `temporal_scope` properties
- Must use both label (Neo4j) and property flag (application)

**Impact:**
- Period discovery (REQ-FUNC-005) blocked
- Temporal queries not possible
- Q17167 (Roman Republic) missing temporal metadata

**Action Required:**
1. Execute DDL addendum (add TemporalAnchor constraints/indexes)
2. Query Wikidata for temporal bounds (P580/P582)
3. Add properties + labels to eligible entities

---

### 🔴 **CRITICAL: Tier 3 (Claims) NOT Implemented**

**Reality:**
```
:Claim nodes: 0
:FacetClaim nodes: 0
FacetClaim label: DOES NOT EXIST
```

**Specification:**
- FacetClaim nodes with cipher, subject_entity_cipher, facet_id, analysis_layer
- Qualifiers (P580, P582, P585, P276, P1545)
- InSituClaim vs RetrospectiveClaim discriminated unions

**Impact:**
- No claims in database yet (expected — SFA agents not deployed)
- FacetClaim label missing from schema
- Qualifier support not implemented

**Action Required:**
1. Execute DDL addendum (add FacetClaim support)
2. SFA deployment will create first claims

---

## Detailed Comparison

### Tier 1: Entity Cipher

| Aspect | Reality | Specification | Status |
|--------|---------|---------------|--------|
| **Entity nodes** | 300 | - | [OK] |
| **Constraints** | entity_cipher_unique, entity_qid_unique | Same | [OK] |
| **Indexes** | entity_type_idx exists | Same | [OK] |
| **Cipher format** | 50% old `ent_con_*`, 50% correct | 100% canonical | [DRIFT] |
| **Entity types** | CONCEPT (86%), others (14%) | 9 canonical types | [DRIFT] |

**Assessment:** ✅ Infrastructure in place, ⚠️ data needs migration

---

### Tier 2: Faceted Entity Cipher

| Aspect | Reality | Specification | Status |
|--------|---------|---------------|--------|
| **FacetedEntity nodes** | 360 | 0 expected | [AHEAD] |
| **Constraints** | faceted_cipher_unique exists | Same | [OK] |
| **Indexes** | faceted_entity_facet_idx exists | Same | [OK] |

**Assessment:** ✅ Ahead of spec — Tier 2 partially implemented

**Action Needed:** Verify FacetedEntity schema compliance (sample inspection).

---

### Tier 3: Claim Cipher

| Aspect | Reality | Specification | Status |
|--------|---------|---------------|--------|
| **FacetClaim label** | Does not exist | Required | [MISSING] |
| **Claim nodes** | 0 | - | [EXPECTED] |
| **Qualifier properties** | Not implemented | 5 required | [MISSING] |
| **Qualifier indexes** | 0 created | 7 required | [MISSING] |

**Assessment:** ❌ Not implemented — DDL addendum needed

---

### TemporalAnchor Pattern (ADR-002)

| Aspect | Reality | Specification | Status |
|--------|---------|---------------|--------|
| **:TemporalAnchor label** | 0 nodes | Required for temporal entities | [MISSING] |
| **temporal_start_year** | 0 nodes | Required for anchors | [MISSING] |
| **temporal_end_year** | 0 nodes | Required for anchors | [MISSING] |
| **temporal_scope** | 0 nodes | Required for anchors | [MISSING] |
| **Constraints** | 0 created | 3 required | [MISSING] |
| **Indexes** | 0 created | 3 required | [MISSING] |

**Assessment:** ❌ Not implemented — DDL addendum + data migration needed

---

## Schema Drift Analysis

### Issue 1: "CONCEPT" Entity Type (258 entities)

**What it is:**
- Legacy entity type from earlier implementation
- Represents entities that haven't been classified to canonical types
- Uses deprecated cipher prefix `ent_con_*`

**Examples of misclassified entities:**
```
ent_con_Q11514315 - "historical period" → Should be: ent_prd_Q11514315 (PERIOD)
ent_con_Q130614 - "Roman Senate" → Should be: ent_org_Q130614 (ORGANIZATION)
ent_con_Q337547 - "ancient Roman religion" → Should be: ??? (needs SCA classification)
ent_con_Q397 - "Latin" → Should be: ??? (language - no entity type for this)
```

**Root Cause:**
- Early SCA implementation used "CONCEPT" as catch-all
- Migration to 9 canonical types incomplete
- No CONCEPT entry in ENTITY_TYPE_PREFIXES registry

**Migration Strategy:**

**Phase 1: Add CONCEPT as Legacy Type (Temporary)**
```python
# Add to ENTITY_TYPE_PREFIXES in entity_cipher.py
ENTITY_TYPE_PREFIXES = {
    # ... existing 9 types ...
    "CONCEPT": "con",  # DEPRECATED - Legacy only, do not use for new entities
}
```

**Phase 2: Reclassify CONCEPT Entities (Gradual)**
```cypher
// Query CONCEPT entities with their P31 (instance of) values
MATCH (n:Entity {entity_type: "CONCEPT"})
OPTIONAL MATCH (n)-[:INSTANCE_OF]->(class)
RETURN n.qid, n.label, collect(class.qid) as instance_of, n.entity_cipher
LIMIT 10

// Reclassify based on P31:
// Q11514315 (historical period) → entity_type = "PERIOD"
// Q130614 (organization) → entity_type = "ORGANIZATION"
// etc.
```

**Phase 3: Update Ciphers**
```cypher
// After reclassification, update ciphers:
MATCH (n:Entity {entity_type: "PERIOD"})
WHERE n.entity_cipher STARTS WITH 'ent_con_'
SET n.entity_cipher = 'ent_prd_' + n.qid
```

---

### Issue 2: FacetedEntity Schema Unknown

**Discovery:**
- 360 FacetedEntity nodes exist (unexpected!)
- Need to verify schema compliance

**Required Verification:**
```cypher
// Check FacetedEntity schema
MATCH (f:FacetedEntity)
RETURN 
  f.faceted_cipher as cipher,
  f.entity_cipher as entity,
  f.facet_id as facet,
  f.subjectconcept_id as subject,
  keys(f) as all_properties
LIMIT 10
```

**Questions:**
1. Do faceted_ciphers use canonical format? (`fent_{facet_prefix}_{qid}_{subject}`)
2. Are facet_id values in the 18 canonical facets?
3. Are they linked to Entity nodes via HAS_FACETED_VIEW?

**Action:** Run detailed Tier 2 compliance audit.

---

## Migration Plan

### Phase 1: Execute DDL Addendum (SAFE, IMMEDIATE)

**What:** Add missing constraints and indexes  
**Risk:** LOW (IF NOT EXISTS prevents conflicts)  
**Time:** 15 minutes  
**Blocks:** Nothing (schema additions only)

**Expected Additions:**
- 3 TemporalAnchor constraints
- 3 TemporalAnchor indexes
- 7 Qualifier indexes
- Total: ~13 new schema items

**Execution:**
```bash
# Create and run DDL script
python scripts/execute_ddl_addendum.py

# Verify
# Before: 72 constraints, 65 indexes
# After:  75 constraints, 75 indexes
```

---

### Phase 2: Add CONCEPT to Registry (IMMEDIATE, LOW RISK)

**What:** Temporarily add CONCEPT as legacy entity type  
**Risk:** LOW (acknowledges existing data)  
**Time:** 5 minutes  

**Implementation:**
```python
# Update scripts/tools/entity_cipher.py
ENTITY_TYPE_PREFIXES = {
    "PERSON": "per",
    "EVENT": "evt",
    "PLACE": "plc",
    "SUBJECTCONCEPT": "sub",
    "WORK": "wrk",
    "ORGANIZATION": "org",
    "PERIOD": "prd",
    "MATERIAL": "mat",
    "OBJECT": "obj",
    "CONCEPT": "con",  # LEGACY - Deprecated, migrate to canonical types
}
```

**Rationale:**
- Makes current database valid according to spec
- Prevents errors when validating existing entities
- Marks as deprecated to prevent new usage
- Enables gradual migration

---

### Phase 3: Migrate CONCEPT Entities (DEFERRED, HIGH EFFORT)

**What:** Reclassify 258 CONCEPT entities to canonical types  
**Risk:** MEDIUM (data modification)  
**Time:** 8-12 hours (needs SCA reclassification)  
**Blocks:** Nothing immediate (can defer until entity scaling)

**Approach:**
1. Query Wikidata P31 (instance of) for each CONCEPT entity
2. Use SCA classification logic to determine canonical type
3. Update entity_type property
4. Regenerate entity_cipher with correct prefix
5. Update all FacetedEntity references

**Defer Until:** Entity scaling sprint (can batch with new entities)

---

### Phase 4: Implement TemporalAnchor Pattern (MEDIUM PRIORITY)

**What:** Add temporal properties to eligible entities  
**Risk:** MEDIUM (requires Wikidata queries)  
**Time:** 4-6 hours  
**Blocks:** Period discovery (REQ-FUNC-005)

**Implementation:**
1. Query Wikidata for P580/P582 (start/end time) for all entities
2. Normalize to `temporal_start_year`, `temporal_end_year`, `temporal_scope`
3. Add `temporal_calendar` metadata
4. Set `is_temporal_anchor = true`
5. Add `:TemporalAnchor` label

**Target Entities (Priority):**
- Q17167 (Roman Republic)
- Q2277 (Roman Empire)
- Q201038 (Roman Kingdom)
- Q2839628 (Early Roman Republic)
- Q6106068 (Middle Roman Republic)
- Q2815472 (Late Roman Republic)

---

## Recommendations for Dev Agent

### Priority 1: Execute DDL Addendum [IMMEDIATE, LOW RISK]

**File:** Create `scripts/execute_ddl_addendum.py` from DEV_AGENT_SCHEMA_EXECUTION_GUIDE.md

**What it does:**
- Adds 3 TemporalAnchor constraints
- Adds 3 TemporalAnchor indexes
- Adds 7 Qualifier indexes
- Uses `IF NOT EXISTS` (safe — skips existing)

**Expected Result:**
- Before: 72 constraints, 65 indexes
- After: 75 constraints, 75 indexes
- No errors (all uses IF NOT EXISTS)

**Verification:**
```bash
python check_schema.py
# Check: Total constraints = 75
# Check: Total indexes = 75
```

---

### Priority 2: Add CONCEPT to Entity Type Registry [IMMEDIATE, LOW RISK]

**File:** `scripts/tools/entity_cipher.py`

**Change:**
```python
ENTITY_TYPE_PREFIXES = {
    # Canonical types (use for new entities)
    "PERSON": "per",
    "EVENT": "evt",
    "PLACE": "plc",
    "SUBJECTCONCEPT": "sub",
    "WORK": "wrk",
    "ORGANIZATION": "org",
    "PERIOD": "prd",
    "MATERIAL": "mat",
    "OBJECT": "obj",
    
    # Legacy type (deprecated - do not use for new entities)
    "CONCEPT": "con",  # TODO: Migrate 258 CONCEPT entities to canonical types
}
```

**Rationale:**
- Makes existing database valid
- Prevents validation errors
- Documents migration need
- Enables gradual transition

---

### Priority 3: Verify FacetedEntity Schema [IMMEDIATE, LOW RISK]

**Surprising discovery:** 360 FacetedEntity nodes already exist!

**Need to verify:**
```python
#!/usr/bin/env python3
"""Verify FacetedEntity schema compliance"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    # Sample FacetedEntity schema
    result = session.run("""
        MATCH (f:FacetedEntity)
        RETURN 
          f.faceted_cipher as cipher,
          f.entity_cipher as entity,
          f.facet_id as facet,
          f.subjectconcept_id as subject,
          keys(f) as props
        LIMIT 10
    """)
    
    print("FacetedEntity Schema:")
    for r in result:
        print(f"  Cipher: {r['cipher']}")
        print(f"  Entity: {r['entity']}")
        print(f"  Facet: {r['facet']}")
        print(f"  Subject: {r['subject']}")
        print(f"  Props: {sorted(r['props'])}")
        print()
    
    # Check facet_id values
    result = session.run("""
        MATCH (f:FacetedEntity)
        RETURN DISTINCT f.facet_id as facet, count(*) as count
        ORDER BY count DESC
    """)
    
    print("Facet usage:")
    CANONICAL_FACETS = {
        "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
        "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
        "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
        "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
        "SOCIAL", "TECHNOLOGICAL"
    }
    
    for r in result:
        facet = r['facet']
        count = r['count']
        status = "[OK]" if facet in CANONICAL_FACETS else "[!]"
        print(f"  {status} {facet}: {count}")

driver.close()
```

**Save as:** `scripts/verify_faceted_entities.py`

---

### Priority 4: Implement TemporalAnchor Pattern [DEFERRED, MEDIUM RISK]

**What:** Add temporal properties to entities that should be temporal anchors

**Target Entities (from audit - entities likely to have P580/P582):**
```
Q17167 - Roman Republic (SUBJECTCONCEPT)
Q2277 - Roman Empire (SUBJECTCONCEPT)
Q201038 - Roman Kingdom (SUBJECTCONCEPT)
Q2839628 - Early Roman Republic (SUBJECTCONCEPT)
Q6106068 - Middle Roman Republic (SUBJECTCONCEPT)
Q2815472 - Late Roman Republic (SUBJECTCONCEPT)
```

**Implementation:**
```python
#!/usr/bin/env python3
"""Add TemporalAnchor pattern to eligible entities"""

from neo4j import GraphDatabase
import requests

# Wikidata SPARQL query for P580/P582
def get_temporal_bounds(qid):
    """Query Wikidata for start/end times"""
    query = f"""
    SELECT ?start ?end WHERE {{
      wd:{qid} p:P580/psv:P580/wikibase:timeValue ?start .
      wd:{qid} p:P582/psv:P582/wikibase:timeValue ?end .
    }}
    """
    # ... SPARQL execution
    return start_year, end_year

# Update Neo4j entities
driver = GraphDatabase.driver(...)

ELIGIBLE_ENTITIES = ['Q17167', 'Q2277', 'Q201038', 'Q2839628', 'Q6106068', 'Q2815472']

for qid in ELIGIBLE_ENTITIES:
    start_year, end_year = get_temporal_bounds(qid)
    
    if start_year and end_year:
        with driver.session() as session:
            session.run("""
                MATCH (n:Entity {qid: $qid})
                SET n.temporal_start_year = $start_year,
                    n.temporal_end_year = $end_year,
                    n.temporal_scope = $scope,
                    n.temporal_calendar = 'julian',
                    n.is_temporal_anchor = true,
                    n:TemporalAnchor
            """, qid=qid, start_year=start_year, end_year=end_year, 
                 scope=f"{start_year}/{end_year}")
```

---

## Architectural Guidance

### ADR-004: Legacy CONCEPT Type Handling

**Status:** Proposed (February 22, 2026)

**Context:**
Database contains 258 entities (86%) classified as "CONCEPT" — a type not in the canonical registry. This represents schema drift from earlier implementation.

**Options:**

**A. Immediate Migration (Purist)**
- Reclassify all 258 CONCEPT entities now
- Update ciphers to canonical prefixes
- Pros: Clean architecture immediately
- Cons: 8-12 hours effort, blocks other work

**B. Perpetuate Drift (Pragmatist)**
- Add CONCEPT permanently to registry
- Accept non-canonical type
- Pros: Zero effort
- Cons: Technical debt, unclear semantics

**C. Transitional Type (Recommended)**
- Add CONCEPT as DEPRECATED/LEGACY type
- Mark for migration
- Migrate incrementally during entity scaling
- Pros: Validates current data, enables gradual cleanup
- Cons: Temporary technical debt

**Decision:** **Option C — Transitional Type**

**Implementation:**
1. Add `"CONCEPT": "con"` to ENTITY_TYPE_PREFIXES with DEPRECATED comment
2. Update Pydantic models to accept CONCEPT but warn
3. During entity scaling sprint, reclassify CONCEPT entities as new entities are added
4. Target: 0 CONCEPT entities by end of entity scaling (10K entities)

**Success Criteria:**
- Current entities validate without errors
- New entities never use CONCEPT type
- CONCEPT count decreases over time
- All CONCEPT entities migrated before production

---

## Summary: Database vs Specification Gap Matrix

| Component | Spec | Reality | Gap | Priority | Effort | Risk |
|-----------|------|---------|-----|----------|--------|------|
| **Tier 1 constraints** | 4 | 2 exist | 2 missing | P1 | 5min | LOW |
| **Tier 1 indexes** | 2 | 1 exists | 1 missing | P1 | 5min | LOW |
| **Tier 2 constraints** | 6 | Some exist | Verify | P2 | 30min | LOW |
| **Tier 2 nodes** | 0 | 360 | Ahead! | P2 | N/A | N/A |
| **Tier 3 constraints** | 4 | 0 | 4 missing | P1 | 10min | LOW |
| **Tier 3 indexes** | 10 | 0 | 10 missing | P1 | 10min | LOW |
| **TemporalAnchor** | Pattern | 0 nodes | Full gap | P3 | 6h | MED |
| **CONCEPT type** | Not in spec | 258 entities | Drift | P2 | 10h | MED |
| **Qualifier support** | 5 props | 0 props | Full gap | P1 | 15min | LOW |

---

## Execution Checklist for Dev Agent

### Immediate (Next 2 Hours) ✅

- [ ] Execute DDL addendum script
  - Adds TemporalAnchor constraints/indexes
  - Adds Qualifier indexes
  - Uses IF NOT EXISTS (safe)
  
- [ ] Add CONCEPT to entity type registry
  - File: `scripts/tools/entity_cipher.py`
  - Mark as DEPRECATED
  
- [ ] Verify FacetedEntity schema
  - Run `scripts/verify_faceted_entities.py`
  - Check compliance with Tier 2 spec

### Short-Term (This Sprint)

- [ ] Implement Pydantic models
  - `scripts/models/entities.py`
  - `scripts/models/claims.py`
  - Accept CONCEPT as legacy type

### Medium-Term (Entity Scaling Sprint)

- [ ] Migrate CONCEPT entities
  - Reclassify to canonical types
  - Update ciphers
  - Target: 0 CONCEPT entities by 10K milestone
  
- [ ] Implement TemporalAnchor pattern
  - Query Wikidata for temporal bounds
  - Add properties + labels
  - Target: 6 SubjectConcept entities initially

---

## Files Created

| File | Purpose |
|------|---------|
| `audit_simple.py` | Schema audit script (reality check) |
| `output/SCHEMA_AUDIT_REPORT.txt` | Audit results (saved) |
| `md/Architecture/SCHEMA_REALITY_VS_SPEC_ANALYSIS.md` | This document |

---

## References

- **ENTITY_CIPHER_FOR_VERTEX_JUMPS.md** — Three-tier cipher specification
- **NEO4J_SCHEMA_DDL_COMPLETE.md** — Target schema (constraints/indexes)
- **TIER_3_CLAIM_CIPHER_ADDENDUM.md** — Qualifier support
- **output/SCHEMA_AUDIT_REPORT.txt** — Live database audit results

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| **Feb 22, 2026** | **1.0** | **Initial reality vs spec analysis, CONCEPT type drift identified, migration plan proposed** |

---

**Document Status:** ✅ Architectural Analysis Complete  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026  
**Next Action:** Awaiting stakeholder approval for ADR-004 (CONCEPT legacy type handling)
