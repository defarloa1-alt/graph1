# Relationship Count Clarification

**Date:** December 10, 2025  
**Issue:** Documentation references both 235 and 236  
**Resolution:** Canonical count is **235 relationships**

---

## The Confusion

During consolidation, documentation referenced "236 relationships" but the actual canonical CSV has **235** relationships.

---

## Source of Truth

**File:** `relations/canonical_relationship_types.csv`

**Verified Count:**
```powershell
Import-Csv relations\canonical_relationship_types.csv | Measure-Object
# Result: 235 rows
```

**Breakdown by Category:**
```
Political:      39
Military:       23
Geographic:     18
Familial:       13
Legal:          13
Authorship:     12
Economic:       12
Diplomatic:     12
Attribution:    11
Institutional:   9
Position:        8
Honorific:       8
Cultural:        8
Causality:       8
Relations:       7
Temporal:        6
Religious:       6
Social:          4
Application:     4
Trade:           3
Moral:           3
Ideological:     2
Linguistic:      2
Membership:      2
Measurement:     2
---
TOTAL:         235
```

---

## What Happened

**Issue:** Line 29 in the original CSV was a duplicate header row:
```
Category,Relationship Type,Description,Parent_Relationship,Specificity_Level,,,,,,active,,bidirectional_csv,1.0
```

**Resolution:** 
- Removed duplicate header
- Regenerated `chrystallum_schema.json` with correct count
- Script now correctly shows 235 relationships

---

## Updated Files

### ✅ Already Correct (235)
- `Reference/chrystallum_schema.json` - Regenerated with 235 ✅
- `relations/canonical_relationship_types.csv` - Cleaned to 235 ✅

### ⚠️ Need Manual Update (still say 236)
- `Reference/llm_system_prompt.txt` - Update to 235
- `arch/0- Graph Governance Specification.md` - Update to 235
- `cypher_template_library.json` - Update to 235
- Various documentation files created during consolidation

---

## Correct References

**When documenting:**
- ✅ Use: "235 canonical relationship types"
- ✅ Source: `relations/canonical_relationship_types.csv`
- ❌ Don't say: "236 relationships"

---

## Why This Matters

**Accuracy:** Documentation should match actual data  
**Validation:** Schema validation checks will fail if expecting 236  
**Clarity:** Prevents confusion about missing relationship

---

*Canonical count is 235 relationship types, not 236.*

