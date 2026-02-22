# Appendix P: Semantic Enrichment Ontology Alignment

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

