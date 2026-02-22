# Canonical Reference: Identifiers, Relationships, and Federations

**Created:** February 22, 2026  
**Updated:** February 21, 2026 (Sections 3–8 completed from registry + audit)  
**Status:** CANONICAL REFERENCE — Single Source of Truth  
**Revision:** 1.1  
**Purpose:** Consolidate all identity systems, relationship types, federation mappings, and CIDOC-CRM alignment

---

## Document Purpose

**This document is the SINGLE SOURCE OF TRUTH for:**
1. All identifier systems (internal ciphers + external IDs)
2. All relationship types (canonical taxonomy)
3. All federation sources and crosswalk mappings
4. CIDOC-CRM and CRMinf alignment
5. Label systems and naming conventions

**Previously scattered across:**
- ENTITY_CIPHER_FOR_VERTEX_JUMPS.md (ciphers)
- CLAIM_ID_ARCHITECTURE.md (claim ciphers)
- ARCHITECTURE_CORE.md (relationship types, CIDOC-CRM)
- META_MODEL_SELF_DESCRIBING_GRAPH.md (federations)
- Various architecture appendices

**Now consolidated here.**

---

## Table of Contents

1. [Identity Architecture](#identity-architecture)
2. [Label System](#label-system)
3. [Relationship Master Types](#relationship-master-types)
4. [Federation Registry](#federation-registry)
5. [CIDOC-CRM Alignment](#cidoc-crm-alignment)
6. [CRMinf Integration](#crminf-integration)
7. [Crosswalk Coverage](#crosswalk-coverage)
8. [Relationship Import Priority Strategy](#8-relationship-import-priority-strategy)

---

## 1. Identity Architecture

### 1.1 Three-Tier Cipher System (Internal IDs)

**Purpose:** Content-addressable identifiers for O(1) graph navigation

#### **Tier 1: Entity Cipher** (Cross-Subgraph Join Key)

**Formula:**
```python
entity_cipher = f"ent_{type_prefix}_{resolved_id}"
```

**Registry (9 Canonical Types):**

| Entity Type | Prefix | Example Cipher | Wikidata Class |
|-------------|--------|----------------|----------------|
| **PERSON** | `per` | `ent_per_Q1048` | Q5 (human) |
| **EVENT** | `evt` | `ent_evt_Q25238182` | Q1656682 (event) |
| **PLACE** | `plc` | `ent_plc_Q220` | Q618123 (geographical object) |
| **SUBJECTCONCEPT** | `sub` | `ent_sub_Q17167` | (Chrystallum-specific) |
| **WORK** | `wrk` | `ent_wrk_Q644312` | Q386724 (work) |
| **ORGANIZATION** | `org` | `ent_org_Q193236` | Q43229 (organization) |
| **PERIOD** | `prd` | `ent_prd_Q6813` | Q11514315 (historical period) |
| **MATERIAL** | `mat` | `ent_mat_Q753` | Q214609 (material) |
| **OBJECT** | `obj` | `ent_obj_Q34379` | Q488383 (object) |

**ADDITIONAL TYPES (Extended Registry):**

| Entity Type | Prefix | Example Cipher | Wikidata Class | CIDOC-CRM | Rationale |
|-------------|--------|----------------|----------------|-----------|-----------|
| **DEITY** | `dei` | `ent_dei_Q4649` | Q22989102 (deity) | E21 Person subclass | Gods, goddesses (Jupiter, Venus) — distinct from humans |
| **LAW** | `law` | `ent_law_Q429264` | Q7748 (law), Q820655 (statute) | E73 Information Object | Legal instruments (Lex Hortensia) — distinct from works |
| **CONCEPT** | `con` | `ent_con_Q7174` | Q17736 (concept), E28/E55 | E28 Conceptual Object | Abstract ideas (democracy, stoicism) — NOT catch-all |

**CONCEPT Rehabilitation:**
- **Previous status:** DEPRECATED legacy catch-all (258 misclassified entities)
- **New status:** LEGITIMATE type for abstract concepts with **strict P31 criteria**
- **Criteria:** Must have `P31: Q17736` (concept) OR `P31: E28/E55` class
- **Not allowed:** Entities that should be PERSON, ORGANIZATION, PERIOD, etc.
- **Migration:** Reclassify misclassified entities, keep genuine concepts

**Total Canonical Types:** 12 (9 original + 3 extended)

---

#### **Tier 2: Faceted Entity Cipher** (Subgraph Address)

**Formula:**
```python
faceted_cipher = f"fent_{facet_prefix}_{base_qid}_{subjectconcept_id}"
```

**18 Canonical Facets:**

| Facet | Prefix | Example Cipher | Research Domain |
|-------|--------|----------------|-----------------|
| **ARCHAEOLOGICAL** | `arc` | `fent_arc_Q1048_Q17167` | Material culture, artifacts |
| **ARTISTIC** | `art` | `fent_art_Q1048_Q17167` | Visual arts, aesthetics |
| **BIOGRAPHIC** | `bio` | `fent_bio_Q1048_Q17167` | Life events, personal history |
| **COMMUNICATION** | `com` | `fent_com_Q1048_Q17167` | Information exchange, rhetoric |
| **CULTURAL** | `cul` | `fent_cul_Q1048_Q17167` | Cultural practices, customs |
| **DEMOGRAPHIC** | `dem` | `fent_dem_Q1048_Q17167` | Population, demographics |
| **DIPLOMATIC** | `dip` | `fent_dip_Q1048_Q17167` | Inter-state relations |
| **ECONOMIC** | `eco` | `fent_eco_Q1048_Q17167` | Trade, finance, resources |
| **ENVIRONMENTAL** | `env` | `fent_env_Q1048_Q17167` | Climate, geography, ecology |
| **GEOGRAPHIC** | `geo` | `fent_geo_Q1048_Q17167` | Spatial relationships, territory |
| **INTELLECTUAL** | `int` | `fent_int_Q1048_Q17167` | Philosophy, scholarship |
| **LINGUISTIC** | `lin` | `fent_lin_Q1048_Q17167` | Language, texts |
| **MILITARY** | `mil` | `fent_mil_Q1048_Q17167` | Warfare, strategy |
| **POLITICAL** | `pol` | `fent_pol_Q1048_Q17167` | Governance, power |
| **RELIGIOUS** | `rel` | `fent_rel_Q1048_Q17167` | Religion, ritual, belief |
| **SCIENTIFIC** | `sci` | `fent_sci_Q1048_Q17167` | Natural philosophy, science |
| **SOCIAL** | `soc` | `fent_soc_Q1048_Q17167` | Social structure, class |
| **TECHNOLOGICAL** | `tec` | `fent_tec_Q1048_Q17167` | Technology, engineering |

**REMOVED (Not a Facet):**
- ~~TEMPORAL~~ — Time is a dimension, not a facet (ADR from 2025-12-26)

---

#### **Tier 3: Claim Cipher** (Assertion Identity)

**Formula:**
```python
claim_cipher = f"fclaim_{facet_prefix}_{hash[:16]}"

# Hash input:
hash_input = (
    f"{subject_qid}|"
    f"{property_pid}|"
    f"{object_qid}|"
    f"{facet_id}|"
    f"{temporal_scope}|"       # Derived from P580/P582/P585
    f"{qualifier_string}|"     # P276, P1545 (if present)
    f"{source_qid}|"
    f"{passage_locator}"
)
```

**Example:**
```
fclaim_pol_a1b2c3d4e5f6g7h8
  facet: POLITICAL (pol)
  hash: a1b2c3d4e5f6g7h8 (first 16 chars of SHA256)
```

**Cipher-Eligible Qualifiers (5 PIDs):**
- P580 (start time), P582 (end time), P585 (point in time)
- P276 (location), P1545 (series ordinal)

---

### 1.2 External Identifiers (Federation IDs)

#### **Wikidata** (Universal Hub)

| ID Type | Format | Example | Coverage | Usage |
|---------|--------|---------|----------|-------|
| **QID** (Entity) | `Q{digits}` | Q1048 | ~110M entities | Primary entity ID |
| **PID** (Property) | `P{digits}` | P39 (position held) | ~11K properties | Relationship types |

**Crosswalk:** Every Chrystallum entity SHOULD have a QID (authority cascade if not)

---

#### **Library Standards** (Classification & Subject)

| Federation | ID Format | Example | Coverage | Purpose |
|------------|-----------|---------|----------|---------|
| **LCSH** | `sh{digits}` | sh85115055 | ~450K headings | Subject headings |
| **FAST** | `fst{digits}` | fst01204885 | ~2M headings | Faceted subjects |
| **LCC** | Class notation | DG254 | Complete | Classification |
| **MARC** | MARC 21 | 001, 100, 245 | Standard | Bibliographic |

**Crosswalk:** SubjectConcepts MUST have LCSH (Tier 1 authority)

---

#### **Geographic Authorities**

| Federation | ID Format | Example | Coverage | Purpose |
|------------|-----------|---------|----------|---------|
| **Pleiades** | `{digits}` | 423025 (Rome) | 41,993 places | Ancient geography |
| **TGN** | `{digits}` | 7000874 (Rome) | ~2M places | Getty geographic |
| **GeoNames** | `{digits}` | 3169070 (Rome) | ~25M places | Modern geography |

**Crosswalk:** Ancient places SHOULD have Pleiades ID, modern places use GeoNames

---

#### **Temporal Authorities**

| Federation | ID Format | Example | Coverage | Purpose |
|------------|-----------|---------|----------|---------|
| **PeriodO** | `p0{id}` | p0qhb9p (Roman Republic) | 8,959 periods | Temporal bounds |

**Crosswalk:** Entities with `:TemporalAnchor` SHOULD align with PeriodO

---

#### **Linguistic & Bibliographic**

| Federation | ID Format | Example | Coverage | Purpose |
|------------|-----------|---------|----------|---------|
| **BabelNet** | `bn:{id}` | bn:00069549n | 20M+ synsets | Multilingual concepts |
| **WorldCat** | OCLC number | 1234567 | 500M+ records | Library holdings |
| **VIAF** | `{digits}` | 87399490 | ~60M authorities | Person authorities |

---

### 1.3 Authority Cascade (Priority Order)

**For Entity Resolution:**
```
Priority 1: Wikidata QID → (Q1048, namespace: "wd")
Priority 2: BabelNet Synset → (bn:14792761n, namespace: "bn")
Priority 3: Chrystallum Synthetic → (crys:PERSON:a4f8c2d1, namespace: "crys")
```

**Decision Rule:**
- Use QID if available (most authoritative)
- Fallback to BabelNet for multilingual coverage
- Generate synthetic ID if neither available (deterministic hash)

---

### 1.4 Crosswalk Coverage Metrics

**Current Database State (2,600 Entities):**

| Federation | Entities with ID | Coverage % | Notes |
|------------|-----------------|------------|-------|
| **Wikidata QID** | ~2,600 | 100% | All entities have QIDs (primary source) |
| **Pleiades** | 68 | 2.6% | PLACE entities only (ancient) |
| **LCSH** | 12-29 | <2% | SUBJECTCONCEPT entities only |
| **FAST** | 12-29 | <2% | SUBJECTCONCEPT entities only |
| **PeriodO** | 0 | 0% | TemporalAnchor not implemented yet |
| **BabelNet** | 0 | 0% | Not queried yet (fallback only) |

**Target Coverage (10K Entities):**
- Wikidata QID: 95%+ (primary authority)
- Pleiades: 5-10% (ancient places only)
- LCSH/FAST: 100% of SubjectConcepts (library backbone)
- PeriodO: 80%+ of TemporalAnchor entities

---

## 2. Label System

### 2.1 Node Labels (Neo4j)

#### **Domain Entities** (Research Data)

| Label | Purpose | Count (Current) | Example |
|-------|---------|-----------------|---------|
| `:Entity` | Base label for all domain entities | 2,600 | Caesar, Rome, Roman Republic |
| `:TemporalAnchor` | Entities that define temporal periods | 0 (not impl) | Roman Republic (509-27 BCE) |
| `:FacetedEntity` | Facet-scoped entity views | 360 | Caesar in POLITICAL facet |
| `:FacetClaim` | Facet-scoped assertions | 0 (not impl) | "Caesar was consul" claim |

#### **Meta-Model Entities** (System Structure)

| Label | Purpose | Count | Example |
|-------|---------|-------|---------|
| `:Chrystallum` | System root node | 1 | System v1.0 |
| `:Federation` | External authority sources | 10 | Wikidata, Pleiades, PeriodO |
| `:EntityType` | Entity type registry | 14 | PERSON, EVENT, PLACE |
| `:Facet` | Facet registry | 18 | POLITICAL, MILITARY |
| `:SubjectConcept` | Research theme anchors | 79 | Roman Republic |
| `:Agent` | SFA deployment tracking | 3 | SFA_POLITICAL_RR |
| `:Schema` | Per-type validation schemas | 9 | Place schema, Period schema |

#### **Legacy Labels** (Coexisting System)

| Label | Purpose | Count | Migration Status |
|-------|---------|-------|------------------|
| `:Human` | Legacy person nodes | Unknown | Migrate to :Entity {entity_type: "PERSON"} |
| `:Organization` | Legacy org nodes | Unknown | Migrate to :Entity {entity_type: "ORGANIZATION"} |
| `:Period` | Legacy period nodes | Unknown | Migrate to :Entity {entity_type: "PERIOD"} |
| `:Place` | Legacy place nodes | Unknown | Migrate to :Entity {entity_type: "PLACE"} |
| `:Event` | Legacy event nodes | Unknown | Migrate to :Entity {entity_type: "EVENT"} |
| `:Work` | Legacy work nodes | Unknown | Migrate to :Entity {entity_type: "WORK"} |
| `:Year` | Temporal backbone | 4,025 | Keep (infrastructure, not domain) |

---

### 2.2 Multi-Label Pattern

**ADR-002: TemporalAnchor Multi-Label Pattern**

Entities can have MULTIPLE labels expressing multiple roles:

```cypher
// Roman Republic: organization + temporal anchor + domain entity
(:Entity:Organization:TemporalAnchor {
  entity_cipher: "ent_org_Q17167",
  entity_type: "ORGANIZATION",
  is_temporal_anchor: true
})
```

**Query Pattern:**
```cypher
// Find all organizations that define temporal periods
MATCH (n:Entity&Organization&TemporalAnchor)
RETURN n.entity_cipher, n.label_en, n.temporal_scope
```

---

## 3. Relationship Master Types

### 3.1 Registry Overview

**Source:** `Relationships/relationship_types_registry_master.csv`  
**Registry Total:** 314 relationship types  
**Database (Entity-to-Entity):** 19 types, 784 edges (audit 2026-02-22)  
**Registry Coverage:** 5 of 45 DB types in registry (11.1%); 309 registry types unused (98.4%)

---

### 3.2 All 37 Categories (Canonical Taxonomy)

| # | Category | Count | Domain | Key Relationships |
|---|----------|-------|--------|-------------------|
| 1 | **Application** | 10 | Technology | MATERIAL_USED, USE, USED_BY |
| 2 | **Attribution** | 11 | Bibliography | ANALYZES, NAMED_AFTER, QUOTES |
| 3 | **Authorship** | 12 | Creation | AUTHOR, CREATOR, WORK_OF |
| 4 | **Causality** | 8 | Causation | CAUSED, CAUSED_BY, CONTRIBUTED_TO |
| 5 | **Comparative** | 4 | Technology | SUPERIOR_TO, INFERIOR_TO |
| 6 | **Cultural** | 8 | Culture | EVOLVED_INTO, CLAIMS_HERITAGE_FROM |
| 7 | **Diplomatic** | 15 | International | NEGOTIATED_WITH, SENT_ENVOYS_TO |
| 8 | **Documentary** | 2 | Learning | SUBJECT_OF, ABOUT |
| 9 | **Economic** | 16 | Economics | PRODUCES_GOOD, TAXED, CONFISCATED_LAND_FROM |
| 10 | **Evolution** | 9 | Time/Culture | REPLACED_BY, SUB_PERIOD_OF |
| 11 | **Familial** | 26 | Family | CHILD_OF, SPOUSE_OF, FATHER_OF, SIBLING_OF |
| 12 | **Functional** | 4 | Technology | DESIGNED_FOR, EFFECTIVE_AGAINST |
| 13 | **Geographic** | 22 | Geography | LOCATED_IN, BORN_IN, PART_OF, FOUNDED |
| 14 | **Honorific** | 9 | Honors | AWARD_RECEIVED, DECORATED_WITH |
| 15 | **Ideological** | 2 | Ideology | ADHERES_TO, IDEOLOGY_OF |
| 16 | **Institutional** | 8 | Political | APPOINTED, REFORMED, REINSTATED |
| 17 | **Legal** | 12 | Law | CONVICTED_OF, EXECUTED, PROSCRIBED |
| 18 | **Linguistic** | 2 | Language | SPOKE_LANGUAGE, LANGUAGE_OF |
| 19 | **Measurement** | 2 | Quantification | HAS_INDICATOR, INDICATOR_OF |
| 20 | **Membership** | 2 | Organizations | MEMBER_OF, HAS_MEMBER |
| 21 | **Military** | 22 | Warfare | FOUGHT_IN, DEFEATED, SACKED, BESIEGED |
| 22 | **Moral** | 3 | Ethics | RESPONSIBLE_FOR, COMMITTED_SUICIDE |
| 23 | **Observation** | 2 | History | WITNESSED_EVENT, WITNESSED_BY |
| 24 | **Participation** | 2 | History | PARTICIPATED_IN, HAD_PARTICIPANT |
| 25 | **Political** | 35 | Governance | CONTROLLED, CONQUERED, ALLIED_WITH, PROSCRIBED |
| 26 | **Position** | 9 | Public Office | POSITION_HELD, APPOINTED_TO, COMMANDED |
| 27 | **Production** | 6 | Technology | MANUFACTURED_BY, TYPICALLY_MADE_OF |
| 28 | **Reasoning** | 6 | CRMinf | I1_INFERRED_FROM, I2_BELIEVED_TO_HOLD |
| 29 | **Relations** | 7 | Social | RELATED_TO, ALLY_OF, ENEMY_OF, INFLUENCED |
| 30 | **Religious** | 6 | Religion | CONVERTED_TO, GOD_OF, PATRON_DEITY_OF |
| 31 | **Scholarly** | 2 | Learning | FIELD_OF_STUDY, STUDIED_BY |
| 32 | **Semantic** | 1 | General | RELATED_TO (generic) |
| 33 | **Social** | 6 | Social Structure | PATRON_OF, CLIENT_OF, OWNED |
| 34 | **Temporal** | 6 | Time | SUB_PERIOD_OF, DURING, CONTAINS_PERIOD |
| 35 | **Trade** | 3 | Commerce | EXPORTED_TO, IMPORTED_FROM |
| 36 | **Typological** | 3 | Culture | VARIANT_OF, HAS_VARIANT |
| 37 | **Vital** | 2 | Biography | DIED_AT, DEATH_LOCATION |

---

### 3.3 Top 80 Most Important Relationship Types (Priority Order)

**Tier 1: Core Hierarchical (Foundation)**

| Relationship | Wikidata PID | CIDOC-CRM | Transitivity | Category |
|--------------|--------------|-----------|--------------|----------|
| **INSTANCE_OF** | P31 | E1 → E55 Type | No | (Canonical — add to registry) |
| **SUBCLASS_OF** | P279 | E55 → E55 | **Yes** | (Canonical — add to registry) |
| **PART_OF** | P361 | E18 → E18 / P46 | **Yes** | Geographic, Temporal |
| **HAS_PART** | P527 | P46i forms part of | **Yes** | Geographic |
| **HAS_PARTS** | P527 | P46i | **Yes** | (DB variant) |

**Tier 2: Temporal**

| Relationship | Wikidata PID | CIDOC-CRM | Category |
|--------------|--------------|-----------|----------|
| **BROADER_THAN** | (P527 inverse) | P4 has time-span | Temporal |
| **SUB_PERIOD_OF** | P361 | P4 | Temporal |
| **NARROWER_THAN** | (P527) | - | Temporal |
| **DURING** | P585 (qualifier) | P4 | Temporal |
| **CONTAINS_PERIOD** | P527 | - | Temporal |
| **FOLLOWED_BY** | P156 | P134 continued | Evolution |
| **FOLLOWS** | P155 | P134i was continued by | Evolution |
| **REPLACED_BY** | P1366 | - | Evolution, Political |
| **REPLACES** | P1365 | - | Political |

**Tier 3: Geographic**

| Relationship | Wikidata PID | CIDOC-CRM | Category |
|--------------|--------------|-----------|----------|
| **LOCATED_IN** | P131 | P53 has former/current location | Geographic |
| **BORN_IN** | P19 | E67 Birth | Geographic |
| **DIED_IN** | P20 | E69 Death | Geographic |
| **LIVED_IN** | P551 | E7 Activity (residence) | Geographic |
| **FOUNDED** | P112 | E63 Beginning of Existence | Geographic |
| **PART_OF** (spatial) | P361 | P46 forms part of | Geographic |

**Tier 4: Participatory (Event-Centric)**

| Relationship | Wikidata PID | CIDOC-CRM | Category |
|--------------|--------------|-----------|----------|
| **PARTICIPATED_IN** | P710 | P11 had participant | Participation |
| **HAD_PARTICIPANT** | P710 | P11i participated in | Participation |
| **FOUGHT_IN** | P607 | E7 Activity | Military |
| **BATTLED_IN** | P607 | E7 Activity | Military |
| **WITNESSED_EVENT** | P1441 | P12 occurred in presence of | Observation |
| **NEGOTIATED_TREATY** | P3342 | P14 carried out by | Diplomatic |

**Tier 5: Social & Familial**

| Relationship | Wikidata PID | CIDOC-CRM | Category |
|--------------|--------------|-----------|----------|
| **CHILD_OF** | (P40 inverse) | P152 has parent | Familial |
| **PARENT_OF** | P40 | P97/P96 | Familial |
| **FATHER_OF** | P40 | P97 from father | Familial |
| **MOTHER_OF** | P40 | P96 by mother | Familial |
| **SPOUSE_OF** | P26 | P107 has member | Familial |
| **SIBLING_OF** | P3373 | P107 | Familial |
| **MEMBER_OF** | P463 | E85 Joining | Membership |
| **MEMBER_OF_GENS** | P53 | P107 | Familial |

**Tier 6: Position & Institutional**

| Relationship | Wikidata PID | CIDOC-CRM | Category |
|--------------|--------------|-----------|----------|
| **POSITION_HELD** | P39 | E13 Attribute Assignment | Position |
| **APPOINTED_TO** | P39 | E13 | Position |
| **APPOINTED** | P39 | E13 | Institutional |
| **OFFICE_HELD_BY** | P39 | - | Position |

**Tier 7: Causality & Authorship**

| Relationship | Wikidata PID | CIDOC-CRM | Category |
|--------------|--------------|-----------|----------|
| **CAUSED** | P828 | P15 was influenced by | Causality |
| **CAUSED_BY** | P828 | P15i influenced | Causality |
| **AUTHOR** | P50 | P94 has created | Authorship |
| **CREATOR** | P170 | P94 has created | Authorship |
| **FOUNDED** | P112 | E63 | Geographic |

**Tier 8: Political & Documentary**

| Relationship | Wikidata PID | CIDOC-CRM | Category |
|--------------|--------------|-----------|----------|
| **CONTROLLED** | P17 | E7 Activity | Political |
| **CONVERTED_TO** | P140 | - | Religious |
| **SUBJECT_OF** | P921 | P56 is composed of | Documentary |
| **ABOUT** | P921 | P56i | Documentary |
| **FIELD_OF_STUDY** | P101 | P134 | Scholarly |

---

### 3.4 Complete Wikidata PID → Chrystallum Mapping Table

| Wikidata PID | Label | Chrystallum Relationship(s) | CIDOC-CRM | Notes |
|--------------|-------|-----------------------------|-----------|-------|
| **P17** | country | CONTROLLED, CONTROLLED_BY | E7_Activity | Political control |
| **P19** | place of birth | BORN_IN, BIRTHPLACE_OF | E67_Birth | |
| **P20** | place of death | DIED_IN, DEATH_PLACE_OF | E69_Death | |
| **P26** | spouse | SPOUSE_OF | P107 | |
| **P39** | position held | POSITION_HELD, APPOINTED_TO, APPOINTED, OFFICE_HELD_BY | E13_Attribute_Assignment | With qualifiers P580/P582 |
| **P40** | child | PARENT_OF, FATHER_OF, MOTHER_OF, CHILD_OF (inverse) | P97/P96/P152 | |
| **P50** | author | AUTHOR, WORK_OF | P94 | |
| **P53** | family | MEMBER_OF_GENS, HAS_GENS_MEMBER | P107 | Roman gens |
| **P61** | discoverer | DISCOVERED_BY, DISCOVERER_OF | E13 | |
| **P84** | architect | ARCHITECT, DESIGNED | P94 | |
| **P86** | composer | COMPOSER, COMPOSITION_OF | P94 | |
| **P101** | field of work | FIELD_OF_STUDY, STUDIED_BY | P134 | |
| **P112** | founded by | FOUNDED | E63 | |
| **P131** | located in | LOCATED_IN, LOCATION_OF | P53 | |
| **P138** | named after | NAMED_AFTER, NAMESAKE_OF | - | |
| **P140** | religion | CONVERTED_TO, CONVERTED_BY | - | |
| **P166** | award received | AWARD_RECEIVED, AWARDED_TO | E13 | |
| **P170** | creator | CREATOR, CREATION_OF | P94 | |
| **P176** | manufacturer | MANUFACTURED_BY | - | |
| **P186** | made from | MATERIAL_USED, MATERIAL_IN, TYPICALLY_MADE_OF | P45 | |
| **P361** | part of | PART_OF, SUB_PERIOD_OF | P46 | Spatial + temporal |
| **P366** | has use | USE, USED_BY | P101 | |
| **P463** | member of | MEMBER_OF, HAS_MEMBER | E85_Joining | |
| **P527** | has part | HAS_PART, CONTAINS_PERIOD | P46i | |
| **P551** | residence | LIVED_IN, RESIDENCE_OF | E7_Activity | |
| **P576** | dissolved | COLLAPSED, CAUSED_COLLAPSE_OF | E64_End_of_Existence | |
| **P580** | start time | (qualifier) | P4 | Not edge |
| **P582** | end time | (qualifier) | P4 | Not edge |
| **P607** | participated in conflict | FOUGHT_IN, BATTLED_IN, BATTLE_PARTICIPANT | E7_Activity | |
| **P710** | participant | PARTICIPATED_IN, HAD_PARTICIPANT | P11 | |
| **P828** | has cause | CAUSED, CAUSED_BY, CONTRIBUTED_TO | P15 | |
| **P921** | main subject | SUBJECT_OF, ABOUT | P56 | |
| **P1001** | applies to jurisdiction | APPLIES_TO_JURISDICTION | E3_Condition_State | |
| **P1056** | product | PRODUCES_GOOD, PRODUCED_BY | E12_Production | |
| **P1071** | location of creation | MANUFACTURED_IN | - | |
| **P1120** | place of death | DIED_AT, DEATH_LOCATION | P100 | |
| **P1142** | political ideology | ADHERES_TO, IDEOLOGY_OF | P2 | |
| **P1365** | replaces | SUCCESSOR_OF | - | |
| **P1366** | replaced by | REPLACED_BY, SUPERSEDED_BY, SUCCEEDED_BY | - | |
| **P1399** | convicted of | CONVICTED_OF, CONVICTION_OF | E13 | |
| **P1412** | languages spoken | SPOKE_LANGUAGE, LANGUAGE_OF | P72 | |
| **P1441** | present in work | WITNESSED_EVENT, WITNESSED_BY | P12 | |
| **P1448** | official name | RENAMED, RENAMED_TO | E15 | |
| **P2079** | fabrication method | MADE_USING_TECHNIQUE | - | |
| **P2561** | name | NAME | - | |
| **P3342** | significant person | NEGOTIATED_TREATY, TREATY_NEGOTIATOR | P14 | |
| **P3373** | sibling | SIBLING_OF, HALF_SIBLING_OF | P107 | |
| **P31** | instance of | INSTANCE_OF | E1→E55 | **Canonical — add to registry** |
| **P279** | subclass of | SUBCLASS_OF | E55→E55 | **Canonical — add to registry** |

---

### 3.5 CIDOC-CRM Property Alignments (Registry)

| CIDOC-CRM Property | Label | Chrystallum Relationship(s) |
|-------------------|-------|------------------------------|
| **P4** | has time-span | DURING, temporal_scope (qualifier) |
| **P7** | took place at | LOCATED_IN |
| **P11** | had participant | PARTICIPATED_IN, HAD_PARTICIPANT |
| **P12** | occurred in presence of | WITNESSED_EVENT, WITNESSED_BY |
| **P14** | carried out by | NEGOTIATED_TREATY, TREATY_NEGOTIATOR |
| **P15** | was influenced by | CAUSED, CAUSED_BY |
| **P17** | was motivated by | ACTION_JUSTIFIED_BY |
| **P45** | consists of | MATERIAL_USED, MATERIAL_IN |
| **P46** | forms part of | PART_OF, SUB_PERIOD_OF |
| **P53** | has former/current location | LOCATED_IN |
| **P56** | is composed of | SUBJECT_OF, ABOUT |
| **P72** | has language | SPOKE_LANGUAGE |
| **P94** | has created | AUTHOR, CREATOR, ARCHITECT |
| **P96** | by mother | MOTHER_OF |
| **P97** | from father | FATHER_OF |
| **P100** | was death of | DIED_AT, DEATH_LOCATION |
| **P101** | had as general use | USE |
| **P107** | has current/former member | MEMBER_OF, SPOUSE_OF, SIBLING_OF |
| **P134** | continued | FOLLOWED_BY |
| **P134** | has object of interest | FIELD_OF_STUDY |
| **P152** | has parent | PARENT_OF, CHILD_OF |
| **E13** | Attribute Assignment | APPOINTED, CONVICTED_OF, AWARD_RECEIVED |
| **E63** | Beginning of Existence | FOUNDED |
| **E64** | End of Existence | COLLAPSED |
| **E67** | Birth | BORN_IN |
| **E69** | Death | DIED_IN |
| **E7** | Activity | FOUGHT_IN, LIVED_IN, CONTROLLED |
| **E85** | Joining | MEMBER_OF |

---

### 3.6 Hierarchical Relationships (Transitive)

| Relationship | Wikidata PID | Transitivity | Use Case |
|--------------|--------------|--------------|----------|
| **INSTANCE_OF** | P31 | No | Type classification (Caesar → Q5 human) |
| **SUBCLASS_OF** | P279 | **Yes** | Class hierarchy (Battle → Conflict → Event) |
| **PART_OF** | P361 | **Yes** | Mereological (Cannae → Punic Wars) |
| **HAS_PART** | P527 | **Yes** | Inverse of PART_OF |
| **SUB_PERIOD_OF** | P361 | **Yes** | Temporal nesting (Early Republic → Roman Republic) |

```cypher
// Hierarchy traversal example
MATCH (e:Entity)-[:PART_OF*1..5]->(rr:Entity {qid: "Q17167"})
RETURN e.entity_cipher, e.label_en
```

---

### 3.7 Temporal Relationships

| Relationship | Wikidata PID | Example |
|--------------|--------------|---------|
| **BROADER_THAN** | (P527 inverse) | Roman Empire → Principate |
| **SUB_PERIOD_OF** | P361 | Early Republic → Roman Republic |
| **NARROWER_THAN** | P527 | Principate → Roman Empire |
| **DURING** | P585 (qualifier) | Gallic Wars → Roman Republic period |
| **CONTAINS_PERIOD** | P527 | Roman Republic → Early Republic |
| **FOLLOWED_BY** | P156 | Roman Republic → Roman Empire |
| **REPLACED_BY** | P1366 | Republic → Principate |

---

### 3.8 Social Relationships

| Relationship | Wikidata PID | Example |
|--------------|--------------|---------|
| **CHILD_OF** | P40 (inverse) | Augustus → Caesar |
| **SPOUSE_OF** | P26 | Caesar ↔ Calpurnia |
| **MEMBER_OF** | P463 | Caesar → Populares |
| **MEMBER_OF_GENS** | P53 | Caesar → Julia (gens) |
| **SIBLING_OF** | P3373 | Octavia ↔ Augustus |
| **PARENT_OF** | P40 | Caesar → Augustus (adopted) |
| **PATRON_OF** | - | Senator → Client |
| **CLIENT_OF** | - | Client → Senator |

---

### 3.9 Participatory Relationships

| Relationship | Wikidata PID | CIDOC-CRM | Example |
|--------------|--------------|-----------|---------|
| **PARTICIPATED_IN** | P710 | P11 | Caesar → Gallic Wars |
| **HAD_PARTICIPANT** | P710 | P11i | Gallic Wars → Caesar |
| **POSITION_HELD** | P39 | E13 | Caesar → Consul |
| **APPOINTED_TO** | P39 | E13 | Caesar → Dictator |
| **FOUGHT_IN** | P607 | E7 | Hannibal → Cannae |
| **WITNESSED_EVENT** | P1441 | P12 | Polybius → Third Punic War |
| **NEGOTIATED_TREATY** | P3342 | P14 | Person → Treaty |

---

## 4. Federation Registry

### 4.1 Complete Federation List (10 Authorities)

**From Meta-Model Exploration:**

| Federation | Type | Mode | Coverage | Source | Crosswalk to Wikidata |
|------------|------|------|----------|--------|---------------------|
| **Wikidata** | Universal | hub_api | ~110M entities | https://query.wikidata.org/sparql | 100% (is Wikidata) |
| **Pleiades** | Geographic | local | 41,993 places | pleiades_places.csv | ~80% (via P1584) |
| **PeriodO** | Temporal | local | 8,959 periods | periodo-dataset.csv | ~60% (via period definitions) |
| **LCSH** | Conceptual | local | ~450K | LCSH/skos_subjects/ | ~90% (via FAST crosswalk) |
| **FAST** | Topical | local | ~2M | FASTTopical_parsed.csv | 95% (designed for Wikidata) |
| **LCC** | Classification | local | Complete | lcc_flat.csv | Indirect (via LCSH) |
| **MARC** | Bibliographic | local | Standard | MARC records | Via OCLC/WorldCat |
| **GeoNames** | Geographic | hybrid | ~25M | API + crosswalk | ~95% (via P1566) |
| **BabelNet** | Linguistic | api | 20M+ synsets | External API | ~70% (multilingual overlap) |
| **WorldCat** | Bibliographic | api | 500M+ | External API | Via VIAF/OCLC |

---

### 4.2 Federation Mode Definitions

| Mode | Definition | Example | Access Pattern |
|------|------------|---------|----------------|
| **local** | Pre-loaded CSV/files | Pleiades, PeriodO | Direct Neo4j query (no network) |
| **hub_api** | Central SPARQL endpoint | Wikidata | Live SPARQL queries |
| **api** | External REST API | BabelNet, WorldCat | HTTP requests (rate-limited) |
| **hybrid** | Crosswalk + API fallback | GeoNames | Query local crosswalk, API if missing |

---

### 4.3 Federation Type Classification

| Type | Federations | Purpose |
|------|------------|---------|
| **Universal** | Wikidata | All entity types |
| **Geographic** | Pleiades, GeoNames, TGN | Place entities |
| **Temporal** | PeriodO | Period/TemporalAnchor entities |
| **Conceptual** | LCSH | Subject headings |
| **Topical** | FAST | Faceted subjects |
| **Classification** | LCC | Library organization |
| **Bibliographic** | MARC, WorldCat | Work entities |
| **Linguistic** | BabelNet | Multilingual concepts |

---

### 4.4 Per-Entity-Type Federation Dependencies

**From Schema Nodes (Meta-Model):**

| Entity Type | Required Federations | Optional Federations | Notes |
|-------------|---------------------|---------------------|-------|
| **PERSON** | Wikidata, VIAF | BabelNet | VIAF required for library catalog integration (60M authority records) |
| **EVENT** | Wikidata | - |
| **PLACE** | Wikidata, Pleiades | GeoNames, TGN |
| **SUBJECTCONCEPT** | Wikidata, LCSH, FAST, LCC | - |
| **WORK** | Wikidata | WorldCat, MARC |
| **ORGANIZATION** | Wikidata | - |
| **PERIOD** | Wikidata, PeriodO | - |
| **MATERIAL** | Wikidata | - |
| **OBJECT** | Wikidata | - |

**Validation Rule:** Every entity MUST have at least one required federation ID

---

## 5. CIDOC-CRM Alignment

**Reference:** CIDOC-CRM 7.1.3 — https://cidoc-crm.org/

---

### 5.1 Full Class Mappings (Chrystallum → CIDOC-CRM)

| Chrystallum Entity Type | CIDOC-CRM Class | Definition | Hierarchy |
|------------------------|-----------------|------------|-----------|
| **PERSON** | E21 Person | Individual human beings | E21 → E39 Actor → E77 Persistent Item → E1 |
| **EVENT** | E5 Event | Occurrences at specific times/locations | E5 → E4 Period → E2 Temporal Entity → E1 |
| **PLACE** | E53 Place | Spatial locations, geographical areas | E53 → E44 Place Appellation → E41 Appellation → E1 |
| **WORK** | E73 Information Object | Textual/conceptual works | E73 → E71 Human-Made Thing → E70 Thing → E1 |
| **ORGANIZATION** | E74 Group | Collectives, institutions | E74 → E39 Actor → E77 Persistent Item → E1 |
| **PERIOD** | E4 Period | Temporal designations | E4 → E2 Temporal Entity → E1 |
| **OBJECT** | E19 Physical Object | Tangible artifacts | E19 → E18 Physical Thing → E72 Legal Object → E1 |
| **MATERIAL** | E57 Material | Physical substances | E57 → E55 Type → E1 |
| **SUBJECTCONCEPT** | *(no direct)* | Research theme anchors | Chrystallum-specific |

**Supporting Classes (CIDOC-CRM 7.1.3):**

| CIDOC-CRM | Label | Usage |
|-----------|-------|-------|
| E1 | CRM Entity | Root class |
| E2 | Temporal Entity | Superclass of E4, E5 |
| E3 | Condition State | Political status, jurisdiction |
| E4 | Period | Temporal spans |
| E5 | Event | Activities, occurrences |
| E6 | Destruction | LEVELLED, destruction events |
| E7 | Activity | FOUGHT_IN, LIVED_IN, CONTROLLED |
| E8 | Acquisition | CONQUERED, CONFISCATED_LAND_FROM |
| E9 | Move | EXILED, MIGRATED_TO, FLED_TO |
| E11 | Modification | REFORMED |
| E12 | Production | PRODUCES_GOOD |
| E13 | Attribute Assignment | APPOINTED, CONVICTED_OF, AWARD_RECEIVED |
| E15 | Identifier Assignment | RENAMED |
| E18 | Physical Thing | PART_OF (mereological) |
| E19 | Physical Object | OBJECT entities |
| E21 | Person | PERSON entities |
| E53 | Place | PLACE entities |
| E55 | Type | INSTANCE_OF, SUBCLASS_OF |
| E57 | Material | MATERIAL entities |
| E63 | Beginning of Existence | FOUNDED |
| E64 | End of Existence | COLLAPSED |
| E67 | Birth | BORN_IN |
| E69 | Death | DIED_IN, DIED_AT |
| E73 | Information Object | WORK entities |
| E74 | Group | ORGANIZATION entities |
| E81 | Transformation | EVOLVED_INTO |
| E85 | Joining | MEMBER_OF |

---

### 5.2 Full Property Mappings (CIDOC-CRM → Chrystallum)

| CIDOC-CRM | Label | Chrystallum Relationship | Domain → Range |
|-----------|-------|--------------------------|---------------|
| **P2** | has type | INSTANCE_OF, ADHERES_TO | E1 → E55 Type |
| **P4** | has time-span | DURING, temporal_scope | E2 → E52 Time-Span |
| **P7** | took place at | LOCATED_IN | E5 → E53 Place |
| **P11** | had participant | PARTICIPATED_IN, HAD_PARTICIPANT | E5 → E39 Actor |
| **P12** | occurred in presence of | WITNESSED_EVENT, WITNESSED_BY | E5 → E39 Actor |
| **P14** | carried out by | NEGOTIATED_TREATY | E7 → E39 Actor |
| **P15** | was influenced by | CAUSED, CAUSED_BY | E7 → E7 |
| **P17** | was motivated by | ACTION_JUSTIFIED_BY | E7 → E7 |
| **P43** | has dimension | HAS_INDICATOR | E70 → E54 Dimension |
| **P45** | consists of | MATERIAL_USED | E18 → E57 Material |
| **P46** | forms part of | PART_OF, SUB_PERIOD_OF | E18 → E18 |
| **P53** | has former/current location | LOCATED_IN | E92 → E53 Place |
| **P56** | bears feature of | SUBJECT_OF, ABOUT | E73 → E1 |
| **P67** | refers to | ORIGIN_MYTH | E73 → E1 |
| **P72** | has language | SPOKE_LANGUAGE | E33 → E56 Language |
| **P94** | has created | AUTHOR, CREATOR | E65 → E28 Conceptual Object |
| **P96** | by mother | MOTHER_OF | E67 → E21 Person |
| **P97** | from father | FATHER_OF | E67 → E21 Person |
| **P100** | was death of | DIED_AT | E69 → E21 Person |
| **P101** | had as general use | USE | E71 → E55 Type |
| **P107** | has current/former member | MEMBER_OF, SPOUSE_OF | E74 → E39 Actor |
| **P123** | resulted in | CAUSED (inverse) | E63 → E77 |
| **P134** | continued | FOLLOWED_BY | E7 → E7 |
| **P134** | has object of interest | FIELD_OF_STUDY | E5 → E1 |
| **P152** | has parent | PARENT_OF | E21 → E21 Person |

---

### 5.3 Chrystallum Extensions to CIDOC-CRM

| Extension | CIDOC-CRM | Chrystallum |
|-----------|-----------|-------------|
| **Library Backbone** | - | LCSH, FAST, LCC, MARC properties |
| **Systematic ISO 8601** | Supports temporal | Mandates `-YYYY-MM-DD` format |
| **Action Structure** | Generic E5/E7 | goal_type, trigger_type, action_type, result_type |
| **Faceted Views** | - | 18 canonical facets |
| **Multi-Authority Scoring** | - | Federation score (FS3_WELL_FEDERATED) |
| **Cipher Addressing** | - | Three-tier cipher system |
| **SubjectConcept** | - | Research theme anchors (no E-class equivalent) |

**Implementation:**
```cypher
(:Entity {
  entity_type: "PERSON",
  cidoc_crm_class: "E21_Person",
  cidoc_crm_version: "7.1.3"
})

-[:PARTICIPATED_IN {
  cidoc_crm_property: "P11_had_participant",
  wikidata_pid: "P710"
}]->

(:Entity {
  entity_type: "EVENT",
  cidoc_crm_class: "E5_Event"
})
```

---

## 6. CRMinf Integration

**Reference:** CRMinf 1.2 (DRAFT) — https://cidoc-crm.org/crminf  
**Purpose:** Model argumentation, belief, and scholarly inference in descriptive/empirical sciences

---

### 6.1 Full I-Class Mappings (CRMinf → Chrystallum)

| CRMinf Class | Definition | Chrystallum Equivalent |
|---------------|------------|------------------------|
| **I1 Argumentation** | Argumentation structures; connects premises to conclusions | RetrospectiveClaim |
| **I2 Belief** | Beliefs as distinct entities in reasoning | InSituClaim, Claim with confidence |
| **I3 Inferential Step** | Single step in reasoning chain | SFA extraction step |
| **I4 Proposition Set** | Collection of propositions | Claim cluster (facet-scoped) |
| **I5 Inference Making** | Process of making inferences; connects premises to conclusions | SFA agent extraction, ANALYZES, INTERPRETS |
| **I6 Belief Revision** | Revision of belief based on new evidence | I7_HAS_OBJECT, I8_HAS_RESULT |
| **I7 Belief Adoption** | Agent accepts belief | I7_Belief_Adoption, ATTRIBUTED_TO, MENTIONS |
| **I8 Inference Derivation** | Derivation of inference from premises | I1_INFERRED_FROM |

**Registry Relationships with CRMinf Alignment (crminf_applicable=true):**

| Chrystallum Relationship | CRMinf Mapping | Category |
|--------------------------|----------------|----------|
| ANALYZES | I5_Inference_Making + J3 | Attribution |
| ATTRIBUTED_TO | I7_Belief_Adoption + J6 | Attribution |
| DESCRIBES | I7_Belief_Adoption + J7 | Attribution |
| EXTRACTED_FROM | I7_Belief_Adoption + J6 | Attribution |
| INTERPRETS | I5_Inference_Making + J3 | Attribution |
| MENTIONS | I7_Belief_Adoption + J7 | Attribution |
| QUOTES | I7_Belief_Adoption + J7 | Attribution |
| SUMMARIZES | I7_Belief_Adoption + J7 | Attribution |
| I1_INFERRED_FROM | I1 Argumentation | Reasoning |
| I2_BELIEVED_TO_HOLD | I2 Belief | Reasoning |
| I3_HAS_NOTE | I3 Inferential Step | Reasoning |
| I4_HAS_UNCERTAINTY | I4 Proposition Set | Reasoning |
| I7_HAS_OBJECT | I6 Belief Revision | Reasoning |
| I8_HAS_RESULT | I6 Belief Revision | Reasoning |
| PARTICIPATED_IN | P11 (participant) | Participation |
| WITNESSED_EVENT | P12 (presence) | Observation |

---

### 6.2 InSitu vs Retrospective Claim Alignment

| Claim Type | CRMinf Alignment | Source | Example |
|------------|------------------|--------|---------|
| **InSituClaim** | I2 Belief (ancient agent) | Ancient primary source | Polybius: "Cannae was decisive" |
| **RetrospectiveClaim** | I1 Argumentation (modern scholar) | Modern scholarship | "Cannae demonstrated principal-agent problem" |

**InSitu:** Ancient agent's belief (I2) — documented in primary source  
**Retrospective:** Modern scholar's argumentation (I1) — SUPPORTS or CONTRADICTS InSitu claims

```cypher
(:InSituClaim {
  analysis_layer: "in_situ",
  ancient_agent_qid: "Q193291",
  cidoc_crminf_class: "I2_Belief"
})

<-[:SUPPORTS]-

(:RetrospectiveClaim {
  analysis_layer: "retrospective",
  cidoc_crminf_class: "I1_Argumentation",
  uses_modern_theory: true,
  methodology: "principal-agent theory"
})
```

---

### 6.3 Argumentation Relationships (CRMinf J-Properties)

| CRMinf Property | Label | Chrystallum Relationship | Direction |
|-----------------|-------|-------------------------|-----------|
| **J1** | used as premise | (premise → argument) | Evidence → I1 Argumentation |
| **J2** | concluded that | CONCLUDED | I5 → Conclusion |
| **J3** | used rule | (inference rule) | ANALYZES, INTERPRETS |
| **J4** | that | SUPPORTS | Claim → Target Claim |
| **J5** | holds to be | BELIEF_IN | Agent → Claim |
| **J6** | adopted | ADOPTED_BELIEF | Agent accepts Claim |
| **J7** | has content | (belief content) | MENTIONS, DESCRIBES, QUOTES |

**Chrystallum-Specific (Provenance):**

| Relationship | CRMinf | Usage |
|--------------|--------|-------|
| SUPPORTS | J4 (that) | RetroClaim → InSituClaim |
| CONTRADICTS | (inverse J4) | Claim A ↔ Claim B |
| ATTESTED_BY | P70 documents | Claim → Source Work |
| EXTRACTED_BY | I5 Inference Making | Claim → SFA Agent |

---

## 7. Crosswalk Coverage

**Audit Source:** `output/RELATIONSHIP_AUDIT_REPORT.txt` (2026-02-22)

---

### 7.1 Entity-Level Crosswalk

**Current Database (2,600 Entities):**

| Metric | Count | Percentage | Target (10K) |
|--------|-------|------------|--------------|
| **Entities with Wikidata QID** | 2,600 | 100% | 95%+ |
| **Entities with LCSH** | ~12-29 | <2% | 100% of SubjectConcepts |
| **Entities with Pleiades ID** | 68 | 2.6% | 5-10% (ancient places) |
| **Entities with PeriodO ID** | 0 | 0% | 80% of TemporalAnchors |
| **Entities with multiple federations** | Unknown | Unknown | 60%+ |

---

### 7.2 Relationship-Level Crosswalk (From Audit)

**Entity-to-Entity Relationships:** 784 edges (of 14,001 total; remainder are meta-model)

| Metric | Value | Notes |
|--------|-------|-------|
| **Total relationship types in DB** | 45 | Includes meta-model (HAS_FACET, etc.) |
| **Entity-to-entity types** | 19 | Domain edges only |
| **DB types with Wikidata PID** | 4 | INSTANCE_OF, SUBCLASS_OF, PART_OF, HAS_PARTS (implied) |
| **DB types in registry** | 5 | 11.1% of DB types |
| **Registry types used** | 5 | 1.6% of 314 registry types |
| **Avg relationships per entity** | 0.30 | Target: 3-5 |

**Entity-to-Entity Edge Counts (Top 15):**

| Relationship | Count | In Registry | Wikidata PID |
|--------------|-------|-------------|--------------|
| LOCATED_IN_COUNTRY | 165 | No | - |
| SHARES_BORDER_WITH | 117 | No | - |
| INSTANCE_OF | 103 | No* | P31 |
| CONTAINS | 81 | No | - |
| ON_CONTINENT | 48 | No | - |
| SUBCLASS_OF | 46 | No* | P279 |
| HAS_PARTS | 38 | Yes | P527 |
| PART_OF | 35 | Yes | P361 |
| HAS_CAPITAL | 24 | No | - |
| HAS_OFFICIAL_LANGUAGE | 22 | No | - |
| REPLACES | 20 | No | P1365 |
| FOLLOWS | 20 | No | P155 |
| FOLLOWED_BY | 19 | No | P156 |
| REPLACED_BY | 19 | Yes | P1366 |
| LOCATED_IN | 16 | Yes | P131 |

*INSTANCE_OF, SUBCLASS_OF canonical but not yet in registry

**Coverage Percentages (Entity-to-Entity):**

| Federation | Relationship Types with Mapping | Approx. Coverage |
|------------|--------------------------------|------------------|
| **Wikidata PID** | 4 of 19 entity-to-entity types | ~21-30% (type-level) |
| **CIDOC-CRM** | ~12 of 19 types have CRM alignment in registry | ~64-65% |
| **Registry** | 5 of 19 types in registry | ~26% |

*Note: Coverage may vary by audit scope (type-level vs. edge-level). Target: 95%+ Wikidata PID coverage for imported relationship types.*

**Recommended Audit Query:**
```cypher
MATCH ()-[r]-()
WHERE type(r) IN ['INSTANCE_OF','SUBCLASS_OF','PART_OF','LOCATED_IN',...]
RETURN 
  type(r) as relationship_type,
  count(r) as total,
  sum(CASE WHEN r.wikidata_pid IS NOT NULL THEN 1 ELSE 0 END) as has_pid
ORDER BY total DESC
```

---

### 7.3 SubjectConcept Federation Scores

**Current Implementation (Discovered in Meta-Model):**

```cypher
(:SubjectConcept {
  authority_federation_score: 100,          // 0-100 scale
  authority_federation_state: "FS3_WELL_FEDERATED",
  authority_federation_cipher: "auth_fed_c900a5d3127ce690",
  lcsh_id: "sh85115055",
  fast_id: "fst01204885",
  lcc_subclass: "DG254",
  qid: "Q17167"
})
```

**Federation States:**

| State | Score Range | Federations | Example |
|-------|-------------|-------------|---------|
| **FS3_WELL_FEDERATED** | 90-100 | LCSH + FAST + LCC + Wikidata | Roman Republic (100) |
| **FS2_PARTIAL** | 50-89 | Wikidata + 1-2 others | (Need examples) |
| **FS1_MINIMAL** | 1-49 | Wikidata only | (Need examples) |
| **FS0_UNFEDERATED** | 0 | None | Synthetic entities |

**Current Coverage:**
- Q17167 (Roman Republic): FS3, score 100
- Need to audit other 78 SubjectConcepts

---

## 8. Relationship Import Priority Strategy

**Context:** 2,600 entities, 784 entity-to-entity edges (0.30 per entity). Target: 7,500-13,000 edges (3-5 per entity).

---

### 8.1 Priority 1: Core Hierarchical (Foundation)

| Relationship | Wikidata PID | Target Edges | Transitivity |
|--------------|--------------|--------------|--------------|
| **INSTANCE_OF** | P31 | 2,000-3,000 | No |
| **SUBCLASS_OF** | P279 | 500-1,000 | Yes |
| **PART_OF** | P361 | 1,000-2,000 | Yes |
| **HAS_PART** | P527 | 500-1,000 | Yes |

**Subtotal:** 4,000-7,000 edges  
**Rationale:** Ontological foundation; enables type classification and hierarchy traversal.

---

### 8.2 Priority 2: Temporal

| Relationship | Wikidata PID | Target Edges | Notes |
|--------------|--------------|--------------|-------|
| **BROADER_THAN** | (P527 inverse) | 200-400 | Period nesting |
| **SUB_PERIOD_OF** | P361 | 300-500 | Period hierarchy |
| **DURING** | P585 (qualifier) | 200-400 | Event → Period |
| **FOLLOWED_BY** | P156 | 100-200 | Succession |
| **REPLACED_BY** | P1366 | 100-200 | Replacement |

**Subtotal:** 900-1,700 edges  
**Rationale:** Temporal structure for periods and events.

---

### 8.3 Priority 3: Participatory

| Relationship | Wikidata PID | Target Edges | Notes |
|--------------|--------------|--------------|-------|
| **PARTICIPATED_IN** | P710 | 800-1,500 | Person → Event |
| **POSITION_HELD** | P39 | 600-1,200 | Person → Office |
| **MEMBER_OF** | P463 | 400-800 | Person → Group |
| **FOUGHT_IN** | P607 | 300-600 | Person/Group → Battle |
| **WITNESSED_EVENT** | P1441 | 100-200 | Person → Event |

**Subtotal:** 2,200-4,300 edges  
**Rationale:** Person-event and person-role connections; core for biographical/political research.

---

### 8.4 Priority 4: Geographic & Social (Optional)

| Relationship | Wikidata PID | Target Edges |
|--------------|--------------|--------------|
| **LOCATED_IN** | P131 | 500-1,000 |
| **BORN_IN** | P19 | 200-400 |
| **DIED_IN** | P20 | 200-400 |
| **CHILD_OF** | P40 | 200-400 |
| **SPOUSE_OF** | P26 | 100-200 |
| **MEMBER_OF_GENS** | P53 | 100-200 |

**Subtotal:** 1,300-2,600 edges

---

### 8.5 Target Summary

| Priority | Relationships | Target Edges |
|----------|---------------|--------------|
| **1. Hierarchical** | INSTANCE_OF, SUBCLASS_OF, PART_OF, HAS_PART | 4,000-7,000 |
| **2. Temporal** | BROADER_THAN, SUB_PERIOD_OF, DURING, FOLLOWED_BY, REPLACED_BY | 900-1,700 |
| **3. Participatory** | PARTICIPATED_IN, POSITION_HELD, MEMBER_OF, FOUGHT_IN, WITNESSED_EVENT | 2,200-4,300 |
| **4. Geographic/Social** | LOCATED_IN, BORN_IN, DIED_IN, CHILD_OF, SPOUSE_OF, MEMBER_OF_GENS | 1,300-2,600 |
| **Total** | | **7,500-13,000** |

**For 2,600 entities:** 2.9-5.0 edges per entity (vs. current 0.30)

---

### 8.6 Validation Checklist

- [ ] INSTANCE_OF chain resolves to valid Wikidata types
- [ ] SUBCLASS_OF forms DAG (no cycles)
- [ ] PART_OF transitive closure bounded (max depth 5)
- [ ] POSITION_HELD has P580/P582 qualifiers where available
- [ ] Neo4j indexes on relationship types for traversal