Tony, I’m ready — here is the **fully rewritten, fully enhanced, production‑grade Subject Architecture document**, integrating:

- your original draft
- the debate synthesis
- Claude’s enhancements
- Perplexity’s enhancements
- my own architectural corrections
- all missing sections (facet rules, mapping heuristics, Topic Spine, evolution triggers, weighted ABOUT, etc.)

This is now the **canonical Subject Architecture** for your system.  
It is structured, rigorous, and aligned with the Agent Architecture.

---

# ⭐ **SUBJECT ARCHITECTURE (FINAL, ENHANCED, PRODUCTION‑GRADE)**

### _Authority Concepts, Facets, Hierarchy, Entity Mapping & Agent Integration_

---

# 1. Purpose

The Subject layer provides the **conceptual classification system** for the entire knowledge graph.  
It is the backbone for:

- topical organization
- agent routing
- domain scoping
- aboutness modeling
- authority alignment
- cross‑scheme interoperability
- conceptual navigation
- multi‑agent coordination

Subjects are represented as **SubjectConcept** nodes — SKOS‑style authority concepts drawn from LCSH, FAST, LCC, Dewey, and other schemes.

SubjectConcepts do **not** represent entities in the world.  
They represent **units of thought** used for classification, indexing, and reasoning.

---

# 2. Core Principles

### ✔ 2.1 Subjects ≠ Entities

Entities = things in the world.  
SubjectConcepts = conceptual categories.

### ✔ 2.2 Subjects are SKOS‑like

They support:

- broader/narrower hierarchy
- related terms
- facets
- authority metadata

### ✔ 2.3 Subjects are multi‑authority

Each SubjectConcept may carry:

- LCSH ID
- FAST ID
- Dewey
- LCC
- VIAF
- GND
- Wikidata QID (crosswalk only)

### ✔ 2.4 Subjects classify entities

```
(entity)-[:HAS_SUBJECT_CONCEPT]->(subjectConcept)
```

### ✔ 2.5 Works express aboutness

```
(work)-[:ABOUT]->(entity OR subjectConcept)
```

### ✔ 2.6 Agents use SubjectConcepts for routing

SubjectConcepts define:

- agent domains
- agent boundaries
- agent specialization
- agent spawning
- cross‑facet fusion
- boundary detection

---

# 3. SubjectConcept Node Schema

### Node Label

```cypher
:SubjectConcept
```

### Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`authority_id`|string|"sh85115055"|Primary identifier|
|`scheme`|string|"LCSH"|Authority scheme|
|`heading`|string|"Rome--History--Republic, 510-30 B.C."|Human-readable heading|
|`facet`|string|"topical"|Concept type|
|`unique_id`|string|"SCHEME_LCSH_sh85115055"|Composite key|

### Optional Properties (Authority Metadata)

- `description`
- `aliases`
- `broader_terms`
- `narrower_terms`
- `related_terms`
- `lcc_code`
- `dewey`
- `fast_id`
- `viaf_id`
- `gnd_id`
- `wikidata_qid`
- `wikidata_url`
- `lcsh_url`

---

# 4. Facets

Facets classify SubjectConcepts into functional categories:

- `topical`
- `discipline`
- `geo`
- `event`
- `chronological`
- `name`
- `form`
- `material`
- `occupation`
- `cultural_group`

### Why facets matter

Facets enable:

- agent routing
- domain filtering
- cross‑facet fusion
- conceptual spine selection
- multi‑dimensional reasoning

### Facet Priority (for routing)

From most specific → least specific:

1. **name**
2. **geo**
3. **event**
4. **chronological**
5. **discipline**
6. **topical**

Used when multiple agents match a query.

---

# 5. Facet Assignment Rules

### 5.1 Name facet

If heading contains dates or personal-name pattern:

- “Caesar, Julius, 100–44 B.C.”
- “Senate (Rome)”

### 5.2 Geo facet

If heading refers to a place or region:

- “Rome (Italy)”
- “Gaul”

### 5.3 Event facet

If heading contains:

- battle
- war
- revolt
- siege
- treaty
- campaign

### 5.4 Chronological facet

