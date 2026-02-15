# IMPLEMENTATION ROADMAP: Facet Discovery → Integrated Authority System

## Current State (As of Feb 15, 2026)

### ✅ COMPLETE (Layer 1-2, Part of Layer 4)
```
Your Existing Infrastructure:
├─ LCSH/LCC/FAST/Dewey authority systems ✅
├─ Wikidata federation infrastructure ✅
├─ SubjectConcept nodes (5 bootstrap) ✅
├─ Subject ontology framework ✅
├─ Dispatcher routing (backlink harvester) ✅
└─ Phase 2A+2B agent structure (ready) ✅

Files:
├─ Subjects/subject_concept_api.py
├─ SUBJECT_CONCEPT_IMPLEMENTATION.md
├─ SUBJECT_ONTOLOGY_ARCHITECTURE.md
├─ scripts/tools/wikidata_dispatcher.py (backlink harvester)
└─ Cypher/subject_concept_schema.cypher
```

### 🆕 JUST ADDED (Layer 3 Foundation)
```
Facet Discovery System:
├─ facet_qid_discovery.py (Wikipedia + Wikidata extraction) ✅
├─ discover_all_facets.py (batch discovery) ✅
├─ FACET_DISCOVERY_FROM_DISCIPLINE_QID.md (architecture) ✅
└─ FACET_DISCOVERY_INTEGRATION_GUIDE.md (tech roadmap) ✅

Files (NEW):
├─ scripts/reference/facet_qid_discovery.py ✅
├─ scripts/reference/discover_all_facets.py ✅
├─ FACET_DISCOVERY_*.md* ✅
└─ FACET_DISCOVERY_SUBJECT_CONCEPT_INTEGRATION.md ✅ (THIS SESSION)
```

### ⏳ NEEDED NEXT (Integration Layer - Layer 3 implementation)

```
Integration Components TO CREATE:

1. Facet Reference Neo4j Schema
   └─ FacetReference node type + indexes + constraints
   └─ File: Cypher/facet_reference_schema.cypher (NEW)

2. Facet Reference Loader
   └─ Load discovered facets to Neo4j
   └─ File: scripts/reference/facet_reference_loader.py (UPDATE existing)

3. Subject Concept Facet Integration
   └─ Link discovered facets to SubjectConcept
   └─ File: scripts/reference/subject_concept_facet_integration.py (NEW)

4. Authority Tier Evaluator
   └─ Calculate LCSH + Wikidata + Wikipedia tier
   └─ File: scripts/reference/authority_tier_evaluator.py (NEW)

5. Three-Layer Validator
   └─ Discipline + Authority + Civilization validation
   └─ File: scripts/reference/three_layer_validator.py (NEW)

6. Updated Neo4j Schema
   └─ Add facet relationships to SubjectConcept
   └─ File: Cypher/subject_concept_facet_relationships.cypher (NEW)
```

---

## Week-by-Week Implementation Plan

### WEEK 1: Verify & Deploy Facet Discovery (Feb 15-22)

#### Monday, Feb 15
- [x] Create `facet_qid_discovery.py` ✅
- [x] Create `discover_all_facets.py` ✅
- [x] Create documentation ✅

#### Tuesday-Wednesday, Feb 16-17
- [ ] **TASK**: Test facet discovery
  ```bash
  cd c:\Projects\Graph1\scripts\reference
  python discover_all_facets.py --facet Economic --no-load
  python discover_all_facets.py --output discovered_facets.json --no-load
  ```
- [ ] **TASK**: Inspect results in `discovered_facets.json`
  - Verify 5+ categories per facet
  - Check confidence scores (should be 0.65+)
  - Review keywords extracted

#### Thursday-Friday, Feb 18-19
- [ ] **TASK**: Create `Cypher/facet_reference_schema.cypher`
  ```cypher
  CREATE CONSTRAINT facet_reference_unique ON (f:FacetReference) ASSERT f.facet_qid IS UNIQUE;
  CREATE INDEX facet_reference_facet ON (f:FacetReference) FOR (f.facet);
  CREATE CONSTRAINT concept_category_unique ON (c:ConceptCategory) ASSERT c.id IS UNIQUE;
  CREATE INDEX concept_category_confidence ON (c:ConceptCategory) FOR (c.confidence);
  ```

