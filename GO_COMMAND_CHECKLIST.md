# Phase 2A+2B GO Command Checklist

**Purpose:** Final approval checklist before executing Phase 2A+2B backlink harvest  
**Last Updated:** 2026-02-15  
**Status:** Ready for GO/NO-GO decision

---

## Executive Summary

**What Phase 2A+2B Delivers:**
- ~2,100 discovered entities (1,847 direct historical + 251 temporal bridges)
- Validation of two-track temporal validation architecture
- Real data for Chrystallum Place/PlaceVersion design
- 15 test cases for quality assurance

**Timeline:** ~30 minutes execution + 1-2 hours analysis

**Risk Level:** LOW (analysis run, non-destructive, Neo4j schema prepared)

---

## GO/NO-GO Criteria

### ✅ **READY TO GO**

| Category | Requirement | Status | Evidence |
|----------|-------------|--------|----------|
| **Neo4j Schema** | Indexes created | ✅ | Step 1 executed, BridgeTypes created |
| **Neo4j Schema** | Database empty/ready | ✅ | Verified 0 Entity nodes, temporal backbone intact |
| **GPT Setup** | Custom GPT created | ✅ | Instructions pasted, saved |
| **GPT Setup** | Phase 2 message ready | ✅ | Prompt in PHASE_2_QUICK_START.md |
| **Architecture** | Two-track validation defined | ✅ | temporal_bridge_discovery.py complete |
| **Architecture** | Chrystallum decisions documented | ✅ | 6 questions answered, AI_CONTEXT.md updated |
| **Documentation** | Execution guide ready | ✅ | PHASE_2_QUICK_START.md |
| **Documentation** | Integration roadmap ready | ✅ | CHRYSTALLUM_PHASE2_INTEGRATION.md |
| **Change Control** | Architecture updates logged | ✅ | Change_log.py, ARCHITECTURE_IMPLEMENTATION_INDEX.md |

---

### ⏸️ **DEFERRED (By Design)**

| Component | Why Deferred | When to Implement |
|-----------|--------------|-------------------|
| PlaceVersion nodes | Design based on discovered patterns | Week 3 (post-analysis) |
| Geometry nodes | Requires authority integration | Week 4 (post-design) |
| Place transformation | Entity→Place conversion | Week 4 (after schema finalized) |
| Temporal relationships | Year linkage for PlaceVersions | Week 4 (after versioning) |
| Facet assignment to PlaceVersion | Context-based assignment | Week 4 (during enrichment) |

---

## Pre-Flight Checklist

### **A. Neo4j Readiness**

- [ ] **Database accessible:** `http://localhost:7474` responds
- [ ] **Schema deployed:** Run this verification query:
  ```cypher
  SHOW INDEXES YIELD name
  WHERE name STARTS WITH 'entity_'
  RETURN count(name) AS entity_indexes
  // Expected: 6
  ```
- [ ] **BridgeTypes created:** Run this verification:
  ```cypher
  MATCH (bt:BridgeType)
  RETURN bt.type, bt.base_confidence
  ORDER BY bt.type
  // Expected: 5 rows (archaeological, cultural, historiographic, political_precedent, scientific)
  ```
- [ ] **Temporal backbone intact:** Run this verification:
  ```cypher
  MATCH (y:Year) RETURN count(y) AS year_count
  // Expected: 4025
  ```

### **B. ChatGPT Readiness**

- [ ] **Custom GPT created:** Name "Historical Knowledge Graph Extractor"
- [ ] **Instructions pasted:** Full content from `GPT_PHASE_2_PARALLEL_PROMPT.md`
- [ ] **Instructions saved:** Click "Save" completed
- [ ] **Phase 2 message ready:** Copy from `PHASE_2_QUICK_START.md` Step 3

### **C. Documentation Readiness**

- [ ] **Execution guide reviewed:** `PHASE_2_QUICK_START.md`
- [ ] **Expected output understood:** `EXPECTED_OUTPUT_TWO_TRACK_VALIDATION.md`
- [ ] **Integration roadmap reviewed:** `CHRYSTALLUM_PHASE2_INTEGRATION.md`
- [ ] **15 test cases identified:** Ready to run post-execution

---

## Execution Sequence

### **Step 1: Verify Neo4j (2 minutes)**

```cypher
// Run all three checks above
// Confirm: 6 entity indexes, 5 BridgeTypes, 4025 Year nodes
```

**GO if:** All three queries return expected counts  
**NO-GO if:** Any query fails or returns 0

---

### **Step 2: Send GPT Message (1 minute)**

Paste this into your Custom GPT:

