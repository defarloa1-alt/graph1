# Chrystallum Architecture → Implementation Reference Index

**Date:** February 13, 2026  
**Purpose:** Cross-reference between architecture specification and implementation files  
**Status:** Phase 1 Ready

---

## Quick Navigation

### Architecture Sections → Implementation Files

| Architecture Section | Implementation Files | Status |
|---|---|---|
| **Section 3: Entity Layer** | `Neo4j/schema/01_schema_constraints.cypher` | ✅ 60+ constraints |
| | `Neo4j/schema/02_schema_indexes.cypher` | ✅ 50+ indexes |
| | `Neo4j/schema/03_schema_initialization.cypher` | ✅ Bootstrap entities |
| **Section 3.4: Temporal Modeling** | `Neo4j/schema/03_schema_initialization.cypher` (lines: Year backbone) | ✅ 4,026 nodes |
| **Section 4: Subject Layer** | `Python/fast/scripts/import_fast_subjects_to_neo4j.py` | ✅ FAST → Cypher |
| **Section 4.3: Temporal Authority** | (See Section 3.4 + PeriodO integration) | ⏳ Phase 2 |
| **Section 4.4: Geographic Authority** | (Pleiades/TGN linking - Phase 2) | ⏳ Phase 2 |
| **Section 4.5: Wikidata Integration** | `Neo4j/IMPLEMENTATION_ROADMAP.md` (Step 4: Federation Supercharging) | ⏳ Phase 2 |
| **Section 5: Agent Architecture** | `Python/agents/chrystallum_agents.py` (TBD Phase 3) | ⏳ Phase 3 |
| **Section 6: Claims Layer** | (Claims initialization - Phase 3) | ⏳ Phase 3 |
| **Section 8: Technology Stack** | `Neo4j/IMPLEMENTATION_ROADMAP.md` (Neo4j 5.0+, LangGraph orchestration) | ✅ Documented |
| **Section 10: Quality Assurance** | (QA pipeline - Phase 3) | ⏳ Phase 3 |

---

## Implementation File Structure

### Core Schema Files

