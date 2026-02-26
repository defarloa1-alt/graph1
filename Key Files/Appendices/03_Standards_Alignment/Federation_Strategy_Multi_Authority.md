# Appendix R: Federation Strategy & Multi-Authority Integration

**Version:** 4.0  
**Date:** 2026-02-25  
**Status:** Current — supersedes v3.2 (February 19, 2026)  
**Change summary:** Added DPRR as confirmed operational federation; scoping source hierarchy updated; Project Mercury (numismatic) added as next target; OCD integration path documented; SFA constitution model replaces Methods Agent framing; Phase 1/2/3 model from FEDERATION_ARCHITECTURE.md incorporated.

---

## Navigation

**Main Architecture:**
- [ARCHITECTURE_CORE.md](../../ARCHITECTURE_CORE.md)
- [ARCHITECTURE_ONTOLOGY.md](../../ARCHITECTURE_ONTOLOGY.md)
- [ARCHITECTURE_IMPLEMENTATION.md](../../ARCHITECTURE_IMPLEMENTATION.md)
- [ARCHITECTURE_GOVERNANCE.md](../../ARCHITECTURE_GOVERNANCE.md)

**Appendices Index:** [README.md](../README.md)

**Supporting documents:**
- [docs/FEDERATION_ARCHITECTURE.md](../../docs/FEDERATION_ARCHITECTURE.md) — Phase 1/2/3 pipeline model
- [docs/BASELINE_POST_DPRR_2026-02-25.md](../../docs/BASELINE_POST_DPRR_2026-02-25.md) — Post-DPRR graph state
- [docs/IMPORT_DECISIONS.md](../../docs/IMPORT_DECISIONS.md) — DPRR reification decision (Option A)
- [docs/HARVESTER_SCOPING_DESIGN.md](../../docs/HARVESTER_SCOPING_DESIGN.md) — Scoping rules per source

---

## R.1 Federation Architecture Principles

### R.1.1 Wikidata as Federation Broker, Not Final Authority

Wikidata functions as the **identity hub and router** in the federation architecture:

- **Discovery layer**: Provides QIDs, labels, descriptions, and external identifier properties (P214, P1584, P1566, P6863, P9106, etc.)
- **Routing mechanism**: External ID properties serve as jump-off points to domain authorities
- **Confidence positioning**: Layer 2 federation with confidence floor 0.90
- **Epistemic status**: Treated as broad identity hint, not canonical source

Wikidata assertions are *discovery inputs*, not *verified outputs*. When a domain authority and Wikidata disagree, the domain authority wins — domain authorities provide the canonical data, Wikidata provides the reach.

### R.1.2 Two-Phase Federation Model

Federation follows a two-phase architecture defined in [docs/FEDERATION_ARCHITECTURE.md](../../docs/FEDERATION_ARCHITECTURE.md):

**Phase 1: Federation as Gate**  
Federation IDs validate that a harvested Wikidata entity is genuinely domain-relevant (scoping). The gate runs at harvest time. An entity with a Pleiades ID is confirmed as an ancient place; an entity with a DPRR ID is confirmed as a Republican-period person. The gate writes `scoping_status`, `scoping_confidence`, and `scoping_source` onto Entity nodes.

**Phase 2: Federation as Source**  
Federation APIs are interrogated for what Wikidata does not carry: primary source citations, attestation records, variant name forms, social network data, geographic precision, uncertainty metadata. Phase 2 runs as a separate enrichment pass over scoped entities, writing claims with full PROV-O provenance (source: trismegistos, source: lgpn, etc.).

**Phase 3: SFA Reasoning**  
Specialist Facet Agents reason over an entity layer that has Wikidata's ontological breadth AND the federations' primary source depth. The quality difference from reasoning over Wikidata alone is qualitative, not just quantitative — the narrative layer can cite attestations, trace social networks, and flag contested identifications.

**Design constraint**: Phase 1 must not close off Phase 2. Federation IDs must be persisted on Entity nodes (not just used as filters and discarded). Federation fetch functions must be kept separate from the scoping gate. Federation fetches must be logged for idempotency.

### R.1.3 Scoping Source Hierarchy

As of 2026-02-25, four sources can confer temporal scoping on a Wikidata entity:

