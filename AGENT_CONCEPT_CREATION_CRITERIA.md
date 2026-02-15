# Agent Criteria for Proposing New SubjectConcepts

**Date**: 2026-02-15  
**Purpose**: Define when agents should create new SubjectConcepts vs reuse existing ones  
**Goal**: Ground concepts in canonical standards while enabling discovery

---

## 1. Decision Tree: Should Agent Create New Concept?

```
Agent discovers entity/event → Wants to create SubjectConcept

Step 1: CHECK HIERARCHY
├─ Does parent concept exist in SubjectConceptRegistry?
│  ├─ YES → Continue to Step 2
│  └─ NO → REJECT (can't create orphan concepts)

Step 2: CHECK WIKIDATA
├─ Does Wikidata Q-identifier exist?
│  ├─ YES → Go to TIER 1 validation
│  └─ NO → Go to TIER 3 validation

Step 3: CHECK AUTHORITIES
├─ Can concept be mapped to LCC/LCSH/FAST?
│  ├─ YES (1+ authorities aligned) → Continue
│  └─ NO → Go to TIER 4 validation (if confidence high)

Step 4: VALIDATE PRIMARY SOURCES
├─ Is evidence from historical documents/scholarly sources?
│  ├─ YES → Continue
│  └─ NO → REJECT (unsourced)

Step 5: TEMPORAL VALIDATION
├─ Are period_start/period_end verifiable?
│  ├─ YES → Continue
│  └─ NO → REJECT (unverifiable timeline)

Step 6: CONFIDENCE CHECK
├─ confidence >= 0.75?
│  ├─ YES → APPROVE (or pending_review if < 0.90)
│  └─ NO → REJECT

Result: APPROVED or REJECTED with reason
```

---

## 2. Tiered Validation Framework

### **TIER 1: Canonical Standard (Highest Confidence)**
**Criteria**: Wikidata + Authority Alignment

✅ **APPROVE** new concept if:
1. ✓ Concept exists in Wikidata (has Q-identifier)
2. ✓ Maps to ≥1 authority (LCC primary, or LCSH, or FAST)
3. ✓ Primary source evidence provided
4. ✓ Parent concept exists
5. ✓ Temporal bounds verifiable
6. ✓ confidence >= 0.80

**Examples:**
- "Battle of Cannae" (Q181098) → LCC DG262 + LCSH sh85010755
- "Caesar's Dictatorship" (Q26884) → LCSH sh85021241

**Agent Action:**
```python
concept = api.claim_new_concept(
    label="Battle of Cannae",
    parent_id="subj_f36bb758dbd1",  # Punic Wars
    wikidata_qid="Q181098",
    lcc_codes=["DG262"],
    lcsh_ids=["sh85010755"],
    confidence=0.93,
    evidence="Livy, Polybius, primary sources"
)
# Status: auto_approved (confidence >= 0.90)
```

---

### **TIER 2: Wikidata-Only (High Confidence)**
**Criteria**: Wikidata exists, authorities not yet mapped

✅ **APPROVE** new concept if:
1. ✓ Concept exists in Wikidata
2. ✗ No LCC/LCSH/FAST alignment YET (deferred to authority mapping phase)
3. ✓ Primary source evidence
4. ✓ Parent exists
5. ✓ Temporal bounds verifiable
6. ✓ confidence >= 0.82

**Examples:**
- Lesser-known historical figures: "Vercingetorix" (Q206209)
- Regional events: "Siege of Alesia" (Q187699)

**Notes:**
- Authority alignment can be added later (Phase 3 enhancement)
- Concept is still canonical (grounded in Wikidata)
- Search LCC/LCSH/FAST but don't reject if nothing found

**Agent Action:**
```python
# At create time:
concept = api.claim_new_concept(
    label="Vercingetorix",
    parent_id="subj_roman_republic",
    wikidata_qid="Q206209",
    lcc_codes=[],  # Not yet mapped
    lcsh_ids=[],
    confidence=0.87,
    evidence="Gallic Wars sources, Wikipedia"
)

# Later (Phase 3):
# Authority mapping job finds: 
#   LCC DP801.G2 (Gallic history)
#   LCSH sh85143748
# Update concept with authority links
```

