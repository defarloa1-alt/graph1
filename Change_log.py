"""
CHANGE LOG
==========

Purpose: Track non-trivial architecture changes, new capabilities, and significant updates

Format:
-------
Date: YYYY-MM-DD HH:MM
Category: [Architecture | Capability | Schema | Docs | Refactor | Integration]
Summary: Brief description
Files: List of affected files
Reason: Why this change was made

Guidelines:
-----------
- Log changes that affect system architecture, data model, or core capabilities
- Include context for future reference
- Keep entries concise but informative
- Newest entries at the top

================================================================================
"""

# ==============================================================================
# 2026-02-14 11:24 | Consolidated Spec: First-Class Node Normative Lock
# ==============================================================================
# Category: Architecture, Docs, Schema
# Summary: Added explicit normative first-class node section to consolidated architecture and formalized Communication as facet-only
# Files:
#   - Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md
# Reason: Eliminate ambiguity between operational lists and architecture spec before schema refactor/Neo4j rollout.
# Notes:
#   - Added Section `3.0.1 Canonical First-Class Node Set (Normative)`.
#   - Locked legacy label mapping in spec text (`Subject/Concept` -> `SubjectConcept`, `Person` -> `Human`).
#   - Updated Section 3.3 facet count to 17 and clarified `Communication` as facet/domain dimension only.
# ==============================================================================

# ==============================================================================
# 2026-02-14 11:15 | First-Class Node Lock + Communication Demotion
# ==============================================================================
# Category: Schema, Docs
# Summary: Locked canonical first-class node list and removed legacy labels from operational baseline docs
# Files:
#   - Key Files/Main nodes.md
#   - md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md
#   - AI_CONTEXT.md
# Reason: Finalize node-model decisions before broader claim/federation expansion.
# Notes:
#   - Main nodes now: `SubjectConcept, Human, Gens, Praenomen, Cognomen, Event, Place, Period, Dynasty, Institution, LegalRestriction, Claim, Organization, Year`.
#   - Legacy labels removed from baseline list: `Subject`, `Person`, `Concept`.
#   - `Communication` is now facet/domain-only (not a first-class node label).
# ==============================================================================

# ==============================================================================
# 2026-02-14 10:19 | Republic Agent SubjectConcept Seed Pack (Q17167)
# ==============================================================================
# Category: Capability, Docs
# Summary: Added import-ready SubjectConcept seed pack for Republic agent domain with facet tags/confidence
# Files:
#   - JSON/wikidata/proposals/Q17167_republic_agent_subject_concepts.csv
#   - JSON/wikidata/proposals/Q17167_republic_agent_subject_concepts.json
# Reason: Provide concrete first-pass SubjectConcept implementation set for Roman Republic multi-facet routing.
# Notes:
#   - 17 proposed SubjectConcept nodes.
#   - Includes discipline flag, primary facet/confidence, and parent hierarchy proposals.
#   - JSON includes facet_confidence vectors and BROADER_THAN relationship proposals.
# ==============================================================================

# ==============================================================================
# 2026-02-14 10:08 | Q17167 Critical Test: Claim-Rich Subgraph Proposal
# ==============================================================================
# Category: Capability, Integration, Docs
# Summary: Executed end-to-end Q17167 direct+backlink analysis and generated claim/subgraph proposal artifacts
# Files:
#   - scripts/tools/wikidata_generate_claim_subgraph_proposal.py
#   - JSON/wikidata/statements/Q17167_statements_full.json
#   - JSON/wikidata/statements/Q17167_statement_datatype_profile_summary.json
#   - JSON/wikidata/statements/Q17167_statement_datatype_profile_by_property.csv
#   - JSON/wikidata/statements/Q17167_statement_datatype_profile_datatype_pairs.csv
#   - JSON/wikidata/backlinks/Q17167_backlink_harvest_report.json
#   - JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_summary.json
#   - JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_by_entity.csv
#   - JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_pair_counts.csv
#   - JSON/wikidata/proposals/Q17167_claim_subgraph_proposal.json
#   - JSON/wikidata/proposals/Q17167_claim_subgraph_proposal.md
# Reason: Validate federation/backlink pipeline against a high-value historical seed and produce a concrete subgraph claim proposal.
# Notes:
#   - Seed: `Q17167` (Roman Republic)
#   - Discovery harvest: candidates considered=227, accepted=150, gate status=pass
#   - Proposal output: nodes=178, relationship claims=197 (direct=39, backlink=158), attribute claims=41
# ==============================================================================

