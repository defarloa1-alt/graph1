# Period Enrichment with Perplexity

## Overview

This script analyzes periods from your Cypher import file using Perplexity AI to:
1. **Determine primary facets** for each period (Political, Cultural, Technological, etc.)
2. **Filter out events** that shouldn't be classified as periods
3. **Restructure edges** with proper facet relationships according to schema
4. **Generate clean Cypher** with proper `HAS_[FACET_TYPE]_FACET` relationships

## Setup

### Option 1: With Perplexity API (Recommended)

1. **Get Perplexity API Key:**
   - Sign up at https://www.perplexity.ai/
   - Get API key from dashboard

2. **Create config file:**
   ```python
   # config.py (create in project root)
   PERPLEXITY_API_KEY = "your-api-key-here"
   ```

3. **Install dependencies:**
   ```bash
   pip install requests
   ```

### Option 2: Without Perplexity API (Rule-Based)

The script will automatically fall back to rule-based classification if no API key is found. This uses keyword matching against period labels.

## Usage

```bash
python scripts/backbone/temporal/enrich_periods_with_perplexity.py
```

**Input:** `Subjects/periods_import.cypher`  
**Output:** `Subjects/periods_import_enriched.cypher`

## What It Does

### 1. Parses Periods
- Extracts all Period nodes from your Cypher file
- Captures: qid, label, start_year, end_year, current facets

### 2. Analyzes Each Period
- **With Perplexity:** Queries AI to determine primary facets and verify it's a period (not an event)
- **Without Perplexity:** Uses rule-based keyword matching

### 3. Filters Events
- Removes any items that are events (battles, wars, treaties, etc.)
- Events should be in Event nodes, not Period nodes

### 4. Restructures Edges
**Before (generic):**
```cypher
MERGE (f:Facet {label: 'historical period'})
MERGE (p)-[:HAS_FACET]->(f)
```

**After (typed facets):**
```cypher
MERGE (f:PoliticalFacet:Facet {unique_id: 'POLITICALFACET_political'})
SET f.label = 'political'
MERGE (p)-[:HAS_POLITICAL_FACET]->(f)
```

## Facet Types

The script maps periods to these facet types (from schema):

- `PoliticalFacet` - States, regimes, dynasties, governance
- `CulturalFacet` - Cultural eras, practices, identity
- `TechnologicalFacet` - Tool regimes, production technologies
- `ReligiousFacet` - Religious movements, institutions
- `EconomicFacet` - Economic systems, trade regimes
- `MilitaryFacet` - Warfare, conquests, military systems
- `ArchaeologicalFacet` - Material-culture periods
- `DiplomaticFacet` - International systems, alliances
- And more...

## Output Format

Each period block:
```cypher
MERGE (p:Period {qid: '...'}); 
SET p.label = '...'; 
SET p.start_year = 1482; 
MERGE (start:Year {value: 1482}); 
MERGE (p)-[:STARTS_IN]->(start); 
MERGE (f:PoliticalFacet:Facet {unique_id: 'POLITICALFACET_political'}); 
SET f.label = 'political'; 
MERGE (p)-[:HAS_POLITICAL_FACET]->(f);
```

## Example Output

```
================================================================================
Enriching Periods with Perplexity Analysis
================================================================================
Input: Subjects/periods_import.cypher
Output: Subjects/periods_import_enriched.cypher

📊 Step 1: Parsing periods from Cypher file...
   Found 1005 periods

🤖 Step 2: Analyzing periods with Perplexity...
   [1/1005] Analyzing: Prehistoric Brussels... Facets: ArchaeologicalFacet
   [2/1005] Analyzing: Habsburg Netherlands... Facets: PoliticalFacet, CulturalFacet
   [3/1005] Analyzing: Battle of Pharsalus... Facets: MilitaryFacet [EVENT - WILL SKIP]
   ...

📝 Step 3: Generating enriched Cypher file...
✅ Generated Subjects/periods_import_enriched.cypher with 950 periods

================================================================================
Summary
================================================================================
Total analyzed: 1005
Periods: 950
Events (filtered out): 55
✅ Enriched file ready: Subjects/periods_import_enriched.cypher
================================================================================
```

## Next Steps

1. **Review the enriched file:**
   ```bash
   # Check first few periods
   head -20 Subjects/periods_import_enriched.cypher
   ```

2. **Import to Neo4j:**
   ```cypher
   // In Neo4j Browser or cypher-shell
   :source Subjects/periods_import_enriched.cypher
   ```

3. **Verify facets:**
   ```cypher
   MATCH (p:Period)-[r]->(f:Facet)
   RETURN type(r), f.label, count(*) as count
   ORDER BY count DESC
   ```

## Troubleshooting

### "Perplexity API error"
- Check your API key in `config.py`
- Verify API key is valid
- Script will fall back to rule-based classification

### "No periods found"
- Check that `Subjects/periods_import.cypher` exists
- Verify file format matches expected pattern

### "Too many events filtered"
- Review the EVENT_KEYWORDS list in the script
- Adjust keywords if needed for your domain

## Schema Compliance

The output follows the schema defined in `Key Files/NODE_TYPE_SCHEMAS.md`:
- Uses typed facet nodes (`:PoliticalFacet`, `:CulturalFacet`, etc.)
- Uses specific relationship types (`HAS_POLITICAL_FACET`, etc.)
- Each facet has `unique_id` and `label` properties
- Properly structured for faceted search and filtering

