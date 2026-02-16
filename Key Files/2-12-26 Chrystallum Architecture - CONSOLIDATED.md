# **Chrystallum Architecture Specification**
**Version:** 3.2 Consolidated  
**Date:** February 12, 2026  
**Status:** Draft for Review

---

## **Document Purpose**

This document is the **authoritative architectural specification** for Chrystallum, a multi-agent knowledge graph system designed for historical research. It consolidates:

- Core ontology layers (Entity, Subject, Agent, Claims, Relationships)
- Implementation architecture (LangGraph orchestration, Neo4j storage)
- Authority standard alignment (LCC, FAST, LCSH, MARC, Wikidata, CIDOC-CRM)
- Operational governance (validation, quality, maintenance)

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
- Appendix A: Canonical Relationship Types
- Appendix B: Action Structure Vocabularies
- Appendix C: Entity Type Taxonomies
- Appendix D: Subject Facet Classification
- Appendix E: Temporal Authority Alignment
- Appendix F: Geographic Authority Integration
- Appendix G: Legacy Implementation Patterns
- Appendix H: Architectural Decision Records
- Appendix I: Mathematical Formalization (Optional)
- Appendix J: Implementation Examples
- Appendix K: Wikidata Integration Patterns
- Appendix L: CIDOC-CRM Integration Guide
- Appendix M: Identifier Safety Reference
- Appendix N: Property Extensions & Advanced Attributes
- Appendix O: Facet Training Resources Registry
- Appendix P: Semantic Enrichment & Ontology Alignment (CIDOC-CRM/CRMinf)
- Appendix Q: Operational Modes & Agent Orchestration
- Appendix R: Federation Strategy & Multi-Authority Integration
- Appendix S: BabelNet Lexical Authority Integration
- Appendix T: Subject Facet Agent Workflow - "Day in the Life"

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

### **1.2.1 Two-Stage Architecture: LLM Extraction â†’ Reasoning Validation**

**Problem:** LLMs hallucinate. Deterministic reasoning models provide verifiable logic but lack extraction capabilities.

**Solution:** Separate concerns:
1. **LLM Stage:** Extract entities, relationships, temporal data from unstructured text
2. **Reasoning Stage:** Validate extractions against schema, authorities, temporal logic

**Benefits:**
- âœ… Leverage LLM's extraction power
- âœ… Constrain errors with deterministic validation
- âœ… Preserve provenance at every step
- âœ… Enable human review at validation boundaries

**Implementation:**
```
User Input â†’ LLM Extraction â†’ Structured Proposal â†’ Reasoning Validator â†’ Neo4j Write
                â†“                      â†“                    â†“
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
- âœ… **Thematic queries:** Historians ask questions about subjects, not entity IDs
- âœ… **Scoped context:** Agents work within subject domains, not global graph
- âœ… **Faceted exploration:** Subjects have political/military/legal facets for refined queries
- âœ… **RAG integration:** Each agent maintains subject-scoped vector stores

**Architectural Impact:**
- SubjectConcepts are **first-class citizens**, not tags
- Entity † Subject relationships are **mandatory** for entities to be discoverable
- Agent routing uses Subject † LCC mappings (not entity types)

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
- âœ… Avoid redundant subject hierarchies (no need for "Political Events" AND "Military Events" hierarchies)
- âœ… Enable faceted search (filter by multiple topics)
- âœ… Support multiple perspectives (same entity relevant to different topics)
- âœ… Align with library science principles (FAST/LCC designed for this)

**Source:** `md/Architecture/ONTOLOGY_PRINCIPLES.md` (2025-12-26)

---

### **1.2.4 CIDOC-CRM Relationship**

**Question:** Why build Chrystallum when CIDOC-CRM (ISO 21127:2023) already exists for cultural heritage information?

**Answer:** Chrystallum **extends** CIDOC-CRM's event-centric foundation with historical research capabilities.

#### **What CIDOC-CRM Provides (Foundation)**

âœ… **Event-centric model:** E5_Event, E21_Person, E53_Place, E52_Time-Span  
âœ… **Temporal/spatial relationships:** P4_has_time-span, P7_took_place_at  
âœ… **Museum interoperability:** ISO 21127:2023 standard, RDF/OWL compatibility  
âœ… **Provenance tracking:** E31_Document, production events  

#### **What CIDOC-CRM Does NOT Provide (Gaps)**

âŒ **Library backbone standards:** No FAST, LCC, LCSH, MARC properties  
âŒ **Systematic historical date handling:** Supports temporal data but doesn't standardize ISO 8601 negative years (BCE)  
âŒ **Action structure vocabularies:** Events are generic (E5_Event, E7_Activity) without goal/trigger/action/result semantics  
âŒ **Wikidata alignment:** Can link to external vocabularies but not built-in systematic QID mapping  
âŒ **Agent-based construction methodology:** CIDOC-CRM is a modeling standard, not an LLM-reasoning workflow  

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
   - Entity types â†’ Wikidata QIDs systematic mapping
   - Action types â†’ Wikidata property alignment
   - Enables SPARQL federation queries
   - CIDOC-CRM can link but not systematic

5. **Two-Stage LLM-Reasoning Architecture (UNIQUE)**
   - LLM extraction â†’ deterministic validation workflow
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
- âœ… Museum/archival compatibility (via CIDOC-CRM compliance)
- âœ… Historical research features (via Chrystallum extensions)
- âœ… International standard alignment (ISO 21127:2023 base)
- âœ… Best of both worlds

**Implementation Phases:**
1. **Phase 1 (Current):** Use CIDOC-CRM classes, add Chrystallum properties
2. **Phase 2 (Future):** Full P4_has_time-span temporal modeling if museum integration required
3. **Phase 3 (Optional):** CRMgeo (geographic extensions) or CRMinf (inference modeling) if specific needs arise

**Source:** `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md` (2025-12-26)

**See:** Appendix L (CIDOC-CRM Integration Guide) for technical implementation details

---

## **1.3 System Scope**

**Historical Periods Covered:**
- Ancient Mediterranean (Greece, Rome, Near East): 3000 BCE - 500 CE
- Medieval Europe: 500 - 1500 CE
- Early Modern: 1500 - 1800 CE (initial coverage)

**Entity Types Supported:** 127 types across 14 categories  
**Relationship Types:** 300 canonical types with action structure vocabularies  
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
**Source:** `md/Architecture/LCC_AGENT_ROUTING.md` (2025-12-26)  
**See:** Section 5.6 (Agent Routing Logic)

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
- âœ… Prevents agent proliferation (22 specialists vs. 1000s)
- âœ… Maintains domain expertise (not generic "ancient history")
- âœ… Enables hierarchical routing (FAST â†’ LCC â†’ specific query)

**Example Routing:**
```
User: "Tell me about Caesar's military tactics"
  â†’ FAST: fst01411640 (Roman Civil War) â†’ Roman History Agent
    â†’ LCC: DG261.C35 (Caesar biography) â†’ RAG query within agent
      â†’ Specific tactics from agent's vector store
```

**Source:** `md/Architecture/Subject_Agent_Granularity_Strategy.md` (2025-12-26)  
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
- âœ… Prevents false confidence degradation from calendar mismatches
- âœ… Enables accurate temporal queries across calendar systems
- âœ… Preserves source fidelity (original dates retained)

**Source:** `md/Architecture/Historical_Dating_Schema_Disambiguation.md` (2025-12-26)  
**See:** Section 3.4 (Temporal Modeling Architecture), Appendix E (Temporal Authority Alignment)

## 1.5 Domain Adaptability: Beyond History

While the current implementation of Chrystallum is optimized for historical research, the underlying architecture serves as a domain-agnosticÂ **Epistemological Engine**Â designed for high-stakes evidence processing. The system separates theÂ **Universal Core**Â (reasoning, evidence tracking, agent orchestration) from theÂ **Domain Pack**Â (ontologies, authorities, classification standards).

This modular design allows the architecture to be re-skinned for other evidence-heavy domainsâ€”such as Law, Intelligence Analysis, or Corporate Strategyâ€”by swapping the authority modules while retaining the core logic of truth construction.

## 1.5.1 The Universal Core ("The Operating System")

These architectural components are fundamental to any system requiring rigorous validation of unstructured text:

- **Evidence-Aware Claims Architecture:**Â The pipeline (`Source`Â $\to$Â `Extraction`Â $\to$Â `Claim`Â $\to$Â `Validation`) is universal. Whether the source is a 1st-century chronicle (History) or a sworn deposition (Law), the requirement to trace an assertion back to a specific line of text remains identical.
    
- **Two-Stage Validation Pattern:**Â The separation ofÂ **LLM Extraction**Â (probabilistic proposal) fromÂ **Deterministic Validation**Â (rule-based verification) enables the use of AI in high-stakes environments where hallucination is unacceptable.
    
- **Multi-Agent Orchestration:**Â The pattern of using stateless, specialized agents to reason against a schema is transferable. A "Military Historian Agent" checking troop movements uses the same logic as a "Tort Law Agent" checking liability elements.
    

## 1.5.2 The Domain Pack ("The Cartridge")

Adaptation requires replacing the specific semantic "cartridges" used for classification and validation:

|Component|Historical Configuration (Current)|Legal Configuration (Example)|
|---|---|---|
|**Classification**|**LCC Class D**Â (History)|**LCC Class K**Â (Law) /Â **West Key Number System**|
|**Ontology**|**CIDOC-CRM**Â (Events, Cultural Heritage)|**LKIF**Â (Legal Knowledge Interchange Format)|
|**Entities**|`Person`,Â `Place`,Â `Event`,Â `Dynasty`|`Plaintiff`,Â `Defendant`,Â `Contract`,Â `Statute`|
|**Backbone**|**PeriodO**Â (Temporal),Â **Pleiades**Â (Spatial)|**Jurisdiction**Â (e.g., SDNY),Â **Statutes of Limitation**|
|**Validation**|Historical Consensus & Source Criticality|**Stare Decisis**Â & Rules of Evidence|

## 1.5.3 Use Case Example: Legal Discovery

In a legal context, Chrystallum transforms from a historical analyzer into aÂ **Case Construction Engine**:

- **Ingestion:**Â Instead of ancient texts, the system ingests discovery corpora (emails, contracts, depositions).
    
- **Entity Resolution:**Â "Crossing the Rubicon" becomes "The Merger Meeting of Jan 10."
    
- **Argumentation:**Â TheÂ **CRMinf**Â logic used to infer historical intent is repurposed to inferÂ **legal intent**Â (_mens rea_) or knowledge, linking disparate facts (an email, a calendar entry, a bank transfer) into a coherent, evidence-backed legal argument.
    

**Conclusion:**Â Chrystallum is not merely a historical tool; it is a general-purpose architecture forÂ **structured knowledge construction from unstructured evidence**, applicable wherever truth must be derived from text with verifiable provenance.

## 1.5.4 Simple Explanation

## 1. To a Friend (The "Dinner Party" Explanation)

"You know how ChatGPT hallucinates when you ask it about specific historical details? I'm building a system called **Chrystallum** that fixes that.

Instead of just letting an AI make things up, I built a two-stage engine. First, an AI reads historical texts—like a biography of Caesar—and extracts facts. But instead of trusting those facts immediately, it passes them to a second, strict logic layer that checks them against real library standards and timelines. It’s like having an impulsive grad student find the data and a grumpy, tenure-track professor verify it before it goes into the database.

The cool part? It organizes everything by _subject_ rather than just keywords. So if you ask about the 'Roman Civil War,' it knows exactly which generals, battles, and political laws are relevant because it uses the same classification system the Library of Congress uses. It’s basically a hallucination-proof history engine."

---

## 2. To a CTO (The "Architecture & Stack" Explanation)

"Chrystallum is a **deterministic knowledge graph platform** designed to solve the provenance and hallucination problems inherent in RAG systems.

We use a **two-stage pipeline**:

1. **Ingestion & Extraction (Probabilistic):** LLM agents parse unstructured historical texts to propose entities and relationships.
    
2. **Validation & Write (Deterministic):** A LangGraph-orchestrated reasoning layer validates these proposals against a strict ontology (CIDOC-CRM extension) and authority files (Wikidata, LCC, FAST).
    

**The Stack:**

- **Storage:** Neo4j graph database acting as the ground truth.
    
- **Orchestration:** LangGraph for multi-agent coordination.
    
- **Ontology:** We map entities to canonical authorities—Wikidata QIDs for identity, Library of Congress (LCC) for classification, and PeriodO for temporal bounding.
    

**Key differentiator:** We treat 'Subjects' (like _Roman Civil War_) as first-class graph nodes that anchor subgraphs. This solves the context window problem by allowing agents to retrieve pre-validated, thematically scoped clusters of data rather than doing expensive vector similarity searches across the entire dataset."

---

## 3. To a CEO (The "Value & Vision" Explanation)

"Chrystallum is an **Epistemological Engine**—a system that turns unstructured text into verified, high-value knowledge assets.

While we are piloting this with historical data, the core innovation is domain-agnostic. We have solved the 'AI Trust' problem by separating **extraction** (finding data) from **validation** (verifying data).

Most AI systems today are 'black boxes'—you put a document in and hope the summary is true. Chrystallum creates an **auditable evidence chain**: every fact in our system can be traced back to the specific sentence in the specific document it came from.

**Business Value:**

1. **Trust:** We eliminate AI hallucinations in high-stakes environments.
    
2. **Scalability:** We use standard library classifications (LCC) to route data, meaning the system gets smarter and more organized as it grows, rather than more chaotic.
    
3. **Adaptability:** Today it validates Roman history; tomorrow it could validate legal contracts, intelligence reports, or corporate compliance documents just by swapping the underlying ontology."

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
User Input â†’ LLM Extraction â†’ Claim Proposal â†’ Agent Validation â†’ Neo4j Write
    â†“             â†“                  â†“               â†“              â†“
[Text]      [Entities, Dates]  [Structured]  [Verified]     [Canonical Graph]
```

---

## **2.2 W5H1 Framework (Conceptual Lens)**

Historical research asks six fundamental questions. Chrystallum's ontology answers them:

| Question | Chrystallum Answer | Node/Property |
|----------|-------------------|---------------|
| **Who?** | Entities (Human, Organization, Dynasty) | `:Human`, `:Organization`, `:Dynasty` |
| **What?** | Entities (Event, Object, Work) | `:Event`, `:Object`, `:Work` |
| **When?** | Temporal backbone (Year, Period, date properties) | `:Year`, `:Period`, `start_date`, `end_date`, PeriodO |
| **Where?** | Geographic entities (Place with TGN/Pleiades) | `:Place`, `pleiades_id`, `tgn_id`, coordinates |
| **Why?** | Action structure (`goal_type`, `trigger_type`) | Relationship metadata, `:Claim` justification |
| **How?** | Action structure (`action_type`, `result_type`) | Relationship metadata, process descriptions |

**Architectural Integration:**
- **Who/What:** Entity Layer (Section 3)
- **When:** Temporal Modeling (Section 3.6) + PeriodO (Appendix E)
- **Where:** Geographic Integration (Appendix F) + TGN/Pleiades
- **Why/How:** Action Structure Vocabularies (Appendix B) + Claims Layer (Section 6)

**Source:** `md/Architecture/Proposed_Knowledge_Structure.md` (2025-12-26)

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
  â†’ Passage/Citation (specific text)
    â†’ Agent Extraction (who, when, how)
      â†’ Claim (structured assertion)
        â†’ Belief (confidence-weighted conclusion)
          â†’ Review (validation decision)
            â†’ Entity/Relationship (canonical graph)
```

**Chain Properties:**
- **Backward traceability:** From any entity, query the claims that support it
- **Forward traceability:** From any source, query the entities it contributes to
- **Temporal tracking:** Know when each assertion was made and by whom
- **Confidence propagation:** Higher-tier sources â†’ higher confidence claims

**Benefits:**
- âœ… Transparent research: "Why does the graph say this?"
- âœ… Dispute resolution: Multiple conflicting claims visible with evidence
- âœ… Historical scholarship: Track evolution of interpretations
- âœ… Trust calibration: Users see confidence levels and sources

**See:** Section 6 (Claims Layer), Section 10 (Quality Assurance)

---

# **PART II: CORE ONTOLOGY LAYERS**

---

# **3. Entity Layer**

## **3.0 Overview**

The **Entity Layer** represents real-world historical entities: people, places, events, organizations, works, and related historical structures. Entities are the **nodes** in the knowledge graph, connected by relationships.

**Core Principles:**
1. **Entity types are semantic, not structural:** `Human` vs `Organization` matters for reasoning
2. **Entities are identified by authorities:** `qid` (Wikidata), `viaf_id` (persons), `pleiades_id` (places)
3. **Entities have temporal existence:** `start_date`, `end_date`, `date_precision`
4. **Entities are classified by subjects:** `backbone_lcc`, `backbone_fast` for discovery

### **3.0.1 Canonical First-Class Node Set (Normative)**

The canonical first-class node set for active implementation is:
- `SubjectConcept`
- `Human`
- `Gens`
- `Praenomen`
- `Cognomen`
- `Event`
- `Place`
- `Period`
- `Dynasty`
- `Institution`
- `LegalRestriction`
- `Claim`
- `Organization`
- `Year`
- `Work`
- `Material`
- `Object`
- `ConditionState`

**Deprecated (replaced or merged):**
- ~~`Position`~~ → Merged into `Institution` (with typed `HELD_BY` edge) or modeled as typed `Event` (appointment/tenure)
- ~~`Activity`~~ → Concrete instances route to `Event` (with appropriate `action_type`); abstract patterns route to `SubjectConcept`

**Policy lock-ins:**
- `Subject` and `Concept` are legacy labels and MUST map to `SubjectConcept`.
- `Person` is legacy wording and MUST map to `Human`.
- `Communication` is NOT a first-class node label; it is modeled as a facet/domain axis in Section 3.3.
- `Position` is deprecated as of 2026-02-16; use Institution-edge patterns (§3.1.11 migration guide).
- `Activity` is deprecated as of 2026-02-16; use Event or SubjectConcept routing (§3.1.14 migration guide).

---

## **3.1 Core Entity Types** 

### **3.1.1 Human**

**Node Label:** `:Human`

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"hum_000123"`)
- `name` (string): Primary name (e.g., `"Gaius Julius Caesar"`)
- `qid` (string): Wikidata QID (e.g., `"Q1048"`)
- `entity_type` (string): Always `"Human"`

**Optional Properties:**
- `birth_date` (ISO 8601 string): e.g., `"-0100-07-12"` for 100 BCE
- `death_date` (ISO 8601 string): e.g., `"-0044-03-15"` for 44 BCE  
- `date_precision` (string): `"day"`, `"month"`, `"year"`, `"circa"`
- `gender` (string): `"male"`, `"female"`, `"unknown"`
- `viaf_id` (string): Virtual International Authority File ID
- `backbone_lcc` (string): Library of Congress Classification
- `backbone_fast` (array): FAST topic IDs
- `backbone_lcsh` (array): LCSH subject headings

**Authority Alignment:**
- `cidoc_crm_class`: `"E21_Person"`
- `cidoc_crm_version`: `"8.0"`
- `iso_standard`: `"ISO 21127:2023"`

**Temporal Properties:**
- `calendar_system` (string): `"Julian"`, `"Gregorian"`, `"Roman AUC"`
- `temporal_uncertainty` (boolean): Flag for uncertain dates

**Optional Edges:**
- `BORN_IN` â†’ `:Place` (birthplace)
- `DIED_IN` â†’ `:Place` (deathplace)
- `MEMBER_OF` â†’ `:Organization`
- `PART_OF_GENS` â†’ `:Gens` (Roman naming)
- `HAS_POSITION` â†’ `:Position` (offices held)
- `PARTICIPATED_IN` â†’ `:Event`
- `LIVED_DURING` â†’ `:Period`
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept` (classification)
- `SUBJECT_OF` â†’ `:Claim` (provenance)

---

### **3.1.2 Place**

**Node Label:** `:Place`

**Purpose:** Represents stable geographic identity (abstract concept of a location that persists across time).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"plc_000456"`)
- `label` (string): Primary place name (e.g., `"Rome"`)
- `qid` (string): Wikidata QID (e.g., `"Q220"`)
- `entity_type` (string): Always `"Place"`

**Optional Properties:**
- `pleiades_id` (string): Pleiades gazetteer ID for ancient places
- `tgn_id` (string): Getty Thesaurus of Geographic Names ID
- `latitude` (float): Decimal degrees (modern/primary location)
- `longitude` (float): Decimal degrees
- `place_type` (string): `"city"`, `"province"`, `"region"`, `"settlement"`, `"natural_feature"`
- `modern_country` (string): Modern political entity

**Authority Alignment:**
- `cidoc_crm_class`: `"E53_Place"`

**Required Edges:**
- `LOCATED_IN` â†’ `:Place` (spatial hierarchy)

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

**Note:** For historical "shifting borders" problem, use **`:PlaceVersion`** pattern (see below).

---

### **3.1.2.1 PlaceVersion (Temporal Instantiation)**

**Node Label:** `:PlaceVersion`

**Purpose:** Represents time-scoped and authority-scoped instantiation of a place (e.g., "Roman Province of Syria, 1st Century CE").

**Required Properties:**
- `pver_id` (string): Internal unique identifier (e.g., `"pver_00123_01"`)
- `label` (string): Temporal description (e.g., `"Antioch (Roman Period)"`)
- `start_date` (ISO 8601 string): Period start
- `end_date` (ISO 8601 string): Period end
- `authority` (string): Source of definition (e.g., `"Pleiades"`, `"TGN"`)
- `confidence` (float): Authority confidence (0.0-1.0)

**Required Edges:**
- `VERSION_OF` â†’ `:Place` (links to stable identity)
- `HAS_GEOMETRY` â†’ `:Geometry` (spatial representation)

**Optional Edges:**
- `BROADER_THAN` â†’ `:PlaceVersion` (administrative hierarchy)
- `NARROWER_THAN` â†’ `:PlaceVersion`

**Use Pattern:**
```cypher
(:Event)-[:TOOK_PLACE_AT]->(:PlaceVersion)-[:VERSION_OF]->(:Place)
```

---

### **3.1.2.2 Geometry (Spatial Data)**

**Node Label:** `:Geometry`

**Purpose:** Stores geographic coordinates/shapes; allows multiple conflicting geometries for same place version.

**Required Properties:**
- `geo_id` (string): Internal unique identifier
- `wkt` (string): Well-Known Text format (e.g., `"POINT(36.16 36.20)"`, `"POLYGON(...)"`)
- `source` (string): Data source (e.g., `"Wikidata"`, `"Pleiades"`)
- `method` (string): Derivation method (e.g., `"centroid"`, `"survey"`, `"estimate"`)

**Required Edges:**
- None (connected via incoming `HAS_GEOMETRY` from PlaceVersion)

---

### **3.1.3 Event**

**Node Label:** `:Event`

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"evt_000987"`)
- `label` (string): Event description (e.g., `"Battle of Actium"`)
- `qid` (string): Wikidata QID (e.g., `"Q193304"`)
- `entity_type` (string): Always `"Event"`

**Temporal Properties:**
- `start_date` (ISO 8601 string): Event start (e.g., `"-0049-01-10"`)
- `end_date` (ISO 8601 string): Event end
- `date_precision` (string): `"day"`, `"month"`, `"year"`, `"circa"`
- `calendar_system` (string): Original calendar system
- `temporal_uncertainty` (boolean)

**Optional Properties:**
- `event_type` (string): `"battle"`, `"treaty"`, `"revolt"`, `"election"`, `"assassination"`
- `casualties_estimate` (integer): Estimated casualties
- `location_qid` (string): Primary location Wikidata ID

**Authority Alignment:**
- `cidoc_crm_class`: `"E5_Event"`

**Action Structure:**
- `action_type` (string): From action structure vocabulary (Appendix B)
- `goal_type` (string): From goal type vocabulary
- `trigger_type` (string): From trigger vocabulary
- `result_type` (string): From result vocabulary

**Required Edges:**
- `OCCURRED_AT` â†’ `:Place` or `:PlaceVersion` (location)
- `OCCURRED_DURING` â†’ `:Period` (temporal context)
- `STARTS_IN_YEAR` â†’ `:Year` (start year)
- `ENDS_IN_YEAR` â†’ `:Year` (end year)

**Optional Edges:**
- `PARTICIPANT` â†’ `:Human`, `:Organization`
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.4 Period**

**Node Label:** `:Period`

**Purpose:** Represents named historiographic periods with fuzzy temporal boundaries (e.g., "Roman Republic", "Julio-Claudian Dynasty").

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"prd_000111"`)
- `label` (string): Period name (e.g., `"Roman Republic"`)
- `start` (string): Nominal start year (e.g., `"-0510"`)
- `end` (string): Nominal end year (e.g., `"-0027"`)
- `entity_type` (string): Always `"Period"`

**Optional Properties (Fuzzy Bounds):**
- `earliest_start` (string): Earliest plausible start (e.g., `"-0520"`)
- `latest_start` (string): Latest plausible start (e.g., `"-0500"`)
- `earliest_end` (string): Earliest plausible end (e.g., `"-0035"`)
- `latest_end` (string): Latest plausible end (e.g., `"-0020"`)
- `authority` (string): Source authority (e.g., `"PeriodO"`, `"Wikidata"`)
- `authority_uri` (string): External identifier (PeriodO URI)
- `culture` (string): Cultural frame (e.g., `"Roman"`, `"Greek"`)
- `facet` (string): Facet classification (e.g., `"political"`, `"economic"`, `"technical"`)
- `qid` (string): Wikidata QID
- `spatial_coverage` (array): Geographic scope (e.g., `["Italy", "Mediterranean"]`)

**Required Edges:**
- `STARTS_IN_YEAR` â†’ `:Year` (nominal start)
- `ENDS_IN_YEAR` â†’ `:Year` (nominal end)

**Optional Edges:**
- `BROADER_THAN` â†’ `:Period` (hierarchy, e.g., Empire > Early Empire)
- `NARROWER_THAN` â†’ `:Period`
- `ALIGNED_WITH` â†’ `:Period` (cross-authority alignment)
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.5 Year**

**Node Label:** `:Year`

**Purpose:** Atomic temporal entity used for chronological alignment, period boundaries, event dating, and claim temporal grounding. Forms the **global Year backbone** from at least -2000 to 2025.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"year_-0049"`)
- `year` (integer): Astronomical year notation (BCE = negative, e.g., `-49`)
- `label` (string): Human-readable label (e.g., `"49 BCE"`)
- `entity_type` (string): Always `"Year"`

**Optional Properties:**
- `iso` (string): Zero-padded ISO 8601 year (e.g., `"-0049"`)
- `calendar` (string): Default calendar system (e.g., `"proleptic Julian"`)

**Required Edges:**
- `FOLLOWED_BY` â†’ `:Year` (next year in sequence)
- `PRECEDED_BY` â†’ `:Year` (previous year in sequence)

**Optional Edges:**
- `PART_OF` â†’ `:Decade` / `:Century` / `:Millennium` (if hierarchy nodes exist)

**Usage Pattern:** Every temporally grounded entity or claim must tether to one or more Year nodes.

---

### **3.1.6 Organization**

**Node Label:** `:Organization`

**Purpose:** Represents political bodies, military units, religious colleges, administrative institutions.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"org_000222"`)
- `label` (string): Organization name (e.g., `"Roman Senate"`)
- `qid` (string): Wikidata QID (e.g., `"Q41410"`)
- `entity_type` (string): Always `"Organization"`

**Optional Properties:**
- `organization_type` (string): `"political_body"`, `"military_unit"`, `"religious_college"`, `"administrative"`, `"commercial"`
- `founding_date` (ISO 8601 string)
- `dissolution_date` (ISO 8601 string)

**Authority Alignment:**
- `cidoc_crm_class`: `"E74_Group"`

**Required Edges:**
- `LOCATED_IN` â†’ `:Place`

**Optional Edges:**
- `HAS_MEMBER` â†’ `:Human`
- `PARTICIPATED_IN` â†’ `:Event`
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.7 Institution**

**Node Label:** `:Institution`

**Purpose:** Represents abstract but real-world structures (legal institutions, political institutions, religious institutions, administrative systems). Distinct from Organizations (which have members) and Concepts (which are abstract categories).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"inst_000333"`)
- `label` (string): Institution name (e.g., `"Roman Dictatorship"`, `"Consulship"`)
- `entity_type` (string): Always `"Institution"`

**Optional Properties:**
- `institution_type` (string): `"legal"`, `"political"`, `"religious"`, `"administrative"`, `"educational"`
- `founding_date` (ISO 8601 string)
- `abolition_date` (ISO 8601 string)

**Required Edges:**
- `LOCATED_IN` â†’ `:Place`

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.8 Dynasty**

**Node Label:** `:Dynasty`

**Purpose:** Represents ruling families or succession lines.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"dyn_000444"`)
- `label` (string): Dynasty name (e.g., `"Julio-Claudian Dynasty"`)
- `start` (string): Dynasty start year (e.g., `"-0027"`)
- `end` (string): Dynasty end year (e.g., `"0068"`)
- `entity_type` (string): Always `"Dynasty"`

**Required Edges:**
- `RULED` â†’ `:Place` (geographic extent)
- `HAS_MEMBER` â†’ `:Human` (rulers)

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.9 LegalRestriction**

**Node Label:** `:LegalRestriction`

**Purpose:** Represents laws, decrees, bans, privileges, legal statuses.

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"law_000555"`)
- `label` (string): Law name (e.g., `"Senatus Consultum Ultimum"`)
- `date` (string): Enactment date (e.g., `"-0052"`)
- `entity_type` (string): Always `"LegalRestriction"`

**Required Edges:**
- `ISSUED_BY` â†’ `:Organization`
- `APPLIED_TO` â†’ `:Human`, `:Organization`, `:Place`

**Optional Edges:**
- `HAS_SUBJECT_CONCEPT` â†’ `:SubjectConcept`
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.1.10 Work**

**Node Label:** `:Work`

**Purpose:** Represents texts, inscriptions, manuscripts, artifacts, and modern scholarship. Critical for provenance chain (Work â†’ Passage â†’ Claim).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"wrk_000666"`)
- `title` (string): Work title (e.g., `"Life of Caesar"`)
- `qid` (string): Wikidata QID (e.g., `"Q2896"`)
- `entity_type` (string): Always `"Work"`

**Optional Properties:**
- `author` (string): Author name or QID
- `publication_date` (ISO 8601 string)
- `work_type` (string): `"ancient_text"`, `"modern_monograph"`, `"inscription"`, `"manuscript"`, `"article"`
- `source_tier` (string): `"Primary"`, `"Secondary"`, `"Tertiary"`
- `language` (string): ISO 639-1 language code

**Authority Alignment:**
- `cidoc_crm_class`: `"E73_Information_Object"`

**Required Edges:**
- `WRITTEN_BY` â†’ `:Human`

**Optional Edges:**
- `ABOUT` â†’ `:Entity`, `:SubjectConcept` (aboutness)
- `CITED_IN` â†’ `:Claim` (provenance)
- `RETRIEVED_FROM` â†’ `:RetrievalContext` (LLM extraction context)

---

### **3.1.11 Position (DEPRECATED)**

⚠️ **Status:** Deprecated as of 2026-02-16. Do not use for new implementations.

**Previous Purpose:** Represented offices, titles, and roles (e.g., Consul, Tribune, Governor).

**Removal Rationale:**
- `Position` redundantly duplicates semantics already expressible via `Institution` + typed edge properties
- In CIDOC-CRM terms, holding an office is an **E7_Activity** (appointment/tenure event), not a distinct entity
- Biographic facet (Section 3.3) models office-holding as career sequence on the Human node

**Migration Guide:**
- **Option A (preferred):** Use rich `HELD_POSITION` edge on Institution with properties: `{position_type, start_date, end_date, source}`
- **Option B:** Model office-holding as typed `Event` with `event_type: "appointment"`

---

### **3.1.11a ConditionState**

**Node Label:** `:ConditionState`

**Purpose:** Represents time-scoped condition observations of artifacts. Enables tracking condition changes over time without full object versioning (mirrors PlaceVersion and PeriodVersion patterns).

**Required Properties:**
- `entity_id` (string): Internal ID (e.g., `"cond_000123"`)
- `state_label` (string): Condition description (e.g., `"mint"`, `"worn"`, `"corroded"`, `"overstruck"`)
- `entity_type` (string): Always `"ConditionState"`

**Optional Properties:**
- `description` (string): Detailed condition notes
- `assessment_date` (ISO 8601 string): When this condition was observed/recorded
- `source` (string): Museum catalog, publication, or assessment source
- `method` (string): Assessment method (e.g., `"visual"`, `"XRF"`, `"X-ray"`, `"conservation report"`)
- `confidence` (float 0-1): Confidence level of assessment

**Edges:**
- `APPLIES_TO` -> `:Object` (which object this condition describes)
- `ASSESSED_DURING` -> `:Period` or `:Year` (when the observation was made)
- `SUBJECT_OF` -> `:Claim` (claims about condition)

**Usage Pattern:**
- Object node remains stable identity
- Each ConditionState is a time-bound observation with provenance
- Query: (obj:Object)-[:HAS_CONDITION_STATE]->(cond:ConditionState) to track state history
- Optional: Denormalize current best-known condition on Object as `current_condition` property (derived from latest validated ConditionState)

---

### **3.1.12 Material**

**Node Label:** `:Material`

**Purpose:** Represents physical materials (E57_Material in CIDOC-CRM). Critical for artifact composition tracking and material culture queries.

**Required Properties:**
- `entity_id` (string): Internal ID (e.g., `"mat_000123"`)
- `label` (string): Canonical name (e.g., `"gold"`, `"marble"`)
- `entity_type` (string): Always `"Material"`

**Authority / Classification Properties:**
- `aat_id` (string): Getty AAT ID (primary authority for materials)
- `aat_pref_label` (string): AAT preferred label
- `aat_broader` (array): Parent AAT IDs (SKOS hierarchy, one direction)
- `wikidata_qid` (string, optional): Wikidata material item
- `bm_material_id` (string, optional): British Museum materials thesaurus ID

**Type Flags (denormalized for query performance):**
- `material_family` (string): "metal", "stone", "ceramic", "glass", "organic", "composite"
- `metal_type` (string, optional): "precious", "base" (for gold/silver vs iron/bronze)
- `period_relevance` (array): e.g., ["Roman Republic", "Hellenistic"]

**Edges:**
- `BROADER_THAN` -> `:Material` (SKOS hierarchy; store one direction only)
- `USED_IN` -> `:Object` (inverse of Object-MADE_OF, optional convenience edge)

---

### **3.1.13 Object**

**Node Label:** `:Object`

**Purpose:** Represents artifacts, tools, weapons, coins, inscriptions, sculptures (E22_Human-Made_Object in CIDOC-CRM). Critical for archaeological and material-culture reasoning.

**Required Properties:**
- `entity_id` (string): Internal ID (e.g., `"obj_000999"`)
- `label` (string): Short description (e.g., `"Denarius of Caesar"`)
- `entity_type` (string): Always `"Object"`

**Optional Descriptive Properties:**
- `object_type` (string): "coin", "weapon", "tool", "inscription", "sculpture", "vessel", etc.
- `date_from` / `date_to` (ISO 8601 strings): Object production/use range
- `cidoc_crm_class` (string): Usually `"E22_Human-Made_Object"`

**Authority / Classification Properties:**
- `aat_id` (string): AAT object-type ID (primary authority)
- `aat_pref_label` (string): AAT preferred label
- `aat_broader` (array): AAT hierarchy
- `wikidata_qid` (string, optional): Wikidata item
- `bm_object_type_id` (string, optional): British Museum object type
- `backbone_fast` (array): FAST topics  (e.g., "Coins, Roman")
- `backbone_lcc` (string, optional): LCC classification

**Authority Precedence:** AAT -> BM/FISH -> Wikidata -> local

**Edges:**
- `MADE_OF` -> `:Material` (multi-edge; edge props: role, fraction, source, confidence)
- `CREATED_BY` -> `:Human` or `:Organization`
- `FOUND_AT` -> `:Place` or `:PlaceVersion`
- `DATED_TO` -> `:Period` and/or `:Year`
- `DEPICTS` -> `:Human` / `:Event` (iconography)
- `HAS_SUBJECT_CONCEPT` -> `:SubjectConcept` (classification)
- `HAS_CONDITION_STATE` -> `:ConditionState` (time-scoped condition observations)
- `SUBJECT_OF` -> `:Claim` (claims about the object)

---

### **3.1.14 Activity (DEPRECATED)**

[DEPRECATED as of 2026-02-16. Do not use for new implementations.]

**Previous Purpose:** Represented actions, rituals, practices, occupations (abstract patterns of behavior).

**Removal Rationale:**
- Conflates two distinct concepts: things-in-the-world vs. concepts-about-the-world
- Concrete activities (specific triumph, specific trade mission) should route to Event nodes with appropriate action_type
- Abstract activity patterns ("Agriculture as a practice", "the institution of Triumph") should route to SubjectConcept nodes

**Migration Guide:**
- **Concrete instances** -> Event with event_type and action_type properties
- **Abstract patterns** -> SubjectConcept with classification properties (e.g., facet_tag: "occupational")
- Example: A specific triumphus = Event; "Triumph as an institution" = SubjectConcept

---

## **3.2 Roman-Specific Entity Types**

These extend the Human entity model with Roman naming conventions.

### **3.2.1 Gens**

**Node Label:** `:Gens`

**Purpose:** Represents Roman family clans (e.g., Julia, Cornelia, Claudia).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"gens_000001"`)
- `label` (string): Gens name (e.g., `"Julia"`)
- `entity_type` (string): Always `"Gens"`

**Required Edges:**
- `HAS_MEMBER` â†’ `:Human`

**Optional Edges:**
- `SUBJECT_OF` â†’ `:Claim`

---

### **3.2.2 Praenomen**

**Node Label:** `:Praenomen`

**Purpose:** Represents Roman first names (e.g., Gaius, Marcus, Lucius).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"prae_000001"`)
- `label` (string): Praenomen (e.g., `"Gaius"`)
- `abbreviation` (string): Standard abbreviation (e.g., `"C."`)
- `entity_type` (string): Always `"Praenomen"`

---

### **3.2.3 Cognomen**

**Node Label:** `:Cognomen`

**Purpose:** Represents Roman family surnames (e.g., Caesar, Cicero, Brutus).

**Required Properties:**
- `entity_id` (string): Internal unique identifier (e.g., `"cog_000001"`)
- `label` (string): Cognomen (e.g., `"Caesar"`)
- `entity_type` (string): Always `"Cognomen"`

**Optional Properties:**
- `meaning` (string): Etymology or meaning (e.g., `"hairy"` for Caesar)

---

### **3.2.4 AnalysisRun** ðŸŸ¡ **NEW NODE TYPE**

**Node Label:** `:AnalysisRun`

**Purpose:** Represents one execution of the claim evaluation pipeline. Enables re-running analysis and comparing results across evaluation versions.

**Required Properties:**
- `run_id` (string): Unique run identifier (e.g., `"RUN_2026_02_12_001"`)
- `pipeline_version` (string): Version of evaluation pipeline (e.g., `"v1.2"`, `"v2.0_experimental")`

**Optional Properties:**
- `created_at` (ISO 8601 datetime): When analysis run started
- `updated_at` (ISO 8601 datetime): When analysis run completed
- `prompt_set` (string): Identifier for prompt configuration used
- `model_config` (string): Model version/config identifier
- `status` (enum): `"in_progress"`, `"completed"`, `"failed"`

**Required Edges:**
- `HAS_ANALYSIS_RUN` â† `:Claim` (incoming edge from claim being analyzed)

**Related Edges:**
- `HAS_FACET_ASSESSMENT` â†’ `:FacetAssessment` (one per facet evaluated)

**Purpose/Key Insight:**
- Single claim can have multiple AnalysisRuns over time
- Each run contains independent facet assessments
- Enables A/B testing: compare "run v1" vs "run v2" for same claim
- Stores pipeline metadata once per run (not repeated per assessment)

---

### **3.2.5 FacetAssessment**  **NEW NODE TYPE**

**Node Label:** `:FacetAssessment`

**Purpose:** Represents one facet-specific evaluation of a claim within an AnalysisRun. Each claim's AnalysisRun contains multiple FacetAssessments (one per analytical dimension).

**Required Properties:**
- `assessment_id` (string): Unique assessment identifier (e.g., `"FA_CAESAR_POL_001"`)
- `score` (float, 0.0-1.0): Confidence/quality score for this facet
- `status` (enum): `"supported"`, `"challenged"`, `"uncertain"`, `"mostly_supported"`

**Optional Properties:**
- `rationale` (string): Explanation of assessment (e.g., "High confidence based on primary sources")
- `created_at` (ISO 8601 datetime): When assessment created
- `evidence_count` (integer): Number of supporting sources cited

**Required Edges:**
- `HAS_FACET_ASSESSMENT` â† `:AnalysisRun` (incoming edge from parent run)
- [`ASSESSES_FACET`](ASSESSES_FACET) â†’ `:Facet` subclass (e.g., `:PoliticalFacet`, `:MilitaryFacet`)
- [`EVALUATED_BY`](EVALUATED_BY) â†’ `:Agent` (which agent made this assessment)

**Star Pattern Insight:**
- Single claim can have assessments across all 16 facets simultaneously
- Each facet evaluation is independent (political_confidence â‰  military_confidence)
- Each assessment can cite different sources
- Enables UI tabs: "Political view" | "Military view" | "Economic view" etc.
- Enables agent specialization: political expert only evaluates political facets

**Example:**
Battle of Pharsalus (48 BCE) single AnalysisRun with multiple assessments:
```cypher
(run:AnalysisRun {run_id: "RUN_001"})
  -[:HAS_FACET_ASSESSMENT]->(fa1:FacetAssessment {score: 0.95, status: "supported"})
    -[:ASSESSES_FACET]->(mil:MilitaryFacet)
    -[:EVALUATED_BY]->(military_agent)
  -[:HAS_FACET_ASSESSMENT]->(fa2:FacetAssessment {score: 0.92, status: "supported"})
    -[:ASSESSES_FACET]->(pol:PoliticalFacet)
    -[:EVALUATED_BY]->(political_agent)
  -[:HAS_FACET_ASSESSMENT]->(fa3:FacetAssessment {score: 0.80, status: "mostly_supported"})
    -[:ASSESSES_FACET]->(geo:GeographicFacet)
    -[:EVALUATED_BY]->(geography_agent)
```

---

### **3.2.6 FacetCategory**** NEW NODE TYPE**

**Node Label:** `:FacetCategory`

**Purpose:** Organizes 16 analytical facets into semantic categories. Enables UI grouping and agent specialization assignment.

**Required Properties:**
- `key` (string, uppercase enum): Facet category identifier (e.g., `"POLITICAL"`, `"MILITARY"`, `"ECONOMIC"`)
- `label` (string): Display label (e.g., `"Political"`)

**Optional Properties:**
- `definition` (string): Category scope definition
- `color` (hex): UI color for facet category tabs/visualizations

**Related Edges:**
- `IN_FACET_CATEGORY` â† `:Facet` (all facets link to their category)
- `OWNS_CATEGORY` â† `:Agent` (agents specialize in specific facet categories)

**Example:**
```cypher
(:FacetCategory {key: "POLITICAL", label: "Political"})
  â† (:PoliticalFacet {unique_id: "POLITICALFACET_Q3624078"})
  â† (:Agent {agent_id: "AGENT_POLITICAL_V1"})-[:OWNS_CATEGORY]
```

---

## **3.3 Facets (Entity-Level Classification) â€“ Star Pattern Architecture**

Entities can be classified along **17 analytical dimensions** (facets) for multi-dimensional discovery.
Canonical source of truth: `Facets/facet_registry_master.json` (with tabular export at `Facets/facet_registry_master.csv`).
Temporal modeling is handled separately in Section 3.4.

1. **Geographic:** Spatial distribution and location
2. **Political:** Governance, power, authority
3. **Cultural:** Art, literature, customs, identity
4. **Technological:** Tools, methods, innovations
5. **Religious:** Beliefs, practices, institutions
6. **Economic:** Trade, production, finance
7. **Military:** Warfare, tactics, organization
8. **Environmental:** Climate, geography, resources
9. **Demographic:** Population, migration, ethnicity
10. **Intellectual:** Philosophy, science, education
11. **Scientific:** Technical knowledge, inquiry
12. **Artistic:** Visual arts, architecture, aesthetics
13. **Social:** Class, family, social structures
14. **Linguistic:** Languages, writing systems
15. **Archaeological:** Material culture, excavation
16. **Diplomatic:** Treaties, alliances, negotiations
17. **Communication:** mass media, messaging, propaganda, and ideology transmission

Facet policy:
- `Communication` remains a facet/domain dimension and is not materialized as `:Communication` in the first-class node set.

**Implementation:** Entities link to SubjectConcepts representing these facets (see Section 4):
```cypher
(:Human)-[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {facet: "Political"})
```

---

## **3.4 Temporal Modeling Architecture**

### **3.4.1 Year Backbone**

The **Year backbone** is a continuous linked list of Year nodes from at least -2000 to 2025 (extensible).

**Purpose:**
- Global temporal grid for all historical reasoning
- Atomic temporal resolution
- Period boundary anchoring
- Event dating precision

**Structure:**
```cypher
(:Year {year: -49})-[:FOLLOWED_BY]->(:Year {year: -48})
(:Year {year: -48})-[:PRECEDED_BY]->(:Year {year: -49})
```

**Usage:** Every temporally grounded entity or claim tethers to Year nodes via `STARTS_IN_YEAR`, `ENDS_IN_YEAR`, or `DURING`.

---

### **3.4.2 Period Classification (Tiered)**

Not all temporal spans are periods. Chrystallum uses a **four-tier classification**:

**Tier 1: Historical Periods** (keep as `:Period`)
- Extended spans (decades+)
- Widely used in historiography
- Coherent political/social/cultural patterns
- Examples: Migration Period, Dutch Golden Age, Viking Age

**Tier 2: Events / Phases** (relabel as `:Event`)
- Short duration (< 5-10 years)
- Wars, crises, campaigns
- Examples: Crisis of the Third Century, Reign of Terror, Phoney War

**Tier 3: Institutional Spans** (use `:InstitutionalSpan` or `:Period` with flag)
- Lifetimes of courts, offices, archives
- Administrative intervals, not historiographic periods
- Examples: Rehnquist Court, Birmingham pen trade

**Tier 4: Problematic Entries** (remove or reclassify)
- Disciplines masquerading as periods
- Suspicious date ranges
- Overly broad/vague spans

**Source:** Period data seeded from `Temporal/time_periods.csv` (Wikidata extraction) and `Temporal/periodo-dataset.csv` (PeriodO authority).

---

### **3.4.3 Faceted Periods (Stacked Timelines via Facet Vectors)**

**Vector Jump Pattern:** Periods link to Facet nodes enabling temporal vectors across analytical dimensions.

**Structure:**
```cypher
(:Period {label: "Late Republic", qid: "Q17167"})
  -[:HAS_POLITICAL_FACET]->
(:PoliticalFacet {label: "Roman Republic", unique_id: "POLITICALFACET_Q17167"})

(:Period {label: "Late Republic", qid: "Q17167"})
  -[:HAS_ECONOMIC_FACET]->
(:EconomicFacet {label: "Late Republican economy", unique_id: "ECONOMICFACET_Q17167E"})

(:Period {label: "Late Republic", qid: "Q17167"})
  -[:HAS_MILITARY_FACET]->
(:MilitaryFacet {label: "Imperial wars", unique_id: "MILITARYFACET_Q17167M"})
```

**Period Classification by Facet:**
- Political dimension: "Late Republic" = governance under republican institutions
- Economic dimension: "Late Republican economy" = transition to monetary economy
- Military dimension: "Imperial wars" = conquest phase military operations
- [13 other facet vectors...]

**Query Pattern:** Retrieve all periods for a culture grouped by facet, aligned via `STARTS_IN_YEAR`/`ENDS_IN_YEAR`/`IN_FACET_CATEGORY` to generate stacked timeline visualizations:

```cypher
MATCH (p:Period {culture: "Roman"})-[:STARTS_IN_YEAR]->(y:Year)
MATCH (p)-[:HAS_POLITICAL_FACET|:HAS_MILITARY_FACET|:HAS_ECONOMIC_FACET]->(f:Facet)
MATCH (f)-[:IN_FACET_CATEGORY]->(cat:FacetCategory)
RETURN y.year, cat.key, f.label
ORDER BY y.year, cat.key
// Result: stacked timeline with [Political][Military][Economic] rows per year
```

---

### **3.4.4 Authority Alignment (PeriodO, LCSH)**

Period nodes integrate with two external authorities:

**1. PeriodO (Temporal Period Authority):**
- Curated period definitions with URIs
- Properties: `authority = "PeriodO"`, `authority_uri = <PeriodO URI>`
- Enriches Period nodes with scholarly consensus boundaries

**2. LCSH (Library of Congress Subject Headings):**
- Maps periods to subject headings via `:SubjectConcept`
- Pattern: `(:Period)-[:ALIGNED_WITH]->(:SubjectConcept {authority_id: <LCSH ID>})`
- Enables library catalog interoperability

**Source Files:**
- `Temporal/periodo-dataset.csv`: PeriodO data
- `Temporal/time_periods.csv`: seed period set
- `Temporal/period_classification_decisions.csv`: period classification decisions

---

### **3.4.5 Event-Period-Year Wiring (Minimal Pattern)**

To avoid over-edging (e.g., long-running events creating thousands of edges), use **minimal temporal wiring**:

**Pattern:**
```cypher
(:Event {start_date: "-0049-01-10", end_date: "-0044-03-15"})
  -[:OCCURRED_DURING]->(:Period)
  -[:STARTS_IN_YEAR]->(:Year {year: -49})
  -[:ENDS_IN_YEAR]->(:Year {year: -44})
```

**Intermediate years** (e.g., -48, -47, -46, -45) are **not** stored as edges but expanded at query/UI time.

**Exception:** For specific UIs requiring fast year-by-year browsing, optionally materialize `ACTIVE_IN_YEAR` edges, but test scale carefully.

---

## **3.5 Schema Enforcement & Constraints**

### **3.5.1 Uniqueness Constraints**

```cypher
-- Core Identity
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE;

CREATE CONSTRAINT human_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.entity_id IS UNIQUE;

CREATE CONSTRAINT place_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.place_id IS UNIQUE;

CREATE CONSTRAINT claim_id_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE;

-- External Authority Keys
CREATE CONSTRAINT qid_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.qid IS UNIQUE;

CREATE CONSTRAINT viaf_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.viaf_id IS UNIQUE;
```

---

### **3.5.2 Architectural Decisions**

**1. SKOS Directionality: `BROADER_THAN` Only**
- **Rationale:** Reduces graph density by 50%. The inverse (`NARROWER_THAN`) is implied and handled at query time by traversing `<-[:BROADER_THAN]-`.
- **Decision:** Store only `BROADER_THAN` relationships in the graph.

**2. Facet Policy (Hybrid)**
- **Primary Facet:** Stored as property for speed (e.g., `Period.facet = "Political"`)
- **Complex Facets:** Stored as nodes for hierarchy (e.g., `(:Period)-[:HAS_FACET]->(:Facet {label: "Naval Warfare"})`)
- **Rationale:** Balances query performance with expressiveness.

---

## **3.6 Example Cypher Patterns**

### **Create a Human Entity**
```cypher
CREATE (p:Human {
  entity_id: "hum_000123",
  name: "Gaius Julius Caesar",
  qid: "Q1048",
  birth_date: "-0100-07-12",
  death_date: "-0044-03-15",
  gender: "male",
  viaf_id: "286265178",
  cidoc_crm_class: "E21_Person"
})
```

### **Link Human to Gens**
```cypher
MATCH (p:Human {qid: "Q1048"}), (g:Gens {label: "Julia"})
CREATE (p)-[:PART_OF_GENS]->(g)
```

### **Create an Event with Temporal and Spatial Context**
```cypher
MATCH (place:PlaceVersion {label: "Rubicon River (49 BCE)"}),
      (period:Period {label: "Roman Republic"}),
      (year_start:Year {year: -49})
CREATE (e:Event {
  entity_id: "evt_000987",
  label: "Caesar Crosses the Rubicon",
  qid: "Q159950",
  start_date: "-0049-01-10",
  event_type: "military_crossing",
  action_type: "deliberate_defiance",
  cidoc_crm_class: "E5_Event"
})
CREATE (e)-[:TOOK_PLACE_AT]->(place)
CREATE (e)-[:OCCURRED_DURING]->(period)
CREATE (e)-[:STARTS_IN_YEAR]->(year_start)
```

### **Link Work to SubjectConcept (Aboutness)**
```cypher
MATCH (w:Work {title: "Life of Caesar"}),
      (sc:SubjectConcept {authority_id: "sh85115055"})
CREATE (w)-[:ABOUT]->(sc)
```

---

# **4. Subject Layer**

## **4.0 Subject Layer Overview**

The **Subject Layer** provides the **conceptual backbone** of Chrystallum's ontology. It defines:

- The **SubjectConcept** node type (conceptual categories, topics, themes)
- The **facet system** (16 active analytical dimensions; see `Facets/facet_registry_master.json`)
- The **SKOS-like hierarchy** (polyhierarchical classification)
- The **multi-authority metadata model** (LCSH, FAST, LCC, Dewey, Wikidata, VIAF, GND)
- The **Topic Spine** (canonical curated hierarchy)
- The **CIP â†’ QID â†’ LCC â†’ LCSH â†’ FAST chain** (cross-authority alignment)
- The **Academic Discipline model**
- The **Entity â†’ Subject mapping rules**
- The **Work â†’ Subject aboutness model**
- The **Agent domain assignment logic**

**Core Principle:** There is **no separate Concept entity**â€”all conceptual categories are **SubjectConcepts**.

**Relationship to Entities:**

| Layer | Represents | Examples |
|-------|-----------|----------|
| **Entity Layer** | Things in the world | Caesar, Rome, Battle of Actium |
| **Subject Layer** | Concepts about the world | Roman politics, civil war, dictatorship |

---

## **4.0.1 Foundational Principles: Structure vs. Topics**

**CRITICAL DISTINCTION** (from ONTOLOGY_PRINCIPLES.md, see also ADR-002 in Appendix H):

### **LCC = Structure (ONE Path)**
- **Purpose:** Organizational backbone for classification
- **Pattern:** ONE entity gets ONE LCC assignment (primary classification)
- **Example:** Julius Caesar â†’ `DG` (Roman History)
- **Usage:** Agent routing, primary subject determination
- **Metaphor:** Library shelf location (one place)

### **FAST = Topics (MANY Tags)**
- **Purpose:** Semantic discovery across multiple dimensions
- **Pattern:** ONE entity gets MANY FAST assignments (faceted tagging)
- **Example:** Julius Caesar â†’ `Roman politics`, `Military leaders`, `Assassinations`, `Civil war`
- **Usage:** Cross-domain queries, thematic research
- **Metaphor:** Index entries (many keywords)

**Why This Matters:**
- **Prevents redundant hierarchies:** LCC provides the primary organizational path, FAST provides multi-dimensional discovery
- **Enables precision + recall:** LCC for focused classification, FAST for broad discovery
- **Supports agent specialization:** Agents can specialize by LCC class (structural expertise) or FAST topic (thematic expertise)

**Implementation:**
```cypher
// LCC: ONE primary classification
(:Human {entity_id: "hum_000123"})
  -[:HAS_PRIMARY_LCC]->(:SubjectConcept {lcc_class: "DG"})

// FAST: MANY topical tags
(:Human {entity_id: "hum_000123"})
  -[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {fast_id: "fst01234567"})
(:Human {entity_id: "hum_000123"})
  -[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {fast_id: "fst07654321"})
(:Human {entity_id: "hum_000123"})
  -[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {fast_id: "fst09876543"})
```

**Source:** `md/Architecture/ONTOLOGY_PRINCIPLES.md` (2025-12-26) â€” foundational architectural decision

---

## **4.1 SubjectConcept Node Schema**

### **Node Label**

```cypher
:SubjectConcept
```

### **Purpose**

Represents a conceptual category, topic, theme, or subject heading, including:
- Topical subjects (e.g., "Roman politics")
- Academic disciplines (e.g., "History", "Archaeology")
- LCSH/FAST headings
- LCC classes
- CIP categories
- Topic Spine nodes
- Facets

### **Required Properties**

| Property | Type | Example |
|----------|------|---------|
| `subject_id` | string | `"subj_000123"` |
| `label` | string | `"Romeâ€”Politics and governmentâ€”510â€“30 B.C."` |
| `facet` | string | `"POLITICAL"` (uppercase canonical key) |

**Facet Normalization Rule:**
- `facet` property values MUST match canonical keys from `Facets/facet_registry_master.json`
- All facet keys are UPPERCASE (e.g., `"POLITICAL"`, `"MILITARY"`, `"ECONOMIC"`, etc.; see Section 4.2 for complete list)
- Lowercase or mixed-case facet values are NOT valid (prevents case-collision bugs in queries)
- Rationale: Deterministic filtering, consistent routing, union-safe deduplication

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `authority_id` | string | `"sh85115055"` | LCSH ID |
| `fast_id` | string | `"fst01234567"` | FAST ID |
| `lcc_class` | string | `"DG"` | LCC class |
| `lcc_subclass` | string | `"DG209"` | LCC subclass |
| `cip_code` | string | `"22.01"` | CIP category (Classification of Instructional Programs) |
| `qid` | string | `"Q123456"` | Wikidata concept QID |
| `broader_label` | string | `"Roman history"` | For convenience |
| `narrower_labels` | array | `["Roman Republic"]` | For convenience |
| `discipline` | boolean | `true` | Flag for academic disciplines |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `BROADER_THAN` | SubjectConcept | SKOS broader relationship |

**Note:** Architectural decision (see Section 3.5.2) is to store **`BROADER_THAN` only** to reduce graph density by 50%. The inverse (`NARROWER_THAN`) is implied and handled at query time by traversing `<-[:BROADER_THAN]-`.

### **Optional Edges**

- `ALIGNED_WITH` â†’ SubjectConcept (cross-authority alignment)
- `HAS_FACET` â†’ Facet (complex facet hierarchies)
- `ABOUT_ENTITY` â†’ Entity (semantic grounding)
- `ABOUT_PERIOD` â†’ Period  
- `ABOUT_EVENT` â†’ Event
- `SUBJECT_OF` â†’ Claim (provenance)

---

## **4.2 Facets (16 Analytical Dimensions)**

Chrystallum uses **16 active facets** for multi-dimensional classification of entities and subjects.
Canonical source of truth: `Facets/facet_registry_master.json` (with tabular export at `Facets/facet_registry_master.csv`).
Temporal modeling is handled separately in Section 3.4.

1. **Geographic:** Spatial distribution and location
2. **Political:** Governance, power, authority
3. **Cultural:** Art, literature, customs, identity
4. **Technological:** Tools, methods, innovations
5. **Religious:** Beliefs, practices, institutions
6. **Economic:** Trade, production, finance
7. **Military:** Warfare, tactics, organization
8. **Environmental:** Climate, geography, resources
9. **Demographic:** Population, migration, ethnicity
10. **Intellectual:** Philosophy, science, education
11. **Scientific:** Technical knowledge, inquiry
12. **Artistic:** Visual arts, architecture, aesthetics
13. **Social:** Class, family, social structures
14. **Linguistic:** Languages, writing systems
15. **Archaeological:** Material culture, excavation
16. **Diplomatic:** Treaties, alliances, negotiations

### **Facet Node Schema**

**Node Label:** `:Facet`

**Required Properties:**
| Property | Type | Example |
|----------|------|---------|
| `facet_id` | string | `"facet_political"` |
| `label` | string | `"Political"` |

**Required Edges:**
- `HAS_FACET` â†’ SubjectConcept (for complex facet hierarchies)

### **Facet Policy (Hybrid Approach)**

**Primary Facet (Property):** Stored as property for fast queries
```cypher
Period {facet: "Political"}
```

**Complex Facets (Nodes):** Stored as nodes for hierarchical facets
```cypher
(:Period)-[:HAS_FACET]->(:Facet {label: "Naval Warfare"})
```

**Rationale:** Balances query performance with expressiveness.

---

## **4.3 SKOS-Like Hierarchy**

SubjectConcepts form a **polyhierarchical** structure using SKOS-inspired relationships:

### **Relationships**

- `BROADER_THAN`: Parent concept (stored)
- `NARROWER_THAN`: Child concept (implied, query via inverse)
- `RELATED_TO`: Associative relationship (optional)

### **Example Hierarchy**

```
"Ancient history"
    BROADER_THAN
        "Roman history"
            BROADER_THAN
                "Roman Republic"
                "Roman Empire"
```

### **Cypher Example**

```cypher
MATCH (parent:SubjectConcept {label: "Roman history"})
MATCH (child:SubjectConcept {label: "Roman Republic"})
CREATE (parent)-[:BROADER_THAN]->(child)

// Query inverse (narrower concepts)
MATCH (parent:SubjectConcept {label: "Roman history"})
      <-[:BROADER_THAN]-(child)
RETURN child.label
```

---

## **4.4 Multi-Authority Metadata Model**

Each SubjectConcept can carry metadata from **multiple authority standards** for cross-domain interoperability:

| Authority | Property | Example | Purpose |
|-----------|----------|---------|---------|
| **LCSH** | `authority_id` | `"sh85115055"` | Library catalog compatibility |
| **FAST** | `fast_id` | `"fst01234567"` | Faceted subject headings |
| **LCC** | `lcc_class`, `lcc_subclass` | `"DG"`, `"DG209"` | Classification backbone |
| **CIP** | `cip_code` | `"22.01"` | Academic program alignment |
| **Wikidata** | `qid` | `"Q12107"` | Linked open data |
| **Dewey** | `dewey_decimal` | `"937"` | Library classification (optional) |
| **VIAF** | `viaf_id` | `"123456789"` | Authority control (optional) |
| **GND** | `gnd_id` | `"4076899-5"` | German National Library (optional) |

**Authority Precedence for SubjectConcepts (Normalization Rule):**

**Tier 1 (Preferred):**
- LCSH (Library of Congress Subject Headings) - established scholarly standard; query-optimized
- FAST (Faceted Application of Subject Terminology) - complementary faceted tagging for cross-domain discovery

**Tier 2 (Secondary):**
- LCC (Library of Congress Classification) - structural backbone for primary classification only
- CIP (Classification of Instructional Programs) - academic discipline alignment

**Tier 3 (Tertiary):**
- Wikidata (QID) - linked open data reference; use when LCSH/FAST coverage gaps exist
- Dewey, VIAF, GND - legacy/supplementary authorities

**Implementation Rule:**
1. When creating SubjectConcept: Prefer LCSH/FAST â†' LCC/CIP â†' Wikidata â†' other
2. When updating: Enrich with lower-tier authorities without replacing higher-tier mappings
3. When querying: Check Tier 1 first; fall through to Tier 3 if needed

**Rationale:** LCSH/FAST are domain-optimized for historical scholarship; Wikidata as fallback; mirrors Entity Layer authority policy (Material/Object precedence)

### **Purpose**

- Unify legacy cataloging systems
- Support agent domain assignment (Section 5)
- Support claim classification (Section 6)
- Enable authority crosswalks

---

## **4.5 Entity â†’ Subject Mapping Rules**

Entities link to SubjectConcepts to establish classification and discoverability.

### **Mapping Pattern**

```cypher
(entity)-[:HAS_SUBJECT_CONCEPT]->(subjectConcept)
```

### **Mapping Rules by Entity Type**

| Entity Type | Mapping Strategy | Example |
|-------------|------------------|---------|
| **Human** | Biography, occupation, era, associated events | Caesar â†’ "Roman politics", "Military leaders", "Dictators" |
| **Event** | Event type, participants, location, historical period | Battle of Actium â†’ "Naval battles", "Roman civil wars", "Greco-Roman warfare" |
| **Place** | Geographic hierarchy, cultural regions | Rome â†’ "Ancient cities", "Italian history", "Capital cities" |
| **Period** | Historical classification, culture, facet | Roman Republic â†’ "Ancient Rome", "Republican government", "Classical period" |
| **Work** | Aboutness (see Section 4.6) | Plutarch's *Life of Caesar* â†’ "Roman biography", "Classical literature" |
| **Organization** | Organization type, function, domain | Roman Senate â†’ "Legislative bodies", "Roman institutions", "Republican government" |

### **Cypher Example**

```cypher
MATCH (p:Human {qid: "Q1048"})
MATCH (sc:SubjectConcept {authority_id: "sh85115055"})
CREATE (p)-[:HAS_SUBJECT_CONCEPT]->(sc)
```

---

## **4.6 Work â†’ Subject Aboutness Model**

Works (texts, inscriptions, scholarship) link to SubjectConcepts via the **aboutness** relationship to support RAG retrieval and claim provenance.

### **Aboutness Pattern**

```cypher
(work)-[:ABOUT]->(subjectConcept)
```

### **Example**

```cypher
MATCH (w:Work {title: "Life of Caesar"})
MATCH (sc:SubjectConcept {label: "Roman politics"})
CREATE (w)-[:ABOUT]->(sc)
```

### **Aboutness Supports**

- **RAG retrieval:** Find relevant texts by subject (Section 5.5)
- **Claim provenance:** Trace claims to source subjects (Section 6.2)
- **Agent training:** Define agent expertise domains (Section 5.3)

---

## **4.7 Topic Spine (Canonical Curated Hierarchy)**

The **Topic Spine** is a **canonical, curated hierarchy** of SubjectConcepts that:

- Spans all 16 active facets
- Provides a stable conceptual backbone
- Supports agent routing (Section 5.6)
- Supports claim classification (Section 6.2)
- Serves as the primary navigation structure

### **Topic Spine Structure**

```
History
    Ancient History
        Roman History
            Roman Republic
                Roman Politics
                    Civil War
                        Caesar's Dictatorship
```

### **Node Label** (Optional)

Can use `:TopicSpine` label or property flag:
```cypher
SubjectConcept {is_spine_node: true}
```

### **Spine Edges**

- `SPINE_PARENT`: Explicit spine hierarchy
- `SPINE_CHILD`: Inverse

---

## **4.8 CIP â†’ QID â†’ LCC â†’ LCSH â†’ FAST Chain**

This is the **cross-authority alignment pipeline** for subject normalization and agent domain inference.

### **Chain Flow**

```
CIP category (modern academic classification)
    â†“ maps to
Wikidata QID (linked open data concept)
    â†“ maps to
LCC class/subclass (library classification backbone)
    â†“ maps to
LCSH heading (library subject authority)
    â†“ maps to
FAST heading (faceted subject tags)
```

### **Example Mapping**

| Layer | Example | ID |
|-------|---------|-----|
| **CIP** | History | 22.01 |
| **QID** | History (concept) | Q11772 |
| **LCC** | World History | D |
| **LCSH** | History | sh85061212 |
| **FAST** | History | fst00958235 |

### **Purpose**

- Unify modern academic classification (CIP) with library standards (LCC/LCSH)
- Enable agent domain assignment via multiple authority paths
- Support subject normalization across different source materials

---

## **4.9 Academic Discipline Model**

Academic disciplines are modeled as SubjectConcepts with special properties.

### **Discipline Schema**

**Properties:**
- `facet: "Intellectual"`
- `discipline: true`

**Examples:**
- History
- Archaeology
- Classics
- Political Science
- Economics
- Art History
- Philology

### **Discipline Edges**

- `BROADER_THAN` â†’ parent discipline (e.g., History â†’ Ancient History)
- `RELATED_TO` â†’ adjacent disciplines (e.g., History â†” Archaeology)

### **Usage**

- Agent specialization by discipline
- Claim review routing by disciplinary expertise (Section 6.3)
- Interdisciplinary query support

### **Discipline Flag Usage in SFA Training Initialization**

**Critical Pattern:** When a SubjectFacetAgent (SFA) is instantiated for a discipline + facet pair, the `discipline: true` flag identifies canonical root concepts for ontology building.

**Initialization Algorithm:**
```
1. Query: Find all SubjectConcepts where discipline=true AND facet=TARGET_FACET
2. Root Node Selection: SFA adopts matched concepts as roots
3. Ontology Building: SFA traverses via BROADER_THAN* to build hierarchical ontology
```

**Example:** MilitarySFA with facet MILITARY finds root concepts like "Military Science", then builds: Military Science â†' Naval Warfare â†' Trireme Tactics â†' ...

**Rationale:**
- `discipline: true` marks canonical entry points for agent specialization
- Prevents SFAs from adopting arbitrary concepts as roots
- Gates SFA scope (e.g., Military SFA doesn't treat "Economic History" as root)
- Enables reproducible SFA initialization across sessions
- Supports disciplinary curriculum alignment (CIP codes â†' discipline roots)

**See Also:**
- Section 5.1: Agent domain assignment (`OWNS_DOMAIN` edges to SubjectConcepts)
- Section 5.2: Subject Agents (domain expertise patterns)
- REAL_AGENTS_DEPLOYED.md: Current SFA instantiation configurations

---

## **4.10 LCC Official Classification Structure**

The **Library of Congress Classification (LCC)** provides the primary **organizational backbone** for Chrystallum.

### **Why LCC?** (See ADR-003, Appendix H)
- **100% coverage** of history domain (vs. Dewey 12.3%)
- **Deep granularity** for ancient history (DG class for Roman history)
- **Institutional standard** for research libraries
- **Authority alignment** with LCSH and MARC

### **LCC Classes**

| Class | Domain |
|-------|--------|
| A | General Works |
| B | Philosophy, Psychology, Religion |
| C | Auxiliary Sciences of History |
| D | World History |
| Eâ€“F | American History |
| G | Geography, Anthropology |
| H | Social Sciences |
| J | Political Science |
| K | Law |
| L | Education |
| M | Music |
| N | Fine Arts |
| P | Language & Literature |
| Q | Science |
| R | Medicine |
| S | Agriculture |
| T | Technology |
| U | Military Science |
| V | Naval Science |
| Z | Bibliography, Library Science |

### **LCC Subclasses (Example: Roman History)**

| Subclass | Coverage |
|----------|----------|
| DG | Italy, Roman History |
| DG11-365 | Italy (general) |
| DG51-190 | Ancient Italy, Rome to 476 CE |
| DG201-365 | Medieval & Modern Italy |

### **LCC Mapping to SubjectConcepts**

```cypher
(subject:SubjectConcept {label: "Roman Republic"})
  -[:HAS_LCC_CLASS]->(:LCC {class: "DG", subclass: "DG83"})
```

---

## **4.11 Agent Domain Assignment via Subject Layer**

Agents define their expertise domains through connections to SubjectConcepts (see Section 5 for details).

### **Domain Definition Pattern**

```cypher
(agent:Agent)-[:OWNS_DOMAIN]->(subjectConcept:SubjectConcept)
```

### **Example**

```cypher
MATCH (agent:Agent {agent_id: "roman_republic_agent"})
MATCH (sc1:SubjectConcept {label: "Roman Republic"})
MATCH (sc2:SubjectConcept {label: "Roman politics"})
MATCH (sc3:SubjectConcept {label: "Civil war"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc1)
CREATE (agent)-[:OWNS_DOMAIN]->(sc2)
CREATE (agent)-[:OWNS_DOMAIN]->(sc3)
```

### **Domain Inference Paths**

Agents can be assigned domains via:
1. **Direct SubjectConcept assignment:** Explicit domain declaration
2. **LCC class coverage:** All SubjectConcepts with specific LCC class
3. **CIP category alignment:** All SubjectConcepts with CIP code
4. **Topic Spine path:** All descendants of a spine node
5. **Facet membership:** All SubjectConcepts with specific facet

---

## **4.12 Subject Evolution & Versioning**

SubjectConcepts evolve over time as vocabularies update and scholarship advances.

### **Versioning Properties**

| Property | Type | Purpose |
|----------|------|---------|
| `created_at` | ISO 8601 string | Creation timestamp |
| `updated_at` | ISO 8601 string | Last modification |
| `deprecated` | boolean | Deprecated flag |
| `replaced_by` | string | Successor subject_id |

### **Evolution Patterns**

1. **New concepts added:** Emerging fields, refined terminology
2. **Deprecated concepts merged:** Consolidation of redundant terms
3. **Authority metadata updated:** New QID, FAST ID, etc.
4. **Crosswalks refined:** Improved LCC/LCSH/FAST alignment

---

## **4.13 Cypher Examples**

### **Create a SubjectConcept**

```cypher
CREATE (sc:SubjectConcept {
  subject_id: "subj_000123",
  label: "Roman politics",
  facet: "Political",
  authority_id: "sh85115055",
  fast_id: "fst01234567",
  lcc_class: "DG",
  qid: "Q12345",
  discipline: false
})
```

### **Link SubjectConcept to LCC Class**

```cypher
MATCH (sc:SubjectConcept {label: "Roman history"})
MATCH (lcc:LCC {class: "DG"})
CREATE (sc)-[:HAS_LCC_CLASS]->(lcc)
```

### **Map Work to SubjectConcept (Aboutness)**

```cypher
MATCH (w:Work {title: "Life of Caesar"})
MATCH (sc:SubjectConcept {label: "Roman Republic"})
CREATE (w)-[:ABOUT]->(sc)
```

### **Agent Domain Assignment**

```cypher
MATCH (agent:Agent {agent_id: "roman_republic_agent"})
MATCH (sc:SubjectConcept {label: "Roman Republic"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc)
```

### **Query BROADER_THAN Hierarchy**

```cypher
// Get all narrower concepts
MATCH (parent:SubjectConcept {label: "Roman history"})
      -[:BROADER_THAN*]->(child)
RETURN child.label, child.lcc_class
```

### **Cross-Authority Lookup**

```cypher
// Find SubjectConcept by multiple authorities
MATCH (sc:SubjectConcept)
WHERE sc.authority_id = "sh85115055"
   OR sc.fast_id = "fst01234567"
   OR sc.qid = "Q12345"
RETURN sc
```

---

# **5. Agent Layer**

## **5.0 Agent Layer Overview**

The **Agent Layer** defines the **intelligent actors** in Chrystallum that perform classification, extraction, reasoning, validation, and coordination.

**Agents** in Chrystallum are **not** LLMsâ€”they are **graph-native reasoning actors** with:
- **Explicit domain scopes** (defined via Subject Layer)
- **Explicit memory** (cached knowledge, previous decisions)
- **Explicit reasoning traces** (transparent decision logic)
- **Explicit retrieval contexts** (RAG patterns)
- **Explicit claim generation and review protocols** (quality assurance)

### **Agent Types**

1. **Subject Agents:** Experts in conceptual domains (e.g., "Roman Republic Specialist")
2. **Entity Agents:** Experts in entity types (e.g., "Event Validator")
3. **Coordinator Agents:** Orchestrators of multi-agent workflows

### **Agent Responsibilities**

- Classify entities and works to SubjectConcepts
- Generate claims from source material (Section 6)
- Review and validate claims (Section 6.3)
- Perform historical reasoning over knowledge graph
- Retrieve evidence via RAG patterns
- Maintain memory of previous decisions
- Coordinate consensus among multiple agents
- Route tasks across the agent ecosystem

---

## **5.1 Agent Node Schema**

### **Node Label**

```cypher
:Agent
```

### **Required Properties**

| Property | Type | Example |
|----------|------|---------|
| `agent_id` | string | `"roman_republic_agent"` |
| `label` | string | `"Roman Republic Specialist"` |
| `agent_type` | string | `"subject"`, `"entity"`, `"coordinator"` |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `description` | string | `"Expert in Roman political history"` | Human-readable description |
| `confidence_calibration` | float | `0.92` | Calibration factor for confidence scores |
| `specialization_level` | string | `"high"`, `"medium"`, `"low"` | Generalist vs specialist |
| `created_at` | ISO 8601 string | `"2026-02-12T10:00:00Z"` | Creation timestamp |
| `version` | string | `"v1.2"` | Agent version identifier |

### **Required Edges**

- `OWNS_DOMAIN` â†’ SubjectConcept (domain expertise)
- `REVIEWED` â†’ Review (validation history)
- `MADE_CLAIM` â†’ Claim (claim authorship)

### **Optional Edges**

- `TRAINED_ON` â†’ Work (training corpus)
- `INCLUDES_CONCEPT` â†’ SubjectConcept (expanded domain)
- `MEMORY_OF` â†’ AgentMemory (cached knowledge)
- `PERFORMED_BY` â†’ Synthesis (reasoning activity)

---

## **5.2 Subject Agents**

**Subject Agents** specialize in **conceptual domains** defined by SubjectConcepts, LCC classes, CIP categories, Topic Spine nodes, and facets.

### **Example**

```
roman_republic_agent (Subject Agent)
    OWNS_DOMAIN â†’ "Roman Republic" (SubjectConcept)
    OWNS_DOMAIN â†’ "Roman politics" (SubjectConcept)
    OWNS_DOMAIN â†’ "Civil war" (SubjectConcept)
```

### **Responsibilities**

- Classify claims by subject
- Review claims within domain expertise
- Generate interpretive claims (synthesis, analysis)
- Detect logical fallacies and inconsistencies
- Perform scholarly synthesis across conflicting claims

### **Cypher Example**

```cypher
CREATE (agent:Agent {
  agent_id: "roman_republic_agent",
  label: "Roman Republic Specialist",
  agent_type: "subject",
  description: "Expert in Roman Republican political history (510-27 BCE)",
  confidence_calibration: 0.93,
  specialization_level: "high",
  created_at: "2026-02-12T10:00:00Z"
})

MATCH (sc1:SubjectConcept {label: "Roman Republic"})
MATCH (sc2:SubjectConcept {label: "Roman politics"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc1)
CREATE (agent)-[:OWNS_DOMAIN]->(sc2)
```

---

## **5.3 Entity Agents**

**Entity Agents** specialize in **entity types** and validate entity-level properties.

### **Example**

```
event_agent (Entity Agent)
    OWNS_ENTITY_TYPE â†’ Event
```

### **Responsibilities**

- Validate entity properties (dates, names, identifiers)
- Detect entity-level inconsistencies
- Classify events by type (battle, treaty, election, etc.)
- Support claim grounding (ensure entities exist before creating claims)

### **Cypher Example**

```cypher
CREATE (agent:Agent {
  agent_id: "event_validator_agent",
  label: "Event Validator",
  agent_type: "entity",
  description: "Validates historical event properties and classifications",
  confidence_calibration: 0.95,
  specialization_level: "medium"
})
```

---

## **5.4 Agent Granularity Strategy (Two-Level Architecture)**

**CRITICAL DESIGN DECISION** (see ADR-004, Appendix H):

Chrystallum uses a **two-level agent routing strategy** to balance expertise precision with scalability.

### **Level 1: FAST Broad Topics (22 Agents)**

**Purpose:** Initial routing to general domain experts

**Example Topics:**
- Ancient History
- Roman History
- Military History
- Political History
- Religious History

**Agent Count:** ~22 broad-topic agents covering major historical domains

**Routing Mechanism:**
```cypher
// User query: "Caesar crosses Rubicon"
// Topic classification: "Roman History" (FAST)
// â†’ Route to roman_history_agent
```

### **Level 2: LCC Subdivisions (Dynamic Routing)**

**Purpose:** Fine-grained expertise via LCC classification within broad topics

**Example LCC Classes (Roman History):**
- DG51-190: Ancient Italy, Rome to 476 CE
- DG83: Roman Republic (510-27 BCE)
- DG290-365: Medieval & Modern Italy

**Agent Count:** Dynamicâ€”agents specialize in LCC subclasses as needed

**Routing Mechanism:**
```cypher
// Within roman_history_agent domain
// LCC classification: DG83 (Roman Republic)
// â†’ Route to roman_republic_specialist_agent (LCC DG83)
```

### **Why Two-Level?**

**Problem:** Single-level routing creates agent proliferation
- Too broad: Agents lack expertise (1 agent for all history)
- Too narrow: Too many agents (100+ specialist agents)

**Solution:** Two-level hierarchy
- **FAST (Level 1):** 22 broad agents (manageable, expert routing)
- **LCC (Level 2):** Dynamic specialists (precise expertise, scales with content)

**Benefits:**
- Prevents agent proliferation (22 base agents, not 100+)
- Maintains deep expertise (LCC specialists for narrow domains)
- Scales naturally (add LCC specialists as content grows)
- Familiar to scholars (FAST and LCC are standard authorities)

**Source:** `md/Architecture/Subject_Agent_Granularity_Strategy.md` (2025-12-26)

---

## **5.5 SubjectConceptAgent â†" SubjectFacetAgent Coordination (SCA â†" SFA)**

**CRITICAL ARCHITECTURAL PATTERN** (Finalized February 15, 2026):

Chrystallum implements a **two-phase agent coordination model** with **selective intelligent routing** for claim creation and multi-facet enrichment.

**Reference:** `SCA_SFA_ROLES_DISCUSSION.md` (complete specification)

### **5.5.1 Agent Types & Roles**

**SubjectConceptAgent (SCA):**
- **Role:** Seed agent & intelligent orchestrator
- **Responsibilities:**
  * Un-faceted exploration (Phase 1: breadth-first)
  * Spawns SubjectFacetAgents (SFAs) on-demand
  * Routes training data to SFAs (Discovery Mode)
  * **Evaluates claims:** Abstract concepts vs Concrete events
  * **Selective routing:** Queues claims for multi-facet review ONLY when warranted
  * Generates bridge claims connecting domains
  * Manages claim lifecycle & convergence detection

**SubjectFacetAgent (SFA):**
- **Role:** Domain-specific experts (18 facets: 16 core + biographic + communication)
- **Facet List:** Archaeological, Artistic, Cultural, Demographic, Diplomatic, Economic, Environmental, Geographic, Intellectual, Linguistic, Military, Political, Religious, Scientific, Social, Technological, **Biographic** (prosopography/person identity), **Communication** (rhetoric/meta-facet)
- **Facets:** Political, Military, Economic, Cultural, Religious, Legal, Scientific, Technological, Environmental, Social, Diplomatic, Administrative, Educational, Artistic, Literary, Philosophical, Medical
- **Responsibilities:**
  * **Training Phase:** Build domain ontologies independently (abstract concepts)
  * **Perspective Phase:** Analyze concrete claims when queued by SCA
  * Create Claim nodes (cipher-based) + FacetPerspective nodes
  * Inherit all FacetAgent capabilities (Steps 1-5 methods)
  * Stay within facet domain (no cross-domain claim creation)

### **5.5.2 Two-Phase Workflow**

**Phase 1: Training Mode (Independent Domain Study)**

SFAs build subject ontologies for their disciplines **independently**, without cross-facet collaboration.

**Process:**
```
SCA:
  â†' Spawn all SFAs (Political, Military, Economic, etc.)
  â†' Route discipline training data to each SFA
  â†' Collect claims from all SFAs

SFAs (Independent Work):
  â†' Study discipline (Political Science, Military History, etc.)
  â†' Build domain ontology (abstract concepts)
  â†' Create Claim nodes + FacetPerspectives
  â†' Return claim ciphers to SCA

SCA (Accept All):
  â†' Receive training claims
  â†' Evaluate: Are these abstract domain concepts? (YES)
  â†' Decision: Accept as-is (NO QUEUE to other SFAs)
  â†' Integrate into graph
```

**Example Training Claims (NO CROSS-FACET REVIEW):**
```
Political SFA:
  â†' "Senate held legislative authority in Roman Republic"
  â†' Type: Abstract political concept
  â†' SCA evaluation: Abstract domain concept â†' Accept as-is (no queue)

Military SFA:
  â†' "Legion composed of cohorts and maniples"
  â†' Type: Abstract military structure
  â†' SCA evaluation: Abstract domain concept â†' Accept as-is (no queue)

Economic SFA:
  â†' "Roman economy based on agricultural production"
  â†' Type: Abstract economic principle
  â†' SCA evaluation: Abstract domain concept â†' Accept as-is (no queue)
```

**Rationale:** These are **disciplinary ontology claims**, not concrete historical events. Political, Military, and Economic SFAs do not need to review each other's abstract domain concepts.

---

**Phase 2: Operational Mode (Selective Multi-Facet Collaboration)**

SFAs encounter **concrete entities/events**. SCA evaluates each claim for multi-facet potential and **selectively queues** to relevant SFAs only.

**Process:**
```
SFA creates concrete claim:
  â†' Claim cipher: "claim_abc123..."
  â†' Claim text: "Caesar was appointed dictator in 49 BCE"
  â†' FacetPerspective: political
  â†' Returns cipher to SCA

SCA evaluates claim:
  1. Type: Concrete historical event (not abstract concept)
  2. Entities: Caesar (Q1048), Dictator office, 49 BCE
  3. Multi-domain potential: YES

SCA relevance scoring:
  â†' Military SFA: 0.9 (Caesar = commander) â†' QUEUE
  â†' Economic SFA: 0.8 (dictator = treasury control) â†' QUEUE
  â†' Cultural SFA: 0.3 (minor impact) â†' SKIP
  â†' Religious SFA: 0.2 (no dimension) â†' SKIP
  â†' Scientific SFA: 0.1 (irrelevant) â†' SKIP

SCA decision: Queue to Military + Economic ONLY

Military SFA (Perspective Mode):
  â†' Receives: claim_cipher="claim_abc123..."
  â†' Analyzes from military perspective
  â†' Creates FacetPerspective (military angle)
  â†' Returns: perspective_id="persp_002"

Economic SFA (Perspective Mode):
  â†' Receives: claim_cipher="claim_abc123..."
  â†' Analyzes from economic perspective
  â†' Creates FacetPerspective (economic angle)
  â†' Returns: perspective_id="persp_003"

Result:
  1 Claim (cipher="claim_abc123...")
  + 3 FacetPerspectives (political, military, economic)
  Consensus: AVG(0.95, 0.90, 0.88) = 0.91
```

### **5.5.3 Claim Architecture: Cipher + Star Pattern**

**Claims are star pattern subgraphs**, not isolated nodes.

**Claim Cipher (Content-Addressable ID):**
```python
claim_cipher = Hash(
    source_work_qid +           # Where claim came from
    passage_text_hash +          # Exact text
    subject_entity_qid +         # Who/what it's about
    relationship_type +          # What relationship
    temporal_data +              # When
    confidence_score +           # Initial confidence
    extractor_agent_id +         # Which SFA created it
    extraction_timestamp         # When created
)
# Result: "claim_abc123..." (unique cipher)
```

**Benefit:** Two SFAs discovering SAME claim â†' SAME cipher â†' Single Claim node (automatic deduplication)

**Star Pattern Structure:**
```
                    (Claim: cipher="claim_abc123...")
                              â"‚
         â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
         â"‚                        â"‚                        â"‚
    [PERSP_ON]              [PERSP_ON]              [PERSP_ON]
         â"‚                        â"‚                        â"‚
         â–¼                        â–¼                        â–¼
   (FacetPerspective:    (FacetPerspective:    (FacetPerspective:
    Political)            Military)             Economic)
```

**FacetPerspective Node (NEW NODE TYPE):**
```cypher
(:FacetPerspective {
  perspective_id: "persp_001",
  facet: "political",
  parent_claim_cipher: "claim_abc123...",
  facet_claim_text: "Caesar challenged Senate authority",
  confidence: 0.95,
  source_agent_id: "political_sfa_001",
  timestamp: "2026-02-15T10:00:00Z",
  reasoning: "Dictatorship violated Republican norms"
})-[:PERSPECTIVE_ON]->(Claim {cipher: "claim_abc123..."})
```

**Why FacetPerspective instead of separate claims?**
- âœ… **Single source of truth:** One Claim node (via cipher deduplication)
- âœ… **Multi-facet enrichment:** Multiple perspectives attached
- âœ… **Consensus calculation:** AVG(all perspective confidences)
- âœ… **Clear semantics:** Claim = base assertion, Perspective = facet interpretation

### **5.5.4 SCA Routing Criteria (5-Criteria Framework)**

**How SCA determines which claims warrant cross-facet review:**

**Criterion 1: Abstract vs Concrete Detection**
- **Abstract domain concepts** â†' NO QUEUE (accept as-is)
  * Theoretical frameworks ("Senate legislative authority")
  * Discipline-specific methods ("Manipular tactics")
  * General principles ("Agricultural economy base")
- **Concrete events/entities** â†' EVALUATE FOR QUEUE
  * Specific historical events ("Caesar crossed Rubicon")
  * Named individuals with roles ("Caesar appointed dictator")
  * Dated occurrences ("49 BCE")

**Criterion 2: Multi-Domain Relevance Scoring (0-1.0 scale)**
- **High Relevance (0.8-1.0)** â†' Queue to SFA
- **Medium Relevance (0.5-0.7)** â†' Queue to SFA
- **Low Relevance (0.0-0.4)** â†' Do NOT queue

**Example: "Caesar was appointed dictator in 49 BCE"**
```
Political SFA (creator): 1.0 (created the claim)
Military SFA: 0.9 (Caesar = commander, dictator = supreme command)
Economic SFA: 0.8 (dictator = treasury control, state finances)
Cultural SFA: 0.3 (minor cultural impact, not primary)
Religious SFA: 0.2 (no significant religious dimension)
Scientific SFA: 0.1 (irrelevant to scientific domain)

SCA Decision:
â†' Queue to: Military (0.9), Economic (0.8)
â†' Skip: Cultural (0.3), Religious (0.2), Scientific (0.1)
```

**Criterion 3: Entity Type Detection**
- Query Wikidata P31 (instance of)
- Map entity types to facet relevance:
  * Q5 (Human) â†' Political, Military, Cultural potential
  * Q198 (War) â†' Military, Political, Economic potential
  * Q216353 (Battle) â†' Military, Geographic potential

**Criterion 4: Conflict Detection**
- Date discrepancies â†' Queue for synthesis
- Attribute conflicts â†' Queue for synthesis
- Relationship disputes â†' Queue for synthesis

**Criterion 5: Existing Perspectives Check**
```cypher
MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim {cipher: $cipher})
RETURN COLLECT(p.facet) AS existing_facets
// Only queue to facets NOT in existing_facets
```

**Complete Routing Pseudocode:**
```python
def evaluate_claim_for_queue(claim: Claim, source_facet: str) -> Dict[str, float]:
    # Step 1: Check if abstract concept
    if is_abstract_concept(claim):
        return {}  # No queue
    
    # Step 2: Extract entities
    entities = extract_entities(claim.text)
    
    # Step 3: Score relevance to each facet
    relevance_scores = {}
    for facet in ALL_FACETS:
        if facet == source_facet:
            continue  # Skip source facet
        
        score = 0.0
        for entity in entities:
            entity_type = get_entity_type(entity.qid)
            score += calculate_relevance(entity_type, facet)
        
        relevance_scores[facet] = score / len(entities)
    
    # Step 4: Check existing perspectives
    existing_facets = get_existing_perspectives(claim.cipher)
    
    # Step 5: Filter by threshold
    queue_targets = {
        facet: score 
        for facet, score in relevance_scores.items()
        if score >= 0.5 and facet not in existing_facets
    }
    
    return queue_targets
```

### **5.5.5 Benefits & Implementation Status**

**Benefits:**
- âœ… **Efficient Collaboration:** Only concrete/multi-domain claims get cross-facet review
- âœ… **Independent Learning:** SFAs build domain ontologies without interference
- âœ… **Selective Enrichment:** Multi-facet analysis applied where it adds value
- âœ… **SCA Intelligence:** Orchestrator makes informed routing decisions
- âœ… **Automatic Deduplication:** Cipher ensures single Claim node per unique assertion
- âœ… **Consensus Calculation:** Multiple perspectives averaged for confidence

**Implementation Status (as of 2026-02-15):**
- âœ… Architecture documented (SCA_SFA_ROLES_DISCUSSION.md)
- âœ… Workflow models compared (CLAIM_WORKFLOW_MODELS.md)
- âœ… Routing criteria specified (5 criteria with examples)
- âœ… FacetPerspective pattern defined
- âœ… Cipher-based deduplication documented
- â³ FacetPerspective node schema (add to NODE_TYPE_SCHEMAS.md)
- â³ SCA claim evaluation implementation
- â³ SCA relevance scoring implementation
- â³ FacetPerspective creation in SFA
- â³ Selective queue logic in SCA

**References:**
- Complete specification: `SCA_SFA_ROLES_DISCUSSION.md`
- Workflow comparison: `CLAIM_WORKFLOW_MODELS.md`
- Military SFA methodology: `Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md`

---

## **5.6 Coordinator Agents**

**Coordinator Agents** orchestrate multi-agent workflows, consensus building, and claim promotion.

### **Example**

```
claims_coordinator
    agent_type: "coordinator"
```

### **Responsibilities**

- Identify claims needing review
- Route claims to appropriate subject/entity agents
- Route claims to facet-specialist agents (Section 3.2.6, facet assessment workflow; Section 5.5, SCA â†" SFA coordination)
- Compute `consensus_score` from multiple reviews
- Update `claim.status` based on validation results
- Trigger claim promotion to canonical graph (Section 6.9)
- Synthesize conflicting claims (Section 6.7)

### **Facet-Based Agent Assignment** ðŸŸ¡ **NEW**

**Agent Specialization by Facet Category:**

Each agent specializes in ONE facet category and evaluates claims from that dimensional perspective.

```cypher
// Agent specialization assignment
CREATE (agent:Agent {
  agent_id: "AGENT_POLITICAL_V1",
  label: "Political Historian Agent",
  agent_type: "facet_specialist",
  specialization_facet: "PoliticalFacet",
  description: "Evaluates claims from political/governance dimension"
})

// Link agent to facet category it owns
MERGE (agent)-[:OWNS_CATEGORY]->(:FacetCategory {key: "POLITICAL"})
```

**Agent Roster (16 Facet-Specialists):**

| Agent ID | Specialization | Facet Category | Scope |
|----------|---|---|---|
| AGENT_POLITICAL_V1 | Political | States, empires, governance | Evaluates political implications |
| AGENT_MILITARY_V1 | Military | Warfare, tactics, strategy | Evaluates military accuracy |
| AGENT_ECONOMIC_V1 | Economic | Trade, production, finance | Evaluates economic context |
| AGENT_CULTURAL_V1 | Cultural | Art, customs, identity | Evaluates cultural dimensions |
| AGENT_RELIGIOUS_V1 | Religious | Beliefs, practices, institutions | Evaluates religious aspects |
| AGENT_INTELLECTUAL_V1 | Intellectual | Philosophy, thought | Evaluates intellectual context |
| AGENT_SCIENTIFIC_V1 | Scientific | Scientific paradigms | Evaluates scientific validity |
| AGENT_ARTISTIC_V1 | Artistic | Art, architecture, aesthetics | Evaluates artistic authenticity |
| AGENT_SOCIAL_V1 | Social | Social structures, class | Evaluates social implications |
| AGENT_DEMOGRAPHIC_V1 | Demographic | Population, migration | Evaluates demographic accuracy |
| AGENT_ENVIRONMENTAL_V1 | Environmental | Climate, ecology | Evaluates environmental context |
| AGENT_TECHNOLOGICAL_V1 | Technological | Tools, innovations, technology | Evaluates technical accuracy |
| AGENT_LINGUISTIC_V1 | Linguistic | Languages, scripts | Evaluates linguistic aspects |
| AGENT_ARCHAEOLOGICAL_V1 | Archaeological | Material culture, stratigraphy | Evaluates archaeological validity |
| AGENT_DIPLOMATIC_V1 | Diplomatic | Treaties, alliances, diplomacy | Evaluates diplomatic accuracy |
| AGENT_GEOGRAPHIC_V1 | Geographic | Spatial regions, territories | Evaluates geographic accuracy |

**Coordinator Routing to Facet-Specialists:**

When a claim arrives for evaluation:

1. **Action:** Coordinator creates AnalysisRun node (Section 3.2.4)
2. **Action:** Coordinator queues claim for all 16 facet-specialist agents
3. **Each Facet-Specialist:** Creates independent FacetAssessment (Section 3.2.5)
4. **Result:** Star pattern with 16 dimensional assessments (Section 9.6)

```cypher
// Coordinator routing logic
MATCH (agent:Agent)-[:OWNS_CATEGORY]->(cat:FacetCategory)
MATCH (cat)<-[:IN_FACET_CATEGORY]-(f:Facet)
// Queue (agent, claim) pair for evaluation
CREATE (task:EvaluationTask {
  agent_id: agent.agent_id,
  claim_id: claim.claim_id,
  facet_type: f.label,
  status: "queued"
})
```

### **Cypher Example**

```cypher
CREATE (agent:Agent {
  agent_id: "claims_coordinator",
  label: "Claims Coordination Agent",
  agent_type: "coordinator",
  description: "Orchestrates multi-agent claim review, facet assessment, and promotion"
})
```

---

## **5.6 Agent Routing Logic**

**Agent routing** determines which agent handles which task based on subject classification, entity type, and claim content.

### **Routing Inputs**

1. **Subject classification:** LCC class, FAST topics from SubjectConcepts
2. **Entity type:** Human, Event, Place, etc.
3. **Claim type:** entity_existence, relationship_assertion, property_assertion
4. **Temporal scope:** Period coverage
5. **Geographic scope:** Place coverage

### **Routing Algorithm**

```
1. Extract SubjectConcepts from claim content
2. Identify primary LCC class
3. Route to FAST-level agent (Level 1)
4. Within FAST agent, identify LCC subdivision
5. Route to LCC specialist (Level 2) if available
6. If no specialist, use generalist FAST agent
```

### **Cypher Routing Query**

```cypher
// Find agents for claim about "Caesar crosses Rubicon"
MATCH (claim:Claim {claim_id: "claim_00123"})
      -[:SUBJECT_OF]->(:SubjectConcept)
      <-[:OWNS_DOMAIN]-(agent:Agent)
WHERE agent.agent_type = "subject"
RETURN agent.agent_id, agent.label, COUNT(*) AS domain_overlap
ORDER BY domain_overlap DESC
LIMIT 3
```

---

## **5.7 SFA Ontology Building Methodology**

**Context:** SubjectFacetAgents (SFAs) build domain-specific ontologies during **Training Phase** (Section 5.5.2). This requires filtering federated authority noise to extract clean disciplinary structures.

**Problem:** Wikidata "what links here" queries return massive platform noise (Wikimedia categories, templates, Commons files) overwhelming domain content.

**Solution:** Disciplinary filtering methodology using scholarly roots, property whitelists, and platform blacklists.

### **5.7.1 Military SFA Methodology (Example)**

**Reference:** `Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md` (complete specification with SPARQL queries, validation checklist, expected ontology structure)

**Anchor:** Start from `Q192386` (military science) as scholarly discipline root, not vague "military" label.

**Property Whitelist (PREFER):**
| Property | Code | Purpose | Priority |
|----------|------|---------|----------|
| subclass of | P279 | Taxonomic backbone | HIGH |
| instance of | P31 | Type classification | HIGH |
| part of | P361 | Compositional structure | HIGH |
| has part | P527 | Compositional structure | HIGH |
| conflict | P607 | Military conflicts | HIGH |
| military branch | P241 | Branch of service | HIGH |
| military rank | P410 | Rank classification | HIGH |
| military unit | P7779 | Unit types | HIGH |

**Wikimedia Blacklist (EXCLUDE):**
| QID | Type | Rationale |
|-----|------|-----------|
| Q4167836 | Wikimedia category | Platform navigation |
| Q11266439 | Wikimedia template | Platform scaffolding |
| Q17633526 | Wikinews article | News content |
| Q15184295 | Wikimedia module | Technical infrastructure |
| Q4663903 | Wikimedia portal | Portal organization |

**Inclusion Criteria (items must satisfy MOST of):**
- Has `P279` or `P31` linking to military domain class
- Has `P425` (field of occupation) = military science
- Appears in military science scholarly treatments
- Has meaningful `P361`/`P527`/`P607`/`P241`/`P410` relations
- Fits naturally as a class in hierarchy
- Needed to explain military processes or institutions

**Exclusion Criteria (items must fail ALL of):**
- `P31` is Wikimedia infrastructure class
- Only connects via category/Commons/site links
- Orphaned (no core military properties)
- Over-generic buzzword without military specificity
- Pure media container (image, category)
- Anachronistic (for Roman Republic specialization)

**Roman Republic Refinement:**
- Intersect generic military ontology with Q17167 (Roman Republic)
- Use P1001 (applies to jurisdiction), P361 (part of)
- Temporal overlap: 509 BCE - 27 BCE
- Exclude anachronisms (air force, cyberwarfare, modern operational concepts)

**Expected Results:**
- Generic military ontology: ~500-1,000 concepts (~2,000-5,000 edges after filtering)
- Roman Republican specialization: ~100-200 concepts (~500-1,000 edges after filtering)
- Noise reduction: 80-90% (typical Wikidata query returns 10,000+ items, filtered to ~500-1,000)

**Example Training Claims (Military SFA, NO CROSS-FACET REVIEW):**
```
Claim 1: "Legion was primary Roman military unit"
  â†' Type: Discovery Mode (abstract domain concept)
  â†' Source: Wikidata Q170944 + scholarly sources
  â†' Confidence: 0.95
  â†' Facet: Military
  â†' SCA Action: Accept as-is (NO QUEUE)

Claim 2: "Cohort composed of multiple maniples"
  â†' Type: Discovery Mode (abstract structural relationship)
  â†' Source: Wikidata Q82955, Q1541817
  â†' Confidence: 0.90
  â†' Facet: Military
  â†' SCA Action: Accept as-is (NO QUEUE)

Claim 3: "Centurion commanded century of soldiers"
  â†' Type: Discovery Mode (abstract organizational principle)
  â†' Source: Wikidata Q2747456
  â†' Confidence: 0.95
  â†' Facet: Military
  â†' SCA Action: Accept as-is (NO QUEUE)
```

**Rationale:** These are **disciplinary ontology claims**, not concrete historical events. They do not warrant cross-facet review by Political, Economic, or Cultural SFAs during training phase.

### **5.7.2 Generalized Methodology (All SFAs)**

**Step 1: Identify Disciplinary Root**
- Find Wikidata QID for discipline (e.g., Q192386 for military science, Q36442 for political science)
- Verify `P31` = field of study (Q11862829) or academic discipline (Q11862829)
- Use as scholarly anchor, not arbitrary category

**Step 2: Property Whitelist**
- Select semantic properties (P279, P31, P361, P527, domain-specific properties)
- Exclude platform properties (P373 Commons category, P910 topic's main category, P1151 main portal)

**Step 3: Wikimedia Blacklist**
- Exclude all `P31` â†' Wikimedia infrastructure classes (Q4167836, Q11266439, etc.)
- Filter out pure media containers (images, galleries, categories)

**Step 4: Polity/Period Refinement**
- Intersect generic ontology with historical context (e.g., Q17167 Roman Republic)
- Use P1001 (jurisdiction), P361 (part of), P580/P582 (temporal bounds)
- Exclude anachronisms for historical specializations

**Step 5: Training Claim Generation**
- Create Discovery Mode claims about abstract concepts
- All claims tagged with facet
- SCA accepts all training claims as-is (no queue to other SFAs)

**Expected Noise Reduction:** 70-90% depending on domain complexity and Wikidata coverage

**Benefits:**
- âœ… Clean disciplinary ontologies (not platform artifacts)
- âœ… Scholarly grounding (from recognized academic disciplines)
- âœ… Efficient training (SFAs don't review irrelevant abstract concepts from other facets)
- âœ… Scalable methodology (applicable to all 17 facet domains)

---

## **5.8 Agent Memory (AgentMemory Node)**

Agents maintain **explicit memory** of previous decisions, patterns, and cached knowledge.

### **AgentMemory Node Schema**

**Node Label:** `:AgentMemory`

**Required Properties:**
| Property | Type | Example |
|----------|------|---------|
| `memory_id` | string | `"mem_000456"` |
| `agent_id` | string | `"roman_republic_agent"` |
| `memory_type` | string | `"decision"`, `"pattern"`, `"cached_knowledge"` |
| `content` | string | Serialized memory content |
| `created_at` | ISO 8601 string | `"2026-02-12T11:00:00Z"` |

**Required Edges:**
- `MEMORY_OF` â†’ Agent

### **Memory Types**

1. **Decision Memory:** Previous review decisions and rationale
2. **Pattern Memory:** Recognized patterns (e.g., "Caesar always spelled with 'ae'")
3. **Cached Knowledge:** Pre-computed facts (e.g., "Roman Republic = 510-27 BCE")

### **Cypher Example**

```cypher
CREATE (mem:AgentMemory {
  memory_id: "mem_000456",
  agent_id: "roman_republic_agent",
  memory_type: "pattern",
  content: "Caesar name variants: Gaius Julius Caesar, C. Julius Caesar, Julius Caesar",
  created_at: "2026-02-12T11:00:00Z"
})

MATCH (agent:Agent {agent_id: "roman_republic_agent"})
CREATE (mem)-[:MEMORY_OF]->(agent)
```

---

## **5.8 Agent Lifecycle & Caching**

**Agent versioning** and **cache management** ensure consistent behavior and efficient operation.

### **Agent Versioning Strategy**

**Version Identifier Format:**
```
{agent_type}_{qid}_{lcc_class}_{version}_{timestamp}
```

**Example:**
```
genericagent_Q1048_DG83_v1.2_20260212T100000Z
```

**Components:**
- `agent_type`: `genericagent`, `subjectagent`, `entityagent`, `coordinator`
- `qid`: Wikidata QID of primary domain concept
- `lcc_class`: Primary LCC classification
- `version`: Semantic version (v1.2)
- `timestamp`: Creation timestamp

### **Cache Versioning**

**Problem:** Agent knowledge evolves; old cached results may be stale.

**Solution:** Cache entries tagged with agent version:

```cypher
AgentMemory {
  agent_version: "v1.2",
  cache_expiry: "2026-03-12T00:00:00Z"
}
```

**Cache Invalidation Rules:**
1. Agent version increments â†’ invalidate all caches
2. Expiry timestamp reached â†’ refresh cache
3. Upstream SubjectConcept updated â†’ invalidate related caches

**Source:** Old conversation analysis (cache versioning for vertex jump concept)

---

## **5.9 Cypher Examples**

### **Create Subject Agent with Domain**

```cypher
CREATE (agent:Agent {
  agent_id: "roman_republic_agent",
  label: "Roman Republic Specialist",
  agent_type: "subject",
  confidence_calibration: 0.93,
  specialization_level: "high",
  version: "v1.0",
  created_at: "2026-02-12T10:00:00Z"
})

MATCH (sc:SubjectConcept {lcc_class: "DG83"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc)
```

### **Route Claim to Agents**

```cypher
// Find agents for a claim
MATCH (claim:Claim {claim_id: "claim_00123"})
      -[:ABOUT_SUBJECT]->(:SubjectConcept)
      <-[:OWNS_DOMAIN]-(agent:Agent)
WHERE agent.agent_type = "subject"
  AND agent.specialization_level IN ["high", "medium"]
RETURN agent.agent_id, agent.label
LIMIT 5
```

### **Agent Review History**

```cypher
// Get agent's review history
MATCH (agent:Agent {agent_id: "roman_republic_agent"})
      -[:REVIEWED]->(review:Review)
      -[:REVIEW_OF]->(claim:Claim)
RETURN claim.claim_id, review.decision, review.confidence
ORDER BY review.review_timestamp DESC
LIMIT 20
```

### **Create Agent Memory**

```cypher
CREATE (mem:AgentMemory {
  memory_id: "mem_000789",
  agent_id: "roman_republic_agent",
  memory_type: "cached_knowledge",
  content: "Roman Republic period boundaries: start=-510, end=-27, uncertainty=Â±5 years",
  agent_version: "v1.0",
  cache_expiry: "2026-03-12T00:00:00Z",
  created_at: "2026-02-12T12:00:00Z"
})

MATCH (agent:Agent {agent_id: "roman_republic_agent"})
CREATE (mem)-[:MEMORY_OF]->(agent)
```

---

### **Link Work to SubjectConcept (Aboutness)**

# **6. Claims Layer**

## **6.0 Claims Layer Overview**

The **Claims Layer** provides evidence-aware assertion management with transparent provenance, multi-agent validation, and cryptographic verification. Claims are not simple edgesâ€”they are **complex subgraphs** representing complete evidence chains.

**Core Concept:** Every assertion in Chrystallum has explicit provenance from source material through agent extraction to validated canonical graph representation.

---

## **6.1 Claims Architecture Components**

The Claims Layer manages the complete lifecycle of evidence-based assertions, from initial extraction through multi-agent validation to canonical graph promotion.

### **Core Node Types:**

**1. Claim** - Structured assertion with provenance
- Represents an agent's assertion about the world
- Includes confidence, provenance, and verification metadata
- Identified by content-addressable cipher (Section 6.4)

**2. Review** - Multi-agent validation decision
- Single agent's evaluation of a claim
- Includes confidence, verdict, fallacy detection
- Feeds into consensus calculation

**3. ProposedEdge** - Relationship awaiting validation
- Represents edges not yet promoted to canonical graph
- Converted to actual relationships upon validation
- Maintains proposed structure separate from verified graph

**4. ReasoningTrace** - Derivation provenance
- How an agent reached a conclusion
- Reasoning steps, sources consulted, confidence chain
- Enables explainability and audit trails

**5. Synthesis** - Multi-agent consensus resolution
- Resolves conflicting claims from multiple agents
- Records consensus method and participating agents
- Produces consolidated output claim

**6. RetrievalContext** - Evidence retrieval record
- Documents and passages retrieved from private vector stores
- Links retrieval actions to reasoning traces
- Maintains query-response provenance

### **Provenance Chain:**
```
Work (Source Entity - Section 3) 
  â†’ Agent (Extraction)
    â†’ Claim (Assertion + Cipher)
      â†’ ReasoningTrace (How derived)
      â†’ RetrievalContext (Evidence used)
      â†’ Review (Validation by peers)
        â†’ Synthesis (Consensus building)
          â†’ Status Update (proposed â†’ validated)
            â†’ Promotion (to canonical graph)
```

### **System Architecture Context**

**Two Separate Systems:**
| System | Storage | Shared? | Purpose |
|--------|---------|---------|---------|
| **Neo4j Graph** | Nodes & edges | âœ… YES | Structural knowledge, claims, provenance |
| **Vector Stores** | Text embeddings | âŒ NO | Semantic retrieval per agent (private) |

**Key Principle:** Claims, Reviews, Reasoning Traces, and Agent Memory live in the **shared graph**. Text embeddings and document chunks live in **private per-agent vector stores**.

---

## **6.2 Claim Node Schema**

**Node Label:** `:Claim`

**Purpose:** Represents an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges). Claims support multi-agent review, provenance, and gradual promotion of "proposed" structure into validated KG facts.

### **Required Properties**

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `claim_id` | string | text | `"claim_000123"` | Unique ID |
| `cipher` | string | hash | `"claim_b22020c0e271b7d8..."` | **Content-addressable identifier** (Section 6.4) |
| `text` | string | text | `"Caesar crossed the Rubicon on January 10, 49 BCE."` | Human-readable claim text |
| `claim_type` | string | enum | `"factual"` | `"factual"`, `"interpretive"`, `"causal"`, `"temporal"`, `"entity_existence"`, `"relationship_assertion"`, `"property_assertion"` |
| `source_agent` | string | text | `"roman_republic_agent_001"` | Agent that originated the claim |
| `timestamp` | string | ISO 8601 | `"2026-02-12T15:30:00Z"` | When the claim was created |
| `status` | string | enum | `"proposed"` | `"proposed"`, `"validated"`, `"disputed"`, `"rejected"` |
| `confidence` | float | [0,1] | `0.85` | Agent's internal confidence at creation |

### **Provenance Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `source_work_qid` | string | `"Q644312"` | Wikidata ID of source work |
| `passage_text` | string | `"Caesar...Rubicon...49 BCE"` | Actual text supporting claim |
| `passage_hash` | string | `"p_a1b2c3d4..."` | Hash of passage for verification |
| `extractor_agent_id` | string | `"genericagent_Q767253_D_v2.0"` | Agent that extracted claim |
| `extraction_timestamp` | string | `"2026-02-12T10:30:00Z"` | When extracted |
| `provenance` | string[] | `["Plutarch, Caesar 32", "Suetonius, Julius 31"]` | Source citations |

### **Content Properties (varies by claim_type)**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `subject_entity_qid` | string | `"Q1048"` | Primary entity claim is about |
| `object_entity_qid` | string | `"Q644312"` | Secondary entity (for relationships) |
| `relationship_type` | string | `"CAUSED"` | Type of relationship asserted (Section 7) |
| `property_name` | string | `"death_date"` | Property being asserted |
| `property_value` | any | `"-0044-03-15"` | Value of property |
| `temporal_data` | string | `"-0049-01-10"` | Temporal information |
| `action_structure` | JSON | `{"goal": "POL", "trigger": "OPPORT"}` | Goal-trigger-action-result (Section 7.6) |

### **Consensus & Review Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `review_count` | int | `3` | Number of reviews received |
| `consensus_score` | float | `0.78` | Aggregated review confidence |
| `claim_scope` | string | `"Battle of Actium casualties"` | Short label for domain |
| `reasoning_trace_id` | string | `"trace_000987"` | ID of associated ReasoningTrace |
| `proposed_nodes` | string[] | `["event_123", "place_456"]` | IDs of nodes this claim proposes |
| `proposed_edges` | string[] | `["pedge_001", "pedge_002"]` | IDs of ProposedEdge nodes |

### **Verification Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `state_root` | string | `"merkle_root_abc123..."` | Merkle tree root for cryptographic verification |
| `lamport_clock` | integer | `12345` | Logical timestamp for distributed ordering |

### **Required Edges**

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `MADE_CLAIM` | Agent | 1 | `(agent)-[:MADE_CLAIM]->(claim)` |
| `SUBJECT_OF` | Entity/SubjectConcept | 1+ | `(entity OR concept)-[:SUBJECT_OF]->(claim)` |

### **Optional Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `PROPOSES` | Entity | Claim proposes existence/interpretation of a node |
| `PROPOSES` | ProposedEdge | Claim proposes a new relationship |
| `HAS_TRACE` | ReasoningTrace | `(claim)-[:HAS_TRACE]->(trace)` |
| `SUPERSEDES` | Claim | Links newer version to older version |

---

## **6.3 Review Node Schema**

**Node Label:** `:Review`

**Purpose:** Represents a single agent's evaluation of a Claim, including confidence, detected fallacies, and a reasoning summary. Reviews feed into consensus and claim status updates.

### **Required Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `review_id` | string | `"review_000456"` | Unique ID |
| `agent_id` | string | `"naval_warfare_agent"` | Reviewing agent |
| `claim_id` | string | `"claim_000123"` | Reviewed claim |
| `timestamp` | string | `"2026-02-12T16:00:00Z"` | When review was made |
| `confidence` | float | `0.72` | Reviewer's confidence |
| `verdict` | string | `"support"` | `"support"`, `"challenge"`, `"uncertain"` |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `fallacies_detected` | string[] | `["anachronism", "post_hoc"]` | Fischer-style historical fallacies |
| `reasoning_summary` | string | `"Plutarch exaggerates casualties; Dio provides more conservative estimate"` | Short text summary |
| `evidence_refs` | string[] | `["Goldsworthy p.145", "Dio 50.35"]` | Evidence used in review |
| `bayesian_posterior` | float | `0.68` | Output of Bayesian reasoning engine |
| `weight` | float | `1.0` | Reviewer weight (expertise-based) |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `REVIEWED` | Agent | `(agent)-[:REVIEWED]->(review)` |
| `REVIEWS` | Claim | `(review)-[:REVIEWS]->(claim)` |

### **Example Cypher**

```cypher
// Create review
CREATE (review:Review {
  review_id: "review_000456",
  agent_id: "naval_warfare_agent",
  claim_id: "claim_000123",
  timestamp: "2026-02-12T16:00:00Z",
  confidence: 0.72,
  verdict: "support",
  reasoning_summary: "Dio's account provides corroborating evidence"
})

// Link to agent and claim
MATCH (agent:Agent {agent_id: "naval_warfare_agent"}),
      (claim:Claim {claim_id: "claim_000123"})
CREATE (agent)-[:REVIEWED]->(review)-[:REVIEWS]->(claim)
```

---

## **6.4 Content-Addressable Claim Identification** ðŸ”¥ NEW

### **Claim Cipher Generation**

**Core Innovation:** Claims are uniquely identified by a **cipher** generated from their complete structure:

```python
claim_cipher = Hash(
    source_work_qid +           # Q644312 (Plutarch, Life of Caesar)
    passage_text_hash +          # Hash("Caesar...Rubicon...49 BCE")
    subject_entity_qid +         # Q1048 (Julius Caesar)
    object_entity_qid +          # Q644312 (Crossing of Rubicon event QID)
    relationship_type +          # "CAUSED"
    action_structure +           # {goal: "POL", trigger: "OPPORT", ...}
    temporal_data +              # {start_date: "-0049-01-10"}
    confidence_score +           # 0.95
    extractor_agent_id +         # "genericagent_Q767253_D_v2.0_1760104502"
    extraction_timestamp         # "2026-02-12T10:30:00Z"
)

# Result: "claim_kc1-b22020c0e271b7d8e4a5f6c9d1b2a3e4" (unique cipher)
```

### **Why Content-Addressable Claims?**

#### **1. Automatic Deduplication** âœ…

```python
# Agent A extracts claim from Plutarch at 10:00 AM
claim_data_A = {
    "source": "Q644312",
    "passage": "Caesar crossed the Rubicon...",
    "subject": "Q1048",
    "relationship": "CAUSED",
    "timestamp": "2026-02-12T10:00:00Z"
}
cipher_A = Hash(claim_data_A)  # â†’ "claim_abc123..."

# Agent B extracts SAME claim from Plutarch at 2:00 PM
claim_data_B = {
    "source": "Q644312",
    "passage": "Caesar crossed the Rubicon...",
    "subject": "Q1048", 
    "relationship": "CAUSED",
    "timestamp": "2026-02-12T14:00:00Z"  # Different time!
}
cipher_B = Hash(claim_data_B)  # â†’ "claim_abc123..." (SAME!)

# Graph check prevents duplicate
if exists_in_graph(cipher_B):
    # Don't create duplicate - add Agent B's review to existing claim
    add_supporting_review(cipher_B, agent_B, timestamp_B)
    increment_confidence(cipher_B)
else:
    # New claim - create subgraph
    create_claim_subgraph(cipher_B, claim_data_B)
```

**Benefits:**
- Multiple agents validating same claim â†’ higher confidence, not duplicates
- Automatic consensus detection
- No manual deduplication needed

---

#### **2. Cryptographic Verification** âœ…

```python
# University A creates claim
claim = create_claim(claim_data)
cipher = claim.cipher  # Content-addressable ID
state_root = MerkleRoot([cipher, related_entities, sources])

# Publish with verification receipt
publish({
    "cipher": cipher,
    "state_root": state_root, 
    "timestamp": "2026-02-12T10:30:00Z",
    "institution": "University A"
})

# University B downloads and verifies
downloaded_claim = fetch_claim(cipher)
recomputed_cipher = Hash(downloaded_claim.data)

if recomputed_cipher == cipher:
    # âœ… Claim data matches cipher - integrity verified
    # Can cite with cryptographic proof
    cite_with_proof(cipher, state_root)
else:
    # âŒ Data corrupted or tampered
    reject_claim("Integrity verification failed")
```

**Benefits:**
- Academic claims verifiable with cryptographic proof
- No trust needed - math verifies integrity
- Enables distributed academic knowledge networks

---

#### **3. Claim as Subgraph Cluster** âœ…

**A claim isn't a single nodeâ€”it's a complete evidence structure:**

```cypher
// The cipher identifies the entire subgraph cluster
(claim:Claim {
  cipher: "claim_abc123...",
  claim_id: "claim_00123"  // Also keep internal ID for convenience
})

// Subgraph components attached to cipher
(source:Work {qid: "Q644312"})-[:EXTRACTED_FROM]->(claim)
(passage:Passage {text: "Caesar..."})-[:CITED_BY]->(claim)
(caesar:Human {qid: "Q1048"})-[:SUBJECT_OF]->(claim)
(event:Event {qid: "Q644312"})-[:OBJECT_OF]->(claim)
(rel:CAUSED)-[:ASSERTED_BY]->(claim)
(agent:Agent {agent_id: "genericagent..."})-[:EXTRACTED_BY]->(claim)
```

**The cipher is the cluster key** - all components reference it.

---

#### **4. Framework/Review Attachment via Cipher** âœ…

```cypher
// Frameworks analyze claim via cipher reference
(framework:Framework {name: "W5H1"})
  -[:ANALYZES]->
  (claim:Claim {cipher: "claim_abc123"})

// Reviews validate claim via cipher reference  
(review:Review {
  status: "verified",
  reviewer: "Dr. Smith",
  timestamp: "2026-02-12T11:00:00Z"
})
  -[:VALIDATES]->
  (claim:Claim {cipher: "claim_abc123"})

// Beliefs derive from claim via cipher reference
(belief:Belief {
  confidence: 0.95,
  reasoning: "Two independent sources confirm"
})
  -[:DERIVED_FROM]->
  (claim:Claim {cipher: "claim_abc123"})

// Query: "Find all frameworks analyzing this claim"
MATCH (f:Framework)-[:ANALYZES]->(c:Claim {cipher: $cipher})
RETURN f

// No ambiguity - cipher uniquely identifies claim subgraph
```

**Benefits:**
- Unambiguous attachment point (cipher = unique identifier)
- Works across distributed systems (same cipher everywhere)
- Can query all validations for specific evidence cluster

---

#### **5. Claim Versioning Built-In** âœ…

```cypher
// Original claim extracted with confidence 0.85
(claim_v1:Claim {
  cipher: "claim_abc123...",  // Computed with confidence=0.85
  confidence: 0.85,
  status: "under_review",
  timestamp: "2026-02-12T10:00:00Z"
})

// New evidence raises confidence to 0.95
// Different confidence â†’ different cipher!
(claim_v2:Claim {
  cipher: "claim_xyz789...",  // Different cipher
  confidence: 0.95,
  status: "verified", 
  timestamp: "2026-02-12T14:00:00Z"
})

// Link versions explicitly
(claim_v2)-[:SUPERSEDES]->(claim_v1)
(claim_v2)-[:EVIDENCE_ADDED]->(:Review {
  new_source: "Suetonius",
  reason: "Additional corroboration"
})

// Query claim evolution
MATCH path = (c_new:Claim)-[:SUPERSEDES*]->(c_old:Claim)
WHERE c_new.cipher = "claim_xyz789..."
RETURN path
```

**Benefits:**
- Claim evolution tracked automatically
- Can query historical confidence levels
- Audit trail for scholarly disputes
- Immutable history (old claim preserved with original cipher)

---

### **6.4.1 Facet Claim Node Schema**

**Neo4j Implementation (Facet-Level Claim):**

```cypher
// Create facet claim with stable cipher
CREATE (claim:FacetClaim {
  // Content-addressable ID (primary, stable across provenance changes)
  cipher: "fclaim_pol_b22020c0e271b7d8",
  
  // Internal ID (convenience)
  claim_id: "claim_00123",
  
  // CIPHER COMPONENTS (stable, logical content)
  subject_node_id: "Q1048",           // Caesar
  property_path_id: "CHALLENGED_AUTHORITY_OF",
  object_node_id: "Q1747689",         // Roman Senate
  facet_id: "political",              // Essential!
  temporal_scope: "-0049-01-10",
  source_document_id: "Q644312",       // Plutarch
  passage_locator: "Caesar.32",
  
  // PROVENANCE METADATA (separate from cipher, can change)
  confidence: 0.85,                    // Can update without changing cipher
  extracting_agents: [                 // Multiple agents = evidence accumulation
    "political_sfa_001",
    "military_sfa_001"                // Added later via deduplication
  ],
  extraction_timestamps: [
    "2026-02-12T10:00:00Z",
    "2026-02-12T14:00:00Z"
  ],
  created_by_agent: "political_sfa_001",  // Original extractor
  last_updated: "2026-02-12T14:00:00Z",
  
  // DERIVED PROPERTIES
  assertion_text: "Caesar challenged Senate authority by crossing Rubicon",
  cidoc_crm_property: "P17_was_motivated_by",
  
  // STATUS & VALIDATION (lifecycle, not identity)
  status: "validated",
  review_count: 2,
  consensus_score: 0.91,
  validation_timestamp: "2026-02-12T15:00:00Z",
  
  // CRYPTOGRAPHIC VERIFICATION (optional)
  state_root: "merkle_xyz789...",     // Merkle root of assertion graph
  lamport_clock: 1234567
})

// Indexes
CREATE INDEX facet_claim_cipher_idx FOR (c:FacetClaim) ON (c.cipher);
CREATE INDEX facet_claim_facet_idx FOR (c:FacetClaim) ON (c.facet_id);
```

---

### **6.4.2 Deduplication Query Pattern**

```cypher
// Before creating new claim, check if cipher exists
MATCH (existing:Claim {cipher: $computed_cipher})
RETURN existing

// If found: Add supporting review instead of duplicate
MERGE (existing:Claim {cipher: $computed_cipher})
ON MATCH SET 
  existing.review_count = existing.review_count + 1,
  existing.confidence = existing.confidence + ($new_confidence_boost)
CREATE (review:Review {
  reviewer_agent: $agent_id,
  timestamp: $timestamp,
  status: "confirmed"
})-[:VALIDATES]->(existing)

// If not found: Create new claim subgraph
ON CREATE SET
  existing.claim_id = $internal_id,
  existing.source_work_qid = $source_qid,
  existing.confidence = $initial_confidence,
  existing.status = "proposed",
  existing.review_count = 1
```

---

### **6.4.3 Verification Query Pattern**

```cypher
// Verify claim integrity by recomputing cipher from stable components ONLY
MATCH (c:FacetClaim {cipher: $claimed_cipher})
WITH c, 
  Hash(
    c.subject_node_id + 
    c.property_path_id + 
    c.object_node_id +
    c.facet_id +
    c.temporal_scope +
    c.source_document_id +
    c.passage_locator
    // NOTE: NO confidence, NO agent, NO timestamp!
  ) AS recomputed_cipher
RETURN 
  c.cipher = recomputed_cipher AS integrity_verified,
  c.cipher AS original_cipher,
  recomputed_cipher AS computed_cipher,
  CASE 
    WHEN c.cipher = recomputed_cipher THEN "✅ Claim identity verified"
    ELSE "❌ Cipher mismatch - possible tampering"
  END AS verification_status
```

**Check for Deduplication Candidates:**
```cypher
// Find potential duplicate claims (same content, different provenance)
MATCH (c1:FacetClaim), (c2:FacetClaim)
WHERE c1.subject_node_id = c2.subject_node_id
  AND c1.property_path_id = c2.property_path_id
  AND c1.object_node_id = c2.object_node_id
  AND c1.facet_id = c2.facet_id
  AND c1.cipher <> c2.cipher  // Different ciphers despite same core content
RETURN c1.cipher, c2.cipher, 
       "Potential deduplication issue" AS status,
       c1.extracting_agents AS agents1,
       c2.extracting_agents AS agents2
```

---

### **6.4.4 Framework Attachment Query Pattern**

```cypher
// Attach W5H1 framework analysis to claim
MATCH (claim:Claim {cipher: $cipher})
CREATE (framework:Framework {
  name: "W5H1",
  analysis: {
    who: "Julius Caesar",
    what: "Crossing of Rubicon", 
    when: "-0049-01-10",
    where: "Rubicon River",
    why: "Political opportunity",
    how: "Military action"
  }
})-[:ANALYZES]->(claim)

// Query all frameworks analyzing specific claim
MATCH (f:Framework)-[:ANALYZES]->(c:Claim {cipher: $cipher})
RETURN f.name, f.analysis

// Query all claims analyzed by specific framework
MATCH (f:Framework {name: "W5H1"})-[:ANALYZES]->(c:Claim)
RETURN c.cipher, c.claim_id, c.confidence
```

---

## **6.5 Hybrid Architecture: Entities vs. Claims**

### **Different Layers, Different Patterns:**

| Aspect | Entity Layer | Claims Layer |
|--------|--------------|--------------|
| **Identification** | Multiple authorities (qid, viaf_id, etc.) | Content-addressable cipher |
| **Query Pattern** | Traversal, exploration, discovery | Direct cipher lookup, verification |
| **Purpose** | Represent real-world entities | Represent evidence assertions |
| **Mutability** | Properties can change | Immutable (change = new cipher) |
| **Deduplication** | Via authority matching | Automatic via cipher collision |
| **Verification** | Authority ID validation | Cryptographic hash verification |

### **Why Hybrid Approach?**

**Entities need flexibility:**
- Relationship discovery: "What connects Caesar to Cleopatra?"
- Pattern matching: "Find all senators who opposed Caesar"
- Graph algorithms: PageRank, centrality, community detection
- **Traversal is the answer**

**Claims need verification:**
- Deduplication: "Have we seen this evidence before?"
- Integrity: "Has this claim been tampered with?"
- Provenance: "What exact source supports this?"
- **Content-addressable is the answer**

---

## **6.6 Distributed Academic Knowledge Networks** ðŸš€

### **Vision: P2P Verified Citations**

```python
# University A creates claim about Caesar
claim = {
    "source": "Plutarch_Life_of_Caesar",
    "assertion": "Caesar crossed Rubicon in 49 BCE",
    "evidence": "...",
    "cipher": "claim_abc123..."
}

# Generate verification receipt
state_root = MerkleRoot([claim.cipher, sources, entities])
publish_to_network({
    "cipher": claim.cipher,
    "state_root": state_root,
    "institution": "University A",
    "timestamp": "2026-02-12T10:30:00Z"
})

# University B references claim in their research
cite_claim(
    cipher="claim_abc123...",
    state_root="merkle_xyz789...",
    verification_timestamp="2026-02-12T15:00:00Z"
)

# Anyone can verify citation integrity
downloaded = fetch_claim("claim_abc123...")
verified = verify_cipher(downloaded)  # Cryptographic proof
if verified:
    # âœ… Citation is authentic and unaltered
    use_in_research(downloaded)
```

**Enables:**
- âœ… Federated institutional repositories
- âœ… P2P knowledge sharing
- âœ… Reproducible science
- âœ… Academic claims with built-in provenance
- âœ… No central authority needed

---

## **6.7 Implementation Guidelines**

### **Cipher Generation Function:**

```python
import hashlib
import json

def generate_claim_cipher(claim_data: dict) -> str:
    """
    Generate content-addressable cipher for claim.
    
    Args:
        claim_data: Dictionary with all claim components
        
    Returns:
        Unique cipher string (hex hash)
    """
    # Normalize data for consistent hashing
    normalized = {
        "source_work_qid": claim_data["source_work_qid"],
        "passage_hash": hashlib.sha256(
            claim_data["passage_text"].encode()
        ).hexdigest(),
        "subject_entity_qid": claim_data["subject_entity_qid"],
        "object_entity_qid": claim_data.get("object_entity_qid", ""),
        "relationship_type": claim_data.get("relationship_type", ""),
        "temporal_data": claim_data.get("temporal_data", ""),
        "confidence": f"{claim_data['confidence']:.2f}",
        "extractor_agent_id": claim_data["extractor_agent_id"],
        "extraction_timestamp": claim_data["extraction_timestamp"]
    }
    
    # Sort keys for deterministic ordering
    canonical = json.dumps(normalized, sort_keys=True)
    
    # Generate cipher
    cipher_hash = hashlib.sha256(canonical.encode()).hexdigest()
    
    return f"claim_{cipher_hash[:32]}"  # Prefix + first 32 hex chars

# Example usage
claim = generate_claim_cipher({
    "source_work_qid": "Q644312",
    "passage_text": "Caesar crossed the Rubicon...",
    "subject_entity_qid": "Q1048",
    "object_entity_qid": "Q644312",
    "relationship_type": "CAUSED",
    "temporal_data": "-0049-01-10",
    "confidence": 0.95,
    "extractor_agent_id": "genericagent_Q767253_D_v2.0",
    "extraction_timestamp": "2026-02-12T10:30:00Z"
})
# Returns: "claim_b22020c0e271b7d8e4a5f6c9d1b2a3e4"
```

---

### **Best Practices:**

1. **Always check cipher before creating claim**
   - Prevents duplicates
   - Enables automatic consensus

2. **Include timestamp in cipher components**
   - Different extraction times = same cipher (if content identical)
   - Enables temporal tracking

3. **Version claims explicitly when confidence changes**
   - Create new claim with new cipher
   - Link via `SUPERSEDES` relationship
   - Preserve historical record

4. **Index cipher property for performance**
   - O(1) lookup critical for deduplication
   - Consider composite index with status

5. **Use state roots for distributed verification**
   - Merkle tree enables efficient verification
   - Supports P2P academic networks

---

## **6.8 ProposedEdge Node Schema**

**Node Label:** `:ProposedEdge`

**Purpose:** Represents a relationship proposed by a claim that has not yet been materialized. Once validated, the ProposedEdge is converted to an actual relationship in the canonical graph.

### **Required Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `edge_id` | string | `"pedge_001"` | Unique ID |
| `edge_type` | string | `"PARTICIPATED_IN"` | The relationship type to create (Section 7) |
| `from_qid` | string | `"Q1048"` | Source node identifier |
| `to_qid` | string | `"Q193304"` | Target node identifier |
| `timestamp` | string | `"2026-02-12T15:30:00Z"` | When proposed |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `confidence` | float | `0.82` | Confidence in this specific edge |
| `edge_properties` | JSON | `{"role": "commander", "date": "-49-01-10"}` | Properties to add to relationship when materialized |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `PROPOSES` | Claim | `(claim)-[:PROPOSES]->(proposedEdge)` |

### **Example Cypher**

```cypher
// Create proposed edge
CREATE (pedge:ProposedEdge {
  edge_id: "pedge_001",
  edge_type: "FOUGHT_IN",
  from_qid: "Q1048",
  to_qid: "Q193304",
  timestamp: "2026-02-12T15:30:00Z",
  confidence: 0.85,
  edge_properties: {role: "commander", date: "-49-01-10"}
})

// Link to claim
MATCH (claim:Claim {claim_id: "claim_000123"})
CREATE (claim)-[:PROPOSES]->(pedge)
```

---

## **6.9 ReasoningTrace Node Schema**

**Node Label:** `:ReasoningTrace`

**Purpose:** Persist the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted. Enables explainability and audit trails.

### **Required Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `trace_id` | string | `"trace_000987"` | Unique ID |
| `agent_id` | string | `"roman_republic_agent_001"` | Agent that produced this trace |
| `query_text` | string | `"How did Caesar become dictator?"` | Original natural language query |
| `timestamp` | string | `"2026-02-12T15:30:00Z"` | When reasoning occurred |
| `pattern` | string | `"causal_chain"` | High-level reasoning pattern |

### **Optional Properties**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `steps` | string[] | `["Retrieved passages...", "Connected Xâ†’Y"]` | Human-readable reasoning steps |
| `sources_consulted` | string[] | `["Goldsworthy p.145", "Plutarch 32"]` | Bibliographic strings |
| `retrieved_passages` | JSON[] | `[{"source": "Goldsworthy p.145", "text": "..."}]` | Key passages |
| `intermediate_claims` | string[] | `["claim_000120"]` | Supporting claims |
| `confidence` | float | `0.85` | Confidence in the reasoning chain |
| `reasoning_depth` | int | `3` | Number of reasoning hops |
| `fallacy_checks` | string[] | `["anachronism: pass"]` | Fallacy checks performed |

### **Required Edges**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `TRACE_OF` | Claim | `(trace)-[:TRACE_OF]->(claim)` |
| `USED_FOR` | RetrievalContext | `(retrieval)-[:USED_FOR]->(trace)` (optional) |

### **Example Cypher**

```cypher
// Create reasoning trace
CREATE (trace:ReasoningTrace {
  trace_id: "trace_000987",
  agent_id: "roman_republic_agent_001",
  query_text: "How did Caesar become dictator?",
  timestamp: "2026-02-12T15:30:00Z",
  pattern: "causal_chain",
  steps: [
    "Retrieved passages from Plutarch and Suetonius",
    "Connected civil war â†’ dictatorship promotion",
    "Verified with scholarly sources"
  ],
  confidence: 0.85,
  reasoning_depth: 3
})

// Link to claim
MATCH (claim:Claim {claim_id: "claim_000123"})
CREATE (trace)-[:TRACE_OF]->(claim)
```

---

## **6.10 Synthesis & Consensus Resolution**

### **Synthesis Node Schema**

**Node Label:** `:Synthesis`

**Purpose:** When multiple agents produce conflicting claims or reviews, a Synthesis node records the consensus-building process and final resolution.

**Required Properties:**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `synthesis_id` | string | `"synth_000789"` | Unique ID |
| `timestamp` | string | `"2026-02-12T16:15:00Z"` | When synthesis was performed |
| `synthesis_type` | string | `"claim_consolidation"` | Type of synthesis performed |
| `consensus_method` | string | `"weighted_bayesian"` | Method used |

**Optional Properties:**

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `participating_agents` | string[] | `["agent_001", "agent_002"]` | Agents involved |
| `input_claims` | string[] | `["claim_001", "claim_002"]` | Claims being synthesized |
| `output_claim` | string | `"claim_003"` | Resulting synthesized claim |
| `consensus_score` | float | `0.76` | Final consensus confidence |
| `resolution_strategy` | string | `"weighted_average"` | How conflicts were resolved |
| `notes` | string | `"Plutarch's figure accepted as upper bound"` | Summary |

**Required Edges:**

| Relationship | Target | Notes |
|--------------|--------|-------|
| `SYNTHESIZED_FROM` | Claim | Input claims |
| `PRODUCED` | Claim | Output claim |
| `PERFORMED_BY` | Agent | `(agent)-[:PERFORMED_BY]->(synthesis)` |

### **Consensus Calculation Cypher**

```cypher
// Calculate consensus score from reviews
MATCH (claim:Claim {claim_id: "claim_000123"})<-[:REVIEWS]-(review:Review)
WITH claim, 
     avg(review.confidence) AS avg_confidence,
     sum(review.weight * review.confidence) / sum(review.weight) AS weighted_confidence,
     collect(review.verdict) AS verdicts
WITH claim, weighted_confidence,
     size([v IN verdicts WHERE v = "support"]) AS support_count,
     size(verdicts) AS total_count
SET claim.consensus_score = weighted_confidence,
    claim.review_count = total_count,
    claim.status = CASE
        WHEN weighted_confidence >= 0.8 AND support_count >= total_count * 0.7 THEN "validated"
        WHEN weighted_confidence >= 0.5 THEN "disputed"
        ELSE "rejected"
    END
RETURN claim.claim_id, claim.status, claim.consensus_score
```

---

## **6.11 Claim Status Lifecycle**

Claims progress through a validation lifecycle from initial proposal to final disposition:

```
proposed â†’ (validated | disputed | rejected)
```

### **Status Definitions**

**proposed** - Created by a source agent, awaiting review
- Initial state after claim extraction
- Not yet visible in canonical graph
- Requires review by domain agents

**validated** - Supported by sufficient reviews (consensus_score â‰¥ 0.8)
- High confidence from multiple reviewers
- Support from â‰¥70% of reviews
- Proposed subgraph promoted to canonical graph
- Visible in standard queries

**disputed** - Mixed or low-confidence reviews (0.5 â‰¤ consensus_score < 0.8)
- Conflicting agent opinions
- Requires additional evidence or human review
- Not promoted to canonical graph
- Flagged for further investigation

**rejected** - Strong consensus against (consensus_score < 0.5)
- Low confidence from reviewers
- Majority of reviews challenge claim
- Not promoted to canonical graph
- May indicate extraction error or source misinterpretation

### **State Transition Rules**

```cypher
// Automatic status update based on consensus
MATCH (claim:Claim {status: "proposed"})
WHERE claim.review_count >= 3  // Minimum reviews required
WITH claim
MATCH (claim)<-[:REVIEWS]-(review:Review)
WITH claim,
     avg(review.confidence) AS avg_conf,
     sum(CASE WHEN review.verdict = "support" THEN 1 ELSE 0 END) * 1.0 / count(review) AS support_ratio
SET claim.status = CASE
    WHEN avg_conf >= 0.8 AND support_ratio >= 0.7 THEN "validated"
    WHEN avg_conf >= 0.5 THEN "disputed"
    ELSE "rejected"
END
```

---

## **6.12 Promotion Logic**

When a claim reaches `status = "validated"`, its proposed structure is **promoted** to the canonical graph.

### **Promotion Steps**

1. **Remove proposed status** from proposed nodes
   ```cypher
   MATCH (claim:Claim {status: "validated"})-[:PROPOSES]->(entity)
   REMOVE entity.claim_status
   SET entity.promoted = true,
       entity.promotion_date = datetime()
   ```

2. **Convert ProposedEdge to actual relationships**
   ```cypher
   MATCH (claim:Claim {status: "validated"})-[:PROPOSES]->(pedge:ProposedEdge)
   MATCH (from {qid: pedge.from_qid}), (to {qid: pedge.to_qid})
   CALL apoc.create.relationship(
     from, 
     pedge.edge_type, 
     pedge.edge_properties, 
     to
   ) YIELD rel
   SET rel.promoted_from_claim = claim.claim_id,
       rel.promotion_date = datetime()
   DELETE pedge
   ```

3. **Update consensus metadata**
   ```cypher
   MATCH (claim:Claim {status: "validated"})
   SET claim.promoted = true,
       claim.promotion_date = datetime()
   ```

4. **Link claim to materialized structure via provenance edges**
   ```cypher
   MATCH (claim:Claim {status: "validated"})
   MATCH (entity {qid: claim.subject_entity_qid})
   CREATE (entity)-[:SUPPORTED_BY {
     confidence: claim.consensus_score,
     promotion_date: datetime()
   }]->(claim)
   ```

### **Key Properties**

- **Idempotent:** Promotion can be safely re-run without creating duplicates
- **Reversible:** Claims can be demoted if new evidence challenges consensus
- **Auditable:** Promotional edges maintain provenance trail

### **Query Pattern: Check Promotion Status**

```cypher
// Find all validated but unpromoted claims
MATCH (claim:Claim {status: "validated"})
WHERE claim.promoted IS NULL OR claim.promoted = false
RETURN claim.claim_id, claim.consensus_score, claim.review_count
ORDER BY claim.consensus_score DESC

// Find promoted structure for specific claim
MATCH (claim:Claim {claim_id: "claim_000123"})
MATCH (entity)-[rel:SUPPORTED_BY]->(claim)
RETURN entity, rel, claim
```

---

## **6.13 Integration with Other Layers**

The Claims Layer is deeply integrated with Entity (Section 3), Subject (Section 4), Agent (Section 5), and Relationship (Section 7) layers.

### **6.13.1 Subject Layer Integration**

Claims attach to SubjectConcepts for domain classification:

```cypher
(claim)-[:SUBJECT_OF]->(subjectConcept)
```

**Enables:**
- Topic classification by LCC/FAST
- Agent routing (Section 5.6)
- Facet alignment (Section 4.2)
- Domain-specific review
- Synthesis grouping

**Example: Route claim to domain experts**
```cypher
MATCH (claim:Claim {claim_id: "claim_000123"})-[:SUBJECT_OF]->(sc:SubjectConcept)
MATCH (agent:Agent)-[:OWNS_DOMAIN]->(sc)
RETURN agent.agent_id, agent.label, sc.lcc_class
```

### **6.13.2 Entity Layer Integration**

Claims attach to entities they describe:

```cypher
(entity)-[:SUBJECT_OF]->(claim)
```

**Enables:**
- Entity-centric reasoning
- Event interpretation
- Biographical claims
- Periodization claims
- Geographic claims

**Example: All claims about Caesar**
```cypher
MATCH (p:Human {qid: "Q1048"})-[:SUBJECT_OF]->(claim:Claim)
WHERE claim.status IN ["validated", "proposed"]
RETURN claim.text, claim.confidence, claim.status
ORDER BY claim.confidence DESC
```

### **6.13.3 Agent Layer Integration**

Agents interact with claims throughout their lifecycle:

**Agent Actions:**
- `MADE_CLAIM` - Create claims
- `REVIEWED` - Review claims  
- `PERFORMED_BY` - Perform synthesis
- `OWNS_DOMAIN` - Claim routing (via SubjectConcept)

**Example: Agent's claim history**
```cypher
MATCH (agent:Agent {agent_id: "roman_republic_agent"})-[:MADE_CLAIM]->(claim:Claim)
RETURN claim.claim_id, claim.text, claim.status, claim.consensus_score
ORDER BY claim.timestamp DESC

// Agent's review activity
MATCH (agent:Agent {agent_id: "roman_republic_agent"})-[:REVIEWED]->(review:Review)
      -[:REVIEWS]->(claim:Claim)
RETURN claim.claim_id, review.verdict, review.confidence
```

### **6.13.4 Relationship Layer Integration**

Claims propose relationships via ProposedEdge nodes:

```cypher
(claim)-[:PROPOSES]->(proposed_edge:ProposedEdge)
```

**Upon validation:**
- ProposedEdge specifies relationship type from canonical registry (Section 7.1)
- Edge properties include action structure metadata (Section 7.6)
- Promoted edges maintain provenance links to originating claims

**Example: Claim proposing relationships**
```cypher
MATCH (claim:Claim {claim_id: "claim_000123"})-[:PROPOSES]->(pedge:ProposedEdge)
RETURN pedge.edge_type, pedge.from_qid, pedge.to_qid, pedge.confidence

// After promotion: Find promoted relationship
MATCH (claim:Claim {claim_id: "claim_000123", status: "validated"})
MATCH (from)-[rel]->(to)
WHERE rel.promoted_from_claim = claim.claim_id
RETURN type(rel), from.name, to.name, rel.promotion_date
```

---

## **6.14 Cypher Query Patterns**

### **Pattern 1: Complete Claim Provenance Chain**

```cypher
// Trace claim from source to validation
MATCH (work:Work {qid: "Q644312"})
      <-[:EXTRACTED_FROM]-(claim:Claim {claim_id: "claim_000123"})
      <-[:MADE_CLAIM]-(agent:Agent)
OPTIONAL MATCH (claim)<-[:REVIEWS]-(review:Review)<-[:REVIEWED]-(reviewer:Agent)
OPTIONAL MATCH (claim)-[:HAS_TRACE]->(trace:ReasoningTrace)
RETURN work.title, agent.agent_id, claim.text, claim.status,
       collect(DISTINCT reviewer.agent_id) AS reviewers,
       trace.reasoning_depth
```

### **Pattern 2: Find Claims Needing Review**

```cypher
// Claims with insufficient reviews
MATCH (claim:Claim {status: "proposed"})
WHERE claim.review_count < 3
  AND duration.between(datetime(claim.timestamp), datetime()).days < 30
RETURN claim.claim_id, claim.text, claim.review_count, claim.confidence
ORDER BY claim.confidence DESC
LIMIT 20
```

### **Pattern 3: Consensus Analysis**

```cypher
// Analyze review distribution for claim
MATCH (claim:Claim {claim_id: "claim_000123"})<-[:REVIEWS]-(review:Review)
WITH claim,
     collect({
       agent: review.agent_id,
       verdict: review.verdict,
       confidence: review.confidence
     }) AS reviews,
     avg(review.confidence) AS avg_confidence
RETURN claim.claim_id,
       claim.consensus_score,
       avg_confidence,
       reviews
```

### **Pattern 4: Conflicting Claims Detection**

```cypher
// Find claims about same subject with conflicting assertions
MATCH (entity {qid: "Q1048"})-[:SUBJECT_OF]->(claim1:Claim)
MATCH (entity)-[:SUBJECT_OF]->(claim2:Claim)
WHERE claim1.claim_id < claim2.claim_id
  AND claim1.relationship_type = claim2.relationship_type
  AND claim1.object_entity_qid <> claim2.object_entity_qid
  AND claim1.status = "validated"
  AND claim2.status = "validated"
RETURN claim1.text, claim2.text, 
       claim1.consensus_score, claim2.consensus_score
```

---

# **7. Relationship Layer**

## **7.0 Relationship Layer Overview**

The **Relationship Layer** defines canonical relationship types connecting entities in the knowledge graph. Unlike Claims (which represent evidence), relationships are **first-class graph edges** supporting traversal, pattern matching, and graph algorithms.

### **Key Principles**

**1. Triple Alignment Architecture**
- **Chrystallum:** Native relationship types optimized for historical research
- **Wikidata:** P-property alignment for linked data interoperability
- **CIDOC-CRM:** ISO 21127:2023 compliance for museum/archival integration

**2. Semantic Categorization**
- 300 canonical relationship types across 31 semantic categories
- Categories align with historical domains (Military, Political, Economic, etc.)
- Hierarchical with parent-child specificity levels

**3. Multi-Authority Metadata**
- **LCC classification:** Domain-specific routing (e.g., "D" for History)
- **LCSH heading:** Standardized terminology (e.g., "Military History")
- **FAST ID:** Faceted topic tagging for discovery

**4. Bidirectional Clarity**
- Forward/inverse/symmetric directionality explicitly defined
- Enables natural language expression from either entity perspective
- Reduces query complexity by providing both directions

**5. Lifecycle Management**
- Status tracking: `candidate`, `active`, `deprecated`
- Version control: tracks schema evolution
- Source attribution: links to discovery/import process

---

## **7.1 Relationship Type Schema**

### **Canonical Relationship Type Properties**

```cypher
(:RelationshipType {
  // IDENTIFICATION
  relationship_type: "FOUGHT_IN",           // Canonical type name
  category: "Military",                      // Semantic category
  
  // DESCRIPTION & DIRECTIONALITY
  description: "Person participated in battle/war",
  directionality: "forward",                 // forward | inverse | symmetric | unidirectional
  
  // TRIPLE ALIGNMENT
  wikidata_property: "P607",                 // Wikidata P-ID
  cidoc_crm_property: "P11_had_participant", // CIDOC-CRM property
  cidoc_crm_class: "E7_Activity",           // CRM class (if reified as event)
  
  // HIERARCHY & SPECIFICITY
  parent_relationship: "MILITARY_ACTION",    // Parent type (for hierarchy)
  specificity_level: 2,                      // 1=generic, 2=specific, 3=highly specific
  
  // AUTHORITY ALIGNMENT
  lcc_code: "U",                            // Library of Congress Class
  lcsh_heading: "Military History",         // LCSH subject heading
  fast_id: "fst01021997",                   // FAST topical ID
  
  // LIFECYCLE
  status: "active",                         // candidate | active | deprecated
  lifecycle_status: "implemented",          // candidate | implemented | deprecated
  version: "1.0",                           // Schema version
  source: "bidirectional_csv",              // Discovery source
  note: "Person as participant in military event"
})
```

---

## **7.2 Relationship Categories**

### **Distribution by Category (300 Total Relationship Types)**

| Category | Count | Description | Example Types |
|----------|-------|-------------|--------------|
| **Political** | 39 | Governance, power, institutions | APPOINTED, GOVERNED, ALLIED_WITH |
| **Familial** | 30 | Family relationships | FATHER_OF, MARRIED_TO, COUSIN_OF |
| **Military** | 23 | Warfare, command, battles | DEFEATED, COMMANDED_BY, BESIEGED |
| **Geographic** | 20 | Location, movement | BORN_IN, MIGRATED_TO, LOCATED_IN |
| **Economic** | 16 | Wealth, trade, taxation | TAXED, CONFISCATED_LAND_FROM |
| **Legal** | 13 | Law, justice, punishment | CONVICTED_OF, SENTENCED_TO |
| **Diplomatic** | 13 | Negotiation, alliances, envoys | NEGOTIATED_WITH, SENT_ENVOYS_TO |
| **Authorship** | 12 | Creation, attribution | AUTHOR, COMPOSER, ARCHITECT |
| **Attribution** | 11 | Citation, analysis, mention | EXTRACTED_FROM, DESCRIBES |
| **Application** | 10 | Material usage, production | MATERIAL_USED, PRODUCED_IN |
| **Evolution** | 10 | Change over time | REPLACED_BY, INTRODUCED_IN |
| **Institutional** | 9 | Organization membership | MEMBER_OF, PART_OF |
| **Position** | 8 | Roles, offices held | POSITION_HELD, HELD_POSITION_IN |
| **Cultural** | 8 | Cultural identity, assimilation | ASSIMILATED_TO, EVOLVED_FROM |
| **Honorific** | 8 | Awards, titles, decorations | AWARDED_TO, GRANTED_TITLE |
| **Causality** | 8 | Cause-effect relationships | CAUSED, CONTRIBUTED_TO |
| **Religious** | 6 | Faith, conversion, doctrine | CONVERTED_TO, RELIGIOUS_LEADER_OF |
| **Reasoning** | 6 | Inference, belief adoption | BELIEF_ABOUT, EVIDENCE_FOR |
| **Production** | 6 | Creation, manufacturing | DEPICTS, DISCOVERED_BY |
| **Social** | 6 | Patronage, social ties | PATRON_TO, SUPPORTER_OF |
| **Temporal** | 6 | Time relationships | DURING, PART_OF |
| **Functional** | 4 | Purpose, use | USE, USED_BY |
| **Comparative** | 4 | Superiority, inferiority | SUPERIOR_TO, ADVANTAGE |
| **Trade** | 3 | Commerce, exchange | TRADED_WITH, EXPORTED_TO |
| **Typological** | 3 | Type classification | SUBTYPE_OF, INSTANCE_OF |
| **Moral** | 3 | Ethics, justice | JUSTIFIED_BY, RIGHT_THING |
| **Linguistic** | 2 | Language, translation | TRANSLATION_OF, NAMED_AFTER |
| **Ideological** | 2 | Belief systems | IDEOLOGICAL_ALIGNMENT |
| **Membership** | 2 | Group belonging | TRIBE_MEMBERSHIP |
| **Measurement** | 2 | Quantification | MEASURED_AS |

---

## **7.3 Triple Alignment: Chrystallum â†” Wikidata â†” CIDOC-CRM**

### **Alignment Strategy**

**Purpose:** Enable interoperability with linked data (Wikidata) and cultural heritage systems (CIDOC-CRM) while maintaining Chrystallum's historical research optimizations.

**Benefits:**
1. **Museum/Archival Integration:** Export CIDOC-CRM compatible RDF/OWL
2. **Linked Data Queries:** Query via Wikidata SPARQL endpoints
3. **Academic Standards:** ISO 21127:2023 compliance
4. **Query Flexibility:** All three ontologies available simultaneously

### **Alignment Examples**

| Chrystallum Type | Wikidata Property | CIDOC-CRM Property | CIDOC-CRM Class |
|------------------|-------------------|--------------------|-----------------|
| **LOCATED_IN** | P131 (located in the administrative territorial entity) | crm:P7_took_place_at | â€” |
| **AUTHOR** | P50 (author) | crm:P14_carried_out_by | E12_Production |
| **FOUGHT_IN** | P607 (conflict) | crm:P11_had_participant | E7_Activity |
| **BORN_IN** | P19 (place of birth) | crm:P7_took_place_at | E67_Birth |
| **CAUSED** | P828 (has cause) | crm:P15_was_influenced_by | â€” |
| **APPOINTED** | P39 (position held) | crm:P14.1_in_the_role_of | E13_Attribute_Assignment |
| **PART_OF** | â€” | crm:P86_falls_within | â€” |
| **FOUNDED** | P112 (founded by) | crm:P14_carried_out_by | E63_Beginning_of_Existence |

### **Coverage Statistics**

- **Total Relationship Types:** 300
- **With Wikidata Alignment:** 147 (49%)
- **With CIDOC-CRM Alignment:** 89 (30%)
- **With Both Alignments:** 72 (24%)
- **Chrystallum-Specific:** 153 (51%) - optimized for historical research needs

**Note:** Chrystallum-specific relationships address historical domain needs not covered by general-purpose ontologies (e.g., Roman gens relationships, patron-client ties, proscription lists).

---

## **7.4 Directionality Patterns**

### **Directionality Types**

**1. Forward (Source â†’ Target)**
```cypher
(:Human {name: "Caesar"})-[:FOUGHT_IN]->(:Event {label: "Battle of Pharsalus"})
```

**2. Inverse (Target â† Source)**
```cypher
(:Event {label: "Battle of Pharsalus"})-[:BATTLE_PARTICIPANT]->(:Human {name: "Caesar"})
```
*Note: Inverse types provide natural language clarity from the opposite entity perspective*

**3. Symmetric (Bidirectional)**
```cypher
(:Human {name: "Caesar"})-[:ALLIED_WITH]->(:Human {name: "Pompey"})
(:Human {name: "Pompey"})-[:ALLIED_WITH]->(:Human {name: "Caesar"})
```
*Note: Symmetric relationships create edges in both directions*

**4. Unidirectional (Single Direction)**
```cypher
(:Event {label: "Death of Caesar"})-[:CAUSED]->(:Event {label: "Second Triumvirate"})
```
*Note: No inverse relationship type defined*

### **Bidirectional Pairs (Forward/Inverse)**

Common patterns enabling natural queries from either entity:

| Forward | Inverse | Example |
|---------|---------|---------|
| FATHER_OF | CHILD_OF | Caesar FATHER_OF Julia / Julia CHILD_OF Caesar |
| FOUNDED | FOUNDED_BY | Caesar FOUNDED colony / Colony FOUNDED_BY Caesar |
| CONQUERED | CONQUERED_BY | Rome CONQUERED Gaul / Gaul CONQUERED_BY Rome |
| AUTHOR | WORK_OF | Plutarch AUTHOR "Life of Caesar" / "Life of Caesar" WORK_OF Plutarch |
| PRODUCES_GOOD | PRODUCED_BY | Factory PRODUCES_GOOD pottery / Pottery PRODUCED_BY factory |

---

## **7.5 Hierarchical Relationships (Parent-Child Specificity)**

### **Specificity Levels**

**Level 1 (Generic):** Broad categories
- `MILITARY_ACTION`, `POLITICAL_ACTION`, `ECONOMIC_ACTION`
- Used when specific relationship type unknown or inapplicable

**Level 2 (Specific):** Common historical relationships
- `FOUGHT_IN`, `APPOINTED`, `TAXED`
- Most common level for historical research

**Level 3 (Highly Specific):** Nuanced distinctions
- `COMMANDED_CAVALRY_IN`, `PROSCRIBED`, `CONDEMNED_WITHOUT_TRIAL`
- Captures fine-grained historical detail

### **Hierarchical Examples**

**Military Hierarchy:**
```
MILITARY_ACTION (level 1)
  â”œâ”€ FOUGHT_IN (level 2)
  â”œâ”€ COMMANDED_BY (level 2)
  â”‚   â””â”€ COMMANDED_CAVALRY_IN (level 3)
  â”œâ”€ DEFEATED (level 2)
  â””â”€ BESIEGED (level 2)
```

**Political Hierarchy:**
```
POLITICAL_ACTION (level 1)
  â”œâ”€ APPOINTED (level 2)
  â”‚   â””â”€ APPOINTED_CONSUL (level 3)
  â”œâ”€ GOVERNED (level 2)
  â””â”€ DEPOSED (level 2)
```

**Economic Hierarchy:**
```
ECONOMIC_ACTION (level 1)
  â”œâ”€ TAXED (level 2)
  â”œâ”€ CONFISCATED_LAND_FROM (level 2)
  â””â”€ DISTRIBUTED_LAND_TO (level 2)
```

**Benefits:**
- Enables query generalization (find all `MILITARY_ACTION` relationships)
- Supports progressive refinement (start broad, drill down to specifics)
- Facilitates agent routing (broad categories â†’ specialist agents)

---

## **7.6 Action Structure Integration**

### **Action Structure Vocabularies**

Chrystallum incorporates **goal-trigger-action-result** framework for understanding historical events. This structured approach enables agents to reason about motivation, causality, and outcomes.

**Vocabulary Categories:**

**1. Goal Types (14 vocabularies)**
- Political, Personal, Military, Economic, Constitutional, Moral, Cultural, Religious, Diplomatic, Survival
- *Example:* "Caesar's goal: Gain political power (POLITICAL)"

**2. Trigger Types (10 vocabularies)**
- Circumstantial, Moral, Emotional, Political, Personal, External Threat, Internal Pressure, Legal, Ambition, Opportunity
- *Example:* "Trigger: Senate threatens prosecution (POLITICAL_TRIGGER)"

**3. Action Types (16 vocabularies)**
- Political Revolution, Military Action, Criminal Act, Diplomatic Action, Constitutional Innovation, Economic Action, Legal Action, Social Action, Religious Action, Personal Action, Administrative, Causal Chain, Tyrannical Governance, Defensive Action, Offensive Action
- *Example:* "Action: Cross Rubicon with army (MILITARY_ACTION)"

**4. Result Types (14 vocabularies)**
- Political Transformation, Institutional Creation, Conquest, Defeat, Alliance, Tragic, Success, Failure, Stability, Instability, Legal Outcome, Cultural Change, Personal Outcome, Economic Outcome
- *Example:* "Result: Civil war begins (POLITICAL_TRANSFORMATION)"

### **Integration with Relationship Types**

Action structure properties are **optional annotations** on relationship edges, enabling richer historical analysis:

```cypher
(:Human {name: "Caesar"})
  -[:CAUSED {
      goal_type: "POLITICAL",
      trigger_type: "POLITICAL_TRIGGER", 
      action_type: "MILITARY_ACTION",
      result_type: "POLITICAL_TRANSFORMATION",
      goal_description: "Assert power against Senate",
      trigger_description: "Senate threatens prosecution",
      action_description: "Cross Rubicon with legion",
      result_description: "Start of civil war"
    }]->
(:Event {label: "Roman Civil War"})
```

### **Wikidata Property Mapping**

Action structure types align with Wikidata qualifiers:

| Action Component | Wikidata Property | Example |
|------------------|-------------------|---------|
| **Goal** | P3712 (objective) | "Gain territory" |
| **Trigger** | P828 (has cause) | "Enemy invasion" |
| **Action** | P279 (subclass of) | "Military campaign" |
| **Result** | P1542 (has effect) | "Conquest completed" |

**Source:** `CSV/action_structure_vocabularies.csv`, `CSV/action_structure_wikidata_mapping.csv`

---

## **7.7 Key Relationship Types by Domain**

### **7.7.1 Military Relationships (23 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **FOUGHT_IN** | forward | P607 | P11_had_participant | Person participated in battle/war |
| **BATTLE_PARTICIPANT** | inverse | â€” | P11i_participated_in | Battle had this participant |
| **DEFEATED** | forward | â€” | â€” | Victor defeated vanquished entity |
| **DEFEATED_BY** | inverse | â€” | â€” | Vanquished was defeated by victor |
| **COMMANDED_BY** | forward | â€” | P14_carried_out_by | Military unit commanded by person |
| **SERVED_UNDER** | forward | â€” | â€” | Person served under commander |
| **BESIEGED** | forward | â€” | â€” | Entity besieged location |
| **BESIEGED_BY** | inverse | â€” | â€” | Location was besieged by entity |
| **CONQUERED** | forward | P47 | E8_Acquisition | Entity conquered territory |
| **CONQUERED_BY** | inverse | P47 | E8_Acquisition | Territory conquered by entity |
| **MASSACRED** | forward | â€” | â€” | Entity massacred group |
| **LEVELLED** | forward | â€” | E6_Destruction | Entity destroyed/leveled location |
| **SACKED** | forward | â€” | â€” | Entity sacked/pillaged location |
| **GARRISONED** | forward | â€” | â€” | Entity garrisoned troops at location |
| **BETRAYED** | forward | â€” | â€” | Entity betrayed another entity |
| **DEFECTED_TO** | forward | â€” | E85_Joining | Entity defected to another allegiance |

**Example Cypher:**
```cypher
// Find all battles Caesar fought in
MATCH (caesar:Human {name: "Gaius Julius Caesar"})
      -[:FOUGHT_IN]->(battle:Event {event_type: "battle"})
RETURN battle.label, battle.start_date, battle.location

// Find who defeated Pompey
MATCH (pompey:Human {name: "Pompey"})<-[:DEFEATED]-(victor:Human)
RETURN victor.name, battle.label

// Military command structure
MATCH (commander:Human)-[:COMMANDED_BY*1..3]-(subordinate:Human)
WHERE commander.name = "Caesar"
RETURN subordinate.name, subordinate.rank
```

---

### **7.7.2 Political Relationships (39 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **APPOINTED** | forward | P39 | E13_Attribute_Assignment | Appointer appointed person to office |
| **APPOINTED_BY** | inverse | P39 | E13_Attribute_Assignment | Person was appointed by appointer |
| **GOVERNED** | forward | â€” | â€” | Person governed jurisdiction during period |
| **CONTROLLED** | forward | P17 | â€” | Entity controlled territory/institution |
| **ALLIED_WITH** | symmetric | â€” | â€” | Entities formed alliance |
| **OPPOSED** | symmetric | â€” | â€” | Entities were in opposition |
| **DEPOSED** | forward | â€” | E86_Leaving | Entity deposed ruler from power |
| **PROSCRIBED** | forward | â€” | E13_Attribute_Assignment | Authority proscribed person (outlawed with property confiscation) |
| **OUTLAWED** | forward | â€” | E13_Attribute_Assignment | Authority outlawed person |
| **LEGITIMATED** | forward | â€” | â€” | Entity legitimated authority's power |
| **DECLARED_FOR** | forward | â€” | â€” | Entity declared allegiance to another |
| **COMPETED_WITH** | symmetric | â€” | â€” | Entities competed for power/office |
| **ADVISED** | forward | â€” | â€” | Advisor advised leader/institution |
| **MANIPULATED** | forward | â€” | â€” | Entity manipulated another for political aims |
| **HEIR_TO** | forward | P1365 | â€” | Person designated heir to position/realm |

**Example Cypher:**
```cypher
// Find Caesar's political appointments
MATCH (caesar:Human {name: "Caesar"})-[:APPOINTED]->(appointee:Human)
      -[:POSITION_HELD]->(position:Position)
RETURN appointee.name, position.label, position.start_date

// Find who opposed Caesar
MATCH (caesar:Human {name: "Caesar"})-[:OPPOSED]-(opponent:Human)
RETURN opponent.name

// Political alliance network
MATCH path = (entity:Human)-[:ALLIED_WITH*1..3]-(ally:Human)
WHERE entity.entity_id = "hum_caesar"
RETURN ally.name, length(path) AS degrees_of_alliance
```

---

### **7.7.3 Familial Relationships (30 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **FATHER_OF** | forward | P40 | â€” | Person is father of child |
| **CHILD_OF** | inverse | P22 | â€” | Person is child of parent |
| **MARRIED_TO** | symmetric | P26 | â€” | Person married to spouse |
| **SIBLING_OF** | symmetric | P3373 | â€” | Person is sibling |
| **HALF_SIBLING_OF** | symmetric | P3373 | â€” | Person is half-sibling |
| **GRANDPARENT_OF** | forward | â€” | â€” | Person is grandparent of grandchild |
| **GRANDCHILD_OF** | inverse | â€” | â€” | Person is grandchild of grandparent |
| **COUSIN_OF** | symmetric | â€” | â€” | Person is cousin |
| **AUNT_OF** | forward | â€” | â€” | Person is aunt/uncle |
| **ADOPTED_BY** | forward | â€” | â€” | Person was adopted by adopter |
| **FATHER_IN_LAW_OF** | forward | â€” | â€” | Person is father-in-law |
| **BROTHER_IN_LAW_OF** | forward | â€” | â€” | Person is brother-in-law |
| **DAUGHTER_IN_LAW_OF** | forward | â€” | â€” | Person is daughter-in-law |

**Roman-Specific Familial:**
| **MEMBER_OF_GENS** | forward | â€” | â€” | Person member of Roman gens (clan) |
| **GENS_OF** | inverse | â€” | â€” | Gens contains this person |
| **HAS_PRAENOMEN** | forward | â€” | â€” | Person has Roman praenomen (personal name) |
| **HAS_COGNOMEN** | forward | â€” | â€” | Person has Roman cognomen (family branch name) |

**Example Cypher:**
```cypher
// Find Caesar's family tree (3 generations)
MATCH path = (caesar:Human {name: "Caesar"})
             -[:FATHER_OF|CHILD_OF|SIBLING_OF*1..3]-(relative:Human)
RETURN relative.name, labels(relative), length(path)

// Roman gens membership
MATCH (person:Human)-[:MEMBER_OF_GENS]->(gens:Gens {name: "Julia"})
RETURN person.name, person.praenomen, person.cognomen

// Marriage alliances
MATCH (person1:Human)-[:MARRIED_TO]->(person2:Human)
WHERE (person1)-[:MEMBER_OF_GENS]->(:Gens {name: "Julia"})
RETURN person1.name, person2.name, person2.gens_name
```

---

### **7.7.4 Geographic Relationships (20 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **BORN_IN** | forward | P19 | P7_took_place_at | Person born in location |
| **DIED_IN** | forward | P20 | P7_took_place_at | Person died in location |
| **LIVED_IN** | forward | P551 | â€” | Person resided in location during period |
| **LOCATED_IN** | forward | P131 | P7_took_place_at | Entity located in geographic region |
| **MIGRATED_TO** | forward | â€” | P26_moved_to | Group migrated to destination |
| **MIGRATED_FROM** | forward | â€” | P27_moved_from | Group migrated from origin |
| **EXILED** | forward | â€” | â€” | Authority exiled person to location |
| **FLED_TO** | forward | â€” | â€” | Person fled to safe location |
| **FLED_FROM** | forward | â€” | â€” | Person fled from dangerous location |
| **FOUNDED** | forward | P112 | E63_Beginning_of_Existence | Founder established place/institution in location |
| **CAMPAIGN_IN** | forward | â€” | â€” | Military campaign occurred in region |
| **RENAMED** | forward | P1448 | E15_Identifier_Assignment | Entity renamed place |

**Example Cypher:**
```cypher
// Find where Caesar lived
MATCH (caesar:Human {name: "Caesar"})-[:LIVED_IN]->(place:Place)
RETURN place.label, place.place_type

// Migration patterns
MATCH (group:Group)-[:MIGRATED_FROM]->(origin:Place),
      (group)-[:MIGRATED_TO]->(dest:Place)
RETURN group.name, origin.label, dest.label

// Exile network
MATCH (person:Human)-[:EXILED]->(:Place {label: "Massilia"})
RETURN person.name, person.exile_start_date
```

---

### **7.7.5 Diplomatic Relationships (13 types)**

| Relationship Type | Directionality | Wikidata | Description |
|-------------------|----------------|----------|-------------|
| **NEGOTIATED_WITH** | symmetric | â€” | Entities engaged in negotiations |
| **SENT_ENVOYS_TO** | forward | â€” | Sender dispatched envoys to recipient |
| **RECEIVED_ENVOYS_FROM** | inverse | â€” | Recipient received envoys from sender |
| **APPEALED_TO** | forward | â€” | Appellant requested help from entity |
| **RECEIVED_APPEAL_FROM** | inverse | â€” | Entity received request for help |
| **ACCEPTED_OFFER** | forward | â€” | Entity accepted diplomatic offer |
| **REJECTED_OFFER** | forward | â€” | Entity rejected diplomatic offer |
| **OFFERED_SELF_TO** | forward | â€” | Entity offered allegiance/submission |
| **RECEIVED_OFFER_FROM** | inverse | â€” | Entity received offer of allegiance |

**Example Cypher:**
```cypher
// Diplomatic negotiations between Rome and tribes
MATCH (rome:Organization {name: "Roman Republic"})
      -[:NEGOTIATED_WITH]-(tribe:Group)
WHERE tribe.group_type = "Germanic tribe"
RETURN tribe.name, tribe.treaty_date

// Envoy network
MATCH (sender)-[:SENT_ENVOYS_TO]->(recipient)
WHERE sender.name CONTAINS "Rome"
RETURN recipient.name, COUNT(*) AS envoy_missions
ORDER BY envoy_missions DESC

// Failed diplomacy leading to war
MATCH (entity1)-[:REJECTED_OFFER]->(offer),
      (offer)<-[:MADE_OFFER]-(entity2),
      (entity1)-[:FOUGHT_IN]->(war:Event),
      (entity2)-[:FOUGHT_IN]->(war)
RETURN entity1.name, entity2.name, war.label
```

---

### **7.7.6 Economic Relationships (16 types)**

| Relationship Type | Directionality | Wikidata | Description |
|-------------------|----------------|----------|-------------|
| **CONFISCATED_LAND_FROM** | forward | â€” | Authority confiscated property from owner |
| **DISTRIBUTED_LAND_TO** | forward | â€” | Authority distributed land to recipients |
| **TAXED** | forward | â€” | Authority taxed entity/territory |
| **PRODUCES_GOOD** | forward | P1056 | Entity produces goods/services |
| **PRODUCED_BY** | inverse | P1056 | Goods produced by entity |
| **TRADED_WITH** | symmetric | â€” | Entities engaged in trade |
| **EXPORTED_TO** | forward | â€” | Entity exported goods to destination |
| **IMPORTED_FROM** | forward | â€” | Entity imported goods from source |
| **SOLD_INTO_SLAVERY** | forward | â€” | Entity sold people into slavery |
| **EXPERIENCED_RECESSION** | forward | â€” | Economy experienced recession during period |

**Example Cypher:**
```cypher
// Land confiscation during proscriptions
MATCH (authority)-[:CONFISCATED_LAND_FROM]->(victim:Human)
      -[:PROSCRIBED_BY]->(authority)
WHERE authority.name = "Second Triumvirate"
RETURN victim.name, victim.property_value

// Trade networks
MATCH path = (city1:Place)-[:TRADED_WITH*1..3]-(city2:Place)
WHERE city1.label = "Rome"
RETURN city2.label, length(path) AS trade_distance

// Economic production chains
MATCH (region:Place)-[:PRODUCES_GOOD]->(good:Material)
      -[:EXPORTED_TO]->(destination:Place {label: "Rome"})
RETURN region.label, good.name, COUNT(*) AS export_volume
```

---

### **7.7.7 Legal Relationships (13 types)**

| Relationship Type | Directionality | Wikidata | CIDOC-CRM | Description |
|-------------------|----------------|----------|-----------|-------------|
| **CHARGED_WITH** | forward | â€” | E13_Attribute_Assignment | Person charged with crime |
| **CONVICTED_OF** | forward | P1399 | E13_Attribute_Assignment | Person convicted of crime |
| **SENTENCED_TO** | forward | â€” | E13_Attribute_Assignment | Person sentenced to punishment |
| **EXECUTED** | forward | â€” | E69_Death | Authority executed person |
| **IMPRISONED_IN** | forward | â€” | â€” | Person imprisoned in facility |
| **CONDEMNED_WITHOUT_TRIAL** | forward | â€” | â€” | Authority condemned person without legal process |
| **LEGAL_ACTION** | unidirectional | â€” | â€” | Generic legal proceeding |

**Example Cypher:**
```cypher
// Caesar's assassination conspirators - legal aftermath
MATCH (conspirator:Human)-[:PARTICIPATED_IN]->(:Event {label: "Assassination of Caesar"})
OPTIONAL MATCH (conspirator)-[:CHARGED_WITH]->(crime),
               (conspirator)-[:EXECUTED_BY]->(executor)
RETURN conspirator.name, crime.label, executor.name

// Proscription victims
MATCH (victim:Human)-[:PROSCRIBED]->(authority)
      -[:CONDEMNED_WITHOUT_TRIAL]->(victim)
RETURN victim.name, authority.name, victim.proscription_date

// Prison locations
MATCH (person:Human)-[:IMPRISONED_IN]->(facility:Place)
WHERE facility.place_type = "prison"
RETURN facility.label, COUNT(person) AS prisoner_count
```

---

### **7.7.8 Temporal Relationships (6 types)**

| Relationship Type | Directionality | CIDOC-CRM | Description |
|-------------------|----------------|-----------|-------------|
| **DURING** | forward | P4_has_time-span | Event occurred during period |
| **PART_OF** | forward | P86_falls_within | Year/decade/century falls within larger temporal span |
| **SUB_PERIOD_OF** | forward | P9_consists_of | Period is subdivision of larger period |
| **CONTAINS_EVENT** | inverse | P9i_forms_part_of | Period contains event |
| **START_EDGE** | forward | P4_has_time-span | Marks beginning of period |
| **END_EDGE** | forward | P4_has_time-span | Marks end of period |

**Example Cypher:**
```cypher
// Events during Roman Republic period
MATCH (event:Event)-[:DURING]->(period:Period {label: "Roman Republic"})
RETURN event.label, event.start_date
ORDER BY event.start_date

// Period hierarchy (Roman history)
MATCH path = (sub_period:Period)-[:SUB_PERIOD_OF*1..3]->(period:Period)
WHERE period.label = "Ancient Rome"
RETURN sub_period.label, length(path) AS depth

// Beginning/end markers
MATCH (period:Period {label: "Roman Republic"})
OPTIONAL MATCH (period)-[:START_EDGE]->(start_event:Event)
OPTIONAL MATCH (period)-[:END_EDGE]->(end_event:Event)
RETURN period.label, start_event.label, end_event.label
```

---

### **7.7.9 Attribution & Citation Relationships (11 types)**

| Relationship Type | Directionality | Description |
|-------------------|----------------|-------------|
| **EXTRACTED_FROM** | forward | Claim extracted from source work |
| **DESCRIBES** | forward | Citation describes entity/event |
| **MENTIONS** | forward | Citation mentions entity |
| **ANALYZES** | forward | Citation provides analysis of entity |
| **INTERPRETS** | forward | Citation interprets entity/event |
| **SUMMARIZES** | forward | Citation summarizes entity/event |
| **QUOTES** | forward | Citation is direct quote from source |
| **ATTRIBUTED_TO** | forward | Citation attributed to author |

**Example Cypher:**
```cypher
// Find all sources describing Caesar's death
MATCH (work:Work)-[:DESCRIBES]->(event:Event {label: "Death of Caesar"})
RETURN work.title, work.author_name, work.composition_date

// Citation network for specific claim
MATCH (claim:Claim)-[:EXTRACTED_FROM]->(passage:Passage)
      -[:PART_OF]->(work:Work)
      -[:ATTRIBUTED_TO]->(author:Human)
RETURN author.name, work.title, passage.citation, claim.confidence

// Most frequently cited works
MATCH (work:Work)<-[:EXTRACTED_FROM]-(claim:Claim)
RETURN work.title, COUNT(claim) AS citation_count
ORDER BY citation_count DESC
LIMIT 10
```

---

## **7.8 Relationship Constraints & Validation**

### **Neo4j Schema Constraints**

```cypher
// Ensure relationship types exist in canonical registry
CREATE CONSTRAINT relationship_type_exists
FOR ()-[r]-()
REQUIRE r.relationship_type IN [list of canonical types]

// Require triple alignment metadata on all relationships
CREATE CONSTRAINT relationship_has_alignment
FOR ()-[r]-()
REQUIRE r.relationship_type IS NOT NULL

// Index for relationship type lookups
CREATE INDEX relationship_type_index
FOR ()-[r]-()
ON (r.relationship_type)

// Index for action structure queries
CREATE INDEX action_structure_index
FOR ()-[r]-()
ON (r.goal_type, r.action_type, r.result_type)
```

### **Validation Rules**

**1. Relationship Type Existence**
- All relationships MUST use canonical relationship types from registry
- Agent output validation checks against canonical list
- Unknown types flagged for review

**2. Directionality Compliance**
- Forward relationships: Source â†’ Target  
- Inverse relationships: Target â† Source
- Symmetric relationships: Both directions created
- Unidirectional: Only specified direction allowed

**3. Domain/Range Constraints (Selected)**
```cypher
// BORN_IN: Human â†’ Place
MATCH (h:Human)-[:BORN_IN]->(p)
WHERE NOT p:Place
RETURN "Invalid BORN_IN target" AS error, h.entity_id, id(p)

// AUTHOR: Human â†’ Work
MATCH (h:Human)-[:AUTHOR]->(w)
WHERE NOT w:Work
RETURN "Invalid AUTHOR target" AS error, h.entity_id, id(w)

// FATHER_OF: Human â†’ Human  
MATCH (h1:Human)-[:FATHER_OF]->(h2)
WHERE NOT h2:Human
RETURN "Invalid FATHER_OF target" AS error, h1.entity_id, id(h2)
```

**4. Triple Alignment Completeness**
- Wikidata property stored when alignment exists
- CIDOC-CRM property stored when alignment exists
- NULL allowed for Chrystallum-specific relationships

---

## **7.9 Cypher Query Patterns**

### **Pattern 1: Entity-Centric Relationship Discovery**

```cypher
// Find all relationships for specific entity
MATCH (entity {entity_id: $entity_id})-[r]->(related)
RETURN type(r) AS relationship_type, 
       labels(related) AS related_entity_types,
       related.name AS related_name,
       r.goal_type AS goal,
       r.result_type AS result
```

### **Pattern 2: Relationship Type Filtering**

```cypher
// Find all military relationships
MATCH (e1)-[r]->(e2)
WHERE r.relationship_type IN [
  "FOUGHT_IN", "DEFEATED", "COMMANDED_BY", 
  "BESIEGED", "CONQUERED"
]
RETURN e1.name, type(r), e2.name
```

### **Pattern 3: Action Structure Analysis**

```cypher
// Find relationships with specific goal-action-result pattern
MATCH (entity1)-[r]->(entity2)
WHERE r.goal_type = "POLITICAL"
  AND r.action_type = "MILITARY_ACTION"
  AND r.result_type = "POLITICAL_TRANSFORMATION"
RETURN entity1.name, 
       r.goal_description,
       r.action_description, 
       r.result_description,
       entity2.name
```

### **Pattern 4: Triple Alignment Queries**

```cypher
// Query using Wikidata property
MATCH (e1)-[r]->(e2)
WHERE r.wikidata_property = "P607"  // P607 = conflict
RETURN e1.name, e2.label, r.relationship_type

// Query using CIDOC-CRM property
MATCH (e1)-[r]->(e2)
WHERE r.cidoc_crm_property = "P11_had_participant"
RETURN e1.name, e2.label, r.cidoc_crm_class
```

### **Pattern 5: Multi-Hop Traversal**

```cypher
// Find indirect connections (3 degrees)
MATCH path = (caesar:Human {name: "Caesar"})
             -[*1..3]-(connected)
WHERE connected:Human OR connected:Organization
RETURN connected.name, 
       length(path) AS degrees_of_separation,
       [r IN relationships(path) | type(r)] AS relationship_chain
ORDER BY degrees_of_separation
LIMIT 20
```

### **Pattern 6: Hierarchical Relationship Queries**

```cypher
// Find all specific types under generic MILITARY_ACTION
MATCH (e1)-[r]->(e2)
WHERE r.parent_relationship = "MILITARY_ACTION"
   OR r.relationship_type = "MILITARY_ACTION"
RETURN DISTINCT r.relationship_type, COUNT(*) AS usage_count
ORDER BY usage_count DESC
```

---

## **7.10 Relationship Evolution & Versioning**

### **Lifecycle States**

| Status | Description | Agent Behavior |
|--------|-------------|----------------|
| **candidate** | Proposed relationship type, under review | Agents flag but don't use |
| **active** | Production-ready, validated | Agents use freely |
| **deprecated** | Superseded by newer type | Agents create warnings, suggest replacement |

### **Version Tracking**

```cypher
(:RelationshipType {
  relationship_type: "FOUGHT_IN",
  version: "1.0",
  created_date: "2025-12-01",
  last_modified: "2026-01-15",
  change_log: [
    "1.0: Initial implementation",
    "1.1: Added action structure properties"
  ]
})
```

### **Deprecation Pattern**

```cypher
// Old relationship type deprecated
(:RelationshipType {
  relationship_type: "PARTICIPATED_IN_BATTLE",
  status: "deprecated",
  lifecycle_status: "deprecated",
  deprecated_date: "2026-01-15",
  superseded_by: "FOUGHT_IN",
  deprecation_reason: "Merged into FOUGHT_IN for consistency"
})

// New relationship type active
(:RelationshipType {
  relationship_type: "FOUGHT_IN",
  status: "active",
  replaces: ["PARTICIPATED_IN_BATTLE", "ENGAGED_IN_COMBAT"]
})
```

### **Migration Strategy**

When deprecating relationship types:
1. Mark old type as `deprecated` (don't delete)
2. Create `superseded_by` link to replacement type
3. Add agent validation warnings
4. Provide migration Cypher query
5. Preserve old relationships for historical research

```cypher
// Migration query example
MATCH (e1)-[old:PARTICIPATED_IN_BATTLE]->(e2)
CREATE (e1)-[new:FOUGHT_IN]->(e2)
SET new = properties(old)
SET new.relationship_type = "FOUGHT_IN"
SET new.migrated_from = "PARTICIPATED_IN_BATTLE"
SET new.migration_date = datetime()
// Optionally delete old relationship after verification
```

---

# **PART III: IMPLEMENTATION & TECHNOLOGY**

---

# **8. Technology Stack & Orchestration**

## **8.0 Implementation Overview**

This section describes Chrystallum's technical implementation: the runtime environment, technology choices, orchestration patterns, and critical operational guidelines for safe system behavior.

**Key Components:**
- **Neo4j 4.x+**: Property graph database with APOC extensions
- **LangGraph**: Multi-agent orchestration framework (Python-based)
- **Python 3.11+**: Implementation language
- **LLM Integration**: OpenAI/Anthropic for extraction phase
- **Frontend**: React + Cytoscape.js for graph visualization

**Implementation Philosophy:**
- **Two-stage architecture**: LLM extraction â†’ deterministic validation (Section 1.2.1)
- **Evidence-aware**: Complete provenance chains for all knowledge
- **Safety-first**: Explicit identifier handling rules prevent data corruption

---

## **8.1 Core Technology Stack**

### **8.1.1 Neo4j Property Graph Database**

**Version:** Neo4j 4.x or later (5.x recommended)

**Required Extensions:**
- **APOC**: Utilities for graph algorithms, data integration, and schema operations
- **GDS (Graph Data Science)**: For network analysis and similarity computations (optional)

**Key Features Used:**
- Property graphs with typed relationships
- Cypher query language
- Multi-property indexes
- Full-text search
- Uniqueness constraints
- Temporal properties (ISO 8601 dates)

**Performance Considerations:**
- Index all frequently queried properties (qid, entity_id, fast_id, lcc_code)
- Use relationship direction intentionally (BROADER_THAN only, not NARROWER_THAN)
- Batch writes for bulk operations (use APOC batch functions)

**Connection Details:**
```python
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
```

---

### **8.1.2 LangGraph Multi-Agent Orchestration**

**Purpose:** Coordinate multiple specialized agents for collaborative knowledge construction.

**Architecture Pattern:**
```
User Query â†’ CoordinatorAgent â†’ SubjectAgent â†’ EntityAgent â†’ Neo4j Write
                â†“                    â†“              â†“
           Route by LCC      Extract entities  Validate/Resolve
```

**Core LangGraph Concepts:**
- **Nodes**: Individual agents (SubjectAgent, EntityAgent, CoordinatorAgent)
- **Edges**: Communication channels between agents
- **State**: Shared context across agent invocations
- **Conditional Edges**: Routing logic based on state

**Example LangGraph Workflow:**
```python
from langgraph.graph import StateGraph, END

# Define workflow graph
workflow = StateGraph()

# Add agent nodes
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("subject_agent", subject_agent)
workflow.add_node("entity_agent", entity_agent)
workflow.add_node("neo4j_writer", neo4j_writer)

# Add edges
workflow.add_edge("coordinator", "subject_agent")
workflow.add_edge("subject_agent", "entity_agent")
workflow.add_edge("entity_agent", "neo4j_writer")
workflow.add_edge("neo4j_writer", END)

# Set entry point
workflow.set_entry_point("coordinator")

# Compile workflow
app = workflow.compile()
```

---

### **8.1.3 Python Implementation Environment**

**Version:** Python 3.11 or later

**Required Libraries:**
```python
# Core dependencies
neo4j>=5.0.0              # Neo4j driver
langgraph>=0.0.20         # Multi-agent orchestration
langchain>=0.1.0          # LLM integration
openai>=1.0.0             # OpenAI API (or anthropic for Claude)

# Data processing
pandas>=2.0.0             # CSV/data manipulation
pydantic>=2.0.0           # Data validation

# Utilities
python-dotenv>=1.0.0      # Environment variables
loguru>=0.7.0             # Logging

# Optional
requests>=2.31.0          # HTTP requests (Wikidata API)
spacy>=3.7.0              # NLP (if needed for extraction enhancement)
```

**Virtual Environment Setup:**
```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # Unix/macOS
.venv\\Scripts\\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## **8.2 LangGraph Workflow Architecture**

### **8.2.1 Agent Definitions**

**CoordinatorAgent:**
- **Purpose**: Routes queries to appropriate subject domain agents
- **Inputs**: User query, extracted entities/relationships
- **Outputs**: Routing decision (LCC code determination)
- **LLM Role**: Classify query into LCC domain

**SubjectAgent:**
- **Purpose**: Extract subject-specific knowledge from sources
- **Inputs**: Source text, domain context (LCC subdivision)
- **Outputs**: Structured entity/relationship proposals
- **LLM Role**: Extract entities, dates, relationships from unstructured text

**EntityAgent:**
- **Purpose**: Validate and resolve entities to canonical identifiers
- **Inputs**: Proposed entities from SubjectAgent
- **Outputs**: Validated entities with QIDs, authority IDs
- **LLM Role**: None (tool-based resolution only - Wikidata API, FAST lookup)

**ReasoningAgent** (optional):
- **Purpose**: Validate logical consistency of proposed claims
- **Inputs**: Claim structure, supporting evidence
- **Outputs**: Validation result, confidence score
- **LLM Role**: None (deterministic reasoning rules)

---

### **8.2.2 State Management**

**Shared State Structure:**
```python
from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    query: str                          # Original user query
    lcc_code: Optional[str]             # Classified LCC domain
    subject_concept_id: Optional[str]   # SubjectConcept node ID
    
    # Extracted entities (from SubjectAgent)
    proposed_entities: List[Dict]       # [{label, type, properties}, ...]
    proposed_relationships: List[Dict]  # [{from, to, type, properties}, ...]
    
    # Validated entities (from EntityAgent)
    validated_entities: List[Dict]      # [{label, qid, fast_id, ...}, ...]
    
    # Claims (from ReasoningAgent)
    claims: List[Dict]                  # [{claim_id, text, confidence}, ...]
    
    # Metadata
    agent_history: List[str]            # Agent execution trace
    errors: List[str]                   # Error messages
```

---

### **8.2.3 Agent Communication Pattern**

```python
def coordinator_agent(state: AgentState) -> AgentState:
    """Route query to appropriate subject domain."""
    query = state["query"]
    
    # LLM classifies query into LCC domain
    lcc_code = classify_query_to_lcc(query)
    
    # Update state
    state["lcc_code"] = lcc_code
    state["agent_history"].append("coordinator: classified to " + lcc_code)
    
    return state

def subject_agent(state: AgentState) -> AgentState:
    """Extract entities and relationships from source text."""
    lcc_code = state["lcc_code"]
    query = state["query"]
    
    # LLM extracts structured data
    extractions = extract_entities_and_relationships(query, lcc_code)
    
    # Update state
    state["proposed_entities"] = extractions["entities"]
    state["proposed_relationships"] = extractions["relationships"]
    state["agent_history"].append(f"subject_agent: extracted {len(extractions['entities'])} entities")
    
    return state

def entity_agent(state: AgentState) -> AgentState:
    """Validate and resolve entities to canonical identifiers."""
    proposed = state["proposed_entities"]
    validated = []
    
    for entity in proposed:
        # Tool-based resolution (NO LLM)
        qid = wikidata_lookup(entity["label"])
        fast_id = fast_lookup(entity["label"], entity["type"])
        
        validated.append({
            **entity,
            "qid": qid,
            "fast_id": fast_id,
            "validated": True
        })
    
    # Update state
    state["validated_entities"] = validated
    state["agent_history"].append(f"entity_agent: validated {len(validated)} entities")
    
    return state
```

---

## **8.3 Multi-Agent Coordination Patterns**

### **8.3.1 Sequential Processing**

**Pattern**: Execute agents in order (coordinator â†’ subject â†’ entity â†’ writer)

**Use Case**: Standard entity extraction and resolution

```python
workflow.add_edge("coordinator", "subject_agent")
workflow.add_edge("subject_agent", "entity_agent")
workflow.add_edge("entity_agent", "neo4j_writer")
```

---

### **8.3.2 Conditional Routing**

**Pattern**: Route to different agents based on state

**Use Case**: Route to specialist agents based on LCC classification

```python
def route_by_lcc(state: AgentState) -> str:
    """Route to specialist agent based on LCC code."""
    lcc = state["lcc_code"]
    
    if lcc.startswith("D"):  # History
        return "history_specialist"
    elif lcc.startswith("J"):  # Political science
        return "political_specialist"
    elif lcc.startswith("N"):  # Fine arts
        return "art_specialist"
    else:
        return "general_agent"

# Add conditional edge
workflow.add_conditional_edges(
    "coordinator",
    route_by_lcc,
    {
        "history_specialist": "history_agent",
        "political_specialist": "political_agent",
        "art_specialist": "art_agent",
        "general_agent": "subject_agent"
    }
)
```

---

### **8.3.3 Parallel Processing**

**Pattern**: Execute multiple agents simultaneously

**Use Case**: Validate entity and check for duplicates in parallel

```python
workflow.add_edge("subject_agent", ["entity_validator", "duplicate_checker"])
workflow.add_edge(["entity_validator", "duplicate_checker"], "merge_results")
```

---

### **8.3.4 Feedback Loops**

**Pattern**: Agent can route back to earlier stage

**Use Case**: Entity resolution fails â†’ request more context from subject agent

```python
def check_validation_status(state: AgentState) -> str:
    """Check if entities validated successfully."""
    if state.get("errors"):
        return "request_more_context"
    else:
        return "proceed_to_writer"

workflow.add_conditional_edges(
    "entity_agent",
    check_validation_status,
    {
        "request_more_context": "subject_agent",  # Loop back
        "proceed_to_writer": "neo4j_writer"       # Continue
    }
)
```

---

## **8.4 LLM Integration Patterns**

### **8.4.1 Extraction Phase (LLM-Powered)**

**Purpose**: Extract structured data from unstructured text

**LLM Role**: Natural language understanding, entity recognition, relationship extraction

**Example:**
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def extract_entities_and_relationships(text: str, domain: str) -> Dict:
    """Extract structured data from text using LLM."""
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a historical research assistant. Extract entities and relationships from the provided text."),
        ("user", f"Domain: {domain}\\n\\nText: {text}\\n\\nExtract: 1) People (name, role), 2) Places (name, type), 3) Events (name, date), 4) Relationships (who did what to whom)")
    ])
    
    response = llm.invoke(prompt.format_messages())
    
    # Parse LLM response into structured format
    parsed = parse_llm_extraction(response.content)
    
    return parsed
```

**âš ï¸ CRITICAL**: Never pass system identifiers (QIDs, FAST IDs, LCC codes) to LLM. See Section 8.5.

---

### **8.4.2 Resolution Phase (Tool-Based, NO LLM)**

**Purpose**: Resolve entity labels to canonical identifiers

**LLM Role**: NONE - use deterministic API lookups

**Example:**
```python
def wikidata_lookup(entity_label: str) -> Optional[str]:
    """Resolve entity label to Wikidata QID using API (NO LLM)."""
    
    # Use Wikidata search API
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": entity_label,
        "language": "en",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    results = response.json().get("search", [])
    
    if results:
        return results[0]["id"]  # Return QID as atomic string
    else:
        return None

def fast_lookup(subject_label: str, subject_type: str) -> Optional[str]:
    """Resolve subject to FAST ID using lookup table (NO LLM)."""
    
    # Use FAST subject headings lookup (from CSV or API)
    fast_mapping = load_fast_mapping()  # Pre-loaded CSV
    
    key = (subject_label.lower(), subject_type)
    fast_id = fast_mapping.get(key)
    
    return fast_id  # Return as atomic string
```

**âš ï¸ CRITICAL**: These functions return **atomic strings** (QIDs, FAST IDs). Never pass these to LLMs. See Section 8.5.

---

### **8.4.3 LLM Degradation Handling**

**Issue**: LLM responses can degrade over time due to model updates, prompt changes, or service issues.

**Mitigation Strategies:**
1. **Version locking**: Pin LLM model versions in production
2. **Response validation**: Schema validation (Pydantic) on all LLM outputs
3. **Fallback mechanisms**: If LLM fails, route to human review queue
4. **Monitoring**: Track extraction accuracy over time, alert on degradation

**Reference**: See `md/CIDOC/Reference/LLM_Degradation.md` for detailed analysis

---

## **8.5 Identifier Handling & LLM Safety** ðŸ”´ **CRITICAL**

### **8.5.1 The Tokenization Problem**

**CRITICAL ISSUE**: System identifiers (FAST IDs, LCC codes, MARC codes, Pleiades IDs, Wikidata QIDs) **fragment when tokenized by LLMs**, causing silent data corruption.

**Example of Fragmentation:**
```python
# âŒ DANGER - Passing FAST ID to LLM:
fast_id = "1145002"  # Technology (7-digit atomic identifier)
llm_response = llm.ask(f"What subject is FAST ID {fast_id}?")

# LLM tokenizes the input:
#   Input: "What subject is FAST ID 1145002?"
#   Tokens: ["What", "subject", "is", "FAST", "ID", "114", "500", "2", "?"]
#                                                      ^^^^^^^^^^^^^^^^^^^
#                                                      âŒ FRAGMENTED!

# LLM cannot recognize "1145002" as a single identifier
# Lookup fails, backbone alignment breaks silently

# âŒ Similar fragmentation for other identifiers:
lcc_code = "DG241-269"  # Roman history
# Tokens: ["DG", "241", "-", "269"]  âŒ FRAGMENTED!

marc_code = "sh85115058"  # Subject heading
# Tokens: ["sh", "851", "150", "58"]  âŒ FRAGMENTED!

pleiades_id = "423025"  # Rome
# Tokens: ["423", "025"]  âŒ FRAGMENTED!

qid = "Q17193"  # Roman Republic
# Tokens: ["Q", "17", "19", "3"]  âŒ FRAGMENTED!
```

**Consequence**: If agents accidentally pass these identifiers to LLMs:
- FAST backbone alignment fails â†’ subject classification breaks
- Pleiades lookups fail â†’ ancient geography breaks
- MARC integration fails â†’ bibliographic links break
- QID lookups fail â†’ entity resolution breaks
- **Silent failures** - no obvious errors, just bad data

---

### **8.5.2 The Two-Stage Processing Pattern** âœ…

**CORRECT PATTERN**: LLM extracts natural language labels â†’ Tools resolve to atomic identifiers

```python
# âœ… CORRECT - Two-stage processing:

# Stage 1: LLM extracts natural language labels
text = "During the Roman Republic, Rome was the capital"
extracted = llm.extract({
    "period": "Roman Republic",    # âœ… Natural language (LLM can process)
    "place": "Rome"                 # âœ… Natural language (LLM can process)
})

# Stage 2: Tools resolve labels to atomic identifiers (NO LLM)
resolved = {
    "period": {
        "label": "Roman Republic",                      # âœ… Human-readable
        "qid": wikidata_tool.lookup("Roman Republic"),  # "Q17193" (atomic)
        "fast_id": fast_tool.lookup("Roman Republic")   # "1411640" (atomic)
    },
    "place": {
        "label": "Rome",                           # âœ… Human-readable
        "qid": wikidata_tool.lookup("Rome"),       # "Q220" (atomic)
        "pleiades_id": pleiades_tool.lookup("Rome") # "423025" (atomic)
    }
}

# Stage 3: Store both formats in Neo4j
graph.create_node({
    "label": "Roman Republic",      # âœ… Natural (for display, search)
    "qid": "Q17193",                # âŒ Atomic (for lookups, NEVER pass to LLM)
    "fast_id": "1411640"            # âŒ Atomic (for backbone, NEVER pass to LLM)
})
```

---

### **8.5.3 Identifier Atomicity Rules**

**Golden Rule**: **NEVER pass atomic identifiers to LLMs for interpretation.**

| Identifier Type | Example | LLM Safe? | How to Handle | Tokenization Risk |
|-----------------|---------|-----------|---------------|-------------------|
| **Period name** | "Roman Republic" | âœ… YES | Extract with LLM | âœ… None (designed for it) |
| **Date text** | "49 BCE" | âœ… YES | Extract with LLM, convert with tool | âœ… None |
| **Place name** | "Rome" | âœ… YES | Extract with LLM | âœ… None |
| **Subject heading** | "Political science" | âœ… YES | Extract with LLM | âœ… None |
| | | | | |
| **Wikidata QID** | **"Q17193"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **FAST ID** | **"1145002"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **LCC code (range)** | **"DG241-269"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **LCC code (simple)** | **"T"** | **âŒ NO** | **Tool lookup only** | ðŸŸ¡ **MEDIUM** |
| **MARC code** | **"sh85115058"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **Pleiades ID** | **"423025"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **GeoNames ID** | **"2643743"** | **âŒ NO** | **Tool lookup only** | ðŸŸ¡ **MEDIUM** |
| **ISO 8601 date** | **"-0753-01-01"** | **âŒ NO** | **Tool-formatted only** | ðŸ”´ **HIGH** |

---

### **8.5.4 Implementation Patterns**

#### **Pattern 1: Entity Extraction (Correct)**

```python
def extract_and_resolve_entities(source_text: str) -> List[Dict]:
    """Extract entities from text and resolve to canonical identifiers."""
    
    # Stage 1: LLM extracts natural language
    llm_prompt = f"""
    Extract historical entities from this text. For each entity, provide:
    - label: The entity's name (e.g., "Julius Caesar", "Rome")
    - type: Entity type (Person, Place, Event, etc.)
    
    Text: {source_text}
    
    Return JSON list of entities.
    """
    
    # âœ… GOOD: LLM processes natural language only
    raw_entities = llm.extract(llm_prompt)
    
    # Stage 2: Tools resolve to atomic identifiers (NO LLM)
    resolved_entities = []
    for entity in raw_entities:
        label = entity["label"]      # âœ… Natural language string
        entity_type = entity["type"]
        
        # âœ… GOOD: Tool-based resolution (NO LLM involved)
        qid = wikidata_api.search(label, entity_type)  # Returns atomic string
        fast_id = fast_api.lookup(label, entity_type)  # Returns atomic string
        
        resolved_entities.append({
            "label": label,           # âœ… Natural (human-readable)
            "qid": qid,               # âŒ Atomic (machine lookup key)
            "fast_id": fast_id,       # âŒ Atomic (machine lookup key)
            "entity_type": entity_type
        })
    
    return resolved_entities
```

#### **Pattern 2: Subject Classification (Correct)**

```python
def classify_query_to_lcc(query: str) -> str:
    """Classify user query into LCC domain using LLM."""
    
    # LLM classifies using NATURAL LANGUAGE descriptions
    llm_prompt = f"""
    Classify this query into a Library of Congress Classification domain.
    
    Query: {query}
    
    Choose from (PROVIDE DESCRIPTIONS, NOT CODES):
    - History: Events, people, civilizations, wars
    - Political Science: Governance, institutions, law
    - Fine Arts: Painting, sculpture, architecture
    - Philosophy: Ethics, logic, metaphysics
    - Literature: Poetry, novels, drama
    
    Return: The domain NAME (not the code).
    """
    
    # âœ… GOOD: LLM processes natural language domain names
    domain_name = llm.extract(llm_prompt)  # Returns "History", not "D"
    
    # Tool converts name to LCC code (NO LLM)
    lcc_code = lcc_mapping[domain_name]    # "History" â†’ "D"
    
    return lcc_code  # Returns atomic string "D" (NEVER pass back to LLM)
```

#### **Pattern 3: Backbone Alignment (Correct)**

```python
def align_entity_to_backbone(entity_label: str, entity_type: str) -> Dict:
    """Align entity to FAST/LCC/LCSH backbone standards."""
    
    # âœ… GOOD: All lookups use natural language labels, not codes
    fast_id = fast_api.lookup(entity_label, entity_type)
    lcc_code = lcc_api.classify(entity_label, entity_type)
    lcsh_heading = lcsh_api.lookup(entity_label)
    marc_code = marc_api.lookup(entity_label)
    
    # Return atomic identifiers (NEVER pass these to LLM)
    return {
        "fast_id": fast_id,        # "1145002" - atomic string
        "lcc_code": lcc_code,      # "DG241-269" - atomic string
        "lcsh_heading": lcsh_heading,  # "Rome--History--Republic" - natural language (OK)
        "marc_code": marc_code     # "sh85115058" - atomic string
    }
```

---

### **8.5.5 Validation Checklist**

**Before sending ANY text to an LLM, verify:**

- [ ] No QIDs (Q followed by digits)
- [ ] No FAST IDs (7-digit numbers)
- [ ] No LCC codes (letters + numbers with ranges like "DG241-269")
- [ ] No MARC codes (sh + 8 digits)
- [ ] No Pleiades IDs (6-digit numbers in geographic context)
- [ ] No GeoNames IDs (5-8 digit numbers in geographic context)
- [ ] No ISO dates (YYYY-MM-DD format, especially with negative years)
- [ ] No dates without delimiters (YYYYMMDD)

**If any detected â†’ Remove from prompt and use tool lookup instead!**

---

### **8.5.6 Validation Implementation**

```python
import re
from typing import List, Dict

class IdentifierValidator:
    """Validate prompts for atomic identifiers before LLM calls."""
    
    PATTERNS = {
        "qid": r"\\bQ\\d+\\b",                          # Q17193
        "fast_id": r"\\b\\d{7}\\b",                     # 1145002
        "lcc_range": r"\\b[A-Z]{1,2}\\d+[-]\\d+\\b",   # DG241-269
        "marc": r"\\bsh\\d{8}\\b",                      # sh85115058
        "pleiades": r"\\b\\d{6}\\b",                    # 423025
        "iso_date": r"-?\\d{4}-\\d{2}-\\d{2}",         # -0509-01-01
    }
    
    def check_prompt(self, prompt: str) -> Dict:
        """Check prompt for atomic identifiers."""
        issues = []
        
        for id_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, prompt)
            if matches:
                issues.append({
                    "type": id_type,
                    "matches": matches,
                    "risk": "HIGH",
                    "message": f"Found {id_type} in prompt: {matches}. Remove before LLM call."
                })
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues,
            "summary": f"Found {len(issues)} identifier safety issues" if issues else "Prompt is safe"
        }

# Usage example
validator = IdentifierValidator()

# Before LLM call:
prompt = "Tell me about Q17193"
result = validator.check_prompt(prompt)

if not result['is_safe']:
    raise ValueError(f"Prompt contains atomic identifiers: {result['summary']}")
    # Or: Clean prompt and use tool lookup instead
```

---

### **8.5.7 Storage Format Examples**

#### **Period Entity (With Both Formats)**

```json
{
  "label": "Roman Republic",           // âœ… Natural (LLM extracts)
  "qid": "Q17193",                     // âŒ Atomic (tool resolves)
  "fast_id": "1411640",                // âŒ Atomic (tool resolves)
  "lcc_code": "DG241-269",             // âŒ Atomic (tool resolves)
  "lcsh_heading": "Rome--History--Republic",  // âœ… Natural (human-readable)
  "marc_code": "sh85115058",           // âŒ Atomic (tool resolves)
  "start_date_text": "509 BCE",        // âœ… Natural (LLM extracts)
  "start_date_iso": "-0509-01-01",    // âŒ Atomic (tool formats)
  "start_year": -509                   // âœ… Numeric (calculations)
}
```

#### **Place Entity (With Both Formats)**

```json
{
  "label": "Rome",                     // âœ… Natural (LLM extracts)
  "qid": "Q220",                       // âŒ Atomic (tool resolves)
  "pleiades_id": "423025",             // âŒ Atomic (tool resolves)
  "geonames_id": "3169070",            // âŒ Atomic (tool resolves)
  "latitude": 41.9028,                 // âœ… Numeric (not string!)
  "longitude": 12.4964,                // âœ… Numeric (not string!)
  "description": "Capital of the Roman Empire"  // âœ… Natural (LLM extracts)
}
```

---

### **8.5.8 Common Anti-Patterns (AVOID)**

#### **âŒ Anti-Pattern 1: Passing QID to LLM**

```python
# âŒ WRONG - QID gets tokenized and fragmented
qid = "Q17193"
llm_response = llm.ask(f"What period is {qid}?")
# Tokens: ["What", "period", "is", "Q", "17", "19", "3", "?"]
# Result: LLM doesn't recognize QID, gives garbage response

# âœ… CORRECT - Use tool lookup
qid = "Q17193"
wikidata_data = wikidata_api.get_entity(qid)  # Tool-based, no LLM
period_label = wikidata_data["labels"]["en"]["value"]
```

#### **âŒ Anti-Pattern 2: Asking LLM to Generate FAST IDs**

```python
# âŒ WRONG - LLM cannot generate valid FAST IDs
subject_text = "political science"
llm_response = llm.ask(f"What is the FAST ID for {subject_text}?")
# LLM might hallucinate: "1145002" (could be wrong)

# âœ… CORRECT - Use FAST API or lookup table
fast_id = fast_api.lookup(subject_text)  # Authoritative source
```

#### **âŒ Anti-Pattern 3: Constructing LLM Prompts with Identifiers**

```python
# âŒ WRONG - Identifier in prompt gets tokenized
fast_id = "1145002"
lcc_code = "DG241-269"
llm_prompt = f"Classify this entity with FAST ID {fast_id} and LCC code {lcc_code}"
# Tokenization breaks both identifiers

# âœ… CORRECT - Use labels in prompts, identifiers for lookups
label = "Roman history"
llm_prompt = f"Classify this entity about {label}"
# After LLM response, use tools to get FAST/LCC
```

---

### **8.5.9 Emergency Decision Tree**

Is this data being processed?  
â”‚  
â”œâ”€ Natural language text? (period name, date text, place name)  
â”‚  â””â”€ âœ… LLM can extract it  
â”‚  
â”œâ”€ System identifier? (QID, FAST ID, LCC, MARC, Pleiades, GeoNames)  
â”‚  â””â”€ âŒ Tool resolves it, NEVER pass to LLM  
â”‚  
â”œâ”€ ISO 8601 date?  
â”‚  â””â”€ âŒ Tool formats it, NEVER pass to LLM  
â”‚  
â”œâ”€ Numeric value? (year, coordinate)  
â”‚  â””â”€ âœ… Store as number, use in calculations  
â”‚  
â””â”€ Unsure?  
   â””â”€ Default to âŒ Tool handling (safer to over-protect)

---

### **8.5.10 Summary: Identifier Safety Rules**

| âœ… LLM Can Process | âŒ LLM Cannot Process (Atomic) |
|-------------------|--------------------------------|
| Period names | Wikidata QIDs |
| Place names | FAST IDs |
| Date text (BCE/CE) | LCC codes |
| Subject headings (LCSH) | MARC codes |
| Descriptions | Pleiades IDs |
| Natural language | GeoNames IDs |
| | ISO 8601 dates |

**Remember:** When in doubt, use tools! It's always safer to over-protect identifiers than risk tokenization.

**For complete reference, see:** Appendix M (Identifier Safety Reference)

---

## **8.6 Federation Dispatcher and Backlink Control Plane**

All Wikidata statement ingestion MUST use a deterministic dispatcher keyed by:
- `mainsnak.datatype`
- `mainsnak.datavalue.type` (`value_type`)

This control plane separates topology, federation identity, and literal attributes.
No statement may bypass dispatcher routing.

### **8.6.1 Dispatcher Route Matrix (Normative)**

| Pair (`datatype + value_type`) | Route | Required Action |
|---|---|---|
| `wikibase-item + wikibase-entityid` | `edge_candidate` | Candidate graph edge write (subject to schema/class checks) |
| `external-id + string` | `federation_id` | Store namespaced external ID and run dedupe/merge check |
| `time + time` with precision >= threshold | `temporal_anchor` | Parse and anchor to temporal backbone |
| `time + time` with precision < threshold | `temporal_uncertain` | Route to uncertain bucket, do not treat as precise anchor |
| `string + string`, `monolingualtext + monolingualtext`, `url + string` | `node_property` | Store as literal/content attributes |
| `quantity + quantity` | `measured_attribute` | Store normalized numeric payload |
| `globe-coordinate + globecoordinate` | `geo_attribute` | Route to geographic handler |
| `commonsMedia + string` | `media_reference` | Store media reference metadata |
| missing `datavalue` | `quarantine_missing_datavalue` | Quarantine with reason |
| unsupported pair | `quarantine_unsupported_pair` | Quarantine with reason |

### **8.6.2 Temporal Precision Gate**

Use Wikidata precision codes:
- `9` year
- `10` month
- `11` day

Default policy:
- minimum precision for `temporal_anchor` is `9` (year)
- lower precision routes to `temporal_uncertain`

No temporal statement is silently dropped.

### **8.6.3 Class Controls and Backlink Admission**

For reverse-link expansion:
1. Start from reverse triples `?source ?property ?target`.
2. Resolve source classes via `P31`.
3. Expand class lineage via bounded `P279` walk.
4. Admit only schema-allowlisted classes.
5. Optionally reject explicit denylisted classes (`P31` denylist).

### **8.6.4 Frontier Eligibility Guard (Anti-Hairball Rule)**

Accepted nodes can still be excluded from traversal frontier.

Default exclusion rules:
- `edge_candidate_count == 0` -> exclude (`no_edge_candidates`)
- `literal_heavy_ratio > 0.80` -> exclude (`literal_heavy`)

These exclusions affect recursion and frontier growth, not node retention.

### **8.6.5 Provenance and Safety Requirements**

Every materialized backlink edge MUST include:
- `source_system`
- `source_mode`
- `source_property`
- `retrieved_at`

Every run report MUST emit:
- route counts
- quarantine reason counts
- unsupported pair rate
- unresolved class rate
- frontier eligible/excluded counts

Silent drops are prohibited.

### **8.6.6 Operational Reference**

Canonical tooling:
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`
- `JSON/wikidata/backlinks/README.md`

Operational contract details are defined in Appendix K.4 through K.6.

---

# **9. Workflows & Agent Coordination**

## **9.0 Workflow Overview**

This section describes the operational workflows that govern how agents collaborate to construct, validate, and promote knowledge in Chrystallum.

**Core Workflows:**
1. **Claim Generation**: Extract claims from source texts
2. **Claim Review**: Multi-agent validation of claims
3. **Consensus Building**: Resolve conflicting claims from multiple agents
4. **Claim Promotion**: Convert validated claims to canonical graph

**Workflow Properties:**
- **Asynchronous**: Agents operate concurrently on different tasks
- **Event-driven**: State changes trigger agent actions
- **Auditable**: Complete provenance trail for all operations
- **Idempotent**: Safe to re-run workflows without duplication

---

## **9.1 Claim Generation Workflow**

### **9.1.1 Workflow Steps**

```
Source Text â†’ SubjectAgent â†’ EntityAgent â†’ ClaimAgent â†’ Neo4j (Claim nodes)
                  â†“              â†“             â†“
            (Extract)      (Validate)    (Structure)
```

**Step 1: Extract Entities and Relationships (SubjectAgent)**
- **Input**: Source text (e.g., paragraph from Plutarch)
- **LLM Role**: Extract entities, dates, relationships from natural language
- **Output**: Proposed entities and relationships (labels only, no identifiers yet)

**Step 2: Validate and Resolve (EntityAgent)**
- **Input**: Proposed entities from Step 1
- **Tool Role**: Resolve labels to QIDs, FAST IDs, check for existing entities
- **Output**: Validated entities with canonical identifiers

**Step 3: Structure Claims (ClaimAgent)**
- **Input**: Validated entities and relationships
- **Tool Role**: Create Claim nodes with provenance properties
- **Output**: Structured claims with cipher (content-addressable hash)

**Step 4: Write to Neo4j**
- **Input**: Structured claims
- **Output**: Claim nodes, ProposedEdge nodes, ReasoningTrace nodes

---

### **9.1.2 Implementation Example**

```python
from typing import Dict, List

def claim_generation_workflow(source_text: str, source_work_qid: str, agent_id: str) -> Dict:
    """Generate claims from source text."""
    
    # Step 1: Extract entities and relationships (LLM)
    raw_extractions = subject_agent.extract(source_text)
    # Returns: {entities: [{label, type}, ...], relationships: [{from, to, type}, ...]}
    
    # Step 2: Validate and resolve (Tools, NO LLM)
    validated_entities = entity_agent.validate(raw_extractions["entities"])
    # Returns: [{label, qid, fast_id, entity_type}, ...]
    
    # Step 3: Structure claims
    claims = []
    for rel in raw_extractions["relationships"]:
        # Build claim structure
        claim = {
            "claim_text": f"{rel['from']} {rel['type']} {rel['to']}",
            "subject_entity_qid": find_qid(rel["from"], validated_entities),
            "object_entity_qid": find_qid(rel["to"], validated_entities),
            "relationship_type": rel["type"],
            "source_work_qid": source_work_qid,
            "source_agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "status": "proposed",  # Awaiting review
            "confidence": 0.7  # Initial confidence
        }
        
        # Generate content-addressable cipher
        claim["cipher"] = generate_cipher(claim)
        
        claims.append(claim)
    
    # Step 4: Write to Neo4j
    for claim in claims:
        neo4j_writer.create_claim(claim)
        
        # Create ProposedEdge for relationship
        neo4j_writer.create_proposed_edge(
            edge_type=claim["relationship_type"],
            from_qid=claim["subject_entity_qid"],
            to_qid=claim["object_entity_qid"],
            claim_id=claim["cipher"]
        )
        
        # Create ReasoningTrace for explainability
        neo4j_writer.create_reasoning_trace(
            agent_id=agent_id,
            claim_id=claim["cipher"],
            source_text=source_text,
            reasoning_steps=[
                "Extracted entities from source",
                "Resolved to Wikidata QIDs",
                "Structured as relationship claim"
            ]
        )
    
    return {
        "claims_generated": len(claims),
        "ciphers": [c["cipher"] for c in claims]
    }
```

---

## **9.2 Claim Review Workflow**

### **9.2.1 Workflow Steps**

```
Claim (proposed) â†’ ReviewerAgent â†’ Review Node â†’ Consensus Calculation â†’ Status Update
                       â†“               â†“                â†“
                  (Evaluate)      (Record)        (Aggregate)
```

**Step 1: Select Claims for Review**
- Query Neo4j for claims with `status="proposed"` and insufficient reviews (< 3)

**Step 2: Agent Review (ReviewerAgent)**
- **Input**: Claim structure, source text, existing evidence
- **LLM Role** (optional): Evaluate claim plausibility, check for fallacies
- **Tool Role**: Check against existing knowledge, verify sources
- **Output**: Review verdict (support/challenge/uncertain), confidence, reasoning

**Step 3: Record Review**
- Create Review node linked to Claim
- Record verdict, confidence, fallacies detected, reasoning summary

**Step 4: Calculate Consensus**
- Aggregate all reviews for this claim
- Calculate consensus score (weighted Bayesian average)
- Update claim status based on thresholds

**Step 5: Update Claim Status**
- `validated` (consensus â‰¥ 0.8 + 70% support)
- `disputed` (consensus â‰¥ 0.5 but mixed reviews)
- `rejected` (consensus < 0.5)

---

### **9.2.2 Implementation Example**

```python
def claim_review_workflow(claim_id: str, reviewer_agent_id: str) -> Dict:
    """Review existing claim and update consensus."""
    
    # Step 1: Retrieve claim from Neo4j
    claim = neo4j_reader.get_claim(claim_id)
    
    if not claim:
        return {"error": "Claim not found"}
    
    # Step 2: Agent evaluates claim
    review_result = reviewer_agent.evaluate_claim(
        claim_text=claim["text"],
        subject_qid=claim["subject_entity_qid"],
        object_qid=claim["object_entity_qid"],
        source_text=claim["passage_text"]
    )
    
    # Step 3: Record review in Neo4j
    review = {
        "review_id": generate_uuid(),
        "agent_id": reviewer_agent_id,
        "claim_id": claim_id,
        "timestamp": datetime.now().isoformat(),
        "verdict": review_result["verdict"],  # "support", "challenge", "uncertain"
        "confidence": review_result["confidence"],  # 0.0 - 1.0
        "reasoning_summary": review_result["reasoning"],
        "fallacies_detected": review_result.get("fallacies", [])
    }
    
    neo4j_writer.create_review(review)
    
    # Step 4: Calculate consensus
    all_reviews = neo4j_reader.get_reviews_for_claim(claim_id)
    consensus = calculate_consensus(all_reviews)
    
    # Step 5: Update claim status
    new_status = determine_status(consensus, all_reviews)
    
    neo4j_writer.update_claim(claim_id, {
        "consensus_score": consensus,
        "review_count": len(all_reviews),
        "status": new_status,
        "last_reviewed": datetime.now().isoformat()
    })
    
    return {
        "review_id": review["review_id"],
        "verdict": review["verdict"],
        "consensus_score": consensus,
        "new_status": new_status,
        "total_reviews": len(all_reviews)
    }

def calculate_consensus(reviews: List[Dict]) -> float:
    """Calculate weighted Bayesian consensus score."""
    if not reviews:
        return 0.5  # Neutral prior
    
    # Weight each review by agent confidence and expertise
    weighted_sum = 0
    weight_total = 0
    
    for review in reviews:
        weight = review.get("weight", 1.0)
        confidence = review["confidence"]
        
        # Convert verdict to numeric value
        if review["verdict"] == "support":
            value = 1.0
        elif review["verdict"] == "challenge":
            value = 0.0
        else:  # uncertain
            value = 0.5
        
        weighted_sum += value * confidence * weight
        weight_total += weight
    
    # Bayesian average with prior
    prior_weight = 1.0
    prior_value = 0.5
    
    consensus = (weighted_sum + prior_weight * prior_value) / (weight_total + prior_weight)
    
    return consensus

def determine_status(consensus: float, reviews: List[Dict]) -> str:
    """Determine claim status from consensus score and review distribution."""
    if len(reviews) < 3:
        return "proposed"  # Need minimum reviews
    
    # Count support vs challenge
    support_count = sum(1 for r in reviews if r["verdict"] == "support")
    total_count = len(reviews)
    support_ratio = support_count / total_count if total_count > 0 else 0
    
    # Apply thresholds
    if consensus >= 0.8 and support_ratio >= 0.7:
        return "validated"
    elif consensus >= 0.5:
        return "disputed"
    else:
        return "rejected"
```

---

## **9.3 Consensus Building Workflow**

### **9.3.1 Synthesis for Conflicting Claims**

When multiple agents propose conflicting claims about the same subject:

```
ClaimA (Agent1) â”€â”
ClaimB (Agent2) â”€â”¼â”€> SynthesisAgent â†’ Synthesis Node â†’ Resolved Claim
ClaimC (Agent3) â”€â”˜
```

**Example Conflict:**
- Agent1: "Caesar crossed Rubicon on January 10, 49 BCE"
- Agent2: "Caesar crossed Rubicon on January 11, 49 BCE"
- Agent3: "Caesar crossed Rubicon in early January 49 BCE"

**Resolution:**
- SynthesisAgent creates Synthesis node
- Records all conflicting claims
- Consensus method: Weighted average of dates + uncertainty annotation
- Result: "Caesar crossed Rubicon circa January 10-11, 49 BCE" (confidence 0.85)

---

### **9.3.2 Implementation Example**

```python
def synthesis_workflow(claim_ids: List[str], synthesis_agent_id: str) -> Dict:
    """Resolve conflicting claims through synthesis."""
    
    # Retrieve all conflicting claims
    claims = [neo4j_reader.get_claim(cid) for cid in claim_ids]
    
    # Analyze conflict type
    conflict_type = analyze_conflict(claims)
    # Returns: "temporal" (date conflict), "spatial" (location conflict), "factual" (contradiction)
    
    # Agent synthesizes resolution
    synthesis_result = synthesis_agent.resolve_conflict(
        claims=claims,
        conflict_type=conflict_type
    )
    
    # Create Synthesis node
    synthesis = {
        "synthesis_id": generate_uuid(),
        "agent_id": synthesis_agent_id,
        "timestamp": datetime.now().isoformat(),
        "consensus_method": "weighted_bayesian",
        "consensus_score": synthesis_result["confidence"],
        "resolution_strategy": synthesis_result["strategy"],
        "resolved_text": synthesis_result["resolution_text"]
    }
    
    neo4j_writer.create_synthesis(synthesis)
    
    # Link to all source claims
    for claim_id in claim_ids:
        neo4j_writer.create_edge(synthesis["synthesis_id"], "SYNTHESIZED_FROM", claim_id)
    
    # Create new resolved claim
    resolved_claim = {
        "claim_text": synthesis_result["resolution_text"],
        "cipher": generate_cipher(synthesis_result["resolution_text"]),
        "status": "validated",
        "confidence": synthesis_result["confidence"],
        "synthesis_id": synthesis["synthesis_id"],
        "source_claims": claim_ids
    }
    
    neo4j_writer.create_claim(resolved_claim)
    
    return {
        "synthesis_id": synthesis["synthesis_id"],
        "resolved_claim_cipher": resolved_claim["cipher"],
        "consensus_score": synthesis_result["confidence"]
    }
```

---

## **9.4 Claim Promotion Workflow**

### **9.4.1 Promotion Steps**

Convert validated claims from evidence layer to canonical graph:

```
Claim (validated) â†’ Promotion Process â†’ Canonical Entity/Relationship + Provenance Link
      â†“                    â†“                           â†“
(status=validated)   (4-step process)     (SUPPORTED_BY edge to claim)
```

**4-Step Promotion Process:**

1. **Remove Proposed Status**: Update entities/relationships to canonical
2. **Convert ProposedEdge**: Create actual relationship edge from ProposedEdge template
3. **Update Metadata**: Set promotion date, promoted flag
4. **Link Provenance**: Create `SUPPORTED_BY` edge from canonical element to claim

---

### **9.4.2 Implementation Example**

```python
def claim_promotion_workflow(claim_id: str) -> Dict:
    """Promote validated claim to canonical graph."""
    
    # Step 1: Retrieve claim and verify status
    claim = neo4j_reader.get_claim(claim_id)
    
    if claim["status"] != "validated":
        return {"error": "Only validated claims can be promoted"}
    
    # Step 2: Promotion Process (4 steps)
    
    # Step 2a: Remove proposed status from nodes
    neo4j_writer.update_entity(claim["subject_entity_qid"], {
        "claim_status": None,  # Remove proposed flag
        "promoted": True,
        "promotion_date": datetime.now().isoformat()
    })
    
    neo4j_writer.update_entity(claim["object_entity_qid"], {
        "claim_status": None,
        "promoted": True,
        "promotion_date": datetime.now().isoformat()
    })
    
    # Step 2b: Convert ProposedEdge to actual relationship
    proposed_edges = neo4j_reader.get_proposed_edges_for_claim(claim_id)
    
    for pedge in proposed_edges:
        # Create actual relationship edge
        neo4j_writer.create_relationship(
            from_qid=pedge["from_qid"],
            to_qid=pedge["to_qid"],
            relationship_type=pedge["edge_type"],
            properties={
                **pedge.get("edge_properties", {}),
                "promoted_from_claim": claim_id,
                "promotion_date": datetime.now().isoformat(),
                "confidence": claim["consensus_score"]
            }
        )
        
        # Delete ProposedEdge (or mark as promoted)
        neo4j_writer.delete_node(pedge["edge_id"])
    
    # Step 2c: Update claim metadata
    neo4j_writer.update_claim(claim_id, {
        "promoted": True,
        "promotion_date": datetime.now().isoformat()
    })
    
    # Step 2d: Link provenance (SUPPORTED_BY edge)
    canonical_entity = neo4j_reader.get_entity(claim["subject_entity_qid"])
    
    neo4j_writer.create_edge(
        from_id=canonical_entity["entity_id"],
        edge_type="SUPPORTED_BY",
        to_id=claim_id,
        properties={
            "confidence": claim["consensus_score"],
            "promotion_date": datetime.now().isoformat()
        }
    )
    
    return {
        "promoted": True,
        "claim_id": claim_id,
        "entities_promoted": [claim["subject_entity_qid"], claim["object_entity_qid"]],
        "relationships_created": len(proposed_edges),
        "consensus_score": claim["consensus_score"]
    }
```

---

### **9.4.3 Idempotency & Reversibility**

**Idempotent**: Safe to re-run promotion workflow
- Check if already promoted before processing
- Use MERGE instead of CREATE for edges
- Skip if `promoted=true` flag already set

**Reversible**: Can demote claim if evidence changes
- Keep original Claim nodes (don't delete)
- Mark canonical elements as `demoted=true`
- Preserve provenance trail for audit

```cypher
// Demotion query (if consensus drops below threshold)
MATCH (entity)-[r:SUPPORTED_BY]->(claim:Claim {claim_id: $claim_id})
WHERE claim.promoted = true AND claim.consensus_score < 0.8
SET entity.demoted = true,
    entity.demotion_date = datetime(),
    claim.promoted = false
// Keep claim and provenance for historical record
```

---

## **9.5 Error Handling & Recovery**

### **9.5.1 Workflow Failure Modes**

| Failure Type | Recovery Strategy |
|--------------|-------------------|
| **LLM Timeout** | Retry with exponential backoff (3 attempts) |
| **LLM Hallucination** | Validation layer catches (EntityAgent rejects invalid QIDs) |
| **Neo4j Connection Loss** | Queue writes, retry when connection restored |
| **Duplicate Claim** | Check cipher collision, merge reviews if duplicate found |
| **Agent Crash** | Workflow state persisted, resume from last checkpoint |

---

### **9.5.2 Workflow Monitoring**

```python
class WorkflowMonitor:
    """Monitor workflow execution and alert on failures."""
    
    def log_workflow_start(self, workflow_type: str, workflow_id: str):
        """Record workflow start."""
        log.info(f"Workflow {workflow_type} started: {workflow_id}")
        self.metrics["workflows_started"] += 1
    
    def log_workflow_completion(self, workflow_type: str, workflow_id: str, duration: float):
        """Record workflow completion."""
        log.info(f"Workflow {workflow_type} completed: {workflow_id} in {duration}s")
        self.metrics["workflows_completed"] += 1
        self.metrics["avg_duration"] = (self.metrics["avg_duration"] + duration) / 2
    
    def log_workflow_error(self, workflow_type: str, workflow_id: str, error: str):
        """Record workflow error and alert."""
        log.error(f"Workflow {workflow_type} failed: {workflow_id} - {error}")
        self.metrics["workflows_failed"] += 1
        
        # Alert if failure rate exceeds threshold
        failure_rate = self.metrics["workflows_failed"] / max(self.metrics["workflows_started"], 1)
        if failure_rate > 0.1:  # 10% failure rate
            self.send_alert(f"High workflow failure rate: {failure_rate:.1%}")
```

---

## **9.6 Facet Assessment Workflow** ðŸŸ¡ **STAR PATTERN - Multi-Dimensional Analysis**

### **9.6.1 Overview: Star Pattern for Claims**

**Core Concept:** A claim is evaluated **independently across all 16 analytical dimensions** simultaneously. Each facet (political, military, economic, etc.) receives its own assessment by a specialist agent.

**The Star Pattern:**
```
                â”Œâ”€â”€â†’ MilitaryFacet
                â”‚
   â”Œâ”€â”€â†’ Belief â”€â”¼â”€â”€â†’ DiplomaticFacet
   â”‚            â”‚
Claim â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â†’ PoliticalFacet
   â”‚          â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤â”€â”€â†’ EconomicFacet
               â””â”€â”€â†’ [12 other facet vectors]
```

**Key Property:** One AnalysisRun creates multiple independent FacetAssessments, each with its own confidence score, rationale, and source citations.

### **9.6.2 Facet Assessment Workflow (6 Steps)**

**Step 1: Receive Claim for Multi-Dimensional Analysis**
```python
def start_facet_assessment_workflow(claim_id: str) -> Dict:
    """Initiate multi-dimensional facet analysis."""
    claim = neo4j_reader.get_claim(claim_id)
    
    # Create AnalysisRun node (parent container)
    run_id = f"RUN_{claim_id}_{datetime.now().isoformat()}"
    run = neo4j_writer.create_node("AnalysisRun", {
        "run_id": run_id,
        "pipeline_version": "v2.0_faceted",
        "created_at": datetime.now().isoformat(),
        "status": "in_progress"
    })
    
    # Link claim to run
    neo4j_writer.create_edge(claim_id, "HAS_ANALYSIS_RUN", run_id)
    
    return {"run_id": run_id, "claim_id": claim_id, "status": "step_1_complete"}
```

**Step 2: Route Claim to Facet-Specialist Agents**
```python
def route_to_facet_agents(claim_id: str, run_id: str) -> List[Dict]:
    """Route claim to all 16 facet-specialist agents."""
    facet_agents = [
        ("AGENT_POLITICAL_V1", "PoliticalFacet"),
        ("AGENT_MILITARY_V1", "MilitaryFacet"),
        ("AGENT_ECONOMIC_V1", "EconomicFacet"),
        ("AGENT_CULTURAL_V1", "CulturalFacet"),
        ("AGENT_RELIGIOUS_V1", "ReligiousFacet"),
        ("AGENT_INTELLECTUAL_V1", "IntellectualFacet"),
        ("AGENT_SCIENTIFIC_V1", "ScientificFacet"),
        ("AGENT_ARTISTIC_V1", "ArtisticFacet"),
        ("AGENT_SOCIAL_V1", "SocialFacet"),
        ("AGENT_DEMOGRAPHIC_V1", "DemographicFacet"),
        ("AGENT_ENVIRONMENTAL_V1", "EnvironmentalFacet"),
        ("AGENT_TECHNOLOGICAL_V1", "TechnologicalFacet"),
        ("AGENT_LINGUISTIC_V1", "LinguisticFacet"),
        ("AGENT_ARCHAEOLOGICAL_V1", "ArchaeologicalFacet"),
        ("AGENT_DIPLOMATIC_V1", "DiplomaticFacet"),
        ("AGENT_GEOGRAPHIC_V1", "GeographicFacet"),
    ]
    
    routing_tasks = []
    for agent_id, facet_type in facet_agents:
        routing_tasks.append({
            "claim_id": claim_id,
            "run_id": run_id,
            "agent_id": agent_id,
            "facet_type": facet_type,
            "status": "queued"
        })
    
    return routing_tasks
```

**Step 3: Each Agent Creates Independent Facet Assessment**
```python
def evaluate_claim_for_facet(claim_id: str, run_id: str, agent_id: str, facet_type: str) -> Dict:
    """Evaluate claim from single facet perspective."""
    claim = neo4j_reader.get_claim(claim_id)
    
    # Agent evaluates claim through its facet lens
    # (e.g., political agent evaluates political implications)
    prompt = f"""
    Evaluate this historical claim from the {facet_type} perspective:
    
    "{claim['text']}"
    
    Provide:
    1. Confidence score (0.0-1.0)
    2. Status (supported/challenged/uncertain/mostly_supported)
    3. Rationale (2-3 sentences)
    4. Key supporting/contradicting evidence
    """
    
    assessment_result = llm_agent.evaluate(prompt)
    
    # Create FacetAssessment node
    assessment_id = f"FA_{claim_id}_{facet_type}_{run_id}"
    assessment = neo4j_writer.create_node("FacetAssessment", {
        "assessment_id": assessment_id,
        "score": assessment_result["confidence"],
        "status": assessment_result["status"],
        "rationale": assessment_result["rationale"],
        "evidence_count": len(assessment_result["sources"]),
        "created_at": datetime.now().isoformat()
    })
    
    # Link to AnalysisRun
    neo4j_writer.create_edge(run_id, "HAS_FACET_ASSESSMENT", assessment_id)
    
    # Link to Facet node
    facet_node = neo4j_reader.get_facet(facet_type)
    neo4j_writer.create_edge(assessment_id, "ASSESSES_FACET", facet_node["unique_id"])
    
    # Link to Agent
    neo4j_writer.create_edge(assessment_id, "EVALUATED_BY", agent_id)
    
    return {
        "assessment_id": assessment_id,
        "score": assessment_result["confidence"],
        "status": assessment_result["status"]
    }
```

**Step 4: Aggregate Facet Assessments (Star Pattern Complete)**
```python
def aggregate_facet_assessments(run_id: str) -> Dict:
    """Aggregate all 16 facet assessments into star pattern."""
    # Query: Get all assessments for this run
    query = """
    MATCH (run:AnalysisRun {run_id: $run_id})
      -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
      -[:ASSESSES_FACET]->(f:Facet)
      -[:IN_FACET_CATEGORY]->(cat:FacetCategory)
    OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
    RETURN
      cat.key AS facet_category,
      f.label AS facet_label,
      fa.score AS assessment_score,
      fa.status AS assessment_status,
      fa.rationale AS assessment_rationale,
      a.label AS agent_label
    ORDER BY cat.key
    """
    
    assessments = neo4j_reader.query(query, run_id=run_id)
    
    # Group by facet category for UI tabs
    by_category = {}
    for assessment in assessments:
        cat = assessment["facet_category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(assessment)
    
    return {
        "run_id": run_id,
        "total_assessments": len(assessments),
        "facets_evaluated": len(by_category),
        "by_category": by_category,
        "status": "aggregated"
    }
```

**Step 5: Generate Multi-Dimensional Confidence Score**
```python
def calculate_multi_dimensional_confidence(run_id: str) -> Dict:
    """Calculate overall claim confidence from facet assessments."""
    query = """
    MATCH (run:AnalysisRun {run_id: $run_id})
      -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
    RETURN
      fa.score AS score,
      fa.status AS status,
      count(*) AS count
    """
    
    results = neo4j_reader.query(query, run_id=run_id)
    
    # Calculate weighted average (supported=1.0, mostly_supported=0.8, uncertain=0.5, challenged=0.0)
    status_weights = {"supported": 1.0, "mostly_supported": 0.8, "uncertain": 0.5, "challenged": 0.0}
    
    total_score = 0
    total_weight = 0
    facet_scores = []
    
    for result in results:
        score = result["score"]
        status = result["status"]
        weight = status_weights.get(status, 0.5)
        
        total_score += score * weight
        total_weight += weight
        facet_scores.append({"status": status, "score": score})
    
    overall_confidence = total_score / total_weight if total_weight > 0 else 0.5
    
    return {
        "overall_confidence": overall_confidence,
        "facet_scores": facet_scores,
        "summary": f"{len(facet_scores)} dimensions analyzed, avg confidence {overall_confidence:.2f}"
    }
```

**Step 6: Mark Assessment Complete & Generate Reports**
```python
def complete_facet_assessment(run_id: str, overall_confidence: float) -> Dict:
    """Complete analysis run and generate reports."""
    # Update AnalysisRun status
    neo4j_writer.update_node(run_id, {
        "status": "completed",
        "updated_at": datetime.now().isoformat(),
        "overall_confidence": overall_confidence
    })
    
    # Query for report generation
    query = """
    MATCH (claim:Claim)-[:HAS_ANALYSIS_RUN]->(run:AnalysisRun {run_id: $run_id})
      -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
      -[:ASSESSES_FACET]->(f:Facet)
      -[:IN_FACET_CATEGORY]->(cat:FacetCategory)
    OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
    RETURN
      claim.text AS claim_text,
      run.run_id AS run_id,
      run.pipeline_version AS pipeline_version,
      collect({
        category: cat.key,
        facet: f.label,
        score: fa.score,
        status: fa.status,
        rationale: fa.rationale,
        agent: a.label
      }) AS assessments
    """
    
    report = neo4j_reader.query(query, run_id=run_id)[0]
    
    return {
        "status": "complete",
        "run_id": run_id,
        "claim": report["claim_text"],
        "overall_confidence": overall_confidence,
        "facet_assessments": report["assessments"],
        "ui_ready": True
    }
```

### **9.6.3 UI Query Patterns (Facet Tab Interface)**

**Query 1: Get All Assessments Grouped by Facet Category**
```cypher
MATCH (c:Claim {claim_id: "CLAIM_CAESAR_RUBICON"})
  -[:HAS_ANALYSIS_RUN]->(run:AnalysisRun)
  -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
  -[:ASSESSES_FACET]->(f:Facet)
  -[:IN_FACET_CATEGORY]->(cat:FacetCategory)
OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
RETURN
  cat.key AS facet_category,
  cat.label AS category_label,
  collect({
    facet_id: f.unique_id,
    facet_label: f.label,
    score: fa.score,
    status: fa.status,
    rationale: fa.rationale,
    agent: a.label
  }) AS assessments
ORDER BY facet_category;
```

**Result (JSON for UI tabs):**
```json
{
  "facet_category": "POLITICAL",
  "category_label": "Political",
  "assessments": [
    {
      "facet_id": "POLITICALFACET_Q3624078",
      "facet_label": "Caesar's political dominance",
      "score": 0.92,
      "status": "supported",
      "rationale": "Multiple primary sources corroborate political implications",
      "agent": "Political Historian Agent"
    }
  ]
}
```

**Query 2: Compare Two Analysis Runs (A/B Testing)**
```cypher
MATCH (claim:Claim)-[:HAS_ANALYSIS_RUN]->(run1:AnalysisRun {run_id: "RUN_001"})
MATCH (claim)-[:HAS_ANALYSIS_RUN]->(run2:AnalysisRun {run_id: "RUN_002"})
MATCH (run1)-[:HAS_FACET_ASSESSMENT]->(fa1:FacetAssessment)
MATCH (run2)-[:HAS_FACET_ASSESSMENT]->(fa2:FacetAssessment)
WHERE fa1.assessment_id STARTS WITH fa2.assessment_id SPLIT("_")[0]
RETURN
  fa1.score AS run1_score,
  fa2.score AS run2_score,
  fa1.score - fa2.score AS score_difference
ORDER BY abs(score_difference) DESC;
```

### **9.6.4 Benefits of Star Pattern**

1. **Multi-Dimensional Analysis:** Single event analyzed across all 16 analytical axes
2. **Agent Specialization:** Political expert evaluates political facet, military expert evaluates military facet
3. **Independent Confidence:** Each facet has its own confidence score (military_conf â‰  political_conf)
4. **Separate Sourcing:** Each facet cites relevant sources (military from military historians, political from political historians)
5. **UI Tabs:** Display "Political" | "Military" | "Economic" | etc. tabs for easy navigation
6. **Re-Runnable:** Compare analysis "v1" vs "v2" to track prompt/model improvements
7. **Extensible:** Add new facet dimensions without changing claim structure

---

# **PART IV: OPERATIONAL GOVERNANCE**

---

# **10. Quality Assurance & Validation**

## **10.0 Quality Assurance Overview**

Quality assurance in Chrystallum operates at multiple levels:
1. **Schema Validation**: Ensure all nodes/edges conform to type schemas
2. **Confidence Scoring**: Systematic evaluation of claim reliability
3. **Source Tier Assessment**: Classify sources by scholarly authority
4. **Agent Calibration**: Monitor and adjust agent performance over time

---

## **10.1 Schema Validation Rules**

### **10.1.1 Required Property Validation**

**Enforcement:** Reject writes that violate required property constraints

```cypher
// Constraint: Every Entity must have entity_id, label, qid, entity_type
CREATE CONSTRAINT entity_required_properties IF NOT EXISTS
FOR (e:Entity)
REQUIRE e.entity_id IS NOT NULL
  AND e.label IS NOT NULL
  AND e.qid IS NOT NULL
  AND e.entity_type IS NOT NULL;
```

**Python Validation:**
```python
from pydantic import BaseModel, Field

class EntitySchema(BaseModel):
    """Validation schema for Entity nodes."""
    entity_id: str = Field(..., description="Internal unique identifier")
    label: str = Field(..., description="Primary name/label")
    qid: str = Field(..., pattern=r"^Q\\d+$", description="Wikidata QID")
    entity_type: str = Field(..., description="Entity type classification")
    
    # Optional properties
    fast_id: Optional[str] = None
    lcc_code: Optional[str] = None
    
    def validate_before_write(self):
        """Additional validation before Neo4j write."""
        # Check QID format
        if not self.qid.startswith("Q"):
            raise ValueError(f"Invalid QID format: {self.qid}")
        
        # Check entity_type is in allowed list
        allowed_types = ["Human", "Place", "Event", "Period", "Organization"]
        if self.entity_type not in allowed_types:
            raise ValueError(f"Invalid entity_type: {self.entity_type}")
```

---

### **10.1.2 Relationship Type Validation**

**Validation:** Ensure all relationships use canonical types from registry

```python
def validate_relationship_type(rel_type: str) -> bool:
    """Check if relationship type is in canonical registry."""
    canonical_types = load_canonical_relationship_types()  # From CSV
    return rel_type in canonical_types

def create_relationship_with_validation(from_id: str, to_id: str, rel_type: str, properties: Dict):
    """Create relationship with type validation."""
    if not validate_relationship_type(rel_type):
        raise ValueError(f"Invalid relationship type: {rel_type}. Not in canonical registry.")
    
    # Proceed with creation
    neo4j_writer.create_relationship(from_id, to_id, rel_type, properties)
```

---

## **10.2 Confidence Scoring Methodology**

### **10.2.1 Source Tier Definitions**

Chrystallum classifies sources by scholarly authority:

| Tier | Description | Confidence Range | Examples |
|------|-------------|------------------|----------|
| **Primary** | Original historical sources | 0.90 - 1.00 | Ancient texts, inscriptions, archaeological evidence |
| **Secondary (Academic)** | Peer-reviewed scholarship | 0.80 - 0.90 | Journal articles, university press monographs |
| **Secondary (Trade)** | Non-peer-reviewed but reputable | 0.70 - 0.80 | Popular history by credentialed authors |
| **Tertiary** | Reference works | 0.60 - 0.70 | Encyclopedias, dictionaries |
| **Uncertain** | Unverified or contested | < 0.60 | Wikipedia (pre-verification), forums, blogs |

**Implementation:**
```python
def assign_source_tier(source_work_qid: str) -> Dict:
    """Assign confidence tier based on source classification."""
    work_data = wikidata_api.get_entity(source_work_qid)
    
    # Check work type
    instance_of = work_data.get("claims", {}).get("P31", [])  # P31 = instance of
    
    if "Q5633421" in instance_of:  # Scientific journal article
        return {"tier": "Secondary (Academic)", "base_confidence": 0.85}
    elif "Q571" in instance_of:  # Book
        # Check publisher for university press
        publisher = work_data.get("claims", {}).get("P123", [])
        if is_university_press(publisher):
            return {"tier": "Secondary (Academic)", "base_confidence": 0.85}
        else:
            return {"tier": "Secondary (Trade)", "base_confidence": 0.75}
    elif "Q8242" in instance_of:  # Ancient text
        return {"tier": "Primary", "base_confidence": 0.95}
    else:
        return {"tier": "Uncertain", "base_confidence": 0.50}
```

---

### **10.2.2 Confidence Adjustment Factors**

Base confidence can be adjusted based on additional factors:

| Factor | Adjustment | Rationale |
|--------|------------|-----------|
| **Multiple attestations** | +0.05 per additional source (max +0.15) | Corroboration increases confidence |
| **Agent consensus** | +0.10 if â‰¥80% agent agreement | Multi-agent validation |
| **Temporal proximity** | +0.05 if contemporary source | Closer to events = more reliable |
| **Conflict detected** | -0.15 | Conflicting claims reduce confidence |
| **Agent expertise** | Â±0.05 | Specialist agents weight higher |

```python
def calculate_adjusted_confidence(base_confidence: float, factors: Dict) -> float:
    """Adjust base confidence score based on additional factors."""
    adjusted = base_confidence
    
    # Multiple attestations
    attestation_count = factors.get("attestation_count", 1)
    adjusted += min(0.15, (attestation_count - 1) * 0.05)
    
    # Agent consensus
    if factors.get("agent_consensus", 0) >= 0.8:
        adjusted += 0.10
    
    # Temporal proximity
    if factors.get("contemporary_source", False):
        adjusted += 0.05
    
    # Conflicts
    if factors.get("conflict_detected", False):
        adjusted -= 0.15
    
    # Agent expertise
    adjusted += factors.get("agent_expertise_adjustment", 0)
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, adjusted))
```

---

## **10.3 Agent Calibration Procedures**

### **10.3.1 Performance Metrics**

Track agent performance across multiple dimensions:

```python
class AgentPerformanceMetrics:
    """Track agent performance over time."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.metrics = {
            "claims_generated": 0,
            "claims_validated": 0,
            "claims_rejected": 0,
            "avg_confidence": 0.0,
            "avg_consensus_score": 0.0,
            "hallucination_rate": 0.0,  # Invalid entity extractions
            "accuracy_rate": 0.0         # Correct entity resolutions
        }
    
    def update_metrics(self, claim_result: Dict):
        """Update metrics after claim processing."""
        self.metrics["claims_generated"] += 1
        
        if claim_result["status"] == "validated":
            self.metrics["claims_validated"] += 1
        elif claim_result["status"] == "rejected":
            self.metrics["claims_rejected"] += 1
        
        # Update averages
        self.metrics["avg_consensus_score"] = (
            (self.metrics["avg_consensus_score"] * (self.metrics["claims_generated"] - 1) 
             + claim_result["consensus_score"]) 
            / self.metrics["claims_generated"]
        )
    
    def get_calibration_adjustment(self) -> float:
        """Calculate agent weight adjustment based on performance."""
        # High-performing agents get higher weight
        performance_score = (
            self.metrics["accuracy_rate"] * 0.4 +
            self.metrics["avg_consensus_score"] * 0.3 +
            (1 - self.metrics["hallucination_rate"]) * 0.3
        )
        
        # Weight adjustment: Â±20% based on performance
        adjustment = (performance_score - 0.5) * 0.4
        return 1.0 + adjustment  # Range: [0.8, 1.2]
```

---

### **10.3.2 Automatic Recalibration**

```python
def recalibrate_agent(agent_id: str):
    """Recalibrate agent based on recent performance."""
    metrics = AgentPerformanceMetrics(agent_id)
    metrics.load_recent_history(days=30)  # Last 30 days
    
    new_weight = metrics.get_calibration_adjustment()
    
    # Update agent configuration
    neo4j_writer.update_agent(agent_id, {
        "weight": new_weight,
        "calibration_date": datetime.now().isoformat(),
        "performance_score": metrics.metrics["accuracy_rate"]
    })
    
    # Alert if performance degraded significantly
    if new_weight < 0.9:
        log.warning(f"Agent {agent_id} performance degraded. New weight: {new_weight:.2f}")
        send_alert(f"Agent {agent_id} requires review")
```

---

## **10.4 Validation Query Patterns**

### **10.4.1 Data Integrity Checks**

```cypher
// Check for orphaned claims (no source work)
MATCH (c:Claim)
WHERE NOT EXISTS((c)-[:EXTRACTED_FROM]->(:Work))
RETURN c.claim_id, c.text, c.timestamp
ORDER BY c.timestamp DESC
LIMIT 100;

// Check for entities missing required properties
MATCH (e:Entity)
WHERE e.qid IS NULL OR e.label IS NULL
RETURN e.entity_id, e.entity_type, labels(e)
LIMIT 100;

// Check for duplicate QIDs
MATCH (e:Entity)
WITH e.qid AS qid, collect(e) AS entities
WHERE size(entities) > 1
RETURN qid, [e IN entities | e.entity_id] AS duplicate_ids;

// Check for claims without reviews
MATCH (c:Claim {status: "proposed"})
WHERE NOT EXISTS((c)<-[:REVIEWS]-(:Review))
  AND datetime(c.timestamp) < datetime() - duration({days: 7})
RETURN c.claim_id, c.text, c.timestamp
ORDER BY c.timestamp
LIMIT 50;
```

---

### **10.4.2 Performance Monitoring Queries**

```cypher
// Agent productivity (claims per agent)
MATCH (a:Agent)-[:MADE_CLAIM]->(c:Claim)
WITH a.agent_id AS agent, 
     count(c) AS claims_total,
     sum(CASE WHEN c.status = "validated" THEN 1 ELSE 0 END) AS claims_validated
RETURN agent, claims_total, claims_validated,
       round(claims_validated * 100.0 / claims_total, 1) AS validation_rate_pct
ORDER BY validation_rate_pct DESC;

// Consensus distribution
MATCH (c:Claim)
WHERE c.consensus_score IS NOT NULL
RETURN 
  count(CASE WHEN c.consensus_score >= 0.8 THEN 1 END) AS high_confidence,
  count(CASE WHEN c.consensus_score >= 0.5 AND c.consensus_score < 0.8 THEN 1 END) AS medium_confidence,
  count(CASE WHEN c.consensus_score < 0.5 THEN 1 END) AS low_confidence;

// Average review time
MATCH (c:Claim)-[:REVIEWS]-(r:Review)
WITH c, collect(r) AS reviews
WHERE size(reviews) >= 3
WITH c.timestamp AS claim_time,
     max([r IN reviews | datetime(r.timestamp)]) AS last_review_time
RETURN avg(duration.between(datetime(claim_time), last_review_time).days) AS avg_review_days;
```

---

# **11. Graph Governance & Maintenance**

## **11.0 Governance Overview**

Graph governance ensures long-term system health through:
1. **Schema Versioning**: Track schema changes over time
2. **Neo4j Indexing Strategy**: Optimize query performance
3. **Backup & Recovery**: Protect against data loss
4. **Monitoring & Alerts**: Detect issues proactively

---

## **11.1 Schema Versioning Strategy**

### **11.1.1 Version Metadata**

Track schema versions in dedicated nodes:

```cypher
CREATE (schema:SchemaVersion {
  version: "3.2",
  release_date: "2026-02-12",
  description: "Added identifier safety validation, expanded relationship types",
  breaking_changes: ["Claim cipher generation algorithm updated"],
  migration_required: false
});
```

---

### **11.1.2 Migration Patterns**

When schema changes require data migration:

```cypher
// Example: Add new required property to existing nodes
MATCH (e:Entity)
WHERE e.backbone_marc IS NULL
SET e.backbone_marc = ""  // Default empty string
SET e.schema_version = "3.2",
    e.migration_date = datetime();

// Track migration completion
CREATE (m:Migration {
  migration_id: "add_backbone_marc_2026_02_12",
  start_time: datetime(),
  end_time: datetime(),
  nodes_affected: count(e),
  status: "completed"
});
```

---

## **11.2 Neo4j Indexing Strategy**

### **11.2.1 Required Indexes**

```cypher
// Core entity lookups
CREATE INDEX entity_id_index IF NOT EXISTS FOR (e:Entity) ON (e.entity_id);
CREATE INDEX qid_index IF NOT EXISTS FOR (e:Entity) ON (e.qid);
CREATE INDEX fast_id_index IF NOT EXISTS FOR (s:SubjectConcept) ON (s.fast_id);

// Temporal indexes
CREATE INDEX year_index IF NOT EXISTS FOR (y:Year) ON (y.year);
CREATE INDEX event_start_date_index IF NOT EXISTS FOR (e:Event) ON (e.start_date);

// Claims workflow
CREATE INDEX claim_status_index IF NOT EXISTS FOR (c:Claim) ON (c.status);
CREATE INDEX claim_cipher_index IF NOT EXISTS FOR (c:Claim) ON (c.cipher);

// Full-text search
CREATE FULLTEXT INDEX entity_search IF NOT EXISTS
FOR (e:Entity) ON EACH [e.label, e.name];

CREATE FULLTEXT INDEX claim_text_search IF NOT EXISTS
FOR (c:Claim) ON EACH [c.text, c.passage_text];
```

---

### **11.2.2 Composite Indexes**

For common multi-property queries:

```cypher
// Agent + status lookup
CREATE INDEX agent_claim_status IF NOT EXISTS
FOR (c:Claim) ON (c.source_agent_id, c.status);

// Date range queries
CREATE INDEX period_date_range IF NOT EXISTS
FOR (p:Period) ON (p.start_date, p.end_date);

// Action structure queries
CREATE INDEX action_structure_index IF NOT EXISTS
FOR ()-[r:RELATIONSHIP]-() ON (r.goal_type, r.action_type);
```

---

## **11.3 Backup & Recovery Procedures**

### **11.3.1 Backup Strategy**

```bash
# Daily incremental backups
neo4j-admin backup \\
  --from=localhost:6362 \\
  --backup-dir=/backups/incremental \\
  --name=chrystallum_$(date +%Y%m%d)

# Weekly full backups
neo4j-admin backup \\
  --from=localhost:6362 \\
  --backup-dir=/backups/full \\
  --name=chrystallum_full_$(date +%Y%m%d) \\
  --fallback-to-full=true
```

---

### **11.3.2 Recovery Procedures**

```bash
# Restore from backup
neo4j-admin restore \\
  --from=/backups/full/chrystallum_full_20260212 \\
  --database=chrystallum \\
  --force

# Verify restored data integrity
cypher-shell -u neo4j -p password \\
  "MATCH (n) RETURN count(n) AS node_count;"
```

---

## **11.4 Monitoring & Alerts**

### **11.4.1 Health Check Queries**

```cypher
// Daily health check: Count nodes by type
CALL apoc.meta.stats() YIELD labels
RETURN labels;

// Check for schema violations
MATCH (e:Entity)
WHERE e.qid IS NULL OR NOT e.qid STARTS WITH "Q"
RETURN count(e) AS invalid_qids;

// Check consensus score distribution
MATCH (c:Claim)
RETURN 
  avg(c.consensus_score) AS avg_consensus,
  stdev(c.consensus_score) AS stdev_consensus,
  percentileCont(c.consensus_score, 0.5) AS median_consensus;
```

---

### **11.4.2 Alert Conditions**

```python
class SystemMonitor:
    """Monitor system health and send alerts."""
    
    THRESHOLDS = {
        "claim_review_backlog": 100,        # Alert if >100 unreviewed claims
        "invalid_qid_rate": 0.05,           # Alert if >5% invalid QIDs
        "agent_failure_rate": 0.10,         # Alert if >10% agent failures
        "consensus_score_drop": 0.15        # Alert if avg drops >0.15
    }
    
    def check_health(self):
        """Run all health checks."""
        issues = []
        
        # Check claim backlog
        unreviewed = self.query_neo4j("""
            MATCH (c:Claim {status: 'proposed'})
            WHERE NOT EXISTS((c)<-[:REVIEWS]-())
            RETURN count(c) AS count
        """)[0]["count"]
        
        if unreviewed > self.THRESHOLDS["claim_review_backlog"]:
            issues.append(f"Claim review backlog: {unreviewed} claims awaiting review")
        
        # Check invalid QIDs
        invalid_rate = self.get_invalid_qid_rate()
        if invalid_rate > self.THRESHOLDS["invalid_qid_rate"]:
            issues.append(f"High invalid QID rate: {invalid_rate:.1%}")
        
        # Send alerts if issues found
        if issues:
            self.send_alert("System Health Issues", "\n".join(issues))
```

---

# **12. Future Directions**

## **12.0 Roadmap Overview**

Chrystallum's future development focuses on three areas:
1. **Scalability**: Federated graph networks, distributed consensus
2. **Enrichment**: Expanded authority integration, multilingual support
3. **Research Tools**: Advanced visualization, hypothesis testing

---

## **12.1 Federated Graph Networks**

**Vision**: Multiple Chrystallum instances share knowledge via content-addressable claims

**Architecture:**
```
University A Graph â”€â”
University B Graph â”€â”¼â”€> Shared Claim Registry (ciphers)
Research Lab Graph â”€â”˜         â†“
                          Cross-instance validation
```

**Benefits:**
- Distributed scholarly collaboration
- No central authority required
- Cipher ensures claim integrity across networks
- Consensus emerges from multiple independent validations

**Technical Challenges:**
- Cipher collision resolution
- Cross-instance claim synchronization
- Trust models for foreign claims

---

## **12.2 Multilingual Entity Support**

**Current State**: English-primary with Wikidata multilingual labels

**Future Enhancement:**
- Native support for Latin, Ancient Greek primary sources
- Non-Latin script support (Arabic, Chinese for Silk Road research)
- Language-specific agents with cultural domain expertise

**Implementation:**
```python
# Multi-language entity representation
{
  "qid": "Q1048",
  "labels": {
    "en": "Gaius Julius Caesar",
    "la": "Gaius Iulius Caesar",
    "fr": "Jules CÃ©sar",
    "de": "Gaius Julius CÃ¤sar"
  },
  "primary_language": "la",  # Latin for ancient Roman figure
  "label_preferred": "Gaius Iulius Caesar"  # Use Latin form
}
```

---

## **12.3 Advanced Visualization**

**Planned Features:**
- **Timeline Views**: Stacked timelines by facet (political, military, economic eras)
- **Geographic Maps**: Animated territorial changes over time (PlaceVersion sequence)
- **Network Graphs**: Relationship networks with confidence-weighted edges
- **Provenance Trees**: Visualize complete evidence chains for any claim

**Technology Stack:**
- Cytoscape.js for graph visualization
- D3.js for custom timeline/map rendering
- Neo4j graph algorithms for network analysis

---

## **12.4 Hypothesis Testing Framework**

**Vision**: Researchers propose historical hypotheses, system validates against evidence

**Workflow:**
```
Researcher Hypothesis â†’ Decompose into testable claims â†’ Query graph for supporting/challenging evidence â†’ Calculate hypothesis confidence
```

**Example:**
- Hypothesis: "Caesar's military success was primarily due to loyal veteran legions"
- Decomposition: Check for COMMANDED relationships, VETERAN properties, loyalty indicators
- Evidence: Retrieve all Caesar military campaigns, analyze legion composition
- Result: Confidence score + supporting evidence summary

---

## **12.5 Integration with Emerging Standards**

**Planned Integrations:**
- **IIIF (International Image Interoperability Framework)**: Link to digitized manuscripts
- **TEI (Text Encoding Initiative)**: XML markup for primary source texts
- **Schema.org**: Web semantic markup for public-facing data
- **Linked Open Data (LOD)**: Full RDF export capability

---

---

# **PART V: APPENDICES**

---

## Appendix Strategy

The appendices are now organized as implementation references, while critical operational logic remains in Sections 3-8 for day-to-day readability.

- Sections 3-8 contain the normative architecture and required behavior.
- Appendices provide registries, mappings, governance rules, and examples.
- Appendices E, F, and K are intentionally concise because their core logic is integrated in the body (Sections 3.4, 4.4, 4.5).

---

# **Appendix A: Canonical Relationship Types**

## **A.1 Purpose**

Defines the canonical relationship registry used to normalize edge semantics, directionality, and external mappings.
`lcc_code`, `lcsh_heading`, and `fast_id` are registry-level classification metadata for governance/routing, not properties stored on graph edge instances.

## **A.2 Authoritative Files**

- Primary registry: `Relationships/relationship_types_registry_master.csv`
- Historical duplicate archived: `Archive/Key Files/1-14-26-Canonical_relationship_types.archived-2026-02-13.csv`
- Seed script: `Relationships/relationship_types_seed.cypher`

## **A.3 Current Registry Snapshot**

From `Relationships/relationship_types_registry_master.csv`:

- Total relationship types: `300`
- Categories: `31`
- Lifecycle status: `192 implemented`, `108 candidate`
- Active status: `300 active`

Top categories by volume:

| Category | Count |
|---|---:|
| Political | 39 |
| Familial | 30 |
| Military | 23 |
| Geographic | 20 |
| Economic | 16 |
| Legal | 13 |
| Authorship | 12 |
| Diplomatic | 12 |

## **A.4 Registry Fields (Required Core)**

| Field | Meaning |
|---|---|
| `category` | Semantic family (`Political`, `Military`, etc.) |
| `relationship_type` | Canonical edge label (`PARTICIPATED_IN`, `LOCATED_IN`, etc.) |
| `directionality` | `forward`, `inverse`, or `symmetric` |
| `wikidata_property` | Optional direct Wikidata `P` property |
| `parent_relationship` | Optional inheritance parent |
| `specificity_level` | Relative abstraction level |
| `lcc_code` / `lcsh_heading` / `fast_id` | Library alignment metadata |
| `lifecycle_status` | `implemented` or `candidate` |

## **A.5 Governance Rules**

1. Do not add ad hoc relationship labels directly in code.
2. Add candidate relationships to registry first, with source and rationale.
3. Promote candidate to implemented only after:
- domain/range validation
- directionality review
- external mapping check (if available)
4. Keep inverse forms explicit where required for query ergonomics.

## **A.6 Query Pattern**

```cypher
MATCH ()-[r]->()
WITH type(r) AS rel, count(*) AS n
RETURN rel, n
ORDER BY n DESC;
```

---

**(End of Appendix A)**

---

# **Appendix B: Action Structure Vocabularies**

## **B.1 Purpose**

Defines controlled vocabularies for relationship-level action semantics:

- goal (`goal_type`)
- trigger (`trigger_type`)
- action (`action_type`)
- result (`result_type`)

## **B.2 Authoritative Files**

- Vocabulary registry: `CSV/action_structure_vocabularies.csv`
- Wikidata alignment: `CSV/action_structure_wikidata_mapping.csv`
- Reference explainer: `md/Reference/Action_Structure_Vocabularies.md`

## **B.3 Vocabulary Counts**

From `CSV/action_structure_vocabularies.csv` (`54` total entries):

| Component | Count |
|---|---:|
| Goal Type | 10 |
| Trigger Type | 10 |
| Action Type | 15 |
| Result Type | 19 |

## **B.4 Example Codes**

| Component | Code | Meaning |
|---|---|---|
| Goal | `POL` | Political objective |
| Goal | `MIL` | Military objective |
| Trigger | `POL_TRIGGER` | Political trigger |
| Trigger | `EXT_THREAT` | External threat |
| Action | `MIL_ACT` | Military action |
| Action | `DIPL_ACT` | Diplomatic action |
| Result | `POL_TRANS` | Political transformation |
| Result | `CONQUEST` | Conquest outcome |

## **B.5 Usage Contract**

- Store codes on relationships.
- Keep human-readable descriptions in companion properties.
- Validate code membership before write.
- Use code-to-QID alignment from `CSV/action_structure_wikidata_mapping.csv` for federation.

Example:

```cypher
MATCH (a:Human {label: 'Julius Caesar'}), (b:Event {label: 'Roman Civil War'})
MERGE (a)-[r:CAUSED]->(b)
SET r.goal_type = 'POL',
    r.trigger_type = 'POL_TRIGGER',
    r.action_type = 'MIL_ACT',
    r.result_type = 'POL_TRANS';
```

---

**(End of Appendix B)**

---

# **Appendix C: Entity Taxonomies and Subject Authority Tiers**

## **C.1 Core Entity Families**

Primary entity families are defined in Section 3 and include:

- Person and group entities (`Human`, `Organization`, `Institution`, `Dynasty`)
- Spatiotemporal entities (`Place`, `PlaceVersion`, `Period`, `Year`, `Event`)
- Knowledge/provenance entities (`Work`, `Claim`, `Review`, `Synthesis`)
- Domain-specific entities (Roman naming and office structures)

## **C.2 Subject Authority Tier Policy**

Subject concepts are classified by authority confidence:

| Tier | Criteria | Usage |
|---|---|---|
| `TIER_1` | Strong authority grounding + stable coverage | Default production |
| `TIER_2` | Valid but narrower or less complete coverage | Included with caution |
| `TIER_3` | Provisional or sparse authority support | Include with explicit confidence |
| `EXCLUDED` | Fails authority threshold | Do not ingest |

## **C.3 Required Identifier Backbone by Entity Type**

| Entity Type | Required IDs | Preferred IDs |
|---|---|---|
| Human | `qid` | `viaf_id`, `isni`, `lcsh_id` |
| Place | `qid` | `tgn_id`, `pleiades_id`, `geonames_id` |
| Period | `qid` or local canonical id | `periodo_uri`, `lcsh_id`, `fast_id` |
| Work | `qid` or catalog id | `worldcat_id`, `viaf_id` |
| SubjectConcept | `fast_id` or `lcsh_id` | `qid`, `lcc_code`, `marc_id` |

## **C.4 Consistency Rules**

1. Labels are natural language.
2. Identifiers are atomic strings.
3. Every canonical entity written to graph must include provenance linkage.
4. Subject assignment must not be inferred from entity type alone; use FAST/LCSH/LCC mappings.

---

**(End of Appendix C)**

---

# **Appendix D: Subject Facet Classification**

## **D.1 Purpose**

Defines facet classes and anchor concepts used by the star-pattern architecture.

## **D.2 Authoritative Files**

- Registry: `Facets/facet_registry_master.csv`
- Consolidation note: `Facets/FACETS_CONSOLIDATION_2026-02-12.md`
- Pattern note: `Facets/star-pattern-claims.md`

## **D.3 Current Registry Snapshot**

From `Facets/facet_registry_master.csv`:

- Total facet-anchor rows: `86`
- Facet classes: `16`
- Facet keys: `16`

Facet classes:

- `ArchaeologicalFacet`
- `ArtisticFacet`
- `CulturalFacet`
- `DemographicFacet`
- `DiplomaticFacet`
- `EconomicFacet`
- `EnvironmentalFacet`
- `GeographicFacet`
- `IntellectualFacet`
- `LinguisticFacet`
- `MilitaryFacet`
- `PoliticalFacet`
- `ReligiousFacet`
- `ScientificFacet`
- `SocialFacet`
- `TechnologicalFacet`

## **D.4 Structural Contract**

```cypher
(:Claim)-[:HAS_FACET_ASSESSMENT]->(:FacetAssessment)-[:ASSESSES_FACET]->(:Facet)
(:Facet)-[:IN_FACET_CATEGORY]->(:FacetCategory)
```

## **D.5 Quality and Promotion Rules**

- Resolve anchor `qid` conflicts before promotion.
- Keep `facet_key` stable; evolve labels, not keys.
- Treat facet confidence as independent dimensions, not one global confidence.

---

**(End of Appendix D)**

---

# **Appendix E: Temporal Authority Alignment**

## **E.1 Scope**

Normative temporal modeling is in Section 3.4 and Section 4.3. This appendix is a reference index.

## **E.2 Authoritative Files**

- `Temporal/time_periods.csv`
- `Temporal/periodo-dataset.csv`
- `Temporal/period_classification_decisions.csv`
- `Temporal/PERIOD_CLASSIFICATION_PLAN.md`

## **E.3 Current Decision Snapshot**

From `Temporal/period_classification_decisions.csv` (`22` decisions):

- Tier 2 -> `convert_to_event`: `9`
- Tier 3 -> `delete`: `6`
- Tier 4 -> `delete`: `7`

## **E.4 Temporal Normalization Contract**

- Use ISO 8601 canonical storage (`-0049-01-01` for BCE).
- Preserve source-original date text and calendar system metadata.
- Separate historiographic periods from short event phases.

---

**(End of Appendix E)**

---

# **Appendix F: Geographic Authority Integration**

## **F.1 Scope**

Normative geographic federation logic is in Section 4.4. This appendix is the source and ingestion reference.

## **F.2 Authoritative Files**

- Raw authority snapshots: `Geographic/*.out`
- Curated registry: `Geographic/geographic_registry_master.csv`
- RDF references: `Geographic/ontology.rdf`, `Geographic/tgn_7011179-place.rdf`
- Consolidation note: `Geographic/GEOGRAPHIC_CONSOLIDATION_2026-02-12.md`

## **F.3 Curated Registry Snapshot**

From `Geographic/geographic_registry_master.csv`:

- Rows: `20`
- Facet assignments observed:
- `cultural_geographic`: 8
- `pure_spatial`: 3
- `political`: 2
- unassigned/blank: 7

## **F.4 Ingestion Rules**

1. Use authority place IDs (TGN/Pleiades/GeoNames) as atomic identifiers.
2. Keep historical names and modern names as separate properties.
3. Preserve hierarchy and containment relations independently of political regime naming.
4. Do not collapse culturally-defined regions into purely geometric regions.

---

**(End of Appendix F)**

---

# **Appendix G: Legacy Implementation Patterns**

## **G.1 Purpose**

Documents deprecated patterns to prevent accidental reintroduction.

## **G.2 Deprecated vs Current**

| Legacy Pattern | Problem | Current Pattern |
|---|---|---|
| Flat subject tagging without facets | No multidimensional analysis | Star-pattern facets with per-facet confidence |
| Treating short crises as periods | Temporal ambiguity | Period/Event distinction with classification workflow |
| Identifier handling through LLM prompts | Tokenization breakage | Two-stage: LLM labels -> tool ID resolution |
| Ad hoc relationship labels | Query fragmentation | Registry-first relationship governance |

## **G.3 Migration Note**

All new implementations should follow Sections 3-8 plus appendices A, B, D, and M.

---

**(End of Appendix G)**

---

# **Appendix H: Architectural Decision Records**

## **H.1 ADR Index**

| ADR | Title | Status | Primary Section |
|---|---|---|---|
| ADR-001 | Two-stage architecture (LLM extraction -> reasoning validation) | Adopted | 1.2.1 |
| ADR-002 | Structure vs topics separation (LCC vs FAST) | Adopted | 1.2.3 |
| ADR-003 | LCC as primary classification backbone | Adopted | 1.4.1 |
| ADR-004 | Two-level agent granularity (FAST + LCC) | Adopted | 1.4.2, 5.4 |
| ADR-005 | CIDOC-CRM foundation with Chrystallum extensions | Adopted | 1.2.4 |
| ADR-006 | Hybrid architecture: traversable entities + content-addressable claims | Adopted | 6.4 |
| ADR-007 | Calendar normalization for historical dates | Adopted | 1.4.3, 3.4 |

## **H.2 ADR-006 (Detailed)**

Decision:

- Entities remain traversal-first in Neo4j for exploratory graph analytics.
- Claims use content-addressable `cipher` identity for immutability, deduplication, and verification.

Why:

- Traversal and discovery are essential for entity-layer research questions.
- Claim verification and provenance integrity require immutable claim identity.

Consequence:

- Mixed architecture by design; each layer optimized for its function.

## **H.3 ADR-007 (Detailed)**

Decision:

- Store normalized canonical dates plus original source dates and calendar metadata.

Why:

- Prevent false contradiction from Julian/Gregorian mismatches.
- Preserve source fidelity while enabling deterministic timeline queries.

Consequence:

- Temporal ingestion requires normalization step before confidence scoring.

## **H.4 Primary ADR Sources**

- `md/Architecture/ONTOLOGY_PRINCIPLES.md`
- `md/Architecture/LCC_AGENT_ROUTING.md`
- `md/Architecture/Subject_Agent_Granularity_Strategy.md`
- `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md`
- `md/Architecture/Historical_Dating_Schema_Disambiguation.md`

---

**(End of Appendix H)**

---

# **Appendix I: Mathematical Formalization**

## **I.1 Confidence Components**

Source confidence:

```text
T_confidence = T_tier + delta_recency - delta_contradiction
```

Claim confidence (weighted by relevance):

```text
C_confidence = sum(T_confidence_i * relevance_i) / sum(relevance_i)
```

Facet enrichment score:

```text
FES = (facets_present / 16) * 100
```

## **I.2 Temporal Decay Function**

For time-sensitive claims:

```text
decay(t) = exp(-lambda * t)
```

Where:

- `t` = years since claim assertion or source timestamp
- `lambda` is domain-specific decay rate

## **I.3 Practical Bounds**

- Confidence values are bounded to `[0.0, 1.0]`.
- Contradiction penalties should never drive score below `0.0`.
- Use explicit null/unknown handling for missing components.

---

**(End of Appendix I)**

---

# **Appendix J: Implementation Examples**

## **J.1 Subject-Centric Retrieval**

```cypher
MATCH (s:SubjectConcept {fast_id: 'fst01204885'})<-[:HAS_SUBJECT_CONCEPT]-(e)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(c:Claim)
RETURN e.label AS entity, count(c) AS supporting_claims
ORDER BY supporting_claims DESC
LIMIT 50;
```

## **J.2 Claim Verification by Cipher**

```cypher
MATCH (c:Claim {cipher: $cipher})
OPTIONAL MATCH (c)<-[:REVIEWED]-(r:Review)
RETURN c.status, c.confidence, collect(r.verdict) AS verdicts;
```

## **J.3 Identifier-Safe Ingestion Skeleton**

```python
# Stage 1: LLM extracts natural-language labels
labels = extractor.extract(text)

# Stage 2: deterministic tools resolve identifiers
qid = wikidata.resolve(labels["entity_label"])
fast_id = fast.resolve(labels["subject_label"])

# Stage 3: persist both label and atomic IDs
record = {
    "label": labels["entity_label"],
    "qid": qid,
    "fast_id": fast_id,
}
```

## **J.4 Script Operations Reference**

- Script registry: `md/Reference/SCRIPT_REGISTRY_2026-02-13.md`
- Registry CSV: `md/Reference/SCRIPT_REGISTRY_2026-02-13.csv`

---

**(End of Appendix J)**

---

# **Appendix K: Wikidata Integration Patterns**

## **K.1 Scope**

Normative federation architecture is defined in Section 4.4 and Section 8.6. This appendix provides operational query patterns.

## **K.2 Authoritative Files**

- `md/Architecture/Wikidata_SPARQL_Patterns.md`
- `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`

## **K.3 Core SPARQL Patterns**

### Direct property bundle resolution

```sparql
SELECT ?lcsh ?fast ?lcc ?viaf ?tgn ?pleiades ?trismegistos WHERE {
  BIND(wd:Q1048 AS ?item)
  OPTIONAL { ?item wdt:P244  ?lcsh }
  OPTIONAL { ?item wdt:P2163 ?fast }
  OPTIONAL { ?item wdt:P1149 ?lcc }
  OPTIONAL { ?item wdt:P214  ?viaf }
  OPTIONAL { ?item wdt:P1667 ?tgn }
  OPTIONAL { ?item wdt:P1584 ?pleiades }
  OPTIONAL { ?item wdt:P1958 ?trismegistos }
}
```

### Backlink enrichment (reverse-link context expansion)

```sparql
SELECT ?source ?sourceLabel ?property ?propertyLabel WHERE {
  BIND(wd:Q1048 AS ?target)
  ?source ?property ?target .
  VALUES ?property { wdt:P710 wdt:P1441 wdt:P138 wdt:P112 }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 500
```

## **K.4 Pipeline Contract**

1. Resolve label -> QID.
2. Pull authority property bundle.
3. Optionally run backlink expansion for context discovery.
4. Classify results by source entity type (`P31`, bounded `P279`) and ingest with provenance.
5. Route every statement through the dispatcher (`datatype + value_type`).
6. Apply the temporal precision gate before temporal anchoring.
7. Apply the frontier eligibility guard before recursive expansion.
8. Quarantine unsupported or malformed statements with explicit reason.

## **K.5 Property Lookup Contract (Reference-Book Pattern)**

Chrystallum MUST NOT ingest the full Wikidata property universe as graph nodes for runtime reasoning.  
Use a tool-backed property catalog lookup pattern instead (local reference store + deterministic filtering).

### Authoritative lookup assets

- `Relationships/relationship_types_registry_master.csv` (approved canonical mappings first)
- `CSV/wikiPvalues.csv` (Wikidata property catalog)
- `scripts/tools/enrich_wikidata_properties_from_api.py` (optional metadata enrichment pass)
- `scripts/tools/generate_wikidata_property_candidates_from_catalog.py` (candidate generation)

### Required lookup sequence

1. Attempt exact canonical mapping from `relationship_types_registry_master.csv`.
2. If unmapped, query local property catalog (label + description + aliases).
3. Apply datatype gate before ranking candidates.
4. Rank candidates using label match + alias match + description overlap.
5. Auto-apply only if confidence threshold is met; otherwise emit review queue entry.

### Datatype gate (hard filter)

- Candidate datatype MUST be compatible with relationship semantics.
- Examples:
  - Person/group/place/event relations -> prefer `wikibase-item`
  - Date/time relations -> `time`
  - Numeric indicator relations -> `quantity`
  - Media/file relations -> `commonsMedia`
  - Identifier relations -> `external-id`

### Alias handling (`propertyAltLabels`)

- Parse `propertyAltLabels` as pipe-delimited (`|`), normalize casing/whitespace, de-duplicate.
- Score exact alias matches strongly (same as exact label-class signals).
- Use aliases only after datatype compatibility is satisfied.

### Safety rule

- No low-confidence property mappings may be written directly to canonical registry.
- Low-confidence results MUST be written to review backlog and human-approved first.
- Identifier handling constraints in Appendix M still apply (tool resolution only, no LLM free-form ID generation).

## **K.6 Dispatcher and Backlink Operations**

Canonical scripts:
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`

Canonical report location:
- `JSON/wikidata/backlinks/`

Required report fields (minimum):
- `route_counts`
- `quarantine_reasons`
- `unsupported_pair_rate`
- `unresolved_class_rate`
- `frontier_eligible`
- `frontier_excluded`

---

**(End of Appendix K)**

---

# **Appendix L: CIDOC-CRM Integration Guide**

## **L.1 Scope**

Defines triple alignment approach: Chrystallum relation type <-> Wikidata property <-> CIDOC-CRM property/class.

## **L.2 Authoritative Files**

- `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md`
- `md/Architecture/CIDOC-CRM_Alignment_Summary.md`
- `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`

## **L.3 High-Value Mappings**

| Chrystallum | Wikidata | CIDOC-CRM |
|---|---|---|
| `PARTICIPATED_IN` | `P710` | `P11_had_participant` |
| `LOCATED_IN` | `P131` | `P7_took_place_at` |
| `PART_OF` | n/a | `P86_falls_within` |
| `CAUSED` | `P828` | `P15_was_influenced_by` |
| `AUTHOR` | `P50` | `P14_carried_out_by` via `E12_Production` |

## **L.4 Entity Class Alignment**

| Chrystallum Node | CIDOC-CRM Class |
|---|---|
| Event | `E5_Event` |
| Human | `E21_Person` |
| Place | `E53_Place` |
| Organization | `E74_Group` / `E40_Legal_Body` |
| TimeSpan | `E52_Time-Span` |

## **L.5 Implementation Rule**

CIDOC-CRM alignment is additive. Chrystallum-specific capabilities (library backbones, action-structure vocabularies, identifier safety) remain first-class and are not dropped for standards compatibility.

---

**(End of Appendix L)**

---

# **Appendix M: Identifier Safety Reference**

## **M.1 Core Rule**

Never pass atomic identifiers to LLMs for interpretation.

Use two-stage processing:

1. LLM extracts natural language labels.
2. Deterministic tools resolve and validate identifiers.

## **M.2 Decision Table**

| Input Type | Example | LLM-safe | Handling |
|---|---|---|---|
| Natural-language label | `Roman Republic` | Yes | LLM extraction/classification |
| Wikidata QID | `Q17193` | No | Tool lookup only |
| FAST ID | `1145002` | No | Tool lookup only |
| LCC code | `DG241-269` | No | Tool lookup only |
| MARC authority ID | `sh85115058` | No | Tool lookup only |
| Pleiades ID | `423025` | No | Tool lookup only |
| ISO date with negative year | `-0509-01-01` | No | Store/format with temporal tool |

## **M.3 Authoritative References**

- `md/Reference/IDENTIFIER_ATOMICITY_AUDIT.md`
- `md/Reference/IDENTIFIER_CHEAT_SHEET.md`
- Section 8.5 in this architecture document

## **M.4 Pre-Prompt Validation Checklist**

Before any LLM call:

- remove QIDs and catalog IDs
- replace with human-readable labels
- keep numeric/scalar fields only when they are true numeric values
- run identifier validator where available

---

**(End of Appendix M)**

---

# **Appendix N: Property Extensions and Advanced Attributes**

## **N.1 Purpose**

Defines optional-but-supported extension properties that enrich entities without breaking base schema compatibility.

## **N.2 Authoritative Files**

- `md/Reference/Entity_Property_Extensions.md`
- `md/Reference/Property_Extensions_Implementation_Guide.md`
- `md/Reference/Property_Extensions_Summary.md`

## **N.3 Extension Groups**

### Place Extensions

- `geo_coordinates`
- `pleiades_id`, `pleiades_link`
- `google_earth_link`
- optional geometry payload (`geo_json`)

### Temporal Extensions

- `end_date`
- `date_precision`
- `temporal_uncertainty`

### Backbone Extensions

- `backbone_fast`
- `backbone_lcc`
- `backbone_lcsh`
- `backbone_marc`

### Person/Work Discovery Extensions

- image metadata (`image_url`, `image_source`, `image_license`)
- related works arrays (`related_fiction`, `related_art`, `related_nonfiction`)
- online text availability metadata

## **N.4 Validation Rules**

1. Extension properties must not replace core required properties.
2. Keep external IDs as atomic strings.
3. Validate URL and coordinate formats before write.
4. Treat extension blocks as forward-compatible optional schema.

## **N.5 Recommended Rollout**

- Phase 1: temporal and backbone extensions
- Phase 2: geographic extension enrichment
- Phase 3: person/work media and online text extensions

---

**(End of Appendix N)**

---

# **Appendix O: Facet Training Resources Registry**

## **O.1 Purpose**

Defines curated discipline-specific resources for **SubjectFacetAgent (SFA) training initialization**. These resources serve as **discipline roots** for building SubjectConcept hierarchies via BROADER_THAN relationships.

**Integration Point:** Step 5 Discipline Root Detection uses Priority 1 resources to mark `discipline=true` flags in Neo4j.

## **O.2 Authority Schema**

Each resource includes:
- **name**: Human-readable resource title
- **role**: Resource function (discipline_reference, bibliographic_index, curated_portal, etc.)
- **priority**: 1 (Tier 1 discipline anchor) or 2 (Tier 2 methodological pattern)
- **access**: "open" (freely available) or "subscription" (institutional access)
- **url**: Direct link or gateway URL
- **notes**: Contextual guidance for SFA training bootstrap

## **O.3 Priority Tier System**

**Priority 1 (Tier 1 Discipline Anchors):**
- Standard discipline references (Stanford Encyclopedia, Oxford References)
- Comprehensive bibliographic indexes (Historical Abstracts, Linguistic Bibliography)
- Empirical data portals (Economic History Society datasets)
- **Action**: Create SubjectConcept nodes with `discipline=true` flag
- **Query Pattern**: `WHERE discipline=true AND facet=TARGET_FACET`

**Priority 2 (Tier 2 Methodological Patterns):**
- Curated secondary sources (Norwich Military History, Zinn Education Project)
- Pedagogical syllabi (Stanford OHS)
- Primary source methodology templates (Robin Bernstein model)
- **Action**: Use for narrative patterns and case study methodologies

## **O.4 Canonical 17 Facet Registry**

### POLITICAL
- **Tier 1**: Stanford Encyclopedia of Philosophy – Political Philosophy (open)
- **Tier 1**: Historical Abstracts (political history) (subscription)

### MILITARY
- **Tier 2**: Norwich University – Military History Websites (open)
- **Tier 1**: Historical Abstracts (military history) (subscription)

### ECONOMIC
- **Tier 1**: Economic History Society – Online Resources (open) — PRIMARY discipline portal
- **Tier 2**: VoxEU – Economic History & Macrohistory (open)

### CULTURAL
- **Tier 2**: Primary Sources in U.S. Cultural History – Robin Bernstein (open) — narrative template
- **Tier 1**: Historical Abstracts (cultural history) (subscription)

### RELIGIOUS
- **Tier 1**: Theology and Religion Online (Bloomsbury) (subscription)
- **Tier 1**: Oxford Reference – Religion/Theology (subscription)

### SOCIAL
- **Tier 1**: Economic History Society – labour/demography resources (open)
- **Tier 2**: Zinn Education Project – Teaching People's History (open)

### DEMOGRAPHIC
- **Tier 1**: Economic History Society – demographic datasets (open) — quantitative anchor

### INTELLECTUAL
- **Tier 1**: Stanford Encyclopedia of Philosophy – HPS & related (open)
- **Tier 2**: History & Philosophy of Science – Stanford OHS (open)

### SCIENTIFIC
- **Tier 1**: Stanford Encyclopedia of Philosophy – Science entries (open)

### TECHNOLOGICAL
- **Tier 1**: Economic History Society – industrialization/technology (open)
- **Tier 1**: Historical Abstracts (history of technology) (subscription)

### LINGUISTIC
- **Tier 1**: Library of Congress – Linguistics Electronic Resources (open)
- **Tier 1**: Linguistic Bibliography Online (subscription)

### GEOGRAPHIC
- **Tier 2**: LOC – Environmental History (maps & place framing) (open)

### ENVIRONMENTAL
- **Tier 2**: LOC – Environmental History Classroom Materials (open)
- **Tier 1**: Economic History Society – climate/resource-related (open)

### ARCHAEOLOGICAL
- **Tier 2**: Archaeology: Reference Materials – COD Library (open)
- **Tier 1**: Oxford Encyclopedia/Companion to Archaeology (subscription)

### DIPLOMATIC
- **Tier 1**: Historical Abstracts – diplomatic history (subscription)
- **Tier 2**: Norwich Military History guide (treaties/foreign policy) (open)

### ARTISTIC
- **Tier 1**: Oxford Art Online / Grove Art (subscription)
- **Tier 2**: Primary Sources in Cultural History – visual culture pattern (open)

### COMMUNICATION
- **Tier 2**: Zinn Education Project – rhetoric & narrative framing (open)
- **Tier 2**: Cultural/political primary-source portals (pattern) (open)

## **O.5 SFA Initialization Workflow**

**Step 1: Load Facet Resources**
```python
def load_facet_resources(facet: str) -> List[Dict]:
    """Load Priority 1 & 2 resources for target facet."""
    resources = parse_yaml("Facets/TrainingResources.yml")
    return resources[facet.upper()]
```

**Step 2: Seed Discipline Roots (Priority 1 only)**
```cypher
// Create discipline root SubjectConcepts
MERGE (sc:SubjectConcept {
  label: "Political Philosophy",  // from Stanford Encyclopedia
  facet: "POLITICAL",
  authority_id: "sh85104440",  // LCSH if available
  discipline: true  // DISCIPLINE FLAG
})
```

**Step 3: Query Discipline Roots for Training**
```cypher
// SFA initialization query
MATCH (root:SubjectConcept)
WHERE root.discipline = true 
  AND root.facet = "POLITICAL"
MATCH (root)-[:BROADER_THAN*]->(narrower:SubjectConcept)
RETURN root, narrower
```

**Step 4: Expand Hierarchy via BROADER_THAN**
- Use Wikidata P279 (subclass of) traversal
- Build BROADER_THAN edges from discipline roots downward
- Validate against LCSH/FAST authority hierarchies (Tier 1 authorities)

## **O.6 Authority Precedence Integration**

When enriching discipline roots with multi-authority metadata:

**Tier 1 Search (LCSH/FAST):**
```cypher
MATCH (root:SubjectConcept {discipline: true})
WHERE root.authority_id IS NULL
// Enrich with LCSH first, then FAST
CALL lcsh.lookup(root.label) YIELD authority_id, fast_id
SET root.authority_id = authority_id, root.fast_id = fast_id
```

**Tier 2 Fallback (LCC/CIP):**
```cypher
MATCH (root:SubjectConcept {discipline: true})
WHERE root.authority_id IS NULL AND root.fast_id IS NULL
// Fallback to LCC classification
CALL lcc.classify(root.label) YIELD lcc_code
SET root.backbone_lcc = lcc_code
```

**Tier 3 Fallback (Wikidata/Other):**
```cypher
MATCH (root:SubjectConcept {discipline: true})
WHERE root.authority_id IS NULL AND root.fast_id IS NULL
// Last resort: Wikidata QID lookup
CALL wikidata.search(root.label) YIELD qid
SET root.wikidata_qid = qid
```

## **O.7 Authoritative Source File**

- **File**: `Facets/TrainingResources.yml`
- **Version**: 2.0 (2026-02-16)
- **Maintenance**: Update when adding new facet training pipelines

## **O.8 Related Sections**

- **Step 5 Discipline Root Detection algorithm**
- **Appendix D**: Subject Facet Classification (17 canonical facets)
- **Section 4.4**: Multi-Authority Model (Tier 1/2/3 precedence)
- **Section 4.9**: Academic Discipline Model (discipline flag usage)

---

**(End of Appendix O)**

---

# **Appendix P: Semantic Enrichment & Ontology Alignment (CIDOC-CRM/CRMinf)**

## **P.1 Purpose**

Implements automatic **CIDOC-CRM and CRMinf ontology alignment** for all entities and claims in the Chrystallum knowledge graph. This provides:

- **Triple alignment**: Chrystallum ↔ Wikidata ↔ CIDOC-CRM
- **Cultural heritage interoperability** (CIDOC-CRM ISO 21127 standard)
- **Belief tracking** with CRMinf argumentation ontology
- **Semantic web compatibility** for RDF/OWL export

Every SubjectConcept node and Claim includes ontology alignment metadata alongside its Wikidata QID, enabling multi-ontology queries and museum/archive data exchange.

**Implementation Status:** ✅ Complete (Step 4, 2026-02-15)
**Source:** ~250 lines added to `scripts/agents/facet_agent_framework.py`

---

## **P.2 CIDOC-CRM Entity Mappings**

**Source:** `CIDOC/cidoc_wikidata_mapping_validated.csv` (105 validated mappings)

### **P.2.1 Key Entity Class Mappings**

| Wikidata QID | Description | CIDOC-CRM Class | Confidence |
|-------------|-------------|-----------------|------------|
| **Q5** | human | **E21_Person** | High |
| **Q1656682** | event | **E5_Event** | High |
| **Q178561** | battle | **E5_Event** | High |
| **Q82794** | geographic region | **E53_Place** | High |
| **Q515** | city | **E53_Place** | High |
| **Q43229** | organization | **E74_Group** | High |
| **Q7252** | cultural heritage | **E22_Man-Made_Object** | Medium |
| **Q273057** | discourse | **E28_Conceptual_Object** | Medium |

### **P.2.2 Key Property Mappings**

| Wikidata Prop | Description | CIDOC-CRM Prop | Confidence |
|--------------|-------------|----------------|------------|
| **P31** | instance of | **P2_has_type** | High |
| **P279** | subclass of | **P127_has_broader_term** | High |
| **P276** | location | **P7_took_place_at** | High |
| **P710** | participant | **P11_had_participant** | High |
| **P580** | start time | **P82a_begin_of_the_begin** | High |
| **P582** | end time | **P82b_end_of_the_end** | High |
| **P131** | located in admin territory | **P89_falls_within** | High |
| **P361** | part of | **P106_is_composed_of** (inverse) | Medium |

---

## **P.3 CRMinf Belief Tracking**

**CRMinf Ontology:** Argumentation and reasoning extension to CIDOC-CRM

### **P.3.1 Core Mappings**

| CRMinf Class/Property | Chrystallum Mapping | Usage |
|----------------------|---------------------|-------|
| **I2_Belief** | Claim node | Core belief held by agent |
| **J4_that** | Claim.label | The proposition (text) |
| **J5_holds_to_be** | Claim.confidence | Belief value 0.0-1.0 |
| **I4_Proposition_Set** | Related claim cluster | Multi-agent debate |
| **I5_Inference_Making** | Bayesian update | When posterior_probability exists |
| **I6_Belief_Value** | Confidence tiers | Layer-based authority |

### **P.3.2 Claim Storage Format**

**Example Claim with CRMinf Alignment:**

```python
{
  "label": "Battle of Pharsalus occurred on August 9, 48 BCE",
  "confidence": 0.90,
  "authority_source": "Wikidata",
  "authority_ids": {
    "source_qid": "Q28048",
    "property": "P585",
    "target_value": "48 BCE-08-09"
  },
  "facet": "military",
  "crminf_alignment": {
    "crminf_class": "I2_Belief",
    "J4_that": "Battle of Pharsalus occurred on August 9, 48 BCE",
    "J5_holds_to_be": 0.90,
    "source_agent": "military_facet",
    "facet": "military",
    "rationale": "From Wikidata property P585 (point in time)",
    "inference_method": "wikidata_federation",
    "timestamp": "2026-02-15T12:00:00Z"
  }
}
```

**Interpretation:**
- Belief (I2_Belief) held by military_facet agent
- Proposition (J4_that) is textual claim
- Agent holds with 0.90 confidence (J5_holds_to_be)
- Formed via wikidata_federation (trusted external source)

---

## **P.4 Authority Precedence Integration**

**Integration:** Step 4-5 commit (d56fc0e) integrates multi-tier authority checking with ontology enrichment.

### **P.4.1 Multi-Tier Authority Policy**

**Authority Tier Policy (from §4.4):**
```
Tier 1 (Preferred): LCSH, FAST               (domain-optimized for historical subjects)
Tier 2 (Secondary): LCC, CIP                 (structural backbone + academic alignment)
Tier 3 (Tertiary):  Wikidata, Dewey, VIAF   (fallback authorities)
```

### **P.4.2 Enhanced Enrichment Algorithm**

**Pseudo-code for Multi-Authority Node Enrichment:**

```python
def enrich_node_with_authorities(entity_qid):
    """
    Enrich SubjectConcept node with multi-authority IDs (Tier 1/2/3)
    + CIDOC-CRM ontology alignment
    """
    node = {'qid': entity_qid}
    
    # STEP 1: Fetch Wikidata data
    wikidata_data = fetch_wikidata_entity(entity_qid)
    
    # STEP 2: Extract Tier 1 authorities from Wikidata (if available)
    lcsh_id = wikidata_data.get('P244')      # Library of Congress authority ID
    fast_id = wikidata_data.get('special:fast_id')  # FAST derived from LCSH
    
    if lcsh_id:
        node['authority_id'] = lcsh_id          # ← Tier 1 primary
        node['authority_tier'] = 1
    
    if fast_id:
        node['fast_id'] = fast_id                # ← Tier 1 secondary
    
    # STEP 3: If no Tier 1, check Tier 2 (LCC)
    if not lcsh_id:
        lcc_mapping = lookup_lcc_for_qid(entity_qid)
        if lcc_mapping:
            node['lcc_class'] = lcc_mapping['class']
            node['authority_tier'] = 2
    
    # STEP 4: Always include Wikidata (Tier 3 fallback)
    node['wikidata_qid'] = entity_qid
    node['qid_tier'] = 3
    
    # STEP 5: Add CIDOC-CRM alignment (orthogonal to authorities)
    cidoc_enrichment = enrich_with_ontology_alignment(wikidata_data)
    node['cidoc_crm_class'] = cidoc_enrichment['cidoc_crm_class']
    node['cidoc_crm_confidence'] = cidoc_enrichment['cidoc_crm_confidence']
    
    return node
```

**Result Node Structure:**

```python
{
    'authority_id': 'sh85115055',           # Tier 1: LCSH (preferred)
    'authority_tier': 1,
    'fast_id': 'fst01234567',              # Tier 1: FAST (complementary)
    'wikidata_qid': 'Q12107',              # Tier 3: Wikidata fallback
    'qid_tier': 3,
    'cidoc_crm_class': 'E5_Event',         # Orthogonal semantic alignment
    'cidoc_crm_confidence': 'High',
    'label': 'Roman politics'
}
```

### **P.4.3 Query Examples**

**Before Multi-Authority (Wikidata Only):**

```cypher
// Single authority source
MATCH (n:SubjectConcept {wikidata_qid: 'Q12107'})
RETURN n
```

**After Multi-Authority Integration:**

```cypher
// Multi-authority aware query with tier preference
MATCH (n:SubjectConcept)
WHERE n.authority_id = 'sh85115055'        // LCSH preferred
   OR n.fast_id = 'fst01234567'            // FAST complementary
   OR n.wikidata_qid = 'Q12107'            // Fallback
ORDER BY COALESCE(n.authority_tier, 3)     // Tier 1 results first
RETURN n
```

**Query by CIDOC Class:**

```cypher
// Find all E21_Person entities (humans)
MATCH (n:SubjectConcept {cidoc_crm_class: 'E21_Person'})
RETURN n.label, n.wikidata_qid, n.authority_id
LIMIT 10

// Find all E5_Event entities (battles, conflicts)
MATCH (n:SubjectConcept {cidoc_crm_class: 'E5_Event'})
WHERE n.label CONTAINS 'Battle'
RETURN n.label, n.wikidata_qid
LIMIT 10
```

### **P.4.4 Data Audit Query**

**Check Authority Coverage:**

```cypher
// Authority coverage statistics
MATCH (n:SubjectConcept)
RETURN 
    count(CASE WHEN n.authority_id IS NOT NULL THEN 1 END) as lcsh_count,
    count(CASE WHEN n.fast_id IS NOT NULL THEN 1 END) as fast_count,
    count(CASE WHEN n.wikidata_qid IS NOT NULL THEN 1 END) as wikidata_count,
    count(CASE WHEN n.cidoc_crm_class IS NOT NULL THEN 1 END) as cidoc_count,
    count(n) as total
```

**Rationale:**
- LCSH/FAST domain-optimized for historical scholarship; reduces federation friction
- Multi-authority storage enables library catalog interoperability
- Tier hierarchy prevents dependency lock on Wikidata
- CIDOC-CRM stays orthogonal to authority tier system

---

## **P.5 Implementation Methods**

**Added to:** `scripts/agents/facet_agent_framework.py` (~250 lines)

### **P.5.1 Method Signatures**

**1. Load CIDOC Crosswalk (~80 lines)**

```python
def _load_cidoc_crosswalk(self) -> Dict:
    """
    Load and parse CIDOC/Wikidata/CRMinf mappings from CSV.
    
    Source: CIDOC/cidoc_wikidata_mapping_validated.csv (105 mappings)
    Caching: Loads once per agent instance → self._cached_cidoc_crosswalk
    
    Returns:
        {
            'cidoc_by_qid': {
                'Q5': {'cidoc_class': 'E21_Person', 'confidence': 'High'},
                'Q1656682': {'cidoc_class': 'E5_Event', 'confidence': 'High'},
                ...
            },
            'cidoc_by_property': {
                'P710': {'cidoc_property': 'P11_had_participant', 'confidence': 'High'},
                'P276': {'cidoc_property': 'P7_took_place_at', 'confidence': 'High'},
                ...
            },
            'crminf_mappings': {
                'I2_Belief': 'Chrystallum Claim node',
                'J4_that': 'Claim.label (proposition)',
                'J5_holds_to_be': 'Claim.confidence (belief value)',
                ...
            }
        }
    """
```

**2. Enrich with Ontology Alignment (~90 lines)**

```python
def enrich_with_ontology_alignment(self, entity: Dict) -> Dict:
    """
    Add CIDOC-CRM classes and properties to Wikidata entity.
    
    Args:
        entity: Entity dict from fetch_wikidata_entity() or similar
        
    Process:
        1. Look up CIDOC class via P31 (instance of) QID
        2. Map entity properties to CIDOC properties
        3. Generate semantic triples (QID+Property+Value+CIDOC)
        4. Add ontology_alignment section to entity
        
    Returns:
        Enriched entity with ontology_alignment section:
        {
            ...existing entity data...,
            'ontology_alignment': {
                'cidoc_crm_class': 'E5_Event',
                'cidoc_crm_confidence': 'High',
                'cidoc_properties': [...],
                'semantic_triples': [...]
            }
        }
    """
```

**3. Enrich Claim with CRMinf (~60 lines)**

```python
def enrich_claim_with_crminf(self, claim: Dict, belief_value: float = 0.90) -> Dict:
    """
    Add CRMinf belief tracking metadata to Chrystallum Claim.
    
    Args:
        claim: Claim dict from generate_claims_from_wikidata() or agent reasoning
        belief_value: Confidence level (default 0.90)
        
    CRMinf Mapping:
        - Claim → I2_Belief (belief held by agent)
        - Claim.label → J4_that (proposition)
        - Claim.confidence → J5_holds_to_be (belief value 0.0-1.0)
        - Bayesian update → I5_Inference_Making (reasoning process)
        
    Returns:
        Enriched claim with crminf_alignment section:
        {
            ...existing claim data...,
            'crminf_alignment': {
                'crminf_class': 'I2_Belief',
                'J4_that': '...',
                'J5_holds_to_be': 0.90,
                'source_agent': '...',
                'inference_method': '...',
                'timestamp': '...'
            }
        }
    """
```

**4. Generate Semantic Triples (~70 lines)**

```python
def generate_semantic_triples(
    self, 
    entity_qid: str, 
    include_cidoc: bool = True, 
    include_crminf: bool = False
) -> List[Dict]:
    """
    Generate complete semantic triples for RDF/OWL export or validation.
    
    Args:
        entity_qid: Entity QID (must be in graph or fetchable from Wikidata)
        include_cidoc: Add CIDOC-CRM alignment to each triple
        include_crminf: Add CRMinf belief tracking (for claims)
        
    Returns:
        List of fully-aligned semantic triples:
        [
            {
                'subject': 'Q28048',
                'subject_label': 'Battle of Pharsalus',
                'subject_cidoc': 'E5_Event',
                'property': 'P276',
                'property_label': 'location',
                'property_cidoc': 'P7_took_place_at',
                'value': 'Q240898',
                'value_label': 'Pharsalus',
                'value_cidoc': 'E53_Place',
                'confidence': 0.90,
                'crminf_belief': {...}  # if include_crminf=True
            }
        ]
    """
```

---

## **P.6 Semantic Triple Generation**

### **P.6.1 Example Output Structure**

**Query:** `generate_semantic_triples('Q28048', include_cidoc=True, include_crminf=True)`

**Output:**

```python
[
    {
        # Subject (entity)
        "subject": "Q28048",
        "subject_label": "Battle of Pharsalus",
        "subject_cidoc": "E5_Event",
        
        # Predicate (relationship)
        "property": "P276",
        "property_label": "location",
        "property_cidoc": "P7_took_place_at",
        
        # Object (target entity or literal)
        "value": "Q240898",
        "value_label": "Pharsalus",
        "value_cidoc": "E53_Place",
        
        # Provenance & belief tracking
        "confidence": 0.90,
        "crminf_belief": {
            "class": "I2_Belief",
            "J4_that": "Battle of Pharsalus took place at Pharsalus",
            "J5_holds_to_be": 0.90,
            "source": "Wikidata",
            "inference_method": "wikidata_federation"
        }
    }
]
```

### **P.6.2 Use Cases**

1. **RDF/OWL Export**: Convert to Turtle, RDF-XML, JSON-LD for semantic web
2. **CIDOC-CRM Validation**: Check if triple conforms to CIDOC constraints
3. **Museum Systems**: Export to collection management systems (CollectionSpace, TMS)
4. **SPARQL Queries**: Enable federated queries across Wikidata + Chrystallum + CIDOC repositories

---

## **P.7 Source Files**

### **P.7.1 Primary Implementation**

- **File:** `scripts/agents/facet_agent_framework.py`
- **Lines Added:** ~250 (4 methods)
- **Version:** 2026-02-15-step4

### **P.7.2 CIDOC Crosswalk Data**

- **File:** `CIDOC/cidoc_wikidata_mapping_validated.csv`
- **Mappings:** 105 validated entity/property mappings
- **Confidence Levels:** High, Medium, Low

### **P.7.3 System Prompts Update**

- **File:** `facet_agent_system_prompts.json`
- **Version:** 2026-02-15-step4
- **Content:** Added "SEMANTIC ENRICHMENT & ONTOLOGY ALIGNMENT" section to all 17 facets

### **P.7.4 Workflow Integration**

**Modified Methods:**
- `enrich_node_from_wikidata()` (lines ~751-840): Auto-enrichment in node creation
- `generate_claims_from_wikidata()` (lines ~928-1080): Auto-enrichment in claim generation

**Node Storage Format:**

```cypher
CREATE (n:SubjectConcept {
  id: 'wiki:Q28048',
  label: 'Battle of Pharsalus',
  wikidata_qid: 'Q28048',
  cidoc_crm_class: 'E5_Event',         // ← NEW (Step 4)
  cidoc_crm_confidence: 'High',        // ← NEW (Step 4)
  authority_tier: 2,
  confidence_floor: 0.90,
  created_at: '2026-02-15T...',
  created_by: 'military_facet'
})
```

---

## **P.8 Related Sections**

### **P.8.1 Internal Cross-References**

- **Appendix L**: CIDOC-CRM Integration Guide (foundational ontology overview)
- **Section 4.4**: Multi-Authority Model (Tier 1/2/3 precedence policy)
- **Section 4.9**: Academic Discipline Model (discipline flag usage)
- **Appendix K**: Wikidata Integration Patterns (federation discovery)
- **Section 6.4**: Claims Generation (CRMinf belief tracking integration)

### **P.8.2 Integration Points**

**Step 1 (Architecture Understanding):**
- `enrich_with_ontology_alignment()` uses `introspect_node_label()` for entity type validation

**Step 2 (State Introspection):**
- `get_session_context()` includes CIDOC alignment status
- `get_node_provenance()` shows ontology mapping history

**Step 3 (Federation Discovery):**
- `bootstrap_from_qid()` automatically calls enrichment methods
- `discover_hierarchy_from_entity()` maintains CIDOC alignment through hierarchy traversal

**Step 3.5 (Completeness Validation):**
- `validate_entity_completeness()` uses CIDOC class for type inference
- Property patterns validate against both Wikidata and CIDOC constraints

### **P.8.3 Benefits & Impact**

**Cultural Heritage Interoperability:**
- CIDOC-CRM ISO 21127 alignment enables data exchange with museum systems
- Compatible with: CollectionSpace, TMS, Arches, ResearchSpace

**Semantic Web Integration:**
- RDF/OWL export via semantic triples
- SPARQL queries across Wikidata, Chrystallum, and CIDOC endpoints
- Linked Open Data (LOD) publishing capability

**Argumentation & Belief Tracking:**
- CRMinf ontology models agent reasoning and confidence
- Multi-agent debate tracking with I4_Proposition_Set
- Bayesian updates tracked via I5_Inference_Making

**Multi-Ontology Querying:**
- Query by Wikidata (Q5, P31, etc.)
- Query by CIDOC-CRM (E21_Person, P7_took_place_at)
- Query by Chrystallum (SubjectConcept, INSTANCE_OF)
- Cross-ontology validation ensures consistency

---

**(End of Appendix P)**

---

# **Appendix Q: Operational Modes & Agent Orchestration**

**Version:** 2026-02-16  
**Status:** Operational (Initialize, Subject Ontology Proposal, Training modes implemented)  
**Source:** STEP_5_COMPLETE.md

---

## **Q.1 Purpose**

This appendix defines how agents operate in different contexts within the Chrystallum system. Unlike Steps 1-4 (which provide capabilities), Step 5 operational modes define **how agents work** with verbose logging for validation. Operational modes bridge the gap between agent capabilities and user workflows, supporting everything from initial domain bootstrapping to cross-domain query synthesis.

**Key Operational Modes:**
- **Initialize Mode:** Bootstrap new domain from Wikidata anchor
- **Subject Ontology Proposal:** Analyze hierarchies and propose domain ontology
- **Training Mode:** Extended iterative claim generation with validation
- **Schema Query Mode:** Answer questions about Neo4j model structure (design complete)
- **Data Query Mode:** Answer questions about actual graph data (design complete)
- **Wikipedia Training Mode:** LLM-driven article discovery (in design)

**Cross-Domain Orchestration:**
- **SubjectConceptAgent (SCA):** Master coordinator for multi-facet queries and bridge concept discovery

---

## **Q.2 SubjectConceptAgent (SCA) Two-Phase Architecture**

The **SubjectConceptAgent** is a **SEED AGENT** with **TWO DISTINCT PHASES** that operates differently from domain-specific SubjectFacetAgents (SFAs):

### **Q.2.1 Phase 1: Un-Faceted Exploration**

**Scope:** Initialize Mode + Subject Ontology Proposal  
**Goal:** Broad discovery without facet constraints

**Characteristics:**
- **No facet lens** - Just hunting nodes and edges across all domains
- **Trawls hierarchies broadly** via P31 (instance_of), P279 (subclass_of), P361 (part_of) traversal
- **Goes beyond initial domain** - military → politics → culture → science
- **Creates shell nodes** for ALL discovered concepts (lightweight placeholders)
- **"Purple to mollusk" scenarios** - discovers seemingly unrelated cross-domain connections
- **Outputs proposed ontology** → APPROVAL POINT before facet analysis begins

**Example Discovery Path:**
```
Roman Republic (military anchor)
  → Roman Senate (political structure)
    → Senator rank (political hierarchy)
      → Toga praetexta (cultural artifact)
        → Tyrian purple dye (material culture)
          → Murex snail (scientific taxonomy)
```

**Data Created:**
- Shell SubjectConcept nodes with basic properties
- Hierarchical relationships (BROADER_THAN, INSTANCE_OF, PART_OF)
- Wikidata QID federation links
- Authority alignments (FAST, LCSH where available)

---

### **Q.2.2 Phase 2: Facet-by-Facet Analysis**

**Scope:** Training Mode  
**Goal:** Deep analysis through sequential facet lenses

**Characteristics:**
- **SCA adopts facet roles sequentially** - one facet at a time
- Reads claims from MILITARY perspective → then POLITICAL → then CULTURAL, etc.
- **Same nodes/edges analyzed through different facet lenses**
- Generates facet-specific claims and insights
- Uses proposed ontology from Phase 1 to prioritize nodes

**Process:**
```python
# Pseudo-code for Phase 2
for facet in ['MILITARY', 'POLITICAL', 'ECONOMIC', ...]:
    sca.set_facet_context(facet)
    for node in shell_nodes_from_phase1:
        if node.relevant_to(facet):
            claims = sca.generate_claims_with_facet_lens(node, facet)
            sca.enrich_node_with_facet_properties(node, facet, claims)
```

**Example Multi-Facet Analysis:**

Node: "Tyrian purple dye"

- **MILITARY facet:** "Used to mark senatorial authority in military contexts"
- **POLITICAL facet:** "Symbol of senatorial rank and imperium"
- **ECONOMIC facet:** "Luxury trade good, monopolized by elites"
- **CULTURAL facet:** "Status symbol in Roman dress codes"
- **SCIENTIFIC facet:** "Extracted from Murex brandaris mollusks"

**Architecture Diagram:**
```
┌─────────────────────────────────────────────┐
│      SubjectConceptAgent (SCA)              │
│      Master Coordinator                     │
│                                             │
│  • Facet classification (LLM)              │
│  • Multi-agent orchestration               │
│  • Bridge concept discovery                │
│  • Cross-domain synthesis                  │
└──────────────┬──────────────────────────────┘
               │
               │ Spawns & coordinates
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│ Military │      │Political │ ...  │ Biology  │
│   SFA    │      │   SFA    │      │   SFA    │
└──────────┘      └──────────┘      └──────────┘
```

---

## **Q.3 Canonical 17 Facets (UPPERCASE Keys)**

**Definitive List:**
```
ARCHAEOLOGICAL, ARTISTIC, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, 
ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, 
RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL, COMMUNICATION
```

### **Q.3.1 Facet Key Normalization Rule**

**Policy (from commit d56fc0e):**
- All facet identifiers MUST be UPPERCASE
- SCA facet classification outputs UPPERCASE keys: `facets=['POLITICAL', 'MILITARY', 'ECONOMIC']`
- SubjectConcept.facet property = UPPERCASE (prevents case-collision bugs)
- Query filters: `WHERE n.facet IN ["POLITICAL", "MILITARY", ...]` (uppercase only)

**Rationale:**
- **Deterministic routing:** Prevents case-sensitive routing errors
- **Union-safe deduplication:** `['Military', 'MILITARY', 'military']` → `['MILITARY']`
- **Consistent with registry:** facet_registry_master.json uses UPPERCASE canonical keys

**Enforcement Points:**
```python
# Classification normalization
def classify_facets(query):
    llm_output = llm.invoke(query)  # may return mixed case
    return [f.upper() for f in llm_output['facets']]  # normalized

# Node creation
def create_subject_concept(label, facet):
    node = SubjectConcept(label=label, facet=facet.upper())

# Query filter
query = """
MATCH (n:SubjectConcept)
WHERE n.facet IN ["POLITICAL", "MILITARY"]  // UPPERCASE only
RETURN n
"""
```

---

## **Q.4 Operational Modes**

### **Q.4.1 Initialize Mode**

**Method:** `execute_initialize_mode(anchor_qid, depth, auto_submit_claims, ui_callback)`

**Purpose:** Bootstrap new domain from a Wikidata anchor entity.

**Workflow:**
1. Generate unique session ID
2. Fetch Wikidata anchor entity (Step 3)
3. Validate completeness (Step 3.5) - reject if <60%
4. Enrich with CIDOC-CRM (Step 4)
5. **Enrich with authority precedence** (LCSH/FAST before Wikidata) ← NEW
6. Bootstrap from QID (Step 3) - creates nodes + discovers hierarchy
7. **Detect discipline roots** for 17 facets ← NEW (see Q.5)
8. Generate foundational claims
9. Optionally auto-submit high-confidence claims (≥0.90)
10. Log all actions verbosely
11. Return comprehensive result dict

**Parameters:**
- `anchor_qid`: Wikidata QID to bootstrap from (e.g., 'Q17167' for Roman Republic)
- `depth`: Hierarchy traversal depth (1=fast, 2=moderate, 3=comprehensive)
- `auto_submit_claims`: Whether to submit claims ≥0.90 confidence automatically
- `ui_callback`: Optional callback function for real-time log streaming to UI

**Returns:**
```python
{
    'status': 'INITIALIZED',  # or 'REJECTED', 'ERROR'
    'session_id': 'military_20260215_143022_Q17167',
    'anchor_qid': 'Q17167',
    'anchor_label': 'Roman Republic',
    'nodes_created': 23,
    'relationships_discovered': 47,
    'claims_generated': 147,
    'claims_submitted': 0,
    'completeness_score': 0.87,
    'cidoc_crm_class': 'E5_Event',
    'cidoc_crm_confidence': 'High',
    'discipline_roots_detected': 1,
    'duration_seconds': 42.3,
    'log_file': 'logs/military_agent_military_20260215_143022_Q17167_initialize.log'
}
```

---

### **Q.4.2 Subject Ontology Proposal Mode**

**Method:** `propose_subject_ontology(ui_callback)`

**Purpose:** Bridge between Initialize (discovery) and Training (systematic generation).

After Initialize mode discovers nodes and their hierarchical type properties, Subject Ontology Proposal analyzes these hierarchies to extract and propose a coherent domain ontology. This ontology then guides Training mode's claim generation.

**Workflow:**
1. Load initialized nodes (via session context)
2. Extract hierarchical type properties (P31, P279, P361)
3. Identify conceptual clusters using LLM
4. Propose ontology classes and relationships
5. Generate claim templates for Training mode
6. Define validation rules
7. Calculate strength score

**Outputs:**
```python
{
    'status': 'ONTOLOGY_PROPOSED',
    'session_id': 'military_20260215_143500',
    'facet': 'military',
    'ontology_classes': [
        {
            'class_name': 'Military Commander',
            'parent_class': None,
            'member_count': 15,
            'characteristics': ['rank', 'victories', 'legions_commanded'],
            'examples': ['Caesar', 'Pompey']
        }
    ],
    'hierarchy_depth': 3,
    'clusters': [...],
    'relationships': [...],
    'claim_templates': [...],
    'validation_rules': [...],
    'strength_score': 0.88,
    'reasoning': 'LLM explanation...',
    'duration_seconds': 22.4
}
```

---

### **Q.4.3 Training Mode**

**Method:** `execute_training_mode(max_iterations, target_claims, min_confidence, auto_submit_high_confidence, ui_callback)`

**Purpose:** Extended iterative claim generation with validation and quality metrics.

**Workflow:**
1. Load session context (Step 2) - get existing nodes
2. **Use proposed subject ontology** to guide claim generation
3. Iterate through SubjectConcept nodes (prioritize by ontology class)
4. For each node:
   - Check for Wikidata QID (skip if absent)
   - Fetch Wikidata entity (Step 3)
   - Validate completeness (Step 3.5)
   - Log reasoning for validation
   - Generate claims from statements (Step 3)
   - Enrich claims with CRMinf (Step 4) - automatic
   - Filter by min_confidence threshold
   - Optionally auto-submit claims ≥0.90 confidence
   - Log every decision with reasoning
5. Track metrics (claims/sec, avg confidence, avg completeness)
6. Stop when target_claims reached or max_iterations exhausted
7. Return comprehensive metrics

**Parameters:**
- `max_iterations`: Maximum nodes to process (5-100, default 100)
- `target_claims`: Stop after generating this many claims (10-500, default 500)
- `min_confidence`: Minimum confidence for claim proposals (0.5-1.0, default 0.80)
- `auto_submit_high_confidence`: Auto-submit claims ≥0.90 confidence (default False)
- `ui_callback`: Optional callback for real-time log streaming

**Returns:**
```python
{
    'status': 'TRAINING_COMPLETE',  # or 'ERROR'
    'session_id': 'military_20260215_143500',
    'iterations': 73,
    'nodes_processed': 73,
    'claims_proposed': 503,
    'claims_submitted': 0,
    'avg_confidence': 0.87,
    'avg_completeness': 0.82,
    'duration_seconds': 342.5,
    'claims_per_second': 1.47
}
```

---

### **Q.4.4 Schema Query Mode**

**Status:** Design complete, implementation pending  
**Purpose:** Answer questions about Neo4j model structure

**Capabilities (Planned):**
- Natural language queries about node types, properties, relationships
- Schema introspection and documentation
- Validation rule queries

**Example Queries:**
- "What properties does a SubjectConcept node have?"
- "What are all the relationship types between Human and Event nodes?"
- "Show me the validation rules for temporal properties"

---

### **Q.4.5 Data Query Mode**

**Status:** Design complete, implementation pending  
**Purpose:** Answer questions about actual graph data

**Capabilities (Planned):**
- Natural language to Cypher translation
- Facet-scoped data queries
- Cross-domain data synthesis

**Example Queries:**
- "How many military events occurred in the Roman Republic?"
- "Who were the political figures involved in the Battle of Pharsalus?"
- "What geographic locations are mentioned in connection with Julius Caesar?"

---

### **Q.4.6 Wikipedia Training Mode**

**Status:** In design  
**Purpose:** LLM-driven article discovery and claim extraction

**Capabilities (Planned):**
- Identify relevant Wikipedia articles for a subject domain
- Line-by-line claim extraction
- Registry validation (facets, relationships, entities)
- Claim creation/augmentation logic

---

## **Q.5 Discipline Root Detection & SFA Initialization**

**Integration Point:** After Initialize mode discovers hierarchy, detect canonical roots for SFA training (implements §4.9 policy).

**Method:** `detect_and_mark_discipline_roots(discovered_nodes, facet_key)`

**Purpose:** Identify which discovered nodes are discipline entry points (should have `discipline: true` flag).

### **Q.5.1 Detection Algorithm**

**Strategy 1: BROADER_THAN Reachability**
```python
def detect_discipline_roots(nodes_dict, facet_key):
    """
    Identify top-level concepts that should seed SFA training.
    Discipline roots are canonical entry points for agent specialization.
    """
    roots = []
    
    # Strategy 1: BROADER_THAN reachability (highest arity wins)
    for node in nodes_dict.values():
        reachability = count_reachable_via_broader_than(node)
        if reachability > 0.7 * len(nodes_dict):  # 70% of nodes below this root
            roots.append({
                'node_id': node['id'],
                'label': node['label'],
                'reachability': reachability,
                'method': 'high_reachability',
                'discipline_candidate': True
            })
    
    # Strategy 2: Explicit heuristics (facet-specific)
    if facet_key == 'MILITARY':
        military_keywords = ['Military', 'Warfare', 'Battle', 'Armed Force']
        for node in nodes_dict.values():
            if any(kw in node['label'] for kw in military_keywords):
                if len(node.get('BROADER_THAN', [])) == 0:  # No parent
                    roots.append({
                        'node_id': node['id'],
                        'label': node['label'],
                        'method': 'keyword_heuristic',
                        'discipline_candidate': True
                    })
    
    # Remove duplicates, return top 1-3 roots
    unique_roots = deduplicate_by_node_id(roots)
    return sorted(unique_roots, key=lambda x: x['reachability'], reverse=True)[:3]
```

**Result Format:**
```python
{
    'discipline_roots': [
        {
            'node_id': 'wiki:Q28048',
            'label': 'Roman Republic',
            'reachability': 0.95,
            'method': 'high_reachability',
            'facet': 'MILITARY'
        }
    ],
    'nodes_marked': 1,
    'ready_for_sfa_training': True
}
```

---

### **Q.5.2 Neo4j Implementation**

**Mark Discipline Roots:**
```cypher
-- After Initialize mode creates nodes, mark discipline roots:
MATCH (root:SubjectConcept {id: 'wiki:Q17167'})
SET root.discipline = true,
    root.facet = 'MILITARY',
    root.discipline_training_seed = true,
    root.discipline_marked_at = datetime()
```

**Query for SFA Training Initialization:**
```cypher
-- SFA queries for available roots:
MATCH (n:SubjectConcept)
WHERE n.discipline = true AND n.facet = 'MILITARY'
RETURN n.label, n.id, count((m)-[:BROADER_THAN*]->(n)) as hierarchy_depth
ORDER BY hierarchy_depth DESC
```

---

### **Q.5.3 Pre-Seeding Option**

If automatic detection is insufficient, pre-seed canonical root nodes explicitly:

```cypher
CREATE (root:SubjectConcept {
    subject_id: 'discipline_military_root',
    label: 'Military Science',
    facet: 'MILITARY',
    discipline: true,
    authority_id: 'sh85052639',  -- Library of Congress for "Military science"
    created_by: 'initialize_preseed',
    created_at: datetime()
})

-- Repeat for all 17 facets:
-- POLITICAL → 'Political Science'
-- ECONOMIC → 'Economic History'
-- CULTURAL → 'Cultural History'
-- (14 more...)
```

---

### **Q.5.4 Impact on SFA Training**

```python
# MilitarySFA initialization (from §4.9 refinement)
nodes = gds.query_graph(
    "MATCH (root:SubjectConcept) "
    "WHERE root.discipline = true AND root.facet = 'MILITARY' "
    "RETURN root"
)
# Gets: [SubjectConcept(Roman Republic)]

# SFA now builds hierarchy downward:
# Military Science → Roman Military → Legions → Tactics → ...

military_sfa.initialize_with_roots(nodes)
military_sfa.train_on_hierarchy()  # Build disciplinary ontology
```

---

## **Q.6 Cross-Domain Query Example: "Senator to Mollusk"**

**Query:** *"What is the relationship between a Roman senator and a mollusk?"*

### **Q.6.1 Classification Phase**

```python
sca = SubjectConceptAgent()
result = sca.execute_cross_domain_query(
    "What is the relationship between a Roman senator and a mollusk?"
)

# Classification output:
{
    'facets': ['POLITICAL', 'SCIENTIFIC', 'CULTURAL'],
    'cross_domain': True,
    'reasoning': 'Query spans political (senator), scientific (mollusk biology), cultural (textile dyeing)',
    'bridge_concepts': ['Tyrian purple', 'purple dye']
}
```

---

### **Q.6.2 Agent Spawning & Query Execution**

**Note:** Current implementation uses **simulated agents** (hard-coded mock responses) for smoke testing. Real SubjectFacetAgents can be spawned but require domain training.

```python
# SCA spawns 3 simulated agents
political_sfa = sca.spawn_agent('POLITICAL')  # Simulated
scientific_sfa = sca.spawn_agent('SCIENTIFIC')  # Simulated
cultural_sfa = sca.spawn_agent('CULTURAL')  # Simulated

# Each agent returns domain-specific results:
political_results = political_sfa.query("senator and purple")
# Returns: [senator → toga → purple stripe]

scientific_results = scientific_sfa.query("mollusk and dye")
# Returns: [mollusk → murex → dye production]

cultural_results = cultural_sfa.query("purple and textile")
# Returns: [purple dye → Tyrian purple → textile]
```

---

### **Q.6.3 Bridge Claim Generation**

SCA generates **data creation claims** (not just concept labels):

**1. NODE_CREATION Claim:**
```python
{
    'claim_type': 'NODE_CREATION',
    'label': 'Tyrian purple',
    'node_type': 'SubjectConcept',
    'facets': ['POLITICAL', 'SCIENTIFIC', 'CULTURAL'],  # Multi-facet node
    'properties': {
        'bridge_type': 'label_intersection',
        'source_facets': ['POLITICAL', 'SCIENTIFIC', 'CULTURAL']
    },
    'confidence': 0.85,
    'reasoning': 'Concept "Tyrian purple" appears in multiple domains'
}
```

**2. EDGE_CREATION Claims:**
```python
[
    {
        'claim_type': 'EDGE_CREATION',
        'source_node': 'node_pol_1',  # Roman senator
        'target_node': 'Tyrian purple',
        'relationship_type': 'RELATES_TO',
        'facet': 'POLITICAL',
        'confidence': 0.85,
        'reasoning': 'Bridge connection from political domain'
    },
    {
        'claim_type': 'EDGE_CREATION',
        'source_node': 'node_sci_2',  # murex snail
        'target_node': 'Tyrian purple',
        'relationship_type': 'RELATES_TO',
        'facet': 'SCIENTIFIC',
        'confidence': 0.85,
        'reasoning': 'Bridge connection from scientific domain'
    }
]
```

**3. NODE_MODIFICATION Claim:**
```python
{
    'claim_type': 'NODE_MODIFICATION',
    'label': 'Tyrian purple',
    'node_id': 'existing_node_123',
    'modifications': {
        'add_facets': ['POLITICAL', 'SCIENTIFIC'],
        'add_property': {'key': 'bridge_concept', 'value': True}
    },
    'confidence': 0.80,
    'reasoning': 'Found in additional domain(s)'
}
```

---

### **Q.6.4 Synthesis**

**Natural Language Response:**
```
Roman senators wore togas with purple stripes (toga praetexta) or all-purple 
togas (toga purpurea) as symbols of their rank. The distinctive Tyrian purple 
dye used for these garments was extracted from murex sea snails, a type of 
mollusk. This expensive dye—requiring thousands of mollusks to produce just a 
few grams—was reserved for the Roman elite, making it a luxury marker of 
senatorial status.
```

**Key Insight:** Bridge discovery doesn't just find labels—it **generates claims** to create graph structure connecting disparate domains.

---

## **Q.7 Implementation Components**

### **Q.7.1 Core Framework Components**

**1. AgentOperationalMode Enum**
```python
class AgentOperationalMode(Enum):
    INITIALIZE = "initialize"
    TRAINING = "training"
    SCHEMA_QUERY = "schema_query"
    DATA_QUERY = "data_query"
```

**2. AgentLogger Class** (~200 lines)

**Purpose:** Verbose logging with structured action tracking, reasoning capture, and session metrics.

**Key Methods:**
- `log_action(action, details, level)` - Log structured actions
- `log_reasoning(decision, rationale, confidence)` - Log agent reasoning
- `log_query(query_type, query, result)` - Log queries (Cypher, API)
- `log_error(error, context)` - Log errors with context
- `log_claim_proposed(claim_id, label, confidence)` - Track claim proposals
- `log_node_created(node_id, label, type)` - Track node creation
- `get_summary()` - Generate session summary statistics
- `close()` - Close logger and write summary

**3. SubjectConceptAgent (SCA)** (~400 lines)

**Purpose:** Master coordinator for cross-domain orchestration.

**Key Methods:**
- `classify_facets(query, max_facets)` - LLM-based facet classification (from canonical 17)
- `spawn_agent(facet_key)` - Simulate SubjectFacetAgent (smoke test mode)
- `execute_cross_domain_query(query)` - Orchestrate multi-facet query
- `query_within_facet(query, facet_key)` - Single-facet convenience method
- `route_claim(claim)` - Tag and route claims to multiple facets
- `_simulate_facet_query(facet_key, query)` - Mock query execution (for testing)
- `_find_conceptual_bridges(facet_results, suggested_bridges)` - Generate bridge CLAIMS
- `_synthesize_response(query, facet_results, bridge_claims)` - LLM synthesis

**4. FacetAgent Class** (~50 lines base + facet-specific methods)

**Purpose:** Domain-specific agent for single-facet operations.

**Key Methods:**
- `execute_initialize_mode(anchor_qid, depth, ...)` - Bootstrap from Wikidata
- `propose_subject_ontology(ui_callback)` - Analyze hierarchies
- `execute_training_mode(max_iterations, ...)` - Iterative claim generation
- `detect_and_mark_discipline_roots(nodes, facet)` - Root detection
- `set_mode(mode)` / `get_mode()` - Operational mode management

---

### **Q.7.2 Method Signatures**

**Initialize Mode:**
```python
def execute_initialize_mode(
    anchor_qid: str,
    depth: int = 1,
    auto_submit_claims: bool = False,
    ui_callback: Optional[Callable] = None
) -> Dict[str, Any]
```

**Training Mode:**
```python
def execute_training_mode(
    max_iterations: int = 100,
    target_claims: int = 500,
    min_confidence: float = 0.80,
    auto_submit_high_confidence: bool = False,
    ui_callback: Optional[Callable] = None
) -> Dict[str, Any]
```

**Cross-Domain Query:**
```python
def execute_cross_domain_query(
    query: str,
    auto_classify: bool = True,
    facets: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Claim Routing:**
```python
def route_claim(
    claim: Dict[str, Any]
) -> Dict[str, Any]
```

---

## **Q.8 Log Output Format**

### **Q.8.1 Log File Structure**

**File Location:** `logs/{agent_id}_{session_id}_{mode}.log`

**Example:** `logs/military_agent_military_20260215_143022_Q17167_initialize.log`

**Structure:**
```
# Agent Log: military_agent
# Mode: initialize
# Session: military_20260215_143022_Q17167
# Started: 2026-02-15T14:30:22.123456
================================================================================

[timestamp] [level] [category] message

...action logs...
...reasoning logs...
...query logs...
...error logs...

================================================================================
# SESSION SUMMARY
# Duration: 42.3s
# Actions: 127
# Reasoning steps: 23
# Queries: 8
# Errors: 0
# Claims proposed: 147
# Nodes created: 23
================================================================================
```

---

### **Q.8.2 Log Categories**

- `[INITIALIZE]` - Initialize mode actions
- `[TRAINING]` - Training mode actions
- `[REASONING]` - Decision reasoning with confidence
- `[QUERY]` - Cypher/API query execution
- `[ERROR]` - Errors with context

---

### **Q.8.3 Initialize Mode Log Example**

```
[2026-02-15T14:30:22] [INFO] [INITIALIZE] INITIALIZE_START: anchor_qid=Q17167, depth=2, facet=military, auto_submit=False
[2026-02-15T14:30:23] [INFO] [INITIALIZE] FETCH_ANCHOR: qid=Q17167
[2026-02-15T14:30:25] [INFO] [INITIALIZE] FETCH_COMPLETE: label=Roman Republic, statements=142
[2026-02-15T14:30:26] [INFO] [REASONING] COMPLETENESS_VALIDATION: Found 47/52 expected properties (confidence=0.87)
[2026-02-15T14:30:27] [INFO] [INITIALIZE] CIDOC_ENRICHMENT: qid=Q17167
[2026-02-15T14:30:28] [INFO] [INITIALIZE] CIDOC_COMPLETE: cidoc_class=E5_Event, confidence=High
[2026-02-15T14:30:29] [INFO] [INITIALIZE] AUTHORITY_ENRICHMENT: qid=Q17167
[2026-02-15T14:30:29] [INFO] [INITIALIZE] AUTHORITY_TIER_1: authority_id=sh85115055, fast_id=fst01234567
[2026-02-15T14:30:30] [INFO] [INITIALIZE] BOOTSTRAP_START: qid=Q17167, depth=2
[2026-02-15T14:31:03] [INFO] [INITIALIZE] BOOTSTRAP_COMPLETE: nodes_created=23, relationships=47, claims_generated=147
[2026-02-15T14:31:03] [INFO] [INITIALIZE] DISCIPLINE_ROOT_DETECTION: Analyzing 23 nodes for discipline candidates
[2026-02-15T14:31:04] [INFO] [INITIALIZE] DISCIPLINE_ROOTS_FOUND: 3 candidates (Roman Republic, Military Power, Civil War)
[2026-02-15T14:31:04] [INFO] [INITIALIZE] SET_DISCIPLINE_FLAG: Roman Republic marked discipline=true (MILITARY facet root)
[2026-02-15T14:31:04] [INFO] [INITIALIZE] INITIALIZE_COMPLETE: status=SUCCESS, duration=42.3s, nodes_with_discipline=1
```

---

### **Q.8.4 Training Mode Log Example**

```
[2026-02-15T14:35:00] [INFO] [TRAINING] TRAINING_START: max_iterations=20, target_claims=100, min_confidence=0.80, auto_submit=False
[2026-02-15T14:35:01] [INFO] [TRAINING] LOAD_CONTEXT: session_id=military_20260215_143500
[2026-02-15T14:35:03] [INFO] [TRAINING] CONTEXT_LOADED: existing_nodes=157, pending_claims=23
[2026-02-15T14:35:04] [INFO] [TRAINING] ITERATION_START: iteration=1, total=20, node_id=abc123, node_label=Battle of Pharsalus
[2026-02-15T14:35:05] [INFO] [TRAINING] FETCH_WIKIDATA: qid=Q28048
[2026-02-15T14:35:07] [INFO] [REASONING] COMPLETENESS_VALIDATED: 47/52 properties (confidence=0.91)
[2026-02-15T14:35:08] [INFO] [TRAINING] GENERATE_CLAIMS: qid=Q28048
[2026-02-15T14:35:12] [INFO] [TRAINING] CLAIMS_GENERATED: count=8, qid=Q28048
[2026-02-15T14:35:13] [INFO] [TRAINING] CLAIM_PROPOSED: claim_id=claim_1, label=Battle of Pharsalus occurred at Pharsalus, confidence=0.90
[2026-02-15T14:35:14] [INFO] [TRAINING] CLAIM_PROPOSED: claim_id=claim_2, label=Julius Caesar participated in Battle of Pharsalus, confidence=0.90
[2026-02-15T14:35:20] [INFO] [TRAINING] ITERATION_COMPLETE: iteration=1, claims_this_node=8, total_proposed=8
[2026-02-15T14:35:21] [INFO] [TRAINING] ITERATION_START: iteration=2, total=20, node_id=def456, node_label=Julius Caesar
[...continues...]
[2026-02-15T14:37:45] [INFO] [TRAINING] TRAINING_COMPLETE: status=SUCCESS, nodes_processed=20, claims_proposed=147, duration=165.2s, claims_per_second=0.89
```

---

## **Q.9 Source Files**

### **Q.9.1 Primary Implementation**

**File:** `scripts/agents/facet_agent_framework.py`  
**Total Lines:** ~1,100 (Steps 1-5 cumulative)  
**Version:** 2026-02-15-step5-sca

**Classes Added in Step 5:**
- `AgentOperationalMode` (Enum) - 4 operational modes
- `AgentLogger` (~200 lines) - Verbose logging infrastructure
- `SubjectConceptAgent` (~400 lines) - Cross-domain orchestration

**Methods Added in Step 5:**
- `set_mode()` / `get_mode()` - Mode management
- `execute_initialize_mode()` - Bootstrap workflow
- `propose_subject_ontology()` - Hierarchy analysis
- `execute_training_mode()` - Iterative claim generation
- `detect_and_mark_discipline_roots()` - Root detection
- `classify_facets()` - LLM-based facet classification
- `spawn_agent()` - Agent spawning (simulated)
- `execute_cross_domain_query()` - Multi-facet orchestration
- `query_within_facet()` - Single-facet query
- `route_claim()` - Multi-facet claim routing
- `_simulate_facet_query()` - Mock execution for testing
- `_find_conceptual_bridges()` - Bridge claim generation
- `_synthesize_response()` - LLM synthesis

---

### **Q.9.2 UI Implementation**

**File:** `scripts/ui/agent_gradio_app.py`  
**Version:** 2026-02-15

**New Tabs:**
- "⚙️ Agent Operations" - Initialize & Training modes (single-facet)
- "🌐 Cross-Domain" - SubjectConceptAgent orchestration

---

### **Q.9.3 Training Resources**

**File:** `Facets/TrainingResources.yml`  
**Referenced by:** Appendix O (Facet Training Resources Registry)

Contains canonical training patterns and exemplar claims for each of the 17 facets.

---

## **Q.10 Related Sections**

### **Q.10.1 Internal Cross-References**

- **Appendix O:** Facet Training Resources Registry (training patterns for 17 facets)
- **Section 4.9:** Academic Discipline Model (discipline flag usage policy)
- **Appendix D:** Subject Facet Classification (17 canonical facets)
- **Appendix K:** Wikidata Integration Patterns (federation discovery P31/P279/P361)
- **Appendix P:** Semantic Enrichment & Ontology Alignment (CIDOC-CRM/CRMinf automatic enrichment)
- **Section 5:** Agent Architecture (agent roles and workflows)
- **Section 6:** Claims Layer (claim structure and validation)

---

### **Q.10.2 Integration Points**

**Step 1 (Schema Understanding):**
- Initialize mode validates claim structure before proposal
- Training mode checks required properties per node type
- Both use schema introspection for validation

**Step 2 (State Loading):**
- Training mode REQUIRES `get_session_context()` to load existing nodes
- Both modes use `find_claims_for_node()` to avoid duplicates
- State tracking ensures iterative progress

**Step 3 (Federation Discovery):**
- Initialize mode BUILT ON `bootstrap_from_qid()`
- Training mode uses `fetch_wikidata_entity()` per node
- Both use `generate_claims_from_wikidata()` for claim generation
- Hierarchy traversal via `discover_hierarchy_from_entity()`

**Step 3.5 (Completeness Validation):**
- Both modes REQUIRE `validate_entity_completeness()` before processing
- Reject entities with <60% completeness
- Track completeness metrics in training mode

**Step 4 (Ontology Alignment):**
- Both modes AUTOMATICALLY call `enrich_with_ontology_alignment()`
- All nodes get `cidoc_crm_class` property
- All claims get `crminf_alignment` section via `enrich_claim_with_crminf()`
- Ontology enrichment happens transparently in workflow

---

### **Q.10.3 Usage Examples**

**Initialize Roman Military History Domain:**
```python
from facet_agent_framework import FacetAgentFactory

factory = FacetAgentFactory()
agent = factory.get_agent('military')

result = agent.execute_initialize_mode(
    anchor_qid='Q17167',  # Roman Republic
    depth=2,
    auto_submit_claims=False
)

print(f"✅ Initialized {result['nodes_created']} nodes")
print(f"📊 Generated {result['claims_generated']} claims")
print(f"📈 Completeness: {result['completeness_score']:.1%}")
print(f"🏛️ CIDOC class: {result['cidoc_crm_class']}")
```

**Cross-Domain Query:**
```python
from facet_agent_framework import SubjectConceptAgent

sca = SubjectConceptAgent()

result = sca.execute_cross_domain_query(
    "What is the relationship between a Roman senator and a mollusk?"
)

print(f"✅ Query complete")
print(f"🌐 Facets: {', '.join(result['classification']['facets'])}")
print(f"🔗 Bridge claims: {result['bridge_claim_count']}")
print(f"\n💡 Answer:\n{result['synthesized_response']}")

sca.close()
```

**Continue with Training:**
```python
result = agent.execute_training_mode(
    max_iterations=50,
    target_claims=300,
    min_confidence=0.80
)

print(f"✅ Processed {result['nodes_processed']} nodes")
print(f"📊 Proposed {result['claims_proposed']} claims")
print(f"⚡ Performance: {result['claims_per_second']:.2f} claims/sec")
```

---

**(End of Appendix Q)**

---

# **Appendix R: Federation Strategy & Multi-Authority Integration**

## **R.1 Federation Architecture Principles**

Chrystallum employs **federation** as a core architectural pattern to reconcile, validate, and enrich historical data across multiple authoritative systems. Rather than depending on a single source of truth, the system orchestrates a **multi-hop enrichment network** where Wikidata serves as a discovery broker and domain-specific authorities provide canonical grounding.

### **R.1.1 Wikidata as Federation Broker, Not Final Authority**

Wikidata functions as the **identity hub and router** in the federation architecture:

- **Discovery layer**: Provides QIDs, labels, descriptions, and external identifier properties (P214, P1584, P1566, etc.)
- **Routing mechanism**: External ID properties serve as jump-off points to domain authorities (VIAF, Pleiades, GeoNames, Trismegistos, etc.)
- **Confidence positioning**: Resides at Layer 2 Federation with confidence floor 0.90
- **Epistemic status**: Treated as broad identity hint, not canonical source

**Key principle**: Always resolve candidate entities to Wikidata QID first, then follow federation links to deeper authorities. Wikidata assertions are *discovery inputs*, not *verified outputs*.

### **R.1.2 Two-Hop Enrichment Pattern**

Federation follows a systematic two-hop pattern:

```cypher
// Hop 1: Wikidata resolution
MATCH (candidate:Entity {label: "Emerita Augusta"})
MERGE (wd:WikidataEntity {qid: "Q13560"})
CREATE (candidate)-[:ALIGNED_WITH]->(wd)

// Hop 2: Domain authority enrichment
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)
MERGE (place:PleiadesPlace {id: pleiades_id})
WITH place
CALL apoc.load.json("https://pleiades.stoa.org/places/" + place.id + "/json") 
YIELD value
SET place.names = value.names,
    place.temporal_range = value.temporalRange,
    place.coordinates = value.reprPoint
CREATE (candidate)-[:SAME_AS {confidence: 0.95}]->(place)
```

This pattern ensures:
1. **Broad discovery** via Wikidata's extensive coverage
2. **Deep grounding** via specialist authorities
3. **Provenance tracking** at each hop
4. **Confidence scoring** based on federation depth

### **R.1.3 Confidence Floors and Layer 2 Federation Positioning**

Federation authorities are tiered by epistemic strength:

- **Layer 1 (0.95-1.0)**: Domain-specific canonical authorities
  - LCSH/FAST for subjects
  - Pleiades for ancient places
  - PIR/PLRE for Roman prosopography
  - EDH for Latin inscriptions

- **Layer 2 (0.85-0.94)**: Broad integration hubs
  - Wikidata (0.90 baseline)
  - VIAF (0.88 for persons, 0.85 for works)
  - Getty AAT (0.90 for hierarchical concepts)

- **Layer 3 (0.70-0.84)**: Complementary sources and derived data
  - GeoNames/OSM (0.75 for modern coordinates)
  - Crowdsourced content (case-by-case evaluation)

**Confidence boost rules**:
- Adding epigraphic evidence (EDH/Trismegistos): +0.15 to +0.20
- Cross-validation by 2+ authorities: +0.10
- Temporal/geographic constraint satisfaction: +0.10
- Primary source linkage: +0.15

### **R.1.4 Federation Edge Patterns**

The system uses typed federation relationships to capture different alignment strengths:

```cypher
// SAME_AS: High-confidence identity match (0.90+)
(candidate)-[:SAME_AS {confidence: 0.95, 
                       verified_at: datetime(),
                       method: "P1584_resolution"}]->(pleiades)

// ALIGNED_WITH: Probable match requiring validation (0.70-0.89)
(candidate)-[:ALIGNED_WITH {confidence: 0.80,
                            conflicts: ["date_range_mismatch"],
                            review_required: true}]->(wikidata)

// DERIVED_FROM: Extracted/inferred from authority
(claim)-[:DERIVED_FROM {extraction_date: date(),
                        confidence: 0.85,
                        extractor_version: "v2.3"}]->(viaf_record)

// CONFLICTS_WITH: Explicit disagreement requiring adjudication
(source_a)-[:CONFLICTS_WITH {conflict_type: "temporal_range",
                             source_a_value: "-509/-27",
                             source_b_value: "-500/-31",
                             resolution: null}]->(source_b)
```

These edge types enable:
- **Confidence propagation**: `SAME_AS` edges boost target confidence
- **Review triggers**: `ALIGNED_WITH` and `CONFLICTS_WITH` flag human review
- **Provenance chains**: `DERIVED_FROM` tracks extraction lineage
- **Quality metrics**: Edge distributions measure federation health

---

## **R.2 Current Federation Layers (6 Operational)**

### **R.2.1 Subject Authority Federation** 
**Status**: Most mature

**Authorities**: LCC/LCSH/FAST/Wikidata

**Coverage**: Entire subject classification backbone, routing for specialist agents, bibliographic crosswalks

**Key artifacts**:
- `query_lcsh_enriched.tsv` (LCSH mappings)
- `Python/lcsh/scripts`, `Python/fast/scripts` (ingestion pipelines)
- `LCC_AGENT_ROUTING.md` (agent scope definitions)

**Usage pattern**:
1. Resolve subject string → LCSH/FAST heading
2. Map heading → LCC call number range
3. Route to appropriate Specialist Facet Agent based on LCC class
4. Cross-reference Wikidata P-codes for international concept alignment
5. Apply facet tags from shared registry

### **R.2.2 Temporal Federation**
**Status**: Strong

**Authorities**: Year backbone + curated periods + PeriodO alignment

**Coverage**: All temporal concepts, period-based lensing, date normalization

**Key artifacts**:
- `time_periods.csv` (1,083 curated periods)
- `periodo-dataset.csv` (PeriodO mappings)
- `scripts/backbone/temporal` (Year node generation)

**Usage pattern**:
1. Parse temporal expression (label, date range, uncertainty markers)
2. Create/link to Year nodes (ISO-normalized)
3. Resolve period label → PeriodO ID with explicit bounds
4. Attach Period nodes to Events/Persons/Places as temporal envelopes
5. Validate temporal plausibility (events must fall within period bounds)
6. Support period-based lensing ("show only Late Republic events")

### **R.2.3 Facet Federation**
**Status**: Strong conceptual, moderate automation

**Authorities**: 17 canonical facets applied across subject and temporal layers

**Coverage**: Cross-cutting conceptual dimensions (warfare, religion, law, etc.)

**Key artifacts**:
- `facet_registry_master.json` (canonical facet definitions)
- `period_facet_tagger.py` (automated facet assignment)
- Agent scope definitions (facet-based routing)

**Usage pattern**:
1. Analyze entity/event for facet applicability
2. Assign facet tags from registry (e.g., `WARFARE`, `LEGAL_TOPICS`, `GEOGRAPHY`)
3. Use facet tags for:
   - Agent routing (LCC + facet → specialist agent)
   - Cross-domain queries ("all warfare-related concepts across periods")
   - Framework-specific emphasis (Marxist framework privileges `ECONOMICS`)

### **R.2.4 Relationship Semantics Federation**
**Status**: In progress

**Authorities**: CIDOC-CRM/CRMinf + Wikidata predicates

**Coverage**: Canonical relationship vocabulary, action structures, event participation roles

**Key artifacts**:
- `action_structure_vocabularies.csv` (relationship types)
- `action_structure_wikidata_mapping.csv` (Wikidata P-code mappings)
- Architecture relationship sections (CIDOC alignment)

**Usage pattern**:
1. Extract relationship from claim text
2. Map to canonical vocabulary entry (e.g., "commanded" → `COMMANDED_MILITARY_UNIT`)
3. Align to CIDOC-CRM class (e.g., `E7 Activity`, `PC14 carried out by`)
4. Cross-reference Wikidata predicate (e.g., P598 `commander of`)
5. Store all mappings for cross-system queries

### **R.2.5 Geographic Federation**
**Status**: Early/transition

**Authorities**: Geographic registry + authority extracts (stabilizing)

**Coverage**: Place concepts, modern/ancient name variants, coordinate resolution

**Key artifacts**:
- `geographic_registry_master.csv` (place registry)
- Large authority extract files (Getty, GeoNames)

**Current challenges**:
- Source selection (Getty language vs. place pull)
- Ancient vs. modern place disambiguation
- Coordinate precision for historical periods

**Usage pattern** (in development):
1. Resolve place string → registry entry
2. Distinguish ancient (Pleiades) vs. modern (GeoNames) context
3. Pull name variants and temporal validity
4. Use coordinates for visualization only, not primary ontology

### **R.2.6 Agent/Claims Federation**
**Status**: Architecturally defined, partial implementation

**Authorities**: Specialist agents with defined scopes + review/synthesis workflow

**Coverage**: Agent capability declarations, claim provenance, review chains

**Key artifacts**:
- `2-12-26 Chrystallum Architecture - DRAFT.md` (agent model)
- `facet_agent_system_prompts.json` (agent definitions)
- `SCA_SFA_ARCHITECTURE_PACKAGE.md` (workflow specification)

**Usage pattern**:
1. Route claim → appropriate Specialist Facet Agent based on LCC/facet/period
2. SFA generates claim with provenance metadata
3. Seed Claim Agent reviews for conflicts and gaps
4. Framework-specific lensing applies interpretive emphasis
5. All steps tracked as federation of agent contributions

---

## **R.3 Stacked Evidence Ladder**

**Core Principle**: Move candidate nodes as far down the evidence ladder as possible before they are considered "solid." Each tier provides a different kind of epistemic support, and depth down the ladder translates to higher confidence scores and stronger validation.

### **R.3.1 People/Names** (3-tier ladder)

#### **Tier 1: Broad Identity** (Wikidata + VIAF)

**Purpose**: Establish high-level identity for persons, especially elites, authors, and subjects of modern works

**Authorities**: Wikidata QID, VIAF (via P214)

**How to use**:
- Resolve person string → Wikidata QID (e.g., "Gaius Julius Caesar" → Q1048)
- Follow P214 to VIAF cluster for canonical name forms in multiple languages
- Check VIAF for cluster quality:
  - Single clean cluster = strong identity
  - Multiple clusters = name collision, treat with caution
- Use for prosopography of elites, author attribution, modern scholarly linking

**Confidence rule**: Wikidata-only person = **textual/unconfirmed** (0.70-0.75)

```cypher
// Tier 1 enrichment
MATCH (p:Person {label: "Gaius Julius Caesar"})
MERGE (wd:WikidataEntity {qid: "Q1048"})
CREATE (p)-[:ALIGNED_WITH {confidence: 0.75}]->(wd)
WITH p, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id)
MERGE (viaf:VIAFRecord {id: viaf_id})
CREATE (p)-[:DERIVED_FROM {confidence: 0.80, layer: "identity"}]->(viaf)
SET p.canonical_names = viaf.name_variants,
    p.identity_tier = 1
```

#### **Tier 2: Historical Grounding** (Trismegistos People + PIR/PLRE)

**Purpose**: Confirm person appears in primary documentary evidence with historical context (offices, locations, dates)

**Authorities**: Trismegistos People (TM_People), PIR (Prosopographia Imperii Romani), PLRE (Prosopography of the Later Roman Empire)

**How to use**:
- Check TM_People for papyrological/epigraphic attestations
- For Roman elites, resolve to PIR/PLRE prosopography ID
- Extract structured data:
  - Offices held (consul, praetor, legatus)
  - Attested locations with date ranges
  - Family relationships (gens, cognomen patterns)
- Use as **hard constraints**:
  - Do not allow events outside person's active date window
  - Geography envelope from attested locations
  - Office-based event participation rules (can't command legion without military office)

**Confidence rule**: Wikidata + VIAF + Trismegistos + PIR = **strongly attested historical person** (0.90-0.95)

```cypher
// Tier 2 enrichment
MATCH (p:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WITH p, wd
// Check Trismegistos
CALL apoc.load.json("https://www.trismegistos.org/person/" + tm_id) YIELD value
MERGE (tm:TrismegistosPerson {id: value.person_id})
CREATE (p)-[:SAME_AS {confidence: 0.90, evidence_type: "documentary"}]->(tm)
SET p.attested_documents = value.document_count,
    p.date_range = [value.earliest_date, value.latest_date],
    p.attested_locations = value.places,
    p.identity_tier = 2
// Add PIR for Roman elites
MERGE (pir:PIREntry {id: pir_id})
CREATE (p)-[:SAME_AS {confidence: 0.95, prosopography: "PIR"}]->(pir)
SET p.offices = pir.offices,
    p.cursus_honorum = pir.career_path
```

#### **Tier 3: Micro-Evidence** (LGPN + DDbDP)

**Purpose**: Ground person in specific documentary/onomastic evidence at the micro-historical level

**Authorities**: LGPN (Lexicon of Greek Personal Names), DDbDP (Duke Databank of Documentary Papyri)

**How to use**:
- **For Greek names**: Query LGPN for name frequency and geographic distribution
  - Use to support cultural/ethnic inferences ("common freedman name in Alexandria")
  - Check name variants and spelling patterns
- **For documentary papyri**: Link person to specific DDbDP documents
  - Create Evidence nodes for each papyrus mentioning person
  - Extract roles: party to contract, witness, official, recipient
  - Link Evidence → Person → Document → Place → Date for full provenance chain

**Confidence rule**: Tier 3 grounding = **micro-attested with primary source linkage** (0.95-0.98)

```cypher
// Tier 3 enrichment: Documentary evidence nodes
MATCH (p:Person)-[:SAME_AS]->(tm:TrismegistosPerson)
WITH p, tm
UNWIND tm.document_ids AS doc_id
MERGE (doc:Document {tm_id: doc_id})
MERGE (ev:Evidence {id: "ev_" + doc_id})
SET ev.type = "papyrological",
    ev.text = doc.transcription,
    ev.material = "papyrus",
    ev.findspot = doc.provenance,
    ev.date_range = doc.date
CREATE (ev)-[:DOCUMENTS]->(p)
CREATE (ev)-[:FOUND_AT]->(place:Place {pleiades_id: doc.pleiades_place})
CREATE (ev)-[:DATED_TO]->(year:Year {iso_year: doc.middle_date})
SET p.evidence_count = size(collect(DISTINCT doc_id)),
    p.identity_tier = 3

// LGPN onomastic support
MERGE (lgpn:LGPNEntry {name: p.label})
SET lgpn.frequency = lgpn_frequency,
    lgpn.geographic_distribution = lgpn_regions
CREATE (p)-[:ONOMASTIC_SUPPORT]->(lgpn)
```

**Attestation strength summary**:
- **Wikidata-only**: Textual reference, unverified (0.70-0.75)
- **VIAF + Wikidata**: Author/creator authority (0.80-0.85)
- **VIAF + Trismegistos + PIR**: Strongly attested elite (0.90-0.95)
- **VIAF + TM + PIR + DDbDP**: Micro-attested with full provenance (0.95-0.98)

---

### **R.3.2 Places** (3-tier ladder)

#### **Tier 1: Conceptual Place** (Pleiades)

**Purpose**: Establish ancient geographic concept with temporal validity and name variants

**Authority**: Pleiades (via P1584)

**How to use**:
- Resolve ancient place → Pleiades ID
- Pleiades provides:
  - **Conceptual place** (not just coordinate point)
  - Ancient and modern name variants
  - **Temporal validity periods** (which historical periods the place exists in)
  - Coordinate ranges (often approximate, reflecting uncertainty)
- Use as **canonical place key** for ancient geography
- Apply temporal validity to constrain events:
  - Events using this place must fall within its valid period
  - Flag anachronistic references (e.g., "Constantinople" used before founding)

**Confidence rule**: Pleiades place grounding + temporal validity = +0.10 to base confidence

```cypher
// Tier 1: Pleiades resolution
MATCH (place:Place {label: "Emerita Augusta"})
MERGE (wd:WikidataEntity {qid: "Q13560"})
CREATE (place)-[:ALIGNED_WITH]->(wd)
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pleiades_id + "/json") 
YIELD value
MERGE (pleiades:PleiadesPlace {id: pleiades_id})
SET pleiades.names = value.names,
    pleiades.temporal_range = value.temporalRange,
    pleiades.coordinates = value.reprPoint,
    pleiades.periods = value.periods
CREATE (place)-[:SAME_AS {confidence: 0.90, temporal_validity: pleiades.temporal_range}]->(pleiades)
SET place.ancient_names = [n in value.names WHERE n.language IN ['grc', 'la'] | n.nameTransliterated],
    place.modern_names = [n in value.names WHERE n.language = 'en' | n.nameTransliterated],
    place.valid_periods = pleiades.periods
```

#### **Tier 2: Granular Geography** (Trismegistos Geo + DARE)

**Purpose**: Village-level, quarter-level, and network geography for fine-grained historical context

**Authorities**: 
- **Trismegistos Geo (TM_Geo)**: Village/quarter level, especially Egypt/Eastern Mediterranean
- **DARE (Digital Atlas of the Roman Empire)**: Roads, military installations, administrative geography

**How to use**:
- **TM_Geo for local places**:
  - Resolve village/quarter names to TM_Geo IDs
  - Map TM_Geo → Pleiades to anchor micro-places in global ancient map
  - Use for papyrus provenance, fine-grained population studies
- **DARE for network geography**:
  - Validate route plausibility between places using Roman road network
  - Locate military sites, administrative centers, border installations
  - Calculate distances and travel times for event modeling

**Confidence rule**: Tier 2 granularity + network validation = +0.15 beyond Tier 1

```cypher
// Tier 2: Trismegistos Geo (micro-geography)
MATCH (place:Place {label: "Theadelphia"})
CALL apoc.load.json("https://www.trismegistos.org/place/" + tm_geo_id) YIELD value
MERGE (tm_place:TMGeoPlace {id: tm_geo_id})
SET tm_place.type = "village",
    tm_place.nome = value.administrative_unit,
    tm_place.parent_place = value.parent
CREATE (place)-[:SAME_AS {confidence: 0.92, granularity: "village"}]->(tm_place)
// Link to parent Pleiades region
MATCH (parent:PleiadesPlace {id: tm_place.parent_pleiades})
CREATE (place)-[:PART_OF]->(parent)

// DARE road network validation
MATCH (event:Event)-[:OCCURRED_AT]->(origin:Place),
      (event)-[:DESTINATION]->(destination:Place)
WITH event, origin, destination
CALL dare.validateRoute(origin.pleiades_id, destination.pleiades_id) YIELD isPlausible, distance_km, travel_days
WHERE isPlausible = true
SET event.validated_route = true,
    event.distance_km = distance_km,
    event.travel_time_estimate = travel_days
```

#### **Tier 3: Modern Ground Truth** (GeoNames/OSM)

**Purpose**: Precise modern coordinates and admin boundaries for visualization only

**Authorities**: GeoNames (via P1566), OpenStreetMap

**How to use**:
- Use **only for UI maps and modern context**
- Never as primary historical geography
- Pull precise coordinates, bounding boxes, current admin units
- Useful for:
  - Map visualization layers
  - Modern place-name resolution for user queries
  - Spatial indexing for approximation queries

**Critical constraint**: GeoNames/OSM provide modern geography. Roman provinces, ancient boundaries, and historical place concepts come from Pleiades/DARE/TM_Geo, not modern systems.

```cypher
// Tier 3: Modern coordinates (UI-only)
MATCH (place:Place)-[:SAME_AS]->(pleiades:PleiadesPlace)
WITH place, pleiades
MATCH (wd:WikidataEntity)-[:HAS_EXTERNAL_ID {property: "P1566"}]->(geonames_id)
WHERE (place)-[:ALIGNED_WITH]->(wd)
CALL apoc.load.json("http://api.geonames.org/getJSON?geonameId=" + geonames_id) 
YIELD value
MERGE (gn:GeoNamesPlace {id: geonames_id})
SET gn.lat = value.lat,
    gn.lng = value.lng,
    gn.modern_name = value.name,
    gn.admin_units = [value.countryName, value.adminName1],
    gn.bbox = value.bbox
CREATE (place)-[:HAS_MODERN_LOCATION {usage: "visualization_only"}]->(gn)
SET place.map_coordinates = point({latitude: gn.lat, longitude: gn.lng})
// Do NOT use for historical assertions
```

---

### **R.3.3 Events/Claims/Communications** (3-tier ladder)

#### **Tier 1: Named Events** (Wikidata)

**Purpose**: Discover event seeds from Wikidata's named events and basic participation structure

**Authority**: Wikidata (battles, reforms, assassinations, foundations, treaties)

**How to use**:
- Query Wikidata for events related to entities, periods, or places
- Extract basic structure:
  - Event type (P31): battle, reform, assassination, etc.
  - Participants (P710): with roles like "commander," "victim," "location"
  - Date (P585, P580-P582): point in time or start-end
  - Place (P276, P17): where event occurred
- Treat as **event seeds, not fully trusted events**
- Propose Event node with:
  - Event type classification
  - Ordered participant roles
  - Temporal and spatial anchors
  - Confidence: 0.75 (seed level)

**Confidence rule**: Wikidata event seed = 0.75, requires corroboration for acceptance

```cypher
// Tier 1: Wikidata event seed discovery
CALL apoc.load.json("https://www.wikidata.org/wiki/Special:EntityData/Q48314.json") 
YIELD value
WITH value.entities["Q48314"] AS battle
MERGE (event:Event {wikidata_qid: "Q48314"})
SET event.label = battle.labels.en.value,
    event.type = "battle",
    event.confidence_tier = 1,
    event.base_confidence = 0.75,
    event.requires_corroboration = true
// Extract participants
FOREACH (claim IN battle.claims.P710 |
  MERGE (participant:Entity {qid: claim.mainsnak.datavalue.value.id})
  CREATE (event)-[:HAS_PARTICIPANT {role: claim.qualifiers.P3831[0].datavalue.value.id}]->(participant)
)
// Extract temporal and spatial
SET event.date_point = battle.claims.P585[0].mainsnak.datavalue.value.time,
    event.place_qid = battle.claims.P276[0].mainsnak.datavalue.value.id
```

#### **Tier 2: Epigraphic/Documentary Evidence** (EDH + Trismegistos Texts)

**Purpose**: Corroborate events with primary epigraphic or documentary sources

**Authorities**: 
- **EDH (Epigraphic Database Heidelberg)**: Latin inscriptions (via P2192)
- **Trismegistos Texts**: Papyri and inscriptions catalog

**How to use**:
- For each event seed, search authorities for inscriptions/papyri mentioning:
  - Event participants (persons, organizations)
  - Event location and date range
  - Event type keywords (battle, dedication, victory, law)
- Create **Communication/Evidence nodes** for each source:
  - Full text transcription
  - Material type (marble, bronze, papyrus)
  - Dimensions and physical description
  - Findspot (linked to Place nodes via Pleiades/GeoNames)
  - Date range (linked to Year nodes)
- Link to Event with typed role:
  - `PRIMARY_EPIGRAPHIC_EVIDENCE`: Inscription directly commemorating event
  - `CONTEMPORARY_DOCUMENT`: Papyrus from event's time period referencing it
  - `LATER_COMMEMORATIVE`: Post-event memorial or historical inscription
- **Raise Event confidence** when at least one epigraphic record corroborates participants/date/place

**Confidence rule**: Event with EDH/TM textual evidence = +0.20 confidence (up to 0.95)

```cypher
// Tier 2: EDH inscription evidence
MATCH (event:Event {label: "Battle of Pharsalus"})
WITH event
// Search EDH for inscriptions mentioning event participants
CALL apoc.load.json("https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search?person=Caesar") 
YIELD value
UNWIND value.items AS inscription
MERGE (ev:Evidence {edh_id: inscription.id})
SET ev.type = "inscription",
    ev.material = inscription.materialDescription,
    ev.text_latin = inscription.text,
    ev.findspot = inscription.findspot,
    ev.date_range = [inscription.notBefore, inscription.notAfter],
    ev.dimensions = inscription.dimensions
CREATE (ev)-[:DOCUMENTS {role: "PRIMARY_EPIGRAPHIC_EVIDENCE"}]->(event)
// Link to place
MERGE (place:Place {pleiades_id: inscription.pleiadesId})
CREATE (ev)-[:FOUND_AT]->(place)
// Link to date
CREATE (ev)-[:DATED_TO]->(year:Year {iso_year: inscription.middleDate})
// Boost event confidence
SET event.evidence_count = coalesce(event.evidence_count, 0) + 1,
    event.confidence_tier = 2,
    event.base_confidence = event.base_confidence + 0.20
```

```cypher
// Tier 2: Trismegistos documentary papyri
MATCH (event:Event)-[:HAS_PARTICIPANT]->(person:Person)
WITH event, person
MATCH (person)-[:SAME_AS]->(tm:TrismegistosPerson)
WITH event, tm
CALL apoc.load.json("https://www.trismegistos.org/text/search?person_id=" + tm.id) 
YIELD value
UNWIND value.texts AS text
MERGE (doc:Document {tm_text_id: text.id})
SET doc.type = text.type,
    doc.material = text.material,
    doc.provenance = text.provenance,
    doc.date = text.date
MERGE (ev:Evidence {id: "ev_tm_" + text.id})
SET ev.type = "documentary_papyrus",
    ev.text_content = text.transcription
CREATE (ev)-[:DOCUMENTS {role: "CONTEMPORARY_DOCUMENT"}]->(event)
CREATE (ev)-[:SOURCE_DOCUMENT]->(doc)
SET event.documentary_evidence_count = coalesce(event.documentary_evidence_count, 0) + 1
```

#### **Tier 3: Multi-Source Claims with HiCO Modeling**

**Purpose**: Model each historical statement as a Claim with full provenance, allowing multiple conflicting assertions per event

**Authorities**: All sources (primary inscriptions/papyri, literary narratives, modern scholarly reconstructions)

**How to use**:
- For each Event, create multiple Claim nodes representing different source assertions:
  - **Claimant**: Livy, Polybius, EDH inscription EDH12345, modern historian
  - **Claim content**: Specific assertion (date, outcome, casualty count, motive)
  - **Target**: The Event node
  - **Claim type**: Primary evidence vs. secondary narrative vs. scholarly interpretation
- Use federation sources to classify claim types:
  - **Primary evidence**: EDH, Trismegistos papyri, archaeological reports
  - **Secondary narrative**: Literary sources (Livy, Plutarch, Tacitus)
  - **Tertiary reconstruction**: Modern scholarly works, Wikipedia
- Enable **framework-specific claim weighting**:
  - Source-critical framework: Privilege epigraphy > papyri > literary narrative
  - Great Man framework: Privilege biographical literary sources
  - Marxist framework: Privilege economic documentary evidence
- Store all claims, expose conflicts, allow adjudication

**Confidence rule**: Multi-source claims with explicit conflict modeling = highest rigor (0.95-0.98 for well-adjudicated events)

```cypher
// Tier 3: Multi-source claim modeling
MATCH (event:Event {label: "Battle of Pharsalus"})
WITH event
// Claim 1: Livy's narrative account
MERGE (livy:Author {name: "Livy"})
CREATE (claim1:Claim {id: "claim_livy_pharsalus_date"})
SET claim1.content = "Battle occurred in 48 BCE during consulship of Caesar",
    claim1.claim_type = "date_assertion",
    claim1.date_value = date("-048-08-09"),
    claim1.source_type = "secondary_narrative",
    claim1.confidence = 0.85
CREATE (claim1)-[:MADE_BY]->(livy)
CREATE (claim1)-[:ABOUT]->(event)

// Claim 2: Epigraphic evidence (EDH inscription)
MATCH (inscription:Evidence {edh_id: "HD012345"})
CREATE (claim2:Claim {id: "claim_edh12345_pharsalus"})
SET claim2.content = "Inscription commemorates Caesar's victory, dated by consulship",
    claim2.claim_type = "event_confirmation",
    claim2.date_value = date("-048"),
    claim2.source_type = "primary_epigraphic",
    claim2.confidence = 0.95
CREATE (claim2)-[:DERIVED_FROM]->(inscription)
CREATE (claim2)-[:ABOUT]->(event)

// Claim 3: Conflicting modern scholarly reconstruction
MERGE (scholar:Author {name: "Smith, J."})
CREATE (claim3:Claim {id: "claim_smith_pharsalus_redate"})
SET claim3.content = "Re-dating to July 48 BCE based on astronomical calculations",
    claim3.claim_type = "date_assertion",
    claim3.date_value = date("-048-07-15"),
    claim3.source_type = "modern_reconstruction",
    claim3.confidence = 0.75
CREATE (claim3)-[:MADE_BY]->(scholar)
CREATE (claim3)-[:ABOUT]->(event)

// Model explicit conflict
CREATE (claim3)-[:CONFLICTS_WITH {
  conflict_type: "date_precision",
  difference: "~1 month",
  adjudication: "Livy's consulship date preferred, supported by EDH evidence"
}]->(claim1)

// Set event confidence based on claim constellation
WITH event, collect(claim1) + collect(claim2) + collect(claim3) AS claims
SET event.claim_count = size(claims),
    event.primary_evidence_count = size([c IN claims WHERE c.source_type = "primary_epigraphic"]),
    event.confidence_tier = 3,
    event.base_confidence = 0.95  // High confidence due to primary + secondary corroboration
```

**Outcome**: Events become nodes anchored by multi-source claims, not flat facts. Frameworks can weight claims differently, conflicts are explicit, and provenance is complete.

---

## **R.4 Federation Usage Patterns by Authority**

This section provides concrete guidance for leveraging each major federation authority within Chrystallum's architecture.

### **R.4.1 Wikidata** (Central Hub, Layer 2, 0.90 Confidence Floor)

**Role**: Identity hub and router

**How to leverage**:
1. **Always resolve candidate entities to QID first**
   - Use labels, descriptions, aliases for disambiguation
   - Check P31 (instance of) and P279 (subclass of) for type validation
   - Use P361 (part of) for hierarchical context

2. **Use external ID properties as federation jump-off points**
   - P214 → VIAF (persons)
   - P1584 → Pleiades (ancient places)
   - P1566 → GeoNames (modern places)
   - P2192 → EDH (inscriptions)
   - P1958 → Trismegistos Places
   - P4230 → Trismegistos Texts
   - P227 → GND (German authority)
   - P2950 → Nomisma (numismatics)

3. **Extract event/period seeds from Wikidata structure**
   - Query events by type, participant, period, or location
   - Use as discovery layer for entities not yet in your graph
   - Treat all Wikidata assertions as *provisional*, requiring domain authority confirmation

4. **Store Wikidata provenance but don't treat as final authority**
   - Keep QID for linking and discovery
   - Overwrite Wikidata values when domain authorities provide better data
   - Track when Wikidata and domain authorities conflict

**Cypher pattern**:
```cypher
// Wikidata as router to domain authorities
MATCH (candidate:Entity {label: $label})
CALL apoc.load.json("https://www.wikidata.org/wiki/Special:EntityData/" + $qid + ".json")
YIELD value
WITH candidate, value.entities[$qid] AS wd_entity
// Store Wikidata link
MERGE (wd:WikidataEntity {qid: $qid})
SET wd.label = wd_entity.labels.en.value,
    wd.description = wd_entity.descriptions.en.value
CREATE (candidate)-[:ALIGNED_WITH {confidence: 0.90, layer: 2}]->(wd)
// Extract external IDs for federation
WITH candidate, wd_entity.claims AS claims
UNWIND keys(claims) AS property
WHERE property STARTS WITH "P" AND claims[property][0].mainsnak.datatype = "external-id"
WITH candidate, property, claims[property][0].mainsnak.datavalue.value AS external_id
MERGE (ext:ExternalID {property: property, value: external_id})
CREATE (candidate)-[:HAS_EXTERNAL_ID {property: property}]->(ext)
```

---

### **R.4.2 Pleiades** (Ancient Places Backbone)

**Role**: Authority for ancient geographic concepts

**How to leverage**:
1. **Resolve to Pleiades ID via Wikidata P1584**
   - Treat Pleiades as canonical ancient place identifier
   - Store Pleiades URI as primary external reference

2. **Pull structured geographic data**
   - Coordinate ranges (often polygons or representative points)
   - Ancient name variants (Greek, Latin, indigenous)
   - Modern name variants
   - Temporal validity periods (which historical periods place exists in)
   - Connection types (at, near, within for related places)

3. **Use temporal validity to constrain events**
   - Events at a place must fall within its active period
   - Flag anachronistic references for review
   - Support geo-temporal federation (place-period joint constraints)

4. **Handle coordinate uncertainty appropriately**
   - Pleiades coordinates often represent approximate area, not precise point
   - Use coordinate ranges for spatial queries, not exact positioning
   - Prefer Pleiades conceptual place over GeoNames precise coordinates for historical context

**Cypher pattern**:
```cypher
// Pleiades place enrichment
MATCH (place:Place)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id:ExternalID)
WITH place, pleiades_id.value AS pid
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pid + "/json") YIELD value
MERGE (pleiades:PleiadesPlace {id: pid})
SET pleiades.title = value.title,
    pleiades.ancient_names = [n IN value.names WHERE n.language IN ['grc', 'la', 'egy'] | 
                              {transcription: n.nameTransliterated, 
                               attestations: n.attestations,
                               language: n.language}],
    pleiades.modern_names = [n IN value.names WHERE n.language = 'en' | n.romanized],
    pleiades.coordinate_point = point({latitude: value.reprPoint[1], longitude: value.reprPoint[0]}),
    pleiades.periods = [p IN value.features[0].properties.periods | p],
    pleiades.temporal_range = {
      start: value.features[0].properties.minDate,
      end: value.features[0].properties.maxDate
    },
    pleiades.place_types = value.placeTypes
CREATE (place)-[:SAME_AS {confidence: 0.95, authority: "Pleiades"}]->(pleiades)
// Apply temporal validity constraint
WITH place, pleiades
MATCH (place)<-[:OCCURRED_AT]-(event:Event)
WHERE event.year < pleiades.temporal_range.start 
   OR event.year > pleiades.temporal_range.end
SET event.temporal_flags = coalesce(event.temporal_flags, []) + ["anachronistic_place_usage"],
    event.requires_review = true
```

---

### **R.4.3 Trismegistos** (Texts, People, Local Geography)

**Role**: Epigraphic/papyrological hub for documentary sources

**How to leverage**:

#### **TMPeople (Trismegistos People)**
1. **Check documentary source attestation**
   - Search for person by name or external ID
   - Get count of papyri/inscriptions mentioning person
   - Pull date range and geographic distribution of attestations

2. **Combine with PIR/PLRE for elite disambiguation**
   - Wikidata-only + no TM = textual figure, low confidence
   - Wikidata + TM + PIR = documentary evidence of elite, high confidence

3. **Use attestations as confidence bump**
   - TM presence = structurally stronger than Wikidata-only
   - Add +0.15 confidence for primary documentary evidence

#### **TMGeo (Trismegistos Geography)**
1. **Village/quarter-level geography**
   - Especially valuable for Egypt and Eastern Mediterranean
   - Use for fine-grained provenance of papyri
   - Map to Pleiades parent regions for global anchoring

2. **Administrative hierarchies**
   - Nome, toparchy, village structures for Greco-Roman Egypt
   - Use for population studies and micro-regional analysis

#### **TMTexts (Trismegistos Texts)**
1. **Create Communication/Evidence nodes for each text**
   - Full text transcription (when available)
   - Material type (papyrus, ostracon, parchment)
   - Provenance (findspot)
   - Date range
   - Text type (letter, contract, petition, etc.)

2. **Link texts to Events, Persons, Places**
   - Use role annotations: `PRIMARY_EPIGRAPHIC_EVIDENCE`, `CONTEMPORARY_DOCUMENT`
   - Build provenance chains: Evidence → Person → Event → Place → Date

**Cypher pattern**:
```cypher
// Trismegistos People enrichment
MATCH (person:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]-()) // P4343 = TM Person ID
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]->(tm_id:ExternalID)
WITH person, tm_id.value AS tm_person_id
CALL apoc.load.json("https://www.trismegistos.org/person/" + tm_person_id) YIELD value
MERGE (tm:TrismegistosPerson {id: tm_person_id})
SET tm.name = value.name,
    tm.document_count = value.attestations_count,
    tm.date_range = [value.date_min, value.date_max],
    tm.locations = value.attestation_places
CREATE (person)-[:SAME_AS {confidence: 0.90, evidence: "documentary"}]->(tm)
SET person.documentary_attestations = tm.document_count,
    person.confidence_boost = 0.15

// Trismegistos Texts → Evidence nodes
MATCH (tm:TrismegistosPerson)
WITH tm
CALL apoc.load.json("https://www.trismegistos.org/text/search?person_id=" + tm.id) YIELD value
UNWIND value.texts AS text
MERGE (doc:Document {tm_text_id: text.tm_id})
SET doc.type = text.text_type,
    doc.material = text.material,
    doc.date_range = [text.date_min, text.date_max],
    doc.provenance = text.provenance
MERGE (ev:Evidence {id: "ev_tm_" + text.tm_id})
SET ev.type = "documentary_papyrus",
    ev.text_content = text.transcription,
    ev.material = text.material
CREATE (ev)-[:SOURCE_DOCUMENT]->(doc)
CREATE (ev)-[:DOCUMENTS]->(person:Person)-[:SAME_AS]->(tm)
// Link to place via TMGeo
MERGE (place:Place {tm_geo_id: text.place_id})
CREATE (ev)-[:FOUND_AT]->(place)
```

---

### **R.4.4 EDH** (Latin Inscriptions)

**Role**: Authority for Latin inscriptions and their findspots/dates

**How to leverage**:
1. **Search inscriptions mentioning entities**
   - Query by person name, place, date range
   - Use EDH API for full-text search

2. **Create Evidence nodes with full material context**
   - Full text (original and translation when available)
   - Material (marble, bronze, limestone, etc.)
   - Dimensions and physical description
   - Findspot (link to Pleiades/GeoNames)
   - Date range (link to Year nodes)
   - Current location (museum/collection)

3. **Link to Events with typed roles**
   - `PRIMARY_EPIGRAPHIC_EVIDENCE`: Inscription directly commemorating event
   - `DEDICATORY_INSCRIPTION`: Honors person/god related to event
   - `BUILDING_INSCRIPTION`: Documents construction or renovation
   - `FUNERARY_INSCRIPTION`: Provides biographical data

4. **Raise Event confidence when EDH corroborates**
   - At least one EDH record mentioning event participants/place/date
   - Add +0.20 to event confidence
   - Mark event as "epigraphically attested"

**Cypher pattern**:
```cypher
// EDH inscription search and Evidence node creation
MATCH (person:Person {label: "Julius Caesar"})
WITH person
CALL apoc.load.json("https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search?person=" + person.label) 
YIELD value
UNWIND value.items AS inscription
MERGE (ev:Evidence {edh_id: inscription.id})
SET ev.type = "latin_inscription",
    ev.material = inscription.attributes.material,
    ev.text_latin = inscription.transcription.latin,
    ev.text_translation = inscription.transcription.translation,
    ev.dimensions = {
      height_cm: inscription.attributes.height,
      width_cm: inscription.attributes.width,
      depth_cm: inscription.attributes.depth
    },
    ev.date_range = [inscription.dates.notBefore, inscription.dates.notAfter],
    ev.findspot_description = inscription.findspot.description,
    ev.current_location = inscription.repository
CREATE (ev)-[:DOCUMENTS {role: "epigraphic_attestation"}]->(person)
// Link to Place
MERGE (findspot:Place {pleiades_id: inscription.findspot.pleiadesId})
CREATE (ev)-[:FOUND_AT]->(findspot)
// Link to date
WITH ev, inscription.dates.notBefore AS start_year, inscription.dates.notAfter AS end_year
UNWIND range(start_year, end_year) AS year_val
MERGE (year:Year {iso_year: year_val})
CREATE (ev)-[:DATED_TO]->(year)
// Boost person confidence
MATCH (person)<-[:DOCUMENTS]-(ev)
SET person.epigraphic_attestations = coalesce(person.epigraphic_attestations, 0) + 1,
    person.base_confidence = person.base_confidence + 0.20
```

---

### **R.4.5 VIAF** (People and Works Disambiguation)

**Role**: Name authority for persons and works

**How to leverage**:
1. **Resolve to VIAF via Wikidata P214**
   - VIAF provides canonical name forms in multiple languages
   - Links to national authority files (LoC, BnF, DNB, etc.)

2. **Use for identity confirmation**
   - Single clean VIAF cluster = strong identity
   - Multiple clusters = name collision, disambiguation needed
   - Check co-references for same-person validation

3. **Separate Person vs. Author vs. Subject roles**
   - VIAF work lists distinguish person as author vs. subject of works
   - Use for scholarly reception tracking
   - Connect Person node to WorksAbout and WorksBy lists

4. **Attestation strength matrix**:
   - Wikidata-only = textual/unconfirmed (0.70)
   - Wikidata + VIAF = author/creator authority (0.80)
   - VIAF + Trismegistos + PIR = strongly attested historical person (0.90)

**Cypher pattern**:
```cypher
// VIAF person enrichment
MATCH (person:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P214"}]-()) // P214 = VIAF ID
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id:ExternalID)
WITH person, viaf_id.value AS viaf_id_val
CALL apoc.load.json("https://viaf.org/viaf/" + viaf_id_val + "/viaf.json") YIELD value
MERGE (viaf:VIAFRecord {id: viaf_id_val})
SET viaf.canonical_names = [n IN value.mainHeadings.data | n.text],
    viaf.name_variants = [n IN value.x400s.x400 | n.datafield.subfield[0].text],
    viaf.national_authorities = [s IN value.sources.source | s],
    viaf.works_count = size(value.titles.work)
CREATE (person)-[:SAME_AS {confidence: 0.85, authority: "VIAF"}]->(viaf)
SET person.canonical_name = viaf.canonical_names[0],
    person.name_variants = viaf.name_variants
// Extract works relationships
WITH person, viaf, value.titles.work AS works
UNWIND works AS work
MERGE (w:Work {title: work.title})
CREATE (person)-[:AUTHOR_OF]->(w)
// Check attestation strength
WITH person
OPTIONAL MATCH (person)-[:SAME_AS]->(tm:TrismegistosPerson)
OPTIONAL MATCH (person)-[:SAME_AS]->(pir:PIREntry)
WITH person, tm, pir
SET person.attestation_level = CASE
  WHEN tm IS NOT NULL AND pir IS NOT NULL THEN "strongly_attested"
  WHEN tm IS NOT NULL THEN "documentary_attested"
  ELSE "textual_only"
END,
person.base_confidence = CASE
  WHEN tm IS NOT NULL AND pir IS NOT NULL THEN 0.95
  WHEN tm IS NOT NULL THEN 0.85
  ELSE 0.75
END
```

---

### **R.4.6 GeoNames/OSM** (Modern Coordinates)

**Role**: Modern geographic ground truth for visualization

**How to leverage**:
1. **Pull precise coordinates and bounding boxes**
   - Use GeoNames API via Wikidata P1566
   - Get latitude, longitude, elevation
   - Pull admin hierarchy (country, state, region)
   - Get bounding box for spatial queries

2. **Use ONLY for UI maps and modern context**
   - Never as primary historical geography
   - Historical geography comes from Pleiades/DARE/TM_Geo
   - GeoNames provides visualization layer only

3. **Map ancient → modern for user experience**
   - Show "ancient Rome" on modern Italy map
   - Provide modern place names for context
   - Calculate modern travel distances for comparison

**Critical constraint**: Roman provinces, ancient boundaries, and historical place concepts are NOT derived from modern geography. Pleiades/DARE provide historical ontology; GeoNames provides visual convenience only.

**Cypher pattern**:
```cypher
// GeoNames modern coordinates (visualization-only)
MATCH (place:Place)-[:SAME_AS]->(pleiades:PleiadesPlace)
WITH place, pleiades
MATCH (place)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P1566"}]-()) // P1566 = GeoNames ID
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1566"}]->(gn_id:ExternalID)
WITH place, gn_id.value AS geonames_id
CALL apoc.load.json("http://api.geonames.org/getJSON?geonameId=" + geonames_id + "&username=demo") 
YIELD value
MERGE (gn:GeoNamesPlace {id: geonames_id})
SET gn.lat = toFloat(value.lat),
    gn.lng = toFloat(value.lng),
    gn.modern_name = value.name,
    gn.country = value.countryName,
    gn.admin1 = value.adminName1,
    gn.admin2 = value.adminName2,
    gn.bbox = value.bbox
CREATE (place)-[:HAS_MODERN_LOCATION {
  usage: "visualization_only",
  ontology_role: "none"
}]->(gn)
SET place.visualization_point = point({latitude: gn.lat, longitude: gn.lng})
// CRITICAL: Flag as non-ontological
WITH place, gn
SET gn:VisualizationOnly,
    gn.warning = "Modern coordinates only. Use Pleiades for historical geography."
```

---

### **R.4.7 PeriodO** (Period Semantics)

**Role**: Authority for named historical periods and temporal intervals

**How to leverage**:
1. **Resolve period labels to PeriodO IDs**
   - Match free-text period names to PeriodO entries
   - Get explicit start-end bounds (often BCE/CE year ranges)
   - Pull spatial scope (where period applies)

2. **Attach Period nodes to temporal envelopes**
   - Events: Period indicates when event could occur
   - Persons: Active period for person's life span
   - Places: Valid period for place existence/usage
   - Concepts: Period when concept was relevant (e.g., "Roman citizenship" only during Roman period)

3. **Check temporal plausibility**
   - Event cannot occur outside its named period bounds
   - Flag violations for review
   - Allow explicit override when justified (e.g., retroactive term use)

4. **Support period-based lensing**
   - "Show only Late Republic events"
   - "Filter to Augustan Age persons"
   - Enable comparative analysis across periods

**Cypher pattern**:
```cypher
// PeriodO period resolution and temporal constraints
MATCH (event:Event {period_label: "Late Republic"})
WITH event
CALL apoc.load.json("http://perio.do/periods.json") YIELD value
WITH event, value.periodCollections AS collections
UNWIND collections AS collection
UNWIND collection.definitions AS period
WHERE period.label CONTAINS "Late Republic" OR period.spatialCoverageDescription CONTAINS "Rome"
WITH event, period
WHERE period.label CONTAINS event.period_label
MERGE (p:Period {periodo_id: period.id})
SET p.label = period.label,
    p.start_year = toInteger(split(period.start.in.value, "-")[0]),
    p.end_year = toInteger(split(period.stop.in.value, "-")[0]),
    p.spatial_scope = period.spatialCoverage,
    p.authority = period.source
CREATE (event)-[:DURING_PERIOD]->(p)
// Validate temporal plausibility
WITH event, p
WHERE event.year < p.start_year OR event.year > p.end_year
SET event.temporal_violations = coalesce(event.temporal_violations, []) + [
  "Event year " + event.year + " outside period bounds [" + p.start_year + ", " + p.end_year + "]"
],
event.requires_review = true
// Enable period-based lensing
WITH event, p
MATCH (person:Person)-[:PARTICIPATED_IN]->(event)
CREATE (person)-[:ACTIVE_IN_PERIOD]->(p)
```

---

### **R.4.8 Getty AAT + LCSH/FAST** (Concepts and Institutions)

**Role**: Deep concept hierarchies (AAT) + library-grade topic hierarchies (LCSH/FAST)

**How to leverage**:

#### **Getty AAT (Art & Architecture Thesaurus)**
1. **Assign to abstract concepts and institutions**
   - For nodes like Concept, Institution, LegalRestriction, Organization
   - Get ontological type (e.g., "colony (settlements)", "senate (legislative bodies)", "taxation (fiscal function)")

2. **Use hierarchical structure**
   - Broader/narrower term navigation
   - Related terms for discovery
   - Scope notes for definition

3. **Enable faceted navigation**
   - "Show all events involving colonial institutions"
   - "Find concepts related to Roman taxation"
   - Support SFA concept spine building

#### **LCSH/FAST (Library of Congress Subject Headings / FAST)**
1. **Bibliographic crosswalk**
   - Already core to your Subject backbone
   - Assign LCSH/FAST to SubjectConcepts for library catalog linking

2. **Authority precedence (from Appendix P)**
   - Tier 1: LCSH/FAST (highest precedence for subjects)
   - Tier 2: LCC/CIP (second tier)
   - Tier 3: Wikidata + domain authorities (specialists)

3. **Agent routing**
   - LCC ranges map to specialist agent scopes
   - LCSH headings trigger facet assignments

**Cypher pattern**:
```cypher
// Getty AAT concept enrichment
MATCH (concept:Concept {label: "Roman Senate"})
WITH concept
CALL apoc.load.json("http://vocab.getty.edu/aat/300025306.json") YIELD value
MERGE (aat:AATConcept {id: "300025306"})
SET aat.term = value.prefLabel,
    aat.scope_note = value.scopeNote,
    aat.broader_terms = [b IN value.broader | b.label],
    aat.narrower_terms = [n IN value.narrower | n.label],
    aat.related_terms = [r IN value.related | r.label]
CREATE (concept)-[:SAME_AS {confidence: 0.90, authority: "Getty AAT"}]->(aat)
SET concept.ontological_type = aat.term,
    concept.hierarchy = aat.broader_terms

// LCSH/FAST subject heading assignment
WITH concept
MATCH (subject:Subject {lcsh_heading: "Rome--Politics and government--265-30 B.C."})
CREATE (concept)-[:HAS_SUBJECT]->(subject)
// Enable faceted query
SET concept.facets = ["GOVERNANCE", "POLITICAL_INSTITUTIONS"]

// Crosswalk for bibliographic discovery
WITH concept, subject
MATCH (work:Work)-[:ABOUT_SUBJECT]->(subject)
CREATE (concept)-[:DOCUMENTED_IN_WORKS]->(work)
```

---

## **R.5 Potential Federation Enhancements**

Building on the six operational federations, these five enhancements represent logical next steps for deepening Chrystallum's multi-authority integration.

### **R.5.1 Evidence Federation**

**Goal**: Unify source documents, passages, citations as first-class Evidence nodes linked to Claims and Reviews

**Current state**: Evidence nodes exist for EDH inscriptions and Trismegistos texts, but not unified across all source types

**Enhancement**:
- Create Evidence node schema for:
  - Literary sources (Livy, Plutarch, Tacitus) with passage-level references
  - Numismatic evidence (coin types, legends, iconography)
  - Archaeological reports (excavation publications, artifact catalogs)
  - Modern scholarly works (with claim extraction)
- Typed evidence relationships:
  - `PRIMARY_EVIDENCE`: Contemporary documents, inscriptions, archaeological material
  - `SECONDARY_NARRATIVE`: Literary sources postdating events
  - `TERTIARY_SYNTHESIS`: Modern scholarly reconstructions
- Enable evidence-based confidence scoring:
  - Claims with primary evidence get +0.20 confidence
  - Multiple corroborating pieces of evidence compound boost
  - Conflicting evidence triggers review workflow

**Example structure**:
```cypher
(claim:Claim)-[:SUPPORTED_BY {weight: 0.85}]->(evidence:Evidence {type: "inscription"})
(claim:Claim)-[:CONTRADICTED_BY {weight: 0.70}]->(evidence2:Evidence {type: "literary_narrative"})
(evidence)-[:CITED_IN]->(work:ModernWork)
(evidence)-[:FOUND_AT]->(place:Place)
(evidence)-[:DATED_TO]->(year:Year)
```

---

### **R.5.2 Identity Federation**

**Goal**: Crosswalk people/places/events across multiple identity authorities (VIAF, GND, Wikidata, LoC)

**Current state**: VIAF used for persons, but no systematic crosswalk across all national authority files

**Enhancement**:
- Create IdentityCluster nodes that aggregate same-entity references across:
  - VIAF (international virtual authority)
  - GND (German National Library)
  - BnF (Bibliothèque nationale de France)
  - LoC (Library of Congress)
  - ISNI (International Standard Name Identifier)
- Confidence-based identity resolution:
  - Same identifier in 3+ authorities = high-confidence match (0.95+)
  - Conflicting identifiers = disambiguation required
  - Single-source identifier = provisional (0.75)
- Enable cross-system queries:
  - "Find all works about Caesar in any national library catalog"
  - "Resolve ambiguous 'Marcus Antonius' via authority crosswalk"

**Example structure**:
```cypher
(person:Person)-[:IDENTITY_CLUSTER]->(cluster:IdentityCluster)
(cluster)-[:VIAF_ID {confidence: 0.90}]->(viaf:ExternalID {value: "12345"})
(cluster)-[:GND_ID {confidence: 0.92}]->(gnd:ExternalID {value: "67890"})
(cluster)-[:LOC_ID {confidence: 0.88}]->(loc:ExternalID {value: "n12345"})
SET cluster.match_confidence = avg([0.90, 0.92, 0.88]) // 0.90
```

---

### **R.5.3 Authority Conflict Federation**

**Goal**: Formal conflict-resolution layer when LCSH/FAST/Wikidata/PeriodO disagree, with stored adjudication rules

**Current state**: Conflicts detected (e.g., via `CONFLICTS_WITH` edges), but resolution is ad-hoc

**Enhancement**:
- Create ConflictResolution nodes capturing:
  - Conflicting authorities (Source A vs. Source B)
  - Conflict type (date_range, place_name, person_identity, etc.)
  - Source values (what each authority claims)
  - Resolution rule (precedence policy, expert adjudication, majority vote)
  - Resolution outcome (chosen value, flagged as unresolvable)
- Implement precedence policies:
  - Subjects: LCSH/FAST > LCC > Wikidata (from Appendix P)
  - Ancient Places: Pleiades > Wikidata > GeoNames
  - Dates: Primary sources (EDH, TM) > literary sources > modern reconstruction
- Enable audit trail:
  - Track all conflicts over time
  - Report authority agreement rates
  - Identify systematic divergences requiring policy updates

**Example structure**:
```cypher
(source_a:Authority {name: "LCSH"})-[:ASSERTS {value: "Roman Republic"}]->(entity)
(source_b:Authority {name: "Wikidata"})-[:ASSERTS {value: "Roman Kingdom"}]->(entity)
CREATE (conflict:ConflictResolution {
  type: "period_name",
  source_a: "LCSH",
  source_a_value: "Roman Republic",
  source_b: "Wikidata",
  source_b_value: "Roman Kingdom",
  resolution_rule: "LCSH_precedence",
  chosen_value: "Roman Republic",
  adjudication_date: date(),
  adjudicator: "system_policy"
})
CREATE (source_a)-[:CONFLICTS_WITH]->(conflict)-[:RESOLVED_BY]->(entity)
```

---

### **R.5.4 Geo-Temporal Federation**

**Goal**: Joint place-time validity layer for historical boundaries and names per period

**Current state**: Pleiades provides temporal validity, PeriodO provides period bounds, but no integrated place-period constraint model

**Enhancement**:
- Create PlacePeriodValidity nodes capturing:
  - Place ID (Pleiades)
  - Period ID (PeriodO)
  - Valid names for that place during that period
  - Boundary changes (e.g., "Mesopotamia" boundaries differ across Persian, Hellenistic, Roman periods)
  - Governance changes (colony → municipium → colonia; client kingdom → province)
- Enable period-aware queries:
  - "Show all places in 'Roman Britain' period" (place exists AND period overlaps AND place under Roman control)
  - "What was 'Constantinople' called in 100 BCE?" → "Byzantium"
  - "Which provinces existed during the Severan Dynasty?"
- Support dynamic historical maps:
  - Render boundaries appropriate to selected period
  - Show place name forms contemporary to period
  - Track expansion/contraction of empires over time

**Example structure**:
```cypher
(place:Place {label: "Constantinople"})-[:VALID_IN_PERIOD]->(ppv:PlacePeriodValidity {
  period_id: "late_antiquity",
  names: ["Constantinople", "Nova Roma"],
  governance: "imperial_capital",
  boundaries: "walls_of_constantine.geojson"
})
(place)-[:VALID_IN_PERIOD]->(ppv2:PlacePeriodValidity {
  period_id: "classical_period",
  names: ["Byzantium"],
  governance: "Greek_colony",
  boundaries: "archaic_byzantium.geojson"
})
// Query with period constraint
MATCH (e:Event)-[:OCCURRED_AT]->(p:Place)-[:VALID_IN_PERIOD]->(ppv)
WHERE e.year >= ppv.period_start AND e.year <= ppv.period_end
RETURN p.label, ppv.names[0] AS period_name // Use name appropriate to event's period
```

---

### **R.5.5 Agent Capability Federation**

**Goal**: Explicit machine-readable mapping from agent scope → LCC ranges/facets/periods for deterministic routing and coverage audits

**Current state**: Agent scopes defined conceptually (in `facet_agent_system_prompts.json`), but not fully machine-readable for automated routing

**Enhancement**:
- Create AgentCapability nodes for each Specialist Facet Agent:
  - LCC call number ranges (e.g., "D51-D90" for Roman History SFA)
  - Facet tags (e.g., ["WARFARE", "GOVERNANCE"] for Military History SFA)
  - Period ranges (e.g., "-500/500" for Classical Period SFA)
  - Geographic scope (e.g., "Mediterranean" for Ancient Mediterranean SFA)
- Implement deterministic routing:
  - Given entity with LCC + facet + period + place → compute best-match SFA
  - Score overlap between entity properties and agent capabilities
  - Route to agent with highest overlap score
- Enable coverage audits:
  - Identify gaps (LCC ranges with no assigned agent)
  - Identify overlaps (multiple agents claiming same scope)
  - Report agent workload (how many entities routed to each agent)
  - Validate agent specialization (check if routed entities truly match declared scope)

**Example structure**:
```cypher
MERGE (sfa:SpecialistFacetAgent {name: "Roman_History_SFA"})
MERGE (cap:AgentCapability {id: "cap_roman_history"})
SET cap.lcc_ranges = ["D51-D59", "D60-D69", "D70-D79"],
    cap.facets = ["GOVERNANCE", "WARFARE", "LEGAL_TOPICS", "ECONOMICS"],
    cap.period_start = -753,
    cap.period_end = 476,
    cap.geographic_scope = ["Italy", "Mediterranean", "Western_Europe"]
CREATE (sfa)-[:HAS_CAPABILITY]->(cap)

// Routing query
MATCH (entity:Entity)
WHERE entity.lcc = "D62" 
  AND "GOVERNANCE" IN entity.facets
  AND entity.year >= -509 AND entity.year <= 27
WITH entity
MATCH (sfa:SpecialistFacetAgent)-[:HAS_CAPABILITY]->(cap:AgentCapability)
WHERE entity.lcc STARTS WITH cap.lcc_ranges[0][0..2] // Match LCC prefix
  AND ANY(facet IN entity.facets WHERE facet IN cap.facets)
  AND entity.year >= cap.period_start AND entity.year <= cap.period_end
WITH entity, sfa, cap, 
     size([f IN entity.facets WHERE f IN cap.facets]) AS facet_overlap
ORDER BY facet_overlap DESC
LIMIT 1
MERGE (entity)-[:ROUTED_TO]->(sfa)
```

---

## **R.6 API Reference Summary**

| Federation | Wikidata Property | Entity Type | API Endpoint | Confidence Impact |
|------------|------------------|-------------|--------------|-------------------|
| **Pleiades** | P1584 | Place | `https://pleiades.stoa.org/places/[ID]/json` | +0.10 temporal validity |
| **Trismegistos People** | P4343 | Person | `https://www.trismegistos.org/person/[ID]` | +0.15 primary source |
| **Trismegistos Geo** | P1958 | Place | `https://www.trismegistos.org/place/[ID]` | +0.10 granular geo |
| **Trismegistos Texts** | P4230 | Text/Document | `https://www.trismegistos.org/text/[ID]` | +0.15 documentary evidence |
| **EDH** | P2192 | Inscription | `https://edh.ub.uni-heidelberg.de/data/api/inscriptions/[ID]` | +0.20 epigraphic evidence |
| **VIAF** | P214 | Person, Work | `https://viaf.org/viaf/[ID]/viaf.json` | +0.10 name authority |
| **GeoNames** | P1566 | Modern Location | `http://api.geonames.org/getJSON?geonameId=[ID]` | N/A (UI-only) |
| **PeriodO** | (label match) | Period | `http://perio.do/[ID]` | +0.10 temporal bounds |
| **Getty AAT** | P1014 | Concept | `http://vocab.getty.edu/aat/[ID].json` | +0.05 hierarchical type |
| **LCSH** | (subject match) | Subject | `https://id.loc.gov/authorities/subjects/[ID]` | Primary (Tier 1) |
| **FAST** | P2163 | Subject | `http://id.worldcat.org/fast/[ID]` | Primary (Tier 1) |
| **Wikidata** | (QID) | Universal | `https://www.wikidata.org/wiki/Special:EntityData/[QID].json` | 0.90 baseline (Layer 2) |

**Usage notes**:
- **Confidence Impact**: Typical boost to base confidence when this authority corroborates entity
- **Wikidata Property**: External ID property used to jump from Wikidata to domain authority
- **API Endpoint**: Template for direct authority access (replace `[ID]` with identifier)
- **"UI-only"**: Authority used for visualization/convenience, not primary ontology

---

## **R.7 Integration with Authority Precedence**

Federation strategy aligns with Chrystallum's tiered authority precedence model (defined in Section 4.4 and Appendix P).

### **R.7.1 Tier 1 (LCSH/FAST): Subject Authority Federation**

**Precedence**: Always check first for SubjectConcepts

**Federation pattern**:
1. Resolve subject string → LCSH heading or FAST topic
2. Pull LCSH hierarchy (broader/narrower terms)
3. Map to LCC call number range for agent routing
4. Cross-reference Wikidata P-codes for international alignment
5. Store mapping with `authority: "LCSH"` and `confidence: 0.95`

**Integration points**:
- **Agent routing**: LCSH/FAST → LCC → Specialist Facet Agent
- **Bibliographic crosswalk**: LCSH enables library catalog integration
- **Facet assignment**: LCSH headings trigger canonical facet tags
- **Conflict resolution**: LCSH overrides Wikidata for subject classification (per Appendix P §P.4)

**Example**:
```cypher
MATCH (entity:Entity {label: "Roman Senate"})
MERGE (lcsh:LCSHHeading {heading: "Rome--Politics and government--510-30 B.C."})
CREATE (entity)-[:HAS_SUBJECT {authority: "LCSH", confidence: 0.95, tier: 1}]->(lcsh)
SET entity.lcc_range = "JC85", // Derived from LCSH
    entity.routed_agent = "Roman_Governance_SFA"
```

---

### **R.7.2 Tier 2 (LCC/CIP): Fallback for Concepts Without LCSH/FAST Coverage**

**Precedence**: Second tier when LCSH/FAST unavailable

**Federation pattern**:
1. Check for LCSH/FAST first (Tier 1)
2. If not found, resolve to LCC call number directly
3. Use CIP (Cataloging in Publication) data for subjects
4. Still route to agents via LCC range
5. Store mapping with `authority: "LCC"` and `confidence: 0.85`

**Integration points**:
- **Gap coverage**: LCC provides broader classification when specific LCSH heading doesn't exist
- **Agent routing**: LCC ranges still enable deterministic agent routing
- **Hierarchy**: LCC provides coarse-grained hierarchy (D = History, D51-D90 = Ancient Rome)

**Example**:
```cypher
MATCH (entity:Entity {label: "Patrician-Plebeian Conflict"})
WHERE NOT EXISTS((entity)-[:HAS_SUBJECT]->(:LCSHHeading))
MERGE (lcc:LCCClass {call_number: "DG231-234"})
CREATE (entity)-[:CLASSIFIED_AS {authority: "LCC", confidence: 0.85, tier: 2}]->(lcc)
SET entity.routed_agent = "Roman_Social_History_SFA"
```

---

### **R.7.3 Tier 3 (Wikidata + Domain Authorities): Specialist Grounding**

**Precedence**: Use Wikidata as router, then jump to domain-specific authorities

**Federation pattern**:
1. Resolve entity → Wikidata QID (Layer 2, confidence 0.90)
2. Follow external ID properties to domain authorities:
   - **People**: VIAF, Trismegistos, PIR/PLRE
   - **Places**: Pleiades, Trismegistos Geo, DARE
   - **Events**: EDH, Trismegistos Texts, PeriodO
   - **Concepts**: Getty AAT, specialized thesauri
3. Domain authority confidence typically 0.90-0.95 (Tier 1 for their domain)
4. Wikidata serves as discovery, domain authority as canonical source

**Integration points**:
- **Two-hop enrichment**: Wikidata → external ID → domain authority graph
- **Cross-domain**: Wikidata enables linking across specialist silos
- **Provenance**: Track both Wikidata and domain authority as sources
- **Conflict resolution**: Domain authority overrides Wikidata when they disagree

**Example**:
```cypher
// Wikidata as router
MATCH (person:Person {label: "Marcus Tullius Cicero"})
MERGE (wd:WikidataEntity {qid: "Q1541"})
CREATE (person)-[:ALIGNED_WITH {confidence: 0.90, layer: 2, tier: 3}]->(wd)

// Jump to VIAF (person authority)
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id)
MERGE (viaf:VIAFRecord {id: viaf_id.value})
CREATE (person)-[:SAME_AS {authority: "VIAF", confidence: 0.90, tier: 3}]->(viaf)

// Jump to Trismegistos (documentary evidence)
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]->(tm_id)
MERGE (tm:TrismegistosPerson {id: tm_id.value})
CREATE (person)-[:SAME_AS {authority: "Trismegistos", confidence: 0.95, tier: 1_for_papyrology}]->(tm)

// Domain authority precedence: TM > VIAF > Wikidata for documentary evidence
SET person.documentary_confidence = 0.95 // TM provides primary source grounding
```

---

### **R.7.4 Crosswalk Pattern: Use Wikidata P-codes to Route to Domain Authority, Then Enrich Backward**

**Key principle**: Wikidata external ID properties (P-codes) function as federation routing keys, not final data sources.

**Crosswalk workflow**:
1. **Forward routing**: Entity → Wikidata QID → P-code → domain authority
2. **Data enrichment**: Pull canonical data from domain authority
3. **Backward propagation**: Enrich original entity with domain authority data
4. **Provenance tracking**: Store both Wikidata and domain source metadata
5. **Conflict handling**: When Wikidata and domain authority disagree, flag for resolution using precedence rules

**Crosswalk example (Place federation)**:
```cypher
// Step 1: Forward routing via Wikidata
MATCH (place:Place {label: "Tarraco"})
MERGE (wd:WikidataEntity {qid: "Q15695"})
CREATE (place)-[:ALIGNED_WITH {role: "discovery"}]->(wd)

// Step 2: Extract P1584 (Pleiades ID)
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)

// Step 3: Enrich from Pleiades (canonical ancient place authority)
WITH place, pleiades_id.value AS pid
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pid + "/json") YIELD value
MERGE (pleiades:PleiadesPlace {id: pid})
SET pleiades.canonical_names = value.names,
    pleiades.temporal_validity = value.temporalRange,
    pleiades.coordinates = value.reprPoint
CREATE (place)-[:SAME_AS {authority: "Pleiades", confidence: 0.95}]->(pleiades)

// Step 4: Backward propagation to original Place node
SET place.ancient_names = [n IN value.names WHERE n.language IN ['la', 'grc'] | n.nameTransliterated],
    place.valid_periods = value.periods,
    place.primary_authority = "Pleiades",
    place.enrichment_date = datetime()

// Step 5: Conflict detection (if Wikidata and Pleiades disagree)
WITH place, wd, pleiades
WHERE wd.label <> pleiades.canonical_names[0]
CREATE (conflict:ConflictResolution {
  type: "place_name",
  wikidata_value: wd.label,
  pleiades_value: pleiades.canonical_names[0],
  resolution: "Pleiades_precedence",
  chosen_value: pleiades.canonical_names[0]
})
SET place.label = pleiades.canonical_names[0] // Pleiades wins per precedence rule
```

**Crosswalk pattern advantages**:
- **Leverages Wikidata's breadth** for discovery and initial linkage
- **Respects domain authorities' depth** for canonical data
- **Traceable provenance** with explicit routing path
- **Conflict-aware** with adjudication rules
- **Bidirectional enrichment**: Wikidata improves coverage, domain authorities improve quality

---

## **R.8 Source Files**

This appendix synthesizes content from the following Federation layer documentation:

1. **[Federation/2-16-26-FederationCandidates.md](Federation/2-16-26-FederationCandidates.md)** (170 lines)
   - Federation usage patterns for 8 major authorities
   - Role → How to leverage structure for each federation
   - Stacked evidence ladder principle

2. **[Federation/FederationUsage.txt](Federation/FederationUsage.txt)** (241 lines)
   - Detailed stacked evidence ladder for People, Places, Events
   - Tier-by-tier enrichment patterns
   - Confidence rules and attestation strength matrix
   - Operationalization guidance for ingestion, validation, and lensing phases

3. **[Federation/2-12-26-federations.md](Federation/2-12-26-federations.md)**
   - 6 current operational federations
   - 5 potential federation enhancements
   - Wikidata as "federation broker, not final authority" principle
   - Federation architecture: two-hop enrichment, typed edges, Layer 2 positioning

4. **[Federation/Federation Impact Report_ Chrystallum Data Targets.md](Federation/Federation Impact Report_ Chrystallum Data Targets.md)** (not merged)
   - Detailed API reference with endpoints, parameters, response formats
   - Kept as separate technical reference for implementation
   - Not duplicated here to avoid excessive length

---

## **R.9 Related Sections**

Federation strategy integrates with multiple existing architecture components:

- **Section 4.4: Multi-Authority Model**  
  Defines Tier 1/2/3 precedence policy that governs federation conflict resolution

- **Appendix K: Wikidata Integration Patterns**  
  Detailed patterns for Wikidata as discovery layer and external ID routing

- **Appendix L: CIDOC-CRM Integration Guide**  
  Relationship vocabulary aligned with CIDOC E-classes and P-codes, used in federation edges

- **Appendix O (§O.6): Authority Precedence for Training Resources**  
  Training pipeline respects same LCSH > LCC > Wikidata hierarchy used in federation

- **Appendix P (§P.4): Authority Precedence Integration with CIDOC-CRM**  
  Formal precedence rules: LCSH/FAST (Tier 1) > LCC/CIP (Tier 2) > Wikidata + domain authorities (Tier 3)

- **Appendix Q: Operational Modes & Agent Orchestration**  
  Agent routing depends on LCC/facet/period federation for deterministic specialist assignment

---

## **R.10 API Implementation Guide**

This section provides **practical code examples** for accessing each federation's API endpoints, based on existing patterns in the codebase.

### **R.10.1 General Implementation Principles**

- Use `requests` library with proper headers (User-Agent identification)
- Set timeouts (30s for entity fetches, 60s for bulk operations)
- Implement exponential backoff for rate limiting (429 responses)
- Cache responses locally (Redis or file-based for batch operations)
- Log all API errors with traceback for debugging

---

### **R.10.2 Wikidata API Access**

Complete Python example based on `scripts/agents/facet_agent_framework.py` (lines 920-1020):

```python
import requests
from typing import Optional, Dict, Any

def fetch_wikidata_entity(qid: str) -> Optional[Dict[str, Any]]:
    """Fetch Wikidata entity with all claims."""
    API_URL = "https://www.wikidata.org/w/api.php"
    
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": qid,
        "languages": "en",
        "props": "labels|descriptions|claims|aliases",
    }
    
    headers = {"User-Agent": "Chrystallum/1.0 (research project)"}
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        entity = data.get("entities", {}).get(qid)
        if not entity or "missing" in entity:
            return None
            
        return {
            "qid": qid,
            "label": entity.get("labels", {}).get("en", {}).get("value"),
            "description": entity.get("descriptions", {}).get("en", {}).get("value"),
            "claims": entity.get("claims", {})
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikidata entity {qid}: {e}")
        return None
```

**Key Points:**
- Action: `wbgetentities` for entity fetch, `wbsearchentities` for search
- Rate limit: No official limit, but be respectful (1-2 req/sec recommended)
- Authentication: Not required for read operations
- Bulk: Use pipe-separated QIDs: `ids=Q1048|Q1056|Q2277`

---

### **R.10.3 Pleiades API Access**

```python
def fetch_pleiades_place(pleiades_id: str) -> Optional[Dict[str, Any]]:
    """Fetch Pleiades place with coordinates and temporal scope."""
    API_URL = f"https://pleiades.stoa.org/places/{pleiades_id}/json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            "pleiades_id": pleiades_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "reprPoint": data.get("reprPoint"),  # [lon, lat]
            "names": data.get("names", []),
            "timeperiods": data.get("timeperiods", []),
            "connections": data.get("connections", [])
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pleiades {pleiades_id}: {e}")
        return None
```

**Key Points:**
- No API key required
- Rate limit: ~1 req/sec polite crawling
- Bulk download: https://atlantides.org/downloads/pleiades/dumps/ (CSV/JSON dumps updated monthly)
- GeoJSON available: append `/json` to place URL

---

### **R.10.4 VIAF API Access**

```python
def fetch_viaf_authority(viaf_id: str) -> Optional[Dict[str, Any]]:
    """Fetch VIAF authority record with name forms."""
    API_URL = f"https://viaf.org/viaf/{viaf_id}/viaf.json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # VIAF JSON structure is deeply nested
        main_headings = data.get("mainHeadings", {}).get("data", [])
        
        return {
            "viaf_id": viaf_id,
            "name_forms": [h.get("text") for h in main_headings],
            "sources": data.get("sources", {}).get("source", []),
            "birth_date": data.get("birthDate"),
            "death_date": data.get("deathDate")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching VIAF {viaf_id}: {e}")
        return None
```

**Key Points:**
- No API key required
- Multiple formats: `/viaf.json`, `/viaf.xml`, `/rdf.xml`
- Search API: `http://viaf.org/viaf/search?query=...&httpAccept=application/json`
- Rate limit: Not published; use 1 req/sec

---

### **R.10.5 GeoNames API Access (Requires Free Registration)**

```python
def fetch_geonames_place(geonames_id: str, username: str) -> Optional[Dict[str, Any]]:
    """Fetch GeoNames place with modern coordinates."""
    API_URL = "http://api.geonames.org/getJSON"
    
    params = {
        "geonameId": geonames_id,
        "username": username  # Required: register at geonames.org
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            "geonames_id": geonames_id,
            "name": data.get("name"),
            "toponymName": data.get("toponymName"),
            "lat": data.get("lat"),
            "lng": data.get("lng"),
            "countryCode": data.get("countryCode"),
            "adminName1": data.get("adminName1"),  # State/province
            "featureClass": data.get("fcl"),
            "featureCode": data.get("fcode")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GeoNames {geonames_id}: {e}")
        return None
```

**Key Points:**
- **Authentication required**: Free username registration at http://www.geonames.org/login
- Rate limit: 1000 credits/hour, 30,000/day (free tier)
- Premium tier: 80,000/day ($200/year)
- Bulk download: http://download.geonames.org/export/dump/ (tab-delimited files)

---

### **R.10.6 PeriodO API Access**

```python
def fetch_periodo_periods(search_term: str = None) -> Optional[Dict[str, Any]]:
    """Fetch PeriodO period definitions."""
    API_URL = "http://n2t.net/ark:/99152/p0d.json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # PeriodO returns entire dataset; filter locally
        period_collections = data.get("periodCollections", {})
        
        if search_term:
            # Simple label matching (implement proper search as needed)
            matches = []
            for coll_id, collection in period_collections.items():
                for period_id, period in collection.get("definitions", {}).items():
                    label = period.get("label", "")
                    if search_term.lower() in label.lower():
                        matches.append({
                            "periodo_id": f"{coll_id}#{period_id}",
                            "label": label,
                            "spatialCoverage": period.get("spatialCoverage", []),
                            "start": period.get("start", {}),
                            "stop": period.get("stop", {})
                        })
            return {"periods": matches}
        
        return {"periodCollections": period_collections}
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PeriodO: {e}")
        return None
```

**Key Points:**
- No API key required
- Entire dataset in single JSON file (~15MB; cache locally)
- No rate limit (dataset updated infrequently)
- Period URIs: `http://n2t.net/ark:/99152/p0{collection_id}#{period_id}`

---

### **R.10.7 Trismegistos, EDH, Getty AAT Access**

**Trismegistos** - No public API; bulk data via:
- https://www.trismegistos.org/downloads.php
- CSV exports for TMPeople, TMGeo, TMTexts
- Direct database queries not supported; must use exports

**EDH (Epigraphic Database Heidelberg)**:
```python
def search_edh_inscriptions(search_term: str, max_results: int = 20) -> Optional[List[Dict]]:
    """Search EDH inscriptions."""
    API_URL = "https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search"
    
    params = {
        "text": search_term,
        "limit": max_results
    }
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return data.get("items", [])
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching EDH: {e}")
        return None
```

**Getty AAT** - SPARQL endpoint (advanced):
- Endpoint: `http://vocab.getty.edu/sparql`
- Requires SPARQL query language
- Easier: Use Linked Open Data URIs: `http://vocab.getty.edu/aat/{concept_id}.json`

---

### **R.10.8 Rate Limiting & Caching Strategy**

```python
import time
from functools import wraps

def rate_limit(calls_per_second: float = 1.0):
    """Decorator to rate-limit API calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=1.0)
def fetch_wikidata_entity_throttled(qid: str) -> Optional[Dict]:
    return fetch_wikidata_entity(qid)
```

**Caching with file-based storage**:
```python
import json
from pathlib import Path

def cache_api_response(cache_dir: str = "./federation_cache"):
    """Decorator to cache API responses to disk."""
    Path(cache_dir).mkdir(exist_ok=True)
    
    def decorator(func):
        @wraps(func)
        def wrapper(entity_id: str, *args, **kwargs):
            cache_file = Path(cache_dir) / f"{func.__name__}_{entity_id}.json"
            
            if cache_file.exists():
                with open(cache_file) as f:
                    return json.load(f)
            
            result = func(entity_id, *args, **kwargs)
            
            if result:
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
            
            return result
        return wrapper
    return decorator

@cache_api_response()
@rate_limit(calls_per_second=1.0)
def fetch_pleiades_place_cached(pleiades_id: str) -> Optional[Dict]:
    return fetch_pleiades_place(pleiades_id)
```

---

### **R.10.9 Configuration Management**

Store API credentials in environment variables or config file:

```python
# config.py
import os
from pathlib import Path

class FederationConfig:
    # GeoNames (requires free registration)
    GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "")
    
    # User-Agent for all requests
    USER_AGENT = "Chrystallum/1.0 (historical research; contact@example.com)"
    
    # Rate limits (requests per second)
    RATE_LIMITS = {
        "wikidata": 2.0,
        "pleiades": 1.0,
        "viaf": 1.0,
        "geonames": 0.5,  # Conservative for free tier
        "edh": 1.0
    }
    
    # Cache directory
    CACHE_DIR = Path(__file__).parent / "data" / "federation_cache"
    
    # Timeouts (seconds)
    DEFAULT_TIMEOUT = 30
    BULK_TIMEOUT = 60
```

---

### **R.10.10 Error Handling Pattern**

```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FederationAPIError(Exception):
    """Base exception for federation API errors."""
    pass

def safe_fetch_with_retry(
    fetch_func,
    entity_id: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Optional[Dict[str, Any]]:
    """Fetch with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            result = fetch_func(entity_id)
            if result:
                return result
            
            logger.warning(f"Empty result for {entity_id} (attempt {attempt + 1})")
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {entity_id} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(backoff_factor ** attempt)
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = backoff_factor ** (attempt + 1)
                logger.warning(f"Rate limited; waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                break
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    return None
```

---

### **R.10.11 Integration with Neo4j Write Pattern**

```python
def enrich_node_from_federation(
    neo4j_driver,
    node_id: str,
    qid: str
) -> Dict[str, Any]:
    """Fetch Wikidata, enrich with federations, write to Neo4j."""
    
    # 1. Fetch Wikidata entity
    entity = fetch_wikidata_entity(qid)
    if not entity:
        return {"status": "error", "message": "Entity not found"}
    
    # 2. Extract federation IDs from Wikidata claims
    claims = entity.get("claims", {})
    pleiades_id = extract_claim_value(claims, "P1584")  # Pleiades
    viaf_id = extract_claim_value(claims, "P214")  # VIAF
    geonames_id = extract_claim_value(claims, "P1566")  # GeoNames
    
    # 3. Fetch from federations (with caching & rate limiting)
    enrichments = {}
    
    if pleiades_id:
        enrichments["pleiades"] = fetch_pleiades_place_cached(pleiades_id)
    
    if viaf_id:
        enrichments["viaf"] = fetch_viaf_authority(viaf_id)
    
    if geonames_id:
        enrichments["geonames"] = fetch_geonames_place(
            geonames_id, 
            FederationConfig.GEONAMES_USERNAME
        )
    
    # 4. Write to Neo4j with federation metadata
    with neo4j_driver.session() as session:
        result = session.execute_write(
            lambda tx: write_enriched_node(tx, node_id, entity, enrichments)
        )
    
    return result

def write_enriched_node(tx, node_id, entity, enrichments):
    """Cypher write with federation properties."""
    cypher = """
    MATCH (n {node_id: $node_id})
    SET n.wikidata_qid = $qid,
        n.wikidata_label = $label,
        n.wikidata_description = $description,
        n.pleiades_id = $pleiades_id,
        n.viaf_id = $viaf_id,
        n.geonames_id = $geonames_id,
        n.federation_enriched = datetime(),
        n.federation_sources = $sources
    RETURN n
    """
    
    params = {
        "node_id": node_id,
        "qid": entity.get("qid"),
        "label": entity.get("label"),
        "description": entity.get("description"),
        "pleiades_id": enrichments.get("pleiades", {}).get("pleiades_id"),
        "viaf_id": enrichments.get("viaf", {}).get("viaf_id"),
        "geonames_id": enrichments.get("geonames", {}).get("geonames_id"),
        "sources": ["wikidata", "pleiades", "viaf", "geonames"]
    }
    
    result = tx.run(cypher, params)
    return result.single()
```

---

### **R.10.12 Existing Implementation Files**

Current implementations in codebase:
- `scripts/agents/facet_agent_framework.py` (lines 920-1020): Wikidata entity fetching
- `Subjects/CIP/2-11-26-subjects_broader_narrower.py`: Wikidata API patterns
- `Subjects/index_scan.py`: Wikidata search and entity retrieval
- `scripts/reference/agent_training_pipeline.py`: Wikidata federation integration

**Next Steps for Production:**
1. Centralize federation API logic in `scripts/federation/` module
2. Add pytest unit tests with mocked API responses
3. Implement Redis caching for production (file-based for development)
4. Add monitoring/logging for API failures and rate limit tracking
5. Document API key acquisition process in SETUP_GUIDE.md

---

**(End of Appendix R)**

---

## **APPENDIX S: BabelNet Lexical Authority Integration**

### **S.1 Positioning and Layer Architecture**

BabelNet operates as a **multilingual lexical layer** positioned at **Layer 2.5** in the Chrystallum architecture:

- **Layer 1:** Core ontology (SubjectConcept nodes, Claims, Relationships)
- **Layer 2:** Federation authorities (Wikidata, LCSH, FAST, TGN, Pleiades)
- **Layer 2.5:** BabelNet (lexical/semantic enrichment)
- **Layer 3:** Facet Authority (SFAs generating domain-specific ontologies)

**Architectural Position:**
- **Not a primary fact authority** (Wikidata holds factual ground truth)
- **Lexical sidecar** for multilingual labels, glosses, synsets, and cross-language entity linking
- **Semantic enrichment** for term disambiguation and synonym expansion
- **Cross-reference hub** linking WordNet, Wikipedia, Wikidata, and language-specific resources

**Key Distinction:**
- Wikidata provides **factual claims** (dates, locations, relationships) → confidence 0.90
- BabelNet provides **lexical/semantic context** (multilingual labels, senses, glosses) → confidence 0.75-0.85
- Combined alignment (BabelNet synset + Wikidata QID) → confidence boost +0.05

---

### **S.2 Core Use Cases**

#### **S.2.1 SubjectConcept Lexical Enrichment**

**Scenario:** A SubjectConcept node for "Roman Republic" needs multilingual labels and glosses.

**Workflow:**
1. SubjectConcept has `wikidata_id: Q17167`, `label: "Roman Republic"`, `facet: "political"`
2. Call BabelNet API with English label + QID to retrieve synset
3. Extract multilingual labels (Latin: *Res publica Romana*, French: *République romaine*, etc.)
4. Store on SubjectConcept:
   - `babelnet_id: bn:00068294n`
   - `alt_labels: {"la": "Res publica Romana", "fr": "République romaine", ...}`
   - `glosses: {"en": "ancient Roman state...", "fr": "état romain ancien...", ...}`
5. Enrich SFA prompts with multilingual vocabulary for cross-language reasoning

**Benefits:**
- Enhanced query matching across languages
- Richer context for LLM-based clustering and classification
- Support for non-English historical sources

#### **S.2.2 Cross-Lingual Entity Linking**

**Scenario:** User query in French: *"République romaine et ses consuls"*

**Workflow:**
1. Parse query, extract surface form: *"République romaine"*
2. Query BabelNet for French lexicalization → retrieves BabelNet synset `bn:00068294n`
3. Map synset to Wikidata QID (BabelNet includes Wikidata links) → Q17167
4. Retrieve SubjectConcept node with `wikidata_id: Q17167`
5. Execute graph query with language-agnostic identifier

**Benefits:**
- Normalize cross-language queries to canonical identifiers
- Support multilingual research workflows
- Expand retrieval with synonyms and related terms

#### **S.2.3 Facet-Aware Sense Disambiguation**

**Scenario:** Disambiguate "legion" in military vs. religious contexts.

**Workflow:**
1. SFA encounters term "legion" in text extraction
2. Query BabelNet → returns multiple synsets:
   - `bn:00051234n`: military unit (hypernym: armed forces)
   - `bn:00051235n`: large number (hypernym: multitude)
   - `bn:00051236n`: demon (hypernym: evil spirit)
3. **Facet filter:** Military SFA prioritizes military synset based on hypernym match
4. Store chosen `babelnet_id` on SubjectConcept as part of lexical profile
5. Use synset to inform CIDOC-CRM class alignment (E74 Group for military unit)

**Benefits:**
- Reduce ambiguity in multi-sense terms
- Align lexical choices with ontology structure
- Provide explainable reasoning for sense selection

#### **S.2.4 Graph-RAG Over SubjectConcept + BabelNet**

**Scenario:** Discover conceptual neighbors for "dictator" to propose new SubjectConcepts.

**Workflow:**
1. SubjectConcept exists for "Dictator (Roman)"
2. Query BabelNet synset relations: hypernyms (*magistrate*, *ruler*), hyponyms (*tyrant*, *autocrat*)
3. For each related synset, check if corresponding SubjectConcept exists
4. Propose new shell nodes for missing concepts (e.g., "Roman Magistrate")
5. Submit proposals through Subject Ontology Proposal validation pipeline

**Benefits:**
- Semi-automated ontology expansion
- Discover gaps in subject coverage
- Maintain lexical coherence across related concepts

---

### **S.3 Implementation Patterns**

#### **S.3.1 API Integration Pattern**

BabelNet follows the same federation API patterns documented in **Appendix R.10**.

**Cross-Reference:** See [Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration) for:
- R.10.1: Generic API request pattern with retry logic
- R.10.2: Wikidata API example (similar structure for BabelNet)
- R.10.9: Error handling patterns
- R.10.10: Rate limiting and caching strategies

#### **S.3.2 BabelNet API Access Example**

```python
import requests
from typing import Optional, Dict
import os

def fetch_babelnet_synset(synset_id: str, api_key: str = None) -> Optional[Dict]:
    """
    Fetch BabelNet synset with multilingual labels and glosses.
    
    Args:
        synset_id: BabelNet synset ID (e.g., 'bn:00068294n')
        api_key: BabelNet API key (defaults to BABELNET_API_KEY env var)
    
    Returns:
        JSON response with synset data, or None on error
    """
    api_key = api_key or os.getenv("BABELNET_API_KEY")
    if not api_key:
        raise ValueError("BabelNet API key required")
    
    API_URL = "https://babelnet.io/v9/getSynset"
    params = {
        "id": synset_id,
        "key": api_key,
        "targetLang": "EN,IT,FR,DE,ES,LA"  # Multilingual support
    }
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        # Standard pattern from R.10.1
        response = requests.get(
            API_URL, 
            params=params, 
            headers=headers, 
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limit exceeded - see R.10.10 for retry logic
            print(f"Rate limit exceeded: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"Timeout fetching synset {synset_id}")
        return None
    except Exception as e:
        print(f"Error fetching BabelNet synset: {e}")
        return None

def enrich_node_from_babelnet(node_id: str, wikidata_qid: str, label: str) -> Dict:
    """
    Enrich SubjectConcept node with BabelNet lexical data.
    
    Workflow:
    1. Query BabelNet for synsets matching label + QID
    2. Extract multilingual labels, glosses, synset relations
    3. Store babelnet_id, alt_labels, glosses on node
    4. Return enrichment metadata with confidence score
    """
    # Search BabelNet by Wikidata QID
    api_key = os.getenv("BABELNET_API_KEY")
    search_url = "https://babelnet.io/v9/getIds"
    params = {
        "lemma": label,
        "searchLang": "EN",
        "key": api_key,
        "source": f"WIKIDATA:{wikidata_qid}"
    }
    
    response = requests.get(search_url, params=params, timeout=30)
    if response.status_code == 200:
        synset_ids = response.json()
        if synset_ids:
            # Fetch full synset data for first match
            synset_data = fetch_babelnet_synset(synset_ids[0]["id"], api_key)
            if synset_data:
                return {
                    "babelnet_id": synset_ids[0]["id"],
                    "alt_labels": extract_multilingual_labels(synset_data),
                    "glosses": extract_glosses(synset_data),
                    "confidence": 0.80,  # Base confidence for BabelNet alignment
                    "source": "BabelNet v9"
                }
    
    return {"confidence": 0.0, "error": "No synset found"}

def extract_multilingual_labels(synset_data: Dict) -> Dict[str, str]:
    """Extract multilingual labels from BabelNet synset response."""
    labels = {}
    for sense in synset_data.get("senses", []):
        lang = sense.get("language", "")
        lemma = sense.get("properties", {}).get("fullLemma", "")
        if lang and lemma:
            labels[lang] = lemma
    return labels

def extract_glosses(synset_data: Dict) -> Dict[str, str]:
    """Extract glosses (short definitions) from BabelNet synset."""
    glosses = {}
    for gloss in synset_data.get("glosses", []):
        lang = gloss.get("language", "")
        text = gloss.get("gloss", "")
        if lang and text:
            glosses[lang] = text
    return glosses
```

#### **S.3.3 Caching and Rate Limiting**

**BabelNet API Limits:**
- **Free tier:** 1,000 requests/day
- **Paid subscription:** 10,000-100,000 requests/day (tiered pricing)

**Caching Strategy** (see Appendix R.10.10):
- Cache synset responses in Redis with 30-day TTL
- Use file-based cache for development: `cache/babelnet/{synset_id}.json`
- Cache key: `babelnet:synset:{synset_id}`

**Implementation:**
```python
import json
from pathlib import Path

def get_cached_synset(synset_id: str) -> Optional[Dict]:
    cache_path = Path(f"cache/babelnet/{synset_id}.json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return None

def cache_synset(synset_id: str, data: Dict):
    cache_path = Path(f"cache/babelnet/{synset_id}.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=2))
```

---

### **S.4 Confidence Scoring for BabelNet-Derived Properties**

#### **S.4.1 Base Confidence Levels**

**BabelNet Synset Alignment:** 0.75-0.85 confidence
- **Rationale:** BabelNet is a lexical/semantic authority, not a factual authority
- **Lower than Wikidata (0.90)** because:
  - Lexical relationships are more subjective than factual claims
  - Synset boundaries and sense distinctions vary by resource
  - Multilingual alignments introduce translation ambiguity

**Confidence Ranges:**
- **0.85:** BabelNet synset with Wikidata QID alignment + high statement count
- **0.80:** BabelNet synset with Wikidata QID alignment (standard case)
- **0.75:** BabelNet synset without Wikidata alignment (WordNet/Wikipedia only)

#### **S.4.2 Confidence Boost Patterns**

**BabelNet + Wikidata Alignment:** +0.05 confidence boost
- When BabelNet synset includes `WIKIDATA:Q12345` link and QID matches existing SubjectConcept
- Example: Base 0.80 → 0.85 with QID confirmation

**Multi-Source Lexical Convergence:** +0.10 confidence boost
- When BabelNet synset aligns with:
  - Wikidata QID
  - LCSH preferred term
  - FAST heading
- Example: Base 0.75 → 0.85 with triple alignment

**Facet-Specific Disambiguation:** +0.05 confidence boost
- When chosen synset hypernym matches facet domain
- Example: Military SFA selects military synset for "legion" → +0.05

#### **S.4.3 Confidence Degradation**

**Ambiguous Synset Selection:** -0.10 confidence penalty
- Multiple candidate synsets with similar scores
- No clear facet-based discriminator

**Missing Wikidata Link:** -0.05 confidence penalty
- BabelNet synset lacks Wikidata connection
- Reliance on WordNet/Wikipedia only

#### **S.4.4 Example Confidence Calculations**

**Scenario 1: High-Confidence Alignment**
- SubjectConcept: "Roman Republic" (wikidata_id: Q17167)
- BabelNet synset: bn:00068294n
- BabelNet includes: WIKIDATA:Q17167 link
- Synset has 15+ language lexicalizations
- **Confidence:** 0.80 (base) + 0.05 (QID match) = **0.85**

**Scenario 2: Medium-Confidence Alignment**
- SubjectConcept: "Roman Legion"
- BabelNet synset: bn:00051234n (military unit)
- Multiple candidate synsets, facet filter applied
- **Confidence:** 0.80 (base) + 0.05 (facet match) = **0.85**

**Scenario 3: Low-Confidence Alignment**
- SubjectConcept: "Ancient Assembly"
- BabelNet synset: bn:00012345n
- No Wikidata link, ambiguous sense
- **Confidence:** 0.75 (base) - 0.05 (no QID) - 0.10 (ambiguous) = **0.60**

---

### **S.5 Integration with SFA Workflow**

#### **S.5.1 Phase 3.5: Lexical Enrichment (Optional)**

**Position:** After Initialize Mode (Phase 3), before Ontology Proposal (Phase 4)

**Workflow:**
1. SFA completes Initialize Mode, creates SubjectConcept nodes with Wikidata enrichment
2. **Lexical Enrichment Phase (Optional):**
   - For each new SubjectConcept with `wikidata_id`:
     - Call `enrich_node_from_babelnet(node_id, wikidata_qid, label)`
     - Store `babelnet_id`, `alt_labels`, `glosses` on node properties
     - Log enrichment with confidence score
   - Skip nodes without Wikidata QID (cannot reliably align)
3. Proceed to Ontology Proposal with enriched lexical context

**Benefits:**
- Richer multilingual labels for clustering and classification
- Enhanced LLM prompts with glosses and synonyms
- Cross-language support for future queries

**Configuration:**
```python
# In facet_agent_framework.py
if config.get("babelnet_enrichment_enabled", False):
    for node in new_nodes:
        if node.get("wikidata_id"):
            enrichment = enrich_node_from_babelnet(
                node["id"], 
                node["wikidata_id"], 
                node["label"]
            )
            if enrichment.get("confidence", 0) >= 0.75:
                update_node_properties(node["id"], enrichment)
```

#### **S.5.2 Phase 5: Training Mode Disambiguation**

**Use Case:** Polysemous term disambiguation during claim generation

**Scenario:** Military SFA encounters "cohort" in text:
- Could mean: military unit, statistical group, companion group

**Workflow:**
1. Extract term "cohort" from historical text
2. Query BabelNet for synsets matching "cohort"
3. **Facet-aware filtering:**
   - Military SFA prioritizes synset with hypernym "military unit"
   - Filters out statistical/demographic senses
4. Store chosen `babelnet_id` on new SubjectConcept or claim metadata
5. Use synset to guide CIDOC-CRM class assignment

**Benefits:**
- Reduce ambiguity in extracted terms
- Align lexical choices with domain expertise
- Provide explainable term selection

**Cross-Reference:** See **Appendix T.3** (Training Mode workflow) for implementation details.

---

### **S.6 Configuration and Authentication**

#### **S.6.1 API Key Management**

**BabelNet API requires paid subscription** (after free tier exhaustion)

**Environment Variable:**
```bash
export BABELNET_API_KEY="your_api_key_here"
```

**Configuration in config.py:**
```python
BABELNET_CONFIG = {
    "api_key": os.getenv("BABELNET_API_KEY"),
    "base_url": "https://babelnet.io/v9",
    "rate_limit": 1000,  # requests/day for free tier
    "timeout": 30,  # seconds
    "cache_enabled": True,
    "cache_ttl": 2592000,  # 30 days
}
```

#### **S.6.2 Rate Limit Tracking**

**Free Tier:** 1,000 requests/day
- Track daily usage in Redis: `babelnet:usage:{date}`
- Implement circuit breaker when approaching limit

**Implementation:**
```python
import redis
from datetime import date

def check_rate_limit() -> bool:
    r = redis.Redis()
    today = date.today().isoformat()
    key = f"babelnet:usage:{today}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 86400)  # 24 hours
    return count <= 1000  # Free tier limit
```

#### **S.6.3 Fallback Strategies**

**When BabelNet Unavailable:**
1. **Use cached synsets** for previously seen terms
2. **Skip lexical enrichment** for new terms (graceful degradation)
3. **Fall back to Wikidata labels** only (mono-lingual)
4. **Log skipped enrichments** for manual review

---

### **S.7 Cross-References**

**Related Appendices:**
- **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#r10-api-implementation-patterns):** Federation API patterns (request structure, error handling, caching)
- **[Appendix T](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-t-subject-facet-agent-workflow---day-in-the-life):** SFA workflow integration points (Phase 3.5, Phase 5 disambiguation)
- **[Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf):** CIDOC-CRM alignment for lexical concepts (E55 Type for BabelNet synsets)
- **[Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns):** Wikidata integration patterns (primary fact authority)
- **[Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration):** Operational Modes (Initialize, Training)

**Implementation Files:**
- `scripts/federation/babelnet_client.py`: BabelNet API client (to be created)
- `scripts/agents/facet_agent_framework.py`: SFA orchestration with BabelNet integration
- `config.py`: BabelNet configuration settings

**External Resources:**
- BabelNet API Documentation: https://babelnet.io/guide
- BabelNet Paper (ACM 2012): https://dl.acm.org/doi/10.5555/2887533.2887534
- Multilingual Linked Data Report: http://www.w3.org/2015/09/bpmlod-reports/multilingual-dictionaries/

---

**(End of Appendix S)**

---

## **APPENDIX T: Subject Facet Agent Workflow - "Day in the Life"**

A newly instantiated SubjectFacetAgent (SFA) follows a structured workflow that ensures disciplined knowledge construction through schema introspection, state loading, federation bootstrap, ontology proposal, and training. This appendix documents the complete lifecycle of an SFA from instantiation to claim generation.

---

### **T.1 Wake-Up and Self-Orientation**

#### **T.1.1 Agent Instantiation**

**Factory Pattern:**
```python
from scripts.agents.facet_agent_framework import FacetAgentFactory

factory = FacetAgentFactory()
agent = factory.get_agent("military")  # or political, religious, economic, etc.
```

**Supported Facets:**
- `military`: Military units, campaigns, tactics, leadership
- `political`: Governments, institutions, offices, political events
- `religious`: Beliefs, practices, institutions, figures
- `economic`: Trade, currency, production, labor
- `cultural`: Arts, literature, daily life, customs
- `geographic`: Places, regions, territories, boundaries

#### **T.1.2 Schema Introspection (Step 1)**

**Purpose:** Learn "what is allowed" at the schema level before touching data.

**Actions:**
1. **Node schema introspection:**
   ```python
   schema = agent.introspect_node_label("SubjectConcept")
   # Returns: required properties, optional properties, tier, validation rules
   ```

2. **Layer 2.5 property discovery:**
   ```python
   properties = agent.get_layer25_properties()
   # Returns: P31 (instance of), P279 (subclass of), P361 (part of), etc.
   # These are the allowed Wikidata properties for hierarchy traversal
   ```

3. **Relationship discovery:**
   ```python
   relationships = agent.discover_relationships_between("Human", "Event")
   # Returns: PARTICIPATED_IN, COMMANDED, WITNESSED, etc.
   ```

**Output:** SFA now knows:
- Required properties for SubjectConcept nodes
- Valid Wikidata properties for federation
- Allowed relationship types for claims

**Cross-Reference:** See [Appendix M](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-m-identifier-safety-reference) for schema validation patterns.

---

### **T.2 Session Start: Load Current State**

#### **T.2.1 State Introspection (Step 2)**

**Purpose:** Learn "what already exists" and "what I have done before."

**Actions:**
```python
context = agent.get_session_context()
# Returns:
# - sample_nodes: Recent SubjectConcept nodes in this facet
# - sample_relationships: Recent relationships involving these nodes
# - pending_claims: Claims awaiting validation
# - agent_history: This agent's past contributions and promotion rate
# - meta_schema_version: Schema version for compatibility check
```

#### **T.2.2 Subgraph and Provenance Checks**

**Check for existing anchor:**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=200)
# Search for planned anchor node (e.g., "Roman Republic")
anchor_exists = any(node.label == "Roman Republic" for node in subgraph)
```

**Provenance analysis:**
```python
if anchor_exists:
    node_id = get_node_id("Roman Republic")
    claims = agent.find_claims_for_node(node_id)
    provenance = agent.get_node_provenance(node_id)
    # Avoid duplicate claims, understand existing coverage
```

**Agent contribution tracking:**
```python
contributions = agent.find_agent_contributions()
# Returns: claims_proposed, claims_promoted, claims_rejected, promotion_rate
# Use to adjust confidence thresholds
```

**Cross-Reference:** See [Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration) for state management patterns.

---

### **T.3 Initialize Mode: Bootstrap Domain from Wikidata**

#### **T.3.1 Mode Activation and Logging (Step 5)**

**Purpose:** Bootstrap a new domain area from a trusted Wikidata anchor.

**Execution:**
```python
result_init = agent.execute_initialize_mode(
    anchor_qid="Q17167",  # Roman Republic
    depth=2,  # Traverse hierarchy 2 levels deep
    autosubmit_claims=False,  # Manual review required
    ui_callback=ui_log_callback  # Real-time logging
)
```

#### **T.3.2 Initialize Mode Workflow**

**Step-by-Step Process:**

1. **Fetch Wikidata anchor entity:**
   ```python
   entity = fetch_wikidata_entity("Q17167")
   # Returns: labels, descriptions, aliases, statements, sitelinks
   ```

2. **Auto-enrich/create root SubjectConcept:**
   ```python
   node_id = enrich_node_from_wikidata(
       wikidata_qid="Q17167",
       facet="political",
       create_if_missing=True
   )
   # Sets: label, description, alt_labels, wikidata_id, statement_count
   ```

3. **Validate completeness (Step 3.5):**
   ```python
   completeness = validate_node_completeness(node_id)
   # Checks: required properties present, label/description quality
   # Returns: score 0.0-1.0, missing_fields, validation_errors
   if completeness["score"] < 0.70:
       log_warning("Low completeness", completeness)
       return  # Abort if below threshold
   ```

4. **Enrich with CIDOC-CRM alignment:**
   ```python
   enrich_with_ontology_alignment(node_id, entity)
   # Maps Wikidata P31 types to CIDOC-CRM classes
   # Sets: cidoc_crm_class (e.g., E74_Group, E4_Period)
   ```

5. **Traverse hierarchy with allowed properties:**
   ```python
   related = discover_hierarchy_from_entity(
       qid="Q17167",
       depth=2,
       properties=["P31", "P279", "P361", "P527"]  # From Layer 2.5
   )
   # Returns: related entities, relationship types, hierarchy structure
   ```

6. **Generate claims from Wikidata statements:**
   ```python
   claims = generate_claims_from_wikidata(
       node_id=node_id,
       entity=entity,
       base_confidence=0.90,  # Wikidata authority
       facet="political"
   )
   # Each claim enriched with CRMinf belief metadata
   # Tagged with facet, source, extraction_time
   ```

7. **Optional auto-submit high-confidence claims:**
   ```python
   if autosubmit_claims:
       for claim in claims:
           if claim["confidence"] >= 0.90:
               submit_claim_for_validation(claim)
   ```

8. **Log all actions:**
   ```python
   logger.log_action(
       action_type="INITIALIZE",
       node_id=node_id,
       details={"qid": "Q17167", "depth": 2, "claims_generated": len(claims)}
   )
   ```

**Output:**
```python
{
    "nodes_created": 15,
    "relationships_discovered": 42,
    "claims_generated": 68,
    "completeness_score": 0.87,
    "cidoc_crm_class": "E4_Period",
    "log_file": "logs/military_initialize_20260216_143022.json"
}
```

**Cross-Reference:** See [Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns) for Wikidata API patterns.

---

### **T.3.5 Lexical Enrichment (Optional)**

#### **T.3.5.1 BabelNet Integration Phase**

**Position:** After Initialize Mode (Phase 3), before Ontology Proposal (Phase 4)

**Purpose:** Enrich SubjectConcept nodes with multilingual labels, glosses, and synsets for enhanced cross-language support and semantic disambiguation.

**Workflow:**

1. **Check configuration:**
   ```python
   if config.get("babelnet_enrichment_enabled", False):
       api_key = os.getenv("BABELNET_API_KEY")
       if not api_key:
           log_warning("BabelNet enrichment skipped: API key not configured")
           return
   ```

2. **Enrich each new SubjectConcept:**
   ```python
   for node in result_init["nodes_created"]:
       if node.get("wikidata_id"):  # Require Wikidata alignment
           enrichment = enrich_node_from_babelnet(
               node_id=node["id"],
               wikidata_qid=node["wikidata_id"],
               label=node["label"]
           )
           
           if enrichment.get("confidence", 0) >= 0.75:
               # Store BabelNet data on node
               update_node_properties(node["id"], {
                   "babelnet_id": enrichment["babelnet_id"],
                   "alt_labels": json.dumps(enrichment["alt_labels"]),
                   "glosses": json.dumps(enrichment["glosses"]),
                   "babelnet_confidence": enrichment["confidence"]
               })
               
               log_action(
                   action_type="LEXICAL_ENRICHMENT",
                   node_id=node["id"],
                   details=enrichment
               )
   ```

3. **Handle enrichment failures gracefully:**
   ```python
   # Lexical enrichment is optional - don't block on failure
   try:
       enrich_from_babelnet()
   except BabelNetAPIError as e:
       log_warning(f"BabelNet enrichment failed: {e}")
       # Continue to Ontology Proposal without BabelNet data
   ```

**Benefits:**
- Multilingual query support (French, German, Latin, etc.)
- Richer context for LLM-based clustering in Ontology Proposal
- Term disambiguation during Training Mode

**Configuration:**
```python
# config.py
BABELNET_ENRICHMENT = {
    "enabled": True,
    "min_confidence": 0.75,
    "required_languages": ["EN", "LA", "FR", "DE"],
    "skip_on_failure": True  # Graceful degradation
}
```

**Cross-Reference:** See **[Appendix S](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-s-babelnet-lexical-authority-integration)** for detailed BabelNet integration patterns.

---

### **T.4 Subject Ontology Proposal (Bridge Step, via SCA Component)**

#### **T.4.1 Ontology Proposal Execution (Step 5 Bridge)**

**Purpose:** Structure discovered entities into conceptual clusters with claim templates and validation rules.

**Execution:**
```python
result_onto = agent.propose_subject_ontology(ui_callback=ui_log_callback)
```

#### **T.4.2 Ontology Proposal Workflow**

**Step-by-Step Process:**

1. **Collect entities from Initialize Mode:**
   ```python
   nodes = result_init["nodes_created"]
   # Each node has: label, wikidata_id, P31/P279 types
   ```

2. **Fetch full Wikidata entities:**
   ```python
   for node in nodes:
       entity = fetch_wikidata_entity(node["wikidata_id"])
       type_chains = extract_type_hierarchy(entity)  # P31/P279 chains
   ```

3. **LLM clustering pass:**
   ```python
   clusters = llm_cluster_types(
       types=type_chains,
       facet="military",
       prompt_template="cluster_military_concepts"
   )
   # Returns: conceptual clusters (e.g., Military Leadership, Military Operations)
   ```

4. **Convert clusters to ontology classes:**
   ```python
   ontology_classes = []
   for cluster in clusters:
       ontology_class = {
           "class_name": cluster["name"],
           "parent_class": cluster.get("parent", "SubjectConcept"),
           "member_count": len(cluster["members"]),
           "characteristics": cluster["description"],
           "example_members": cluster["members"][:5]
       }
       ontology_classes.append(ontology_class)
   ```

5. **Generate claim templates:**
   ```python
   templates = generate_claim_templates(ontology_classes)
   # Example: "All Military Commanders have property:rank with value:MilitaryRank"
   ```

6. **Define validation rules:**
   ```python
   rules = [
       {"type": "membership", "rule": "All members must have P31 pointing to class"},
       {"type": "cardinality", "rule": "rank property: 1-3 values per entity"},
       {"type": "temporal", "rule": "service dates must be within lifetime"},
       {"type": "cross_facet", "rule": "military unit must align with geographic location"}
   ]
   ```

7. **Compute strength score:**
   ```python
   strength_score = compute_ontology_strength(
       member_count=len(nodes),
       template_coverage=len(templates) / len(nodes),
       rule_coverage=len(rules)
   )
   # Returns: 0.0-1.0 score indicating ontology quality
   ```

8. **Store ontology on agent instance:**
   ```python
   agent.proposed_ontology = {
       "classes": ontology_classes,
       "templates": templates,
       "rules": rules,
       "strength_score": strength_score,
       "created_at": datetime.now().isoformat()
   }
   ```

**Output:**
```python
{
    "classes": [
        {
            "class_name": "MilitaryLeadership",
            "parent_class": "SubjectConcept",
            "member_count": 8,
            "characteristics": "Individuals who commanded military units...",
            "example_members": ["Julius Caesar", "Pompey", "Scipio Africanus"]
        },
        # ... more classes
    ],
    "templates": [
        "MilitaryLeadership has rank: MilitaryRank",
        "MilitaryLeadership commanded: MilitaryUnit"
    ],
    "rules": [...],
    "strength_score": 0.82
}
```

**Cross-Reference:** See [Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf) for CIDOC-CRM alignment during ontology proposal.

---

### **T.5 Training Mode: Extended Claim Generation**

#### **T.5.1 Training Mode Execution**

**Purpose:** Generate claims guided by proposed ontology, with validation and quality controls.

**Execution:**
```python
result_train = agent.execute_training_mode(
    max_iterations=50,
    target_claims=300,
    min_confidence=0.80,
    autosubmit_high_confidence=False,
    ui_callback=ui_log_callback
)
```

#### **T.5.2 Training Mode Workflow**

**Per-Node Processing Loop:**

1. **Reload context (detect inter-agent changes):**
   ```python
   context = agent.get_session_context()
   # See if other facets have added claims or nodes
   ```

2. **Prioritize nodes using ontology:**
   ```python
   priority_nodes = sort_by_ontology_class(
       nodes=context["sample_nodes"],
       ontology=agent.proposed_ontology
   )
   # Process high-priority classes first (e.g., MilitaryLeadership)
   ```

3. **For each node:**

   a. **Ensure Wikidata QID exists:**
   ```python
   if not node.get("wikidata_id"):
       enrichment = enrich_node_from_wikidata(node["id"])
       if not enrichment.get("wikidata_id"):
           log_warning(f"Skipping node {node['id']}: no QID")
           continue
   ```

   b. **Validate completeness:**
   ```python
   completeness = validate_node_completeness(node["id"])
   log_metric("completeness", completeness["score"])
   if completeness["score"] < 0.70:
       attempt_auto_enrichment(node["id"])
   ```

   c. **Fetch Wikidata entity:**
   ```python
   entity = fetch_wikidata_entity(node["wikidata_id"])
   ```

   d. **Generate claims filtered by ontology:**
   ```python
   claims = generate_claims_from_wikidata(
       node_id=node["id"],
       entity=entity,
       base_confidence=0.90,
       facet=agent.facet_key,
       templates=agent.proposed_ontology["templates"],  # Filter by templates
       rules=agent.proposed_ontology["rules"]  # Validate against rules
   )
   ```

   e. **Use BabelNet for polysemous term disambiguation:**
   ```python
   # NEW: BabelNet integration for ambiguous terms
   if claim.get("value_label") in POLYSEMOUS_TERMS:
       babelnet_synset = disambiguate_with_babelnet(
           term=claim["value_label"],
           facet=agent.facet_key,
           context=node["label"]
       )
       if babelnet_synset:
           claim["babelnet_synset"] = babelnet_synset["synset_id"]
           claim["sense_gloss"] = babelnet_synset["gloss"]
   ```
   **Cross-Reference:** See **[Appendix S.5](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#s52-phase-5-training-mode-disambiguation)** for BabelNet disambiguation patterns.

   f. **Enrich claims with CRMinf:**
   ```python
   for claim in claims:
       enrich_claim_with_crminf(
           claim=claim,
           belief_type="I4_Proposition_Set",
           confidence=claim["confidence"]
       )
   ```

   g. **Validate CIDOC alignment:**
   ```python
   cidoc_valid = validate_cidoc_alignment(node["id"], claim)
   if not cidoc_valid:
       log_warning(f"CIDOC alignment failed for claim {claim['id']}")
       claim["confidence"] *= 0.90  # Confidence penalty
   ```

   h. **Filter by minimum confidence:**
   ```python
   claims = [c for c in claims if c["confidence"] >= min_confidence]
   ```

   i. **Auto-submit high-confidence claims:**
   ```python
   if autosubmit_high_confidence:
       for claim in claims:
           if claim["confidence"] >= 0.90:
               submit_claim_for_validation(claim)
   ```

   j. **Log each claim proposal:**
   ```python
   for claim in claims:
       logger.log_action(
           action_type="CLAIM_PROPOSED",
           node_id=node["id"],
           details={
               "label": claim["label"],
               "confidence": claim["confidence"],
               "rationale": claim["rationale"]
           }
       )
   ```

4. **Track metrics:**
   ```python
   metrics = {
       "nodes_processed": iteration_count,
       "claims_proposed": total_claims,
       "avg_confidence": mean(claim_confidences),
       "avg_completeness": mean(completeness_scores),
       "claims_per_second": total_claims / elapsed_time
   }
   ```

**Output:**
```python
{
    "nodes_processed": 45,
    "claims_proposed": 287,
    "avg_confidence": 0.86,
    "avg_completeness": 0.83,
    "claims_per_second": 2.4,
    "log_file": "logs/military_training_20260216_150345.json"
}
```

**Cross-Reference:** See [Appendix N](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-n-property-extensions--advanced-attributes) for advanced claim properties.

---

### **T.6 Between Tasks: Collaboration and Introspection**

#### **T.6.1 Cross-Facet Awareness**

**Monitor other facets:**
```python
# Check pending claims from all facets
all_pending = list_pending_claims()  # No facet filter

# Adjust behavior based on system load
if len(all_pending) > 1000:
    # Reduce proposal rate if validation queue is backed up
    agent.proposal_rate *= 0.75
```

#### **T.6.2 Self-Monitoring**

**Track promotion rate:**
```python
contributions = agent.find_agent_contributions()
promotion_rate = contributions["claims_promoted"] / contributions["claims_proposed"]

if promotion_rate < 0.70:
    # Increase confidence threshold if many claims are rejected
    agent.min_confidence += 0.05
    log_warning(f"Low promotion rate ({promotion_rate:.2f}), increasing threshold")
```

#### **T.6.3 Provenance Analysis**

**Understand node history:**
```python
for node in priority_nodes:
    provenance = get_node_provenance(node["id"])
    claim_history = get_claim_history(node["id"])
    
    # Avoid duplicate claims
    existing_claims = [c["label"] for c in claim_history]
    new_claims = [c for c in proposed_claims if c["label"] not in existing_claims]
```

**Cross-Reference:** See [Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration) for multi-agent coordination patterns.

---

### **T.7 End of "Day": Session Summary**

#### **T.7.1 Logger Summary**

**Final metrics:**
```python
summary = logger.generate_summary()
# Returns:
# - action_counts: {INITIALIZE: 1, REASONING: 45, QUERY: 203, CLAIM_PROPOSED: 287}
# - error_counts: {API_TIMEOUT: 3, VALIDATION_FAILED: 12}
# - claim_stats: {proposed: 287, high_confidence: 198, low_confidence: 89}
# - completeness_avg: 0.83
# - session_duration: 4520.3 seconds
```

#### **T.7.2 Persistence (Future Work)**

**Store ontology:**
```python
# Future: persist ontology for next session
save_ontology(
    facet=agent.facet_key,
    ontology=agent.proposed_ontology,
    version=agent.ontology_version
)
```

**Store session metrics:**
```python
# Future: track agent performance over time
save_session_metrics(
    agent_id=agent.agent_id,
    metrics=summary,
    timestamp=datetime.now()
)
```

---

### **T.8 Federation Enrichment Integration**

#### **T.8.1 Multi-Authority Enrichment Pattern**

**Purpose:** Enrich SubjectConcept nodes with data from multiple federation authorities beyond Wikidata.

**Workflow Position:** After Phase 3 (Initialize Mode), optionally before or alongside Phase 3.5 (Lexical Enrichment)

**Supported Authorities:**
- **Pleiades:** Ancient place identifiers and coordinates
- **VIAF:** Person authority with multi-national library identifiers
- **GeoNames:** Geographic name authority with modern coordinates
- **FAST:** Subject heading alignment
- **TGN:** Getty Thesaurus of Geographic Names

**Implementation:**
```python
def enrich_node_from_federation(
    node_id: str,
    authorities: List[str] = ["pleiades", "viaf", "geonames"]
) -> Dict:
    """
    Enrich node with data from multiple federation authorities.
    
    Follows patterns from Appendix R.10.
    """
    enrichments = {}
    
    for authority in authorities:
        try:
            if authority == "pleiades" and node.get("entity_type") == "Place":
                pleiades_data = enrich_from_pleiades(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if pleiades_data:
                    enrichments["pleiades_id"] = pleiades_data["id"]
                    enrichments["ancient_coordinates"] = pleiades_data["coords"]
                    enrichments["confidence"] = 0.85
            
            elif authority == "viaf" and node.get("entity_type") == "Person":
                viaf_data = enrich_from_viaf(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if viaf_data:
                    enrichments["viaf_id"] = viaf_data["id"]
                    enrichments["library_identifiers"] = viaf_data["identifiers"]
                    enrichments["confidence"] = 0.85
            
            elif authority == "geonames":
                geonames_data = enrich_from_geonames(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if geonames_data:
                    enrichments["geonames_id"] = geonames_data["id"]
                    enrichments["modern_coordinates"] = geonames_data["coords"]
                    enrichments["confidence"] = 0.80
        
        except FederationAPIError as e:
            log_warning(f"{authority} enrichment failed: {e}")
            continue
    
    # Stack evidence from multiple sources
    if len(enrichments) > 1:
        enrichments["confidence"] = min(0.95, enrichments["confidence"] + 0.10)
    
    return enrichments
```

**Usage in Initialize Mode:**
```python
# After creating SubjectConcept nodes from Wikidata
for node in result_init["nodes_created"]:
    if config.get("federation_enrichment_enabled", True):
        federation_data = enrich_node_from_federation(
            node_id=node["id"],
            authorities=["pleiades", "viaf", "geonames"]
        )
        if federation_data:
            update_node_properties(node["id"], federation_data)
```

**Confidence Stacking:**
- **Single authority:** 0.80-0.85 confidence
- **Two authorities:** +0.10 boost → 0.90-0.95
- **Three+ authorities:** +0.15 boost → 0.95-1.00 (capped)

**Cross-Reference:** See **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#r10-api-implementation-patterns)** for detailed API implementation patterns for each authority.

---

### **T.9 Error Recovery and Retry Patterns**

#### **T.9.1 API Timeout Handling**

**Pattern from Appendix R.10.10:**
```python
import time
from typing import Optional

def fetch_with_retry(
    fetch_func,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    timeout: int = 30
) -> Optional[Dict]:
    """
    Retry API calls with exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            return fetch_func(timeout=timeout)
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                log_warning(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                log_error("Max retries exceeded, giving up")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = int(e.response.headers.get("Retry-After", 60))
                log_warning(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
    return None
```

**Usage in Training Mode:**
```python
entity = fetch_with_retry(
    lambda timeout: fetch_wikidata_entity(node["wikidata_id"], timeout=timeout),
    max_retries=3
)
if not entity:
    log_error(f"Failed to fetch entity for node {node['id']}")
    continue  # Skip this node, move to next
```

#### **T.9.2 Completeness Validation Failures**

**Scenario:** Node fails completeness check (Step 3.5)

**Recovery Strategy:**
```python
completeness = validate_node_completeness(node_id)

if completeness["score"] < 0.70:
    # Attempt auto-enrichment
    missing_fields = completeness["missing_fields"]
    
    if "description" in missing_fields:
        # Fetch from Wikidata if not already present
        entity = fetch_wikidata_entity(node["wikidata_id"])
        if entity.get("descriptions", {}).get("en"):
            update_node_property(
                node_id,
                "description",
                entity["descriptions"]["en"]["value"]
            )
    
    if "alt_labels" in missing_fields:
        # Fetch from BabelNet or Wikidata aliases
        alt_labels = fetch_alt_labels(node["wikidata_id"])
        if alt_labels:
            update_node_property(node_id, "alt_labels", json.dumps(alt_labels))
    
    # Re-validate
    completeness = validate_node_completeness(node_id)
    
    if completeness["score"] < 0.70:
        log_warning(f"Node {node_id} still incomplete after enrichment")
        # Mark for manual review
        tag_node_for_review(node_id, reason="low_completeness")
```

#### **T.9.3 Claim Validation Errors**

**Scenario:** Generated claim fails validation rules

**Recovery Strategy:**
```python
def generate_and_validate_claims(node_id, entity, ontology_rules):
    claims = generate_claims_from_wikidata(node_id, entity)
    
    validated_claims = []
    for claim in claims:
        validation = validate_claim(claim, ontology_rules)
        
        if validation["valid"]:
            validated_claims.append(claim)
        else:
            # Attempt to fix common validation errors
            if validation["error"] == "missing_temporal_bound":
                # Add default temporal bound from entity lifespan
                claim["temporal_start"] = entity.get("birth_date")
                claim["temporal_end"] = entity.get("death_date")
                
                # Re-validate
                validation = validate_claim(claim, ontology_rules)
                if validation["valid"]:
                    validated_claims.append(claim)
                else:
                    log_warning(f"Claim {claim['id']} still invalid after fix")
            
            elif validation["error"] == "cardinality_violation":
                # Lower confidence and flag for review
                claim["confidence"] *= 0.80
                claim["validation_warning"] = validation["error"]
                validated_claims.append(claim)
            
            else:
                # Cannot auto-fix, log and skip
                log_error(f"Claim validation failed: {validation['error']}")
    
    return validated_claims
```

**Cross-Reference:** See [Appendix R.10.9](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration) for federation-specific error handling.

---

### **T.10 Cross-References**

**Related Appendices:**
- **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration):** Federation API implementation patterns, error handling, caching
- **[Appendix S](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-s-babelnet-lexical-authority-integration):** BabelNet lexical enrichment (Phase 3.5, Training Mode disambiguation)
- **[Appendix O](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-o-facet-training-resources-registry):** Training resources for facet-specific knowledge
- **[Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf):** CIDOC-CRM alignment during enrichment
- **[Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration):** Operational modes (Initialize, Training, Validation)
- **[Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns):** Wikidata integration patterns
- **[Appendix M](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-m-identifier-safety-reference):** Schema validation and identifier safety

**Implementation Files:**
- `scripts/agents/facet_agent_framework.py`: SFA orchestration and workflow
- `scripts/agents/subject_concept_agent.py`: SubjectConceptAgent (SCA) for ontology proposal
- `scripts/federation/wikidata_client.py`: Wikidata API client
- `scripts/federation/babelnet_client.py`: BabelNet API client (to be created)
- `scripts/validation/completeness_validator.py`: Completeness validation (Step 3.5)
- `scripts/logging/agent_logger.py`: Agent action logging

**Key Integration Points:**
- **Phase 1:** Schema introspection (STEP_1_COMPLETE.md)
- **Phase 2:** State loading (STEP_2_COMPLETE.md)
- **Phase 3:** Initialize Mode (STEP_5_COMPLETE.md)
- **Phase 3.5:** Completeness validation (STEP_3_COMPLETE.md)
- **Phase 4:** CIDOC-CRM enrichment (STEP_4_COMPLETE.md)
- **Phase 5:** Subject Ontology Proposal (STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- **Phase 6:** Training Mode (STEP_3_COMPLETE.md, STEP_5_COMPLETE.md)

---

**(End of Appendix T)**

---

(End of consolidated document snapshot)
