# Complete Succession Chain - All Candidate Nodes

**Properties captured:** P155 (follows), P156 (followed by), P1365 (replaces), P1366 (replaced by)  
**Found in:** 5-hop data (100 entities)

---

## 📊 SUCCESSION PROPERTY COVERAGE

```
P155 (follows): 6 entities have this property
P156 (followed by): 6 entities have this property
P1365 (replaces): 2 entities have this property
P1366 (replaced by): 2 entities have this property

Total entities with succession: 8 unique
Total succession relationships: 16 (some entities have multiple)
```

---

## 🔗 COMPLETE SUCCESSION CHAINS

### **Chain 1: Roman Timeline (Main)**

```
Q2566630 (Roman Iron Age)
    ↓ P156 (followed by)
Q201038 (Roman Kingdom) ← CANDIDATE
    ↓ P156 / P1366 (followed by / replaced by)
Q17167 (Roman Republic) ← ROOT ← CANDIDATE
    ├─ Q2839628 (Early Roman Republic) ← CANDIDATE
    │   ↓ P156
    ├─ Q6106068 (Middle Roman Republic) ← CANDIDATE
    │   ↓ P156
    └─ Q2815472 (Late Roman Republic) ← CANDIDATE
        ↓ P156
Q787204 (High Roman Empire) ← CANDIDATE (NEW!)
    ↓
Q2277 (Roman Empire) ← CANDIDATE
    AND
Q206414 (Principate) ← CANDIDATE
    ↓
(continues...)
```

### **Chain 2: Ancient Rome Extended**

```
Q1747689 (Ancient Rome) ← CANDIDATE
    ↓ P156 (followed by)
Q3940476 (Rome in the Middle Ages) ← CANDIDATE (NEW!)
    AND
Q12544 (Byzantine Empire) ← CANDIDATE
```

### **Chain 3: Early Republic Transitions**

```
Q201038 (Roman Kingdom)
    ↓
Q16931679 (Overthrow of the Roman monarchy) ← CANDIDATE (NEW!)
    ↓
Q2839628 (Early Roman Republic)
    
AND

Q119137625 (Second Roman Kingdom) ← CANDIDATE (NEW!)
    ↓ P156
Q2839628 (Early Roman Republic)
```

### **Chain 4: Pre-Kingdom**

```
Q5171759 (Corniculum) ← CANDIDATE (NEW!)
    ↓ P1366 (replaced by)
Q201038 (Roman Kingdom)
```

---

## 📋 ALL CANDIDATE NODES FROM SUCCESSION

### **Nodes in 5-hop data (8):**

| QID | Label | Property | In Our 100? |
|-----|-------|----------|-------------|
| Q17167 | Roman Republic | P155, P156, P1365, P1366 | ✅ YES |
| Q201038 | Roman Kingdom | P155, P156, P1365, P1366 | ✅ YES |
| Q1747689 | Ancient Rome | P155, P156 | ✅ YES |
| Q2839628 | Early Roman Republic | P155, P156 | ✅ YES |
| Q6106068 | Middle Roman Republic | P155, P156 | ✅ YES |
| Q2815472 | Late Roman Republic | P155, P156 | ✅ YES |
| Q206414 | Principate | (referenced) | ✅ YES |
| Q2277 | Roman Empire | (referenced) | ❌ NO (not fetched in 5-hop) |

### **NEW Nodes Referenced but NOT in 5-hop (9):**

| QID | Label | Relationship | Status |
|-----|-------|--------------|--------|
| Q2277 | Roman Empire | P156 from Q17167 | ❌ NOT IN 100 |
| Q787204 | High Roman Empire | P156 from Q2815472 | ❌ NOT IN 100 |
| Q3940476 | Rome in the Middle Ages | P156 from Q1747689 | ❌ NOT IN 100 |
| Q12544 | Byzantine Empire | P156 from Q1747689 | ❌ NOT IN 100 |
| Q16931679 | Overthrow of monarchy | P155 to Q2839628 | ❌ NOT IN 100 |
| Q119137625 | Second Roman Kingdom | P156 to Q2839628 | ❌ NOT IN 100 |
| Q2566630 | Roman Iron Age | P156 to Q201038 | ❌ NOT IN 100 |
| Q5171759 | Corniculum | P1366 to Q201038 | ❌ NOT IN 100 |
| Q634818 | culture | P155 from Q1747689 | ❌ NOT IN 100 |

---

## 🎯 **ANSWER: PARTIALLY CAPTURED**

### ✅ **What WAS captured:**

- Succession properties exist in the data (P155, P156, P1365, P1366)
- 8 entities have succession relationships
- Immediate predecessors/successors identified

### ❌ **What was NOT fully explored:**

**9 entities referenced in succession but NOT fetched:**
- Q2277 (Roman Empire) - successor
- Q787204 (High Roman Empire) - successor to Late Republic
- Q3940476 (Rome in Middle Ages) - successor to Ancient Rome
- Q12544 (Byzantine Empire) - successor to Ancient Rome
- And 5 more...

**Why not in 100?**
- Succession was NOT explored recursively
- Only fetched 1 hop in succession (immediate before/after)
- Did NOT fetch the successors' successors
- Did NOT fetch the predecessors' predecessors

---

## 🔍 **WHAT THIS REVEALS:**

### **Missing from our exploration:**

```
BACKWARD (not explored):
  ? → Corniculum → Roman Kingdom → Roman Republic

FORWARD (not explored):
  Roman Republic → Principate → ? → ? → Byzantine Empire → ?
  Late Republic → High Roman Empire → ? → ?
  Ancient Rome → Rome in Middle Ages → ?
```

**The succession chain continues BEYOND what we fetched!**

---

## 📊 **COMPLETE SUCCESSION CANDIDATES:**

**Known (in our data):** 8 entities  
**Referenced but not fetched:** 9 entities  
**Total succession candidates:** **17 entities**

### **All 17 Succession Candidate Nodes:**

1. Q5171759 (Corniculum) - pre-Kingdom
2. Q2566630 (Roman Iron Age) - pre-Kingdom
3. Q201038 (Roman Kingdom) ✅
4. Q16931679 (Overthrow of monarchy) - transition
5. Q119137625 (Second Roman Kingdom) - parallel?
6. Q2839628 (Early Roman Republic) ✅
7. Q6106068 (Middle Roman Republic) ✅
8. Q2815472 (Late Roman Republic) ✅
9. Q17167 (Roman Republic) ✅ ROOT
10. Q206414 (Principate) ✅
11. Q787204 (High Roman Empire) - early empire
12. Q2277 (Roman Empire) - main empire
13. Q1747689 (Ancient Rome) ✅ - overarching
14. Q3940476 (Rome in the Middle Ages) - medieval
15. Q12544 (Byzantine Empire) - late empire
16. Q634818 (culture) - abstract?
17. (Unknown) - what came after Byzantine?

---

## 🎯 **RECOMMENDATION:**

**SCA should RECURSIVELY explore succession:**

```python
def explore_succession_chain(qid, direction='both', max_hops=10):
    """
    direction: 'forward', 'backward', or 'both'
    """
    if direction in ['backward', 'both']:
        # Follow P155 (follows) and P1365 (replaces)
        recursively fetch predecessors
    
    if direction in ['forward', 'both']:
        # Follow P156 (followed by) and P1366 (replaced by)
        recursively fetch successors
```

**This would capture the COMPLETE timeline!**

**All succession chain entities are candidate nodes for SubjectConcepts!** ⏱️