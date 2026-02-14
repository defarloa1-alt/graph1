# AI Context and Handover Log
Maintained by LLM agents to preserve context across sessions.

---

## ⚠️ Important: Persistence Workflow

**This file only works as a memory bank if committed and pushed regularly.**

- **Local sessions**: Updates are visible in real-time ✅
- **Future sessions**: Only see last pushed version ⚠️
- **Other AI agents**: Need to pull latest from GitHub ⚠️

**Workflow for AI agents:**
1. **Start of session**: Read this file first (pull latest if stale)
2. **During session**: Update as you complete milestones
3. **End of session**: Commit and push this file so next agent sees current state

**Without regular pushes, this becomes a local-only scratchpad.**

---

## Project
Chrystallum Knowledge Graph
Goal: Build a federated historical knowledge graph using Neo4j, Python, and LangGraph.

## Current Architecture State (verified 2026-02-13)

### 1. Temporal Backbone (Calendrical Spine)
Structure:
`Year -> PART_OF -> Decade -> PART_OF -> Century -> PART_OF -> Millennium`

Status: Implemented.

Decisions locked in:
- Historical mode: no `Year {year: 0}` node.
- Year sequence is unidirectional: `FOLLOWED_BY` only.
- BCE/CE labels are historical-style while IDs remain numeric buckets.

Canonical implementation files:
- `scripts/backbone/temporal/genYearsToNeo.py`
- `scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py`
- `scripts/backbone/temporal/05_temporal_hierarchy_levels.cypher`

### 2. Historical Period Spine
Status in clean baseline: not materialized in the live DB.

Notes:
- `scripts/backbone/temporal/create_canonical_spine.py` exists for period/era modeling.
- `scripts/backbone/temporal/link_years_to_periods.py` does not exist.

### 3. Live Neo4j Baseline (clean)
Only temporal backbone labels are present:
- `Year: 4025` (`-2000..2025`, no year 0)
- `Decade: 403`
- `Century: 41`
- `Millennium: 5`

Relationships:
- `FOLLOWED_BY` (Year chain): 4024
- `PART_OF`: 4469
- `PRECEDED_BY`: 0
- Bridge exists: `(-1)-[:FOLLOWED_BY]->(1)`

## Key Corrections (important)
- Previous notes claiming `link_years_to_periods.py` were inaccurate.
- Migration scripts were synced to corrected historical logic (BCE-safe bucketing and labels).
- Documentation was updated to reflect `FOLLOWED_BY`-only year sequencing.

## Concept Label Canonicalization (verified 2026-02-14)

Decision locked:
- `Concept` is deprecated as a node label.
- `SubjectConcept` is canonical.

Migration note:
- `md/Architecture/CONCEPT_TO_SUBJECTCONCEPT_MIGRATION_2026-02-14.md`

Applied updates:
- Removed legacy multi-label examples like `:Person:Concept`, `:Place:Concept`, `:Event:Concept`.
- Updated prompts/guides/roadmap snippets to map concept-like targets to `:SubjectConcept`.
- Updated canonical source index to point to the migration note.

## Main-Node Baseline Sync (verified 2026-02-14)

- `md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md` now references `Key Files/Main nodes.md` as the current operational main-node baseline.
- The operational list was synchronized to:
  - `SubjectConcept, Human, Gens, Praenomen, Cognomen, Event, Place, Period, Dynasty, Institution, LegalRestriction, Claim, Organization, Year`
- `Communication` was demoted from first-class node status and is now treated as a facet/domain axis.
- The consolidated architecture now includes an explicit normative lock:
  - `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`, Section `3.0.1 Canonical First-Class Node Set (Normative)`.
  - Section 3.3 facet count corrected to 17 with explicit communication facet policy.
