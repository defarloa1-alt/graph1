"""Explore a Subject through the local read-only MCP connector and save a review.

This command sends graph tool results to the configured model provider. It does
not access Wikidata or Wikipedia online, change the graph, or alter an inquiry.
Its output is unapproved research context, not a reader input or a source.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from GraphRevised.proposals.passage_reader import anthropic_client
from GraphRevised.proposals.prompt_version import prompt_version
from GraphRevised.subject_backbone import local_config

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "claude-sonnet-5-5"
ALLOWED_TOOLS = {"get_subject", "find_entities", "lookup_authority", "get_entity", "get_fact", "event_overview"}
MAX_TOOL_CALLS = 16
MAX_MODEL_CALLS = 8
MAX_RESULT_CHARS = 60000
MAX_OUTPUT_TOKENS = 8000
SYSTEM_PROMPT = """\
Explore the historical knowledge graph for a curator, starting from the supplied Subject.
Use only the supplied read-only tools. Follow relevant entities, works, and connections as
needed; inspect their assertion status, attribution, and authority records. Treat Wikidata
identifiers and aliases as identity leads, not proof; do not claim to have consulted a live
Wikidata or Wikipedia page. Consider Wikipedia as a possible separately researched source.
Do not equate proposed claims with accepted claims or treat existing graph claims as evidence
for a new source passage. Do not equate forces belonging to different events merely because
they share a commander. Repeated claims do not necessarily represent independent sources.
Finish with a concise review: relevant existing entities and connections, their statuses and
tool-derived IDs, useful authority or source leads, uncertainties and next review steps. State
what was not checked. Report leads, not decisions, and do not invent facts or tool results."""

PROMPT_VERSION = prompt_version("graph-explorer-v1", SYSTEM_PROMPT)


async def checked_tool(session: Any, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = await session.call_tool(name, arguments)
    if result.isError:
        raise RuntimeError(f"MCP tool {name} failed: {result.content}")
    value = result.structuredContent
    if not isinstance(value, dict):
        raise RuntimeError(f"MCP tool {name} returned no structured object.")
    if "error" in value:
        raise ValueError(f"MCP tool {name}: {value['error']}")
    if len(json.dumps(value, ensure_ascii=False)) > MAX_RESULT_CHARS:
        raise ValueError(f"MCP tool {name} returned more than {MAX_RESULT_CHARS} characters; narrow the request.")
    return value


async def explore(session: Any, client: Any, subject_id: str, model: str) -> dict[str, Any]:
    if not subject_id.startswith("chr:subject:") or not subject_id[len("chr:subject:"):].strip():
        raise ValueError("A local chr:subject: ID is required.")
    available = {tool.name: tool for tool in (await session.list_tools()).tools}
    missing = ALLOWED_TOOLS - available.keys()
    if missing:
        raise RuntimeError(f"MCP connector is missing required tools: {sorted(missing)}")
    tools = [{"name": t.name, "description": t.description or "", "input_schema": t.inputSchema}
             for t in (available[name] for name in sorted(ALLOWED_TOOLS))]
    seed = await checked_tool(session, "get_subject", {"subject_id": subject_id})
    if not seed.get("focus"):
        raise ValueError(f"Subject {subject_id} has no focus Entity.")
    focus_ids = {focus["id"] for focus in seed["focus"] if focus.get("id")}
    if not focus_ids:
        raise ValueError(f"Subject {subject_id} has no focus Entity with an ID.")
    calls = [{"name": "get_subject", "arguments": {"subject_id": subject_id}, "result": seed}]
    messages = [{"role": "user", "content": "Explore this Subject and its focus. This initial data came from "
                 "the get_subject MCP tool:\n" + json.dumps(seed, ensure_ascii=False)}]
    usage = {"inputTokens": 0, "outputTokens": 0}
    for _ in range(MAX_MODEL_CALLS):
        response = client.messages.create(model=model, max_tokens=MAX_OUTPUT_TOKENS, system=SYSTEM_PROMPT,
                                          tools=tools, messages=messages)
        usage["inputTokens"] += response.usage.input_tokens
        usage["outputTokens"] += response.usage.output_tokens
        if response.stop_reason == "end_turn":
            inspected = {call["arguments"].get("entity_id") for call in calls if call["name"] == "get_entity"}
            inspected |= {call["arguments"].get("event_id") for call in calls if call["name"] == "event_overview"}
            if not focus_ids.issubset(inspected):
                raise RuntimeError("The model did not inspect every Subject focus; no review saved.")
            summary = "\n".join(block.text for block in response.content if block.type == "text").strip()
            if not summary:
                raise RuntimeError("The model returned no exploration summary.")
            return {
                "subjectId": subject_id, "createdAt": datetime.now(timezone.utc).isoformat(),
                "status": "needs-review", "model": model, "promptVersion": PROMPT_VERSION,
                "limits": {"maxToolCalls": MAX_TOOL_CALLS, "maxModelCalls": MAX_MODEL_CALLS,
                           "maxOutputTokensPerCall": MAX_OUTPUT_TOKENS},
                "usage": usage, "toolCalls": calls, "summary": summary,
                "limitations": [
                    "Model output is unverified and is not an approved scope or source list.",
                    "Graph context does not establish a new claim or identity.",
                    "No online Wikidata or Wikipedia lookup was performed.",
                    "This report is not automatically used by the passage reader.",
                ],
            }
        if response.stop_reason != "tool_use":
            raise RuntimeError(f"Model exploration stopped without a review: {response.stop_reason}")
        requests = [block for block in response.content if block.type == "tool_use"]
        if not requests:
            raise RuntimeError("Model requested tools but supplied no tool calls.")
        if len(calls) + len(requests) > MAX_TOOL_CALLS:
            raise RuntimeError(f"Exploration exceeded the {MAX_TOOL_CALLS}-call MCP limit; no review saved.")
        messages.append({"role": "assistant", "content": [block.model_dump(exclude_none=True)
                                                           for block in response.content]})
        results = []
        for request in requests:
            if request.name not in ALLOWED_TOOLS or not isinstance(request.input, dict):
                raise ValueError(f"Model requested a disallowed or malformed tool: {request.name}")
            value = await checked_tool(session, request.name, request.input)
            calls.append({"name": request.name, "arguments": request.input, "result": value})
            results.append({"type": "tool_result", "tool_use_id": request.id,
                            "content": json.dumps(value, ensure_ascii=False)})
        messages.append({"role": "user", "content": results})
    raise RuntimeError(f"Exploration exceeded the {MAX_MODEL_CALLS}-call model limit; no review saved.")


async def run(subject_id: str, model: str) -> dict[str, Any]:
    config = local_config()
    env = dict(os.environ)
    env.update({"NEO4J_URI": config["uri"], "NEO4J_USERNAME": config["user"],
                "NEO4J_PASSWORD": config["password"], "NEO4J_DATABASE": config["database"]})
    params = StdioServerParameters(command=sys.executable, args=["-m", "GraphRevised.connector.server"],
                                   cwd=ROOT, env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await explore(session, anthropic_client(), subject_id, model)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subject_id", help="Existing local Subject ID")
    parser.add_argument("--output", type=Path, required=True, help="New review JSON; existing files are not overwritten")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(f"Review already exists: {args.output}")
    report = asyncio.run(run(args.subject_id, args.model))
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"Unapproved exploration review written to {args.output}; "
          f"{len(report['toolCalls'])} graph calls, {report['usage']['inputTokens']} input tokens, "
          f"{report['usage']['outputTokens']} output tokens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
