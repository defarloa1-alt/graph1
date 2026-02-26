# SCA Filters - Complete Review

**Purpose:** Define what entities SCA keeps vs removes when building the subgraph

---

## 🎯 FILTER 1: TIME PERIOD CRITERIA

**What qualifies as a time period?**

### ✅ INCLUDE if entity has:

| Criterion | Properties | Example |
|-----------|------------|---------|
| **A. Explicit Period** | P31 = Q11514315 (historical period) | Q17167 (Roman Republic) |
| **B. Explicit Era** | P31 = Q6428674 (era) | Q182688 (Victorian era) |
| **C. Start/End Time** | P580 (start) + P582 (end) | Q17167 has both |
| **D. Inception/Dissolved** | P571 (inception) + P576 (dissolved) | Q17167 has both |
| **E. Time Interval** | P31 = Q186081 (time interval) | Q41493 (ancient history) |

### ❌ EXCLUDE:

| Type | Why Exclude | Example |
|------|-------------|---------|
| **Events** | Only P585 (point in time), no duration | Battle of Waterloo |
| **Ongoing** | Only P571, no P576 (still exists) | United States (founded 1776, still exists) |
| **People** | P31 = Q5 (human) | Julius Caesar (not a period) |
| **Places** | P31 = Q515 (city) without temporal bounds | Modern Rome |

---

## 🎯 FILTER 2: LIBRARY AUTHORITY IDs (CRITICAL)

**SCA ONLY keeps entities with library subject authority**

### ✅ MUST HAVE at least ONE of:

| Property | Label | Authority | Example |
|----------|-------|-----------|---------|
| **P244** | Library of Congress authority ID | **LCSH** | sh85115114 (Roman Republic) |
| **P2163** | FAST ID | **FAST** | fst01204885 (Roman Republic) |
| **P1149** | Library of Congress Classification | **LCC** | DG241-269 (Roman Republic) |
| **P10832** | WorldCat Entities ID | **WorldCat** | (library catalog) |

### ❌ REMOVE if entity has:

- **NONE** of the above library authority IDs
- Only non-library IDs (Freebase, Quora, IMDb, etc.)

**Rationale:** If it's not in library subject systems, it's not a scholarly subject concept

---

## 🎯 FILTER 3: PROPERTY DENSITY (Optional)

**Filter by information richness**

### Thresholds:

| Density Level | Property Count | Action |
|---------------|----------------|--------|
| **High** | ≥50 properties | Always include, priority analysis |
| **Medium** | 10-49 properties | Include if has authorities |
| **Low** | <10 properties | Include only if explicit period + authorities |

### Examples:

| Entity | Properties | Density | Keep? |
|--------|------------|---------|-------|
| Q1747689 (Ancient Rome) | 114 | High | ✅ YES (if has authorities) |
| Q17167 (Roman Republic) | 61 | High | ✅ YES (has P244) |
| Q2839628 (Early Roman Republic) | 8 | Low | ⚠️ Only if has authorities |

---

## 🎯 FILTER 4: FACET RELEVANCE

**Entity must map to at least 1 of 18 canonical facets**

### How to determine facet mapping:

| Facet | Evidence Properties | Example |
|-------|---------------------|---------|
| **POLITICAL** | P31 (government), P194 (legislature), P122 (gov form) | Q17167 has all 3 |
| **RELIGIOUS** | P140 (religion), P3075 (official religion) | Q17167 has both |
| **MILITARY** | P793 (wars), P607 (conflicts) | Q17167 has 7 wars |
| **ECONOMIC** | P38 (currency), P2046 (area growth) | Q17167 has both |
| **LINGUISTIC** | P37 (language), P2936 (languages used) | Q17167 has both |
| **GEOGRAPHIC** | P30 (continent), P36 (capital), P625 (coordinates) | Q17167 has all 3 |

### ❌ REMOVE if:

- Cannot map to any of the 18 facets
- No relevant properties for domain analysis

---

## 🎯 FILTER 5: INHERITANCE FILTER

**Do NOT automatically inherit - check each entity**

### ❌ DON'T ASSUME:

- If A is part of B, A inherits B's properties
- If A is subclass of B, A has same authorities as B

### ✅ DO CHECK:

- Does A have its OWN library authority IDs? (P244, P2163, etc.)
- Does A have its OWN facet-relevant properties?
- Is A independently a subject in library systems?

### Example:

```
Q17167 (Roman Republic)
  [P361] Q1747689 (Ancient Rome)
  
Check Q17167:
  ✅ P244: sh85115114 (own LCSH ID)
  ✅ P31: historical period (own classification)
  ✅ P194: legislative bodies (own properties)
  → KEEP (independently qualified)

If Q17167 had NO P244 and NO own properties:
  ❌ REMOVE (only related to Ancient Rome, not a subject itself)
```

