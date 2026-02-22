# Fresh Chrystallum Instance Rebuild Guide

**Date:** 2026-02-19  
**Status:** Ready to Execute  
**Target:** Brand new Neo4j Chrystallum instance  
**Strategy:** Clean rebuild - Temporal first, then Geographic

---

## 🎯 **Rebuild Strategy**

**Philosophy:** Start fresh, build clean, validate at each stage

**Order:**
1. **Schema & Constraints** - Set up the foundation
2. **Temporal Backbone** - Years (-2000 to 2025) + Hierarchy
3. **Periods** - PeriodO canonical periods + facet classification
4. **Geographic Backbone** - Places (Pleiades) + Hierarchy
5. **Verification** - Validate each stage before proceeding

**Why This Order:**
- Temporal first because EVERYTHING needs temporal grounding
- Periods depend on Year nodes
- Geographic can reference Period nodes for temporal context
- Each stage validates before moving forward

---

## 📋 **Prerequisites**

### 1. Neo4j Instance Ready
- ✅ New Chrystallum instance created
- ✅ Neo4j running (version 5.x recommended)
- ✅ Default database name confirmed (use `chrystallum` or `neo4j`)

### 2. Environment Variables Set
```powershell
# Set these first
$env:NEO4J_URI = "bolt://localhost:7687"
$env:NEO4J_USERNAME = "neo4j"
$env:NEO4J_PASSWORD = "YourPasswordHere"
$env:NEO4J_DATABASE = "chrystallum"  # Or "neo4j" if using default
```

### 3. Verify Connectivity
```powershell
# Quick connection test
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '$env:NEO4J_PASSWORD')); driver.verify_connectivity(); print('Connected!'); driver.close()"
```

---

## 🏗️ **Stage 1: Schema & Constraints**

### Purpose
Set up constraints and indexes before loading data (much faster than adding after).

### Execution

**Option A: Run pre-built schema files**
```powershell
# Neo4j 5.x compatible constraints
python Neo4j/schema/run_cypher_file.py Neo4j/schema/01_schema_constraints_neo5_compatible.cypher

# Indexes for performance
python Neo4j/schema/run_cypher_file.py Neo4j/schema/02_schema_indexes.cypher
```

**Option B: If schema files have issues, run minimal bootstrap**
```cypher
// Core constraints (run in Neo4j Browser if needed)
CREATE CONSTRAINT year_unique IF NOT EXISTS 
FOR (y:Year) REQUIRE y.year IS UNIQUE;

CREATE CONSTRAINT place_id_unique IF NOT EXISTS 
FOR (p:Place) REQUIRE p.place_id IS UNIQUE;

CREATE CONSTRAINT period_id_unique IF NOT EXISTS 
FOR (p:Period) REQUIRE p.period_id IS UNIQUE;

CREATE CONSTRAINT subject_id_unique IF NOT EXISTS 
FOR (s:SubjectConcept) REQUIRE s.subject_id IS UNIQUE;

CREATE CONSTRAINT claim_id_unique IF NOT EXISTS 
FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE;
```

### Verification
```cypher
SHOW CONSTRAINTS;
// Should see at least 5 constraints created
```

**Expected Output:**
```
| name | type | entityType | labelsOrTypes | properties |
|------|------|------------|---------------|------------|
| year_unique | UNIQUENESS | NODE | Year | [year] |
| place_id_unique | UNIQUENESS | NODE | Place | [place_id] |
| ... (more constraints) ... |
```

---

## 📅 **Stage 2: Temporal Backbone - Year Nodes**

### Purpose
Create the global temporal grid (Year nodes from -2000 to 2025).

### Data Source
Script generates Year nodes programmatically.

### Execution

```powershell
python scripts/backbone/temporal/genYearsToNeo.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE `
  --start -2000 `
  --end 2025
```

### What This Creates

**Nodes:** 4,025 Year nodes
- Years: -2000, -1999, ..., -1, 1, 2, ..., 2025
- **Note:** No year 0 (astronomically correct)

**Relationships:**
- `(:Year {year: -49})-[:FOLLOWED_BY]->(:Year {year: -48})`
- `(:Year {year: -48})-[:PRECEDED_BY]->(:Year {year: -49})`

### Verification

```cypher
// Count Year nodes
MATCH (y:Year) RETURN count(y) AS year_count;
// Expected: 4025

// Check year range
MATCH (y:Year) RETURN min(y.year) AS earliest, max(y.year) AS latest;
// Expected: earliest=-2000, latest=2025

// Verify chain integrity
MATCH (y1:Year {year: -49})-[:FOLLOWED_BY]->(y2:Year {year: -48})
RETURN y1.label, y2.label;
// Expected: "49 BCE" -> "48 BCE"

// Check for year 0 (should NOT exist)
MATCH (y:Year {year: 0}) RETURN count(y);
// Expected: 0 (no year 0)
```

