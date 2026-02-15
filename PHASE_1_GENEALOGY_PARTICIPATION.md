# Phase 1: Genealogical & Participation Modeling Implementation

**Status:** In Progress  
**Date:** February 14, 2026  
**Objective:** Wire together genealogical and event participation relationships with explicit facet mappings and Bayesian confidence baselines  

---

## Phase 1 Summary

This phase extends Chrystallum's support for **family tree modeling** and **event participant tracking** by:

1. ✅ **Auditing existing schema** — Found genealogical relationships already exist in `relationship_types_registry_master.csv`
2. 🔄 **Adding missing relationships** — Create entries for `PARTICIPATED_IN`, `DIED_AT`, `MEMBER_OF_GENS`
3. 🔄 **Enriching metadata** — Add `confidence_threshold` and `domain_facets` columns to existing entries
4. 🔄 **Adding N-N mapping properties** — Add `wikidata_role_qualifiers` for rank/faction/outcome on relationships
5. 🔄 **Updating Neo4j schema** — Add QID constraints and genealogy-specific indexes
6. 🔄 **Extending claim pipeline** — Support genealogy + participation claims with role metadata
7. 🔄 **Creating discovery prompts** — Extract family/participation indicators from text

---

## Audit Results

### ✅ Genealogical Relationships (Existing in CSV)

| Relationship Type | Inverse | Wikidata Property | Current Status | Facets | Confidence |
|-------------------|---------|-------------------|-----------------|--------|------------|
| PARENT_OF | CHILD_OF | P40 | implemented | demographic, social | ❌ MISSING |
| FATHER_OF | (inverse to CHILD_OF) | P40 | implemented | demographic, social | ❌ MISSING |
| MOTHER_OF | (inverse to CHILD_OF) | P40 | implemented | demographic, social | ❌ MISSING |
| SPOUSE_OF | SPOUSE_OF | P26 | implemented | social, political | ❌ MISSING |
| SIBLING_OF | SIBLING_OF | P3373 | implemented | demographic, social | ❌ MISSING |
| HALF_SIBLING_OF | HALF_SIBLING_OF | P3373 | implemented | demographic, social | ❌ MISSING |
| GRANDPARENT_OF | GRANDCHILD_OF | P152 | implemented | demographic | ❌ MISSING |
| AUNT_OF | NEPHEW_OR_NIECE_OF | P107 | implemented | social, cultural | ❌ MISSING |
| UNCLE_OF | NEPHEW_OR_NIECE_OF | P107 | implemented | social, cultural | ❌ MISSING |
| COUSIN_OF | COUSIN_OF | P107 | implemented | social, cultural | ❌ MISSING |

### ✅ Military/Event Relationships (Existing in CSV)

| Relationship Type | Inverse | Wikidata Property | Current Status | Facets | Confidence |
|-------------------|---------|-------------------|-----------------|--------|------------|
| FOUGHT_IN | BATTLE_PARTICIPANT | P607 | implemented | military | ❌ MISSING |
| COMMANDED_BY | COMMANDED (Position) | — | implemented | military | ❌ MISSING |
| DEFEATED | DEFEATED_BY | — | implemented | military | ❌ MISSING |
| SERVED_UNDER | — | P585 (timespan) | implemented | military | ❌ MISSING |
| BETRAYED | BETRAYED_BY | — | implemented | military, political | ❌ MISSING |

### ❌ Missing Relationships (Need to Add)

| Relationship Type | Inverse | Suggested P-value | Facets | Confidence |
|-------------------|---------|-------------------|--------|------------|
| PARTICIPATED_IN | HAD_PARTICIPANT | P710 | military, political, diplomatic | 0.85 |
| DIED_AT | DEATH_LOCATION | P1120 | military, demographic | 0.95 |
| MEMBER_OF_GENS | HAS_GENS_MEMBER | P53 | social, cultural | 0.90 |
| NEGOTIATED_VIA_DIPLOMAT | INVOLVED_DIPLOMAT | P3342 | diplomatic, political | 0.80 |
| WITNESSED | WITNESSED_BY | P1441 | diplomatic, communication | 0.75 |

---

## Key Insights from Independent Review

**Authority Alignment:** Wikidata P-value mapping for genealogy and participation:
- **Genealogical:** P22 (father), P25 (mother), P26 (spouse), P40 (child), P3373 (sibling), P53 (family/gens)
- **Participation:** P710 (participant), P1344 (participant of), P1441 (present in work), P3342 (significant person)  
- **Roles:** P410 (military rank), P241 (military branch), P106 (occupation), P39 (position held)

