# Chrystallum Data Dictionary

**Created:** February 21, 2026
**Revised:** March 6, 2026
**Status:** Living Document
**Version:** 2.0
**Source of truth:** `Key Files/chrystallum_architecture.jsx` (logical architecture diagram, 2026-03-03)
**Cross-referenced against:** Live Neo4j graph via MCP, codebase (`scripts/tools/entity_cipher.py`, `scripts/federation/federation_scorer.py`, `Python/models/canonicalization.py`)

---

## 1. Introduction

### 1.1 Purpose

This data dictionary documents all data elements in the Chrystallum knowledge graph: node labels, properties, relationship types, controlled vocabularies, cipher architecture, federation scoring, and claim lifecycle. Every definition is grounded in the live graph, not aspirational design.

### 1.2 Scope

- Domain node types: Person, Place, SubjectConcept, Event, and supporting clusters
- System (SYS_*) self-describing governance nodes
- Claim and provenance layer (Claim, ScaffoldNode, ScaffoldEdge, ConflictNote)
- 290+ relationship types (registered in SYS_RelationshipType)
- Three-tier cipher architecture (entity, faceted, claim)
- Federation scoring (weighted 0-100, states FS0-FS3)
- Controlled vocabularies and registries
- 17 federation sources

### 1.3 Related Documents

| Document | What it covers |
|----------|---------------|
| `Key Files/chrystallum_architecture.jsx` | Logical architecture diagram (source of truth) |
| `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md` | Per-node property tables from loaders |
| `docs/architecture/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` | Three-tier cipher specification |
| `Key Files/Appendices/05_Architecture_Decisions/ADR_001_*` | Claim identity ciphers |
| `Key Files/Appendices/05_Architecture_Decisions/ADR_006_*` | Bootstrap scaffold contract |
| `md/Architecture/ADR-013-*` | Hardcoded rules to decision tables |
| `Key Files/Appendices/05_Architecture_Decisions/ADR_014_*` | Domain quality matrix |

### 1.4 Conventions

- `attribute_name` - Property name as stored in Neo4j
- **Bold** = Required (NOT NULL)
- *Italic* = Computed/derived
- Data types: String, Integer, Float, DateTime (ISO 8601), Enum, QID (Q + digits), PID (P + digits)

---

## 2. Graph Summary (Live)

| Metric | Value |
|--------|-------|
| Total nodes | ~105,600 |
| Distinct node labels | 82 |
| Distinct relationship types | 290+ |
| Federation sources | 17 (6 operational, 2 partial, 1 blocked, 8 planned) |
| Confidence thresholds | 0.75 (review) / 0.90 (promotion) |

---

## 3. Domain Layer — Node Types

### 3.1 Person Cluster

#### :Person

**Count:** 5,248
**Primary Key:** `entity_id` (e.g., `person_q1048`)
**Created By:** Person harvest pipeline (Layer 1 + Layer 3)

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| **entity_id** | String | YES | Graph primary key | `person_q1048` |
| **qid** | QID | YES | Wikidata identifier | `Q1048` |
| **entity_type** | Enum | YES | Always `PERSON` | `PERSON` |
| entity_cipher | String | NO | Tier 1 cross-subgraph join key | `ent_per_Q1048` |
| label | String | NO | English display label | `Julius Caesar` |
| label_latin | String | NO | Latin name form | `Gaius Iulius Caesar` |
| label_dprr | String | NO | DPRR canonical form | `Iulius (Re 131) C. Caesar` |
| label_sort | String | NO | Sort key | `Iulius Caesar, C.` |
| dprr_id | String | NO | DPRR person ID | `1058` |
| dprr_uri | String | NO | Full DPRR URI | `https://romanrepublic.ac.uk/person/1058` |
| dprr_imported | Boolean | NO | Whether DPRR data loaded | `true` |
| viaf_id | String | NO | VIAF cluster ID | `86013533` |
| lcnaf_id | String | NO | LC Name Authority File ID | `n80126218` |
| ocd_id | String | NO | Oxford Classical Dictionary ID | |
| gnd_id | String | NO | German National Library ID | |
| nomisma_id | String | NO | Numismatic authority ID | |
| birth_date | String | NO | ISO 8601 (BCE negative) | `-0100-07-12` |
| birth_year | Integer | NO | Year only (BCE negative) | `-100` |
| birth_place_qid | QID | NO | Place of birth | `Q220` |
| death_date | String | NO | ISO 8601 | `-0044-03-15` |
| death_year | Integer | NO | Year only | `-44` |
| death_place_qid | QID | NO | Place of death | `Q220` |
| cause_of_death_qid | QID | NO | Manner/cause | `Q3882219` |
| burial_place_qid | QID | NO | Burial location | |
| floruit_start | Integer | NO | Active period start year | `-70` |
| floruit_end | Integer | NO | Active period end year | `-44` |
| floruit_derived | Boolean | NO | Whether floruit was computed | `true` |
| bio_harvested_at | DateTime | NO | When bio harvest ran | |
| subject_candidate | Boolean | NO | Flagged as potential SubjectConcept | |
| subject_candidate_sources | String | NO | Why flagged | |
| created_at | DateTime | NO | Creation timestamp | |

