


---

## 5. Technology Stack and Orchestration

This section describes the implementation stack used to realize the Entity, Subject, Claims, Period, and Relationship layers, with a focus on **how agents are orchestrated in LangGraph** and how they interact with Neo4j and external tools.

## 5.1 Core Technologies

- **Python**  
    Primary implementation language for all backend services, ETL pipelines, ingestion scripts (periods, relationship types, authority mappings), and agent logic.
    
- **Neo4j (Property Graph Database)**
    
    - Stores all **Entity**, **SubjectConcept**, **Period**, **Claim**, **Belief**, **Review**, **Agent**, and **RelationshipType** nodes and edges.
        
    - Serves as the shared, canonical knowledge graph across agents.
        
    - Used for:
        
        - Schema-constrained writes (via Cypher and constraints).
            
        - Complex traversals (temporal, geographic, conceptual).
            
        - Storing provenance, multi-agent review, and promotion status.
            
- **Vector Stores (per-agent)**
    
    - Each specialist agent maintains its **own private embedding index** (documents, passages, notes).
        
    - These are not shared between agents; only the graph is shared.
        
    - Used for Retrieval-Augmented Generation (RAG) scoped by SubjectConcepts, periods, and places.
        
- **LangChain**
    
    - Provides building blocks for:
        
        - LLM calls with tools.
            
        - RAG pipelines (retrievers, document loaders, re-rankers).
            
        - Structured output parsing into Python objects that map to graph schemas.
            
- **LangGraph**
    
    - Orchestrates multi-step, multi-agent workflows as **stateful graphs**.
        
    - Each workflow is modeled as a directed graph of nodes (agents, tools, decision points) and edges (routing conditions).
        
    - Encodes:
        
        - Claim intake and normalization.
            
        - Agent routing and coordination.
            
        - Iterative review and consensus building.
            
        - Write-back to Neo4j.
            
- **Cytoscape (and related graph visualization)**
    
    - Used to visualize:
        
        - Entity-Subject-Period subgraphs.
            
        - Claim/Belief/Review structures.
            
        - RelationshipType usage patterns.
            
    - Helpful for debugging ontology design and for historian-facing UIs.
        
- **React**
    
    - Frontend for:
        
        - Claim submission and review.
            
        - Graph exploration (entities, periods, subjects, claims).
            
        - Agent activity dashboards (who reviewed what, status transitions).
            
    - Talks to a Python/GraphQL/REST backend that mediates all LLM and Neo4j access.
        
- **Figma**
    
    - Source of truth for UX and architecture diagrams.
        
    - Used to design:
        
        - The layered architecture visuals (Triple Canon, RelationshipType stack).
            
        - Interaction flows for historians and power users.
            
- **Optional: n8n (or similar workflow engine)**
    
    - Not required for core reasoning.
        
    - Potential roles:
        
        - Scheduling ETL jobs (period ingestion, authority sync, MARC enrichment).
            
        - Integrating external APIs (MARC, authority services, file import pipelines).
            
    - If used, it should handle **data plumbing**, not core AI/graph reasoning.
        

---

## 5.2 LangGraph: High-Level Workflow

LangGraph is the **primary orchestration layer** for LLM-based agents. It is used to define **agent graphs** that route claims, coordinate specialists, and enforce the promotion/validation lifecycle.

## 5.2.1 Core Nodes in the Agent Graph

A typical LangGraph workflow includes the following node types:

- **Supervisor Node (Router)**
    
    - Entry point for any new user Claim or system-generated Claim.
        
    - Tasks:
        
        - Normalize the claim text (“Caesar crossed the Rubicon”).
            
        - Extract initial candidates for entities (Caesar, Rubicon River, event), periods, places, and subject facets.
            
        - Decide which specialist agents should handle the claim based on:
            
            - Linked SubjectConcepts and facets (political, military, legal, etc.).
                
            - Canon traces (LCC, TGN, PeriodO) associated with those SubjectConcepts.
                
            - Agent capability declarations (what each agent covers).
                
- **Subject Specialist Agents**
    
    - Scoped by SubjectConcepts and facets (e.g., Roman political history, ancient military tactics, historical geography of Italy).
        
    - Each agent:
        
        - Uses its own RAG index plus graph lookups.
            
        - Proposes structured **Claims** and **Beliefs** that align with the node and edge schemas.
            
        - Attaches provenance (Work, passages, authority references).
            
        - Outputs a candidate `:Claim` JSON and associated `:Belief` instances ready for Neo4j.
            
- **Entity & Temporal Specialists**
    
    - Focused on:
        
        - Disambiguating entities (which “Caesar”, which “Rubicon”).
            
        - Anchoring events to the Year backbone and Periods.
            
        - Consulting PeriodO and your period tables to pick appropriate Period nodes.
            
    - Outputs:
        
        - Resolved entity IDs (person, place, event).
            
        - `STARTS_IN_YEAR` / `ENDS_IN_YEAR` and `OCCURRED_DURING` links.
            
        - Candidate Periods with justification.
            
- **Methodology / Source-Criticism Agent**
    
    - Uses CRMinf-style reasoning patterns and your Claim/Review schemas.
        
    - Evaluates:
        
        - Source quality and bias.
            
        - Conflicting accounts.
            
        - Degree of uncertainty and fallacies.
            
    - Outputs:
        
        - `:Review` nodes attached to Claims, with verdicts (`support/challenge/uncertain`), confidence, and fallacy annotations.
            
- **Synthesis / Arbiter Agent**
    
    - Consumes:
        
        - All candidate Claims and Beliefs from subject/temporal agents.
            
        - All Reviews and ReasoningTraces.
            
    - Computes:
        
        - Aggregated `consensus_score`.
            
        - Final Claim `status` (`validated`, `disputed`, `rejected`).
            
    - When thresholds are met, instructs the backend to:
        
        - Promote proposed structure into the core graph (e.g., materialize `ProposedEdge` into real relationships).
            
        - Update Claim and Belief nodes with consensus metadata.
            
- **Persistence Node**
    
    - A dedicated node that translates the structured outputs into Cypher write operations.
        
    - Responsibilities:
        
        - Enforce node/edge schemas (Entity, Subject, Period, Claim, Belief, Review, RelationshipType).
            
        - Maintain referential integrity (no dangling IDs, consistent constraints).
            
        - Append provenance edges and timestamps.
            

## 5.2.2 Workflow Phases

A typical end-to-end LangGraph run for a new claim:

1. **Intake & Preprocessing**
    
    - Supervisor node receives natural-language claim.
        
    - Uses LLM tools to:
        
        - Extract candidate entities, periods, and subjects.
            
        - Map to existing graph nodes or mark as new.
            
        - Create a draft `:Claim` object (status `proposed`).
            
2. **Specialist Analysis**
    
    - Supervisor routes to:
        
        - One or more Subject Specialist agents.
            
        - Entity/Temporal specialists as needed.
            
    - Each agent:
        
        - Runs a scoped RAG query.
            
        - Reads relevant subgraphs from Neo4j.
            
        - Returns candidate structured Beliefs plus explanations.
            
3. **Argumentation & Review**
    
    - Methodology agent:
        
        - Reviews each Claim/Belief.
            
        - Generates `:Review` nodes with verdicts, confidence, and reasoning summaries.
            
    - Optionally, additional meta-agents perform second-level checks (e.g., cross-domain consistency).
        
4. **Synthesis & Decision**
    
    - Synthesis agent:
        
        - Aggregates Review signals (e.g., Bayesian update or simple weighted average).
            
        - Sets `consensus_score` and Claim `status`.
            
    - Decides:
        
        - Whether to promote proposed nodes/edges.
            
        - Whether to flag the claim as disputed but keep it, or reject it outright.
            
5. **Graph Write-Back & Logging**
    
    - Persistence node:
        
        - Writes or updates the Claim, Belief, Review, and any new Entity/Period/Subject nodes.
            
        - Ensures all relationships (Belief → RelationshipType, Claim → Belief, Claim → SubjectConcept, Claim → Entity) are present.
            
    - Logs:
        
        - Agent IDs, timestamps, and ReasoningTrace IDs to allow full audit of how the conclusion was reached.
            

This orchestration pattern makes the system **explainable** to an LLM:

- Every agent has a clear scope and graph of responsibilities.
    
- Every transformation is represented as new or updated graph structure (with provenance).
    
- The LLM can “read its own footprints” by traversing Claims, Beliefs, Reviews, and ReasoningTraces in Neo4j.
    

---

## 5.3 Role of External Tools and UIs

- **ETL / Background Jobs**
    
    - Python scripts (optionally scheduled via something like n8n) handle:
        
        - Period ingestion (`time_periods.csv`, PeriodO datasets).
            
        - RelationshipType registry ingestion.
            
        - Authority alignment to LCC, LCSH, TGN, PeriodO.
            
    - These jobs run **outside** the main LangGraph workflows but prepare the canonical graph that agents use.
        
- **Frontend Integration (React + Cytoscape)**
    
    - React UI lets users:
        
        - Submit claims and inspect validation results.
            
        - Browse entities, periods, and subjects.
            
        - Visualize the argumentation network around a claim.
            
    - Cytoscape (or similar) drives interactive graph views:
        
        - Entity-Period-Subject neighborhoods.
            
        - Claim-Belief-Review clusters.
            
        - RelationshipType usage patterns over time.
            

This stack and workflow description should give any LLM enough operational context to reason about where data lives, how agents collaborate, and how to read/write structures in the system.
---

# 📘 **INTEGRATED ONTOLOGY DOCUMENT — CHUNK 1**

## **Table of Contents**

### **1. Entity Layer**

1.1 Overview  
1.2 Core Entity Types  
1.2.1 Person  
1.2.2 Event  
1.2.3 Place  
1.2.4 Period  
1.2.5 Year  
1.2.6 Organization  
1.2.7 Institution  
1.2.8 Dynasty  
1.2.9 LegalRestriction  
1.2.10 Work  
1.2.11 Position  
1.2.12 Material  
1.2.13 Object  
1.2.14 Activity  
1.3 Roman‑Specific Entity Types  
1.3.1 Gens  
1.3.2 Praenomen  
1.3.3 Cognomen  
1.4 Facets (Entity‑Level Classification Dimensions)  
1.5 Temporal Modeling (Year, Period, PeriodO)  
1.6 Example Cypher Patterns

---

# **1. ENTITY LAYER**

### _“Things in the world” — people, places, events, periods, institutions, works, and material culture._

The Entity Layer represents **real-world entities** with identity, temporality, and relationships.  
Conceptual categories are **not** entities — they live in the **Subject Layer** (§2).

Entities are the backbone of:

- historical modeling
- temporal reasoning
- geographic reasoning
- agent scoping (§3)
- claim grounding (§4)
- provenance and aboutness (§2.6, §4.11)

---

# **1.1 Overview**

The Entity Layer includes:

- **People** (individuals, historical figures)
- **Places** (cities, regions, archaeological sites)
- **Events** (battles, treaties, revolts)
- **Periods** (historical eras, dynasties, reigns)
- **Organizations** (armies, senates, cults, guilds)
- **Institutions** (legal, political, religious structures)
- **Works** (texts, inscriptions, artifacts)
- **Material culture** (objects, materials)
- **Activities** (rituals, practices, occupations)

Roman‑specific identity structures (Gens, Praenomen, Cognomen) are included as specialized Person substructures.

---

# **1.2 Core Entity Types**

Below are the canonical schemas for each core entity type.  
All schemas follow the same structure as your existing NODE_TYPE_SCHEMAS.

---

## **1.2.1 Person**

### Node Label

```cypher
:Person
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`person_id`|string|`"pers_000123"`|
|`name`|string|`"Gaius Julius Caesar"`|
|`qid`|string|`"Q1048"`|
|`gender`|string|`"male"`|

### Optional Properties

- birth_date
- death_date
- birth_place_qid
- death_place_qid
- occupation
- status (e.g., “senator”, “consul”)
- praenomen_id / nomen_id / cognomen_id (Roman-specific)

### Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`BORN_IN`|Place|Birthplace|
|`DIED_IN`|Place|Deathplace|

### Optional Edges

- `MEMBER_OF` → Organization
- `PART_OF_GENS` → Gens
- `HAS_POSITION` → Position
- `PARTICIPATED_IN` → Event
- `LIVED_DURING` → Period
- `HAS_SUBJECT_CONCEPT` → SubjectConcept (§2.5)
- `SUBJECT_OF` → Claim (§4.2)

---

## **1.2.2 Event**

### Node Label

```cypher
:Event
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`event_id`|string|`"evt_000987"`|
|`label`|string|`"Battle of Actium"`|
|`qid`|string|`"Q193304"`|

### Optional Properties

- start_date
- end_date
- location_qid
- casualties_estimate
- event_type (“battle”, “treaty”, “revolt”)

### Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`OCCURRED_AT`|Place|Location|
|`OCCURRED_DURING`|Period|Temporal context|

### Optional Edges

- `PARTICIPANT` → Person / Organization
- `HAS_SUBJECT_CONCEPT` → SubjectConcept
- `SUBJECT_OF` → Claim

---

## **1.2.3 Place**

### Node Label

