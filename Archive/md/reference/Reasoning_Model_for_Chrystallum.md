# Reasoning Model for Chrystallum's Integrated Structure

## The Problem

**Observation:** Chrystallum has:
- ✅ Vertices (entities) with **disparate integrated data** (FAST, Wikidata, CIDOC-CRM, ISO 8601, etc.)
- ✅ Connections (relationships) between entities
- ⚠️ **No explicit reasoning model** to make sense of it all

**Question:** What reasoning/inference capabilities would provide insight from this integrated structure?

---

## Why Reasoning Is Needed

### The Challenge: Disparate Data Integration

**Current Structure:**
```cypher
(entity:Human {
  // Multiple standards integrated
  backbone_fast: 'fst01411640',     // Library standard
  qid: 'Q1048',                      // Wikidata
  cidoc_crm_class: 'E21_Person',    // Museum standard
  viaf_id: '78287861',               // Authority control
  start_date: '-0100-07-12',        // ISO 8601
  pleiades_id: '393484'             // Geographic
})
```

**Problems:**
- ❌ Data from different sources may **conflict**
- ❌ Standards may have **different granularities**
- ❌ Missing **validation** across standards
- ❌ No way to **reason** about consistency
- ❌ No **inference** from integrated data

---

## Reasoning Models to Consider

### 1. **Multi-Standard Consistency Reasoning**

#### Problem

**Conflicting Data Across Standards:**
```
Entity A:
  - Wikidata: birth_date = "100 BCE"
  - FAST record: birth_date = "100-44 BCE"
  - MARC record: birth_date = "c. 100 BCE"
  - CIDOC-CRM: Time-Span = "100-44 BCE"

Are these consistent? How to resolve?
```

#### Reasoning Model

**Consistency Checker:**
```cypher
// Rule: Dates from different standards should be compatible
MATCH (e:Human)
WHERE e.wikidata_birth_date IS NOT NULL 
  AND e.marc_birth_date IS NOT NULL
WITH e,
  CASE 
    WHEN e.wikidata_birth_date = e.marc_birth_date THEN 'consistent'
    WHEN date_range_overlaps(e.wikidata_birth_date, e.marc_birth_date) THEN 'compatible'
    ELSE 'conflict'
  END AS consistency_status
WHERE consistency_status = 'conflict'
RETURN e, e.wikidata_birth_date, e.marc_birth_date
```

**Reasoning Logic:**
- ✅ **Exact match** = Consistent
- ✅ **Overlap** = Compatible (within uncertainty)
- ❌ **No overlap** = Conflict (flag for review)

---

### 2. **Cross-Standard Entity Resolution**

#### Problem

**Same Entity, Different Identifiers:**
```
VIAF ID: 78287861 = "Julius Caesar"
Wikidata QID: Q1048 = "Julius Caesar"
MARC ID: sh85018691 = "Caesar, Julius"
FAST ID: fst01411640 = "Caesar, Julius"

Are these the same? How to validate?
```

#### Reasoning Model

**Entity Resolution Algorithm:**

```python
def resolve_entity_candidates(identifier, standard):
    """
    Given an identifier from one standard,
    find matching entities using other standards.
    """
    # 1. Direct lookup by identifier
    entity = lookup_by_identifier(identifier, standard)
    
    # 2. Cross-reference with other standards
    matches = []
    
    # Check VIAF
    if entity.viaf_id:
        viaf_matches = lookup_by_viaf(entity.viaf_id)
        matches.extend(viaf_matches)
    
    # Check Wikidata
    if entity.qid:
        wikidata_matches = lookup_by_qid(entity.qid)
        matches.extend(wikidata_matches)
    
    # 3. Fuzzy matching on names/labels
    label_matches = fuzzy_match_labels(entity.label)
    matches.extend(label_matches)
    
    # 4. Temporal/spatial consistency
    consistent_matches = filter_by_temporal_spatial_consistency(matches, entity)
    
    # 5. Confidence scoring
    scored_matches = score_matches(consistent_matches, entity)
    
    return scored_matches
```

**Reasoning Rules:**
- ✅ **Same VIAF ID** = High confidence match
- ✅ **Same Wikidata QID** = High confidence match
- ✅ **Same dates + same name** = Medium confidence match
- ✅ **Different dates but compatible** = Low confidence (needs review)

---

### 3. **Inference from Integrated Data**

#### Problem

**Implicit Knowledge Not Explicitly Stated:**
```
Entity A:
  - backbone_lcc: 'DG241-269'  // Roman Republic period
  - start_date: '-0049-01-10'  // 49 BCE
  
Entity B:
  - backbone_lcc: 'DG241-269'  // Roman Republic period
  - start_date: '-0050-03-15'  // 50 BCE

Can we infer they're contemporaries?
Can we infer they're in the same historical period?
```

