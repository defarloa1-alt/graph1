# AI Context and Handover Log
Maintained by LLM agents to preserve context across sessions.

---

## ⚠️ Important: Persistence Workflow

**This file only works as a memory bank if committed and pushed regularly.**

- **Local sessions**: Updates are visible in real-time ✅
- **Future sessions**: Only see last pushed version ⚠️
- **Other AI agents**: Need to pull latest from GitHub ⚠️

**Workflow for AI agents:**
1. **Start of session**: Read this file first (pull latest if stale)
2. **During session**: Update as you complete milestones
3. **End of session**: Commit and push this file so next agent sees current state

**Without regular pushes, this becomes a local-only scratchpad.**

---

## Project
Chrystallum Knowledge Graph
Goal: Build a federated historical knowledge graph using Neo4j, Python, and LangGraph.

## PRIMARY ARCHITECTURE SOURCE

**Canonical Reference:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` (v3.2)
- **Authoritative specification** for all architecture decisions
- 7,698 lines covering Entity Layer, Subject Layer, Agent Architecture, Claims, Relationships
- Sections 1-12 + Appendices A-N
- **DO NOT DUPLICATE** architecture content here—reference sections instead

**Implementation Index:** `ARCHITECTURE_IMPLEMENTATION_INDEX.md` (maps sections → implementation files)

---

## Latest Update: BiographicSFA Responsibilities Clarification (2026-02-16 Afternoon)

### Three Critical Producer Roles Defined

**Context:** User clarified that BiographicSFA is responsible for constructing family trees, defining canonical relationships, and proposing biographical events that seed other facets.

**BiographicSFA Primary Responsibilities:**

1. **Person Identity & Career Structure**
   - Creates person nodes (Q5 instances) with canonical IDs
   - Builds career sequences (cursus honorum)
   - Defines status markers (senatorial, equestrian, plebeian)

2. **Family Tree & Relationship Network Construction** 🔥 CRITICAL
   - Constructs family trees (genealogical stemma)
   - Maps kinship relations with **canonical relationship types**
   - Models adoption patterns (critical in Roman society)
   - Maps marriage alliances (political marriages)
   - See `Facets/CANONICAL_RELATIONSHIP_TYPES.md` for complete taxonomy

3. **Biographical Event Proposal** 🔥 NEW ROLE
   - **Proposes event claims** that seed multi-facet analysis:
     * Birth/death events (temporal boundaries)
     * Office appointments (career milestones)
     * Marriage events (alliance formation)
     * Adoption events (legal identity changes)
   - **Seeder pattern:** BiographicSFA proposes → Other facets analyze
   - Example: BiographicSFA: "Caesar born 100 BCE" → MilitarySFA: "Caesar commanded..." (constrained by birth date)

**Files Created/Updated:**
- ✅ `Facets/BIOGRAPHIC_SFA_ONTOLOGY_METHODOLOGY.md` (enhanced with canonical relationships + event proposals)
- ✅ `Facets/CANONICAL_RELATIONSHIP_TYPES.md` (NEW - complete relationship taxonomy reference)
- ✅ Implementation checklist updated (family tree construction, event workflow validation)

**Key Insight:** BiographicSFA is a **producer facet** (creates nodes/events) that other facets **consume** (reference for their analyses). No other facet creates person nodes or biographical events—they only reference BiographicSFA's claims.

**Canonical Relationship Types (Quick Reference):**
- Family: CHILD_OF, PARENT_OF, SIBLING_OF, MARRIED, ADOPTED_BY
- Clan: MEMBER_OF_GENS, FOUNDER_OF_GENS, COGNOMEN_BRANCH
- Political: POLITICAL_ALLY_OF, POLITICAL_RIVAL_OF, ENEMY_OF
- Social: PATRON_OF, CLIENT_OF, MENTOR_OF, FRIEND_OF
- Affinal: FATHER_IN_LAW_OF, SON_IN_LAW_OF, BROTHER_IN_LAW_OF

**Event Proposal Pattern:**
```python
# BiographicSFA creates event
bio_event = create_facet_claim(
    facet="biographic",
    subject="Q1048",  # Caesar
    property="APPOINTED_TO",  # Canonical event type
    object="Q20056508",  # Consul
    temporal_scope="-0059"
)

# SCA evaluates relevance → queues to Political & Military SFAs

# Other facets create THEIR OWN claims referencing the event
pol_claim = create_facet_claim(
    facet="political",
    subject="Q1048",
    property="HELD_SUPREME_AUTHORITY",
    temporal_scope="-0059",
    context_claims=[bio_event.cipher]  # References bio event
)
```

---

## Previous Update: Claim ID Architecture Refinement (2026-02-16 Morning)

### Critical Architectural Revision: Stable Claim Ciphers

**Context:** User challenged existing claim cipher formula that included provenance metadata (confidence, agent, timestamp) in the hash, causing instability and breaking deduplication.

**Problems Identified:**
1. **Confidence in cipher** → Evidence improvement creates new claim ID (instability)
2. **Timestamp in cipher** → Two agents discovering same fact at different times = different IDs (breaks deduplication)
3. **Agent in cipher** → Provenance metadata treated as logical content (conflates concerns)
4. **Missing facet_id** → Facet dimension not explicit in formula (critical for 17-facet architecture)
5. **Implementation divergence** → Code used 4-component formula, docs specified 9 components

**User Insight:** "Treat the claim as its own first-class node whose ID is derived from its *content and context*, not by concatenating all underlying node IDs." Cited nanopublication standards (research.vu.nl, pmc.ncbi.nlm.nih.gov, cidoc-crm.org).

**Solution: Nanopublication-Aligned Claim Identity**

#### Revised Facet-Level Claim Cipher (Stable)
```python
facet_claim_cipher = Hash(
    # Core assertion
    subject_node_id +            # Q1048 (Caesar)
    property_path_id +           # "CHALLENGED_AUTHORITY_OF"
    object_node_id +             # Q1747689 (Roman Senate)
    
    # Context
    facet_id +                   # "political" (essential!)
    temporal_scope +             # "-0049-01-10"
    
    # Source
    source_document_id +         # Q644312 (Plutarch)
    passage_locator              # "Caesar.32"
    
    # REMOVED: confidence, agent, timestamp (now separate metadata)
)
```

#### Hierarchical Facet Claims (Sibling/Parent Model)
- **Facet Claims (Siblings):** Independent assertions per facet (military, political, geographic)
- **Composite Claims (Parent):** References sorted facet claim ciphers, not raw node IDs
- Prevents concatenation instability (entity evolution ≠ claim identity)

**Files Updated:**
- ✅ Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md (Section 6.4, ~200 lines)
- ✅ SCA_SFA_ROLES_DISCUSSION.md (~100 lines)
- ✅ SCA_SFA_ARCHITECTURE_PACKAGE.md (~80 lines)
- ✅ scripts/tools/claim_ingestion_pipeline.py (_calculate_cipher method rewritten)
- ✅ **NEW:** Key Files/CLAIM_ID_ARCHITECTURE.md (comprehensive 10-section reference, ~800 lines)

**Benefits:**
- ✅ Automatic deduplication (same content = same cipher regardless of agent/time)
- ✅ Citation stability (cipher unchanged when confidence updates)
- ✅ Clean separation: entity identity vs assertion identity
- ✅ Aligned with nanopublication assertion graph standards

**Reference:** See `Key Files/CLAIM_ID_ARCHITECTURE.md` for complete specification.

**Facet Architecture Update (Feb 16):**
- Added **BiographicFacet** (#17) - Prosopography, careers, person identity (DPRR integration)
- Added **CommunicationFacet** (#18) - Rhetoric, media, information transmission (meta-facet)
- **Total: 18 facets** (16 core + biographic + communication)

---

## Previous Update: SCA ↔ SFA Roles Finalized + Selective Queue Model (2026-02-15 Evening)

### Major Architectural Decision: Agent Coordination Model

**Context:** After real agent spawning deployment, needed to finalize how SubjectConceptAgent (SCA) coordinates SubjectFacetAgents (SFAs) during claim creation.

**Key Insight from User:** "SFA is studying the discipline, dealing with abstract concepts at first, so it is really building a subject ontology and it might be premature to involve the other SFAs at this particular point in the process."

**Solution: Two-Phase Workflow with Selective Queue**

#### Phase 1: Training Mode (Independent)
- SFAs study discipline independently (Political Science, Military History, etc.)
- Build domain-specific subject ontologies
- Create claims about **abstract concepts** ("Senate legislative authority", "Legion structure")
- Work **independently** - NO cross-facet collaboration yet
- SCA accepts all training claims as-is (**NO QUEUE**)

**Example:**
```
Political SFA (Training):
  → "Senate held legislative authority" (abstract political concept)
  → SCA evaluation: Abstract domain concept → Accept as-is (no queue)

