# Entity Type Classification Decision Tree

**Date:** February 22, 2026  
**Status:** Canonical Algorithm  
**Source:** Advisor guidance + Wikidata ontology patterns  
**Purpose:** Complete decision tree for classifying entities into 9 canonical types

---

## The Complete Algorithm

### **Tier 1: Primary Signal (P31 + P279* Pattern)**

**This is the canonical Wikidata classification pattern.**

```sparql
?entity wdt:P31/wdt:P279* ?class

Translation: 
  Follow P31 once, then P279 zero or more times
  Lands you at root ontological category
```

**Examples:**
```
Julius Caesar (Q1048)
  → P31 → Q5 (human)
  Classification: PERSON

Roman Republic (Q17167)
  → P31 → Q3024240 (historical country)
    → P279 → Q6256 (country)
      → P279 → Q43229 (organization)
  Classification: ORGANIZATION (with TemporalAnchor flag)

Battle of Alesia (Q125258)
  → P31 → Q178561 (battle)
    → P279 → Q180684 (conflict)  
      → P279 → Q1656682 (event)
  Classification: EVENT
```

**Decision Rules:**

```python
def classify_from_p31_p279(qid: str) -> str:
    """Primary classification using P31/P279* traversal"""
    
    # Get P31 direct
    p31_values = get_p31(qid)
    
    if not p31_values:
        # No P31 → check P279 (it's a class node)
        return classify_from_p279(qid)
    
    # Check each P31 value
    for p31_qid in p31_values:
        # Fast-path: Direct matches
        if p31_qid == 'Q5':
            return 'PERSON'
        elif p31_qid == 'Q515' or p31_qid == 'Q486972':  # city, settlement
            return 'PLACE'
        elif p31_qid == 'Q11514315':  # historical period
            return 'PERIOD'
        elif p31_qid == 'Q43229':  # organization
            return 'ORGANIZATION'
        elif p31_qid == 'Q1656682':  # event
            return 'EVENT'
        
        # Mid-level class → traverse P279*
        root_class = traverse_p279_to_root(p31_qid)
        
        if root_class in ['Q5']:
            return 'PERSON'
        elif root_class in ['Q17334', 'Q618123']:  # location, geo object
            return 'PLACE'
        elif root_class in ['Q1656682']:
            return 'EVENT'
        elif root_class in ['Q43229', 'Q15911314']:  # organization, institution
            return 'ORGANIZATION'
        elif root_class in ['Q386724', 'Q47461344']:  # work, written work
            return 'WORK'
        elif root_class in ['Q214609']:  # material
            return 'MATERIAL'
        elif root_class in ['Q488383']:  # object
            return 'OBJECT'
    
    # No match → go to Tier 2
    return None
```

---

### **Tier 2: Fast-Path Shortcuts (Property Presence)**

**Before expensive P279* traversal, check for fast signals:**

```python
def check_fast_path(qid: str) -> str | None:
    """Fast classification from presence of specific properties"""
    
    properties = get_property_list(qid)  # Just PIDs, not values
    
    # Human indicators
    if 'P21' in properties:  # sex or gender
        return 'PERSON'
    elif 'P106' in properties:  # occupation
        return 'PERSON'
    elif 'P569' in properties or 'P570' in properties:  # birth/death
        return 'PERSON'
    
    # Place indicators
    elif 'P625' in properties:  # coordinates
        return 'PLACE'
    elif 'P131' in properties and 'P17' in properties:  # located in + country
        return 'PLACE'
    
    # Organization indicators
    elif 'P571' in properties or 'P576' in properties:  # inception/dissolved
        return 'ORGANIZATION'
    
    # Work indicators
    elif 'P50' in properties or 'P57' in properties:  # author/director
        return 'WORK'
    
    # Event indicators (via qualifiers)
    # Check if entity appears as SUBJECT with temporal qualifiers
    elif has_temporal_qualifiers(qid):  # P580, P582, P585
        return 'EVENT'
    
    return None  # No fast path → do full P31/P279* traversal
```

---

### **Tier 3: Property Signature Classifier (Fallback)**

**For entities with NO P31 and NO P279:**

