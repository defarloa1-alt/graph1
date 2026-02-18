# Chrystallum Architecture Implementation Index

**Last Updated:** 2026-02-18  
**Status:** Consolidated-Only Crosswalk (canonical)

---

## Canonical Architecture Source

**PRIMARY SOURCE:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` (v3.2)
- 7,698 lines covering complete system architecture
- Sections 1-12 (Executive, Ontology, Implementation, Governance)
- Appendices A-N (Registries, Taxonomies, Alignment Strategies)
- **DO NOT DUPLICATE** content from this file—reference section numbers instead

Deprecated as architecture sources: legacy split documents.

Appendices remain part of the consolidated file, not separate source documents.

---

## Agent Implementation Progress

**Step-by-Step Agent Build-Out (2026-02-15):**

| Step | Status | Purpose | Methods Added | Documentation |
|------|--------|---------|---------------|---------------|
| **Step 1** | ✅ Complete | Architecture understanding via meta-schema | 8 methods | `md/Reports/STEP_1_COMPLETE.md` |
| **Step 2** | ✅ Complete | State introspection for stateless LLMs | 8 methods | `md/Reports/STEP_2_COMPLETE.md` |
| **Step 3** | ✅ Complete | Federation-driven discovery (Wikidata) | 6 methods | `md/Reports/STEP_3_COMPLETE.md` |
| **Step 3.5** | ✅ Complete | Completeness validation (841 entities) | 2 methods | `md/Architecture/PROPERTY_PATTERN_MINING_INTEGRATION.md` |
| **Step 4** | ✅ Complete | Ontology alignment (CIDOC-CRM/CRMinf) | 4 methods | `Archive/STEP_4_COMPLETE_2026-02-15.md` |
| **Step 5** | ✅ Complete | Operational Modes (Initialize → Proposal → Training) | 3 methods | `md/Reports/STEP_5_DESIGN_OPERATIONAL_MODES.md`, `md/Reports/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md` |
| **Step 6** | 🎯 Design | Wikipedia Training (Article discovery → Claim extraction) | 1 method | `md/Reports/STEP_6_DESIGN_WIKIPEDIA_TRAINING.md` |
| **Step 5+** | ⏸️ Pending | Query modes (Schema/Data) + SubjectConceptAgent | TBD | `md/Reports/STEP_5_DESIGN_OPERATIONAL_MODES.md` |

**Total Methods:** 31 across 5 operational modes (Steps 1-4 + Step 5 Initialize/Proposal/Training)  
**System Prompts Version:** 2026-02-15-step5 (17 facets updated)  
**Agent Framework:** `scripts/agents/facet_agent_framework.py` (~3,000 lines + Subject Ontology Proposal method)

**NEW (2026-02-15): SCA Two-Phase Workflow**
- **Phase 1: Un-Faceted Exploration** (Initialize + Ontology Proposal)
  * Just hunting nodes and edges (NO facet lens)
  * Creates shell nodes via hierarchy traversal + backlinks
  * Outputs proposed ontology → **APPROVAL POINT**
- **Phase 2: Facet-by-Facet Analysis** (Training Mode)
  * SCA sequentially adopts facet roles (military → political → cultural → etc.)
  * Reads same claims from different facet perspectives
  * 5x claim richness from multi-facet analysis
- **Purple to mollusk** scenarios enabled by un-faceted discovery
- See: [SCA_TWO_PHASE_WORKFLOW.md](../Agents/SCA/SCA_TWO_PHASE_WORKFLOW.md), [SCA_SEED_AGENT_PATTERN.md](../Agents/SCA/SCA_SEED_AGENT_PATTERN.md)

---

## Section Crosswalk (Consolidated -> Implementation)

| Consolidated section | Implementation assets | Notes |
|---|---|---|
| **Section 3: Entity Layer** | `Neo4j/schema/01_schema_constraints.cypher`, `Neo4j/schema/02_schema_indexes.cypher`, `Neo4j/schema/03_schema_initialization.cypher`, `Neo4j/schema/05_temporal_hierarchy_levels.cypher` | First-class node and temporal backbone model |
| **Section 3.3: Facets** | `Facets/facet_registry_master.json`, `Facets/facet_registry_master.csv` | 18 facets (biographic added), registry is canonical source |
| **Section 3.4: Temporal Modeling** | `scripts/backbone/temporal/genYearsToNeo.py`, `scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py`, `Neo4j/schema/05_temporal_hierarchy_levels.cypher` | Year->Decade->Century->Millennium hierarchy |
| **Section 4: Subject Layer** | `scripts/backbone/subject/create_subject_nodes.py`, `Python/fast/scripts/import_fast_subjects_to_neo4j.py` | SubjectConcept authority alignment |
| **Section 4.3: Temporal Authorities** | `Temporal/` assets, temporal scripts, PeriodO integration scripts (as available) | Authority alignment + uncertain date handling |
| **Section 4.4: Geographic Authorities** | `Geographic/` assets, place normalization scripts | TGN/Pleiades/GeoNames integration |
| **Section 4.4.1: Place/PlaceVersion (Chrystallum)** | `CHRYSTALLUM_PLACE_SEEDING_REQUIREMENTS.md`, `PLACE_VERSION_NEO4J_SCHEMA.cypher`, `CHRYSTALLUM_PHASE2_INTEGRATION.md` | Temporal-geographic modeling with boundary versioning (deferred to post-Phase-2 analysis) |
| **Section 4.5: Wikidata Integration** | `scripts/tools/wikidata_fetch_all_statements.py`, `scripts/tools/wikidata_statement_datatype_profile.py`, `scripts/tools/wikidata_backlink_harvest.py`, `scripts/tools/wikidata_backlink_profile.py` | Federation + backlink pipeline |
| **Section 4.5.1: CIDOC-CRM/CRMinf Alignment** | `CIDOC/cidoc_wikidata_mapping_validated.csv`, `scripts/agents/facet_agent_framework.py` (Step 4 methods), `STEP_4_COMPLETE.md` | Ontology alignment for museum/archive interoperability (105 mappings) |
| **Section 4.5.2: KBpedia/KKO Overlay (proposal-only)** | `md/Architecture/ADR-003-KBpedia-Role-and-Boundaries.md`, `md/Architecture/KBPEDIA_MAPPING_CONFIDENCE_RUBRIC.md`, `CSV/kko_chrystallum_crosswalk.csv`, `scripts/tools/kko_mapping_proposal_loader.py` | Semantic typing overlay; scaffold/proposal only, no direct canonical mutation |
| **Section 5: Agent Architecture** | `md/Agents/` prompts/specs, orchestration docs in `md/Architecture/` | Domain routing + specialization |
| **Section 6: Claims Layer** | `Neo4j/schema/01_schema_constraints.cypher` (Claim constraints), claim proposal artifacts in `JSON/wikidata/proposals/`, `md/Architecture/ADR-006-Claim-Confidence-Decision-Model.md`, `Neo4j/schema/17_policy_decision_subgraph_schema.cypher` | claim_id + cipher + lifecycle + deterministic confidence policy track + policy subgraph projection |
| **Section 7: Relationship Layer** | `Relationships/relationship_types_registry_master.csv`, `CSV/project_p_values_canonical.csv` | canonical relation typing + P-value alignment |
| **Section 8: Technology/Orchestration** | `Neo4j/IMPLEMENTATION_ROADMAP.md`, orchestration docs in `md/Architecture/` | runtime architecture |
| **Section 8.6: Federation Dispatcher** | `scripts/tools/wikidata_backlink_harvest.py`, `Neo4j/FEDERATION_BACKLINK_STRATEGY.md` | route-by-datatype/value_type + gates |
| **Section 9: Workflows** | Workflow docs in `md/Architecture/`, scripts in `scripts/tools/` | extraction -> validation -> write |
| **Section 10: Quality Assurance** | `md/Guides/PHASE_1_CHECKLIST.md`, validation queries in `Neo4j/schema/04_temporal_bbox_queries.cypher` | quality gates + verification |

---

## Phase Mapping (Consolidated Numbering)

| Phase | Scope | Primary consolidated sections | Primary files |
|---|---|---|---|
| **Phase 1** | Schema + temporal backbone baseline | **3**, **3.4**, **10** | `Neo4j/schema/01_schema_constraints.cypher`, `Neo4j/schema/02_schema_indexes.cypher`, `Neo4j/schema/03_schema_initialization.cypher`, `Neo4j/schema/05_temporal_hierarchy_levels.cypher` |
| **Phase 2A+2B** | Backlink harvest + two-track validation (analysis run) | **4.5**, **8.6**, **9** | `GPT_PHASE_2_PARALLEL_PROMPT.md`, `temporal_bridge_discovery.py`, `PHASE_2_QUICK_START.md`, `NEO4J_SCHEMA_UPDATES_PHASE2.md` |
| **Phase 2** | Federation + enrichment | **4.3**, **4.4**, **4.5**, **8.6**, **9** | `scripts/tools/wikidata_*`, `Neo4j/FEDERATION_BACKLINK_STRATEGY.md`, geographic/temporal federation scripts |
| **Phase 3** | Agent orchestration + claims lifecycle | **5**, **6**, **7**, **8**, **9**, **10** | agent specs/prompts, claim workflow scripts, relationship registries |
| **Phase 4+** | Place/PlaceVersion enrichment | **4.4.1**, **3.4** | `CHRYSTALLUM_PLACE_SEEDING_REQUIREMENTS.md`, `PLACE_VERSION_NEO4J_SCHEMA.cypher`, transformation scripts (TBD) |

---

## Critical Alignment Rules

1. Section references in implementation docs must cite consolidated numbering.
2. `Subject`/`Concept` are legacy labels; use `SubjectConcept`.
3. `Person` is legacy wording; use `Human`.
4. `Communication` is a facet/domain axis, not a first-class node label.
5. Federation writes must pass dispatcher gates (Section 8.6) before persistence.

---

## Operational Entry Points

### Neo4j schema
- `Neo4j/schema/01_schema_constraints.cypher`
- `Neo4j/schema/02_schema_indexes.cypher`
- `Neo4j/schema/03_schema_initialization.cypher`
- `Neo4j/schema/05_temporal_hierarchy_levels.cypher`
- `Neo4j/schema/17_policy_decision_subgraph_schema.cypher`

### Federation tools
- `scripts/tools/wikidata_fetch_all_statements.py`
- `scripts/tools/wikidata_statement_datatype_profile.py`
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`
- `scripts/tools/wikidata_generate_claim_subgraph_proposal.py`
- `scripts/backbone/geographic/download_pleiades_bulk.py`
- `scripts/backbone/geographic/import_pleiades_to_neo4j.py`
- `scripts/backbone/geographic/verify_pleiades_import.py`

