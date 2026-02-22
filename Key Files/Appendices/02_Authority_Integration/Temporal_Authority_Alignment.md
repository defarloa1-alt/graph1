# Appendix E: Temporal Authority Alignment

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

# **Appendix E: Temporal Authority Alignment**

## **E.1 Scope**

Normative temporal modeling is in Section 3.4 and Section 4.3. This appendix is a reference index.

## **E.2 Authoritative Files**

- `Temporal/time_periods.csv`
- `Temporal/periodo-dataset.csv`
- `Temporal/period_classification_decisions.csv`
- `Temporal/PERIOD_CLASSIFICATION_PLAN.md`

## **E.3 Current Decision Snapshot**

From `Temporal/period_classification_decisions.csv` (`22` decisions):

- Tier 2 -> `convert_to_event`: `9`
- Tier 3 -> `delete`: `6`
- Tier 4 -> `delete`: `7`

## **E.4 Temporal Normalization Contract**

- Use ISO 8601 canonical storage (`-0049-01-01` for BCE).
- Preserve source-original date text and calendar system metadata.
- Separate historiographic periods from short event phases.

---

**(End of Appendix E)**

---

# **Appendix F: Geographic Authority Integration**

## **F.1 Scope**

Normative geographic federation logic is in Section 4.4. This appendix is the source and ingestion reference.

## **F.2 Authoritative Files**

- Raw authority snapshots: `Geographic/*.out`
- Curated registry: `Geographic/geographic_registry_master.csv`
- RDF references: `Geographic/ontology.rdf`, `Geographic/tgn_7011179-place.rdf`
- Consolidation note: `Geographic/GEOGRAPHIC_CONSOLIDATION_2026-02-12.md`

## **F.3 Curated Registry Snapshot**

From `Geographic/geographic_registry_master.csv`:

- Rows: `20`
- Facet assignments observed:
- `cultural_geographic`: 8
- `pure_spatial`: 3
- `political`: 2
- unassigned/blank: 7

## **F.4 Ingestion Rules**

1. Use authority place IDs (TGN/Pleiades/GeoNames) as atomic identifiers.
2. Keep historical names and modern names as separate properties.
3. Preserve hierarchy and containment relations independently of political regime naming.
4. Do not collapse culturally-defined regions into purely geometric regions.

---

**(End of Appendix F)**

---

# **Appendix G: Legacy Implementation Patterns**

## **G.1 Purpose**

Documents deprecated patterns to prevent accidental reintroduction.

## **G.2 Deprecated vs Current**

| Legacy Pattern | Problem | Current Pattern |
|---|---|---|
| Flat subject tagging without facets | No multidimensional analysis | Star-pattern facets with per-facet confidence |
| Treating short crises as periods | Temporal ambiguity | Period/Event distinction with classification workflow |
| Identifier handling through LLM prompts | Tokenization breakage | Two-stage: LLM labels -> tool ID resolution |
| Ad hoc relationship labels | Query fragmentation | Registry-first relationship governance |

## **G.3 Migration Note**

All new implementations should follow Sections 3-8 plus appendices A, B, D, and M.

---

**(End of Appendix G)**

---

# **Appendix H: Architectural Decision Records**

## **H.1 ADR Index**

| ADR | Title | Status | Primary Section |
|---|---|---|---|
| ADR-001 | Two-stage architecture (LLM extraction -> reasoning validation) | Adopted | 1.2.1 |
| ADR-002 | Structure vs topics separation (LCC vs FAST) | Adopted | 1.2.3 |
| ADR-003 | LCC as primary classification backbone | Adopted | 1.4.1 |
| ADR-004 | Two-level agent granularity (FAST + LCC) | Adopted | 1.4.2, 5.4 |
| ADR-005 | CIDOC-CRM foundation with Chrystallum extensions | Adopted | 1.2.4 |
| ADR-006 | Hybrid architecture: traversable entities + content-addressable claims | Adopted | 6.4 |
| ADR-007 | Calendar normalization for historical dates | Adopted | 1.4.3, 3.4 |

## **H.2 ADR-006 (Detailed)**

Decision:

- Entities remain traversal-first in Neo4j for exploratory graph analytics.
- Claims use content-addressable `cipher` identity for immutability, deduplication, and verification.

Why:

- Traversal and discovery are essential for entity-layer research questions.
- Claim verification and provenance integrity require immutable claim identity.

Consequence:

- Mixed architecture by design; each layer optimized for its function.

## **H.3 ADR-007 (Detailed)**

Decision:

- Store normalized canonical dates plus original source dates and calendar metadata.

Why:

- Prevent false contradiction from Julian/Gregorian mismatches.
- Preserve source fidelity while enabling deterministic timeline queries.

Consequence:

- Temporal ingestion requires normalization step before confidence scoring.

## **H.4 Primary ADR Sources**

- `md/Architecture/ONTOLOGY_PRINCIPLES.md`
- `md/Architecture/LCC_AGENT_ROUTING.md`
- `md/Architecture/Subject_Agent_Granularity_Strategy.md`
- `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md`
- `md/Architecture/Historical_Dating_Schema_Disambiguation.md`

---

**(End of Appendix H)**

---

# **Appendix I: Mathematical Formalization**

## **I.1 Confidence Components**

Source confidence:

```text
T_confidence = T_tier + delta_recency - delta_contradiction
```

Claim confidence (weighted by relevance):

```text
C_confidence = sum(T_confidence_i * relevance_i) / sum(relevance_i)
```

Facet enrichment score:

```text
FES = (facets_present / 16) * 100
```

## **I.2 Temporal Decay Function**

For time-sensitive claims:

```text
decay(t) = exp(-lambda * t)
```

Where:

- `t` = years since claim assertion or source timestamp
- `lambda` is domain-specific decay rate

## **I.3 Practical Bounds**

- Confidence values are bounded to `[0.0, 1.0]`.
- Contradiction penalties should never drive score below `0.0`.
- Use explicit null/unknown handling for missing components.

---

**(End of Appendix I)**

---

# **Appendix J: Implementation Examples**

## **J.1 Subject-Centric Retrieval**

```cypher
MATCH (s:SubjectConcept {fast_id: 'fst01204885'})<-[:HAS_SUBJECT_CONCEPT]-(e)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(c:Claim)
RETURN e.label AS entity, count(c) AS supporting_claims
ORDER BY supporting_claims DESC
LIMIT 50;
```

## **J.2 Claim Verification by Cipher**

```cypher
MATCH (c:Claim {cipher: $cipher})
OPTIONAL MATCH (c)<-[:REVIEWED]-(r:Review)
RETURN c.status, c.confidence, collect(r.verdict) AS verdicts;
```

## **J.3 Identifier-Safe Ingestion Skeleton**

```python
# Stage 1: LLM extracts natural-language labels
labels = extractor.extract(text)

# Stage 2: deterministic tools resolve identifiers
qid = wikidata.resolve(labels["entity_label"])
fast_id = fast.resolve(labels["subject_label"])

# Stage 3: persist both label and atomic IDs
record = {
    "label": labels["entity_label"],
    "qid": qid,
    "fast_id": fast_id,
}
```

## **J.4 Script Operations Reference**

- Script registry: `md/Reference/SCRIPT_REGISTRY_2026-02-13.md`
- Registry CSV: `md/Reference/SCRIPT_REGISTRY_2026-02-13.csv`

---

**(End of Appendix J)**

---

# **Appendix K: Wikidata Integration Patterns**

## **K.1 Scope**

Normative federation architecture is defined in Section 4.4 and Section 8.6. This appendix provides operational query patterns.

## **K.2 Authoritative Files**

- `md/Architecture/Wikidata_SPARQL_Patterns.md`
- `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`

## **K.3 Core SPARQL Patterns**

### Direct property bundle resolution

```sparql
SELECT ?lcsh ?fast ?lcc ?viaf ?tgn ?pleiades ?trismegistos WHERE {
  BIND(wd:Q1048 AS ?item)
  OPTIONAL { ?item wdt:P244  ?lcsh }
  OPTIONAL { ?item wdt:P2163 ?fast }
  OPTIONAL { ?item wdt:P1149 ?lcc }
  OPTIONAL { ?item wdt:P214  ?viaf }
  OPTIONAL { ?item wdt:P1667 ?tgn }
  OPTIONAL { ?item wdt:P1584 ?pleiades }
  OPTIONAL { ?item wdt:P1958 ?trismegistos }
}
```

### Backlink enrichment (reverse-link context expansion)

```sparql
SELECT ?source ?sourceLabel ?property ?propertyLabel WHERE {
  BIND(wd:Q1048 AS ?target)
  ?source ?property ?target .
  VALUES ?property { wdt:P710 wdt:P1441 wdt:P138 wdt:P112 }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 500
```

## **K.4 Pipeline Contract**

1. Resolve label -> QID.
2. Pull authority property bundle.
3. Optionally run backlink expansion for context discovery.
4. Classify results by source entity type (`P31`, bounded `P279`) and ingest with provenance.
5. Route every statement through the dispatcher (`datatype + value_type`).
6. Apply the temporal precision gate before temporal anchoring.
7. Apply the frontier eligibility guard before recursive expansion.
8. Quarantine unsupported or malformed statements with explicit reason.

## **K.5 Property Lookup Contract (Reference-Book Pattern)**

Chrystallum MUST NOT ingest the full Wikidata property universe as graph nodes for runtime reasoning.  
Use a tool-backed property catalog lookup pattern instead (local reference store + deterministic filtering).

### Authoritative lookup assets

- `Relationships/relationship_types_registry_master.csv` (approved canonical mappings first)
- `CSV/wikiPvalues.csv` (Wikidata property catalog)
- `scripts/tools/enrich_wikidata_properties_from_api.py` (optional metadata enrichment pass)
- `scripts/tools/generate_wikidata_property_candidates_from_catalog.py` (candidate generation)

### Required lookup sequence

1. Attempt exact canonical mapping from `relationship_types_registry_master.csv`.
2. If unmapped, query local property catalog (label + description + aliases).
3. Apply datatype gate before ranking candidates.
4. Rank candidates using label match + alias match + description overlap.
5. Auto-apply only if confidence threshold is met; otherwise emit review queue entry.

### Datatype gate (hard filter)

- Candidate datatype MUST be compatible with relationship semantics.
- Examples:
  - Person/group/place/event relations -> prefer `wikibase-item`
  - Date/time relations -> `time`
  - Numeric indicator relations -> `quantity`
  - Media/file relations -> `commonsMedia`
  - Identifier relations -> `external-id`

### Alias handling (`propertyAltLabels`)

- Parse `propertyAltLabels` as pipe-delimited (`|`), normalize casing/whitespace, de-duplicate.
- Score exact alias matches strongly (same as exact label-class signals).
- Use aliases only after datatype compatibility is satisfied.

### Safety rule

- No low-confidence property mappings may be written directly to canonical registry.
- Low-confidence results MUST be written to review backlog and human-approved first.
- Identifier handling constraints in Appendix M still apply (tool resolution only, no LLM free-form ID generation).

## **K.6 Dispatcher and Backlink Operations**

Canonical scripts:
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`

Canonical report location:
- `JSON/wikidata/backlinks/`

Required report fields (minimum):
- `route_counts`
- `quarantine_reasons`
- `unsupported_pair_rate`
- `unresolved_class_rate`
- `frontier_eligible`
- `frontier_excluded`

---

**(End of Appendix K)**

---

# **Appendix L: CIDOC-CRM Integration Guide**

## **L.1 Scope**

Defines triple alignment approach: Chrystallum relation type <-> Wikidata property <-> CIDOC-CRM property/class.

## **L.2 Authoritative Files**

- `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md`
- `md/Architecture/CIDOC-CRM_Alignment_Summary.md`
- `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`

## **L.3 High-Value Mappings**

| Chrystallum | Wikidata | CIDOC-CRM |
|---|---|---|
| `PARTICIPATED_IN` | `P710` | `P11_had_participant` |
| `LOCATED_IN` | `P131` | `P7_took_place_at` |
| `PART_OF` | n/a | `P86_falls_within` |
| `CAUSED` | `P828` | `P15_was_influenced_by` |
| `AUTHOR` | `P50` | `P14_carried_out_by` via `E12_Production` |

## **L.4 Entity Class Alignment**

| Chrystallum Node | CIDOC-CRM Class |
|---|---|
| Event | `E5_Event` |
| Human | `E21_Person` |
| Place | `E53_Place` |
| Organization | `E74_Group` / `E40_Legal_Body` |
| TimeSpan | `E52_Time-Span` |

## **L.5 Implementation Rule**

CIDOC-CRM alignment is additive. Chrystallum-specific capabilities (library backbones, action-structure vocabularies, identifier safety) remain first-class and are not dropped for standards compatibility.

---

**(End of Appendix L)**

---

# **Appendix M: Identifier Safety Reference**

## **M.1 Core Rule**

Never pass atomic identifiers to LLMs for interpretation.

Use two-stage processing:

1. LLM extracts natural language labels.
2. Deterministic tools resolve and validate identifiers.

## **M.2 Decision Table**

| Input Type | Example | LLM-safe | Handling |
|---|---|---|---|
| Natural-language label | `Roman Republic` | Yes | LLM extraction/classification |
| Wikidata QID | `Q17193` | No | Tool lookup only |
| FAST ID | `1145002` | No | Tool lookup only |
| LCC code | `DG241-269` | No | Tool lookup only |
| MARC authority ID | `sh85115058` | No | Tool lookup only |
| Pleiades ID | `423025` | No | Tool lookup only |
| ISO date with negative year | `-0509-01-01` | No | Store/format with temporal tool |

## **M.3 Authoritative References**

- `md/Reference/IDENTIFIER_ATOMICITY_AUDIT.md`
- `md/Reference/IDENTIFIER_CHEAT_SHEET.md`
- Section 8.5 in this architecture document

## **M.4 Pre-Prompt Validation Checklist**

Before any LLM call:

- remove QIDs and catalog IDs
- replace with human-readable labels
- keep numeric/scalar fields only when they are true numeric values
- run identifier validator where available

---

**(End of Appendix M)**

---

# **Appendix N: Property Extensions and Advanced Attributes**

## **N.1 Purpose**

Defines optional-but-supported extension properties that enrich entities without breaking base schema compatibility.

## **N.2 Authoritative Files**

- `md/Reference/Entity_Property_Extensions.md`
- `md/Reference/Property_Extensions_Implementation_Guide.md`
- `md/Reference/Property_Extensions_Summary.md`

## **N.3 Extension Groups**

### Place Extensions

- `geo_coordinates`
- `pleiades_id`, `pleiades_link`
- `google_earth_link`
- optional geometry payload (`geo_json`)

### Temporal Extensions

- `end_date`
- `date_precision`
- `temporal_uncertainty`

### Backbone Extensions

- `backbone_fast`
- `backbone_lcc`
- `backbone_lcsh`
- `backbone_marc`

### Person/Work Discovery Extensions

- image metadata (`image_url`, `image_source`, `image_license`)
- related works arrays (`related_fiction`, `related_art`, `related_nonfiction`)
- online text availability metadata

## **N.4 Validation Rules**

1. Extension properties must not replace core required properties.
2. Keep external IDs as atomic strings.
3. Validate URL and coordinate formats before write.
4. Treat extension blocks as forward-compatible optional schema.

## **N.5 Recommended Rollout**

- Phase 1: temporal and backbone extensions
- Phase 2: geographic extension enrichment
- Phase 3: person/work media and online text extensions

---

**(End of Appendix N)**

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

# **Appendix P: Semantic Enrichment & Ontology Alignment (CIDOC-CRM/CRMinf)**

## **P.1 Purpose**

Implements automatic **CIDOC-CRM and CRMinf ontology alignment** for all entities and claims in the Chrystallum knowledge graph. This provides:

- **Triple alignment**: Chrystallum ↔ Wikidata ↔ CIDOC-CRM
- **Cultural heritage interoperability** (CIDOC-CRM ISO 21127 standard)
- **Belief tracking** with CRMinf argumentation ontology
- **Semantic web compatibility** for RDF/OWL export

Every SubjectConcept node and Claim includes ontology alignment metadata alongside its Wikidata QID, enabling multi-ontology queries and museum/archive data exchange.

**Implementation Status:** ✅ Complete (Step 4, 2026-02-15)
**Source:** ~250 lines added to `scripts/agents/facet_agent_framework.py`

---

## **P.2 CIDOC-CRM Entity Mappings**

**Source:** `CIDOC/cidoc_wikidata_mapping_validated.csv` (105 validated mappings)

### **P.2.1 Key Entity Class Mappings**

| Wikidata QID | Description | CIDOC-CRM Class | Confidence |
|-------------|-------------|-----------------|------------|
| **Q5** | human | **E21_Person** | High |
| **Q1656682** | event | **E5_Event** | High |
| **Q178561** | battle | **E5_Event** | High |
| **Q82794** | geographic region | **E53_Place** | High |
| **Q515** | city | **E53_Place** | High |
| **Q43229** | organization | **E74_Group** | High |
| **Q7252** | cultural heritage | **E22_Man-Made_Object** | Medium |
| **Q273057** | discourse | **E28_Conceptual_Object** | Medium |

### **P.2.2 Key Property Mappings**

| Wikidata Prop | Description | CIDOC-CRM Prop | Confidence |
|--------------|-------------|----------------|------------|
| **P31** | instance of | **P2_has_type** | High |
| **P279** | subclass of | **P127_has_broader_term** | High |
| **P276** | location | **P7_took_place_at** | High |
| **P710** | participant | **P11_had_participant** | High |
| **P580** | start time | **P82a_begin_of_the_begin** | High |
| **P582** | end time | **P82b_end_of_the_end** | High |
| **P131** | located in admin territory | **P89_falls_within** | High |
| **P361** | part of | **P106_is_composed_of** (inverse) | Medium |

---

## **P.3 CRMinf Belief Tracking**

**CRMinf Ontology:** Argumentation and reasoning extension to CIDOC-CRM

### **P.3.1 Core Mappings**

| CRMinf Class/Property | Chrystallum Mapping | Usage |
|----------------------|---------------------|-------|
| **I2_Belief** | Claim node | Core belief held by agent |
| **J4_that** | Claim.label | The proposition (text) |
| **J5_holds_to_be** | Claim.confidence | Belief value 0.0-1.0 |
| **I4_Proposition_Set** | Related claim cluster | Multi-agent debate |
| **I5_Inference_Making** | Bayesian update | When posterior_probability exists |
| **I6_Belief_Value** | Confidence tiers | Layer-based authority |

### **P.3.2 Claim Storage Format**

**Example Claim with CRMinf Alignment:**

```python
{
  "label": "Battle of Pharsalus occurred on August 9, 48 BCE",
  "confidence": 0.90,
  "authority_source": "Wikidata",
  "authority_ids": {
    "source_qid": "Q28048",
    "property": "P585",
    "target_value": "48 BCE-08-09"
  },
  "facet": "military",
  "crminf_alignment": {
    "crminf_class": "I2_Belief",
    "J4_that": "Battle of Pharsalus occurred on August 9, 48 BCE",
    "J5_holds_to_be": 0.90,
    "source_agent": "military_facet",
    "facet": "military",
    "rationale": "From Wikidata property P585 (point in time)",
    "inference_method": "wikidata_federation",
    "timestamp": "2026-02-15T12:00:00Z"
  }
}
```

**Interpretation:**
- Belief (I2_Belief) held by military_facet agent
- Proposition (J4_that) is textual claim
- Agent holds with 0.90 confidence (J5_holds_to_be)
- Formed via wikidata_federation (trusted external source)

---

## **P.4 Authority Precedence Integration**

**Integration:** Step 4-5 commit (d56fc0e) integrates multi-tier authority checking with ontology enrichment.

### **P.4.1 Multi-Tier Authority Policy**

**Authority Tier Policy (from §4.4):**
```
Tier 1 (Preferred): LCSH, FAST               (domain-optimized for historical subjects)
Tier 2 (Secondary): LCC, CIP                 (structural backbone + academic alignment)
Tier 3 (Tertiary):  Wikidata, Dewey, VIAF   (fallback authorities)
```

### **P.4.2 Enhanced Enrichment Algorithm**

**Pseudo-code for Multi-Authority Node Enrichment:**

```python
def enrich_node_with_authorities(entity_qid):
    """
    Enrich SubjectConcept node with multi-authority IDs (Tier 1/2/3)
    + CIDOC-CRM ontology alignment
    """
    node = {'qid': entity_qid}
    
    # STEP 1: Fetch Wikidata data
    wikidata_data = fetch_wikidata_entity(entity_qid)
    
    # STEP 2: Extract Tier 1 authorities from Wikidata (if available)
    lcsh_id = wikidata_data.get('P244')      # Library of Congress authority ID
    fast_id = wikidata_data.get('special:fast_id')  # FAST derived from LCSH
    
    if lcsh_id:
        node['authority_id'] = lcsh_id          # ← Tier 1 primary
        node['authority_tier'] = 1
    
    if fast_id:
        node['fast_id'] = fast_id                # ← Tier 1 secondary
    
    # STEP 3: If no Tier 1, check Tier 2 (LCC)
    if not lcsh_id:
        lcc_mapping = lookup_lcc_for_qid(entity_qid)
        if lcc_mapping:
            node['lcc_class'] = lcc_mapping['class']
            node['authority_tier'] = 2
    
    # STEP 4: Always include Wikidata (Tier 3 fallback)
    node['wikidata_qid'] = entity_qid
    node['qid_tier'] = 3
    
    # STEP 5: Add CIDOC-CRM alignment (orthogonal to authorities)
    cidoc_enrichment = enrich_with_ontology_alignment(wikidata_data)
    node['cidoc_crm_class'] = cidoc_enrichment['cidoc_crm_class']
    node['cidoc_crm_confidence'] = cidoc_enrichment['cidoc_crm_confidence']
    
    return node
```

**Result Node Structure:**

```python
{
    'authority_id': 'sh85115055',           # Tier 1: LCSH (preferred)
    'authority_tier': 1,
    'fast_id': 'fst01234567',              # Tier 1: FAST (complementary)
    'wikidata_qid': 'Q12107',              # Tier 3: Wikidata fallback
    'qid_tier': 3,
    'cidoc_crm_class': 'E5_Event',         # Orthogonal semantic alignment
    'cidoc_crm_confidence': 'High',
    'label': 'Roman politics'
}
```

### **P.4.3 Query Examples**

**Before Multi-Authority (Wikidata Only):**

```cypher
// Single authority source
MATCH (n:SubjectConcept {wikidata_qid: 'Q12107'})
RETURN n
```

**After Multi-Authority Integration:**

```cypher
// Multi-authority aware query with tier preference
MATCH (n:SubjectConcept)
WHERE n.authority_id = 'sh85115055'        // LCSH preferred
   OR n.fast_id = 'fst01234567'            // FAST complementary
   OR n.wikidata_qid = 'Q12107'            // Fallback
ORDER BY COALESCE(n.authority_tier, 3)     // Tier 1 results first
RETURN n
```

**Query by CIDOC Class:**

```cypher
// Find all E21_Person entities (humans)
MATCH (n:SubjectConcept {cidoc_crm_class: 'E21_Person'})
RETURN n.label, n.wikidata_qid, n.authority_id
LIMIT 10

// Find all E5_Event entities (battles, conflicts)
MATCH (n:SubjectConcept {cidoc_crm_class: 'E5_Event'})
WHERE n.label CONTAINS 'Battle'
RETURN n.label, n.wikidata_qid
LIMIT 10
```

### **P.4.4 Data Audit Query**

**Check Authority Coverage:**

```cypher
// Authority coverage statistics
MATCH (n:SubjectConcept)
RETURN 
    count(CASE WHEN n.authority_id IS NOT NULL THEN 1 END) as lcsh_count,
    count(CASE WHEN n.fast_id IS NOT NULL THEN 1 END) as fast_count,
    count(CASE WHEN n.wikidata_qid IS NOT NULL THEN 1 END) as wikidata_count,
    count(CASE WHEN n.cidoc_crm_class IS NOT NULL THEN 1 END) as cidoc_count,
    count(n) as total
```

**Rationale:**
- LCSH/FAST domain-optimized for historical scholarship; reduces federation friction
- Multi-authority storage enables library catalog interoperability
- Tier hierarchy prevents dependency lock on Wikidata
- CIDOC-CRM stays orthogonal to authority tier system

---

## **P.5 Implementation Methods**

**Added to:** `scripts/agents/facet_agent_framework.py` (~250 lines)

### **P.5.1 Method Signatures**

**1. Load CIDOC Crosswalk (~80 lines)**

```python
def _load_cidoc_crosswalk(self) -> Dict:
    """
    Load and parse CIDOC/Wikidata/CRMinf mappings from CSV.
    
    Source: CIDOC/cidoc_wikidata_mapping_validated.csv (105 mappings)
    Caching: Loads once per agent instance → self._cached_cidoc_crosswalk
    
    Returns:
        {
            'cidoc_by_qid': {
                'Q5': {'cidoc_class': 'E21_Person', 'confidence': 'High'},
                'Q1656682': {'cidoc_class': 'E5_Event', 'confidence': 'High'},
                ...
            },
            'cidoc_by_property': {
                'P710': {'cidoc_property': 'P11_had_participant', 'confidence': 'High'},
                'P276': {'cidoc_property': 'P7_took_place_at', 'confidence': 'High'},
                ...
            },
            'crminf_mappings': {
                'I2_Belief': 'Chrystallum Claim node',
                'J4_that': 'Claim.label (proposition)',
                'J5_holds_to_be': 'Claim.confidence (belief value)',
                ...
            }
        }
    """
```

**2. Enrich with Ontology Alignment (~90 lines)**

```python
def enrich_with_ontology_alignment(self, entity: Dict) -> Dict:
    """
    Add CIDOC-CRM classes and properties to Wikidata entity.
    
    Args:
        entity: Entity dict from fetch_wikidata_entity() or similar
        
    Process:
        1. Look up CIDOC class via P31 (instance of) QID
        2. Map entity properties to CIDOC properties
        3. Generate semantic triples (QID+Property+Value+CIDOC)
        4. Add ontology_alignment section to entity
        
    Returns:
        Enriched entity with ontology_alignment section:
        {
            ...existing entity data...,
            'ontology_alignment': {
                'cidoc_crm_class': 'E5_Event',
                'cidoc_crm_confidence': 'High',
                'cidoc_properties': [...],
                'semantic_triples': [...]
            }
        }
    """
```

**3. Enrich Claim with CRMinf (~60 lines)**

```python
def enrich_claim_with_crminf(self, claim: Dict, belief_value: float = 0.90) -> Dict:
    """
    Add CRMinf belief tracking metadata to Chrystallum Claim.
    
    Args:
        claim: Claim dict from generate_claims_from_wikidata() or agent reasoning
        belief_value: Confidence level (default 0.90)
        
    CRMinf Mapping:
        - Claim → I2_Belief (belief held by agent)
        - Claim.label → J4_that (proposition)
        - Claim.confidence → J5_holds_to_be (belief value 0.0-1.0)
        - Bayesian update → I5_Inference_Making (reasoning process)
        
    Returns:
        Enriched claim with crminf_alignment section:
        {
            ...existing claim data...,
            'crminf_alignment': {
                'crminf_class': 'I2_Belief',
                'J4_that': '...',
                'J5_holds_to_be': 0.90,
                'source_agent': '...',
                'inference_method': '...',
                'timestamp': '...'
            }
        }
    """
```

**4. Generate Semantic Triples (~70 lines)**

```python
def generate_semantic_triples(
    self, 
    entity_qid: str, 
    include_cidoc: bool = True, 
    include_crminf: bool = False
) -> List[Dict]:
    """
    Generate complete semantic triples for RDF/OWL export or validation.
    
    Args:
        entity_qid: Entity QID (must be in graph or fetchable from Wikidata)
        include_cidoc: Add CIDOC-CRM alignment to each triple
        include_crminf: Add CRMinf belief tracking (for claims)
        
    Returns:
        List of fully-aligned semantic triples:
        [
            {
                'subject': 'Q28048',
                'subject_label': 'Battle of Pharsalus',
                'subject_cidoc': 'E5_Event',
                'property': 'P276',
                'property_label': 'location',
                'property_cidoc': 'P7_took_place_at',
                'value': 'Q240898',
                'value_label': 'Pharsalus',
                'value_cidoc': 'E53_Place',
                'confidence': 0.90,
                'crminf_belief': {...}  # if include_crminf=True
            }
        ]
    """
```

---

## **P.6 Semantic Triple Generation**

### **P.6.1 Example Output Structure**

**Query:** `generate_semantic_triples('Q28048', include_cidoc=True, include_crminf=True)`

**Output:**

```python
[
    {
        # Subject (entity)
        "subject": "Q28048",
        "subject_label": "Battle of Pharsalus",
        "subject_cidoc": "E5_Event",
        
        # Predicate (relationship)
        "property": "P276",
        "property_label": "location",
        "property_cidoc": "P7_took_place_at",
        
        # Object (target entity or literal)
        "value": "Q240898",
        "value_label": "Pharsalus",
        "value_cidoc": "E53_Place",
        
        # Provenance & belief tracking
        "confidence": 0.90,
        "crminf_belief": {
            "class": "I2_Belief",
            "J4_that": "Battle of Pharsalus took place at Pharsalus",
            "J5_holds_to_be": 0.90,
            "source": "Wikidata",
            "inference_method": "wikidata_federation"
        }
    }
]
```

### **P.6.2 Use Cases**

1. **RDF/OWL Export**: Convert to Turtle, RDF-XML, JSON-LD for semantic web
2. **CIDOC-CRM Validation**: Check if triple conforms to CIDOC constraints
3. **Museum Systems**: Export to collection management systems (CollectionSpace, TMS)
4. **SPARQL Queries**: Enable federated queries across Wikidata + Chrystallum + CIDOC repositories

---

## **P.7 Source Files**

### **P.7.1 Primary Implementation**

- **File:** `scripts/agents/facet_agent_framework.py`
- **Lines Added:** ~250 (4 methods)
- **Version:** 2026-02-15-step4

### **P.7.2 CIDOC Crosswalk Data**

- **File:** `CIDOC/cidoc_wikidata_mapping_validated.csv`
- **Mappings:** 105 validated entity/property mappings
- **Confidence Levels:** High, Medium, Low

### **P.7.3 System Prompts Update**

- **File:** `facet_agent_system_prompts.json`
- **Version:** 2026-02-15-step4
- **Content:** Added "SEMANTIC ENRICHMENT & ONTOLOGY ALIGNMENT" section to all 17 facets

### **P.7.4 Workflow Integration**

**Modified Methods:**
- `enrich_node_from_wikidata()` (lines ~751-840): Auto-enrichment in node creation
- `generate_claims_from_wikidata()` (lines ~928-1080): Auto-enrichment in claim generation

**Node Storage Format:**

```cypher
CREATE (n:SubjectConcept {
  id: 'wiki:Q28048',
  label: 'Battle of Pharsalus',
  wikidata_qid: 'Q28048',
  cidoc_crm_class: 'E5_Event',         // ← NEW (Step 4)
  cidoc_crm_confidence: 'High',        // ← NEW (Step 4)
  authority_tier: 2,
  confidence_floor: 0.90,
  created_at: '2026-02-15T...',
  created_by: 'military_facet'
})
```

---

## **P.8 Related Sections**

### **P.8.1 Internal Cross-References**

- **Appendix L**: CIDOC-CRM Integration Guide (foundational ontology overview)
- **Section 4.4**: Multi-Authority Model (Tier 1/2/3 precedence policy)
- **Section 4.9**: Academic Discipline Model (discipline flag usage)
- **Appendix K**: Wikidata Integration Patterns (federation discovery)
- **Section 6.4**: Claims Generation (CRMinf belief tracking integration)

### **P.8.2 Integration Points**

**Step 1 (Architecture Understanding):**
- `enrich_with_ontology_alignment()` uses `introspect_node_label()` for entity type validation

**Step 2 (State Introspection):**
- `get_session_context()` includes CIDOC alignment status
- `get_node_provenance()` shows ontology mapping history

**Step 3 (Federation Discovery):**
- `bootstrap_from_qid()` automatically calls enrichment methods
- `discover_hierarchy_from_entity()` maintains CIDOC alignment through hierarchy traversal

**Step 3.5 (Completeness Validation):**
- `validate_entity_completeness()` uses CIDOC class for type inference
- Property patterns validate against both Wikidata and CIDOC constraints

### **P.8.3 Benefits & Impact**

**Cultural Heritage Interoperability:**
- CIDOC-CRM ISO 21127 alignment enables data exchange with museum systems
- Compatible with: CollectionSpace, TMS, Arches, ResearchSpace

**Semantic Web Integration:**
- RDF/OWL export via semantic triples
- SPARQL queries across Wikidata, Chrystallum, and CIDOC endpoints
- Linked Open Data (LOD) publishing capability

**Argumentation & Belief Tracking:**
- CRMinf ontology models agent reasoning and confidence
- Multi-agent debate tracking with I4_Proposition_Set
- Bayesian updates tracked via I5_Inference_Making

**Multi-Ontology Querying:**
- Query by Wikidata (Q5, P31, etc.)
- Query by CIDOC-CRM (E21_Person, P7_took_place_at)
- Query by Chrystallum (SubjectConcept, INSTANCE_OF)
- Cross-ontology validation ensures consistency

---

**(End of Appendix P)**

---

# **Appendix Q: Operational Modes & Agent Orchestration**

**Version:** 2026-02-16  
**Status:** Operational (Initialize, Subject Ontology Proposal, Training modes implemented)  
**Source:** STEP_5_COMPLETE.md

---

## **Q.1 Purpose**

This appendix defines how agents operate in different contexts within the Chrystallum system. Unlike Steps 1-4 (which provide capabilities), Step 5 operational modes define **how agents work** with verbose logging for validation. Operational modes bridge the gap between agent capabilities and user workflows, supporting everything from initial domain bootstrapping to cross-domain query synthesis.

**Key Operational Modes:**
- **Initialize Mode:** Bootstrap new domain from Wikidata anchor
- **Subject Ontology Proposal:** Analyze hierarchies and propose domain ontology
- **Training Mode:** Extended iterative claim generation with validation
- **Schema Query Mode:** Answer questions about Neo4j model structure (design complete)
- **Data Query Mode:** Answer questions about actual graph data (design complete)
- **Wikipedia Training Mode:** LLM-driven article discovery (in design)

**Cross-Domain Orchestration:**
- **SubjectConceptAgent (SCA):** Master coordinator for multi-facet queries and bridge concept discovery

---

## **Q.2 SubjectConceptAgent (SCA) Two-Phase Architecture**

The **SubjectConceptAgent** is a **SEED AGENT** with **TWO DISTINCT PHASES** that operates differently from domain-specific SubjectFacetAgents (SFAs):

### **Q.2.0 Normative v0 Bootstrap Recraft (2026-02-17)**

For v0 bootstrap runs, apply the following contract (aligned with Appendix Y):

- Structural discovery writes are scaffold-only (`:ScaffoldNode`, `:ScaffoldEdge`).
- `:AnalysisRun` is the run anchor and must be created once per bootstrap run.
- Lateral traversal uses mapped properties only.
- SFA pre-promotion outputs are candidate/scaffold artifacts; canonical labels are promotion-gated.
- Canonical claim edge structure remains:
  - `(:Claim)-[:ASSERTS_EDGE]->(:ProposedEdge)-[:FROM]->(source)`
  - `(:ProposedEdge)-[:TO]->(target)`

### **Q.2.1 Phase 1: Un-Faceted Exploration**

**Scope:** Initialize Mode + Subject Ontology Proposal  
**Goal:** Broad discovery without facet constraints

**Characteristics:**
- **No facet lens** - Just hunting nodes and edges across all domains
- **Trawls hierarchies broadly** via P31 (instance_of), P279 (subclass_of), P361 (part_of) traversal
- **Goes beyond initial domain** - military → politics → culture → science
- **Creates shell nodes** for ALL discovered concepts (lightweight placeholders)
- **"Purple to mollusk" scenarios** - discovers seemingly unrelated cross-domain connections
- **Outputs proposed ontology** → APPROVAL POINT before facet analysis begins

**Example Discovery Path:**
```
Roman Republic (military anchor)
  → Roman Senate (political structure)
    → Senator rank (political hierarchy)
      → Toga praetexta (cultural artifact)
        → Tyrian purple dye (material culture)
          → Murex snail (scientific taxonomy)
