# Wikidata Alignment Analysis: Action Structure Vocabularies

## Question

Do our goal types, trigger types, action types, and result types align with Wikidata QIDs or properties?

---

## Current Action Structure Vocabulary

From `action_structure_vocabularies.csv`:

### Goal Types (10)
1. **POL** - Political
2. **PERS** - Personal
3. **MIL** - Military
4. **ECON** - Economic
5. **CONST** - Constitutional
6. **MORAL** - Moral
7. **CULT** - Cultural
8. **RELIG** - Religious
9. **DIPL** - Diplomatic
10. **SURV** - Survival

### Trigger Types (10)
1. **CIRCUM** - Circumstantial
2. **MORAL_TRIGGER** - Moral
3. **EMOT** - Emotional
4. **POL_TRIGGER** - Political
5. **PERS_TRIGGER** - Personal
6. **EXT_THREAT** - External Threat
7. **INT_PRESS** - Internal Pressure
8. **LEGAL** - Legal
9. **AMB** - Ambition
10. **OPPORT** - Opportunity

### Action Types (15)
1. **REVOL** - Political Revolution
2. **MIL_ACT** - Military Action
3. **CRIME** - Criminal Act
4. **DIPL_ACT** - Diplomatic Action
5. **CONST_INNOV** - Constitutional Innovation
6. **ECON_ACT** - Economic Action
7. **LEGAL_ACT** - Legal Action
8. **SOC_ACT** - Social Action
9. **RELIG_ACT** - Religious Action
10. **PERS_ACT** - Personal Action
11. **ADMIN** - Administrative
12. **CAUSAL** - Causal Chain
13. **TYRANNY** - Tyrannical Governance
14. **DEFENSIVE** - Defensive Action
15. **OFFENSIVE** - Offensive Action

### Result Types (19)
- Various outcome types (Political Transformation, Conquest, Defeat, etc.)

---

## Wikidata Alignment Analysis

### 1. Goal Types → Wikidata Mapping

**Partial Alignment Possible:**

| Our Code | Our Type | Wikidata Equivalent | Alignment |
|----------|----------|---------------------|-----------|
| **POL** | Political | Concept: Q7163 (politics) | ✅ Can map to QID |
| **PERS** | Personal | Concept: Q5 (human) / personal motivations | ⚠️ Broad concept |
| **MIL** | Military | Concept: Q49892 (military) | ✅ Can map to QID |
| **ECON** | Economic | Concept: Q11425 (economics) | ✅ Can map to QID |
| **CONST** | Constitutional | Concept: Q7755 (constitution) | ✅ Can map to QID |
| **MORAL** | Moral | Concept: Q177639 (ethics) | ✅ Can map to QID |
| **CULT** | Cultural | Concept: Q11042 (culture) | ✅ Can map to QID |
| **RELIG** | Religious | Concept: Q9174 (religion) | ✅ Can map to QID |
| **DIPL** | Diplomatic | Concept: Q1889 (diplomacy) | ✅ Can map to QID |
| **SURV** | Survival | Concept: Q2057971 (survival) | ✅ Can map to QID |

**Wikidata Properties for Goals/Motives:**
- **P3716** - "motive" (if exists)
- **P3717** - "goal" (if exists)  
- **P8264** - "intention" (if exists)
- **P1476** - "title" (not relevant)
- No direct "goal type" property found

**Conclusion**: Goal types align with **Wikidata QIDs** (concepts), not properties. These are **classifications/categories** rather than relationships.

---

### 2. Trigger Types → Wikidata Mapping

**Alignment:**

| Our Code | Our Type | Wikidata Equivalent | Alignment |
|----------|----------|---------------------|-----------|
| **MORAL_TRIGGER** | Moral | Q177639 (ethics) / moral concepts | ✅ Concept-based |
| **EMOT** | Emotional | Q9418 (emotion) | ✅ Concept QID |
| **POL_TRIGGER** | Political | Q7163 (politics) | ✅ Concept QID |
| **EXT_THREAT** | External Threat | Q41207 (threat) | ✅ Concept QID |
| **LEGAL** | Legal | Q4932206 (law) | ✅ Concept QID |
| **AMB** | Ambition | Concept: ambition (may not have QID) | ⚠️ May need to create |

**Conclusion**: Trigger types also align with **Wikidata QIDs** (concepts), not properties.

---

### 3. Action Types → Wikidata Mapping

**Stronger Alignment Possible:**

| Our Code | Our Type | Wikidata Equivalent | Alignment |
|----------|----------|---------------------|-----------|
| **REVOL** | Political Revolution | Q10931 (revolution) | ✅ Entity type QID |
| **MIL_ACT** | Military Action | Q178561 (battle) / Q198 (war) | ✅ Event types |
| **CRIME** | Criminal Act | Q3820 (massacre) / criminal acts | ✅ Event types |
| **DIPL_ACT** | Diplomatic Action | Q93288 (treaty) / diplomatic events | ✅ Entity types |
| **ECON_ACT** | Economic Action | Economic events (trade, etc.) | ✅ Can map |
| **LEGAL_ACT** | Legal Action | Q1787438 (decree) / Q7817 (law) | ✅ Entity types |
| **RELIG_ACT** | Religious Action | Religious events/concepts | ✅ Can map |

**Wikidata Properties for Actions:**
- **P31** - "instance of" (can classify actions as instances of event types)
- **P361** - "part of" (for action sequences)
- **P828** - "has cause" (for triggers)
- **P276** - "location" (where action occurred)

**Conclusion**: Action types align with both:
- **Wikidata QIDs** (event/entity types)
- **Wikidata Properties** (for relationships)

---

### 4. Result Types → Wikidata Mapping

**Similar to Action Types:**

