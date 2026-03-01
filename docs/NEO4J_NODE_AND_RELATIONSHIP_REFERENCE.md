# Neo4j Node Types, Attributes, and Relationships Reference

**Purpose:** Single reference for all node types, properties, and relationships in the Chrystallum Neo4j graph.  
**Source:** Loaders, schema files, and Cypher operations.  
**Last updated:** 2026-02-27

---

## Quick Map

**Schema root:** Chrystallum (`id: 'CHRYSTALLUM_ROOT'`) — branches to facets, federations, subjects, biblio. See `docs/CHRYSTALLUM_SUBGRAPH_SPEC.md`.

**Core discovery node labels:** SubjectConcept, CanonicalFacet, LCC_Class, LCSH_Heading, Work, Human, Place, Event, Period

**Core relationships:** MAPS_TO_FACET, CLASSIFIED_BY_LCC, HAS_LCSH_AUTHORITY, CLASSIFIED_BY, ABOUT, ASSIGNED_IN

---

## 1. Federation Survey Nodes (from Phase 0 loaders)

These nodes are created by federation survey loaders from `output/nodes/*.json`.

### LCSH_Heading

| Property       | Type    | Required | Description                                      |
|----------------|---------|----------|--------------------------------------------------|
| `lcsh_id`      | string  | ✓        | LCSH authority ID (e.g. `sh85115114`)            |
| `label`        | string  | ✓        | Subject heading text                             |
| `uri`          | string  |          | `https://id.loc.gov/authorities/subjects/{id}`   |
| `domain`       | string  |          | Survey domain (e.g. `roman_republic`)             |
| `concept_ref`  | string  |          | LCSH URI for alignment                           |
| `semantic_facet` | string |        | Canonical facet key (e.g. `POLITICAL`)           |
| `temporal_start` | int   |          | Start year (BCE negative)                        |
| `temporal_end` | int    |          | End year (BCE negative)                          |
| `survey_depth` | int     |          | Breadth-first depth from seed                     |
| `is_seed`      | boolean |          | True if seed node                                 |

**Relationships:**
- `(l:LCSH_Heading)-[:MAPS_TO_FACET {weight: 1.0}]->(f:CanonicalFacet)` when `semantic_facet` present

**Loader:** `scripts/backbone/subject/load_lcsh_survey.py`

---

### Pleiades_Place

| Property        | Type    | Required | Description                                      |
|-----------------|---------|----------|--------------------------------------------------|
| `pleiades_id`   | string  | ✓        | Pleiades place ID (e.g. `423025`)                |
| `label`         | string  | ✓        | Place name                                       |
| `uri`           | string  |          | Pleiades URI                                     |
| `domain`        | string  |          | Survey domain                                    |
| `concept_ref`   | string  |          | LCSH URI for alignment                           |
| `spatial_anchor`| string  |          | Pleiades URI or coordinates                       |
| `semantic_facet`| string  |          | Canonical facet key                              |
| `temporal_start`| int     |          | Start year                                       |
| `temporal_end`  | int     |          | End year                                         |
| `survey_depth`  | int     |          | Breadth-first depth                               |
| `is_seed`       | boolean |          | True if seed node                                 |

**Relationships:**
- `(p:Pleiades_Place)-[:MAPS_TO_FACET {weight: 1.0}]->(f:CanonicalFacet)` when `semantic_facet` present
- `(p:Pleiades_Place)-[:ALIGNED_WITH_GEO_BACKBONE]->(place:Place)` when Place exists with same `pleiades_id` (post-load: `link_pleiades_place_to_geo_backbone.py`)

**Loader:** `scripts/backbone/subject/load_federation_survey.py --survey output/nodes/pleiades_roman_republic.json`

---

### Periodo_Period

| Property        | Type    | Required | Description                                      |
|-----------------|---------|----------|--------------------------------------------------|
| `periodo_id`    | string  | ✓        | PeriodO ID (e.g. `p0rl7n`)                       |
| `label`         | string  | ✓        | Period label                                     |
| `uri`           | string  |          | PeriodO ark URI                                  |
| `domain`        | string  |          | Survey domain                                    |
| `concept_ref`   | string  |          | LCSH URI                                         |
| `spatial_anchor`| string  |          | Pleiades URI or coordinates                       |
| `semantic_facet`| string  |          | Canonical facet key                              |
| `temporal_start`| int     |          | Start year                                       |
| `temporal_end`  | int     |          | End year                                         |
| `survey_depth`  | int     |          | Breadth-first depth                               |
| `is_seed`       | boolean |          | True if seed node                                 |

**Relationships:**
- `(p:Periodo_Period)-[:MAPS_TO_FACET {weight: 1.0}]->(f:CanonicalFacet)` when `semantic_facet` present

**Loader:** `scripts/backbone/subject/load_federation_survey.py --survey output/nodes/periodo_roman_republic.json`

