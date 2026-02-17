# Chrystallum Schema Reference

**Purpose:** Quick reference for agents and developers  
**Date:** February 14, 2026  
**Version:** Phase 1 Complete

---

## Node Types

### Primary Entities

**Human**
- People, historical figures
- Required: `qid` (Wikidata QID or `local_entity_{hash}`)
- Properties: `label`, `labels_multilingual`, `birth_year`, `death_year`, `authority_ids`, `confidence`, `minf_belief_id`
- Example: Julius Caesar (Q1048)

**Event**
- Historical events, battles, ceremonies
- Required: `qid`, `label`
- Properties: `cidoc_crm_type`, `authority_ids`, `property_chain`, `minf_confidence`, `source_statements`
- Example: Battle of Actium (Q193304)

**Place**
- Geographic locations, cities, regions
- Required: `qid`, `label`
- Properties: `labels_multilingual`, `authority_ids`, `coordinates`
- Example: Rome, Italy (Q220)

**Period**
- Time spans, eras, epochs
- Required: `label`, `start_year`, `end_year`
- Properties: `qid`, `authority_ids`, `facet_context`
- Example: Roman Republic (-509 to -27)

**SubjectConcept**
- Thematic anchors for classification
- Required: `label`, `backbone_fast` (FAST ID)
- Properties: `qid`, `lcsh_heading`, `lcc_code`, `authority_ids`
- Example: Roman Civil War

**Claim**
- Knowledge assertions with evidence
- Required: `claim_id`, `cipher`, `label`, `claim_type`, `facet`
- Properties: `confidence`, `posterior_probability`, `authority_source`, `authority_ids`, `minf_belief_id`
- Example: "Julius Caesar crossed the Rubicon in 49 BCE"

**Year**
- Temporal backbone nodes
- Range: -3000 to 2025
- Properties: `year` (ISO 8601 integer), `decade`, `century`, `millennium`
- Example: Year -49 (49 BCE)

### Roman Naming System

**Gens**
- Roman family/clan
- Properties: `label`, `qid`, `political_faction`, `notable_members`
- Example: Gens Julia

**Praenomen**
- Roman first name
- Properties: `label`, `abbreviated_form`, `gender`
- Example: Gaius (C.), Marcus (M.)

**Cognomen**
- Family branch or nickname
- Properties: `label`, `qid`, `meaning`, `origin`
- Example: Caesar, Brutus, Cicero

---

## Relationship Types (Key Selection)

Full registry: 312 types in `Relationships/relationship_types_registry_master.csv`

### Genealogical (24 types)

**PARENT_OF** (P40) / **CHILD_OF**
- Parent-child biological relationship
- Facets: demographic (0.92), social (0.85), political (0.75)
- Example: Gaius Julius Caesar → Julius Caesar

**FATHER_OF** (P22) / **MOTHER_OF** (P25)
- Gender-specific parent relationships
- Facets: demographic (0.92), social (0.88)
- More specific than PARENT_OF

**SPOUSE_OF** (P26)
- Marital union (symmetric)
- Facets: social (0.90), political (0.92), demographic (0.88), economic (0.85)
- Example: Julius Caesar ↔ Cornelia

**SIBLING_OF** (P3373) / **HALF_SIBLING_OF**
- Brother/sister relationships
- Facets: demographic (0.85), social (0.88), political (0.75)

**MEMBER_OF_GENS** (P53) / **HAS_GENS_MEMBER**
- Roman family/clan affiliation
- Facets: social (0.90), political (0.85), cultural (0.88), demographic (0.85)
- Example: Julius Caesar → Gens Julia

**GRANDPARENT_OF** / **GRANDCHILD_OF**
- Two-generation relationships
- Facets: demographic (0.88), social (0.80)

**ANCESTOR_OF** / **DESCENDANT_OF** (P1038)
- Distant lineage claims
- Facets: demographic (0.75), social (0.70), cultural (0.65)
- Note: cultural facet includes mythical ancestors

