# SCA ↔ SFA Roles and Responsibilities - Discussion Framework

**Date:** February 15, 2026  
**Context:** Post-deployment of real agent spawning  
**Status:** ✅ MAJOR DECISIONS FINALIZED  

---

## Current State

**SubjectConceptAgent (SCA):**
- Seed agent for breadth-first exploration
- Spawns SubjectFacetAgents (SFAs) on-demand
- **Intelligent orchestrator** with selective claim routing
- Evaluates claims: Abstract concepts vs Concrete events
- Queues claims for multi-facet review ONLY when warranted
- Generates bridge claims connecting domains

**SubjectFacetAgents (SFAs):**
- Domain-specific experts (17 facets)
- Each has LLM integration with facet-specific system prompt
- **Training Phase:** Build domain ontologies independently (abstract concepts)
- **Perspective Phase:** Analyze concrete claims when queued by SCA
- Create Claim nodes (cipher-based) + FacetPerspective nodes
- Inherit all FacetAgent capabilities (Steps 1-5 methods)

**Claim Architecture:**
- **Claim = Star Pattern Subgraph** (cipher at center, perspectives radiating outward)
- **Cipher:** Content-addressable ID for automatic deduplication
- **FacetPerspective Nodes:** Facet-specific interpretations attached to claims
- **Selective Queue:** SCA routes claims based on relevance scoring, not automatically

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

### SCA Selective Claim Routing

**The Intelligence:** SCA doesn't queue ALL claims - it uses judgment to determine when cross-facet review adds value.

**Scenario 1: Abstract Domain Concept (No Queue)**
```
Political SFA creates: "Senate held legislative authority in Roman Republic"
  → Abstract political concept
  → Domain ontology building
  
SCA decision: Accept as-is
  → No cross-facet review needed
  → Pure political science concept
  → Don't queue to other SFAs
```

**Scenario 2: Concrete Historical Event (Selective Queue)**
```
Political SFA creates: "Caesar was appointed dictator in 49 BCE"
  → References: Caesar (concrete person), 49 BCE (concrete event)
  → Historical event, not abstract concept
  
SCA analyzes:
  → Caesar = military commander (military relevance)
  → Dictator office = economic control (economic relevance)
  → Concrete historical moment (multi-facet potential)
  
SCA decision: Queue for perspectives
  → Queue to Military SFA (Caesar's military role)
  → Queue to Economic SFA (treasury control)
  → Don't queue to Cultural/Religious (not relevant)
  
Military SFA receives queued claim:
  → Creates FacetPerspective: "Caesar commanded all Roman armies as dictator"
  
Economic SFA receives queued claim:
  → Creates FacetPerspective: "Caesar gained control of state treasury as dictator"
```

### Two Phases of SFA Work

**Phase 1: Training Mode (Independent)**
- SFA studies discipline (Political Science, Military History, etc.)
- Builds **subject ontology** for domain
- Creates claims about **abstract concepts** (governance structures, tactical theory)
- Works **independently** - no cross-facet review needed yet
- Example: Political SFA → "Senate held legislative authority", "Consulship rotated annually"

**Phase 2: Operational Mode (Selective Collaboration)**
- SFA encounters claims referencing **concrete entities/events**
- **SCA decides** if claim warrants cross-facet review
- If queued: SFA analyzes from its facet perspective
- Creates FacetPerspective nodes for selected claims

### Workflow Implication

