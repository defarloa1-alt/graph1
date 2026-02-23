# Dev Agent Schema Execution Guide

**Date:** February 22, 2026  
**From:** Graph Architect  
**To:** Dev Agent  
**Status:** Ready to Execute (Awaiting Stakeholder Go-Ahead)

---

## Executive Summary

✅ **Neo4j Aura Access:** Confirmed  
⚠️ **Schema Status:** Migration (not greenfield) — 73 constraints and 79 indexes already exist  
✅ **Safe to Execute:** DDL uses `IF NOT EXISTS` — will skip existing, add only missing  
🎯 **Expected Additions:** ~6 constraints, ~10 indexes (TemporalAnchor + Qualifiers)

---

## Current Database State (As of 2026-02-22)

### What Already Exists ✅

**Constraints (73 total):**
- ✅ `entity_cipher_unique` (Entity.entity_cipher) — **Already matches our spec!**
- ✅ `entity_qid_unique` (Entity.qid) — **Already matches our spec!**
- ✅ `entity_has_type` (Entity.entity_type NOT NULL) — **Already matches our spec!**
- ✅ `claim_cipher_unique` (Claim.cipher) — **Already matches our spec!**
- ✅ 69 other constraints for legacy node types (Human, Organization, Period, etc.)

**Indexes (79 total):**
- ✅ `entity_type_idx` (Entity.entity_type, entity_cipher) — **Already matches our spec!**
- ✅ `faceted_cipher_idx` (FacetedEntity.faceted_cipher) — **Already matches our spec!**
- ✅ `faceted_entity_facet_idx` (FacetedEntity.entity_cipher, facet_id) — **Already matches our spec!**
- ✅ 76 other indexes (auto-created from constraints + legacy types)

### What's Missing ❌

**TemporalAnchor Pattern (0 nodes):**
- ❌ No `:TemporalAnchor` labels exist
- ❌ No `temporal_start_year` properties
- ❌ No `temporal_end_year` properties
- ❌ No `temporal_scope` properties
- ❌ No TemporalAnchor constraints (6 missing)
- ❌ No TemporalAnchor indexes (3 missing)

**Qualifier Support (0 claims with qualifiers):**
- ❌ No qualifier indexes (7 missing)
- ❌ No `qualifier_p580_normalized` properties
- ❌ No qualifier-based claims yet

### Schema Issues (Migration Needed)

**Issue 1: Old Cipher Format**
- Found: `ent_con_Q11514315` (CONCEPT - deprecated)
- Expected: `ent_prd_Q11514315` (PERIOD - canonical)
- Count: ~297 entities using old format

**Issue 2: Dual Schema**
- Legacy node types: `:Human`, `:Organization`, `:Period`, `:Place`, `:Event`, `:Work`
- New unified type: `:Entity` (with entity_type property)
- Both coexist in database

---

## Execution Plan (Safe, Incremental)

### Phase 1: Execute DDL Addendum (LOW RISK)

**Why it's safe:**
- All DDL uses `IF NOT EXISTS` clauses
- Neo4j will skip existing constraints/indexes
- Only missing items will be created
- No data modification (schema only)

**What will be created:**
```
Expected Additions:
  TemporalAnchor Constraints: 3
  TemporalAnchor Indexes: 3
  Qualifier Indexes: 7
  Total New Items: ~13
```

**What will be skipped:**
```
Already Exists (Will Skip):
  entity_cipher_unique
  entity_qid_unique
  entity_has_type
  entity_type_idx
  claim_cipher_unique
  faceted_cipher_idx
  faceted_entity_facet_idx
  ... and others
```

**Execution Script:** (Ready to run)

