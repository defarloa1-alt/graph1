# Chrystallum - Comprehensive Project Management Plan

**Project Manager:** AI PM Agent  
**Date:** February 20, 2026  
**Based on:** Complete documentation review (230+ files) + AI_CONTEXT analysis  
**Current Phase:** Foundation → Entity Loading & Quality

---

## 🎯 **EXECUTIVE SUMMARY**

### **Project Health: 8.5/10**

**What's Working:**
- ✅ **Architecture:** Complete, modular, self-describing (9/10)
- ✅ **Documentation:** 230+ files, well-organized (8.5/10)
- ✅ **Foundation:** Neo4j Aura with 48,920 nodes, clean (10/10)
- ✅ **SCA Agent:** Production-ready, tested (9/10)
- ✅ **Processes:** Requirements framework, QA testing (8/10)

**What Needs Attention:**
- 🔴 **CRITICAL BLOCKER:** REQ-FUNC-001 missing constraints (prevents scaling)
- 🟡 **SFA Prompts:** Only 3/18 complete (17% vs 100% needed)
- 🟡 **Entity Count:** 300 entities (0.3% of 100K target)
- 🟡 **Git Push:** 42 commits stuck locally
- 🟡 **MCP:** Configured but not tested

---

## 📊 **CURRENT STATE ANALYSIS**

### **Documentation Maturity: 8.5/10**

**Strengths:**
- 27 modular architecture files (Feb 19 decomposition)
- 26 appendices in 6 thematic clusters
- Comprehensive agent documentation (SCA excellent)
- Active requirements framework (Feb 21)
- Complete QA test suite

**Gaps Identified:**
- 2 missing appendices (BabelNet, SFA Workflow)
- 15 missing SFA prompts (3/18 complete)
- Agent Use Case Matrix needs update (17→18)
- Facet casing inconsistency in docs
- Some consolidation status unclear

### **Implementation Maturity: 6/10**

**Completed:**
- ✅ Neo4j Aura instance (clean architecture)
- ✅ Temporal backbone (4,025 years)
- ✅ Geographic backbone (41,993 places)
- ✅ Subject ontology (79 concepts, 1 domain)
- ✅ Python SCA agent (operational)

**In Progress:**
- 🟡 Entity loading (300/10,000 - 3%)
- 🟡 REQ-FUNC-001 (COMPLETED but constraints missing)
- 🟡 SFA development (3/18 prompts)

**Not Started:**
- ⏳ Period discovery (ready, not executed)
- ⏳ Claims architecture (designed, not built)
- ⏳ Multi-domain expansion (1/5 domains)

---

## 🚨 **CRITICAL PATH & BLOCKERS**

### **BLOCKER #1: Missing Uniqueness Constraints** 🔴

**Issue:** REQ-FUNC-001 implemented MERGE but forgot constraints  
**Impact:** HIGH - Database unprotected, duplicates possible  
**Status:** QA identified, waiting for Dev to add 2 constraints  
**ETA:** 15 minutes  
**Priority:** **URGENT - DO NOW**

**Action Required:**
```cypher
CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
  FOR (e:Entity) REQUIRE e.entity_cipher IS UNIQUE;

CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS
  FOR (e:Entity) REQUIRE e.qid IS UNIQUE;
```

**Then:** QA re-verifies (test 5 should pass), marks VERIFIED

---

### **BLOCKER #2: Git Push Failure** 🟡

**Issue:** 42 commits stuck locally (network timeout)  
**Impact:** MEDIUM - Work safe but not backed up remotely  
**Mitigation:** Commits are local, can recover  
**Action:** Try smaller batches or wait for better network

---

### **BLOCKER #3: SFA Prompt Gap** 🟡

**Issue:** Only 3/18 SFA prompts complete (17% coverage)  
**Impact:** MEDIUM - Limits agent creation to 3 facets  
**Action:** Create remaining 15 prompts (template-based, 1-2 hours)

---

## 📅 **3-PHASE ROADMAP**

### **PHASE 1: Quality & Foundation [95% COMPLETE]**

**Target:** Production-ready architecture + clean data  
**Duration:** Completed + 1 day for constraints  
**Status:** 🟡 Nearly complete, critical constraint missing

