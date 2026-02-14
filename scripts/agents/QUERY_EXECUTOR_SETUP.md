# Query Executor Agent - Setup & Test Guide

**Purpose:** Test driving Neo4j queries via ChatGPT natural language  
**Date:** February 14, 2026  
**Status:** Initial test implementation

---

## Quick Start (5 minutes)

### 1. Set Environment Variables

```bash
# Neo4j credentials (local)
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=your_neo4j_password

# Or for Aura cloud
export NEO4J_URI=neo4j+s://e504e285.databases.neo4j.io
export NEO4J_PASSWORD=G-HkO6oAp3n-DIbP0Y7uqbmVeudLEHrwYWGmFNhJ5QA

# OpenAI API
export OPENAI_API_KEY=sk-...your_api_key...
```

### 2. Install Dependencies

```bash
cd C:\Projects\Graph1
pip install neo4j openai
```

### 3. Run Tests

**Option A: Automated test queries**
```bash
python scripts/agents/query_executor_agent_test.py
```

**Option B: Interactive mode (manual testing)**
```bash
python scripts/agents/query_executor_agent_test.py interactive
```

**Option C: Single query**
```bash
python scripts/agents/query_executor_agent_test.py "Show me all Humans in the graph"
```

---

## What It Does

### Flow

```
Natural Language Query
    ↓
[Agent discovers Neo4j schema]
    ↓
ChatGPT generates Cypher
    ↓
Execute against Neo4j
    ↓
Format & return results
```

### Example Session

```
Query> Show me all subjects
  Generating Cypher...
  Generated: MATCH (n:SubjectConcept) RETURN n LIMIT 10
  Executing query...

✓ Found 5 result(s):

1. label: Roman Civil War | id_hash: subj_roman_civil_war_001
2. label: Roman Republic | id_hash: subj_roman_republic_001
3. label: Julius Caesar | id_hash: subj_julius_caesar_001
...
```

---

## Environment Setup (Windows PowerShell)

### Step 1: Neo4j Credentials

```powershell
# Local Neo4j Desktop
$env:NEO4J_URI = "bolt://localhost:7687"
$env:NEO4J_USERNAME = "neo4j"
$env:NEO4J_PASSWORD = "your_password"

# OR Aura cloud
$env:NEO4J_URI = "neo4j+s://e504e285.databases.neo4j.io"
$env:NEO4J_PASSWORD = "G-HkO6oAp3n-DIbP0Y7uqbmVeudLEHrwYWGmFNhJ5QA"

# OpenAI API key
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

### Step 2: Verify Installation

```powershell
cd C:\Projects\Graph1

# Check Python
python --version

# Install dependencies
pip install neo4j openai

# Test Neo4j connection
python -c "from neo4j import GraphDatabase; print('Neo4j driver OK')"

# Test OpenAI
python -c "import openai; print('OpenAI OK')"
```

### Step 3: Run Agent

```powershell
# Activate your venv if needed
& .\.venv\Scripts\Activate.ps1

# Run test mode
python scripts/agents/query_executor_agent_test.py

# Or interactive mode
python scripts/agents/query_executor_agent_test.py interactive
```

---

## How the Agent Works

### 1. Schema Discovery

On startup, the agent queries Neo4j to learn what's available:

```cypher
CALL db.labels()              # Discover node types
CALL db.relationshipTypes()   # Discover relationship types
```

### 2. Cypher Generation

Uses ChatGPT system prompt to generate valid Cypher:

```
GPT sees available labels: [SubjectConcept, Human, Event, Place, Period, ...]
GPT sees available rels: [CLASSIFIED_BY, PARTICIPATED_IN, DURING, ...]
User asks: "Show me people in the Roman Republic"
GPT generates: MATCH (h:Human)-[:CLASSIFIED_BY]-(s:SubjectConcept) 
               WHERE s.label CONTAINS 'Roman Republic' 
               RETURN h LIMIT 10
