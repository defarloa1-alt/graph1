# CIDOC-CRM: Conceptual Reference Model Explained

## Overview

**CIDOC-CRM** (Conceptual Reference Model) is an **ISO 21127 standard** ontology designed for **cultural heritage information**. It provides a formal structure for describing entities, events, and relationships in museums, archives, libraries, and archaeological contexts.

**Key Characteristics:**
- ✅ **Event-centric**: Events are primary entities; everything else participates in events
- ✅ **International standard**: ISO 21127:2014 (updated ISO 21127:2023)
- ✅ **Domain-agnostic**: Works for any cultural heritage domain
- ✅ **Semantic web compatible**: RDF/OWL ontology

---

## Core Philosophy: Event-Centric Model

### Traditional Approach (Entity-Centric)

```
(Caesar) -[OWNS]-> (Sword)
(Caesar) -[LIVED_IN]-> (Rome)
```

**Focus:** Entities and their attributes

**Problem:** Doesn't capture **when**, **where**, or **how** things happened

---

### CIDOC-CRM Approach (Event-Centric)

```
(Caesar) -[PARTICIPATED_IN]-> (OwnershipEvent) -[OF]-> (Sword)
(OwnershipEvent) -[OCCURRED_AT]-> (Rome)
(OwnershipEvent) -[HAD_TIME_SPAN]-> (TimeSpan: '49-44 BCE')
```

**Focus:** Events as primary entities; everything else participates in events

**Advantage:** Captures **temporal**, **spatial**, and **contextual** information

---

## Fundamental Concepts

### 1. **Events (Primary Entities)**

In CIDOC-CRM, **events are the primary way to represent change, actions, and occurrences**.

**CIDOC-CRM Principle:**
> "All information about the world can be expressed in terms of entities participating in events over time."

#### Core Event Classes

**E5_Event** (Base Event)
- Any event/occurrence
- Example: "Battle of Pharsalus", "Creation of sculpture"

**E7_Activity** (Human Activity)
- Events involving human agency
- Example: "Excavation", "Conservation", "Exhibition"

**E8_Acquisition** (Acquisition Event)
- Events where ownership changes
- Example: "Museum acquires artifact"

**E9_Move** (Move Event)
- Spatial movement of objects
- Example: "Artifact moved from excavation site to museum"

**E12_Production** (Production Event)
- Creation of objects/works
- Example: "Sculpture carved", "Manuscript written"

**E67_Birth** / **E69_Death** (Life Events)
- Birth and death of persons
- Example: "Birth of Caesar", "Death of Brutus"

**E85_Joining** / **E86_Leaving** (Group Membership)
- Joining/leaving groups
- Example: "Caesar joins Senate", "Legionnaire leaves army"

---

### 2. **Temporal Information**

#### P4_has_time-span

**Property:** Links events to time periods

**Example:**
```
(CrossingRubicon: E5_Event)
  -[P4_has_time-span]->
  (TimeSpan: E52_Time-Span {
    P82a_begin_of_the_begin: '-0049-01-10T00:00:00',
    P82b_end_of_the_end: '-0049-01-10T23:59:59'
  })
```

**Why Important:**
- Separates event from temporal information
- Supports uncertain dates, date ranges
- Enables temporal reasoning

---

#### Time-Span Properties

**E52_Time-Span** properties:
- `P82a_begin_of_the_begin`: Earliest possible start
- `P82b_end_of_the_end`: Latest possible end
- `P81a_begin_of_the_end`: Latest possible start
- `P81b_end_of_the_begin`: Earliest possible end

**Supports Uncertainty:**
```
(TimeSpan: E52_Time-Span {
  P82a_begin_of_the_begin: '-0050-01-01',  // Earliest possible: 50 BCE
  P82b_end_of_the_end: '-0048-12-31'       // Latest possible: 48 BCE
})
// Event occurred "sometime between 50-48 BCE"
```

---

### 3. **Spatial Information**

#### P7_took_place_at

**Property:** Links events to places

**Example:**
```
(CrossingRubicon: E5_Event)
  -[P7_took_place_at]->
  (Rubicon: E53_Place)
```

---

#### Place Classes

**E53_Place** (Place)
- Geographic location
- Can have coordinates, names, hierarchies

**E44_Place_Appellation** (Place Name)
- Names for places
- Supports multiple names, historical names, variants

**Example:**
```
(Rome: E53_Place)
  -[P1_is_identified_by]->
  (Name1: E44_Place_Appellation {value: 'Roma'}),
  (Name2: E44_Place_Appellation {value: 'Rome'}),
  (Name3: E44_Place_Appellation {value: 'Urbs Aeterna'})
```

