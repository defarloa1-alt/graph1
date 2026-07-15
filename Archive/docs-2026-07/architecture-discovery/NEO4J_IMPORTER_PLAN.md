# Neo4j Importer - Wikidata to Chrystallum Mapping

**Purpose:** Import discovered entities into Neo4j using canonical relationship types

**Input:** 
- SCA output (5000 entities JSON)
- Federation mapping (optional)

**Output:**
- Neo4j Cypher files
- Nodes created
- Relationships mapped to canonical types

---

## 📊 WORKFLOW

```
SCA Output (5000 entities)
  ↓
Entity Type Classification
  ↓
Node Creation (by type)
  ↓
Wikidata Property → Canonical Relationship Mapping
  ↓
Relationship Creation
  ↓
Neo4j Database populated
```

---

## 🗂️ WIKIDATA TO CANONICAL RELATIONSHIP MAPPING

### **Hierarchical Relationships:**

| Wikidata Property | Canonical Relationship | Direction | Example |
|-------------------|------------------------|-----------|---------|
| P31 (instance of) | INSTANCE_OF | Entity → Class | Roman Republic → historical period |
| P279 (subclass of) | SUBCLASS_OF | Class → SuperClass | Middle Ages → ancient history |
| P361 (part of) | PART_OF | Child → Parent | Roman Republic → Ancient Rome |
| P527 (has parts) | HAS_PARTS | Parent → Child | Roman Republic → Early Republic |
| P150 (contains) | CONTAINS | Container → Contained | (admin entities) |

### **Temporal Relationships:**

| Wikidata Property | Canonical Relationship | Direction | Example |
|-------------------|------------------------|-----------|---------|
| P155 (follows) | FOLLOWS | Current → Previous | Roman Republic → Roman Kingdom |
| P156 (followed by) | FOLLOWED_BY | Previous → Next | Roman Republic → Roman Empire |
| P1365 (replaces) | REPLACES | New → Old | Roman Republic → Roman Kingdom |
| P1366 (replaced by) | REPLACED_BY | Old → New | Roman Republic → Roman Empire |
| P580 (start time) | STARTS_IN_YEAR | Entity → Year | Roman Republic → Year:-509 |
| P582 (end time) | ENDS_IN_YEAR | Entity → Year | Roman Republic → Year:-27 |
| P571 (inception) | STARTS_IN_YEAR | Entity → Year | (alternative start) |
| P576 (dissolved) | ENDS_IN_YEAR | Entity → Year | (alternative end) |
| P2348 (time period) | WITHIN_TIME_PERIOD | Entity → Period | Roman Republic → classical antiquity |

### **Geographic Relationships:**

| Wikidata Property | Canonical Relationship | Direction | Example |
|-------------------|------------------------|-----------|---------|
| P36 (capital) | HAS_CAPITAL | Entity → Place | Roman Republic → Rome |
| P276 (location) | LOCATED_IN | Entity → Place | (various) |
| P17 (country) | PART_OF_COUNTRY | Entity → Country | (modern entities) |
| P30 (continent) | ON_CONTINENT | Entity → Continent | Roman Republic → Europe |
| P47 (shares border) | SHARES_BORDER_WITH | Place → Place | Ancient Rome → Persian Empire |
| P706 (located in) | LOCATED_IN | Entity → Feature | Ancient Rome → Mediterranean Basin |
| P625 (coordinates) | (stored as property) | - | lat/long properties |

### **Domain Relationships:**

| Wikidata Property | Canonical Relationship | Direction | Example |
|-------------------|------------------------|-----------|---------|
| P793 (significant event) | HAS_SIGNIFICANT_EVENT | Entity → Event | Roman Republic → Punic Wars |
| P1344 (participant in) | PARTICIPATED_IN | Entity → Event | (reverse) |
| P194 (legislative body) | HAS_LEGISLATIVE_BODY | Entity → Org | Roman Republic → Roman Senate |
| P140 (religion) | HAS_OFFICIAL_RELIGION | Entity → Religion | Roman Republic → ancient Roman religion |
| P3075 (official religion) | HAS_OFFICIAL_RELIGION | Entity → Religion | (same) |
| P38 (currency) | HAS_CURRENCY | Entity → Object | Roman Republic → Roman currency |
| P37 (official language) | HAS_OFFICIAL_LANGUAGE | Entity → Language | Roman Republic → Latin |
| P2936 (language used) | USES_LANGUAGE | Entity → Language | Roman Republic → Ancient Greek |

### **Authority Relationships:**

| Wikidata Property | Canonical Relationship | Direction | Example |
|-------------------|------------------------|-----------|---------|
| P244 (LCSH) | HAS_LCSH_AUTHORITY | Entity → LCSH | Roman Republic → sh85115114 |
| P2163 (FAST) | HAS_FAST_AUTHORITY | Entity → FAST | Rome → 1204500 |
| P1149 (LCC) | CLASSIFIED_BY_LCC | Entity → LCC | Roman Republic → DG241-269 |
| P1584 (Pleiades) | HAS_PLEIADES_ID | Place → Pleiades | Rome → 423025 |
| P1667 (TGN) | HAS_TGN_ID | Place → TGN | Rome → 7000874 |

---

## 🔧 NEO4J IMPORTER FUNCTIONALITY

### **Function 1: Classify Entities**

```python
def classify_entity_type(entity: dict) -> str:
    """
    Determine Chrystallum node type from Wikidata P31
    
    Returns: SubjectConcept, Place, Event, Human, Organization, Work, etc.
    """
    
    p31_values = extract_p31(entity)
    
    # Check classifications
    if 'Q11514315' in p31_values:  # historical period
        return 'SubjectConcept'
    elif 'Q515' in p31_values:  # city
        return 'Place'
    elif 'Q5' in p31_values:  # human
        return 'Human'
    elif 'Q1190554' in p31_values:  # event
        return 'Event'
    elif 'Q43229' in p31_values:  # organization
        return 'Organization'
    elif 'Q47461344' in p31_values:  # written work
        return 'Work'
    # ... more types
    else:
        return 'Concept'  # Default to abstract concept
```