- [ ] **TASK**: Test loading to Neo4j
  ```bash
  python discover_all_facets.py --output discovered_facets.json
  # Load results to Neo4j
  ```

**SUCCESS CRITERIA FOR WEEK 1**:
- ✓ All 17 facets discovered successfully
- ✓ Average confidence > 0.70
- ✓ 5+ categories per facet captured
- ✓ Loaded to Neo4j and queryable

---

### WEEK 1.5: Build Hierarchy Query Engine (Feb 19-22)

#### Friday, Feb 19
- [ ] **TASK**: Create `Cypher/wikidata_hierarchy_relationships.cypher`
  - Constraints for P31/P279/P361/P101/P2578/P921/P1269 relationships
  - Indexes for efficient traversal (especially transitive P279, P361)
  - Bootstrap example data (5 scholars, battles, disciplines)
  ```cypher
  CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:INSTANCE_OF]-() REQUIRE r.source IS NOT NULL;
  CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:SUBCLASS_OF]-() REQUIRE r.source IS NOT NULL;
  CREATE INDEX instance_of_outgoing IF NOT EXISTS FOR ()-[r:INSTANCE_OF]->();
  CREATE INDEX subclass_of_incoming IF NOT EXISTS FOR ()-[r:SUBCLASS_OF]->(n:SubjectConcept) ON (n.qid);
  ```

- [ ] **TASK**: Create `scripts/reference/hierarchy_query_engine.py`
  - Class: `HierarchyQueryEngine` with 4 main use cases:
    - **Semantic query expansion**: `find_instances_of_class()`, `find_superclasses()`, `find_components()`
    - **Expert discovery**: `find_experts_in_field()`, `find_disciplines_for_expert()`
    - **Source discovery**: `find_works_about_topic()`, `find_works_by_expert()`
    - **Contradiction detection**: `find_cross_hierarchy_contradictions()`
  - Utility methods: `find_all_facets_of_concept()`, `find_what_discipline_studies()`, `infer_facets_from_hierarchy()`
  - Batch operations for multiple lookups

#### Saturday, Feb 20
- [ ] **TASK**: Create `scripts/reference/academic_property_harvester.py`
  - SPARQL queries for P101/P2578/P921/P1269 harvesting
  - Methods: `harvest_p101_field_of_work()`, `harvest_p2578_studies()`, `harvest_p921_main_subject()`, `harvest_p1269_facet_of()`
  - Domain-specific mappings: DOMAIN_DISCIPLINE_MAPPINGS (Roman Republic, Mediterranean History)
  - Output to CSV + JSON + Cypher import scripts

- [ ] **TASK**: Create `scripts/reference/hierarchy_relationships_loader.py`
  - Class: `HierarchyRelationshipsLoader` to import CSV to Neo4j
  - Methods for each property type (P101-P921-P1269)
  - Batch loading with error handling
  - Verification queries

#### Sunday-Monday, Feb 21-22
- [ ] **TASK**: Test hierarchy query engine
  ```bash
  # Test with bootstrap data
  python -c "
  from neo4j import GraphDatabase
  from scripts.reference.hierarchy_query_engine import HierarchyQueryEngine
  
  with GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')) as driver:
      with driver.session() as session:
          engine = HierarchyQueryEngine(session)
          
          # Use Case 1: Find instances
          battles = engine.find_instances_of_class('Q178561')  # battle
          print(f'Found {len(battles)} battles')
          
          # Use Case 2: Find experts
          experts = engine.find_experts_in_field('Q188507')  # military history
          print(f'Found {len(experts)} military historians')
          
          # Use Case 3: Find works
          works = engine.find_works_about_topic('Q7163')  # politics
          print(f'Found {len(works)} works about politics')
  "
  ```

- [ ] **TASK**: Run academic property harvester for Roman Republic
  ```bash
  python scripts/reference/academic_property_harvester.py
  # Outputs: academic_properties_roman_republic.csv, .json, .cypher
  ```