**Key relationships:**
- `MEMBER_OF_GENS → :Gens` (4,840 edges)
- `HAS_NOMEN → :Nomen` (4,619)
- `HAS_COGNOMEN → :Cognomen` (3,882)
- `HAS_PRAENOMEN → :Praenomen` (3,670)
- `MEMBER_OF_TRIBE → :Tribe` (353)
- `CITIZEN_OF → :Polity / :HistoricalPolity` (5,243)
- `POSITION_HELD → :Position` (7,342)
- `FATHER_OF / MOTHER_OF / CHILD_OF / SIBLING_OF / SPOUSE_OF` (family)
- `BORN_IN_YEAR / DIED_IN_YEAR → :Year`
- `BORN_IN_PLACE / DIED_IN_PLACE → :Place`
- `ACTIVE_IN_YEAR → :Year` (18,217)
- `DESCRIBED_BY_SOURCE → :WorldCat_Work` (3,630)
- `PARTICIPATED_IN → :Event` (201)

#### :MythologicalPerson

**Count:** 3
Same properties as `:Person`. Dual-labeled `:Person:MythologicalPerson`.

#### Supporting onomastic nodes

| Label | Count | Primary Key | Key Properties |
|-------|-------|-------------|----------------|
| :Gens | 585 | `gens_id` | `name`, `qid`, `nomen` |
| :Nomen | 917 | `nomen_id` | `name`, `qid` |
| :Cognomen | 1,000 | `cognomen_id` | `name`, `qid` |
| :Praenomen | 24 | `praenomen_id` | `name`, `abbreviation`, `qid` |
| :Tribe | 29 | `tribe_id` | `name`, `qid` |

---

### 3.2 Place Cluster

#### :Place

**Count:** 44,060
**Primary Key:** `place_id` or `qid`

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| **qid** | QID | YES* | Wikidata QID (*some Pleiades-only) | `Q220` |
| pleiades_id | String | NO | Pleiades gazetteer ID | `423025` |
| tgn_id | String | NO | Getty TGN ID | |
| geonames_id | String | NO | GeoNames ID | |
| geonames_feature_code | String | NO | Feature classification | |
| label | String | NO | Display name | `Rome` |
| description | String | NO | Short description | |
| place_type | String | NO | Classification | `settlement` |
| lat | Float | NO | Latitude | `41.8919` |
| long | Float | NO | Longitude | `12.5113` |
| bbox | String | NO | Bounding box | |
| min_date | Integer | NO | Earliest attestation year | `-753` |
| max_date | Integer | NO | Latest attestation year | `2026` |
| federation_score | Integer | NO | Weighted 0-100 | `85` |
| federation_state | String | NO | FS0-FS3 state | `FS3_WELL_FEDERATED` |
| federation_cipher_key | String | NO | `fed_` + SHA256[:16] | `fed_a1b2c3d4e5f6g7h8` |
| vertex_jump_enabled | Boolean | NO | Can agents vertex-jump? | `true` |

**Key relationships:**
- `ALIGNED_WITH_GEO_BACKBONE → :Pleiades_Place` (32,480)
- `LOCATED_IN → :Place` (3,380)
- `BORDERS → :Place` (1,223)
- `CONTROLLED_BY → :Polity` (1,191)
- `CONTAINS → :Place` (1,526)
- `IN_PERIOD → :Periodo_Period` (105)

#### :Pleiades_Place

**Count:** 32,572
Ancient world gazetteer nodes. Linked to `:Place` via `ALIGNED_WITH_GEO_BACKBONE`.

---

### 3.3 Knowledge / Taxonomy Cluster

| Label | Count | Primary Key | Description |
|-------|-------|-------------|-------------|
| :SubjectConcept | 30 | `entity_id` / `subject_id` | Research domain anchors (e.g., Q17167 Roman Republic) |
| :Discipline | 1,363 | `discipline_id` | Academic discipline ontology |
| :LCC_Class | 4,490 | `lcc_id` | Library of Congress Classification nodes |
| :Periodo_Period | 1,118 | `periodo_id` | PeriodO temporal period authority |
| :LCSH_Heading | 15 | `lcsh_id` | Library of Congress Subject Headings |
| :WorldCat_Work | 196 | `work_id` | Bibliographic works |
| :Year | 4,030 | `year` | Calendar year nodes for temporal indexing |
| :Position | 171 | `position_id` | Political/religious offices (consul, tribune, etc.) |
| :Facet | 18 | `facet_id` | 18 canonical facets |
| :Event | 57 | `event_id` / `qid` | Historical events |
| :Polity | 10 | `polity_id` | Political entities |
| :HistoricalPolity | 9 | `polity_id` | Time-bounded political entities |
| :Religion | 12 | `religion_id` | Religious traditions |

