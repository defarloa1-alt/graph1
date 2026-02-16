# Property Pattern Mining - Integration Guide

**Experimental Feature:** Empirical property usage patterns from Wikidata  
**Date:** February 15, 2026  
**Status:** Proof-of-concept complete, integration pending

---

## Overview

The property pattern miner discovers which properties are commonly used together for different entity types by analyzing real Wikidata data. This creates **type signatures** that can inform validation, agent hinting, and quality checking.

## What Was Built

**Script:** [Python/wikidata_property_pattern_miner.py](Python/wikidata_property_pattern_miner.py)

**Capabilities:**
- Fetches entities from Wikidata API
- Groups entities by P31 (instance of) type
- Calculates property coverage per type
- Classifies properties as mandatory (≥90%), common (50-90%), or optional (<50%)
- Exports JSON signatures + CSV statistics

## Experimental Results

**Test Run:** 30 diverse QIDs (humans, countries, cities, concepts, etc.)

**Key Findings:**

### 1. Human (Q5) - 4 samples
**Mandatory properties (100% coverage):**
- P31 (instance of)
- P21 (sex or gender)
- P106 (occupation)
- P569 (date of birth)
- P800 (notable work)

**Common properties (75% coverage):**
- P570 (date of death)
- P20 (place of death)
- P119 (place of burial)
- P509 (cause of death)

**Insight:** Every human should have basic biographical info. Missing P21 or P569 indicates incomplete data.

### 2. Country (Q6256) - 6 samples
**Mandatory properties (100% coverage):**
- P2924 (Great Russian Encyclopedia ID)
- P227 (GND ID)
- P1792 (category of associated people)
- P1333 (contains statistical region)
- P3221 (New York Times topic ID)

**Common properties (83% coverage):**
- P1344 (participant in)
- P950 (Biblioteca Nacional de España ID)
- P2004 (Freebase ID)

**Insight:** Countries have extensive external ID properties. High coverage on authority control IDs.

### 3. Geographic Entities
Multiple geographic types discovered:
- Q200250 (4 samples) - 100% coverage on P610 (highest point), P47 (shares border with)
- Q3624078 (5 samples) - 100% coverage on P1705 (native label), P1622 (driving side)

**Insight:** Geographic entities have strong structural consistency for spatial relationships.

---

## Integration with Step 3 (Federation Discovery)

### Current State (Step 3)
Agents can bootstrap from Wikidata and auto-generate claims, but they don't know:
- What properties to *expect* for a given entity type
- When an entity is *incomplete* or missing mandatory properties
- Which properties are *indicative* of entity type

### Proposed Enhancement

**Add type signature validation to federation discovery:**

```python
# In facet_agent_framework.py

def validate_entity_completeness(self, qid: str, entity_type: str) -> Dict:
    """
    Check if entity has expected properties for its type
    Uses empirically-derived property signatures
    """
    # Load property signatures (from mined patterns)
    signatures = self._load_property_signatures()
    
    if entity_type not in signatures:
        return {'status': 'unknown_type', 'confidence': 0.5}
    
    # Fetch entity
    entity = self.fetch_wikidata_entity(qid)
    entity_props = set(entity['claims'].keys())
    
    # Check coverage
    type_sig = signatures[entity_type]
    mandatory_props = set(type_sig['mandatory']['properties'])
    common_props = set(type_sig['common']['properties'])
    
    missing_mandatory = mandatory_props - entity_props
    missing_common = common_props - entity_props
    
    # Calculate completeness score
    mandatory_coverage = len(mandatory_props & entity_props) / len(mandatory_props)
    common_coverage = len(common_props & entity_props) / len(common_props)
    
    completeness_score = (mandatory_coverage * 0.7) + (common_coverage * 0.3)
    
    return {
        'status': 'validated',
        'completeness_score': completeness_score,
        'missing_mandatory': list(missing_mandatory),
        'missing_common': list(missing_common),
        'recommendation': 'bootstrap' if completeness_score >= 0.8 else 'manual_review'
    }
```

### Use Cases

**1. Bootstrap Quality Gating**
```python
# Before bootstrapping, check if entity is well-formed
validation = agent.validate_entity_completeness('Q17167', 'Q6256')

if validation['completeness_score'] < 0.7:
    print(f"⚠ Low completeness: {validation['completeness_score']:.1%}")
    print(f"Missing mandatory: {validation['missing_mandatory']}")
    # Decision: skip bootstrap or flag for manual review

else:
    # Proceed with bootstrap
    result = agent.bootstrap_from_qid('Q17167')
```

**2. Claim Prioritization**
```python
# When discovering hierarchy, prioritize mandatory properties
hierarchy = agent.discover_hierarchy_from_entity('Q17167', depth=2)

# Load type signatures
signatures = agent._load_property_signatures()
mandatory_props = signatures.get('Q6256', {}).get('mandatory', {}).get('properties', [])

# Focus claims on mandatory properties first
priority_claims = []
optional_claims = []

for claim in hierarchy['discovered_relationships']:
    if claim['property'] in mandatory_props:
        priority_claims.append(claim)
    else:
        optional_claims.append(claim)

# Submit priority claims first
for claim in priority_claims:
    agent.pipeline.ingest_claim(claim)
```