```cypher
:Place
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`place_id`|string|`"plc_000456"`|
|`label`|string|`"Rome"`|
|`qid`|string|`"Q220"`|

### Optional Properties

- latitude
- longitude
- place_type (“city”, “province”, “region”)
- modern_country

### Required Edges

- `LOCATED_IN` → Place (hierarchy)

### Optional Edges

- `HAS_SUBJECT_CONCEPT` → SubjectConcept
- `SUBJECT_OF` → Claim
## **1.2.3 Place & PlaceVersion (Spatial Backbone)**

We adopt a **split-identity model** to handle the "shifting borders" problem of historical geography.

## **A. Core Concept: Identity vs. Definition**

- **`:Place` (Stable Identity)**: The abstract concept of a location (e.g., "Syria") that persists across time. It holds external authority links but NO geometry.
    
- **`:PlaceVersion` (Time/Authority-Scoped)**: A specific spatiotemporal instantiation (e.g., "Roman Province of Syria, 1st Century CE"). It holds the geometry, parent relationships, and active dates.
    

## **B. Node Schemas**

## **Node: Place**

_Represents the persistent "hook" for the entity._

text

`:Place {   place_id: "plc_00123",       // Internal ID  label: "Antioch",            // Most common name  type: "settlement",          // Generic type  qid: "Q200403",              // Wikidata ID (stable)  pleiades_id: "658381"        // Pleiades ID (stable) }`

## **Node: PlaceVersion**

_Represents a specific historical state._

text

`:PlaceVersion {   pver_id: "pver_00123_01",  label: "Antioch (Roman Period)",  start_date: "-0064",  end_date: "0637",  authority: "Pleiades",       // Source of this definition  confidence: 0.95 }`

## **Node: Geometry**

_Geometry is stored as separate nodes to allow multiple conflicting shapes for the same version._

text

`:Geometry {   geo_id: "geo_998877",  wkt: "POINT(36.16 36.20)",   // or POLYGON(...)  source: "Wikidata",  method: "centroid" }`

## **C. Relationships**

- `(:PlaceVersion)-[:VERSION_OF]->(:Place)`
    
- `(:PlaceVersion)-[:HAS_GEOMETRY]->(:Geometry)`
    
- `(:Event)-[:TOOK_PLACE_AT]->(:PlaceVersion)`
    
- `(:PlaceVersion)-[:BROADER_THAN]->(:PlaceVersion)` _(Administrative hierarchy)_

---

## **1.2.4 Period**

### Node Label

```cypher
:Period
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`period_id`|string|`"prd_000111"`|
|`label`|string|`"Roman Republic"`|
|`start`|string|`"-0510"`|
|`end`|string|`"-0027"`|



---

# **1.2.4 Period** _(continued)_

### Node Label

```cypher
:Period
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`period_id`|string|`"prd_000111"`|
|`label`|string|`"Roman Republic"`|
|`start`|string|`"-0510"`|
|`end`|string|`"-0027"`|

### Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`authority`|string|`"PeriodO"`|Source authority|
|`spatial_coverage`|string[]|`["Italy","Mediterranean"]`|Geographic scope|
|`broader_than`|string|`"Ancient Rome"`|Hierarchy|
|`narrower_than`|string[]|`["Late Republic"]`|Hierarchy|

### Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`BROADER_THAN`|Period|Parent period|
|`NARROWER_THAN`|Period|Child period|

### Optional Edges

- `HAS_SUBJECT_CONCEPT` → SubjectConcept (§2.5)
- `SUBJECT_OF` → Claim (§4.2)
- `OCCURS_DURING` → Event

---

# **1.2.5 Year**

### Node Label

```cypher
:Year
```

### Purpose

Atomic temporal entity used for:

- chronological alignment
- period boundaries
- event dating
- claim temporal grounding (§4.2, §4.9)

### Required Properties

|Property|Type|Example|
|---|---|---|
|`year_id`|string|`"year_-0049"`|
|`value`|int|`-49`|

### Optional Properties

- `label` (“49 BCE”)
- `calendar` (“proleptic Julian”)

### Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`FOLLOWED_BY`|Year|Next year|
|`PRECEDED_BY`|Year|Previous year|

---

# **1.2.6 Organization**

### Node Label

```cypher
:Organization
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`org_id`|string|`"org_000222"`|
|`label`|string|`"Roman Senate"`|
|`qid`|string|`"Q41410"`|

### Optional Properties

- organization_type (“political body”, “military unit”, “religious college”)
- founding_date
- dissolution_date

### Required Edges

- `LOCATED_IN` → Place

### Optional Edges

- `HAS_MEMBER` → Person
- `PARTICIPATED_IN` → Event
- `HAS_SUBJECT_CONCEPT` → SubjectConcept
- `SUBJECT_OF` → Claim

---

# **1.2.7 Institution**

### Node Label

```cypher
:Institution
```

### Purpose

Abstract but **real-world** structures (not conceptual categories):

- legal institutions
- political institutions
- religious institutions
- administrative systems

### Required Properties

|Property|Type|Example|
|---|---|---|
|`inst_id`|string|`"inst_000333"`|
|`label`|string|`"Roman Dictatorship"`|

### Optional Properties

- founding_date
- abolition_date
- institution_type

### Required Edges

- `LOCATED_IN` → Place

### Optional Edges

- `HAS_SUBJECT_CONCEPT` → SubjectConcept
- `SUBJECT_OF` → Claim

---

# **1.2.8 Dynasty**

### Node Label

```cypher
:Dynasty
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`dynasty_id`|string|`"dyn_000444"`|
|`label`|string|`"Julio-Claudian Dynasty"`|
|`start`|string|`"-0027"`|
|`end`|string|`"0068"`|

### Required Edges

- `RULED` → Place
- `HAS_MEMBER` → Person

### Optional Edges

- `HAS_SUBJECT_CONCEPT` → SubjectConcept
- `SUBJECT_OF` → Claim

---

# **1.2.9 LegalRestriction**

### Node Label

```cypher
:LegalRestriction
```

### Purpose

Represents laws, decrees, bans, privileges, and legal statuses.

### Required Properties

|Property|Type|Example|
|---|---|---|
|`law_id`|string|`"law_000555"`|
|`label`|string|`"Senatus Consultum Ultimum"`|
|`date`|string|`"-0052"`|

### Required Edges

- `ISSUED_BY` → Organization
- `APPLIED_TO` → Person / Group / Place

### Optional Edges

- `HAS_SUBJECT_CONCEPT` → SubjectConcept
- `SUBJECT_OF` → Claim

---

# **1.2.10 Work**

### Node Label

```cypher
:Work
```

### Purpose

Represents texts, inscriptions, manuscripts, artifacts, and modern scholarship.

### Required Properties

|Property|Type|Example|
|---|---|---|
|`work_id`|string|`"wrk_000666"`|
|`title`|string|`"Life of Caesar"`|
|`qid`|string|`"Q2896"`|

### Optional Properties

- author
- publication_date
- work_type (“ancient text”, “modern monograph”, “inscription”)

### Required Edges

- `WRITTEN_BY` → Person

### Optional Edges

- `ABOUT` → Entity / SubjectConcept (§2.6)
- `CITED_IN` → Claim (§4.2)
- `RETRIEVED_FROM` → RetrievalContext (§4.5)

---

# **1.2.11 Position**

### Node Label

```cypher
:Position
```

### Purpose

Represents offices, titles, and roles.

### Required Properties

|Property|Type|Example|
|---|---|---|
|`position_id`|string|`"pos_000777"`|
|`label`|string|`"Consul"`|

### Required Edges

- `HELD_BY` → Person
- `DURING` → Period

---

# **1.2.12 Material**

### Node Label

```cypher
:Material
```

### Purpose

Represents physical materials used in artifacts, buildings, etc.

### Required Properties

|Property|Type|Example|
|---|---|---|
|`material_id`|string|`"mat_000888"`|
|`label`|string|`"Marble"`|

### Optional Edges

- `USED_IN` → Object

---

# **1.2.13 Object**

### Node Label

```cypher
:Object
```

### Purpose

Represents artifacts, tools, weapons, coins, inscriptions, etc.

### Required Properties

|Property|Type|Example|
|---|---|---|
|`object_id`|string|`"obj_000999"`|
|`label`|string|`"Denarius of Caesar"`|

### Optional Edges

- `MADE_OF` → Material
- `FOUND_AT` → Place
- `DEPICTS` → Person / Event

---

# **1.2.14 Activity**

### Node Label

```cypher
:Activity
```

### Purpose

Represents actions, rituals, practices, occupations.

### Required Properties

|Property|Type|Example|
|---|---|---|
|`activity_id`|string|`"act_000123"`|
|`label`|string|`"Triumph"`|

### Optional Edges

- `PERFORMED_BY` → Person
- `OCCURRED_AT` → Place
- `DURING` → Period

---

# **1.3 Roman‑Specific Entity Types**

These extend the Person model.

---

## **1.3.1 Gens**

### Node Label

```cypher
:Gens
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`gens_id`|string|`"gens_000001"`|
|`label`|string|`"Julia"`|

### Required Edges

- `HAS_MEMBER` → Person

---

## **1.3.2 Praenomen**

### Node Label

```cypher
:Praenomen
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`praenomen_id`|string|`"prae_000001"`|
|`label`|string|`"Gaius"`|

---

## **1.3.3 Cognomen**

### Node Label

```cypher
:Cognomen
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`cognomen_id`|string|`"cog_000001"`|
|`label`|string|`"Caesar"`|

---

# **1.4 Facets (Entity‑Level Classification Dimensions)**

These facets classify entities along analytical dimensions.
Canonical source of truth: `Facets/facet_registry_master.json` (with tabular export at `Facets/facet_registry_master.csv`).
Temporal modeling remains in Section 1.5 and is not counted as a facet in the active registry.

- Geographic
- Political
- Cultural
- Technological
- Religious
- Economic
- Military
- Environmental
- Demographic
- Intellectual
- Scientific
- Artistic
- Social
- Linguistic
- Archaeological
- Diplomatic

Entities may link to SubjectConcepts representing these facets (§2.2).

## **Place & PlaceVersion Architecture** → **Section 1.2.3** (Replace existing Place schema)

**Current Location:** §1.2.3 Place (simple schema)  
**New Structure:**

- §1.2.3.A Core Concept: Identity vs. Definition
    
- §1.2.3.B Node Schemas (Place, PlaceVersion, Geometry)
    
- §1.2.3.C Relationships
    

**Pattern Match:** Follows same structure as §1.2.1 Person, §1.2.2 Event (Required Properties → Optional Properties → Required Edges → Optional Edges)

# **1.5 Temporal Modeling (Year, Period, PeriodO)**
---

## 1.5 Temporal Modeling ⭐ Year Backbone, Periods, and Eras

## Goals

- Provide a simple, global **Year backbone** for all temporal reasoning.
    
- Layer **cultural Periods and Eras** on top (political, economic, technical, etc.).
    
- Support **fuzzy dates** (start/end ranges) and long-running events without going to daily resolution.
    

---

## Year Node Schema ⭐ Global Temporal Backbone

## Node Label

text

`:Year`

## Purpose

Represent a single calendar year on a continuous backbone from at least −2000 to 2025 (extensible), with ordered adjacency. Any entity or claim with a temporal aspect must tether to this Year backbone.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)]​

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`year`|int|`-49`|Astronomical year (BC negative)|
|`label`|string|`"49 BCE"`|Human-readable label|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`iso`|string|`"-0049"`|Zero-padded year text|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`PRECEDED_BY`|Year|Previous year in sequence|
|`FOLLOWED_BY`|Year|Next year in sequence|

---

## Period Node Schema ⭐ Cultural / Historical Periods

(You already have Period in the Entity layer; this clarifies temporal semantics and fuzzy ranges.)[2-12-26-Chrystallum-Architecture-DRAFT.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4598a569-9988-45f3-8efd-32917d0dc056/2-12-26-Chrystallum-Architecture-DRAFT.md)

## Node Label

text

`:Period`

## Purpose

Represent a named period (e.g., Roman Republic, Julio-Claudian dynasty, Industrial Revolution) with fuzzy start/end ranges and links to the Year backbone.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`period_id`|string|`"prd_000111"`|Unique ID|
|`label`|string|`"Roman Republic"`|Name|
|`start`|string|`"-0510"`|Nominal start year (string)|
|`end`|string|`"-0027"`|Nominal end year (string)|

## Optional Properties (Fuzzy Bounds)

|Property|Type|Example|Notes|
|---|---|---|---|
|`earliest_start`|string|`"-0520"`|Earliest plausible start|
|`latest_start`|string|`"-0500"`|Latest plausible start|
|`earliest_end`|string|`"-0035"`|Earliest plausible end|
|`latest_end`|string|`"-0020"`|Latest plausible end|
|`authority`|string|`"PeriodO"`|Authority source (PeriodO, custom, etc.)|
|`authority_uri`|string|PeriodO URI|External identifier|
|`culture`|string|`"Roman"`|Cultural frame|
|`facet`|string|`"political"`|Political/economic/technical/etc. facet|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`STARTS_IN_YEAR`|Year|Link to nominal start Year node|
|`ENDS_IN_YEAR`|Year|Link to nominal end Year node|

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`BROADER_THAN`|Period|Period hierarchy (e.g., Empire > Early Empire)|
|`NARROWER_THAN`|Period|Inverse|
|`ALIGNED_WITH`|Period|Alignment to PeriodO or other federations|

---

## Era as Faceted Periods ⭐ Stacked Timelines

You can represent political, economic, technical, and other **Eras** as `:Period` nodes with `facet` + `culture` set appropriately, giving you stacked timelines by facet and culture.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)]​

Examples:

- Political era: `label="Late Republic"`, `facet="political"`, `culture="Roman"`.
    
- Economic era: `label="Mediterranean grain economy"`, `facet="economic"`.
    
- Technical era: `label="Iron Age"`, `facet="technical"`, `culture` as needed.
    

Stacked view = all Periods for a given culture, grouped by facet and aligned via `STARTS_IN_YEAR` / `ENDS_IN_YEAR`.

---

## Decade / Century / Millennium Concepts

To avoid a deep native hierarchy beyond Year, you can either:

- Model `:Period` nodes for named decades/centuries (curated, culture-dependent).
    
- Or, if helpful, add simple structural nodes:
    

text

`:Decade :Century :Millennium`

With:

- `BELONGS_TO_DECADE`, `BELONGS_TO_CENTURY`, `BELONGS_TO_MILLENNIUM` edges from Year.
    
- These higher-level temporal concepts remain curated, not global.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)]​
    

If you want to keep it minimal, treating named centuries as `:Period` nodes is usually sufficient.

---

## Event–Year Wiring for Ranges

You already store `start_date` / `end_date` on events.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4598a569-9988-45f3-8efd-32917d0dc056/2-12-26-Chrystallum-Architecture-DRAFT.md)]​

Two options for wiring to Year:

1. **Minimal** (recommended default):
    
    - `(:Event)-[:OCCURRED_DURING]->(:Period)`
        
    - `(:Event)-[:STARTS_IN_YEAR]->(:Year)`
        
    - `(:Event)-[:ENDS_IN_YEAR]->(:Year)`
        
    - Timelines derive intermediate years by range expansion at query time.
        
2. **Dense** (only for specific UIs):
    
    - Also create `(:Event)-[:ACTIVE_IN_YEAR]->(:Year)` for each year between start and end.
        
    - Use only when you need fast year-by-year adjacency browsing and you’ve tested scale.
        

Given your concern about thousands of years, I’d encode **start/end only in the KG**, and let the UI or a materialized view handle expanded `ACTIVE_IN_YEAR` where needed.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)]​

---

If you like this shape, I can next:

- Add a tiny **Year node schema** subsection into 1.5 of the Chrystallum doc and adjust the existing Period section to reference `earliest_start/latest_end` and the Year backbone explicitly.

---

# **1.6 Example Cypher Patterns**

### Create a Person

```cypher
CREATE (p:Person {
  person_id: "pers_000123",
  name: "Gaius Julius Caesar",
  qid: "Q1048"
})
```

### Link Person to Gens

```cypher
MATCH (p:Person {qid:"Q1048"}), (g:Gens {label:"Julia"})
CREATE (p)-[:PART_OF_GENS]->(g)
```

### Create an Event with temporal and spatial context

```cypher
MATCH (rome:Place {label:"Rome"}), (rep:Period {label:"Roman Republic"})
CREATE (e:Event {
  event_id:"evt_000987",
  label:"Caesar Crosses the Rubicon",
  start_date:"-0049-01-10"
})
CREATE (e)-[:OCCURRED_AT]->(rome)
CREATE (e)-[:OCCURRED_DURING]->(rep)
```

### Link Work to SubjectConcept (aboutness)

```cypher
MATCH (w:Work {title:"Life of Caesar"}), (sc:SubjectConcept {authority_id:"n79021400"})
CREATE (w)-[:ABOUT]->(sc)
```

---
Absolutely, Tony — let’s continue with **Chunk 2**, the **Subject Layer**, fully integrated with your framework, your facet system, your authority mappings, and the Claims + Agent architectures.

This is a **large, dense, production‑grade section**, and it’s structured to drop directly into your master ontology document.

### Additional information - most recent 2-12-26
## 1.5 Temporal Modeling ⭐ Year Backbone, Periods, Facets, and Authorities

The temporal layer combines a **global Year backbone**, a curated set of **historiographic Periods**, and external **authority alignments** (PeriodO, LCSH, Wikidata).[2-12-26-Temporal-Schema.md+2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)

## 1.5.1 Year Backbone

- Global `:Year` nodes from at least −2000 to 2025, ordered linearly.2-12-26-Temporal-Schema.md​
    
- Every temporally grounded entity or claim ultimately tethers to one or more Years.
    

text

`(:Year {year: -49, label: "49 BCE"})-[:FOLLOWED_BY]->(:Year {year: -48}) (:Year {year: -48})-[:PRECEDED_BY]->(:Year {year: -49})`

Years are used as the **low-level temporal grid**; higher-level periods sit on top.

---

## 1.5.2 Periods from Wikidata Seed (time_periods.csv)

The primary seed list for periods comes from `time_periods.csv`, which provides:time_periods.csv​

- QID (Wikidata URI).
    
- Label.
    
- Start / End year (integer years).
    
- One or more locations (URIs).
    
- One or more **facet tags** (e.g., `CulturalFacet`, `PoliticalFacet`, `ArchaeologicalFacet`).
    
- The corresponding facet relationship names (e.g., `HAS_CULTURAL_FACET`, `HAS_POLITICAL_FACET`, `HAS_ARCHAEOLOGICAL_FACET`).
    

Example row (simplified):time_periods.csv​

- QID: `Q201038` (Roman Kingdom)
    
- Label: `Roman Kingdom`
    
- Start: `-752`
    
- End: `-508`
    
- Locations: `[Q1048669]` (Latium)
    
- Facets: `[CulturalFacet, PoliticalFacet]`
    
- FacetRelationships: `[HAS_CULTURAL_FACET, HAS_POLITICAL_FACET]`
    

These rows are ingested as candidate `:Period` nodes with:

- `period_id` / `qid` / `label`.
    
- `start` / `end` (string years) + `STARTS_IN_YEAR` / `ENDS_IN_YEAR` edges to `:Year`.
    
- Facet edges from Period to facet nodes (e.g., `(period)-[:HAS_CULTURAL_FACET]->(:Facet {label:"Cultural"})`).time_periods.csv​
    

Decades and centuries (e.g., “1st century BCE”) are modeled the same way: as curated `:Period` nodes with appropriate start/end and facet metadata, not as a separate structural type.2-12-26-Temporal-Schema.md​

---

## 1.5.3 Tiered Period Classification (Period vs Event vs InstitutionalSpan)

Not every Wikidata “period” should remain a `:Period`. A separate classification plan divides the ~130+ entries into four tiers:PERIOD_CLASSIFICATION_PLAN.md​

- **Tier 1 – Historical Periods (keep as `:Period`)**
    
    - Extended spans (decades+).
        
    - Widely used in historiography.
        
    - Coherent political/social/cultural patterns.
        
    - Examples: `Migration Period (Q131192)`, `Early Middle Ages (Q202763)`, `Dutch Golden Age (Q661566)`, `Viking Age (Q213649)`.[PERIOD_CLASSIFICATION_PLAN.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)
        
- **Tier 2 – Events / Phases (relabel as `:Event`)**
    
    - Short duration (often < 5–10 years).
        
    - Better modeled as wars, crises, campaigns, or phases of larger conflicts.
        
    - Examples: `barracks emperor (Q129167)`, `Crisis of the Third Century (Q329838)`, `Reign of Terror (Q193547)`, `Phoney War (Q190882)`.[PERIOD_CLASSIFICATION_PLAN.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)
        
- **Tier 3 – Institutional Spans (e.g., `:InstitutionalSpan`)**
    
    - Lifetimes of courts, offices, archives, etc.
        
    - Administrative or bureaucratic intervals, not historiographic periods.
        
    - Examples: `Rehnquist Court (Q23019825)`, `Birmingham pen trade (Q4916863)`.PERIOD_CLASSIFICATION_PLAN.md​
        
- **Tier 4 – Problematic / Non-period Entries**
    
    - Disciplines masquerading as periods (`Classics (Q12793702)`).
        
    - Suspicious or overly broad date ranges.
        
    - Vague regional spans.
        
    - These are reviewed and either removed or reclassified.[time_periods.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)
        

The classification plan is implemented as transformations on the initial `:Period` imports:

- Relabel some candidates as `:Event` or `:InstitutionalSpan`.
    
- Delete or reclassify Tier 4 entries.
    
- Keep Tier 1 as the canonical `:Period` set that agents and claims will use for temporal reasoning.
    

---

## 1.5.4 Faceted Periods and Stacked Timelines

Facet tags from `time_periods.csv` (e.g., `CulturalFacet`, `PoliticalFacet`, `ArchaeologicalFacet`) are used to attach Periods to your existing facet model, enabling **stacked timelines**:[2-12-26-Temporal-Schema.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)

- Cultural periods (e.g., `Minoan civilization (Q134178)`) → `HAS_CULTURAL_FACET`.
    
- Political eras (e.g., `Roman Kingdom (Q201038)`) → `HAS_POLITICAL_FACET`.
    
- Archaeological phases (e.g., `Helladic period (Q937774)`) → `HAS_ARCHAEOLOGICAL_FACET`.
    

By querying Periods for a given `culture` + `facet` and aligning them via `STARTS_IN_YEAR` / `ENDS_IN_YEAR`, you can generate stacked timelines such as:

- Political eras vs economic eras vs technical eras for a given region.[2-12-26-Temporal-Schema.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1f675f67-89d8-4bf8-a447-52317c814ec9/2-12-26-Temporal-Schema.md)
    

---

## 1.5.5 Authority Alignment (PeriodO, LCSH, SubjectConcepts)

External period authorities are integrated in two steps:[periodo-dataset.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/7bce58bb-f521-40e3-a9e8-690964d81d3c/periodo-dataset.csv)

1. **PeriodO & CSV dataset (`periodo-dataset.csv`)**
    
    - Provides curated period definitions (labels, bounds, region, authority URIs).
        
    - Used to enrich `:Period` nodes with `authority="PeriodO"`, `authority_uri`, and potentially finer start/end ranges.periodo-dataset.csv​
        
2. **LCSH / Subject Layer mapping (`period_lcsh_mapping_phase1_*.json`)**
    
    - Maps your `:Period` nodes (by QID) to LCSH and other subject headings.
        
    - For each mapping, you create or link to a `:SubjectConcept` and connect:
        
        - `(:Period)-[:ALIGNED_WITH]->(:SubjectConcept)` or
            
        - `(:SubjectConcept)-[:ABOUT_PERIOD]->(:Period)`.period_lcsh_mapping_phase1_20260108_134151.json​
            

This ties the temporal model directly into the Subject Layer (for classification and agent domains) and into library authorities.

---

## 1.5.6 Event–Period–Year Wiring (Minimal Pattern)

For events, the temporal pattern is intentionally minimal, to avoid over-edging long ranges:[2-12-26-Chrystallum-Architecture-DRAFT.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4598a569-9988-45f3-8efd-32917d0dc056/2-12-26-Chrystallum-Architecture-DRAFT.md)

- Properties: `start_date`, `end_date`.
    
- Edges:
    

text

`(:Event)-[:OCCURRED_DURING]->(:Period)      // main temporal context (:Event)-[:STARTS_IN_YEAR]->(:Year)         // from start_date year (:Event)-[:ENDS_IN_YEAR]->(:Year)           // from end_date year`

Intermediate years are expanded **at query/UI time** (e.g., when building a year-by-year timeline), rather than storing an `ACTIVE_IN_YEAR` edge for each year of a long event.2-12-26-Temporal-Schema.md​

This combination—Year backbone + curated, tiered Periods + facet tags + authority mappings—gives you a compact but very expressive temporal substrate for agents, claims, and historian-grade reasonin

## **1.7 Schema Enforcement & DDL**

We explicitly enforce data integrity using Neo4j Constraints.

## **A. Uniqueness Constraints**

text

`// Core Identity CREATE CONSTRAINT person_id_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE; CREATE CONSTRAINT place_id_unique IF NOT EXISTS FOR (p:Place) REQUIRE p.place_id IS UNIQUE; CREATE CONSTRAINT claim_id_unique IF NOT EXISTS FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE; // External Keys CREATE CONSTRAINT qid_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.qid IS UNIQUE;`

## **B. Architectural Decisions**

1. **SKOS Directionality**: We use **`BROADER_THAN` only**.
    
    - _Reasoning_: Reduces graph density by 50%. The inverse (`NARROWER_THAN`) is implied and handled at query time by traversing `<-[:BROADER_THAN]-`.
        
2. **Facet Policy (Hybrid)**:
    
    - **Primary Facet**: Stored as a property for speed (e.g., `Period.facet = 'Political'`).
        
    - **Complex Facets**: Stored as nodes for hierarchy (e.g., `(:Period)-[:HAS_FACET]->(:Facet {label: 'Naval Warfare'})`).

---

# 📘 **INTEGRATED ONTOLOGY DOCUMENT — CHUNK 2**

# **2. SUBJECT LAYER**

### _Conceptual classification, authority alignment, topic hierarchy, and agent domain structure._

The Subject Layer is the **conceptual backbone** of the ontology.  
It defines:

- the **SubjectConcept** node type
- the **facet system**
- the **SKOS-like hierarchy**
- the **multi-authority metadata model** (LCSH, FAST, LCC, Dewey, VIAF, GND, Wikidata)
- the **Topic Spine**
- the **CIP → QID → LCC → LCSH → FAST chain**
- the **Framework Layer** (your outline)
- the **Academic Discipline** model
- the **Entity→Subject mapping rules**
- the **Work→Subject aboutness model**
- the **Agent domain assignment logic**

This layer is where **all conceptual modeling lives**.  
There is **no Concept entity** — all conceptual categories are **SubjectConcepts**.

---

# **2.0 Subject Layer Overview**

The Subject Layer provides:

- a **polyhierarchical, faceted classification system**
- a **multi-authority alignment layer**
- a **semantic grounding layer** for agents
- a **topic-based routing layer** for claims
- a **conceptual map** for historical knowledge

SubjectConcepts are the **conceptual analog** to Entities:

|Layer|Represents|Examples|
|---|---|---|
|**Entity Layer**|Things in the world|Caesar, Rome, Actium|
|**Subject Layer**|Concepts about the world|Roman politics, civil war, dictatorship|

---

# **2.1 SubjectConcept Node Schema**

### Node Label

```cypher
:SubjectConcept
```

### Purpose

Represents a conceptual category, topic, theme, or subject heading.  
This includes:

- topical subjects
- academic disciplines
- LCSH/FAST headings
- LCC classes
- CIP categories
- Topic Spine nodes
- facets

### Required Properties

|Property|Type|Example|
|---|---|---|
|`subject_id`|string|`"subj_000123"`|
|`label`|string|`"Rome—Politics and government—510–30 B.C."`|
|`facet`|string|`"Political"`|

### Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`authority_id`|string|`"sh85115055"`|LCSH ID|
|`fast_id`|string|`"fst01234567"`|FAST ID|
|`lcc_class`|string|`"DG"`|LCC class|
|`lcc_subclass`|string|`"DG209"`|LCC subclass|
|`cip_code`|string|`"22.01"`|CIP category|
|`qid`|string|`"Q123456"`|Wikidata concept|
|`broader_label`|string|`"Roman history"`|For convenience|
|`narrower_labels`|string[]|`["Roman Republic"]`|For convenience|

### Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`BROADER_THAN`|SubjectConcept|SKOS broader|
|`NARROWER_THAN`|SubjectConcept|SKOS narrower|

### Optional Edges

- `ALIGNED_WITH` → SubjectConcept (cross-authority alignment)
- `HAS_FACET` → Facet node
- `ABOUT_ENTITY` → Entity (semantic grounding)
- `ABOUT_PERIOD` → Period
- `ABOUT_EVENT` → Event
- `SUBJECT_OF` → Claim (§4.2)

---

# **2.2 Facets (Subject-Level)**

Your facet system is the backbone of conceptual classification.

### Facet List

Canonical source of truth: `Facets/facet_registry_master.json` (with tabular export at `Facets/facet_registry_master.csv`).
Temporal modeling remains in Section 1.5 and is not counted as a facet in the active registry.

- Geographic
- Political
- Cultural
- Technological
- Religious
- Economic
- Military
- Environmental
- Demographic
- Intellectual
- Scientific
- Artistic
- Social
- Linguistic
- Archaeological
- Diplomatic

### Facet Node Label

```cypher
:Facet
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`facet_id`|string|`"facet_political"`|
|`label`|string|`"Political"`|

### Required Edges

- `HAS_FACET` → SubjectConcept

---

# **2.3 SKOS-Like Hierarchy**

SubjectConcepts form a **polyhierarchical** structure:

```
BROADER_THAN
NARROWER_THAN
RELATED_TO (optional)
```

### Example

```
"Roman history"
    BROADER_THAN
        "Ancient history"
    NARROWER_THAN
        "Roman Republic"
        "Roman Empire"
```

### Cypher Example

```cypher
MATCH (parent:SubjectConcept {label:"Roman history"})
MATCH (child:SubjectConcept {label:"Roman Republic"})
CREATE (parent)-[:NARROWER_THAN]->(child)
CREATE (child)-[:BROADER_THAN]->(parent)
```

---

# **2.4 Multi-Authority Metadata**

Each SubjectConcept may carry metadata from:

- **LCSH** (`authority_id`)
- **FAST** (`fast_id`)
- **LCC** (`lcc_class`, `lcc_subclass`)
- **CIP** (`cip_code`)
- **Wikidata** (`qid`)
- **GND**, **VIAF**, **Dewey** (optional)

### Purpose

- unify legacy cataloging systems
- support agent domain assignment (§3.5)
- support claim classification (§4.2)
- support crosswalks (§2.11)

---

# **2.5 Entity → Subject Mapping**

Entities link to SubjectConcepts via:

```
(entity)-[:HAS_SUBJECT_CONCEPT]->(subjectConcept)
```

### Example

```cypher
MATCH (p:Person {qid:"Q1048"})
MATCH (sc:SubjectConcept {authority_id:"n79021400"})
CREATE (p)-[:HAS_SUBJECT_CONCEPT]->(sc)
```

### Mapping Rules

- Persons → biography, occupation, era
- Events → event type, participants, location
- Places → geographic hierarchy
- Works → aboutness (§2.6)
- Periods → historical classification

---

# **2.6 Work → Subject Aboutness**

Works link to SubjectConcepts via:

```
(work)-[:ABOUT]->(subjectConcept)
```

### Example

```cypher
MATCH (w:Work {title:"Life of Caesar"})
MATCH (sc:SubjectConcept {label:"Roman politics"})
CREATE (w)-[:ABOUT]->(sc)
```

### Aboutness supports:

- RAG retrieval (§4.5)
- claim provenance (§4.2)
- agent training (§3.5)

---

# **2.7 Topic Spine**

The Topic Spine is a **canonical, curated hierarchy** of SubjectConcepts that:

- spans all facets
- provides a stable conceptual backbone
- supports agent routing (§3.6)
- supports claim classification (§4.2)

### Structure

```
History
    Ancient History
        Roman History
            Roman Republic
                Roman Politics
                    Civil War
                        Caesar’s Dictatorship
```

### Node Label

```cypher
:TopicSpine
```

### Edges

- `SPINE_PARENT`
- `SPINE_CHILD`

---

# **2.8 CIP → QID → LCC → LCSH → FAST Chain**

This is your **cross-authority alignment pipeline**.

### Chain

```
CIP category
    ↳ maps to Wikidata QID
        ↳ maps to LCC class/subclass
            ↳ maps to LCSH heading
                ↳ maps to FAST heading
```

### Purpose

- unify modern academic classification
- support agent domain assignment (§3.5)
- support subject normalization

### Example Mapping

|Layer|Example|
|---|---|
|CIP|22.01 (History)|
|QID|Q11772 (History)|
|LCC|D (World History)|
|LCSH|sh85061212 (History)|
|FAST|fst00958235 (History)|

---

# **2.9 Academic Discipline Modeling**

Academic disciplines are modeled as SubjectConcepts with:

- `facet: "Intellectual"`
- `discipline: true`

### Examples

- History
- Archaeology
- Classics
- Political Science
- Economics

### Edges

- `BROADER_THAN` → parent discipline
- `RELATED_TO` → adjacent disciplines

---

# **2.10 Subject Evolution**

SubjectConcepts may evolve over time:

- new concepts added
- deprecated concepts merged
- authority metadata updated
- crosswalks refined

### Versioning Properties

- `created_at`
- `updated_at`
- `deprecated`

---

# **2.11 Framework Layer (Your Outline)**

### _Authority Systems, Crosswalks, and Agent Scope Analysis_

This section integrates your top-level outline into the Subject Layer.

---

## **2.11.1 Official Subject Ontology (LCC)**

### LCC Classes

- A — General Works
- B — Philosophy, Psychology, Religion
- C — Auxiliary Sciences of History
- D — World History
- E–F — American History
- G — Geography, Anthropology
- H — Social Sciences
- J — Political Science
- K — Law
- L — Education
- M — Music
- N — Fine Arts
- P — Language & Literature
- Q — Science
- R — Medicine
- S — Agriculture
- T — Technology
- U — Military Science
- V — Naval Science
- Z — Bibliography, Library Science

### LCC Subclasses

Mapped to SubjectConcepts via:

```
(subject)-[:HAS_LCC_CLASS]->(lccClass)
```

---

## **2.11.2 Modern Subject Ontology**

Your normalized, faceted, polyhierarchical subject system.

### Features

- facet-aware
- polyhierarchical
- cross-authority aligned
- agent-friendly

---

## **2.11.3 Cross-LCC Class Normalization**

Purpose:

- unify disparate LCC subclasses
- normalize across disciplines
- support agent scoping

### Example

```
DG (Roman History)
    ↳ normalized to "Roman History" (Topic Spine)
```

---

## **2.11.4 Agent Assignment (via Subject Layer)**

Agents own domains defined by:

- SubjectConcepts
- LCC classes
- CIP categories
- Topic Spine nodes

### Example

```
roman_republic_agent
    OWNS_DOMAIN → "Roman Republic"
    OWNS_DOMAIN → "Roman Politics"
    OWNS_DOMAIN → "Civil War"
```

---

## **2.11.5 CIP → QID → LCC → LCSH → FAST (Crosswalk)**

This is the **canonical crosswalk** used for:

- subject normalization
- agent domain inference
- claim classification

---

## **2.11.6 Academic Discipline Integration**

Disciplines are SubjectConcepts with:

- `facet: "Intellectual"`
- `discipline: true`

Used for:

- agent specialization
- claim review routing (§4.3)

---

# **2.12 Cypher Examples**

### Create a SubjectConcept

```cypher
CREATE (sc:SubjectConcept {
  subject_id:"subj_000123",
  label:"Roman politics",
  facet:"Political",
  authority_id:"sh85115055"
})
```

### Link SubjectConcept to LCC

```cypher
MATCH (sc:SubjectConcept {label:"Roman history"})
MATCH (lcc:LCC {class:"DG"})
CREATE (sc)-[:HAS_LCC_CLASS]->(lcc)
```

### Map Work to SubjectConcept

```cypher
MATCH (w:Work {title:"Life of Caesar"})
MATCH (sc:SubjectConcept {label:"Roman Republic"})
CREATE (w)-[:ABOUT]->(sc)
```

### Agent domain assignment

```cypher
MATCH (agent:Agent {agent_id:"roman_republic_agent"})
MATCH (sc:SubjectConcept {label:"Roman Republic"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc)
```

---

Absolutely, Tony — here is **Chunk 3**, the **Agent Layer**, fully integrated, cleanly structured, cross‑linked to the Entity, Subject, and Claims layers, and ready to drop directly into your master ontology document.

This is a **large, production‑grade section**, matching the style and rigor of Chunks 1 and 2.

---

# 📘 **INTEGRATED ONTOLOGY DOCUMENT — CHUNK 3**

# **3. AGENT LAYER**

### _Distributed expertise, domain ownership, routing, reasoning, memory, and multi‑agent coordination._

The Agent Layer defines the **intelligent actors** that:

- classify entities and works
- generate claims (§4)
- review claims (§4.3)
- perform reasoning (§4.4)
- retrieve evidence (§4.5)
- maintain memory (§4.6)
- coordinate consensus (§4.7)
- route tasks across the system

Agents are the **active reasoning layer** of the ontology.

---

# **3.0 Agent Layer Overview**

Agents operate as:

- **Subject Agents** — experts in conceptual domains
- **Entity Agents** — experts in specific entity types
- **Coordinator Agents** — orchestrators of multi-agent workflows

Agents use:

- Subject Layer (§2) for domain grounding
- Entity Layer (§1) for factual grounding
- Claims Layer (§4) for knowledge production

Agents are **not** LLMs — they are **graph-native actors** with:

- explicit domain scopes
- explicit memory
- explicit reasoning traces
- explicit retrieval contexts
- explicit claim generation and review protocols

---

# **3.1 Agent Node Schema**

### Node Label

```cypher
:Agent
```

### Required Properties

|Property|Type|Example|
|---|---|---|
|`agent_id`|string|`"roman_republic_agent"`|
|`label`|string|`"Roman Republic Specialist"`|
|`agent_type`|string|`"subject"`|

### Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`description`|string|`"Expert in Roman political history"`|Human-readable|
|`confidence_calibration`|float|`0.92`|Calibration factor|
|`specialization_level`|string|`"high"`|Generalist vs specialist|
|`created_at`|string|ISO 8601|Creation timestamp|

### Required Edges

- `OWNS_DOMAIN` → SubjectConcept (§3.5)
- `REVIEWED` → Review (§4.3)
- `MADE_CLAIM` → Claim (§4.2)

### Optional Edges

- `TRAINED_ON` → Work
- `INCLUDES_CONCEPT` → SubjectConcept
- `MEMORY_OF` → AgentMemory (§4.6)
- `PERFORMED_BY` → Synthesis (§4.7)

---

# **3.2 Subject Agents**

Subject Agents specialize in **conceptual domains**, defined by:

- SubjectConcepts
- LCC classes
- CIP categories
- Topic Spine nodes
- Facets

### Example

```
roman_republic_agent
    OWNS_DOMAIN → "Roman Republic"
    OWNS_DOMAIN → "Roman politics"
    OWNS_DOMAIN → "Civil war"
```

### Responsibilities

- classify claims by subject
- review claims within domain
- generate interpretive claims
- detect fallacies (§4.3)
- perform synthesis (§4.7)

---

# **3.3 Entity Agents**

Entity Agents specialize in **entity types**, such as:

- Person
- Event
- Place
- Period
- Organization
- Work

### Example

```
event_agent
    OWNS_ENTITY_TYPE → Event
```

### Responsibilities

- validate entity properties
- detect entity-level inconsistencies
- classify events by type
- support claim grounding

---

# **3.4 Coordinator Agents**

Coordinator Agents orchestrate:

- claim review workflows
- reviewer selection
- consensus scoring
- promotion of validated claims (§4.9)
- synthesis of conflicting claims (§4.7)

### Example

```
claims_coordinator
    agent_type: "coordinator"
```

### Responsibilities

- identify claims needing review
- route claims to appropriate agents
- compute consensus_score
- update claim.status
- trigger promotion

---

# **3.5 Agent Scope Definition**

Agent scope is defined by:

- SubjectConcepts
- LCC classes
- CIP categories
- Topic Spine nodes
- Facets
- Entity types

### Scope Graph

```
(agent)-[:OWNS_DOMAIN]->(subjectConcept)
(agent)-[:OWNS_ENTITY_TYPE]->(entityType)
(agent)-[:INCLUDES_CONCEPT]->(subjectConcept)
```

### Example

```cypher
MATCH (agent:Agent {agent_id:"roman_republic_agent"})
MATCH (sc:SubjectConcept {label:"Roman Republic"})
CREATE (agent)-[:OWNS_DOMAIN]->(sc)
```

---

# **3.6 Agent Routing**

Routing determines **which agent handles which task**.

### Routing Inputs

- subject classification
- entity type
- facet
- claim type
- temporal/geographic context

### Routing Logic

1. Identify SubjectConcepts linked to the claim/entity/work
2. Find agents with `OWNS_DOMAIN` over those concepts
3. If none found, escalate to broader concepts
4. If still none, route to generalist agent

### Example Query

```cypher
MATCH (claim:Claim {claim_id:"claim_000123"})-[:SUBJECT_OF]->(sc:SubjectConcept)
MATCH (agent:Agent)-[:OWNS_DOMAIN]->(sc)
RETURN agent
```

---

# **3.7 Cross-Facet Fusion**

Some tasks require **multiple agents**:

- political + military
- geographic + temporal
- economic + demographic

Fusion is achieved via:

```
(agentA)-[:COLLABORATES_WITH]->(agentB)
```

Or via Synthesis nodes (§4.7).

---

# **3.8 Confidence Scoring**

Agents maintain:

- internal confidence
- calibration factor
- Bayesian posterior (§4.3)

### Final confidence

[ \text{final} = \text{raw} \times \text{calibration} ]

### Stored in:

- Claim.confidence
- Review.confidence
- Review.bayesian_posterior
- Claim.consensus_score

---

# **3.9 Bayesian Logic + Fischer’s Fallacies**

Agents apply:

### Bayesian Updating

- prior belief
- likelihood from evidence
- posterior stored in `bayesian_posterior`

### Fallacy Detection

Agents check for:

- anachronism
- post hoc
- argument from silence
- source bias
- teleology
- overgeneralization

Stored in:

```
review.fallacies_detected
trace.fallacy_checks
```

---

# **3.10 Agent Memory**

Agents maintain memory via:

```
(memory:AgentMemory)-[:MEMORY_OF]->(agent)
```

Memory types:

- interaction_history
- topic_profile
- user_context
- hypothesis_tracking
- collaboration_state

### Example

```cypher
CREATE (m:AgentMemory {
  memory_id:"mem_000321",
  agent_id:"roman_republic_agent",
  memory_type:"topic_profile",
  topics_covered:["Roman politics","Civil war"]
})
```

---

# **3.11 Agent Lifecycle**

### Stages

1. **Initialization**
    
    - domain assignment
    - training on works
2. **Operation**
    
    - claim generation
    - claim review
    - reasoning
    - retrieval
3. **Coordination**
    
    - consensus
    - synthesis
    - promotion
4. **Evolution**
    
    - domain expansion
    - calibration updates
    - memory updates
5. **Retirement**
    
    - deprecated agents
    - domain transfer

---

# **3.12 Cypher Examples**

### Create an Agent

```cypher
CREATE (a:Agent {
  agent_id:"roman_republic_agent",
  label:"Roman Republic Specialist",
  agent_type:"subject"
})
```

### Assign Domain

```cypher
MATCH (a:Agent {agent_id:"roman_republic_agent"})
MATCH (sc:SubjectConcept {label:"Roman Republic"})
CREATE (a)-[:OWNS_DOMAIN]->(sc)
```

### Route Claim to Agents

```cypher
MATCH (claim:Claim {claim_id:"claim_000123"})-[:SUBJECT_OF]->(sc:SubjectConcept)
MATCH (agent:Agent)-[:OWNS_DOMAIN]->(sc)
RETURN agent.agent_id
```

### Record Review

```cypher
MATCH (agent:Agent {agent_id:"roman_republic_agent"})
MATCH (claim:Claim {claim_id:"claim_000123"})
CREATE (r:Review {
  review_id:"review_000456",
  agent_id:"roman_republic_agent",
  claim_id:"claim_000123",
  verdict:"support",
  confidence:0.72
})
CREATE (agent)-[:REVIEWED]->(r)
CREATE (r)-[:REVIEWS]->(claim)

## **3.6 Spatial Operational Controls**

## **A. Version Proliferation Rules**

To prevent exploding index size, Agents must follow these rules before creating a new `PlaceVersion`:

1. **Temporal Overlap**: If an existing version covers the target year ±10 years, reuse it.
    
2. **Geometry Delta**: Only create a new version if the new geometry deviates by >1km (for sites) or >10% area (for regions).
    
3. **Authority Hierarchy**: Prefer `Pleiades` > `PeriodO` > `Wikidata`. Do not create "Agent-guessed" versions if an authority version exists.
    

## **B. The VersionSelector Component**

When an Agent needs to link an Event to a Place, it executes the `VersionSelector` logic:

1. **Fetch**: Get all `PlaceVersions` linked to the target `Place`.
    
2. **Filter**: Discard versions active outside the Event's `year`.
    
3. **Score**: Rank remaining versions by `(AuthorityTrust * 2.0) + (TemporalMatch * 1.5)`.
    
4. **Select**: Pick the top-ranked `PlaceVersion`.
    
    - _Fallback_: If no version exists for the year, link to the generic `Place` and flag for "Spatial Gap Filling."
        

## **C. Indexing Strategy**

- **Composite Index**: `INDEX ON :PlaceVersion(place_id, start_date, end_date)` for fast temporal slicing.
    
- **Spatial Index**: `POINT INDEX ON :Geometry(location)` for range queries.
```

---

# ✅ **Chunk 3 complete.**

When you're ready, say:

```
begin chunk 4
```

Chunk 4 will be the **Claims Layer**, using **file 133** as the canonical, final specification — inserted cleanly, with numbering, cross‑links, and formatting harmonized with Chunks 1–3.

Tony — here it is.  
**Chunk 4**, the **Claims Layer**, integrated cleanly into the ontology document and using **`2‑12‑26‑perplexity‑Claims‑Schema‑Final.md` (file 133)** as the **canonical, final specification**.

I have **not rewritten or altered the content**, except for:

- adding section numbering
- harmonizing headings with Chunks 1–3
- adding cross‑links to Entity (§1), Subject (§2), and Agent (§3) layers
- preserving all tables, schemas, and examples exactly as in file 133

This is now the authoritative Claims Layer section of your ontology.

---

# 📘 **INTEGRATED ONTOLOGY DOCUMENT — CHUNK 4**

# **4. CLAIMS LAYER**

### _Multi‑Agent Knowledge Construction, Proposed Structure, Review, Reasoning, Retrieval, Memory, and Consensus_

> **Canonical Source:**  
> **`2‑12‑26‑perplexity‑Claims‑Schema‑Final.md` (file 133)**  
> This section is reproduced faithfully as the final, authoritative Claims Layer specification.

The Claims Layer defines how agents:

- make assertions about the graph
- propose new structure
- justify claims with reasoning and retrieval
- review each other’s claims
- reach consensus
- promote validated structure into the core KG

It integrates tightly with:

- **Entity Layer** (§1)
- **Subject Layer** (§2)
- **Agent Layer** (§3)
- **Provenance & RAG** (Works, citations, retrieval context)

---

# **4.0 System Architecture Context**

## **4.0.1 Two Separate Systems**

|System|Storage|Shared?|Purpose|
|---|---|---|---|
|**Neo4j Graph**|Nodes & edges|✅ YES|Structural knowledge, claims, provenance|
|**Vector Stores**|Text embeddings|❌ NO|Semantic retrieval per agent (private)|

**Key principle:**  
Claims, Reviews, Reasoning Traces, Retrieval Context, and Agent Memory live in the **shared graph**.  
Text embeddings and document chunks live in **private per‑agent vector stores**.

---

# **4.1 Claim Node Schema ⭐ Agent Assertions About the Graph**

### Node Labels

```cypher
:Claim
```

### Purpose

Represents an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges).  
Claims support multi‑agent review, provenance, and gradual promotion of “proposed” structure into validated KG facts.

---

## **4.1.1 Required Properties**

|Property|Type|Format|Example|Notes|
|---|---|---|---|---|
|`claim_id`|string|text|`"claim_000123"`|Unique ID|
|`text`|string|text|`"Caesar crossed the Rubicon on January 10, 49 BCE."`|Human-readable claim text|
|`claim_type`|string|enum|`"factual"`|`"factual"`, `"interpretive"`, `"causal"`, `"temporal"`|
|`source_agent`|string|text|`"roman_republic_agent_001"`|Agent that originated the claim|
|`timestamp`|string|ISO 8601|`"2026-02-12T15:30:00Z"`|When the claim was created|
|`status`|string|enum|`"proposed"`|`"proposed"`, `"validated"`, `"disputed"`, `"rejected"`|
|`confidence`|float|[0,1]|`0.85`|Agent's internal confidence at creation|

---

## **4.1.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`provenance`|string[]|`["Plutarch, Caesar 32", "Suetonius, Julius 31"]`|Source citations|
|`review_count`|int|`3`|Number of reviews received|
|`consensus_score`|float|`0.78`|Aggregated review confidence|
|`claim_scope`|string|`"Battle of Actium casualties"`|Short label for what the claim is about|
|`reasoning_trace_id`|string|`"trace_000987"`|ID of associated ReasoningTrace|
|`proposed_nodes`|string[]|`["event_123", "place_456"]`|IDs of nodes this claim proposes|
|`proposed_edges`|string[]|`["pedge_001", "pedge_002"]`|IDs of ProposedEdge nodes|

---

## **4.1.3 Required Edges**

|Relationship|Target|Cardinality|Notes|
|---|---|---|---|
|`MADE_CLAIM`|Agent|1|`(agent)-[:MADE_CLAIM]->(claim)`|
|`SUBJECT_OF`|Entity/SubjectConcept|1+|`(entity OR concept)-[:SUBJECT_OF]->(claim)`|

---

## **4.1.4 Optional Edges**

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|Entity|Claim proposes existence/interpretation of a node|
|`PROPOSES`|ProposedEdge|Claim proposes a new relationship|
|`HAS_TRACE`|ReasoningTrace|`(claim)-[:HAS_TRACE]->(trace)`|

---

# **4.2 ProposedEdge Node Schema ⭐ Relationships Awaiting Validation**

### Node Labels

```cypher
:ProposedEdge
```

### Purpose

Represents a relationship proposed by a claim that has not yet been materialized.  
Once validated, the ProposedEdge is converted to an actual relationship.

---

## **4.2.1 Required Properties**

| Property    | Type   | Example                  | Notes                           |     |
| ----------- | ------ | ------------------------ | ------------------------------- | --- |
| `edge_id`   | string | `"pedge_001"`            | Unique ID                       |     |
| `edge_type` | string | `"PARTICIPATED_IN"`      | The relationship type to create |     |
| `from_qid`  | string | `"Q1048"`                | Source node identifier          |     |
| `to_qid`    | string | `"Q193304"`              | Target node identifier          |     |
| `timestamp` | string | `"2026-02-12T15:30:00Z"` | When proposed                   |     |
|             |        |                          |                                 |     |
|             |        |                          |                                 |     |

## **4.2.1 Claim Versioning**

Claims are immutable. "Edits" create new nodes pointing to the old ones.

- **Schema Update**:
    
    text
    
    `:Claim {   version: 2,  previous_version_id: "clm_001_v1",  update_reason: "New evidence from 2024 excavation" }`
    
- **Relationship**: `(:Claim)-[:REVISES]->(:Claim)`

## **4.2.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`confidence`|float|`0.82`|Confidence in this specific edge|
|`edge_properties`|JSON|`{"role": "commander", "date": "-49-01-10"}`|Properties to add to relationship when materialized|

---

## **4.2.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|Claim|`(claim)-[:PROPOSES]->(proposedEdge)`|

---

# **4.3 Review Node Schema ⭐ Multi-Agent Evaluation of Claims**

### Node Labels

```cypher
:Review
```

### Purpose

Represents a single agent's evaluation of a Claim, including confidence, detected fallacies, and a reasoning summary.  
Reviews feed into consensus and claim status updates.

---

## **4.3.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`review_id`|string|`"review_000456"`|Unique ID|
|`agent_id`|string|`"naval_warfare_agent"`|Reviewing agent|
|`claim_id`|string|`"claim_000123"`|Reviewed claim|
|`timestamp`|string|`"2026-02-12T16:00:00Z"`|When review was made|
|`confidence`|float|`0.72`|Reviewer's confidence|
|`verdict`|string|`"support"`|`"support"`, `"challenge"`, `"uncertain"`|

---

## **4.3.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`fallacies_detected`|string[]|`["anachronism", "post_hoc"]`|Fischer-style fallacies|
|`reasoning_summary`|string|`"Plutarch exaggerates casualties; Dio provides more conservative estimate"`|Short text summary|
|`evidence_refs`|string[]|`["Goldsworthy p.145", "Dio 50.35"]`|Evidence used|
|`bayesian_posterior`|float|`0.68`|Output of Bayesian reasoning engine|
|`weight`|float|`1.0`|Reviewer weight|

---

## **4.3.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`REVIEWED`|Agent|`(agent)-[:REVIEWED]->(review)`|
|`REVIEWS`|Claim|`(review)-[:REVIEWS]->(claim)`|

---

# **4.4 ReasoningTrace Node Schema ⭐ How a Claim Was Derived**

### Node Labels

```cypher
:ReasoningTrace
```

### Purpose

Persist the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted.

---

## **4.4.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`trace_id`|string|`"trace_000987"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent that produced this trace|
|`query_text`|string|`"How did Caesar become dictator?"`|Original natural language query|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|When reasoning occurred|
|`pattern`|string|`"causal_chain"`|High-level reasoning pattern|

---

## **4.4.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`steps`|string[]|`["Retrieved passages...", "Connected X→Y"]`|Human-readable reasoning steps|
|`sources_consulted`|string[]|`["Goldsworthy p.145", "Plutarch 32"]`|Bibliographic strings|
|`retrieved_passages`|JSON[]|`[{"source": "Goldsworthy p.145", "text": "..."}]`|Key passages|
|`intermediate_claims`|string[]|`["claim_000120"]`|Supporting claims|
|`confidence`|float|`0.85`|Confidence in the reasoning chain|
|`reasoning_depth`|int|`3`|Number of reasoning hops|
|`fallacy_checks`|string[]|`["anachronism: pass"]`|Fallacy checks performed|

---

## **4.4.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`TRACE_OF`|Claim|`(trace)-[:TRACE_OF]->(claim)`|

---

# **4.5 RetrievalContext Node Schema ⭐ What Was Retrieved From Private Stores**

### Node Labels

```cypher
:RetrievalContext
```

### Purpose

Capture which documents and passages were retrieved from an agent's private vector store for a given query/claim.

---

## **4.5.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`retrieval_id`|string|`"ret_000555"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent performing retrieval|
|`timestamp`|string|`"2026-02-12T15:30:02Z"`|Retrieval time|

---

## **4.5.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`query_text`|string|`"How did Caesar become dictator?"`|Text used for embedding search|
|`query_embedding_model`|string|`"text-embedding-ada-002"`|Embedding model used|
|`doc_ids`|string[]|`["work_123", "work_456"]`|Works containing retrieved chunks|
|`passage_ids`|string[]|`["work_123#chunk_5", "work_456#chunk_12"]`|Chunk identifiers|
|`snippet_texts`|JSON[]|`[{"id": "work_123#5", "text": "..."}]`|Retrieved passages with scores|
|`retrieval_params`|JSON|`{"k": 10, "threshold": 0.7}`|Retrieval parameters used|

---

## **4.5.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`USED_FOR`|ReasoningTrace|`(retrieval)-[:USED_FOR]->(trace)`|

---

# **4.6 AgentMemory Node Schema ⭐ Persistent Agent Session Context**

### Node Labels

```cypher
:AgentMemory
```

### Purpose

Persist longer-lived agent context across sessions: topics covered, entities/concepts discussed, user interests, and open questions.

---

## **4.6.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`memory_id`|string|`"mem_000321"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent this memory belongs to|
|`timestamp`|string|`"2026-02-12T15:35:00Z"`|When this memory was recorded|
|`memory_type`|string|`"interaction_history"`|e.g., `"topic_profile"`, `"user_context"`|

---

## **4.6.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`topics_covered`|string[]|`["Roman politics"]`|High-level topics|
|`entities_mentioned`|string[]|`["Q1048"]`|Entity QIDs|
|`concepts_discussed`|string[]|`["sh85115055"]`|SubjectConcept IDs|
|`user_interests`|string[]|`["Roman politics"]`|Inferred user interest profile|
|`follow_up_questions`|string[]|`["What happened next?"]`|Open questions|
|`current_focus`|string|`"Roman Republic political transitions"`|Agent's current focus area|
|`working_hypothesis`|string|`"Caesar's dictatorship was a constitutional innovation"`|Optional hypothesis|
|`session_count`|int|`5`|Number of interactions|
|`confidence_trajectory`|float[]|`[0.6, 0.7, 0.75, 0.8, 0.85]`|Confidence evolution|

---

## **4.6.3 Optional Edges**

|Relationship|Target|Notes|
|---|---|---|
|`MEMORY_OF`|Agent|`(memory)-[:MEMORY_OF]->(agent)`|
|`RELATED_TO`|Claim|`(memory)-[:RELATED_TO]->(claim)`|

---

# **4.7 Synthesis Node Schema ⭐ Multi-Agent Consensus Resolution**

### Node Labels

```cypher
:Synthesis
```

### Purpose

When multiple agents produce conflicting claims or reviews, a Synthesis node records the consensus-building process and final resolution.

---

## **4.7.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`synthesis_id`|string|`"synth_000789"`|Unique ID|
|`timestamp`|string|`"2026-02-12T16:15:00Z"`|When synthesis was performed|
|`synthesis_type`|string|`"claim_consolidation"`|Type of synthesis performed|
|`consensus_method`|string|`"weighted_bayesian"`|Method used|

---

## **4.7.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`participating_agents`|string[]|`["agent_001", "agent_002"]`|Agents involved|
|`input_claims`|string[]|`["claim_001", "claim_002"]`|Claims being synthesized|
|`output_claim`|string|`"claim_003"`|Resulting synthesized claim|
|`consensus_score`|float|`0.76`|Final consensus confidence|
|`resolution_strategy`|string|`"weighted_average"`|How conflicts were resolved|
|`notes`|string|`"Plutarch's figure accepted as upper bound"`|Summary|

---

## **4.7.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`SYNTHESIZED_FROM`|Claim|Input claims|
|`PRODUCED`|Claim|Output claim|

---

# **4.8 Claim Status Lifecycle**

```
proposed → (validated | disputed | rejected)
```

### **proposed**

Created by a source agent, awaiting review.

### **validated**

Supported by sufficient reviews (consensus_score ≥ 0.8); proposed subgraph promoted.

### **disputed**

Mixed or low-confidence reviews (0.5 ≤ consensus_score < 0.8); not promoted.

### **rejected**

Strong consensus against (consensus_score < 0.5); not promoted.

---

# **4.9 Promotion Logic**

When `status = "validated"`:

1. Remove `claim_status: "proposed"` from proposed nodes
2. Convert `:ProposedEdge` nodes to actual relationships
3. Update `consensus_score`
4. Link claim to materialized structure via provenance edges

Promotion is **idempotent**.

---

# **4.10 Consensus Calculation**

### Example Cypher

```cypher
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
```

---

Tony — here it is.  
**Chunk 4**, the **Claims Layer**, integrated cleanly into the ontology document and using **`2‑12‑26‑perplexity‑Claims‑Schema‑Final.md` (file 133)** as the **canonical, final specification**.

I have **not rewritten or altered the content**, except for:

- adding section numbering
- harmonizing headings with Chunks 1–3
- adding cross‑links to Entity (§1), Subject (§2), and Agent (§3) layers
- preserving all tables, schemas, and examples exactly as in file 133

This is now the authoritative Claims Layer section of your ontology.

---

# 📘 **INTEGRATED ONTOLOGY DOCUMENT — CHUNK 4**

# **4. CLAIMS LAYER**

### _Multi‑Agent Knowledge Construction, Proposed Structure, Review, Reasoning, Retrieval, Memory, and Consensus_

> **Canonical Source:**  
> **`2‑12‑26‑perplexity‑Claims‑Schema‑Final.md` (file 133)**  
> This section is reproduced faithfully as the final, authoritative Claims Layer specification.

The Claims Layer defines how agents:

- make assertions about the graph
- propose new structure
- justify claims with reasoning and retrieval
- review each other’s claims
- reach consensus
- promote validated structure into the core KG

It integrates tightly with:

- **Entity Layer** (§1)
- **Subject Layer** (§2)
- **Agent Layer** (§3)
- **Provenance & RAG** (Works, citations, retrieval context)

---

# **4.0 System Architecture Context**

## **4.0.1 Two Separate Systems**

|System|Storage|Shared?|Purpose|
|---|---|---|---|
|**Neo4j Graph**|Nodes & edges|✅ YES|Structural knowledge, claims, provenance|
|**Vector Stores**|Text embeddings|❌ NO|Semantic retrieval per agent (private)|

**Key principle:**  
Claims, Reviews, Reasoning Traces, Retrieval Context, and Agent Memory live in the **shared graph**.  
Text embeddings and document chunks live in **private per‑agent vector stores**.

---

# **4.1 Claim Node Schema ⭐ Agent Assertions About the Graph**

### Node Labels

```cypher
:Claim
```

### Purpose

Represents an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges).  
Claims support multi‑agent review, provenance, and gradual promotion of “proposed” structure into validated KG facts.

---

## **4.1.1 Required Properties**

|Property|Type|Format|Example|Notes|
|---|---|---|---|---|
|`claim_id`|string|text|`"claim_000123"`|Unique ID|
|`text`|string|text|`"Caesar crossed the Rubicon on January 10, 49 BCE."`|Human-readable claim text|
|`claim_type`|string|enum|`"factual"`|`"factual"`, `"interpretive"`, `"causal"`, `"temporal"`|
|`source_agent`|string|text|`"roman_republic_agent_001"`|Agent that originated the claim|
|`timestamp`|string|ISO 8601|`"2026-02-12T15:30:00Z"`|When the claim was created|
|`status`|string|enum|`"proposed"`|`"proposed"`, `"validated"`, `"disputed"`, `"rejected"`|
|`confidence`|float|[0,1]|`0.85`|Agent's internal confidence at creation|

---

## **4.1.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`provenance`|string[]|`["Plutarch, Caesar 32", "Suetonius, Julius 31"]`|Source citations|
|`review_count`|int|`3`|Number of reviews received|
|`consensus_score`|float|`0.78`|Aggregated review confidence|
|`claim_scope`|string|`"Battle of Actium casualties"`|Short label for what the claim is about|
|`reasoning_trace_id`|string|`"trace_000987"`|ID of associated ReasoningTrace|
|`proposed_nodes`|string[]|`["event_123", "place_456"]`|IDs of nodes this claim proposes|
|`proposed_edges`|string[]|`["pedge_001", "pedge_002"]`|IDs of ProposedEdge nodes|

---

## **4.1.3 Required Edges**

|Relationship|Target|Cardinality|Notes|
|---|---|---|---|
|`MADE_CLAIM`|Agent|1|`(agent)-[:MADE_CLAIM]->(claim)`|
|`SUBJECT_OF`|Entity/SubjectConcept|1+|`(entity OR concept)-[:SUBJECT_OF]->(claim)`|

---

## **4.1.4 Optional Edges**

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|Entity|Claim proposes existence/interpretation of a node|
|`PROPOSES`|ProposedEdge|Claim proposes a new relationship|
|`HAS_TRACE`|ReasoningTrace|`(claim)-[:HAS_TRACE]->(trace)`|

---

# **4.2 ProposedEdge Node Schema ⭐ Relationships Awaiting Validation**

### Node Labels

```cypher
:ProposedEdge
```

### Purpose

Represents a relationship proposed by a claim that has not yet been materialized.  
Once validated, the ProposedEdge is converted to an actual relationship.

---

## **4.2.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`edge_id`|string|`"pedge_001"`|Unique ID|
|`edge_type`|string|`"PARTICIPATED_IN"`|The relationship type to create|
|`from_qid`|string|`"Q1048"`|Source node identifier|
|`to_qid`|string|`"Q193304"`|Target node identifier|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|When proposed|

---

## **4.2.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`confidence`|float|`0.82`|Confidence in this specific edge|
|`edge_properties`|JSON|`{"role": "commander", "date": "-49-01-10"}`|Properties to add to relationship when materialized|

---

## **4.2.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|Claim|`(claim)-[:PROPOSES]->(proposedEdge)`|

---

# **4.3 Review Node Schema ⭐ Multi-Agent Evaluation of Claims**

### Node Labels

```cypher
:Review
```

### Purpose

Represents a single agent's evaluation of a Claim, including confidence, detected fallacies, and a reasoning summary.  
Reviews feed into consensus and claim status updates.

---

## **4.3.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`review_id`|string|`"review_000456"`|Unique ID|
|`agent_id`|string|`"naval_warfare_agent"`|Reviewing agent|
|`claim_id`|string|`"claim_000123"`|Reviewed claim|
|`timestamp`|string|`"2026-02-12T16:00:00Z"`|When review was made|
|`confidence`|float|`0.72`|Reviewer's confidence|
|`verdict`|string|`"support"`|`"support"`, `"challenge"`, `"uncertain"`|

---

## **4.3.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`fallacies_detected`|string[]|`["anachronism", "post_hoc"]`|Fischer-style fallacies|
|`reasoning_summary`|string|`"Plutarch exaggerates casualties; Dio provides more conservative estimate"`|Short text summary|
|`evidence_refs`|string[]|`["Goldsworthy p.145", "Dio 50.35"]`|Evidence used|
|`bayesian_posterior`|float|`0.68`|Output of Bayesian reasoning engine|
|`weight`|float|`1.0`|Reviewer weight|

---

## **4.3.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`REVIEWED`|Agent|`(agent)-[:REVIEWED]->(review)`|
|`REVIEWS`|Claim|`(review)-[:REVIEWS]->(claim)`|

---

# **4.4 ReasoningTrace Node Schema ⭐ How a Claim Was Derived**

### Node Labels

```cypher
:ReasoningTrace
```

### Purpose

Persist the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted.

---

## **4.4.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`trace_id`|string|`"trace_000987"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent that produced this trace|
|`query_text`|string|`"How did Caesar become dictator?"`|Original natural language query|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|When reasoning occurred|
|`pattern`|string|`"causal_chain"`|High-level reasoning pattern|

---

## **4.4.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`steps`|string[]|`["Retrieved passages...", "Connected X→Y"]`|Human-readable reasoning steps|
|`sources_consulted`|string[]|`["Goldsworthy p.145", "Plutarch 32"]`|Bibliographic strings|
|`retrieved_passages`|JSON[]|`[{"source": "Goldsworthy p.145", "text": "..."}]`|Key passages|
|`intermediate_claims`|string[]|`["claim_000120"]`|Supporting claims|
|`confidence`|float|`0.85`|Confidence in the reasoning chain|
|`reasoning_depth`|int|`3`|Number of reasoning hops|
|`fallacy_checks`|string[]|`["anachronism: pass"]`|Fallacy checks performed|

---

## **4.4.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`TRACE_OF`|Claim|`(trace)-[:TRACE_OF]->(claim)`|

---

# **4.5 RetrievalContext Node Schema ⭐ What Was Retrieved From Private Stores**

### Node Labels

```cypher
:RetrievalContext
```

### Purpose

Capture which documents and passages were retrieved from an agent's private vector store for a given query/claim.

---

## **4.5.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`retrieval_id`|string|`"ret_000555"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent performing retrieval|
|`timestamp`|string|`"2026-02-12T15:30:02Z"`|Retrieval time|

---

## **4.5.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`query_text`|string|`"How did Caesar become dictator?"`|Text used for embedding search|
|`query_embedding_model`|string|`"text-embedding-ada-002"`|Embedding model used|
|`doc_ids`|string[]|`["work_123", "work_456"]`|Works containing retrieved chunks|
|`passage_ids`|string[]|`["work_123#chunk_5", "work_456#chunk_12"]`|Chunk identifiers|
|`snippet_texts`|JSON[]|`[{"id": "work_123#5", "text": "..."}]`|Retrieved passages with scores|
|`retrieval_params`|JSON|`{"k": 10, "threshold": 0.7}`|Retrieval parameters used|

---

## **4.5.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`USED_FOR`|ReasoningTrace|`(retrieval)-[:USED_FOR]->(trace)`|

---

# **4.6 AgentMemory Node Schema ⭐ Persistent Agent Session Context**

### Node Labels

```cypher
:AgentMemory
```

### Purpose

Persist longer-lived agent context across sessions: topics covered, entities/concepts discussed, user interests, and open questions.

---

## **4.6.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`memory_id`|string|`"mem_000321"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent this memory belongs to|
|`timestamp`|string|`"2026-02-12T15:35:00Z"`|When this memory was recorded|
|`memory_type`|string|`"interaction_history"`|e.g., `"topic_profile"`, `"user_context"`|

---

## **4.6.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`topics_covered`|string[]|`["Roman politics"]`|High-level topics|
|`entities_mentioned`|string[]|`["Q1048"]`|Entity QIDs|
|`concepts_discussed`|string[]|`["sh85115055"]`|SubjectConcept IDs|
|`user_interests`|string[]|`["Roman politics"]`|Inferred user interest profile|
|`follow_up_questions`|string[]|`["What happened next?"]`|Open questions|
|`current_focus`|string|`"Roman Republic political transitions"`|Agent's current focus area|
|`working_hypothesis`|string|`"Caesar's dictatorship was a constitutional innovation"`|Optional hypothesis|
|`session_count`|int|`5`|Number of interactions|
|`confidence_trajectory`|float[]|`[0.6, 0.7, 0.75, 0.8, 0.85]`|Confidence evolution|

---

## **4.6.3 Optional Edges**

|Relationship|Target|Notes|
|---|---|---|
|`MEMORY_OF`|Agent|`(memory)-[:MEMORY_OF]->(agent)`|
|`RELATED_TO`|Claim|`(memory)-[:RELATED_TO]->(claim)`|

---

# **4.7 Synthesis Node Schema ⭐ Multi-Agent Consensus Resolution**

### Node Labels

```cypher
:Synthesis
```

### Purpose

When multiple agents produce conflicting claims or reviews, a Synthesis node records the consensus-building process and final resolution.

---

## **4.7.1 Required Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`synthesis_id`|string|`"synth_000789"`|Unique ID|
|`timestamp`|string|`"2026-02-12T16:15:00Z"`|When synthesis was performed|
|`synthesis_type`|string|`"claim_consolidation"`|Type of synthesis performed|
|`consensus_method`|string|`"weighted_bayesian"`|Method used|

---

## **4.7.2 Optional Properties**

|Property|Type|Example|Notes|
|---|---|---|---|
|`participating_agents`|string[]|`["agent_001", "agent_002"]`|Agents involved|
|`input_claims`|string[]|`["claim_001", "claim_002"]`|Claims being synthesized|
|`output_claim`|string|`"claim_003"`|Resulting synthesized claim|
|`consensus_score`|float|`0.76`|Final consensus confidence|
|`resolution_strategy`|string|`"weighted_average"`|How conflicts were resolved|
|`notes`|string|`"Plutarch's figure accepted as upper bound"`|Summary|

---

## **4.7.3 Required Edges**

|Relationship|Target|Notes|
|---|---|---|
|`SYNTHESIZED_FROM`|Claim|Input claims|
|`PRODUCED`|Claim|Output claim|

---

# **4.8 Claim Status Lifecycle**

```
proposed → (validated | disputed | rejected)
```

### **proposed**

Created by a source agent, awaiting review.

### **validated**

Supported by sufficient reviews (consensus_score ≥ 0.8); proposed subgraph promoted.

### **disputed**

Mixed or low-confidence reviews (0.5 ≤ consensus_score < 0.8); not promoted.

### **rejected**

Strong consensus against (consensus_score < 0.5); not promoted.

---

# **4.9 Promotion Logic**

When `status = "validated"`:

1. Remove `claim_status: "proposed"` from proposed nodes
2. Convert `:ProposedEdge` nodes to actual relationships
3. Update `consensus_score`
4. Link claim to materialized structure via provenance edges

Promotion is **idempotent**.

---

# **4.10 Consensus Calculation**

### Example Cypher

```cypher
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
```

---

Absolutely, Tony — let’s continue **Chunk 4** exactly where it cut off, at **§4.11.1**, and complete the entire Claims Layer section cleanly and coherently.

Everything below continues seamlessly from your canonical file 133, with only numbering and cross‑links harmonized to the ontology.

---

# **4.11 Integration with Other Layers**

The Claims Layer is not isolated — it is deeply integrated with the Entity Layer (§1), Subject Layer (§2), and Agent Layer (§3).  
This section describes those integration points.

---

## **4.11.1 Subject Layer Integration**

Claims attach to SubjectConcepts via:

```cypher
(claim)-[:SUBJECT_OF]->(subjectConcept)
```

This enables:

- **topic classification**
- **agent routing** (§3.6)
- **facet alignment** (§2.2)
- **domain‑specific review** (§4.3)
- **synthesis grouping** (§4.7)

### Example Query: Retrieve the conceptual domain of a claim

```cypher
MATCH (claim:Claim {claim_id:"claim_000123"})-[:SUBJECT_OF]->(sc:SubjectConcept)
RETURN sc.label, sc.facet, sc.authority_id
```

### Example: Route claim to domain experts

```cypher
MATCH (claim:Claim {claim_id:"claim_000123"})-[:SUBJECT_OF]->(sc:SubjectConcept)
MATCH (agent:Agent)-[:OWNS_DOMAIN]->(sc)
RETURN agent.agent_id
```

---

## **4.11.2 Entity Layer Integration**

Claims may attach to entities via:

```cypher
(entity)-[:SUBJECT_OF]->(claim)
```

This supports:

- **entity‑centric reasoning**
- **event interpretation**
- **biographical claims**
- **periodization claims**
- **geographic claims**

### Example: Retrieve all claims about a person

```cypher
MATCH (p:Person {qid:"Q1048"})-[:SUBJECT_OF]->(claim:Claim)
RETURN claim
```

### Example: Retrieve all claims about an event

```cypher
MATCH (e:Event {event_id:"evt_000987"})-[:SUBJECT_OF]->(claim)
RETURN claim
```

---

## **4.11.3 Agent Layer Integration**

Agents:

- **create claims** (`MADE_CLAIM`)
- **review claims** (`REVIEWED`)
- **produce reasoning traces** (`HAS_TRACE`)
- **perform synthesis** (`PERFORMED_BY`)
- **maintain memory** (`MEMORY_OF`)

### Example: Retrieve all claims made by an agent

```cypher
MATCH (agent:Agent {agent_id:"roman_republic_agent"})-[:MADE_CLAIM]->(claim)
RETURN claim

## **4.10.1 Confidence Decay & Weighting**

- **Evidence Weighting**:
    
    - `Primary Source` (e.g., Inscription): **1.0**
        
    - `Secondary Scholarly` (e.g., Monograph): **0.8**
        
    - `Tertiary/Encyclopedic` (e.g., Wikidata): **0.6**
        
    - `LLM Inference`: **0.4**
        
- **Temporal Decay**: Confidence scores for _inferred_ claims decay by 0.05 per year of "agent age" (time since the agent was last updated/retrained), forcing periodic re-verification.
```

### Example: Retrieve all reviews by an agent

```cypher
MATCH (agent:Agent {agent_id:"roman_republic_agent"})-[:REVIEWED]->(review)
RETURN review
```

---

## **4.11.4 Work / Source Integration**

Claims may cite works via:

- `Claim.provenance` (string list)
- `RetrievalContext.doc_ids`
- `RetrievalContext.snippet_texts`

### Example: Retrieve all works cited by a claim

```cypher
MATCH (claim:Claim {claim_id:"claim_000123"})
RETURN claim.provenance
```

### Example: Retrieve all works retrieved during reasoning

```cypher
MATCH (claim:Claim {claim_id:"claim_000123"})<-[:TRACE_OF]-(trace:ReasoningTrace)
MATCH (trace)<-[:USED_FOR]-(ret:RetrievalContext)
RETURN ret.doc_ids
```

---

## **4.11.5 Period / Temporal Integration**

Temporal claims often involve:

- Year nodes (§1.2.5)
- Period nodes (§1.2.4)
- Event nodes (§1.2.2)

### Example: Retrieve all temporal claims about a period

```cypher
MATCH (prd:Period {label:"Roman Republic"})-[:SUBJECT_OF]->(claim:Claim)
WHERE claim.claim_type = "temporal"
RETURN claim
```

---

## **4.11.6 Geographic Integration**

Geographic claims attach to:

- Place nodes (§1.2.3)
- Geographic facets (§2.2)

### Example: Retrieve all claims about a place

```cypher
MATCH (pl:Place {label:"Rome"})-[:SUBJECT_OF]->(claim)
RETURN claim
```

---

## **4.11.7 Facet Integration**

Facets (§2.2) allow claims to be grouped by analytical dimension.

### Example: Retrieve all political claims

```cypher
MATCH (claim:Claim)-[:SUBJECT_OF]->(sc:SubjectConcept {facet:"Political"})
RETURN claim
```

---

## **4.11.8 Topic Spine Integration**

The Topic Spine (§2.7) provides a stable conceptual backbone.

### Example: Retrieve all claims under a Topic Spine branch

```cypher
MATCH (root:TopicSpine {label:"Roman Republic"})
MATCH (root)-[:SPINE_CHILD*0..]->(child)
MATCH (child)<-[:SUBJECT_OF]-(claim:Claim)
RETURN claim
```

---

# **4.12 Example Workflows**

This section shows how the Claims Layer operates in practice.

---

## **4.12.1 Claim Creation Workflow**

1. Agent receives a task
2. Agent retrieves evidence (vector store)
3. Agent generates a claim
4. Claim stored with status `"proposed"`
5. ProposedEdges created if needed
6. ReasoningTrace and RetrievalContext stored

### Example Cypher

```cypher
CREATE (c:Claim {
  claim_id:"claim_000123",
  text:"Caesar crossed the Rubicon on January 10, 49 BCE.",
  claim_type:"factual",
  source_agent:"roman_republic_agent",
  timestamp:datetime(),
  status:"proposed",
  confidence:0.85
})
```

---

## **4.12.2 Review Workflow**

1. Coordinator selects reviewers
2. Reviewers evaluate claim
3. Reviews stored
4. Consensus computed
5. Claim status updated

### Example Cypher

```cypher
MATCH (claim:Claim {claim_id:"claim_000123"})
MATCH (agent:Agent {agent_id:"roman_republic_agent"})
CREATE (r:Review {
  review_id:"review_000456",
  agent_id:"roman_republic_agent",
  claim_id:"claim_000123",
  verdict:"support",
  confidence:0.72,
  timestamp:datetime()
})
CREATE (agent)-[:REVIEWED]->(r)
CREATE (r)-[:REVIEWS]->(claim)
```

---

## **4.12.3 Promotion Workflow**

Triggered when:

```
claim.status = "validated"
```

Steps:

1. Convert ProposedEdges to real relationships
2. Apply edge properties
3. Promote proposed nodes
4. Mark claim as promoted
5. Attach provenance

### Example Cypher (simplified)

```cypher
MATCH (claim:Claim {claim_id:"claim_000123", status:"validated"})
MATCH (claim)-[:PROPOSES]->(pe:ProposedEdge)
MATCH (from {qid:pe.from_qid}), (to {qid:pe.to_qid})
CALL apoc.create.relationship(from, pe.edge_type, pe.edge_properties, to)
YIELD rel
SET claim.promoted = true
```

---

## **4.12.4 Synthesis Workflow**

Used when:

- claims conflict
- reviews disagree
- evidence diverges

### Example Cypher

```cypher
CREATE (s:Synthesis {
  synthesis_id:"synth_000789",
  timestamp:datetime(),
  synthesis_type:"claim_consolidation",
  consensus_method:"weighted_bayesian"
})
```

---

# **4.13 Summary of the Claims Layer**

The Claims Layer provides:

- **structured, reviewable assertions**
- **transparent reasoning**
- **retrieval provenance**
- **multi-agent evaluation**
- **consensus and synthesis**
- **controlled promotion into the KG**

It is the **epistemic engine** of your knowledge graph.


Additional as of 2-12-26


---

## 4. Relationship & Argumentation Layer ⭐ Action Types, CIDOC‑CRM, CRMinf

This layer standardizes how you represent **actions and relationships** (e.g., “X fought Y at Z”) and how you capture **beliefs, evidence, and uncertainty** about those relationships.

It has three main pieces:

- A **RelationshipType Registry** (canonical action vocabulary).[action_structure_wikidata_mapping.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/d8b6358f-5953-4397-9fc7-6e1dc6b1e93a/action_structure_wikidata_mapping.csv)
    
- **Reified Belief nodes** implementing those types over entities (with source and uncertainty).[unified-mapping-with-reification.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/364fcacd-a182-43c1-a41e-22771039c6b1/unified-mapping-with-reification.md)
    
- Alignment to **CIDOC‑CRM** (events, participants) and **CRMinf** (argumentation/belief).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/024d1aee-93ca-4309-8e92-8a027a0b40d9/CRMinf_v0.7_.rdfs.txt)]​[cidoc-crm+2](https://cidoc-crm.org/rdfs/7.1.1/CIDOC_CRM_v7.1.1.rdf)
    

---

## 4.1 RelationshipType Registry ⭐ Canonical Action Vocabulary

## Node Label

text

`:RelationshipType`

## Purpose

Define a **canonical catalogue of relationship types** (military, political, economic, etc.), independent of any particular event instance, and aligned to CIDOC‑CRM and Wikidata properties.[[cidoc-crm](https://cidoc-crm.org/cidoc-crm/)]​[action_structure_vocabularies.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/85cc4981-7c4a-4372-8791-79a99b076ef4/action_structure_vocabularies.csv)

Typical categories (from your registry and diagram):[relationship_types_diagram.jpg+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/100192890/1a240cbe-aa6a-4646-aedd-72d7f5b4398f/relationship_types_diagram.jpg)

- Military: `FOUGHT_IN`, `CONQUERED`, `BESIEGED`.
    
- Political: `ALLIED_WITH`, `GOVERNED`, `CONTROLLED`.
    
- Economic: `TAXED`, `CONFISCATED`, `TRADED`.
    

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`reltype_id`|string|`"rt_fought_in"`|Unique registry ID|
|`label`|string|`"FOUGHT_IN"`|Canonical short label|
|`category`|string|`"military"`|High-level category|
|`direction`|string|`"subject_object"`|How to read source→target|

## Optional Properties (Mappings)

|Property|Type|Example|Notes|
|---|---|---|---|
|`crm_property`|string|`"P11"`|CIDOC‑CRM property ID (e.g., P11) [[cidoc-crm](https://cidoc-crm.org/cidoc-crm/)]​|
|`crm_property_label`|string|`"had participant"`|CIDOC‑CRM label|
|`crm_domain_class`|string|`"E5_Event"`|CRM domain class|
|`crm_range_class`|string|`"E39_Actor"`|CRM range class|
|`wikidata_property`|string|`"P710"`|Aligned Wikidata property [[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/d8b6358f-5953-4397-9fc7-6e1dc6b1e93a/action_structure_wikidata_mapping.csv)]​|
|`description`|string|`"Actor participated in battle"`|Human-readable|
|`notes`|string||Free-form comments|

## Example (conceptual)

- `FOUGHT_IN`
    
    - `crm_property = "P11"` (`E5 Event` – `P11 had participant` – `E39 Actor`).[[cidoc-crm](https://cidoc-crm.org/cidoc-crm/)]​
        
    - `wikidata_property = "P710"` (participant).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/d8b6358f-5953-4397-9fc7-6e1dc6b1e93a/action_structure_wikidata_mapping.csv)]​
        

The registry is ingested from `action_structure_vocabularies.csv` and `action_structure_wikidata_mapping.csv`.[action_structure_vocabularies.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/85cc4981-7c4a-4372-8791-79a99b076ef4/action_structure_vocabularies.csv)

---

## 4.2 Belief Node (Reified Relationship Instance) ⭐ “X Fought at Y”

Instead of directly asserting `(A)-[:FOUGHT_IN]->(B)`, you create a **Belief** node that:

- Instantiates a `RelationshipType`.
    
- Connects to the subject and object entities.
    
- Carries evidence, uncertainty, and alignment.[unified-mapping-with-reification.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/364fcacd-a182-43c1-a41e-22771039c6b1/unified-mapping-with-reification.md)
    

## Node Label

text

`:Belief`

## Purpose

Represent a **single asserted relationship instance** (e.g., “Caesar fought in the Battle of Pharsalus”), with attached sources and confidence. This is the CRMinf‑style proposition you can review and revise.[[cidoc-crm](https://cidoc-crm.org/sites/default/files/CRMinf%20v1.1%20\(2024.12.09\).pdf)]​[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/024d1aee-93ca-4309-8e92-8a027a0b40d9/CRMinf_v0.7_.rdfs.txt)]​

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`belief_id`|string|`"bel_000123"`|Unique ID|
|`reltype_id`|string|`"rt_fought_in"`|Which RelationshipType it instantiates|
|`statement`|string|`"Caesar fought in the Battle of Pharsalus"`|Human-readable|
|`timestamp`|string|`"2026-02-12T15:00:00Z"`|When this belief was created|
|`confidence`|float|`0.85`|System/agent confidence|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`source_agent`|string|`"roman_republic_agent_001"`|Agent that created the belief|
|`crm_property`|string|`"P11"`|Redundant copy from RelationshipType|
|`wikidata_property`|string|`"P710"`|Optional shortcut|
|`justification`|string|`"Based on Plutarch, Caesar 39"`|Brief justification|
|`uncertainty_note`|string|`"Modern scholarship disputes troop numbers"`|Narrative uncertainty|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`USES_RELTYPE`|RelationshipType|`(belief)-[:USES_RELTYPE]->(rt)`|
|`BELIEF_SUBJECT`|Entity|`(belief)-[:BELIEF_SUBJECT]->(entityA)`|
|`BELIEF_OBJECT`|Entity|`(belief)-[:BELIEF_OBJECT]->(entityB)`|

Entities here are usually `Event`, `Person`, `Place`, `Organization`, etc.

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`HAS_SOURCE`|Work|Evidence works (books, inscriptions, datasets)|
|`HAS_PASSAGE`|Claim/ReasoningTrace|Link into Claims layer context|
|`HAS_NOTE`|Note|Uncertainty/annotation nodes|
|`ABOUT_EVENT`|Event|If belief itself is tied to a specific event|

This is the **Layer 3 “belief node”** in your diagram: RelationshipType nodes (Layer 1/2) define the semantics; Belief nodes represent concrete instances.[relationship_types_diagram.jpg+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/100192890/1a240cbe-aa6a-4646-aedd-72d7f5b4398f/relationship_types_diagram.jpg)

---

## 4.3 CIDOC‑CRM Alignment Layer ⭐ Events, Participation, Place

Each RelationshipType aligns to one or more **CIDOC‑CRM** properties so that your graph can be exported or interpreted in standard CRM terms.[cidoc-crm+1](https://cidoc-crm.org/rdfs/7.1.1/CIDOC_CRM_v7.1.1.rdf)

Key CRM patterns (conceptual):

- `E5 Event` – `P11 had participant` – `E39 Actor`.
    
- `E5 Event` – `P7 took place at` – `E53 Place`.
    
- `E7 Activity` – `P14 carried out by` – `E39 Actor`.[[cidoc-crm](https://cidoc-crm.org/cidoc-crm/)]​
    

Mapping into your model:

- `:Event` nodes correspond to `E5 Event` / `E7 Activity`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4598a569-9988-45f3-8efd-32917d0dc056/2-12-26-Chrystallum-Architecture-DRAFT.md)]​[[cidoc-crm](https://cidoc-crm.org/cidoc-crm/)]​
    
- `:Person` / `:Organization` correspond to `E39 Actor`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4598a569-9988-45f3-8efd-32917d0dc056/2-12-26-Chrystallum-Architecture-DRAFT.md)]​
    
- `:Place` corresponds to `E53 Place`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4598a569-9988-45f3-8efd-32917d0dc056/2-12-26-Chrystallum-Architecture-DRAFT.md)]​
    

For an instance like “Caesar fought in the Battle of Pharsalus”:

- CRM view: `BattleOfPharsalus (E5)` – `P11 had participant` – `Caesar (E39)`.[[cidoc-crm](https://cidoc-crm.org/cidoc-crm/)]​
    
- Your view:
    
    - `RelationshipType rt_fought_in` with `crm_property = "P11"`.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/85cc4981-7c4a-4372-8791-79a99b076ef4/action_structure_vocabularies.csv)]​[[cidoc-crm](https://cidoc-crm.org/cidoc-crm/)]​
        
    - `Belief bel_000123` with `USES_RELTYPE -> rt_fought_in`, `BELIEF_SUBJECT -> Caesar`, `BELIEF_OBJECT -> BattleOfPharsalus`.
        

This keeps your internal representation rich (with belief and evidence) while preserving a straightforward CRM projection.

---

## 4.4 CRMinf Alignment Layer ⭐ Argumentation & Propositions

CRMinf extends CIDOC‑CRM with classes for **argumentation and belief** (e.g., `I1 Argumentation`, `I2 Belief`, `I3 Inference Logic`, `I4 Proposition Set`).[cidoc-crm+1](https://cidoc-crm.org/sites/default/files/CRMinf%20v1.0\(site\).pdf)[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/024d1aee-93ca-4309-8e92-8a027a0b40d9/CRMinf_v0.7_.rdfs.txt)]​

You already have a Claims layer; here’s how things align:

- `:Claim` ≈ **I2 Belief / I4 Proposition Set** (a stated proposition about the world).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4d6e3156-c17c-4ea7-8279-6a3a5afb8f1f/2-12-26-perplexity-Claims-Schema-Final.md)]​[[cidoc-crm](https://cidoc-crm.org/sites/default/files/CRMinf%20v1.1%20\(2024.12.09\).pdf)]​
    
- `:ReasoningTrace` ≈ **I1 Argumentation / I3 Inference Logic** (how the belief was derived).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/65b71526-bce0-40ca-93d8-f9d03e0ae7da/2-12-26-Claim-node-schema-final.md)]​[[cidoc-crm](https://cidoc-crm.org/sites/default/files/CRMinf%20v1.1%20\(2024.12.09\).pdf)]​
    
- `:Review` ≈ **evaluations of beliefs** by different agents.[[cidoc-crm](https://cidoc-crm.org/sites/default/files/CRMinf%20v1.1%20\(2024.12.09\).pdf)]​[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/65b71526-bce0-40ca-93d8-f9d03e0ae7da/2-12-26-Claim-node-schema-final.md)]​
    
- `:Belief` (this section) can serve as the **proposition node** for concrete relationships, which Claims refer to.
    

Pattern:

- `Claim` expresses a natural-language assertion and its status (`proposed/validated/...`).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4d6e3156-c17c-4ea7-8279-6a3a5afb8f1f/2-12-26-perplexity-Claims-Schema-Final.md)]​
    
- `Belief` encodes the same assertion structurally (subject/object/reltype).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/364fcacd-a182-43c1-a41e-22771039c6b1/unified-mapping-with-reification.md)]​
    
- `ReasoningTrace` explains how the Claim/Belief was derived.[CRMinf_v0.7_.rdfs.txt+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/024d1aee-93ca-4309-8e92-8a027a0b40d9/CRMinf_v0.7_.rdfs.txt)
    
- `Review` nodes implement multi-agent argumentation over that Claim/Belief.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/65b71526-bce0-40ca-93d8-f9d03e0ae7da/2-12-26-Claim-node-schema-final.md)]​
    

You can link them explicitly:

text

`// Claim → Belief alignment MATCH (c:Claim {claim_id: $claim_id}), (b:Belief {belief_id: $belief_id}) MERGE (c)-[:ASSERTS_BELIEF]->(b); // ReasoningTrace used to support Belief MATCH (t:ReasoningTrace {trace_id: $trace_id}), (b:Belief {belief_id: $belief_id}) MERGE (t)-[:SUPPORTS_BELIEF]->(b);`

This gives you a CRMinf-style network of propositions, arguments, and evaluations, grounded in CRM-compatible events and actors.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/024d1aee-93ca-4309-8e92-8a027a0b40d9/CRMinf_v0.7_.rdfs.txt)]​[[cidoc-crm](https://cidoc-crm.org/sites/default/files/CRMinf%20v1.1%20\(2024.12.09\).pdf)]​

---

## 4.5 End-to-End Example (Military Relationship)

Example: “Caesar commanded Pompey’s forces at Pharsalus” (hypothetical pattern).

1. **Registry**
    

text

`MERGE (rt:RelationshipType {   reltype_id: "rt_commanded_forces" }) SET rt.label            = "COMMANDED_FORCES",     rt.category         = "military",    rt.crm_property     = "P14",            // carried out by (activity ↔ actor) [web:167]    rt.crm_domain_class = "E7_Activity",    rt.crm_range_class  = "E39_Actor",    rt.wikidata_property= "P710";          // example, real mapping from CSV [file:152]`

2. **Belief**
    

text

`MATCH (caesar:Person {qid:"Q1048"}),       (pharsalus:Event {qid:"Q123456"}) MERGE (b:Belief {   belief_id: "bel_000900",  reltype_id: "rt_commanded_forces" }) SET b.statement  = "Caesar commanded the Roman forces at Pharsalus",     b.timestamp  = "2026-02-12T15:00:00Z",    b.confidence = 0.82; MERGE (b)-[:USES_RELTYPE]->(rt) MERGE (b)-[:BELIEF_SUBJECT]->(caesar) MERGE (b)-[:BELIEF_OBJECT]->(pharsalus);`

3. **Evidence and Claim**
    

text

`MATCH (work:Work {title:"Caesar: A Biography"}),       (b:Belief {belief_id:"bel_000900"}) MERGE (b)-[:HAS_SOURCE]->(work); // Claim links narrative to belief MERGE (c:Claim {claim_id:"claim_000900"}) SET c.text       = "Caesar commanded the Roman forces at Pharsalus.",     c.status     = "proposed",    c.confidence = 0.82; MERGE (c)-[:ASSERTS_BELIEF]->(b);`

This example shows how the **RelationshipType registry**, **Belief nodes**, **Claims**, and **CIDOC‑CRM/CRMinf alignment** all work together as one coherent layer.

---

# ✅ **Chunk 4 complete.**

When you're ready, say:

```
begin chunk 5
```

Chunk 5 will include:

- Glossary
- Ontology overview diagram
- Data flow diagram
- Promotion pipeline diagram
- Versioning & change log

This will finalize the full integrated ontology document.

Absolutely, Tony — here is **Chunk 5**, the final section of the integrated ontology document.  
This closes out the full specification with:

- **Glossary**
- **Ontology Overview Diagram**
- **Data Flow Diagram**
- **Promotion Pipeline Diagram**
- **Versioning & Change Log**

Everything is formatted to drop directly into your master ontology file.

---

# 📘 **INTEGRATED ONTOLOGY DOCUMENT — CHUNK 5**

# **5. APPENDICES**

These appendices provide reference material, diagrams, and versioning structures that support long‑term maintenance and onboarding for future contributors.

---

# **5.1 Glossary**

A concise glossary of all major terms used across the ontology.

### **Agent**

A graph-native reasoning actor that generates claims, reviews claims, retrieves evidence, and maintains memory. Not an LLM; a structured component of the system.

### **AgentMemory**

A persistent record of an agent’s long-term context, including topics covered, entities discussed, and working hypotheses.

### **Authority Metadata**

Identifiers from external classification systems (LCSH, FAST, LCC, CIP, Wikidata, etc.) attached to SubjectConcepts.

### **BROADER_THAN / NARROWER_THAN**

SKOS-like hierarchical relationships between SubjectConcepts.

### **Claim**

A structured assertion made by an agent about the world, subject to review, consensus, and promotion.

### **Consensus Score**

Weighted confidence score derived from reviews; determines claim status.

### **Entity**

A real-world thing: person, place, event, period, organization, etc.

### **Facet**

An analytical dimension used to classify SubjectConcepts (e.g., Political, Military, Economic).

### **Framework Layer**

The cross-authority alignment system (CIP → QID → LCC → LCSH → FAST) and normalization logic.

### **ProposedEdge**

A relationship proposed by a claim but not yet materialized.

### **ReasoningTrace**

A structured record of how an agent derived a claim.

### **RetrievalContext**

A record of what passages were retrieved from an agent’s private vector store.

### **Synthesis**

A node representing multi-agent consensus-building when claims conflict.

### **SubjectConcept**

A conceptual category used for classification, topic modeling, and agent domain definition.

### **Topic Spine**

A curated, stable hierarchy of SubjectConcepts spanning all facets.

---

# **5.2 Ontology Overview Diagram**

A high-level ASCII diagram showing how the four major layers relate.

```
+-------------------------------------------------------------+
|                         ONTOLOGY                            |
+-------------------------------------------------------------+

  +-------------------+       +-----------------------------+
  |   Entity Layer    |       |       Subject Layer         |
  | (People, Places,  |       | (SubjectConcepts, Facets,   |
  |  Events, Periods) |<----->|  Authority Metadata, Spine) |
  +-------------------+       +-----------------------------+
             ^                           ^
             |                           |
             |                           |
             v                           v
  +---------------------------------------------------------+
  |                     Agent Layer                         |
  | (Subject Agents, Entity Agents, Coordinator Agents,     |
  |  Routing, Memory, Domain Ownership)                     |
  +---------------------------------------------------------+
                             |
                             |
                             v
  +---------------------------------------------------------+
  |                     Claims Layer                        |
  | (Claims, Reviews, ProposedEdges, ReasoningTraces,       |
  |  RetrievalContext, Synthesis, Promotion)                |
  +---------------------------------------------------------+
```

---

# **5.3 Data Flow Diagram**

Shows how information moves through the system during claim creation and review.

```
USER QUERY
    |
    v
AGENT
    |
    |---> Vector Store Retrieval
    |          |
    |          v
    |     RetrievalContext
    |
    |---> Reasoning
    |          |
    |          v
    |     ReasoningTrace
    |
    |---> Claim Creation
    |          |
    |          v
    |     Claim (status="proposed")
    |
    v
COORDINATOR AGENT
    |
    |---> Select Reviewers
    |---> Collect Reviews
    |---> Compute Consensus
    |
    v
CLAIM STATUS UPDATE
    |
    |---> validated → Promotion
    |---> disputed  → Hold
    |---> rejected  → Archive
```

---

# **5.4 Promotion Pipeline Diagram**

Shows how proposed structure becomes validated graph structure.

```
Claim (proposed)
    |
    v
Reviews
    |
    v
Consensus Score
    |
    |-- score >= 0.8 → VALIDATED
    |-- 0.5–0.79     → DISPUTED
    |-- < 0.5        → REJECTED
    |
    v
VALIDATED
    |
    v
Promotion Pipeline
    |
    |-- Convert ProposedEdges → Real Relationships
    |-- Apply edge_properties
    |-- Promote proposed nodes
    |-- Attach provenance
    |-- Mark claim.promoted = true
    |
    v
Core Graph Updated
```

---

# **5.5 Versioning & Change Log**

A structure for tracking ontology evolution.

---

## **5.5.1 Ontology Versioning**

Use semantic versioning:

```
MAJOR.MINOR.PATCH
```

- **MAJOR** — breaking changes (schema changes, new node types)
- **MINOR** — new features (new relationships, new facets)
- **PATCH** — fixes, clarifications, metadata updates

### Example

```
Ontology Version: 1.3.0
Claims Layer Version: 1.0.0 (canonical from file 133)
Subject Layer Version: 1.2.1
Entity Layer Version: 1.1.0
Agent Layer Version: 1.1.3
```

---

## **5.5.2 Change Log Template**

```
## [1.3.0] — 2026-02-12
### Added
- Added Claims Layer (canonical file 133)
- Added Synthesis node type
- Added Promotion Pipeline

### Changed
- Updated SubjectConcept schema with new facet fields
- Updated Agent routing logic

### Fixed
- Corrected BROADER_THAN/NARROWER_THAN directionality
```

---

## **5.5.3 Deprecation Policy**

- Deprecated nodes marked with `deprecated: true`
- Deprecated relationships marked with `deprecated: true`
- Deprecated SubjectConcepts linked to replacements via `REPLACED_BY`

---

# **5.6 Final Notes**

This completes the **full integrated ontology document**, across:

1. **Entity Layer**
2. **Subject Layer**
3. **Agent Layer**
4. **Claims Layer (canonical)**
5. **Appendices**

You now have a **production‑grade, cross‑linked, versioned, fully modular ontology** ready for implementation, documentation, and long-term maintenance.

---


Yes, the Triple Canon diagram is still conceptually valid with your current architecture; it just needs updated labels to match your newer terms.

How it lines up now:[2-12-26-Chrystallum-Architecture-DRAFT.md+2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4598a569-9988-45f3-8efd-32917d0dc056/2-12-26-Chrystallum-Architecture-DRAFT.md)

- **User Layer / Historical Claim**  
    Maps directly to your `:Claim` + `:Belief` pattern: a user assertion (“Caesar crossed the Rubicon”) entering the Claims layer.
    
- **Modern Concept Layer**  
    This is now your **SubjectConcept / Topic Spine** plus any local “modern concept” wrappers you keep for UX. The “concept_id: caesar_rubicon” slot is effectively a SubjectConcept‑like node with facets and keywords, aligned to LCSH/FAST etc.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- **Triple Canon (LCC/MARC, Getty TGN, PeriodO)**  
    Still correct as three external **authority canons**:
    
    - LCC/MARC → SubjectConcepts and Work metadata.
        
    - TGN → Place entities and geographic SubjectConcepts.
        
    - PeriodO → Period entities and chronological SubjectConcepts.[periodo-dataset.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/7bce58bb-f521-40e3-a9e8-690964d81d3c/periodo-dataset.csv)
        
    
    In the current system, these become `:SubjectConcept` and `:Period` nodes with `scheme/authority` properties and `ALIGNED_WITH` edges.
    
- **LangGraph Agent Layer**  
    Matches your **Agent Architecture**: Orchestrator/Supervisor routes the claim to domain agents (Roman history, geography, methodology), each with its own RAG index and shared graph access.[2-12-26-Agent-Schema.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/efe642f5-3182-4f8d-97d0-88672a370339/2-12-26-Agent-Schema.md)
    
- **Validation Output**  
    Now implemented more explicitly via **Claim + Review + Synthesis**:
    
    - `status = validated/disputed/rejected`.
        
    - `consensus_score` ≈ the “confidence 0.94” shown in the diagram.[2-12-26-perplexity-Claims-Schema-Final.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4d6e3156-c17c-4ea7-8279-6a3a5afb8f1f/2-12-26-perplexity-Claims-Schema-Final.md)
        

So logically it’s still right; you would just:

- Rename “Modern Concept Layer” in your text to explicitly mention **SubjectConcepts** and the Topic Spine.
    
- Note that “Validation Output” is the **Claims Layer** output (`:Claim` + `:Belief` + `:Review`), not just a single score.

![[Pasted image 20260212143207.png]]r


The diagram `cypher_patterns.jpg` matches the logical progression we’ve been building, but with a slight terminology shift you should align.[cypher_patterns.jpg+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/100192890/267a2a52-f37a-4929-9984-130833a04973/cypher_patterns.jpg?AWSAccessKeyId=ASIA2F3EMEYERTI7TZKX&Signature=KDC37NEka6L7a0RDCNt6Uz3udvQ%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEBQaCXVzLWVhc3QtMSJHMEUCIHU1BJR1wztdMPv3nmDPMNmiamOkZH8pKRVL6CeMdv2mAiEA8xKwZDhpFQej%2BB3QY%2F5PhpXiQj7rUww0cy3Vx1%2FBrLkq%2FAQI3P%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDFOiaGiful3lIyXU6SrQBADP4LBdMzNQGUIR63NCnCrk%2Fw0%2BlNNxyDEO8kzuss6Kd5vsZnrMHDXfRrY4JRRKBBXLbB9ec0eRuCaKemZ5ZMTvrl026eUylpbiskKkSXrO0lqQxhihGt%2B5Q1ax%2FeX8AqCqc9a0RU37rOrS5yn8rCxQk9rbmR1LIoKilTtwna1ojx%2BIqDAUbU7eL1hdXCX6mDUTz9zBUVzm9%2FDwoC5F1VgX8MHB9OzW9rhZg7Rb4dAvug3xGM9zBUO4F4TLe4i66Y5bhkI2foavL8hI61yA7qG1p%2FkQnHIa60mMhyGE4rltZlRD%2BJ%2FdXotpH43egAeUxZ9IQSneB190qBZFuBBtxSI7UKhSmomKHlNuP7TRzmI5zwuqV0l3roJGUJehGAiICEf10IeltJ%2BDpXZ09BWhcxtkK0Ejqo6R2O6GHyEfu9IHDfjnsmSdNINr9aXMmHIy24j2FEBM8J7%2FtX4ZKnRe6bJn8JPLnGdlijWe6pcAAJSFZ3N7DxujVD74gCud5XsmzFLoC3OyzeK1T70v1NMiD1IXXWOSJTXeAyIJjph6E6485IE6%2BgwSn6lQ%2Bn%2BeRc1HGjACCAZ%2BZBEmBU%2FLdvy2bXVVPZFzO2DCaqvFHNItruEJvTb4388AbO1arh%2BAvWAPHv2ThAlsS0flBuRtq9semlUhV5dT9l8IqNyT95I5mnD2ZgggTBq9NopOdSNWHQ4wae6xy83i4lB%2FcYPpUV744gd%2FPcLZcKu9geyc4k124Q%2Fnm%2FD8YB8Qh7rFhora3L59RGH%2Boety6NXy74XEPAYRcW4wqMu4zAY6mAGcSK4flf%2FiMRIL6XauYIf2G2ipPUQ0aaTxrDM1zaP611vrTNzpBFzBdG7u5Z%2F%2BDtocleUKBDWEWCyLZrnGpNyflNVpts6HssR7mA%2F3ZyTem04cOsvbTBwBSfVvFvregp76Ty1lsOjLouySd8T7vr3UHV0bhjWRy5OoCY0QVQF3l7yuapD3aUB%2Bd1WUcpUN1fkutRiHMzs0JQ%3D%3D&Expires=1770925215)

It outlines 6 levels of query complexity:

1. **Simple Query** (Direct CRM edges: `CRM_TOOK_PLACE_AT`).
    
2. **Evidenced Relationships** (Via `CRM_BELIEF_OBJECT` to a `:Belief` node).
    
3. **With Evidence/Citations** (Belief → `CRM_HAS_SOURCE` → Citation).
    
4. **With Caveats/Uncertainty** (Belief → `MINF_HAS_NOTE`).
    
5. **Belief Revision Pattern** (Old Belief → `MINF_REPLACED_BY` → New Belief).
    
6. **By Relationship Type** (Aggregation via `RelationshipType`).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/100192890/267a2a52-f37a-4929-9984-130833a04973/cypher_patterns.jpg?AWSAccessKeyId=ASIA2F3EMEYERTI7TZKX&Signature=KDC37NEka6L7a0RDCNt6Uz3udvQ%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEBQaCXVzLWVhc3QtMSJHMEUCIHU1BJR1wztdMPv3nmDPMNmiamOkZH8pKRVL6CeMdv2mAiEA8xKwZDhpFQej%2BB3QY%2F5PhpXiQj7rUww0cy3Vx1%2FBrLkq%2FAQI3P%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDFOiaGiful3lIyXU6SrQBADP4LBdMzNQGUIR63NCnCrk%2Fw0%2BlNNxyDEO8kzuss6Kd5vsZnrMHDXfRrY4JRRKBBXLbB9ec0eRuCaKemZ5ZMTvrl026eUylpbiskKkSXrO0lqQxhihGt%2B5Q1ax%2FeX8AqCqc9a0RU37rOrS5yn8rCxQk9rbmR1LIoKilTtwna1ojx%2BIqDAUbU7eL1hdXCX6mDUTz9zBUVzm9%2FDwoC5F1VgX8MHB9OzW9rhZg7Rb4dAvug3xGM9zBUO4F4TLe4i66Y5bhkI2foavL8hI61yA7qG1p%2FkQnHIa60mMhyGE4rltZlRD%2BJ%2FdXotpH43egAeUxZ9IQSneB190qBZFuBBtxSI7UKhSmomKHlNuP7TRzmI5zwuqV0l3roJGUJehGAiICEf10IeltJ%2BDpXZ09BWhcxtkK0Ejqo6R2O6GHyEfu9IHDfjnsmSdNINr9aXMmHIy24j2FEBM8J7%2FtX4ZKnRe6bJn8JPLnGdlijWe6pcAAJSFZ3N7DxujVD74gCud5XsmzFLoC3OyzeK1T70v1NMiD1IXXWOSJTXeAyIJjph6E6485IE6%2BgwSn6lQ%2Bn%2BeRc1HGjACCAZ%2BZBEmBU%2FLdvy2bXVVPZFzO2DCaqvFHNItruEJvTb4388AbO1arh%2BAvWAPHv2ThAlsS0flBuRtq9semlUhV5dT9l8IqNyT95I5mnD2ZgggTBq9NopOdSNWHQ4wae6xy83i4lB%2FcYPpUV744gd%2FPcLZcKu9geyc4k124Q%2Fnm%2FD8YB8Qh7rFhora3L59RGH%2Boety6NXy74XEPAYRcW4wqMu4zAY6mAGcSK4flf%2FiMRIL6XauYIf2G2ipPUQ0aaTxrDM1zaP611vrTNzpBFzBdG7u5Z%2F%2BDtocleUKBDWEWCyLZrnGpNyflNVpts6HssR7mA%2F3ZyTem04cOsvbTBwBSfVvFvregp76Ty1lsOjLouySd8T7vr3UHV0bhjWRy5OoCY0QVQF3l7yuapD3aUB%2Bd1WUcpUN1fkutRiHMzs0JQ%3D%3D&Expires=1770925215)]​
    

This **is still true** and valid for your architecture, with these minor schema alignments:

- **Edges**: The diagram uses specific edge labels like `:CRM_BELIEF_OBJECT` and `:MINF_REPLACED_BY`. In your `Relationship & Argumentation Layer` (Section 4), we named these `:BELIEF_OBJECT` and `:SUPPORTS_BELIEF` for simplicity. You should pick one naming convention (I recommend the simpler ones unless you strictly need the CRM prefix).
    
- **Nodes**: `:Belief` is central in both your spec and this diagram.
    
- **Patterns**: The diagram correctly shows the "incremental complexity" strategy: use direct edges for speed (Level 1), use Belief nodes for scholarly nuance (Levels 2-6).
    

So, **keep this diagram**. It’s a perfect visual summary of _why_ you have a Belief layer (to handle evidence, uncertainty, and revision) and _how_ to query it.

I can rename the edge labels in your `Relationship & Argumentation Layer` section to match the diagram exactly if you prefer strict consistency (e.g., `USES_RELTYPE` vs `HAS_TYPE`, `BELIEF_OBJECT` vs `CRM_BELIEF_OBJECT`). Which set do you prefer?


# **Non-Functional Requirements & Scale**

## **6.1 Scale Targets (Phase 1)**

- **Entities**: ~50,000 (Focus: Roman Republic 100-44 BCE)
    
- **Claims**: ~200,000 (Avg 4 claims per entity)
    
- **Latency**: < 200ms for direct entity lookups; < 2s for 2-hop graph traversals.
    

## **6.2 Testing Strategy**

- **The "Triple Canon" Benchmark**: A gold-standard dataset of 500 verified facts (e.g., "Caesar crossed the Rubicon in 49 BCE").
    
- **Agent Validation**: Every agent build must score >95% accuracy on the Triple Canon before deployment.
    
- **Hallucination Check**: Random sampling of 1% of new claims for human review weekly.
    

## **6.3 Security (AuthN/AuthZ)**

- **User Roles**: `Viewer`, `Contributor` (can propose claims), `Editor` (can validate/merge), `Admin`.
    
- **Agent Auth**: Each Agent has a unique API key and is restricted to writing specific Relationship Types (e.g., "MilitaryAgent" cannot write "Marriage" edges).
    

Prepared using Gemini 3 Pro

## **2. Operational Controls for Spatial Data** → **New Section 1.7** (Insert after §1.6 Example Cypher Patterns)

**New Section:**

text

`# **1.7 Operational Governance** ## **1.7.1 Spatial Version Proliferation Rules** ## **1.7.2 The VersionSelector Component** ## **1.7.3 Indexing Strategy**`

**Pattern Match:** Follows architectural decision pattern from existing sections

## **. Neo4j Constraints & Decisions** → **New Section 1.8** (Insert after §1.7)

**New Section:**

text

`# **1.8 Schema Enforcement & DDL** ## **1.8.1 Uniqueness Constraints** ## **1.8.2 Architectural Decisions**   - SKOS Directionality  - Facet Policy (Hybrid)`

**Pattern Match:** Technical specification pattern consistent with existing schemas

## **4. Period Classification & Ingestion** → **Expand Section 1.5** (Update existing Temporal Modeling)

**Current:** §1.5 Temporal Modeling (Year, Period, PeriodO)  
**Expanded:**

text

`# **1.5 Temporal Modeling** ## **1.5.1 Year Backbone** ## **1.5.2 Period Classification (Tiers 1-4)** ## **1.5.3 Period Ingestion Pipeline**   - Phase 1: Load time_periods.csv  - Phase 2: Apply Tier Logic  - Phase 3: Authority Alignment ## **1.5.4 PeriodO Integration**`

**Pattern Match:** Follows the multi-subsection pattern used in Entity Layer

## **5. Claims Versioning & Confidence Policies** → **Update Section 4.1 & 4.10**

**Insert into existing Claims Layer:**

**§4.1.5 Claim Versioning** (new subsection after §4.1.4 Optional Edges)

text

`:Claim {   version: 2,  previous_version_id: "clm_001_v1",  update_reason: "New evidence from 2024 excavation" }`

**§4.10.2 Evidence Weighting & Temporal Decay** (new subsection after §4.10.1 Consensus Calculation)

- Primary Source: 1.0
    
- Secondary Scholarly: 0.8
    
- Tertiary/Encyclopedic: 0.6
    
- LLM Inference: 0.4
    
- Temporal Decay: -0.05/year
    

**Pattern Match:** Follows the subsection numbering pattern in Claims Layer

---

## **6. Non-Functional Requirements** → **New Section 6** (Append after Section 5)

**New Section:**

text

`# **6. NON-FUNCTIONAL REQUIREMENTS & SCALE** ## **6.1 Scale Targets (Phase 1)** ## **6.2 Testing Strategy**   - The "Triple Canon" Benchmark  - Agent Validation  - Hallucination Check ## **6.3 Security (AuthN/AuthZ)**   - User Roles  - Agent Auth ## **6.4 Performance Goals**   - <200ms direct lookups  - <2s 2-hop traversals`

**Pattern Match:** Follows top-level section numbering (1. Entity, 2. Subject, 3. Agent, 4. Claims, 5. Appendices, **6. Non-Functional**)

---

## **7. Vector Store Clarification** → **Update Section 4.0.1** (Existing System Architecture Context)

**Current:** §4.0.1 Two Separate Systems (table)  
**Add subsection:** §4.0.2 The Claim Bridge Pattern

text

`### **4.0.2 The Claim Bridge Pattern** Agents operate as: 1. Read private vector stores → Retrieve evidence 2. Synthesize answer → Generate Claim 3. Write public Claim to Neo4j → Shared knowledge **Key Rule:** Vector stores are private inputs; Claims are public outputs.`

**Pattern Match:** Extends existing architectural context section

---

## **Summary Table: Where Each Piece Goes**

| Extracted Content                     | Target Section           | Insert Method          |
| ------------------------------------- | ------------------------ | ---------------------- |
| Place/PlaceVersion Architecture       | §1.2.3                   | Replace existing       |
| VersionSelector & Proliferation Rules | §1.7 (new)               | Append to Entity Layer |
| Neo4j Constraints & Decisions         | §1.8 (new)               | Append to Entity Layer |
| Period Tier Classification            | §1.5.2 (expand)          | Update existing        |
| Period Ingestion Pipeline             | §1.5.3 (new)             | Append to §1.5         |
| Claim Versioning                      | §4.1.5 (new subsection)  | Insert after §4.1.4    |
| Evidence Weighting                    | §4.10.2 (new subsection) | Insert after §4.10.1   |
| Non-Functional Requirements           | §6 (new section)         | Append after §5        |
| Vector/Graph Separation               | §4.0.2 (new subsection)  | Expand §4.0            |
These new files (`ACTION_PLAN.md`, `GAP_ANALYSIS_SUMMARY.md`, `bdd-periodo.md`) add significant operational detail to the **Temporal** and **Subject** layers.

Here is how I will integrate them into your Architecture Document:

## **1. Integration: Period Ingestion & Gap Filling (Section 1.5.3)**

_(Enhances the "Ingestion Pipeline" based on Action Plan and Gap Analysis)_

**Source:** (Action Plan), (Gap Analysis)[ACTION_PLAN.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1b282e14-ec2f-4bbb-9c18-6d4911839ac9/ACTION_PLAN.md)

**Updated Plan:**

- **Phase 1: Quick Wins**: Pattern-based facet enhancement (Regex for "Economic", "Technological" facets) & Canonical Eras (8 global eras).
    
- **Phase 2: Gap Filling**: Targeted queries for missing regions (Sub-Saharan Africa, Oceania) and missing critical periods (Industrial Revolution, Han Dynasty).
    
- **Phase 3: Wikipedia Year Extraction**: Extract events from Year pages to densify the timeline.
    

## **2. Integration: The PeriodO BDD Architecture (Section 1.5.4)**

_(New deep-dive section for PeriodO Federation)_

**Source:** (BDD PeriodO)[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/310b21d9-0029-4a07-858d-82d4fbffa71e/bdd-periodo.md)]​

**New Content:**

- **Block Definition Diagrams (BDD)**: Explicitly map `Period` (PeriodO-centric) vs. `Place` (Temporal Identity derived from Period).
    
- **LLM Ports**: Define specific tasks for LLMs:
    
    - `llm_resolve_temporal_conflicts`: Reconcile start/end dates.
        
    - `llm_infer_spatial_applicability`: Map generic periods to specific places.
        
    - `llm_resolve_authority_conflicts`: Handle Wikidata vs. Pleiades disagreements.
        
- **Pipelines**:
    
    - **Temporal Reasoning Pipeline**: Load PeriodO → Build Hierarchy → Infer Perspective → Inherit to Place.
        
    - **Spatial Reasoning Pipeline**: Load Gazetteers → Resolve Equivalence → Align Geometries.
        

## **3. Integration: Canonical Global Spine (Section 1.2.4)**

_(Refines the "Era" node definition)_

**Source:** (Action Plan - Phase 1B)[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/1b282e14-ec2f-4bbb-9c18-6d4911839ac9/ACTION_PLAN.md)]​

**Explicit Schema Update:**

- Define the **8 Canonical Eras** as hardcoded `TopicSpine` nodes:
    
    1. Prehistory
        
    2. Ancient
        
    3. Classical
        
    4. Post-Classical
        
    5. Early Modern
        
    6. Long 19th Century
        
    7. Short 20th Century
        
    8. Contemporary
        

## **4. Integration: Gap Analysis Strategy (Section 6.1)**

_(Enhances Scale & Scope targets)_

**Source:** (Gap Analysis)[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/41cc4b14-9d4d-4b0c-bcc6-289b355db3f8/GAP_ANALYSIS_SUMMARY.md)]​