Federation adapter status:
- Active: Wikidata, Pleiades
- Planned/TODO (architecture-defined): Trismegistos, EDH, VIAF, GeoNames

### KBpedia/KKO proposal-only mapping
- `md/Architecture/ADR-003-KBpedia-Role-and-Boundaries.md`
- `md/Architecture/KBPEDIA_MAPPING_CONFIDENCE_RUBRIC.md`
- `CSV/kko_chrystallum_crosswalk.csv`
- `scripts/tools/kko_mapping_proposal_loader.py`

### Claim confidence decision model (policy-gate track)
- `md/Architecture/ADR-006-Claim-Confidence-Decision-Model.md`
- `JSON/policy/claim_confidence_policy_v1.json`
- `scripts/tools/claim_confidence_policy_engine.py`
- `scripts/tools/policy_subgraph_loader.py`
- `Neo4j/schema/17_policy_decision_subgraph_schema.cypher`
- existing claim pipeline paths to migrate from fixed thresholds:
- `Neo4j/schema/14_claim_promotion_seed.cypher`
- `Neo4j/schema/run_qid_pipeline.py`

### CIDOC-CRM/CRMinf Ontology Alignment (Step 4)
- `CIDOC/cidoc_wikidata_mapping_validated.csv` (105 mappings)
- `CIDOC/CIDOC-CRM_Wikidata_Alignment_Strategy.md` (alignment strategy)
- `scripts/agents/facet_agent_framework.py` (Step 4 methods: enrich_with_ontology_alignment, enrich_claim_with_crminf)
- `Archive/STEP_4_COMPLETE_2026-02-15.md` (Step 4 documentation)

