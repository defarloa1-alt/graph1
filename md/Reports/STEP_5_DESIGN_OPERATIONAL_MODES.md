# Step 5 Design: Operational Modes & Query Workflows

**Date:** February 15, 2026  
**Status:** 🎯 DESIGN PHASE  
**Prerequisites:** Steps 1-4 complete (28 methods)

---

## Overview

Step 5 defines **how agents actually operate** in different operational contexts. Unlike Steps 1-4 (which focus on capabilities), Step 5 defines **workflows** for:

1. **Initialize Mode** - Bootstrap new domain from scratch
2. **Training Mode** - Extended learning with verbose validation
3. **Schema Query Mode** - Answer questions about Neo4j model structure
4. **Data Query Mode** - Answer questions about actual graph data

**Critical Requirement:** Verbose output to UI/logs showing **what the LLM is doing and why** (smoke test validation).

---

## User Requirements Analysis

### 1. Initialize Mode
**User:** "creates its unique id concatenation, starts proposing claims to build subjectconcept node structure"

**Interpretation:**
- Agent bootstraps into a new domain (e.g., "Roman Military History")
- Creates a unique identifier for tracking
- Starts building core SubjectConcept taxonomy
- Proposes foundational claims for validation

**Key Activities:**
- Generate session ID: `{facet}_{timestamp}_{qid_anchor}`
- Bootstrap from QID anchor (already exists via Step 3)
- Build SubjectConcept hierarchy (2-3 levels deep)
- Propose claims for each new node
- Track progress with checkpoints

**Expected Output:**
```
[INITIALIZE] Military Agent - Session: military_20260215_Q17167
[INITIALIZE] Bootstrap anchor: Q17167 (Roman Republic)
[INITIALIZE] Completeness: 87% (Step 3.5 validation)
[INITIALIZE] CIDOC-CRM: E5_Event (Step 4 alignment)
[INITIALIZE] Discovered hierarchy: 12 entities via P361 (part of)
[INITIALIZE] Proposed 8 SubjectConcept nodes
[INITIALIZE] Generated 47 claims (pending validation)
[INITIALIZE] Status: READY FOR TRAINING
```

### 2. Training Mode
**User:** "leverage every resource collected to start proposing claims rigorously. the llm at this time is in a prolonged training mode"

**Interpretation:**
- Extended iterative learning session
- Use all available resources (Wikidata, LCSH, FAST, property patterns)
- Generate hundreds/thousands of claims systematically
- Verbose logging for every decision
- Validation loop with feedback

**Key Activities:**
- Load session context (Step 2)
- Iterate through SubjectConcept nodes
- For each node:
  - Fetch Wikidata enrichment (Step 3)
  - Validate completeness (Step 3.5)
  - Enrich with CIDOC-CRM (Step 4)
  - Generate claims from statements
  - Validate claim structure (Step 1)
  - Submit for review
- Log reasoning at each step
- Track metrics (claims/hour, promotion rate)

**Expected Output:**
```
[TRAINING] Session: military_20260215_Q17167 | Iteration 1/50
[TRAINING] Node: wiki:Q28048 (Battle of Pharsalus)
[TRAINING]   → Fetching Wikidata entity... OK (142 statements)
[TRAINING]   → Completeness validation: 91% (47/52 expected properties)
[TRAINING]   → CIDOC-CRM alignment: E5_Event (High confidence)
[TRAINING]   → Generating claims from P276 (location)...
[TRAINING]     ✓ Claim: "Battle of Pharsalus occurred at Pharsalus"
[TRAINING]     ✓ Authority: Wikidata P276 → Q240898
[TRAINING]     ✓ CIDOC: E5_Event → P7_took_place_at → E53_Place
[TRAINING]     ✓ Confidence: 0.90 (Layer 2 Federation)
[TRAINING]     ✓ Status: PROPOSED (claim_abc123)
[TRAINING]   → Generating claims from P710 (participant)...
[TRAINING]     ✓ Claim: "Julius Caesar participated in Battle of Pharsalus"
[TRAINING]     ✓ Authority: Wikidata P710 → Q1048
[TRAINING]     ✓ CIDOC: E21_Person → P11_had_participant → E5_Event
[TRAINING]     ✓ Confidence: 0.90
[TRAINING]     ✓ Status: PROPOSED (claim_abc124)
[TRAINING]   → Iteration complete: 8 claims proposed, 0 errors
[TRAINING] Batch summary: 8/50 nodes processed, 47 claims, 0.94 avg confidence
```

