# Advice: Preserving Multi-Facet Period Data

## The Issue

The original file had **1005 period entries**, but many were duplicates with different facets:

**Example: Same period, multiple instance of classifications**
```
Habsburg Netherlands:
  - facet: 'historical period'
  - facet: 'historical country'
  - facet: 'dynasty'

Byzantine Empire:
  - facet: 'historical period'
  - facet: 'empire'
  - facet: 'civilization'
```

**What we're losing:** These multiple facets represent different Wikidata P31 (instance of) values - they're valuable multi-dimensional classifications!

## Current Approach (Losing Data)

**Current script:**
- Assigns ONE primary facet per period
- Filters out duplicates
- Result: 118 unique periods with single facet each

**Problem:**
- âŒ Loses rich multi-facet data
- âŒ Period can be both 'political' AND 'cultural'
- âŒ Can't query "find periods that are both dynasties and historical countries"

## Recommended Solution: Keep ALL Facets

### Option 1: Modify Script to Keep Multiple Facets (Recommended)

Update `enrich_periods_with_perplexity.py` to:

1. **Group duplicates by QID:**
```python
# Group periods by QID
period_groups = {}
for period in parsed_periods:
    qid = period['qid']
    if qid not in period_groups:
        period_groups[qid] = {
            'qid': qid,
            'label': period['label'],
            'start_year': period.get('start_year'),
            'end_year': period.get('end_year'),
            'location_qid': period.get('location_qid'),
            'facets': []
        }
    # Collect all facets for this period
    if period.get('current_facet'):
        period_groups[qid]['facets'].append(period['current_facet'])
```

2. **Map each facet to typed facet:**
```python
facet_mapping = {
    'historical period': 'CulturalFacet',
    'historical country': 'PoliticalFacet',
    'dynasty': 'PoliticalFacet',
    'empire': 'PoliticalFacet',
    'civilization': 'CulturalFacet',
    'archaeological period': 'ArchaeologicalFacet',
    'war': 'MilitaryFacet',  # But filter if it's an event
    # etc.
}
```

3. **Create multiple facet relationships:**
```cypher
MERGE (p:Period {qid: '...'})
SET p.label = 'Byzantine Empire'
SET p.start_year = 330
SET p.end_year = 1453
MERGE (start:Year {value: 330})
MERGE (p)-[:STARTS_IN]->(start)
MERGE (end:Year {value: 1453})
MERGE (p)-[:ENDS_IN]->(end)
// Multiple facets!
MERGE (f1:PoliticalFacet:Facet {unique_id: 'POLITICALFACET_political'})
MERGE (p)-[:HAS_POLITICAL_FACET]->(f1)
MERGE (f2:CulturalFacet:Facet {unique_id: 'CULTURALFACET_cultural'})
MERGE (p)-[:HAS_CULTURAL_FACET]->(f2)
MERGE (geo:Place {qid: '...'})
MERGE (p)-[:LOCATED_IN]->(geo);
```

### Option 2: Two-Pass Approach (Quick Fix)

1. **Keep current enriched file** (386 periods with primary facets)
2. **Create supplementary facet file** from original duplicates
3. **Import both**

### Option 3: Manual Facet Mapping (Most Control)

Extract the original facet labels and create a mapping file:

```csv
qid,original_facet,typed_facet
Q12544,historical period,CulturalFacet
Q12544,empire,PoliticalFacet
Q12544,civilization,CulturalFacet
```

Then import additional facets separately.

## Recommendation

**Best approach: Modify the script** to keep ALL facets (Option 1)

**Why:**
- Preserves all Wikidata instance of data
- Allows multi-dimensional classification
- Enables richer queries
- Still validates (dates, location, not event, date range)

**Changes needed in script:**
1. Group periods by QID (not treat each as separate)
2. Collect ALL facets for each period
3. Map original facet labels to typed facets
4. Create multiple HAS_[FACET_TYPE]_FACET relationships

**Result:**
- 118 unique periods (current)
- Multiple facets per period (new!)
- All validation still applied
- Richer classification

## Quick Fix for Now

If you want to keep the current 118 periods but add more facets later:

```cypher
// Keep what you have, add more facets later
MATCH (p:Period {qid: 'Q12544'})
MERGE (f:PoliticalFacet:Facet {unique_id: 'POLITICALFACET_political'})
MERGE (p)-[:HAS_POLITICAL_FACET]->(f)
```

## What to Do

1. **Keep current 118 periods** - they're valid with primary facets
2. **I can modify the script** to preserve ALL facets from duplicates
3. **Re-run enrichment** to get full multi-facet data

Want me to update the script to keep multiple facets per period?


