# Cotton Node - Graph Schema Representation

## Cotton Entity in Chrystallum Knowledge Graph

Based on the India cotton trade text, here's how the **Cotton** node would appear in the Chrystallum graph schema.

---

## Node: Cotton

### Basic Properties

```cypher
CREATE (cotton:Product {
  id: 'Q11457',
  unique_id: 'Q11457_PRODUCT_COTTON',
  label: 'Cotton',
  type: 'Product',
  qid: 'Q11457',
  
  // Core properties
  description: 'Fiber used for textile production',
  material_type: 'Plant Fiber',
  
  // Temporal (if applicable)
  start_date: null,  // Cotton cultivation has ancient origins
  end_date: null,
  
  // Source attribution
  sources: [
    {
      source: 'Steven Johnson - Wonderland',
      source_type: 'tertiary',
      source_quality_tier: 3
    },
    {
      source: 'Strabo - Geography',
      source_type: 'primary',
      source_quality_tier: 1
    },
    {
      source: 'John Keay - India: A History',
      source_type: 'authoritative_secondary',
      source_quality_tier: 2
    }
  ],
  
  // Validation metadata
  confidence: 0.85,
  validation_status: 'verified',
  verification_status: 'cross_referenced',
  temporal_certainty: 'uncertain',
  consistency_status: 'fully_consistent',
  
  // Backbone alignment
  backbone_fast: '...',
  backbone_lcc: '...',
  backbone_lcsh: ['Cotton', 'Cotton trade']
})
```

---

## Relationships from Cotton Node

### 1. Geographic: ORIGINATED_IN

```cypher
(cotton)-[:ORIGINATED_IN {
  // Action Structure
  goal: 'Identify geographic origin of cotton cultivation',
  goal_type: 'ACAD',
  trigger: 'Archaeological and historical evidence',
  trigger_type: 'RESEARCH',
  action_type: 'LOCALIZE',
  action_description: 'Cotton originated in the Indian subcontinent',
  result: 'India established as origin point of cotton production',
  result_type: 'DISCOVERY',
  
  // Narrative
  narrative_summary: 'The link between cotton and the subcontinent is an ancient one. Archaeological excavations along the Indus River in modern day Pakistan uncovered cotton threads from 2300 BCE, making India one of the earliest known centers of cotton cultivation and processing.',
  
  // Properties
  temporal: '2300 BCE onwards',
  confidence: 0.90,
  validation_status: 'verified',
  sources: [
    {source: 'Archaeological evidence', source_type: 'primary', tier: 1},
    {source: 'Steven Johnson - Wonderland', source_type: 'tertiary', tier: 3}
  ]
}]->(india:Place {
  id: 'Q668',
  label: 'India',
  type: 'Country'
})
```

### 2. Geographic: LOCATED_IN (Indus Valley)

```cypher
(cotton)-[:LOCATED_IN {
  narrative_summary: 'Earliest archaeological evidence of cotton found in Indus Valley excavations, with cotton threads discovered in modern-day Pakistan dating to 2300 BCE.',
  temporal: '2300 BCE',
  confidence: 0.85,
  validation_status: 'flagged',  // Needs specific site citation
  flags: [
    {
      flag_type: 'single_source',
      flag_severity: 'minor',
      description: 'Needs specific archaeological site citation'
    }
  ]
}]->(indusValley:Place {
  id: 'C_INDUS_VALLEY',
  label: 'Indus Valley',
  type: 'Region'
})
```

### 3. Material: MATERIAL_USED_IN

```cypher
(cotton)-[:MATERIAL_USED_IN {
  // Action Structure
  goal: 'Create dyed cotton fabrics for trade',
  goal_type: 'ECON',
  trigger: 'Global demand for colorful textiles',
  trigger_type: 'MARKET',
  action_type: 'PROD',
  action_description: 'Cotton fiber used as base material for dyed cotton fabrics',
  result: 'Production of world\'s most sought-after textiles',
  result_type: 'PROD_OUTPUT',
  
  narrative_summary: 'Cotton served as the base material for India\'s famous dyed cotton fabrics, which became the world\'s most sought-after textile product. The quality of the cotton fiber, combined with innovative dyeing techniques, created fabrics that could retain vibrant colors after multiple washings.',
  
  confidence: 0.95,
  validation_status: 'verified'
}]->(dyedCottonFabric:Product {
  id: 'C_DYED_COTTON_FABRICS',
  label: 'Dyed Cotton Fabrics',
  type: 'Product'
})
```