### **Function 2: Create Node**

```python
def create_node_cypher(entity: dict, node_type: str) -> str:
    """
    Generate Cypher CREATE statement for node
    
    Returns: Cypher string
    """
    
    if node_type == 'SubjectConcept':
        return f"""
        CREATE (:SubjectConcept {{
          subject_id: 'subj_{clean_label}_{qid.lower()}',
          label: '{label}',
          qid: '{qid}',
          primary_facet: '{primary_facet}',
          related_facets: {related_facets},
          lcsh_id: '{lcsh_id}',
          fast_id: '{fast_id}',
          start_date: '{start_date}',
          end_date: '{end_date}',
          federation_score: {fed_score},
          confidence: {confidence}
        }})
        """
    
    elif node_type == 'Place':
        return f"""
        CREATE (:Place {{
          place_id: 'place_{clean_label}_{qid.lower()}',
          label: '{label}',
          qid: '{qid}',
          pleiades_id: '{pleiades_id}',
          tgn_id: '{tgn_id}',
          lcsh_id: '{lcsh_id}',
          lat: {lat},
          long: {long},
          federation_score: {fed_score}
        }})
        """
    
    # ... more node types
```

### **Function 3: Map Relationships**

```python
def create_relationship_cypher(from_qid: str, to_qid: str, wikidata_prop: str) -> str:
    """
    Map Wikidata property to canonical relationship
    
    Returns: Cypher MATCH + CREATE statement
    """
    
    # Map property to canonical type
    relationship_map = {
        'P31': 'INSTANCE_OF',
        'P279': 'SUBCLASS_OF',
        'P361': 'PART_OF',
        'P527': 'HAS_PARTS',
        'P155': 'FOLLOWS',
        'P156': 'FOLLOWED_BY',
        'P36': 'HAS_CAPITAL',
        'P793': 'HAS_SIGNIFICANT_EVENT',
        'P194': 'HAS_LEGISLATIVE_BODY',
        'P140': 'HAS_OFFICIAL_RELIGION',
        'P38': 'HAS_CURRENCY',
        # ... all mappings
    }
    
    rel_type = relationship_map.get(wikidata_prop, 'RELATED_TO')
    
    return f"""
    MATCH (from {{qid: '{from_qid}'}})
    MATCH (to {{qid: '{to_qid}'}})
    CREATE (from)-[:{rel_type} {{
      source: 'wikidata',
      wikidata_property: '{wikidata_prop}'
    }}]->(to)
    """
```

### **Function 4: Generate Complete Import**

```python
def generate_neo4j_import(entities: dict, show_progress: bool = True) -> str:
    """
    Generate complete Neo4j import with progress
    
    Shows progress as it processes each entity
    """
    
    cypher_lines = []
    
    print(f"\n{'='*80}")
    print(f"NEO4J IMPORT GENERATION")
    print(f"{'='*80}\n")
    
    # Phase 1: Create nodes
    print(f"PHASE 1: Creating nodes...\n")
    
    for i, (qid, entity) in enumerate(entities.items(), 1):
        node_type = classify_entity_type(entity)
        cypher = create_node_cypher(entity, node_type)
        cypher_lines.append(cypher)
        
        if show_progress:
            print(f"[{i}/{len(entities)}] Node: {qid} ({entity['label']}) -> {node_type}")
    
    # Phase 2: Create relationships
    print(f"\nPHASE 2: Creating relationships...\n")
    
    rel_count = 0
    for i, (qid, entity) in enumerate(entities.items(), 1):
        # Extract all QID-valued properties
        for prop_id, claims in entity['claims'].items():
            for claim in claims:
                target_qid = extract_entity_id(claim)
                if target_qid and target_qid in entities:
                    cypher = create_relationship_cypher(qid, target_qid, prop_id)
                    cypher_lines.append(cypher)
                    rel_count += 1
        
        if show_progress and i % 100 == 0:
            print(f"[{i}/{len(entities)}] Processed relationships for {qid}")
    
    print(f"\nTotal relationships: {rel_count}\n")
    
    # Save
    output_file = "output/neo4j/import.cypher"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cypher_lines))
    
    print(f"Saved: {output_file}\n")
    
    return output_file
```

---

## 📋 COMPLETE PIPELINE

```
Step 1: SCA Traversal (1.5 hours)
  → 5000 entities discovered
  → Shows: QID (Label) - TYPE - Fed:N - All properties
  → Filters: Skip pre-2000 BC, skip periods without end dates
  → Output: entities JSON

Step 2: Federation Mapper (30 min)
  → Map to LCSH, FAST, LCC, PeriodO, Pleiades
  → Shows progress with all federation IDs
  → Output: federation mapping JSON

Step 3: Neo4j Importer (10 min)
  → Classify entity types
  → Create nodes (SubjectConcept, Place, Event, etc.)
  → Map properties to canonical relationships
  → Generate Cypher files
  → Output: import.cypher (ready to execute)

Step 4: Execute in Neo4j
  → Run import.cypher
  → 5000+ nodes created
  → 10,000+ relationships created
  → Complete domain in Neo4j!
```

---

## ✅ **READY FOR NEXT PHASE:**

**After SCA completes, we'll build:**
1. Neo4j Importer (maps properties to canonical relationships)
2. Uses your relationship master
3. Shows progress as it generates Cypher

**Let me know when SCA finishes and we'll build the importer!** 🎯