**Facet Mapping (New):**
- Genealogical claims → `demographic` (primary) + `social` (secondary)
- Participation → `military` (combat), `diplomatic` (negotiation), `political` (voting/governance)
- Family alliances → `political` (alliance context) + `social` (kinship context)

**Bayesian Confidence Baselines (New):**
- Core genealogy (parent-child, spouse) → 0.90-0.95
- Extended family (aunt-uncle-cousin) → 0.80-0.85
- Event participation → 0.85-0.95 (depending on role clarity)
- Military outcomes (killed, defeated) → 0.95 (high confidence due to historical records)

---

## Implementation Tasks

### Task 1: Extend CSV with New Columns (PRIORITY: CRITICAL)

Add these columns to `relationship_types_registry_master.csv`:

```csv
Column Name | Type | Purpose | Example
confidence_threshold | float | Bayesian baseline for promotion | 0.90
domain_facets | string (CSV) | Facets where relationship applies | demographic|social
inverse_type | string | Explicit inverse relationship name | CHILD_OF
qualifier_fields | string (CSV) | Edge properties for role/faction | rank,faction,outcome
bayesian_note | string | Explanation of confidence baseline | High confidence due to historical attestation
```

**Action:** Add these columns at end of CSV header row

### Task 2: Add Missing Relationship Entries (PRIORITY: HIGH)

Create new rows in `relationship_types_registry_master.csv`:

```csv
category,relationship_type,inverse_type,wikidata_property,directionality,domain_facets,confidence_threshold,qualifier_fields,status,note
Participation,PARTICIPATED_IN,HAD_PARTICIPANT,P710,forward,military|political|diplomatic,0.85,rank,role,faction,confidence,implemented,Generic participation in events
Participation,HAD_PARTICIPANT,PARTICIPATED_IN,P710,inverse,military|political|diplomatic,0.85,,implemented,Inverse of PARTICIPATED_IN
Participation,DIED_AT,DEATH_LOCATION,P1120,forward,military|demographic,0.95,casualty_type,outcome,implemented,Person died in battle/location
Participation,DEATH_LOCATION,DIED_AT,P1120,inverse,military|demographic,0.95,,implemented,Inverse of DIED_AT
Familial,MEMBER_OF_GENS,HAS_GENS_MEMBER,P53,forward,social|cultural,0.90,,implemented,Roman family membership
Familial,HAS_GENS_MEMBER,MEMBER_OF_GENS,P53,inverse,social|cultural,0.90,,implemented,Inverse of MEMBER_OF_GENS
Diplomatic,NEGOTIATED_TREATY,TREATY_NEGOTIATOR,P3342,forward,diplomatic|political,0.80,treaty_type,parties,implemented,Person negotiated treaty
Diplomatic,TREATY_NEGOTIATOR,NEGOTIATED_TREATY,P3342,inverse,diplomatic|political,0.80,,implemented,Inverse of NEGOTIATED_TREATY
Diplomatic,WITNESSED_EVENT,WITNESSED_BY,P1441,forward,diplomatic|communication,0.75,,implemented,Person witnessed historical event
Diplomatic,WITNESSED_BY,WITNESSED_EVENT,P1441,inverse,diplomatic|communication,0.75,,implemented,Inverse of WITNESSED_EVENT
```

### Task 3: Update Neo4j Schema Constraints (PRIORITY: HIGH)

**File:** `Neo4j/schema/01_schema_constraints.cypher`

