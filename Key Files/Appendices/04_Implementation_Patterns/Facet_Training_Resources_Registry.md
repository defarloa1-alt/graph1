# Appendix O: Facet Training Resources Registry

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

# **Appendix O: Facet Training Resources Registry**

## **O.1 Purpose**

Defines curated discipline-specific resources for **SubjectFacetAgent (SFA) training initialization**. These resources serve as **discipline roots** for building SubjectConcept hierarchies via BROADER_THAN relationships.

**Integration Point:** Step 5 Discipline Root Detection uses Priority 1 resources to mark `discipline=true` flags in Neo4j.

## **O.2 Authority Schema**

Each resource includes:
- **name**: Human-readable resource title
- **role**: Resource function (discipline_reference, bibliographic_index, curated_portal, etc.)
- **priority**: 1 (Tier 1 discipline anchor) or 2 (Tier 2 methodological pattern)
- **access**: "open" (freely available) or "subscription" (institutional access)
- **url**: Direct link or gateway URL
- **notes**: Contextual guidance for SFA training bootstrap

## **O.3 Priority Tier System**

**Priority 1 (Tier 1 Discipline Anchors):**
- Standard discipline references (Stanford Encyclopedia, Oxford References)
- Comprehensive bibliographic indexes (Historical Abstracts, Linguistic Bibliography)
- Empirical data portals (Economic History Society datasets)
- **Action**: Create SubjectConcept nodes with `discipline=true` flag
- **Query Pattern**: `WHERE discipline=true AND facet=TARGET_FACET`

**Priority 2 (Tier 2 Methodological Patterns):**
- Curated secondary sources (Norwich Military History, Zinn Education Project)
- Pedagogical syllabi (Stanford OHS)
- Primary source methodology templates (Robin Bernstein model)
- **Action**: Use for narrative patterns and case study methodologies

## **O.4 Canonical 17 Facet Registry**

### POLITICAL
- **Tier 1**: Stanford Encyclopedia of Philosophy – Political Philosophy (open)
- **Tier 1**: Historical Abstracts (political history) (subscription)

### MILITARY
- **Tier 2**: Norwich University – Military History Websites (open)
- **Tier 1**: Historical Abstracts (military history) (subscription)

### ECONOMIC
- **Tier 1**: Economic History Society – Online Resources (open) — PRIMARY discipline portal
- **Tier 2**: VoxEU – Economic History & Macrohistory (open)

### CULTURAL
- **Tier 2**: Primary Sources in U.S. Cultural History – Robin Bernstein (open) — narrative template
- **Tier 1**: Historical Abstracts (cultural history) (subscription)

### RELIGIOUS
- **Tier 1**: Theology and Religion Online (Bloomsbury) (subscription)
- **Tier 1**: Oxford Reference – Religion/Theology (subscription)

### SOCIAL
- **Tier 1**: Economic History Society – labour/demography resources (open)
- **Tier 2**: Zinn Education Project – Teaching People's History (open)

### DEMOGRAPHIC
- **Tier 1**: Economic History Society – demographic datasets (open) — quantitative anchor

### INTELLECTUAL
- **Tier 1**: Stanford Encyclopedia of Philosophy – HPS & related (open)
- **Tier 2**: History & Philosophy of Science – Stanford OHS (open)

### SCIENTIFIC
- **Tier 1**: Stanford Encyclopedia of Philosophy – Science entries (open)

### TECHNOLOGICAL
- **Tier 1**: Economic History Society – industrialization/technology (open)
- **Tier 1**: Historical Abstracts (history of technology) (subscription)

### LINGUISTIC
- **Tier 1**: Library of Congress – Linguistics Electronic Resources (open)
- **Tier 1**: Linguistic Bibliography Online (subscription)

### GEOGRAPHIC
- **Tier 2**: LOC – Environmental History (maps & place framing) (open)

### ENVIRONMENTAL
- **Tier 2**: LOC – Environmental History Classroom Materials (open)
- **Tier 1**: Economic History Society – climate/resource-related (open)

### ARCHAEOLOGICAL
- **Tier 2**: Archaeology: Reference Materials – COD Library (open)
- **Tier 1**: Oxford Encyclopedia/Companion to Archaeology (subscription)

### DIPLOMATIC
- **Tier 1**: Historical Abstracts – diplomatic history (subscription)
- **Tier 2**: Norwich Military History guide (treaties/foreign policy) (open)

### ARTISTIC
- **Tier 1**: Oxford Art Online / Grove Art (subscription)
- **Tier 2**: Primary Sources in Cultural History – visual culture pattern (open)

### COMMUNICATION
- **Tier 2**: Zinn Education Project – rhetoric & narrative framing (open)
- **Tier 2**: Cultural/political primary-source portals (pattern) (open)

## **O.5 SFA Initialization Workflow**

**Step 1: Load Facet Resources**
```python
def load_facet_resources(facet: str) -> List[Dict]:
    """Load Priority 1 & 2 resources for target facet."""
    resources = parse_yaml("Facets/TrainingResources.yml")
    return resources[facet.upper()]
```

**Step 2: Seed Discipline Roots (Priority 1 only)**
```cypher
// Create discipline root SubjectConcepts
MERGE (sc:SubjectConcept {
  label: "Political Philosophy",  // from Stanford Encyclopedia
  facet: "POLITICAL",
  authority_id: "sh85104440",  // LCSH if available
  discipline: true  // DISCIPLINE FLAG
})
```

**Step 3: Query Discipline Roots for Training**
```cypher
// SFA initialization query
MATCH (root:SubjectConcept)
WHERE root.discipline = true 
  AND root.facet = "POLITICAL"
MATCH (root)-[:BROADER_THAN*]->(narrower:SubjectConcept)
RETURN root, narrower
```

**Step 4: Expand Hierarchy via BROADER_THAN**
- Use Wikidata P279 (subclass of) traversal
- Build BROADER_THAN edges from discipline roots downward
- Validate against LCSH/FAST authority hierarchies (Tier 1 authorities)

## **O.6 Authority Precedence Integration**

When enriching discipline roots with multi-authority metadata:

**Tier 1 Search (LCSH/FAST):**
```cypher
MATCH (root:SubjectConcept {discipline: true})
WHERE root.authority_id IS NULL
// Enrich with LCSH first, then FAST
CALL lcsh.lookup(root.label) YIELD authority_id, fast_id
SET root.authority_id = authority_id, root.fast_id = fast_id
```

**Tier 2 Fallback (LCC/CIP):**
```cypher
MATCH (root:SubjectConcept {discipline: true})
WHERE root.authority_id IS NULL AND root.fast_id IS NULL
// Fallback to LCC classification
CALL lcc.classify(root.label) YIELD lcc_code
SET root.backbone_lcc = lcc_code
```

**Tier 3 Fallback (Wikidata/Other):**
```cypher
MATCH (root:SubjectConcept {discipline: true})
WHERE root.authority_id IS NULL AND root.fast_id IS NULL
// Last resort: Wikidata QID lookup
CALL wikidata.search(root.label) YIELD qid
SET root.wikidata_qid = qid
```

## **O.7 Authoritative Source File**

- **File**: `Facets/TrainingResources.yml`
- **Version**: 2.0 (2026-02-16)
- **Maintenance**: Update when adding new facet training pipelines

## **O.8 Related Sections**

- **Step 5 Discipline Root Detection algorithm**
- **Appendix D**: Subject Facet Classification (17 canonical facets)
- **Section 4.4**: Multi-Authority Model (Tier 1/2/3 precedence)
- **Section 4.9**: Academic Discipline Model (discipline flag usage)

---

**(End of Appendix O)**

---

