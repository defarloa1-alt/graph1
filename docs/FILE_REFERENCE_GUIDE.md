# Chrystallum File Reference Guide

**Created:** 2026-02-22  
**PM:** AI PM Agent  
**Purpose:** Comprehensive file catalog for team review and disposition decisions  
**Sources:** File system analysis, AI_CONTEXT.md, Change_log.py

---

## 📁 **New Folder Structure**

```
C:\Projects\Graph1\
├── docs/
│   ├── project-management/  - PM plans, Kanban, QA reports, BA docs
│   ├── setup/               - Setup guides, MCP config, Dev guides
│   ├── analysis/            - Analysis reports, findings, reviews
│   ├── sessions/            - Session summaries, deliverables
│   └── reference/           - Dictionaries, specifications, guides
├── scripts/                 - All Python scripts (unchanged)
├── [data folders]           - CSV, Temporal, Geographic, etc. (unchanged)
└── [root files]             - AI_CONTEXT, KANBAN, REQUIREMENTS, README (core only)
```

---

## 📊 **Root Directory Files (193 Total)**

### **Category 1: Keep in Root (Core Coordination)**

| File | Size | Modified | Purpose |
|------|------|----------|---------|
| `AI_CONTEXT.md` | 373 KB | 2026-02-22 | AI agent coordination hub - STAYS |
| Kanban | — | — | LachyFS extension (`.devtool/features/`); no KANBAN.md |
| `REQUIREMENTS.md` | 58 KB | 2026-02-21 | Requirements tracking - STAYS |
| `README.md` | 12 KB | 2026-02-19 | Project overview - STAYS |
| `requirements.txt` | 0.2 KB | - | Python dependencies - STAYS |
| `.gitignore` | - | - | Git configuration - STAYS |

**Total: 6 files stay in root** ✅

---

### **Category 2: Project Management (Move to docs/project-management/)**

| File | Size | Modified | Purpose | Disposition |
|------|------|----------|---------|-------------|
| `PROJECT_PLAN_2026-02-20.md` | 11 KB | 2026-02-21 | High-level roadmap | MOVE |
| `PM_COMPREHENSIVE_PLAN_2026-02-20.md` | 17 KB | 2026-02-21 | Comprehensive PM plan | MOVE (primary plan) |
| `PM_PLAN_REVISED_AI_DRIVEN_2026-02-20.md` | 17 KB | 2026-02-21 | AI-driven PM plan revision | ARCHIVE (duplicate) |
| `BA_ACTION_ITEMS_FROM_ARCHITECTURE_REVIEW.md` | 18 KB | 2026-02-21 | BA action items | MOVE |
| `BA_SELF_DESCRIBING_SYSTEM_ANALYSIS.md` | 28 KB | 2026-02-22 | BA system analysis | MOVE |
| `BA_WIKIDATA_PID_MODEL_BUSINESS_FEATURES.md` | 20 KB | 2026-02-22 | BA business features | MOVE |
| `QA_RESULTS_SUMMARY.md` | 2 KB | 2026-02-21 | QA summary | MOVE |
| `QA_TEST_REPORT.md` | 8 KB | 2026-02-21 | QA test report | MOVE |
| `QA_HANDOFF_NEO4J_TESTING.md` | 12 KB | 2026-02-21 | QA handoff | MOVE |
| `QA_QUICK_START.md` | 2 KB | 2026-02-21 | QA quick start | MOVE |

