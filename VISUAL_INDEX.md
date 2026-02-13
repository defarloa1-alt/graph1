# Visual Index: All Diagrams

Navigate your Obsidian vault using this index of all Mermaid diagrams.

---

## Quick Navigation

### By Purpose

**Learning the Architecture:**
1. Start with **Diagram 1: 6-Layer Ontology** → see all layers stack
2. Then **Diagram 2: Relationship Type to MINF Flow** → understand data transformation
3. Finally **Diagram 5: Query Patterns Spectrum** → see what you can query

**Building Your Graph:**
1. **Diagram 3: Battle of Pharsalus Example** → concrete entity example
2. **Diagram 4: Neo4j Relationships** → actual graph structure
3. **Diagram 9: Query Sophistication Levels** → understand complexity

**Implementation:**
1. **Diagram 10: Implementation Phases** → your project timeline
2. **Diagram 6: Data Flow (Claim to Agent)** → end-to-end pipeline
3. **Diagram 7: 200+ Relationship Categories** → your vocabulary

**Reference:**
1. **Diagram 8: MINF I1-I8 Properties** → understanding inference
2. **CHEATSHEET.md** → print and keep at desk
3. **EXAMPLES.md** → copy-paste ready code

---

## All Diagrams

### Diagram 1: Complete 6-Layer Ontology
**File:** CONCEPTUAL_MODEL.md
**What it shows:** All 6 layers stacked vertically
- Layer 1: Your 200+ canonical types (CSV)
- Layer 2: CIDOC-CRM formal classes
- Layer 3: Wikidata authority
- Layer 4: LCSH/FAST + 15 Facets
- Layer 5: Neo4j node types
- Layer 6: MINF inference
**When to use:** First-time learning, architecture overview
**Size:** Large, comprehensive
**Time to understand:** 15-20 minutes

---

### Diagram 2: Relationship Type → MINF Flow
**File:** CONCEPTUAL_MODEL.md
**What it shows:** How a CSV row becomes a rich MINF node
- CSV type → CRM property → Wikidata → LCSH → Neo4j nodes → MINF
- Concrete example: FOUGHT_IN type flowing through all layers
**When to use:** Understanding transformation pipeline
**Size:** Medium, linear
**Time to understand:** 5-10 minutes

---

### Diagram 3: Battle of Pharsalus - Complete Example
**File:** CONCEPTUAL_MODEL.md
**What it shows:** Concrete entity with all node types
- INPUT: Claim from Livy
- ENTITIES: Event, Place, Period, Person
- RELATIONSHIPS: Belief, RelType, Citation, Note
- CLASSIFICATION: Subject, Facets
**When to use:** Reference for building your own entities
**Size:** Large, complex network
**Time to understand:** 10-15 minutes

---

### Diagram 4: Neo4j Relationships
**File:** CONCEPTUAL_MODEL.md
**What it shows:** Actual graph nodes and edges
- Color-coded by type (CRM, vocabulary, reified, evidence, classification)
- Shows all relationship types
- Example: Battle of Pharsalus network
**When to use:** Understanding Neo4j structure
**Size:** Large, network layout
**Time to understand:** 10 minutes

---

### Diagram 5: Query Patterns Spectrum
**File:** CONCEPTUAL_MODEL.md
**What it shows:** 6 levels of query sophistication
- Level 1: Simple edge
- Level 2: With confidence
- Level 3: With evidence
- Level 4: With caveats
- Level 5: By relationship type
- Level 6: Belief revision
**When to use:** Before writing Cypher
**Size:** Wide, horizontal spectrum
**Time to understand:** 10 minutes

---

### Diagram 6: Data Flow (Claim → Graph → Agent)
**File:** CONCEPTUAL_MODEL.md
**What it shows:** Complete pipeline from input to output
- Claim input → LLM extraction → Node creation → Query layer → Agent routing
**When to use:** Understanding end-to-end workflow
**Size:** Medium, left-to-right
**Time to understand:** 5-10 minutes

---

### Diagram 7: 200+ Relationship Types Organization
**File:** CONCEPTUAL_MODEL.md
**What it shows:** All 30 categories with example types
- 10 main categories (Creative, Historical, Social, etc.)
- Detailed example: Military category with 25+ types
**When to use:** Finding relationship type for your data
**Size:** Large, hierarchical
**Time to understand:** 5 minutes

