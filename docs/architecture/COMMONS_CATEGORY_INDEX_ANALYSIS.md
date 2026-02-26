# Commons Category Index - Discovery Mechanism

**Property:** P373 (Commons category)  
**Found in:** 43 of 100 entities (43%)

---

## 📊 ENTITIES WITH COMMONS CATEGORIES

### **Historical Entities (3):**

| QID | Label | Commons Category |
|-----|-------|------------------|
| Q17167 | Roman Republic | Roman Republic |
| Q1747689 | Ancient Rome | Ancient Rome |
| Q201038 | Roman Kingdom | Roman Kingdom |

### **Abstract Concepts (40):**

| QID | Label | Commons Category |
|-----|-------|------------------|
| Q48349 | empire | Empires |
| Q7269 | monarchy | Monarchies |
| Q6256 | country | Countries |
| Q8432 | civilization | Civilizations |
| Q11042 | culture | Culture |
| Q8425 | society | Society |
| ... | (34 more) | (various) |

---

## 🔍 **WHAT COMMONS CATEGORY INDEX REVEALS:**

### **Wikimedia Commons Category Structure:**

Each category like "Roman Republic" has:

1. **Parent categories** (broader topics)
2. **Subcategories** (narrower topics)
3. **Sister categories** (related at same level)
4. **Files/Media** (images, maps, documents)

### **Example: Category:Roman Republic**

**Hypothetical structure:**

```
Category:Ancient Rome (PARENT)
  ├─ Category:Roman Kingdom (SIBLING)
  ├─ Category:Roman Republic (THIS ONE)
  │  ├─ Category:Roman Republic government (SUBCATEGORY)
  │  ├─ Category:Roman Republic military (SUBCATEGORY)
  │  ├─ Category:People of the Roman Republic (SUBCATEGORY)
  │  ├─ Category:Buildings of the Roman Republic (SUBCATEGORY)
  │  ├─ Category:Wars of the Roman Republic (SUBCATEGORY)
  │  ├─ Category:Maps of the Roman Republic (SUBCATEGORY)
  │  └─ (100+ more subcategories)
  └─ Category:Roman Empire (SIBLING)
```

---

## 🎯 **HOW SCA SHOULD USE COMMONS INDEX:**

### **Step 1: Get Category Hierarchy**

**Query Commons API:**
```
https://commons.wikimedia.org/w/api.php?
  action=query
  &titles=Category:Roman Republic
  &prop=categories|categoryinfo
  &format=json
```

**Returns:**
- Parent categories
- Number of subcategories
- Number of files

---

### **Step 2: Get Subcategories**

**Query:**
```
https://commons.wikimedia.org/w/api.php?
  action=query
  &list=categorymembers
  &cmtitle=Category:Roman Republic
  &cmtype=subcat
  &cmlimit=500
  &format=json
```

**Returns:** All subcategories (paginated)

**Expected for "Roman Republic":**
- 50-200 subcategories
- Examples:
  - Roman Republic government
  - Roman Republic military
  - Roman Republic maps
  - Roman Republic coinage
  - People of Roman Republic
  - Buildings in Roman Republic
  - etc.

---

### **Step 3: Triage Subcategories**

**Each subcategory name reveals:**

| Subcategory | Maps to Facet | Entity Type |
|-------------|---------------|-------------|
| "Roman Republic military" | MILITARY | Topic area |
| "Roman Republic government" | POLITICAL | Topic area |
| "Roman Republic economy" | ECONOMIC | Topic area |
| "Roman Republic art" | ARTISTIC | Topic area |
| "Roman Republic coinage" | ECONOMIC | Objects |
| "Maps of Roman Republic" | GEOGRAPHIC | Media |
| "People of Roman Republic" | BIOGRAPHIC | People |
| "Buildings in Roman Republic" | ARCHITECTURAL | Places |

---

### **Step 4: Link Subcategories to Wikidata**

**For each subcategory, query:**
```sparql
SELECT ?item WHERE {
  ?item wdt:P373 "Roman Republic military" .
}
```

**Finds:** Wikidata entity that has this Commons category  
**Then:** Fetch that entity and add to domain

---

## 📊 **EXPECTED DISCOVERY FROM COMMONS:**

### **From "Category:Roman Republic" subcategories:**

**Estimated finds:**
- 50-100 subcategories
- Each maps to 1-5 Wikidata entities
- **Total:** 100-300 new candidate entities

**Entity types:**
- Military units, battles, tactics → MILITARY facet
- Government offices, laws → POLITICAL facet
- Currency, trade routes → ECONOMIC facet
- Temples, festivals → RELIGIOUS facet
- Languages, inscriptions → LINGUISTIC facet
- Provinces, cities → GEOGRAPHIC facet
- Social classes, families → SOCIAL facet
- Art, architecture → ARTISTIC facet

---

## 🎯 **SCA PROCESS FOR COMMONS CATEGORIES:**

```
1. Entity has P373 (Commons category)
   ↓
2. Query Commons API for category structure
   - Get parent categories
   - Get subcategories (paginated, ALL pages)
   - Get file count
   ↓
3. For each subcategory:
   - Parse name for facet keywords
   - Query Wikidata for P373 = subcategory name
   - Fetch matched entities
   ↓
4. Triage entities by type:
   - People → check VIAF/LCNAF
   - Places → check Pleiades/TGN
   - Events → check LCSH
   - Concepts → check LCSH/FAST
   ↓
5. Add to appropriate buckets
   - Bucket by facet
   - Bucket by entity type
   - Bucket by authority presence
```

---

## 📋 **WHAT WE HAVE:**

**Commons categories in our 100 entities:** 43

**Concrete historical (3):**
- Roman Republic
- Ancient Rome
- Roman Kingdom

**Abstract concepts (40):**
- empire, monarchy, culture, civilization, etc.

---

## 🔍 **NEXT ACTIONS:**

### **For Roman Republic specifically:**

1. Query Commons API for "Category:Roman Republic"
2. Get all subcategories (could be 50-200)
3. Map subcategories to 18 facets
4. Query Wikidata for entities in each subcategory
5. Check entities for library IDs
6. Add to domain

**Expected result:** 100-300 additional entities from Commons alone!

---

## ✅ **KEY INSIGHT:**

**Commons category is a RICH discovery mechanism:**

- Organized by librarians/curators
- Hierarchical structure mirrors subject organization
- Subcategories map directly to facets
- Each subcategory → Wikidata entities → potential SubjectConcepts

**SCA should ALWAYS check P373 and explore Commons index!**

**43 of our 100 entities have Commons categories - all are entry points for discovery!** 📚
