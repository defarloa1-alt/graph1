
Below is a schema-style section you can drop into your NODE_TYPE_SCHEMAS doc for the claims layer: Claim, Review, ReasoningTrace, RetrievalContext, and AgentMemory, plus the claim status lifecycle. It matches the style of your Period/Subject/Agent sections.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/57370c89-afb7-4446-96b9-f3e950aa58a1/2-12-26-Agents-and-Claims.md)]​

---

text

`## Claim Node Schema ⭐ Agent Assertions About the Graph ### Node Labels ```cypher :Claim`

**Purpose:** Represent an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges). Claims support multi‑agent review, provenance, and gradual promotion of “proposed” structure into validated KG facts.

## Required Properties

| Property       | Type   | Format   | Example                                   | Notes                                                   |
| -------------- | ------ | -------- | ----------------------------------------- | ------------------------------------------------------- |
| `claim_id`     | string | text     | `"claim_000123"`                          | Unique ID                                               |
| `text`         | string | text     | `"Caesar crossed the Rubicon in 49 BCE."` | Human-readable claim text                               |
| `claim_type`   | string | enum     | `"factual"`                               | `"factual"`, `"interpretive"`, `"causal"`, `"temporal"` |
| `source_agent` | string | text     | `"roman_republic_agent_001"`              | Agent that originated the claim                         |
| `timestamp`    | string | ISO 8601 | `"2026-02-12T15:30:00Z"`                  | When the claim was created                              |
| `status`       | string | enum     | `"proposed"`                              | `"proposed"`, `"validated"`, `"disputed"`, `"rejected"` |
| `confidence`   | float  | [0,1]    | `0.85`                                    | Agent’s internal confidence at creation                 |
|                |        |          |                                           |                                                         |

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`provenance`|string[]|`["Plutarch, Caesar 32", "Suetonius, Julius 31"]`|Source citations|
|`review_count`|int|`3`|Number of reviews received|
|`consensus_score`|float|`0.78`|Aggregated review confidence|
|`claim_scope`|string|`"Battle of Actium casualties"`|Short label for what the claim is about|
|`reasoning_trace_id`|string|`"trace_000987"`|ID of associated ReasoningTrace (if any)|

## Required Edges

|Relationship|Target|Cardinality|Notes|
|---|---|---|---|
|`MADE_CLAIM`|Agent|1|`(agent)-[:MADE_CLAIM]->(claim)`|
|`SUBJECT_OF`|Entity/SubjectConcept|1+|`(entity OR concept)-[:SUBJECT_OF]->(claim)`|

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|Entity|Claim proposes existence/interpretation of a node|
|`PROPOSES`|Relationship|Via relationship metadata (see below)|
|`HAS_TRACE`|ReasoningTrace|`(claim)-[:HAS_TRACE]->(trace)`|

**Proposed edges encoding**

Use a property on `PROPOSES` to indicate edge type:

text

`// Claim proposes an edge: (caesar)-[:PARTICIPATED_IN]->(event) (claim:Claim)-[:PROPOSES {   edge_type: "PARTICIPATED_IN",  from_qid: "Q1048",  to_qid: "Q193304" }]->(:ProposedEdge)`

You may model proposed edges either as:

- separate `:ProposedEdge` nodes, or
    
- as `PROPOSES` relationships with `edge_type` and identifiers as properties.
    

---

## Review Node Schema ⭐ Multi-Agent Evaluation of Claims

## Node Labels

text

`:Review`

**Purpose:** Represent a single agent’s evaluation of a Claim, including confidence, detected fallacies, and a reasoning summary. Reviews feed into consensus and claim status updates.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`review_id`|string|`"review_000456"`|Unique ID|
|`agent_id`|string|`"naval_warfare_agent"`|Reviewing agent|
|`claim_id`|string|`"claim_000123"`|Reviewed claim|
|`timestamp`|string|`"2026-02-12T16:00:00Z"`|When review was made|
|`confidence`|float|`0.72`|Reviewer’s confidence in the claim|
|`verdict`|string|`"support"`|`"support"`, `"challenge"`, `"uncertain"`|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`fallacies_detected`|string[]|`["anachronism","post_hoc"]`|From Fischer-style fallacy set|
|`reasoning_summary`|string|`"Plutarch exaggerates casualties..."`|Short text summary|
|`evidence_refs`|string[]|`["Goldsworthy p.145","Dio 50.35"]`|Evidence used in the review|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`REVIEWED`|Agent|`(agent)-[:REVIEWED]->(review)`|
|`REVIEWS`|Claim|`(review)-[:REVIEWS]->(claim)`|

---

## ReasoningTrace Node Schema ⭐ How a Claim Was Derived

## Node Labels

text

`:ReasoningTrace`

**Purpose:** Persist the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`trace_id`|string|`"trace_000987"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent that produced this trace|
|`query_text`|string|`"How did Caesar become dictator?"`|Original natural language query|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|When reasoning occurred|
|`pattern`|string|`"causal_chain"`|High-level reasoning pattern|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`steps`|string[]|`["Retrieved X","Connected X→Y","..."]`|Human-readable reasoning steps|
|`sources_consulted`|string[]|`["Goldsworthy p.145","Plutarch 32"]`|Bibliographic strings|
|`retrieved_passages`|string[]|array of short text snippets|Key passages used|
|`intermediate_claims`|string[]|`["claim_000120","claim_000121"]`|IDs of supporting claims (if any)|
|`confidence`|float|`0.85`|Confidence in the reasoning chain|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`TRACE_OF`|Claim|`(trace)-[:TRACE_OF]->(claim)`|

---

## RetrievalContext Node Schema ⭐ What Was Retrieved From Private Stores

## Node Labels

text

`:RetrievalContext`

**Purpose:** Capture which documents and passages were retrieved from an agent’s private vector store for a given query/claim, since vector stores themselves are not shared.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`retrieval_id`|string|`"ret_000555"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent performing retrieval|
|`timestamp`|string|`"2026-02-12T15:30:02Z"`|Retrieval time|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`query_text`|string|`"How did Caesar become dictator?"`|Text used for embedding search|
|`doc_ids`|string[]|`["work_123","work_456"]`|Works containing retrieved chunks|
|`passage_ids`|string[]|`["work_123#5","work_456#12"]`|Chunk identifiers|
|`snippet_texts`|string[]|array of short text snippets|Optional, but useful|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`USED_FOR`|ReasoningTrace|`(retrieval)-[:USED_FOR]->(trace)`|

