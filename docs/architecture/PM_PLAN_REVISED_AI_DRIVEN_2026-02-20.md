# Chrystallum Project Plan - AI-Driven Development

**Project Manager:** AI PM Agent  
**Date:** February 20, 2026  
**Methodology:** PMBOK 7th Edition Principles + AI-Driven Agile  
**Reality:** AI agents complete work in hours, not weeks

---

## 🎯 **PMBOK 7TH EDITION PRINCIPLES APPLIED**

### **Project Performance Domains:**

1. **Stakeholders** - You (stakeholder) + AI agent team
2. **Team** - Dev, QA, Requirements, SCA, PM (all AI)
3. **Development Approach** - AI-driven iterative (tasks in hours)
4. **Planning** - Outcome-focused, not date-driven
5. **Project Work** - Autonomous AI execution
6. **Delivery** - Continuous (commit-based)
7. **Measurement** - Outcomes achieved, not time spent
8. **Uncertainty** - Low (AI agents work 24/7, consistent)

---

## 📊 **PROJECT STATUS (Outcome-Based)**

### **Foundation Phase: ✅ COMPLETE**

**What's Done:**
- ✅ Self-describing system architecture (Chrystallum + 4 branches)
- ✅ 48,920 nodes in Neo4j (clean, canonical)
- ✅ 230+ documentation files (well-organized)
- ✅ Python SCA agent (operational)
- ✅ REQ-FUNC-001 VERIFIED (import pipeline production-ready)
- ✅ Requirements framework active

**Outcome:** Production-ready foundation ✅

---

### **Current Phase: Entity Loading & Discovery**

**What's In Progress:**
- 🟡 300 entities loaded (target: 10K+)
- 🟡 1 domain ontology (target: 5-10)
- 🟡 7 PROPOSED requirements (need approval)
- 🟢 Period discovery ready (not started)

**Next Outcomes:**
1. Scale to 10,000 entities
2. Create 5 domain ontologies
3. Discover and classify 1,000 periods
4. Approve backfilled requirements

---

## 🎯 **OUTCOME-BASED ROADMAP (No Dates)**

### **Track 1: Entity Scaling**

**Current:** 300 entities (Roman Republic)  
**Target:** 10,000 entities across 5 domains  
**Progress:** 3%

**Work Breakdown (AI Execution):**
- Deep dive: Roman Republic → +2,500 entities (~2-4 hours AI work)
- Domain 2: Ancient Greece → +2,000 entities (~2-3 hours)
- Domain 3: Ancient Egypt → +2,000 entities (~2-3 hours)
- Domain 4: Medieval Europe → +1,500 entities (~2 hours)
- Domain 5: Hellenistic Period → +1,500 entities (~2 hours)

**Total AI Effort:** 10-15 hours (not weeks!)  
**Dependency:** None (REQ-FUNC-001 verified)  
**Blocker:** None  
**Status:** ✅ Ready to execute

---

### **Track 2: Period Discovery & Classification**

**Current:** 1,077 periods (PeriodO import)  
**Target:** +1,000 classified periods from Wikidata  
**Progress:** Ready to start

**Work Breakdown (AI Execution):**
- Wikidata backlink harvest → ~500 candidates (~30 min API calls)
- Perplexity classification → period types (~2-3 hours, API dependent)
- PeriodO mapping → match to existing (~1 hour)
- Review + approve → human time variable
- Load to Neo4j → approved periods (~30 min)

**Total AI Effort:** 4-5 hours + human review  
**Dependency:** None (can start now)  
**Blocker:** None  
**Status:** ✅ Ready to execute

---

### **Track 3: SFA Development**

**Current:** 3/18 SFA prompts complete  
**Target:** 18/18 complete  
**Progress:** 17%

**Work Breakdown (AI Execution):**
- Create template SFA prompt (~30 min)
- Generate 15 prompts from template (~2-3 hours with validation)
- Test and refine (~1-2 hours)

**Total AI Effort:** 3-5 hours  
**Dependency:** None  
**Blocker:** None  
**Status:** ✅ Ready to execute

---

### **Track 4: Claims Architecture**

**Current:** Designed, not implemented  
**Target:** Operational claims pipeline  
**Progress:** 0% implementation

**Work Breakdown (AI Execution):**
- Implement Claim node creation (~2 hours)
- FacetPerspective star pattern (~2 hours)
- Evidence linking (~1 hour)
- SCA → SFA handoff (~2 hours)
- Testing and refinement (~2 hours)

**Total AI Effort:** 9-10 hours  
**Dependency:** Prefer 10K+ entities first (richer testing)  
**Blocker:** None (can start, better with more data)  
**Status:** 🟡 Ready but recommend deferring