# ==============================================================================
# 2026-02-14 09:58 | Backlink Harvester Discovery Mode + Expanded Budgets
# ==============================================================================
# Category: Capability, Docs, Architecture
# Summary: Added explicit discovery/production modes to backlink harvester with mode-aware budget and class-gate behavior
# Files:
#   - scripts/tools/wikidata_backlink_harvest.py
#   - JSON/wikidata/backlinks/README.md
#   - JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json
# Reason: Support broad hierarchy learning runs without weakening production controls.
# Notes:
#   - New `--mode {production,discovery}`.
#   - Discovery defaults: `sparql_limit=2000`, `max_sources_per_seed=1000`, `max_new_nodes_per_seed=500`.
#   - Discovery auto behavior: unions schema relationship properties into property surface and disables class allowlist gate by default.
#   - New `--class-allowlist-mode {auto,schema,disabled}` for explicit gate control.
#   - Verified run: `Q1048` report now records `mode: discovery` and `class_allowlist_mode: disabled`.
# ==============================================================================

# ==============================================================================
# 2026-02-14 09:25 | Section 8.6 and Appendix K Consistency Pass
# ==============================================================================
# Category: Docs, Architecture
# Summary: Tightened wording and section consistency for federation dispatcher text in consolidated architecture
# Files:
#   - Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md
# Reason: Ensure Section 8.6 reads natively with surrounding Section 8 style and aligns with Appendix K contract language.
# Notes:
#   - Clarified dispatcher as mandatory control plane and no-bypass rule.
#   - Renamed 8.6.1 heading to "Dispatcher Route Matrix (Normative)" for consistency.
#   - Harmonized run-report wording and frontier phrasing.
#   - Added explicit cross-reference from 8.6.6 to Appendix K.4-K.6.
# ==============================================================================

# ==============================================================================
# 2026-02-14 09:20 | Canonical Sources Synced to Main Nodes Baseline
# ==============================================================================
# Category: Docs, Schema
# Summary: Updated canonical node-source reference to reflect operational main-node list in Key Files/Main nodes.md
# Files:
#   - md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md
#   - Change_log.py
# Reason: User identified mismatch between canonical-sources node list and current main-node list.
# Notes:
#   - Added `Key Files/Main nodes.md` as top source for current operational main nodes.
#   - Replaced first-class baseline list with the exact Main nodes list.
#   - Preserved normalization note for legacy labels (`Subject`/`Concept`) vs consolidated architecture mapping.
# ==============================================================================

# ==============================================================================
# 2026-02-14 09:03 | Concept Label Deprecation Enforcement (Concept -> SubjectConcept)
# ==============================================================================
# Category: Schema, Docs, Refactor
# Summary: Enforced canonical SubjectConcept usage across active prompts/guides and added formal migration note
# Files:
#   - md/Agents/TEST_SUBJECT_AGENT_PROMPT.md
#   - md/Guides/Neo4j_Import_Guide.md
#   - Neo4j/IMPLEMENTATION_ROADMAP.md
#   - md/Architecture/Backbone_Alignment_Validation_Tools.md
#   - md/Architecture/Technical_Persistence_Flow.md
#   - md/Architecture/Langraph_Workflow.md
#   - md/Core/building chrystallum a knowledge graph of history.md
#   - md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md
#   - md/Architecture/CONCEPT_TO_SUBJECTCONCEPT_MIGRATION_2026-02-14.md
# Reason: Prevent schema drift and ensure agents/scripts stop emitting legacy :Concept labels.
# Notes:
#   - Legacy `:Concept` usage in active examples was removed or mapped to `:SubjectConcept`.
#   - `Person:Concept`/`Place:Concept`/`Event:Concept` examples were normalized to concrete labels only.
#   - Wikidata concept/ideology inputs are now explicitly mapped to `SubjectConcept` in roadmap examples.
# ==============================================================================