**Remaining Work:**
- 🔴 Add uniqueness constraints (15 min) - **URGENT**
- 🟡 Fix Agent Use Case Matrix (17→18)
- 🟡 Standardize facet casing in docs
- 🟡 Push 42 commits to GitHub

**Deliverables:**
- ✅ Self-describing system (Chrystallum + 4 branches)
- ✅ Clean architecture (48,920 nodes, canonical)
- ✅ Python SCA agent (operational)
- ⏳ Database constraints (2 missing)

**ETA to Phase 1 Complete:** 1 day

---

### **PHASE 2: Entity Scale & Multi-Domain [3% COMPLETE]**

**Target:** 10,000 entities across 5 domains  
**Duration:** 2-3 weeks  
**Status:** 🟡 Started (300 entities), blocked by constraints

**Track 2A: Entity Import Pipeline (CRITICAL PATH)**
```
Current: 300 entities (Roman Republic)
Target: 10,000 entities
Blocker: Constraints missing
Progress: 3% (300/10,000)

Week 1: Fix constraints → Import 2,500 entities (Roman deep dive)
Week 2: Import 7,500 more entities (4 new domains)
```

**Track 2B: Domain Ontology Expansion (PARALLEL)**
```
Current: 1 domain (Roman Republic, 79 concepts)
Target: 5 domains (400 concepts total)
Progress: 20% (1/5 domains)

Week 1: Create 2 domain ontologies (Greece, Egypt)
Week 2: Create 2 more (Medieval, Hellenistic)
```

**Track 2C: SFA Prompt Library (PARALLEL)**
```
Current: 3/18 SFA prompts (MILITARY, BIOGRAPHIC, COMMUNICATION)
Target: 18/18 complete
Progress: 17%

Week 1: Create 8 more prompts (template-based)
Week 2: Create remaining 7 prompts
```

**Dependencies:**
- 2A blocks entity scaling until constraints added
- 2B and 2C can proceed in parallel

**ETA to Phase 2 Complete:** 3 weeks (1 day + 2-3 weeks)

---

### **PHASE 3: Period Discovery & Claims [DESIGNED, NOT STARTED]**

**Target:** 1,000 classified periods + Claims architecture  
**Duration:** 3-4 weeks  
**Status:** ⏳ Ready to start

**Track 3A: Period Discovery (Ready to Start)**
```
Method: Wikidata backlinks → Perplexity classification
Input: Seed QIDs (Q11756, Q12554, Q17167, etc.)
Output: 500-1,000 validated Period nodes
Tool: Python SCA (scripts/agents/sca_agent.py)

Week 1: Harvest backlinks (500 candidates)
Week 2: Classify with Perplexity (period types)
Week 3: Map to PeriodO (match existing)
Week 4: Review & load approved periods
```

**Track 3B: Claims Architecture Implementation**
```
Prerequisite: 10,000+ entities (Phase 2 complete)
Architecture: Complete (ADR-001, ADR-005)
Implementation: Not started

Week 1: Implement Claim node creation
Week 2: FacetPerspective star pattern
Week 3: Evidence linking & provenance
Week 4: Agent coordination (SCA → SFA)
```

**Dependencies:**
- 3A can start immediately (parallel with Phase 2)
- 3B blocked by Phase 2 completion

**ETA to Phase 3 Complete:** 4 weeks (can overlap with Phase 2)

---

## 🎯 **SPRINT PLAN: NEXT 14 DAYS**

### **Sprint 1: Critical Path & Parallel Work (Days 1-7)**

**Day 1: URGENT - Constraints**
- 🔴 Add uniqueness constraints (15 min)
- 🔴 QA verify (30 min)
- 🔴 Mark REQ-FUNC-001 VERIFIED
- **Result:** Unblocks entity scaling

**Day 1-2: Start Period Discovery**
- 🟢 Run Wikidata backlink harvesting (Python SCA)
- 🟢 Seed QIDs: Q11756, Q12554, Q17167, Q2277, Q12544
- 🟢 Harvest ~500 period candidates
- **Deliverable:** period_candidates.json

**Day 2-3: Perplexity Classification**
- 🟢 Classify period types (political, cultural, geological, etc.)
- 🟢 Infer temporal bounds
- 🟢 Calculate confidence scores
- **Deliverable:** period_proposals.json (500 periods)