**New Scope Targets:**

- **Target Coverage**: ~450 high-priority periods (up from current 125).
    
- **Critical Gaps to Close**: Industrial Revolution, Chinese Dynasties (Han/Tang/Ming/Qing), Modern Eras (Atomic/Space/Information Ages).
    

---

## **Summary of Where These Go:**

|File Content|Target Section in Architecture Doc|
|---|---|
|**PeriodO BDD & LLM Ports**|**§1.5.4** PeriodO Federation & LLM Architecture|
|**Canonical Eras List**|**§1.2.4** Period / Era Schema|
|**Ingestion Phases (1-3)**|**§1.5.3** Period Ingestion Pipeline|
|**Gap Analysis Targets**|**§6.1** Scale Targets (Phase 1)|
|**Facet Regex Strategy**|**§2.2** Facet System (Implementation Note)|

I have extracted all the necessary logic. You can now archive `ACTION_PLAN.md`, `GAP_ANALYSIS_SUMMARY.md`, and `bdd-periodo.md`.

**Would you like me to generate the final, fully-integrated `Chrystallum-Architecture-FINAL.md` document now?**[[]]

I have integrated the insights from `time_periods.csv` and the review files into a **Classification & Facet Strategy** section for your Appendix.

This addition addresses the specific gaps identified in your CSV (e.g., Euro-centricity, missing economic facets) and operationalizes the decision criteria (Tiers 1-4) for period ingestion.

