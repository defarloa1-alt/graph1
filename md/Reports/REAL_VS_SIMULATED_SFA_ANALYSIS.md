# Real vs Simulated SFAs: Implementation Analysis

**Date:** February 15, 2026  
**Context:** User question about effort to spawn real SubjectFacetAgents vs simulated

---

## Current Approach: Simulated Agents

### What It Does

```python
def spawn_agent(self, facet_key: str) -> Dict[str, Any]:
    """Simulate spawning a SubjectFacetAgent (returns mock/stub for smoke test)"""
    
    simulated_agent = {
        'facet_key': facet_key,
        'facet_label': facet_key.capitalize(),
        'type': 'SIMULATED',
        'query_method': self._simulate_facet_query  # Mock method
    }
    
    self.active_agents[facet_key] = simulated_agent
    return simulated_agent

def _simulate_facet_query(self, facet_key: str, query: str) -> Dict[str, Any]:
    """Returns hard-coded mock data"""
    
    if 'senator' in query.lower() and facet_key == 'political':
        return {
            'nodes': [
                {'id': 'node_pol_1', 'label': 'Roman senator'},
                {'id': 'node_pol_2', 'label': 'toga praetexta'}
            ],
            'status': 'SIMULATED'
        }
```

### Problems

1. **Not a real smoke test** - doesn't test actual agent capabilities
2. **Hard-coded responses** - only works for specific queries (senator & mollusk)
3. **No LLM integration** - doesn't exercise the AI reasoning path
4. **No facet training** - agents have no domain knowledge
5. **False confidence** - smoke test passes but real agents never tested

---

## Proposed Approach: Real Agent Spawning

### What's Already Built

**FacetAgentFactory exists** (lines 3139-3177):
```python
@staticmethod
def create_agent(facet_key: str, facet_label: str, system_prompt: str) -> FacetAgent:
    """Create a specialized facet agent"""
    
    class SpecializedFacetAgent(FacetAgent):
        pass

    agent = SpecializedFacetAgent(facet_key, facet_label, system_prompt)
    return agent

@staticmethod
def create_all_agents() -> Dict[str, FacetAgent]:
    """Create all 17 facet agents"""
    
    agents = {}
    with open('facet_agent_system_prompts.json') as f:
        prompts_registry = json.load(f)

    for facet_config in prompts_registry['facets']:
        agent = FacetAgentFactory.create_agent(
            facet_key=facet_config['key'],
            facet_label=facet_config['label'],
            system_prompt=facet_config['system_prompt']
        )
        agents[facet_config['key']] = agent

    return agents
```

**FacetAgent capabilities** (each agent has):
- ✅ LLM integration (`self.chat()` method with OpenAI)
- ✅ System prompt loaded from JSON
- ✅ Neo4j connection
- ✅ Steps 1-5 methods (28 methods total)
- ✅ Initialize, Training, Query modes

---

## Implementation Changes Required

### Minimal Change (~20 lines)

**Before (Simulated):**
```python
def spawn_agent(self, facet_key: str) -> Dict[str, Any]:
    """Simulate spawning a SubjectFacetAgent"""
    
    simulated_agent = {
        'facet_key': facet_key,
        'type': 'SIMULATED',
        'query_method': self._simulate_facet_query
    }
    
    self.active_agents[facet_key] = simulated_agent
    return simulated_agent
```

**After (Real Agents):**
```python
def spawn_agent(self, facet_key: str, mode: str = 'real') -> FacetAgent:
    """
    Spawn a real SubjectFacetAgent (SFA)
    
    Args:
        facet_key: Facet to spawn (e.g., 'military', 'political')
        mode: 'real' or 'simulated' (default 'real')
        
    Returns:
        FacetAgent instance (or simulated dict if mode='simulated')
    """
    if mode == 'simulated':
        # Legacy simulation mode
        return self._spawn_simulated_agent(facet_key)
    
    # Load system prompt
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 
                          'facet_agent_system_prompts.json')) as f:
        prompts_registry = json.load(f)
    
    # Find facet config
    facet_config = next(
        (f for f in prompts_registry['facets'] if f['key'] == facet_key), 
        None
    )
    
    if not facet_config:
        raise ValueError(f"Unknown facet: {facet_key}")
    
    # Create REAL agent using factory
    agent = FacetAgentFactory.create_agent(
        facet_key=facet_config['key'],
        facet_label=facet_config['label'],
        system_prompt=facet_config['system_prompt']
    )
    
    # Cache it
    self.active_agents[facet_key] = agent
    
    print(f"✓ Spawned SubjectFacetAgent: {facet_key.capitalize()} (REAL agent)")
    return agent
```

### Query Execution Change (~5 lines)

**Before:**
```python
# Call simulated query method
result = agent_stub['query_method'](facet_key, query)
```

