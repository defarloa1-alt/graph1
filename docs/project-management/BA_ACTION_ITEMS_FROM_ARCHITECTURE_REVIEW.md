# Requirements Analyst Action Items from Architecture Review

**Date:** February 22, 2026  
**From:** Graph Architect  
**To:** Requirements Analyst (BA)  
**Purpose:** Translate architectural findings into actionable requirements work

---

## Executive Summary

Graph Architect's schema audit and meta-model exploration revealed **3 areas requiring requirements work**:

1. ✅ **ADR-004 Approved** — CONCEPT type migration (needs requirement?)
2. ⚠️ **Entity Type Naming Mismatch** — Meta-model vs Cipher spec alignment
3. ⚠️ **Missing Entity Types** — MATERIAL, OBJECT not in meta-model registry

**BA Action Required:** Review findings below and determine if new requirements needed.

---

## Finding 1: ADR-004 (CONCEPT Type Migration) — Approved

### What Graph Architect Found

**Issue:** 258 entities (86%) use `entity_type="CONCEPT"` — not in canonical registry

**Examples:**
```
ent_con_Q11514315 (historical period) → Should be: ent_prd_Q11514315 (PERIOD)
ent_con_Q130614 (Roman Senate) → Should be: ent_org_Q130614 (ORGANIZATION)
```

**Architectural Decision (ADR-004):**
- Add CONCEPT as DEPRECATED/LEGACY type (immediate)
- Migrate to canonical types during entity scaling (incremental)
- Target: 0 CONCEPT entities by 10K milestone

### BA Action: Review if New Requirement Needed

**Question:** Does this need a formal requirement?

**Option A: Create New Requirement**
```markdown
REQ-DATA-004: Legacy CONCEPT Type Migration

Business Requirement:
Migrate 258 entities from deprecated CONCEPT type to canonical entity types.

Business Value:
- Schema compliance (9 canonical types only)
- Cipher format consistency (no deprecated ent_con_* prefixes)
- Clean architecture by 10K entity milestone

Business Rules:
BR-CONCEPT-01: No new entities with CONCEPT type
  Severity: CRITICAL
  All new entities MUST use canonical types

BR-CONCEPT-02: Incremental migration
  Severity: MEDIUM
  Migrate during entity scaling (100 entities per sprint)

BR-CONCEPT-03: Zero CONCEPT by production
  Severity: HIGH
  Before production launch: 0 CONCEPT entities

Acceptance Criteria:
- CONCEPT count decreases over time
- New entities never use CONCEPT
- 0 CONCEPT entities by 10K milestone
- All migrated entities have correct cipher format

Priority: MEDIUM (non-blocking, defer to entity scaling)
Effort: 10 hours (distributed across scaling sprints)
```

**Option B: Update Existing Requirement**
- Update REQ-FUNC-006 (Entity Scaling) to include CONCEPT migration
- Add acceptance criterion: "Reclassify CONCEPT entities as part of scaling"

**Option C: No Requirement Needed**
- ADR-004 is architectural guidance only
- Dev implements as part of registry update (5 min immediate, migration deferred)

**BA Decision Required:** Which option? (Recommend: **Option B** — fold into entity scaling)

---

## Finding 2: Entity Type Naming Mismatch — Meta-Model vs Cipher Spec

### What Graph Architect Found

**Meta-Model (In Database):**
```
14 EntityType nodes:
  Human, Organization, Period, Event, Place, Work, SubjectConcept, Claim
  Year, Decade, Century, Millennium, PlaceType, PeriodCandidate
```

**Cipher Spec (ENTITY_CIPHER_FOR_VERTEX_JUMPS.md):**
```
9 Canonical entity types:
  PERSON, ORGANIZATION, PERIOD, EVENT, PLACE, WORK,
  SUBJECTCONCEPT, MATERIAL, OBJECT
```

**Mismatches:**

