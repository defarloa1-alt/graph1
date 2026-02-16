# SCA â†" SFA Architecture Implementation Package

**Date:** February 15, 2026  
**Status:** ✅ Architecture Finalized, Ready for Implementation  
**Version:** 1.0

---

## Executive Summary

This package documents the **SubjectConceptAgent (SCA) â†" SubjectFacetAgent (SFA) coordination architecture**, including:

1. **Two-Phase Workflow:** Training (independent) → Operational (selective collaboration)
2. **Selective Queue Model:** SCA uses intelligent routing, not automatic queuing
3. **FacetPerspective Nodes:** Multi-facet claim enrichment pattern
4. **Cipher-Based Deduplication:** Content-addressable claim IDs
5. **SCA Routing Criteria:** 5-criteria framework for intelligent orchestration
6. **Military SFA Methodology:** Wikidata filtering strategy (example for all SFAs)

**Key Insight:** During training phase, SFAs build domain ontologies independently. SCA only queues concrete claims for cross-facet review when multi-domain analysis adds value.

---

## Architecture Decision Context

### Problem Statement

After real agent spawning deployment, we needed to finalize how SubjectConceptAgent (SCA) coordinates SubjectFacetAgents (SFAs) during claim creation.

**Three Critical Problems:**

1. **Automatic Queuing Overwhelms System**
   - Initial model: SCA queues ALL claims to ALL SFAs for perspectives
   - Result: Massive inefficiency, SFAs reviewing irrelevant claims
   - Example: "Senate legislative authority" (abstract political concept) doesn't need military/economic/cultural review

2. **Training Phase Needs Independence**
   - User insight: "SFA studying discipline, dealing with abstract concepts, building subject ontology, premature to involve other SFAs"
   - Training phase: SFAs build domain ontologies independently
   - Operational phase: SFAs collaborate on concrete events selectively

3. **Claim Schema Confusion**
   - Two competing models: Separate claims vs Single claim with perspectives
   - Existing architecture had claims as star patterns with cipher IDs
   - Needed: Integration of existing schema + multi-facet enrichment pattern

### Solution: Selective Queue Model with Two-Phase Workflow

**Before (Automatic Queuing):**
```
SCA → Political SFA creates claim → Queue to ALL other SFAs automatically
Problem: Military SFA reviewing "Senate legislative power" (irrelevant)
Result: Wasted computation, SFA confusion about relevance
```

**After (Selective Queuing):**
```
Phase 1 - Training (Independent):
  SCA → Route discipline training data to SFAs
  Political SFA → Build political ontology (abstract concepts)
  Military SFA → Build military ontology (abstract concepts)
  Economic SFA → Build economic ontology (abstract concepts)
  SCA evaluates: All abstract domain concepts → Accept as-is (NO QUEUE)

Phase 2 - Operational (Selective):
  Political SFA → "Caesar appointed dictator 49 BCE" (concrete event)
  SCA evaluates claim characteristics:
    → Concrete historical event (not abstract concept)
    → Multi-domain potential (military + economic relevance)
    → Relevance scoring: Military(0.9), Economic(0.8), Cultural(0.3)
  SCA decision: Queue ONLY to Military + Economic (skip Cultural)
  Military SFA → Create FacetPerspective ("Caesar commanded armies")
  Economic SFA → Create FacetPerspective ("Caesar controlled treasury")
```

---

## File Inventory

### Core Architecture Documents (NEW)

#### 1. SCA_SFA_ROLES_DISCUSSION.md
- **Location:** `c:\Projects\Graph1\SCA_SFA_ROLES_DISCUSSION.md`
- **Size:** 1,153 lines
- **Status:** ✅ MAJOR DECISIONS FINALIZED
- **Purpose:** Comprehensive specification of SCA ↔ SFA roles and responsibilities
- **Key Sections:**
  * Two Phases of SFA Work (Training vs Operational)
  * SCA Selective Claim Routing (abstract vs concrete examples)
  * Claim Architecture (cipher + star pattern + FacetPerspective nodes)
  * SCA Routing Criteria (5 criteria framework with detailed examples)
  * Finalized Roles & Responsibilities table
  * Next Steps (implementation roadmap)
