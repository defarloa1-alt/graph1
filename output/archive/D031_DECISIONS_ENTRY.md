# D-031 — DECISIONS.md Entry (apply manually if needed)

Append to DECISIONS.md after the last entry:

---

### D-031 — MCP Read-Only Server (Local-First)
**Date:** 2026-02-25  
**Status:** Decided — build complete  
**Context:** FORBIDDEN_FACETS was hardcoded identically in sca_agent.py and subject_concept_facet_agents.py — known fragmentation point from DMN extraction audit. SYS_Policy nodes already exist with correct values.  
**Decision:** Build a minimal MCP server (Python, stdio transport) exposing `get_policy(name)` and `get_threshold(name)` reading from SYS_Policy and SYS_Threshold. Refactor both scripts to read forbidden facets from graph via direct Neo4j driver (SCA already has connection; MCP tool is for Cursor agents and external callers). Cursor integration only in v1 — no HTTP, no Claude web.  
**Rationale:** Single source of truth for policy/threshold values. Any change in graph propagates everywhere. FORBIDDEN_FACETS refactor is acceptance test.  
**Consequences:** scripts/mcp/chrystallum_mcp_server.py, .cursor/mcp.json, SYS_Policy facet_key property, sca_agent and subject_concept_facet_agents refactored. Phase 2: get_federation_sources, get_subject_concepts, HTTP transport for Claude web.

---
