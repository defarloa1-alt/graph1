# Chrystallum Place/PlaceVersion Integration Roadmap

**Status:** Phase 2A+2B analysis run → Post-analysis enrichment  
**Last Updated:** 2026-02-15  
**Purpose:** Define transformation path from Phase 2 Entity discovery to Place+PlaceVersion enrichment

---

## Overview

This document describes how Phase 2A+2B entity discovery feeds into the Chrystallum Place/PlaceVersion architecture, and what happens after the analysis run completes.

---

## Two-Phase Approach

### **Phase 2A+2B: Analysis Run (Week 1)**

**Purpose:** Validate entity discovery pipeline, gather real data for PlaceVersion design

**Input:**
- Roman Republic Wikipedia article
- 8-hop backlink harvest
- Two-track validation (direct historical + temporal bridges)

**Output:**
```
~2,100 Entity nodes in Neo4j
├─ Human: 1,542
├─ Event: 600
├─ Place: 189  ← FOCUS for PlaceVersion analysis
└─ Organization: 87

Simple Schema:
Entity {
  entity_id: "ent_rome_q220",
  label: "Rome",
  type: "place",
  qid: "Q220",
  track: "direct_historical",
  is_bridge: false,
  confidence: 0.85,
  date: -753
}
```

**What You Get:**
- ✅ Complete entity inventory (no PlaceVersion yet)
- ✅ 189 discovered places with QIDs
- ✅ Temporal context (dates, periods)
- ✅ 15 test cases runnable
- ✅ Real data for pattern analysis

---

### **Post-Analysis: PlaceVersion Design (Week 2-4)**

**Purpose:** Transform discovered places into Place+PlaceVersion architecture based on actual needs

**Analysis Questions (Week 2):**

1. **Which places have temporal discontinuities?**
   ```cypher
   MATCH (e:Entity {type: "place"})
   WHERE e.destruction_date IS NOT NULL 
      OR e.name_change IS NOT NULL
   RETURN e.label, e.qid, e.date
   
   // Expected: Carthage (destroyed -146), Byzantium (renamed)
   ```

2. **Which places have boundary changes?**
   ```cypher
   MATCH (conquest:Entity {type: "event"})-[:INVOLVED]->(place:Entity {type: "place"})
   WHERE conquest.label CONTAINS "conquest" 
      OR conquest.label CONTAINS "annexation"
   RETURN place.label, conquest.label, conquest.date
   
   // Expected: Gaul (conquered -58 to -50), Spain (gradual conquest)
   ```

3. **Which places have administrative status changes?**
   ```cypher
   MATCH (place:Entity {type: "place"})-[:BECAME]->(status)
   WHERE status.label CONTAINS "province"
      OR status.label CONTAINS "territory"
   RETURN place.label, status.label, status.date
   
   // Expected: Sicily (-241 → first province), Spain (-197 → two provinces)
   ```

4. **Which bridges reference ancient places?**
   ```cypher
   MATCH (bridge:Entity {is_bridge: true})-[r]->(ancient:Entity {type: "place"})
   WHERE ancient.date < -200
   RETURN bridge.label, bridge.bridge_type, ancient.label, bridge.temporal_gap
   
   // Expected: Archaeological discoveries at Carthage, Pompeii, etc.
   ```

**Expected Discovery:**
```python
PLACE_ANALYSIS_RESULTS = {
    'total_places': 189,
    
    'needs_versioning': 42,  # ~22%
    'examples': [
        {'place': 'Gaul', 'reason': 'conquest changed boundaries', 'versions': 2},
        {'place': 'Carthage', 'reason': 'city destroyed, province created', 'versions': 2},
        {'place': 'Spain', 'reason': 'divided into Citerior/Ulterior', 'versions': 3},
        {'place': 'Rome', 'reason': 'Republic capital vs Empire capital', 'versions': 2}
    ],
    
    'stable_places': 147,  # ~78%
    'examples': [
        {'place': 'Tiber River', 'reason': 'natural feature, unchanged'},
        {'place': 'Alps', 'reason': 'natural boundary, stable'},
        {'place': 'Athens', 'reason': 'outside Roman conquest scope (stable ally)'}
    ]
}
```

---

## Transformation Workflow

### **Week 3: Design PlaceVersion Schema**

Based on Week 2 analysis, create formal schema:

1. **Extract versioning patterns**
   - Identify common transition types (conquest, division, destruction)
   - Define temporal bound rules (when to create new version)
   - Specify boundary change thresholds (area change >10%?)