### 4. Chemical/Process: NATURALLY_FIXES_TO (with Indigo)

```cypher
(cotton)-[:NATURALLY_FIXES_TO {
  // Action Structure
  goal: 'Understand dye bonding properties',
  goal_type: 'TECH',
  trigger: 'Need to dye cotton with vibrant colors',
  trigger_type: 'TECH_CONSTRAINT',
  action_type: 'CHEM_BOND',
  action_description: 'Indigo dye naturally bonds with cotton fiber without additional catalysts, unlike other vegetable dyes',
  result: 'Deep blue color achieved without mordant process',
  result_type: 'TECH_BREAKTHROUGH',
  
  narrative_summary: 'Only the deep blue of indigo, which takes its name from the Indus Valley where it was first employed as a dye, fixes itself to cotton without additional catalysts. The waxy cellulose of the cotton fibre naturally repels vegetable dyes, but indigo is unique in its ability to bond directly.',
  
  confidence: 0.80,
  validation_status: 'verified',
  flags: [
    {
      flag_type: 'ambiguous',
      flag_severity: 'minor',
      description: 'Chemical mechanism needs scientific verification'
    }
  ],
  verification_status: 'needs_scientific_verification'
}]->(indigo:Dye {
  id: 'Q19660',
  label: 'Indigo',
  type: 'Dye',
  qid: 'Q19660'
})
```

### 5. Process: REQUIRES (Mordant Process for Other Dyes)

```cypher
(cotton)-[:REQUIRES {
  // Action Structure
  goal: 'Enable cotton to accept vegetable dyes other than indigo',
  goal_type: 'TECH',
  trigger: 'Cotton naturally repels most vegetable dyes',
  trigger_type: 'TECH_CONSTRAINT',
  action_type: 'INNOV',
  action_description: 'Indian artisans developed mordant process involving sour milk, protein-heavy substances, and metallic salts to make cotton receptive to vibrant dyes',
  result: 'Cotton can display brilliant patterns in multiple colors that retain after washing',
  result_type: 'TECH_BREAKTHROUGH',
  
  narrative_summary: 'The process of transforming cotton into a fabric that can be dyed with shades other than indigo is known as mordanting the fiber. The waxy cellulose of the cotton fibre naturally repels vegetable dyes, requiring a complex process involving sour milk, goat urine, camel dung, blood, and metallic salts to create a mordant that permeates the core of the fiber.',
  
  confidence: 0.85,
  validation_status: 'verified',
  sources: [
    {source: 'Traditional dyeing techniques', source_type: 'primary', tier: 1}
  ]
}]->(mordantProcess:ChemicalProcess {
  id: 'C_MORDANT_PROCESS',
  label: 'Mordant Dyeing Process',
  type: 'Chemical Process'
})
```

### 6. Production: PRODUCED_BY

```cypher
(india:Place {id: 'Q668'})-[:PRODUCED {
  // Action Structure
  goal: 'Supply global demand for luxury textiles',
  goal_type: 'ECON',
  trigger: 'Natural abundance of cotton and developed dyeing technology',
  trigger_type: 'TECH',
  action_type: 'PROD',
  action_description: 'India produced copious quantities of cotton and dyed cotton fabrics using unique mordant process',
  result: '1000-year trade surplus, largest global GDP share, attracted imperial ambitions',
  result_type: 'ECON_GROWTH',
  
  narrative_summary: 'India had a copious supply of cotton and developed unique dyeing techniques. From 1 CE to 1500 CE, India\'s cotton textile production contributed to its dominance in global trade and the largest share of global GDP.',
  
  temporal: '1 CE - 1500 CE',
  confidence: 0.90,
  validation_status: 'verified'
}]->(cotton)
```

