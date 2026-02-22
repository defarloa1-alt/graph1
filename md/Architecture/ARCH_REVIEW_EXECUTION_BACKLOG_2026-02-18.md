# Architecture Review Execution Backlog (2026-02-18)

Status: actionable backlog derived from `ARCH_REVIEW_RESPONSE_2026-02-18.md`.

## Status Legend
- `pending`: not started
- `in_progress`: active work
- `complete`: acceptance criteria met

## Status Summary
- `complete`: 13
- `in_progress`: 0
- `pending`: 6

## Execution Rules
- Preserve `U -> Pi -> Commit` for any canonical mutation path.
- Prefer deterministic validation before advanced ML layers.
- Treat ML/GNN tracks as additive; do not block core federation/claims pipelines.

## Phase 1 (0-8 weeks): Baseline Capability Uplift

| ID | Track | Task | Status | Target Artifacts | Acceptance Criteria |
|---|---|---|---|---|---|
| ARB-EMB-001 | Embeddings | Define embedding scope and candidate node sets (`Human`, `Event`, `Place`, `SubjectConcept`) | `complete` | `md/Architecture/EMBEDDING_BASELINE_SCOPE_2026-02-18.md` | Scope doc approved; node cohort and refresh cadence documented. |
| ARB-EMB-002 | Embeddings | Add vector pilot script scaffold and output contract | `complete` | `scripts/ml/train_kg_embeddings.py` (new), `md/Core/AGENT_ARTIFACT_ROUTING_GUIDE.md` (entrypoint) | Script runs with `--help`; emits deterministic metadata header for a pilot run artifact. |
| ARB-EMB-003 | Embeddings | Define vector index integration plan (Neo4j) | `complete` | `md/Architecture/EMBEDDING_VECTOR_INDEX_INTEGRATION_PLAN_2026-02-18.md` | Design includes index name, dimensions, similarity metric, and backfill policy. |
| ARB-REAS-001 | Reasoning | Add SHACL/RDFS-lite validation scope doc | `complete` | `md/Architecture/SHACL_RDFS_LITE_SCOPE_2026-02-18.md` | Lists constraints to validate first (identity, temporal bounds, authority consistency). |
| ARB-REAS-002 | Reasoning | Implement first validator runner scaffold | `complete` | `scripts/tools/validate_semantic_constraints.py` (new) | `--help` works; runner can execute at least one deterministic check and emit JSON report. |
| ARB-LOD-001 | LOD | Define RDF export baseline and format targets | `complete` | `md/Architecture/LOD_BASELINE_SPEC_2026-02-18.md` | Target formats and minimal dataset scope approved (`ttl`, optional `nt`). |
| ARB-LOD-002 | LOD | Add VoID dataset descriptor draft | `complete` | `md/Architecture/VOID_DATASET_DRAFT_2026-02-18.ttl` (new) | Draft validates syntactically and references canonical dataset metadata. |
| ARB-SCHEMA-001 | Schema QA | Add migration regression harness design | `complete` | `md/Architecture/SCHEMA_MIGRATION_REGRESSION_HARNESS_DESIGN_2026-02-18.md` | Defines how schema scripts are tested pre/post with fixed assertions. |

## Phase 2 (8-16 weeks): Federation and Semantic Expansion

| ID | Track | Task | Status | Target Artifacts | Acceptance Criteria |
|---|---|---|---|---|---|
| ARB-FED-001 | Federation | Add bidirectional federation query design for priority authorities | `complete` | `md/Architecture/BIDIRECTIONAL_FEDERATION_QUERY_DESIGN_2026-02-18.md` | Includes query path, caching policy, timeout/fallback behavior. |
| ARB-ER-001 | Entity Resolution | Add embedding-assisted disambiguation policy | `complete` | `md/Architecture/EMBEDDING_ASSISTED_DISAMBIGUATION_POLICY_2026-02-18.md` | Specifies when ML suggestions are advisory vs promotable. |
| ARB-SCHEMA-002 | Schema QA | Implement migration regression runner | `complete` | `scripts/tools/schema_migration_regression.py` (new), `Neo4j/schema/schema_migration_plan_v1.json` (new) | Runner executes against selected schema sequence and reports pass/fail matrix. |

## Phase 3 (16+ weeks): Research-Grade Enhancements

| ID | Track | Task | Status | Target Artifacts | Acceptance Criteria |
|---|---|---|---|---|---|
| ARB-GNN-001 | GNN | Define GNN experiment protocol for link prediction and plausibility ranking | `complete` | `md/Architecture/GNN_EXPERIMENT_PROTOCOL_2026-02-18.md` | Protocol includes baseline models, train/test split strategy, and metrics. |
| ARB-GNN-002 | GNN | Add experiment runner scaffold (non-production) | `complete` | `scripts/ml/link_prediction_gnn.py` (new), `JSON/reports/gnn_experiments/gnn_experiment_smoke_2026-02-18.json` | Script scaffold runs and emits experiment metadata without production writes. |

## Phase 2.5 (next): Federation Triangulation + Meta-Subgraph Hardening

