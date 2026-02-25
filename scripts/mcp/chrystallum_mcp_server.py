#!/usr/bin/env python3
"""
Chrystallum MCP Server — v1 (stdio transport)
Exposes read-only tools for Neo4j SYS_Policy, SYS_Threshold, SYS_FederationSource, SubjectConcept.
D-031: Local-first, Cursor only. No HTTP in v1.
D-034 Step 1: get_federation_sources, get_subject_concepts added.
D-034 Step 2: run_cypher_readonly with allowlist and param injection safety.
D-034 Step 3: HTTP transport (FastAPI), Bearer auth, Railway deploy.

Tools exposed:
  get_policy(name)         → SYS_Policy node properties
  get_threshold(name)      → SYS_Threshold node properties
  list_policies()          → all SYS_Policy names, active, decision_table
  list_thresholds()        → all SYS_Threshold names, value, unit, decision_table
  get_federation_sources() → SYS_FederationSource nodes (D-034)
  get_subject_concepts()   → SubjectConcept nodes (D-034)
  run_cypher_readonly()   → read-only MATCH queries (D-034)

Usage:
  stdio (Cursor): python scripts/mcp/chrystallum_mcp_server.py
  HTTP:          python scripts/mcp/chrystallum_mcp_server.py --transport http --port 8000
  Railway:       Procfile runs --transport http --port $PORT
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Neo4j config — reads from .env via config_loader (same pattern as other scripts)
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


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


def get_federation_sources() -> list:
    """List all SYS_FederationSource nodes (D-034)."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (fs:SYS_FederationSource)
                RETURN fs.name AS name,
                       fs.pid AS pid,
                       fs.status AS status,
                       fs.scoping_weight AS scoping_weight,
                       fs.property_name AS property_name
                ORDER BY fs.name
                """
            )
            return [dict(r) for r in result]
    finally:
        driver.close()


def get_subject_concepts() -> list:
    """List SubjectConcept nodes with label, entity_count, facets (D-034)."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (sc:SubjectConcept)
                RETURN sc.qid AS qid,
                       sc.label AS label,
                       sc.entity_count AS entity_count,
                       sc.facets AS facets
                ORDER BY sc.entity_count DESC
                """
            )
            return [dict(r) for r in result]
    finally:
        driver.close()


def run_cypher_readonly(query: str, params: dict = None) -> list:
    """
    Execute a read-only Cypher query against Chrystallum Neo4j (D-034).
    Safety constraints:
    - Query must start with MATCH (case-insensitive, stripped)
    - Query must not contain forbidden keywords
    - Query length capped at 500 characters
    - Result rows capped at 500
    """
    if params is None:
        params = {}

    # Safety check 1: length
    if len(query) > 500:
        return [{"error": "Query exceeds 500 character limit"}]

    # Safety check 2: must start with MATCH
    query_stripped = query.strip().upper()
    if not query_stripped.startswith("MATCH"):
        return [{"error": "Only MATCH queries permitted"}]

    # Safety check 3: forbidden keywords
    forbidden = ["CREATE", "SET", "DELETE", "MERGE", "CALL", "LOAD",
                 "DROP", "REMOVE", "DETACH"]
    for keyword in forbidden:
        if re.search(rf"\b{keyword}\b", query_stripped):
            return [{"error": f"Forbidden keyword in query: {keyword}"}]

    # Execute with params — no string interpolation
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(query, params)
            rows = [dict(r) for r in result]
            # Row cap
            if len(rows) > 500:
                rows = rows[:500]
                rows.append({"warning": "Result capped at 500 rows"})
            return rows
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
    },
    "get_federation_sources": {
        "description": "List all SYS_FederationSource nodes from Chrystallum graph with name, PID, status, scoping weight",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "get_subject_concepts": {
        "description": "List SubjectConcept nodes with label, entity_count, and facet assignments",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "run_cypher_readonly": {
        "description": "Execute a read-only MATCH query against Chrystallum Neo4j. MATCH only — no writes permitted. 500 char limit, 500 row cap.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Cypher MATCH query. Must start with MATCH. Max 500 chars."
                },
                "params": {
                    "type": "object",
                    "description": "Optional query parameters passed to Neo4j driver. No string interpolation."
                }
            },
            "required": ["query"]
        }
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
            elif tool_name == "get_federation_sources":
                result = get_federation_sources()
            elif tool_name == "get_subject_concepts":
                result = get_subject_concepts()
            elif tool_name == "run_cypher_readonly":
                query = arguments.get("query", "")
                params = arguments.get("params", {})
                result = run_cypher_readonly(query, params)
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

    # Unknown method — return empty result (allows negotiation)
    return {"jsonrpc": "2.0", "id": req_id, "result": {}}


def create_http_app():
    """Create FastAPI app for HTTP MCP transport (D-034 Phase 2)."""
    try:
        from fastapi import Depends, FastAPI, HTTPException, Request
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
        from fastapi.responses import JSONResponse
        import uvicorn
    except ImportError:
        raise RuntimeError("FastAPI/uvicorn not installed. Run: pip install fastapi uvicorn")

    app = FastAPI(title="Chrystallum MCP Server", version="2.0.0")
    security = HTTPBearer()

    API_KEY = os.getenv("MCP_API_KEY")
    if not API_KEY:
        raise RuntimeError("MCP_API_KEY environment variable not set")

    def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
        if credentials.credentials != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return credentials

    @app.post("/mcp")
    async def mcp_endpoint(request: Request, _=Depends(verify_api_key)):
        body = await request.json()
        response = handle_request(body)
        return JSONResponse(content=response)

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "2.0.0", "tools": len(TOOLS)}

    return app, uvicorn


def main():
    """Entry point — stdio (default) or HTTP transport."""
    parser = argparse.ArgumentParser(description="Chrystallum MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"],
                        default="stdio", help="Transport mode")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "http":
        app, uvicorn_mod = create_http_app()
        uvicorn_mod.run(app, host=args.host, port=args.port)
    else:
        # Original stdio loop — unchanged
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