| Meta-Model | Cipher Spec | Issue |
|------------|-------------|-------|
| Human | PERSON | Different name |
| Organization | ORGANIZATION | Capitalization |
| Period | PERIOD | Capitalization |
| SubjectConcept | SUBJECTCONCEPT | Capitalization |
| (missing) | MATERIAL | Not in meta-model |
| (missing) | OBJECT | Not in meta-model |
| Year, Decade, Century, Millennium | (not in spec) | Temporal backbone types |
| PlaceType, PeriodCandidate | (not in spec) | Support types |

### BA Action: Determine Canonical Source of Truth

**Question:** Which is correct — meta-model or cipher spec?

**Analysis:**

**Evidence for Cipher Spec (ENTITY_CIPHER_FOR_VERTEX_JUMPS.md):**
- ✅ Formalized in architectural document
- ✅ Has ADR-001 (accepted Feb 21, 2026)
- ✅ Used by entity import scripts
- ✅ Matches Pydantic models

**Evidence for Meta-Model (Database):**
- ✅ Already implemented (14 EntityType nodes exist)
- ✅ Used by Schema validation nodes
- ✅ Predates cipher spec (created Feb 20)

**Recommendation:** **Cipher spec is canonical** (more recent, formalized in ADR)

**BA Action Required:**

**Option A: Create Alignment Requirement**
```markdown
REQ-DATA-005: Meta-Model Entity Type Alignment

Business Requirement:
Align EntityType meta-model nodes with canonical cipher specification.

Changes Needed:
1. Rename: Human → PERSON
2. Rename: Organization → ORGANIZATION  
3. Rename: Period → PERIOD
4. Rename: SubjectConcept → SUBJECTCONCEPT
5. Add: MATERIAL entity type
6. Add: OBJECT entity type
7. Keep: Year, Decade, Century, Millennium (temporal backbone - not in cipher spec)
8. Keep: PlaceType, PeriodCandidate (support types - not in cipher spec)

Business Value:
- Single source of truth (meta-model matches spec)
- No confusion between Human/PERSON
- Complete registry (all 9 canonical types)

Acceptance Criteria:
- EntityType nodes use canonical names (PERSON, not Human)
- MATERIAL and OBJECT types added to registry
- All 9 canonical types present in meta-model

Priority: LOW (doesn't block work, cleanup task)
Effort: 1 hour
```

**Option B: Update Cipher Spec**
- Accept meta-model names as canonical
- Update ENTITY_CIPHER_FOR_VERTEX_JUMPS.md to use "Human" instead of "PERSON"

**BA Decision Required:** Align meta-model to spec, or spec to meta-model?

**Graph Architect Recommendation:** **Option A** — Update meta-model (cipher spec is canonical, more recent).

---

## Finding 3: Temporal Backbone Types (Year, Decade, Century, Millennium)

### What Graph Architect Found

**Meta-Model includes 4 temporal types:**
```
Year: "Atomic temporal nodes"
Decade: "Decade rollup"
Century: "Century rollup"
Millennium: "Millennium rollup"
```

**Cipher Spec:** These types are **not included** in the 9 canonical types

**Analysis:**
- These are **infrastructure types** (temporal backbone)
- Not "entities" in the research sense (not subjects of claims)
- Used for temporal indexing and period nesting

**Question:** Should these be in the entity type registry?

**BA Decision Required:**

**Option A: Keep Separate**
- Temporal backbone types are infrastructure, not entities
- Don't add to ENTITY_TYPE_PREFIXES
- No cipher generation for Year/Decade/Century/Millennium

**Option B: Add to Registry**
```python
ENTITY_TYPE_PREFIXES = {
    # ... existing 9 types ...
    "YEAR": "yr",      # Temporal backbone
    "DECADE": "dec",
    "CENTURY": "cen",
    "MILLENNIUM": "mil"
}
```

**Graph Architect Recommendation:** **Option A** — Keep separate (infrastructure, not domain entities).

---

## Finding 4: Schema Nodes Define Federation Dependencies

### What Graph Architect Found

**Schema nodes specify which federations each entity type uses:**

```cypher
Place Schema:
  uses_federations: ["Pleiades", "Wikidata", "GeoNames"]

Period Schema:
  uses_federations: ["PeriodO", "Wikidata"]

SubjectConcept Schema:
  uses_federations: ["LCSH", "FAST", "LCC", "Wikidata"]
```

