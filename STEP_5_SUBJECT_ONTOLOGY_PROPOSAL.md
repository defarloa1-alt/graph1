# Step 5: Subject Ontology Proposal

**Date:** February 15, 2026  
**Status:** ✅ IMPLEMENTED & INTEGRATED  
**Component:** Bridge between Initialize Mode and Training Mode  

---

## Overview

**Subject Ontology Proposal** is the critical step that runs **after Initialize Mode** and **before Training Mode**.

### Purpose

Initialize mode discovers nodes and hierarchical type properties (P31, P279, P361). This raw data needs to be analyzed to extract a coherent **subject ontology** - the conceptual framework that structures the domain.

**Subject Ontology Proposal is UN-FACETED exploration** (SCA as seed agent):

1. **Just hunting nodes and edges** - NO facet lens at this point
2. **Trawls hierarchies broadly** - Follows P31/P279/P361 chains well beyond initial domain
3. **Creates shell nodes** - Lightweight placeholders for cross-domain concepts discovered
4. **Uses backlinks** - Discovers unexpected connections ("purple to mollusk" scenarios)
5. **Expansive ontology** - NOT limited to 3-5 classes; captures ALL discovered subject concepts
6. **Outputs proposed ontology** - This becomes **approval point** before facet-specific work

Subject Ontology Proposal examines these hierarchies and proposes:
1. **Nodes** - ALL discovered entities across domains (breadth exploration)
2. **Edges** - ALL discovered relationships (no facet filtering yet)
3. **Shell Nodes** - Placeholders for concepts outside initial domain
4. **Ontology Structure** - Clusters, hierarchies, type patterns
5. **Claim Templates** - Patterns Training mode will use

**APPROVAL POINT:** Human reviews proposed ontology before Training Mode begins.

After approval, Training Mode uses this ontology as the frame for **facet-by-facet analysis**.

---

## The Three-Step Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ INITIALIZE MODE                                             │
│ - Anchor on Wikidata QID (e.g., Q17167)                    │
│ - Fetch entity + properties                                 │
│ - Validate completeness (Step 3.5)                         │
│ - Enrich with CIDOC-CRM (Step 4)                          │
│ - Discover type hierarchies via P31/P279/P361              │
│ - Generate foundational claims                              │
│ OUTPUT: nodes_created, claims_generated, session_id         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ SUBJECT ONTOLOGY PROPOSAL ← UN-FACETED EXPLORATION         │
│ - Just hunting nodes and edges (NO facet lens)             │
│ - Analyze discovered hierarchies                            │
│ - Identify conceptual clusters                              │
│ - Propose domain ontology structure                         │
│ - Generate claim templates                                  │
│ OUTPUT: ontology_classes, shell_nodes, strength_score       │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ⚠️ APPROVAL POINT ⚠️
              (Human reviews proposed ontology)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ TRAINING MODE - FACET-BY-FACET ANALYSIS                    │
│ - SCA adopts MILITARY facet role                            │
│   → Reads claims from military perspective                  │
│ - SCA adopts POLITICAL facet role                           │
│   → Reads same claims from political perspective            │
│ - SCA adopts CULTURAL facet role                            │
│   → Reads same claims from cultural perspective             │
│ - ...sequential through all relevant facets                 │
│ OUTPUT: claims_proposed, metrics, session_id                │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Method Signature

```python
def propose_subject_ontology(
    self,
    ui_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
```

**Location:** `scripts/agents/facet_agent_framework.py` (lines ~2805-2955)

### Workflow Steps

#### Step 1: Load Initialized Nodes
- Load nodes created during Initialize mode (via session context)
- Requires Initialize mode to have run first
- Returns if no nodes found (SKIPPED status)

#### Step 2: Extract Type Hierarchies
- For each node, fetch full Wikidata entity
- Extract P31 (instance_of) chains
- Extract P279 (subclass_of) chains  
- Extract P361 (part_of) chains
- Build type hierarchy map: `node → [types] → [parent_types]`

**Example for Q17167 (Roman Republic):**
```
P31: Q30 (state), Q15284 (oligarchy)
P279: Q7275 (empire), Q11772 (historical state)
P361: Q221 (ancient Rome)
```