```
Process the Roman Republic Wikipedia article.
Execute PHASE 2A+2B: Simultaneous parallel backlink harvest with two-track validation.

Period: Q17167 (Roman Republic, -509 to -27 BCE)
Depth: 8 hops
Validation: Two-track (direct historical + temporal bridges)
Output format: JSON as specified in instructions.

Begin discovery.
```

**GO if:** GPT acknowledges and begins processing  
**NO-GO if:** GPT returns error or doesn't respond

---

### **Step 3: Wait for GPT Completion (15-20 minutes)**

**Monitor:**
- GPT shows progress through discovery phases
- No error messages appear
- JSON output begins generating

**Expected behavior:**
- Phase 1: Statement extraction (~2 min)
- Phase 2: Backlink harvest (~5 min)
- Phase 3: Entity resolution (~3 min)
- Phase 4: Temporal validation (~5 min)
- Phase 5: Bridge detection (~2 min)
- Phase 6: JSON output (~3 min)

---

### **Step 4: Load Results to Neo4j (3 minutes)**

```cypher
// Copy entities array from GPT JSON output

// Load direct historical entities
UNWIND [
  // PASTE track_1_direct_historical.entities HERE
] AS entity
MERGE (e:Entity {entity_id: entity.entity_id})
SET e += entity, e.track = "direct_historical", e.is_bridge = false;

// Load bridge entities
UNWIND [
  // PASTE track_2_bridges.entities HERE
] AS bridge
MERGE (e:Entity {entity_id: bridge.entity_id})
SET e += bridge, e.track = "bridging_discovery", e.is_bridge = true;

// Verify
MATCH (e:Entity)
RETURN 
  COUNT(CASE WHEN e.track = "direct_historical" THEN 1 END) AS direct_count,
  COUNT(CASE WHEN e.is_bridge = true THEN 1 END) AS bridge_count,
  COUNT(e) AS total;
```

**GO if:** Total ~2,100 entities (1,847 direct + 251 bridges)  
**NO-GO if:** Total < 1,000 or > 5,000 (unexpected output)

---

## Post-Execution Validation

### **Immediate Checks (5 minutes)**

```cypher
// Check 1: Entity type distribution
MATCH (e:Entity)
RETURN e.type, COUNT(e) AS count
ORDER BY count DESC
// Expected: human ~1,542, event ~600, place ~189, organization ~87

// Check 2: Bridge type distribution
MATCH (e:Entity {is_bridge: true})
RETURN e.bridge_type, COUNT(e) AS count
ORDER BY count DESC
// Expected: archaeological ~67, cultural ~64, historiographic ~58, precedent ~42, scientific ~20

// Check 3: Temporal coverage
MATCH (e:Entity)
WHERE e.date IS NOT NULL
WITH e.date AS year, COUNT(e) AS count
RETURN year, count
ORDER BY year
// Expected: Peak around -150 to -50 BCE (Late Republic crisis)

// Check 4: Place entities discovered
MATCH (e:Entity {type: "place"})
RETURN e.label, e.qid, e.date
ORDER BY e.label
LIMIT 20
// Expected: Rome (Q220), Carthage (Q6343), Gaul (Q38), etc.
```

---

### **15 Test Cases (1-2 hours, deferred to Week 2)**

See `CHRYSTALLUM_PHASE2_INTEGRATION.md` Section "Analysis Questions" for full list.

**Sample test cases:**

1. **TC01: Place discovery** - Did GPT find Rome (Q220)?
2. **TC02: Boundary change detection** - Did GPT detect Carthage destruction (-146)?
3. **TC06: Contemporaneity** - Do Battle of Cannae entities link to Cannae context?
4. **TC07: Bridge detection** - Are archaeological discoveries flagged as bridges?
5. **TC11: Territorial expansion** - Does Roman territory show different extents over time?

---

## GO/NO-GO Decision Matrix

| Condition | Action |
|-----------|--------|
| **All pre-flight checks ✅** | **GO** - Execute Phase 2A+2B |
| **Neo4j schema incomplete** | **NO-GO** - Re-run Step 1 from PHASE_2_QUICK_START.md |
| **GPT not responding** | **NO-GO** - Verify Custom GPT saved correctly |
| **Post-execution: < 1,000 entities** | **INVESTIGATE** - Review GPT output for errors |
| **Post-execution: ~2,100 entities** | **SUCCESS** - Proceed to Week 2 analysis |

---

## Success Criteria

**Phase 2A+2B is COMPLETE when:**

