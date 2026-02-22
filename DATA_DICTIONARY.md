# Chrystallum Data Dictionary

**Document Owner:** Requirements Analyst Agent  
**Created:** February 21, 2026  
**Status:** Living Document (Backfilled from existing architecture)  
**Version:** 1.0

---

## 1. Introduction

### 1.1 Purpose
This data dictionary documents all data elements in the Chrystallum knowledge graph system, including entities, relationships, attributes, controlled vocabularies, and data lineage.

### 1.2 Scope
- Core entities (Entity, FacetedEntity, FacetClaim, SubjectConcept)
- Specialized entity types (Person, Place, Event, etc.)
- Relationship types (311 canonical types)
- Controlled vocabularies and registries
- Authority sources and data lineage
- Data quality rules and constraints

### 1.3 Related Documents
- `ARCHITECTURE_CORE.md` - System architecture overview
- `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` - Three-tier cipher specification
- `CLAIM_ID_ARCHITECTURE.md` - Claim cipher details
- `ARCHITECTURE_ONTOLOGY.md` - Ontology layer specifications

### 1.4 Conventions

**Attribute Notation:**
- `attribute_name` - Property name as stored in Neo4j
- **Bold** = Required field (NOT NULL)
- *Italic* = Computed/derived field

**Data Types:**
- String - Variable length text
- Integer - Whole numbers
- Float - Decimal numbers
- DateTime - ISO 8601 timestamp
- Enum - Controlled vocabulary
- QID - Wikidata identifier (Q + digits)
- PID - Wikidata property identifier (P + digits)

---

## 2. Core Entity Definitions

### 2.1 Entity (Base Node)

**Purpose:** Represents any real-world thing in the knowledge graph with a cross-subgraph identity.

**Neo4j Label:** `:Entity`

**Primary Key:** `entity_cipher` (Tier 1 cipher)

**Created By:** SCA (Subject Concept Agent)

**Attributes:**

| Attribute | Type | Required | Default | Description | Example | Source |
|-----------|------|----------|---------|-------------|---------|--------|
| **entity_cipher** | String | YES | - | Tier 1 cipher: cross-subgraph join key | `ent_per_Q1048` | Computed by `generate_entity_cipher()` |
| **qid** | QID | YES* | - | Wikidata identifier (*or namespace = bn/crys) | `Q1048` | Wikidata |
| **entity_type** | Enum | YES | - | Classification from ENTITY_TYPE_PREFIXES | `PERSON` | Computed via Entity Type Decision Table |
| **namespace** | Enum | YES | `wd` | Authority source: wd, bn, crys | `wd` | Authority cascade |
| label_en | String | NO | NULL | English label (display) | `Julius Caesar` | Wikidata label |
| label_la | String | NO | NULL | Latin label (if applicable) | `Gaius Iulius Caesar` | Wikidata label |
| instance_of | List[QID] | NO | [] | P31 values from Wikidata | `["Q5"]` | Wikidata P31 |
| federation_score | Integer | NO | 1 | Count of authority IDs (1-6) | 5 | Computed: COUNT(qid, lcsh, fast, lcc, pleiades, tgn) |
| property_summary | Object | NO | {} | QID-valued properties with values | `{"P27": ["Q17167"]}` | Wikidata claims |
| properties_count | Integer | NO | 0 | Total number of properties | 61 | Computed |
| status | Enum | YES | `candidate` | Lifecycle status | `approved` | Workflow state |
| proposed_by | String | NO | NULL | Agent ID that discovered entity | `sca_001` | System-generated |
| created_at | DateTime | YES | NOW() | Creation timestamp | `2026-02-21T10:00:00Z` | System-generated |
| created_by_agent | String | NO | NULL | Agent that created entity | `sca_001` | System-generated |

**Controlled Vocabularies:**

```yaml
entity_type (ENTITY_TYPE_PREFIXES registry):
  - PERSON: "per"
  - EVENT: "evt"
  - PLACE: "plc"
  - SUBJECTCONCEPT: "sub"
  - WORK: "wrk"
  - ORGANIZATION: "org"
  - PERIOD: "prd"
  - MATERIAL: "mat"
  - OBJECT: "obj"

namespace:
  - wd: Wikidata (primary authority)
  - bn: BabelNet (multilingual synset)
  - crys: Chrystallum synthetic (deterministic hash)

status:
  - candidate: Discovered but not validated
  - proposed: Proposed by agent, awaiting review
  - validated: Passed validation rules
  - approved: Human-reviewed and approved
  - rejected: Failed validation
  - archived: Superseded or deprecated
```