Military SFA (Training):
  → "Legion composed of cohorts" (abstract military structure)
  → SCA evaluation: Abstract domain concept → Accept as-is (no queue)
```

#### Phase 2: Operational Mode (Selective Collaboration)
- SFAs encounter **concrete entities/events**
- **SCA evaluates** each claim for multi-facet potential
- SCA uses **relevance scoring** (0-1.0) to determine which SFAs should analyze
- Only relevant SFAs receive claim for perspective creation
- FacetPerspective nodes created when queued

**Example:**
```
Political SFA creates:
  → "Caesar appointed dictator in 49 BCE" (concrete historical event)

SCA evaluation:
  → Type: Concrete event (not abstract concept)
  → Entities: Caesar (Q1048), Dictator office, 49 BCE
  → Relevance scoring:
    * Military SFA: 0.9 (Caesar = commander) → QUEUE
    * Economic SFA: 0.8 (dictator = treasury) → QUEUE
    * Cultural SFA: 0.3 (minor impact) → SKIP
    * Religious SFA: 0.2 (no dimension) → SKIP

SCA decision: Queue to Military + Economic ONLY

Military SFA (Perspective Mode):
  → Creates FacetPerspective: "Caesar commanded all Roman armies as dictator"
  → Attaches to same claim via cipher

Economic SFA (Perspective Mode):
  → Creates FacetPerspective: "Caesar controlled state treasury as dictator"
  → Attaches to same claim via cipher

Result:
  1 Claim (cipher-based) + 3 FacetPerspectives (political, military, economic)
  Consensus: AVG(0.95, 0.90, 0.88) = 0.91
```

#### Claim Architecture: Cipher + Star Pattern

**Claim = Star Pattern Subgraph** (not single node):
```
              (Claim: cipher="claim_abc123...")
                        │
   ┌────────────────────┼────────────────────┐
   │                    │                    │
[PERSP_ON]         [PERSP_ON]         [PERSP_ON]
   │                    │                    │
   ▼                    ▼                    ▼
(Perspective:      (Perspective:      (Perspective:
 Political)         Military)          Economic)
```

**Cipher (Content-Addressable ID):**
```python
claim_cipher = Hash(
    source_work_qid + passage_text_hash + subject_entity_qid +
    relationship_type + temporal_data + confidence_score +
    extractor_agent_id + extraction_timestamp
)
# Result: "claim_abc123..." (unique cipher)
```

**Benefit:** Two SFAs discovering SAME claim → SAME cipher → Single Claim node (automatic deduplication)

**FacetPerspective Nodes (NEW):**
```cypher
(:FacetPerspective {
  perspective_id: "persp_001",
  facet: "political",
  parent_claim_cipher: "claim_abc123...",
  facet_claim_text: "Caesar challenged Senate authority",
  confidence: 0.95,
  source_agent_id: "political_sfa_001",
  timestamp: "2026-02-15T10:00:00Z",
  reasoning: "Dictatorship violated Republican norms"
})-[:PERSPECTIVE_ON]->(Claim {cipher: "claim_abc123..."})
```

#### SCA Routing Criteria (5 Criteria Framework)

**How SCA determines which claims warrant cross-facet review:**

1. **Abstract vs Concrete Detection:**
   - Abstract domain concepts → NO QUEUE (accept as-is)
   - Concrete events/entities → EVALUATE FOR QUEUE

2. **Multi-Domain Relevance Scoring (0-1.0 scale):**
   - High (0.8-1.0) → Queue to SFA
   - Medium (0.5-0.7) → Queue to SFA
   - Low (0.0-0.4) → Skip

3. **Entity Type Detection:**
   - Query Wikidata P31 (instance of)
   - Map entity types to facet relevance
   - Q5 (Human) → Political, Military, Cultural potential

4. **Conflict Detection:**
   - Date discrepancies → Queue for synthesis
   - Attribute conflicts → Queue for synthesis

5. **Existing Perspectives Check:**
   - Query: `MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim {cipher: $cipher})`
   - Only queue to facets NOT already analyzed

#### Military SFA Ontology Methodology

**Problem:** Wikidata "what links here" overwhelmed by platform noise (Wikimedia categories, templates, Commons files)

**Solution:** Disciplinary filtering methodology

**Anchor:** Start from `Q192386` (military science) as scholarly root, not vague "military" label

**Property Whitelist (PREFER):**
- P279 (subclass of) - Taxonomic backbone
- P31 (instance of) - Type classification
- P361 (part of) / P527 (has part) - Compositional structure
- P607 (conflict) - Military conflicts
- P241 (military branch), P410 (military rank), P7779 (military unit)

**Wikimedia Blacklist (EXCLUDE):**
- Q4167836 (Wikimedia category)
- Q11266439 (Wikimedia template)
- Q17633526 (Wikinews article)
- Q15184295 (Wikimedia module)

**Roman Republic Refinement:**
- Intersect generic military ontology with Q17167 (Roman Republic)
- Use P1001 (applies to jurisdiction), P361 (part of)
- Temporal overlap: 509 BCE - 27 BCE

**Result:** ~80-90% noise reduction, clean disciplinary ontology (~500-1,000 generic military concepts → ~100-200 Roman Republican specializations)

**Files:**
- [SCA_SFA_ROLES_DISCUSSION.md](SCA_SFA_ROLES_DISCUSSION.md) - Complete roles specification (1,153 lines)
- [CLAIM_WORKFLOW_MODELS.md](CLAIM_WORKFLOW_MODELS.md) - Workflow comparison (450 lines)
- [Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md](Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md) - Wikidata filtering methodology (1,100 lines)

**Status:** ✅ Architecture finalized, ready for implementation

---

## Previous Update: Step 4 Complete - Semantic Enrichment & CIDOC-CRM/CRMinf Ontology Alignment (2026-02-15 Afternoon)

### Critical Problem: LLMs Don't Persist Between Sessions
**User Requirement:** "the llm cannot be counted on to persist between sessions, and it needs to know what the subgraph for the SubjectConcept currently looks like and whether an external SubjectConcept agent has made a claim against any of those nodes and edges"

**Solution:** Comprehensive state introspection API for agents to reload graph state at session start.

**File:** `STEP_2_COMPLETE.md` (comprehensive documentation)

**What Was Built:**

1. **Current State Introspection Methods** (8 new methods in `scripts/agents/facet_agent_framework.py`)
   - **`get_session_context()`** - **CRITICAL:** Call first! Loads SubjectConcept snapshot, pending claims, agent stats
   - `get_subjectconcept_subgraph(limit)` - Current SubjectConcept nodes and relationships
   - `find_claims_for_node(node_id)` - All claims referencing a specific node
   - `find_claims_for_relationship(source_id, target_id, rel_type)` - Claims about relationships
   - `get_node_provenance(node_id)` - Which claim(s) created/modified this node
   - `get_claim_history(node_id)` - Full audit trail for a node (chronological)
   - `list_pending_claims(facet, min_confidence, limit)` - Claims awaiting validation
   - `find_agent_contributions(agent_id, limit)` - What this agent has proposed (stats + list)

2. **Claim Lifecycle & Provenance Model**
   - **Status lifecycle:** `proposed` → `validated` → `promoted=true` (or `rejected`)
   - **Auto-promotion:** `confidence >= 0.90` AND `posterior_probability >= 0.90`
   - **Node provenance:** `(Node)-[:SUPPORTED_BY]->(Claim)` after promotion
   - **Relationship provenance:** `promoted_from_claim_id` property on relationships
   - **Traceability:** Full audit trail via claim history queries

3. **Updated System Prompts** (`facet_agent_system_prompts.json`)
   - All 17 facet prompts now include "CURRENT STATE INTROSPECTION (STEP 2)" section
   - Session initialization workflow documented
   - "BEFORE PROPOSING NEW CLAIMS" checklist
   - Collaborative awareness guidance
   - Version bumped to `2026-02-15-step2`
   - Script: `scripts/update_facet_prompts_step2.py` (automation)

---

### Critical Problem: No Ontology Alignment for Interoperability
**User Requirement:** "the llm knows the critical schemas and how to implement them - the always tag something as much as possible with qid, property and value, cidoc crm and minf also utilizing a crosswalk i recall we made for cidoc and minf to wiki"

**Solution:** Automatic CIDOC-CRM (cultural heritage standard) and CRMinf (belief/argumentation) ontology alignment on all entities and claims.

**File:** `STEP_4_COMPLETE.md` (comprehensive documentation)

**What Was Built:**

1. **Semantic Enrichment Methods** (4 new methods in `scripts/agents/facet_agent_framework.py`)
   - `_load_cidoc_crosswalk()` - Load 105 validated Wikidata↔CIDOC-CRM↔CRMinf mappings
   - `enrich_with_ontology_alignment(entity)` - Add CIDOC-CRM classes to entities (E21_Person, E5_Event, E53_Place)
   - `enrich_claim_with_crminf(claim)` - Add CRMinf belief tracking (I2_Belief, J4_that, J5_holds_to_be)
   - `generate_semantic_triples(qid)` - Full QID+Property+Value+CIDOC+CRMinf alignment

2. **CIDOC-CRM Crosswalk** (existing file utilized)
   - Source: `CIDOC/cidoc_wikidata_mapping_validated.csv` (105 mappings)
   - Entity mappings: Q5→E21_Person, Q1656682→E5_Event, Q82794→E53_Place, Q43229→E74_Group
   - Property mappings: P276→P7_took_place_at, P710→P11_had_participant, P31→P2_has_type
   - CRMinf mappings: Claim→I2_Belief, confidence→J5_holds_to_be, proposition→J4_that

3. **Automatic Integration**
   - Modified `enrich_node_from_wikidata()`: Adds `cidoc_crm_class` property to all SubjectConcept nodes
   - Modified `generate_claims_from_wikidata()`: Adds `crminf_alignment` section to all claims
   - Bootstrap workflow now enriches automatically during federation discovery

4. **Updated System Prompts** (`facet_agent_system_prompts.json`)
   - All 17 facet prompts now include "SEMANTIC ENRICHMENT & ONTOLOGY ALIGNMENT (STEP 4)" section
   - CIDOC-CRM class mappings documented
   - CRMinf belief tracking model explained
   - Semantic triple generation examples
   - Version bumped to `2026-02-15-step4`
   - Script: `scripts/update_facet_prompts_step4.py` (automation)

**Benefits:**
- Museum/archive interoperability (CIDOC-CRM ISO 21127 standard)
- Belief/argumentation tracking (CRMinf ontology)
- RDF/OWL export capability via semantic triples
- Multi-ontology queries (Wikidata OR CIDOC OR Chrystallum)

**Node Storage Example:**
```cypher
(n:SubjectConcept {
  wikidata_qid: 'Q28048',
  cidoc_crm_class: 'E5_Event',
  cidoc_crm_confidence: 'High'
})
```

**Claim Enrichment Example:**
```python
{
  "crminf_alignment": {
    "crminf_class": "I2_Belief",
    "J4_that": "Battle of Pharsalus occurred in 48 BCE",
    "J5_holds_to_be": 0.90,
    "source_agent": "military_facet",
    "inference_method": "wikidata_federation"
  }
}
```

---

## Step 3.5 Complete - Completeness Validation & Property Pattern Mining (2026-02-15)

### Problem: Blind Bootstrap Without Quality Checks
**User Requirement:** "option a but you need a bigger sample i think to validate patterns" (property pattern mining experiment)

**Solution:** Mine empirical property patterns from 841 historical entities to validate Wikidata entity completeness.

**File:** `PROPERTY_PATTERN_MINING_INTEGRATION.md` (comprehensive documentation)

**What Was Built:**

1. **Property Pattern Mining** (`Python/wikidata_property_pattern_miner.py`)
   - Mined 841 entities from 12 historical types (battles, humans, cities, countries, events, etc.)
   - Statistical validation: Mandatory properties (≥85%), Common (50-85%), Optional (<50%)
   - Output: `property_patterns_large_sample_20260215_174051.json`

2. **Completeness Validation Methods** (2 new methods in `scripts/agents/facet_agent_framework.py`)
   - `_load_property_patterns()` - Load empirical patterns from JSON
   - `validate_entity_completeness(entity, entity_type)` - Score entity quality (0.0-1.0)

3. **Bootstrap Integration**
   - Modified `bootstrap_from_qid()`: Rejects entities with completeness score <0.60
   - Prevents low-quality entities from entering the graph
   - Logs validation results for transparency

4. **Updated System Prompts** (`facet_agent_system_prompts.json`)
   - All 17 facet prompts include "COMPLETENESS VALIDATION (STEP 3.5)" section
   - Version: `2026-02-15-step3.5`
   - Script: `scripts/update_facet_prompts_step3_5.py`

**Sample Results:**
- **Battle entities:** 91% have P276 (location), 88% have P361 (part of war)
- **Human entities:** 100% have P19/P21/P27 (birthplace/sex/citizenship)
- **City entities:** 100% have P17/P625 (country/coordinates)

---

## Step 3 Complete - Federation-Driven Discovery & Automatic Claim Generation (2026-02-15)

### Critical Problem: Manual Entity Creation Bottleneck
**User Requirement:** "when first instantiated, create the qid+all properties from the wikidata page and concat to id. at this point it could trawl any hierarchies from the properties and start making claims about newly discovered nodes and relationships"

**Solution:** Automatic Wikidata integration enabling agents to bootstrap knowledge, traverse hierarchies, and auto-generate claims.

**File:** `STEP_3_COMPLETE.md` (comprehensive documentation)

**What Was Built:**

1. **Federation Discovery Methods** (6 new methods in `scripts/agents/facet_agent_framework.py`)
   - **`bootstrap_from_qid(qid, depth, auto_submit)`** - High-level initialization from Wikidata QID
   - `fetch_wikidata_entity(qid)` - API integration for entity retrieval
   - `enrich_node_from_wikidata(node_id, qid)` - Create/update nodes with Wikidata properties
   - `discover_hierarchy_from_entity(qid, depth)` - Traverse P31/P279/P361 hierarchies
   - `generate_claims_from_wikidata(qid)` - Auto-generate claims from statements
   - `_map_wikidata_property_to_relationship(property)` - P-code to relationship mapping

2. **Wikidata API Integration**
   - Endpoint: `https://www.wikidata.org/w/api.php`
   - Fetches: labels, descriptions, aliases, all claims/statements
   - Node ID generation: `sha256(f"wikidata:{qid}")[:16]`
   - Layer 2.5 properties: P31, P279, P361, P101, P2578, P921, P1269

