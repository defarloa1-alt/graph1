# SCA ↔ SFA Roles and Responsibilities - Discussion Framework

**Date:** February 15, 2026  
**Context:** Post-deployment of real agent spawning  
**Status:** 🔄 DISCUSSION DRAFT  

---

## Current State

**SubjectConceptAgent (SCA):**
- Seed agent for breadth-first exploration
- Spawns SubjectFacetAgents (SFAs) on-demand
- Orchestrates cross-domain queries
- Generates bridge claims connecting domains

**SubjectFacetAgents (SFAs):**
- Domain-specific experts (17 facets)
- Each has LLM integration with facet-specific system prompt
- Inherit all FacetAgent capabilities (Steps 1-5 methods)
- Can query Neo4j, validate claims, generate claims

---

## Key Questions to Resolve

### 1. WHO owns the ontology discovery?

**✅ DECISION: Option A - SCA owns, SFAs consume**

- SCA discovers nodes/edges (Phase 1: un-faceted)
- SCA proposes ontology → approval → passes to SFAs
- SFAs analyze approved ontology from their perspective (Phase 2)

**Rationale:**
- SCA provides breadth-first exploration
- Ontology approval happens once (not per-facet)
- SFAs receive curated starting point for facet-specific analysis

---

### 2. WHO creates claims?

**✅ DECISION: SFAs create all claims**

- SFAs read raw data (Wikipedia, Wikidata)
- SFAs extract claims from their facet perspective
- SCA manages claim relationships (same claim vs different claims)

**SCA's Role in Claim Management:**
- **Perspective Analysis:** Determine if multiple SFAs are describing:
  * **Same claim, different perspectives** → Link as facet variance
  * **Different claims entirely** → Keep as distinct assertions
- **Bridge Claims:** SCA creates structural/cross-domain connections
- **Deduplication:** Prevent duplicate claims across facets

**Important Nuance - Facet-Specific Claims:**
SFAs trained at the "field of study" or "academic discipline" level create claims **within their facet perspective only**.

**Example:** "Caesar crossed the Rubicon" - SAME EVENT, different facet claims

