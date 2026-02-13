# Facet System Impact Analysis
**Date:** February 12, 2026  
**Analyzer:** GitHub Copilot  
**Files Analyzed:** 6 facet system files  
**Target Document:** 2-12-26 Chrystallum Architecture - CONSOLIDATED.md  

---

## Executive Summary

**Overall Impact: 🔴 HIGH - Major Architectural Gap**

The facet system files reveal a comprehensive **star pattern architecture** for multi-dimensional claim evaluation that is **largely missing** from the consolidated architecture document. This is not a minor feature—it's a core architectural pattern that affects claim evaluation, agent coordination, quality assurance, and UI design.

**Critical Finding:** The consolidated document treats facets as simple property classifications, but the actual architecture uses facets as **first-class graph nodes** in a **star pattern** where claims are evaluated independently across 16 analytical dimensions.

---

## Files Analyzed

1. **facet assessment - future.md** - Star pattern for claim evaluation with AnalysisRun nodes
2. **facet_node_schema_proposal.md** - Complete schema for 16 facet node types
3. **facet_registry_master.json** - Registry of 16 facets with 86 anchor examples
4. **FACETS_CONSOLIDATION_2026-02-12.md** - Consolidation metadata
5. **periods_with_facets.json** - Sample period data with facet tagging
6. **star-pattern-claims.md** - Detailed star pattern architecture explanation

---

## Current State in Consolidated Document

### What's Already Documented

**Section 3.3: Facets (Entity-Level Classification)**
- Lists 16 analytical dimensions (facets)
- References `Facets/facet_registry_master.json` as canonical source
- Shows basic implementation: `(:Human)-[:HAS_SUBJECT_CONCEPT]->(:SubjectConcept {facet: "Political"})`

**Section 3.4.3: Faceted Periods**
- Mentions facet property on Period nodes: `Period {label: "Late Republic", facet: "political"}`
- Describes stacked timeline views grouped by facet

**Appendix D: Subject Facet Classification** (planned, not yet created)
- Listed in table of contents but content not yet added

### What's Missing

🔴 **CRITICAL GAPS:**

1. **Star Pattern Architecture** - No documentation of:
   - `:AnalysisRun` node type (evaluation pipeline execution)
   - `:FacetAssessment` node type (per-facet evaluation results)
   - `:FacetCategory` node type (facet taxonomy organization)
   - Star pattern: `Claim → AnalysisRun → FacetAssessment → Facet`
   - Multi-dimensional claim evaluation workflow

2. **Facet as First-Class Nodes** - Current doc shows facets as properties, missing:
   - 16 explicit facet node types (`:PoliticalFacet`, `:MilitaryFacet`, etc.)
   - Facet node schemas (unique_id, label, definition, source_qid)
   - `HAS_[FACET_TYPE]_FACET` relationship patterns
   - Facet nodes as reusable graph entities

3. **Facet Assessment Workflow** - No documentation of:
   - How claims are evaluated across multiple facets simultaneously
   - Agent-per-facet assignment (`OWNS_CATEGORY` relationship)
   - AnalysisRun versioning (pipeline_version, re-run comparison)
   - UI patterns for facet-grouped claim evidence

4. **Facet-Specific Agent Routing** - Missing:
   - How agents specialize by facet category
   - Facet-based workload distribution
   - `EVALUATED_BY` relationship linking assessments to agents

---

## Detailed Findings

### Finding 1: Star Pattern for Claims (Critical Architecture)

**Source:** star-pattern-claims.md, facet assessment - future.md

**What It Is:**
A claim is not a simple tree structure—it's a **star hub** with multiple independent evaluations across analytical dimensions:

```
                ┌─→ MilitaryFacet
                │
   ┌─→ Belief ──┼─→ DiplomaticFacet
   │            │
Claim ──→ AnalysisRun ──→ FacetAssessment ──→ PoliticalFacet
   │                           │
   └─→ Place                   ├─→ EconomicFacet
                               └─→ SocialFacet
```

**Key Components:**

