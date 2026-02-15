# Chrystallum Multi-Agent Facet Framework

**Status:** Production Ready  
**Date:** February 15, 2026  
**Purpose:** 17 specialized agents for facet-specific knowledge discovery and querying

---

## Architecture Overview

```
Chrystallum Multi-Agent System (Feb 15, 2026)

┌─────────────────────────────────────────────────────────────┐
│                    DISCOVERY LAYER                           │
│  Phase 2.5 Stage 1: Book Discovery (All 17 Facets)          │
│  - BookDiscoveryAgent (Perplexity API)                       │
│  - 7-indicator scoring algorithm                             │
│  - Parallel facet discovery                                  │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              QUERY EXECUTION LAYER                           │
│  Router → Facet Agents → Results → Aggregator               │
│  - MultiAgentRouter (determines facet relevance)             │
│  - 17 FacetAgent instances (parallel execution)              │
│  - Result deduplication & aggregation                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              CLAIM GENERATION LAYER                          │
│  Proposal Mode: Generate files, never write to DB            │
│  - Facet-specific claim validation                           │
│  - Automatic facet assignment                                │
│  - Audit trail logging                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 17 Facet Agents

Each agent has:
- **System prompt** with domain expertise
- **Key Wikidata anchors** for validation
- **Query patterns** specific to domain
- **Validation rules** for claims

### Facet Registry

| Key | Label | Definition | Authority |
|-----|-------|-----------|-----------|
| military | Military | Warfare, battles, commanders, strategy | Q8473, Q198, Q192781 |
| political | Political | States, rulers, governance, succession | Q3624078, Q3024240 |
| economic | Economic | Trade, currency, systems, finance | Q8134, Q7406919 |
| religious | Religious | Religion, belief, institutions, clergy | Q9174, Q16970 |
| social | Social | Classes, kinship, family, status | Q49773, Q189290 |
| cultural | Cultural | Cultures, identity, movements | Q11042, Q1792644 |
| artistic | Artistic | Art, architecture, aesthetic styles | Q968159, Q32880 |
| intellectual | Intellectual | Philosophy, ideas, schools | Q192110, Q4663903 |
| linguistic | Linguistic | Languages, writing, scripts | Q315, Q34770 |
| geographic | Geographic | Regions, territories, borders | Q1620908, Q6256 |
| environmental | Environmental | Climate, ecology, disasters | Q7937, Q8072 |
| technological | Technological | Tools, innovations, technology | Q11016, Q8148 |
| demographic | Demographic | Population, migration, urbanization | Q8436, Q61509 |
| diplomatic | Diplomatic | Diplomacy, treaties, relations | Q187947, Q131569 |
| scientific | Scientific | Science, theories, paradigms | Q336, Q11862829 |
| archaeological | Archaeological | Sites, artifacts, material culture | Q1190554, Q839954 |
| communication | Communication | Messages, rhetoric, propaganda | Q11029, Q1047 |

---

## File Structure

```
scripts/agents/
├── facet_agent_framework.py          ← Base FacetAgent + Router
├── book_discovery_agent.py            ← Phase 2.5 Stage 1 discovery
├── query_executor_agent_test.py       ← Original (still functional)
└── README.md                          ← This file

facet_agent_system_prompts.json        ← 17 system prompts (root)

tmp/
├── book_rankings_*.json               ← Output from discovery
├── book_rankings_*.md                 ← Human-readable rankings
└── PHASE_2_5_DISCOVERY_SUMMARY_*.json ← Summary across all facets
```

---

## Usage

### 1. Single Facet Agent (Query Mode)

```python
from scripts.agents.facet_agent_framework import FacetAgentFactory

# Create military agent
military_prompt = """Your expertise:
- Warfare, battles, military campaigns...
[full system prompt loaded from JSON]"""

agent = FacetAgentFactory.create_agent(
    facet_key="military",
    facet_label="Military",
    system_prompt=military_prompt
)

# Query
result = agent.query("Show me battles in 49 BCE")
print(result)

# Propose claim
agent.propose_claim(
    entity_id="Q181098",  # Battle of Cannae
    relationship_type="OCCURRED_IN",
    target_id="Y-0216",   # Year 216 BCE
    confidence=0.95,
    label="Battle of Cannae in 216 BCE",
    subject_qid="Q17167"  # Roman Republic
)

agent.close()
```

### 2. Multi-Agent Router (Automatic Facet Routing)

```python
from scripts.agents.facet_agent_framework import (
    FacetAgentFactory, MultiAgentRouter
)

# Create all 17 agents
agents = FacetAgentFactory.create_all_agents()

# Create router
router = MultiAgentRouter(agents)

# Auto-detect relevant facets
query = "What was the military and political response to Caesar's assassination?"
facet_keys, reasoning = router.route_query(query)

print(f"Routed to: {facet_keys}")
print(f"Reasoning: {reasoning}")

# Execute across multiple agents
results = router.execute_multi_facet(query, facet_keys)

print(results)

# Cleanup
router.close_all()
```

### 3. Phase 2.5 Book Discovery (Parallel)

```bash
# Run from command line
cd c:\Projects\Graph1
python scripts\phase_2_5_discovery_runner.py

# Or in Python
from scripts.phase_2_5_discovery_runner import DiscoveryPhase25Runner

runner = DiscoveryPhase25Runner()

# Discover across all 17 facets (parallel)
summary = runner.discover_all_facets(parallel=True, max_workers=3)

# Export results
summary_file = runner.export_summary(summary)

