# Appendix V: ADR 002 Function Driven Relationships

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