---

### **TIER 3: Authority-Grounded Discovery (Medium Confidence)**
**Criteria**: NOT in Wikidata, but grounded in LCC/LCSH/FAST authority classification

✅ **APPROVE** new concept if:
1. ✗ No Wikidata Q-identifier
2. ✓ Maps to LCC class hierarchy (primary grounding)
3. ✓ Primary source evidence (not just authority headings)
4. ✓ Parent exists & has authority alignment
5. ✓ Temporal bounds verifiable from sources
6. ✓ confidence >= 0.85 (higher threshold due to no Wikidata)

**Examples:**
- Hyper-specific administrative units: "Roman Military District γ, Province of Egypt (50-70 CE)"
- Archaic institutions: "Athenian Board of Hellenotamiae (mid-5th century BCE)"

**Why This Matters:**
- LCC class hierarchies contain granular concepts predating Wikidata
- LCSH authority records document historical concepts no longer well-known
- Enables discovery of "lost" or specialized concepts not covered by modern Wikidata

**Research Process:**
```python
concept = api.claim_new_concept(
    label="Egyptian Military District γ, Roman Period",
    parent_id="subj_roman_egypt_...",  # Must exist
    wikidata_qid=None,  # Not in Wikidata
    lcc_codes=["DS112.5.A45"],  # Authority grounding
    lcsh_ids=["sh85137609"],  # LCSH also aligns
    confidence=0.88,
    evidence="Papyri records (P. Oxy. 2103), Strabo Geography",
    source="LCC-LCSH authority mapping"
)
```

---

### **TIER 4: Pure Discovery (Lower Confidence, Restricted)**
**Criteria**: NOT in Wikidata, NOT in authority standards, but grounded in research

⚠️ **CONDITIONAL APPROVAL** - Only if all conditions met:
1. ✗ NOT in Wikidata
2. ✗ NOT in LCC/LCSH/FAST (no authority grounding)
3. ✓ Primary source evidence REQUIRED (manuscripts, coins, inscriptions)
4. ✓ Parent exists & is well-established
5. ✓ Temporal bounds rigorously verifiable
6. ✓ confidence >= 0.88 (very high due to no external validation)
7. ✓ Documented by ≥2 independent scholarly sources
8. ✓ NOT discoverable from other authorities later (verified by registry curator)

**Restrictions:**
- REQUIRES curator pre-approval (NOT auto_approved even at high confidence)
- Can only be created as child of CANONICAL parent (not another T4 concept)
- Max 5% of all concepts can be T4 (governance limit)

**Examples:**
- Rare archaeological findings: "Bronze coin hoard, Type Λ-variant, Uncertain mint, 145-140 BCE"
- Ephemeral administrative units: "Temporary Roman military garrison at Portus Namnetum, 55 BCE"

**Agent Action:**
```python
concept = api.claim_new_concept(
    label="Bronze Hoard Type Λ-variant, Uncertain Mint",
    parent_id="subj_roman_coinage",  # Must be canonical
    wikidata_qid=None,
    lcc_codes=[],  # No authority
    lcsh_ids=[],
    confidence=0.90,
    evidence=[
        "Crawford RRC Catalog entry 545/variant",
        "Jones, Roman Numismatics (2020)",
        "Coin Conservation Report NHM-2019-847"
    ],
    validation_status="pending_review",  # FORCED to pending
    agent_name="ArchaeologyAgent_v2"
)
# Even with confidence 0.90, forced to pending_review
# Curator must manually review within 48 hours
```

---

## 3. Authority Search Algorithm

**Before proposing ANY concept**, agent MUST search authorities:

```python
def search_authorities(label: str, 
                       wikidata_qid: str = None,
                       period_start: int = None) -> Dict:
    """
    Search LCC, LCSH, FAST for candidate alignments
    Returns: {tier: int, authorities: [...], confidence: float}
    """
    
    results = {
        "wikidata": wikidata_qid if wikidata_qid else None,
        "lcc_codes": [],
        "lcsh_ids": [],
        "fast_ids": [],
        "tier": None
    }
    
    # Step 1: Search LCSH by heading
    lcsh_matches = search_lcsh(label)  # Fuzzy match, normalized
    if lcsh_matches:
        results["lcsh_ids"] = [m["lcsh_id"] for m in lcsh_matches]
        results["lcsh_confidence"] = lcsh_matches[0]["match_confidence"]
    
    # Step 2: Search LCC by classification range
    if period_start:
        lcc_matches = search_lcc_by_period(label, period_start)
        if lcc_matches:
            results["lcc_codes"] = [m["code"] for m in lcc_matches]
            results["lcc_confidence"] = lcc_matches[0]["match_confidence"]
    
    # Step 3: Search FAST
    fast_matches = search_fast(label)
    if fast_matches:
        results["fast_ids"] = [m["fast_id"] for m in fast_matches]
        results["fast_confidence"] = fast_matches[0]["match_confidence"]
    
    # Step 4: Determine tier
    if wikidata_qid and (results["lcc_codes"] or results["lcsh_ids"] or results["fast_ids"]):
        results["tier"] = 1  # Wikidata + Authority
    elif wikidata_qid:
        results["tier"] = 2  # Wikidata only
    elif results["lcc_codes"]:
        results["tier"] = 3  # LCC-grounded
    else:
        results["tier"] = 4  # Pure discovery
    
    return results

# Usage in agent:
authority_search = search_authorities(
    label="Battle of Cannae",
    wikidata_qid=None,  # Lookup will find it
    period_start=-216
)

if authority_search["tier"] >= 3:
    # Tier 3-4: safe to create
    concept = api.claim_new_concept(...)
else:
    # Tier < 3: Cannot create
    print("Concept not grounded in authority standards")
```

---

## 4. Ecosystem Artifacts & Validation

### **Chrystallum Artifacts (Our Standards)**

**Required to Create New Concept:**
1. ✓ Parent in SubjectConceptRegistry (hierarchy integrity)
2. ✓ Evidence from Chrystallum CIDOCrm reference nodes (if applicable)
3. ✓ Facet-to-concept coherence (facet inference from claims)
4. ✓ Temporal bounds validated against Year nodes in Neo4j
5. ✓ Authority codes (if T1-T3) match our authority mapping tables

**Example Validation:**
```python
# Agent creates concept "Roman Legion, III Augusta"
concept_validation = {
    "parent_exists": True,  # ✓ "Roman Military Units" exists
    "wikidata_linked": "Q123456",
    "cidoc_applicable": True,  # ✓ Uses E14 Organization
    "facet_coherent": True,  # Military facet + temporal period align
    "temporal_valid": True,  # Period -27 to 400 reasonable for III Augusta
    "authority_aligned": ["LCC:PS3", "LCSH:sh85114472"]
}
```

---

## 5. Rejection Criteria

❌ **REJECT** concept proposal if:

| Reason | Tier | Action |
|--------|------|--------|
| No parent concept | 1-4 | Reject: "Parent concept not found" |
| confidence < 0.75 | 1-4 | Reject: "Confidence below minimum (0.75)" |
| No primary source evidence | 1-4 | Reject: "Unsourced concept" |
| Parent not canonical | 4 | Reject: "TIER 4 can only have canonical parent" |
| Temporal unverifiable | 1-4 | Reject: "Period bounds not verifiable from evidence" |
| Registry duplicate exists | 1-4 | Warn: "Concept exists" (return existing) |
| Authority conflict | 1-3 | Warn: "Authority sources conflict (manual review needed)" |
| Multiple authority mappings | 1-3 | Warn: "Concept maps to multiple authority concepts (clarify before approving)" |

---

## 6. Practical Examples

### ✅ APPROVE - Tier 1 (Wikidata + Authority)
```
Agent: "I found Battle of Cannae (Q181098)"
Criteria Check:
  ✓ Parent exists: Punic Wars (Q3105)
  ✓ Wikidata: Q181098
  ✓ LCC: DG262
  ✓ LCSH: sh85010755
  ✓ Evidence: "Livy, Polybius describe battle tactics"
  ✓ Period: -216 (verifiable)
  ✓ Confidence: 0.95
→ AUTO-APPROVED (confidence >= 0.90)
```