- **Content:**
  * 11 major sections
  * Complete workflow examples (training + operational phases)
  * Cipher-based deduplication walkthrough
  * SCA evaluate_claim_for_queue() pseudocode (~50 lines)
  * "Caesar dictator" example with relevance scoring across all facets
  * Convergence detection patterns
  * FacetPerspective node schema
- **Key Decisions:**
  1. ✅ SCA owns ontology, SFAs consume
  2. ✅ SFAs create facet-specific claims ONLY (no cross-domain)
  3. ✅ Training Phase: Independent domain ontology building
  4. ✅ Operational Phase: Selective multi-facet collaboration
  5. ✅ Selective Queue Model: Intelligent routing, not automatic
  6. ✅ SCA Routing Criteria: 5 criteria documented

#### 2. CLAIM_WORKFLOW_MODELS.md
- **Location:** `c:\Projects\Graph1\CLAIM_WORKFLOW_MODELS.md`
- **Size:** 450 lines
- **Status:** ✅ RECOMMENDATIONS FINALIZED
- **Purpose:** Compare claim workflow approaches and recommend optimal model
- **Key Sections:**
  * Model A: Independent with Selective Queue
  * Model B: Proposed Claim + SFA Responses
  * Hybrid Model: Training + Selective Review (RECOMMENDED)
  * Alternative: FacetPerspective Nodes
  * Recommendation section with detailed examples
  * Next Steps for implementation
- **Content:**
  * 4 workflow models compared
  * Complete star pattern diagrams
  * Training phase walkthrough (3 SFAs building ontologies independently)
  * Operational phase walkthrough ("Caesar dictator" example with selective routing)
  * Schema extension for FacetPerspective node
  * Pros/cons analysis for each model
- **Recommended Model:** Training + Selective Review
  * Phase 1: Independent domain ontology building (abstract concepts, no queue)
  * Phase 2: Selective multi-facet review (concrete events, intelligent routing)

#### 3. Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md
- **Location:** `c:\Projects\Graph1\Facets\MILITARY_SFA_ONTOLOGY_METHODOLOGY.md`
- **Size:** 1,100 lines
- **Status:** ✅ READY FOR IMPLEMENTATION
- **Purpose:** Wikidata filtering methodology for Military SFA training phase
- **Key Sections:**
  * 1. Anchor: Military as Discipline (Q192386)
  * 2. Inclusion Criteria for Ontology Nodes
  * 3. Exclusion Criteria to Strip Noise
  * 4. Structural Filters on Properties
  * 5. Roman Republic–Specific Refinement
  * 6. Implementation Strategy (SPARQL queries)
  * 7. Validation Checklist
  * 8. Expected Ontology Structure
  * 9. Integration with SCA Workflow
  * 10. References
- **Content:**
  * Property whitelist (P279, P31, P361, P527, P607, P241, P410, P7779)
  * Wikimedia blacklist (Q4167836, Q11266439, etc.)
  * Inclusion/exclusion criteria with examples
  * Ready-to-run SPARQL queries for both phases
  * Expected ontology statistics (~500-1,000 generic, ~100-200 Roman)
  * Training claim examples (abstract concepts, no queue)
  * Integration with SCA evaluation logic
  * Complete validation checklist
- **Noise Reduction:** 80-90% expected
- **Applicability:** Template for all 17 facet SFAs

#### 4. REAL_AGENTS_DEPLOYED.md
- **Location:** `c:\Projects\Graph1\REAL_AGENTS_DEPLOYED.md`
- **Size:** ~200 lines (estimated)
- **Status:** ✅ REFERENCE DOCUMENTATION
- **Purpose:** Documents completion of real agent spawning
- **Key Content:**
  * Real agent spawning implementation complete
  * FacetAgentFactory.spawn_agent(mode='real') functional
  * LLM integration working (facet-specific system prompts)
  * 17 facet agents spawnable on-demand

