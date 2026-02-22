# Cannon Trajectory Text: Graph Parsing Example

## Source Text

> "Aiming a cannon on a 17th century vessel is not even an art, much less a science. Calculating the proper trajectories for a projectile hurtling through the air at hundreds of miles per hour is hard enough on land. In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile. Some of the first differential equations were developed to predict the flight of a cannon ball shot."

---

## Core Entity Extraction

### Primary Entities

1. **Cannon** (Object/Technology)
   - Type: `Concept` or `Material`
   - Wikidata QID: `Q12876` (Cannon)

2. **Cannonball** (Object/Projectile)
   - Type: `Concept` or `Material`
   - Wikidata QID: `Q1723884` (Cannonball)

3. **Ship** (17th Century Vessel)
   - Type: `Infrastructure`
   - Wikidata QID: `Q11446` (Ship)

4. **Differential Equations** (Mathematical Concept)
   - Type: `Concept`
   - Wikidata QID: `Q177932` (Differential equation)

5. **Mathematical Innovation** (Abstract Concept)
   - Type: `Concept`
   - Represents the general concept of mathematical ingenuity/innovation

---

## Core Relationship Structure

### 1. **Cannon LOCATED_IN Ship**
- **Relationship Type:** `LOCATED_IN`
- **Temporal Context:** 17th century
- **Action Structure:** Deploying/positioning cannon on vessel

### 2. **Cannon FIRES/USES Cannonball (at target)**
- **Relationship Type:** `USE` or `USED_BY`
- **Action Structure (IGaR):**
  - **Goal:** Hit target/destroy enemy
  - **Goal Type:** `MIL` (Military)
  - **Trigger:** Need to engage enemy/military objective
  - **Trigger Type:** `MIL` (Military) or `TECH` (Technical)
  - **Action Type:** `MIL_ACT` (Military Action)
  - **Result:** Projectile launched toward target
  - **Result Type:** `MIL_ACT` (Military Action outcome)

### 3. **Differential Equations RELATES_TO Cannon (via trajectory calculation)**
- **Relationship Type:** `RELATED_TO` or `DEVELOPED_FOR`
- **Purpose:** Calculate trajectory for cannonball
- **Action Structure:**
  - **Goal:** Predict cannonball flight path
  - **Goal Type:** `TECH` (Technical) or `PRAC` (Practical)
  - **Trigger:** Need to accurately aim cannon
  - **Trigger Type:** `TECH` (Technical need)
  - **Action Type:** `KNOW_CREATE` (Knowledge Creation)
  - **Result:** Mathematical tool for trajectory prediction
  - **Result Type:** `KNOW_OUTCOME` (Knowledge Outcome)

### 4. **Differential Equations CONNECTS_TO Mathematical Innovation**
- **Relationship Type:** `INFLUENCED` or `PART_OF`
- **Purpose:** Shows differential equations as mathematical innovation
- **Action Structure:**
  - **Goal:** Develop mathematical tools
  - **Goal Type:** `KNOW` (Knowledge)
  - **Trigger:** Practical need for prediction
  - **Trigger Type:** `PRAC` (Practical)
  - **Action Type:** `KNOW_CREATE` (Knowledge Creation)
  - **Result:** Mathematical innovation created
  - **Result Type:** `KNOW_OUTCOME` (Knowledge Outcome)

---

## Date Format Standards (ISO 8601 + Canonical Time Backbone)

All dates in this graph conform to:
1. **ISO 8601 Format:**
   - CE dates: `'1600-01-01'` (positive year, YYYY-MM-DD)
   - BCE dates: `'-0049-01-10'` (negative year with leading zeros, -YYYY-MM-DD)

2. **Canonical Time Backbone Properties:**
   - `start_date`: ISO 8601 formatted date string
   - `end_date`: ISO 8601 formatted date string
   - `date_precision`: Precision level (`'day'`, `'month'`, `'year'`, `'century'`)
   - `temporal_period_classification`: Historical period name (from `Temporal/time_periods.csv`)
   - `temporal_period_qid`: Wikidata QID of the historical period
   - `temporal_period_start`: Start year of the period (integer)
   - `temporal_period_end`: End year of the period (integer)

3. **Historical Period Classification:**
   - 17th century (1600-1699) falls within **Early Modern Period** (1500-1800, QID: `Q5308718`)
   - Source: `Temporal/time_periods.csv`