```

**Data Created:**
- Shell SubjectConcept nodes with basic properties
- Hierarchical relationships (BROADER_THAN, INSTANCE_OF, PART_OF)
- Wikidata QID federation links
- Authority alignments (FAST, LCSH where available)

---

### **Q.2.2 Phase 2: Facet-by-Facet Analysis**

**Scope:** Training Mode  
**Goal:** Deep analysis through sequential facet lenses

**Characteristics:**
- **SCA adopts facet roles sequentially** - one facet at a time
- Reads claims from MILITARY perspective → then POLITICAL → then CULTURAL, etc.
- **Same nodes/edges analyzed through different facet lenses**
- Generates facet-specific claims and insights
- Uses proposed ontology from Phase 1 to prioritize nodes

**Process:**
```python
# Pseudo-code for Phase 2
for facet in ['MILITARY', 'POLITICAL', 'ECONOMIC', ...]:
    sca.set_facet_context(facet)
    for node in shell_nodes_from_phase1:
        if node.relevant_to(facet):
            claims = sca.generate_claims_with_facet_lens(node, facet)
            sca.enrich_node_with_facet_properties(node, facet, claims)
```

**Example Multi-Facet Analysis:**

Node: "Tyrian purple dye"

- **MILITARY facet:** "Used to mark senatorial authority in military contexts"
- **POLITICAL facet:** "Symbol of senatorial rank and imperium"
- **ECONOMIC facet:** "Luxury trade good, monopolized by elites"
- **CULTURAL facet:** "Status symbol in Roman dress codes"
- **SCIENTIFIC facet:** "Extracted from Murex brandaris mollusks"

**Architecture Diagram:**
```
┌─────────────────────────────────────────────┐
│      SubjectConceptAgent (SCA)              │
│      Master Coordinator                     │
│                                             │
│  • Facet classification (LLM)              │
│  • Multi-agent orchestration               │
│  • Bridge concept discovery                │
│  • Cross-domain synthesis                  │
└──────────────┬──────────────────────────────┘
               │
               │ Spawns & coordinates
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│ Military │      │Political │ ...  │ Biology  │
│   SFA    │      │   SFA    │      │   SFA    │
└──────────┘      └──────────┘      └──────────┘
```

---

## **Q.3 Canonical 18 Facets (UPPERCASE Keys)**

**Definitive List:**
```
ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, 
ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, 
RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL, COMMUNICATION
```

### **Q.3.1 Facet Key Normalization Rule**

**Policy (from commit d56fc0e):**
- All facet identifiers MUST be UPPERCASE
- SCA facet classification outputs UPPERCASE keys: `facets=['POLITICAL', 'MILITARY', 'ECONOMIC']`
- SubjectConcept.facet property = UPPERCASE (prevents case-collision bugs)
- Query filters: `WHERE n.facet IN ["POLITICAL", "MILITARY", ...]` (uppercase only)

**Rationale:**
- **Deterministic routing:** Prevents case-sensitive routing errors
- **Union-safe deduplication:** `['Military', 'MILITARY', 'military']` → `['MILITARY']`
- **Consistent with registry:** facet_registry_master.json uses UPPERCASE canonical keys

**Enforcement Points:**
```python
# Classification normalization
def classify_facets(query):
    llm_output = llm.invoke(query)  # may return mixed case
    return [f.upper() for f in llm_output['facets']]  # normalized

# Node creation
def create_subject_concept(label, facet):
    node = SubjectConcept(label=label, facet=facet.upper())

# Query filter
query = """
MATCH (n:SubjectConcept)
WHERE n.facet IN ["POLITICAL", "MILITARY"]  // UPPERCASE only
RETURN n
"""
```

---

### **Q.3.2 Facet Registry Validation (REQUIRED)**

**Architecture Requirement (from 2026-02-16 review):**
- Facet taxonomy MUST be validated against canonical registry at write-time
- No "by convention" - enforce programmatically via Pydantic + DB constraints
- Reject invalid facet keys before they enter the graph

**Implementation Pattern:**

```python
import json
from enum import Enum
from typing import List
from pydantic import BaseModel, validator

# Load canonical registry at startup
with open("Facets/facet_registry_master.json") as f:
    FACET_REGISTRY = json.load(f)
    VALID_FACETS = {f["key"].upper() for f in FACET_REGISTRY["facets"]}
    # {'ARCHAEOLOGICAL', 'ARTISTIC', 'BIOGRAPHIC', ..., 'COMMUNICATION'} (18 facets)

# Pydantic model for facet validation
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

class SubjectConceptCreate(BaseModel):
    """Pydantic model for SubjectConcept creation."""
    label: str
    facet: FacetKey  # Enum enforces valid values
    qid: str
    
    @validator('facet', pre=True)
    def normalize_facet(cls, v):
        """Normalize to uppercase and validate against registry."""
        normalized = v.upper() if isinstance(v, str) else v
        if normalized not in VALID_FACETS:
            raise ValueError(
                f"Invalid facet '{v}'. Must be one of: {sorted(VALID_FACETS)}"
            )
        return normalized

# Usage in node creation
def create_subject_concept(label: str, facet: str, qid: str):
    """Create SubjectConcept with facet validation."""
    try:
        # Pydantic validates and normalizes
        validated = SubjectConceptCreate(label=label, facet=facet, qid=qid)
        
        # Write to Neo4j
        with driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run("""
                    CREATE (n:SubjectConcept {
                        label: $label,
                        facet: $facet,
                        qid: $qid
                    })
                    RETURN n
                """, label=validated.label, facet=validated.facet, qid=validated.qid)
            )
        return {"status": "created", "facet": validated.facet}
        
    except ValueError as e:
        # Invalid facet rejected at Python layer
        return {"status": "error", "message": str(e)}

# SCA facet classification with validation
def classify_and_validate_facets(text: str) -> List[str]:
    """LLM classification + registry validation."""
    # LLM may return mixed case or invalid facets
    llm_output = llm.invoke({
        "text": text,
        "valid_facets": list(VALID_FACETS)  # Provide valid options
    })
    
    facets = llm_output.get("facets", [])
    validated = []
    
    for facet in facets:
        normalized = facet.upper()
        if normalized in VALID_FACETS:
            validated.append(normalized)
        else:
            # Log invalid facet from LLM (but don't crash)
            logger.warning(f"LLM returned invalid facet: {facet}. Skipping.")
    
    return validated
```

**Neo4j Constraint (Database-Level Enforcement):**

```cypher
// Create constraint: facet MUST be in valid set
CREATE CONSTRAINT subject_concept_valid_facet IF NOT EXISTS
FOR (n:SubjectConcept)
REQUIRE n.facet IN [
  'ARCHAEOLOGICAL', 'ARTISTIC', 'CULTURAL', 'DEMOGRAPHIC', 
  'DIPLOMATIC', 'ECONOMIC', 'ENVIRONMENTAL', 'GEOGRAPHIC', 
  'INTELLECTUAL', 'LINGUISTIC', 'MILITARY', 'POLITICAL', 
  'RELIGIOUS', 'SCIENTIFIC', 'SOCIAL', 'TECHNOLOGICAL', 'COMMUNICATION'
];

// Test: This will SUCCEED
CREATE (n:SubjectConcept {label: 'Roman Republic', facet: 'POLITICAL'})

// Test: This will FAIL with constraint violation
CREATE (n:SubjectConcept {label: 'Test', facet: 'LEGAL'})
// Error: Node violates constraint subject_concept_valid_facet
```

**Benefits:**
- ✅ **Programmatic enforcement:** Invalid facets rejected at Python layer (Pydantic) AND database layer (Neo4j constraint)
- ✅ **No silent errors:** LLM returning "Legal" or other invalid facets → caught and logged (BIOGRAPHIC is now canonical, LLM returns it correctly)
- ✅ **Single source of truth:** facet_registry_master.json is authoritative
- ✅ **Migration safety:** Can't accidentally introduce invalid facets during data imports
- ✅ **Clear error messages:** "Invalid facet 'LEGAL'. Must be one of: [ARCHAEOLOGICAL, ARTISTIC, ...]"

**Enforcement Points:**
1. **Node creation:** Pydantic validates before write
2. **Database write:** Neo4j constraint validates on commit
3. **LLM classification:** Validate and filter LLM outputs
4. **Query filters:** Use `WHERE n.facet IN [...]` with canonical list (see Q.3.1)
5. **Router logic:** Validate facet keys before routing to SFAs

---

## **Q.4 Operational Modes**

**Normative v0 boundary:**
- Initialize mode is structural bootstrap and scaffold persistence only.
- Canonical node/relationship writes occur via explicit Promotion workflow, not during bootstrap.

### **Q.4.1 Initialize Mode**

**Method:** `execute_initialize_mode(anchor_qid, depth, auto_submit_claims, ui_callback)`

**Purpose:** Bootstrap new domain from a Wikidata anchor entity.

**Workflow:**
1. Generate unique session ID
2. Create one `:AnalysisRun` anchor for the run
3. Fetch Wikidata anchor entity and validate basic completeness
4. Persist seed scaffold node (`:ScaffoldNode`) + optional seed dossier
5. Run bounded upward pass (P31/P279, depth caps)
6. Run mapped-property-only lateral pass (hop caps)
7. Run downward pass (inverse P279 depth caps + optional inverse P31 sampling)
8. Persist only scaffold artifacts (`:ScaffoldNode`, `:ScaffoldEdge`) and traces
9. Record caps/filters/truncation in run metadata
10. Return bootstrap summary (no canonical promotion in this mode)

**Parameters:**
- `anchor_qid`: Wikidata QID to bootstrap from (e.g., 'Q17167' for Roman Republic)
- `depth`: Hierarchy traversal depth (1=fast, 2=moderate, 3=comprehensive)
- `auto_submit_claims`: Whether to submit claims ≥0.90 confidence automatically
- `ui_callback`: Optional callback function for real-time log streaming to UI

**Returns:**
```python
{
    'status': 'INITIALIZED',  # or 'REJECTED', 'ERROR'
    'session_id': 'sca_20260217_143022_Q17167',
    'analysis_run_id': 'run_bootstrap_q17167_20260217_143022',
    'anchor_qid': 'Q17167',
    'anchor_label': 'Roman Republic',
    'scaffold_nodes_created': 523,
    'scaffold_edges_created': 1487,
    'upward_levels_traversed': 4,
    'lateral_hops_traversed': 2,
    'downward_depth_traversed': 2,
    'completeness_score': 0.87,
    'caps_applied': {'per_property_cap': 25, 'per_node_neighbor_cap': 200, 'per_parent_child_cap': 50},
    'truncation_events': 12,
    'duration_seconds': 42.3,
    'log_file': 'logs/military_agent_military_20260215_143022_Q17167_initialize.log'
}
```

---

### **Q.4.2 Subject Ontology Proposal Mode**

**Method:** `propose_subject_ontology(ui_callback)`

**Purpose:** Bridge between Initialize (discovery) and Training (systematic generation).

After Initialize mode discovers nodes and their hierarchical type properties, Subject Ontology Proposal analyzes these hierarchies to extract and propose a coherent domain ontology. This ontology then guides Training mode's claim generation.

**Workflow:**
1. Load initialized nodes (via session context)
2. Extract hierarchical type properties (P31, P279, P361)
3. Identify conceptual clusters using LLM
4. Propose ontology classes and relationships
5. Generate claim templates for Training mode
6. Define validation rules
7. Calculate strength score

**Outputs:**
```python
{
    'status': 'ONTOLOGY_PROPOSED',
    'session_id': 'military_20260215_143500',
    'facet': 'military',
    'ontology_classes': [
        {
            'class_name': 'Military Commander',
            'parent_class': None,
            'member_count': 15,
            'characteristics': ['rank', 'victories', 'legions_commanded'],
            'examples': ['Caesar', 'Pompey']
        }
    ],
    'hierarchy_depth': 3,
    'clusters': [...],
    'relationships': [...],
    'claim_templates': [...],
    'validation_rules': [...],
    'strength_score': 0.88,
    'reasoning': 'LLM explanation...',
    'duration_seconds': 22.4
}
```

---

### **Q.4.3 Training Mode**

**Method:** `execute_training_mode(max_iterations, target_claims, min_confidence, auto_submit_high_confidence, ui_callback)`

**Purpose:** Extended iterative claim generation with validation and quality metrics.

**Workflow:**
1. Load session context (Step 2) - get existing nodes
2. **Use proposed subject ontology** to guide claim generation
3. Iterate through SubjectConcept nodes (prioritize by ontology class)
4. For each node:
   - Check for Wikidata QID (skip if absent)
   - Fetch Wikidata entity (Step 3)
   - Validate completeness (Step 3.5)
   - Log reasoning for validation
   - Generate claims from statements (Step 3)
   - Enrich claims with CRMinf (Step 4) - automatic
   - Filter by min_confidence threshold
   - Optionally auto-submit claims ≥0.90 confidence
   - Log every decision with reasoning
5. Track metrics (claims/sec, avg confidence, avg completeness)
6. Stop when target_claims reached or max_iterations exhausted
7. Return comprehensive metrics

**Parameters:**
- `max_iterations`: Maximum nodes to process (5-100, default 100)
- `target_claims`: Stop after generating this many claims (10-500, default 500)
- `min_confidence`: Minimum confidence for claim proposals (0.5-1.0, default 0.80)
- `auto_submit_high_confidence`: Auto-submit claims ≥0.90 confidence (default False)
- `ui_callback`: Optional callback for real-time log streaming

**Returns:**
```python
{
    'status': 'TRAINING_COMPLETE',  # or 'ERROR'
    'session_id': 'military_20260215_143500',
    'iterations': 73,
    'nodes_processed': 73,
    'claims_proposed': 503,
    'claims_submitted': 0,
    'avg_confidence': 0.87,
    'avg_completeness': 0.82,
    'duration_seconds': 342.5,
    'claims_per_second': 1.47
}
```

---

### **Q.4.4 Schema Query Mode**

**Status:** Design complete, implementation pending  
**Purpose:** Answer questions about Neo4j model structure

**Capabilities (Planned):**
- Natural language queries about node types, properties, relationships
- Schema introspection and documentation
- Validation rule queries

**Example Queries:**
- "What properties does a SubjectConcept node have?"
- "What are all the relationship types between Human and Event nodes?"
- "Show me the validation rules for temporal properties"

---

### **Q.4.5 Data Query Mode**

**Status:** Design complete, implementation pending  
**Purpose:** Answer questions about actual graph data

**Capabilities (Planned):**
- Natural language to Cypher translation
- Facet-scoped data queries
- Cross-domain data synthesis

**Example Queries:**
- "How many military events occurred in the Roman Republic?"
- "Who were the political figures involved in the Battle of Pharsalus?"
- "What geographic locations are mentioned in connection with Julius Caesar?"

---

### **Q.4.6 Wikipedia Training Mode**

**Status:** In design  
**Purpose:** LLM-driven article discovery and claim extraction

**Capabilities (Planned):**
- Identify relevant Wikipedia articles for a subject domain
- Line-by-line claim extraction
- Registry validation (facets, relationships, entities)
- Claim creation/augmentation logic

---

## **Q.5 Discipline Root Detection & SFA Initialization**

**Integration Point:** After Initialize mode discovers hierarchy, detect canonical roots for SFA training (implements §4.9 policy).

**Method:** `detect_and_mark_discipline_roots(discovered_nodes, facet_key)`

**Purpose:** Identify which discovered nodes are discipline entry points (should have `discipline: true` flag).

### **Q.5.1 Detection Algorithm**

**Strategy 1: BROADER_THAN Reachability**
```python
def detect_discipline_roots(nodes_dict, facet_key):
    """
    Identify top-level concepts that should seed SFA training.
    Discipline roots are canonical entry points for agent specialization.
    """
    roots = []
    
    # Strategy 1: BROADER_THAN reachability (highest arity wins)
    for node in nodes_dict.values():
        reachability = count_reachable_via_broader_than(node)
        if reachability > 0.7 * len(nodes_dict):  # 70% of nodes below this root
            roots.append({
                'node_id': node['id'],
                'label': node['label'],
                'reachability': reachability,
                'method': 'high_reachability',
                'discipline_candidate': True
            })
    
    # Strategy 2: Explicit heuristics (facet-specific)
    if facet_key == 'MILITARY':
        military_keywords = ['Military', 'Warfare', 'Battle', 'Armed Force']
        for node in nodes_dict.values():
            if any(kw in node['label'] for kw in military_keywords):
                if len(node.get('BROADER_THAN', [])) == 0:  # No parent
                    roots.append({
                        'node_id': node['id'],
                        'label': node['label'],
                        'method': 'keyword_heuristic',
                        'discipline_candidate': True
                    })
    
    # Remove duplicates, return top 1-3 roots
    unique_roots = deduplicate_by_node_id(roots)
    return sorted(unique_roots, key=lambda x: x['reachability'], reverse=True)[:3]
```

**Result Format:**
```python
{
    'discipline_roots': [
        {
            'node_id': 'wiki:Q28048',
            'label': 'Roman Republic',
            'reachability': 0.95,
            'method': 'high_reachability',
            'facet': 'MILITARY'
        }
    ],
    'nodes_marked': 1,
    'ready_for_sfa_training': True
}
```

---

### **Q.5.2 Neo4j Implementation**

**Mark Discipline Roots:**
```cypher
-- After Initialize mode creates nodes, mark discipline roots:
MATCH (root:SubjectConcept {id: 'wiki:Q17167'})
SET root.discipline = true,
    root.facet = 'MILITARY',
    root.discipline_training_seed = true,
    root.discipline_marked_at = datetime()
```

**Query for SFA Training Initialization:**
```cypher
-- SFA queries for available roots:
MATCH (n:SubjectConcept)
WHERE n.discipline = true AND n.facet = 'MILITARY'
RETURN n.label, n.id, count((m)-[:BROADER_THAN*]->(n)) as hierarchy_depth
ORDER BY hierarchy_depth DESC
```

---

### **Q.5.3 Pre-Seeding Option**

If automatic detection is insufficient, pre-seed canonical root nodes explicitly:

```cypher
CREATE (root:SubjectConcept {
    subject_id: 'discipline_military_root',
    label: 'Military Science',
    facet: 'MILITARY',
    discipline: true,
    authority_id: 'sh85052639',  -- Library of Congress for "Military science"
    created_by: 'initialize_preseed',
    created_at: datetime()
})

-- Repeat for all 17 facets:
-- POLITICAL → 'Political Science'
-- ECONOMIC → 'Economic History'
-- CULTURAL → 'Cultural History'
-- (14 more...)
```

---

### **Q.5.4 Impact on SFA Training**

```python
# MilitarySFA initialization (from §4.9 refinement)
nodes = gds.query_graph(
    "MATCH (root:SubjectConcept) "
    "WHERE root.discipline = true AND root.facet = 'MILITARY' "
    "RETURN root"
)
# Gets: [SubjectConcept(Roman Republic)]

# SFA now builds hierarchy downward:
# Military Science → Roman Military → Legions → Tactics → ...

military_sfa.initialize_with_roots(nodes)
military_sfa.train_on_hierarchy()  # Build disciplinary ontology
```

---

## **Q.6 Cross-Domain Query Example: "Senator to Mollusk"**

**Query:** *"What is the relationship between a Roman senator and a mollusk?"*

### **Q.6.1 Classification Phase**

```python
sca = SubjectConceptAgent()
result = sca.execute_cross_domain_query(
    "What is the relationship between a Roman senator and a mollusk?"
)

# Classification output:
{
    'facets': ['POLITICAL', 'SCIENTIFIC', 'CULTURAL'],
    'cross_domain': True,
    'reasoning': 'Query spans political (senator), scientific (mollusk biology), cultural (textile dyeing)',
    'bridge_concepts': ['Tyrian purple', 'purple dye']
}
```

---

### **Q.6.2 Agent Spawning & Query Execution**

**Note:** Current implementation uses **simulated agents** (hard-coded mock responses) for smoke testing. Real SubjectFacetAgents can be spawned but require domain training.

```python
# SCA spawns 3 simulated agents
political_sfa = sca.spawn_agent('POLITICAL')  # Simulated
scientific_sfa = sca.spawn_agent('SCIENTIFIC')  # Simulated
cultural_sfa = sca.spawn_agent('CULTURAL')  # Simulated

# Each agent returns domain-specific results:
political_results = political_sfa.query("senator and purple")
# Returns: [senator → toga → purple stripe]

scientific_results = scientific_sfa.query("mollusk and dye")
# Returns: [mollusk → murex → dye production]

cultural_results = cultural_sfa.query("purple and textile")
# Returns: [purple dye → Tyrian purple → textile]
```

---

### **Q.6.3 Bridge Claim Generation**

SCA generates **data creation claims** (not just concept labels):

**1. NODE_CREATION Claim:**
```python
{
    'claim_type': 'NODE_CREATION',
    'label': 'Tyrian purple',
    'node_type': 'SubjectConcept',
    'facets': ['POLITICAL', 'SCIENTIFIC', 'CULTURAL'],  # Multi-facet node
    'properties': {
        'bridge_type': 'label_intersection',
        'source_facets': ['POLITICAL', 'SCIENTIFIC', 'CULTURAL']
    },
    'confidence': 0.85,
    'reasoning': 'Concept "Tyrian purple" appears in multiple domains'
}
```

**2. EDGE_CREATION Claims:**
```python
[
    {
        'claim_type': 'EDGE_CREATION',
        'source_node': 'node_pol_1',  # Roman senator
        'target_node': 'Tyrian purple',
        'relationship_type': 'RELATES_TO',
        'facet': 'POLITICAL',
        'confidence': 0.85,
        'reasoning': 'Bridge connection from political domain'
    },
    {
        'claim_type': 'EDGE_CREATION',
        'source_node': 'node_sci_2',  # murex snail
        'target_node': 'Tyrian purple',
        'relationship_type': 'RELATES_TO',
        'facet': 'SCIENTIFIC',
        'confidence': 0.85,
        'reasoning': 'Bridge connection from scientific domain'
    }
]
```

**3. NODE_MODIFICATION Claim:**
```python
{
    'claim_type': 'NODE_MODIFICATION',
    'label': 'Tyrian purple',
    'node_id': 'existing_node_123',
    'modifications': {
        'add_facets': ['POLITICAL', 'SCIENTIFIC'],
        'add_property': {'key': 'bridge_concept', 'value': True}
    },
    'confidence': 0.80,
    'reasoning': 'Found in additional domain(s)'
}
```

---

### **Q.6.4 Synthesis**

**Natural Language Response:**
```
Roman senators wore togas with purple stripes (toga praetexta) or all-purple 
togas (toga purpurea) as symbols of their rank. The distinctive Tyrian purple 
dye used for these garments was extracted from murex sea snails, a type of 
mollusk. This expensive dye—requiring thousands of mollusks to produce just a 
few grams—was reserved for the Roman elite, making it a luxury marker of 
senatorial status.
```

**Key Insight:** Bridge discovery doesn't just find labels—it **generates claims** to create graph structure connecting disparate domains.

---

## **Q.7 Implementation Components**

### **Q.7.1 Core Framework Components**

**1. AgentOperationalMode Enum**
```python
class AgentOperationalMode(Enum):
    INITIALIZE = "initialize"
    TRAINING = "training"
    SCHEMA_QUERY = "schema_query"
    DATA_QUERY = "data_query"