---

### DPRR_Office

| Property        | Type    | Required | Description                                      |
|-----------------|---------|----------|--------------------------------------------------|
| `dprr_id`       | string  | ✓        | DPRR office ID (e.g. `off-0001`)                 |
| `label`         | string  | ✓        | Office name (e.g. Consul)                        |
| `uri`           | string  |          | DPRR URI                                         |
| `domain`        | string  |          | Survey domain                                    |
| `concept_ref`   | string  |          | LCSH URI                                         |
| `spatial_anchor`| string  |          | Pleiades URI                                     |
| `semantic_facet`| string  |          | Canonical facet key                              |
| `temporal_start`| int     |          | Start year                                       |
| `temporal_end`  | int     |          | End year                                         |
| `survey_depth`  | int     |          | Breadth-first depth                               |
| `is_seed`       | boolean |          | True if seed node                                 |

**Relationships:**
- `(d:DPRR_Office)-[:MAPS_TO_FACET {weight: 1.0}]->(f:CanonicalFacet)` when `semantic_facet` present

**Loader:** `scripts/backbone/subject/load_federation_survey.py --survey output/nodes/dprr_roman_republic.json`

---

### WorldCat_Work

| Property        | Type    | Required | Description                                      |
|-----------------|---------|----------|--------------------------------------------------|
| `worldcat_id`   | string  | ✓        | WorldCat work ID                                 |
| `label`         | string  | ✓        | Work title                                       |
| `uri`           | string  |          | WorldCat URI                                     |
| `domain`        | string  |          | Survey domain                                    |
| `concept_ref`   | string  |          | LCSH URI                                         |
| `spatial_anchor`| string  |          | Pleiades URI                                     |
| `semantic_facet`| string  |          | Canonical facet key                              |
| `temporal_start`| int     |          | Start year                                       |
| `temporal_end`  | int     |          | End year                                         |
| `survey_depth`  | int     |          | Breadth-first depth                               |
| `is_seed`       | boolean |          | True if seed node                                 |

**Relationships:**
- `(w:WorldCat_Work)-[:MAPS_TO_FACET {weight: 1.0}]->(f:CanonicalFacet)` when `semantic_facet` present

**Loader:** `scripts/backbone/subject/load_federation_survey.py --survey output/nodes/worldcat_roman_republic.json`

**Note:** `WorldCat_Work` is a federation survey node. For enriched bibliographic works with ISBN, OA fields, and curriculum links, see **Work** (section 3a).

---

### LCC_Class

| Property | Type   | Required | Description                                      |
|----------|--------|----------|--------------------------------------------------|
| `code`   | string | ✓        | LCC class code (e.g. `DG241-269`)                |
| `label`  | string | ✓        | Class label                                     |
| `prefix` | string |          | Prefix (e.g. `DG`)                               |
| `start`  | float  |          | Range start (for hierarchy inference)           |
| `end`    | float  |          | Range end                                       |
| `uri`    | string |          | `https://id.loc.gov/authorities/classification/{code}` |

**Relationships:**
- `(broader:LCC_Class)-[:BROADER_THAN]->(narrower:LCC_Class)` — hierarchy (parent → child)
- `(l:LCC_Class)-[:MAPS_TO_FACET {weight}]->(f:CanonicalFacet)` — facet mapping (weight 0.0–1.0)

**Loader:** `scripts/backbone/subject/load_lcc_nodes.py`

---

### Discipline (legacy)

| Property   | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| `lcsh_id`  | string | ✓        | LCSH ID (e.g. `sh85115114`) or pipe-separated    |

**Relationships:** `(parent:Discipline)-[:BROADER_THAN]->(child:Discipline)`

**Note:** Used in `output/lcsh_broader_than_edges.cypher`; legacy discipline-major mapping. For the new cleaned registry, see **Discipline (registry)** in section 3a.

---

## 2. Canonical Facet Nodes

### CanonicalFacet (Facet)

18 canonical analytical dimensions (ADR-004). Labels: `ArchaeologicalFacet`, `ArtisticFacet`, etc. All share `:Facet:CanonicalFacet`.

| Property      | Type   | Required | Description                                      |
|---------------|--------|----------|--------------------------------------------------|
| `unique_id`   | string | ✓        | e.g. `FACET_ARCHAEOLOGICAL`                      |
| `key`         | string | ✓        | Uppercase key (e.g. `ARCHAEOLOGICAL`)           |
| `label`       | string | ✓        | Human-readable label                             |
| `description` | string |          | Facet description                                |

**18 keys:** ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL

**Cypher:** Use `CanonicalFacet.key` consistently (e.g. `MATCH (f:CanonicalFacet {key: 'POLITICAL'})`).