**Day 3-5: Entity Scaling**
- 🟡 Import 2,500 more Roman Republic entities
- 🟡 Federation scoring
- 🟡 Link to SubjectConcept ontology
- **Target:** 2,800 total entities (10% of goal)

**Day 5-7: Domain Expansion**
- 🟡 Create Greek history ontology (SCA)
- 🟡 Create Egyptian history ontology (SCA)
- 🟡 Import 1,000 entities per domain
- **Target:** 4,800 entities, 3 domains

### **Sprint 2: Breadth & Quality (Days 8-14)**

**Day 8-10: Period Review & Loading**
- 🟢 Review 500 period proposals
- 🟢 Approve ~300 periods
- 🟢 Load to Neo4j
- 🟢 Tether to Year backbone
- **Target:** 1,377 total periods (1,077 existing + 300 new)

**Day 10-12: Continue Entity Scaling**
- 🟡 Create 2 more domain ontologies (Medieval, Hellenistic)
- 🟡 Import 2,500 entities per domain (5,000 total)
- **Target:** 9,800 entities, 5 domains

**Day 12-14: SFA Prompt Library**
- 🟡 Create 8 SFA prompts (template-based)
- 🟡 Test 3 existing SFA prompts
- **Target:** 11/18 SFA prompts (61%)

---

## 📊 **METRICS & TARGETS**

### **End of Sprint 1 (Day 7):**
- ✅ REQ-FUNC-001 VERIFIED
- 🎯 2,800 entities (10% of 10K goal)
- 🎯 500 period proposals classified
- 🎯 3 domain ontologies
- 🎯 42 commits pushed to GitHub

### **End of Sprint 2 (Day 14):**
- 🎯 9,800 entities (98% of 10K goal)
- 🎯 1,377 periods (300 new + 1,077 existing)
- 🎯 5 domain ontologies
- 🎯 11/18 SFA prompts complete

### **End of Month (Day 30):**
- 🎯 50,000 entities
- 🎯 2,000 periods
- 🎯 10 domains
- 🎯 18/18 SFA prompts
- 🎯 Claims architecture operational

---

## 🛠️ **RESOURCE ALLOCATION**

### **Agent Assignments:**

**Dev Agent (High Utilization):**
- 🔴 REQ-FUNC-001 constraints (15 min) - **NOW**
- 🟡 Entity import scaling (ongoing)
- 🟡 Claims implementation (Phase 3)

**QA Agent (Medium Utilization):**
- 🔴 Verify REQ-FUNC-001 (30 min) - After Dev
- 🟡 Regression testing (as entities scale)
- 🟡 Claims testing (Phase 3)

**SCA Agent (High Utilization):**
- 🟢 Period discovery (ongoing)
- 🟢 Domain ontology creation (parallel)
- 🟢 Authority enrichment

**Requirements Analyst (Low Utilization):**
- ⏳ Standby for next business requirement
- 🟡 Documentation updates as needed

**PM (This Role):**
- 📊 Daily coordination via AI_CONTEXT.md
- 📊 Sprint tracking
- 📊 Risk mitigation
- 📊 Tooling setup

---

## 🎯 **IMMEDIATE ACTION PLAN (Next 4 Hours)**

### **Hour 1: Critical Path Resolution**
```
WHO: Dev Agent
WHAT: Add 2 uniqueness constraints
WHY: Unblocks entity scaling (CRITICAL)
HOW: Run Cypher commands in Neo4j
WHERE: AI_CONTEXT.md lines 76-86 for exact commands
TIME: 15 minutes
```

### **Hour 1-2: QA Verification**
```
WHO: QA Agent
WHAT: Re-verify REQ-FUNC-001
WHY: Confirm constraints work
HOW: Run test suite, check constraints exist
RESULT: Mark VERIFIED if 5/5 tests pass
TIME: 30 minutes
```

### **Hour 2-4: Parallel Period Work (Can Start Now)**
```
WHO: SCA Agent (Python)
WHAT: Wikidata backlink harvesting
WHY: Get ahead on period discovery
HOW: Run scripts/agents/sca_agent.py
INPUT: Seed QIDs (Q11756, Q12554, Q17167)
OUTPUT: 500 period candidates
TIME: 2 hours
```