```python
#!/usr/bin/env python3
"""
Execute DDL Addendum: TemporalAnchor + Qualifiers
Safe to run - uses IF NOT EXISTS
"""

from neo4j import GraphDatabase
import sys

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# DDL statements (ONLY what's missing from analysis)
ddl_statements = [
    # ─────────────────────────────────────────────────────────
    # TEMPORALANCHOR CONSTRAINTS (3 new)
    # ─────────────────────────────────────────────────────────
    "CREATE CONSTRAINT temporal_start_year_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_start_year IS NOT NULL",
    "CREATE CONSTRAINT temporal_end_year_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_end_year IS NOT NULL",
    "CREATE CONSTRAINT temporal_scope_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_scope IS NOT NULL",
    
    # ─────────────────────────────────────────────────────────
    # TEMPORALANCHOR INDEXES (3 new)
    # ─────────────────────────────────────────────────────────
    "CREATE INDEX temporal_range_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_start_year, n.temporal_end_year)",
    "CREATE INDEX temporal_nesting_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_start_year)",
    "CREATE INDEX temporal_calendar_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_calendar)",
    
    # ─────────────────────────────────────────────────────────
    # QUALIFIER INDEXES - TIER 3 (7 new)
    # ─────────────────────────────────────────────────────────
    "CREATE INDEX claim_wikidata_triple_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.wikidata_pid, c.object_qid)",
    "CREATE INDEX claim_temporal_start_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p580_normalized)",
    "CREATE INDEX claim_temporal_end_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p582_normalized)",
    "CREATE INDEX claim_temporal_point_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p585_normalized)",
    "CREATE INDEX claim_location_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p276_qid)",
    "CREATE INDEX claim_ordinal_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p1545_ordinal)",
    "CREATE INDEX claim_temporal_scope_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.temporal_scope)",
]

print("=" * 60)
print("EXECUTING DDL ADDENDUM")
print("=" * 60)
print(f"Total statements: {len(ddl_statements)}")
print(f"Database: {NEO4J_URI}")
print()

created = []
skipped = []
errors = []

with driver.session() as session:
    for i, ddl in enumerate(ddl_statements, 1):
        # Extract name (CONSTRAINT name or INDEX name)
        parts = ddl.split()
        if 'CONSTRAINT' in ddl:
            name = parts[2]  # CREATE CONSTRAINT name_here
        elif 'INDEX' in ddl:
            name = parts[2]  # CREATE INDEX name_here
        else:
            name = "unknown"
        
        print(f"[{i:2d}/{len(ddl_statements)}] {name}...")
        
        try:
            session.run(ddl)
            created.append(name)
            print(f"         ✓ Created")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "equivalent" in error_msg:
                skipped.append(name)
                print(f"         ○ Already exists (skipped)")
            else:
                errors.append((name, str(e)))
                print(f"         ✗ Error: {e}")

print()
print("=" * 60)
print("EXECUTION SUMMARY")
print("=" * 60)
print(f"Created:  {len(created)}")
print(f"Skipped:  {len(skipped)}")
print(f"Errors:   {len(errors)}")
print()

if created:
    print("Created:")
    for name in created:
        print(f"  ✓ {name}")
    print()

if errors:
    print("Errors:")
    for name, error in errors:
        print(f"  ✗ {name}: {error}")
    print()

# Verification
print("=" * 60)
print("VERIFICATION")
print("=" * 60)

with driver.session() as session:
    # Count constraints
    result = session.run("SHOW CONSTRAINTS")
    total_constraints = sum(1 for _ in result)
    print(f"Total Constraints: {total_constraints}")
    
    # Count indexes
    result = session.run("SHOW INDEXES")
    total_indexes = sum(1 for _ in result)
    print(f"Total Indexes: {total_indexes}")
    
    # Check TemporalAnchor
    result = session.run("MATCH (n:TemporalAnchor) RETURN count(n) as total")
    temporal_count = result.single()['total']
    print(f"TemporalAnchor nodes: {temporal_count}")

driver.close()

print()
print("=" * 60)
if len(errors) == 0:
    print("✓ DDL EXECUTION COMPLETE")
else:
    print("✗ DDL EXECUTION COMPLETED WITH ERRORS")
    sys.exit(1)
print("=" * 60)
```

**Save as:** `scripts/execute_ddl_addendum.py`

**Priority 2: Verify Schema Changes**

```bash
# After running DDL, verify changes:
python check_schema.py

# Expected output:
#   Total Constraints: ~79 (73 + 6 new)
#   Total Indexes: ~89 (79 + 10 new)
#   TemporalAnchor nodes: 0 (labels/properties not added yet)
```

**Priority 3: Implement Pydantic Models**

