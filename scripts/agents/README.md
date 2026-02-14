# Agents - Chrystallum Query & Claim Submission

## Overview

This directory contains agent implementations for the Chrystallum knowledge graph, including:

- **Query Executor Agent** - ChatGPT-powered Neo4j query executor
- Extensible agent framework for future LLM integrations

## Current Implementations

### Query Executor Agent

A ChatGPT-based agent that can:
- Execute natural language queries against Chrystallum
- Discover Neo4j schema dynamically
- Generate and execute Cypher queries
- Submit claims to the knowledge graph with automatic validation and promotion

**Key Files:**
- [query_executor_agent_test.py](./query_executor_agent_test.py) - Main agent implementation
- [QUERY_EXECUTOR_QUICKSTART.md](./QUERY_EXECUTOR_QUICKSTART.md) - **START HERE** for usage
- [QUERY_EXECUTOR_SETUP.md](./QUERY_EXECUTOR_SETUP.md) - Detailed setup guide

**System Prompt:**
- [md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md](../../md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md) - Agent role definition

## Quick Start

```bash
# 1. Set environment variables
$env:NEO4J_PASSWORD = "your_password"
$env:OPENAI_API_KEY = "your_api_key"

# 2. Run basic query tests
python query_executor_agent_test.py test

# 3. Run claim submission tests
python query_executor_agent_test.py claims

# 4. Interactive mode
python query_executor_agent_test.py interactive
```

## Claim Submission Workflow

The agent can submit structured claims to the knowledge graph:

```python
result = executor.submit_claim(
    entity_id="evt_battle_of_actium_q193304",
    relationship_type="OCCURRED_DURING",
    target_id="prd_roman_republic_q17167",
    confidence=0.95,
    label="Battle of Actium in Roman Republic"
)
# → Pipeline validates → Creates nodes → Promotes if confidence >= 0.90
# → Returns: {status: "promoted", claim_id, cipher, promoted: true}
```

**Returns:**
```python
{
    "status": "created" | "promoted" | "error",
    "claim_id": "claim_<hash>",
    "cipher": "<SHA256>",
    "promoted": bool,
    "error": null | error_message
}
```

## Architecture

### Agent Layer (Direct Query Execution)
- Neo4j driver (direct connection, not MCP)
- OpenAI API (ChatGPT 3.5-turbo)
- Dynamic schema discovery (CALL db.labels(), CALL db.relationshipTypes())
- ClaimIngestionPipeline for structured claim management

### Claim Processing Pipeline
- Validation (entity/field verification)
- Deterministic claim ID generation
- SHA256 cipher for integrity
- Intermediary node creation (Context, Analysis, Facet)
- Entity linking (ASSERTS relationships)
- Automatic promotion (if confidence >= 0.90)
- Traceability (SUPPORTED_BY edges)

### Separation of Concerns
- **Agent (ChatGPT):** Query generation, natural language processing, result formatting
- **Pipeline (Python):** Validation, node creation, relationship management, promotion logic
- **Neo4j:** Graph storage, transaction management, integrity constraints

## Files & Purposes

| File | Purpose | Status |
|------|---------|--------|
| [query_executor_agent_test.py](./query_executor_agent_test.py) | Main agent implementation (460 lines) | ✅ Production-ready |
| [QUERY_EXECUTOR_QUICKSTART.md](./QUERY_EXECUTOR_QUICKSTART.md) | User-friendly quickstart guide | ✅ Complete |
| [QUERY_EXECUTOR_SETUP.md](./QUERY_EXECUTOR_SETUP.md) | Detailed setup & troubleshooting | ✅ Complete |
| [requirements.txt](./requirements.txt) | Python dependencies | ✅ Updated |
| [../tools/claim_ingestion_pipeline.py](../tools/claim_ingestion_pipeline.py) | Claim validation & promotion | ✅ Production-ready |
| [../../md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md](../../md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md) | Agent system prompt (400+ lines) | ✅ Complete |

## Dependencies

### Required Packages
```
neo4j>=5.0.0
openai>=0.27.0
```

### Install
```bash
pip install -r requirements.txt
```

### Environment Variables
```powershell
$env:NEO4J_URI = "bolt://localhost:7687"          # Neo4j connection
$env:NEO4J_USERNAME = "neo4j"                      # Neo4j user
$env:NEO4J_PASSWORD = "your_password"              # Neo4j password
$env:NEO4J_DATABASE = "neo4j"                      # Database name
$env:OPENAI_API_KEY = "sk-your-api-key"           # OpenAI API key
```

## Usage Modes

### Mode 1: Test Basic Queries
```bash
python query_executor_agent_test.py test
```
Tests agent's query generation and execution capabilities.

### Mode 2: Test Claim Submission
```bash
python query_executor_agent_test.py claims
```
Tests full claim ingestion and promotion workflow.

### Mode 3: Interactive REPL
```bash
python query_executor_agent_test.py interactive
```
Manual query testing with persistent connection.

### Mode 4: Single Query
```bash
python query_executor_agent_test.py "Your query here"
```
Execute a single query and exit.

### Mode 5: Default (Basic Tests)
```bash
python query_executor_agent_test.py
```
Equivalent to Mode 1.

## Example Queries

**Natural Language:**
```
"Show all events in 31 BCE"
"Find all humans related to Q17167"
"List subjects with military facet"
"What locations are in North Africa?"
```

**Agent Generates Cypher:**
```cypher
MATCH (n:Event) WHERE n.date_start = "-0031-01-01" RETURN n
MATCH (h:Human)-[r]-(q:SubjectConcept) WHERE q.id = "subj_q17167_001" RETURN h
MATCH (s:SubjectConcept) WHERE "military" IN s.facets RETURN s
MATCH (l:Location) WHERE l.region = "North Africa" RETURN l
```