**This is architectural governance at the schema level!**

### BA Action: Document This Pattern in Requirements?

**Question:** Should federation dependencies be formalized in requirements?

**Option A: Create Requirement**
```markdown
REQ-DATA-006: Federation Dependency Schema

Business Requirement:
Each entity type MUST declare which federations it depends on via Schema nodes.

Business Rules:
BR-FED-01: Required Federations
  Each entity type MUST specify required federations in Schema.uses_federations

BR-FED-02: Wikidata Universal
  All entity types (except temporal backbone) MUST include Wikidata in uses_federations

Examples:
- Place: MUST use Pleiades (ancient geography authority)
- Period: MUST use PeriodO (temporal authority)
- SubjectConcept: MUST use LCSH + FAST + LCC (library standards)

Acceptance Criteria:
- All Schema nodes have uses_federations property
- Federation list matches actual data sources
- Can query: "Which entity types use Wikidata?"
```

**Option B: Document as Pattern**
- This is implementation detail, not business requirement
- Document in ARCHITECTURE_GOVERNANCE.md
- No formal requirement needed

**Graph Architect Recommendation:** **Option B** — This is architectural pattern, not business requirement.

---

## Summary: BA Action Items

### Immediate Actions

| # | Action | Effort | Priority | Recommendation |
|---|--------|--------|----------|----------------|
| 1 | **Decide on ADR-004 requirement** | 30 min | MEDIUM | Fold into REQ-FUNC-006 (Entity Scaling) |
| 2 | **Align entity type naming** | 1 hour | LOW | Create REQ-DATA-005 or defer to Dev |
| 3 | **Decide on temporal backbone types** | 15 min | LOW | Document as infrastructure (no requirement) |
| 4 | **Document federation dependencies** | 30 min | LOW | Architectural pattern (no requirement) |

### Recommended New Requirements (If Any)

**REQ-DATA-005: Meta-Model Entity Type Alignment** (Optional — LOW priority)
- Align EntityType registry with cipher spec
- Rename: Human → PERSON, etc.
- Add: MATERIAL, OBJECT
- Effort: 1 hour (Dev), 30 min (QA)

**No other requirements needed** — architectural findings are implementation details that Dev can handle without formal requirements.

---

## Validation: Check Existing Requirements

### Do Any Existing Requirements Need Updates?

Let me check if architectural findings conflict with or enhance existing requirements:

| Requirement | Impact from Architecture Review | Action Needed |
|-------------|--------------------------------|---------------|
| **REQ-FUNC-001** (Entity Import) | ✅ Validated by schema audit | No change |
| **REQ-FUNC-002** (Tier 1 Cipher) | ✅ Validated, constraints exist | No change |
| **REQ-FUNC-003** (Tier 2 Cipher) | ✅ Validated, 360 FacetedEntity nodes | No change |
| **REQ-FUNC-004** (Authority Cascade) | ✅ Enhanced by federation scoring discovery | Consider: Add federation score to requirement? |
| **REQ-FUNC-005** (Temporal Anchor) | ✅ ADR-002 supports this | No change |
| **REQ-DATA-001** (Entity Types) | ⚠️ Mismatch: 9 canonical vs 14 in meta-model | Consider: Clarify which types are canonical |
| **REQ-DATA-002** (Facet Registry) | ✅ Perfect match (18 facets) | No change |
| **REQ-DATA-003** (Qualifiers) | ✅ Addressed in Tier 3 addendum | No change |
| **REQ-FUNC-006** (Entity Scaling) | ⚠️ Should include CONCEPT migration | **Update:** Add CONCEPT migration to acceptance criteria |
| **REQ-FUNC-010** (Relationships) | ✅ Validated (788 rels imported) | No change |

### Recommended Update: REQ-FUNC-006 (Entity Scaling)

**Current Acceptance Criteria (check REQUIREMENTS.md):**
```gherkin
Scenario: Scale to 10,000 entities
  When entity scaling complete
  Then 10,000+ entities exist
  And all entities have relationships
  And federation scores calculated
```

