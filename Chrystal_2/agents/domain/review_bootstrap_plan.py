#!/usr/bin/env python3
"""Domain LLM review of a bootstrap plan (biblio + PeriodO)."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

PRINCIPLES = Path(__file__).resolve().parent / "PRINCIPLES_BOOTSTRAP_REVIEW.md"


def _anthropic_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY") or ""
    if key:
        return key.strip().strip("\"'")
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
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
    keys = (
        "action",
        "lcsh_id",
        "fast_id",
        "class_number",
        "qid",
        "periodo_id",
        "pleiades_id",
        "qid",
        "label",
        "role",
        "soft",
        "lat",
        "long",
        "chrono_facet",
        "note",
        "rationale",
    )
    out: list[dict[str, Any]] = []
    for i, a in enumerate(actions):
        row: dict[str, Any] = {"i": i}
        for k in keys:
            if a.get(k) is not None:
                row[k] = a[k]
        out.append(row)
    return out


def review_bootstrap_plan(
    *,
    domain_id: str,
    actions: list[dict[str, Any]],
    neo_snapshot: dict[str, Any] | None = None,
    model: str = "claude-sonnet-4-5",
) -> dict[str, Any]:
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit("pip install anthropic") from exc

    payload = {
        "domain_id": domain_id,
        "actions": compact_actions(actions),
        "neo_snapshot_compact": {
            "lcsh": (neo_snapshot or {}).get("lcsh"),
            "fast": (neo_snapshot or {}).get("fast"),
            "lcc": (neo_snapshot or {}).get("lcc"),
            "periodo_id": (neo_snapshot or {}).get("periodo_id"),
            "periods": (neo_snapshot or {}).get("periods"),
            "places": (neo_snapshot or {}).get("places"),
        },
    }
    client = anthropic.Anthropic(api_key=_anthropic_key())
    msg = client.messages.create(
        model=model,
        max_tokens=2500,
        system=PRINCIPLES.read_text(encoding="utf-8"),
        messages=[
            {
                "role": "user",
                "content": (
                    "Review Domain bootstrap plan. Return JSON only with drop_indices.\n\n"
                    + json.dumps(payload, ensure_ascii=False, indent=2)
                ),
            }
        ],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    review = _extract_json(text)
    drops = review.get("drop_indices") or []
    if not isinstance(drops, list):
        raise SystemExit("drop_indices must be a list")
    # Never drop noop — they document intentional skips
    noop_idxs = {i for i, a in enumerate(actions) if a.get("action") == "noop"}
    review["drop_indices"] = [int(x) for x in drops if int(x) not in noop_idxs]
    return review


def apply_review_drops(
    actions: list[dict[str, Any]],
    drop_indices: list[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    drop = set(drop_indices)
    kept: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for i, a in enumerate(actions):
        if i in drop:
            skipped.append({"reason": "bootstrap_review_drop", "index": i, **a})
        else:
            kept.append(a)
    return kept, skipped