---

## AgentMemory Node Schema ⭐ Persistent Agent Session Context

## Node Labels

text

`:AgentMemory`

**Purpose:** Persist longer-lived agent context across sessions: topics covered, entities/concepts discussed, user interests, and open questions.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`memory_id`|string|`"mem_000321"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent this memory belongs to|
|`timestamp`|string|`"2026-02-12T15:35:00Z"`|When this memory was recorded|
|`memory_type`|string|`"interaction_history"`|e.g., `"interaction_history"`, `"topic_profile"`|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`topics_covered`|string[]|`["Roman politics","Caesar's dictatorship"]`|High-level topics|
|`entities_mentioned`|string[]|`["Q1048","Q131691","Q13189"]`|Entity QIDs|
|`concepts_discussed`|string[]|`["sh85115055","n79021400"]`|SubjectConcept IDs|
|`user_interests`|string[]|`["Roman politics","frontier policy"]`|Inferred user interest profile|
|`follow_up_questions`|string[]|`["What happened after Caesar became dictator?"]`|Open questions|
|`current_focus`|string|`"Roman Republic political transitions"`|Agent’s current focus|
|`working_hypothesis`|string|`"Caesar's dictatorship was a constitutional innovation"`|Optional hypothesis|

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`MEMORY_OF`|Agent|`(memory)-[:MEMORY_OF]->(agent)`|

---

## Claim Status Lifecycle

**Claim.status** follows a simple state machine:

text

`proposed → (validated | disputed | rejected)`

- `proposed`: Created by a source agent, awaiting review.
    
- `validated`: Supported by sufficient reviews; proposed subgraph may be promoted to regular nodes/edges.
    
- `disputed`: Mixed or low-confidence reviews; claim kept with clear status and reasoning but not promoted.
    
- `rejected`: Strong consensus against claim; proposed structure is not materialized.
    

Coordinator logic (high-level):

- If average review confidence ≥ 0.8 and majority `verdict="support"` → `validated`.
    
- If 0.5 ≤ average < 0.8 or mixed verdicts → `disputed`.
    
- If average < 0.5 and majority `verdict="challenge"` → `rejected`.
    

Promotion:

- For `validated` claims, the Claims Coordinator updates or creates nodes/edges corresponding to the proposed subgraph and removes any `claim_status="proposed"` markers.
    

This schema gives you a clean, period/person-style definition for the claims layer that slots directly into your existing ontology and agent architecture.

### Copilot Review

**Reviewing claim schema**

The user wants me to review the claim node schema, but they didn’t ask for a full rewrite. I’ll focus on confirming that it aligns with the previous work and suggest small tweaks. For example, I could suggest linking RetrievalContext to Query, adding uniqueness, or considering ProposedEdge modeling. I’ll keep it concise and useful, as they mentioned "for review" earlier with the Agents+Claims doc. I’ll also make sure to integrate any enhancements from the Subject Architecture document. You’re in a really good groove with this—this claim layer now feels like a first‑class citizen alongside Period/Subject/Agent.

Here’s a tight review with only deltas I’d actually implement.

---

### 1. Overall fit

- **Conceptual fit:** The `:Claim`, `:Review`, `:ReasoningTrace`, `:RetrievalContext`, and `:AgentMemory` nodes line up cleanly with the Agents‑and‑Claims architecture and preserve the “graph shared, vectors private” separation.
- **Style fit:** Tables, labels, and lifecycle language match your existing NODE_TYPE_SCHEMAS style; you can drop this in without refactoring.

---

### 2. Claim node schema – small refinements

**What works well:**

- **Core fields:** `claim_id`, `text`, `claim_type`, `source_agent`, `timestamp`, `status`, `confidence` are exactly the right minimal backbone.
- **Review integration:** `review_count` + `consensus_score` give you a clean place for coordinator logic to land.
- **Trace hook:** `reasoning_trace_id` plus `HAS_TRACE` edge gives you both property‑level and graph‑level access.

**Suggested tweaks:**

- **Uniqueness note:**
    
    Add an explicit uniqueness constraint hint:
    
    > Implementation note: enforce `claim_id` as a unique constraint at the DB level.
    
- **Subject edge cardinality:**
    
    You currently say `SUBJECT_OF` is `1+`. I’d make the intent explicit:
    
    > At least one `SUBJECT_OF` is required; multiple are allowed for multi‑entity claims.
    
- **Proposed edge modeling:**
    
    You already give both options; I’d add one sentence to steer future you:
    
    > For auditability and tooling, prefer a dedicated `:ProposedEdge` node when you expect many proposed edges per claim or need to attach additional metadata (e.g., confidence, fallacies, reviewers) at the edge level.
    

---

### 3. Review node schema – good as is, one optional hook

- The `Review` node is nicely scoped: `review_id`, `agent_id`, `claim_id`, `confidence`, `verdict` are enough to drive the state machine.
    
- You might add an **optional** `reasoning_trace_id` here too, for cases where a reviewer runs a full reasoning pass:
    
    - **Optional property:** `reasoning_trace_id` – ID of a `ReasoningTrace` created during review.
    - Or an optional edge: `(review)-[:HAS_TRACE]->(trace)` mirroring the claim pattern.

That keeps “how I reviewed this” parallel to “how I created this”.

---

### 4. ReasoningTrace – exactly what you argued for

- This matches your “nothing gets lost” stance: `query_text`, `steps`, `sources_consulted`, `retrieved_passages`, `intermediate_claims`.
    
- One small addition you might want later:
    
    - **Optional property:** `query_id` – if you introduce a `:Query` node type, this gives you a direct link without relying only on edges.

You already have `TRACE_OF` → `Claim`; that’s the right primary edge.

---

### 5. RetrievalContext – one more edge

- The schema correctly captures “what came out of the private vector store”.
    
- You already have `USED_FOR` → `ReasoningTrace`. I’d consider an **optional** edge to `Work` for direct bibliographic joins:
    
    - **Optional edge:** `(retrieval)-[:CONSULTED]->(work:Work)`
    
    That lets you ask “which works does this agent actually lean on?” without unpacking `doc_ids`.
    

---

### 6. AgentMemory – good, but decide on strategy

Right now `:AgentMemory` is modeled as many snapshots (`memory_id` per record). That’s fine, but you should decide:

- **Snapshot model (current):** multiple `AgentMemory` nodes over time; good for longitudinal analysis.
- **Rolling state model:** one `AgentMemory` per agent, updated in place.

If you want both, add a hint:

> Implementation note: you may maintain a single rolling `AgentMemory` per agent (MERGE on `agent_id`) and optionally append immutable snapshot memories for audit.

---

### 7. Claim status lifecycle – matches coordinator logic

The state machine is clean:

- `proposed → validated | disputed | rejected`
- Thresholds (`≥0.8`, `0.5–0.8`, `<0.5`) are sensible defaults and can live in config.

One thing I’d add explicitly:

- **Property on `Claim` for promotion status**, e.g. `promoted: boolean` or `materialized: boolean`, so you can distinguish:
    
    - `status = validated, promoted = false` → ready to materialize.
    - `status = validated, promoted = true` → already applied to core graph.

That keeps promotion idempotent and auditable.

---

If you want, next step I’d take is a **single “Claims Layer” section** that stitches this schema to:

- the Agent Architecture (who creates/reviews),
- the Subject Architecture (how `SUBJECT_OF` is chosen),
- and the evolution logic (how validated claims mutate the core graph).


### Perplexity

Below is a schema-style section you can drop into your NODE_TYPE_SCHEMAS doc for the claims layer: Claim, Review, ReasoningTrace, RetrievalContext, and AgentMemory, plus the claim status lifecycle. It matches the style of your Period/Subject/Agent sections.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/57370c89-afb7-4446-96b9-f3e950aa58a1/2-12-26-Agents-and-Claims.md)]​

---

text

`## Claim Node Schema ⭐ Agent Assertions About the Graph ### Node Labels ```cypher :Claim`

