# FACET REFERENCE LAYER: Phase 4-5 Discipline Framework

## Your Insight

> "For phase 4 and 5 a facet is typically a discipline, which means there must be a way for LLM to understand the major concept categories of a facet. For example economics - supply demand production, frameworks macroeconomic and microecon concepts. I believe there can be a canonical per facet reference subgraph."

**Exactly right.** Each facet is a discipline with canonical concept categories that should be represented as a reference subgraph in Neo4j.

---

## The Problem Solved

### Before (Without Facet Reference)
```
EconomicAgent analyzes: "Evidence of large-scale taxation and fiscal systems"

No discipline framework:
  ✗ Agent doesn't understand that taxation is MACROECONOMIC (not microeconomic)
  ✗ Can't distinguish between supply-demand vs resource allocation concepts
  ✗ Might propose incoherent sub-concepts
  ✗ Risk of hallucination (creating concepts outside discipline)
```

### After (With Facet Reference)
```
EconomicAgent analyzes same finding

With discipline framework:
  ✓ Agent checks against 5 canonical categories
  ✓ Recognizes "taxation" → Macroeconomic Systems
  ✓ Validates against Roman ontology (also Macroeconomic)
  ✓ Proposes "Roman Republic--Taxation and State Revenue" (coherent)
  ✓ No hallucination (bounded by canonical framework)
```

---

## Architecture: 3-Layer Ontology

### Layer 1: FACET REFERENCE (Discipline Knowledge)
```
FacetReference(Economic)
  ├─ ConceptCategory: Supply & Demand
  ├─ ConceptCategory: Production & Resource Allocation
  ├─ ConceptCategory: Macroeconomic Systems
  ├─ ConceptCategory: Microeconomic Actors
  └─ ConceptCategory: Trade & Commerce

FacetReference(Military)
  ├─ ConceptCategory: Strategy & Tactics
  ├─ ConceptCategory: Logistics & Supply
  ├─ ConceptCategory: Weaponry & Technology
  ├─ ConceptCategory: Battles & Combat
  └─ ConceptCategory: Leadership & Organization
```

**Created by**: Discipline scholars/domain experts
**Scope**: One per facet (17 total)
**Update frequency**: Rarely (established disciplines)
**Query pattern**: `MATCH (f:FacetReference {facet: "Economic"})-[:CONTAINS]->(cat:ConceptCategory)`

### Layer 2: CIVILIZATION ONTOLOGIES (Trained from Wikipedia)
```
Roman Republic Economic Ontology:
  ├─ Roman Republic--Economy (maps to → Production & Resource Allocation)
  ├─ Roman Republic--Trade and Commerce (maps to → Trade & Commerce)
  ├─ Roman Republic--Coinage and Monetary Systems (maps to → Macroeconomic Systems)
  ├─ Roman Republic--Taxation and State Revenue (maps to → Macroeconomic Systems)
  └─ Roman Republic--Labor Systems (maps to → Microeconomic Actors)

Ancient Egypt Economic Ontology:
  ├─ Ancient Egypt--Economy (maps to → Production & Resource Allocation)
  ├─ Ancient Egypt--Trade Networks (maps to → Trade & Commerce)
  ├─ Ancient Egypt--State Revenue and Taxation (maps to → Macroeconomic Systems)
  └─ ...etc
```

**Created by**: Agent training pipeline (Wikipedia parsing)
**Scope**: One per civilization+facet
**Update frequency**: Can retrain anytime
**Query pattern**: `MATCH (root:SubjectConcept {subject_id: "..."})-[:HAS_TRAINED_AGENT]->(agent:FacetAgent {facet: "Economic"})`

### Layer 3: SUBJECT CONCEPT REGISTRY (Specific Instances)
```
SubjectConcept:Roman Republic
  ├─ Claim: "Large-scale taxation evidence..."
  ├─ Claim: "Trade network discovered..."
  ├─ Sub-concept: "Roman Republic--Taxation and State Revenue" (proposed)
  └─ Sub-concept: "Roman Republic--Trade Networks" (proposed)
```

