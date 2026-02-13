Here is a cleaned‑up, detailed Agent section that incorporates the comments in 2‑12‑26-Agent-Schema and tightens the semantics around scope, training, confidence, coordination, splitting, and historian logic. You can drop this into your architecture doc as the canonical agent model. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/efe642f5-3182-4f8d-97d0-88672a370339/2-12-26-Agent-Schema.md)

```markdown
## Agent Architecture ⭐ Scope, Training, Assignment & Coordination

### Node Labels
```cypher
:Agent
```

**Purpose:** Agents are bounded, subject‑specialized worker processes that operate over both the Entity layer and the SubjectConcept layer. They are not generic LLMs. Each agent is scoped to a deterministic slice of the graph, ingests a bounded corpus within that scope, answers queries within its domain, and routes out‑of‑scope queries to other agents.

**Canonical Definition**

> An agent is a bounded worker process whose role is defined by:
> 1. **Authority‑scoped SubjectConcept coverage** (scheme + facet + LCSH/FAST hierarchy position + optional Dewey/LCC bands)
> 2. **Allowed entity types** plus optional temporal/spatial constraints
> 3. **An operational function**: specialist (Subject or Entity) or coordinator/synthesizer
>
> “Training” means:
> - (a) defining scope via graph filters over SubjectConcepts, entities, periods, and places, and  
> - (b) indexing/ingesting a bounded corpus within that scope (RAG‑style).  
> It does **not** mean updating model weights.
>
> Agents share graph‑level artifacts (nodes, edges, annotations, provenance). Agents do **not** share internal embeddings, vector stores, or retrieval indexes.

---

## Agent Types

### 1. Subject Agents

_“I know everything about this topical domain.”_

Subject Agents are scoped by **SubjectConcept** nodes, not directly by entity types.

A Subject Agent’s scope is defined by:

- The SubjectConcept’s **facet**:
  - `topical`, `discipline`, `geo`, `event`, `chronological`, `form`, `name`, etc.
- Its **position** in the LCSH/FAST broader/narrower hierarchy.
- Its **authority metadata**:
  - Dewey range, LCC range, FAST facets, etc.
- Its **domain**:
  - history, law, religion, economics, linguistics, etc.

**Scope formula (informal)**

```text
Scope(subject_agent) =
  Primary SubjectConcept(s)
  + descendant concepts (narrower terms via BROADER_THAN traversal)
  + (optionally) ancestor concepts if included
  + all entities mapped to those concepts (via HAS_SUBJECT_CONCEPT)
  + all works ABOUT those entities or concepts
```

**Key rule:** Subject Agents do **not** own entities; they own SubjectConcepts. Entities enter their scope only through `HAS_SUBJECT_CONCEPT` mappings.

**Spawning**

If a SubjectConcept has many narrower terms or the domain becomes too broad, a Subject Agent may spawn:

- narrower **topical** agents,
- narrower **discipline** agents,
- narrower **geo** agents,
- or other facet‑specific sub‑agents.

This mirrors the LCSH/FAST tree.

---

### 2. Entity Agents

_“I know everything about this type of thing in the world.”_

Entity Agents correspond to first‑class ontology types:

- Person Agent
- Place Agent
- Event Agent
- Period Agent
- Organization Agent
- Material Agent
- Object Agent
- Activity Agent

An Entity Agent’s scope includes:

```text
Scope(entity_agent) =
  All nodes of the agent’s entity type
  + all edges relevant to that type (e.g. Person → BORN_IN, LIVED_DURING)
  + all SubjectConcepts linked to those entities (classification metadata)
  + all works ABOUT those entities
  + all Wikidata enrichment for those entities
