# SCA as Seed Agent: Breadth-First Exploration Pattern

**Date:** February 15, 2026  
**Context:** Clarification on SubjectConceptAgent (SCA) role in ontology discovery

---

## Core Principle: Two-Phase Workflow

The **SubjectConceptAgent (SCA)** is a **SEED AGENT** with **TWO DISTINCT PHASES**:

### Phase 1: Un-Faceted Exploration (Initialize + Ontology Proposal)

**Just Hunting Nodes and Edges:**
- Starts with anchor QID (e.g., Q17167 "Roman Republic")
- **NO facet lens at this point** - pure structural discovery
- Discovers entities and relationships through:
  * P31 (instance_of) chains
  * P279 (subclass_of) chains
  * P361 (part_of) chains
  * **Backlinks** from Wikidata (reverse triple discovery)
- Goes well beyond initial domain (breadth over depth)

**Creates Shell Nodes:**
- When SCA discovers a concept, it creates a **shell node** (lightweight placeholder)
- NO facet assignment yet - just structural placeholders
- No full property expansion (deferred)

**Outputs Proposed Ontology:**
- ALL discovered nodes (entities)
- ALL discovered edges (relationships)
- Shell nodes for cross-domain concepts
- Structural clusters and hierarchies

**→ APPROVAL POINT:** Human reviews proposed ontology

### Phase 2: Facet-by-Facet Analysis (Training Mode)

**After approval, SCA adopts sequential facet roles:**
- **Step 1:** SCA takes on MILITARY facet role
  * Reads all claims from military perspective
  * Extracts military-specific insights
- **Step 2:** SCA takes on POLITICAL facet role
  * Reads SAME claims from political perspective
  * Extracts political-specific insights
- **Step 3:** SCA takes on CULTURAL facet role
  * Reads SAME claims from cultural perspective
  * Extracts cultural-specific insights
- **Step N:** Continue through all relevant facets

**Purple to Mollusk Scenario:**
- Phase 1: Discovers "Roman senator" → "purple toga" → "Tyrian purple" → "murex snail" (un-faceted)
- Phase 2: Analyzes murex from MILITARY perspective (dye trade logistics), ECONOMIC perspective (trade value), SCIENTIFIC perspective (biology), etc.

---

## The Purple to Mollusk Example

### Starting Point
```
Agent: Military FacetAgent
Anchor: Q17167 (Roman Republic)
Domain: military (initial facet)
```

### Hierarchy Traversal (P31/P279/P361)

```
Q17167 (Roman Republic)
  ├─ P31 → Q7275 (state)
  ├─ P279 → Q15284 (oligarchy)
  └─ P361 → Q1747689 (Ancient Rome)
       └─ P31 → Q28171280 (ancient civilization)
            └─ Discovers: Q172645 (toga) [political/cultural]
```

**SCA Action:** Creates shell node for "toga" (outside military facet)

### Backlinks Discovery

```
Query Wikidata backlinks for Q172645 (toga):

Backlink sources mentioning toga:
  - Q191172 (Roman senator) [political facet]
  - Q189108 (Tyrian purple) [material_culture facet]
  - Q178801 (purple stripe) [political/cultural]
```

**SCA Action:** Creates shell nodes for "murex", "shellfish", "textile dyeing"

### Result: Un-Faceted Ontology (Phase 1 Output)

**From ONE anchor, SCA discovered 15+ concepts across multiple domains:**

| Concept | QID | Discovered Via | Node Type | Facet Assignment |
|---------|-----|----------------|-----------|------------------|
| Roman Republic | Q17167 | Anchor (initial) | Core | TBD (after approval) |
| Roman senator | Q191172 | P31 hierarchy | Shell | TBD |
| toga | Q172645 | P31 traversal | Shell | TBD |
| purple stripe | Q178801 | Backlink from toga | Shell | TBD |
| Tyrian purple | Q189108 | Backlink from stripe | Shell | TBD |
| murex snail | Q191989 | Backlink from purple | Shell | ⭐ TBD |
| shellfish | Q28922 | P279 hierarchy | Shell | TBD |
| textile dyeing | Q184211 | Backlink from purple | Shell | TBD |
| dye production | (derived) | P361 from textile | Shell | TBD |

**Key Point:** At this stage, NO FACETS have been assigned. These are just discovered nodes and edges.

---

## Approval Point: Human Review

After Phase 1 (un-faceted exploration), the proposed ontology is presented for **human approval**:

### What Gets Reviewed

