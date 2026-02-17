# Claim Workflow Models - Comparison

**Date:** February 15, 2026  
**Context:** Comparing two approaches to SFA claim creation  

## 2026-02-17 Alignment Note (Canonical Direction)

This file remains useful for historical model comparison, but canonical direction is now:

- Claim edge reification in canonical runtime:
  - `(:Claim)-[:ASSERTS_EDGE]->(:ProposedEdge)-[:FROM]->(source)`
  - `(:ProposedEdge)-[:TO]->(target)`
- Facet evaluation topology:
  - `(:Claim)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun)-[:HAS_FACET_ASSESSMENT]->(:FacetAssessment)`
- Scaffold/bootstrap edge persistence uses scaffold-only labels:
  - `:ScaffoldNode` and `:ScaffoldEdge` (not canonical `:ProposedEdge`)

Primary source of truth remains:
- `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

---

## Current Claim Schema (Existing Architecture)

### Claim as Star Pattern Subgraph

From existing architecture docs: **A claim is NOT a single node - it's a complete evidence structure (subgraph cluster)**

```
                    ┌─────────────┐
                    │    Agent    │
                    │  (creator)  │
                    └──────┬──────┘
                           │
                    [MADE_CLAIM]
                           │
                           ▼
    ┌───────────────────────────────────────────┐
    │                                           │
    │          :Claim (center node)             │
    │  cipher: "claim_abc123..."                │
    │  claim_id: "claim_00123"                  │
    │  text: "Caesar crossed Rubicon..."        │
    │  status: "proposed"                       │
    │  confidence: 0.85                         │
    │                                           │
    └───────────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    [SUBJECT_OF]    [PROPOSES]     [HAS_TRACE]
        │               │               │
        ▼               ▼               ▼
    (Caesar)      (ProposedEdge)  (ReasoningTrace)
    Q1048         CROSSED         
                      │
                      ▼
                  (Rubicon)
                  Q186901
```

### Cipher = Content-Addressable ID

```python
claim_cipher = Hash(
    source_work_qid +           # Where claim came from
    passage_text_hash +          # Exact text
    subject_entity_qid +         # Who/what it's about
    object_entity_qid +          # Related entity
    relationship_type +          # What relationship
    temporal_data +              # When
    confidence_score +           # How confident
    extractor_agent_id +         # Who extracted it
    extraction_timestamp         # When extracted
)
```

**Key Point:** Two agents extracting the SAME claim generate the SAME cipher → automatic deduplication

---

## Model A: Independent SFA Claims with Selective Queue (Current Model)

### Workflow - Training Phase

```
1. Political SFA reads discipline training data
   → Creates claim: "Senate held legislative authority" (abstract concept)
   → Returns to SCA
   → SCA decision: Abstract political concept → Accept as-is (NO QUEUE)

2. Military SFA reads discipline training data
   → Creates claim: "Legions organized into cohorts" (abstract concept)
   → Returns to SCA
   → SCA decision: Abstract military concept → Accept as-is (NO QUEUE)

Result: Independent domain ontologies, no cross-facet review
```

### Workflow - Operational Phase (Concrete Claims)

```
1. Political SFA encounters concrete event
   → Creates claim: "Caesar was appointed dictator in 49 BCE"
   → Returns to SCA

2. SCA evaluates claim
   → Type: Concrete historical event (not abstract)
   → Entities: Caesar (military relevant), Dictator (economic relevant)
   → Decision: Multi-facet potential HIGH
   → Selectively queues to Military SFA, Economic SFA only

3. Military SFA processes queued claim
   → Creates FacetPerspective: "Caesar commanded all armies as dictator"
   → Returns to SCA

4. Economic SFA processes queued claim
   → Creates FacetPerspective: "Caesar controlled treasury as dictator"
   → Returns to SCA