---

## 🔧 **TOOLING STRATEGY**

### **Recommended: GitHub Issues + Projects**

**Setup Plan (30 minutes):**

1. **Create GitHub Project**
   - Name: "Chrystallum Development"
   - Template: Board
   - Columns: Backlog, Ready, In Progress, Review, Done

2. **Convert Requirements to Issues**
   - REQ-FUNC-001 → Issue #1
   - Future requirements → Issues #2, #3, etc.
   - Label by priority (critical, high, medium, low)
   - Milestone by phase (Phase 2, Phase 3, etc.)

3. **Agent Workflow**
   - Commit messages mention issues (`Fix #1`, `Closes #2`)
   - AI_CONTEXT.md references issue numbers
   - Weekly board review

**Benefits:**
- ✅ Visual kanban board
- ✅ Integrated with git
- ✅ Free, no external tools
- ✅ AI agents can update via commits

**Keep:**
- AI_CONTEXT.md for agent handoffs (detailed context)
- GitHub Issues for task tracking (structured)
- Hybrid approach = best of both

---

## 📋 **DETAILED WORK BREAKDOWN**

### **Workstream 1: Quality & Stability (CRITICAL)**

**Owner:** Dev + QA Agents  
**Goal:** Production-ready import pipeline

| Task | Owner | ETA | Status | Blocking |
|------|-------|-----|--------|----------|
| Add constraints | Dev | 15m | 🔴 URGENT | YES |
| Verify constraints | QA | 30m | ⏳ After Dev | - |
| Test idempotent import | QA | 1h | ⏳ After Dev | - |
| Push commits to GitHub | PM | 1h | 🟡 Retry | - |
| Test MCP in Cursor | PM | 15m | ⏳ | - |

**Total:** 3 hours to unblock critical path

---

### **Workstream 2: Period Discovery (READY TO START)**

**Owner:** SCA Agent (Python)  
**Goal:** 500-1,000 classified periods

| Task | Tool | ETA | Status | Blocking |
|------|------|-----|--------|----------|
| Backlink harvesting | Python SCA | 2h | 🟢 Can start now | NO |
| Perplexity classification | Perplexity API | 3h | ⏳ After harvest | - |
| PeriodO mapping | Python | 2h | ⏳ After classify | - |
| Review & approve | Human | 2h | ⏳ After mapping | - |
| Load to Neo4j | Python | 1h | ⏳ After approve | - |

**Total:** 10 hours over 3-5 days (can start immediately)

---

### **Workstream 3: Entity Scaling (BLOCKED)**

**Owner:** Dev Agent + SCA  
**Goal:** Scale from 300 → 10,000 entities

| Task | Owner | ETA | Status | Blocking |
|------|------|-----|--------|----------|
| Roman deep dive | SCA | 5h | ⏳ | Constraints |
| Greek entities | SCA | 5h | ⏳ | Constraints |
| Egyptian entities | SCA | 5h | ⏳ | Constraints |
| Medieval entities | SCA | 5h | ⏳ | Constraints |
| Hellenistic entities | SCA | 5h | ⏳ | Constraints |

**Total:** 25 hours (5 days) - **BLOCKED until constraints added**

---

### **Workstream 4: SFA Development (PARALLEL)**

**Owner:** Requirements Analyst or designated agent  
**Goal:** 18/18 SFA prompts

| Task | ETA | Status |
|------|-----|--------|
| Template SFA prompt | 1h | ⏳ |
| Create 15 prompts from template | 8h | ⏳ |
| Test 3 existing prompts | 2h | ⏳ |
| Document in architecture | 2h | ⏳ |

**Total:** 13 hours (2 days) - Can start anytime

---

### **Workstream 5: Documentation Cleanup (LOW PRIORITY)**

**Owner:** PM or designated agent  
**Goal:** Consistency and completeness

| Task | ETA | Priority |
|------|-----|----------|
| Fix Agent Use Case Matrix | 30m | 🟡 Medium |
| Standardize facet casing | 1h | 🟡 Medium |
| Clarify missing appendices | 1h | 🟢 Low |
| Update consolidation status | 30m | 🟢 Low |

**Total:** 3 hours

---

## 🎯 **SUCCESS CRITERIA**