---

## 🎯 FILTER 6: RELATIONSHIP ORTHOGONALITY

**Entities are ORTHOGONAL (separate) until proven hierarchical**

### Relationships to preserve:

| Relationship | Property | Meaning | Example |
|--------------|----------|---------|---------|
| **Parent-Child** | P361 (part of) | Child is subdivision of parent | High/Middle/Late Medieval part of Middle Ages |
| **Classification** | P31 (instance of) | Entity is type of class | Roman Republic instance of historical period |
| **Taxonomy** | P279 (subclass of) | Concept is subset of broader | Middle Ages subclass of ancient history |
| **Succession** | P155/P156 (follows) | Temporal sequence | Kingdom → Republic → Empire |

### ❌ Don't conflate:

- P361 (part of) ≠ inheritance of properties
- P279 (subclass of) ≠ automatic inclusion
- Entities are separate nodes until relationships proven

---

## 🎯 FILTER 7: ACADEMIC RELEVANCE

**Prefer entities with academic/scholarly properties**

### High Value Properties:

| Property | Label | Why Important |
|----------|-------|---------------|
| **P2579** | studied by | Shows academic disciplines study this |
| **P1343** | described by source | Has scholarly sources |
| **P921** | main subject | Is main subject of scholarly works |
| **P101** | field of work | Academic field association |

### Boost Score if entity has:

- P2579 (studied by) = +20 confidence
- P1343 (described by source) = +10 confidence
- Multiple library IDs (P244 + P2163) = +15 confidence

---

## 🎯 FILTER 8: EXCLUSIONS (Always Remove)

### ❌ EXCLUDE these entity types:

| Type | P31 Value | Why Exclude | Example |
|------|-----------|-------------|---------|
| **Living People** | Q5 (human) + no P570 (death) | Not historical subjects | Modern politicians |
| **Modern Entities** | P571 > 2000, no P576 | Too recent | Current countries |
| **Pop Culture** | Only P2850 (Spotify), P8033 (Letterboxd) | Not scholarly | TV shows, games |
| **Single Events** | Only P585 (point in time) | Events, not periods | Single battles |
| **Fictional** | P1080 (from narrative universe) | Not real | Middle-earth |

---

## 📊 COMPLETE FILTER PIPELINE

### SCA Processing Flow:

```
1. Query Wikidata
   ├─ P31 = historical period (Query 1)
   ├─ P580 + P582 (Query 2)
   └─ P571 + P576 (Query 3)
   
2. Initial Filter
   ├─ Remove: ongoing entities (no end date)
   ├─ Remove: single events (only P585)
   └─ Keep: all with temporal bounds
   
3. Library Authority Filter (CRITICAL)
   ├─ Check: P244 (LCSH)
   ├─ Check: P2163 (FAST)
   ├─ Check: P1149 (LCC)
   └─ Check: P10832 (WorldCat)
   → Remove if NONE found
   
4. Density Filter
   ├─ High (≥50 props): Always keep if has authorities
   ├─ Medium (10-49 props): Keep if has authorities
   └─ Low (<10 props): Keep only if explicit period + authorities
   
5. Facet Mapping
   ├─ Map properties to 18 facets
   ├─ Must map to ≥1 facet
   └─ Remove if no facet mapping
   
6. Academic Boost
   ├─ Check: P2579 (studied by)
   ├─ Check: P1343 (sources)
   └─ Boost confidence if present
   
7. Final Validation
   ├─ Has library IDs? ✅
   ├─ Has temporal bounds? ✅
   ├─ Maps to facets? ✅
   └─ Accept as SubjectConcept
```

---

## ✅ **SUMMARY OF FILTERS:**

| Filter # | Name | Criteria | Purpose |
|----------|------|----------|---------|
| 1 | **Time Period** | P31, P580+P582, P571+P576 | Define what is a period |
| 2 | **Library Authority** | P244, P2163, P1149, P10832 | **CRITICAL - scholarly subjects only** |
| 3 | **Property Density** | Property count thresholds | Prioritize data-rich entities |
| 4 | **Facet Relevance** | Properties map to 18 facets | Must be analyzable |
| 5 | **No Inheritance** | Check each entity independently | No automatic inclusion |
| 6 | **Orthogonality** | Separate until proven related | Keep relationships explicit |
| 7 | **Academic Boost** | P2579, P1343 | Prefer scholarly subjects |
| 8 | **Exclusions** | Living, modern, fictional, pop culture | Remove non-historical |

**Most Critical:** **Filter 2 (Library Authority)** - without this, entity is removed! 📚