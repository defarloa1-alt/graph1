# Integration Agent - Plan

**After SCA collects entities, Integration Agent processes them**

---

## 🤖 TWO-AGENT ARCHITECTURE

### **Agent 1: SCA (Subject Concept Agent)**

**Purpose:** Discovery and collection  
**Input:** Seed QID  
**Process:**
- Generic graph traversal
- Collect ALL entities (5000+)
- Fetch ALL properties
- Resolve ALL labels

**Output:**
```json
{
  "entities": {
    "Q17167": {
      "label": "Roman Republic",
      "properties_count": 61,
      "claims": { /* raw Wikidata claims */ },
      "depth": 0
    },
    "Q220": {
      "label": "Rome",
      "properties_count": 262,
      "claims": { /* raw Wikidata claims */ },
      "depth": 1
    }
  }
}
```

**Focus:** Raw data collection, no interpretation

---

### **Agent 2: Integration Agent (New)**

**Purpose:** Schema mapping and federation  
**Input:** SCA output JSON  
**Process:**

#### **Phase 1: Entity Type Mapping**

Map each entity to Chrystallum schema:

```python
For each entity:
  Check P31 (instance of):
    - Q11514315 → SubjectConcept (Period)
    - Q515 → Place
    - Q5 → Human
    - Q1190554 → Event
    - Q43229 → Organization
    - Q47461344 → Work
    etc.
  
  Assign to node type:
    → (:SubjectConcept)
    → (:Place)
    → (:Human)
    → (:Event)
    → (:Organization)
    → (:Work)
```

#### **Phase 2: Authority Federation**

Match to external authorities:

**2.1 Library Authorities (from Wikidata):**
```python
Check properties:
  P244 (LCSH) → Link to LCSH authority
  P2163 (FAST) → Link to FAST authority
  P1149 (LCC) → Link to LCC classification
  P10832 (WorldCat) → Link to WorldCat
```

**2.2 Geographic Authorities (from Wikidata):**
```python
For Place entities:
  P1584 (Pleiades) → Link to Pleiades gazetteer
  P1667 (TGN) → Link to Getty TGN
  P8216 (iDAI) → Link to iDAI.gazetteer
```

**2.3 PeriodO Integration (external matching):**
```python
For Period entities:
  Extract temporal bounds:
    P580 (start) + P582 (end)
    OR P571 (inception) + P576 (dissolved)
  
  Match to PeriodO dataset:
    Load: Temporal/periodo-dataset.csv
    
    Match by:
      1. Label similarity (Roman Republic ≈ periodo label)
      2. Temporal overlap (dates match)
      3. QID if present in PeriodO
    
    Assign periodo_id:
      periodo_id: "p0xxxxx"
```

**2.4 Pleiades Integration (for Places without P1584):**
```python
For Place entities WITHOUT P1584:
  Load: Geographic/pleiades_places.csv (41,993 places)
  
  Match by:
    1. Label similarity
    2. Coordinates proximity (if P625 present)
    3. QID crosswalk
  
  Assign pleiades_id:
    pleiades_id: "423025"
```

#### **Phase 3: Relationship Mapping**

Map Wikidata properties to Chrystallum relationships:

```cypher
// Hierarchical
P31 (instance of) → [:INSTANCE_OF]
P279 (subclass of) → [:SUBCLASS_OF]
P361 (part of) → [:PART_OF]
P527 (has parts) → [:HAS_PARTS]

// Temporal
P155 (follows) → [:FOLLOWS]
P156 (followed by) → [:FOLLOWED_BY]
P1365 (replaces) → [:REPLACES]
P1366 (replaced by) → [:REPLACED_BY]

// Domain
P36 (capital) → [:HAS_CAPITAL]
P793 (event) → [:HAS_SIGNIFICANT_EVENT]
P194 (legislature) → [:HAS_LEGISLATIVE_BODY]
P140 (religion) → [:HAS_OFFICIAL_RELIGION]
P38 (currency) → [:HAS_CURRENCY]

// Temporal Backbone
start_date → [:STARTS_IN_YEAR]→(:Year)
end_date → [:ENDS_IN_YEAR]→(:Year)
```

#### **Phase 4: Facet Assignment**

Map properties to 18 canonical facets:

```python
For each entity:
  facets = []
  
  If P140 or P3075: facets.append('RELIGIOUS')
  If P194 or P122: facets.append('POLITICAL')
  If P793 (wars): facets.append('MILITARY')
  If P38: facets.append('ECONOMIC')
  If P37 or P2936: facets.append('LINGUISTIC')
  If P30 or P625: facets.append('GEOGRAPHIC')
  If P1792: facets.append('SOCIAL')
  etc.
  
  Assign:
    primary_facet = facets[0]
    related_facets = facets[1:]
```

#### **Phase 5: Generate Neo4j Cypher**

Create Cypher statements:

```cypher
// For each SubjectConcept
CREATE (:SubjectConcept {
  subject_id: 'subj_roman_republic_q17167',
  label: 'Roman Republic',
  qid: 'Q17167',
  primary_facet: 'POLITICAL',
  related_facets: ['MILITARY', 'RELIGIOUS', ...],
  lcsh_id: 'sh85115114',
  fast_id: '1204885',
  periodo_id: 'p0xxxxx',
  start_date: '-0509-00-00',
  end_date: '-0027-01-16',
  confidence: 0.95
})

// For each Place
CREATE (:Place {
  place_id: 'place_rome_q220',
  label: 'Rome',
  qid: 'Q220',
  pleiades_id: '423025',
  tgn_id: '7000874',
  lcsh_id: 'n79018704',
  fast_id: '1204500',
  lat: 41.9,
  long: 12.5
})

// Relationships
MATCH (sc:SubjectConcept {qid: 'Q17167'})
MATCH (place:Place {qid: 'Q220'})
CREATE (sc)-[:HAS_CAPITAL]->(place)

// etc.
```

---

## 📊 INTEGRATION AGENT WORKFLOW

```
INPUT: SCA output (5000 entities JSON)
  ↓
STEP 1: Entity Type Classification
  - Map P31 values to node labels
  - Result: SubjectConcepts, Places, Events, etc.
  ↓
STEP 2: Authority Federation
  - Link to LCSH, FAST, LCC (from Wikidata)
  - Match to PeriodO (external CSV)
  - Match to Pleiades (external CSV)
  ↓
STEP 3: Relationship Mapping
  - Map Wikidata properties to Chrystallum relationships
  - Create edge definitions
  ↓
STEP 4: Facet Assignment
  - Analyze properties
  - Map to 18 canonical facets
  ↓
STEP 5: Generate Cypher
  - CREATE statements for nodes
  - CREATE statements for relationships
  - CREATE statements for authority links
  ↓
OUTPUT: 
  - Neo4j Cypher files (ready to execute)
  - Entity mapping report
  - Authority coverage report
  - Facet distribution report
```

---

## 🗂️ INTEGRATION AGENT COMPONENTS

### **Component 1: Entity Classifier**

**File:** `scripts/integration/entity_classifier.py`

**Functionality:**
- Takes SCA entities
- Checks P31 values
- Maps to Chrystallum node types
- Validates required properties

### **Component 2: PeriodO Matcher**

**File:** `scripts/integration/periodo_matcher.py`

**Functionality:**
- Loads PeriodO dataset
- Matches periods by label and dates
- Assigns periodo_id
- Reports match confidence

### **Component 3: Pleiades Matcher**

**File:** `scripts/integration/pleiades_matcher.py`

**Functionality:**
- Loads Pleiades dataset (41,993 places)
- Matches places by label and coordinates
- Assigns pleiades_id
- Reports match confidence

### **Component 4: Relationship Mapper**

**File:** `scripts/integration/relationship_mapper.py`

**Functionality:**
- Maps Wikidata properties to Chrystallum relationships
- Validates relationship targets exist
- Creates edge list with types

### **Component 5: Facet Assigner**

**File:** `scripts/integration/facet_assigner.py`

**Functionality:**
- Analyzes entity properties
- Maps to 18 canonical facets
- Assigns primary + related facets
- Reports facet distribution

### **Component 6: Cypher Generator**

**File:** `scripts/integration/cypher_generator.py`

**Functionality:**
- Generates CREATE statements for nodes
- Generates CREATE statements for relationships
- Generates authority links
- Outputs executable Cypher files

---

## 📋 PROPERTY COVERAGE

**Integration Agent will handle:**

✅ **Temporal Properties:**
- P580 (start time)
- P582 (end time)
- P571 (inception)
- P576 (dissolved)
→ Map to: start_date, end_date, tether to Year backbone

✅ **Geographic Properties:**
- P30 (continent)
- P36 (capital)
- P625 (coordinates)
- P276 (location)
→ Map to: geographic properties, link to Places

✅ **Authority Properties:**
- P244 (LCSH) → lcsh_id
- P2163 (FAST) → fast_id
- P1149 (LCC) → lcc_class
- P1584 (Pleiades) → pleiades_id
- P1667 (TGN) → tgn_id

✅ **Relationship Properties:**
- P31, P279, P361, P527 → Hierarchy
- P155, P156, P1365, P1366 → Succession
- P36, P793, P194, P38, P140 → Domain

---

## 🎯 FINAL WORKFLOW

```
USER → Enters QID (Q17167)
  ↓
SCA → Traverses 5000 entities (1.5 hours)
  ↓
SCA OUTPUT → JSON with 5000 entities, all properties, all labels
  ↓
INTEGRATION AGENT → Processes entities (30 min)
  ↓
INTEGRATION OUTPUT → 
  - entity_mapping.json (what each entity is)
  - authority_federation.json (all external IDs)
  - relationships.json (all edges)
  - facet_assignments.json (facet mappings)
  - neo4j_import.cypher (ready to execute)
  ↓
NEO4J → Execute Cypher, import complete domain
  ↓
RESULT → Complete SubjectConcept domain in Neo4j!
```

---

## ✅ SUMMARY

**SCA Agent:** Discovers (running now in your terminal!)  
**Integration Agent:** Maps and federates (build next)

**Watch your terminal - when SCA completes, we'll build the Integration Agent!** 🎯
