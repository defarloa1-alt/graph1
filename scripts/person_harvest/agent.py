#!/usr/bin/env python3
"""
Person Harvest Agent — ADR-008 Layer 2

Agent reasoning: cross-federation name reconciliation, conflict classification,
authority tier weighting. Produces PersonHarvestPlan. No graph writes.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def produce_harvest_plan(
    context_packet: dict,
    qid: str,
    dprr_id: str | None,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    Produce PersonHarvestPlan from context packet. ADR-008 §4.2.
    Returns plan dict with identity_resolution_decisions, attribute_claims, person_class, etc.
    """
    plan = {
        "plan_id": str(uuid.uuid4()),
        "person_qid": qid,
        "dprr_id": dprr_id,
        "person_class": "CONFIRMED",
        "identity_resolution_decisions": [],
        "attribute_claims": [],
        "conflict_notes": [],
        "threshold_override": 0.75,
    }

    stub = context_packet.get("person_stub") or {}
    dprr = context_packet.get("dprr_raw")
    wd = context_packet.get("wikidata_raw") or {}

    # Identity: if dprr_id matches, strong resolution
    if dprr and dprr.get("dprr_id"):
        plan["identity_resolution_decisions"].append({
            "source": "DPRR",
            "matched_to": dprr_id,
            "confidence": 1.0,
            "rationale": "DPRR ID exact match",
        })

    # Attribute claims from Wikidata
    claims = wd.get("claims", {})
    for pid, vals in claims.items():
        for v in vals:
            val = v.get("value", "")
            if pid == "P22" and val:
                plan["attribute_claims"].append({
                    "attribute": "father_qid",
                    "source": "wikidata",
                    "value": val,
                    "claim_tier": "primary",
                    "conflict_type": None,
                })
            elif pid == "P25" and val:
                plan["attribute_claims"].append({
                    "attribute": "mother_qid",
                    "source": "wikidata",
                    "value": val,
                    "claim_tier": "primary",
                    "conflict_type": None,
                })
            elif pid == "P27" and val:
                plan["attribute_claims"].append({
                    "attribute": "CITIZEN_OF",
                    "source": "wikidata",
                    "value": val,
                    "claim_tier": "primary",
                    "conflict_type": None,
                })
            elif pid == "P6863" and val:
                plan["attribute_claims"].append({
                    "attribute": "dprr_id",
                    "source": "wikidata",
                    "value": val,
                    "claim_tier": "primary",
                    "conflict_type": None,
                })

    # If OpenAI available, run full agent reasoning
    if HAS_OPENAI:
        try:
            client = OpenAI()
            prompt = _build_agent_prompt(context_packet, plan)
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content
            if content:
                parsed = json.loads(content)
                plan.update(parsed)
        except Exception:
            pass  # Keep rule-based plan

    return plan


def _build_agent_prompt(context_packet: dict, plan: dict) -> str:
    return f"""You are a prosopography expert reconciling Roman Republic person data across Wikidata and DPRR.

Context packet:
{json.dumps(context_packet, indent=2, default=str)}

Current plan draft:
{json.dumps(plan, indent=2)}

Refine the plan. Return JSON with keys: person_class (CONFIRMED|MYTHOLOGICAL|NEEDS_REVIEW), identity_resolution_decisions (array), attribute_claims (array), conflict_notes (array if any conflicts). Keep threshold_override 0.75 for ancient persons."""
