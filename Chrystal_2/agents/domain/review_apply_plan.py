#!/usr/bin/env python3
"""Domain LLM review of an apply plan (drop bloated / duplicate PID actions)."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

PRINCIPLES = Path(__file__).resolve().parent / "PRINCIPLES_APPLY_REVIEW.md"


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


def compact_plan_for_review(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Shrink values so the review prompt stays small."""
    out: list[dict[str, Any]] = []
    for i, a in enumerate(actions):
        row = {"i": i, "action": a.get("action")}
        for k in (
            "pid",
            "property",
            "property_label",
            "node_label",
            "relationship_type",
            "qid",
            "label",
            "federation",
        ):
            if k in a and a[k] is not None:
                row[k] = a[k]
        if "value" in a:
            v = a["value"]
            s = json.dumps(v, ensure_ascii=False, default=str)
            row["value"] = s if len(s) <= 180 else s[:177] + "..."
        out.append(row)
    return out


def review_apply_plan(
    *,
    domain_id: str,
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
        "actions": compact_plan_for_review(actions),
        "skipped_summary": {
            s.get("reason"): sum(1 for x in skipped if x.get("reason") == s.get("reason"))
            for s in skipped
        },
    }
    client = anthropic.Anthropic(api_key=_anthropic_key())
    msg = client.messages.create(
        model=model,
        max_tokens=4000,
        system=system,
        messages=[
            {
                "role": "user",
                "content": (
                    "Review this apply plan. Return JSON only with drop_pids.\n\n"
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
    drops = review.get("drop_pids") or []
    if not isinstance(drops, list):
        raise SystemExit("review drop_pids must be a list")
    review["drop_pids"] = [str(p) for p in drops]
    return review


def apply_review_drops(
    actions: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    drop_pids: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    drop = set(drop_pids)
    kept: list[dict[str, Any]] = []
    for a in actions:
        pid = a.get("pid")
        if pid and pid in drop and a.get("action") in {
            "set_domain_property",
            "set_identity_tether",
            "merge_node_and_rel",
        }:
            skipped.append(
                {
                    "reason": "domain_review_drop",
                    "pid": pid,
                    "action": a.get("action"),
                    "property": a.get("property"),
                }
            )
            continue
        kept.append(a)
    return kept, skipped
