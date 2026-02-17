# COMPLETE ARCHITECTURE: Facet Discovery + Authority Stack + Subject Ontology

## The Full Hierarchy (Visual)

```
████████████████████████████████████████████████████████████████████
█                                                                  █
█                    KNOWLEDGE GRAPH AUTHORITY                    █
█               5.5-LAYER INTEGRATED SYSTEM (COMPLETE)            █
█                                                                  █
████████████████████████████████████████████████████████████████████

LAYER 1: LIBRARY SCIENCE AUTHORITY (Canonical Gate)
┌────────────────────────────────────────────────────────────────┐
│  LCSH (Library of Congress Subject Headings)                     │
│  ├─ GATE FUNCTION: "Is this a valid subject?"                   │
│  ├─ EXAMPLE: sh85115055 = "Rome--History"                       │
│  └─ STORE: Sparse pointer relationship [:ALIGNED_WITH_LCSH]     │
│                                                                  │
│  LCC (Library of Congress Classification)                        │
│  ├─ GATE FUNCTION: "Where would this be shelved?"               │
│  ├─ EXAMPLE: DG235-254 = "Roman Republic (510-27 BC)"           │
│  └─ STORE: Sparse pointer relationship [:ALIGNED_WITH_LCC]      │
│                                                                  │
│  FAST (Faceted Application of Subject Terminology)               │
│  ├─ GATE FUNCTION: "What standardized facets apply?"            │
│  ├─ EXAMPLE: 1352255 = "Rome--History--Republic"                │
│  └─ STORE: Sparse pointer relationship [:ALIGNED_WITH_FAST]     │
│                                                                  │
│  Dewey Decimal                                                   │
│  ├─ GATE FUNCTION: "Broader subject classification"             │
│  ├─ EXAMPLE: 937.05 = "Roman history"                           │
│  └─ STORE: Sparse pointer (optional)                            │
└────────────────────────────────────────────────────────────────┘
         TIER 1: Concepts must have valid LCSH ID
         CONFIDENCE: These have survived library vetting

LAYER 2: FEDERATION AUTHORITY (Linked Data Gate)
┌────────────────────────────────────────────────────────────────┐
│  Wikidata (Machine-readable identifiers)                         │
│  ├─ GATE FUNCTION: "Is this linked to knowledge graph?"         │
│  ├─ EXAMPLE: Q17167 = Roman Republic                            │
│  ├─ PROVIDES: Properties (P279, P361), classes, relationships   │
│  └─ STORE: Full wikidata_qid in SubjectConcept node             │
│                                                                  │
│  Wikipedia (Human-readable knowledge)                            │
│  ├─ GATE FUNCTION: "Is this documented by community?"           │
│  ├─ EXAMPLE: en.wikipedia.org/wiki/Roman_Republic               │
│  ├─ PROVIDES: Article structure, sections, relationships        │
│  └─ STORE: Referenced in source + Wikipedia sections            │
│                                                                  │
│  External Identifiers (VIAF, DBpedia, GeoNames)                  │
│  ├─ GATE FUNCTION: "Cross-link validation"                      │
│  └─ STORE: federation_id dispatcher routing                     │
└────────────────────────────────────────────────────────────────┘
         TIER 2: Concepts should have Wikidata QID
         CONFIDENCE: Community-vetted on multiple platforms

LAYER 2.5: HIERARCHY QUERY ENGINE (Semantic Integration) ← NEW
┌────────────────────────────────────────────────────────────────┐
│ Wikidata Semantic Properties & Transitive Inference            │
│                                                                 │
│ P31 (Instance-Of) - "IS A"                                    │
│ ├─ Pattern: Individual → Type/Class                            │
│ ├─ Example: Battle of Cannae (Q13377) → battle (Q178561)      │
│ ├─ Used by: Entity classification, semantic queries           │
│ └─ Non-transitive: Cannae ≠ instance of Conflict              │
│                                                                 │
│ P279 (Subclass-Of) - "IS A TYPE OF" [TRANSITIVE]             │
│ ├─ Pattern: Class → Broader Class                              │
│ ├─ Example: battle (Q178561) → conflict (Q180684)             │
│ ├─ Transitive: battle → conflict → event (implicit)           │
│ ├─ Used by: Query expansion, contradiction detection          │
│ └─ Enables: "Find all battles" expands to "all conflicts"    │
│                                                                 │
│ P361 (Part-Of) - "CONTAINED IN" [TRANSITIVE]                 │
│ ├─ Pattern: Component → Whole (mereological)                   │
│ ├─ Example: Cannae → Punic Wars → Punic Wars (implicit)       │
│ ├─ Transitive: Cannae part-of Wars part-of Ancient Med        │
│ ├─ Used by: Hierarchical entity nesting                        │
│ └─ Enables: Find all events contained in a period             │
│                                                                 │
│ P101 (Field-Of-Work) - "Specializes In"                       │
│ ├─ Pattern: Person/Org → Discipline (domain mapping)           │
│ ├─ Example: Polybius (Q7345) → military history (Q188507)     │
│ ├─ Used by: Expert discovery, claim sourcing                  │
│ └─ Enables: "Find military historians" → Route to experts     │
│                                                                 │
│ P2578 (Studies) - "Discipline Studies"                         │
│ ├─ Pattern: Discipline → Object of Study (domain definition)  │
│ ├─ Example: military history → warfare, strategy              │
│ ├─ Used by: Discipline grounding, facet validation            │
│ └─ Enables: "Military history studies warfare"                │
│                                                                 │
│ P921 (Main-Subject) - "Work Is About"                          │
│ ├─ Pattern: Work → Topic (primary topic mapping)               │
│ ├─ Example: Histories (Polybius) → Second Punic War           │
│ ├─ Used by: Source discovery, evidence grounding              │
│ └─ Enables: "Find works on Roman politics"                    │
│                                                                 │
│ P1269 (Facet-Of) - "Is Aspect Of"                             │
│ ├─ Pattern: Aspect → Broader Concept (facet hierarchy)        │
│ ├─ Example: microeconomics → economics → social science       │
│ ├─ Used by: Facet relationships, inheritance                  │
│ └─ Enables: "Show aspects of economics"                       │
│                                                                 │
│ Neo4j Indexes (for Performance):                               │
│ ├─ Transitive P279 chains: <200ms per query                  │
│ ├─ Transitive P361 chains: <200ms per query                  │
│ ├─ Expert lookup (P101): <100ms batch query                  │
│ ├─ Source lookup (P921): <150ms batch query                  │
│ └─ Contradiction detection: <300ms cross-check                │
│                                                                 │
│ Query Engine Methods:                                          │
│ ├─ find_instances_of_class() - Semantic expansion             │
│ ├─ find_superclasses() - Entity classification                │
│ ├─ find_components() - Mereological hierarchy                 │
│ ├─ find_experts_in_field() - Expert discovery                 │
│ ├─ find_works_about_topic() - Source discovery                │
│ ├─ find_cross_hierarchy_contradictions() - Validation         │
│ └─ infer_facets_from_hierarchy() - Auto-facet assignment      │
└────────────────────────────────────────────────────────────────┘
         TIER 2.5: Semantic query infrastructure
         CONFIDENCE: From Wikidata properties (0.95+)

LAYER 3: DISCIPLINE-SPECIFIC KNOWLEDGE (Facet Authority) ← NEW
┌────────────────────────────────────────────────────────────────┐
│  Automated Facet Discovery from Wikipedia               │
│  ├─ GATE FUNCTION: "What discipline categories apply?"          │
│  ├─ SOURCE: Wikipedia discipline article (e.g., Q8134=Economics)│
│  ├─ EXTRACTION: Major sections → concept categories             │
│  ├─ EXAMPLE:                                                     │
│  │  ├─ Wikipedia section: "Supply and Demand"                   │
│  │  ├─ Extracted keywords: [supply, demand, price, equilibrium] │
│  │  ├─ Confidence: 0.85 (based on content length)              │
│  │  └─ Source: Wikipedia discipline article systematic analysis │
│  ├─ PROVIDES: Facet confidence scores, keyword matching         │
│  └─ STORE: FacetReference in Neo4j queryable by agent          │
│                                                                  │
│  Wikidata Properties (P279, P361)                                │
│  ├─ GATE FUNCTION: "What types/branches exist?"                 │
│  ├─ EXAMPLE: Q8134 subclass_of → Econometrics, Finance         │
│  ├─ PROVIDES: Type hierarchy, broader contexts                  │
│  └─ STORE: Parsed from Wikidata properties                      │
└────────────────────────────────────────────────────────────────┘
         TIER 3: Concepts should have discipline QID
         CONFIDENCE: Automatically extracted from authoritative sources

LAYER 4: SUBJECT CONCEPT HIERARCHY (Instance Authority)
┌────────────────────────────────────────────────────────────────┐
│  SubjectConcept Nodes (Your Knowledge Graph)                     │
│  ├─ GATE FUNCTION: "Is this a valid concept in our graph?"      │
│  ├─ STORES: All authority links (LCSH, LCC, FAST, Wikidata)    │
│  ├─ STORES: Facet assignments (from discovery)                  │
│  ├─ STORES: Authority tier (Tier 1-3 + confidence)             │
│  ├─ STORES: Hierarchy (parent-child relationships)              │
│  ├─ EXAMPLE:                                                     │
│  │  concept_id: "subj_roman_republic_q17167"                   │
│  │  label: "Roman Republic"                                     │
│  │  lcsh_id: "sh85115055"                                       │
│  │  wikidata_qid: "Q17167"                                      │
│  │  authority_tier: 1 (LCSH+Wikidata+Wikipedia)                │
│  │  facet: "Political"                                          │
│  │  facet_discovery: {source: "Q17167", confidence: 0.92}      │
│  │  related_facets: ["Military", "Economic", "Geographic"]     │
│  └─ STORE: Relationships to authority tier nodes                │
└────────────────────────────────────────────────────────────────┘
         TIER 4: Instances of the above tiers
         CONFIDENCE: Composite of all upstream layers

LAYER 5: AGENT-DISCOVERED CONCEPTS (Inference Authority)
┌────────────────────────────────────────────────────────────────┐
│  Phase 2B Creates NEW SubjectConcepts                            │
│  ├─ GATE FUNCTION: "Does this pass validation?"                 │
│  ├─ VALIDATION CHECKS:                                          │
│  │  └─ Confidence ≥ 0.75 required                              │
│  │  └─ Maps to valid facet(s)                                  │
│  │  └─ Linked to parent concept                                │
│  │  └─ Temporal bounds within civilizational scope             │
│  ├─ CONFIDENCE TIER: Depends on evidence quality                │
│  ├─ FACET ASSIGNMENT: From discovery engine                     │
│  └─ STORE: As SubjectConcept node with agent_created=true       │
│                                                                  │
│  Example: "Battle of Cannae"                                     │
│  ├─ Parent: Punic Wars (subj_punic_wars_q3105)                │
│  ├─ Facet: Military (primary)                                   │
│  ├─ Related facets: Political, Tactical, Geographic            │
│  ├─ Confidence: 0.96 (multiple sources agree)                  │
│  ├─ Evidence: Livy, Polybius, Wikipedia                        │
│  └─ Authority tier: 2 (no LCSH, but Wikidata Q181098)         │
└────────────────────────────────────────────────────────────────┘
         TIER 5: User/Agent-created concepts
         CONFIDENCE: Based on validation passing
```