**ADOPTED_BY** / **GUARDIAN_OF**
- Legal guardianship and adoption
- Facets: social (0.85), political (0.88), demographic (0.80)
- Example: Octavian adopted by Julius Caesar

### Participation (10 types)

**PARTICIPATED_IN** (P710) / **HAD_PARTICIPANT**
- Generic event participation
- Facets: military (0.85), political (0.85), diplomatic (0.88), social (0.80), religious (0.82), cultural (0.80)
- Edge properties: `role` (from canonical registry), `faction`, `outcome`
- Example: Caesar PARTICIPATED_IN {role: "commander"} → Battle of Pharsalus

**COMMANDED** / **COMMANDED_BY**
- Military command authority
- Facets: military (0.90), political (0.88)

**FOUGHT_IN** / **FOUGHT_AT**
- Combat participation
- Facets: military (0.85), demographic (0.82)

**DIED_AT** (P1120) / **DEATH_LOCATION**
- Death location or event
- Facets: demographic (0.95), military (0.98), social (0.90)
- Example: Pompey DIED_AT → Egypt

**NEGOTIATED_TREATY** (P3342) / **TREATY_NEGOTIATOR**
- Treaty negotiation role
- Facets: diplomatic (0.88), political (0.85), communication (0.82)

**WITNESSED_EVENT** (P1441) / **WITNESSED_BY**
- Observer or attestor
- Facets: communication (0.80), political (0.78), social (0.75)

### Political (15 types)

**HELD_OFFICE** (P39)
- Office holding (consul, praetor, tribune, etc.)
- Facets: political (0.95), social (0.90)

**GOVERNED**
- Provincial governorship
- Facets: political (0.92), geographic (0.90), military (0.85)
- Example: Caesar GOVERNED → Gaul

**ELECTED_TO** / **APPOINTED_TO**
- Electoral victories vs. appointments
- Facets: political (0.92), social (0.88)

**ALLIED_WITH** / **AT_WAR_WITH**
- Interstate relations
- Facets: diplomatic (0.90), political (0.92), military (0.88)

### Temporal (8 types)

**OCCURRED_DURING**
- Event temporal location within period
- Example: Battle of Pharsalus OCCURRED_DURING → Roman Republic

**STARTS_IN_YEAR** / **ENDS_IN_YEAR**
- Event temporal anchoring to specific years
- Example: Crossing of Rubicon STARTS_IN_YEAR → Year -49

**PART_OF**
- Hierarchical temporal organization
- Example: Decade -40s PART_OF → Century -1

### Classification (5 types)

**CLASSIFIED_BY** / **SUBJECT_OF**
- Entity to subject concept linkage
- Example: Battle of Actium CLASSIFIED_BY → Roman Civil War (subject)

**SUPPORTED_BY**
- Claim evidence linking
- Example: Claim SUPPORTED_BY → RetrievalContext

---

## Node Properties (Common Pattern)

### Identity & Federation
- `qid`: Wikidata QID (e.g., Q1048) or provisional (e.g., local_entity_a8f9e2c4)
- `label`: Primary name/label
- `labels_multilingual`: JSON object with language tags (@en, @fr, @it, @la)
- `authority_ids`: JSON object with LCSH (sh prefix), FAST (fst prefix), CIDOC identifiers

### Confidence & Reasoning
- `confidence`: 0.0-1.0 score (claim quality)
- `posterior_probability`: Bayesian posterior from historian logic engine
- `minf_belief_id`: CRMinf I2_Belief node identifier for reasoning provenance
- `minf_confidence`: Posterior from CRMinf layer

### Authority & Source
- `authority_source`: Source system (e.g., "wikidata", "lcsh", "cidoc_crm")
- `source_statements`: JSON array of source statement IDs
- `property_chain`: Wikidata P-value sequence (e.g., "P793→P585→P1344")

### Temporal
- `birth_year`, `death_year`: ISO 8601 integers (negative for BCE)
- `start_year`, `end_year`: Period boundaries
- `year`: Year node value

### CIDOC-CRM Alignment
- `cidoc_crm_type`: E-class identifier (e.g., E21_Person, E5_Event, E53_Place)
- `cidoc_crm_kind`: "ENTITY" or "PROPERTY"