**Relationships:**
- `(federation_node)-[:MAPS_TO_FACET {weight}]->(f:CanonicalFacet)` — from LCSH_Heading, Pleiades_Place, Periodo_Period, DPRR_Office, WorldCat_Work, LCC_Class
- `(cat:Facets:Category)-[:IS_COMPOSED_OF]->(f:CanonicalFacet)`
- `(c:Chrystallum)-[:HAS_FACET_CLUSTER]->(cat:Facets:Category)`

**Bootstrap:** `scripts/federation/create_facets_cluster.cypher`

---

### FacetCategory (legacy)

| Property     | Type   | Required | Description                                      |
|--------------|--------|----------|--------------------------------------------------|
| `key`        | string | ✓        | Lowercase facet key (unique)                     |
| `label`      | string |          | Label                                            |
| `entity_type`| string |          | `FacetCategory`                                 |

**Bootstrap:** `Neo4j/schema/03_schema_initialization_simple.cypher`

---

## 3. Core Entity Nodes

### Human

| Property            | Type   | Required | Description                                      |
|---------------------|--------|----------|--------------------------------------------------|
| `qid`               | string | ✓*       | Wikidata QID or `local_entity_{hash}`            |
| `name` / `label`    | string | ✓        | Primary name                                     |
| `entity_id`         | string |          | Internal ID (e.g. `human_caesar`)                 |
| `birth_year`        | int    |          | ISO 8601 (negative = BCE)                         |
| `death_year`        | int    |          | ISO 8601                                         |
| `labels_multilingual`| object|          | `{@en, @la, @fr, ...}`                          |
| `authority_ids`     | object |          | LCSH, FAST, VIAF                                 |
| `entity_type`       | string |          | `Human`                                          |

**Relationships:** PARTICIPATED_IN, HELD_OFFICE, PARENT_OF, SPOUSE_OF, MEMBER_OF_GENS, CLASSIFIED_BY, etc.

---

### Place

| Property       | Type   | Required | Description                                      |
|----------------|--------|----------|--------------------------------------------------|
| `qid`          | string | ✓*       | Wikidata QID                                    |
| `label`        | string | ✓        | Place name                                       |
| `entity_id`    | string |          | Internal ID (e.g. `place_rome`)                   |
| `place_type`   | string |          | e.g. `place`                                     |
| `modern_country`| string|          | Modern country name                              |
| `coordinates`  | object |          | Lat/lon                                          |
| `entity_type`  | string |          | `Place`                                          |

**Relationships:** OCCURRED_AT, LOCATED_IN, ALIGNED_WITH_PLEIADES, etc.

---

### Period

| Property         | Type   | Required | Description                                      |
|------------------|--------|----------|--------------------------------------------------|
| `qid`            | string |          | Wikidata QID (e.g. `Q17167`)                     |
| `label`          | string | ✓        | Period name                                      |
| `entity_id`      | string |          | Internal ID                                      |
| `start` / `start_year` | int |       | Start year (BCE negative)                         |
| `end` / `end_year` | int   |          | End year                                         |
| `start_date_min` | string |         | ISO date                                         |
| `end_date_max`   | string |          | ISO date                                         |
| `facet`          | string |          | Primary facet (e.g. `Political`)                  |
| `entity_type`    | string |          | `Period`                                         |

**Relationships:** STARTS_IN_YEAR, ENDS_IN_YEAR, OCCURRED_DURING, PART_OF, HAS_SUBJECT_CONCEPT

---

### Event

| Property         | Type   | Required | Description                                      |
|------------------|--------|----------|--------------------------------------------------|
| `qid`            | string |          | Wikidata QID                                    |
| `label`          | string | ✓        | Event name                                       |
| `entity_id`      | string |          | Internal ID                                      |
| `event_type`     | string |          | e.g. `battle`                                    |
| `start_date`     | string |          | ISO date                                         |
| `end_date`       | string |          | ISO date                                         |
| `date_precision` | string |          | e.g. `day`                                      |
| `entity_type`    | string |          | `Event`                                          |

**Relationships:** OCCURRED_DURING, OCCURRED_AT, STARTS_IN_YEAR, ENDS_IN_YEAR, HAS_SUBJECT_CONCEPT

---

### Year

| Property     | Type   | Required | Description                                      |
|--------------|--------|----------|--------------------------------------------------|
| `year`       | int    | ✓        | ISO 8601 year (negative = BCE)                   |
| `entity_id`  | string |          | e.g. `year_509_bce`                             |
| `label`      | string |          | e.g. `509 BCE`                                   |
| `entity_type`| string |          | `Year`                                           |

**Relationships:** PART_OF (→ Decade → Century → Millennium), STARTS_IN_YEAR, ENDS_IN_YEAR

---

## 3a. Work and Curriculum Nodes

### Work

