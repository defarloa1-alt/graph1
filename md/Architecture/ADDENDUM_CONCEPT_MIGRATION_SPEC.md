# Appendix: CONCEPT Entity Migration Specification

**Date:** February 22, 2026  
**Status:** Migration Plan  
**Related:** CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md, REQ-DATA-004

---

## Purpose

Provide executable migration plan for reclassifying 258 CONCEPT entities from legacy catch-all to canonical types or rehabilitated CONCEPT (abstract ideas only).

---

## Background

**Issue:** 86% of database (258/300 entities, now 2,034/2,600) classified as `entity_type="CONCEPT"`

**Root Cause:** Early SCA used CONCEPT as catch-all for unclassified entities

**Solution:** 
- **Rehabilitate CONCEPT** as legitimate type for abstract ideas (democracy, stoicism)
- **Reclassify misclassified entities** to canonical types (PERSON, ORGANIZATION, PERIOD, etc.)

---

## Decision Rules (DMN-Style)

### Rule 1: Genuine Abstract Concepts (Keep as CONCEPT)

**Criteria:** Must have `P31: Q17736` (concept) OR be genuinely abstract

**Examples:**
```
Q7174 (democracy) - Abstract political concept → KEEP as CONCEPT
Q48235 (stoicism) - Abstract philosophical concept → KEEP as CONCEPT
Q9134 (monotheism) - Abstract religious concept → KEEP as CONCEPT
```

**P31 Classes for CONCEPT:**
- Q17736 (concept)
- Q7725634 (literary concept)
- Q2151998 (philosophical concept)
- E28 Conceptual Object
- E55 Type

**Action:** Keep `entity_type="CONCEPT"`, `entity_cipher="ent_con_Q7174"`

---

### Rule 2: Misclassified Historical Periods (Reclassify to PERIOD)

**Criteria:** Has `P31: Q11514315` (historical period)

**Examples:**
```
ent_con_Q11514315 (historical period itself) → ent_prd_Q11514315 (PERIOD)
ent_con_Q6813 (Hellenistic period) → ent_prd_Q6813 (PERIOD)
```

**Action:** Reclassify to PERIOD

---

### Rule 3: Misclassified Organizations (Reclassify to ORGANIZATION)

**Criteria:** Has `P31: Q43229` (organization) OR `P31: Q15911314` (institution)

**Examples:**
```
ent_con_Q130614 (Roman Senate) → ent_org_Q130614 (ORGANIZATION)
ent_con_Q1114821 (citizens' assemblies) → ent_org_Q1114821 (ORGANIZATION)
```

**Action:** Reclassify to ORGANIZATION

---

### Rule 4: Misclassified Categories (Special Handling)

**Criteria:** QID starts with "Category:" or has `P31: Q4167836` (Wikimedia category)

**Examples:**
```
ent_con_Q6944405 (Category:Roman Republic) → DELETE or flag as meta
ent_con_Q13285410 (Category:People from Roman Republic) → DELETE or flag as meta
```

**Action:** These are Wikimedia metadata, not domain entities. Mark for deletion or reclassify as tags.

---

### Rule 5: Religion/Language/Culture (Reclassify or Keep CONCEPT)

**Criteria:** Determine if concrete or abstract

**Examples:**
```
ent_con_Q337547 (ancient Roman religion) → ent_con_Q337547 (CONCEPT - abstract religious system)
ent_con_Q397 (Latin language) → ent_con_Q397 (CONCEPT - abstract language concept)
OR
Create new type: LANGUAGE (lan) for languages specifically
```

**Decision Needed:** Add LANGUAGE type, or keep as CONCEPT?

---

### Rule 6: Forms of Government (Keep CONCEPT or Reclassify)

**Criteria:** Abstract political system vs concrete instance

**Examples:**
```
ent_con_Q1307214 (form of government) → ent_con_Q1307214 (CONCEPT - abstract)
ent_con_Q48349 (empire - as concept) → ent_con_Q48349 (CONCEPT - abstract)

BUT:
Q12548 (Holy Roman Empire - specific instance) → ent_org_Q12548 (ORGANIZATION)
```

**Rule:** If P31 includes Q1048835 (political territorial entity), reclassify to ORGANIZATION. Otherwise keep as CONCEPT (abstract).

