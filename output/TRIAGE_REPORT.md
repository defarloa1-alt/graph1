# Folder and Document Triage Report

**Date:** 2026-02-25  
**Scope:** output/, docs/, loose markdown in root  
**Rules:** KEEP = actively referenced; ARCHIVE = historical value, move to output/archive/; EXTRACT = content should go to canonical file — flag only, no extraction.

---

## KEEP — Actively Referenced

| File | Rationale |
|------|-----------|
| `output/PROCESS_MODEL_FIRST_CHANGE_COMMUNICATION.md` | Referenced by AGENTS.md First Reads; model-first sequence |
| `output/DMN_EXTRACTION_AUDIT.md` | Source for sysml/DMN_DECISION_TABLES.md; canonical audit of hardcoded values |
| `output/DEV_HANDOFF_ARCHITECTURAL_DECISIONS_2026-02-21.md` | Referenced by user; D-027/D-029 handoff to dev; investigation findings |
| `output/NODE_LABEL_ARCHITECTURE_TABLE.md` | Feeds block catalog; node label verdicts; referenced by NODE_LABEL source line |
| `output/analysis/scoping_advisor_report.md` | Referenced by docs/ADVISOR_HANDOFF_2026-02-25.md as scoping output |
| `output/analysis/property_chain_trace.md` | Referenced by docs/HARVESTER_SCOPING_DESIGN.md |
| `tasks/ROUND3_D10_D8_REFACTOR.md` | Active task file; referenced by AGENTS.md |
| `docs/SFA_CONSTITUTION_NOTES_2026-02-25.md` | Referenced by DECISIONS.md, block catalog |
| `docs/SCA_SFA_CONTRACT.md` | Referenced by DECISIONS.md, block catalog |
| `docs/PERIOD_ENTITY_ARCHITECTURE_CLARIFICATION.md` | Referenced by DECISIONS.md D-012 |
| `docs/FEDERATION_REGISTRY_REBUILD_SPEC.md` | Referenced by DECISIONS.md D-022 |
| `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md` | Referenced by block catalog, DECISIONS.md |
| `docs/OCD_INTEGRATION_NOTES_2026-02-25.md` | Referenced by DECISIONS.md D-025 |
| `docs/HARVESTER_SCOPING_DESIGN.md` | Referenced by Key Files/Federation_Strategy_Multi_Authority.md |
| `docs/BASELINE_POST_DPRR_2026-02-25.md` | Referenced by ADVISOR_HANDOFF, Federation strategy |
| `docs/IMPORT_DECISIONS.md` | Referenced by Federation strategy |
| `docs/FEDERATION_ARCHITECTURE.md` | Referenced by Federation strategy |
| `docs/ADVISOR_HANDOFF_2026-02-25.md` | Advisor handoff; references multiple docs |
| `docs/FEDERATION_AS_SOURCE.md` | Federation design; may be referenced |
| `docs/FILE_REFERENCE_GUIDE.md` | File organization reference |
| `docs/SUBJECT_CONCEPT_AGENTS_GUIDE.md` | Referenced by FINAL_SESSION_DELIVERABLES |
| `docs/BACKLINK_ENTITY_TYPE_PROPERTIES.md` | Backlink design |
| `docs/BACKLINK_QID_VERIFICATION_ALGORITHM.md` | Backlink verification |
| `docs/PIPELINE_READ_BACK_PRINCIPLE.md` | Pipeline design |
| `docs/NARRATIVE_PATHS_DESIGN.md` | Narrative paths design |
| `docs/EXTERNAL_IDS_PERSISTENCE_ISSUE.md` | External IDs design |
| `docs/prosopographic_federation_design.md` | Prosopographic federation |
| `docs/SUBJ_RR_MIGRATION_RUNBOOK.md` | Migration runbook |
| `docs/setup/CURSOR_MCP_SETUP.md` | MCP setup |
| `docs/setup/DEV_AGENT_SCHEMA_EXECUTION_GUIDE.md` | Dev execution guide |
| `docs/project-management/PM_COMPREHENSIVE_PLAN_2026-02-20.md` | Project management |
| `docs/project-management/PROJECT_PLAN_2026-02-20.md` | Project plan |
| `docs/project-management/BA_ACTION_ITEMS_FROM_ARCHITECTURE_REVIEW.md` | BA action items |
| `docs/project-management/QA_RESULTS_SUMMARY.md` | QA results |
| `docs/FILE_ORGANIZATION_PLAN.md` | File organization |

---