#### :SubjectConcept Properties

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| **entity_id** | String | Primary key | `subjectconcept_q17167` |
| **qid** | QID | Wikidata QID | `Q17167` |
| subject_id | String | Subject identifier | |
| entity_type | Enum | Always `SUBJECTCONCEPT` | |
| label | String | Display name | `Roman Republic` |
| entity_cipher | String | Tier 1 cipher | `ent_sub_Q17167` |
| primary_facet | String | Dominant facet | `POLITICAL` |
| secondary_facets | List | Supporting facets | `["MILITARY","SOCIAL"]` |
| federation_score | Integer | Weighted 0-100 | |
| namespace | Enum | Authority source | `wd` |
| temporal_start | Integer | Period start (BCE neg) | `-509` |
| temporal_end | Integer | Period end (BCE neg) | `-27` |
| temporal_bucket | String | Classification | |
| sca_confidence | Float | SCA assessment [0-1] | `0.92` |
| properties_count | Integer | WD property count | `61` |
| viaf_id | String | VIAF ID | |
| pleiades_id | String | Pleiades ID | |
| getty_aat_id | String | Getty AAT ID | |
| capability_cipher | String | Computed cipher | |
| discovered_from | String | Discovery source | |
| imported_at | DateTime | Import timestamp | |
| promoted_at | DateTime | Promotion timestamp | |
| promoted_by | String | Promoting agent | |

---

## 4. System Layer — SYS_* Nodes (Self-Describing Graph)

The system layer makes the graph self-describing. Agents read these nodes to understand schema, policies, and thresholds without external documentation.

| Label | Count | Purpose |
|-------|-------|---------|
| SYS_FederationSource | 17 | Registered external authority databases |
| SYS_AuthorityTier | 6 | Authority weighting tiers |
| SYS_ConfidenceTier | 8 | Confidence level classifications |
| SYS_DecisionTable | 21 | DMN-style decision tables |
| SYS_DecisionRow | 128 | Individual decision rules |
| SYS_Policy | 16 | Active governance policies |
| SYS_Threshold | 25 | Numeric thresholds (confidence, scoring, etc.) |
| SYS_RelationshipType | 98 | Registered relationship types with domain/range |
| SYS_NodeType | 43 | Registered node types |
| SYS_PropertyMapping | 500 | Property-to-facet routing mappings |
| SYS_ValidationRule | 12 | Schema validation rules |
| SYS_WikidataProperty | 55 | Wikidata PID registry |
| SYS_ClaimStatus | 10 | Claim lifecycle states |
| SYS_RejectionReason | 8 | Standardized rejection codes |
| SYS_ADR | 8 | Architecture Decision Records (in-graph) |
| SYS_OnboardingStep | 26 | Agent onboarding protocol steps |
| SYS_OnboardingProtocol | 2 | Onboarding protocol definitions |
| SYS_QueryPattern | 5 | Canonical query patterns |
| SYS_AgentType | 5 | Registered agent types |
| SYS_SchemaRegistry | 1 | Schema root node |
| SYS_FederationRegistry | 1 | Federation root node |
| SYS_HarvestPlan | 1 | Harvest plan audit trail |
| SYS_SchemaBootstrap | 1 | Bootstrap metadata |
| SYS_FacetPolicy | 3 | Facet-specific policies |
| SYS_AnchorTypeMapping | 9 | P31 anchor type mappings |
| SYS_ClassificationTier | 4 | Classification level definitions |
| SYS_ConfidenceModifier | 7 | Confidence adjustment rules |
| SYS_EdgeType | 8 | Edge type classifications |
| SYS_ClassificationAlgorithm | 1 | Algorithm metadata |

---

## 5. Claim & Provenance Layer

### 5.1 :Claim

**Count:** 1 (early stage)
**Primary Key:** `claim_id`

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| **claim_id** | String | Unique claim identifier | |
| **cipher** | String | Content-addressable SHA256 hash (64 hex chars, no prefix) | `b22020c0a1...` |
| **text** | String | Claim text | |
| label | String | Short label | |
| confidence | Float | Score [0.0, 1.0] | `0.95` |
| status | Enum | Lifecycle state (see 5.2) | `proposed` |
| review_status | String | Human review state | |
| reviewer | String | Human reviewer ID | |
| claim_type | String | Classification | |
| authority_source | String | Source authority | |
| source_agent | String | Agent that created claim | |
| is_exemplar | Boolean | Template claim? | |
| promoted_at | DateTime | Promotion timestamp | |
| cipher_note | String | Cipher computation notes | |
| timestamp | DateTime | Creation time | |
| updated | DateTime | Last update | |

### 5.2 Claim Status Lifecycle (SYS_ClaimStatus)

10 states registered in graph:

| Status | Description | Transitions To |
|--------|-------------|---------------|
| `proposed` | Agent created claim with cipher, text, confidence, provenance | `needs_provenance`, `under_review`, `rejected_low_confidence` |
| `needs_provenance` | Meets threshold but lacks RetrievalContext | `under_review` |
| `under_review` | Being evaluated by D10 decision table and/or human | `reviewed_approved`, `reviewed_rejected` |
| `reviewed_approved` | Human approved, ready for promotion | `promoted` |
| `reviewed_rejected` | Human rejected | (terminal) |
| `promoted` | First-class edge materialized (ProposedEdge) | `superseded`, `retracted` |
| `rejected_low_confidence` | Below threshold, agent may retry | `proposed` |
| `rejected_human` | Explicitly rejected by human | (terminal) |
| `superseded` | Replaced by higher-confidence claim | (terminal) |
| `retracted` | Agent or human retracted (incorrect) | (terminal) |

### 5.3 Provenance Nodes

| Label | Purpose |
|-------|---------|
| ScaffoldNode | Stub node placeholder (ADR-006) |
| ScaffoldEdge | Stub edge with `FROM`/`TO` + `dprr_assertion_uri` provenance |
| ProposedEdge | Edge proposed by claim promotion |
| ConflictNote | Structured conflict documentation |
| FacetAssessment | Per-entity facet evaluation record |

---

## 6. Controlled Vocabularies

### 6.1 Entity Type Registry

**Registry Name:** `ENTITY_TYPE_PREFIXES`
**Source:** `scripts/tools/entity_cipher.py`
**Status:** LOCKED (10 types)

| Entity Type | Prefix | Description | Example QID |
|-------------|--------|-------------|-------------|
| PERSON | per | Individual human | Q1048 |
| EVENT | evt | Historical event | Q25238182 |
| PLACE | plc | Geographic location | Q220 |
| SUBJECTCONCEPT | sub | Subject/topic/period | Q17167 |
| WORK | wrk | Creative work | Q644312 |
| ORGANIZATION | org | Organized group | Q193236 |
| PERIOD | prd | Time period | Q17167 |
| MATERIAL | mat | Substance/material | Q753 |
| OBJECT | obj | Physical object | Q34379 |
| CONCEPT | con | Abstract concept | |

**Cipher format:** `ent_{prefix}_{qid}` (e.g., `ent_per_Q1048`)

### 6.2 Facet Registry (18 Canonical Facets)

**Registry Name:** `FACET_PREFIXES`
**Source:** `scripts/tools/entity_cipher.py`
**Status:** LOCKED (18 facets, ADR-004)
**Graph nodes:** 18 `:Facet` nodes

| Facet | Prefix | Description |
|-------|--------|-------------|
| ARCHAEOLOGICAL | arc | Excavations, artifacts, sites |
| ARTISTIC | art | Sculpture, painting, architecture |
| BIOGRAPHIC | bio | Birth, death, family, career |
| COMMUNICATION | com | Writing systems, media, signals |
| CULTURAL | cul | Customs, traditions, rituals |
| DEMOGRAPHIC | dem | Census, migration, demographics |
| DIPLOMATIC | dip | Treaties, embassies, negotiations |
| ECONOMIC | eco | Trade, currency, taxation |
| ENVIRONMENTAL | env | Climate, geography, resources |
| GEOGRAPHIC | geo | Locations, coordinates, borders |
| INTELLECTUAL | int | Ideas, philosophy, scholarship |
| LINGUISTIC | lin | Grammar, vocabulary, dialects |
| MILITARY | mil | Battles, ranks, strategy |
| POLITICAL | pol | Offices, laws, institutions |
| RELIGIOUS | rel | Deities, rituals, theology |
| SCIENTIFIC | sci | Discovery, methods, theories |
| SOCIAL | soc | Class, kinship, status |
| TECHNOLOGICAL | tec | Inventions, techniques, tools |

**Faceted cipher format:** `fent_{prefix}_{qid}_{subjectconcept_qid}` (e.g., `fent_pol_Q1048_Q17167`)

### 6.3 Cipher-Eligible Qualifiers

**Registry Name:** `CIPHER_ELIGIBLE_QUALIFIERS`
**Source:** `scripts/tools/entity_cipher.py`
**Status:** LOCKED (5 qualifiers)

| PID | Label | W5H1 | Purpose | Example |
|-----|-------|------|---------|---------|
| P580 | start time | WHEN | Temporal identity (1st vs 2nd consulship) | `-59` |
| P582 | end time | WHEN | Temporal bounds | `-58` |
| P585 | point in time | WHEN | Specific date assertions | `-0044-03-15` |
| P276 | location | WHERE | Spatial identity | `Q220` |
| P1545 | series ordinal | WHICH | Instance identity (1st, 2nd, 3rd) | `1` |

### 6.4 Namespace

| Value | Authority | QID format |
|-------|-----------|------------|
| `wd` | Wikidata (primary) | `Q` + digits |
| `bn` | BabelNet | `bn:` + id |
| `crys` | Chrystallum synthetic | `crys:` + hash |