---

## Complete Graph Representation

### Cypher Query

```cypher
// ============================================
// CANNON TRAJECTORY TEXT: CORE GRAPH STRUCTURE
// ============================================

// ============================================
// ENTITIES
// ============================================

// Time Period: 17th Century
(t17thCentury:Concept {
  id: 'Q7015',
  unique_id: 'Q7015_CONCEPT_17TH_CENTURY',
  label: '17th Century',
  type: 'Concept',
  type_qid: 'Q186081',
  qid: 'Q7015',
  // ISO 8601 dates
  start_date: '1600-01-01',
  end_date: '1699-12-31',
  date_precision: 'century',
  // Temporal backbone alignment
  temporal_period_classification: 'Early Modern Period',
  temporal_period_qid: 'Q5308718',  // Early Modern Period (1500-1800)
  temporal_period_start: '1500',
  temporal_period_end: '1800',
  test_case: 'cannon_trajectory'
})

// Ship (17th Century Vessel)
(ship:Infrastructure {
  id: 'Q11446',
  unique_id: 'Q11446_INFRASTRUCTURE_SHIP',
  label: '17th Century Vessel',
  type: 'Infrastructure',
  type_qid: 'Q41176',
  qid: 'Q11446',
  // ISO 8601 dates
  start_date: '1600-01-01',
  end_date: '1699-12-31',
  date_precision: 'century',
  // Temporal backbone alignment
  temporal_period_classification: 'Early Modern Period',
  temporal_period_qid: 'Q5308718',  // Early Modern Period (1500-1800)
  test_case: 'cannon_trajectory'
})

// Cannon
(cannon:Concept {
  id: 'Q12876',
  unique_id: 'Q12876_CONCEPT_CANNON',
  label: 'Cannon',
  type: 'Concept',
  type_qid: 'Q151885',
  qid: 'Q12876',
  test_case: 'cannon_trajectory'
})

// Cannonball
(cannonball:Concept {
  id: 'Q1723884',
  unique_id: 'Q1723884_CONCEPT_CANNONBALL',
  label: 'Cannon Ball',
  type: 'Concept',
  type_qid: 'Q151885',
  qid: 'Q1723884',
  test_case: 'cannon_trajectory'
})

// Differential Equations
(diffEquations:Concept {
  id: 'Q177932',
  unique_id: 'Q177932_CONCEPT_DIFFERENTIAL_EQUATIONS',
  label: 'Differential Equations',
  type: 'Concept',
  type_qid: 'Q151885',
  qid: 'Q177932',
  test_case: 'cannon_trajectory',
  historical_significance: 'Some of the first differential equations'
})

// Mathematical Innovation
(mathInnovation:Concept {
  id: 'mathematical_innovation',
  unique_id: 'mathematical_innovation_CONCEPT_MATHEMATICAL_INNOVATION',
  label: 'Mathematical Innovation',
  type: 'Concept',
  type_qid: 'Q151885',
  test_case: 'cannon_trajectory',
  description: 'Mathematical ingenuity and innovation driven by practical needs'
})

// ============================================
// RELATIONSHIPS WITH ACTION STRUCTURES (IGaR)
// ============================================

// 1. Cannon LOCATED_IN Ship (17th Century)
(cannon)-[:LOCATED_IN {
  // Action Structure - Goal (G)
  goal_type: 'MIL',
  goal_type_qid: 'Q49892',  // military
  goal_text: 'Deploy cannon for naval warfare',
  
  // Action Structure - Trigger (T)
  trigger_type: 'TECH',
  trigger_type_qid: 'Q11019',  // technology
  trigger_text: 'Naval artillery technology deployment',
  
  // Action Structure - Action (Act)
  action_type: 'MIL_ACT',
  action_type_qid: 'Q178561',  // battle/military action
  action_description: 'Aiming a cannon on a 17th century vessel',
  
  // Action Structure - Result (Res)
  result_type: 'MIL_ACT',
  result_type_qid: 'Q178561',
  result_text: 'Cannon positioned and operational on ship',
  
  // Action Structure - Narrative (N)
  narrative: 'Aiming a cannon on a 17th century vessel is not even an art, much less a science.',
  
  // Temporal properties (ISO 8601)
  start_date: '1600-01-01',
  end_date: '1699-12-31',
  date_precision: 'century',
  // Temporal backbone alignment
  temporal_period_classification: 'Early Modern Period',
  temporal_period_qid: 'Q5308718',  // Early Modern Period
  
  // Validation
  confidence: 0.90,
  validation_status: 'extracted',
  test_case: 'cannon_trajectory'
}]->(ship)

// Ship exists in 17th Century
(ship)-[:LOCATED_IN {
  // ISO 8601 dates
  start_date: '1600-01-01',
  end_date: '1699-12-31',
  date_precision: 'century',
  // Temporal backbone alignment
  temporal_period_classification: 'Early Modern Period',
  temporal_period_qid: 'Q5308718',
  test_case: 'cannon_trajectory'
}]->(t17thCentury)

// 2. Cannon FIRES/USES Cannonball (with IGaR action structure)
(cannon)-[:USE {
  // Action Structure - Goal (G)
  goal_type: 'MIL',
  goal_type_qid: 'Q49892',  // military
  goal_text: 'Hit target and achieve military objective',
  
  // Action Structure - Trigger (T)
  trigger_type: 'MIL',
  trigger_type_qid: 'Q49892',  // military
  trigger_text: 'Need to engage enemy target',
  
  // Action Structure - Action (Act)
  action_type: 'MIL_ACT',
  action_type_qid: 'Q178561',  // battle/military action
  action_description: 'Firing cannonball from cannon toward target',
  
  // Action Structure - Result (Res)
  result_type: 'MIL_ACT',
  result_type_qid: 'Q178561',
  result_text: 'Cannonball launched at hundreds of miles per hour toward target',
  
  // Action Structure - Narrative (N)
  narrative: 'Firing a cannonball requires calculating the proper trajectory for a projectile hurtling through the air at hundreds of miles per hour.',
  
  // Context
  projectile_velocity: 'hundreds of miles per hour',
  difficulty: 'hard',
  context: 'naval warfare',
  
  // Validation
  confidence: 0.95,
  validation_status: 'extracted',
  test_case: 'cannon_trajectory'
}]->(cannonball)

// 3. Differential Equations RELATED_TO Cannon (via trajectory calculation need)
(diffEquations)-[:RELATED_TO {
  // Action Structure - Goal (G)
  goal_type: 'TECH',
  goal_type_qid: 'Q11019',  // technology
  goal_text: 'Calculate accurate trajectory for cannonball',
  
  // Action Structure - Trigger (T)
  trigger_type: 'TECH',
  trigger_type_qid: 'Q11019',  // technology
  trigger_text: 'Need to accurately predict cannonball flight path',
  
  // Action Structure - Action (Act)
  action_type: 'KNOW_CREATE',
  action_type_qid: 'Q28389',  // knowledge
  action_description: 'Differential equations developed to predict the flight of a cannon ball shot',
  
  // Action Structure - Result (Res)
  result_type: 'KNOW_OUTCOME',
  result_type_qid: 'Q28389',  // knowledge
  result_text: 'Mathematical tool enables trajectory prediction',
  
  // Action Structure - Narrative (N)
  narrative: 'Some of the first differential equations were developed to predict the flight of a cannon ball shot.',
  
  // Historical significance
  historical_significance: 'first_differential_equations',
  purpose: 'trajectory_calculation',
  
  // Validation
  confidence: 0.90,
  validation_status: 'extracted',
  test_case: 'cannon_trajectory'
}]->(cannon)

// Also: Cannon NEEDS/REQUIRES Differential Equations (bidirectional relationship)
(cannon)-[:RELATED_TO {
  relationship_type: 'requires',
  purpose: 'trajectory_calculation',
  action_description: 'Cannon firing requires trajectory calculation',
  
  confidence: 0.90,
  test_case: 'cannon_trajectory'
}]->(diffEquations)

// 4. Differential Equations CONNECTS_TO Mathematical Innovation
(diffEquations)-[:INFLUENCED {
  // Action Structure - Goal (G)
  goal_type: 'KNOW',
  goal_type_qid: 'Q28389',  // knowledge
  goal_text: 'Develop mathematical tools for practical problems',
  
  // Action Structure - Trigger (T)
  trigger_type: 'PRAC',
  trigger_type_qid: 'Q7889',  // practical
  trigger_text: 'Practical need: figuring out trajectory of a projectile',
  
  // Action Structure - Action (Act)
  action_type: 'KNOW_CREATE',
  action_type_qid: 'Q28389',  // knowledge
  action_description: 'Few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile',
  
  // Action Structure - Result (Res)
  result_type: 'KNOW_OUTCOME',
  result_type_qid: 'Q28389',  // knowledge
  result_text: 'Mathematical innovation created through practical problem-solving',
  
  // Action Structure - Narrative (N)
  narrative: 'In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile. Some of the first differential equations were developed to predict the flight of a cannon ball shot.',
  
  // Historical context
  historical_significance: 'long_history',
  temporal_scope: 'extended_period',
  
  // Validation
  confidence: 0.93,
  validation_status: 'extracted',
  test_case: 'cannon_trajectory'
}]->(mathInnovation)

// Also: Mathematical Innovation INSPIRED_BY Differential Equations (reverse relationship)
(mathInnovation)-[:INFLUENCED_BY {
  relationship_type: 'inspired_by',
  action_description: 'Mathematical innovation inspired by development of differential equations',
  
  confidence: 0.93,
  test_case: 'cannon_trajectory'
}]->(diffEquations)

// ============================================
// SUMMARY RELATIONSHIP CHAIN
// ============================================

// Core Flow:
// 1. Cannon → LOCATED_IN → Ship (17th century context)
// 2. Cannon → USE → Cannonball (firing action with IGaR structure)
// 3. Differential Equations → RELATED_TO → Cannon (trajectory calculation need)
// 4. Differential Equations → INFLUENCED → Mathematical Innovation (innovation connection)
```