```
Phase 1: Training (Independent)
  SCA:
  ├─ Spin up all SFAs
  ├─ Route discipline training data to each SFA
  └─ Collect claims from all SFAs
  
  SFAs:
  ├─ Study discipline independently
  ├─ Build domain ontology (abstract concepts)
  ├─ Create Claim nodes + FacetPerspectives
  └─ Return claims to SCA

Phase 2: Selective Review (SCA Intelligence)
  SCA analyzes each claim:
  ├─ Abstract domain concept? → Accept as-is (no queue)
  ├─ Concrete event/entity? → Evaluate multi-facet potential
  ├─ References multiple domains? → Queue for perspectives
  └─ Conflicts with existing claims? → Queue for synthesis
  
  SFAs (if queued):
  └─ Create FacetPerspective on selected claims only
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

### Claim Schema: Star Pattern with Cipher

**Key Architectural Point:** Claims are **star pattern subgraphs**, not isolated nodes.

#### Claim Cipher (Content-Addressable ID)

Each claim has a **cipher** - a unique hash computed from its content:

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

**Benefit:** Two SFAs discovering the SAME claim generate the SAME cipher → **automatic deduplication**

#### Claim Structure (Star Pattern)

```
                    ┌────────────┐
                    │    SFA     │
                    │  (creator) │
                    └─────┬──────┘
                          │
                    [MADE_CLAIM]
                          │
                          ▼
     ┌────────────────────────────────────┐
     │       :Claim (center node)         │
     │  cipher: "claim_abc123..."         │
     │  text: "Caesar appointed dictator" │
     │  status: "proposed"                │
     └────────────┬───────────────────────┘
                  │
       ┌──────────┼──────────┐
       │          │          │
  [PERSP_ON] [PERSP_ON] [PERSP_ON]
       │          │          │
       ▼          ▼          ▼
   (Facet     (Facet     (Facet
    Persp:    Persp:     Persp:
    Political) Military)  Economic)
```

#### FacetPerspective Nodes

**New Node Type:** `:FacetPerspective` - Represents a facet-specific interpretation of a claim

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
- ✅ **Single source of truth:** One Claim node (via cipher deduplication)
- ✅ **Multi-facet enrichment:** Multiple perspectives attached
- ✅ **Consensus calculation:** AVG(all perspective confidences)
- ✅ **Clear semantics:** Claim = base assertion, Perspective = facet interpretation

#### Discovery vs Perspective Mode (Updated)

**Discovery Mode:**
```
Political SFA reads text → discovers assertion
→ Creates Claim node (cipher: "claim_abc123...")
→ Creates FacetPerspective (political angle)
→ Returns claim cipher to SCA
```

**Perspective Mode:**
```
Military SFA receives queued claim (cipher: "claim_abc123...")
→ Analyzes from military perspective
→ Creates FacetPerspective (military angle)
→ Attaches to same claim via cipher
→ Returns perspective to SCA
```

**Result:**
- 1 Claim node (deduped via cipher)
- N FacetPerspective nodes (one per facet that analyzed it)

### Benefits & Challenges

**Benefits:**
1. **Efficient Collaboration:** Only concrete/multi-domain claims get cross-facet review
2. **Independent Learning:** SFAs build domain ontologies without interference
3. **Selective Enrichment:** Multi-facet analysis applied where it adds value
4. **SCA Intelligence:** Orchestrator makes informed routing decisions

**Challenges:**
1. **Routing Criteria:** How does SCA determine which claims warrant review?
2. **Abstract vs Concrete:** Drawing the line between domain concepts and reviewable events
3. **Relevance Detection:** Which facets should analyze which claims?
4. **Convergence:** When has a claim received sufficient perspectives?

---

## SFA Claim Queue Implementation

### Queue Structure (Cipher-Based)

```python
sfa_claim_queue = {
    'military': [
        {
            'claim_cipher': 'claim_abc123...',  # Content-addressable ID
            'claim_text': "Caesar was appointed dictator in 49 BCE",
            'source_facet': 'political',
            'entities': ['Q1048', 'Q7747'],  # Caesar, Roman Republic
            'existing_perspectives': ['political'],  # Already analyzed
            'status': 'pending'
        }
    ],
    'economic': [...],
    'cultural': [...]
}
```

### Queue Processing Logic (Selective)

**SCA (Evaluation Phase):**
```
1. Political SFA creates claim
   → Claim cipher: "claim_abc123..."
   → Claim text: "Caesar was appointed dictator in 49 BCE"
   → FacetPerspective: political
   