```

**Key rule:** Entity Agents do **not** traverse the SubjectConcept hierarchy for routing; they use SubjectConcepts as classification metadata on entities.

**Spawning**

- Period Agent → sub‑agents by dynasty / sub‑period / region.
- Place Agent → sub‑agents by region / province / city / site.
- Event Agent → sub‑agents by battles / treaties / campaigns.

---

### 3. Coordinator Agents

_“I decide who should handle this.”_

Coordinator Agents include:

- **Orchestrator Agent** – inspects incoming queries, grounds them to concepts/entities, selects and dispatches specialist agents.
- **Synthesis Agent** – collects results from multiple specialists and integrates them into a coherent answer.
- **Assignment Agent** – resolves which agent owns a given concept or entity when ownership is ambiguous.
- **Boundary Agent** – detects when a query or concept falls outside all existing agent scopes and triggers scope expansion or agent creation.

Coordinator Agents do not own domains. They own the **routing, boundary detection, and integration process**.

---

## Agent Node Schema

### Required Properties

| Property       | Type   | Format   | Example                       | Notes                                                   |
|----------------|--------|----------|-------------------------------|---------------------------------------------------------|
| `agent_id`     | string | text     | `"roman_republic_agent_001"` | Unique agent identifier                                 |
| `name`         | string | text     | `"Roman Republic Specialist"` | Human‑readable name                                     |
| `agent_type`   | string | enum     | `"subject"`                   | `"subject"`, `"entity"`, `"coordinator"`               |
| `status`       | string | enum     | `"active"`                    | `"initializing"`, `"active"`, `"paused"`               |
| `last_trained` | string | ISO 8601 | `"2026-02-12"`                | Last scope refresh / corpus ingestion date             |

### Optional Properties (Scope Configuration)

| Property        | Type     | Format   | Example                         | Notes                                                  |
|-----------------|----------|----------|---------------------------------|--------------------------------------------------------|
| `facet_filter`  | string[] | text     | `["topical","discipline"]`      | Which SubjectConcept facets this agent covers          |
| `scheme_filter` | string[] | text     | `["LCSH","FAST"]`               | Which authority schemes                                |
| `lcc_range`     | string   | text     | `"DG235-254"`                   | LCC class range                                       |
| `dewey_range`   | string   | text     | `"937.02-.05"`                  | Dewey range                                           |
| `entity_types`  | string[] | text     | `["Person","Event","Place"]`    | Allowed entity labels (for entity agents)             |
| `temporal_start`| string   | ISO 8601 | `"-0510"`                       | Earliest time bound                                   |
| `temporal_end`  | string   | ISO 8601 | `"-0027"`                       | Latest time bound                                     |
| `spatial_qids`  | string[] | Q[0-9]+  | `["Q220"]`                      | Place QIDs constraining geographic scope              |

### Example Agent Node

```json
{
  "agent_id": "roman_republic_agent_001",
  "name": "Roman Republic Specialist",
  "agent_type": "subject",
  "status": "active",
  "last_trained": "2026-02-12",
  "facet_filter": ["topical", "discipline"],
  "scheme_filter": ["LCSH"],
  "lcc_range": "DG235-254",
  "dewey_range": "937.02-.05",
  "entity_types": ["Person", "Event", "Place", "Organization"],
  "temporal_start": "-0510",
  "temporal_end": "-0027",
  "spatial_qids": ["Q220"]
}
```

---

## Agent Relationships (Graph Edges)

Only three materialized edge types are required. Everything else is derived at query time.

| Relationship       | Source | Target         | Notes                                                            |
|--------------------|--------|----------------|------------------------------------------------------------------|
| `OWNS_DOMAIN`      | Agent  | SubjectConcept | Agent’s primary subject scope (manually or rule‑assigned)       |
| `INCLUDES_CONCEPT` | Agent  | SubjectConcept | Auto‑expanded narrower concepts within owned domains            |
| `TRAINS_ON`        | Agent  | Work           | Works in the agent’s ingested corpus                            |

**Why only three?**

Edges like `KNOWS_ABOUT` (agent→entity) and `EXPERT_ON` (agent→entity) are derivable via:

```cypher
// Entities in agent's domain (derived, not materialized)
MATCH (agent:Agent)-[:OWNS_DOMAIN|INCLUDES_CONCEPT]->(sc:SubjectConcept)
MATCH (entity)-[:HAS_SUBJECT_CONCEPT]->(sc)
RETURN DISTINCT entity;
```

Materializing such edges would duplicate information already encoded in `HAS_SUBJECT_CONCEPT` and create a maintenance burden.

### Setup Patterns

```cypher
// 1. Assign primary domain
MATCH (agent:Agent {agent_id: "roman_republic_agent_001"})
MATCH (sc:SubjectConcept)
WHERE sc.authority_id IN ["sh85115055", "sh85114934"]
  AND sc.facet IN ["topical", "discipline"]
MERGE (agent)-[:OWNS_DOMAIN]->(sc);

// 2. Auto‑expand to narrower concepts (1–2 hops)
MATCH (agent:Agent {agent_id: "roman_republic_agent_001"})-[:OWNS_DOMAIN]->(sc:SubjectConcept)
MATCH (sc)<-[:BROADER_THAN*1..2]-(narrower:SubjectConcept)
WHERE narrower.scheme = "LCSH"
MERGE (agent)-[:INCLUDES_CONCEPT]->(narrower);

