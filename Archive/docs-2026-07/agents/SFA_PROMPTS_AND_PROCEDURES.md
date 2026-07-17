# SFA Prompts and Procedures - Complete Guide

**Understanding how Subject Facet Agents work internally**

---

## Overview

Subject Facet Agents (SFAs) are **autonomous LLM-powered historians** that analyze entities and concepts from specialized perspectives. Each SFA uses Claude with tool access to the Neo4j graph, following structured procedures and prompts.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│  1. BASE CLASS: SubjectConceptFacetAgent                │
│     - System prompts                                     │
│     - Claude agentic loop                                │
│     - Graph tool access                                  │
│     - Wikidata SPARQL queries                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  2. PHASE 2 INTEGRATION                                  │
│     - ClaimRegistry (entity deduplication)               │
│     - PeerReviewer (cross-facet validation)              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  3. SPECIALIZED SFA: Military, Diplomatic, etc.          │
│     - Facet-specific predicates                          │
│     - Evaluation scoring logic                           │
│     - Wikidata property selection                        │
└─────────────────────────────────────────────────────────┘
```

---

## System Prompt Template

Every SFA starts with this base system prompt:

```python
# From subject_concept_facet_agents.py line 233-254
system = f"""
You are SFA_{facet_key}, a specialized {facet_label} historian 
evaluating candidates for the Chrystallum knowledge graph.

You have tools to query the live Neo4j graph. Use them to check 
existing nodes, decision tables, and thresholds before making judgments.

GRAPH SCHEMA HINTS (use these property names in Cypher):
- SubjectConcept: label, subject_id, wikidata_qid, lcsh_id, seed_qid, concept_cipher
- Facet: label (e.g. 'Military'), key is just the label
- SYS_DecisionTable: table_id (e.g. 'D8'), label, description
- SYS_Threshold: name, value, unit, description
- SYS_FederationSource: source_id, label, phase
- SYS_RelationshipType: rel_type, name, wikidata_property (query before proposing edges)
- Entity: label, qid, dprr_id
- Place: label, pleiades_id, geonames_id

RELATIONSHIP REGISTRY: All predicates must exist in 
relationship_types_registry_master.csv / SYS_RelationshipType. 
Query the graph or consult the CSV before proposing a relationship type.
Do not invent types.

IMPORTANT: Keep graph queries minimal. You already have the candidates 
in the prompt — focus on evaluating them, not re-discovering the graph. 
Return structured JSON.
"""
```

### System Prompt Enhancement

The system prompt is then enhanced with **Republic Graph Context** (specific to the Roman Republic domain):

```python
# From line 256
seed_qid = str(seed.get("qid", "Q17167")).strip().upper()
system = append_republic_graph_context(
    system, 
    seed_qid, 
    driver=self.driver, 
    facet=self.facet_key
)
```

---

## Main Procedures

### 1. Facet Pack Evaluation (`accept_facet_pack`)

**Purpose:** Evaluate candidate SubjectConcepts routed to this facet

**Input:** A "facet pack" containing:
- `facet_delta`: Candidates with QIDs, scores, signals
- `discipline_traversal`: Academic disciplines
- `corpus_endpoints`: 14 federation sources
- `domain_context`: Seed concept, LCSH tether

**Prompt Template:**

```python
# From _build_pack_evaluation_prompt() line 297-315
prompt = f"""
You are SFA_{facet_key}, a specialized {facet_label} historian.

Domain seed: {seed_label} ({seed_qid})
Facet: {facet_label} -- {evidence_summary}

Candidates ({count} total, showing top 20):
  - Battle of Cannae (Q36456) role=primary score=0.95 | military engagement; large casualty count; strategic significance
  - Second Punic War (Q35947) role=secondary score=0.87 | military conflict; multiple battles
  ...

Academic disciplines:
  - Military history (Q124734)
  - Ancient warfare (Q445566)
  ...

Tasks:
1. Which candidates are genuinely relevant to {facet_label}? Flag any mis-routed ones.
2. What within-facet concepts did the harvest MISS that should be added?
3. Any cross-facet relationships worth proposing?
4. Confidence that this facet is active for this domain (0-1)?

Provide structured JSON with keys: 
  relevant_candidates, misrouted, proposed_additions, cross_facet_links, confidence.
"""
```

**Expected JSON Response:**

```json
{
  "relevant_candidates": ["Q36456", "Q35947"],
  "misrouted": ["Q123456"],
  "proposed_additions": [
    {
      "qid": "Q789",
      "label": "Battle of Zama",
      "reason": "Final battle of Second Punic War, military significance"
    }
  ],
  "cross_facet_links": [
    {
      "from_qid": "Q36456",
      "to_qid": "Q123",
      "relationship": "influenced",
      "target_facet": "POLITICAL"
    }
  ],
  "confidence": 0.92
}
```

---

### 2. Subject Concept Analysis (`analyze_subject_concept`)

**Purpose:** Deep analysis of a single SubjectConcept from this facet's perspective

**Input:** `subject_concept_id` (e.g., "SC_001")

**Prompt Template:**

```python
# From _build_analysis_prompt() line 366-379
prompt = f"""
Analyze this subject concept from a {facet_label} perspective:

Subject: {label} (Wikidata {qid})

Questions:
1. What are the key {facet_label.lower()} aspects of this subject?
2. What related {facet_label.lower()} topics should be explored?
3. What entities (people, events, places) are relevant from a {facet_label.lower()} viewpoint?
4. What time periods are significant for {facet_label.lower()} analysis?
5. Confidence in this facet being relevant (0-1)?

Provide structured, scholarly analysis with sources.
"""
```

**Example for Military SFA analyzing "Second Punic War":**

```
Analyze this subject concept from a Military perspective:

Subject: Second Punic War (Wikidata Q35947)

Questions:
1. What are the key military aspects of this subject?
   → Campaigns, battles, strategy, tactics, commanders
   
2. What related military topics should be explored?
   → Roman military reforms, Carthaginian elephant warfare, naval battles
   
3. What entities (people, events, places) are relevant from a military viewpoint?
   → Hannibal, Scipio Africanus, Battle of Cannae, Battle of Zama, Alps crossing
   
4. What time periods are significant for military analysis?
   → 218-201 BCE (duration of war)
   
5. Confidence in this facet being relevant (0-1)?
   → 0.99 (core military subject)
```

---

### 3. Entity Discovery (`discover_related_entities`)

**Purpose:** Find entities (people, events, places) related to a SubjectConcept

**Process:**
1. Build facet-specific Wikidata SPARQL query
2. Execute query against Wikidata endpoint
3. Return candidate entities with QIDs, labels, descriptions

**Example SPARQL for Military SFA:**

```sparql
SELECT DISTINCT ?item ?itemLabel ?description
WHERE {
  # Find military commanders
  ?item wdt:P106 wd:Q294414 .  # occupation: military commander
  
  # Connected to Roman Republic
  ?item wdt:P27 wd:Q1747689 .  # country: Roman Republic
  
  # Time period filter
  ?item wdt:P569 ?birth .
  FILTER(YEAR(?birth) >= -500 && YEAR(?birth) <= 100)
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

---

## Claude Agentic Loop

SFAs use Claude with **tool access** to the Neo4j graph. The agentic loop allows Claude to:
1. Query the graph for context
2. Check thresholds and decision tables
3. Reason about candidates
4. Make informed proposals

### Available Tools

```python
# From subject_concept_facet_agents.py line 104-147
GRAPH_TOOLS = [
    {
        "name": "query_graph",
        "description": "Execute a read-only Cypher query against the Neo4j graph.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cypher": {
                    "type": "string",
                    "description": "Cypher query (SELECT only, no mutations)"
                }
            },
            "required": ["cypher"]
        }
    },
    {
        "name": "get_threshold",
        "description": "Retrieve a system threshold value by name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Threshold name (e.g., 'sfa_proposal_confidence_default')"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_decision_table",
        "description": "Retrieve a decision table and its rows.",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_id": {
                    "type": "string",
                    "description": "Decision table ID (e.g., 'D8', 'D-031')"
                }
            },
            "required": ["table_id"]
        }
    }
]
```

### Agentic Loop Flow

```python
# Simplified from _run_claude_agent() line 451-517
def _run_claude_agent(system, user_prompt, max_turns=20):
    messages = [{"role": "user", "content": user_prompt}]
    
    for turn in range(max_turns):
        # 1. Call Claude with tools
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system,
            tools=GRAPH_TOOLS,
            messages=messages
        )
        
        # 2. Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # 3. Execute tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _handle_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # 4. Add to conversation history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
        else:
            # 5. Final response - return text
            return extract_text(response.content)
    
    return {"error": "max_turns exceeded"}
```

### Example Agentic Interaction

```
USER: Evaluate Battle of Cannae (Q36456) for MILITARY facet

ASSISTANT: [tool_use: query_graph]
{
  "cypher": "MATCH (sc:SubjectConcept {wikidata_qid: 'Q36456'}) RETURN sc"
}

SYSTEM: [tool_result]
{
  "sc": {
    "label": "Battle of Cannae",
    "wikidata_qid": "Q36456",
    "seed_qid": "Q17167"
  }
}

ASSISTANT: [tool_use: get_threshold]
{
  "name": "sfa_proposal_confidence_default"
}

SYSTEM: [tool_result]
{
  "value": 0.75,
  "description": "Default confidence for SFA proposals"
}

ASSISTANT: [final response]
{
  "relevant": true,
  "confidence": 0.95,
  "reasoning": "Battle of Cannae is one of the most significant military engagements in ancient history. Hannibal's double envelopment tactic is studied in military academies. Strong military facet relevance.",
  "proposed_entities": [
    {"qid": "Q5471", "label": "Hannibal", "role": "commander"},
    {"qid": "Q1405", "label": "Lucius Aemilius Paullus", "role": "commander"}
  ]
}
```

---

## Phase 2 Procedures

Beyond the base SFA procedures, Phase 2 SFAs add:

### 1. Claim Submission

```python
# Example from diplomatic/agent.py
def submit_diplomatic_claim(self, entity, predicate, confidence, **kwargs):
    """
    Submit claim via ClaimRegistry.
    
    Flow:
    1. Validate predicate is in DIPLOMATIC_PREDICATES
    2. Call ClaimRegistry.submit_claim()
    3. ClaimRegistry generates entity_cipher
    4. ClaimRegistry checks for existing entity (QID-based)
    5. ClaimRegistry creates/retrieves entity
    6. ClaimRegistry creates :ASSERTS edge with metadata
    7. Returns claim_id
    """
    if predicate not in self.DIPLOMATIC_PREDICATES:
        raise ValueError(f"Unknown predicate: {predicate}")
    
    return self.claim_registry.submit_claim(
        entity=entity,
        predicate=predicate,
        facet=self.facet_label,
        agent_id=self.agent_id,
        confidence=confidence,
        **kwargs
    )
```

### 2. Peer Review

```python
# Example from diplomatic/agent.py
def review_peer_claims(self, entity_cipher, reviewer_agent_id=None):
    """
    Review claims from other SFAs.
    
    Flow:
    1. Call PeerReviewer.review_entity_claims()
    2. PeerReviewer finds all claims about entity (excluding own facet)
    3. PeerReviewer creates :REVIEWED edges (Agent → Entity with metadata)
    4. PeerReviewer checks agreement thresholds
    5. PeerReviewer auto-promotes/flags claims based on consensus
    6. Find contested claims
    7. Return summary
    """
    reviewer_id = reviewer_agent_id or self.agent_id
    
    reviews = self.peer_reviewer.review_entity_claims(
        entity_cipher=entity_cipher,
        reviewing_agent=reviewer_id,
        reviewing_facet=self.facet_label
    )
    
    contested = self.peer_reviewer.find_contested_claims(entity_cipher)
    
    return {
        'entity_cipher': entity_cipher,
        'reviewer': reviewer_id,
        'reviews_submitted': len(reviews),
        'contested_claims': contested
    }
```

### 3. Significance Evaluation

```python
# Example from diplomatic/agent.py
def evaluate_diplomatic_significance(self, entity, wikidata_props=None):
    """
    Score diplomatic significance.
    
    Scoring Factors:
    - Treaty scope (bilateral, multilateral, universal)
    - Number of participants
    - Significant event markers (P793)
    - Lasting effects (P1542)
    - Diplomatic incidents (P1399)
    
    Base confidence: 0.5
    Max confidence: 1.0
    """
    confidence = 0.5
    factors = []
    
    if wikidata_props:
        participants = wikidata_props.get('P710', [])
        
        if len(participants) >= 10:
            confidence += 0.3
            factors.append(f"Multilateral ({len(participants)} parties)")
        elif len(participants) >= 3:
            confidence += 0.2
            factors.append(f"Multiple parties")
        
        if 'P793' in wikidata_props:
            confidence += 0.15
            factors.append("Significant event marker")
    
    confidence = min(confidence, 1.0)
    
    return {
        'confidence': confidence,
        'factors': factors,
        'suggested_predicates': self._suggest_predicates(entity, wikidata_props)
    }
```

---

## Customization Points

When creating a new SFA, customize these methods:

### 1. Override `_build_analysis_prompt()`

```python
def _build_analysis_prompt(self, subject_concept):
    """Custom analysis prompt for your facet"""
    return f"""
    Analyze {subject_concept['label']} from a {self.facet_label} perspective.
    
    Focus on:
    - [Facet-specific aspect 1]
    - [Facet-specific aspect 2]
    - [Facet-specific aspect 3]
    
    Consider:
    - [Facet-specific consideration 1]
    - [Facet-specific consideration 2]
    """
```

### 2. Override `_build_wikidata_discovery_query()`

```python
def _build_wikidata_discovery_query(self, subject_concept_id, entity_type):
    """Custom Wikidata SPARQL for your facet"""
    return f"""
    SELECT DISTINCT ?item ?itemLabel ?description
    WHERE {{
      # Facet-specific Wikidata properties
      ?item wdt:P??? wd:Q??? .
      ?item wdt:P??? ?value .
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 100
    """
```

### 3. Define Facet-Specific Predicates

```python
class YourSFA(SubjectConceptFacetAgent):
    YOUR_PREDICATES = [
        'predicate_1',
        'predicate_2',
        'predicate_3',
        # ... 20-30 predicates total
    ]
```

### 4. Define Relevant Wikidata Properties

```python
class YourSFA(SubjectConceptFacetAgent):
    YOUR_PROPERTIES = [
        'P???',  # property description
        'P???',  # property description
        # ... 10-20 properties total
    ]
```

### 5. Implement Evaluation Logic

```python
def evaluate_your_significance(self, entity, wikidata_props):
    """Score significance for your facet"""
    confidence = 0.5  # Base
    factors = []
    
    # Add scoring logic based on:
    # - Wikidata properties present
    # - Number of connections
    # - Time period relevance
    # - Source quality
    
    return {'confidence': confidence, 'factors': factors}
```

---

## Complete Workflow Example

### Military SFA analyzing "Battle of Cannae"

```
1. INITIALIZATION
   ├─ Create MilitarySFA(driver)
   ├─ Set facet_key = "MILITARY"
   ├─ Set agent_id = "military_sfa_001"
   ├─ Initialize ClaimRegistry
   └─ Initialize PeerReviewer

2. ACCEPT FACET PACK
   ├─ Receive pack with Battle of Cannae (Q36456)
   ├─ Build evaluation prompt:
   │  └─ "You are SFA_MILITARY evaluating Battle of Cannae..."
   ├─ Call Claude with graph tools:
   │  ├─ [Claude]: query_graph("MATCH (sc {qid: 'Q36456'}) RETURN sc")
   │  ├─ [System]: Returns existing SubjectConcept data
   │  ├─ [Claude]: get_threshold("sfa_proposal_confidence_default")
   │  └─ [System]: Returns 0.75
   └─ Return evaluation JSON:
      ├─ relevant: true
      ├─ confidence: 0.95
      └─ proposed_entities: [Hannibal, Scipio, ...]

3. SUBMIT CLAIMS
   ├─ submit_military_claim(
   │    entity={'type': 'EVENT', 'qid': 'Q36456', 'label': 'Battle of Cannae'},
   │    predicate='major_battle',
   │    confidence=0.95
   │  )
   ├─ ClaimRegistry generates cipher: ent_evt_Q36456
   ├─ ClaimRegistry checks existing: Found Q36456
   ├─ ClaimRegistry uses existing cipher: ent_con_Q36456
   ├─ ClaimRegistry creates Agent node: military_sfa_001
   └─ ClaimRegistry creates claim:
      └─ (military_sfa_001)-[:ASSERTS {facet: "MILITARY", predicate: "major_battle", confidence: 0.95}]->(ent_con_Q36456)

4. PEER REVIEW
   ├─ review_peer_claims(entity_cipher='ent_con_Q36456')
   ├─ PeerReviewer finds claims from other facets:
   │  ├─ DIPLOMATIC: "treaty_violation" (confidence: 0.65)
   │  └─ POLITICAL: "regime_change_trigger" (confidence: 0.70)
   ├─ PeerReviewer creates review edges:
   │  └─ (military_sfa_001)-[:REVIEWED {agrees: true, confidence: 0.90}]->(ent_con_Q36456)
   ├─ PeerReviewer calculates agreement scores
   └─ Return summary:
      ├─ reviews_submitted: 2
      └─ contested_claims: []

5. DISCOVER RELATED ENTITIES
   ├─ discover_related_entities('SC_001', 'Human')
   ├─ Build SPARQL query for military commanders
   ├─ Query Wikidata
   └─ Return candidates:
      ├─ Q5471 (Hannibal)
      ├─ Q1405 (Lucius Aemilius Paullus)
      └─ Q2054 (Gaius Terentius Varro)
```

---

## Key Files to Explore

### Base SFA Implementation
- **`scripts/agents/subject_concept_facet_agents.py`** (945 lines)
  - `SubjectConceptFacetAgent` base class
  - System prompt templates
  - Claude agentic loop
  - Graph tools (query_graph, get_threshold, get_decision_table)
  - SPARQL queries

### Phase 2 Integration
- **`scripts/agents/claim_registry.py`** (460 lines)
  - Entity deduplication
  - Claim submission
  - Status management

- **`scripts/agents/peer_reviewer.py`** (280 lines)
  - Cross-facet validation
  - Agreement scoring
  - Conflict detection

### Specialized SFA Examples
- **`scripts/agents/military/agent.py`** (400 lines)
  - Military-specific predicates
  - Evaluation scoring
  - Wikidata properties

- **`scripts/agents/diplomatic/agent.py`** (420 lines)
  - Diplomatic-specific predicates
  - Treaty/alliance evaluation
  - Significance scoring

---

## Summary

### SFA Operation Flow

```
User Request
    │
    ▼
┌───────────────────┐
│  SFA receives     │
│  facet pack or    │──► System Prompt: "You are SFA_MILITARY..."
│  analysis request │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│  Build prompt     │──► Task-specific prompt with candidates/context
│  with context     │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│  Claude agentic   │──► Loop with graph tool access:
│  loop starts      │    - query_graph
└───────────────────┘    - get_threshold
    │                     - get_decision_table
    ▼
┌───────────────────┐
│  Claude reasons   │──► Uses tools, checks context, makes decisions
│  and proposes     │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│  Return structured│──► JSON with evaluations, proposals, confidence
│  response         │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│  Phase 2: Submit  │──► ClaimRegistry → :ASSERTS edges
│  claims to graph  │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│  Phase 2: Peer    │──► PeerReviewer → cross-facet validation
│  review claims    │
└───────────────────┘
```

---

## Next Steps

To fully understand SFA operations:

1. **Read the base class**: `subject_concept_facet_agents.py`
2. **Study an example**: `military/agent.py` or `diplomatic/agent.py`
3. **Run tests**: See actual prompts/responses in test output
4. **Enable logging**: Watch Claude's tool use in real-time
5. **Create your own**: Follow the template to build a new SFA

---

**Questions?** The code is the ultimate documentation - dive into the files listed above to see exactly how SFAs work!
