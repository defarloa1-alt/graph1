# Advice: Period Enrichment Strategy

## Recommended Approach

### Phase 1: Test Parsing (5 minutes)
```bash
python scripts/backbone/temporal/test_period_parsing.py
```
Verify the script can read your periods file correctly.

### Phase 2: Run Enrichment (15-30 minutes)
```bash
python scripts/backbone/temporal/enrich_periods_with_perplexity.py
```

**With Perplexity API:**
- More accurate facet classification
- Better event detection
- Handles edge cases better
- ~15-30 minutes for 1000 periods (with rate limiting)

**Without Perplexity (Rule-Based):**
- Faster (instant)
- Less accurate but still useful
- Good for initial pass
- Can refine manually later

### Phase 3: Review & Refine (30 minutes)

1. **Check filtered events:**
   ```bash
   # Look for "EVENT - WILL SKIP" in output
   # Verify these should indeed be events, not periods
   ```

2. **Review facet assignments:**
   ```bash
   # Open enriched file and spot-check a few periods
   # Verify facets make sense
   ```

3. **Manual corrections:**
   - If a period got wrong facets, edit the enriched file
   - If an event was missed, add it to EVENT_KEYWORDS list

### Phase 4: Import (5 minutes)
```cypher
// In Neo4j Browser
:source Subjects/periods_import_enriched.cypher
```

## Key Benefits

### 1. Proper Facet Structure
**Before:**
- Generic `:Facet` nodes with labels
- Generic `HAS_FACET` relationships
- Hard to query by facet type

**After:**
- Typed facet nodes (`:PoliticalFacet`, `:CulturalFacet`)
- Specific relationships (`HAS_POLITICAL_FACET`, `HAS_CULTURAL_FACET`)
- Easy faceted search and filtering

### 2. Event Filtering
- Removes battles, wars, treaties that shouldn't be periods
- Keeps only true temporal periods
- Events should be in `:Event` nodes, not `:Period` nodes

### 3. Schema Compliance
- Matches `NODE_TYPE_SCHEMAS.md` specification
- Enables proper faceted search
- Supports multi-dimensional classification

## Query Examples After Import

### Find all political periods:
```cypher
MATCH (p:Period)-[:HAS_POLITICAL_FACET]->(f:PoliticalFacet)
RETURN p.label, p.start_year, p.end_year
ORDER BY p.start_year
```

### Find periods with multiple facets:
```cypher
MATCH (p:Period)-[r]->(f:Facet)
WITH p, collect(type(r)) as facets
WHERE size(facets) > 1
RETURN p.label, facets
```

### Filter by facet type:
```cypher
MATCH (p:Period)-[:HAS_CULTURAL_FACET]->(f:CulturalFacet)
WHERE p.start_year >= 1400 AND p.end_year <= 1600
RETURN p.label, p.start_year, p.end_year
```

## Cost Considerations

### Perplexity API
- **Free tier:** Limited requests
- **Paid tier:** ~$0.001-0.002 per period
- **1000 periods:** ~$1-2
- **Alternative:** Use rule-based (free, less accurate)

### Recommendation
1. **Start with rule-based** to see results
2. **Use Perplexity for edge cases** manually
3. **Or use Perplexity for full run** if budget allows

## Troubleshooting

### "Too many periods filtered as events"
- Review `EVENT_KEYWORDS` in script
- Some periods legitimately contain words like "war" (e.g., "Cold War" is a period)
- Adjust keywords or manually review filtered items

### "Facets don't match expectations"
- Perplexity may classify differently than you expect
- Review a sample and adjust `FACET_TYPES` keywords if needed
- Or manually correct in enriched file

### "Script is slow"
- Perplexity API has rate limits
- Script includes 0.5s delay between requests
- For 1000 periods: ~8-10 minutes minimum
- Consider batch processing or using rule-based for speed

## Alternative: Manual Classification

If you prefer manual control:

1. **Export periods to CSV:**
   ```python
   # Quick script to export
   periods = parse_periods_from_cypher("Subjects/periods_import.cypher")
   # Write to CSV with columns: qid, label, start_year, end_year, facet1, facet2
   ```

2. **Classify in spreadsheet:**
   - Add facet columns
   - Use dropdowns for facet types
   - Mark events to exclude

3. **Import back:**
   ```python
   # Script to read CSV and generate Cypher
   ```

## Next Steps After Enrichment

1. **Create facet index:**
   ```cypher
   CREATE INDEX facet_unique_id IF NOT EXISTS FOR (f:Facet) ON (f.unique_id);
   ```

2. **Verify relationships:**
   ```cypher
   MATCH (p:Period)-[r]->(f:Facet)
   RETURN type(r), count(*) as count
   ORDER BY count DESC;
   ```

3. **Test faceted search:**
   ```cypher
   // Find all periods with both political and cultural facets
   MATCH (p:Period)-[:HAS_POLITICAL_FACET]->(:PoliticalFacet)
   MATCH (p)-[:HAS_CULTURAL_FACET]->(:CulturalFacet)
   RETURN p.label, p.start_year, p.end_year
   LIMIT 10;
   ```

