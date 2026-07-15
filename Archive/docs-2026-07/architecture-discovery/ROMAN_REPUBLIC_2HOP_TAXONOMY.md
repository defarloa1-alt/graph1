# Roman Republic - 2-Hop Recursive Taxonomy

**Root:** Q17167 (Roman Republic)  
**Explored:** 2 hops up, 2 hops down, and succession  
**Generated:** 2026-02-20

---

## 📊 SUMMARY STATISTICS

| Metric | Count |
|--------|-------|
| **Total Entities Fetched** | 12 |
| **Total Relationships** | 29 |
| **Upward Relationships** | 23 (parents & grandparents) |
| **Downward Relationships** | 3 (children & grandchildren) |
| **Succession Relationships** | 3 (timeline) |

### Entities by Distance:

| Level | Count | Entities |
|-------|-------|----------|
| **Root** | 1 | Roman Republic |
| **1 Hop Up (Parents)** | 5 | historical period, form of government, empire, historical country, Ancient Rome |
| **2 Hops Up (Grandparents)** | 18 | era, metaclass, form of state, monarchy, realm, etc. |
| **1 Hop Down (Children)** | 3 | Early, Middle, Late Roman Republic |
| **2 Hops Down (Grandchildren)** | 0 | None |
| **Succession** | 3 | Roman Kingdom (before), Roman Empire + Principate (after) |

---

## 📦 ALL 12 ENTITIES WITH FULL DATA

### 1. **Q17167 - Roman Republic** (ROOT)
- **Description:** period of ancient Roman civilization (509 BC–27 BC)
- **Properties:** 61
- **Role:** Starting entity

### 2. **Q11514315 - historical period** (Parent)
- **Description:** segment of time in history
- **Properties:** 20
- **Relationship:** P31 (instance of) from Roman Republic

### 3. **Q1307214 - form of government** (Parent)
- **Description:** Wikidata metaclass for government in terms of organizational
- **Properties:** 30
- **Relationship:** P31 (instance of) from Roman Republic

### 4. **Q48349 - empire** (Parent)
- **Description:** geographically extensive group of states and peoples united
- **Properties:** 55
- **Relationship:** P31 (instance of) from Roman Republic

### 5. **Q3024240 - historical country** (Parent)
- **Description:** country, state or territory that once existed
- **Properties:** 16
- **Relationship:** P31 (instance of) from Roman Republic

### 6. **Q1747689 - Ancient Rome** (Parent)
- **Description:** country that began growing on the Italian Peninsula
- **Properties:** 114 (MOST COMPLEX!)
- **Relationship:** P361 (part of) from Roman Republic

### 7. **Q2839628 - Early Roman Republic** (Child)
- **Description:** period in the Roman Republic (509-265 BC)
- **Properties:** 8
- **Relationship:** P527 (has parts) from Roman Republic

### 8. **Q6106068 - Middle Roman Republic** (Child)
- **Description:** period in the Roman Republic (264 BC-146 BC)
- **Properties:** 8
- **Relationship:** P527 (has parts) from Roman Republic

### 9. **Q2815472 - Late Roman Republic** (Child)
- **Description:** historical period, around 145 to 27 BC
- **Properties:** 10
- **Relationship:** P527 (has parts) from Roman Republic

### 10. **Q201038 - Roman Kingdom** (Predecessor)
- **Description:** period of Roman history when the city and its territory were ruled by kings
- **Properties:** 38
- **Relationship:** P155 (follows) from Roman Republic

### 11. **Q2277 - Roman Empire** (Successor)
- **Description:** period of ancient Rome following the Republic
- **Properties:** 102 (SECOND MOST COMPLEX!)
- **Relationship:** P156 (followed by) from Roman Republic

### 12. **Q206414 - Principate** (Successor)
- **Description:** first period of the Roman Empire (ca. 27 BC to 284 AD)
- **Properties:** 24
- **Relationship:** P156 (followed by) from Roman Republic

---

## 🔼 UPWARD TAXONOMY (Parents → Grandparents)

### Hop 1 Up: 5 Direct Parents

| QID | Label | Property | Rank |
|-----|-------|----------|------|
| Q11514315 | **historical period** | P31 (instance of) | preferred |
| Q1307214 | **form of government** | P31 (instance of) | normal |
| Q48349 | **empire** | P31 (instance of) | normal |
| Q3024240 | **historical country** | P31 (instance of) | preferred |
| Q1747689 | **Ancient Rome** | P361 (part of) | normal |

### Hop 2 Up: 18 Grandparents (from parents above)

**From Q11514315 (historical period):**
- Q6428674 → **era** (P279 subclass of)

**From Q1307214 (form of government):**
- Q19478619 → **metaclass** (P31 instance of)
- Q183039 → **form of state** (P279 subclass of)
- Q2752458 → **administrative type** (P279 subclass of)
- Q28108 → **political system** (P279 subclass of)

**From Q48349 (empire):**
- Q7269 → **monarchy** (P31 instance of)
- Q1250464 → **realm** (P279 subclass of)
- Q3624078 → **sovereign state** (P279 subclass of)