### **This Week (Day 7):**
- ✅ REQ-FUNC-001 VERIFIED (constraints in place)
- ✅ 500 period candidates classified
- ✅ 2,800 entities loaded
- ✅ 3 domains complete
- ✅ Commits pushed to GitHub

### **This Sprint (Day 14):**
- ✅ 9,800 entities loaded
- ✅ 300 new periods approved & loaded
- ✅ 5 domains complete
- ✅ 11/18 SFA prompts complete

### **This Month (Day 30):**
- ✅ 50,000 entities
- ✅ 2,000 periods
- ✅ 10 domains
- ✅ 18/18 SFA prompts
- ✅ Claims architecture operational

---

## 📞 **COMMUNICATION PLAN**

### **Daily Updates (AI_CONTEXT.md):**
- Each agent updates when task complete
- PM reads daily, identifies blockers
- Quick status checks

### **Weekly Status (AI_CONTEXT.md):**
```
WEEK OF: [Date]
PROGRESS:
- Entities: X / 10,000 (Y%)
- Periods: X / 1,000 (Y%)
- Domains: X / 5
- Requirements: X VERIFIED

BLOCKERS:
- List any blockers

NEXT WEEK:
- Planned work
```

### **GitHub Issues (When Setup):**
- Each requirement = Issue
- Sprints = Milestones
- Labels = Priority + Phase
- Agents update via commit messages

---

## ⚠️ **RISK REGISTER**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Constraints not added | HIGH | LOW | PM monitoring, clear instructions |
| Git push continues failing | MEDIUM | MEDIUM | Retry smaller batches, accept partial |
| Perplexity API costs high | MEDIUM | MEDIUM | Batch calls, cache results |
| MCP doesn't work | MEDIUM | LOW | Keep manual workflow, fix later |
| SFA prompts delay | LOW | LOW | Template-based, not blocking |
| Network dependency | LOW | MEDIUM | Local-first architecture mitigates |

---

## 🔄 **PROCESS FLOWS**

### **Requirement → Implementation Flow:**
```
1. Stakeholder → Requirements Analyst (business need)
2. Requirements Analyst → Create REQ-* in REQUIREMENTS.md
3. Stakeholder approves → Status: APPROVED
4. Requirements Analyst → Assign to Dev + QA (parallel)
5. Dev implements → Status: IN_PROGRESS → COMPLETED
6. QA verifies → Status: VERIFIED
7. All agents update AI_CONTEXT.md at each step
```

### **Entity Discovery Flow:**
```
1. SCA bootstrap from Chrystallum
2. SCA query Wikidata (backlinks/hierarchy)
3. SCA classify with Perplexity
4. SCA create proposals (JSON)
5. Human review and approve
6. SCA load to Neo4j (status='approved')
7. SCA update SubjectConceptRegistry
```

---

## 📊 **PM DASHBOARD (Updated Daily)**

**Current Sprint:** Sprint 1 (Days 1-7)  
**Sprint Goal:** Unblock critical path + start period work

**Progress:**
- Constraints: 🔴 0/2 (URGENT)
- Entities: 🟡 300/2,800 (11%)
- Periods: 🟢 0/500 (ready to start)
- Domains: 🟡 1/3 (33%)

**Velocity:** 40 commits in 12 hours (excellent)  
**Health:** 8.5/10 (good, minor issues)  
**Risk:** LOW (foundation solid)

---

## ✅ **IMMEDIATE NEXT STEPS**

**RIGHT NOW (Dev Agent):**
```cypher
-- Takes 15 minutes, unblocks everything
CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
  FOR (e:Entity) REQUIRE e.entity_cipher IS UNIQUE;

CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS
  FOR (e:Entity) REQUIRE e.qid IS UNIQUE;
```

**THEN (QA Agent):**
```
Run verification test suite
Check: 5/5 tests pass
Mark: REQ-FUNC-001 VERIFIED
```

**PARALLEL (SCA Agent - Can Start Now):**
```python
python scripts/agents/sca_agent.py
# Start period backlink harvesting
# Run while waiting for constraints
```

---

**PM PLAN COMPLETE - Ready for Team Coordination!**

**File:** `PM_COMPREHENSIVE_PLAN_2026-02-20.md`
