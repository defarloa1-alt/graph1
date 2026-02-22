# **Chrystallum Architecture - Core Overview**
**Version:** 3.2 Decomposed (from Consolidated)  
**Date:** February 19, 2026  
**Status:** Current  
**Source:** Extracted from `2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

---

## **Navigation**

**This Document:** Core architectural overview and system summary (PART I: Sections 1-2)

**Related Architecture Documents:**
- [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) - Core ontology layers (Sections 3-7)
- [ARCHITECTURE_IMPLEMENTATION.md](ARCHITECTURE_IMPLEMENTATION.md) - Tech stack & workflows (Sections 8-9)
- [ARCHITECTURE_GOVERNANCE.md](ARCHITECTURE_GOVERNANCE.md) - QA, validation, maintenance (Sections 10-12)
- [Appendices/](Appendices/) - 26 detailed appendices organized by topic

**Quick Links:**
- [README.md](../README.md) - Project overview & quick start
- [ARCHITECTURE_IMPLEMENTATION_INDEX.md](ARCHITECTURE_IMPLEMENTATION_INDEX.md) - Maps sections to code files

---

## **Document Purpose**

This document provides the **executive summary and system overview** for Chrystallum, a multi-agent knowledge graph system designed for historical research.

**What you'll find here:**
- System purpose and core innovations
- Architectural principles (two-stage architecture, subject-anchored subgraphs)
- Key design decisions (why LCC, why two-level agents, why calendar normalization)
- Conceptual model and data flow
- Multi-authority alignment strategy
- Evidence architecture

**For detailed specifications:** See ARCHITECTURE_ONTOLOGY.md and other architecture documents

**Target Audience:** System architects, product managers, executives, new developers

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

**See:** [ARCHITECTURE_IMPLEMENTATION.md](ARCHITECTURE_IMPLEMENTATION.md) for LangGraph orchestration details

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
- Entity ↔ Subject relationships are **mandatory** for entities to be discoverable
- Agent routing uses Subject ↔ LCC mappings (not entity types)

**See:** [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) Section 4 for SubjectConcept details

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

**Source:** `md/Architecture/ONTOLOGY_PRINCIPLES.md` (2025-12-26)

**See:** [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) Section 4 for Subject Layer details

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

**Source:** `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md` (2025-12-26)

**See:** [Appendices/03_Standards_Alignment/L_CIDOC_CRM_Integration_Guide.md](Appendices/03_Standards_Alignment/L_CIDOC_CRM_Integration_Guide.md) for technical implementation

---

## **1.3 System Scope**

**Historical Periods Covered:**
- Ancient Mediterranean (Greece, Rome, Near East): 3000 BCE - 500 CE
- Medieval Europe: 500 - 1500 CE
- Early Modern: 1500 - 1800 CE (initial coverage)

**Entity Types Supported:** 127 types across 14 categories  
**Relationship Types:** 311 canonical types with action structure vocabularies  
**Authority Standards:** LCC, FAST, LCSH, MARC, Wikidata, PeriodO, TGN, Pleiades, CIDOC-CRM  

**Out of Scope (V1.0):**
- Modern history (post-1800 primary focus)
- Real-time event tracking
- Social network analysis (future enhancement)
- Archaeological site excavation data (use CIDOC-CRM CRMarchaeo extension if needed)

**See:** [Appendices/01_Domain_Ontology/C_Entity_Type_Taxonomies.md](Appendices/01_Domain_Ontology/C_Entity_Type_Taxonomies.md) for complete entity taxonomy

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
**See:** [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) Section 5 (Agent Architecture)

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

**Source:** `md/Architecture/Subject_Agent_Granularity_Strategy.md` (2025-12-26)  
**See:** [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) Section 5.4 (Agent Granularity Strategy)

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

**Source:** `md/Architecture/Historical_Dating_Schema_Disambiguation.md` (2025-12-26)  
**See:** [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) Section 3.4 (Temporal Modeling), [Appendices/02_Authority_Integration/E_Temporal_Authority_Alignment.md](Appendices/02_Authority_Integration/E_Temporal_Authority_Alignment.md)

---

## **1.5 Domain Adaptability: Beyond History**

While the current implementation of Chrystallum is optimized for historical research, the underlying architecture serves as a domain-agnostic **Epistemological Engine** designed for high-stakes evidence processing. The system separates the **Universal Core** (reasoning, evidence tracking, agent orchestration) from the **Domain Pack** (ontologies, authorities, classification standards).

This modular design allows the architecture to be re-skinned for other evidence-heavy domains—such as Law, Intelligence Analysis, or Corporate Strategy—by swapping the authority modules while retaining the core logic of truth construction.

### **1.5.1 The Universal Core ("The Operating System")**

These architectural components are fundamental to any system requiring rigorous validation of unstructured text:

- **Evidence-Aware Claims Architecture:** The pipeline (`Source` → `Extraction` → `Claim` → `Validation`) is universal. Whether the source is a 1st-century chronicle (History) or a sworn deposition (Law), the requirement to trace an assertion back to a specific line of text remains identical.
    
- **Two-Stage Validation Pattern:** The separation of **LLM Extraction** (probabilistic proposal) from **Deterministic Validation** (rule-based verification) enables the use of AI in high-stakes environments where hallucination is unacceptable.
    
- **Multi-Agent Orchestration:** The pattern of using stateless, specialized agents to reason against a schema is transferable. A "Military Historian Agent" checking troop movements uses the same logic as a "Tort Law Agent" checking liability elements.

### **1.5.2 The Domain Pack ("The Cartridge")**

Adaptation requires replacing the specific semantic "cartridges" used for classification and validation:

| Component | Historical Configuration (Current) | Legal Configuration (Example) |
|---|---|---|
| **Classification** | **LCC Class D** (History) | **LCC Class K** (Law) / **West Key Number System** |
| **Ontology** | **CIDOC-CRM** (Events, Cultural Heritage) | **LKIF** (Legal Knowledge Interchange Format) |
| **Entities** | `Person`, `Place`, `Event`, `Dynasty` | `Plaintiff`, `Defendant`, `Contract`, `Statute` |
| **Backbone** | **PeriodO** (Temporal), **Pleiades** (Spatial) | **Jurisdiction** (e.g., SDNY), **Statutes of Limitation** |
| **Validation** | Historical Consensus & Source Criticality | **Stare Decisis** & Rules of Evidence |

### **1.5.3 Use Case Example: Legal Discovery**

In a legal context, Chrystallum transforms from a historical analyzer into a **Case Construction Engine**:

- **Ingestion:** Instead of ancient texts, the system ingests discovery corpora (emails, contracts, depositions).
    
- **Entity Resolution:** "Crossing the Rubicon" becomes "The Merger Meeting of Jan 10."
    
- **Argumentation:** The **CRMinf** logic used to infer historical intent is repurposed to infer **legal intent** (_mens rea_) or knowledge, linking disparate facts (an email, a calendar entry, a bank transfer) into a coherent, evidence-backed legal argument.

**Conclusion:** Chrystallum is not merely a historical tool; it is a general-purpose architecture for **structured knowledge construction from unstructured evidence**, applicable wherever truth must be derived from text with verifiable provenance.

---

### **1.5.4 Simple Explanations for Different Audiences**

#### **1. To a Friend (The "Dinner Party" Explanation)**

"You know how ChatGPT hallucinates when you ask it about specific historical details? I'm building a system called **Chrystallum** that fixes that.

Instead of just letting an AI make things up, I built a two-stage engine. First, an AI reads historical texts—like a biography of Caesar—and extracts facts. But instead of trusting those facts immediately, it passes them to a second, strict logic layer that checks them against real library standards and timelines. It's like having an impulsive grad student find the data and a grumpy, tenure-track professor verify it before it goes into the database.

The cool part? It organizes everything by _subject_ rather than just keywords. So if you ask about the 'Roman Civil War,' it knows exactly which generals, battles, and political laws are relevant because it uses the same classification system the Library of Congress uses. It's basically a hallucination-proof history engine."

---

#### **2. To a CTO (The "Architecture & Stack" Explanation)**

"Chrystallum is a **deterministic knowledge graph platform** designed to solve the provenance and hallucination problems inherent in RAG systems.

We use a **two-stage pipeline**:

1. **Ingestion & Extraction (Probabilistic):** LLM agents parse unstructured historical texts to propose entities and relationships.
    
2. **Validation & Write (Deterministic):** A LangGraph-orchestrated reasoning layer validates these proposals against a strict ontology (CIDOC-CRM extension) and authority files (Wikidata, LCC, FAST).
    

**The Stack:**

- **Storage:** Neo4j graph database acting as the ground truth.
    
- **Orchestration:** LangGraph for multi-agent coordination.
    
- **Ontology:** We map entities to canonical authorities—Wikidata QIDs for identity, Library of Congress (LCC) for classification, and PeriodO for temporal bounding.
    

**Key differentiator:** We treat 'Subjects' (like _Roman Civil War_) as first-class graph nodes that anchor subgraphs. This solves the context window problem by allowing agents to retrieve pre-validated, thematically scoped clusters of data rather than doing expensive vector similarity searches across the entire dataset."

**See:** [ARCHITECTURE_IMPLEMENTATION.md](ARCHITECTURE_IMPLEMENTATION.md) for complete technology stack details

---

#### **3. To a CEO (The "Value & Vision" Explanation)**

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
User Input → LLM Extraction → Claim Proposal → Agent Validation → Neo4j Write
    ↓             ↓                  ↓               ↓              ↓
[Text]      [Entities, Dates]  [Structured]  [Verified]     [Canonical Graph]
```