```

**2. AgentLogger Class** (~200 lines)

**Purpose:** Verbose logging with structured action tracking, reasoning capture, and session metrics.

**Key Methods:**
- `log_action(action, details, level)` - Log structured actions
- `log_reasoning(decision, rationale, confidence)` - Log agent reasoning
- `log_query(query_type, query, result)` - Log queries (Cypher, API)
- `log_error(error, context)` - Log errors with context
- `log_claim_proposed(claim_id, label, confidence)` - Track claim proposals
- `log_node_created(node_id, label, type)` - Track node creation
- `get_summary()` - Generate session summary statistics
- `close()` - Close logger and write summary

**3. SubjectConceptAgent (SCA)** (~400 lines)

**Purpose:** Master coordinator for cross-domain orchestration.

**Key Methods:**
- `classify_facets(query, max_facets)` - LLM-based facet classification (from canonical 17)
- `spawn_agent(facet_key)` - Simulate SubjectFacetAgent (smoke test mode)
- `execute_cross_domain_query(query)` - Orchestrate multi-facet query
- `query_within_facet(query, facet_key)` - Single-facet convenience method
- `route_claim(claim)` - Tag and route claims to multiple facets
- `_simulate_facet_query(facet_key, query)` - Mock query execution (for testing)
- `_find_conceptual_bridges(facet_results, suggested_bridges)` - Generate bridge CLAIMS
- `_synthesize_response(query, facet_results, bridge_claims)` - LLM synthesis

**4. FacetAgent Class** (~50 lines base + facet-specific methods)

**Purpose:** Domain-specific agent for single-facet operations.

**Key Methods:**
- `execute_initialize_mode(anchor_qid, depth, ...)` - Bootstrap from Wikidata
- `propose_subject_ontology(ui_callback)` - Analyze hierarchies
- `execute_training_mode(max_iterations, ...)` - Iterative claim generation
- `detect_and_mark_discipline_roots(nodes, facet)` - Root detection
- `set_mode(mode)` / `get_mode()` - Operational mode management

---

### **Q.7.2 Method Signatures**

**Initialize Mode:**
```python
def execute_initialize_mode(
    anchor_qid: str,
    depth: int = 1,
    auto_submit_claims: bool = False,
    ui_callback: Optional[Callable] = None
) -> Dict[str, Any]
```

**Training Mode:**
```python
def execute_training_mode(
    max_iterations: int = 100,
    target_claims: int = 500,
    min_confidence: float = 0.80,
    auto_submit_high_confidence: bool = False,
    ui_callback: Optional[Callable] = None
) -> Dict[str, Any]
```

**Cross-Domain Query:**
```python
def execute_cross_domain_query(
    query: str,
    auto_classify: bool = True,
    facets: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Claim Routing:**
```python
def route_claim(
    claim: Dict[str, Any]
) -> Dict[str, Any]
```

---

## **Q.8 Log Output Format**

### **Q.8.1 Log File Structure**

**File Location:** `logs/{agent_id}_{session_id}_{mode}.log`

**Example:** `logs/military_agent_military_20260215_143022_Q17167_initialize.log`

**Structure:**
```
# Agent Log: military_agent
# Mode: initialize
# Session: military_20260215_143022_Q17167
# Started: 2026-02-15T14:30:22.123456
================================================================================

[timestamp] [level] [category] message

...action logs...
...reasoning logs...
...query logs...
...error logs...

================================================================================
# SESSION SUMMARY
# Duration: 42.3s
# Actions: 127
# Reasoning steps: 23
# Queries: 8
# Errors: 0
# Claims proposed: 147
# Nodes created: 23
================================================================================
```

---

### **Q.8.2 Log Categories**

- `[INITIALIZE]` - Initialize mode actions
- `[TRAINING]` - Training mode actions
- `[REASONING]` - Decision reasoning with confidence
- `[QUERY]` - Cypher/API query execution
- `[ERROR]` - Errors with context

---

### **Q.8.3 Initialize Mode Log Example**

```
[2026-02-15T14:30:22] [INFO] [INITIALIZE] INITIALIZE_START: anchor_qid=Q17167, depth=2, facet=military, auto_submit=False
[2026-02-15T14:30:23] [INFO] [INITIALIZE] FETCH_ANCHOR: qid=Q17167
[2026-02-15T14:30:25] [INFO] [INITIALIZE] FETCH_COMPLETE: label=Roman Republic, statements=142
[2026-02-15T14:30:26] [INFO] [REASONING] COMPLETENESS_VALIDATION: Found 47/52 expected properties (confidence=0.87)
[2026-02-15T14:30:27] [INFO] [INITIALIZE] CIDOC_ENRICHMENT: qid=Q17167
[2026-02-15T14:30:28] [INFO] [INITIALIZE] CIDOC_COMPLETE: cidoc_class=E5_Event, confidence=High
[2026-02-15T14:30:29] [INFO] [INITIALIZE] AUTHORITY_ENRICHMENT: qid=Q17167
[2026-02-15T14:30:29] [INFO] [INITIALIZE] AUTHORITY_TIER_1: authority_id=sh85115055, fast_id=fst01234567
[2026-02-15T14:30:30] [INFO] [INITIALIZE] BOOTSTRAP_START: qid=Q17167, depth=2
[2026-02-15T14:31:03] [INFO] [INITIALIZE] BOOTSTRAP_COMPLETE: nodes_created=23, relationships=47, claims_generated=147
[2026-02-15T14:31:03] [INFO] [INITIALIZE] DISCIPLINE_ROOT_DETECTION: Analyzing 23 nodes for discipline candidates
[2026-02-15T14:31:04] [INFO] [INITIALIZE] DISCIPLINE_ROOTS_FOUND: 3 candidates (Roman Republic, Military Power, Civil War)
[2026-02-15T14:31:04] [INFO] [INITIALIZE] SET_DISCIPLINE_FLAG: Roman Republic marked discipline=true (MILITARY facet root)
[2026-02-15T14:31:04] [INFO] [INITIALIZE] INITIALIZE_COMPLETE: status=SUCCESS, duration=42.3s, nodes_with_discipline=1
```

---

### **Q.8.4 Training Mode Log Example**

```
[2026-02-15T14:35:00] [INFO] [TRAINING] TRAINING_START: max_iterations=20, target_claims=100, min_confidence=0.80, auto_submit=False
[2026-02-15T14:35:01] [INFO] [TRAINING] LOAD_CONTEXT: session_id=military_20260215_143500
[2026-02-15T14:35:03] [INFO] [TRAINING] CONTEXT_LOADED: existing_nodes=157, pending_claims=23
[2026-02-15T14:35:04] [INFO] [TRAINING] ITERATION_START: iteration=1, total=20, node_id=abc123, node_label=Battle of Pharsalus
[2026-02-15T14:35:05] [INFO] [TRAINING] FETCH_WIKIDATA: qid=Q28048
[2026-02-15T14:35:07] [INFO] [REASONING] COMPLETENESS_VALIDATED: 47/52 properties (confidence=0.91)
[2026-02-15T14:35:08] [INFO] [TRAINING] GENERATE_CLAIMS: qid=Q28048
[2026-02-15T14:35:12] [INFO] [TRAINING] CLAIMS_GENERATED: count=8, qid=Q28048
[2026-02-15T14:35:13] [INFO] [TRAINING] CLAIM_PROPOSED: claim_id=claim_1, label=Battle of Pharsalus occurred at Pharsalus, confidence=0.90
[2026-02-15T14:35:14] [INFO] [TRAINING] CLAIM_PROPOSED: claim_id=claim_2, label=Julius Caesar participated in Battle of Pharsalus, confidence=0.90
[2026-02-15T14:35:20] [INFO] [TRAINING] ITERATION_COMPLETE: iteration=1, claims_this_node=8, total_proposed=8
[2026-02-15T14:35:21] [INFO] [TRAINING] ITERATION_START: iteration=2, total=20, node_id=def456, node_label=Julius Caesar
[...continues...]
[2026-02-15T14:37:45] [INFO] [TRAINING] TRAINING_COMPLETE: status=SUCCESS, nodes_processed=20, claims_proposed=147, duration=165.2s, claims_per_second=0.89
```

---

## **Q.9 Source Files**

### **Q.9.1 Primary Implementation**

**File:** `scripts/agents/facet_agent_framework.py`  
**Total Lines:** ~1,100 (Steps 1-5 cumulative)  
**Version:** 2026-02-15-step5-sca

**Classes Added in Step 5:**
- `AgentOperationalMode` (Enum) - 4 operational modes
- `AgentLogger` (~200 lines) - Verbose logging infrastructure
- `SubjectConceptAgent` (~400 lines) - Cross-domain orchestration

**Methods Added in Step 5:**
- `set_mode()` / `get_mode()` - Mode management
- `execute_initialize_mode()` - Bootstrap workflow
- `propose_subject_ontology()` - Hierarchy analysis
- `execute_training_mode()` - Iterative claim generation
- `detect_and_mark_discipline_roots()` - Root detection
- `classify_facets()` - LLM-based facet classification
- `spawn_agent()` - Agent spawning (simulated)
- `execute_cross_domain_query()` - Multi-facet orchestration
- `query_within_facet()` - Single-facet query
- `route_claim()` - Multi-facet claim routing
- `_simulate_facet_query()` - Mock execution for testing
- `_find_conceptual_bridges()` - Bridge claim generation
- `_synthesize_response()` - LLM synthesis

---

### **Q.9.2 UI Implementation**

**File:** `scripts/ui/agent_gradio_app.py`  
**Version:** 2026-02-15

**New Tabs:**
- "⚙️ Agent Operations" - Initialize & Training modes (single-facet)
- "🌐 Cross-Domain" - SubjectConceptAgent orchestration

---

### **Q.9.3 Training Resources**

**File:** `Facets/TrainingResources.yml`  
**Referenced by:** Appendix O (Facet Training Resources Registry)

Contains canonical training patterns and exemplar claims for each of the 17 facets.

---

## **Q.10 Related Sections**

### **Q.10.1 Internal Cross-References**

- **Appendix O:** Facet Training Resources Registry (training patterns for 17 facets)
- **Section 4.9:** Academic Discipline Model (discipline flag usage policy)
- **Appendix D:** Subject Facet Classification (17 canonical facets)
- **Appendix K:** Wikidata Integration Patterns (federation discovery P31/P279/P361)
- **Appendix P:** Semantic Enrichment & Ontology Alignment (CIDOC-CRM/CRMinf automatic enrichment)
- **Section 5:** Agent Architecture (agent roles and workflows)
- **Section 6:** Claims Layer (claim structure and validation)

---

### **Q.10.2 Integration Points**

**Step 1 (Schema Understanding):**
- Initialize mode validates claim structure before proposal
- Training mode checks required properties per node type
- Both use schema introspection for validation

**Step 2 (State Loading):**
- Training mode REQUIRES `get_session_context()` to load existing nodes
- Both modes use `find_claims_for_node()` to avoid duplicates
- State tracking ensures iterative progress

**Step 3 (Federation Discovery):**
- Initialize mode BUILT ON `bootstrap_from_qid()`
- Training mode uses `fetch_wikidata_entity()` per node
- Both use `generate_claims_from_wikidata()` for claim generation
- Hierarchy traversal via `discover_hierarchy_from_entity()`

**Step 3.5 (Completeness Validation):**
- Both modes REQUIRE `validate_entity_completeness()` before processing
- Reject entities with <60% completeness
- Track completeness metrics in training mode

**Step 4 (Ontology Alignment):**
- Both modes AUTOMATICALLY call `enrich_with_ontology_alignment()`
- All nodes get `cidoc_crm_class` property
- All claims get `crminf_alignment` section via `enrich_claim_with_crminf()`
- Ontology enrichment happens transparently in workflow

---

### **Q.10.3 Usage Examples**

**Initialize Roman Military History Domain:**
```python
from facet_agent_framework import FacetAgentFactory

factory = FacetAgentFactory()
agent = factory.get_agent('military')

result = agent.execute_initialize_mode(
    anchor_qid='Q17167',  # Roman Republic
    depth=2,
    auto_submit_claims=False
)

print(f"✅ Initialized {result['nodes_created']} nodes")
print(f"📊 Generated {result['claims_generated']} claims")
print(f"📈 Completeness: {result['completeness_score']:.1%}")
print(f"🏛️ CIDOC class: {result['cidoc_crm_class']}")
```

**Cross-Domain Query:**
```python
from facet_agent_framework import SubjectConceptAgent

sca = SubjectConceptAgent()

result = sca.execute_cross_domain_query(
    "What is the relationship between a Roman senator and a mollusk?"
)

print(f"✅ Query complete")
print(f"🌐 Facets: {', '.join(result['classification']['facets'])}")
print(f"🔗 Bridge claims: {result['bridge_claim_count']}")
print(f"\n💡 Answer:\n{result['synthesized_response']}")

sca.close()
```

**Continue with Training:**
```python
result = agent.execute_training_mode(
    max_iterations=50,
    target_claims=300,
    min_confidence=0.80
)

print(f"✅ Processed {result['nodes_processed']} nodes")
print(f"📊 Proposed {result['claims_proposed']} claims")
print(f"⚡ Performance: {result['claims_per_second']:.2f} claims/sec")
```

---

**(End of Appendix Q)**

---

# **Appendix R: Federation Strategy & Multi-Authority Integration**

## **R.1 Federation Architecture Principles**

Chrystallum employs **federation** as a core architectural pattern to reconcile, validate, and enrich historical data across multiple authoritative systems. Rather than depending on a single source of truth, the system orchestrates a **multi-hop enrichment network** where Wikidata serves as a discovery broker and domain-specific authorities provide canonical grounding.

### **R.1.1 Wikidata as Federation Broker, Not Final Authority**

Wikidata functions as the **identity hub and router** in the federation architecture:

- **Discovery layer**: Provides QIDs, labels, descriptions, and external identifier properties (P214, P1584, P1566, etc.)
- **Routing mechanism**: External ID properties serve as jump-off points to domain authorities (VIAF, Pleiades, GeoNames, Trismegistos, etc.)
- **Confidence positioning**: Resides at Layer 2 Federation with confidence floor 0.90
- **Epistemic status**: Treated as broad identity hint, not canonical source

**Key principle**: Always resolve candidate entities to Wikidata QID first, then follow federation links to deeper authorities. Wikidata assertions are *discovery inputs*, not *verified outputs*.

### **R.1.2 Two-Hop Enrichment Pattern**

Federation follows a systematic two-hop pattern:

```cypher
// Hop 1: Wikidata resolution
MATCH (candidate:Entity {label: "Emerita Augusta"})
MERGE (wd:WikidataEntity {qid: "Q13560"})
CREATE (candidate)-[:ALIGNED_WITH]->(wd)

// Hop 2: Domain authority enrichment
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)
MERGE (place:PleiadesPlace {id: pleiades_id})
WITH place
CALL apoc.load.json("https://pleiades.stoa.org/places/" + place.id + "/json") 
YIELD value
SET place.names = value.names,
    place.temporal_range = value.temporalRange,
    place.coordinates = value.reprPoint
CREATE (candidate)-[:SAME_AS {confidence: 0.95}]->(place)
```

This pattern ensures:
1. **Broad discovery** via Wikidata's extensive coverage
2. **Deep grounding** via specialist authorities
3. **Provenance tracking** at each hop
4. **Confidence scoring** based on federation depth

### **R.1.3 Confidence Floors and Layer 2 Federation Positioning**

Federation authorities are tiered by epistemic strength:

- **Layer 1 (0.95-1.0)**: Domain-specific canonical authorities
  - LCSH/FAST for subjects
  - Pleiades for ancient places
  - PIR/PLRE for Roman prosopography
  - EDH for Latin inscriptions

- **Layer 2 (0.85-0.94)**: Broad integration hubs
  - Wikidata (0.90 baseline)
  - VIAF (0.88 for persons, 0.85 for works)
  - Getty AAT (0.90 for hierarchical concepts)

- **Layer 3 (0.70-0.84)**: Complementary sources and derived data
  - GeoNames/OSM (0.75 for modern coordinates)
  - Crowdsourced content (case-by-case evaluation)

**Confidence boost rules**:
- Adding epigraphic evidence (EDH/Trismegistos): +0.15 to +0.20
- Cross-validation by 2+ authorities: +0.10
- Temporal/geographic constraint satisfaction: +0.10
- Primary source linkage: +0.15

### **R.1.4 Federation Edge Patterns**

The system uses typed federation relationships to capture different alignment strengths:

```cypher
// SAME_AS: High-confidence identity match (0.90+)
(candidate)-[:SAME_AS {confidence: 0.95, 
                       verified_at: datetime(),
                       method: "P1584_resolution"}]->(pleiades)

// ALIGNED_WITH: Probable match requiring validation (0.70-0.89)
(candidate)-[:ALIGNED_WITH {confidence: 0.80,
                            conflicts: ["date_range_mismatch"],
                            review_required: true}]->(wikidata)

// DERIVED_FROM: Extracted/inferred from authority
(claim)-[:DERIVED_FROM {extraction_date: date(),
                        confidence: 0.85,
                        extractor_version: "v2.3"}]->(viaf_record)

// CONFLICTS_WITH: Explicit disagreement requiring adjudication
(source_a)-[:CONFLICTS_WITH {conflict_type: "temporal_range",
                             source_a_value: "-509/-27",
                             source_b_value: "-500/-31",
                             resolution: null}]->(source_b)
```

These edge types enable:
- **Confidence propagation**: `SAME_AS` edges boost target confidence
- **Review triggers**: `ALIGNED_WITH` and `CONFLICTS_WITH` flag human review
- **Provenance chains**: `DERIVED_FROM` tracks extraction lineage
- **Quality metrics**: Edge distributions measure federation health

---

## **R.2 Current Federation Layers (6 Operational)**

### **R.2.1 Subject Authority Federation** 
**Status**: Most mature

**Authorities**: LCC/LCSH/FAST/Wikidata

**Coverage**: Entire subject classification backbone, routing for specialist agents, bibliographic crosswalks

**Key artifacts**:
- `query_lcsh_enriched.tsv` (LCSH mappings)
- `Python/lcsh/scripts`, `Python/fast/scripts` (ingestion pipelines)
- `LCC_AGENT_ROUTING.md` (agent scope definitions)

**Usage pattern**:
1. Resolve subject string → LCSH/FAST heading
2. Map heading → LCC call number range
3. Route to appropriate Specialist Facet Agent based on LCC class
4. Cross-reference Wikidata P-codes for international concept alignment
5. Apply facet tags from shared registry

### **R.2.2 Temporal Federation**
**Status**: Strong

**Authorities**: Year backbone + curated periods + PeriodO alignment

**Coverage**: All temporal concepts, period-based lensing, date normalization

**Key artifacts**:
- `time_periods.csv` (1,083 curated periods)
- `periodo-dataset.csv` (PeriodO mappings)
- `scripts/backbone/temporal` (Year node generation)

**Usage pattern**:
1. Parse temporal expression (label, date range, uncertainty markers)
2. Create/link to Year nodes (ISO-normalized)
3. Resolve period label → PeriodO ID with explicit bounds
4. Attach Period nodes to Events/Persons/Places as temporal envelopes
5. Validate temporal plausibility (events must fall within period bounds)
6. Support period-based lensing ("show only Late Republic events")

### **R.2.3 Facet Federation**
**Status**: Strong conceptual, moderate automation

**Authorities**: 17 canonical facets applied across subject and temporal layers

**Coverage**: Cross-cutting conceptual dimensions (warfare, religion, law, etc.)

**Key artifacts**:
- `facet_registry_master.json` (canonical facet definitions)
- `period_facet_tagger.py` (automated facet assignment)
- Agent scope definitions (facet-based routing)

**Usage pattern**:
1. Analyze entity/event for facet applicability
2. Assign facet tags from registry (e.g., `WARFARE`, `LEGAL_TOPICS`, `GEOGRAPHY`)
3. Use facet tags for:
   - Agent routing (LCC + facet → specialist agent)
   - Cross-domain queries ("all warfare-related concepts across periods")
   - Framework-specific emphasis (Marxist framework privileges `ECONOMICS`)

### **R.2.4 Relationship Semantics Federation**
**Status**: In progress

**Authorities**: CIDOC-CRM/CRMinf + Wikidata predicates

**Coverage**: Canonical relationship vocabulary, action structures, event participation roles

**Key artifacts**:
- `action_structure_vocabularies.csv` (relationship types)
- `action_structure_wikidata_mapping.csv` (Wikidata P-code mappings)
- Architecture relationship sections (CIDOC alignment)

**Usage pattern**:
1. Extract relationship from claim text
2. Map to canonical vocabulary entry (e.g., "commanded" → `COMMANDED_MILITARY_UNIT`)
3. Align to CIDOC-CRM class (e.g., `E7 Activity`, `PC14 carried out by`)
4. Cross-reference Wikidata predicate (e.g., P598 `commander of`)
5. Store all mappings for cross-system queries

### **R.2.5 Geographic Federation**
**Status**: Early/transition

**Authorities**: Geographic registry + authority extracts (stabilizing)

**Coverage**: Place concepts, modern/ancient name variants, coordinate resolution

**Key artifacts**:
- `geographic_registry_master.csv` (place registry)
- Large authority extract files (Getty, GeoNames)

**Current challenges**:
- Source selection (Getty language vs. place pull)
- Ancient vs. modern place disambiguation
- Coordinate precision for historical periods

**Usage pattern** (in development):
1. Resolve place string → registry entry
2. Distinguish ancient (Pleiades) vs. modern (GeoNames) context
3. Pull name variants and temporal validity
4. Use coordinates for visualization only, not primary ontology

### **R.2.6 Agent/Claims Federation**
**Status**: Architecturally defined, partial implementation

**Authorities**: Specialist agents with defined scopes + review/synthesis workflow

**Coverage**: Agent capability declarations, claim provenance, review chains

**Key artifacts**:
- `2-12-26 Chrystallum Architecture - DRAFT.md` (agent model)
- `facet_agent_system_prompts.json` (agent definitions)
- `md/Agents/SCA/SCA_SFA_ARCHITECTURE_PACKAGE.md` (workflow specification)

**Usage pattern**:
1. Route claim → appropriate Specialist Facet Agent based on LCC/facet/period
2. SFA generates claim with provenance metadata
3. Seed Claim Agent reviews for conflicts and gaps
4. Framework-specific lensing applies interpretive emphasis
5. All steps tracked as federation of agent contributions

---

## **R.3 Stacked Evidence Ladder**

**Core Principle**: Move candidate nodes as far down the evidence ladder as possible before they are considered "solid." Each tier provides a different kind of epistemic support, and depth down the ladder translates to higher confidence scores and stronger validation.

### **R.3.1 People/Names** (3-tier ladder)

#### **Tier 1: Broad Identity** (Wikidata + VIAF)

**Purpose**: Establish high-level identity for persons, especially elites, authors, and subjects of modern works

**Authorities**: Wikidata QID, VIAF (via P214)

**How to use**:
- Resolve person string → Wikidata QID (e.g., "Gaius Julius Caesar" → Q1048)
- Follow P214 to VIAF cluster for canonical name forms in multiple languages
- Check VIAF for cluster quality:
  - Single clean cluster = strong identity
  - Multiple clusters = name collision, treat with caution
- Use for prosopography of elites, author attribution, modern scholarly linking

**Confidence rule**: Wikidata-only person = **textual/unconfirmed** (0.70-0.75)

```cypher
// Tier 1 enrichment
MATCH (p:Person {label: "Gaius Julius Caesar"})
MERGE (wd:WikidataEntity {qid: "Q1048"})
CREATE (p)-[:ALIGNED_WITH {confidence: 0.75}]->(wd)
WITH p, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id)
MERGE (viaf:VIAFRecord {id: viaf_id})
CREATE (p)-[:DERIVED_FROM {confidence: 0.80, layer: "identity"}]->(viaf)
SET p.canonical_names = viaf.name_variants,
    p.identity_tier = 1
```

#### **Tier 2: Historical Grounding** (Trismegistos People + PIR/PLRE)

**Purpose**: Confirm person appears in primary documentary evidence with historical context (offices, locations, dates)

**Authorities**: Trismegistos People (TM_People), PIR (Prosopographia Imperii Romani), PLRE (Prosopography of the Later Roman Empire)

**How to use**:
- Check TM_People for papyrological/epigraphic attestations
- For Roman elites, resolve to PIR/PLRE prosopography ID
- Extract structured data:
  - Offices held (consul, praetor, legatus)
  - Attested locations with date ranges
  - Family relationships (gens, cognomen patterns)
- Use as **hard constraints**:
  - Do not allow events outside person's active date window
  - Geography envelope from attested locations
  - Office-based event participation rules (can't command legion without military office)

**Confidence rule**: Wikidata + VIAF + Trismegistos + PIR = **strongly attested historical person** (0.90-0.95)

```cypher
// Tier 2 enrichment
MATCH (p:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WITH p, wd
// Check Trismegistos
CALL apoc.load.json("https://www.trismegistos.org/person/" + tm_id) YIELD value
MERGE (tm:TrismegistosPerson {id: value.person_id})
CREATE (p)-[:SAME_AS {confidence: 0.90, evidence_type: "documentary"}]->(tm)
SET p.attested_documents = value.document_count,
    p.date_range = [value.earliest_date, value.latest_date],
    p.attested_locations = value.places,
    p.identity_tier = 2
// Add PIR for Roman elites
MERGE (pir:PIREntry {id: pir_id})
CREATE (p)-[:SAME_AS {confidence: 0.95, prosopography: "PIR"}]->(pir)
SET p.offices = pir.offices,
    p.cursus_honorum = pir.career_path
```

#### **Tier 3: Micro-Evidence** (LGPN + DDbDP)

**Purpose**: Ground person in specific documentary/onomastic evidence at the micro-historical level

**Authorities**: LGPN (Lexicon of Greek Personal Names), DDbDP (Duke Databank of Documentary Papyri)

**How to use**:
- **For Greek names**: Query LGPN for name frequency and geographic distribution
  - Use to support cultural/ethnic inferences ("common freedman name in Alexandria")
  - Check name variants and spelling patterns
- **For documentary papyri**: Link person to specific DDbDP documents
  - Create Evidence nodes for each papyrus mentioning person
  - Extract roles: party to contract, witness, official, recipient
  - Link Evidence → Person → Document → Place → Date for full provenance chain

**Confidence rule**: Tier 3 grounding = **micro-attested with primary source linkage** (0.95-0.98)

```cypher
// Tier 3 enrichment: Documentary evidence nodes
MATCH (p:Person)-[:SAME_AS]->(tm:TrismegistosPerson)
WITH p, tm
UNWIND tm.document_ids AS doc_id
MERGE (doc:Document {tm_id: doc_id})
MERGE (ev:Evidence {id: "ev_" + doc_id})
SET ev.type = "papyrological",
    ev.text = doc.transcription,
    ev.material = "papyrus",
    ev.findspot = doc.provenance,
    ev.date_range = doc.date
CREATE (ev)-[:DOCUMENTS]->(p)
CREATE (ev)-[:FOUND_AT]->(place:Place {pleiades_id: doc.pleiades_place})
CREATE (ev)-[:DATED_TO]->(year:Year {iso_year: doc.middle_date})
SET p.evidence_count = size(collect(DISTINCT doc_id)),
    p.identity_tier = 3

// LGPN onomastic support
MERGE (lgpn:LGPNEntry {name: p.label})
SET lgpn.frequency = lgpn_frequency,
    lgpn.geographic_distribution = lgpn_regions
CREATE (p)-[:ONOMASTIC_SUPPORT]->(lgpn)
```

**Attestation strength summary**:
- **Wikidata-only**: Textual reference, unverified (0.70-0.75)
- **VIAF + Wikidata**: Author/creator authority (0.80-0.85)
- **VIAF + Trismegistos + PIR**: Strongly attested elite (0.90-0.95)
- **VIAF + TM + PIR + DDbDP**: Micro-attested with full provenance (0.95-0.98)

---

### **R.3.2 Places** (3-tier ladder)

#### **Tier 1: Conceptual Place** (Pleiades)

**Purpose**: Establish ancient geographic concept with temporal validity and name variants

**Authority**: Pleiades (via P1584)

**How to use**:
- Resolve ancient place → Pleiades ID
- Pleiades provides:
  - **Conceptual place** (not just coordinate point)
  - Ancient and modern name variants
  - **Temporal validity periods** (which historical periods the place exists in)
  - Coordinate ranges (often approximate, reflecting uncertainty)
- Use as **canonical place key** for ancient geography
- Apply temporal validity to constrain events:
  - Events using this place must fall within its valid period
  - Flag anachronistic references (e.g., "Constantinople" used before founding)

**Confidence rule**: Pleiades place grounding + temporal validity = +0.10 to base confidence

```cypher
// Tier 1: Pleiades resolution
MATCH (place:Place {label: "Emerita Augusta"})
MERGE (wd:WikidataEntity {qid: "Q13560"})
CREATE (place)-[:ALIGNED_WITH]->(wd)
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pleiades_id + "/json") 
YIELD value
MERGE (pleiades:PleiadesPlace {id: pleiades_id})
SET pleiades.names = value.names,
    pleiades.temporal_range = value.temporalRange,
    pleiades.coordinates = value.reprPoint,
    pleiades.periods = value.periods
CREATE (place)-[:SAME_AS {confidence: 0.90, temporal_validity: pleiades.temporal_range}]->(pleiades)
SET place.ancient_names = [n in value.names WHERE n.language IN ['grc', 'la'] | n.nameTransliterated],
    place.modern_names = [n in value.names WHERE n.language = 'en' | n.nameTransliterated],
    place.valid_periods = pleiades.periods
```

#### **Tier 2: Granular Geography** (Trismegistos Geo + DARE)

**Purpose**: Village-level, quarter-level, and network geography for fine-grained historical context

**Authorities**: 
- **Trismegistos Geo (TM_Geo)**: Village/quarter level, especially Egypt/Eastern Mediterranean
- **DARE (Digital Atlas of the Roman Empire)**: Roads, military installations, administrative geography

**How to use**:
- **TM_Geo for local places**:
  - Resolve village/quarter names to TM_Geo IDs
  - Map TM_Geo → Pleiades to anchor micro-places in global ancient map
  - Use for papyrus provenance, fine-grained population studies
- **DARE for network geography**:
  - Validate route plausibility between places using Roman road network
  - Locate military sites, administrative centers, border installations
  - Calculate distances and travel times for event modeling

**Confidence rule**: Tier 2 granularity + network validation = +0.15 beyond Tier 1

```cypher
// Tier 2: Trismegistos Geo (micro-geography)
MATCH (place:Place {label: "Theadelphia"})
CALL apoc.load.json("https://www.trismegistos.org/place/" + tm_geo_id) YIELD value
MERGE (tm_place:TMGeoPlace {id: tm_geo_id})
SET tm_place.type = "village",
    tm_place.nome = value.administrative_unit,
    tm_place.parent_place = value.parent
CREATE (place)-[:SAME_AS {confidence: 0.92, granularity: "village"}]->(tm_place)
// Link to parent Pleiades region
MATCH (parent:PleiadesPlace {id: tm_place.parent_pleiades})
CREATE (place)-[:PART_OF]->(parent)

// DARE road network validation
MATCH (event:Event)-[:OCCURRED_AT]->(origin:Place),
      (event)-[:DESTINATION]->(destination:Place)
WITH event, origin, destination
CALL dare.validateRoute(origin.pleiades_id, destination.pleiades_id) YIELD isPlausible, distance_km, travel_days
WHERE isPlausible = true
SET event.validated_route = true,
    event.distance_km = distance_km,
    event.travel_time_estimate = travel_days
```

#### **Tier 3: Modern Ground Truth** (GeoNames/OSM)

**Purpose**: Precise modern coordinates and admin boundaries for visualization only

**Authorities**: GeoNames (via P1566), OpenStreetMap

**How to use**:
- Use **only for UI maps and modern context**
- Never as primary historical geography
- Pull precise coordinates, bounding boxes, current admin units
- Useful for:
  - Map visualization layers
  - Modern place-name resolution for user queries
  - Spatial indexing for approximation queries

**Critical constraint**: GeoNames/OSM provide modern geography. Roman provinces, ancient boundaries, and historical place concepts come from Pleiades/DARE/TM_Geo, not modern systems.

```cypher
// Tier 3: Modern coordinates (UI-only)
MATCH (place:Place)-[:SAME_AS]->(pleiades:PleiadesPlace)
WITH place, pleiades
MATCH (wd:WikidataEntity)-[:HAS_EXTERNAL_ID {property: "P1566"}]->(geonames_id)
WHERE (place)-[:ALIGNED_WITH]->(wd)
CALL apoc.load.json("http://api.geonames.org/getJSON?geonameId=" + geonames_id) 
YIELD value
MERGE (gn:GeoNamesPlace {id: geonames_id})
SET gn.lat = value.lat,
    gn.lng = value.lng,
    gn.modern_name = value.name,
    gn.admin_units = [value.countryName, value.adminName1],
    gn.bbox = value.bbox
CREATE (place)-[:HAS_MODERN_LOCATION {usage: "visualization_only"}]->(gn)
SET place.map_coordinates = point({latitude: gn.lat, longitude: gn.lng})
// Do NOT use for historical assertions
```

---

### **R.3.3 Events/Claims/Communications** (3-tier ladder)

#### **Tier 1: Named Events** (Wikidata)

**Purpose**: Discover event seeds from Wikidata's named events and basic participation structure

**Authority**: Wikidata (battles, reforms, assassinations, foundations, treaties)

**How to use**:
- Query Wikidata for events related to entities, periods, or places
- Extract basic structure:
  - Event type (P31): battle, reform, assassination, etc.
  - Participants (P710): with roles like "commander," "victim," "location"
  - Date (P585, P580-P582): point in time or start-end
  - Place (P276, P17): where event occurred
- Treat as **event seeds, not fully trusted events**
- Propose Event node with:
  - Event type classification
  - Ordered participant roles
  - Temporal and spatial anchors
  - Confidence: 0.75 (seed level)

**Confidence rule**: Wikidata event seed = 0.75, requires corroboration for acceptance

```cypher
// Tier 1: Wikidata event seed discovery
CALL apoc.load.json("https://www.wikidata.org/wiki/Special:EntityData/Q48314.json") 
YIELD value
WITH value.entities["Q48314"] AS battle
MERGE (event:Event {wikidata_qid: "Q48314"})
SET event.label = battle.labels.en.value,
    event.type = "battle",
    event.confidence_tier = 1,
    event.base_confidence = 0.75,
    event.requires_corroboration = true
// Extract participants
FOREACH (claim IN battle.claims.P710 |
  MERGE (participant:Entity {qid: claim.mainsnak.datavalue.value.id})
  CREATE (event)-[:HAS_PARTICIPANT {role: claim.qualifiers.P3831[0].datavalue.value.id}]->(participant)
)
// Extract temporal and spatial
SET event.date_point = battle.claims.P585[0].mainsnak.datavalue.value.time,
    event.place_qid = battle.claims.P276[0].mainsnak.datavalue.value.id
```

#### **Tier 2: Epigraphic/Documentary Evidence** (EDH + Trismegistos Texts)

**Purpose**: Corroborate events with primary epigraphic or documentary sources

**Authorities**: 
- **EDH (Epigraphic Database Heidelberg)**: Latin inscriptions (via P2192)
- **Trismegistos Texts**: Papyri and inscriptions catalog

**How to use**:
- For each event seed, search authorities for inscriptions/papyri mentioning:
  - Event participants (persons, organizations)
  - Event location and date range
  - Event type keywords (battle, dedication, victory, law)
- Create **Communication/Evidence nodes** for each source:
  - Full text transcription
  - Material type (marble, bronze, papyrus)
  - Dimensions and physical description
  - Findspot (linked to Place nodes via Pleiades/GeoNames)
  - Date range (linked to Year nodes)
- Link to Event with typed role:
  - `PRIMARY_EPIGRAPHIC_EVIDENCE`: Inscription directly commemorating event
  - `CONTEMPORARY_DOCUMENT`: Papyrus from event's time period referencing it
  - `LATER_COMMEMORATIVE`: Post-event memorial or historical inscription
- **Raise Event confidence** when at least one epigraphic record corroborates participants/date/place

**Confidence rule**: Event with EDH/TM textual evidence = +0.20 confidence (up to 0.95)

```cypher
// Tier 2: EDH inscription evidence
MATCH (event:Event {label: "Battle of Pharsalus"})
WITH event
// Search EDH for inscriptions mentioning event participants
CALL apoc.load.json("https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search?person=Caesar") 
YIELD value
UNWIND value.items AS inscription
MERGE (ev:Evidence {edh_id: inscription.id})
SET ev.type = "inscription",
    ev.material = inscription.materialDescription,
    ev.text_latin = inscription.text,
    ev.findspot = inscription.findspot,
    ev.date_range = [inscription.notBefore, inscription.notAfter],
    ev.dimensions = inscription.dimensions
CREATE (ev)-[:DOCUMENTS {role: "PRIMARY_EPIGRAPHIC_EVIDENCE"}]->(event)
// Link to place
MERGE (place:Place {pleiades_id: inscription.pleiadesId})
CREATE (ev)-[:FOUND_AT]->(place)
// Link to date
CREATE (ev)-[:DATED_TO]->(year:Year {iso_year: inscription.middleDate})
// Boost event confidence
SET event.evidence_count = coalesce(event.evidence_count, 0) + 1,
    event.confidence_tier = 2,
    event.base_confidence = event.base_confidence + 0.20
```

```cypher
// Tier 2: Trismegistos documentary papyri
MATCH (event:Event)-[:HAS_PARTICIPANT]->(person:Person)
WITH event, person
MATCH (person)-[:SAME_AS]->(tm:TrismegistosPerson)
WITH event, tm
CALL apoc.load.json("https://www.trismegistos.org/text/search?person_id=" + tm.id) 
YIELD value
UNWIND value.texts AS text
MERGE (doc:Document {tm_text_id: text.id})
SET doc.type = text.type,
    doc.material = text.material,
    doc.provenance = text.provenance,
    doc.date = text.date
MERGE (ev:Evidence {id: "ev_tm_" + text.id})
SET ev.type = "documentary_papyrus",
    ev.text_content = text.transcription
CREATE (ev)-[:DOCUMENTS {role: "CONTEMPORARY_DOCUMENT"}]->(event)
CREATE (ev)-[:SOURCE_DOCUMENT]->(doc)
SET event.documentary_evidence_count = coalesce(event.documentary_evidence_count, 0) + 1
```

#### **Tier 3: Multi-Source Claims with HiCO Modeling**

**Purpose**: Model each historical statement as a Claim with full provenance, allowing multiple conflicting assertions per event

**Authorities**: All sources (primary inscriptions/papyri, literary narratives, modern scholarly reconstructions)

**How to use**:
- For each Event, create multiple Claim nodes representing different source assertions:
  - **Claimant**: Livy, Polybius, EDH inscription EDH12345, modern historian
  - **Claim content**: Specific assertion (date, outcome, casualty count, motive)
  - **Target**: The Event node
  - **Claim type**: Primary evidence vs. secondary narrative vs. scholarly interpretation
- Use federation sources to classify claim types:
  - **Primary evidence**: EDH, Trismegistos papyri, archaeological reports
  - **Secondary narrative**: Literary sources (Livy, Plutarch, Tacitus)
  - **Tertiary reconstruction**: Modern scholarly works, Wikipedia
- Enable **framework-specific claim weighting**:
  - Source-critical framework: Privilege epigraphy > papyri > literary narrative
  - Great Man framework: Privilege biographical literary sources
  - Marxist framework: Privilege economic documentary evidence
- Store all claims, expose conflicts, allow adjudication

**Confidence rule**: Multi-source claims with explicit conflict modeling = highest rigor (0.95-0.98 for well-adjudicated events)

```cypher
// Tier 3: Multi-source claim modeling
MATCH (event:Event {label: "Battle of Pharsalus"})
WITH event
// Claim 1: Livy's narrative account
MERGE (livy:Author {name: "Livy"})
CREATE (claim1:Claim {id: "claim_livy_pharsalus_date"})
SET claim1.content = "Battle occurred in 48 BCE during consulship of Caesar",
    claim1.claim_type = "date_assertion",
    claim1.date_value = date("-048-08-09"),
    claim1.source_type = "secondary_narrative",
    claim1.confidence = 0.85
CREATE (claim1)-[:MADE_BY]->(livy)
CREATE (claim1)-[:ABOUT]->(event)

// Claim 2: Epigraphic evidence (EDH inscription)
MATCH (inscription:Evidence {edh_id: "HD012345"})
CREATE (claim2:Claim {id: "claim_edh12345_pharsalus"})
SET claim2.content = "Inscription commemorates Caesar's victory, dated by consulship",
    claim2.claim_type = "event_confirmation",
    claim2.date_value = date("-048"),
    claim2.source_type = "primary_epigraphic",
    claim2.confidence = 0.95
CREATE (claim2)-[:DERIVED_FROM]->(inscription)
CREATE (claim2)-[:ABOUT]->(event)

// Claim 3: Conflicting modern scholarly reconstruction
MERGE (scholar:Author {name: "Smith, J."})
CREATE (claim3:Claim {id: "claim_smith_pharsalus_redate"})
SET claim3.content = "Re-dating to July 48 BCE based on astronomical calculations",
    claim3.claim_type = "date_assertion",
    claim3.date_value = date("-048-07-15"),
    claim3.source_type = "modern_reconstruction",
    claim3.confidence = 0.75
CREATE (claim3)-[:MADE_BY]->(scholar)
CREATE (claim3)-[:ABOUT]->(event)

// Model explicit conflict
CREATE (claim3)-[:CONFLICTS_WITH {
  conflict_type: "date_precision",
  difference: "~1 month",
  adjudication: "Livy's consulship date preferred, supported by EDH evidence"
}]->(claim1)

// Set event confidence based on claim constellation
WITH event, collect(claim1) + collect(claim2) + collect(claim3) AS claims
SET event.claim_count = size(claims),
    event.primary_evidence_count = size([c IN claims WHERE c.source_type = "primary_epigraphic"]),
    event.confidence_tier = 3,
    event.base_confidence = 0.95  // High confidence due to primary + secondary corroboration
```

**Outcome**: Events become nodes anchored by multi-source claims, not flat facts. Frameworks can weight claims differently, conflicts are explicit, and provenance is complete.

---

## **R.4 Federation Usage Patterns by Authority**

This section provides concrete guidance for leveraging each major federation authority within Chrystallum's architecture.

### **R.4.1 Wikidata** (Central Hub, Layer 2, 0.90 Confidence Floor)

**Role**: Identity hub and router

**How to leverage**:
1. **Always resolve candidate entities to QID first**
   - Use labels, descriptions, aliases for disambiguation
   - Check P31 (instance of) and P279 (subclass of) for type validation
   - Use P361 (part of) for hierarchical context

2. **Use external ID properties as federation jump-off points**
   - P214 → VIAF (persons)
   - P1584 → Pleiades (ancient places)
   - P1566 → GeoNames (modern places)
   - P2192 → EDH (inscriptions)
   - P1958 → Trismegistos Places
   - P4230 → Trismegistos Texts
   - P227 → GND (German authority)
   - P2950 → Nomisma (numismatics)

3. **Extract event/period seeds from Wikidata structure**
   - Query events by type, participant, period, or location
   - Use as discovery layer for entities not yet in your graph
   - Treat all Wikidata assertions as *provisional*, requiring domain authority confirmation

4. **Store Wikidata provenance but don't treat as final authority**
   - Keep QID for linking and discovery
   - Overwrite Wikidata values when domain authorities provide better data
   - Track when Wikidata and domain authorities conflict

**Cypher pattern**:
```cypher
// Wikidata as router to domain authorities
MATCH (candidate:Entity {label: $label})
CALL apoc.load.json("https://www.wikidata.org/wiki/Special:EntityData/" + $qid + ".json")
YIELD value
WITH candidate, value.entities[$qid] AS wd_entity
// Store Wikidata link
MERGE (wd:WikidataEntity {qid: $qid})
SET wd.label = wd_entity.labels.en.value,
    wd.description = wd_entity.descriptions.en.value
CREATE (candidate)-[:ALIGNED_WITH {confidence: 0.90, layer: 2}]->(wd)
// Extract external IDs for federation
WITH candidate, wd_entity.claims AS claims
UNWIND keys(claims) AS property
WHERE property STARTS WITH "P" AND claims[property][0].mainsnak.datatype = "external-id"
WITH candidate, property, claims[property][0].mainsnak.datavalue.value AS external_id
MERGE (ext:ExternalID {property: property, value: external_id})
CREATE (candidate)-[:HAS_EXTERNAL_ID {property: property}]->(ext)
```

---

### **R.4.2 Pleiades** (Ancient Places Backbone)

**Role**: Authority for ancient geographic concepts

**How to leverage**:
1. **Resolve to Pleiades ID via Wikidata P1584**
   - Treat Pleiades as canonical ancient place identifier
   - Store Pleiades URI as primary external reference

2. **Pull structured geographic data**
   - Coordinate ranges (often polygons or representative points)
   - Ancient name variants (Greek, Latin, indigenous)
   - Modern name variants
   - Temporal validity periods (which historical periods place exists in)
   - Connection types (at, near, within for related places)

3. **Use temporal validity to constrain events**
   - Events at a place must fall within its active period
   - Flag anachronistic references for review
   - Support geo-temporal federation (place-period joint constraints)

4. **Handle coordinate uncertainty appropriately**
   - Pleiades coordinates often represent approximate area, not precise point
   - Use coordinate ranges for spatial queries, not exact positioning
   - Prefer Pleiades conceptual place over GeoNames precise coordinates for historical context

**Cypher pattern**:
```cypher
// Pleiades place enrichment
MATCH (place:Place)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id:ExternalID)
WITH place, pleiades_id.value AS pid
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pid + "/json") YIELD value
MERGE (pleiades:PleiadesPlace {id: pid})
SET pleiades.title = value.title,
    pleiades.ancient_names = [n IN value.names WHERE n.language IN ['grc', 'la', 'egy'] | 
                              {transcription: n.nameTransliterated, 
                               attestations: n.attestations,
                               language: n.language}],
    pleiades.modern_names = [n IN value.names WHERE n.language = 'en' | n.romanized],
    pleiades.coordinate_point = point({latitude: value.reprPoint[1], longitude: value.reprPoint[0]}),
    pleiades.periods = [p IN value.features[0].properties.periods | p],
    pleiades.temporal_range = {
      start: value.features[0].properties.minDate,
      end: value.features[0].properties.maxDate
    },
    pleiades.place_types = value.placeTypes
CREATE (place)-[:SAME_AS {confidence: 0.95, authority: "Pleiades"}]->(pleiades)
// Apply temporal validity constraint
WITH place, pleiades
MATCH (place)<-[:OCCURRED_AT]-(event:Event)
WHERE event.year < pleiades.temporal_range.start 
   OR event.year > pleiades.temporal_range.end
SET event.temporal_flags = coalesce(event.temporal_flags, []) + ["anachronistic_place_usage"],
    event.requires_review = true
```

---

### **R.4.3 Trismegistos** (Texts, People, Local Geography)

**Role**: Epigraphic/papyrological hub for documentary sources

**How to leverage**:

#### **TMPeople (Trismegistos People)**
1. **Check documentary source attestation**
   - Search for person by name or external ID
   - Get count of papyri/inscriptions mentioning person
   - Pull date range and geographic distribution of attestations

2. **Combine with PIR/PLRE for elite disambiguation**
   - Wikidata-only + no TM = textual figure, low confidence
   - Wikidata + TM + PIR = documentary evidence of elite, high confidence

3. **Use attestations as confidence bump**
   - TM presence = structurally stronger than Wikidata-only
   - Add +0.15 confidence for primary documentary evidence

#### **TMGeo (Trismegistos Geography)**
1. **Village/quarter-level geography**
   - Especially valuable for Egypt and Eastern Mediterranean
   - Use for fine-grained provenance of papyri
   - Map to Pleiades parent regions for global anchoring

2. **Administrative hierarchies**
   - Nome, toparchy, village structures for Greco-Roman Egypt
   - Use for population studies and micro-regional analysis

#### **TMTexts (Trismegistos Texts)**
1. **Create Communication/Evidence nodes for each text**
   - Full text transcription (when available)
   - Material type (papyrus, ostracon, parchment)
   - Provenance (findspot)
   - Date range
   - Text type (letter, contract, petition, etc.)

2. **Link texts to Events, Persons, Places**
   - Use role annotations: `PRIMARY_EPIGRAPHIC_EVIDENCE`, `CONTEMPORARY_DOCUMENT`
   - Build provenance chains: Evidence → Person → Event → Place → Date

**Cypher pattern**:
```cypher
// Trismegistos People enrichment
MATCH (person:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]-()) // P4343 = TM Person ID
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]->(tm_id:ExternalID)
WITH person, tm_id.value AS tm_person_id
CALL apoc.load.json("https://www.trismegistos.org/person/" + tm_person_id) YIELD value
MERGE (tm:TrismegistosPerson {id: tm_person_id})
SET tm.name = value.name,
    tm.document_count = value.attestations_count,
    tm.date_range = [value.date_min, value.date_max],
    tm.locations = value.attestation_places
CREATE (person)-[:SAME_AS {confidence: 0.90, evidence: "documentary"}]->(tm)
SET person.documentary_attestations = tm.document_count,
    person.confidence_boost = 0.15

// Trismegistos Texts → Evidence nodes
MATCH (tm:TrismegistosPerson)
WITH tm
CALL apoc.load.json("https://www.trismegistos.org/text/search?person_id=" + tm.id) YIELD value
UNWIND value.texts AS text
MERGE (doc:Document {tm_text_id: text.tm_id})
SET doc.type = text.text_type,
    doc.material = text.material,
    doc.date_range = [text.date_min, text.date_max],
    doc.provenance = text.provenance
MERGE (ev:Evidence {id: "ev_tm_" + text.tm_id})
SET ev.type = "documentary_papyrus",
    ev.text_content = text.transcription,
    ev.material = text.material
CREATE (ev)-[:SOURCE_DOCUMENT]->(doc)
CREATE (ev)-[:DOCUMENTS]->(person:Person)-[:SAME_AS]->(tm)
// Link to place via TMGeo
MERGE (place:Place {tm_geo_id: text.place_id})
CREATE (ev)-[:FOUND_AT]->(place)
```

---

### **R.4.4 EDH** (Latin Inscriptions)

**Role**: Authority for Latin inscriptions and their findspots/dates

**How to leverage**:
1. **Search inscriptions mentioning entities**
   - Query by person name, place, date range
   - Use EDH API for full-text search

2. **Create Evidence nodes with full material context**
   - Full text (original and translation when available)
   - Material (marble, bronze, limestone, etc.)
   - Dimensions and physical description
   - Findspot (link to Pleiades/GeoNames)
   - Date range (link to Year nodes)
   - Current location (museum/collection)

3. **Link to Events with typed roles**
   - `PRIMARY_EPIGRAPHIC_EVIDENCE`: Inscription directly commemorating event
   - `DEDICATORY_INSCRIPTION`: Honors person/god related to event
   - `BUILDING_INSCRIPTION`: Documents construction or renovation
   - `FUNERARY_INSCRIPTION`: Provides biographical data

4. **Raise Event confidence when EDH corroborates**
   - At least one EDH record mentioning event participants/place/date
   - Add +0.20 to event confidence
   - Mark event as "epigraphically attested"

**Cypher pattern**:
```cypher
// EDH inscription search and Evidence node creation
MATCH (person:Person {label: "Julius Caesar"})
WITH person
CALL apoc.load.json("https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search?person=" + person.label) 
YIELD value
UNWIND value.items AS inscription
MERGE (ev:Evidence {edh_id: inscription.id})
SET ev.type = "latin_inscription",
    ev.material = inscription.attributes.material,
    ev.text_latin = inscription.transcription.latin,
    ev.text_translation = inscription.transcription.translation,
    ev.dimensions = {
      height_cm: inscription.attributes.height,
      width_cm: inscription.attributes.width,
      depth_cm: inscription.attributes.depth
    },
    ev.date_range = [inscription.dates.notBefore, inscription.dates.notAfter],
    ev.findspot_description = inscription.findspot.description,
    ev.current_location = inscription.repository
CREATE (ev)-[:DOCUMENTS {role: "epigraphic_attestation"}]->(person)
// Link to Place
MERGE (findspot:Place {pleiades_id: inscription.findspot.pleiadesId})
CREATE (ev)-[:FOUND_AT]->(findspot)
// Link to date
WITH ev, inscription.dates.notBefore AS start_year, inscription.dates.notAfter AS end_year
UNWIND range(start_year, end_year) AS year_val
MERGE (year:Year {iso_year: year_val})
CREATE (ev)-[:DATED_TO]->(year)
// Boost person confidence
MATCH (person)<-[:DOCUMENTS]-(ev)
SET person.epigraphic_attestations = coalesce(person.epigraphic_attestations, 0) + 1,
    person.base_confidence = person.base_confidence + 0.20
```

---

### **R.4.5 VIAF** (People and Works Disambiguation)

**Role**: Name authority for persons and works

**How to leverage**:
1. **Resolve to VIAF via Wikidata P214**
   - VIAF provides canonical name forms in multiple languages
   - Links to national authority files (LoC, BnF, DNB, etc.)

2. **Use for identity confirmation**
   - Single clean VIAF cluster = strong identity
   - Multiple clusters = name collision, disambiguation needed
   - Check co-references for same-person validation

3. **Separate Person vs. Author vs. Subject roles**
   - VIAF work lists distinguish person as author vs. subject of works
   - Use for scholarly reception tracking
   - Connect Person node to WorksAbout and WorksBy lists

4. **Attestation strength matrix**:
   - Wikidata-only = textual/unconfirmed (0.70)
   - Wikidata + VIAF = author/creator authority (0.80)
   - VIAF + Trismegistos + PIR = strongly attested historical person (0.90)

**Cypher pattern**:
```cypher
// VIAF person enrichment
MATCH (person:Person)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P214"}]-()) // P214 = VIAF ID
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id:ExternalID)
WITH person, viaf_id.value AS viaf_id_val
CALL apoc.load.json("https://viaf.org/viaf/" + viaf_id_val + "/viaf.json") YIELD value
MERGE (viaf:VIAFRecord {id: viaf_id_val})
SET viaf.canonical_names = [n IN value.mainHeadings.data | n.text],
    viaf.name_variants = [n IN value.x400s.x400 | n.datafield.subfield[0].text],
    viaf.national_authorities = [s IN value.sources.source | s],
    viaf.works_count = size(value.titles.work)
CREATE (person)-[:SAME_AS {confidence: 0.85, authority: "VIAF"}]->(viaf)
SET person.canonical_name = viaf.canonical_names[0],
    person.name_variants = viaf.name_variants
// Extract works relationships
WITH person, viaf, value.titles.work AS works
UNWIND works AS work
MERGE (w:Work {title: work.title})
CREATE (person)-[:AUTHOR_OF]->(w)
// Check attestation strength
WITH person
OPTIONAL MATCH (person)-[:SAME_AS]->(tm:TrismegistosPerson)
OPTIONAL MATCH (person)-[:SAME_AS]->(pir:PIREntry)
WITH person, tm, pir
SET person.attestation_level = CASE
  WHEN tm IS NOT NULL AND pir IS NOT NULL THEN "strongly_attested"
  WHEN tm IS NOT NULL THEN "documentary_attested"
  ELSE "textual_only"
END,
person.base_confidence = CASE
  WHEN tm IS NOT NULL AND pir IS NOT NULL THEN 0.95
  WHEN tm IS NOT NULL THEN 0.85
  ELSE 0.75
END
```

---

### **R.4.6 GeoNames/OSM** (Modern Coordinates)

**Role**: Modern geographic ground truth for visualization

**How to leverage**:
1. **Pull precise coordinates and bounding boxes**
   - Use GeoNames API via Wikidata P1566
   - Get latitude, longitude, elevation
   - Pull admin hierarchy (country, state, region)
   - Get bounding box for spatial queries

2. **Use ONLY for UI maps and modern context**
   - Never as primary historical geography
   - Historical geography comes from Pleiades/DARE/TM_Geo
   - GeoNames provides visualization layer only

3. **Map ancient → modern for user experience**
   - Show "ancient Rome" on modern Italy map
   - Provide modern place names for context
   - Calculate modern travel distances for comparison

**Critical constraint**: Roman provinces, ancient boundaries, and historical place concepts are NOT derived from modern geography. Pleiades/DARE provide historical ontology; GeoNames provides visual convenience only.

**Cypher pattern**:
```cypher
// GeoNames modern coordinates (visualization-only)
MATCH (place:Place)-[:SAME_AS]->(pleiades:PleiadesPlace)
WITH place, pleiades
MATCH (place)-[:ALIGNED_WITH]->(wd:WikidataEntity)
WHERE EXISTS((wd)-[:HAS_EXTERNAL_ID {property: "P1566"}]-()) // P1566 = GeoNames ID
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1566"}]->(gn_id:ExternalID)
WITH place, gn_id.value AS geonames_id
CALL apoc.load.json("http://api.geonames.org/getJSON?geonameId=" + geonames_id + "&username=demo") 
YIELD value
MERGE (gn:GeoNamesPlace {id: geonames_id})
SET gn.lat = toFloat(value.lat),
    gn.lng = toFloat(value.lng),
    gn.modern_name = value.name,
    gn.country = value.countryName,
    gn.admin1 = value.adminName1,
    gn.admin2 = value.adminName2,
    gn.bbox = value.bbox
CREATE (place)-[:HAS_MODERN_LOCATION {
  usage: "visualization_only",
  ontology_role: "none"
}]->(gn)
SET place.visualization_point = point({latitude: gn.lat, longitude: gn.lng})
// CRITICAL: Flag as non-ontological
WITH place, gn
SET gn:VisualizationOnly,
    gn.warning = "Modern coordinates only. Use Pleiades for historical geography."
```

---

### **R.4.7 PeriodO** (Period Semantics)

**Role**: Authority for named historical periods and temporal intervals

**How to leverage**:
1. **Resolve period labels to PeriodO IDs**
   - Match free-text period names to PeriodO entries
   - Get explicit start-end bounds (often BCE/CE year ranges)
   - Pull spatial scope (where period applies)

2. **Attach Period nodes to temporal envelopes**
   - Events: Period indicates when event could occur
   - Persons: Active period for person's life span
   - Places: Valid period for place existence/usage
   - Concepts: Period when concept was relevant (e.g., "Roman citizenship" only during Roman period)

3. **Check temporal plausibility**
   - Event cannot occur outside its named period bounds
   - Flag violations for review
   - Allow explicit override when justified (e.g., retroactive term use)

4. **Support period-based lensing**
   - "Show only Late Republic events"
   - "Filter to Augustan Age persons"
   - Enable comparative analysis across periods

**Cypher pattern**:
```cypher
// PeriodO period resolution and temporal constraints
MATCH (event:Event {period_label: "Late Republic"})
WITH event
CALL apoc.load.json("http://perio.do/periods.json") YIELD value
WITH event, value.periodCollections AS collections
UNWIND collections AS collection
UNWIND collection.definitions AS period
WHERE period.label CONTAINS "Late Republic" OR period.spatialCoverageDescription CONTAINS "Rome"
WITH event, period
WHERE period.label CONTAINS event.period_label
MERGE (p:Period {periodo_id: period.id})
SET p.label = period.label,
    p.start_year = toInteger(split(period.start.in.value, "-")[0]),
    p.end_year = toInteger(split(period.stop.in.value, "-")[0]),
    p.spatial_scope = period.spatialCoverage,
    p.authority = period.source
CREATE (event)-[:DURING_PERIOD]->(p)
// Validate temporal plausibility
WITH event, p
WHERE event.year < p.start_year OR event.year > p.end_year
SET event.temporal_violations = coalesce(event.temporal_violations, []) + [
  "Event year " + event.year + " outside period bounds [" + p.start_year + ", " + p.end_year + "]"
],
event.requires_review = true
// Enable period-based lensing
WITH event, p
MATCH (person:Person)-[:PARTICIPATED_IN]->(event)
CREATE (person)-[:ACTIVE_IN_PERIOD]->(p)
```

---

### **R.4.8 Getty AAT + LCSH/FAST** (Concepts and Institutions)

**Role**: Deep concept hierarchies (AAT) + library-grade topic hierarchies (LCSH/FAST)

**How to leverage**:

#### **Getty AAT (Art & Architecture Thesaurus)**
1. **Assign to abstract concepts and institutions**
   - For nodes like Concept, Institution, LegalRestriction, Organization
   - Get ontological type (e.g., "colony (settlements)", "senate (legislative bodies)", "taxation (fiscal function)")

2. **Use hierarchical structure**
   - Broader/narrower term navigation
   - Related terms for discovery
   - Scope notes for definition

3. **Enable faceted navigation**
   - "Show all events involving colonial institutions"
   - "Find concepts related to Roman taxation"
   - Support SFA concept spine building

#### **LCSH/FAST (Library of Congress Subject Headings / FAST)**
1. **Bibliographic crosswalk**
   - Already core to your Subject backbone
   - Assign LCSH/FAST to SubjectConcepts for library catalog linking

2. **Authority precedence (from Appendix P)**
   - Tier 1: LCSH/FAST (highest precedence for subjects)
   - Tier 2: LCC/CIP (second tier)
   - Tier 3: Wikidata + domain authorities (specialists)

3. **Agent routing**
   - LCC ranges map to specialist agent scopes
   - LCSH headings trigger facet assignments

**Cypher pattern**:
```cypher
// Getty AAT concept enrichment
MATCH (concept:Concept {label: "Roman Senate"})
WITH concept
CALL apoc.load.json("http://vocab.getty.edu/aat/300025306.json") YIELD value
MERGE (aat:AATConcept {id: "300025306"})
SET aat.term = value.prefLabel,
    aat.scope_note = value.scopeNote,
    aat.broader_terms = [b IN value.broader | b.label],
    aat.narrower_terms = [n IN value.narrower | n.label],
    aat.related_terms = [r IN value.related | r.label]
CREATE (concept)-[:SAME_AS {confidence: 0.90, authority: "Getty AAT"}]->(aat)
SET concept.ontological_type = aat.term,
    concept.hierarchy = aat.broader_terms

// LCSH/FAST subject heading assignment
WITH concept
MATCH (subject:Subject {lcsh_heading: "Rome--Politics and government--265-30 B.C."})
CREATE (concept)-[:HAS_SUBJECT]->(subject)
// Enable faceted query
SET concept.facets = ["GOVERNANCE", "POLITICAL_INSTITUTIONS"]

// Crosswalk for bibliographic discovery
WITH concept, subject
MATCH (work:Work)-[:ABOUT_SUBJECT]->(subject)
CREATE (concept)-[:DOCUMENTED_IN_WORKS]->(work)
```

---

## **R.5 Potential Federation Enhancements**

Building on the six operational federations, these five enhancements represent logical next steps for deepening Chrystallum's multi-authority integration.

### **R.5.1 Evidence Federation**

**Goal**: Unify source documents, passages, citations as first-class Evidence nodes linked to Claims and Reviews

**Current state**: Evidence nodes exist for EDH inscriptions and Trismegistos texts, but not unified across all source types

**Enhancement**:
- Create Evidence node schema for:
  - Literary sources (Livy, Plutarch, Tacitus) with passage-level references
  - Numismatic evidence (coin types, legends, iconography)
  - Archaeological reports (excavation publications, artifact catalogs)
  - Modern scholarly works (with claim extraction)
- Typed evidence relationships:
  - `PRIMARY_EVIDENCE`: Contemporary documents, inscriptions, archaeological material
  - `SECONDARY_NARRATIVE`: Literary sources postdating events
  - `TERTIARY_SYNTHESIS`: Modern scholarly reconstructions
- Enable evidence-based confidence scoring:
  - Claims with primary evidence get +0.20 confidence
  - Multiple corroborating pieces of evidence compound boost
  - Conflicting evidence triggers review workflow

**Example structure**:
```cypher
(claim:Claim)-[:SUPPORTED_BY {weight: 0.85}]->(evidence:Evidence {type: "inscription"})
(claim:Claim)-[:CONTRADICTED_BY {weight: 0.70}]->(evidence2:Evidence {type: "literary_narrative"})
(evidence)-[:CITED_IN]->(work:ModernWork)
(evidence)-[:FOUND_AT]->(place:Place)
(evidence)-[:DATED_TO]->(year:Year)
```

---

### **R.5.2 Identity Federation**

**Goal**: Crosswalk people/places/events across multiple identity authorities (VIAF, GND, Wikidata, LoC)

**Current state**: VIAF used for persons, but no systematic crosswalk across all national authority files

**Enhancement**:
- Create IdentityCluster nodes that aggregate same-entity references across:
  - VIAF (international virtual authority)
  - GND (German National Library)
  - BnF (Bibliothèque nationale de France)
  - LoC (Library of Congress)
  - ISNI (International Standard Name Identifier)
- Confidence-based identity resolution:
  - Same identifier in 3+ authorities = high-confidence match (0.95+)
  - Conflicting identifiers = disambiguation required
  - Single-source identifier = provisional (0.75)
- Enable cross-system queries:
  - "Find all works about Caesar in any national library catalog"
  - "Resolve ambiguous 'Marcus Antonius' via authority crosswalk"

**Example structure**:
```cypher
(person:Person)-[:IDENTITY_CLUSTER]->(cluster:IdentityCluster)
(cluster)-[:VIAF_ID {confidence: 0.90}]->(viaf:ExternalID {value: "12345"})
(cluster)-[:GND_ID {confidence: 0.92}]->(gnd:ExternalID {value: "67890"})
(cluster)-[:LOC_ID {confidence: 0.88}]->(loc:ExternalID {value: "n12345"})
SET cluster.match_confidence = avg([0.90, 0.92, 0.88]) // 0.90
```

---

### **R.5.3 Authority Conflict Federation**

**Goal**: Formal conflict-resolution layer when LCSH/FAST/Wikidata/PeriodO disagree, with stored adjudication rules

**Current state**: Conflicts detected (e.g., via `CONFLICTS_WITH` edges), but resolution is ad-hoc

**Enhancement**:
- Create ConflictResolution nodes capturing:
  - Conflicting authorities (Source A vs. Source B)
  - Conflict type (date_range, place_name, person_identity, etc.)
  - Source values (what each authority claims)
  - Resolution rule (precedence policy, expert adjudication, majority vote)
  - Resolution outcome (chosen value, flagged as unresolvable)
- Implement precedence policies:
  - Subjects: LCSH/FAST > LCC > Wikidata (from Appendix P)
  - Ancient Places: Pleiades > Wikidata > GeoNames
  - Dates: Primary sources (EDH, TM) > literary sources > modern reconstruction
- Enable audit trail:
  - Track all conflicts over time
  - Report authority agreement rates
  - Identify systematic divergences requiring policy updates

**Example structure**:
```cypher
(source_a:Authority {name: "LCSH"})-[:ASSERTS {value: "Roman Republic"}]->(entity)
(source_b:Authority {name: "Wikidata"})-[:ASSERTS {value: "Roman Kingdom"}]->(entity)
CREATE (conflict:ConflictResolution {
  type: "period_name",
  source_a: "LCSH",
  source_a_value: "Roman Republic",
  source_b: "Wikidata",
  source_b_value: "Roman Kingdom",
  resolution_rule: "LCSH_precedence",
  chosen_value: "Roman Republic",
  adjudication_date: date(),
  adjudicator: "system_policy"
})
CREATE (source_a)-[:CONFLICTS_WITH]->(conflict)-[:RESOLVED_BY]->(entity)
```

---

### **R.5.4 Geo-Temporal Federation**

**Goal**: Joint place-time validity layer for historical boundaries and names per period

**Current state**: Pleiades provides temporal validity, PeriodO provides period bounds, but no integrated place-period constraint model

**Enhancement**:
- Create PlacePeriodValidity nodes capturing:
  - Place ID (Pleiades)
  - Period ID (PeriodO)
  - Valid names for that place during that period
  - Boundary changes (e.g., "Mesopotamia" boundaries differ across Persian, Hellenistic, Roman periods)
  - Governance changes (colony → municipium → colonia; client kingdom → province)
- Enable period-aware queries:
  - "Show all places in 'Roman Britain' period" (place exists AND period overlaps AND place under Roman control)
  - "What was 'Constantinople' called in 100 BCE?" → "Byzantium"
  - "Which provinces existed during the Severan Dynasty?"
- Support dynamic historical maps:
  - Render boundaries appropriate to selected period
  - Show place name forms contemporary to period
  - Track expansion/contraction of empires over time

**Example structure**:
```cypher
(place:Place {label: "Constantinople"})-[:VALID_IN_PERIOD]->(ppv:PlacePeriodValidity {
  period_id: "late_antiquity",
  names: ["Constantinople", "Nova Roma"],
  governance: "imperial_capital",
  boundaries: "walls_of_constantine.geojson"
})
(place)-[:VALID_IN_PERIOD]->(ppv2:PlacePeriodValidity {
  period_id: "classical_period",
  names: ["Byzantium"],
  governance: "Greek_colony",
  boundaries: "archaic_byzantium.geojson"
})
// Query with period constraint
MATCH (e:Event)-[:OCCURRED_AT]->(p:Place)-[:VALID_IN_PERIOD]->(ppv)
WHERE e.year >= ppv.period_start AND e.year <= ppv.period_end
RETURN p.label, ppv.names[0] AS period_name // Use name appropriate to event's period
```

---

### **R.5.5 Agent Capability Federation**

**Goal**: Explicit machine-readable mapping from agent scope → LCC ranges/facets/periods for deterministic routing and coverage audits

**Current state**: Agent scopes defined conceptually (in `facet_agent_system_prompts.json`), but not fully machine-readable for automated routing

**Enhancement**:
- Create AgentCapability nodes for each Specialist Facet Agent:
  - LCC call number ranges (e.g., "D51-D90" for Roman History SFA)
  - Facet tags (e.g., ["WARFARE", "GOVERNANCE"] for Military History SFA)
  - Period ranges (e.g., "-500/500" for Classical Period SFA)
  - Geographic scope (e.g., "Mediterranean" for Ancient Mediterranean SFA)
- Implement deterministic routing:
  - Given entity with LCC + facet + period + place → compute best-match SFA
  - Score overlap between entity properties and agent capabilities
  - Route to agent with highest overlap score
- Enable coverage audits:
  - Identify gaps (LCC ranges with no assigned agent)
  - Identify overlaps (multiple agents claiming same scope)
  - Report agent workload (how many entities routed to each agent)
  - Validate agent specialization (check if routed entities truly match declared scope)

**Example structure**:
```cypher
MERGE (sfa:SpecialistFacetAgent {name: "Roman_History_SFA"})
MERGE (cap:AgentCapability {id: "cap_roman_history"})
SET cap.lcc_ranges = ["D51-D59", "D60-D69", "D70-D79"],
    cap.facets = ["GOVERNANCE", "WARFARE", "LEGAL_TOPICS", "ECONOMICS"],
    cap.period_start = -753,
    cap.period_end = 476,
    cap.geographic_scope = ["Italy", "Mediterranean", "Western_Europe"]
CREATE (sfa)-[:HAS_CAPABILITY]->(cap)

// Routing query
MATCH (entity:Entity)
WHERE entity.lcc = "D62" 
  AND "GOVERNANCE" IN entity.facets
  AND entity.year >= -509 AND entity.year <= 27
WITH entity
MATCH (sfa:SpecialistFacetAgent)-[:HAS_CAPABILITY]->(cap:AgentCapability)
WHERE entity.lcc STARTS WITH cap.lcc_ranges[0][0..2] // Match LCC prefix
  AND ANY(facet IN entity.facets WHERE facet IN cap.facets)
  AND entity.year >= cap.period_start AND entity.year <= cap.period_end
WITH entity, sfa, cap, 
     size([f IN entity.facets WHERE f IN cap.facets]) AS facet_overlap
ORDER BY facet_overlap DESC
LIMIT 1
MERGE (entity)-[:ROUTED_TO]->(sfa)
```

---

## **R.6 API Reference Summary**

| Federation | Wikidata Property | Entity Type | API Endpoint | Confidence Impact |
|------------|------------------|-------------|--------------|-------------------|
| **Pleiades** | P1584 | Place | `https://pleiades.stoa.org/places/[ID]/json` | +0.10 temporal validity |
| **Trismegistos People** | P4343 | Person | `https://www.trismegistos.org/person/[ID]` | +0.15 primary source |
| **Trismegistos Geo** | P1958 | Place | `https://www.trismegistos.org/place/[ID]` | +0.10 granular geo |
| **Trismegistos Texts** | P4230 | Text/Document | `https://www.trismegistos.org/text/[ID]` | +0.15 documentary evidence |
| **EDH** | P2192 | Inscription | `https://edh.ub.uni-heidelberg.de/data/api/inscriptions/[ID]` | +0.20 epigraphic evidence |
| **VIAF** | P214 | Person, Work | `https://viaf.org/viaf/[ID]/viaf.json` | +0.10 name authority |
| **GeoNames** | P1566 | Modern Location | `http://api.geonames.org/getJSON?geonameId=[ID]` | N/A (UI-only) |
| **PeriodO** | (label match) | Period | `http://perio.do/[ID]` | +0.10 temporal bounds |
| **Getty AAT** | P1014 | Concept | `http://vocab.getty.edu/aat/[ID].json` | +0.05 hierarchical type |
| **LCSH** | (subject match) | Subject | `https://id.loc.gov/authorities/subjects/[ID]` | Primary (Tier 1) |
| **FAST** | P2163 | Subject | `http://id.worldcat.org/fast/[ID]` | Primary (Tier 1) |
| **Wikidata** | (QID) | Universal | `https://www.wikidata.org/wiki/Special:EntityData/[QID].json` | 0.90 baseline (Layer 2) |

**Usage notes**:
- **Confidence Impact**: Typical boost to base confidence when this authority corroborates entity
- **Wikidata Property**: External ID property used to jump from Wikidata to domain authority
- **API Endpoint**: Template for direct authority access (replace `[ID]` with identifier)
- **"UI-only"**: Authority used for visualization/convenience, not primary ontology

---

## **R.7 Integration with Authority Precedence**

Federation strategy aligns with Chrystallum's tiered authority precedence model (defined in Section 4.4 and Appendix P).

### **R.7.1 Tier 1 (LCSH/FAST): Subject Authority Federation**

**Precedence**: Always check first for SubjectConcepts

**Federation pattern**:
1. Resolve subject string → LCSH heading or FAST topic
2. Pull LCSH hierarchy (broader/narrower terms)
3. Map to LCC call number range for agent routing
4. Cross-reference Wikidata P-codes for international alignment
5. Store mapping with `authority: "LCSH"` and `confidence: 0.95`

**Integration points**:
- **Agent routing**: LCSH/FAST → LCC → Specialist Facet Agent
- **Bibliographic crosswalk**: LCSH enables library catalog integration
- **Facet assignment**: LCSH headings trigger canonical facet tags
- **Conflict resolution**: LCSH overrides Wikidata for subject classification (per Appendix P §P.4)

**Example**:
```cypher
MATCH (entity:Entity {label: "Roman Senate"})
MERGE (lcsh:LCSHHeading {heading: "Rome--Politics and government--510-30 B.C."})
CREATE (entity)-[:HAS_SUBJECT {authority: "LCSH", confidence: 0.95, tier: 1}]->(lcsh)
SET entity.lcc_range = "JC85", // Derived from LCSH
    entity.routed_agent = "Roman_Governance_SFA"
```

---

### **R.7.2 Tier 2 (LCC/CIP): Fallback for Concepts Without LCSH/FAST Coverage**

**Precedence**: Second tier when LCSH/FAST unavailable

**Federation pattern**:
1. Check for LCSH/FAST first (Tier 1)
2. If not found, resolve to LCC call number directly
3. Use CIP (Cataloging in Publication) data for subjects
4. Still route to agents via LCC range
5. Store mapping with `authority: "LCC"` and `confidence: 0.85`

**Integration points**:
- **Gap coverage**: LCC provides broader classification when specific LCSH heading doesn't exist
- **Agent routing**: LCC ranges still enable deterministic agent routing
- **Hierarchy**: LCC provides coarse-grained hierarchy (D = History, D51-D90 = Ancient Rome)

**Example**:
```cypher
MATCH (entity:Entity {label: "Patrician-Plebeian Conflict"})
WHERE NOT EXISTS((entity)-[:HAS_SUBJECT]->(:LCSHHeading))
MERGE (lcc:LCCClass {call_number: "DG231-234"})
CREATE (entity)-[:CLASSIFIED_AS {authority: "LCC", confidence: 0.85, tier: 2}]->(lcc)
SET entity.routed_agent = "Roman_Social_History_SFA"
```

---

### **R.7.3 Tier 3 (Wikidata + Domain Authorities): Specialist Grounding**

**Precedence**: Use Wikidata as router, then jump to domain-specific authorities

**Federation pattern**:
1. Resolve entity → Wikidata QID (Layer 2, confidence 0.90)
2. Follow external ID properties to domain authorities:
   - **People**: VIAF, Trismegistos, PIR/PLRE
   - **Places**: Pleiades, Trismegistos Geo, DARE
   - **Events**: EDH, Trismegistos Texts, PeriodO
   - **Concepts**: Getty AAT, specialized thesauri
3. Domain authority confidence typically 0.90-0.95 (Tier 1 for their domain)
4. Wikidata serves as discovery, domain authority as canonical source

**Integration points**:
- **Two-hop enrichment**: Wikidata → external ID → domain authority graph
- **Cross-domain**: Wikidata enables linking across specialist silos
- **Provenance**: Track both Wikidata and domain authority as sources
- **Conflict resolution**: Domain authority overrides Wikidata when they disagree

**Example**:
```cypher
// Wikidata as router
MATCH (person:Person {label: "Marcus Tullius Cicero"})
MERGE (wd:WikidataEntity {qid: "Q1541"})
CREATE (person)-[:ALIGNED_WITH {confidence: 0.90, layer: 2, tier: 3}]->(wd)

// Jump to VIAF (person authority)
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P214"}]->(viaf_id)
MERGE (viaf:VIAFRecord {id: viaf_id.value})
CREATE (person)-[:SAME_AS {authority: "VIAF", confidence: 0.90, tier: 3}]->(viaf)

// Jump to Trismegistos (documentary evidence)
WITH person, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P4343"}]->(tm_id)
MERGE (tm:TrismegistosPerson {id: tm_id.value})
CREATE (person)-[:SAME_AS {authority: "Trismegistos", confidence: 0.95, tier: 1_for_papyrology}]->(tm)

// Domain authority precedence: TM > VIAF > Wikidata for documentary evidence
SET person.documentary_confidence = 0.95 // TM provides primary source grounding
```

---

### **R.7.4 Crosswalk Pattern: Use Wikidata P-codes to Route to Domain Authority, Then Enrich Backward**

**Key principle**: Wikidata external ID properties (P-codes) function as federation routing keys, not final data sources.

**Crosswalk workflow**:
1. **Forward routing**: Entity → Wikidata QID → P-code → domain authority
2. **Data enrichment**: Pull canonical data from domain authority
3. **Backward propagation**: Enrich original entity with domain authority data
4. **Provenance tracking**: Store both Wikidata and domain source metadata
5. **Conflict handling**: When Wikidata and domain authority disagree, flag for resolution using precedence rules

**Crosswalk example (Place federation)**:
```cypher
// Step 1: Forward routing via Wikidata
MATCH (place:Place {label: "Tarraco"})
MERGE (wd:WikidataEntity {qid: "Q15695"})
CREATE (place)-[:ALIGNED_WITH {role: "discovery"}]->(wd)

// Step 2: Extract P1584 (Pleiades ID)
WITH place, wd
MATCH (wd)-[:HAS_EXTERNAL_ID {property: "P1584"}]->(pleiades_id)

// Step 3: Enrich from Pleiades (canonical ancient place authority)
WITH place, pleiades_id.value AS pid
CALL apoc.load.json("https://pleiades.stoa.org/places/" + pid + "/json") YIELD value
MERGE (pleiades:PleiadesPlace {id: pid})
SET pleiades.canonical_names = value.names,
    pleiades.temporal_validity = value.temporalRange,
    pleiades.coordinates = value.reprPoint
CREATE (place)-[:SAME_AS {authority: "Pleiades", confidence: 0.95}]->(pleiades)

// Step 4: Backward propagation to original Place node
SET place.ancient_names = [n IN value.names WHERE n.language IN ['la', 'grc'] | n.nameTransliterated],
    place.valid_periods = value.periods,
    place.primary_authority = "Pleiades",
    place.enrichment_date = datetime()

// Step 5: Conflict detection (if Wikidata and Pleiades disagree)
WITH place, wd, pleiades
WHERE wd.label <> pleiades.canonical_names[0]
CREATE (conflict:ConflictResolution {
  type: "place_name",
  wikidata_value: wd.label,
  pleiades_value: pleiades.canonical_names[0],
  resolution: "Pleiades_precedence",
  chosen_value: pleiades.canonical_names[0]
})
SET place.label = pleiades.canonical_names[0] // Pleiades wins per precedence rule
```

**Crosswalk pattern advantages**:
- **Leverages Wikidata's breadth** for discovery and initial linkage
- **Respects domain authorities' depth** for canonical data
- **Traceable provenance** with explicit routing path
- **Conflict-aware** with adjudication rules
- **Bidirectional enrichment**: Wikidata improves coverage, domain authorities improve quality

---

## **R.8 Source Files**

This appendix synthesizes content from the following Federation layer documentation:

1. **[Archive/Federation/2-16-26-FederationCandidates.md](Archive/Federation/2-16-26-FederationCandidates.md)** (170 lines, archived)
   - Federation usage patterns for 8 major authorities
   - Role → How to leverage structure for each federation
   - Stacked evidence ladder principle

2. **[Archive/Federation/FederationUsage.txt](Archive/Federation/FederationUsage.txt)** (241 lines, archived)
   - Detailed stacked evidence ladder for People, Places, Events
   - Tier-by-tier enrichment patterns
   - Confidence rules and attestation strength matrix
   - Operationalization guidance for ingestion, validation, and lensing phases

3. **[Archive/Federation/2-12-26-federations.md](Archive/Federation/2-12-26-federations.md)** (archived)
   - 6 current operational federations
   - 5 potential federation enhancements
   - Wikidata as "federation broker, not final authority" principle
   - Federation architecture: two-hop enrichment, typed edges, Layer 2 positioning

4. **[Federation/Federation Impact Report_ Chrystallum Data Targets.md](Federation/Federation Impact Report_ Chrystallum Data Targets.md)** (not merged)
   - Detailed API reference with endpoints, parameters, response formats
   - Kept as separate technical reference for implementation
   - Not duplicated here to avoid excessive length

---

## **R.9 Related Sections**

Federation strategy integrates with multiple existing architecture components:

- **Section 4.4: Multi-Authority Model**  
  Defines Tier 1/2/3 precedence policy that governs federation conflict resolution

- **Appendix K: Wikidata Integration Patterns**  
  Detailed patterns for Wikidata as discovery layer and external ID routing

- **Appendix L: CIDOC-CRM Integration Guide**  
  Relationship vocabulary aligned with CIDOC E-classes and P-codes, used in federation edges

- **Appendix O (§O.6): Authority Precedence for Training Resources**  
  Training pipeline respects same LCSH > LCC > Wikidata hierarchy used in federation

- **Appendix P (§P.4): Authority Precedence Integration with CIDOC-CRM**  
  Formal precedence rules: LCSH/FAST (Tier 1) > LCC/CIP (Tier 2) > Wikidata + domain authorities (Tier 3)

- **Appendix Q: Operational Modes & Agent Orchestration**  
  Agent routing depends on LCC/facet/period federation for deterministic specialist assignment

---

## **R.10 API Implementation Guide**

This section provides **practical code examples** for accessing each federation's API endpoints, based on existing patterns in the codebase.

### **R.10.1 General Implementation Principles**

- Use `requests` library with proper headers (User-Agent identification)
- Set timeouts (30s for entity fetches, 60s for bulk operations)
- Implement exponential backoff for rate limiting (429 responses)
- Cache responses locally (Redis or file-based for batch operations)
- Log all API errors with traceback for debugging

---

### **R.10.2 Wikidata API Access**

Complete Python example based on `scripts/agents/facet_agent_framework.py` (lines 920-1020):

```python
import requests
from typing import Optional, Dict, Any

def fetch_wikidata_entity(qid: str) -> Optional[Dict[str, Any]]:
    """Fetch Wikidata entity with all claims."""
    API_URL = "https://www.wikidata.org/w/api.php"
    
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": qid,
        "languages": "en",
        "props": "labels|descriptions|claims|aliases",
    }
    
    headers = {"User-Agent": "Chrystallum/1.0 (research project)"}
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        entity = data.get("entities", {}).get(qid)
        if not entity or "missing" in entity:
            return None
            
        return {
            "qid": qid,
            "label": entity.get("labels", {}).get("en", {}).get("value"),
            "description": entity.get("descriptions", {}).get("en", {}).get("value"),
            "claims": entity.get("claims", {})
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikidata entity {qid}: {e}")
        return None
```

**Key Points:**
- Action: `wbgetentities` for entity fetch, `wbsearchentities` for search
- Rate limit: No official limit, but be respectful (1-2 req/sec recommended)
- Authentication: Not required for read operations
- Bulk: Use pipe-separated QIDs: `ids=Q1048|Q1056|Q2277`

---

### **R.10.3 Pleiades API Access**

```python
def fetch_pleiades_place(pleiades_id: str) -> Optional[Dict[str, Any]]:
    """Fetch Pleiades place with coordinates and temporal scope."""
    API_URL = f"https://pleiades.stoa.org/places/{pleiades_id}/json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            "pleiades_id": pleiades_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "reprPoint": data.get("reprPoint"),  # [lon, lat]
            "names": data.get("names", []),
            "timeperiods": data.get("timeperiods", []),
            "connections": data.get("connections", [])
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pleiades {pleiades_id}: {e}")
        return None
```

**Key Points:**
- No API key required
- Rate limit: ~1 req/sec polite crawling
- Bulk download: https://atlantides.org/downloads/pleiades/dumps/ (CSV/JSON dumps updated monthly)
- GeoJSON available: append `/json` to place URL

---

### **R.10.4 VIAF API Access**

```python
def fetch_viaf_authority(viaf_id: str) -> Optional[Dict[str, Any]]:
    """Fetch VIAF authority record with name forms."""
    API_URL = f"https://viaf.org/viaf/{viaf_id}/viaf.json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # VIAF JSON structure is deeply nested
        main_headings = data.get("mainHeadings", {}).get("data", [])
        
        return {
            "viaf_id": viaf_id,
            "name_forms": [h.get("text") for h in main_headings],
            "sources": data.get("sources", {}).get("source", []),
            "birth_date": data.get("birthDate"),
            "death_date": data.get("deathDate")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching VIAF {viaf_id}: {e}")
        return None
```

**Key Points:**
- No API key required
- Multiple formats: `/viaf.json`, `/viaf.xml`, `/rdf.xml`
- Search API: `http://viaf.org/viaf/search?query=...&httpAccept=application/json`
- Rate limit: Not published; use 1 req/sec

---

### **R.10.5 GeoNames API Access (Requires Free Registration)**

```python
def fetch_geonames_place(geonames_id: str, username: str) -> Optional[Dict[str, Any]]:
    """Fetch GeoNames place with modern coordinates."""
    API_URL = "http://api.geonames.org/getJSON"
    
    params = {
        "geonameId": geonames_id,
        "username": username  # Required: register at geonames.org
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            "geonames_id": geonames_id,
            "name": data.get("name"),
            "toponymName": data.get("toponymName"),
            "lat": data.get("lat"),
            "lng": data.get("lng"),
            "countryCode": data.get("countryCode"),
            "adminName1": data.get("adminName1"),  # State/province
            "featureClass": data.get("fcl"),
            "featureCode": data.get("fcode")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GeoNames {geonames_id}: {e}")
        return None
```

**Key Points:**
- **Authentication required**: Free username registration at http://www.geonames.org/login
- Rate limit: 1000 credits/hour, 30,000/day (free tier)
- Premium tier: 80,000/day ($200/year)
- Bulk download: http://download.geonames.org/export/dump/ (tab-delimited files)

---

### **R.10.6 PeriodO API Access**

```python
def fetch_periodo_periods(search_term: str = None) -> Optional[Dict[str, Any]]:
    """Fetch PeriodO period definitions."""
    API_URL = "http://n2t.net/ark:/99152/p0d.json"
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # PeriodO returns entire dataset; filter locally
        period_collections = data.get("periodCollections", {})
        
        if search_term:
            # Simple label matching (implement proper search as needed)
            matches = []
            for coll_id, collection in period_collections.items():
                for period_id, period in collection.get("definitions", {}).items():
                    label = period.get("label", "")
                    if search_term.lower() in label.lower():
                        matches.append({
                            "periodo_id": f"{coll_id}#{period_id}",
                            "label": label,
                            "spatialCoverage": period.get("spatialCoverage", []),
                            "start": period.get("start", {}),
                            "stop": period.get("stop", {})
                        })
            return {"periods": matches}
        
        return {"periodCollections": period_collections}
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PeriodO: {e}")
        return None
```

**Key Points:**
- No API key required
- Entire dataset in single JSON file (~15MB; cache locally)
- No rate limit (dataset updated infrequently)
- Period URIs: `http://n2t.net/ark:/99152/p0{collection_id}#{period_id}`

---

### **R.10.7 Trismegistos, EDH, Getty AAT Access**

**Trismegistos** - No public API; bulk data via:
- https://www.trismegistos.org/downloads.php
- CSV exports for TMPeople, TMGeo, TMTexts
- Direct database queries not supported; must use exports

**EDH (Epigraphic Database Heidelberg)**:
```python
def search_edh_inscriptions(search_term: str, max_results: int = 20) -> Optional[List[Dict]]:
    """Search EDH inscriptions."""
    API_URL = "https://edh.ub.uni-heidelberg.de/data/api/inscriptions/search"
    
    params = {
        "text": search_term,
        "limit": max_results
    }
    
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return data.get("items", [])
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching EDH: {e}")
        return None
```

**Getty AAT** - SPARQL endpoint (advanced):
- Endpoint: `http://vocab.getty.edu/sparql`
- Requires SPARQL query language
- Easier: Use Linked Open Data URIs: `http://vocab.getty.edu/aat/{concept_id}.json`

---

### **R.10.8 Rate Limiting & Caching Strategy**

```python
import time
from functools import wraps

def rate_limit(calls_per_second: float = 1.0):
    """Decorator to rate-limit API calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=1.0)
def fetch_wikidata_entity_throttled(qid: str) -> Optional[Dict]:
    return fetch_wikidata_entity(qid)
```

**Caching with file-based storage**:
```python
import json
from pathlib import Path

def cache_api_response(cache_dir: str = "./federation_cache"):
    """Decorator to cache API responses to disk."""
    Path(cache_dir).mkdir(exist_ok=True)
    
    def decorator(func):
        @wraps(func)
        def wrapper(entity_id: str, *args, **kwargs):
            cache_file = Path(cache_dir) / f"{func.__name__}_{entity_id}.json"
            
            if cache_file.exists():
                with open(cache_file) as f:
                    return json.load(f)
            
            result = func(entity_id, *args, **kwargs)
            
            if result:
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
            
            return result
        return wrapper
    return decorator

@cache_api_response()
@rate_limit(calls_per_second=1.0)
def fetch_pleiades_place_cached(pleiades_id: str) -> Optional[Dict]:
    return fetch_pleiades_place(pleiades_id)
```

---

### **R.10.9 Configuration Management**

Store API credentials in environment variables or config file:

```python
# config.py
import os
from pathlib import Path

class FederationConfig:
    # GeoNames (requires free registration)
    GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "")
    
    # User-Agent for all requests
    USER_AGENT = "Chrystallum/1.0 (historical research; contact@example.com)"
    
    # Rate limits (requests per second)
    RATE_LIMITS = {
        "wikidata": 2.0,
        "pleiades": 1.0,
        "viaf": 1.0,
        "geonames": 0.5,  # Conservative for free tier
        "edh": 1.0
    }
    
    # Cache directory
    CACHE_DIR = Path(__file__).parent / "data" / "federation_cache"
    
    # Timeouts (seconds)
    DEFAULT_TIMEOUT = 30
    BULK_TIMEOUT = 60
```

---

### **R.10.10 Error Handling Pattern**

```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FederationAPIError(Exception):
    """Base exception for federation API errors."""
    pass

def safe_fetch_with_retry(
    fetch_func,
    entity_id: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Optional[Dict[str, Any]]:
    """Fetch with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            result = fetch_func(entity_id)
            if result:
                return result
            
            logger.warning(f"Empty result for {entity_id} (attempt {attempt + 1})")
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {entity_id} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(backoff_factor ** attempt)
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = backoff_factor ** (attempt + 1)
                logger.warning(f"Rate limited; waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                break
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    
    return None
```

---

### **R.10.11 Integration with Neo4j Write Pattern**

```python
def enrich_node_from_federation(
    neo4j_driver,
    node_id: str,
    qid: str
) -> Dict[str, Any]:
    """Fetch Wikidata, enrich with federations, write to Neo4j."""
    
    # 1. Fetch Wikidata entity
    entity = fetch_wikidata_entity(qid)
    if not entity:
        return {"status": "error", "message": "Entity not found"}
    
    # 2. Extract federation IDs from Wikidata claims
    claims = entity.get("claims", {})
    pleiades_id = extract_claim_value(claims, "P1584")  # Pleiades
    viaf_id = extract_claim_value(claims, "P214")  # VIAF
    geonames_id = extract_claim_value(claims, "P1566")  # GeoNames
    
    # 3. Fetch from federations (with caching & rate limiting)
    enrichments = {}
    
    if pleiades_id:
        enrichments["pleiades"] = fetch_pleiades_place_cached(pleiades_id)
    
    if viaf_id:
        enrichments["viaf"] = fetch_viaf_authority(viaf_id)
    
    if geonames_id:
        enrichments["geonames"] = fetch_geonames_place(
            geonames_id, 
            FederationConfig.GEONAMES_USERNAME
        )
    
    # 4. Write to Neo4j with federation metadata
    with neo4j_driver.session() as session:
        result = session.execute_write(
            lambda tx: write_enriched_node(tx, node_id, entity, enrichments)
        )
    
    return result

def write_enriched_node(tx, node_id, entity, enrichments):
    """Cypher write with federation properties."""
    cypher = """
    MATCH (n {node_id: $node_id})
    SET n.wikidata_qid = $qid,
        n.wikidata_label = $label,
        n.wikidata_description = $description,
        n.pleiades_id = $pleiades_id,
        n.viaf_id = $viaf_id,
        n.geonames_id = $geonames_id,
        n.federation_enriched = datetime(),
        n.federation_sources = $sources
    RETURN n
    """
    
    params = {
        "node_id": node_id,
        "qid": entity.get("qid"),
        "label": entity.get("label"),
        "description": entity.get("description"),
        "pleiades_id": enrichments.get("pleiades", {}).get("pleiades_id"),
        "viaf_id": enrichments.get("viaf", {}).get("viaf_id"),
        "geonames_id": enrichments.get("geonames", {}).get("geonames_id"),
        "sources": ["wikidata", "pleiades", "viaf", "geonames"]
    }
    
    result = tx.run(cypher, params)
    return result.single()
```

---

### **R.10.12 Existing Implementation Files**

Current implementations in codebase:
- `scripts/agents/facet_agent_framework.py` (lines 920-1020): Wikidata entity fetching
- `Subjects/CIP/2-11-26-subjects_broader_narrower.py`: Wikidata API patterns
- `Subjects/index_scan.py`: Wikidata search and entity retrieval
- `scripts/reference/agent_training_pipeline.py`: Wikidata federation integration

**Next Steps for Production:**
1. Centralize federation API logic in `scripts/federation/` module
2. Add pytest unit tests with mocked API responses
3. Implement Redis caching for production (file-based for development)
4. Add monitoring/logging for API failures and rate limit tracking
5. Document API key acquisition process in `md/Guides/SETUP_GUIDE.md`

---

**(End of Appendix R)**

---

## **APPENDIX S: BabelNet Lexical Authority Integration**

### **S.1 Positioning and Layer Architecture**

BabelNet operates as a **multilingual lexical layer** positioned at **Layer 2.5** in the Chrystallum architecture:

- **Layer 1:** Core ontology (SubjectConcept nodes, Claims, Relationships)
- **Layer 2:** Federation authorities (Wikidata, LCSH, FAST, TGN, Pleiades)
- **Layer 2.5:** BabelNet (lexical/semantic enrichment)
- **Layer 3:** Facet Authority (SFAs generating domain-specific ontologies)

**Architectural Position:**
- **Not a primary fact authority** (Wikidata holds factual ground truth)
- **Lexical sidecar** for multilingual labels, glosses, synsets, and cross-language entity linking
- **Semantic enrichment** for term disambiguation and synonym expansion
- **Cross-reference hub** linking WordNet, Wikipedia, Wikidata, and language-specific resources

**Key Distinction:**
- Wikidata provides **factual claims** (dates, locations, relationships) → confidence 0.90
- BabelNet provides **lexical/semantic context** (multilingual labels, senses, glosses) → confidence 0.75-0.85
- Combined alignment (BabelNet synset + Wikidata QID) → confidence boost +0.05

---

### **S.2 Core Use Cases**

#### **S.2.1 SubjectConcept Lexical Enrichment**

**Scenario:** A SubjectConcept node for "Roman Republic" needs multilingual labels and glosses.

**Workflow:**
1. SubjectConcept has `wikidata_id: Q17167`, `label: "Roman Republic"`, `facet: "political"`
2. Call BabelNet API with English label + QID to retrieve synset
3. Extract multilingual labels (Latin: *Res publica Romana*, French: *République romaine*, etc.)
4. Store on SubjectConcept:
   - `babelnet_id: bn:00068294n`
   - `alt_labels: {"la": "Res publica Romana", "fr": "République romaine", ...}`
   - `glosses: {"en": "ancient Roman state...", "fr": "état romain ancien...", ...}`
5. Enrich SFA prompts with multilingual vocabulary for cross-language reasoning

**Benefits:**
- Enhanced query matching across languages
- Richer context for LLM-based clustering and classification
- Support for non-English historical sources

#### **S.2.2 Cross-Lingual Entity Linking**

**Scenario:** User query in French: *"République romaine et ses consuls"*

**Workflow:**
1. Parse query, extract surface form: *"République romaine"*
2. Query BabelNet for French lexicalization → retrieves BabelNet synset `bn:00068294n`
3. Map synset to Wikidata QID (BabelNet includes Wikidata links) → Q17167
4. Retrieve SubjectConcept node with `wikidata_id: Q17167`
5. Execute graph query with language-agnostic identifier

**Benefits:**
- Normalize cross-language queries to canonical identifiers
- Support multilingual research workflows
- Expand retrieval with synonyms and related terms

#### **S.2.3 Facet-Aware Sense Disambiguation**

**Scenario:** Disambiguate "legion" in military vs. religious contexts.

**Workflow:**
1. SFA encounters term "legion" in text extraction
2. Query BabelNet → returns multiple synsets:
   - `bn:00051234n`: military unit (hypernym: armed forces)
   - `bn:00051235n`: large number (hypernym: multitude)
   - `bn:00051236n`: demon (hypernym: evil spirit)
3. **Facet filter:** Military SFA prioritizes military synset based on hypernym match
4. Store chosen `babelnet_id` on SubjectConcept as part of lexical profile
5. Use synset to inform CIDOC-CRM class alignment (E74 Group for military unit)

**Benefits:**
- Reduce ambiguity in multi-sense terms
- Align lexical choices with ontology structure
- Provide explainable reasoning for sense selection

#### **S.2.4 Graph-RAG Over SubjectConcept + BabelNet**

**Scenario:** Discover conceptual neighbors for "dictator" to propose new SubjectConcepts.

**Workflow:**
1. SubjectConcept exists for "Dictator (Roman)"
2. Query BabelNet synset relations: hypernyms (*magistrate*, *ruler*), hyponyms (*tyrant*, *autocrat*)
3. For each related synset, check if corresponding SubjectConcept exists
4. Propose new shell nodes for missing concepts (e.g., "Roman Magistrate")
5. Submit proposals through Subject Ontology Proposal validation pipeline

**Benefits:**
- Semi-automated ontology expansion
- Discover gaps in subject coverage
- Maintain lexical coherence across related concepts

---

### **S.3 Implementation Patterns**

#### **S.3.1 API Integration Pattern**

BabelNet follows the same federation API patterns documented in **Appendix R.10**.

**Cross-Reference:** See [Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration) for:
- R.10.1: Generic API request pattern with retry logic
- R.10.2: Wikidata API example (similar structure for BabelNet)
- R.10.9: Error handling patterns
- R.10.10: Rate limiting and caching strategies

#### **S.3.2 BabelNet API Access Example**

```python
import requests
from typing import Optional, Dict
import os

def fetch_babelnet_synset(synset_id: str, api_key: str = None) -> Optional[Dict]:
    """
    Fetch BabelNet synset with multilingual labels and glosses.
    
    Args:
        synset_id: BabelNet synset ID (e.g., 'bn:00068294n')
        api_key: BabelNet API key (defaults to BABELNET_API_KEY env var)
    
    Returns:
        JSON response with synset data, or None on error
    """
    api_key = api_key or os.getenv("BABELNET_API_KEY")
    if not api_key:
        raise ValueError("BabelNet API key required")
    
    API_URL = "https://babelnet.io/v9/getSynset"
    params = {
        "id": synset_id,
        "key": api_key,
        "targetLang": "EN,IT,FR,DE,ES,LA"  # Multilingual support
    }
    headers = {"User-Agent": "Chrystallum/1.0"}
    
    try:
        # Standard pattern from R.10.1
        response = requests.get(
            API_URL, 
            params=params, 
            headers=headers, 
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limit exceeded - see R.10.10 for retry logic
            print(f"Rate limit exceeded: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"Timeout fetching synset {synset_id}")
        return None
    except Exception as e:
        print(f"Error fetching BabelNet synset: {e}")
        return None

def enrich_node_from_babelnet(node_id: str, wikidata_qid: str, label: str) -> Dict:
    """
    Enrich SubjectConcept node with BabelNet lexical data.
    
    Workflow:
    1. Query BabelNet for synsets matching label + QID
    2. Extract multilingual labels, glosses, synset relations
    3. Store babelnet_id, alt_labels, glosses on node
    4. Return enrichment metadata with confidence score
    """
    # Search BabelNet by Wikidata QID
    api_key = os.getenv("BABELNET_API_KEY")
    search_url = "https://babelnet.io/v9/getIds"
    params = {
        "lemma": label,
        "searchLang": "EN",
        "key": api_key,
        "source": f"WIKIDATA:{wikidata_qid}"
    }
    
    response = requests.get(search_url, params=params, timeout=30)
    if response.status_code == 200:
        synset_ids = response.json()
        if synset_ids:
            # Fetch full synset data for first match
            synset_data = fetch_babelnet_synset(synset_ids[0]["id"], api_key)
            if synset_data:
                return {
                    "babelnet_id": synset_ids[0]["id"],
                    "alt_labels": extract_multilingual_labels(synset_data),
                    "glosses": extract_glosses(synset_data),
                    "confidence": 0.80,  # Base confidence for BabelNet alignment
                    "source": "BabelNet v9"
                }
    
    return {"confidence": 0.0, "error": "No synset found"}

def extract_multilingual_labels(synset_data: Dict) -> Dict[str, str]:
    """Extract multilingual labels from BabelNet synset response."""
    labels = {}
    for sense in synset_data.get("senses", []):
        lang = sense.get("language", "")
        lemma = sense.get("properties", {}).get("fullLemma", "")
        if lang and lemma:
            labels[lang] = lemma
    return labels

def extract_glosses(synset_data: Dict) -> Dict[str, str]:
    """Extract glosses (short definitions) from BabelNet synset."""
    glosses = {}
    for gloss in synset_data.get("glosses", []):
        lang = gloss.get("language", "")
        text = gloss.get("gloss", "")
        if lang and text:
            glosses[lang] = text
    return glosses
```

#### **S.3.3 Caching and Rate Limiting**

**BabelNet API Limits:**
- **Free tier:** 1,000 requests/day
- **Paid subscription:** 10,000-100,000 requests/day (tiered pricing)

**Caching Strategy** (see Appendix R.10.10):
- Cache synset responses in Redis with 30-day TTL
- Use file-based cache for development: `cache/babelnet/{synset_id}.json`
- Cache key: `babelnet:synset:{synset_id}`

**Implementation:**
```python
import json
from pathlib import Path

def get_cached_synset(synset_id: str) -> Optional[Dict]:
    cache_path = Path(f"cache/babelnet/{synset_id}.json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return None

def cache_synset(synset_id: str, data: Dict):
    cache_path = Path(f"cache/babelnet/{synset_id}.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=2))
```

---

### **S.4 Confidence Scoring for BabelNet-Derived Properties**

#### **S.4.1 Base Confidence Levels**

**BabelNet Synset Alignment:** 0.75-0.85 confidence
- **Rationale:** BabelNet is a lexical/semantic authority, not a factual authority
- **Lower than Wikidata (0.90)** because:
  - Lexical relationships are more subjective than factual claims
  - Synset boundaries and sense distinctions vary by resource
  - Multilingual alignments introduce translation ambiguity

**Confidence Ranges:**
- **0.85:** BabelNet synset with Wikidata QID alignment + high statement count
- **0.80:** BabelNet synset with Wikidata QID alignment (standard case)
- **0.75:** BabelNet synset without Wikidata alignment (WordNet/Wikipedia only)

#### **S.4.2 Confidence Boost Patterns**

**BabelNet + Wikidata Alignment:** +0.05 confidence boost
- When BabelNet synset includes `WIKIDATA:Q12345` link and QID matches existing SubjectConcept
- Example: Base 0.80 → 0.85 with QID confirmation

**Multi-Source Lexical Convergence:** +0.10 confidence boost
- When BabelNet synset aligns with:
  - Wikidata QID
  - LCSH preferred term
  - FAST heading
- Example: Base 0.75 → 0.85 with triple alignment

**Facet-Specific Disambiguation:** +0.05 confidence boost
- When chosen synset hypernym matches facet domain
- Example: Military SFA selects military synset for "legion" → +0.05

#### **S.4.3 Confidence Degradation**

**Ambiguous Synset Selection:** -0.10 confidence penalty
- Multiple candidate synsets with similar scores
- No clear facet-based discriminator

**Missing Wikidata Link:** -0.05 confidence penalty
- BabelNet synset lacks Wikidata connection
- Reliance on WordNet/Wikipedia only

#### **S.4.4 Example Confidence Calculations**

**Scenario 1: High-Confidence Alignment**
- SubjectConcept: "Roman Republic" (wikidata_id: Q17167)
- BabelNet synset: bn:00068294n
- BabelNet includes: WIKIDATA:Q17167 link
- Synset has 15+ language lexicalizations
- **Confidence:** 0.80 (base) + 0.05 (QID match) = **0.85**

**Scenario 2: Medium-Confidence Alignment**
- SubjectConcept: "Roman Legion"
- BabelNet synset: bn:00051234n (military unit)
- Multiple candidate synsets, facet filter applied
- **Confidence:** 0.80 (base) + 0.05 (facet match) = **0.85**

**Scenario 3: Low-Confidence Alignment**
- SubjectConcept: "Ancient Assembly"
- BabelNet synset: bn:00012345n
- No Wikidata link, ambiguous sense
- **Confidence:** 0.75 (base) - 0.05 (no QID) - 0.10 (ambiguous) = **0.60**

---

### **S.5 Integration with SFA Workflow**

#### **S.5.1 Phase 3.5: Lexical Enrichment (Optional)**

**Position:** After Initialize Mode (Phase 3), before Ontology Proposal (Phase 4)

**Workflow:**
1. SFA completes Initialize Mode, creates SubjectConcept nodes with Wikidata enrichment
2. **Lexical Enrichment Phase (Optional):**
   - For each new SubjectConcept with `wikidata_id`:
     - Call `enrich_node_from_babelnet(node_id, wikidata_qid, label)`
     - Store `babelnet_id`, `alt_labels`, `glosses` on node properties
     - Log enrichment with confidence score
   - Skip nodes without Wikidata QID (cannot reliably align)
3. Proceed to Ontology Proposal with enriched lexical context

**Benefits:**
- Richer multilingual labels for clustering and classification
- Enhanced LLM prompts with glosses and synonyms
- Cross-language support for future queries

**Configuration:**
```python
# In facet_agent_framework.py
if config.get("babelnet_enrichment_enabled", False):
    for node in new_nodes:
        if node.get("wikidata_id"):
            enrichment = enrich_node_from_babelnet(
                node["id"], 
                node["wikidata_id"], 
                node["label"]
            )
            if enrichment.get("confidence", 0) >= 0.75:
                update_node_properties(node["id"], enrichment)
```

#### **S.5.2 Phase 5: Training Mode Disambiguation**

**Use Case:** Polysemous term disambiguation during claim generation

**Scenario:** Military SFA encounters "cohort" in text:
- Could mean: military unit, statistical group, companion group

**Workflow:**
1. Extract term "cohort" from historical text
2. Query BabelNet for synsets matching "cohort"
3. **Facet-aware filtering:**
   - Military SFA prioritizes synset with hypernym "military unit"
   - Filters out statistical/demographic senses
4. Store chosen `babelnet_id` on new SubjectConcept or claim metadata
5. Use synset to guide CIDOC-CRM class assignment

**Benefits:**
- Reduce ambiguity in extracted terms
- Align lexical choices with domain expertise
- Provide explainable term selection

**Cross-Reference:** See **Appendix T.3** (Training Mode workflow) for implementation details.

---

### **S.6 Configuration and Authentication**

#### **S.6.1 API Key Management**

**BabelNet API requires paid subscription** (after free tier exhaustion)

**Environment Variable:**
```bash
export BABELNET_API_KEY="your_api_key_here"
```

**Configuration in config.py:**
```python
BABELNET_CONFIG = {
    "api_key": os.getenv("BABELNET_API_KEY"),
    "base_url": "https://babelnet.io/v9",
    "rate_limit": 1000,  # requests/day for free tier
    "timeout": 30,  # seconds
    "cache_enabled": True,
    "cache_ttl": 2592000,  # 30 days
}
```

#### **S.6.2 Rate Limit Tracking**

**Free Tier:** 1,000 requests/day
- Track daily usage in Redis: `babelnet:usage:{date}`
- Implement circuit breaker when approaching limit

**Implementation:**
```python
import redis
from datetime import date

def check_rate_limit() -> bool:
    r = redis.Redis()
    today = date.today().isoformat()
    key = f"babelnet:usage:{today}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 86400)  # 24 hours
    return count <= 1000  # Free tier limit
```

#### **S.6.3 Fallback Strategies**

**When BabelNet Unavailable:**
1. **Use cached synsets** for previously seen terms
2. **Skip lexical enrichment** for new terms (graceful degradation)
3. **Fall back to Wikidata labels** only (mono-lingual)
4. **Log skipped enrichments** for manual review

---

### **S.7 Cross-References**

**Related Appendices:**
- **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#r10-api-implementation-patterns):** Federation API patterns (request structure, error handling, caching)
- **[Appendix T](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-t-subject-facet-agent-workflow---day-in-the-life):** SFA workflow integration points (Phase 3.5, Phase 5 disambiguation)
- **[Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf):** CIDOC-CRM alignment for lexical concepts (E55 Type for BabelNet synsets)
- **[Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns):** Wikidata integration patterns (primary fact authority)
- **[Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration):** Operational Modes (Initialize, Training)

**Implementation Files:**
- `scripts/federation/babelnet_client.py`: BabelNet API client (to be created)
- `scripts/agents/facet_agent_framework.py`: SFA orchestration with BabelNet integration
- `config.py`: BabelNet configuration settings

**External Resources:**
- BabelNet API Documentation: https://babelnet.io/guide
- BabelNet Paper (ACM 2012): https://dl.acm.org/doi/10.5555/2887533.2887534
- Multilingual Linked Data Report: http://www.w3.org/2015/09/bpmlod-reports/multilingual-dictionaries/

---

**(End of Appendix S)**

---

## **APPENDIX T: Subject Facet Agent Workflow - "Day in the Life"**

A newly instantiated SubjectFacetAgent (SFA) follows a structured workflow that ensures disciplined knowledge construction through schema introspection, state loading, federation bootstrap, ontology proposal, and training. This appendix documents the complete lifecycle of an SFA from instantiation to claim generation.

---

### **T.1 Wake-Up and Self-Orientation**

#### **T.1.1 Agent Instantiation**

**Factory Pattern:**
```python
from scripts.agents.facet_agent_framework import FacetAgentFactory

factory = FacetAgentFactory()
agent = factory.get_agent("military")  # or political, religious, economic, etc.
```

**Supported Facets:**
- `military`: Military units, campaigns, tactics, leadership
- `political`: Governments, institutions, offices, political events
- `religious`: Beliefs, practices, institutions, figures
- `economic`: Trade, currency, production, labor
- `cultural`: Arts, literature, daily life, customs
- `geographic`: Places, regions, territories, boundaries

#### **T.1.2 Schema Introspection (Step 1)**

**Purpose:** Learn "what is allowed" at the schema level before touching data.

**Actions:**
1. **Node schema introspection:**
   ```python
   schema = agent.introspect_node_label("SubjectConcept")
   # Returns: required properties, optional properties, tier, validation rules
   ```

2. **Layer 2.5 property discovery:**
   ```python
   properties = agent.get_layer25_properties()
   # Returns: P31 (instance of), P279 (subclass of), P361 (part of), etc.
   # These are the allowed Wikidata properties for hierarchy traversal
   ```

3. **Relationship discovery:**
   ```python
   relationships = agent.discover_relationships_between("Human", "Event")
   # Returns: PARTICIPATED_IN, COMMANDED, WITNESSED, etc.
   ```

**Output:** SFA now knows:
- Required properties for SubjectConcept nodes
- Valid Wikidata properties for federation
- Allowed relationship types for claims

**Cross-Reference:** See [Appendix M](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-m-identifier-safety-reference) for schema validation patterns.

---

### **T.2 Session Start: Load Current State**

#### **T.2.1 State Introspection (Step 2)**

**Purpose:** Learn "what already exists" and "what I have done before."

**Actions:**
```python
context = agent.get_session_context()
# Returns:
# - sample_nodes: Recent SubjectConcept nodes in this facet
# - sample_relationships: Recent relationships involving these nodes
# - pending_claims: Claims awaiting validation
# - agent_history: This agent's past contributions and promotion rate
# - meta_schema_version: Schema version for compatibility check
```

#### **T.2.2 Subgraph and Provenance Checks**

**Check for existing anchor:**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=200)
# Search for planned anchor node (e.g., "Roman Republic")
anchor_exists = any(node.label == "Roman Republic" for node in subgraph)
```

**Provenance analysis:**
```python
if anchor_exists:
    node_id = get_node_id("Roman Republic")
    claims = agent.find_claims_for_node(node_id)
    provenance = agent.get_node_provenance(node_id)
    # Avoid duplicate claims, understand existing coverage
```

**Agent contribution tracking:**
```python
contributions = agent.find_agent_contributions()
# Returns: claims_proposed, claims_promoted, claims_rejected, promotion_rate
# Use to adjust confidence thresholds
```

**Cross-Reference:** See [Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration) for state management patterns.

---

### **T.3 Initialize Mode: Bootstrap Domain from Wikidata**

#### **T.3.1 Mode Activation and Logging (Step 5)**

**Purpose:** Bootstrap a new domain area from a trusted Wikidata anchor.

**Execution:**
```python
result_init = agent.execute_initialize_mode(
    anchor_qid="Q17167",  # Roman Republic
    depth=2,  # Traverse hierarchy 2 levels deep
    autosubmit_claims=False,  # Manual review required
    ui_callback=ui_log_callback  # Real-time logging
)
```

#### **T.3.2 Initialize Mode Workflow**

**Step-by-Step Process:**

1. **Fetch Wikidata anchor entity:**
   ```python
   entity = fetch_wikidata_entity("Q17167")
   # Returns: labels, descriptions, aliases, statements, sitelinks
   ```

2. **Auto-enrich/create root SubjectConcept:**
   ```python
   node_id = enrich_node_from_wikidata(
       wikidata_qid="Q17167",
       facet="political",
       create_if_missing=True
   )
   # Sets: label, description, alt_labels, wikidata_id, statement_count
   ```

3. **Validate completeness (Step 3.5):**
   ```python
   completeness = validate_node_completeness(node_id)
   # Checks: required properties present, label/description quality
   # Returns: score 0.0-1.0, missing_fields, validation_errors
   if completeness["score"] < 0.70:
       log_warning("Low completeness", completeness)
       return  # Abort if below threshold
   ```

4. **Enrich with CIDOC-CRM alignment:**
   ```python
   enrich_with_ontology_alignment(node_id, entity)
   # Maps Wikidata P31 types to CIDOC-CRM classes
   # Sets: cidoc_crm_class (e.g., E74_Group, E4_Period)
   ```

5. **Traverse hierarchy with allowed properties:**
   ```python
   related = discover_hierarchy_from_entity(
       qid="Q17167",
       depth=2,
       properties=["P31", "P279", "P361", "P527"]  # From Layer 2.5
   )
   # Returns: related entities, relationship types, hierarchy structure
   ```

6. **Generate claims from Wikidata statements:**
   ```python
   claims = generate_claims_from_wikidata(
       node_id=node_id,
       entity=entity,
       base_confidence=0.90,  # Wikidata authority
       facet="political"
   )
   # Each claim enriched with CRMinf belief metadata
   # Tagged with facet, source, extraction_time
   ```

7. **Optional auto-submit high-confidence claims:**
   ```python
   if autosubmit_claims:
       for claim in claims:
           if claim["confidence"] >= 0.90:
               submit_claim_for_validation(claim)
   ```

8. **Log all actions:**
   ```python
   logger.log_action(
       action_type="INITIALIZE",
       node_id=node_id,
       details={"qid": "Q17167", "depth": 2, "claims_generated": len(claims)}
   )
   ```

**Output:**
```python
{
    "nodes_created": 15,
    "relationships_discovered": 42,
    "claims_generated": 68,
    "completeness_score": 0.87,
    "cidoc_crm_class": "E4_Period",
    "log_file": "logs/military_initialize_20260216_143022.json"
}
```

**Cross-Reference:** See [Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns) for Wikidata API patterns.

---

### **T.3.5 Lexical Enrichment (Optional)**

#### **T.3.5.1 BabelNet Integration Phase**

**Position:** After Initialize Mode (Phase 3), before Ontology Proposal (Phase 4)

**Purpose:** Enrich SubjectConcept nodes with multilingual labels, glosses, and synsets for enhanced cross-language support and semantic disambiguation.

**Workflow:**

1. **Check configuration:**
   ```python
   if config.get("babelnet_enrichment_enabled", False):
       api_key = os.getenv("BABELNET_API_KEY")
       if not api_key:
           log_warning("BabelNet enrichment skipped: API key not configured")
           return
   ```

2. **Enrich each new SubjectConcept:**
   ```python
   for node in result_init["nodes_created"]:
       if node.get("wikidata_id"):  # Require Wikidata alignment
           enrichment = enrich_node_from_babelnet(
               node_id=node["id"],
               wikidata_qid=node["wikidata_id"],
               label=node["label"]
           )
           
           if enrichment.get("confidence", 0) >= 0.75:
               # Store BabelNet data on node
               update_node_properties(node["id"], {
                   "babelnet_id": enrichment["babelnet_id"],
                   "alt_labels": json.dumps(enrichment["alt_labels"]),
                   "glosses": json.dumps(enrichment["glosses"]),
                   "babelnet_confidence": enrichment["confidence"]
               })
               
               log_action(
                   action_type="LEXICAL_ENRICHMENT",
                   node_id=node["id"],
                   details=enrichment
               )
   ```

3. **Handle enrichment failures gracefully:**
   ```python
   # Lexical enrichment is optional - don't block on failure
   try:
       enrich_from_babelnet()
   except BabelNetAPIError as e:
       log_warning(f"BabelNet enrichment failed: {e}")
       # Continue to Ontology Proposal without BabelNet data
   ```

**Benefits:**
- Multilingual query support (French, German, Latin, etc.)
- Richer context for LLM-based clustering in Ontology Proposal
- Term disambiguation during Training Mode

**Configuration:**
```python
# config.py
BABELNET_ENRICHMENT = {
    "enabled": True,
    "min_confidence": 0.75,
    "required_languages": ["EN", "LA", "FR", "DE"],
    "skip_on_failure": True  # Graceful degradation
}
```

**Cross-Reference:** See **[Appendix S](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-s-babelnet-lexical-authority-integration)** for detailed BabelNet integration patterns.

---

### **T.4 Subject Ontology Proposal (Bridge Step, via SCA Component)**

#### **T.4.1 Ontology Proposal Execution (Step 5 Bridge)**

**Purpose:** Structure discovered entities into conceptual clusters with claim templates and validation rules.

**Execution:**
```python
result_onto = agent.propose_subject_ontology(ui_callback=ui_log_callback)
```

#### **T.4.2 Ontology Proposal Workflow**

**Step-by-Step Process:**

1. **Collect entities from Initialize Mode:**
   ```python
   nodes = result_init["nodes_created"]
   # Each node has: label, wikidata_id, P31/P279 types
   ```

2. **Fetch full Wikidata entities:**
   ```python
   for node in nodes:
       entity = fetch_wikidata_entity(node["wikidata_id"])
       type_chains = extract_type_hierarchy(entity)  # P31/P279 chains
   ```

3. **LLM clustering pass:**
   ```python
   clusters = llm_cluster_types(
       types=type_chains,
       facet="military",
       prompt_template="cluster_military_concepts"
   )
   # Returns: conceptual clusters (e.g., Military Leadership, Military Operations)
   ```

4. **Convert clusters to ontology classes:**
   ```python
   ontology_classes = []
   for cluster in clusters:
       ontology_class = {
           "class_name": cluster["name"],
           "parent_class": cluster.get("parent", "SubjectConcept"),
           "member_count": len(cluster["members"]),
           "characteristics": cluster["description"],
           "example_members": cluster["members"][:5]
       }
       ontology_classes.append(ontology_class)
   ```

5. **Generate claim templates:**
   ```python
   templates = generate_claim_templates(ontology_classes)
   # Example: "All Military Commanders have property:rank with value:MilitaryRank"
   ```

6. **Define validation rules:**
   ```python
   rules = [
       {"type": "membership", "rule": "All members must have P31 pointing to class"},
       {"type": "cardinality", "rule": "rank property: 1-3 values per entity"},
       {"type": "temporal", "rule": "service dates must be within lifetime"},
       {"type": "cross_facet", "rule": "military unit must align with geographic location"}
   ]
   ```

7. **Compute strength score:**
   ```python
   strength_score = compute_ontology_strength(
       member_count=len(nodes),
       template_coverage=len(templates) / len(nodes),
       rule_coverage=len(rules)
   )
   # Returns: 0.0-1.0 score indicating ontology quality
   ```

8. **Store ontology on agent instance:**
   ```python
   agent.proposed_ontology = {
       "classes": ontology_classes,
       "templates": templates,
       "rules": rules,
       "strength_score": strength_score,
       "created_at": datetime.now().isoformat()
   }
   ```

**Output:**
```python
{
    "classes": [
        {
            "class_name": "MilitaryLeadership",
            "parent_class": "SubjectConcept",
            "member_count": 8,
            "characteristics": "Individuals who commanded military units...",
            "example_members": ["Julius Caesar", "Pompey", "Scipio Africanus"]
        },
        # ... more classes
    ],
    "templates": [
        "MilitaryLeadership has rank: MilitaryRank",
        "MilitaryLeadership commanded: MilitaryUnit"
    ],
    "rules": [...],
    "strength_score": 0.82
}
```

**Cross-Reference:** See [Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf) for CIDOC-CRM alignment during ontology proposal.

---

### **T.5 Training Mode: Extended Claim Generation**

#### **T.5.1 Training Mode Execution**

**Purpose:** Generate claims guided by proposed ontology, with validation and quality controls.

**Execution:**
```python
result_train = agent.execute_training_mode(
    max_iterations=50,
    target_claims=300,
    min_confidence=0.80,
    autosubmit_high_confidence=False,
    ui_callback=ui_log_callback
)
```

#### **T.5.2 Training Mode Workflow**

**Per-Node Processing Loop:**

1. **Reload context (detect inter-agent changes):**
   ```python
   context = agent.get_session_context()
   # See if other facets have added claims or nodes
   ```

2. **Prioritize nodes using ontology:**
   ```python
   priority_nodes = sort_by_ontology_class(
       nodes=context["sample_nodes"],
       ontology=agent.proposed_ontology
   )
   # Process high-priority classes first (e.g., MilitaryLeadership)
   ```

3. **For each node:**

   a. **Ensure Wikidata QID exists:**
   ```python
   if not node.get("wikidata_id"):
       enrichment = enrich_node_from_wikidata(node["id"])
       if not enrichment.get("wikidata_id"):
           log_warning(f"Skipping node {node['id']}: no QID")
           continue
   ```

   b. **Validate completeness:**
   ```python
   completeness = validate_node_completeness(node["id"])
   log_metric("completeness", completeness["score"])
   if completeness["score"] < 0.70:
       attempt_auto_enrichment(node["id"])
   ```

   c. **Fetch Wikidata entity:**
   ```python
   entity = fetch_wikidata_entity(node["wikidata_id"])
   ```

   d. **Generate claims filtered by ontology:**
   ```python
   claims = generate_claims_from_wikidata(
       node_id=node["id"],
       entity=entity,
       base_confidence=0.90,
       facet=agent.facet_key,
       templates=agent.proposed_ontology["templates"],  # Filter by templates
       rules=agent.proposed_ontology["rules"]  # Validate against rules
   )
   ```

   e. **Use BabelNet for polysemous term disambiguation:**
   ```python
   # NEW: BabelNet integration for ambiguous terms
   if claim.get("value_label") in POLYSEMOUS_TERMS:
       babelnet_synset = disambiguate_with_babelnet(
           term=claim["value_label"],
           facet=agent.facet_key,
           context=node["label"]
       )
       if babelnet_synset:
           claim["babelnet_synset"] = babelnet_synset["synset_id"]
           claim["sense_gloss"] = babelnet_synset["gloss"]
   ```
   **Cross-Reference:** See **[Appendix S.5](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#s52-phase-5-training-mode-disambiguation)** for BabelNet disambiguation patterns.

   f. **Enrich claims with CRMinf:**
   ```python
   for claim in claims:
       enrich_claim_with_crminf(
           claim=claim,
           belief_type="I4_Proposition_Set",
           confidence=claim["confidence"]
       )
   ```

   g. **Validate CIDOC alignment:**
   ```python
   cidoc_valid = validate_cidoc_alignment(node["id"], claim)
   if not cidoc_valid:
       log_warning(f"CIDOC alignment failed for claim {claim['id']}")
       claim["confidence"] *= 0.90  # Confidence penalty
   ```

   h. **Filter by minimum confidence:**
   ```python
   claims = [c for c in claims if c["confidence"] >= min_confidence]
   ```

   i. **Auto-submit high-confidence claims:**
   ```python
   if autosubmit_high_confidence:
       for claim in claims:
           if claim["confidence"] >= 0.90:
               submit_claim_for_validation(claim)
   ```

   j. **Log each claim proposal:**
   ```python
   for claim in claims:
       logger.log_action(
           action_type="CLAIM_PROPOSED",
           node_id=node["id"],
           details={
               "label": claim["label"],
               "confidence": claim["confidence"],
               "rationale": claim["rationale"]
           }
       )
   ```

4. **Track metrics:**
   ```python
   metrics = {
       "nodes_processed": iteration_count,
       "claims_proposed": total_claims,
       "avg_confidence": mean(claim_confidences),
       "avg_completeness": mean(completeness_scores),
       "claims_per_second": total_claims / elapsed_time
   }
   ```

**Output:**
```python
{
    "nodes_processed": 45,
    "claims_proposed": 287,
    "avg_confidence": 0.86,
    "avg_completeness": 0.83,
    "claims_per_second": 2.4,
    "log_file": "logs/military_training_20260216_150345.json"
}
```

**Cross-Reference:** See [Appendix N](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-n-property-extensions--advanced-attributes) for advanced claim properties.

---

### **T.6 Between Tasks: Collaboration and Introspection**

#### **T.6.1 Cross-Facet Awareness**

**Monitor other facets:**
```python
# Check pending claims from all facets
all_pending = list_pending_claims()  # No facet filter

# Adjust behavior based on system load
if len(all_pending) > 1000:
    # Reduce proposal rate if validation queue is backed up
    agent.proposal_rate *= 0.75
```

#### **T.6.2 Self-Monitoring**

**Track promotion rate:**
```python
contributions = agent.find_agent_contributions()
promotion_rate = contributions["claims_promoted"] / contributions["claims_proposed"]

if promotion_rate < 0.70:
    # Increase confidence threshold if many claims are rejected
    agent.min_confidence += 0.05
    log_warning(f"Low promotion rate ({promotion_rate:.2f}), increasing threshold")
```

#### **T.6.3 Provenance Analysis**

**Understand node history:**
```python
for node in priority_nodes:
    provenance = get_node_provenance(node["id"])
    claim_history = get_claim_history(node["id"])
    
    # Avoid duplicate claims
    existing_claims = [c["label"] for c in claim_history]
    new_claims = [c for c in proposed_claims if c["label"] not in existing_claims]
```

**Cross-Reference:** See [Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration) for multi-agent coordination patterns.

---

### **T.7 End of "Day": Session Summary**

#### **T.7.1 Logger Summary**

**Final metrics:**
```python
summary = logger.generate_summary()
# Returns:
# - action_counts: {INITIALIZE: 1, REASONING: 45, QUERY: 203, CLAIM_PROPOSED: 287}
# - error_counts: {API_TIMEOUT: 3, VALIDATION_FAILED: 12}
# - claim_stats: {proposed: 287, high_confidence: 198, low_confidence: 89}
# - completeness_avg: 0.83
# - session_duration: 4520.3 seconds
```

#### **T.7.2 Persistence (Future Work)**

**Store ontology:**
```python
# Future: persist ontology for next session
save_ontology(
    facet=agent.facet_key,
    ontology=agent.proposed_ontology,
    version=agent.ontology_version
)
```

**Store session metrics:**
```python
# Future: track agent performance over time
save_session_metrics(
    agent_id=agent.agent_id,
    metrics=summary,
    timestamp=datetime.now()
)
```

---

### **T.8 Federation Enrichment Integration**

#### **T.8.1 Multi-Authority Enrichment Pattern**

**Purpose:** Enrich SubjectConcept nodes with data from multiple federation authorities beyond Wikidata.

**Workflow Position:** After Phase 3 (Initialize Mode), optionally before or alongside Phase 3.5 (Lexical Enrichment)

**Supported Authorities:**
- **Pleiades:** Ancient place identifiers and coordinates
- **VIAF:** Person authority with multi-national library identifiers
- **GeoNames:** Geographic name authority with modern coordinates
- **FAST:** Subject heading alignment
- **TGN:** Getty Thesaurus of Geographic Names

**Implementation:**
```python
def enrich_node_from_federation(
    node_id: str,
    authorities: List[str] = ["pleiades", "viaf", "geonames"]
) -> Dict:
    """
    Enrich node with data from multiple federation authorities.
    
    Follows patterns from Appendix R.10.
    """
    enrichments = {}
    
    for authority in authorities:
        try:
            if authority == "pleiades" and node.get("entity_type") == "Place":
                pleiades_data = enrich_from_pleiades(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if pleiades_data:
                    enrichments["pleiades_id"] = pleiades_data["id"]
                    enrichments["ancient_coordinates"] = pleiades_data["coords"]
                    enrichments["confidence"] = 0.85
            
            elif authority == "viaf" and node.get("entity_type") == "Person":
                viaf_data = enrich_from_viaf(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if viaf_data:
                    enrichments["viaf_id"] = viaf_data["id"]
                    enrichments["library_identifiers"] = viaf_data["identifiers"]
                    enrichments["confidence"] = 0.85
            
            elif authority == "geonames":
                geonames_data = enrich_from_geonames(
                    label=node["label"],
                    wikidata_qid=node.get("wikidata_id")
                )
                if geonames_data:
                    enrichments["geonames_id"] = geonames_data["id"]
                    enrichments["modern_coordinates"] = geonames_data["coords"]
                    enrichments["confidence"] = 0.80
        
        except FederationAPIError as e:
            log_warning(f"{authority} enrichment failed: {e}")
            continue
    
    # Stack evidence from multiple sources
    if len(enrichments) > 1:
        enrichments["confidence"] = min(0.95, enrichments["confidence"] + 0.10)
    
    return enrichments
```

**Usage in Initialize Mode:**
```python
# After creating SubjectConcept nodes from Wikidata
for node in result_init["nodes_created"]:
    if config.get("federation_enrichment_enabled", True):
        federation_data = enrich_node_from_federation(
            node_id=node["id"],
            authorities=["pleiades", "viaf", "geonames"]
        )
        if federation_data:
            update_node_properties(node["id"], federation_data)
```

**Confidence Stacking:**
- **Single authority:** 0.80-0.85 confidence
- **Two authorities:** +0.10 boost → 0.90-0.95
- **Three+ authorities:** +0.15 boost → 0.95-1.00 (capped)

**Cross-Reference:** See **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#r10-api-implementation-patterns)** for detailed API implementation patterns for each authority.

---

### **T.9 Error Recovery and Retry Patterns**

#### **T.9.1 API Timeout Handling**

**Pattern from Appendix R.10.10:**
```python
import time
from typing import Optional

def fetch_with_retry(
    fetch_func,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    timeout: int = 30
) -> Optional[Dict]:
    """
    Retry API calls with exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            return fetch_func(timeout=timeout)
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                log_warning(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                log_error("Max retries exceeded, giving up")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = int(e.response.headers.get("Retry-After", 60))
                log_warning(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
    return None
```

**Usage in Training Mode:**
```python
entity = fetch_with_retry(
    lambda timeout: fetch_wikidata_entity(node["wikidata_id"], timeout=timeout),
    max_retries=3
)
if not entity:
    log_error(f"Failed to fetch entity for node {node['id']}")
    continue  # Skip this node, move to next
```

#### **T.9.2 Completeness Validation Failures**

**Scenario:** Node fails completeness check (Step 3.5)

**Recovery Strategy:**
```python
completeness = validate_node_completeness(node_id)

if completeness["score"] < 0.70:
    # Attempt auto-enrichment
    missing_fields = completeness["missing_fields"]
    
    if "description" in missing_fields:
        # Fetch from Wikidata if not already present
        entity = fetch_wikidata_entity(node["wikidata_id"])
        if entity.get("descriptions", {}).get("en"):
            update_node_property(
                node_id,
                "description",
                entity["descriptions"]["en"]["value"]
            )
    
    if "alt_labels" in missing_fields:
        # Fetch from BabelNet or Wikidata aliases
        alt_labels = fetch_alt_labels(node["wikidata_id"])
        if alt_labels:
            update_node_property(node_id, "alt_labels", json.dumps(alt_labels))
    
    # Re-validate
    completeness = validate_node_completeness(node_id)
    
    if completeness["score"] < 0.70:
        log_warning(f"Node {node_id} still incomplete after enrichment")
        # Mark for manual review
        tag_node_for_review(node_id, reason="low_completeness")
```

#### **T.9.3 Claim Validation Errors**

**Scenario:** Generated claim fails validation rules

**Recovery Strategy:**
```python
def generate_and_validate_claims(node_id, entity, ontology_rules):
    claims = generate_claims_from_wikidata(node_id, entity)
    
    validated_claims = []
    for claim in claims:
        validation = validate_claim(claim, ontology_rules)
        
        if validation["valid"]:
            validated_claims.append(claim)
        else:
            # Attempt to fix common validation errors
            if validation["error"] == "missing_temporal_bound":
                # Add default temporal bound from entity lifespan
                claim["temporal_start"] = entity.get("birth_date")
                claim["temporal_end"] = entity.get("death_date")
                
                # Re-validate
                validation = validate_claim(claim, ontology_rules)
                if validation["valid"]:
                    validated_claims.append(claim)
                else:
                    log_warning(f"Claim {claim['id']} still invalid after fix")
            
            elif validation["error"] == "cardinality_violation":
                # Lower confidence and flag for review
                claim["confidence"] *= 0.80
                claim["validation_warning"] = validation["error"]
                validated_claims.append(claim)
            
            else:
                # Cannot auto-fix, log and skip
                log_error(f"Claim validation failed: {validation['error']}")
    
    return validated_claims
```

**Cross-Reference:** See [Appendix R.10.9](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration) for federation-specific error handling.

---

### **T.10 Cross-References**

**Related Appendices:**
- **[Appendix R.10](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-r-federation-strategy--multi-authority-integration):** Federation API implementation patterns, error handling, caching
- **[Appendix S](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-s-babelnet-lexical-authority-integration):** BabelNet lexical enrichment (Phase 3.5, Training Mode disambiguation)
- **[Appendix O](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-o-facet-training-resources-registry):** Training resources for facet-specific knowledge
- **[Appendix P](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-p-semantic-enrichment--ontology-alignment-cidoc-crmcrminf):** CIDOC-CRM alignment during enrichment
- **[Appendix Q](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-q-operational-modes--agent-orchestration):** Operational modes (Initialize, Training, Validation)
- **[Appendix K](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-k-wikidata-integration-patterns):** Wikidata integration patterns
- **[Appendix M](2-12-26 Chrystallum Architecture - CONSOLIDATED.md#appendix-m-identifier-safety-reference):** Schema validation and identifier safety

**Implementation Files:**
- `scripts/agents/facet_agent_framework.py`: SFA orchestration and workflow
- `scripts/agents/subject_concept_agent.py`: SubjectConceptAgent (SCA) for ontology proposal
- `scripts/federation/wikidata_client.py`: Wikidata API client
- `scripts/federation/babelnet_client.py`: BabelNet API client (to be created)
- `scripts/validation/completeness_validator.py`: Completeness validation (Step 3.5)
- `scripts/logging/agent_logger.py`: Agent action logging

**Key Integration Points:**
- **Phase 1:** Schema introspection (STEP_1_COMPLETE.md)
- **Phase 2:** State loading (STEP_2_COMPLETE.md)
- **Phase 3:** Initialize Mode (STEP_5_COMPLETE.md)
- **Phase 3.5:** Completeness validation (STEP_3_COMPLETE.md)
- **Phase 4:** CIDOC-CRM enrichment (STEP_4_COMPLETE.md)
- **Phase 5:** Subject Ontology Proposal (STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- **Phase 6:** Training Mode (STEP_3_COMPLETE.md, STEP_5_COMPLETE.md)

---

**(End of Appendix T)**

---

## **Appendix U: ADR-001 - Claim Identity and Content-Addressable Ciphers**

### **ADR-001: Content-Only Cipher for Claim Identity**

**Status:** ACCEPTED (2026-02-16)  
**Deciders:** Architecture Review  
**Date:** 2026-02-16

---

### **Context and Problem Statement**

Claims in the Chrystallum knowledge graph require unique, stable identifiers that enable:
1. **Automatic deduplication** when multiple agents extract the same assertion
2. **Cryptographic verification** of claim integrity across federated institutions
3. **Consensus aggregation** across facets without duplicate claim nodes
4. **Provenance tracking** for confidence evolution and agent accountability

**The Problem:** Initial architecture specifications contained an internal contradiction about what data should be included in the claim cipher (content-addressable hash).

**Conflicting Specifications:**
- **Section 6.4.1** (original): Included `confidence_score`, `extractor_agent_id`, and `extraction_timestamp` in cipher generation
- **Section 6.4.3** (verification pattern): Explicitly excluded confidence, agent, and timestamp with comment "NO confidence, NO agent, NO timestamp!"
- **Section 6.4.2** (deduplication example): Showed two agents extracting at different times producing identical ciphers (impossible if timestamp is in hash)

**Impact:** This inconsistency would break:
- Deduplication (same content extracted by different agents → different ciphers → duplicate nodes)
- Federation (institutions couldn't verify claims with different provenance metadata)
- Consensus (same assertion by multiple facets would create separate claim nodes)

---

### **Decision**

**We adopt Model 1: Content-Only Cipher**

**Claim cipher includes ONLY assertion content:**
- ✅ `source_work_qid` (where was it stated?)
- ✅ `passage_text_hash` (what text supports it?)
- ✅ `subject_entity_qid` (subject of assertion)
- ✅ `object_entity_qid` (object of assertion)
- ✅ `relationship_type` (predicate/relationship)
- ✅ `action_structure` (W5H1/facet-specific semantics)
- ✅ `temporal_data` (when did it occur?)
- ✅ `facet_id` (which facet perspective?)

**Claim cipher EXCLUDES provenance metadata:**
- ❌ `confidence_score` (changes as reviews accumulate)
- ❌ `extractor_agent_id` (different agents can extract same claim)
- ❌ `extraction_timestamp` (extraction time ≠ assertion content)

**Provenance is tracked separately:**
- **FacetPerspective nodes** with `PERSPECTIVE_ON` edges to the Claim node
- Each perspective stores: `agent_id`, `extraction_timestamp`, `confidence`, `contributing_agent`, `rationale`
- Multiple perspectives on same cipher = consensus signal

---

### **Rationale**

**Why Content-Only?**

1. **Stable Identity Across Time and Agents**
   - Same assertion extracted in 2026 and 2030 → same cipher
   - Multiple agents independently discovering same claim → single Claim node
   - Enables true deduplication and consensus detection

2. **Cryptographic Verification Works**
   - Institution A publishes claim with cipher X
   - Institution B downloads and recomputes cipher from content
   - Verification succeeds because cipher depends only on content, not A's metadata
   - Provenance differences don't break verification

3. **Consensus Aggregation is Possible**
   - Political SFA extracts claim at 10:00 AM → cipher ABC
   - Military SFA extracts same claim at 14:00 PM → cipher ABC (same!)
   - Graph query: "How many facets agree on cipher ABC?" → consensus score
   - Without content-only cipher: two separate claim nodes → no consensus detected

4. **Confidence Evolution Doesn't Break Identity**
   - Initial extraction: confidence = 0.75
   - After review: confidence = 0.90
   - Cipher remains unchanged (content hasn't changed, just our belief in it)
   - Federated institutions can track confidence separately without re-hashing

5. **Alignment with Verification Pattern**
   - Section 6.4.3 verification query already excludes confidence/agent/timestamp
   - This ADR makes the generation pattern match the verification pattern
   - Single source of truth for "what makes a claim unique"

---

### **Consequences**

**Positive:**
- ✅ Automatic deduplication works reliably
- ✅ Multiple agents → single claim + multiple perspectives → consensus signal
- ✅ Cryptographic verification across institutions is possible
- ✅ Cipher remains stable as reviews/confidence evolve
- ✅ Federation across Chrystallum instances is feasible
- ✅ Graph queries for consensus are efficient (GROUP BY cipher)

**Negative:**
- ⚠️ Two claims with identical content but different facet perspectives still get different ciphers (facet_id is in hash)
  - **Mitigation:** This is intentional - "Caesar crossed Rubicon" from POLITICAL facet vs. MILITARY facet are legitimately different perspectives
  - FacetPerspective nodes allow cross-facet consensus tracking
- ⚠️ Requires careful normalization of content fields (Unicode, whitespace, date formats)
  - **Mitigation:** Appendix U.2 specifies canonical normalization functions
- ⚠️ Provenance metadata must be stored separately (cannot be embedded in cipher)
  - **Mitigation:** FacetPerspective + PERSPECTIVE_ON edges provide rich provenance model

**Neutral:**
- 🔄 Cipher is facet-aware (facet_id included) rather than pure content
  - **Rationale:** Each facet may interpret same source differently (e.g., "Caesar crossed Rubicon" has distinct POLITICAL, MILITARY, and GEOGRAPHIC dimensions)
  - Consensus detection still works via FacetPerspective aggregation on same cipher

---

### **Implementation Requirements**

**1. Canonical Normalization (REQUIRED)**

All fields in cipher computation MUST be normalized:

```python
def compute_claim_cipher(claim_content: dict) -> str:
    """Generate content-only cipher with canonical normalization."""
    import hashlib, json, unicodedata
    
    # Normalize each component
    components = [
        normalize_unicode(claim_content['source_work_qid']),
        claim_content['passage_text_hash'],  # Already a hash
        normalize_unicode(claim_content['subject_entity_qid']),
        normalize_unicode(claim_content['object_entity_qid']),
        normalize_unicode(claim_content['relationship_type']),
        normalize_json(claim_content['action_structure']),
        normalize_iso8601(claim_content['temporal_data']),
        normalize_unicode(claim_content['facet_id'])
    ]
    
    # Concatenate with delimiter
    canonical_string = '||'.join(components)
    
    # SHA-256 hash with prefix
    cipher = hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
    return f"claim_{cipher[:40]}"  # claim_abc123...

def normalize_unicode(text: str) -> str:
    """Unicode NFC normalization + strip whitespace."""
    return unicodedata.normalize('NFC', text.strip())

def normalize_json(obj: dict) -> str:
    """Canonical JSON: sorted keys, no whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))

def normalize_iso8601(date_str: str) -> str:
    """ISO 8601 extended format with zero-padding."""
    # Example: "-49-01-10" → "-0049-01-10"
    # Ensures consistent format for negative years
    return format_iso8601_extended(date_str)
```

**2. Verification Pattern (REQUIRED)**

All cipher verification queries MUST exclude provenance:

```cypher
// Recompute cipher from content ONLY
MATCH (c:Claim {cipher: $claimed_cipher})
WITH c,
  compute_cipher_hash(
    c.source_work_qid,
    c.passage_text_hash,
    c.subject_entity_qid,
    c.object_entity_qid,
    c.relationship_type,
    c.action_structure,
    c.temporal_data,
    c.facet_id
    // NO confidence, NO agent, NO timestamp!
  ) AS recomputed_cipher
RETURN 
  c.cipher = recomputed_cipher AS integrity_verified,
  c.cipher AS original_cipher,
  recomputed_cipher AS computed_cipher
```

**3. Provenance Storage Pattern (REQUIRED)**

Provenance MUST be stored in separate FacetPerspective nodes:

```cypher
// Create claim with first perspective
MERGE (claim:Claim {cipher: $cipher})
  ON CREATE SET 
    claim.source_work_qid = $content.source,
    claim.subject_entity_qid = $content.subject,
    // ... other content fields

// Create perspective node (provenance)
CREATE (perspective:FacetPerspective {
  perspective_id: randomUUID(),
  facet_key: $provenance.facet,
  parent_claim_cipher: $cipher,
  confidence: $provenance.confidence,
  contributing_agent: $provenance.agent_id,
  assertion_timestamp: $provenance.timestamp,
  rationale: $provenance.rationale
})-[:PERSPECTIVE_ON]->(claim)

RETURN claim.cipher AS cipher, perspective.perspective_id AS perspective_id
```

**4. Consensus Detection Pattern (ENABLED)**

```cypher
// Find claims with multi-facet consensus
MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim)
WITH c, count(DISTINCT p.facet_key) AS facet_count,
     avg(p.confidence) AS avg_confidence
