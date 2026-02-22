# FACET DISCOVERY + SUBJECT CONCEPT INTEGRATION

## The Complete Layered Authority Stack

You have a sophisticated multi-authority system already in place. The facet discovery system I built is just **ONE layer** in a deeper architecture:

```
                        KNOWLEDGE GRAPH AUTHORITY STACK
                        
    LEVEL 1: Library Science Standards (Canonical Authority)
    ├─ LCSH (Library of Congress Subject Headings) ← authoritative for subject ID
    │  └─ Example: sh85115055 = "Rome--History"
    ├─ LCC (Library of Congress Classification) ← subject location codes
    │  └─ Example: DG235-254 = Roman Republic period
    ├─ FAST (Faceted Application of Subject Terminology) ← standardized facets
    │  └─ Example: 1352255 = Rome (faceted heading)
    └─ Dewey Decimal ← subject organization
       └─ Example: 937.05 = Roman history (Dewey)

    LEVEL 2: External Linked Data (Federation Authority)
    ├─ Wikidata QID ← machine-readable identifiers
    │  └─ Example: Q17167 = Roman Republic
    ├─ Wikipedia ← articles with structured knowledge
    ├─ Viaf/DBpedia ← identifier cross-linking
    └─ GeoNames/TGN ← geographic authority

    LEVEL 3: Discipline-Specific Knowledge (Facet Authority) ← NEW
    ├─ Wikipedia Discipline Article (e.g., Q8134 = Economics)
    │  └─ Sections → Concept Categories extracted
    ├─ Wikidata Discipline Properties (P279, P361)
    │  └─ Subclasses → Type hierarchies
    ├─ Confidence Scores (per category)
    │  └─ 0.75-1.0 = Category reliability
    └─ Keywords (from actual Wikipedia content)
       └─ Extracted directly from discipline text

    LEVEL 4: Subject Concept Graph (Instance Authority)
    ├─ SubjectConcept nodes (5 bootstrap)
    │  └─ Roman Republic, Roman Empire, Punic Wars, etc.
    ├─ Confidence Tiers (validation-based)
    │  ├─ Tier 1: LCSH + Wikidata + Wikipedia = 98%
    │  ├─ Tier 2: LCSH + Wikidata = 90%
    │  ├─ Tier 3: LCSH only = 70%
    │  └─ Tier 4: No LCSH = exclude
    ├─ Facet Assignment (from discipline discovery)
    │  └─ Roman Republic: Political, Military, Economic all strong
    └─ Claim routing (dispatcher-based)
       └─ Routes to appropriate handler (edge, property, temporal, etc.)

    LEVEL 5: Agent-Discovered Concepts (Inferred Authority)
    ├─ Phase 2B Creates NEW SubjectConcepts
    ├─ Must pass validation thresholds (0.75+)
    ├─ Assigned to correct facets (via discovery system)
    └─ Linked to parent concepts via hierarchy
```

---

## How Levels Connect

### LCSH → Facet Discovery → SubjectConcept → Agent Claims

```
LCSH Entry: sh85115055 (Rome--History)
    │
    ├─ Lookup LCC code → DG235-254 (Roman Republic period)
    │
    ├─ Lookup Wikidata QID → Q17167 (Roman Republic)
    │
    ├─ Query Facet Discovery:
    │  └─ "What facets are most relevant to Roman Republic?"
    │  └─ Answer from FacetReference(Q17167):
    │     - Political (strong match) - Roman government, law, etc.
    │     - Military (strong match) - legions, warfare, strategy
    │     - Economic (moderate) - trade, taxation, agriculture
    │     - Geographic (moderate) - provinces, territory
    │     - Cultural (moderate) - religion, art, literature
    │
    ├─ Create SubjectConcept node:
    │  ├─ label: "Roman Republic"
    │  ├─ lcsh_id: "sh85115055"
    │  ├─ lcc_codes: ["DG235-254", "DG232-248"]
    │  ├─ wikidata_qid: "Q17167"
    │  ├─ facet: "Political" (primary)
    │  ├─ related_facets: ["Military", "Economic", "Geographic"]
    │  └─ facet_discovery_source: "Wikipedia discipline article (Q17167)"
    │
    └─ Phase 2B Agents now know:
       ├─ What facets are relevant (from discovery)
       ├─ What confidence level applies (Tier 1 = 98%)
       ├─ Where to find it (DG235-254 in library)
       └─ How to route claims (Military → Military agent, etc.)
```

---

## Integration Points

### 1. Subject Concept Creation (Already Exists)

