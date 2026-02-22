````markdown
# **Chrystallum Architecture Specification - BODY SECTIONS 1-12**
**Version:** 3.2 Consolidated (Body Only)  
**Date:** February 12, 2026  
**Status:** Draft for Review

---

## **Document Purpose**

This document contains **Sections 1-12** of the authoritative architectural specification for Chrystallum, a multi-agent knowledge graph system designed for historical research. It consolidates:

- Core ontology layers (Entity, Subject, Agent, Claims, Relationships)
- Implementation architecture (LangGraph orchestration, Neo4j storage)
- Authority standard alignment (LCC, FAST, LCSH, MARC, Wikidata, CIDOC-CRM)
- Operational governance (validation, quality, maintenance)

**Companion Document:** See [2-12-26 Chrystallum Architecture - APPENDICES.md](2-12-26%20Chrystallum%20Architecture%20-%20APPENDICES.md) for appendices (A-N).

**Target Audience:** System architects, developers, historians, data scientists

---

## **Table of Contents**

### **PART I: EXECUTIVE & OVERVIEW**
1. Executive Summary
2. System Overview

### **PART II: CORE ONTOLOGY LAYERS**
3. Entity Layer
4. Subject Layer (w/ Temporal, Geographic, Wikidata Federations)
5. Agent Architecture
6. Claims Layer
7. Relationship Layer

### **PART III: IMPLEMENTATION & TECHNOLOGY**
8. Technology Stack & Orchestration
9. Workflows & Agent Coordination

### **PART IV: OPERATIONAL GOVERNANCE**
10. Quality Assurance & Validation
11. Graph Governance & Maintenance
12. Future Directions

### **PART V: APPENDICES** 
[See companion document: 2-12-26 Chrystallum Architecture - APPENDICES.md]
- Appendix A: Canonical Relationship Types ✅
- Appendix B: Action Structure Vocabularies ✅
- Appendix C: Entity Type Taxonomies ✅
- Appendix D: Subject Facet Classification ✅
- Appendix E: Temporal Authority Alignment ↳ See Section 4.3 ✅
- Appendix F: Geographic Authority Integration ↳ See Section 4.4 ✅
- Appendix G: Legacy Implementation Patterns ✅
- Appendix H: Architectural Decision Records ✅
- Appendix I: Mathematical Formalization ✅
- Appendix J: Implementation Examples ✅
- Appendix K: Wikidata Integration Patterns ↳ See Section 4.5 ✅
- Appendix L: CIDOC-CRM Integration Guide ✅
- Appendix M: Identifier Safety Reference ✅ 🔴 CRITICAL
- Appendix N: Property Extensions & Advanced Attributes ✅

**Status:** 12 sections complete; Sections 4.3-4.5 (Federations) integrated into core architecture

---

# **PART I: EXECUTIVE & OVERVIEW**

---

# **1. Executive Summary**

## **1.1 System Purpose**

**Chrystallum** is an AI-powered knowledge graph system for historical research that combines:
- **Multi-agent orchestration** (LangGraph) for collaborative knowledge construction
- **Evidence-aware claims architecture** for transparent provenance and validation
- **Library backbone standards** (LCC, FAST, LCSH, MARC) for subject organization
- **Historical date precision** (systematic ISO 8601, BCE/CE handling)
- **International standards alignment** (Wikidata, CIDOC-CRM, PeriodO, TGN, Pleiades)

**Core Innovation:** Two-stage architecture separating LLM extraction from deterministic reasoning validation, ensuring reliable knowledge construction while preserving evidence chains.

---

## **1.2 Architectural Principles**

### **1.2.1 Two-Stage Architecture: LLM Extraction → Reasoning Validation**

**Problem:** LLMs hallucinate. Deterministic reasoning models provide verifiable logic but lack extraction capabilities.

**Solution:** Separate concerns:
1. **LLM Stage:** Extract entities, relationships, temporal data from unstructured text
2. **Reasoning Stage:** Validate extractions against schema, authorities, temporal logic

**Benefits:**
- ✅ Leverage LLM's extraction power
- ✅ Constrain errors with deterministic validation
- ✅ Preserve provenance at every step
- ✅ Enable human review at validation boundaries

