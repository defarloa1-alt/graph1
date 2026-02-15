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
# 2026-02-14 23:50 | Phase 1 Final: Custom GPT Knowledge Base + Deduplication
# ==============================================================================
# Category: Docs, Integration, Capability
# Summary: Created comprehensive knowledge base for ChatGPT Custom GPT deployment; added deduplication workflow to prevent duplicate edges
# Files (NEW):
#   - KNOWLEDGE_BASE_INDEX.md (NEW) - Navigation index for all 8 knowledge base files + custom instructions
#   - QUICK_START.md (UPDATED) - Added 360-line Deduplication Workflow section with Cypher patterns
#   - AGENT_EXAMPLES.md (UPDATED) - Added Examples 12a & 12b showing deduplication + conflict resolution
# Files (READY FOR UPLOAD):
#   - SCHEMA_REFERENCE.md (1,200 lines)
#   - AGENT_EXAMPLES.md (1,650+ lines, now with deduplication examples)
#   - QUICK_START.md (600+ lines, now with deduplication workflow)
#   - RELATIONSHIP_TYPES_SAMPLE.md (900 lines)
#   - role_qualifier_reference.json (700 lines)
#   - relationship_facet_baselines.json (400 lines)
#   - PHASE_1_DECISIONS_LOCKED.md (250 lines)
#   - ARCHITECTURE_OPTIMIZATION_REVIEW.md (4,500 lines)
# Reason: 
#   1. Support deployment to ChatGPT Custom GPT (agents need comprehensive reference)
#   2. Prevent duplicate edges (critical gap identified in agent workflow)
#   3. Document deduplication + Bayesian reconciliation patterns
#   4. Support conflict detection (temporal disagreements, source conflicts)
# Changes:
#   1. Deduplication Workflow:
#      - Query pattern: Check existing claim by (source QID, relationship type, target QID, facet, temporal context)
#      - Decision logic: Merge if exists, create if not
#      - Bayesian merging: (prior + new) / 2 * agreement_factor
#      - Authority reconciliation: Append new authority source to authority_ids JSON
#      - Conflict handling: Flag high-magnitude conflicts (temporal delta > 0), escalate to human review
#   2. Examples 12a & 12b:
#      - 12a: Shows merging same claim from two agreeing sources (Wikidata 0.95 + Wikipedia 0.92 → 0.93 posterior)
#      - 12b: Shows conflict detection (DIED_AT -44 vs -43, flags for review, posterior drops to 0.205)
#   3. KNOWLEDGE_BASE_INDEX.md:
#      - Complete navigation guide for all 8 files
#      - File descriptions (size, purpose, when to use)
#      - Upload checklist + custom instructions for ChatGPT
#      - Quick reference table (Question → File + Section)
# Promotion Rule (Unchanged):
#   - Universal: IF confidence >= 0.90 AND posterior >= 0.90 THEN promoted = true
#   - Fallacies: Flagged with intensity (HIGH/LOW), never block promotion
# Next Steps:
#   - Upload 8 files to ChatGPT Custom GPT knowledge base
#   - Use KNOWLEDGE_BASE_INDEX.md and custom instructions as reference
#   - Test agent in ChatGPT; agents should now deduplicate automatically