### 7. Archaeological: DISCOVERED_BY

```cypher
(archaeologicalExcavation:Event {
  id: 'C_ARCHAEOLOGICAL_DISCOVERY',
  label: 'Archaeological Excavation - Indus Valley',
  type: 'Archaeological Discovery'
})-[:DISCOVERED {
  // Action Structure
  goal: 'Understand ancient textile production',
  goal_type: 'ACAD',
  trigger: 'Archaeological investigation along Indus River',
  trigger_type: 'RESEARCH',
  action_type: 'EXCAVATE',
  action_description: 'Excavations uncovered dyed and woven cotton threads affixed to silver vase',
  result: 'Evidence of cotton processing dating to 2300 BCE - earliest known example',
  result_type: 'DISCOVERY',
  
  narrative_summary: 'Archaeological excavations along the Indus River in modern Pakistan revealed cotton threads from 2300 BCE, providing the earliest known evidence of processed cotton fibers and establishing India\'s ancient connection to cotton production.',
  
  temporal: '2300 BCE',
  location: 'Indus River, modern-day Pakistan',
  confidence: 0.85,
  validation_status: 'flagged',
  flags: [
    {
      flag_type: 'single_source',
      flag_severity: 'minor',
      description: 'Needs specific archaeological site citation and publication'
    }
  ]
}]->(cotton)
```

### 8. Innovation: USED_IN (Cotton Seed Extraction Machine)

```cypher
(cotton)-[:USED_IN {
  // Action Structure
  goal: 'Efficiently extract seeds from cotton fibers',
  goal_type: 'TECH',
  trigger: 'Need to process cotton for textile production',
  trigger_type: 'TECH_CONSTRAINT',
  action_type: 'PROCESS',
  action_description: 'Cotton processed using single roller machines to extract seeds - early antecedents of Eli Whitney\'s cotton gin',
  result: 'Cotton fibers separated from seeds for textile production',
  result_type: 'PROD_OUTPUT',
  
  narrative_summary: 'From the beginning, cotton inspired technological innovations. The frescoes in the Ajanta Caves feature Indians working single roller machines designed to extract seeds from cotton fibers - early antecedents of Eli Whitney\'s cotton gin.',
  
  temporal: '2nd century BCE - 5th century CE (Ajanta Caves period)',
  confidence: 0.75,
  validation_status: 'flagged',
  flags: [
    {
      flag_type: 'temporal_inconsistency',
      flag_severity: 'critical',
      description: 'Text incorrectly linked Ajanta Caves (2nd c. BCE-5th c. CE) to 2300 BCE cotton discovery'
    }
  ]
}]->(cottonGin:Machine {
  id: 'C_COTTON_SEED_EXTRACTOR',
  label: 'Cotton Seed Extraction Machine',
  type: 'Machine'
})
```

### 9. Trade: EXPORTED_BY

```cypher
(india:Place {id: 'Q668'})-[:EXPORTED {
  // Action Structure
  goal: 'Generate wealth through global trade',
  goal_type: 'ECON',
  trigger: 'Global demand for Indian cotton textiles',
  trigger_type: 'MARKET',
  action_type: 'TRADE',
  action_description: 'India exported cotton and dyed cotton fabrics globally, creating massive trade surplus',
  result: '1000-year trade surplus, largest global GDP share',
  result_type: 'ECON_GROWTH',
  
  narrative_summary: 'India exported copious quantities of cotton and dyed cotton fabrics. No product ignited the imagination of the world and emptied its pocketbooks like the dyed cotton fabrics, contributing to India\'s 1000-year trade surplus from 1 CE to 1500 CE.',
  
  temporal: '1 CE - 1500 CE',
  export_volume: 'Copious quantities',
  confidence: 0.90,
  validation_status: 'verified'
}]->(cotton)
```

### 10. Historical Observation: DESCRIBED_BY