If heading contains:

- date ranges
- centuries
- “History—[period]”

### 5.5 Discipline facet

If heading is an academic field:

- “Roman law”
- “Classical archaeology”

### 5.6 Form facet

If heading describes document/work type:

- “Inscriptions, Latin”
- “Coins, Roman”

### 5.7 Material facet

If heading describes physical substance:

- “Bronze”
- “Marble”

### 5.8 Occupation facet

If heading describes a role:

- “Gladiators”
- “Soldiers—Rome”

### 5.9 Topical facet (default)

If none of the above apply.

---

# 6. Subject Hierarchy (SKOS‑like)

### Relationship

```
(:SubjectConcept)-[:BROADER_THAN]->(:SubjectConcept)
```

### Notes

- Only one direction is materialized
- Inverse traversal uses `<-[:BROADER_THAN]-`
- Multi-hop traversal supports domain expansion and agent spawning

### Hierarchy Traversal Examples

#### Descendants

```cypher
MATCH (root:SubjectConcept {authority_id:"sh85115055"})
MATCH path = (root)<-[:BROADER_THAN*1..3]-(descendant)
RETURN descendant, length(path)
```

#### Ancestors

```cypher
MATCH (narrow:SubjectConcept {authority_id:"sh85023018"})
MATCH path = (narrow)-[:BROADER_THAN*1..5]->(ancestor)
RETURN ancestor
```

#### Siblings

```cypher
MATCH (c:SubjectConcept {authority_id:"sh85115055"})-[:BROADER_THAN]->(parent)
MATCH (parent)<-[:BROADER_THAN]-(sibling)
WHERE sibling <> c
RETURN sibling
```

---

# 7. Entity ↔ Subject Mapping

### Relationship

```
(entity)-[:HAS_SUBJECT_CONCEPT]->(subjectConcept)
```

### Mapping Heuristics

### 7.1 Person → SubjectConcept

- name facet concept
- occupation concepts
- time period concepts
- geographic concepts

### 7.2 Place → SubjectConcept

- geo facet concept
- time period concepts
- topical concepts

### 7.3 Event → SubjectConcept

- event facet concept
- time period concepts
- geographic concepts
- topical concepts

### 7.4 Work → SubjectConcept

- MARC 650/651/655
- FAST
- Wikidata P921

### Confidence Scoring

Combine:

- catalog alignment
- Wikidata alignment
- temporal alignment
- spatial alignment

---

# 8. Aboutness Modeling

### Relationship

```
(work)-[:ABOUT {weight, source, confidence, facet}]->(entity OR subjectConcept)
```

### Properties

- `weight` (0.0–1.0)
- `source` (“MARC 650”, “FAST”, “inferred”)
- `confidence`
- `facet`

### Notes

- Works may be about multiple things
- Weights support RAG and agent training

---

# 9. SubjectConcept Creation Workflow

### Step 1 — Authority Lookup

Resolve term to:

- LCSH
- FAST
- LCC
- Dewey
- Wikidata

### Step 2 — Node Creation

Create SubjectConcept with:

- authority_id
- scheme
- heading
- facet
- metadata

### Step 3 — Hierarchy Linking

Add `BROADER_THAN` edges.

### Step 4 — Entity Mapping

Add `HAS_SUBJECT_CONCEPT`.

### Step 5 — Work Mapping

Add `ABOUT`.

### Step 6 — Topic Spine Assignment

Add to topical spine if appropriate.

---

# 10. The Topic Spine (Critical)

### Definition

The Topic Spine is the minimal set of **topical-facet** SubjectConcepts that provides comprehensive domain coverage.

### Purpose

- Agent domain definition
- Work classification backbone
- Query routing foundation
- Prevents redundant agents

### Construction Algorithm

1. Start with broadest topical concept (e.g., “Rome—History”).
2. Include first-level narrower concepts.
3. Stop at narrower concepts with < 20 entities.
4. Exclude non-topical facets.

### Query

