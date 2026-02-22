# Action Structure with Wikidata QIDs - Complete Example

## Complete Relationship with Action Structure and Wikidata QIDs

### Example: Brutus Participates in Rebellion (509 BCE)

```cypher
// Full relationship with action structure and Wikidata alignment
(brutus:Human {
  id: 'Q156138',
  unique_id: 'Q156138_HUM_BRUTUS',
  label: 'Lucius Junius Brutus',
  qid: 'Q156138'
})-[:PARTICIPATED_IN {
  // Goal structure
  goal: 'Overthrow tyrannical monarchy and establish free government',
  goal_type: 'POL',              // Our semantic code
  goal_type_qid: 'Q7163',        // Wikidata: politics concept
  
  // Trigger structure
  trigger: 'Rape of Lucretia and public outrage',
  trigger_type: 'MORAL_TRIGGER', // Our semantic code
  trigger_type_qid: 'Q177639',   // Wikidata: ethics concept
  
  // Action structure
  action_type: 'REVOL',          // Our semantic code
  action_type_qid: 'Q10931',     // Wikidata: revolution entity type
  action_description: 'Brutus rallied the Roman people, expelled Tarquin and his family, and established the republic',
  
  // Result structure
  result: 'Monarchy overthrown, Roman Republic established',
  result_type: 'POL_TRANS',      // Our semantic code
  result_type_qid: 'Q10931',     // Wikidata: revolution entity type
  
  // Narrative
  narrative_summary: 'Following Lucretia\'s death and revelation of the crime, Lucius Junius Brutus, who had feigned foolishness to survive under Tarquin\'s tyranny, seized the moment. He rallied the Roman people by displaying Lucretia\'s body, expelled Tarquin and his family from Rome, and established the first consulship, marking the birth of the Roman Republic.',
  
  // Metadata
  role: 'Leader of the rebellion',
  temporal: '-509-01-01',
  location: 'Rome',
  confidence: 0.95,
  test_case: 'roman_kingdom_to_sulla'
}]->(rebellion:Event {
  id: 'C_REBELLION_509',
  unique_id: 'EVENT_REBELLION_509BC',
  label: 'Rebellion of 509 BC',
  type: 'Rebellion'
})
```

---

## Property Breakdown

### Required Properties (Our Semantic Codes)
- `goal_type`: `'POL'` - Our internal code
- `trigger_type`: `'MORAL_TRIGGER'` - Our internal code
- `action_type`: `'REVOL'` - Our internal code
- `result_type`: `'POL_TRANS'` - Our internal code

### Wikidata Alignment Properties (Optional but Recommended)
- `goal_type_qid`: `'Q7163'` - Maps to politics concept
- `trigger_type_qid`: `'Q177639'` - Maps to ethics concept
- `action_type_qid`: `'Q10931'` - Maps to revolution entity type
- `result_type_qid`: `'Q10931'` - Maps to revolution entity type

### Descriptive Properties
- `goal`: Human-readable goal description
- `trigger`: Human-readable trigger description
- `action_description`: Detailed action description
- `result`: Human-readable result description
- `narrative_summary`: Complete narrative context

---

## Wikidata QID Mapping Reference

See `Reference/action_structure_wikidata_mapping.csv` for complete mappings.

### Common Mappings Used in Examples

| Our Code | Wikidata QID | Wikidata Label | Type |
|----------|--------------|----------------|------|
| POL | Q7163 | politics | Concept |
| PERS | Q5 | human | Concept |
| MIL | Q49892 | military | Concept |
| MORAL_TRIGGER | Q177639 | ethics | Concept |
| REVOL | Q10931 | revolution | Entity Type |
| CRIME | Q3820 | massacre | Entity Type |
| POL_TRANS | Q10931 | revolution | Entity Type |
| TRAGIC | Q3820 | massacre | Entity Type |

---

## Query Examples with Wikidata QIDs

### Query by Wikidata QID
```cypher
// Find all relationships with political goals (using Wikidata QID)
MATCH ()-[r]->()
WHERE r.goal_type_qid = 'Q7163'  // politics
RETURN r
```

### Query by Our Code
```cypher
// Find all relationships with political goals (using our code)
MATCH ()-[r]->()
WHERE r.goal_type = 'POL'
RETURN r
```

### Query Both (Most Flexible)
```cypher
// Find all political revolutions (by code OR Wikidata QID)
MATCH ()-[r]->()
WHERE r.action_type = 'REVOL' 
   OR r.action_type_qid = 'Q10931'
RETURN r
```

---

## Benefits of Including Wikidata QIDs

1. **Interoperability**: Can query/export using standard Wikidata identifiers
2. **Validation**: Can verify our codes against Wikidata concepts
3. **Enrichment**: Can pull additional data from Wikidata for aligned concepts
4. **Future-proofing**: Easier integration with other knowledge graphs

---

## Complete Action Structure Schema

```cypher
{
  // Goal properties
  goal: String,                    // Human-readable goal
  goal_type: String,               // Our code (POL, PERS, MIL, etc.)
  goal_type_qid: String,           // Wikidata QID (optional)
  
  // Trigger properties
  trigger: String,                 // Human-readable trigger
  trigger_type: String,            // Our code (MORAL_TRIGGER, etc.)
  trigger_type_qid: String,        // Wikidata QID (optional)
  
  // Action properties
  action_type: String,             // Our code (REVOL, MIL_ACT, etc.)
  action_type_qid: String,         // Wikidata QID (optional)
  action_description: String,      // Detailed action description
  
  // Result properties
  result: String,                  // Human-readable result
  result_type: String,             // Our code (POL_TRANS, etc.)
  result_type_qid: String,         // Wikidata QID (optional)
  
  // Narrative
  narrative_summary: String,       // Complete narrative context
  
  // Metadata
  temporal: String,                // ISO 8601 date
  location: String,                // Location name
  confidence: Float,               // Confidence score (0.0-1.0)
  role: String                     // Optional role in action
}
```

---

## Summary

**Action structure properties include both**:
1. ✅ **Our semantic codes** (POL, REVOL, etc.) - Primary classification
2. ✅ **Wikidata QIDs** (*_qid properties) - For interoperability

**Both are stored as properties on relationships**, enabling flexible querying by either our codes or Wikidata identifiers.