// 3. Assign corpus (works about owned/included concepts)
MATCH (agent:Agent {agent_id: "roman_republic_agent_001"})-[:OWNS_DOMAIN|INCLUDES_CONCEPT]->(sc:SubjectConcept)
MATCH (work:Work)-[:ABOUT]->(sc)
MERGE (agent)-[:TRAINS_ON]->(work);
```

---

## Training (Scope Definition + Corpus Ingestion)

Training has **two phases**. Neither involves weight updates.

### Phase A: Scope Definition (deterministic, graph‑driven)

1. **SubjectConcept Assignment** – assign primary SubjectConcepts via `OWNS_DOMAIN`.
2. **Hierarchy Expansion** – auto‑include narrower concepts via `INCLUDES_CONCEPT`.
3. **Entity Discovery** – derive in‑scope entities via `HAS_SUBJECT_CONCEPT` (no agent→entity edges).
4. **Time/Space Bounds** – apply `temporal_start`, `temporal_end`, and `spatial_qids` as additional filters.

This produces a **bounded subgraph** per agent.

### Phase B: Corpus Ingestion (RAG‑style indexing)

1. **Work Assignment** – find all works linked via `ABOUT` to owned/included concepts; create `TRAINS_ON`.
2. **Local Indexing** – each agent builds a **private** retrieval index over its `TRAINS_ON` works (vector store, BM25, or hybrid). Indexes are per‑agent and never shared.
3. **Delta Updates** – when new works, entities, or SubjectConcepts appear, agents update only on deltas (new nodes/edges, changed properties, new subject mappings).

**Example Corpus (Roman Republic Agent)**

```text
Primary:
  - Livy, Ab Urbe Condita
  - Polybius, Histories
  - Cicero, Letters & Orations

Secondary:
  - Goldsworthy, Pax Romana (chapters 1–5)
  - Scullard, History of the Roman Republic

Archaeological:
  - Coin catalogs (Q‑identifiers)
  - Inscription databases (CIL references)
```

---

## Query Assignment (Routing)

The Orchestrator Agent handles routing in three steps.

### Step 1: Query Grounding

Resolve query terms to entities and/or SubjectConcepts.

Example: “How did Julius Caesar cross the Rubicon?”

```cypher
MATCH (caesar:Person {qid: "Q1048"})
MATCH (rubicon:Place {qid: "Q13189"})
MATCH (event:Event {qid: "Q193304"})  // Crossing of Rubicon

MATCH (caesar)-[:HAS_SUBJECT_CONCEPT]->(sc1:SubjectConcept)
MATCH (event)-[:HAS_SUBJECT_CONCEPT]->(sc2:SubjectConcept)
RETURN sc1, sc2;
// e.g. "Caesar, Julius"; "Rome--History--Republic, 510-30 B.C."
```

### Step 2: Agent Selection

Match grounded concepts against agent domains.

```cypher
MATCH (agent:Agent)-[:OWNS_DOMAIN|INCLUDES_CONCEPT]->(sc:SubjectConcept)
WHERE sc.authority_id IN $grounded_concept_ids
RETURN agent.agent_id, agent.name, count(sc) AS coverage
ORDER BY coverage DESC
LIMIT 3;
```

**Facet priority (when multiple agents match the same concept)**

When several agents match, preference can use a facet priority order:

```text
name > geo > event > chronological > discipline > topical
```

Intuition: name and geo agents are more specific; topical is broad.

### Step 3: Dispatch

- If one agent adequately covers all concepts → **Single Agent** pattern.
- If multiple agents are needed → **Multi‑Agent** pattern (sequential or parallel, plus synthesis).
- If no agent covers a concept → **Boundary Agent** and Orchestrator:
  - extend agent domains (adding `OWNS_DOMAIN`/`INCLUDES_CONCEPT`),
  - or create new specialized agents.

---

## Coordination Patterns

### Pattern A: Single Agent (simple query)

```text
User: "Who was Cicero?"
→ Grounding: Person (Q1541) + SubjectConcept (sh85024937)
→ Agent: roman_republic_agent_001
→ Response: direct answer from that agent's corpus
```

### Pattern B: Sequential Multi‑Agent (cross‑temporal query)

```text
User: "How did Roman military tactics evolve from Republic to Empire?"

→ Grounding: Republic period + Empire period + "Rome—Army" SubjectConcept
→ Agents:
   - republican_military_agent → Republic tactics
   - imperial_military_agent   → Empire tactics
   - synthesis_agent           → combine into one narrative
→ Response: integrated cross‑period analysis
```

### Pattern C: Hierarchical Delegation (multi‑domain query)

```text
User: "Compare Roman and Carthaginian naval strategies"