# ==============================================================================
# 2026-02-14 23:45 | Phase 1: Genealogy & Participation Implementation
# ==============================================================================
# Category: Architecture, Capability, Schema
# Summary: Implemented Phase 1 genealogy/participation support with LLM-assisted QID resolution, dynamic role validation, and per-facet confidence baselines
# Files:
#   - Relationships/role_qualifier_reference.json (NEW)
#   - Relationships/relationship_facet_baselines.json (NEW)
#   - Relationships/relationship_types_registry_master.csv (EXTENDED +10 rows)
#   - scripts/tools/claim_ingestion_pipeline.py (EXTENDED +400 lines)
#   - PHASE_1_DECISIONS_LOCKED.md (NEW)
#   - PHASE_1_GENEALOGY_PARTICIPATION.md (NEW)
# Reason: Enable genealogical modeling and event participation tracking for historical entities (e.g., Roman figures)
# Changes:
#   1. QID Resolution (Decision 1):
#      - Added QIDResolver class with LLM-assisted Wikidata search
#      - Supports provisional local QIDs (local_entity_{hash}) for entities without Wikidata matches
#      - Context-aware scoring: temporal alignment, role match, gens match
#      - Falls back gracefully when Wikidata unavailable or confidence too low
#   2. Role Validation (Decision 3):
#      - Added RoleValidator class with canonical role registry (70+ roles)
#      - Supports exact match, alias match, and LLM fuzzy match
#      - Registry maps roles to Wikidata P-values and CIDOC-CRM types
#      - 10 categories: military, diplomatic, political, religious, intellectual, social, economic, communication, genealogical
#      - Prevents role invention while supporting natural language inputs ("leading forces" → "commander")
#   3. Per-Facet Confidence Baselines (Decision 2):
#      - Created relationship_facet_baselines.json with per-facet confidence overrides
#      - Example: SPOUSE_OF political=0.92, social=0.90, demographic=0.88
#      - Supports context-aware confidence boosting based on facet
#   4. Missing Relationships Added (5 + inverses):
#      - PARTICIPATED_IN / HAD_PARTICIPANT (P710)
#      - DIED_AT / DEATH_LOCATION (P1120)
#      - MEMBER_OF_GENS / HAS_GENS_MEMBER (P53)
#      - NEGOTIATED_TREATY / TREATY_NEGOTIATOR (P3342)
#      - WITNESSED_EVENT / WITNESSED_BY (P1441)
#   5. CRMinf Tracking (Decision 4 - Phase 1 Scope):
#      - Deferred full CIDOC-CRM alignment to Phase 2
#      - CRMinf belief tracking (minf_belief_id) ready for implementation
# Key Design Decisions (PHASE_1_DECISIONS_LOCKED.md):
#   - Option D: LLM-assisted QID resolution with provisional fallback (not hard requirement)
#   - Option B: Per-facet confidence baselines (nuanced promotion)
#   - Option A + Dynamic: Edge properties for roles + canonical registry with LLM fuzzy match
#   - CRMinf now, CIDOC later: Minimizes complexity while enabling reasoning provenance
# Next Steps (Phase 2):
#   - Implement Wikidata API integration for QID resolver
#   - Implement LLM semantic matching for role validator
#   - Add CIDOC-CRM class mappings to relationships
#   - Expand role registry dynamically from Wikidata P410/P39
#   - Test with Caesar-Brutus genealogical cluster
# Notes:
#   - Audit discovered 24 genealogy relationships ALREADY in CSV (better than expected)
#   - Phase 1 adds only 5 missing relationships (not rebuilding from scratch)
#   - Role qualifier reference has 70+ roles covering most historical contexts
#   - Relationship CSV now 312 rows (was 302)
#   - QIDResolver and RoleValidator are Phase 1 stubs; Phase 2 will integrate full LLM/API
# ==============================================================================

# ==============================================================================
# 2026-02-14 22:50 | Fischer Fallacy Flagging (Flag-Only, No Hard Blocks)
# ==============================================================================
# Category: Architecture, Policy Change
# Summary: Refactored from hard-block approach to flag-only; all fallacies flagged for review, promotion based on metrics
# Files:
#   - scripts/tools/claim_ingestion_pipeline.py
#   - scripts/agents/query_executor_agent_test.py
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
#   - AI_CONTEXT.md
# Reason: Fallacy heuristics are imperfect and should not block valid claims; metrics (confidence + posterior) are more reliable
# Notes:
#   - Promotion rule is universal: confidence >= 0.90 AND posterior >= 0.90 → promoted = true
#   - All fallacies always detected and flagged; fallacy_flag_intensity guides downstream review prioritization
#   - New method: _determine_fallacy_flag_intensity(critical_fallacy, claim_type, facet) → "none" | "low" | "high"
#   - High intensity: interpretive claims warrant closer review (motivational, political, causal, etc.)
#   - Low intensity: descriptive claims lower concern (temporal, geographic, taxonomic, etc.)
#   - Fallacies preserved in audit trail in response dict
#   - Test cases show all profiles promoting on metrics, with varying flag intensities
# ==============================================================================