2. **Design Cypher schema**
   Create `PLACE_VERSION_NEO4J_SCHEMA.cypher`:
   ```cypher
   // Place constraints (persistent identity)
   CREATE CONSTRAINT place_id_unique IF NOT EXISTS
   FOR (p:Place) REQUIRE p.id_hash IS UNIQUE;
   
   // PlaceVersion constraints (temporal state)
   CREATE CONSTRAINT place_version_id_unique IF NOT EXISTS
   FOR (pv:PlaceVersion) REQUIRE pv.id_hash IS UNIQUE;
   
   CREATE CONSTRAINT place_version_temporal IF NOT EXISTS
   FOR (pv:PlaceVersion) REQUIRE pv.valid_from IS NOT NULL;
   
   // Indexes for temporal queries
   CREATE INDEX place_version_temporal_range IF NOT EXISTS
   FOR (pv:PlaceVersion) ON (pv.valid_from, pv.valid_to);
   
   CREATE INDEX place_version_place_id IF NOT EXISTS
   FOR (pv:PlaceVersion) ON (pv.place_id);
   ```

3. **Define transformation rules**
   ```python
   def should_create_place_version(entity):
       """Determine if Entity:place needs PlaceVersion enrichment"""
       
       # High priority: Conquered territories
       if entity['label'] in ['Gaul', 'Carthage', 'Spain', 'Macedon']:
           return True, 'territorial_change'
       
       # Medium priority: Administrative status change
       if has_province_transition(entity):
           return True, 'status_change'
       
       # Low priority: Name change only
       if has_name_change_across_periods(entity):
           return True, 'nomenclature'
       
       # Stable: No versioning needed
       return False, None
   ```

---

### **Week 4: Transform Entity → Place + PlaceVersion**

**Step 1: Create Place nodes from Entity:place**
```cypher
// Convert 189 Entity:place → Place nodes
MATCH (e:Entity {type: "place"})
CREATE (p:Place {
  id_hash: replace(e.entity_id, "ent_", "plc_"),
  label: e.label,
  qid: e.qid,
  has_temporal_versions: false  // Will update for versioned places
})
WITH e, p
CREATE (e)-[:CONVERTED_TO]->(p)
```

**Step 2: Create PlaceVersion for identified places**
```cypher
// Example: Gaul (2 versions)
MATCH (p:Place {qid: "Q38"})
SET p.has_temporal_versions = true

CREATE (pv1:PlaceVersion {
  id_hash: "plc_v_gaul_independent_400bce_58bce",
  place_id: p.id_hash,
  label: "Gaul (Independent)",
  valid_from: -400,
  valid_to: -58,
  political_status: "independent_tribal_confederation",
  confidence: 0.85
})

CREATE (pv2:PlaceVersion {
  id_hash: "plc_v_gaul_roman_27bce_476ce",
  place_id: p.id_hash,
  label: "Tres Galliae (Roman Provinces)",
  valid_from: -27,
  valid_to: 476,
  political_status: "roman_provinces",
  confidence: 0.95
})

CREATE (p)-[:HAS_VERSION {temporal_sequence: 1}]->(pv1)
CREATE (p)-[:HAS_VERSION {temporal_sequence: 2}]->(pv2)
CREATE (pv1)-[:SUCCEEDED_BY]->(pv2)
```

**Step 3: Load geometry from authorities**
```python
# For each PlaceVersion, fetch geometry from Wikidata
import requests

def load_geometry_for_place_version(place_version_id, wikidata_qid):
    """Fetch GeoJSON from Wikidata for a specific period"""
    
    sparql_query = f"""
    SELECT ?geometry WHERE {{
      wd:{wikidata_qid} p:P625 ?statement .
      ?statement ps:P625 ?geometry .
      OPTIONAL {{ ?statement pq:P580 ?startTime }}
      OPTIONAL {{ ?statement pq:P582 ?endTime }}
    }}
    """
    
    # Execute query, transform to Geometry node
    geometry_data = execute_sparql(sparql_query)
    
    cypher = """
    MATCH (pv:PlaceVersion {id_hash: $pv_id})
    CREATE (g:Geometry {
      geometry_id: $geom_id,
      type: $geom_type,
      coordinates: $coords,
      source: 'wikidata',
      retrieved_at: datetime()
    })
    CREATE (pv)-[:HAS_GEOMETRY]->(g)
    """
    
    execute_cypher(cypher, {
        'pv_id': place_version_id,
        'geom_id': f"geom_{place_version_id}",
        'geom_type': geometry_data['type'],
        'coords': geometry_data['coordinates']
    })
```

