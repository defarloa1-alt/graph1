# Relationship Types Sample

**Purpose:** Representative sample from full registry (312 types)  
**Source:** `Relationships/relationship_types_registry_master.csv`  
**Date:** February 14, 2026

---

## CSV Format

```
category | relationship_type | description | wikidata_property | directionality | 
parent_relationship | specificity_level | lcc_code | lcsh_heading | fast_id | 
status | note | source | version | lifecycle_status | reify_as | cidoc_crm_code | 
cidoc_crm_kind | wikidata_label | crminf_applicable | mapping_source | 
wikidata_description | wikidata_datatype | wikidata_alt_labels | 
wikidata_role_qualifier_object_pid | wikidata_role_qualifier_subject_pid
```

---

## Genealogical Relationships (24 total)

### Core Family

**PARENT_OF** / **CHILD_OF**
- Category: Familial
- Wikidata: P40 (child)
- Directionality: inverse pair
- Description: Biological parent-child relationship
- CIDOC-CRM: P152_has_parent / P152i_is_parent_of
- Confidence Baselines:
  - demographic: 0.92
  - social: 0.85
  - political: 0.75
- Status: implemented
- Note: Do not use for stepchildren—use RELATIVE (P1038) with kinship qualifier

**FATHER_OF** / **MOTHER_OF**
- Category: Familial
- Wikidata: P22 (father), P25 (mother)
- Specificity: 2 (more specific than PARENT_OF)
- Confidence Baselines:
  - demographic: 0.92
  - social: 0.88
- Status: implemented

**SPOUSE_OF**
- Category: Familial
- Wikidata: P26 (spouse)
- Directionality: symmetric
- Confidence Baselines:
  - social: 0.90
  - political: 0.92 (alliances)
  - demographic: 0.88
  - economic: 0.85 (dowry/inheritance)
- Status: implemented
- Alt Labels: husband, wife, married to

**SIBLING_OF**
- Category: Familial
- Wikidata: P3373 (sibling)
- Directionality: symmetric
- Confidence Baselines:
  - demographic: 0.85
  - social: 0.88
  - political: 0.75
- Status: implemented
- Alt Labels: brother, sister

**HALF_SIBLING_OF**
- Category: Familial
- Wikidata: P3373 (qualified)
- Confidence Baselines:
  - demographic: 0.80
  - social: 0.82
- Status: implemented
- Note: Lower confidence due to potential record ambiguity

### Extended Family

**GRANDPARENT_OF** / **GRANDCHILD_OF**
- Category: Familial
- Parent Relationship: FAMILIAL_RELATION
- Specificity: 3
- Confidence Baselines:
  - demographic: 0.88
  - social: 0.80
- CIDOC-CRM: P152_has_parent_chain
- Status: implemented
- Note: Derived from parent relations

**AUNT_OF** / **UNCLE_OF**
- Category: Familial
- Confidence Baselines:
  - demographic: 0.75
  - social: 0.78
- Status: implemented

**COUSIN_OF**
- Category: Familial
- Confidence Baselines:
  - demographic: 0.70
  - social: 0.75
- Status: implemented
- Note: Often ambiguous in historical records

**ANCESTOR_OF** / **DESCENDANT_OF**
- Category: Familial
- Wikidata: P1038 (relative)
- Confidence Baselines:
  - demographic: 0.75
  - social: 0.70
  - cultural: 0.65 (includes mythical ancestors)
- Status: implemented

### Legal & Social Family

**ADOPTED_BY** / **ADOPTS**
- Category: Familial
- Confidence Baselines:
  - social: 0.85
  - political: 0.88 (testamentary adoption)
  - demographic: 0.80
- Status: implemented
- Note: Political facet higher for Roman testamentary adoption (e.g., Octavian → Augustus)

**GUARDIAN_OF** / **WARD_OF**
- Category: Familial
- Confidence Baselines:
  - social: 0.82
  - economic: 0.80 (property management)
- Status: implemented

**STEPPARENT_OF** / **STEPCHILD_OF**
- Category: Familial
- CIDOC-CRM: P107_has_member (family)
- Status: implemented
- Note: Legal/social fact

### Roman-Specific

**MEMBER_OF_GENS** / **HAS_GENS_MEMBER**
- Category: Familial
- Wikidata: P53 (family)
- Confidence Baselines:
  - social: 0.90
  - political: 0.85
  - cultural: 0.88
  - demographic: 0.85
- Status: implemented
- Source: phase1_genealogy
- Note: Roman gens affiliation; well-documented in Republic era
- Alt Labels: house, clan, family name, gens, familia, dynasty (non-royal)

---

## Participation Relationships (10 total)

### Generic Participation

**PARTICIPATED_IN** / **HAD_PARTICIPANT**
- Category: Participation
- Wikidata: P710 (participant)
- Directionality: forward / inverse
- Confidence Baselines:
  - military: 0.85
  - political: 0.85
  - diplomatic: 0.88
  - social: 0.80
  - religious: 0.82
  - cultural: 0.80
