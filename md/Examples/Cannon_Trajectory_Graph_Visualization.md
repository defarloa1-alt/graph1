# Cannon Trajectory Text: Graph Visualization

## Text Parsed

> "Aiming a cannon on a 17th century vessel is not even an art, much less a science. Calculating the proper trajectories for a projectile hurtling through the air at hundreds of miles per hour is hard enough on land. In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile. Some of the first differential equations were developed to predict the flight of a cannon ball shot."

---

## Graph Structure Overview

### Entity Types Breakdown

```
15 Total Entities:

Concepts (12):
├── 17th Century (Time Period)
├── Cannon
├── Art
├── Science  
├── Trajectory Calculation
├── Projectile
├── Mathematics
├── Mathematical Ingenuity
├── Differential Equations
├── Cannon Ball
├── Flight
└── Practical Task

Infrastructure (1):
└── 17th Century Vessel

Place (1):
└── Land
```

---

## Relationship Graph

```
┌─────────────────┐
│ 17th Century    │
│ (Time Period)   │
└────────┬────────┘
         │ LOCATED_IN
         │
┌────────▼────────┐
│ 17th Century    │
│    Vessel       │
└────────┬────────┘
         │ LOCATED_IN (cannon on vessel)
         │
┌────────▼────────┐
│    Cannon       │
└────┬───────┬────┘
     │       │
     │       │ RELATED_TO (not even an art)
     │       │
┌────▼──┐  ┌─▼─────┐
│  Art  │  │Science│
└───────┘  └───────┘

┌─────────────────┐
│   Trajectory    │
│  Calculation    │
└────┬────────┬───┘
     │        │
     │        │ USE (calculates for)
     │        │
     │   ┌────▼────────┐
     │   │  Projectile │
     │   │  (hundreds  │
     │   │   of mph)   │
     │   └─────────────┘
     │
     │ RELATED_TO (hard enough on land)
     │
┌────▼──┐
│ Land  │
└───────┘

┌─────────────────┐
│  Practical      │
│    Task         │
└────┬────────────┘
     │ INFLUENCED
     │
┌────▼──────────────────┐
│ Mathematical          │
│ Ingenuity             │
└───────────────────────┘
     │
     │ RELATED_TO (part of)
     │
┌────▼────────┐
│ Mathematics │
└─────────────┘

┌─────────────────────┐
│  Trajectory         │
│  Calculation        │
└──────────┬──────────┘
           │ INFLUENCED
           │
┌──────────▼──────────┐
│ Mathematical        │
│ Ingenuity           │
└─────────────────────┘

┌──────────────────────┐
│ Differential         │
│ Equations            │
└──────┬───────────────┘
       │ CAUSED (developed for)
       │
┌──────▼──────┐
│   Flight    │
│ (process)   │
└─────────────┘

┌──────────────────────┐
│ Differential         │
│ Equations            │
└──────┬───────────────┘
       │ USE (predicts)
       │
┌──────▼──────────┐
│  Cannon Ball    │
└─────────────────┘
```

---

## Key Relationship Chains

### Chain 1: Practical Need → Mathematical Development

```
Practical Task
    │
    │ INFLUENCED (inspires)
    │
Mathematical Ingenuity
    │
    │ RELATED_TO (part of)
    │
Mathematics
```

### Chain 2: Trajectory Problem → Differential Equations

```
Trajectory Calculation
    │
    │ INFLUENCED (inspires)
    │
Mathematical Ingenuity
    │
    │ (leads to)
    │
Differential Equations
    │
    │ CAUSED (developed for)
    │
Flight Prediction
    │
    │ (applied to)
    │
Cannon Ball
```

### Chain 3: Historical Context

```
17th Century
    │
    │ LOCATED_IN
    │
17th Century Vessel
    │
    │ LOCATED_IN (contains)
    │
Cannon
```

---

## Action Structures Highlighted

### 1. Practical Task → Mathematical Ingenuity

**Action Structure:**
- **Goal:** Solve practical problems through mathematics
- **Trigger:** Real-world need for solutions
- **Action:** Practical tasks inspiring mathematical ingenuity
- **Result:** Mathematical innovation driven by practical needs
- **Narrative:** "Few practical tasks have a longer history of inspiring mathematical ingenuity..."