**Step 4: Link to temporal backbone**
```cypher
// Link PlaceVersion to Year nodes
MATCH (pv:PlaceVersion)
MATCH (year_start:Year {year: pv.valid_from})
MATCH (year_end:Year {year: pv.valid_to})
CREATE (pv)-[:TEMPORAL_START]->(year_start)
CREATE (pv)-[:TEMPORAL_END]->(year_end)
```

**Step 5: Assign facets**
```cypher
// Assign facets based on PlaceVersion context
MATCH (pv:PlaceVersion {political_status: "roman_province"})
MATCH (political:Facet {label: "Political"})
MATCH (military:Facet {label: "Military"})
CREATE (pv)-[:HAS_FACET]->(political)
CREATE (pv)-[:HAS_FACET]->(military)
```

---

## Validation & Verification

### **Test Cases (Run After Transformation)**

```cypher
// TC01: Verify Place nodes created
MATCH (p:Place)
RETURN COUNT(p) AS place_count
// Expected: 189

// TC02: Verify PlaceVersion count
MATCH (pv:PlaceVersion)
RETURN COUNT(pv) AS version_count
// Expected: ~84 (42 places × 2 versions average)

// TC03: Verify temporal coherence
MATCH (pv:PlaceVersion)
WHERE pv.valid_from >= pv.valid_to
RETURN pv.label, pv.valid_from, pv.valid_to
// Expected: 0 results (no temporal inversions)

// TC04: Verify succession links
MATCH (pv1:PlaceVersion)-[:SUCCEEDED_BY]->(pv2:PlaceVersion)
WHERE pv1.valid_to <> pv2.valid_from
RETURN pv1.label, pv1.valid_to, pv2.label, pv2.valid_from
// Expected: 0 results (no temporal gaps in succession)

// TC05: Verify geometry attachment
MATCH (pv:PlaceVersion)-[:HAS_GEOMETRY]->(g:Geometry)
RETURN COUNT(DISTINCT pv) AS places_with_geometry
// Expected: ~42 (versioned places have geometry)

// TC06: Query temporal context (Gaul example)
MATCH (place:Place {label: "Gaul"})-[:HAS_VERSION]->(pv:PlaceVersion)
WHERE pv.valid_from <= -52 AND pv.valid_to >= -52
RETURN pv.label, pv.political_status
// Expected: "Gaul (Independent)", "independent_tribal_confederation"
```

---

## Success Criteria

**Phase 2A+2B Complete When:**
- ✅ ~2,100 Entity nodes loaded to Neo4j
- ✅ 189 Place entities discovered
- ✅ 15 test cases validate discovery accuracy
- ✅ Analysis identifies versioning needs

**PlaceVersion Enrichment Complete When:**
- ✅ 189 Place nodes created from Entity:place
- ✅ ~42 places enriched with PlaceVersion (~22%)
- ✅ ~84 PlaceVersion nodes created (avg 2 per versioned place)
- ✅ Geometry nodes attached for versioned places
- ✅ Temporal backbone linkage established
- ✅ Facets assigned based on context
- ✅ All 6 validation test cases pass

---

## Files Deliverable

| File | Purpose | Status |
|------|---------|--------|
| **CHRYSTALLUM_PHASE2_INTEGRATION.md** | This file | ✅ Created |
| **PHASE_2_QUICK_START.md** | Phase 2A+2B execution guide | ✅ Exists |
| **GO_COMMAND_CHECKLIST.md** | Final approval checklist | 🔄 Next |
| **CHRYSTALLUM_PLACE_SEEDING_REQUIREMENTS.md** | Comprehensive spec | ⏸️ Deferred to Week 3 |
| **PLACE_VERSION_NEO4J_SCHEMA.cypher** | Schema DDL | ⏸️ Deferred to Week 3 |
| **transform_entity_to_place_version.py** | Transformation script | ⏸️ Deferred to Week 4 |
| **load_place_geometry.py** | Geometry loading script | ⏸️ Deferred to Week 4 |

---

## Next Actions

1. **Review & Approve:** GO_COMMAND_CHECKLIST.md (final sign-off)
2. **Execute Phase 2A+2B:** Follow PHASE_2_QUICK_START.md
3. **Run 15 Test Cases:** Validate discovery accuracy
4. **Analyze Results:** Query patterns, identify versioning needs
5. **Design PlaceVersion:** Create schema based on analysis
6. **Transform Data:** Execute Week 4 transformation scripts
7. **Validate Enrichment:** Run verification test cases

---

**This roadmap ensures PlaceVersion architecture is informed by real data, not speculation.** 🎯
