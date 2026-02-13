# Complete Scripts, Files, and Execution Guide

**Date:** December 11, 2025  
**Purpose:** Comprehensive guide to all scripts, JSON files, Cypher files, and batch files  
**Status:** Reference Documentation  
**Last Updated:** Added unified Neo4j testing from root directory

---

## 📑 Table of Contents

1. [Batch Files (Execution Order)](#batch-files-execution-order)
2. [Python Scripts](#python-scripts)
3. [Cypher Files](#cypher-files)
4. [JSON Configuration Files](#json-configuration-files)
5. [CSV Data Files](#csv-data-files)
6. [Quick Start Workflows](#quick-start-workflows)

---

## 🚀 Batch Files (Execution Order)

### ⚠️ IMPORTANT: All Neo4j Tests Run from Root

**All Neo4j connection and validation tests should be run from the root directory (`graph 3/`).**

This provides:
- ✅ Unified testing interface
- ✅ Consistent credentials handling
- ✅ Single point of entry for all backbone tests
- ✅ Easier troubleshooting

**Note:** Subdirectories may have test scripts (e.g., `scripts/backbone/geographic/test_geo_connection.bat`), but these are convenience wrappers that redirect to the root-level test.

---

### Root-Level Neo4j Tests

#### **Unified Connection Test**

```
test_connection.bat       ← Run from root (graph 3) - tests ALL backbones
```

**Location:** Root directory (`graph 3/`)

**What it does:**
- Tests connection to Neo4j database
- Verifies credentials are correct
- Checks if Neo4j service is running
- Tests basic CRUD operations
- Checks temporal backbone (if imported)
- Checks geographic backbone (if imported)

**When to use:** FIRST - before any other operations

**Output:** Comprehensive test results including backbone status

**Requirements:**
- Neo4j must be running
- Default connection: `bolt://localhost:7687`
- Default credentials: `neo4j` / `Chrystallum`

**Usage:**
```batch
# From root directory (graph 3)
test_connection.bat
# Or with password
test_connection.bat YourPassword
```

**Note:** This is the ONLY Neo4j connection test you need. It tests all backbones (temporal, geographic, etc.) from one place.

---

### Temporal Scripts (`scripts/backbone/temporal/`)

#### **Recommended Execution Order**

```
1. test_connection.bat       ← Run from root (graph 3) - verify Neo4j
2. validate_qids.bat          ← Verify data quality (optional but recommended)
3. generate_csv.bat           ← Generate import CSVs
4. import_periods.bat         ← Import periods to Neo4j
5. import_full.bat            ← Import year nodes to Neo4j
```

**Alternative:** Use `reimport_all.bat` to do steps 3-5 in one command (clears existing data first)

---

### 2. **validate_qids.bat**
```batch
scripts/backbone/temporal/validate_qids.bat
```

**What it does:**
- Validates all Wikidata QIDs in Temporal/time_periods.csv
- Checks format (Q + digits)
- Verifies QIDs are not fragmented/malformed

**When to use:** Before importing data (optional but recommended)

**Output:** Validation report showing any QID issues

**Requirements:**
- `Temporal/time_periods.csv` must exist
- Python installed

---

### 3. **generate_csv.bat**
```batch
scripts/backbone/temporal/generate_csv.bat
```

**What it does:**
- Generates `year_nodes.csv` from period definitions
- Creates year backbone structure (5026 years: 3000 BCE to 2025 CE)
- Links years to periods via relationships

**When to use:** Before importing to Neo4j (or when year range changes)

**Output:** Creates/updates `year_nodes.csv`

**Requirements:**
- `Temporal/time_periods.csv` must exist
- Python installed

---

### 4. **import_periods.bat**
```batch
scripts/backbone/temporal/import_periods.bat
```

**What it does:**
- Imports historical periods from CSV to Neo4j
- Creates Period nodes with temporal metadata
- Does NOT clear existing data (additive)

**When to use:** After generating CSVs, before importing years

**Output:** Period nodes in Neo4j

**Requirements:**
- Neo4j running
- `Temporal/time_periods.csv` in Neo4j import directory
- Can use Cypher script directly or Python script

---

### 5. **import_full.bat**
```batch
scripts/backbone/temporal/import_full.bat
```

**What it does:**
- Imports ALL 5026 year nodes (3000 BCE - 2025 CE)
- Creates relationships between years and periods
- Full temporal backbone import

**When to use:** For production/full system setup

**Output:** 5026 Year nodes + relationships in Neo4j

**Time:** ~2-5 minutes for full import

**Requirements:**
- Neo4j running
- Period nodes already imported
- `year_nodes.csv` generated

---

### 6. **import_test.bat**
```batch
scripts/backbone/temporal/import_test.bat
```

**What it does:**
- Imports LIMITED year range for testing
- Default: 753 BCE - 82 BCE (Roman Kingdom to Sulla)
- Faster than full import for development

**When to use:** For testing and development

**Output:** Subset of Year nodes for testing

**Time:** ~10-30 seconds

**Requirements:**
- Neo4j running
- Period nodes already imported

---

### 7. **reimport_all.bat**
```batch
scripts/backbone/temporal/reimport_all.bat
```

**What it does:**
- ⚠️ **CLEARS ALL temporal data** (periods + years)
- Regenerates CSVs
- Re-imports everything fresh

**When to use:** 
- Starting fresh
- After major taxonomy changes
- When data is corrupted

**Output:** Fresh temporal backbone

**Warning:** ⚠️ DESTRUCTIVE - removes all existing temporal data!

**Requirements:**
- Neo4j running
- All CSV files

---

### 8. **clear_temporal_data.bat**
```batch
scripts/backbone/temporal/clear_temporal_data.bat
```

**What it does:**
- ⚠️ **DELETES ALL** Period and Year nodes from Neo4j
- Clean slate for re-import

**When to use:**
- Before fresh import
- When cleaning up test data

**Warning:** ⚠️ DESTRUCTIVE - removes all temporal data!

**Requirements:**
- Neo4j running

---

### 9. **classify_date.bat**
```batch
scripts/backbone/temporal/classify_date.bat <year>
```

**What it does:**
- Classifies a specific year into historical periods
- Shows which period(s) a year belongs to
- Tool-augmented reasoning (not LLM-based)

**When to use:**
- Testing period classification
- Debugging period assignments
- Verifying taxonomy coverage

**Example:**
```bash
classify_date.bat -753    # Rome founded
classify_date.bat 1347    # Black Death
classify_date.bat 1969    # Moon landing
```

**Output:** Period assignments with confidence

**Requirements:**
- `Temporal/time_periods.csv`
- Python installed

---

### Geographic Scripts (`scripts/backbone/geographic/`)

#### **Recommended Execution Order**

```
1. test_connection.bat       ← Run from root (graph 3) - verify Neo4j
2. validate_geo_csv.py      ← Validate CSV (optional)
3. import_places.bat         ← Import places to Neo4j
4. link_periods_to_places.bat ← Link Period → Place
```

**Alternative:** Use `RUN_FULL_GEO_IMPORT.bat` to do steps 1-4 in one command

---

### 10. **import_places.bat**
```batch
scripts/backbone/geographic/import_places.bat
```

**What it does:**
- Imports geographic places from CSV to Neo4j
- Creates Place nodes with coordinates and metadata
- Does NOT clear existing data (additive)

**When to use:** After validating CSV, before linking periods

**Output:** Place nodes in Neo4j (~34 places)

**Requirements:**
- Neo4j running
- `stable_geographic_features.csv` in Neo4j import directory

---

### 11. **link_periods_to_places.bat**
```batch
scripts/backbone/geographic/link_periods_to_places.bat
```

**What it does:**
- Creates `(Period)-[:LOCATED_IN]->(Place)` relationships
- Links periods to places based on region mapping
- Requires both Period and Place nodes to exist

**When to use:** After importing both periods and places

**Output:** Period-Place links in Neo4j (~12 links)

**Requirements:**
- Neo4j running
- Period nodes imported (temporal backbone)
- Place nodes imported
- `region_place_mapping.csv` in Neo4j import directory

---

### 12. **RUN_FULL_GEO_IMPORT.bat**
```batch
scripts/backbone/geographic/RUN_FULL_GEO_IMPORT.bat
```

**What it does:**
- Runs complete geographic import process
- Tests connection (from root)
- Validates CSV
- Imports places
- Links periods to places
- Validates results

**When to use:** For complete geographic backbone setup

**Output:** Full geographic backbone in Neo4j

**Requirements:**
- Neo4j running
- Temporal backbone imported (for period links)

---

**Note on test_geo_connection.bat:**
- Located in `scripts/backbone/geographic/`
- This is a convenience wrapper that redirects to root-level `test_connection.bat`
- Always use root-level test for consistency

---

## 🐍 Python Scripts

### Root Scripts

#### **consolidate_schema.py**
**Purpose:** Consolidate all CSV schema files into single JSON

**What it does:**
- Reads entity definitions from canonical schema sources
- Reads relationship types from `Relationships/relationship_types_registry_master.csv` (300 types)
- Reads hierarchy metadata from canonical schema sources
- Reads action structure vocabularies and mappings
- Reads temporal period definitions
- Generates `JSON/chrystallum_schema.json` with complete schema

**Usage:**
```bash
python consolidate_schema.py
```

**Output:**
```
[OK] Consolidated schema written to: JSON\chrystallum_schema.json

Summary:
  Entities: (see current schema metadata)
  Relationships: 300
  Entity Hierarchy: (see current schema metadata)
  Goal Types: 10
  Trigger Types: 10
  Action Types: 15
  Result Types: 19
  Wikidata Mappings: 54
  Temporal Periods: 13
```

**When to use:**
- After updating any canonical CSV files
- When relationship types are added/modified
- To regenerate schema JSON from authoritative sources

**Requirements:**
- All source CSV files must be present
- Python 3.6+

**Outputs:** `JSON/chrystallum_schema.json` (schema version 3.3)

**Note:** As of 2025-12-10, the canonical CSV was cleaned to remove unused LCC/FAST columns. See `CSV_CLEANUP_SUMMARY.md` for details.

---

### Temporal Scripts (`scripts/backbone/temporal/`)

#### **temporal_period_classifier.py**
**Purpose:** Core temporal classification engine

**What it does:**
- Tool-augmented period classification (95.31% accuracy)
- Maps years to historical periods
- Handles BCE/CE dates uniformly
- No LLM required - pure rule-based

**Used by:** classify_date.bat, import scripts

**Can be imported:**
```python
from temporal_period_classifier import TemporalPeriodClassifier

classifier = TemporalPeriodClassifier()
result = classifier.classify_date(-753)
print(result.period_name)  # "Roman Kingdom"
```

---

#### **import_year_nodes_to_neo4j.py**
**Purpose:** Import year backbone to Neo4j

**What it does:**
- Creates Year nodes
- Creates DURING relationships to periods
- Generates temporal backbone
- Supports full or partial import

**Usage:**
```bash
# Test range (Roman Kingdom to Sulla)
python import_year_nodes_to_neo4j.py --start -753 --end -82

# Full range (all 5026 years)
python import_year_nodes_to_neo4j.py --full-range

# Test mode (shows what would be created)
python import_year_nodes_to_neo4j.py --start -753 --end -82 --test
```

**Used by:** import_full.bat, import_test.bat

---

#### **generate_csv_for_import.py**
**Purpose:** Generate year_nodes.csv

**What it does:**
- Reads period taxonomy
- Generates year nodes with classifications
- Creates CSV for Neo4j import

**Usage:**
```bash
python generate_csv_for_import.py
```

**Used by:** generate_csv.bat

**Output:** `year_nodes.csv`

---

#### **test_neo4j_connection.py**
**Purpose:** Unified Neo4j connectivity test (runs from root)

**What it does:**
- Tests connection to Neo4j database
- Verifies credentials
- Tests basic CRUD operations
- Checks temporal backbone (if imported)
- Checks geographic backbone (if imported)
- Reports comprehensive status

**Location:** Root directory (`graph 3/`)

**Used by:** `test_connection.bat` (root-level)

**Note:** This is the unified test that covers all backbones. Always run from root directory.

---

#### **clear_temporal_data.py**
**Purpose:** Clear temporal data from Neo4j

**What it does:**
- Deletes all Period nodes
- Deletes all Year nodes
- Cleans up for fresh import

**Used by:** clear_temporal_data.bat, reimport_all.bat

⚠️ **Destructive operation**

---

#### **query_wikidata_periods.py**
**Purpose:** Query Wikidata for period information

**What it does:**
- Looks up period details from Wikidata
- Retrieves QID metadata
- Validates period definitions

**Usage:**
```bash
python query_wikidata_periods.py Q12554  # Middle Ages
```

---

#### **find_correct_qids.py**
**Purpose:** Find/fix QIDs for periods

**What it does:**
- Searches Wikidata for period names
- Suggests correct QIDs
- Helps fix QID issues

**When to use:** When adding new periods or fixing QID errors

---

#### **fix_qids.py**
**Purpose:** Batch fix QIDs in taxonomy

**What it does:**
- Updates QIDs in CSV files
- Fixes known QID issues
- Validates after fixing

**When to use:** After QID corrections identified

---

#### **suggest_missing_periods.py**
**Purpose:** Identify gaps in temporal coverage

**What it does:**
- Analyzes period taxonomy
- Identifies date ranges with no period assignment
- Suggests periods that might be missing

**When to use:** When validating taxonomy comprehensiveness

---

#### **validate_qids_simple.py**
**Purpose:** Quick QID validation

**What it does:**
- Checks QID format
- Validates Q + digits pattern
- Reports malformed QIDs

**Used by:** validate_qids.bat

---

#### **verify_all_qids.py**
**Purpose:** Comprehensive QID verification

**What it does:**
- Validates all QIDs in taxonomy
- Checks against Wikidata
- Verifies QIDs actually exist

**When to use:** Before major imports or after taxonomy changes

---

### Geographic Scripts (`scripts/backbone/geographic/`)

#### **validate_geo_csv.py**
**Purpose:** Validate geographic features CSV

**What it does:**
- Validates QID format
- Validates coordinate ranges
- Checks required columns

**Usage:**
```bash
python validate_geo_csv.py
```

---

#### **create_region_place_mapping.py**
**Purpose:** Generate region to place QID mapping

**What it does:**
- Analyzes period taxonomy regions
- Creates mapping CSV for Period → Place links
- Maps region names to Wikidata QIDs

**Usage:**
```bash
python create_region_place_mapping.py
```

**Output:** `region_place_mapping.csv`

---

#### **resolve_place_names.py**
**Purpose:** Resolve place names to QIDs

**What it does:**
- Uses Wikidata API to resolve place names
- Returns atomic QIDs and coordinates
- Supports batch processing

**Usage:**
```bash
python resolve_place_names.py "Rome, Italy"
python resolve_place_names.py --csv stable_geographic_features.csv
```

---

#### **geocode_locations.py**
**Purpose:** Forward/reverse geocoding

**What it does:**
- Forward geocoding (name → coordinates)
- Reverse geocoding (coordinates → name)
- GeoNames API integration

**Usage:**
```bash
python geocode_locations.py --forward "Rome, Italy"
python geocode_locations.py --reverse 41.9028 12.4964
```

---

#### **validate_coordinates.py**
**Purpose:** Validate coordinate formats

**What it does:**
- Type checking (must be numeric)
- Range validation
- Format conversion

**Usage:**
```bash
python validate_coordinates.py 41.9028 12.4964
```

---

#### **generate_place_entities.py**
**Purpose:** Generate Neo4j entities from CSV

**What it does:**
- Creates Place nodes
- Handles atomic QIDs and coordinates
- Validates all data before generation

**Usage:**
```bash
python generate_place_entities.py --csv stable_geographic_features.csv --output import.cypher
```

---

### Relations Scripts (`relations/scripts/`) [legacy path in examples]

#### **create_canonical_relationships.py**
**Purpose:** Generate canonical relationship types

**What it does:**
- Consolidates relationship types from multiple sources
- Creates/refreshes consolidated registry CSV (300 types)
- Validates backbone alignment (LCC/LCSH/FAST)
- Generates summary JSON

**Usage:**
```bash
cd relations/scripts
python create_canonical_relationships.py
```

**Output:**
- `canonical_relationship_types.csv`
- `canonical_relationship_types_summary.json`

---

#### **load_relationship_registry.py**
**Purpose:** Load relationships into Neo4j PropertyRegistry

**What it does:**
- Creates PropertyRegistry nodes (per Baseline Core 3.1)
- Loads all 300 relationship types
- Stores metadata (directionality, Wikidata props, backbone codes)

**Usage:**
```bash
cd relations/scripts
python load_relationship_registry.py

# With custom Neo4j connection
python load_relationship_registry.py \
  --neo4j-uri bolt://localhost:7687 \
  --username neo4j \
  --password your_password

# Verify only (don't load)
python load_relationship_registry.py --verify-only
```

**Requirements:**
- Neo4j running
- `canonical_relationship_types.csv` exists

---

#### **validate_identifier_atomicity.py**
**Purpose:** Validate atomic identifier handling

**What it does:**
- Scans prompts/code for atomic identifiers (QIDs, FAST IDs, etc.)
- Detects identifiers that should NOT be passed to LLMs
- Reports violations with severity levels

**Usage:**
```bash
cd relations/scripts

# Run test cases
python validate_identifier_atomicity.py

# Check a file
python validate_identifier_atomicity.py path/to/file.py
```

**Can be imported:**
```python
from validate_identifier_atomicity import IdentifierValidator

validator = IdentifierValidator()
result = validator.check_prompt("Tell me about Q17193")
if not result['is_safe']:
    for issue in result['issues']:
        print(issue)
```

---

## 📜 Cypher Files

### Temporal Cypher (`cypher/setup/`)

#### **import_periods_to_neo4j.cypher**
**Purpose:** Import historical periods to Neo4j

**What it does:**
- Loads periods from CSV
- Creates Period nodes with metadata:
  - QID (Wikidata)
  - Start/end years
  - ISO 8601 dates
  - Region
  - Notes
- Creates temporal relationships between periods

**Usage:**
```cypher
// In Neo4j Browser or cypher-shell
:source cypher/setup/import_periods_to_neo4j.cypher
```

**Requirements:**
- CSV file in Neo4j import directory
- Neo4j running

**Atomic Identifiers:** ⚠️ Contains QIDs - see file header warnings

---

#### **example_queries.cypher**
**Purpose:** 50+ example queries for temporal backbone

**What it does:**
- Demonstrates temporal query patterns
- Shows period lookups
- Examples of year-period traversals
- Timeline queries
- Period overlap queries

**Categories:**
- Basic queries (list periods, count years)
- Period queries (years in period, periods for year)
- Timeline queries (events in date range)
- Analysis queries (period overlaps, gaps)
- Advanced queries (multi-period, fuzzy matching)

**Usage:** Copy queries to Neo4j Browser

**Atomic Identifiers:** ⚠️ Contains QIDs - see file header warnings

---

### Geographic Cypher (`cypher/setup/`)

#### **import_places_to_neo4j.cypher**
**Purpose:** Import geographic places to Neo4j

**What it does:**
- Loads places from CSV
- Creates Place nodes with metadata:
  - QID (Wikidata)
  - Coordinates (lat/lon)
  - Feature type
  - GeoNames ID
  - Stability rating
- Creates indexes for performance

**Usage:**
```cypher
// In Neo4j Browser or cypher-shell
:source cypher/setup/import_places_to_neo4j.cypher
```

**Requirements:**
- CSV file in Neo4j import directory
- Neo4j running

**Atomic Identifiers:** ⚠️ Contains QIDs - see file header warnings

---

#### **link_periods_to_places.cypher**
**Purpose:** Link Period nodes to Place nodes

**What it does:**
- Creates `(Period)-[:LOCATED_IN]->(Place)` relationships
- Uses region mapping CSV
- Links periods to places based on region property

**Usage:**
```cypher
// In Neo4j Browser or cypher-shell
:source cypher/setup/link_periods_to_places.cypher
```

**Requirements:**
- Period nodes imported
- Place nodes imported
- Mapping CSV in Neo4j import directory

---

#### **example_geo_queries.cypher**
**Purpose:** 50+ example queries for geographic backbone

**What it does:**
- Demonstrates geographic query patterns
- Shows place lookups
- Examples of period-place traversals
- Full backbone chain queries
- Event-place integration

**Categories:**
- Basic place queries
- Period-place integration
- Event-place integration
- Geographic hierarchy
- Temporal-geographic queries
- Full backbone chain

**Usage:** Copy queries to Neo4j Browser

**Atomic Identifiers:** ⚠️ Contains QIDs - see file header warnings

---

### Roman Republic Cypher

#### **Roman Republic/test_roman_kingdom_to_sulla.cypher**
**Purpose:** Test data for Roman Republic timeline

**What it does:**
- Creates comprehensive test case (753 BCE - 82 BCE)
- Includes entities, events, people, places
- Demonstrates action structure pattern
- Uses backbone alignment (FAST/LCC/MARC)

**Usage:** Complete graph import example

**Atomic Identifiers:** ⚠️ Contains QIDs, FAST IDs, LCC codes, MARC codes, Pleiades IDs - see file header warnings

---

## 📋 JSON Configuration Files

### Root Directory

#### **cypher_templates.json**
**Purpose:** Simple Cypher query templates

**What it contains:**
- Query templates by category
- Basic relationship queries
- Entity lookups

**Used by:** Query generation, documentation

**Format:** Category → Relationship → Cypher template

---

#### **cypher_template_library.json**
**Purpose:** Complete Cypher template library

**What it contains:**
- 134+ relationship type templates (target canonical alignment: 300)
- Forward and inverse query templates
- Wikidata property mappings
- Directionality metadata
- Action structure examples

**Used by:** Query generation tools, documentation

**Status:** ⚠️ Needs update (134 → 300)

**Format:** 
```json
{
  "metadata": { ... },
  "Category": {
    "RELATIONSHIP_TYPE": {
      "forward_template": "...",
      "inverse_template": "...",
      "wikidata_property": "...",
      "directionality": "...",
      "description": "..."
    }
  }
}
```

---

### Reference Folder

#### **JSON/chrystallum_schema.json**
**Purpose:** Complete system schema

**What it contains:**
- Entity types (120+)
- Relationship types (target canonical: 300)
- Entity hierarchy
- Action structure vocabularies
- Wikidata mappings
- Temporal periods

**Used by:** Extraction tools, validation, documentation

**Status:** ⚠️ Review count alignment with current canonical registry (target: 300)

**Format:**
```json
{
  "metadata": { ... },
  "entities": { "count": 121, "types": [...] },
  "relationships": { "count": 300, "types": [...] },
  "entity_hierarchy": { ... },
  "action_structure": { ... },
  "temporal_periods": { ... }
}
```

---

### Relations Folder

#### **JSON/canonical_relationship_types_summary.json**
**Purpose:** Summary of canonical relationship types

**What it contains:**
- Count: 300 relationship types
- Categories breakdown
- Statistics by directionality
- Backbone alignment status

**Generated by:** `create_canonical_relationships.py`

**Used by:** Documentation, quick reference

---

## 📊 CSV Data Files

### Temporal CSVs

#### **Temporal/time_periods.csv**
**Purpose:** Master period definitions

**Columns:**
- Period: Human-readable name
- Start_Year: Start year (negative for BCE)
- End_Year: End year
- QID: Wikidata QID (atomic string)
- Region: Geographic scope
- Notes: Additional information

**Status:** Source of truth for temporal periods

**Used by:** All temporal scripts

---

#### **scripts/backbone/temporal/year_nodes.csv**
**Purpose:** Generated year backbone data

**Generated by:** `generate_csv_for_import.py`

**Contains:** 5026 years (3000 BCE - 2025 CE) with period classifications

**Used by:** Neo4j import scripts

---

#### **scripts/backbone/temporal/period_mappings.csv**
**Purpose:** Period relationship mappings

**What it contains:**
- Period-to-period relationships
- Temporal hierarchies
- Sequential relationships

---

#### **scripts/backbone/temporal/sequential_relationships.csv**
**Purpose:** FOLLOWED_BY relationships

**What it contains:**
- Chronological sequences
- Period progression

---

### Geographic CSVs

#### **scripts/backbone/geographic/stable_geographic_features.csv**
**Purpose:** Geographic features data

**Columns:**
- Feature_Type: Type (Continent, Ocean, City, etc.)
- Feature_Name: Name
- QID: Wikidata QID (atomic string)
- GeoNames_ID: GeoNames identifier (optional)
- Latitude: Latitude (-90 to 90)
- Longitude: Longitude (-180 to 180)
- Stability: Stability rating
- Notes: Additional notes

**Contains:** 34 places (continents, oceans, seas, islands, mountains, rivers)

**Used by:** Geo import scripts

---

#### **scripts/backbone/geographic/region_place_mapping.csv**
**Purpose:** Period region → Place QID mapping

**Columns:**
- Period_Region: Region name from period taxonomy
- Place_QID: Wikidata QID for place
- Place_Type: Type (Continent, Country, etc.)
- Period_Count: Number of periods in region
- Notes: Additional information

**Generated by:** `create_region_place_mapping.py`

**Used by:** Period-Place linking script

---

### Relations CSVs

#### **Relationships/relationship_types_registry_master.csv**
**Purpose:** ⭐ **CANONICAL SOURCE OF TRUTH**

**Contains:** All 300 relationship types

**Columns:**
- category: Relationship category
- relationship_type: Type name
- description: Human-readable description
- wikidata_property: Wikidata P-property
- directionality: forward/inverse/symmetric/unidirectional
- parent_relationship: Hierarchical parent
- specificity_level: Hierarchy level
- lcc_code: Library of Congress Classification
- lcsh_heading: Library of Congress Subject Heading
- fast_id: FAST identifier
- status: active/deprecated/proposed
- note: Additional information
- source: Origin source
- version: Version number

**Used by:** All relationship scripts, validation, Neo4j import

---

#### **Entity hierarchy metadata (canonical schema)**
**Purpose:** Entity type hierarchy context

**Contains:** Parent-child hierarchy metadata in canonical schema artifacts

---

## 🎯 Quick Start Workflows

### Workflow 1: Fresh Installation

```bash
# 1. Verify Neo4j is running (from root - graph 3)
cd "C:\Projects\federated-graph-framework\graph 3"
test_connection.bat

# 2. Validate data quality (optional)
cd scripts/backbone/temporal
validate_qids.bat

# 3. Generate import files
generate_csv.bat

# 4. Import periods
import_periods.bat

# 5. Import full year backbone
import_full.bat

# 6. Load relationship registry
cd ../../relations/scripts
python load_relationship_registry.py

# 7. Verify all backbones (from root)
cd ../..
test_connection.bat
```

**Time:** ~5-10 minutes

---

### Workflow 2: Quick Test Setup

```bash
# Use reimport_all for testing
cd scripts/backbone/temporal
reimport_all.bat

# Loads limited date range for testing
```

**Time:** ~1 minute

---

### Workflow 3: Testing a Specific Date Range

```bash
cd scripts/backbone/temporal

# Clear existing data
clear_temporal_data.bat

# Import test range (Roman period)
import_test.bat

# Test period classification
classify_date.bat -753
classify_date.bat -509
classify_date.bat -82
```

---

### Workflow 4: Updating Relationship Types

```bash
# 1. Edit canonical CSV
notepad Relationships/relationship_types_registry_master.csv

# 2. Regenerate and validate
cd relations/scripts
python create_canonical_relationships.py

# 3. Update Neo4j PropertyRegistry
python load_relationship_registry.py

# 4. Verify
python load_relationship_registry.py --verify-only
```

---

### Workflow 5: Validating Identifier Handling

```bash
# Check all prompts/code for atomic identifier violations
cd relations/scripts
python validate_identifier_atomicity.py

# Check specific file
python validate_identifier_atomicity.py ../../path/to/file.py
```

---

### Workflow 6: Geographic Backbone Setup

```bash
# 1. Verify Neo4j (from root)
cd "C:\Projects\federated-graph-framework\graph 3"
test_connection.bat

# 2. Import geographic places
cd scripts/backbone/geographic
RUN_FULL_GEO_IMPORT.bat

# 3. Verify (from root)
cd ..\..\..
test_connection.bat
```

**Time:** ~2-3 minutes

---

## 📚 Related Documentation

- **`md/Guides/Temporal_Comprehensive_Documentation.md`** - Temporal system reference
- **`md/Guides/Neo4j_Import_Guide.md`** - Detailed import guide
- **`md/Guides/Neo4j_Quick_Start.md`** - Quick start guide
- **`Relationships/RELATIONSHIPS_CONSOLIDATION_2026-02-12.md`** - Relationship registry consolidation summary
- **`md/Reference/IDENTIFIER_CHEAT_SHEET.md`** - Atomic identifier reference
- **`md/Reference/REFERENCE_BACKLOG.md`** - Follow-up backlog and legacy migration notes

---

## ⚠️ Important Notes

### Atomic Identifiers

**NEVER pass these to LLMs:**
- QIDs (e.g., Q17193)
- FAST IDs (e.g., 1145002)
- LCC codes (e.g., DG241-269)
- MARC codes (e.g., sh85115058)
- Pleiades IDs (e.g., 423025)
- GeoNames IDs (numeric)
- ISO 8601 dates (e.g., -0753-01-01)

**Always use tool lookups** for these identifiers.

See: `md/Reference/IDENTIFIER_CHEAT_SHEET.md`

---

### Count Alignment Note

Legacy docs may still mention earlier relationship totals.
Current canonical registry target is:
1. `Relationships/relationship_types_registry_master.csv` (300)
2. `JSON/chrystallum_schema.json` should be kept aligned where applicable
3. `Prompts/extraction_agent.txt` should reference canonical registry path
4. `md/Architecture/Graph_Governance_Specification.md` should avoid stale legacy counts

See: `md/Reference/REFERENCE_BACKLOG.md`

---

## 🔧 Troubleshooting

### Neo4j Connection Fails
```bash
# 1. Run unified test from root (graph 3)
cd "C:\Projects\federated-graph-framework\graph 3"
test_connection.bat

# 2. Check if Neo4j is running
# 3. Verify credentials
# 4. Check error messages in test output

# Note: Always run tests from root, not from subdirectories
```

### Import Fails
```bash
# 1. Clear existing data
clear_temporal_data.bat

# 2. Regenerate CSVs
generate_csv.bat

# 3. Try reimport_all.bat
```

### QID Validation Errors
```bash
# 1. Run validation
validate_qids.bat

# 2. Fix QIDs in CSV
# 3. Use find_correct_qids.py if needed
```

---

**Last Updated:** December 11, 2025  
**Version:** 1.1  
**Canonical Source:** Relationships/relationship_types_registry_master.csv (300 types)