**Total: 10 files → docs/project-management/**

---

### **Category 3: Setup/Guides (Move to docs/setup/)**

| File | Size | Modified | Purpose | Disposition |
|------|------|----------|---------|-------------|
| `START_HERE.txt` | 8 KB | - | Project entry point | MOVE |
| `DEV_AGENT_SCHEMA_EXECUTION_GUIDE.md` | 13 KB | 2026-02-21 | Dev schema guide | MOVE |
| `DEV_INSTRUCTIONS_WIKIDATA_COMPREHENSIVE_IMPORT.md` | 11 KB | 2026-02-22 | Dev import instructions | MOVE |
| `CURSOR_MCP_QUICK_START.md` | 4 KB | 2026-02-19 | MCP quick start | MOVE |
| `CURSOR_MCP_SETUP.md` | 5 KB | 2026-02-19 | MCP setup | MOVE (primary) |
| `MCP_SETUP_INSTRUCTIONS.md` | 5 KB | 2026-02-19 | MCP setup | ARCHIVE (duplicate) |
| `ENABLE_NEO4J_MCP.md` | 2 KB | 2026-02-21 | Enable MCP | ARCHIVE (duplicate) |
| `IMPORT_PROPERTY_MAPPINGS_GUIDE.md` | 7 KB | 2026-02-22 | Property import guide | MOVE |
| `BACKLINKS_EXTRACTION_GUIDE.md` | 4 KB | 2026-02-22 | Backlinks guide | MOVE |
| `PROPERTY_FACET_MAPPER_GUIDE.md` | 5 KB | 2026-02-22 | Property mapper guide | MOVE |
| `WIKIDATA_FETCH_TEST_GUIDE.md` | 8 KB | 2026-02-20 | Wikidata fetch guide | MOVE |

**Total: 11 files → docs/setup/** (4 duplicates → Archive)

---

### **Category 4: Analysis/Research (Move to docs/analysis/)**

| File | Size | Modified | Purpose | Disposition |
|------|------|----------|---------|-------------|
| `PROPERTY_MAPPING_ANALYSIS.md` | 5 KB | 2026-02-22 | Property mapping analysis | MOVE |
| `PROPERTY_DOMAIN_UTILITY_ANALYSIS.md` | 8 KB | 2026-02-22 | Property utility analysis | MOVE |
| `PROPERTY_MAPPING_IMPACT.md` | 5 KB | 2026-02-22 | Property impact analysis | MOVE |
| `MULTI_FACTOR_PROPERTY_ROUTING.md` | 7 KB | 2026-02-22 | Multi-factor routing | MOVE |
| `ARCHITECTURE_ISSUE_HARDCODED_RELATIONSHIPS.md` | 8 KB | 2026-02-22 | Architecture issue doc | MOVE |
| `COMPREHENSIVE_NODE_TYPES_2026-02-19.md` | 8 KB | 2026-02-20 | Node types catalog | MOVE |
| `SYSTEM_SUBGRAPH_ARCHITECTURE_2026-02-19.md` | 5 KB | 2026-02-20 | System architecture | MOVE |
| `CHRYSTALLUM_SYSTEM_VISUALIZATION_2026-02-19.md` | 7 KB | 2026-02-20 | System visualization | MOVE |
| `NODE_ALIGNMENT_ISSUES_2026-02-19.md` | 5 KB | 2026-02-20 | Alignment issues | MOVE |
| `ROMAN_REPUBLIC_Q17167_COMPLETE_PROPERTIES.md` | 7 KB | 2026-02-20 | Roman Republic analysis | MOVE |
| `ROMAN_REPUBLIC_2HOP_TAXONOMY.md` | 9 KB | 2026-02-20 | 2-hop taxonomy | MOVE |
| `Q17167_FACET_MAPPING.md` | 6 KB | 2026-02-20 | Facet mapping | MOVE |
| `Q17167_10_FACETS_CONFIRMED_WITH_LABELS.md` | 8 KB | 2026-02-20 | Facet confirmation | MOVE |
| `HISTORICAL_PERIOD_BACKLINKS_ANALYSIS.md` | 9 KB | 2026-02-20 | Period backlinks | MOVE |
| `HISTORICAL_PERIODS_TREE_CHART.md` | 6 KB | 2026-02-20 | Period tree | MOVE |
| `89_HISTORICAL_PERIODS_COMPLETE_CHART.md` | 4 KB | 2026-02-20 | Period chart (primary) | MOVE |
| `COMPLETE_3HOP_TAXONOMY_ANALYSIS.md` | 16 KB | 2026-02-20 | 3-hop taxonomy | MOVE |
| `5HOP_COMPLETE_TAXONOMY.md` | 17 KB | 2026-02-20 | 5-hop taxonomy | MOVE |
| `5HOP_EXPLORATION_COMPLETENESS.md` | 5 KB | 2026-02-20 | 5-hop completeness | MOVE |
| `3HOP_VISUAL_SUMMARY.md` | 8 KB | 2026-02-20 | 3-hop visual | MOVE |
| `COMPREHENSIVE_DISCOVERY_SUMMARY.md` | 17 KB | 2026-02-20 | Discovery summary | MOVE |
| `TAXONOMY_RELATIONSHIPS_TABLE.md` | 9 KB | 2026-02-20 | Taxonomy table | MOVE |
| `COMPLETE_SUCCESSION_CHAIN.md` | 6 KB | 2026-02-20 | Succession chain | MOVE |
| `COMPLETE_PROPERTY_OUTLINE_SUMMARY.md` | 7 KB | 2026-02-20 | Property outline | MOVE |
| `CSV_ANALYSIS_READY.md` | 10 KB | 2026-02-20 | CSV analysis | MOVE |
| `GEOGRAPHIC_AND_PERIODO_ANALYSIS.md` | 4 KB | 2026-02-20 | Geographic analysis | MOVE |
| `PERIODO_PLEIADES_COMPARISON.md` | 4 KB | 2026-02-20 | Periodo comparison | MOVE |
| `PLACE_MODEL_ANALYSIS.md` | 5 KB | 2026-02-19 | Place model | MOVE |
| `TIME_PERIOD_DEFINITION.md` | 4 KB | 2026-02-20 | Period definition | MOVE |
| `P2184_HISTORY_OF_TOPIC_DISCOVERY.md` | 6 KB | 2026-02-20 | Topic discovery | MOVE |
| `RELIGIOUS_FACET_BACKLINKS.md` | 6 KB | 2026-02-20 | Religious backlinks | MOVE |
| `SCA_CANDIDATE_BUCKETS.md` | 7 KB | 2026-02-20 | SCA buckets | MOVE |
| `SCA_FILTERED_TREE_WITH_AUTHORITIES.md` | 9 KB | 2026-02-20 | SCA tree | MOVE |
| `SCA_FILTERS_COMPLETE_REVIEW.md` | 8 KB | 2026-02-20 | SCA filters | MOVE |
| `SCA_PROCESS_NARRATIVE.md` | 17 KB | 2026-02-20 | SCA narrative | MOVE |
| `IMMEDIATE_SUBJECT_CONCEPTS_AND_SFAS.md` | 7 KB | 2026-02-20 | Subject concepts | MOVE |
| `12_FAILED_PERIODS_TEMPORAL_DATA.md` | 5 KB | 2026-02-20 | Failed periods | MOVE |
| `COMMONS_CATEGORY_INDEX_ANALYSIS.md` | 6 KB | 2026-02-20 | Commons analysis | MOVE |
| `deep-research-report.md` | 49 KB | 2026-02-17 | Research report | MOVE |

**Total: ~38 files → docs/analysis/**

---

### **Category 5: Session Summaries (Move to docs/sessions/)**

| File | Size | Modified | Purpose | Disposition |
|------|------|----------|---------|-------------|
| `SESSION_SUMMARY_PROPERTY_MAPPING.md` | 6 KB | 2026-02-22 | Property mapping session | MOVE |
| `GRAPH_ARCHITECT_FINAL_SESSION_SUMMARY.md` | 8 KB | 2026-02-22 | Architect session | MOVE |
| `GRAPH_ARCHITECT_SESSION_COMPLETE.md` | 10 KB | 2026-02-21 | Architect complete | MOVE |
| `GRAPH_ARCHITECT_COMPLETE_SESSION_SUMMARY.md` | 16 KB | 2026-02-21 | Architect summary | MOVE |
| `GRAPH_ARCHITECT_DELIVERABLES_2026-02-22.md` | 10 KB | 2026-02-21 | Architect deliverables | MOVE |
| `FINAL_SESSION_DELIVERABLES_PROPERTY_MAPPING.md` | 11 KB | 2026-02-22 | Property mapping deliverables | MOVE |
| `FINAL_SESSION_DELIVERABLES.md` | 9 KB | 2026-02-20 | Session deliverables | MOVE |
| `SESSION_SUMMARY_SUBJECT_CONCEPT_AGENTS.md` | 7 KB | 2026-02-20 | SCA session | MOVE |
| `SESSION_CONTEXT_FOR_QA.md` | 3 KB | 2026-02-21 | QA context | MOVE |
| `REBUILD_COMPLETE_SUMMARY.md` | 8 KB | 2026-02-19 | Rebuild summary | MOVE |
| `SUBJECT_CONCEPT_AGENTS_BUILD_SUMMARY.md` | 14 KB | 2026-02-20 | SCA build summary | MOVE |

**Total: 11 files → docs/sessions/**

---

### **Category 6: Reference/Specification (Move to docs/reference/)**

| File | Size | Modified | Purpose | Disposition |
|------|------|----------|---------|-------------|
| `DATA_DICTIONARY.md` | 26 KB | 2026-02-21 | Data dictionary | MOVE |
| `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` | 43 KB | 2026-02-21 | Cipher architecture | MOVE |
| `AGENT_REFERENCE_FILE_PATHS.md` | 17 KB | 2026-02-19 | Agent file paths | MOVE |
| `SCA_BOOTSTRAP_CONSOLIDATED.md` | 8 KB | 2026-02-20 | SCA bootstrap | MOVE |
| `SUBJECT_CONCEPT_AGENTS_QUICK_REF.md` | 8 KB | 2026-02-20 | SCA quick ref | MOVE |
| `REQUIREMENTS_ANALYST_INTRODUCTION.md` | 15 KB | 2026-02-21 | BA introduction | MOVE |
| `FEDERATION_MAPPER_AGENT.md` | 7 KB | 2026-02-20 | Federation mapper | MOVE |
| `NEO4J_IMPORTER_PLAN.md` | 11 KB | 2026-02-20 | Importer plan | MOVE |
| `INTEGRATION_AGENT_PLAN.md` | 9 KB | 2026-02-20 | Integration plan | MOVE |
| `cursor_graph_architect_agent_role_defin.md` | 309 KB | 2026-02-22 | Architect role definition | MOVE |
| `property_mapping_queries_validated.md` | 4 KB | 2026-02-22 | Validated queries | MOVE |
| `cipher-talk.md` | 31 KB | 2026-02-21 | Cipher discussion | MOVE |
| `2-16-26-Day in the life of a facet.md` | 13 KB | 2026-02-18 | Facet narrative | MOVE |
| `chattofile.md` | 15 KB | 2026-02-17 | Chat archive | MOVE or DELETE |

**Total: 14 files → docs/reference/**

---

### **Category 7: Scripts/Utilities (Keep Organized - Maybe Move Some)**

**193 total files - 88 Python scripts in root**

**Recommendation:** Most should stay for now (functional), but consider moving to:
- `scripts/utils/` - One-off utility scripts
- `scripts/qa/` - QA test scripts
- `scripts/setup/` - Setup/config scripts

**Priority:** LOW (defer until scripts needed)

---

### **Category 8: Cypher Files (Move to cypher/queries/)**

| File | Size | Modified | Purpose | Disposition |
|------|------|----------|---------|-------------|
| `property_mapping_test_queries.cypher` | 5 KB | 2026-02-22 | Property test queries | MOVE to cypher/queries/ |
| `complete_ddl.cypher` | 1 KB | 2026-02-21 | Complete DDL | MOVE to cypher/schema/ |
| `execute_ddl.cypher` | 3 KB | 2026-02-21 | Execute DDL | MOVE to cypher/schema/ |
| `schema_ddl_to_execute.cypher` | 4 KB | 2026-02-21 | Schema DDL | MOVE to cypher/schema/ |
| `graph_view_queries.cypher` | 5 KB | 2026-02-21 | Graph views | MOVE to cypher/queries/ |
| `neo4j_queries_graph_overview.cypher` | 6 KB | 2026-02-22 | Graph overview | MOVE to cypher/queries/ |
| `cleanup_duplicates.cypher` | 3 KB | 2026-02-21 | Cleanup | MOVE to cypher/utilities/ |
| `explore_imported_entities.cypher` | 6 KB | 2026-02-21 | Explore entities | MOVE to cypher/queries/ |

**Total: 8 files → cypher/** (organized by subfolder)

---

## 📋 **Disposition Recommendations**

### **Move (73 files):**
- 10 → docs/project-management/
- 11 → docs/setup/
- 38 → docs/analysis/
- 11 → docs/sessions/
- 14 → docs/reference/
- 8 → cypher/ (various subfolders)

### **Keep in Root (6 files):**
- AI_CONTEXT.md (deprecated), Kanban (extension), REQUIREMENTS.md, README.md, requirements.txt, .gitignore

### **Archive Duplicates (~8 files):**
- Old PM plan versions
- Duplicate MCP setup files
- Old period charts

### **Review Later (~88 Python scripts):**
- Functional, working scripts
- Can organize into scripts/ subfolders later
- Not urgent

---

## 🎯 **Execution Plan**

**Phase 1 (Now):**
- Move PM files (10)
- Move setup files (11)
- Update AI_CONTEXT with new paths

**Phase 2 (After Review):**
- Move analysis files (38)
- Move session files (11)
- Move reference files (14)
- Archive duplicates (8)

**Phase 3 (Low Priority):**
- Organize Cypher files (8)
- Consider script organization (defer)

---

**This guide ready for team review!**  
**Recommendations based on file purpose, size, dates, and content.**

**Proceed with file moves?** 📁