- [x] ✅ Neo4j schema deployed (6 indexes, 5 BridgeTypes)
- [ ] ✅ GPT executed Phase 2A+2B without errors
- [ ] ✅ ~2,100 entities loaded to Neo4j
- [ ] ✅ Entity type distribution matches expected (Human, Event, Place, Organization)
- [ ] ✅ Bridge entities present (~251 bridges)
- [ ] ✅ Immediate validation checks pass (4 queries)

**Then proceed to:**
- Week 2: Run 15 test cases
- Week 2: Analyze 189 places for versioning needs
- Week 3: Design PlaceVersion schema
- Week 4: Implement transformation

---

## Rollback Plan

**If Phase 2A+2B fails or produces unexpected output:**

1. **Diagnose:**
   ```cypher
   MATCH (e:Entity)
   DELETE e
   // Clears Entity nodes, preserves temporal backbone
   ```

2. **Check GPT logs:**
   - Review GPT conversation for error messages
   - Verify instructions were complete
   - Check if Wikipedia backlink harvest was blocked

3. **Re-execute:**
   - Fix identified issue
   - Re-run from Step 2 (send GPT message)
   - Monitor more closely

4. **Escalate if:**
   - GPT consistently fails after 3 attempts
   - Neo4j performance issues arise
   - Unexpected entity counts persist

---

## Final Sign-Off

**Project Lead Approval:**

- [ ] I understand Phase 2A+2B is an analysis run
- [ ] I understand PlaceVersion is deferred to post-analysis
- [ ] I understand ~30 min execution + 1-2 hour analysis timeline
- [ ] I have reviewed PHASE_2_QUICK_START.md
- [ ] I have reviewed CHRYSTALLUM_PHASE2_INTEGRATION.md
- [ ] I approve execution of Phase 2A+2B

**Signature:** ___________________________  
**Date:** ___________________________

---

## **📌 ACTION ITEMS (Pin These)**

### **IMMEDIATE (Before Execution)**

- [ ] **Peer Review (OPTIONAL):** Send 4 files to another LLM for validation
  - Files: `GO_COMMAND_CHECKLIST.md`, `CHRYSTALLUM_PHASE2_INTEGRATION.md`, `PHASE_2_QUICK_START.md`, `AI_CONTEXT.md` (Chrystallum section)
  - Prompt: "Validate two-phase approach, success criteria, pre-flight checklist, rollback plan"
  - Timeline: ~10 min review

- [ ] **Load CIDOC-CRM + CRMinf reference nodes (Option 1):**
  - Script: `scripts/reference/load_cidoc_crminf_to_neo4j.py`
  - Input files: `CIDOC/CIDOC_CRM_v7.1.2_JSON-LD_Context.jsonld`, `CIDOC/CRMinf_v0.7_.rdfs.txt`
  - Output: `CIDOC_Class`, `CIDOC_Property`, `CRMinf_Class`, `CRMinf_Property`
  - Timeline: ~5 minutes

- [ ] **Neo4j Pre-Flight:** Run 3 verification queries (Section A above)
  - Verify: 6 entity indexes, 5 BridgeTypes, 4025 Year nodes
  - Timeline: 2 min

- [ ] **Execute Phase 2A+2B:** Follow `PHASE_2_QUICK_START.md`
  - Send message to GPT Custom GPT
  - Wait 15-20 min for completion
  - Load ~2,100 entities to Neo4j
  - Timeline: 30 min total

### **DEFERRED (After Phase 2)**

- [ ] **Week 2: Run 15 Test Cases** (See `CHRYSTALLUM_PHASE2_INTEGRATION.md`)
  - Validate discovery accuracy
  - Analyze 189 places for versioning needs
  - Timeline: 1-2 hours

- [ ] **Week 3: Design PlaceVersion Schema**
  - Create `CHRYSTALLUM_PLACE_SEEDING_REQUIREMENTS.md`
  - Create `PLACE_VERSION_NEO4J_SCHEMA.cypher`
  - Timeline: 2-3 days

- [ ] **Week 4: Transform & Enrich**
  - Write transformation scripts (Entity → Place + PlaceVersion)
  - Load geometry from Wikidata
  - Link to temporal backbone
  - Timeline: 3-4 days

### **NOT NEEDED NOW**

- [ ] ❌ **LCSH SKOS Loading** → DEFER to Phase 3+
  - Reason: Phase 2A+2B uses Wikidata QIDs only
  - When needed: Phase 3 (entity resolution with authority linking)
  - Decision: Don't add reference data until validated as necessary

---

## **🎯 READY TO GO?**

If all pre-flight checks pass and final sign-off complete:

```
✅ EXECUTE PHASE 2A+2B
```

Follow `PHASE_2_QUICK_START.md` starting at Step 1.

---

**Good luck! 🚀**
