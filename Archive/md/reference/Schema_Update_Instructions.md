# Schema Update Instructions - CRITICAL

**Priority:** 🔴 BLOCKING - Must complete before AI extraction  
**Date:** December 10, 2025  
**Impact:** 45 missing relationship types if not fixed

---

## Overview

Three files need urgent updates to reference the canonical 236 relationships:

1. `Reference/chrystallum_schema.json` - JSON schema (191 → 236)
2. `Reference/llm_system_prompt.txt` - LLM prompt (add source reference)
3. `arch/0- Graph Governance Specification.md` - Governance doc (106 → 236)

---

## 1. Update Reference/chrystallum_schema.json

**Current Problem:**
- Line 750: `"count": 191`
- Line 9: References old `neo4j_relationships_bidirectional.csv`

### Option A: Manual Update (Quick Fix)

**Step 1:** Update the count
```json
Line 750: Change from:
  "count": 191,

To:
  "count": 236,
```

**Step 2:** Update metadata source reference
```json
Lines 7-14: Change from:
  "source_files": [
    "neo4j_entities_deduplicated.csv",
    "neo4j_relationships_bidirectional.csv",  ← OLD
    "neo4j_entity_hierarchy.csv",
    ...
  ]

To:
  "source_files": [
    "neo4j_entities_deduplicated.csv",
    "relations/canonical_relationship_types.csv",  ← NEW
    "neo4j_entity_hierarchy.csv",
    ...
  ]
```

**Step 3:** Update last_updated
```json
Line 6: Change to:
  "last_updated": "2025-12-10",
```

**Step 4:** Add note about canonical source
Add after line 750:
```json
  "count": 236,
  "canonical_source": "relations/canonical_relationship_types.csv",
  "consolidation_date": "2025-12-10",
```

### Option B: Full Regeneration (Recommended)

**If you have a script to generate from CSV:**

```bash
# Regenerate entire JSON from canonical CSV
python scripts/generate_schema_json.py \
  --relationships relations/canonical_relationship_types.csv \
  --entities Reference/neo4j_entities_deduplicated.csv \
  --hierarchy relations/neo4j_entity_hierarchy.csv \
  --output Reference/chrystallum_schema.json
```

**If no script exists, this would need to be created.**

### Verification

```bash
# Check count updated
grep '"count":' Reference/chrystallum_schema.json | grep -A 1 relationships

# Should show:
#   "relationships": {
#     "description": "Relationship types with directionality and Wikidata properties",
#     "count": 236,
```

---

## 2. Update Reference/llm_system_prompt.txt

**Current Problem:**
- Line 14: References "relationship types defined in the schema" but doesn't specify which file
- No explicit reference to canonical source

### Update Required

**Add after line 14:**

```
2. **RELATIONSHIP TYPE RULE**: Use ONLY the relationship types defined in the canonical schema.
   
   CANONICAL SOURCE: relations/canonical_relationship_types.csv (236 types)
   JSON SCHEMA: Reference/chrystallum_schema.json
   
   Never invent new relationships. If a relationship seems needed but isn't in the
   canonical list, flag it for review rather than creating a custom type.
```

**Add to validation checklist (after line 148):**

```
Before returning output:
- [ ] All entity types are from the approved list
- [ ] All relationship types are from the canonical list (236 types)
- [ ] Canonical source: relations/canonical_relationship_types.csv
- [ ] All relationships respect the hierarchy rules
- [ ] No invented entity types or relationship types
- [ ] Confidence scores are justified
- [ ] Temporal dates are classified into appropriate historical periods
- [ ] JSON is valid and properly formatted
```

### Verification

```bash
# Check reference added
grep "canonical_relationship_types.csv" Reference/llm_system_prompt.txt

# Should return a match
```

---

## 3. Update arch/0- Graph Governance Specification.md

**Current Problem:**
- Line 12: "neo4j_relationships_bidirectional.csv (106 relationships + P-properties)"
- Multiple references to "106 relationships"

### Find and Replace

**Step 1:** Find all instances of old references

```bash
# Windows PowerShell
Select-String -Path "arch\0- Graph Governance Specification.md" -Pattern "106"

# Expected matches:
# Line 12: (106 relationships + P-properties)
# Possibly other lines mentioning "106"
```

**Step 2:** Update Line 12

```markdown
Before:
### Layer 1: Canonical Schema (Immutable CSVs)
- neo4j_entities_deduplicated.csv (120 types + Q-IDs)
- neo4j_entity_hierarchy.csv (112 parent-child relationships)
- neo4j_relationships_bidirectional.csv (106 relationships + P-properties)
- Source of truth for schema enforcement
- Changes require review and approval

After:
### Layer 1: Canonical Schema (Immutable CSVs)
- neo4j_entities_deduplicated.csv (120 types + Q-IDs)
- neo4j_entity_hierarchy.csv (112 parent-child relationships)
- relations/canonical_relationship_types.csv (236 relationships + backbone alignment)
- Source of truth for schema enforcement
- Changes require review and approval
- Consolidation completed: December 10, 2025
```

**Step 3:** Add note about consolidation

Add new section after Layer 1:

```markdown
### Schema Consolidation (December 2025)

**Note:** Relationship types were consolidated from multiple sources into a single
canonical CSV file:

**Previous sources (deprecated):**
- neo4j_relationships_bidirectional.csv (183 relationships)
- neo4j_relationships_deduplicated.csv (76 relationships)
- Relationshp Types Table.csv (79 relationships)
- Total: 338 relationships with duplicates

**Current canonical source:**
- relations/canonical_relationship_types.csv (236 unique relationships)
- Full backbone alignment: LCC, LCSH, FAST, MARC codes
- Wikidata property mappings
- Hierarchical structure and directionality metadata
- Documentation: relations/CONSOLIDATION_COMPLETE.md

**Deprecated files moved to:** relations/deprecated/
```

**Step 4:** Update references throughout document

Find any other mentions of "106" or old CSV names and update:

```markdown
Change: "from the bidirectional set"
To: "from the canonical relationship types"

Change: "in bidirectional CSV"
To: "in canonical_relationship_types.csv"
```

### Verification

```bash
# Check no old references remain
grep -E "(106|183|191) relationship" "arch\0- Graph Governance Specification.md"

# Should return: nothing

# Check canonical source referenced
grep "canonical_relationship_types" "arch\0- Graph Governance Specification.md"

# Should return: matches found
```

---

## Quick Verification Script

After making all changes, run this to verify:

```powershell
# Create verification script
$issues = @()

# Check chrystallum_schema.json
$json = Get-Content "Reference\chrystallum_schema.json" -Raw
if ($json -match '"count":\s*191') {
    $issues += "❌ chrystallum_schema.json still has count: 191"
} elseif ($json -match '"count":\s*236') {
    Write-Host "✅ chrystallum_schema.json count updated to 236"
} else {
    $issues += "⚠️ chrystallum_schema.json count not found"
}

# Check llm_system_prompt.txt
$prompt = Get-Content "Reference\llm_system_prompt.txt" -Raw
if ($prompt -match "canonical_relationship_types\.csv") {
    Write-Host "✅ llm_system_prompt.txt references canonical source"
} else {
    $issues += "❌ llm_system_prompt.txt missing canonical source reference"
}

# Check Graph Governance Specification
$governance = Get-Content "arch\0- Graph Governance Specification.md" -Raw
if ($governance -match "106 relationship") {
    $issues += "❌ Graph Governance still references 106 relationships"
} elseif ($governance -match "236|canonical_relationship_types") {
    Write-Host "✅ Graph Governance updated to canonical source"
} else {
    $issues += "⚠️ Graph Governance may need review"
}

# Report
if ($issues.Count -eq 0) {
    Write-Host "`n🎉 All schema updates complete!`n"
} else {
    Write-Host "`n⚠️ Issues found:`n"
    $issues | ForEach-Object { Write-Host "  $_" }
}
```

---

## Testing After Update

Once all files are updated, test with:

### 1. Schema Validation

```python
import json

# Load and validate JSON
with open('Reference/chrystallum_schema.json', 'r') as f:
    schema = json.load(f)

# Check relationship count
rel_count = schema['relationships']['count']
print(f"Relationship count: {rel_count}")
assert rel_count == 236, f"Expected 236, got {rel_count}"

# Check canonical source referenced
assert 'canonical_relationship_types.csv' in str(schema), \
    "Canonical source not referenced"

print("✅ Schema validation passed")
```

### 2. CSV Verification

```bash
# Verify canonical CSV has 236 relationships
wc -l relations/canonical_relationship_types.csv

# Should show: 237 (236 relationships + 1 header line)
```

### 3. Cross-Reference Check

```python
# Verify canonical CSV matches JSON count
import csv
import json

# Count CSV rows
with open('relations/canonical_relationship_types.csv', 'r') as f:
    csv_count = len(list(csv.DictReader(f)))

# Check JSON count
with open('Reference/chrystallum_schema.json', 'r') as f:
    json_count = json.load(f)['relationships']['count']

print(f"CSV rows: {csv_count}")
print(f"JSON count: {json_count}")
assert csv_count == json_count, "Counts don't match!"

print("✅ CSV and JSON counts match")
```

---

## Rollback Plan (If Issues Occur)

If updates cause problems:

```bash
# Restore from git
git checkout HEAD -- Reference/chrystallum_schema.json
git checkout HEAD -- Reference/llm_system_prompt.txt
git checkout HEAD -- "arch/0- Graph Governance Specification.md"

# Then try manual updates more carefully
```

---

## Post-Update Documentation

After completing updates, create a note:

```markdown
# Schema Update Complete - December 10, 2025

## Changes Made

1. ✅ Reference/chrystallum_schema.json
   - Updated count: 191 → 236
   - Updated source reference to canonical CSV
   - Updated last_modified date

2. ✅ Reference/llm_system_prompt.txt
   - Added canonical source reference
   - Updated validation checklist

3. ✅ arch/0- Graph Governance Specification.md
   - Updated relationship count: 106 → 236
   - Added consolidation note
   - Updated CSV references

## Verification

- [x] All counts show 236
- [x] No references to 106, 183, or 191 remain
- [x] Canonical CSV referenced in all files
- [x] JSON schema validates
- [x] CSV and JSON counts match

## Ready for Use

System is now ready for AI extraction with full 236 relationship types.
```

---

## Priority Order

1. **URGENT:** Update `llm_system_prompt.txt` (5 minutes - simple text addition)
2. **URGENT:** Update `Graph Governance Specification` (10 minutes - find/replace)
3. **CRITICAL:** Update `chrystallum_schema.json` (15-30 minutes depending on method)

**Total Time:** 30-45 minutes for manual updates

---

*Complete these updates before proceeding with any AI extraction work to ensure all 236 relationship types are available.*