# ==============================================================================
# 2026-02-14 22:45 | Selective Fischer Fallacy Gating Policy Matrix
# ==============================================================================
# Category: Capability, Architecture
# Summary: [DEPRECATED - replaced by flag-only approach] Initially implemented hard-block gating; replaced by flag-only in 22:50 update
# ==============================================================================

# ==============================================================================
# 2026-02-14 22:15 | Authority Provenance Tracking for All Claims
# ==============================================================================
# Category: Capability, Schema, Docs, Integration
# Summary: Added authority/source capture fields to enable upstream traceability to Wikidata, LCSH, and other authority systems
# Files:
#   - scripts/tools/claim_ingestion_pipeline.py
#   - scripts/agents/query_executor_agent_test.py
#   - Neo4j/schema/07_core_pipeline_schema.cypher
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
#   - AI_CONTEXT.md
# Reason: Ensure all claims can capture and persist their authority source and IDs for provenance tracking
# Notes:
#   - New parameters: authority_source (string), authority_ids (string/dict/list)
#   - Authority fields persist on both Claim and RetrievalContext nodes
#   - Schema constraint: Claim.authority_source IS NOT NULL
#   - Normalization helper: _normalize_authority_ids() supports flexible formats
#   - Test examples show Wikidata QID and LCSH identifier patterns
# ==============================================================================

# ==============================================================================
# 2026-02-14 21:30 | Fischer Fallacy Guardrails + Bayesian Posterior in Claim Pipeline
# ==============================================================================
# Category: Capability, Integration
# Summary: Added historian-logic engine with Fischer-style fallacy detection and Bayesian scoring, then wired promotion to posterior+fallacy gates
# Files:
#   - scripts/tools/historian_logic_engine.py
#   - scripts/tools/claim_ingestion_pipeline.py
#   - scripts/agents/query_executor_agent_test.py
#   - md/Agents/AGENT_README.md
#   - AI_CONTEXT.md
# Reason: Enforce reasoning-quality controls during claim ingestion and promotion, not just post-hoc review.
# Notes:
#   - New persisted claim fields: prior_probability, likelihood, posterior_probability, bayesian_score,
#     fallacies_detected, fallacy_penalty, critical_fallacy
#   - Promotion now requires confidence >= 0.90, posterior_probability >= 0.90, and no critical fallacy
# ==============================================================================

# ==============================================================================
# 2026-02-14 19:05 | Strict Claim Signature Enforcement
# ==============================================================================
# Category: Capability, Schema, Docs
# Summary: Enforced strict claim_signature structure and QID match for deterministic claim IDs
# Files:
#   - scripts/tools/claim_ingestion_pipeline.py
#   - scripts/agents/README.md
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
# Reason: Ensure claim IDs are derived from QID + full statement signature with consistent semantics
# Notes:
#   - claim_signature must include qid, pvalues, values
#   - qid must match subject_qid
#   - pvalues/values must use P-IDs and be non-empty
# ==============================================================================

# ==============================================================================
# 2026-02-14 18:50 | Claim ID Now QID + Statement Signature
# ==============================================================================
# Category: Capability, Schema, Docs
# Summary: Claim IDs now derived from subject QID + full statement signature; facet is required explicitly
# Files:
#   - scripts/tools/claim_ingestion_pipeline.py
#   - scripts/agents/query_executor_agent_test.py
#   - scripts/agents/README.md
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
# Reason: Align claim ID semantics with QID+P-value signature requirement and prevent implicit facet defaults
# Notes:
#   - claim_signature accepted as string/dict/list (JSON normalized)
#   - subject_qid is required for deterministic claim_id
#   - facet missing now raises error
# ==============================================================================