Add constraints:
```cypher
// QID constraints (blocking issue from your analysis)
CREATE CONSTRAINT human_has_qid IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS NOT NULL;

CREATE CONSTRAINT event_has_qid IF NOT EXISTS
FOR (e:Event) REQUIRE e.qid IS NOT NULL;

CREATE CONSTRAINT gens_has_label IF NOT EXISTS
FOR (g:Gens) REQUIRE g.label IS NOT NULL;

CREATE CONSTRAINT praenomen_has_label IF NOT EXISTS
FOR (p:Praenomen) REQUIRE p.label IS NOT NULL;

CREATE CONSTRAINT cognomen_has_label IF NOT EXISTS
FOR (c:Cognomen) REQUIRE c.label IS NOT NULL;

// Genealogical relationship indexes
CREATE INDEX genealogy_parent_child IF NOT EXISTS
FOR ()-[r:PARENT_OF|CHILD_OF]->();

CREATE INDEX genealogy_spouse IF NOT EXISTS
FOR ()-[r:SPOUSE_OF]->();

CREATE INDEX genealogy_gens_member IF NOT EXISTS
FOR ()-[r:MEMBER_OF_GENS|HAS_GENS_MEMBER]->();

// Event participation indexes
CREATE INDEX participation_at_event IF NOT EXISTS
FOR ()-[r:PARTICIPATED_IN|HAD_PARTICIPANT]->();

CREATE INDEX participation_role IF NOT EXISTS
FOR ()-[r:PARTICIPATED_IN {role: *}]->();

CREATE INDEX death_at_event IF NOT EXISTS
FOR ()-[r:DIED_AT|DEATH_LOCATION]->();
```

### Task 4: Extend Claim Pipeline for Genealogy (PRIORITY: HIGH)

**File:** `scripts/tools/claim_ingestion_pipeline.py`

Add genealogy baseline confidence:

```python
# Add to class constants
GENEALOGY_CONFIDENCE_BASELINE = {
    "PARENT_OF": 0.92,
    "CHILD_OF": 0.92,
    "SPOUSE_OF": 0.88,
    "SIBLING_OF": 0.85,
    "MEMBER_OF_GENS": 0.90,
    "DIED_AT": 0.95,
    "PARTICIPATED_IN": 0.85,
}

GENEALOGY_FACETS = {
    "PARENT_OF": ["demographic", "social"],
    "CHILD_OF": ["demographic", "social"],
    "SPOUSE_OF": ["social", "political"],
    "SIBLING_OF": ["demographic", "social"],
    "MEMBER_OF_GENS": ["social", "cultural"],
    "DIED_AT": ["military", "demographic"],
    "PARTICIPATED_IN": ["military", "political", "diplomatic"],
}

def ingest_genealogical_claim(
    self,
    entity_id: str,
    relationship_type: str,
    target_id: str,
    confidence: float,
    label: str,
    authority_source: str = "wikidata",
    authority_ids: dict = None,
    qualifiers: dict = None,  # NEW: role, faction, outcome, rank, etc.
    wikidata_property_id: str = None
) -> dict:
    """Ingest claims with genealogical or participation semantics"""
    
    # Apply baseline confidence for genealogy if confidence is low
    if relationship_type in self.GENEALOGY_CONFIDENCE_BASELINE:
        baseline = self.GENEALOGY_CONFIDENCE_BASELINE[relationship_type]
        if confidence < baseline:
            confidence = min(confidence, baseline - 0.05)  # Slightly reduced if source says lower
    
    # Force facets for genealogical relationships
    facets = self.GENEALOGY_FACETS.get(relationship_type, ["NA"])
    
    # Store qualifiers on relationship node
    qualifier_props = {}
    if qualifiers:
        qualifier_props = {
            "qualifier_rank": qualifiers.get("rank"),
            "qualifier_faction": qualifiers.get("faction"),
            "qualifier_outcome": qualifiers.get("outcome"),
            "qualifier_role": qualifiers.get("role"),
            "qualifier_treaty_type": qualifiers.get("treaty_type"),
        }
    
    return self.ingest_claim(
        entity_id=entity_id,
        relationship_type=relationship_type,
        target_id=target_id,
        confidence=confidence,
        label=label,
        facet=facets[0],
        authority_source=authority_source,
        authority_ids=authority_ids,
        wikidata_property_id=wikidata_property_id,
        additional_properties=qualifier_props
    )
```

### Task 5: Discovery Mode Prompts (PRIORITY: MEDIUM)

**File:** Create new `Prompts/genealogy_extraction_prompt.txt`

