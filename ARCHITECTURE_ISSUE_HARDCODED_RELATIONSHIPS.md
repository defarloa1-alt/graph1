# CRITICAL ARCHITECTURE ISSUE: Hardcoded Relationship Whitelist

**Date:** February 22, 2026  
**Severity:** CRITICAL  
**Component:** `scripts/neo4j/import_relationships.py`  
**Impact:** Missing hundreds of relationships from Wikidata

---

## Issue Description

**Current Implementation:**
```python
# Lines 27-47: Hardcoded whitelist (only 19 properties)
RELATIONSHIP_MAP = {
    'P31': 'INSTANCE_OF',
    'P279': 'SUBCLASS_OF',
    'P361': 'PART_OF',
    'P527': 'HAS_PARTS',
    # ... 15 more
}

# Lines 88-89: WHITELIST FILTER
if prop_id not in RELATIONSHIP_MAP:
    continue  # ← SKIPS ALL OTHER PROPERTIES!
```

**Problem:**
- Wikidata has ~11,000 properties (PIDs)
- Checkpoint data likely contains 100-300 properties
- Script only imports 19 properties
- **Missing:** P39 (position held), P40 (child), P26 (spouse), P710 (participant), P607 (conflict), etc.

**Contradiction:**
- User requirement: "Pull all data we can"
- Script behavior: "Pull only 19 hardcoded types"
- Registry: 314 relationship types defined
- Database: Only 5 types match registry (1.6%!)

---

## Impact Assessment

**Current Database State:**
- Entity-to-entity relationships: 784
- Relationship types: 19
- Avg per entity: 0.30

**If We Import ALL Properties:**
- Estimated relationships: 5,000-15,000 (depends on checkpoint data)
- Relationship types: 100-300
- Avg per entity: 2-6 (much better!)

**Gap:**
- 4,000-14,000 missing relationships
- 80-280 missing relationship types
- **This is why the graph looks "junky"!**

---

## Root Cause Analysis

**Why Was It Hardcoded?**

Possible reasons:
1. **Safety:** Only import known, validated relationship types
2. **Mapping:** Need canonical names for Wikidata PIDs
3. **Testing:** Start small, add more later
4. **Governance:** Control which relationships enter the graph

**Architectural Tension:**
- Conservative: Whitelist (quality control)
- Comprehensive: Import all (complete data)

**Current approach:** Conservative (too conservative!)

---

## Proposed Solutions

### **Solution 1: Dynamic Property Mapping (RECOMMENDED)**

**Approach:** Use the 314-relationship registry as the whitelist

```python
def load_relationship_registry():
    """Load canonical relationship map from registry CSV"""
    import csv
    
    registry = {}
    with open('Relationships/relationship_types_registry_master.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wikidata_pid = row.get('wikidata_property', '').strip()
            rel_type = row.get('relationship_type', '').strip()
            lifecycle = row.get('lifecycle_status', '')
            
            if wikidata_pid and rel_type and lifecycle == 'implemented':
                registry[wikidata_pid] = rel_type
    
    return registry

# Use dynamic registry instead of hardcoded map
RELATIONSHIP_MAP = load_relationship_registry()
# Now has ~95 mapped properties instead of 19!
```

**Benefits:**
- ✅ Uses canonical registry (single source of truth)
- ✅ Imports ~95 properties instead of 19 (5x increase!)
- ✅ No hardcoding (registry updates automatically propagate)
- ✅ Governance (only 'implemented' lifecycle status)

**Drawbacks:**
- ⚠️ Still limited to properties in registry
- ⚠️ ~200 unmapped properties remain in checkpoint data

---

### **Solution 2: Import All + Quarantine Unknown (COMPREHENSIVE)**

**Approach:** Import ALL properties, mark unmapped ones for review

```python
def generate_relationship_with_fallback(prop_id, qid_from, qid_to):
    """Import relationship with registry lookup + fallback"""
    
    # Check if in registry
    if prop_id in RELATIONSHIP_MAP:
        rel_type = RELATIONSHIP_MAP[prop_id]
        lifecycle_status = 'implemented'
    else:
        # Fallback: Use PID as relationship type
        rel_type = f"WIKIDATA_{prop_id}"
        lifecycle_status = 'unmapped'
    
    cypher = f"""
MATCH (from:Entity {{qid: '{qid_from}'}})
MATCH (to:Entity {{qid: '{qid_to}'}})
MERGE (from)-[r:{rel_type}]->(to)
ON CREATE SET
  r.wikidata_pid = '{prop_id}',
  r.lifecycle_status = '{lifecycle_status}',
  r.needs_mapping = {lifecycle_status == 'unmapped'},
  r.created_at = datetime(),
  r.source = 'wikidata';
"""
    return cypher
```

