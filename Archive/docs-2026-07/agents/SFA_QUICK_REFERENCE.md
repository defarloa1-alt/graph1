# SFA Quick Reference - Cheat Sheet

**Fast lookup for SFA components and workflows**

---

## SFA Anatomy

```
YourSFA
├── Inheritance: SubjectConceptFacetAgent
├── Phase 2: ClaimRegistry + PeerReviewer
├── Claude Model: claude-sonnet-4-20250514
└── Graph Tools: query_graph, get_threshold, get_decision_table
```

---

## Key Components

### 1. System Prompt (Automatic)
```
"You are SFA_MILITARY, a specialized Military historian..."
+ Graph schema hints
+ Relationship registry rules
+ Republic graph context (domain-specific)
```

### 2. User Prompts (You define)

**Facet Pack Evaluation:**
```
Domain seed: Roman Republic (Q17167)
Candidates: Battle of Cannae (Q36456), Second Punic War (Q35947)...
Tasks: Evaluate relevance, find missing concepts, propose links
```

**Subject Concept Analysis:**
```
Analyze: Battle of Cannae (Q36456)
Questions: Key aspects? Related topics? Relevant entities? Time periods?
```

### 3. Tools (Automatic)

| Tool | Purpose | Example |
|------|---------|---------|
| `query_graph` | Neo4j Cypher queries | `MATCH (sc {qid: 'Q36456'}) RETURN sc` |
| `get_threshold` | System thresholds | `sfa_proposal_confidence_default → 0.75` |
| `get_decision_table` | Decision rules | `D8 → Proposal confidence rules` |

### 4. Predicates (You define)

```python
MILITARY_PREDICATES = [
    'commanded_campaign',
    'participated_in_battle',
    'military_training',
    # ... 20-30 total
]
```

### 5. Wikidata Properties (You define)

```python
MILITARY_PROPERTIES = [
    'P607',  # conflict
    'P241',  # military branch
    'P598',  # commander of
    # ... 10-20 total
]
```

### 6. Evaluation Logic (You define)

```python
def evaluate_significance(entity, wikidata_props):
    confidence = 0.5  # Base
    
    if major_battle:
        confidence += 0.3
    if strategic_importance:
        confidence += 0.2
    
    return {'confidence': min(confidence, 1.0), 'factors': [...]}
```

---

## Core Methods

### Base Class (Inherited)

| Method | Purpose | Returns |
|--------|---------|---------|
| `accept_facet_pack()` | Evaluate candidate SubjectConcepts | Evaluation JSON |
| `analyze_subject_concept()` | Deep analysis of one concept | Analysis dict |
| `discover_related_entities()` | Find related entities via Wikidata | List of candidates |
| `bootstrap_context()` | Load system context | None (sets self.federations, self.entity_types) |

### Phase 2 (Your implementation)

| Method | Purpose | Returns |
|--------|---------|---------|
| `submit_[facet]_claim()` | Submit claim via ClaimRegistry | claim_id |
| `review_peer_claims()` | Review other facets' claims | Review summary dict |
| `evaluate_[facet]_significance()` | Score significance for facet | Confidence + factors |
| `enrich_from_wikidata()` | Fetch Wikidata properties | Property dict |

---

## Workflow Patterns

### Pattern 1: Evaluate Candidates

```python
# 1. Receive facet pack
pack = {
    'facet_delta': {'candidates': [...]},
    'domain_context': {'seed': {'qid': 'Q17167'}},
    'discipline_traversal': {...},
    'corpus_endpoints': {...}
}

# 2. Call SFA
result = military_sfa.accept_facet_pack(pack)

# 3. SFA internally:
#    - Builds prompt
#    - Calls Claude with tools
#    - Claude queries graph
#    - Claude returns evaluation JSON

# 4. Result contains:
{
    'relevant_candidates': ['Q36456', 'Q35947'],
    'misrouted': [],
    'proposed_additions': [...],
    'confidence': 0.92
}
```

### Pattern 2: Submit Claims