## Claim Examples

### Example 1: Low Confidence (Not Promoted)
```python
result = executor.submit_claim(
    entity_id="evt_battle_005",
    relationship_type="INVOLVED_FIGURE",
    target_id="hmn_caesar_001",
    confidence=0.75,
    label="Battle involved Caesar"
)
# result["status"] = "created"
# result["promoted"] = false
```

### Example 2: High Confidence (Promoted)
```python
result = executor.submit_claim(
    entity_id="evt_battle_005",
    relationship_type="OCCURRED_DURING",
    target_id="prd_roman_republic_001",
    confidence=0.95,
    label="Battle occurred during Roman Republic"
)
# result["status"] = "promoted"
# result["promoted"] = true
# Canonical relationship created in graph
```

## Testing & Validation

### Test Suite Included
- `test_basic_queries()` - Predefined query validation
- `test_claim_submission()` - Claim workflow with 2 confidence levels
- `test_interactive()` - REPL mode for manual exploration

### Verify Setup
```bash
# Test Neo4j connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password'))
session = driver.session()
result = session.run('RETURN 1')
session.close()
driver.close()
print('✓ Neo4j connection OK')
"

# Test OpenAI API
python -c "
import openai
openai.api_key = 'your_api_key'
print('✓ OpenAI client OK')
"
```

## Troubleshooting

### "NEO4J_PASSWORD not set"
```bash
$env:NEO4J_PASSWORD = "your_password"
```

### "OPENAI_API_KEY not set"
```bash
$env:OPENAI_API_KEY = "your_api_key"
```

### "Failed to authenticate to server"
- Verify Neo4j service is running
- Check password is correct
- Try connecting manually with Neo4j Desktop

### "ChatGPT returns invalid Cypher"
- Query may be too complex for graph structure
- Review agent's schema output
- Check Neo4j error logs
- Try simpler query

### "Claims not promoting"
- Check confidence >= 0.90
- Verify RetrievalContext node exists
- Verify AnalysisRun node exists
- Check target entity exists in graph

See [QUERY_EXECUTOR_QUICKSTART.md](./QUERY_EXECUTOR_QUICKSTART.md#troubleshooting) for more troubleshooting.

## Implementation Details

### Agent Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `__init__()` | Initialize driver, OpenAI, pipeline, schema | None |
| `query(nlq)` | Execute natural language query | str (formatted results) |
| `submit_claim(...)` | Submit claim to pipeline | dict (status, id, promoted) |
| `close()` | Close Neo4j connection | None |
| `interactive_session()` | Start REPL mode | None (loops until exit) |
| `_discover_schema()` | Query db.labels/relationshipTypes | dict (labels, relationships) |
| `generate_cypher(nlq)` | Use ChatGPT to translate NLQ | str (Cypher query) |
| `query_neo4j(cypher)` | Execute Cypher on Neo4j | List[dict] (records) |

### Pipeline Methods

| Method | Purpose |
|--------|---------|
| `ingest_claim(...)` | Main entry point for claim submission |
| `_validate_claim_data()` | Validate entities and fields exist |
| `_generate_claim_id()` | Create deterministic claim ID |
| `_calculate_cipher()` | Generate SHA256 integrity hash |
| `_create_claim_node()` | Create Claim node with properties |
| `_create_retrieval_context()` | Create RetrievalContext + USED_CONTEXT link |
| `_create_analysis_run()` | Create AnalysisRun + HAS_ANALYSIS_RUN link |
| `_create_facet_assessment()` | Create FacetAssessment + HAS_FACET_ASSESSMENT link |
| `_link_claim_to_entities()` | Create ASSERTS relationships to source/target |
| `_promote_claim()` | Create canonical relationship (confidence >= 0.90) |

## Performance

- **Schema discovery:** ~200ms (cached)
- **Query generation (ChatGPT):** ~1-2s per query
- **Query execution:** Variable by complexity
- **Claim creation:** ~500ms (including intermediary nodes)
- **Claim promotion:** ~300ms additional (atomic transaction)

## Next Steps

1. **Setup & Test:**
   - Configure environment variables
   - Run `python query_executor_agent_test.py test`
   - Run `python query_executor_agent_test.py claims`

2. **Explore Interactively:**
   - Run `python query_executor_agent_test.py interactive`
   - Test various natural language queries

3. **Integrate with Applications:**
   - Import ChromatogramQueryExecutor in your code
   - Call `.query()` for natural language queries
   - Call `.submit_claim()` for structured claims

4. **Future Enhancements:**
   - LangGraph integration for multi-step workflows
   - FastAPI endpoint for HTTP access
   - MCP server tool for VS Code Copilot
   - Advanced error recovery and retry logic
   - Query result caching for performance

## Related Documentation

- [QUERY_EXECUTOR_QUICKSTART.md](./QUERY_EXECUTOR_QUICKSTART.md) - User guide & CLI reference
- [QUERY_EXECUTOR_SETUP.md](./QUERY_EXECUTOR_SETUP.md) - Detailed setup & troubleshooting
- [Neo4j MCP Server](../../mcp/neo4j-server/) - TypeScript MCP for VS Code Copilot
- [Claim Pipeline](../tools/claim_ingestion_pipeline.py) - Claim validation & promotion
- [Agent System Prompt](../../md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md) - ChatGPT role definition

## License & Attribution

Part of the Chrystallum historical knowledge graph project.
See main [README.md](../../README.md) for overall project information.
