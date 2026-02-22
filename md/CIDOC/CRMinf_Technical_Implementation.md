# CRMinf Technical Implementation

## How CRMinf Works Technically

Detailed technical explanation of CRMinf (CIDOC-CRM Inference Extension) - the mechanics, structure, and implementation.

---

## Core Concept

**CRMinf adds inference and reasoning capabilities to CIDOC-CRM by modeling:**
- **Beliefs** (what we believe to be true)
- **Inferences** (how we draw conclusions)
- **Evidence** (what supports beliefs)
- **Reasoning chains** (evidence → inference → belief → fact)

---

## Technical Architecture

### 1. Core Classes

#### E2_Belief (Belief Entity)

**What it is:**
- Represents a belief or assumption about something
- Can be held by a person, institution, or system
- Has a level of certainty/confidence

**Technical Structure:**
```rdf
# RDF/Turtle representation
:belief_1 a crminf:E2_Belief ;
    rdfs:label "Belief that Caesar crossed Rubicon" ;
    crminf:U4_has_certainty :certainty_high .
```

**Properties:**
- `U4_has_certainty`: Level of certainty (high, medium, low, unknown)
- `P1_is_identified_by`: Labels/names for the belief
- `P2_has_type`: Type of belief (hypothesis, conclusion, assumption)

---

#### E5_Inference_Making (Inference Process)

**What it is:**
- The process of making an inference
- The reasoning activity itself
- Links evidence to conclusions

**Technical Structure:**
```rdf
:inference_1 a crminf:E5_Inference_Making ;
    rdfs:label "Inference from primary sources" ;
    crminf:I1_inferred_from :evidence_1, :evidence_2 ;
    crminf:I2_believed_to_hold :fact_1 .
```

**Properties:**
- `I1_inferred_from`: What evidence was used
- `I2_believed_to_hold`: What conclusion was reached
- `P4_has_time-span`: When the inference was made
- `P11_had_participant`: Who made the inference

---

#### E13_Belief_Revision (Belief Update)

**What it is:**
- Change or update to a belief
- Models how beliefs evolve with new evidence
- Tracks belief history

**Technical Structure:**
```rdf
:revision_1 a crminf:E13_Belief_Revision ;
    rdfs:label "Updated belief based on new archaeological evidence" ;
    crminf:I7_has_object :old_belief_1 ;
    crminf:I8_has_result :new_belief_1 ;
    crminf:I1_inferred_from :new_evidence_1 .
```

**Properties:**
- `I7_has_object`: The old belief being revised
- `I8_has_result`: The new/revised belief
- `I1_inferred_from`: New evidence that caused revision

---

### 2. Key Properties

#### I1_inferred_from (Inferred From)

**Technical Definition:**
- Property linking inference/belief to evidence
- Domain: E5_Inference_Making, E13_Belief_Revision
- Range: Any CIDOC-CRM entity (E1_CRM_Entity)

**How it works:**
```rdf
# Inference is based on evidence
:inference_1 crminf:I1_inferred_from :source_suetonius ;
             crminf:I1_inferred_from :source_plutarch ;
             crminf:I1_inferred_from :archaeological_find .

# Belief revision is based on new evidence
:revision_1 crminf:I1_inferred_from :new_dating_evidence .
```

**Mechanics:**
- Multiple `I1_inferred_from` properties allowed (multiple evidence sources)
- Evidence can be any entity type (document, observation, other beliefs)
- Creates reasoning chain: Evidence → Inference → Conclusion

---

#### I2_believed_to_hold (Believed to Hold)

**Technical Definition:**
- Property linking inference/belief to the fact/conclusion
- Domain: E5_Inference_Making, E2_Belief
- Range: Any CIDOC-CRM entity (E1_CRM_Entity)

**How it works:**
```rdf
# Inference concludes a fact
:inference_1 crminf:I2_believed_to_hold :crossing_event .

# Belief is about a fact
:belief_1 crminf:I2_believed_to_hold :crossing_event .
```

**Mechanics:**
- Links reasoning process to the conclusion
- The conclusion is typically a CIDOC-CRM entity (E5_Event, E21_Person, etc.)
- Can have multiple beliefs about the same fact

---

#### I3_has_note (Has Note)

**Technical Definition:**
- Property for notes/explanations about inference
- Domain: E5_Inference_Making, E2_Belief
- Range: E62_String (text string)

**How it works:**
```rdf
:inference_1 crminf:I3_has_note "Both Suetonius and Plutarch independently describe this event, providing strong corroboration" .
```

**Mechanics:**
- Human-readable explanation of reasoning
- Can provide context, methodology, justification
- Useful for transparency and auditability

---

#### I4_has_uncertainty (Has Uncertainty)

**Technical Definition:**
- Property for uncertainty quantification
- Domain: E5_Inference_Making, E2_Belief
- Range: E60_Number (numeric value) or controlled vocabulary

**How it works:**
```rdf
:belief_1 crminf:I4_has_uncertainty :uncertainty_medium ;
          crminf:U4_has_certainty :certainty_high .
```