#### Reasoning Model

**Temporal-Spatial Inference:**

```cypher
// Rule: Entities in same period + overlapping dates = contemporaries
MATCH (a:Human), (b:Human)
WHERE a.backbone_lcc = b.backbone_lcc  // Same period classification
  AND a.start_date IS NOT NULL
  AND b.start_date IS NOT NULL
  AND a.end_date IS NOT NULL
  AND b.end_date IS NOT NULL
WITH a, b,
  CASE
    WHEN a.start_date <= b.end_date AND b.start_date <= a.end_date 
      THEN 'contemporary'
    WHEN ABS(a.start_date - b.start_date) <= INTERVAL({years: 10}) 
      THEN 'near_contemporary'
    ELSE 'not_contemporary'
  END AS temporal_relationship
WHERE temporal_relationship IN ['contemporary', 'near_contemporary']
MERGE (a)-[:INFERRED_CONTEMPORARY_OF {
  confidence: calculate_confidence(a, b),
  reasoning: 'Same LCC period + overlapping dates',
  inference_type: 'temporal-spatial'
}]->(b)
```

**Inference Types:**
1. **Temporal**: Contemporaneity, sequence, causality
2. **Spatial**: Co-location, geographic relationships
3. **Subject**: Same topic/subject classification
4. **Relationship**: Implied relationships from context

---

### 4. **Validation Reasoning**

#### Problem

**Data Quality Across Standards:**
```
Entity has:
  - Confidence: 0.95 (Chrystallum)
  - Validation: 'verified' (Chrystallum)
  - But Wikidata has: 'disputed' flag
  - And MARC has: 'uncertain' note

How to reconcile? What's the true confidence?
```

#### Reasoning Model

**Multi-Factor Confidence Reasoning:**

```python
def calculate_integrated_confidence(entity):
    """
    Calculate confidence based on multiple standards.
    """
    factors = {}
    
    # Factor 1: Chrystallum confidence
    factors['chrystallum'] = entity.confidence or 0.5
    
    # Factor 2: Wikidata validation
    if entity.wikidata_disputed:
        factors['wikidata'] = 0.3  # Low if disputed
    elif entity.wikidata_verified:
        factors['wikidata'] = 0.9  # High if verified
    else:
        factors['wikidata'] = 0.7  # Medium default
    
    # Factor 3: MARC authority
    if entity.marc_certainty == 'certain':
        factors['marc'] = 0.9
    elif entity.marc_certainty == 'uncertain':
        factors['marc'] = 0.5
    else:
        factors['marc'] = 0.7
    
    # Factor 4: Cross-standard consistency
    consistency_score = calculate_consistency(entity)
    factors['consistency'] = consistency_score
    
    # Factor 5: Source count
    source_count = len(entity.sources or [])
    factors['source_count'] = min(0.9, 0.5 + (source_count * 0.1))
    
    # Weighted average
    weights = {
        'chrystallum': 0.3,
        'wikidata': 0.25,
        'marc': 0.2,
        'consistency': 0.15,
        'source_count': 0.1
    }
    
    integrated_confidence = sum(
        factors[key] * weights[key] 
        for key in factors
    )
    
    return integrated_confidence
```

**Reasoning Rules:**
- ✅ **All standards agree** = High confidence
- ⚠️ **Some disagreement** = Medium confidence (weighted)
- ❌ **Major conflicts** = Low confidence (flag for review)

---

### 5. **Causal Chain Reasoning**

#### Problem

**Inferring Causality from Integrated Data:**
```
Event A: backbone_lcc = 'DG241-269', start_date = '-0049-01-10'
Event B: backbone_lcc = 'DG241-269', start_date = '-0049-03-15'
Relationship: A -[:CAUSED]-> B

But is this causal or just temporal sequence?
Can we infer causality from action structures?
```

#### Reasoning Model

**Causal Reasoning:**

```cypher
// Rule: Events with compatible action structures + temporal sequence = likely causal
MATCH (a:Event)-[r:CAUSED]->(b:Event)
WHERE a.start_date IS NOT NULL
  AND b.start_date IS NOT NULL
  AND a.start_date < b.start_date
WITH a, b, r,
  CASE
    // Strong causal: Action type matches result type
    WHEN a.action_type = 'MIL_ACT' 
      AND b.result_type = 'POL_TRANS'
      AND b.start_date - a.start_date < INTERVAL({days: 90})
      THEN 'strong_causal'
    
    // Medium causal: Compatible action/result types
    WHEN action_types_compatible(a.action_type, b.result_type)
      AND b.start_date - a.start_date < INTERVAL({days: 365})
      THEN 'medium_causal'
    
    // Weak causal: Temporal sequence only
    WHEN b.start_date - a.start_date < INTERVAL({days: 365})
      THEN 'weak_causal'
    
    ELSE 'uncertain'
  END AS causal_strength
SET r.causal_strength = causal_strength,
    r.inferred_causality = (causal_strength <> 'uncertain')
```

