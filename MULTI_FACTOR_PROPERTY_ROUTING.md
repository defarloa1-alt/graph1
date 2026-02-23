# Multi-Factor Property Routing System

**Problem:** Property→Facet mapping can't be deterministic because the same property has different meanings in different contexts.

**Example:** P195 (collection) is used by countries, people, artworks, libraries - each needs different facet routing.

**Solution:** Multi-factor contextual routing based on 4 dimensions.

---

## The 4 Routing Factors

### **Factor 1: Property Type** (Base Classification)
```
What we just built: P195 → ["ARTISTIC", "INTELLECTUAL", "CULTURAL"]
(Multiple possible facets based on property type)
```

### **Factor 2: Entity Type** (Subject Context)
```
Human + P195 → BIOGRAPHIC (personal collection)
Artwork + P195 → ARTISTIC (museum collection)
Work + P195 → INTELLECTUAL (library collection)
Place + P195 → CULTURAL (cultural heritage)
```

### **Factor 3: Value Type** (Object Context)
```
P195 → Museum → ARTISTIC
P195 → Library → INTELLECTUAL
P195 → Archive → CULTURAL
P195 → Private Collection → BIOGRAPHIC
```

### **Factor 4: Subject Domain** (Temporal/Geographic Context)
```
P195 + SubjectConcept(Ancient World) → ARCHAEOLOGICAL
P195 + SubjectConcept(Modern Politics) → POLITICAL
P195 + SubjectConcept(Medieval Church) → RELIGIOUS
```

---

## Routing Formula

```python
def route_property_contextually(
    property_id: str,
    source_entity: dict,
    target_value: dict,
    subject_context: dict
) -> list[tuple[str, float]]:
    """
    Multi-factor property routing
    
    Args:
        property_id: "P195"
        source_entity: {type: "Human", qid: "Q1048", ...}
        target_value: {type: "Organization", qid: "Q...", value_type: "Museum"}
        subject_context: {qid: "Q17167", period: "Ancient", ...}
        
    Returns:
        [(facet, confidence), ...] sorted by confidence
    """
    
    facet_scores = defaultdict(float)
    
    # Factor 1: Property type base (from our mapping)
    base_mapping = PROPERTY_MAPPINGS.get(property_id, {})
    for facet in base_mapping.get('all_facets', []):
        facet_scores[facet] += 0.25
    
    # Factor 2: Source entity type
    entity_type = source_entity.get('type')
    if entity_type == 'Human':
        facet_scores['BIOGRAPHIC'] += 0.25
        facet_scores['DEMOGRAPHIC'] += 0.25
    elif entity_type == 'Event':
        facet_scores['MILITARY'] += 0.20
        facet_scores['POLITICAL'] += 0.20
    elif entity_type == 'Place':
        facet_scores['GEOGRAPHIC'] += 0.30
    
    # Factor 3: Target value type
    value_type = target_value.get('value_type', '').lower()
    if 'museum' in value_type:
        facet_scores['ARTISTIC'] += 0.30
        facet_scores['ARCHAEOLOGICAL'] += 0.20
    elif 'library' in value_type:
        facet_scores['INTELLECTUAL'] += 0.30
    elif 'archive' in value_type:
        facet_scores['CULTURAL'] += 0.25
    
    # Factor 4: Subject domain
    period = subject_context.get('period', '').lower()
    if 'ancient' in period:
        facet_scores['ARCHAEOLOGICAL'] += 0.20
        facet_scores['CULTURAL'] += 0.15
    elif 'medieval' in period:
        facet_scores['RELIGIOUS'] += 0.20
        facet_scores['CULTURAL'] += 0.15
    
    # Sort by score
    ranked = sorted(facet_scores.items(), key=lambda x: x[1], reverse=True)
    
    return ranked[:3]  # Top 3 facets
```

---

## Example: P195 Routing in Different Contexts

