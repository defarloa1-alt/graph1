# Appendix Q: Operational Modes Agent Orchestration

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

