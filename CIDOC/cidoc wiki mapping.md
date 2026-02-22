#cidoc wiki mapping
Perfect! Now I have comprehensive information. Let me create a detailed mapping document for you. Based on the CIDOC-CRM structure and Wikidata's approach to cultural heritage, here's the comprehensive mapping:

***

# **CIDOC-CRM to Wikidata Mapping**
## **For Chrystallum Integration**

### **Mapping Methodology**

CIDOC-CRM uses a different ontological approach than Wikidata:
- **CIDOC-CRM**: Event-centric, focuses on activities and temporal entities
- **Wikidata**: Entity-centric, uses statements with qualifiers

**Mapping Strategy:**
1. **Direct equivalents** where Wikidata has specific properties (rare)
2. **Approximate mappings** where Wikidata concepts can represent CRM intent
3. **Composite mappings** where multiple Wikidata properties + qualifiers = 1 CRM class
4. **No mapping** where CRM is more granular than Wikidata supports

***

## **I. CIDOC-CRM CORE CLASSES → Wikidata**

### **Top-Level Entity Classes**

| CIDOC-CRM Class | Wikidata QID | Wikidata Property | Notes |
|-----------------|--------------|-------------------|-------|
| **E1 CRM Entity** | Q35120 (entity) | - | Top-level class, implicit in all Wikidata items |
| **E2 Temporal Entity** | Q1190554 (occurrence) | - | Events, periods, states |
| **E4 Period** | Q11514315 (historical period) | P2348 (time period) | Historical periods, eras |
| **E5 Event** | Q1190554 (occurrence) | P31 (instance of) Q1656682 (event) | Specific occurrences |
| **E52 Time-Span** | - | P580 (start time), P582 (end time) | Temporal bounds, not standalone item |
| **E53 Place** | Q82794 (geographic region) | P276 (location) | Geographic entities |
| **E77 Persistent Item** | - | - | Abstract superclass (People, Things, Concepts) |

### **Actor Classes**

| CIDOC-CRM Class | Wikidata QID | Wikidata Property | Notes |
|-----------------|--------------|-------------------|-------|
| **E39 Actor** | Q24229398 (agent) | - | People, groups, institutions |
| **E21 Person** | Q5 (human) | P31 (instance of) Q5 | Individual people |
| **E74 Group** | Q16334295 (group of humans) | P31 (instance of) | Organizations, families |

### **Thing Classes (Physical)**

| CIDOC-CRM Class | Wikidata QID | Wikidata Property | Notes |
|-----------------|--------------|-------------------|-------|
| **E18 Physical Thing** | Q223557 (physical object) | - | Material objects |
| **E19 Physical Object** | Q488383 (object) | P31 (instance of) | Movable objects |
| **E22 Human-Made Object** | Q16887380 (artifact) | P31 (instance of) | Artifacts, tools |
| **E24 Physical Human-Made Thing** | - | - | Superclass for artifacts + features |
| **E25 Human-Made Feature** | Q811430 (construction) | P31 (instance of) | Buildings, roads, walls |
| **E26 Physical Feature** | Q33837 (landform) | P31 (instance of) | Natural features |
| **E27 Site** | Q839954 (archaeological site) | P31 (instance of) | Excavation sites |

### **Conceptual Object Classes**

| CIDOC-CRM Class | Wikidata QID | Wikidata Property | Notes |
|-----------------|--------------|-------------------|-------|
| **E28 Conceptual Object** | Q151885 (concept) | - | Abstract ideas, designs |
| **E55 Type** | Q28777 (type) | P279 (subclass of) | Classification types |
| **E73 Information Object** | Q11028 (information) | - | Documents, texts, data |
| **E31 Document** | Q49848 (document) | P31 (instance of) Q49848 | Written records |
| **E33 Linguistic Object** | Q17537576 (creative work) | P31 (instance of) | Texts, inscriptions |
| **E35 Title** | Q3409032 (title) | P1476 (title) | Names of works |
| **E36 Visual Item** | Q3305213 (painting) | P18 (image) | Images, depictions |
| **E41 Appellation** | Q82799 (name) | P2561 (name) | Names, identifiers |
| **E42 Identifier** | Q6545185 (identifier) | P1545 (series ordinal) | Catalog numbers, IDs |

