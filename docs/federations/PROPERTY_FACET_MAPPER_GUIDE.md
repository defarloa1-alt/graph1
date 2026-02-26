# Property → Facet Automatic Mapper

## What This Does

Automatically maps Wikidata properties to Chrystallum's 18 facets by:
1. Querying each property's P31 (instance of) classifications
2. Matching against 500 known property types
3. Assigning to facets based on property type semantics

**Result:** Instant property→facet routing for federation!

---

## Quick Start

### Test with Sample Properties (Default)
```powershell
python map_properties_to_facets.py
```

Processes 18 test properties:
- P31 (instance of)
- P39 (position held)
- P580 (start time)
- P625 (coordinate location)
- And more...

### Process Your Properties CSV
```powershell
python map_properties_to_facets.py --input CSV/wikiPvalues.csv --limit 100
```

### Process Specific Properties
```powershell
python map_properties_to_facets.py --properties P31 P39 P106 P27 P580 P582
```

---

## Input Formats

### From CSV
Your CSV must have a column with property IDs. Supported column names:
- `property_id`
- `pid`  
- `property`

**Example CSV:**
```csv
property_id,label,count
P31,instance of,12450
P39,position held,8234
P106,occupation,7890
```

### From Command Line
```powershell
--properties P31 P39 P580 P625 P17
```

---

## Output Format

**File:** `CSV/property_mappings/property_facet_mapping_YYYYMMDD_HHMMSS.csv`

**Columns:**
- `property_id` - Wikidata property (P39)
- `property_label` - Property name ("position held")
- `property_description` - What it describes
- `type_qids` - P31 classifications (comma-separated)
- `type_labels` - Human-readable type names
- `primary_facet` - Best matching Chrystallum facet
- `secondary_facets` - Other matching facets
- `all_facets` - All facet matches
- `is_historical` - True if relevant to historical periods
- `is_authority_control` - True if authority control property
- `confidence` - Mapping confidence (0.0-1.0)
- `type_count` - Number of P31 values

---

## Example Output

```csv
property_id,property_label,primary_facet,all_facets,is_historical,confidence
P39,position held,POLITICAL,"POLITICAL,BIOGRAPHIC",False,0.8
P580,start time,BIOGRAPHIC,BIOGRAPHIC,False,0.8
P625,coordinate location,GEOGRAPHIC,GEOGRAPHIC,False,0.8
P106,occupation,BIOGRAPHIC,BIOGRAPHIC,False,0.8
```

---

## Facet Mapping Rules

The script uses 500 property type classifications to map to 18 facets:

### Core Facets Mapped
- **MILITARY** (2 property types)
- **POLITICAL** (4 property types)
- **RELIGIOUS** (8 property types)
- **GEOGRAPHIC** (5 property types)
- **INTELLECTUAL** (7 property types)
- **ARTISTIC** (5 property types)
- **ARCHAEOLOGICAL** (3 property types)
- **ECONOMIC** (3 property types)
- **DEMOGRAPHIC** (3 property types)
- **CULTURAL** (4 property types)
- **SCIENTIFIC** (6 property types)
- **LINGUISTIC** (5 property types)
- **BIOGRAPHIC** (5 property types)
- **DIPLOMATIC** (2 property types)
- **TECHNOLOGICAL** (2 property types)
- **ENVIRONMENTAL** (2 property types)
- **SOCIAL** (1 property type)

### Special Flags
- `is_historical` - Property types related to Ancient World, Middle Ages, Renaissance, Early Modern
- `is_authority_control` - Authority control properties (higher federation value)

---

## Confidence Scoring

```
Base:           0.5
+ Facet match:  0.8
+ Historical:   +0.2
+ Authority:    +0.2
Max:            1.0
```

---

## Use Cases

### 1. Federation Property Routing
```python
# When processing Wikidata property
property_facet = get_facet_for_property("P39")
# -> "POLITICAL"

# Route to appropriate agent
agent = get_agent_for_facet(property_facet)
```

### 2. Filter Properties by Facet
```cypher
// Load mapping to Neo4j
LOAD CSV WITH HEADERS FROM 'file:///property_facet_mapping.csv' AS row
CREATE (:PropertyMapping {
  property_id: row.property_id,
  primary_facet: row.primary_facet,
  confidence: toFloat(row.confidence)
})

// Query: Get all MILITARY properties
MATCH (pm:PropertyMapping {primary_facet: 'MILITARY'})
RETURN pm.property_id
```

### 3. Prioritize Historical Properties
```python
# Filter for historical research
historical_props = df[df['is_historical'] == True]
# These properties are most relevant for Ancient/Medieval history
```

---

## Performance

- **Rate limit:** 0.5 seconds per property
- **100 properties:** ~1-2 minutes
- **500 properties:** ~5-10 minutes
- **1000+ properties:** Consider batching

---

## Next Steps

1. Run on your full property list (`wikiPvalues.csv` - 13,220 properties)
2. Generate complete property→facet mapping
3. Import to Neo4j as `PropertyMapping` nodes
4. Use for automatic federation routing

---

**Ready to process your full property catalog?** 🚀