Result: 1 Claim + 3 FacetPerspectives (political, military, economic)
```

### Claim Structure

**Claim 1 (Political):**
```
cipher: "claim_pol_abc123..."
subject: Caesar (Q1048)
relationship: APPOINTED_TO
object: Dictator (Q7747)
facet: political
```

**Claim 2 (Military):**
```
cipher: "claim_mil_def456..."
subject: Caesar (Q1048)
relationship: COMMANDED
object: Roman Armies
facet: military
```

**Claim 3 (Economic):**
```
cipher: "claim_eco_ghi789..."
subject: Caesar (Q1048)
relationship: CONTROLLED
object: State Treasury
facet: economic
```

### Linking

SCA creates linking structure:
```
(Claim1)-[:ABOUT_SAME_EVENT]->(Event: "Caesar's Dictatorship 49 BCE")
(Claim2)-[:ABOUT_SAME_EVENT]->(Event: "Caesar's Dictatorship 49 BCE")
(Claim3)-[:ABOUT_SAME_EVENT]->(Event: "Caesar's Dictatorship 49 BCE")
```

### Pros
- ✅ Each SFA creates claims independently (parallel processing)
- ✅ Claims have different confidence scores per facet
- ✅ Clear facet attribution

### Cons
- ❌ 3 separate claim nodes to manage
- ❌ SCA must link claims post-hoc
- ❌ More complex graph structure

---

## Model B: Proposed Claim + SFA Responses (Alternative)

### Workflow

```
1. SCA reads text: "In 49 BCE, Caesar became dictator"
   → Proposes claim (extracts base assertion)
   → Creates Claim node with cipher

2. SCA routes claim to ALL relevant SFAs
   → Political SFA
   → Military SFA
   → Economic SFA

3. Each SFA responds with perspective
   → Political: Creates Review node (political interpretation)
   → Military: Creates Review node (military implications)
   → Economic: Creates Review node (economic impacts)

Result: 1 claim + 3 facet-specific reviews
```

### Claim Structure

**Central Claim (proposed by SCA):**
```
cipher: "claim_xyz789..."
text: "Caesar was appointed dictator in 49 BCE"
subject: Caesar (Q1048)
relationship: APPOINTED_TO
object: Dictator office
status: "proposed"
source: Training text passage
```

**Political SFA Response:**
```
(Review:PoliticalPerspective {
  review_id: "rev_pol_001",
  facet: "political",
  confidence: 0.95,
  interpretation: "Senate authority challenged",
  verdict: "support"
})-[:REVIEWS]->(Claim)
```

**Military SFA Response:**
```
(Review:MilitaryPerspective {
  review_id: "rev_mil_001", 
  facet: "military",
  confidence: 0.90,
  interpretation: "Gained supreme military command",
  verdict: "support"
})-[:REVIEWS]->(Claim)
```

**Economic SFA Response:**
```
(Review:EconomicPerspective {
  review_id: "rev_eco_001",
  facet: "economic", 
  confidence: 0.88,
  interpretation: "Controlled state finances",
  verdict: "support"
})-[:REVIEWS]->(Claim)
```

### Star Pattern

```
                    ┌────────────┐
                    │    SCA     │
                    │ (proposer) │
                    └─────┬──────┘
                          │
                    [PROPOSED]
                          │
                          ▼
     ┌──────────────────────────────────────┐
     │        :Claim (center)               │
     │  "Caesar appointed dictator 49 BCE"  │
     └──────────────┬───────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
   [REVIEWS]   [REVIEWS]   [REVIEWS]
        │           │           │
        ▼           ▼           ▼
    (Review:     (Review:    (Review:
    Political)   Military)   Economic)
    facet: pol   facet: mil  facet: eco
    conf: 0.95   conf: 0.90  conf: 0.88
```

### Pros
- ✅ Single claim node (simpler graph)
- ✅ All facet perspectives attached to same claim
- ✅ Follows existing Review node pattern (architecture already supports this)
- ✅ Consensus score = aggregate of all facet reviews
- ✅ Cipher-based deduplication still works

### Cons
- ❌ SCA must extract/propose claims from text (more SCA responsibility)
- ❌ SFAs respond reactively (less autonomy)
- ❌ Different facets might see different claims in same text

---

## Hybrid Model: Training + Selective Review (Recommended)

### Workflow

**Phase 1: Training (Independent Domain Ontologies)**
```
Each SFA studies discipline independently
→ Creates claims about abstract domain concepts
→ Builds subject ontology for their field
→ Examples: "Senate legislative authority", "Manipular tactics"
→ SCA accepts training claims as-is (NO automatic queuing)
```

**Phase 2: Selective Multi-Facet Review (SCA Intelligence)**
```
For each claim SCA receives:
→ SCA evaluates: Abstract concept vs Concrete event?
→ If abstract: Accept as-is (no queue)
→ If concrete with multi-domain potential:
   → SCA determines WHICH facets are relevant
   → Routes claim to SELECTED SFAs only (not all)
   → SFAs create FacetPerspective nodes
   → All perspectives attach to the claim via cipher