**Recommended Addition:**
```gherkin
Scenario: Migrate legacy CONCEPT entities during scaling
  Given 258 entities with entity_type="CONCEPT"
  When entity scaling from 300 to 10,000
  Then CONCEPT entities reclassified to canonical types
  And CONCEPT count decreases incrementally
  And 0 CONCEPT entities at 10K milestone
  And all migrated entities have correct cipher format
```

---

## Clear BA Action Plan

### Step 1: Review REQ-FUNC-006 (Entity Scaling)

**Check if it includes CONCEPT migration**
- If NO → Add scenario for CONCEPT migration
- If YES → Verify it aligns with ADR-004

### Step 2: Decide on REQ-DATA-005 (Entity Type Alignment)

**Question:** Create new requirement for meta-model alignment?
- **If YES:** Use template above (REQ-DATA-005)
- **If NO:** Flag as Dev task (no formal requirement)

**Recommendation:** **NO requirement needed** — This is technical debt cleanup, can be handled as Dev task during entity scaling.

### Step 3: Clarify REQ-DATA-001 (Entity Type Registry)

**Current state unclear:**
- Does it refer to cipher spec types (9) or meta-model types (14)?
- Should temporal backbone types (Year, Decade, Century) be included?

**Recommended Clarification:**
```markdown
REQ-DATA-001: Entity Type Registry (9 types)

**Scope:** Domain entity types only (entities that can be subjects of claims)

**Included:**
PERSON, EVENT, PLACE, SUBJECTCONCEPT, WORK,
ORGANIZATION, PERIOD, MATERIAL, OBJECT

**Excluded (Infrastructure Types):**
Year, Decade, Century, Millennium — Temporal backbone (not domain entities)
PlaceType, PeriodCandidate — Support types (not domain entities)

**Note:** CONCEPT is DEPRECATED legacy type (ADR-004)
```

### Step 4: No Other Requirements Needed

**Architectural findings that DON'T need requirements:**
- TemporalAnchor pattern → Already covered by REQ-FUNC-005
- Qualifier support → Already covered by REQ-DATA-003
- DDL execution → Implementation task (not business requirement)
- Pydantic models → Implementation task (not business requirement)
- Schema nodes → Architectural pattern (not business requirement)
- Federation registry → Already implemented (discovered, not new)

---

## Summary: Is This Actionable for BA?

### ✅ **Yes, but minimal work needed:**

**Required Actions (2-3 hours total):**
1. **Update REQ-FUNC-006** — Add CONCEPT migration scenario (30 min)
2. **Clarify REQ-DATA-001** — Specify scope (domain entities vs infrastructure) (30 min)
3. **Optional: Create REQ-DATA-005** — Meta-model alignment (1 hour) — OR flag as Dev task (15 min)

**Not Required:**
- No new requirements for DDL execution (Dev task)
- No new requirements for Pydantic models (Dev task)
- No new requirements for federation registry (already exists)
- No new requirements for schema nodes (architectural pattern)

---

## Checklist for BA

### Immediate (Before Dev Executes)

- [ ] Read `md/Architecture/SCHEMA_REALITY_VS_SPEC_ANALYSIS.md` (gap analysis)
- [ ] Read `md/Architecture/META_MODEL_SELF_DESCRIBING_GRAPH.md` (meta-model pattern)
- [ ] Review ADR-004 (CONCEPT type handling) — Already approved, needs documentation?
- [ ] Check REQ-FUNC-006 (Entity Scaling) — Does it include CONCEPT migration?
- [ ] Clarify REQ-DATA-001 (Entity Type Registry) — 9 canonical vs 14 in meta-model

### Decision Points

**Decision 1:** Create REQ-DATA-005 (Meta-Model Alignment)?
- YES → Write requirement for EntityType naming alignment
- NO → Flag as Dev cleanup task

**Decision 2:** Update REQ-FUNC-006 (Entity Scaling)?
- Add CONCEPT migration scenario
- Add acceptance criteria for 0 CONCEPT by 10K