2. SCA receives claim cipher

3. SCA evaluates claim characteristics
   → Type: Concrete historical event (not abstract concept)
   → Entities: Caesar (Q1048), Dictator office, 49 BCE
   → Multi-domain potential: YES (military, economic implications)
   
4. SCA decision: Queue for selective review
   → Concrete event referencing specific person/date
   → Caesar = known military figure (military SFA relevant)
   → Dictator = state control (economic SFA relevant)
   → Cultural/Religious SFAs: Not relevant to this claim
   
5. SCA checks existing perspectives
   → Query: MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim {cipher: "claim_abc123..."})
   → Found: political (already exists)
   → Relevant facets missing: military, economic
   
6. SCA queues claim to RELEVANT facets only
   → Queue to military SFA (high relevance)
   → Queue to economic SFA (medium relevance)
   → Skip cultural/religious/scientific SFAs (not relevant)
```

**Contrast: Abstract Concept (No Queue):**
```
1. Political SFA creates claim
   → Claim cipher: "claim_xyz456..."
   → Claim text: "Senate held legislative authority in Roman Republic"
   → FacetPerspective: political
   
2. SCA receives claim cipher

3. SCA evaluates claim characteristics
   → Type: Abstract political concept (not concrete event)
   → Entities: Senate (institution), legislative authority (concept)
   → Multi-domain potential: NO (pure political science)
   
4. SCA decision: Accept as-is (NO QUEUE)
   → Abstract domain ontology concept
   → No concrete event requiring multiple perspectives
   → Let Political SFA own this claim exclusively
```

**SFA (Perspective Phase):**
```
1. Military SFA receives queued claim
   → claim_cipher: "claim_abc123..."
   → claim_text: "Caesar appointed dictator in 49 BCE"
   
2. Military SFA analyzes from military perspective
   → Interpretation: "Gained supreme military command"
   → Confidence: 0.90
   
3. Military SFA creates FacetPerspective
   → Links to claim via cipher
   → Returns perspective_id to SCA
   
4. SCA checks if more facets needed
   → Query existing perspectives again
   → If all relevant facets covered, remove from queue
```

### Deduplication via Cipher

**Scenario:** Two SFAs discover the same claim independently

```python
# Political SFA at 10:00 AM
claim_data_A = {
    "text": "Caesar appointed dictator 49 BCE",
    "subject": "Q1048",
    "source": "Plutarch"
}
cipher_A = Hash(claim_data_A)  # → "claim_abc123..."

# Military SFA at 10:05 AM (discovers same fact)
claim_data_B = {
    "text": "Caesar became dictator 49 BCE",  # Different wording
    "subject": "Q1048",
    "source": "Plutarch"  # Same source
}
cipher_B = Hash(claim_data_B)  # → "claim_abc123..." (SAME!)

# Neo4j check
MATCH (existing:Claim {cipher: $cipher_B})
RETURN existing

# If found: Attach new perspective instead of duplicate claim
MATCH (claim:Claim {cipher: "claim_abc123..."})
CREATE (persp:FacetPerspective {
  facet: "military",
  perspective_id: "persp_002"
})-[:PERSPECTIVE_ON]->(claim)