- [ ] **TASK**: Load relationships
  ```bash
  python scripts/reference/hierarchy_relationships_loader.py
  # Loads CSV to Neo4j with error handling + verification
  ```

- [ ] **TASK**: Verify hierarchy queries work with real data
  ```python
  # Test expert discovery on loaded data
  engine = HierarchyQueryEngine(session)
  polybius_disciplines = engine.find_disciplines_for_expert("Q7345")
  # Should return [military history, ancient history, ...]
  ```

**SUCCESS CRITERIA FOR WEEK 1.5**:
- ✓ Hierarchy schema deployed to Neo4j
- ✓ All 7 relationship types have indexes
- ✓ Bootstrap example data loaded and queryable
- ✓ Hierarchy query engine working on all 4 use cases
- ✓ Academic properties harvested for Roman Republic (P101/P2578/P921/P1269)
- ✓ Relationships loaded and verified
- ✓ Expert discovery works (can find Polybius, Cicero, etc.)
- ✓ Source discovery works (can find Histories, De re publica)

---

### WEEK 2: Build Integration Layer (Feb 22-Mar 1)

#### Monday-Tuesday, Feb 23-24
- [ ] **TASK**: Create `scripts/reference/facet_reference_loader.py`
  ```python
  class FacetReferenceLoader:
      def __init__(self, uri, user, password):
          self.session = driver.session()
      
      def load_discovered_facet(self, facet: DiscoveredFacet):
          """Load FacetReference + ConceptCategories to Neo4j"""
          # Create FacetReference node
          # Create ConceptCategory nodes
          # Create :CONTAINS relationships
      
      def get_facet_profile(self, wikidata_qid: str):
          """Query facet discovery results by QID"""
          # Returns facet score histogram for routing
  ```

- [ ] **TASK**: Create `subjects/reference/authority_tier_evaluator.py`
  ```python
  class AuthorityTierEvaluator:
      def evaluate_tier(self, has_lcsh, has_wikidata, has_wikipedia):
          """Tier 1-3 classification"""
          # Returns tier + confidence
      
      def map_lcsh_to_facets(self, lcsh_id):
          """Map LCSH ID to primary facets"""
          # Library science → discipline facets
  ```

#### Wednesday-Thursday, Feb 25-26
- [ ] **TASK**: Create `scripts/reference/subject_concept_facet_integration.py`
  ```python
  class SubjectConceptFacetIntegration:
      def assign_facets_to_concept(self, concept_id, facet_profile):
          """Update SubjectConcept with facet assignments"""
          # Map discovery output to concept
      
      def validate_facet_for_concept(self, concept_qid, proposed_facet):
          """Check facet relevance"""
          # Returns relevance score + validation
  ```

- [ ] **TASK**: Create `Cypher/subject_concept_facet_relationships.cypher`
  ```cypher
  -- Link SubjectConcept to FacetReference
  CREATE CONSTRAINT subject_concept_facet_discovery 
    ON (s:SubjectConcept, f:FacetReference) 
    ASSERT s.facet_discovery_qid = f.facet_qid;
  
  -- Add facet discovery metadata
  ALTER CONSTRAINT ... ADD PROPERTY facet_confidence;
  ```

#### Friday, Feb 27
- [ ] **TASK**: Test integration with 5 bootstrap concepts
  ```python
  from subject_concept_facet_integration import SubjectConceptFacetIntegration
  
  integration = SubjectConceptFacetIntegration()
  
  # For each bootstrap concept
  for concept_id in ["subj_roman_republic_q17167", ...]:
      facet_profile = facet_loader.get_facet_profile("Q17167")
      integration.assign_facets_to_concept(concept_id, facet_profile)
  ```

**SUCCESS CRITERIA FOR WEEK 2**:
- ✓ All 5 bootstrap concepts have facet assignments
- ✓ Facet profiles loaded from discovery correctly
- ✓ Authority tier calculated for each concept
- ✓ Can query: "What facets are most relevant to concept X?"

---

