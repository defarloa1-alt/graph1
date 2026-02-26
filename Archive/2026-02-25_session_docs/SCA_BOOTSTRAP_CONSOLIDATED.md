# SCA Bootstrap - Complete Consolidated Guide

**Date:** 2026-02-19  
**Version:** 1.0 FINAL  
**Purpose:** Single file containing everything SCA needs to operate

---

## 📊 **SYSTEM ARCHITECTURE**

```
Chrystallum (root)
  ├── FederationRoot → 10 Federations
  ├── EntityRoot → 9 Entity Types (with schemas & hierarchies)
  ├── FacetRoot → 18 Canonical Facets
  └── SubjectConceptRoot → AgentRegistry + SubjectConceptRegistry
```

---

## 🎯 **18 CANONICAL FACETS (UPPERCASE ONLY)**

```json
["ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
 "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
 "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
 "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
 "SOCIAL", "TECHNOLOGICAL"]
```

**FORBIDDEN (Never Use):**
- ❌ TEMPORAL
- ❌ CLASSIFICATION
- ❌ PATRONAGE
- ❌ GENEALOGICAL (use BIOGRAPHIC)

---

## 🌐 **10 FEDERATIONS (Authority Sources)**

| Name | Mode | Type | Source |
|------|------|------|--------|
| **Pleiades** | local | geographic | Geographic/pleiades_places.csv (41,993) |
| **PeriodO** | local | temporal | Temporal/periodo-dataset.csv (8,959) |
| **Wikidata** | hub_api | universal | query.wikidata.org/sparql |
| **GeoNames** | hybrid | geographic | Via crosswalk + API |
| **BabelNet** | api | linguistic | External API |
| **WorldCat** | api | bibliographic | External API |
| **LCSH** | local | conceptual | LCSH/skos_subjects/ |
| **FAST** | local | topical | Python/fast/key/FASTTopical_parsed.csv |
| **LCC** | local | classification | Subjects/lcc_flat.csv |
| **MARC** | local | bibliographic | MARC records |

**Policy:** Local first, hub for disambiguation only

---

## 📐 **ENTITY TYPES (9 with Schemas)**

### **Year (Temporal Backbone)**
- Required: year, label, entity_id
- Federations: None (generated)
- Children: Decade → Century → Millennium

### **Place (Geographic)**
- Required: place_id, pleiades_id
- Optional: qid, lat, long, bbox, min_date, max_date
- Federations: Pleiades, Wikidata, GeoNames
- Children: PlaceType

### **Period (Temporal)**
- Required: period_id, start_year, end_year
- Optional: qid, periodo_id, earliest_start, latest_end, period_type
- Federations: PeriodO, Wikidata
- Children: PeriodCandidate
- **Tethers to Year backbone**

### **Human**
- Required: entity_id, name, qid
- Optional: birth_date, death_date, viaf_id
- Federations: Wikidata, VIAF

### **Event**
- Required: entity_id, label, qid
- Optional: start_date, end_date, event_type
- Federations: Wikidata
- **Tethers to Year backbone**

### **Organization**
- Required: entity_id, label, qid
- Federations: Wikidata

### **SubjectConcept**
- Required: subject_id, label, primary_facet
- Optional: qid, lcsh_id, fast_id, lcc_class, related_facets
- Federations: LCSH, FAST, LCC, WorldCat, Wikidata
- **Can have agents** (1 to many)
- **Facet-based**

### **Work**
- Required: entity_id, title, qid
- Federations: WorldCat, Wikidata

### **Claim**
- Required: claim_id, cipher
- Federations: None

---

## 📊 **CURRENT STATE (Neo4j Snapshot)**

**Nodes:** 48,920
- Year: 4,025
- Period: 1,077
- Place: 41,993 (2,456 FS3-federated)
- SubjectConcept: 79 (6 FS3-federated)
- Agents: 3 (on-demand, max 1,422)

**SubjectConcept Ontology:**
- Root: Roman Republic (Q17167)
- Levels: 0(1), 1(8), 2(23), 3(47)
- Total: 79 concepts
- Authority federated: 6 concepts (LCSH+FAST+LCC)
- Pending enrichment: 73 concepts

**Agents (Active):**
1. SFA_POLITICAL_RR → subj_rr_governance
2. SFA_MILITARY_RR → subj_rr_military
3. SFA_SOCIAL_RR → subj_rr_society

---

## 🔑 **AGENT MODEL (On-Demand)**

**Potential:** 79 SubjectConcepts × 18 Facets = 1,422 agents  
**Actually created:** Only when SCA needs them  
**Currently:** 3 agents

