# Comprehensive Node Types - All Chrystallum Nodes

**Date:** 2026-02-19  
**Source:** Compiled from Key Files + md architecture documentation  
**Purpose:** Complete catalog of ALL node types (not just "first-class")

---

## 📊 **Node Types by Category**

### **1. SYSTEM GOVERNANCE (7 types)**

**System Subgraph:**
- `Chrystallum` - System root node
- `FederationRoot` - Parent of all federations
- `FacetRoot` - Parent of all facets
- `Federation` - Federation/authority sources (Pleiades, PeriodO, etc.)
- `Facet` - Canonical 18 facets
- `Policy` - Governance rules
- `Threshold` - Monitoring/split triggers

**Status:** ✅ Implemented in Neo4j

---

### **2. CORE ENTITIES (14 types)**

**Historical Entities:**
- `Human` - People, historical figures
- `Event` - Historical events, occurrences
- `Place` - Geographic locations (stable identity)
- `Period` - Historical periods, eras
- `Organization` - Political bodies, groups
- `Dynasty` - Ruling families
- `Institution` - Legal/political/religious structures
- `Work` - Texts, inscriptions, scholarship
- `Claim` - Evidence-based assertions
- `SubjectConcept` - Thematic anchors, concepts

**Roman-Specific:**
- `Gens` - Roman family clans
- `Praenomen` - Roman first names
- `Cognomen` - Roman surnames

**Legal:**
- `LegalRestriction` - Laws, decrees, bans

**Status:** 
- ✅ Implemented: SubjectConcept, Place, Period, Year
- ⏳ Ready for: Human, Event, Organization, Work, Claim, Dynasty, Institution, LegalRestriction, Gens, Praenomen, Cognomen

---

### **3. TEMPORAL BACKBONE (5 types)**

- `Year` - Atomic temporal nodes (-2000 to 2025)
- `Decade` - Rollup of years
- `Century` - Rollup of decades
- `Millennium` - Rollup of centuries
- `PeriodCandidate` - Period triage/validation nodes

**Status:** ✅ Implemented: Year, PeriodCandidate

---

### **4. GEOGRAPHIC (8 types)**

**Core:**
- `Place` - Stable geographic identity
- `PlaceVersion` - Time-scoped place instantiation (name + boundaries change over time)
- `PlaceName` - Alternate names in multiple languages

**Taxonomy:**
- `PlaceType` - Place type taxonomy (settlement, villa, fort, etc.)
- `PlaceTypeTokenMap` - Token → Type mappings
- `GeoSemanticType` - Semantic classification (administrative, natural, cultural, archaeological)
- `Geometry` - Spatial data (WKT coordinates, shapes)
- `GeoCoverageCandidate` - Period-place coverage candidates

**Status:** 
- ✅ Implemented: Place, PlaceType, PlaceTypeTokenMap, GeoSemanticType, GeoCoverageCandidate
- ❌ Removed: PlaceName (simplified to canonical model)
- ⏳ Not yet: PlaceVersion, Geometry

---

### **5. ARCHAEOLOGICAL/MATERIAL (3 types)**

- `Material` - Physical materials (gold, marble, ceramic, etc.)
- `Object` - Artifacts, tools, coins, inscriptions
- `ConditionState` - Time-scoped condition observations

**Status:** ⏳ Ready for (not yet loaded)

---

### **6. AGENT INFRASTRUCTURE (6 types)**

**Agent Management:**
- `Agent` - Agent instances (SCA, SFA, etc.)
- `AgentMemory` - Agent memory/context storage
- `AgentCapability` - Agent capabilities/skills

**LLM Operations:**
- `RetrievalContext` - LLM context tracking
- `AnalysisRun` - Claim evaluation pipeline runs
- `FacetAssessment` - Facet-specific claim evaluations

**Status:** 
- ⏳ To be decided: Are these canonical or agent-specific infrastructure?
- Currently: 0 nodes of these types in Neo4j

---

### **7. CLAIM ARCHITECTURE (4 types)**

**Core Claim:**
- `Claim` - Evidence-based assertion (cipher-based identity)

**Provenance:**
- `FacetPerspective` - Facet-specific interpretation of claim
- `Evidence` - Supporting evidence (inscriptions, sources, etc.)
- `Source` or `Passage` - Specific text passages

**Status:** ⏳ Ready for (claim architecture defined but not loaded)

---

### **8. BOOTSTRAP/SCAFFOLD (2 types)**

