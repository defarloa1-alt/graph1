# Subject Agent Granularity Strategy

## Problem Statement

Each subject agent is a LangGraph agent controlling an LLM. We need:
- **Specificity**: Granular enough to handle domain-specific knowledge (e.g., "Roman Republic", "Roman Republic transition")
- **Not too much**: Avoid over-fragmentation (don't need an agent for every single entity)

## Solution: Two-Level FAST ID Architecture

### Level 1: Agent Assignment (Medium Granularity)
**Agents assigned to medium-level FAST IDs:**
- `FAST:1411640` - "Rome--History--Republic" → Roman History Agent
- `FAST:1208380` - "Greece--History" → Greek History Agent
- `FAST:1145002` - "Technology" → Technology Agent

**Rule**: Agent handles 50-500 entities in a coherent domain

### Level 2: Entity Classification (Granular)
**Agents use FAST lookup tool to get granular FAST IDs:**
- Entity: "Roman Republic" → `backbone_fast: FAST:1411640` (same as agent)
- Entity: "Roman Republic transition" → `backbone_fast: FAST:1234567` (granular lookup)
- Entity: "Sulla" → `backbone_fast: FAST:9876543` (granular lookup)

## Implementation

### Agent Registry (`scripts/agents/agent_registry.py`)
Manages subject domain agents at medium granularity:
```python
from scripts.agents import get_registry

registry = get_registry()
agent = registry.find_agent_for_entity("Roman Republic", "Organization")
# Returns: Roman History Agent (FAST:1411640)
```

### Agent Router (`scripts/agents/agent_router.py`)
Routes entities to appropriate agents:
```python
from scripts.agents import route_to_agent, extract_with_agent

# Route to agent
agent = route_to_agent("Roman Republic", "Organization")

# Extract entity with granular FAST ID
result = extract_with_agent("Roman Republic transition", "Event")
# Returns: {
#   "backbone_fast": "FAST:1234567",  # Granular (entity-level)
#   "agent_domain": "FAST:1411640",   # Agent domain (medium granularity)
#   "agent_id": "roman_history"
# }
```

### FAST Lookup Tool (`scripts/agents/fast_lookup_tool.py`)
Gets granular FAST IDs for entities:
```python
from scripts.agents import FASTLookupTool

tool = FASTLookupTool()
result = tool.lookup_entity("Roman Republic transition", "Event")
# Returns: {"fast_id": "FAST:1234567", "label": "Roman Republic--Transition", ...}
```

## Agent Granularity Rules

### Too Broad (avoid):
- "History" → Too many entities, poor specialization
- "Political science" → Too abstract

### Too Narrow (avoid):
- "Sulla's dictatorship" → Only one entity, not worth dedicated agent
- "509 BCE transition" → Too specific

### Just Right (target):
- "Rome--History--Republic" → Coherent domain, manageable scope (50-500 entities)
- "Greece--History--Classical period" → Specific enough, broad enough
- "Technology--Heat transfer" → Domain-specific but not too narrow

## Benefits

1. **Specificity**: Entities get granular FAST IDs via lookup tool
2. **Manageability**: Agents at medium granularity (not too many agents)
3. **Flexibility**: Can add new agents as domains grow
4. **Scalability**: Agent pool grows organically with knowledge base
5. **Coherence**: Each agent handles a coherent subject domain

## Example Flow

```
1. Entity extraction request: "Roman Republic transition" (Event)

2. Router uses FAST lookup:
   - Granular FAST ID: FAST:1234567 ("Roman Republic--Transition")
   - Parent FAST ID: FAST:1411640 ("Rome--History--Republic")

3. Router finds agent:
   - Agent: roman_history
   - Agent Domain: FAST:1411640

4. Agent extracts entity:
   - Uses LLM to extract details
   - Uses FAST lookup for granular classification
   - Creates entity with backbone_fast: FAST:1234567

5. Result:
   - Entity has granular FAST ID (specificity)
   - Agent remains at medium granularity (manageability)
```

## Files

- `scripts/agents/agent_registry.py` - Agent management
- `scripts/agents/agent_router.py` - Entity routing
- `scripts/agents/fast_lookup_tool.py` - FAST ID lookup
- `scripts/agents/example_usage.py` - Usage examples