**Location:** `c:\Projects\Graph1\Neo4j\schema\`

#### 01_schema_constraints.cypher
- **Lines:** 600+
- **Purpose:** Data integrity enforcement
- **Contains:** 60+ uniqueness & existence constraints
- **Maps to:** Section 3.5 (Schema Enforcement & Constraints)
- **Execution Time:** ~1 minute
- **Prerequisite:** None (run first)

**Key Constraints:**
- Entity uniqueness (entity_id, qid, viaf_id, pleiades_id, etc.)
- Authority ID uniqueness (LCSH, FAST, VIAF, GND)
- Required property constraints (entity must have type, label, etc.)
- Temporal backbone constraints (Year must have year number)

---

#### 02_schema_indexes.cypher
- **Lines:** 400+
- **Purpose:** Query performance optimization
- **Contains:** 50+ indexes across multiple categories
- **Maps to:** Section 3.5.2 (Architectural Decisions re: indexing)
- **Execution Time:** ~5-10 minutes (on cold database)
- **Prerequisite:** 01_schema_constraints.cypher
- **Impact:** 50-1000x query speedup

**Index Categories:**
- **Primary Key Indexes (10+):** entity_id, qid, viaf_id lookups
- **Temporal Indexes (10+):** start_date, end_date, birth_date, death_date
- **Classification Indexes (10+):** entity_type, facet, authority_tier
- **Composite Indexes (5+):** multi-property lookups (type + time, culture + date)
- **Text Search Indexes (5+):** full-text on labels/names

---

#### 03_schema_initialization.cypher
- **Lines:** 500+
- **Purpose:** Bootstrap foundational entities and Year backbone
- **Contains:** Year nodes (4,026), Facets (16), Places (3), Periods (3), Humans (1), Organizations (1)
- **Maps to:** Section 3.4 (Temporal Modeling), Section 3.2 (Facets)
- **Execution Time:** ~30 seconds
- **Prerequisite:** 01_schema_constraints.cypher, 02_schema_indexes.cypher

**Bootstrap Entities:**
- **Year Backbone:** -2000 to 2025 (4,026 linked nodes with FOLLOWED_BY/PRECEDED_BY)
- **Facet Categories:** 16 analytical dimensions (Political, Military, Economic, etc.)
- **Places:** Rome, Italy, Mediterranean
- **Periods:** Roman Republic, Roman Empire, Late Republic
- **Humans:** Julius Caesar (test entity)
- **Organizations:** Roman Senate
- **Gens:** Julia

---

### Implementation Guides

**Location:** `c:\Projects\Graph1\Neo4j\`

#### SCHEMA_BOOTSTRAP_GUIDE.md
- **Lines:** 600+
- **Purpose:** Comprehensive schema documentation
- **Maps to:** All of Section 3 + federation concepts
- **Contains:**
  - Quick-start installation steps
  - Entity type catalog (14 core + 3 Roman + 3 analysis types)
  - Relationship directory (temporal, hierarchical, semantic, analysis)
  - Design patterns explained (Year backbone, PlaceVersion, Facet star pattern, SKOS hierarchy)
  - Constraint strategy & rationale
  - Index strategy & performance benchmarks
  - Initialization details & verification queries
  - Scaling recommendations (1K → 1M+ entities)
  - Maintenance & operations guide
  - Troubleshooting guide

---

#### IMPLEMENTATION_ROADMAP.md
- **Lines:** 450+
- **Purpose:** Step-by-step implementation path (Phase 1-3)
- **Maps to:** Sections 8-9 (Technology Stack, Workflows)
- **Contains:**
  - Phase 1: Neo4j Schema Bootstrap (2-3 hours)
    - Step 1: Schema definition & deployment
    - Step 2: Test data ingestion (FAST subjects)
    - Step 3: Schema validation & performance testing
  - Phase 2: Federation Integration & Data Enrichment (4 days)
    - Step 4: Wikidata Federation Supercharging
    - Step 5: Events & Works Import
    - Step 6: Authority Conflict Resolution
  - Phase 3: Agent & Claims Layer (3 days)
    - Step 7: Claims Layer Initialization
    - Step 8: Multi-Agent Evaluation Setup
  - Configuration files (neo4j.conf, requirements.txt)
  - Timeline & checkpoints
  - Success criteria (Phase 1-3)
  - Implementation checklist

---

### Data Import Pipelines

**Location:** `c:\Projects\Graph1\Python\`

#### fast/scripts/import_fast_subjects_to_neo4j.py
- **Lines:** 400+
- **Purpose:** LCSH/FAST subjects → Cypher import statements
- **Maps to:** Section 4 (Subject Layer)
- **Input:** JSONLD or CSV subjects (FAST/LCSH records)
- **Output:** Cypher CREATE statements (bulk import)
- **Status:** ✅ Tested on 50-subject sample
- **Next:** Full FASTTopical_parsed.csv import (100K+ subjects)

**Functionality:**
- Parse LCSH/FAST authority records
- Classify into authority tiers (TIER_1/2/3)
- Score across 6+ facet dimensions
- Generate facet anchor relationships
- Create Cypher import script

**Example Output:**
```cypher
CREATE (s:Subject {lcsh_id: "sh00000014", unique_id: "SUBJECT_LCSH_sh00000014", 
  label: "Tacos", authority_tier: "TIER_3", authority_confidence: 0.7});
```

---

#### fast/IMPORT_GUIDE.md
- **Lines:** 500+
- **Purpose:** Usage guide for subject import pipeline
- **Contains:**
  - Quick start commands
  - Authority tier framework explanation
  - Facet scoring methodology
  - Data model documentation
  - Cypher import process (3 steps)
  - Enhancement roadmap

---

### Reference Documentation

#### neo4j/schema/SCHEMA_BOOTSTRAP_GUIDE.md
See section above (duplicate entry for clarity)

---

## Architecture → Implementation Mapping Detail

### Entity Layer (Section 3) → Neo4j Schema

```
Section 3.1: Core Entity Types (14 types)
  ├─ Human (PERSON entities)
  │   └─ 01_schema_constraints: human_entity_id_unique, human_qid_unique, human_viaf_id_unique
  │   └─ 02_schema_indexes: human_entity_id_index, human_qid_lookup, human_viaf_lookup, human_birth_date_index
  │   └─ 03_schema_initialization: Create Julius Caesar (test entity)
  │
  ├─ Place (GEOGRAPHIC entities)
  │   └─ 01_schema_constraints: place_entity_id_unique, place_qid_unique, place_pleiades_id_unique
  │   └─ 02_schema_indexes: place_entity_id_index, place_tgn_lookup, place_pleiades_lookup
  │   └─ 03_schema_initialization: Create Rome, Italy, Mediterranean (foundational)
  │
  ├─ Event (TEMPORAL entities)
  │   └─ 01_schema_constraints: event_entity_id_unique, event_qid_unique
  │   └─ 02_schema_indexes: event_entity_id_index, event_start_date_index, event_end_date_index
  │   └─ (FUTURE) Events import pipeline (Phase 2)
  │
  ├─ Period (HISTORIOGRAPHIC temporal spans)
  │   └─ 01_schema_constraints: period_entity_id_unique, period_qid_unique
  │   └─ 02_schema_indexes: period_entity_id_index, period_start_index, period_end_index, period_facet_index
  │   └─ 03_schema_initialization: Create Roman Republic, Empire, Late Republic
  │
  ├─ Year (TEMPORAL BACKBONE - critical)
  │   └─ 01_schema_constraints: year_entity_id_unique, year_year_number_unique
  │   └─ 02_schema_indexes: year_entity_id_index, year_number_index, year_iso_index
  │   └─ 03_schema_initialization: CREATE 4,026 Year nodes (-2000 to 2025) with sequential linkage
  │
  ├─ Organization, Institution, Dynasty, Position, Work, etc.
  │   └─ Each has corresponding constraints & indexes in 01 & 02
  │   └─ 03_schema_initialization: Examples for Senate, Gens Julia