### 3. Schema Query Mode (Ad Hoc - Model Structure)
**User:** "ad hoc queries about the neo model"

**Interpretation:**
- Natural language questions about schema
- "What node labels exist?"
- "What relationships connect Human to Event?"
- "What properties are required for SubjectConcept?"
- Use Step 1 introspection methods
- Translate NL → Schema query → Response

**Key Activities:**
- Parse natural language query
- Identify intent (node labels? relationships? properties?)
- Call appropriate Step 1 method
- Format response in natural language

**Expected Interaction:**
```
User: "What node types can I create?"
Agent: [SCHEMA QUERY] Intent: list_node_labels
Agent: [SCHEMA QUERY] Calling: introspect_node_label() for all labels
Agent: [SCHEMA QUERY] Found 14 node labels:
  - SubjectConcept (Tier 4, confidence ≥0.75)
  - Human (Tier varies)
  - Event (Tier varies)
  - Place (Tier varies)
  - Period (Tier varies)
  - Claim (internal)
  - Year/Decade/Century/Millennium (Tier 1)
  - [+7 more]
Agent: "The graph has 14 node types. The primary entity types are SubjectConcept, Human, Event, Place, and Period. Would you like details on any specific type?"

User: "What relationships can link a battle to a person?"
Agent: [SCHEMA QUERY] Intent: discover_relationships
Agent: [SCHEMA QUERY] Source: Event (assuming battle is Event)
Agent: [SCHEMA QUERY] Target: Human
Agent: [SCHEMA QUERY] Calling: discover_relationships_between('Event', 'Human')
Agent: [SCHEMA QUERY] Found 3 valid relationships:
  - PARTICIPATED_IN (Human → Event)
  - COMMANDED_BY (Event → Human)
  - AFFECTED (Event → Human)
Agent: "Battles (Event nodes) can be linked to people via:
  - PARTICIPATED_IN: The person took part in the battle
  - COMMANDED_BY: The person led forces in the battle
  - AFFECTED: The person was impacted by the battle
The most common is PARTICIPATED_IN with confidence ≥0.80."
```

### 4. Data Query Mode (Ad Hoc - Actual Content)
**User:** "ad hoc queries about data in neo"

**Interpretation:**
- Natural language questions about graph content
- "How many battles occurred in 49 BCE?"
- "Who participated in the Battle of Pharsalus?"
- "What events happened during the Roman Republic?"
- Translate NL → Cypher → Execute → Format response

**Key Activities:**
- Parse natural language query
- Identify entities (battles, years, people)
- Identify relationships (occurred in, participated in)
- Generate Cypher query
- Execute against Neo4j (Step 2 methods)
- Format results in natural language

**Expected Interaction:**
```
User: "How many battles are in the graph?"
Agent: [DATA QUERY] Intent: count_entities
Agent: [DATA QUERY] Entity type: Event (battles)
Agent: [DATA QUERY] Generating Cypher...
Agent: [DATA QUERY] Cypher: MATCH (e:Event) WHERE e.label CONTAINS 'Battle' RETURN count(e)
Agent: [DATA QUERY] Executing query...
Agent: [DATA QUERY] Result: 127 battle events
Agent: "There are 127 battles currently in the graph."

User: "Who fought at the Battle of Pharsalus?"
Agent: [DATA QUERY] Intent: find_participants
Agent: [DATA QUERY] Entity: Battle of Pharsalus (searching...)
Agent: [DATA QUERY] Found node: wiki:Q28048
Agent: [DATA QUERY] Generating Cypher...
Agent: [DATA QUERY] Cypher: MATCH (h:Human)-[:PARTICIPATED_IN]->(e:Event {id: 'wiki:Q28048'}) RETURN h.label
Agent: [DATA QUERY] Executing query...
Agent: [DATA QUERY] Result: 2 participants
  - Julius Caesar (wiki:Q1048)
  - Pompey (wiki:Q81540)
Agent: "Two commanders fought at the Battle of Pharsalus:
  - Julius Caesar (led the optimates)
  - Pompey (led the populares)"
```

