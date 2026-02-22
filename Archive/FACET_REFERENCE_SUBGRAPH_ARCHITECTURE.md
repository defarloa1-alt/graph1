# FACET REFERENCE SUBGRAPH
## Canonical Concept Categories per Discipline

**Core Concept**: Each of 17 facets needs **canonical concept categories** that represent the major themes within that discipline, discovered from disciplinary knowledge (textbooks, encyclopedias, expert frameworks).

---

## Why This Layer Is Essential

### The Problem

Agent needs to understand **Economic facet** but without structure:

```
❌ No discipline framework
   Agent just pattern-matches keywords
   "I see 'trade' → propose something about trade"
   No understanding of supply/demand vs production systems
   Risk of incoherent sub-concepts
```

### The Solution

**Two-layer ontology hierarchy**:

```
Layer 1: FACET REFERENCE (Canonical discipline knowledge)
         └─ Economic (discipline-specific major themes)
            ├─ Supply & Demand
            ├─ Production & Resource Allocation  
            ├─ Macroeconomic Systems
            ├─ Microeconomic Actors
            └─ Trade & Commerce

Layer 2: CIVILIZATION ONTOLOGIES (trained from Wikipedia)
         └─ Roman Republic Wikipedia ontology
            ├─ [Pattern matched to Supply & Demand]
            ├─ [Pattern matched to Production]
            ├─ [Pattern matched to Macroeconomic]
            ├─ [Pattern matched to Microeconomic]
            └─ [Pattern matched to Trade]
```

**Result**: Agent understands both **discipline structure** (canonical) AND **civilization specifics** (trained from Wikipedia).

---

## Architecture: Facet Reference Subgraph

### Neo4j Structure

```cypher
FacetReference {
  facet: "Economic"
  created_date: datetime
  source: "Canonical discipline knowledge"
}

└─ [:CONTAINS] → ConceptCategory {
     id: "econ_001"
     label: "Supply & Demand"
     description: "Market mechanisms, scarcity, price signals"
     key_topics: ["supply", "demand", "price", "scarcity", "equilibrium"]
     facet: "Economic"
   }

└─ [:CONTAINS] → ConceptCategory {
     id: "econ_002"
     label: "Production & Resource Allocation"
     description: "Manufacturing, agriculture, resource distribution"
     key_topics: ["production", "manufacturing", "agriculture"]
     facet: "Economic"
   }

... (5 total categories per facet)
```

### Query Pattern (Agent Initialization)

```cypher
// Agent loads canonical categories for its facet
MATCH (f:FacetReference { facet: "Economic" })
-[:CONTAINS]-> (cat:ConceptCategory)

RETURN 
  cat.label as category,
  cat.description as description,
  cat.key_topics as patterns
ORDER BY cat.label

// Returns 5 canonical categories ready for analysis
```

---

## Example: Economic Facet

### Canonical Concept Categories (Disciplinary Knowledge)

```json
{
  "facet": "Economic",
  "concept_categories": [
    {
      "id": "econ_001",
      "label": "Supply & Demand",
      "description": "Market mechanisms, scarcity, price signals",
      "key_topics": ["supply", "demand", "price", "scarcity", "equilibrium"],
      "discipline_basis": "Fundamental economic principle (Adam Smith, David Ricardo)"
    },
    {
      "id": "econ_002",
      "label": "Production & Resource Allocation",
      "description": "Manufacturing, agriculture, resource distribution",
      "key_topics": ["production", "manufacturing", "agriculture", "resources", "allocation"],
      "discipline_basis": "Economic production function (Cobb-Douglas)"
    },
    {
      "id": "econ_003",
      "label": "Macroeconomic Systems",
      "description": "Aggregate economy, trade, monetary systems, taxation",
      "key_topics": ["macroeconomics", "gdp", "trade", "money", "taxation", "inflation"],
      "discipline_basis": "Macroeconomic aggregation (Keynes, Friedman)"
    },
    {
      "id": "econ_004",
      "label": "Microeconomic Actors",
      "description": "Merchants, craftspeople, labor, business",
      "key_topics": ["merchants", "craftspeople", "labor", "business", "consumers"],
      "discipline_basis": "Microeconomic agents"
    },
    {
      "id": "econ_005",
      "label": "Trade & Commerce",
      "description": "Exchange networks, commercial routes, merchant guilds",
      "key_topics": ["trade", "commerce", "merchants", "routes", "exchange"],
      "discipline_basis": "Comparative advantage (Ricardo), trade theory"
    }
  ]
}
```

