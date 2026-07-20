#!/usr/bin/env python3
"""LEGACY / transitional — prefer Domain bootstrap pipeline.

PeriodO enrich for new packs lives in:
  `python chrystal_2/agents/domain/pipeline.py bootstrap ...`
(actions: enrich_period_shell, stamp_domain_periodo). This CLI keeps the
RR hard-coded WD→PeriodO map for audit replay only — do not grow that map.

Domain — enrich WD Period shells with PeriodO seed (soft).

Maps curated Wikidata Period QIDs under roman_republic to PeriodO seed ids.
Does not bulk-load PeriodO. Pack bounds stay on SubjectDomain.

Usage (repo root):
  python chrystal_2/agents/domain/apply_periodo_enrich.py --domain-id roman_republic --dry-run
  python chrystal_2/agents/domain/apply_periodo_enrich.py --domain-id roman_republic --review-only
  python chrystal_2/agents/domain/apply_periodo_enrich.py --domain-id roman_republic --review-write
  python chrystal_2/agents/domain/apply_periodo_enrich.py --domain-id roman_republic --write
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from neo4j import GraphDatabase

from periodo_tools import periodo_lookup_seed, periodo_resolve_id
from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

PRINCIPLES = Path(__file__).resolve().parent / "PRINCIPLES_PERIODO_ENRICH.md"
INSTANCE = "7fe339d2"

# Curated WD Period shell → PeriodO seed (soft enrich). Explicit — no fuzzy invent.
WD_TO_PERIODO: list[dict[str, Any]] = [
    {
        "qid": "Q2839628",
        "label_hint": "Early Roman Republic",
        "periodo_id": "p06c6g36mkq",
        "soft": True,
        "note": "Early WD shell ↔ LCSH 510-265 PeriodO slice",
    },
    {
        "qid": "Q6106068",
        "label_hint": "Middle Roman Republic",
        "periodo_id": "p06c6g3hb99",
        "soft": True,
        "note": "Middle WD shell ↔ 265-30 PeriodO (overlaps mid+late; soft only)",
    },
    {
        "qid": "Q2815472",
        "label_hint": "Late Roman Republic",
        "periodo_id": "p0jrrjbchh2",
        "soft": True,
        "note": "Late WD shell ↔ Late Roman Republic PeriodO",
    },
]

DOMAIN_PRIMARY = {
    "periodo_id": "p06c6g3p3g3",
    "soft": False,
    "note": "Primary pack chrono PeriodO (full Republic 510-30); stamp on SubjectDomain",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def assert_chrystal_2() -> None:
    if INSTANCE not in (NEO4J_URI or ""):
        raise SystemExit(f"Refusing: not chrystal_2: {NEO4J_URI}")


def load_periods(session, domain_id: str) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: $domain_id})-[r]->(p:Period)
        RETURN p.qid AS qid, p.label AS label, p.periodo_id AS periodo_id,
               p.authority_status AS authority_status, type(r) AS rel
        ORDER BY label
        """,
        domain_id=domain_id,
    ).data()


def build_plan(domain_id: str, existing: list[dict[str, Any]]) -> dict[str, Any]:
    by_qid = {r["qid"]: r for r in existing if r.get("qid")}
    actions: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seed_index = {r["periodo_id"]: r for r in periodo_lookup_seed(domain_id=domain_id)}

    for m in WD_TO_PERIODO:
        qid = m["qid"]
        shell = by_qid.get(qid)
        if not shell:
            skipped.append({"reason": "wd_period_shell_missing", "qid": qid, "label_hint": m["label_hint"]})
            continue
        resolved = seed_index.get(m["periodo_id"]) or periodo_resolve_id(m["periodo_id"])
        if not resolved:
            skipped.append({"reason": "periodo_unresolved", "periodo_id": m["periodo_id"]})
            continue
        if shell.get("periodo_id") == m["periodo_id"]:
            skipped.append(
                {
                    "reason": "already_enriched",
                    "qid": qid,
                    "periodo_id": m["periodo_id"],
                }
            )
            continue
        actions.append(
            {
                "action": "enrich_period_shell",
                "qid": qid,
                "wd_label": shell.get("label"),
                "periodo_id": resolved["periodo_id"],
                "periodo_label": resolved.get("label"),
                "start_year": resolved.get("start_year"),
                "end_year": resolved.get("end_year"),
                "soft": m["soft"],
                "note": m["note"],
                "authority_source": "periodo",
            }
        )

    # Domain primary stamp
    primary = seed_index.get(DOMAIN_PRIMARY["periodo_id"]) or periodo_resolve_id(
        DOMAIN_PRIMARY["periodo_id"]
    )
    if primary:
        actions.append(
            {
                "action": "stamp_domain_periodo",
                "domain_id": domain_id,
                "periodo_id": primary["periodo_id"],
                "periodo_label": primary.get("label"),
                "start_year": primary.get("start_year"),
                "end_year": primary.get("end_year"),
                "soft": DOMAIN_PRIMARY["soft"],
                "note": DOMAIN_PRIMARY["note"],
                "authority_source": "periodo",
            }
        )
    else:
        skipped.append({"reason": "primary_periodo_missing", **DOMAIN_PRIMARY})

    return {"domain_id": domain_id, "actions": actions, "skipped": skipped}


