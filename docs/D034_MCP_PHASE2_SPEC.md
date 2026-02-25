# D-034 — MCP Phase 2: Read-Only Graph Query + HTTP Transport

**Date:** 2026-02-25  
**Status:** Spec — ready for build  
**Context:** D-031 MCP v1 (stdio) is complete. Phase 2 enables Claude.ai to query the graph directly for pre-work (Library Authority, etc.) instead of the cycle: architect writes queries → dev runs → dev reports → architect interprets. With `run_cypher_readonly` the architect queries directly and interprets.

**Decision:** Extend MCP server with (1) `get_federation_sources()` and `get_subject_concepts()`, (2) `run_cypher_readonly` with strict allowlist, (3) HTTP transport for Claude.ai connector.

---

## 1. New Tools — Add to chrystallum_mcp_server.py

### 1.1 get_federation_sources()

Returns list of SYS_FederationSource (or equivalent) nodes: name, source_id, active, priority.

**Example return:**
```json
[
  {"name": "DPRR", "source_id": "DPRR", "active": true, "priority": 1},
  {"name": "Pleiades", "source_id": "Pleiades", "active": true, "priority": 2}
]
```

### 1.2 get_subject_concepts()

Returns list of SubjectConcept nodes: subject_id, label, qid, and any structural keys.

**Example return:**
```json
[
  {"subject_id": "subj_rr_society_Q1392538", "label": "Society", "qid": "Q1392538"},
  ...
]
```

### 1.3 run_cypher_readonly(query: str, params: dict = {})

Execute a read-only Cypher query against the graph. **Strict safety:**

| Rule | Implementation |
|------|----------------|
| **Allowlist** | Only `MATCH` — reject anything else |
| **Blocklist** | Reject `CREATE`, `SET`, `DELETE`, `MERGE`, `CALL`, `LOAD` (case-insensitive) |
| **Query length** | Max 500 characters — reject longer (validate query string only) |
| **Row cap** | Max 500 rows returned — truncate with warning |
| **Parameter injection** | Accept `{"query": "...", "params": {}}`. Validate the query string alone before executing. Pass params to Neo4j driver — never interpolate params into the query string server-side. Neo4j driver handles parameterised queries safely. |

**Input:** `query` (string), `params` (optional dict)  
**Output:** `{"rows": [...], "truncated": bool}` or `{"error": "..."}`

**Rejection rationale:** Return clear error message for each violation (e.g. "Query contains forbidden keyword: CREATE").

---

## 2. HTTP Transport

**Requirements:**
- Expose MCP tools over HTTP so Claude.ai can connect
- Options: `fastmcp` (if MCP-over-HTTP supported) or minimal Flask/FastAPI wrapper
- Same JSON-RPC protocol as stdio — HTTP layer receives POST, forwards to handler

**Hosting:** Railway free tier (or Fly.io). Neo4j credentials as env vars: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`. Railway stores these as encrypted secrets. Server reads via `os.getenv()` — same pattern as config_loader.

**Deploy:** One-time setup. Railway: connect repo, set env vars, deploy. ~5 minutes. **Pre-deploy:** Confirm `.env` is in `.gitignore` so credentials never touch the repo.

---

## 3. Claude.ai MCP Connector

Once the server has an HTTPS endpoint (e.g. `https://chrystallum-mcp.railway.app`), architect connects via Claude.ai Settings → Integrations → Add MCP Server. Endpoint URL goes there. Architect runs pre-work queries directly from Claude.

**What architect needs from dev when D-034 is deployed:** Endpoint URL and confirmation that acceptance tests passed. Architect handles Claude.ai connector setup.

---

## 4. Build Order

1. Add `get_federation_sources()` and `get_subject_concepts()` to chrystallum_mcp_server.py
2. Add `run_cypher_readonly` with allowlist
3. Add HTTP transport (FastAPI or Flask)
4. Deploy to Railway (or similar)
5. Document HTTPS endpoint for Claude.ai connector

---

## 5. Acceptance Tests

- `get_federation_sources()` returns non-empty list when graph has federation sources
- `get_subject_concepts()` returns 61 SubjectConcepts (or current count)
- `run_cypher_readonly("MATCH (n:SubjectConcept) RETURN count(n) AS cnt")` returns count
- `run_cypher_readonly("CREATE (n:Test) RETURN n")` returns error (forbidden keyword)
- `run_cypher_readonly("MATCH (n) RETURN n")` returns error or truncated (row cap)
- Query length > 500 chars returns error
- `run_cypher_readonly("MATCH (n {name: $name}) RETURN n", {"name": "foo"})` executes with params (no string interpolation)

---

## 6. Block Catalog Update

Update `ChrystallumMCPServer` in sysml/BLOCK_CATALOG_RECONCILED.md:

- **Ports:** Add `cypher_query_in` (read-only Cypher), `federation_sources_out`, `subject_concepts_out`
- **Value properties:** `transport = "stdio" | "http"` (configurable)
- **Constraint:** Read-only. No write operations. Neo4j credentials never exposed to clients.