You can append this directly to the **APPENDIX** package I just generated.

---

## **A.4 Period Classification & Facet Strategy**

_(Based on `time_periods.csv` Analysis & `time-period-review.md`)_

## **1. The Classification Problem**

The raw `time_periods.csv` contains heterogeneous entities (e.g., "Cold War" vs. "Boldino autumn"). To build a clean backbone, we apply a **Tiered Classification Logic** during ingestion.

## **2. Tiered Decision Logic (The Filter)**

- **Tier 1: Canonical Periods (Keep)**
    
    - _Criteria_: Multigenerational span (>20 years), broad geographic scope, distinct historiographic identity.
        
    - _Action_: Import as `:Period`. Link to Era Spine.
        
    - _Examples_: "Roman Republic", "Ming Dynasty", "Iron Age".
        
- **Tier 2: Events & Crises (Reclassify)**
    
    - _Criteria_: Short duration (<10 years), defined by specific actions/conflicts rather than a structural state.
        
    - _Action_: Import as `:Event`.
        
    - _Examples_: "Crisis of the Third Century", "Barbarian Invasions" (if treated as waves), "Phoney War".
        
- **Tier 3: Institutional Spans (Reclassify)**
    
    - _Criteria_: Defined strictly by the tenure of a person or body.
        
    - _Action_: Import as `:InstitutionalSpan` or merge into the Organization entity.
        
    - _Examples_: "Reign of Terror", "Rehnquist Court".
        