Bibliographic work node representing a distinct intellectual work (book, article, chapter), enriched from MARC, authority data, curricular data, and open-access services.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `work_id` | string | ✓ | Internal ID (e.g. `work_9780198149185`) |
| `title` | string | ✓ | Work title |
| `subtitle` | string | | Subtitle |
| `authors` | list | | List of author names (strings) |
| `isbn` | string | | Primary ISBN (normalized, no dashes) |
| `isbn_list` | list | | All known ISBNs |
| `doi` | string | | DOI if present |
| `publisher` | string | | Publisher name |
| `publication_year` | int | | Year of publication |
| `edition` | string | | Edition statement |
| `language` | string | | ISO language code (e.g. en, la) |
| `lccn` | string | | Library of Congress Control Number |
| `oclc_number` | string | | OCLC number |
| `entity_type` | string | | `Work` |
| `is_open_access` | boolean | | True if at least one legitimate full-text OA copy is known |
| `open_access_status` | string | | e.g. gold, green, bronze, free-to-read, closed, unknown |
| `open_access_urls` | list | | List of canonical full-text URLs |
| `open_access_source` | list | | Sources asserting OA (["OpenAlex","DOAB","OpenLibrary"]) |
| `created_from` | string | | Source of initial record (e.g. worldcat, open_syllabus, local) |
| `last_enriched_at` | string | | ISO datetime of last OA / authority enrichment |

**Relationships:**
- `(w:Work)-[:CLASSIFIED_AS]->(lcc:LCC_Class)` — LCC classification (from MARC 050/090/082)
- `(w:Work)-[:HAS_LCSH_SUBJECT]->(lcsh:LCSH_Heading)` — LCSH subject headings (from MARC 6XX)
- `(w:Work)-[:HAS_FAST_SUBJECT]->(fast:FAST_Subject)` — FAST subjects derived from LCSH
- `(w:Work)-[:ABOUT {facets, source, confidence}]->(sc:SubjectConcept)` — Work is about a SubjectConcept; facets may store a facet-weight map, source records SCA/SFA, confidence 0.0–1.0
- `(w:Work)-[:ASSIGNED_IN {count, first_year, last_year}]->(d:Discipline)` — Work appears in syllabi for a Discipline
- `(w:Work)-[:HAS_AUTHOR]->(h:Human)` — Work authored by a Human (when authority reconciliation available)
- `(w:Work)-[:HAS_PUBLISHER]->(org:Organization)` — Publisher (optional)

**Loaders / Enrichers:**
- `scripts/backbone/work/load_worldcat_works.py`, `scripts/backbone/work/load_open_syllabus_works.py`
- `scripts/enrichment/enrich_work_openaccess.py` — OpenAlex/DOAB/OpenLibrary OA enrichment
- `scripts/enrichment/enrich_work_marc_authorities.py` — LCC/LCSH/FAST from MARC

---

### Discipline (registry)

Domain-level disciplinary node, derived from the cleaned discipline/major registry (excluding institutions, degrees, and occupations).

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `discipline_id` | string | ✓ | Internal ID (e.g. `disc_ancient_history`) |
| `qid` | string | | Wikidata QID for the discipline/field |
| `label` | string | ✓ | Discipline label (e.g. Ancient history, Roman law) |
| `source` | string | | Origin of registry entry (wikidata_discipline_table, manual) |
| `lcsh_id` | string | | LCSH heading ID if aligned |
| `fast_id` | string | | FAST ID if aligned |
| `ddc` | string | | Dewey numbers (pipe-separated) if applicable |
| `lcc_class` | string | | Representative LCC class/range for this discipline |
| `aat_id` | string | | Getty AAT ID if applicable |
| `status` | string | | e.g. active, deprecated, candidate |
| `entity_type` | string | | `Discipline` |

**Relationships:**
- `(parent:Discipline)-[:BROADER_THAN]->(child:Discipline)` — Optional discipline hierarchy
- `(d:Discipline)-[:COVERS_DOMAIN]->(sd:SubjectDomain)` — Discipline covers a SubjectDomain
- `(w:Work)-[:ASSIGNED_IN {count, first_year, last_year}]->(d:Discipline)` — Work assigned in this discipline
- `(d:Discipline)-[:ALIGNED_WITH_LCSH]->(lcsh:LCSH_Heading)` — Discipline mapped to LCSH heading
- `(d:Discipline)-[:ALIGNED_WITH_FAST]->(fast:FAST_Subject)` — Discipline mapped to FAST subject

**Loader:** `scripts/backbone/discipline/load_disciplines_registry.py`  
Input: `cleaned discipline_majors_consolidated_disciplines_filtered.csv`

---

### SubjectDomain