# Result: 1 Claim + 2 FacetPerspectives (political, military)
```

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
   - Route training data to SFAs (Discovery Mode)
   - Route claims to SFAs (Perspective Mode via queue)
   - Aggregate SFA results
   - Generate bridge claims (structural connections)
   - Synthesize multi-facet responses

3. **SFA Claim Queue Management (Selective)**
   - **Claim Evaluation:** When SFA creates claim, analyze characteristics:
     * Abstract domain concept? → Accept as-is (no queue)
     * Concrete entity/event? → Evaluate multi-facet potential
     * References multiple domains? → Queue to relevant SFAs only
     * Conflicts with existing claims? → Queue for synthesis
   - **Intelligent Routing:** Don't queue everything - use judgment
   - **Queue Prioritization:** Concrete events > abstract concepts for review
   - **Convergence Detection:** Stop when no new perspectives warranted
   - **Loop Prevention:** Track claim analysis history, prevent ping-pong

4. **Claim Management**
   - **Event Linking:** Determine if claims from different SFAs are:
     * Different claims about SAME event → Link to shared historical moment
     * Claims about DIFFERENT events → Keep as distinct moments
   - **Deduplication:** Prevent duplicate claims across facets
   - **Complementary Analysis:** Recognize facet perspectives are additive, not competitive
   - **Discovery vs Perspective:** Tag claims by creation mode

5. **Session Management**
   - Own master session_id
   - Track active SFAs
   - Coordinate approval workflows
   - Log orchestration decisions

6. **Boundary Definition**
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

1. **Training Mode (Independent Discipline Study)**
   - Receive discipline training data from SCA
   - Study domain **independently** (no cross-facet collaboration yet)
   - Build subject ontology for discipline (abstract concepts)
   - Create Claim nodes for domain concepts (with cipher)
   - Create FacetPerspective for own facet
   - Return claim ciphers to SCA
   - Examples: "Senate legislative authority", "Manipular tactics", "Agricultural economy"

2. **Perspective Mode (Selective Review - Only if Queued)**
   - Receive **selected** claim ciphers from SCA (not all claims, only those SCA deems worthy)
   - Analyze concrete claims from facet perspective
   - Create FacetPerspective nodes (attach to claim via cipher)
   - Return "No perspective" if claim not relevant to facet
   - Only triggered when SCA determines multi-facet review warranted

3. **Claim Structure Creation**
   - **Discovery:** Create Claim node + initial FacetPerspective
   - **Perspective:** Create FacetPerspective ONLY (claim already exists)
   - All perspectives link to claim via cipher
   - Cipher-based deduplication handled automatically

4. **Domain Expertise**
   - Load facet-specific system prompt
   - Trained at "field of study" or "academic discipline" level
   - Use LLM for facet-grounded reasoning
   - Validate claims against domain knowledge

5. **Query Execution**
   - Receive queries from SCA
   - Query Neo4j for facet-relevant nodes
   - Return results in standard format
   - Tag all outputs with facet

**NOT Responsible For:**
- ❌ Cross-domain orchestration
- ❌ Event-level claim linking (SCA's job)
- ❌ Agent spawning
- ❌ Session-level decisions
- ❌ Creating claims outside assigned facet
- ❌ Managing claim queue (SCA manages)

---

## Coordination Patterns

### Pattern 1: Discovery Mode (Training)

```
SCA provides training data: "Roman Republic" (Q7747)

SCA:
1. Spawn Political SFA, Military SFA, Economic SFA
2. Route training data to all SFAs
3. Each SFA analyzes independently

Political SFA (Training - Independent):
- Creates claims: "Senate held legislative power" (abstract concept)
- Creates claims: "Consuls elected annually" (abstract concept)
- Returns: 15 political claims
- SCA evaluation: All abstract political concepts → Accept as-is (no queue)

Military SFA (Training - Independent):
- Creates claims: "Legions organized into cohorts" (abstract concept)
- Creates claims: "Roman army used manipular tactics" (abstract concept)
- Returns: 12 military claims
- SCA evaluation: All abstract military concepts → Accept as-is (no queue)

Economic SFA (Training - Independent):
- Creates claims: "Roman economy based on agriculture" (abstract concept)
- Creates claims: "State controlled grain supply" (abstract concept)
- Returns: 10 economic claims
- SCA evaluation: All abstract economic concepts → Accept as-is (no queue)

Result: 37 independent domain ontology claims, NO cross-facet review needed
  → These are foundational concepts for each discipline
  → SFAs built their subject ontologies independently
  → No queue, no perspectives from other facets