---

## Graph Structure Summary

### Entity Count: 6 Core Entities

**Concepts (4):**
- 17th Century (Time Period)
- Cannon
- Cannonball
- Differential Equations
- Mathematical Innovation

**Infrastructure (1):**
- Ship (17th Century Vessel)

---

### Relationship Count: 6 Core Relationships

1. **`LOCATED_IN`** - Cannon on Ship (with IGaR action structure)
   - Goal: Deploy for naval warfare
   - Action: `MIL_ACT`
   - Temporal: 17th century

2. **`LOCATED_IN`** - Ship in 17th Century

3. **`USE`** - Cannon fires Cannonball (with IGaR action structure)
   - Goal: Hit target
   - Action: `MIL_ACT`
   - Result: Projectile launched

4. **`RELATED_TO`** - Differential Equations relates to Cannon (bidirectional)
   - Purpose: Trajectory calculation
   - Action: `KNOW_CREATE`

5. **`INFLUENCED`** - Differential Equations connects to Mathematical Innovation
   - Action: `KNOW_CREATE`
   - Result: Mathematical innovation

6. **`INFLUENCED_BY`** - Mathematical Innovation inspired by Differential Equations (reverse)

---

## Key Insights from Graph Structure

### 1. **Core Entity Focus**
- Focus on three primary entities: **Cannon**, **Cannonball**, **Ship**
- Supporting entities: **Differential Equations**, **Mathematical Innovation**

