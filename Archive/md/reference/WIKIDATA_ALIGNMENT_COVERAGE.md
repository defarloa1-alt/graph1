# Wikidata Alignment Coverage Analysis

**Date:** 2025-12-12  
**Purpose:** Document current Wikidata QID and property alignment coverage in Chrystallum schema  
**Analysis Script:** `scripts/utils/analyze_wikidata_coverage.py`

---

## Executive Summary

The Chrystallum Knowledge Graph schema has **strong entity alignment** with Wikidata (97.6% coverage) but **moderate relationship alignment** (18.1% coverage). Overall Wikidata alignment is **57.8%**.

### Key Findings

- ✅ **124 entities** defined, **121 have Wikidata QIDs** (97.6% coverage)
- ⚠️ **282 relationships** defined, **51 have Wikidata P-properties** (18.1% coverage)
- 📊 **27 unique Wikidata properties** currently mapped
- 🎯 **3 entities** missing QIDs (all in Reasoning category - CRMinf extensions)

---

## Entity Coverage (Wikidata QIDs)

### Overall Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Entities | 124 | 100% |
| Entities with QID | 121 | **97.6%** |
| Entities without QID | 3 | 2.4% |

### Coverage by Category

| Category | With QID | Total | Coverage |
|----------|----------|-------|----------|
| Agreement | 7 | 7 | 100.0% |
| Concept | 8 | 8 | 100.0% |
| Event | 16 | 16 | 100.0% |
| Infrastructure | 14 | 14 | 100.0% |
| Material | 8 | 8 | 100.0% |
| Organization | 15 | 15 | 100.0% |
| Person | 2 | 2 | 100.0% |
| Place | 14 | 14 | 100.0% |
| Position | 14 | 14 | 100.0% |
| **Reasoning** | **0** | **3** | **0.0%** |
| Religious | 15 | 15 | 100.0% |
| Work | 8 | 8 | 100.0% |

### Missing Wikidata QIDs

The following entities are missing Wikidata QIDs (all from CRMinf reasoning extensions):

1. **Reasoning/Belief** - "Belief or assumption about a fact"
   - CIDOC-CRM: `crminf:E2_Belief`
   - **Note:** This is a CRMinf extension concept. May need to create Wikidata item or use alternative mapping.

2. **Reasoning/InferenceMaking** - "Process of making an inference"
   - CIDOC-CRM: `crminf:E5_Inference_Making`
   - **Note:** CRMinf extension. Consider mapping to Q11028 (inference) or creating new item.

3. **Reasoning/BeliefRevision** - "Change or update to a belief"
   - CIDOC-CRM: `crminf:E13_Belief_Revision`
   - **Note:** CRMinf extension. May map to Q11028 (inference) or Q177639 (ethics) depending on context.

### Recommendations for Missing Entity QIDs

1. **Research CRMinf concepts in Wikidata** - Check if equivalent concepts exist
2. **Consider broader mappings** - Map to parent concepts (e.g., Q11028 for inference)
3. **Document rationale** - If no Wikidata equivalent exists, document why and consider creating items

---

## Relationship Coverage (Wikidata Properties)

### Overall Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Relationships | 282 | 100% |
| Relationships with P-property | 51 | **18.1%** |
| Relationships without P-property | 231 | 81.9% |

### Coverage by Category