**Mechanics:**
- Can express uncertainty as:
  - Numeric value (0.0-1.0)
  - Controlled vocabulary (high, medium, low, unknown)
  - Probability distribution
- Separate from certainty (uncertainty is the opposite)

---

#### I5_incorporated_in (Incorporated In)

**Technical Definition:**
- Property linking inference to the work/document that incorporates it
- Domain: E5_Inference_Making
- Range: E31_Document, E73_Information_Object

**How it works:**
```rdf
:inference_1 crminf:I5_incorporated_in :scholarly_article_1 .
```

**Mechanics:**
- Links inference to where it appears
- Useful for citation and provenance
- Can trace how inferences are used in publications

---

### 3. Reasoning Chain Structure

#### Complete Inference Chain

**Technical Flow:**
```
Evidence (Sources/Observations)
  ↓ I1_inferred_from
Inference Making (Reasoning Process)
  ↓ I2_believed_to_hold
Belief (Conclusion)
  ↓ I2_believed_to_hold (or direct link)
Fact (CIDOC-CRM Entity)
```

**Example Implementation:**
```rdf
# Evidence entities
:source_suetonius a crm:E31_Document ;
    rdfs:label "Suetonius - Life of Caesar" .

:source_plutarch a crm:E31_Document ;
    rdfs:label "Plutarch - Life of Caesar" .

# Inference process
:inference_crossing a crminf:E5_Inference_Making ;
    rdfs:label "Inference about Rubicon crossing" ;
    crminf:I1_inferred_from :source_suetonius, :source_plutarch ;
    crminf:I2_believed_to_hold :belief_crossing ;
    crminf:I3_has_note "Two independent primary sources agree" ;
    crminf:I4_has_uncertainty :uncertainty_low .

# Belief
:belief_crossing a crminf:E2_Belief ;
    rdfs:label "Belief that Caesar crossed Rubicon in 49 BCE" ;
    crminf:I2_believed_to_hold :crossing_event ;
    crminf:U4_has_certainty :certainty_high .

# The actual fact (CIDOC-CRM entity)
:crossing_event a crm:E5_Event ;
    rdfs:label "Crossing of the Rubicon" ;
    crm:P4_has_time-span :timespan_49bce .
```

---

### 4. Belief Revision Chain

**Technical Flow:**
```
Old Belief
  ↓ I7_has_object
Belief Revision (Update Process)
  ↓ I8_has_result
New Belief
  ↓ I1_inferred_from
New Evidence
```

**Example Implementation:**
```rdf
# Old belief
:old_belief_date a crminf:E2_Belief ;
    rdfs:label "Belief: Crossing occurred January 10, 49 BCE" .

# New evidence
:new_dating_evidence a crm-sci:S4_Observation ;
    rdfs:label "Radiocarbon dating of artifacts" .

# Belief revision
:revision_1 a crminf:E13_Belief_Revision ;
    rdfs:label "Revision based on new dating" ;
    crminf:I7_has_object :old_belief_date ;
    crminf:I8_has_result :new_belief_date ;
    crminf:I1_inferred_from :new_dating_evidence ;
    crm:P4_has_time-span :timespan_2024 .

# New belief
:new_belief_date a crminf:E2_Believed ;
    rdfs:label "Belief: Crossing occurred January 10-11, 49 BCE" .
```

---

## Technical Implementation in Neo4j/Cypher

### Structure

```cypher
// Evidence (CIDOC-CRM entities)
(source1:Document {
  label: 'Suetonius - Life of Caesar',
  type: 'E31_Document'
})

(source2:Document {
  label: 'Plutarch - Life of Caesar',
  type: 'E31_Document'
})

// Inference Making process
(inference:InferenceMaking {
  label: 'Inference about Rubicon crossing',
  type: 'E5_Inference_Making',
  note: 'Two independent primary sources agree',
  uncertainty: 'low'
})

// Belief
(belief:Belief {
  label: 'Belief that Caesar crossed Rubicon',
  type: 'E2_Belief',
  certainty: 'high'
})

// Actual fact (CIDOC-CRM event)
(crossingEvent:Event {
  label: 'Crossing of the Rubicon',
  type: 'E5_Event',
  start_date: '-0049-01-10'
})

// Relationships
(source1) -[:I1_INFERRED_FROM]-> (inference)
(source2) -[:I1_INFERRED_FROM]-> (inference)
(inference) -[:I2_BELIEVED_TO_HOLD]-> (belief)
(belief) -[:I2_BELIEVED_TO_HOLD]-> (crossingEvent)
```

---

## Query Patterns

### 1. Find All Evidence for a Fact

```cypher
// Find all evidence supporting a belief about an event
MATCH (event:Event {label: 'Crossing of Rubicon'})
MATCH (belief:Belief)-[:I2_BELIEVED_TO_HOLD]->(event)
MATCH (inference:InferenceMaking)-[:I2_BELIEVED_TO_HOLD]->(belief)
MATCH (evidence)-[:I1_INFERRED_FROM]->(inference)
RETURN evidence, inference, belief
```

### 2. Find Reasoning Chain

