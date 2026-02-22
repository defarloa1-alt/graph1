# Claims Layer Node Schemas ⭐ Multi-Agent Knowledge Construction

## Overview

This document defines the node types and relationships for the **Claims Layer** — the system by which agents make assertions about the graph, propose new structure, undergo multi-agent review, and gradually promote validated knowledge into the core knowledge graph.

The Claims Layer integrates with:
- **Entity Layer** (Person, Place, Event, etc.)
- **Subject Layer** (SubjectConcept, LCSH/FAST hierarchy)
- **Agent Architecture** (subject specialists, entity specialists, coordinators)
- **Provenance & RAG** (Works, citations, retrieval context)

---

## System Architecture Context

### Two Separate Systems

| System | Storage | Shared? | Purpose |
|--------|---------|---------|---------|
| **Neo4j Graph** | Nodes & edges | ✅ YES | Structural knowledge, claims, provenance |
| **Vector Stores** | Text embeddings | ❌ NO | Semantic retrieval per agent (private) |

**Key principle**: Claims, Reviews, and Reasoning Traces live in the shared graph. Text embeddings and document chunks live in private per-agent vector stores.

---

## Claim Node Schema ⭐ Agent Assertions About the Graph

### Node Labels
```cypher
:Claim
```

**Purpose:** Represent an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges). Claims support multi-agent review, provenance, and gradual promotion of "proposed" structure into validated KG facts.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `claim_id` | string | text | `"claim_000123"` | Unique ID |
| `text` | string | text | `"Caesar crossed the Rubicon on January 10, 49 BCE."` | Human-readable claim text |
| `claim_type` | string | enum | `"factual"` | `"factual"`, `"interpretive"`, `"causal"`, `"temporal"` |
| `source_agent` | string | text | `"roman_republic_agent_001"` | Agent that originated the claim |
| `timestamp` | string | ISO 8601 | `"2026-02-12T15:30:00Z"` | When the claim was created |
| `status` | string | enum | `"proposed"` | `"proposed"`, `"validated"`, `"disputed"`, `"rejected"` |
| `confidence` | float | [0,1] | `0.85` | Agent's internal confidence at creation |

### Optional Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `provenance` | string[] | `["Plutarch, Caesar 32", "Suetonius, Julius 31"]` | Source citations |
| `review_count` | int | `3` | Number of reviews received |
| `consensus_score` | float | `0.78` | Aggregated review confidence |
| `claim_scope` | string | `"Battle of Actium casualties"` | Short label for what the claim is about |
| `reasoning_trace_id` | string | `"trace_000987"` | ID of associated ReasoningTrace (if any) |
| `proposed_nodes` | string[] | `["event_123", "place_456"]` | IDs of nodes this claim proposes |
| `proposed_edges` | string[] | `["pedge_001", "pedge_002"]` | IDs of ProposedEdge nodes |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `MADE_CLAIM` | Agent | 1 | `(agent)-[:MADE_CLAIM]->(claim)` |
| `SUBJECT_OF` | Entity/SubjectConcept | 1+ | `(entity OR concept)-[:SUBJECT_OF]->(claim)` |

### Optional Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `PROPOSES` | Entity | Claim proposes existence/interpretation of a node |
| `PROPOSES` | ProposedEdge | Claim proposes a new relationship |
| `HAS_TRACE` | ReasoningTrace | `(claim)-[:HAS_TRACE]->(trace)` |

### Claim Status Lifecycle

```text
proposed → (validated | disputed | rejected)
```

**Status definitions:**

- **proposed**: Created by a source agent, awaiting review.
- **validated**: Supported by sufficient reviews (consensus_score ≥ 0.8); proposed subgraph promoted to regular nodes/edges.
- **disputed**: Mixed or low-confidence reviews (0.5 ≤ consensus_score < 0.8); claim kept with clear status but not promoted.
- **rejected**: Strong consensus against claim (consensus_score < 0.5); proposed structure not materialized.

**Promotion logic:**

When `status` transitions to `"validated"`:
1. Remove `claim_status: "proposed"` from proposed nodes
2. Convert `:ProposedEdge` nodes to actual relationships
3. Update `consensus_score` on the claim
4. Link claim to materialized structure via provenance edges

---

## ProposedEdge Node Schema ⭐ Relationships Awaiting Validation