---

### 4. **Participants**

#### P11_had_participant

**Property:** Links events to participants (people, organizations, objects)

**Example:**
```
(CrossingRubicon: E5_Event)
  -[P11_had_participant]->
  (Caesar: E21_Person),
  (LegioXIII: E74_Group)
```

---

#### Participant Roles

**P14.1_in_the_role_of**: Specifies participant's role

**Example:**
```
(BattleOfPharsalus: E5_Event)
  -[P11_had_participant {P14.1_in_the_role_of: 'Commander'}]-> (Caesar: E21_Person)
  -[P11_had_participant {P14.1_in_the_role_of: 'Commander'}]-> (Pompey: E21_Person)
  -[P11_had_participant {P14.1_in_the_role_of: 'Soldier'}]-> (Legionnaire: E21_Person)
```

---

### 5. **Causality and Relationships**

#### P10_falls_within / P10i_contains

**Property:** Temporal/spatial containment

**Example:**
```
(RomanCivilWar: E5_Event)
  -[P10i_contains]->
  (CrossingRubicon: E5_Event),
  (BattleOfPharsalus: E5_Event)
```

---

#### P15_was_influenced_by

**Property:** Causal influence

**Example:**
```
(EndOfRepublic: E5_Event)
  -[P15_was_influenced_by]->
  (CrossingRubicon: E5_Event)
```

---

#### P17_was_motivated_by

**Property:** Motivation for actions

**Example:**
```
(CrossingRubicon: E7_Activity)
  -[P17_was_motivated_by]->
  (DesireToSeizePower: E7_Activity)
```

---

## Key Entity Classes

### Persons and Groups

**E21_Person**
- Individual person
- Has names, birth/death events

**E74_Group**
- Collection of persons
- Example: Legion, Senate, Family

**E40_Legal_Body**
- Organizations with legal status
- Example: Roman Republic, Museum

---

### Objects and Works

**E22_Human-Made_Object**
- Physical objects created by humans
- Example: Sculpture, Coin, Manuscript

**E28_Conceptual_Object**
- Ideas, concepts, intellectual works
- Example: Law, Language, Theory

**E31_Document**
- Written documents
- Example: Treaty, Letter, Manuscript

---

### Places

**E53_Place**
- Geographic location
- Can be point, area, or feature

**E27_Site**
- Place with archaeological/historical significance
- Example: Excavation site, Ruins

---

## Complete Example: "Caesar Crossed the Rubicon"

### CIDOC-CRM Representation

```cypher
// Event
(crossing: E5_Event {
  label: 'Crossing of the Rubicon'
})

// Temporal Information
(timeSpan: E52_Time-Span {
  P82a_begin_of_the_begin: '-0049-01-10T00:00:00',
  P82b_end_of_the_end: '-0049-01-10T23:59:59'
})

// Spatial Information
(rubicon: E53_Place {
  label: 'Rubicon River'
})

// Participants
(caesar: E21_Person {
  label: 'Julius Caesar'
})

(legioXIII: E74_Group {
  label: 'Legio XIII Gemina'
})

// Relationships
(crossing) -[:P4_has_time-span]-> (timeSpan)
(crossing) -[:P7_took_place_at]-> (rubicon)
(crossing) -[:P11_had_participant {P14.1_in_the_role_of: 'Commander'}]-> (caesar)
(crossing) -[:P11_had_participant {P14.1_in_the_role_of: 'Military Unit'}]-> (legioXIII)

// Consequences
(romanCivilWar: E5_Event {
  label: 'Roman Civil War'
})

(crossing) -[:P10i_contains]-> (crossing)  // Self-reference for temporal containment
(romanCivilWar) -[:P10i_contains]-> (crossing)  // Civil war contains crossing event
```

---

## Key Properties Reference

### Temporal Properties

| Property | Description | Example |
|----------|-------------|---------|
| **P4_has_time-span** | Event has time period | Event → Time-Span |
| **P81a_begin_of_the_end** | Latest possible start | Time-Span property |
| **P81b_end_of_the_begin** | Earliest possible end | Time-Span property |
| **P82a_begin_of_the_begin** | Earliest possible start | Time-Span property |
| **P82b_end_of_the_end** | Latest possible end | Time-Span property |

### Spatial Properties

| Property | Description | Example |
|----------|-------------|---------|
| **P7_took_place_at** | Event occurred at place | Event → Place |
| **P53_has_former_or_current_location** | Object at location | Object → Place |
| **P74_has_current_or_former_residence** | Person resided at | Person → Place |