**Success Criteria:**
- ✅ 4,025 Year nodes created
- ✅ No year 0
- ✅ FOLLOWED_BY/PRECEDED_BY chain intact
- ✅ Labels formatted correctly (e.g., "49 BCE", "100 CE")

---

## 📊 **Stage 2.5: Temporal Hierarchy (Optional)**

### Purpose
Add Decade/Century/Millennium hierarchy for queries.

### Execution

```powershell
python Neo4j/schema/run_cypher_file.py Neo4j/schema/05_temporal_hierarchy_levels.cypher
```

### What This Creates

**Additional Nodes:**
- Decade nodes (e.g., -200s, -190s)
- Century nodes (e.g., -2nd century, 1st century)
- Millennium nodes (e.g., -1st millennium, 1st millennium)

**Additional Relationships:**
- `(:Year)-[:PART_OF]->(:Decade)`
- `(:Decade)-[:PART_OF]->(:Century)`
- `(:Century)-[:PART_OF]->(:Millennium)`

### Verification

```cypher
// Count hierarchy nodes
MATCH (d:Decade) RETURN count(d) AS decade_count;
MATCH (c:Century) RETURN count(c) AS century_count;
MATCH (m:Millennium) RETURN count(m) AS millennium_count;

// Verify year->decade links
MATCH (y:Year {year: -49})-[:PART_OF]->(d:Decade)
RETURN y.label, d.label;
// Expected: "49 BCE" -> "-40s BCE" or similar
```

**Success Criteria:**
- ✅ Hierarchy nodes created
- ✅ Year->Decade->Century->Millennium links working

---

## ⏳ **Stage 3: Periods from PeriodO**

### Purpose
Load canonical historical periods from PeriodO authority.

### Data Source
`Temporal/periodo_filtered_end_before_minus2000_with_geography.csv` or similar PeriodO export

### Execution

```powershell
python scripts/backbone/temporal/import_enriched_periods.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE `
  --universal-span-threshold 1000
```

### What This Creates

**Nodes:** ~1,077 Period nodes
- Each with: label, start_year, end_year, spatial_coverage
- Properties: `granularity_class` (universal vs granular), `span_years`
- Temporal tagging: `temporal_tag='unknown'` (SCA baseline)

**Relationships:**
- `(:Period)-[:STARTS_IN_YEAR]->(:Year)`
- `(:Period)-[:ENDS_IN_YEAR]->(:Year)`
- `(:Period)-[:PART_OF]->(:Period)` (hierarchy)
- `(:Period)-[:BROADER_THAN]->(:Period)` (convenience)
- `(:Period)-[:NARROWER_THAN]->(:Period)` (convenience)

### Verification

```cypher
// Count periods
MATCH (p:Period) RETURN count(p) AS period_count;
// Expected: ~1077

// Check year links
MATCH (p:Period)-[:STARTS_IN_YEAR]->(y:Year)
RETURN count(p) AS periods_with_start_year;
// Should be close to period_count

// Sample period
MATCH (p:Period {label: "Roman Republic"})
OPTIONAL MATCH (p)-[:STARTS_IN_YEAR]->(ys:Year)
OPTIONAL MATCH (p)-[:ENDS_IN_YEAR]->(ye:Year)
RETURN p.label, ys.year, ye.year, p.spatial_coverage;
```

**Success Criteria:**
- ✅ ~1,077 Period nodes loaded
- ✅ All periods linked to Year nodes
- ✅ Hierarchy relationships working
- ✅ Spatial coverage populated

---

## 🌍 **Stage 4: Geographic Backbone - Pleiades Places**

### Purpose
Load ancient place gazetteer (Mediterranean focus).

### Data Source
Pleiades bulk download (JSON format, parsed by script).

### Execution

**Full Load:**
```powershell
python scripts/backbone/geographic/import_pleiades_to_neo4j.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE
```

**Test Load (recommended first):**
```powershell
# Load first 1000 places to test
python scripts/backbone/geographic/import_pleiades_to_neo4j.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE `
  --limit 1000
```

### What This Creates

**Nodes:**
- ~41,993 Place nodes (full load)
- ~38,321 PlaceName nodes (alternate names)

**Relationships:**
- `(:Place)-[:HAS_NAME]->(:PlaceName)` (~42,111 relationships)
- `(:Place)-[:LOCATED_IN]->(:Place)` (hierarchy from Wikidata P131)

