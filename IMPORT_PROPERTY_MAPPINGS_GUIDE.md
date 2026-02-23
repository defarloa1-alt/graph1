# Property Mappings - Neo4j Import Guide

## Quick Import (5 minutes)

### Step 1: Copy CSV to Neo4j Import Folder

```powershell
# For Neo4j Desktop
Copy-Item "CSV\property_mappings\property_facet_mapping_HYBRID.csv" "C:\Users\YourName\.Neo4jDesktop\relate-data\dbmss\dbms-xxx\import\"

# For Neo4j Aura (use Neo4j Browser upload)
# Or use the auto_import script
```

### Step 2: Copy Property Types CSV (Optional)

```powershell
Copy-Item "CSV\backlinks\Q107649491_property_types_CLEAN.csv" "C:\Users\YourName\.Neo4jDesktop\relate-data\dbmss\dbms-xxx\import\"
```

### Step 3: Run Import Script

**Option A: Via Neo4j Browser**
1. Open Neo4j Browser
2. Copy-paste from `output/neo4j/import_property_mappings.cypher`
3. Execute sections in order (Steps 1-6)

**Option B: Via Auto Import Script**
```powershell
python scripts/neo4j/auto_import.py `
  output/neo4j/import_property_mappings.cypher `
  100 `
  "neo4j+s://f7b612a3.databases.neo4j.io" `
  "neo4j" `
  "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
```

---

## What Gets Created

### Nodes

**1. PropertyMapping (500 nodes)**
```cypher
(:PropertyMapping {
  property_id: "P39",
  property_label: "position held",
  property_description: "...",
  primary_facet: "POLITICAL",
  secondary_facets: "BIOGRAPHIC",
  all_facets: "POLITICAL,BIOGRAPHIC",
  confidence: 0.8,
  is_historical: false,
  is_authority_control: false,
  resolved_by: "base_mapping",
  type_count: 3
})
```

**2. PropertyType (500 nodes - Optional)**
```cypher
(:PropertyType {
  qid: "Q56248884",
  label: "Wikidata property related to the Ancient World",
  description: "type of Wikidata property",
  meta_type: "property_classification",
  parent_qid: "Q107649491"
})
```

**3. DomainProfile (3 nodes - Optional)**
```cypher
(:DomainProfile {
  domain_id: "ancient_history",
  domain_name: "Ancient & Medieval History",
  temporal_scope: "-3000 to 1800",
  priority_facets: "MILITARY,POLITICAL,RELIGIOUS,BIOGRAPHIC,ARCHAEOLOGICAL"
})
```

### Relationships

```
(PropertyMapping)-[:HAS_PRIMARY_FACET]->(Facet)
(PropertyMapping)-[:HAS_SECONDARY_FACET]->(Facet)
(PropertyMapping)-[:HAS_TYPE]->(PropertyType)
(DomainProfile)-[:PRIORITIZES {tier, boost}]->(PropertyMapping)
```

---

## Verification Queries

### After Import, Run These:

```cypher
// 1. Total count
MATCH (pm:PropertyMapping) 
RETURN count(pm) as total;
// Expected: 500

// 2. Facet distribution
MATCH (pm:PropertyMapping)
RETURN pm.primary_facet as facet, count(pm) as count
ORDER BY count DESC;
// Should show SCIENTIFIC and GEOGRAPHIC at top (~89 each)

// 3. High confidence properties
MATCH (pm:PropertyMapping)
WHERE pm.confidence >= 0.8
RETURN count(pm) as high_confidence;
// Expected: 433

// 4. Authority control properties
MATCH (pm:PropertyMapping {is_authority_control: true})
RETURN count(pm);
// Expected: 45

// 5. Sample property lookup
MATCH (pm:PropertyMapping {property_id: 'P39'})
RETURN pm;
// Should show: position held → POLITICAL

