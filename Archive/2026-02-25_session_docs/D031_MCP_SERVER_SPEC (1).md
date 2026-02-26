# D-031 — MCP Read-Only Server (Local-First)

## DECISIONS.md Entry

**Decision ID:** D-031  
**Date:** 2026-02-25  
**Category:** Infrastructure / Tooling  
**Status:** Approved — build pending  
**Deciders:** Architect + Dev  

**Decision:**
Build a minimal MCP server (Python, stdio transport) exposing `get_policy(name)` and
`get_threshold(name)` reading from SYS_Policy and SYS_Threshold nodes in Neo4j.
Refactor `sca_agent.py` and `subject_concept_facet_agents.py` to call `get_policy`
for FORBIDDEN_FACETS instead of hardcoding. Cursor integration only in v1 — no HTTP
transport, no Claude web, no deployment.

**Phase 2** (after v1 validated): Add `get_federation_sources`, `get_subject_concepts`.
Add HTTP transport (ngrok or cloud host) for Claude web architect-side validation.
`run_cypher_readonly` deferred — arbitrary Cypher is an exfiltration risk; defer until
a safe allowlist pattern is designed.

**Rationale:**
FORBIDDEN_FACETS is hardcoded identically in two scripts — known fragmentation point
from DMN extraction audit. Any change requires finding and updating both files. SYS_Policy
nodes already exist in Neo4j with the correct values. MCP gives scripts a single read
path to those nodes. The FORBIDDEN_FACETS refactor is the acceptance test for the pattern;
if it works cleanly, all 18 hardcoded values identified in the extraction audit follow
the same pattern.

**Consequences:**
- Scripts no longer own policy and threshold values — they read from graph
- SYS_Policy and SYS_Threshold nodes become live configuration, not passive documentation
- Future threshold changes require no code deployment — graph update only
- stdio transport: Cursor starts server as subprocess, no network exposure in v1

**Files affected:**
- `scripts/mcp/chrystallum_mcp_server.py` (new)
- `scripts/agents/sca_agent.py` (refactor _validate_bootstrap)
- `scripts/agents/subject_concept_facet_agents.py` (refactor module-level FORBIDDEN_FACETS)
- `.cursor/mcp.json` (new — Cursor MCP config)
- `DECISIONS.md` (this entry)
- `KANBAN.md` (move MCP server to In Progress)

---

## Build Spec for Dev

### Step 1 — MCP server

Create `scripts/mcp/chrystallum_mcp_server.py`:

```python
#!/usr/bin/env python3
"""
Chrystallum MCP Server — v1 (stdio transport)
Exposes read-only tools for Neo4j SYS_Policy and SYS_Threshold nodes.
D-031: Local-first, Cursor only. No HTTP in v1.

Tools exposed:
  get_policy(name)     → SYS_Policy node properties
  get_threshold(name)  → SYS_Threshold node properties

Usage (Cursor starts this as subprocess via .cursor/mcp.json):
  python scripts/mcp/chrystallum_mcp_server.py
"""

import json
import sys
import os
from typing import Any

# Neo4j config — reads from .env via config_loader (same pattern as other scripts)
try:
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.getenv('NEO4J_URI')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')


def get_driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def get_policy(name: str) -> dict:
    """Read a SYS_Policy node by name."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (p:SYS_Policy {name: $name}) RETURN p",
                name=name
            )
            record = result.single()
            if record is None:
                return {"error": f"SYS_Policy node '{name}' not found"}
            return dict(record["p"])
    finally:
        driver.close()


def get_threshold(name: str) -> dict:
    """Read a SYS_Threshold node by name."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (t:SYS_Threshold {name: $name}) RETURN t",
                name=name
            )
            record = result.single()
            if record is None:
                return {"error": f"SYS_Threshold node '{name}' not found"}
            return dict(record["t"])
    finally:
        driver.close()


def list_policies() -> list:
    """List all SYS_Policy node names and active status."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (p:SYS_Policy) RETURN p.name AS name, p.active AS active, "
                "p.decision_table AS decision_table ORDER BY p.name"
            )
            return [dict(r) for r in result]
    finally:
        driver.close()


def list_thresholds() -> list:
    """List all SYS_Threshold node names and values."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (t:SYS_Threshold) RETURN t.name AS name, t.value AS value, "
                "t.unit AS unit, t.decision_table AS decision_table ORDER BY t.name"
            )
            return [dict(r) for r in result]
    finally:
        driver.close()


# ── MCP stdio protocol ────────────────────────────────────────────────────────
# Minimal implementation: read JSON-RPC from stdin, write to stdout.
# Cursor MCP client sends {"method": "tools/call", "params": {"name": ..., "arguments": ...}}

TOOLS = {
    "get_policy": {
        "description": "Read a SYS_Policy node by name from Chrystallum Neo4j graph",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Policy name, e.g. NoTemporalFacet"}
            },
            "required": ["name"]
        }
    },
    "get_threshold": {
        "description": "Read a SYS_Threshold node by name from Chrystallum Neo4j graph",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Threshold name, e.g. claim_promotion_confidence"}
            },
            "required": ["name"]
        }
    },
    "list_policies": {
        "description": "List all SYS_Policy nodes with name, active status, and decision table",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "list_thresholds": {
        "description": "List all SYS_Threshold nodes with name, value, unit, and decision table",
        "inputSchema": {"type": "object", "properties": {}}
    }
}


def handle_request(req: dict) -> dict:
    method = req.get("method", "")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "chrystallum-mcp", "version": "1.0.0"}
            }
        }

    if method == "tools/list":
        tools_list = [
            {"name": name, "description": spec["description"],
             "inputSchema": spec["inputSchema"]}
            for name, spec in TOOLS.items()
        ]
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

    if method == "tools/call":
        tool_name = req.get("params", {}).get("name")
        arguments = req.get("params", {}).get("arguments", {})

        try:
            if tool_name == "get_policy":
                result = get_policy(arguments["name"])
            elif tool_name == "get_threshold":
                result = get_threshold(arguments["name"])
            elif tool_name == "list_policies":
                result = list_policies()
            elif tool_name == "list_thresholds":
                result = list_thresholds()
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                    "isError": True
                }
            }

    # Unknown method — return empty result (not an error, allows negotiation)
    return {"jsonrpc": "2.0", "id": req_id, "result": {}}


def main():
    """stdio MCP server — read newline-delimited JSON-RPC from stdin."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            response = handle_request(req)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error = {"jsonrpc": "2.0", "id": None,
                     "error": {"code": -32700, "message": f"Parse error: {e}"}}
            print(json.dumps(error), flush=True)


if __name__ == "__main__":
    main()
```

### Step 2 — Cursor MCP config

Create `.cursor/mcp.json` in project root:

```json
{
  "mcpServers": {
    "chrystallum": {
      "command": "python",
      "args": ["scripts/mcp/chrystallum_mcp_server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Step 3 — Refactor sca_agent.py

In `_validate_bootstrap`, replace the hardcoded forbidden facets check:

**Before:**
```python
forbidden = ['TEMPORAL', 'CLASSIFICATION', 'PATRONAGE', 'GENEALOGICAL']
for f in forbidden:
    assert f not in facet_keys, f"Forbidden facet {f} found!"
```

**After:**
```python
# Read forbidden facets from SYS_Policy via MCP tool (D-031)
# Direct Neo4j read here since SCA already has a driver connection
forbidden_policies = ['NoTemporalFacet', 'NoClassificationFacet',
                      'NoPatronageFacet', 'NoGenealogicalFacet']
forbidden = []
with self.driver.session() as session:
    for policy_name in forbidden_policies:
        result = session.run(
            "MATCH (p:SYS_Policy {name: $name, active: true}) "
            "RETURN p.facet_key AS facet_key",
            name=policy_name
        )
        record = result.single()
        if record and record["facet_key"]:
            forbidden.append(record["facet_key"])

for f in forbidden:
    assert f not in facet_keys, f"Forbidden facet {f} found (SYS_Policy: {f})!"