**Relationships:**

```yaml
Outgoing:
  - HAS_FACETED_VIEW → FacetedEntity
    Cardinality: One-to-Many (max 18 per SubjectConcept)
    Description: Links to facet-specific views
    
  - SUPPORTED_BY → FacetClaim
    Cardinality: Many-to-Many
    Description: Canonical entity supported by claims
    Created: When claim promoted (confidence ≥ 0.90)
```

**Indexes:**

```cypher
CREATE INDEX entity_cipher_idx IF NOT EXISTS
  FOR (n:Entity) ON (n.entity_cipher);

CREATE INDEX entity_qid_idx IF NOT EXISTS
  FOR (n:Entity) ON (n.qid);

CREATE INDEX entity_type_cipher_idx IF NOT EXISTS
  FOR (n:Entity) ON (n.entity_type, n.entity_cipher);
```

**Business Rules:**

```
BR-ENT-01: Entity Cipher Format
  entity_cipher MUST match pattern: ^ent_(per|evt|plc|sub|wrk|org|prd|mat|obj)_(Q\d+|bn:.+|crys:.+)$
  Severity: CRITICAL

BR-ENT-02: Entity Type Registry Constraint
  entity_type MUST be in ENTITY_TYPE_PREFIXES registry
  Severity: CRITICAL

BR-ENT-03: Federation Score Range
  federation_score MUST be Integer in range [1, 6]
  Severity: MEDIUM

BR-ENT-04: QID Format (if namespace = wd)
  IF namespace = "wd" THEN qid MUST match ^Q\d+$
  Severity: CRITICAL

BR-ENT-05: Namespace-QID Alignment
  IF namespace = "wd" THEN qid starts with "Q"
  IF namespace = "bn" THEN qid starts with "bn:"
  IF namespace = "crys" THEN qid starts with "crys:"
  Severity: CRITICAL
```

**Sample Data:**

```json
{
  "entity_cipher": "ent_per_Q1048",
  "qid": "Q1048",
  "entity_type": "PERSON",
  "namespace": "wd",
  "label_en": "Julius Caesar",
  "label_la": "Gaius Iulius Caesar",
  "instance_of": ["Q5"],
  "federation_score": 5,
  "property_summary": {
    "P31": [{"qid": "Q5", "label": "human"}],
    "P27": [{"qid": "Q17167", "label": "Roman Republic"}],
    "P569": ["-0100-07-12"],
    "P570": ["-0044-03-15"]
  },
  "properties_count": 61,
  "status": "approved",
  "proposed_by": "sca_001",
  "created_at": "2026-02-21T10:00:00Z",
  "created_by_agent": "sca_001"
}
```

---

### 2.2 FacetedEntity (Hub Node)

**Purpose:** Materialized hub representing an entity evaluated from a specific facet perspective within a SubjectConcept context. Enables O(1) vertex jumps across facets.

**Neo4j Label:** `:FacetedEntity`

**Primary Key:** `faceted_cipher` (Tier 2 cipher)

**Created By:** SCA (Subject Concept Agent)

**Attributes:**

| Attribute | Type | Required | Default | Description | Example | Source |
|-----------|------|----------|---------|-------------|---------|--------|
| **faceted_cipher** | String | YES | - | Tier 2 cipher: subgraph address | `fent_pol_Q1048_Q17167` | Computed by `generate_faceted_cipher()` |
| **entity_cipher** | String | YES | - | Reference to parent Entity (FK) | `ent_per_Q1048` | From Entity node |
| **facet_id** | Enum | YES | - | One of 18 canonical facets | `POLITICAL` | SCA facet assignment |
| **subjectconcept_id** | QID | YES | - | Anchoring SubjectConcept QID | `Q17167` | From SubjectConcept |
| claim_count | Integer | NO | 0 | Number of claims in this context | 47 | Computed aggregate |
| avg_confidence | Float | NO | NULL | Average confidence of claims | 0.87 | Computed from FacetClaims |
| last_updated | DateTime | YES | NOW() | Last modification timestamp | `2026-02-21T10:00:00Z` | System-generated |
| evaluated_by_agent | String | NO | NULL | SFA agent identifier | `political_sfa_001` | SFA that processed this |

