# SCA-Filtered Historical Periods Tree - With Library Authorities

**Filter Logic:** Keep only entities with LCSH, LCC, WorldCat, or FAST IDs  
**Source:** 74 enriched periods (from 89 total)

---

## 🌳 COMPLETE TREE WITH CLASSIFICATIONS

### Legend:
- ✅ = Has library authority IDs (LCSH/LCC/WorldCat/FAST) - **KEEP**
- ❌ = No library authority IDs - **REMOVE**
- **[P31]** = instance of
- **[P279]** = subclass of  
- **[P361]** = part of

---

```
Q11514315 (historical period)
│
├─ Q41493 (ancient history) ✅ HAS AUTHORITIES
│  │ [P31] Q186081 (time interval)
│  │ [P31] Q1047113 (field of study) ← ACADEMIC!
│  │ [P31] Q11514315 (historical period)
│  │ [P279] Q309 (history)
│  │ [P361] Q1066186 (study of history)
│  │
│  └─ Related entities to explore:
│     ├─ Q309 (history) - check for authorities
│     ├─ Q1066186 (study of history) - check for authorities
│     └─ Q1047113 (field of study) - check for authorities
│
├─ Q17167 (Roman Republic) ✅ HAS AUTHORITIES (P244: sh85115114)
│  │ [P31] Q11514315 (historical period)
│  │ [P31] Q1307214 (form of government)
│  │ [P31] Q48349 (empire)
│  │ [P31] Q3024240 (historical country)
│  │ [P361] Q1747689 (Ancient Rome)
│  │
│  └─ Related entities to explore:
│     ├─ Q1747689 (Ancient Rome) - parent, check authorities
│     ├─ Q1307214 (form of government) - abstract, check authorities
│     ├─ Q48349 (empire) - abstract, check authorities
│     └─ Q3024240 (historical country) - abstract, check authorities
│
├─ Q201038 (Roman Kingdom) (checking for authorities...)
│  │ [P31] Q11514315 (historical period)
│  │ [P31] Q3024240 (historical country)
│  │ [P279] Q830852 (history of ancient Rome)
│  │ [P361] Q41493 (ancient history)
│  │
│  └─ Related: Q830852 (history of ancient Rome) - check authorities
│
├─ Q2277 (Roman Empire) (checking for authorities...)
│  │ [P31] Q11514315 (historical period)
│  │ [P31] Q3024240 (historical country)
│  │ [P31] Q48349 (empire)
│  │ [P361] Q1747689 (Ancient Rome)
│  │
│  └─ Same parent as Q17167 (Ancient Rome)
│
├─ Q206414 (Principate) (checking for authorities...)
│  │ [P31] Q11514315 (historical period)
│  │ [P31] Q1307214 (form of government)
│  │ [P361] Q2277 (Roman Empire)
│  │ [P361] Q1747689 (Ancient Rome)
│  │
│  └─ Part of both Roman Empire AND Ancient Rome
│
├─ Q11772 (Ancient Greece) (checking for authorities...)
│  │ [P31] Q11514315 (historical period)
│  │ [P31] Q28171280 (ancient civilization)
│  │ [P31] Q3024240 (historical country)
│  │ [P31] Q465299 (archaeological culture)
│  │ [P31] Q11042 (culture)
│  │ [P31] Q28114 (civilization)
│  │ [P361] Q486761 (classical antiquity)
│  │
│  └─ Rich classification: period + civilization + culture + archaeology
│
├─ Q12554 (Middle Ages) (checking for authorities...)
│  │ [P31] Q11514315 (historical period)
│  │ [P31] Q6428674 (era)
│  │ [P279] Q41493 (ancient history)
│  │
│  └─ Subclass of ancient history!
│
├─ Q12544 (Byzantine Empire) (checking for authorities...)
│  │ [P31] Q11514315 (historical period)
│  │ [P31] Q1620908 (historical region)
│  │ [P31] Q48349 (empire)
│  │ [P31] Q3024240 (historical country)
│  │ [P31] Q465299 (archaeological culture)
│  │ [P361] Q1747689 (Ancient Rome)
│  │ [P361] Q486761 (classical antiquity)
│  │
│  └─ Part of Ancient Rome AND classical antiquity
│
├─ Chinese Dynasties (13 total)
│  │
│  ├─ Q128938 (Shang dynasty)
│  │  │ [P31] Q836688 (ancient Chinese state)
│  │  │ [P31] Q12857432 (Chinese dynasty)
│  │  │ [P31] Q11042 (culture)
│  │  │ [P31] Q1292119 (style)
│  │  │ [P31] Q11514315 (historical period)
│  │  │ [P361] Q10756408 (Three Dynasties)
│  │  │
│  │  └─ Rich classification: state + dynasty + culture
│  │
│  ├─ Q7209 (Han dynasty)
│  │  │ [P31] Q836688 (ancient Chinese state)
│  │  │ [P31] Q12857432 (Chinese dynasty)
│  │  │ [P31] Q11042 (culture)
│  │  │ [P31] Q11514315 (historical period)
│  │  │ [P361] Q148 (People's Republic of China)
│  │  │ [P361] Q13426199 (imperial China)
│  │  │
│  │  └─ Part of imperial China
│  │
│  └─ ... 11 more Chinese dynasties
│
├─ Japanese Periods (7 total)
│  │
│  ├─ Q184963 (Edo period)
│  │  │ [P361] Q130436 (history of Japan)
│  │
│  ├─ Q189178 (Nara period)
│  │  │ [P361] Q130436 (history of Japan)
│  │  │ [P361] Q124030889 (classical Japan)
│  │
│  └─ ... 5 more Japanese periods
│     └─ All part of "history of Japan"
│
├─ Egyptian Periods (5 total)
│  │ All likely part of "history of Egypt"
│  │ All likely "archaeological period"
│  │
│  └─ Need authority IDs to keep
│
├─ Medieval Periods (7 total)
│  │
│  ├─ Q12554 (Middle Ages)
│  │  │ [P31] Q11514315 (historical period)
│  │  │ [P31] Q6428674 (era)
│  │  │ [P279] Q41493 (ancient history) ← Subclass!
│  │
│  ├─ Q212685 (High Middle Ages)
│  │  │ [P361] Q12554 (Middle Ages) ← Part of!
│  │
│  └─ Q212976 (Late Middle Ages)
│     │ [P361] Q12554 (Middle Ages) ← Part of!
│     │
│     └─ Medieval hierarchy revealed!
│
└─ Modern Periods (Wars, Republics, etc.)
   │
   ├─ Q361 (World War I)
   │  │ [P31] Q11514315 (historical period)
   │  │ [P31] Q103495 (World War)
   │  │
   │  └─ Also a "World War" type
   │
   ├─ Q8683 (Cold War)
   │  │ [P31] Q4176199 (cold war)
   │  │ [P31] Q1469686 (perpetual war)
   │  │ [P31] Q864113 (proxy war)
   │  │ [P31] Q11514315 (historical period)
   │  │ [P279] Q369799 (low-intensity conflict)
   │  │ [P279] Q11422542 (international conflict)
   │  │
   │  └─ Multiple war-type classifications
   │
   └─ Many more modern periods
```