| Our Code | Our Type | Wikidata Equivalent | Alignment |
|----------|----------|---------------------|-----------|
| **POL_TRANS** | Political Transformation | Q10931 (revolution) / regime change | ✅ Event types |
| **CONQUEST** | Conquest | Q178561 (battle) / military victory | ✅ Event types |
| **ALLIANCE** | Alliance | Q93288 (treaty) | ✅ Entity type |
| **INST_CREATE** | Institutional Creation | Q294414 (public office) / institutions | ✅ Entity types |

**Conclusion**: Result types align with **Wikidata QIDs** (outcome/entity types).

---

## Key Findings

### ✅ What Aligns Well

1. **Goal/Trigger/Action/Result Types → Wikidata QIDs (Concepts)**
   - These are **classifications/categories**
   - Can map to Wikidata QIDs for concepts (politics, economics, military, etc.)
   - Example: POL → Q7163 (politics)

2. **Action Types → Wikidata Event Types**
   - Action types map to Wikidata event/entity type QIDs
   - Example: REVOL → Q10931 (revolution)
   - Example: MIL_ACT → Q178561 (battle)

3. **Result Types → Wikidata Outcome Types**
   - Result types map to outcome/consequence concepts
   - Example: CONQUEST → Q178561 (battle) / victory concepts

### ⚠️ What Doesn't Align Directly

1. **No Direct Wikidata Property for "Goal Type"**
   - Wikidata doesn't have a property like "P_GOAL_TYPE"
   - We use codes (POL, PERS, etc.) which are **our internal classification**
   - These could be stored as QID references to concepts

2. **Trigger Types Are Conceptual**
   - These are **classifications** of what triggered an action
   - Not direct Wikidata properties, but can reference concept QIDs

3. **Custom Vocabularies**
   - Our codes (POL, PERS, REVOL, etc.) are **Chrystallum-specific**
   - They provide **semantic classification** beyond raw Wikidata

---

## Recommended Alignment Strategy

### Option 1: Map to Wikidata Concept QIDs (Recommended)

Store our codes as QID references to Wikidata concepts:

```cypher
// Example relationship with Wikidata-aligned goal_type
CREATE (person)-[:PERFORMED {
  goal_type: 'POL',  // Our code
  goal_type_qid: 'Q7163',  // Wikidata QID for "politics" concept
  goal: 'Overthrow monarchy',
  ...
}]->(event)
```

**Benefits:**
- ✅ Maintains our semantic codes (POL, PERS, etc.)
- ✅ Links to Wikidata concepts for interoperability
- ✅ Best of both worlds

### Option 2: Use Wikidata Properties for Actions

For **action types**, we already align with event types in our entity schema:

```cypher
// Action type aligns with event entity type
CREATE (event:Event {
  type: 'Revolution',  // Maps to Q10931
  qid: 'Q10931',  // Revolution QID
  ...
})
```

**Our action_type: 'REVOL'** → **Event type: 'Revolution'** → **QID: Q10931**

---

## Specific Wikidata Mappings

### Goal Types → Wikidata QIDs

| Our Code | Wikidata QID | Wikidata Label |
|----------|--------------|----------------|
| POL | Q7163 | politics |
| PERS | Q5 | human (for personal motivations) |
| MIL | Q49892 | military |
| ECON | Q11425 | economics |
| CONST | Q7755 | constitution |
| MORAL | Q177639 | ethics |
| CULT | Q11042 | culture |
| RELIG | Q9174 | religion |
| DIPL | Q1889 | diplomacy |
| SURV | Q2057971 | survival |

### Action Types → Wikidata Event Type QIDs

| Our Code | Wikidata QID | Wikidata Label |
|----------|--------------|----------------|
| REVOL | Q10931 | revolution |
| MIL_ACT | Q178561 | battle |
| CRIME | Q3820 | massacre (or other crime types) |
| DIPL_ACT | Q93288 | treaty |
| CONST_INNOV | Q7755 | constitution |
| LEGAL_ACT | Q7817 | law / Q1787438 decree |

---

## Recommendation

### ✅ **Keep Our Codes, Add Wikidata QID References**

**Best Approach**: Maintain our semantic codes (POL, PERS, REVOL, etc.) but add optional Wikidata QID references:

```cypher
CREATE (person)-[:PERFORMED {
  // Our semantic codes (primary)
  goal_type: 'POL',
  trigger_type: 'MORAL_TRIGGER',
  action_type: 'REVOL',
  result_type: 'POL_TRANS',
  
  // Wikidata alignment (optional, for interoperability)
  goal_type_qid: 'Q7163',  // politics
  trigger_type_qid: 'Q177639',  // ethics
  action_type_qid: 'Q10931',  // revolution
  result_type_qid: 'Q10931',  // revolution/transformation
  
  // ... rest of properties
}]->(event)
```

**Benefits:**
1. ✅ Maintains our semantic classification system
2. ✅ Enables Wikidata integration/interoperability
3. ✅ Allows queries by both our codes AND Wikidata QIDs
4. ✅ Flexible - QIDs are optional additions

---

## Next Steps

1. ✅ **Create mapping file**: `action_structure_wikidata_mapping.csv`
2. ✅ **Update schema documentation** with Wikidata QID references
3. ✅ **Update extraction prompts** to optionally include Wikidata QIDs
4. ⚠️ **Consider**: Should goal_type_qid be required or optional?

---

## Summary

**Answer**: Our goal types, trigger types, action types, and result types align with **Wikidata QIDs (concepts/entity types)**, NOT with Wikidata properties. They are **semantic classifications** that can reference Wikidata concepts for interoperability.

**Recommendation**: Keep our codes, add optional Wikidata QID references for alignment.