---

## The Integration Pipeline

### From LCSH → Facet Assignment → Agent Routing

```
START: User has LCSH ID (sh85115055 = "Rome--History")

    ↓ Step 1: Lookup Authority Tier

    Query: Is this in LCSH? YES
    Query: Has Wikidata QID? YES → Q17167
    Query: Has Wikipedia? YES
    
    Result: TIER 1 (98% confidence)

    ↓ Step 2: Map to Wikidata QID

    sh85115055 → Q17167 (Roman Republic)
    (via LCSH-Wikidata mapping table)

    ↓ Step 3: Discover Facets

    Get Facet Discovery Results for Q17167:
    ├─ Political (0.92 confidence)
    ├─ Military (0.88 confidence)
    ├─ Economic (0.76 confidence)
    ├─ Geographic (0.72 confidence)
    └─ Religious (0.68 confidence)

    ↓ Step 4: Create SubjectConcept

    (:SubjectConcept {
        concept_id: "subj_roman_republic_q17167",
        label: "Roman Republic",
        lcsh_id: "sh85115055",
        lcc_codes: ["DG235-254"],
        wikidata_qid: "Q17167",
        authority_tier: 1,
        authority_confidence: 0.98,
        facet: "Political",
        facet_confidence: 0.92,
        facet_discovery_method: "Wikipedia discipline article",
        related_facets: ["Military", "Economic", "Geographic"],
        related_facet_confidence: [0.88, 0.76, 0.72]
    })

    ↓ Step 5: Setup Agent Routing

    phase_2b_agent = PhaseAgent(
        subject_concept_id="subj_roman_republic_q17167",
        authority_tier=1,
        primary_facets=["Political", "Military"],
        secondary_facets=["Economic", "Geographic"],
        facet_confidence_threshold=0.70
    )

    ↓ Step 6: Phase 2B Process Finding

    Finding: "Senate holds legislative authority"
    
    Agent analyzes:
    ├─ Facet match: Political (score 0.95)
    ├─ Authority tier check: Political facet confidence 0.92 (pass)
    ├─ Discipline validation: Political theory covers governance (pass)
    ├─ Civilization validation: Roman training data supports (pass)
    └─ Three-layer validation: ALL PASS
    
    Creates Claim:
    ├─ text: "Senate holds legislative authority"
    ├─ subject_concept: "subj_roman_republic_q17167"
    ├─ facet: "Political"
    ├─ confidence: 0.96
    ├─ evidence: "Wikipedia + training data"
    └─ validation: "THREE_LAYER_PASS"

END: Claim stored with full validation trail
```

