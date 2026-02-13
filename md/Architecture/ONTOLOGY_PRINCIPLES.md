# Chrystallum Ontology Principles

**Date:** December 12, 2025  
**Status:** Corrected after initial implementation

---

## Core Principle: Structure vs. Topics

### ❌ WRONG: Mixing Structure and Topics

**Initial mistake:**
```cypher
// Redundant - Periods ARE temporal entities!
(period:Period)-[:CATEGORIZED_AS]->(:Subject {label: "Time"})

// Redundant - Places ARE geographic entities!
(place:Place)-[:CATEGORIZED_AS]->(:Subject {label: "Geography"})
```

**Problem:** This confuses **what something IS** (structure) with **what it's ABOUT** (topics).

---

## ✅ CORRECT: Separation of Concerns

### 1. **Structure** = Entity Types + Hierarchies

**Navigate through structural relationships:**

```cypher
// Temporal navigation
(year:Year)-[:FOLLOWED_BY]->(next_year:Year)
(year:Year)-[:WITHIN_TIMESPAN]->(period:Period)
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
MATCH (e:Event)-[:OCCURRED_IN]->(p:Period {label: "Roman Republic"})
RETURN e;

// Navigate period hierarchy
MATCH path = (child:Period)-[:SUB_PERIOD_OF*1..3]->(ancestor:Period)
WHERE child.label = "Roman Republic"
RETURN path;

// Find events in a year
MATCH (y:Year {year_value: -44})<-[:OCCURRED_IN]-(e:Event)
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

### ❌ Structural Categories

These are redundant because they're already in the entity type:

- ❌ "Time" - use `:Period` and `:Year` entity types
- ❌ "Geography" - use `:Place` entity type
- ❌ "People" - use `:Person` entity type
- ❌ "Events" - use `:Event` entity type
- ❌ "Organizations" - use `:Organization` entity type

### ✅ Topical Themes

These add semantic value:

- ✅ "Military history" - describes what the event is about
- ✅ "Political science" - describes the thematic domain
- ✅ "Religious practices" - describes the topical category
- ✅ "Economic policy" - describes the subject matter
- ✅ "Social relations" - describes the theme

---

## Design Decision: Why This Matters

### Problem with Structural Subjects

```cypher
// User wants: "Find all events about politics in the Roman Republic"

// ❌ WRONG approach (if Period linked to "Time" subject):
MATCH (e:Event)-[:OCCURRED_IN]->(p:Period)-[:CATEGORIZED_AS]->(:Subject {label: "Time"})
WHERE p.label = "Roman Republic"
RETURN e;
// Returns: ALL events (because all periods are "Time") - useless!

// ✅ CORRECT approach (topical subjects):
MATCH (e:Event)-[:SUBJECT_OF]->(s:Subject {domain: "political"})
MATCH (e)-[:OCCURRED_IN]->(p:Period {label: "Roman Republic"})
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
| `WITHIN_TIMESPAN` | 672 | Year → Period (temporal structure) |
| `SUB_PERIOD_OF` | 290 | Period → Period (temporal hierarchy) |
| `FOLLOWED_BY` | 671 | Year → Year (temporal sequence) |
| `DEFINED_BY` | ~200 | PropertyRegistry → Subject (relationship types → topics) |
| `SUBJECT_OF` | 0 | **Reserved for future use** (Event/Person → Subject) |

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
    {"from": "event", "to": "period", "type": "OCCURRED_IN"}
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
// ❌ WRONG - Don't do this:
{
  "nodes": [
    {"type": "Period", "label": "Roman Republic"},
    {"type": "Subject", "label": "Time"}  // ❌ Redundant!
  ],
  "edges": [
    {"from": "period", "to": "time_subject", "type": "SUBJECT_OF"}  // ❌ Wrong!
  ]
}

// ✅ CORRECT - Do this instead:
{
  "nodes": [
    {"type": "Period", "label": "Roman Republic"},
    {"type": "Period", "label": "Ancient Rome"}  // Parent period
  ],
  "edges": [
    {"from": "roman_republic", "to": "ancient_rome", "type": "SUB_PERIOD_OF"}  // ✅ Right!
  ]
}
```

---

## Summary

**Ontology = Structure + Topics**

- **Structure:** What entities ARE (types + hierarchies)
  - Navigate: Period → Period, Place → Place, Year → Year
  - Entity types: `:Period`, `:Place`, `:Year`, `:Person`, `:Event`

- **Topics:** What entities are ABOUT (thematic classification)
  - Discover: Event → Subject, Person → Subject
  - Subjects: Politics, Military, Religion, Culture, Economics

**Never mix them!**


