# Appendix W: ADR 004 Canonical 18 Facet System

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Source:** Extracted from Consolidated Architecture Document

---

## Navigation

**Main Architecture:**
- [ARCHITECTURE_CORE.md](../../ARCHITECTURE_CORE.md)
- [ARCHITECTURE_ONTOLOGY.md](../../ARCHITECTURE_ONTOLOGY.md)
- [ARCHITECTURE_IMPLEMENTATION.md](../../ARCHITECTURE_IMPLEMENTATION.md)
- [ARCHITECTURE_GOVERNANCE.md](../../ARCHITECTURE_GOVERNANCE.md)

**Appendices Index:** [README.md](../README.md)

---

# **Appendix W: Facet Taxonomy Canonicalization (ADR-004)**

## **ADR-004: Canonical 18-Facet System with Enforcement**

**Status:** ACCEPTED (2026-02-16, resolves Architecture Review Issue #5)  
**Deciders:** Architecture Review  
**Date:** 2026-02-16

---

### **Context and Problem Statement**

Facet taxonomy was internally inconsistent:
- Document referenced "Biographic facet" in multiple places (e.g., Section 1.2, Section 3.3 notes)
- Official 17-facet list (Section 3.3, Appendix Q.3) did NOT include "BIOGRAPHIC"
- "BIOGRAPHIC" was treated as an invalid facet that LLM classifications would return and then get rejected
- Two different facet lists existed in various sections (18 vs 17, with items added/removed inconsistently)
- Facet validation was "by convention" (checking against list), not programmatically enforced

**Impact:**
- Ambiguity about whether Biographic is a valid facet (it should be - it's referenced throughout)
- LLM classifications returning "BIOGRAPHIC" would be rejected as invalid
- Graph nodes could contain invalid facet values without database constraints
- Pydantic validation incomplete (enum didn't include BIOGRAPHIC)

---

### **Decision**

**We adopt Canonical 18-Facet System with runtime validation enforcement.**

**Canonical Facets (UPPERCASE):**
```
ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, 
ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, 
POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL, COMMUNICATION
```

**Enforcement Rules (REQUIRED):**
1. `facet_registry_master.json` is single source of truth (18 facets, all UPPERCASE)
2. Pydantic FacetKey enum reflects registry exactly (no manual list maintenance)
3. Neo4j constraints reject facet values not in registry
4. All LLM classification outputs normalized to UPPERCASE before validation

---

### **BIOGRAPHIC Facet Definition**

**Key:** `BIOGRAPHIC`  
**Label:** Biographic  
**Definition:** Personal history, biography, life events, office-holding careers, genealogy  
**Use Cases:**
- Character development across historical periods
- Genealogical relationships (patronymic patterns, adoption, legitimacy)
- Career progression (military rank advancement, political offices, religious positions)
- Personal relationships (marriage, mentorship, rivalry)
- Life milestones (birth, education, death, succession)

**Wikidata Anchors:**
- Q5 (human)
- Q101352 (biography)
- Q11019 (family)
- Q4164871 (position / office)

**Related Relationships:**
- `MEMBER_OF_GENS` (Roman clan -specific genealogy)
- `FATHER_OF`, `MOTHER_OF`, `PARENT_OF` (gender-specific family ties)
- `APPOINTED_TO`, `HELD_OFFICE`, `SUCCESSOR_TO` (career progression)
- `BORN_IN`, `DIED_IN`, `LIVED_IN` (biographical geography)

---

### **Rationale**

**Why Include BIOGRAPHIC?**

1. **Already Implemented in Practice**
   - Section 1.2 references "Biographic facet"
   - Relationships registry contains 32 familial relationships (primarily biographic)
   - Office-holding modeled in Human node property `career_sequence`
   - Multiple SFAs need access to biography (Political SFA for succession, Military SFA for promotions)

2. **Distinct Analytical Dimension**
   - Not subsumed by Political/Military/Religious (office-holding has distinct queries)
   - Genealogy (patrilineal/matrilineal) different from political alliances
   - Personal biography distinct from institutional history

3. **Enables Targeted Analysis**
   - Query: "All Roman senators and their family networks" (BIOGRAPHIC focus)
   - Query: "Career progression from military to political office" (BIOGRAPHIC focus)
   - Query: "Succession disputes by genealogical proximity" (BIOGRAPHIC focus)

4. **Consistency with Architecture**
   - Documentation mentions it repeatedly → include it officially
   - LLM agents should return BIOGRAPHIC for biographical claims → make it valid
   - Genealogical relationships are first-class citizens → deserve facet-level organization

---

### **Consequences**

**Positive:**
- ✅ Eliminates existing inconsistency (17 vs 18, Biographic reference vs absence)
- ✅ LLM classification "BIOGRAPHIC" no longer rejected as invalid
- ✅ Clear signal: genealogy and personal history are key analytical dimensions
- ✅ Enables BiographicFacetAgent with targeted ontology for family/successor relationships
- ✅ Facet system now self-consistent and documented

**Negative:**
- ⚠️ One additional facet-specialist agent to manage (17 → 18 agents in SFA roster)
- ⚠️ Slightly more complex facet classification (LLM needs to distinguish BIOGRAPHIC from SOCIAL, CULTURAL)

**Neutral:**
- 🔄 No breaking changes to existing Neo4j data (new facet value available for future nodes)
- 🔄 Existing nodes without BIOGRAPHIC classification remain valid

---

### **Implementation Requirements**

**1. Canonical Registry Update (COMPLETED)**
- ✅ `facets_registry_master.json` updated: 18 facets, includes BIOGRAPHIC with anchors
- ✅ Version bumped to `"2026-02-16-biographic-added"`

**2. Architecture Documentation Update (COMPLETED)**
- ✅ Section 3.3: Lists 18 facets including BIOGRAPHIC
- ✅ Appendix Q.3: Canonical list reflects 18 facets
- ✅ All references to "17 facets" updated to "18 facets"
- ✅ All references to "17 SFAs" updated to "18 SFAs"

**3. Pydantic Enforcement (REQUIRED)**
```python
class FacetKey(str, Enum):
    """Canonical facet keys - UPPERCASE only (18 facets)."""
    ARCHAEOLOGICAL = "ARCHAEOLOGICAL"
    ARTISTIC = "ARTISTIC"
    BIOGRAPHIC = "BIOGRAPHIC"
    CULTURAL = "CULTURAL"
    DEMOGRAPHIC = "DEMOGRAPHIC"
    DIPLOMATIC = "DIPLOMATIC"
    ECONOMIC = "ECONOMIC"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    GEOGRAPHIC = "GEOGRAPHIC"
    INTELLECTUAL = "INTELLECTUAL"
    LINGUISTIC = "LINGUISTIC"
    MILITARY = "MILITARY"
    POLITICAL = "POLITICAL"
    RELIGIOUS = "RELIGIOUS"
    SCIENTIFIC = "SCIENTIFIC"
    SOCIAL = "SOCIAL"
    TECHNOLOGICAL = "TECHNOLOGICAL"
    COMMUNICATION = "COMMUNICATION"

class SubjectConcept(BaseModel):
    label: str
    facet: FacetKey  # Only valid 18 facets accepted
    # ... other fields
```

**4. Neo4j Constraint (RECOMMENDED)**
```cypher
// Enforce facet values at DB level
CREATE CONSTRAINT facet_valid_values IF NOT EXISTS
FOR (n:SubjectConcept)
REQUIRE n.facet IN [
  "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "CULTURAL",
  "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC", "ENVIRONMENTAL",
  "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC", "MILITARY",
  "POLITICAL", "RELIGIOUS", "SCIENTIFIC", "SOCIAL",
  "TECHNOLOGICAL", "COMMUNICATION"
];
```

**5. LLM Prompt Update (REQUIRED)**
```python
FACET_CLASSIFICATION_PROMPT = """
Classify the claim across these 18 research dimensions:
ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, CULTURAL, DEMOGRAPHIC, DIPLOMATIC,
ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY,
POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL, COMMUNICATION

Focus on PRIMARY dimensions only. BIOGRAPHIC applies to personal history,
genealogy, careers, life events - distinct from SOCIAL (class/family structures).
"""
```

---

### **Migration Path**

For existing graphs with 17-facet systems:
1. No breaking changes (existing facet values remain valid)
2. New claims can use BIOGRAPHIC facet
3. Optional: Reprocess historical claims with updated classifier to assign BIOGRAPHIC where applicable

---

### **Related Decisions**

- **ADR-001** (Appendix U): Content-Only Cipher - facet_id IS included in cipher (facet-aware deduplication)
- **ADR-002** (Appendix V): Relationship Kernel - 32 familial relationships map to BIOGRAPHIC facet primarily
- **ADR-005** (Appendix X): Federated Claims Signing - signed faceted claims enable institutional trust
- **Section 3.3**: Facet architecture (updated to 18 facets)
- **Appendix Q.3**: Canonical facet registry with UPPERCASE enforcement

---

### **References**

- `Facets/facet_registry_master.json` - Canonical registry (18 facets, includes BIOGRAPHIC)
- `Facets/facet_registry_master.csv` - Tabular export
- Section 3.3 (Facets Entity Classification)
- Appendix Q.3 (Canonical Facets)
- Architecture Review 2026-02-16, Issue #5: "Facet taxonomy inconsistent"

---

**(End of Appendix W - ADR-004: Facet Taxonomy Canonicalization)**

---

