# CIDOC-CRM Extensions Explained

## Overview

CIDOC-CRM extensions add specialized domain functionality to the core CIDOC-CRM model. They're official extensions maintained by the CIDOC community.

---

## Core CIDOC-CRM vs. Extensions

### Core CIDOC-CRM
- **Base ontology**: Event-centric model for cultural heritage
- **Scope**: General cultural heritage information
- **ISO Standard**: ISO 21127:2023

### Extensions
- **Specialized ontologies**: Domain-specific additions
- **Extend core**: Build on CIDOC-CRM classes/properties
- **Compatible**: Work with core CIDOC-CRM

---

## 1. CRMgeo (Geographic Extensions)

### What It Is

**CRMgeo** extends CIDOC-CRM with geographic and spatial modeling capabilities.

**Purpose:**
- Enhanced geographic data representation
- Coordinate systems and spatial geometries
- Geographic feature hierarchies
- Spatial relationships

### Key Classes

**E26_Physical_Feature** (from core, enhanced in CRMgeo)
- Geographic features (mountains, rivers, etc.)
- Can have geometric representations

**geo:SP5_Geometric_Place_Expression**
- Geometric representation of places
- Points, lines, polygons
- Coordinate systems

**geo:SP6_Declarative_Place**
- Declarative place descriptions
- "Near Rome", "In Italy"
- Text-based geographic references

### Key Properties

**geo:SP7_is_located_in**
- Spatial containment
- Place within another place

**geo:P89_falls_within**
- Geographic containment
- More precise than core CIDOC-CRM spatial properties

**geo:P121_overlaps_with**
- Geographic overlap
- Territories, regions that overlap

### Example

```cypher
// Core CIDOC-CRM
(rubicon: E53_Place {
  label: 'Rubicon River'
})

// CRMgeo extension
(rubiconGeometry: geo:SP5_Geometric_Place_Expression {
  geometry_type: 'LineString',
  coordinates: [[12.3833, 44.1675], [12.4000, 44.2000]]
})

(rubicon) -[:geo:SP7_is_located_in]-> (italia: E53_Place)
(rubicon) -[:geo:P121_has_geometric_representation]-> (rubiconGeometry)
```

### Relevance to Chrystallum

**Overlap with Chrystallum:**
- ✅ We already have geographic data (Pleiades, coordinates)
- ⚠️ CRMgeo adds geometric representations (points, lines, polygons)
- ⚠️ CRMgeo adds spatial relationship properties

**Should We Use CRMgeo?**
- **Maybe**: If we need geometric representations (river courses, boundaries)
- **Not Essential**: Our Pleiades/coordinate approach is sufficient for most use cases
- **Consider**: If we need complex spatial queries (overlaps, boundaries)

---

## 2. CRMinf (Inference and Reasoning Extensions)

### What It Is

**CRMinf** extends CIDOC-CRM with inference, reasoning, and belief modeling.

**Purpose:**
- Represent beliefs, inferences, conclusions
- Model reasoning chains
- Handle uncertainty and probability
- Track how knowledge was derived

### Key Classes

**crminf:E1_CRM_Entity** (extends core E1_CRM_Entity)
- Base class for inference entities

**crminf:E2_Belief**
- Beliefs or assumptions
- What someone believes to be true

**crminf:E5_Inference_Making**
- Process of making inferences
- Reasoning activities

**crminf:E13_Belief_Revision**
- Changes to beliefs
- Updates based on new evidence

### Key Properties

**crminf:I1_inferred_from**
- Knowledge inferred from evidence
- Reasoning chain

**crminf:I2_believed_to_hold**
- Belief about a fact
- Uncertainty representation

**crminf:I3_has_note**
- Notes about inference
- Reasoning explanations

### Example

```cypher
// Core CIDOC-CRM event
(crossing: E5_Event {
  label: 'Crossing of Rubicon'
})

// CRMinf: Belief about the event
(belief: crminf:E2_Belief {
  label: 'Belief that Caesar crossed Rubicon',
  confidence: 0.95
})

// CRMinf: Inference from sources
(inference: crminf:E5_Inference_Making {
  label: 'Inferred from Suetonius and Plutarch'
})

(belief) -[:crminf:I1_inferred_from]-> (inference)
(inference) -[:crminf:I2_believed_to_hold]-> (crossing)
```

### Relevance to Chrystallum

**Overlap with Chrystallum:**
- ✅ We have confidence scores and validation metadata
- ✅ We have source attribution
- ⚠️ CRMinf adds structured reasoning chains
- ⚠️ CRMinf adds belief modeling

**Should We Use CRMinf?**
- **Maybe**: If we need explicit reasoning chains
- **Not Essential**: Our confidence/source approach covers most needs
- **Consider**: If we need to model historical debates/disagreements

---

## 3. CRMsci (Scientific Observation Extensions)

### What It Is

**CRMsci** extends CIDOC-CRM for scientific observation, measurement, and research data.

**Purpose:**
- Scientific observations and measurements
- Research methodologies
- Data collection processes
- Analysis and interpretation

### Key Classes

**crm-sci:S4_Observation**
- Scientific observations
- Data collection events

**crm-sci:S5_Inference**
- Scientific inferences
- Conclusions from observations

**crm-sci:S6_Data_Evaluation**
- Evaluation of data quality
- Validation processes

**crm-sci:S15_Observable_Entity**
- Entities that can be observed
- Measurable phenomena