```

### Subject Layer (Section 4) → Subject Import Pipeline

```
Section 4: Subject Layer
  ├─ 4.0 Overview: Multi-authority alignment
  │   └─ Python/fast/scripts/import_fast_subjects_to_neo4j.py: Implements alignment
  │
  ├─ 4.1 SubjectConcept Node Schema
  │   └─ import_fast_subjects_to_neo4j.py: Creates (:Subject) nodes with required properties
  │
  ├─ 4.2 Facets (16 Analytical Dimensions)
  │   └─ 03_schema_initialization: Create 16 FacetCategory nodes
  │   └─ import_fast_subjects_to_neo4j.py: Link subjects to facets
  │
  ├─ 4.3 Temporal Authority Alignment (ISO 8601, PeriodO)
  │   └─ FUTURE: PeriodO integration (Phase 2)
  │
  ├─ 4.4 Geographic Authority Integration (TGN, Pleiades, Geonames)
  │   └─ FUTURE: Geographic federation pipeline (Phase 2)
  │
  ├─ 4.5 Wikidata Integration Patterns
  │   └─ FUTURE: Federation supercharging (Phase 2, Step 4)
  │   └─ Neo4j/IMPLEMENTATION_ROADMAP.md: Documents approach
```

### Claims Layer (Section 6) → Future Implementation

```
Section 6: Claims Layer
  ├─ 6.0 Overview: Evidence-aware assertions
  │   └─ ⏳ Phase 3: Create claims initialization script
  │
  ├─ 6.1 Claim Node Schema
  │   └─ 01_schema_constraints: claim_id_unique, claim_has_confidence
  │   └─ 02_schema_indexes: claim_id_index, claim_confidence_index
  │   └─ ⏳ Phase 3: Populate claims from extracted facts
  │
  ├─ 6.2 Evidence Nodes
  │   └─ 01_schema_constraints: evidence_id_unique
  │   └─ 02_schema_indexes: evidence_id_index, evidence_confidence_index
  │   └─ ⏳ Phase 3: Link to Work/Source nodes
```

### Agent Layer (Section 5) → Future Implementation

```
Section 5: Agent Architecture
  ├─ 5.0 Overview: 16 facet-specialist agents + coordinator
  │   └─ ⏳ Phase 3: Python/agents/chrystallum_agents.py
  │
  ├─ 5.5 Agent Domain Assignment
  │   └─ 02_schema_indexes: subject_tier_index (for routing)
  │   └─ ⏳ Phase 3: Agent-to-facet mapping
```

---

## Federation Strategy → Implementation

**Reference Document:** `2-13-26-federation-impact.md`

```
Federation Tiers (4 levels):
  1. Golden Tier (LCSH, FAST, LCC, Dewey)
     └─ Already handled by FAST import pipeline
     
  2. Silver Tier (TGN, Pleiades, Trismegistos, DARE, PeriodO, Nomisma, Perseus)
     └─ ⏳ Phase 2, Step 4: Federation Supercharging
     └─ Python/neo4j/scripts/federation_supercharger.py (TBD)
     
  3. Bronze Tier (VIAF, WorldCat, GND, ISNI)
     └─ ⏳ Phase 2, Step 4: Multi-hop federation chains
     
Implementation Strategy:
  - Fetch SPARQL universe when entity ingested/enriched
  - Cache authority_links map on entity node
  - Create ALIGNED_WITH federation edges
  - Enable O(1) cross-authority lookup
  - Persist provenance metadata on each import
```

---

## File Dependency Graph

```
Phase 1: Neo4j Bootstrap
  01_schema_constraints.cypher
    ↓
  02_schema_indexes.cypher
    ↓
  03_schema_initialization.cypher
    ↓
  (VERIFY with SCHEMA_BOOTSTRAP_GUIDE.md)