### **Activity Classes (Events)**

| CIDOC-CRM Class | Wikidata QID | Wikidata Property | Notes |
|-----------------|--------------|-------------------|-------|
| **E7 Activity** | Q1914636 (activity) | P31 (instance of) | Intentional actions |
| **E8 Acquisition** | Q185363 (acquisition) | P580 (start time) + qualifier | Obtaining objects |
| **E9 Move** | Q79030 (motion) | P582 (end time) + P276 (location) | Transport events |
| **E10 Transfer of Custody** | Q2235114 (transfer) | P580 (start time) | Custody changes |
| **E11 Modification** | Q1150070 (modification) | P580 (start time) | Alterations |
| **E12 Production** | Q739302 (production) | P571 (inception) | Creation events |
| **E13 Attribute Assignment** | - | **P1480 (sourcing circumstances)** | **KEY for Chrystallum** - attribution of properties |
| **E65 Creation** | Q386724 (work) | P170 (creator) + P571 (inception) | Conceptual creation |

### **Life Cycle Events**

| CIDOC-CRM Class | Wikidata QID | Wikidata Property | Notes |
|-----------------|--------------|-------------------|-------|
| **E63 Beginning of Existence** | Q14623204 (beginning) | P571 (inception) | Birth, creation, formation |
| **E64 End of Existence** | Q12769393 (end) | P576 (dissolved/abolished) | Death, destruction |
| **E67 Birth** | Q3950 (birth) | P569 (date of birth) | Person birth |
| **E69 Death** | Q4 (death) | P570 (date of death) | Person death |
| **E6 Destruction** | Q18669875 (destruction) | P582 (end time) + P1120 (number of deaths) qualifier | Destruction of objects/buildings |

***

## **II. CIDOC-CRM PROPERTIES → Wikidata**

### **Identification & Typing**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P1 is identified by** | P1476 (title) OR P2561 (name) | Depends on type of appellation |
| **P48 has preferred identifier** | P528 (catalog code) | Preferred ID in a system |
| **P2 has type** | P31 (instance of) | Classification |
| **P137 exemplifies** | P31 (instance of) + P279 (subclass of) | Prototype relationship |

### **Temporal Properties**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P4 has time-span** | P580 (start time) + P582 (end time) | Date range |
| **P81 ongoing throughout** | P585 (point in time) | Specific date |
| **P82 at some time within** | P585 (point in time) + qualifier | Approximate dating |
| **P86 falls within** | - | Temporal containment (use qualifiers) |
| **P160 has temporal projection** | P580 (start time) + P582 (end time) | For spacetime volumes |

### **Spatial Properties**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P7 took place at** | P276 (location) | Event location |
| **P53 has former or current location** | P276 (location) + P580/P582 qualifiers | Object location with dates |
| **P54 has current permanent location** | P276 (location) | Current location |
| **P55 has current location** | P276 (location) | Temporary location |
| **P74 has current or former residence** | P551 (residence) | Person residence |
| **P87 is identified by** (place) | P625 (coordinate location) | Geographic coordinates |
| **P89 falls within** (spatial) | P131 (located in admin territory) | Administrative containment |

### **Participation & Agency**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P11 had participant** | P710 (participant) | General participation |
| **P14 carried out by** | P170 (creator) OR P1640 (curator) | Depends on activity type |
| **P22 transferred title to** | P1830 (owner of) + P580 qualifier | Acquisition recipient |
| **P23 transferred title from** | P1830 (owner of) + P582 qualifier | Previous owner |
| **P51 has former or current owner** | P127 (owned by) | Ownership |
| **P49 has former or current keeper** | P485 (archives at) | Custodianship |
| **P107 has current or former member** | P463 (member of) | Group membership |