### Node Labels
```cypher
:ProposedEdge
```

**Purpose:** Represent a relationship proposed by a claim that has not yet been materialized in the graph. Once validated, the ProposedEdge is converted to an actual relationship.

### Required Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `edge_id` | string | `"pedge_001"` | Unique ID |
| `edge_type` | string | `"PARTICIPATED_IN"` | The relationship type to create |
| `from_qid` | string | `"Q1048"` | Source node identifier (QID or other ID) |
| `to_qid` | string | `"Q193304"` | Target node identifier |
| `timestamp` | string | `"2026-02-12T15:30:00Z"` | When proposed |

### Optional Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `confidence` | float | `0.82` | Confidence in this specific edge |
| `edge_properties` | JSON | `{"role": "commander", "date": "-49-01-10"}` | Properties to add to relationship when materialized |

### Required Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `PROPOSES` | Claim | `(claim)-[:PROPOSES]->(proposedEdge)` |

**Encoding example:**

```cypher
// Claim proposes: (caesar:Person)-[:PARTICIPATED_IN {role: "commander"}]->(event:Event)

CREATE (claim:Claim {claim_id: "claim_001", text: "Caesar commanded at Rubicon"})
CREATE (pedge:ProposedEdge {
  edge_id: "pedge_001",
  edge_type: "PARTICIPATED_IN",
  from_qid: "Q1048",
  to_qid: "Q193304",
  edge_properties: '{"role": "commander"}'
})
CREATE (claim)-[:PROPOSES]->(pedge)
```

When validated:

```cypher
MATCH (claim:Claim {status: "validated"})-[:PROPOSES]->(pedge:ProposedEdge)
MATCH (from {qid: pedge.from_qid}), (to {qid: pedge.to_qid})
CALL apoc.create.relationship(from, pedge.edge_type, apoc.convert.fromJsonMap(pedge.edge_properties), to) YIELD rel
DETACH DELETE pedge
```

---

## Review Node Schema ⭐ Multi-Agent Evaluation of Claims

### Node Labels
```cypher
:Review
```

**Purpose:** Represent a single agent's evaluation of a Claim, including confidence, detected fallacies, and a reasoning summary. Reviews feed into consensus and claim status updates.

### Required Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `review_id` | string | `"review_000456"` | Unique ID |
| `agent_id` | string | `"naval_warfare_agent"` | Reviewing agent |
| `claim_id` | string | `"claim_000123"` | Reviewed claim |
| `timestamp` | string | `"2026-02-12T16:00:00Z"` | When review was made |
| `confidence` | float | `0.72` | Reviewer's confidence in the claim |
| `verdict` | string | `"support"` | `"support"`, `"challenge"`, `"uncertain"` |

### Optional Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `fallacies_detected` | string[] | `["anachronism", "post_hoc"]` | From Fischer-style fallacy set |
| `reasoning_summary` | string | `"Plutarch exaggerates casualties; Dio provides more conservative estimate"` | Short text summary |
| `evidence_refs` | string[] | `["Goldsworthy p.145", "Dio 50.35"]` | Evidence used in the review |
| `bayesian_posterior` | float | `0.68` | Output of Bayesian reasoning engine (may differ from raw confidence) |
| `weight` | float | `1.0` | Review weight (specialist agents may have higher weight) |

### Required Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `REVIEWED` | Agent | `(agent)-[:REVIEWED]->(review)` |
| `REVIEWS` | Claim | `(review)-[:REVIEWS]->(claim)` |

### Consensus Calculation