High-level subject region (e.g. Roman Republic, Roman law) that links disciplines, SubjectConcepts, and temporal/geographic scopes.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `domain_id` | string | ✓ | Internal ID (e.g. `domain_roman_republic`) |
| `label` | string | ✓ | Domain label (e.g. Roman Republic) |
| `description` | string | | Narrative description |
| `temporal_scope` | string | | e.g. -0509/-0027 (ISO-like interval) |
| `geographic_scope` | string | | Free-text or coded geographic scope |
| `primary_lcc` | string | | Primary LCC range(s) (e.g. DG241-269, KJA190-2152) |
| `status` | string | | e.g. active, experimental |
| `entity_type` | string | | `SubjectDomain` |

**Relationships:**
- `(sd:SubjectDomain)-[:HAS_SUBJECT_CONCEPT]->(sc:SubjectConcept)` — SubjectConcepts that constitute this domain
- `(d:Discipline)-[:COVERS_DOMAIN]->(sd:SubjectDomain)` — Disciplines that commonly encompass this domain
- `(sd:SubjectDomain)-[:ALIGNED_WITH_LCC]->(lcc:LCC_Class)` — Domain anchored to major LCC ranges
- `(sd:SubjectDomain)-[:OCCURS_DURING]->(p:Period)` — Domain linked to temporal backbone

**Loader:** `scripts/backbone/domain/bootstrap_subject_domains.py` — Creates SubjectDomain nodes from configuration (JSON/YAML)

---

## 4. Subject Concept & Authority Nodes

### SubjectConcept

**Canonical ID:** Use `subject_id` (e.g. `subj_roman_republic_q17167`) as the unique key for agents and Cypher. Some schema constraints use `concept_id`; treat them as equivalent when both exist.

| Property            | Type   | Required | Description                                      |
|---------------------|--------|----------|--------------------------------------------------|
| `subject_id`        | string | ✓        | Unique ID (e.g. `subj_roman_republic_q17167`) — canonical for agents |
| `concept_id`        | string | ✓*       | Alternative unique ID (schema constraint; same as subject_id when both used) |
| `label`             | string | ✓        | Concept label                                    |
| `primary_facet`     | string | ✓        | Primary facet key                                |
| `related_facets`    | list   |          | Additional facets                                 |
| `qid`               | string |          | Wikidata QID                                     |
| `lcsh_id`           | string |          | LCSH authority ID                                |
| `fast_id`           | string |          | FAST authority ID                                |
| `lcc_class`         | string |          | LCC class code                                   |
| `status`            | string |          | e.g. `approved`, `pending_approval`               |
| `description`       | string |          | Description                                       |
| `temporal_scope`    | string |          | e.g. `-0509/-0027`                               |
| `geographic_scope`  | string |          | Geographic scope                                 |

**Relationships:**
- `(sc)-[:HAS_LCSH_AUTHORITY]->(lcsh:LCSH_Subject)`
- `(sc)-[:HAS_FAST_AUTHORITY]->(fast:FAST_Subject)`
- `(sc)-[:CLASSIFIED_BY_LCC]->(lcc:LCC_Class)`
- `(child)-[:PART_OF]->(parent:SubjectConcept)`
- `(narrower)-[:BROADER_CONCEPT]->(broader:SubjectConcept)`
- `(registry)-[:CONTAINS]->(sc)`
- `(agent)-[:ANALYZES]->(sc)`
- `(entity)-[:CLASSIFIED_BY]->(sc)`
- `(sc)-[:POSITIONED_AS {federation, property, hops, rel_type, anchor_type, confidence}]->(anchor:ClassificationAnchor | Entity)` — federation positioning (SCA)

---

### ClassificationAnchor (federation positioning)

| Property      | Type   | Required | Description                                      |
|---------------|--------|----------|--------------------------------------------------|
| `qid`         | string | ✓        | Wikidata QID                                     |
| `label`       | string |          | Label                                            |
| `anchor_type` | string |          | e.g. `ClassificationAnchor`                     |
| `dewey`       | string |          | Dewey notation (if applicable)                   |
| `lcc`         | string |          | LCC code (if applicable)                        |
| `lcsh_id`     | string |          | LCSH ID (if applicable)                         |
| `federation`  | string |          | Source federation                                |

**Relationships:**
- `(sc:SubjectConcept)-[:POSITIONED_AS]->(a:ClassificationAnchor)` — discovery/federation positioning
- `(fed:SYS_FederationSource)-[:PROVIDES_ANCHOR]->(a:ClassificationAnchor)` — federation provenance

**Note:** When target QID exists as Entity, POSITIONED_AS may point to Entity directly; ClassificationAnchor is used when target is not yet an Entity.

---

### LCSH_Subject (authority, distinct from LCSH_Heading)

| Property   | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| `lcsh_id`  | string | ✓        | LCSH authority ID (unique)                       |
| `heading`  | string |          | Full heading text                                |

**Relationships:** `(sc:SubjectConcept)-[:HAS_LCSH_AUTHORITY]->(lcsh:LCSH_Subject)`

---

### FAST_Subject