| Source | Property / Signal | Confidence | Domain |
|--------|-------------------|------------|--------|
| Trismegistos | P1696 (TM person) or P4230 (TM text) | 0.95 | Papyrological/epigraphic persons and documents |
| LGPN | P1838 (LGPN ID) | 0.93 | Greek personal names, prosopography |
| Pleiades | P1584 (Pleiades ID) | 0.92 | Ancient places |
| DPRR | P6863 (DPRR ID) or `dprr_imported = true` | 0.85 | Roman Republican persons and offices |

An entity with any of these IDs is classified `temporal_scoped`. Entities with domain-specific authority file presence (VIAF, Getty AAT) but no temporal anchor are classified `domain_scoped`. Entities with neither are `unscoped`.

The 8.9% global unscoped rate as of 2026-02-25 represents the genuine noise floor — entities harvested from Wikidata with no confirming federation presence. See [docs/BASELINE_POST_DPRR_2026-02-25.md](../../docs/BASELINE_POST_DPRR_2026-02-25.md).

### R.1.4 Two-Hop Enrichment Pattern

Federation follows a systematic two-hop pattern: Wikidata → external ID → domain authority.

```
// Hop 1: Wikidata resolution
MATCH (candidate:Entity {label: "Emerita Augusta"})
MERGE (wd:WikidataEntity {qid: "Q13560"})
CREATE (candidate)-[:ALIGNED_WITH]->(wd)

// Hop 2: Domain authority enrichment via P1584
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)
// → fetch Pleiades record, write back to candidate with source provenance
```

This pattern ensures:
1. Broad discovery via Wikidata's extensive coverage
2. Deep grounding via specialist authorities
3. Provenance tracking at each hop
4. Confidence scoring based on federation depth

### R.1.5 Reification Policy

**Edge provenance (Option A)** is used for secondary-source federations where claims are not contested between sources:

```
(Caesar)-[:FATHER_OF {
  source: "dprr",
  dprr_assertion_uri: "http://romanrepublic.ac.uk/rdf/entity/RelationshipAssertion/1234",
  secondary_source: "Zmeskal_Adfinitas",
  confidence: 0.85
}]->(Octavian)
```

**Claim node reification (Option B)** is reserved for SFA-generated claims that contest existing assertions — e.g. "Livy suggests a different paternity than Zmeskal records." Option A and Option B coexist in the graph without conflict. See [docs/IMPORT_DECISIONS.md](../../docs/IMPORT_DECISIONS.md) for the full decision rationale.

---

## R.2 Operational Federations

The table below summarizes what each federation can and cannot provide to SFAs and the pipeline: whether it can confer scoping, what kind of evidence it carries, and any notable licensing constraints.

| Federation | Scoping role | Evidence type | Names / onomastics | Social network / careers | Geography / periods | Licensing / access |
|------------|-------------|---------------|--------------------|--------------------------|---------------------|--------------------|
| Wikidata | Discovery only | Secondary summary | Yes (labels, AKA) | Light (some properties) | Yes (GeoNames links, basic dates) | CC0; REST + SPARQL; identity broker, not canon |
| Pleiades | Temporal + domain | Secondary (places) | Yes (ancient/modern) | Limited (place connections) | Strong (coords, period validity, relations) | CC-BY; JSON API + dumps |
| DPRR | Temporal + domain | Secondary prosop. | Yes (elite Romans) | Strong (offices, kin, status) | Indirect (via office dates) | MIT; SPARQL endpoint |
| Trismegistos | Temporal | Primary docs | Yes (persons, places) | Strong (attestations, kin) | Strong (doc findspots, date ranges) | Download (license check); CSV |
| LGPN | Temporal + domain | Primary onomastic | Very strong | Moderate (prosopographic links) | Strong (name distribution, periods) | Download (license check) |
| PeriodO | Temporal | Secondary (periods) | No | No | Very strong (curated period definitions) | Open JSON dataset |
| LCSH/FAST/LCC | Domain (subjects) | Secondary subjects | Yes (subject forms) | No | Indirect (topical periods) | Varied; LCSH/FAST via LC, OCLC |
| Getty AAT | Domain (concepts) | Secondary concepts | Yes (multilingual) | No | Indirect (concept scope, facets) | Open LOD; JSON, SPARQL |
| VIAF | Domain (names) | Secondary authority | Very strong | No | No | Open; REST |
| CHRR | Temporal + material | Primary material | No (coins via Nomisma) | No | Strong (hoard findspots, burial dates) | ODbL; CSV + RDF |
| CRRO | Temporal + material | Primary/secon. numismatics | No (via issuers) | Indirect (issuer–coin links) | Moderate (issue dates, mints) | CC-BY; RDF |