```cypher
// Calculate consensus score for a claim
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

## ReasoningTrace Node Schema ⭐ How a Claim Was Derived

### Node Labels
```cypher
:ReasoningTrace
```

**Purpose:** Persist the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted.

### Required Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `trace_id` | string | `"trace_000987"` | Unique ID |
| `agent_id` | string | `"roman_republic_agent_001"` | Agent that produced this trace |
| `query_text` | string | `"How did Caesar become dictator?"` | Original natural language query |
| `timestamp` | string | `"2026-02-12T15:30:00Z"` | When reasoning occurred |
| `pattern` | string | `"causal_chain"` | High-level reasoning pattern |

### Optional Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `steps` | string[] | `["Retrieved passages about Caesar's consulship", "Found Rubicon crossing event", "Connected civil war victory to dictatorship"]` | Human-readable reasoning steps |
| `sources_consulted` | string[] | `["Goldsworthy, Pax Romana, p. 145", "Plutarch, Life of Caesar, 32"]` | Bibliographic strings |
| `retrieved_passages` | JSON[] | `[{"source": "Goldsworthy p.145", "text": "Caesar crossed...", "score": 0.92}]` | Key passages used (structured as JSON objects) |
| `intermediate_claims` | string[] | `["claim_000120", "claim_000121"]` | IDs of supporting claims (if any) |
| `confidence` | float | `0.85` | Confidence in the reasoning chain |
| `reasoning_depth` | int | `3` | Number of reasoning hops |
| `fallacy_checks` | string[] | `["anachronism: pass", "post_hoc: pass"]` | Fallacy checks performed |

### Required Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `TRACE_OF` | Claim | `(trace)-[:TRACE_OF]->(claim)` |

### Optional Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `USED_CONTEXT` | RetrievalContext | `(trace)-[:USED_CONTEXT]->(retrieval)` |

**Reasoning pattern taxonomy:**

- `"causal_chain"` - X caused Y caused Z
- `"temporal_sequence"` - X then Y then Z
- `"comparative"` - X vs Y comparison
- `"interpretive"` - Multiple sources synthesized into interpretation
- `"deductive"` - General principle applied to specific case
- `"inductive"` - Specific cases generalized to pattern

---

## RetrievalContext Node Schema ⭐ What Was Retrieved From Private Stores

### Node Labels
```cypher
:RetrievalContext
```

**Purpose:** Capture which documents and passages were retrieved from an agent's private vector store for a given query/claim, since vector stores themselves are not shared.

### Required Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `retrieval_id` | string | `"ret_000555"` | Unique ID |
| `agent_id` | string | `"roman_republic_agent_001"` | Agent performing retrieval |
| `timestamp` | string | `"2026-02-12T15:30:02Z"` | Retrieval time |

### Optional Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `query_text` | string | `"How did Caesar become dictator?"` | Text used for embedding search |
| `query_embedding_model` | string | `"text-embedding-ada-002"` | Embedding model used |
| `doc_ids` | string[] | `["work_123", "work_456"]` | Works containing retrieved chunks |
| `passage_ids` | string[] | `["work_123#chunk_5", "work_456#chunk_12"]` | Chunk identifiers |
| `snippet_texts` | JSON[] | `[{"id": "work_123#5", "text": "Caesar crossed...", "score": 0.92}]` | Retrieved passages with scores (structured as JSON) |
| `retrieval_params` | JSON | `{"k": 10, "threshold": 0.7}` | Retrieval parameters used |

### Required Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `USED_FOR` | ReasoningTrace | `(retrieval)-[:USED_FOR]->(trace)` |

### Optional Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `RETRIEVED_FROM` | Work | `(retrieval)-[:RETRIEVED_FROM]->(work)` for each work |

**Example structure:**

```cypher
CREATE (ret:RetrievalContext {
  retrieval_id: "ret_000555",
  agent_id: "roman_republic_agent_001",
  timestamp: "2026-02-12T15:30:02Z",
  query_text: "How did Caesar become dictator?",
  snippet_texts: '[
    {"id": "work_123#5", "text": "Caesar crossed the Rubicon...", "score": 0.92, "source": "Goldsworthy p.145"},
    {"id": "work_456#12", "text": "The Senate declared him an enemy...", "score": 0.88, "source": "Plutarch 32"}
  ]'
})
```

---

## AgentMemory Node Schema ⭐ Persistent Agent Session Context

### Node Labels
```cypher
:AgentMemory
```

**Purpose:** Persist longer-lived agent context across sessions: topics covered, entities/concepts discussed, user interests, and open questions.

### Required Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `memory_id` | string | `"mem_000321"` | Unique ID |
| `agent_id` | string | `"roman_republic_agent_001"` | Agent this memory belongs to |
| `timestamp` | string | `"2026-02-12T15:35:00Z"` | When this memory was recorded |
| `memory_type` | string | `"interaction_history"` | e.g., `"interaction_history"`, `"topic_profile"`, `"user_context"` |

### Optional Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `topics_covered` | string[] | `["Roman politics", "Caesar's dictatorship", "civil war"]` | High-level topics |
| `entities_mentioned` | string[] | `["Q1048", "Q131691", "Q13189"]` | Entity QIDs |
| `concepts_discussed` | string[] | `["sh85115055", "n79021400"]` | SubjectConcept IDs |
| `user_interests` | string[] | `["Roman politics", "frontier policy", "military strategy"]` | Inferred user interest profile |
| `follow_up_questions` | string[] | `["What happened after Caesar became dictator?", "How did the Senate respond?"]` | Open questions |
| `current_focus` | string | `"Roman Republic political transitions"` | Agent's current focus area |
| `working_hypothesis` | string | `"Caesar's dictatorship was a constitutional innovation rather than revolution"` | Optional hypothesis |
| `session_count` | int | `5` | Number of interactions in this memory context |
| `confidence_trajectory` | float[] | `[0.6, 0.7, 0.75, 0.8, 0.85]` | Confidence evolution over sessions |

### Optional Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `MEMORY_OF` | Agent | `(memory)-[:MEMORY_OF]->(agent)` |
| `RELATED_TO` | Claim | `(memory)-[:RELATED_TO]->(claim)` for claims discussed in this context |

**Memory type taxonomy:**

- `"interaction_history"` - Session-level conversation context
- `"topic_profile"` - Long-term topic expertise and focus areas
- `"user_context"` - User interest and preference modeling
- `"hypothesis_tracking"` - Working hypotheses and their evolution
- `"collaboration_state"` - State in multi-agent collaboration

---

## Synthesis Node Schema ⭐ Multi-Agent Consensus Resolution

### Node Labels
```cypher
:Synthesis
```

**Purpose:** When multiple agents produce conflicting claims or reviews, a Synthesis node records the consensus-building process and final resolution.

### Required Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `synthesis_id` | string | `"synth_000789"` | Unique ID |
| `timestamp` | string | `"2026-02-12T16:15:00Z"` | When synthesis was performed |
| `synthesis_type` | string | `"claim_consolidation"` | Type of synthesis performed |
| `consensus_method` | string | `"weighted_bayesian"` | Method used for consensus |

### Optional Properties

| Property | Type | Example | Notes |
|----------|------|---------|-------|
| `participating_agents` | string[] | `["agent_001", "agent_002", "agent_003"]` | Agents involved |
| `input_claims` | string[] | `["claim_001", "claim_002"]` | Claims being synthesized |
| `output_claim` | string | `"claim_003"` | Resulting synthesized claim |
| `consensus_score` | float | `0.76` | Final consensus confidence |
| `resolution_strategy` | string | `"weighted_average"` | How conflicts were resolved |
| `notes` | string | `"Plutarch's figure accepted as upper bound; Dio's as lower bound"` | Human-readable summary |

### Required Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `SYNTHESIZED_FROM` | Claim | `(synthesis)-[:SYNTHESIZED_FROM]->(claim)` for each input claim |
| `PRODUCED` | Claim | `(synthesis)-[:PRODUCED]->(claim)` for output claim |

### Optional Edges

| Relationship | Target | Notes |
|--------------|--------|-------|
| `PERFORMED_BY` | Agent | `(agent)-[:PERFORMED_BY]->(synthesis)` for synthesis agent |

**Synthesis type taxonomy:**

- `"claim_consolidation"` - Multiple claims about same fact merged
- `"conflict_resolution"` - Contradictory claims resolved
- `"range_estimation"` - Numerical estimates combined into range
- `"source_triangulation"` - Multiple sources synthesized
- `"interpretation_fusion"` - Different interpretations reconciled

---

## Implementation Notes

### Claim Creation Workflow

```text
1. User query received by Orchestrator
2. Orchestrator routes to specialist agent
3. Agent queries its private vector store (RetrievalContext created)
4. Agent reasons about retrieved passages (ReasoningTrace created)
5. Agent generates claim (Claim created with status="proposed")
6. Agent creates proposed nodes/edges (ProposedEdge created if needed)
7. Claim linked to entities/concepts via SUBJECT_OF
8. Claim enters review queue
```

### Multi-Agent Review Workflow

```text
1. Claims Coordinator identifies claims needing review
2. Coordinator finds relevant reviewing agents via OWNS_DOMAIN/INCLUDES_CONCEPT
3. Each reviewer:
   a. Queries its own vector store
   b. Generates ReasoningTrace
   c. Creates Review node