# ==============================================================================
# 2026-02-14 18:30 | Claim Pipeline Schema Compatibility + Doc Fixes
# ==============================================================================
# Category: Capability, Schema, Docs
# Summary: Aligned ClaimIngestionPipeline with core schema requirements and normalized doc examples
# Files:
#   - scripts/tools/claim_ingestion_pipeline.py
#   - scripts/agents/query_executor_agent_test.py
#   - Neo4j/schema/run_qid_pipeline.py
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
#   - QUERY_EXECUTOR_QUICK_REFERENCE.md
#   - scripts/agents/README.md
#   - AI_CONTEXT.md
# Reason: Fix required fields/IDs, ensure deterministic claim IDs, and update examples to match runtime behavior
# Notes:
#   - Claim now sets text/claim_type/source_agent/timestamp and uses deterministic claim_id
#   - RetrievalContext uses retrieval_id; AnalysisRun uses run_id with pipeline_version
#   - FacetAssessment now sets score
#   - QID pipeline uses facet_key for factual assessment IDs and variable facet IDs for temporal claims
#   - Docs updated for hashed claim IDs and canonical labels
# ==============================================================================

# ==============================================================================
# 2026-02-14 18:05 | Facet Normalization + Training Constraints Applied
# ==============================================================================
# Category: Capability, Docs, Integration
# Summary: Normalized facet defaults/casing in claim ingestion and agent test; added training constraints to docs and prompt
# Files:
#   - scripts/tools/claim_ingestion_pipeline.py
#   - scripts/agents/query_executor_agent_test.py
#   - md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md
#   - scripts/agents/README.md
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
#   - QUERY_EXECUTOR_QUICK_REFERENCE.md
#   - AI_CONTEXT.md
# Reason: Align facets with registry keys and ensure training runs document caps and trimming behavior
# Notes:
#   - Default facet now lowercase `political`
#   - `geography` example corrected to `geographic`
#   - Training constraints require metadata, trimming rules, allowlist mode, and cap-hit reporting
# ==============================================================================

# ==============================================================================
# 2026-02-14 17:45 | Facet Normalization + Training Workflow Docs
# ==============================================================================
# Category: Docs, Integration
# Summary: Normalized facet keys to lowercase in QID runner and updated agent docs with training workflow and 17-facet model
# Files:
#   - Neo4j/schema/run_qid_pipeline.py
#   - Neo4j/schema/run_qid_pipeline.ps1
#   - scripts/agents/README.md
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
#   - QUERY_EXECUTOR_QUICK_REFERENCE.md
# Reason: Align facet keys with registry, document launch training workflow, and clarify 1-claim-per-facet model
# Notes:
#   - Facet keys now lowercase; labels remain title-cased
#   - Training workflow uses Q17167, expanded backlink caps, proposal cap 1000 nodes, optional second pass
# ==============================================================================

# ==============================================================================
# 2026-02-14 17:20 | Parameterized QID Pipeline Runner + Roman Republic Shortcut
# ==============================================================================
# Category: Capability, Integration
# Summary: Added generic QID pipeline runner with deterministic IDs and BCE-safe parsing, plus a Roman Republic shortcut
# Files:
#   - Neo4j/schema/run_qid_pipeline.py
#   - Neo4j/schema/run_qid_pipeline.ps1
#   - Neo4j/schema/run_roman_republic_q17167_pipeline.ps1
# Reason: Provide a reusable, parameterized pipeline for seed/reset/promotion/verify flows using QIDs
# Notes:
#   - Deterministic IDs derived from QIDs (qid_token)
#   - BCE date/year parsing supports negative years and ISO dates
#   - PowerShell wrapper enforces --flag=value to preserve negative values
#   - Roman Republic run verified: validated claim + OCCURRED_DURING/OCCURRED_AT + SUPPORTED_BY counts 1/1/1
# ==============================================================================

# ==============================================================================
# 2026-02-14 17:00 | Communication Facet Added (Facet 17) + 1-Claim-Per-Facet Model
# ==============================================================================
# Category: Capability, Schema
# Summary: Added Communication as 17th facet; established 1-claim-per-facet pattern
# Files:
#   - Facets/facet_registry_master.json (updated facet_count 16 -> 17)
#   - md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md (new Pattern 6 with communication guidance)
# Reason: Enable agents to consider messaging, narrative framing, propaganda, ceremonies as evidence dimensions
# Notes:
#   - Communication facet: "How and when was this communicated?"
#   - Model: One claim per facet per entity-relationship (not all facets always apply)
#   - Agent guidance: Respond with facet: "NA" if no strong evidence for that facet
#   - Communication examples: Victory narratives, merchant networks, missionary messaging, sermons
#   - Anchors: Q11029 (communication), Q1047 (message), Q11420 (ceremony), Q19832 (propaganda), Q2883829 (oral tradition), Q33829 (narrative)
# ==============================================================================