### WEEK 3: Build Validation Layer (Mar 1-8)

#### Monday-Tuesday, Mar 2-3
- [ ] **TASK**: Create `scripts/reference/three_layer_validator.py`
  ```python
  class ThreeLayerValidator:
      def validate_layer_1_discipline(self, facet, wikidata_qid, claim_text):
          """Check Wikipedia discipline knowledge"""
          facet_profile = facet_loader.get_facet_profile(wikidata_qid)
          keyword_matches = match_keywords(facet_profile[facet]["topics"], claim_text)
          return {
              "valid": True,
              "facet_confidence": facet_profile[facet]["confidence"],
              "keyword_match_score": len(keyword_matches) / len(topics),
              "layer_score": ...
          }
      
      def validate_layer_2_authority(self, concept_id, facet):
          """Check LCSH/Wikidata/Wikipedia authority"""
          concept = get_concept(concept_id)
          tier = evaluate_tier(
              has_lcsh=bool(concept.lcsh_id),
              has_wikidata=bool(concept.wikidata_qid),
              has_wikipedia=...
          )
          return {
              "authority_tier": tier,
              "facet_supported": facet in supported_facets_for_tier(tier),
              "layer_score": tier * 0.33 + 0.66
          }
      
      def validate_layer_3_civilization(self, concept_id, facet, claim_text, trained_ontology):
          """Check training data patterns"""
          facet_patterns = trained_ontology.get_facet_patterns(facet)
          keyword_overlap = match_keywords(facet_patterns["keywords"], claim_text)
          return {
              "training_coverage": len(facet_patterns["examples"]) / 50,
              "keyword_overlap": len(keyword_overlap) / len(facet_patterns["keywords"]),
              "layer_score": ...
          }
      
      def validate_all_three(self, concept_id, facet, claim_text, trained_ontology):
          """Combine layers"""
          l1 = self.validate_layer_1_discipline(...)
          l2 = self.validate_layer_2_authority(...)
          l3 = self.validate_layer_3_civilization(...)
          
          if l1["valid"] and l2["facet_supported"] and l3["layer_score"] > 0.3:
              confidence = (l1["score"] + l2["score"] + l3["score"]) / 3
              return {"valid": True, "confidence": confidence}
          return {"valid": False, "confidence": 0}
  ```

#### Wednesday-Thursday, Mar 4-5
- [ ] **TASK**: Integration testing
  ```python
  # Test finding validation
  finding = "Evidence of taxation systems and state revenue collection"
  result = validator.validate_all_three(
      concept_id="subj_roman_republic_q17167",
      facet="Economic",
      claim_text=finding,
      trained_ontology=roman_trained_ontology
  )
  # Should return confidence ~0.85+
  ```

#### Friday, Mar 6
- [ ] **TASK**: Update phase_2b_agent.py to use three-layer validation
  ```python
  # In Phase 2B GPT handling:
  for proposed_concept in discovered_concepts:
      validation = validator.validate_all_three(
          proposal.subject_concept_id,
          proposal.facet,
          proposal.finding_text,
          trained_ontology
      )
      
      if validation["valid"]:
          if validation["confidence"] >= 0.90:
              proposal.status = "AUTO_APPROVED"
          else:
              proposal.status = "APPROVED_PENDING_REVIEW"
      else:
          proposal.status = "REJECTED"
  ```

**SUCCESS CRITERIA FOR WEEK 3**:
- ✓ Three-layer validation working on test findings
- ✓ Can distinguish high-confidence from low-confidence proposals
- ✓ All three layers contributing to final score
- ✓ Integration with Phase 2B ready

---

### WEEK 4: End-to-End Testing (Mar 8-15)

#### Monday-Tuesday, Mar 9-10
- [ ] **TASK**: Update Phase 2A+2B GPT prompts
  ```
  # Inject at agent initialization:
  facet_profile = integration.get_facet_profile(subject_concept_id)
  
  prompt += f"""
  ## FACET ROUTING
  
  This subject has these facet strengths:
  {facet_profile toString()}
  
  ## VALIDATION REQUIREMENT
  
  All discovered entities must pass:
  1. Discipline validation (against Wikipedia facet knowledge)
  2. Authority validation (against LCSH/Wikidata)
  3. Civilization validation (against training data)
  
  DO NOT propose concepts that fail any layer.
  """
  ```