---

## 🎯 **PRIORITY QUEUE (Outcome-Focused)**

### **Priority 1: Scale Entity Count (READY)**
**Why:** Foundation complete, import verified, need data volume  
**Target:** 300 → 10,000 entities  
**AI Effort:** 10-15 hours execution  
**Human Effort:** Review and approve (as needed)  
**Outcome:** Rich knowledge graph for testing

### **Priority 2: Period Discovery (READY, PARALLEL)**
**Why:** Different data source, no dependencies  
**Target:** +1,000 classified periods  
**AI Effort:** 4-5 hours + API time  
**Human Effort:** Approve period proposals  
**Outcome:** Complete temporal coverage

### **Priority 3: Complete SFA Library (READY, PARALLEL)**
**Why:** Enables full 18-facet analysis  
**Target:** 18/18 SFA prompts  
**AI Effort:** 3-5 hours  
**Human Effort:** Review and approve prompts  
**Outcome:** Complete agent toolkit

### **Priority 4: Git Hygiene (READY)**
**Why:** Backup work to GitHub  
**Target:** Push 42+ commits  
**AI Effort:** Retry push, troubleshoot  
**Human Effort:** May need network intervention  
**Outcome:** Work backed up remotely

### **Priority 5: Approve Backfilled Requirements (WAITING)**
**Why:** Formalize existing architecture  
**Target:** Approve REQ-FUNC-002 through REQ-DATA-003  
**AI Effort:** None (already documented)  
**Human Effort:** Review and approve 7 requirements  
**Outcome:** Requirements complete for current architecture

---

## 📊 **AI EFFORT ESTIMATION MODEL**

### **AI Agent Work (Actual Reality):**

**Task Complexity vs AI Time:**
- **Simple** (query, analysis, document): Minutes
- **Moderate** (code generation, testing): 1-2 hours
- **Complex** (architecture, multi-file coordination): 2-4 hours
- **Very Complex** (novel algorithms, integration): 4-8 hours

**API-Dependent Work:**
- Wikidata SPARQL: Fast (~seconds per query)
- Perplexity classification: ~1-3 seconds per item
- Bottleneck: API rate limits, not AI thinking time

**Human-Dependent Work:**
- Review and approval: Variable (minutes to days)
- Decision-making: Variable
- Strategic direction: Variable

### **Revised Effort Estimates:**

| Task | Human Estimate | AI Reality | Factor |
|------|----------------|------------|--------|
| Import 2,500 entities | 3 days | 2-3 hours | 24x faster |
| Create domain ontology | 1 week | 1-2 hours | 40x faster |
| Write 15 SFA prompts | 1 week | 3-5 hours | 20x faster |
| Classify 500 periods | 2 weeks | 4-5 hours | 50x faster |

**Key Insight:** AI agents complete in **hours** what humans do in **weeks**

---

## 🎯 **SIMPLIFIED EXECUTION PLAN**

### **Batch 1: Data Volume (Can Execute Now)**

**Tasks:**
1. Entity scaling (300 → 10K)
2. Period discovery (500 candidates)
3. Period classification (Perplexity)

**AI Execution Time:** ~15-20 hours total  
**Human Time:** Review and approve outputs  
**Outcome:** 10K entities + 500 period proposals

**Sequence:**
- Start all three in parallel (no dependencies)
- AI agents work autonomously
- Output proposals for human review
- Load approved items to Neo4j

---

### **Batch 2: Agent Completeness (Can Execute Now)**

**Tasks:**
1. Complete 15 SFA prompts
2. Test all 18 SFA prompts
3. Document SFA methodology

**AI Execution Time:** ~5-8 hours total  
**Human Time:** Review and approve prompts  
**Outcome:** Complete 18-facet agent toolkit

**Sequence:**
- Create template
- Generate 15 prompts
- Test and refine
- Document

---

### **Batch 3: Claims Pipeline (Defer Until Batch 1 Complete)**

**Tasks:**
1. Implement Claim architecture
2. SCA/SFA coordination
3. Evidence and provenance
4. Multi-facet analysis

**AI Execution Time:** ~10-12 hours  
**Reason to Defer:** Works better with 10K+ entities  
**Outcome:** Operational claims system

---

## 📋 **EXECUTION MODEL (AI-Driven Agile)**

### **Sprint = Collection of Outcomes (Not Time Box)**

**Sprint 1 Outcomes:**
- ✅ Import pipeline verified (DONE - REQ-FUNC-001)
- 🎯 10,000 entities across 5 domains
- 🎯 500 period candidates classified
- 🎯 18/18 SFA prompts complete