**Controlled Vocabularies:**

```yaml
facet_id (CANONICAL_FACETS registry - 18 values):
  - ARCHAEOLOGICAL: "arc"
  - ARTISTIC: "art"
  - BIOGRAPHIC: "bio"
  - COMMUNICATION: "com"
  - CULTURAL: "cul"
  - DEMOGRAPHIC: "dem"
  - DIPLOMATIC: "dip"
  - ECONOMIC: "eco"
  - ENVIRONMENTAL: "env"
  - GEOGRAPHIC: "geo"
  - INTELLECTUAL: "int"
  - LINGUISTIC: "lin"
  - MILITARY: "mil"
  - POLITICAL: "pol"
  - RELIGIOUS: "rel"
  - SCIENTIFIC: "sci"
  - SOCIAL: "soc"
  - TECHNOLOGICAL: "tec"
```

**Relationships:**

```yaml
Incoming:
  - HAS_FACETED_VIEW (from :Entity)
    Cardinality: Many-to-One
    
Outgoing:
  - CONTAINS_CLAIM → FacetClaim
    Cardinality: One-to-Many
    
  - ASSESSES_FACET → Facet
    Cardinality: Many-to-One
```

**Indexes:**

```cypher
CREATE INDEX faceted_cipher_idx IF NOT EXISTS
  FOR (n:FacetedEntity) ON (n.faceted_cipher);

CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS
  FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);

CREATE INDEX faceted_subj_facet_idx IF NOT EXISTS
  FOR (n:FacetedEntity) ON (n.subjectconcept_id, n.facet_id);
```

**Business Rules:**

```
BR-FE-01: Faceted Cipher Format
  faceted_cipher MUST match pattern: ^fent_(arc|art|bio|com|cul|dem|dip|eco|env|geo|int|lin|mil|pol|rel|sci|soc|tec)_Q\d+_Q\d+$
  Severity: CRITICAL

BR-FE-02: Entity Reference Integrity
  entity_cipher MUST reference an existing Entity.entity_cipher
  Severity: CRITICAL

BR-FE-03: Facet Registry Constraint
  facet_id MUST be in CANONICAL_FACETS list
  Severity: CRITICAL

BR-FE-04: Unique Combination
  Combination (entity_cipher, facet_id, subjectconcept_id) MUST be unique
  Severity: CRITICAL
  Implementation: MERGE operation

BR-FE-05: Confidence Range
  IF avg_confidence IS NOT NULL THEN avg_confidence MUST be in [0.0, 1.0]
  Severity: MEDIUM

BR-FE-06: Claim Count Non-Negative
  claim_count MUST be >= 0
  Severity: MEDIUM
```

**Sample Data:**

```json
{
  "faceted_cipher": "fent_pol_Q1048_Q17167",
  "entity_cipher": "ent_per_Q1048",
  "facet_id": "POLITICAL",
  "subjectconcept_id": "Q17167",
  "claim_count": 47,
  "avg_confidence": 0.87,
  "last_updated": "2026-02-21T10:00:00Z",
  "evaluated_by_agent": "political_sfa_001"
}
```

---

### 2.3 FacetClaim (Assertion Node)

**Purpose:** Evidence-based assertion about an entity from a specific facet perspective, with complete provenance chain.

**Neo4j Label:** `:FacetClaim`

**Primary Key:** `cipher` (Tier 3 claim cipher)

**Created By:** SFA (Subject Facet Agent)

**Attributes:**