```

### Example

**Political SFA discovers:**
```
Claim cipher: "claim_pol_abc123..."
Text: "Caesar was appointed dictator in 49 BCE"
Facet: political
```

**SCA routes to Military + Economic SFAs:**

**Military SFA reviews:**
```
(Review:MilitaryPerspective {
  facet: "military",
  interpretation: "Gained supreme military command"
})-[:REVIEWS]->(Claim cipher: "claim_pol_abc123...")
```

**Economic SFA reviews:**
```
(Review:EconomicPerspective {
  facet: "economic",
  interpretation: "Controlled state treasury"
})-[:REVIEWS]->(Claim cipher: "claim_pol_abc123...")
```

**Result:**
```
1 Claim node (created by Political SFA)
+ 2 Review nodes (created by Military + Economic SFAs)
+ All attached to same cipher
```

### Pros
- ✅ SFAs maintain discovery autonomy
- ✅ Uses existing Review pattern
- ✅ Single claim node per assertion (after deduplication)
- ✅ Multi-facet enrichment via reviews
- ✅ Cipher deduplication handles overlaps

### Cons
- ❌ More complex workflow (2 phases)
- ❌ Requires queue management

---

## Alternative: FacetPerspective Nodes (New Pattern)

### Extended Star Pattern

Instead of using Review nodes (which imply validation), use **FacetPerspective** nodes:

```
            ┌────────────┐
            │   Claim    │
            │  (center)  │
            └──────┬─────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
   [HAS_PERSP] [HAS_PERSP] [HAS_PERSP]
        │          │          │
        ▼          ▼          ▼
   (Perspective: (Perspective: (Perspective:
    Political)    Military)    Economic)
    facet: pol    facet: mil   facet: eco
    claim_text:   claim_text:  claim_text:
    "Senate       "Command     "Treasury
     challenge"    gained"      control"
```

**FacetPerspective Schema:**
```cypher
(:FacetPerspective {
  perspective_id: "persp_001",
  facet: "political",
  claim_cipher: "claim_xyz789...",  // Parent claim
  facet_claim_text: "Caesar challenged Senate authority",
  confidence: 0.95,
  source_agent: "political_sfa_001",
  timestamp: "2026-02-15T10:00:00Z"
})-[:PERSPECTIVE_ON]->(Claim)
```

### Benefits
- ✅ Semantic distinction: Review = validation, Perspective = interpretation
- ✅ Each facet can have different claim text (same event, different angles)
- ✅ Clearer than overloading Review nodes
- ✅ Still maintains star pattern with single central claim

---

## Recommendation

**Use Training + Selective Review Model with FacetPerspective Nodes**

### Why?

1. **Respects Learning Phase:** SFAs build domain ontologies independently during training
2. **SCA Intelligence:** Orchestrator uses judgment to determine when collaboration adds value
3. **Efficient Collaboration:** Only concrete, multi-domain claims get cross-facet review
4. **Single Source of Truth:** Cipher deduplication ensures one claim node per assertion
5. **Clear Semantics:** FacetPerspective nodes clarify facet-specific interpretations
6. **Existing Architecture:** Leverages claim cipher pattern already implemented

### Updated Workflow

**Training Phase:**
```
1. SCA spins up all SFAs with discipline training data

2. Political SFA reads political science texts
   → Creates claims about abstract concepts: "Senate held legislative authority"
   → Creates Claim node (cipher: "claim_abc...")
   → Creates FacetPerspective (political angle)
   → Returns to SCA
   → SCA evaluation: Abstract political concept → Accept as-is (NO QUEUE)

3. Military SFA reads military history texts (parallel)
   → Creates claims about military concepts: "Legions organized into cohorts"
   → Creates Claim node (cipher: "claim_def...")
   → Creates FacetPerspective (military angle)
   → Returns to SCA
   → SCA evaluation: Abstract military concept → Accept as-is (NO QUEUE)