| ID | Track | Task | Status | Target Artifacts | Acceptance Criteria |
|---|---|---|---|---|---|
| ARB-FED-002 | Federation | Define triangulated federation-score policy (`Wikidata+Pleiades+GeoNames+Temporal+Geo`) | `pending` | `md/Architecture/FEDERATION_GOLDEN_PATTERN_TODO_2026-02-19.md`, `md/Architecture/FEDERATION_SCORE_MODEL_2026-02-19.md` | `federation_score`/`federation_state` policy is explicit and testable. |
| ARB-FED-003 | Federation | Upgrade assignment logic from stars to `federation_score` + pattern states | `pending` | `scripts/backbone/geographic/build_place_type_hierarchy.py`, `scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py` | Produced outputs include deterministic `federation_score`, `federation_state`, and `federation_pattern_id`. |
| ARB-FED-004 | Federation | Model Chrystallum federation meta-subgraph rooted at `Q124542039` concept | `pending` | `md/Architecture/FEDERATION_GOLDEN_PATTERN_TODO_2026-02-19.md`, `Neo4j/schema/20_federation_meta_subgraph.cypher` (new) | Subgraph seeded with platform root, federation hub, source/property/IO contract nodes. |
| ARB-GEO-001 | Geo Ontology | Add lightweight GeoNames superclass overlay for feature codes | `pending` | `md/Architecture/FEDERATION_GOLDEN_PATTERN_TODO_2026-02-19.md`, mapping CSV/script updates | All GeoNames feature codes map to one lightweight superclass. |
| ARB-FED-005 | Federation QA | Add deterministic federation cipher key contract for what+where+when tests | `pending` | `md/Architecture/FEDERATION_GOLDEN_PATTERN_TODO_2026-02-19.md`, script output columns | Key is reproducible and queryable in CSV and graph outputs. |
| ARB-FED-006 | Federation QA | Add validation query pack for triangulation coverage and federation-score outcomes | `pending` | `md/Architecture/FEDERATION_GOLDEN_PATTERN_TODO_2026-02-19.md`, `md/Architecture/FEDERATION_SCORE_MODEL_2026-02-19.md`, QA query artifact (new) | One-command or one-query coverage report for state-band counts and base/triangulated pattern coverage. |

## Immediate Start Order
1. `ARB-FED-002`
2. `ARB-FED-003`
3. `ARB-FED-004`
4. `ARB-GEO-001`
5. `ARB-FED-005`
6. `ARB-FED-006`

## Exit Criteria for "Review Response Implemented"
- Phase 1 tasks have executable scaffolds or approved designs with acceptance checks.
- Artifact registry includes all new files with correct owner/scope/gate metadata.
- Review queue remains at 0 open items after regeneration.

## Progress Update (2026-02-18)
- `ARB-FED-003` support path added: `scripts/backbone/geographic/build_geonames_wikidata_bridge.py` now builds GeoNames->Wikidata (`P1566`) and merged `Pleiades+GeoNames+Wikidata+TGN` crosswalk artifacts with terminal progress output.
- `ARB-FED-002`: todo scope drafted (`md/Architecture/FEDERATION_GOLDEN_PATTERN_TODO_2026-02-19.md`) and upgraded with federation-score model (`md/Architecture/FEDERATION_SCORE_MODEL_2026-02-19.md`).
- `ARB-LOD-001`: draft complete (`md/Architecture/LOD_BASELINE_SPEC_2026-02-18.md`).
- `ARB-LOD-002`: draft complete (`md/Architecture/VOID_DATASET_DRAFT_2026-02-18.ttl`) and parser-validated (`rdflib` parse succeeded, 28 triples).
- `ARB-EMB-001`: complete (`md/Architecture/EMBEDDING_BASELINE_SCOPE_2026-02-18.md`).
- `ARB-REAS-001`: complete (`md/Architecture/SHACL_RDFS_LITE_SCOPE_2026-02-18.md`).
- `ARB-EMB-002`: complete (`scripts/ml/train_kg_embeddings.py`) with deterministic pilot metadata contract.
- `ARB-REAS-002`: complete (`scripts/tools/validate_semantic_constraints.py`) with deterministic JSON check report.
- `ARB-SCHEMA-001`: complete (`md/Architecture/SCHEMA_MIGRATION_REGRESSION_HARNESS_DESIGN_2026-02-18.md`) with pre/post assertion plan.
- `ARB-SCHEMA-002`: complete (`scripts/tools/schema_migration_regression.py`) with deterministic dry-run pass/fail matrix report.
- `ARB-EMB-003`: complete (`md/Architecture/EMBEDDING_VECTOR_INDEX_INTEGRATION_PLAN_2026-02-18.md`) with index profile + backfill policy.
- `ARB-FED-001`: complete (`md/Architecture/BIDIRECTIONAL_FEDERATION_QUERY_DESIGN_2026-02-18.md`) with cache/timeout/fallback policy.
- `ARB-ER-001`: complete (`md/Architecture/EMBEDDING_ASSISTED_DISAMBIGUATION_POLICY_2026-02-18.md`) with advisory vs promotable boundaries.
- `ARB-GNN-001`: complete (`md/Architecture/GNN_EXPERIMENT_PROTOCOL_2026-02-18.md`) as research-only protocol baseline.
- `ARB-GNN-002`: complete (`scripts/ml/link_prediction_gnn.py`) with deterministic non-production experiment metadata artifact.
