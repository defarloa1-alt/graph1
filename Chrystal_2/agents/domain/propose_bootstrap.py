#!/usr/bin/env python3
"""Domain bootstrap propose — one LLM plan for biblio + PeriodO + geo (no Neo write)."""

from __future__ import annotations

import csv
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

from scripts.agents.lcsh_resolve import resolve_lcsh
from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

from periodo_tools import periodo_lookup_seed
from pleiades_tools import pleiades_lookup_seed, pleiades_resolve_qid

try:
    from federation_tools import derive_fast_facets_from_lcsh_heading
except ImportError:
    sys.path.insert(0, str(ROOT / "Chrystal_2" / "agents" / "librarian"))
    from federation_tools import derive_fast_facets_from_lcsh_heading  # type: ignore

AGENT_DIR = Path(__file__).resolve().parent
PRINCIPLES = AGENT_DIR / "PRINCIPLES_BOOTSTRAP.md"
PACKS = ROOT / "JSON" / "wikidata" / "packs"
CROSS = ROOT / "Chrystal_2" / "federations" / "crosswalks"
FED = ROOT / "Chrystal_2" / "federations"
ALLOWED = frozenset(
    {
        "tether_lcsh",
        "tether_fast",
        "align_lcc",
        "enrich_period_shell",
        "stamp_domain_periodo",
        "stamp_place_pleiades",
        "noop",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def neo_snapshot(session, domain_id: str) -> dict[str, Any]:
    sd = session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: $d})
        OPTIONAL MATCH (sd)-[:HAS_LCSH_AUTHORITY]->(h:LCSH_Heading)
        OPTIONAL MATCH (sd)-[:HAS_FAST_AUTHORITY]->(f:FAST_Heading)
        OPTIONAL MATCH (sd)-[:ALIGNED_WITH_LCC]->(l:LCC_Class)
        OPTIONAL MATCH (sd)-[:STARTS_IN_YEAR]->(ys:Year)
        OPTIONAL MATCH (sd)-[:ENDS_IN_YEAR]->(ye:Year)
        OPTIONAL MATCH (sd)-[rp]->(pl:Place)
        RETURN sd.domain_id AS domain_id, sd.label AS label, sd.seed_qid AS seed_qid,
               sd.wd_p244 AS wd_p244, sd.start_year AS start_year, sd.end_year AS end_year,
               sd.periodo_id AS periodo_id, sd.biblio_lcsh_id AS biblio_lcsh_id,
               ys.year AS year_start, ye.year AS year_end,
               collect(DISTINCT {id:h.lcsh_id, label:coalesce(h.label,h.heading)}) AS lcsh,
               collect(DISTINCT {id:f.fast_id, label:coalesce(f.label,f.heading)}) AS fast,
               collect(DISTINCT {id:coalesce(l.class_number,l.code), label:l.label}) AS lcc,
               collect(DISTINCT {
                 qid: pl.qid, label: pl.label, via: type(rp),
                 pleiades_id: pl.pleiades_id, lat: pl.lat, long: pl.long
               }) AS places
        """,
        d=domain_id,
    ).single()
    periods = session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: $d})-[r]->(p:Period)
        RETURN p.qid AS qid, p.label AS label, p.periodo_id AS periodo_id,
               p.authority_status AS authority_status, type(r) AS rel
        """,
        d=domain_id,
    ).data()
    feds = session.run(
        """
        MATCH (fs:SYS_FederationSource)
        RETURN fs.source_id AS source_id, fs.status AS status, fs.tool_names AS tools
        ORDER BY source_id
        """
    ).data()
    out = dict(sd) if sd else {"domain_id": domain_id}
    for key in ("lcsh", "fast", "lcc"):
        out[key] = [x for x in (out.get(key) or []) if x and x.get("id")]
    out["places"] = [x for x in (out.get("places") or []) if x and x.get("qid")]
    out["periods"] = periods
    out["federations"] = feds
    return out


def prefetch_tools(domain: dict[str, Any]) -> dict[str, Any]:
    """Run federation tools once; inject results (LLM does not call HTTP)."""
    domain_id = domain.get("domain_id") or "roman_republic"
    lcsh_id = domain.get("biblio_lcsh_id") or domain.get("wd_p244")
    loc = resolve_lcsh(str(lcsh_id)) if lcsh_id else None
    heading = (loc or {}).get("label") or domain.get("biblio_heading")
    fast = derive_fast_facets_from_lcsh_heading(heading) if heading else []
    place_hits = []
    for pl in domain.get("places") or []:
        qid = pl.get("qid")
        if not qid:
            continue
        hit = pleiades_resolve_qid(str(qid))
        if hit:
            place_hits.append(hit)
    return {
        "loc_fetch_heading": loc,
        "fast_from_heading": fast,
        "periodo_seed": periodo_lookup_seed(domain_id=domain_id),
        "pleiades_seed": pleiades_lookup_seed(domain_id=domain_id),
        "pleiades_for_domain_places": place_hits,
    }