WHERE facet_count >= 2  // At least 2 facets agree
RETURN c.cipher, facet_count, avg_confidence
ORDER BY facet_count DESC, avg_confidence DESC
```

---

### **Migration Path**

**For Existing Claims (if any):**

1. **Audit Phase:**
   ```cypher
   // Find claims with provenance in cipher (old model)
   MATCH (c:Claim)
   WHERE c.extractor_agent_id IS NOT NULL 
      OR c.extraction_timestamp IS NOT NULL
   RETURN count(c) AS claims_needing_migration
   ```

2. **Migrate Phase:**
   ```cypher
   // Extract provenance to FacetPerspective, recompute cipher
   MATCH (c:Claim)
   WHERE c.extractor_agent_id IS NOT NULL
   WITH c, compute_content_only_cipher(c) AS new_cipher
   
   // Create perspective node with old provenance
   CREATE (p:FacetPerspective {
     facet_key: c.facet_id,
     confidence: c.confidence_score,
     contributing_agent: c.extractor_agent_id,
     assertion_timestamp: c.extraction_timestamp
   })
   
   // Update claim with new cipher, remove provenance fields
   SET c.cipher = new_cipher
   REMOVE c.confidence_score, c.extractor_agent_id, c.extraction_timestamp
   
   // Link perspective to claim
   CREATE (p)-[:PERSPECTIVE_ON]->(c)
   ```

3. **Verify Phase:**
   ```cypher
   // Verify all ciphers can be recomputed
   MATCH (c:Claim)
   WITH c, compute_content_only_cipher(c) AS recomputed
   WHERE c.cipher <> recomputed
   RETURN c.cipher, recomputed, "MISMATCH" AS status
   // Should return 0 rows
   ```

---

### **Related Decisions**

- **ADR-002** (future): Trust model for federated claims (signatures, transparency log, key distribution)
- **ADR-003** (future): Facet taxonomy canonicalization (single registry, uppercase enforcement)
- **Appendix R**: Federation Strategy (multi-authority integration, confidence bumps)
- **Section 6.4**: Content-Addressable Claim Identification (implementation of this ADR)

---

### **References**

- Architecture Review 2026-02-16 (md/Architecture/2-16-26-architecture review.txt)
- Section 6.4.1: Claim Cipher Generation (corrected 2026-02-16)
- Section 6.4.2: Automatic Deduplication (corrected 2026-02-16)
- Section 6.4.3: Verification Query Pattern (already correct)
- Section 5.5.3: Claim Architecture - Cipher + Star Pattern

---

**(End of Appendix U - ADR-001)**

---

## **Appendix U.5: ADR-001 Resolution Status (Architecture Review Issue #4)**

**Status:** ISSUE #4 RESOLVED  
**Date:** 2026-02-16  
**Architecture Review Item:** "Claim identity/cipher semantics internally inconsistent"

**Review Finding:**
> "Cipher generation includes fields like confidence, extractor_agent_id, and extraction_timestamp in the normalized hash input. Elsewhere, the verification pattern explicitly says the recomputation must exclude confidence/agent/timestamp ("NO confidence, NO agent, NO timestamp!"). Those can't both be the definition of "the cipher.""

**Resolution:**
✅ **ADR-001 (Appendix U) adopted Model 1: Content-Only Cipher**
- Cipher INCLUDES only: subject, object, relationship, temporal data, source work, passage hash, facet_id
- Cipher EXCLUDES: confidence_score, extractor_agent_id, extraction_timestamp
- **Consequence**: Same assertion extracted by different agents at different times = same cipher = automatic deduplication
- **Consequence**: Confidence evolution does NOT change cipher (provenance tracked separately in FacetPerspective nodes)
- **Consequence**: Cryptographic verification works across institutions (content-only signature)

**Implementation Compliance:**
- ✅ Section 6.4.1 Cipher Generation specifies content-only hash with explicit "NO confidence, NO agent, NO timestamp!" rule
- ✅ Section 6.4.3 Verification Query Pattern correctly recomputes exclude cipher from content only
- ✅ Section 6.4.2 Deduplication Query Pattern assumes same content = same cipher
- ✅ Appendix U specifies normalization functions and implementation requirements
- ✅ Section 5.5.3 Claim Architecture applies cipher consistently

**Minor Documentation Clarification Needed:**
- Section 6.4.1 "Claim Versioning Built-In" contains outdated comment "Computed with confidence=0.85" 
- Should be: "Content-only cipher (confidence NOT included in hash)"
- Context: Clarifies that confidence updates do NOT change cipher (cipher is stable identifier)
- **Action**: Mark for documentation pass (non-blocking - code behavior is correct)

**Impact on Federation:**
- ✅ Enables Wikidata/CIDOC/external system verification (content hash transcends institutional boundaries)
- ✅ Multiple Chrystallum instances can detect duplicate claims via cipher (distributed deduplication)
- ✅ Confidence can be aggregated separately without re-hashing

---

# **Appendix V: Relationship Kernel Strategy (ADR-002)**

## **V.1 Problem Statement**

### **V.1.1 Scope Risk**

The canonical relationship catalog defines 300 relationship types aligned simultaneously to:
- Native Chrystallum semantics (historical research optimization)
- Wikidata properties (linked data interoperability)
- CIDOC-CRM (ISO 21127:2023 museum/archival standards)

**Risk Identified** (Architecture Review 2026-02-16):
> "A 300-relationship canonical set aligned simultaneously to native Chrystallum semantics, Wikidata properties, and CIDOC-CRM is a large knowledge-engineering commitment, and it creates a high risk of 'design completeness' without operational correctness."

### **V.1.2 Impact**

Attempting to implement all 300 relationships simultaneously creates:
1. **Development Bottleneck**: Validating 300 edge types delays operational deployment
2. **Testing Complexity**: Comprehensive test coverage becomes impractical
3. **Documentation Burden**: Complete usage guidance for 300 types is overwhelming
4. **Query Fragmentation**: Too many edge types dilute graph traversal patterns
5. **Maintenance Overhead**: Schema evolution impacts 300 relationships simultaneously

### **V.1.3 Recommendation**

Architecture reviewer: *"Define a minimal 'v1 relationship kernel' (maybe 30–50 edges) that unlocks real traversal, and treat the rest as staged expansions with migration rules."*

---

## **V.2 Decision: Function-Driven Relationship Catalog**

### **V.2.1 Architecture Decision**

**Status**: ACCEPTED (2026-02-16, revised 2026-02-16)

**Decision**: Maintain comprehensive relationship catalog (311 types) organized by **functional capabilities delivered** rather than arbitrary size limits.

**Relationship Catalog State** (as of 2026-02-16):
- **Total**: 311 relationship types (actual registry count)
- **Implemented**: 202 types (`lifecycle_status = "implemented"`)
- **Candidate**: 108 types (`lifecycle_status = "candidate"`) - validated backlog awaiting implementation
- **Categories**: 31 semantic domains

**Crosswalk Coverage**:
- **Wikidata properties**: 91 types (29.4%) ← enables federated SPARQL queries
- **CIDOC-CRM codes**: 199 types (64.2%) ← enables museum/archival RDF export
- **CRMinf applicable**: 24 types (7.7%) ← enables argumentation/inference tracking

**Rationale**: 
- Edge semantics ARE the knowledge graph's value proposition
- Multiple Chrystallum relationships → single Wikidata property is precision, not redundancy
- Example: `FATHER_OF`, `MOTHER_OF`, `PARENT_OF` all map to P40, but enable gender-specific genealogy queries
- Reducing to arbitrary "48 types" sacrifices semantic precision for false simplicity

---

## **V.3 Functional Capabilities & Dependencies**

### **V.3.1 Core Graph Traversal Functions**

**Function**: Basic entity navigation (Person↔Event↔Place↔Work)

**Dependencies**:
- **Relationships required** (12 types, all implemented):
  - Participation: `PARTICIPATED_IN`, `HAD_PARTICIPANT` (P710)
  - Birth/Death: `BORN_IN`, `BIRTHPLACE_OF` (P19), `DIED_IN`, `DEATH_PLACE_OF` (P20)
  - Location: `LOCATED_IN`, `LOCATION_OF` (P131)
  - Authorship: `AUTHOR`, `WORK_OF` (P50)
  - Observation: `WITNESSED_EVENT`, `WITNESSED_BY` (P1441)

- **Wikidata crosswalk**: 100% coverage (all 12 mapped) ✅
- **CIDOC-CRM crosswalk**: Required for RDF export
- **CRMinf crosswalk**: Not applicable (factual relationships, not inferences)

**Query examples enabled**:
```cypher
// Find all events Caesar participated in and their locations
MATCH (caesar:Human {name: "Caesar"})-[:PARTICIPATED_IN]->(event:Event)
      -[:LOCATED_IN]->(place:Place)
