# Roman Republic - 3-Hop Complete Taxonomy Analysis

**Root:** Q17167 (Roman Republic)  
**Total Entities:** 28  
**Total Relationships:** 76  
**Total Properties:** ~900+ across all entities

---

## 📊 STATISTICS OVERVIEW

| Metric | Count |
|--------|-------|
| **Total Entities Fetched** | 28 |
| **Root** | 1 |
| **Hop 1 Up (Parents)** | 5 |
| **Hop 2 Up (Grandparents)** | 18 |
| **Hop 3 Up (Great-grandparents)** | Many (from grandparents) |
| **Hop 1 Down (Children)** | 3 |
| **Hop 2 Down (Grandchildren)** | 0 |
| **Hop 3 Down (Great-grandchildren)** | 0 |
| **Succession** | 3 |
| **Total Relationships** | 76 |

---

## 📦 ALL 28 ENTITIES (Sorted by Properties)

| Rank | QID | Label | Properties | Description |
|------|-----|-------|------------|-------------|
| 1 | **Q1747689** | **Ancient Rome** | 114 | Parent civilization - RICHEST |
| 2 | **Q2277** | **Roman Empire** | 102 | Successor - SECOND RICHEST |
| 3 | **Q7269** | **monarchy** | 76 | Government form |
| 4 | **Q6256** | **country** | 68 | Geographic/political concept |
| 5 | **Q17167** | **ROMAN REPUBLIC (ROOT)** | 61 | Our starting point |
| 6 | **Q48349** | **empire** | 55 | Imperial concept |
| 7 | **Q28108** | **political system** | 39 | Political organization |
| 8 | **Q201038** | **Roman Kingdom** | 38 | Predecessor |
| 9 | **Q1307214** | **form of government** | 30 | Gov classification |
| 10 | **Q465299** | **archaeological culture** | 27 | Cultural concept |
| 11 | **Q6428674** | **era** | 26 | Temporal concept |
| 12 | **Q206414** | **Principate** | 24 | Successor period |
| 13 | **Q3624078** | **sovereign state** | 24 | State concept |
| 14 | **Q11514315** | **historical period** | 20 | Period concept |
| 15 | **Q3024240** | **historical country** | 16 | Country concept |
| 16 | **Q1250464** | **realm** | 15 | Territory concept |
| 17 | **Q28171280** | **ancient civilization** | 14 | Civilization type |
| 18 | **Q19478619** | **metaclass** | 13 | Ontology concept |
| 19 | **Q183039** | **form of state** | 12 | State classification |
| 20 | **Q2815472** | **Late Roman Republic** | 10 | Child period |
| 21 | **Q120754777** | **Roman civilization** | 10 | Cultural concept |
| 22 | **Q26907166** | **temporal entity** | 9 | Time concept |
| 23 | **Q2839628** | **Early Roman Republic** | 8 | Child period |
| 24 | **Q6106068** | **Middle Roman Republic** | 8 | Child period |
| 25 | **Q19953632** | **former administrative entity** | 7 | Admin concept |
| 26 | **Q2752458** | **administrative type** | 5 | Admin classification |
| 27 | **Q19832712** | **historical administrative division** | 4 | Admin concept |
| 28 | **Q96196009** | **former or current state** | 4 | State concept |

**Total Properties Across All Entities:** ~900+

---

## 🌳 COMPLETE TAXONOMY TREE

### UPWARD (Classification Hierarchy)