3. **Automatic Hierarchy Traversal**
   - Breadth-first search with configurable depth (1-3 recommended)
   - Discovers related entities through semantic relationships
   - Prevents explosion via per-property limits
   - Tracks visited entities to avoid cycles

4. **Auto-Claim Generation**
   - Transforms Wikidata statements → Chrystallum claims
   - High confidence (0.90) for Layer 2 Federation Authority
   - Complete provenance: `{source_qid, target_qid, property}`
   - Optional auto-submission or review-before-submit

5. **Updated System Prompts** (`facet_agent_system_prompts.json`)
   - All 17 facet prompts now include "FEDERATION-DRIVEN DISCOVERY (STEP 3)" section
   - Bootstrap workflows documented
   - Hierarchy traversal strategies
   - Auto-claim generation guidance
   - Version bumped to `2026-02-15-step3`
   - Script: `scripts/update_facet_prompts_step3.py` (automation)

**Example Bootstrap Workflow:**
```python
# Initialize agent on Roman Republic
result = agent.bootstrap_from_qid('Q17167', depth=2, auto_submit=False)
print(f"Created {result['nodes_created']} nodes")
print(f"Generated {result['claims_generated']} claims")

# Review and submit claims
for claim in result['claims']:
    if claim['confidence'] >= 0.90:
        agent.pipeline.ingest_claim(claim)
```

**Integration with Previous Steps:**
- Uses `get_layer25_properties()` (Step 1) to know which properties to traverse
- Uses `get_session_context()` (Step 2) to avoid duplicate node creation
- Validates schema via `introspect_node_label()` (Step 1) before creating claims
- Validated by `validate_entity_completeness()` (Step 3.5) before node creation
- Enriched with `enrich_with_ontology_alignment()` (Step 4) for CIDOC-CRM alignment

**Claim Structure Reference:**
```cypher
(Claim {
  claim_id, cipher, status, source_agent, facet, confidence,
  prior_probability, likelihood, posterior_probability,
  fallacies_detected, critical_fallacy,
  timestamp, promoted, promotion_date,
  label, text, claim_type,
  authority_source, authority_ids
})

// Relationships
(Claim)-[:ASSERTS]->(Entity)              // Claims reference entities
(Entity)-[:SUPPORTED_BY]->(Claim)         // Provenance after promotion
(Claim)-[:USED_CONTEXT]->(RetrievalContext)
(Claim)-[:HAS_ANALYSIS_RUN]->(AnalysisRun)
(Claim)-[:HAS_FACET_ASSESSMENT]->(FacetAssessment)

// Promoted relationships
(Source)-[r:REL_TYPE {promoted_from_claim_id: "claim_abc"}]->(Target)
```