# ==============================================================================
# 2026-02-13 19:06 | Node Schema Legacy-to-Canonical Mapping Clarification
# ==============================================================================
# Category: Docs, Architecture
# Summary: Added explicit legacy label mapping and canonical first-class node list reference
# Files:
#   - md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md
# Reason: Resolve confusion between archived node schemas and current consolidated architecture labels.
# Notes:
#   - `Person` -> `Human`
#   - `Subject`/`Concept` -> `SubjectConcept`
#   - Documented canonical domain and supporting node labels in one place.
# ==============================================================================

# ==============================================================================
# 2026-02-13 16:00 | Consolidated Architecture Update for Federation Dispatcher
# ==============================================================================
# Category: Architecture, Docs
# Summary: Updated consolidated architecture spec with normative dispatcher/backlink control-plane rules
# Files:
#   - Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md
#   - AI_CONTEXT.md
# Reason: Align canonical architecture doc with implemented federation routing, gating, and frontier controls.
# Notes:
#   - Added Section 8.6 (dispatcher routes, temporal precision gate, class controls, frontier guard).
#   - Updated Appendix K scope and pipeline contract to include dispatcher + quarantine behavior.
# ==============================================================================

# ==============================================================================
# 2026-02-13 15:56 | Dispatcher Routing + Frontier Control in Backlink Harvester
# ==============================================================================
# Category: Capability, Architecture, Docs
# Summary: Upgraded backlink harvester from pair counting to explicit dispatcher routing with frontier eligibility controls
# Files:
#   - scripts/tools/wikidata_backlink_harvest.py
#   - JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json
#   - Neo4j/FEDERATION_BACKLINK_STRATEGY.md
#   - AI_CONTEXT.md
# Reason: Enforce topology/identity/attribute separation operationally and prevent traversal hairballs.
# Notes:
#   - Added statement routing buckets (edge_candidate, federation_id, temporal_anchor, node_property, quarantine, etc.).
#   - Added temporal precision gate (`--min-temporal-precision`, default year=9).
#   - Added optional class denylist (`--p31-denylist-qid`).
#   - Added frontier exclusion logic (`no_edge_candidates` and literal-heavy threshold).
# ==============================================================================

# ==============================================================================
# 2026-02-13 15:55 | Standalone Backlink Candidate Profiler
# ==============================================================================
# Category: Capability, Docs
# Summary: Added standalone profiler for backlink candidate QID sets without running harvest
# Files:
#   - scripts/tools/wikidata_backlink_profile.py
#   - JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_summary.json
#   - JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_by_entity.csv
#   - JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_pair_counts.csv
#   - JSON/wikidata/backlinks/README.md
#   - Neo4j/FEDERATION_BACKLINK_STRATEGY.md
#   - AI_CONTEXT.md
# Reason: Enable fast datatype/value_type policy assessment for candidate sets from report/list inputs.
# Notes:
#   - Accepts input from report sections (`accepted`, `rejected`, `all`) or explicit QID lists.
#   - Emits summary + per-entity + pair-count artifacts for operational review.
# ==============================================================================

