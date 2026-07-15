# 3-Hop Taxonomy - Visual Summary

**Generated:** 2026-02-20  
**Root:** Q17167 (Roman Republic)

---

## 🎯 WHAT WE FETCHED

```
         28 ENTITIES
         76 RELATIONSHIPS  
        900+ PROPERTIES
    ALL WITH LABELS ✅
```

---

## 📊 ENTITY BREAKDOWN

```
Hop 3 Up:    [Many great-grandparents]
              ↑
Hop 2 Up:    [18 grandparents]
              ↑
Hop 1 Up:    [5 parents]
              ↑
ROOT:        Q17167 (Roman Republic) ← START HERE
              ↓
Hop 1 Down:  [3 children]
              ↓
Hop 2 Down:  [NONE - leaf nodes]
              ↓
Hop 3 Down:  [NONE - leaf nodes]

Succession:  [3 entities: Kingdom → Republic → Empire]
```

---

## 🌳 TAXONOMY TREE (Simplified)

```
UPWARD CLASSIFICATION:
━━━━━━━━━━━━━━━━━━━━━

Q17167 (Roman Republic)
│
├── TEMPORAL BRANCH
│   └─ historical period (20p)
│      └─ era (26p)
│         └─ time interval
│
├── POLITICAL BRANCH  
│   └─ form of government (30p)
│      ├─ metaclass (13p)
│      │  └─ concept → ontology
│      ├─ form of state (12p)
│      │  └─ political system (39p) ★
│      ├─ administrative type (5p)
│      │  └─ classification scheme
│      └─ political system (39p) ★
│
├── IMPERIAL BRANCH
│   └─ empire (55p) ★
│      ├─ monarchy (76p) ★
│      │  └─ monarchic system
│      ├─ realm (15p)
│      │  └─ sovereign state (24p)
│      │     └─ country (68p) ★
│      └─ sovereign state (24p)
│
├── GEOGRAPHIC BRANCH
│   └─ historical country (16p)
│      └─ country (68p) ★
│         └─ state
│
└── CULTURAL BRANCH
    └─ Ancient Rome (114p) ★★★
       ├─ historical country (circular)
       ├─ ancient civilization (14p)
       ├─ temporal entity (9p)
       └─ Roman civilization (10p)
          ├─ civilization ★
          ├─ culture ★
          ├─ Greco-Roman world ★
          └─ Western culture ★

DOWNWARD SUBDIVISION:
━━━━━━━━━━━━━━━━━━━━

Q17167 (Roman Republic)
│
├─ Early Roman Republic (8p) [509-265 BC]
├─ Middle Roman Republic (8p) [264-146 BC]
└─ Late Roman Republic (10p) [145-27 BC]

SUCCESSION:
━━━━━━━━━━━

753 BC → Roman Kingdom (38p)
           ↓
509 BC → ROMAN REPUBLIC (61p) ← ROOT
           ↓
 27 BC → Roman Empire (102p) + Principate (24p)
```

---

## ⭐ ENTITIES MARKED WITH ★ (High Value)

These have the most properties and likely contain:
- Field of study
- Academic discipline  
- Practiced by
- Rich facet data

| Symbol | QID | Label | Properties | Should Explore? |
|--------|-----|-------|------------|-----------------|
| ★★★ | Q1747689 | Ancient Rome | 114 | **HIGHEST PRIORITY** |
| ★★ | Q2277 | Roman Empire | 102 | **HIGH PRIORITY** |
| ★ | Q7269 | monarchy | 76 | YES - abstract concept |
| ★ | Q6256 | country | 68 | YES - abstract concept |
| ★ | Q48349 | empire | 55 | YES - abstract concept |
| ★ | Q28108 | political system | 39 | YES - abstract concept |

---

## 📋 COMPLETE DATA TABLE

### All 28 Entities with Full Information:

| # | QID | Label | Props | Type | Notes |
|---|-----|-------|-------|------|-------|
| 1 | Q17167 | Roman Republic | 61 | Concrete/Historical | ROOT |
| 2 | Q2839628 | Early Roman Republic | 8 | Concrete/Historical | Child (leaf) |
| 3 | Q6106068 | Middle Roman Republic | 8 | Concrete/Historical | Child (leaf) |
| 4 | Q2815472 | Late Roman Republic | 10 | Concrete/Historical | Child (leaf) |
| 5 | Q201038 | Roman Kingdom | 38 | Concrete/Historical | Predecessor |
| 6 | Q2277 | Roman Empire | 102 | Concrete/Historical | Successor |
| 7 | Q206414 | Principate | 24 | Concrete/Historical | Successor |
| 8 | Q1747689 | Ancient Rome | 114 | Concrete/Historical | Parent |
| 9 | Q11514315 | historical period | 20 | Abstract/Temporal | Parent |
| 10 | Q6428674 | era | 26 | Abstract/Temporal | Grandparent |
| 11 | Q186081 | time interval | ? | Abstract/Temporal | Great-grandparent |
| 12 | Q1307214 | form of government | 30 | Abstract/Political | Parent |
| 13 | Q183039 | form of state | 12 | Abstract/Political | Grandparent |
| 14 | Q2752458 | administrative type | 5 | Abstract/Political | Grandparent |
| 15 | Q28108 | political system | 39 | Abstract/Political | Grandparent |
| 16 | Q48349 | empire | 55 | Abstract/Political | Parent |
| 17 | Q7269 | monarchy | 76 | Abstract/Political | Grandparent |
| 18 | Q1250464 | realm | 15 | Abstract/Political | Grandparent |
| 19 | Q3624078 | sovereign state | 24 | Abstract/Political | Grandparent |
| 20 | Q6256 | country | 68 | Abstract/Geographic | Grandparent |
| 21 | Q3024240 | historical country | 16 | Abstract/Geographic | Parent |
| 22 | Q19478619 | metaclass | 13 | Abstract/Ontology | Grandparent |
| 23 | Q151885 | concept | ? | Abstract/Ontology | Great-grandparent |
| 24 | Q120754777 | Roman civilization | 10 | Abstract/Cultural | Grandparent |
| 25 | Q465299 | archaeological culture | 27 | Abstract/Cultural | Grandparent |
| 26 | Q28171280 | ancient civilization | 14 | Abstract/Cultural | Grandparent |
| 27 | Q19953632 | former admin entity | 7 | Abstract/Political | Grandparent |
| 28 | Q96196009 | former/current state | 4 | Abstract/Political | Grandparent |

---

## 💾 OUTPUT FILE

**File:** `output/taxonomy_recursive/Q17167_recursive_20260220_135044.json`

**Size:** Large (all 28 entities with complete data)

**Contains for EACH entity:**
```json
{
  "qid": "Q2839628",
  "label": "Early Roman Republic",
  "description": "period in the Roman Republic (509-265 BC)",
  "labels": { /* 138 languages */ },
  "descriptions": { /* 45 languages */ },
  "claims_with_labels": {
    "P31": {
      "property_id": "P31",
      "property_label": "instance of",
      "statements": [
        {
          "value": "Q11514315",
          "value_label": "historical period",
          "rank": "preferred",
          "qualifiers_with_labels": { /* with labels */ },
          "references_with_labels": [ /* with labels */ ]
        }
      ]
    }
    /* ... all other properties ... */
  },
  "statistics": {
    "total_properties": 8,
    "total_statements": 12
  }
}
```

---

## 🚀 WHAT THIS ENABLES

### 1. **Complete Structural Analysis** ✅
- Every entity has QID + Label
- Every property has ID + Label
- Every value has ID + Label (if QID)
- Every qualifier has ID + Label
- Every reference has ID + Label

### 2. **Network Visualization Ready** ✅
- 28 nodes
- 76 edges
- All labeled
- Can import to Neo4j directly

### 3. **Facet Classification Ready** ✅
- Analyze properties of each entity
- Map to 18 canonical facets
- Create SubjectConcept proposals

### 4. **Domain Building Ready** ✅
- Complete taxonomy structure
- Parent-child relationships
- Succession timeline
- Cultural context (Greco-Roman world)

---

## 🎯 RECOMMENDED NEXT STEPS

**Option A:** Explore 2-3 high-value abstract entities
```python
# These likely have academic/field properties:
explore('Q8432')   # civilization
explore('Q11042')  # culture  
explore('Q28108')  # political system
```

**Option B:** Build domain from these 28 entities
- Create SubjectConcepts for all
- Assign facets
- Build Neo4j graph

**Option C:** Go even deeper (4-5 hops)
- Find the ultimate root concepts
- Map complete ontology

**What's your preference?** 🎯