**Created by**: GPT Phase 2A+2B analysis
**Scope**: Individual claims + discovered sub-concepts
**Update frequency**: Per discovery run
**Query pattern**: Standard Neo4j subject-claim queries

---

## Data Model: Facet Reference Node

```json
{
  "node_type": "FacetReference",
  "properties": {
    "facet": "Economic",
    "created_date": "2026-02-15T00:00:00Z",
    "source": "Canonical discipline knowledge",
    "version": "1.0"
  },
  "relationships": {
    "CONTAINS": [
      {
        "node_type": "ConceptCategory",
        "id": "econ_001",
        "label": "Supply & Demand",
        "description": "Market mechanisms, scarcity, price signals",
        "key_topics": ["supply", "demand", "price", "scarcity", "equilibrium"],
        "discipline_basis": "Fundamental economics (Smith, Ricardo)"
      },
      ...5 categories per facet
    ]
  }
}
```

---

## Agent Initialization: 3-Step Process

### Step 1: Load Canonical Categories
```python
# Agent receives facet assignment
agent = EconomicAgent(
    civilization="Roman Republic",
    facet="Economic"
)

# Query Neo4j for canonical framework
categories = loader.get_facet_categories("Economic")
# Returns: Supply & Demand, Production, Macroeconomics, Microeconomics, Trade

agent.canonical_categories = categories
```

### Step 2: Load Civilization Ontology
```python
# Query trained Wikipedia ontology
civilization_ontology = loader.get_trained_ontology(
    subject_concept_id="subj_37decd8454b1",
    facet="Economic"
)
# Returns: Roman Republic economic sub-concepts + pattern mappings

agent.civilization_ontology = civilization_ontology
```

### Step 3: Ready for Analysis
```python
agent.analyze_finding("Evidence of taxation systems and tribute collection")

# Agent processes through:
# 1. Canonical framework: Check which economic category
# 2. Civilization ontology: Cross-reference with Roman patterns
# 3. Result: Coherent sub-concept proposal
```

---

## Analysis Flow: 4-Step Pipeline

### Step 1: Match Canonical Framework
```
Finding: "Large-scale taxation and state resource redistribution"

Check against 5 economic categories:
  Supply & Demand: 0 matches (no price/market concepts)
  Production: 1 match (resources)
  Macroeconomic Systems: 3 matches ✓ PRIMARY (taxation, system, state)
  Microeconomic: 0 matches
  Trade: 0 matches

Result: MACROECONOMIC SYSTEMS (60% confidence based on keyword match)
```

### Step 2: Cross-Reference Civilization Ontology
```
Roman ontology for "Macroeconomic Systems" category:
  ├─ Roman Republic--Coinage and Monetary Systems
  ├─ Roman Republic--Taxation and State Revenue ✓ MATCHES
  └─ (other macro concepts)

Check civilization patterns:
  "Taxation and State Revenue" has patterns: [taxation, tax, tribute, revenue, fiscal]
  Finding contains: [taxation, tribute] → 50% pattern match

Result: Civilization subconcept exists and matches reasonably well
```

### Step 3: Coherence Validation
```
Canonical framework says: Macroeconomic Systems
Civilization ontology says: Also Macroeconomic Systems

✓ COHERENT: Both layers agree
→ Can safely use existing Roman Republic--Taxation and State Revenue

If they disagreed: Use primary canonical, but flag as secondary interpretation
```

### Step 4: Propose Sub-Concept
```
Proposal:
  {
    "label": "Roman Republic--Taxation and State Revenue",
    "facet": "Economic",
    "confidence": 0.59 (average of layers),
    "canonical_category": "Macroeconomic Systems",
    "grounding": "Discipline framework + Civilization ontology",
    "evidence_keywords": ["taxation", "tribute", "state", "redistribution"]
  }

Ready to load to Neo4j or mark as duplicate if already exists.
```

---

## Example: Complete Analysis Output

**Finding**: "Evidence of large-scale taxation systems, tribute collection from provinces, and centralized fiscal administration"