```python
# 1. Submit claim
claim_id = military_sfa.submit_military_claim(
    entity={'type': 'EVENT', 'qid': 'Q36456', 'label': 'Battle of Cannae'},
    predicate='major_battle',
    confidence=0.95
)

# 2. ClaimRegistry internally:
#    - Generates entity_cipher
#    - Checks for existing entity (QID-based)
#    - Creates/retrieves entity
#    - Creates Agent node
#    - Creates :ASSERTS edge with metadata

# 3. Result: 'military_sfa_001_ent_con_Q36456_MILITARY'
```

### Pattern 3: Peer Review

```python
# 1. Get entity cipher
entity_cipher = 'ent_con_Q36456'

# 2. Review claims
review = military_sfa.review_peer_claims(entity_cipher)

# 3. PeerReviewer internally:
#    - Finds claims from other facets
#    - Creates :REVIEWED edges
#    - Calculates agreement scores
#    - Auto-promotes/flags claims

# 4. Result:
{
    'entity_cipher': 'ent_con_Q36456',
    'reviewer': 'military_sfa_001',
    'reviews_submitted': 2,
    'contested_claims': []
}
```

---

## Prompt Templates

### Template 1: Facet Pack Evaluation

```
You are SFA_{FACET}, a specialized {Facet Label} historian.

Domain seed: {seed_label} ({seed_qid})
Facet: {facet_label} -- {evidence_summary}

Candidates ({count} total):
  - {candidate_1}
  - {candidate_2}
  ...

Academic disciplines:
  - {discipline_1}
  - {discipline_2}
  ...

Tasks:
1. Which candidates are genuinely relevant?
2. What concepts are MISSING?
3. Cross-facet relationships to propose?
4. Confidence this facet is active (0-1)?

Return JSON: relevant_candidates, misrouted, proposed_additions, cross_facet_links, confidence
```

### Template 2: Subject Analysis

```
Analyze this subject concept from a {Facet Label} perspective:

Subject: {label} (Wikidata {qid})

Questions:
1. Key {facet} aspects?
2. Related {facet} topics?
3. Relevant entities (people, events, places)?
4. Significant time periods?
5. Confidence this facet is relevant (0-1)?

Provide structured, scholarly analysis with sources.
```

### Template 3: Entity Discovery (SPARQL)

```sparql
SELECT DISTINCT ?item ?itemLabel ?description
WHERE {
  # Facet-specific filters
  ?item wdt:P??? wd:Q??? .
  ?item wdt:P??? ?value .
  
  # Optional filters
  FILTER(...) .
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

---

## Response Formats

### Facet Pack Evaluation Response

```json
{
  "relevant_candidates": ["Q36456", "Q35947"],
  "misrouted": ["Q123456"],
  "proposed_additions": [
    {"qid": "Q789", "label": "...", "reason": "..."}
  ],
  "cross_facet_links": [
    {"from_qid": "Q36456", "to_qid": "Q123", "relationship": "...", "target_facet": "..."}
  ],
  "confidence": 0.92
}
```

### Subject Analysis Response

```json
{
  "key_aspects": ["aspect1", "aspect2"],
  "related_topics": ["topic1", "topic2"],
  "relevant_entities": [
    {"qid": "Q5471", "label": "Hannibal", "role": "commander"}
  ],
  "time_periods": ["218-201 BCE"],
  "confidence": 0.95,
  "reasoning": "..."
}
```

### Claim Submission Response

```python
claim_id = "military_sfa_001_ent_con_Q36456_MILITARY"
# Format: {agent_id}_{entity_cipher}_{facet}
```

### Peer Review Response

```python
{
    'entity_cipher': 'ent_con_Q36456',
    'reviewer': 'military_sfa_001',
    'reviews_submitted': 2,
    'contested_count': 0,
    'contested_claims': []
}
```

---

## Claude Tool Usage Example

```
USER: Evaluate Battle of Cannae

ASSISTANT: [tool_use: query_graph]
{
  "cypher": "MATCH (sc:SubjectConcept {wikidata_qid: 'Q36456'}) RETURN sc"
}

USER: [tool_result]
{
  "sc": {
    "label": "Battle of Cannae",
    "wikidata_qid": "Q36456"
  }
}