// 6. Facet relationships
MATCH (pm:PropertyMapping {property_id: 'P189'})-[:HAS_PRIMARY_FACET]->(pf:Facet)
OPTIONAL MATCH (pm)-[:HAS_SECONDARY_FACET]->(sf:Facet)
RETURN pm.property_id, pm.property_label, pf.key as primary, collect(sf.key) as secondary;
// Should show: P189 → GEOGRAPHIC primary, [ARCHAEOLOGICAL, SCIENTIFIC] secondary
```

---

## Usage Examples

### Example 1: Get Properties for MILITARY Facet
```cypher
MATCH (f:Facet {key: 'MILITARY'})<-[:HAS_PRIMARY_FACET]-(pm:PropertyMapping)
WHERE pm.confidence >= 0.7
RETURN pm.property_id, pm.property_label, pm.confidence
ORDER BY pm.confidence DESC;
```

**Use Case:** When SCA processes MILITARY facet, use these properties

### Example 2: Route Property to Agent
```cypher
// Given a property, find which agent should handle it
MATCH (pm:PropertyMapping {property_id: $property_id})
MATCH (pm)-[:HAS_PRIMARY_FACET]->(f:Facet)
MATCH (agent:Agent)-[:ASSIGNED_TO_FACET]->(f)
WHERE agent.subject_id = $subject_id
RETURN agent.id as agent_to_use, f.key as facet;
```

**Use Case:** Automatic agent routing when processing Wikidata claims

### Example 3: Filter Properties by Domain
```cypher
// Get high-priority properties for ancient history domain
MATCH (dp:DomainProfile {domain_id: 'ancient_history'})-[:PRIORITIZES]->(pm:PropertyMapping)
RETURN pm.property_id, pm.property_label, pm.primary_facet
ORDER BY pm.confidence DESC;
```

**Use Case:** Domain-specific property filtering

### Example 4: Multi-Facet Property Analysis
```cypher
// Find properties that span multiple facets (context-dependent)
MATCH (pm:PropertyMapping)-[:HAS_SECONDARY_FACET]->(:Facet)
WITH pm, size(split(pm.all_facets, ',')) as facet_count
WHERE facet_count >= 3
RETURN pm.property_id, pm.property_label, pm.all_facets, facet_count
ORDER BY facet_count DESC;
```

**Use Case:** Identify properties needing contextual routing

---

## Performance Notes

- **Import time:** ~2-3 minutes for 500 nodes
- **Index creation:** ~30 seconds
- **Total:** ~5 minutes

**After import:**
- Property lookup: O(1) via index
- Facet filtering: O(n) where n = properties per facet (~30 avg)
- Agent routing: 2-hop query (property→facet→agent)

---

## Integration with Chrystallum

### SCA Workflow Integration
```python
# When processing Wikidata statement
def process_statement(property_id, value, entity):
    # Lookup property mapping
    facet = get_property_facet(property_id)  # Query Neo4j
    
    # Route to appropriate agent
    agent = get_facet_agent(subject_id, facet)
    
    # Process with context
    agent.analyze_statement(property_id, value, entity)
```

### Federation Scoring
```python
# Calculate property priority score
def score_property(property_id, domain='ancient_history'):
    pm = get_property_mapping(property_id)
    
    score = pm.confidence  # Base 0.5-1.0
    
    if pm.is_authority_control:
        score += 0.2
    
    if pm.is_historical:
        score += 0.2
    
    if pm.primary_facet in ['MILITARY', 'POLITICAL', 'RELIGIOUS']:
        score += 0.1
    
    return min(score, 1.0)
```

---

## Next Steps

1. ✅ Import property mappings to Neo4j
2. ✅ Verify with test queries
3. ⏳ Expand to all 13,220 properties (currently 500)
4. ⏳ Implement multi-factor contextual routing
5. ⏳ Integrate with SCA workflow
6. ⏳ Add property scoring to federation

---

**Ready to import!** Run the Cypher script and verify with the test queries. 🚀
