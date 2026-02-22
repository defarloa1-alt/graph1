# Appendix R: Federation Strategy Multi Authority

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Source:** Extracted from Consolidated Architecture Document

---

## Navigation

**Main Architecture:**
- [ARCHITECTURE_CORE.md](../../ARCHITECTURE_CORE.md)
- [ARCHITECTURE_ONTOLOGY.md](../../ARCHITECTURE_ONTOLOGY.md)
- [ARCHITECTURE_IMPLEMENTATION.md](../../ARCHITECTURE_IMPLEMENTATION.md)
- [ARCHITECTURE_GOVERNANCE.md](../../ARCHITECTURE_GOVERNANCE.md)

**Appendices Index:** [README.md](../README.md)

---

# **Appendix R: Federation Strategy & Multi-Authority Integration**

## **R.1 Federation Architecture Principles**

Chrystallum employs **federation** as a core architectural pattern to reconcile, validate, and enrich historical data across multiple authoritative systems. Rather than depending on a single source of truth, the system orchestrates a **multi-hop enrichment network** where Wikidata serves as a discovery broker and domain-specific authorities provide canonical grounding.

### **R.1.1 Wikidata as Federation Broker, Not Final Authority**

Wikidata functions as the **identity hub and router** in the federation architecture:

- **Discovery layer**: Provides QIDs, labels, descriptions, and external identifier properties (P214, P1584, P1566, etc.)
- **Routing mechanism**: External ID properties serve as jump-off points to domain authorities (VIAF, Pleiades, GeoNames, Trismegistos, etc.)
- **Confidence positioning**: Resides at Layer 2 Federation with confidence floor 0.90
- **Epistemic status**: Treated as broad identity hint, not canonical source

**Key principle**: Always resolve candidate entities to Wikidata QID first, then follow federation links to deeper authorities. Wikidata assertions are *discovery inputs*, not *verified outputs*.

### **R.1.2 Two-Hop Enrichment Pattern**

Federation follows a systematic two-hop pattern:

```cypher
// Hop 1: Wikidata resolution
MATCH (candidate:Entity {label: "Emerita Augusta"})
MERGE (wd:WikidataEntity {qid: "Q13560"})
CREATE (candidate)-[:ALIGNED_WITH]->(wd)

// Hop 2: Domain authority enrichment
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)
MERGE (place:PleiadesPlace {id: pleiades_id})
WITH place
CALL apoc.load.json("https://pleiades.stoa.org/places/" + place.id + "/json") 
YIELD value
SET place.names = value.names,
    place.temporal_range = value.temporalRange,
    place.coordinates = value.reprPoint
CREATE (candidate)-[:SAME_AS {confidence: 0.95}]->(place)
```

This pattern ensures:
1. **Broad discovery** via Wikidata's extensive coverage
2. **Deep grounding** via specialist authorities
3. **Provenance tracking** at each hop
4. **Confidence scoring** based on federation depth

### **R.1.3 Confidence Floors and Layer 2 Federation Positioning**

Federation authorities are tiered by epistemic strength:

- **Layer 1 (0.95-1.0)**: Domain-specific canonical authorities
  - LCSH/FAST for subjects
  - Pleiades for ancient places
  - PIR/PLRE for Roman prosopography
  - EDH for Latin inscriptions

- **Layer 2 (0.85-0.94)**: Broad integration hubs
  - Wikidata (0.90 baseline)
  - VIAF (0.88 for persons, 0.85 for works)
  - Getty AAT (0.90 for hierarchical concepts)

- **Layer 3 (0.70-0.84)**: Complementary sources and derived data
  - GeoNames/OSM (0.75 for modern coordinates)
  - Crowdsourced content (case-by-case evaluation)

**Confidence boost rules**:
- Adding epigraphic evidence (EDH/Trismegistos): +0.15 to +0.20
- Cross-validation by 2+ authorities: +0.10
- Temporal/geographic constraint satisfaction: +0.10
- Primary source linkage: +0.15

### **R.1.4 Federation Edge Patterns**

The system uses typed federation relationships to capture different alignment strengths:

```cypher
// SAME_AS: High-confidence identity match (0.90+)
(candidate)-[:SAME_AS {confidence: 0.95, 
                       verified_at: datetime(),
                       method: "P1584_resolution"}]->(pleiades)

// ALIGNED_WITH: Probable match requiring validation (0.70-0.89)
(candidate)-[:ALIGNED_WITH {confidence: 0.80,
                            conflicts: ["date_range_mismatch"],
                            review_required: true}]->(wikidata)

// DERIVED_FROM: Extracted/inferred from authority
(claim)-[:DERIVED_FROM {extraction_date: date(),
                        confidence: 0.85,
                        extractor_version: "v2.3"}]->(viaf_record)

// CONFLICTS_WITH: Explicit disagreement requiring adjudication
(source_a)-[:CONFLICTS_WITH {conflict_type: "temporal_range",
                             source_a_value: "-509/-27",
                             source_b_value: "-500/-31",
                             resolution: null}]->(source_b)
```

These edge types enable:
- **Confidence propagation**: `SAME_AS` edges boost target confidence
- **Review triggers**: `ALIGNED_WITH` and `CONFLICTS_WITH` flag human review
- **Provenance chains**: `DERIVED_FROM` tracks extraction lineage
- **Quality metrics**: Edge distributions measure federation health

---

## **R.2 Current Federation Layers (6 Operational)**

### **R.2.1 Subject Authority Federation** 
**Status**: Most mature

**Authorities**: LCC/LCSH/FAST/Wikidata

**Coverage**: Entire subject classification backbone, routing for specialist agents, bibliographic crosswalks

**Key artifacts**:
- `query_lcsh_enriched.tsv` (LCSH mappings)
- `Python/lcsh/scripts`, `Python/fast/scripts` (ingestion pipelines)
- `LCC_AGENT_ROUTING.md` (agent scope definitions)

**Usage pattern**:
1. Resolve subject string → LCSH/FAST heading
2. Map heading → LCC call number range
3. Route to appropriate Specialist Facet Agent based on LCC class
4. Cross-reference Wikidata P-codes for international concept alignment
5. Apply facet tags from shared registry

### **R.2.2 Temporal Federation**
**Status**: Strong

**Authorities**: Year backbone + curated periods + PeriodO alignment

**Coverage**: All temporal concepts, period-based lensing, date normalization

**Key artifacts**:
- `time_periods.csv` (1,083 curated periods)
- `periodo-dataset.csv` (PeriodO mappings)
- `scripts/backbone/temporal` (Year node generation)

**Usage pattern**:
1. Parse temporal expression (label, date range, uncertainty markers)
2. Create/link to Year nodes (ISO-normalized)
3. Resolve period label → PeriodO ID with explicit bounds
4. Attach Period nodes to Events/Persons/Places as temporal envelopes
5. Validate temporal plausibility (events must fall within period bounds)
6. Support period-based lensing ("show only Late Republic events")

### **R.2.3 Facet Federation**
**Status**: Strong conceptual, moderate automation

**Authorities**: 17 canonical facets applied across subject and temporal layers

**Coverage**: Cross-cutting conceptual dimensions (warfare, religion, law, etc.)

**Key artifacts**:
- `facet_registry_master.json` (canonical facet definitions)
- `period_facet_tagger.py` (automated facet assignment)
- Agent scope definitions (facet-based routing)

**Usage pattern**:
1. Analyze entity/event for facet applicability
2. Assign facet tags from registry (e.g., `WARFARE`, `LEGAL_TOPICS`, `GEOGRAPHY`)
3. Use facet tags for:
   - Agent routing (LCC + facet → specialist agent)
   - Cross-domain queries ("all warfare-related concepts across periods")
   - Framework-specific emphasis (Marxist framework privileges `ECONOMICS`)

### **R.2.4 Relationship Semantics Federation**
**Status**: In progress

**Authorities**: CIDOC-CRM/CRMinf + Wikidata predicates

**Coverage**: Canonical relationship vocabulary, action structures, event participation roles

**Key artifacts**:
- `action_structure_vocabularies.csv` (relationship types)
- `action_structure_wikidata_mapping.csv` (Wikidata P-code mappings)
- Architecture relationship sections (CIDOC alignment)

**Usage pattern**:
1. Extract relationship from claim text
2. Map to canonical vocabulary entry (e.g., "commanded" → `COMMANDED_MILITARY_UNIT`)
3. Align to CIDOC-CRM class (e.g., `E7 Activity`, `PC14 carried out by`)
4. Cross-reference Wikidata predicate (e.g., P598 `commander of`)
5. Store all mappings for cross-system queries

### **R.2.5 Geographic Federation**
**Status**: Early/transition

**Authorities**: Geographic registry + authority extracts (stabilizing)

**Coverage**: Place concepts, modern/ancient name variants, coordinate resolution

**Key artifacts**:
- `geographic_registry_master.csv` (place registry)
- Large authority extract files (Getty, GeoNames)

**Current challenges**:
- Source selection (Getty language vs. place pull)
- Ancient vs. modern place disambiguation
- Coordinate precision for historical periods

**Usage pattern** (in development):
1. Resolve place string → registry entry
2. Distinguish ancient (Pleiades) vs. modern (GeoNames) context
3. Pull name variants and temporal validity
4. Use coordinates for visualization only, not primary ontology

### **R.2.6 Agent/Claims Federation**
**Status**: Architecturally defined, partial implementation

**Authorities**: Specialist agents with defined scopes + review/synthesis workflow

**Coverage**: Agent capability declarations, claim provenance, review chains

**Key artifacts**:
- `2-12-26 Chrystallum Architecture - DRAFT.md` (agent model)
- `facet_agent_system_prompts.json` (agent definitions)
- `md/Agents/SCA/SCA_SFA_ARCHITECTURE_PACKAGE.md` (workflow specification)

**Usage pattern**:
1. Route claim → appropriate Specialist Facet Agent based on LCC/facet/period
2. SFA generates claim with provenance metadata
3. Seed Claim Agent reviews for conflicts and gaps
4. Framework-specific lensing applies interpretive emphasis
5. All steps tracked as federation of agent contributions

---

## **R.3 Stacked Evidence Ladder**

**Core Principle**: Move candidate nodes as far down the evidence ladder as possible before they are considered "solid." Each tier provides a different kind of epistemic support, and depth down the ladder translates to higher confidence scores and stronger validation.

### **R.3.1 People/Names** (3-tier ladder)

#### **Tier 1: Broad Identity** (Wikidata + VIAF)

**Purpose**: Establish high-level identity for persons, especially elites, authors, and subjects of modern works

**Authorities**: Wikidata QID, VIAF (via P214)

**How to use**:
- Resolve person string → Wikidata QID (e.g., "Gaius Julius Caesar" → Q1048)
- Follow P214 to VIAF cluster for canonical name forms in multiple languages
- Check VIAF for cluster quality:
  - Single clean cluster = strong identity
  - Multiple clusters = name collision, treat with caution
- Use for prosopography of elites, author attribution, modern scholarly linking

**Confidence rule**: Wikidata-only person = **textual/unconfirmed** (0.70-0.75)

```cypher
// Tier 1 enrichment
MATCH (p:Person {label: "Gaius Julius Caesar"})
MERGE (wd:WikidataEntity {qid: "Q1048"})
CREATE (p)-[:ALIGNED_WITH {confidence: 0.75}]->(wd)
WITH p, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id)
MERGE (viaf:VIAFRecord {id: viaf_id})
CREATE (p)-[:DERIVED_FROM {confidence: 0.80, layer: "identity"}]->(viaf)
SET p.canonical_names = viaf.name_variants,
    p.identity_tier = 1
```

#### **Tier 2: Historical Grounding** (Trismegistos People + PIR/PLRE)

**Purpose**: Confirm person appears in primary documentary evidence with historical context (offices, locations, dates)

**Authorities**: Trismegistos People (TM_People), PIR (Prosopographia Imperii Romani), PLRE (Prosopography of the Later Roman Empire)

**How to use**:
- Check TM_People for papyrological/epigraphic attestations
- For Roman elites, resolve to PIR/PLRE prosopography ID
- Extract structured data:
  - Offices held (consul, praetor, legatus)
  - Attested locations with date ranges
  - Family relationships (gens, cognomen patterns)