**Implementation:**
```
User Input → LLM Extraction → Structured Proposal → Reasoning Validator → Neo4j Write
                ↓                      ↓                    ↓
          [Entities, Dates]    [Schema Compliance]   [Authority Match]
```

**Critical Insight:** LLMs propose; reasoning models validate. Never trust LLM output directly into the graph.

---

### **1.2.2 Subject-Anchored Subgraph Pattern**

**Problem:** Historical research is thematic, not entity-centric. Users explore "Roman Civil War" or "Hellenistic Philosophy," not individual persons in isolation.

**Solution:** **SubjectConcepts** serve as **thematic anchors** for subgraph queries:

```cypher
// Query pattern: Start with subject, traverse to entities and relationships
MATCH (subject:SubjectConcept {backbone_fast: 'fst01411640'})  // Roman Civil War
MATCH (subject)<-[:CLASSIFIED_BY]-(entity)
MATCH (entity)-[r:CAUSED|PARTICIPATED_IN]->(event)
WHERE event.start_date >= '-0050-01-01' AND event.end_date <= '-0044-01-01'
RETURN subject, entity, r, event
```

**Why This Matters:**
- ✅ **Thematic queries:** Historians ask questions about subjects, not entity IDs
- ✅ **Scoped context:** Agents work within subject domains, not global graph
- ✅ **Faceted exploration:** Subjects have political/military/legal facets for refined queries
- ✅ **RAG integration:** Each agent maintains subject-scoped vector stores

**Architectural Impact:**
- SubjectConcepts are **first-class citizens**, not tags
- Entity→Subject relationships are **mandatory** for entities to be discoverable
- Agent routing uses Subject→LCC mappings (not entity types)

---

### **1.2.3 Structure vs. Topics Separation (ONTOLOGY_PRINCIPLES)**

**Problem:** Historical events can be "about" multiple topics. How do we organize knowledge without redundant subject hierarchies?

**Solution:** **FAST principles** separate **structure** (organization) from **topics** (aboutness):

**Structure (Classification):**
- LCC classes: DG (Roman history), DF (Greek history), DS (Asia)
- Hierarchical navigation path
- Used for agent routing and organization
- **One primary structure per entity**

**Topics (Aboutness):**
- FAST headings: "Military tactics," "Political philosophy," "Trade routes"
- Multiple topics per entity
- Used for semantic search and thematic queries
- **Many topics per entity**

**Example:**
```cypher
// Julius Caesar entity
(caesar:Human {
  // STRUCTURE (classification)
  backbone_lcc: 'DG261.C35',  // Roman biography - single organizational path
  
  // TOPICS (aboutness)
  backbone_fast: ['fst01411640', 'fst01779841', 'fst01204885'],
               // Roman Civil War, Generals, Statesmen - multiple topics
  backbone_lcsh: ['Caesar, Julius', 'Rome--History--Civil War, 49-45 B.C.']
})
```

**Critical Distinction:**
- **Structure:** Where does this belong in the classification system? (One answer)
- **Topics:** What is this about? (Many answers)

**Benefits:**
- ✅ Avoid redundant subject hierarchies (no need for "Political Events" AND "Military Events" hierarchies)
- ✅ Enable faceted search (filter by multiple topics)
- ✅ Support multiple perspectives (same entity relevant to different topics)
- ✅ Align with library science principles (FAST/LCC designed for this)

**Source:** ONTOLOGY_PRINCIPLES.md (2025-12-26)

---

### **1.2.4 CIDOC-CRM Relationship**

**Question:** Why build Chrystallum when CIDOC-CRM (ISO 21127:2023) already exists for cultural heritage information?

**Answer:** Chrystallum **extends** CIDOC-CRM's event-centric foundation with historical research capabilities.

#### **What CIDOC-CRM Provides (Foundation)**

✅ **Event-centric model:** E5_Event, E21_Person, E53_Place, E52_Time-Span  
✅ **Temporal/spatial relationships:** P4_has_time-span, P7_took_place_at  
✅ **Museum interoperability:** ISO 21127:2023 standard, RDF/OWL compatibility  
✅ **Provenance tracking:** E31_Document, production events  

#### **What CIDOC-CRM Does NOT Provide (Gaps)**