- **Tier 4: Archival/Niche (Drop)**
    
    - _Criteria_: Metadata artifacts or hyper-local micro-periods.
        
    - _Action_: Discard.
        
    - _Examples_: "The Alfred Nobel Family Archives 1868–1905", "Boldino autumn".
        

## **3. Facet Enrichment Strategy (The Regex Fix)**

The current CSV lacks Economic, Technological, and Religious facets. We will apply this regex-based enrichment during Phase 1 ingestion:

|Target Facet|Regex Keywords|Examples to Catch|
|---|---|---|
|**Technological**|`(industrial\|steam\|digital\|atomic\|space\|bronze\|iron)`|Industrial Revolution, Atomic Age, Bronze Age|
|**Economic**|`(trade\|commerce\|depression\|panic\|gilded\|market)`|Great Depression, Gilded Age, Commercial Revolution|
|**Religious**|`(reformation\|crusade\|awakening\|schism\|temple)`|Reformation, Second Temple Period, Great Awakening|
|**Environmental**|`(ice age\|warming\|climatic\|plague\|famine)`|Little Ice Age, Black Death (as period)|
|**Intellectual**|`(enlightenment\|renaissance\|reason\|modernism)`|Age of Enlightenment, Harlem Renaissance|

## **4. Addressing Geographic Bias**