- CIDOC-CRM: P11_had_participant / P11i_participated_in
- CRMinf: applicable
- Status: implemented
- Source: phase1_genealogy
- Role Qualifier: P3831 (object role)
- Note: Generic participation; context-dependent; role qualifier increases confidence

### Military Participation

**COMMANDED** / **COMMANDED_BY**
- Category: Military
- Confidence Baselines:
  - military: 0.90
  - political: 0.88
- Status: implemented
- Note: Military command well-documented

**FOUGHT_IN** / **FOUGHT_AT**
- Category: Military
- Wikidata: P607 (conflict)
- Confidence Baselines:
  - military: 0.85
  - demographic: 0.82
- Status: implemented

**SERVED_UNDER**
- Category: Military
- Confidence Baselines:
  - military: 0.88
  - social: 0.82
- Status: implemented

### Vital Events

**DIED_AT** / **DEATH_LOCATION**
- Category: Vital
- Wikidata: P1120 (place of death)
- Specificity: 2
- Confidence Baselines:
  - demographic: 0.95
  - military: 0.98 (combat deaths)
  - social: 0.90
- CIDOC-CRM: P100_was_death_of / P100i_died_in
- CRMinf: applicable
- Status: implemented
- Source: phase1_genealogy
- Note: Death events well-documented; military facet for combat deaths
- Alt Labels: death place, died in, place of death, death location, died at, place where died

**BORN_AT** / **BIRTH_LOCATION**
- Category: Vital
- Wikidata: P19 (place of birth)
- Confidence Baselines:
  - demographic: 0.90
  - social: 0.85
- Status: implemented

### Diplomatic Participation

**NEGOTIATED_TREATY** / **TREATY_NEGOTIATOR**
- Category: Diplomatic
- Wikidata: P3342 (significant person)
- Specificity: 2
- Confidence Baselines:
  - diplomatic: 0.88
  - political: 0.85
  - communication: 0.82
- CIDOC-CRM: P14_carried_out_by / P14i_performed
- CRMinf: applicable
- Status: implemented
- Source: phase1_genealogy
- Role Qualifier: P3831
- Note: Treaty negotiation role; communication for messaging/ceremony
- Alt Labels: negotiator, diplomat, peace broker, mediator

**WITNESSED_EVENT** / **WITNESSED_BY**
- Category: Observation
- Wikidata: P1441 (present in work)
- Confidence Baselines:
  - communication: 0.80
  - political: 0.78
  - social: 0.75
- CIDOC-CRM: P12_occurred_in_the_presence_of / P12i_was_present_at
- CRMinf: applicable
- Status: implemented
- Source: phase1_genealogy
- Note: Observer role; lower confidence due to indirect evidence
- Alt Labels: appears in, featured in, depicted in, present at, witnessed

---

## Political Relationships (15 total)

### Office Holding

**HELD_OFFICE**
- Category: Political
- Wikidata: P39 (position held)
- Confidence Baselines:
  - political: 0.95
  - social: 0.90
- Status: implemented
- Note: Political offices well-documented (consul, praetor, tribune, dictator, etc.)

**ELECTED_TO**
- Category: Political
- Wikidata: P39 (qualified with election method)
- Confidence Baselines:
  - political: 0.92
  - social: 0.88
- Status: implemented
- Note: Electoral victories documented in fasti

**APPOINTED_TO**
- Category: Political
- Wikidata: P39 (qualified with appointment)
- Confidence Baselines:
  - political: 0.90
  - social: 0.85
- Status: implemented
- Note: Appointments (dictator, proconsul)

**GOVERNED** / **GOVERNED_BY**
- Category: Political
- Confidence Baselines:
  - political: 0.92
  - geographic: 0.90
  - military: 0.85
- Status: implemented
- Note: Provincial governorships well-recorded

### Interstate Relations

**ALLIED_WITH**
- Category: Diplomatic
- Directionality: symmetric
- Confidence Baselines:
  - diplomatic: 0.90
  - political: 0.92
  - military: 0.88
- Status: implemented
- Note: Alliances documented in treaties

**TREATY_WITH**
- Category: Diplomatic
- Directionality: symmetric
- Confidence Baselines:
  - diplomatic: 0.95
  - political: 0.92
- Status: implemented
- Note: Formal treaties well-preserved

**AT_WAR_WITH**
- Category: Military
- Directionality: symmetric
- Confidence Baselines:
  - military: 0.92
  - diplomatic: 0.90
  - political: 0.88
- Status: implemented
- Note: Wars extensively documented

---

## Military Relationships (12 total)

**CONQUERED** / **CONQUERED_BY**
- Category: Military
- Confidence Baselines:
  - military: 0.92
  - political: 0.90
  - geographic: 0.88
- Status: implemented

**DEFEATED** / **DEFEATED_BY**
- Category: Military
- Confidence Baselines:
  - military: 0.90
  - political: 0.88
- Status: implemented
- Note: Military defeats recorded by victors

**BESIEGED** / **BESIEGED_BY**
- Category: Military
- Confidence Baselines:
  - military: 0.88
  - political: 0.85
- Status: implemented