---

## Edge Properties (Qualifiers)

Relationships can carry qualifiers to capture Wikidata-style nuance:

### Role & Context
- `role`: From canonical registry (e.g., "commander", "soldier", "senator")
- `faction`: Affiliation or allegiance (e.g., "Roman", "Carthaginian", "Optimates")
- `outcome`: Result of participation (e.g., "victorious", "killed", "wounded")

### Wikidata Mapping
- `wikidata_property_id`: P-value (e.g., "P710", "P40", "P26")
- `wikidata_role_qualifier_object_pid`: Qualifier property for target (e.g., P3831)
- `wikidata_role_qualifier_subject_pid`: Qualifier property for source

### Temporal & Spatial Qualifiers
- `qualifier_timespan`: JSON with start/end dates
- `qualifier_location`: Place QID or label
- `qualifier_sourcing_property`: Which P-value sourced the qualifier

### Reasoning & Confidence
- `minf_belief_id`: Statement-level belief node
- `minf_confidence`: Relationship-specific confidence
- `minf_statement_id`: CRMinf statement identifier

### Example Edge
```cypher
(caesar:Human)-[:PARTICIPATED_IN {
  role: "commander",
  faction: "Roman",
  outcome: "victorious",
  wikidata_property_id: "P710",
  qualifier_timespan: {start: -48, end: -48},
  minf_belief_id: "I2-003447",
  minf_confidence: 0.95
}]->(pharsalus:Event)
```

---

## Facet Model

17 facets categorize claims and contexts. Each claim evaluated **per facet**; not all facets apply to all relationships.

**Complete List:**
1. `archaeological` - Material cultures, stratigraphic horizons
2. `artistic` - Art movements, aesthetic regimes
3. `cultural` - Identity regimes, symbolic systems
4. `demographic` - Population structure, vital statistics
5. `diplomatic` - Interstate relations, treaties
6. `economic` - Trade, commerce, financial systems
7. `environmental` - Climate, ecological shifts
8. `geographic` - Spatial regions, territorial extents
9. `intellectual` - Schools of thought, scholarly movements
10. `linguistic` - Language families, linguistic shifts
11. `military` - Warfare, conquests, strategic eras
12. `political` - States, governance, political eras
13. `religious` - Religious movements, doctrinal eras
14. `scientific` - Scientific paradigms, epistemic frameworks
15. `social` - Social structures, class systems, kinship
16. `technological` - Tool complexes, material innovations
17. `communication` - How events were communicated, propaganda, messaging

**Facet-Specific Confidence:**
See `Relationships/relationship_facet_baselines.json` for per-facet confidence baselines.

Example:
- SPOUSE_OF has **political** baseline 0.92 (alliances) vs. **social** baseline 0.90 (personal union)

---

## Canonical Roles

70+ roles in `Relationships/role_qualifier_reference.json`

**Categories:**
- **Military:** commander, soldier, general, cavalry, casualty, officer, deserter, scout
- **Diplomatic:** ambassador, negotiator, hostage, witness
- **Political:** senator, consul, tribune, dictator, praetor, censor, aedile, quaestor, proconsul
- **Religious:** pontifex_maximus, augur, vestal_virgin, priest
- **Intellectual:** orator, philosopher, historian, poet
- **Social:** patron, client, freedman, slave
- **Economic:** merchant, craftsman, landowner
- **Communication:** messenger, propagandist, herald
- **Genealogical:** father, mother, child, spouse, sibling, ancestor

Each role maps to:
- Wikidata P-value
- CIDOC-CRM type
- Context facets
- Confidence baseline
- Aliases for fuzzy matching

---

## Constraints & Indexes

### Required Constraints
```cypher
// Identity constraints (Phase 1: flexible QID requirement)
CREATE CONSTRAINT human_has_identifier IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS NOT NULL OR h.authority_ids IS NOT NULL;

CREATE CONSTRAINT claim_has_id IF NOT EXISTS
FOR (c:Claim) REQUIRE c.claim_id IS NOT NULL;

// Authority constraints
CREATE CONSTRAINT claim_has_authority_source IF NOT EXISTS
FOR (c:Claim) REQUIRE c.authority_source IS NOT NULL;
```

