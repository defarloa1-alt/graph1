# Time Period Definition - Comprehensive Criteria

**Purpose:** Define what makes an entity a "time period" for SCA domain building

---

## 🎯 CRITERIA FOR TIME PERIOD

An entity is a **time period candidate** if it has ANY of:

### **Option 1: Explicit Classification**
- P31 (instance of) = Q11514315 (historical period)
- P31 (instance of) = Q6428674 (era)
- P31 (instance of) = Q186081 (time interval)

### **Option 2: Start/End Time Properties**
- P580 (start time) AND P582 (end time)

### **Option 3: Inception/Dissolved Properties**
- P571 (inception) AND P576 (dissolved, abolished or demolished date)

### **Option 4: Multiple Temporal Properties**
- Has at least 2 of: P571, P576, P580, P582, P585

---

## 📊 PROPERTY COMBINATIONS

| Combination | Properties | Example | Period? |
|-------------|------------|---------|---------|
| **1** | P31 = Q11514315 | Q17167 (Roman Republic) | ✅ YES |
| **2** | P580 + P582 | Any entity with start/end | ✅ YES |
| **3** | P571 + P576 | Any entity with inception/dissolved | ✅ YES |
| **4** | P31 = Q11514315 + P580 + P582 | Q17167 (explicit + bounds) | ✅ YES (highest confidence) |
| **5** | P31 = Q11514315 + P571 + P576 | Some republics/states | ✅ YES (high confidence) |
| **6** | Only P571 (no end) | Ongoing entities | ❌ NO (still active) |
| **7** | Only P585 (point in time) | Single events | ❌ NO (events, not periods) |

---

## 🔍 EXPANDED QUERY

### Query 1: Explicit Historical Periods (Current)
```sparql
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q11514315 .  # instance of: historical period
}
```
**Result:** 89+ entities (we got 100 in our sample)

### Query 2: Entities with Start/End Time
```sparql
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P580 ?start .
  ?item wdt:P582 ?end .
  FILTER NOT EXISTS { ?item wdt:P31 wd:Q11514315 }
}
LIMIT 100
```
**Expected:** Countries, organizations, conflicts with temporal bounds

### Query 3: Entities with Inception/Dissolved
```sparql
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P571 ?inception .
  ?item wdt:P576 ?dissolved .
  FILTER NOT EXISTS { ?item wdt:P31 wd:Q11514315 }
}
LIMIT 100
```
**Expected:** States, republics, empires, dynasties

### Query 4: Combined (All Temporal Entities)
```sparql
SELECT DISTINCT ?item ?itemLabel WHERE {
  {
    ?item wdt:P31 wd:Q11514315 .  # historical period
  } UNION {
    ?item wdt:P580 ?start .
    ?item wdt:P582 ?end .
  } UNION {
    ?item wdt:P571 ?inception .
    ?item wdt:P576 ?dissolved .
  }
}
LIMIT 500
```
**Expected:** 300-500+ temporal entities (periods, states, organizations, conflicts)

---

## 📋 EXAMPLES FROM OUR DATA

### Entities with P571/P576:

From our Roman Republic data:
```
Q17167 (Roman Republic)
  P571 (inception): -0509-00-00
  P576 (dissolved): -0027-01-16
  
Also has:
  P580 (start time): -0509-00-00
  P582 (end time): -0027-00-00
  P31: Q11514315 (historical period)
  
→ Triple confirmation! Definitely a period
```

### Likely Entities with ONLY P571/P576:

- Republics (P31 = republic, P571 = founded, P576 = dissolved)
- Monarchies (P31 = monarchy, P571 = established, P576 = abolished)
- Organizations (P31 = organization, P571 = founded, P576 = dissolved)
- States (P31 = state, P571 = independence, P576 = dissolution)

**These would be MISSED by Query 1 (only looking for P31=historical period)**

---

## 🎯 RECOMMENDED SCA CRITERIA

### High Confidence Periods:
✅ P31 = Q11514315 (historical period)  
✅ P580 + P582 (start/end time)  
✅ P571 + P576 (inception/dissolved)

### Medium Confidence Periods:
⚠️ P31 = Q6428674 (era)  
⚠️ P31 = Q186081 (time interval)  
⚠️ Has 3+ of: P571, P576, P580, P582

### Low Confidence (Evaluate):
⚠️ Only P571 or only P576 (incomplete temporal data)  
⚠️ Only P585 (point in time - likely event, not period)

---

## 🚀 NEXT STEP: EXPANDED QUERIES

Run all 4 queries to get:
- Query 1: ~100 explicit historical periods ✅ (done)
- Query 2: ~100 entities with P580/P582
- Query 3: ~100 entities with P571/P576
- Query 4: ~500 combined temporal entities

**Total potential:** 300-500 time period candidates

**Then filter by library authorities** (P244, P2163, P1149, P10832)

**Should we run the expanded queries?** 🎯
