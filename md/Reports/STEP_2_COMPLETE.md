# Step 2 Complete: Current State Introspection & Claim Tracking
**Date:** February 15, 2026  
**Status:** ✅ Complete  
**Critical Problem:** LLMs don't persist between sessions → agents must reload graph state

## Problem Statement

**User Requirement:**
> "the llm cannot be counted on to persist between sessions, and it needs to know what the subgraph for the SubjectConcept currently looks like and whether an external SubjectConcept agent has made a claim against any of those nodes and edges"

**Why This Matters:**
1. **No Memory Between Sessions:** LLM agents reset after each conversation
2. **Collaborative Environment:** Multiple agents work on the same graph
3. **Provenance Critical:** Need to know who created/modified what
4. **Duplicate Avoidance:** Must check existing claims before proposing new ones
5. **Awareness of Current State:** Can't assume what exists in the graph

## What Was Implemented

### 1. Current State Introspection Methods (8 new methods)
**File:** `scripts/agents/facet_agent_framework.py`

#### Session Initialization
```python
get_session_context() -> Dict[str, Any]
```
**Critical:** CALL THIS FIRST at session start!

Returns comprehensive session snapshot:
- `subgraph_sample`: SubjectConcept nodes and relationships (limit 50)
- `pending_claims`: This agent's unvalidated claims (limit 20)
- `recent_promotions`: Recently promoted claims (all agents, limit 10)
- `my_contributions`: This agent's claim statistics (total, promoted, pending, rejected)
- `schema_version`: Meta-schema node label count (validation check)
- `timestamp`: Session initialization time
- `agent_id`: This agent's facet key

**Usage:**
```python
context = agent.get_session_context()
print(f"SubjectConcept nodes: {context['subgraph_sample']['count']}")
print(f"My pending claims: {len(context['pending_claims'])}")
print(f"My promoted: {context['my_contributions']['promoted_claims']}")
```

#### Subgraph Queries
```python
get_subjectconcept_subgraph(limit: int = 100) -> Dict[str, Any]
```
Get snapshot of current SubjectConcept nodes and relationships.

Returns:
- `nodes`: List of SubjectConcept nodes with properties
- `relationships`: List of relationships between SubjectConcept nodes
- `count`: Total SubjectConcept count
- `sampled`: Whether result is sampled (count > limit)

**Usage:**
```python
subgraph = agent.get_subjectconcept_subgraph(limit=200)
existing_labels = [n['label'] for n in subgraph['nodes']]
if "Roman Republic" in existing_labels:
    print("Roman Republic already exists!")
```

#### Claim Discovery
```python
find_claims_for_node(node_id: str) -> List[Dict[str, Any]]
```
Find all claims that reference a specific node.

Returns claims with:
- claim_id, label, status, confidence, posterior_probability
- source_agent, facet, timestamp, promoted

**Usage:**
```python
claims = agent.find_claims_for_node("hash_of_node")
for claim in claims:
    print(f"{claim['source_agent']} proposed: {claim['label']}")
```

```python
find_claims_for_relationship(
    source_id: str,
    target_id: str,
    rel_type: Optional[str] = None
) -> List[Dict[str, Any]]
```
Find claims about relationships between two nodes.

**Usage:**
```python
# Find all relationship claims between nodes
claims = agent.find_claims_for_relationship(
    source_id="hash_of_human",
    target_id="hash_of_event"
)

# Filter by relationship type
claims = agent.find_claims_for_relationship(
    source_id="hash_of_human",
    target_id="hash_of_event",
    rel_type="PARTICIPATED_IN"
)
```

#### Provenance Tracking
```python
get_node_provenance(node_id: str) -> Dict[str, Any]
```
Discover which claim(s) created/modified a node.

Returns:
- `created_by_claim`: First validated claim (or None if manually created)
- `modified_by_claims`: Subsequent validated claims
- `validated_claims`: All validated claims for this node
- `proposed_claims`: Pending claims for this node
- `total_claims`: Total claim count

**Usage:**
```python
provenance = agent.get_node_provenance("hash_of_node")
if provenance['created_by_claim']:
    print(f"Created by claim: {provenance['created_by_claim']}")
else:
    print("Manually created (no claim provenance)")
```

```python
get_claim_history(node_id: str) -> Dict[str, Any]
```
Full audit trail of claims for a node (chronologically ordered).

Returns:
- `node_id`, `node_label`
- `claim_timeline`: Ordered list of claims with timestamps
- `agents_involved`: Unique agent IDs that made claims
- `facets_involved`: Unique facets that contributed