| Attribute | Type | Required | Default | Description | Example | Source |
|-----------|------|----------|---------|-------------|---------|--------|
| **cipher** | String | YES | - | Tier 3 claim cipher (content-addressable) | `fclaim_pol_b22020c0...` | Computed via SHA256 hash |
| **subject_entity_cipher** | String | YES | - | Entity this claim is about (Tier 1) | `ent_per_Q1048` | From Entity |
| **facet_id** | Enum | YES | - | Facet dimension | `POLITICAL` | SFA context |
| **subjectconcept_cipher** | String | YES | - | SubjectConcept context (Tier 1) | `ent_sub_Q17167` | From SubjectConcept |
| **property_pid** | PID | YES | - | Wikidata property | `P39` | Wikidata statement |
| **object_qid** | QID | NO | NULL | Target entity (if QID-valued) | `Q39686` | Wikidata statement |
| **object_value** | String | NO | NULL | Literal value (if not QID-valued) | `"Rome"` | Wikidata statement |
| qualifiers | Object | NO | {} | Cipher-eligible qualifiers only | `{"P580": -59, "P1545": 1}` | Wikidata qualifiers |
| source_qid | QID | YES | - | Source work QID | `Q47461` | Provenance |
| passage_locator | String | YES | - | Specific citation | `"Hist.2.14"` | Provenance |
| confidence | Float | YES | - | Claim confidence score [0.0, 1.0] | 0.95 | Agent assessment |
| status | Enum | YES | `proposed` | Lifecycle status | `validated` | Workflow |
| promoted | Boolean | NO | FALSE | Promoted to canonical graph? | TRUE | Promotion flag |
| promotion_date | DateTime | NO | NULL | When promoted (if promoted) | `2026-02-21T10:05:00Z` | System-generated |
| created_at | DateTime | YES | NOW() | Creation timestamp | `2026-02-21T10:00:00Z` | System-generated |
| created_by_agent | String | YES | - | SFA agent identifier | `political_sfa_001` | SFA ID |

**Controlled Vocabularies:**

```yaml
facet_id: (same as FacetedEntity - 18 canonical facets)

status:
  - proposed: Initial claim from SFA
  - validated: Passed validation rules
  - promoted: Confidence ≥ 0.90, created canonical relationship
  - disputed: Conflicting claims exist
  - rejected: Failed validation

Cipher-Eligible Qualifiers (included in cipher hash):
  - P580: start time
  - P582: end time
  - P585: point in time
  - P276: location
  - P1545: series ordinal
```

**Relationships:**

```yaml
Incoming:
  - CONTAINS_CLAIM (from :FacetedEntity)
    Cardinality: Many-to-One
    
Outgoing:
  - ASSERTS (to target :Entity or literal)
    Cardinality: Many-to-One
    Description: What this claim asserts
    
  - CITES_SOURCE → Work
    Cardinality: Many-to-One
    Description: Source work citation
```

**Indexes:**

```cypher
CREATE INDEX claim_cipher_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.cipher);

CREATE INDEX claim_entity_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.subject_entity_cipher);

CREATE INDEX claim_entity_facet_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.facet_id);

CREATE INDEX claim_subj_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.subjectconcept_cipher);
```

**Business Rules:**

```
BR-FC-01: Cipher Determinism
  Same (subject, property, object, facet, qualifiers, source, passage) MUST produce same cipher
  Severity: CRITICAL

BR-FC-02: Confidence Range
  confidence MUST be Float in [0.0, 1.0]
  Severity: CRITICAL

BR-FC-03: Promotion Threshold
  IF promoted = TRUE THEN confidence MUST be >= 0.90
  Severity: HIGH

BR-FC-04: Object Value XOR
  Exactly one of (object_qid, object_value) MUST be NOT NULL
  Severity: CRITICAL

BR-FC-05: Cipher-Eligible Qualifiers Only
  qualifiers keys MUST be subset of {P580, P582, P585, P276, P1545}
  Severity: HIGH
  Note: Other qualifiers stored separately as metadata
```

**Sample Data:**

```json
{
  "cipher": "fclaim_pol_a1b2c3d4e5f6g7h8",
  "subject_entity_cipher": "ent_per_Q1048",
  "facet_id": "POLITICAL",
  "subjectconcept_cipher": "ent_sub_Q17167",
  "property_pid": "P39",
  "object_qid": "Q39686",
  "object_value": null,
  "qualifiers": {
    "P580": -59,
    "P582": -58,
    "P1545": 1
  },
  "source_qid": "Q47461",
  "passage_locator": "Hist.2.14",
  "confidence": 0.95,
  "status": "promoted",
  "promoted": true,
  "promotion_date": "2026-02-21T10:05:00Z",
  "created_at": "2026-02-21T10:00:00Z",
  "created_by_agent": "political_sfa_001"
}
```

---

## 3. Controlled Vocabularies

### 3.1 Entity Type Registry

**Registry Name:** `ENTITY_TYPE_PREFIXES`