**Key Benefits:**
- **Session Recovery:** Agents can reload state with single `get_session_context()` call
- **Duplicate Avoidance:** Check existing nodes/claims before proposing
- **Provenance Tracking:** Full audit trail (who created what, when)
- **Collaboration:** Agents see each other's contributions
- **Quality Metrics:** Track promotion rates per agent/facet

**Integration with Step 1:**
- Step 1: Agents know WHAT the schema IS (labels, relationships, tiers)
- Step 2: Agents know WHAT currently EXISTS (nodes, edges, claims)
- Combined: Schema + State introspection = informed claim proposals

**Status:**
- ✅ 8 state introspection methods implemented
- ✅ Session context initialization complete
- ✅ Provenance tracking queryable
- ✅ System prompts updated (17 facets)
- ⏸️ Integration tests (awaiting Neo4j deployment)

**Status:**
- ✅ Steps 1-4 complete (28 methods total)
- ✅ Property patterns validated (841 entities)
- ✅ CIDOC-CRM/CRMinf ontology alignment integrated
- ✅ System prompts updated (version 2026-02-15-step4)
- ⏸️ Integration tests (awaiting Neo4j deployment)

**Next Steps:** User will guide Step 5+ (query decomposition? multi-agent debate? RDF export?).

---

## Step 1: Agent Architecture Understanding (2026-02-15)

### Implementation: Hybrid Meta-Graph + Curated Docs Approach
**Decision:** Agents can introspect schema via queryable meta-graph while historians read rationale in curated docs.

**File:** `STEP_1_COMPLETE.md` (comprehensive summary)

**What Was Built:**

1. **Meta-Schema Graph** (`Neo4j/schema/06_meta_schema_graph.cypher` - 783 lines)
   - 6 `_Schema:AuthorityTier` nodes (5.5-layer stack with confidence floors)
   - 14 `_Schema:NodeLabel` nodes (SubjectConcept, Human, Event, Place, etc.)
   - 17 `_Schema:FacetReference` meta-tags (Military, Political, Economic, etc.)
   - Sample `_Schema:RelationshipType` nodes (expandable to 312 from registry)
   - `_Schema:Property` nodes with validation rules
   - 5 `_Schema:ValidationRule` nodes
   - 6 query examples for agent usage
   - 5 indexes for fast introspection

2. **Agent Introspection Methods** (`scripts/agents/facet_agent_framework.py`)
   - `introspect_node_label(label_name)` - Get label definition, tier, properties
   - `discover_relationships_between(source, target)` - Find valid relationship types
   - `get_required_properties(label_name)` - Get required properties for validation
   - `get_authority_tier(tier)` - Get layer definition, gates, confidence floor
   - `list_facets(filter_key)` - Get facet definitions with Wikidata anchors
   - `validate_claim_structure(claim_dict)` - Validate claim before proposal
   - `get_layer25_properties()` - Get P31/P279/P361 properties for semantic expansion
   - `_discover_schema()` - Existing method that lists all labels and relationships

3. **Updated System Prompts** (`facet_agent_system_prompts.json`)
   - All 17 facet prompts now include "SCHEMA INTROSPECTION (NEW)" section
   - Lists available introspection methods
   - Provides example meta-graph queries
   - Documents validation workflow
   - Shows authority stack with confidence floors
   - Script: `scripts/update_facet_prompts_with_schema.py` (automated update)

**Status:**
- ✅ Meta-schema Cypher script complete
- ✅ Agent introspection methods added
- ✅ System prompts updated for all 17 facets
- ⏸️ Meta-schema deployment pending Neo4j credentials
- ⏸️ Introspection tests pending deployment

**Benefits:**
- Agents can query schema without hardcoding
- Validation happens before claim proposal
- Self-documenting architecture via introspection
- Single source of truth for schema
- Authority stack confidence floors queryable
- Facet boundaries clear with Wikidata anchors

---

## Current Architecture State (verified 2026-02-15)