---

## Example: Military Facet

```json
{
  "facet": "Military",
  "concept_categories": [
    {
      "id": "mil_001",
      "label": "Strategy & Tactics",
      "description": "Military planning, battlefield tactics, campaign strategy",
      "key_topics": ["strategy", "tactics", "planning", "maneuvers", "campaigns"],
      "discipline_basis": "Military science (Sun Tzu, Clausewitz)"
    },
    {
      "id": "mil_002",
      "label": "Logistics & Supply",
      "description": "Supplies, transportation, provisions, bases",
      "key_topics": ["logistics", "supplies", "transportation", "provisions", "bases"],
      "discipline_basis": "Military logistics (Napoleon, modern warfare theory)"
    },
    {
      "id": "mil_003",
      "label": "Weaponry & Technology",
      "description": "Weapons, fortifications, military innovations",
      "key_topics": ["weapons", "fortifications", "technology", "armor", "siege"],
      "discipline_basis": "Military technology evolution"
    },
    {
      "id": "mil_004",
      "label": "Battles & Combat",
      "description": "Individual battles, engagements, military operations",
      "key_topics": ["battle", "combat", "engagement", "operation"],
      "discipline_basis": "Military history (specific conflicts)"
    },
    {
      "id": "mil_005",
      "label": "Leadership & Organization",
      "description": "Command structure, military hierarchy, leadership",
      "key_topics": ["leadership", "command", "hierarchy", "general", "organization"],
      "discipline_basis": "Military organization theory"
    }
  ]
}
```

---

## Full Set: 17 Facet Categories

### Currently Defined (facet_reference_subgraph.py)

1. **Economic** (5 categories)
   - Supply & Demand, Production, Macroeconomics, Microeconomics, Trade

2. **Military** (5 categories)
   - Strategy & Tactics, Logistics, Weaponry, Battles, Leadership

3. **Political** (5 categories)
   - Governance Structures, Legal Frameworks, Power & Succession, Factions, International Relations

4. **Social** (5 categories)
   - Class Systems, Kinship, Gender Roles, Ethnicity, Labor

5. **Religious** (5 categories)
   - Theology, Institutions, Ritual & Practice, Religious Movements, Sacred Texts

6. **Artistic** (5 categories)
   - Visual Arts, Performing Arts, Literary Arts, Movements, Artists & Patrons

7. **Technological** (5 categories)
   - Tools & Implements, Agricultural Technology, Construction, Manufacturing, Transportation

8. **Geographic** (5 categories)
   - Physical Geography, Political Geography, Population & Settlement, Resources, Exploration

### To Be Defined (Template)

9. **Diplomatic** (5 categories)
   - [Treaty & Alliance Frameworks, Negotiation & Mediation, etc.]

10. **Legal** (5 categories)
    - [Property & Rights, Crime & Punishment, Contract Law, etc.]

11. **Literary** (5 categories)
    - [Poetry & Drama, History & Documentation, Philosophy, Rhetoric, etc.]

12. **Biographical** (5 categories)
    - [Individual Achievement, Family & Lineage, Thought Leadership, etc.]

13. **Chronological** (5 categories)
    - [Period Definition, Historical Events, Time Measurement, Calendar Systems, etc.]

14. **Philosophical** (5 categories)
    - [Metaphysics, Epistemology, Ethics, Logic, Aesthetics, etc.]

15. **Communicational** (5 categories)
    - [Language & Linguistics, Writing Systems, Information Networks, Rhetoric, etc.]

16. **Agricultural** (5 categories)
    - [Crop Systems, Irrigation, Land Tenure, Animal Husbandry, etc.]

17. **Epidemiological** (5 categories)
    - [Disease Spread, Health Systems, Medicine & Cures, Mortality, etc.]

---

## Agent Initialization Flow

### Step 1: Agent Receives Facet Assignment
```
Agent Type: EconomicAgent
Civilization: Roman Republic
Facet: Economic
```

### Step 2: Load Canonical Categories
```python
# Query Neo4j
categories = loader.get_facet_categories("Economic")

# Returns 5 canonical categories:
# 1. Supply & Demand
# 2. Production & Resource Allocation
# 3. Macroeconomic Systems
# 4. Microeconomic Actors
# 5. Trade & Commerce
```