---

### Canonical Documentation (UPDATED)

#### 5. Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md
- **Location:** `c:\Projects\Graph1\Key Files\2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
- **Size:** 7,992 lines (was 7,698, +294 lines)
- **Status:** ✅ PRIMARY ARCHITECTURE SPEC (v3.2+)
- **Updates:**
  * **NEW Section 5.5:** SubjectConceptAgent ↔ SubjectFacetAgent Coordination (SCA ↔ SFA)
    - 5.5.1 Agent Types & Roles
    - 5.5.2 Two-Phase Workflow (Training + Operational)
    - 5.5.3 Claim Architecture: Cipher + Star Pattern
    - 5.5.4 SCA Routing Criteria (5-Criteria Framework)
    - 5.5.5 Benefits & Implementation Status
  * **NEW Section 5.7:** SFA Ontology Building Methodology
    - 5.7.1 Military SFA Methodology (Example)
    - 5.7.2 Generalized Methodology (All SFAs)
  * **Updated Section 5.6:** Coordinator Agents (reference to Section 5.5)
- **Added Content:**
  * ~300 lines of SCA ↔ SFA coordination architecture
  * Complete two-phase workflow documentation
  * FacetPerspective node schema
  * Cipher-based deduplication explanation
  * SCA routing criteria with examples and pseudocode
  * Military SFA methodology summary
  * Generalized SFA ontology building steps
- **Cross-References:**
  * Section 3.2.6 (facet assessment workflow)
  * Section 6 (Claims Layer)
  * Section 6.9 (claim promotion)
  * SCA_SFA_ROLES_DISCUSSION.md (complete specification)
  * CLAIM_WORKFLOW_MODELS.md (workflow comparison)
  * Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md (filtering methodology)

#### 6. AI_CONTEXT.md
- **Location:** `c:\Projects\Graph1\AI_CONTEXT.md`
- **Size:** 1,142 lines (was ~1,000, +142 lines)
- **Status:** ✅ UPDATED
- **Updates:**
  * **NEW Latest Update Section:** SCA ↔ SFA Roles Finalized + Selective Queue Model
    - Two-Phase Workflow (Training vs Operational)
    - Claim Architecture (Cipher + Star Pattern) with diagram
    - FacetPerspective Nodes schema
    - SCA Routing Criteria (5 criteria)
    - Military SFA Ontology Methodology summary
    - Complete examples (abstract vs concrete claims)
  * Moved previous "Latest Update" to "Previous Update"
- **Key Content:**
  * User insight: "SFA studying discipline, dealing with abstract concepts"
  * Training phase walkthrough (Political/Military/Economic SFAs)
  * Operational phase walkthrough ("Caesar dictator" example)
  * Star pattern diagram (ASCII art)
  * Cipher computation formula
  * Complete relevance scoring example
  * File references with locations
- **Status Line:** ✅ Architecture finalized, ready for implementation

#### 7. Change_log.py
- **Location:** `c:\Projects\Graph1\Change_log.py`
- **Size:** 1,374 lines (was ~1,200, +174 lines)
- **Status:** ✅ UPDATED
- **Updates:**
  * **NEW Entry:** 2026-02-15 22:00 | SCA/SFA ROLES FINALIZED + SELECTIVE QUEUE MODEL + MILITARY METHODOLOGY
- **Entry Content (~150 lines):**
  * Summary: Finalized SCA ↔ SFA architecture, selective queue model, two-phase workflow, FacetPerspective nodes, cipher deduplication, SCA routing criteria, Military SFA methodology
  * Files (NEW): 3 major documents created
  * Files (UPDATED): 2 major documents updated (~600 lines changed)
  * Reason: Critical architectural decision context (3 problems documented)
  * Architecture Changes: BEFORE (automatic queuing) vs AFTER (selective queuing)
  * Key Components: 5 major components documented
  * Implementation Status: Checkmarks for completed, pending items
  * Benefits: 6 key benefits listed
  * Documentation: 3 reference files

---

## Key Architectural Concepts

### 1. Two-Phase SFA Workflow

**Phase 1: Training Mode (Independent)**
- SFAs study discipline independently (Political Science, Military History, etc.)
- Build domain-specific subject ontologies
- Create claims about **abstract concepts** (governance structures, tactical theory)
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

**Phase 2: Operational Mode (Selective Collaboration)**
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

---

### 2. Claim Architecture: Cipher + Star Pattern

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

**Claim Cipher (Content-Addressable ID - REVISED):**
```python
# Facet-Level Claim Cipher (Stable, Content-Based)
facet_claim_cipher = Hash(
    # Core assertion
    subject_node_id +            # Q1048 (Caesar)
    property_path_id +           # "CHALLENGED_AUTHORITY_OF"
    object_node_id +             # Q1747689 (Roman Senate)
    
    # Context
    facet_id +                   # "political" (essential!)
    temporal_scope +             # "-0049-01-10"
    
    # Source provenance
    source_document_id +         # Q644312 (Plutarch)
    passage_locator              # "Caesar.32"
    
    # REMOVED: confidence, agent, timestamp (now separate metadata)
)
# Result: "fclaim_pol_abc123..." (stable cipher)
```

**Key Changes:**
- ❌ **REMOVED:** `confidence_score` (evidence quality ≠ claim identity)
- ❌ **REMOVED:** `extractor_agent_id` (provenance, not content)
- ❌ **REMOVED:** `extraction_timestamp` (enables deduplication across time)
- ✅ **ADDED:** `facet_id` (explicit facet dimension)
- ✅ **ADDED:** `property_path_id` (normalized predicate)

**Benefit:** Two SFAs discovering SAME claim at different times → SAME cipher → Single Claim node (automatic deduplication)

**Alignment:** Follows nanopublication assertion graph patterns (claim identity separate from provenance)

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

**Why FacetPerspective instead of separate claims?**
- ✅ **Single source of truth:** One Claim node (via cipher deduplication)
- ✅ **Multi-facet enrichment:** Multiple perspectives attached
- ✅ **Consensus calculation:** AVG(all perspective confidences)
- ✅ **Clear semantics:** Claim = base assertion, Perspective = facet interpretation

---

### 3. SCA Routing Criteria (5-Criteria Framework)

**How SCA determines which claims warrant cross-facet review:**

**Criterion 1: Abstract vs Concrete Detection**
- **Abstract domain concepts** → NO QUEUE (accept as-is)
  * Theoretical frameworks ("Senate legislative authority")
  * Discipline-specific methods ("Manipular tactics")
  * General principles ("Agricultural economy base")
- **Concrete events/entities** → EVALUATE FOR QUEUE
  * Specific historical events ("Caesar crossed Rubicon")
  * Named individuals with roles ("Caesar appointed dictator")
  * Dated occurrences ("49 BCE")

**Criterion 2: Multi-Domain Relevance Scoring (0-1.0 scale)**
- **High Relevance (0.8-1.0)** → Queue to SFA
- **Medium Relevance (0.5-0.7)** → Queue to SFA
- **Low Relevance (0.0-0.4)** → Do NOT queue

**Example: "Caesar was appointed dictator in 49 BCE"**
```
Political SFA (creator): 1.0 (created the claim)
Military SFA: 0.9 (Caesar = commander, dictator = supreme command)
Economic SFA: 0.8 (dictator = treasury control, state finances)
Cultural SFA: 0.3 (minor cultural impact, not primary)
Religious SFA: 0.2 (no significant religious dimension)
Scientific SFA: 0.1 (irrelevant to scientific domain)

