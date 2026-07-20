#!/usr/bin/env python3
"""Librarian LLM review of FAST/LCC enrich plan actions."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

PRINCIPLES = Path(__file__).resolve().parent / "PRINCIPLES_ENRICH_REVIEW.md"


def _anthropic_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY") or ""
    if key:
        return key.strip().strip("\"'")
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("ANTHROPIC_API_KEY not set")


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def compact_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, a in enumerate(actions):
        row = {"i": i, "action": a.get("action")}
        for k in (
            "lcsh_id",
            "fast_id",
            "class_number",
            "label",
            "role",
            "facet_role",
            "soft",
            "match_score",
            "chrono_facet",
            "relationship_type",
            "node_label",
        ):
            if a.get(k) is not None:
                row[k] = a[k]
        out.append(row)
    return out


def review_enrich_plan(
    *,
    domain_id: str,
    heading: str | None,
    actions: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    model: str = "claude-sonnet-4-5",
) -> dict[str, Any]:
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit("pip install anthropic") from exc

    system = PRINCIPLES.read_text(encoding="utf-8")
    payload = {
        "domain_id": domain_id,
        "lcsh_heading": heading,
        "actions": compact_actions(actions),
        "skipped_summary": {
            s.get("reason"): sum(1 for x in skipped if x.get("reason") == s.get("reason"))
            for s in skipped
        },
    }
    client = anthropic.Anthropic(api_key=_anthropic_key())
    msg = client.messages.create(
        model=model,
        max_tokens=2500,
        system=system,
        messages=[
            {
                "role": "user",
                "content": (
                    "Review this Librarian enrich plan. Return JSON only with drop_indices.\n\n"
                    + json.dumps(payload, ensure_ascii=False, indent=2)
                ),
            }
        ],
    )
    parts = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    review = _extract_json("\n".join(parts))
    drops = review.get("drop_indices") or []
    if not isinstance(drops, list):
        raise SystemExit("review drop_indices must be a list")
    review["drop_indices"] = [int(x) for x in drops]
    return review


def apply_review_drops(
    actions: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    drop_indices: list[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    drop = set(drop_indices)
    kept: list[dict[str, Any]] = []
    for i, a in enumerate(actions):
        if i in drop:
            skipped.append(
                {
                    "reason": "llm_enrich_review_drop",
                    "index": i,
                    "action": a.get("action"),
                    "fast_id": a.get("fast_id"),
                    "class_number": a.get("class_number"),
                    "label": a.get("label"),
                }
            )
        else:
            kept.append(a)
    return kept, skipped