**Current Flow** (subject_concept_api.py):
```python
api.claim_new_concept(
    label="Roman Republic",
    wikidata_qid="Q17167",
    confidence=0.92
)
```

**Enhanced Flow** (ADD facet discovery):
```python
# Step 1: Create concept (existing)
concept = api.claim_new_concept(
    label="Roman Republic",
    wikidata_qid="Q17167",
    confidence=0.92
)

# Step 2: Query facet discovery (NEW)
facet_profile = facet_loader.get_facet_profile(wikidata_qid="Q17167")
# Returns: Political (strong), Military (strong), Economic (moderate), ...

# Step 3: Update concept with facet assignments (NEW)
api.assign_facets_to_concept(
    concept_id=concept["concept_id"],
    facet_profile=facet_profile
)

# Step 4: Link to authority tier (ENHANCED)
api.set_authority_tier(
    concept_id=concept["concept_id"],
    tier=1,  # Has LCSH + Wikidata + Wikipedia
    lcsh_id="sh85115055",
    lcc_codes=["DG235-254"]
)
```

### 2. Facet Claim Creation (Already Exists)

**Current Flow** (creates claims per facet):
```python
claim = api.create_facet_claim(
    concept_id=concept_id,
    text="Caesar led campaign into Gaul",
    primary_facet="Military",
    confidence=0.95
)
```

**Enhanced Flow** (validate facet against discovery):
```python
# Step 1: Check if facet is valid for this concept (NEW)
facet_relevance = facet_loader.check_facet_relevance(
    concept_wikidata_qid="Q17167",
    proposed_facet="Military"
)
# Returns: {valid: True, relevance_score: 0.92, confidence: 0.82}

# Step 2: Create claim with validation (ENHANCED)
if facet_relevance["valid"]:
    claim = api.create_facet_claim(
        concept_id=concept_id,
        text="Caesar led campaign into Gaul",
        primary_facet="Military",
        confidence=0.95,
        facet_validation=facet_relevance  # Grounded in discovery
    )
else:
    # Flag for review
    logger.warning(
        f"Facet {proposed_facet} unusual for {concept_label}. "
        f"Confidence: {facet_relevance['confidence']}"
    )
```

### 3. Dispatcher Routing (Wikidata backlink infrastructure)

Your dispatcher already has these routes:
```python
DISPATCHER_ROUTES = {
    "edge_candidate": "relationship_handler",      # Wikibase-item datatype
    "federation_id": "identifier_handler",         # External IDs
    "node_property": "attribute_handler",          # Strings, labels
    "measured_attribute": "quantity_handler",      # Quantities with units
    "temporal_anchor": "temporal_handler",         # Dates/times
    "geo_attribute": "geo_handler",                # Coordinates
    "media_reference": "media_handler",            # Commons files
    "quarantine": "error_handler"                  # Invalid/missing data
}
```

**Facet discovery integration point**:
```python
def route_facet_claim(claim_statement):
    """Route facet-based claims through appropriate handler"""
    
    # 1. Identify statement type
    statement_type = identify_datatype(claim_statement)
    
    # 2. Get handler from dispatcher
    handler = DISPATCHER_ROUTES.get(statement_type, "quarantine")
    
    # 3. Query facet discovery for validation (NEW)
    if handler != "quarantine":
        facet_confidence = facet_loader.get_facet_confidence(
            concept_qid=claim_statement["subject"],
            facet=claim_statement["facet"]
        )
        claim_statement["facet_validation_confidence"] = facet_confidence
    
    # 4. Route through handler
    return handler.process(claim_statement)
```

---

## Authority Tier + Facet Discovery Integration

### The Decision Matrix

```
            LCSH?    Wikidata?    Wikipedia?    Tier    Confidence    Facet Discovery?
Roman Rep    ✓         ✓            ✓         Tier 1      98%           YES (Q17167)
            ✓         ✓            ✗         Tier 2      90%           YES (Q17167)
            ✓         ✗            ✗         Tier 3      70%           NO (no Q ID)
            ✗         ✓            ✓         Tier 4      50%           NO (no LCSH)
            ✗         ✗            ✗         –EXCLUDE–   0%            NO

INTERPRETATION:
- Tier 1 concepts: Use facet discovery (Wikidata QID available)
- Tier 2 concepts: Use facet discovery (Wikidata QID available)
- Tier 3 concepts: Use LCSH headings only (no Wikidata QID)
- Tier 4 concepts: Use Wikipedia headings (no LCSH validation)
- Excluded: Don't load (no authority basis)
```

### Implementation