| Property          | Type   | Required | Description                                      |
|-------------------|--------|----------|--------------------------------------------------|
| `fast_id`         | string | ✓        | FAST authority ID (unique)                      |
| `preferred_label` | string |          | Preferred label                                  |

**Relationships:** `(sc:SubjectConcept)-[:HAS_FAST_AUTHORITY]->(fast:FAST_Subject)`

---

## 5. Claim & Reasoning Nodes

### Claim

Generic node capturing an interpretive or empirical assertion made by an agent about a relationship or classification. Claims can be attached to edges or represent higher-level statements.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `claim_id` | string | ✓ | Unique ID (e.g. `claim_sc_subjromanarmy_sfa_polybian_001`) |
| `cipher` | string | ✓* | Content-addressable hash (unique) — for promoted-claim flow |
| `claim_type` | string | ✓ | e.g. ABOUT, POSITIONING, RELATIONSHIP, FACET_ASSIGNMENT, temporal, geographic |
| `subject_id` | string | | ID of subject node (SubjectConcept, Work, Entity) involved |
| `object_id` | string | | ID of object node involved |
| `relation_key` | string | | Relationship type proposed (e.g. BROADER_CONCEPT, VETO_MECHANISM) |
| `label` | string | | Human-readable claim |
| `text` | string | | Full claim text |
| `facets` | object | | Optional facet-weight map for this claim |
| `facet` / `primary_facet` | string | | Primary facet |
| `source_agent_id` | string | | agent_id of Agent that produced the claim |
| `framework_key` | string | | Framework identifier (for SFA claims; optional for SCA) |
| `evidence_type` | string | | authority, harvested_graph, full_text, abstract, metadata |
| `evidence_ref` | string | | Reference to logs, prompt, or external source |
| `confidence` | float | | 0.0–1.0 |
| `posterior_probability` | float | | Bayesian posterior |
| `status` | string | | pending, approved, rejected, superseded |
| `authority_source` | string | | Source system (for promoted-claim flow) |
| `created_at` | string | | ISO datetime |
| `updated_at` | string | | ISO datetime |
| `entity_type` | string | | `Claim` |

**Relationships:**
- `(agent:Agent)-[:PRODUCED]->(c:Claim)` — Agent produced this claim
- `(c:Claim)-[:ABOUT_SUBJECT]->(s:SubjectConcept | Work | Entity)` — Claim refers to subject node
- `(c:Claim)-[:ABOUT_OBJECT]->(o:SubjectConcept | Work | Entity)` — Claim refers to object node
- `(c:Claim)-[:EVIDENCE_IN]->(w:Work)` — Claim grounded in a particular Work
- SUPPORTED_BY, EDGE (promoted relationships), HAS_FACET_ASSESSMENT

**Note on edge-level claims:** You can store `source`, `confidence`, `framework_key` directly on relationships created by agents (e.g. :ABOUT, :BROADER_CONCEPT, :POSITIONED_AS). Use Claim nodes for higher-level tracking (who proposed what, when, with what evidence) and for conflicting proposals.

**Loader:** `scripts/agents/sca_sfa_claim_writer.py` — Reads agent outputs (JSON) and creates Claim nodes

---

### FacetAssessment

| Property        | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| `assessment_id` | string | ✓        | Unique (claim, facet, run)                       |
| `facet`         | string |          | Facet key                                        |

---

## 6. Agent & Registry Nodes

### Agent