```bash
# Create model files from specifications
mkdir -p scripts/models
touch scripts/models/__init__.py

# Copy code from:
# - PYDANTIC_MODELS_SPECIFICATION.md → scripts/models/entities.py
# - TIER_3_CLAIM_CIPHER_ADDENDUM.md → scripts/models/claims.py

# Install dependencies
pip install pydantic>=2.0

# Test
python -c "from scripts.models.entities import Entity; print('✓ Models loaded')"
```

**Priority 4: Schema Migration Tasks (DEFER UNTIL STAKEHOLDER APPROVAL)**

These tasks modify data, not just schema. Require explicit approval:

1. **Migrate old cipher format** (`ent_con_*` → canonical entity type prefixes)
2. **Add TemporalAnchor properties** to eligible entities (Q17167, etc.)
3. **Add TemporalAnchor labels** to entities with temporal properties
4. **Reconcile dual schema** (legacy labels vs unified Entity)

---

## Critical Implementation Notes

### ⚠️ MERGE + Label Interaction (STILL APPLIES)

Even after DDL is run, Dev must handle label addition explicitly:

```cypher
// When updating entities with temporal properties:
MERGE (n:Entity {entity_cipher: $cipher})
ON CREATE SET n += $properties
ON MATCH SET n += $properties

// Explicitly add TemporalAnchor label if temporal properties present
WITH n
WHERE n.temporal_start_year IS NOT NULL 
  AND n.temporal_end_year IS NOT NULL
  AND NOT n:TemporalAnchor
SET n:TemporalAnchor
```

**Test Cases Required:**
1. Create new entity with temporal properties → `:TemporalAnchor` label added
2. Update existing entity with temporal properties → `:TemporalAnchor` label added
3. Re-import same entity → idempotent (no duplicates)

---

## Risk Assessment

| Task | Risk Level | Mitigation |
|------|-----------|------------|
| Execute DDL addendum | LOW | `IF NOT EXISTS` prevents conflicts |
| Add TemporalAnchor constraints | LOW | New label, no existing nodes affected |
| Add qualifier indexes | LOW | New properties, no conflicts |
| Migrate cipher format | MEDIUM | Requires data updates, test thoroughly |
| Add temporal properties | MEDIUM | Requires Wikidata queries, validation |

**Recommendation:** Execute Phase 1 (DDL addendum) immediately — zero risk, enables future work.

---

## Success Criteria

**After DDL Execution:**
- [ ] 6 new TemporalAnchor constraints created
- [ ] 10 new indexes created (3 TemporalAnchor + 7 Qualifier)
- [ ] No errors during execution
- [ ] `SHOW CONSTRAINTS` returns ~79 total
- [ ] `SHOW INDEXES` returns ~89 total

**After Pydantic Implementation:**
- [ ] `scripts/models/entities.py` created and tested
- [ ] `scripts/models/claims.py` created and tested
- [ ] Entity validation passes for 300 existing entities
- [ ] Claim validation includes qualifier normalization

---

## Files for Execution

| File | Purpose | Usage |
|------|---------|-------|
| `scripts/execute_ddl_addendum.py` | Run DDL (create from guide above) | `python scripts/execute_ddl_addendum.py` |
| `check_schema.py` | Verify schema after execution | `python check_schema.py` |
| `md/Architecture/NEO4J_SCHEMA_DDL_COMPLETE.md` | Complete DDL reference | Read-only (reference) |
| `md/Architecture/TIER_3_CLAIM_CIPHER_ADDENDUM.md` | Qualifier spec | Read-only (reference) |
| `md/Architecture/PYDANTIC_MODELS_SPECIFICATION.md` | Pydantic models | Copy code to scripts/models/ |

---

## Next Actions (Awaiting Stakeholder Approval)

**Immediate (Safe to Execute):**
1. Run `scripts/execute_ddl_addendum.py` (DDL only, no data changes)
2. Verify with `check_schema.py`
3. Implement Pydantic models

**Deferred (Requires Approval):**
1. Migrate cipher format (data modification)
2. Add TemporalAnchor properties (Wikidata queries)
3. Backfill temporal data for 300 entities

---

**Status:** ✅ Ready for execution when stakeholder approves  
**Estimated Time:** 1-2 hours (DDL + Pydantic)  
**Risk:** LOW (schema additions only, no data modification)

---

**Graph Architect:** Chrystallum Architecture Team  
**Last Updated:** February 22, 2026