---

## Migration Query (Executable Cypher)

```cypher
// ═══════════════════════════════════════════════════════════════
// CONCEPT ENTITY RECLASSIFICATION (2026-02-22)
// ═══════════════════════════════════════════════════════════════

// Step 1: Identify entities to reclassify
MATCH (e:Entity {entity_type: "CONCEPT"})
OPTIONAL MATCH (e)-[:INSTANCE_OF]->(class)
WITH e, collect(class.qid) as instance_classes

// Step 2: Apply decision rules
WITH e, instance_classes,
  CASE
    // Rule 1: Genuine concepts (keep as CONCEPT)
    WHEN any(c IN instance_classes WHERE c IN ['Q17736', 'Q7725634', 'Q2151998'])
      THEN 'KEEP_CONCEPT'
    
    // Rule 2: Historical periods
    WHEN any(c IN instance_classes WHERE c = 'Q11514315')
      THEN 'RECLASSIFY_PERIOD'
    
    // Rule 3: Organizations
    WHEN any(c IN instance_classes WHERE c IN ['Q43229', 'Q15911314', 'Q1048835'])
      THEN 'RECLASSIFY_ORGANIZATION'
    
    // Rule 4: Wikimedia categories (delete)
    WHEN e.qid STARTS WITH 'Q' AND e.label STARTS WITH 'Category:'
      THEN 'DELETE_CATEGORY'
    
    // Rule 5: Abstract systems (keep as CONCEPT)
    WHEN any(c IN instance_classes WHERE c IN ['Q9134', 'Q48235', 'Q397'])  // religion, philosophy, language
      THEN 'KEEP_CONCEPT'
    
    // Rule 6: Political territorial entities
    WHEN any(c IN instance_classes WHERE c IN ['Q1048835', 'Q7275'])  // political entity, state
      THEN 'RECLASSIFY_ORGANIZATION'
    
    // Default: Manual review needed
    ELSE 'MANUAL_REVIEW'
  END as migration_action

// Step 3: Execute reclassification
WITH e, migration_action
WHERE migration_action <> 'KEEP_CONCEPT'

// Reclassify to PERIOD
CALL {
  WITH e, migration_action
  WITH e WHERE migration_action = 'RECLASSIFY_PERIOD'
  SET e.entity_type = 'PERIOD',
      e.entity_cipher = 'ent_prd_' + e.qid,
      e.migration_date = datetime(),
      e.migration_from = 'CONCEPT'
  CREATE (e)-[:SAME_AS {
    reason: 'CONCEPT_MIGRATION',
    old_cipher: 'ent_con_' + e.qid,
    new_cipher: 'ent_prd_' + e.qid,
    migrated_at: datetime()
  }]->(e)
  RETURN count(e) as period_count
}

// Reclassify to ORGANIZATION
CALL {
  WITH e, migration_action
  WITH e WHERE migration_action = 'RECLASSIFY_ORGANIZATION'
  SET e.entity_type = 'ORGANIZATION',
      e.entity_cipher = 'ent_org_' + e.qid,
      e.migration_date = datetime(),
      e.migration_from = 'CONCEPT'
  CREATE (e)-[:SAME_AS {
    reason: 'CONCEPT_MIGRATION',
    old_cipher: 'ent_con_' + e.qid,
    new_cipher: 'ent_org_' + e.qid,
    migrated_at: datetime()
  }]->(e)
  RETURN count(e) as org_count
}

// Mark for deletion (Wikimedia categories)
CALL {
  WITH e, migration_action
  WITH e WHERE migration_action = 'DELETE_CATEGORY'
  SET e:ToDelete,
      e.deletion_reason = 'Wikimedia metadata, not domain entity',
      e.flagged_at = datetime()
  RETURN count(e) as delete_count
}

// Flag for manual review
CALL {
  WITH e, migration_action
  WITH e WHERE migration_action = 'MANUAL_REVIEW'
  SET e:RequiresReview,
      e.review_reason = 'Could not auto-classify, needs SCA review',
      e.flagged_at = datetime()
  RETURN count(e) as review_count
}

RETURN 
  period_count,
  org_count,
  delete_count,
  review_count;
```