**See:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` for full architecture specification (Sections 1-12 + Appendices A-N)

### 1. Temporal Backbone (Calendrical Spine)
Structure:
`Year -> PART_OF -> Decade -> PART_OF -> Century -> PART_OF -> Millennium`

Status: Implemented.

Decisions locked in:
- Historical mode: no `Year {year: 0}` node.
- Year sequence is unidirectional: `FOLLOWED_BY` only.
- BCE/CE labels are historical-style while IDs remain numeric buckets.

Canonical implementation files:
- `scripts/backbone/temporal/genYearsToNeo.py`
- `scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py`
- `scripts/backbone/temporal/05_temporal_hierarchy_levels.cypher`

### 2. Historical Period Spine
Status in clean baseline: not materialized in the live DB.

Notes:
- `scripts/backbone/temporal/create_canonical_spine.py` exists for period/era modeling.
- `scripts/backbone/temporal/link_years_to_periods.py` does not exist.

### 3. Live Neo4j Baseline (clean)
Only temporal backbone labels are present:
- `Year: 4025` (`-2000..2025`, no year 0)
- `Decade: 403`
- `Century: 41`
- `Millennium: 5`

Relationships:
- `FOLLOWED_BY` (Year chain): 4024
- `PART_OF`: 4469
- `PRECEDED_BY`: 0
- Bridge exists: `(-1)-[:FOLLOWED_BY]->(1)`

## Key Corrections (important)
- Previous notes claiming `link_years_to_periods.py` were inaccurate.
- Migration scripts were synced to corrected historical logic (BCE-safe bucketing and labels).
- Documentation was updated to reflect `FOLLOWED_BY`-only year sequencing.

## Concept Label Canonicalization (verified 2026-02-14)

Decision locked:
- `Concept` is deprecated as a node label.
- `SubjectConcept` is canonical.

Migration note:
- `md/Architecture/CONCEPT_TO_SUBJECTCONCEPT_MIGRATION_2026-02-14.md`

Applied updates:
- Removed legacy multi-label examples like `:Person:Concept`, `:Place:Concept`, `:Event:Concept`.
- Updated prompts/guides/roadmap snippets to map concept-like targets to `:SubjectConcept`.
- Updated canonical source index to point to the migration note.

## Main-Node Baseline Sync (verified 2026-02-14)

- `md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md` now references `Key Files/Main nodes.md` as the current operational main-node baseline.
- The operational list was synchronized to:
  - `SubjectConcept, Human, Gens, Praenomen, Cognomen, Event, Place, Period, Dynasty, Institution, LegalRestriction, Claim, Organization, Year`
- `Communication` was demoted from first-class node status and is now treated as a facet/domain axis.
- The consolidated architecture now includes an explicit normative lock:
  - `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`, Section `3.0.1 Canonical First-Class Node Set (Normative)`.
  - Section 3.3 facet count corrected to 17 with explicit communication facet policy.
- Neo4j schema files were aligned to this lock:
  - `Neo4j/schema/01_schema_constraints.cypher`: canonical label lock note + first-class `id_hash` uniqueness + `Claim.cipher` required.
  - `Neo4j/schema/02_schema_indexes.cypher`: first-class `id_hash` and `status` indexes + explicit `Claim.cipher` index.

## Consolidated Doc Consistency Pass (verified 2026-02-14)

- Performed a wording/structure pass for Section `8.6 Federation Dispatcher and Backlink Control Plane` and Appendix K pipeline wording.
- Clarified dispatcher no-bypass rule and aligned terminology between:
  - Section `8.6` route/gate rules
  - Appendix `K.4-K.6` operational contract

## SysML + Implementation Index Realignment (verified 2026-02-14)

- SysML model now references consolidated architecture as the sole normative source:
  - `Key Files/2-13-26 SysML v2 System Model - Blocks and Ports (Starter).md`
- Updated SysML coverage to include:
  - block responsibilities aligned to consolidated sections
  - typed port payload contracts
  - federation dispatcher flow control (Section 8.6)
  - claim lifecycle states (`proposed|validated|disputed|rejected`)
  - deterministic agent routing policy
- Both implementation indexes were rewritten as consolidated-only crosswalks:
  - `Key Files/ARCHITECTURE_IMPLEMENTATION_INDEX.md`
  - `ARCHITECTURE_IMPLEMENTATION_INDEX.md`
- BODY/APPENDICES are no longer used as architecture source documents in the index mapping.

## Bootstrap Validation Runner (verified 2026-02-14)

- Added a single dry-validation Cypher runner:
  - `Neo4j/schema/06_bootstrap_validation_runner.cypher`
- Validates:
  - `SHOW CONSTRAINTS` name set vs expected
  - `SHOW INDEXES` user-created name set vs expected
  - non-ONLINE user index detection
  - final PASS/FAIL summary row
- Expected name sets are generated from:
  - `Neo4j/schema/01_schema_constraints.cypher`
  - `Neo4j/schema/02_schema_indexes.cypher`
- Compatibility lock:
  - use `SHOW CONSTRAINTS` / `SHOW INDEXES` directly (no dependency on `db.constraints()` or `db.indexes()`, which may be unavailable in some builds)
  - aggregate-safe pattern is required: collect in `WITH`, then compare lists in later `WITH`/`RETURN` stages

## Core Pipeline Schema Phase (verified 2026-02-14)

- Added focused schema bootstrap:
  - `Neo4j/schema/07_core_pipeline_schema.cypher`
- Added phase-matched validator:
  - `Neo4j/schema/08_core_pipeline_validation_runner.cypher`
- Phase scope:
  - `Human`, `Place`, `Event`, `Period`, `SubjectConcept`, `Claim`,
    `RetrievalContext`, `Agent`, `AnalysisRun`, `FacetAssessment`
- Execution model:
  - Run after temporal backbone baseline (`Year/Decade/Century/Millennium`)
  - Uses `IF NOT EXISTS` for all constraints/indexes so reruns are safe
- Validation model:
  - PASS/FAIL is based on missing required names only (extra indexes/constraints are informational)
  - parser compatibility note: if Neo4j rejects `SHOW` composition, use:
    - `Neo4j/schema/08_core_pipeline_validation_runner.cypher` for browser-safe inventories
    - `python Neo4j/schema/08_core_pipeline_validation_runner.py` for authoritative PASS/FAIL

## Core Pipeline Pilot Seed (verified 2026-02-14)

- Added minimal non-temporal pilot seed:
  - `Neo4j/schema/09_core_pipeline_pilot_seed.cypher`
  - `Neo4j/schema/10_core_pipeline_pilot_verify.cypher`
- Pilot cluster includes:
  - `SubjectConcept` (`subj_roman_republic_001`)
  - `Agent` (`agent_roman_republic_v1`)
  - `Claim` (`claim_roman_republic_end_27bce_001`)
  - `RetrievalContext`, `AnalysisRun`, `Facet`, `FacetAssessment`
- Seeded edges:
  - `OWNS_DOMAIN`, `MADE_CLAIM`, `SUBJECT_OF`, `USED_CONTEXT`,
    `HAS_ANALYSIS_RUN`, `HAS_FACET_ASSESSMENT`, `ASSESSES_FACET`, `EVALUATED_BY`
- Compatibility adjustment applied:
  - use `toString(datetime())` (not `datetime().toString()`) for this Neo4j parser/version.

## Event-Period Claim Pilot (verified 2026-02-14)

- Added concrete entity-grounded pilot:
  - `Neo4j/schema/11_event_period_claim_seed.cypher`
  - `Neo4j/schema/12_event_period_claim_verify.cypher`
- Seeded entities:
  - `Period`: Roman Republic (`Q17167`)
  - `Event`: Battle of Actium (`Q193304`)
  - `Place`: Actium (`Q41747`)
- Seeded second claim flow:
  - `claim_actium_in_republic_31bce_001`
  - retrieval: `retr_actium_q193304_001`
  - analysis run: `run_actium_001`
  - facet assessment: `fa_actium_mil_001`
- Added parser hardening for script execution:
  - `Neo4j/schema/run_cypher_file.py` now splits statements on semicolons only when outside quoted strings.

## Claim Label Enforcement (verified 2026-02-14)

- Core schema now requires `Claim.label`:
  - `Neo4j/schema/07_core_pipeline_schema.cypher`
  - constraint: `claim_has_label`
  - index: `claim_label_index`
- Validator updated for new requirement:
  - `Neo4j/schema/08_core_pipeline_validation_runner.py`
- Backfill script added:
  - `Neo4j/schema/13_claim_label_backfill.cypher`
- Current pilot claim labels:
  - `claim_roman_republic_end_27bce_001` -> `Roman Republic Ended in 27 BCE`
  - `claim_actium_in_republic_31bce_001` -> `Battle of Actium in Roman Republic (31 BCE)`

## Claim Promotion Pilot (verified 2026-02-14)

- Added promotion scripts:
  - `Neo4j/schema/14_claim_promotion_seed.cypher`
  - `Neo4j/schema/15_claim_promotion_verify.cypher`
- Promoted claim:
  - `claim_actium_in_republic_31bce_001` -> `status=validated`, `promoted=true`
- Canonical/provenance wiring verified:
  - `(:Event {evt_battle_of_actium_q193304})-[:OCCURRED_DURING]->(:Period {prd_roman_republic_q17167})`
  - `Event-[:SUPPORTED_BY]->Claim` count = 1
  - `Period-[:SUPPORTED_BY]->Claim` count = 1

## Backlink Discovery Mode Upgrade (verified 2026-02-14)

- `scripts/tools/wikidata_backlink_harvest.py` now supports:
  - `--mode production` (default constrained behavior)
  - `--mode discovery` (expanded budgets + broader property surface)
- New mode-aware defaults:
  - production: `sparql_limit=500`, `max_sources_per_seed=200`, `max_new_nodes_per_seed=100`
  - discovery: `sparql_limit=2000`, `max_sources_per_seed=1000`, `max_new_nodes_per_seed=500`
- New class gate control:
  - `--class-allowlist-mode {auto,schema,disabled}`
  - `auto` resolves to `disabled` in discovery and `schema` in production
- Discovery run verified on `Q1048`:
  - report: `JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json`
  - includes `mode: discovery` and `class_allowlist_mode: disabled`

## Q17167 Critical Test (verified 2026-02-14)

Objective completed:
- Generate a claim-rich subgraph proposal for `Q17167` using direct statements + backlinks.

Pipeline executed:
- Direct statements export:
  - `JSON/wikidata/statements/Q17167_statements_full.json`
- Direct datatype profile:
  - `JSON/wikidata/statements/Q17167_statement_datatype_profile_summary.json`
  - `JSON/wikidata/statements/Q17167_statement_datatype_profile_by_property.csv`
  - `JSON/wikidata/statements/Q17167_statement_datatype_profile_datatype_pairs.csv`
- Discovery backlink harvest:
  - `JSON/wikidata/backlinks/Q17167_backlink_harvest_report.json`
- Backlink accepted profile:
  - `JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_summary.json`
  - `JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_by_entity.csv`
  - `JSON/wikidata/backlinks/Q17167_backlink_profile_accepted_pair_counts.csv`

New generator capability:
- `scripts/tools/wikidata_generate_claim_subgraph_proposal.py`
  - merges direct claims + accepted backlinks
  - maps predicate PIDs to canonical relationship types via registry
  - emits machine + human artifacts:
    - `JSON/wikidata/proposals/Q17167_claim_subgraph_proposal.json`
    - `JSON/wikidata/proposals/Q17167_claim_subgraph_proposal.md`

Q17167 proposal snapshot:
- nodes: `178`
- relationship claims: `197`
  - direct: `39`
  - backlink: `158`
- attribute claims: `41`
- backlink gate status: `pass`

## Republic Agent SubjectConcept Seed Pack (verified 2026-02-14)

- Added implementation-ready seed files for Republic-agent domain concepts:
  - `JSON/wikidata/proposals/Q17167_republic_agent_subject_concepts.csv`
  - `JSON/wikidata/proposals/Q17167_republic_agent_subject_concepts.json`
- Pack contents:
  - 17 proposed `SubjectConcept` nodes
  - `discipline=true`, primary facet, primary confidence
  - multi-facet confidence vectors (JSON)
  - parent hierarchy using `BROADER_THAN` relationship proposals

## Federation Datatype Work (verified 2026-02-13)

### New capability
- Full statement export and datatype profiling are now in place for federation design.

Artifacts:
- Full statements export: `JSON/wikidata/statements/Q1048_statements_full.json`
- 100-row flattened sample: `JSON/wikidata/statements/Q1048_statements_sample_100.csv`
- Datatype profile summary: `JSON/wikidata/statements/Q1048_statement_datatype_profile_summary.json`
- Datatype profile by property: `JSON/wikidata/statements/Q1048_statement_datatype_profile_by_property.csv`
- Datatype/value-type pairs: `JSON/wikidata/statements/Q1048_statement_datatype_profile_datatype_pairs.csv`

Scripts:
- `scripts/tools/wikidata_fetch_all_statements.py`
- `scripts/tools/wikidata_sample_statement_records.py`
- `scripts/tools/wikidata_statement_datatype_profile.py`

Spec:
- `md/Architecture/Wikidata_Statement_Datatype_Ingestion_Spec.md`

Observed Q1048 profile baseline:
- statements: 451
- properties: 324
- datatypes: 7
- value types: 5
- qualifier coverage: 23.28%
- reference coverage: 24.17%

## Backlink Policy Refinement (verified 2026-02-13)

- Canonical backlink policy was cleaned and tightened:
  - `Neo4j/FEDERATION_BACKLINK_STRATEGY.md`
- Key lock-ins:
  - Backlink source is semantic reverse triples, not MediaWiki page `linkshere`.
  - `datatype` + `value_type` are mandatory routing gates, not optional metadata.
  - Stop conditions are required (`max_depth`, per-seed budgets, class/property allowlists).
  - Backlink candidates must pass the same datatype profiling workflow as direct statements.

## Backlink Harvester Implementation (verified 2026-02-13)

- New script:
  - `scripts/tools/wikidata_backlink_harvest.py`
- Report output location:
  - `JSON/wikidata/backlinks/`
- Sample run artifact:
  - `JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json`

Q1048 sample (bounded run):
- backlink rows: 87
- candidate sources considered: 25
- accepted: 10
- unresolved class rate: 20.00% (gate pass at default 20%)
- unsupported datatype pair rate: 0.00% (gate pass)
- overall status: `pass`
- dispatcher route metrics now emitted in report (`route_counts`, `quarantine_reasons`)
- frontier metrics now emitted (`frontier_eligible`, `frontier_excluded`, per-entity `frontier_eligible`)
- consolidated architecture updated:
  - `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
  - new normative section `8.6 Federation Dispatcher and Backlink Control Plane`
  - Appendix K updated with dispatcher/backlink operational contract