---

### R.2.1 DPRR (Digital Prosopography of the Roman Republic)

**Status**: Operational — imported 2026-02-25  
**License**: MIT  
**SPARQL endpoint**: `http://romanrepublic.ac.uk/rdf/endpoint/`  
**Wikidata property**: P6863  
**Alignment coverage**: 3,018 of 4,876 DPRR persons have P6863 in Wikidata (~62%)

**What DPRR provides:**
- 4,876 persons from Roman Republican elite (senators, magistrates, priests, equestrians)
- 9,807 PostAssertions — offices held with year, sourced from Broughton's *Magistrates of the Roman Republic*
- 6,928 RelationshipAssertions — family and social relationships sourced from Zmeskal's *Adfinitas*
- 1,992 StatusAssertions — senatorial and equestrian class records
- OWL-based ontology at `http://romanrepublic.ac.uk/rdf/ontology#`

**DPRR gap (known)**: DPRR links assertions to secondary sources (Broughton, Zmeskal) but not to primary sources (Livy, inscriptions). The primary source grounding layer is what Chrystallum adds on top of DPRR.

**Import state as of 2026-02-25:**

| Metric | Value |
|--------|-------|
| Group A merged (Wikidata QID + P6863 aligned) | 2,960 |
| Group C created (unique to DPRR, not in Wikidata) | 1,916 |
| POSITION_HELD edges imported | 8,365 |
| Familial/social edges imported | 6,928 |
| Status assertions imported | 0 (pending) |
| Group C POSITION_HELD imported | 0 (pending) |

**Remaining DPRR import tasks:**
- Status assertions (1,992 records — senatorial/equestrian class)
- Group C POSITION_HELD (1,442 records — office records for persons without Wikidata QIDs)

**Impact**: Q899409 (Roman families) went from 999 entities / 1.8% scoped to 5,272 entities / 0.0% unscoped. Family network navigation use case is now viable. The 8,365 POSITION_HELD edges constitute the first complete Fasti layer in the graph.

**DPRR alignment query (SPARQL):**
```sparql
SELECT ?item ?dprrId WHERE {
  ?item wdt:P6863 ?dprrId .
}
```
Returns ~3,018 items with confirmed Wikidata ↔ DPRR alignment.

**DPRR relationship vocabulary** (43 types, all mapped to Chrystallum canonical types):
Top types by count: brother of (1,477), son of (1,417), father of (1,408), husband of, wife of, daughter of, mother of, uncle of, cousin of, nephew of, adoptive father of, adoptive son of, half-brother of, step-father of, step-son of, and 28 others — all map to FATHER_OF, MOTHER_OF, SIBLING_OF, SPOUSE_OF, ADOPTED_BY/ADOPTED, COUSIN_OF, NEPHEW_OF etc.

---

### R.2.2 Pleiades (Ancient Places)

**Status**: Operational — Phase 1 scoping, Phase 2 enrichment pending  
**License**: CC-BY  
**Wikidata property**: P1584  
**Endpoint**: `https://pleiades.stoa.org/places/{ID}/json`  
**Bulk download**: `https://atlantides.org/downloads/pleiades/dumps/`

**What Pleiades provides:**
- Canonical ancient place identifier (conceptual place, not just a coordinate)
- Ancient and modern name variants
- Temporal validity periods (which historical periods the place exists in)
- Coordinate ranges (approximate, reflecting ancient uncertainty)
- Connection types (at, near, within for related places)

**Current usage**: P1584 presence on Wikidata entity → `temporal_scoped`, confidence 0.92. Pleiades ID persisted on Entity node for Phase 2 interrogation.

**Phase 2 target**: Pull coordinates, period-specific names, connected places from Pleiades API. Write back to Entity nodes with `source: pleiades` provenance. Temporal validity from Pleiades to constrain event placement.

**Q182547 (Provinces) anchor**: 49 entities in this cluster are Pleiades-scoped (ancient places). 51 are VIAF-scoped (scholarly concepts / administrative entities). P31-only allowlist gates harvesting cleanly for this anchor.