**Reasoning Rules:**
- ✅ **Action type → Result type match** = Strong causal
- ✅ **Temporal proximity + compatible types** = Medium causal
- ⚠️ **Temporal sequence only** = Weak causal
- ❌ **No temporal relationship** = Uncertain

---

### 6. **Gap Detection Reasoning**

#### Problem

**Missing Data Across Standards:**
```
Entity has:
  - Wikidata QID: Q1048 ✅
  - FAST ID: ❌ Missing
  - VIAF ID: ❌ Missing
  - MARC ID: ❌ Missing

Should we infer these? Can we find them?
```

#### Reasoning Model

**Gap Detection and Inference:**

```cypher
// Rule: If entity has Wikidata QID but missing other standards, try to find them
MATCH (e:Human)
WHERE e.qid IS NOT NULL
  AND (e.backbone_fast IS NULL 
    OR e.viaf_id IS NULL 
    OR e.backbone_marc IS NULL)
WITH e
CALL apoc.load.json('https://www.wikidata.org/wiki/Special:EntityData/' + e.qid + '.json')
YIELD value
WITH e, value.entities[e.qid] AS wikidata_data
// Extract identifiers from Wikidata claims
WITH e, 
  extract_ids_from_wikidata(wikidata_data) AS extracted_ids
SET e.suggested_backbone_fast = extracted_ids.fast_id,
    e.suggested_viaf_id = extracted_ids.viaf_id,
    e.suggested_backbone_marc = extracted_ids.marc_id,
    e.gap_filled_by = 'wikidata_inference',
    e.gap_fill_confidence = calculate_fill_confidence(extracted_ids)
```

**Reasoning Rules:**
- ✅ **Wikidata has FAST/VIAF/MARC links** = High confidence fill
- ✅ **Wikidata has name + dates** = Medium confidence (fuzzy match)
- ❌ **No Wikidata links** = Cannot infer

---

## Integrated Reasoning Architecture

### Layer 1: Data Integration (Current)

```
Entity {
  // Disparate data integrated
  backbone_fast: '...',
  qid: '...',
  viaf_id: '...',
  start_date: '...'
}
```

### Layer 2: Reasoning Engine (Proposed)

```
Entity {
  // Integrated data
  ...
  
  // Reasoning results
  integrated_confidence: 0.87,
  consistency_status: 'consistent',
  inferred_properties: {...},
  reasoning_flags: [...]
}
```

### Layer 3: Inference Results

```
// New inferred relationships
(entity1)-[:INFERRED_CONTEMPORARY_OF {
  confidence: 0.85,
  reasoning: 'Same period + overlapping dates'
}]->(entity2)

// New inferred properties
(entity)-[:INFERRED_FROM]->(source_entity)
```

---

## Reasoning Model Components

### 1. **Consistency Checker**

**Purpose:** Validate data consistency across standards

**Inputs:**
- Entity with multiple standard properties
- Validation rules

**Outputs:**
- Consistency score (0.0-1.0)
- Conflict flags
- Suggested resolutions

**Implementation:**
```python
class ConsistencyChecker:
    def check_temporal_consistency(self, entity):
        """Check if dates from different standards are consistent."""
        dates = {
            'chrystallum': entity.start_date,
            'wikidata': entity.wikidata_birth_date,
            'marc': entity.marc_birth_date
        }
        return self.validate_date_consistency(dates)
    
    def check_entity_resolution(self, entity):
        """Check if identifiers resolve to same entity."""
        identifiers = {
            'viaf': entity.viaf_id,
            'wikidata': entity.qid,
            'marc': entity.backbone_marc
        }
        return self.validate_entity_resolution(identifiers)
```

---

### 2. **Inference Engine**

**Purpose:** Infer new knowledge from integrated data

**Types of Inferences:**
- **Temporal**: Contemporaneity, sequences
- **Spatial**: Co-location, geographic relationships
- **Causal**: Action → Result patterns
- **Subject**: Same topic/subject relationships
- **Gap filling**: Missing identifier inference