## ARCHIVE — Historical Value, Move to output/archive/

| File | Rationale |
|------|-----------|
| `output/SCHEMA_NODES_FULL_PROPERTIES.md` | One-time schema dump for architect ruling; work done; DEV_HANDOFF referenced it |
| `output/SCHEMA_NODE_RULINGS_2026-02-21.md` | One-time architect rulings on Schema nodes; D-029 migration done |
| `output/DMN_POLICY_THRESHOLD_INVENTORY_2026-02-21.md` | Superseded by sysml/DMN_DECISION_TABLES.md (D1-D14 complete) |
| `output/D031_DECISIONS_ENTRY.md` | Content applied to DECISIONS.md; draft entry |
| `output/DMN_DECISION_TABLES_D6_D14.md` | Superseded by sysml/DMN_DECISION_TABLES.md (D1-D14) |
| `output/DEV_MESSAGE_PRE_PUSH_2026-02-21.md` | Session handoff message |
| `output/DEV_REPORT_2026-02-21.md` | Session dev report |
| `output/ADVISOR_REPORT_POST_FEDERATION_LIST.md` | One-time advisor report post-federation |
| `output/subject-analysis.md` | One-time subject analysis |
| `output/analysis/periods_enriched_chart_20260220_174630.md` | One-time period enrichment chart |
| `output/analysis/unmapped_edges_analysis.md` | One-time unmapped edges analysis |
| `output/analysis/federations_complete_list.md` | One-time federation list |
| `output/analysis/property_chain_Q899409.md` | One-time property chain trace |
| `output/mermaid/Q17167_5hop_taxonomy.md` | One-time taxonomy output |
| `output/mermaid/Q17167_filtered_taxonomy.md` | One-time taxonomy output |
| `output/META_MODEL_EXPLORATION.txt` | One-time meta model exploration |
| `output/META_MODEL_DETAILED.txt` | One-time meta model output |
| `output/P2184_results.txt` | One-time P2184 query results |
| `output/schema_audit_cleanup.txt` | One-time schema audit |
| `output/SCHEMA_AUDIT_REPORT.txt` | One-time schema audit |
| `output/RELATIONSHIP_AUDIT_REPORT.txt` | One-time relationship audit |
| `output/analysis/self_describing_diagnostics.txt` | One-time diagnostics |
| `output/analysis/noise_hotspot_diagnostic_Q1764124_Q271108.txt` | One-time noise diagnostic |
| `output/analysis/registry_unmapped_to_wikidata.txt` | One-time registry analysis |
| `output/outlines/Q17167_complete_property_outline.txt` | One-time property outline |
| `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN_2026-02-25.md` | Session-specific design notes; structure in non-dated version |

---

## EXTRACT — Flag for Content to Canonical Files

| File | Note |
|------|------|
| (none flagged) | No files identified where content should be extracted to DECISIONS.md, DMN tables, or block catalog but is not yet. DEV_HANDOFF and D031_DECISIONS_ENTRY content already in DECISIONS. DMN_POLICY_THRESHOLD and DMN_EXTRACTION_AUDIT content in sysml/DMN_DECISION_TABLES. |

---

## Root Markdown (Loose Files)

| File | Call | Rationale |
|------|------|-----------|
| `AGENTS.md` | KEEP | Canonical; agent context |
| `DECISIONS.md` | KEEP | Canonical; decision log |
| `KANBAN.md` | KEEP | Canonical; task tracking |
| `README.md` | KEEP | Canonical; project intro |
| `REQUIREMENTS.md` | KEEP | Canonical; requirements |
| `DMN_EXTRACTION_AUDIT.md` | ARCHIVE | Duplicate of output/DMN_EXTRACTION_AUDIT.md; output/ is canonical location |
| `D031_MCP_SERVER_SPEC.md` | ARCHIVE | D-031 build spec; content in DECISIONS.md |
| `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` | KEEP | Referenced by md/Architecture; cipher design |
| `AI_CONTEXT.md` | ARCHIVE | D-020 deprecates; redistribute to docs/ then Archive |
| Other root .md (SESSION_SUMMARY_*, FINAL_*, etc.) | ARCHIVE | Session deliverables; historical value |

---

## Data Files (output/) — Not Triaged

JSON, CSV, .cypher, and other data outputs in output/backlinks/, output/neo4j/, output/analysis/*.json, etc. are runtime or pipeline outputs. Recommend bulk ARCHIVE of older dated outputs to output/archive/ after doc moves are reviewed. Not listed individually here.
