# P2184 (History of Topic) - Discovery Results

**Query:** Find all entities that HAVE P2184 property  
**Found:** 100 entities (first page only)

---

## 📊 WHAT WAS DISCOVERED

### **Entities WITH P2184 (history of topic):**

**Countries (18):**
- Q30 (United States) → Q131110 (history of the United States)
- Q145 (United Kingdom) → Q113162 (history of the United Kingdom)
- Q142 (France) → Q7778 (history of France)
- Q159 (Russia) → Q161414 (history of Russia)
- Q41 (Greece) → Q7794 (history of Greece)
- Q219 (Bulgaria) → Q7800 (history of Bulgaria)
- Q45 (Portugal) → Q7790 (history of Portugal)
- Q794 (Iran) → Q28926 (history of Iran)
- ... and 10 more countries

**Regions/Continents (4):**
- Q46 (Europe) → Q7787 (history of Europe)
- Q15 (Africa) → Q149813 (history of Africa)
- Q49 (North America) → Q149527 (history of North America)
- Q39760 (Gaza Strip) → Q73569 (history of Gaza)

**Events (6+):**
- Q361 (World War I) → Q74978 (timeline of World War I)
- Q362 (World War II) → (multiple timelines/histories)

**Topics/Subjects (20+):**
- Q166543 (general anaesthesia) → Q40029 (history of general anesthesia)
- Q860372 (digital art) → Q50637 (art history)
- Q2018526 (arts) → Q50641 (history of art)
- Q25558247 (Chinese civilization) → Q82972 (history of China)

**Organizations (2):**
- Q1065 (United Nations) → Q172416 (history of the United Nations)

**Technology (1):**
- Q48493 (iOS) → Q27148 (iOS version history)

---

## 🎯 **THE TARGET ENTITIES (100 "history of X" topics):**

### **What P2184 points TO (the history topics themselves):**

**Major History Topics:**

| QID | Label | Subject Area | Likely has LCSH? |
|-----|-------|--------------|------------------|
| Q131110 | history of the United States | National history | ✅ YES |
| Q113162 | history of the United Kingdom | National history | ✅ YES |
| Q7778 | history of France | National history | ✅ YES |
| Q161414 | history of Russia | National history | ✅ YES |
| Q7794 | history of Greece | National history | ✅ YES |
| Q7787 | history of Europe | Regional history | ✅ YES |
| Q149813 | history of Africa | Regional history | ✅ YES |
| Q82972 | history of China | National history | ✅ YES |
| Q50641 | history of art | Art history | ✅ YES |
| Q50637 | art history | Academic field | ✅ YES |
| Q74978 | timeline of World War I | Military history | ✅ Likely |
| Q172416 | history of the United Nations | Organizational history | ✅ Likely |
| Q28926 | history of Iran | National history | ✅ YES |
| Q40029 | history of general anesthesia | Medical history | ⚠️ Maybe |
| ... | (86 more history topics) | (various) | (check each) |

---

## 🔍 **WHAT SCA SHOULD DO WITH THESE:**

### **Step 1: Extract all unique "history of X" QIDs**

From 100 P2184 values, we have ~50-80 unique history topics

### **Step 2: Fetch each history topic**

For each (e.g., Q7778 "history of France"):
- Get P31 (instance of) - is it a field? academic discipline?
- Get P279 (subclass of) - parent field?
- Get P361 (part of) - broader history?
- Get P244 (LCSH) - library authority?
- Get P2163 (FAST) - subject heading?

### **Step 3: Query backlinks to each history topic**

Example: Q7778 (history of France)
```sparql
SELECT ?item WHERE {
  {?item wdt:P31 wd:Q7778}  # instance of history of France
  UNION
  {?item wdt:P361 wd:Q7778} # part of history of France  
  UNION
  {?item wdt:P279 wd:Q7778} # subclass of history of France
}
```

**Expected finds:**
- French monarchs
- French revolutions
- French wars
- French periods (Bourbon, Valois, Capetian)
- French territories

### **Step 4: Do 5-hop from each history topic**

**Would reveal:**
- All French historical periods
- All French historical figures
- All French historical events
- Complete French history domain!

---

## 📊 **ESTIMATED EXPANSION:**

**If SCA explores P2184 targets:**

| History Topic | Est. Entities | Examples |
|---------------|---------------|----------|
| history of France | 500+ | Monarchs, periods, wars, revolutions |
| history of USA | 500+ | Presidents, states, wars, movements |
| history of Europe | 1000+ | All European entities |
| history of China | 800+ | Dynasties, emperors, periods |
| history of art | 1000+ | Artists, movements, works |
| ... (80 more) | (variable) | (comprehensive) |

**Total potential:** 10,000-50,000+ entities across all history domains!

---

## 🎯 **SCA BEHAVIOR FOR P2184:**

```
1. Find entities with P2184 (history of topic)
   → Got: 100 entities (countries, regions, topics)

2. Extract P2184 values (the history topics themselves)
   → Got: ~80 unique history topics

3. For EACH history topic:
   a. Fetch entity data
   b. Check P244 (LCSH) - if yes → SubjectConcept candidate
   c. Check P31/P279/P361 - get classifications
   d. Query backlinks (what's instance of / part of this history?)
   e. Do 5-hop from history topic
   f. Map all findings to 18 facets

4. Organize by domain:
   → Bucket: French history entities
   → Bucket: American history entities
   → Bucket: Chinese history entities
   → etc.

5. Check ALL for library authorities
   → Keep if LCSH/FAST/LCC
   → Evaluate if connected to kept entities
```

---

## ✅ **KEY DISCOVERY:**

**P2184 reveals 100 "history of X" topics!**

Each topic is:
- A potential SubjectConcept (check LCSH)
- An entry point to a complete domain
- A facet-specific subject area

**Examples:**
- history of France → POLITICAL, MILITARY, CULTURAL facets
- history of art → ARTISTIC, CULTURAL facets
- history of United Nations → DIPLOMATIC, POLITICAL facets

**SCA should explore P2184 targets with full 5-hop traversal!** 📚