- **Problem**: The CSV is heavily Euro/Sino-centric.
    
- **Action**: The "Gap Filling" phase (A.3 Phase 2) must explicitly target **QIDs for Sub-Saharan Africa and Oceania** using the Wikidata SPARQL endpoint, specifically filtering for `instance of: historical period` + `location: [Region]`.
    

---

This completes the **Appendix Package**. You now have the architecture for:

1. **PeriodO Integration** (A.1)
    
2. **Spatial Federation** (A.2)
    
3. **Operational Action Plan** (A.3)
    
4. **Classification & Facet Logic** (A.4)
    

You can copy-paste the entire Appendix section into your master document now.

I have extracted the core logic from `lcc-hierarchy-notes.md` to create a **Subject Backbone** appendix.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/229327e9-c872-4dad-86bb-dffe666a652a/lcc-hierarchy-notes.md)]​

This file provides the blueprint for parsing the Library of Congress Classification (LCC) schedules into a **hierarchical SubjectConcept tree** (or DAG) that will serve as the "spine" for your Subject Agents.

Here is the Appendix Package.

---

## **Appendix Package: Subject Backbone & LCC Architecture**

# **APPENDIX B: SUBJECT BACKBONE (LCC ARCHITECTURE)**

## **B.1 The LCC Subject Spine**