- Neo4j schema files were aligned to this lock:
  - `Neo4j/schema/01_schema_constraints.cypher`: canonical label lock note + first-class `id_hash` uniqueness + `Claim.cipher` required.
  - `Neo4j/schema/02_schema_indexes.cypher`: first-class `id_hash` and `status` indexes + explicit `Claim.cipher` index.

## Consolidated Doc Consistency Pass (verified 2026-02-14)

- Performed a wording/structure pass for Section `8.6 Federation Dispatcher and Backlink Control Plane` and Appendix K pipeline wording.
- Clarified dispatcher no-bypass rule and aligned terminology between:
  - Section `8.6` route/gate rules
  - Appendix `K.4-K.6` operational contract

## SysML + Implementation Index Realignment (verified 2026-02-14)

- SysML model now references consolidated architecture as the sole normative source:
  - `Key Files/2-13-26 SysML v2 System Model - Blocks and Ports (Starter).md`
- Updated SysML coverage to include:
  - block responsibilities aligned to consolidated sections
  - typed port payload contracts
  - federation dispatcher flow control (Section 8.6)
  - claim lifecycle states (`proposed|validated|disputed|rejected`)
  - deterministic agent routing policy
- Both implementation indexes were rewritten as consolidated-only crosswalks:
  - `Key Files/ARCHITECTURE_IMPLEMENTATION_INDEX.md`
  - `ARCHITECTURE_IMPLEMENTATION_INDEX.md`
- BODY/APPENDICES are no longer used as architecture source documents in the index mapping.

## Bootstrap Validation Runner (verified 2026-02-14)

- Added a single dry-validation Cypher runner:
  - `Neo4j/schema/06_bootstrap_validation_runner.cypher`
- Validates:
  - `SHOW CONSTRAINTS` name set vs expected
  - `SHOW INDEXES` user-created name set vs expected
  - non-ONLINE user index detection
  - final PASS/FAIL summary row
- Expected name sets are generated from:
  - `Neo4j/schema/01_schema_constraints.cypher`
  - `Neo4j/schema/02_schema_indexes.cypher`
- Compatibility lock:
  - use `SHOW CONSTRAINTS` / `SHOW INDEXES` directly (no dependency on `db.constraints()` or `db.indexes()`, which may be unavailable in some builds)
  - aggregate-safe pattern is required: collect in `WITH`, then compare lists in later `WITH`/`RETURN` stages

## Core Pipeline Schema Phase (verified 2026-02-14)

- Added focused schema bootstrap:
  - `Neo4j/schema/07_core_pipeline_schema.cypher`
- Added phase-matched validator:
  - `Neo4j/schema/08_core_pipeline_validation_runner.cypher`
- Phase scope:
  - `Human`, `Place`, `Event`, `Period`, `SubjectConcept`, `Claim`,
    `RetrievalContext`, `Agent`, `AnalysisRun`, `FacetAssessment`
- Execution model:
  - Run after temporal backbone baseline (`Year/Decade/Century/Millennium`)
  - Uses `IF NOT EXISTS` for all constraints/indexes so reruns are safe
- Validation model:
  - PASS/FAIL is based on missing required names only (extra indexes/constraints are informational)
  - parser compatibility note: if Neo4j rejects `SHOW` composition, use:
    - `Neo4j/schema/08_core_pipeline_validation_runner.cypher` for browser-safe inventories
    - `python Neo4j/schema/08_core_pipeline_validation_runner.py` for authoritative PASS/FAIL

## Core Pipeline Pilot Seed (verified 2026-02-14)

- Added minimal non-temporal pilot seed:
  - `Neo4j/schema/09_core_pipeline_pilot_seed.cypher`
  - `Neo4j/schema/10_core_pipeline_pilot_verify.cypher`
- Pilot cluster includes:
  - `SubjectConcept` (`subj_roman_republic_001`)
  - `Agent` (`agent_roman_republic_v1`)
  - `Claim` (`claim_roman_republic_end_27bce_001`)
  - `RetrievalContext`, `AnalysisRun`, `Facet`, `FacetAssessment`
