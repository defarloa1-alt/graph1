# Roman Republic Ontology Proposal - Review & Corrections

**Date:** 2026-02-19  
**Anchor QID:** Q17167 (Roman Republic)  
**Agent:** SCA (Subject Concept Agent)  
**Status:** EXCELLENT - Needs facet alignment corrections

---

## 📊 **Overall Assessment**

**Grade: A- (Excellent structure, needs canonical facet alignment)**

**Strengths:**
- ✅ Comprehensive 3-tier hierarchy (Root → L2 → L3)
- ✅ 10 major branches with logical subdivisions
- ✅ Clear facet assignments per concept
- ✅ 12 SFA agents proposed with split criteria
- ✅ 5 macro groups for agent coordination
- ✅ Cross-links identified (RELATED_TO relationships)
- ✅ Discipline anchors for academic routing
- ✅ Clear handoff instructions for SFAs

---

## ⚠️ **Critical Issues Requiring Fix**

### **Issue 1: Non-Canonical Facets Used**

**Canonical Source:** `Facets/facet_registry_master.json` (18 facets)

**Problems in Proposal:**

| Proposal Facet | Status | Fix |
|----------------|--------|-----|
| `genealogical` | ❌ NOT canonical | Change to `BIOGRAPHIC` |
| `patronage` | ❌ NOT canonical | Merge into `SOCIAL` or `POLITICAL` |
| `spatial` | ❌ Wrong name | Change to `GEOGRAPHIC` |
| `political` | ⚠️ Lowercase | Change to `POLITICAL` |
| `military` | ⚠️ Lowercase | Change to `MILITARY` |
| All others | ⚠️ Lowercase | Change to UPPERCASE |

**Canonical 18 Facets (Uppercase):**
```
ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION, CULTURAL,
DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC,
INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS,
SCIENTIFIC, SOCIAL, TECHNOLOGICAL
```

**Reference:** `Facets/facet_registry_master.json`

---

### **Issue 2: Facet Key Casing**

**From ADR-004 (Architecture Decision Record):**
> All facet keys MUST be UPPERCASE to prevent case-collision bugs in queries.

**Current proposal:**
```json
"primary_facet": "political",  ← Wrong
"related_facets": ["military", "social"]  ← Wrong
```

**Must be:**
```json
"primary_facet": "POLITICAL",  ← Correct
"related_facets": ["MILITARY", "SOCIAL"]  ← Correct
```

**Why:** Pydantic validation, Neo4j constraints, query consistency

---

### **Issue 3: Missing Canonical Facets**

**Not included in proposal:**
- ARCHAEOLOGICAL (material culture, excavation sites)
- ARTISTIC (art, architecture, aesthetics)
- ENVIRONMENTAL (climate, geography, natural resources)
- LINGUISTIC (Latin language, scripts)
- SCIENTIFIC (natural philosophy, astronomy)
- TECHNOLOGICAL (mentioned once but not developed)

**Should these be added?**
- Roman Republic had significant engineering (TECHNOLOGICAL)
- Archaeological evidence is critical (ARCHAEOLOGICAL)
- Latin language development (LINGUISTIC)

**Recommendation:** Add branches for these or document why excluded

---

## ✅ **Corrected Examples**

### **Example 1: Biographic (was "genealogical")**

**BEFORE:**
```json
{
  "concept_id": "subj_rr_social_family_gentes",
  "label": "Families, Gentes, and Prosopography",
  "primary_facet": "genealogical",  ← Non-canonical
  "related_facets": ["social", "political", "patronage", "demographic"]  ← Lowercase
}
```

**AFTER:**
```json
{
  "concept_id": "subj_rr_biographic_prosopography",
  "label": "Families, Gentes, and Prosopography",
  "primary_facet": "BIOGRAPHIC",  ← Canonical + uppercase
  "related_facets": ["SOCIAL", "POLITICAL", "DEMOGRAPHIC"]  ← Uppercase + removed "patronage"
}
```

---