```

### Pattern 2: Perspective Mode (Cipher-Based Deduplication)

```
Political SFA creates claim:
  → Claim node: cipher="claim_abc123...", text="Caesar appointed dictator 49 BCE"
  → FacetPerspective node: political angle
  → Returns claim cipher to SCA

SCA receives claim cipher "claim_abc123...":
1. Query existing perspectives:
   MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim {cipher: "claim_abc123..."})
   RETURN COLLECT(p.facet) AS existing_facets
   → Found: ['political']

2. Analyze claim entities:
   → Caesar (Q1048) = military relevance
   → Dictator office = economic relevance

3. Determine missing perspectives:
   → Need: military, economic
   → Already have: political

4. Queue claim cipher to:
   → Military SFA queue
   → Economic SFA queue

Military SFA (Perspective Mode):
  → Receives: claim_cipher="claim_abc123..."
  → Queries claim: MATCH (c:Claim {cipher: "claim_abc123..."}) RETURN c.text
  → Analyzes from military perspective
  → Creates FacetPerspective:
      facet="military"
      facet_claim_text="Caesar commanded all Roman armies as dictator"
      confidence=0.90
  → Links: (FacetPerspective)-[:PERSPECTIVE_ON]->(Claim {cipher: "claim_abc123..."})
  → Returns: perspective_id="persp_002"

Economic SFA (Perspective Mode):
  → Receives: claim_cipher="claim_abc123..."
  → Analyzes from economic perspective
  → Creates FacetPerspective:
      facet="economic"
      facet_claim_text="Caesar controlled state treasury as dictator"
      confidence=0.88
  → Links: (FacetPerspective)-[:PERSPECTIVE_ON]->(Claim {cipher: "claim_abc123..."})
  → Returns: perspective_id="persp_003"

Result Star Pattern:
                    (Claim: cipher="claim_abc123...")
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   [PERSP_ON]           [PERSP_ON]           [PERSP_ON]
        │                    │                    │
        ▼                    ▼                    ▼
   (Perspective:        (Perspective:        (Perspective:
    Political)          Military)            Economic)
    conf: 0.95          conf: 0.90           conf: 0.88

Consensus Score: AVG(0.95, 0.90, 0.88) = 0.91
```


### Pattern 3: Convergence Detection

```
Iteration 1:
  Political SFA: 15 discovery claims → Queue 30 perspective requests
  Military SFA: 12 discovery claims → Queue 24 perspective requests
  Economic SFA: 10 discovery claims → Queue 20 perspective requests
  Total queue: 74 items

Iteration 2:
  Process 74 queued claims
  → 45 perspective claims created
  → Queue 18 new perspective requests (diminishing)
  Total queue: 18 items

Iteration 3:
  Process 18 queued claims
  → 5 perspective claims created
  → Queue 2 new perspective requests
  Total queue: 2 items

Iteration 4:
  Process 2 queued claims
  → 0 perspective claims created (SFAs return "No perspective")
  → Queue 0 new requests
  
Convergence: Queue empty, stop processing
```

### Pattern 4: Shell Node Expansion

```
SCA creates shell node: Q191989 (murex) [status: shell]

Option A (SCA initiates):
1. SCA detects shell node needs expansion
2. SCA identifies relevant facet: scientific
3. SCA spawns ScientificSFA
4. SCA: "Expand Q191989 for me"
5. ScientificSFA expands shell → full node