### **Conceptual Relationships**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P62 depicts** | P180 (depicts) | Visual representation |
| **P65 shows visual item** | P18 (image) | Image of physical thing |
| **P67 refers to** | P921 (main subject) | Subject matter |
| **P70 documents** | P1343 (described by source) | Documentary reference |
| **P129 is about** | P921 (main subject) | Primary topic |
| **P138 represents** | P1299 (depicted by) | Symbolic representation |
| **P140 assigned attribute to** | **COMPOSITE** | Use P31 + sourcing circumstances (P1480) |
| **P141 assigned** | **COMPOSITE** | The actual attribute assigned |
| **P177 assigned property type** | - | **No direct equivalent** - needs custom solution |

### **Composition & Part-Whole**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P9 consists of** (Temporal) | - | Temporal decomposition (use qualifiers) |
| **P10 falls within** | - | Period containment |
| **P46 is composed of** (Physical) | P527 (has part) | Physical parts |
| **P56 bears feature** | P1299 (depicted by) OR custom | Features on objects |
| **P106 is composed of** (Conceptual) | P527 (has part) | Conceptual parts |
| **P148 has component** | P527 (has part) | Generic parts |

### **Production & Creation**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P92 brought into existence** | P571 (inception) | Generic creation |
| **P94 has created** | P170 (creator) + P571 (inception) | Conceptual creation |
| **P95 has formed** | P571 (inception) + P112 (founded by) | Group formation |
| **P96 by mother** | P25 (mother) | Birth relationship |
| **P97 from father** | P22 (father) | Birth relationship |
| **P108 has produced** | P170 (creator) | Production of physical thing |
| **P186 produced thing of product type** | P31 (instance of) + P170 (creator) | Type-based production |

### **Knowledge & Documentation (Critical for Chrystallum)**

| CIDOC-CRM Property | Wikidata Property | Notes |
|--------------------|-------------------|-------|
| **P15 was influenced by** | P737 (influenced by) | Influences on activity |
| **P16 used specific object** | P518 (applies to part) | Tool usage |
| **P17 was motivated by** | P828 (has cause) | Motivation for activity |
| **P32 used general technique** | P2079 (fabrication method) | Technique/method |
| **P33 used specific technique** | P2079 (fabrication method) | Specific technique |
| **P68 foresees use of** | P366 (has use) | Intended purpose |
| **P130 shows features of** | P1889 (different from) + qualifier | Similarity |

***

## **III. CRMinf (Argumentation Model) → Wikidata**

### **CRMinf Core Classes**

| CRMinf Class | Wikidata QID | Wikidata Property | Chrystallum Mapping |
|--------------|--------------|-------------------|---------------------|
| **I1 Argumentation** | - | **CUSTOM: Use Claim node** | Your `Claim` with `claim_type='inference'` |
| **I2 Belief** | - | **CUSTOM: Use Claim node** | Your `Claim` with confidence score |
| **I4 Proposition Set** | - | **CUSTOM: Use Claim cluster** | Multiple claims with same confidence |
| **I5 Inference Making** | Q1643989 (inference) | - | **Your Multi-Agent Debate Engine** |
| **I6 Belief Value** | - | **P1480 (sourcing circumstances)** | Confidence score (0.0-1.0) |
| **I7 Belief Adoption** | - | **CUSTOM** | Accepting a claim after validation |
| **I10 Provenance Statement** | - | P1343 (described by source) | Evidence provenance |

### **CRMinf Properties**

| CRMinf Property | Wikidata Property | Chrystallum Implementation |
|-----------------|-------------------|----------------------------|
| **J2 concluded that** | - | `Claim.generated_by` → `AnalysisRun` |
| **J4 that** | - | `Claim.label` (the proposition itself) |
| **J5 holds to be** | - | `Claim.confidence` (belief value) |

***

## **IV. CHRYSTALLUM-SPECIFIC MAPPINGS**

### **Key Architectural Decisions**

#### **1. E13 Attribute Assignment = Chrystallum's Epistemological Core**