**Properties on Place:**
- `place_id`, `label`, `pleiades_id`
- `latitude`, `longitude` (if available)
- `place_type`, `modern_country`

### Verification

```cypher
// Count places and names
MATCH (p:Place) RETURN count(p) AS place_count;
MATCH (n:PlaceName) RETURN count(n) AS name_count;
// Expected: ~41,993 places, ~38,321 names (full load)
// Or ~1,000 places if test load

// Check name links
MATCH (p:Place)-[:HAS_NAME]->(n:PlaceName)
RETURN count(*) AS name_links;

// Sample place
MATCH (p:Place {label: "Rome"})
OPTIONAL MATCH (p)-[:HAS_NAME]->(n:PlaceName)
RETURN p.label, p.pleiades_id, p.latitude, p.longitude, collect(n.name) AS alternate_names;
```

**Success Criteria:**
- ✅ Place nodes loaded
- ✅ PlaceName nodes created
- ✅ HAS_NAME relationships working
- ✅ Coordinates present for most places

---

## 🗺️ **Stage 5: Geographic Type Hierarchy**

### Purpose
Add semantic place types (city, province, settlement, etc.) and type-based classification.

### Execution

```powershell
python scripts/backbone/geographic/build_place_type_hierarchy.py `
  --no-wikidata `
  --load-neo4j `
  --neo4j-mode core `
  --force-http `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE
```

### What This Creates

**Nodes:**
- ~14 PlaceType nodes (city, settlement, province, etc.)
- ~212 PlaceTypeTokenMap nodes (mapping tokens to types)
- ~4 GeoSemanticType nodes (administrative, natural, cultural, archaeological)

**Relationships:**
- `(:Place)-[:INSTANCE_OF_PLACE_TYPE]->(:PlaceType)` (~52,005)
- `(:Place)-[:HAS_GEO_SEMANTIC_TYPE]->(:GeoSemanticType)` (~48,159)
- `(:PlaceType)-[:HAS_GEO_SEMANTIC_TYPE]->(:GeoSemanticType)` (~10)

### Verification

```cypher
// Count type nodes
MATCH (pt:PlaceType) RETURN count(pt) AS place_types;
MATCH (gs:GeoSemanticType) RETURN count(gs) AS geo_semantic_types;
// Expected: 14 place types, 4 geo semantic types

// Check place type assignments
MATCH (p:Place)-[:INSTANCE_OF_PLACE_TYPE]->(pt:PlaceType)
RETURN pt.label, count(p) AS place_count
ORDER BY place_count DESC;
// Should show distribution (e.g., "settlement": 25000, "city": 3000)

// Sample place with types
MATCH (p:Place {label: "Rome"})
OPTIONAL MATCH (p)-[:INSTANCE_OF_PLACE_TYPE]->(pt:PlaceType)
OPTIONAL MATCH (p)-[:HAS_GEO_SEMANTIC_TYPE]->(gs:GeoSemanticType)
RETURN p.label, pt.label, gs.label;
```

**Success Criteria:**
- ✅ 14 PlaceType nodes
- ✅ 4 GeoSemanticType nodes
- ✅ Places linked to types
- ✅ Type hierarchy working

---

## ✅ **Stage 6: Final Verification**

### Comprehensive Health Check

```cypher
// === OVERVIEW ===
CALL db.labels() YIELD label
RETURN label ORDER BY label;
// Should see: Year, Decade, Century, Millennium, Period, Place, PlaceName, PlaceType, etc.

CALL db.relationshipTypes() YIELD relationshipType
RETURN relationshipType ORDER BY relationshipType;
// Should see: FOLLOWED_BY, PRECEDED_BY, STARTS_IN_YEAR, ENDS_IN_YEAR, HAS_NAME, etc.

// === NODE COUNTS ===
CALL apoc.meta.stats() YIELD labels
RETURN labels;
// OR manual:
RETURN
  count { MATCH (:Year) } AS years,
  count { MATCH (:Decade) } AS decades,
  count { MATCH (:Century) } AS centuries,
  count { MATCH (:Millennium) } AS millennia,
  count { MATCH (:Period) } AS periods,
  count { MATCH (:Place) } AS places,
  count { MATCH (:PlaceName) } AS place_names,
  count { MATCH (:PlaceType) } AS place_types,
  count { MATCH (:GeoSemanticType) } AS geo_semantic_types;

// === RELATIONSHIP COUNTS ===
MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC;