```cypher
// Complete reasoning chain: Evidence → Inference → Belief → Fact
MATCH path = (evidence)-[:I1_INFERRED_FROM]->
             (inference:InferenceMaking)-[:I2_BELIEVED_TO_HOLD]->
             (belief:Belief)-[:I2_BELIEVED_TO_HOLD]->
             (fact:Event)
WHERE fact.label = 'Crossing of Rubicon'
RETURN path
```

### 3. Find Conflicting Beliefs

```cypher
// Find multiple beliefs about the same fact
MATCH (belief1:Belief)-[:I2_BELIEVED_TO_HOLD]->(event:Event)
MATCH (belief2:Belief)-[:I2_BELIEVED_TO_HOLD]->(event)
WHERE belief1.certainty <> belief2.certainty
  OR belief1 <> belief2
RETURN event, belief1, belief2
```

### 4. Find Belief Revisions

```cypher
// Find how a belief was revised
MATCH (oldBelief:Belief)<-[:I7_HAS_OBJECT]-
      (revision:BeliefRevision)-[:I8_HAS_RESULT]->
      (newBelief:Belief)
RETURN oldBelief, revision, newBelief
```

---

## Comparison with Chrystallum Approach

### Chrystallum (Current)

```cypher
(event:Event {
  label: 'Crossing of Rubicon',
  confidence: 0.95,
  validation_status: 'verified',
  sources: [
    {source: 'Suetonius', source_type: 'primary', tier: 1},
    {source: 'Plutarch', source_type: 'primary', tier: 1}
  ]
})
```

**Characteristics:**
- ✅ Simpler structure
- ✅ Properties directly on entity
- ✅ Sources as metadata
- ⚠️ Less explicit reasoning chain

---

### CRMinf Approach

```cypher
// Multiple entities for reasoning chain
(evidence1:Document {...})
(evidence2:Document {...})
(inference:InferenceMaking {...})
(belief:Belief {...})
(event:Event {...})

// Explicit relationships
(evidence1) -[:I1_INFERRED_FROM]-> (inference)
(inference) -[:I2_BELIEVED_TO_HOLD]-> (belief)
(belief) -[:I2_BELIEVED_TO_HOLD]-> (event)
```

**Characteristics:**
- ✅ Explicit reasoning chain
- ✅ Can model multiple beliefs about same fact
- ✅ Can model belief revisions
- ⚠️ More complex structure
- ⚠️ More entities and relationships

---

## When to Use CRMinf

### ✅ Use CRMinf When:

1. **Multiple Competing Beliefs**
   - Different scholars have different interpretations
   - Need to model disagreement

2. **Complex Reasoning Chains**
   - Evidence → Inference → Conclusion chains
   - Multiple evidence sources per conclusion

3. **Belief Revision Tracking**
   - How beliefs change over time
   - Historical development of understanding

4. **Transparent Reasoning**
   - Need to show exactly how conclusions were reached
   - Audit trail for inferences

### ❌ Don't Use CRMinf When:

1. **Simple Facts**
   - Well-established, uncontested facts
   - Direct source attribution sufficient

2. **Simple Confidence Scores**
   - Just need confidence levels
   - No need for explicit reasoning chains

3. **Performance Critical**
   - CRMinf adds complexity
   - More entities and relationships = slower queries

---

## Hybrid Approach: Chrystallum + CRMinf

### Combine Both

```cypher
// Chrystallum structure (simple, fast queries)
(event:Event {
  label: 'Crossing of Rubicon',
  confidence: 0.95,
  start_date: '-0049-01-10'
})

// CRMinf structure (explicit reasoning, when needed)
(inference:InferenceMaking {
  label: 'Inference from primary sources'
})

(belief:Belief {
  label: 'Belief about crossing date',
  certainty: 'high'
})

// Link them
(belief) -[:I2_BELIEVED_TO_HOLD]-> (event)

// Use CRMinf for complex cases, Chrystallum for simple cases
```

**Benefits:**
- ✅ Simple facts: Use Chrystallum (fast, simple)
- ✅ Complex reasoning: Use CRMinf (explicit chains)
- ✅ Best of both worlds

---

## Summary

### How CRMinf Works Technically:

1. **Entities:**
   - `E2_Belief`: What we believe
   - `E5_Inference_Making`: How we reason
   - `E13_Belief_Revision`: How beliefs change

2. **Properties:**
   - `I1_inferred_from`: Links to evidence
   - `I2_believed_to_hold`: Links to conclusions
   - `I3_has_note`: Explanations
   - `I4_has_uncertainty`: Uncertainty quantification

3. **Mechanics:**
   - Evidence → Inference → Belief → Fact chain
   - Explicit reasoning relationships
   - Can model multiple beliefs, revisions, conflicts

4. **Implementation:**
   - RDF/OWL ontology
   - Multiple entities and relationships
   - Queryable reasoning chains

**For Chrystallum:** CRMinf is useful for complex reasoning cases but adds complexity. Consider hybrid approach: simple facts = Chrystallum, complex reasoning = CRMinf.



