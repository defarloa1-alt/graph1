# "Caesar Crossed the Rubicon" - Most Concise and Most Granular Representations

Using concepts from `JSON/chrystallum_schema.json`, here are representations from most concise to most granular.

---

## Option 1: Most Concise

**Single relationship with minimal action structure:**

```cypher
(Caesar:Human {qid: 'Q1048'})
-[:LOCATED_IN {
  action_type: 'MIL_ACT',
  action_type_qid: 'Q178561',
  result_type: 'POL_TRANS',
  result_type_qid: 'Q10931',
  start_date: '-0049-01-10'
}]->(Rubicon:River {qid: 'Q192946'})
```

---

## Option 2: Most Concise with ALL Labels and QIDs

**Complete representation with all entity types, relationship types, and action structure QIDs:**

```cypher
// Entities with type QIDs
(Caesar:Human {
  id: 'caesar_julius',
  label: 'Julius Caesar',
  type: 'Human',
  type_qid: 'Q5',
  qid: 'Q1048'
})

(Rubicon:River {
  id: 'rubicon',
  label: 'Rubicon',
  type: 'River',
  type_qid: 'Q4022',
  qid: 'Q192946'
})

// Relationship with all action structure QIDs
(Caesar)-[:LOCATED_IN {
  goal_type: 'POL',
  goal_type_qid: 'Q7163',
  trigger_type: 'OPPORT',
  trigger_type_qid: 'Q18108648',
  action_type: 'MIL_ACT',
  action_type_qid: 'Q178561',
  result_type: 'POL_TRANS',
  result_type_qid: 'Q10931',
  start_date: '-0049-01-10',
  narrative: 'Caesar crossed the Rubicon'
}]->(Rubicon)
```

---

## Option 3: MOST GRANULAR (Complete Schema Compliance)

**Full representation with all properties, metadata, validation, and extensions:**

```cypher
// Entities with complete structure
(Caesar:Human {
  // Core properties
  id: 'Q1048',
  unique_id: 'Q1048_HUM_JULIUS_CAESAR',
  label: 'Julius Caesar',
  type: 'Human',
  type_qid: 'Q5',
  qid: 'Q1048',
  
  // Temporal extensions
  start_date: '-0100-07-12',  // Birth date (if known)
  end_date: '-0044-03-15',     // Death date
  date_precision: 'day',
  temporal_uncertainty: false,
  
  // Person extensions
  image_url: 'https://upload.wikimedia.org/wikipedia/commons/...',
  image_source: 'Wikimedia Commons',
  wikimedia_image: 'File:Julius_Caesar.jpg',
  related_fiction: [
    {title: 'Julius Caesar', author: 'William Shakespeare', work_type: 'Play', qid: 'Q104832'}
  ],
  related_nonfiction: [
    {title: 'Life of Caesar', author: 'Plutarch', work_type: 'Biography', qid: 'Q...'}
  ],
  online_text_available: true,
  online_text_sources: [
    {source: 'Project Gutenberg', url: '...', format: 'HTML', language: 'en'}
  ],
  
  // Backbone alignment
  backbone_fast: 'fst01411640',
  backbone_lcc: 'DG261.C35',
  backbone_lcsh: ['Caesar, Julius'],
  backbone_marc: 'sh85018691',
  
  // Metadata
  test_case: 'caesar_rubicon',
  confidence: 0.98,
  validation_status: 'verified'
})

(Rubicon:River {
  // Core properties
  id: 'Q192946',
  unique_id: 'Q192946_RIVER_RUBICON',
  label: 'Rubicon',
  type: 'River',
  type_qid: 'Q4022',
  qid: 'Q192946',
  
  // Geographic extensions
  geo_coordinates: {
    latitude: 44.1675,
    longitude: 12.3833,
    precision: 'approximate'
  },
  pleiades_id: '393484',
  pleiades_link: 'https://pleiades.stoa.org/places/393484',
  google_earth_link: 'https://earth.google.com/web/@44.1675,12.3833,0a,0y,0h,0t,0r',
  
  // Backbone alignment
  backbone_fast: 'fst01310173',
  backbone_lcc: 'DG262',
  backbone_lcsh: ['Rubicon River (Italy)'],
  backbone_marc: 'sh85115828',
  
  // Metadata
  test_case: 'caesar_rubicon',
  confidence: 0.95,
  validation_status: 'verified'
})

// Relationship with COMPLETE action structure
(Caesar)-[:LOCATED_IN {
  // Action Structure - Goal (G)
  goal_type: 'POL',
  goal_type_qid: 'Q7163',
  goal_text: 'Seize political power in Rome and prevent prosecution',
  
  // Action Structure - Trigger (T)
  trigger_type: 'OPPORT',
  trigger_type_qid: 'Q18108648',
  trigger_text: 'Opportunity to march on Rome with his legions',
  
  // Action Structure - Action (Act)
  action_type: 'MIL_ACT',
  action_type_qid: 'Q178561',
  action_description: 'Caesar led his army across the Rubicon river, violating Roman law',
  
  // Action Structure - Result (Res)
  result_type: 'POL_TRANS',
  result_type_qid: 'Q10931',
  result_text: 'Initiated Roman Civil War, leading to end of Republic and rise of Empire',
  
  // Action Structure - Narrative (N)
  narrative: 'In 49 BCE, Julius Caesar crossed the Rubicon river with his army, defying the Roman Senate\'s order to disband. This act violated Roman law prohibiting generals from bringing armies into Italy, effectively declaring civil war and setting in motion events that would end the Roman Republic.',
  
  // Temporal properties
  start_date: '-0049-01-10',
  end_date: null,  // Instantaneous event
  date_precision: 'day',
  temporal_uncertainty: false,
  
  // Validation metadata
  confidence: 0.95,
  validation_status: 'verified',
  sources: [
    {
      source: 'Suetonius - Life of Caesar',
      source_type: 'primary',
      source_quality_tier: 1,
      citation: 'Suet. Caes. 31-32'
    },
    {
      source: 'Plutarch - Life of Caesar',
      source_type: 'primary',
      source_quality_tier: 1,
      citation: 'Plut. Caes. 32'
    },
    {
      source: 'Appian - Civil Wars',
      source_type: 'primary',
      source_quality_tier: 1,
      citation: 'App. BCiv. 2.35'
    }
  ],
  
  // Standard properties
  test_case: 'caesar_rubicon',
  created_date: '2025-01-02',
  last_validated: '2025-01-02',
  validator_agent: 'chrystallum_v1.0'
}]->(Rubicon)
```