**After:**
```python
# Call REAL agent's query method (depends on operational mode)
if isinstance(agent, FacetAgent):
    # Real agent - use appropriate method based on context
    result = agent.execute_data_query(
        query=query,
        max_results=10
    )
else:
    # Fallback to simulation
    result = agent['query_method'](facet_key, query)
```

---

## Effort Analysis

### Implementation Effort: **LOW** (~1-2 hours)

| Task | Complexity | Time |
|------|------------|------|
| Modify `spawn_agent()` to use FacetAgentFactory | Simple refactor | 30 min |
| Add mode='real' parameter to SCA | Trivial | 10 min |
| Update query execution to call real agent methods | Simple | 20 min |
| Test with 2-3 facets (military, political, scientific) | Testing | 30 min |
| Update Gradio UI to support real vs simulated toggle | UI change | 30 min |

**Total: ~2 hours**

### What You Get

#### Real Agent Benefits

1. **Real smoke test** - Actually tests agent capabilities
2. **LLM reasoning** - Genuine AI analysis, not hard-coded responses
3. **Facet perspective** - Agent uses its system prompt to analyze domain
4. **Scalable** - Works for ANY query, not just "senator & mollusk"
5. **True validation** - If smoke test passes, agents actually work

#### Real Agent Behavior

```python
# Example: Political agent analyzing "Roman senator and mollusk"

# Agent receives system prompt:
system_prompt = """
You are a Political History domain expert specializing in governance, 
power structures, political movements, and institutional dynamics...
"""

# Agent analyzes query from POLITICAL perspective:
result = political_agent.execute_data_query("Roman senator and mollusk")

# Real LLM reasoning:
# - "Senator" → toga praetexta (political insignia)
# - "Purple stripe" → rank indicator (political)
# - "Tyrian purple" → status symbol (political power)
# - "Mollusk" → ignored (not political domain)

# Returns real Neo4j query results:
{
    'nodes': [
        {'qid': 'Q191172', 'label': 'Roman senator', 'facet': 'political'},
        {'qid': 'Q172645', 'label': 'toga praetexta', 'facet': 'political'}
    ],
    'edges': [
        {'from': 'Q191172', 'to': 'Q172645', 'relation': 'WEARS'}
    ],
    'reasoning': 'Political analysis: Senator's toga indicates rank...'
}
```

---

## Short-Term Solution (Before LangGraph)

### Option 1: Direct Agent Spawning (Recommended)

**Use FacetAgentFactory to create real agents:**
- Each agent is a Python class instance
- Agent manages its own LLM calls via `self.chat()`
- Agent has access to Neo4j
- Agent uses Steps 1-5 methods
- No external orchestration needed

**Pros:**
- ✅ Simple implementation (~2 hours)
- ✅ Real agent behavior
- ✅ True smoke test
- ✅ Uses existing codebase

**Cons:**
- ⚠️ No persistent agent nodes in Neo4j (ephemeral instances)
- ⚠️ No agent orchestration framework (just Python class instances)

### Option 2: Agent Nodes in Neo4j

**Create Agent nodes to track spawned agents:**

```cypher
// Create Agent node
CREATE (agent:Agent {
    agent_id: 'sfa_military_20260215_143500',
    agent_type: 'SubjectFacetAgent',
    facet_key: 'military',
    facet_label: 'Military',
    status: 'active',
    spawned_at: datetime(),
    spawned_by: 'sca_20260215',
    session_id: 'military_20260215_143500'
})

// Link to SubjectConcept domain
MATCH (sc:SubjectConcept {label: 'Roman Republic'})
CREATE (agent)-[:OWNS_DOMAIN]->(sc)

// Track queries
CREATE (query:AgentQuery {
    query_id: 'query_001',
    query_text: 'Roman senator and mollusk',
    timestamp: datetime()
})
CREATE (agent)-[:EXECUTED_QUERY]->(query)
```

**Implementation:**
```python
def spawn_agent_with_persistence(self, facet_key: str) -> FacetAgent:
    """Spawn agent and create Agent node in Neo4j"""
    
    # 1. Create real agent instance
    agent = FacetAgentFactory.create_agent(...)
    
    # 2. Create Agent node in Neo4j
    self.create_agent_node(
        agent_id=f"sfa_{facet_key}_{session_id}",
        facet_key=facet_key,
        spawned_by=self.session_id
    )
    
    # 3. Cache in memory
    self.active_agents[facet_key] = agent
    
    return agent

def create_agent_node(self, agent_id: str, facet_key: str, spawned_by: str):
    """Create Agent node in Neo4j"""
    
    query = """
    CREATE (agent:Agent {
        agent_id: $agent_id,
        agent_type: 'SubjectFacetAgent',
        facet_key: $facet_key,
        status: 'active',
        spawned_at: datetime(),
        spawned_by: $spawned_by
    })
    RETURN agent
    """
    
    with self.driver.session() as session:
        session.run(query, agent_id=agent_id, facet_key=facet_key, spawned_by=spawned_by)
```