---

## 7. Cipher Architecture

Three tiers, per ADR-001:

### 7.1 Tier 1 — Entity Cipher

**Function:** `generate_entity_cipher(resolved_id, entity_type, namespace)`
**Format:** `ent_{type_prefix}_{resolved_id}`
**Purpose:** Cross-subgraph join key, O(1) deduplication
**Example:** `ent_per_Q1048`

Note: The live graph uses `entity_id` (e.g., `person_q1048`) as the Neo4j primary key. `entity_cipher` is an additional content-addressable property for cross-federation merge.

### 7.2 Tier 2 — Faceted Cipher

**Function:** `generate_faceted_cipher(entity_cipher, facet_id, subjectconcept_id)`
**Format:** `fent_{facet_prefix}_{qid}_{subjectconcept_qid}`
**Purpose:** Subgraph address for vertex jumps
**Example:** `fent_pol_Q1048_Q17167`

### 7.3 Tier 3 — Claim Cipher

**Function:** `compute_claim_cipher(content, metadata)` in `Python/models/canonicalization.py`
**Format:** 64-character hex SHA256 digest (no prefix)
**Purpose:** Content-addressable assertion identity
**Process:**
1. Canonicalize content (NFC Unicode, whitespace normalization)
2. Canonicalize metadata (sorted keys, float precision, datetime normalization)
3. Serialize to canonical JSON
4. SHA256 hash → hex digest

### 7.4 Edge Cipher

**Format:** SHA256(`source_entity_id` | `rel_type` | `target_entity_id`)[:16]
**Purpose:** Idempotent MERGE operations

---

## 8. Federation Scoring

**Source:** `scripts/federation/federation_scorer.py`
**System:** Weighted 0-100 point scoring with 4 states

### 8.1 Weight Table

| Component | Weight | Description |
|-----------|--------|-------------|
| place_qid | 30 | Place federated to Wikidata |
| period_qid | 30 | Period federated to Wikidata |
| geo_context_qid | 20 | Geographic context federated |
| temporal_bounds | 15 | Temporal signal present |
| relationships | 5 | Vertex jump edges exist |

### 8.2 Federation States

| State | Range | Vertex Jump |
|-------|-------|-------------|
| FS0_UNFEDERATED | 0-39 | No |
| FS1_BASE | 40-59 | No |
| FS2_FEDERATED | 60-79 | Conditional |
| FS3_WELL_FEDERATED | 80-100 | Yes |

### 8.3 Federation Sources (17 registered)

| Source | Status | Scoping Weight | Property in graph |
|--------|--------|---------------|-------------------|
| Wikidata | operational | 1.00 | `qid` |
| Pleiades | operational | 0.92 | `pleiades_id` |
| PeriodO | operational | 0.85 | `periodo_id` |
| LCSH/FAST/LCC | operational | 0.90 | `lcsh_id`, `fast_id`, `lcc_id` |
| Trismegistos | operational | 0.95 | `trismegistos_id` |
| LGPN | operational | 0.93 | `lgpn_id` |
| VIAF | partial | 0.85 | `viaf_id` |
| Getty AAT | partial | 0.90 | `getty_aat_id` |
| DPRR | blocked (snapshot) | 0.85 | `dprr_id` |
| Nomisma | planned | — | `nomisma_id` |
| OCD | planned | — | `ocd_id` |
| OpenAlex | planned | — | — |
| Open Library | planned | — | — |
| Open Syllabus | planned | — | — |
| Perseus | planned | — | — |
| CHRR | planned | — | — |
| CRRO | planned | — | — |

---

## 9. Relationship Types (Top 50 by Edge Count)