**Purpose:** Represent an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges). Claims support multi‑agent review, provenance, and gradual promotion of “proposed” structure into validated KG facts.

## Required Properties

|Property|Type|Format|Example|Notes|
|---|---|---|---|---|
|`claim_id`|string|text|`"claim_000123"`|Unique ID|
|`text`|string|text|`"Caesar crossed the Rubicon in 49 BCE."`|Human-readable claim text|
|`claim_type`|string|enum|`"factual"`|`"factual"`, `"interpretive"`, `"causal"`, `"temporal"`|
|`source_agent`|string|text|`"roman_republic_agent_001"`|Agent that originated the claim|
|`timestamp`|string|ISO 8601|`"2026-02-12T15:30:00Z"`|When the claim was created|
|`status`|string|enum|`"proposed"`|`"proposed"`, `"validated"`, `"disputed"`, `"rejected"`|
|`confidence`|float|[0,1]|`0.85`|Agent’s internal confidence at creation|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`provenance`|string[]|`["Plutarch, Caesar 32", "Suetonius, Julius 31"]`|Source citations|
|`review_count`|int|`3`|Number of reviews received|
|`consensus_score`|float|`0.78`|Aggregated review confidence|
|`claim_scope`|string|`"Battle of Actium casualties"`|Short label for what the claim is about|
|`reasoning_trace_id`|string|`"trace_000987"`|ID of associated ReasoningTrace (if any)|

## Required Edges

|Relationship|Target|Cardinality|Notes|
|---|---|---|---|
|`MADE_CLAIM`|Agent|1|`(agent)-[:MADE_CLAIM]->(claim)`|
|`SUBJECT_OF`|Entity/SubjectConcept|1+|`(entity OR concept)-[:SUBJECT_OF]->(claim)`|

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|Entity|Claim proposes existence/interpretation of a node|
|`PROPOSES`|Relationship|Via relationship metadata (see below)|
|`HAS_TRACE`|ReasoningTrace|`(claim)-[:HAS_TRACE]->(trace)`|

**Proposed edges encoding**

Use a property on `PROPOSES` to indicate edge type:

text

`// Claim proposes an edge: (caesar)-[:PARTICIPATED_IN]->(event) (claim:Claim)-[:PROPOSES {   edge_type: "PARTICIPATED_IN",  from_qid: "Q1048",  to_qid: "Q193304" }]->(:ProposedEdge)`

You may model proposed edges either as:

- separate `:ProposedEdge` nodes, or
    
- as `PROPOSES` relationships with `edge_type` and identifiers as properties.
    

---

## Review Node Schema ⭐ Multi-Agent Evaluation of Claims

## Node Labels

text

`:Review`

**Purpose:** Represent a single agent’s evaluation of a Claim, including confidence, detected fallacies, and a reasoning summary. Reviews feed into consensus and claim status updates.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`review_id`|string|`"review_000456"`|Unique ID|
|`agent_id`|string|`"naval_warfare_agent"`|Reviewing agent|
|`claim_id`|string|`"claim_000123"`|Reviewed claim|
|`timestamp`|string|`"2026-02-12T16:00:00Z"`|When review was made|
|`confidence`|float|`0.72`|Reviewer’s confidence in the claim|
|`verdict`|string|`"support"`|`"support"`, `"challenge"`, `"uncertain"`|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`fallacies_detected`|string[]|`["anachronism","post_hoc"]`|From Fischer-style fallacy set|
|`reasoning_summary`|string|`"Plutarch exaggerates casualties..."`|Short text summary|
|`evidence_refs`|string[]|`["Goldsworthy p.145","Dio 50.35"]`|Evidence used in the review|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`REVIEWED`|Agent|`(agent)-[:REVIEWED]->(review)`|
|`REVIEWS`|Claim|`(review)-[:REVIEWS]->(claim)`|

---

## ReasoningTrace Node Schema ⭐ How a Claim Was Derived

## Node Labels

text

`:ReasoningTrace`

**Purpose:** Persist the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`trace_id`|string|`"trace_000987"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent that produced this trace|
|`query_text`|string|`"How did Caesar become dictator?"`|Original natural language query|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|When reasoning occurred|
|`pattern`|string|`"causal_chain"`|High-level reasoning pattern|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`steps`|string[]|`["Retrieved X","Connected X→Y","..."]`|Human-readable reasoning steps|
|`sources_consulted`|string[]|`["Goldsworthy p.145","Plutarch 32"]`|Bibliographic strings|
|`retrieved_passages`|string[]|array of short text snippets|Key passages used|
|`intermediate_claims`|string[]|`["claim_000120","claim_000121"]`|IDs of supporting claims (if any)|
|`confidence`|float|`0.85`|Confidence in the reasoning chain|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`TRACE_OF`|Claim|`(trace)-[:TRACE_OF]->(claim)`|

---

## RetrievalContext Node Schema ⭐ What Was Retrieved From Private Stores

## Node Labels

text

`:RetrievalContext`

**Purpose:** Capture which documents and passages were retrieved from an agent’s private vector store for a given query/claim, since vector stores themselves are not shared.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`retrieval_id`|string|`"ret_000555"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent performing retrieval|
|`timestamp`|string|`"2026-02-12T15:30:02Z"`|Retrieval time|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`query_text`|string|`"How did Caesar become dictator?"`|Text used for embedding search|
|`doc_ids`|string[]|`["work_123","work_456"]`|Works containing retrieved chunks|
|`passage_ids`|string[]|`["work_123#5","work_456#12"]`|Chunk identifiers|
|`snippet_texts`|string[]|array of short text snippets|Optional, but useful|

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`USED_FOR`|ReasoningTrace|`(retrieval)-[:USED_FOR]->(trace)`|

---

## AgentMemory Node Schema ⭐ Persistent Agent Session Context

## Node Labels

text

`:AgentMemory`