```json
{
  "session_id": "military_20260215_143500",
  "anchor": {"qid": "Q17167", "label": "Roman Republic"},
  
  "discovered_nodes": [
    {"qid": "Q17167", "label": "Roman Republic", "type": "core"},
    {"qid": "Q191172", "label": "Roman senator", "type": "shell"},
    {"qid": "Q172645", "label": "toga", "type": "shell"},
    {"qid": "Q189108", "label": "Tyrian purple", "type": "shell"},
    {"qid": "Q191989", "label": "murex", "type": "shell"},
    // ...+10 more
  ],
  
  "discovered_edges": [
    {"from": "Q17167", "to": "Q191172", "via": "P31", "property": "instance_of"},
    {"from": "Q191172", "to": "Q172645", "via": "backlink", "property": "wears"},
    {"from": "Q172645", "to": "Q189108", "via": "P31", "property": "colored_with"},
    {"from": "Q189108", "to": "Q191989", "via": "backlink", "property": "extracted_from"},
    // ...+20 more edges
  ],
  
  "structural_clusters": [
    {"cluster": "Political Entities", "node_count": 8, "examples": ["Q191172", "Q17167"]},
    {"cluster": "Material Culture", "node_count": 5, "examples": ["Q172645", "Q189108"]},
    {"cluster": "Biological Entities", "node_count": 3, "examples": ["Q191989", "Q28922"]}
  ],
  
  "strength_score": 0.88,
  "reasoning": "Discovered 15 nodes across 3 domains via hierarchy + backlinks. Purple-to-mollusk cross-domain path validated."
}
```

### Approval Decision

**Human reviews and decides:**
- ✅ **Approve** → Proceed to Phase 2 (facet-by-facet analysis)
- ❌ **Reject** → Adjust parameters and re-run Phase 1
- 📝 **Modify** → Edit discovered nodes/edges, then approve

### Why Approval Matters

1. **Quality Control:** Ensure discovered nodes are relevant (not noise)
2. **Scope Validation:** Confirm breadth exploration captured the right domain
3. **Resource Planning:** Decide which shell nodes to expand (prioritize)
4. **Facet Strategy:** Plan which facets to apply in Phase 2

---

## Phase 2: Facet-by-Facet Analysis

After approval, SCA enters **Training Mode** where it **sequentially adopts facet roles**.

### Sequential Facet Workflow

```python
# Phase 2: Sequential facet analysis
approved_ontology = {
    'nodes': [...],  # 15 discovered nodes
    'edges': [...]   # 23 discovered edges
}

# SCA adopts facet roles one at a time
for facet in ['military', 'political', 'cultural', 'economic', 'scientific']:
    sca.adopt_facet_role(facet)
    
    # Read claims from THIS facet's perspective
    claims = sca.analyze_from_facet_perspective(
        ontology=approved_ontology,
        facet=facet
    )
    
    # Extract facet-specific insights
    facet_insights = sca.extract_facet_insights(claims, facet)
    
    # Store facet-specific claims
    store_claims(claims, facet)
```

### Example: Same Node, Different Facets

**Node:** Q189108 (Tyrian purple)

**Military Facet Analysis:**
- Claim: "Tyrian purple used to distinguish military commanders"
- Insight: "Purple stripe on toga = centurion rank"
- Confidence: 0.85
- Facet: military

**Political Facet Analysis:**
- Claim: "Tyrian purple indicated senatorial rank"
- Insight: "Purple toga border = political authority"
- Confidence: 0.92
- Facet: political

**Economic Facet Analysis:**
- Claim: "Tyrian purple trade route from Phoenicia"
- Insight: "High-value commodity, trade monopoly"
- Confidence: 0.88
- Facet: economic

**Scientific Facet Analysis:**
- Claim: "Tyrian purple extracted from murex snail"
- Insight: "Biological source: Murex brandaris"
- Confidence: 0.95
- Facet: scientific

**Cultural Facet Analysis:**
- Claim: "Tyrian purple symbolized prestige in Roman culture"
- Insight: "Color symbolism, social status marker"
- Confidence: 0.90
- Facet: cultural

### Why Sequential Facet Analysis Works

1. **Same data, multiple lenses:** One ontology examined from 5+ perspectives
2. **No interference:** Each facet gets clean read without cross-contamination
3. **Comprehensive coverage:** Ensures all facet-relevant insights extracted
4. **Claim richness:** Generates 5x more claims than single-facet analysis

---

## Complete Purple to Mollusk Workflow

**This is the GOLD STANDARD for cross-domain discovery:**

### Phase 1: Un-Faceted Discovery
```
Military agent anchors on Q17167 (Roman Republic)
  ↓ (P31 traversal)
Discovers Q191172 (Roman senator)
  ↓ (backlink)
Discovers Q172645 (toga)
  ↓ (P31 traversal)
Discovers Q189108 (Tyrian purple)
  ↓ (backlink)
Discovers Q191989 (murex) ⭐

Result: Shell nodes created (NO facets assigned yet)
```

