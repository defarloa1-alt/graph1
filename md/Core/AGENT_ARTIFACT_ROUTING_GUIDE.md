# Agent Artifact Routing Guide

Status: generated first-pass routing index from active canonical folders.

- Generated: `2026-02-18`
- Total artifacts indexed: `271`
- Source registry: `CSV/registry/project_artifact_registry.csv`
- Overrides: `JSON/registry/project_artifact_registry_overrides.json`
- Review queue: `CSV/registry/project_artifact_registry_review_queue.csv`
- Decisions log: `md/Core/PROJECT_ARTIFACT_REGISTRY_DECISIONS.md`
- Rebuild command: `python scripts/tools/build_project_artifact_registry.py`

## Priority Entry Points

- `Neo4j/schema/run_qid_pipeline.py`
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/claim_confidence_policy_engine.py`
- `scripts/tools/policy_subgraph_loader.py`
- `scripts/tools/kko_mapping_proposal_loader.py`
- `md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md`
- `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

## Routing by Task Tag

### `agent_routing`
- `Facets/BIOGRAPHIC_SFA_ONTOLOGY_METHODOLOGY.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `Facets/CANONICAL_RELATIONSHIP_TYPES.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `Facets/COMMUNICATION_SFA_ONTOLOGY_METHODOLOGY.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `Facets/FACETS_CONSOLIDATION_2026-02-12.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `Facets/facet assessment - future.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`

### `claims`
- `JSON/policy/claim_confidence_policy_v1.json` | type=`policy` | scope=`read_only` | gates=`none`
- `Neo4j/schema/11_event_period_claim_seed.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/12_event_period_claim_verify.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/13_claim_label_backfill.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/14_claim_promotion_seed.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/15_claim_promotion_verify.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`

### `federation`
- `CSV/action_structure_wikidata_mapping.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `Facets/facet_federation_matrix.json` | type=`registry` | scope=`read_only` | gates=`none`
- `Relationships/wikidata_p_api_candidates_2026-02-13.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `Relationships/wikidata_p_api_candidates_medium_rank1_2026-02-13.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `Relationships/wikidata_p_catalog_candidates_2026-02-13.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `Relationships/wikidata_p_mapping_review_queue_2026-02-13.csv` | type=`registry` | scope=`read_only` | gates=`none`

### `general`
- `CSV/project_p_values_canonical.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `CSV/registry/project_artifact_registry.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `CSV/registry/project_artifact_registry_review_queue.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `md/Core/Discipline.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `md/Core/PROJECT_ARTIFACT_REGISTRY_DECISIONS.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`

### `geographic`
- `md/Agents/geographic_extraction.md` | type=`prompt_or_agent_spec` | scope=`read_only` | gates=`none`
- `scripts/backbone/geographic/download_pleiades_bulk.py` | type=`script` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `scripts/backbone/geographic/import_pleiades_to_neo4j.py` | type=`script` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `scripts/backbone/geographic/pleiades_bulk_ingest_roman_republic.py` | type=`script` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `scripts/backbone/geographic/verify_pleiades_import.py` | type=`script` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `scripts/backbone/temporal/fetch_tgn_places_sparql.py` | type=`script` | scope=`read_only` | gates=`none`

### `kbpedia`
- `CSV/kko_chrystallum_crosswalk.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `JSON/kbpedia/proposals/kko_map_smoke_20260218_b_kko_mapping_proposal.json` | type=`registry` | scope=`read_only` | gates=`none`
- `JSON/kbpedia/proposals/kko_map_smoke_20260218_b_kko_mapping_proposal.md` | type=`registry` | scope=`read_only` | gates=`none`
- `JSON/kbpedia/proposals/kko_map_smoke_20260218_kko_mapping_proposal.json` | type=`registry` | scope=`read_only` | gates=`none`
- `JSON/kbpedia/proposals/kko_map_smoke_20260218_kko_mapping_proposal.md` | type=`registry` | scope=`read_only` | gates=`none`
- `md/Architecture/ADR-003-KBpedia-Role-and-Boundaries.md` | type=`adr` | scope=`read_only` | gates=`none`

### `policy`
- `JSON/policy/claim_confidence_policy_v1.json` | type=`policy` | scope=`read_only` | gates=`none`
- `Neo4j/schema/17_policy_decision_subgraph_schema.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md` | type=`adr` | scope=`read_only` | gates=`none`
- `scripts/tools/claim_confidence_policy_engine.py` | type=`script` | scope=`read_only` | gates=`none`
- `scripts/tools/policy_subgraph_loader.py` | type=`script` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`