Option B (SFA discovers):
1. ScientificSFA queries Neo4j
2. ScientificSFA encounters shell node Q191989
3. ScientificSFA: "Found shell node, expanding"
4. ScientificSFA expands shell → full node
5. ScientificSFA reports back to SCA
```

---

## ✅ Finalized Roles & Responsibilities

| Responsibility | SCA | SFA |
|----------------|-----|-----|
| **Discovery** | ✅ Breadth (un-faceted) | Depth (facet-specific) |
| **Spawning** | ✅ Spawns SFAs | ❌ Cannot spawn |
| **Training Phase** | Routes discipline data | ✅ Independent study (no queue) |
| **Claim Evaluation** | ✅ Abstract vs Concrete | Creates claims from facet lens |
| **Claim Creation** | Bridge/event claims | ✅ Claim + FacetPerspective |
| **Queue Management** | ✅ Selective routing (intelligent) | Processes selected claims only |
| **Routing Criteria** | ✅ Multi-domain potential | N/A |
| **Perspective Creation** | N/A | ✅ When queued by SCA |
| **Domain Boundaries** | Assigns domains | ✅ Stays within facet |
| **Ontology** | ✅ Discovers & proposes | ✅ Builds domain ontology |
| **Neo4j Access** | ✅ Queries | ✅ Queries |
| **Session** | ✅ Owns master session | Shares session_id |
| **Orchestration** | ✅ Intelligent aggregation | ❌ No orchestration |
| **Training Scope** | N/A | Field of study level (broad) |

---

## SCA Routing Criteria (Critical Design Decision)

### How SCA Determines Which Claims Warrant Cross-Facet Review

**Key Question:** When should SCA queue a claim for multi-facet analysis?

#### Criterion 1: Abstract vs Concrete

**Abstract Domain Concepts → NO QUEUE**
- Theoretical frameworks (e.g., "Senate held legislative authority")
- Discipline-specific methods (e.g., "Manipular tactics")
- General principles (e.g., "Agricultural economy base")
- Domain ontology building
- **Action:** Accept claim as-is, no cross-facet review needed

**Concrete Events/Entities → EVALUATE FOR QUEUE**
- Specific historical events (e.g., "Caesar crossed Rubicon")
- Named individuals with roles (e.g., "Caesar appointed dictator")
- Dated occurrences (e.g., "49 BCE")
- Geographic locations in context (e.g., "Rubicon River boundary")
- **Action:** Evaluate multi-domain potential

#### Criterion 2: Multi-Domain Relevance Scoring

When claim is concrete, SCA scores relevance to each facet:

**High Relevance (Score: 0.8-1.0) → Queue to SFA**
- Entity is central to facet domain (e.g., Caesar = military commander)
- Event has direct facet implications (e.g., dictatorship = state control)
- Claim text contains facet-specific terminology

**Medium Relevance (Score: 0.5-0.7) → Queue to SFA**
- Entity has secondary connection to facet
- Event has indirect facet implications
- Potential for facet-specific insight

**Low Relevance (Score: 0.0-0.4) → Do NOT queue**
- Entity not related to facet domain
- Event has no facet implications
- No facet-specific insight likely

**Example: "Caesar was appointed dictator in 49 BCE"**
```
Political SFA (creator): 1.0 (created the claim)
Military SFA: 0.9 (Caesar = commander, dictator = supreme command)
Economic SFA: 0.8 (dictator = treasury control, state finances)
Cultural SFA: 0.3 (minor cultural impact, not primary)
Religious SFA: 0.2 (no significant religious dimension)
Scientific SFA: 0.1 (irrelevant to scientific domain)

SCA Decision:
→ Queue to: Military (0.9), Economic (0.8)
→ Skip: Cultural (0.3), Religious (0.2), Scientific (0.1)
```

#### Criterion 3: Entity Type Detection

**QID Pattern Analysis:**
```python
def get_entity_type(qid):
    # Query Wikidata for P31 (instance of)
    entity_type = wikidata.query(f"SELECT ?type WHERE {{ wd:{qid} wdt:P31 ?type }}")
    
    # Map to facet relevance
    if entity_type in [Q5, Q10648343]:  # Human, historical figure
        return {
            'military': check_military_roles(qid),
            'political': check_political_roles(qid),
            'cultural': check_cultural_impact(qid),
            ...
        }