❌ **Library backbone standards:** No FAST, LCC, LCSH, MARC properties  
❌ **Systematic historical date handling:** Supports temporal data but doesn't standardize ISO 8601 negative years (BCE)  
❌ **Action structure vocabularies:** Events are generic (E5_Event, E7_Activity) without goal/trigger/action/result semantics  
❌ **Wikidata alignment:** Can link to external vocabularies but not built-in systematic QID mapping  
❌ **Agent-based construction methodology:** CIDOC-CRM is a modeling standard, not an LLM-reasoning workflow  

#### **Chrystallum's Unique Value Propositions**

1. **Embedded Library Standards (CRITICAL)**
   - Every entity has `backbone_fast`, `backbone_lcc`, `backbone_lcsh`, `backbone_marc` properties
   - Enables direct library catalog integration and LCC-based agent routing
   - CIDOC-CRM has no equivalent

2. **Systematic ISO 8601 Historical Dates (CRITICAL)**
   - All dates: ISO 8601 format (`-0049-01-10` for 49 BCE)
   - `date_precision` property (year/month/day/circa)
   - `temporal_uncertainty` flag
   - Enables consistent temporal queries across data sources
   - CIDOC-CRM supports temporal data but doesn't mandate format

3. **Action Structure Vocabularies (CRITICAL)**
   - Relationships have `goal_type`, `trigger_type`, `action_type`, `result_type` properties
   - Structured narrative semantics (not just generic events)
   - Enables queries like "Find all military actions triggered by political opportunities"
   - CIDOC-CRM has no equivalent

4. **Wikidata Alignment Built-In (IMPORTANT)**
   - Entity types → Wikidata QIDs systematic mapping
   - Action types → Wikidata property alignment
   - Enables SPARQL federation queries
   - CIDOC-CRM can link but not systematic

5. **Two-Stage LLM-Reasoning Architecture (UNIQUE)**
   - LLM extraction → deterministic validation workflow
   - Evidence-aware claims with provenance chains
   - Multi-agent specialist coordination
   - CIDOC-CRM is a modeling standard, not operational architecture

#### **Hybrid Architecture Decision**

**Approach:** Use CIDOC-CRM as **foundation**, extend with Chrystallum features

```cypher
// CIDOC-CRM Base (Event-centric model)
(event:Event {
  // CIDOC-CRM alignment
  cidoc_crm_class: 'E5_Event',
  cidoc_crm_version: '8.0',
  iso_standard: 'ISO 21127:2023',
  
  // Chrystallum Extensions (Unique Features)
  backbone_fast: 'fst01411640',           // Library standards
  backbone_lcc: 'DG241-269',
  start_date: '-0049-01-10',              // Systematic ISO 8601
  date_precision: 'day',
  action_type: 'MIL_ACT',                 // Action structure
  goal_type: 'POL',
  qid: 'Q644312',                         // Wikidata alignment
  confidence: 0.95,                       // Evidence tracking
  validation_status: 'verified'
})

// CIDOC-CRM temporal pattern (standard compliance)
(event)-[:P4_has_time-span]->(timeSpan:TimeSpan {
  P82a_begin_of_the_begin: '-0049-01-10T00:00:00',
  P82b_end_of_the_end: '-0049-01-10T23:59:59'
})
```

**Benefits:**
- ✅ Museum/archival compatibility (via CIDOC-CRM compliance)
- ✅ Historical research features (via Chrystallum extensions)
- ✅ International standard alignment (ISO 21127:2023 base)
- ✅ Best of both worlds

**Implementation Phases:**
1. **Phase 1 (Current):** Use CIDOC-CRM classes, add Chrystallum properties
2. **Phase 2 (Future):** Full P4_has_time-span temporal modeling if museum integration required
3. **Phase 3 (Optional):** CRMgeo (geographic extensions) or CRMinf (inference modeling) if specific needs arise

**Source:** CIDOC-CRM_vs_Chrystallum_Comparison.md (2025-12-26)

**See:** Appendix L (CIDOC-CRM Integration Guide) for technical implementation details

---

## **1.3 System Scope**

**Historical Periods Covered:**
- Ancient Mediterranean (Greece, Rome, Near East): 3000 BCE - 500 CE
- Medieval Europe: 500 - 1500 CE
- Early Modern: 1500 - 1800 CE (initial coverage)

**Entity Types Supported:** 127 types across 14 categories  
**Relationship Types:** 235 canonical types with action structure vocabularies  
**Authority Standards:** LCC, FAST, LCSH, MARC, Wikidata, PeriodO, TGN, Pleiades, CIDOC-CRM  