| Category | With Property | Total | Coverage | Priority |
|----------|---------------|-------|----------|----------|
| **Authorship** | 10 | 12 | **83.3%** | ✅ High |
| **Ideological** | 2 | 2 | **100.0%** | ✅ Complete |
| **Linguistic** | 2 | 2 | **100.0%** | ✅ Complete |
| Application | 4 | 10 | 40.0% | ⚠️ Medium |
| Attribution | 3 | 11 | 27.3% | ⚠️ Medium |
| Causality | 3 | 8 | 37.5% | ⚠️ Medium |
| Geographic | 7 | 18 | 38.9% | ⚠️ Medium |
| Religious | 2 | 6 | 33.3% | ⚠️ Medium |
| Temporal | 2 | 6 | 33.3% | ⚠️ Medium |
| Honorific | 2 | 8 | 25.0% | ⚠️ Medium |
| Institutional | 2 | 9 | 22.2% | ⚠️ Medium |
| Political | 7 | 39 | 17.9% | ⚠️ Medium |
| Economic | 2 | 16 | 12.5% | 🔴 Low |
| Legal | 1 | 13 | 7.7% | 🔴 Low |
| **Comparative** | 0 | 5 | **0.0%** | 🔴 High Priority |
| **Cultural** | 0 | 8 | **0.0%** | 🔴 High Priority |
| **Diplomatic** | 0 | 12 | **0.0%** | 🔴 High Priority |
| **Evolution** | 0 | 10 | **0.0%** | 🔴 High Priority |
| **Familial** | 0 | 13 | **0.0%** | 🔴 High Priority |
| **Functional** | 0 | 4 | **0.0%** | 🔴 High Priority |
| **Military** | 0 | 23 | **0.0%** | 🔴 High Priority |
| **Production** | 0 | 6 | **0.0%** | 🔴 High Priority |
| **Social** | 0 | 6 | **0.0%** | 🔴 High Priority |
| **Trade** | 0 | 3 | **0.0%** | 🔴 High Priority |
| **Typological** | 0 | 3 | **0.0%** | 🔴 High Priority |
| Category | 0 | 1 | 0.0% | - |
| Measurement | 0 | 2 | 0.0% | - |
| Membership | 0 | 2 | 0.0% | - |
| Moral | 0 | 3 | 0.0% | - |
| Position | 2 | 8 | 25.0% | - |
| Reasoning | 0 | 6 | 0.0% | - |
| Relations | 0 | 7 | 0.0% | - |

### Currently Mapped Wikidata Properties

**27 unique properties** are currently mapped:

- **P1001** - Applies to jurisdiction
- **P1056** - Product or material produced
- **P112** - Founded by
- **P1142** - Political ideology
- **P138** - Named after
- **P1399** - Convicted of
- **P140** - Religion
- **P1412** - Languages spoken, written or signed
- **P1448** - Official name
- **P166** - Award received
- **P17** - Country
- **P170** - Creator
- **P186** - Material used
- **P19** - Place of birth
- **P20** - Place of death
- **P2561** - Name
- **P361** - Part of
- **P366** - Use
- **P39** - Position held
- **P50** - Author
- **P61** - Discoverer or inventor
- **P710** - Participant
- **P828** - Has cause
- **P84** - Architect
- **P86** - Composer
- **P131** - Located in administrative territorial entity
- **P1441** - Present in work

### High-Priority Categories for Property Mapping

These categories have **0% coverage** and represent significant gaps:

1. **Military (0/23)** - Critical for historical analysis
   - Examples: COMMANDED, LED_CAMPAIGN, DEFEATED, VICTOR_IN
   - Potential mappings: P607 (conflict), P710 (participant), P361 (part of)

2. **Familial (0/13)** - Important for biographical data
   - Examples: CHILD_OF, PARENT_OF, SPOUSE_OF, SIBLING_OF
   - Potential mappings: P40 (child), P22 (father), P25 (mother), P26 (spouse)

3. **Diplomatic (0/12)** - Key for political history
   - Examples: NEGOTIATED_WITH, SENT_ENVOYS_TO, RECEIVED_ENVOYS_FROM
   - Potential mappings: P710 (participant), P361 (part of)

4. **Cultural (0/8)** - Important for cultural analysis
   - Examples: EVOLVED_FROM, EVOLVED_INTO, CLAIMS_HERITAGE_FROM
   - Potential mappings: P361 (part of), P460 (said to be the same as)

5. **Evolution (0/10)** - Temporal change relationships
   - Examples: PREVALENT_DURING, INTRODUCED_IN, CEASED_USE_IN
   - Potential mappings: P580 (start time), P582 (end time), P361 (part of)

6. **Production (0/6)** - Manufacturing and creation
   - Examples: MANUFACTURED_IN, MANUFACTURED_BY, MADE_USING_TECHNIQUE
   - Potential mappings: P1056 (product), P170 (creator), P186 (material)

7. **Social (0/6)** - Social relationships
   - Examples: WEARS, WORN_BY, ASSOCIATED_WITH
   - Potential mappings: P186 (material), P366 (use)

---

## Alignment Strategy

### Current Approach

1. **Entity QIDs** - Direct mapping to Wikidata item types (Q-IDs)
2. **Relationship Properties** - Mapping to Wikidata properties (P-IDs) where semantically equivalent
3. **CIDOC-CRM Alignment** - Also maintained alongside Wikidata (see `Docs/architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`)