### Hierarchy Query Usage (Layer 2.5)

**Example 1: Semantic Query Expansion**
```
User Query: "Find all battles in the Second Punic War"

→ Query Engine: find_components("Q185736")  # Second Punic War
→ P361 traversal: Battle → Part-Of Punic Wars
→ Result: [Cannae, Trebia, Zama, ...] with confidence scores

Neo4j Pattern:
MATCH (component)-[:PART_OF*1..3]->(whole {qid: "Q185736"})
WHERE component.node_type = "Event"
RETURN component
```

**Example 2: Expert Discovery**
```
User Query: "Who can interpret claims about military history?"

→ Query Engine: find_experts_in_field("Q188507")  # Military History
→ P101 inversion: Person → Field-Of-Work → Military History
→ Result: [Polybius (0.95), Livy (0.95), Caesar (0.90)]

Neo4j Pattern:
MATCH (expert)-[:FIELD_OF_WORK]->(discipline {qid: "Q188507"})
RETURN expert, expert.confidence
ORDER BY confidence DESC
```

**Example 3: Source Discovery**
```
User Query: "What primary works discuss Roman politics?"

→ Query Engine: find_works_about_topic("Q7163")  # Politics
→ P921 inversion: Work → Main-Subject → Politics
→ Result: [De re publica, Politics (Aristotle), ...]

Neo4j Pattern:
MATCH (work)-[:MAIN_SUBJECT]->(topic {qid: "Q7163"})
RETURN work
ORDER BY work.publication_date DESC
```