- Use as **hard constraints**:
  - Do not allow events outside person's active date window
  - Geography envelope from attested locations
  - Office-based event participation rules (can't command legion without military office)

**Confidence rule**: Wikidata + VIAF + Trismegistos + PIR = **strongly attested historical person** (0.90-0.95)

```cypher
// Tier 2 enrichment
MATCH (p:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WITH p, wd
// Check Trismegistos
CALL apoc.load.json("https://www.trismegistos.org/person/" + tm_id) YIELD value
MERGE (tm:TrismegistosPerson {id: value.person_id})
CREATE (p)-[:SAME_AS {confidence: 0.90, evidence_type: "documentary"}]->(tm)
SET p.attested_documents = value.document_count,
    p.date_range = [value.earliest_date, value.latest_date],
    p.attested_locations = value.places,
    p.identity_tier = 2
// Add PIR for Roman elites
MERGE (pir:PIREntry {id: pir_id})
CREATE (p)-[:SAME_AS {confidence: 0.95, prosopography: "PIR"}]->(pir)
SET p.offices = pir.offices,
    p.cursus_honorum = pir.career_path
```

#### **Tier 3: Micro-Evidence** (LGPN + DDbDP)

**Purpose**: Ground person in specific documentary/onomastic evidence at the micro-historical level

**Authorities**: LGPN (Lexicon of Greek Personal Names), DDbDP (Duke Databank of Documentary Papyri)

**How to use**:
- **For Greek names**: Query LGPN for name frequency and geographic distribution
  - Use to support cultural/ethnic inferences ("common freedman name in Alexandria")
  - Check name variants and spelling patterns
- **For documentary papyri**: Link person to specific DDbDP documents
  - Create Evidence nodes for each papyrus mentioning person
  - Extract roles: party to contract, witness, official, recipient
  - Link Evidence → Person → Document → Place → Date for full provenance chain

**Confidence rule**: Tier 3 grounding = **micro-attested with primary source linkage** (0.95-0.98)

```cypher
// Tier 3 enrichment: Documentary evidence nodes
MATCH (p:Person)-[:SAME_AS]->(tm:TrismegistosPerson)
WITH p, tm
UNWIND tm.document_ids AS doc_id
MERGE (doc:Document {tm_id: doc_id})
MERGE (ev:Evidence {id: "ev_" + doc_id})
SET ev.type = "papyrological",
    ev.text = doc.transcription,
    ev.material = "papyrus",
    ev.findspot = doc.provenance,
    ev.date_range = doc.date
CREATE (ev)-[:DOCUMENTS]->(p)
CREATE (ev)-[:FOUND_AT]->(place:Place {pleiades_id: doc.pleiades_place})
CREATE (ev)-[:DATED_TO]->(year:Year {iso_year: doc.middle_date})
SET p.evidence_count = size(collect(DISTINCT doc_id)),
    p.identity_tier = 3

// LGPN onomastic support
MERGE (lgpn:LGPNEntry {name: p.label})
SET lgpn.frequency = lgpn_frequency,
    lgpn.geographic_distribution = lgpn_regions
CREATE (p)-[:ONOMASTIC_SUPPORT]->(lgpn)
```

**Attestation strength summary**:
- **Wikidata-only**: Textual reference, unverified (0.70-0.75)
- **VIAF + Wikidata**: Author/creator authority (0.80-0.85)
- **VIAF + Trismegistos + PIR**: Strongly attested elite (0.90-0.95)
- **VIAF + TM + PIR + DDbDP**: Micro-attested with full provenance (0.95-0.98)

---

### **R.3.2 Places** (3-tier ladder)

#### **Tier 1: Conceptual Place** (Pleiades)

**Purpose**: Establish ancient geographic concept with temporal validity and name variants

**Authority**: Pleiades (via P1584)

**How to use**:
- Resolve ancient place → Pleiades ID
- Pleiades provides:
  - **Conceptual place** (not just coordinate point)
  - Ancient and modern name variants
  - **Temporal validity periods** (which historical periods the place exists in)
  - Coordinate ranges (often approximate, reflecting uncertainty)
- Use as **canonical place key** for ancient geography
- Apply temporal validity to constrain events:
  - Events using this place must fall within its valid period
  - Flag anachronistic references (e.g., "Constantinople" used before founding)

**Confidence rule**: Pleiades place grounding + temporal validity = +0.10 to base confidence

```cypher
// Tier 1: Pleiades resolution
MATCH (place:Place {label: "Emerita Augusta"})
MERGE (wd:WikidataEntity {qid: "Q13560"})
CREATE (place)-[:ALIGNED_WITH]->(wd)
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pleiades_id + "/json") 
YIELD value
MERGE (pleiades:PleiadesPlace {id: pleiades_id})
SET pleiades.names = value.names,
    pleiades.temporal_range = value.temporalRange,
    pleiades.coordinates = value.reprPoint,
    pleiades.periods = value.periods
CREATE (place)-[:SAME_AS {confidence: 0.90, temporal_validity: pleiades.temporal_range}]->(pleiades)
SET place.ancient_names = [n in value.names WHERE n.language IN ['grc', 'la'] | n.nameTransliterated],
    place.modern_names = [n in value.names WHERE n.language = 'en' | n.nameTransliterated],
    place.valid_periods = pleiades.periods
```

#### **Tier 2: Granular Geography** (Trismegistos Geo + DARE)

**Purpose**: Village-level, quarter-level, and network geography for fine-grained historical context

**Authorities**: 
- **Trismegistos Geo (TM_Geo)**: Village/quarter level, especially Egypt/Eastern Mediterranean
- **DARE (Digital Atlas of the Roman Empire)**: Roads, military installations, administrative geography

**How to use**:
- **TM_Geo for local places**:
  - Resolve village/quarter names to TM_Geo IDs
  - Map TM_Geo → Pleiades to anchor micro-places in global ancient map
  - Use for papyrus provenance, fine-grained population studies
- **DARE for network geography**:
  - Validate route plausibility between places using Roman road network
  - Locate military sites, administrative centers, border installations
  - Calculate distances and travel times for event modeling

**Confidence rule**: Tier 2 granularity + network validation = +0.15 beyond Tier 1

```cypher
// Tier 2: Trismegistos Geo (micro-geography)
MATCH (place:Place {label: "Theadelphia"})
CALL apoc.load.json("https://www.trismegistos.org/place/" + tm_geo_id) YIELD value
MERGE (tm_place:TMGeoPlace {id: tm_geo_id})
SET tm_place.type = "village",
    tm_place.nome = value.administrative_unit,
    tm_place.parent_place = value.parent
CREATE (place)-[:SAME_AS {confidence: 0.92, granularity: "village"}]->(tm_place)
// Link to parent Pleiades region
MATCH (parent:PleiadesPlace {id: tm_place.parent_pleiades})
CREATE (place)-[:PART_OF]->(parent)

// DARE road network validation
MATCH (event:Event)-[:OCCURRED_AT]->(origin:Place),
      (event)-[:DESTINATION]->(destination:Place)
WITH event, origin, destination
CALL dare.validateRoute(origin.pleiades_id, destination.pleiades_id) YIELD isPlausible, distance_km, travel_days
WHERE isPlausible = true
SET event.validated_route = true,
    event.distance_km = distance_km,
    event.travel_time_estimate = travel_days
```

#### **Tier 3: Modern Ground Truth** (GeoNames/OSM)

**Purpose**: Precise modern coordinates and admin boundaries for visualization only

**Authorities**: GeoNames (via P1566), OpenStreetMap

**How to use**:
- Use **only for UI maps and modern context**
- Never as primary historical geography
- Pull precise coordinates, bounding boxes, current admin units
- Useful for:
  - Map visualization layers
  - Modern place-name resolution for user queries
  - Spatial indexing for approximation queries

**Critical constraint**: GeoNames/OSM provide modern geography. Roman provinces, ancient boundaries, and historical place concepts come from Pleiades/DARE/TM_Geo, not modern systems.

```cypher
// Tier 3: Modern coordinates (UI-only)
MATCH (place:Place)-[:SAME_AS]->(pleiades:PleiadesPlace)
WITH place, pleiades
MATCH (wd:WikidataEntity)-[:HAS_EXTERNAL_ID {property: "P1566"}]->(geonames_id)
WHERE (place)-[:ALIGNED_WITH]->(wd)
CALL apoc.load.json("http://api.geonames.org/getJSON?geonameId=" + geonames_id) 
YIELD value
MERGE (gn:GeoNamesPlace {id: geonames_id})
SET gn.lat = value.lat,
    gn.lng = value.lng,
    gn.modern_name = value.name,
    gn.admin_units = [value.countryName, value.adminName1],
    gn.bbox = value.bbox
CREATE (place)-[:HAS_MODERN_LOCATION {usage: "visualization_only"}]->(gn)
SET place.map_coordinates = point({latitude: gn.lat, longitude: gn.lng})
// Do NOT use for historical assertions
```

---

### **R.3.3 Events/Claims/Communications** (3-tier ladder)

#### **Tier 1: Named Events** (Wikidata)

**Purpose**: Discover event seeds from Wikidata's named events and basic participation structure

**Authority**: Wikidata (battles, reforms, assassinations, foundations, treaties)

**How to use**:
- Query Wikidata for events related to entities, periods, or places
- Extract basic structure:
  - Event type (P31): battle, reform, assassination, etc.
  - Participants (P710): with roles like "commander," "victim," "location"
  - Date (P585, P580-P582): point in time or start-end
  - Place (P276, P17): where event occurred
- Treat as **event seeds, not fully trusted events**
- Propose Event node with:
  - Event type classification
  - Ordered participant roles
  - Temporal and spatial anchors
  - Confidence: 0.75 (seed level)

**Confidence rule**: Wikidata event seed = 0.75, requires corroboration for acceptance

```cypher
// Tier 1: Wikidata event seed discovery
CALL apoc.load.json("https://www.wikidata.org/wiki/Special:EntityData/Q48314.json") 
YIELD value
WITH value.entities["Q48314"] AS battle
MERGE (event:Event {wikidata_qid: "Q48314"})
SET event.label = battle.labels.en.value,
    event.type = "battle",
    event.confidence_tier = 1,
    event.base_confidence = 0.75,
    event.requires_corroboration = true
// Extract participants
FOREACH (claim IN battle.claims.P710 |
  MERGE (participant:Entity {qid: claim.mainsnak.datavalue.value.id})
  CREATE (event)-[:HAS_PARTICIPANT {role: claim.qualifiers.P3831[0].datavalue.value.id}]->(participant)
)
// Extract temporal and spatial
SET event.date_point = battle.claims.P585[0].mainsnak.datavalue.value.time,
    event.place_qid = battle.claims.P276[0].mainsnak.datavalue.value.id
```

#### **Tier 2: Epigraphic/Documentary Evidence** (EDH + Trismegistos Texts)

**Purpose**: Corroborate events with primary epigraphic or documentary sources

**Authorities**: 
- **EDH (Epigraphic Database Heidelberg)**: Latin inscriptions (via P2192)
- **Trismegistos Texts**: Papyri and inscriptions catalog

**How to use**:
- For each event seed, search authorities for inscriptions/papyri mentioning:
  - Event participants (persons, organizations)
  - Event location and date range
  - Event type keywords (battle, dedication, victory, law)
- Create **Communication/Evidence nodes** for each source:
  - Full text transcription
  - Material type (marble, bronze, papyrus)
  - Dimensions and physical description
  - Findspot (linked to Place nodes via Pleiades/GeoNames)
  - Date range (linked to Year nodes)
- Link to Event with typed role:
  - `PRIMARY_EPIGRAPHIC_EVIDENCE`: Inscription directly commemorating event
  - `CONTEMPORARY_DOCUMENT`: Papyrus from event's time period referencing it
  - `LATER_COMMEMORATIVE`: Post-event memorial or historical inscription
- **Raise Event confidence** when at least one epigraphic record corroborates participants/date/place

**Confidence rule**: Event with EDH/TM textual evidence = +0.20 confidence (up to 0.95)

```cypher
// Tier 2: EDH inscription evidence
MATCH (event:Event {label: "Battle of Pharsalus"})
WITH event
// Search EDH for inscriptions mentioning event participants
CALL apoc.load.json("https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search?person=Caesar") 
YIELD value
UNWIND value.items AS inscription
MERGE (ev:Evidence {edh_id: inscription.id})
SET ev.type = "inscription",
    ev.material = inscription.materialDescription,
    ev.text_latin = inscription.text,
    ev.findspot = inscription.findspot,
    ev.date_range = [inscription.notBefore, inscription.notAfter],
    ev.dimensions = inscription.dimensions
CREATE (ev)-[:DOCUMENTS {role: "PRIMARY_EPIGRAPHIC_EVIDENCE"}]->(event)
// Link to place
MERGE (place:Place {pleiades_id: inscription.pleiadesId})
CREATE (ev)-[:FOUND_AT]->(place)
// Link to date
CREATE (ev)-[:DATED_TO]->(year:Year {iso_year: inscription.middleDate})
// Boost event confidence
SET event.evidence_count = coalesce(event.evidence_count, 0) + 1,
    event.confidence_tier = 2,
    event.base_confidence = event.base_confidence + 0.20
```

```cypher
// Tier 2: Trismegistos documentary papyri
MATCH (event:Event)-[:HAS_PARTICIPANT]->(person:Person)
WITH event, person
MATCH (person)-[:SAME_AS]->(tm:TrismegistosPerson)
WITH event, tm
CALL apoc.load.json("https://www.trismegistos.org/text/search?person_id=" + tm.id) 
YIELD value
UNWIND value.texts AS text
MERGE (doc:Document {tm_text_id: text.id})
SET doc.type = text.type,
    doc.material = text.material,
    doc.provenance = text.provenance,
    doc.date = text.date
MERGE (ev:Evidence {id: "ev_tm_" + text.id})
SET ev.type = "documentary_papyrus",
    ev.text_content = text.transcription
CREATE (ev)-[:DOCUMENTS {role: "CONTEMPORARY_DOCUMENT"}]->(event)
CREATE (ev)-[:SOURCE_DOCUMENT]->(doc)
SET event.documentary_evidence_count = coalesce(event.documentary_evidence_count, 0) + 1
```

#### **Tier 3: Multi-Source Claims with HiCO Modeling**

**Purpose**: Model each historical statement as a Claim with full provenance, allowing multiple conflicting assertions per event

**Authorities**: All sources (primary inscriptions/papyri, literary narratives, modern scholarly reconstructions)

**How to use**:
- For each Event, create multiple Claim nodes representing different source assertions:
  - **Claimant**: Livy, Polybius, EDH inscription EDH12345, modern historian
  - **Claim content**: Specific assertion (date, outcome, casualty count, motive)
  - **Target**: The Event node
  - **Claim type**: Primary evidence vs. secondary narrative vs. scholarly interpretation
- Use federation sources to classify claim types:
  - **Primary evidence**: EDH, Trismegistos papyri, archaeological reports
  - **Secondary narrative**: Literary sources (Livy, Plutarch, Tacitus)
  - **Tertiary reconstruction**: Modern scholarly works, Wikipedia
- Enable **framework-specific claim weighting**:
  - Source-critical framework: Privilege epigraphy > papyri > literary narrative
  - Great Man framework: Privilege biographical literary sources
  - Marxist framework: Privilege economic documentary evidence
- Store all claims, expose conflicts, allow adjudication

**Confidence rule**: Multi-source claims with explicit conflict modeling = highest rigor (0.95-0.98 for well-adjudicated events)

```cypher
// Tier 3: Multi-source claim modeling
MATCH (event:Event {label: "Battle of Pharsalus"})
WITH event
// Claim 1: Livy's narrative account
MERGE (livy:Author {name: "Livy"})
CREATE (claim1:Claim {id: "claim_livy_pharsalus_date"})
SET claim1.content = "Battle occurred in 48 BCE during consulship of Caesar",
    claim1.claim_type = "date_assertion",
    claim1.date_value = date("-048-08-09"),
    claim1.source_type = "secondary_narrative",
    claim1.confidence = 0.85
CREATE (claim1)-[:MADE_BY]->(livy)
CREATE (claim1)-[:ABOUT]->(event)

// Claim 2: Epigraphic evidence (EDH inscription)
MATCH (inscription:Evidence {edh_id: "HD012345"})
CREATE (claim2:Claim {id: "claim_edh12345_pharsalus"})
SET claim2.content = "Inscription commemorates Caesar's victory, dated by consulship",
    claim2.claim_type = "event_confirmation",
    claim2.date_value = date("-048"),
    claim2.source_type = "primary_epigraphic",
    claim2.confidence = 0.95
CREATE (claim2)-[:DERIVED_FROM]->(inscription)
CREATE (claim2)-[:ABOUT]->(event)

// Claim 3: Conflicting modern scholarly reconstruction
MERGE (scholar:Author {name: "Smith, J."})
CREATE (claim3:Claim {id: "claim_smith_pharsalus_redate"})
SET claim3.content = "Re-dating to July 48 BCE based on astronomical calculations",
    claim3.claim_type = "date_assertion",
    claim3.date_value = date("-048-07-15"),
    claim3.source_type = "modern_reconstruction",
    claim3.confidence = 0.75
CREATE (claim3)-[:MADE_BY]->(scholar)
CREATE (claim3)-[:ABOUT]->(event)

// Model explicit conflict
CREATE (claim3)-[:CONFLICTS_WITH {
  conflict_type: "date_precision",
  difference: "~1 month",
  adjudication: "Livy's consulship date preferred, supported by EDH evidence"
}]->(claim1)

// Set event confidence based on claim constellation
WITH event, collect(claim1) + collect(claim2) + collect(claim3) AS claims
SET event.claim_count = size(claims),
    event.primary_evidence_count = size([c IN claims WHERE c.source_type = "primary_epigraphic"]),
    event.confidence_tier = 3,
    event.base_confidence = 0.95  // High confidence due to primary + secondary corroboration
```

**Outcome**: Events become nodes anchored by multi-source claims, not flat facts. Frameworks can weight claims differently, conflicts are explicit, and provenance is complete.

---

## **R.4 Federation Usage Patterns by Authority**

This section provides concrete guidance for leveraging each major federation authority within Chrystallum's architecture.

### **R.4.1 Wikidata** (Central Hub, Layer 2, 0.90 Confidence Floor)

**Role**: Identity hub and router

**How to leverage**:
1. **Always resolve candidate entities to QID first**
   - Use labels, descriptions, aliases for disambiguation
   - Check P31 (instance of) and P279 (subclass of) for type validation
   - Use P361 (part of) for hierarchical context

2. **Use external ID properties as federation jump-off points**
   - P214 → VIAF (persons)
   - P1584 → Pleiades (ancient places)
   - P1566 → GeoNames (modern places)
   - P2192 → EDH (inscriptions)
   - P1958 → Trismegistos Places
   - P4230 → Trismegistos Texts
   - P227 → GND (German authority)
   - P2950 → Nomisma (numismatics)

3. **Extract event/period seeds from Wikidata structure**
   - Query events by type, participant, period, or location
   - Use as discovery layer for entities not yet in your graph
   - Treat all Wikidata assertions as *provisional*, requiring domain authority confirmation

4. **Store Wikidata provenance but don't treat as final authority**
   - Keep QID for linking and discovery
   - Overwrite Wikidata values when domain authorities provide better data
   - Track when Wikidata and domain authorities conflict

**Cypher pattern**:
```cypher
// Wikidata as router to domain authorities
MATCH (candidate:Entity {label: $label})
CALL apoc.load.json("https://www.wikidata.org/wiki/Special:EntityData/" + $qid + ".json")
YIELD value
WITH candidate, value.entities[$qid] AS wd_entity
// Store Wikidata link
MERGE (wd:WikidataEntity {qid: $qid})
SET wd.label = wd_entity.labels.en.value,
    wd.description = wd_entity.descriptions.en.value
CREATE (candidate)-[:ALIGNED_WITH {confidence: 0.90, layer: 2}]->(wd)
// Extract external IDs for federation
WITH candidate, wd_entity.claims AS claims
UNWIND keys(claims) AS property
WHERE property STARTS WITH "P" AND claims[property][0].mainsnak.datatype = "external-id"
WITH candidate, property, claims[property][0].mainsnak.datavalue.value AS external_id
MERGE (ext:ExternalID {property: property, value: external_id})
CREATE (candidate)-[:HAS_EXTERNAL_ID {property: property}]->(ext)
```

---

### **R.4.2 Pleiades** (Ancient Places Backbone)

**Role**: Authority for ancient geographic concepts

**How to leverage**:
1. **Resolve to Pleiades ID via Wikidata P1584**
   - Treat Pleiades as canonical ancient place identifier
   - Store Pleiades URI as primary external reference

2. **Pull structured geographic data**
   - Coordinate ranges (often polygons or representative points)
   - Ancient name variants (Greek, Latin, indigenous)
   - Modern name variants
   - Temporal validity periods (which historical periods place exists in)
   - Connection types (at, near, within for related places)

3. **Use temporal validity to constrain events**
   - Events at a place must fall within its active period
   - Flag anachronistic references for review
   - Support geo-temporal federation (place-period joint constraints)

4. **Handle coordinate uncertainty appropriately**
   - Pleiades coordinates often represent approximate area, not precise point
   - Use coordinate ranges for spatial queries, not exact positioning
   - Prefer Pleiades conceptual place over GeoNames precise coordinates for historical context

**Cypher pattern**:
```cypher
// Pleiades place enrichment
MATCH (place:Place)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id:ExternalID)
WITH place, pleiades_id.value AS pid
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pid + "/json") YIELD value
MERGE (pleiades:PleiadesPlace {id: pid})
SET pleiades.title = value.title,
    pleiades.ancient_names = [n IN value.names WHERE n.language IN ['grc', 'la', 'egy'] | 
                              {transcription: n.nameTransliterated, 
                               attestations: n.attestations,
                               language: n.language}],
    pleiades.modern_names = [n IN value.names WHERE n.language = 'en' | n.romanized],
    pleiades.coordinate_point = point({latitude: value.reprPoint[1], longitude: value.reprPoint[0]}),
    pleiades.periods = [p IN value.features[0].properties.periods | p],
    pleiades.temporal_range = {
      start: value.features[0].properties.minDate,
      end: value.features[0].properties.maxDate
    },
    pleiades.place_types = value.placeTypes
CREATE (place)-[:SAME_AS {confidence: 0.95, authority: "Pleiades"}]->(pleiades)
// Apply temporal validity constraint
WITH place, pleiades
MATCH (place)<-[:OCCURRED_AT]-(event:Event)
WHERE event.year < pleiades.temporal_range.start 
   OR event.year > pleiades.temporal_range.end
SET event.temporal_flags = coalesce(event.temporal_flags, []) + ["anachronistic_place_usage"],
    event.requires_review = true
```

---

### **R.4.3 Trismegistos** (Texts, People, Local Geography)

**Role**: Epigraphic/papyrological hub for documentary sources

**How to leverage**:

#### **TMPeople (Trismegistos People)**
1. **Check documentary source attestation**
   - Search for person by name or external ID
   - Get count of papyri/inscriptions mentioning person
   - Pull date range and geographic distribution of attestations

2. **Combine with PIR/PLRE for elite disambiguation**
   - Wikidata-only + no TM = textual figure, low confidence
   - Wikidata + TM + PIR = documentary evidence of elite, high confidence

3. **Use attestations as confidence bump**
   - TM presence = structurally stronger than Wikidata-only
   - Add +0.15 confidence for primary documentary evidence

#### **TMGeo (Trismegistos Geography)**
1. **Village/quarter-level geography**
   - Especially valuable for Egypt and Eastern Mediterranean
   - Use for fine-grained provenance of papyri
   - Map to Pleiades parent regions for global anchoring

2. **Administrative hierarchies**
   - Nome, toparchy, village structures for Greco-Roman Egypt
   - Use for population studies and micro-regional analysis

#### **TMTexts (Trismegistos Texts)**
1. **Create Communication/Evidence nodes for each text**
   - Full text transcription (when available)
   - Material type (papyrus, ostracon, parchment)
   - Provenance (findspot)
   - Date range
   - Text type (letter, contract, petition, etc.)

2. **Link texts to Events, Persons, Places**
   - Use role annotations: `PRIMARY_EPIGRAPHIC_EVIDENCE`, `CONTEMPORARY_DOCUMENT`
   - Build provenance chains: Evidence → Person → Event → Place → Date

**Cypher pattern**:
```cypher
// Trismegistos People enrichment
MATCH (person:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]-()) // P4343 = TM Person ID
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]->(tm_id:ExternalID)
WITH person, tm_id.value AS tm_person_id
CALL apoc.load.json("https://www.trismegistos.org/person/" + tm_person_id) YIELD value
MERGE (tm:TrismegistosPerson {id: tm_person_id})
SET tm.name = value.name,
    tm.document_count = value.attestations_count,
    tm.date_range = [value.date_min, value.date_max],
    tm.locations = value.attestation_places
CREATE (person)-[:SAME_AS {confidence: 0.90, evidence: "documentary"}]->(tm)
SET person.documentary_attestations = tm.document_count,
    person.confidence_boost = 0.15

// Trismegistos Texts → Evidence nodes
MATCH (tm:TrismegistosPerson)
WITH tm
CALL apoc.load.json("https://www.trismegistos.org/text/search?person_id=" + tm.id) YIELD value
UNWIND value.texts AS text
MERGE (doc:Document {tm_text_id: text.tm_id})
SET doc.type = text.text_type,
    doc.material = text.material,
    doc.date_range = [text.date_min, text.date_max],
    doc.provenance = text.provenance
MERGE (ev:Evidence {id: "ev_tm_" + text.tm_id})
SET ev.type = "documentary_papyrus",
    ev.text_content = text.transcription,
    ev.material = text.material
CREATE (ev)-[:SOURCE_DOCUMENT]->(doc)
CREATE (ev)-[:DOCUMENTS]->(person:Person)-[:SAME_AS]->(tm)
// Link to place via TMGeo
MERGE (place:Place {tm_geo_id: text.place_id})
CREATE (ev)-[:FOUND_AT]->(place)
```

---

### **R.4.4 EDH** (Latin Inscriptions)

**Role**: Authority for Latin inscriptions and their findspots/dates

**How to leverage**:
1. **Search inscriptions mentioning entities**
   - Query by person name, place, date range
   - Use EDH API for full-text search

2. **Create Evidence nodes with full material context**
   - Full text (original and translation when available)
   - Material (marble, bronze, limestone, etc.)
   - Dimensions and physical description
   - Findspot (link to Pleiades/GeoNames)
   - Date range (link to Year nodes)
   - Current location (museum/collection)

3. **Link to Events with typed roles**
   - `PRIMARY_EPIGRAPHIC_EVIDENCE`: Inscription directly commemorating event
   - `DEDICATORY_INSCRIPTION`: Honors person/god related to event
   - `BUILDING_INSCRIPTION`: Documents construction or renovation
   - `FUNERARY_INSCRIPTION`: Provides biographical data

4. **Raise Event confidence when EDH corroborates**
   - At least one EDH record mentioning event participants/place/date
   - Add +0.20 to event confidence
   - Mark event as "epigraphically attested"

**Cypher pattern**:
```cypher
// EDH inscription search and Evidence node creation
MATCH (person:Person {label: "Julius Caesar"})
WITH person
CALL apoc.load.json("https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search?person=" + person.label) 
YIELD value
UNWIND value.items AS inscription
MERGE (ev:Evidence {edh_id: inscription.id})
SET ev.type = "latin_inscription",
    ev.material = inscription.attributes.material,
    ev.text_latin = inscription.transcription.latin,
    ev.text_translation = inscription.transcription.translation,
    ev.dimensions = {
      height_cm: inscription.attributes.height,
      width_cm: inscription.attributes.width,
      depth_cm: inscription.attributes.depth
    },
    ev.date_range = [inscription.dates.notBefore, inscription.dates.notAfter],
    ev.findspot_description = inscription.findspot.description,
    ev.current_location = inscription.repository
CREATE (ev)-[:DOCUMENTS {role: "epigraphic_attestation"}]->(person)
// Link to Place
MERGE (findspot:Place {pleiades_id: inscription.findspot.pleiadesId})
CREATE (ev)-[:FOUND_AT]->(findspot)
// Link to date
WITH ev, inscription.dates.notBefore AS start_year, inscription.dates.notAfter AS end_year
UNWIND range(start_year, end_year) AS year_val
MERGE (year:Year {iso_year: year_val})
CREATE (ev)-[:DATED_TO]->(year)
// Boost person confidence
MATCH (person)<-[:DOCUMENTS]-(ev)
SET person.epigraphic_attestations = coalesce(person.epigraphic_attestations, 0) + 1,
    person.base_confidence = person.base_confidence + 0.20
```

---

### **R.4.5 VIAF** (People and Works Disambiguation)

**Role**: Name authority for persons and works

**How to leverage**:
1. **Resolve to VIAF via Wikidata P214**
   - VIAF provides canonical name forms in multiple languages
   - Links to national authority files (LoC, BnF, DNB, etc.)

2. **Use for identity confirmation**
   - Single clean VIAF cluster = strong identity
   - Multiple clusters = name collision, disambiguation needed
   - Check co-references for same-person validation

3. **Separate Person vs. Author vs. Subject roles**
   - VIAF work lists distinguish person as author vs. subject of works
   - Use for scholarly reception tracking
   - Connect Person node to WorksAbout and WorksBy lists

4. **Attestation strength matrix**:
   - Wikidata-only = textual/unconfirmed (0.70)
   - Wikidata + VIAF = author/creator authority (0.80)
   - VIAF + Trismegistos + PIR = strongly attested historical person (0.90)

**Cypher pattern**:
```cypher
// VIAF person enrichment
MATCH (person:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P214"}]-()) // P214 = VIAF ID
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id:ExternalID)
WITH person, viaf_id.value AS viaf_id_val
CALL apoc.load.json("https://viaf.org/viaf/" + viaf_id_val + "/viaf.json") YIELD value
MERGE (viaf:VIAFRecord {id: viaf_id_val})
SET viaf.canonical_names = [n IN value.mainHeadings.data | n.text],
    viaf.name_variants = [n IN value.x400s.x400 | n.datafield.subfield[0].text],
    viaf.national_authorities = [s IN value.sources.source | s],
    viaf.works_count = size(value.titles.work)
CREATE (person)-[:SAME_AS {confidence: 0.85, authority: "VIAF"}]->(viaf)
SET person.canonical_name = viaf.canonical_names[0],
    person.name_variants = viaf.name_variants
// Extract works relationships
WITH person, viaf, value.titles.work AS works
UNWIND works AS work
MERGE (w:Work {title: work.title})
CREATE (person)-[:AUTHOR_OF]->(w)
// Check attestation strength
WITH person
OPTIONAL MATCH (person)-[:SAME_AS]->(tm:TrismegistosPerson)
OPTIONAL MATCH (person)-[:SAME_AS]->(pir:PIREntry)
WITH person, tm, pir
SET person.attestation_level = CASE
  WHEN tm IS NOT NULL AND pir IS NOT NULL THEN "strongly_attested"
  WHEN tm IS NOT NULL THEN "documentary_attested"
  ELSE "textual_only"
END,
person.base_confidence = CASE
  WHEN tm IS NOT NULL AND pir IS NOT NULL THEN 0.95
  WHEN tm IS NOT NULL THEN 0.85
  ELSE 0.75
END
```

---

### **R.4.6 GeoNames/OSM** (Modern Coordinates)

**Role**: Modern geographic ground truth for visualization

**How to leverage**:
1. **Pull precise coordinates and bounding boxes**
   - Use GeoNames API via Wikidata P1566
   - Get latitude, longitude, elevation
   - Pull admin hierarchy (country, state, region)
   - Get bounding box for spatial queries

2. **Use ONLY for UI maps and modern context**
   - Never as primary historical geography
   - Historical geography comes from Pleiades/DARE/TM_Geo
   - GeoNames provides visualization layer only

3. **Map ancient → modern for user experience**
   - Show "ancient Rome" on modern Italy map
   - Provide modern place names for context
   - Calculate modern travel distances for comparison

**Critical constraint**: Roman provinces, ancient boundaries, and historical place concepts are NOT derived from modern geography. Pleiades/DARE provide historical ontology; GeoNames provides visual convenience only.

**Cypher pattern**:
```cypher
// GeoNames modern coordinates (visualization-only)
MATCH (place:Place)-[:SAME_AS]->(pleiades:PleiadesPlace)
WITH place, pleiades
MATCH (place)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P1566"}]-()) // P1566 = GeoNames ID
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1566"}]->(gn_id:ExternalID)
WITH place, gn_id.value AS geonames_id
CALL apoc.load.json("http://api.geonames.org/getJSON?geonameId=" + geonames_id + "&username=demo") 
YIELD value
MERGE (gn:GeoNamesPlace {id: geonames_id})
SET gn.lat = toFloat(value.lat),
    gn.lng = toFloat(value.lng),
    gn.modern_name = value.name,
    gn.country = value.countryName,
    gn.admin1 = value.adminName1,
    gn.admin2 = value.adminName2,
    gn.bbox = value.bbox
CREATE (place)-[:HAS_MODERN_LOCATION {
  usage: "visualization_only",
  ontology_role: "none"
}]->(gn)
SET place.visualization_point = point({latitude: gn.lat, longitude: gn.lng})
// CRITICAL: Flag as non-ontological
WITH place, gn
SET gn:VisualizationOnly,
    gn.warning = "Modern coordinates only. Use Pleiades for historical geography."
```

---

### **R.4.7 PeriodO** (Period Semantics)

**Role**: Authority for named historical periods and temporal intervals

**How to leverage**:
1. **Resolve period labels to PeriodO IDs**
   - Match free-text period names to PeriodO entries
   - Get explicit start-end bounds (often BCE/CE year ranges)
   - Pull spatial scope (where period applies)

2. **Attach Period nodes to temporal envelopes**
   - Events: Period indicates when event could occur
   - Persons: Active period for person's life span
   - Places: Valid period for place existence/usage
   - Concepts: Period when concept was relevant (e.g., "Roman citizenship" only during Roman period)

3. **Check temporal plausibility**
   - Event cannot occur outside its named period bounds
   - Flag violations for review
   - Allow explicit override when justified (e.g., retroactive term use)

4. **Support period-based lensing**
   - "Show only Late Republic events"
   - "Filter to Augustan Age persons"
   - Enable comparative analysis across periods

**Cypher pattern**:
```cypher
// PeriodO period resolution and temporal constraints
MATCH (event:Event {period_label: "Late Republic"})
WITH event
CALL apoc.load.json("http://perio.do/periods.json") YIELD value
WITH event, value.periodCollections AS collections
UNWIND collections AS collection
UNWIND collection.definitions AS period
WHERE period.label CONTAINS "Late Republic" OR period.spatialCoverageDescription CONTAINS "Rome"
WITH event, period
WHERE period.label CONTAINS event.period_label
MERGE (p:Period {periodo_id: period.id})
SET p.label = period.label,
    p.start_year = toInteger(split(period.start.in.value, "-")[0]),
    p.end_year = toInteger(split(period.stop.in.value, "-")[0]),
    p.spatial_scope = period.spatialCoverage,
    p.authority = period.source
CREATE (event)-[:DURING_PERIOD]->(p)
// Validate temporal plausibility
WITH event, p
WHERE event.year < p.start_year OR event.year > p.end_year
SET event.temporal_violations = coalesce(event.temporal_violations, []) + [
  "Event year " + event.year + " outside period bounds [" + p.start_year + ", " + p.end_year + "]"
],
event.requires_review = true
// Enable period-based lensing
WITH event, p
MATCH (person:Person)-[:PARTICIPATED_IN]->(event)
CREATE (person)-[:ACTIVE_IN_PERIOD]->(p)
```

---

### **R.4.8 Getty AAT + LCSH/FAST** (Concepts and Institutions)

**Role**: Deep concept hierarchies (AAT) + library-grade topic hierarchies (LCSH/FAST)

**How to leverage**:

#### **Getty AAT (Art & Architecture Thesaurus)**
1. **Assign to abstract concepts and institutions**
   - For nodes like Concept, Institution, LegalRestriction, Organization
   - Get ontological type (e.g., "colony (settlements)", "senate (legislative bodies)", "taxation (fiscal function)")

2. **Use hierarchical structure**
   - Broader/narrower term navigation
   - Related terms for discovery
   - Scope notes for definition

3. **Enable faceted navigation**
   - "Show all events involving colonial institutions"
   - "Find concepts related to Roman taxation"
   - Support SFA concept spine building

#### **LCSH/FAST (Library of Congress Subject Headings / FAST)**
1. **Bibliographic crosswalk**
   - Already core to your Subject backbone
   - Assign LCSH/FAST to SubjectConcepts for library catalog linking

2. **Authority precedence (from Appendix P)**
   - Tier 1: LCSH/FAST (highest precedence for subjects)
   - Tier 2: LCC/CIP (second tier)
   - Tier 3: Wikidata + domain authorities (specialists)

3. **Agent routing**
   - LCC ranges map to specialist agent scopes
   - LCSH headings trigger facet assignments

**Cypher pattern**:
```cypher
// Getty AAT concept enrichment
MATCH (concept:Concept {label: "Roman Senate"})
WITH concept
CALL apoc.load.json("http://vocab.getty.edu/aat/300025306.json") YIELD value
MERGE (aat:AATConcept {id: "300025306"})
SET aat.term = value.prefLabel,
    aat.scope_note = value.scopeNote,
    aat.broader_terms = [b IN value.broader | b.label],
    aat.narrower_terms = [n IN value.narrower | n.label],
    aat.related_terms = [r IN value.related | r.label]
CREATE (concept)-[:SAME_AS {confidence: 0.90, authority: "Getty AAT"}]->(aat)
SET concept.ontological_type = aat.term,
    concept.hierarchy = aat.broader_terms

// LCSH/FAST subject heading assignment
WITH concept
MATCH (subject:Subject {lcsh_heading: "Rome--Politics and government--265-30 B.C."})
CREATE (concept)-[:HAS_SUBJECT]->(subject)
// Enable faceted query
SET concept.facets = ["GOVERNANCE", "POLITICAL_INSTITUTIONS"]

// Crosswalk for bibliographic discovery
WITH concept, subject
MATCH (work:Work)-[:ABOUT_SUBJECT]->(subject)
CREATE (concept)-[:DOCUMENTED_IN_WORKS]->(work)
```

---

## **R.5 Potential Federation Enhancements**

Building on the six operational federations, these five enhancements represent logical next steps for deepening Chrystallum's multi-authority integration.

### **R.5.1 Evidence Federation**

**Goal**: Unify source documents, passages, citations as first-class Evidence nodes linked to Claims and Reviews

**Current state**: Evidence nodes exist for EDH inscriptions and Trismegistos texts, but not unified across all source types

**Enhancement**:
- Create Evidence node schema for:
  - Literary sources (Livy, Plutarch, Tacitus) with passage-level references
  - Numismatic evidence (coin types, legends, iconography)
  - Archaeological reports (excavation publications, artifact catalogs)
  - Modern scholarly works (with claim extraction)
- Typed evidence relationships:
  - `PRIMARY_EVIDENCE`: Contemporary documents, inscriptions, archaeological material
  - `SECONDARY_NARRATIVE`: Literary sources postdating events
  - `TERTIARY_SYNTHESIS`: Modern scholarly reconstructions
- Enable evidence-based confidence scoring:
  - Claims with primary evidence get +0.20 confidence
  - Multiple corroborating pieces of evidence compound boost
  - Conflicting evidence triggers review workflow

**Example structure**:
```cypher
(claim:Claim)-[:SUPPORTED_BY {weight: 0.85}]->(evidence:Evidence {type: "inscription"})
(claim:Claim)-[:CONTRADICTED_BY {weight: 0.70}]->(evidence2:Evidence {type: "literary_narrative"})
(evidence)-[:CITED_IN]->(work:ModernWork)
(evidence)-[:FOUND_AT]->(place:Place)
(evidence)-[:DATED_TO]->(year:Year)
```

---

### **R.5.2 Identity Federation**

**Goal**: Crosswalk people/places/events across multiple identity authorities (VIAF, GND, Wikidata, LoC)

**Current state**: VIAF used for persons, but no systematic crosswalk across all national authority files

**Enhancement**:
- Create IdentityCluster nodes that aggregate same-entity references across:
  - VIAF (international virtual authority)
  - GND (German National Library)
  - BnF (Bibliothèque nationale de France)
  - LoC (Library of Congress)
  - ISNI (International Standard Name Identifier)
- Confidence-based identity resolution:
  - Same identifier in 3+ authorities = high-confidence match (0.95+)
  - Conflicting identifiers = disambiguation required
  - Single-source identifier = provisional (0.75)
- Enable cross-system queries:
  - "Find all works about Caesar in any national library catalog"
  - "Resolve ambiguous 'Marcus Antonius' via authority crosswalk"

**Example structure**:
```cypher
(person:Person)-[:IDENTITY_CLUSTER]->(cluster:IdentityCluster)
(cluster)-[:VIAF_ID {confidence: 0.90}]->(viaf:ExternalID {value: "12345"})
(cluster)-[:GND_ID {confidence: 0.92}]->(gnd:ExternalID {value: "67890"})
(cluster)-[:LOC_ID {confidence: 0.88}]->(loc:ExternalID {value: "n12345"})
SET cluster.match_confidence = avg([0.90, 0.92, 0.88]) // 0.90
```

---

### **R.5.3 Authority Conflict Federation**

**Goal**: Formal conflict-resolution layer when LCSH/FAST/Wikidata/PeriodO disagree, with stored adjudication rules

**Current state**: Conflicts detected (e.g., via `CONFLICTS_WITH` edges), but resolution is ad-hoc

**Enhancement**:
- Create ConflictResolution nodes capturing:
  - Conflicting authorities (Source A vs. Source B)
  - Conflict type (date_range, place_name, person_identity, etc.)
  - Source values (what each authority claims)
  - Resolution rule (precedence policy, expert adjudication, majority vote)
  - Resolution outcome (chosen value, flagged as unresolvable)
- Implement precedence policies:
  - Subjects: LCSH/FAST > LCC > Wikidata (from Appendix P)
  - Ancient Places: Pleiades > Wikidata > GeoNames
  - Dates: Primary sources (EDH, TM) > literary sources > modern reconstruction
- Enable audit trail:
  - Track all conflicts over time
  - Report authority agreement rates
  - Identify systematic divergences requiring policy updates

**Example structure**:
```cypher
(source_a:Authority {name: "LCSH"})-[:ASSERTS {value: "Roman Republic"}]->(entity)
(source_b:Authority {name: "Wikidata"})-[:ASSERTS {value: "Roman Kingdom"}]->(entity)
CREATE (conflict:ConflictResolution {
  type: "period_name",
  source_a: "LCSH",
  source_a_value: "Roman Republic",
  source_b: "Wikidata",
  source_b_value: "Roman Kingdom",
  resolution_rule: "LCSH_precedence",
  chosen_value: "Roman Republic",
  adjudication_date: date(),
  adjudicator: "system_policy"
})
CREATE (source_a)-[:CONFLICTS_WITH]->(conflict)-[:RESOLVED_BY]->(entity)
```

---

### **R.5.4 Geo-Temporal Federation**

**Goal**: Joint place-time validity layer for historical boundaries and names per period

**Current state**: Pleiades provides temporal validity, PeriodO provides period bounds, but no integrated place-period constraint model

**Enhancement**:
- Create PlacePeriodValidity nodes capturing:
  - Place ID (Pleiades)
  - Period ID (PeriodO)
  - Valid names for that place during that period
  - Boundary changes (e.g., "Mesopotamia" boundaries differ across Persian, Hellenistic, Roman periods)
  - Governance changes (colony → municipium → colonia; client kingdom → province)
- Enable period-aware queries:
  - "Show all places in 'Roman Britain' period" (place exists AND period overlaps AND place under Roman control)
  - "What was 'Constantinople' called in 100 BCE?" → "Byzantium"
  - "Which provinces existed during the Severan Dynasty?"
- Support dynamic historical maps:
  - Render boundaries appropriate to selected period
  - Show place name forms contemporary to period
  - Track expansion/contraction of empires over time

**Example structure**:
```cypher
(place:Place {label: "Constantinople"})-[:VALID_IN_PERIOD]->(ppv:PlacePeriodValidity {
  period_id: "late_antiquity",
  names: ["Constantinople", "Nova Roma"],
  governance: "imperial_capital",
  boundaries: "walls_of_constantine.geojson"
})
(place)-[:VALID_IN_PERIOD]->(ppv2:PlacePeriodValidity {
  period_id: "classical_period",
  names: ["Byzantium"],
  governance: "Greek_colony",
  boundaries: "archaic_byzantium.geojson"
})
// Query with period constraint
MATCH (e:Event)-[:OCCURRED_AT]->(p:Place)-[:VALID_IN_PERIOD]->(ppv)
WHERE e.year >= ppv.period_start AND e.year <= ppv.period_end
RETURN p.label, ppv.names[0] AS period_name // Use name appropriate to event's period
```

---

### **R.5.5 Agent Capability Federation**

**Goal**: Explicit machine-readable mapping from agent scope → LCC ranges/facets/periods for deterministic routing and coverage audits

**Current state**: Agent scopes defined conceptually (in `facet_agent_system_prompts.json`), but not fully machine-readable for automated routing

**Enhancement**:
- Create AgentCapability nodes for each Specialist Facet Agent:
  - LCC call number ranges (e.g., "D51-D90" for Roman History SFA)
  - Facet tags (e.g., ["WARFARE", "GOVERNANCE"] for Military History SFA)
  - Period ranges (e.g., "-500/500" for Classical Period SFA)
  - Geographic scope (e.g., "Mediterranean" for Ancient Mediterranean SFA)
- Implement deterministic routing:
  - Given entity with LCC + facet + period + place → compute best-match SFA
  - Score overlap between entity properties and agent capabilities
  - Route to agent with highest overlap score
- Enable coverage audits:
  - Identify gaps (LCC ranges with no assigned agent)
  - Identify overlaps (multiple agents claiming same scope)
  - Report agent workload (how many entities routed to each agent)
  - Validate agent specialization (check if routed entities truly match declared scope)

**Example structure**:
```cypher
MERGE (sfa:SpecialistFacetAgent {name: "Roman_History_SFA"})
MERGE (cap:AgentCapability {id: "cap_roman_history"})
SET cap.lcc_ranges = ["D51-D59", "D60-D69", "D70-D79"],
    cap.facets = ["GOVERNANCE", "WARFARE", "LEGAL_TOPICS", "ECONOMICS"],
    cap.period_start = -753,
    cap.period_end = 476,
    cap.geographic_scope = ["Italy", "Mediterranean", "Western_Europe"]
CREATE (sfa)-[:HAS_CAPABILITY]->(cap)

// Routing query
MATCH (entity:Entity)
WHERE entity.lcc = "D62" 
  AND "GOVERNANCE" IN entity.facets
  AND entity.year >= -509 AND entity.year <= 27
WITH entity
MATCH (sfa:SpecialistFacetAgent)-[:HAS_CAPABILITY]->(cap:AgentCapability)
WHERE entity.lcc STARTS WITH cap.lcc_ranges[0][0..2] // Match LCC prefix
  AND ANY(facet IN entity.facets WHERE facet IN cap.facets)
  AND entity.year >= cap.period_start AND entity.year <= cap.period_end
WITH entity, sfa, cap, 
     size([f IN entity.facets WHERE f IN cap.facets]) AS facet_overlap
ORDER BY facet_overlap DESC
LIMIT 1
MERGE (entity)-[:ROUTED_TO]->(sfa)
```

---

## **R.6 API Reference Summary**

| Federation | Wikidata Property | Entity Type | API Endpoint | Confidence Impact |
|------------|------------------|-------------|--------------|-------------------|
| **Pleiades** | P1584 | Place | `https://pleiades.stoa.org/places/[ID]/json` | +0.10 temporal validity |
| **Trismegistos People** | P4343 | Person | `https://www.trismegistos.org/person/[ID]` | +0.15 primary source |
| **Trismegistos Geo** | P1958 | Place | `https://www.trismegistos.org/place/[ID]` | +0.10 granular geo |
| **Trismegistos Texts** | P4230 | Text/Document | `https://www.trismegistos.org/text/[ID]` | +0.15 documentary evidence |
| **EDH** | P2192 | Inscription | `https://edh.ub.uni-heidelberg.de/data/api/inscriptions/[ID]` | +0.20 epigraphic evidence |
| **VIAF** | P214 | Person, Work | `https://viaf.org/viaf/[ID]/viaf.json` | +0.10 name authority |
| **GeoNames** | P1566 | Modern Location | `http://api.geonames.org/getJSON?geonameId=[ID]` | N/A (UI-only) |
| **PeriodO** | (label match) | Period | `http://perio.do/[ID]` | +0.10 temporal bounds |
| **Getty AAT** | P1014 | Concept | `http://vocab.getty.edu/aat/[ID].json` | +0.05 hierarchical type |
| **LCSH** | (subject match) | Subject | `https://id.loc.gov/authorities/subjects/[ID]` | Primary (Tier 1) |
| **FAST** | P2163 | Subject | `http://id.worldcat.org/fast/[ID]` | Primary (Tier 1) |
| **Wikidata** | (QID) | Universal | `https://www.wikidata.org/wiki/Special:EntityData/[QID].json` | 0.90 baseline (Layer 2) |

**Usage notes**:
- **Confidence Impact**: Typical boost to base confidence when this authority corroborates entity
- **Wikidata Property**: External ID property used to jump from Wikidata to domain authority
- **API Endpoint**: Template for direct authority access (replace `[ID]` with identifier)
- **"UI-only"**: Authority used for visualization/convenience, not primary ontology

---

## **R.7 Integration with Authority Precedence**

Federation strategy aligns with Chrystallum's tiered authority precedence model (defined in Section 4.4 and Appendix P).

### **R.7.1 Tier 1 (LCSH/FAST): Subject Authority Federation**

**Precedence**: Always check first for SubjectConcepts

**Federation pattern**:
1. Resolve subject string → LCSH heading or FAST topic
2. Pull LCSH hierarchy (broader/narrower terms)
3. Map to LCC call number range for agent routing
4. Cross-reference Wikidata P-codes for international alignment
5. Store mapping with `authority: "LCSH"` and `confidence: 0.95`

**Integration points**:
- **Agent routing**: LCSH/FAST → LCC → Specialist Facet Agent
- **Bibliographic crosswalk**: LCSH enables library catalog integration
- **Facet assignment**: LCSH headings trigger canonical facet tags
- **Conflict resolution**: LCSH overrides Wikidata for subject classification (per Appendix P §P.4)

**Example**:
```cypher
MATCH (entity:Entity {label: "Roman Senate"})
MERGE (lcsh:LCSHHeading {heading: "Rome--Politics and government--510-30 B.C."})
CREATE (entity)-[:HAS_SUBJECT {authority: "LCSH", confidence: 0.95, tier: 1}]->(lcsh)
SET entity.lcc_range = "JC85", // Derived from LCSH
    entity.routed_agent = "Roman_Governance_SFA"
```

---

### **R.7.2 Tier 2 (LCC/CIP): Fallback for Concepts Without LCSH/FAST Coverage**

**Precedence**: Second tier when LCSH/FAST unavailable

**Federation pattern**:
1. Check for LCSH/FAST first (Tier 1)
2. If not found, resolve to LCC call number directly
3. Use CIP (Cataloging in Publication) data for subjects
4. Still route to agents via LCC range
5. Store mapping with `authority: "LCC"` and `confidence: 0.85`

**Integration points**:
- **Gap coverage**: LCC provides broader classification when specific LCSH heading doesn't exist
- **Agent routing**: LCC ranges still enable deterministic agent routing
- **Hierarchy**: LCC provides coarse-grained hierarchy (D = History, D51-D90 = Ancient Rome)

**Example**:
```cypher
MATCH (entity:Entity {label: "Patrician-Plebeian Conflict"})
WHERE NOT EXISTS((entity)-[:HAS_SUBJECT]->(:LCSHHeading))
MERGE (lcc:LCCClass {call_number: "DG231-234"})
CREATE (entity)-[:CLASSIFIED_AS {authority: "LCC", confidence: 0.85, tier: 2}]->(lcc)
SET entity.routed_agent = "Roman_Social_History_SFA"
```

---

### **R.7.3 Tier 3 (Wikidata + Domain Authorities): Specialist Grounding**

**Precedence**: Use Wikidata as router, then jump to domain-specific authorities

**Federation pattern**:
1. Resolve entity → Wikidata QID (Layer 2, confidence 0.90)
2. Follow external ID properties to domain authorities:
   - **People**: VIAF, Trismegistos, PIR/PLRE
   - **Places**: Pleiades, Trismegistos Geo, DARE
   - **Events**: EDH, Trismegistos Texts, PeriodO
   - **Concepts**: Getty AAT, specialized thesauri
3. Domain authority confidence typically 0.90-0.95 (Tier 1 for their domain)
4. Wikidata serves as discovery, domain authority as canonical source

**Integration points**:
- **Two-hop enrichment**: Wikidata → external ID → domain authority graph
- **Cross-domain**: Wikidata enables linking across specialist silos
- **Provenance**: Track both Wikidata and domain authority as sources
- **Conflict resolution**: Domain authority overrides Wikidata when they disagree

**Example**:
```cypher
// Wikidata as router
MATCH (person:Person {label: "Marcus Tullius Cicero"})
MERGE (wd:WikidataEntity {qid: "Q1541"})
CREATE (person)-[:ALIGNED_WITH {confidence: 0.90, layer: 2, tier: 3}]->(wd)

// Jump to VIAF (person authority)
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id)
MERGE (viaf:VIAFRecord {id: viaf_id.value})
CREATE (person)-[:SAME_AS {authority: "VIAF", confidence: 0.90, tier: 3}]->(viaf)

// Jump to Trismegistos (documentary evidence)
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]->(tm_id)
MERGE (tm:TrismegistosPerson {id: tm_id.value})
CREATE (person)-[:SAME_AS {authority: "Trismegistos", confidence: 0.95, tier: 1_for_papyrology}]->(tm)

// Domain authority precedence: TM > VIAF > Wikidata for documentary evidence
SET person.documentary_confidence = 0.95 // TM provides primary source grounding
```

---

### **R.7.4 Crosswalk Pattern: Use Wikidata P-codes to Route to Domain Authority, Then Enrich Backward**

**Key principle**: Wikidata external ID properties (P-codes) function as federation routing keys, not final data sources.

**Crosswalk workflow**:
1. **Forward routing**: Entity → Wikidata QID → P-code → domain authority
2. **Data enrichment**: Pull canonical data from domain authority
3. **Backward propagation**: Enrich original entity with domain authority data
4. **Provenance tracking**: Store both Wikidata and domain source metadata
5. **Conflict handling**: When Wikidata and domain authority disagree, flag for resolution using precedence rules

**Crosswalk example (Place federation)**:
```cypher
// Step 1: Forward routing via Wikidata
MATCH (place:Place {label: "Tarraco"})
MERGE (wd:WikidataEntity {qid: "Q15695"})
CREATE (place)-[:ALIGNED_WITH {role: "discovery"}]->(wd)

// Step 2: Extract P1584 (Pleiades ID)
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)

// Step 3: Enrich from Pleiades (canonical ancient place authority)
WITH place, pleiades_id.value AS pid
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pid + "/json") YIELD value
MERGE (pleiades:PleiadesPlace {id: pid})
SET pleiades.canonical_names = value.names,
    pleiades.temporal_validity = value.temporalRange,
    pleiades.coordinates = value.reprPoint
CREATE (place)-[:SAME_AS {authority: "Pleiades", confidence: 0.95}]->(pleiades)

// Step 4: Backward propagation to original Place node
SET place.ancient_names = [n IN value.names WHERE n.language IN ['la', 'grc'] | n.nameTransliterated],
    place.valid_periods = value.periods,
    place.primary_authority = "Pleiades",
    place.enrichment_date = datetime()

// Step 5: Conflict detection (if Wikidata and Pleiades disagree)
WITH place, wd, pleiades
WHERE wd.label <> pleiades.canonical_names[0]
CREATE (conflict:ConflictResolution {
  type: "place_name",
  wikidata_value: wd.label,
  pleiades_value: pleiades.canonical_names[0],
  resolution: "Pleiades_precedence",
  chosen_value: pleiades.canonical_names[0]
})
SET place.label = pleiades.canonical_names[0] // Pleiades wins per precedence rule
```

**Crosswalk pattern advantages**:
- **Leverages Wikidata's breadth** for discovery and initial linkage
- **Respects domain authorities' depth** for canonical data
- **Traceable provenance** with explicit routing path
- **Conflict-aware** with adjudication rules
- **Bidirectional enrichment**: Wikidata improves coverage, domain authorities improve quality

---

## **R.8 Source Files**

This appendix synthesizes content from the following Federation layer documentation:

1. **[Archive/Federation/2-16-26-FederationCandidates.md](Archive/Federation/2-16-26-FederationCandidates.md)** (170 lines, archived)
   - Federation usage patterns for 8 major authorities
   - Role → How to leverage structure for each federation
   - Stacked evidence ladder principle

2. **[Archive/Federation/FederationUsage.txt](Archive/Federation/FederationUsage.txt)** (241 lines, archived)
   - Detailed stacked evidence ladder for People, Places, Events
   - Tier-by-tier enrichment patterns
   - Confidence rules and attestation strength matrix
   - Operationalization guidance for ingestion, validation, and lensing phases

3. **[Archive/Federation/2-12-26-federations.md](Archive/Federation/2-12-26-federations.md)** (archived)
   - 6 current operational federations
   - 5 potential federation enhancements
   - Wikidata as "federation broker, not final authority" principle
   - Federation architecture: two-hop enrichment, typed edges, Layer 2 positioning

4. **[Federation/Federation Impact Report_ Chrystallum Data Targets.md](Federation/Federation Impact Report_ Chrystallum Data Targets.md)** (not merged)
   - Detailed API reference with endpoints, parameters, response formats
   - Kept as separate technical reference for implementation
   - Not duplicated here to avoid excessive length

---

## **R.9 Related Sections**

Federation strategy integrates with multiple existing architecture components:

- **Section 4.4: Multi-Authority Model**  
  Defines Tier 1/2/3 precedence policy that governs federation conflict resolution

- **Appendix K: Wikidata Integration Patterns**  
  Detailed patterns for Wikidata as discovery layer and external ID routing

- **Appendix L: CIDOC-CRM Integration Guide**  
  Relationship vocabulary aligned with CIDOC E-classes and P-codes, used in federation edges

- **Appendix O (§O.6): Authority Precedence for Training Resources**  
  Training pipeline respects same LCSH > LCC > Wikidata hierarchy used in federation

- **Appendix P (§P.4): Authority Precedence Integration with CIDOC-CRM**  
  Formal precedence rules: LCSH/FAST (Tier 1) > LCC/CIP (Tier 2) > Wikidata + domain authorities (Tier 3)

- **Appendix Q: Operational Modes & Agent Orchestration**  
  Agent routing depends on LCC/facet/period federation for deterministic specialist assignment

---

## **R.10 API Implementation Guide**

This section provides **practical code examples** for accessing each federation's API endpoints, based on existing patterns in the codebase.

### **R.10.1 General Implementation Principles**

- Use `requests` library with proper headers (User-Agent identification)
- Set timeouts (30s for entity fetches, 60s for bulk operations)
- Implement exponential backoff for rate limiting (429 responses)
- Cache responses locally (Redis or file-based for batch operations)
- Log all API errors with traceback for debugging

---

### **R.10.2 Wikidata API Access**

Complete Python example based on `scripts/agents/facet_agent_framework.py` (lines 920-1020):

```python
import requests
from typing import Optional, Dict, Any

def fetch_wikidata_entity(qid: str) -> Optional[Dict[str, Any]]:
    """Fetch Wikidata entity with all claims."""
    API_URL = "https://www.wikidata.org/w/api.php"
    
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": qid,
        "languages": "en",
        "props": "labels|descriptions|claims|aliases",
    }
    
    headers = {"User-Agent": "Chrystallum/1.0 (research project)"}
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        entity = data.get("entities", {}).get(qid)
        if not entity or "missing" in entity:
            return None
            
        return {
            "qid": qid,
            "label": entity.get("labels", {}).get("en", {}).get("value"),
            "description": entity.get("descriptions", {}).get("en", {}).get("value"),
            "claims": entity.get("claims", {})
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikidata entity {qid}: {e}")
        return None
```

**Key Points:**
- Action: `wbgetentities` for entity fetch, `wbsearchentities` for search
- Rate limit: No official limit, but be respectful (1-2 req/sec recommended)
- Authentication: Not required for read operations
- Bulk: Use pipe-separated QIDs: `ids=Q1048|Q1056|Q2277`

---

### **R.10.3 Pleiades API Access**

```python
def fetch_pleiades_place(pleiades_id: str) -> Optional[Dict[str, Any]]:
    """Fetch Pleiades place with coordinates and temporal scope."""
    API_URL = f"https://pleiades.stoa.org/places/{pleiades_id}/json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            "pleiades_id": pleiades_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "reprPoint": data.get("reprPoint"),  # [lon, lat]
            "names": data.get("names", []),
            "timeperiods": data.get("timeperiods", []),
            "connections": data.get("connections", [])
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pleiades {pleiades_id}: {e}")
        return None
```

**Key Points:**
- No API key required
- Rate limit: ~1 req/sec polite crawling
- Bulk download: https://atlantides.org/downloads/pleiades/dumps/ (CSV/JSON dumps updated monthly)
- GeoJSON available: append `/json` to place URL

---

### **R.10.4 VIAF API Access**

```python
def fetch_viaf_authority(viaf_id: str) -> Optional[Dict[str, Any]]:
    """Fetch VIAF authority record with name forms."""
    API_URL = f"https://viaf.org/viaf/{viaf_id}/viaf.json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # VIAF JSON structure is deeply nested
        main_headings = data.get("mainHeadings", {}).get("data", [])
        
        return {
            "viaf_id": viaf_id,
            "name_forms": [h.get("text") for h in main_headings],
            "sources": data.get("sources", {}).get("source", []),
            "birth_date": data.get("birthDate"),
            "death_date": data.get("deathDate")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching VIAF {viaf_id}: {e}")
        return None
```

**Key Points:**
- No API key required
- Multiple formats: `/viaf.json`, `/viaf.xml`, `/rdf.xml`
- Search API: `http://viaf.org/viaf/search?query=...&httpAccept=application/json`
- Rate limit: Not published; use 1 req/sec

---

### **R.10.5 GeoNames API Access (Requires Free Registration)**

```python
def fetch_geonames_place(geonames_id: str, username: str) -> Optional[Dict[str, Any]]:
    """Fetch GeoNames place with modern coordinates."""
    API_URL = "http://api.geonames.org/getJSON"
    
    params = {
        "geonameId": geonames_id,
        "username": username  # Required: register at geonames.org
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            "geonames_id": geonames_id,
            "name": data.get("name"),
            "toponymName": data.get("toponymName"),
            "lat": data.get("lat"),
            "lng": data.get("lng"),
            "countryCode": data.get("countryCode"),
            "adminName1": data.get("adminName1"),  # State/province
            "featureClass": data.get("fcl"),
            "featureCode": data.get("fcode")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GeoNames {geonames_id}: {e}")
        return None
```

**Key Points:**
- **Authentication required**: Free username registration at http://www.geonames.org/login
- Rate limit: 1000 credits/hour, 30,000/day (free tier)
- Premium tier: 80,000/day ($200/year)
- Bulk download: http://download.geonames.org/export/dump/ (tab-delimited files)

---

### **R.10.6 PeriodO API Access**

```python
def fetch_periodo_periods(search_term: str = None) -> Optional[Dict[str, Any]]:
    """Fetch PeriodO period definitions."""
    API_URL = "http://n2t.net/ark:/99152/p0d.json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # PeriodO returns entire dataset; filter locally
        period_collections = data.get("periodCollections", {})
        
        if search_term:
            # Simple label matching (implement proper search as needed)
            matches = []
            for coll_id, collection in period_collections.items():
                for period_id, period in collection.get("definitions", {}).items():
                    label = period.get("label", "")
                    if search_term.lower() in label.lower():
                        matches.append({
                            "periodo_id": f"{coll_id}#{period_id}",
                            "label": label,
                            "spatialCoverage": period.get("spatialCoverage", []),
                            "start": period.get("start", {}),
                            "stop": period.get("stop", {})
                        })
            return {"periods": matches}
        
        return {"periodCollections": period_collections}
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PeriodO: {e}")
        return None
```

**Key Points:**
- No API key required
- Entire dataset in single JSON file (~15MB; cache locally)
- No rate limit (dataset updated infrequently)
- Period URIs: `http://n2t.net/ark:/99152/p0{collection_id}#{period_id}`

---

### **R.10.7 Trismegistos, EDH, Getty AAT Access**

**Trismegistos** - No public API; bulk data via:
- https://www.trismegistos.org/downloads.php
- CSV exports for TMPeople, TMGeo, TMTexts
- Direct database queries not supported; must use exports

**EDH (Epigraphic Database Heidelberg)**:
```python
def search_edh_inscriptions(search_term: str, max_results: int = 20) -> Optional[List[Dict]]:
    """Search EDH inscriptions."""
    API_URL = "https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search"
    
    params = {
        "text": search_term,
        "limit": max_results
    }
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return data.get("items", [])
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching EDH: {e}")
        return None
```

**Getty AAT** - SPARQL endpoint (advanced):
- Endpoint: `http://vocab.getty.edu/sparql`
- Requires SPARQL query language
- Easier: Use Linked Open Data URIs: `http://vocab.getty.edu/aat/{concept_id}.json`

---

### **R.10.8 Rate Limiting & Caching Strategy**

```python
import time
from functools import wraps

def rate_limit(calls_per_second: float = 1.0):
    """Decorator to rate-limit API calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=1.0)
def fetch_wikidata_entity_throttled(qid: str) -> Optional[Dict]:
    return fetch_wikidata_entity(qid)
```

**Caching with file-based storage**:
```python
import json
from pathlib import Path

def cache_api_response(cache_dir: str = "./federation_cache"):
    """Decorator to cache API responses to disk."""
    Path(cache_dir).mkdir(exist_ok=True)
    
    def decorator(func):
        @wraps(func)
        def wrapper(entity_id: str, *args, **kwargs):
            cache_file = Path(cache_dir) / f"{func.__name__}_{entity_id}.json"
            
            if cache_file.exists():
                with open(cache_file) as f:
                    return json.load(f)
            
            result = func(entity_id, *args, **kwargs)
            
            if result:
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
            
            return result
        return wrapper
    return decorator

@cache_api_response()
@rate_limit(calls_per_second=1.0)
def fetch_pleiades_place_cached(pleiades_id: str) -> Optional[Dict]:
    return fetch_pleiades_place(pleiades_id)
```

---

### **R.10.9 Configuration Management**

Store API credentials in environment variables or config file:

```python
# config.py
import os
from pathlib import Path

class FederationConfig:
    # GeoNames (requires free registration)
    GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "")
    
    # User-Agent for all requests
    USER_AGENT = "Chrystallum/1.0 (historical research; contact@example.com)"
    
    # Rate limits (requests per second)
    RATE_LIMITS = {
        "wikidata": 2.0,
        "pleiades": 1.0,
        "viaf": 1.0,
        "geonames": 0.5,  # Conservative for free tier
        "edh": 1.0
    }
    
    # Cache directory
    CACHE_DIR = Path(__file__).parent / "data" / "federation_cache"
    
    # Timeouts (seconds)
    DEFAULT_TIMEOUT = 30
    BULK_TIMEOUT = 60
```

---

### **R.10.10 Error Handling Pattern**

```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FederationAPIError(Exception):
    """Base exception for federation API errors."""
    pass

def safe_fetch_with_retry(
    fetch_func,
    entity_id: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Optional[Dict[str, Any]]:
    """Fetch with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            result = fetch_func(entity_id)
            if result:
                return result
            
            logger.warning(f"Empty result for {entity_id} (attempt {attempt + 1})")
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {entity_id} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(backoff_factor ** attempt)
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = backoff_factor ** (attempt + 1)
                logger.warning(f"Rate limited; waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                break
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    return None
```

---

### **R.10.11 Integration with Neo4j Write Pattern**

```python
def enrich_node_from_federation(
    neo4j_driver,
    node_id: str,
    qid: str
) -> Dict[str, Any]:
    """Fetch Wikidata, enrich with federations, write to Neo4j."""
    
    # 1. Fetch Wikidata entity
    entity = fetch_wikidata_entity(qid)
    if not entity:
        return {"status": "error", "message": "Entity not found"}
    
    # 2. Extract federation IDs from Wikidata claims
    claims = entity.get("claims", {})
    pleiades_id = extract_claim_value(claims, "P1584")  # Pleiades
    viaf_id = extract_claim_value(claims, "P214")  # VIAF
    geonames_id = extract_claim_value(claims, "P1566")  # GeoNames
    
    # 3. Fetch from federations (with caching & rate limiting)
    enrichments = {}
    
    if pleiades_id:
        enrichments["pleiades"] = fetch_pleiades_place_cached(pleiades_id)
    
    if viaf_id:
        enrichments["viaf"] = fetch_viaf_authority(viaf_id)
    
    if geonames_id:
        enrichments["geonames"] = fetch_geonames_place(
            geonames_id, 
            FederationConfig.GEONAMES_USERNAME
        )
    
    # 4. Write to Neo4j with federation metadata
    with neo4j_driver.session() as session:
        result = session.execute_write(
            lambda tx: write_enriched_node(tx, node_id, entity, enrichments)
        )
    
    return result

def write_enriched_node(tx, node_id, entity, enrichments):
    """Cypher write with federation properties."""
    cypher = """
    MATCH (n {node_id: $node_id})
    SET n.wikidata_qid = $qid,
        n.wikidata_label = $label,
        n.wikidata_description = $description,
        n.pleiades_id = $pleiades_id,
        n.viaf_id = $viaf_id,
        n.geonames_id = $geonames_id,
        n.federation_enriched = datetime(),
        n.federation_sources = $sources
    RETURN n
    """
    
    params = {
        "node_id": node_id,
        "qid": entity.get("qid"),
        "label": entity.get("label"),
        "description": entity.get("description"),
        "pleiades_id": enrichments.get("pleiades", {}).get("pleiades_id"),
        "viaf_id": enrichments.get("viaf", {}).get("viaf_id"),
        "geonames_id": enrichments.get("geonames", {}).get("geonames_id"),
        "sources": ["wikidata", "pleiades", "viaf", "geonames"]
    }
    
    result = tx.run(cypher, params)
    return result.single()
```

---

### **R.10.12 Existing Implementation Files**

Current implementations in codebase:
- `scripts/agents/facet_agent_framework.py` (lines 920-1020): Wikidata entity fetching
- `Subjects/CIP/2-11-26-subjects_broader_narrower.py`: Wikidata API patterns
- `Subjects/index_scan.py`: Wikidata search and entity retrieval
- `scripts/reference/agent_training_pipeline.py`: Wikidata federation integration

**Next Steps for Production:**
1. Centralize federation API logic in `scripts/federation/` module
2. Add pytest unit tests with mocked API responses
3. Implement Redis caching for production (file-based for development)
4. Add monitoring/logging for API failures and rate limit tracking
5. Document API key acquisition process in `md/Guides/SETUP_GUIDE.md`

---

**(End of Appendix R)**

---

## **APPENDIX S: BabelNet Lexical Authority Integration**

### **S.1 Positioning and Layer Architecture**

BabelNet operates as a **multilingual lexical layer** positioned at **Layer 2.5** in the Chrystallum architecture:

- **Layer 1:** Core ontology (SubjectConcept nodes, Claims, Relationships)
- **Layer 2:** Federation authorities (Wikidata, LCSH, FAST, TGN, Pleiades)
- **Layer 2.5:** BabelNet (lexical/semantic enrichment)
- **Layer 3:** Facet Authority (SFAs generating domain-specific ontologies)

**Architectural Position:**
- **Not a primary fact authority** (Wikidata holds factual ground truth)
- **Lexical sidecar** for multilingual labels, glosses, synsets, and cross-language entity linking
- **Semantic enrichment** for term disambiguation and synonym expansion
- **Cross-reference hub** linking WordNet, Wikipedia, Wikidata, and language-specific resources

**Key Distinction:**
- Wikidata provides **factual claims** (dates, locations, relationships) → confidence 0.90
- BabelNet provides **lexical/semantic context** (multilingual labels, senses, glosses) → confidence 0.75-0.85
- Combined alignment (BabelNet synset + Wikidata QID) → confidence boost +0.05

---

### **S.2 Core Use Cases**

#### **S.2.1 SubjectConcept Lexical Enrichment**

**Scenario:** A SubjectConcept node for "Roman Republic" needs multilingual labels and glosses.

**Workflow:**
1. SubjectConcept has `wikidata_id: Q17167`, `label: "Roman Republic"`, `facet: "political"`
2. Call BabelNet API with English label + QID to retrieve synset
3. Extract multilingual labels (Latin: *Res publica Romana*, French: *République romaine*, etc.)
4. Store on SubjectConcept:
   - `babelnet_id: bn:00068294n`
   - `alt_labels: {"la": "Res publica Romana", "fr": "République romaine", ...}`
   - `glosses: {"en": "ancient Roman state...", "fr": "état romain ancien...", ...}`
5. Enrich SFA prompts with multilingual vocabulary for cross-language reasoning

**Benefits:**
- Enhanced query matching across languages
- Richer context for LLM-based clustering and classification
- Support for non-English historical sources

#### **S.2.2 Cross-Lingual Entity Linking**

**Scenario:** User query in French: *"République romaine et ses consuls"*

**Workflow:**
1. Parse query, extract surface form: *"République romaine"*
2. Query BabelNet for French lexicalization → retrieves BabelNet synset `bn:00068294n`
3. Map synset to Wikidata QID (BabelNet includes Wikidata links) → Q17167
4. Retrieve SubjectConcept node with `wikidata_id: Q17167`
5. Execute graph query with language-agnostic identifier

**Benefits:**
- Normalize cross-language queries to canonical identifiers
- Support multilingual research workflows
- Expand retrieval with synonyms and related terms

#### **S.2.3 Facet-Aware Sense Disambiguation**

**Scenario:** Disambiguate "legion" in military vs. religious contexts.

**Workflow:**
1. SFA encounters term "legion" in text extraction
2. Query BabelNet → returns multiple synsets:
   - `bn:00051234n`: military unit (hypernym: armed forces)
   - `bn:00051235n`: large number (hypernym: multitude)
   - `bn:00051236n`: demon (hypernym: evil spirit)
3. **Facet filter:** Military SFA prioritizes military synset based on hypernym match
4. Store chosen `babelnet_id` on SubjectConcept as part of lexical profile
5. Use synset to inform CIDOC-CRM class alignment (E74 Group for military unit)

**Benefits:**
- Reduce ambiguity in multi-sense terms
- Align lexical choices with ontology structure
- Provide explainable reasoning for sense selection

#### **S.2.4 Graph-RAG Over SubjectConcept + BabelNet**

**Scenario:** Discover conceptual neighbors for "dictator" to propose new SubjectConcepts.

**Workflow:**
1. SubjectConcept exists for "Dictator (Roman)"
2. Query BabelNet synset relations: hypernyms (*magistrate*, *ruler*), hyponyms (*tyrant*, *autocrat*)
3. For each related synset, check if corresponding SubjectConcept exists
4. Propose new shell nodes for missing concepts (e.g., "Roman Magistrate")
5. Submit proposals through Subject Ontology Proposal validation pipeline

**Benefits:**
- Semi-automated ontology expansion
- Discover gaps in subject coverage
- Maintain lexical coherence across related concepts

---

### **S.3 Implementation Patterns**

#### **S.3.1 API Integration Pattern**

BabelNet follows the same federation API patterns documented in **Appendix R.10**.

**Cross-Reference:** See [Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration) for:
- R.10.1: Generic API request pattern with retry logic
- R.10.2: Wikidata API example (similar structure for BabelNet)
- R.10.9: Error handling patterns
- R.10.10: Rate limiting and caching strategies

#### **S.3.2 BabelNet API Access Example**

```python
import requests
from typing import Optional, Dict
import os

def fetch_babelnet_synset(synset_id: str, api_key: str = None) -> Optional[Dict]:
    """
    Fetch BabelNet synset with multilingual labels and glosses.
    
    Args:
        synset_id: BabelNet synset ID (e.g., 'bn:00068294n')
        api_key: BabelNet API key (defaults to BABELNET_API_KEY env var)
    
    Returns:
        JSON response with synset data, or None on error
    """
    api_key = api_key or os.getenv("BABELNET_API_KEY")
    if not api_key:
        raise ValueError("BabelNet API key required")
    
    API_URL = "https://babelnet.io/v9/getSynset"
    params = {
        "id": synset_id,
        "key": api_key,
        "targetLang": "EN,IT,FR,DE,ES,LA"  # Multilingual support
    }
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        # Standard pattern from R.10.1
        response = requests.get(
            API_URL, 
            params=params, 
            headers=headers, 
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limit exceeded - see R.10.10 for retry logic
            print(f"Rate limit exceeded: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"Timeout fetching synset {synset_id}")
        return None
    except Exception as e:
        print(f"Error fetching BabelNet synset: {e}")
        return None

def enrich_node_from_babelnet(node_id: str, wikidata_qid: str, label: str) -> Dict:
    """
    Enrich SubjectConcept node with BabelNet lexical data.
    
    Workflow:
    1. Query BabelNet for synsets matching label + QID
    2. Extract multilingual labels, glosses, synset relations
    3. Store babelnet_id, alt_labels, glosses on node
    4. Return enrichment metadata with confidence score
    """
    # Search BabelNet by Wikidata QID
    api_key = os.getenv("BABELNET_API_KEY")
    search_url = "https://babelnet.io/v9/getIds"
    params = {
        "lemma": label,
        "searchLang": "EN",
        "key": api_key,
        "source": f"WIKIDATA:{wikidata_qid}"
    }
    
    response = requests.get(search_url, params=params, timeout=30)
    if response.status_code == 200:
        synset_ids = response.json()
        if synset_ids:
            # Fetch full synset data for first match
            synset_data = fetch_babelnet_synset(synset_ids[0]["id"], api_key)
            if synset_data:
                return {
                    "babelnet_id": synset_ids[0]["id"],
                    "alt_labels": extract_multilingual_labels(synset_data),
                    "glosses": extract_glosses(synset_data),
                    "confidence": 0.80,  # Base confidence for BabelNet alignment
                    "source": "BabelNet v9"
                }
    
    return {"confidence": 0.0, "error": "No synset found"}

def extract_multilingual_labels(synset_data: Dict) -> Dict[str, str]:
    """Extract multilingual labels from BabelNet synset response."""
    labels = {}
    for sense in synset_data.get("senses", []):
        lang = sense.get("language", "")
        lemma = sense.get("properties", {}).get("fullLemma", "")
        if lang and lemma:
            labels[lang] = lemma
    return labels

def extract_glosses(synset_data: Dict) -> Dict[str, str]:
    """Extract glosses (short definitions) from BabelNet synset."""
    glosses = {}
    for gloss in synset_data.get("glosses", []):
        lang = gloss.get("language", "")
        text = gloss.get("gloss", "")
        if lang and text:
            glosses[lang] = text
    return glosses
```

#### **S.3.3 Caching and Rate Limiting**

**BabelNet API Limits:**
- **Free tier:** 1,000 requests/day
- **Paid subscription:** 10,000-100,000 requests/day (tiered pricing)

**Caching Strategy** (see Appendix R.10.10):
- Cache synset responses in Redis with 30-day TTL
- Use file-based cache for development: `cache/babelnet/{synset_id}.json`
- Cache key: `babelnet:synset:{synset_id}`

**Implementation:**
```python
import json
from pathlib import Path

def get_cached_synset(synset_id: str) -> Optional[Dict]:
    cache_path = Path(f"cache/babelnet/{synset_id}.json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return None

def cache_synset(synset_id: str, data: Dict):
    cache_path = Path(f"cache/babelnet/{synset_id}.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=2))
```

---

### **S.4 Confidence Scoring for BabelNet-Derived Properties**

#### **S.4.1 Base Confidence Levels**

**BabelNet Synset Alignment:** 0.75-0.85 confidence
- **Rationale:** BabelNet is a lexical/semantic authority, not a factual authority
- **Lower than Wikidata (0.90)** because:
  - Lexical relationships are more subjective than factual claims
  - Synset boundaries and sense distinctions vary by resource
  - Multilingual alignments introduce translation ambiguity

**Confidence Ranges:**
- **0.85:** BabelNet synset with Wikidata QID alignment + high statement count
- **0.80:** BabelNet synset with Wikidata QID alignment (standard case)
- **0.75:** BabelNet synset without Wikidata alignment (WordNet/Wikipedia only)

#### **S.4.2 Confidence Boost Patterns**

**BabelNet + Wikidata Alignment:** +0.05 confidence boost
- When BabelNet synset includes `WIKIDATA:Q12345` link and QID matches existing SubjectConcept
- Example: Base 0.80 → 0.85 with QID confirmation

**Multi-Source Lexical Convergence:** +0.10 confidence boost
- When BabelNet synset aligns with:
  - Wikidata QID
  - LCSH preferred term
  - FAST heading
- Example: Base 0.75 → 0.85 with triple alignment

**Facet-Specific Disambiguation:** +0.05 confidence boost
- When chosen synset hypernym matches facet domain
- Example: Military SFA selects military synset for "legion" → +0.05

#### **S.4.3 Confidence Degradation**

**Ambiguous Synset Selection:** -0.10 confidence penalty
- Multiple candidate synsets with similar scores
- No clear facet-based discriminator

**Missing Wikidata Link:** -0.05 confidence penalty
- BabelNet synset lacks Wikidata connection
- Reliance on WordNet/Wikipedia only

#### **S.4.4 Example Confidence Calculations**

**Scenario 1: High-Confidence Alignment**
- SubjectConcept: "Roman Republic" (wikidata_id: Q17167)
- BabelNet synset: bn:00068294n
- BabelNet includes: WIKIDATA:Q17167 link
- Synset has 15+ language lexicalizations
- **Confidence:** 0.80 (base) + 0.05 (QID match) = **0.85**

**Scenario 2: Medium-Confidence Alignment**
- SubjectConcept: "Roman Legion"
- BabelNet synset: bn:00051234n (military unit)
- Multiple candidate synsets, facet filter applied
- **Confidence:** 0.80 (base) + 0.05 (facet match) = **0.85**

**Scenario 3: Low-Confidence Alignment**
- SubjectConcept: "Ancient Assembly"
- BabelNet synset: bn:00012345n
- No Wikidata link, ambiguous sense
- **Confidence:** 0.75 (base) - 0.05 (no QID) - 0.10 (ambiguous) = **0.60**

---

### **S.5 Integration with SFA Workflow**

#### **S.5.1 Phase 3.5: Lexical Enrichment (Optional)**

**Position:** After Initialize Mode (Phase 3), before Ontology Proposal (Phase 4)

**Workflow:**
1. SFA completes Initialize Mode, creates SubjectConcept nodes with Wikidata enrichment
2. **Lexical Enrichment Phase (Optional):**
   - For each new SubjectConcept with `wikidata_id`:
     - Call `enrich_node_from_babelnet(node_id, wikidata_qid, label)`
     - Store `babelnet_id`, `alt_labels`, `glosses` on node properties
     - Log enrichment with confidence score
   - Skip nodes without Wikidata QID (cannot reliably align)
3. Proceed to Ontology Proposal with enriched lexical context

**Benefits:**
- Richer multilingual labels for clustering and classification
- Enhanced LLM prompts with glosses and synonyms
- Cross-language support for future queries

**Configuration:**
```python
# In facet_agent_framework.py
if config.get("babelnet_enrichment_enabled", False):
    for node in new_nodes:
        if node.get("wikidata_id"):
            enrichment = enrich_node_from_babelnet(
                node["id"], 
                node["wikidata_id"], 
                node["label"]
            )
            if enrichment.get("confidence", 0) >= 0.75:
                update_node_properties(node["id"], enrichment)
```

#### **S.5.2 Phase 5: Training Mode Disambiguation**

**Use Case:** Polysemous term disambiguation during claim generation

**Scenario:** Military SFA encounters "cohort" in text:
- Could mean: military unit, statistical group, companion group

**Workflow:**
1. Extract term "cohort" from historical text
2. Query BabelNet for synsets matching "cohort"
3. **Facet-aware filtering:**
   - Military SFA prioritizes synset with hypernym "military unit"
   - Filters out statistical/demographic senses
4. Store chosen `babelnet_id` on new SubjectConcept or claim metadata
5. Use synset to guide CIDOC-CRM class assignment

**Benefits:**
- Reduce ambiguity in extracted terms
- Align lexical choices with domain expertise
- Provide explainable term selection

**Cross-Reference:** See **Appendix T.3** (Training Mode workflow) for implementation details.

---

### **S.6 Configuration and Authentication**

#### **S.6.1 API Key Management**

**BabelNet API requires paid subscription** (after free tier exhaustion)

**Environment Variable:**
```bash
export BABELNET_API_KEY="your_api_key_here"
```

**Configuration in config.py:**
```python
BABELNET_CONFIG = {
    "api_key": os.getenv("BABELNET_API_KEY"),
    "base_url": "https://babelnet.io/v9",
    "rate_limit": 1000,  # requests/day for free tier
    "timeout": 30,  # seconds
    "cache_enabled": True,
    "cache_ttl": 2592000,  # 30 days
}
```

#### **S.6.2 Rate Limit Tracking**

**Free Tier:** 1,000 requests/day
- Track daily usage in Redis: `babelnet:usage:{date}`
- Implement circuit breaker when approaching limit

**Implementation:**
```python
import redis
from datetime import date

def check_rate_limit() -> bool:
    r = redis.Redis()
    today = date.today().isoformat()
    key = f"babelnet:usage:{today}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 86400)  # 24 hours
    return count <= 1000  # Free tier limit
```

#### **S.6.3 Fallback Strategies**

**When BabelNet Unavailable:**
1. **Use cached synsets** for previously seen terms
2. **Skip lexical enrichment** for new terms (graceful degradation)
3. **Fall back to Wikidata labels** only (mono-lingual)
4. **Log skipped enrichments** for manual review

---

### **S.7 Cross-References**

**Related Appendices:**
- **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#r10-api-implementation-patterns):** Federation API patterns (request structure, error handling, caching)
- **[Appendix T](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-t-subject-facet-agent-workflow---day-in-the-life):** SFA workflow integration points (Phase 3.5, Phase 5 disambiguation)
- **[Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf):** CIDOC-CRM alignment for lexical concepts (E55 Type for BabelNet synsets)
- **[Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns):** Wikidata integration patterns (primary fact authority)
- **[Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration):** Operational Modes (Initialize, Training)

**Implementation Files:**
- `scripts/federation/babelnet_client.py`: BabelNet API client (to be created)
- `scripts/agents/facet_agent_framework.py`: SFA orchestration with BabelNet integration
- `config.py`: BabelNet configuration settings

**External Resources:**
- BabelNet API Documentation: https://babelnet.io/guide
- BabelNet Paper (ACM 2012): https://dl.acm.org/doi/10.5555/2887533.2887534
- Multilingual Linked Data Report: http://www.w3.org/2015/09/bpmlod-reports/multilingual-dictionaries/

---

**(End of Appendix S)**

---

## **APPENDIX T: Subject Facet Agent Workflow - "Day in the Life"**

A newly instantiated SubjectFacetAgent (SFA) follows a structured workflow that ensures disciplined knowledge construction through schema introspection, state loading, federation bootstrap, ontology proposal, and training. This appendix documents the complete lifecycle of an SFA from instantiation to claim generation.

---

### **T.1 Wake-Up and Self-Orientation**

#### **T.1.1 Agent Instantiation**

**Factory Pattern:**
```python
from scripts.agents.facet_agent_framework import FacetAgentFactory

factory = FacetAgentFactory()
agent = factory.get_agent("military")  # or political, religious, economic, etc.
```

**Supported Facets:**
- `military`: Military units, campaigns, tactics, leadership
- `political`: Governments, institutions, offices, political events
- `religious`: Beliefs, practices, institutions, figures
- `economic`: Trade, currency, production, labor
- `cultural`: Arts, literature, daily life, customs
- `geographic`: Places, regions, territories, boundaries

#### **T.1.2 Schema Introspection (Step 1)**

**Purpose:** Learn "what is allowed" at the schema level before touching data.

**Actions:**
1. **Node schema introspection:**
   ```python
   schema = agent.introspect_node_label("SubjectConcept")
   # Returns: required properties, optional properties, tier, validation rules
   ```

2. **Layer 2.5 property discovery:**
   ```python
   properties = agent.get_layer25_properties()
   # Returns: P31 (instance of), P279 (subclass of), P361 (part of), etc.
   # These are the allowed Wikidata properties for hierarchy traversal
   ```

3. **Relationship discovery:**
   ```python
   relationships = agent.discover_relationships_between("Human", "Event")
   # Returns: PARTICIPATED_IN, COMMANDED, WITNESSED, etc.
   ```

**Output:** SFA now knows:
- Required properties for SubjectConcept nodes
- Valid Wikidata properties for federation
- Allowed relationship types for claims

**Cross-Reference:** See [Appendix M](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-m-identifier-safety-reference) for schema validation patterns.

---

### **T.2 Session Start: Load Current State**

#### **T.2.1 State Introspection (Step 2)**

**Purpose:** Learn "what already exists" and "what I have done before."

**Actions:**
```python
context = agent.get_session_context()
# Returns:
# - sample_nodes: Recent SubjectConcept nodes in this facet
# - sample_relationships: Recent relationships involving these nodes
# - pending_claims: Claims awaiting validation
# - agent_history: This agent's past contributions and promotion rate
# - meta_schema_version: Schema version for compatibility check
```

#### **T.2.2 Subgraph and Provenance Checks**

**Check for existing anchor:**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=200)
# Search for planned anchor node (e.g., "Roman Republic")
anchor_exists = any(node.label == "Roman Republic" for node in subgraph)
```

**Provenance analysis:**
```python
if anchor_exists:
    node_id = get_node_id("Roman Republic")
    claims = agent.find_claims_for_node(node_id)
    provenance = agent.get_node_provenance(node_id)
    # Avoid duplicate claims, understand existing coverage