**See:** [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) for detailed layer specifications

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
- **Who/What:** Entity Layer ([ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) Section 3)
- **When:** Temporal Modeling (Section 3.4) + PeriodO ([Appendices/02_Authority_Integration/E_Temporal_Authority_Alignment.md](Appendices/02_Authority_Integration/E_Temporal_Authority_Alignment.md))
- **Where:** Geographic Integration ([Appendices/02_Authority_Integration/F_Geographic_Authority_Integration.md](Appendices/02_Authority_Integration/F_Geographic_Authority_Integration.md)) + TGN/Pleiades
- **Why/How:** Action Structure Vocabularies ([Appendices/01_Domain_Ontology/B_Action_Structure_Vocabularies.md](Appendices/01_Domain_Ontology/B_Action_Structure_Vocabularies.md)) + Claims Layer (Section 6)

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

**Alignment Strategy:** See [Appendices/03_Standards_Alignment/R_Federation_Strategy_Multi_Authority.md](Appendices/03_Standards_Alignment/R_Federation_Strategy_Multi_Authority.md)

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

**See:** [ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md) Section 6 (Claims Layer), [ARCHITECTURE_GOVERNANCE.md](ARCHITECTURE_GOVERNANCE.md) Section 10 (Quality Assurance)

---

## **Next Steps**