---

## Required Components

### 1. Operational Mode Framework

**New class:** `AgentOperationalMode` (enum)
```python
from enum import Enum

class AgentOperationalMode(Enum):
    INITIALIZE = "initialize"
    TRAINING = "training"
    SCHEMA_QUERY = "schema_query"
    DATA_QUERY = "data_query"
```

**New methods in FacetAgent:**
```python
def set_mode(self, mode: AgentOperationalMode):
    """Switch operational mode"""
    
def get_mode(self) -> AgentOperationalMode:
    """Get current mode"""
    
def execute_mode_workflow(self, mode: AgentOperationalMode, **kwargs):
    """Execute workflow for specified mode"""
```

### 2. Verbose Logging System

**New class:** `AgentLogger`
```python
class AgentLogger:
    """Verbose logging for agent operations"""
    
    def __init__(self, agent_id: str, mode: str, session_id: str, log_to_file=True, log_to_ui=True):
        self.agent_id = agent_id
        self.mode = mode
        self.session_id = session_id
        self.log_file = f"logs/{agent_id}_{session_id}_{mode}.log"
        self.ui_callback = None  # For streaming to UI
        
    def log_action(self, action: str, details: dict, level="INFO"):
        """Log an action with structured details"""
        
    def log_reasoning(self, decision: str, rationale: str, confidence: float):
        """Log reasoning behind a decision"""
        
    def log_query(self, query_type: str, query: str, result: dict):
        """Log a query execution"""
        
    def log_error(self, error: str, context: dict):
        """Log an error with context"""
        
    def get_summary(self) -> dict:
        """Get session summary statistics"""
```

**Integration:**
```python
# In FacetAgent
self.logger = AgentLogger(
    agent_id=f"{self.facet_key}_agent",
    mode="training",
    session_id=self.session_id
)

# Usage
self.logger.log_action(
    action="FETCH_WIKIDATA",
    details={"qid": "Q28048", "statements": 142, "completeness": 0.91}
)

self.logger.log_reasoning(
    decision="PROPOSE_CLAIM",
    rationale="Property P276 (location) present in Wikidata with rank 'preferred'",
    confidence=0.90
)
```

### 3. Initialize Workflow

**New method:** `execute_initialize_mode()`
```python
def execute_initialize_mode(self, anchor_qid: str, depth: int = 2) -> dict:
    """
    Initialize mode: Bootstrap new domain
    
    Args:
        anchor_qid: Starting Wikidata QID (e.g., Q17167 for Roman Republic)
        depth: Hierarchy depth to traverse (1-3)
        
    Returns:
        {
            'session_id': str,
            'nodes_created': int,
            'claims_proposed': int,
            'status': 'INITIALIZED',
            'duration_seconds': float,
            'log_file': str
        }
    """
    self.logger = AgentLogger(self.agent_id, "initialize", self.session_id)
    
    self.logger.log_action("INITIALIZE_START", {
        "anchor_qid": anchor_qid,
        "depth": depth,
        "facet": self.facet_key
    })
    
    # Step 1: Bootstrap from QID (already exists)
    result = self.bootstrap_from_qid(anchor_qid, depth=depth, auto_submit_claims=False)
    
    self.logger.log_action("BOOTSTRAP_COMPLETE", {
        "nodes_created": result['nodes_created'],
        "claims_generated": result['claims_generated']
    })
    
    # Step 2: Build SubjectConcept structure
    # ... (to be implemented)
    
    # Step 3: Propose foundational claims
    # ... (to be implemented)
    
    return result
```

### 4. Training Workflow