**Source File:** `scripts/tools/entity_cipher.py`

**Status:** LOCKED (requires architecture approval to modify)

**Governance:** Architecture team approval + ADR required

| Entity Type | 3-Char Prefix | Description | Example QID | P31 Value |
|-------------|---------------|-------------|-------------|-----------|
| PERSON | per | Individual human | Q1048 (Caesar) | Q5 |
| EVENT | evt | Historical event | Q25238182 (Rubicon) | Q1190554 |
| PLACE | plc | Geographic location | Q220 (Rome) | Q515, Q486972 |
| SUBJECTCONCEPT | sub | Subject/topic/period | Q17167 (Roman Republic) | Q11514315 |
| WORK | wrk | Creative work | Q644312 (Plutarch Life) | Q7725634 |
| ORGANIZATION | org | Organized group | Q193236 (Roman Senate) | Q43229 |
| PERIOD | prd | Time period | Q17167 (can also be period) | Q11514315 |
| MATERIAL | mat | Substance/material | Q753 (Copper) | Q214609 |
| OBJECT | obj | Physical object | Q34379 (Sword) | Q488383 |

**Usage:**
- Tier 1 cipher generation: `ent_{prefix}_{qid}`
- Entity type classification via P31 decision table
- Agent routing and specialization

---

### 3.2 Facet Registry (18 Canonical Facets)

**Registry Name:** `CANONICAL_FACETS` / `FACET_PREFIXES`

**Source File:** `scripts/tools/entity_cipher.py`

**Status:** LOCKED (18 canonical facets, established by architecture)

**Count:** 18

| Facet | 3-Char Prefix | Description | Example Focus |
|-------|---------------|-------------|---------------|
| ARCHAEOLOGICAL | arc | Archaeological evidence | Excavations, artifacts, sites |
| ARTISTIC | art | Art and aesthetics | Sculpture, painting, architecture |
| BIOGRAPHIC | bio | Individual life narratives | Birth, death, family, career |
| COMMUNICATION | com | Information exchange | Writing systems, media, signals |
| CULTURAL | cul | Cultural practices | Customs, traditions, rituals |
| DEMOGRAPHIC | dem | Population data | Census, migration, demographics |
| DIPLOMATIC | dip | International relations | Treaties, embassies, negotiations |
| ECONOMIC | eco | Economic activity | Trade, currency, taxation |
| ENVIRONMENTAL | env | Natural environment | Climate, geography, resources |
| GEOGRAPHIC | geo | Spatial information | Locations, coordinates, borders |
| INTELLECTUAL | int | Ideas and philosophy | Thought, scholarship, logic |
| LINGUISTIC | lin | Language and linguistics | Grammar, vocabulary, dialects |
| MILITARY | mil | Warfare and armed forces | Battles, ranks, strategy |
| POLITICAL | pol | Governance and power | Offices, laws, institutions |
| RELIGIOUS | rel | Religious beliefs | Deities, rituals, theology |
| SCIENTIFIC | sci | Scientific knowledge | Discovery, methods, theories |
| SOCIAL | soc | Social structures | Class, kinship, status |
| TECHNOLOGICAL | tec | Technology and tools | Inventions, techniques, tools |

**Usage:**
- Tier 2 cipher generation: `fent_{prefix}_{qid}_{subjectconcept}`
- SFA routing (which facet agents process entity)
- Facet assessment workflow (star pattern)

---

### 3.3 Cipher-Eligible Qualifiers

**Registry Name:** `CIPHER_ELIGIBLE_QUALIFIERS`

**Source:** `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` §4.2

**Status:** LOCKED (5 qualifiers define assertion identity)

| PID | Label | W5H1 | Reason for Inclusion | Example |
|-----|-------|------|----------------------|---------|
| P580 | start time | WHEN | Distinguishes temporal identity (1st vs 2nd consulship) | -59 (59 BCE) |
| P582 | end time | WHEN | Temporal bounds | -58 (58 BCE) |
| P585 | point in time | WHEN | Specific date assertions | -0044-03-15 |
| P276 | location | WHERE | Spatial identity (same event, different locations) | Q220 (Rome) |
| P1545 | series ordinal | WHICH | Instance identity (1st, 2nd, 3rd) | 1 |

**Excluded Qualifiers (Metadata - NOT in cipher):**