Result: Independent domain ontologies built
```

**Operational Phase (Selective Review):**
```
1. Political SFA encounters concrete event
   → Creates Claim node (cipher: "claim_xyz...")
   → Claim text: "Caesar was appointed dictator in 49 BCE"
   → Creates FacetPerspective (political angle)
   → Returns to SCA

2. SCA evaluates claim characteristics
   → Type: Concrete historical event (not abstract concept)
   → Entities: Caesar (military figure), Dictator (state control)
   → Decision: Multi-facet potential HIGH
   → Selectively routes to Military + Economic SFAs only

3. Military SFA processes queued claim
   → Creates FacetPerspective (military angle)
   → Attaches to same claim cipher

4. Economic SFA processes queued claim
   → Creates FacetPerspective (economic angle)
   → Attaches to same claim cipher

Result: 
- 1 Claim node (cipher-based deduplication)
- 3 FacetPerspective nodes (complementary interpretations)
- All linked via [PERSPECTIVE_ON] relationships
- Cultural/Religious/Scientific SFAs NOT queued (not relevant to this claim)
```

---

## Schema Extension Needed

### New Node: FacetPerspective

```cypher
CREATE (persp:FacetPerspective {
  perspective_id: "persp_001",
  facet: "political",
  parent_claim_cipher: "claim_xyz789...",
  facet_claim_text: "Caesar challenged Senate authority by assuming dictatorship",
  confidence: 0.95,
  source_agent_id: "political_sfa_001",
  timestamp: "2026-02-15T10:00:00Z",
  reasoning: "Dictatorship violated traditional Republican norms",
  entities_emphasized: ["Q1048", "Q7747"],  // Caesar, Roman Senate
  relationships_proposed: ["CHALLENGED_AUTHORITY"]
})

// Link to parent claim
MATCH (claim:Claim {cipher: "claim_xyz789..."})
CREATE (persp)-[:PERSPECTIVE_ON]->(claim)

// Link to agent who created perspective
MATCH (agent:Agent {agent_id: "political_sfa_001"})
CREATE (agent)-[:CREATED_PERSPECTIVE]->(persp)
```

### Query Patterns

**Get all perspectives on a claim:**
```cypher
MATCH (persp:FacetPerspective)-[:PERSPECTIVE_ON]->(claim:Claim {cipher: $cipher})
RETURN persp.facet, persp.facet_claim_text, persp.confidence
ORDER BY persp.confidence DESC
```

**Get consensus across facets:**
```cypher
MATCH (persp:FacetPerspective)-[:PERSPECTIVE_ON]->(claim:Claim {cipher: $cipher})
RETURN 
  claim.cipher,
  claim.text AS base_claim,
  AVG(persp.confidence) AS consensus_score,
  COUNT(persp) AS facet_count,
  COLLECT({facet: persp.facet, confidence: persp.confidence}) AS perspectives
```

**Find claims with multi-facet agreement:**
```cypher
MATCH (persp:FacetPerspective)-[:PERSPECTIVE_ON]->(claim:Claim)
WITH claim, COUNT(DISTINCT persp.facet) AS facet_count, AVG(persp.confidence) AS avg_conf
WHERE facet_count >= 3 AND avg_conf > 0.85
RETURN claim.cipher, claim.text, facet_count, avg_conf
ORDER BY avg_conf DESC
```

---

## Next Steps

1. ✅ **Document** FacetPerspective node schema
2. **Update** SCA_SFA_ROLES_DISCUSSION.md with selective queue pattern ✅
3. **Define** SCA routing criteria (how to identify abstract vs concrete claims)
4. **Implement** claim evaluation logic in SCA:
   - Abstract domain concept detection
   - Concrete event/entity detection
   - Multi-domain relevance scoring
5. **Implement** FacetPerspective creation in SFA:
   - Training mode: Create Claim + FacetPerspective
   - Perspective mode: Create FacetPerspective only (if queued by SCA)
6. **Implement** selective queue in SCA:
   - Evaluate each claim for review worthiness
   - Route only to RELEVANT facets (not all)
   - Track which perspectives already exist
7. **Test** with two scenarios:
   - Training: "Senate legislative authority" → No queue
   - Operational: "Caesar dictator 49 BCE" → Selective queue (military, economic only)