1. **`:AnalysisRun` Node** (NEW node type, not in consolidated doc)
   - Represents one execution of evaluation pipeline
   - Properties: `run_id`, `pipeline_version`, `created_at`, `updated_at`
   - Enables re-running analysis and comparing versions
   - One claim can have multiple AnalysisRuns over time

2. **`:FacetAssessment` Node** (NEW node type, not in consolidated doc)
   - Per-facet evaluation output (one per facet per run)
   - Properties:
     - `assessment_id` (unique identifier)
     - `score` (float, confidence/quality score)
     - `rationale` (string, explanation)
     - `status` (enum: "supported", "challenged", "uncertain", "mostly_supported")
     - `created_at` (timestamp)
   - Links to Facet node via `ASSESSES_FACET` relationship
   - Links to Agent via `EVALUATED_BY` relationship

3. **`:FacetCategory` Node** (NEW node type, not in consolidated doc)
   - Organizes facets into categories (e.g., "POLITICAL", "MILITARY")
   - Properties: `key` (uppercase enum), `label` (display name)
   - Enables UI grouping ("show all political assessments")
   - Used for agent assignment (`agent)-[:OWNS_CATEGORY]->(category)`)

**Relationships:**
```cypher
(claim)-[:HAS_ANALYSIS_RUN]->(run)
(run)-[:HAS_FACET_ASSESSMENT]->(assessment)
(assessment)-[:ASSESSES_FACET]->(facet:PoliticalFacet)
(assessment)-[:EVALUATED_BY]->(agent)
(agent)-[:OWNS_CATEGORY]->(category:FacetCategory)
(facet)-[:IN_FACET_CATEGORY]->(category)
```

**Why It Matters:**
- **Multi-dimensional analysis:** Single event evaluated independently across 16 dimensions
- **Agent specialization:** Political expert evaluates political facet, military expert evaluates military facet
- **Independent confidence:** Military_conf=0.95, Political_conf=0.92, Economic_conf=0.80
- **Separate sourcing:** Each facet can cite different sources (Livy for military, Plutarch for political)
- **UI tabs:** "Show me political analysis" / "Show me military analysis"
- **Re-runnable:** Can re-run analysis with new pipeline and compare results

**Example:**
Battle of Pharsalus (48 BCE) evaluated as:
- **Military Facet:** "Military engagement" (conf=0.95, agent=military_historian)
- **Political Facet:** "Political transformation" (conf=0.92, agent=political_historian)
- **Economic Facet:** "War economy impact" (conf=0.80, agent=economic_historian)
- **Social Facet:** "Military service patterns" (conf=0.85, agent=social_historian)

Each dimension is independent with its own evidence, confidence, and expert agent.

---

### Finding 2: Facet Nodes as First-Class Graph Entities

**Source:** facet_node_schema_proposal.md, facet_registry_master.json

**Current Approach (in consolidated doc):**
```cypher
(:Period {label: "Late Republic", facet: "political"})  // Facet as string property
```

**Correct Approach (from new files):**
```cypher
(:Period)-[:HAS_POLITICAL_FACET]->(:PoliticalFacet {
  unique_id: "POLITICALFACET_Q17193",
  label: "Roman Republic",
  definition: "States, empires, governance systems, political eras",
  source_qid: "Q17193"
})
```

**16 Facet Node Types (all missing from Section 3):**

1. `:PoliticalFacet` - States, empires, governance systems
2. `:CulturalFacet` - Cultural formations, identity regimes, symbolic systems
3. `:TechnologicalFacet` - Tool regimes, production technologies, industrial phases
4. `:ReligiousFacet` - Religious movements, institutions, doctrinal eras
5. `:EconomicFacet` - Economic systems, trade regimes, financial structures
6. `:MilitaryFacet` - Warfare, conquests, military systems, strategic eras
7. `:EnvironmentalFacet` - Climate regimes, ecological shifts, environmental phases
8. `:DemographicFacet` - Population structure, migration, urbanization waves
9. `:IntellectualFacet` - Schools of thought, philosophical movements
10. `:ScientificFacet` - Scientific paradigms, revolutions, epistemic frameworks
11. `:ArtisticFacet` - Art movements, architectural styles, aesthetic regimes
12. `:SocialFacet` - Social structures, class systems, kinship regimes
13. `:LinguisticFacet` - Language families, linguistic shifts, script traditions
14. `:ArchaeologicalFacet` - Material cultures, site phases, stratigraphic horizons
15. `:DiplomaticFacet` - Interstate relations, treaties, alliances, diplomatic systems
16. `:CommunicationFacet` - Use of media to communicate messages