| PID | Label | Why Excluded |
|-----|-------|-------------|
| P1480 | sourcing circumstances | Provenance metadata |
| P459 | determination method | How we know (not what we know) |
| P3831 | object has role | Contextual, may change |
| P1810 | subject named as | Language-dependent string |
| P2241 | reason for deprecated rank | Wikidata lifecycle |
| P1932 | object stated as | Language-dependent string |

---

### 3.4 Status Lifecycle

**Enumeration:** `status` (used in Entity, FacetClaim)

| Value | Description | Transitions From | Transitions To |
|-------|-------------|------------------|----------------|
| candidate | Discovered but not validated | - | proposed, rejected |
| proposed | Proposed by agent | candidate | validated, rejected |
| validated | Passed validation rules | proposed | approved, disputed |
| approved | Human-reviewed and approved | validated | archived |
| disputed | Conflicting claims exist | validated | validated, rejected |
| rejected | Failed validation | any | - |
| archived | Superseded or deprecated | approved | - |

---

## 4. Data Lineage

### 4.1 Authority Sources

| Authority | URL | Identifier Format | Coverage | Usage in Chrystallum | Property |
|-----------|-----|-------------------|----------|----------------------|----------|
| **Wikidata** | https://wikidata.org | Q{digits} (entity)<br>P{digits} (property) | 100M+ entities | Primary entity resolution, property values | `qid` |
| **LCSH** | https://id.loc.gov/authorities/subjects | sh{8 digits} | 400K+ headings | Subject classification | `backbone_lcsh` |
| **FAST** | http://fast.oclc.org | fst{7 digits} | 2M+ headings | Faceted subject classification | `backbone_fast` |
| **LCC** | - | Letter + number range<br>(e.g., DG241-269) | History (D class) complete | Agent routing, classification | `backbone_lcc` |
| **PeriodO** | https://perio.do | p{id} | 10K+ periods | Temporal period authority | `periodo_id` |
| **Pleiades** | https://pleiades.stoa.org | {6 digits} | 35K+ ancient places | Ancient geography | `pleiades_id` |
| **TGN** | http://vocab.getty.edu/tgn | {7 digits} | 2M+ places | Geographic names | `tgn_id` |
| **BabelNet** | https://babelnet.org | bn:{id} | 500+ languages | Multilingual synsets | `qid` (when namespace=bn) |

### 4.2 Computed Fields

| Field | Computation | Dependencies | Example |
|-------|-------------|--------------|---------|
| entity_cipher | `f"ent_{type_prefix}_{qid}"` | entity_type, qid | `ent_per_Q1048` |
| faceted_cipher | `f"fent_{facet_prefix}_{qid}_{subject_qid}"` | facet_id, entity_cipher, subjectconcept_id | `fent_pol_Q1048_Q17167` |
| claim_cipher | SHA256(subject \| property \| object \| facet \| qualifiers \| source \| passage) | All claim components | `fclaim_pol_b22020c0...` |
| federation_score | COUNT(qid, lcsh, fast, lcc, pleiades, tgn) | Authority IDs present | 5 |
| avg_confidence | AVG(FacetClaim.confidence WHERE faceted_entity) | FacetClaims | 0.87 |

---

## 5. Data Quality Rules

### 5.1 Uniqueness Constraints

```yaml
UC-01: Entity Cipher Uniqueness
  Entity.entity_cipher MUST be unique
  Enforcement: Neo4j unique constraint
  
UC-02: Faceted Cipher Uniqueness
  FacetedEntity.faceted_cipher MUST be unique
  Enforcement: Neo4j unique constraint
  
UC-03: Claim Cipher Uniqueness
  FacetClaim.cipher MUST be unique
  Enforcement: MERGE operation (idempotent)
  
UC-04: Entity-Facet-Subject Combination
  UNIQUE (entity_cipher, facet_id, subjectconcept_id) on FacetedEntity
  Enforcement: Composite constraint
```

### 5.2 Referential Integrity

```yaml
RI-01: FacetedEntity → Entity
  FacetedEntity.entity_cipher MUST reference Entity.entity_cipher
  Enforcement: Validation before creation
  
RI-02: FacetClaim → Entity
  FacetClaim.subject_entity_cipher MUST reference Entity.entity_cipher
  Enforcement: Validation before creation
  
RI-03: SubjectConcept Reference
  FacetedEntity.subjectconcept_id SHOULD reference Entity WHERE entity_type = "SUBJECTCONCEPT"
  Enforcement: Warning (not blocking)
```

