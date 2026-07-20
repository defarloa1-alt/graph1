#!/usr/bin/env python3
"""Domain — apply a bootstrap plan (biblio + PeriodO + geo). Registry-gated writes."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from neo4j import GraphDatabase

from periodo_tools import periodo_resolve_id
from pleiades_tools import pleiades_resolve_id, pleiades_resolve_qid
from review_bootstrap_plan import apply_review_drops, review_bootstrap_plan
from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

from propose_bootstrap import neo_snapshot, propose

PACKS = ROOT / "JSON" / "wikidata" / "packs"
INSTANCE = "7fe339d2"
REQUIRED_NODES = frozenset(
    {"LCSH_Heading", "FAST_Heading", "LCC_Class", "Period", "SubjectDomain", "Place"}
)
REQUIRED_RELS = frozenset(
    {"HAS_LCSH_AUTHORITY", "HAS_FAST_AUTHORITY", "ALIGNED_WITH_LCC", "CAPITAL"}
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def assert_chrystal_2() -> None:
    if INSTANCE not in (NEO4J_URI or ""):
        raise SystemExit(f"Refusing: not chrystal_2: {NEO4J_URI}")


def load_registry(session) -> tuple[set[str], set[str]]:
    nodes = {
        r["name"]
        for r in session.run("MATCH (n:SYS_NodeType) RETURN n.name AS name")
        if r["name"]
    }
    rels = {
        r["name"]
        for r in session.run("MATCH (r:SYS_RelationshipType) RETURN r.name AS name")
        if r["name"]
    }
    return nodes, rels


def assert_registry(nodes: set[str], rels: set[str]) -> None:
    missing_n = REQUIRED_NODES - nodes
    missing_r = REQUIRED_RELS - rels
    if missing_n or missing_r:
        raise SystemExit(f"Registry gap nodes={sorted(missing_n)} rels={sorted(missing_r)}")


def load_plan(qid: str) -> dict[str, Any]:
    path = PACKS / f"{qid}_domain_bootstrap_plan.json"
    if not path.exists():
        raise SystemExit(f"Missing plan: {path} — run propose first or pipeline bootstrap")
    return json.loads(path.read_text(encoding="utf-8"))


def execute(session, domain_id: str, actions: list[dict[str, Any]], write: bool) -> dict[str, Any]:
    if not write:
        return {"mode": "dry_run", "actions": actions, "applied": 0}

    applied = 0
    for step in actions:
        act = step.get("action")
        if act == "noop":
            continue
        if act == "tether_lcsh":
            session.run(
                """
                MERGE (h:LCSH_Heading {lcsh_id: $lcsh_id})
                SET h.label = coalesce($label, h.label),
                    h.heading = coalesce($label, h.heading),
                    h.uri = coalesce($uri, h.uri),
                    h.source = coalesce(h.source, 'bootstrap'),
                    h.updated_at = datetime()
                WITH h
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                MERGE (sd)-[r:HAS_LCSH_AUTHORITY]->(h)
                SET r.role = $role,
                    r.soft = $soft,
                    r.authority_source = 'lcsh_fast_lcc',
                    r.placed_by = 'domain_bootstrap',
                    r.placed_at = datetime()
                WITH sd
                SET sd.biblio_lcsh_id = coalesce(sd.biblio_lcsh_id, $lcsh_id),
                    sd.biblio_heading = coalesce(sd.biblio_heading, $label),
                    sd.biblio_status = coalesce(sd.biblio_status, 'placed'),
                    sd.biblio_placed_at = coalesce(sd.biblio_placed_at, $ts)
                """,
                domain_id=domain_id,
                lcsh_id=step["lcsh_id"],
                label=step.get("label"),
                uri=step.get("uri"),
                role=step.get("role") or "pack_chrono_aboutness",
                soft=bool(step.get("soft")),
                ts=_now(),
            )
            applied += 1
        elif act == "tether_fast":
            session.run(
                """
                MERGE (f:FAST_Heading {fast_id: $fast_id})
                SET f.label = coalesce($label, f.label),
                    f.heading = coalesce($label, f.heading),
                    f.uri = coalesce($uri, f.uri),
                    f.source = coalesce(f.source, 'bootstrap'),
                    f.soft = $soft,
                    f.updated_at = datetime()
                WITH f
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                MERGE (sd)-[r:HAS_FAST_AUTHORITY]->(f)
                SET r.role = $role,
                    r.soft = $soft,
                    r.chrono_facet = $chrono_facet,
                    r.authority_source = 'lcsh_fast_lcc',
                    r.placed_by = 'domain_bootstrap',
                    r.placed_at = datetime()
                """,
                domain_id=domain_id,
                fast_id=step["fast_id"],
                label=step.get("label"),
                uri=step.get("uri"),
                role=step.get("role") or "soft_facet",
                soft=bool(step.get("soft", True)),
                chrono_facet=step.get("chrono_facet"),
            )
            applied += 1
        elif act == "align_lcc":
            class_number = step.get("class_number") or step.get("code")
            session.run(
                """
                MERGE (l:LCC_Class {class_number: $class_number})
                SET l.code = $class_number,
                    l.label = coalesce($label, l.label),
                    l.uri = coalesce($uri, l.uri),
                    l.source = coalesce(l.source, 'bootstrap'),
                    l.soft = true,
                    l.updated_at = datetime()
                WITH l
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                MERGE (sd)-[r:ALIGNED_WITH_LCC]->(l)
                SET r.role = $role,
                    r.soft = true,
                    r.authority_source = 'lcsh_fast_lcc',
                    r.placed_by = 'domain_bootstrap',
                    r.placed_at = datetime()
                """,
                domain_id=domain_id,
                class_number=class_number,
                label=step.get("label"),
                uri=step.get("uri"),
                role=step.get("role") or "soft_lcc",
            )
            applied += 1
        elif act == "enrich_period_shell":
            resolved = None
            if step.get("periodo_id") and not step.get("periodo_label"):
                resolved = periodo_resolve_id(step["periodo_id"])
            session.run(
                """
                MATCH (p:Period {qid: $qid})
                SET p.periodo_id = $periodo_id,
                    p.periodo_label = coalesce($periodo_label, p.periodo_label),
                    p.periodo_start_year = coalesce($start_year, p.periodo_start_year),
                    p.periodo_end_year = coalesce($end_year, p.periodo_end_year),
                    p.authority_source = 'periodo',
                    p.authority_status = CASE
                      WHEN $soft THEN 'periodo_enriched_soft'
                      ELSE 'periodo_enriched'
                    END,
                    p.soft = $soft,
                    p.periodo_note = coalesce($note, p.periodo_note),
                    p.periodo_enriched_at = $ts,
                    p.provisional = coalesce(p.provisional, true)
                """,
                qid=step["qid"],
                periodo_id=step["periodo_id"],
                periodo_label=step.get("periodo_label")
                or (resolved or {}).get("label"),
                start_year=step.get("start_year") or (resolved or {}).get("start_year"),
                end_year=step.get("end_year") or (resolved or {}).get("end_year"),
                soft=bool(step.get("soft", True)),
                note=step.get("note") or step.get("rationale"),
                ts=_now(),
            )
            applied += 1
        elif act == "stamp_domain_periodo":
            resolved = None
            if step.get("periodo_id") and not step.get("periodo_label"):
                resolved = periodo_resolve_id(step["periodo_id"])
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                SET sd.periodo_id = $periodo_id,
                    sd.periodo_label = coalesce($periodo_label, sd.periodo_label),
                    sd.periodo_start_year = coalesce($start_year, sd.periodo_start_year),
                    sd.periodo_end_year = coalesce($end_year, sd.periodo_end_year),
                    sd.periodo_authority = 'periodo',
                    sd.periodo_soft = $soft,
                    sd.periodo_note = coalesce($note, sd.periodo_note),
                    sd.periodo_enriched_at = $ts
                """,
                domain_id=domain_id,
                periodo_id=step["periodo_id"],
                periodo_label=step.get("periodo_label")
                or (resolved or {}).get("label"),
                start_year=step.get("start_year") or (resolved or {}).get("start_year"),
                end_year=step.get("end_year") or (resolved or {}).get("end_year"),
                soft=bool(step.get("soft")),
                note=step.get("note") or step.get("rationale"),
                ts=_now(),
            )
            applied += 1
        elif act == "stamp_place_pleiades":
            resolved = None
            if step.get("pleiades_id") and (
                step.get("lat") is None or step.get("long") is None
            ):
                resolved = pleiades_resolve_id(str(step["pleiades_id"]))
            elif not step.get("pleiades_id") and step.get("qid"):
                resolved = pleiades_resolve_qid(str(step["qid"]))
            pleiades_id = step.get("pleiades_id") or (resolved or {}).get("pleiades_id")
            if not pleiades_id:
                raise SystemExit(f"stamp_place_pleiades missing pleiades_id for {step}")
            session.run(
                """
                MATCH (p:Place {qid: $qid})
                SET p.pleiades_id = $pleiades_id,
                    p.pleiades_label = coalesce($pleiades_label, p.pleiades_label),
                    p.pleiades_uri = coalesce($uri, p.pleiades_uri),
                    p.lat = coalesce($lat, p.lat),
                    p.long = coalesce($long, p.long),
                    p.place_type = coalesce($place_type, p.place_type),
                    p.geo_authority = 'pleiades',
                    p.geo_soft = $soft,
                    p.geo_role = coalesce($role, p.geo_role),
                    p.geo_note = coalesce($note, p.geo_note),
                    p.geo_enriched_at = $ts,
                    p.authority_status = CASE
                      WHEN $soft THEN 'pleiades_enriched_soft'
                      ELSE 'pleiades_enriched'
                    END
                """,
                qid=step["qid"],
                pleiades_id=str(pleiades_id),
                pleiades_label=step.get("pleiades_label")
                or step.get("label")
                or (resolved or {}).get("label"),
                uri=step.get("uri")
                or (resolved or {}).get("uri")
                or f"https://pleiades.stoa.org/places/{pleiades_id}",
                lat=step.get("lat") if step.get("lat") is not None else (resolved or {}).get("lat"),
                long=step.get("long")
                if step.get("long") is not None
                else (resolved or {}).get("long"),
                place_type=step.get("place_type") or (resolved or {}).get("place_type"),
                soft=bool(step.get("soft")),
                role=step.get("role") or "domain_place",
                note=step.get("note") or step.get("rationale"),
                ts=_now(),
            )
            applied += 1
        else:
            raise SystemExit(f"unknown action: {act}")

    return {"mode": "write", "actions": actions, "applied": applied}