```cypher
// CIDOC-CRM Approach:
(:Event {label: "Battle of Cannae"})-[:P7_TOOK_PLACE_AT]->(:Place {label: "Cannae"})

// Enhanced with E13:
(:E13_AttributeAssignment {
  performed_by: "Polybius",
  date: -150,
  confidence: 0.95
})
  -[:P140_ASSIGNED_ATTRIBUTE_TO]->(:Event {label: "Battle of Cannae"})
  -[:P141_ASSIGNED]->(:Place {label: "Cannae"})
  -[:P177_ASSIGNED_PROPERTY_TYPE]->(crm:P7_TOOK_PLACE_AT)

// Chrystallum Equivalent:
(:Claim {
  id_hash: "clm_cannae_location_polybius",
  label: "Battle of Cannae occurred at Cannae",
  confidence: 0.95,
  facet: "geographic|military",
  source: "Polybius, Histories III.107"
})
  -[:GENERATED_BY]->(:AnalysisRun {run_id: "2026-02-15"})
  -[:SUBJECT]->(:Event {qid: "Q13377", label: "Battle of Cannae"})
  -[:OBJECT]->(:Place {qid: "Q2415459", label: "Cannae"})
  -[:HAS_RELATIONSHIP_TYPE {type: "OCCURRED_AT"}]->()
```

**Recommendation:** Map all E13 Attribute Assignments to your `Claim` node structure with provenance tracking.

#### **2. CRMinf I5 Inference Making = Multi-Agent Debate**

```cypher
// CRMinf Structure:
(:I5_InferenceMaking {id: "inf_001"})
  -[:J1_USED_AS_PREMISE]->(:I2_Belief {proposition: "Polybius says X"})
  -[:J3_APPLIES]->(:I3_InferenceLogic {type: "source_criticism"})
  -[:J2_CONCLUDED_THAT]->(:I2_Belief {proposition: "X is 85% likely true"})

// Chrystallum Equivalent:
(:MultiAgentDebate {
  debate_id: "deb_20260215_001",
  claim_id: "clm_cannae_location_polybius"
})
  -[:INPUT_CLAIM]->(:Claim {id: "clm_001"})
  -[:AGENT_EVALUATION {agent: "source_critic", confidence: 0.85}]->()
  -[:AGENT_EVALUATION {agent: "quantitative_analyst", confidence: 0.90}]->()
  -[:CONSENSUS_CLAIM]->(:Claim {confidence: 0.87, status: "FACT"})
```

#### **3. PlaceVersion = E53 Place + Temporal Qualifiers**

```cypher
// CIDOC-CRM with temporal:
(:E53_Place {label: "Rome"})
  -[:P87_IS_IDENTIFIED_BY]->(:E47_SpatialCoordinate)
  -[:P1_IS_IDENTIFIED_BY]->(:E41_Appellation {value: "Roma"})

(:E4_Period {label: "Roman Republic", start: -509, end: -27})
  -[:P7_TOOK_PLACE_AT]->(:E53_Place {label: "Rome"})

// Chrystallum with PlaceVersion:
(:Place {id_hash: "plc_roma_q220", qid: "Q220", label: "Rome"})
  -[:HAS_VERSION]->(:PlaceVersion {
    id_hash: "plc_v_roma_republic",
    label: "Rome (Roman Republic capital)",
    valid_from: -509,
    valid_to: -27,
    administrative_status: "republic_capital",
    political_entity: "Q17167"
  })
```

***

## **V. IMPLEMENTATION RECOMMENDATIONS**

### **Priority 1: Essential Mappings for Roman Republic**

```python
# Add to CSV/EntityTypes/entity_types_registry_master.csv

entity_type_id,wikidata_qid,cidoc_crm_class,description
Human,Q5,E21,Individual people
Event,Q1656682,E5,Specific occurrences
Battle,Q178561,E7,Military confrontations
Place,Q82794,E53,Geographic locations
Period,Q11514315,E4,Historical periods
Organization,Q43229,E74,Groups and institutions
Artifact,Q16887380,E22,Human-made objects
Document,Q49848,E31,Written records
Claim,CUSTOM,I2,Beliefs about propositions
```

