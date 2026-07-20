#!/usr/bin/env python3
"""Stamp drawable start/end years on Domain-linked Period shells.

Sources (in order of preference per shell):
  1. Existing PeriodO enrichment props (periodo_start_year / periodo_end_year)
  2. Wikidata P580/P582 then P571/P576 (federation lookup)

Also MERGEs STARTS_IN_YEAR / ENDS_IN_YEAR to Year backbone when years exist.

Refuses unless NEO4J_URI hosts 7fe339d2.

Usage (repo root):
  python chrystal_2/agents/domain/stamp_period_years.py --domain-id roman_republic --dry-run
  python chrystal_2/agents/domain/stamp_period_years.py --domain-id roman_republic --write
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

INSTANCE = "7fe339d2"
UA = "Chrystal2-Domain/0.1 (local research; roman_republic acceptance)"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def assert_chrystal_2() -> None:
    if INSTANCE not in (NEO4J_URI or ""):
        raise SystemExit(f"Refusing: not chrystal_2: {NEO4J_URI}")


def wd_time_year(claims: dict[str, Any], pid: str) -> int | None:
    arr = claims.get(pid) or []
    if not arr:
        return None
    preferred = [c for c in arr if c.get("rank") == "preferred"] or [
        c for c in arr if c.get("rank") != "deprecated"
    ]
    if not preferred:
        return None
    sn = preferred[0].get("mainsnak") or {}
    v = (sn.get("datavalue") or {}).get("value") or {}
    t = v.get("time") or ""
    if not t or t[0] not in "+-":
        return None
    sign = -1 if t[0] == "-" else 1
    try:
        return sign * int(t[1:5])
    except ValueError:
        return None


def wd_fetch_years(qids: list[str]) -> dict[str, dict[str, Any]]:
    if not qids:
        return {}
    ids = "|".join(sorted(set(qids)))
    url = (
        "https://www.wikidata.org/w/api.php"
        f"?action=wbgetentities&ids={ids}&props=claims|labels&languages=en&format=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    out: dict[str, dict[str, Any]] = {}
    for qid, ent in (data.get("entities") or {}).items():
        claims = ent.get("claims") or {}
        start = wd_time_year(claims, "P580") or wd_time_year(claims, "P571")
        end = wd_time_year(claims, "P582") or wd_time_year(claims, "P576")
        out[qid] = {
            "label": ((ent.get("labels") or {}).get("en") or {}).get("value"),
            "start_year": start,
            "end_year": end,
            "source": "wikidata",
        }
    return out


def load_period_shells(session, domain_id: str) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: $d})-[r]->(p:Period)
        RETURN DISTINCT p.qid AS qid, p.label AS label,
               p.start_year AS start_year, p.end_year AS end_year,
               p.periodo_id AS periodo_id,
               p.periodo_start_year AS periodo_start_year,
               p.periodo_end_year AS periodo_end_year,
               p.authority_status AS authority_status,
               type(r) AS via_rel
        ORDER BY label
        """,
        d=domain_id,
    ).data()


def resolve_bounds(shell: dict[str, Any], wd: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return start/end + provenance, or None if already stamped / unresolved."""
    if shell.get("start_year") is not None and shell.get("end_year") is not None:
        return None  # already drawable

    if shell.get("periodo_start_year") is not None and shell.get("periodo_end_year") is not None:
        return {
            "qid": shell["qid"],
            "label": shell.get("label"),
            "start_year": int(shell["periodo_start_year"]),
            "end_year": int(shell["periodo_end_year"]),
            "year_source": "periodo",
            "soft": True,
            "note": f"promote PeriodO {shell.get('periodo_id')}",
        }

    if wd and (wd.get("start_year") is not None or wd.get("end_year") is not None):
        return {
            "qid": shell["qid"],
            "label": shell.get("label") or wd.get("label"),
            "start_year": wd.get("start_year"),
            "end_year": wd.get("end_year"),
            "year_source": "wikidata",
            "soft": True,
            "note": "WD P580/P582 or P571/P576",
        }
    return {
        "qid": shell["qid"],
        "label": shell.get("label"),
        "unresolved": True,
        "note": "no PeriodO years and no WD inception/end",
    }


def build_plan(shells: list[dict[str, Any]], wd_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for shell in shells:
        qid = shell.get("qid")
        if not qid or qid in seen:
            continue
        seen.add(qid)
        if shell.get("start_year") is not None and shell.get("end_year") is not None:
            skipped.append({"reason": "already_has_years", "qid": qid, "label": shell.get("label")})
            continue
        row = resolve_bounds(shell, wd_map.get(qid))
        if not row:
            continue
        if row.get("unresolved"):
            skipped.append({"reason": "unresolved", **row})
            continue
        if row.get("start_year") is None and row.get("end_year") is None:
            skipped.append({"reason": "empty_bounds", **row})
            continue
        actions.append({"action": "stamp_period_years", **row})
    return {"actions": actions, "skipped": skipped}


def execute(session, plan: dict[str, Any], write: bool) -> dict[str, Any]:
    if not write:
        return {"mode": "dry_run", **plan}

    applied = 0
    for step in plan["actions"]:
        session.run(
            """
            MATCH (p:Period {qid: $qid})
            SET p.start_year = $start_year,
                p.end_year = $end_year,
                p.year_source = $year_source,
                p.years_soft = $soft,
                p.years_note = $note,
                p.years_stamped_at = $ts
            WITH p
            FOREACH (_ IN CASE WHEN $start_year IS NULL THEN [] ELSE [1] END |
              MERGE (ys:Year {year: $start_year})
              MERGE (p)-[:STARTS_IN_YEAR]->(ys)
            )
            FOREACH (_ IN CASE WHEN $end_year IS NULL THEN [] ELSE [1] END |
              MERGE (ye:Year {year: $end_year})
              MERGE (p)-[:ENDS_IN_YEAR]->(ye)
            )
            """,
            qid=step["qid"],
            start_year=step.get("start_year"),
            end_year=step.get("end_year"),
            year_source=step.get("year_source"),
            soft=bool(step.get("soft")),
            note=step.get("note"),
            ts=_now(),
        )
        applied += 1
    return {"mode": "write", "applied": applied, **plan}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Stamp Period start/end years for timeline readiness")
    p.add_argument("--domain-id", default="roman_republic")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--write", action="store_true")
    args = p.parse_args(argv)
    if sum(bool(x) for x in (args.dry_run, args.write)) != 1:
        print("Use exactly one of --dry-run / --write")
        return 2

    assert_chrystal_2()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            shells = load_period_shells(session, args.domain_id)
            need_wd = [
                s["qid"]
                for s in shells
                if s.get("qid")
                and (s.get("start_year") is None or s.get("end_year") is None)
                and (s.get("periodo_start_year") is None or s.get("periodo_end_year") is None)
            ]
            wd_map = wd_fetch_years(need_wd)
            plan = build_plan(shells, wd_map)
            plan["domain_id"] = args.domain_id
            plan["wd_lookups"] = wd_map
            result = execute(session, plan, write=args.write)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