---

## Social Relationships (8 total)

**PATRON_OF** / **CLIENT_OF**
- Category: Social
- Wikidata: P1830 (owner of)
- Confidence Baselines:
  - social: 0.85
  - economic: 0.82
  - political: 0.80
- Status: implemented
- Note: Patronage networks; economic for support

**ENSLAVED_BY** / **ENSLAVED**
- Category: Social
- Confidence Baselines:
  - social: 0.88
  - economic: 0.85 (property aspect)
  - demographic: 0.82
- Status: implemented

**FREED_BY** / **FREED**
- Category: Social
- Confidence Baselines:
  - social: 0.90
  - economic: 0.85
  - demographic: 0.88
- Status: implemented
- Note: Manumission; well-documented legal act

---

## Intellectual Relationships (6 total)

**TAUGHT** / **STUDIED_UNDER**
- Category: Intellectual
- Confidence Baselines:
  - intellectual: 0.88
  - social: 0.85
  - communication: 0.82
- Status: implemented

**WROTE** / **WRITTEN_BY**
- Category: Intellectual
- Wikidata: P50 (author)
- Confidence Baselines:
  - intellectual: 0.92
  - communication: 0.90
  - artistic: 0.85
- Status: implemented
- Note: Authorship well-documented

---

## Religious Relationships (5 total)

**PRIEST_OF**
- Category: Religious
- Wikidata: P39 (position held - priesthood)
- Confidence Baselines:
  - religious: 0.92
  - political: 0.88
  - social: 0.85
- Status: implemented
- Note: Priesthoods recorded in fasti

**WORSHIPPED_AT** / **CULT_CENTER_FOR**
- Category: Religious
- Confidence Baselines:
  - religious: 0.85
  - social: 0.80
  - cultural: 0.82
- Status: implemented

**DEDICATED_TO** / **DEDICATED_BY**
- Category: Religious
- Confidence Baselines:
  - religious: 0.88
  - artistic: 0.85
  - cultural: 0.82
- Status: implemented
- Note: Temple/monument dedications

---

## Economic Relationships (7 total)

**TRADED_WITH**
- Category: Economic
- Confidence Baselines:
  - economic: 0.82
  - diplomatic: 0.80
  - social: 0.75
- Status: implemented
- Note: Trade relationships; less directly documented

**OWNED** / **OWNED_BY**
- Category: Economic
- Confidence Baselines:
  - economic: 0.85
  - social: 0.82
  - political: 0.80
- Status: implemented

**INHERITED_FROM** / **BEQUEATHED_TO**
- Category: Economic
- Confidence Baselines:
  - economic: 0.88
  - social: 0.85
  - demographic: 0.82
- Status: implemented
- Note: Inheritance; testamentary evidence

---

## Temporal Relationships (8 total)

**OCCURRED_DURING** / **DURING**
- Category: Temporal
- Description: Event temporal location within period
- Status: implemented

**STARTS_IN_YEAR** / **ENDS_IN_YEAR**
- Category: Temporal
- Description: Event temporal anchoring to specific years
- LCC: QB (Astronomy, Time)
- FAST: 1151043
- Status: implemented

**PART_OF** / **HAS_PART**
- Category: Temporal
- Description: Hierarchical temporal organization
- Status: implemented

**BEFORE** / **AFTER**
- Category: Temporal
- Description: Relative temporal ordering
- Status: implemented

---

## Classification Relationships (5 total)

**CLASSIFIED_BY** / **CLASSIFIES**
- Category: Classification
- Description: Entity to subject concept linkage
- Status: implemented

**SUBJECT_OF** / **HAS_SUBJECT**
- Category: Classification
- Description: Thematic classification
- Status: implemented

**SUPPORTED_BY** / **SUPPORTS**
- Category: Evidence
- Description: Claim evidence linking
- Status: implemented

---

## Total Registry Statistics

- **Total Relationship Types:** 312 rows
- **Categories:** 25+ distinct categories
- **Implemented:** 280+ (90%)
- **Candidate:** 30+ (10%)
- **With Wikidata P-values:** 180+ (58%)
- **With CIDOC-CRM Codes:** 150+ (48%)
- **CRMinf Applicable:** 120+ (39%)

---

## Notes on Usage

1. **Directionality Matters:** Always check if relationship is forward, inverse, or symmetric
2. **Facet Context:** Use `relationship_facet_baselines.json` for per-facet confidence
3. **Role Qualifiers:** Many relationships support edge properties from `role_qualifier_reference.json`
4. **Wikidata Alignment:** P-values enable federation with Wikidata ecosystem
5. **CIDOC-CRM Grounding:** CRM codes enable semantic interoperability with museum/archive RDF
6. **Confidence Baselines:** Adjust based on facet + relationship combination

---

**For Full Registry:** See `Relationships/relationship_types_registry_master.csv` (312 rows)  
**For Role Qualifiers:** See `Relationships/role_qualifier_reference.json` (70+ roles)  
**For Facet Baselines:** See `Relationships/relationship_facet_baselines.json` (50+ relationships)
