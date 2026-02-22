# Religious Facet - Backlinks Analysis

**From:** Q17167 (Roman Republic) → P140 → Q337547 (ancient Roman religion)  
**Exploring:** Q337547's classifications and backlinks

---

## 📊 Q337547 (ANCIENT ROMAN RELIGION) CLASSIFICATIONS

### **P31 (instance of):**
- Q108704490 (**polytheistic religion**)

### **P361 (part of):**
- (Need to check - likely Roman mythology)

### **Library Authority:**
- ✅ **P244 (LCSH):** sh96009771 "Rome--Religion"

---

## 🔍 BACKLINKS TO Q108704490 (POLYTHEISTIC RELIGION)

**Query:** All entities with P31 (instance of) → Q108704490  
**Found:** 24 backlinks

### **RELIGIOUS ENTITIES DISCOVERED:**

| # | QID | Label | Region/Culture |
|---|-----|-------|----------------|
| 1 | Q812767 | Shinto | Japanese |
| 2 | Q446021 | Ancient Semitic religion | Middle Eastern |
| 3 | Q797944 | Babylonian religion | Mesopotamian |
| 4 | Q11884379 | Etruscan religion | Italian |
| 5 | Q337547 | ancient Roman religion | Roman ← OUR ORIGINAL |
| 6 | Q2914567 | Canaanite religion | Levantine |
| 7 | Q4765190 | Tai folk religion | Southeast Asian |
| 8 | Q6105081 | Assyrian religion | Mesopotamian |
| 9 | Q970026 | Ugaritic religion | Levantine |
| 10 | Q113145936 | Zulu traditional religion | African |
| ... | (14 more) | (various polytheistic religions) | (global) |

---

## 🎯 WHAT KINDS OF ENTITIES SCA WOULD FIND

### **Category 1: Ancient Polytheistic Religions (24)**

**Entity Type:** Religious systems  
**Time Period:** Ancient to modern  
**Geographic Scope:** Global

**Examples:**
- Mediterranean: Roman, Etruscan, Greek (implied)
- Middle Eastern: Babylonian, Assyrian, Canaanite, Ugaritic, Semitic
- Asian: Shinto, Tai folk religion
- African: Zulu traditional religion

**Properties these likely have:**
- P31 (instance of): polytheistic religion
- P361 (part of): Mythology systems
- P2348 (time period): Ancient periods
- P17 (country/region): Geographic locations
- P140 (practiced in): Ancient civilizations

**Library Authority potential:**
- LCSH: High (religious topics are well-catalogued)
- FAST: High (subject headings for religions)
- LCC: Likely BL800-890 (Roman/Classical religion)

---

## 🔗 WHAT BACKLINKS WOULD REVEAL

### **For Polytheistic Religion (Q108704490):**

**Expected entity types:**

| Type | Count Est. | Examples | SubjectConcept? |
|------|------------|----------|-----------------|
| **Religions** | 20-30 | Greek, Egyptian, Norse, Hindu | ✅ YES (if LCSH) |
| **Deities** | 100s | Jupiter, Mars, Venus, etc. | ⚠️ Check LCSH |
| **Mythologies** | 10-20 | Roman, Greek, Norse, Egyptian | ✅ YES (likely LCSH) |
| **Practices** | 50+ | Sacrifice, augury, festivals | ⚠️ Check LCSH |
| **Temples** | 100s | Temple of Jupiter, etc. | ❌ NO (places, not subjects) |
| **Priests** | 50+ | Pontifex, Augur, Vestal | ⚠️ Check LCSH |

---

## 🔗 WHAT ROMAN MYTHOLOGY BACKLINKS WOULD REVEAL

**If we query:** P361 (part of) → Roman mythology

**Expected entity types:**

| Type | Count Est. | Examples | SubjectConcept? |
|------|------------|----------|-----------------|
| **Deities** | 50-100 | Jupiter, Mars, Venus, Neptune | ⚠️ Check LCSH |
| **Mythological figures** | 100+ | Romulus, Remus, Aeneas | ⚠️ Check LCSH |
| **Myths/Stories** | 50+ | Founding of Rome, etc. | ⚠️ Check LCSH |
| **Religious concepts** | 20+ | Pietas, Virtus, etc. | ❌ Unlikely LCSH |
| **Religious practices** | 30+ | Triumph, augury, etc. | ⚠️ Check LCSH |

---

## 🎯 **TRIAGE BUCKETS FOR RELIGIOUS BACKLINKS:**

### **Bucket 1: Major Religions (High Priority)**

**Criteria:** 
- P31 = polytheistic religion (or other religion type)
- Has LCSH/FAST ID
- Has temporal period association

**Examples:**
- Q337547 (ancient Roman religion) ✅ LCSH: sh96009771
- Q812767 (Shinto) - check for LCSH
- Q446021 (Ancient Semitic religion) - check for LCSH

**Use:** Create RELIGIOUS facet SubjectConcepts

---

### **Bucket 2: Deities (Medium Priority)**

**Criteria:**
- P31 = deity/god
- Part of a Bucket 1 religion
- Check for LCSH (major deities often have entries)

**Examples:**
- Jupiter, Mars, Venus (Roman)
- Zeus, Athena (Greek)
- Ishtar, Marduk (Babylonian)

**Use:** Entity candidates for RELIGIOUS facet analysis

---

### **Bucket 3: Practices/Rituals (Low Priority)**

**Criteria:**
- P31 = religious practice/ritual
- Associated with Bucket 1 religions
- Rarely have LCSH (too specific)

**Examples:**
- Augury, sacrifice, triumph ceremonies

**Use:** Detail entities for SFA analysis, not SubjectConcepts

---

### **Bucket 4: Mythological Figures (Medium Priority)**

**Criteria:**
- P31 = mythological character
- Part of mythology system
- Some have LCSH (famous figures)

**Examples:**
- Romulus, Remus, Aeneas

**Use:** Check for LCSH, if present → potential SubjectConcepts

---

## 📊 **EXPECTED TRIAGE RESULTS:**

**From polytheistic religion backlinks (24 found):**
- Major religions: 15-20 (check LCSH → high % should have)
- Deities: 0 (they're subclass, not instance)
- Practices: 0-5 (some hybrid classifications)
- Mythologies: 0 (they're broader category)

**From Roman mythology backlinks (not yet queried):**
- Deities: 50-100
- Mythological figures: 50-100
- Myths/stories: 20-50
- Practices: 20-30

**Total potential:** 150-300 RELIGIOUS facet entities

---

## ✅ **KEY DISCOVERY:**

**Q337547 (ancient Roman religion):**
- ✅ Has LCSH: sh96009771
- ✅ Instance of: Q108704490 (polytheistic religion)
- ✅ 24 peer religions found (Shinto, Babylonian, Etruscan, etc.)

**Each peer religion is a SubjectConcept candidate if it has LCSH!**

**SCA behavior:**
1. Follow P140 (religion) from periods
2. Fetch religion entity
3. Get P31 (instance of) and P361 (part of)
4. Query backlinks to parent concepts
5. Triage by entity type
6. Check for LCSH/FAST
7. Create RELIGIOUS facet SubjectConcepts

**File:** `RELIGIOUS_FACET_BACKLINKS.md` 🙏