def run_bootstrap(
    *,
    qid: str,
    domain_id: str,
    mode: str,
    model: str = "claude-sonnet-4-5",
    reuse_plan: bool = False,
) -> dict[str, Any]:
    """mode: dry_run | review_only | review_write"""
    assert_chrystal_2()
    qid = qid.strip().upper()
    domain_id = domain_id.strip()

    if reuse_plan:
        plan = load_plan(qid)
    else:
        plan = propose(qid=qid, domain_id=domain_id, model=model)

    actions = list(plan.get("actions") or [])
    skipped: list[dict[str, Any]] = []
    review = None

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            nodes, rels = load_registry(session)
            assert_registry(nodes, rels)
            snap = neo_snapshot(session, domain_id)

            if mode in ("review_only", "review_write"):
                review = review_bootstrap_plan(
                    domain_id=domain_id,
                    actions=actions,
                    neo_snapshot=snap,
                    model=model,
                )
                actions, skipped = apply_review_drops(
                    actions, review.get("drop_indices") or []
                )

            if mode == "review_only":
                result: dict[str, Any] = {
                    "mode": "review_only",
                    "actions": actions,
                    "skipped": skipped,
                    "review": review,
                    "plan_path": (plan.get("_meta") or {}).get("path"),
                }
            else:
                write = mode == "review_write"
                # dry_run also allowed without review
                if mode == "dry_run":
                    write = False
                result = execute(session, domain_id, actions, write=write)
                result["skipped"] = skipped
                if review is not None:
                    result["review"] = review
                result["plan_path"] = (plan.get("_meta") or {}).get("path")
                if write:
                    result["neo_after"] = neo_snapshot(session, domain_id)

            result["agent"] = "DOMAIN"
            result["pipeline"] = "bootstrap"
            result["domain_id"] = domain_id
            result["seed_qid"] = qid
            return result
    finally:
        driver.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Apply Domain bootstrap plan")
    p.add_argument("--qid", required=True)
    p.add_argument("--domain-id", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--review-only", action="store_true")
    p.add_argument("--review-write", action="store_true")
    p.add_argument("--reuse-plan", action="store_true", help="Skip propose; use existing JSON")
    p.add_argument("--model", default="claude-sonnet-4-5")
    args = p.parse_args(argv)

    modes = sum(bool(x) for x in (args.dry_run, args.review_only, args.review_write))
    if modes != 1:
        print("Use exactly one of --dry-run / --review-only / --review-write")
        return 2
    mode = (
        "review_write"
        if args.review_write
        else "review_only"
        if args.review_only
        else "dry_run"
    )
    result = run_bootstrap(
        qid=args.qid,
        domain_id=args.domain_id,
        mode=mode,
        model=args.model,
        reuse_plan=args.reuse_plan,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