### Key Properties

**crm-sci:O1_observed_dimension**
- Dimensions observed
- What was measured

**crm-sci:O2_observed_value**
- Observed values
- Measurement results

**crm-sci:O3_has_observed_property**
- Properties observed
- Characteristics measured

### Example

```cypher
// Archaeological observation
(excavation: E7_Activity {
  label: 'Excavation of Rubicon crossing site'
})

// CRMsci: Observation
(observation: crm-sci:S4_Observation {
  label: 'Observation of artifact dating',
  method: 'Radiocarbon dating'
})

// CRMsci: Observed value
(observation) -[:crm-sci:O2_observed_value]->
(value: crm-sci:S15_Observable_Entity {
  value: '49 BCE +/- 2 years',
  dimension: 'Temporal'
})

(observation) -[:P11_had_participant]-> (archaeologist: E21_Person)
(excavation) -[:P10i_contains]-> (observation)
```

### Relevance to Chrystallum

**Overlap with Chrystallum:**
- ⚠️ Less relevant for historical narrative focus
- ✅ Could be useful for archaeological data
- ✅ Could model scientific dating methods

**Should We Use CRMsci?**
- **Maybe**: If we integrate archaeological data
- **Not Essential**: For historical narrative knowledge graphs
- **Consider**: If we need to model dating methods, archaeological evidence

---

## Other CIDOC-CRM Extensions

### CRMarchaeo (Archaeological Extensions)

**Purpose:**
- Archaeological excavation modeling
- Stratigraphy and context
- Find registration

**Relevance:**
- ⚠️ Specialized for archaeology
- ⚠️ Less relevant for historical narrative focus

### CRMtex (Text Extensions)

**Purpose:**
- Textual analysis
- Manuscript relationships
- Textual variants

**Relevance:**
- ⚠️ Could be useful for historical sources
- ⚠️ May overlap with our Work entity type

---

## Should Chrystallum Use These Extensions?

### Decision Matrix

| Extension | Core Function | Chrystallum Need | Recommendation |
|-----------|---------------|------------------|----------------|
| **CRMgeo** | Geographic geometry | Basic (we have Pleiades/coords) | ⚠️ **Optional** - Use if complex geometries needed |
| **CRMinf** | Inference/reasoning | We have confidence/sources | ⚠️ **Optional** - Use if explicit reasoning chains needed |
| **CRMsci** | Scientific observation | Minimal (historical focus) | ❌ **Not Needed** - Too specialized |
| **CRMarchaeo** | Archaeology | Minimal (historical focus) | ❌ **Not Needed** - Too specialized |
| **CRMtex** | Textual analysis | Maybe for sources | ⚠️ **Maybe** - If deep textual analysis needed |

---

## Recommended Approach

### Phase 1: Core CIDOC-CRM Only

**Use:**
- Core CIDOC-CRM classes/properties
- Chrystallum extensions (FAST, action structure, ISO 8601)

**Skip:**
- Specialized extensions (CRMsci, CRMarchaeo)
- Complex extensions (CRMgeo, CRMinf) - for now

### Phase 2: Evaluate Extensions As Needed

**Consider CRMgeo if:**
- Need geometric representations (river courses, boundaries)
- Complex spatial queries required
- Museum/archival integration needs it

**Consider CRMinf if:**
- Need explicit reasoning chains
- Modeling historical debates/disagreements
- Complex uncertainty representation

**Consider CRMtex if:**
- Deep textual analysis of sources
- Manuscript variant tracking
- Textual relationship modeling

---

## Implementation Strategy

### Minimal Approach (Recommended Start)

```cypher
// Core CIDOC-CRM only
(event: E5_Event {
  cidoc_crm_class: 'E5_Event',
  cidoc_crm_version: '8.0',
  
  // Chrystallum extensions
  backbone_fast: 'fst01411640',
  start_date: '-0049-01-10',
  action_type: 'MIL_ACT'
})
```

### Extension Approach (If Needed)

```cypher
// Core CIDOC-CRM
(event: E5_Event {...})

// CRMgeo extension (if needed)
(place: E53_Place) -[:geo:SP7_is_located_in]-> (region: E53_Place)

// CRMinf extension (if needed)
(belief: crminf:E2_Belief) -[:crminf:I2_believed_to_hold]-> (event)
```

---

## Summary

### CRMgeo (Geographic)
- **Purpose**: Geographic geometry and spatial relationships
- **Chrystallum Need**: Low (we have Pleiades/coordinates)
- **Recommendation**: Optional - use if complex geometries needed

### CRMinf (Inference)
- **Purpose**: Reasoning chains and belief modeling
- **Chrystallum Need**: Medium (we have confidence/sources)
- **Recommendation**: Optional - use if explicit reasoning needed

### CRMsci (Scientific)
- **Purpose**: Scientific observations and measurements
- **Chrystallum Need**: Low (historical narrative focus)
- **Recommendation**: Not needed - too specialized

### Bottom Line

**Start with Core CIDOC-CRM + Chrystallum extensions.**

**Add specialized extensions only if specific needs arise:**
- CRMgeo: Complex geographic queries
- CRMinf: Explicit reasoning chains
- CRMsci/CRMarchaeo: Archaeological/scientific data

**Our unique features (FAST, action structure, ISO 8601) are more valuable than these extensions for historical knowledge graphs.**