**Pros:**
- ✅ Persistent tracking of agent lifecycle
- ✅ Query history in graph
- ✅ Agent ownership of domains
- ✅ Foundation for LangGraph migration

**Cons:**
- ⚠️ Additional complexity (~4 hours implementation)
- ⚠️ Neo4j schema changes needed

---

## Recommendation

### Phase 1: Real Agent Spawning (Now)

**Why:**
- Simulated agents don't test real behavior
- SFAs need to be trained in their discipline to be useful
- Factory already exists, just use it
- Minimal effort (~2 hours)

**Implementation:**
1. Modify `spawn_agent()` to call `FacetAgentFactory.create_agent()`
2. Add `mode='real'` parameter (default to real, keep simulated for legacy)
3. Update query execution to call real agent methods
4. Test with military + political + scientific facets

### Phase 2: Agent Node Persistence (Later)

**Why:**
- Foundation for LangGraph orchestration
- Agent lifecycle tracking
- Query history
- Domain ownership model

**When:**
- After Phase 1 validated
- Before LangGraph migration
- When agent orchestration patterns stabilized

---

## Code Diff (Minimal Change)

```diff
# SubjectConceptAgent class

- def spawn_agent(self, facet_key: str) -> Dict[str, Any]:
+ def spawn_agent(self, facet_key: str, mode: str = 'real') -> Union[FacetAgent, Dict[str, Any]]:
-     """Simulate spawning a SubjectFacetAgent (returns mock/stub for smoke test)"""
+     """
+     Spawn a SubjectFacetAgent (real or simulated)
+     
+     Args:
+         facet_key: Facet to spawn
+         mode: 'real' (default) or 'simulated'
+     """
+     
+     if mode == 'simulated':
+         return self._spawn_simulated_agent(facet_key)
+     
+     # Load facet config
+     with open('facet_agent_system_prompts.json') as f:
+         prompts = json.load(f)
+     
+     facet_config = next((f for f in prompts['facets'] if f['key'] == facet_key), None)
+     if not facet_config:
+         raise ValueError(f"Unknown facet: {facet_key}")
-     
-     simulated_agent = {
-         'facet_key': facet_key,
-         'facet_label': facet_key.capitalize(),
-         'type': 'SIMULATED',
-         'query_method': self._simulate_facet_query
-     }
+     
+     # Create REAL agent
+     agent = FacetAgentFactory.create_agent(
+         facet_key=facet_config['key'],
+         facet_label=facet_config['label'],
+         system_prompt=facet_config['system_prompt']
+     )
-     
-     self.active_agents[facet_key] = simulated_agent
-     return simulated_agent
+     
+     self.active_agents[facet_key] = agent
+     print(f"✓ Spawned REAL SubjectFacetAgent: {facet_key.capitalize()}")
+     return agent

+ def _spawn_simulated_agent(self, facet_key: str) -> Dict[str, Any]:
+     """Legacy simulation mode for testing"""
+     simulated_agent = {
+         'facet_key': facet_key,
+         'type': 'SIMULATED',
+         'query_method': self._simulate_facet_query
+     }
+     self.active_agents[facet_key] = simulated_agent
+     return simulated_agent

  def execute_cross_domain_query(...):
      # ... spawn agents ...
      for facet_key in facets:
-         agents[facet_key] = self.spawn_agent(facet_key)
+         agents[facet_key] = self.spawn_agent(facet_key, mode='real')  # ← Change here
      
      # ... execute queries ...
      for facet_key, agent in agents.items():
-         result = agent['query_method'](facet_key, query)
+         if isinstance(agent, FacetAgent):
+             # Real agent
+             result = agent.execute_data_query(query, max_results=10)
+         else:
+             # Simulated fallback
+             result = agent['query_method'](facet_key, query)
```

**Total lines changed: ~30 lines**

---

## Summary

**Question:** What's the effort to spawn real agents vs simulated?

**Answer:** **LOW EFFORT (~2 hours)**

**Why it's easy:**
- FacetAgentFactory already exists
- Each FacetAgent already has LLM integration
- System prompts already loaded from JSON
- Just refactor `spawn_agent()` to use factory instead of creating mock dict

**Why you should do it:**
- Simulated agents aren't a real smoke test
- SFAs need facet training to be useful
- Real agents use actual LLM reasoning
- Works for ANY query (not hard-coded)

**Recommendation:** **Switch to real agent spawning NOW**, add Neo4j Agent nodes later when designing orchestration patterns.

---

**Next Step:** Implement Phase 1 (real agent spawning) in ~2 hours or keep simulated mode?
