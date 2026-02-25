#!/usr/bin/env python3
"""
Chrystallum MCP Server — v1 (stdio transport)
Exposes read-only tools for Neo4j SYS_Policy and SYS_Threshold nodes.
D-031: Local-first, Cursor only. No HTTP in v1.

Tools exposed:
  get_policy(name)     → SYS_Policy node properties
  get_threshold(name)  → SYS_Threshold node properties
  list_policies()     → all SYS_Policy names, active, decision_table
  list_thresholds()   → all SYS_Threshold names, value, unit, decision_table

Usage (Cursor starts this as subprocess via .cursor/mcp.json):
  python scripts/mcp/chrystallum_mcp_server.py
"""

import json
import sys
import os
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

    # Unknown method — return empty result (allows negotiation)
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