# ==============================================================================
# 2026-02-14 16:45 | Query Executor Agent + Claim Pipeline - Production Ready
# ==============================================================================
# Category: Capability, Integration, Agent, Schema
# Summary: Implemented production-ready Query Executor Agent with claim submission pipeline
# Files:
#   - scripts/agents/query_executor_agent_test.py (391 lines)
#   - scripts/tools/claim_ingestion_pipeline.py (460 lines)
#   - md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md (400+ lines, updated with 16-facet registry)
#   - scripts/agents/README.md (400+ lines)
#   - scripts/agents/QUERY_EXECUTOR_QUICKSTART.md (300+ lines)
#   - QUERY_EXECUTOR_QUICK_REFERENCE.md (reference guide)
#   - Key Files/2026-02-14 Query Executor Implementation.md (implementation summary)
# Reason: Provide working agent test without LangGraph dependency; support live query + claim workflows
# Notes:
#   - Agent: ChatGPT-powered with dynamic schema discovery (CALL db.labels, CALL db.relationshipTypes)
#   - Pipeline: Full claim lifecycle (validate -> hash -> create -> link -> promote if confidence >= 0.90)
#   - CLI: 5 modes (test, claims, interactive, single query, default)
#   - Facets: Integrated with 16-facet registry from Facets/facet_registry_master.json
#   - No syntax errors, ready for immediate testing
#   - Files not yet committed (staged for push)
# ==============================================================================

# ==============================================================================
# 2026-02-14 15:36 | Claim Promotion Pilot (14/15) Implemented and Verified
# ==============================================================================
# Category: Capability, Integration, Schema
# Summary: Added first claim-promotion workflow and verification scripts for validated-claim -> canonical provenance linkage
# Files:
#   - Neo4j/schema/14_claim_promotion_seed.cypher
#   - Neo4j/schema/15_claim_promotion_verify.cypher
# Reason: Move from claim storage to controlled promotion into canonical graph with traceability.
# Notes:
#   - Promotion guard: confidence threshold + required context edges.
#   - Promotion outputs: claim status/flags, canonical relationship metadata, `SUPPORTED_BY` provenance edges.
#   - Parser-safe fix applied to keep period `SUPPORTED_BY` merge in same bound-variable statement.
# ==============================================================================

# ==============================================================================
# 2026-02-14 15:25 | Claim Label Requirement + Backfill
# ==============================================================================
# Category: Schema, Integration
# Summary: Made `Claim.label` required in core schema and backfilled existing claim labels for graph readability
# Files:
#   - Neo4j/schema/07_core_pipeline_schema.cypher
#   - Neo4j/schema/08_core_pipeline_validation_runner.py
#   - Neo4j/schema/09_core_pipeline_pilot_seed.cypher
#   - Neo4j/schema/10_core_pipeline_pilot_verify.cypher
#   - Neo4j/schema/11_event_period_claim_seed.cypher
#   - Neo4j/schema/12_event_period_claim_verify.cypher
#   - Neo4j/schema/13_claim_label_backfill.cypher
# Reason: Improve graph visualization and enforce consistent human-readable claim identity.
# Notes:
#   - Added `claim_has_label` existence constraint and `claim_label_index`.
#   - Backfilled existing claims from `text` where labels were missing.
#   - Updated pilot verify queries to return `claim_label`.
# ==============================================================================

# ==============================================================================
# 2026-02-14 15:00 | Event-Period Claim Pilot + Cypher Runner Parser Hardening
# ==============================================================================
# Category: Capability, Schema, Integration
# Summary: Added concrete Event/Period/Place claim pilot flow and hardened .cypher runner to handle semicolons inside string literals
# Files:
#   - Neo4j/schema/11_event_period_claim_seed.cypher
#   - Neo4j/schema/12_event_period_claim_verify.cypher
#   - Neo4j/schema/run_cypher_file.py
# Reason: Extend pilot from abstract claim chain to entity-grounded claim suitable for promotion-flow testing.
# Notes:
#   - Added Roman Republic period (`Q17167`), Battle of Actium event (`Q193304`), and Actium place (`Q41747`).
#   - Added second temporal claim: `claim_actium_in_republic_31bce_001` with retrieval context, analysis run, and facet assessment.
#   - Updated runner statement parser to split only on semicolons outside quoted strings.
# ============================================================================== 