### Recommended Improvements

#### Phase 1: Complete High-Priority Categories (Target: +50 relationships)

1. **Familial Relationships** (13 relationships)
   - Map to P40, P22, P25, P26, P1038 (relative)
   - **Estimated effort:** 2-3 hours

2. **Military Relationships** (23 relationships)
   - Map to P607, P710, P361, P580, P582
   - **Estimated effort:** 4-6 hours

3. **Diplomatic Relationships** (12 relationships)
   - Map to P710, P361, P580
   - **Estimated effort:** 2-3 hours

**Total:** 48 relationships → **Target coverage: 35.1%**

#### Phase 2: Medium-Priority Categories (Target: +30 relationships)

1. **Cultural Relationships** (8 relationships)
2. **Evolution Relationships** (10 relationships)
3. **Production Relationships** (6 relationships)
4. **Social Relationships** (6 relationships)

**Total:** 30 relationships → **Target coverage: 45.7%**

#### Phase 3: Complete Remaining Categories (Target: +153 relationships)

- Remaining categories with partial or no coverage
- **Target coverage: 100%**

---

## Wikidata Property Reference

### Commonly Used Properties

| Property | Label | Used For |
|----------|-------|----------|
| P19 | Place of birth | Geographic relationships |
| P20 | Place of death | Geographic relationships |
| P39 | Position held | Position relationships |
| P50 | Author | Authorship relationships |
| P84 | Architect | Authorship relationships |
| P86 | Composer | Authorship relationships |
| P170 | Creator | Authorship relationships |
| P186 | Material used | Application relationships |
| P366 | Use | Application relationships |
| P710 | Participant | Event participation |
| P828 | Has cause | Causality relationships |

### Properties to Research for Missing Mappings

- **P22** - Father
- **P25** - Mother
- **P26** - Spouse
- **P40** - Child
- **P1038** - Relative
- **P607** - Conflict
- **P580** - Start time
- **P582** - End time
- **P361** - Part of
- **P460** - Said to be the same as

---

## Implementation Notes

### Current Implementation

- Entity QIDs stored in `data/schemas/chrystallum_schema.json` as `wikidata_qid`
- Relationship properties stored in `relations/canonical_relationship_types.csv` as `wikidata_property`
- Action structure mappings in `Reference/action_structure_wikidata_mapping.csv`

### Schema Files

1. **Entity Schema:** `data/schemas/chrystallum_schema.json`
   - 124 entity types with QID mappings
   - Source: `Reference/neo4j_entities_deduplicated.csv`

2. **Relationship Schema:** `relations/canonical_relationship_types.csv`
   - 282 relationship types
   - 51 with Wikidata property mappings

3. **Action Structure:** `Reference/action_structure_wikidata_mapping.csv`
   - Goal/Trigger/Action/Result type mappings

### Validation

Run coverage analysis:
```bash
python scripts/utils/analyze_wikidata_coverage.py
```

---

## Next Steps

### Immediate Actions

1. ✅ **Document current coverage** (this document)
2. ⏳ **Research missing QIDs** for Reasoning entities
3. ⏳ **Map Familial relationships** (highest priority, most straightforward)
4. ⏳ **Map Military relationships** (critical for historical analysis)

### Short-Term Goals (1-2 weeks)

1. Complete Phase 1 mappings (+50 relationships)
2. Update `canonical_relationship_types.csv` with new properties
3. Regenerate consolidated schema JSON
4. Update documentation

### Long-Term Goals (1-2 months)

1. Complete Phase 2 and Phase 3 mappings
2. Achieve 100% Wikidata alignment
3. Create validation scripts to ensure alignment quality
4. Document mapping rationale for each relationship

---

## References

- **Wikidata Property Documentation:** https://www.wikidata.org/wiki/Wikidata:List_of_properties
- **CIDOC-CRM Alignment:** `Docs/architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`
- **Action Structure Mapping:** `Reference/action_structure_wikidata_mapping.csv`
- **Schema Consolidation Script:** `scripts/schema/consolidate_schema.py`

---

**Last Updated:** 2025-12-12  
**Analysis Version:** 1.0  
**Next Review:** After Phase 1 completion