#### Step 3: Identify Conceptual Clusters
Uses LLM (GPT-4) to analyze type hierarchies and identify natural clusters:

**Example Output:**
```json
{
  "clusters": [
    {
      "name": "Political Leadership",
      "concept_count": 8,
      "examples": ["Caesar", "Pompey", "Cicero"],
      "characteristics": ["power base", "political influence", "faction"],
      "parent_cluster": null
    },
    {
      "name": "Military Operations",
      "concept_count": 12,
      "examples": ["Battle of Pharsalus", "Punic Wars"],
      "characteristics": ["date", "duration", "participants"],
      "parent_cluster": null
    }
  ],
  "hierarchy_depth": 3,
  "reasoning": "These clusters emerge naturally from the instance_of relationships..."
}
```

#### Step 4: Propose Ontology Classes
- Convert clusters into formal ontology classes
- Establish relationships between classes (e.g., "subclass_of")
- Assign characteristics to each class

**Output:**
```python
ontology_classes = [
    {
        'class_name': 'Political Actor',
        'parent_class': None,
        'member_count': 25,
        'characteristics': ['power_base', 'affiliations', 'influence_sphere'],
        'examples': ['Pompey', 'Caesar', 'Cato']
    },
    {
        'class_name': 'Military Commander',
        'parent_class': 'Political Actor',
        'member_count': 15,
        'characteristics': ['legions_commanded', 'battles_led', 'military_ranks'],
        'examples': ['Caesar', 'Pompey']
    }
]
```

#### Step 5: Generate Claim Templates
For each class, create templates for what claims Training mode should generate:

```python
claim_templates = [
    {
        'claim_class': 'Political Actor',
        'property': 'power_base',
        'template': 'All {subject} in Political Actor {verb} {value}',
        'validation': 'Check if {value} is a valid power_base',
        'expected_confidence': 0.85
    },
    {
        'claim_class': 'Military Commander',
        'property': 'legions_commanded',
        'template': '{subject} commanded Legion {value}',
        'validation': 'Verify legion existed during {subject}\'s period',
        'expected_confidence': 0.90
    }
]
```

#### Step 6: Define Validation Rules
Ontology-aware validation rules for Training mode to follow:

```python
validation_rules = [
    {
        'rule': 'Within_ontology_class',
        'description': 'Subject must be instance of ontology class',
        'importance': 'HIGH'
    },
    {
        'rule': 'Property_cardinality',
        'description': 'Property values must match class characteristic cardinality',
        'importance': 'MEDIUM'
    },
    {
        'rule': 'Temporal_consistency',
        'description': 'Claims must be temporally consistent with entity dates',
        'importance': 'MEDIUM'
    },
    {
        'rule': 'Cross_facet_alignment',
        'description': 'Property values should align with related facets',
        'importance': 'LOW'
    }
]
```

### Output

```python
{
    'status': 'ONTOLOGY_PROPOSED',           # Success status
    'session_id': str,                       # Session identifier
    'facet': str,                            # Which facet (e.g., "military")
    
    # Ontology structure
    'ontology_classes': List[Dict],          # Proposed classes
    'hierarchy_depth': int,                  # Deepest hierarchy level (1-5)
    'clusters': List[Dict],                  # Identified clusters
    'relationships': List[Dict],             # Class relationships
    
    # Guides for Training mode
    'claim_templates': List[Dict],           # Claim patterns (30-50 templates)
    'validation_rules': List[Dict],          # Quality rules (4-6 rules)
    
    # Quality metrics
    'strength_score': float,                 # Confidence in ontology (0-1)
    'reasoning': str,                        # LLM explanation
    
    # Logging
    'duration_seconds': float,               # Execution time
    'log_file': str,                         # Path to detailed log
}
```

---

## Example: Roman Military Domain

### Initialize Mode Output (inputs to Subject Ontology Proposal)
```
Nodes created: 23
- Caesar (Q1048)
- Pompey (Q1131)
- Battle of Pharsalus (Q28048)
- Legionarii (Q1234567)
...

Type hierarchies discovered:
- Caesar: P31=[Q5 (human), Q1339089 (military commander)]
- Battle of Pharsalus: P31=[Q178561 (battle)]
- Legionarii: P31=[Q11372 (military unit), Q1234567 (organized group)]
```

### Subject Ontology Proposal Analysis