ASSISTANT: [tool_use: get_threshold]
{
  "name": "sfa_proposal_confidence_default"
}

USER: [tool_result]
{
  "value": 0.75
}

ASSISTANT: [final_response]
{
  "relevant": true,
  "confidence": 0.95,
  "reasoning": "Major military engagement, Hannibal's tactical masterpiece..."
}
```

---

## File Locations

```
scripts/agents/
├── subject_concept_facet_agents.py   ← Base class
├── claim_registry.py                 ← Phase 2: Claims
├── peer_reviewer.py                  ← Phase 2: Reviews
├── military/
│   ├── __init__.py
│   ├── agent.py                      ← Military SFA
│   └── README.md
└── diplomatic/
    ├── __init__.py
    ├── agent.py                      ← Diplomatic SFA
    └── README.md
```

---

## Configuration

### Required Environment Variables

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
ANTHROPIC_API_KEY=sk-ant-...
```

### Initialization

```python
from neo4j import GraphDatabase
from scripts.agents.military.agent import MilitarySFA

# 1. Create driver
driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
)

# 2. Create SFA
military_sfa = MilitarySFA(driver)

# 3. Use it
result = military_sfa.submit_military_claim(...)
```

---

## Testing

```bash
# Run tests for a specific SFA
pytest scripts/tests/test_military_sfa.py -v
pytest scripts/tests/test_diplomatic_sfa.py -v

# Run all SFA tests
pytest scripts/tests/test_*_sfa.py -v
```

---

## Checklist: Creating a New SFA

- [ ] Create package: `scripts/agents/[facet]/`
- [ ] Define `FACET_PREDICATES` (20-30)
- [ ] Define `FACET_PROPERTIES` (10-20 Wikidata)
- [ ] Implement `__init__()` (inherit from base, set facet_key/label)
- [ ] Implement `submit_[facet]_claim()`
- [ ] Implement `review_peer_claims()`
- [ ] Implement `evaluate_[facet]_significance()`
- [ ] Implement `enrich_from_wikidata()`
- [ ] Override `_build_analysis_prompt()` (optional)
- [ ] Override `_build_wikidata_discovery_query()` (optional)
- [ ] Create test suite (13 tests)
- [ ] Create README with examples
- [ ] Run tests (all must pass)
- [ ] Document predicates and properties

---

## Common Patterns

### Query Graph for Existing Entity

```python
cypher = """
    MATCH (e {qid: $qid})
    RETURN e.entity_cipher, e.label, labels(e)
"""
```

### Get Agreement Score

```python
agreement = peer_reviewer.get_agreement_score(
    entity_cipher='ent_con_Q36456',
    claim_predicate='major_battle',
    facet='MILITARY'
)
```

### Find Contested Claims

```python
contested = peer_reviewer.find_contested_claims('ent_con_Q36456')
# Returns claims with disagreement
```

### Enrich from Wikidata

```python
props = diplomatic_sfa.enrich_from_wikidata('Q170185')
# Returns: {'P710': [...], 'P793': [...], ...}
```

---

## Quick Debug

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('scripts.agents.claim_registry')
```

### Inspect Tool Calls

```python
# Tool calls are logged in the response
result = military_sfa.accept_facet_pack(pack)
print(result['evaluation']['tool_calls'])
```

### Check Token Usage

```python
result = military_sfa.accept_facet_pack(pack)
print(result['evaluation']['usage'])
# {'input_tokens': 1234, 'output_tokens': 567}
```

---

## Resources

- **Base SFA Code:** `scripts/agents/subject_concept_facet_agents.py`
- **Military SFA:** `scripts/agents/military/agent.py`
- **Diplomatic SFA:** `scripts/agents/diplomatic/agent.py`
- **Full Guide:** `SFA_PROMPTS_AND_PROCEDURES.md`
- **Status Update:** `SFA_STATUS_UPDATE.md`

---

**Quick Tip:** Start by reading an existing SFA (Military or Diplomatic) to see the pattern, then create your own by copying the structure and customizing the predicates, properties, and evaluation logic.
