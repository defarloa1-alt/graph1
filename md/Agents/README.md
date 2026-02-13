# Agent Work Archive - December 12, 2025

## Why Archived

These documents were created during an exploration of ChatGPT agent architectures for the Chrystallum framework. They were archived because:

1. **Architecture still being defined** - Multi-agent coordination (SME â†’ Mediating â†’ Persistence) needs more design work
2. **Key decisions pending** - How to handle claim conflicts, citation as nodes, confidence-based merging
3. **Premature implementation** - Better to design the architecture carefully before building agent prompts

## What's Archived

### System Maintenance Agent (Not Needed)
- `CHATGPT_AGENT_PROMPT.md` - Agent to help users understand/use Chrystallum system
- `AGENT_TRAINING_FILES.md` - Files to train the system agent
- `AGENT_IMPLEMENTATION_GUIDE.md` - How to create the system agent
- `AGENT_README.md` - Overview of system agent

**Why archived:** This was a "help desk" agent to answer questions about the Chrystallum system itself. Not the core use case.

### Test Subject Agent (Architecture Unclear)
- `TEST_SUBJECT_AGENT_PROMPT.md` - Roman Republic historian to test extraction
- `TEST_SUBJECT_AGENT_FILES.md` - Training files for test subject

**Why archived:** Good concept (SME agent generates subgraphs for testing), but architecture decisions needed:
- Should return JSON (not Cypher) - confirmed
- Should include confidence scores with reasoning - confirmed
- Should include citations as nodes - confirmed
- How to handle claim conflicts - **NOT DEFINED**
- Multi-agent coordination - **NOT DEFINED**

### Graph Insights (Useful Concepts)
- `GRAPH_INSIGHT_SUMMARY.md` - Why relationships are the core value of graphs

**Why archived:** Created during agent work, but contains useful fundamental concepts:
- Relationships ARE the data (not just metadata)
- Subgraph generation vs entity extraction
- Graph-first thinking
- Sparse vs rich subgraphs

**Note:** This document has valuable concepts that should inform future architecture, even though it was written in the context of agent work.

---

## What's NOT Archived (Still Active)

### Core Framework Files (Kept in Root)
- `md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md` - Node type templates (Person, Event, Place, etc.)
  - **Why kept:** Useful regardless of agent architecture
  - Defines required properties and edges for each node type
  - Can be used by any extraction system (agents, manual, automated)

---

## Key Architectural Questions (Still Open)

### 1. Claim Conflicts
**Scenario:** New claim contradicts existing subgraph
```
Existing: (Caesar)-[:BORN_IN {confidence: 0.8}]->(Rome)
New:      (Caesar)-[:BORN_IN {confidence: 0.9}]->(Subura)
```
**Options:**
- Replace (higher confidence wins)
- Additive (keep both, mark conflict)
- Ignore (first claim wins)
- Debate (trigger mediating agent)

**Decision needed:** Which strategy? When?

### 2. Citation as Nodes
**Concept:** Citations are first-class entities, not just properties
```cypher
(claim)-[:CITED_BY]->(source:Citation {
  author_qid: "Q203787",  // Plutarch
  work: "Life of Caesar",
  passage: "Born in Subura district"
})
```

**Questions:**
- How do citations affect confidence?
- Can multiple citations support one claim?
- Do we track citation chains?
- How to model contradictory sources?

### 3. Multi-Agent Coordination
**Proposed Flow:**
```
User Query 
  â†’ SME Agent (JSON claims with confidence)
  â†’ Mediating Agent (validates, resolves conflicts)
  â†’ Persistence Agent (converts to Cypher, imports)
  â†’ Neo4j
```

**Questions:**
- What format for agent-to-agent communication?
- When does mediating agent trigger?
- How does debate/validation work?
- Who decides which claim wins?

### 4. Confidence Reasoning
**Example:**
```json
{
  "claim": {...},
  "confidence": 0.95,
  "reasoning": "Multiple primary sources agree",
  "sources": ["Q203787", "Q6233"],
  "conflicts_with": []
}
```

**Questions:**
- How to calculate confidence scores?
- How do sources affect confidence?
- Does agent explain its reasoning?
- Can users override confidence?

### 5. Subgraph Merging
**Scenarios:**
- **Additive:** New claim extends existing (Caesar crossed Rubicon + Caesar born in Rome)
- **Conflicting:** New claim contradicts (born in Rome vs born in Subura)
- **Refining:** New claim adds detail (born in Rome â†’ born in Subura district of Rome)

**Questions:**
- How to detect each scenario?
- Different strategies for each?
- Who decides (agent or user)?

---

## Useful Concepts to Preserve

### From GRAPH_INSIGHT_SUMMARY.md

**Core Insight:** In knowledge graphs, **relationships ARE the value**, not entities.

**Key Points:**
1. **Subgraph generation** - Agents should return connected nodes + edges, not just entities
2. **Relationship-centric** - Focus on maximizing edges, not just node properties
3. **Graph density** - Measure edges-per-node ratio (target: 1.5-2.0)
4. **Multi-hop paths** - Rich subgraphs enable discovery queries
5. **Explorable networks** - The goal is query-ability, not just storage

**Example:**
```cypher
// Low value (1 node, 0 edges)
(caesar:Person)

// High value (5 nodes, 7 edges)
(caesar)-[:CROSSED]->(rubicon)
(caesar)-[:OPPOSED_BY]->(senate)
(caesar)-[:COMMANDED]->(legion)
(crossing)-[:CAUSED]->(civil_war)
(crossing)-[:POINT_IN_TIME]->(year_49)
```

**Metric:** Edges-per-query matters more than nodes-per-query

### From TEST_SUBJECT_AGENT_PROMPT.md

**Good Patterns:**
- Agent returns structured subgraphs, not prose
- Every entity needs QID, type_qid, cidoc_class
- Relationship types must be from canonical list
- Temporal properties in ISO 8601
- Geographic entities need coordinates

**To Carry Forward:**
- Schema-driven generation (use md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md)
- Canonical relationship types only
- CIDOC-CRM alignment
- Wikidata integration

---

## When to Revisit

Come back to this archive when:

1. âœ… Multi-agent architecture is designed
2. âœ… Claim/conflict resolution strategy is defined
3. âœ… Citation model is specified
4. âœ… Confidence calculation is designed
5. âœ… Agent coordination protocol is established

Then extract:
- Useful patterns from TEST_SUBJECT_AGENT_PROMPT.md
- Graph insights from GRAPH_INSIGHT_SUMMARY.md
- Update with new architecture decisions

---

## What to Build Next

### Option A: Start with Single Agent
Build just the SME agent that:
- Returns JSON (not Cypher)
- Includes confidence + reasoning
- Includes citation node references
- No conflict resolution (always additive)
- Test manually before adding mediating agent

### Option B: Design Multi-Agent First
Spec out the complete architecture:
1. SME agent protocol (JSON format)
2. Mediating agent logic (validation rules)
3. Persistence agent (Cypher generation)
4. Agent coordination (message passing)
5. Conflict resolution (policies)

Then implement all at once.

---

**Archived:** December 12, 2025  
**Reason:** Architecture decisions needed before implementation  
**Status:** Concepts useful, implementation premature  
**Next Step:** Design multi-agent coordination and claim resolution  

**Key Takeaway:** The work here identified the right questions, even if the answers aren't ready yet.


