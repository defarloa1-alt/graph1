
# Subject Concept Agents - Complete Guide

**Version:** 1.0  
**Date:** 2026-02-20  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [18 Canonical Facets](#18-canonical-facets)
4. [Python Agents](#python-agents)
5. [Cypher Operations](#cypher-operations)
6. [Workflows](#workflows)
7. [Quick Start](#quick-start)
8. [Examples](#examples)
9. [API Reference](#api-reference)

---

## Overview

Subject Concept Agents (SCA) are specialized AI agents that analyze and enrich **SubjectConcepts** in the Chrystallum knowledge graph from 18 different scholarly perspectives (facets).

### What are SubjectConcepts?

SubjectConcepts are **thematic anchors** for organizing historical knowledge:
- **Examples:** "Roman Republic", "Ancient Greek Philosophy", "Mediterranean Trade"
- **Purpose:** Provide conceptual organization beyond individual entities
- **Structure:** Each SubjectConcept has a primary facet and 0-3 related facets

### What are Facet Agents?

Each facet agent analyzes SubjectConcepts from a specialized disciplinary perspective:
- **MILITARY Agent:** Analyzes warfare, battles, strategy aspects
- **POLITICAL Agent:** Analyzes governance, rulers, states
- **ECONOMIC Agent:** Analyzes trade, currency, economic systems
- *...and 15 more specialized agents*

### Key Features

✅ **On-demand agent creation** (not all 1,422 upfront)  
✅ **Stateless operation** (bootstrap from Chrystallum system graph)  
✅ **Multi-authority federation** (Wikidata, LCSH, FAST, LCC)  
✅ **Evidence-based proposals** (human approval workflow)  
✅ **Perplexity API integration** (online reasoning and sources)  
✅ **Wikidata SPARQL queries** (hierarchical discovery)

---

## Architecture

### System Structure

```
Chrystallum (root)
  └── SubjectConceptRoot
      ├── SubjectConceptRegistry (manages all SubjectConcepts)
      │   └── SubjectConcept nodes (79 current, growing)
      └── AgentRegistry (manages all agents)
          └── Agent nodes (3 current, max 1,422 possible)
```

### On-Demand Agent Model

**Potential:** 79 SubjectConcepts × 18 Facets = **1,422 possible agents**  
**Actually created:** Only when needed  
**Currently:** 3 agents active

**Agent ID Pattern:** `SFA_{subject_id}_{facet_key}`

**Example:**
```
SubjectConcept: subj_roman_republic_q17167
Primary Facet: POLITICAL
Related Facets: MILITARY, SOCIAL, ECONOMIC

Agents Created (on-demand):
  - SFA_subj_roman_republic_q17167_POLITICAL
  - SFA_subj_roman_republic_q17167_MILITARY
  - SFA_subj_roman_republic_q17167_SOCIAL
```

### Data Flow

```
Discovery → Classification → Enrichment → Validation → Approval
    ↓            ↓              ↓            ↓           ↓
[Wikidata]  [Perplexity]   [LCSH/FAST]  [Scoring]  [Neo4j]
```

---

## 18 Canonical Facets

### Full List (UPPERCASE ONLY)

| Facet | Description | Example Focus |
|-------|-------------|---------------|
| **ARCHAEOLOGICAL** | Sites, artifacts, material culture | Pompeii excavations |
| **ARTISTIC** | Art, architecture, aesthetics | Hellenistic sculpture |
| **BIOGRAPHIC** | Individual lives, genealogy | Julius Caesar's life |
| **COMMUNICATION** | Messaging, propaganda, media | Roman Senate speeches |
| **CULTURAL** | Identity, movements, symbols | Greek cultural identity |
| **DEMOGRAPHIC** | Population, migration, settlement | Roman colonization |
| **DIPLOMATIC** | Treaties, alliances, negotiations | Peace of Nicias |
| **ECONOMIC** | Trade, currency, markets | Mediterranean trade networks |
| **ENVIRONMENTAL** | Climate, ecology, nature | Mediterranean agriculture |
| **GEOGRAPHIC** | Regions, territories, zones | Italian peninsula |
| **INTELLECTUAL** | Philosophy, ideas, schools | Stoicism, Platonism |
| **LINGUISTIC** | Languages, scripts, writing | Latin language |
| **MILITARY** | Warfare, battles, strategy | Punic Wars |
| **POLITICAL** | States, rulers, governance | Roman Senate |
| **RELIGIOUS** | Faith, institutions, clergy | Roman religion |
| **SCIENTIFIC** | Science, theories, paradigms | Greek mathematics |
| **SOCIAL** | Class, kinship, family | Roman social hierarchy |
| **TECHNOLOGICAL** | Innovation, tools, engineering | Roman aqueducts |

### Forbidden Facets (Never Use)

❌ **TEMPORAL** - Use temporal properties instead  
❌ **CLASSIFICATION** - Use LCC/FAST instead  
❌ **PATRONAGE** - Use ECONOMIC or SOCIAL  
❌ **GENEALOGICAL** - Use BIOGRAPHIC

---

## Python Agents

### File: `scripts/agents/subject_concept_facet_agents.py`

Provides 18 specialized facet agents with:
- Perplexity API reasoning
- Wikidata SPARQL queries
- Entity discovery
- Proposal creation

### Classes

#### `SubjectConceptFacetAgent` (Base Class)

Base agent for all facet analysis.

```python
from scripts.agents.subject_concept_facet_agents import SubjectConceptAgentFactory
from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(USER, PASSWORD))

# Create single facet agent
military_agent = SubjectConceptAgentFactory.create_agent(
    facet_key="MILITARY",
    neo4j_driver=driver,
    perplexity_api_key=PERPLEXITY_KEY
)

# Analyze a subject concept
analysis = military_agent.analyze_subject_concept("subj_roman_republic_q17167")
print(analysis['analysis']['content'])
```

#### Specialized Agents

- `MilitaryFacetAgent` - Warfare analysis
- `PoliticalFacetAgent` - Governance analysis  
- `EconomicFacetAgent` - Trade analysis
- *More can be added following the same pattern*

#### `SubjectConceptAgentFactory`

Creates facet agents on demand.

```python
# Create all 18 agents
all_agents = SubjectConceptAgentFactory.create_all_agents(
    neo4j_driver=driver,
    perplexity_api_key=PERPLEXITY_KEY
)

# Access specific agent
political_agent = all_agents['POLITICAL']
```

#### `MultiFacetSubjectAnalyzer`

Analyzes subjects across multiple facets.

```python
from scripts.agents.subject_concept_facet_agents import MultiFacetSubjectAnalyzer

analyzer = MultiFacetSubjectAnalyzer(
    neo4j_driver=driver,
    perplexity_api_key=PERPLEXITY_KEY
)

# Analyze from all 18 facets
full_analysis = analyzer.analyze_subject_all_facets("subj_roman_republic_q17167")

# Analyze from selected facets
selected_analysis = analyzer.analyze_subject_selected_facets(
    subject_concept_id="subj_roman_republic_q17167",
    facet_keys=["MILITARY", "POLITICAL", "ECONOMIC"]
)
```

---

## Cypher Operations

### File: `Cypher/subject_concept_operations.cypher`

Comprehensive Cypher queries for:
- Creating SubjectConcepts
- Linking to authorities (LCSH, FAST, LCC)
- Building hierarchies
- Managing agents
- Temporal tethering
- Statistical reporting

### Key Queries

#### Create SubjectConcept

```cypher
CREATE (sc:SubjectConcept {
  subject_id: 'subj_roman_republic_q17167',
  label: 'Roman Republic',
  primary_facet: 'POLITICAL',
  related_facets: ['MILITARY', 'SOCIAL', 'ECONOMIC'],
  qid: 'Q17167',
  lcsh_id: 'sh85115087',
  fast_id: 'fst01204885',
  lcc_class: 'DG241-269',
  status: 'approved',
  confidence: 0.95
})
RETURN sc;
```

#### Find SubjectConcepts by Facet

```cypher
MATCH (sc:SubjectConcept {primary_facet: 'MILITARY'})
RETURN sc.subject_id, sc.label, sc.confidence
ORDER BY sc.confidence DESC;
```

#### Get Agents for SubjectConcept

```cypher
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (agent:Agent)-[:ANALYZES]->(sc)
RETURN agent.id, agent.facet, agent.status
ORDER BY agent.facet;
```

#### Link to Temporal Backbone

```cypher
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (start_year:Year {year: -509})
MATCH (end_year:Year {year: -27})
MERGE (sc)-[:STARTS_IN_YEAR]->(start_year)
MERGE (sc)-[:ENDS_IN_YEAR]->(end_year)
RETURN sc, start_year, end_year;
```

---

## Workflows

### File: `scripts/agents/subject_concept_workflow.py`

Complete orchestration pipelines.

### 1. Discovery Workflow

Discover new SubjectConcepts via Wikidata backlinks.

```python
from scripts.agents.subject_concept_workflow import SubjectConceptDiscoveryWorkflow

discovery = SubjectConceptDiscoveryWorkflow(
    neo4j_driver=driver,
    perplexity_api_key=PERPLEXITY_KEY,
    output_dir="output/subject_proposals"
)

# Discover from seed QIDs
proposals = discovery.run_full_workflow(
    seed_qids=['Q17167', 'Q1747689', 'Q11768'],
    limit_per_seed=50,
    save=True
)

# Output: JSON proposals file in output/subject_proposals/
```

**Workflow Steps:**
1. Query Wikidata backlinks from seeds
2. Classify candidates with Perplexity
3. Filter by confidence >= 0.7
4. Create proposals with status='pending_approval'
5. Save to JSON for human review

### 2. Enrichment Workflow

Enrich existing SubjectConcepts with authority federation.

```python
from scripts.agents.subject_concept_workflow import SubjectConceptEnrichmentWorkflow

enrichment = SubjectConceptEnrichmentWorkflow(
    neo4j_driver=driver,
    fast_data_path="Python/fast/key/FASTTopical_parsed.csv",
    lcc_data_path="Subjects/lcc_flat.csv"
)

# Enrich single SubjectConcept
result = enrichment.enrich_subject_concept("subj_roman_republic_q17167")

# Output: enrichment dict with FAST/LCC matches
```

**Workflow Steps:**
1. Load FAST and LCC indexes from local files
2. Match SubjectConcept labels to authorities
3. Update Neo4j properties
4. Create authority relationship links

---

## Quick Start

### Prerequisites

```bash
pip install neo4j requests python-dotenv
```

### Configuration

Create `config.py`:

```python
NEO4J_URI = "neo4j+s://your-instance.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your-password"
PERPLEXITY_API_KEY = "your-perplexity-key"
```

### Step 1: Bootstrap Infrastructure

Run the Cypher bootstrap script:

```bash
# In Neo4j Browser or via neo4j-admin
# Execute: Cypher/bootstrap_subject_concept_agents.cypher
```

This creates:
- SubjectConceptRoot and registries
- 18 Canonical Facets
- 6 Sample SubjectConcepts
- 3 Sample Agents

### Step 2: Create Facet Agents

```python
from scripts.agents.subject_concept_facet_agents import SubjectConceptAgentFactory
from neo4j import GraphDatabase
from config import *

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Create specific agent
military_agent = SubjectConceptAgentFactory.create_agent(
    facet_key="MILITARY",
    neo4j_driver=driver,
    perplexity_api_key=PERPLEXITY_API_KEY
)

# Bootstrap from Chrystallum
military_agent.bootstrap_context()

# Analyze
analysis = military_agent.analyze_subject_concept("subj_roman_republic_q17167")
print(analysis)
```

### Step 3: Run Discovery Workflow

```python
from scripts.agents.subject_concept_workflow import SubjectConceptDiscoveryWorkflow

discovery = SubjectConceptDiscoveryWorkflow(
    neo4j_driver=driver,
    perplexity_api_key=PERPLEXITY_API_KEY
)

proposals = discovery.run_full_workflow(
    seed_qids=['Q17167'],  # Roman Republic
    limit_per_seed=20
)

# Review proposals in output/subject_proposals/
```

### Step 4: Approve and Load

Review JSON proposals, then load to Neo4j:

```python
# Load approved proposals
from scripts.agents.sca_agent import SCAAgent

sca = SCAAgent(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

# Load single proposal
sca.load_proposal_to_neo4j(approved_proposal)
```

---

## Examples

### Example 1: Create All 18 Agents

```python
agents = SubjectConceptAgentFactory.create_all_agents(driver, PERPLEXITY_API_KEY)

print(f"Created {len(agents)} agents:")
for facet, agent in agents.items():
    print(f"  {facet}: {agent.agent_id}")
```

### Example 2: Multi-Facet Analysis

```python
analyzer = MultiFacetSubjectAnalyzer(driver, PERPLEXITY_API_KEY)

# Analyze Roman Republic from Military, Political, Economic perspectives
analysis = analyzer.analyze_subject_selected_facets(
    subject_concept_id="subj_roman_republic_q17167",
    facet_keys=["MILITARY", "POLITICAL", "ECONOMIC"]
)

for facet, result in analysis['facet_analyses'].items():
    print(f"\n{facet} Analysis:")
    print(result['analysis']['content'][:500])
```

### Example 3: Discover Related Entities

```python
military_agent = SubjectConceptAgentFactory.create_agent("MILITARY", driver, PERPLEXITY_API_KEY)

# Discover military figures related to Roman Republic
humans = military_agent.discover_related_entities(
    subject_concept_id="subj_roman_republic_q17167",
    entity_type="Human"
)

print(f"Found {len(humans)} military figures:")
for human in humans[:5]:
    print(f"  - {human['label']} ({human['qid']})")
```

### Example 4: Bulk Discovery from Seeds

```python
discovery = SubjectConceptDiscoveryWorkflow(driver, PERPLEXITY_API_KEY)

# Ancient history seeds
seeds = [
    'Q17167',   # Roman Republic
    'Q1747689', # Ancient Rome
    'Q11768',   # Ancient Greece
    'Q11772',   # Byzantine Empire
    'Q11764'    # Hellenistic period
]

proposals = discovery.run_full_workflow(seeds, limit_per_seed=30)

print(f"Created {proposals['proposal_count']} proposals")
```

---

## API Reference

### SubjectConceptFacetAgent

#### Methods

**`bootstrap_context()`**  
Load system context from Chrystallum (federations, entity types).

**`analyze_subject_concept(subject_concept_id: str) -> Dict`**  
Analyze SubjectConcept from facet perspective.

**`discover_related_entities(subject_concept_id: str, entity_type: str) -> List[Dict]`**  
Discover entities via Wikidata SPARQL.

**`create_entity_proposal(entity_type, qid, label, properties, confidence) -> Dict`**  
Create entity proposal for SubjectConcept.

### SubjectConceptAgentFactory

#### Methods

**`create_agent(facet_key: str, neo4j_driver, perplexity_api_key) -> SubjectConceptFacetAgent`**  
Create single facet agent.

**`create_all_agents(neo4j_driver, perplexity_api_key) -> Dict`**  
Create all 18 facet agents.

### MultiFacetSubjectAnalyzer

#### Methods

**`analyze_subject_all_facets(subject_concept_id: str) -> Dict`**  
Analyze from all 18 facets.

**`analyze_subject_selected_facets(subject_concept_id, facet_keys) -> Dict`**  
Analyze from selected facets.

### SubjectConceptDiscoveryWorkflow

#### Methods

**`discover_from_seed(seed_qids: List[str], limit_per_seed: int) -> List[Dict]`**  
Discover candidates from Wikidata backlinks.

**`classify_candidates(candidates: List[Dict]) -> List[Dict]`**  
Classify with Perplexity.

**`create_proposals(classified_candidates: List[Dict]) -> Dict`**  
Create SubjectConcept proposals.

**`run_full_workflow(seed_qids, limit_per_seed, save) -> Dict`**  
Complete discovery pipeline.

### SubjectConceptEnrichmentWorkflow

#### Methods

**`enrich_subject_concept(subject_id: str) -> Dict`**  
Enrich with FAST/LCC authorities.

---

## Best Practices

### 1. Facet Selection

✅ **DO:** Choose primary facet that best represents the subject's **dominant** characteristic  
✅ **DO:** Add 0-3 related facets for secondary perspectives  
❌ **DON'T:** Add all facets - be selective  
❌ **DON'T:** Use forbidden facets (TEMPORAL, CLASSIFICATION, etc.)

### 2. Agent Creation

✅ **DO:** Create agents on-demand (when needed for analysis)  
✅ **DO:** Reuse existing agents  
❌ **DON'T:** Create all 1,422 agents upfront  
❌ **DON'T:** Create duplicate agents

### 3. Proposal Review

✅ **DO:** Review all proposals before loading to Neo4j  
✅ **DO:** Check confidence scores (>=0.7 recommended)  
✅ **DO:** Verify Wikidata QIDs are correct  
❌ **DON'T:** Auto-approve without human review

### 4. Authority Federation

✅ **DO:** Link to multiple authorities (Wikidata + LCSH + FAST + LCC)  
✅ **DO:** Use Wikidata as primary identity (QID)  
✅ **DO:** Use library standards (LCSH/FAST/LCC) for classification  
❌ **DON'T:** Rely on single authority source

---

## Troubleshooting

### Issue: "Invalid facet" error

**Cause:** Facet key not uppercase or not in canonical list  
**Solution:** Use UPPERCASE facet keys from canonical list

```python
# Wrong
agent = factory.create_agent("military", driver)  

# Correct
agent = factory.create_agent("MILITARY", driver)
```

### Issue: "PERPLEXITY_API_KEY not set"

**Cause:** API key not configured  
**Solution:** Set in config.py or environment

```python
# Option 1: config.py
PERPLEXITY_API_KEY = "pplx-xxx"

# Option 2: Environment variable
export PERPLEXITY_API_KEY="pplx-xxx"
```

### Issue: Proposals not saving

**Cause:** Output directory doesn't exist  
**Solution:** Create directory or let workflow create it

```python
discovery = SubjectConceptDiscoveryWorkflow(
    neo4j_driver=driver,
    output_dir="output/subject_proposals"  # Will be created
)
```

---

## Roadmap

### Phase 1 (Complete) ✅
- 18 Canonical Facets defined
- Base agent framework
- Discovery workflow
- Enrichment workflow
- Neo4j operations

### Phase 2 (In Progress) 🔄
- Specialized agents for all 18 facets
- Advanced Wikidata queries per facet
- Confidence scoring algorithms
- Validation workflows

### Phase 3 (Planned) 📅
- Agent learning from user feedback
- Automated authority matching
- Batch operations for 79 SubjectConcepts
- Performance optimization

---

## Contributing

### Adding New Specialized Agents

1. Inherit from `SubjectConceptFacetAgent`
2. Override `_build_analysis_prompt()`
3. Override `_build_wikidata_discovery_query()`
4. Register in `SubjectConceptAgentFactory.SPECIALIZED_AGENTS`

Example:

```python
class ReligiousFacetAgent(SubjectConceptFacetAgent):
    def _build_analysis_prompt(self, subject_concept: Dict) -> str:
        # Custom religious analysis prompt
        pass
    
    def _build_wikidata_discovery_query(self, subject_id, entity_type) -> str:
        # Religious-specific SPARQL query
        pass
```

---

## License

[Your License Here]

---

## Support

**Issues:** GitHub Issues  
**Documentation:** This guide + inline code comments  
**Contact:** [Your Contact]

---

**Built with:** Neo4j, Python, Perplexity, Wikidata  
**Last Updated:** February 20, 2026  
**Version:** 1.0