### `relationships`
- `Facets/CANONICAL_RELATIONSHIP_TYPES.md` | type=`architecture_doc` | scope=`read_only` | gates=`none`
- `Relationships/relationship_facet_baselines.json` | type=`registry` | scope=`read_only` | gates=`none`
- `Relationships/relationship_type_p_suggestions_exact_alias_2026-02-13.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `Relationships/relationship_type_p_suggestions_relaxed_alias_2026-02-13.csv` | type=`registry` | scope=`read_only` | gates=`none`
- `Relationships/relationship_types_diagram.png` | type=`diagram` | scope=`read_only` | gates=`none`
- `Relationships/relationship_types_registry_master.csv` | type=`registry` | scope=`read_only` | gates=`none`

### `schema`
- `Neo4j/schema/01_schema_constraints.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/01_schema_constraints_neo5_compatible.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/02_schema_indexes.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/03_schema_initialization.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/03_schema_initialization_simple.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/04_temporal_bbox_queries.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`

### `sysml`
- `scripts/tools/validate_sysml_contracts.py` | type=`script` | scope=`read_only` | gates=`none`
- `sysml/README.md` | type=`sysml_bdd` | scope=`read_only` | gates=`none`
- `sysml/claim_scope_validation_in.json` | type=`sysml_contract` | scope=`read_only` | gates=`none`
- `sysml/dispatcher_decision_out.json` | type=`sysml_contract` | scope=`read_only` | gates=`none`
- `sysml/error_envelope.json` | type=`sysml_contract` | scope=`read_only` | gates=`none`
- `sysml/observability_event_in.json` | type=`sysml_contract` | scope=`read_only` | gates=`none`

### `temporal`
- `Neo4j/schema/04_temporal_bbox_queries.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/05_temporal_hierarchy_levels.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/11_event_period_claim_seed.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Neo4j/schema/12_event_period_claim_verify.cypher` | type=`schema_cypher` | scope=`canonical_write` | gates=`dispatcher_gate|policy_gate|U->Pi->Commit`
- `Facets/periods_with_facets.json` | type=`registry` | scope=`read_only` | gates=`none`
- `md/Agents/temporal_extraction.md` | type=`prompt_or_agent_spec` | scope=`read_only` | gates=`none`

## Routing by Owner Role

### `Pi`
- `JSON/policy/claim_confidence_policy_v1.json` | type=`policy` | tags=`claims;policy`
- `Neo4j/schema/01_schema_constraints.cypher` | type=`schema_cypher` | tags=`schema`
- `Neo4j/schema/01_schema_constraints_neo5_compatible.cypher` | type=`schema_cypher` | tags=`schema`
- `Neo4j/schema/02_schema_indexes.cypher` | type=`schema_cypher` | tags=`schema`
- `Neo4j/schema/03_schema_initialization.cypher` | type=`schema_cypher` | tags=`schema`
- `Neo4j/schema/03_schema_initialization_simple.cypher` | type=`schema_cypher` | tags=`schema`

### `Platform`
- `CSV/action_structure_wikidata_mapping.csv` | type=`registry` | tags=`federation`
- `CSV/kko_chrystallum_crosswalk.csv` | type=`registry` | tags=`kbpedia`
- `CSV/project_p_values_canonical.csv` | type=`registry` | tags=`general`
- `CSV/registry/project_artifact_registry.csv` | type=`registry` | tags=`general`
- `CSV/registry/project_artifact_registry_review_queue.csv` | type=`registry` | tags=`general`
- `Facets/BIOGRAPHIC_SFA_ONTOLOGY_METHODOLOGY.md` | type=`architecture_doc` | tags=`agent_routing`

### `SCA`
- `md/Agents/CHATGPT_INSTRUCTIONS_FINAL.md` | type=`prompt_or_agent_spec` | tags=`agent_routing`
- `md/Agents/CHATGPT_QUICK_UPLOAD_CHECKLIST.md` | type=`prompt_or_agent_spec` | tags=`agent_routing`
- `md/Agents/CHATGPT_UPLOAD_PACKAGE.md` | type=`prompt_or_agent_spec` | tags=`agent_routing`
- `md/Agents/GRAPH_INSIGHT_SUMMARY.md` | type=`prompt_or_agent_spec` | tags=`agent_routing`
- `md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md` | type=`prompt_or_agent_spec` | tags=`agent_routing`
- `md/Agents/QUERY_EXECUTOR_AGENT_PROMPT_COMPACT.md` | type=`prompt_or_agent_spec` | tags=`agent_routing`

### `SFA`
- `scripts/backbone/geographic/download_pleiades_bulk.py` | type=`script` | tags=`geographic`
- `scripts/backbone/geographic/import_pleiades_to_neo4j.py` | type=`script` | tags=`geographic`
- `scripts/backbone/geographic/pleiades_bulk_ingest_roman_republic.py` | type=`script` | tags=`geographic`
- `scripts/backbone/geographic/verify_pleiades_import.py` | type=`script` | tags=`geographic`
- `scripts/backbone/subject/create_subject_nodes.py` | type=`script` | tags=`general`
- `scripts/backbone/subject/link_entities_to_subjects.py` | type=`script` | tags=`general`

## Guardrails

- Canonical write paths must follow `U -> Pi -> Commit`.
- Proposal-only artifacts do not mutate canonical graph directly.
- Use `md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md` for executable crosswalk anchors.