### Step 3: Load Civilization Ontology
```python
# Query trained wikipedia ontology for Roman Republic
civilization_ontology = loader.get_trained_ontology(
  subject_concept_id="subj_37decd8454b1",
  facet="Economic"
)

# Returns: Wikipedia-trained sub-concepts
# - Economy section
# - Trade and Commerce section
# - Coinage section
```

### Step 4: Map Civilization → Canonical
```
Roman Wikipedia Sub-Concepts    ← →    Canonical Categories

Economy                               Supply & Demand
Trade and Commerce                    Trade & Commerce
Coinage System                        Macroeconomic Systems
Labor Systems                         Microeconomic Actors
```

### Step 5: Agent Analyzes Evidence
```
Finding: "Evidence of large-scale grain storage and distribution networks"

Agent asks: "Which canonical category matches this?"
- Keywords: "storage", "distribution", "networks"
- Best match: "Supply & Demand" (price signals, distribution)
- Secondary: "Production & Resource Allocation" (resource management)
- Roman sub-concept: "Economy" or "Trade"

Result: Coherent categorization using discipline framework
```

---

## How Agent Uses Canonical Categories

### Pattern Matching Algorithm

```python
def categorize_finding(finding_text, canonical_categories):
    """
    Match finding against canonical framework.
    """
    matches = []
    
    for category in canonical_categories:
        # Check how many key_topics appear in finding
        matched_topics = [
            topic for topic in category["key_topics"]
            if topic in finding_text.lower()
        ]
        
        # Calculate confidence
        if matched_topics:
            confidence = len(matched_topics) / len(category["key_topics"])
            matches.append({
                "category": category["label"],
                "matched_topics": matched_topics,
                "confidence": confidence
            })
    
    # Sort by confidence
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "primary_category": matches[0]["category"],  # Best match
        "all_matches": matches,  # All matches ranked
        "coherent": True  # Always coherent within framework
    }
```

### Example: Finding Analysis

**Input**: "Evidence of systematic taxation, tribute collection, and redistribution of resources"

**Canonical Categories**:
1. Supply & Demand
2. Production & Resource Allocation
3. Macroeconomic Systems
4. Microeconomic Actors
5. Trade & Commerce

**Analysis**:
```
Supply & Demand: 0 matches (no price/demand keywords)
Production: 1 match (resource allocation) → 20%
Macroeconomic: 3 matches (taxation, redistribution, system) → 60% ⭐ PRIMARY
Microeconomic: 0 matches
Trade: 1 match (indirect) → 20%
```

**Result**: Finding categorized as **Macroeconomic Systems** with 60% confidence
- Agent proposes: "Roman Republic--Macroeconomic Taxation Framework"
- Discipline grounding: "This aligns with fiscal policy (macro-level)"
- Evidence keywords: [taxation, tribute, redistribution]

---

## Benefits of Facet Reference Layer

| Aspect | Without | With Facet Reference |
|--------|---------|---------------------|
| **Discipline Understanding** | Agent knows keywords | Agent knows discipline structure |
| **Sub-Concept Coherence** | Scattered proposals | All proposals fit discipline framework |
| **Inference Quality** | Generic pattern matching | Informed categorization |
| **Hallucination Risk** | Medium (no structure) | Low (bounded by canonical) |
| **Cross-Civilization Consistency** | Different per civilization | Same categories (Econ is Econ everywhere) |
| **Knowledge Transfer** | No overlap | Roman Economic agent helps understand Ming Economic patterns |

---

## Integration with Phase 2A+2B

### GPT Prompt Update

```markdown
## FACET REFERENCE KNOWLEDGE

You are an EconomicAgent for Roman Republic.

### Your Discipline Framework (Canonical Categories)

These are the major concept categories in Economics:

1. Supply & Demand
   - Market mechanisms, scarcity, price signals
   - Keywords: supply, demand, price, equilibrium
   
2. Production & Resource Allocation
   - Manufacturing, agriculture, distribution
   - Keywords: production, agriculture, manufacturing, resources
   
3. Macroeconomic Systems
   - Aggregate economy, trade, monetary systems, taxation
   - Keywords: economy, trade, taxation, money, inflation
   
4. Microeconomic Actors
   - Individual merchants, producers, consumers
   - Keywords: merchant, producer, consumer, business
   
5. Trade & Commerce
   - Exchange networks, routes, commerce
   - Keywords: trade, commerce, merchant, routes

### Civilizational Specifics

Roman Republic economic sub-concepts (trained from Wikipedia):
- Economy → typically Supply & Demand + Production
- Trade and Commerce → typically Trade & Commerce + Macroeconomics
- Coinage → Macroeconomic Systems

### When Analyzing Evidence

1. Check which canonical category matches keywords
2. Cross-reference with Roman sub-concepts
3. Propose coherent sub-concept within framework
4. Set confidence as MIN(finding_confidence, framework_alignment)

### Example

Finding: "Evidence of large-scale taxation and state resource redistribution"
Canonical match: Macroeconomic Systems (3/3 keywords: taxation, state, redistribution)
Roman sub-concept: Economy
Proposal: "Roman Republic--State Fiscal Systems"
Confidence: 0.82
```