**Analysis Result**:
```
✓ Layer 1 (Canonical): Macroeconomic Systems (38% keyword match)
✓ Layer 2 (Civilization): Roman Republic--Taxation and State Revenue
✓ Layer 3 (Coherence): Both layers agree
✓ Sub-Concept Proposal: "Roman Republic--Taxation and State Revenue"
   Confidence: 0.59 (grounded in both canonicial + civilization)
```

**Without Facet Reference (Risky)**:
```
Finding mentions: "taxation", "tribute", "system"
Keyword matching alone:
  ? Could be Supply & Demand (if "market" mentioned)
  ? Could be Trade (if "exchange" mentioned)
  ? Could be Production (if "resources" mentioned)
  ? High hallucination risk
```

---

## 17 Facets: Canonical Categories Needed

Currently Defined (8 facets):
- ✅ Economic (5 categories)
- ✅ Military (5 categories)
- ✅ Political (5 categories)
- ✅ Social (5 categories)
- ✅ Religious (5 categories)
- ✅ Artistic (5 categories)
- ✅ Technological (5 categories)
- ✅ Geographic (5 categories)

Still Needed (9 facets):
- ⏳ Diplomatic (5 categories suggested)
- ⏳ Legal (5 categories suggested)
- ⏳ Literary (5 categories suggested)
- ⏳ Biographical (5 categories suggested)
- ⏳ Chronological (5 categories suggested)
- ⏳ Philosophical (5 categories suggested)
- ⏳ Communicational (5 categories suggested)
- ⏳ Agricultural (5 categories suggested)
- ⏳ Epidemiological (5 categories suggested)

**Standard**: 5 major concept categories per facet = 85 total canonical concepts

---

## Neo4j Schema

### Constraints
```cypher
CREATE CONSTRAINT facet_reference_unique
ON (f:FacetReference) ASSERT f.facet IS UNIQUE;

CREATE CONSTRAINT concept_category_unique
ON (c:ConceptCategory) ASSERT c.id IS UNIQUE;
```

### Indexes
```cypher
CREATE INDEX facet_index
FOR (f:FacetReference) ON (f.facet);

CREATE INDEX category_facet_index
FOR (c:ConceptCategory) ON (c.facet);

CREATE INDEX category_topics_index
FOR (c:ConceptCategory) ON (c.key_topics);
```

### Relationships
```cypher
FacetReference-[:CONTAINS]->ConceptCategory
  └─ Represents discipline structure
     One FacetReference per facet
     5 ConceptCategories per facet
```

---

## Integration with Phase 2A+2B

### Updated GPT Prompt Template

```markdown
## AGENT: Economic Analyst for Roman Republic

### Your Discipline Framework (Layer 1: Canonical)

Economics has 5 major concept categories:

1. Supply & Demand
   - Market mechanisms, scarcity, equilibrium
   - Keywords: supply, demand, price, market, equilibrium
   
2. Production & Resource Allocation
   - Manufacturing, agriculture, distribution
   - Keywords: production, agriculture, manufacturing, resources
   
3. Macroeconomic Systems
   - Aggregate economy, fiscal policy, monetary systems
   - Keywords: economy, taxation, money, trade relationships, inflation
   
4. Microeconomic Actors
   - Individual merchants, producers, workers
   - Keywords: merchant, producer, craftspeople, consumer, labor
   
5. Trade & Commerce
   - Exchange networks, commercial routes
   - Keywords: trade, commerce, routes, exchange, networks

### Roman Republic Context (Layer 2: Civilization)

Your trained ontology recognizes these Roman economic concepts:
- Economy (matches Production & Resource Allocation)
- Trade and Commerce (matches Trade & Commerce)
- Coinage and Monetary Systems (matches Macroeconomic Systems)
- Taxation and State Revenue (matches Macroeconomic Systems)
- Labor Systems (matches Microeconomic Actors)

### Analysis Instructions

When you find evidence about Roman economy:
1. Check which canonical category matches the evidence keywords
2. Cross-reference with your trained Roman sub-concepts
3. If both layers agree, propose that sub-concept with high confidence
4. If layers differ, use canonical framework as primary guide
5. Always ground proposals in both discipline knowledge AND civilization specifics
```