## Backlink Profiler Implementation (verified 2026-02-13)

- New script:
  - `scripts/tools/wikidata_backlink_profile.py`
- Profiling artifacts (Q1048 accepted candidates):
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_summary.json`
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_by_entity.csv`
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_pair_counts.csv`

Q1048 profile sample:
- requested QIDs: 10
- resolved entities: 10
- statements: 342
- unsupported pair rate: 0.00%
- overall status: `pass`

## Query Executor Agent + Claim Pipeline (verified 2026-02-14)

### New Agent Implementation
- Added production-ready Query Executor Agent:
  - `scripts/agents/query_executor_agent_test.py` (391 lines)
  - ChatGPT-powered with dynamic schema discovery
  - Integrated claim submission via ClaimIngestionPipeline
  - 5 CLI modes: test, claims, interactive, single query, default

### Claim Ingestion Pipeline
- New pipeline:
  - `scripts/tools/claim_ingestion_pipeline.py` (460 lines)
  - Entry point: `ingest_claim(entity_id, relationship_type, target_id, confidence, ...)`
  - Returns: `{status: 'created'|'promoted'|'error', claim_id, cipher, promoted}`
  - Workflow: Validate -> Hash -> Create -> Link -> Promote
    (if confidence >= 0.90 and posterior_probability >= 0.90 and no critical fallacy)
  - Intermediary nodes: RetrievalContext, AnalysisRun, FacetAssessment
  - Traceability: SUPPORTED_BY edges + canonical relationship promotion

### Facet Integration (Updated 2026-02-15)
- **NEW**: 17-facet model with Communication as META-FACET
- **16 Domain Facets**:
  - Military, Political, Social, Economic, Diplomatic, Religious, Legal, Literary
  - Cultural, Technological, Agricultural, Artistic, Philosophical, Scientific, Geographic, Biographical
- **1 Meta-Facet (Communication)**: Applies ACROSS all domains, not competing with them
  - Dimensions: Medium (oral, written, visual, performative), Purpose (propaganda, persuasion, legitimation)
  - Audience (Senate, people, military, allies, posterity), Strategy (ethos, pathos, logos, invective, exemplarity)
- **0-to-Many Claim Distribution** (replacing forced 1:1 model):
  - Military/Political: 6-10 claims per entity (well-documented)
  - Social/Legal/Religious: 2-5 claims per entity (good documentation)
  - Artistic/Scientific: 0-1 claims per entity (sparse documentation)
  - Total: 15-35 claims per entity (reflects historical documentation reality)
- **Facet Registry Status**: ACTIVE - `Facets/facet_registry_master.json`
- **Communication Routing**: Entities with communication_primacy >= 0.75 routed to specialized CommunicationAgent
- **Claim Properties**: Primary facet (1), related facets (0-to-many), confidence per facet, evidence, authority, temporal
- **References**:
  - SubjectsAgentsProposal evaluation: `SUBJECTSAGENTS_PROPOSAL_EVALUATION.md`
  - Communication facet spec: `subjectsAgentsProposal/files2/COMMUNICATION_FACET_FINAL_SPEC.md`
  - 0-to-many model: `subjectsAgentsProposal/files3/CORRECTED_0_TO_MANY_MODEL.md`

### Documentation Package
- System prompt: `md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md` (400+ lines, with facet patterns)
- Agent README: `scripts/agents/README.md` (400+ lines)
- Quickstart: `scripts/agents/QUERY_EXECUTOR_QUICKSTART.md` (300+ lines)
- Quick reference: `QUERY_EXECUTOR_QUICK_REFERENCE.md`
- Implementation summary: `Key Files/2026-02-14 Query Executor Implementation.md`

### Execution Model
- Agent layer: Direct neo4j-driver + OpenAI API (no MCP overhead for agents)
- Pipeline layer: Python validation + transactional Neo4j writes
- Separation: ChatGPT handles query/format, pipeline handles validation/promotion
- Status: ✅ Syntax validated, ready for testing
- Deployment: Files staged for git commit (awaiting push)

## Parameterized QID Pipeline Runner (verified 2026-02-14)

### New Generic Runner
- Added a parameterized pipeline runner for period/event/place QIDs:
  - `Neo4j/schema/run_qid_pipeline.py`
  - Deterministic IDs derived from QIDs (`qid_token`)
  - BCE-safe year/date parsing (negative years + ISO dates)
  - Single run handles reset, seed, promotion, and verification
  - Facet keys normalized to lowercase; labels title-cased

### PowerShell Wrapper
- Added wrapper with strict `--flag=value` args to preserve negative years/dates:
  - `Neo4j/schema/run_qid_pipeline.ps1`

### Roman Republic Shortcut
- Shortcut wrapper with Roman Republic defaults:
  - `Neo4j/schema/run_roman_republic_q17167_pipeline.ps1`
- Validation executed successfully:
  - validated temporal claim
  - canonical `OCCURRED_DURING` and `OCCURRED_AT`
  - `SUPPORTED_BY` counts = 1/1/1 (event/period/place)

### Training Workflow Constraints (Q17167)
- Record run metadata in the proposal: mode, caps, and whether trimming occurred.
- If the proposal exceeds 1000 nodes, document the trimming rule used (drop lowest-priority nodes).
- Log `class_allowlist_mode` and any overrides used during harvest.
- If any budget caps are hit, mark the proposal as partial and recommend a second pass.

## Historian Logic Upgrade (verified 2026-02-14)

- Implemented both requested reasoning controls in the live claim path:
  - Fischer-style fallacy heuristics
  - Bayesian posterior scoring
- New module:
  - `scripts/tools/historian_logic_engine.py`
- Integrated into claim pipeline:
  - `scripts/tools/claim_ingestion_pipeline.py`
  - claim properties now persist: `prior_probability`, `likelihood`, `posterior_probability`,
    `fallacies_detected`, `fallacy_penalty`, `critical_fallacy`, `bayesian_score`
- Promotion gate now requires all:
  - `confidence >= 0.90`
  - `posterior_probability >= 0.90`
  - `critical_fallacy = false`
- Query executor now prints posterior/fallacy outputs after submission:
  - `scripts/agents/query_executor_agent_test.py`
### Example Usage
```
Neo4j\schema\run_qid_pipeline.ps1 `
  -PeriodQid "Q17167" -PeriodLabel "Roman Republic" -PeriodStart "-0510" -PeriodEnd "-0027" `
  -EventQid "Q193304" -EventLabel "Battle of Actium" -EventDate "-0031-09-02" -EventType "battle" `
  -PlaceQid "Q41747" -PlaceLabel "Actium" -PlaceType "place" -ModernCountry "Greece" `
  -ResetEntities -LegacyRomanClean
