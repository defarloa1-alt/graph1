# Subgraph Structure - Agent Output Format

**Date:** December 12, 2025  
**Status:** Schema Complete, Ready for Implementation

---

## Core Principle: Every Subgraph Has a Subject

**A subgraph is anchored by its TOPIC (Subject), not just its entities.**

```
Subject (ALWAYS) - What the subgraph is ABOUT
   ↓
Entities (Event/Person/Organization) - The historical content
   ↓
Connected to Backbone:
   - Time period hierarchy (when)
   - Geographic hierarchy (where)
   - Subject hierarchy (related topics)
```

---

## Subgraph Schema

### Required Components:

1. **Subject (ALWAYS)** - Topical classification
   - What is this subgraph about?
   - Links to LCSH/FAST taxonomy
   - Examples: "Military conflicts", "Political transitions", "Religious practices"

2. **Entities (1+)** - Historical content
   - Person, Event, Organization
   - The actual historical data

3. **Temporal Dimension (SHOULD HAVE)** - When
   - Link to Period hierarchy
   - Optionally link to specific Year

4. **Geographic Dimension (SHOULD HAVE)** - Where
   - Link to Place hierarchy

5. **Subject Hierarchy (MAY HAVE)** - Related topics
   - Broader terms
   - Narrower terms
   - Related subjects

---

## Example Subgraphs from Current Data

### Subgraph 1: "Overthrow of Roman Monarchy"

```cypher
// SUBJECT (what it's about)
(:Subject {
  label: "Political transitions",
  fast_id: "...",
  domain: "political"
})
  ↓ SUBJECT_OF
  
// ENTITY (the event)
(:Event {
  label: "Overthrow of Roman Monarchy",
  date: "-509",
  description: "End of Roman Kingdom, beginning of Republic"
})
  ↓ OCCURRED_IN
  
// TIME HIERARCHY
(:Period {label: "Roman Kingdom", start: -753, end: -509})
  ↓ FOLLOWED_BY
(:Period {label: "Roman Republic", start: -509, end: -27})
  ↓ SUB_PERIOD_OF
(:Period {label: "Ancient Rome", start: -753, end: 476})

  ↓ LOCATED_AT
// GEOGRAPHIC HIERARCHY
(:Place {label: "Rome", type: "city"})
  ↓ LOCATED_IN
(:Place {label: "Italy", type: "country"})

  ↓ RESULTED_IN
// RELATED ENTITIES
(:Organization {label: "Roman Republic"})
  ↓ SUBJECT_OF
(:Subject {label: "Political institutions"})
```

**Subgraph Vertex Count:** 1 (one subject anchor)

---

### Subgraph 2: "Sulla's Dictatorship"

```cypher
// SUBJECTS (multi-topic)
(:Subject {label: "Political science", fast_id: "1069263"})
(:Subject {label: "Military history", fast_id: "1020874"})
  ↓ SUBJECT_OF
  
// ENTITY
(:Event {
  label: "Sulla's Dictatorship",
  start_date: "-82",
  end_date: "-79",
  description: "Sulla's authoritarian rule"
})
  ↓ OCCURRED_IN
  
// TIME HIERARCHY
(:Year {year_value: -82})
  ↓ WITHIN_TIMESPAN
(:Period {label: "Roman Republic"})
  ↓ SUB_PERIOD_OF
(:Period {label: "Ancient Rome"})

  ↓ LOCATED_AT
// GEOGRAPHIC HIERARCHY
(:Place {label: "Rome"})
  ↓ LOCATED_IN
(:Place {label: "Italy"})
```