SCA Decision:
→ Queue to: Military (0.9), Economic (0.8)
→ Skip: Cultural (0.3), Religious (0.2), Scientific (0.1)
```

**Criterion 3: Entity Type Detection**
- Query Wikidata P31 (instance of)
- Map entity types to facet relevance:
  * Q5 (Human) → Political, Military, Cultural potential
  * Q198 (War) → Military, Political, Economic potential
  * Q216353 (Battle) → Military, Geographic potential

**Criterion 4: Conflict Detection**
- Date discrepancies → Queue for synthesis
- Attribute conflicts → Queue for synthesis
- Relationship disputes → Queue for synthesis

**Criterion 5: Existing Perspectives Check**
```cypher
MATCH (p:FacetPerspective)-[:PERSPECTIVE_ON]->(c:Claim {cipher: $cipher})
RETURN COLLECT(p.facet) AS existing_facets
// Only queue to facets NOT in existing_facets
```

**Complete Routing Pseudocode:**
```python
def evaluate_claim_for_queue(claim: Claim, source_facet: str) -> Dict[str, float]:
    """
    Evaluate which SFAs should analyze this claim
    
    Returns: Dict of facet → relevance_score
    """
    # Step 1: Check if abstract concept
    if is_abstract_concept(claim):
        return {}  # No queue
    
    # Step 2: Extract entities
    entities = extract_entities(claim.text)
    
    # Step 3: Score relevance to each facet
    relevance_scores = {}
    for facet in ALL_FACETS:
        if facet == source_facet:
            continue  # Skip source facet
        
        score = 0.0
        for entity in entities:
            entity_type = get_entity_type(entity.qid)
            score += calculate_relevance(entity_type, facet)
        
        relevance_scores[facet] = score / len(entities)
    
    # Step 4: Check existing perspectives
    existing_facets = get_existing_perspectives(claim.cipher)
    
    # Step 5: Filter by threshold
    queue_targets = {
        facet: score 
        for facet, score in relevance_scores.items()
        if score >= 0.5 and facet not in existing_facets
    }
    
    return queue_targets
