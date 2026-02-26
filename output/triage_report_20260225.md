# Chrystallum Project Triage Report

**Date:** 2026-02-25  
**Reference:** DECISIONS.md D-017 (Folder Organization)  
**Status:** Classification + execution — COMPLETE

**Summary:**
- 19 files → Archive/2026-02-25_session_docs/
- 53 files → docs/architecture/
- 3 files → docs/federations/
- 5 files → docs/agents/
- 1 file → docs/examples/
- 86 files → scripts/legacy/
- 1 file → scripts/tools/ (canonicalize_edges.py)
- 9 files → Cypher/
- 9 misc → Archive/

---

## Root KEEP (per D-017)

| File | Rationale |
|------|-----------|
| KANBAN.md | Root discipline |
| REQUIREMENTS.md | Root discipline |
| DECISIONS.md | Root discipline |
| README.md | Root discipline |
| START_HERE.txt | Root discipline |
| AGENTS.md | Active agent guidance |
| .env | Config |
| requirements.txt | Dependencies |
| .gitignore | Standard |
| .gitattributes | Standard |
| Procfile | Railway deploy |
| railpack.json | Railway deploy |
| config.py | Config |
| config.py.example | Config template |

---

## ARCHIVE → Archive/

Deprecated, superseded, or session artifacts.

| File |
|------|
| AI_CONTEXT.md |
| chattofile.md |
| cipher-talk.md |
| SCA_PROCESS_NARRATIVE.md |
| SCA_BOOTSTRAP_CONSOLIDATED.md |
| SCA_CANDIDATE_BUCKETS.md |
| GRAPH_ARCHITECT_COMPLETE_SESSION_SUMMARY.md |
| GRAPH_ARCHITECT_FINAL_SESSION_SUMMARY.md |
| GRAPH_ARCHITECT_SESSION_COMPLETE.md |
| GRAPH_ARCHITECT_DELIVERABLES_2026-02-22.md |
| REBUILD_COMPLETE_SUMMARY.md |
| FINAL_SESSION_DELIVERABLES.md |
| FINAL_SESSION_DELIVERABLES_PROPERTY_MAPPING.md |
| SESSION_SUMMARY_PROPERTY_MAPPING.md |
| SESSION_SUMMARY_SUBJECT_CONCEPT_AGENTS.md |
| SESSION_CONTEXT_FOR_QA.md |
| deep-research-report.md |
| D031_MCP_SERVER_SPEC (1).md |
| cursor_graph_architect_agent_role_defin.md |

---

## EXTRACT → docs/architecture/

Architecture and analysis docs.

