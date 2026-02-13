# What the LLM (Perplexity) Returns and Final Output

## What Perplexity Returns

When you query Perplexity for each period, it returns a JSON response like this:

```json
{
  "is_period": true,
  "is_event": false,
  "primary_facet": "PoliticalFacet",
  "confidence": 0.85
}
```

**Or for an event:**
```json
{
  "is_period": false,
  "is_event": true,
  "primary_facet": "MilitaryFacet",
  "confidence": 0.9
}
```

**Fields:**
- `is_period`: Boolean - Is this actually a period (not an event)?
- `is_event`: Boolean - Is this an event that should be filtered out?
- `primary_facet`: String - ONE facet type (e.g., "PoliticalFacet", "CulturalFacet")
- `confidence`: Float - How confident is the classification (0.0 to 1.0)

## What the Script Does

### Step 1: Parse Input File
Extracts from your current `periods_import.cypher`:
- Period QID
- Label
- Start year (if present)
- End year (if present)
- Location QID (if present)
- Current facet (if present)

### Step 2: Query Perplexity (or Use Rule-Based)
For each period, asks Perplexity:
> "What type of historical period is 'Habsburg Netherlands' (1482 to 1797)? What is the PRIMARY facet for this period? Choose ONE: Political, Cultural, Technological, Religious, Economic, Military, Archaeological, or other. Is this a period or an event?"

### Step 3: Validate Requirements
Checks each period against ALL requirements:
1. ✅ Not an event (`is_event == false`)
2. ✅ Has start_year
3. ✅ Has end_year
4. ✅ Has location_qid
5. ✅ End year >= -2000 (not before 2000 BCE)

### Step 4: Generate Enhanced Cypher
For each VALID period, generates properly structured Cypher.

## Complete Example: Input → LLM → Output

### Input (Your Current File)
```cypher
MERGE (p:Period {qid: '<http://www.wikidata.org/entity/Q1031430>'});
SET p.label = 'Habsburg Netherlands';
SET p.start_year = 1482;
SET p.end_year = 1797;
MERGE (start:Year {value: 1482});
MERGE (p)-[:STARTS_IN]->(start);
MERGE (end:Year {value: 1797});
MERGE (p)-[:ENDS_IN]->(end);
MERGE (f:Facet {label: 'historical period'});
MERGE (p)-[:HAS_FACET]->(f);
MERGE (geo:Place {qid: '<http://www.wikidata.org/entity/Q476033>'});
MERGE (p)-[:LOCATED_IN]->(geo);
```

### Perplexity Analysis
**Query:** "What type of historical period is 'Habsburg Netherlands' (1482 to 1797)? What is the PRIMARY facet? Is this a period or an event?"

**Response:**
```json
{
  "is_period": true,
  "is_event": false,
  "primary_facet": "PoliticalFacet",
  "confidence": 0.9
}
```

**Reasoning:** Habsburg Netherlands was a political entity (state/regime), so PRIMARY facet = PoliticalFacet

### Output (Enhanced File)
```cypher
MERGE (p:Period {qid: '<http://www.wikidata.org/entity/Q1031430>'});
SET p.label = 'Habsburg Netherlands';
SET p.start_year = 1482;
SET p.end_year = 1797;
MERGE (start:Year {value: 1482});
MERGE (p)-[:STARTS_IN]->(start);
MERGE (end:Year {value: 1797});
MERGE (p)-[:ENDS_IN]->(end);
MERGE (f:PoliticalFacet:Facet {unique_id: 'POLITICALFACET_political'});
SET f.label = 'political';
MERGE (p)-[:HAS_POLITICAL_FACET]->(f);
MERGE (geo:Place {qid: '<http://www.wikidata.org/entity/Q476033>'});
MERGE (p)-[:LOCATED_IN]->(geo);
```

**Key Changes:**
1. ✅ Generic `Facet {label: 'historical period'}` → Typed `PoliticalFacet:Facet {unique_id: '...'}`
2. ✅ Generic `HAS_FACET` → Specific `HAS_POLITICAL_FACET`
3. ✅ All requirements validated (dates, location, not event, not too old)

