# Property→Facet Mapping - Impact for Chrystallum

## What We're Building

**Automatic routing system** that maps any Wikidata property to Chrystallum facets based on property type classifications.

---

## The Chain

```
Wikidata Property (P39)
    ↓ P31 (instance of)
Property Type (Q18608871 - "property for items about people")
    ↓ Semantic matching
Chrystallum Facet (DEMOGRAPHIC, BIOGRAPHIC)
    ↓ Agent routing
Subject Facet Agent (SFA)
```

---

## Current Run

**Processing:** 500 properties from `CSV/wikiPvalues.csv`  
**Output:** `CSV/property_mappings/property_facet_mapping_20260222_HHMMSS.csv`  
**Time:** ~5-6 minutes  
**Progress:** Running in background...

---

## Expected Results

### Mapping Success Rate
- **High confidence (≥0.8):** 40-50% of properties
- **Partial match:** 20-30%
- **Unknown:** 20-40% (need more facet rules)

### Example Mappings

**Political Properties:**
- P39 (position held)
- P194 (legislative body)
- P102 (member of political party)

**Geographic Properties:**
- P625 (coordinate location)
- P17 (country)
- P131 (located in administrative entity)
- P276 (location)

**Biographic Properties:**
- P569 (date of birth)
- P570 (date of death)
- P19 (place of birth)
- P20 (place of death)

**Military Properties:**
- P607 (conflict)
- P241 (military branch)

---

## How This Powers Chrystallum

### 1. **Automatic Agent Routing**

When processing a Wikidata claim:
```python
# Get property
property_id = "P39"  # position held

# Lookup facet mapping
facet = get_facet_for_property("P39")  # -> "POLITICAL"

# Route to appropriate SFA
agent = get_agent(subject_id="Q17167", facet="POLITICAL")
agent.process_claim(property_id="P39", ...)
```

### 2. **Federation Scoring**

Properties get scores based on facet relevance:
```python
def score_property(property_id, facet_mapping):
    score = 0.5  # Base
    
    if facet_mapping['is_historical']:
        score += 0.3  # Ancient World properties
    
    if facet_mapping['is_authority_control']:
        score += 0.2  # Authority properties
    
    if facet_mapping['primary_facet'] in ['POLITICAL', 'MILITARY', 'RELIGIOUS']:
        score += 0.1  # Core historical facets
    
    return min(score, 1.0)
```

### 3. **Property Filtering**

```cypher
// Load property mappings to Neo4j
LOAD CSV WITH HEADERS FROM 'file:///property_facet_mapping.csv' AS row
CREATE (:PropertyMapping {
  property_id: row.property_id,
  property_label: row.property_label,
  primary_facet: row.primary_facet,
  is_historical: row.is_historical = 'True',
  confidence: toFloat(row.confidence)
})

// Query: Get all MILITARY-related properties
MATCH (pm:PropertyMapping)
WHERE pm.primary_facet = 'MILITARY'
   OR pm.all_facets CONTAINS 'MILITARY'
RETURN pm.property_id, pm.property_label

// Result: Properties to prioritize for military facet analysis
```

### 4. **Wikidata Property Prioritization**

When fetching from Wikidata, prioritize high-value properties:
```python
# Get property mapping
mapping = property_mappings[property_id]

if mapping['confidence'] >= 0.8:
    priority = 'HIGH'
elif mapping['is_historical'] or mapping['is_authority_control']:
    priority = 'MEDIUM'
else:
    priority = 'LOW'

# Fetch in priority order
```

---

## After Processing Completes

### Immediate Actions

1. **Review output CSV**
   - Check mapping quality
   - Identify gaps (properties marked UNKNOWN)

2. **Enhance facet rules**
   - Add more property type QIDs to `FACET_RULES`
   - Improve coverage from 50% to 70-80%

3. **Import to Neo4j**
   - Create PropertyMapping nodes
   - Link to property usage in graph

### Medium-term Use

4. **Update SCA workflow**
   - Use mappings for automatic facet assignment
   - Route properties to correct agents

5. **Federation dispatcher**
   - Filter properties by facet relevance
   - Prioritize historical properties

6. **Property catalog**
   - Document which properties map to which facets
   - Create property→facet lookup table

---

## Success Metrics

This mapping is successful if:
- ✅ 60%+ properties mapped to a facet (not UNKNOWN)
- ✅ Core properties (P31, P39, P580, P625, P17) mapped correctly
- ✅ Historical properties flagged (is_historical=True)
- ✅ Authority control properties identified
- ✅ Multi-facet properties captured (secondary_facets populated)

---

## Current Status

⏳ **PROCESSING:** 500 properties (~92/500 complete after 1 min)  
🎯 **ETA:** 4 more minutes  
📊 **Output:** CSV with property→facet mappings  
✅ **Ready for:** Neo4j import and agent routing

---

**Check back in 5 minutes for complete results!** ⏱️