```python
# Add to CSV/Relationships/relationship_types_registry_master.csv

relationship_type,wikidata_property,cidoc_crm_property,facet_primary
OCCURRED_AT,P276,P7,geographic|military
CARRIED_OUT_BY,P710,P14,military|political
TOOK_PLACE_ON,P585,P4,temporal
DEPICTS,P180,P62,cultural|communication
CREATED_BY,P170,P94,cultural|intellectual
HAS_PARTICIPANT,P710,P11,social|political
DOCUMENTED_IN,P1343,P70,communication|intellectual
ASSIGNED_ATTRIBUTE,P1480,P140,intellectual|communication
```

### **Priority 2: Epistemological Mappings (Your Palantír Feature)**

```python
# Add to CSV/EpistemicRelationships/epistemic_registry.csv

epistemic_relationship,cidoc_crm_class,chrystallum_implementation
VALIDATES_CLAIM,I5_InferenceMaking,MultiAgentDebate.consensus_claim
CHALLENGES_CLAIM,I5_InferenceMaking,MultiAgentDebate.dissenting_opinion
PROVIDES_EVIDENCE_FOR,I10_ProvenanceStatement,Claim.evidence_chain
DERIVES_FROM_SOURCE,E13_AttributeAssignment,Claim.source_provenance
INFERRED_BY_REASONING,I5_InferenceMaking,Claim.inference_method
```

### **Priority 3: Wikidata Export Format**

```python
class WikidataExporter:
    """Export Chrystallum claims to Wikidata-compatible format"""
    
    def export_claim_as_statement(self, claim: Dict) -> Dict:
        """
        Convert Chrystallum Claim to Wikidata statement structure
        """
        return {
            'property': self._map_relationship_to_property(claim['relationship_type']),
            'value': claim['object_entity']['wikidata_qid'],
            'qualifiers': {
                'P580': claim.get('temporal_start'),  # start time
                'P582': claim.get('temporal_end'),    # end time
                'P1480': self._map_confidence_to_sourcing_circumstance(claim['confidence']),
                'P1343': claim['source_text'],  # described by source
                'P813': claim['analysis_date']  # retrieved
            },
            'references': [{
                'P248': 'Q115300957',  # stated in: Chrystallum
                'P854': claim['evidence_url'],
                'P1476': claim['source_text']
            }]
        }
    
    def _map_confidence_to_sourcing_circumstance(self, confidence: float) -> str:
        """Map Chrystallum confidence to Wikidata sourcing circumstances"""
        if confidence >= 0.95:
            return 'Q5727902'  # circa (high confidence)
        elif confidence >= 0.80:
            return 'Q18122778'  # presumably (medium-high)
        elif confidence >= 0.60:
            return 'Q18122761'  # possibly (medium)
        else:
            return 'Q18123970'  # allegedly (low)
```

***

## **VI. GAPS & CUSTOM SOLUTIONS NEEDED**

### **Where Wikidata Cannot Express CIDOC-CRM Concepts**

| CIDOC-CRM Feature | Wikidata Limitation | Chrystallum Solution |
|-------------------|---------------------|----------------------|
| **E13 Attribute Assignment** | No meta-property tracking | Use `Claim` node with provenance |
| **I5 Inference Making** | No inference chains | Multi-Agent Debate Engine |
| **I6 Belief Value** | Binary (stated/uncertain) only | Float confidence scores (0.0-1.0) |
| **P177 assigned property type** | Can't assign properties as values | Store as `claim.relationship_type` |
| **Temporal qualifiers on relationships** | Limited to P580/P582 | PlaceVersion with `valid_from`/`valid_to` |
| **Multi-faceted classification** | Single P31 value | Your 17-facet array |

***

## **VII. RECOMMENDED CSV STRUCTURE FOR YOUR REPO**

**File: `CSV/Ontology/cidoc_crm_wikidata_mapping.csv`**