### 2. Differential Equations → Flight Prediction

**Action Structure:**
- **Goal:** Predict cannon ball flight accurately
- **Trigger:** Need to predict projectile trajectory
- **Action:** Some of the first differential equations were developed
- **Result:** Differential equations created, enabling trajectory prediction
- **Narrative:** "Some of the first differential equations were developed to predict the flight of a cannon ball shot."

---

## Comparison Relationships

### 1. Cannon vs Art
- **Type:** Negative comparison
- **Relationship:** RELATED_TO
- **Metadata:** `comparison_value: false` (is NOT art)

### 2. Cannon vs Science
- **Type:** Negative comparison  
- **Relationship:** RELATED_TO
- **Metadata:** `comparison_value: false` (much less a science)

### 3. Land Context Comparison
- **Type:** Difficulty comparison
- **Relationship:** RELATED_TO
- **Metadata:** `comparison_context: 'land'`, `implication: 'sea is even harder'`

---

## Historical Significance Markers

### 1. "First Differential Equations"
- **Property:** `historical_significance: 'first_differential_equations'`
- **Property:** `temporal_importance: 'early_development'`
- **On:** Differential Equations entity

### 2. "Longer History"
- **Property:** `historical_significance: 'long_history'`
- **Property:** `temporal_scope: 'extended_period'`
- **On:** Practical Task → Mathematical Ingenuity relationship

---

## Query Insights

### What inspired differential equations?

**Query:**
```cypher
MATCH (inspirer)-[:INFLUENCED|:CAUSED]->(diffEq:Concept {label: 'Differential Equations'})
RETURN inspirer.label, diffEq.label
```

**Graph Path:**
- Practical Task → INFLUENCED → Mathematical Ingenuity
- Trajectory Calculation → INFLUENCED → Mathematical Ingenuity
- Mathematical Ingenuity → (develops) → Differential Equations

### What was developed for cannon ball prediction?

**Query:**
```cypher
MATCH (method)-[:CAUSED]->(prediction)
WHERE prediction.label CONTAINS 'Flight'
RETURN method.label, prediction.label
```

**Result:**
- Differential Equations → CAUSED → Flight Prediction

### What comparisons are made in the text?

**Query:**
```cypher
MATCH (source)-[r:RELATED_TO]->(target)
WHERE r.comparison_type IS NOT NULL
RETURN source.label, r.comparison_type, target.label
```

**Results:**
1. Cannon → Art (negative_comparison)
2. Cannon → Science (negative_comparison)
3. Trajectory Calculation → Land (difficulty_comparison)

---

## Schema Validation

✅ **All entity types valid:**
- Concept (12 instances)
- Infrastructure (1 instance)
- Place (1 instance)

✅ **All relationship types valid:**
- LOCATED_IN (2 instances)
- RELATED_TO (4 instances)
- USE (3 instances)
- INFLUENCED (2 instances)
- CAUSED (1 instance)

✅ **Action structures present:**
- Goal, Trigger, Action, Result, Narrative on key relationships

✅ **Temporal data:**
- ISO 8601 format: `1600-01-01` to `1699-12-31`
- Date precision: `century`

✅ **Historical metadata:**
- Historical significance markers
- Temporal importance indicators

---

## Text → Graph Transformation Summary

**Input:** 4 sentences of prose

**Output:**
- 15 entities
- 13 relationships
- 5 action structures
- 3 comparison relationships
- Historical significance metadata
- Temporal context (17th century)

**Key Transformation:**
- **Abstract concepts** (art, science, mathematics) → Concept entities
- **Comparisons** → RELATED_TO relationships with comparison metadata
- **Historical claims** ("first", "longer history") → metadata properties
- **Causal chains** → CAUSED/INFLUENCED relationships
- **Temporal context** → Time Period entity + temporal relationships

**This demonstrates:** The Chrystallum schema successfully captures both surface-level facts AND deeper semantic relationships (inspiration, development, comparison, historical significance) in a queryable graph structure.

