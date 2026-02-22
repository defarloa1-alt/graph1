# SCA Candidate Buckets - Not Filters!

**Important:** SCA does NOT remove entities yet - it creates **candidate buckets** for analysis

**Rationale:** A low-property entity (Roman garment) might connect a senator to a mollusk (purple dye) - we need these connections!

---

## 🪣 BUCKET 1: TIME PERIODS WITH LIBRARY IDs (Priority)

**Criteria:**
- Has temporal bounds (P580+P582 OR P571+P576)
- **AND** has library authority (P244, P2163, P1149, P10832)

**Example:**
```
Q17167 (Roman Republic)
  ✅ P571 (inception): -0509
  ✅ P576 (dissolved): -0027
  ✅ P244 (LCSH): sh85115114
  → Bucket 1: High-confidence SubjectConcept candidate
```

**Use:** Primary SubjectConcept creation

---

## 🪣 BUCKET 2: TIME PERIODS WITHOUT LIBRARY IDs

**Criteria:**
- Has temporal bounds (P580+P582 OR P571+P576)
- **BUT** no library authority IDs

**Example:**
```
Q35560 (Attitude Era)
  ✅ P31: historical period
  ❌ P244: None
  ❌ P2163: None
  → Bucket 2: Period but not library subject
```

**Use:** 
- Check if it's part of a Bucket 1 entity (keep as child)
- Check if it connects important entities (keep as bridge)
- Otherwise: low priority

---

## 🪣 BUCKET 3: ABSTRACT CONCEPTS (Field of Study, etc.)

**Criteria:**
- P31 (instance of) = field of study, academic discipline, etc.
- OR P2579 (studied by) has values
- OR P279 (subclass of) = knowledge/academic concepts

**Example:**
```
Q41493 (ancient history)
  ✅ P31: Q1047113 (field of study)
  ✅ P2579: studied by disciplines
  ✅ P361: Q1066186 (study of history)
  → Bucket 3: Academic concept candidate
```

**Use:** Create facet ontology, link to SFAs

---

## 🪣 BUCKET 4: RELATED ENTITIES (People, Places, Events)

**Criteria:**
- Connected to Bucket 1/2/3 entities via relationships
- ANY entity type: Human, Place, Event, Organization, Work, etc.
- **NO density filter** - even 1 property is useful if it connects!

**Example:**
```
Hypothetical: Q12345 (purple dye garment)
  Properties: 3 (low density)
  P31: clothing
  P361: part of Roman senatorial dress
  P186: made from Q678 (Tyrian purple from Murex mollusk)
  
  → Bucket 4: Keep! Connects:
     - Senator (person)
     - Garment (object)
     - Mollusk (organism)
     - Purple dye (material)
     - Economic (trade)
     - Social (status symbol)
```

**Use:** Entity discovery for SubjectConcepts, relationship building

---

## 🪣 BUCKET 5: HIERARCHICAL PARENTS

**Criteria:**
- Referenced by P361 (part of) from Bucket 1 entities
- Referenced by P279 (subclass of) from Bucket 1 entities

**Example:**
```
Q1747689 (Ancient Rome)
  ← Q17167 (Roman Republic) [P361 part of]
  ← Q2277 (Roman Empire) [P361 part of]
  → Bucket 5: Parent concept, check for library IDs
```

**Use:** Build upward hierarchy, create parent SubjectConcepts

---

## 🪣 BUCKET 6: HIERARCHICAL CHILDREN

**Criteria:**
- Referenced by P527 (has parts) from Bucket 1 entities
- Referenced by P150 (contains) from Bucket 1 entities

**Example:**
```
Q2839628 (Early Roman Republic)
  Q17167 (Roman Republic) [P527] → this entity
  → Bucket 6: Child period, keep even without library IDs
```

**Use:** Build downward hierarchy, create child SubjectConcepts

---

## 🪣 BUCKET 7: SUCCESSION CHAIN

**Criteria:**
- Referenced by P155/P156 (follows/followed by) from Bucket 1

**Example:**
```
Q201038 (Roman Kingdom)
  Q17167 (Roman Republic) [P155 follows] → this entity
  → Bucket 7: Predecessor, keep for timeline
  
Q2277 (Roman Empire)
  Q17167 (Roman Republic) [P156 followed by] → this entity
  → Bucket 7: Successor, keep for timeline
```

**Use:** Build temporal succession, complete timeline

---

## 🪣 BUCKET 8: EXTERNAL IDs ONLY (Low Priority)

**Criteria:**
- Has Freebase, Quora, IMDb, etc.
- **NO** library authority IDs
- **NOT** connected to Bucket 1-7 entities

**Example:**
```
Hypothetical: Q99999 (pop culture period)
  P3417 (Quora ID): xyz
  P646 (Freebase ID): /m/abc
  No P244, P2163, P1149
  No connections to scholarly periods
  → Bucket 8: Low priority, evaluate later
```

**Use:** Review manually, might have scholarly value not yet linked

---

## 🪣 BUCKET 9: FAILED/INCOMPLETE (Retry)

**Criteria:**
- Query failed (rate limit, timeout, etc.)
- Incomplete data
- Need retry

**Example:**
```
Q185063 (Warring States period)
  Error: 429 Too Many Requests
  → Bucket 9: Retry after rate limit reset
```

**Use:** Retry queue

---

## 📊 BUCKET PRIORITY FOR SCA

| Priority | Bucket | Action | Why |
|----------|--------|--------|-----|
| **1** | Time Periods + Library IDs | Create SubjectConcepts immediately | High confidence scholarly subjects |
| **2** | Abstract Concepts (field of study) | Create facet ontology | Academic framework |
| **3** | Parents/Children/Succession | Create if in Bucket 1's network | Complete hierarchies |
| **4** | Related Entities (people, places) | Collect, analyze connections | Build entity network |
| **5** | Periods without Library IDs | Evaluate connections | Might be children/bridges |
| **6** | External IDs only | Low priority review | Check for missed scholarly value |
| **7** | Failed/Incomplete | Retry later | Complete the dataset |

---

## 🎯 NO REMOVAL YET!

**SCA Workflow:**

```
1. Fetch all candidates → Put in buckets
2. Analyze connections → Understand relationships  
3. Map to facets → Understand domain coverage
4. Check library IDs → Identify scholarly subjects
5. Build network graph → See the structure
6. THEN decide → What to keep/remove based on network role

NOT:
  ❌ Filter early based on density
  ❌ Remove before seeing connections
  ❌ Assume without checking
```

---

## 💡 KEY INSIGHT:

**Even a 1-property entity can be crucial:**

```
Senator → wears → Purple Garment (1 prop)
  ↓
Purple Garment → made from → Murex Mollusk (1 prop)
  ↓
Murex → from → Mediterranean Sea (1 prop)
  ↓
REVEALS:
  - ECONOMIC facet (luxury trade)
  - GEOGRAPHIC facet (Mediterranean)
  - SOCIAL facet (status symbol)
  - ENVIRONMENTAL facet (marine biology)
```

**Keep everything in buckets, filter based on ROLE not DENSITY!**

---

## ✅ **REVISED APPROACH:**

**SCA creates buckets, SFAs analyze content, THEN we filter based on:**
1. Network role (connector, leaf, hub)
2. Facet coverage (does it add new facet dimensions?)
3. Scholarly value (library IDs = high, connections = medium, isolated = low)

**No premature removal!** 🎯