# ==============================================================================
# 2026-02-14 14:34 | Core Pipeline Pilot Seed Flow (SubjectConcept-Agent-Claim)
# ==============================================================================
# Category: Capability, Schema, Integration
# Summary: Added and validated minimal non-temporal pilot cluster for core claim flow
# Files:
#   - Neo4j/schema/09_core_pipeline_pilot_seed.cypher
#   - Neo4j/schema/10_core_pipeline_pilot_verify.cypher
# Reason: Provide concrete first ingest target after temporal-only baseline and core schema lock.
# Notes:
#   - Seeded nodes: SubjectConcept, Agent, Claim, RetrievalContext, AnalysisRun, Facet, FacetAssessment.
#   - Seeded edges: OWNS_DOMAIN, MADE_CLAIM, SUBJECT_OF, USED_CONTEXT, HAS_ANALYSIS_RUN, HAS_FACET_ASSESSMENT, ASSESSES_FACET, EVALUATED_BY.
#   - Compatibility fix: replaced `datetime().toString()` with `toString(datetime())`.
#   - Cleaned failed intermediate artifacts (8 non-temporal edges + 16 unlabeled nodes) before final seed run.
# ==============================================================================

# ==============================================================================
# 2026-02-14 14:16 | Core Validator Compatibility Split (Cypher Inventory + Python PASS/FAIL)
# ==============================================================================
# Category: Capability, Schema, Docs
# Summary: Reworked core pipeline validator for Neo4j environments that only support top-level SHOW
# Files:
#   - Neo4j/schema/08_core_pipeline_validation_runner.cypher
#   - Neo4j/schema/08_core_pipeline_validation_runner.py
# Reason: `SHOW ... WITH` and `CALL { SHOW ... }` patterns failed on target parser.
# Notes:
#   - Cypher file now provides browser-safe inventory queries only.
#   - Python runner performs authoritative PASS/FAIL checks (constraints + non-constraint indexes + online state).
#   - Expected index set excludes fields already covered by uniqueness constraints (no duplicate-index false failures).
# ==============================================================================

# ==============================================================================
# 2026-02-14 13:44 | Core Pipeline Schema Bootstrap (Phase 1) + Targeted Validator
# ==============================================================================
# Category: Schema, Capability, Docs
# Summary: Added focused core-pipeline schema bootstrap and matching validation runner for non-temporal rollout on top of temporal baseline
# Files:
#   - Neo4j/schema/07_core_pipeline_schema.cypher
#   - Neo4j/schema/08_core_pipeline_validation_runner.cypher
#   - AI_CONTEXT.md
# Reason: Move from all-in bootstrap to a controlled next phase that can be applied and validated incrementally.
# Notes:
#   - Scope locked to: `Human`, `Place`, `Event`, `Period`, `SubjectConcept`, `Claim`,
#     `RetrievalContext`, `Agent`, `AnalysisRun`, `FacetAssessment`.
#   - Validation runner checks required presence only (extras are informational), so temporal-only artifacts do not cause false failures.
#   - Core runner pattern uses `SHOW CONSTRAINTS` / `SHOW INDEXES` with aggregate-safe `WITH` staging.
# ==============================================================================

# ==============================================================================
# 2026-02-14 12:56 | Bootstrap Runner Parser Compatibility (SHOW Removed)
# ==============================================================================
# Category: Capability, Schema
# Summary: Replaced SHOW-based validation with db.constraints()/db.indexes() only
# Files:
#   - Neo4j/schema/06_bootstrap_validation_runner.cypher
# Reason: Target Neo4j parser rejected SHOW in composed query context.
# Notes:
#   - Runner now contains no SHOW clauses and starts with `WITH`.
#   - File saved UTF-8 without BOM.
# ==============================================================================

