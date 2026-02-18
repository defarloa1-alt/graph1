#!/usr/bin/env python3
"""Ordered single-hit claim confidence policy evaluator."""

from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Tuple

CLAIM_TYPE_TO_EPISTEMIC: Dict[str, str] = {
    "temporal": "EVENT",
    "factual": "EVENT",
    "relational": "ACTOR_CAUSAL",
    "causal": "ACTOR_CAUSAL",
    "pattern": "PATTERN_THEORY",
    "counterfactual": "COUNTERFACTUAL",
}


def load_policy(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if payload.get("evaluation_mode") != "ordered_single_hit":
        raise ValueError("Unsupported policy evaluation mode")
    payload["_policy_hash"] = canonical_policy_hash(payload)
    return payload


def map_claim_type_to_epistemic(claim_type: str, default: str = "EVENT") -> str:
    key = (claim_type or "").strip().lower()
    return CLAIM_TYPE_TO_EPISTEMIC.get(key, default)


def clamp_confidence(value: float, min_conf: float, max_conf: float) -> float:
    return max(min_conf, min(max_conf, value))


def canonical_policy_hash(policy: Dict[str, Any]) -> str:
    normalized = {k: v for k, v in policy.items() if not str(k).startswith("_")}
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def policy_hash(policy: Dict[str, Any]) -> str:
    return policy.get("_policy_hash") or canonical_policy_hash(policy)


def _numeric_compare(actual: float, condition: str) -> bool:
    m = re.match(r"^\s*(>=|<=|>|<|=)\s*(-?\d+(?:\.\d+)?)\s*$", condition)
    if not m:
        return False
    op = m.group(1)
    rhs = float(m.group(2))
    if op == ">=":
        return actual >= rhs
    if op == "<=":
        return actual <= rhs
    if op == ">":
        return actual > rhs
    if op == "<":
        return actual < rhs
    return actual == rhs


def _matches_condition(actual: Any, expected: Any) -> bool:
    if expected == "any":
        return True
    if isinstance(expected, bool):
        return bool(actual) is expected
    if isinstance(expected, (int, float)):
        return actual == expected
    if isinstance(expected, str):
        if re.match(r"^\s*(>=|<=|>|<|=)\s*-?\d+(?:\.\d+)?\s*$", expected):
            try:
                return _numeric_compare(float(actual), expected)
            except (TypeError, ValueError):
                return False
        return str(actual) == expected
    return actual == expected


def evaluate_table(rows: List[Dict[str, Any]], inputs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    for row in rows:
        conditions = row.get("conditions", {})
        if all(_matches_condition(inputs.get(k), v) for k, v in conditions.items()):
            return row.get("row_id", "UNKNOWN"), row.get("output", {})
    raise ValueError("No matching row and no default row found")


def evaluate_claim_confidence_policy(
    policy: Dict[str, Any],
    *,
    primary_count: int,
    secondary_count: int,
    tertiary_count: int,
    has_conflicts: bool,
    epistemic_type: str,
    federation_depth: int,
) -> Dict[str, Any]:
    tables = policy.get("tables", {})

    source_row, source_out = evaluate_table(
        tables.get("source_strength", []),
        {
            "primary_count": primary_count,
            "secondary_count": secondary_count,
            "tertiary_count": tertiary_count,
        },
    )
    source_strength = source_out["source_strength"]

    conflict_row, conflict_out = evaluate_table(
        tables.get("conflict_code", []),
        {"has_conflicts": has_conflicts},
    )
    conflict_code = conflict_out["conflict_code"]

    profile_row, profile_out = evaluate_table(
        tables.get("claim_confidence_profile", []),
        {
            "epistemic_type": epistemic_type,
            "source_strength": source_strength,
            "conflict_code": conflict_code,
            "federation_depth": federation_depth,
        },
    )

    return {
        "policy_id": policy.get("policy_id", "unknown_policy"),
        "policy_hash": policy_hash(policy),
        "row_ids": {
            "source_strength": source_row,
            "conflict_code": conflict_row,
            "claim_confidence_profile": profile_row,
        },
        "source_strength": source_strength,
        "conflict_code": conflict_code,
        "min_confidence": float(profile_out["min_confidence"]),
        "max_confidence": float(profile_out["max_confidence"]),
        "require_debate_bridge": bool(profile_out["require_debate_bridge"]),
        "require_expert_review": bool(profile_out["require_expert_review"]),
    }