---

### R.2.3 Trismegistos (Texts and People)

**Status**: Phase 1 scoping operational; Phase 2 enrichment pending  
**License**: Requires verification before commercialization  
**Wikidata properties**: P1696 (TM person), P4230 (TM text), P1958 (TM place)  
**Access**: Bulk data at `https://www.trismegistos.org/downloads.php` — no public REST API; CSV exports for TMPeople, TMGeo, TMTexts

**What Trismegistos provides (Phase 2 targets):**
- Attestation records — every appearance of a person in a papyrus or inscription
- Date ranges and geographic distribution of attestations
- Social network data — family connections, career reconstructions, freedmen lists
- Variant name forms
- Document count and provenance per person

**Current usage**: P1696 or P4230 presence → `temporal_scoped`, confidence 0.95.

**Q337547 (Public ritual) anchor**: P140 (religious belief), P101 (field of work), P361 (part of) allowlist used. 2 temporal-scoped, 52 domain-scoped, 46 unscoped (46%). Investigation pending: whether P361 "part of" is source of unscoped entities (candidate for removal from allowlist).

---

### R.2.4 LGPN (Lexicon of Greek Personal Names)

**Status**: Phase 1 scoping operational; Phase 2 enrichment pending; forward SPARQL design pending  
**License**: Requires verification before commercialization  
**Wikidata property**: P1838  
**Access**: Bulk data at `https://www.lgpn.ox.ac.uk/`

**What LGPN provides (Phase 2 targets):**
- Onomastic family — name frequency and geographic distribution
- Variant spellings and forms
- Social status indicators
- Date range of name usage
- Geographic distribution of attestations

**Current usage**: P1838 presence → `temporal_scoped`, confidence 0.93.

**Q899409 gap**: LGPN-attested persons do not point *to* Q899409 (Roman families) via backlinks — the harvester's standard pull-by-category pattern doesn't work for this anchor. Requires forward SPARQL (find persons with P1838 AND Roman gens membership) rather than reverse backlink harvest. Separate tool required; design pending.

**Forward SPARQL pattern (design target):**
```sparql
SELECT ?person ?lgpn ?gens WHERE {
  ?person wdt:P31 wd:Q5 .
  ?person wdt:P1838 ?lgpn .
  ?person wdt:P53 ?gens .          # P53 = family/gens — confirm correct predicate
  ?gens wdt:P31/wdt:P279* wd:Q899409 .
}
```

---

### R.2.5 Wikidata (Discovery and Identity Hub)

**Status**: Core operational  
**Confidence**: 0.90 baseline (Layer 2)  
**API**: `https://www.wikidata.org/w/api.php`

**Role**: Discovery and routing only. Not a canonical source. Wikidata assertions are discovery inputs; domain authorities provide canonical data.

**Key routing properties for Chrystallum domain:**

| Property | Target Authority | Domain |
|----------|-----------------|--------|
| P1584 | Pleiades | Ancient places |
| P6863 | DPRR | Roman Republican persons |
| P1696 | Trismegistos People | Papyrological persons |
| P4230 | Trismegistos Texts | Papyrological documents |
| P1958 | Trismegistos Geo | Ancient places (granular) |
| P1838 | LGPN | Greek personal names |
| P214 | VIAF | Person name authority |
| P9106 | OCD online (4th ed.) | Oxford Classical Dictionary entries |
| P1343 | OCD 1949 (via Q430486) | Oxford Classical Dictionary (bibliographic) |
| P2950 | Nomisma | Numismatic identifiers |
| P1566 | GeoNames | Modern place coordinates (UI-only) |

**Harvest property denylist** (administrative noise, excluded from harvest):
- P6104 (maintained by WikiProject)
- P5008 (on focus list of WikiProject)
- P6216 (copyright status)

**Wikimedia category contamination**: Entities with P31 = Q4167836 (Wikimedia category) must be excluded at harvest. Category: nodes are Wikipedia's administrative filing system, not domain entities. Add Q4167836 to P31 denylist in harvester. Cleanup query pending for existing category nodes.

---

### R.2.6 Subject Authority Federation (LCSH / FAST / LCC)