### 5.3 Data Type Constraints

```yaml
DT-01: Confidence Range
  ALL confidence fields MUST be Float in [0.0, 1.0]
  
DT-02: QID Format
  ALL qid fields MUST match regex: ^Q\d+$
  
DT-03: PID Format
  ALL property_pid fields MUST match regex: ^P\d+$
  
DT-04: ISO 8601 Dates
  ALL temporal fields MUST be ISO 8601: YYYY-MM-DD or -YYYY-MM-DD (BCE)
  
DT-05: Federation Score Range
  federation_score MUST be Integer in [1, 6]
```

---

## 6. Neo4j Schema DDL

### 6.1 Index Definitions

```cypher
-- Entity indexes
CREATE INDEX entity_cipher_idx IF NOT EXISTS
  FOR (n:Entity) ON (n.entity_cipher);

CREATE INDEX entity_qid_idx IF NOT EXISTS
  FOR (n:Entity) ON (n.qid);

CREATE INDEX entity_type_cipher_idx IF NOT EXISTS
  FOR (n:Entity) ON (n.entity_type, n.entity_cipher);

-- FacetedEntity indexes
CREATE INDEX faceted_cipher_idx IF NOT EXISTS
  FOR (n:FacetedEntity) ON (n.faceted_cipher);

CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS
  FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);

CREATE INDEX faceted_subj_facet_idx IF NOT EXISTS
  FOR (n:FacetedEntity) ON (n.subjectconcept_id, n.facet_id);

CREATE INDEX faceted_subj_idx IF NOT EXISTS
  FOR (n:FacetedEntity) ON (n.subjectconcept_id);

-- FacetClaim indexes
CREATE INDEX claim_cipher_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.cipher);

CREATE INDEX claim_entity_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.subject_entity_cipher);

CREATE INDEX claim_entity_facet_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.facet_id);

CREATE INDEX claim_subj_idx IF NOT EXISTS
  FOR (c:FacetClaim) ON (c.subjectconcept_cipher);
```

### 6.2 Constraint Definitions

```cypher
-- Unique constraints
CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
  FOR (n:Entity) REQUIRE n.entity_cipher IS UNIQUE;

CREATE CONSTRAINT faceted_cipher_unique IF NOT EXISTS
  FOR (n:FacetedEntity) REQUIRE n.faceted_cipher IS UNIQUE;

CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS
  FOR (c:FacetClaim) REQUIRE c.cipher IS UNIQUE;

-- Existence constraints (NOT NULL)
CREATE CONSTRAINT entity_cipher_exists IF NOT EXISTS
  FOR (n:Entity) REQUIRE n.entity_cipher IS NOT NULL;

CREATE CONSTRAINT entity_type_exists IF NOT EXISTS
  FOR (n:Entity) REQUIRE n.entity_type IS NOT NULL;
```

---

## 7. Change History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-02-21 | 1.0 | Initial data dictionary creation (backfilled from architecture) | Requirements Analyst Agent |

---

## 8. Appendices

### A. Sample Queries

**Find all faceted views of an entity:**
```cypher
MATCH (e:Entity {entity_cipher: 'ent_per_Q1048'})
  -[:HAS_FACETED_VIEW]->(fe:FacetedEntity)
RETURN e, fe
ORDER BY fe.facet_id;
```

**Vertex jump (cross-facet navigation):**
```cypher
// No traversal - direct index seeks
MATCH (mil:FacetedEntity {faceted_cipher: 'fent_mil_Q1048_Q17167'})
MATCH (pol:FacetedEntity {faceted_cipher: 'fent_pol_Q1048_Q17167'})
RETURN mil, pol;
```

**Find all claims for entity in specific facet:**
```cypher
MATCH (fe:FacetedEntity {
  entity_cipher: 'ent_per_Q1048',
  facet_id: 'POLITICAL'
})-[:CONTAINS_CLAIM]->(c:FacetClaim)
RETURN fe, c
ORDER BY c.confidence DESC;
```

---

**Document maintained by:** Requirements Analyst Agent  
**Last updated:** February 21, 2026