---

## Implementation Steps

### Step 1: Define All 17 Facet Categories
- Economics ✅ (done: 5 categories)
- Military ✅ (done: 5 categories)
- Political ✅ (done: 5 categories)
- Social ✅ (done: 5 categories)
- Religious ✅ (done: 5 categories)
- Artistic ✅ (done: 5 categories)
- Technological ✅ (done: 5 categories)
- Geographic ✅ (done: 5 categories)
- Diplomatic (todo: 5 categories)
- Legal (todo: 5 categories)
- Literary (todo: 5 categories)
- Biographical (todo: 5 categories)
- Chronological (todo: 5 categories)
- Philosophical (todo: 5 categories)
- Communicational (todo: 5 categories)
- Agricultural (todo: 5 categories)
- Epidemiological (todo: 5 categories)

### Step 2: Load to Neo4j
```python
loader = FacetReferenceLoader(uri, user, password)
loader.create_facet_schema()
loader.load_all_facets()
```

### Step 3: Update Agent Initialization
```python
# Agent loads facet reference during init
agent = EconomicAgent(
    civilization="Roman Republic",
    facet_reference=loader.get_facet_categories("Economic")
)
```

### Step 4: Update Phase 2A+2B Prompts
Include canonical categories for each agent type

### Step 5: Test with One Agent
- Economic Agent for Roman Republic
- Analyze sample findings
- Verify categorization accuracy
- Check sub-concept proposals

---

## Query Examples

### Query 1: Get Canonical Categories for Facet
```cypher
MATCH (f:FacetReference { facet: "Economic" })
-[:CONTAINS]-> (cat:ConceptCategory)
RETURN cat.label, cat.description, cat.key_topics
ORDER BY cat.label
```

### Query 2: Find Category by Topic
```cypher
MATCH (cat:ConceptCategory)
WHERE "taxation" IN cat.key_topics
RETURN cat.label, cat.facet, cat.description
```

### Query 3: Connect to Civilization Ontology
```cypher
MATCH (f:FacetReference { facet: "Economic" })-[:CONTAINS]->(cat:ConceptCategory)
,      (civilization:SubjectConcept { label: "Roman Republic" })
       -[:HAS_TRAINED_ONTOLOGY]->(civoont:ConceptCategory { facet: "Economic" })

RETURN f.facet, cat.label as canonical, civoont.label as roman_specific
```

---

## Next Steps

1. ✅ Complete facet_reference_subgraph.py (8 facets defined)
2. ⏳ Define remaining 9 facet categories
3. ⏳ Create Neo4j Cypher schema file
4. ⏳ Create loader script for all facets
5. ⏳ Update agent initialization to query facet reference
6. ⏳ Update Phase 2A+2B prompts with canonical categories
7. ⏳ Test with Economic agent + sample findings

---

## Relationship to Other Ontology Layers

```
LAYER 1: FACET REFERENCE (this)
         Canonical concept categories per discipline
         ├─ 17 facets × 5 categories each = 85 canonical concepts
         
LAYER 2: CIVILIZATION ONTOLOGIES (trained from Wikipedia)
         Sub-concepts grounded in Wikipedia sections
         ├─ Roman Republic: 6-12 sub-concepts per facet
         ├─ Ancient Egypt: 6-12 sub-concepts per facet
         └─ etc.
         
LAYER 3: SUBJECT CONCEPT REGISTRY (existing)
         Individual concepts + claims
         ├─ SubjectConcepts (5 bootstrap bootstraps)
         ├─ Claims (40,000+)
         └─ Facet Claims (mapped to facets)

AGENT INIT:
├─ Facet (e.g., "Economic")
├─ Load Canonical Categories (facet reference)
├─ Load Civilization Ontology (trained Wikipedia)
├─ Load Subject Instances (registry)
└─ Ready to analyze findings coherently
```

**Key Insight**: Each layer adds specificity without losing coherence: Discipline → Civilization → Specific Instance