**New method:** `execute_training_mode()`
```python
def execute_training_mode(self, max_iterations: int = 100, target_claims: int = 500) -> dict:
    """
    Training mode: Extended iterative claim generation
    
    Args:
        max_iterations: Max nodes to process
        target_claims: Stop after this many claims
        
    Returns:
        {
            'session_id': str,
            'iterations': int,
            'claims_proposed': int,
            'claims_promoted': int,
            'avg_confidence': float,
            'duration_seconds': float,
            'log_file': str
        }
    """
    self.logger = AgentLogger(self.agent_id, "training", self.session_id)
    
    # Load session context (Step 2)
    context = self.get_session_context()
    
    self.logger.log_action("TRAINING_START", {
        "existing_nodes": context['subgraph_sample']['count'],
        "pending_claims": len(context['pending_claims']),
        "target_claims": target_claims
    })
    
    # Iterate through SubjectConcept nodes
    claims_proposed = 0
    for i, node in enumerate(context['subgraph_sample']['nodes'][:max_iterations]):
        self.logger.log_action("ITERATION_START", {
            "iteration": i+1,
            "node_id": node['id_hash'],
            "node_label": node['label']
        })
        
        # Process node (fetch, validate, enrich, generate claims)
        # ... (to be implemented)
        
        if claims_proposed >= target_claims:
            break
    
    return result
```

### 5. Schema Query Handler

**New method:** `execute_schema_query()`
```python
def execute_schema_query(self, natural_language_query: str) -> dict:
    """
    Schema query mode: Answer questions about Neo4j model structure
    
    Args:
        natural_language_query: User's question
        
    Returns:
        {
            'query': str,
            'intent': str,
            'method_called': str,
            'result': dict,
            'natural_language_response': str
        }
    """
    self.logger = AgentLogger(self.agent_id, "schema_query", self.session_id)
    
    # Parse intent
    intent = self._parse_schema_query_intent(natural_language_query)
    
    self.logger.log_reasoning(
        decision="INTENT_CLASSIFICATION",
        rationale=f"Detected intent: {intent['type']}",
        confidence=intent['confidence']
    )
    
    # Route to appropriate Step 1 method
    if intent['type'] == 'list_node_labels':
        result = self._discover_schema()
    elif intent['type'] == 'discover_relationships':
        result = self.discover_relationships_between(intent['source'], intent['target'])
    elif intent['type'] == 'get_properties':
        result = self.get_required_properties(intent['label'])
    # ... more routing
    
    # Format natural language response
    nl_response = self._format_schema_response(intent, result)
    
    return {
        'query': natural_language_query,
        'intent': intent['type'],
        'method_called': intent['method'],
        'result': result,
        'natural_language_response': nl_response
    }
```

### 6. Data Query Handler

**New method:** `execute_data_query()`
```python
def execute_data_query(self, natural_language_query: str) -> dict:
    """
    Data query mode: Answer questions about actual graph data
    
    Args:
        natural_language_query: User's question
        
    Returns:
        {
            'query': str,
            'intent': str,
            'cypher': str,
            'result': list,
            'natural_language_response': str
        }
    """
    self.logger = AgentLogger(self.agent_id, "data_query", self.session_id)
    
    # Parse intent and entities
    intent = self._parse_data_query_intent(natural_language_query)
    
    self.logger.log_reasoning(
        decision="INTENT_CLASSIFICATION",
        rationale=f"Detected intent: {intent['type']} for entity: {intent.get('entity')}",
        confidence=intent['confidence']
    )
    
    # Generate Cypher query
    cypher = self._generate_cypher_from_intent(intent)
    
    self.logger.log_query(
        query_type="DATA_QUERY",
        query=cypher,
        result={"status": "generated"}
    )
    
    # Execute query
    result = self.query_neo4j(cypher)
    
    self.logger.log_query(
        query_type="DATA_QUERY",
        query=cypher,
        result={"records": len(result), "status": "completed"}
    )
    
    # Format natural language response
    nl_response = self._format_data_response(intent, result)
    
    return {
        'query': natural_language_query,
        'intent': intent['type'],
        'cypher': cypher,
        'result': result,
        'natural_language_response': nl_response
    }
```

---

## Implementation Priorities

### Phase A: Core Framework (1-2 days)
1. ✅ AgentOperationalMode enum
2. ✅ AgentLogger class with file + UI streaming
3. ✅ Mode switching methods in FacetAgent
4. ✅ Session ID generation