**Status**: Operational (most mature)  
**Authorities**: LCC / LCSH / FAST / Wikidata  
**Coverage**: Subject classification backbone, agent routing, bibliographic crosswalks

**Usage pattern:**
1. Resolve subject string → LCSH heading or FAST topic
2. Map heading → LCC call number range
3. Route to SFA based on LCC class
4. Cross-reference Wikidata P-codes for international alignment
5. Apply facet tags from shared registry

**Authority precedence (from Appendix P):**
- Tier 1: LCSH/FAST (highest for subjects)
- Tier 2: LCC/CIP (fallback)
- Tier 3: Wikidata + domain authorities (specialists)

---

### R.2.7 Temporal Federation (PeriodO)

**Status**: Operational  
**Authorities**: Year backbone + curated periods + PeriodO alignment  
**Coverage**: Temporal concepts, period-based lensing, date normalization  
**Dataset**: `http://n2t.net/ark:/99152/p0d.json` (~15MB, download and cache locally)

---

## R.3 Confirmed Next Federations (Project Mercury)

### R.3.1 CHRR (Coin Hoards of the Roman Republic)

**Status**: Assessed — awaiting import sprint  
**URL**: `https://numismatics.org/chrr/`  
**License**: ODbL  
**Period**: 155 BC – AD 2 (Republican period exactly)  
**Access**: CSV export with hoard URI / location / dates / coin types / findspot URI via GeoNames; RDF dumps conforming to Nomisma and Pelagios 3

**What CHRR provides:**
- Hoard findspot (GeoNames URI → Pleiades alignment possible)
- Burial date range (correlates with political disruption events)
- Coin type composition (connects to issuing magistrates via CRRO)
- Spatial evidence of political and economic stress

**Chain this enables:**
```
DPRR person → held office → issued coinage → CRRO coin type → found in hoard → CHRR hoard → GeoNames/Pleiades findspot
```

This is the complete material evidence chain from person to physical artifact to archaeological findspot. No other current project assembles it.

**Import approach**: CSV → MATERIAL_EVIDENCE nodes with spatial/temporal properties. GeoNames findspot URIs → align to Pleiades IDs already in graph.

---

### R.3.2 CRRO (Coinage of the Roman Republic Online)

**Status**: Assessed — awaiting import sprint  
**URL**: `https://numismatics.org/crro/`  
**License**: CC-BY  
**Access**: RDF dump with Nomisma URIs

**What CRRO provides:**
- Crawford's *Roman Republican Coinage* digitized
- Every Republican coin type with issuer / date / iconography
- Issuing magistrate identifiers — links to DPRR persons via Nomisma

**Import approach**: RDF dump → align issuing magistrate Nomisma IDs to DPRR person URIs and Wikidata QIDs → import coin types as ARTIFACT nodes → ISSUED_BY edges to DPRR persons.

This is a linked data federation (same architecture as DPRR), not a simple CSV import.

---

### R.3.3 Cities (OxRep / Hanson 2016)

**Status**: Assessed — awaiting import sprint  
**Period**: 100 BC – AD 300  
**Access**: CSV with city names / coordinates / civic status / monuments

**What it provides:**
- Urban characteristics and civic status
- Pleiades alignment likely (ancient city coordinates)
- Enrichment of existing place nodes rather than new entities

**Import approach**: Enrich existing Place nodes with civic status, population estimates, monument types.

---

## R.4 Planned Federations

### R.4.1 Oxford Classical Dictionary (OCD 1949)

**Status**: Planning — OCR extraction protocol designed  
**Source**: Archive.org full text download (7.3MB plain text, ABBYY FineReader 11.0 OCR)  
**Copyright**: In public domain (published 1949, publisher Oxford University Press)  
**Wikidata alignment**: P9106 (OCD online ID, 4th ed.) — use to identify which entities Wikidata already links to OCD, then match to 1949 headwords by label normalization  
**Items with P9106 in Wikidata**: Hundreds to low thousands for Roman Republic domain (seed mapping; remainder requires label matching)

**What OCD provides:**
- Scholarly entry for every significant ancient concept, person, place, and institution
- Cross-reference graph via `(q.v.)` markers — each cross-reference is a directed edge between entries, machine-extractable
- Author attribution at entry level (editor initials at end of each entry → whose scholarly judgment the entry represents)
- Taxonomy enrichment: OCD's entry structure encodes decades of scholarly consensus about conceptual organization
- Salience signal: entries Syme, Nock, Denniston chose to include and cross-reference are significant by field consensus

