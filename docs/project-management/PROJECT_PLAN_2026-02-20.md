# Chrystallum Project Plan - High-Level Roadmap

**Project Manager Assessment**  
**Date:** February 20, 2026  
**Current Phase:** Foundation Complete → Entity Loading Phase  
**Status:** ON TRACK - Excellent foundation, ready for acceleration

---

## 🎯 **PROJECT STATUS ASSESSMENT**

### **Overall Health: 9/10 (EXCELLENT)**

**Strengths:**
- ✅ Solid architectural foundation (self-describing system)
- ✅ Production Neo4j instance (48,920 nodes, clean)
- ✅ Comprehensive documentation (27 modular architecture files)
- ✅ Working Python SCA agent (bootstrap tested)
- ✅ Requirements framework established
- ✅ Clear processes and workflows

**Risks:**
- ⚠️ 41 commits not pushed (network issues) - mitigated by local backup
- ⚠️ REQ-FUNC-001 waiting for Dev implementation (critical blocker)
- ⚠️ MCP not yet active (manual workflow, slower)
- ⚠️ Only 300 entities loaded (need 10K+ for production)

---

## 📊 **CURRENT STATE SUMMARY**

### **Neo4j Aura (f7b612a3):**
```
Nodes: 48,920
├─ System Metadata: 120 (Chrystallum architecture)
├─ Temporal: 5,102 (Year backbone + Periods)
├─ Geographic: 42,364 (Places + types)
├─ Subject: 79 (Roman Republic ontology)
└─ Entities: 300 (Roman Republic entities - QA found 50 duplicates)
```

### **Architecture Maturity:**
- ✅ **Foundation:** Complete (self-describing, registries, schemas)
- ✅ **Backbones:** Complete (temporal, geographic)
- 🟡 **Ontology:** 79 concepts (1 domain, need 5-10 more)
- 🟡 **Entities:** 300 entities (0.3% of target)
- ⏳ **Claims:** Architecture defined, not implemented
- ⏳ **Agents:** 3 sample agents (SCA framework ready)