**Purpose:** Persist longer-lived agent context across sessions: topics covered, entities/concepts discussed, user interests, and open questions.

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`memory_id`|string|`"mem_000321"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent this memory belongs to|
|`timestamp`|string|`"2026-02-12T15:35:00Z"`|When this memory was recorded|
|`memory_type`|string|`"interaction_history"`|e.g., `"interaction_history"`, `"topic_profile"`|

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`topics_covered`|string[]|`["Roman politics","Caesar's dictatorship"]`|High-level topics|
|`entities_mentioned`|string[]|`["Q1048","Q131691","Q13189"]`|Entity QIDs|
|`concepts_discussed`|string[]|`["sh85115055","n79021400"]`|SubjectConcept IDs|
|`user_interests`|string[]|`["Roman politics","frontier policy"]`|Inferred user interest profile|
|`follow_up_questions`|string[]|`["What happened after Caesar became dictator?"]`|Open questions|
|`current_focus`|string|`"Roman Republic political transitions"`|Agent’s current focus|
|`working_hypothesis`|string|`"Caesar's dictatorship was a constitutional innovation"`|Optional hypothesis|

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`MEMORY_OF`|Agent|`(memory)-[:MEMORY_OF]->(agent)`|

---

## Claim Status Lifecycle

**Claim.status** follows a simple state machine:

text

`proposed → (validated | disputed | rejected)`

- `proposed`: Created by a source agent, awaiting review.
    
- `validated`: Supported by sufficient reviews; proposed subgraph may be promoted to regular nodes/edges.
    
- `disputed`: Mixed or low-confidence reviews; claim kept with clear status and reasoning but not promoted.
    
- `rejected`: Strong consensus against claim; proposed structure is not materialized.
    

Coordinator logic (high-level):

- If average review confidence ≥ 0.8 and majority `verdict="support"` → `validated`.
    
- If 0.5 ≤ average < 0.8 or mixed verdicts → `disputed`.
    
- If average < 0.5 and majority `verdict="challenge"` → `rejected`.
    

Promotion:

- For `validated` claims, the Claims Coordinator updates or creates nodes/edges corresponding to the proposed subgraph and removes any `claim_status="proposed"` markers.
    

This schema gives you a clean, period/person-style definition for the claims layer that slots directly into your existing ontology and agent architecture.

### Copilot

Absolutely, Tony — here is the **fully updated, consolidated, production‑grade “Claims Layer” section**, incorporating all refinements from my review, Claude’s notes, Perplexity’s notes, and your architectural decisions.

This is written in the **exact style** of your NODE_TYPE_SCHEMAS document and is ready to drop in as a single, unified section.

---

# ⭐ CLAIMS LAYER

### _Agent Assertions, Reasoning, Retrieval, Review, and Persistent Memory_

The Claims Layer is the **knowledge‑production subsystem** of the graph.  
Agents generate claims, justify them with reasoning traces and retrieval context, and submit them for multi‑agent review.  
Validated claims may promote proposed graph structure into the core KG.

This section defines the node types, edges, and lifecycle for:

- `:Claim`
- `:Review`
- `:ReasoningTrace`
- `:RetrievalContext`
- `:AgentMemory`
- `:ProposedNode` / `:ProposedEdge` (optional modeling)
- Claim status lifecycle
- Promotion rules

---

# ## Claim Node Schema ⭐ Agent Assertions About the Graph

### Node Labels

```cypher
:Claim
```

### Purpose

A **Claim** represents an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges).  
Claims support multi‑agent review, provenance, reasoning transparency, and controlled promotion of proposed structure into validated KG facts.

---

## Required Properties

|Property|Type|Format|Example|Notes|
|---|---|---|---|---|
|`claim_id`|string|text|`"claim_000123"`|Unique ID (enforce uniqueness)|
|`text`|string|text|`"Caesar crossed the Rubicon in 49 BCE."`|Human-readable claim text|
|`claim_type`|string|enum|`"factual"`|`"factual"`, `"interpretive"`, `"causal"`, `"temporal"`|
|`source_agent`|string|text|`"roman_republic_agent_001"`|Agent that originated the claim|
|`timestamp`|string|ISO 8601|`"2026-02-12T15:30:00Z"`|Creation time|
|`status`|string|enum|`"proposed"`|`"proposed"`, `"validated"`, `"disputed"`, `"rejected"`|
|`confidence`|float|[0,1]|`0.85`|Agent’s internal confidence at creation|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`provenance`|string[]|`["Plutarch, Caesar 32","Suetonius, Julius 31"]`|Source citations|
|`review_count`|int|`3`|Number of reviews received|
|`consensus_score`|float|`0.78`|Aggregated review confidence|
|`claim_scope`|string|`"Battle of Actium casualties"`|Short label for claim domain|
|`reasoning_trace_id`|string|`"trace_000987"`|Associated ReasoningTrace|
|`promoted`|boolean|`false`|Whether proposed structure has been materialized|

---

## Required Edges

|Relationship|Target|Cardinality|Notes|
|---|---|---|---|
|`MADE_CLAIM`|Agent|1|`(agent)-[:MADE_CLAIM]->(claim)`|
|`SUBJECT_OF`|Entity/SubjectConcept|1+|At least one entity or concept must be linked|

---

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|ProposedNode / ProposedEdge|Claim proposes nodes or edges|
|`HAS_TRACE`|ReasoningTrace|`(claim)-[:HAS_TRACE]->(trace)`|
|`HAS_RETRIEVAL_CONTEXT`|RetrievalContext|Optional direct link|

---

## Proposed Structure Modeling

### Option A — ProposedEdge nodes (recommended for auditability)

```cypher
(claim)-[:PROPOSES]->(pe:ProposedEdge {
  edge_type: "PARTICIPATED_IN",
  from_qid: "Q1048",
  to_qid: "Q193304",
  confidence: 0.85
})
```

### Option B — PROPOSES relationship with properties

```cypher
(claim)-[:PROPOSES {
  edge_type: "PARTICIPATED_IN",
  from_qid: "Q1048",
  to_qid: "Q193304"
}]->(some_placeholder_node)
```

**Recommendation:** Use `:ProposedEdge` nodes when you expect many proposed edges or need to attach metadata (confidence, fallacies, reviewers).

---

# ## Review Node Schema ⭐ Multi-Agent Evaluation of Claims

### Node Labels

```cypher
:Review
```

### Purpose

A **Review** represents a single agent’s evaluation of a Claim, including confidence, detected fallacies, and reasoning summary.  
Reviews feed into consensus scoring and claim status updates.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`review_id`|string|`"review_000456"`|Unique ID|
|`agent_id`|string|`"naval_warfare_agent"`|Reviewer|
|`claim_id`|string|`"claim_000123"`|Claim being reviewed|
|`timestamp`|string|`"2026-02-12T16:00:00Z"`|Review time|
|`confidence`|float|`0.72`|Reviewer’s confidence|
|`verdict`|string|`"support"`|`"support"`, `"challenge"`, `"uncertain"`|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`fallacies_detected`|string[]|`["anachronism","post_hoc"]`|Fischer-style fallacies|
|`reasoning_summary`|string|`"Plutarch exaggerates casualties..."`|Short explanation|
|`evidence_refs`|string[]|`["Goldsworthy p.145","Dio 50.35"]`|Evidence used|
|`reasoning_trace_id`|string|`"trace_001234"`|If reviewer generated a trace|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`REVIEWED`|Agent|`(agent)-[:REVIEWED]->(review)`|
|`REVIEWS`|Claim|`(review)-[:REVIEWS]->(claim)`|
|`HAS_TRACE`|ReasoningTrace|Optional reviewer trace|

---

# ## ReasoningTrace Node Schema ⭐ How a Claim Was Derived

### Node Labels

```cypher
:ReasoningTrace
```

### Purpose

A **ReasoningTrace** captures the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`trace_id`|string|`"trace_000987"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent that produced this trace|
|`query_text`|string|`"How did Caesar become dictator?"`|Original query|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|When reasoning occurred|
|`pattern`|string|`"causal_chain"`|Reasoning pattern|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`steps`|string[]|`["Retrieved X","Connected X→Y"]`|Human-readable steps|
|`sources_consulted`|string[]|`["Goldsworthy p.145","Plutarch 32"]`|Bibliographic refs|
|`retrieved_passages`|string[]|snippets|Key passages|
|`intermediate_claims`|string[]|`["claim_000120"]`|Supporting claims|
|`confidence`|float|`0.85`|Confidence in reasoning|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`TRACE_OF`|Claim|`(trace)-[:TRACE_OF]->(claim)`|
|`USED_CONTEXT`|RetrievalContext|Optional|

