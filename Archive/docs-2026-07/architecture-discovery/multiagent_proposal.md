This is a rich architectural problem that maps well onto known patterns. Here's a comprehensive breakdown:

***

## The Core Problem: Fragmented Claims Across Facets

You've identified what's classically called the **multi-perspective assertion problem** in knowledge graph systems. When your Military SFA and Bio SFA both independently "discover" Caesar crossing the Rubicon, you get claim duplication — but that duplication actually contains signal. The question is whether the system should **deduplicate to a canonical event** or **preserve both perspectives as distinct but linked assertions**. [youtube](https://www.youtube.com/watch?v=MPKd9t_XXOQ)

The answer that best fits Chrystallum is: **canonical event node + perspective-scoped claim edges**, which is a well-studied pattern.

***

## Pattern 1: The Canonical Event Node (Your Foundation)

CIDOC-CRM solved this exact problem at the ontology level. Its **E5 Event** class is defined as "changes of states in cultural, social or physical systems...brought about by a series of coherent physical, cultural, or legal phenomena." The key insight is: [ontome](https://ontome.net/class/5/namespace/1)

> **The event exists once. Perspectives on it multiply.**

In your Neo4j model, Caesar crossing the Rubicon (January 49 BCE) should be **one node** — `(:Event {id: "rubicon_crossing", date: "49-01 BCE"})`. Both SFAs do not *own* it; they *assert claims about it from their facet perspective*. The relationships they create hang off that canonical node:

```cypher
(military_sfa)-[:ASSERTS {facet:'MILITARY', confidence:0.9, predicate:'was_military_escalation'}]->(rubicon_event)
(bio_sfa)-[:ASSERTS {facet:'BIOGRAPHIC', confidence:0.95, predicate:'was_career_defining_act'}]->(rubicon_event)
```

This is precisely how Wikidata handles it — one item, many claims from many sources. The Bio SFA does not own the event; it owns the **biographical interpretation** of it. [blog.metaphacts](https://blog.metaphacts.com/citation-needed-provenance-with-rdf-star)

***

## Pattern 2: The Blackboard Architecture (Your Coordination Layer)

The pattern you need to prevent fragmentation is the **Blackboard Architecture**, a foundational AI pattern from the 1970s that is seeing a major revival in LLM-based multi-agent systems. It maps onto your concern almost perfectly: [rajatpandit](https://rajatpandit.com/agentic-ai/the-blackboard-architecture/)

- **The Blackboard**: your Neo4j graph itself, the shared world model. Every agent reads and writes here. It stores entities, relationships, provenance, confidence scores, and task state. [youtube](https://www.youtube.com/watch?v=MPKd9t_XXOQ)
- **Knowledge Sources (Agents)**: your SFAs — they do not talk to each other directly. They interact solely through the board. [rajatpandit](https://rajatpandit.com/agentic-ai/the-blackboard-architecture/)
- **Control Shell / Orchestrator**: the Subject Concept Agent that spawned them, or a dedicated coordination layer that decides what gets written and resolves contention.

Research at Google has shown the Blackboard paradigm outperforms master-slave and RAG baselines by 13–57% in multi-agent data science tasks. The key property relevant to your case: **a conflict model that treats disagreement as data rather than an error to be silently overwritten**. [research](https://research.google/pubs/blackboard-multi-agent-systems-for-information-discovery-in-data-science/)

***

## Pattern 3: Claim Provenance via Named Graphs / RDF-star Logic

In your Neo4j context, this maps to **edge-level metadata (relationship properties)** on every claim:

```cypher
(sfa)-[:CLAIMS {
  facet: 'MILITARY',
  agent_id: 'military_sfa_001',
  confidence: 0.87,
  source_wikidata: 'Q40979',
  submitted_at: timestamp(),
  predicate_status: 'CONFIRMED' // or TBD
}]->(event_node)
```

This is equivalent to RDF Named Graphs for provenance — each claim carries its own epistemic context. The PROV-O vocabulary pattern is: *who asserted it, when, from what source, with what confidence*. Neo4j's relationship properties make this native. [ld4pe.dublincore](https://ld4pe.dublincore.org/competency_index/d2695955/s2695991/s2696007/s2709875/)

***

## Pattern 4: The Two-Phase SFA Model You Described

Your intuition about two SFA functions is correct and has a formal equivalent:

| Phase | Function | Known As |
|---|---|---|
| Phase 1 | Learn + submit claims | **Knowledge Acquisition** (KA phase) |
| Phase 2 | Review peer claims from own facet perspective | **Critique / Peer Review** (the Blackboard "Consensus Loop") |

The Blackboard Consensus Loop forces iterative peer-review directly on the board before claims are promoted to confirmed status, which "drastically reduces hallucination rates before the final output." For Chrystallum this means: [rajatpandit](https://rajatpandit.com/agentic-ai/the-blackboard-architecture/)

1. Military SFA submits: `(:Event)<-[:MILITARY_CLAIM {predicate:'TBD', confidence:0.6}]-(military_sfa)`
2. Bio SFA submits its own claim on the same event node
3. In Phase 2, Military SFA *reads* the Bio SFA's claim and adds a review edge: `(military_sfa)-[:REVIEWED {agrees: true, note:'confirms military context'}]->(bio_claim)`
4. The Control Shell promotes the event's `predicate_status` from `TBD` to `CONFIRMED` once consensus threshold is met

***

## Handling the Specific Caesar/Rubicon Conflict

The deduplication pipeline works as follows: [decodingai](https://www.decodingai.com/p/keep-knowledge-graph-clean)

1. **Entity Resolution first**: Before writing, each SFA queries: `MATCH (e:Event) WHERE e.wikidata_qid = 'Q...' RETURN e`. If found, the canonical node exists — do not create a duplicate.
2. **Confidence-weighted merge**: If two SFAs create near-duplicate events (same date, same actors, similar description), your orchestrator runs a similarity check. High confidence (≥0.95) → auto-merge. Medium (0.85–0.95) → flag for human review. Low → new node. [decodingai](https://www.decodingai.com/p/keep-knowledge-graph-clean)
3. **Facet claim edges proliferate freely**: Both SFAs write their own `:ASSERTS` edge with facet metadata. This is not fragmentation — it's richness. The Military SFA's interpretation and the Bio SFA's interpretation are both valid and complementary.

***

## Tools and Frameworks to Consider

| Tool/Pattern | Fit for Chrystallum | Notes |
|---|---|---|
| **LangGraph** | High | Native support for Blackboard-style shared state, checkpointing, and time-travel debugging [rajatpandit](https://rajatpandit.com/agentic-ai/the-blackboard-architecture/) |
| **Neo4j as shared blackboard** | Very High | NODES AI 2026 session explicitly covers multi-agent shared graph memory with Cypher examples [youtube](https://www.youtube.com/watch?v=MPKd9t_XXOQ) |
| **PROV-O / RDF-star metadata** | High | Edge-level provenance on every claim; already native to Neo4j relationship properties [blog.metaphacts](https://blog.metaphacts.com/citation-needed-provenance-with-rdf-star) |
| **CIDOC-CRM E13 Attribute Assignment** | High | Formal class for "an agent asserting a property of an object" — maps cleanly to your SFA claim pattern [linked](https://linked.art/model/profile/class_analysis/) |
| **n-ary relationship nodes** | Medium | For complex claims with multiple qualifiers, reify the claim as a node rather than an edge |

***

## Recommended Chrystallum Architecture

The concise design that resolves your fragmentation concern:

1. **One canonical `:Event` node per real-world event**, keyed by Wikidata QID where possible
2. **Each SFA writes `:CLAIMS` edges** (not ownership) — the Bio SFA owns the *person*, not the events they participated in
3. **All SFA-to-graph writes go through a Claim Registry** (a lightweight Control Shell) that checks for existing canonical nodes before allowing creation
4. **Phase 2 review** is a separate pass where each SFA iterates over claims *tagged by other facets* for the same event and writes a `:REVIEWED` edge
5. **Predicate promotion**: claims start as `predicate_status: TBD` and get promoted to `CONFIRMED` after N facet reviews agree, or `CONTESTED` if reviews conflict — **treating disagreement as data** [youtube](https://www.youtube.com/watch?v=MPKd9t_XXOQ)

The key mental model shift: your SFAs are not competing claim-owners — they are **multiple witnesses to the same events, each testifying from their domain expertise**. The graph holds the canonical event; the SFAs hold the interpretations.