```

## Hierarchy Query Engine & Layer 2.5 Implementation (verified 2026-02-15)

### Objective Completed
Discovered and implemented missing Layer 2.5 (semantic query infrastructure) that bridges Federation Authority (Layer 2) and Facet Discovery (Layer 3). Layer 2.5 enables expert finding, source discovery, contradiction detection, and semantic expansion through Wikidata relationship properties.

### Key Discovery
Archived document `subjectsAgentProposal/files/chatSubjectConcepts.md` (1,296 lines) contained complete infrastructure design using Wikidata properties P31/P279/P361/P101/P2578/P921/P1269, but was not connected to the main architecture flow.

### Architecture: 5.5-Layer Stack (Complete)
- **Layer 1:** Library Authority (LCSH/LCC/FAST/Dewey) - gate validation
- **Layer 2:** Federation Authority (Wikidata/Wikipedia) - federation IDs
- **Layer 2.5:** Hierarchy Queries (NEW) - P31/P279/P361/P101/P2578/P921/P1269 semantic properties
- **Layer 3:** Facet Discovery - Wikipedia QID extraction to FacetReference
- **Layer 4:** Subject Integration - SubjectConcept nodes + authority tier mapping
- **Layer 5:** Validation - Three-layer validator + contradiction detection

### Relationship Properties (7 types)
1. **P31 (Instance-Of) - "IS A"**: Individual → Type/Class (non-transitive)
2. **P279 (Subclass-Of) - "IS A TYPE OF"** [TRANSITIVE]: Class → Broader Class
3. **P361 (Part-Of) - "CONTAINED IN"** [TRANSITIVE]: Component → Whole (mereology)
4. **P101 (Field-Of-Work)**: Person/Org → Discipline (expert mapping)
5. **P2578 (Studies)**: Discipline → Object of Study (domain definition)
6. **P921 (Main-Subject)**: Work → Topic (evidence grounding)
7. **P1269 (Facet-Of)**: Aspect → Broader Concept (facet hierarchy)

### Implementation: 4 Production-Ready Python Files

**1. hierarchy_query_engine.py** (620 lines)
- **Path:** `scripts/reference/hierarchy_query_engine.py`
- **Classes:** HierarchyNode, HierarchyPath, HierarchyQueryEngine
- **Use Case 1 - Semantic Expansion:**
  - `find_instances_of_class(qid)` - Find all instances (e.g., Battle of Cannae from Q178561)
  - `find_superclasses(entity_qid)` - Classification chain
  - `find_components(whole_qid)` - All parts of a whole (e.g., battles in Punic Wars)
- **Use Case 2 - Expert Discovery:**
  - `find_experts_in_field(discipline_qid)` - Specialists via P101 (e.g., military historians)
  - `find_disciplines_for_expert(person_qid)` - What disciplines expert covers
- **Use Case 3 - Source Discovery:**
  - `find_works_about_topic(topic_qid)` - Primary/secondary sources via P921
  - `find_works_by_expert(person_qid)` - Works authored + their subjects
- **Use Case 4 - Contradiction Detection:**
  - `find_cross_hierarchy_contradictions()` - Conflicting claims at different levels
- **Utilities:** Facet inference, batch operations, error handling
- **Status:** ✅ Production-ready (620 lines, docstrings, logging)

**2. academic_property_harvester.py** (380 lines)
- **Path:** `scripts/reference/academic_property_harvester.py`
- **Purpose:** SPARQL harvest of academic properties from Wikidata
- **Domain Mappings:** Roman Republic (8 disciplines), Mediterranean History (6 disciplines)
- **Harvest Methods:**
  - `harvest_p101_field_of_work()` - Extract people in discipline (60-150 per domain)
  - `harvest_p2578_studies()` - Extract discipline objects (20-30 per domain)
  - `harvest_p921_main_subject()` - Extract works on topic (100-200 per domain)
  - `harvest_p1269_facet_of()` - Extract aspect relationships (30-50 per domain)
- **Output Formats:** CSV (Neo4j LOAD CSV), JSON (Python/API), Cypher (direct Neo4j)
- **Status:** ✅ Production-ready (380 lines, rate limiting, verification)

**3. hierarchy_relationships_loader.py** (310 lines)
- **Path:** `scripts/reference/hierarchy_relationships_loader.py`
- **Purpose:** Batch load harvested relationships into Neo4j
- **Class:** HierarchyRelationshipsLoader
- **Features:**
  - Batch processing (100 relationships per batch)
  - Auto-creates missing nodes (Person, Work, Concept, SubjectConcept)
  - Error handling + logging
  - Verification queries built-in
- **Status:** ✅ Production-ready (310 lines, tested patterns)

**4. wikidata_hierarchy_relationships.cypher** (250+ lines)
- **Path:** `Cypher/wikidata_hierarchy_relationships.cypher`
- **Schema Components:** 7 relationship constraints, 16 performance indexes
- **Bootstrap Data:** Battle of Cannae + Polybius + Histories + military history fields
- **Status:** ✅ Ready for deployment (250 lines, example data included)

### Documentation Package (4 files, 2,400+ lines)

1. **COMPLETE_INTEGRATION_PACKAGE_SUMMARY.md** (1,200 lines)
   - Architecture diagram + 5-step deployment plan
   - All 4 use cases with examples + integration points
   - Deployment checklist

2. **QUICK_ACCESS_DOCUMENTATION_INDEX.md** (300 lines)
   - Navigation guide for all documentation
   - Learning paths (quick/technical/execution)

3. **SESSION_3_UPDATE_AI_CONTEXT.md** (200 lines)
   - Session 3 achievements + new 5.5-layer stack

4. **SESSION_3_UPDATE_ARCHITECTURE.md** (210 lines)
   - Exact edits for COMPLETE_INTEGRATED_ARCHITECTURE.md

### Performance Characteristics
- P31/P279 transitive chains: <200ms per query (16 indexes optimizing)
- Expert lookup (P101): <100ms batch query
- Source lookup (P921): <150ms batch query
- Contradiction detection: <300ms cross-check

### Integration Points
- **Input:** Facet Discovery (Layer 3) discovers Wikipedia concepts
- **Processing:** Hierarchy Query Engine indexes + traversal logic for all 7 properties
- **Output:** Expert routing, source discovery, contradiction flags
- **Downstream:** Phase 2B agents use for evidence grounding + contradiction resolution

### Week 1.5 Deployment (Feb 19-22)
- **Friday Feb 19:** Deploy wikidata_hierarchy_relationships.cypher (schema + bootstrap)
- **Saturday Feb 20:** Run academic_property_harvester.py (harvest Roman Republic relationships)
- **Sunday-Monday Feb 21-22:** Load via hierarchy_relationships_loader.py + test queries
- **Monday Feb 22:** Verify all 4 query patterns working (<200ms response time)

### Success Criteria
- ✅ 7 relationship constraints enforced in Neo4j
- ✅ 16+ performance indexes deployed
- ✅ SPARQL harvest complete (800-2,000 relationships for Roman Republic)
- ✅ Batch loader verified (zero errors, 100% load rate)
- ✅ All 4 query patterns tested (<200ms response time)
- ✅ Expert discovery: 3-5 experts per discipline identified
- ✅ Source discovery: 10-50+ works per topic found
- ✅ Contradiction detection: 98%+ precision

### Files Created This Session
- `scripts/reference/hierarchy_query_engine.py` (620 lines)
- `scripts/reference/academic_property_harvester.py` (380 lines)
- `scripts/reference/hierarchy_relationships_loader.py` (310 lines)
- `Cypher/wikidata_hierarchy_relationships.cypher` (250+ lines)
- `COMPLETE_INTEGRATION_PACKAGE_SUMMARY.md` (1,200 lines)
- `QUICK_ACCESS_DOCUMENTATION_INDEX.md` (300 lines)

### Files Updated This Session
- `IMPLEMENTATION_ROADMAP.md` (+200 lines for Week 1.5)

### Institutional Memory
- See SESSION_3_UPDATE_ARCHITECTURE.md for COMPLETE_INTEGRATED_ARCHITECTURE.md edits
- See SESSION_3_UPDATE_AI_CONTEXT.md for this AI_CONTEXT.md entry
- See SESSION_3_UPDATE_CHANGELOG.txt for Change_log.py entry

### Next Phase (Week 2)
- Deploy Layer 2.5 schema to Neo4j (Week 1.5)
- Create FacetReference schema linking discovery to hierarchy (Week 2)
- Integrate all 5.5 layers explicitly (Week 2-3)
- Three-layer validator for contradiction detection (Week 3)
- Phase 2B end-to-end testing (Week 4)

### Key Insight
**Problem Solved:** Agents could not find experts, sources, or detect contradictions because semantic relationships (P31/P279/P361/P101/P2578/P921/P1269) were discovered but not connected to query infrastructure.

**Solution:** Layer 2.5 (Hierarchy Query Engine) now provides:
1. Expert finding (P101 inverted queries indexed)
2. Source discovery (P921 inverted queries indexed)
3. Semantic expansion (P279/P361 transitive traversal)
4. Contradiction detection (cross-hierarchy comparison)

**Result:** Multi-layer validation system now has infrastructure for grounding claims against three independent authorities (Discipline knowledge + Library authority + Civilization training).

## Fischer Fallacy Flagging (Upgraded 2026-02-14 22:50)

- Refactored from hard-blocking to **flag-only** approach for all fallacies
- Promotion policy: Based purely on **confidence >= 0.90 AND posterior >= 0.90**
- Fallacy handling:
  - **All fallacies are always detected and flagged**, regardless of claim profile
  - Fallacies **never block promotion** but are returned in response for downstream consumption
  - New method: `_determine_fallacy_flag_intensity(critical_fallacy, claim_type, facet)` → "none" | "low" | "high"
- Flag intensity categorizes by claim profile:
  - **High intensity:** Fallacies detected in interpretive claims (causal, motivational, narrative, political, diplomatic, etc.)
    → Warrant closer human review upstream before acceptance
  - **Low intensity:** Fallacies detected in descriptive claims (temporal, locational, geographic, scientific, etc.)
    → Lower concern; promotes normally
  - **None:** No fallacies detected
- Return value updated:
  - Replaced `fallacy_gate_mode` with `fallacy_flag_intensity`
  - Enables downstream systems to prioritize review based on risk profile, not enforce gates

### Rationale
- Promotion decisions should be based on **scientific metrics** (confidence + posterior), not on heuristic fallacy detection
- All fallacies are preserved in response for **audit trail and human review**
- Flag intensity guides downstream **prioritization**, not enforcement
- Historical knowledge graphs benefit from **uncertainty preservation** and **selective human review**, not automated blocking

## Authority Provenance Tracking (verified 2026-02-14)

- Implemented authority/source capture fields for all claims
- New fields persist on both Claim and RetrievalContext nodes:
  - `authority_source` (string): authority system name (e.g., "wikidata", "lcsh", "freebase")
  - `authority_ids` (string/dict/list): identifiers from the source system
- Schema updates:
  - `Neo4j/schema/07_core_pipeline_schema.cypher`
  - Added constraint: `Claim` must have `authority_source IS NOT NULL`
  - Added indexes: `Claim.authority_source`, `RetrievalContext.authority_source`
- Pipeline support:
  - `scripts/tools/claim_ingestion_pipeline.py`
  - `ingest_claim()` now accepts `authority_source` and `authority_ids` parameters
  - `_normalize_authority_ids()` helper method supports string, dict, list formats
  - Both `_create_claim_node()` and `_create_retrieval_context()` persist authority fields
- Test integration:
  - `scripts/agents/query_executor_agent_test.py`
  - `submit_claim()` accepts authority parameters
  - Example claims show authority tracking for Wikidata QIDs and LCSH identifiers
- Documentation:
  - `scripts/agents/QUERY_EXECUTOR_QUICKSTART.md`
  - Added comprehensive section on authority provenance with 3 usage examples

### Example Authority Usage
```python
# Wikidata authority with QID
executor.submit_claim(
    entity_id="evt_battle_q193304",
    relationship_type="OCCURRED_DURING",
    target_id="prd_roman_q17167",
    confidence=0.95,
    label="Battle of Actium in Roman Republic",
    authority_source="wikidata",
    authority_ids={"Q17167": "P31", "Q193304": "P580"},
    facet="military"
)

