"""Passage-specific, read-only MCP exploration for candidate entity identities."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, Field

from GraphRevised.discovery.graph_explorer import checked_tool
from GraphRevised.proposals.prompt_version import prompt_version
from GraphRevised.subject_backbone import local_config

ROOT = Path(__file__).resolve().parents[2]
TOOLS = {"find_entities", "get_entity", "lookup_authority"}
MAX_TOOL_CALLS = 8
MAX_MODEL_CALLS = 5
MAX_OUTPUT_TOKENS = 2000
PROMPT = """\
Investigate names in a historical passage for a proposed-claims reader.
Use the read-only local graph tools to search and inspect possible existing entities.
Use passage context and authority links to distinguish namesakes and changes of name;
an alias alone is not proof. Only select an entity after inspecting it with get_entity.
Choose only entities whose identity is sufficiently supported; omit uncertain or missing
identities. Do not infer participation from graph links, turn graph context into passage
evidence, or equate forces from different events. Do not invent IDs or create entities.
Finish with select_entities, including for each selected entity the name exactly as it
occurs in the target passage and a concise identification rationale. Return an empty list
if none can be identified. You have at most eight graph-tool calls and five model turns.
Inspect only the most useful candidates and finish promptly; on the last turn you must
select from entities already inspected. Your selections are reviewable leads, not accepted identities."""
PROMPT_VERSION = prompt_version("passage-graph-lookup-v1", PROMPT)


class Selection(BaseModel):
    entity_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=10, max_length=300)


class Selections(BaseModel):
    selections: list[Selection] = Field(max_length=8)


async def explore(session: Any, client: Any, model: str, inquiry: Any, passage: str,
                  context: list[tuple[str, str]], audit: dict[str, Any] | None = None) -> dict[str, Any]:
    available = {tool.name: tool for tool in (await session.list_tools()).tools}
    if TOOLS - available.keys():
        raise RuntimeError(f"MCP connector is missing tools: {sorted(TOOLS - available.keys())}")
    tools = [{"name": t.name, "description": t.description or "", "input_schema": t.inputSchema}
             for t in (available[name] for name in sorted(TOOLS))]
    tools.append({"name": "select_entities", "description": "Finish with reviewable candidate identities.",
                  "input_schema": {
                      "type": "object",
                      "properties": {"selections": {"type": "array", "items": {
                          "type": "object",
                          "properties": {"entity_id": {"type": "string"}, "name": {"type": "string"},
                                         "rationale": {"type": "string"}},
                          "required": ["entity_id", "name", "rationale"],
                      }}},
                      "required": ["selections"],
                  }})
    user = (f"Inquiry: {inquiry.label}\nSubject: {inquiry.subject['label']}\n"
            f"Source work ID: {inquiry.work_id}\n"
            + "Already in scope: " + json.dumps(
                [{"id": e["id"], "label": e["label"], "kind": e["kind"]} for e in inquiry.scope],
                ensure_ascii=False)
            + "\nSurrounding sections (context, not evidence):\n"
            + "\n".join(f"[{ref}] {text}" for ref, text in context)
            + "\nTarget passage:\n" + passage)
    messages = [{"role": "user", "content": user}]
    calls = []
    inspected: dict[str, dict[str, Any]] = {}
    usage = {"inputTokens": 0, "outputTokens": 0,
             "cacheReadTokens": 0, "cacheWriteTokens": 0}
    if audit is not None:
        audit.update({"toolCalls": calls, "usage": usage, "model": model, "promptVersion": PROMPT_VERSION})
    for turn in range(MAX_MODEL_CALLS):
        force_selection = turn == MAX_MODEL_CALLS - 1 or len(calls) >= MAX_TOOL_CALLS - 2
        turn_tools = [tools[-1]] if force_selection else tools
        response = client.messages.create(model=model, max_tokens=MAX_OUTPUT_TOKENS,
                                          system=PROMPT, tools=turn_tools, messages=messages)
        if response.model != model:
            raise RuntimeError(f"Unexpected graph lookup model: {response.model}")
        usage["inputTokens"] += response.usage.input_tokens
        usage["outputTokens"] += response.usage.output_tokens
        usage["cacheReadTokens"] += response.usage.cache_read_input_tokens or 0
        usage["cacheWriteTokens"] += response.usage.cache_creation_input_tokens or 0
        if response.stop_reason != "tool_use":
            raise RuntimeError(f"Graph lookup ended without selections: {response.stop_reason}")
        requests = [block for block in response.content if block.type == "tool_use"]
        if not requests:
            raise RuntimeError("Graph lookup requested tools without tool calls.")
        final = [request for request in requests if request.name == "select_entities"]
        if final:
            if len(requests) != 1:
                raise ValueError("Selection must be the only tool call in its turn.")
            selected = Selections.model_validate(final[0].input).selections
            seen = set()
            seen_names = set()
            entities = []
            for selection in selected:
                entity = inspected.get(selection.entity_id)
                if entity is None:
                    raise ValueError(f"Selected entity was not inspected: {selection.entity_id}")
                if selection.entity_id in seen:
                    raise ValueError(f"Entity selected more than once: {selection.entity_id}")
                if not selection.name.strip() or selection.name not in passage:
                    raise ValueError(f"Selected name does not occur in the target passage: {selection.name!r}")
                if not selection.rationale.strip():
                    raise ValueError("Selected entity needs an identification rationale.")
                if selection.name.casefold() in seen_names:
                    raise ValueError(f"Ambiguous name selected for multiple entities: {selection.name!r}")
                if entity.get("status") in {"rejected", "deprecated", "superseded"}:
                    raise ValueError(f"Selected entity is not live: {selection.entity_id}")
                if selection.entity_id.startswith("chr:entity:depicted:"):
                    raise ValueError("A source-specific depicted event cannot resolve an identity.")
                seen.add(selection.entity_id)
                seen_names.add(selection.name.casefold())
                entities.append({**selection.model_dump(), "entity": entity})
            return {"selections": entities, "toolCalls": calls, "usage": usage, "promptVersion": PROMPT_VERSION,
                    "model": model, "limits": {"toolCalls": MAX_TOOL_CALLS, "modelCalls": MAX_MODEL_CALLS}}
        messages.append({"role": "assistant", "content": [block.model_dump(exclude_none=True)
                                                           for block in response.content]})
        results = []
        for request in requests:
            if request.name not in TOOLS or not isinstance(request.input, dict):
                raise ValueError(f"Disallowed graph lookup tool: {request.name}")
            if len(calls) >= MAX_TOOL_CALLS:
                results.append({"type": "tool_result", "tool_use_id": request.id, "is_error": True,
                                "content": "Graph-tool call limit reached; finish with inspected entities."})
                continue
            call = {"name": request.name, "arguments": request.input}
            calls.append(call)
            value = await checked_tool(session, request.name, request.input)
            call["result"] = value
            if request.name == "get_entity":
                entity_id = request.input.get("entity_id")
                if value.get("id") != entity_id or not value.get("kind") or not value.get("label"):
                    raise ValueError(f"Invalid inspected entity: {entity_id}")
                inspected[entity_id] = value
            results.append({"type": "tool_result", "tool_use_id": request.id,
                            "content": json.dumps(value, ensure_ascii=False)})
        messages.append({"role": "user", "content": results})
    raise RuntimeError(f"Graph lookup exceeded the {MAX_MODEL_CALLS}-call model limit.")


async def run(client: Any, model: str, inquiry: Any, passage: str,
              context: list[tuple[str, str]], audit: dict[str, Any] | None = None) -> dict[str, Any]:
    config = local_config()
    env = dict(os.environ)
    env.update({"NEO4J_URI": config["uri"], "NEO4J_USERNAME": config["user"],
                "NEO4J_PASSWORD": config["password"], "NEO4J_DATABASE": config["database"]})
    params = StdioServerParameters(command=sys.executable, args=["-m", "GraphRevised.connector.server"],
                                   cwd=ROOT, env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await explore(session, client, model, inquiry, passage, context, audit)


def lookup(client: Any, model: str, inquiry: Any, passage: str,
           context: list[tuple[str, str]], audit: dict[str, Any] | None = None) -> dict[str, Any]:
    return asyncio.run(run(client, model, inquiry, passage, context, audit))