**OCR quality**: High. Entry delimiter `}` after headword makes segmentation straightforward. Cross-references via `(q.v.)` are machine-readable. Author initials at end of each entry are consistent. Greek characters transliterated cleanly.

**Extraction output per entry:**
```json
{
  "headword": "SULLA",
  "entry_text": "...",
  "cross_references": ["MARIUS", "PROSCRIPTIONS", "SOCIAL WAR"],
  "author_initials": "M.C.",
  "author": "Cary",
  "page_estimate": 862,
  "raw": "..."
}
```

**Four-layer resolution target:**
1. OCD entry text (scholarly judgment, 1949)
2. Wikipedia article (accessible narrative)
3. Wikidata QID (machine-readable identity via P9106)
4. Chrystallum graph node (full epistemological provenance)

When a user reads a Wikipedia article, the browser extension can pull the Wikidata QID from Wikipedia page metadata, resolve to Chrystallum entity, and link back to OCD entry as authoritative source. The circle closes.

**Priority for taxonomy enrichment**: Legal concepts (provocatio, lex, intercessio, imperium), religious institutions (flamines, Vestals, Lupercalia), material culture (toga praetexta, fasces, corona triumphalis). These are gaps in current SubjectConcept hierarchy that OCD's entry structure would fill.

**Epistemic stance**: OCD 1949 is treated as a historically situated reference work, not as an absolute ontology of the ancient world. Its entry selection, cross-reference structure, and authorial judgments encode the consensus and blind spots of mid-20th-century classical scholarship. Chrystallum uses OCD's headwords and `(q.v.)` graph as one taxonomy signal and a source of scholarly salience, but does not privilege its structure over later scholarship, domain authorities (DPRR, Pleiades, Trismegistos, LGPN), or subject federations (LCSH/FAST/UNESCO/AAT). Where OCD's conceptual organization conflicts with other authorities or with primary-source-grounded claims, OCD is treated as one lens on the material, not the final arbiter.

---

### R.4.2 Syme Index (Roman Revolution, 1939)

**Status**: Planning — photography protocol established; extraction pending  
**Source**: Physical book, pages 535–568 (34 pages, two-column alphabetical index)  
**Copyright**: Published 1939, Syme died 1989, UK copyright runs to 2059. Index itself (names, dates, page references as short phrases) is facts extraction, not text reproduction — different copyright character than prose.

**What the Syme index provides:**
- **Disambiguation format**: `Nomen Cognomen, Praenomen (cos. YEAR B.C.)` — already fully disambiguated with consular date as disambiguation key. Maps directly to DPRR PostAssertion format.
- **Salience signal**: Persons Syme indexed with multiple sub-entries are high-salience nodes in the late Republic narrative. Index density → serious reader persona salience weights.
- **Relationship seeds**: Sub-entries are pre-parsed relationship candidates. `in alliance with Antonius, 109` → ALLIED_WITH claim with page citation. `proscribes his brother, 192` → PROSCRIBED action claim.
- **Alignment path**: Syme consular date → DPRR PostAssertion → DPRR person URI → Wikidata QID.

**Extraction output per entry:**
```json
{
  "headword": "Aemilius Lepidus, M.",
  "disambiguator": "cos. 46 B.C.",
  "page_refs": [109, 110, 192, 230],
  "sub_entries": [
    {"topic": "in alliance with Antonius", "pages": [109]},
    {"topic": "his provinces", "pages": [110]},
    {"topic": "proscribes his brother", "pages": [192]}
  ],
  "source": "Syme_Roman_Revolution_1939"
}
```

**Other book indexes in reading list with similar value** (to photograph after Syme):

Tier 1 — photograph first (prosopographic, Republican-period specific, scholarly):
- Astin, *Scipio Aemilianus* (374 pp) — mid-Republican period 185–129 BC, monograph on single figure
- Scullard, *History of the Roman World 753–146 BC* (552 pp) — early and middle Republic, systematic
- Greenidge, *History of Rome During the Later Republic* (534 pp) — 133–44 BC, dense scholarly index
- Oman, *Seven Roman Statesmen* (348 pp) — Gracchi, Sulla, Crassus, Cato, Pompey, Caesar
- Raaflaub, *Social Struggles in Archaic Rome* (444 pp) — Conflict of the Orders, institutional history