---

### Diagram 8: MINF I1-I8 Properties
**File:** CONCEPTUAL_MODEL.md
**What it shows:** All MINF inference properties explained
- I1: Inferred from (evidence)
- I2: Belief level (assessment)
- I3: Has note (caveat)
- I4: Has uncertainty (confidence)
- I7: Has object (old belief)
- I8: Has result (new belief)
- Bonus: Belief revision pattern
**When to use:** Understanding inference & belief revision
**Size:** Large, hierarchical
**Time to understand:** 10 minutes

---

### Diagram 9: Query Sophistication Levels
**File:** CONCEPTUAL_MODEL.md
**What it shows:** Three user types and their queries
- Casual user → simple edge query
- Researcher → belief + evidence query
- Expert agent → MINF + confidence + caveats query
- Concrete example: "Battle in Thessaly?"
**When to use:** Understanding query complexity tradeoff
**Size:** Medium, comparative
**Time to understand:** 5 minutes

---

### Diagram 10: Implementation Phases
**File:** CONCEPTUAL_MODEL.md
**What it shows:** 6-phase implementation timeline
- Phase 1: Foundation (RelationshipType nodes)
- Phase 2: Entity enrichment
- Phase 3: Reification (Belief nodes)
- Phase 4: Evidence (Citation nodes)
- Phase 5: Classification (Facets)
- Phase 6: Querying
**When to use:** Planning your project
**Size:** Small, linear
**Time to understand:** 3 minutes

---

## Reference Documents

### CHEATSHEET.md
**Contents:**
- Layer summaries (1 page each)
- Relationships at a glance
- 6 query levels
- Decision matrix (which node type?)
- Implementation checklist
- Quick start (first 3 steps)

**Use:** Print and keep at desk
**Read time:** 10 minutes
**Best for:** Quick lookup, decision-making

---