4. Coordinator calculates consensus_score
5. Coordinator updates claim.status based on consensus
6. If validated: materialize proposed subgraph
7. If disputed: keep claim with provenance but don't promote
8. If rejected: mark claim as rejected, keep for audit trail
```

### Query Resolution

```cypher
// Find validated claims about Caesar's dictatorship
MATCH (caesar:Person {qid: "Q1048"})-[:SUBJECT_OF]->(claim:Claim {status: "validated"})
WHERE claim.text CONTAINS "dictator"
RETURN claim.text, claim.consensus_score, claim.provenance
ORDER BY claim.consensus_score DESC
```

### Provenance Chain

```cypher
// Full provenance chain for a claim
MATCH path = (work:Work)<-[:RETRIEVED_FROM]-(ret:RetrievalContext)
             -[:USED_FOR]->(trace:ReasoningTrace)
             -[:TRACE_OF]->(claim:Claim)
             <-[:REVIEWS]-(review:Review)
             <-[:REVIEWED]-(agent:Agent)
RETURN path
```

### Confidence Evolution

```cypher
// Track how claim confidence evolved through reviews
MATCH (claim:Claim {claim_id: "claim_000123"})<-[:REVIEWS]-(review:Review)
WITH claim, review
ORDER BY review.timestamp
WITH claim, collect({
  agent: review.agent_id,
  confidence: review.confidence,
  verdict: review.verdict,
  timestamp: review.timestamp
}) AS review_history
RETURN claim.claim_id, 
       claim.confidence AS initial_confidence,
       claim.consensus_score AS final_consensus,
       review_history
