# AI Context and Handover Log
Maintained by LLM agents to preserve context across sessions.

---

## ⚠️ Important: Persistence Workflow

**This file only works as a memory bank if committed and pushed regularly.**

- **Local sessions**: Updates are visible in real-time ✅
- **Future sessions**: Only see last pushed version ⚠️
- **Other AI agents**: Need to pull latest from GitHub ⚠️

**Workflow for AI agents:**
1. **Start of session**: Read this file first (pull latest if stale)
2. **During session**: Update as you complete milestones
3. **End of session**: Commit and push this file so next agent sees current state

**Without regular pushes, this becomes a local-only scratchpad.**

---

## Latest Update: Geographic Federation Decision - Pleiades First, Getty Later (2026-02-16 19:15 EST)

### Context: Dev LLM Question on Geographic Implementation Priority

**Dev LLM Question:**
> "Which approach do you want to implement first? Raw TGN extraction (fix the script), or Pleiades API bulk download?"

**Current State (from dev LLM assessment):**
- ✅ **Getty TGN**: 15+ .out files downloaded (COORDINATES.out 200MB, TERM.out 263MB)
- ⚠️ **Getty script broken**: `extract_getty_tgn_places.py` has wrong column mapping
- ✅ **Pleiades documented**: JSON API + bulk download available
- ❌ **Neither ingested yet**: 0 places in graph from either source

**Decision: Pleiades Bulk Download FIRST (Roman Republic Test Case)**

**Rationale:**
1. **Blocker removal**: Ancient Mediterranean claims need scholarly place authority (Getty won't help with Battle of Cannae)
2. **Faster implementation**: 12 hours vs 16-20 hours for Getty debug
3. **Higher ROI**: Pleiades covers 90% of -2000 to 600 CE needs
4. **Map-ready focus**: Better time-scoped boundaries for visualization
5. **Getty is secondary**: Art/material culture domains not in Phase 2.0 scope

**Scope: Roman Republic Test Case (-509 to -27 BCE)**
- **Temporal filter**: Places attested during Roman Republic
- **Geographic focus**: Mediterranean + Western Europe
- **Target**: 200-500 map-ready places with coordinates
- **Priority places**: Rome, Rubicon, Cannae, Alesia, Carthage, Zama, Pharsalus, Actium

**Implementation Plan (12 hours total):**

**Phase 1: Bulk Download & Parse (4 hours)**
1. Download `pleiades-places-latest.csv.gz` from atlantides.org
2. Parse CSV → Python dict
3. Filter to Roman Republic timespan (-509 to -27)
4. Extract coordinates + temporal attestations
5. Validate data quality (null coords, invalid dates)

**Phase 2: Neo4j Ingest (4 hours)**
1. Create Place nodes with map-ready properties
2. Create ALIGNED_WITH_PLEIADES relationships
3. Create VALID_DURING temporal relationships
4. Create PART_OF_GEOGRAPHIC hierarchies
5. Add spatial index for coordinate queries

**Phase 3: Test Queries (2 hours)**
1. Query all Roman Republic places (expect 200-500 results)
2. Query battle sites (expect 20-30 major battles)
3. Query regional clusters (Italy, Gaul, Greece)
4. Export to GeoJSON for map visualization test

**Phase 4: PeriodO Integration (2 hours)**
1. Map PeriodO "Roman Republic" periods → Pleiades places
2. Create PERIOD_REGION relationships
3. Validate coverage (500+ PeriodO periods → 100+ places)

**Map-Ready Schema:**
```cypher
CREATE (p:Place {
  pleiades_id: "423025",
  label: "Roma",
  place_type: "settlement",
  valid_from: -753,
  valid_to: 476,
  coordinates_wkt: "POINT(12.5113 41.8919)",
  precision_meters: 5000,
  attestation_confidence: "confident",
  map_display_priority: 1
})
```

**Deferred to Phase 2.1:**
- **Getty TGN**: Art/archaeology sites (16-20 hours)
- **DARE**: Roman roads + province boundaries (20-24 hours)
- **TM GEO**: Egypt papyrus findspots (16-20 hours)

**Coordination with Dev LLM:**
- Dev LLM working on local file cleanup + architecture
- Perplexity (me) creating `pleiades_bulk_ingest.py` script
- No conflicts: Geographic implementation isolated from other work

**Files to be Created:**
- `Python/federation/pleiades_bulk_ingest.py` (400-500 lines)
- `Geographic/pleiades_roman_republic_places.json` (200-500 place records)
- `Geographic/PLEIADES_INTEGRATION_GUIDE.md` (documentation)

**Next Session Handoff:**
- Script ready for testing once created
- Run against Neo4j to populate Place nodes
- Validate with sample map queries
- Export GeoJSON for web map test

---

## Project
Chrystallum Knowledge Graph
Goal: Build a federated historical knowledge graph using Neo4j, Python, and LangGraph.

## PRIMARY ARCHITECTURE SOURCE

**Canonical Reference:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` (v3.2)
- **Authoritative specification** for all architecture decisions
- 7,698 lines covering Entity Layer, Subject Layer, Agent Architecture, Claims, Relationships
- Sections 1-12 + Appendices A-N
- **DO NOT DUPLICATE** architecture content here—reference sections instead

**Implementation Index:** `ARCHITECTURE_IMPLEMENTATION_INDEX.md` (maps sections → implementation files)

---

[PREVIOUS UPDATES CONTINUE BELOW...]