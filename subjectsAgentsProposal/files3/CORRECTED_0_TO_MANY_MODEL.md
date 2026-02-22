# CORRECTED: 0-to-Many Claims per Facet Model

**Date**: 2026-02-15  
**Correction**: Fixed from forced 1:1 to natural 0-to-many distribution

---

## **What Changed**

### **WRONG Approach (v1):**
```
Force agent to generate exactly 1 claim per facet
→ Artificial constraint
→ Results in weak claims for some facets
→ Doesn't reflect historical reality
```

### **CORRECT Approach (v2):**
```
Agent generates 25-30 historically significant claims
→ Natural distribution across facets
→ Some facets have many claims (Military: 8, Political: 6)
→ Some facets have few or zero claims (Artistic: 0)
→ Reflects actual historical importance and documentation
```

---

## **Why This is Better**

### **1. Historical Accuracy**
Roman Republic is better documented in military and political dimensions than artistic or philosophical. The claim distribution should reflect this reality.

### **2. Agent Flexibility**
Agents shouldn't be forced to generate claims where evidence is weak or topics are less significant.

### **3. Future-Proof**
When we add specialized sub-agents, they'll naturally generate multiple claims for their domain:
- `MilitaryAgent` → 5-10 military claims
- `PoliticalAgent` → 5-8 political claims
- `ArtisticAgent` → 0-2 artistic claims (less documentation)

---

## **Expected Distribution for Roman Republic**

Based on historical documentation:

| Facet | Expected Claims | Rationale |
|-------|----------------|-----------|
| Military | 6-10 | Well-documented (legion structure, tactics, wars) |
| Political | 6-9 | Extensive sources (Senate, magistrates, laws) |
| Social | 3-5 | Good documentation (class structure, citizenship) |
| Legal | 3-5 | Strong sources (Twelve Tables, legal texts) |
| Economic | 2-4 | Moderate documentation (trade, coinage) |
| Diplomatic | 2-4 | Treaty records, embassy accounts |
| Religious | 2-4 | Ritual documentation, priestly records |
| Literary | 2-3 | Major authors (Cicero, Caesar, Livy) |
| Communication | 2-3 | Rhetoric, speeches, propaganda |
| Geographic | 1-3 | Expansion records, provincial administration |
| Biographical | 1-3 | Major figures (Caesar, Scipio, etc.) |
| Cultural | 1-2 | Some documentation |
| Technological | 1-2 | Limited to military/infrastructure |
| Agricultural | 0-2 | Some sources (Cato, Varro) |
| Scientific | 0-1 | Very limited |
| Philosophical | 0-1 | Limited to late Republic |
| Artistic | 0-1 | Very limited documentation |

**Total: 25-35 claims** (natural distribution)

---

## **Data Model**

### **Claim Structure (Updated)**

```json
{
  "claim_text": "The maniple formation provided tactical flexibility...",
  "primary_facet": "Military",
  "related_facets": ["Political", "Technological"],
  "evidence": { ... },
  "confidence": 0.92,
  "temporal": { ... }
}
```

**Key Changes:**
- `facet` → `primary_facet` (more explicit)
- `related_facets` remains (0-to-many secondary facets)
- Multiple claims can have same `primary_facet`

---

## **Neo4j Graph Pattern**

### **Before (Wrong):**
```
SubjectConcept ─[:HAS_CLAIM]→ Claim1 ─[:ABOUT_FACET]→ Military
                              Claim2 ─[:ABOUT_FACET]→ Political
                              Claim3 ─[:ABOUT_FACET]→ Social
                              ...
                              Claim17 ─[:ABOUT_FACET]→ Communication

(Exactly 17 claims, one per facet - forced)
```

### **After (Correct):**
```
SubjectConcept ─[:HAS_CLAIM]→ Claim1 ─[:ABOUT_FACET]→ Military
              │                Claim2 ─[:ABOUT_FACET]→ Military
              │                Claim3 ─[:ABOUT_FACET]→ Military
              │                Claim4 ─[:ABOUT_FACET]→ Political
              │                Claim5 ─[:ABOUT_FACET]→ Political
              │                ...
              └───[:HAS_CLAIM]→ Claim27 ─[:ABOUT_FACET]→ Communication

(25-30 claims, naturally distributed - some facets have 0, some have 8+)
```