```

---

## Integration with Other Layers

### Subject Architecture Integration

Claims are classified by SubjectConcept:

```cypher
MATCH (claim:Claim)-[:SUBJECT_OF]-(concept:SubjectConcept)
RETURN concept.facet, count(claim) AS claim_count
ORDER BY claim_count DESC
```

### Agent Architecture Integration

Agents are evaluated by claim validation rate:

```cypher
MATCH (agent:Agent)-[:MADE_CLAIM]->(claim:Claim)
WITH agent, 
     count(claim) AS total_claims,
     size([c IN collect(claim) WHERE c.status = "validated"]) AS validated_claims
RETURN agent.agent_id,
       validated_claims * 1.0 / total_claims AS validation_rate
ORDER BY validation_rate DESC
```

### Work & RAG Integration

Claims trace back to source works:

```cypher
MATCH (claim:Claim)-[:HAS_TRACE]->(trace:ReasoningTrace)
      -[:USED_CONTEXT]->(ret:RetrievalContext)
      -[:RETRIEVED_FROM]->(work:Work)
RETURN claim.text, collect(DISTINCT work.title) AS source_works
```

---

## Future Extensions

### Planned Enhancements

1. **Temporal Claims** - Claims with time-varying validity
2. **Claim Versioning** - Track claim evolution over time
3. **Probabilistic Claims** - Claims with probability distributions
4. **Claim Hierarchies** - Claims that support or refute other claims
5. **External Validation** - Integration with external fact-checking systems
6. **Automated Fallacy Detection** - Fischer's Fallacies as automated checks

### Research Directions

1. **Bayesian Claim Networks** - Full probabilistic reasoning over claim dependencies
2. **Adversarial Review** - Deliberate devil's advocate agents
3. **Confidence Calibration** - Learning when agents are over/under-confident
4. **Source Credibility Modeling** - Weighting sources by reliability
5. **Temporal Decay** - Claims becoming less certain over time without re-validation

---

## Status: Production Ready ✅

This schema is aligned with:
- ✅ Entity Layer (Person, Place, Event, etc.)
- ✅ Subject Architecture (SubjectConcept, LCSH/FAST)
- ✅ Agent Architecture (specialists, coordinators)
- ✅ Work & RAG layers (provenance, citations)
- ✅ Multi-agent reasoning (reviews, synthesis)
- ✅ Historian methodology (Fischer's Fallacies, Bayesian reasoning)

Ready for implementation and integration into NODE_TYPE_SCHEMAS master document.