---

## Migration Phases

### Phase 1: Automated Reclassification (Immediate)

**Input:** 2,034 CONCEPT entities (from 2,600 total as of 2026-02-22)

**Decision Rules:**
- P31-based classification (200-300 entities)
- Label pattern matching (50-100 entities)
- QID-based rules (Wikimedia categories)

**Expected Output:**
- PERIOD: 50-100 entities
- ORGANIZATION: 30-60 entities
- DELETE: 10-20 Wikimedia categories
- KEEP_CONCEPT: 100-200 genuine concepts
- MANUAL_REVIEW: 1,600-1,800 entities

**Time:** 2 hours (query execution + validation)

---

### Phase 2: Manual Review (During Entity Scaling)

**Input:** ~1,600-1,800 entities flagged for manual review

**Process:**
1. Export entities with `:RequiresReview` label
2. SCA reviews in batches of 100
3. Apply classification logic
4. Update `entity_type` and `entity_cipher`
5. Remove `:RequiresReview` label

**Time:** 10 hours (distributed across entity scaling sprints)

---

### Phase 3: Validation (After Migration)

**Verification Queries:**

```cypher
// 1. Check: No CONCEPT entities remain with wrong P31
MATCH (e:Entity {entity_type: "CONCEPT"})
OPTIONAL MATCH (e)-[:INSTANCE_OF]->(class)
WHERE class.qid NOT IN ['Q17736', 'Q7725634', 'Q2151998']
RETURN count(e) as misclassified_concepts
// Should return: 0

// 2. Check: All reclassified entities have correct ciphers
MATCH (e:Entity)
WHERE e.entity_type = 'PERIOD' AND e.entity_cipher STARTS WITH 'ent_con_'
RETURN count(e) as wrong_cipher_periods
// Should return: 0

// 3. Check: SAME_AS edges created for all migrations
MATCH (e:Entity)
WHERE e.migration_from = 'CONCEPT'
MATCH (e)-[s:SAME_AS]->(e)
WHERE s.reason = 'CONCEPT_MIGRATION'
RETURN count(e) as with_same_as, count(s) as same_as_edges
// Should match

// 4. Summary statistics
MATCH (e:Entity)
RETURN e.entity_type, count(e) as count
ORDER BY count DESC
// Should show: CONCEPT count significantly reduced
```

---

## Expected Outcomes

**Before Migration (Current):**
```
CONCEPT: 2,034 entities (78%)
PERSON: 403
PLACE: 68
ORGANIZATION: 39
Others: 56
```

**After Phase 1 (Automated):**
```
CONCEPT: ~1,700 (needs review) + ~150 (genuine concepts)
PERIOD: ~100 (reclassified from CONCEPT)
ORGANIZATION: ~90 (39 + 51 reclassified)
:ToDelete: ~20 (Wikimedia categories)
:RequiresReview: ~1,700 (manual)
```

**After Phase 2 (Manual Review):**
```
CONCEPT: ~150-300 (genuine abstract concepts only)
All others: Properly classified to 12 canonical types
:RequiresReview: 0
```

**Target by 10K Entities:**
```
CONCEPT: 1-3% (only genuine abstract concepts)
All canonical types properly distributed
Zero misclassified entities
```

---

## Implementation Checklist

**Dev Agent:**
- [ ] Run Phase 1 automated reclassification query
- [ ] Verify SAME_AS edges created
- [ ] Export `:RequiresReview` entities to CSV
- [ ] Update `scripts/tools/entity_cipher.py` with DEITY, LAW, rehabilitated CONCEPT

**SCA Agent:**
- [ ] Review flagged entities (batch of 100)
- [ ] Apply classification rules
- [ ] Update entity_type + regenerate ciphers

**QA Agent:**
- [ ] Run validation queries (4 checks)
- [ ] Verify no misclassified CONCEPT entities
- [ ] Verify all ciphers match entity_type
- [ ] Verify SAME_AS edge integrity

---

## References

- REQ-DATA-004: Legacy CONCEPT Type Migration
- ADR-004: Legacy CONCEPT Type Handling (approved)
- CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md §1.1

---

**Document Status:** ✅ Migration Spec Complete  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026
