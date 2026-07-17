"""
IGAR metadata helpers for Military (and other actor-centric Event) claims.

IGAR = Input -> Goal -> Action -> Result
- Optional interpretation layer — NOT required for atomic participation (Q-P-Q)
- Not claim cipher identity, not a predicate
- Year-level temporal fields when known
- Distinct from CIDOC-CRM (predicate) and CRMinf (belief lifecycle)
"""

from __future__ import annotations

import json
from typing import Any


REQUIRED_KEYS = ("input", "goal", "action", "result")
OPTIONAL_YEAR_KEYS = ("input_year", "action_year", "result_year")


def normalize_igar(igar: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a cleaned IGAR dict or None if empty."""
    if not igar:
        return None
    out: dict[str, Any] = {}
    for key in REQUIRED_KEYS:
        val = igar.get(key)
        if val is None:
            continue
        text = str(val).strip()
        if text:
            out[key] = text
    for key in OPTIONAL_YEAR_KEYS:
        if key not in igar or igar[key] is None or igar[key] == "":
            continue
        try:
            out[key] = int(igar[key])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"igar.{key} must be an integer year (BCE negative)") from exc
    return out or None


def validate_igar(
    igar: dict[str, Any] | None,
    *,
    require_complete: bool = False,
) -> list[str]:
    """Return list of validation problems (empty = ok)."""
    problems: list[str] = []
    if not igar:
        if require_complete:
            problems.append("IGAR missing (Input -> Goal -> Action -> Result required)")
        return problems
    for key in REQUIRED_KEYS:
        if not str(igar.get(key) or "").strip():
            problems.append(f"IGAR.{key} empty")
    years = []
    for key in ("input_year", "action_year", "result_year"):
        if key in igar and igar[key] is not None:
            years.append((key, int(igar[key])))
    by_name = dict(years)
    if "input_year" in by_name and "action_year" in by_name:
        if by_name["input_year"] > by_name["action_year"]:
            problems.append("IGAR input_year must be <= action_year")
    if "action_year" in by_name and "result_year" in by_name:
        if by_name["action_year"] > by_name["result_year"]:
            problems.append("IGAR action_year must be <= result_year")
    return problems


def igar_complete(igar: dict[str, Any] | None) -> bool:
    return not validate_igar(igar, require_complete=True)


def igar_to_json(igar: dict[str, Any] | None) -> str | None:
    normalized = normalize_igar(igar)
    if not normalized:
        return None
    return json.dumps(normalized, ensure_ascii=False)


def igar_flat_props(igar: dict[str, Any] | None) -> dict[str, Any]:
    """Flatten IGAR for Neo4j Claim properties + JSON blob."""
    normalized = normalize_igar(igar)
    if not normalized:
        return {
            "igar_json": None,
            "igar_input": None,
            "igar_goal": None,
            "igar_action": None,
            "igar_result": None,
            "igar_input_year": None,
            "igar_action_year": None,
            "igar_result_year": None,
            "igar_complete": False,
        }
    return {
        "igar_json": json.dumps(normalized, ensure_ascii=False),
        "igar_input": normalized.get("input"),
        "igar_goal": normalized.get("goal"),
        "igar_action": normalized.get("action"),
        "igar_result": normalized.get("result"),
        "igar_input_year": normalized.get("input_year"),
        "igar_action_year": normalized.get("action_year"),
        "igar_result_year": normalized.get("result_year"),
        "igar_complete": igar_complete(normalized),
    }


def clear_igar_props() -> dict[str, Any]:
    """Property map used to strip bad/provisional IGAR from a Claim."""
    return igar_flat_props(None)


# Methodical agent stance (inject into Military SFA / pilot prompts)
MILITARY_BATTLE_METHOD_PROMPT = """
Working stance (mandatory):
- Take your time. Be slow and methodical. Do not rush to fill every field.
- Study the battle as a multi-actor Event: consider participants on BOTH sides.
- Prefer fewer well-sourced claims over many thin ones.

Atomic participation (default for FOUGHT_IN / P607):
- Persist language-neutral Wikidata statement: subjectQID-PID-objectQID
  (example: Q36456-P607-Q179591).
- Natural-language labels are optional gloss only.
- IGAR is NOT required for atomic participation.

IGAR (Input -> Goal -> Action -> Result):
- Separate interpretive layer for actor-decision narratives.
- Only attach after slow, source-based research with passage citations.
- Input = triggering condition the actor responds to — not a biography sketch.
- If IGAR cannot yet be justified, omit it and Hold interpretation work.

Gaps:
- Missing Person with real QID -> create via approved entity path, then claim.
- Unclear registry predicate -> predicate_status=tbd, Hold, research_notes.
- Event Place geodata required: Event must have LOCATION_OF_EVENT -> Place with
  lat/long (normally Wikidata P276 + P625). Missing geo -> Hold; do not Validate.
  Backfill: python scripts/system/ensure_event_place_geo.py --event-qid <QID>
- Never invent relationship_type strings or fake QIDs/dates.

Alignment:
- CIDOC-CRM codes come from the relationship registry automatically.
- CRMinf belief lifecycle is Claim status — do not conflate with IGAR.
""".strip()