RETURN event.label, place.label, event.start_date

// Find all works written by people born in Rome
MATCH (rome:Place {name: "Rome"})<-[:BORN_IN]-(author:Human)
      -[:AUTHOR]->(work:Work)
RETURN author.name, work.label
```

---

### **V.3.2 Familial Network Analysis**

**Function**: Genealogical queries, family tree construction, kinship analysis

**Dependencies**:
- **Relationships required** (32 types in Familial category, all implemented):
  - Nuclear: `PARENT_OF`, `CHILD_OF`, `FATHER_OF`, `MOTHER_OF` (P40)
  - Sibling: `SIBLING_OF`, `HALF_SIBLING_OF` (P3373)
  - Marriage: `SPOUSE_OF` (P26)
  - Extended: `GRANDPARENT_OF`, `GRANDCHILD_OF`, `AUNT_OF`, `UNCLE_OF`, `COUSIN_OF`
  - In-law: `FATHER_IN_LAW_OF`, `MOTHER_IN_LAW_OF`, `BROTHER_IN_LAW_OF`, `SISTER_IN_LAW_OF`, etc.
  - Roman-specific: `MEMBER_OF_GENS`, `HAS_GENS_MEMBER` (P53)
  - Adoption: `ADOPTED`, `ADOPTED_BY`

- **Wikidata crosswalk**: Partial (core relationships mapped, extended relationships Chrystallum-specific)
- **Precision benefit**: Gender-specific relationships (`FATHER_OF` vs `MOTHER_OF`) enable patrilineal/matrilineal queries impossible in Wikidata

**Query examples enabled**:
```cypher
// Find Caesar's patrilineal ancestry (father-line only)
MATCH path = (caesar:Human {name: "Caesar"})-[:CHILD_OF*1..5]->(ancestor:Human)
WHERE ALL(r IN relationships(path) WHERE 
  EXISTS((endNode(r))-[:FATHER_OF]->(startNode(r))))