```csv
cidoc_crm_id,cidoc_crm_label,cidoc_type,wikidata_qid,wikidata_property,mapping_type,chrystallum_node_type,notes
E1,CRM Entity,Class,Q35120,,DIRECT,Entity,Top-level class
E2,Temporal Entity,Class,Q1190554,,APPROXIMATE,Event,
E4,Period,Class,Q11514315,P2348,COMPOSITE,Period,Use with start/end dates
E5,Event,Class,Q1656682,P31,DIRECT,Event,
E7,Activity,Class,Q1914636,P31,DIRECT,Event,Intentional actions
E13,Attribute Assignment,Class,,P1480,CUSTOM,Claim,**Core epistemic tracking**
E21,Person,Class,Q5,P31,DIRECT,Human,
E22,Human-Made Object,Class,Q16887380,P31,DIRECT,Artifact,
E31,Document,Class,Q49848,P31,DIRECT,CreativeWork,
E39,Actor,Class,Q24229398,,APPROXIMATE,Human|Organization,
E53,Place,Class,Q82794,P276,DIRECT,Place|PlaceVersion,**Use PlaceVersion for temporal**
E55,Type,Class,Q28777,P279,DIRECT,SubjectConcept,
E74,Group,Class,Q16334295,P31,DIRECT,Organization,
I1,Argumentation,Class,,,CUSTOM,MultiAgentDebate,CRMinf extension
I2,Belief,Class,,,CUSTOM,Claim,CRMinf extension
I4,Proposition Set,Class,,,CUSTOM,ClaimCluster,CRMinf extension
I5,Inference Making,Class,Q1643989,,CUSTOM,MultiAgentDebate,**Your debate engine**
I6,Belief Value,Class,,P1480,CUSTOM,Confidence Score,Float 0.0-1.0
P1,is identified by,Property,,P1476|P2561,CONTEXT_DEPENDENT,,Depends on appellation type
P2,has type,Property,,P31,DIRECT,,Classification
P4,has time-span,Property,,P580+P582,COMPOSITE,,Date range
P7,took place at,Property,,P276,DIRECT,,Event location
P11,had participant,Property,,P710,DIRECT,,
P14,carried out by,Property,,P170|P1640,CONTEXT_DEPENDENT,,Depends on activity
P31,has modified,Property,,,COMPOSITE,,Use P31+sourcing circumstances
P67,refers to,Property,,P921,APPROXIMATE,,
P70,documents,Property,,P1343,DIRECT,,
P92,brought into existence,Property,,P571,DIRECT,,
P94,has created,Property,,P170+P571,COMPOSITE,,
P127,has broader term,Property,,P279,DIRECT,,Hierarchical
P129,is about,Property,,P921,DIRECT,,
P140,assigned attribute to,Property,,P1480,CUSTOM,,**Use Claim.subject**
P141,assigned,Property,,,CUSTOM,,**Use Claim.object**
P177,assigned property type,Property,,,CUSTOM,,**Use Claim.relationship_type**
J2,concluded that,Property,,,CUSTOM,,**MultiAgentDebate → Claim**
J4,that,Property,,,CUSTOM,,**Claim.label**
J5,holds to be,Property,,,CUSTOM,,**Claim.confidence**
```

***

## **BOTTOM LINE**

### **What You Can Do:**

1. **Import this mapping CSV** into your repository
2. **Add `cidoc_crm_class` field** to your entity/relationship registries
3. **Enable bidirectional translation**: Chrystallum ↔ CIDOC-CRM ↔ Wikidata
4. **Export claims to Wikidata** using composite property mappings
5. **Use E13 Attribute Assignment** as theoretical foundation for your `Claim` architecture

### **The Power:**

Your system becomes **trilingually literate**:
- **Wikidata** for federation and broad coverage
- **CIDOC-CRM** for epistemological rigor and museum interoperability
- **Chrystallum native** for 17-facet analysis, temporal bridges, and scholarly debate

This positions you as **the Rosetta Stone for digital humanities knowledge graphs**.

Would you like me to generate the actual Python code to implement these mappings in your ingestion pipeline?