**Initialize Mode (v0 Bootstrap):**
- `ScaffoldNode` - Lightweight discovery nodes (non-canonical)
- `ScaffoldEdge` - Proposed relationships (non-canonical)

**Purpose:** SCA creates these during discovery, promotes to canonical after approval

**Status:** ⏳ Per ADR-006, used during Initialize mode only

---

### **9. REIFIED EDGES (1 type)**

- `ProposedEdge` - Reified relationship proposals

**Pattern:**
```cypher
(:Claim)-[:ASSERTS_EDGE]->(:ProposedEdge)-[:FROM]->(source)
                                      -[:TO]->(target)
```

**Status:** Per architecture, used for claim-relationship reification

---

### **10. DEPRECATED (2 types)**

**DO NOT USE:**
- `Position` ❌ Deprecated 2026-02-16 (use Institution + typed edges instead)
- `Activity` ❌ Deprecated 2026-02-16 (use Event or SubjectConcept instead)

**Status:** ✅ Correctly not in Neo4j (0 nodes)

---

## 📊 **Complete Catalog Summary**

### **By Implementation Status:**

**✅ Currently in Neo4j (12 types):**
1. Chrystallum
2. FederationRoot
3. FacetRoot
4. Federation
5. Facet
6. Year
7. Period
8. PeriodCandidate
9. Place
10. PlaceType
11. PlaceTypeTokenMap
12. GeoSemanticType
13. GeoCoverageCandidate
14. SubjectConcept

**⏳ Defined but Not Loaded (22 types):**
15. Human
16. Event
17. Organization
18. Dynasty
19. Institution
20. Work
21. Claim
22. Gens, Praenomen, Cognomen
23. LegalRestriction
24. Material, Object, ConditionState
25. PlaceVersion, Geometry
26. Decade, Century, Millennium
27. FacetPerspective, Evidence
28. Agent, AgentMemory, AgentCapability
29. RetrievalContext, AnalysisRun, FacetAssessment
30. ScaffoldNode, ScaffoldEdge
31. ProposedEdge
32. Policy, Threshold

**❌ Deprecated (2 types):**
33. Position
34. Activity

**TOTAL: 34 node types defined in architecture**

---

## 🎯 **Node Type Categories**

| Category | Count | In Neo4j | Purpose |
|----------|-------|----------|---------|
| System Governance | 7 | 7/7 ✅ | Self-describing configuration |
| Core Entities | 14 | 4/14 | Historical data |
| Temporal Backbone | 5 | 2/5 | Time infrastructure |
| Geographic | 8 | 5/8 | Place infrastructure |
| Material/Archaeological | 3 | 0/3 | Artifact tracking |
| Agent Infrastructure | 6 | 0/6 | Agent operations |
| Claim Architecture | 4 | 0/4 | Evidence/provenance |
| Bootstrap/Scaffold | 2 | 0/2 | Discovery mode |
| Reified Edges | 1 | 0/1 | Relationship proposals |
| Deprecated | 2 | 0/2 ✅ | Do not use |

---

## ✅ **Canonical Node Types (Your List)**

**Based on comprehensive review:**

**Loaded:**
1. SubjectConcept
2. Place
3. Period
4. Year

**Ready to Load:**
5. Human
6. Event
7. Organization
8. Dynasty
9. Institution
10. Work
11. Claim
12. Gens, Praenomen, Cognomen
13. LegalRestriction
14. Material, Object, ConditionState

**Infrastructure (Decide if Canonical):**
15. PlaceVersion, Geometry
16. Decade, Century, Millennium
17. FacetPerspective, Evidence
18. Agent, AgentMemory
19. RetrievalContext, AnalysisRun, FacetAssessment
20. ScaffoldNode, ScaffoldEdge, ProposedEdge

**System Metadata (Canonical):**
21. Chrystallum, FederationRoot, FacetRoot
22. Federation, Facet
23. Policy, Threshold
24. PlaceType, PlaceTypeTokenMap, GeoSemanticType
25. PeriodCandidate, GeoCoverageCandidate

---

## 📝 **Recommendations**

**Core data types to prioritize:**
1. Human (people)
2. Event (historical events)
3. Work (sources)
4. Claim (assertions)
5. Evidence (supporting materials)

**Infrastructure to clarify:**
- Agent-related nodes (canonical or separate?)
- Scaffold nodes (bootstrap only or persistent?)
- Reified edges (needed for all claims?)

---

**Total Distinct Node Types: ~50** (including all variations, infrastructure, and deprecated)

**Core Canonical (Your Working Set): ~25-30**

---

**This is your comprehensive node type catalog!** ✅