_(Based on `lcc-hierarchy-notes.md` logic)_

The Subject Layer uses the **Library of Congress Classification (LCC)** as its primary hierarchical backbone. This provides a stable, globally recognized taxonomy for agent domain scoping.

## **1. Node Structure**

SubjectConcepts derived from LCC are structured as:

- **Top Level**: Broad Class (e.g., `H1-99 Social Sciences (General)`).
    
- **Mid Level**: Subclass Range (e.g., `HA1-4737 Statistics`).
    
- **Low Level**: Specific Topic (e.g., `HA29-32 Theory and method of social science statistics`).
    

## **2. Parsing Logic (XLSX to Hierarchy)**

The ingestion pipeline parses raw LCC schedules using **Containment Logic**:

1. **Tokenize**: Extract `CODE_RANGE` (e.g., "HD28-70") and `LABEL`.
    
2. **Parse Range**: Split "HD28-70" into `Prefix="HD"`, `Start=28`, `End=70`.
    
3. **Build Tree**: A node is a **child** of another node if:
    
    - They share the same Prefix.
        
    - The child's numeric range is fully contained within the parent's numeric range.
        
    - The parent is the _narrowest_ such range available.
        

## **3. The Multi-Parent DAG Strategy**

To support multi-agent validation, the hierarchy is modeled as a **Directed Acyclic Graph (DAG)**, not a strict tree.