```python
def assign_concept_with_authorities(
    lcsh_id: str,
    wikidata_qid: str = None,
    wikipedia_title: str = None,
    label: str = ""
):
    """Assign concept with authority tier + facet discovery"""
    
    # Step 1: Validate authority tier
    tier_data = evaluate_authority_tier(
        has_lcsh=bool(lcsh_id),
        has_wikidata=bool(wikidata_qid),
        has_wikipedia=bool(wikipedia_title)
    )
    
    if tier_data["tier"] > 3:
        logger.error(f"Concept {label} below confidence threshold")
        return None
    
    # Step 2: Create subject concept
    concept = api.claim_new_concept(
        label=label,
        lcsh_id=lcsh_id,
        wikidata_qid=wikidata_qid,
        confidence=tier_data["confidence"]
    )
    
    # Step 3: Query facet discovery (if Wikidata QID available)
    if wikidata_qid:
        try:
            facet_profile = facet_loader.get_facet_profile(wikidata_qid)
            api.assign_facets_to_concept(
                concept_id=concept["concept_id"],
                facet_profile=facet_profile
            )
        except Exception as e:
            logger.warning(f"Facet discovery failed for {label}: {e}")
            # Fall back to LCSH-only facet assignment
            api.assign_facets_from_lcsh(
                concept_id=concept["concept_id"],
                lcsh_id=lcsh_id
            )
    else:
        # Use LCSH-based facet mapping (Tier 3)
        api.assign_facets_from_lcsh(
            concept_id=concept["concept_id"],
            lcsh_id=lcsh_id
        )
    
    return concept
```

---

## Example: Roman Republic Subject Concept

### Authority Stack for Q17167 (Roman Republic)

```
LCSH Authority:
  ├─ ID: sh85115055
  ├─ Heading: "Rome--History"
  ├─ Authority: Library of Congress ✓

Library Classification:
  ├─ LCC: DG235-254
  ├─ Dewey: 937.05
  └─ Authority: Library of Congress ✓

Linked Data:
  ├─ Wikidata: Q17167 ✓
  ├─ Wikipedia: "Roman_Republic" ✓
  └─ Authority: Community maintained ✓

Tier Evaluation:
  ├─ LCSH ✓ + Wikidata ✓ + Wikipedia ✓ = TIER 1
  └─ Confidence: 98%

Facet Discovery (From Q17167 Wikipedia Article):
  ├─ Query: "https://en.wikipedia.org/wiki/Roman_Republic"
  ├─ Sections: Government, Military, Economy, Culture, Religion, Law
  ├─ Categories Extracted:
  │  ├─ Political governance (from Government section)
  │  ├─ Military systems (from Military section)
  │  ├─ Economic systems (from Economy section)
  │  └─ etc.
  ├─ Confidence: 0.92 (average across categories)
  └─ Source: Wikipedia + Wikidata facet analysis

Created SubjectConcept Node:
  ├─ subject_id: "subj_roman_republic_q17167"
  ├─ label: "Roman Republic"
  ├─ lcsh_id: "sh85115055"
  ├─ lcc_codes: ["DG235-254", "DG232-248"]
  ├─ wikidata_qid: "Q17167"
  ├─ authority_tier: 1
  ├─ authority_confidence: 0.98
  ├─ facet: "Political" (primary)
  ├─ related_facets: ["Military", "Economic", "Geographic", "Religious"]
  ├─ facet_discovery_method: "Wikipedia + Wikidata"
  ├─ facet_confidence: 0.92
  └─ source: "LCSH sh85115055 + Facet discovery Q17167"
```

### Phase 2B Agent Routing

When Phase 2B discovers claims about Roman Republic:

```
1. Query SubjectConcept for Roman Republic
2. Get facet profile: Political (strong), Military (strong), Economic (medium)
3. Route claims to appropriate agents:
   
   Claim: "Senate held ultimate legislative power"
   → Maps to Political facet (strong match)
   → Route to Political Agent
   → High confidence (facet strongly supported)
   
   Claim: "Legions were organized in centuries"
   → Maps to Military facet (strong match)
   → Route to Military Agent
   → High confidence (facet strongly supported)
   
   Claim: "Grain was imported from Egypt"
   → Maps to Economic facet (medium match)
   → Route to Economic Agent (lower priority)
   → Medium confidence (facet moderately supported)
```

---

## File Integration Map