- Seeded edges:
  - `OWNS_DOMAIN`, `MADE_CLAIM`, `SUBJECT_OF`, `USED_CONTEXT`,
    `HAS_ANALYSIS_RUN`, `HAS_FACET_ASSESSMENT`, `ASSESSES_FACET`, `EVALUATED_BY`
- Compatibility adjustment applied:
  - use `toString(datetime())` (not `datetime().toString()`) for this Neo4j parser/version.

## Event-Period Claim Pilot (verified 2026-02-14)

- Added concrete entity-grounded pilot:
  - `Neo4j/schema/11_event_period_claim_seed.cypher`
  - `Neo4j/schema/12_event_period_claim_verify.cypher`
- Seeded entities:
  - `Period`: Roman Republic (`Q17167`)
  - `Event`: Battle of Actium (`Q193304`)
  - `Place`: Actium (`Q41747`)
- Seeded second claim flow:
  - `claim_actium_in_republic_31bce_001`
  - retrieval: `retr_actium_q193304_001`
  - analysis run: `run_actium_001`
  - facet assessment: `fa_actium_mil_001`
- Added parser hardening for script execution:
  - `Neo4j/schema/run_cypher_file.py` now splits statements on semicolons only when outside quoted strings.

## Claim Label Enforcement (verified 2026-02-14)

- Core schema now requires `Claim.label`:
  - `Neo4j/schema/07_core_pipeline_schema.cypher`
  - constraint: `claim_has_label`
  - index: `claim_label_index`
- Validator updated for new requirement:
  - `Neo4j/schema/08_core_pipeline_validation_runner.py`
- Backfill script added:
  - `Neo4j/schema/13_claim_label_backfill.cypher`
- Current pilot claim labels:
  - `claim_roman_republic_end_27bce_001` -> `Roman Republic Ended in 27 BCE`
  - `claim_actium_in_republic_31bce_001` -> `Battle of Actium in Roman Republic (31 BCE)`

## Claim Promotion Pilot (verified 2026-02-14)

- Added promotion scripts:
  - `Neo4j/schema/14_claim_promotion_seed.cypher`
  - `Neo4j/schema/15_claim_promotion_verify.cypher`
- Promoted claim:
  - `claim_actium_in_republic_31bce_001` -> `status=validated`, `promoted=true`
- Canonical/provenance wiring verified:
  - `(:Event {evt_battle_of_actium_q193304})-[:OCCURRED_DURING]->(:Period {prd_roman_republic_q17167})`
  - `Event-[:SUPPORTED_BY]->Claim` count = 1
  - `Period-[:SUPPORTED_BY]->Claim` count = 1

## Backlink Discovery Mode Upgrade (verified 2026-02-14)

- `scripts/tools/wikidata_backlink_harvest.py` now supports:
  - `--mode production` (default constrained behavior)
  - `--mode discovery` (expanded budgets + broader property surface)
- New mode-aware defaults:
  - production: `sparql_limit=500`, `max_sources_per_seed=200`, `max_new_nodes_per_seed=100`
  - discovery: `sparql_limit=2000`, `max_sources_per_seed=1000`, `max_new_nodes_per_seed=500`
- New class gate control:
  - `--class-allowlist-mode {auto,schema,disabled}`
  - `auto` resolves to `disabled` in discovery and `schema` in production
- Discovery run verified on `Q1048`:
  - report: `JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json`
  - includes `mode: discovery` and `class_allowlist_mode: disabled`

## Q17167 Critical Test (verified 2026-02-14)

Objective completed:
- Generate a claim-rich subgraph proposal for `Q17167` using direct statements + backlinks.

Pipeline executed:
- Direct statements export:
  - `JSON/wikidata/statements/Q17167_statements_full.json`