**Common Properties (all facet types):**
```json
{
  "unique_id": "POLITICALFACET_Q17193",
  "label": "Roman Republic",
  "definition": "Periods defined by states, regimes, dynasties, governance",
  "source_qid": "Q17193"
}
```

**Specialized Properties:**
- **TemporalFacet:** `start_year`, `end_year`, `precision`
- **GeographicFacet:** `region_qid`, `lat`, `lon`

**Relationship Patterns:**
```cypher
// Generic pattern for any entity type
(entity)-[:HAS_POLITICAL_FACET]->(facet:PoliticalFacet)
(entity)-[:HAS_MILITARY_FACET]->(facet:MilitaryFacet)
(entity)-[:HAS_ECONOMIC_FACET]->(facet:EconomicFacet)

// All facets link to category
(facet:PoliticalFacet)-[:IN_FACET_CATEGORY]->(:FacetCategory {key: "POLITICAL"})
```

**Why First-Class Nodes Matter:**
- **Reusability:** Multiple Period nodes can link to same `PoliticalFacet {qid: "Q17193"}`
- **Rich metadata:** Each facet has definition, source_qid, anchor examples
- **Queryability:** "Find all entities with PoliticalFacet Q17193"
- **Extensibility:** Add new facets without schema migration
- **Authority alignment:** Facets link to Wikidata QIDs for validation

---

### Finding 3: Agent-Per-Facet Assignment Pattern

**Source:** facet assessment - future.md

**Architecture:**
```cypher
// Agent owns a facet category
(:Agent {agent_id: "AGENT_POLITICAL_V1", label: "Political evaluator"})
  -[:OWNS_CATEGORY]->
(:FacetCategory {key: "POLITICAL"})

// When evaluating a claim, agent creates assessment
(:FacetAssessment {score: 0.92, rationale: "High confidence..."})
  -[:EVALUATED_BY]->
(:Agent {agent_id: "AGENT_POLITICAL_V1"})

// Assessment evaluates a specific facet
(:FacetAssessment)-[:ASSESSES_FACET]->(:PoliticalFacet)
```

**Benefits:**
- **Specialization:** Political expert evaluates political dimension only
- **Workload distribution:** Each agent handles their facet category
- **Expertise tracking:** UI shows "evaluated by political historian"
- **Accountability:** Know which agent made which assessment
- **Calibration:** Track agent performance per facet category

**Integration with Section 5 (Agent Architecture):**
Currently Section 5.5 describes Coordinator Agents but doesn't mention facet-based agent assignment. Need to add:
- Agent-per-facet specialization pattern
- `OWNS_CATEGORY` relationship
- Facet-based routing in coordinator workflow

---

### Finding 4: UI Query Patterns for Facet-Grouped Analysis

**Source:** facet assessment - future.md

**Key Query: Show Analysis Grouped by Facet Category**
```cypher
MATCH (c:Claim {claim_id: "CLAIM_CAESAR_RUBICON"})
  -[:HAS_ANALYSIS_RUN]->(run:AnalysisRun)
MATCH (run)-[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
  -[:ASSESSES_FACET]->(f:Facet)
  -[:IN_FACET_CATEGORY]->(cat:FacetCategory)
OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
RETURN
  cat.key AS facet_category,
  cat.label AS category_label,
  collect({
    facet_id: f.unique_id,
    facet_label: f.label,
    score: fa.score,
    status: fa.status,
    rationale: fa.rationale,
    agent: a.label
  }) AS assessments
ORDER BY facet_category;
```