### Agent Framework Documentation
- `md/Reports/STEP_1_COMPLETE.md` (Architecture understanding)
- `md/Reports/STEP_2_COMPLETE.md` (State introspection)
- `md/Reports/STEP_3_COMPLETE.md` (Federation discovery)
- `md/Architecture/PROPERTY_PATTERN_MINING_INTEGRATION.md` (Step 3.5 completeness validation)
- `Archive/STEP_4_COMPLETE_2026-02-15.md` (Ontology alignment)
- `md/Reference/AGENT_SESSION_QUICK_REFERENCE.md` (Quick reference for all 28 methods)
- `Prompts/facet_agent_system_prompts.json` (version 2026-02-15-step4)

### Project Artifact Registry (SCA/SFA routing)
- `scripts/tools/build_project_artifact_registry.py`
- `CSV/registry/project_artifact_registry.csv`
- `CSV/registry/project_artifact_registry_review_queue.csv`
- `JSON/registry/project_artifact_registry.json`
- `JSON/registry/project_artifact_registry_overrides.json`
- `md/Core/AGENT_ARTIFACT_ROUTING_GUIDE.md`
- `md/Core/PROJECT_ARTIFACT_REGISTRY_TODO.md`
- `md/Core/PROJECT_ARTIFACT_REGISTRY_DECISIONS.md`

