# What the Enhanced Cypher File Contains

## Overview

The script takes your current `periods_import.cypher` and produces an **enhanced and slimmed down** version: `periods_import_enriched.cypher`

## What Gets Removed (Slimmed Down)

### 1. Events (Not Periods)
**Before:**
```cypher
MERGE (p:Period {qid: '<http://www.wikidata.org/entity/Q362>'})
SET p.label = 'World War II'
```
**Action:** ❌ REMOVED (this is an event, not a period)

### 2. Periods Without Both Dates
**Before:**
```cypher
MERGE (p:Period {qid: '...'})
SET p.label = 'Modern animation in the United States'
// No start_year or end_year
```
**Action:** ❌ REMOVED (missing required dates)

### 3. Periods Without Location
**Before:**
```cypher
MERGE (p:Period {qid: '...'})
SET p.label = 'Some Period'
// No Place node with LOCATED_IN
```
**Action:** ❌ REMOVED (missing location)

### 4. Periods Ending Before 2000 BCE
**Before:**
```cypher
MERGE (p:Period {qid: '...'})
SET p.label = 'Early Dynastic Period'
SET p.end_year = -2339  // Before 2000 BCE
```
**Action:** ❌ REMOVED (too old)

## What Gets Enhanced

### 1. Primary Facet Assignment (LLM Contribution)

**What Perplexity Does:**
- Analyzes each period's label and context
- Determines the **PRIMARY facet** (Political, Cultural, Military, etc.)
- Verifies it's actually a period (not an event)

**Before (Generic):**
```cypher
MERGE (f:Facet {label: 'historical period'})
MERGE (p)-[:HAS_FACET]->(f)
```

**After (Typed, Primary Facet):**
```cypher
MERGE (f:PoliticalFacet:Facet {unique_id: 'POLITICALFACET_political'})
SET f.label = 'political'
MERGE (p)-[:HAS_POLITICAL_FACET]->(f)
```

### 2. Proper Structure

**Before:**
```cypher
MERGE (p:Period {qid: '...'}); SET p.label = 'Habsburg Netherlands'; SET p.start_year = 1482; SET p.end_year = 1797; MERGE (end:Year {value: 56}); MERGE (p)-[:ENDS_IN]->(end); MERGE (f:Facet {label: 'historical period'}); MERGE (p)-[:HAS_FACET]->(f);
```

**After (Enhanced):**
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

## Complete Example: Before vs After

### Input (Current File)
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
1. ✅ Generic `Facet` → Typed `PoliticalFacet`
2. ✅ Generic `HAS_FACET` → Specific `HAS_POLITICAL_FACET`
3. ✅ Added `unique_id` to facet node
4. ✅ All requirements validated (dates, location, not event, not too old)

## What Perplexity Returns

When you query Perplexity for a period, it returns:

```json
{
  "is_period": true,
  "is_event": false,
  "primary_facet": "PoliticalFacet",
  "confidence": 0.85
}
```

**The script then:**
1. Uses `primary_facet` to create typed facet node
2. Uses `is_event` to filter out events
3. Validates dates, location, date range
4. Generates properly structured Cypher

## Summary: What You Get

### Input File
- **1005 periods** (raw, unfiltered) ✅ Verified
- Generic facets
- Some missing dates/locations
- Some events mixed in
- Some too old (before 2000 BCE)

### Output File
- **~700-800 periods** (filtered, validated)
- Typed primary facets (PoliticalFacet, CulturalFacet, etc.)
- All have start_year AND end_year
- All have location (Place node)
- All end >= 2000 BCE
- No events
- Proper schema-compliant structure

## File Comparison

| Metric | Input File | Output File |
|--------|-----------|-------------|
| Total periods | 1005 ✅ Verified | ~700-800 (estimated after filtering) |
| Events removed | 0 | ~50-100 |
| Missing dates removed | 0 | ~30-50 |
| Missing location removed | 0 | ~45-75 |
| Too old removed | 0 | ~30-50 |
| Facet structure | Generic | Typed (15 types) |
| Schema compliance | Partial | Full |

## Next Steps

1. **Run the script:**
   ```bash
   python scripts/backbone/temporal/enrich_periods_with_perplexity.py
   ```

2. **Review output:**
   - Check how many periods were filtered
   - Verify facet assignments look correct
   - Spot-check a few periods

3. **Import to Neo4j:**
   ```cypher
   :source Subjects/periods_import_enriched.cypher
   ```

4. **Query with facets:**
   ```cypher
   MATCH (p:Period)-[:HAS_POLITICAL_FACET]->(f:PoliticalFacet)
   RETURN p.label, p.start_year, p.end_year
   LIMIT 10
   ```