### EXAMPLES.md
**Contents:**
- Example 1: Battle of Pharsalus (complete walkthrough)
- Example 2: Roman Republic (multi-faceted)
- Example 3: Belief revision (Caesar's birthplace)
- Example 4: Agent routing (historian, scientist, uncertain agent)
- Example 5: LCSH integration (AIDS example)
- Template: Copy-paste for new entities

**Use:** Copy Cypher code for your own data
**Read time:** 30 minutes
**Best for:** Building, learning by doing

---

### RELATIONSHIP_TYPES_ARCHITECTURE.md
**Contents:**
- Complete system architecture (524 lines)
- All 30 relationship categories explained
- CIDOC-CRM mapping table
- MINF I1-I8 detailed
- Complete Cypher templates
- Query patterns (6 levels)

**Use:** Deep reference
**Read time:** 60 minutes
**Best for:** Understanding rationale, troubleshooting

---

## Suggested Reading Order

### First Time (30 minutes)
1. This index (5 min)
2. Diagram 1: 6-Layer Ontology (15 min)
3. CHEATSHEET: Quick Reference (10 min)

### Building (60 minutes)
1. Diagram 3: Battle of Pharsalus Example (10 min)
2. EXAMPLES.md: Example 1 (20 min)
3. EXAMPLES.md: Copy template (5 min)
4. CHEATSHEET: Checklist (5 min)
5. Try building own entity in Neo4j (15 min)

### Deepening (90 minutes)
1. Diagram 2: Transformation Flow (10 min)
2. Diagram 4: Neo4j Relationships (10 min)
3. Diagram 5: Query Patterns (10 min)
4. EXAMPLES.md: Example 2-5 (30 min)
5. RELATIONSHIP_TYPES_ARCHITECTURE.md: Read sections (30 min)

### Reference (ongoing)
- CHEATSHEET.md: Printed, at desk
- EXAMPLES.md: Open in split view while coding
- Diagram 5: Before writing Cypher
- Diagram 8: When working with MINF

---

## By Topic

### Understanding the Layers
- Diagram 1 (overview)
- CHEATSHEET: Layer 1-6 sections
- RELATIONSHIP_TYPES_ARCHITECTURE: Layers section

### Building Entities
- Diagram 3 (example)
- EXAMPLES.md: All examples
- CHEATSHEET: Checklist
- EXAMPLES.md: Template

### Writing Queries
- Diagram 5 (patterns)
- Diagram 9 (sophistication levels)
- EXAMPLES.md: Query sections
- CHEATSHEET: 6 query levels

### Understanding Relationships
- Diagram 2 (flow)
- Diagram 4 (graph structure)
- Diagram 7 (categories)
- RELATIONSHIP_TYPES_ARCHITECTURE: Complete section

### Understanding MINF
- Diagram 8 (I1-I8)
- Diagram 3 (example with Belief/Citation/Note)
- EXAMPLES.md: Example 3 (belief revision)
- CHEATSHEET: MINF section

### Project Planning
- Diagram 10 (phases)
- CHEATSHEET: Quick Start
- EXAMPLES.md: Implementation notes

---

## File Organization for Obsidian

Suggested vault structure:

```
Knowledge Graph/
├─ 00 Index
│  ├─ README.md
│  └─ This file (Visual Index.md)
│
├─ 10 Conceptual
│  ├─ CONCEPTUAL_MODEL.md (all 10 diagrams)
│  └─ CHEATSHEET.md
│
├─ 20 Implementation
│  ├─ RELATIONSHIP_TYPES_ARCHITECTURE.md
│  ├─ NODE_TYPE_SCHEMAS-1.md [file:362]
│  └─ canonical_relationship_types.csv [file:367]
│
├─ 30 Examples
│  ├─ EXAMPLES.md
│  ├─ Example - Battle of Pharsalus.md
│  ├─ Example - Roman Republic.md
│  ├─ Example - Belief Revision.md
│  └─ Example - LCSH Integration.md
│
├─ 40 Queries
│  ├─ Query Patterns.md
│  ├─ Query - Simple Edges.md
│  ├─ Query - With Evidence.md
│  ├─ Query - With Caveats.md
│  └─ Query - By Type.md
│
├─ 50 Reference
│  ├─ CIDOC-CRM Classes.md
│  ├─ Wikidata Properties.md
│  ├─ LCSH Subdivisions.md
│  ├─ Facets (15 classes).md
│  └─ MINF I1-I8.md
│
└─ 60 Implementation
   ├─ Phase 1 - Foundation.md
   ├─ Phase 2 - Entities.md
   ├─ Phase 3 - Reification.md
   ├─ Phase 4 - Evidence.md
   ├─ Phase 5 - Classification.md
   └─ Phase 6 - Querying.md
```

Use Obsidian's linking to connect:
- CONCEPTUAL_MODEL.md → each example
- EXAMPLES.md → specific query patterns
- CHEATSHEET.md → RELATIONSHIP_TYPES_ARCHITECTURE.md
- Implementation phases → working files

---

## Quick Lookup

**Q: What does Layer 2 do?**
A: CHEATSHEET.md → "Layer 2: CIDOC-CRM Formal Ontology"

**Q: How do I add confidence?**
A: CHEATSHEET.md → "Layer 6: MINF Inference Layer" → I4: HAS_UNCERTAINTY

**Q: What query gets high-confidence relationships?**
A: Diagram 5 → Level 2, or EXAMPLES.md → Query 2, or CHEATSHEET.md → "Level 2: With Confidence"

**Q: How do I track belief changes?**
A: Diagram 8 → Belief Revision Tracking, or EXAMPLES.md → Example 3

**Q: Where do relationship types come from?**
A: CHEATSHEET.md → "Layer 1: Canonical Relationship Types" → points to file:367

**Q: How many facets are there?**
A: CHEATSHEET.md → "Layer 4: LCSH/FAST" → Table showing 15

**Q: How do I start?**
A: CHEATSHEET.md → "Quick Start: First 3 Steps" (3 Cypher statements)

---

## Print This

Print the CHEATSHEET.md (2-3 pages) and keep it:
- At your desk
- In your coding environment
- On a reference card

The diagrams are too large to print, but live in Obsidian for reference.

---

**Version**: 1.0 (January 14, 2026)
**Last Updated**: 2026-01-14T05:19:00Z
**Total Pages**: 10 Mermaid diagrams + 3 reference docs + this index