---

## Schema Components Reference

### Entity Structure (Mathematical Definition)
$$v = (id, unique\_id, label, type, qid, P, metadata, extensions)$$

### Action Structure (Mathematical Definition)
$$A = (G, T, Act, Res, N)$$

Where:
- **G** = (goal_text, goal_type, goal_type_qid)
- **T** = (trigger_text, trigger_type, trigger_type_qid)
- **Act** = (action_type, action_type_qid, action_description)
- **Res** = (result_text, result_type, result_type_qid)
- **N** = narrative

### Relationship Structure
$$R_a = (source, target, rel\_type, properties, action\_structure, metadata)$$

---

## QID Reference

### Entity Types
- `Human` (Q5) - Individual person
- `River` (Q4022) - Watercourse

### Entities
- `Julius Caesar` (Q1048) - Historical figure
- `Rubicon` (Q192946) - River in Italy

### Action Structure QIDs
- `goal_type: 'POL'` → Q7163 (politics)
- `trigger_type: 'OPPORT'` → Q18108648 (opportunity)
- `action_type: 'MIL_ACT'` → Q178561 (battle)
- `result_type: 'POL_TRANS'` → Q10931 (revolution)

---

## Comparison: Concise vs Granular

| Component | Concise | Granular |
|-----------|---------|----------|
| **Entity properties** | id, label, type, qid | + unique_id, extensions, metadata, backbone |
| **Action structure** | action_type, result_type (codes only) | + goal, trigger, action, result (full text + codes + QIDs), narrative |
| **Temporal data** | start_date | + end_date, date_precision, temporal_uncertainty |
| **Validation** | None | + confidence, validation_status, sources |
| **Metadata** | None | + test_case, created_date, validator_agent |

---

## Usage Recommendations

### Use **Concise** when:
- ✅ Quick prototyping
- ✅ Testing schema compliance
- ✅ Minimal viable representation
- ✅ High-confidence, well-known facts

### Use **Granular** when:
- ✅ Production knowledge graph
- ✅ Complex historical analysis
- ✅ Multi-source validation required
- ✅ Interoperability with external systems
- ✅ Research and scholarly applications

---

## Cypher Query Templates

### Most Concise Template
```cypher
MERGE (person:Human {qid: $person_qid})
MERGE (place:River {qid: $place_qid})
MERGE (person)-[:LOCATED_IN {
  action_type: $action_type,
  action_type_qid: $action_type_qid,
  result_type: $result_type,
  result_type_qid: $result_type_qid,
  start_date: $start_date
}]->(place)
```

### Most Granular Template
```cypher
MERGE (person:Human {
  id: $person_id,
  unique_id: $person_unique_id,
  label: $person_label,
  type: 'Human',
  type_qid: 'Q5',
  qid: $person_qid,
  start_date: $person_start_date,
  end_date: $person_end_date,
  date_precision: $date_precision,
  backbone_fast: $backbone_fast,
  backbone_lcc: $backbone_lcc,
  test_case: $test_case,
  confidence: $confidence
})
MERGE (place:River {
  id: $place_id,
  unique_id: $place_unique_id,
  label: $place_label,
  type: 'River',
  type_qid: 'Q4022',
  qid: $place_qid,
  geo_coordinates: $geo_coordinates,
  pleiades_id: $pleiades_id,
  backbone_fast: $place_backbone_fast,
  test_case: $test_case,
  confidence: $confidence
})
MERGE (person)-[:LOCATED_IN {
  goal_type: $goal_type,
  goal_type_qid: $goal_type_qid,
  goal_text: $goal_text,
  trigger_type: $trigger_type,
  trigger_type_qid: $trigger_type_qid,
  trigger_text: $trigger_text,
  action_type: $action_type,
  action_type_qid: $action_type_qid,
  action_description: $action_description,
  result_type: $result_type,
  result_type_qid: $result_type_qid,
  result_text: $result_text,
  narrative: $narrative,
  start_date: $start_date,
  date_precision: $date_precision,
  confidence: $confidence,
  validation_status: $validation_status,
  sources: $sources,
  test_case: $test_case
}]->(place)
```

---

## Summary

**Most Concise:**
- 2 nodes, 1 edge
- Minimal action structure (codes + QIDs)
- Essential properties only

**Most Granular:**
- 2 nodes with full entity structure (unique_id, extensions, metadata, backbone alignment)
- 1 edge with complete action structure (G, T, Act, Res, N with full text + codes + QIDs)
- Complete temporal data (start/end dates, precision, uncertainty)
- Full validation metadata (confidence, sources, validation_status)
- Complete interoperability (backbone alignment, external links)

The granular version provides maximum semantic richness, validation, and interoperability while maintaining full schema compliance.
