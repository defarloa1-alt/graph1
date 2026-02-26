# 12 Failed Periods - Complete Temporal Data

**Status:** All 12 have START + END dates ✅  
**Reason they failed:** Wikidata rate limits during enrichment (429 errors)  
**Data:** Successfully retrieved on retry with delays

---

## 📊 SUMMARY

```
Total: 12 periods
✅ With start+end dates: 12 (100%)
❌ Without complete dates: 0 (0%)
```

**ALL 12 ARE VALID TIME PERIODS** - they were just missed due to rate limits!

---

## 📅 COMPLETE TEMPORAL DATA (All 12 Periods)

### 1. **Q185063 - Warring States period**
- **P580 (start time):** -0476-00-00 (476 BC)
- **P582 (end time):** -0221-00-00 (221 BC)
- **Duration:** 255 years
- **Region:** China

---

### 2. **Q27837 - Twenty Years' Anarchy**
- **P580 (start time):** +0695-00-00 (695 AD)
- **P582 (end time):** +0717-00-00 (717 AD)
- **Duration:** 22 years
- **Region:** Byzantine

---

### 3. **Q185852 - Edwardian era**
- **P580 (start time):** +1901-00-00 (1901 AD)
- **P582 (end time):** +1910-00-00 (1910 AD)
- **Duration:** 9 years
- **Region:** British

---

### 4. **Q16410 - Hungarian People's Republic**
- **P571 (inception):** +1949-08-20 (August 20, 1949)
- **P576 (dissolved):** +1989-10-23 (October 23, 1989)
- **Duration:** 40 years
- **Region:** Hungary

---

### 5. **Q187979 - Early Dynastic Period of Egypt**
- **P580 (start time):** -3032-00-00 (3032 BC)
- **P582 (end time):** -2707-00-00 (2707 BC)
- **Duration:** 325 years
- **Region:** Egypt

---

### 6. **Q49696 - Northern and Southern dynasties**
- **P580 (start time):** +0420-00-00 (420 AD)
- **P582 (end time):** +0589-00-00 (589 AD)
- **P2348 (time period):** Q1197281 (Six Dynasties)
- **Duration:** 169 years
- **Region:** China

---

### 7. **Q189297 - Zemene Mesafint**
- **P580 (start time):** +1769-05-07 (May 7, 1769)
- **P582 (end time):** +1855-02-11 (February 11, 1855)
- **Duration:** 86 years
- **Region:** Ethiopia

---

### 8. **Q75207 - Pax Romana**
- **P580 (start time):** -0027-00-00 (27 BC)
- **P582 (end time):** +0180-00-00 (180 AD)
- **Duration:** 207 years
- **Region:** Roman Empire

---

### 9. **Q190882 - Phoney War**
- **P580 (start time):** +1939-10-01 (October 1, 1939)
- **P582 (end time):** +1958-04-00 (April 1958)
- **Duration:** ~19 years
- **Region:** Europe (WWII)

---

### 10. **Q148499 - Margraviate of Brandenburg**
- **P571 (inception):** +1157-06-11 (June 11, 1157)
- **P576 (dissolved):** +1806-01-01 (January 1, 1806)
- **Duration:** 649 years
- **Region:** Germany

---

### 11. **Q191324 - Middle Kingdom of Egypt**
- **P571 (inception):** -2040-00-00 (2040 BC)
- **P576 (dissolved):** -1782-00-00 (1782 BC)
- **Duration:** 258 years
- **Region:** Egypt

---

### 12. **Q8951 - Third Republic of Venezuela**
- **P580 (start time):** +1817-00-00 (1817 AD)
- **P582 (end time):** +1821-00-00 (1821 AD)
- **Duration:** 4 years
- **Region:** Venezuela

---

## 📊 TEMPORAL PROPERTY PATTERNS

### Property Usage:

| Property | Count | Periods Using |
|----------|-------|---------------|
| **P580 (start time)** | 9 | Warring States, Twenty Years, Edwardian, Early Dynastic Egypt, Northern/Southern, Zemene, Pax Romana, Phoney War, Third Venezuela |
| **P582 (end time)** | 9 | Same as P580 |
| **P571 (inception)** | 3 | Hungarian PR, Margraviate Brandenburg, Middle Kingdom Egypt |
| **P576 (dissolved)** | 3 | Same as P571 |
| **P2348 (time period)** | 1 | Northern and Southern dynasties → Six Dynasties |

### Pattern:

- 9 periods use P580/P582 (start/end time)
- 3 periods use P571/P576 (inception/dissolved)
- All 12 have BOTH start AND end dates ✅

---

## 🎯 KEY FINDINGS

### 1. **All 12 Are Valid Time Periods**

Every single one has:
- ✅ Start date
- ✅ End date
- ✅ P31 = Q11514315 (historical period)

**They should have been in our analysis but failed due to rate limits!**

### 2. **Time Ranges Span Millennia**

| Range | Count | Examples |
|-------|-------|----------|
| **Ancient (BC)** | 4 | Warring States, Early Dynastic Egypt, Middle Kingdom Egypt, Pax Romana |
| **Medieval (400-1500)** | 2 | Twenty Years' Anarchy, Northern/Southern dynasties |
| **Early Modern (1500-1800)** | 2 | Zemene Mesafint, Third Venezuela |
| **Modern (1800+)** | 4 | Margraviate, Hungarian PR, Edwardian, Phoney War |

### 3. **Duration Varies Wildly**

| Duration | Period | Years |
|----------|--------|-------|
| **Shortest** | Third Republic of Venezuela | 4 years |
| **Short** | Edwardian era | 9 years |
| **Medium** | Pax Romana | 207 years |
| **Long** | Warring States | 255 years |
| **Longest** | Margraviate of Brandenburg | 649 years |

---

## ✅ **RECOMMENDATION:**

**These 12 periods should be RETRIED and added to analysis!**

All have:
- Complete temporal bounds
- P31 = historical period
- Potential library authority IDs (need to check P244, P2163, etc.)

**Total potential:** 77 (enriched) + 12 (failed) = **89 complete time periods** 🎯