```cypher
MATCH (root:SubjectConcept {facet:'topical', heading:'Rome--History'})
MATCH path = (root)<-[:BROADER_THAN*1..2]-(spine)
WHERE spine.facet='topical'
WITH spine, count{(spine)<-[:HAS_SUBJECT_CONCEPT]-()} AS entity_count
WHERE entity_count > 20
RETURN spine.heading, entity_count
```

---

# 11. SubjectConcept Roles in Agent Architecture

### 11.1 Domain Definition

Agents define scope via:

- `OWNS_DOMAIN`
- `INCLUDES_CONCEPT`

### 11.2 Routing

Agents selected based on:

- facet
- scheme
- Dewey
- LCC
- hierarchy position

### 11.3 Spawning

Agents spawn sub‑agents when:

- narrower concepts exceed threshold
- domain becomes too broad
- temporal/geographic spread increases

### 11.4 Cross‑Facet Fusion

Agents collaborate across facets:

- geo + topical
- event + discipline
- name + topical

### 11.5 Boundary Detection

If concept outside domain:

- refer to Orchestrator
- Orchestrator may spawn new agent
- Orchestrator may expand SubjectConcept coverage

---

# 12. SubjectConcept Evolution

### 12.1 New Authority Data

Update:

- metadata
- hierarchy
- facet
- crosswalks

### 12.2 Drift Detection

Check:

- concept coverage
- facet alignment
- Dewey/LCC alignment
- temporal/spatial alignment

### 12.3 Concept Splitting

Split when:

- too many entities
- too many narrower terms
- too broad for agent routing

### 12.4 Concept Merging

Merge when:

- too few entities
- redundant with sibling
- orphaned

### 12.5 Facet Conflict Detection

If facet mismatches entity types → flag for review.

### 12.6 Orphan Detection

If no entities, no works, no agents → candidate for deletion.

---

# 13. SubjectConcept Lifecycle Summary

```
1. RESOLVE   → Authority lookup
2. CREATE    → SubjectConcept node
3. CLASSIFY  → Assign facet
4. LINK      → Add BROADER_THAN edges
5. MAP       → Link entities via HAS_SUBJECT_CONCEPT
6. ABOUT     → Link works via ABOUT
7. SPINE     → Add to Topic Spine if appropriate
8. ROUTE     → Agents use SubjectConcepts for domain definition
9. EVOLVE    → Update as authority data grows
```

---

# ⭐ Next Steps

I can now generate:

### ✔ SubjectConcept Schema Table (Period/Person style)

### ✔ Full ingestion pipeline (Python + Cypher)

### ✔ Facet detection module

### ✔ Topic Spine builder

### ✔ Entity→Subject mapping engine

### ✔ Weighted ABOUT assignment engine

Just tell me which one you want next.

From perplexity
This final Subject Architecture reads coherent, implementable, and tightly aligned with the Agent Architecture. It captures all the critical pieces you need.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​

Highlights that are especially strong:

- The **Purpose** and **Core Principles** sections are crisp and clearly separate entities from SubjectConcepts while anchoring everything in SKOS-like behavior and multi-authority alignment.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- The **SubjectConcept Node Schema** is minimal but complete, and `unique_id` as a composite key over `scheme` + `authority_id` is exactly what you want in Neo4j or any backing store.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- The **facet taxonomy and assignment rules** are now explicit and operational, which will make automated facet tagging far easier and more predictable.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- The **hierarchy traversal examples** (descendants, ancestors, siblings) are concrete Cypher patterns you can reuse in agent setup and domain expansion.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- The **Entity ↔ Subject mapping heuristics** by entity type are a pragmatic guide for your Wikidata + index fusion pipelines.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- The **ABOUT edge with weight/source/confidence/facet** gives you the right hooks for both RAG and historian-style provenance reasoning.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- The **Topic Spine** section is an important addition: it codifies how you get a manageable, high-coverage topical backbone instead of just “all topical concepts,” and the algorithm/thresholds are clear.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5bb0df32-bea4-43b6-b193-a8e0111b75ec/2-12-26-Subject-Architecture-Final.md)]​
    
- The integration section (**SubjectConcept Roles in Agent Architecture**) matches the Agent Architecture you just finalized; nothing is out of sync.[2-12-26-Agent-Schema.md+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/efe642f5-3182-4f8d-97d0-88672a370339/2-12-26-Agent-Schema.md)
    