```

**Agent contribution tracking:**
```python
contributions = agent.find_agent_contributions()
# Returns: claims_proposed, claims_promoted, claims_rejected, promotion_rate
# Use to adjust confidence thresholds
```

**Cross-Reference:** See [Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration) for state management patterns.

---

### **T.3 Initialize Mode: Bootstrap Domain from Wikidata**

#### **T.3.1 Mode Activation and Logging (Step 5)**

**Purpose:** Bootstrap a new domain area from a trusted Wikidata anchor.

**Execution:**
```python
result_init = agent.execute_initialize_mode(
    anchor_qid="Q17167",  # Roman Republic
    depth=2,  # Traverse hierarchy 2 levels deep
    autosubmit_claims=False,  # Manual review required
    ui_callback=ui_log_callback  # Real-time logging
)
```

#### **T.3.2 Initialize Mode Workflow**

**Step-by-Step Process:**

1. **Fetch Wikidata anchor entity:**
   ```python
   entity = fetch_wikidata_entity("Q17167")
   # Returns: labels, descriptions, aliases, statements, sitelinks
   ```

2. **Auto-enrich/create root SubjectConcept:**
   ```python
   node_id = enrich_node_from_wikidata(
       wikidata_qid="Q17167",
       facet="political",
       create_if_missing=True
   )
   # Sets: label, description, alt_labels, wikidata_id, statement_count
   ```

3. **Validate completeness (Step 3.5):**
   ```python
   completeness = validate_node_completeness(node_id)
   # Checks: required properties present, label/description quality
   # Returns: score 0.0-1.0, missing_fields, validation_errors
   if completeness["score"] < 0.70:
       log_warning("Low completeness", completeness)
       return  # Abort if below threshold
   ```

4. **Enrich with CIDOC-CRM alignment:**
   ```python
   enrich_with_ontology_alignment(node_id, entity)
   # Maps Wikidata P31 types to CIDOC-CRM classes
   # Sets: cidoc_crm_class (e.g., E74_Group, E4_Period)
   ```

5. **Traverse hierarchy with allowed properties:**
   ```python
   related = discover_hierarchy_from_entity(
       qid="Q17167",
       depth=2,
       properties=["P31", "P279", "P361", "P527"]  # From Layer 2.5
   )
   # Returns: related entities, relationship types, hierarchy structure
   ```

6. **Generate claims from Wikidata statements:**
   ```python
   claims = generate_claims_from_wikidata(
       node_id=node_id,
       entity=entity,
       base_confidence=0.90,  # Wikidata authority
       facet="political"
   )
   # Each claim enriched with CRMinf belief metadata
   # Tagged with facet, source, extraction_time
   ```

7. **Optional auto-submit high-confidence claims:**
   ```python
   if autosubmit_claims:
       for claim in claims:
           if claim["confidence"] >= 0.90:
               submit_claim_for_validation(claim)
   ```

8. **Log all actions:**
   ```python
   logger.log_action(
       action_type="INITIALIZE",
       node_id=node_id,
       details={"qid": "Q17167", "depth": 2, "claims_generated": len(claims)}
   )
   ```

**Output:**
```python
{
    "nodes_created": 15,
    "relationships_discovered": 42,
    "claims_generated": 68,
    "completeness_score": 0.87,
    "cidoc_crm_class": "E4_Period",
    "log_file": "logs/military_initialize_20260216_143022.json"
}
```

**Cross-Reference:** See [Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns) for Wikidata API patterns.

---

### **T.3.5 Lexical Enrichment (Optional)**

#### **T.3.5.1 BabelNet Integration Phase**

**Position:** After Initialize Mode (Phase 3), before Ontology Proposal (Phase 4)

**Purpose:** Enrich SubjectConcept nodes with multilingual labels, glosses, and synsets for enhanced cross-language support and semantic disambiguation.

**Workflow:**

1. **Check configuration:**
   ```python
   if config.get("babelnet_enrichment_enabled", False):
       api_key = os.getenv("BABELNET_API_KEY")
       if not api_key:
           log_warning("BabelNet enrichment skipped: API key not configured")
           return
   ```

2. **Enrich each new SubjectConcept:**
   ```python
   for node in result_init["nodes_created"]:
       if node.get("wikidata_id"):  # Require Wikidata alignment
           enrichment = enrich_node_from_babelnet(
               node_id=node["id"],
               wikidata_qid=node["wikidata_id"],
               label=node["label"]
           )
           
           if enrichment.get("confidence", 0) >= 0.75:
               # Store BabelNet data on node
               update_node_properties(node["id"], {
                   "babelnet_id": enrichment["babelnet_id"],
                   "alt_labels": json.dumps(enrichment["alt_labels"]),
                   "glosses": json.dumps(enrichment["glosses"]),
                   "babelnet_confidence": enrichment["confidence"]
               })
               
               log_action(
                   action_type="LEXICAL_ENRICHMENT",
                   node_id=node["id"],
                   details=enrichment
               )
   ```

3. **Handle enrichment failures gracefully:**
   ```python
   # Lexical enrichment is optional - don't block on failure
   try:
       enrich_from_babelnet()
   except BabelNetAPIError as e:
       log_warning(f"BabelNet enrichment failed: {e}")
       # Continue to Ontology Proposal without BabelNet data
   ```

**Benefits:**
- Multilingual query support (French, German, Latin, etc.)
- Richer context for LLM-based clustering in Ontology Proposal
- Term disambiguation during Training Mode

**Configuration:**
```python
# config.py
BABELNET_ENRICHMENT = {
    "enabled": True,
    "min_confidence": 0.75,
    "required_languages": ["EN", "LA", "FR", "DE"],
    "skip_on_failure": True  # Graceful degradation
}
```

**Cross-Reference:** See **[Appendix S](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-s-babelnet-lexical-authority-integration)** for detailed BabelNet integration patterns.

---

### **T.4 Subject Ontology Proposal (Bridge Step, via SCA Component)**

#### **T.4.1 Ontology Proposal Execution (Step 5 Bridge)**

**Purpose:** Structure discovered entities into conceptual clusters with claim templates and validation rules.

**Execution:**
```python
result_onto = agent.propose_subject_ontology(ui_callback=ui_log_callback)
```

#### **T.4.2 Ontology Proposal Workflow**

**Step-by-Step Process:**

1. **Collect entities from Initialize Mode:**
   ```python
   nodes = result_init["nodes_created"]
   # Each node has: label, wikidata_id, P31/P279 types
   ```

2. **Fetch full Wikidata entities:**
   ```python
   for node in nodes:
       entity = fetch_wikidata_entity(node["wikidata_id"])
       type_chains = extract_type_hierarchy(entity)  # P31/P279 chains
   ```

3. **LLM clustering pass:**
   ```python
   clusters = llm_cluster_types(
       types=type_chains,
       facet="military",
       prompt_template="cluster_military_concepts"
   )
   # Returns: conceptual clusters (e.g., Military Leadership, Military Operations)
   ```

4. **Convert clusters to ontology classes:**
   ```python
   ontology_classes = []
   for cluster in clusters:
       ontology_class = {
           "class_name": cluster["name"],
           "parent_class": cluster.get("parent", "SubjectConcept"),
           "member_count": len(cluster["members"]),
           "characteristics": cluster["description"],
           "example_members": cluster["members"][:5]
       }
       ontology_classes.append(ontology_class)
   ```

5. **Generate claim templates:**
   ```python
   templates = generate_claim_templates(ontology_classes)
   # Example: "All Military Commanders have property:rank with value:MilitaryRank"
   ```

6. **Define validation rules:**
   ```python
   rules = [
       {"type": "membership", "rule": "All members must have P31 pointing to class"},
       {"type": "cardinality", "rule": "rank property: 1-3 values per entity"},
       {"type": "temporal", "rule": "service dates must be within lifetime"},
       {"type": "cross_facet", "rule": "military unit must align with geographic location"}
   ]
   ```

7. **Compute strength score:**
   ```python
   strength_score = compute_ontology_strength(
       member_count=len(nodes),
       template_coverage=len(templates) / len(nodes),
       rule_coverage=len(rules)
   )
   # Returns: 0.0-1.0 score indicating ontology quality
   ```

8. **Store ontology on agent instance:**
   ```python
   agent.proposed_ontology = {
       "classes": ontology_classes,
       "templates": templates,
       "rules": rules,
       "strength_score": strength_score,
       "created_at": datetime.now().isoformat()
   }
   ```

**Output:**
```python
{
    "classes": [
        {
            "class_name": "MilitaryLeadership",
            "parent_class": "SubjectConcept",
            "member_count": 8,
            "characteristics": "Individuals who commanded military units...",
            "example_members": ["Julius Caesar", "Pompey", "Scipio Africanus"]
        },
        # ... more classes
    ],
    "templates": [
        "MilitaryLeadership has rank: MilitaryRank",
        "MilitaryLeadership commanded: MilitaryUnit"
    ],
    "rules": [...],
    "strength_score": 0.82
}
```

**Cross-Reference:** See [Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf) for CIDOC-CRM alignment during ontology proposal.

---

### **T.5 Training Mode: Extended Claim Generation**

#### **T.5.1 Training Mode Execution**

**Purpose:** Generate claims guided by proposed ontology, with validation and quality controls.

**Execution:**
```python
result_train = agent.execute_training_mode(
    max_iterations=50,
    target_claims=300,
    min_confidence=0.80,
    autosubmit_high_confidence=False,
    ui_callback=ui_log_callback
)
```

#### **T.5.2 Training Mode Workflow**

**Per-Node Processing Loop:**

1. **Reload context (detect inter-agent changes):**
   ```python
   context = agent.get_session_context()
   # See if other facets have added claims or nodes
   ```

2. **Prioritize nodes using ontology:**
   ```python
   priority_nodes = sort_by_ontology_class(
       nodes=context["sample_nodes"],
       ontology=agent.proposed_ontology
   )
   # Process high-priority classes first (e.g., MilitaryLeadership)
   ```

3. **For each node:**

   a. **Ensure Wikidata QID exists:**
   ```python
   if not node.get("wikidata_id"):
       enrichment = enrich_node_from_wikidata(node["id"])
       if not enrichment.get("wikidata_id"):
           log_warning(f"Skipping node {node['id']}: no QID")
           continue
   ```

   b. **Validate completeness:**
   ```python
   completeness = validate_node_completeness(node["id"])
   log_metric("completeness", completeness["score"])
   if completeness["score"] < 0.70:
       attempt_auto_enrichment(node["id"])
   ```

   c. **Fetch Wikidata entity:**
   ```python
   entity = fetch_wikidata_entity(node["wikidata_id"])
   ```

   d. **Generate claims filtered by ontology:**
   ```python
   claims = generate_claims_from_wikidata(
       node_id=node["id"],
       entity=entity,
       base_confidence=0.90,
       facet=agent.facet_key,
       templates=agent.proposed_ontology["templates"],  # Filter by templates
       rules=agent.proposed_ontology["rules"]  # Validate against rules
   )
   ```

   e. **Use BabelNet for polysemous term disambiguation:**
   ```python
   # NEW: BabelNet integration for ambiguous terms
   if claim.get("value_label") in POLYSEMOUS_TERMS:
       babelnet_synset = disambiguate_with_babelnet(
           term=claim["value_label"],
           facet=agent.facet_key,
           context=node["label"]
       )
       if babelnet_synset:
           claim["babelnet_synset"] = babelnet_synset["synset_id"]
           claim["sense_gloss"] = babelnet_synset["gloss"]
   ```
   **Cross-Reference:** See **[Appendix S.5](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#s52-phase-5-training-mode-disambiguation)** for BabelNet disambiguation patterns.

   f. **Enrich claims with CRMinf:**
   ```python
   for claim in claims:
       enrich_claim_with_crminf(
           claim=claim,
           belief_type="I4_Proposition_Set",
           confidence=claim["confidence"]
       )
   ```

   g. **Validate CIDOC alignment:**
   ```python
   cidoc_valid = validate_cidoc_alignment(node["id"], claim)
   if not cidoc_valid:
       log_warning(f"CIDOC alignment failed for claim {claim['id']}")
       claim["confidence"] *= 0.90  # Confidence penalty
   ```

   h. **Filter by minimum confidence:**
   ```python
   claims = [c for c in claims if c["confidence"] >= min_confidence]
   ```

   i. **Auto-submit high-confidence claims:**
   ```python
   if autosubmit_high_confidence:
       for claim in claims:
           if claim["confidence"] >= 0.90:
               submit_claim_for_validation(claim)
   ```

   j. **Log each claim proposal:**
   ```python
   for claim in claims:
       logger.log_action(
           action_type="CLAIM_PROPOSED",
           node_id=node["id"],
           details={
               "label": claim["label"],
               "confidence": claim["confidence"],
               "rationale": claim["rationale"]
           }
       )
   ```

4. **Track metrics:**
   ```python
   metrics = {
       "nodes_processed": iteration_count,
       "claims_proposed": total_claims,
       "avg_confidence": mean(claim_confidences),
       "avg_completeness": mean(completeness_scores),
       "claims_per_second": total_claims / elapsed_time
   }
   ```

**Output:**
```python
{
    "nodes_processed": 45,
    "claims_proposed": 287,
    "avg_confidence": 0.86,
    "avg_completeness": 0.83,
    "claims_per_second": 2.4,
    "log_file": "logs/military_training_20260216_150345.json"
}
```

**Cross-Reference:** See [Appendix N](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-n-property-extensions--advanced-attributes) for advanced claim properties.

---

### **T.6 Between Tasks: Collaboration and Introspection**

#### **T.6.1 Cross-Facet Awareness**

**Monitor other facets:**
```python
# Check pending claims from all facets
all_pending = list_pending_claims()  # No facet filter