### **Team Capacity:**
- ✅ Requirements Analyst (active)
- ⏳ Dev Agent (1 task assigned, waiting)
- ⏳ QA Agent (1 task assigned, waiting)
- ✅ SCA Agent (Python implementation ready)
- ⏳ Project Manager (you're reading this!)

---

## 🎯 **HIGH-LEVEL ROADMAP**

### **PHASE 1: Foundation [COMPLETE] ✅**
**Duration:** 12+ hours (completed Feb 19)  
**Status:** DONE

**Deliverables:**
- ✅ Neo4j Aura instance with clean architecture
- ✅ Self-describing system (Chrystallum + 4 branches)
- ✅ 10 Federations, 18 Facets, 9 Entity Types
- ✅ Temporal + Geographic backbones
- ✅ Documentation (27 files)
- ✅ Python SCA agent

---

### **PHASE 2: Entity Pipeline [IN PROGRESS] 🟡**
**Target:** 10,000 entities across 5-10 domains  
**Current:** 300 entities (1 domain)  
**Blocking Issue:** REQ-FUNC-001 (duplicate imports)

**Track 2A: Fix Import Pipeline (CRITICAL PATH)**
- ⏳ REQ-FUNC-001: Idempotent imports (Dev + QA, ~6 hours)
- ⏳ Add constraints (entity_cipher, qid uniqueness)
- ⏳ Update import scripts (MERGE pattern)
- ⏳ Verify with QA test suite

**Track 2B: Scale Entity Import (Blocked by 2A)**
- ⏳ Import 5,000 entities (Roman Republic deep dive)
- ⏳ Import 5,000 entities (4 more domains: Greece, Egypt, Medieval, etc.)
- ⏳ Enrich with federation scores
- ⏳ Link to SubjectConcept ontology

**Track 2C: Subject Ontology Expansion (Parallel)**
- ⏳ Create 4 more domain ontologies (via SCA)
- ⏳ Target: 400 SubjectConcepts across 5 domains
- ⏳ Authority enrichment (LCSH/FAST/LCC for remaining 73 concepts)

**Dependencies:**
- 2B blocked by 2A (need working import)
- 2C can proceed in parallel

**Estimated Duration:** 2-3 weeks  
**Critical Path:** 2A (6 hours) → 2B (3-5 days)

---

### **PHASE 3: Period Discovery & Classification [READY]**
**Status:** Architecture complete, SCA ready

**Track 3A: Wikidata Period Discovery**
- ⏳ Run backlink harvesting (seed: Q11756, Q12554, Q17167)
- ⏳ Discover ~500 period candidates
- ⏳ Filter: Period vs Event vs Polity
- **Tool:** Python SCA (`sca_agent.py`)

**Track 3B: Perplexity Classification**
- ⏳ Classify period types (political, cultural, geological, etc.)
- ⏳ Infer temporal bounds
- ⏳ Calculate confidence scores
- **Tool:** Perplexity API via SCA

**Track 3C: PeriodO Mapping**
- ⏳ Match Wikidata candidates to PeriodO (8,959 periods)
- ⏳ Create Period nodes (status='pending_approval')
- ⏳ User reviews and approves
- **Target:** 500-1,000 validated periods

**Dependencies:**
- Can start immediately (no blockers)
- Parallel with Phase 2

**Estimated Duration:** 1-2 weeks

---

### **PHASE 4: Claim Architecture [DESIGNED]**
**Status:** Spec complete, implementation pending

**Track 4A: Claim Pipeline**
- ⏳ Implement Claim node creation
- ⏳ FacetPerspective star pattern
- ⏳ Evidence linking
- ⏳ Provenance tracking

**Track 4B: Agent Coordination**
- ⏳ SCA → SFA handoff workflow
- ⏳ Multi-facet claim analysis
- ⏳ Approval workflow

**Dependencies:**
- Needs 10K+ entities (Phase 2 complete)
- Needs 5+ domain ontologies (Phase 2C)

**Estimated Duration:** 2-3 weeks

---

### **PHASE 5: Production Scale [FUTURE]**
**Target:** 100K+ entities, Claims, Full agent network

**Deferred until Phases 2-4 complete**

---

## 🚨 **CRITICAL PATH & BLOCKERS**

### **BLOCKER #1: REQ-FUNC-001 (Idempotent Imports)**
**Impact:** HIGH - Blocks Phase 2B (entity scaling)  
**Status:** APPROVED, waiting for Dev implementation  
**ETA:** 6 hours (4 Dev + 2 QA)  
**Action:** **DEV AGENT NEEDED NOW**

### **BLOCKER #2: Network Push Failure**
**Impact:** MEDIUM - 41 commits not on GitHub  
**Status:** Local commits safe, push pending  
**Mitigation:** Try smaller batches, remove large files  
**Action:** Retry push or accept partial push

### **BLOCKER #3: MCP Not Active**
**Impact:** MEDIUM - Manual copy-paste workflow slower  
**Status:** Configured but not tested  
**Action:** Test MCP in Cursor chat (`@neo4j RETURN 1`)

---

## 📅 **SPRINT PLANNING (Next 2 Weeks)**

### **Sprint 1: Critical Fixes & Scaling (Week 1)**

**Day 1-2: Critical Path**
- 🔴 **Priority 1:** REQ-FUNC-001 implementation (Dev + QA)
- 🔴 **Priority 2:** Test MCP connectivity
- 🟡 **Priority 3:** Push commits to GitHub

**Day 3-5: Entity Scaling**
- 🟡 Import 5,000 more Roman Republic entities
- 🟡 Verify federation scoring
- 🟡 Link to SubjectConcept ontology

**Day 6-7: Period Discovery**
- 🟢 Run Wikidata backlink harvesting
- 🟢 Classify with Perplexity
- 🟢 Create 500 Period proposals

### **Sprint 2: Breadth & Depth (Week 2)**

**Day 8-10: Domain Expansion**
- 🟡 Create 3 more domain ontologies (Greece, Egypt, Medieval)
- 🟡 Import 3,000 entities per domain (9K total)
- 🟡 Authority enrichment

**Day 11-14: Period Integration**
- 🟢 Review Period proposals (500 candidates)
- 🟢 Approve and load to Neo4j
- 🟢 Tether to Year backbone
- 🟢 Link to SubjectConcepts

---

## 🛠️ **PROJECT MANAGEMENT TOOLS**

### **Recommended: GitHub Projects + Issues**

**Why GitHub:**
- ✅ Already using GitHub for code
- ✅ Free, integrated with repo
- ✅ AI agents can update via git commits
- ✅ Kanban boards, milestones, labels

**Setup:**
```
1. Create GitHub Project in your repo
2. Columns: Backlog, Ready, In Progress, Review, Done
3. Convert requirements to Issues
4. Link to commits/PRs
5. Agents update via commit messages
```

### **Alternative: Linear.app**
- Modern issue tracker
- AI-friendly (good API)
- Clean interface
- Better for fast-moving teams

### **Alternative: Jira**
- Enterprise-grade
- More complex
- Overkill for current team size

### **Current (AI_CONTEXT.md):**
- ✅ Works for AI agent handoffs
- ✅ Lightweight, no overhead
- ❌ Not structured for PM tracking
- ❌ Hard to visualize progress

**Recommendation:** **Hybrid approach**
- Keep AI_CONTEXT.md for agent handoffs
- Add GitHub Issues for requirement tracking
- Use commit messages for status updates
- Agents read/write both

---

## 📊 **CAPACITY PLANNING**

### **Current Velocity:**
- 12-hour session: Complete foundation + architecture
- Average: ~3 commits/hour sustained
- Quality: High (comprehensive, documented)

### **Team Model:**
- **Requirements Analyst:** Active, framework ready
- **Dev Agent:** On standby, 1 task assigned
- **QA Agent:** Active, test suite ready
- **SCA Agent:** Implemented, ready for period work
- **PM (this role):** Coordinating

### **Bottlenecks:**
1. **Dev Agent activation** (REQ-FUNC-001 waiting)
2. **Single-threaded workflow** (agents work sequentially)
3. **Manual copy-paste** (no MCP yet)

**Mitigation:**
- Prioritize MCP activation (enables faster workflow)
- Parallelize where possible (Period work while waiting for Dev)
- Use Python SCA for automated discovery

---

## 🎯 **IMMEDIATE ACTIONS (Next 24 Hours)**

### **Priority 1: Unblock Critical Path**
```
NEEDED: Dev Agent to implement REQ-FUNC-001
THEN: QA Agent to verify
RESULT: Entity import pipeline production-ready
```

### **Priority 2: Parallel Period Work**
```
START: Python SCA period discovery
RUN: scripts/agents/sca_agent.py with Perplexity
OUTPUT: 500 period proposals
```

### **Priority 3: Git Push**
```
TRY: git push origin master
OR: Push in batches
GOAL: 41 commits on GitHub
```

---

## 📝 **SUCCESS METRICS**

### **This Sprint (2 weeks):**
- ✅ REQ-FUNC-001 verified
- ✅ 10,000+ entities imported
- ✅ 500+ periods classified
- ✅ 5 domain ontologies
- ✅ MCP active
- ✅ Commits pushed to GitHub

### **End of Month:**
- 50,000 entities
- 1,000 periods
- 10 domains
- Claims architecture implemented
- 50+ agents active

---

## 🔧 **TOOLING RECOMMENDATIONS**

### **For Task Tracking:**
**Option 1: GitHub Issues (Recommended)**
```
Pros: Integrated, free, AI-accessible
Cons: Basic features
Setup: 1 hour
```

**Option 2: Linear.app**
```
Pros: Beautiful, fast, AI-friendly
Cons: $8/user/month
Setup: 30 minutes
```

### **For Agent Coordination:**
**Current: AI_CONTEXT.md (Keep)**
```
Pros: Works, lightweight, version-controlled
Cons: Manual, not visual
Recommendation: Keep + supplement with Issues
```

### **For Metrics/Dashboards:**
**Option: Grafana + Prometheus**
```
Track: Nodes/day, commits/hour, test pass rate
Overkill for now, defer to Phase 5
```

---

## 📞 **STAKEHOLDER COMMUNICATION**

**Weekly Status Template:**
```
WEEK OF: [Date]
COMPLETED:
- List achievements
- Metrics (nodes added, tests passed)

IN PROGRESS:
- Current focus
- Blockers

NEXT WEEK:
- Planned work
- Support needed

RISKS:
- Any issues
```

**Frequency:** Weekly updates to stakeholder via AI_CONTEXT.md

---

## ✅ **PM RECOMMENDATIONS**

### **Immediate (Today):**
1. **Activate Dev Agent** for REQ-FUNC-001
2. **Start Period Discovery** (parallel work)
3. **Test MCP** in Cursor chat

### **This Week:**
1. Complete REQ-FUNC-001
2. Import 5,000 more entities
3. Create 500 period proposals
4. Push commits to GitHub

### **This Month:**
1. Scale to 50,000 entities
2. Expand to 5-10 domains
3. Implement claims architecture
4. Activate 20+ agents

---

**PM ASSESSMENT COMPLETE - Ready for team coordination!**