# ==============================================================================
# 2026-02-13 15:50 | Backlink Harvester Script + Run Report Capability
# ==============================================================================
# Category: Capability, Architecture, Docs
# Summary: Implemented controlled Wikidata backlink harvester with class and datatype policy gates
# Files:
#   - scripts/tools/wikidata_backlink_harvest.py
#   - JSON/wikidata/backlinks/README.md
#   - JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json
#   - Neo4j/FEDERATION_BACKLINK_STRATEGY.md
#   - AI_CONTEXT.md
# Reason: Move backlink strategy from concept to executable workflow with measurable acceptance/rejection criteria.
# Notes:
#   - Enforces property allowlist + schema class allowlist (`P31` with `P279` ancestor walk).
#   - Emits accepted/rejected lists and rejection reasons (including budget constraints).
#   - Applies datatype/value_type gate on accepted source nodes before downstream ingestion.
# ==============================================================================

# ==============================================================================
# 2026-02-13 15:45 | Backlink Policy Canonicalization + Datatype Routing Clarification
# ==============================================================================
# Category: Architecture, Capability, Docs
# Summary: Replaced noisy backlink notes with a strict canonical strategy tied to datatype/value-type routing gates
# Files:
#   - Neo4j/FEDERATION_BACKLINK_STRATEGY.md
#   - AI_CONTEXT.md
# Reason: Keep only actionable backlink logic and explicitly define how datatype/value_type control ingest behavior.
# Notes:
#   - Locked in reverse-triple approach (`?source ?prop ?target`) over page-level backlink APIs.
#   - Added mandatory stop conditions (depth, budget, allowlists, abort thresholds).
#   - Clarified operational use of datatype/value_type for routing, safety, and cost control.
# ==============================================================================

# ==============================================================================
# 2026-02-13 15:20 | Wikidata Statement Datatype Profiling + Spec
# ==============================================================================
# Category: Capability, Architecture, Docs
# Summary: Added full-statement datatype profiling workflow and formal ingestion spec
# Files:
#   - scripts/tools/wikidata_statement_datatype_profile.py
#   - scripts/tools/wikidata_sample_statement_records.py
#   - scripts/tools/wikidata_fetch_all_statements.py
#   - md/Architecture/Wikidata_Statement_Datatype_Ingestion_Spec.md
#   - statement data types.md
#   - JSON/wikidata/statements/Q1048_statement_datatype_profile_summary.json
#   - JSON/wikidata/statements/Q1048_statement_datatype_profile_by_property.csv
#   - JSON/wikidata/statements/Q1048_statement_datatype_profile_datatype_pairs.csv
#   - JSON/wikidata/statements/Q1048_statements_sample_100.csv
# Reason: Move from ad hoc property handling to datatype-driven federation ingestion design.
# Notes:
#   - Verified on Q1048 full statements export (451 statements, 324 properties).
#   - Datatype profile captured counts for wikibase-item/external-id/time/monolingualtext/etc.
#   - Provides concrete basis for external-id federation mapping and qualifier/reference retention.
# ==============================================================================

# ==============================================================================
# 2026-02-13 13:30 | AI Context Memory Bank
# ==============================================================================
# Category: Docs, Architecture
# Summary: Created AI_CONTEXT.md as persistent memory bank for AI agents
# Files:
#   - AI_CONTEXT.md (project state, recent actions, active todos)
# Reason: Enable AI agents to understand project state across sessions
# Notes: Documents dual-spine temporal architecture, migration scripts, next steps
#        Added workflow note: file must be committed/pushed to persist across sessions
# ==============================================================================

# ==============================================================================
# 2026-02-13 12:00 | Git Setup & Documentation
# ==============================================================================
# Category: Docs, Infrastructure
# Summary: Initial repository setup with Git LFS configuration and workflow guide
# Files:
#   - .gitignore (large data dumps, generated outputs)
#   - .gitattributes (Git LFS tracking rules)
#   - Environment/GIT_WORKFLOW_GUIDE.md (beginner Git guide with VS Code tips)
# Reason: Enable GitHub collaboration and document Git workflow for team members
# Notes: Removed oversized files from history; Birthday.txt purged for secrets
# ============================================================================== 
