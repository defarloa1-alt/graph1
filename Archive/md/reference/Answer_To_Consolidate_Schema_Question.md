# Answer: Yes, There's a Script to Generate Schema JSON from CSV

**Question:** Is there a script to generate from CSV for schema JSON?

**Answer:** **YES!** → `consolidate_schema.py`

---

## The Script

**File:** `scripts/schema/consolidate_schema.py`

**What it does:**
Consolidates all schema CSV files into a single `data/schemas/chrystallum_schema.json`

---

## Usage

```cmd
python scripts/schema/consolidate_schema.py
```

**That's it!** No arguments needed.

---

## What Gets Generated

**Output File:** `data/schemas/chrystallum_schema.json`

**Includes:**
- ✅ 121 entity types (from `data/reference/neo4j_entities_deduplicated.csv`)
- ✅ 235 relationship types (from `data/backbone/relations/canonical_relationship_types.csv`)
- ✅ 248 entity hierarchy entries (from `data/backbone/relations/neo4j_entity_hierarchy.csv`)
- ✅ Action structure vocabularies (goals, triggers, actions, results)
- ✅ Wikidata mappings for action structures
- ✅ 13 temporal period definitions

---

## Source CSV Files

The script reads from these CSVs:

1. **`data/reference/neo4j_entities_deduplicated.csv`**
   - Entity types with Wikidata Q-IDs

2. **`data/backbone/relations/canonical_relationship_types.csv`** ⭐ **CANONICAL SOURCE**
   - 235 relationship types
   - With directionality, Wikidata P-properties
   - Includes backbone alignment (LCC, LCSH, FAST)

3. **`data/backbone/relations/neo4j_entity_hierarchy.csv`**
   - Parent-child relationships between entity types

4. **`data/reference/action_structure_vocabularies.csv`**
   - Goal, trigger, action, result type vocabularies

5. **`data/reference/action_structure_wikidata_mapping.csv`**
   - Wikidata Q-ID mappings for action structures

6. **`data/backbone/temporal/historical_periods_taxonomy.csv`**
   - Historical period definitions with date ranges

---

## Example Output

```
[OK] Consolidated schema written to: data\schemas\chrystallum_schema.json

Summary:
  Entities: 121
  Relationships: 235
  Entity Hierarchy: 248
  Goal Types: 10
  Trigger Types: 10
  Action Types: 15
  Result Types: 19
  Wikidata Mappings: 54
  Temporal Periods: 13
```

---

## When to Use

**Run this script whenever:**
- You add new relationship types to `canonical_relationship_types.csv`
- You modify entity types
- You update the entity hierarchy
- You need to regenerate the master schema JSON

---

## What I Just Fixed

### Updated `consolidate_schema.py` to:
1. ✅ Use canonical source: `data/backbone/relations/canonical_relationship_types.csv` (was using old CSV)
2. ✅ Use correct hierarchy: `data/backbone/relations/neo4j_entity_hierarchy.csv`
3. ✅ Use correct temporal periods: `data/backbone/temporal/historical_periods_taxonomy.csv`
4. ✅ Include backbone alignment fields (LCC, LCSH, FAST)
5. ✅ Update schema version to 3.3
6. ✅ Document canonical source in metadata

### Generated Fresh Schema:
- ✅ `data/schemas/chrystallum_schema.json` now has **235 relationships** (up from 191)
- ✅ All metadata updated to 2025-12-10
- ✅ References canonical source

---

## Related Updates I Made

While fixing the script, I also updated these critical files to match:

1. **`prompts/system/extraction_agent.txt`**
   - Added canonical source reference
   - Documents 235 relationship types

2. **`Docs/architecture/0- Graph Governance Specification.md`**
   - Updated to 235 relationships
   - Updated CSV paths

3. **`cypher_template_library.json`**
   - Added metadata section
   - Documents 235 total relationships
   - References canonical source

4. **`data/backbone/relations/canonical_relationship_types.csv`**
   - Removed duplicate header at line 29
   - Now clean 235 relationship types

---

## Verification

Check it worked:

```powershell
# Verify JSON was created
Test-Path data\schemas\chrystallum_schema.json

# Check relationship count
$json = Get-Content data\schemas\chrystallum_schema.json -Raw | ConvertFrom-Json
$json.relationships.count  # Should be: 235

# Verify canonical source
$json.metadata.source_files  # Should list: data/backbone/relations/canonical_relationship_types.csv
```

---

## Documentation

Full details in:
- **`SCRIPTS_AND_FILES_GUIDE.md`** - Complete guide to all scripts (now includes consolidate_schema.py)
- **`SCHEMA_UPDATES_COMPLETE.md`** - All schema updates completed today
- **`RELATIONSHIP_COUNT_CLARIFICATION.md`** - Why it's 235, not 236

---

## Summary

✅ **YES**, the script exists: `consolidate_schema.py`  
✅ It generates schema JSON from CSV files  
✅ I updated it to use the canonical sources  
✅ I ran it - generated `chrystallum_schema.json` with 235 relationships  
✅ All critical files now updated and consistent  

**Just run:** `python consolidate_schema.py` whenever you update CSVs!