**Usage:**
```python
history = agent.get_claim_history("hash_of_node")
print(f"Timeline for {history['node_label']}:")
for claim in history['claim_timeline']:
    print(f"  {claim['timestamp']}: {claim['agent']} - {claim['label']}")
```

#### Claim Management
```python
list_pending_claims(
    facet: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 50
) -> List[Dict[str, Any]]
```
List claims awaiting validation, optionally filtered by facet.

**Usage:**
```python
# Get my pending claims
pending = agent.list_pending_claims(facet=agent.facet_key)

# Get all high-confidence pending claims
pending = agent.list_pending_claims(min_confidence=0.85, limit=100)
```

```python
find_agent_contributions(
    agent_id: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]
```
Find what an agent has proposed (defaults to self).

Returns:
- `total_claims`, `promoted_claims`, `pending_claims`, `rejected_claims`
- `claims`: List of claim records

**Usage:**
```python
# My contributions
my_stats = agent.find_agent_contributions()
print(f"Promoted: {my_stats['promoted_claims']}/{my_stats['total_claims']}")

# Another agent's contributions
other = agent.find_agent_contributions(agent_id="political")
```

### 2. Claim Lifecycle & Provenance

#### Claim Status Lifecycle
```
proposed → validated → (promoted=true)
          ↓
        rejected (rare)
```