Tier 2 — photograph after Tier 1:
- Meier, *Caesar* (513 pp) — German scholarly biography
- Forsythe, *Critical History of Early Rome* (400 pp) — pre-Punic War period
- Sampson, *Rome Blood and Politics* + *Crisis of Rome* — Marius, Jugurtha, Social War generation
- Gargola, *Shape of the Roman Order* (304 pp) — institutional and spatial history

---

### R.4.3 VIAF (Person Name Authority)

**Status**: Defined, partial implementation  
**Wikidata property**: P214  
**Role**: Name authority for persons — canonical name forms in multiple languages, national authority file crosswalk

**Usage**: Supplement DPRR person identity with multilingual name forms. Distinguish person-as-author vs. person-as-subject. Track scholarly reception.

---

### R.4.4 Getty AAT (Concepts and Institutions)

**Status**: Defined, pending implementation  
**Wikidata property**: P1014  
**Role**: Deep concept hierarchies for abstract concepts and institutions  
**Endpoint**: `http://vocab.getty.edu/aat/{concept_id}.json`

---

## R.5 Confidence Architecture

### R.5.1 Scoping Confidence by Source

| Source | Confidence | Rationale |
|--------|------------|-----------|
| Trismegistos | 0.95 | Primary documentary evidence — papyri and inscriptions |
| LGPN | 0.93 | Primary onomastic evidence with geographic and social context |
| Pleiades | 0.92 | Canonical ancient place authority — community-maintained, temporally validated |
| DPRR | 0.85 | Secondary source prosopography — sourced from Broughton and Zmeskal, not primary sources directly |
| VIAF | 0.85 | Person name authority — confirms scholarly identity, not historical existence |
| Wikidata | 0.90 | Discovery hub — broad but not deep |

### R.5.2 Confidence Boost Rules

- Adding Trismegistos/LGPN epigraphic or papyrological evidence: +0.15 to +0.20
- Cross-validation by 2+ authorities: +0.10
- Temporal/geographic constraint satisfaction: +0.10
- Primary source linkage via Phase 2 enrichment: +0.15

### R.5.3 Federation Edge Types

```
// SAME_AS: High-confidence identity match (0.90+)
(candidate)-[:SAME_AS {confidence: 0.95, method: "P1584_resolution"}]->(pleiades)

// ALIGNED_WITH: Probable match requiring validation (0.70–0.89)
(candidate)-[:ALIGNED_WITH {confidence: 0.80, review_required: true}]->(wikidata)

// DERIVED_FROM: Extracted/inferred from authority
(claim)-[:DERIVED_FROM {confidence: 0.85}]->(source_record)

// CONFLICTS_WITH: Explicit disagreement requiring adjudication
(source_a)-[:CONFLICTS_WITH {conflict_type: "date", resolution: null}]->(source_b)
```

---

## R.6 SFA Constitution and Federation

Federation data is not only infrastructure for the graph — it is Layer 3 SFA constitution material. Each SFA's methodological stance determines which federation sources it privileges and how it reasons about their evidence.

### R.6.1 The Three-Layer SFA Model

Every SFA has three layers of constitutive knowledge:

**Layer 1 — Domain data**: What the graph contains. DPRR persons, Pleiades places, Wikidata entities, POSITION_HELD and familial edges.

**Layer 2 — Primary sources**: What the ancient authors say. Livy, Polybius, Appian, Cicero. Retrieved via Perseus citation resolution.

**Layer 3 — Methodological stance**: How to reason about Layers 1 and 2. This is the SFA constitution document layer — not a shared Methods Agent output, but SFA-specific texts that define the epistemological posture each agent brings to the data.

### R.6.2 Federation Affinity by SFA

Different SFAs privilege different federations as their primary evidence sources:

| SFA | Primary federation sources | Characteristic questions |
|-----|---------------------------|-----------------------------|
| Prosopographer | DPRR, LGPN, Trismegistos | Who held this office? Who were their kin? What attestations exist? |
| Economic historian | CRRO, CHRR, OxRep | What did this person's coinage signal? Where were hoards buried? |
| Military historian | DPRR (PostAssertions), Pleiades | What commands did this person hold? At which locations? |
| Legal/institutional | DPRR (StatusAssertions), OCD | What was this person's legal status? What office carried what powers? |
| Literary/source critic | OCD, Syme index | Which sources mention this? What does their cross-reference structure reveal? |