| Relationship | Count | Domain → Range |
|-------------|-------|---------------|
| ALIGNED_WITH_GEO_BACKBONE | 32,480 | Place → Pleiades_Place |
| ACTIVE_IN_YEAR | 18,217 | Person → Year |
| POSITION_HELD | 7,342 | Person → Position |
| CITIZEN_OF | 5,243 | Person → Polity |
| MEMBER_OF_GENS | 4,840 | Person → Gens |
| HAS_NOMEN | 4,619 | Person → Nomen |
| BIO_CANDIDATE_REL | 4,346 | Person → Entity |
| BROADER_THAN | 4,154 | LCC_Class → LCC_Class |
| FOLLOWED_BY | 4,152 | Year → Year |
| HAS_COGNOMEN | 3,882 | Person → Cognomen |
| HAS_PRAENOMEN | 3,670 | Person → Praenomen |
| DESCRIBED_BY_SOURCE | 3,630 | Person → WorldCat_Work |
| LOCATED_IN | 3,380 | Place → Place |
| CHILD_OF | 2,711 | Person → Person |
| SIBLING_OF | 2,162 | Person → Person |
| INSTANCE_OF | 2,122 | Entity → EntityType |
| FATHER_OF | 2,122 | Person → Person |
| HAS_STATUS | 1,919 | various |
| DIPLOMATIC_RELATION | 1,726 | Place → Place |
| CONTAINS | 1,526 | Place → Place |
| BORN_IN_YEAR | 1,301 | Person → Year |
| BORN_IN_PLACE | 1,261 | Person → Place |
| BORDERS | 1,223 | Place → Place |
| CONTROLLED_BY | 1,191 | Place → Polity |
| DIED_IN_YEAR | 1,110 | Person → Year |
| DISCIPLINE_SUBCLASS_OF | 998 | Discipline → Discipline |
| DISCIPLINE_BROADER_THAN | 726 | Discipline → Discipline |
| SPOUSE_OF | 634 | Person → Person |
| MOTHER_OF | 589 | Person → Person |
| HAS_PRIMARY_FACET | 500 | SYS_PropertyMapping → Facet |
| SUB_PERIOD_OF | 490 | Periodo_Period → Periodo_Period |
| DIFFERENT_FROM | 481 | Entity → Entity |
| GENDER | 436 | Person → (value) |
| CONTAINS_PERIOD | 435 | Periodo_Period → Periodo_Period |
| DIED_IN | 408 | Person → Place |
| MEMBER_OF | 396 | Person → Organization |
| DISCIPLINE_HAS_PART | 372 | Discipline → Discipline |
| TYPE_OF | 361 | various |
| MEMBER_OF_TRIBE | 353 | Person → Tribe |
| ADMINISTRATIVE_PART_OF | 353 | Place → Place |
| COLLABORATOR_OF | 330 | Person → Person |
| MAINTAINED_BY_WIKIPROJECT | 312 | various |
| LOCATED_IN_CONTINENT | 278 | Place → (value) |
| SPOKE_LANGUAGE | 248 | Person → (value) |
| DIED_IN_PLACE | 231 | Person → Place |
| PARTICIPATED_IN | 201 | Person → Event |
| BORN_IN | 200 | Person → Place |
| HAS_SECONDARY_FACET | 195 | SYS_PropertyMapping → Facet |
| TWINNED_ADMINISTRATIVE_BODY | 172 | Place → Place |
| LANGUAGE_OF_WORK_OR_NAME | 172 | Work → (value) |

Full list: 290+ types. Query `SYS_RelationshipType` for the registered subset with domain/range constraints.

---

## 10. Data Quality Rules

### 10.1 Uniqueness Constraints

```yaml
UC-01: entity_id unique per label
UC-02: entity_cipher unique (when present)
UC-03: claim cipher unique (content-addressable)
```

### 10.2 Data Type Constraints

```yaml
DT-01: confidence MUST be Float in [0.0, 1.0]
DT-02: QID fields MUST match ^Q\d+$
DT-03: PID fields MUST match ^P\d+$
DT-04: Temporal fields MUST be ISO 8601 or BCE-offset integer
DT-05: federation_score MUST be Integer in [0, 100]
DT-06: federation_state MUST be one of {FS0_UNFEDERATED, FS1_BASE, FS2_FEDERATED, FS3_WELL_FEDERATED}
```

### 10.3 Business Rules

```yaml
BR-01: Entity Cipher Format
  entity_cipher MUST match: ^ent_(per|evt|plc|sub|wrk|org|prd|mat|obj|con)_(Q\d+|bn:.+|crys:.+)$

BR-02: Faceted Cipher Format
  faceted_cipher MUST match: ^fent_(arc|art|bio|com|cul|dem|dip|eco|env|geo|int|lin|mil|pol|rel|sci|soc|tec)_Q\d+_Q\d+$

BR-03: Claim Cipher Determinism
  Same input MUST produce same 64-char hex SHA256 digest

BR-04: Promotion Threshold
  Claim promotion requires confidence >= 0.90

BR-05: Review Threshold
  Claims with confidence >= 0.75 enter under_review

BR-06: Agent Write Prohibition (Layer 2)
  LLM agents CANNOT write to graph — deterministic Layer 3 executes all writes
```

---

## 11. Architecture Layers

Per `chrystallum_architecture.jsx`:

| Layer | Name | Type | Description |
|-------|------|------|-------------|
| 0 | Federation Sources | External | 17 registered authorities |
| 1 | Harvest Pipeline | Deterministic | DPRR parser, P-code mapper, date normaliser, backlink capture, QID validator, context packet assembler |
| 2 | Agent Reasoning | LLM-orchestrated | Cross-federation reconciliation, conflict classification, filiation disambiguation. **Never writes to graph.** |
| 3 | Deterministic Execution | Schema-validated Cypher | 13-step idempotent sequence, ADR-006 ScaffoldNode/ScaffoldEdge compliant |
| — | Neo4j Graph | Storage | Single source of truth |
| — | Query & Access | Read | MCP, Neo4j Browser/Bloom, planned React UI, planned GEDCOM 7.0 export |

---

## 12. Sample Queries (Working)