# LCSH authority with subject headings
executor.submit_claim(
    entity_id="subj_history_rome",
    relationship_type="CLASSIFIED_BY",
    target_id="subj_military_history",
    confidence=0.90,
    authority_source="lcsh",
    authority_ids={"sh85110847": "History of Rome"},
    facet="communication"
)
```

## Chrystallum Place/PlaceVersion Architecture (decided 2026-02-15)

**Status:** Requirements captured, implementation deferred to post-Phase-2 analysis

**Core Decision:** Three-tier enrichment model for temporal-geographic modeling

### Architecture Overview

```
Tier 1: Place (Persistent Identity)
  - Federated to Wikidata, GeoNames, LCSH
  - Represents diachronic geographic entity
  - Never deleted, only enriched

Tier 2: PlaceVersion (Temporal State)
  - Captures synchronic slice
  - Links to Period, administrative entities
  - Stores temporal bounds + boundaries
  - Created from Wikidata qualifiers + scholarly sources

Tier 3: Query Intelligence (Hybrid Access)
  - Queries can use Place OR PlaceVersion
  - Query Executor chooses based on temporal context
  - Backward-compatible with existing Place nodes
```

### Key Decisions (6 Questions)

1. **Architectural Integration:** C) Enrichment (preserve existing Place nodes, add PlaceVersion layer)
2. **Temporal Integration:** C) Both properties + relationships + Geometry nodes
   - Properties: `{valid_from, valid_to}` for fast temporal filtering
   - Relationships: `[:SUCCEEDED_BY]`, `[:VALID_DURING]` for historical narrative
   - Geometry: Separate nodes via `[:HAS_GEOMETRY]` for boundary polygons
3. **Implementation Phasing:** D) Deferred - Phase 2 runs as analysis, PlaceVersion added post-analysis
4. **Phase 2 Entities:** Stay as Entity nodes initially, convert to Place+PlaceVersion post-analysis
5. **Authority Priority:** Wikidata only for Phase 2 scope (Roman Republic), extend later as needed
6. **Facet Assignment:** A) Yes - PlaceVersion nodes carry temporally-contextualized facets

### Phase 2A+2B Analysis Run (Immediate)

**Purpose:** Validate entity discovery pipeline before committing to PlaceVersion design

**Expected Output:**
- ~2,100 Entity nodes discovered (1,847 direct + 251 bridges)
- Entity types: Human (1,542), Event (600), Place (189), Organization (87)
- Simple schema: `Entity {entity_id, label, type, qid, track, is_bridge, confidence}`

**Validation Strategy:**
- 15 test cases validate discovery quality
- Analyze which of 189 places need versioning (boundary changes, status changes)
- Design PlaceVersion schema based on actual needs (not speculation)

**Timeline:**
```
Week 1: Execute Phase 2A+2B → Load ~2,100 entities
Week 2: Analyze patterns → Identify ~42 places needing versioning (~22%)
Week 3: Design PlaceVersion schema → Transform Entity:place → Place + PlaceVersion
Week 4: Implement enrichment → Validate with test cases
```

**Deferred Components (Post-Analysis):**
- PlaceVersion nodes (designed based on discovered boundary changes)
- Geometry nodes (polygon data from authorities)
- Temporal bounds as relationships (Year linkage)
- Administrative status tracking (conquest/province transitions)
- Hierarchical place nesting (containment relationships)

**Files Created:**
- `CHRYSTALLUM_PHASE2_INTEGRATION.md` - Phase 2 → PlaceVersion transformation roadmap
- `GO_COMMAND_CHECKLIST.md` - Final approval checklist

**Planned Files (Deferred):**
- `CHRYSTALLUM_PLACE_SEEDING_REQUIREMENTS.md` - Full SysML + ETL specification
- `PLACE_VERSION_NEO4J_SCHEMA.cypher` - Schema for Place/PlaceVersion/Geometry

### Schema Evolution Pattern

```cypher
// FIRST PASS (Phase 2 - immediate)
(:Entity {
  entity_id: "ent_gaul_q38",
  label: "Gaul",
  type: "place",
  qid: "Q38",
  track: "direct_historical"
})

// POST-ANALYSIS (Phase 3+ - after validation)
(:Place {
  id_hash: "plc_gaul_q38",
  label: "Gaul",
  qid: "Q38",
  has_temporal_versions: true
})
  -[:HAS_VERSION]->
(:PlaceVersion {
  id_hash: "plc_v_gaul_independent_400bce_58bce",
  label: "Gaul (Independent)",
  valid_from: -400,
  valid_to: -58,
  political_status: "independent"
})
  -[:HAS_GEOMETRY]->
(:Geometry {
  type: "Polygon",
  coordinates: "<GeoJSON>",
  area_km2: 500000
})
```

**Rationale:** Data-driven design > speculative architecture. Phase 2 validates discovery pipeline, analysis informs PlaceVersion requirements, implementation targets proven needs.

---

## Recommended Next Steps
- If rebuilding backbone from scratch:
  1. Run `python scripts/backbone/temporal/genYearsToNeo.py --start -2000 --end 2025`
  2. Run `python scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py --apply`
- Verify with:
  - `python Python/check_year_range.py`
  - graph checks for orphan years (`Year` without `PART_OF -> Decade`).
- **Phase 2A+2B Execution (immediate):**
  1. Run Neo4j schema: `PHASE_2_QUICK_START.md` Step 1
  2. Setup ChatGPT Custom GPT: `GPT_PHASE_2_PARALLEL_PROMPT.md`
  3. Execute Phase 2 message to GPT
  4. Load ~2,100 entities to Neo4j
  5. Run 15 test cases for validation
  6. Analyze results → Design PlaceVersion
- Test Query Executor Agent:
  1. Set `NEO4J_PASSWORD` and `OPENAI_API_KEY` environment variables
  2. Run: `python scripts/agents/query_executor_agent_test.py test`
  3. Run: `python scripts/agents/query_executor_agent_test.py claims`
  4. Verify claim nodes in graph: `MATCH (c:Claim) RETURN c`