**Result Structure (for UI tabs):**
```json
{
  "facet_category": "POLITICAL",
  "category_label": "Political",
  "assessments": [
    {
      "facet_id": "POLITICALFACET_Q17193",
      "facet_label": "Roman Republic",
      "score": 0.92,
      "status": "supported",
      "rationale": "High confidence based on primary sources",
      "agent": "Political evaluator"
    }
  ]
}
```

**UI Design Pattern:**
- **Tabs per facet category:** Political | Military | Economic | Social | ...
- **Assessment cards:** Each card shows score, status, rationale, agent
- **Comparison view:** Show multiple AnalysisRuns side-by-side
- **Filter by status:** Show only "supported" or "challenged" assessments

**Missing from Consolidated Doc:**
- Section 9 (Workflows) doesn't include facet assessment workflow
- No query examples for facet-grouped UI
- No mention of AnalysisRun versioning for comparison

---

### Finding 5: Facet Registry with 86 Anchors

**Source:** facet_registry_master.json

**What It Contains:**
- 16 facet definitions
- 86 anchor examples (QIDs) across all facets
- Quality flags (e.g., "qid_label_conflict")
- Source priority metadata ("latest" vs "ref" vs "anchors")

**Example Entry:**
```json
{
  "key": "political",
  "facet_class": "PoliticalFacet",
  "label": "Political",
  "definition": "States, empires, governance systems, political eras",
  "anchor_count": 5,
  "quality_flags": ["qid_label_conflict"],
  "source_priority": "latest",
  "lifecycle_status": "active",
  "anchors": [
    {"qid": "Q11514315", "label": "Empire", "source": "latest"},
    {"qid": "Q3624078", "label": "Sovereign state", "source": "latest"},
    /* ... 3 more anchors ... */
  ]
}
```

**Use Cases:**
- **Validation:** Check if entity QID matches known facet anchors
- **Auto-classification:** If entity has QID Q11514315, tag with PoliticalFacet
- **Quality assurance:** Quality flags indicate conflicts needing resolution
- **Documentation:** Anchor examples help humans understand facet scope

**Missing from Consolidated Doc:**
- Appendix D (Subject Facet Classification) not yet created
- No mention of anchor examples for each facet
- No quality flag guidance

---

## Impact Assessment by Document Section

| Section | Current State | Required Changes | Effort | Priority |
|---------|---------------|------------------|--------|----------|
| **3.1-3.2** (Core Node Types) | Missing AnalysisRun, FacetAssessment, FacetCategory | Add 3 new node type schemas | 30 min | 🔴 HIGH |
| **3.3** (Facets) | Basic facet list, property-based approach | Replace with facet node architecture, add 16 facet node types | 45 min | 🔴 HIGH |
| **5.5** (Coordinator Agents) | Generic coordinator description | Add agent-per-facet assignment, OWNS_CATEGORY pattern | 15 min | 🟡 MEDIUM |
| **9.2** (Claim Review Workflow) | Basic review workflow | Add facet assessment workflow, AnalysisRun creation | 30 min | 🔴 HIGH |
| **Appendix D** (Subject Facet Classification) | Placeholder only | Create complete appendix with 16 facets, anchors, registry | 45 min | 🔴 HIGH |

---

## Recommended Actions

### Priority 1: 🔴 CRITICAL (Add Before Implementation)

**1. Add Missing Node Types (Section 3.1-3.2)**
Add schemas for:
- `:AnalysisRun` - Evaluation pipeline execution container
- `:FacetAssessment` - Per-facet evaluation result
- `:FacetCategory` - Facet taxonomy organization
- 16 specific facet node types (`:PoliticalFacet`, `:MilitaryFacet`, etc.)

**Estimated time:** 30 minutes  
**Impact:** Foundational—required for facet assessment workflow

---

**2. Rewrite Section 3.3: Facets (Entity-Level Classification)**
Replace current property-based approach with:
- Facets as first-class graph nodes
- 16 facet node type schemas
- `HAS_[FACET_TYPE]_FACET` relationship patterns
- Facet reusability explanation
- Reference to facet_registry_master.json for anchors