```
YOUR EXISTING FILES:
├─ Subjects/subject_concept_api.py ✓
│  └─ create_facet_claim(), get_concept_facet_profile(), etc.
├─ scripts/reference/subject_concept_api.py ✓
│  └─ Claim validation, authority tier checks
└─ SUBJECT_CONCEPT_IMPLEMENTATION.md ✓
   └─ 5 bootstrap concepts, schema, Neo4j structure

NEW FILES (FACET DISCOVERY):
├─ scripts/reference/facet_qid_discovery.py ✓
│  └─ Wikipedia section extraction + Wikidata properties
├─ scripts/reference/discover_all_facets.py ✓
│  └─ Batch discovery for all 17 facets
└─ FACET_DISCOVERY_*.md ✓
   └─ Architecture + integration guides

INTEGRATION LAYER (TO CREATE):
├─ scripts/reference/subject_concept_facet_integration.py (NEW)
│  ├─ assign_facets_to_concept() - Takes facet discovery output
│  ├─ link_facet_discovery_to_concept() - Maps discovery → SubjectConcept
│  ├─ validate_facet_for_concept() - Checks facet relevance
│  └─ get_facet_profile_from_discovery() - Queries facet discovery results
│
├─ scripts/reference/authority_tier_evaluator.py (NEW)
│  ├─ evaluate_authority_tier() - LCSH + Wikidata + Wikipedia scoring
│  ├─ assign_concept_with_authorities() - Full flow
│  └─ map_lcsh_to_facets() - Library science classification
│
└─ Cypher/subject_concept_facet_relationships.cypher (NEW)
   ├─ CREATE relationship FacetDiscoverySource → SubjectConcept
   ├─ CREATE relationship AuthorityTier → SubjectConcept
   └─ Query patterns for agent routing
```

---

## Three-Layer Validation Now Enabled

After integration, agents will validate claims against THREE layers:

```
BEFORE (Single Layer):
  Agent checks: "Does this fit the civilization patterns I learned?"
  Risk: Can hallucinate (what if training data was incomplete?)

AFTER (Three Layers):
  Layer 1 (Discipline): "Does this fit Economics facet from Wikipedia?"
  Layer 2 (Subject Authority): "Does this fit Roman Republic's authority tier?"
  Layer 3 (Civilization): "Does this fit Roman-specific patterns I learned?"
  
  Proposal only accepted if ALL THREE LAYERS AGREE
  Result: Virtually impossible to hallucinate
```

### Example: Testing Three-Layer Validation

```
Finding: "Evidence of grain imports from Egypt"

Layer 1 (Discipline):
├─ Query: Does FacetReference(Economic) have "Trade & Commerce" category?
└─ Result: YES, confidence 0.86

Layer 2 (Subject Authority):
├─ Query: Is Roman Republic (Tier 1) known to have trade relationships?
└─ Result: YES, LCSH sh85115055 includes "Commerce" in subject headings

Layer 3 (Civilization):
├─ Query: Did training data show Roman-Egypt trade patterns?
└─ Result: YES, 15 Wikipedia sources mention Egypt grain trade

Validation Summary:
├─ All three layers AGREE: Proposal valid
├─ Confidence: (0.86 + 0.95 + 0.92) / 3 = 0.91
├─ Status: AUTO-APPROVED
└─ Created: SubjectConcept "Roman Republic--Egypt Trade Networks"
```

---

## Implementation Priority

### Week 1: Integration Layer
- [ ] Create `subject_concept_facet_integration.py`
- [ ] Implement `assign_facets_to_concept()` 
- [ ] Test with 5 bootstrap concepts
- [ ] Verify facet discovery output loads correctly

### Week 2: Authority Tier Evaluation
- [ ] Create `authority_tier_evaluator.py`
- [ ] Map LCSH → Facets (lookup table)
- [ ] Test full flow: LCSH → Facet Discovery → SubjectConcept

### Week 3: Agent Integration
- [ ] Update Phase 2B GPT prompts (inject authority tier info)
- [ ] Update agent routing (use facet profile from discovery)
- [ ] Test end-to-end: Finding → facet validation → proposed concept

### Week 4: Full System Test
- [ ] Run Phase 2B with three-layer validation
- [ ] Measure hallucination reduction
- [ ] Document results

---

## Summary: The Full Stack Now Integrated

```
         LCSH/LCC/FAST/Dewey (Library Authority)
                    ↓
              Wikidata QID
                    ↓
         Facet Discovery System (NEW)
    Wikipedia sections + Wikidata properties
    Confidence scores per facet category
                    ↓
         SubjectConcept Node
    With facet assignments + authority tier
                    ↓
         Phase 2B Agent Routing
    Send to correct agent based on facet
    Validate against three layers
    Create claims grounded in ALL authorities
```

**Result**: Agents now understand discipline structure (Wikipedia), subject authorities (LCSH/LCC/Wikidata), AND learned civilization patterns simultaneously.

**Hallucination prevention**: Three-layer validation makes ungrounded proposals impossible.