**Subgraph Vertex Count:** 1 (even with multiple subjects, it's one thematic cluster)

---

### Subgraph 3: "Julius Caesar" (Hypothetical - Person-Centered)

```cypher
// SUBJECTS
(:Subject {label: "Political leaders", fast_id: "..."})
(:Subject {label: "Military commanders", fast_id: "..."})
  ↓ SUBJECT_OF
  
// ENTITY
(:Person {
  label: "Julius Caesar",
  qid: "Q1048",
  birth_date: "-100-07-12",
  death_date: "-44-03-15"
})
  ↓ LIVED_DURING
  
// TIME HIERARCHY
(:Period {label: "Late Roman Republic"})
  ↓ SUB_PERIOD_OF
(:Period {label: "Roman Republic"})
  ↓ SUB_PERIOD_OF
(:Period {label: "Ancient Rome"})

  ↓ BORN_IN / DIED_IN
// GEOGRAPHIC HIERARCHY
(:Place {label: "Rome"})
  ↓ LOCATED_IN
(:Place {label: "Italy"})

  ↓ PARTICIPATED_IN
// RELATED EVENTS
(:Event {label: "Gallic Wars"})
  ↓ SUBJECT_OF
(:Subject {label: "Military campaigns"})

(:Event {label: "Crossing of the Rubicon"})
  ↓ SUBJECT_OF
(:Subject {label: "Political transitions"})
```

**Subgraph Vertex Count:** 1 (one person as anchor, even with multiple events)

---

## Current Database: 3 Potential Subgraph Vertices

| Subgraph | Central Entity | Subject Needed | Period Needed | Place Needed | Status |
|----------|----------------|----------------|---------------|--------------|--------|
| 1 | Overthrow of Monarchy | Political transitions | Roman Kingdom → Republic | Rome → Italy | ❌ Not linked |
| 2 | Republic transition | Political science | Roman Kingdom → Republic | Rome → Italy | ❌ Not linked |
| 3 | Sulla's Dictatorship | Political + Military | Roman Republic | Rome → Italy | ❌ Not linked |

---

## What Needs to Happen:

### Step 1: Link Events to Subjects
```cypher
MATCH (e:Event {label: "Overthrow of Roman Monarchy"})
MATCH (s:Subject {label: "Political science"})
CREATE (e)-[:SUBJECT_OF]->(s);
```

### Step 2: Link Events to Periods
```cypher
MATCH (e:Event {label: "Overthrow of Roman Monarchy"})
MATCH (p:Period {label: "Roman Kingdom"})
CREATE (e)-[:OCCURRED_IN]->(p);
```

### Step 3: Link Events to Places
```cypher
MATCH (e:Event {label: "Overthrow of Roman Monarchy"})
MATCH (place:Place {label: "Rome"})
CREATE (e)-[:LOCATED_AT]->(place);
```

---

## Agent Output Format (JSON)

When an agent generates a subgraph, it should return:

```json
{
  "subgraph_id": "monarchy_overthrow_001",
  "subject": {
    "primary": {
      "label": "Political transitions",
      "fast_id": "..."
    },
    "secondary": [
      {"label": "Revolutionary movements", "fast_id": "..."}
    ]
  },
  "entities": {
    "events": [
      {
        "qid": "Q...",
        "label": "Overthrow of Roman Monarchy",
        "date": "-509",
        "location_qid": "Q220",
        "period_qid": "Q..."
      }
    ],
    "people": [],
    "organizations": [
      {
        "qid": "Q...",
        "label": "Roman Republic",
        "founded": "-509"
      }
    ]
  },
  "relationships": [
    {
      "from": "event_001",
      "to": "organization_001",
      "type": "RESULTED_IN",
      "properties": {"confidence": 0.95}
    }
  ],
  "narrative": "In 509 BCE, the Roman people overthrew the last king..."
}
```

---

## Testing Plan

### Phase 1: Link Existing 3 Events ✅ READY
1. Create SUBJECT_OF relationships
2. Create OCCURRED_IN relationships
3. Create LOCATED_AT relationships
4. Verify 3 complete subgraphs

### Phase 2: Agent Generation 🔄 NEXT
1. Create test prompt for SME agent (Roman Republic historian)
2. Generate subgraph JSON for a new event
3. Import to Neo4j
4. Validate against schema

### Phase 3: Validation & Conflict 🔜 FUTURE
1. Multi-agent claims
2. Confidence scoring
3. Conflict resolution

---

## Summary

**Current Status:**
- ✅ Schemas complete (Person, Event, Subject, Period, Place)
- ✅ Backbone ready (23 subjects, 86 periods, 36 places)
- ✅ 3 events exist
- ❌ Events not linked to backbone

**Next Steps:**
1. Link 3 existing events to create 3 complete subgraph vertices
2. Test visualization queries
3. Document as examples for agent training

**Subgraph Vertices = Events/People/Organizations properly linked to Subject + Time + Geography backbones**