### 2. **Spatial Relationship**
- Cannon is **LOCATED_IN** Ship (deployment relationship)
- Temporal context: 17th century

### 3. **Action Relationship with IGaR Structure**
- Cannon **USE** Cannonball (firing action)
- Complete IGaR structure: Goal (MIL), Trigger (MIL), Action (MIL_ACT), Result (MIL_ACT)

### 4. **Knowledge Relationship**
- Differential Equations **RELATED_TO** Cannon
- Connection: Need to calculate trajectory
- Shows practical need driving mathematical development

### 5. **Innovation Relationship**
- Differential Equations **INFLUENCED** Mathematical Innovation
- Demonstrates historical pattern: practical problems inspire mathematical innovation

---

## Query Examples

### Find all military actions involving cannon

```cypher
MATCH (cannon:Concept {qid: 'Q12876'})-[r:USE|:LOCATED_IN]->(target)
WHERE r.action_type = 'MIL_ACT'
RETURN cannon.label, type(r), target.label, r.action_description, r.goal_text
```

**Returns:**
- Cannon → USE → Cannonball (firing action)
- Cannon → LOCATED_IN → Ship (naval warfare deployment)

---

### Find what mathematical tools relate to cannon

```cypher
MATCH (cannon:Concept {qid: 'Q12876'})<-[r:RELATED_TO]-(math:Concept)
RETURN math.label, r.purpose, r.action_description
```

**Returns:**
- Differential Equations → trajectory_calculation → Cannon

---