### Participant Properties

| Property | Description | Example |
|----------|-------------|---------|
| **P11_had_participant** | Event had participant | Event → Person/Group/Object |
| **P14.1_in_the_role_of** | Participant's role | Qualifier on P11 |
| **P14.2_performed** | Person performed activity | Person → Activity |

### Causal Properties

| Property | Description | Example |
|----------|-------------|---------|
| **P10_falls_within** | Event within larger event | Sub-event → Super-event |
| **P10i_contains** | Event contains sub-events | Super-event → Sub-event |
| **P15_was_influenced_by** | Causal influence | Effect → Cause |
| **P17_was_motivated_by** | Motivation | Action → Motivation |

---

## Comparison: CIDOC-CRM vs. Chrystallum

### Similarities

| Aspect | CIDOC-CRM | Chrystallum | Alignment |
|--------|-----------|-------------|-----------|
| **Event-centric** | ✅ E5_Event | ✅ Event nodes | ✅ Aligned |
| **Temporal** | ✅ P4_has_time-span | ✅ start_date, end_date | ✅ Aligned |
| **Spatial** | ✅ P7_took_place_at | ✅ LOCATED_IN | ✅ Aligned |
| **Participants** | ✅ P11_had_participant | ✅ Relationships | ✅ Aligned |
| **Causality** | ✅ P15_was_influenced_by | ✅ CAUSED | ✅ Aligned |

---

### Differences

| Aspect | CIDOC-CRM | Chrystallum | Gap |
|--------|-----------|-------------|-----|
| **Event Properties** | Separate Time-Span entities | Properties on event | Different structure |
| **Action Structure** | Generic events | Goal/Trigger/Action/Result | More detailed |
| **Uncertainty** | P81a/P81b/P82a/P82b | date_precision, temporal_uncertainty | Different approach |
| **Subject Classification** | Not included | FAST/LCC/LCSH/MARC | Chrystallum addition |
| **Backbone Alignment** | Not included | Embedded properties | Chrystallum unique |

---

## Integration Strategy: Chrystallum + CIDOC-CRM

### Option 1: Mapping Layer (Recommended)

**Add CIDOC-CRM class/property IDs to entities:**

```cypher
(event:Event {
  label: 'Crossing of Rubicon',
  
  // Chrystallum properties
  start_date: '-0049-01-10',
  action_type: 'MIL_ACT',
  
  // CIDOC-CRM alignment
  cidoc_crm_class: 'E5_Event',
  cidoc_crm_properties: {
    'P4_has_time-span': 'E52_Time-Span',
    'P7_took_place_at': 'E53_Place',
    'P11_had_participant': ['E21_Person', 'E74_Group']
  }
})

(relationship:CAUSED {
  // CIDOC-CRM alignment
  cidoc_crm_property: 'P15_was_influenced_by'
})
```

**Advantages:**
- ✅ Preserves Chrystallum's action structure
- ✅ Enables CIDOC-CRM queries
- ✅ Bidirectional mapping

---

### Option 2: Dual Representation

**Store both formats:**

```cypher
// Chrystallum representation
(crossing:Event {start_date: '-0049-01-10'})

// CIDOC-CRM representation
(crossingCRM:E5_Event) -[:P4_has_time-span]-> (timeSpan:E52_Time-Span)

// Link them
(crossing) -[:MAPS_TO]-> (crossingCRM)
```

**Advantages:**
- ✅ Full CIDOC-CRM compliance
- ✅ Native Chrystallum queries
- ❌ Data duplication

---

### Option 3: CIDOC-CRM as Extension

**Use CIDOC-CRM for museum/archival integration only:**

```cypher
// Core Chrystallum entity
(crossing:Event {...})

// CIDOC-CRM extension for museum collections
(museumArtifact:E22_Human-Made_Object {
  cidoc_crm_class: 'E22_Human-Made_Object'
}) -[:CREATED_DURING {cidoc_crm_property: 'P4_has_time-span'}]-> (crossing)
```

**Advantages:**
- ✅ Chrystallum core unchanged
- ✅ CIDOC-CRM for specialized domains
- ✅ Gradual adoption

---

## Benefits of CIDOC-CRM Integration

### 1. **Museum Integration**

**Problem:** Museums use CIDOC-CRM for collections management

**Solution:** Chrystallum entities with CIDOC-CRM alignment