**For detailed specifications, continue to:**

1. **[ARCHITECTURE_ONTOLOGY.md](ARCHITECTURE_ONTOLOGY.md)** - Core ontology layers (Sections 3-7)
   - Entity Layer: Node types, properties, constraints
   - Subject Layer: SubjectConcepts, facets, LCC/FAST alignment
   - Agent Architecture: 18 specialized facet agents
   - Claims Layer: Evidence-based assertions
   - Relationship Layer: 311 canonical relationship types

2. **[ARCHITECTURE_IMPLEMENTATION.md](ARCHITECTURE_IMPLEMENTATION.md)** - Technology & workflows (Sections 8-9)
   - Neo4j, Python, LangGraph stack
   - Agent coordination patterns
   - Workflow definitions

3. **[ARCHITECTURE_GOVERNANCE.md](ARCHITECTURE_GOVERNANCE.md)** - QA & maintenance (Sections 10-12)
   - Quality assurance processes
   - Validation gates
   - Future roadmap

4. **[Appendices/](Appendices/)** - Deep dives on specific topics
   - 26 detailed appendices organized in 6 thematic clusters
   - Canonical relationship types, authority alignment, ADRs, implementation examples

---

**Document Status:** ✅ Current (extracted 2026-02-19)  
**Maintainers:** Chrystallum Architecture Team  
**Last Updated:** February 19, 2026  
**Source:** Sections 1-2 from `2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