RETURN ancestor.name, length(path) AS generations

// Find all Julia gens members married to other patrician families
MATCH (julia_member:Human)-[:MEMBER_OF_GENS]->(:Gens {name: "Julia"}),
      (julia_member)-[:SPOUSE_OF]->(spouse:Human)
      -[:MEMBER_OF_GENS]->(other_gens:Gens)
WHERE other_gens.name <> "Julia"
RETURN julia_member.name, spouse.name, other_gens.name
```

---

### **V.3.3 Political Network Analysis**

**Function**: Power networks, territorial control, political succession, alliances

**Dependencies**:
- **Relationships required** (39 types in Political category):
  - Control: `CONTROLLED`, `CONTROLLED_BY` (P17), `CONQUERED`, `CONQUERED_BY`
  - Alliance: `ALLIED_WITH`, `ALLIED_VIA_MARRIAGE`, `ENEMY_OF`
  - Appointment: `APPOINTED`, `APPOINTED_BY` (P39), `POSITION_HELD`
  - Succession: `HEIR_TO`, `SUCCEEDED_BY`, `COLLAPSED`, `CAUSED_COLLAPSE_OF` (P576)
  - Influence: `INFLUENCED`, `INFLUENCED_BY`, `MANIPULATED`
  - Legal/Proscription: `OUTLAWED`, `PROSCRIBED` (Legal action relationships)

- **Wikidata crosswalk**: Strong coverage for core control/appointment, Chrystallum-specific for Roman proscription
- **CIDOC-CRM crosswalk**: E7_Activity for most political actions

**Query examples enabled**:
```cypher
// Find political alliance networks during Second Punic War
MATCH (rome:Institution {name: "Rome"})-[:ALLIED_WITH*1..2]-(ally)
      -[:PARTICIPATED_IN]->(war:Event {label: "Second Punic War"})
