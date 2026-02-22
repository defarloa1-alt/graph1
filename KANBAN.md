# Chrystallum Project Kanban Board

**Last Updated:** 2026-02-22  
**PM:** AI PM Agent  
**Discipline:** Update KANBAN.md + REQUIREMENTS.md in same commit

---

## In Progress

- [ ] **Schema Naming Alignment (ADR-005)** #high @architect
  - **BLOCKING:** Entity scaling Phase 2
  - **Issue:** Meta-model uses "Human", cipher spec uses "PERSON"
  - **Decision Needed:** Architect chooses canonical standard
  - **Recommended:** Keep "PERSON" (matches cipher spec)
  - **Tasks:** Create ADR-005 → Dev implements → QA validates
  - **Effort:** 2-3 hours total (1-2h decision, 1h implementation)
  - **Priority:** HIGH (Stakeholder escalated)
  - **Assigned:** Graph Architect (decision), Dev (implementation)

- [x] **Entity Scaling Phase 1: Complete!** 300 → 2,600 ✅
  - **MILESTONE ACHIEVED:** 2,600 entities imported
  - **QA VERIFIED:** All checks pass
  - Growth: 8.67x increase
  - **Paused for:** Schema naming fix
  
- [ ] **Entity Scaling Phase 2: 2,600 → 5,000** #high @dev
  - **Status:** ON HOLD (waiting for schema alignment)
  - Current: 2,600 entities (26% of target)
  - Next checkpoint: 5,000 entities (50% of target)
  - Will resume after schema fix
  - Effort: ~5 hours autonomous

---

## Ready

- [ ] **Implement Pydantic Validation Models** #high @dev
  - Files: PYDANTIC_MODELS_SPECIFICATION.md
  - Deliverables: scripts/models/entities.py, claims.py
  - Effort: 2-3 hours
  - Depends on: DDL execution complete
  
- [ ] **REQ-FUNC-005: Period Discovery (Phase 1)** #high @dev
  - Tag existing temporal anchors
  - Harvest pure periods (100-200)
  - PeriodO alignment
  - Effort: 5 hours total

- [ ] **REQ-FUNC-006: Entity Scaling to 10K** #medium @dev
  - Target: 300 → 10,000 entities
  - Domains: Roman, Greek, Egyptian, Medieval, Hellenistic
  - Depends on: Legacy cipher migration
  - Effort: ~15 hours autonomous

- [ ] **REQ-FUNC-007: SFA Prompt Library** #medium @dev
  - Current: 3/18 prompts
  - Target: 18/18 prompts
  - Template-based generation
  - Effort: 4 hours

---

## Review

- [ ] **Architect Mid-Priority Design** (Incoming)
  - Status: Architect working on it
  - Priority: Medium
  - Waiting for: Architect to complete and update AI_CONTEXT

- [ ] **7 Backfilled Requirements** (APPROVED, awaiting formal review)
  - REQ-FUNC-002: Tier 1 Entity Cipher
  - REQ-FUNC-003: Tier 2 Faceted Cipher
  - REQ-FUNC-004: Authority Cascade
  - REQ-PERF-001: O(1) Performance
  - REQ-DATA-001: Entity Type Registry
  - REQ-DATA-002: Facet Registry
  - REQ-DATA-003: Cipher Qualifiers

---

## Backlog

- [ ] REQ-UI-001: Faceted Timeline Visualization
- [ ] REQ-FUNC-009: Geographic Coverage Claims
- [ ] Claims Architecture Implementation
- [ ] Perplexity Period Classification
- [ ] Domain Ontology Expansion (Greek, Egyptian, etc.)
- [ ] MCP Testing and Activation
- [ ] Git Push Retry (54 commits)

---

## Done

- [x] **REQ-DATA-004 Phase 1: CONCEPT Added to Registry** ✅ COMPLETE (2026-02-22)
  - Added to entity_cipher.py as DEPRECATED
  - Validates 258 current CONCEPT entities
  - Delivered by: Dev Agent
  - Verified by: QA Agent

- [x] **DDL Addendum Execution** ✅ COMPLETE (2026-02-22)
  - 13/13 statements executed
  - TemporalAnchor: 3 constraints + 3 indexes
  - Qualifiers: 7 indexes
  - Database: 79 constraints, 81 indexes total
  - Delivered by: Dev Agent
  - Verified by: QA Agent

- [x] **ADR-004: Legacy CONCEPT Type Handling** ✅ APPROVED (2026-02-22)
  - Decision: Add CONCEPT as deprecated type
  - Phased migration plan (incremental, not blocking)
  - Stakeholder approved
  - Delivered by: Graph Architect

