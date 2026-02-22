# Subject Concept Agents - Quick Reference Card

**Version:** 1.0 | **Date:** 2026-02-20

---

## 📁 Files Created

```
scripts/agents/subject_concept_facet_agents.py    (680 lines)
scripts/agents/subject_concept_workflow.py        (500 lines)
scripts/agents/test_subject_concept_agents.py     (550 lines)
Cypher/subject_concept_operations.cypher          (650 lines)
Cypher/bootstrap_subject_concept_agents.cypher    (450 lines)
docs/SUBJECT_CONCEPT_AGENTS_GUIDE.md              (1,200 lines)
```

---

## 🎯 18 Canonical Facets (UPPERCASE ONLY)

```
ARCHAEOLOGICAL  ARTISTIC      BIOGRAPHIC     COMMUNICATION
CULTURAL        DEMOGRAPHIC   DIPLOMATIC     ECONOMIC
ENVIRONMENTAL   GEOGRAPHIC    INTELLECTUAL   LINGUISTIC
MILITARY        POLITICAL     RELIGIOUS      SCIENTIFIC
SOCIAL          TECHNOLOGICAL
```

**Forbidden:** ❌ TEMPORAL, CLASSIFICATION, PATRONAGE, GENEALOGICAL

---

## ⚡ Quick Start (5 Minutes)

### 1. Bootstrap Neo4j (one-time)
```cypher
// Execute in Neo4j Browser:
Cypher/bootstrap_subject_concept_agents.cypher
```

### 2. Test Setup
```bash
python scripts/agents/test_subject_concept_agents.py
```

### 3. Create Agent
```python
from scripts.agents.subject_concept_facet_agents import SubjectConceptAgentFactory
from neo4j import GraphDatabase
from config import *

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
agent = SubjectConceptAgentFactory.create_agent("MILITARY", driver, PERPLEXITY_API_KEY)
```

---

## 🔑 Key Python Classes

| Class | Purpose | Import |
|-------|---------|--------|
| `SubjectConceptFacetAgent` | Base agent | `subject_concept_facet_agents` |
| `SubjectConceptAgentFactory` | Create agents | `subject_concept_facet_agents` |
| `MultiFacetSubjectAnalyzer` | Multi-perspective analysis | `subject_concept_facet_agents` |
| `SubjectConceptDiscoveryWorkflow` | Find new subjects | `subject_concept_workflow` |
| `SubjectConceptEnrichmentWorkflow` | Link authorities | `subject_concept_workflow` |

---

## 💻 Common Code Snippets

### Create Single Agent
```python
agent = SubjectConceptAgentFactory.create_agent(
    facet_key="MILITARY",
    neo4j_driver=driver,
    perplexity_api_key=PERPLEXITY_API_KEY
)
```

### Create All 18 Agents
```python
agents = SubjectConceptAgentFactory.create_all_agents(driver, PERPLEXITY_API_KEY)
```

### Analyze Subject
```python
analysis = agent.analyze_subject_concept("subj_roman_republic_q17167")
print(analysis['analysis']['content'])
```

### Multi-Facet Analysis
```python
analyzer = MultiFacetSubjectAnalyzer(driver, PERPLEXITY_API_KEY)
result = analyzer.analyze_subject_selected_facets(
    "subj_roman_republic_q17167", 
    ["MILITARY", "POLITICAL"]
)
```

### Discovery Workflow
```python
discovery = SubjectConceptDiscoveryWorkflow(driver, PERPLEXITY_API_KEY)
proposals = discovery.run_full_workflow(
    seed_qids=['Q17167'], 
    limit_per_seed=50
)
```

---

## 🔍 Common Cypher Queries

### Find SubjectConcepts by Facet
```cypher
MATCH (sc:SubjectConcept {primary_facet: 'MILITARY'})
RETURN sc.subject_id, sc.label, sc.confidence
ORDER BY sc.confidence DESC;
```

### Get Agents for Subject
```cypher
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (agent:Agent)-[:ANALYZES]->(sc)
RETURN agent.id, agent.facet, agent.status;
```

### Create SubjectConcept
```cypher
CREATE (sc:SubjectConcept {
  subject_id: 'subj_example',
  label: 'Example Subject',
  primary_facet: 'POLITICAL',
  related_facets: ['MILITARY'],
  qid: 'Q12345',
  status: 'approved',
  confidence: 0.9
})
RETURN sc;
```

### Link to Year Backbone
```cypher
MATCH (sc:SubjectConcept {subject_id: 'subj_example'})
MATCH (start:Year {year: -500})
MATCH (end:Year {year: -400})
MERGE (sc)-[:STARTS_IN_YEAR]->(start)
MERGE (sc)-[:ENDS_IN_YEAR]->(end);
```

---

## 📊 Data Model

