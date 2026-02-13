# Action Structure Wikidata Mapping - Complete

## Status: ✅ All Entries Mapped

**Vocabulary File**: `Reference/action_structure_vocabularies.csv` - **54 entries**  
**Mapping File**: `Reference/action_structure_wikidata_mapping.csv` - **54 entries**

---

## Breakdown by Category

| Category | Vocabulary Entries | Mapped Entries | Status |
|----------|-------------------|----------------|--------|
| **Goal Type** | 10 | 10 | ✅ Complete |
| **Trigger Type** | 10 | 10 | ✅ Complete |
| **Action Type** | 15 | 15 | ✅ Complete |
| **Result Type** | 19 | 19 | ✅ Complete |
| **Total** | **54** | **54** | ✅ **100% Complete** |

---

## Mapping Strategy

### 1. Entity Type QIDs (Strongest Alignment)
**Used when our codes map directly to entity types in our CSV schema**

Examples:
- `REVOL` → Q10931 (Revolution) - Already in entity CSV
- `MIL_ACT` → Q178561 (Battle) - Already in entity CSV
- `TREATY` → Q93288 (Treaty) - Already in entity CSV

**Count**: ~15 entries have direct entity type mappings

---

### 2. Concept QIDs (Semantic Classification)
**Used when our codes represent abstract concepts**

Examples:
- `POL` → Q7163 (politics) - Concept
- `MORAL` → Q177639 (ethics) - Concept
- `ECON` → Q11425 (economics) - Concept

**Count**: ~35 entries map to concept QIDs

---

### 3. Proxy Mappings (Best Fit)
**Used when no direct mapping exists, but a related concept fits**

Examples:
- `TYRANNY` → Q7188 (government) - Tyranny is a form of governance
- `SOC_ACT` → Q11042 (culture) - Social actions relate to culture
- `PERS_ACT` → Q5 (human) - Personal actions relate to human behavior

**Count**: ~4 entries use proxy mappings

---

## Key Improvements Made

### 1. **TYRANNY** Mapping
- **Before**: Q1067209 (modern history) - Not appropriate
- **After**: Q7188 (government) - Tyranny is a form of governance
- **Rationale**: Already in entity CSV as Government organization type

### 2. **AMB (Ambition)** Mapping
- **Before**: Q7163 (politics) - Too narrow
- **After**: Q5 (human) - Ambition is a personal human trait
- **Rationale**: Ambition can be personal, not necessarily political

### 3. **INSTABILITY** Mapping
- **Before**: Listed as Concept QID
- **After**: Q198 (war) - Entity Type QID from entity CSV
- **Rationale**: Instability often leads to conflict/war events

---

## Alignment Types

| Alignment Type | Count | Description |
|----------------|-------|-------------|
| **Entity Type QID** | ~15 | Direct mapping to entity types in our schema |
| **Concept QID** | ~35 | Abstract concepts from Wikidata |
| **Proxy Mapping** | ~4 | Best-fit related concepts |

---

## Usage

### In Code
```python
import csv

# Load mapping
with open('Reference/action_structure_wikidata_mapping.csv', 'r') as f:
    reader = csv.DictReader(f)
    mappings = {row['Our_Code']: row for row in reader}

# Get Wikidata QID for a code
code = 'REVOL'
if code in mappings:
    qid = mappings[code]['Wikidata_QID']
    label = mappings[code]['Wikidata_Label']
    print(f"{code} → {qid} ({label})")
```

### In Cypher Queries
```cypher
// Filter by goal type using Wikidata QID
MATCH (a)-[r:PERFORMED]->(e)
WHERE r.goal_type_qid = 'Q7163'  // Political
RETURN a, r, e
```

---

## Notes

1. **All entries are now mapped** - No missing mappings
2. **Mapping quality varies** - Some are direct, some are proxies
3. **Entity type mappings are strongest** - These align with our existing schema
4. **Concept mappings are semantic** - Useful for classification and queries
5. **Proxy mappings are best-fit** - May need refinement based on usage

---

## Recommendations

### 1. Use Entity Type Mappings First
When querying, prioritize entities that have direct entity type mappings (they align with our schema).

### 2. Store Both Codes and QIDs
In relationships, store both:
- `goal_type: 'POL'` (our semantic code)
- `goal_type_qid: 'Q7163'` (Wikidata QID for interoperability)

### 3. Validate Proxy Mappings
Monitor usage of proxy mappings (TYRANNY, SOC_ACT, etc.) and refine if needed.

---

## Files

- **Vocabulary Source**: `Reference/action_structure_vocabularies.csv`
- **Mapping File**: `Reference/action_structure_wikidata_mapping.csv`
- **Documentation**: `Docs/Action_Structure_Wikidata_Alignment.md`