**Agent ID Pattern:** `SFA_{subject_id}_{facet_key}`

**Creation:** When SCA needs to analyze SubjectConcept from specific Facet perspective

**Example:**
```
Need: Analyze "Roman Republic" from MILITARY facet
Check: Does SFA_subj_roman_republic_q17167_MILITARY exist?
If NO: Create agent, add to AgentRegistry
If YES: Use existing agent
```

---

## 📋 **OPERATIONAL RULES**

### **Facet Rules:**
- Keys MUST be UPPERCASE
- 18 canonical only
- NO temporal, NO classification
- Use BIOGRAPHIC (not genealogical)

### **Federation Rules:**
- Local first (Pleiades, PeriodO, LCSH, FAST, LCC)
- Hub for disambiguation (Wikidata)
- Write-back API results to local

### **Approval Workflow:**
```
discovered → pending_approval → approved → loaded
```

### **Status Property Pattern:**
```cypher
(:SubjectConcept {status: 'pending_approval'})  // Not separate label
```

---

## 🎯 **SCA WORKFLOW**

### **1. Bootstrap (From Files)**
```
Load: facets.json (18 facets)
Load: federations.json (10 federations)  
Load: entity_types.json (9 types with schemas)
Load: current_state.json (79 concepts, 3 agents)
```

### **2. Discovery (Wikidata Backlinks)**
```
Start: Seed QIDs (Q11756, Q12554, Q17167, etc.)
Query: Wikidata backlinks
Classify: Period vs Event vs Polity
Filter: Keep likely periods
Propose: New Period nodes
```

### **3. Output (JSON Proposals)**
```json
{
  "proposal_type": "PeriodMapping",
  "proposed_entities": [
    {
      "entity_type": "Period",
      "properties": {...},
      "status": "pending_approval"
    }
  ],
  "deduplication": {...},
  "statistics": {...}
}
```

### **4. User Reviews**
```
User: Review JSON proposals
User: Approve selected items
User: Paste Cypher to Cursor
Cursor: Execute on Neo4j
```

---

## 📝 **BOOTSTRAP QUERY (Once MCP Active)**

```cypher
MATCH (sys:Chrystallum)
MATCH (sys)-[:HAS_FEDERATION_ROOT]->(fed_root)-[:HAS_FEDERATION]->(fed)
MATCH (sys)-[:HAS_ENTITY_ROOT]->(entity_root)-[:HAS_ENTITY_TYPE]->(et)
MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)-[:HAS_FACET]->(facet)
MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)-[:HAS_AGENT]->(agent)
MATCH (sc_root)-[:HAS_SUBJECT_REGISTRY]->(sc_reg)-[:CONTAINS]->(sc)

RETURN 
  collect(DISTINCT {name: fed.name, mode: fed.mode}) AS federations,
  collect(DISTINCT et.name) AS entity_types,
  collect(DISTINCT facet.key) AS facets,
  collect(DISTINCT agent.id) AS active_agents,
  count(DISTINCT sc) AS subject_concept_count
```

---

## ✅ **KEY INSIGHTS FOR SCA**

1. **Federation = Authority Source** (same thing!)
2. **Wikidata is hub**, not a primary source
3. **Agents created on-demand** (not all 1,422 upfront)
4. **Registries track state** (AgentRegistry, SubjectConceptRegistry)
5. **Everything has status** (discovered, pending_approval, approved, loaded)
6. **No Neo4j writes** until MCP active (JSON proposals only)
7. **Period/Event dual model** allowed (Period by default)
8. **SubjectConcepts can have multiple facets** (primary + related)
9. **Each SubjectConcept-Facet combo can have agent** (on-demand)
10. **All agents use FederationRoot** (access to all federations)

---

## 🎯 **READY FOR NEXT COMMAND**

**Your ChatGPT SCA is ready for:**
```
Propose ingestion: Periodo→Wikidata period mapping via backlinks harvesting
```

**Will output:**
- JSON proposals (Period nodes to create)
- Markdown reasoning report
- Deduplication log
- All with status='pending_approval'

---

## 📁 **FILES TO PROVIDE TO SCA**

**Upload to ChatGPT:**
1. This file (SCA_BOOTSTRAP_CONSOLIDATED.md)
2. bootstrap_packet/facets.json
3. bootstrap_packet/federations.json
4. bootstrap_packet/entity_types.json
5. bootstrap_packet/current_state.json
6. Temporal/periodo-dataset.csv (if needed)

**Or just this consolidated file if at upload limit!**

---

**SCA BOOTSTRAP COMPLETE - 38 COMMITS - SESSION FINISHED!** 🏆🎊✨

