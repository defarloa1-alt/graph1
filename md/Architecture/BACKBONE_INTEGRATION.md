# Backbone Integration Architecture

**Date:** December 12, 2025  
**Core Principle:** Subject nodes are the integration layer between Chrystallum and standardized taxonomies

---

## The Subject Node: Backbone Tie Point

### Definition

**Subject nodes ARE the tie to the LCC/FAST/LCSH backbone.**

They are not just classifications - they are **integration points** that connect Chrystallum entities to the Library of Congress taxonomy and other standardized knowledge organization systems.

---

## Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   CHRYSTALLUM GRAPH                         â”‚
â”‚                                                             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”                                               â”‚
â”‚  â”‚ Event   â”‚                                               â”‚
â”‚  â”‚ Person  â”‚                                               â”‚
â”‚  â”‚ Org     â”‚                                               â”‚
â”‚  â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜                                               â”‚
â”‚       â”‚ SUBJECT_OF                                         â”‚
â”‚       â†“                                                     â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                          â”‚
â”‚  â”‚   SUBJECT NODE              â”‚                          â”‚
â”‚  â”‚   (Integration Layer)       â”‚                          â”‚
â”‚  â”‚                             â”‚                          â”‚
â”‚  â”‚  fast_id: "1411640"         â”‚ â†â”€â”€â”€ FAST Backbone      â”‚
â”‚  â”‚  lcsh_heading: "Rome--..."  â”‚ â†â”€â”€â”€ LCSH Backbone      â”‚
â”‚  â”‚  lcc_code: "DG241-269"      â”‚ â†â”€â”€â”€ LCC Backbone       â”‚
â”‚  â”‚                             â”‚                          â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                          â”‚
â”‚       â†“                                                     â”‚
â”‚   BACKBONE ALIGNMENT                                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              EXTERNAL SYSTEMS                               â”‚
â”‚                                                             â”‚
â”‚  â€¢ Library of Congress Catalog                             â”‚
â”‚  â€¢ WorldCat                                                 â”‚
â”‚  â€¢ Digital Humanities Projects                             â”‚
â”‚  â€¢ Wikidata                                                 â”‚
â”‚  â€¢ Academic Databases                                       â”‚
â”‚  â€¢ Museum Collections                                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Why Subject Nodes Are Critical

### 1. Cross-System Interoperability

**Query Chrystallum using Library of Congress identifiers:**

```cypher
// Find all Chrystallum entities in LCC section DG241-269
MATCH (s:Subject {lcc_code: "DG241-269"})
MATCH (s)<-[:SUBJECT_OF]-(entity)
RETURN entity;
```

### 2. Standardized Discovery

**All entities on the same "library shelf" are linked:**

```cypher
// Find everything about Roman Republic history
MATCH (s:Subject {fast_id: "1411640"})
MATCH (s)<-[:SUBJECT_OF]-(entity)
RETURN labels(entity)[0] as type, entity.label as name;

// Returns:
// Event | "Overthrow of Roman Monarchy"
// Event | "Roman Republic transition"
// Event | "Sulla's Dictatorship"
// Person | "Cicero"  (when added)
// Organization | "Roman Senate" (when added)
```

### 3. Agent Integration

**Agents must return FAST/LCSH to tie to backbone:**

```json
{
  "entity": {
    "type": "Event",
    "label": "Battle of Pharsalus"
  },
  "subject_alignment": {
    "fast_id": "1411640",
    "lcsh_heading": "Rome--History--Republic",
    "lcc_code": "DG241-269"
  }
}
```

**System creates/finds Subject node and links entity to it.**

---

## Subject Node Schema (Integration Layer)

```cypher
(:Subject {
  // BACKBONE IDENTIFIERS (atomic)
  fast_id: "1411640",                    // FAST taxonomy ID
  lcsh_heading: "Rome--History--Republic", // LCSH subject string
  lcc_code: "DG241-269",                 // Library call number
  
  // SYSTEM PROPERTIES
  label: "Rome--History--Republic",      // Primary label (= lcsh_heading)
  unique_id: "SUBJECT_FAST_1411640",     // Internal ID
  domain: "historical_geographic",       // Chrystallum domain
  
  // METADATA
  backbone_alignment: true,              // Marks as backbone node
  created_from: "event_lcsh_data",       // Source of alignment
  description: "Roman history during Republican period"
})
```

---

## Integration Patterns

### Pattern 1: Entity Creation with Backbone Alignment

```cypher
// Step 1: Agent extracts entity + FAST ID
{
  "entity": {...},
  "fast_id": "1411640"
}

// Step 2: System finds/creates Subject node
MERGE (s:Subject {fast_id: "1411640"})
ON CREATE SET s.lcsh_heading = "Rome--History--Republic", ...

// Step 3: Link entity to Subject
CREATE (entity)-[:SUBJECT_OF]->(s)
```

### Pattern 2: Cross-System Query

```cypher
// External system provides FAST ID
// Chrystallum returns all related entities

MATCH (s:Subject {fast_id: $external_fast_id})
MATCH (s)<-[:SUBJECT_OF]-(entity)
OPTIONAL MATCH (entity)-[:DURING]->(period:Period)
OPTIONAL MATCH (entity)-[:LOCATED_AT]->(place:Place)
RETURN entity, period, place;
```