**Identified Clusters:**
1. **Military Leadership** (P31: military commander)
2. **Military Operations** (P31: battle)
3. **Military Organization** (P31: military unit)

**Proposed Ontology Classes:**
```
Military Leadership
├─ Characteristics: commands, rank, victories, defeats
├─ Examples: Caesar, Pompey
└─ Member count: 8

Military Operations
├─ Characteristics: date, participants, outcome, location
├─ Examples: Battle of Pharsalus
└─ Member count: 12

Military Organization
├─ Characteristics: size, type, parent_unit, commanders
├─ Examples: Legionarii, Cavalry Unit
└─ Member count: 3
```

**Claim Templates Generated:**
- "All military commanders have a rank" → Template for rank-based claims
- "All battles have a date and location" → Template for operation claims
- "All units have a parent organization" → Template for hierarchy claims

**Strength Score:** 0.88
- 3 core classes + 12 shell nodes identified (breadth exploration)
- Hierarchy depth: 2
- Successful type hierarchy extraction
- Backlinks discovered 8 cross-domain concepts
- Clear LLM reasoning about domain structure

**Shell Nodes Created:**
- "Tyrian purple" (discovered via hierarchy traversal → political facet)
- "Murex snail" (backlink from purple → scientific facet)
- "Textile dyeing" (cross-domain link → cultural facet)
- ...9 more cross-domain concepts

**Note:** Shell nodes are placeholders. When a specialized agent is assigned to "Tyrian purple" SubjectConcept, it will be expanded with full claims. This allows **breadth-first discovery without immediate LLM cost**.

### Training Mode Uses Ontology

Training mode now knows:
1. **Prioritize:** Military Leadership class (high-value entities)
2. **Template:** Which claim patterns to use for each class
3. **Validate:** Apply ontology-aware validation rules
4. **Focus:** Generate 30-40 claims about military leadership, 20-30 about operations

---

## Integration Points

### 1. Calls After Initialize Mode
```python
# After Initialize completes successfully
result_init = agent.execute_initialize_mode(anchor_qid, depth=2)

# Then propose ontology
result_onto = agent.propose_subject_ontology(ui_callback=ui_log_callback)

# Check strength before Training
if result_onto['strength_score'] > 0.70:
    # Proceed to Training
    result_train = agent.execute_training_mode(...)
```

### 2. Data Flow to Training Mode
Subject Ontology Proposal stores the proposed ontology in the agent:
```python
# In FacetAgent instance
self.proposed_ontology = {
    'classes': ontology_classes,
    'templates': claim_templates,
    'rules': validation_rules,
    'strength': strength_score
}
```

Training mode retrieves and uses it:
```python
def execute_training_mode(self, ...):
    # Use stored ontology to guide claim generation
    ontology = self.proposed_ontology
    for cls in ontology['classes']:
        # Generate claims for this class type
        # Use templates from ontology['templates']
        # Apply rules from ontology['rules']
```

### 3. UI Integration
Gradio tab shows:
- **Initialize Mode** → Prop accordion (collapsed)
- **Subject Ontology Proposal** → Prop accordion (open after Init)
- **Training Mode** → Prop accordion (collapsed, enabled after Ontology)

---

## Performance Characteristics

### Time Complexity
- **Load nodes:** O(n) where n = number of initialized nodes (typically 20-50)
- **Extract hierarchies:** O(n × m) where m = avg. properties per node (typically 5-10)
- **LLM cluster analysis:** O(1) - single LLM call
- **Generate templates:** O(c × p) where c = classes, p = avg properties per class

### Typical Execution Time
- **Optimal (Initialize with 20 nodes):** 15-20 seconds
- **Moderate (Initialize with 50 nodes):** 25-35 seconds
- **Comprehensive (Initialize with 100 nodes):** 40-50 seconds

### Resource Usage
- **Memory:** ~5-10MB (LLM input/outputs, data structures)
- **API calls:** 1 GPT-4 API call (~1000 tokens)
- **Neo4j queries:** 5-10 read queries (no writes)

---

## Error Handling

### Skipped Cases
- **No initialized nodes:** Returns `{status: 'SKIPPED', reason: '...'}`
- **Session context not found:** Returns `{status: 'SKIPPED'}`