### Phase B: Initialize & Training Modes (2-3 days)
1. ✅ execute_initialize_mode() workflow
2. ✅ execute_training_mode() workflow
3. ✅ Verbose logging integration
4. ✅ Progress tracking & checkpoints
5. ✅ UI streaming hooks

### Phase C: Query Modes (2-3 days)
1. ✅ Intent classification (NL → intent)
2. ✅ execute_schema_query() with Step 1 routing
3. ✅ execute_data_query() with Cypher generation
4. ✅ Natural language response formatting
5. ✅ Error handling & fallbacks

### Phase D: Testing & Validation (1-2 days)
1. ✅ Smoke test: Initialize mode on Roman Republic
2. ✅ Smoke test: Training mode for 50 iterations
3. ✅ Smoke test: Schema queries (10 examples)
4. ✅ Smoke test: Data queries (10 examples)
5. ✅ Log file validation
6. ✅ UI output validation

**Total Estimate:** 6-10 days for complete Step 5 implementation

---

## Integration with Previous Steps

### Step 1 Integration (Schema Understanding)
- Schema query mode uses: introspect_node_label(), discover_relationships_between()
- Initialize mode uses: validate_claim_structure()
- Training mode uses: get_required_properties()

### Step 2 Integration (State Loading)
- Training mode uses: get_session_context(), get_subjectconcept_subgraph()
- All modes use: get_node_provenance(), find_claims_for_node()
- Data query mode uses: find_claims_for_relationship()

### Step 3 Integration (Federation)
- Initialize mode uses: bootstrap_from_qid()
- Training mode uses: fetch_wikidata_entity(), enrich_node_from_wikidata()
- Both use: discover_hierarchy_from_entity(), generate_claims_from_wikidata()

### Step 3.5 Integration (Validation)
- Initialize mode uses: validate_entity_completeness()
- Training mode validates every entity before processing

### Step 4 Integration (Ontology)
- Initialize mode uses: enrich_with_ontology_alignment()
- Training mode uses: enrich_claim_with_crminf()
- Both can use: generate_semantic_triples()

---

## Expected Workflow Examples

### Example 1: Initialize New Domain

```python
from facet_agent_framework import FacetAgent, AgentOperationalMode

# Create agent
agent = FacetAgent('military', 'Military', system_prompt)

# Initialize on Roman Republic
result = agent.execute_initialize_mode(
    anchor_qid='Q17167',  # Roman Republic
    depth=2
)

print(f"Session: {result['session_id']}")
print(f"Nodes: {result['nodes_created']}")
print(f"Claims: {result['claims_proposed']}")
print(f"Log: {result['log_file']}")
```

**Output:**
```
Session: military_20260215_143022_Q17167
Nodes: 23
Claims: 147
Log: logs/military_agent_military_20260215_143022_Q17167_initialize.log
```

### Example 2: Training Mode

```python
# Continue from initialized session
result = agent.execute_training_mode(
    max_iterations=100,
    target_claims=500
)

print(f"Iterations: {result['iterations']}")
print(f"Claims proposed: {result['claims_proposed']}")
print(f"Claims promoted: {result['claims_promoted']}")
print(f"Avg confidence: {result['avg_confidence']:.2f}")
print(f"Duration: {result['duration_seconds']}s")
```

**Output:**
```
Iterations: 73
Claims proposed: 503
Claims promoted: 412
Avg confidence: 0.87
Duration: 342.5s
```

### Example 3: Schema Query

```python
# Query about model
result = agent.execute_schema_query(
    "What relationships connect battles to people?"
)

print(result['natural_language_response'])
```

**Output:**
```
"Battles (Event nodes) can be linked to people (Human nodes) via three relationships:
- PARTICIPATED_IN: The person took part in the battle (most common, requires confidence ≥0.80)
- COMMANDED_BY: The person led forces in the battle (confidence ≥0.85)
- AFFECTED: The person was impacted by the battle outcome (confidence ≥0.70)
The PARTICIPATED_IN relationship is used in 89% of battle-person connections."
```

### Example 4: Data Query