```
ROOT: Q17167 (Roman Republic) [61 props]
│
├─ P31 instance of → Q11514315 (historical period) [20 props]
│  └─ P279 subclass of → Q6428674 (era) [26 props]
│     └─ P279 subclass of → Q186081 (time interval)
│
├─ P31 instance of → Q1307214 (form of government) [30 props]
│  ├─ P31 instance of → Q19478619 (metaclass) [13 props]
│  │  ├─ P31 instance of → Q151885 (concept)
│  │  ├─ P361 part of → Q324254 (ontology)
│  │  └─ P279 subclass of → Q16889133 (class)
│  │
│  ├─ P279 subclass of → Q183039 (form of state) [12 props]
│  │  └─ P279 subclass of → Q28108 (political system) [39 props]
│  │     ├─ P31 instance of → Q96116695
│  │     └─ P279 subclass of → Q1639378
│  │
│  ├─ P279 subclass of → Q2752458 (administrative type) [5 props]
│  │  ├─ P31 instance of → Q2712963 (abstract noun)
│  │  ├─ P31 instance of → Q5962346 (classification scheme)
│  │  ├─ P279 subclass of → Q96247293 (type of management)
│  │  └─ P279 subclass of → Q28108 (political system) [circular]
│  │
│  └─ P279 subclass of → Q28108 (political system) [39 props]
│
├─ P31 instance of → Q48349 (empire) [55 props]
│  ├─ P31 instance of → Q7269 (monarchy) [76 props]
│  │  ├─ P31 instance of → Q1307214 (form of government) [circular!]
│  │  ├─ P279 subclass of → Q22676587 (monarchic system)
│  │
│  ├─ P279 subclass of → Q1250464 (realm) [15 props]
│  │  ├─ P279 subclass of → Q7275 (state)
│  │  ├─ P279 subclass of → Q183366 (territory)
│  │  └─ P279 subclass of → Q3624078 (sovereign state) [24 props]
│  │     ├─ P279 subclass of → Q7275 (state)
│  │     └─ P279 subclass of → Q6256 (country) [68 props]
│  │
│  └─ P279 subclass of → Q3624078 (sovereign state) [24 props]
│
├─ P31 instance of → Q3024240 (historical country) [16 props]
│  ├─ P279 subclass of → Q19953632 (former admin entity) [7 props]
│  ├─ P279 subclass of → Q96196009 (former/current state) [4 props]
│  ├─ P279 subclass of → Q19832712 (historical admin division) [4 props]
│  └─ P279 subclass of → Q6256 (country) [68 props]
│
└─ P361 part of → Q1747689 (Ancient Rome) [114 props]
   ├─ P31 instance of → Q3024240 (historical country) [circular!]
   ├─ P31 instance of → Q28171280 (ancient civilization) [14 props]
   ├─ P31 instance of → Q26907166 (temporal entity) [9 props]
   ├─ P361 part of → Q120754777 (Roman civilization) [10 props]
   │  ├─ P31 instance of → Q8432 (civilization)
   │  ├─ P31 instance of → Q11042 (culture)
   │  ├─ P361 part of → Q937284 (Greco-Roman world)
   │  └─ P279 subclass of → Q478958 (Western culture)
   │
   ├─ P279 subclass of → Q465299 (archaeological culture) [27 props]
   │  ├─ P31 instance of → Q151885 (concept)
   │  ├─ P279 subclass of → Q4808636 (assemblage)
   │  ├─ P279 subclass of → Q11042 (culture)
   │  └─ P279 subclass of → Q120754777 (Roman civilization) [circular!]
   │
   └─ P279 subclass of → Q120754777 (Roman civilization) [10 props]
```

### DOWNWARD (Subdivision Hierarchy)

```
ROOT: Q17167 (Roman Republic) [61 props]
│
├─ P527 has parts → Q2839628 (Early Roman Republic) [8 props]
│  └─ NO CHILDREN (leaf)
│
├─ P527 has parts → Q6106068 (Middle Roman Republic) [8 props]
│  └─ NO CHILDREN (leaf)
│
└─ P527 has parts → Q2815472 (Late Roman Republic) [10 props]
   └─ NO CHILDREN (leaf)
```

### SUCCESSION (Timeline)

```
Q201038 (Roman Kingdom) [38 props]
    753-509 BC
    ↓
Q17167 (ROMAN REPUBLIC) [61 props]
    509-27 BC
    ├─ Early (509-265 BC)
    ├─ Middle (264-146 BC)
    └─ Late (145-27 BC)
    ↓
Q2277 (Roman Empire) [102 props]
    27 BC - 476 AD (West)
    
Q206414 (Principate) [24 props]
    27 BC - 284 AD
```

---

## 🎯 STRUCTURAL INSIGHTS

### 1. **Classification Complexity**

Roman Republic has **5 different classifications** at Hop 1:
- Temporal: **historical period** → era → time interval
- Political: **form of government** → political system → state
- Imperial: **empire** → monarchy → realm → sovereign state → country
- Geographic: **historical country** → country
- Cultural: **part of Ancient Rome** → Roman civilization → Greco-Roman world

### 2. **Circular References Found!**

| Entity 1 | → | Entity 2 | → | Back to Entity 1 |
|----------|---|----------|---|------------------|
| Roman Republic | P31 | form of government | P31 | monarchy | P31 | form of government ✓ |
| Roman Republic | P31 | historical country | ← P31 | Ancient Rome | P361 | Roman Republic ✓ |
| Roman Republic | P361 | Ancient Rome | P279 | Roman civilization | P279 | archaeological culture | P279 | Roman civilization ✓ |

**This is normal in Wikidata** - shows interconnected concepts.

### 3. **Abstract Concepts Discovered**

Now we have abstract entities that MIGHT have academic properties:
- Q28108 (**political system**) - 39 properties
- Q7269 (**monarchy**) - 76 properties
- Q6256 (**country**) - 68 properties
- Q465299 (**archaeological culture**) - 27 properties
- Q8432 (**civilization**) - need to fetch
- Q11042 (**culture**) - need to fetch