- Direct datatype profile:
  - `JSON/wikidata/statements/Q17167_statement_datatype_profile_summary.json`
  - `JSON/wikidata/statements/Q17167_statement_datatype_profile_by_property.csv`
  - `JSON/wikidata/statements/Q17167_statement_datatype_profile_datatype_pairs.csv`
- Discovery backlink harvest:
  - `JSON/wikidata/backlinks/Q17167_backlink_harvest_report.json`
- Backlink accepted profile:
  - `JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_summary.json`
  - `JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_by_entity.csv`
  - `JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_pair_counts.csv`

New generator capability:
- `scripts/tools/wikidata_generate_claim_subgraph_proposal.py`
  - merges direct claims + accepted backlinks
  - maps predicate PIDs to canonical relationship types via registry
  - emits machine + human artifacts:
    - `JSON/wikidata/proposals/Q17167_claim_subgraph_proposal.json`
    - `JSON/wikidata/proposals/Q17167_claim_subgraph_proposal.md`

Q17167 proposal snapshot:
- nodes: `178`
- relationship claims: `197`
  - direct: `39`
  - backlink: `158`
- attribute claims: `41`
- backlink gate status: `pass`

## Republic Agent SubjectConcept Seed Pack (verified 2026-02-14)

- Added implementation-ready seed files for Republic-agent domain concepts:
  - `JSON/wikidata/proposals/Q17167_republic_agent_subject_concepts.csv`
  - `JSON/wikidata/proposals/Q17167_republic_agent_subject_concepts.json`
- Pack contents:
  - 17 proposed `SubjectConcept` nodes
  - `discipline=true`, primary facet, primary confidence
  - multi-facet confidence vectors (JSON)
  - parent hierarchy using `BROADER_THAN` relationship proposals

## Federation Datatype Work (verified 2026-02-13)

### New capability
- Full statement export and datatype profiling are now in place for federation design.

Artifacts:
- Full statements export: `JSON/wikidata/statements/Q1048_statements_full.json`
- 100-row flattened sample: `JSON/wikidata/statements/Q1048_statements_sample_100.csv`
- Datatype profile summary: `JSON/wikidata/statements/Q1048_statement_datatype_profile_summary.json`
- Datatype profile by property: `JSON/wikidata/statements/Q1048_statement_datatype_profile_by_property.csv`
- Datatype/value-type pairs: `JSON/wikidata/statements/Q1048_statement_datatype_profile_datatype_pairs.csv`

Scripts:
- `scripts/tools/wikidata_fetch_all_statements.py`
- `scripts/tools/wikidata_sample_statement_records.py`
- `scripts/tools/wikidata_statement_datatype_profile.py`

Spec:
- `md/Architecture/Wikidata_Statement_Datatype_Ingestion_Spec.md`

Observed Q1048 profile baseline:
- statements: 451
- properties: 324
- datatypes: 7
- value types: 5
- qualifier coverage: 23.28%
- reference coverage: 24.17%

## Backlink Policy Refinement (verified 2026-02-13)

- Canonical backlink policy was cleaned and tightened:
  - `Neo4j/FEDERATION_BACKLINK_STRATEGY.md`
- Key lock-ins:
  - Backlink source is semantic reverse triples, not MediaWiki page `linkshere`.
  - `datatype` + `value_type` are mandatory routing gates, not optional metadata.
  - Stop conditions are required (`max_depth`, per-seed budgets, class/property allowlists).
  - Backlink candidates must pass the same datatype profiling workflow as direct statements.

## Backlink Harvester Implementation (verified 2026-02-13)

- New script:
  - `scripts/tools/wikidata_backlink_harvest.py`
- Report output location:
  - `JSON/wikidata/backlinks/`
- Sample run artifact:
  - `JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json`