### Find mathematical innovations inspired by practical needs

```cypher
MATCH (practical)-[:RELATED_TO]->(cannon:Concept {qid: 'Q12876'})
      <-[:RELATED_TO]-(diffEq:Concept {qid: 'Q177932'})
      -[:INFLUENCED]->(innovation:Concept)
RETURN diffEq.label, innovation.label
```

**Returns:**
- Differential Equations → Mathematical Innovation

---

### Trace the complete chain: Ship → Cannon → Cannonball → Math

```cypher
MATCH path = (ship:Infrastructure {qid: 'Q11446'})
            <-[:LOCATED_IN]-(cannon:Concept {qid: 'Q12876'})
            -[:USE]->(cannonball:Concept {qid: 'Q1723884'})
            <-[:RELATED_TO]-(diffEq:Concept {qid: 'Q177932'})
            -[:INFLUENCED]->(math:Concept)
RETURN path
```

**Returns:** Complete relationship chain from physical deployment to mathematical innovation

---

## Schema Validation

### ✅ Core Entities Use Valid Types
- Concepts (Cannon, Cannonball, Differential Equations, Mathematical Innovation)
- Infrastructure (Ship)
- All have valid Wikidata QIDs where applicable

### ✅ Relationships Use Valid Types
- `LOCATED_IN` (Cannon on Ship)
- `USE` (Cannon fires Cannonball)
- `RELATED_TO` (Differential Equations to Cannon)
- `INFLUENCED` / `INFLUENCED_BY` (Differential Equations to Mathematical Innovation)

### ✅ IGaR Action Structures Included
- All key relationships include complete action structure:
  - Goal (G) with goal_type and goal_type_qid
  - Trigger (T) with trigger_type and trigger_type_qid
  - Action (Act) with action_type and action_type_qid
  - Result (Res) with result_type and result_type_qid
  - Narrative (N)

### ✅ Action Types Use Valid Codes
- `MIL_ACT` for military actions (cannon firing, deployment)
- `KNOW_CREATE` for knowledge creation (differential equations development)
- `TECH` for technical goals/triggers
- `MIL` for military goals/triggers
- `PRAC` for practical triggers

### ✅ Temporal Data (ISO 8601 + Canonical Time Backbone)
- **ISO 8601 format:** `'1600-01-01'` to `'1699-12-31'` (CE dates use positive years)
- **Date precision:** `'century'` specified
- **Temporal backbone alignment:**
  - `temporal_period_classification: 'Early Modern Period'`
  - `temporal_period_qid: 'Q5308718'` (from Temporal/time_periods.csv)
  - `temporal_period_start: '1500'`
  - `temporal_period_end: '1800'`
- **Note:** BCE dates would use negative ISO 8601 format (e.g., `'-0049-01-10'` for 49 BCE)

### ✅ Validation Metadata
- Confidence scores
- Test case tracking
- Validation status

---

## What This Structure Reveals

### Strengths:
1. ✅ **Clear entity focus** - Core entities (Cannon, Cannonball, Ship) are prominent
2. ✅ **Proper IGaR structure** - Action relationships include complete Goal/Trigger/Action/Result
3. ✅ **Practical-to-mathematical chain** - Shows how practical needs (trajectory calculation) drive mathematical innovation
4. ✅ **Temporal context** - 17th century properly captured
5. ✅ **Bidirectional relationships** - Differential Equations ↔ Cannon relationship shows mutual dependency

### Relationship Chain Flow:
```
Ship (17th century)
  ← Cannon LOCATED_IN (naval deployment)
Cannon
  → Cannonball USE (firing action with IGaR)
  ← Differential Equations RELATED_TO (trajectory calculation need)
Differential Equations
  → Mathematical Innovation INFLUENCED (innovation outcome)
```

---

## Conclusion

The restructured graph focuses on:
- **Core entities:** Cannon, Cannonball, Ship
- **Spatial relationship:** Cannon LOCATED_IN Ship
- **Action relationship:** Cannon USE Cannonball with complete IGaR structure (Goal/Trigger/Action/Result)
- **Knowledge relationship:** Differential Equations RELATED_TO Cannon (trajectory calculation)
- **Innovation relationship:** Differential Equations INFLUENCED Mathematical Innovation

This structure captures the essential relationships while maintaining proper action structure terminology (IGaR) and showing the connection from practical military needs to mathematical innovation.