def review_plan(plan: dict[str, Any], model: str = "claude-sonnet-4-5") -> dict[str, Any]:
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit("pip install anthropic") from exc

    client = anthropic.Anthropic(api_key=_anthropic_key())
    payload = {
        "domain_id": plan["domain_id"],
        "actions": [
            {"i": i, **{k: v for k, v in a.items() if k != "action" or True}}
            for i, a in enumerate(plan["actions"])
        ],
        "skipped": plan["skipped"],
    }
    # slim actions for prompt
    for row in payload["actions"]:
        row["action"] = plan["actions"][row["i"]]["action"]

    msg = client.messages.create(
        model=model,
        max_tokens=2000,
        system=PRINCIPLES.read_text(encoding="utf-8"),
        messages=[
            {
                "role": "user",
                "content": "Review PeriodO enrich plan. JSON only with drop_indices.\n\n"
                + json.dumps(payload, ensure_ascii=False, indent=2),
            }
        ],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    review = _extract_json(text)
    drops = review.get("drop_indices") or []
    review["drop_indices"] = [int(x) for x in drops]
    return review


def apply_drops(plan: dict[str, Any], drop_indices: list[int]) -> dict[str, Any]:
    drop = set(drop_indices)
    kept = []
    for i, a in enumerate(plan["actions"]):
        if i in drop:
            plan["skipped"].append({"reason": "llm_periodo_review_drop", "index": i, **a})
        else:
            kept.append(a)
    plan["actions"] = kept
    return plan


def execute(session, plan: dict[str, Any], write: bool) -> dict[str, Any]:
    if not write:
        return {"mode": "dry_run", "actions": plan["actions"], "skipped": plan["skipped"]}

    applied = 0
    for step in plan["actions"]:
        if step["action"] == "enrich_period_shell":
            session.run(
                """
                MATCH (p:Period {qid: $qid})
                SET p.periodo_id = $periodo_id,
                    p.periodo_label = $periodo_label,
                    p.periodo_start_year = $start_year,
                    p.periodo_end_year = $end_year,
                    p.authority_source = $authority_source,
                    p.authority_status = CASE
                      WHEN $soft THEN 'periodo_enriched_soft'
                      ELSE 'periodo_enriched'
                    END,
                    p.soft = $soft,
                    p.periodo_note = $note,
                    p.periodo_enriched_at = $ts,
                    p.provisional = coalesce(p.provisional, true)
                """,
                qid=step["qid"],
                periodo_id=step["periodo_id"],
                periodo_label=step.get("periodo_label"),
                start_year=step.get("start_year"),
                end_year=step.get("end_year"),
                authority_source=step.get("authority_source"),
                soft=bool(step.get("soft")),
                note=step.get("note"),
                ts=_now(),
            )
            applied += 1
        elif step["action"] == "stamp_domain_periodo":
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                SET sd.periodo_id = $periodo_id,
                    sd.periodo_label = $periodo_label,
                    sd.periodo_start_year = $start_year,
                    sd.periodo_end_year = $end_year,
                    sd.periodo_authority = $authority_source,
                    sd.periodo_soft = $soft,
                    sd.periodo_note = $note,
                    sd.periodo_enriched_at = $ts
                """,
                domain_id=step["domain_id"],
                periodo_id=step["periodo_id"],
                periodo_label=step.get("periodo_label"),
                start_year=step.get("start_year"),
                end_year=step.get("end_year"),
                authority_source=step.get("authority_source"),
                soft=bool(step.get("soft")),
                note=step.get("note"),
                ts=_now(),
            )
            applied += 1
        else:
            raise SystemExit(f"unknown action {step['action']}")
    return {
        "mode": "write",
        "applied": applied,
        "actions": plan["actions"],
        "skipped": plan["skipped"],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Enrich WD Period shells with PeriodO seed")
    p.add_argument("--domain-id", default="roman_republic")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--write", action="store_true")
    p.add_argument("--review-only", action="store_true")
    p.add_argument("--review-write", action="store_true")
    args = p.parse_args(argv)

    modes = sum(bool(x) for x in (args.dry_run, args.write, args.review_only, args.review_write))
    if modes != 1:
        print("Use exactly one of --dry-run / --write / --review-only / --review-write")
        return 2

    assert_chrystal_2()
    write = bool(args.write or args.review_write)
    do_review = bool(args.review_only or args.review_write)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            existing = load_periods(session, args.domain_id)
            plan = build_plan(args.domain_id, existing)
            review = None
            if do_review:
                review = review_plan(plan)
                plan = apply_drops(plan, review.get("drop_indices") or [])

            if args.review_only:
                result = {
                    "mode": "review_only",
                    "actions": plan["actions"],
                    "skipped": plan["skipped"],
                    "review": review,
                }
            else:
                result = execute(session, plan, write=write)
                if review is not None:
                    result["review"] = review

            print(
                json.dumps(
                    {
                        "agent": "DOMAIN",
                        "federation": "periodo",
                        "existing_period_shells": existing,
                        **result,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            if write and result.get("applied"):
                print(
                    "\nVERIFY:",
                    json.dumps(load_periods(session, args.domain_id), indent=2),
                )
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