```python
# Query about actual data
result = agent.execute_data_query(
    "How many battles happened in 49 BCE?"
)

print(result['natural_language_response'])
print(f"Cypher: {result['cypher']}")
```

**Output:**
```
"There are 8 battles in 49 BCE:
- Battle of Ilerda (March-July 49 BCE)
- Battle of Massilia (June-September 49 BCE)
- Battle of Dyrrhachium (July 49 BCE)
- [+5 more]
All are linked to the Year node Y-0049 via OCCURRED_IN relationships."

Cypher: MATCH (e:Event)-[:OCCURRED_IN]->(y:Year {year: -49}) WHERE e.label CONTAINS 'Battle' RETURN e.label, e.id ORDER BY e.label
```

---

## UI Integration Requirements

### Gradio UI Updates Needed

**New tab: "Agent Operations"**

Components:
1. **Mode selector** dropdown: Initialize, Training, Schema Query, Data Query
2. **Initialize panel:**
   - QID input (anchor entity)
   - Depth slider (1-3)
   - "Start Initialize" button
   - Progress bar
   - Live log output (streaming)
3. **Training panel:**
   - Max iterations input
   - Target claims input
   - "Start Training" button
   - Progress bar
   - Live log output
   - Metrics display (claims/sec, avg confidence)
4. **Schema Query panel:**
   - Natural language input
   - "Ask" button
   - Response display
   - Show Method Called
5. **Data Query panel:**
   - Natural language input
   - "Query" button
   - Response display
   - Show Generated Cypher
   - Results table

### Log Streaming Implementation

```python
# In AgentLogger
def set_ui_callback(self, callback_fn):
    """Set callback function for streaming to UI"""
    self.ui_callback = callback_fn

# In Gradio UI
def stream_log_to_ui(message):
    """Callback to append to Gradio textbox"""
    return message + "\n"

agent.logger.set_ui_callback(stream_log_to_ui)
```

---

## Testing Strategy

### Smoke Test Checklist

**Initialize Mode:**
- [ ] Create session ID correctly
- [ ] Bootstrap from Q17167 (Roman Republic)
- [ ] Create 20+ SubjectConcept nodes
- [ ] Generate 100+ claims
- [ ] Log file created and readable
- [ ] UI shows live progress

**Training Mode:**
- [ ] Load session context successfully
- [ ] Process 50 nodes without errors
- [ ] Generate 300+ claims
- [ ] Validate completeness for each entity
- [ ] Enrich with CIDOC-CRM alignment
- [ ] Log shows reasoning for each decision
- [ ] Metrics calculated correctly

**Schema Query Mode:**
- [ ] "What node types exist?" → correct response
- [ ] "What relationships link X to Y?" → correct response
- [ ] "What properties are required for Z?" → correct response
- [ ] Response formatted in natural language
- [ ] Log shows method routing

**Data Query Mode:**
- [ ] "How many battles?" → count correct
- [ ] "Who fought at X?" → participants correct
- [ ] "What happened in Y BCE?" → events correct
- [ ] Cypher generated correctly
- [ ] Results formatted naturally

---

## Next Steps

**Decision Point:** Which component should we implement first?

**Option A: Core Framework First** (recommended)
1. Implement AgentOperationalMode enum
2. Implement AgentLogger class
3. Add mode switching to FacetAgent
4. Test with simple workflows

**Option B: Initialize Mode First** (fastest to demo)
1. Implement execute_initialize_mode()
2. Add basic logging
3. Test with Roman Republic bootstrap
4. Show results in UI

**Option C: Query Modes First** (most visible)
1. Implement intent classification
2. Implement execute_schema_query()
3. Implement execute_data_query()
4. Show in UI immediately

**Recommendation:** Start with **Option A** (Core Framework) to lay foundation, then implement in order: Initialize → Training → Query modes.

**Estimated Timeline:**
- Week 1 (Feb 15-22): Core Framework + Initialize Mode
- Week 2 (Feb 23-Mar 1): Training Mode + verbose logging
- Week 3 (Mar 2-8): Query Modes + UI integration
- Week 4 (Mar 9-15): Testing + smoke test validation

---

**Status:** 🎯 Design complete, ready for implementation approval