### **Example 2: Geographic (was "spatial")**

**BEFORE:**
```json
{
  "concept_id": "subj_rr_spatial_geography_expansion",
  "label": "Geography, Provinces, and Expansion",
  "primary_facet": "spatial",  ← Wrong name
  "related_facets": ["political", "military", "economic", "temporal"]
}
```

**AFTER:**
```json
{
  "concept_id": "subj_rr_geographic_provinces_expansion",
  "label": "Geography, Provinces, and Expansion",
  "primary_facet": "GEOGRAPHIC",  ← Canonical + uppercase
  "related_facets": ["POLITICAL", "MILITARY", "ECONOMIC"]  ← Uppercase
}
```

---

### **Example 3: Patronage Merged into Social**

**BEFORE:**
```json
{
  "concept_id": "subj_rr_social_patronage_networks",
  "label": "Patronage, Clientage, and Elite Networks",
  "primary_facet": "patronage",  ← Non-canonical
  "related_facets": ["social", "political", "communication"]
}
```

**AFTER:**
```json
{
  "concept_id": "subj_rr_social_patronage_networks",
  "label": "Patronage, Clientage, and Elite Networks",
  "primary_facet": "SOCIAL",  ← Canonical (patronage is a social structure)
  "related_facets": ["POLITICAL", "BIOGRAPHIC", "COMMUNICATION"]  ← Uppercase
}
```

---

## 🔧 **Corrections Needed**

### **Global Changes:**

**1. Facet Name Mappings:**
```
genealogical → BIOGRAPHIC
patronage → SOCIAL (or POLITICAL depending on context)
spatial → GEOGRAPHIC
organizational → POLITICAL (or merge into primary facets)
classification → Remove (not a facet, it's a meta-concern)
```

**2. Uppercase All Facets:**
```python
# Search and replace in proposal
"political" → "POLITICAL"
"military" → "MILITARY"
"social" → "SOCIAL"
"economic" → "ECONOMIC"
"diplomatic" → "DIPLOMATIC"
"cultural" → "CULTURAL"
"religious" → "RELIGIOUS"
"intellectual" → "INTELLECTUAL"
"communication" → "COMMUNICATION"
"geographic" → "GEOGRAPHIC"
"temporal" → Remove or document (temporal is backbone, not facet)
```

**3. Add Missing Canonical Facets:**
```json
// Add these branches
{
  "concept_id": "subj_rr_technological_engineering",
  "label": "Engineering, Aqueducts, Roads, Military Tech",
  "primary_facet": "TECHNOLOGICAL",
  "related_facets": ["MILITARY", "ECONOMIC", "GEOGRAPHIC"]
},
{
  "concept_id": "subj_rr_archaeological_material_evidence",
  "label": "Material Culture and Archaeological Evidence",
  "primary_facet": "ARCHAEOLOGICAL",
  "related_facets": ["CULTURAL", "TECHNOLOGICAL", "ECONOMIC"]
},
{
  "concept_id": "subj_rr_linguistic_latin_development",
  "label": "Latin Language and Inscriptions",
  "primary_facet": "LINGUISTIC",
  "related_facets": ["CULTURAL", "COMMUNICATION"]
}
```

---

## 📐 **Architectural Validation**

### **Check Against Canonical Sources:**

**File:** `Facets/facet_registry_master.json`

**Validation Script:**
```python
import json

# Load canonical facets
with open('Facets/facet_registry_master.json') as f:
    canonical = json.load(f)
    canonical_keys = {f['key'].upper() for f in canonical['facets']}

print("Canonical 18 facets:")
for key in sorted(canonical_keys):
    print(f"  {key}")

# Load your proposal
with open('proposal.json') as f:
    proposal = json.load(f)
    proposal_facets = set(proposal['facet_registry']['facets'])

# Find mismatches
not_canonical = proposal_facets - canonical_keys
missing = canonical_keys - proposal_facets

print(f"\nNon-canonical in proposal: {not_canonical}")
print(f"Missing from proposal: {missing}")
```