# Adjust behavior based on system load
if len(all_pending) > 1000:
    # Reduce proposal rate if validation queue is backed up
    agent.proposal_rate *= 0.75
```

#### **T.6.2 Self-Monitoring**

**Track promotion rate:**
```python
contributions = agent.find_agent_contributions()
promotion_rate = contributions["claims_promoted"] / contributions["claims_proposed"]

if promotion_rate < 0.70:
    # Increase confidence threshold if many claims are rejected
    agent.min_confidence += 0.05
    log_warning(f"Low promotion rate ({promotion_rate:.2f}), increasing threshold")
```

#### **T.6.3 Provenance Analysis**

**Understand node history:**
```python
for node in priority_nodes:
    provenance = get_node_provenance(node["id"])
    claim_history = get_claim_history(node["id"])
    
    # Avoid duplicate claims
    existing_claims = [c["label"] for c in claim_history]
    new_claims = [c for c in proposed_claims if c["label"] not in existing_claims]
```

**Cross-Reference:** See [Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration) for multi-agent coordination patterns.

---

### **T.7 End of "Day": Session Summary**

#### **T.7.1 Logger Summary**

**Final metrics:**
```python
summary = logger.generate_summary()
# Returns:
# - action_counts: {INITIALIZE: 1, REASONING: 45, QUERY: 203, CLAIM_PROPOSED: 287}
# - error_counts: {API_TIMEOUT: 3, VALIDATION_FAILED: 12}
# - claim_stats: {proposed: 287, high_confidence: 198, low_confidence: 89}
# - completeness_avg: 0.83
# - session_duration: 4520.3 seconds
```

#### **T.7.2 Persistence (Future Work)**

**Store ontology:**
```python
# Future: persist ontology for next session
save_ontology(
    facet=agent.facet_key,
    ontology=agent.proposed_ontology,
    version=agent.ontology_version
)
```

**Store session metrics:**
```python
# Future: track agent performance over time
save_session_metrics(
    agent_id=agent.agent_id,
    metrics=summary,
    timestamp=datetime.now()
)
```

---

### **T.8 Federation Enrichment Integration**

#### **T.8.1 Multi-Authority Enrichment Pattern**

**Purpose:** Enrich SubjectConcept nodes with data from multiple federation authorities beyond Wikidata.

**Workflow Position:** After Phase 3 (Initialize Mode), optionally before or alongside Phase 3.5 (Lexical Enrichment)

**Supported Authorities:**
- **Pleiades:** Ancient place identifiers and coordinates
- **VIAF:** Person authority with multi-national library identifiers
- **GeoNames:** Geographic name authority with modern coordinates
- **FAST:** Subject heading alignment
- **TGN:** Getty Thesaurus of Geographic Names

**Implementation:**
```python
def enrich_node_from_federation(
    node_id: str,
    authorities: List[str] = ["pleiades", "viaf", "geonames"]
) -> Dict:
    """
    Enrich node with data from multiple federation authorities.
    
    Follows patterns from Appendix R.10.
    """
    enrichments = {}
    
    for authority in authorities:
        try:
            if authority == "pleiades" and node.get("entity_type") == "Place":
                pleiades_data = enrich_from_pleiades(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if pleiades_data:
                    enrichments["pleiades_id"] = pleiades_data["id"]
                    enrichments["ancient_coordinates"] = pleiades_data["coords"]
                    enrichments["confidence"] = 0.85
            
            elif authority == "viaf" and node.get("entity_type") == "Person":
                viaf_data = enrich_from_viaf(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if viaf_data:
                    enrichments["viaf_id"] = viaf_data["id"]
                    enrichments["library_identifiers"] = viaf_data["identifiers"]
                    enrichments["confidence"] = 0.85
            
            elif authority == "geonames":
                geonames_data = enrich_from_geonames(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if geonames_data:
                    enrichments["geonames_id"] = geonames_data["id"]
                    enrichments["modern_coordinates"] = geonames_data["coords"]
                    enrichments["confidence"] = 0.80
        
        except FederationAPIError as e:
            log_warning(f"{authority} enrichment failed: {e}")
            continue
    
    # Stack evidence from multiple sources
    if len(enrichments) > 1:
        enrichments["confidence"] = min(0.95, enrichments["confidence"] + 0.10)
    
    return enrichments
```

**Usage in Initialize Mode:**
```python
# After creating SubjectConcept nodes from Wikidata
for node in result_init["nodes_created"]:
    if config.get("federation_enrichment_enabled", True):
        federation_data = enrich_node_from_federation(
            node_id=node["id"],
            authorities=["pleiades", "viaf", "geonames"]
        )
        if federation_data:
            update_node_properties(node["id"], federation_data)
```

**Confidence Stacking:**
- **Single authority:** 0.80-0.85 confidence
- **Two authorities:** +0.10 boost → 0.90-0.95
- **Three+ authorities:** +0.15 boost → 0.95-1.00 (capped)

**Cross-Reference:** See **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#r10-api-implementation-patterns)** for detailed API implementation patterns for each authority.

---

### **T.9 Error Recovery and Retry Patterns**

#### **T.9.1 API Timeout Handling**

**Pattern from Appendix R.10.10:**
```python
import time
from typing import Optional

def fetch_with_retry(
    fetch_func,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    timeout: int = 30
) -> Optional[Dict]:
    """
    Retry API calls with exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            return fetch_func(timeout=timeout)
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                log_warning(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                log_error("Max retries exceeded, giving up")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = int(e.response.headers.get("Retry-After", 60))
                log_warning(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
    return None
```

**Usage in Training Mode:**
```python
entity = fetch_with_retry(
    lambda timeout: fetch_wikidata_entity(node["wikidata_id"], timeout=timeout),
    max_retries=3
)
if not entity:
    log_error(f"Failed to fetch entity for node {node['id']}")
    continue  # Skip this node, move to next
```

#### **T.9.2 Completeness Validation Failures**

**Scenario:** Node fails completeness check (Step 3.5)

**Recovery Strategy:**
```python
completeness = validate_node_completeness(node_id)

if completeness["score"] < 0.70:
    # Attempt auto-enrichment
    missing_fields = completeness["missing_fields"]
    
    if "description" in missing_fields:
        # Fetch from Wikidata if not already present
        entity = fetch_wikidata_entity(node["wikidata_id"])
        if entity.get("descriptions", {}).get("en"):
            update_node_property(
                node_id,
                "description",
                entity["descriptions"]["en"]["value"]
            )
    
    if "alt_labels" in missing_fields:
        # Fetch from BabelNet or Wikidata aliases
        alt_labels = fetch_alt_labels(node["wikidata_id"])
        if alt_labels:
            update_node_property(node_id, "alt_labels", json.dumps(alt_labels))
    
    # Re-validate
    completeness = validate_node_completeness(node_id)
    
    if completeness["score"] < 0.70:
        log_warning(f"Node {node_id} still incomplete after enrichment")
        # Mark for manual review
        tag_node_for_review(node_id, reason="low_completeness")
```

#### **T.9.3 Claim Validation Errors**

**Scenario:** Generated claim fails validation rules

**Recovery Strategy:**
```python
def generate_and_validate_claims(node_id, entity, ontology_rules):
    claims = generate_claims_from_wikidata(node_id, entity)
    
    validated_claims = []
    for claim in claims:
        validation = validate_claim(claim, ontology_rules)
        
        if validation["valid"]:
            validated_claims.append(claim)
        else:
            # Attempt to fix common validation errors
            if validation["error"] == "missing_temporal_bound":
                # Add default temporal bound from entity lifespan
                claim["temporal_start"] = entity.get("birth_date")
                claim["temporal_end"] = entity.get("death_date")
                
                # Re-validate
                validation = validate_claim(claim, ontology_rules)
                if validation["valid"]:
                    validated_claims.append(claim)
                else:
                    log_warning(f"Claim {claim['id']} still invalid after fix")
            
            elif validation["error"] == "cardinality_violation":
                # Lower confidence and flag for review
                claim["confidence"] *= 0.80
                claim["validation_warning"] = validation["error"]
                validated_claims.append(claim)
            
            else:
                # Cannot auto-fix, log and skip
                log_error(f"Claim validation failed: {validation['error']}")
    
    return validated_claims
```

**Cross-Reference:** See [Appendix R.10.9](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration) for federation-specific error handling.

---

### **T.10 Cross-References**

**Related Appendices:**
- **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration):** Federation API implementation patterns, error handling, caching
- **[Appendix S](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-s-babelnet-lexical-authority-integration):** BabelNet lexical enrichment (Phase 3.5, Training Mode disambiguation)
- **[Appendix O](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-o-facet-training-resources-registry):** Training resources for facet-specific knowledge
- **[Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf):** CIDOC-CRM alignment during enrichment
- **[Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration):** Operational modes (Initialize, Training, Validation)
- **[Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns):** Wikidata integration patterns
- **[Appendix M](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-m-identifier-safety-reference):** Schema validation and identifier safety

**Implementation Files:**
- `scripts/agents/facet_agent_framework.py`: SFA orchestration and workflow
- `scripts/agents/subject_concept_agent.py`: SubjectConceptAgent (SCA) for ontology proposal
- `scripts/federation/wikidata_client.py`: Wikidata API client
- `scripts/federation/babelnet_client.py`: BabelNet API client (to be created)
- `scripts/validation/completeness_validator.py`: Completeness validation (Step 3.5)
- `scripts/logging/agent_logger.py`: Agent action logging

**Key Integration Points:**
- **Phase 1:** Schema introspection (STEP_1_COMPLETE.md)
- **Phase 2:** State loading (STEP_2_COMPLETE.md)
- **Phase 3:** Initialize Mode (STEP_5_COMPLETE.md)
- **Phase 3.5:** Completeness validation (STEP_3_COMPLETE.md)
- **Phase 4:** CIDOC-CRM enrichment (STEP_4_COMPLETE.md)
- **Phase 5:** Subject Ontology Proposal (STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- **Phase 6:** Training Mode (STEP_3_COMPLETE.md, STEP_5_COMPLETE.md)

---

**(End of Appendix T)**

---

## **Appendix U: ADR-001 - Claim Identity and Content-Addressable Ciphers**

### **ADR-001: Content-Only Cipher for Claim Identity**

**Status:** ACCEPTED (2026-02-16)  
**Deciders:** Architecture Review  
**Date:** 2026-02-16

---

### **Context and Problem Statement**

Claims in the Chrystallum knowledge graph require unique, stable identifiers that enable:
1. **Automatic deduplication** when multiple agents extract the same assertion
2. **Cryptographic verification** of claim integrity across federated institutions
3. **Consensus aggregation** across facets without duplicate claim nodes
4. **Provenance tracking** for confidence evolution and agent accountability

**The Problem:** Initial architecture specifications contained an internal contradiction about what data should be included in the claim cipher (content-addressable hash).

**Conflicting Specifications:**
- **Section 6.4.1** (original): Included `confidence_score`, `extractor_agent_id`, and `extraction_timestamp` in cipher generation
- **Section 6.4.3** (verification pattern): Explicitly excluded confidence, agent, and timestamp with comment "NO confidence, NO agent, NO timestamp!"
- **Section 6.4.2** (deduplication example): Showed two agents extracting at different times producing identical ciphers (impossible if timestamp is in hash)

**Impact:** This inconsistency would break:
- Deduplication (same content extracted by different agents → different ciphers → duplicate nodes)
- Federation (institutions couldn't verify claims with different provenance metadata)
- Consensus (same assertion by multiple facets would create separate claim nodes)

---

### **Decision**

**We adopt Model 1: Content-Only Cipher**

**Claim cipher includes ONLY assertion content:**
- ✅ `source_work_qid` (where was it stated?)
- ✅ `passage_text_hash` (what text supports it?)
- ✅ `subject_entity_qid` (subject of assertion)
- ✅ `object_entity_qid` (object of assertion)
- ✅ `relationship_type` (predicate/relationship)
- ✅ `action_structure` (W5H1/facet-specific semantics)
- ✅ `temporal_data` (when did it occur?)
- ✅ `facet_id` (which facet perspective?)

**Claim cipher EXCLUDES provenance metadata:**
- ❌ `confidence_score` (changes as reviews accumulate)
- ❌ `extractor_agent_id` (different agents can extract same claim)
- ❌ `extraction_timestamp` (extraction time ≠ assertion content)

**Provenance is tracked separately:**
- **FacetPerspective nodes** with `PERSPECTIVE_ON` edges to the Claim node
- Each perspective stores: `agent_id`, `extraction_timestamp`, `confidence`, `contributing_agent`, `rationale`
- Multiple perspectives on same cipher = consensus signal

---

### **Rationale**

**Why Content-Only?**

1. **Stable Identity Across Time and Agents**
   - Same assertion extracted in 2026 and 2030 → same cipher
   - Multiple agents independently discovering same claim → single Claim node
   - Enables true deduplication and consensus detection

2. **Cryptographic Verification Works**
   - Institution A publishes claim with cipher X
   - Institution B downloads and recomputes cipher from content
   - Verification succeeds because cipher depends only on content, not A's metadata
   - Provenance differences don't break verification

3. **Consensus Aggregation is Possible**
   - Political SFA extracts claim at 10:00 AM → cipher ABC
   - Military SFA extracts same claim at 14:00 PM → cipher ABC (same!)
   - Graph query: "How many facets agree on cipher ABC?" → consensus score
   - Without content-only cipher: two separate claim nodes → no consensus detected

4. **Confidence Evolution Doesn't Break Identity**
   - Initial extraction: confidence = 0.75
   - After review: confidence = 0.90
   - Cipher remains unchanged (content hasn't changed, just our belief in it)
   - Federated institutions can track confidence separately without re-hashing

5. **Alignment with Verification Pattern**
   - Section 6.4.3 verification query already excludes confidence/agent/timestamp
   - This ADR makes the generation pattern match the verification pattern
   - Single source of truth for "what makes a claim unique"

---

### **Consequences**

**Positive:**
- ✅ Automatic deduplication works reliably
- ✅ Multiple agents → single claim + multiple perspectives → consensus signal
- ✅ Cryptographic verification across institutions is possible
- ✅ Cipher remains stable as reviews/confidence evolve
- ✅ Federation across Chrystallum instances is feasible
- ✅ Graph queries for consensus are efficient (GROUP BY cipher)

**Negative:**
- ⚠️ Two claims with identical content but different facet perspectives still get different ciphers (facet_id is in hash)
  - **Mitigation:** This is intentional - "Caesar crossed Rubicon" from POLITICAL facet vs. MILITARY facet are legitimately different perspectives
  - FacetPerspective nodes allow cross-facet consensus tracking
- ⚠️ Requires careful normalization of content fields (Unicode, whitespace, date formats)
  - **Mitigation:** Appendix U.2 specifies canonical normalization functions
- ⚠️ Provenance metadata must be stored separately (cannot be embedded in cipher)
  - **Mitigation:** FacetPerspective + PERSPECTIVE_ON edges provide rich provenance model

**Neutral:**
- 🔄 Cipher is facet-aware (facet_id included) rather than pure content
  - **Rationale:** Each facet may interpret same source differently (e.g., "Caesar crossed Rubicon" has distinct POLITICAL, MILITARY, and GEOGRAPHIC dimensions)
  - Consensus detection still works via FacetPerspective aggregation on same cipher

---

### **Implementation Requirements**

**1. Canonical Normalization (REQUIRED)**

All fields in cipher computation MUST be normalized:

```python
def compute_claim_cipher(claim_content: dict) -> str:
    """Generate content-only cipher with canonical normalization."""
    import hashlib, json, unicodedata
    
    # Normalize each component
    components = [
        normalize_unicode(claim_content['source_work_qid']),
        claim_content['passage_text_hash'],  # Already a hash
        normalize_unicode(claim_content['subject_entity_qid']),
        normalize_unicode(claim_content['object_entity_qid']),
        normalize_unicode(claim_content['relationship_type']),
        normalize_json(claim_content['action_structure']),
        normalize_iso8601(claim_content['temporal_data']),
        normalize_unicode(claim_content['facet_id'])
    ]
    
    # Concatenate with delimiter
    canonical_string = '||'.join(components)
    
    # SHA-256 hash with prefix
    cipher = hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
    return f"claim_{cipher[:40]}"  # claim_abc123...

def normalize_unicode(text: str) -> str:
    """Unicode NFC normalization + strip whitespace."""
    return unicodedata.normalize('NFC', text.strip())

def normalize_json(obj: dict) -> str:
    """Canonical JSON: sorted keys, no whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))

def normalize_iso8601(date_str: str) -> str:
    """ISO 8601 extended format with zero-padding."""
    # Example: "-49-01-10" → "-0049-01-10"
    # Ensures consistent format for negative years
    return format_iso8601_extended(date_str)
```

**2. Verification Pattern (REQUIRED)**

All cipher verification queries MUST exclude provenance:

```cypher
// Recompute cipher from content ONLY
MATCH (c:Claim {cipher: $claimed_cipher})
WITH c,
  compute_cipher_hash(
    c.source_work_qid,
    c.passage_text_hash,
    c.subject_entity_qid,
    c.object_entity_qid,
    c.relationship_type,
    c.action_structure,
    c.temporal_data,
    c.facet_id
    // NO confidence, NO agent, NO timestamp!
  ) AS recomputed_cipher
RETURN 
  c.cipher = recomputed_cipher AS integrity_verified,
  c.cipher AS original_cipher,
  recomputed_cipher AS computed_cipher
```

**3. Provenance Storage Pattern (REQUIRED)**

Provenance MUST be stored in separate FacetPerspective nodes:

```cypher
// Create claim with first perspective
MERGE (claim:Claim {cipher: $cipher})
  ON CREATE SET 
    claim.source_work_qid = $content.source,
    claim.subject_entity_qid = $content.subject,
    // ... other content fields

// Create perspective node (provenance)
CREATE (perspective:FacetPerspective {
  perspective_id: randomUUID(),
  facet_key: $provenance.facet,
  parent_claim_cipher: $cipher,
  confidence: $provenance.confidence,
  contributing_agent: $provenance.agent_id,
  assertion_timestamp: $provenance.timestamp,
  rationale: $provenance.rationale
})-[:PERSPECTIVE_ON]->(claim)

RETURN claim.cipher AS cipher, perspective.perspective_id AS perspective_id
```

**4. Consensus Detection Pattern (ENABLED)**

```cypher
// Find claims with multi-facet consensus
MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim)
WITH c, count(DISTINCT p.facet_key) AS facet_count,
     avg(p.confidence) AS avg_confidence
