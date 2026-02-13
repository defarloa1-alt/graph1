# Chrystallum Ontology Principles

**Date:** December 12, 2025  
**Status:** Corrected after initial implementation

---

## Core Principle: Structure vs. Topics

### âŒ WRONG: Mixing Structure and Topics

**Initial mistake:**
```cypher
// Redundant - Periods ARE temporal entities!
(period:Period)-[:CATEGORIZED_AS]->(:Subject {label: "Time"})

// Redundant - Places ARE geographic entities!
(place:Place)-[:CATEGORIZED_AS]->(:Subject {label: "Geography"})
```

**Problem:** This confuses **what something IS** (structure) with **what it's ABOUT** (topics).

---

## âœ… CORRECT: Separation of Concerns

### 1. **Structure** = Entity Types + Hierarchies

**Navigate through structural relationships:**

```cypher
// Temporal navigation
(year:Year)-[:FOLLOWED_BY]->(next_year:Year)
(year:Year)-[:PART_OF]->(period:Period)
(period:Period)-[:SUB_PERIOD_OF]->(parent_period:Period)

// Spatial navigation  
(place:Place)-[:LOCATED_IN]->(parent_place:Place)

// Organizational navigation
(person:Person)-[:MEMBER_OF]->(org:Organization)
```

**Entity types define STRUCTURE:**
- `:Year` - temporal nodes (concrete years)
- `:Period` - historical periods
- `:Place` - geographic entities
- `:Person` - historical people
- `:Event` - historical events
- `:Organization` - groups, institutions

---

### 2. **Topics** = Subject Classifications

**Classify by WHAT entities are ABOUT:**

```cypher
// Events classified by topic
(event:Event {label: "Battle of Zama"})-[:SUBJECT_OF]->(:Subject {label: "Military history"})
(event:Event {label: "Assassination of Caesar"})-[:SUBJECT_OF]->(:Subject {label: "Political violence"})

// People classified by topic
(person:Person {label: "Caesar"})-[:SUBJECT_OF]->(:Subject {label: "Political leaders"})
(person:Person {label: "Cicero"})-[:SUBJECT_OF]->(:Subject {label: "Orators"})

// Organizations classified by topic
(org:Organization {label: "Roman Senate"})-[:SUBJECT_OF]->(:Subject {label: "Political institutions"})
```

**Topical subjects (from LCSH/FAST):**
- `:Subject {domain: "political"}` - Political science, Governance
- `:Subject {domain: "military"}` - Military history, Warfare
- `:Subject {domain: "religious"}` - Religion, Theology
- `:Subject {domain: "cultural"}` - Culture, Arts
- `:Subject {domain: "economic"}` - Economics, Commerce
- `:Subject {domain: "social"}` - Social structure, Relations

---

## Navigation Patterns

### Temporal Navigation (Structure)

```cypher
// Find events in a period
MATCH (e:Event)-[:DURING]->(p:Period {label: "Roman Republic"})
RETURN e;

// Navigate period hierarchy
MATCH path = (child:Period)-[:SUB_PERIOD_OF*1..3]->(ancestor:Period)
WHERE child.label = "Roman Republic"
RETURN path;

// Find events in a year
MATCH (y:Year {year: -44})<-[:STARTS_IN_YEAR]-(e:Event)
RETURN e;
```

### Topical Discovery (Subjects)

```cypher
// Find all military events
MATCH (e:Event)-[:SUBJECT_OF]->(s:Subject {domain: "military"})
RETURN e;

// Find political entities across time
MATCH (entity)-[:SUBJECT_OF]->(s:Subject {label: "Political science"})
RETURN entity;

// Cross-domain connections
MATCH (military_event:Event)-[:SUBJECT_OF]->(ms:Subject {domain: "military"})
MATCH (military_event)-[:CAUSED]->(political_event:Event)-[:SUBJECT_OF]->(ps:Subject {domain: "political"})
RETURN military_event, political_event;
```

---

## What Should NOT Be Subjects

### âŒ Structural Categories

These are redundant because they're already in the entity type:

- âŒ "Time" - use `:Period` and `:Year` entity types
- âŒ "Geography" - use `:Place` entity type
- âŒ "People" - use `:Person` entity type
- âŒ "Events" - use `:Event` entity type
- âŒ "Organizations" - use `:Organization` entity type

### âœ… Topical Themes

These add semantic value:

- âœ… "Military history" - describes what the event is about
- âœ… "Political science" - describes the thematic domain
- âœ… "Religious practices" - describes the topical category
- âœ… "Economic policy" - describes the subject matter
- âœ… "Social relations" - describes the theme

---

## Design Decision: Why This Matters

### Problem with Structural Subjects

```cypher
// User wants: "Find all events about politics in the Roman Republic"

// âŒ WRONG approach (if Period linked to "Time" subject):
MATCH (e:Event)-[:DURING]->(p:Period)-[:CATEGORIZED_AS]->(:Subject {label: "Time"})
WHERE p.label = "Roman Republic"
RETURN e;
// Returns: ALL events (because all periods are "Time") - useless!

// âœ… CORRECT approach (topical subjects):
MATCH (e:Event)-[:SUBJECT_OF]->(s:Subject {domain: "political"})
MATCH (e)-[:DURING]->(p:Period {label: "Roman Republic"})
RETURN e;
// Returns: Only political events in Roman Republic - useful!
```

---

## Current Database State (After Fix)

### Nodes: 817 Total

| Node Type | Count | Purpose |
|-----------|-------|---------|
| `:Year` | 672 | Temporal backbone |
| `:Period` | 86 | Historical periods |
| `:Place` | 36 | Geographic entities |
| `:Subject` | 23 | **Topical subjects only** (removed Time, Geography) |

### Key Relationships

| Relationship | Count | Purpose |
|--------------|-------|---------|
| `PART_OF` | 672 | Year â†’ Period (temporal structure) |
| `SUB_PERIOD_OF` | 290 | Period â†’ Period (temporal hierarchy) |
| `FOLLOWED_BY` | 671 | Year â†’ Year (temporal sequence) |
| `DEFINED_BY` | ~200 | PropertyRegistry â†’ Subject (relationship types â†’ topics) |
| `SUBJECT_OF` | 0 | **Reserved for future use** (Event/Person â†’ Subject) |

**Note:** `CATEGORIZED_AS` relationships removed - they were structurally redundant.

---

## For Agent Implementation

When agents generate subgraphs, they should:

### 1. Use Entity Types for Structure

```json
{
  "nodes": [
    {
      "type": "Event",
      "label": "Crossing of the Rubicon",
      "qid": "Q3044",
      "date": "-0049-01-10"
    },
    {
      "type": "Period",
      "label": "Roman Republic",
      "qid": "Q17167"
    }
  ],
  "edges": [
    {"from": "event", "to": "period", "type": "DURING"}
  ]
}
```

### 2. Add Topical Classification

```json
{
  "nodes": [
    {
      "type": "Event",
      "label": "Crossing of the Rubicon"
    },
    {
      "type": "Subject",
      "label": "Military history",
      "fast_id": "1020874"
    },
    {
      "type": "Subject",
      "label": "Political science",
      "fast_id": "1069263"
    }
  ],
  "edges": [
    {"from": "event", "to": "military_subject", "type": "SUBJECT_OF"},
    {"from": "event", "to": "political_subject", "type": "SUBJECT_OF"}
  ]
}
```

### 3. Don't Create Redundant Subjects

```json
// âŒ WRONG - Don't do this:
{
  "nodes": [
    {"type": "Period", "label": "Roman Republic"},
    {"type": "Subject", "label": "Time"}  // âŒ Redundant!
  ],
  "edges": [
    {"from": "period", "to": "time_subject", "type": "SUBJECT_OF"}  // âŒ Wrong!
  ]
}

// âœ… CORRECT - Do this instead:
{
  "nodes": [
    {"type": "Period", "label": "Roman Republic"},
    {"type": "Period", "label": "Ancient Rome"}  // Parent period
  ],
  "edges": [
    {"from": "roman_republic", "to": "ancient_rome", "type": "SUB_PERIOD_OF"}  // âœ… Right!
  ]
}
```

---

## Summary

**Ontology = Structure + Topics**

- **Structure:** What entities ARE (types + hierarchies)
  - Navigate: Period â†’ Period, Place â†’ Place, Year â†’ Year
  - Entity types: `:Period`, `:Place`, `:Year`, `:Person`, `:Event`

- **Topics:** What entities are ABOUT (thematic classification)
  - Discover: Event â†’ Subject, Person â†’ Subject
  - Subjects: Politics, Military, Religion, Culture, Economics

**Never mix them!**