You don’t need structural changes at this point. If you want to iterate further, the next layer would be:

- A concrete **SubjectConcept CSV schema** (column names + types) matching this architecture.
    
- A small **ingestion script layout** (Python + Cypher) that takes LCSH/FAST dumps and produces `:SubjectConcept` + `BROADER_THAN` + `HAS_SUBJECT_CONCEPT` edges.
    

When you’re ready, I can sketch those two pieces so you can move from architecture to a first working import.

From claude

Perfect! This **Final Subject Architecture** document is production-ready and comprehensive. Let me validate it against the requirements:

---

## ✅ Completeness Check

|Component|Status|Location|
|---|---|---|
|**Core principles**|✅ Complete|Section 2|
|**Node schema**|✅ Complete|Section 3|
|**Facets**|✅ Complete|Section 4|
|**Facet assignment rules**|✅ Complete|Section 5 (NEW)|
|**Hierarchy (SKOS)**|✅ Complete|Section 6|
|**Entity→Subject mapping**|✅ Complete|Section 7 (ENHANCED)|
|**Aboutness modeling**|✅ Complete|Section 8 (ENHANCED with weights)|
|**Creation workflow**|✅ Complete|Section 9|
|**Topic Spine**|✅ Complete|Section 10 (NEW - Critical!)|
|**Agent integration**|✅ Complete|Section 11|
|**Evolution & maintenance**|✅ Complete|Section 12 (ENHANCED)|
|**Lifecycle summary**|✅ Complete|Section 13|

---

## 🎯 Key Strengths

### 1. **Facet Assignment Rules** (Section 5)

Finally answers "how do we determine facet?" with clear heuristics:

- Name: dates in heading
- Geo: place names
- Event: battle/war/treaty keywords
- Chronological: date ranges, centuries
- Etc.

### 2. **Topic Spine** (Section 10)

This is the **missing piece** that connects Subject Architecture to Agent Architecture:

```cypher
// Topic Spine = agent domain boundaries
MATCH (agent:Agent)-[:OWNS_DOMAIN]->(spine_concept:SubjectConcept)
WHERE spine_concept IN topic_spine
RETURN agent
```

Without the Topic Spine, agents would need to own thousands of concepts. With it, they own ~10-50 spine concepts and auto-expand to narrower terms.

### 3. **Weighted ABOUT** (Section 8)

```cypher
(work)-[:ABOUT {weight: 0.8, source: "MARC 650", confidence: 0.95}]->(subject)
```

This supports sophisticated RAG ranking and agent training prioritization.

### 4. **Evolution Triggers** (Section 12)

Not just theory—actual maintenance procedures:

- Concept splitting (too many entities)
- Concept merging (too few entities)
- Facet conflict detection
- Orphan detection

### 5. **Complete Lifecycle** (Section 13)

Clear operational workflow from authority lookup through evolution.

---

## 📊 Architecture Alignment

### Subject Architecture ↔ Agent Architecture

|Subject Component|Agent Use Case|
|---|---|
|**Facets**|Agent routing priority (name > geo > event > topical)|
|**Topic Spine**|`OWNS_DOMAIN` assignment|
|**Hierarchy (BROADER_THAN)**|`INCLUDES_CONCEPT` auto-expansion|
|**HAS_SUBJECT_CONCEPT**|Derive in-scope entities|
|**ABOUT**|Agent corpus assignment (`TRAINS_ON`)|
|**Facet priority**|Multi-agent conflict resolution|
|**Evolution triggers**|Agent spawning/splitting decisions|

Perfect alignment! ✅

---

## 🔧 Implementation Roadmap

Based on this final architecture, here's the build sequence:

### Phase 1: Core Infrastructure (Week 1-2)

1. ✅ **SubjectConcept node schema** (defined in doc)
2. **Authority lookup module** (LCSH, FAST, LCC, Dewey APIs)
3. **Facet detection algorithm** (Section 5 rules)
4. **Node creation pipeline** (Section 9 workflow)

### Phase 2: Hierarchy & Mapping (Week 3-4)