- **Political Science SFA** analyzing the event:
  - Creates claim: "Caesar challenged Senate authority"
  - Creates claim: "Rubicon crossing violated Roman law (armies forbidden in Italy)"
  - Does NOT create: "Legio XIII marched into Italy" (that's military domain)
  - Perspective: Authority/governance angle
  
- **Military History SFA** analyzing the SAME event:
  - Creates claim: "Legio XIII entered Italy from Gaul"
  - Creates claim: "Caesar initiated military campaign against Pompey"
  - Does NOT create: "Caesar defied Senate" (that's political domain)
  - Perspective: Troop movement/strategic angle
  
- **SCA's job:** Recognize these are **different claims about the SAME event**
  - Not duplicates, but complementary perspectives
  - Link claims to the same historical moment (Rubicon Crossing, 49 BCE)
  - Both claims are TRUE, from different facet lenses

---

### 3. WHO manages agent lifecycle?

**Option A: SCA is sole spawner**
- Only SCA can spawn SFAs
- SFAs are ephemeral (exist during query only)
- SCA tracks active agents in memory

**Option B: Persistent SFA instances**
- SFAs spawn once, persist indefinitely
- SCA retrieves existing SFAs from Agent registry
- SFAs have long-running sessions

**Option C: Hybrid**
- SCA spawns SFAs for sessions
- Agent nodes in Neo4j track lifecycle
- SFAs can be reactivated across sessions

**Current Implementation:** Option A (SCA spawns, ephemeral)

---

### 4. WHO owns domain boundaries?

**Option A: SCA defines, SFAs enforce**
- SCA assigns SubjectConcept → SFA mappings
- SFAs only work within assigned domain
- Strict boundaries, no overlap

**Option B: SFAs define their own boundaries**
- Each SFA declares what SubjectConcepts it covers
- SCA routes based on SFA declarations
- Boundaries can overlap (multi-facet concepts)

**Option C: Dynamic negotiation**
- SCA proposes domains
- SFAs accept/reject/counter-propose
- Boundaries negotiated per session

**Current Implementation:** Not defined (SCA passes query, SFA decide relevance)

---

### 5. WHO handles conflicts?

**Scenario:** Political SFA says "Caesar was a dictator" (confidence: 0.95)  
            Military SFA says "Caesar was a general" (confidence: 0.93)

**Option A: SCA arbitrates**
- SFAs report conflicts to SCA
- SCA decides resolution (accept both, merge, priority)
- SCA creates Divergence nodes

**Option B: No arbitration (coexistence)**
- Both claims exist independently
- Claims tagged with facet perspective
- Users see multiple perspectives

**Option C: SFAs negotiate**
- SFAs communicate to resolve conflicts
- SCA only facilitates negotiation
- Consensus or divergence recorded

**Current Implementation:** Option B (both claims coexist with facet tags)

---

### 6. WHO queries Neo4j?

**Option A: SFAs query directly**
- Each SFA has Neo4j driver access
- SFAs construct Cypher queries
- SCA aggregates results

**Option B: SCA queries, SFAs analyze**
- SCA executes all Neo4j queries
- SCA passes results to SFAs for analysis
- SFAs don't touch database directly

**Option C: Shared query interface**
- Common query API both use
- Results cached by SCA
- SFAs can request additional queries

**Current Implementation:** Option A (SFAs have driver, query directly)

---

### 7. WHO trains SFAs?

**Option A: SCA trains SFAs during Initialize**
- SCA runs Initialize Mode
- SCA invokes each SFA's execute_training_mode()
- SFAs learn their domain under SCA guidance

**Option B: SFAs self-train**
- Each SFA runs own Initialize + Training independently
- SCA not involved in training
- SFAs report readiness to SCA

**Option C: External training**
- Human/external process trains SFAs
- Training data prepared separately
- SCA spawns already-trained SFAs

**Current Implementation:** Not defined (training not implemented yet)

---

### 8. WHO owns the session?

**Option A: SCA owns session**
- One session_id for entire SCA workflow
- All SFAs share same session_id
- Session tracks SCA + SFA activity

**Option B: Each SFA has own session**
- SCA has master session_id
- Each SFA has child session_id
- Hierarchical session tracking

**Option C: No sessions**
- Stateless agents
- Each query independent
- No session continuity

**Current Implementation:** Option A (session_id owned by SCA/FacetAgent)

---

## ✅ Key Decisions Summary

### 1. Ontology Discovery
**SCA owns, SFAs consume** - SCA does Phase 1 un-faceted exploration, proposes ontology, SFAs analyze in Phase 2

### 2. Claim Creation
**SFAs create facet-specific claims ONLY** - Each SFA stays within its domain perspective
- Political SFA creates political claims
- Military SFA creates military claims  
- NO cross-domain claim creation by individual SFAs

### 3. SCA's Claim Management Role
**Event Linking** - SCA determines if claims from different SFAs are:
- **Different claims about SAME event** → Link claims to shared historical moment
- **Claims about DIFFERENT events** → Keep as distinct historical moments

### 4. Exploratory Scope
**Get them all** - No prioritization of early vs late SubjectConcepts, all explored equally

---

## Multi-Facet Claim Analysis (Key Insight)

### Two Phases of Claim Creation

**Phase 1: Training Mode - Independent Discovery**
- Each SFA starts with its high-level discipline (field of study)
- SFAs create claims independently during training
- Claims likely do NOT overlap initially (different domains)
- Example:
  * Political SFA training on "Roman Republic" → Creates political structure claims
  * Military SFA training on "Roman Legions" → Creates military organization claims
  * These are independent, non-overlapping claims

**Phase 2: Operational Mode - Recursive Analysis**
- SFAs discover claims that reference entities from other facets
- **Recursive Issue:** Each new claim potentially needs multi-facet analysis
- Creates an **SFA Claim Queue** - claims awaiting facet perspective analysis

### The SFA Claim Queue Problem

**Scenario:**
```
Political SFA creates: "Caesar was appointed dictator in 49 BCE"
  → References: Caesar (person), Roman Republic (polity), dictator (office)
  
SCA recognizes: This claim has entities relevant to OTHER facets
  → Caesar = military commander (Military SFA should analyze)
  → Dictator office = economic impact (Economic SFA should analyze)
  → Creates entries in SFA Claim Queue
  
Military SFA receives queued claim: "Caesar was appointed dictator in 49 BCE"
  → Analyzes from military perspective
  → Creates NEW claim: "Caesar commanded all Roman armies as dictator"
  
Economic SFA receives queued claim: "Caesar was appointed dictator in 49 BCE"
  → Analyzes from economic perspective  
  → Creates NEW claim: "Caesar gained control of state treasury as dictator"
```

### Two Types of SFA Work

**1. Discovery Claims (Proactive)**
- SFA discovers new information from training data
- Creates claims from primary facet perspective
- Drives initial knowledge base population

**2. Perspective Claims (Reactive)**
- SFA receives existing claim from queue
- Analyzes claim from its facet perspective
- Creates complementary claims about same entities/events

### Workflow Implication

```
SFA Responsibilities:
├─ Discovery Mode (Training)
│  └─ Create claims from training data (Wikipedia, Wikidata)
│
└─ Queue Processing Mode (Operational)
   └─ Analyze claims from other SFAs for facet-specific insights

SCA Responsibilities:
├─ Route training data to SFAs (Discovery)
├─ Collect discovery claims from all SFAs
├─ Analyze claims for multi-facet potential
├─ Queue claims to relevant SFAs (Perspective analysis)
└─ Link resulting claims to entities/events
```

### Recursive Termination

**Question:** When does the queue stop growing?

**Answer:** When SFAs have no new perspectives to add

**Example:**
```
Iteration 1:
  Political SFA: "Caesar crossed Rubicon" → Queue for Military, Geographic
  
Iteration 2:
  Military SFA: "Legio XIII entered Italy" → Already covered, no new queue
  Geographic SFA: "Rubicon river boundary violated" → Already covered, no new queue
  
Termination: No new facet perspectives discovered
```

### Benefits & Challenges

**Benefits:**
1. **Complete Multi-Facet Coverage:** Every claim analyzed from all relevant perspectives
2. **Emergent Connections:** SFAs discover cross-domain relationships organically
3. **Progressive Enrichment:** Knowledge base grows richer with each iteration

**Challenges:**
1. **Queue Management:** SCA must track which claims need which facet analyses
2. **Avoid Infinite Loops:** Prevent claims from ping-ponging between SFAs
3. **Prioritization:** Which queued claims to process first?
4. **Convergence:** How to detect when multi-facet analysis is "complete"?

---

## SFA Claim Queue Implementation

### Queue Structure

```python
sfa_claim_queue = {
    'military': [
        {
            'claim_id': 'CLM_001',
            'claim_text': "Caesar was appointed dictator in 49 BCE",
            'source_facet': 'political',
            'entities': ['Q1048', 'Q7747'],  # Caesar, Roman Republic
            'status': 'pending'
        }
    ],
    'economic': [...],
    'cultural': [...]
}
```

### Queue Processing Logic

**SCA:**
1. SFA creates claim → SCA receives
2. SCA analyzes claim entities
3. SCA determines: Which OTHER facets should analyze this?
4. SCA adds claim to relevant SFA queues
5. SCA monitors queue depth, prioritizes

**SFA:**
1. Process Discovery queue (training data)
2. Process Perspective queue (claims from other SFAs)
3. Return new claims to SCA
4. SCA repeats analysis for new claims

### Convergence Detection

**Option A: Fixed Iterations**
- Process N rounds of perspective analysis
- Stop after N iterations regardless

**Option B: Queue Empty**
- Continue until all SFA queues empty
- Risk: May never converge if SFAs keep generating perspectives

**Option C: Diminishing Returns**
- Track new claims per iteration
- Stop when new claims < threshold

**Option D: Explicit "No Perspective" Response**
- SFAs can return "No additional perspective from my facet"
- Stop when all SFAs return no-perspective for queued claims

---

## Proposed Roles & Responsibilities

### SubjectConceptAgent (SCA)

**PRIMARY ROLE:** Seed agent & orchestrator

**Responsibilities:**
1. **Un-faceted Exploration (Phase 1)**
   - Anchor on initial QID
   - Traverse hierarchies (P31/P279/P361)
   - Discover backlinks
   - Create shell nodes (un-faceted)
   - Propose ontology

2. **Orchestration**
   - Spawn SFAs on-demand
   - Route queries to appropriate SFAs
   - Aggregate SFA results
   - Generate bridge claims (structural connections)
   - Synthesize multi-facet responses

3. **Claim Management**
   - **Event Linking:** Determine if claims from different SFAs are:
     * Different claims about SAME event → Link to shared historical moment
     * Claims about DIFFERENT events → Keep as distinct moments
   - **Deduplication:** Prevent duplicate claims across facets
   - **Complementary Analysis:** Recognize facet perspectives are additive, not competitive

4. **Session Management**
   - Own master session_id
   - Track active SFAs
   - Coordinate approval workflows
   - Log orchestration decisions

5. **Boundary Definition**
   - Assign initial domains to SFAs
   - Define SubjectConcept → SFA mappings
   - Ensure each facet analyzes from its perspective only

**NOT Responsible For:**
- ❌ Facet-specific claim creation
- ❌ Domain expertise / deep facet analysis
- ❌ Determining what claims belong in which facet

---

### SubjectFacetAgent (SFA)

**PRIMARY ROLE:** Domain expert

**Responsibilities:**
1. **Facet-Specific Analysis (Phase 2)**
   - Receive ontology from SCA
   - Analyze from facet perspective ONLY
   - Extract facet-relevant insights
   - Generate claims within assigned facet

2. **Claim Creation**
   - Create claims from facet perspective ONLY
   - **Stay within facet domain** (no cross-domain claims)
   - Tag all claims with facet origin
   - Assign facet-specific confidence scores
   - Return claims to SCA for event linking

3. **Domain Expertise**
   - Load facet-specific system prompt
   - Trained at "field of study" or "academic discipline" level
   - Use LLM for facet-grounded reasoning
   - Validate claims against domain knowledge

4. **Query Execution**
   - Receive queries from SCA
   - Query Neo4j for facet-relevant nodes
   - Return results in standard format
   - Tag all outputs with facet

5. **Training (Future)**
   - Execute training mode for assigned domain
   - Learn domain patterns from Wikipedia + Wikidata
   - Build domain-specific claim templates
   - Training scope: Field of study level (broad)

**NOT Responsible For:**
- ❌ Cross-domain orchestration
- ❌ Event-level claim linking (SCA's job)
- ❌ Agent spawning
- ❌ Session-level decisions
- ❌ Creating claims outside assigned facet

---

## Coordination Patterns

### Pattern 1: Query Routing

```
User query: "How did environmental disasters affect military campaigns?"

SCA:
1. Classify facets → [environmental, military]
2. Spawn EnvironmentalSFA, MilitarySFA
3. Route query to both SFAs
4. Aggregate results
5. Generate bridge claims (disaster → campaign)
6. Synthesize answer

Environmental SFA:
- Analyze disasters from environmental perspective
- Return: volcanic eruptions, earthquakes, floods
- Facet: environmental

Military SFA:
- Analyze campaigns from military perspective
- Return: campaigns, battles, strategic decisions
- Facet: military
```

### Pattern 2: Facet-by-Facet Analysis

```
SCA discovers: Q189108 (Tyrian purple)

SCA:
1. Phase 1: Discov✅ Breadth (un-faceted) | Depth (facet-specific) |
| **Spawning** | ✅ Spawns SFAs | ❌ Cannot spawn |
| **Query Routing** | ✅ Route/event claims | ✅ Facet-specific claims ONLY |
| **Claim Management** | ✅ Links claims to events | Tags claims with facet |
| **Domain Boundaries** | Assigns domains | ✅ Stays within facet
| **Domain Boundaries** | Assigns domains | ⚠️ Can create cross-domain claims |
| **Ontology** | ✅ Discovers & proposes | Analyzes & enriches |
| **Neo4j Access** | ✅ Queries | ✅ Queries |
| **Session** | ✅ Owns master session | Shares session_id |
| **Orchestration** | ✅ Aggregates SFAs | ❌ No orchestration |
| **Training Scope** | N/A | Field of study level (broad)
### Pattern 3: Shell Node Expansion

```
SCA creates shell node: Q191989 (murex) [status: shell]
✅ **Decided:** SCA owns ontology, SFAs consume
2. ✅ **Decided:** SFAs create all claims (including cross-domain)
3. ✅ **Decided:** SCA manages claim perspectives (same vs different)
4. 🔄 **Decide:** Remaining open questions (3-8)
5. **Document** final SCA ↔ SFA contract
6. **Implement** claim perspective analysis
7. **Test** with multi-facet queries

---

**Status:** 🔄 IN PROGRESS - Key decisions made, implementation next
1. ScientificSFA queries Neo4j
2. ScientificSFA encounters shell node Q191989
3. ScientificSFA: "Found shell node, expanding"
4. ScientificSFA expands shell → full node
5. ScientificSFA reports back to SCA
```

---

## Open Design Questions

### 1. Should SFAs be stateful or stateless?

**Stateful:**
- SFA remembers previous queries
- Builds up domain knowledge over time
- Can reference past analysis

**Stateless:**
- Each query independent
- No memory between invocations
- Simpler, more scalable

### 2. Can SFAs spawn other SFAs?

**Allow:**
- Political SFA discovers economic connection
- Political SFA spawns EconomicSFA to analyze
- Recursive agent coordination

**Forbid:**
- Only SCA can spawn SFAs
- SFAs report needs to SCA
- SCA decides spawning

### 3. How do SFAs handle out-of-domain queries?

**Reject:**
- SFA returns "NOT MY DOMAIN"
- SCA re-routes to correct SFA

**Attempt:**
- SFA tries best effort analysis
- Lower confidence score
- Tags as "out-of-domain"

### 4. What's the SFA training workflow?

**Option A: Training Mode (already implemented)**
- Each SFA runs execute_training_mode()
- Learns from Wikidata + Wikipedia
- Generates facet-specific claims

**Option B: Fine-tuning**
- Fine-tune LLM for each facet
- Domain-specific model weights
- More expensive, better performance

**Option C: Prompt engineering only**
- System prompt = entire training
- No additional learning
- Simpler, cheaper

---

## ✅ Finalized Roles & Responsibilities

| Responsibility | SCA | SFA |
|----------------|-----|-----|
| **Discovery** | ✅ Breadth (un-faceted) | Depth (facet-specific) |
| **Spawning** | ✅ Spawns SFAs | ❌ Cannot spawn |
| **Query Routing** | ✅ Routes queries | ❌ Receives queries |
| **Claim Creation** | Bridge/event claims | ✅ Facet-specific claims ONLY |
| **Claim Management** | ✅ Links claims to events | Tags claims with facet |
| **Domain Boundaries** | Assigns domains | ✅ Stays within facet |
| **Ontology** | ✅ Discovers & proposes | Analyzes & enriches |
| **Neo4j Access** | ✅ Queries | ✅ Queries |
| **Session** | ✅ Owns master session | Shares session_id |
| **Orchestration** | ✅ Aggregates SFAs | ❌ No orchestration |
| **Training Scope** | N/A | Field of study level (broad) |
| **Exploration** | ✅ Get them all (exploratory) | Analyzes assigned portion |

---

## Next Steps

1. ✅ **Decided:** SCA owns ontology, SFAs consume
2. ✅ **Decided:** SFAs create facet-specific claims ONLY
3. ✅ **Decided:** SCA manages event linking (different claims about same event)
4. ✅ **Decided:** Exploratory scope - get them all
5. 🔄 **Decide:** Remaining open questions (3-8: lifecycle, boundaries, conflicts, etc.)
6. **Implement** event linking logic in SCA
7. **Test** with multi-facet queries (Rubicon crossing example)

---

**Status:** 🔄 IN PROGRESS - Key decisions finalized, implementation planning next
