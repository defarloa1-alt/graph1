# Discovery Relationships - Wikidata Alignment Analysis

**Date:** 2025-12-12  
**Purpose:** Identify Wikidata property mappings for discovery relationships added in this session  
**Impact:** 40 new relationships (Evolution, Production, Functional, Comparative, Typological) currently have 0% Wikidata coverage

---

## Summary

The user's principle: **"If aligned with [Wikidata], should use the federated ids"**

This means: When our relationships semantically match Wikidata properties, we should add the Wikidata property for federation/interoperability, even though "ours are better" (more specific).

---

## Potential Wikidata Property Mappings

### Evolution Relationships (10 relationships)

| Chrystallum Relationship | Wikidata Property | Rationale | Status |
|-------------------------|-------------------|-----------|--------|
| `REPLACED_BY` | `P1366` | Replaced by (item replaced by) | ✅ Good match |
| `SUPERSEDED_BY` | `P1366` | Also "replaced by" (same concept) | ✅ Good match |
| `DISPLACED_BY` | `P1366` | Similar to replaced by | ⚠️ Close match |
| `INTRODUCED_IN` | `P580` | Start time / introduced | ✅ Good match |
| `CEASED_USE_IN` | `P582` | End time / ceased | ✅ Good match |
| `PREVALENT_DURING` | `P580/P582` | Time period (would need qualifiers) | ⚠️ Complex |
| `INTRODUCED_BY` | `P828` | Has cause / introduced by event | ⚠️ Close match |
| `OBSOLETE_AFTER` | `P582` | End time / obsolete after | ✅ Good match |
| `OBSOLETE_DUE_TO` | `P828` | Has cause / reason | ⚠️ Close match |
| `PHASED_OUT_BECAUSE` | `P828` | Has cause / reason | ⚠️ Close match |

**Note:** P1366 is "replaced by", P580 is "start time", P582 is "end time", P828 is "has cause"

### Production Relationships (6 relationships)

| Chrystallum Relationship | Wikidata Property | Rationale | Status |
|-------------------------|-------------------|-----------|--------|
| `MANUFACTURED_BY` | `P176` | Manufacturer | ✅ Excellent match |
| `MANUFACTURED_IN` | `P1071` | Location of creation | ✅ Good match |
| `TYPICALLY_MADE_OF` | `P186` | Material used | ✅ Good match (already used for MATERIAL_USED) |
| `REQUIRES_MATERIAL` | `P186` | Material used / required | ⚠️ Close (but different nuance) |
| `MADE_USING_TECHNIQUE` | `P2079` | Fabrication method | ✅ Good match |
| `REQUIRES_SKILL` | *No direct match* | Skills are complex in Wikidata | ❌ No match |

**Note:** P176 is "manufacturer", P1071 is "location of creation", P186 is "material used", P2079 is "fabrication method"

### Functional Relationships (4 relationships)

| Chrystallum Relationship | Wikidata Property | Rationale | Status |
|-------------------------|-------------------|-----------|--------|
| `DESIGNED_FOR` | `P366` | Use case | ✅ Good match (already used for USE) |
| `EFFECTIVE_AGAINST` | `P366` | Use case / effective against | ⚠️ Close (different nuance) |
| `INEFFECTIVE_AGAINST` | *No direct match* | Negative effectiveness | ❌ No match |
| `OPTIMAL_IN` | `P366` | Use case | ⚠️ Close (different nuance) |

**Note:** P366 is "use" (used for purpose)

### Typological Relationships (3 relationships)

| Chrystallum Relationship | Wikidata Property | Rationale | Status |
|-------------------------|-------------------|-----------|--------|
| `VARIANT_OF` | `P279` | Subclass of | ⚠️ Close but P279 is for entities, not relationships |
| `HAS_VARIANT` | `P279` | Inverse of subclass | ⚠️ Same issue |
| `ALTERNATIVE_TO` | *No direct match* | Alternative/equivalent | ❌ No match |

**Note:** P279 is "subclass of" but it's a property of entities, not a relationship type. Our relationships connect entities, so this may not align well.

### Comparative Relationships (5 relationships)

| Chrystallum Relationship | Wikidata Property | Rationale | Status |
|-------------------------|-------------------|-----------|--------|
| `SUPERIOR_TO` | *No direct match* | Comparison | ❌ No match |
| `INFERIOR_TO` | *No direct match* | Comparison | ❌ No match |
| `ADVANTAGE` | *No direct match* | Advantage descriptor | ❌ No match |
| `DISADVANTAGE` | *No direct match* | Disadvantage descriptor | ❌ No match |
| `COMPETED_WITH` | *No direct match* | Competition | ❌ No match |

**Note:** Wikidata doesn't have direct comparison properties - these are more semantic/analytical relationships.

---

## Recommended Mappings (High Confidence)

### Should Add Wikidata Properties:

1. **REPLACED_BY** → `P1366` (Replaced by) ✅
2. **SUPERSEDED_BY** → `P1366` (Replaced by) ✅
3. **MANUFACTURED_BY** → `P176` (Manufacturer) ✅
4. **MANUFACTURED_IN** → `P1071` (Location of creation) ✅
5. **TYPICALLY_MADE_OF** → `P186` (Material used) ✅
6. **MADE_USING_TECHNIQUE** → `P2079` (Fabrication method) ✅
7. **INTRODUCED_IN** → `P580` (Start time) ✅
8. **CEASED_USE_IN** → `P582` (End time) ✅
9. **OBSOLETE_AFTER** → `P582` (End time) ✅

### Close Matches (Consider but with caveats):

1. **DISPLACED_BY** → `P1366` (Replaced by) - close semantically
2. **DESIGNED_FOR** → `P366` (Use) - close but P366 is already used for USE
3. **REQUIRES_MATERIAL** → `P186` (Material used) - close but different nuance

### No Wikidata Match:

- Comparative relationships (SUPERIOR_TO, INFERIOR_TO, ADVANTAGE, etc.)
- Typological relationships (VARIANT_OF aligns with P279 but it's entity-level, not relationship)
- Some temporal/evolution relationships (PREVALENT_DURING, OBSOLETE_DUE_TO) need qualifiers
- INEFFECTIVE_AGAINST (negative relationships not well supported in Wikidata)

---

## Impact Assessment

### Relationships That Should Get Wikidata Properties: **9**

- Evolution: 4 (REPLACED_BY, SUPERSEDED_BY, INTRODUCED_IN, CEASED_USE_IN, OBSOLETE_AFTER)
- Production: 5 (MANUFACTURED_BY, MANUFACTURED_IN, TYPICALLY_MADE_OF, MADE_USING_TECHNIQUE)

### Coverage Improvement

- Current: 0/40 (0%)
- After mapping: 9/40 (22.5%)
- Remaining: 31/40 (77.5%) - these are genuinely more specific than Wikidata

---

## Recommendation

**Yes, we should add Wikidata properties where they align.** This enables:
1. **Federation** - Query across Wikidata and Chrystallum
2. **Interoperability** - Export/import aligned data
3. **Validation** - Cross-reference with Wikidata data
4. **Discovery** - Users can find related Wikidata items

**Implementation:** Follow the plan's approach - create a script similar to `add_cidoc_crm_alignment.py` but for Wikidata properties, starting with these 9 high-confidence mappings.