**Out of Scope (V1.0):**
- Modern history (post-1800 primary focus)
- Real-time event tracking
- Social network analysis (future enhancement)
- Archaeological site excavation data (use CIDOC-CRM CRMarchaeo extension if needed)

---

## **1.4 Key Design Decisions**

### **1.4.1 Why LCC Instead of Dewey?**

**Coverage Analysis:**
- **LCC D class (History):** 100% coverage for ancient/medieval history
- **Dewey 930-999:** 12.3% equivalent granularity

**Specific Examples:**
- LCC: `DG261.C35` (Julius Caesar biography)
- Dewey: `937.05092` (Roman Republic biography - generic)

**Decision:** Use LCC as **primary** classification backbone  
**Source:** LCC_AGENT_ROUTING.md (2025-12-26)  
**See:** Section 4.11 (Agent Routing Architecture)

---

### **1.4.2 Why Two-Level Agent Granularity (FAST + LCC)?**

**Problem:** How granular should specialist agents be?
- Too coarse: "Ancient History Agent" lacks domain expertise
- Too fine: "Julius Caesar Specialist Agent" causes agent proliferation

**Solution:** **Two-level hierarchy**

**Level 1: FAST Broad Topics (22 agents)**
- `fst01411640` - Rome--History--Civil War, 49-45 B.C.
- `fst01204885` - Rome--History--Republic, 265-30 B.C.
- Creates manageable agent count

**Level 2: LCC Subdivisions (Dynamic Routing)**
- `DG261.C35` - Biography: Julius Caesar
- `DG62-63` - Military history
- Routes within Level 1 agent scope

**Benefits:**
- ✅ Prevents agent proliferation (22 specialists vs. 1000s)
- ✅ Maintains domain expertise (not generic "ancient history")
- ✅ Enables hierarchical routing (FAST → LCC → specific query)

**Example Routing:**
```
User: "Tell me about Caesar's military tactics"
  → FAST: fst01411640 (Roman Civil War) → Roman History Agent
    → LCC: DG261.C35 (Caesar biography) → RAG query within agent
      → Specific tactics from agent's vector store
```

**Source:** Subject_Agent_Granularity_Strategy.md (2025-12-26)  
**See:** Section 5.4 (Agent Granularity Strategy)

---

### **1.4.3 Why Calendar Normalization?**

**Problem:** Historical sources use different calendar systems, creating false confidence degradation.

**Example:**
- **Julian calendar:** "October 5, 1582"
- **Gregorian calendar:** "October 15, 1582" (same day!)
- **Without normalization:** System sees date conflicts, lowers confidence
- **With normalization:** System recognizes same date in different systems

**Solution:** **Canonical ISO 8601 dates with calendar metadata**

```cypher
(event:Event {
  start_date: '1582-10-05',           // Canonical: Julian to Gregorian
  start_date_original: '1582-10-05',  // Source value
  calendar_system: 'Julian',          // Metadata
  date_precision: 'day'
})
```

**Normalization Rules:**
- Pre-1582-10-15: Assume Julian unless stated
- Post-1582-10-15: Assume Gregorian unless stated
- BCE dates: Always ISO 8601 negative years (`-0049` for 49 BCE)
- Store original + normalized for provenance

**Impact:**
- ✅ Prevents false confidence degradation from calendar mismatches
- ✅ Enables accurate temporal queries across calendar systems
- ✅ Preserves source fidelity (original dates retained)

**Source:** Historical_Dating_Schema_Disambiguation.md (2025-12-26)  
**See:** Section 3.6 (Temporal Modeling), Appendix E (Temporal Authority Alignment)

---

# **2. System Overview**

## **2.1 Conceptual Model**

Chrystallum organizes knowledge in **six layers**:

1. **Entity Layer:** Real-world things (persons, places, events, works)
2. **Subject Layer:** Conceptual organization (topics, disciplines, classifications via LCC/FAST/LCSH)
3. **Agent Layer:** Specialist reasoners scoped by subjects and periods
4. **Claims Layer:** Evidence-based assertions with provenance and validation
5. **Relationship Layer:** Semantic connections between entities with action structure
6. **Technology Layer:** Implementation (Neo4j, LangGraph, Python, React)

