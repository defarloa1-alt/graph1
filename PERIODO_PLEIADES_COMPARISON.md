# PeriodO & Pleiades ID Comparison

**Comparing:** Unfiltered list (89 periods) vs Filtered list (100 entities in 5-hop)

---

## 📊 RESULTS FROM 5-HOP DATA (100 ENTITIES)

### Geographic/Temporal Authority IDs:

**Searching for:**
- P1584 (Pleiades ID) - ancient place gazetteer
- P1667 (Getty TGN ID) - geographic names thesaurus
- P8216 (iDAI.gazetteer ID) - archaeological gazetteer
- PeriodO - (no direct Wikidata property)

**Found:**

| Entity | QID | Authority | ID |
|--------|-----|-----------|-----|
| Ancient Rome | Q1747689 | Getty TGN | P1667 |

```
Total with geographic gazetteer IDs: 1 (1%)
Total without: 99 (99%)
```

---

## 🎯 KEY FINDING

### **Why So Few?**

1. **Pleiades is for PLACES, not PERIODS**
   - Pleiades: Ancient place gazetteer (cities, sites)
   - Our data: Historical periods and abstract concepts
   - Mismatch in entity types

2. **PeriodO has NO Wikidata property**
   - PeriodO uses external URIs
   - Must be matched separately
   - Not embedded in Wikidata

3. **Our 5-hop data is mostly ABSTRACT**
   - 93 entities are concepts (government, culture, etc.)
   - Only 7 are concrete historical entities
   - Geographic IDs only on concrete entities

---

## 📋 COMPARISON

### Unfiltered List (89 Historical Periods):

**From backlinks query:**
- All are P31 = Q11514315 (historical period)
- All are CONCRETE periods (not abstract)
- Examples: Roman Republic, Ancient Greece, Cold War, etc.

**Expected geographic authority coverage:**
- Pleiades: ~5-10% (only ancient periods with known places)
- Getty TGN: ~10-20% (historical countries with geographic data)
- PeriodO: 0% (not in Wikidata)

### Filtered List (100 Entities in 5-hop):

**From recursive exploration:**
- 7 concrete historical entities (7%)
- 93 abstract concepts (93%)

**Actual geographic authority coverage:**
- Pleiades: 0%
- Getty TGN: 1% (Ancient Rome only)
- PeriodO: 0%

**Difference:**
- 5-hop includes mostly abstract ontology
- 89 periods list is all concrete historical periods
- Geographic IDs will be MUCH higher in the 89 periods

---

## 🔍 **WHAT THIS MEANS:**

### For the 89 Historical Periods:

**If we check ALL 89 for geographic authorities:**

Expected results:
- Ancient periods (20): ~30% might have Pleiades/TGN
- Medieval periods (7): ~20% might have TGN
- Modern periods (30+): ~40% might have TGN
- Asian dynasties (20+): ~20% might have TGN

**Estimated:** 15-25 of 89 periods (17-28%) will have geographic authority IDs

### For the 5-hop Abstract Concepts:

**Current:** 1 of 100 (1%) has geographic authority

**Why:** Abstract concepts (empire, monarchy, culture) don't have geographic IDs

---

## 📊 **COMPARISON TABLE**

| Dataset | Total | Concrete | Abstract | With Geo IDs | % Coverage |
|---------|-------|----------|----------|--------------|------------|
| **89 Periods** (unfiltered) | 89 | 89 | 0 | ~15-25 (est.) | 17-28% (est.) |
| **100 5-hop** (filtered) | 100 | 7 | 93 | 1 (confirmed) | 1% |
| **Difference** | +11 | -82 | +93 | -14-24 (est.) | -16-27% |

---

## 💡 **KEY INSIGHTS:**

### 1. **5-hop went UP into abstraction**
- Started with Q17167 (concrete)
- Explored parents: form of government, empire, etc. (abstract)
- Ended with 93% abstract concepts

### 2. **89 periods are ALL concrete**
- All are actual historical periods
- All have temporal bounds
- Many will have geographic context

### 3. **Geographic IDs are on PLACES, not PERIODS**
- Pleiades: For places like Rome, Athens
- Not for periods like "Roman Republic"
- Must link period → place → Pleiades ID

---

## 🎯 **RECOMMENDATION:**

**Don't expect periods to have Pleiades IDs directly**

Instead, check:
1. **Does period have P36 (capital)?** → Link to Place → Check Place for Pleiades
2. **Does period have P17 (country)?** → Link to Country → Check for Pleiades
3. **Does period have P276 (location)?** → Link to Location → Check for Pleiades

**Example:**
```
Q17167 (Roman Republic)
  → P36 (capital): Q220 (Rome)
    → Rome might have: P1584 (Pleiades ID)
    
Not:
  Q17167 → P1584 (direct Pleiades)
```

---

## ✅ **CURRENT STATE:**

**Unfiltered (89 periods):** Need to check geographic authority IDs  
**Filtered (100 5-hop):** Only 1 has geographic ID (Ancient Rome)  
**Difference:** 5-hop is abstraction layer, not geographic layer

**File:** `PERIODO_PLEIADES_COMPARISON.md` 📍
