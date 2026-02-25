# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a federated historical knowledge graph with 17 specialized facet agents. The core stack is Python + Neo4j + OpenAI + LangChain/LangGraph, with two small TypeScript sub-projects (MCP server, XML converter).

### Services

| Service | Port | How to Start |
|---------|------|-------------|
| Neo4j | 7474 (HTTP), 7687 (Bolt) | `sudo docker start neo4j-dev` (container already exists) |
| Gradio UI | 7860 | See below |
| Streamlit UI | 8501 | `streamlit run scripts/ui/agent_streamlit_app.py` |

### Running the Gradio UI (primary web app)

The Gradio UI requires env vars to be set:

```bash
NEO4J_URI=$NEO4J_URI NEO4J_USERNAME=$NEO4J_USERNAME NEO4J_PASSWORD=$NEO4J_PASSWORD \
OPENAI_API_KEY=$OPENAI_API_KEY \
python3 scripts/ui/agent_gradio_app.py
```

It starts on `http://127.0.0.1:7860`. Ignore D-Bus errors in headless environments (browser auto-open fails but server works fine).

### Neo4j (Docker)

The dev environment uses Neo4j Community 5.15 via Docker. Credentials are set via env vars `NEO4J_USERNAME` and `NEO4J_PASSWORD`. The container is named `neo4j-dev`.

- Property existence constraints in `01_schema_constraints_neo5_compatible.cypher` require Enterprise Edition and will fail on Community; the first ~50 uniqueness constraints and all 102 indexes apply fine.
- If the container doesn't exist yet: `sudo docker run -d --name neo4j-dev -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/$NEO4J_PASSWORD neo4j:5.15.0-community`
- If Docker daemon isn't running: `sudo dockerd &>/tmp/dockerd.log &`

### Running tests

Tests are standalone Python scripts (no pytest framework). Key test:

```bash
python3 Python/models/test_models.py
```

This runs 6 validation tests for registries, facets, relationships, claims, and Neo4j constraint generation. All tests should pass (6/6).

### Lint / syntax checking

No formal lint configuration exists. Use `python3 -m py_compile <file>` for syntax checks. For TypeScript: `npx tsc --noEmit` in `mcp/neo4j-server/`.

### Key gotchas

- Use `python3` not `python` unless a symlink exists (`sudo ln -sf /usr/bin/python3 /usr/bin/python`).
- Gradio 4.x is required (not 5.x or 6.x) due to `show_copy_button` API in `agent_gradio_app.py`. Install with `pip install 'gradio>=4.0.0,<5.0.0'`. Additionally `huggingface-hub<0.25.0` is needed for compatibility.
- The `.env` file uses `NEO4J_USERNAME` but `config.py.example` uses `NEO4J_USER`; `config_loader.py` handles both.
- The `scripts/` directory uses relative imports from `config_loader` and `facet_agent_framework`, so scripts must be run from the workspace root or have the correct `sys.path` setup.
- Agent queries (Single Facet, Auto-Route, Cross-Domain) require a valid `OPENAI_API_KEY` to generate Cypher queries.