| File |
|------|
| ENTITY_CIPHER_FOR_VERTEX_JUMPS.md |
| DMN_EXTRACTION_AUDIT.md |
| ARCHITECTURE_ISSUE_HARDCODED_RELATIONSHIPS.md |
| NODE_ALIGNMENT_ISSUES_2026-02-19.md |
| PLACE_MODEL_ANALYSIS.md |
| PROPERTY_DOMAIN_UTILITY_ANALYSIS.md |
| GEOGRAPHIC_AND_PERIODO_ANALYSIS.md |
| ROMAN_REPUBLIC_TAXONOMY_ANALYSIS.md |
| ROMAN_REPUBLIC_2HOP_TAXONOMY.md |
| HISTORICAL_PERIOD_BACKLINKS_ANALYSIS.md |
| COMMONS_CATEGORY_INDEX_ANALYSIS.md |
| BA_WIKIDATA_PID_MODEL_BUSINESS_FEATURES.md |
| CHRYSTALLUM_SYSTEM_VISUALIZATION_2026-02-19.md |
| 89_HISTORICAL_PERIODS_COMPLETE_CHART.md |
| COMPLETE_3HOP_TAXONOMY_ANALYSIS.md |
| COMPREHENSIVE_NODE_TYPES_2026-02-19.md |
| SYSTEM_SUBGRAPH_ARCHITECTURE_2026-02-19.md |
| BA_SELF_DESCRIBING_SYSTEM_ANALYSIS.md |
| 12_FAILED_PERIODS_TEMPORAL_DATA.md |
| 3HOP_VISUAL_SUMMARY.md |
| 5HOP_COMPLETE_TAXONOMY.md |
| 5HOP_EXPLORATION_COMPLETENESS.md |
| HISTORICAL_PERIODS_TREE_CHART.md |
| PERIODO_PLEIADES_COMPARISON.md |
| TIME_PERIOD_DEFINITION.md |
| MULTI_FACTOR_PROPERTY_ROUTING.md |
| RELIGIOUS_FACET_BACKLINKS.md |
| P2184_HISTORY_OF_TOPIC_DISCOVERY.md |
| Q17167_10_FACETS_CONFIRMED_WITH_LABELS.md |
| Q17167_FACET_MAPPING.md |
| ROMAN_REPUBLIC_Q17167_COMPLETE_PROPERTIES.md |
| COMPLETE_PROPERTY_OUTLINE_SUMMARY.md |
| COMPLETE_SUCCESSION_CHAIN.md |
| COMPREHENSIVE_DISCOVERY_SUMMARY.md |
| PROPERTY_MAPPING_ANALYSIS.md |
| PROPERTY_MAPPING_IMPACT.md |
| TAXONOMY_RELATIONSHIPS_TABLE.md |
| SCA_FILTERED_TREE_WITH_AUTHORITIES.md |
| SCA_FILTERS_COMPLETE_REVIEW.md |
| IMMEDIATE_SUBJECT_CONCEPTS_AND_SFAS.md |
| SUBJECT_CONCEPT_AGENTS_BUILD_SUMMARY.md |
| 2-16-26-Day in the life of a facet.md |
| CSV_ANALYSIS_READY.md |
| INTEGRATION_AGENT_PLAN.md |
| NEO4J_IMPORTER_PLAN.md |
| DATA_DICTIONARY.md |
| BACKLINKS_EXTRACTION_GUIDE.md |
| DEV_INSTRUCTIONS_WIKIDATA_COMPREHENSIVE_IMPORT.md |
| PM_PLAN_REVISED_AI_DRIVEN_2026-02-20.md |
| REQUIREMENTS_ANALYST_INTRODUCTION.md |
| QA_HANDOFF_NEO4J_TESTING.md |
| QA_QUICK_START.md |
| QA_TEST_REPORT.md |

---

## EXTRACT → docs/federations/

| File |
|------|
| FEDERATION_MAPPER_AGENT.md |
| IMPORT_PROPERTY_MAPPINGS_GUIDE.md |
| PROPERTY_FACET_MAPPER_GUIDE.md |

---

## EXTRACT → docs/agents/

| File |
|------|
| AGENT_REFERENCE_FILE_PATHS.md |
| MCP_SETUP_INSTRUCTIONS.md |
| ENABLE_NEO4J_MCP.md |
| CURSOR_MCP_QUICK_START.md |
| SUBJECT_CONCEPT_AGENTS_QUICK_REF.md |

---

## EXTRACT → scripts/legacy/

Root-level Python scripts (verify before use).