Q1048 sample (bounded run):
- backlink rows: 87
- candidate sources considered: 25
- accepted: 10
- unresolved class rate: 20.00% (gate pass at default 20%)
- unsupported datatype pair rate: 0.00% (gate pass)
- overall status: `pass`
- dispatcher route metrics now emitted in report (`route_counts`, `quarantine_reasons`)
- frontier metrics now emitted (`frontier_eligible`, `frontier_excluded`, per-entity `frontier_eligible`)
- consolidated architecture updated:
  - `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
  - new normative section `8.6 Federation Dispatcher and Backlink Control Plane`
  - Appendix K updated with dispatcher/backlink operational contract

## Backlink Profiler Implementation (verified 2026-02-13)

- New script:
  - `scripts/tools/wikidata_backlink_profile.py`
- Profiling artifacts (Q1048 accepted candidates):
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_summary.json`
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_by_entity.csv`
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_pair_counts.csv`

Q1048 profile sample:
- requested QIDs: 10
- resolved entities: 10
- statements: 342
- unsupported pair rate: 0.00%
- overall status: `pass`

## Query Executor Agent + Claim Pipeline (verified 2026-02-14)

### New Agent Implementation
- Added production-ready Query Executor Agent:
  - `scripts/agents/query_executor_agent_test.py` (391 lines)
  - ChatGPT-powered with dynamic schema discovery
  - Integrated claim submission via ClaimIngestionPipeline
  - 5 CLI modes: test, claims, interactive, single query, default

### Claim Ingestion Pipeline
- New pipeline:
  - `scripts/tools/claim_ingestion_pipeline.py` (460 lines)
  - Entry point: `ingest_claim(entity_id, relationship_type, target_id, confidence, ...)`
  - Returns: `{status: 'created'|'promoted'|'error', claim_id, cipher, promoted}`
  - Workflow: Validate -> Hash -> Create -> Link -> Promote (if confidence >= 0.90)
  - Intermediary nodes: RetrievalContext, AnalysisRun, FacetAssessment
  - Traceability: SUPPORTED_BY edges + canonical relationship promotion

### Facet Integration
- Agent now aware of 16-facet registry from `Facets/facet_registry_master.json`:
  - archaeological, artistic, cultural, demographic, diplomatic, economic
  - environmental, geographic, intellectual, linguistic, military, political
  - religious, scientific, social, technological
- Facet registry status: ACTIVE (16 facets, not 17 as previously estimated)
- Claims include `facet` parameter for FacetAssessment node creation
- Agent prompt updated with facet reference patterns

### Documentation Package
- System prompt: `md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md` (400+ lines, with facet patterns)
- Agent README: `scripts/agents/README.md` (400+ lines)
- Quickstart: `scripts/agents/QUERY_EXECUTOR_QUICKSTART.md` (300+ lines)
- Quick reference: `QUERY_EXECUTOR_QUICK_REFERENCE.md`
- Implementation summary: `Key Files/2026-02-14 Query Executor Implementation.md`

### Execution Model
- Agent layer: Direct neo4j-driver + OpenAI API (no MCP overhead for agents)
- Pipeline layer: Python validation + transactional Neo4j writes
- Separation: ChatGPT handles query/format, pipeline handles validation/promotion
- Status: ✅ Syntax validated, ready for testing
- Deployment: Files staged for git commit (awaiting push)

## Recommended Next Steps
- If rebuilding backbone from scratch:
  1. Run `python scripts/backbone/temporal/genYearsToNeo.py --start -2000 --end 2025`
  2. Run `python scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py --apply`
- Verify with:
  - `python Python/check_year_range.py`
  - graph checks for orphan years (`Year` without `PART_OF -> Decade`).
- Test Query Executor Agent:
  1. Set `NEO4J_PASSWORD` and `OPENAI_API_KEY` environment variables
  2. Run: `python scripts/agents/query_executor_agent_test.py test`
  3. Run: `python scripts/agents/query_executor_agent_test.py claims`
  4. Verify claim nodes in graph: `MATCH (c:Claim) RETURN c`