#### Wednesday-Thursday, Mar 11-12
- [ ] **TASK**: Run Phase 2B with full integration
  ```bash
  python scripts/phase_2b/entity_discovery.py \
    --subject-concept "subj_roman_republic_q17167" \
    --with-three-layer-validation \
    --with-facet-routing \
    --output discoveries_validated.json
  ```

- [ ] **TASK**: Analyze results
  - How many proposals passed all three layers?
  - Average confidence of approved proposals
  - Any hallucinations detected?
  - Facet distribution in approved concepts

#### Friday, Mar 13
- [ ] **TASK**: Documentation + validation report
  - Document integration results
  - Update README with three-layer architecture
  - Create example queries and patterns

**SUCCESS CRITERIA FOR WEEK 4**:
- ✓ Phase 2B running with full three-layer validation
- ✓ All discovered concepts have facet assignments
- ✓ Zero hallucinations (all proposals grounded in 3 layers)
- ✓ Archive scores documented (confidence distribution)

---

## Files to Create (Summary)

| File | Status | Week | Purpose |
|------|--------|------|---------|
| `Cypher/wikidata_hierarchy_relationships.cypher` | 🆕 | 1.5 | P31/P279/P361/P101/P2578/P921/P1269 schema |
| `scripts/reference/hierarchy_query_engine.py` | 🆕 | 1.5 | Query patterns (expertise, sources, contradictions) |
| `scripts/reference/academic_property_harvester.py` | 🆕 | 1.5 | SPARQL harvester for academic properties |
| `scripts/reference/hierarchy_relationships_loader.py` | 🆕 | 1.5 | Load harvested relationships to Neo4j |
| `Cypher/facet_reference_schema.cypher` | 🆕 | 2 | FacetReference node type |
| `scripts/reference/facet_reference_loader.py` | 🆕 | 2 | Load discovered facets |
| `scripts/reference/authority_tier_evaluator.py` | 🆕 | 2 | Calculate tier/confidence |
| `scripts/reference/subject_concept_facet_integration.py` | 🆕 | 2 | Link discovery to concepts |
| `scripts/reference/three_layer_validator.py` | 🆕 | 3 | Validation pipeline |
| `Cypher/subject_concept_facet_relationships.cypher` | 🆕 | 2 | Neo4j relationships |
| Update: `scripts/phase_2b/entity_discovery.py` | 🔄 | 3 | Inject validation |
| Update: `Prompts/*.md` | 🔄 | 3 | Add facet routing instructions |
| Update: `AI_CONTEXT.md` | 🔄 | 4 | Track integration progress |

---

## Success Criteria: Final Integration

By end of Week 4, the system will have:

### ✅ Facet Discovery
- [x] Automatic extraction from Wikipedia discipline articles
- [x] Confidence scores per category
- [x] All 17+ facets discoverable

### ✅ Hierarchy Query Engine
- [x] P31/P279/P361 transitive traversal (instance/class/whole)
- [x] Semantic query expansion (find all battles in Punic Wars)
- [x] Expert discovery (who specializes in military history)
- [x] Source discovery (what works on Roman politics)
- [x] Contradiction detection (cross-hierarchy inconsistencies)
- [x] Facet inference from hierarchy (entity → superclasses → facets)

### ✅ Authority Integration
- [x] LCSH/LCC/FAST/Dewey authority gates
- [x] Tier 1-3 classification
- [x] Sparse pointer relationships (no data duplication)
- [x] Academic properties (P101/P2578/P921/P1269) linked to concepts

### ✅ Subject Concept Enhanced
- [x] Facet assignments from discovery
- [x] Authority tier metadata
- [x] Hierarchy relationships (can traverse to experts/sources)
- [x] Three-layer validation enabled