```
Chrystallum
  └── SubjectConceptRoot
      ├── SubjectConceptRegistry
      │   └── SubjectConcept (79 current, growing)
      │       ├── primary_facet (1 required)
      │       ├── related_facets (0-3 optional)
      │       ├── qid (Wikidata)
      │       ├── lcsh_id (Library of Congress)
      │       ├── fast_id (FAST)
      │       └── lcc_class (LCC)
      │
      └── AgentRegistry
          └── Agent (3 current, max 1,422)
              ├── id: SFA_{subject_id}_{facet}
              ├── facet (UPPERCASE)
              └── status (active/inactive)
```

---

## ✅ Prerequisites

1. **Neo4j** running with credentials in `config.py`
2. **Python 3.8+** with: `pip install neo4j requests`
3. **Perplexity API Key** (for analysis workflows)
4. **Authority files** (optional, for enrichment):
   - `Python/fast/key/FASTTopical_parsed.csv`
   - `Subjects/lcc_flat.csv`

---

## 🚀 Agent ID Pattern

```
Format: SFA_{subject_id}_{facet_key}

Examples:
  SFA_subj_roman_republic_q17167_MILITARY
  SFA_subj_roman_republic_q17167_POLITICAL
  SFA_subj_greek_philosophy_q192125_INTELLECTUAL
```

**Potential:** 79 subjects × 18 facets = 1,422 agents  
**Created:** On-demand only

---

## 📈 Workflow Summary

### Discovery
```
Wikidata Backlinks → Perplexity Classification → JSON Proposals → Human Review → Neo4j Load
```

### Enrichment
```
SubjectConcept → Match FAST/LCC → Update Properties → Link Authorities
```

### Analysis
```
SubjectConcept + Facet → Perplexity Reasoning → Analysis Results
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid facet" | Use UPPERCASE facet key from canonical list |
| "PERPLEXITY_API_KEY not set" | Add to `config.py` or environment |
| "Chrystallum not found" | Run bootstrap Cypher script first |
| "No SubjectConcepts found" | Run bootstrap Cypher script first |
| Proposals not saving | Check `output_dir` exists or let workflow create it |

---

## 📚 Documentation

**Full Guide:** `docs/SUBJECT_CONCEPT_AGENTS_GUIDE.md` (1,200 lines)  
**Build Summary:** `SUBJECT_CONCEPT_AGENTS_BUILD_SUMMARY.md`  
**This Card:** `SUBJECT_CONCEPT_AGENTS_QUICK_REF.md`

---

## 🧪 Run Tests

```bash
python scripts/agents/test_subject_concept_agents.py
```

**10 Tests:**
1. Neo4j connection
2. Chrystallum structure
3. 18 facets exist
4. SubjectConcepts exist
5. Create single agent
6. Create all 18 agents
7. Analyze subject (Perplexity)
8. Multi-facet analysis (Perplexity)
9. Discovery workflow (Wikidata)
10. Enrichment workflow (FAST/LCC)

---

## 💡 Common Use Cases

### 1. Analyze Subject from Military Perspective
```python
military = SubjectConceptAgentFactory.create_agent("MILITARY", driver, PERPLEXITY_KEY)
analysis = military.analyze_subject_concept("subj_roman_republic_q17167")
```

### 2. Find All Military SubjectConcepts
```cypher
MATCH (sc:SubjectConcept {primary_facet: 'MILITARY'})
RETURN sc.label, sc.qid
ORDER BY sc.confidence DESC;
```

### 3. Discover New Subjects from Roman Republic
```python
discovery = SubjectConceptDiscoveryWorkflow(driver, PERPLEXITY_KEY)
proposals = discovery.run_full_workflow(seed_qids=['Q17167'])
```

### 4. Get All Agents for a Subject
```cypher
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (agent:Agent)-[:ANALYZES]->(sc)
RETURN agent.facet;
```

---

## 🎓 Key Concepts

**SubjectConcept:** Thematic anchor for organizing knowledge (e.g., "Roman Republic")  
**Facet:** Scholarly perspective/discipline (e.g., MILITARY, POLITICAL)  
**Agent:** AI that analyzes SubjectConcepts from a facet perspective  
**On-Demand:** Agents created only when needed, not all upfront  
**Federation:** Linking to multiple authorities (Wikidata, LCSH, FAST, LCC)  
**Proposal:** Suggested change requiring human approval before Neo4j write

---

## 📞 Quick Help

**Can't connect to Neo4j?** Check `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` in `config.py`  
**Perplexity errors?** Verify `PERPLEXITY_API_KEY` is valid  
**No SubjectConcepts?** Run `Cypher/bootstrap_subject_concept_agents.cypher`  
**Need examples?** See `docs/SUBJECT_CONCEPT_AGENTS_GUIDE.md`

---

**Version:** 1.0 | **Status:** ✅ Production Ready | **Date:** 2026-02-20