```python
PROPERTY_SIGNATURES = {
    'PERSON': {'P569', 'P570', 'P21', 'P106', 'P27', 'P19', 'P20'},
    'PLACE': {'P625', 'P17', 'P131', 'P47', 'P36', 'P1376'},
    'ORGANIZATION': {'P571', 'P576', 'P856', 'P159', 'P112', 'P1454'},
    'EVENT': {'P580', 'P582', 'P585', 'P276', 'P710', 'P793'},
    'WORK': {'P50', 'P577', 'P495', 'P123', 'P407', 'P921'},
    'MATERIAL': {'P186', 'P2079', 'P1056'},
    'OBJECT': {'P186', 'P127', 'P195', 'P276'}
}

def classify_from_signature(qid: str) -> tuple[str, float]:
    """
    Classify based on property presence pattern.
    
    Returns: (entity_type, confidence)
    """
    properties = set(get_property_list(qid))
    
    scores = {}
    for entity_type, signature in PROPERTY_SIGNATURES.items():
        # How many signature properties present?
        overlap = len(properties & signature)
        total_signature = len(signature)
        
        scores[entity_type] = overlap / total_signature if total_signature > 0 else 0
    
    # Best match
    best_type = max(scores, key=scores.get)
    confidence = scores[best_type]
    
    if confidence < 0.3:
        # Too ambiguous
        return 'CONCEPT', 0.5  # Fallback to CONCEPT with low confidence
    
    return best_type, confidence
```

**Flag as low-confidence:** Signature-based classification is inference, not direct reading

---

### **Special Cases**

**Deities (No P31 to Q5):**
```python
# Jupiter: P31 → Q22989102 (deity) → P279* → Q4271324 (mythical character)
# Doesn't reach Q5 (human)

if chains_to('Q22989102') or chains_to('Q4271324'):
    return 'PERSON', {'mythological': True, 'confidence': 0.9}
```

**Wikimedia Metadata:**
```python
# Categories, templates, lists
if p31_value in ['Q4167836', 'Q15184295', 'Q13406463']:
    return 'METADATA', {'wikimedia_artifact': True}
    # Flag for exclusion from domain graph
```

**Abstract Concepts (Rehabilitated CONCEPT):**
```python
if p31_value == 'Q17736':  # concept
    return 'CONCEPT', {'abstract': True, 'confidence': 1.0}
```

---

## Complete Decision Flow

```
┌─ Start: Classify QID ──────────────────────────────┐
│                                                     │
│ 1. Check Fast Path (P21, P106, P569, P625, etc.)  │
│    └─ Match → Return type immediately              │
│                                                     │
│ 2. Get P31 values                                  │
│    └─ None? → Check P279 (class node)             │
│                                                     │
│ 3. For each P31 value:                            │
│    ├─ Direct match? (Q5, Q515, Q11514315)        │
│    │  └─ Return type                               │
│    │                                                │
│    └─ Mid-level class? → Traverse P279*           │
│       └─ Match root category → Return type        │
│                                                     │
│ 4. No match from P31/P279? → Property Signature   │
│    └─ Count signature overlap                      │
│       └─ Return best match (with low confidence)  │
│                                                     │
│ 5. Still no match? → Default                      │
│    └─ Return 'CONCEPT' (low confidence)           │
│       └─ Flag for manual review                    │
└─────────────────────────────────────────────────────┘
```

---

## Properties to Query (Minimal Set)

**For classification, query these properties:**

**Ontological (Primary):**
- P31 (instance of)
- P279 (subclass of)

**Fast-Path Indicators:**
- P21 (sex/gender) - human signal
- P106 (occupation) - human signal
- P569/P570 (birth/death) - human signal
- P625 (coordinates) - place signal
- P17/P131 (country/located in) - place signal
- P571/P576 (inception/dissolved) - organization signal
- P50/P57 (author/director) - work signal

**Temporal Signals:**
- P580/P582/P585 (start/end/point in time) - event/tenure signal

**Total: ~15 properties** needed for robust classification (not 3,777!)

---

## Implementation Strategy

**Phase 1: Use what we have (our graph)**
- P31/P279 edges already imported (:P31, :P279)
- Can traverse locally in Neo4j
- No additional Wikidata queries needed

**Phase 2: Backlink extraction enhancement**
- When querying backlinks, also get P31 + these 15 key properties
- Classify backlink sources locally
- Build type distribution

**Phase 3: Property signature fallback**
- For entities with no P31/P279 in our graph
- Check which of the 15 signal properties they have
- Classify based on signature overlap

---

## Validation

**High Confidence:**
- P31 direct match: 1.0
- P31 + P279* root match: 0.95
- Fast-path match: 0.9

**Medium Confidence:**
- Property signature (>50% overlap): 0.7
- Property signature (30-50% overlap): 0.5

**Low Confidence:**
- Property signature (<30% overlap): 0.3
- Default to CONCEPT: 0.2
- Flag for manual review

---

**Document Status:** ✅ Complete Classification Algorithm  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026  
**Purpose:** Canonical algorithm for entity type assignment from Wikidata