**Example 4: Contradiction Detection**
```
Finding: "Battle of Cannae was a Roman victory"
vs.
General claim: "Rome suffered defeats in Second Punic War"

→ Query Engine: find_cross_hierarchy_contradictions("Q13377")
→ Traversal: Cannae → Instance-Of → Battle → Part-Of → Punic Wars
→ Comparison: specific claim confidence vs. general claim confidence
→ Decision: Flag for multi-agent debate if confidence mismatch

Neo4j Pattern:
MATCH (specific:Claim)-[:SUBJECT]->(entity {qid: "Q13377"})
MATCH (entity)-[:INSTANCE_OF|PART_OF*1..3]->(general_entity)
MATCH (general:Claim)-[:SUBJECT]->(general_entity)
WHERE specific.confidence < general.confidence
  AND specific.label CONTAINS "victory"
  AND general.label CONTAINS "defeat"
RETURN {specific, general, contradiction: true}
```

---

## The Dispatcher Architecture (How Data Flows)

Your Wikidata backlink infrastructure already has this:

```
DISPATCHER ROUTING (Statement Datatype Analysis)
├─ edge_candidate (54.7%)
│  └─ Wikibase-item datatype
│  └─ Handler: relationship_handler
│  └─ Creates edges between concepts
│  └─ Facet discovery validates: "Is this relationship within expected facet scope?"
│
├─ federation_id (28.9%)
│  └─ External identifier datatype
│  └─ Handler: identifier_handler
│  └─ Links to LCSH, Wikidata, DBpedia, etc.
│  └─ Facet discovery validates: "Are federated concepts in same discipline?"
│
├─ node_property (5.0%)
│  └─ String, label datatypes
│  └─ Handler: attribute_handler
│  └─ Updates node labels and text
│  └─ Facet discovery validates: "Does this text match facet keywords?"
│
├─ measured_attribute (2.9%)
│  └─ Quantity datatype (with units)
│  └─ Handler: quantity_handler
│  └─ Numbers, measurements
│  └─ Facet discovery validates: "Are units appropriate for facet?"
│
├─ temporal_anchor (2.6%)
│  └─ Date/time datatype
│  └─ Handler: temporal_handler
│  └─ Routes to temporal validators
│  └─ Facet discovery validates: "Do dates match temporal scope?"
│
├─ geo_attribute (2.3%)
│  └─ Coordinate datatype
│  └─ Handler: geo_handler
│  └─ Geographic information
│  └─ Facet discovery validates: "Is geography relevant to this facet?"
│
├─ media_reference (3.2%)
│  └─ Commons file datatype
│  └─ Handler: media_handler
│  └─ Images, documents, etc.
│  └─ Facet discovery validates: "Does media depict facet concepts?"
│
└─ quarantine (0.3%)
   └─ Invalid/missing datavalue
   └─ Handler: error_handler
   └─ Facet discovery validates: "Can we salvage any facet signal?"
```