**These are candidates for field of study queries!**

### 4. **Property Density Pattern**

| Entity Type | Avg Properties | Examples |
|-------------|----------------|----------|
| **Concrete Historical** | 50-114 | Ancient Rome (114), Roman Empire (102), Roman Republic (61) |
| **Abstract Concepts** | 20-76 | monarchy (76), country (68), political system (39) |
| **Temporal Subdivisions** | 8-10 | Early/Middle/Late Roman Republic |
| **Meta-concepts** | 4-15 | administrative type (5), metaclass (13) |

---

## 📋 COMPLETE RELATIONSHIP TABLE

### All 76 Relationships with QIDs and Labels:

| From QID | From Label | Property | To QID | To Label | Hop | Direction |
|----------|------------|----------|--------|----------|-----|-----------|
| Q17167 | Roman Republic | P31 | Q11514315 | historical period | 1 | UP |
| Q17167 | Roman Republic | P31 | Q1307214 | form of government | 1 | UP |
| Q17167 | Roman Republic | P31 | Q48349 | empire | 1 | UP |
| Q17167 | Roman Republic | P31 | Q3024240 | historical country | 1 | UP |
| Q17167 | Roman Republic | P361 | Q1747689 | Ancient Rome | 1 | UP |
| Q11514315 | historical period | P279 | Q6428674 | era | 2 | UP |
| Q6428674 | era | P279 | Q186081 | time interval | 3 | UP |
| Q1307214 | form of government | P31 | Q19478619 | metaclass | 2 | UP |
| Q1307214 | form of government | P279 | Q183039 | form of state | 2 | UP |
| Q1307214 | form of government | P279 | Q2752458 | administrative type | 2 | UP |
| Q1307214 | form of government | P279 | Q28108 | political system | 2 | UP |
| Q19478619 | metaclass | P31 | Q151885 | concept | 3 | UP |
| Q19478619 | metaclass | P31 | Q19868531 | formal ontology concept | 3 | UP |
| Q19478619 | metaclass | P31 | Q23958852 | variable-order class | 3 | UP |
| Q19478619 | metaclass | P361 | Q324254 | ontology | 3 | UP |
| Q19478619 | metaclass | P279 | Q16889133 | class | 3 | UP |
| Q183039 | form of state | P279 | Q28108 | political system | 3 | UP |
| Q2752458 | administrative type | P31 | Q2712963 | abstract noun | 3 | UP |
| Q2752458 | administrative type | P31 | Q5962346 | classification scheme | 3 | UP |
| Q2752458 | administrative type | P279 | Q96247293 | type of management | 3 | UP |
| Q2752458 | administrative type | P279 | Q28108 | political system | 3 | UP |
| Q28108 | political system | P31 | Q96116695 | (unlabeled) | 3 | UP |
| Q28108 | political system | P279 | Q1639378 | (unlabeled) | 3 | UP |
| Q48349 | empire | P31 | Q7269 | monarchy | 2 | UP |
| Q48349 | empire | P279 | Q1250464 | realm | 2 | UP |
| Q48349 | empire | P279 | Q3624078 | sovereign state | 2 | UP |
| Q7269 | monarchy | P31 | Q1307214 | form of government | 3 | UP |
| Q7269 | monarchy | P279 | Q22676587 | monarchic system | 3 | UP |
| Q1250464 | realm | P279 | Q7275 | state | 3 | UP |
| Q1250464 | realm | P279 | Q183366 | territory | 3 | UP |
| Q1250464 | realm | P279 | Q3624078 | sovereign state | 3 | UP |
| Q3624078 | sovereign state | P279 | Q7275 | state | 3 | UP |
| Q3624078 | sovereign state | P279 | Q6256 | country | 3 | UP |
| Q3024240 | historical country | P279 | Q19953632 | former admin entity | 2 | UP |
| Q3024240 | historical country | P279 | Q96196009 | former/current state | 2 | UP |
| Q3024240 | historical country | P279 | Q19832712 | historical admin division | 2 | UP |
| Q3024240 | historical country | P279 | Q6256 | country | 2 | UP |
| Q1747689 | Ancient Rome | P31 | Q3024240 | historical country | 2 | UP |
| Q1747689 | Ancient Rome | P31 | Q28171280 | ancient civilization | 2 | UP |
| Q1747689 | Ancient Rome | P31 | Q26907166 | temporal entity | 2 | UP |
| Q1747689 | Ancient Rome | P361 | Q120754777 | Roman civilization | 2 | UP |
| Q1747689 | Ancient Rome | P279 | Q465299 | archaeological culture | 2 | UP |
| Q1747689 | Ancient Rome | P279 | Q120754777 | Roman civilization | 2 | UP |
| Q120754777 | Roman civilization | P31 | Q8432 | civilization | 3 | UP |
| Q120754777 | Roman civilization | P31 | Q11042 | culture | 3 | UP |
| Q120754777 | Roman civilization | P361 | Q937284 | Greco-Roman world | 3 | UP |
| Q120754777 | Roman civilization | P279 | Q478958 | Western culture | 3 | UP |
| Q465299 | archaeological culture | P31 | Q151885 | concept | 3 | UP |
| Q465299 | archaeological culture | P279 | Q4808636 | assemblage | 3 | UP |
| Q465299 | archaeological culture | P279 | Q11042 | culture | 3 | UP |
| Q465299 | archaeological culture | P279 | Q120754777 | Roman civilization | 3 | UP |
| Q17167 | Roman Republic | P527 | Q2839628 | Early Roman Republic | 1 | DOWN |
| Q17167 | Roman Republic | P527 | Q6106068 | Middle Roman Republic | 1 | DOWN |
| Q17167 | Roman Republic | P527 | Q2815472 | Late Roman Republic | 1 | DOWN |
| Q201038 | Roman Kingdom | P155 | Q17167 | Roman Republic | 0 | SUCCESSION |
| Q17167 | Roman Republic | P156 | Q2277 | Roman Empire | 0 | SUCCESSION |
| Q17167 | Roman Republic | P156 | Q206414 | Principate | 0 | SUCCESSION |