Phase 2: FAST & Federation
  Python/fast/scripts/import_fast_subjects_to_neo4j.py
    ├─ Input: subjects_sample_50.jsonld OR FASTTopical_parsed.csv
    ├─ Output: subjects_import_sample.cypher OR fast_full_import.cypher
    └─ Import to Neo4j
  ↓
  (FUTURE) Python/neo4j/scripts/federation_supercharger.py (Step 4a)
    ├─ Queries Wikidata SPARQL for each subject
    ├─ Caches authority_links on Subject nodes
    └─ Creates ALIGNED_WITH federation edges
  ↓
  (FUTURE) Python/neo4j/scripts/backlink_enricher.py (Step 4b)
    ├─ Queries Wikidata reverse relationships (P710, P1441, P737, P828, P138, P112)
    ├─ Buckets by property + P31 (instance_of classification)
    ├─ Materializes edges: PARTICIPATED_IN, DEPICTED_IN, INFLUENCED, EPONYM_OF, etc.
    └─ Queues ambiguous edges for agent review
  ↓
  (FUTURE) Python/neo4j/scripts/temporal_facet_populator.py (Step 3)
    ├─ Queries PeriodO for all periods containing event dates
    ├─ Classifies by facet (Historiographical, Scientific, Religious, Economic, PeriodO, Fuzzy)
    ├─ Materializes OCCURRED_DURING edges with facet labels
    └─ Supports spatio-temporal bounding (Late Bronze Age varies by region)

Phase 3: Agents & Claims
  Python/agents/chrystallum_agents.py (TBD)
    ├─ Implements 16 facet-specialist agents
    ├─ Routes claims to agents
    └─ Generates FacetAssessment nodes
  ↓
  (FUTURE) Claims evaluation pipeline
```

---

## Key Files at a Glance

| File | Purpose | Lines | Location |
|---|---|---|---|
| **CONSOLIDATED.md** | Main architecture spec | 9,525 | Key Files/ |
| **01_schema_constraints.cypher** | Data integrity | 600+ | Neo4j/schema/ |
| **02_schema_indexes.cypher** | Performance | 400+ | Neo4j/schema/ |
| **03_schema_initialization.cypher** | Bootstrap | 500+ | Neo4j/schema/ |
| **SCHEMA_BOOTSTRAP_GUIDE.md** | Schema docs | 600+ | Neo4j/schema/ |
| **IMPLEMENTATION_ROADMAP.md** | Phase 1-3 plan | 500+ | Neo4j/ |
| **FEDERATION_BACKLINK_STRATEGY.md** | Backlink enrichment | 630+ | Neo4j/ |
| **TEMPORAL_FACET_STRATEGY.md** | Poly-temporal framework | 550+ | Neo4j/ |
| **import_fast_subjects_to_neo4j.py** | Subject importer | 400+ | Python/fast/scripts/ |
| **2-13-26-federation-impact.md** | Federation strategy | 130+ | Project root |

---

## Cross-References for Verification

✅ **All section references are linked:**
- Section 3 → Neo4j schema files
- Section 4 → FAST import + federation roadmap
- Section 5 → Agent implementation roadmap
- Section 6 → Claims implementation roadmap
- Section 8-9 → IMPLEMENTATION_ROADMAP.md
- Section 10 → IMPLEMENTATION_ROADMAP.md (Phase 3)

✅ **Phase 2 Enrichment (Recently Added):**
- FEDERATION_BACKLINK_STRATEGY.md: Backlink enrichment strategy & implementation (Step 4b)
- TEMPORAL_FACET_STRATEGY.md: Poly-temporal framework for multi-authority time (Step 3)

⏳ **Future cross-references (Phase 2-3):**
- Add links to federation_supercharger.py (Step 4a) when created
- Add links to backlink_enricher.py (Step 4b) when created
- Add links to temporal_facet_populator.py (Step 3) when created
- Add links to agent implementations when created
- Add links to claims initialization script when created

---

## How to Use This Index

**For Implementation:**
1. Start with **IMPLEMENTATION_ROADMAP.md** for step-by-step guidance
2. Reference **SCHEMA_BOOTSTRAP_GUIDE.md** for schema design details
3. Execute scripts in order: 01 → 02 → 03
4. Follow Phase progression for data imports

**For Architecture Review:**
1. Read **CONSOLIDATED.md** main sections (1-12)
2. Use this index to cross-reference implementation files
3. Verify each section has corresponding implementation coverage

**For Troubleshooting:**
1. Consult **SCHEMA_BOOTSTRAP_GUIDE.md** "Troubleshooting" section
2. Check **IMPLEMENTATION_ROADMAP.md** "Support & Troubleshooting"
3. Review constraint/index definitions in 01_schema_constraints.cypher and 02_schema_indexes.cypher

---

**Last Updated:** 2026-02-13  
**Next Update:** After Phase 1 completion (add implementation results)