---

## Benefits Summary

| Aspect | Without | With Facet Reference |
|--------|---------|---------------------|
| **Discipline Understanding** | Keywords only | Structured concept categories |
| **Sub-Concept Coherence** | Scattered | All proposals within discipline |
| **Hallucination Risk** | Medium (unbounded) | Low (bounded by canonical) |
| **Cross-Civilization Consistency** | Different per civilization | Same framework (Econ is Econ everywhere) |
| **Analysis Quality** | Pattern matching | Informed categorization |
| **Knowledge Transfer** | No transfer | Roman econ patterns inform other civilizations |
| **Scalability** | Limited | Scales to all 17 facets × all civilizations |

---

## Files Created

### Code
- ✅ `facet_reference_subgraph.py` (490 lines)
  - FacetReferenceLoader class
  - All 8 facets defined with categories
  - Neo4j schema + CRUD operations
  - Agent initialization example

- ✅ `example_agent_analysis_with_facet_reference.py` (400 lines)
  - Complete analysis pipeline
  - Shows 3-step validation
  - Demonstrates coherence checking
  - 5 example findings + proposals

### Documentation
- ✅ `FACET_REFERENCE_SUBGRAPH_ARCHITECTURE.md` (550 lines)
  - Complete architectural guide
  - Why this layer is essential
  - Full design explanation
  - Integration with Phase 2A+2B

---

## Next Steps

### Phase 1: Setup (1-2 hours)
- [ ] Load all 8 facet references to Neo4j
- [ ] Verify schema + constraints
- [ ] Test queries

### Phase 2: Complete Remaining Facets (2-3 hours)
- [ ] Define Diplomatic, Legal, Literary, Biographical, Chronological, Philosophical, Communicational, Agricultural, Epidemiological
- [ ] Load to Neo4j
- [ ] Verify all 17 facets

### Phase 3: Integration (1-2 hours)
- [ ] Update agent initialization to load facet categories
- [ ] Test with one agent (EconomicAgent)
- [ ] Verify finding analysis

### Phase 4: Phase 2A+2B Update (2-3 hours)
- [ ] Update GPT prompts with canonical categories
- [ ] Test with sample findings
- [ ] Run full Phase 2A+2B with facet-aware agents

---

## Key Insight (Your Observation)

**You said**: "A facet is typically a discipline, which means there must be a way for LLM to understand the major concept categories."

**This is the solution**: 
- Define canonical categories per facet (in Neo4j)
- Agents load these during initialization
- Use them to validate/ground all proposals
- Result: Discipline-coherent, hallucination-resistant analysis

Every facet becomes a represented discipline within the knowledge graph, not just a label.

---

## Architecture Summary

```
                    AGENT INITIALIZATION
                    
                    ├─ Facet: "Economic"
                    │
        ┌───────────┴──────────────┐
        │                          │
    Layer 1                    Layer 2
    CANONICAL                 CIVILIZATION
    FacetReference            Trained Ontology
    ├─ Supply & Demand        ├─ Economy
    ├─ Production             ├─ Trade
    ├─ Macroeconomics ────────→ Taxation ✓
    ├─ Microeconomics         ├─ Coinage
    └─ Trade                  └─ Labor
        │                          │
        │        ┌────────────────┐
        │        │                │
        │   FINDING ANALYSIS      │
        │   "Taxation evidence"   │
        │        │                │
        │   ┌────▼────────────────┘
        │   │
        │   ├─ Canonical match: Macroeconomic Systems
        │   ├─ Civilization match: Taxation & Revenue
        │   ├─ Coherence: ✓ BOTH AGREE
        │   │
        │   └─ PROPOSAL:
        │      Label: Roman Republic--Taxation and State Revenue
        │      Confidence: 0.59
        │      Grounding: Discipline framework + Civilization
```

**Result**: Well-grounded, coherent, hallucination-resistant proposals.
