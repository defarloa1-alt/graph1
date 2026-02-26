# Geographic & PeriodO Analysis - 100 Entities

**Source:** Q17167_recursive_20260220_135756.json (5-hop taxonomy)

---

## 📊 GEOGRAPHIC PROPERTIES

```
Total entities: 100
✅ WITH geography: 7 (7.0%)
❌ WITHOUT geography: 93 (93.0%)
```

---

## ✅ 7 ENTITIES WITH GEOGRAPHIC PROPERTIES

| QID | Label | Geo Props | Properties Found |
|-----|-------|-----------|------------------|
| Q1747689 | **Ancient Rome** | 5 | P30 (continents), P36 (capital), P625 (coords), P706 (Mediterranean), P47 (borders) |
| Q201038 | **Roman Kingdom** | 4 | P30 (continents), P36 (capital), P625 (coords), P276 (Latium) |
| Q17167 | **Roman Republic** | 3 | P30 (continents), P36 (capital), P625 (coords) |
| Q2267705 | field of study | 1 | P276 (universities) |
| Q2839628 | Early Roman Republic | 1 | P17 (country: Roman Republic) |
| Q6106068 | Middle Roman Republic | 1 | P17 (country: Roman Republic) |
| Q2815472 | Late Roman Republic | 1 | P17 (country: Roman Republic) |

---

## ❌ 93 ENTITIES WITHOUT GEOGRAPHIC PROPERTIES

**Reason:** Most are abstract concepts (government, monarchy, empire, culture, etc.)

**Note:** These are ONTOLOGICAL nodes, not geographic entities!

---

## 📅 P2348 (TIME PERIOD) PROPERTY

```
Total entities: 100
✅ WITH P2348: 3 (3.0%)
❌ WITHOUT P2348: 97 (97.0%)
```

### ✅ 3 ENTITIES WITH P2348 (time period):

| QID | Label | P2348 Value |
|-----|-------|-------------|
| Q17167 | **Roman Republic** | Q486761 (classical antiquity) |
| Q1747689 | **Ancient Rome** | Q486761 (classical antiquity) |
| Q28171280 | ancient civilization | Q41493 (ancient history) |

**Pattern:** Concrete periods link to broader temporal context

---

## 🌐 PERIODO ID ANALYSIS

**Searching for PeriodO references...**

### PeriodO in Wikidata:

❌ **No direct PeriodO property in Wikidata**

PeriodO (http://perio.do) is an external gazetteer that:
- Uses URIs (not Wikidata properties)
- Must be matched separately
- Not embedded in Wikidata claims

### Our System (Chrystallum):

In our Neo4j schema, we have:
```cypher
(:Period {
  periodo_id: "p0xxxxx",  // PeriodO URI
  qid: "Q17167",          // Wikidata QID
  label: "Roman Republic"
})
```

**PeriodO matching is EXTERNAL to Wikidata!**

---

## 🎯 KEY FINDINGS:

### 1. **Dual Classification:**

```
Q17167 (Roman Republic)
  P31 (instance of):
    - Q11514315 (historical period) ✅
    - Q3024240 (historical country) ✅
    
  → It's BOTH a period AND a country!
```

### 2. **Geographic Coverage:**

**Only 7 concrete entities (7%) have geography:**
- 3 Roman periods (Kingdom, Republic, Ancient Rome)
- 3 Roman Republic subdivisions (Early, Middle, Late)
- 1 academic concept (field of study = universities)

**93 abstract concepts (93%) have NO geography**

### 3. **Temporal Context:**

**Only 3 entities (3%) explicitly link to broader time periods:**
- Roman Republic → classical antiquity
- Ancient Rome → classical antiquity
- ancient civilization → ancient history

---

## 📊 SUMMARY TABLE

| Property | Entities With | Entities Without | % Coverage |
|----------|---------------|------------------|------------|
| **Geographic** (P30/P36/P625/P276/etc.) | 7 | 93 | 7.0% |
| **Time Period** (P2348) | 3 | 97 | 3.0% |
| **PeriodO ID** | 0 | 100 | 0.0% (not in Wikidata) |

---

## 💡 IMPLICATIONS:

1. **Geographic Facet:** Only applicable to 7 concrete historical entities
2. **Time Period Context:** Only 3 entities explicitly state broader period
3. **PeriodO:** Must be matched externally (not in Wikidata)
4. **Abstract vs Concrete:** Clear divide between ontology (93) and history (7)

**For SCA:** Keep all buckets, but recognize only 7 are concrete historical subjects with geography! 🌍