### Context 1: Julius Caesar's Personal Papers
```python
route_property_contextually(
    property_id="P195",
    source_entity={type: "Human", qid: "Q1048"},
    target_value={type: "Archive", value_type: "private_collection"},
    subject_context={qid: "Q17167", period: "Ancient"}
)
# Returns:
# [
#   ("BIOGRAPHIC", 0.65),   # Human + private collection
#   ("ARCHAEOLOGICAL", 0.45), # Ancient period
#   ("CULTURAL", 0.40)
# ]
```

### Context 2: Roman Museum Artifacts
```python
route_property_contextually(
    property_id="P195",
    source_entity={type: "Object", qid: "Q..."},
    target_value={type: "Organization", value_type: "museum"},
    subject_context={qid: "Q17167", period: "Ancient"}
)
# Returns:
# [
#   ("ARTISTIC", 0.55),        # Museum context
#   ("ARCHAEOLOGICAL", 0.45),   # Ancient + museum
#   ("CULTURAL", 0.40)
# ]
```

### Context 3: Medieval Church Records
```python
route_property_contextually(
    property_id="P195",
    source_entity={type: "Work", qid: "Q..."},
    target_value={type: "Organization", value_type: "library"},
    subject_context={qid: "Q...", period: "Medieval"}
)
# Returns:
# [
#   ("INTELLECTUAL", 0.55),  # Library + Work
#   ("RELIGIOUS", 0.45),     # Medieval church
#   ("CULTURAL", 0.40)
# ]
```

---

## Implementation Architecture

### Layer 1: Base Property Mapping (What We Just Built)
```
500 properties → Base facet associations
Use as: Starting point + filtering
```

### Layer 2: Entity Type Rules
```
Source entity type → Facet weights
Defined per entity type in schema
```

### Layer 3: Value Type Rules
```
Target value characteristics → Facet weights
Museums, libraries, archives, institutions
```

### Layer 4: Domain Context
```
SubjectConcept + Period + Geographic → Facet weights
Roman Republic + Ancient + Mediterranean → weights
```

### Combined Router
```
Aggregate all 4 layers → Top 3 facets with confidence scores
```

---

## Data Structures Needed

### 1. Property Base Mapping (We Have This!)
```json
{
  "P195": {
    "base_facets": ["ARTISTIC", "INTELLECTUAL", "CULTURAL"],
    "confidence": 0.5
  }
}
```

### 2. Entity Type → Facet Weights
```json
{
  "Human": {
    "BIOGRAPHIC": 0.30,
    "DEMOGRAPHIC": 0.25,
    "POLITICAL": 0.15
  },
  "Event": {
    "MILITARY": 0.25,
    "POLITICAL": 0.25,
    "DIPLOMATIC": 0.15
  }
}
```

### 3. Value Type → Facet Weights
```json
{
  "museum": {"ARTISTIC": 0.30, "ARCHAEOLOGICAL": 0.20},
  "library": {"INTELLECTUAL": 0.30},
  "archive": {"CULTURAL": 0.25, "INTELLECTUAL": 0.20}
}
```

### 4. Domain Context → Facet Boosts
```json
{
  "ancient": {"ARCHAEOLOGICAL": 0.20, "CULTURAL": 0.15},
  "medieval": {"RELIGIOUS": 0.20, "CULTURAL": 0.15},
  "military_context": {"MILITARY": 0.25}
}
```

---

## Next Steps to Build This

1. ✅ **Base property mapping** - DONE (500 properties)
2. ⏳ **Define entity type rules** - Create weight tables
3. ⏳ **Define value type rules** - Museum, library, archive patterns
4. ⏳ **Define domain context rules** - Period/geographic boosts
5. ⏳ **Implement scoring engine** - Combine all 4 factors
6. ⏳ **Test with real claims** - Validate routing quality

---

**Should we start designing the entity type rules next?** Or review the base mapping results first? 🎯
