# Complete Taxonomy Relationships - Structural Analysis

**Root:** Q17167 (Roman Republic)  
**Fetched:** 12 entities, 29 relationships  
**All IDs include labels** ✅

---

## 🔼 UPWARD RELATIONSHIPS (Parents & Grandparents)

### Hop 1 Up: Direct Parents of Roman Republic

| From QID | From Label | Relationship | To QID | To Label | Notes |
|----------|------------|--------------|--------|----------|-------|
| Q17167 | Roman Republic | **P31** instance of | Q11514315 | **historical period** | Primary type (preferred) |
| Q17167 | Roman Republic | **P31** instance of | Q1307214 | **form of government** | Political type |
| Q17167 | Roman Republic | **P31** instance of | Q48349 | **empire** | Interesting paradox! |
| Q17167 | Roman Republic | **P31** instance of | Q3024240 | **historical country** | Geopolitical type (preferred) |
| Q17167 | Roman Republic | **P361** part of | Q1747689 | **Ancient Rome** | Parent civilization |

### Hop 2 Up: Grandparents (from each parent)

| From QID | From Label | Relationship | To QID | To Label | Chain |
|----------|------------|--------------|--------|----------|-------|
| **From Q11514315 (historical period):** |
| Q11514315 | historical period | **P279** subclass of | Q6428674 | **era** | Roman Republic → historical period → era |
| **From Q1307214 (form of government):** |
| Q1307214 | form of government | **P31** instance of | Q19478619 | **metaclass** | Roman Republic → form of gov → metaclass |
| Q1307214 | form of government | **P279** subclass of | Q183039 | **form of state** | Roman Republic → form of gov → form of state |
| Q1307214 | form of government | **P279** subclass of | Q2752458 | **administrative type** | Roman Republic → form of gov → admin type |
| Q1307214 | form of government | **P279** subclass of | Q28108 | **political system** | Roman Republic → form of gov → political system |
| **From Q48349 (empire):** |
| Q48349 | empire | **P31** instance of | Q7269 | **monarchy** | Roman Republic → empire → monarchy |
| Q48349 | empire | **P279** subclass of | Q1250464 | **realm** | Roman Republic → empire → realm |
| Q48349 | empire | **P279** subclass of | Q3624078 | **sovereign state** | Roman Republic → empire → sovereign state |
| **From Q3024240 (historical country):** |
| Q3024240 | historical country | **P279** subclass of | Q19953632 | **former administrative territorial entity** | Roman Republic → historical country → former entity |
| Q3024240 | historical country | **P279** subclass of | Q96196009 | **former or current state** | Roman Republic → historical country → state |
| Q3024240 | historical country | **P279** subclass of | Q19832712 | **historical administrative division** | Roman Republic → historical country → division |
| Q3024240 | historical country | **P279** subclass of | Q6256 | **country** | Roman Republic → historical country → country |
| **From Q1747689 (Ancient Rome):** |
| Q1747689 | Ancient Rome | **P31** instance of | Q3024240 | **historical country** | Circular reference! |
| Q1747689 | Ancient Rome | **P361** part of | Q120754777 | **Roman civilization** | Roman Republic → Ancient Rome → civilization |
| Q1747689 | Ancient Rome | **P279** subclass of | Q465299 | **archaeological culture** | Roman Republic → Ancient Rome → arch culture |
| Q1747689 | Ancient Rome | **P279** subclass of | Q120754777 | **Roman civilization** | Roman Republic → Ancient Rome → civilization |

---

## 🔽 DOWNWARD RELATIONSHIPS (Children & Grandchildren)

### Hop 1 Down: Direct Children of Roman Republic

| From QID | From Label | Relationship | To QID | To Label | Date Range |
|----------|------------|--------------|--------|----------|------------|
| Q17167 | Roman Republic | **P527** has parts | Q2839628 | **Early Roman Republic** | 509-265 BC |
| Q17167 | Roman Republic | **P527** has parts | Q6106068 | **Middle Roman Republic** | 264-146 BC |
| Q17167 | Roman Republic | **P527** has parts | Q2815472 | **Late Roman Republic** | 145-27 BC |

### Hop 2 Down: Grandchildren

| From QID | From Label | Relationship | To QID | To Label | Notes |
|----------|------------|--------------|--------|----------|-------|
| - | - | - | - | **NONE FOUND** | All 3 periods are leaf nodes |

**Analysis:** The 3 temporal subdivisions have NO further subdivisions.

---

## ⏱️ SUCCESSION RELATIONSHIPS (Timeline)

### Complete Succession Chain:

| From QID | From Label | Relationship | To QID | To Label | Date Transition |
|----------|------------|--------------|--------|----------|-----------------|
| Q201038 | **Roman Kingdom** | **P155** follows | Q17167 | **Roman Republic** | 509 BC (monarchy → republic) |
| Q17167 | **Roman Republic** | **P156** followed by | Q2277 | **Roman Empire** | 27 BC (republic → empire) |
| Q17167 | **Roman Republic** | **P156** followed by | Q206414 | **Principate** | 27 BC (republic → principate) |

**Timeline Visualization:**
```
753 BC              509 BC              27 BC               476 AD
   │                   │                   │                   │
   ├─ Roman Kingdom ───┤                   │                   │
   │                   │                   │                   │
   │                   ├─ Early (509-265)──┤                   │
   │                   ├─ Middle (264-146)─┤                   │
   │                   ├─ Late (145-27) ───┤                   │
   │                   │                   │                   │
   │                   │                   ├─ Principate ──────┤
   │                   │                   │                   │
   │                   │                   ├─ Roman Empire ────┼──→ 1453 AD
```

---

## 📊 PROPERTY DISTRIBUTION ANALYSIS

### Entities by Complexity (Property Count):

| Category | QID | Label | Properties | Complexity |
|----------|-----|-------|------------|------------|
| **High Complexity** | Q1747689 | Ancient Rome | 114 | Very High |
| **High Complexity** | Q2277 | Roman Empire | 102 | Very High |
| **Medium-High** | Q17167 | Roman Republic | 61 | High |
| **Medium-High** | Q48349 | empire | 55 | High |
| **Medium** | Q201038 | Roman Kingdom | 38 | Medium |
| **Medium** | Q1307214 | form of government | 30 | Medium |
| **Medium** | Q206414 | Principate | 24 | Medium |
| **Low** | Q11514315 | historical period | 20 | Low |
| **Low** | Q3024240 | historical country | 16 | Low |
| **Very Low** | Q2815472 | Late Roman Republic | 10 | Very Low |
| **Very Low** | Q2839628 | Early Roman Republic | 8 | Very Low |
| **Very Low** | Q6106068 | Middle Roman Republic | 8 | Very Low |

**Total Properties Across All 12 Entities:** ~554

---

## 🎯 DOMAIN BUILDING INSIGHTS

### 1. **Immediate Next Queries:**

These entities have the most data and should be explored next:

| Priority | QID | Label | Properties | Why Important |
|----------|-----|-------|------------|---------------|
| **1** | Q1747689 | Ancient Rome | 114 | Parent civilization - richest data |
| **2** | Q2277 | Roman Empire | 102 | Successor - equally rich |
| **3** | Q48349 | empire | 55 | Abstract concept - may have field of study |
| **4** | Q201038 | Roman Kingdom | 38 | Predecessor - complete trilogy |

### 2. **Classification Insights:**

**Roman Republic has MULTIPLE classifications:**
- ✅ Temporal: "historical period"
- ✅ Political: "form of government"
- ✅ Geopolitical: "historical country"
- ✅ Imperial: "empire" (paradox!)

This means we can create SubjectConcepts for:
- Roman Republic (the period)
- Roman Republic (the government system)
- Roman Republic (the state/country)

### 3. **Hierarchy Depth:**

**Maximum upward depth:** 2 hops (can go deeper)
- Roman Republic → historical period → era
- Roman Republic → form of government → political system
- Roman Republic → Ancient Rome → Roman civilization

**Maximum downward depth:** 1 hop (no grandchildren)
- Roman Republic → Early/Middle/Late (leaf nodes)

### 4. **Missing Academic Links:**

Still NO:
- ❌ Field of study (P2579)
- ❌ Academic discipline (P101)
- ❌ Practiced by (P3095)

**Why?** These are on ABSTRACT CONCEPTS, not historical entities.

**To find them:** Query Q48349 (empire) or Q1307214 (form of government) - these abstract concepts might have "studied by" properties.

---

## 📁 OUTPUT FILES

1. **JSON:** `output/taxonomy_recursive/Q17167_recursive_20260220_134235.json`
   - Complete data for all 12 entities
   - All 29 relationships
   - All properties and values with labels

2. **Analysis:** This file (TAXONOMY_RELATIONSHIPS_TABLE.md)
   - Structured tables
   - All relationships mapped
   - Ready for domain construction

---

## 🔍 WHAT'S NEXT?

**Option 1:** Analyze Ancient Rome (Q1747689) - 114 properties!  
**Option 2:** Analyze abstract concepts (Q48349 empire, Q1307214 form of government)  
**Option 3:** Build SubjectConcepts from these 12 entities  
**Option 4:** Clear Aura and start fresh with this taxonomy

**Which direction should we go?** 🎯