### ✅ APPROVE - Tier 2 (Wikidata Only)
```
Agent: "I found Emperor Pertinax (Q1391)"
Criteria Check:
  ✓ Parent exists: Roman Emperors
  ✓ Wikidata: Q1391
  ✗ LCC: Not yet mapped
  ✗ LCSH: Not yet mapped
  ✓ Evidence: "Historical record, coins"
  ✓ Period: 193 CE (verifiable)
  ✓ Confidence: 0.88
→ PENDING REVIEW (authority mapping deferred to Phase 3)
```

### ✅ APPROVE - Tier 3 (LCC-Grounded)
```
Agent: "Found Egyptian administrative district in LCC DS112.5"
Criteria Check:
  ✓ Parent exists: Egypt, Roman Period
  ✗ Wikidata: None
  ✓ LCC: DS112.5.A45
  ✓ LCSH: sh85137609
  ✓ Evidence: "Papyri records, Strabo"
  ✓ Period: 50-70 CE (from papyri dates)
  ✓ Confidence: 0.88 (no Wikidata = higher bar)
→ AUTO-APPROVED (LCC-grounded)
```

### ❌ REJECT - Tier 4 (No Authorities, High Risk)
```
Agent: "Found rare coin variant, not in any authority"
Criteria Check:
  ✓ Parent exists: Roman Coinage
  ✗ Wikidata: None
  ✗ LCC: None
  ✗ LCSH: None
  ✓ Evidence: "Coin conservation report, Crawford RRC"
  ✓ Period: 145-140 BCE
  ✓ Confidence: 0.90
  But: 2+ sources required, max 5% budget
→ REJECT (T4 exceeds governance limit, OR force pending_review)
```

### ❌ REJECT - Authority Mismatch
```
Agent: "Creating 'Caesar the Time Traveler' concept"
Criteria Check:
  ✓ Parent exists: Caesar
  ✗ Wikidata: None (doesn't make sense)
  ✗ LCC: None (not historical)
  ✗ LCSH: None
  ✓ Evidence: "Science fiction novel"
  ✗ Temporal: -100 BCE... 2025 CE (impossible)
→ REJECT (temporal unverifiable, not historical)
```

---

## 7. Governance Rules

### **Decision Matrix**

|  | Wikidata | Authority | Confidence | Temporal | Evidence | → Tier | → Status |
|---|----------|-----------|-----------|----------|----------|--------|----------|
| ✓ | ✓ | ✓1+ | ≥0.80 | Verifiable | Primary | 1 | Auto-Approve* |
| ✓ | ✓ | ✗ | ≥0.82 | Verifiable | Primary | 2 | Pending Review |
| ✗ | ✓ | ✓1+ | ≥0.85 | Verifiable | Primary | 3 | Auto-Approve* |
| ✗ | ✗ | ✓1+ | ≥0.88 | Verifiable | Primary | 3 | Auto-Approve* |
| ✗ | ✗ | ✗ | ≥0.90 | Verifiable | Primary×2 | 4 | Pending Review* |

**Legend:**
- `*` Auto-approve if confidence ≥0.90
- Pending review if 0.75 ≤ confidence < 0.90
- Reject if confidence < 0.75
- **× = Source count requirement**

### **Curator Review SLA**
- **Tier 1-3**: Auto-approved concepts reviewed weekly (spot-check)
- **Tier 2 Pending**: Reviewed within 24 hours
- **Tier 4 Pending**: Reviewed within 48 hours (high scrutiny)

---

## 8. Summary: When Agent Should Create New Concept

**YES, create if:**
1. Parent concept already exists ✓
2. Concept is in **at least one canonical standard** (Wikidata, LCC, LCSH, FAST) ✓
3. Primary source evidence provided ✓
4. Temporal bounds verifiable ✓
5. Confidence ≥ 0.75 ✓

**NO, don't create if:**
1. Parent doesn't exist ✗
2. No canonical grounding ✗
3. Unsourced ✗
4. Temporal ambiguous ✗
5. Confidence < 0.75 ✗

**DEFERRED (Curator Review):**
- Tier 2 without authority mapping (Wikidata-only)
- Tier 4 pure discovery (low statistical prevalence)