**Find a Person with all onomastic parts:**
```cypher
MATCH (p:Person {qid: 'Q1048'})
OPTIONAL MATCH (p)-[:MEMBER_OF_GENS]->(g:Gens)
OPTIONAL MATCH (p)-[:HAS_PRAENOMEN]->(pr:Praenomen)
OPTIONAL MATCH (p)-[:HAS_NOMEN]->(n:Nomen)
OPTIONAL MATCH (p)-[:HAS_COGNOMEN]->(c:Cognomen)
RETURN p.label, pr.name, n.name, g.name, c.name;
```

**Vertex jump via entity_cipher:**
```cypher
MATCH (p:Person {entity_cipher: 'ent_per_Q1048'})
RETURN p.label, p.entity_id, p.qid;
```

**All positions held by a person:**
```cypher
MATCH (p:Person {qid: 'Q1048'})-[:POSITION_HELD]->(pos:Position)
RETURN p.label, pos.label;
```

**Federation state of a place:**
```cypher
MATCH (pl:Place {qid: 'Q220'})
RETURN pl.label, pl.federation_score, pl.federation_state, pl.vertex_jump_enabled;
```

**Walk claim lifecycle:**
```cypher
MATCH (s:SYS_ClaimStatus)
OPTIONAL MATCH (s)-[:CAN_TRANSITION_TO]->(t:SYS_ClaimStatus)
RETURN s.status, s.description, collect(t.status) AS transitions
ORDER BY s.order;
```

---

## 13. Change History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-21 | 1.0 | Initial backfill from architecture (Requirements Analyst Agent) |
| 2026-03-06 | 2.0 | Complete rewrite from .jsx + live graph + codebase. Removed phantom `:FacetedEntity`/`:FacetClaim` sections. Added Person/Place/SubjectConcept actual properties. Added SYS_* layer. Fixed federation scoring (weighted 0-100, not COUNT 1-6). Fixed claim lifecycle (10 states from SYS_ClaimStatus). Fixed entity type count (10, not 9). Added relationship type inventory. Added architecture layers. |

---

## Appendix A: Documents Recommended for Archive

The following documents contain information that is stale, superseded, or contradicts the live graph. They should be moved to `docs/archive/` to prevent confusion.

### Superseded by this Data Dictionary (v2.0)

| File | Why archive |
|------|-------------|
| `docs/architecture/COMPREHENSIVE_NODE_TYPES_2026-02-19.md` | Pre-DPRR node type list; counts and labels are wrong |
| `docs/architecture/NODE_ALIGNMENT_ISSUES_2026-02-19.md` | Issues documented here have been resolved |
| `docs/architecture/SYSTEM_SUBGRAPH_ARCHITECTURE_2026-02-19.md` | SYS layer has evolved significantly; counts/structure outdated |
| `docs/architecture/CHRYSTALLUM_SYSTEM_VISUALIZATION_2026-02-19.md` | Superseded by `chrystallum_architecture.jsx` (2026-03-03) |
| `docs/architecture/COMPLETE_PROPERTY_OUTLINE_SUMMARY.md` | Property list predates Person domain (ADR-007) |
| `docs/architecture/COMPREHENSIVE_DISCOVERY_SUMMARY.md` | Early exploration notes, no longer actionable |
| `docs/architecture/CSV_ANALYSIS_READY.md` | One-time analysis artifact |

### Superseded by Live Graph / Decision Tables

| File | Why archive |
|------|-------------|
| `docs/architecture/ARCHITECTURE_ISSUE_HARDCODED_RELATIONSHIPS.md` | Issue resolved — relationships now from SYS_RelationshipType registry |
| `docs/architecture/NEO4J_IMPORTER_PLAN.md` | Importer built and running; plan is stale |
| `docs/architecture/DEV_INSTRUCTIONS_WIKIDATA_COMPREHENSIVE_IMPORT.md` | Import pipeline changed; these instructions would cause errors |
| `docs/architecture/INTEGRATION_AGENT_PLAN.md` | Early agent design; superseded by 3-layer architecture |
| `docs/architecture/PM_PLAN_REVISED_AI_DRIVEN_2026-02-20.md` | Project plan from week 1; milestones have shifted |
| `docs/architecture/REQUIREMENTS_ANALYST_INTRODUCTION.md` | One-time session artifact |

### Superseded by Specific ADRs or Newer Specs

| File | Why archive | Superseded by |
|------|-------------|---------------|
| `docs/architecture/MULTI_FACTOR_PROPERTY_ROUTING.md` | Property routing now via SYS_PropertyMapping | Decision tables |
| `docs/architecture/TAXONOMY_HARVESTER_AGENT_SPEC.md` | SCA design evolved past this spec | SCA_SFA_CONTRACT.md |
| `docs/architecture/IMMEDIATE_SUBJECT_CONCEPTS_AND_SFAS.md` | Early SFA design | SCA_SFA_CONTRACT.md |
| `docs/architecture/QID_TO_SFA_LEARNING_FLOW.md` | Flow diagram for old pipeline | 3-layer architecture |
| `docs/architecture/D9_SFA_CONSTITUTION_SPEC.md` | SFA spec v1 | SCA_SFA_CONTRACT.md + ADR-004 |
| `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md` | v1 of self-describing design | `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN_2026-02-25.md` |
| `docs/architecture/BA_SELF_DESCRIBING_SYSTEM_ANALYSIS.md` | Analysis leading to v2 | v2 design doc |