**Implementation:**
```python
class InferenceEngine:
    def infer_contemporaries(self, entity):
        """Find contemporaries based on dates and period classification."""
        period = entity.backbone_lcc
        date_range = (entity.start_date, entity.end_date)
        return self.find_overlapping_entities(period, date_range)
    
    def infer_causal_chains(self, event):
        """Infer causal relationships from action structures."""
        if event.action_type == 'MIL_ACT':
            # Find events with compatible result types
            potential_effects = self.find_events_with_result_type('POL_TRANS')
            return self.score_causal_relationships(event, potential_effects)
```

---

### 3. **Confidence Aggregator**

**Purpose:** Aggregate confidence across standards

**Inputs:**
- Confidence scores from multiple standards
- Consistency scores
- Source counts

**Outputs:**
- Integrated confidence score
- Confidence breakdown by source
- Uncertainty flags

---

### 4. **Conflict Resolver**

**Purpose:** Resolve conflicts across standards

**Strategies:**
- **Majority vote**: Most standards agree
- **Authority-based**: Weight by source authority
- **Temporal weighting**: More recent sources
- **Expert review**: Flag for human review

---

## CRMinf Integration

### Use CRMinf for Explicit Reasoning Chains

**When to Use:**
- Complex reasoning chains
- Multiple competing beliefs
- Transparent inference documentation

**Structure:**
```cypher
// Evidence (from integrated standards)
(viaf_data:Document {source: 'VIAF'})
(wikidata_data:Document {source: 'Wikidata'})

// Inference process
(inference:InferenceMaking {
  label: 'Entity resolution inference',
  reasoning: 'VIAF and Wikidata match on name and dates'
})

// Belief (conclusion)
(belief:Belief {
  label: 'Belief that entities are same',
  certainty: 'high'
})

// The resolved entity
(entity:Human {
  viaf_id: '78287861',
  qid: 'Q1048'
})

// Reasoning chain
(viaf_data) -[:I1_INFERRED_FROM]-> (inference)
(wikidata_data) -[:I1_INFERRED_FROM]-> (inference)
(inference) -[:I2_BELIEVED_TO_HOLD]-> (belief)
(belief) -[:I2_BELIEVED_TO_HOLD]-> (entity)
```

---

## Recommended Reasoning Model

### Hybrid Approach: Chrystallum + CRMinf

**Simple Cases (Chrystallum):**
```cypher
// Direct confidence aggregation
(entity:Human {
  confidence: 0.87,
  consistency_status: 'consistent',
  inferred_contemporaries: [...]
})
```

**Complex Cases (CRMinf):**
```cypher
// Explicit reasoning chains
(inference)-[:I2_BELIEVED_TO_HOLD]->(belief)-[:I2_BELIEVED_TO_HOLD]->(entity)
```

---

## Implementation Priority

### Phase 1: Consistency Reasoning (High Priority)

1. **Temporal consistency checker**
   - Validate dates across standards
   - Flag conflicts

2. **Entity resolution validator**
   - Check if identifiers resolve to same entity
   - Flag mismatches

### Phase 2: Inference Engine (Medium Priority)

3. **Temporal inference**
   - Find contemporaries
   - Infer sequences

4. **Causal inference**
   - Infer causal relationships
   - Score causal strength

### Phase 3: Gap Filling (Lower Priority)

5. **Identifier inference**
   - Fill missing FAST/VIAF/MARC from Wikidata
   - Suggest matches

6. **Property inference**
   - Infer missing properties from related entities

---

## Summary

### Why Reasoning Is Needed

**Chrystallum's Structure:**
- ✅ Vertices with disparate integrated data
- ✅ Multiple standards per entity
- ⚠️ No explicit reasoning model

**Problems Without Reasoning:**
- ❌ No way to detect conflicts
- ❌ No way to validate consistency
- ❌ No way to infer new knowledge
- ❌ No way to resolve entities

### Recommended Reasoning Model

**Components:**
1. ✅ **Consistency Checker** - Validate across standards
2. ✅ **Inference Engine** - Infer from integrated data
3. ✅ **Confidence Aggregator** - Combine confidence scores
4. ✅ **Conflict Resolver** - Resolve standard conflicts
5. ✅ **CRMinf Integration** - Explicit reasoning chains for complex cases

**Value:**
- ✅ Detects data quality issues
- ✅ Infers new knowledge from integrated data
- ✅ Validates entity resolution
- ✅ Provides confidence scores
- ✅ Makes sense of disparate integrated data

**Bottom Line:** Yes, a reasoning model is **essential** for making sense of Chrystallum's integrated structure. Without it, the disparate data remains disconnected. With it, the integrated structure becomes **intelligible and valuable**.