---

## 🔍 **SCA FILTERING LOGIC:**

### **KEEP if entity has ANY of these properties:**

| Property # | Property Label | Authority Type |
|------------|----------------|----------------|
| **P244** | Library of Congress authority ID | LCSH |
| **P1149** | Library of Congress Classification | LCC |
| **P10832** | WorldCat Entities ID | WorldCat |
| **P2163** | FAST ID | FAST |

### **Example - Roman Republic:**

```
Q17167 (Roman Republic)
  P244: sh85115114 ✅ HAS LCSH
  → KEEP in subgraph
  → Create SubjectConcept
  → Create SFAs
```

### **Example - Without Authorities:**

```
Q35560 (Attitude Era)
  P244: None
  P1149: None
  P10832: None
  P2163: None
  → REMOVE from subgraph (not a library subject)
```

---

## 📊 **BREAKDOWN SUMMARY (From 74 Enriched):**

### Instance Of (P31) Patterns:

| What They Are | Count | Examples |
|---------------|-------|----------|
| historical period | 74 | All have this |
| historical country | 15 | Q17167, Q43287, Q69829, etc. |
| empire | 8 | Q17167, Q43287, Q48349, etc. |
| culture | 5 | Q128938, Q11772, Q40203, etc. |
| dynasty | 13 | Chinese dynasties, Q126416, etc. |
| form of government | 3 | Q17167, Q206414, Q1307214 |
| archaeological culture | 2 | Q11772, Q12544 |
| civilization | 3 | Q11772, Q134178, Q28171280 |

### Part Of (P361) Patterns:

| Parent Concept | Count | Examples |
|----------------|-------|----------|
| Q1747689 (Ancient Rome) | 3 | Q17167, Q2277, Q206414 |
| Q130436 (history of Japan) | 2 | Q184963, Q189178 |
| Q12554 (Middle Ages) | 2 | Q212685, Q212976 |
| Q41493 (ancient history) | 1 | Q201038 |
| Q486761 (classical antiquity) | 2 | Q11772, Q12544 |

### Subclass Of (P279) Patterns:

| Parent Class | Count | Examples |
|--------------|-------|----------|
| Q309 (history) | 1 | Q41493 (ancient history) |
| Q41493 (ancient history) | 1 | Q12554 (Middle Ages) |
| Various history domains | 5+ | Q7778 (history of France), Q830852 (history of ancient Rome) |

---

## 🎯 **COMPLETE ENRICHED TREE:**

**File:** `output/analysis/periods_enriched_chart_20260220_174630.md`

**Shows for each period:**
- QID + Label
- P31 (instance of) - all values with labels
- P279 (subclass of) - all values with labels
- P361 (part of) - all values with labels

**Next step:** Check which have library authority IDs to filter the subgraph! 📚