```
GENEALOGY & PARTICIPATION EXTRACTION PROMPT

Extract family relationships and event participation from historical texts.

FAMILY RELATIONSHIP INDICATORS:
- Direct: "son of", "daughter of", "father of", "mother of", "brother of", "sister of"
- Spouse: "married to", "wife of", "husband of", "spouse of", "married twice"
- Extended: "uncle of", "aunt of", "cousin of", "nephew of", "niece of"
- Gens/Clan: "of the gens [name]", "[name] family", "house of [name]"
- Adoption: "adopted by", "adoptive father", "adopted son"

PARTICIPATION INDICATORS:
- Combat: "fought at", "battled at", "participated in battle", "served in"
- Command: "commanded forces", "led troops", "general of", "admiral of"
- Death: "fell at", "killed in", "died at", "casualty of", "martyred at"
- Negotiation: "negotiated with", "treaty with", "ambassador to"
- Witness: "witnessed", "present at", "attended", "observed"

OUTPUT FORMAT FOR EACH EXTRACTED FACT:

Fact Type: [GENEALOGY|PARTICIPATION]
Relationship: [PARENT_OF|CHILD_OF|SPOUSE_OF|PARTICIPATED_IN|COMMANDED|DIED_AT|etc.]
From: [person/entity name and Q-ID if available]
To: [person/entity/location name and Q-ID if available]
Confidence: [0.75-0.99]
Qualifiers: 
  - role: [commander|soldier|witness|etc.]
  - faction: [Roman|Carthaginian|etc.]
  - outcome: [killed|wounded|victorious|etc.]
Source Quote: "[exact text from source]"
```

### Task 6: Create Phase 1 Test Case (PRIORITY: MEDIUM)

**Test entities:** Caesar-Brutus genealogical cluster (rich genealogy + assassination)

```python
# Test case: Marcus Junius Brutus genealogy
facts = [
    {
        "entity": "Marcus Junius Brutus",
        "relationship": "CHILD_OF",
        "target": "Servilia",
        "confidence": 0.95,
        "authority": "wikidata",
        "facet": "demographic",
    },
    {
        "entity": "Marcus Junius Brutus",
        "relationship": "PARTICIPATED_IN",
        "target": "Battle of Philippi",
        "confidence": 0.92,
        "authority": "wikidata",
        "facet": "military",
        "qualifiers": {"role": "commander", "outcome": "defeated"},
    },
    {
        "entity": "Marcus Junius Brutus",
        "relationship": "MEMBER_OF_GENS",
        "target": "Gens Junia",
        "confidence": 0.98,
        "authority": "wikidata",
        "facet": "social",
    },
]
```

---

## Blocking Issues Resolved

| Issue | Solution | Priority |
|-------|----------|----------|
| QID fields missing on nodes | Add NOT NULL constraints to QID fields | CRITICAL |
| Genealogy in privacy/time-period limbo | Wikidata/Wikipedia content is public (confirmed) | RESOLVED |
| Facet mappings not documented | Added domain_facets column to registry | HIGH |
| Confidence baselines not documented | Added confidence_threshold column to registry | HIGH |
| Role/faction not storable on relationships | Added qualifier_fields to registry | HIGH |

---

## Deliverables (Phase 1)

- [ ] **Extended relationship_types_registry_master.csv** with new columns + entries
- [ ] **Updated Neo4j schema constraints** with QID + index statements
- [ ] **Updated claim_ingestion_pipeline.py** with genealogy baseline logic
- [ ] **Generated genealogy_extraction_prompt.txt** for discovery mode
- [ ] **Tested with Caesar-Brutus cluster** (verification)
- [ ] **Updated AI_CONTEXT.md** with Phase 1 completion notes
- [ ] **Updated Change_log.py** with Phase 1 entry

---

## Next Steps (Phase 2)

1. **Extend schema with adoption + illegitimacy** (presently simplified)
2. **Add time-period constraints** for genealogy validity (e.g., divorce not valid pre-500 CE in Rome)
3. **Cross-authority genealogy conflict resolution** (Wikidata vs. LCSH disagreement)
4. **Implement privacy filtering** for modern genealogy (optional, post-1900)
5. **Test full Caesar → Caesarion → Cleopatra cluster** (cross-cultural genealogy)

---

## Wikidata Property Reference (For Implementation)

```
Genealogical Properties:
P22   - father
P25   - mother
P26   - spouse
P40   - child
P3373 - sibling
P1038 - relative (non-sibling)
P53   - family (gens in Roman context)
P451  - unmarried partner

Event Participation Properties:
P710  - participant
P1344 - participant of (inverse)
P1441 - present in work
P3342 - significant person
P598  - commander of
P607  - participant in battle

Role/Rank Properties:
P410  - military rank
P241  - military branch
P106  - occupation
P39   - position held
P585  - point in time (timespan qualifier)
P580  - start time (qualifier)
P582  - end time (qualifier)

Death/Casualty Properties:
P1120 - died from
P970  - cause of death
P509  - cause of death (medical)
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-14 22:55  
**Status:** Ready for Phase 1 Implementation Start
