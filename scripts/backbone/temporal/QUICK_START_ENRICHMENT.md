# Quick Start: Period Enrichment with Perplexity

## ✅ Ready to Use

The script is ready! It successfully parsed **1005 periods** from your file.

## Quick Start (3 Steps)

### Step 1: Test Parsing (Already Done ✅)
```bash
python scripts/backbone/temporal/test_period_parsing.py
```
✅ Confirmed: 1005 periods found

### Step 2: Run Enrichment

**Option A: With Perplexity API (More Accurate)**
1. Get API key from https://www.perplexity.ai/
2. Create `config.py`:
   ```python
   PERPLEXITY_API_KEY = "your-key-here"
   ```
3. Run:
   ```bash
   python scripts/backbone/temporal/enrich_periods_with_perplexity.py
   ```
   ⏱️ Takes ~15-30 minutes for 1005 periods

**Option B: Without API (Rule-Based, Instant)**
```bash
python scripts/backbone/temporal/enrich_periods_with_perplexity.py
```
- Works without API key
- Uses keyword matching
- Less accurate but fast
- Good for initial pass

### Step 3: Import to Neo4j
```cypher
// In Neo4j Browser
:source Subjects/periods_import_enriched.cypher
```

## What You'll Get

### Before (Current):
```cypher
MERGE (f:Facet {label: 'historical period'})
MERGE (p)-[:HAS_FACET]->(f)
```

### After (Enriched):
```cypher
MERGE (f:PoliticalFacet:Facet {unique_id: 'POLITICALFACET_political'})
SET f.label = 'political'
MERGE (p)-[:HAS_POLITICAL_FACET]->(f)
```

## Benefits

1. ✅ **Proper Facet Structure** - Typed facets per schema
2. ✅ **Event Filtering** - Removes battles/wars that aren't periods
3. ✅ **Schema Compliance** - Matches NODE_TYPE_SCHEMAS.md
4. ✅ **Better Queries** - Easy faceted search

## Sample Output

The script will:
- Analyze each period
- Assign 1-2 primary facets
- Filter out events
- Generate clean Cypher

Example output:
```
[1/1005] Analyzing: Prehistoric Brussels... Facets: ArchaeologicalFacet
[2/1005] Analyzing: Habsburg Netherlands... Facets: PoliticalFacet, CulturalFacet
[3/1005] Analyzing: Battle of Pharsalus... Facets: MilitaryFacet [EVENT - WILL SKIP]
...
✅ Generated Subjects/periods_import_enriched.cypher with 950 periods
```

## Files Created

- ✅ `scripts/backbone/temporal/enrich_periods_with_perplexity.py` - Main script
- ✅ `scripts/backbone/temporal/test_period_parsing.py` - Test script
- ✅ `scripts/backbone/temporal/README_PERIOD_ENRICHMENT.md` - Full docs
- ✅ `scripts/backbone/temporal/ADVICE_PERIOD_ENRICHMENT.md` - Detailed advice
- ✅ `config.py.example` - Config template

## Next Steps

1. **Run enrichment** (choose API or rule-based)
2. **Review output** - Check a few periods look correct
3. **Import to Neo4j** - Use the enriched file
4. **Test queries** - Try faceted search queries

## Questions?

See `ADVICE_PERIOD_ENRICHMENT.md` for:
- Cost considerations
- Troubleshooting
- Manual classification options
- Query examples