RETURN ally.name, length(path) AS degrees_from_rome

// Find who appointed whom during the First Triumvirate
MATCH (appointer:Human)-[:APPOINTED]->(appointee:Human)
      -[:POSITION_HELD]->(office:Position)
WHERE appointee.active_period OVERLAPS "(-60, -53)"
RETURN appointer.name, appointee.name, office.label
```

---

### **V.3.4 Military Campaign Tracking**

**Function**: Battle analysis, command structures, military outcomes

**Dependencies**:
- **Relationships required** (23 types in Military category):
  - Participation: `FOUGHT_IN`, `BATTLE_PARTICIPANT`, `BATTLED_IN` (P607)
  - Outcomes: `DEFEATED`, `DEFEATED_BY`, `BESIEGED`, `BESIEGED_BY`
  - Command: `COMMANDED_BY`, `SERVED_UNDER`
  - Extreme actions: `MASSACRED`, `SACKED`, `LEVELLED`
  - Loyalty shifts: `BETRAYED`, `DEFECTED_TO`, `DEFECTED_FROM`

- **Wikidata crosswalk**: Core participation mapped (P607), outcomes Chrystallum-specific
- **CIDOC-CRM crosswalk**: E7_Activity for military actions

**Query examples enabled**:
```cypher
// Find all battles of Gallic Wars with participants and outcomes
MATCH (war:Event {label: "Gallic Wars"})<-[:PART_OF]-(battle:Event)
OPTIONAL MATCH (victor:Human)-[:DEFEATED]->(vanquished:Human)
WHERE EXISTS((victor)-[:FOUGHT_IN]->(battle))
RETURN battle.label, battle.year, 
       collect(DISTINCT victor.name) AS victors,
       collect(DISTINCT vanquished.name) AS defeated
```

---

### **V.3.5 Geographic Movement & Settlement**

**Function**: Migration routes, population movement, residence tracking, exile patterns

**Dependencies**:
- **Relationships required** (20 types in Geographic category):
  - Movement: `MIGRATED_FROM`, `MIGRATED_TO`, `FLED_TO`, `FLED_FROM`
  - Residence: `LIVED_IN`, `RESIDENCE_OF` (P551)
  - Exile: `EXILED`, `EXILED_BY`
  - Foundation: `FOUNDED` (P112)
  - Core location: Inherits `LOCATED_IN`, `BORN_IN`, `DIED_IN` from Core Traversal

- **Wikidata crosswalk**: Core location/residence mapped, migration relationships Chrystallum-specific

**Query examples enabled**:
```cypher
// Track Cimbri migration route across Gaul
MATCH path = (cimbri:Group {name: "Cimbri"})
             -[:MIGRATED_FROM|MIGRATED_TO*]-(place:Place)
WITH nodes(path) AS migration_nodes
UNWIND migration_nodes AS place
MATCH (place)-[:LOCATED_IN]->(region:Place)
RETURN place.name, region.name, place.coordinates
ORDER BY place.year_range
```

---

### **V.3.6 Provenance & Claim Attribution**

**Function**: Evidence chains, source attribution, work citations, claim verification

**Dependencies**:
- **Relationships required** (11 types in Attribution category):
  - Citation: `DESCRIBES`, `MENTIONS`, `QUOTES`, `SUMMARIZES`, `ANALYZES`
  - Attribution: `ATTRIBUTED_TO`, `EXTRACTED_FROM`
  - Naming: `NAMED_AFTER`, `NAMESAKE_OF` (P138)
  - Interpretation: `INTERPRETS`

- **Wikidata crosswalk**: Minimal (most attribution is CRMinf domain)
- **CRMinf crosswalk**: CRITICAL - these map to I7_Belief_Adoption, I5_Inference_Making
- **Dependency**: Requires Claim nodes + FacetPerspective provenance architecture

**Query examples enabled**:
```cypher
// Find all works that mention Caesar and their authors
MATCH (caesar:Human {name: "Caesar"})<-[:MENTIONS]-(work:Work)
      -[:AUTHOR]->(author:Human)
RETURN work.label, author.name, work.publication_year
ORDER BY work.publication_year

// Find claim provenance chain from Work to Claim
MATCH path = (claim:Claim)-[:EXTRACTED_FROM]->(work:Work)
             -[:AUTHOR]->(author:Human)
RETURN claim.cipher, work.label, author.name, 
       claim.confidence_score, claim.facet_id
```

---

### **V.3.7 Federated Query Functions**

**Function**: Cross-institution queries via Wikidata SPARQL, external dataset linking

**Dependencies**:
- **Wikidata crosswalk**: MANDATORY (91 relationships currently mapped, target: 200+)
- **Missing coverage impacts**:
  - 220 relationships (70.6%) not yet mapped to Wikidata properties
  - Federated queries can only traverse mapped relationships
  - Backlog files exist: `wikidata_p_unmapped_backlog_2026-02-13.csv`, `wikidata_p_catalog_candidates_2026-02-13.csv`

**Federated query example** (requires Wikidata alignment):
```cypher
// Find Chrystallum claims about entities also in external Wikidata
MATCH (entity:Human)-[:PARTICIPATED_IN]->(event:Event)
WHERE entity.qid IS NOT NULL  // Has Wikidata alignment
WITH entity.qid AS qid, event
// Execute federated SPARQL query via Wikidata P710 (conflict)
CALL apoc.load.jsonParams(
  "https://query.wikidata.org/sparql?query=" + 
  urlencode("SELECT ?conflict WHERE { wd:" + qid + " wdt:P710 ?conflict }")
)
YIELD value
RETURN event.label AS chrystallum_event, 
       value.conflict AS wikidata_conflict,
       "CROSS_VALIDATED" AS status
```

---

### **V.3.8 Museum/Archival Integration Functions**

**Function**: CIDOC-CRM RDF export, archival standards compliance (ISO 21127:2023)

**Dependencies**:
- **CIDOC-CRM crosswalk**: Already strong (199 relationships = 64.2% coverage) ✅
- **Coverage by type**:
  - `cidoc_crm_kind = "PROPERTY"`: Direct property mappings (e.g., P45_consists_of)
  - `cidoc_crm_kind = "EVENT"`: Reified as E7_Activity nodes (e.g., FOUGHT_IN)
  - `cidoc_crm_kind = "CLASS"`: Maps to CIDOC class hierarchy (e.g., E21_Person)
  - `cidoc_crm_kind = "OPTIONAL_EVENT"`: May reify based on granularity needs

**Export example**:
```python
# Export Chrystallum claim to CIDOC-CRM RDF
def export_claim_to_cidoc(claim_cipher):
    relationship = get_relationship_type(claim.relationship_type)
    
    if relationship.cidoc_crm_kind == "EVENT":
        # Reify as E7_Activity
        return f"""
        <crm:E7_Activity rdf:about="chrystallum:claim/{claim_cipher}">
            <crm:{relationship.cidoc_crm_code}>
                <crm:E21_Person rdf:about="wikidata:{claim.subject_qid}"/>
            </crm:{relationship.cidoc_crm_code}>
        </crm:E7_Activity>
        """
```

---

### **V.3.9 Argumentation & Inference Functions**

**Function**: Multi-agent debate tracking, belief adoption, inference chains, confidence evolution

**Dependencies**:
- **CRMinf crosswalk**: Currently minimal (24 relationships = 7.7%)
- **Critical mappings needed**:
  - Attribution relationships → I7_Belief_Adoption (claim acceptance)
  - Reasoning relationships → I5_Inference_Making (logical inference)
  - No Wikidata equivalents exist for CRMinf (documented in `CIDOC/cidoc_wikidata_mapping_validated.csv`)
  - Chrystallum Claim architecture provides fallback (I2_Belief, I6_Belief_Value)

**Candidate relationships for CRMinf**:
- `BELIEF_ABOUT`, `EVIDENCE_FOR` → map to I7_Belief_Adoption
- `INFERRED_FROM`, `LOGICALLY_IMPLIES` → map to I5_Inference_Making
- `CHALLENGED_BY`, `SUPPORTED_BY` → argumentation tracking (I1_Argumentation)

---

## **V.4 Candidate Backlog**

### **V.4.1 Registry State**

**Implemented relationships**: 202 types (ready for production use)  
**Candidate relationships**: 108 types (validated semantics, awaiting implementation)

**Candidate status** means:
- Relationship semantics defined and validated
- Category assignment confirmed
- Use cases documented
- Implementation pending (Neo4j seed script, validation, tests, examples)

**Backlog  location**: `Relationships/relationship_types_registry_master.csv` (filter `lifecycle_status = "candidate"`)

---

### **V.4.2 Crosswalk Backlog**

**Wikidata Property Mapping**:
- Current: 91 relationships mapped (29.4%)
- Backlog: 220 relationships unmapped (70.6%)
- **Backlog files**:
  - `Relationships/wikidata_p_unmapped_backlog_2026-02-13.csv` - relationships needing P-property assignment
  - `Relationships/wikidata_p_catalog_candidates_2026-02-13.csv` - candidate Wikidata properties
  - `Relationships/wikidata_p_api_candidates_2026-02-13.csv` - API-harvested property candidates
  - `Relationships/relationship_type_p_suggestions_exact_alias_2026-02-13.csv` - exact alias matches
  - `Relationships/relationship_type_p_suggestions_relaxed_alias_2026-02-13.csv` - fuzzy alias matches

**CIDOC-CRM Code Mapping**:
- Current: 199 relationships mapped (64.2%) ✅ Strong coverage
- Backlog: 112 relationships unmapped  
  (Primarily Application, Evolution, Reasoning categories)

**CRMinf Applicable Flag**:
- Current: 24 relationships marked (7.7%)
- Backlog: Attribution, Reasoning, Authorship categories need CRMinf review
- **Reference**: `CIDOC/cidoc_wikidata_mapping_validated.csv` documents "no Wikidata equivalent" cases

---

### **V.4.3 Priority Candidates by Function**

**For Federated Queries** (requires Wikidata mapping):
- Economic: `TRADED_WITH`, `EXPORTED_TO`, `IMPORTED_FROM`
- Legal: `CONVICTED_OF`, `SENTENCED_TO`, `IMPRISONED_IN`
- Diplomatic: `NEGOTIATED_WITH`, `SENT_ENVOYS_TO`, `RECEIVED_ENVOYS_FROM`

**For Museum Integration** (requires CIDOC-CRM mapping):
- Application: `MATERIAL_USED`, `PRODUCED_IN`
- Production: `DEPICTS`, `PORTRAYS`, `SYMBOLIZES`
- Evolution: `REPLACED_BY`, `SUPERSEDED_BY`, `OBSOLETE_AFTER`

**For Argumentation/Inference** (requires CRMinf mapping):
- Reasoning: `BELIEF_ABOUT`, `EVIDENCE_FOR`, `INFERRED_FROM`
- Attribution: `INTERPRETS`, `ANALYZES`, `CHALLENGES`
- Observation: `OBSERVED_BY`, `DOCUMENTED_IN`

---

## **V.5 Migration Contracts**

### **V.5.1 Adding New Relationships** (Non-Breaking)

**Process**:
1. Add to `Relationships/relationship_types_registry_master.csv` with `lifecycle_status = "candidate"`
2. Document: category, description, directionality, parent_relationship, specificity_level
3. Validate: No naming conflicts, directionality consistent with parent
4. Optional: Map to wikidata_property, cidoc_crm_code if applicable
5. Promote: Change `lifecycle_status = "implemented"` when ready
6. Implement: Create Neo4j seed script entry, validation rules, test coverage, query examples

**Compatibility guarantee**:
- New relationship types can be added at any time
- Existing queries using other relationships remain unaffected
- New edge types do not change traversal patterns of existing types

---

### **V.5.2 Deprecating Relationships** (Breaking - Requires Migration)

**Process**:
1. Mark relationship with `status = "deprecated"` in registry
2. Document deprecation reason in `note` field
3. Provide migration path: `deprecated_relationship → replacement_relationship` mapping
4. Create automated migration Cypher script to rewrite existing edges
5. Update all documentation/examples removing deprecated type
6. Remove from registry only after confirming zero usage in graph

**Compatibility requirement**:
- 12-month deprecation notice before removal
- Migration script provided
- Clear communication of breaking change

---

### **V.5.3 Changing Directionality** (Breaking - Avoid)

**DO NOT** change directionality of existing relationships.

**Instead**:
1. Create new relationship with correct directionality
2. Mark old relationship as deprecated
3. Provide migration path (12-month window)

**Rationale**: Directionality changes break all queries using that relationship type.

---

### **V.5.4 Renaming Relationships** (Breaking - Avoid)

**Avoid renaming**. Instead:
- Add aliases via `wikidata_alt_labels` field in registry
- Keep canonical `relationship_type` stable

**If rename necessary** (e.g., semantic correction):
- Treat as deprecate + add new (12-month migration window)
- Automated Cypher script to rewrite edge types:
  ```cypher
  MATCH ()-[r:OLD_NAME]->()
  CREATE (startNode(r))-[:NEW_NAME {properties: r}]->(endNode(r))
  DELETE r
  ```

---

## **V.6 Functional Benefits of Comprehensive Catalog**

### **V.6.1 Semantic Precision**

**Benefit**: Multiple Chrystallum relationships mapping to single Wikidata property enables precision impossible in federated datasets.

**Example**: `FATHER_OF`, `MOTHER_OF`, `PARENT_OF` all map to Wikidata P40 (child), but enable:
- Patrilineal queries (father-line only):
  ```cypher
  MATCH path = (person)-[:CHILD_OF*]->(:Human)
  WHERE ALL(r IN relationships(path) WHERE 
    EXISTS((endNode(r))-[:FATHER_OF]->(startNode(r))))
  ```
- Matrilineal queries (mother-line only):
  ```cypher
  MATCH path = (person)-[:CHILD_OF*]->(:Human)
  WHERE ALL(r IN relationships(path) WHERE 
    EXISTS((endNode(r))-[:MOTHER_OF]->(startNode(r))))
  ```

**Without gender-specific relationships**: Impossible to distinguish lineages in Wikidata alone.

---

### **V.6.2 Historical Domain Specialization**

**Benefit**: Chrystallum-specific relationships capture Roman historical semantics not present in general ontologies.

**Examples**:
- `PROSCRIBED` (outlawed with property confiscation) vs generic `OUTLAWED`
- `MEMBER_OF_GENS` (Roman clan membership) vs generic `MEMBER_OF`
- `DEFECTED_TO` (military loyalty shift) vs generic `JOINED`
- `BESIEGED` (siege warfare) vs generic `FOUGHT_IN`

**Coverage**: 153 Chrystallum-specific relationships (49% of catalog) enable domain queries impossible with Wikidata/CIDOC alone.

---

### **V.6.3 Query Composability**

**Benefit**: Comprehensive relationship catalog enables complex multi-hop queries combining semantics.

**Example**: "Find all people who married into enemy families during civil wars"
```cypher
MATCH (person:Human)-[:MEMBER_OF_GENS]->(gens1:Gens),
      (person)-[:SPOUSE_OF]->(spouse:Human)-[:MEMBER_OF_GENS]->(gens2:Gens),
      (gens1)-[:ENEMY_OF]-(gens2) DURING war:Event,
      (war)<-[:PARTICIPATED_IN]-(opposing_combatants)
WHERE war.event_type = "civil_war"
RETURN person.name, spouse.name, gens1.name, gens2.name, war.label
```

**Requires**: `MEMBER_OF_GENS`, `SPOUSE_OF`, `ENEMY_OF`, `PARTICIPATED_IN` all present with correct directionality.

---

### **V.6.4 Crosswalk Optionality**

**Benefit**: Functions work without complete crosswalks; crosswalks unlock federation bonuses.

**Function degradation gracefully**:
- **No Wikidata mapping**: Chrystallum queries work fully, federated queries unavailable
- **No CIDOC mapping**: RDF export unavailable, internal Neo4j queries unaffected
- **No CRMinf mapping**: Argumentation tracking uses Chrystallum Claim semantics

**Example**: `PROSCRIBED` has no Wikidata equivalent (Roman-specific), but:
- ✅ Chrystallum queries work: `MATCH (person)-[:PROSCRIBED]->(authority)`
- ❌ Federated SPARQL queries unavailable (no P-property exists)
- ✅ CIDOC export works via `cidoc_crm_code = "E13_Attribute_Assignment"`
- Solution: Export as CIDOC, document "no Wikidata equivalent" in crosswalk CSV

---

## **V.7 Related Decisions**

- **ADR-001** (Appendix U): Content-Only Cipher - enables claim deduplication across time/agents
- **ADR-004** (Appendix W): Facet Taxonomy Canonicalization - 18 canonical facets with enforcement
- **ADR-005** (Appendix X): Federated Claims Signing & Trust Model - institutional signing, transparency logs
- **Section 7**: Relationship Layer - full 311-relationship catalog documentation
- **Appendix A**: Canonical Relationship Types - registry metadata and governance rules
- **Section 7.7**: Key Relationship Types by Domain - examples for major categories

---

## **V.8 References**

- Architecture Review 2026-02-16: `md/Architecture/2-16-26-architecture review.txt`
- Canonical Registry: `Relationships/relationship_types_registry_master.csv` (311 types, 202 implemented, 108 candidate)
- CIDOC-CRM Crosswalk: `CIDOC/cidoc_wikidata_mapping_validated.csv` (105 entity/property mappings)
- CIDOC-CRM Ontology: `CIDOC/CIDOC_CRM_v7.1.2_JSON-LD_Context.jsonld` (official version 7.1.2)
- CRMinf Ontology: `CIDOC/CRMinf_v0.7_.rdfs.txt` (argumentation/inference extension)
- Role Qualifiers: `Relationships/role_qualifier_reference.json` (527 lines, P-value mappings)
- Wikidata Backlog: `Relationships/wikidata_p_unmapped_backlog_2026-02-13.csv`
- Neo4j Loader: `scripts/reference/load_cidoc_crminf_to_neo4j.py`

---

**(End of Appendix V - ADR-002: Relationship Catalog Strategy)**

*Family trees and genealogical networks*

| Relationship Type | Wikidata | Directionality | Description |
|-------------------|----------|----------------|-------------|
| **PARENT_OF** | P40 | inverse | Parent of child |
| **CHILD_OF** | P40 | forward | Person is child of parent |
| **FATHER_OF** | P40 | forward | Father of child |
| **MOTHER_OF** | P40 | forward | Mother of child |
| **SIBLING_OF** | P3373 | symmetric | Person is sibling |
| **SPOUSE_OF** | P26 | symmetric | Person is spouse |
| **GRANDPARENT_OF** | — | inverse | Grandparent of grandchild |
| **GRANDCHILD_OF** | — | forward | Grandchild of grandparent |
| **MEMBER_OF_GENS** | P53 | forward | Roman gens membership |
| **HAS_GENS_MEMBER** | P53 | inverse | Gens has this member |

**Query Example:**
```cypher
// Find Caesar's family tree (3 generations)
MATCH path = (caesar:Human {name: "Caesar"})
             -[:FATHER_OF|CHILD_OF|SIBLING_OF*1..3]-(relative:Human)
RETURN relative.name, length(path) AS degrees_of_separation
```

---

### **V.3.4 Political (10 relationships)**

*Power networks, territorial control, political change*

| Relationship Type | Wikidata | Directionality | Description |
|-------------------|----------|----------------|-------------|
| **CONTROLLED** | P17 | forward | Entity controlled territory |
| **CONTROLLED_BY** | P17 | inverse | Territory controlled by entity |
| **ALLIED_WITH** | — | forward | Formal/strategic alliance |
| **CONQUERED** | — | forward | Entity conquered territory |
| **CONQUERED_BY** | — | inverse | Territory conquered by entity |
| **APPOINTED** | P39 | forward | Entity appointed person to office |
| **APPOINTED_BY** | P39 | inverse | Person appointed by entity |
| **COLLAPSED** | P576 | forward | Political entity ceased |
| **CAUSED_COLLAPSE_OF** | P576 | inverse | Entity caused collapse |
| **DECLARED_FOR** | — | forward | Declared support/allegiance |

**Query Example:**
```cypher
// Find political alliances during Second Punic War
MATCH (rome:Institution {name: "Rome"})
      -[:ALLIED_WITH]-(ally:Institution)
      -[:PARTICIPATED_IN]->(event:Event {label: "Second Punic War"})
RETURN ally.name, event.start_date, event.end_date
```

---

### **V.3.5 Military (7 relationships)**

*Campaigns, battles, military actions*

| Relationship Type | Wikidata | Directionality | Description |
|-------------------|----------|----------------|-------------|
| **FOUGHT_IN** | P607 | forward | Participated in battle/war |
| **BATTLE_PARTICIPANT** | P607 | inverse | Battle had this participant |
| **DEFEATED** | — | forward | Defeated opponent |
| **DEFEATED_BY** | — | inverse | Was defeated by opponent |
| **BESIEGED** | — | forward | Laid siege to place |
| **BESIEGED_BY** | — | inverse | Place besieged by entity |
| **SERVED_UNDER** | — | forward | Served under commander |

**Query Example:**
```cypher
// Find battles of the Gallic Wars and participants
MATCH (war:Event {label: "Gallic Wars"})
      <-[:PART_OF]-(battle:Event)
      <-[:FOUGHT_IN]-(participant:Human)
RETURN battle.label, battle.year, collect(participant.name) AS participants
ORDER BY battle.year
```

---

### **V.3.6 Geographic (7 relationships)**

*Movement, location, geographic context*

| Relationship Type | Wikidata | Directionality | Description |
|-------------------|----------|----------------|-------------|
| **LIVED_IN** | P551 | forward | Person resided in place |
| **RESIDENCE_OF** | P551 | inverse | Place was residence of person |
| **FOUNDED** | P112 | forward | Established place/institution |
| **MIGRATED_FROM** | — | forward | Group migrated from place |
| **MIGRATED_TO** | — | forward | Group migrated to place |
| **FLED_TO** | — | forward | Fled to location (exile/escape) |
| **EXILED** | — | forward | Person exiled to place |

**Query Example:**
```cypher
// Track Cimbri migration route
MATCH path = (cimbri:Group {name: "Cimbri"})
             -[:MIGRATED_FROM|MIGRATED_TO*]-(place:Place)
RETURN nodes(path) AS migration_path
```

---

### **V.3.7 Authorship & Attribution (7 relationships)**

*Provenance, evidence, claims about knowledge*

| Relationship Type | Wikidata | Directionality | Description |
|-------------------|----------|----------------|-------------|
| **CREATOR** | P170 | forward | Created by |
| **CREATION_OF** | P170 | inverse | Created by (inverse) |
| **DESCRIBES** | — | forward | Citation describes entity |
| **MENTIONS** | — | forward | Citation mentions entity |
| **NAMED_AFTER** | P138 | forward | Named for |
| **NAMESAKE_OF** | P138 | inverse | Is namesake of |
| **DISCOVERED_BY** | P61 | forward | Discovered by |

**Query Example:**
```cypher
// Find all works that mention Caesar and their authors
MATCH (caesar:Human {name: "Caesar"})
      <-[:MENTIONS]-(work:Work)
      -[:AUTHOR]->(author:Human)
