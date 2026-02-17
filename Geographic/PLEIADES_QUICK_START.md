# Pleiades Geographic Data - Quick Start Guide

## What is Pleiades?

Pleiades (https://pleiades.stoa.org) is a gazetteer of ancient places, maintained by the Institute for the Study of the Ancient World (ISAW). It provides:
- **~40,000 ancient places** (Mediterranean, Near East, Europe, North Africa)
- **Historical names** in multiple languages (Latin, Greek, etc.)
- **Temporal bounds** (approximate date ranges when places existed)
- **Coordinates** with precision indicators
- **Authority URIs** for stable citations

## Quick Start (3 Steps)

### Step 1: Download Pleiades Bulk Data (~5-10 minutes)

```powershell
# From C:\Projects\Graph1
python scripts/backbone/geographic/download_pleiades_bulk.py
```

**What this does:**
- Downloads 3 CSV files from Pleiades (~45 MB total compressed)
  - `pleiades-places-latest.csv.gz` (6.3 MB) - Core places
  - `pleiades-names-latest.csv.gz` (3.4 MB) - Historical names
  - `pleiades-locations-latest.csv.gz` (35 MB) - Coordinates
- Extracts to `Geographic/temp/`
- Processes into Neo4j-ready CSVs in `Geographic/`:
  - `pleiades_places.csv`
  - `pleiades_names.csv`
  - `pleiades_coordinates.csv`

**Expected output:**
```
✓ Places: 38,000+ processed
✓ Names: 95,000+ processed
✓ Locations: 42,000+ processed
```

### Step 2: Import to Neo4j (~2-5 minutes)

```powershell
# Full import
python scripts/backbone/geographic/import_pleiades_to_neo4j.py

# Or test with limited dataset first
python scripts/backbone/geographic/import_pleiades_to_neo4j.py --limit 1000
```

**What this does:**
- Creates schema (constraints + indexes)
- Imports `:Place` nodes with Pleiades IDs
- Links `:PlaceName` nodes (historical names)
- Links `:Location` nodes (coordinates)

**Schema created:**
```cypher
(:Place {
  pleiades_id: "423025",
  label: "Roma",
  description: "An ancient city...",
  place_type: "settlement",
  lat: 41.891775,
  long: 12.486137,
  min_date: -1000,
  max_date: 2100,
  uri: "https://pleiades.stoa.org/places/423025",
  authority: "Pleiades",
  confidence: 0.90
})

(:PlaceName {
  name_id: "423025_1",
  name_attested: "Ῥώμη",
  language: "grc",
  name_type: "geographic",
  romanized: "Rhōmē"
})

(:Location {
  location_id: "423025_loc",
  lat: 41.891775,
  long: 12.486137,
  precision: "precise"
})

(Place)-[:HAS_NAME]->(PlaceName)
(Place)-[:HAS_LOCATION]->(Location)
```

### Step 3: Verify Import

```cypher
// Count places
MATCH (p:Place) RETURN count(p)

// Find Rome
MATCH (p:Place) WHERE p.label CONTAINS 'Rom' RETURN p LIMIT 5

// Places with Greek names
MATCH (p:Place)-[:HAS_NAME]->(n:PlaceName)
WHERE n.language = 'grc'
RETURN p.label, n.name_attested
LIMIT 10

// Places in Italy (rough bounding box)
MATCH (p:Place)
WHERE p.lat > 36 AND p.lat < 47
  AND p.long > 6 AND p.long < 19
RETURN p.label, p.place_type, p.lat, p.long
LIMIT 20

// Ancient places (before 500 CE)
MATCH (p:Place)
WHERE p.max_date IS NOT NULL AND p.max_date < 500
RETURN p.label, p.min_date, p.max_date
ORDER BY p.min_date
LIMIT 10
```

## Data Quality & Coverage

### Geographic Coverage
- **Mediterranean Basin:** Comprehensive (Italy, Greece, Turkey, Egypt, North Africa)
- **Roman Empire:** Very strong coverage
- **Ancient Near East:** Good coverage (Mesopotamia, Levant, Persia)
- **Northern Europe:** Moderate (Roman provinces: Gaul, Britain, Germania)

### Temporal Coverage
- **Classical Antiquity:** Primary focus (1000 BCE - 500 CE)
- **Bronze Age:** Some coverage (Minoan, Mycenaean sites)
- **Medieval:** Limited (Byzantine era only)
- **Modern:** Not a focus

### Data Types
- **~38,000 places** with Pleiades IDs
- **~95,000 name variants** (Latin, Greek, Ancient Egyptian, etc.)
- **~42,000 coordinate sets** (varying precision)
- **~30,000 with temporal bounds** (min_date/max_date)

## Integration with Chrystallum

### Authority Confidence
- Base confidence: **0.90** (Pleiades is peer-reviewed)
- Tier: **Layer 2** (Federation authority)
- Comparable to Wikidata, higher than GeoNames (modern only)

### Use Cases

**1. Period Triage Workflow (Geographic Normalization)**
```python
# scripts/backbone/temporal/period_triage.py
def normalize_period_region(region_string: str) -> str:
    """Map PeriodO region string to canonical Place."""
    # Query Pleiades for match
    query = """
    MATCH (p:Place)
    WHERE p.label =~ $regex OR p.description CONTAINS $region
    RETURN p.pleiades_id, p.label, p.uri
    LIMIT 5
    """
    # Returns: pleiades_id for canonical linkage
```

**2. Event Location Validation**
```cypher
// Link Event -> Place via Pleiades
MATCH (e:Event {label: "Battle of Cannae"})
MATCH (p:Place {pleiades_id: "442800"}) // Cannae
MERGE (e)-[:OCCURRED_AT]->(p)
```

**3. Legal Domain (OJ Simpson Trial)**
```cypher
// Create Place for courthouse
MATCH (p:Place)
WHERE p.label CONTAINS 'Los Angeles'
  AND p.min_date IS NULL // Modern place (no ancient bounds)
RETURN p
// Note: Pleiades won't have this (modern).
// Fallback: GeoNames or manual Place node
```

**4. Facet Linking (Geographic Agent)**
```python
# Geographic facet queries Pleiades for place types
MATCH (p:Place)
WHERE p.place_type IN ['settlement', 'temple', 'province']
RETURN p.pleiades_id, p.label, p.place_type
```

## Performance Characteristics

### Import Times (Full Dataset)
- Download: ~5 minutes (depends on network)
- Processing: ~2 minutes
- Neo4j import: ~3 minutes
- **Total: ~10 minutes** for complete ancient geography backbone

### Query Performance (with indexes)
- Pleiades ID lookup: <10ms
- Label search: <50ms
- Bounding box search: <100ms
- Name variant search: <150ms

## Maintenance

### Update Frequency
Pleiades bulk exports update **daily** at:
`https://atlantides.org/downloads/pleiades/dumps/pleiades-*-latest.csv.gz`

### Re-import Process
```powershell
# Download latest data
python scripts/backbone/geographic/download_pleiades_bulk.py

# Clear existing Pleiades data
# (Neo4j Browser or cypher-shell)
MATCH (p:Place {authority: 'Pleiades'})
DETACH DELETE p

# Re-import
python scripts/backbone/geographic/import_pleiades_to_neo4j.py
```

## Known Limitations

### Not Covered by Pleiades
1. **Modern places** (use GeoNames for cities post-500 CE)
2. **Americas, East Asia, Sub-Saharan Africa** (use regional gazetteers)
3. **Non-archaeological sites** (e.g., modern courthouses → manual creation)

### Workarounds
- **Missing modern places:** Create manual `:Place` nodes with `authority: 'Manual'`
- **Incomplete coordinates:** Some ancient places have approximate locations only
- **Name variants:** Not all languages represented (focus on Greek, Latin, Ancient Egyptian)

## Next Steps After Import

1. **Link to Periods:**
   ```cypher
   MATCH (p:Place), (per:Period)
   WHERE p.min_date >= per.begin_year
     AND p.max_date <= per.end_year
   MERGE (p)-[:EXISTED_DURING]->(per)
   ```

2. **Link to Events:**
   ```cypher
   MATCH (e:Event {label: 'Battle of Actium'})
   MATCH (p:Place {pleiades_id: '295374'})
   MERGE (e)-[:OCCURRED_AT]->(p)
   ```

3. **Link to SubjectConcepts:**
   ```cypher
   MATCH (sc:SubjectConcept {label: 'Roman Republic'})
   MATCH (p:Place {label: 'Roma'})
   MERGE (sc)-[:LOCATED_IN]->(p)
   ```

4. **Enable Geographic Facet Queries:**
   - See `facet_agent_system_prompts.json` → "GEOGRAPHIC" facet
   - Place nodes now queryable for facet enrichment

## Troubleshooting

### CSV Import Errors
```
Neo4j.ClientError.Statement.SyntaxError: Invalid input
```
**Fix:** Ensure CSV files use absolute paths or are in Neo4j import directory
```powershell
# Copy to Neo4j import folder (if needed)
Copy-Item Geographic\pleiades_*.csv $env:NEO4J_HOME\import\
```

### Missing Data After Import
```
✓ Imported 0 places
```
**Fix:** Check CSV file exists and has content
```powershell
Get-Content Geographic\pleiades_places.csv -Head 5
```

### Performance Issues
```
Import taking >10 minutes
```
**Fix:** Use `--limit 1000` to test subset first, then run full import

## References

- **Pleiades Homepage:** https://pleiades.stoa.org
- **Downloads Page:** https://atlantides.org/downloads/pleiades/dumps/
- **Documentation:** https://pleiades.stoa.org/downloads
- **API Docs:** https://pleiades.stoa.org/help/api (for per-place JSON lookups)
- **Chrystallum Architecture:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` § 4.4 (Geographic Integration)