### Canonical registries
- `Relationships/relationship_types_registry_master.csv`
- `CSV/project_p_values_canonical.csv`
- `Facets/facet_registry_master.json`

---

## Verification Checklist

- [ ] No split-document references as source-of-truth.
- [ ] All phase mappings cite consolidated section numbers.
- [ ] All node label examples use canonical labels.
- [ ] Federation documentation references dispatcher controls.

---

## Change Control

When architecture changes, update in this order:
1. `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
2. Neo4j schema/scripts
3. This index file
4. `AI_CONTEXT.md` and `Change_log.py`

**Recent Updates:**
- **2026-02-18:** Artifact registry override engine + decisions log added; review queue reduced to 0 open items
- **2026-02-18:** Project artifact registry bootstrap added (generator + CSV/JSON snapshots + routing guide) for SCA/SFA/Pi entry-point routing
- **2026-02-18:** Policy-subgraph projection path added (loader + Neo4j schema) for hash-pinned decision tables
- **2026-02-18:** Claim confidence decision-model ADR added (`ADR-006`) for ordered single-hit policy-gate evaluation
- **2026-02-18:** KBpedia/KKO overlay boundaries formalized (ADR-003), confidence rubric added, crosswalk seed + proposal-only loader added
- **2026-02-15:** Step 4 complete (CIDOC-CRM/CRMinf ontology alignment integrated)
- **2026-02-15:** Step 3.5 complete (Property pattern mining from 841 entities)
- **2026-02-15:** Step 3 complete (Federation-driven discovery with Wikidata)
- **2026-02-15:** Step 2 complete (State introspection for stateless LLMs)
- **2026-02-15:** Step 1 complete (Meta-schema graph for architecture understanding)
- **2026-02-14:** Architecture consolidated to single source document