### Session / Handoff Artifacts (Historical, Not Reference)

| File | Why archive |
|------|-------------|
| `docs/ADVISOR_HANDOFF_2026-02-25.md` | Point-in-time handoff |
| `docs/BASELINE_POST_DPRR_2026-02-25.md` | Snapshot baseline; graph has grown 3x since |
| `docs/HANDOFF_2026-02-26.md` | Point-in-time handoff |
| `docs/HANDOFF_TO_HUB_DEV_2026-03-03.md` | Point-in-time handoff |
| `docs/OCD_INTEGRATION_NOTES_2026-02-25.md` | Session notes |
| `docs/SFA_CONSTITUTION_NOTES_2026-02-25.md` | Session notes |
| `docs/sessions/FEDERATION_POSITIONING_VERIFICATION_2026-02-26.md` | Verification run artifact |
| `docs/project-management/PM_COMPREHENSIVE_PLAN_2026-02-20.md` | Week-1 PM plan |
| `docs/project-management/PROJECT_PLAN_2026-02-20.md` | Week-1 PM plan |
| `docs/project-management/QA_RESULTS_SUMMARY.md` | One-time QA run |
| `docs/architecture/QA_HANDOFF_NEO4J_TESTING.md` | One-time QA handoff |
| `docs/architecture/QA_QUICK_START.md` | Early QA setup |
| `docs/architecture/QA_TEST_REPORT.md` | Early QA report |

### Duplicated or Exploration Artifacts

| File | Why archive |
|------|-------------|
| `docs/architecture/3HOP_VISUAL_SUMMARY.md` | Exploration artifact |
| `docs/architecture/5HOP_COMPLETE_TAXONOMY.md` | Exploration artifact |
| `docs/architecture/5HOP_EXPLORATION_COMPLETENESS.md` | Exploration artifact |
| `docs/architecture/ROMAN_REPUBLIC_2HOP_TAXONOMY.md` | Exploration artifact |
| `docs/architecture/ROMAN_REPUBLIC_Q17167_COMPLETE_PROPERTIES.md` | Exploration artifact |
| `docs/architecture/ROMAN_REPUBLIC_TAXONOMY_ANALYSIS.md` | Exploration artifact |
| `docs/architecture/COMPLETE_3HOP_TAXONOMY_ANALYSIS.md` | Exploration artifact |
| `docs/architecture/COMPLETE_SUCCESSION_CHAIN.md` | Exploration artifact |
| `docs/architecture/GEOGRAPHIC_AND_PERIODO_ANALYSIS.md` | Exploration artifact |
| `docs/architecture/HISTORICAL_PERIODS_TREE_CHART.md` | Exploration artifact |
| `docs/architecture/HISTORICAL_PERIOD_BACKLINKS_ANALYSIS.md` | Exploration artifact |
| `docs/architecture/89_HISTORICAL_PERIODS_COMPLETE_CHART.md` | Exploration artifact |
| `docs/architecture/12_FAILED_PERIODS_TEMPORAL_DATA.md` | Exploration artifact |
| `docs/architecture/P2184_HISTORY_OF_TOPIC_DISCOVERY.md` | Exploration artifact |
| `docs/architecture/PERIODO_PLEIADES_COMPARISON.md` | Exploration artifact |
| `docs/architecture/RELIGIOUS_FACET_BACKLINKS.md` | Exploration artifact |
| `docs/architecture/Q17167_10_FACETS_CONFIRMED_WITH_LABELS.md` | Exploration artifact |
| `docs/architecture/Q17167_FACET_MAPPING.md` | Exploration artifact |
| `docs/architecture/COMMONS_CATEGORY_INDEX_ANALYSIS.md` | Exploration artifact |
| `docs/architecture/PROPERTY_DOMAIN_UTILITY_ANALYSIS.md` | Exploration artifact |
| `docs/architecture/PROPERTY_MAPPING_ANALYSIS.md` | Exploration artifact |
| `docs/architecture/PROPERTY_MAPPING_IMPACT.md` | Exploration artifact |

### Summary

| Category | Count |
|----------|-------|
| Superseded by this data dictionary | 7 |
| Superseded by live graph / decision tables | 6 |
| Superseded by ADRs / newer specs | 7 |
| Session / handoff artifacts | 13 |
| Exploration artifacts | 22 |
| **Total recommended for archive** | **55** |
| **Remaining active docs (of 117)** | **~62** |

---

**Last updated:** March 6, 2026