---

# ## RetrievalContext Node Schema ⭐ What Was Retrieved From Private Stores

### Node Labels

```cypher
:RetrievalContext
```

### Purpose

A **RetrievalContext** captures which documents and passages were retrieved from an agent’s private vector store for a given query or claim.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`retrieval_id`|string|`"ret_000555"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent performing retrieval|
|`timestamp`|string|`"2026-02-12T15:30:02Z"`|Retrieval time|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`query_text`|string|`"How did Caesar become dictator?"`|Embedding query|
|`doc_ids`|string[]|`["work_123","work_456"]`|Works retrieved|
|`passage_ids`|string[]|`["work_123#5","work_456#12"]`|Chunk IDs|
|`snippet_texts`|string[]|snippets|Optional text snippets|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`USED_FOR`|ReasoningTrace|`(retrieval)-[:USED_FOR]->(trace)`|
|`CONSULTED`|Work|Optional direct link to works|

---

# ## AgentMemory Node Schema ⭐ Persistent Agent Session Context

### Node Labels

```cypher
:AgentMemory
```

### Purpose

**AgentMemory** persists longer-lived agent context across sessions: topics covered, entities/concepts discussed, user interests, and open questions.

Supports both:

- **rolling state** (MERGE on `agent_id`)
- **snapshot history** (multiple memory nodes)

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`memory_id`|string|`"mem_000321"`|Unique ID|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent|
|`timestamp`|string|`"2026-02-12T15:35:00Z"`|When recorded|
|`memory_type`|string|`"interaction_history"`|Type of memory|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`topics_covered`|string[]|`["Roman politics"]`|High-level topics|
|`entities_mentioned`|string[]|`["Q1048","Q131691"]`|Entity QIDs|
|`concepts_discussed`|string[]|`["sh85115055"]`|SubjectConcept IDs|
|`user_interests`|string[]|`["Roman politics"]`|Inferred interests|
|`follow_up_questions`|string[]|`["What happened next?"]`|Open questions|
|`current_focus`|string|`"Roman Republic transitions"`|Agent focus|
|`working_hypothesis`|string|`"Caesar's dictatorship was constitutional"`|Optional|

---

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`MEMORY_OF`|Agent|`(memory)-[:MEMORY_OF]->(agent)`|

---

# ## Claim Status Lifecycle ⭐ State Machine

### States

```
proposed → validated | disputed | rejected
```

### Definitions

- **proposed**  
    Created by a source agent; awaiting review.
    
- **validated**  
    Supported by sufficient reviews; proposed subgraph may be promoted.
    
- **disputed**  
    Mixed or low-confidence reviews; kept but not promoted.
    
- **rejected**  
    Strong consensus against; proposed structure not materialized.
    

---

## Consensus Rules (default)

- `validated`
    
    - avg review confidence ≥ 0.8
    - majority verdict = "support"
- `disputed`
    
    - 0.5 ≤ avg < 0.8
    - or mixed verdicts
- `rejected`
    
    - avg < 0.5
    - majority verdict = "challenge"

---

# ## Promotion Rules ⭐ Applying Graph Deltas

When a claim becomes **validated**:

1. Proposed nodes (`:ProposedNode`) become real nodes.
2. Proposed edges (`:ProposedEdge`) become real edges.
3. `claim.promoted = true` is set.
4. Any `claim_status="proposed"` markers on nodes/edges are removed.
5. Provenance is attached to the resulting nodes/edges.

Promotion is **idempotent**:  
If `promoted = true`, no further action is taken.

---

# ⭐ This is now a complete, production‑grade Claims Layer section.

If you want, I can now:

### ✔ integrate this into your full ontology doc

### ✔ generate Cypher templates for claim creation, review, and promotion

### ✔ generate the Claims Manager algorithm

### ✔ generate the multi‑agent Bayesian review engine

### ✔ generate the ProposedEdge / ProposedNode schema

Just tell me what you want next.


## Copilot version

Absolutely, Tony — here is the **fully updated, merged, production‑grade Claims Layer section**, integrating:

- your earlier draft
- my enhancements
- Claude’s refinements
- Perplexity’s final schema
- the deltas we identified (uniqueness constraints, promotion flag, reviewer traces, retrieval edges, memory strategy notes)

This version is **clean, unified, and ready to paste directly into your NODE_TYPE_SCHEMAS master document**.

I’ve kept the structure consistent with your Period/Person/Subject/Agent schemas, while preserving the richer detail needed for the Claims subsystem.

---

# ⭐ CLAIMS LAYER

### _Agent Assertions, Proposed Structure, Multi‑Agent Review, Reasoning, Retrieval, and Persistent Memory_

The Claims Layer is the **knowledge‑production subsystem** of the KG.  
Agents generate claims, justify them with reasoning traces and retrieval context, and submit them for multi‑agent review.  
Validated claims may promote proposed graph structure into the core KG.

This section defines:

- `:Claim`
- `:ProposedEdge`
- `:Review`
- `:ReasoningTrace`
- `:RetrievalContext`
- `:AgentMemory`
- `:Synthesis`
- Claim lifecycle
- Promotion rules

All schemas follow the same style as your Period/Person/Subject/Agent definitions.

---

# ## Claim Node Schema ⭐ Agent Assertions About the Graph

### Node Labels

```cypher
:Claim
```

### Purpose

A **Claim** is an assertion made by an Agent about the world, expressed as proposed or interpreted graph structure (nodes + edges).  
Claims support multi‑agent review, provenance, reasoning transparency, and controlled promotion of proposed structure into validated KG facts.

---

## Required Properties

|Property|Type|Format|Example|Notes|
|---|---|---|---|---|
|`claim_id`|string|text|`"claim_000123"`|**Unique** (enforce DB constraint)|
|`text`|string|text|`"Caesar crossed the Rubicon in 49 BCE."`|Human-readable|
|`claim_type`|string|enum|`"factual"`|`"factual"`, `"interpretive"`, `"causal"`, `"temporal"`|
|`source_agent`|string|text|`"roman_republic_agent_001"`|Originating agent|
|`timestamp`|string|ISO 8601|`"2026-02-12T15:30:00Z"`|Creation time|
|`status`|string|enum|`"proposed"`|`"proposed"`, `"validated"`, `"disputed"`, `"rejected"`|
|`confidence`|float|[0,1]|`0.85`|Agent’s internal confidence|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`provenance`|string[]|`["Plutarch 32","Suetonius 31"]`|Source citations|
|`review_count`|int|`3`|Number of reviews|
|`consensus_score`|float|`0.78`|Aggregated review confidence|
|`claim_scope`|string|`"Battle of Actium casualties"`|Short domain label|
|`reasoning_trace_id`|string|`"trace_000987"`|Associated trace|
|`proposed_nodes`|string[]|IDs|Proposed nodes|
|`proposed_edges`|string[]|IDs|Proposed edges|
|`promoted`|boolean|`false`|Whether graph delta applied|

---

## Required Edges

|Relationship|Target|Cardinality|Notes|
|---|---|---|---|
|`MADE_CLAIM`|Agent|1|Originating agent|
|`SUBJECT_OF`|Entity/SubjectConcept|1+|At least one entity or concept|

---

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|ProposedEdge|Claim proposes a relationship|
|`HAS_TRACE`|ReasoningTrace|Primary reasoning trace|
|`HAS_RETRIEVAL_CONTEXT`|RetrievalContext|Optional direct link|

---

# ## ProposedEdge Node Schema ⭐ Proposed Relationships Awaiting Validation

### Node Labels

```cypher
:ProposedEdge
```

### Purpose

Represents a relationship proposed by a claim that has not yet been materialized.  
Once validated, the ProposedEdge is converted into an actual relationship.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`edge_id`|string|`"pedge_001"`|**Unique**|
|`edge_type`|string|`"PARTICIPATED_IN"`|Relationship type|
|`from_qid`|string|`"Q1048"`|Source node identifier|
|`to_qid`|string|`"Q193304"`|Target node identifier|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|Proposal time|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`confidence`|float|`0.82`|Edge-level confidence|
|`edge_properties`|JSON|`{"role":"commander"}`|Properties to apply on promotion|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`PROPOSES`|Claim|`(claim)-[:PROPOSES]->(pedge)`|

---

# ## Review Node Schema ⭐ Multi-Agent Evaluation of Claims

### Node Labels

```cypher
:Review
```

### Purpose

A **Review** is a single agent’s evaluation of a Claim, including confidence, fallacies, and reasoning summary.  
Reviews feed into consensus scoring and claim status updates.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`review_id`|string|`"review_000456"`|**Unique**|
|`agent_id`|string|`"naval_warfare_agent"`|Reviewer|
|`claim_id`|string|`"claim_000123"`|Claim reviewed|
|`timestamp`|string|`"2026-02-12T16:00:00Z"`|Review time|
|`confidence`|float|`0.72`|Reviewer’s confidence|
|`verdict`|string|`"support"`|`"support"`, `"challenge"`, `"uncertain"`|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`fallacies_detected`|string[]|`["anachronism","post_hoc"]`|Fischer fallacies|
|`reasoning_summary`|string|`"Plutarch exaggerates casualties"`|Short explanation|
|`evidence_refs`|string[]|`["Goldsworthy p.145"]`|Evidence|
|`bayesian_posterior`|float|`0.68`|Bayesian update|
|`weight`|float|`1.0`|Reviewer weight|
|`reasoning_trace_id`|string|`"trace_001234"`|Optional reviewer trace|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`REVIEWED`|Agent|Reviewer|
|`REVIEWS`|Claim|Claim being reviewed|
|`HAS_TRACE`|ReasoningTrace|Optional reviewer trace|

---

# ## ReasoningTrace Node Schema ⭐ How a Claim Was Derived

### Node Labels

```cypher
:ReasoningTrace
```

### Purpose

Captures the reasoning path by which an agent produced a claim: what was asked, what was retrieved, how steps were chained, and which sources were consulted.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`trace_id`|string|`"trace_000987"`|**Unique**|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent|
|`query_text`|string|`"How did Caesar become dictator?"`|Original query|
|`timestamp`|string|`"2026-02-12T15:30:00Z"`|Reasoning time|
|`pattern`|string|`"causal_chain"`|Reasoning pattern|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`steps`|string[]|`["Retrieved X","Connected X→Y"]`|Reasoning steps|
|`sources_consulted`|string[]|`["Goldsworthy p.145"]`|Bibliographic refs|
|`retrieved_passages`|JSON[]|snippets|Key passages|
|`intermediate_claims`|string[]|IDs|Supporting claims|
|`confidence`|float|`0.85`|Reasoning confidence|
|`reasoning_depth`|int|`3`|Depth of chain|
|`fallacy_checks`|string[]|`["anachronism: pass"]`|Fallacy checks|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`TRACE_OF`|Claim|Primary claim|
|`USED_CONTEXT`|RetrievalContext|Retrieval used|

---

# ## RetrievalContext Node Schema ⭐ What Was Retrieved From Private Stores

### Node Labels

```cypher
:RetrievalContext
```

### Purpose

Captures which documents and passages were retrieved from an agent’s private vector store for a given query or claim.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`retrieval_id`|string|`"ret_000555"`|**Unique**|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent|
|`timestamp`|string|`"2026-02-12T15:30:02Z"`|Retrieval time|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`query_text`|string|`"How did Caesar become dictator?"`|Embedding query|
|`query_embedding_model`|string|`"text-embedding-ada-002"`|Model used|
|`doc_ids`|string[]|IDs|Works retrieved|
|`passage_ids`|string[]|IDs|Chunk IDs|
|`snippet_texts`|JSON[]|snippets|Retrieved passages|
|`retrieval_params`|JSON|`{"k":10}`|Search parameters|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`USED_FOR`|ReasoningTrace|Used in reasoning|

---

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`RETRIEVED_FROM`|Work|Direct bibliographic link|

---

# ## AgentMemory Node Schema ⭐ Persistent Agent Session Context

### Node Labels

```cypher
:AgentMemory
```

### Purpose

Persists longer-lived agent context across sessions: topics covered, entities/concepts discussed, user interests, and open questions.

Supports both:

- **rolling state** (MERGE on `agent_id`)
- **snapshot history** (multiple nodes)

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`memory_id`|string|`"mem_000321"`|**Unique**|
|`agent_id`|string|`"roman_republic_agent_001"`|Agent|
|`timestamp`|string|`"2026-02-12T15:35:00Z"`|Recorded time|
|`memory_type`|string|`"interaction_history"`|Memory category|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`topics_covered`|string[]|`["Roman politics"]`|Topics|
|`entities_mentioned`|string[]|`["Q1048"]`|Entities|
|`concepts_discussed`|string[]|`["sh85115055"]`|Concepts|
|`user_interests`|string[]|`["Roman politics"]`|User profile|
|`follow_up_questions`|string[]|`["What happened next?"]`|Open questions|
|`current_focus`|string|`"Roman Republic transitions"`|Agent focus|
|`working_hypothesis`|string|`"Caesar's dictatorship was constitutional"`|Hypothesis|
|`session_count`|int|`5`|Interaction count|
|`confidence_trajectory`|float[]|`[0.6,0.7,0.8]`|Confidence evolution|

---

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`MEMORY_OF`|Agent|Owner|
|`RELATED_TO`|Claim|Claims discussed|

---

# ## Synthesis Node Schema ⭐ Multi-Agent Consensus Resolution

### Node Labels

```cypher
:Synthesis
```

### Purpose

Represents multi-agent consensus-building when claims conflict or require consolidation.

---

## Required Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`synthesis_id`|string|`"synth_000789"`|**Unique**|
|`timestamp`|string|`"2026-02-12T16:15:00Z"`|Time|
|`synthesis_type`|string|`"claim_consolidation"`|Type|
|`consensus_method`|string|`"weighted_bayesian"`|Method|

---

## Optional Properties

|Property|Type|Example|Notes|
|---|---|---|---|
|`participating_agents`|string[]|IDs|Agents involved|
|`input_claims`|string[]|IDs|Claims merged|
|`output_claim`|string|ID|Resulting claim|
|`consensus_score`|float|`0.76`|Final score|
|`resolution_strategy`|string|`"weighted_average"`|Strategy|
|`notes`|string|`"Plutarch upper bound; Dio lower bound"`|Summary|

---

## Required Edges

|Relationship|Target|Notes|
|---|---|---|
|`SYNTHESIZED_FROM`|Claim|Input claims|
|`PRODUCED`|Claim|Output claim|

---

## Optional Edges

|Relationship|Target|Notes|
|---|---|---|
|`PERFORMED_BY`|Agent|Synthesis agent|

---

# ## Claim Status Lifecycle ⭐ State Machine

```
proposed → validated | disputed | rejected
```

### validated

- consensus_score ≥ 0.8
- majority verdict = "support"

### disputed

- 0.5 ≤ consensus_score < 0.8
- or mixed verdicts

### rejected

- consensus_score < 0.5
- majority verdict = "challenge"

---

# ## Promotion Rules ⭐ Applying Graph Deltas

When a claim becomes **validated**:

1. Convert `:ProposedEdge` nodes into real relationships
2. Apply `edge_properties`
3. Promote proposed nodes (if any)
4. Set `claim.promoted = true`
5. Attach provenance to resulting nodes/edges
6. Remove any `claim_status="proposed"` markers

Promotion is **idempotent**.

---

# ⭐ This is now the final, unified Claims Layer section — ready for your ontology.

If you want, I can now:

- integrate this into the full ontology doc
- generate the Claims Manager algorithm
- generate Cypher templates for claim creation, review, and promotion
- generate the Bayesian review engine
- generate the ProposedNode schema (if you want to support proposed nodes explicitly)

Just tell me where you want to go next.