### Approval Point
```
Human reviews:
- 15 nodes discovered
- 23 edges found
- Purple → mollusk path validated
- Strength score: 0.88

Decision: ✅ APPROVED
```

### Phase 2: Facet-by-Facet Analysis
```
SCA adopts MILITARY facet:
  Q191989 (murex) → "Dye trade for military insignia" (confidence: 0.80)

SCA adopts POLITICAL facet:
  Q191989 (murex) → "Source of senatorial purple" (confidence: 0.92)

SCA adopts ECONOMIC facet:
  Q191989 (murex) → "High-value trade commodity" (confidence: 0.88)

SCA adopts SCIENTIFIC facet:
  Q191989 (murex) → "Murex brandaris biology" (confidence: 0.95)

SCA adopts CULTURAL facet:
  Q191989 (murex) → "Symbol of prestige" (confidence: 0.90)

Result: 5 claims about murex, each from different facet perspective
```

**Starting from military domain → discovered biological entity → analyzed from 5 facets!**

---

## Backlinks Function: Critical for Discovery

### What Are Backlinks?

**Backlinks** = reverse triple discovery in Wikidata

```cypher
// Forward triple (normal):
Q17167 (Roman Republic) -[:P31]-> Q7275 (state)

// Backlink (reverse):
Q191172 (Roman senator) -[:P31]-> Q17167 (Roman Republic)
                                   ↑ This is a backlink TO Roman Republic
```

### Why Backlinks Matter

1. **Discover Related Entities:**
   - "What links TO this concept?" (not just "What does this link to?")
   - Example: Q189108 (Tyrian purple) ← Q191989 (murex) [via P279 or P31]

2. **Cross-Domain Bridges:**
   - Backlinks reveal **unexpected connections**
   - Example: Academic articles about Roman history might mention murex shells in context of purple dye trade
   - These connections wouldn't be found by forward traversal alone

3. **Authority Validation:**
   - If concept is linked TO by many high-quality sources → high confidence
   - Backlinks from featured Wikipedia articles, academic sources → validation

4. **Completeness:**
   - Forward traversal only sees what Wikidata modelers added as properties
   - Backlinks see what OTHER entities reference this one
   - Example: Q17167 (Roman Republic) has P31 properties, but also is referenced by hundreds of other entities (people, events, places)

### Backlinks in Action

```python
# Discover hierarchy from Roman Republic (forward)
hierarchy = agent.discover_hierarchy_from_entity('Q17167', depth=2)
# Result: 50 entities (P31/P279/P361 chains)

# Discover backlinks TO Roman Republic (reverse)
backlinks = agent.fetch_wikidata_backlinks('Q17167', properties=['P31', 'P279', 'P361', 'P17', 'P131'])
# Result: 3,847 entities that REFERENCE Roman Republic
# Includes: senators, battles, buildings, modern books, archaeological sites, etc.

# Filter backlinks by P31 (instance_of)
accepted = filter_backlinks_by_class(backlinks, accept_classes=['Q5', 'Q178561', 'Q11424'])
# Result: 2,318 accepted (people, events, places)
# Rejected: 1,529 (modern organizations, disambiguation pages, etc.)

# Shell nodes created: 2,318 lightweight nodes
# Cost: Minimal (just graph writes, no LLM calls yet)
```

---

## Shell Node Pattern

### What Is a Shell Node?

A **shell node** is a lightweight placeholder created during breadth exploration.

**Characteristics:**
- Has SubjectConcept node in Neo4j
- Has basic metadata:
  * `label`: "Tyrian purple"
  * `qid`: "Q189108"
  * `facet`: "material_culture"
  * `status`: "shell"
  * `discovered_by`: "military_agent_20260215"
  * `discovery_method`: "backlink_from_Q172645"
- **Empty properties:** No full claims yet (deferred)
- **No LLM expansion:** No cost incurred

### When Is a Shell Node Expanded?

Shell nodes are expanded on-demand:

1. **User Query:** "Tell me about Tyrian purple"
   - System detects shell node
   - Instantiates a specialized MaterialCultureAgent
   - Agent expands the node with full claims

2. **Agent Assignment:** Admin creates "textile_agent" and assigns it domain including "Q189108"
   - Agent expands all shell nodes in its domain
   - Converts shell → full node with properties

3. **Training Mode:** Agent is training on material culture domain
   - Encounters shell node Q189108
   - Expands it as part of systematic domain coverage

### Benefits of Shell Nodes