### Pattern 3: Library Catalog Integration

```cypher
// Map Chrystallum entities to library call numbers

MATCH (s:Subject)
MATCH (s)<-[:SUBJECT_OF]-(entity)
RETURN s.lcc_code as call_number,
       s.lcsh_heading as subject,
       collect(entity.label) as entities
ORDER BY call_number;

// Output matches library catalog organization:
// DG241-269 | Rome--History--Republic | [event1, event2, person1...]
```

---

## Design Principles

### 1. Subject Nodes Are NOT Just Tags

**âŒ Wrong thinking:**
```
Subject = "category" or "tag"
```

**âœ… Correct thinking:**
```
Subject = backbone integration point
Subject = bridge to Library of Congress
Subject = interoperability layer
```

### 2. Granularity Matches Entity Specificity

**Subject granularity should match the shelf you'd find in a library:**

```
âŒ Too broad:   "History"
âŒ Too broad:   "Political science"
âœ… Just right:  "Rome--History--Republic"
âœ… Even better: "Rome--History--Republic--Punic Wars"
```

### 3. Atomic Identifiers Required

**FAST IDs, LCC codes, and LCSH headings are ATOMIC:**

```cypher
// âœ… Correct
fast_id: "1411640"

// âŒ Wrong
fast_id: "FAST 1411640" // LLM might tokenize this
fast_id: 1411640        // Must be string, not integer
```

---

## Agent Requirements

### When Creating Entities

**Agents MUST provide backbone alignment:**

```json
{
  "entity": {
    "type": "Event",
    "label": "Crossing of the Rubicon",
    "qid": "Q161954"
  },
  "required_backbone_alignment": {
    "fast_id": "1411640",
    "lcsh_heading": "Rome--History--Republic",
    "lcc_code": "DG241-269"
  }
}
```

**System responsibilities:**
1. Find or create Subject node with these identifiers
2. Link entity to Subject node
3. Return confirmation with Subject node ID

### How Agents Get FAST IDs

**Two-stage process:**

1. **Agent extracts natural language subject:**
   ```json
   "subject": "Roman Republican history"
   ```

2. **Tool resolves to FAST ID:**
   ```python
   fast_id = lcsh_lookup("Roman Republican history")
   # Returns: "1411640"
   ```

3. **System creates/links:**
   ```cypher
   MERGE (s:Subject {fast_id: "1411640"})
   CREATE (entity)-[:SUBJECT_OF]->(s)
   ```

---

## Current Implementation

### Backbone Status

| Backbone | Status | Count | Notes |
|----------|--------|-------|-------|
| FAST IDs | âœ… Active | 24 | Includes 1 specific (Rome--History--Republic) |
| LCSH headings | âœ… Active | 24 | Stored on Subject nodes |
| LCC codes | âœ… Active | 24 | Call number system |

### Entity Integration

| Entity Type | Subject Links | Status |
|-------------|---------------|--------|
| Event | 3 events â†’ 1 Subject | âœ… Complete |
| Person | 0 | â³ Future |
| Organization | 0 | â³ Future |

### Queries Enabled

```cypher
// 1. Find all entities about Roman Republic
MATCH (s:Subject {fast_id: "1411640"})<-[:SUBJECT_OF]-(e)
RETURN e;

// 2. Browse by library call number
MATCH (s:Subject {lcc_code: "DG241-269"})<-[:SUBJECT_OF]-(e)
RETURN e;

// 3. Cross-domain discovery
MATCH (s1:Subject {domain: "historical_geographic"})<-[:SUBJECT_OF]-(e)
MATCH (e)-[:CAUSED]->(result)
MATCH (result)-[:SUBJECT_OF]->(s2:Subject {domain: "political"})
RETURN e, result, s1, s2;
```

---

## Future Enhancements

### 1. Subject Hierarchy

**LCSH has broader/narrower term relationships:**

```cypher
(:Subject {label: "Rome--History"})
  -[:NARROWER_TERM]->
(:Subject {label: "Rome--History--Republic"})
  -[:NARROWER_TERM]->
(:Subject {label: "Rome--History--Republic--Punic Wars"})
```

### 2. Multi-Subject Entities

**Some entities span multiple subjects:**

```cypher
(:Event {label: "Caesar's Assassination"})
  -[:SUBJECT_OF]-> (:Subject {lcsh: "Rome--History--Republic"})
  -[:SUBJECT_OF]-> (:Subject {lcsh: "Political violence"})
  -[:SUBJECT_OF]-> (:Subject {lcsh: "Assassinations"})
```

### 3. Cross-System Linking

**Link to external authority files:**

```cypher
(:Subject {fast_id: "1411640"})
  -[:SAME_AS]-> (:ExternalAuthority {
    system: "VIAF",
    id: "..."
  })
```

---

## Summary

**Subject nodes are the backbone integration layer.**

They are not just classifications - they are the **tie points** that connect Chrystallum to:
- Library of Congress taxonomies (LCC/LCSH/FAST)
- Academic research databases
- Digital humanities projects
- Cultural heritage systems
- Library catalogs worldwide

**Every entity in Chrystallum must link to a Subject node to be integrated with the standardized knowledge ecosystem.**

This is what makes Chrystallum interoperable with the broader knowledge infrastructure.