**From Q3024240 (historical country):**
- Q19953632 → **former administrative territorial entity** (P279 subclass of)
- Q96196009 → **former or current state** (P279 subclass of)
- Q19832712 → **historical administrative division** (P279 subclass of)
- Q6256 → **country** (P279 subclass of)

**From Q1747689 (Ancient Rome):**
- Q3024240 → **historical country** (P31 instance of) [circular!]
- Q28171280 → **Q28171280** (P31 instance of)
- Q26907166 → **Q26907166** (P31 instance of)
- Q120754777 → **Roman civilization** (P361 part of)
- Q465299 → **archaeological culture** (P279 subclass of)
- Q120754777 → **Roman civilization** (P279 subclass of)

---

## 🔽 DOWNWARD TAXONOMY (Children → Grandchildren)

### Hop 1 Down: 3 Direct Children

| QID | Label | Property | Date Range |
|-----|-------|----------|------------|
| Q2839628 | **Early Roman Republic** | P527 (has parts) | 509-265 BC |
| Q6106068 | **Middle Roman Republic** | P527 (has parts) | 264-146 BC |
| Q2815472 | **Late Roman Republic** | P527 (has parts) | 145-27 BC |

### Hop 2 Down: 0 Grandchildren

**All 3 children have NO further subdivisions (leaf nodes)**

---

## ⏱️ SUCCESSION (Timeline)

### Complete Timeline:

```
Q201038 (Roman Kingdom)
    753 BC - 509 BC
    ↓ [P155 follows / P1365 replaces]
    
Q17167 (ROMAN REPUBLIC) ← ROOT
    509 BC - 27 BC
    ├─ Q2839628 (Early) 509-265 BC
    ├─ Q6106068 (Middle) 264-146 BC
    └─ Q2815472 (Late) 145-27 BC
    
    ↓ [P156 followed by / P1366 replaced by]
    
Q2277 (Roman Empire)
    27 BC - 476 AD (West) / 1453 AD (East)
    
Q206414 (Principate)
    27 BC - 284 AD
```

---

## 📊 PROPERTIES PER ENTITY

| Rank | QID | Label | Properties |
|------|-----|-------|------------|
| 1 | Q1747689 | Ancient Rome | **114** |
| 2 | Q2277 | Roman Empire | **102** |
| 3 | Q17167 | **Roman Republic** | **61** |
| 4 | Q48349 | empire | 55 |
| 5 | Q201038 | Roman Kingdom | 38 |
| 6 | Q1307214 | form of government | 30 |
| 7 | Q206414 | Principate | 24 |
| 8 | Q11514315 | historical period | 20 |
| 9 | Q3024240 | historical country | 16 |
| 10 | Q2815472 | Late Roman Republic | 10 |
| 11 | Q2839628 | Early Roman Republic | 8 |
| 12 | Q6106068 | Middle Roman Republic | 8 |

**Total Properties Across All Entities:** ~554

---

## 🎯 KEY INSIGHTS FOR DOMAIN BUILDING

### 1. **Rich Hierarchical Structure**
- 5 different parent classifications
- Each parent has its own parent hierarchy (up to 18 grandparents)
- Clear temporal subdivisions (3 periods)

### 2. **Temporal Completeness**
- Full timeline coverage: Kingdom → Republic → Empire
- Subdivisions provide granular periodization
- Each period has defined date ranges

### 3. **Classification Diversity**
- Roman Republic classified as BOTH:
  - Historical period (temporal)
  - Historical country (political)
  - Form of government (systemic)
  - Empire (despite name "Republic"!)

### 4. **Complexity Indicators**
- **Ancient Rome** (114 props) = Most complex parent
- **Roman Empire** (102 props) = Most complex successor
- **Children** (8-10 props) = Simpler leaf entities

### 5. **Network Opportunities**
Each entity can be further explored:
- Ancient Rome → 114 properties to analyze
- Roman Empire → 102 properties to analyze
- Each grandparent → own children/context

---

## 💾 DATA AVAILABLE

**For EACH of the 12 entities, we have:**
✅ QID + Label + Description  
✅ ALL properties with property labels  
✅ ALL values with value labels  
✅ ALL qualifiers with labels  
✅ ALL references with labels

**Example:** For Q2839628 (Early Roman Republic), we have:
- 8 complete properties
- All values resolved to labels
- Ready for facet classification
- Ready for SubjectConcept creation

---

## 🚀 NEXT STEPS

### Option 1: Analyze Each Entity
- Extract facets for all 12 entities
- Create SubjectConcept proposals for each
- Build complete domain taxonomy

### Option 2: Go Deeper
- Fetch grandchildren (if any)
- Fetch great-grandparents
- Explore Roman Empire (102 properties!)
- Explore Ancient Rome (114 properties!)

### Option 3: Build Graph
- Create Neo4j nodes for all 12 entities
- Create relationships (23 upward, 3 downward, 3 succession)
- Visualize complete network

### Option 4: Extract Facets
- Analyze properties of each entity
- Classify by 18 canonical facets
- Generate facet assignments

---

**File Saved:** `output/taxonomy_recursive/Q17167_recursive_20260220_134235.json`

**Contains:** Complete data for all 12 entities with all relationships and properties!