```

### 3. Query Execution

Executes the generated Cypher safely:

```python
results = executor.query_neo4j(cypher)
```

### 4. Result Formatting

Presents results in readable format:

```
Found 10 result(s):
1. label: Julius Caesar | birth_date: -100 | death_date: -44
2. label: Pompey the Great | birth_date: -106 | death_date: -48
...
```

---

## Test Queries to Try

```
1. "Show me all SubjectConcepts"
2. "What claims are in the graph?"
3. "Find all Events"
4. "Show me Places"
5. "Find Humans named Caesar"
6. "What happened in 49 BCE?"
7. "Find relationships between Julius Caesar and the Civil War"
8. "Show me periods in the graph"
```

---

## Troubleshooting

### "NEO4J_PASSWORD not set"
**Fix:** Set environment variable before running:
```powershell
$env:NEO4J_PASSWORD = "your_password"
python scripts/agents/query_executor_agent_test.py
```

### "Failed to connect to bolt://localhost:7687"
**Causes:**
1. Neo4j Desktop not running
2. Wrong port (default is 7687, check your instance)
3. Wrong credentials

**Fix:**
```bash
# Check if Neo4j is running
netstat -ano | findstr "7687"

# If nothing, start Neo4j Desktop
# If something, verify credentials
```

### "OPENAI_API_KEY not set"
**Fix:** Get API key from https://platform.openai.com/api-keys and set:
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

### "ChatGPT returned invalid Cypher"
**Causes:**
1. Label names changed in Neo4j
2. Ambiguous query

**Fix:**
- Check schema: `CALL db.labels()`
- Try simpler query: "Show me all SubjectConcepts"
- Agent will retry and suggest alternatives

### "No results found"
**Causes:**
1. Query is valid but data doesn't exist
2. Graph is empty

**Fix:**
- Try: "Show me all nodes"
- Check Neo4j directly:
  ```cypher
  MATCH (n) RETURN count(n) as total_nodes
  ```

---

## Files

| File | Purpose |
|------|---------|
| `md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md` | Agent system prompt (context for ChatGPT) |
| `scripts/agents/query_executor_agent_test.py` | Main implementation |
| `scripts/agents/QUERY_EXECUTOR_SETUP.md` | This file |

---

## Next Steps

### Short Term
- ✅ Run test queries
- ✅ Verify Neo4j connectivity
- ✅ Test ChatGPT Cypher generation
- 🔄 Collect failures and edge cases

### Medium Term
- Enhance error handling and fallback patterns
- Add context window caching (schema inspection)
- Build agent memory (track successful queries)
- Create domain-specialized versions (Roman agent, Geography agent)

### Long Term
- Migrate to LangGraph for workflow orchestration
- Add tool use patterns (agent calls specific tools vs. generic)
- Implement multi-turn agent conversations
- Integrate with MCP server for VS Code Copilot

---

## Architecture Notes

### Why Not LangGraph Yet?

This is a **minimal test** to validate the concept:
- ✅ Proof that agents can query Neo4j
- ✅ ChatGPT can generate valid Cypher
- ✅ Direct driver connection works well
- ❌ No workflow complexity yet

Once this works reliably, we migrate to LangGraph for:
- Multi-agent orchestration
- Tool-based dispatch (specialized agents for different query types)
- State management
- Memory/context windows

### Agent Layers (Future Architecture)

```
User Query
    ↓
[Router] - Dispatch to specialist
    ├─ Temporal Agent (date queries)
    ├─ Geographic Agent (place queries)  
    ├─ Claim Agent (evidence queries)
    └─ General Agent (anything else)
    ↓
[Query Generator] - Cypher from natural language
    ↓
[Neo4j Executor] - Run & validate
    ↓
[Result Formatter] - Readable output
```

This test is the foundation for that architecture.

---

## Success Criteria

You've succeeded when:

✅ Agent connects to Neo4j  
✅ Agent discovers schema  
✅ ChatGPT generates valid Cypher  
✅ Query executes and returns results  
✅ Results are readable and correct  
✅ Agent handles errors gracefully
