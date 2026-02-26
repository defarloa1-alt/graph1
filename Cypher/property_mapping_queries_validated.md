# Property Mapping Queries - Validated by User (2026-02-22)

These queries have been tested and confirmed working in Neo4j.

## Query 1: Get Facet for Specific Property

**Without parameters (direct value):**
```cypher
MATCH (pm:PropertyMapping {property_id: 'P39'})
RETURN pm.primary_facet;
```

**With parameters (Neo4j Browser):**
```cypher
// CORRECT SYNTAX - Set parameters:
:params {prop: 'P39'}

// Then run:
MATCH (pm:PropertyMapping {property_id: $prop})
RETURN pm.primary_facet;
```

---

## Query 2: Route to Agent (Property → Facet → Agent)

**Version A: With literal values**
```cypher
MATCH (pm:PropertyMapping {property_id: 'P39'})
MATCH (pm)-[:HAS_PRIMARY_FACET]->(f:Facet)
MATCH (agent:Agent)-[:ASSIGNED_TO_FACET]->(f)
WHERE agent.subject_id = 'Q17167'
RETURN agent.id, f.key;
```

**Version B: With parameters (CORRECT SYNTAX)**
```cypher
// Set parameters first (use JSON format):
:params {prop: 'P39', subject: 'Q17167'}

// Then run:
MATCH (pm:PropertyMapping {property_id: $prop})
MATCH (pm)-[:HAS_PRIMARY_FACET]->(f:Facet)
MATCH (agent:Agent)-[:ASSIGNED_TO_FACET]->(f)
WHERE agent.subject_id = $subject
RETURN agent.id, f.key;
```

**Alternative (individual params):**
```cypher
// Neo4j 5.x syntax:
:param prop: 'P39'
:param subject: 'Q17167'
```

---

## Query 3: List All MILITARY Properties

```cypher
MATCH (pm:PropertyMapping {primary_facet: 'MILITARY'})
RETURN pm.property_id, pm.property_label, pm.confidence
ORDER BY pm.confidence DESC;
```

**Expected Results:**
- ~13 properties
- Including: P533 (target), P798 (military designation), P520 (armament)
- Confidence scores: 0.8-0.9

---

## Query 4: Check New Imports by Resolution Method

```cypher
// Properties imported in this session
MATCH (pm:PropertyMapping)
WHERE pm.resolved_by IN ['claude', 'base_mapping']
RETURN pm.resolved_by as method, count(pm) as count;
```

**Expected Results:**
- claude: ~360
- base_mapping: ~346
- Total: ~706

---

## Usage Examples

**Get facet for property P607 (conflict):**
```cypher
MATCH (pm:PropertyMapping {property_id: 'P607'})
RETURN pm.primary_facet, pm.confidence;
// Expected: MILITARY, confidence ~0.85
```

**Find all GEOGRAPHIC properties:**
```cypher
MATCH (pm:PropertyMapping {primary_facet: 'GEOGRAPHIC'})
RETURN pm.property_id, pm.property_label
ORDER BY pm.property_id;
// Expected: ~113 properties
```

**Check multi-facet properties:**
```cypher
MATCH (pm:PropertyMapping)
WHERE pm.secondary_facets IS NOT NULL AND pm.secondary_facets <> ''
RETURN pm.property_id, pm.primary_facet, pm.secondary_facets
LIMIT 20;
// Expected: Properties with multiple facet applicability
```

---

## Integration Pattern for SCA

**When SCA encounters Wikidata property:**

```python
# 1. Lookup facet mapping
result = session.run("""
    MATCH (pm:PropertyMapping {property_id: $prop_id})
    RETURN pm.primary_facet as facet, 
           pm.secondary_facets as secondary,
           pm.confidence as confidence
""", prop_id=property_id)

if result.peek():
    mapping = result.single()
    primary_facet = mapping['facet']
    
    # 2. Route to appropriate SFA
    sfa_result = session.run("""
        MATCH (f:Facet {key: $facet_key})
        MATCH (agent:Agent)-[:ASSIGNED_TO_FACET]->(f)
        WHERE agent.subject_id = $subject_qid
        RETURN agent.id as agent_id
    """, facet_key=primary_facet, subject_qid=subject_concept_qid)
    
    # 3. Dispatch to SFA for processing
```

---

## Validation Results

**All queries tested:** ✅ Working  
**Use cases:** Property lookup, agent routing, facet filtering  
**Performance:** Fast (indexed on property_id and primary_facet)

**Documented:** 2026-02-22 by QA Agent