1. **Cost Efficiency:**
   - Create 2,000 shell nodes: ~$0.00 (graph writes only)
   - Expand 2,000 nodes immediately: ~$50-100 (LLM calls for each)
   - **Save 99% of cost** by deferring expansion

2. **Semantic Horizon:**
   - Graph "knows about" 2,000 concepts
   - Can route queries correctly ("Tyrian purple" → material_culture agent)
   - Even before full expansion

3. **Lazy Loading:**
   - Expand only what's needed
   - 80% of shell nodes may never be queried
   - No wasted LLM cost

4. **Breadth-First Strategy:**
   - Discover widely across domains FIRST
   - Prioritize expansion based on:
     * User demand (most queried)
     * Agent coverage (fill gaps)
     * Authority signals (high-confidence sources)

---

## Integration with Steps 5-6

### Step 5: Subject Ontology Proposal (with Shell Nodes)

```python
def propose_subject_ontology(session_id: str) -> Dict:
    """
    Analyzes discovered hierarchies + backlinks
    
    Returns:
        {
            'core_classes': [
                {'class': 'Military Leadership', 'nodes': 8},
                {'class': 'Military Operations', 'nodes': 12},
                {'class': 'Military Organization', 'nodes': 3}
            ],
            'shell_nodes': [
                {'qid': 'Q189108', 'label': 'Tyrian purple', 'facet': 'material_culture', 
                 'discovered_via': 'backlink', 'confidence': 0.85},
                {'qid': 'Q191989', 'label': 'murex', 'facet': 'scientific',
                 'discovered_via': 'P279_chain', 'confidence': 0.82},
                // ...+200 more shell nodes
            ],
            'cross_domain_links': [
                {'from': 'Q191172', 'to': 'Q189108', 'via': 'P31', 'bridge': True},
                {'from': 'Q189108', 'to': 'Q191989', 'via': 'backlink', 'bridge': True}
            ],
            'strength_score': 0.91,
            'reasoning': 'Discovered 3 core classes + 203 shell nodes via hierarchy + backlinks'
        }
    """
```

### Step 6: Wikipedia Training (Core + Shell Nodes)

```python
def discover_wikipedia_articles(proposed_ontology: Dict) -> List[str]:
    """
    LLM selects Wikipedia articles for BOTH core concepts AND shell nodes
    
    Core concepts: Full training (100+ sentences per article)
    Shell nodes: Light training (20-30 sentences, validate shell hypothesis)
    
    Returns:
        [
            'Julius_Caesar',          # Core (Military Leadership)
            'Battle_of_Pharsalus',    # Core (Military Operations)
            'Roman_legion',           # Core (Military Organization)
            'Tyrian_purple',          # Shell node validation
            'Murex',                  # Shell node validation
            'Toga',                   # Shell node validation
        ]
    """
```

---

## Key Takeaways

### Two-Phase Workflow

1. **Phase 1: Un-Faceted Exploration** (Initialize + Ontology Proposal)
   - Just hunting nodes and edges - NO facet lens
   - Hierarchy traversal (P31/P279/P361) + backlinks
   - Shell nodes created for ALL discoveries
   - Outputs proposed ontology → APPROVAL POINT

2. **Phase 2: Facet-by-Facet Analysis** (Training Mode)
   - SCA sequentially adopts facet roles (military → political → cultural → etc.)
   - Reads same claims from different facet perspectives
   - Generates facet-specific insights
   - 5x claim richness vs single-facet approach

### Critical Concepts

- **SCA is SEED AGENT** - breadth exploration, not depth
- **Un-faceted first** - discovers structure before applying facet lenses
- **Approval point** - human reviews ontology before facet analysis
- **Backlinks are CRITICAL** - reverse triple discovery enables cross-domain connections
- **Shell nodes** - lightweight placeholders for lazy expansion (cost efficient)
- **Sequential facets** - one facet at a time, analyzing same ontology repeatedly
- **No class limits** - ontology is EXPANSIVE (not constrained to 3-5 classes)
- **Purple to mollusk** - gold standard for cross-domain discovery (military → biology)

---

## Files Modified

- [STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md](STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md) - Added breadth exploration emphasis
- [STEP_5_COMPLETE.md](STEP_5_COMPLETE.md) - Clarified SCA as seed agent
- [STEP_6_DESIGN_WIKIPEDIA_TRAINING.md](STEP_6_DESIGN_WIKIPEDIA_TRAINING.md) - Removed class limitations
- [STEP_6_QUICK_REFERENCE.md](STEP_6_QUICK_REFERENCE.md) - Updated flow with shell nodes

---

**Status:** ✅ Documentation updated to reflect SCA seed agent pattern with breadth exploration, shell node creation, and backlinks function.