### R.6.3 F001–F005 Nodes and Federation

The epistemological framework nodes F001–F005 in the schema are the graph representation of each SFA's methodological stance (Layer 3). They are not outputs of a Methods Agent. Each node encodes the SFA's characteristic questions, favored source types, and known limitations — the same information that the SFA constitution documents capture in prose.

When an SFA generates a claim, it tags it with the lens it used. The F-node is the interpretable artifact: "this claim was generated from a prosopographic lens, which privileges DPRR and LGPN attestations and recognizes elite bias as a known limitation."

---

## R.7 API Reference Summary

| Federation | Status | Wikidata Prop | Access | Confidence |
|------------|--------|--------------|--------|------------|
| **DPRR** | Operational | P6863 | SPARQL endpoint | 0.85 |
| **Pleiades** | Phase 1 operational | P1584 | REST JSON + bulk dump | 0.92 |
| **Trismegistos** | Phase 1 operational | P1696, P4230 | Bulk CSV download | 0.95 |
| **LGPN** | Phase 1 operational | P1838 | Bulk download | 0.93 |
| **Wikidata** | Core operational | QID | REST API | 0.90 |
| **LCSH/FAST** | Operational (most mature) | P2163 | REST / SPARQL | Tier 1 |
| **PeriodO** | Operational | label match | Single JSON dataset | +0.10 |
| **CHRR** | Planned (Project Mercury) | — | CSV + RDF | ODbL |
| **CRRO** | Planned (Project Mercury) | P2950 | RDF dump | CC-BY |
| **OCD 1949** | Planned | P1343 / P9106 | Archive.org plain text | Public domain |
| **Syme index** | Planned | — | Physical photography | Facts extraction |
| **VIAF** | Defined | P214 | REST JSON | 0.85 |
| **Getty AAT** | Defined | P1014 | REST JSON | 0.90 |
| **GeoNames** | UI-only | P1566 | REST (free registration) | UI layer |

---

## R.8 Baseline State (2026-02-25)

For the authoritative post-DPRR graph state, see [docs/BASELINE_POST_DPRR_2026-02-25.md](../../docs/BASELINE_POST_DPRR_2026-02-25.md).

Summary:
- 63,689 nodes, 53,148 edges
- Global unscoped: 8.9% (from 86.4%)
- Q899409: 5,272 entities, 0.0% unscoped (from 1.8%)
- 1,916 persons unique to Chrystallum (not in Wikidata) — Group C DPRR persons

---

## R.9 Known Issues and Pending Work

| Issue | Status | Notes |
|-------|--------|-------|
| Wikimedia category contamination | Pending | Add Q4167836 to P31 denylist; cleanup query for existing nodes |
| Q337547 unscoped breakdown | Pending | P361 "part of" may be noise source; needs investigation |
| Q182547 budget cap | Pending | Verify no Pleiades entities dropped in 64 budget-capped rejections |
| LGPN forward SPARQL | Pending | Inverted query direction; separate tool needed |
| Status assertions import | Pending | 1,992 DPRR records |
| Group C POSITION_HELD | Pending | 1,442 records for 1,916 Group C persons |
| Phase 2 enrichment clients | Pending | Trismegistos, LGPN, Pleiades API interrogation |
| WIKIDATA_P1343 normalization | Pending | 404 edges still carrying raw prefix form |
| Category entity cleanup | Pending | Full scope larger than P971 edges alone |

---

## R.10 Related Appendices

- **Appendix K**: Wikidata Integration Patterns — detailed QID mapping, SPARQL federation
- **Appendix L**: CIDOC-CRM Integration — relationship vocabulary, class mappings
- **Appendix O**: Facet Training Resources Registry — SFA constitution documents
- **Appendix P**: Semantic Enrichment and Ontology Alignment — authority precedence (LCSH > LCC > Wikidata)
- **Appendix Q**: Operational Modes and Agent Orchestration — SFA routing depends on LCC/facet/period federation
- **Appendix T**: SFA Workflow — Phase 3.5 enrichment integration points

---

**(End of Appendix R v4.0)**