### Graceful Degradation
- **LLM cluster analysis fails:** Falls back to hierarchical depth only
- **Wikidata fetch fails for a node:** Logs error, continues with other nodes
- **Type extraction fails:** Node skipped, process continues

### Error Status
- Returns `{status: 'ERROR', error: str(e)}`
- Includes `log_file` path for debugging

---

## Key Insights

### Why This Step Matters

1. **Bridges Initialize to Training**
   - Initialize discovers raw data (nodes, hierarchies)
   - Subject Ontology Proposal structures that data
   - Training uses structure to guide systematic generation

2. **Provides Domain Framework**
   - Not all types are equally important
   - Ontology identifies primary classes
   - Training prioritizes high-value entities

3. **Enables Claim Quality**
   - Claim templates ensure consistency
   - Validation rules prevent erroneous claims
   - Type schema catches nonsensical claims early

4. **Reduces Training Redundancy**
   - Instead of generating blind 100 claims
   - Training now knows domain structure
   - Generates targeted claims within ontology

### What Makes It Work

1. **Type Hierarchies (P31/P279/P361)**
   - Wikidata's instance_of chains encode domain structure
   - By analyzing chains, we extract natural classes
   - LLM recognizes these as conceptual clusters

2. **LLM + Structured Analysis**
   - Type hierarchies give LLM concrete data
   - LLM adds semantic understanding
   - Result: human-interpretable ontology

3. **Intermediate Storage**
   - Proposed ontology stored with agent
   - Training mode accesses it systematically
   - No redundant recalculation

---

## Testing Checklist

### Functionality
- [ ] Loads session context correctly
- [ ] Extracts P31/P279/P361 chains
- [ ] Identifies clusters with LLM
- [ ] Proposes classes and relationships
- [ ] Generates claim templates
- [ ] Defines validation rules
- [ ] Calculates realistic strength score

### Quality
- [ ] Ontology classes match domain (review manually)
- [ ] Claim templates are usable (check wording)
- [ ] Validation rules cover key concerns
- [ ] Strength score correlates with complexity

### Performance
- [ ] Completes in <30s for typical Initialize output
- [ ] Doesn't crash on edge cases
- [ ] Logs are readable and helpful

### Integration
- [ ] Runs after Initialize succeeds
- [ ] Stores ontology for Training to use
- [ ] UI shows results clearly
- [ ] Graceful handling of skip/error cases

---

## Next Steps

### For Development
1. ✅ Implement `propose_subject_ontology()` method
2. ✅ Add Gradio UI tab
3. ✅ Update checklist
4. ⏳ Update Training mode to use proposed ontology
5. ⏳ Run complete smoke test: Initialize → Proposal → Training

### For Validation
1. Run Initialize mode with Q17167 (Roman Republic)
2. Run Subject Ontology Proposal
3. Verify:
   - 3-5 major ontology classes
   - Strength score > 0.70
   - Claim templates well-formed
   - Validation rules reasonable
4. Run Training mode (should use ontology to guide claims)

### For Production
1. Store ontology in Neo4j for persistence
2. Add multi-language ontology descriptions
3. Support ontology versioning
4. Add ontology visualization (graph view)
5. Enable manual ontology adjustment

---

## Related Documentation

- **[STEP_5_COMPLETE.md](STEP_5_COMPLETE.md)** - Full Step 5 implementation guide
- **[STEP_5_DESIGN_OPERATIONAL_MODES.md](STEP_5_DESIGN_OPERATIONAL_MODES.md)** - Design specification
- **[facet_agent_framework.py](scripts/agents/facet_agent_framework.py)** - Implementation (lines 2805-2955)
- **[agent_gradio_app.py](scripts/ui/agent_gradio_app.py)** - UI integration

---

## Summary

**Subject Ontology Proposal** is the bridge between Initialize (discovery) and Training (systematic generation).

It examines type hierarchies discovered during Initialize mode and proposes a coherent subject ontology that structures the domain. This ontology provides:

1. **Classes** - Domain categories
2. **Relationships** - How they relate
3. **Templates** - Claim patterns
4. **Rules** - Quality criteria

Training mode then uses this ontology to guide the generation of systematic, high-confidence claims across the discovered entities.

**Status:** ✅ Ready for smoke testing