**Integration Point**: Facet discovery adds validation gate to dispatcher routing:

```python
def route_claim(claim_statement, subject_concept):
    """Route claim through dispatcher with facet validation"""
    
    # 1. Identify statement type
    stmt_type = identify_datatype(claim_statement)
    handler = DISPATCHER_ROUTES[stmt_type]
    
    # 2. Get facet relevance from discovery
    facet_relevance = get_facet_relevance(
        subject_concept.wikidata_qid,
        claim_statement.facet
    )
    
    # 3. Validate against discipline
    if facet_relevance.confidence < 0.50:
        logger.warning(f"Low facet confidence: {facet_relevance}")
        # Still route, but flag for review
    
    # 4. Process through appropriate handler
    return handler.process(claim_statement)
```

---

## Your Existing + New Components

### ✅ Already Implemented

1. **Authority Framework** (LCSH, LCC, FAST, Dewey)
   - Library science standards for subject validation
   - Tier system based on evidence quality
   - File: `Subjects/*`, `LCSH/*`, `LCC/*`

2. **Subject Concept Layer** (SubjectConcept nodes)
   - 5 bootstrap concepts (Roman Republic, Roman Empire, etc.)
   - SubjectConceptRegistry for governance
   - File: `scripts/reference/subject_concept_api.py`
   - File: `SUBJECT_CONCEPT_IMPLEMENTATION.md`

3. **Subject Ontology** (Authority alignments)
   - Sparse pointer relationships to LCSH, LCC, FAST
   - Hierarchy support (parent-child)
   - File: `SUBJECT_ONTOLOGY_ARCHITECTURE.md`

4. **Dispatcher Infrastructure** (Wikidata federation)
   - Statement routing by datatype
   - Property allowlists, class denylists
   - Budget-constrained harvesting
   - File: `scripts/tools/wikidata_dispatcher.py` (your backlink harvester)

### 🆕 Now Adding (Facet Discovery)