```cypher
(strabo:Human {
  id: 'Q43067',
  label: 'Strabo',
  type: 'Human',
  qid: 'Q43067'
})-[:DESCRIBED {
  narrative_summary: 'Strabo documented India\'s cotton production and trade in his Geography, noting India\'s vast wealth and resources.',
  
  temporal: '1st century BCE - 1st century CE',
  confidence: 0.85,
  validation_status: 'verified',
  sources: [
    {source: 'Strabo - Geography', source_type: 'primary', tier: 1}
  ]
}]->(cotton)
```

---

## Visual Graph Representation

```
                    [India]
                       |
                       | PRODUCED
                       |
                       v
                    [Cotton] <--ORIGINATED_IN--
                       |                          |
                       |                          |
                       |                          v
                       |                      [India]
                       |
        +--------------+--------------+
        |              |              |
        |              |              |
    MATERIAL_USED  LOCATED_IN   NATURALLY_FIXES
        |              |              |
        v              v              v
[Dyed Cotton    [Indus Valley]    [Indigo]
  Fabrics]
        |
        |
    EXPORTED
        |
        v
[Global Markets]

[Cotton]
    |
    | REQUIRES
    |
    v
[Mordant Process] <--DEVELOPED_BY-- [India]

[Cotton]
    |
    | USED_IN
    |
    v
[Cotton Seed Extraction Machine]
    |
    | DEPICTED_IN
    |
    v
[Ajanta Caves] ⚠️ (Date error in text)

[Cotton]
    |
    | DISCOVERED
    |
    v
[Archaeological Excavation] --LOCATED_IN--> [Indus Valley, Pakistan]
    |
    | Temporal: 2300 BCE
    |
```

---

## Summary: Cotton Node Properties

### Core Node Properties
- **Type**: Product
- **QID**: Q11457 (Wikidata)
- **Label**: Cotton
- **Description**: Fiber used for textile production
- **Confidence**: 0.85

### Key Relationships (10 total)
1. **ORIGINATED_IN** → India
2. **LOCATED_IN** → Indus Valley
3. **MATERIAL_USED_IN** → Dyed Cotton Fabrics
4. **NATURALLY_FIXES_TO** → Indigo (chemical property)
5. **REQUIRES** → Mordant Process (for non-indigo dyes)
6. **PRODUCED_BY** ← India
7. **DISCOVERED_BY** ← Archaeological Excavation
8. **USED_IN** → Cotton Seed Extraction Machine
9. **EXPORTED_BY** ← India
10. **DESCRIBED_BY** ← Strabo

### Relationship Properties
- **Action Structure**: 7 relationships have full action structure (goal, trigger, action, result)
- **Narrative Summaries**: All relationships include narrative context
- **Temporal Information**: 6 relationships have temporal properties
- **Confidence Scores**: Range from 0.75 to 0.95
- **Validation Status**: Most verified, 3 flagged (need citations/verification)
- **Sources**: Relationships include source attribution

### Validation Flags
- ⚠️ **Temporal inconsistency**: Ajanta Caves date error (critical flag)
- ⚠️ **Single source**: Some archaeological claims need more citations
- ⚠️ **Scientific verification needed**: Indigo bonding mechanism

---

## Insights for Schema

### Relationship Types Needed
- ✅ `ORIGINATED_IN` - Geographic origin
- ✅ `MATERIAL_USED_IN` - Material composition
- ✅ `NATURALLY_FIXES_TO` - Chemical bonding (may need custom type)
- ✅ `REQUIRES` - Process dependency
- ✅ `DISCOVERED_BY` - Archaeological discovery
- ✅ `DESCRIBED_BY` - Historical documentation

### Entity Types Needed
- ✅ `Product` - Cotton
- ✅ `Dye` - Indigo
- ✅ `Chemical Process` - Mordant
- ✅ `Machine` - Cotton gin
- ⚠️ May need `Archaeological Site` or map to `Place`

### Property Extensions Demonstrated
- ✅ Temporal properties (dates, periods)
- ✅ Source attribution (multi-source)
- ✅ Confidence scoring
- ✅ Validation flags
- ✅ Narrative summaries
- ✅ Action structure (embedded in relationships)

---

This shows how a single entity (Cotton) becomes a rich, interconnected node in the Chrystallum knowledge graph with multiple relationship types, comprehensive properties, and validation metadata.