RETURN work.label, author.name, work.publication_year
ORDER BY work.publication_year
```

---

### **V.3.8 Temporal & Institutional (5 relationships)**

*Time, organizations, institutional changes*

| Relationship Type | Wikidata | Directionality | Description |
|-------------------|----------|----------------|-------------|
| **LEGITIMATED** | — | forward | Institution legitimated authority |
| **LEGITIMATED_BY** | — | inverse | Authority legitimated by institution |
| **REFORMED** | — | forward | Reformed institution/system |
| **ADHERES_TO** | P1142 | forward | Person/org adheres to ideology |
| **IDEOLOGY_OF** | P1142 | inverse | Ideology adhered to by person/org |

---

### **V.3.9 v1.0 Kernel Statistics**

- **Total Relationships**: 48 types (intentionally under 50 for focused scope)
- **Wikidata Mapped**: 28 (58% - strong federation capability)
- **CIDOC-CRM Mapped**: To be validated during v1.0 implementation
- **Categories Covered**: 7 of 31 (focused on core historical research)
- **Lifecycle Status**: 100% `implemented` (all ready for production)

**Capabilities Unlocked:**
✅ Family tree construction and genealogical queries  
✅ Political network analysis (alliances, conquests, appointments)  
✅ Military campaign tracking (battles, participants, outcomes)  
✅ Geographic movement and settlement patterns  
✅ Work attribution and provenance chains  
✅ Institutional legitimacy and reform tracking  
✅ Basic temporal reasoning and organizational membership  

---

## **V.4 Staged Expansion Plan**

### **V.4.1 Tier 2: v1.1 Specialized Research (50-75 relationships)**

**Target Domains:**
- **Legal**: Convictions, sentences, trials, legal codes
- **Economic**: Trade, taxation, production, slavery
- **Diplomatic**: Negotiations, envoys, treaties, appeals
- **Cultural**: Assimilation, cultural evolution, heritage claims
- **Religious**: Conversion, religious leadership, doctrine
- **Honorific**: Awards, titles, decorations, patronage

**Inclusion Criteria:**
- Extends v1.0 kernel into specialized research domains
- Enables advanced queries (legal proceedings, trade networks, cultural transmission)
- lifecycle_status = "implemented" OR strong evidence for implementation
- Documentation includes cross-references to v1.0 kernel relationships

**Migration Strategy:**
- Add Tier 2 relationships as new edge types (no v1.0 changes)
- Queries using only v1.0 relationships remain unaffected
- New queries can combine v1.0 + v1.1 relationships

---

### **V.4.2 Tier 3: v2.0 Full Catalog (175-200 relationships)**

**Target Domains:**
- **Application**: Material extraction, dyeing, production locations
- **Evolution**: Type obsolescence, phasing out, replacement chains
- **Reasoning**: Inference chains, belief adoption, evidence relationships
- **Comparative**: Superiority, inferiority, advantages/disadvantages
- **Functional**: Purpose, use, instrument relationships
- **Moral**: Ethical justification, moral reasoning

**Inclusion Criteria:**
- Completes comprehensive domain coverage
- Supports specialized scholarly workflows (material culture, technological evolution, intellectual history)
- May include lifecycle_status = "candidate" (requires implementation first)
- Full CIDOC-CRM and Wikidata triple alignment

**Migration Strategy:**
- Add Tier 3 relationships incrementally (not all at once)
- Each addition requires: implementation, testing, documentation, example queries
- Deprecation policy: No removal of v1.0/v1.1 relationships without 12-month notice

---

## **V.5 Implementation Strategy**

### **V.5.1 Development Phases**

**Phase 1: v1.0 Kernel (Current Priority)**
1. ✅ Document 48 essential relationships (this appendix)
2. ⏳ Create Neo4j seed script: `Relationships/v1_kernel_seed.cypher`
3. ⏳ Implement validation: Check all v1.0 relationships exist in registry
4. ⏳ Test coverage: Unit tests for each relationship type
5. ⏳ Documentation: Update Section 7.7 with v1.0 kernel examples
6. ⏳ Production deployment: Load v1.0 kernel into Neo4j with constraints

**Phase 2: v1.1 Expansion (Next)**
1. Identify 50-75 Tier 2 relationships from registry (Legal, Economic, Diplomatic, Cultural, Religious, Honorific)
2. Validate lifecycle_status = "implemented" or implement missing relationships
3. Create `Relationships/v1.1_expansion_seed.cypher` (additive, non-breaking)
4. Test v1.0 + v1.1 combined queries
5. Documentation: Appendix V.4.1 expansion

**Phase 3: v2.0 Full Catalog (Long-term)**
1. Implement remaining "candidate" relationships (requires field work, authority alignment)
2. Complete CIDOC-CRM triple alignment for all 300 relationships
3. Deprecation policy: Define sunset procedures for unused relationships
4. Versioning: Track relationship schema versions (v1.0 → v1.1 → v2.0)

---

### **V.5.2 Validation Checklist**

Before promoting a relationship from candidate → implemented:
- [ ] Wikidata property alignment verified (or documented why not applicable)
- [ ] CIDOC-CRM property alignment verified (or documented why not applicable)
- [ ] Directionality tested (forward/inverse/symmetric/unidirectional)
- [ ] Example query demonstrates practical usage
- [ ] Neo4j constraint created (if applicable)
- [ ] Documentation updated in Section 7.7 and Appendix V

---

### **V.5.3 Migration Rules**

**Adding New Relationships (Non-Breaking):**
- New relationship types can be added at any time
- Existing queries using v1.0/v1.1 relationships remain valid
- New edge types do not affect existing traversal patterns

**Deprecating Relationships (Breaking - Requires Migration):**
- 12-month deprecation notice required before removal
- Provide migration path: `OLD_RELATIONSHIP` → `NEW_RELATIONSHIP` mapping
- Automated migration script: Rewrite edges from deprecated to replacement type
- Documentation: Update all examples removing deprecated relationships

**Renaming Relationships (Breaking - Avoid):**
- Rename = Deprecate + Add New (12-month migration window)
- Prefer adding aliases via registry metadata (keep canonical name stable)

**Changing Directionality (Breaking - Avoid):**
- Do NOT change directionality of existing relationships
- If directionality was wrong, create new relationship with correct directionality
- Deprecate old relationship with migration path

---

## **V.6 Benefits of Kernel Approach**

### **V.6.1 Development Velocity**

- **Ship v1.0 kernel fast**: 48 relationships instead of 300 (84% reduction)
- **Test coverage feasible**: Comprehensive tests for 48 types vs. impractical for 300
- **Documentation complete**: Full usage examples for v1.0 instead of partial coverage

### **V.6.2 Operational Correctness**

- **Real-world validation**: v1.0 kernel tested in production before expanding
- **Query patterns emerge**: Understand actual usage before adding specialized relationships
- **Performance tuning**: Optimize 48 relationships before complexity increases

### **V.6.3 Maintenance Simplicity**

- **Focused schema evolution**: Changes impact 48 types, not 300
- **Clear deprecation boundaries**: Tier boundaries guide sunset decisions
- **Incremental complexity**: Add relationships only when justified by research needs

### **V.6.4 Federation Readiness**

- **Strong Wikidata alignment**: 58% of v1.0 kernel has Wikidata properties
- **Federated queries work**: Can query external SPARQL endpoints via aligned properties
- **Interoperability proven**: Validate federation with 48 types before scaling

---

## **V.7 Related Decisions**

- **ADR-001**: Content-Only Cipher (Appendix U) - claim deduplication across time/agents
- **ADR-003** (future): Facet Taxonomy Canonicalization - single registry enforcement
- **Section 7**: Relationship Layer - full 300-relationship catalog documentation
- **Appendix A**: Canonical Relationship Types - registry of all 300 relationships
- **Section 7.7**: Key Relationship Types by Domain - examples for major categories

---

## **V.8 References**

- Architecture Review 2026-02-16 (md/Architecture/2-16-26-architecture review.txt)
- Canonical Registry: `Relationships/relationship_types_registry_master.csv` (300 types, 202 implemented, 108 candidate)
- v1.0 Kernel Seed Script: `Relationships/v1_kernel_seed.cypher` (to be created)
- Section 7.1: Relationship Type Schema (canonical properties and fields)
- Section 7.2: Relationship Categories (distribution by category)

---

**(End of Appendix V - ADR-002: Relationship Kernel Strategy)**

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

# **Appendix X: Federated Claims Signing & Cryptographic Trust Model (ADR-005)**

**Status**: ACCEPTED (2026-02-16, Architecture Review Issue #6)

**Context & Problem**

The system currently describes **content-addressable claims** (`cipher` = SHA256 of claim content) and **Merkle trees** for verifying claim integrity. However, the architecture underspecifies **how institutions establish trust across boundaries** when exchanging claims:

- Who signs claims? (Institution? Individual agents? Query endpoints?)
- How do external institutions discover/verify a signing key? (Centralized registry? DNSSEC? DHT?)
- What happens when two institutions provide conflicting signed claims? (Competing signatures, same cipher)
- How are compromised keys handled? (Revocation, rotation, retroactive audit)
- Can a single institution operate without signing? (Personal research tool vs. federated authority)

**Current state**: Cryptographic verification works for integrity (cipher + Merkle root) but not for **provenance authentication** across institutional boundaries. A claim could be valid content (matches cipher) but falsely attributed to the wrong endpoint.

**Evidence of underspecification**:

1. Section 6.4.2 discusses "institutional signature" but doesn't specify format
2. Section 6.4 mentions "state_root" (Merkle tree) but not cryptographic signatures
3. Appendix R (Federation Strategy) describes authority layers but not institutional key distribution
4. No dispute resolution model for conflicting signed claims

---

## **X.1 Decision & Solution**

**Adopt a three-tier federated trust model** combining institutional signing, transparency logging, and cryptographic verification:

### **X.1.1 Signing Model: Institutional Claims Authority**

**Principle**: Each institution that publishes claims must operate an **institutional signing authority** with:

1. **Long-term key pair** (Ed25519 or RSA-4096):
   - Public key: Published in institutional registry (DNS TXT record or `.well-known/chrystallum.json`)
   - Private key: Stored in hardware security module (HSM) or trusted key management service
   - Key ID: Calculated from public key fingerprint (first 16 chars of SHA256)

2. **Per-claim signature**:
   - Signs the content hash (cipher), not the full claim data
   - Format: `<institution_key_id>.<timestamp>.<proof_chain_root>`
   - Proof chain root: Merkle root of all claims signed in same batch (~5min window)

3. **Institutional registry entry**:
   ```json
   {
     "institution": "University of Oxford",
     "endpoint": "https://claims-api.ox.ac.uk",
     "public_key_id": "ox_2026_0a1b",
     "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
     "key_algorithm": "Ed25519",
     "key_rotated_at": "2026-01-15T00:00:00Z",
     "transparency_log": "https://claims-transparency.ox.ac.uk",
     "signing_policy": "https://claims-api.ox.ac.uk/.well-known/signing-policy.txt",
     "contact": "claims-admin@ox.ac.uk"
   }
   ```

**Benefits**:
- Verifiable without centralized certificate authority (DIY PublicKeyInfrastructure)
- Key rotation via timestamp (old signatures still valid with historical key)
- Accountability: Signed claims tied to institution, not individual agents

**Limitations**:
- Institutions must operate key management infrastructure
- DNS/registry poisoning possible (recommend DNSSEC + pinning)
- No online revocation (timestamp-based keys don't support instant revocation)

---

### **X.1.2 Claim Signing Structure**

**Every signed claim contains**:

```json
{
  "claim_id": "claim_00456",
  "cipher": "sha256_abc123def456...",
  "content": { /* claim data */ },
  
  // CRYPTOGRAPHIC PROVENANCE
  "signatures": [
    {
      "institution_key_id": "ox_2026_0a1b",
      "timestamp": "2026-02-16T10:30:00Z",
      "algorithm": "Ed25519",
      "value": "30450220_0761_43d0_8c67_8a3a9c2d1b4f...",
      
      // PROOF CHAIN (enables transparency verification)
      "proof_chain_root": "merkle_root_batch_2026_02_16_10_30",
      "proof_chain_path": ["leaf_hash_1", "parent_hash_2", "parent_hash_3"],
      
      // BATCH CONTEXT (links to transparency log entry)
      "batch_id": "batch_2026_02_16_10_30_001",
      "batch_index": 23,  // This claim is #23 in batch
      "batch_log_url": "https://claims-transparency.ox.ac.uk/batch/2026_02_16_10_30_001"
    }
  ],
  
  // VERIFICATION RECEIPT (used to re-fetch key + signature proof)
  "verification_receipt": {
    "institution": "University of Oxford",
    "key_registry_url": "https://claims-api.ox.ac.uk/.well-known/chrystallum.json",
    "verified_at": "2026-02-16T10:30:05Z"
  }
}
```

**Signature verification algorithm**:

```python
def verify_claim_signature(claim: dict, institutional_registry: dict) -> bool:
    """
    Verify a claim's cryptographic signature.
    
    Args:
        claim: Claim with signatures field
        institutional_registry: Dict mapping institution_key_id → public_key
    
    Returns:
        True if signature valid, False otherwise
    """
    for sig in claim.get("signatures", []):
        key_id = sig["institution_key_id"]
        pub_key = institutional_registry.get(key_id)
        
        if not pub_key:
            logger.warning(f"Unknown key ID: {key_id}")
            continue
        
        # Re-hash the cipher to verify signature wasn't tampered
        signed_data = f"{claim['cipher']}.{sig['timestamp']}.{sig['proof_chain_root']}"
        
        try:
            # Import public key and verify
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(
                base64.b64decode(pub_key)
            )
            public_key.verify(
                base64.b64decode(sig["value"]),
                signed_data.encode()
            )
            logger.info(f"✓ Signature valid for key {key_id}")
            return True
        except cryptography.exceptions.InvalidSignature:
            logger.error(f"✗ Signature invalid for key {key_id}")
            return False
    
    logger.warning("No valid signatures found")
    return False
```

---

### **X.1.3 Institutional Registry & Key Distribution**

**Institutions publish public keys via**:

1. **DNS TXT record** (DNSSEC-protected):
   ```
   _chrystallum.ox.ac.uk. IN TXT "v=chrys1; key_id=ox_2026_0a1b; pubkey=MIIBIjANBgk... ; endpoint=https://claims-api.ox.ac.uk"
   ```

2. **`.well-known/chrystallum.json`** (served over HTTPS with HSTS):
   ```json
   {
     "institution": "University of Oxford",
     "keys": [
       {
         "key_id": "ox_2026_0a1b",
         "public_key": "-----BEGIN PUBLIC KEY-----\n...",
         "valid_from": "2026-01-15T00:00:00Z",
         "valid_until": "2027-01-15T00:00:00Z",
         "algorithm": "Ed25519",
         "rotate_next": "2027-01-01T00:00:00Z"
       },
       {
         "key_id": "ox_2025_1c2d",
         "public_key": "-----BEGIN PUBLIC KEY-----\n...",
         "valid_from": "2025-01-15T00:00:00Z",
         "valid_until": "2026-01-15T00:00:00Z",
         "algorithm": "Ed25519",
         "retired": true
       }
     ],
     "transparency_log": "https://claims-transparency.ox.ac.uk",
     "policy": "https://claims-api.ox.ac.uk/.well-known/signing-policy.txt"
   }
   ```

3. **Federated registry service** (optional, maintained by consortium):
   - Gossip protocol to sync key updates
   - Prevents DNS-only dependency
   - Enables pin/revocation signaling

**Key rotation**: 
- Short-lived keys (12 months), new key added 3 months before expiry
- Old keys kept in registry for 2+ years to verify historical signatures
- Revocation via "revoked" flag + reasoning field (compromise, transition, etc.)

---

### **X.1.4 Transparency Logging for Dispute Resolution**

**Problem**: If two institutions claim to have authored the same content (same cipher), which signature is authoritative?

**Solution**: Each institution maintains an **append-only transparency log** of all claims it signs, enabling:
- Auditability: "Did institution X sign this claim on date Y?"
- Consistency: Proving no clock skew (same cipher never signed twice in 24h)
- Repudiation resistance: Institution can't deny signing a claim once in public log

**Transparency log structure** (similar to Certificate Transparency [RFC 6962]):

```json
{
  "version": "chrystallum_ct/2026-01-01",
  "batch_id": "batch_2026_02_16_10_30_001",
  "batch_timestamp": "2026-02-16T10:30:00Z",
  "batch_root": "merkle_root_abc123",
  "entries": [
    {
      "index": 1,
      "claim_id": "claim_00123",
      "cipher": "sha256_xyz789",
      "timestamp": "2026-02-16T10:30:01Z",
      "facet": "DIPLOMATIC",
      "geographic_scope": "Rome",
      "temporal_scope": "-27/14",
      "source_id": "source_001_plb_001",
      "signature": "30450220_...",
      "leaf_hash": "hash_of_this_entry"
    },
    ...
  ],
  "batch_proof": {
    "tree_size_before": 45678,
    "tree_size_after": 45800,
    "tree_root": "merkle_root_post_batch",
    "consistency_proof": ["proof_hash_1", "proof_hash_2"]
  }
}
```

**Dispute resolution using transparency logs**:

```python
def resolve_signature_conflict(cipher: str, sig1: dict, sig2: dict) -> str:
    """
    When two institutions claim to have signed the same content (same cipher),
    determine which signature should be trusted.
    
    Algorithm:
    1. Both signatures must be in respective transparency logs
    2. Earlier timestamp wins (first publisher)
    3. If timestamps identical, institution_key_id alphabetically first wins
    4. If institution disputes entry in log, requires cryptographic proof
       of log tampering (detectable via tree hash consistency mismatches)
    """
    
    # Verify both signatures are in respective transparency logs
    log1_valid = fetch_from_transparency_log(
        sig1["institution_key_id"], 
        sig1["batch_id"], 
        sig1["batch_index"]
    )
    log2_valid = fetch_from_transparency_log(
        sig2["institution_key_id"], 
        sig2["batch_id"], 
        sig2["batch_index"]
    )
    
    if not (log1_valid and log2_valid):
        raise ConflictResolutionError(
            f"Cannot resolve: one signature not in transparency log"
        )
    
    t1 = datetime.fromisoformat(sig1["timestamp"])
    t2 = datetime.fromisoformat(sig2["timestamp"])
    
    if t1 < t2:
        return "sig1"  # Sig1 has earlier timestamp, sig1 wins
    elif t2 < t1:
        return "sig2"
    else:
        # Timestamps identical (should be rare, within same batch)
        # Break tie alphabetically
        return "sig1" if sig1["institution_key_id"] < sig2["institution_key_id"] else "sig2"
```

**Transparency log verification** (client-side audit):

```python
def audit_transparency_log(batch_data: dict, previous_root: str) -> bool:
    """
    Verify a transparency log batch hasn't been tampered with.
    
    Uses merkle tree consistency proofs to ensure:
    1. No entries were removed from previous batches
    2. No entries were added out-of-order
    3. Tree structure matches announced root
    """
    
    # Compute tree root from entries
    computed_root = merkle_tree_from_entries(batch_data["entries"])
    
    if computed_root != batch_data["batch_root"]:
        raise LogTamperDetected("Batch root mismatch")
    
    # Verify consistency proof (linking to previous tree)
    if not verify_merkle_consistency_proof(
        previous_root=previous_root,
        new_root=batch_data["batch_root"],
        consistency_proof=batch_data["batch_proof"]["consistency_proof"],
        tree_size_before=batch_data["batch_proof"]["tree_size_before"],
        tree_size_after=batch_data["batch_proof"]["tree_size_after"]
    ):
        raise LogTamperDetected("Consistency proof verification failed")
    
    logger.info(f"✓ Transparency log batch {batch_data['batch_id']} verified")
    return True
```

---

### **X.1.5 Verification Flow for External Institutions**

**Harvard researcher wants to verify a claim published by Oxford:**

```python
def verify_external_claim(claim_url: str) -> dict:
    """
    Full verification flow for a claim published by external institution.
    """
    
    # Step 1: Fetch claim from external endpoint
    claim = requests.get(claim_url).json()
    cipher = claim["cipher"]
    
    # Step 2: Verify cipher matches content (integrity check)
    computed_cipher = sha256(json.dumps(claim["content"])).hexdigest()
    if computed_cipher != cipher:
        raise IntegrityError("Content doesn't match cipher")
    
    # Step 3: Fetch institutional public key
    institution = claim["verification_receipt"]["institution"]
    key_registry_url = claim["verification_receipt"]["key_registry_url"]
    registry = requests.get(key_registry_url).json()
    
    pub_key = None
    for sig in claim["signatures"]:
        key_id = sig["institution_key_id"]
        for key_entry in registry["keys"]:
            if key_entry["key_id"] == key_id:
                pub_key = key_entry["public_key"]
                break
    
    if not pub_key:
        raise KeyNotFoundError(f"Public key not found for claim")
    
    # Step 4: Verify cryptographic signature
    if not verify_claim_signature(claim, {key_id: pub_key}):
        raise SignatureError("Signature verification failed")
    
    # Step 5: Audit transparency log entry
    for sig in claim["signatures"]:
        batch = requests.get(sig["batch_log_url"]).json()
        if not audit_transparency_log(batch, previous_root):
            raise LogTamperDetected("Transparency log tampered")
    
    logger.info(f"✓ Claim {claim['claim_id']} verified with institutional signature")
    return {
        "verified": True,
        "institution": institution,
        "signatures": len(claim["signatures"]),
        "timestamp": claim["signatures"][0]["timestamp"]
    }
```

---

## **X.2 Rationale & Evidence**

**Why this approach?**

1. **Verifiable without central authority**: Each institution is responsible for its own keys (like DNSSEC)
2. **Enables dispute resolution**: Transparency logs provide immutable audit trail
3. **Compatible with existing cipher model**: Signatures are separate from content hash
4. **Scales to consortiums**: Multiple institutions can sign same claim (consensus) or conflicting claims (logged)
5. **Supports anonymous research**: Single-institution queries don't require signing

**Precedent**:
- **Certificate Transparency** (RFC 6962): Transparency logs for X.509 certificates, detects unauthorized certificates
- **Sigsum** (formerly Trillian fork): Alternative to CT for verifiable transparency logs
- **HyperLedger Fabric**: Multi-organization signing with cryptographic proofs

**Evidence of feasibility**:
- OpenSSL/cryptography libraries support Ed25519 + Merkle trees
- DNSSEC infrastructure exists (institutions with .well-known already trusted)
- Transparency logs proven in production (Google, DigiCert, Let's Encrypt)

---

## **X.3 Consequences**

### **Positive**:
- ✅ **Verifiable provenance**: Claims cryptographically tied to institutions, not forgers
- ✅ **Dispute resolution**: Transparency logs provide evidence of "who signed first"
- ✅ **Retroactive audit**: Historical claims auditable even after key rotation
- ✅ **Consortium operations**: Multiple institutions can sign same claim for consensus
- ✅ **Enables federation trust**: Solves "how do we trust external claims?" without central authority

### **Negative**:
- ⚠️ **Key management complexity**: Institutions must operate HSM or equivalent (support burden)
- ⚠️ **DNS dependency**: Key distribution requires DNSSEC or alternative (not all registrars support)
- ⚠️ **Transparency log scaling**: Append-only logs grow continuously (mitigated by log rotation + archival)
- ⚠️ **No real-time revocation**: Compromised keys can't be instantly revoked (timestamp-based keys expire naturally)

### **Neutral**:
- ○ Single-institution deployments can operate without external signing
- ○ Claim cipher remains unchanged (backward compatible)
- ○ Batch signing reduces per-claim overhead

---

## **X.4 Implementation Requirements**

### **X.4.1 Backend: Institutional Signing Authority**

**Required changes to claim creation workflow**:

```python
# Python pseudocode for claim creation with signing

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import hashes, serialization
from datetime import datetime, timedelta
import hashlib
import json

class InstitutionalSigningAuthority:
    """Manages institutional claim signing."""
    
    def __init__(self, private_key_path: str, institution_id: str):
        with open(private_key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None
            )
        self.institution_id = institution_id
        self.batch_claims = []
        self.batch_timestamp = None
    
    def sign_claim(self, claim: dict, facet: str, source_id: str) -> dict:
        """
        Sign a claim and add to current batch.
        
        Args:
            claim: Claim dictionary with 'cipher' field
            facet: Facet classification (e.g., 'DIPLOMATIC')
            source_id: Source passage ID
        
        Returns:
            Claim with signatures field populated
        """
        
        # Create batch if needed
        if self.batch_timestamp is None:
            self.batch_timestamp = datetime.utcnow()
            self.batch_id = f"batch_{self.batch_timestamp.isoformat().replace(':', '').replace('.', '_')}"
        
        # Build signature input
        timestamp = datetime.utcnow().isoformat() + "Z"
        proof_chain_root = self.compute_batch_merkle_root()  # Recomputed as batch grows
        
        signed_data = f"{claim['cipher']}.{timestamp}.{proof_chain_root}".encode()
        signature = self.private_key.sign(signed_data)
        
        # Generate key ID from public key
        pub_key_bytes = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        key_fingerprint = hashlib.sha256(pub_key_bytes).hexdigest()[:16]
        key_id = f"{self.institution_id}_2026_{key_fingerprint}"
        
        # Add signature
        sig_entry = {
            "institution_key_id": key_id,
            "timestamp": timestamp,
            "algorithm": "Ed25519",
            "value": signature.hex(),
            "proof_chain_root": proof_chain_root,
            "proof_chain_path": self.compute_merkle_path(len(self.batch_claims)),
            "batch_id": self.batch_id,
            "batch_index": len(self.batch_claims),
            "batch_log_url": f"https://claims-transparency.{self.institution_id}.edu/batch/{self.batch_id}"
        }
        
        # Add metadata
        claim["signatures"] = [sig_entry]
        claim["verification_receipt"] = {
            "institution": self.institution_id,
            "key_registry_url": f"https://claims-api.{self.institution_id}.edu/.well-known/chrystallum.json",
            "verified_at": timestamp
        }
        
        # Buffer for transparency log
        self.batch_claims.append({
            "claim": claim,
            "facet": facet,
            "source_id": source_id
        })
        
        # Flush batch if it reaches size threshold or time limit
        if len(self.batch_claims) >= 100 or \
           (datetime.utcnow() - self.batch_timestamp).total_seconds() > 300:
            self.flush_batch()
        
        return claim
    
    def compute_batch_merkle_root(self) -> str:
        """Compute Merkle root of current batch claims."""
        if not self.batch_claims:
            return hashlib.sha256(b"empty_batch").hexdigest()
        
        leaves = [
            hashlib.sha256(entry["claim"]["cipher"].encode()).digest()
            for entry in self.batch_claims
        ]
        
        while len(leaves) > 1:
            if len(leaves) % 2 == 1:
                leaves.append(leaves[-1])  # Duplicate last for odd trees
            leaves = [
                hashlib.sha256(leaves[i] + leaves[i+1]).digest()
                for i in range(0, len(leaves), 2)
            ]
        
        return leaves[0].hex() if leaves else hashlib.sha256(b"empty").hexdigest()
    
    def compute_merkle_path(self, leaf_index: int) -> list:
        """Compute Merkle path from leaf to root."""
        # Simplified; full implementation would track tree structure
        # Returns list of sibling hashes needed to compute root
        return ["sibling_hash_1", "sibling_hash_2"]  # Placeholder
    
    def flush_batch(self):
        """Publish batch to transparency log and reset."""
        if not self.batch_claims:
            return
        
        batch_log_entry = {
            "batch_id": self.batch_id,
            "batch_timestamp": self.batch_timestamp.isoformat() + "Z",
            "batch_root": self.compute_batch_merkle_root(),
            "entries": [
                {
                    "claim_id": entry["claim"]["claim_id"],
                    "cipher": entry["claim"]["cipher"],
                    "timestamp": entry["claim"]["signatures"][0]["timestamp"],
                    "facet": entry["facet"],
                    "source_id": entry["source_id"]
                }
                for entry in self.batch_claims
            ]
        }
        
        # POST to transparency log endpoint
        requests.post(
            f"https://claims-transparency.{self.institution_id}.edu/batch",
            json=batch_log_entry,
            timeout=30
        )
        
        logger.info(f"Flushed batch {self.batch_id} with {len(self.batch_claims)} claims")
        self.batch_claims = []
        self.batch_timestamp = None
```

### **X.4.2 Configuration: Institutional Signing Setup**

**New config file: `config_signing.yaml`**

```yaml
# Institutional Signing Configuration
institution:
  name: "University of Oxford"
  domain: "ox.ac.uk"
  endpoint: "https://claims-api.ox.ac.uk"
  contact: "claims-admin@ox.ac.uk"

signing:
  # Path to Ed25519 private key (must be protected by permissions 0600)
  private_key_path: "/etc/chrystallum/secrets/ox_signing_key_2026.pem"
  
  # Key metadata
  key_id: "ox_2026_0a1b"
  algorithm: "Ed25519"
  valid_from: "2026-01-15T00:00:00Z"
  valid_until: "2027-01-15T00:00:00Z"
  rotate_next: "2027-01-01T00:00:00Z"
  
  # Batch settings
  batch_size_threshold: 100  # Flush after 100 claims
  batch_time_threshold_seconds: 300  # Flush after 5 minutes
  
transparency_log:
  # Append-only log of all signed claims
  endpoint: "https://claims-transparency.ox.ac.uk"
  storage_type: "postgresql"  # postgresql, sqlite, s3
  storage_connection: "postgresql://tlog:secret@tlog.ox.ac.uk/chrystallum_tlog"
  
key_registry:
  # Published at .well-known/chrystallum.json
  publish_url: "https://claims-api.ox.ac.uk/.well-known/chrystallum.json"
  include_retired_keys: true  # Keep old keys for historical verification
  retired_key_retention_days: 730  # 2 years
```

### **X.4.3 Deployment: Key Generation & Rotation**

**Script: `scripts/setup_institutional_signing.sh`**

```bash
#!/bin/bash
# Initialize institutional signing authority

INSTITUTION=$1
PRIVATE_KEY_PATH="/etc/chrystallum/secrets/${INSTITUTION}_signing_key.pem"
YEARS_VALID=1

if [ -z "$INSTITUTION" ]; then
    echo "Usage: setup_institutional_signing.sh <institution_domain>"
    exit 1
fi

# Generate Ed25519 private key
openssl genpkey -algorithm ed25519 -out "$PRIVATE_KEY_PATH"
chmod 0600 "$PRIVATE_KEY_PATH"

# Extract public key
PUBKEY_PATH="/etc/chrystallum/secrets/${INSTITUTION}_pubkey.pem"
openssl pkey -in "$PRIVATE_KEY_PATH" -pubout -out "$PUBKEY_PATH"

# Calculate key ID (first 16 chars of key fingerprint)
KEY_ID=$(openssl pkey -pubin -in "$PUBKEY_PATH" -text -noout | \
         grep -A1 "pub:" | tail -1 | \
         tr -d ' :' | \
         head -c 16)

echo "✓ Generated signing key for $INSTITUTION"
echo "  Private key: $PRIVATE_KEY_PATH"
echo "  Public key: $PUBKEY_PATH"
echo "  Key ID: ${INSTITUTION}_2026_${KEY_ID}"
echo ""
echo "Next steps:"
echo "1. Publish public key at: https://${INSTITUTION}/.well-known/chrystallum.json"
echo "2. Configure config_signing.yaml with private_key_path and key_id"
echo "3. Set up transparency log database"
echo "4. Test signing with: python -m chrystallum.signing test-sign"
```

### **X.4.4 Validation: Signature Verification Tests**

**Unit tests in `tests/test_signing.py`**:

```python
import pytest
from chrystallum.signing import verify_claim_signature, InstitutionalSigningAuthority

def test_claim_signature_verification():
    """Test that signed claims can be verified."""
    authority = InstitutionalSigningAuthority(
        private_key_path="tests/fixtures/test_key.pem",
        institution_id="test_institution"
    )
    
    claim = {
        "claim_id": "test_001",
        "cipher": "sha256_abc123",
        "content": {"subject": "Q1048", "object": "Q5"}
    }
    
    # Sign claim
    signed_claim = authority.sign_claim(claim, facet="DIPLOMATIC", source_id="test_src")
    
    # Verify signature
    registry = {
        signed_claim["signatures"][0]["institution_key_id"]: 
            "-----BEGIN PUBLIC KEY-----\n..."
    }
    
    assert verify_claim_signature(signed_claim, registry) is True

def test_signature_tampering_detection():
    """Test that tampered signatures are rejected."""
    # Modify cipher after signing
    signed_claim["cipher"] = "sha256_different"
    
    assert verify_claim_signature(signed_claim, registry) is False

def test_transparency_log_consistency():
    """Test that transparency log consistency proofs work."""
    batch1 = create_batch([claim1, claim2, claim3])
    batch2 = create_batch([claim4, claim5])
    
    # Verify batch1 and batch2 form consistent append-only log
    assert verify_merkle_consistency_proof(
        batch1["batch_root"],
        batch2["batch_root"],
        batch2["batch_proof"]["consistency_proof"],
        tree_size_before=3,
        tree_size_after=5
    ) is True
```

---

## **X.5 Related Decisions**

- **ADR-001** (Appendix U): Content-Only Cipher - signatures separate from cipher
- **ADR-002** (Appendix V): Function-Driven Relationship Catalog - organizing claim types
- **ADR-004** (Appendix W): Canonical 18-Facet System - classifying signed claims
- **Section 6.4**: Cryptographic Verification (cipher + Merkle tree)
- **Appendix R**: Federation Strategy (institutional authorities, confidence layers)

---

## **X.6 References**

- RFC 6962: Certificate Transparency (transparency log pattern)
- Sigsum: Verifiable Transparency Logs (alternative CT design)
- HyperLedger Fabric: Multi-org signing (consortium signing model)
- DNSSEC RFC 4033-4035: Securing DNS (key distribution via DNS TXT)
- Ed25519 (RFC 8037): Elliptic curve signing (cryptographic algorithm)
- Merkle Tree Consistency Proofs: RFC 6962 Section 2.1.4

---

**(End of Appendix X - ADR-005: Federated Claims Signing & Cryptographic Trust Model)**

---

## **Appendix Y: v0 Bootstrap Scaffolding Contract (2026-02-17 Decisions)**

**Status:** Normative for v0 bootstrap and scaffold/promotion boundaries.  
**Source Input:** `md/Architecture/2-17-26-CHRYSTALLUM_v0_AGENT_BOOTSTRAP_SPEC.md`

### **Y.1 Scope and precedence**

For v0 bootstrap workflows, this appendix supersedes conflicting legacy examples in this consolidated file.

### **Y.2 Canonical vs scaffold boundary**

- Canonical writes are promotion-gated.
- Bootstrap and SFA pre-promotion writes are scaffold-only.
- Scaffold labels are distinct from canonical labels.

### **Y.3 Required scaffold labels**

- `:ScaffoldNode`
- `:ScaffoldEdge`
- `:AnalysisRun` (canonical run anchor reused)

### **Y.4 Required scaffold edge contract**

Scaffold edge-as-node pattern:

```cypher
(e:ScaffoldEdge)-[:FROM]->(s:ScaffoldNode)
(e:ScaffoldEdge)-[:TO]->(o:ScaffoldNode)
```

Required ScaffoldEdge properties:
- `edge_id`
- `analysis_run_id`
- `relationship_type`
- `wd_property`
- `direction`
- `confidence`
- `created_at`

### **Y.5 Bootstrap traversal controls (v0 defaults)**

- Upward P31/P279 depth: `4`
- Lateral mapped-property hops: `2` (mapped properties only)
- Downward inverse P279 depth: `2`
- Inverse P31: sampling only (bounded)
- Hard caps and NOT-filters must be logged with truncation metadata

### **Y.6 Canonical facet topology**

```cypher
(:Claim)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun)-[:HAS_FACET_ASSESSMENT]->(:FacetAssessment)-[:ASSESSES_FACET]->(:Facet)
```

### **Y.7 Promotion contract**

Promotion service:
1. Validates candidates against filter/meta-ceiling policy.
2. Merges canonical nodes.
3. Creates canonical relationships (registry-approved types only).
4. Creates/attaches canonical claims and evidence where needed.
5. Records a promotion event linking promoted artifacts to `analysis_run_id` and source scaffold artifacts.

### **Y.8 Occupation/profession policy**

- No first-class `:Occupation` node label in canonical model.
- Profession/occupation concepts canonize as `:SubjectConcept` when approved.
- Human-profession assertions require temporal bounding.

---