1. **Facet Discovery Engine** (`facet_qid_discovery.py`)
   - Extracts concepts from Wikipedia discipline articles
   - Queries Wikidata properties
   - Calculates confidence scores

2. **Batch Discovery** (`discover_all_facets.py`)
   - Discovers all 17+ facets simultaneously
   - Stores in `FacetReference` (Neo4j queryable)

3. **Integration Layer** (NEW - to create)
   - Links facet discovery output to SubjectConcept
   - Maps authority tiers to facet assignments
   - Implements three-layer validation

4. **Neo4j Schema Updates** (NEW)
   - Add facet_discovery metadata to SubjectConcept
   - New relationship: `:FACET_DISCOVERY_SOURCE`
   - New constraint: Facet must be in FacetReference

---

## Three-Layer Validation Implementation

### Layer 1: Discipline Knowledge (Wikipedia)
```python
def validate_layer_1_discipline(facet: str, wikidata_qid: str, claim_text: str):
    """Check if facet is valid for this subject's discipline"""
    
    # Get facet discovery results for this QID
    facet_profile = facet_loader.get_facet_profile(wikidata_qid)
    
    # Check if proposed facet exists in profile
    if facet not in facet_profile:
        return {
            "valid": False,
            "reason": f"Facet '{facet}' not in discipline"
        }
    
    # Get confidence for this facet
    facet_confidence = facet_profile[facet]["confidence"]
    
    # Keyword matching
    keywords = facet_profile[facet]["key_topics"]
    matched_keywords = [kw for kw in keywords if kw.lower() in claim_text.lower()]
    
    return {
        "valid": True,
        "facet_confidence": facet_confidence,
        "keyword_matches": matched_keywords,
        "keyword_match_score": len(matched_keywords) / len(keywords),
        "layer_1_score": (facet_confidence + keyword_match_score) / 2
    }
```

### Layer 2: Subject Authority (LCSH + Wikidata + Wikipedia)
```python
def validate_layer_2_authority(concept_id: str, facet: str):
    """Check if facet is valid for this subject's authority tier"""
    
    concept = get_subject_concept(concept_id)
    
    # Evaluate authority tier
    tier_data = {
        "has_lcsh": bool(concept.lcsh_id),
        "has_wikidata": bool(concept.wikidata_qid),
        "has_wikipedia": check_wikipedia_exists(concept.label)
    }
    
    tier = evaluate_authority_tier(tier_data)
    
    # Check if facet is supported at this tier
    if tier == 1:
        # Tier 1: Any facet supported
        confidence = 0.98
    elif tier == 2:
        # Tier 2: Facet must be in Wikidata properties
        confidence = check_wikidata_properties(concept.wikidata_qid, facet)
    else:
        # Tier 3: Facet must be in LCSH
        confidence = check_lcsh_facet_coverage(concept.lcsh_id, facet)
    
    return {
        "authority_tier": tier,
        "authority_confidence": confidence,
        "facet_supported": confidence > 0.50,
        "layer_2_score": confidence
    }
```

### Layer 3: Civilization Patterns (Agent Training)
```python
def validate_layer_3_civilization(
    concept_id: str,
    facet: str,
    claim_text: str,
    trained_ontology
):
    """Check if facet patterns match training data"""
    
    # Get facet-specific training data
    facet_patterns = trained_ontology.get_facet_patterns(facet)
    
    # Check keyword overlap with training
    training_keywords = facet_patterns.get("keywords", [])
    claim_keywords = extract_keywords(claim_text)
    overlap = set(training_keywords) ∩ set(claim_keywords)
    
    # Check if facet has sufficient training coverage
    training_count = facet_patterns.get("training_examples", 0)
    
    return {
        "facet_training_coverage": min(training_count / 50, 1.0),  # Normalize to 0-1
        "training_keyword_overlap": len(overlap) / len(training_keywords) if training_keywords else 0,
        "is_extrapolation": len(overlap) == 0,  # Applying facet outside training
        "layer_3_score": (facet_training_coverage + training_keyword_overlap) / 2
    }
```