def load_candidates_csv() -> list[dict[str, str]]:
    path = CROSS / "roman_republic_domain_authority_candidates.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def card_summaries() -> list[dict[str, Any]]:
    out = []
    for name in ("lcsh_fast_lcc.json", "periodo.json", "pleiades.json"):
        path = FED / name
        if not path.exists():
            continue
        card = load_json(path)
        out.append(
            {
                "source_id": card.get("source_id"),
                "tool_names": card.get("tool_names"),
                "query_capabilities": card.get("query_capabilities"),
                "notes": card.get("notes"),
            }
        )
    return out


def build_user_payload(
    *,
    qid: str,
    domain_id: str,
    pack: dict[str, Any],
    proposal: dict[str, Any],
    neo: dict[str, Any],
    tools: dict[str, Any],
) -> dict[str, Any]:
    identity = [
        r
        for r in (proposal.get("proposals") or [])
        if r.get("decision") == "identity_tether"
    ]
    return {
        "instruction": (
            "Propose Domain bootstrap actions for biblio + PeriodO + thin Place geo. "
            "Schema structure is already decided in schema_proposal. Return JSON only."
        ),
        "domain_id": domain_id,
        "seed": pack.get("seed"),
        "schema_identity_tethers": identity,
        "neo_snapshot": neo,
        "federation_cards": card_summaries(),
        "tool_results": tools,
        "authority_candidates_csv": load_candidates_csv(),
        "principles_file": "PRINCIPLES_BOOTSTRAP.md",
    }


def validate_plan(plan: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    actions = plan.get("actions")
    if not isinstance(actions, list):
        return ["actions must be a list"]
    for i, a in enumerate(actions):
        if not isinstance(a, dict):
            errs.append(f"actions[{i}] not object")
            continue
        act = a.get("action")
        if act not in ALLOWED:
            errs.append(f"actions[{i}] bad action {act!r}")
        if act != "noop" and not a.get("rationale") and not a.get("note"):
            errs.append(f"actions[{i}] missing rationale/note")
    return errs


def call_llm(system: str, payload: dict[str, Any], model: str) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=_anthropic_key())
    msg = client.messages.create(
        model=model,
        max_tokens=5000,
        system=system,
        messages=[
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, indent=2),
            }
        ],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    return _extract_json(text)


def propose(
    *,
    qid: str,
    domain_id: str,
    model: str = "claude-sonnet-4-5",
) -> dict[str, Any]:
    if "7fe339d2" not in (NEO4J_URI or ""):
        raise SystemExit(f"Refusing: not chrystal_2: {NEO4J_URI}")

    pack_path = PACKS / f"{qid}_pack_library.json"
    prop_path = PACKS / f"{qid}_schema_proposal.json"
    if not pack_path.exists() or not prop_path.exists():
        raise SystemExit(f"Need pack + schema proposal: {pack_path}, {prop_path}")

    pack = load_json(pack_path)
    proposal = load_json(prop_path)
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            neo = neo_snapshot(session, domain_id)
    finally:
        driver.close()

    tools = prefetch_tools(neo)
    payload = build_user_payload(
        qid=qid,
        domain_id=domain_id,
        pack=pack,
        proposal=proposal,
        neo=neo,
        tools=tools,
    )
    system = PRINCIPLES.read_text(encoding="utf-8")
    plan = call_llm(system, payload, model)
    plan.setdefault("_meta", {})
    plan["_meta"].update(
        {
            "mode": "domain_bootstrap_llm",
            "domain_id": domain_id,
            "seed_qid": qid,
            "generated_at": _now(),
            "writes_neo": False,
            "model": model,
            "grounding": [
                "pack_library",
                "schema_proposal",
                "neo_snapshot",
                "federation_cards",
                "tool_results",
            ],
        }
    )
    errs = validate_plan(plan)
    if errs:
        raise SystemExit("Invalid plan:\n- " + "\n- ".join(errs))
    out = PACKS / f"{qid}_domain_bootstrap_plan.json"
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    plan["_meta"]["path"] = str(out.relative_to(ROOT)).replace("\\", "/")
    return plan


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Domain bootstrap propose (biblio+PeriodO)")
    p.add_argument("--qid", required=True)
    p.add_argument("--domain-id", required=True)
    p.add_argument("--model", default="claude-sonnet-4-5")
    args = p.parse_args(argv)
    plan = propose(qid=args.qid.strip().upper(), domain_id=args.domain_id.strip(), model=args.model)
    print(json.dumps({"wrote": plan["_meta"].get("path"), "actions": len(plan.get("actions") or [])}, indent=2))
    print(json.dumps(plan, indent=2, ensure_ascii=False)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