### Performance Indexes
```cypher
// QID lookups
CREATE INDEX human_qid IF NOT EXISTS FOR (h:Human) ON (h.qid);
CREATE INDEX event_qid IF NOT EXISTS FOR (e:Event) ON (e.qid);

// Temporal queries
CREATE INDEX year_value IF NOT EXISTS FOR (y:Year) ON (y.year);

// Subject classification
CREATE INDEX subject_fast IF NOT EXISTS FOR (s:SubjectConcept) ON (s.backbone_fast);

// Genealogy traversal
CREATE INDEX human_gens IF NOT EXISTS FOR (h:Human) ON (h.gens_label);
```

---

## Promotion Rules

**Universal Promotion Criteria:**
```
IF confidence >= 0.90 AND posterior_probability >= 0.90
THEN claim is promoted to canonical relationship
```

**Fallacy Flagging:**
- All fallacies detected and flagged (Fischer heuristics)
- Fallacy flag intensity: "none", "low", "high"
- Fallacies do NOT block promotion (metrics-only promotion)
- High intensity: interpretive claims (motivational, causal, political)
- Low intensity: descriptive claims (temporal, geographic, taxonomic)

**Facet-Aware Baselines:**
- Baseline varies by relationship + facet combination
- Pipeline can boost confidence based on facet context
- See `relationship_facet_baselines.json` for mappings

---

## QID Resolution

**Phase 1 (Current):** Stub implementation
- LLM-assisted Wikidata search (placeholder)
- Provisional local QIDs: `local_entity_{hash}`
- Context-aware scoring: temporal, role, geographic, gens alignment

**Provisional QID Format:**
```
local_entity_a8f9e2c4
```
- Deterministic hash from entity label
- Enables post-hoc linking when Wikidata match found
- Accepted if `authority_ids` exist (LCSH, FAST)

**Phase 2 (Planned):**
- Full Wikidata API integration
- SPARQL fuzzy search
- Multi-candidate scoring with confidence thresholds

---

## Example Entity Patterns

### Julius Caesar (Complete)
```json
{
  "qid": "Q1048",
  "label": "Julius Caesar",
  "labels_multilingual": {
    "@la": "Gaius Iulius Caesar",
    "@en": "Julius Caesar",
    "@fr": "Jules César",
    "@it": "Giulio Cesare"
  },
  "birth_year": -100,
  "death_year": -44,
  "authority_ids": {
    "lcsh": "sh85018840",
    "fast": "fst00030953",
    "viaf": "100227445"
  },
  "cidoc_crm_type": "E21_Person",
  "confidence": 0.98,
  "minf_belief_id": "I2-001234"
}
```

### Battle of Pharsalus
```json
{
  "qid": "Q193492",
  "label": "Battle of Pharsalus",
  "labels_multilingual": {
    "@en": "Battle of Pharsalus",
    "@la": "Proelium Pharsalicum",
    "@grc": "Μάχη της Φαρσάλου"
  },
  "year": -48,
  "authority_ids": {
    "lcsh": "sh85011542"
  },
  "cidoc_crm_type": "E5_Event",
  "property_chain": "P793→P585→P1344",
  "minf_confidence": 0.95
}
```

---

## Version History

- **Phase 1 (February 14, 2026):** Genealogy & participation support
  - QID resolver (stub implementation)
  - Role validator (70+ canonical roles)
  - Per-facet confidence baselines
  - 5 new relationship types added

- **Phase 0 (January 2026):** Foundation
  - 24 genealogy relationships
  - 17-facet model
  - Fischer fallacy detection
  - Authority tracking

---

**For Implementation Details:** See `PHASE_1_DECISIONS_LOCKED.md`, `PHASE_1_GENEALOGY_PARTICIPATION.md`, and `AI_CONTEXT.md`