**Decision 3:** Clarify REQ-DATA-001 (Entity Type Registry)?
- Specify: "9 canonical types (domain entities only)"
- Exclude: Temporal backbone types, support types

### After Review

- [ ] Update REQUIREMENTS.md with changes
- [ ] Update AI_CONTEXT.md with BA actions taken
- [ ] Coordinate with PM for KANBAN updates

---

## Template: If Creating REQ-DATA-005

**Copy-paste ready:**

```markdown
### REQ-DATA-005: Meta-Model Entity Type Alignment

**Status:** PROPOSED  
**Priority:** LOW  
**Submitted:** 2026-02-22  
**Source:** Graph Architect schema audit (META_MODEL_SELF_DESCRIBING_GRAPH.md)  
**Submitted By:** Requirements Analyst Agent

**Business Requirement:**
Align EntityType meta-model registry with canonical cipher specification.

**Business Value:**
- Single source of truth (no Human/PERSON confusion)
- Complete registry (all 9 canonical types present)
- Schema consistency (meta-model matches architecture docs)

**Changes Required:**

| Current (Meta-Model) | Target (Cipher Spec) | Action |
|---------------------|---------------------|--------|
| Human | PERSON | RENAME |
| Organization | ORGANIZATION | RENAME |
| Period | PERIOD | RENAME |
| SubjectConcept | SUBJECTCONCEPT | RENAME |
| (missing) | MATERIAL | ADD |
| (missing) | OBJECT | ADD |

**Keep Unchanged:**
- Year, Decade, Century, Millennium (temporal backbone — infrastructure types)
- PlaceType, PeriodCandidate (support types)

**Business Rules:**
```
BR-META-01: Canonical Names Required
  EntityType nodes MUST use canonical uppercase names (PERSON, not Human)
  Severity: MEDIUM

BR-META-02: Complete Registry
  Meta-model MUST include all 9 canonical entity types
  Severity: MEDIUM

BR-META-03: Backward Compatibility
  Store legacy names in legacy_name property for reference
  Severity: LOW
```

**Acceptance Criteria:**
```gherkin
Scenario: EntityType names match cipher spec
  When query EntityType registry
  Then names are PERSON, ORGANIZATION, PERIOD (uppercase)
  And no "Human", "Organization" lowercase names

Scenario: All 9 canonical types present
  When query EntityType registry
  Then MATERIAL and OBJECT types exist
  And total canonical types = 9

Scenario: Legacy names preserved
  When query EntityType {name: "PERSON"}
  Then legacy_name property = "Human"
```

**Implementation:**
```cypher
// Update EntityType names
MATCH (et:EntityType {name: "Human"})
SET et.legacy_name = "Human", et.name = "PERSON"

MATCH (et:EntityType {name: "Organization"})
SET et.legacy_name = "Organization", et.name = "ORGANIZATION"

// Add missing types
CREATE (et1:EntityType {
  name: "MATERIAL",
  description: "Physical materials (metals, stone, wood)"
})
CREATE (et2:EntityType {
  name: "OBJECT",
  description: "Physical objects (weapons, tools, artifacts)"
})

MATCH (root:EntityRoot)
CREATE (root)-[:HAS_CHILD_TYPE]->(et1)
CREATE (root)-[:HAS_CHILD_TYPE]->(et2)
```

**Effort:** 1 hour (Dev), 30 min (QA verification)  
**Risk:** LOW (meta-model update only, no data changes)
```

---

## Final Answer: Is This Actionable?

### ✅ **YES — Here's What BA Should Do:**

**Minimum Required (1 hour):**
1. Update REQ-FUNC-006 with CONCEPT migration scenario
2. Clarify REQ-DATA-001 scope (9 canonical types, infrastructure excluded)

**Optional (1 hour):**
3. Create REQ-DATA-005 for meta-model alignment

**Total BA Effort:** 1-2 hours max

**Everything else is Dev implementation** (DDL, Pydantic, registry updates) — no requirements needed.

---

**Document Status:** ✅ BA Action Plan Complete  
**Graph Architect:** Chrystallum Architecture Team  
**Date:** February 22, 2026