// === SAMPLE QUERIES ===
// Roman Republic with temporal bounds
MATCH (p:Period {label: "Roman Republic"})
OPTIONAL MATCH (p)-[:STARTS_IN_YEAR]->(ys:Year)
OPTIONAL MATCH (p)-[:ENDS_IN_YEAR]->(ye:Year)
RETURN p.label, ys.year AS start, ye.year AS end, p.spatial_coverage;

// Rome with geographic context
MATCH (place:Place {label: "Rome"})
OPTIONAL MATCH (place)-[:HAS_NAME]->(n:PlaceName)
OPTIONAL MATCH (place)-[:INSTANCE_OF_PLACE_TYPE]->(pt:PlaceType)
RETURN place.label, place.pleiades_id, 
       place.latitude, place.longitude,
       collect(DISTINCT n.name) AS names,
       pt.label AS place_type;
```

---

## 📊 **Expected Final State**

### Node Counts

| Label | Count | Source |
|-------|-------|--------|
| Year | 4,025 | Generated (-2000 to 2025, no year 0) |
| Decade | ~400 | Generated hierarchy |
| Century | ~40 | Generated hierarchy |
| Millennium | ~4 | Generated hierarchy |
| Period | ~1,077 | PeriodO filtered import |
| Place | ~41,993 | Pleiades full import (or ~1,000 for test) |
| PlaceName | ~38,321 | Pleiades names (or ~900 for test) |
| PlaceType | 14 | Place type taxonomy |
| PlaceTypeTokenMap | 212 | Type mapping tokens |
| GeoSemanticType | 4 | Semantic classification |

**Total Nodes (full build):** ~86,000

### Relationship Counts

| Type | Count | Purpose |
|------|-------|---------|
| FOLLOWED_BY | 4,024 | Year sequence forward |
| PRECEDED_BY | 4,024 | Year sequence backward |
| PART_OF | ~400 (Y->D) + ~40 (D->C) + ~4 (C->M) + ~272 (P->P) | Hierarchy |
| STARTS_IN_YEAR | ~1,077 | Period start dates |
| ENDS_IN_YEAR | ~1,077 | Period end dates |
| BROADER_THAN | ~272 | Period hierarchy |
| NARROWER_THAN | ~272 | Period hierarchy |
| HAS_NAME | ~42,111 | Place alternate names |
| INSTANCE_OF_PLACE_TYPE | ~52,005 | Place type classification |
| HAS_GEO_SEMANTIC_TYPE | ~48,159 (places) + ~10 (types) | Semantic classification |
| LOCATED_IN | Variable | Place hierarchy |
| HAS_GEO_COVERAGE | ~2,961 | Period-place links |

**Total Relationships (full build):** ~157,000

---

## 🔧 **Troubleshooting**

### Issue: "Database not found"

**Solution:**
```cypher
// In Neo4j Browser, check available databases
SHOW DATABASES;

// If chrystallum doesn't exist, create it
CREATE DATABASE chrystallum;

// Then use it
:use chrystallum
```

### Issue: "Constraint already exists"

**Solution:** This is fine - constraints are idempotent. Script will skip existing ones.

### Issue: "Year nodes not linking to decades"

**Solution:** Run stage 2.5 (temporal hierarchy script) after year backbone.

### Issue: "Place import timeout"

**Solution:** Use `--limit 1000` flag for testing, then run full import when confident:
```powershell
# Test first
--limit 1000

# Then full load (takes 10-20 minutes)
# Remove --limit flag
```

### Issue: "Period-Year links are 0"

**Possible Cause:** Loaded periods extend earlier than Year backbone range (-2000)

**Solution:**
```powershell
# Option A: Extend year backbone earlier
python scripts/backbone/temporal/genYearsToNeo.py `
  --start -3000 `  # Extend to -3000
  --end 2025

# Option B: Filter periods to match year range
# Use filtered PeriodO import that only includes periods ending after -2000
```

---

## 🎯 **Quick Start Commands (Copy-Paste Ready)**

### Prerequisites
```powershell
# Set environment variables (replace with your values)
$env:NEO4J_URI = "bolt://localhost:7687"
$env:NEO4J_USERNAME = "neo4j"  
$env:NEO4J_PASSWORD = "YourPasswordHere"
$env:NEO4J_DATABASE = "chrystallum"
```

### Full Rebuild Sequence

```powershell
# Stage 1: Schema
python Neo4j/schema/run_cypher_file.py Neo4j/schema/01_schema_constraints_neo5_compatible.cypher
python Neo4j/schema/run_cypher_file.py Neo4j/schema/02_schema_indexes.cypher

# Stage 2: Temporal Backbone
python scripts/backbone/temporal/genYearsToNeo.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE `
  --start -2000 `
  --end 2025