## Example: Event Gets Filtered Out

### Input
```cypher
MERGE (p:Period {qid: '<http://www.wikidata.org/entity/Q362>'});
SET p.label = 'World War II';
SET p.start_year = 1939;
SET p.end_year = 1945;
```

### Perplexity Analysis
**Response:**
```json
{
  "is_period": false,
  "is_event": true,
  "primary_facet": "MilitaryFacet",
  "confidence": 0.95
}
```

**Reasoning:** World War II is a war/event, not a time period

### Output
**❌ NOT INCLUDED** - Filtered out as event

## Example: Period Without Dates Gets Filtered

### Input
```cypher
MERGE (p:Period {qid: '<http://www.wikidata.org/entity/Q1038653>'});
SET p.label = 'Modern animation in the United States';
MERGE (f:Facet {label: 'history of animation'});
MERGE (p)-[:HAS_FACET]->(f);
```

### Perplexity Analysis
**Response:**
```json
{
  "is_period": true,
  "is_event": false,
  "primary_facet": "CulturalFacet",
  "confidence": 0.8
}
```

### Output
**❌ NOT INCLUDED** - Missing start_year AND end_year

## Example: Period Too Old Gets Filtered

### Input
```cypher
MERGE (p:Period {qid: '<http://www.wikidata.org/entity/Q109386511>'});
SET p.label = 'Early Dynastic III';
SET p.start_year = 2599;
SET p.end_year = 2339;  // Before 2000 BCE
```

### Perplexity Analysis
**Response:**
```json
{
  "is_period": true,
  "is_event": false,
  "primary_facet": "ArchaeologicalFacet",
  "confidence": 0.85
}
```

### Output
**❌ NOT INCLUDED** - End year (-2339) is before 2000 BCE (-2000)

## Summary: What You Get

### Input File (`periods_import.cypher`)
- **1005 periods** (raw, unfiltered) ✅ Verified
- Generic facets: `Facet {label: 'historical period'}`
- Generic relationships: `HAS_FACET`
- Mixed quality: some missing dates, some events, some too old

### Output File (`periods_import_enriched.cypher`)
- **~700-800 periods** (filtered, validated)
- **Typed primary facets:** `PoliticalFacet`, `CulturalFacet`, `MilitaryFacet`, etc.
- **Specific relationships:** `HAS_POLITICAL_FACET`, `HAS_CULTURAL_FACET`, etc.
- **All validated:**
  - ✅ Not events
  - ✅ Have start_year AND end_year
  - ✅ Have location (Place node)
  - ✅ End >= 2000 BCE
  - ✅ Have primary facet assigned

## The LLM's Role

**Perplexity determines:**
1. **Primary Facet** - Which ONE facet type best describes this period?
2. **Is Event?** - Is this actually an event that should be filtered out?

**The script handles:**
- Date validation
- Location validation
- Date range filtering (2000 BCE cutoff)
- Cypher generation with proper structure

## Final Output Structure

Each period in the enriched file follows this pattern:

```cypher
MERGE (p:Period {qid: '...'}); 
SET p.label = '...'; 
SET p.start_year = YYYY; 
SET p.end_year = YYYY; 
MERGE (start:Year {value: YYYY}); 
MERGE (p)-[:STARTS_IN]->(start); 
MERGE (end:Year {value: YYYY}); 
MERGE (p)-[:ENDS_IN]->(end); 
MERGE (f:[PRIMARY_FACET_TYPE]:Facet {unique_id: '...'}); 
SET f.label = '...'; 
MERGE (p)-[:HAS_[FACET_TYPE]_FACET]->(f); 
MERGE (geo:Place {qid: '...'}); 
MERGE (p)-[:LOCATED_IN]->(geo);
```

Where `[PRIMARY_FACET_TYPE]` is determined by Perplexity (e.g., `PoliticalFacet`, `CulturalFacet`).