---

## ✅ **What's Already Correct**

### **Excellent Design Decisions:**

**1. Hierarchy Structure:**
```json
"hierarchy_relationship": "PART_OF"  ← Correct
"cross_links_relationship": "RELATED_TO"  ← Correct
```

**2. Agent Splitting Logic:**
```json
"splitting_rule": "Only split when subject becomes too large for one SFA"  ← Smart
"default_depth_target": 2  ← Reasonable
"max_depth_without_split": 3  ← Good limit
```

**3. Macro Groups:**
- Power/Conflict/Statecraft
- Society/Meaning
- Material/Systems
- Indexing/Controls
- People/Kinship

**These are well-designed clustering strategies!**

**4. Cross-Links:**
All 5 RELATED_TO proposals are valid:
- ✅ Political factions ↔ Military wars
- ✅ Patronage ↔ Political institutions
- ✅ Taxation ↔ Provincial administration
- ✅ Oratory ↔ Political conflict
- ✅ Religious offices ↔ Political offices

---

## 🎯 **Corrected Facet Registry Section**

**Replace this section in your proposal:**

```json
"facet_registry": {
  "facets": [
    "ARCHAEOLOGICAL",
    "ARTISTIC",
    "BIOGRAPHIC",
    "COMMUNICATION",
    "CULTURAL",
    "DEMOGRAPHIC",
    "DIPLOMATIC",
    "ECONOMIC",
    "ENVIRONMENTAL",
    "GEOGRAPHIC",
    "INTELLECTUAL",
    "LINGUISTIC",
    "MILITARY",
    "POLITICAL",
    "RELIGIOUS",
    "SCIENTIFIC",
    "SOCIAL",
    "TECHNOLOGICAL"
  ],
  "note": "All 18 canonical facets from Facets/facet_registry_master.json",
  "enforcement": "UPPERCASE keys required per ADR-004"
}
```

---

## 📋 **Approval Checklist**

Before loading to Neo4j:

- [ ] All facets match canonical 18
- [ ] All facet keys are UPPERCASE
- [ ] No "genealogical" facet (use BIOGRAPHIC)
- [ ] No "patronage" facet (merge into SOCIAL/POLITICAL)
- [ ] "spatial" changed to "GEOGRAPHIC"
- [ ] Missing facets added or exclusion documented
- [ ] Cross-validated with `Facets/facet_registry_master.json`
- [ ] Agent IDs updated to use canonical facets

**Then:** ✅ APPROVE and load to Neo4j

---

## 🚀 **Next Steps**

### **Step 1: Generate Corrected Proposal**
- Apply facet name corrections
- Uppercase all facet values
- Add missing facet branches
- Validate against canonical registry

### **Step 2: Load to Neo4j**
```cypher
// Create root SubjectConcept
CREATE (root:SubjectConcept {
  concept_id: 'subj_roman_republic_q17167',
  qid: 'Q17167',
  label: 'Roman Republic',
  primary_facet: 'POLITICAL',
  status: 'approved'
})

// Create L2 branches
CREATE (pol:SubjectConcept {
  concept_id: 'subj_rr_political_state_governance',
  label: 'Government, Constitution, and Governance',
  primary_facet: 'POLITICAL'
})
CREATE (pol)-[:PART_OF]->(root)

// ... repeat for all branches
```

### **Step 3: Instantiate SFAs**
- Use corrected agent mapping
- Spawn 10 minimum viable SFAs
- Assign concept_ids to each SFA

---

## 📝 **Summary**

**Your ontology proposal is EXCELLENT** - just needs:
1. Facet alignment with canonical 18
2. Uppercase facet keys
3. Add missing facets

**Once fixed:** Ready to load to Neo4j and spawn SFAs!

**Want me to generate the corrected JSON proposal for you?**

---

**Saved to:** `md/Agents/SCA/ROMAN_REPUBLIC_ONTOLOGY_PROPOSAL_REVIEW_2026-02-19.md`