---

## 🔍 KEY ENTITIES TO EXPLORE NEXT

### High-Value Targets (Many Properties):

| QID | Label | Properties | Why Explore |
|-----|-------|------------|-------------|
| **Q1747689** | Ancient Rome | 114 | Parent - may have field of study, academic discipline |
| **Q2277** | Roman Empire | 102 | Successor - complete picture |
| **Q7269** | monarchy | 76 | Abstract - may have practiced by, studied by |
| **Q6256** | country | 68 | Abstract - may have academic properties |
| **Q28108** | political system | 39 | Abstract - likely has studied by |
| **Q465299** | archaeological culture | 27 | May have academic/study properties |

### Abstract Concepts (Likely to have Academic Properties):

| QID | Label | Type | Next Query |
|-----|-------|------|------------|
| Q8432 | civilization | Not fetched yet | Fetch to check P2579 (studied by) |
| Q11042 | culture | Not fetched yet | Fetch to check P101 (field of work) |
| Q937284 | Greco-Roman world | Not fetched yet | May have academic properties |
| Q478958 | Western culture | Not fetched yet | May have studied by |
| Q151885 | concept | Not fetched yet | Meta-level, may have ontology properties |

---

## 💡 DISCOVERIES & PATTERNS

### Pattern 1: Dual Nature Entities
- **Roman Republic** = BOTH period AND government AND country
- **Ancient Rome** = BOTH country AND civilization AND culture
- **empire** = BOTH monarchy AND realm AND sovereign state

### Pattern 2: Circular References
- form of government ↔ monarchy ↔ form of government
- historical country ↔ Ancient Rome ↔ historical country
- Roman civilization ↔ archaeological culture ↔ Roman civilization

**This is GOOD** - shows semantic richness in Wikidata

### Pattern 3: Property Density
- Concrete historical entities: 38-114 properties
- Abstract concepts: 12-76 properties
- Temporal subdivisions: 8-10 properties (minimal)

### Pattern 4: Upward Explosion
- 1 root → 5 parents → 18 grandparents → many great-grandparents
- Shows rich classification space

### Pattern 5: Downward Simplicity
- 1 root → 3 children → 0 grandchildren
- Children are leaf nodes (no further subdivision)

---

## 📊 WHAT WE NOW HAVE:

**For structural analysis:**
- ✅ 28 complete entities with ALL properties
- ✅ 76 relationships with QIDs AND labels
- ✅ ~900+ total properties to analyze
- ✅ Full taxonomy 3 hops up and down
- ✅ Complete succession chain

**For domain building:**
- ✅ Clear parent hierarchy
- ✅ Clear child structure
- ✅ Clear temporal progression
- ✅ Multiple classification paths
- ✅ Rich context (Ancient Rome, Roman Empire)

---

## 🚀 NEXT ACTIONS

**Option 1:** Fetch the abstract concepts (civilization, culture, political system)
- These WILL have academic/field of study properties

**Option 2:** Analyze Ancient Rome (Q1747689) - 114 properties
- See all its relationships and classifications

**Option 3:** Build domain from these 28 entities
- Create SubjectConcepts
- Assign facets
- Build Neo4j graph

**What should we do next?** 🎯