**When Complete:** Sprint 1 done (regardless of time)  
**Typical AI Time:** 20-30 hours of autonomous work  
**Human Time:** Reviews and approvals as outputs ready

**No artificial deadlines** - work completes when outcomes achieved

---

### **Backlog = Prioritized Outcomes**

**Priority Queue:**
1. Entity scaling (blocking downstream work)
2. Period discovery (parallel, no blocking)
3. SFA completeness (parallel, enables richer analysis)
4. Claims architecture (blocked by #1, deferred)

**Pull Model:** Agents pull next task when ready  
**Push Model:** PM assigns critical path items

---

## 🔄 **COORDINATION VIA AI_CONTEXT**

### **Status Updates (Outcome-Based):**

```markdown
## Agent Status Update

**Agent:** [Dev/QA/SCA/Requirements]  
**Completed Outcomes:**
- List what was achieved
- Metrics (nodes created, tests passed, requirements approved)

**Current Work:**
- What agent is working on now

**Blocked/Needs:**
- Any blockers or human input needed

**Next Outcomes:**
- What agent will work on next
```

**Frequency:** Update when outcomes complete (not daily)  
**Location:** AI_CONTEXT.md latest update section

---

## 📊 **METRICS (Outcome-Focused)**

### **Knowledge Graph Growth:**
- Current: 48,920 nodes
- Target: 60,000 nodes (Sprint 1)
- Target: 100,000 nodes (Sprint 2)

### **Entity Coverage:**
- Current: 300 entities (1 domain)
- Target: 10,000 entities (5 domains)
- Progress: Measured by entity count

### **Period Coverage:**
- Current: 1,077 periods (PeriodO)
- Target: 2,000 periods (PeriodO + Wikidata)
- Progress: Measured by classified periods

### **Agent Capability:**
- Current: 3/18 SFA prompts
- Target: 18/18 SFA prompts
- Progress: Measured by prompt count

### **Requirements:**
- Current: 8 requirements (1 VERIFIED, 7 PROPOSED)
- Target: All PROPOSED → APPROVED
- Progress: Measured by verified requirements

---

## ✅ **IMMEDIATE EXECUTION PLAN**

### **What Can Start Now (No Blockers):**

**1. Entity Scaling** ← Start this
```
Tool: Python SCA agent
Input: Seed QIDs for 5 domains
Process: Wikidata traversal → entity discovery
Output: 10K entity proposals
AI Time: ~15 hours autonomous execution
Human: Review and approve in batches
```

**2. Period Discovery** ← Start this (parallel)
```
Tool: Python SCA + Perplexity
Input: Seed period QIDs (Q11756, Q12554, etc.)
Process: Backlinks → classification → proposals
Output: 500 period proposals
AI Time: ~5 hours + API
Human: Review and approve
```

**3. SFA Prompts** ← Start this (parallel)
```
Tool: Template-based generation
Input: 3 existing SFA methodologies
Process: Extract pattern → generate 15 more
Output: 18/18 SFA prompts
AI Time: ~4 hours
Human: Review and approve
```

**All three can run in parallel** - no dependencies, no blockers

---

## 🎯 **SUCCESS = OUTCOMES ACHIEVED**

**Not:** "Completed by Friday"  
**But:** "10K entities loaded and verified"

**Not:** "2-week sprint"  
**But:** "Outcomes 1-3 complete" (happens when it happens)

**Not:** "4 hours estimated"  
**But:** "Task unblocked, executing" (AI works autonomously)

---

## 🔧 **TOOLING FOR AI-DRIVEN PM**

### **Recommended: Hopper Velocity Model**

**Structure:**
1. **PROJECT.md** - Goals and success criteria (your REQUIREMENTS.md)
2. **ROADMAP.md** - Phases and milestones (outcome-based)
3. **PLAN.md** - Executable checklists (this plan)

**Benefits for AI:**
- Outcome-focused (not time-based)
- Executable checklists
- Clear acceptance criteria
- No artificial deadlines

### **AI_CONTEXT.md = Living Status**

**What Works:**
- ✅ Agent coordination
- ✅ Outcome tracking
- ✅ Handoffs

**What to Add:**
- Outcome-based status (not dates)
- Blocker tracking
- Human decision log

### **GitHub Issues = Work Queue**

**Use as:**
- Backlog (outcomes to achieve)
- Kanban (current work)
- Labels (priority, not deadlines)

**Not as:**
- Schedule (no due dates)
- Time tracking (irrelevant for AI)

---

## 📋 **EXECUTION QUEUE (Pull-Based)**

### **Ready to Execute (No Blockers):**

**Queue Position 1:** Entity Scaling
- Outcome: 10K entities
- AI Effort: Autonomous (~15 hrs)
- Blocker: None
- **Status: READY → Assign to SCA Agent**

**Queue Position 2:** Period Discovery
- Outcome: 500 classified periods
- AI Effort: Autonomous (~5 hrs) + Perplexity API
- Blocker: None
- **Status: READY → Can start immediately**

**Queue Position 3:** SFA Completion
- Outcome: 18/18 prompts
- AI Effort: Template-based (~4 hrs)
- Blocker: None
- **Status: READY → Assign to Requirements or designated agent**

### **Waiting on Human:**

**Queue Position 4:** Approve Backfilled Requirements
- Outcome: 7 PROPOSED → APPROVED
- AI Effort: None (already documented)
- Human Effort: Review 7 requirements
- **Status: WAITING → Human review needed**

**Queue Position 5:** Git Push
- Outcome: 42 commits on GitHub
- AI Effort: Retry mechanism
- Human Effort: May need network intervention
- **Status: READY → Retry push**

### **Deferred (Waiting for Data Volume):**

**Queue Position 6:** Claims Implementation
- Outcome: Operational claims pipeline
- AI Effort: ~10 hours
- Blocker: Prefer 10K+ entities first
- **Status: DEFERRED → Execute after Queue Position 1**

---

## 🎯 **PM COORDINATION PATTERN**

### **Daily (As Outcomes Complete):**

**Agent completes outcome** → Updates AI_CONTEXT:
```markdown
## [Agent] Outcome Complete: [Description]
- What: [Outcome achieved]
- Results: [Metrics, nodes, etc.]
- Next: [What agent will work on next]
```

**PM reads AI_CONTEXT** → Identifies:
- What's complete
- What's blocked
- What needs human input
- What to assign next

---

### **Weekly (Outcome Review):**

**PM publishes progress:**
```markdown
## PM Weekly: Outcomes Achieved

COMPLETED OUTCOMES:
- List all completed outcomes with metrics

ACTIVE WORK:
- What agents are currently executing

WAITING FOR:
- Human approvals/reviews/decisions

NEXT OUTCOMES:
- What's queued for next batch
```

**No deadlines** - progress measured by outcomes, not time

---

## ✅ **REVISED PM APPROACH**

### **What Changed:**

**OLD (Human-Style PM):**
- Sprint = 2 weeks time box
- Tasks estimated in days
- Deadlines and schedules
- Gantt charts

**NEW (AI-Driven PM):**
- Sprint = Collection of outcomes
- Tasks completed in hours (AI autonomous)
- No deadlines, just dependencies
- Outcome-based tracking

### **What Stayed:**

- ✅ Clear priorities
- ✅ Dependency management
- ✅ Blocker identification
- ✅ Team coordination
- ✅ Status communication

---

## 🚀 **IMMEDIATE ACTIONS (Ready to Execute)**

**For AI Agents (Can Start Now):**

**1. SCA Agent:** Start entity scaling
```bash
python scripts/agents/sca_agent.py --mode discover --domains 5 --target 10000
# Or whatever the actual command is
```

**2. SCA Agent:** Start period discovery (parallel)
```bash
python scripts/agents/sca_agent.py --mode periods --backlinks --seeds Q11756,Q12554,Q17167
```

**3. Requirements Analyst:** Generate 15 SFA prompts
```
Use template from existing 3 prompts
Generate for remaining 15 facets
Output to md/Agents/SFA/ directory
```

**For Human (Your Review Needed):**

**4. Approve 7 Backfilled Requirements**
- Read REQUIREMENTS.md (REQ-FUNC-002 through REQ-DATA-003)
- These document existing architecture
- Approve → formalizes decisions

**5. Decide on Tooling**
- Setup GitHub Issues? (30 min)
- Use current AI_CONTEXT-only? (keep simple)
- Try Linear.app? (trial available)

---

## 📊 **PM DASHBOARD (Outcome-Based)**

**Phase:** Entity Loading & Discovery  
**Health:** 9/10 (excellent, unblocked)

**Outcomes Achieved:**
- ✅ Foundation complete
- ✅ Import pipeline verified
- ✅ Requirements framework operational

**Outcomes In Queue (Ready):**
- 🎯 10K entities
- 🎯 500 periods
- 🎯 18 SFA prompts
- 🎯 Commits pushed

**Waiting on Human:**
- ⏳ Approve 7 requirements
- ⏳ Review entity/period proposals (as ready)

**Blockers:** None  
**Risk Level:** LOW

---

**PM PLAN REVISED - AI-Driven, Outcome-Focused, No Artificial Deadlines**

**Execution Model: Outcomes → Review → Next Outcomes**

**Ready to start Priority 1, 2, and 3 in parallel!** 🚀