**Estimated time:** 45 minutes  
**Impact:** Core architectural pattern affecting all entity types

---

**3. Add Facet Assessment Workflow (Section 9.2 or new 9.6)**
Document complete workflow:
1. Claim submitted for evaluation
2. Create AnalysisRun node
3. Coordinator routes to facet-specialist agents
4. Each agent creates FacetAssessment node
5. Assessments link to facet nodes via ASSESSES_FACET
6. UI queries for facet-grouped results

Include:
- Complete Cypher example (claim + run + 3 assessments)
- UI query patterns for facet tabs
- AnalysisRun versioning and comparison

**Estimated time:** 30 minutes  
**Impact:** Critical operational workflow for multi-dimensional analysis

---

**4. Create Appendix D: Subject Facet Classification**
Full appendix with:
- Complete list of 16 facets with definitions
- Anchor examples per facet (from registry)
- Node schemas for each facet type
- Relationship patterns
- Quality flags explanation
- Cross-reference to facet_registry_master.json

**Estimated time:** 45 minutes  
**Impact:** Essential reference for implementers

---

### Priority 2: 🟡 MEDIUM (Enhancement)

**5. Update Section 5.5: Coordinator Agents**
Add facet-based agent routing:
- Agent-per-facet specialization pattern
- `OWNS_CATEGORY` relationship
- Coordinator workflow for facet-based routing

**Estimated time:** 15 minutes  
**Impact:** Clarifies agent coordination model

---

**6. Add AnalysisRun Comparison Query Patterns**
Show how to compare multiple runs:
```cypher
// Compare two analysis runs for same claim
MATCH (c:Claim)-[:HAS_ANALYSIS_RUN]->(run1:AnalysisRun {run_id: "RUN_001"})
MATCH (c)-[:HAS_ANALYSIS_RUN]->(run2:AnalysisRun {run_id: "RUN_002"})
// ... compare assessments
```

**Estimated time:** 10 minutes  
**Impact:** Enables pipeline improvement tracking

---

### Priority 3: 🟢 LOW (Future Enhancement)

**7. Add Facet Visualization Examples (Section 12.3)**
- Facet-based timeline stacking
- Radar chart showing claim confidence across facets
- Agent workload distribution by facet category

**Estimated time:** 15 minutes  
**Impact:** Visual design guidance

---

## Summary Statistics

**Total Missing Content:**
- **3 new core node types** (AnalysisRun, FacetAssessment, FacetCategory)
- **16 facet node types** (PoliticalFacet, MilitaryFacet, etc.)
- **1 major architectural pattern** (star pattern for claims)
- **1 complete workflow** (facet assessment pipeline)
- **1 appendix** (Appendix D: Subject Facet Classification)

**Estimated Total Effort:** ~3 hours to add all missing content

**Risk if Not Added:**
- Implementers will use property-based facets (wrong pattern)
- Multi-dimensional claim analysis won't work
- Agent specialization by facet won't be possible
- UI tabs for facet-grouped evidence won't be feasible
- Re-runnable analysis pipeline won't be available

**Recommendation:** Add Priority 1 items (Critical) before implementation begins. This is a foundational architectural pattern affecting multiple system components.

---

## Cross-References

**Related Sections That Need Updates:**
- Section 3.1-3.2: Core Node Types (add AnalysisRun, FacetAssessment, FacetCategory, 16 facet types)
- Section 3.3: Facets (complete rewrite with node-based architecture)
- Section 5.5: Coordinator Agents (add facet-based routing)
- Section 9.2: Claim Review Workflow (add facet assessment workflow)
- Appendix D: Subject Facet Classification (create complete appendix)

**Files to Reference:**
- `Facets/facet_registry_master.json` (canonical registry, 16 facets, 86 anchors)
- `Facets/facet_registry_master.csv` (tabular export)
- `Facets/facet_node_schema_proposal.md` (detailed schemas)
- `Facets/star-pattern-claims.md` (star pattern architecture)
- `Facets/facet assessment - future.md` (assessment workflow)

---

**(End of Impact Analysis)**