- [x] **Graph Architecture Specifications** ✅ COMPLETE (2026-02-22)
  - NEO4J_SCHEMA_DDL_COMPLETE.md (850 lines)
  - PYDANTIC_MODELS_SPECIFICATION.md (950 lines)
  - TIER_3_CLAIM_CIPHER_ADDENDUM.md (700 lines)
  - ADR-002: TemporalAnchor multi-label pattern
  - ADR-003: Temporal scope derivation
  - DEV_AGENT_SCHEMA_EXECUTION_GUIDE.md
  - Delivered by: Graph Architect Agent

- [x] **Architecture Backfill** (7 requirements documented)
  - Requirements extracted from Entity Cipher architecture
  - Formalized existing implementations
  - Delivered by: Requirements Analyst
  
- [x] **Data Dictionary** ✅ COMPLETE
  - Complete data model documented
  - Controlled vocabularies
  - Authority sources

- [x] **REQ-FUNC-001: Idempotent Entity Import** ✅ VERIFIED
  - 300 unique entities
  - No duplicates
  - Constraints in place (entity_cipher_unique, entity_qid_unique)
  - 10/10 tests PASS
  
- [x] **REQ-FUNC-010: Entity Relationship Import** ✅ VERIFIED
  - 1,568 relationships
  - 81.7% connectivity
  - 10 relationship types
  - 6/6 tests PASS
  
- [x] **System Architecture** (Chrystallum + 4 branches)
  - Self-describing system
  - 48,920 nodes
  - Federation + Entity + Facet + SubjectConcept roots
  
- [x] **Roman Republic Ontology** (79 SubjectConcepts)
  - 6 authority-federated
  - 3 agents created
  
- [x] **Documentation Decomposition** (27 files + 26 appendices)
  
- [x] **Python SCA Agent** (operational)

---

## Metrics

**Entities:** 2,600 / 10,000 (26%) ⚡ **8.67x GROWTH**  
**Relationships:** 1,568 / 50,000 (3%) - Next: Import for new 2,300 entities  
**Connectivity:** 81.7% (target: 90%)  
**Domains:** 1 / 5 (20%)  
**SFA Prompts:** 3 / 18 (17%)  
**Requirements VERIFIED:** 2 / 15 (13%)  
**Architecture Specs:** 3 major deliverables ✅

**Velocity:** 2,600 entities in 1 session! 🚀

**Latest:**
- 🎉 **MAJOR MILESTONE:** 2,600 entities imported (QA VERIFIED)
- ✅ Dev scaling successful (300 → 2,600)
- ✅ Ready for next phase (2,600 → 5,000)

---

## Critical Issues

**✅ #1: CONCEPT Type Drift** - RESOLVED Phase 1 (2026-02-22)
- ~~258 entities (86%!) use deprecated "CONCEPT" type~~
- **Resolution:** CONCEPT added to registry as DEPRECATED ✅
- **Status:** Phase 1 complete, Phases 2-3 during entity scaling
- **Impact:** Database now valid, migration planned
- **Found By:** Graph Architect → **Resolved By:** Dev + QA

**✅ #2: MIGRATION NOT GREENFIELD** - RESOLVED (2026-02-22)
- ~~Database has existing constraints/indexes~~
- **Resolution:** DDL used IF NOT EXISTS ✅
- **Status:** 79 constraints, 81 indexes active, no conflicts
- **Impact:** Schema safe, no overwrites
- **Found By:** Graph Architect → **Resolved By:** Dev

**⚠️ #3: MERGE + Label Interaction** - DOCUMENTED (Active)
- Neo4j doesn't auto-add labels on MERGE MATCH
- **Action:** Dev must explicitly SET :TemporalAnchor in code
- **Status:** Documented in DDL spec §5 for Dev reference
- **Impact:** Dev must implement correctly (not a blocker, a pattern)
- **Reference:** NEO4J_SCHEMA_DDL_COMPLETE.md §5

**All Critical Blockers Resolved** ✅  
**Remaining:** Implementation pattern (#3) - not a blocker

---

## Notes

**Current Sprint:** Entity Scaling (UNBLOCKED)  
**Critical Path:** Entity scaling → Period discovery → Claims  
**Blockers:** None ✅ (All resolved)  
**Success Rate:** 100% (2/2 requirements verified)  
**Schema State:** 79 constraints, 81 indexes, ready for scale

**Update Discipline:**
- KANBAN.md + REQUIREMENTS.md updated in same commit
- Keep boards in sync
- No drift between documents