```

---

### 4. Military SFA Ontology Methodology

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

**Result:** ~80-90% noise reduction
- Generic military ontology: ~500-1,000 concepts
- Roman Republican specialization: ~100-200 concepts

**Example Training Claims (NO CROSS-FACET REVIEW):**
```
Claim 1: "Legion was primary Roman military unit"
  → Type: Discovery Mode (abstract domain concept)
  → Source: Wikidata Q170944 + scholarly sources
  → Confidence: 0.95
  → Facet: Military
  → SCA Action: Accept as-is (NO QUEUE)

Claim 2: "Cohort composed of multiple maniples"
  → Type: Discovery Mode (abstract structural relationship)
  → Source: Wikidata Q82955, Q1541817
  → Confidence: 0.90
  → Facet: Military
  → SCA Action: Accept as-is (NO QUEUE)
```

---

## Implementation Roadmap

### Completed ✅

1. ✅ Real agent spawning (FacetAgentFactory.spawn_agent with mode='real')
2. ✅ SCA ↔ SFA roles definition
3. ✅ Two-phase workflow design (Training + Operational)
4. ✅ Claim schema integration (cipher + star pattern)
5. ✅ FacetPerspective node pattern definition
6. ✅ Selective queue model design
7. ✅ SCA routing criteria documentation (5 criteria with examples)
8. ✅ Military SFA methodology documentation (Wikidata filtering)
9. ✅ All documentation updated (2 major files, ~600 lines changed)
10. ✅ Canonical architecture updated (CONSOLIDATED.md, +294 lines)

### Pending ⏸️

1. ⏸️ FacetPerspective node schema (add to NODE_TYPE_SCHEMAS.md)
2. ⏸️ SCA claim evaluation implementation (abstract vs concrete detection)
3. ⏸️ SCA relevance scoring implementation (0-1.0 scale)
4. ⏸️ Entity type detection (Wikidata P31 queries)
5. ⏸️ FacetPerspective creation in SFA (both modes)
6. ⏸️ Cipher-based claim deduplication implementation
7. ⏸️ Selective queue logic in SCA
8. ⏸️ Testing: Training phase (independent ontology building)
9. ⏸️ Testing: Operational phase (selective routing)

### Next Actions (Immediate)

**1. Update NODE_TYPE_SCHEMAS.md**
- Add FacetPerspective node schema
- Properties: perspective_id, facet, parent_claim_cipher, facet_claim_text, confidence, reasoning
- Relationships: [:PERSPECTIVE_ON]->(Claim), [:CREATED_BY]->(Agent)

**2. Implement SCA Claim Evaluation**
- `is_abstract_concept(claim)` method
- Criteria: entity types, terminology patterns, specificity indicators
- Returns: boolean

**3. Implement SCA Relevance Scoring**
- `calculate_relevance(entity_type, facet)` method
- Entity type mapping (Q5→Political/Military, Q198→Military/Political/Economic)
- Returns: float (0-1.0)

**4. Implement FacetPerspective Creation (SFA)**
- Training mode: Create Claim + FacetPerspective
- Perspective mode: Create FacetPerspective only (if queued)
- Cipher-based linking

**5. Implement Cipher Deduplication**
- Before creating Claim, check if cipher exists
- If exists: Add FacetPerspective only
- If new: Create Claim + FacetPerspective

**6. Implement Selective Queue Logic (SCA)**
- `evaluate_claim_for_queue()` method
- Returns: Dict[facet → relevance_score]
- Only queue to facets with score ≥ 0.5

---

## Testing Strategy

### Training Phase Testing

**Goal:** Validate independent domain ontology building

**Test Scenarios:**
1. Spawn 3 SFAs (Political, Military, Economic)
2. Route discipline training data to each SFA
3. Each SFA creates ~10-20 abstract domain concept claims
4. SCA receives all claims
5. SCA evaluates: Are these abstract? (YES for all)
6. SCA decision: Accept all as-is (NO QUEUE)
7. Verify: No cross-facet perspectives created
8. Verify: All 30-60 claims integrated into graph

**Expected Results:**
- 0 claims queued to other SFAs
- Training phase completes in single iteration
- SFAs work independently without interference

### Operational Phase Testing

**Goal:** Validate selective multi-facet collaboration

**Test Scenarios:**
1. Political SFA creates concrete claim: "Caesar appointed dictator in 49 BCE"
2. SCA receives claim
3. SCA evaluates: Concrete event (not abstract)
4. SCA relevance scoring:
   - Military: 0.9 → QUEUE
   - Economic: 0.8 → QUEUE
   - Cultural: 0.3 → SKIP
   - Religious: 0.2 → SKIP
5. SCA queues to Military + Economic only
6. Military SFA creates FacetPerspective
7. Economic SFA creates FacetPerspective
8. SCA checks: All relevant perspectives received?
9. SCA calculates consensus: AVG(0.95, 0.90, 0.88) = 0.91
10. Verify: 1 Claim + 3 FacetPerspectives in graph

**Expected Results:**
- Only 2 SFAs (Military, Economic) receive queue
- 3 SFAs (Cultural, Religious, Scientific) skipped
- Selective routing = ~60% efficiency gain vs automatic queuing
- Consensus score calculated correctly

### Cipher Deduplication Testing

**Goal:** Validate automatic deduplication when two SFAs discover same claim

**Test Scenarios:**
1. Political SFA creates claim: "Caesar crossed Rubicon 49 BCE"
   - Claim cipher: "claim_abc123..."
   - FacetPerspective: political
2. SCA queues to Military SFA
3. Military SFA independently discovers SAME fact from different source
4. Military SFA computes cipher: "claim_abc123..." (SAME!)
5. Neo4j check: Does claim cipher already exist? (YES)
6. Military SFA creates FacetPerspective ONLY (not new Claim)
7. Verify: 1 Claim + 2 FacetPerspectives in graph (not 2 Claims)

**Expected Results:**
- Cipher computation generates identical hash for same content
- MERGE logic prevents duplicate Claim nodes
- Multiple FacetPerspectives attach to single Claim
- Automatic deduplication without manual intervention

---

## Benefits Summary

### 1. Efficient Collaboration
- Only concrete/multi-domain claims get cross-facet review
- Abstract domain concepts accepted without queuing
- ~60-80% reduction in unnecessary SFA reviews

### 2. Independent Learning
- SFAs build domain ontologies without interference
- Training phase respects disciplinary expertise
- No premature cross-facet collaboration

### 3. Selective Enrichment
- Multi-facet analysis applied where it adds value
- Relevance scoring ensures appropriate SFA involvement
- Resources focused on concrete events, not abstract concepts

### 4. SCA Intelligence
- Orchestrator makes informed routing decisions
- 5-criteria framework provides systematic evaluation
- Prevents both over-queuing and under-queuing

### 5. Noise Reduction
- Military SFA filters Wikidata platform artifacts
- 80-90% noise reduction from disciplinary anchoring
- Clean ontologies for all 17 facet domains

### 6. Disciplinary Grounding
- Q192386 (military science) as scholarly root
- Property whitelists emphasize semantic structure
- Methodology applicable to all academic disciplines

---

## References

### Primary Documents (This Package)
1. SCA_SFA_ROLES_DISCUSSION.md - Complete roles specification
2. CLAIM_WORKFLOW_MODELS.md - Workflow comparison
3. Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md - Wikidata filtering
4. This file (SCA_SFA_ARCHITECTURE_PACKAGE.md) - Package summary

### Canonical Architecture
- Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md (Section 5.5, 5.7)

### Context & History
- AI_CONTEXT.md (Latest Update section)
- Change_log.py (2026-02-15 22:00 entry)

### Implementation Files (Existing)
- scripts/agents/facet_agent_framework.py (agent base classes)
- scripts/agents/FacetAgentFactory.py (agent spawning)
- scripts/agents/facet_agent_system_prompts.json (17 facet prompts)

### Related Documentation
- REAL_AGENTS_DEPLOYED.md (agent spawning completion)
- PHASE_1_CHECKLIST.md (project roadmap)
- ARCHITECTURE_IMPLEMENTATION_INDEX.md (section → file mapping)

---

## Package Checklist

Use this checklist when packaging files for review or deployment:

### Core Architecture Documents
- [ ] SCA_SFA_ROLES_DISCUSSION.md (1,153 lines)
- [ ] CLAIM_WORKFLOW_MODELS.md (450 lines)
- [ ] Facets/MILITARY_SFA_ONTOLOGY_METHODOLOGY.md (1,100 lines)
- [ ] REAL_AGENTS_DEPLOYED.md (~200 lines)
- [ ] SCA_SFA_ARCHITECTURE_PACKAGE.md (this file, ~1,000 lines)

### Updated Canonical Docs
- [ ] Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md (Section 5.5, 5.7)
- [ ] AI_CONTEXT.md (Latest Update section)
- [ ] Change_log.py (2026-02-15 22:00 entry)

### Implementation References (Existing)
- [ ] scripts/agents/facet_agent_framework.py
- [ ] scripts/agents/FacetAgentFactory.py
- [ ] scripts/agents/facet_agent_system_prompts.json

### Total Package Size
- **New Documents:** ~3,000 lines (3 major files + 1 reference + this summary)
- **Updated Documents:** ~600 lines changed across 3 files
- **Total Impact:** ~3,600 lines of new/updated content

---

## Version History

### v1.0 (2026-02-15 Evening)
- Initial package creation
- All architecture decisions documented
- All files inventoried
- Implementation roadmap complete
- Testing strategy defined
- Ready for implementation phase

---

**Status:** ✅ ARCHITECTURE FINALIZED - Ready for implementation

**Next Milestone:** Implement FacetPerspective nodes + SCA claim evaluation logic

**Estimated Implementation Time:** 2-3 days for core features, 1 week for full testing