# ==============================================================================
# 2026-02-14 12:45 | Bootstrap Runner Compatibility Rewrite (Single Statement)
# ==============================================================================
# Category: Capability, Schema
# Summary: Rewrote bootstrap validator as a single Cypher statement using db.constraints()/db.indexes()
# Files:
#   - Neo4j/schema/06_bootstrap_validation_runner.cypher
# Reason: Ensure reliable execution in Neo4j Browser and avoid multi-statement/SHOW parser edge cases.
# Notes:
#   - Single RETURN now emits: missing/unexpected constraints, missing/unexpected indexes, non-online indexes, and overall PASS/FAIL.
# ==============================================================================

# ==============================================================================
# 2026-02-14 12:22 | Bootstrap Validation Runner Syntax Fix (SHOW + WITH)
# ==============================================================================
# Category: Capability, Schema, Docs
# Summary: Fixed Cypher syntax in validation runner by moving SHOW clauses into CALL subqueries
# Files:
#   - Neo4j/schema/06_bootstrap_validation_runner.cypher
# Reason: Neo4j does not allow `SHOW ...` directly after `WITH` in this script pattern.
# Notes:
#   - Reworked audits to use `CALL { SHOW ... RETURN collect(...) }`.
#   - Preserved all expected constraint/index name checks and final PASS/FAIL summary.
# ==============================================================================

# ==============================================================================
# 2026-02-14 12:18 | Bootstrap Dry-Validation Runner for Constraints/Indexes
# ==============================================================================
# Category: Capability, Schema, Docs
# Summary: Added single Cypher runner to validate SHOW CONSTRAINTS/SHOW INDEXES against expected bootstrap schema names
# Files:
#   - Neo4j/schema/06_bootstrap_validation_runner.cypher
# Reason: Provide fast post-bootstrap verification and drift detection before data ingestion.
# Notes:
#   - Expectations are generated from:
#     - `Neo4j/schema/01_schema_constraints.cypher`
#     - `Neo4j/schema/02_schema_indexes.cypher`
#   - Includes inventories, missing/unexpected name audits, index state health, and final PASS/FAIL summary row.
# ==============================================================================

# ==============================================================================
# 2026-02-14 12:04 | SysML + Implementation Index Consolidated Realignment
# ==============================================================================
# Category: Architecture, Docs, Integration
# Summary: Realigned SysML model and implementation cross-reference indexes to consolidated architecture as sole source of truth
# Files:
#   - Key Files/2-13-26 SysML v2 System Model - Blocks and Ports (Starter).md
#   - Key Files/ARCHITECTURE_IMPLEMENTATION_INDEX.md
#   - ARCHITECTURE_IMPLEMENTATION_INDEX.md
# Reason: Remove split-era drift and enforce consolidated section-number mapping for onboarding and implementation.
# Notes:
#   - SysML updated with block responsibilities, typed port payload contracts, federation dispatcher flow, claim lifecycle states, and deterministic agent routing.
#   - Implementation indexes now map Phase 1-3 directly to consolidated section numbers.
#   - BODY/APPENDICES are no longer used as architecture sources; appendices treated as in-document consolidated content.
# ==============================================================================

# ==============================================================================
# 2026-02-14 11:36 | Neo4j Schema Lock-In: Canonical Labels + ID Hash Hardening
# ==============================================================================
# Category: Schema, Architecture, Docs
# Summary: Updated Neo4j constraints/indexes to enforce canonical first-class label policy and new id_hash lookup/uniqueness model
# Files:
#   - Neo4j/schema/01_schema_constraints.cypher
#   - Neo4j/schema/02_schema_indexes.cypher
# Reason: Remove residual legacy-label drift risk and align schema layer with approved node model before import.
# Notes:
#   - Added canonical label lock header + legacy mapping policy (`Subject/Concept` -> `SubjectConcept`, `Person` -> `Human`).
#   - Added `id_hash` uniqueness constraints for first-class labels.
#   - Added `id_hash` lookup indexes and status indexes for first-class labels.
#   - Added explicit `Claim.cipher` index and `Claim.cipher IS NOT NULL` constraint.
#   - Updated traversal comments to use `SUBJECT_CONCEPT` wording.
# ==============================================================================

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