print(f"Results: {summary_file}")
```

---

## Phase 2.5 Workflow

### Stage 1: Book Discovery (Feb 15-18)

**Agent:** `BookDiscoveryAgent` (Perplexity API)

**Process:**
1. For each facet, query library catalogs:
   - Internet Archive
   - HathiTrust
   - Library of Congress
2. Score by 7-indicator algorithm:
   - English language (weight 1.0)
   - Full text available (weight 1.0)
   - Index presence (weight 0.8)
   - Publication year (weight 0.6)
   - Academic authority (weight 0.9)
   - Page count 300-600pp (weight 0.5)
   - Historical closeness (weight 0.7)
3. Export rankings per facet
4. Team reviews top books, selects 5-7 pilots

**Output:**
- `tmp/book_rankings_*.json` (per facet)
- `tmp/book_rankings_*.md` (human-readable)
- `tmp/PHASE_2_5_DISCOVERY_SUMMARY_*.json` (aggregated)

**Timeline:** Feb 15-18 (3 days)

### Stage 2: Index Extraction (Feb 19-22)

**Agent:** Manual + OCR  
**Input:** Pilot books (5-7 selected)  
**Process:**
1. Extract table of contents
2. OCR index (>95% accuracy)
3. Parse entities from index entries
4. Link to Wikidata QIDs

**Output:** Structured index JSON files  
**Timeline:** Feb 19-22 (4 days)

### Stage 3: Claim Generation (Mar 3-10)

**Agent:** All 17 facet agents (Proposal Mode)  
**Input:** Extracted indexes  
**Process:**
1. For each index entry:
   - Parse entity + relationships
   - Assign to appropriate facet(s)
   - Generate Cypher proposal (file-based)
2. Deduplicate claims across facets
3. Calculate posteriors for each claim

**Output:** JSON proposal files + logs  
**Timeline:** Mar 3-10 (1 week)

### Stage 4: Validation + Promotion (Mar 10-15)

**Agent:** Historian team + validation service  
**Input:** Proposed claims  
**Process:**
1. Historian review (facet-specific)
2. Validate against existing graph
3. Promote if posterior ≥ 0.90
4. Log all decisions

**Output:** Promoted claims in Neo4j  
**Success criteria:** 1,500-2,500 claims promoted by Mar 15  
**Timeline:** Mar 10-15 (5 days)

---

## Domain-Specific Features

### Military Agent
- Knows battlefield terminology (phalanx, legionnaire, cohort, etc.)
- Validates military history experts (P101=military history)
- Routes military events to correct facets
- Example: "Battle of Cannae" is military-primary+ political secondary

### Political Agent
- Understands succession logic (heir → ruler)
- Knows government structures per period
- Validates rulers and state entities
- Example: "Augustus" succeeded "Caesar" (not the same as inheriting)

### Economic Agent
- Knows trade route networks
- Understands monetary systems
- Validates commerce relationships
- Example: "Silk Route" ← time period constraint

### Religious Agent
- Maps religions to belief systems
- Validates clergy as religious authorities
- Distinguishes sect/denomination/organization
- Example: Christianity ≠ Christ (person vs concept)

### Social Agent
- Understands class hierarchies
- Validates kinship relationships
- Maps social movements to periods
- Example: "Patrician" = social class; "Octavian" = patrician person

---

## Configuration

### Environment Variables

```bash
# Required
NEO4J_PASSWORD=your_neo4j_password
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...

# Optional
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_DATABASE=neo4j
```

### System Prompts

Loaded from: `facet_agent_system_prompts.json`

Each facet has:
- Expertise description
- Key Wikidata anchors
- Query patterns
- Validation rules
- Important distinctions (what NOT to do)

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Agent init | 100-200ms | Schema discovery + Neo4j conn |
| Query generation | 500-1000ms | ChatGPT call (gpt-3.5-turbo) |
| Cypher execution | 50-200ms | Depends on query complexity |
| Claim proposal | 200-500ms | File generation + JSON validation |
| Book discovery | 5-30s/facet | Perplexity API call |
| 7-indicator scoring | <100ms/book | Local calculation |

---

## Validation Rules

### Per-Facet Validation

**Military:**
- Battles must have date (Year node)
- Military leaders must have expertise (P101)
- Conflicts must map to Q198 or subclass

**Political:**
- Rulers must have title/office
- Succession must be logical
- States must have temporal bounds

**Economic:**
- Trade routes must connect places
- Currency must be period-specific
- Economic systems must have dates

*[Similar for all 17 facets]*

---

## Error Handling

All agents implement:
- Try/except on API calls
- Graceful fallbacks on parsing errors
- Logging to console + file
- Result validation before return

---

## Next Steps

1. **Deploy agents to Perplexity + OpenAI** ✓ (This release)
2. **Run Phase 2.5 Stage 1** (Feb 15-18)
   - `python scripts/phase_2_5_discovery_runner.py`
3. **Team selects pilot books** (Feb 18)
4. **Index extraction** (Feb 19-22)
5. **Claim generation** (Mar 3-10)
6. **Validation + promotion** (Mar 10-15)
7. **Go/No-go decision** (Mar 15)

---

## Support & Troubleshooting

**Issue:** Agents not found  
**Solution:** `FacetAgentFactory.create_all_agents()` requires `facet_agent_system_prompts.json` in root

**Issue:** Perplexity API rate limit  
**Solution:** Run discovery with `max_workers=1` (sequential instead of parallel)

**Issue:** Neo4j connection timeout  
**Solution:** Check `NEO4J_URI` and credentials. Run verification:
```python
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('✓ Connected')
```

---

**Last updated:** February 15, 2026  
**Framework version:** 1.0  
**Status:** Production Ready