```

**Example Entity Types:**
- **Q5 (Human):** Political, Military, Cultural potential
- **Q198 (War):** Military, Political, Economic potential
- **Q216353 (Battle):** Military, Geographic potential
- **Q7275 (State):** Political, Economic potential
- **Q8142 (Currency):** Economic, Political potential

#### Criterion 4: Conflict Detection

**Claim Conflicts with Existing Knowledge → Queue for Synthesis**
- Date discrepancy: "Caesar dictator 49 BCE" vs "Caesar dictator 48 BCE"
- Attribute conflict: Different sources claim different properties
- Relationship dispute: Competing relationship assertions
- **Action:** Queue to SynthesisAgent + relevant SFAs

#### Criterion 5: Existing Perspectives Check

Before queuing, SCA checks what perspectives already exist:

```cypher
MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim {cipher: $cipher})
RETURN COLLECT(p.facet) AS existing_facets

// Only queue to facets NOT in existing_facets
```

**Prevents:**
- Duplicate perspective requests
- Wasted SFA effort
- Ping-pong between SFAs

### Implementation Pseudocode

```python
def evaluate_claim_for_queue(claim: Claim, source_facet: str) -> Dict[str, float]:
    """
    Evaluate which SFAs should analyze this claim
    
    Returns: Dict of facet -> relevance_score
    """
    # Step 1: Check if abstract concept
    if is_abstract_concept(claim):
        return {}  # No queue
    
    # Step 2: Extract entities from claim
    entities = extract_entities(claim.text)
    
    # Step 3: Score relevance to each facet
    relevance_scores = {}
    for facet in ALL_FACETS:
        if facet == source_facet:
            continue  # Skip source facet (already has perspective)
        
        score = 0.0
        for entity in entities:
            entity_type = get_entity_type(entity.qid)
            score += calculate_relevance(entity_type, facet)
        
        relevance_scores[facet] = score / len(entities)
    
    # Step 4: Check existing perspectives
    existing_facets = get_existing_perspectives(claim.cipher)
    
    # Step 5: Filter by threshold and existing
    queue_targets = {
        facet: score 
        for facet, score in relevance_scores.items()
        if score >= 0.5 and facet not in existing_facets
    }
    
    return queue_targets
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
2. ✅ **Decided:** SFAs create facet-specific claims ONLY (no cross-domain)
3. ✅ **Decided:** Claims use cipher-based deduplication (star pattern)
4. ✅ **Decided:** FacetPerspective nodes for multi-facet enrichment
5. ✅ **Decided:** Exploratory scope - get them all
6. ✅ **Decided:** SFA Training Phase - independent discipline study
   - Training Mode: SFAs work independently, build domain ontologies (abstract concepts)
   - SCA accepts training claims as-is (no automatic queuing)
7. ✅ **Decided:** SCA Selective Claim Queue - intelligent routing
   - SCA evaluates claim characteristics (abstract vs concrete, multi-domain potential)
   - Only queues claims that warrant cross-facet review
   - Perspective Mode: SFAs create FacetPerspective only when SCA requests it
   - Efficient collaboration, not automatic routing
8. ✅ **Documented:** SCA routing criteria (5 criteria framework)
   - Abstract vs Concrete detection
   - Multi-domain relevance scoring
   - Entity type detection
   - Conflict detection
   - Existing perspectives check
9. **Document** FacetPerspective node schema (add to NODE_TYPE_SCHEMAS.md)
10. **Implement** SCA claim evaluation logic (abstract vs concrete, multi-domain detection)
11. **Implement** FacetPerspective creation in SFA (both training and perspective modes)
12. **Implement** Cipher-based claim deduplication in SFA/SCA
13. **Implement** SCA selective queue logic (intelligent routing, not automatic)
14. **Test** training phase: Independent domain ontology building (no cross-facet review)
15. **Test** operational phase: Selective multi-facet review (Caesar dictator example: 1 claim + 3 perspectives)

---

**Status:** ✅ ARCHITECTURE FINALIZED - Major decisions complete, implementation ready