```

**Note:** SCA already has a Neo4j driver — it reads directly from graph rather than
calling the MCP tool itself. The MCP tool is for Cursor agents and external scripts.
SCA's internal reads use the driver connection it already holds.

### Step 4 — Refactor subject_concept_facet_agents.py

Replace module-level `FORBIDDEN_FACETS` hardcoded list with a graph read function:

**Before:**
```python
FORBIDDEN_FACETS = ["TEMPORAL", "CLASSIFICATION", "PATRONAGE", "GENEALOGICAL"]
```

**After:**
```python
def _load_forbidden_facets(driver) -> list[str]:
    """Load forbidden facets from SYS_Policy nodes (D-031)."""
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:SYS_Policy)
            WHERE p.active = true AND p.facet_key IS NOT NULL
              AND p.description CONTAINS 'forbidden facet'
            RETURN p.facet_key AS facet_key
            """
        )
        return [r["facet_key"] for r in result if r["facet_key"]]

# FORBIDDEN_FACETS loaded at agent initialisation, not module level
# Call _load_forbidden_facets(driver) in SubjectConceptFacetAgent.__init__
```

**Note:** This requires adding a `facet_key` property to the four SYS_Policy nodes
(NoTemporalFacet → "TEMPORAL", NoClassificationFacet → "CLASSIFICATION" etc.) and
a `description` containing "forbidden facet". Update the Cypher script accordingly.

### Step 5 — Update SYS_Policy nodes

Add `facet_key` property to the four forbidden-facet policy nodes:

```cypher
MATCH (p:SYS_Policy {name: 'NoTemporalFacet'})
SET p.facet_key = 'TEMPORAL';

MATCH (p:SYS_Policy {name: 'NoClassificationFacet'})
SET p.facet_key = 'CLASSIFICATION';

MATCH (p:SYS_Policy {name: 'NoPatronageFacet'})
SET p.facet_key = 'PATRONAGE';

MATCH (p:SYS_Policy {name: 'NoGenealogicalFacet'})
SET p.facet_key = 'GENEALOGICAL';
```

Add to `scripts/neo4j/add_sys_properties_and_relabel_d029.cypher` or create
`scripts/neo4j/update_sys_policy_facet_keys_d031.cypher`.

### Acceptance Test

After all steps complete, verify:

1. `python scripts/mcp/chrystallum_mcp_server.py` starts without error
2. Cursor can call `get_policy("NoTemporalFacet")` and get `{facet_key: "TEMPORAL", active: true, ...}`
3. `python scripts/agents/sca_agent.py` bootstraps successfully — forbidden facets
   loaded from graph, not from hardcoded list
4. `python scripts/agents/subject_concept_facet_agents.py` initialises without
   referencing the hardcoded FORBIDDEN_FACETS constant
5. Grep confirms: `grep -r "FORBIDDEN_FACETS\|TEMPORAL.*CLASSIFICATION.*PATRONAGE" scripts/agents/` returns no hardcoded list definitions

### Commit message

```
D-031: MCP server v1 (stdio), FORBIDDEN_FACETS refactor
- scripts/mcp/chrystallum_mcp_server.py (get_policy, get_threshold, list_*)
- .cursor/mcp.json
- sca_agent.py: forbidden facets from SYS_Policy
- subject_concept_facet_agents.py: forbidden facets from SYS_Policy
- scripts/neo4j/update_sys_policy_facet_keys_d031.cypher
```

---

## Phase 2 Notes (after v1 validated)

**Additional tools to add:**
- `get_federation_sources()` — list SYS_FederationSource nodes with status and PID
- `get_subject_concepts()` — list SubjectConcept nodes with label, entity_count, facets

**HTTP transport:**
```bash
# Add to server: --transport http flag
# Or use fastmcp library which handles both stdio and HTTP
pip install fastmcp
```

**Claude web connection:**
Once HTTP transport is running, add to Claude.ai settings:
- MCP server URL: `https://your-host/mcp` (ngrok or Railway)
- API key header configured on server

**run_cypher_readonly (deferred):**
Design a safe allowlist before implementing:
- Only permit queries starting with `MATCH`
- Reject any query containing `CREATE`, `SET`, `DELETE`, `MERGE`, `CALL`, `LOAD`
- Consider query length limit and result row cap (e.g. max 500 rows)