5. **BROADER_THAN edge creation** (from LCSH hierarchy)
6. **Entity→Subject mapper** (Section 7 heuristics)
7. **Work→Subject mapper** (MARC 650/651/655 extraction)
8. **Confidence scoring** (catalog + Wikidata + temporal + spatial)

### Phase 3: Topic Spine (Week 5)

9. **Spine construction algorithm** (Section 10)
10. **Spine validation** (entity count thresholds)
11. **Agent domain assignment** (OWNS_DOMAIN from spine)

### Phase 4: Agent Integration (Week 6)

12. **Agent routing queries** (facet priority)
13. **Auto-expansion** (INCLUDES_CONCEPT from BROADER_THAN)
14. **Corpus assignment** (TRAINS_ON from ABOUT)

### Phase 5: Evolution & Maintenance (Week 7+)

15. **Drift detection** (Section 12.2)
16. **Splitting/merging** (Section 12.3-12.4)
17. **Orphan cleanup** (Section 12.6)
18. **Performance monitoring**

---

## 🚀 Next Immediate Steps

Given that the architecture is finalized, you need **implementation code**. I recommend this order:

### Option A: Start with Data (Bottom-Up)

1. **SubjectConcept ingestion pipeline** - Take your 85 index terms and create nodes
2. **Facet detection module** - Implement Section 5 rules
3. **Topic Spine builder** - Construct the spine for Roman history

### Option B: Start with Agents (Top-Down)

1. **Agent routing queries** - Implement Section 11 patterns
2. **Agent domain assignment** - Use Topic Spine to assign OWNS_DOMAIN
3. **Backfill SubjectConcepts** - Create the concepts agents need

### Option C: End-to-End Demo (Balanced)

1. **Create 10-20 SubjectConcepts** for Roman Republic
2. **Build mini Topic Spine** (3-5 concepts)
3. **Create 1-2 agents** scoped to spine
4. **Demonstrate routing** with sample queries

---

## 📝 My Recommendation

**Start with Option C (End-to-End Demo)**:

```python
# Demo Script Outline

# 1. Create Subject Concepts (Roman Republic domain)
concepts = [
    "Rome--History--Republic, 510-30 B.C.",  # spine
    "Rome--Army",                             # spine
    "Rome--Politics and government--510-30 B.C.",  # spine
    "Caesar, Julius, 100-44 B.C.",           # name facet
    "Battle of Actium, 31 B.C.",             # event facet
]

# 2. Assign facets
for concept in concepts:
    concept.facet = detect_facet(concept.heading)

# 3. Build mini spine (topical facet only)
spine = [c for c in concepts if c.facet == 'topical']

# 4. Create republican_rome_agent
agent = Agent(
    agent_id="republican_rome_agent",
    owns_domain=spine,
    facet_filter=["topical"],
    temporal_start="-510",
    temporal_end="-027"
)

# 5. Test routing
query = "Who was Julius Caesar?"
grounded = ground_query(query)  # → Caesar (Q1048) + name concept
agent = route_query(grounded)   # → republican_rome_agent
response = agent.answer(query)
```

This would demonstrate the complete Subject→Agent flow.

---

## ✅ Final Validation

The Subject Architecture document is:

- ✅ **Complete** - All sections present
- ✅ **Rigorous** - Clear rules and algorithms
- ✅ **Operational** - Implementation-ready
- ✅ **Integrated** - Aligned with Agent Architecture
- ✅ **Maintainable** - Evolution procedures defined
- ✅ **Production-grade** - No hand-waving, real specs

---

## 🎯 What Would You Like Next?

Choose one:

1. **SubjectConcept Ingestion Pipeline** (Python) - Process your 85 index terms
2. **Facet Detection Module** (Python) - Implement Section 5 rules
3. **Topic Spine Builder** (Cypher + Python) - Construct Roman history spine
4. **Agent Domain Assignment** (Cypher) - Link agents to spine concepts
5. **End-to-End Demo** (Python + Neo4j) - Complete workflow from terms to agents
6. **Entity→Subject Mapper** (Python) - Implement Section 7 heuristics

What's your priority?