→ Coordinator: naval_warfare_coordinator
→ Delegates:
   - roman_naval_agent        → Roman naval tactics
   - carthaginian_agent       → Carthaginian background
   - battle_specialist_agent  → specific battles/campaigns
→ Synthesis: coordinator integrates perspectives
```

### Pattern D: Debate (conflicting evidence)

```text
User: "How many casualties at Boudicca's revolt?"

→ Agents:
   - roman_britain_agent
   - literary_sources_agent
   - archaeology_agent
→ Each agent provides estimates with provenance.
→ synthesis_agent presents ranges, sources, and evaluation of reliability.
```

### Pattern E: Cross‑Facet Fusion

“Cross‑facet fusion” occurs when agents from **different facets** collaborate on multi‑dimensional questions:

- geo agent + topical agent
- event agent + discipline agent
- name agent + topical agent

Example: “What happened in Rome during Caesar’s time?”

- Geo facet → Rome agent (`facet='geo'`).
- Name facet → Caesar agent (`facet='name'`).
- Chronological facet → first‑century BCE agent (`facet='chronological'`).
- Cross‑facet fusion agent intersects their scopes to produce the result set.

---

## Coordination Rules

1. **Shared grounding** – all agents read/write against the same entity and SubjectConcept nodes. No agent invents its own copy of Caesar or Rome.
2. **No embedding sharing** – agents share graph artifacts (nodes, edges, annotations, provenance), but never internal retrieval indexes.
3. **Provenance tagging** – derived data (estimates, interpretations, annotations) are tagged with:
   - `source_agent`
   - `confidence`
   - `provenance_work` (or works)
4. **Conflict resolution** – the Synthesis Agent uses domain‑specific rules, e.g.:
   - Epigraphic > literary for dates, names, unit designations.
   - Modern scholarship > ancient source for historiographical interpretations.
   - Multiple independent sources > single source.
5. **Boundary detection** – if a query concept falls outside `OWNS_DOMAIN|INCLUDES_CONCEPT`, the agent does not guess; it signals the Orchestrator/Boundary Agent:

```cypher
MATCH (query_concept:SubjectConcept {authority_id: $concept_id})
MATCH (agent:Agent {agent_id: $agent_id})-[:OWNS_DOMAIN|INCLUDES_CONCEPT]->(owned:SubjectConcept)
OPTIONAL MATCH path = (owned)<-[:BROADER_THAN*]-(query_concept)
WITH agent, query_concept, path
WHERE path IS NULL
// → outside agent domain; refer to Orchestrator/Boundary Agent
```

---

## Confidence Scoring

Each agent computes a confidence score before answering.

Core factors:

- **Concept overlap** – how many query SubjectConcepts are in the agent’s domain.
- **Entity overlap** – how many grounded entities are in the agent’s domain.
- **Corpus relevance** – how often those entities/concepts appear in the agent’s corpus.

**Added factors: temporal and spatial alignment**

Confidence is **increased** when the query’s time/place lies within the agent’s configured bounds.

Pseudo‑code:

```python
def confidence_score(self,
                     query_concepts,
                     query_entities,
                     query_temporal=None,
                     query_spatial=None):

    # Concept overlap (0–1)
    owned_concepts = self.get_owned_concepts()
    concept_overlap = len(query_concepts & owned_concepts) / max(len(query_concepts), 1)

    # Entity overlap (0–1)
    known_entities = self.get_in_scope_entities()
    entity_overlap = len(query_entities & known_entities) / max(len(query_entities), 1)

    # Corpus relevance (0–1)
    corpus_hits = self.count_corpus_mentions(query_entities)
    corpus_relevance = normalize(corpus_hits)

    # Temporal alignment (0, 0.5, 1)
    temporal_match = 0.0
    if query_temporal and self.temporal_start and self.temporal_end:
        if self.temporal_start <= query_temporal <= self.temporal_end:
            temporal_match = 1.0
        elif overlaps(query_temporal, (self.temporal_start, self.temporal_end)):
            temporal_match = 0.5

    # Spatial alignment (0, 0.7, 1)
    spatial_match = 0.0
    if query_spatial and self.spatial_qids:
        if query_spatial in self.spatial_qids:
            spatial_match = 1.0
        elif any(is_part_of(query_spatial, q) for q in self.spatial_qids):
            spatial_match = 0.7

    # Weighted score
    return (
        0.30 * concept_overlap +
        0.20 * entity_overlap +
        0.20 * corpus_relevance +
        0.15 * temporal_match +
        0.15 * spatial_match
    )