**Data Flow:**
```
User Input → LLM Extraction → Claim Proposal → Agent Validation → Neo4j Write
    ↓             ↓                  ↓               ↓              ↓
[Text]      [Entities, Dates]  [Structured]  [Verified]     [Canonical Graph]
```

---

## **2.2 W5H1 Framework (Conceptual Lens)**

Historical research asks six fundamental questions. Chrystallum's ontology answers them:

| Question | Chrystallum Answer | Node/Property |
|----------|-------------------|---------------|
| **Who?** | Entities (Human, Organization, Dynasty) | `:Human`, `:Organization`, `:Dynasty` |
| **What?** | Entities (Event, Activity, Object, Work) | `:Event`, `:Activity`, `:Object`, `:Work` |
| **When?** | Temporal backbone (Year, Period, date properties) | `:Year`, `:Period`, `start_date`, `end_date`, PeriodO |
| **Where?** | Geographic entities (Place with TGN/Pleiades) | `:Place`, `pleiades_id`, `tgn_id`, coordinates |
| **Why?** | Action structure (`goal_type`, `trigger_type`) | Relationship metadata, `:Claim` justification |
| **How?** | Action structure (`action_type`, `result_type`) | Relationship metadata, process descriptions |

**Architectural Integration:**
- **Who/What:** Entity Layer (Section 3)
- **When:** Temporal Modeling (Section 3.6) + PeriodO (Appendix E)
- **Where:** Geographic Integration (Appendix F) + TGN/Pleiades
- **Why/How:** Action Structure Vocabularies (Appendix B) + Claims Layer (Section 6)

**Source:** Proposed_Knowledge_Structure.md (2025-12-26)

---

## **2.3 Multi-Canon Architecture**

Chrystallum aligns with **nine authority standards** simultaneously:

| Standard | Purpose | Coverage | Implementation |
|----------|---------|----------|----------------|
| **LCC** | Classification backbone | History (D class 100%) | `backbone_lcc` property, agent routing |
| **FAST** | Faceted subject headings | Topical, geographic, chronological | `backbone_fast` arrays, subject topics |
| **LCSH** | Subject heading authority | Library catalog compatibility | `backbone_lcsh` arrays, variant forms |
| **MARC** | Bibliographic standard | Work identification | `backbone_marc` for works and authorities |
| **Wikidata** | Linked open data | Entity identification | `qid` properties, SPARQL federation |
| **CIDOC-CRM** | Cultural heritage ontology | Museum interoperability | `cidoc_crm_class`, property mappings |
| **PeriodO** | Period authority | Temporal period definitions | `:Period` nodes, `periodo_id` |
| **TGN** | Geographic names | Ancient place authority | `:Place` nodes, `tgn_id` |
| **Pleiades** | Ancient geography | Mediterranean archaeology | `:Place` nodes, `pleiades_id` |

**Why Multiple Authorities?**
- Different domains use different standards (libraries = LCC, museums = CIDOC-CRM, archaeology = Pleiades)
- Cross-domain queries require alignment (e.g., "Find all museum objects from Pleiades locations described in FAST subjects")
- Authority disambiguation (multiple IDs increase confidence)

**Alignment Strategy:** Triple alignment pattern (Section 7.2, Appendix L)

---

## **2.4 Evidence Architecture**

Every assertion in Chrystallum has **explicit provenance chains**:

```
Source (Work/Document)
  → Passage/Citation (specific text)
    → Agent Extraction (who, when, how)
      → Claim (structured assertion)
        → Belief (confidence-weighted conclusion)
          → Review (validation decision)
            → Entity/Relationship (canonical graph)
```

**Chain Properties:**
- **Backward traceability:** From any entity, query the claims that support it
- **Forward traceability:** From any source, query the entities it contributes to
- **Temporal tracking:** Know when each assertion was made and by whom
- **Confidence propagation:** Higher-tier sources → higher confidence claims

**Benefits:**
- ✅ Transparent research: "Why does the graph say this?"
- ✅ Dispute resolution: Multiple conflicting claims visible with evidence
- ✅ Historical scholarship: Track evolution of interpretations
- ✅ Trust calibration: Users see confidence levels and sources

**See:** Section 6 (Claims Layer), Section 10 (Quality Assurance)

---

[Content continues with Sections 3-12... this is where the body sections would continue]