### ✅ Phase 2B Enhanced
- [x] Facet-aware routing (use P2578 to route to discipline-specific agents)
- [x] Three-layer validation before claiming
- [x] Expert sourcing (find quoted experts via P101)
- [x] No hallucinations (impossible without 3-layer pass)

### ✅ Query Capability
```cypher
# "Show me Roman concepts with strong economic facets"
MATCH (s:SubjectConcept {wikidata_qid: "Q17167"})
  -[:HAS_FACET_ASSIGNMENT]->(f:FacetAssignment {facet: "Economic"})
  WHERE f.confidence > 0.75
RETURN s.label, f.facet, f.confidence, f.related_facets

# "Find experts in Roman military history and their works"
MATCH (expert:Person)-[:FIELD_OF_WORK]->(mil_hist:SubjectConcept {label: "military history"})
      -[:STUDIES]->(warfare:SubjectConcept)
OPTIONAL MATCH (expert)-[:AUTHOR_OF]->(work:Work)-[:MAIN_SUBJECT]->(topic)
WHERE topic IN [warfare]
RETURN expert.label, collect(DISTINCT work.label) as works

# "What contradicts this finding?"
MATCH (specific_claim:Claim)-[:SUBJECT]->(specific_entity {qid: "Q13377"})
      -[:INSTANCE_OF|PART_OF*1..3]->(general_entity)
      <-[:SUBJECT]-(general_claim:Claim)
WHERE specific_claim.label CONTAINS "victory" AND general_claim.label CONTAINS "defeat"
  AND general_claim.confidence > specific_claim.confidence
RETURN specific_claim, general_claim, "contradiction" as relationship_type
```

---

## Quick Reference: What Gets Built

```
Layer 1 (LIBRARY AUTHORITY): Already exists
  LCSH → LCC → FAST → Dewey

Layer 2 (FEDERATION): Already exists
  Wikidata + Wikipedia

Layer 2.5 (HIERARCHY QUERIES): Getting built Week 1.5 ⭐ NEW
  P31/P279/P361 (instance/class/whole) traversal
  P101 (experts in field)
  P2578 (what disciplines study)
  P921 (works about topic)
  P1269 (facets/aspects)
  → Query engine: semantic expansion, expert discovery, source discovery, contradiction detection

Layer 3 (FACET DISCOVERY): Getting main components Week 1
  Wikipedia extraction → FacetReference → Neo4j

Layer 4 (SUBJECT INTEGRATION): Getting built Week 2
  SubjectConcept ← FacetAssignment ← FacetReference
  + Hierarchy routing (use best facet from P2578 studies)

Layer 5 (VALIDATION): Getting built Week 3-4
  ThreeLayerValidator → AutoApproved/FlaggedForReview/Rejected

Result: Maximum grounding, minimum hallucination, automatic routing
```

---

## Immediate Next Step

**THIS WEEK (Feb 15-19) - WEEK 1**:
```bash
# Verify facet discovery works
python c:\Projects\Graph1\scripts\reference\discover_all_facets.py --no-load

# When ready to load:
python c:\Projects\Graph1\scripts\reference\discover_all_facets.py
# (Will load to Neo4j once loader implemented)
```

**NEXT WEEKEND (Feb 19-22) - WEEK 1.5** ⭐ NEW:
```bash
# Deploy hierarchy schema
cypher-shell -u neo4j -p password < c:\Projects\Graph1\Cypher\wikidata_hierarchy_relationships.cypher

# Harvest academic properties for Roman Republic
python c:\Projects\Graph1\scripts\reference\academic_property_harvester.py
# Output: academic_properties_roman_republic.csv, .json, .cypher

# Load relationships to Neo4j
python c:\Projects\Graph1\scripts\reference\hierarchy_relationships_loader.py

# Test query engine
python -c "
from neo4j import GraphDatabase
from scripts.reference.hierarchy_query_engine import HierarchyQueryEngine

with GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')) as driver:
    with driver.session() as session:
        engine = HierarchyQueryEngine(session)
        battles = engine.find_instances_of_class('Q178561')
        print(f'Found {len(battles)} battles')
"
```

**THEN (Week 2 onward)**:
Build integration files in sequence above.