- **Primary Parent**: Determined by numeric containment (e.g., `Agricultural Labor` is a child of `Agriculture`).
    
- **Secondary Parents**: Determined by thematic cross-references (e.g., `Agricultural Labor` is also a child of `Labor/Working Class`).
    
- **Utility**: This allows a claim about "farm workers" to automatically trigger review from both the **Agriculture Agent** and the **Labor Agent**.
    

## **B.2 SubjectConcept JSON Schema (Intermediate)**

The parsing pipeline outputs this intermediate JSON structure before graph ingestion:

json

`{   "id": "HD1501-1542",  "code": "HD1501-1542",  "prefix": "HD",  "start": 1501,  "end": 1542,  "label": "Agricultural classes",  "note": "Including farm tenancy, agricultural laborers",  "primary_parent": "HD1401-2210",  "secondary_parents": ["HD4801-8943"],  "children": [] }`

## **B.3 Operational Integration**

1. **Agent Scoping**: Agents are assigned domains based on these LCC ranges (e.g., `Agent_Labor` owns `HD4801-8943` and all its descendants).
    
2. **Claim Routing**: When a claim is linked to a SubjectConcept, the system traverses the `BROADER_THAN` (primary parent) and `RELATED_TO` (secondary parent) edges to find the owning agents.
    

---

You can append this **Appendix B** to your document following Appendix A. It formalizes the logic for transforming LCC schedules into your agent routing backbone.

I have synthesized the contents of the validated files into a detailed **Appendix C**. This section now serves as the "Instruction Manual" for your Agents, explicitly defining the logic they must import from the legacy files to function within the new Claims architecture.

You can copy this into your master document.

---

# **APPENDIX C: LOGIC & VALIDATION PROTOCOLS**

_(Incorporating `geographic_extraction.md`, `temporal_extraction.md`, and `confidence_scoring_rubric.md`)_

This appendix operationalizes the "Laws of Extraction" that all Subject Agents must follow. While the architectural implementation has changed (from direct Cypher to JSON Claims), the **extraction logic** in these files remains the source of truth.

## **C.1 The Geographic Protocol**

_(Source: `geographic_extraction.md` )_[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/826b7389-1502-46ac-9d45-43c41c507cb2/geographic_extraction.md)]​

**1. The "Atomic vs. Tokenizable" Rule**  
Agents must strictly separate natural language (safe for LLMs) from system identifiers (unsafe for LLMs).

- **Tokenizable (LLM Safe)**: Place names ("Rome"), physical features ("Alps"), political entities ("Roman Republic").
    
- **Atomic (Tool Only)**: Coordinates (`41.9, 12.4`), QIDs (`Q220`), GeoNames IDs.
    
    - _Constraint_: An Agent must never attempt to "guess" or "tokenize" a coordinate pair. It must output the place name for the Tool Layer to resolve.
        

**2. The Stability Hierarchy**  
When resolving a location for a Claim, Agents must prioritize features based on temporal stability:

- **Tier 1 (Eternal)**: Continents, Tectonic Plates.
    
- **Tier 2 (Geographic)**: Mountain ranges, Rivers, Islands (Stable > 5,000 years).
    
- **Tier 3 (Settlement)**: Cities (Stable names, but variable footprints).
    
- **Tier 4 (Political)**: Borders, Empires, Provinces (High volatility; unstable identifiers).
    
    - _Rule_: A Claim should link to a Tier 2 or 3 anchor whenever possible, with Tier 4 as a "contextual overlay" property.
        

## **C.2 The Temporal Protocol**

_(Source: `temporal_extraction.md` )_[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/ea8214a2-c1be-414f-9391-b461f6d147f2/temporal_extraction.md)]​

**1. Two-Stage Extraction**  
Agents must not attempt to format ISO dates directly from complex text.

- **Step 1**: Extract the raw text snippet (e.g., "mid-1930s", "Reign of Augustus").
    
- **Step 2**: The Tool Layer (Python) resolves this to ISO 8601 intervals (`1934-01-01/1936-12-31`).
    

**2. The "Fuzzy Consistency" Rule**  
If a historical period term (e.g., "The Great Depression") is consistently used in literature, the Agent must capture it **even if the exact dates are debated**.

- _Action_: The Agent outputs the `Period_Label` and a `Confidence_Score` for the term. It does _not_ force an arbitrary start/end date if the text is ambiguous.
    

**3. Atomic Backbone IDs**  
Agents must treat the following as opaque strings (never tokenized):

- **LCC Codes** (e.g., `DG241-269`)
    
- **FAST IDs** (e.g., `1145002`)
    
- **MARC Codes** (e.g., `sh85115058`)
    

## **C.3 The Confidence Protocol (Scoring Rubric)**

_(Source: `confidence_scoring_rubric.md` )_[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/6f11f311-160d-4fbb-8c52-6d8a1a52e4b4/confidence_scoring_rubric.md)]​

All Claims must include a `confidence_score` (0.0 to 1.0). Agents calculate this using the following Tiered Logic:

**1. Base Score by Source Tier**

|Tier|Description|Base Score|
|---|---|---|
|**Primary**|Coins, inscriptions, contemporary legal texts|**0.90 - 1.00**|
|**Secondary (Academic)**|Peer-reviewed journals, expert monographs|**0.80 - 0.90**|
|**Secondary (General)**|Wikipedia, reliable general history|**0.70 - 0.80**|
|**Inference/LLM**|Synthesized knowledge without direct citation|**0.50 - 0.70**|
|**Speculation**|"It is possible that...", "Historians guess..."|**< 0.40**|

**2. Score Modifiers**

- **+0.05**: Corroborated by 3+ independent sources.
    
- **+0.10**: Supported by physical archaeological evidence.
    
- **-0.15**: Significant historiographical disagreement.
    
- **-0.20**: Direct conflict with a Primary Source.
    

**3. Threshold Actions (The "Bridge")**

- **Score > 0.80**: Generate a standard `Claim` node. (High certainty).
    
- **Score 0.50 - 0.79**: Generate a `Claim` node + trigger `CRMinf` reasoning chain (explain _why_ it's probable).
    
- **Score < 0.50**: Do not ingest as a fact. Store as a `Hypothesis` or discard.
    

## **C.4 The Bridge Protocol: Mapping Logic to JSON**

This protocol defines how an Agent translates these rules into the **February 2026 Claim Schema**.

**Input**:

> _Source Text: "Suetonius states Caesar was born in Subura (Primary Source)."_

**Agent Processing**:

1. **Geographic**: "Subura" is a neighborhood (Tier 3/4). Tool resolves to QID.
    
2. **Confidence**: Source is Suetonius (Primary/Contemporary). Base Score = 0.90.
    
3. **Schema Construction**:
    

json

`{   "node_type": "Claim",  "claim_id": "UUID-...",  "subject_qid": "Q1048",  // Caesar  "property": "P19",       // place of birth  "object_qid": "Q218867", // Subura  "confidence_score": 0.90, // Derived from C.3 (Primary Source)  "confidence_reasoning": "Sourced from Suetonius (Life of Caesar); Primary Source Tier.",  "spatial_context": {    "name": "Subura",      // Derived from C.1 (Natural Language)    "resolution_tier": "Neighborhood/CityDistrict"  },  "citation": {    "source_id": "works:suetonius_caesar",    "passage": "born in Subura"  } }`