# Stage 2.5: Temporal Hierarchy (optional)
python Neo4j/schema/run_cypher_file.py Neo4j/schema/05_temporal_hierarchy_levels.cypher

# Stage 3: Periods
python scripts/backbone/temporal/import_enriched_periods.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE

# Stage 4: Geographic (test with limit first)
python scripts/backbone/geographic/import_pleiades_to_neo4j.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE `
  --limit 1000

# Stage 5: Geographic Types
python scripts/backbone/geographic/build_place_type_hierarchy.py `
  --no-wikidata `
  --load-neo4j `
  --neo4j-mode core `
  --force-http `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database $env:NEO4J_DATABASE

# Verify
# Run verification queries in Neo4j Browser
```

### Verification Query (Copy-Paste to Neo4j Browser)

```cypher
RETURN
  count { MATCH (:Year) } AS years,
  count { MATCH (:Period) } AS periods,
  count { MATCH (:Place) } AS places,
  count { MATCH (:PlaceName) } AS place_names,
  count { MATCH (:PlaceType) } AS place_types,
  count { MATCH ()-[:STARTS_IN_YEAR]->() } AS period_starts,
  count { MATCH ()-[:ENDS_IN_YEAR]->() } AS period_ends,
  count { MATCH ()-[:HAS_NAME]->() } AS place_name_links,
  count { MATCH ()-[:INSTANCE_OF_PLACE_TYPE]->() } AS place_type_links;
```

---

## ⏱️ **Estimated Timeline**

| Stage | Time | Notes |
|-------|------|-------|
| Stage 1: Schema | 2 min | Fast |
| Stage 2: Years | 5 min | 4,025 nodes |
| Stage 2.5: Hierarchy | 2 min | Optional |
| Stage 3: Periods | 10 min | 1,077 nodes |
| Stage 4: Places (test) | 2 min | 1,000 nodes |
| Stage 4: Places (full) | 15 min | 41,993 nodes |
| Stage 5: Types | 5 min | 14 type nodes |
| Verification | 5 min | Run queries |
| **TOTAL (test load)** | **~30 min** | Quick validation |
| **TOTAL (full load)** | **~45 min** | Complete backbone |

---

## 📝 **Post-Rebuild Next Steps**

Once backbone is loaded:

1. **Federation CSV Crosswalks** (no Neo4j writes, just CSV generation)
   ```powershell
   python scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py
   python scripts/backbone/geographic/build_geonames_wikidata_bridge.py
   ```

2. **Subject Concepts** (after backbone is solid)
   ```powershell
   python scripts/backbone/subject/create_subject_nodes.py
   ```

3. **Federation Scoring** (your Priority #1)
   - Implement scoring module
   - Integrate with place/period nodes

4. **Perplexity Period Enrichment** (your Priority #4)
   - Test existing pipeline
   - Enrich period facet classifications

---

## 🚨 **Critical Notes**

### Year 0 Does Not Exist
- Astronomically correct: 1 BCE → 1 CE (no year 0)
- Scripts handle this automatically
- Verify: `MATCH (y:Year {year: 0}) RETURN count(y)` should return 0

### Database Name Consistency
- Use same `$env:NEO4J_DATABASE` value for all commands
- Recommended: `chrystallum` (not `neo4j` to avoid default DB issues)

### Test Before Full Load
- Always test with `--limit 1000` on geographic data first
- Verify structure looks good
- Then run full load

### Backup Strategy
- Take Neo4j backup after each successful stage
- Tag git commits for code changes
- Can rebuild from scripts if needed

---

## 📦 **What You'll Have After Complete Rebuild**

A clean Chrystallum instance with:

✅ **Temporal Backbone**
- 4,025 Year nodes (continuous chain -2000 to 2025)
- ~400 Decade, ~40 Century, ~4 Millennium nodes (if hierarchy loaded)
- ~1,077 Period nodes (PeriodO authority)
- All periods linked to Year nodes for temporal grounding

✅ **Geographic Backbone**  
- ~42,000 Place nodes (Pleiades gazetteer)
- ~38,000 PlaceName nodes (alternate names)
- 14 PlaceType classifications
- 4 GeoSemanticType categories
- ~52,000 place-to-type links

✅ **Ready for Next Phase**
- Subject concepts
- Entity nodes (Human, Event, etc.)
- Claims and assertions
- Federation scoring
- Perplexity enrichment

**Total:** ~86,000 nodes, ~157,000 relationships in fresh, validated instance

---

**Status:** Ready to Execute  
**Estimated Time:** 30 minutes (test) to 45 minutes (full)  
**Created:** 2026-02-19  
**Let me know when Neo4j is ready and we'll execute the rebuild!**

