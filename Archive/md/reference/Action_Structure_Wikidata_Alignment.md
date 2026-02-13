# Action Structure Vocabularies - Wikidata Alignment

## Summary

**Answer**: Our goal types, trigger types, action types, and result types align with **Wikidata QIDs (concepts/entity types)**, NOT with Wikidata properties.

---

## Alignment Type

### ✅ **Strong Alignment: Action Types → Entity Types**

Many of our action types already align with entity types in our `neo4j_entities_deduplicated.csv`:

| Our Action Type | Code | Wikidata QID | Already in Entity CSV? |
|-----------------|------|--------------|------------------------|
| Political Revolution | REVOL | Q10931 (revolution) | ✅ **Yes** - Event type |
| Military Action | MIL_ACT | Q178561 (battle) | ✅ **Yes** - Event type |
| Criminal Act | CRIME | Q3820 (massacre) | ✅ **Yes** - Event type |
| Diplomatic Action | DIPL_ACT | Q93288 (treaty) | ✅ **Yes** - Agreement type |
| Constitutional Innovation | CONST_INNOV | Q7755 (constitution) | ✅ **Yes** - Agreement type |
| Legal Action | LEGAL_ACT | Q1787438 (decree) | ✅ **Yes** - Agreement type |
| Religious Action | RELIG_ACT | Q9174 (religion) | ✅ **Yes** - Religious type |

**This is excellent alignment!** Our action types directly map to entity types we already track.

---

### ⚠️ **Partial Alignment: Goal/Trigger Types → Concepts**

Goal and trigger types align with **Wikidata concepts** (not entity types):

| Our Code | Type | Wikidata QID | Wikidata Label | Alignment |
|----------|------|--------------|----------------|-----------|
| POL | Political | Q7163 | politics | ✅ Concept QID |
| MIL | Military | Q49892 | military | ✅ Concept QID |
| ECON | Economic | Q11425 | economics | ✅ Concept QID |
| CONST | Constitutional | Q7755 | constitution | ✅ Entity type (already tracked) |
| RELIG | Religious | Q9174 | religion | ✅ Entity type (already tracked) |
| MORAL | Moral | Q177639 | ethics | ✅ Concept QID |
| CULT | Cultural | Q11042 | culture | ✅ Concept QID |
| DIPL | Diplomatic | Q1889 | diplomacy | ✅ Concept QID |

**These are semantic classifications** that can reference Wikidata concept QIDs.

---

## Key Insight

### Action Types = Entity Types (Strong Alignment)

Our action types (REVOL, MIL_ACT, CRIME, etc.) are essentially **entity types** we already have in our schema:

```
Action Type "REVOL" → Entity Type "Revolution" → QID Q10931
Action Type "MIL_ACT" → Entity Type "Battle" → QID Q178561
Action Type "CRIME" → Entity Type "Massacre" → QID Q3820
```

This means when we create an Event node with `type: 'Revolution'`, it already has the Wikidata alignment (Q10931).

---

## Recommended Implementation

### Option 1: Reference Entity Types (For Action Types)

Since action types align with entity types, we can reference them:

```cypher
CREATE (person)-[:PERFORMED {
  action_type: 'REVOL',  // Our code
  action_type_entity_type: 'Revolution',  // Maps to entity type
  action_type_qid: 'Q10931',  // From entity schema
  ...
}]->(revolutionEvent:Event {
  type: 'Revolution',  // Entity type
  qid: 'Q10931'  // Same QID!
})
```

### Option 2: Add Wikidata QID References (For Goal/Trigger Types)

For goal and trigger types, add optional QID references:

```cypher
CREATE (person)-[:PERFORMED {
  goal_type: 'POL',  // Our code
  goal_type_qid: 'Q7163',  // Optional: Wikidata concept QID
  trigger_type: 'MORAL_TRIGGER',
  trigger_type_qid: 'Q177639',  // Optional: Wikidata concept QID
  ...
}]->(event)
```

---

## Complete Mapping

See `action_structure_wikidata_mapping.csv` for complete mapping of:
- Goal types → Wikidata QIDs
- Trigger types → Wikidata QIDs  
- Action types → Wikidata QIDs (with entity type references)
- Result types → Wikidata QIDs

---

## Benefits of Alignment

1. ✅ **Interoperability**: Can query by both our codes and Wikidata QIDs
2. ✅ **Validation**: Can verify entity types against Wikidata
3. ✅ **Enrichment**: Can pull additional data from Wikidata for aligned concepts
4. ✅ **Consistency**: Action types already align with our entity schema

---

## Recommendation

**Keep our codes as primary**, but add optional Wikidata QID references for alignment. The action types especially have strong alignment since they map to entity types we already track.