- **proposed:** Awaiting validation (initial state)
- **validated:** Passed validation, promoted to canonical graph
- **promoted=true:** Claim executed, entities/relationships created
- **rejected:** Failed validation (uncommon, fallacies don't auto-reject)

#### Auto-Promotion Criteria
Claims auto-promote when:
- `confidence >= 0.90` AND
- `posterior_probability >= 0.90`

Fallacies are flagged but never block promotion (scientific metrics only).

#### Provenance Model

**Node Provenance:**
```cypher
(Node)-[:SUPPORTED_BY]->(Claim)
```
When a claim is promoted, created nodes link to the claim via `SUPPORTED_BY`.

**Relationship Provenance:**
```cypher
(Source)-[r:RELATIONSHIP_TYPE {promoted_from_claim_id: "claim_abc123"}]->(Target)
```
Promoted relationships get `promoted_from_claim_id` property pointing to originating claim.

**Traceability:**
```cypher
MATCH (n {id_hash: "node123"})-[:SUPPORTED_BY]->(c:Claim)
RETURN c.source_agent, c.facet, c.timestamp
```

### 3. Updated System Prompts (17 facets)
**File:** `facet_agent_system_prompts.json`
**Version:** `2026-02-15-step2`

**Added to all 17 prompts:**
```
CURRENT STATE INTROSPECTION (STEP 2 - NEW):
CRITICAL: LLMs don't persist between sessions. You must reload graph state at session start.

Available state query methods:
- get_session_context() - CALL THIS FIRST!
- get_subjectconcept_subgraph()
- find_claims_for_node()
- find_claims_for_relationship()
- get_node_provenance()
- get_claim_history()
- list_pending_claims()
- find_agent_contributions()

SESSION INITIALIZATION WORKFLOW:
1. ALWAYS call get_session_context() at start of new session
2. Review subgraph_sample to see what SubjectConcept nodes exist
3. Check pending_claims for unvalidated claims
4. Review recent_promotions to see recent additions
5. Use my_contributions stats to understand track record

BEFORE PROPOSING NEW CLAIMS:
1. Check if node already exists: get_subjectconcept_subgraph()
2. Review existing claims: find_claims_for_node(node_id)
3. Check provenance: get_node_provenance(node_id)
4. Avoid duplicates: list_pending_claims(facet=self.facet_key)

COLLABORATIVE AWARENESS:
Multiple agents work on the same graph. Always check:
- What other agents have proposed about this topic
- Whether claims conflict or complement
- Provenance to understand agent specialization
```

**Facets Updated:**
- ✅ Military, Political, Economic, Religious, Social, Cultural, Artistic
- ✅ Intellectual, Linguistic, Geographic, Environmental, Technological
- ✅ Demographic, Diplomatic, Scientific, Archaeological, Communication

### 4. Claim Structure Reference

**Claim Node Properties:**
```cypher
CREATE (c:Claim {
  // Required
  claim_id: "claim_abc123",          // Unique identifier
  cipher: "sha256_hash",             // Integrity hash
  status: "proposed",                // Lifecycle status
  source_agent: "military",          // Agent that proposed
  facet: "military",                 // Domain facet
  confidence: 0.92,                  // Agent confidence
  
  // Bayesian scoring
  prior_probability: 0.75,
  likelihood: 0.85,
  posterior_probability: 0.90,
  bayesian_score: 0.90,
  
  // Fallacy detection
  fallacies_detected: ["hasty_generalization"],
  fallacy_penalty: -0.05,
  critical_fallacy: true,
  
  // Lifecycle
  timestamp: "2026-02-15T10:30:00Z",
  promoted: false,
  promotion_date: null,
  
  // Content
  label: "Battle of Pharsalus participation",
  text: "Caesar participated in Battle of Pharsalus",
  claim_type: "causal",
  
  // Authority
  authority_source: "Wikidata",
  authority_ids: {qid: "Q47506", pid: "P607"},
  subject_qid: "Q1048"
})
```

**Claim Relationships:**
```cypher
// Claim references entities
(Claim)-[:ASSERTS]->(Entity)

// Entity provenance after promotion
(Entity)-[:SUPPORTED_BY]->(Claim)

// Context and analysis
(Claim)-[:USED_CONTEXT]->(RetrievalContext)
(Claim)-[:HAS_ANALYSIS_RUN]->(AnalysisRun)
(Claim)-[:HAS_FACET_ASSESSMENT]->(FacetAssessment)
```

## Benefits Achieved

### For Agents (LLM Instances)
1. **Session Initialization:** `get_session_context()` provides complete state snapshot
2. **Duplicate Avoidance:** Check existing nodes/claims before proposing
3. **Provenance Awareness:** Know who created what and when
4. **Collaboration:** See other agents' contributions
5. **Track Record:** Monitor own promotion success rate

### For Multi-Agent System
1. **Coordination:** Agents see each other's work
2. **Conflict Detection:** Identify competing claims early
3. **Specialization Tracking:** Understand which agents handle what
4. **Quality Metrics:** Track promotion rates per agent/facet

### For Historians
1. **Transparency:** Full audit trail for every node/edge
2. **Attribution:** Know which agent/claim created entities
3. **Validation Tracking:** See claim lifecycle progression
4. **Contribution Analysis:** Understand agent specialization patterns

### For Developers
1. **Debugging:** Trace entity creation back to claims
2. **Quality Analysis:** Identify high/low performing agents
3. **State Recovery:** Reconstruct graph history from claims
4. **Performance Metrics:** Monitor promotion rates and confidence distribution

## Verification Tests

Once Neo4j is deployed, verify state introspection:

```python
from scripts.agents.facet_agent_framework import FacetAgent

# Initialize agent (e.g., Military)
agent = FacetAgent('military', 'Military', system_prompt='...')

# Test 1: Session initialization
print("=== Session Context ===")
context = agent.get_session_context()
print(f"SubjectConcept count: {context['subgraph_sample']['count']}")
print(f"My pending claims: {len(context['pending_claims'])}")
print(f"My promoted claims: {context['my_contributions']['promoted_claims']}")

# Test 2: Subgraph query
print("\n=== SubjectConcept Subgraph ===")
subgraph = agent.get_subjectconcept_subgraph(limit=10)
print(f"Nodes: {len(subgraph['nodes'])}")
print(f"Relationships: {len(subgraph['relationships'])}")
for node in subgraph['nodes'][:3]:
    print(f"  - {node['label']}")

# Test 3: Claim discovery
print("\n=== Claim Discovery ===")
if subgraph['nodes']:
    node_id = subgraph['nodes'][0]['id_hash']
    claims = agent.find_claims_for_node(node_id)
    print(f"Claims for {subgraph['nodes'][0]['label']}: {len(claims)}")

# Test 4: Provenance tracking
print("\n=== Provenance ===")
if subgraph['nodes']:
    node_id = subgraph['nodes'][0]['id_hash']
    prov = agent.get_node_provenance(node_id)
    print(f"Created by: {prov['created_by_claim']}")
    print(f"Total claims: {prov['total_claims']}")

# Test 5: Pending claims
print("\n=== Pending Claims ===")
pending = agent.list_pending_claims(facet='military', limit=5)
print(f"Pending military claims: {len(pending)}")

# Test 6: Agent contributions
print("\n=== Agent Contributions ===")
contrib = agent.find_agent_contributions()
print(f"Total: {contrib['total_claims']}")
print(f"Promoted: {contrib['promoted_claims']}")
print(f"Pending: {contrib['pending_claims']}")

# Test 7: Claim history
print("\n=== Claim History ===")
if subgraph['nodes']:
    node_id = subgraph['nodes'][0]['id_hash']
    history = agent.get_claim_history(node_id)
    print(f"Agents involved: {history['agents_involved']}")
    print(f"Facets involved: {history['facets_involved']}")
    print(f"Timeline length: {len(history['claim_timeline'])}")
```

## Example Session Workflow

### Session Start (Critical)
```python
# 1. Initialize agent
agent = FacetAgent('military', 'Military', system_prompt=prompts['military'])

# 2. Load session context (REQUIRED!)
context = agent.get_session_context()

# 3. Review current state
print(f"Current SubjectConcept nodes: {context['subgraph_sample']['count']}")
print(f"Sample nodes:")
for node in context['subgraph_sample']['nodes'][:5]:
    print(f"  - {node['label']} (QID: {node['wikidata_qid']})")

# 4. Check pending claims
if context['pending_claims']:
    print(f"\nI have {len(context['pending_claims'])} pending claims:")
    for claim in context['pending_claims']:
        print(f"  - {claim['label']} (conf: {claim['confidence']:.2f})")

# 5. Review track record
stats = context['my_contributions']
promotion_rate = stats['promoted_claims'] / stats['total_claims'] if stats['total_claims'] > 0 else 0
print(f"\nMy track record:")
print(f"  Promoted: {stats['promoted_claims']}/{stats['total_claims']} ({promotion_rate:.1%})")
```

### Before Proposing Claim
```python
# 1. Check if entity already exists
subgraph = agent.get_subjectconcept_subgraph(limit=500)
existing_labels = [n['label'].lower() for n in subgraph['nodes']]

proposed_label = "Battle of Pharsalus"
if proposed_label.lower() in existing_labels:
    print(f"{proposed_label} already exists!")
    
    # Find the node
    node = next(n for n in subgraph['nodes'] if n['label'].lower() == proposed_label.lower())
    node_id = node['id_hash']
    
    # Check existing claims
    claims = agent.find_claims_for_node(node_id)
    print(f"Existing claims: {len(claims)}")
    
    # Check provenance
    prov = agent.get_node_provenance(node_id)
    print(f"Created by: {prov['created_by_claim']}")
    
    # Don't duplicate!
    return

# 2. Check for pending claims on similar topics
pending = agent.list_pending_claims(facet='military', min_confidence=0.80)
similar = [c for c in pending if "pharsalus" in c['label'].lower()]
if similar:
    print(f"Found {len(similar)} similar pending claims")
    # Review before proposing

# 3. Now safe to propose new claim
agent.propose_claim(...)
```

## Files Modified

1. ✅ `scripts/agents/facet_agent_framework.py` (added 8 state introspection methods)
2. ✅ `facet_agent_system_prompts.json` (updated all 17 prompts with Step 2 guidance)
3. ✅ `scripts/update_facet_prompts_step2.py` (automation script for prompt updates)

## Integration with Step 1

**Step 1 (Architecture Understanding):**
- Agents know WHAT the schema IS (labels, relationships, tiers)
- Agents can validate structure before proposing

**Step 2 (Current State Tracking):**
- Agents know WHAT currently EXISTS (nodes, edges, claims)
- Agents can avoid duplicates and track provenance

**Combined Workflow:**
1. Schema introspection: "What labels/relationships are valid?"
2. State introspection: "What instances currently exist?"
3. Validation: "Does my proposed claim fit schema and avoid duplicates?"
4. Proposal: Submit claim with confidence

## Next Steps (Step 3-N)

User will continue defining step-by-step agent process:
- **Step 3:** Claim proposal process? Query decomposition? Cypher generation?
- **Step 4:** Authority stack integration? Layer 2.5 hierarchy queries?
- **Step 5:** Validation workflow? Three-layer validation?
- **Step N:** Additional topics

## Completion Checklist

- ✅ 8 state introspection methods added to FacetAgent
- ✅ Session context initialization implemented
- ✅ Provenance tracking fully queryable
- ✅ Claim discovery methods complete
- ✅ System prompts updated (17 facets)
- ✅ Version bumped to `2026-02-15-step2`
- ⏸️ Integration tests (awaiting Neo4j deployment)
- ⏸️ Documentation in AI_CONTEXT.md (pending)

**Status:** Step 2 implementation complete, ready for testing when Neo4j is deployed.

---

## Key Takeaway

**Problem:** LLMs are stateless → agents forget everything between sessions.

**Solution:** Comprehensive state introspection API allowing agents to:
1. Load current graph state at session start (`get_session_context()`)
2. Discover existing nodes/edges before proposing duplicates
3. Track provenance (who created what, when)
4. Monitor own performance (promotion rates, pending claims)
5. Collaborate effectively (see other agents' work)

**Critical Call:** Every agent session MUST start with `get_session_context()` to reload state.