WHERE facet_count >= 2  // At least 2 facets agree
RETURN c.cipher, facet_count, avg_confidence
ORDER BY facet_count DESC, avg_confidence DESC
```

---

### **Migration Path**

**For Existing Claims (if any):**

1. **Audit Phase:**
   ```cypher
   // Find claims with provenance in cipher (old model)
   MATCH (c:Claim)
   WHERE c.extractor_agent_id IS NOT NULL 
      OR c.extraction_timestamp IS NOT NULL
   RETURN count(c) AS claims_needing_migration
   ```

2. **Migrate Phase:**
   ```cypher
   // Extract provenance to FacetPerspective, recompute cipher
   MATCH (c:Claim)
   WHERE c.extractor_agent_id IS NOT NULL
   WITH c, compute_content_only_cipher(c) AS new_cipher
   
   // Create perspective node with old provenance
   CREATE (p:FacetPerspective {
     facet_key: c.facet_id,
     confidence: c.confidence_score,
     contributing_agent: c.extractor_agent_id,
     assertion_timestamp: c.extraction_timestamp
   })
   
   // Update claim with new cipher, remove provenance fields
   SET c.cipher = new_cipher
   REMOVE c.confidence_score, c.extractor_agent_id, c.extraction_timestamp
   
   // Link perspective to claim
   CREATE (p)-[:PERSPECTIVE_ON]->(c)
   ```

3. **Verify Phase:**
   ```cypher
   // Verify all ciphers can be recomputed
   MATCH (c:Claim)
   WITH c, compute_content_only_cipher(c) AS recomputed
   WHERE c.cipher <> recomputed
   RETURN c.cipher, recomputed, "MISMATCH" AS status
   // Should return 0 rows
   ```

---

### **Related Decisions**

- **ADR-002** (future): Trust model for federated claims (signatures, transparency log, key distribution)
- **ADR-003** (future): Facet taxonomy canonicalization (single registry, uppercase enforcement)
- **Appendix R**: Federation Strategy (multi-authority integration, confidence bumps)
- **Section 6.4**: Content-Addressable Claim Identification (implementation of this ADR)

---

### **References**

- Architecture Review 2026-02-16 (md/Architecture/2-16-26-architecture review.txt)
- Section 6.4.1: Claim Cipher Generation (corrected 2026-02-16)
- Section 6.4.2: Automatic Deduplication (corrected 2026-02-16)
- Section 6.4.3: Verification Query Pattern (already correct)
- Section 5.5.3: Claim Architecture - Cipher + Star Pattern

---

**(End of Appendix U - ADR-001)**

---

