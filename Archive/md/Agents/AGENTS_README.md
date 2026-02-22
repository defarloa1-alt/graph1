# Agents Directory

**Purpose:** Agent prompts, guides, and documentation for Chrystallum multi-agent system  
**Date:** December 12, 2025  
**Status:** Architecture in development

---

## Directory Structure

```
agents/
â”œâ”€â”€ prompts/                              Agent system prompts and guides
â”‚   â”œâ”€â”€ system/                          Agent system prompts
â”‚   â”‚   â”œâ”€â”€ extraction_agent.txt         Main extraction agent
â”‚   â”‚   â””â”€â”€ person_research_agent.txt    Person research specialist
â”‚   â”œâ”€â”€ guides/                          Extraction methodology guides
â”‚   â”‚   â”œâ”€â”€ geographic_extraction.md     Geographic data handling
â”‚   â”‚   â””â”€â”€ temporal_extraction.md       Temporal data handling
â”‚   â””â”€â”€ templates/                       Python utilities
â”‚       â””â”€â”€ load_prompts.py              Prompt loader utilities
â”‚
â”œâ”€â”€ CHATGPT_AGENT_PROMPT.md              System maintenance agent (archived)
â”œâ”€â”€ AGENT_TRAINING_FILES.md              Training files list (archived)
â”œâ”€â”€ AGENT_IMPLEMENTATION_GUIDE.md        Implementation guide (archived)
â”œâ”€â”€ AGENT_README.md                      Agent overview (archived)
â”‚
â”œâ”€â”€ TEST_SUBJECT_AGENT_PROMPT.md         Test subject SME agent (archived)
â”œâ”€â”€ TEST_SUBJECT_AGENT_FILES.md          Test subject training files (archived)
â”‚
â”œâ”€â”€ GRAPH_INSIGHT_SUMMARY.md             Why relationships matter (concepts)
â””â”€â”€ README.md                            Archive explanation from 2025-12-12
```

---

## Active Agent Components

### System Prompts (`prompts/system/`)

**extraction_agent.txt**
- Main extraction agent system prompt
- Handles knowledge extraction from text
- Status: Active

**person_research_agent.txt**
- Specialized agent for person entity research
- Status: Active/In Development

### Extraction Guides (`prompts/guides/`)

**geographic_extraction.md**
- How to handle geographic data (atomic vs tokenizable)
- Place names, coordinates, stability hierarchy
- Status: Active reference

**temporal_extraction.md**
- How to handle temporal data (dates, periods)
- ISO 8601 formatting, period classification
- Status: Active reference

### Utilities (`prompts/templates/`)

**load_prompts.py**
- Python utilities for loading prompt templates
- Status: Utility library

---

## Archived Agent Designs

The following files represent **earlier design iterations** that were archived because the multi-agent architecture is still being defined:

### System Maintenance Agent (Not Implemented)
- `CHATGPT_AGENT_PROMPT.md` - Help desk agent for Chrystallum users
- `AGENT_TRAINING_FILES.md` - Training file list
- `AGENT_IMPLEMENTATION_GUIDE.md` - Setup guide
- `AGENT_README.md` - Overview

**Status:** Not needed for core use case

### Test Subject Agent (Architecture Pending)
- `TEST_SUBJECT_AGENT_PROMPT.md` - Roman Republic historian for testing extraction
- `TEST_SUBJECT_AGENT_FILES.md` - Training files and test data

**Status:** Good concept, but needs architecture decisions:
- Should return JSON (not Cypher) âœ… Confirmed
- Should include confidence scores with reasoning âœ… Confirmed
- Should include citations as nodes âœ… Confirmed
- How to handle claim conflicts âŒ Not defined
- Multi-agent coordination âŒ Not defined

### Conceptual Documentation
- `GRAPH_INSIGHT_SUMMARY.md` - Why relationships are the core value of graphs
- `README.md` - Archive explanation and open questions

**Status:** Contains useful concepts for future architecture

---

## Open Architecture Questions

### Multi-Agent Coordination
```
User Query 
  â†’ SME Agent (JSON claims with confidence)
  â†’ Mediating Agent (validates, resolves conflicts)
  â†’ Persistence Agent (converts to Cypher, imports)
  â†’ Neo4j
```

**Questions:**
1. What format for agent-to-agent communication?
2. When does mediating agent trigger?
3. How to handle claim conflicts?
4. Who decides which claim wins?

### Claim Structure (Proposed)
```json
{
  "claim_id": "CLAIM_001",
  "confidence": 0.95,
  "reasoning": "Multiple primary sources agree",
  "nodes": [...],
  "edges": [...],
  "citations": [
    {"source_qid": "Q203787", "passage": "..."}
  ],
  "conflicts_with": []
}
```

### Citation as Nodes
```cypher
(claim)-[:CITED_BY]->(source:Citation {
  author_qid: "Q203787",  // Plutarch
  work: "Life of Caesar",
  passage: "Born in Subura"
})
```

**Questions:**
- How do citations affect confidence?
- How to model contradictory sources?
- Do we track citation chains?

---

## Current Active System

### What's Working Now

**Active Agents:**
- Extraction agent (Prompts/extraction_agent.txt)
- Person research agent (prompts/system/person_research_agent.txt)

**Active Guides:**
- Geographic extraction methodology
- Temporal extraction methodology

**Data Schema (in root):**
- md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md - Node type templates (Person, Event, Place, etc.)

### What's Still Being Designed

**Multi-agent system:**
- SME agents (subject matter experts)
- Mediating agents (validation/debate)
- Persistence agents (Cypher generation)

**Claim management:**
- Conflict resolution
- Confidence scoring
- Citation modeling
- Subgraph merging

---

## Next Steps

### When Architecture is Ready

1. **Update TEST_SUBJECT_AGENT_PROMPT.md**
   - Return JSON (not Cypher)
   - Include confidence + reasoning
   - Include citation references
   - Define conflict handling

2. **Create MEDIATING_AGENT_PROMPT.md**
   - Define validation logic
   - Specify debate rules
   - Set conflict resolution policies

3. **Create PERSISTENCE_AGENT_PROMPT.md**
   - JSON to Cypher conversion
   - Import strategy
   - Merge vs replace logic

4. **Update System Prompts**
   - Integrate with multi-agent coordination
   - Add claim structure
   - Include citation handling

---

## File References

### For Agent Development
- `prompts/system/` - Current agent system prompts
- `prompts/guides/` - Extraction methodology
- `md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md` - Node structure requirements

### For Architecture Planning
- `GRAPH_INSIGHT_SUMMARY.md` - Graph-first thinking concepts
- `README.md` - Archived design questions and rationale
- `TEST_SUBJECT_AGENT_PROMPT.md` - Example of schema-driven agent

### For Implementation
- `prompts/templates/load_prompts.py` - Prompt utilities
- `md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md` - Validation schemas
- Canonical relationship types (in relations/)

---

**Status:** Active development with archived explorations  
**Next:** Define multi-agent architecture, then implement  
**Key Insight:** Agents should return JSON claims (not Cypher), include confidence/citations, handle conflicts via mediation