**Example:**
```
// Museum artifact linked to historical event
(artifact: E22_Human-Made_Object {
  cidoc_crm_class: 'E22_Human-Made_Object'
}) -[:CREATED_DURING {cidoc_crm_property: 'P4_has_time-span'}]-> 
(crossingEvent: Event {
  cidoc_crm_class: 'E5_Event'
})
```

---

### 2. **Event-Centric Queries**

**CIDOC-CRM enables queries like:**

```cypher
// Find all events at a place
MATCH (event:E5_Event)-[:P7_took_place_at]->(place)
WHERE place.label = 'Rubicon'
RETURN event

// Find all participants in events
MATCH (event:E5_Event)-[:P11_had_participant]->(participant)
RETURN event, participant

// Find causal chains
MATCH path = (cause:E5_Event)-[:P15_was_influenced_by*]->(effect:E5_Event)
RETURN path
```

---

### 3. **Temporal Uncertainty Handling**

**CIDOC-CRM's time-span properties handle uncertainty:**

```
(uncertainEvent: E5_Event)
  -[:P4_has_time-span]->
  (timeSpan: E52_Time-Span {
    P82a_begin_of_the_begin: '-0050-01-01',  // Earliest: 50 BCE
    P82b_end_of_the_end: '-0048-12-31'       // Latest: 48 BCE
  })
// Event occurred "sometime between 50-48 BCE"
```

**Chrystallum equivalent:**
```
(event:Event {
  start_date: '-0049-01-01',  // Mid-point estimate
  date_precision: 'year',
  temporal_uncertainty: true,
  date_range: {
    earliest: '-0050-01-01',
    latest: '-0048-12-31'
  }
})
```

---

### 4. **International Standard Compliance**

**Benefits:**
- ✅ **Interoperability**: Works with museum systems worldwide
- ✅ **Data Exchange**: Export/import CIDOC-CRM data
- ✅ **Tool Support**: Many tools support CIDOC-CRM
- ✅ **Research**: Academic research uses CIDOC-CRM

---

## Challenges & Considerations

### 1. **Complexity**

**CIDOC-CRM is comprehensive:**
- 90+ entity classes
- 150+ properties
- Steep learning curve

**Mitigation:** Start with core classes (E5_Event, E21_Person, E53_Place, E52_Time-Span)

---

### 2. **Different Modeling Philosophy**

**CIDOC-CRM:** Event-centric (everything is an event)
**Chrystallum:** Entity-centric with action structure

**Solution:** Mapping layer maintains both views

---

### 3. **Event vs. Relationship Debate**

**CIDOC-CRM:** "Crossing Rubicon" = Event entity
**Chrystallum:** "Crossing Rubicon" = Relationship with action structure

**Solution:** Can represent both ways, map between them

---

## Recommended Integration Approach

### Phase 1: Core Classes (Immediate)

Add CIDOC-CRM alignment to core entities:

```cypher
(event:Event {
  cidoc_crm_class: 'E5_Event'
})

(person:Human {
  cidoc_crm_class: 'E21_Person'
})

(place:Place {
  cidoc_crm_class: 'E53_Place'
})
```

### Phase 2: Key Properties (Short-term)

Map key relationships:

```cypher
// Temporal
(event:Event)-[:P4_has_time-span]->(timeSpan:TimeSpan)

// Spatial
(event:Event)-[:P7_took_place_at]->(place:Place)

// Participants
(event:Event)-[:P11_had_participant]->(person:Human)

// Causality
(effect:Event)-[:P15_was_influenced_by]->(cause:Event)
```

### Phase 3: Full Alignment (Long-term)

Complete mapping of Chrystallum schema to CIDOC-CRM classes and properties

---

## Summary

**CIDOC-CRM is an event-centric ontology for cultural heritage information.**

**Key Concepts:**
- ✅ Events are primary entities
- ✅ Temporal/spatial/participant information linked via properties
- ✅ Supports uncertainty and complex temporal relationships
- ✅ International standard (ISO 21127)

**Integration Benefits:**
- ✅ Museum/archival interoperability
- ✅ Event-centric queries
- ✅ Standard compliance
- ✅ Tool ecosystem support

**Recommended Approach:**
- Start with mapping layer (Option 1)
- Add CIDOC-CRM class/property IDs to entities
- Preserve Chrystallum's unique action structure
- Enable bidirectional queries

**Chrystallum Advantage:**
- Our action structure (Goal/Trigger/Action/Result) provides **more detail** than generic CIDOC-CRM events
- CIDOC-CRM alignment adds **interoperability** without losing our unique features