---

## **Validation Updates**

### **Old Validation:**
- ❌ Required exactly 17 claims
- ❌ Required all 17 facets covered
- ❌ Rejected duplicate facets

### **New Validation:**
- ✅ Requires 20-40 claims (flexible)
- ✅ Warns if < 8 facets covered (diversity check)
- ✅ Allows multiple claims per facet
- ✅ Shows facet distribution (0, 1-2, 3+)

---

## **ChatGPT Prompt Changes**

### **Old Prompt:**
```
Generate ONE claim for each of the 17 facets
```

### **New Prompt:**
```
Generate 25-30 historically significant claims about Roman Republic.
Tag each with primary_facet and related_facets.
Some facets will have many claims, some may have zero - this is OK!
Focus on historical importance, not forced coverage.
```

---

## **What This Means for Future Development**

### **Phase 1: Smoke Test (Current)**
```
Single ChatGPT agent generates 25-30 claims
→ Natural distribution
→ Validates model works
```

### **Phase 2: Specialized Agents**
```
MilitaryAgent → Generates 5-10 military claims
PoliticalAgent → Generates 5-8 political claims
CommunicationAgent → Generates 2-4 communication claims
ArtisticAgent → Generates 0-1 artistic claims (limited sources)
```

### **Phase 3: Dynamic Spawning**
```
User submits claim: "Caesar's Gallic War was propaganda"
→ Coordinator analyzes: Military + Political + Communication + Literary
→ Spawns 4 sub-agents
→ Each generates claims from their perspective
→ Result: 4-12 total claims across facets
```

---

## **Examples of Natural Claim Generation**

### **Military Facet (8 claims):**
1. Maniple formation adoption (315 BC)
2. Legion reorganization under Marius (107 BC)
3. Punic War naval innovations
4. Siege tactics at Alesia
5. Centurion leadership structure
6. Military road construction (Via Appia)
7. Auxiliary troop integration
8. Triumphal procession traditions

### **Artistic Facet (0 claims):**
(No claims generated - limited documentation for Republican period art)

### **Political Facet (7 claims):**
1. Conflict of the Orders resolution (287 BC)
2. Consulship power-sharing system
3. Tribune veto authority
4. Senate foreign policy dominance
5. Centuriate assembly voting
6. Provincial governance structure
7. Cursus honorum career path

---

## **Files Updated**

1. **`chatgpt_prompt_roman_republic.txt`**
   - Changed from "17 claims" to "25-30 claims"
   - Added emphasis on natural distribution
   - Changed `facet` to `primary_facet`

2. **`validate_claims.py`**
   - Removed strict 17-claim requirement
   - Added flexible 20-40 range with warnings
   - Changed to show facet distribution
   - Removed duplicate facet error (now expected)

3. **`ingest_claims.py`**
   - Updated to handle `primary_facet` field
   - Backward compatible with old `facet` field
   - Handles multiple claims per facet

---

## **Success Criteria (Updated)**

### **Quantitative:**
- ✅ 20-40 claims generated
- ✅ At least 8 different facets covered
- ✅ Military and Political have most claims (5-10 each)
- ✅ All claims have required fields
- ✅ Confidence scores 0.0-1.0

### **Qualitative:**
- ✅ Claims are historically significant
- ✅ Distribution reflects documentation reality
- ✅ No forced/weak claims for poorly-documented facets
- ✅ Evidence is real and verifiable

---

## **Next Steps**

1. **Run corrected smoke test**
   - Use updated `chatgpt_prompt_roman_republic.txt`
   - Expect 25-30 claims with natural distribution
   - Validate with updated scripts

2. **Analyze distribution**
   - Which facets have most claims?
   - Does it match expected distribution?
   - Are there surprising gaps or concentrations?

3. **Iterate if needed**
   - If all claims are military → prompt needs balance adjustment
   - If distribution is too flat → agent isn't prioritizing importance

4. **Build specialized agents**
   - Start with MilitaryAgent (should generate 5-10 claims)
   - Then PoliticalAgent
   - Then CommunicationAgent

---

**This corrected model reflects reality: not all dimensions of a subject are equally documented or significant.**