Abstract agent node for automated actors operating on the graph (Subject Concept Agents, Subject Framework Agents, and specialized facet agents).

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agent_id` / `id` | string | ✓ | Unique ID (e.g. SCA_holistic_v1, SFA_polybian_v1, SFA_subj_..._MILITARY) |
| `label` | string | | Human-readable label |
| `agent_type` | string | ✓ | SCA, SFA, FacetAgent, SubjectFacetAgent, WorkflowAgent, etc. |
| `facet_key` / `facet` | string | | For facet agents, canonical facet key (e.g. MILITARY) |
| `framework_key` | string | | For SFAs, framework identifier (e.g. polybian, clash_civ) |
| `subject_concept_id` | string | | Linked SubjectConcept |
| `version` | string | | Agent version (e.g. 1.0.0) |
| `provider` | string | | LLM provider or engine (perplexity, openai, rule_based) |
| `model` | string | | LLM model |
| `config_ref` | string | | Path or ID for config/prompt used |
| `status` | string | | active, deprecated, experimental |
| `capabilities` | list | | e.g. ['analysis','discovery','classification'] |
| `created_at` | string | | ISO datetime |
| `updated_at` | string | | ISO datetime |
| `entity_type` | string | | `Agent` |

**Relationships:**
- `(agent:Agent)-[:ANALYZES]->(sc:SubjectConcept)` — Agent analyzes a SubjectConcept (SCA or FacetAgent)
- `(agent:Agent)-[:ANALYZES]->(w:Work)` — Agent analyzes a Work (e.g. for Work→SubjectConcept links)
- `(agent:Agent)-[:PRODUCED]->(c:Claim)` — Agent produced a Claim node
- `(registry:AgentRegistry)-[:HAS_AGENT]->(agent)` or `[:REGISTERS]->(agent)` — Agent registered

**Bootstrap:** `scripts/agents/bootstrap_agents.cypher` — Creates core SCA and SFA agent nodes from configuration

---

### SubjectConceptRegistry

| Property          | Type   | Required | Description                                      |
|-------------------|--------|----------|--------------------------------------------------|
| `registry_id`     | string | ✓        | Unique registry ID                              |
| `parent_concept_id` | string |        | Parent concept                                   |
| `last_updated`    | datetime |       | Last update                                      |

**Relationships:** `(registry)-[:CONTAINS]->(sc:SubjectConcept)`

---

## 7. Temporal Hierarchy Nodes

### Decade, Century, Millennium

| Property     | Type | Required | Description                                      |
|--------------|------|----------|--------------------------------------------------|
| `start_year` | int  | ✓        | Start year of the span                           |

**Relationships:**
- `(y:Year)-[:PART_OF]->(d:Decade)-[:PART_OF]->(c:Century)-[:PART_OF]->(m:Millennium)`
- `(a)-[:FOLLOWED_BY]->(b)` (sequential ordering)

---

## 8. Meta & Policy Nodes

### Chrystallum (Schema Subgraph Root)

**Canonical key:** `{id: 'CHRYSTALLUM_ROOT'}` — use this for all MERGE/MATCH to avoid multiple roots.

| Property      | Type   | Description                                      |
|---------------|--------|--------------------------------------------------|
| `id`          | string | `'CHRYSTALLUM_ROOT'` (required, unique)          |
| `label`       | string | `'Chrystallum'`                                  |
| `name`        | string | `'Chrystallum Knowledge Graph'`                  |
| `type`        | string | `'knowledge_graph_root'`                         |

**Subgraph branches (see `docs/CHRYSTALLUM_SUBGRAPH_SPEC.md`):**

| Relationship            | Target                         | Description                                      |
|-------------------------|--------------------------------|--------------------------------------------------|
| HAS_FACET_CLUSTER       | Facets:Category                | → CanonicalFacet (18 facets)                     |
| HAS_FEDERATION_CLUSTER  | Federation:Category            | → Federation:AuthoritySystem (LCSH, Wikidata…)   |
| HAS_FEDERATION          | SYS_FederationRegistry         | → SYS_FederationSource (rebuild spec)            |
| HAS_SUBJECT_CONCEPT_ROOT| SubjectConceptRoot             | → SubjectConceptRegistry, AgentRegistry          |
| HAS_BIBLIOGRAPHY        | BibliographyRegistry           | → BibliographySource (planned)                   |
| HAS_SELF_DESCRIPTION    | SystemDescription              | Generated narrative                              |

**Note:** Multiple Chrystallum nodes can exist if scripts use different MERGE keys (`name` vs `id`). Consolidate to one with `id: 'CHRYSTALLUM_ROOT'`.

### Federation, FederationRoot

| Property | Type   | Description                                      |
|----------|--------|--------------------------------------------------|
| `name`   | string | Federation name (e.g. Trismegistos, LGPN)       |

**Relationships:** `(fr:FederationRoot)-[:HAS_FEDERATION]->(f:Federation)`

### SYS_Policy, PolicyVersion, DecisionTable, DecisionRule, etc.

Policy subgraph for decision rules. See `Neo4j/schema/17_policy_decision_subgraph_schema.cypher`.

---

## 9. Relationship Summary

| Relationship      | From → To                    | Description                                      |
|-------------------|------------------------------|--------------------------------------------------|
| MAPS_TO_FACET     | Federation node → CanonicalFacet | Semantic facet mapping, optional `weight`   |
| BROADER_THAN      | LCC_Class → LCC_Class         | Hierarchy (broader → narrower)                    |
| BROADER_THAN      | LCSH_Heading → LCSH_Heading   | (if loaded) Broader heading                      |
| BROADER_THAN      | Discipline → Discipline      | (legacy)                                         |
| HAS_LCSH_AUTHORITY| SubjectConcept → LCSH_Subject | Authority link                                  |
| HAS_FAST_AUTHORITY| SubjectConcept → FAST_Subject| Authority link                                   |
| CLASSIFIED_BY_LCC | SubjectConcept → LCC_Class   | LCC classification                               |
| PART_OF           | SubjectConcept → SubjectConcept | Hierarchy                                     |
| BROADER_CONCEPT   | SubjectConcept → SubjectConcept | Broader-narrower                             |
| CONTAINS          | Registry → SubjectConcept    | Registry membership                               |
| ANALYZES          | Agent → SubjectConcept       | Agent assignment                                 |
| CLASSIFIED_BY     | Human/Event/Place/Period → SubjectConcept | Entity classification (routing)        |
| ABOUT             | Work → SubjectConcept       | Work is about a SubjectConcept; edge may have `{facets, source, confidence}` |
| ASSIGNED_IN       | Work → Discipline           | Work appears in syllabi; edge may have `{count, first_year, last_year}` |
| CLASSIFIED_AS     | Work → LCC_Class            | Work LCC classification                       |
| HAS_LCSH_SUBJECT  | Work → LCSH_Heading         | Work has LCSH subject heading                  |
| HAS_FAST_SUBJECT  | Work → FAST_Subject        | Work has FAST subject                          |
| PRODUCED          | Agent → Claim               | Agent produced a Claim                          |
| PARTICIPATED_IN   | Human → Period/Event         | Participation                                   |
| OCCURRED_DURING   | Event → Period               | Temporal grounding                                |
| OCCURRED_AT       | Event → Place                | Spatial grounding                                 |
| STARTS_IN_YEAR    | Period/Event → Year           | Temporal anchor                                   |
| ENDS_IN_YEAR      | Period/Event → Year           | Temporal anchor                                   |
| PART_OF           | Year → Decade → Century → Millennium | Temporal hierarchy                        |
| HAS_SUBJECT_CONCEPT | Period/Event → SubjectConcept | Domain link                                   |
| ALIGNED_WITH_PLEIADES | Place → AuthorityRecord   | Pleiades alignment                               |
| POSITIONED_AS       | SubjectConcept → ClassificationAnchor/Entity | Federation positioning (SCA), with `federation`, `hops`, `rel_type` |
| PROVIDES_ANCHOR     | SYS_FederationSource → ClassificationAnchor | Federation provenance                          |
| HAS_FACET_CLUSTER   | Chrystallum → Facets:Category                | Facet taxonomy root                            |
| HAS_FEDERATION_CLUSTER | Chrystallum → Federation:Category         | Authority system taxonomy                      |
| HAS_FEDERATION      | Chrystallum → SYS_FederationRegistry         | Operational federation sources                 |
| HAS_SUBJECT_CONCEPT_ROOT | Chrystallum → SubjectConceptRoot         | Subject concept + agent registries             |
| HAS_BIBLIOGRAPHY    | Chrystallum → BibliographyRegistry          | Bibliography backbone (planned)                |
| ALIGNED_WITH_GEO_BACKBONE | Pleiades_Place → Place                   | Links survey node to geographic backbone (same pleiades_id) |

---

## 10. Loader Quick Reference

| Node Type      | Loader Script                          | Survey JSON                               |
|----------------|----------------------------------------|-------------------------------------------|
| LCSH_Heading   | `load_lcsh_survey.py`                  | `lcsh_roman_republic.json`                |
| Pleiades_Place | `load_federation_survey.py`            | `pleiades_roman_republic.json` (+ `link_pleiades_place_to_geo_backbone.py` post-load) |
| Periodo_Period | `load_federation_survey.py`            | `periodo_roman_republic.json`             |
| DPRR_Office    | `load_federation_survey.py`            | `dprr_roman_republic.json`                |
| WorldCat_Work  | `load_federation_survey.py`            | `worldcat_roman_republic.json`            |
| LCC_Class      | `load_lcc_nodes.py`                    | `lcc_roman_republic.json` / `lcc_full.json` |
| CanonicalFacet | `create_facets_cluster.cypher`         | (bootstrap)                               |
| Work           | `load_worldcat_works.py`, `load_open_syllabus_works.py` | (enriched) |
| Discipline     | `load_disciplines_registry.py`         | `discipline_majors_consolidated_disciplines_filtered.csv` |
| SubjectDomain  | `bootstrap_subject_domains.py`          | (config)                                  |
| Agent          | `bootstrap_agents.cypher`               | (bootstrap)                               |
| Claim          | `sca_sfa_claim_writer.py`               | (agent outputs)                           |

---

## 11. Related Documentation

- **Chrystallum subgraph:** `docs/CHRYSTALLUM_SUBGRAPH_SPEC.md` (root structure, branches, bootstrap runbook)
- **Bootstrap full system:** `python scripts/neo4j/bootstrap_system_subgraph.py`
- **View full subgraph:** `scripts/federation/view_full_system_subgraph.cypher` (run in Neo4j Browser)
- **Schema reference:** `md/Reference/SCHEMA_REFERENCE.md` (core entities, relationships, facets)
- **Subject concept:** `Cypher/subject_concept_operations.cypher`, `docs/architecture/SUBJECT_CONCEPT_CREATION_AND_AUTHORITY.md`
- **Federation node schema:** `scripts/federation_node_schema.py` (alignment fields, dimensions)
- **Constraints:** `Cypher/schema/constraints_chrystallum_generated.cypher`