**3. Entity Type Inference**
```python
# Given a QID, infer likely type from property signature
def infer_entity_type(self, qid: str) -> List[Dict]:
    """
    Infer entity type by matching property set to known signatures
    Returns ranked list of candidate types
    """
    entity = self.fetch_wikidata_entity(qid)
    entity_props = set(entity['claims'].keys())
    
    signatures = self._load_property_signatures()
    
    # Score each type by property overlap
    type_scores = []
    for type_qid, sig in signatures.items():
        mandatory = set(sig['mandatory']['properties'])
        common = set(sig['common']['properties'])
        
        # Jaccard similarity
        intersection = len(entity_props & (mandatory | common))
        union = len(entity_props | mandatory | common)
        similarity = intersection / union if union > 0 else 0
        
        type_scores.append({
            'type_qid': type_qid,
            'type_label': sig['type_label'],
            'similarity': similarity,
            'mandatory_coverage': len(entity_props & mandatory) / len(mandatory)
        })
    
    # Return top 5 candidates
    return sorted(type_scores, key=lambda x: x['similarity'], reverse=True)[:5]
```

**4. Quality Metrics Dashboard**
```python
# Track entity quality across bootstrap sessions
def audit_bootstrap_quality(self) -> Dict:
    """
    After bootstrap session, audit quality of discovered entities
    """
    context = self.get_session_context()
    nodes = context['subgraph_sample']['nodes']
    
    quality_report = {
        'total_nodes': len(nodes),
        'with_wikidata': sum(1 for n in nodes if n.get('wikidata_qid')),
        'completeness_scores': [],
        'missing_critical_properties': []
    }
    
    for node in nodes:
        if qid := node.get('wikidata_qid'):
            # Extract type from node (assume stored during bootstrap)
            entity_type = node.get('entity_type')
            
            if entity_type:
                validation = self.validate_entity_completeness(qid, entity_type)
                quality_report['completeness_scores'].append(validation['completeness_score'])
                
                if validation['missing_mandatory']:
                    quality_report['missing_critical_properties'].append({
                        'node': node['label'],
                        'qid': qid,
                        'missing': validation['missing_mandatory']
                    })
    
    # Statistics
    if quality_report['completeness_scores']:
        quality_report['avg_completeness'] = sum(quality_report['completeness_scores']) / len(quality_report['completeness_scores'])
    
    return quality_report
```

---

## Next Steps

### Phase 1: Expand Pattern Mining (Now)
- [x] Create proof-of-concept miner
- [ ] Mine larger samples per type (100+ items per major type)
- [ ] Focus on historical domain types:
  - Q178561 (battle)
  - Q190401 (military unit)
  - Q620634 (military operation)
  - Q1907114 (military conflict)
  - Q82794 (geographic region)
  - Q15642541 (human biblical figure)

### Phase 2: Integration (Step 3.5?)
- [ ] Add `validate_entity_completeness()` to FacetAgent
- [ ] Add `infer_entity_type()` for type inference
- [ ] Load property signatures from JSON file
- [ ] Update bootstrap workflow to use validation
- [ ] Add completeness scoring to claim generation

### Phase 3: Constraints & Shapes (Step 4+?)
- [ ] Generate Neo4j SHACL-style shapes from patterns
- [ ] Implement property-level validation rules
- [ ] Add cardinality constraints (1-to-1 vs 1-to-many)
- [ ] Create validation agent for claim quality checking

### Phase 4: Continuous Learning
- [ ] Periodic re-mining to update patterns
- [ ] Domain-specific pattern extraction (military, political, etc.)
- [ ] Facet-specific property signatures
- [ ] Collaborative filtering for property recommendations

---

## Files Created

1. **Python/wikidata_property_pattern_miner.py** - Mining script
2. **property_patterns_experiment_20260215_173552.json** - Sample results (30 QIDs, 87 types)
3. **property_patterns_experiment_20260215_173552.csv** - Statistics table
4. **PROPERTY_PATTERN_MINING_INTEGRATION.md** - This file

---

## Value Proposition

**Without property patterns:**
- Agents bootstrap blindly from Wikidata
- No way to assess entity quality
- No prioritization of mandatory vs optional properties
- No type inference from property sets

**With property patterns:**
- ✅ Quality gating before bootstrap (completeness scores)
- ✅ Intelligent claim prioritization (mandatory first)
- ✅ Entity type inference from property signatures
- ✅ Validation constraints derived from empirical data
- ✅ Quality metrics dashboard for audit

**ROI:** High-value enhancement with minimal integration cost. Patterns are derived automatically from Wikidata and directly improve Step 3 federation discovery.

---

## Decision Point

**Question for user:** Should we integrate property pattern validation into Step 3, or defer to a later step (e.g., Step 4 on validation)?

**Option A:** Integrate now (Step 3.5)
- Pros: Immediate quality improvement, natural fit with federation discovery
- Cons: Adds complexity to Step 3

**Option B:** Defer to Step 4 (Validation & Quality)
- Pros: Keeps Step 3 focused, allows dedicated validation step
- Cons: Delayed value, agents bootstrap without quality checks

**Recommendation:** Start with minimal integration (completeness scoring in bootstrap) now, full validation in Step 4.