| File |
|------|
| add_constraints.py |
| add_bbox_to_places.py |
| analyze_backlink_profiles.py |
| analyze_checkpoint_claims.py |
| analyze_entity_completeness.py |
| audit_neo4j_schema_cleanup.py |
| audit_relationships_detailed.py |
| audit_schema_vs_spec.py |
| audit_simple.py |
| build_complete_chrystallum_architecture.py |
| build_system_subgraph_step_by_step.py |
| Change_log.py |
| check_facets.py |
| check_labels.py |
| check_neo4j.py |
| check_placename_usage.py |
| check_place_data.py |
| check_property_facet_links.py |
| check_rebuild_status.py |
| check_relationships.py |
| check_schema.py |
| cleanup_non_canonical_nodes.py |
| cleanup_placename_nodes.py |
| convert_csv_to_cypher.py |
| count_entities.py |
| deduplicate_backlinks.py |
| direct_check.py |
| enrich_places_with_wikidata.py |
| execute_ddl_addendum.py |
| explore_meta_detailed.py |
| explore_meta_model.py |
| extract_places_with_qid.py |
| extract_q107649491_backlinks.py |
| extract_wikidata_backlinks.py |
| filter_property_types.py |
| finalize_system_architecture.py |
| final_verification.py |
| fix_duplicates.py |
| fix_place_constraint.py |
| generate_rename_cypher.py |
| get_property_types.py |
| import_all_places.py |
| import_property_mappings_direct.py |
| import_simple_edges_comprehensive.py |
| inspect_neo4j_state.py |
| inspect_placetype_tokens.py |
| llm_resolve_unknown_properties.py |
| manual_llm_resolve.py |
| map_properties_to_facets.py |
| merge_claude_assignments.py |
| perplexity_resolve_properties.py |
| qa_test_suite.py |
| rebuild_simple_structure.py |
| rebuild_system_subgraph_correct.py |
| remove_wikidata_prefix.py |
| replace_indexes_with_constraints.py |
| run_cleanup.py |
| run_federation_import.py |
| sca_clean_labels.py |
| sca_enhanced_with_details.py |
| sca_gradio_fixed.py |
| sca_run_with_progress.py |
| sca_ui_working.py |
| sca_with_checkpoints.py |
| score_all_places.py |
| show_stats.py |
| test_aura_connection.py |
| test_aura_real.py |
| test_neo4j_connection.py |
| test_quote_escaping.py |
| test_wikidata_fetch.py |
| validate_2600_import.py |
| validate_checkpoint_completeness.py |
| validate_database_state.py |
| validate_import.py |
| validate_property_facets_with_backlinks.py |
| verify_and_import.py |
| verify_arch_alignment.py |
| verify_dev_fixes.py |
| verify_placename_properties.py |
| verify_property_import.py |
| verify_property_mappings.py |
| verify_relationships.py |
| verify_req_func_010.py |
| verify_wikidata_enrichment.py |

---

## EXTRACT → scripts/tools/ (active)

| File |
|------|
| canonicalize_edges.py |

---

## EXTRACT → Cypher/ (or Neo4j/)

Root Cypher files.

| File |
|------|
| cleanup_duplicates.cypher |
| complete_ddl.cypher |
| execute_ddl.cypher |
| explore_imported_entities.cypher |
| graph_view_queries.cypher |
| neo4j_queries_graph_overview.cypher |
| property_mapping_test_queries.cypher |
| schema_ddl_to_execute.cypher |
| property_mapping_queries_validated.md |

---

## KEEP at root (batch/setup)

| File |
|------|
| launch_gradio_ui.bat |
| launch_gradio_ui.sh |
| launch_streamlit_ui.bat |
| launch_streamlit_ui.sh |
| run_explore_queries.ps1 |
| run_subj_rr_migration.ps1 |
| setup_aura_connection.bat |
| setup_config.bat |
| setup_config.sh |
| setup_neo4j_mcp.ps1 |
| test_mcp_connection.bat |
| rebuild_chrystallum_fresh.bat |
| SETUP_COMPLETE.bat |

---

## Data/misc — KEEP or Archive

| File | Action |
|------|--------|
| all-collections-list.xlsx | Archive |
| all_relationship_types.txt | Archive |
| contentlist.xls | Archive |
| historical_entity_samples.txt | docs/examples/ |
| historical_entity_type_mapping.json | Keep (data) |
| mcp-config.json | Keep |
| query.csv | Archive |
| query (1).csv | Archive |
| requirements_backlinks.txt | Keep |
| Q1392538, Q2576746, Q2862991 | Archive (stray files) |
| Chrystallum Query Executor - Capabilities Overview.html | Archive |

---

## Post-triage actions

- **run_explore_queries.ps1** — Updated to use `Cypher/explore_imported_entities.cypher`
- **docs/agents/AGENT_REFERENCE_FILE_PATHS.md** — May need path updates for moved scripts
- **Scripts with hardcoded paths** — Grep before running any legacy script
