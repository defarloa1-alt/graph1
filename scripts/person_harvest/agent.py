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
    claims = wd.get("claims", {})

    # MythologicalPerson: P31 = mythical/fictional character → do not traverse (ADR-008)
    MYTHOLOGICAL_P31 = {"Q4271324", "Q95074", "Q178885"}  # mythical character, fictional character, deity
    p31_vals = claims.get("P31", [])
    for v in p31_vals:
        inst = (v.get("value") or "").upper()
        if inst in MYTHOLOGICAL_P31:
            plan["person_class"] = "MYTHOLOGICAL"
            break

    # Parent sex (P21) for P40 child_qid → FATHER_OF vs MOTHER_OF vs PARENT_OF
    plan["parent_sex"] = None
    p21_vals = claims.get("P21", [])
    if p21_vals:
        sex_qid = (p21_vals[0].get("value") or "").upper()
        if sex_qid in ("Q6581097", "Q6581072"):  # male, female
            plan["parent_sex"] = "male" if sex_qid == "Q6581097" else "female"

    # Identity: if dprr_id matches, strong resolution
    if dprr and dprr.get("dprr_id"):
        plan["identity_resolution_decisions"].append({
            "source": "DPRR",
            "matched_to": dprr_id,
            "confidence": 1.0,
            "rationale": "DPRR ID exact match",
        })

    # Attribute claims from Wikidata
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
            elif pid == "P3373" and val:
                plan["attribute_claims"].append({
                    "attribute": "sibling_qid",
                    "source": "wikidata",
                    "value": val,
                    "claim_tier": "primary",
                    "conflict_type": None,
                })
            elif pid == "P26" and val:
                plan["attribute_claims"].append({
                    "attribute": "spouse_qid",
                    "source": "wikidata",
                    "value": val,
                    "claim_tier": "primary",
                    "conflict_type": None,
                })
            elif pid == "P40" and val:
                # Parent's perspective: (parent)-[:FATHER_OF|MOTHER_OF|PARENT_OF]->(child)
                plan["attribute_claims"].append({
                    "attribute": "child_qid",
                    "source": "wikidata",
                    "value": val,
                    "claim_tier": "primary",
                    "conflict_type": None,
                })
            elif pid == "P3448" and val:
                plan["attribute_claims"].append({
                    "attribute": "stepparent_qid",
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