```

If `confidence < threshold` (e.g. 0.3), the agent declines and the Orchestrator reassigns or composes a multi‑agent response.

---

## Historian Logic & Bayesian Checks (Planned)

Each agent can optionally include a **Historian Logic Engine** to apply Bayesian reasoning and guardrails inspired by Fischer’s _Historians’ Fallacies_:

- Detect and penalize:
  - question‑begging,
  - anachronism,
  - post hoc causal fallacies,
  - “fallacy of motivation” (assuming intent without evidence).

High‑level behavior:

- Compute a **prior** from the agent’s corpus.
- Compute a **likelihood** based on how well evidence supports the claim.
- Apply **fallacy penalties** when patterns suggest weak reasoning.
- Output a **posterior confidence** used in the agent’s final answer and shared with the Synthesis Agent.

(Implementation details can live in a separate design note.)

---

## Agent Evolution

### New Work Ingestion

Detect new works in the agent’s domain that are not yet in its corpus:

```cypher
MATCH (work:Work)-[:ABOUT]->(sc:SubjectConcept)
MATCH (agent:Agent)-[:OWNS_DOMAIN|INCLUDES_CONCEPT]->(sc)
WHERE NOT EXISTS { (agent)-[:TRAINS_ON]->(work) }
  AND work.publication_date > agent.last_trained
MERGE (agent)-[:NEEDS_REINDEX]->(work);
```

### Domain Boundary Expansion

Suggest new SubjectConcepts for the agent’s domain based on co‑occurrence in works:

```cypher
MATCH (agent:Agent)-[:OWNS_DOMAIN]->(owned:SubjectConcept)
MATCH (work:Work)-[:ABOUT]->(owned)
MATCH (work)-[:ABOUT]->(related:SubjectConcept)
WHERE NOT EXISTS { (agent)-[:OWNS_DOMAIN|INCLUDES_CONCEPT]->(related) }
WITH agent, related, count(work) AS co_occurrence
WHERE co_occurrence > 10
RETURN related.heading AS suggest_expansion, co_occurrence
ORDER BY co_occurrence DESC;
```

### Agent Splitting

When an agent’s domain becomes too large, the Orchestrator may split it:

- Narrower **topical** agents (by subject branch).
- Narrower **temporal** agents (by sub‑ranges of `temporal_start`/`temporal_end`).
- Narrower **geographic** agents (by subsets of `spatial_qids`).

Heuristic: number of `INCLUDES_CONCEPT` concepts or total in‑scope entities exceeds a configured threshold.

---

## Agent Lifecycle

```text
1. CREATE     → Define Agent node with type and scope properties
2. SCOPE      → Assign SubjectConcepts via OWNS_DOMAIN
3. EXPAND     → Auto‑include narrower concepts via INCLUDES_CONCEPT
4. INGEST     → Build private corpus index via TRAINS_ON
5. SERVE      → Answer queries within domain
6. ROUTE      → Refer out‑of‑scope queries to Orchestrator/Boundary Agent
7. COORDINATE → Collaborate on multi‑domain queries via shared graph
8. EVOLVE     → Delta‑update scope and corpus; split when domains get large
```

---

## Example Agent Registry (Roman World)

| Agent ID                 | Type       | Primary Concepts                                         | LCC        | Temporal      | Entity Types                |
|--------------------------|-----------|----------------------------------------------------------|-----------|--------------|----------------------------|
| `republican_rome_agent` | subject   | `sh85115055` (Rome–History–Republic, 510–30 B.C.)       | DG235‑254 | −510 to −27  | Person, Event, Place, Org  |
| `imperial_rome_agent`   | subject   | `sh85115057` (Rome–History–Empire, 30 B.C.–476 A.D.)    | DG270‑365 | −27 to 476   | Person, Event, Place, Org  |
| `roman_military_agent`  | subject   | `sh85114937` (Rome—Army)                                | U35       | cross‑temporal| Event, Organization, Object |
| `roman_britain_agent`   | subject   | `sh85056721` (Great Britain–History–Roman period)       | DA145‑150 | −55 to 449   | Person, Event, Place       |
| `judaea_agent`          | subject   | `sh85070689` (Judaea–History)                           | DS110‑115 | −63 to 135   | Person, Event, Place       |
| `person_agent`          | entity    | (all Person nodes)                                      | —         | —            | Person                     |
| `event_agent`           | entity    | (all Event nodes)                                       | —         | —            | Event                      |
| `orchestrator`          | coordinator | (none; routes only)                                   | —         | —            | —                          |
| `synthesis_agent`       | coordinator | (none; integrates/debates only)                       | —         | —            | —                          |
```