### Final Validation
```python
def validate_three_layers(proposal):
    """Combine all three layers"""
    
    layer1 = validate_layer_1_discipline(...)
    layer2 = validate_layer_2_authority(...)
    layer3 = validate_layer_3_civilization(...)
    
    # All must agree
    all_valid = (
        layer1["valid"] and
        layer2["facet_supported"] and
        (layer3["facet_training_coverage"] > 0.30 or not layer3["is_extrapolation"])
    )
    
    if all_valid:
        # Average confidence across layers
        confidence = (
            layer1["layer_1_score"] +
            layer2["layer_2_score"] +
            layer3["layer_3_score"]
        ) / 3
        
        if confidence >= 0.90:
            status = "AUTO_APPROVED"
        elif confidence >= 0.75:
            status = "APPROVED_PENDING_REVIEW"
        else:
            status = "FLAGGED_LOW_CONFIDENCE"
    else:
        status = "REJECTED"
        confidence = 0.0
    
    return {
        "status": status,
        "confidence": confidence,
        "layer1": layer1,
        "layer2": layer2,
        "layer3": layer3
    }
```

---

## Data Flow: Complete End-to-End

```
INPUT: Finding text about Roman civilization

  USER/GPT SUBMITS:
  ├─ Subject: Roman Republic
  ├─ Finding: "Evidence of grain imports from Egypt"
  └─ Proposed facet: Economic

  SYSTEM VALIDATES:
  
  Step 1: Load Subject Concept
  └─ Get: subj_roman_republic_q17167 (Tier 1, strong facets)
  
  Step 2: Layer 1 - Discipline Knowledge
  ├─ Query: FacetReference(Economic) → Categories
  ├─ Check: Does "Trade" category exist? YES
  ├─ Match: Keywords [trade, import, export, commerce] vs finding
  ├─ Score: 4/5 keywords matched = 0.80
  └─ Layer 1 Result: PASS (0.80 confidence)
  
  Step 3: Layer 2 - Authority
  ├─ Query: Roman Republic (Tier 1)
  ├─ Check: Economic facet supported? YES (LCSH + Wikidata + Wikipedia)
  ├─ Score: Tier 1 baseline 0.98
  └─ Layer 2 Result: PASS (0.98 confidence)
  
  Step 4: Layer 3 - Civilization
  ├─ Query: Trained ontology for Roman + Economic
  ├─ Check: Egypt trade mentioned in training? YES (15 Wikipedia sources)
  ├─ Match: Keywords [Egypt, grain, import] in training
  ├─ Score: 30/50 training examples = 0.60, keyword overlap = 0.80
  ├─ Average: (0.60 + 0.80) / 2 = 0.70
  └─ Layer 3 Result: PASS (0.70 confidence)
  
  Step 5: Final Validation
  ├─ Layer 1 PASS (0.80)
  ├─ Layer 2 PASS (0.98)
  ├─ Layer 3 PASS (0.70)
  ├─ All three agree: YES
  ├─ Average: (0.80 + 0.98 + 0.70) / 3 = 0.83
  └─ Status: AUTO_APPROVED (confidence 0.83)

OUTPUT: Create SubjectConcept + Claim
  ├─ Concept: "Roman Egypt Trade Networks"
  ├─ Parent: Roman Republic
  ├─ Facet: Economic
  ├─ Confidence: 0.83
  ├─ Validation: "THREE_LAYER_PASS"
  ├─ Evidence: [Layer1, Layer2, Layer3 validation traces]
  └─ Stored to Neo4j with full audit trail
```

---

## Summary: How All Pieces Work Together

```
Your existing authorities (LCSH, LCC, FAST, Wikidata, Wikipedia)
    ↓
Facet discovery extracts discipline structure from Wikipedia/Wikidata
    ↓
SubjectConcept nodes link all authorities together
    ↓
Authority tiers determine confidence levels
    ↓
Phase 2B agents route claims using facet assignments
    ↓
Three-layer validation ensures no hallucination
    ↓
Dispatcher routes to appropriate handler based on datatype
    ↓
Final claims stored with complete validation trail
    ↓
Library system can answer: "Under what subject, in which facet, with what confidence?"
```

**Result**: An integrated authority system that grounds all claims in multiple independent sources (library science, external linked data, Wikipedia, training data) simultaneously.