**Benefits:**
- ✅ Imports ALL relationship data
- ✅ No data loss
- ✅ Can review unmapped properties later
- ✅ Complete graph structure visible

**Drawbacks:**
- ⚠️ Unmapped relationships need review
- ⚠️ More relationship types in database (100-300)
- ⚠️ Need cleanup process for unmapped types

---

### **Solution 3: Tiered Import (PRAGMATIC)**

**Approach:** Import in phases based on priority

**Phase 1: Core Hierarchical (Current - 4 types)**
```python
CORE_PROPERTIES = {'P31', 'P279', 'P361', 'P527'}
```

**Phase 2: Registry Implemented (95 types)**
```python
REGISTRY_PROPERTIES = load_relationship_registry(lifecycle='implemented')
# ~95 properties from canonical registry
```

**Phase 3: Registry Candidates (108 types)**
```python
CANDIDATE_PROPERTIES = load_relationship_registry(lifecycle='candidate')
# Another ~108 properties marked as candidates
```

**Phase 4: All Remaining (Unknown count)**
```python
ALL_PROPERTIES = set(checkpoint_data_properties)
# Import everything, mark for review
```

**Benefits:**
- ✅ Incremental expansion
- ✅ Quality control (validate each phase)
- ✅ Can stop at any phase
- ✅ Clear governance

---

## Recommended Action

**Immediate (5 minutes):**

Replace hardcoded map with dynamic registry load:

```python
# OLD (Lines 27-47)
RELATIONSHIP_MAP = {
    'P31': 'INSTANCE_OF',
    # ... 18 more hardcoded
}

# NEW
def load_relationship_registry():
    import csv
    registry = {}
    with open('Relationships/relationship_types_registry_master.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get('wikidata_property', '').strip()
            rel_type = row.get('relationship_type', '').strip()
            if pid and rel_type and row.get('lifecycle_status') == 'implemented':
                registry[pid] = rel_type
    return registry

RELATIONSHIP_MAP = load_relationship_registry()
print(f"Loaded {len(RELATIONSHIP_MAP)} relationship types from registry")
```

**Expected Result:**
- Before: 19 properties → 784 relationships
- After: ~95 properties → 3,000-8,000 relationships (estimated)
- Ratio: 5x more relationships imported!

---

## Validation

**Check what's in the checkpoint:**
```python
# Count all properties in checkpoint
import json

with open('output/checkpoints/QQ17167_checkpoint_20260221_061318.json') as f:
    data = json.load(f)

all_props = set()
for qid, entity in data['entities'].items():
    all_props.update(entity.get('claims', {}).keys())

print(f"Total properties in checkpoint: {len(all_props)}")
print(f"Hardcoded whitelist: 19")
print(f"Registry implemented: ~95")
print(f"Missing from current import: {len(all_props) - 19}")
```

---

## Answer to Your Questions

### **1. Are we pulling all the data we can?**

❌ **NO!**
- Checkpoint likely has 100-300 properties
- Script only imports 19 properties
- **Missing: 80-280 relationship types** from available data

### **2. If we get P361 (part of), has an edge been created?**

✅ **YES!**
- Line 30: `'P361': 'PART_OF'` in hardcoded map
- Lines 103-114: Creates `MERGE (from)-[r:PART_OF]->(to)`
- Current database: 35 PART_OF relationships exist

**But only for entities already in database!**
- Line 101: `if qid_to in all_qids` ← Only if target entity loaded

---

## Architectural Recommendation

**Replace hardcoded whitelist with dynamic registry:**

**Benefits:**
- 5x more relationships imported immediately
- Single source of truth (registry CSV)
- Governance maintained (lifecycle_status filter)
- Aligns with requirement ("pull all data")

**Action:** Update `import_relationships.py` to use registry (5-minute fix)

**Should I create the updated script?** 🎯