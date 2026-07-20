#!/usr/bin/env python3
"""LEGACY / transitional — prefer Domain bootstrap `stamp_place_pleiades`.

New packs: `python chrystal_2/agents/domain/pipeline.py bootstrap ...`
This CLI remains for replay/debug only.

Stamp soft Pleiades id + coords on Domain-linked Place shells.

Local seed/dump first. Does not mint Places — enriches existing WD shells.

Usage (repo root):
  python chrystal_2/agents/domain/stamp_place_geo.py --domain-id roman_republic --dry-run
  python chrystal_2/agents/domain/stamp_place_geo.py --domain-id roman_republic --write
"""

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

from pleiades_tools import (
    pleiades_lookup_seed,
    pleiades_resolve_id,
    pleiades_resolve_qid,
)
from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

INSTANCE = "7fe339d2"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def assert_chrystal_2() -> None:
    if INSTANCE not in (NEO4J_URI or ""):
        raise SystemExit(f"Refusing: not chrystal_2: {NEO4J_URI}")


def load_places(session, domain_id: str) -> list[dict[str, Any]]:
    return session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: $d})-[r]->(p:Place)
        RETURN type(r) AS via_rel, p.qid AS qid, p.label AS label,
               p.pleiades_id AS pleiades_id, p.lat AS lat, p.long AS long
        ORDER BY via_rel, label
        """,
        d=domain_id,
    ).data()


def build_plan(domain_id: str, places: list[dict[str, Any]]) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seed_by_qid = {
        (r.get("wd_qid") or "").upper(): r
        for r in pleiades_lookup_seed(domain_id=domain_id)
        if r.get("wd_qid")
    }

    for place in places:
        qid = (place.get("qid") or "").strip().upper()
        if not qid:
            skipped.append({"reason": "place_missing_qid", **place})
            continue
        if place.get("pleiades_id") and place.get("lat") is not None and place.get("long") is not None:
            skipped.append({"reason": "already_enriched", "qid": qid, "label": place.get("label")})
            continue

        resolved = seed_by_qid.get(qid) or pleiades_resolve_qid(qid)
        if not resolved and place.get("pleiades_id"):
            resolved = pleiades_resolve_id(str(place["pleiades_id"]))
        if not resolved or not resolved.get("pleiades_id"):
            skipped.append({"reason": "pleiades_unresolved", "qid": qid, "label": place.get("label")})
            continue

        actions.append(
            {
                "action": "stamp_place_pleiades",
                "qid": qid,
                "label": place.get("label") or resolved.get("label"),
                "via_rel": place.get("via_rel"),
                "pleiades_id": str(resolved["pleiades_id"]),
                "pleiades_label": resolved.get("label"),
                "lat": resolved.get("lat"),
                "long": resolved.get("long"),
                "place_type": resolved.get("place_type"),
                "uri": resolved.get("uri")
                or f"https://pleiades.stoa.org/places/{resolved['pleiades_id']}",
                "soft": bool(resolved.get("soft", False)),
                "role": resolved.get("role") or "domain_place",
                "note": resolved.get("note") or "Pleiades soft enrich on WD Place shell",
                "authority_source": "pleiades",
            }
        )
    return {"domain_id": domain_id, "actions": actions, "skipped": skipped}


def execute(session, plan: dict[str, Any], write: bool) -> dict[str, Any]:
    if not write:
        return {"mode": "dry_run", **plan}

    applied = 0
    for step in plan["actions"]:
        session.run(
            """
            MATCH (p:Place {qid: $qid})
            SET p.pleiades_id = $pleiades_id,
                p.pleiades_label = $pleiades_label,
                p.pleiades_uri = $uri,
                p.lat = $lat,
                p.long = $long,
                p.place_type = coalesce($place_type, p.place_type),
                p.geo_authority = $authority_source,
                p.geo_soft = $soft,
                p.geo_role = $role,
                p.geo_note = $note,
                p.geo_enriched_at = $ts,
                p.authority_status = CASE
                  WHEN $soft THEN 'pleiades_enriched_soft'
                  ELSE 'pleiades_enriched'
                END
            """,
            qid=step["qid"],
            pleiades_id=step["pleiades_id"],
            pleiades_label=step.get("pleiades_label"),
            uri=step.get("uri"),
            lat=step.get("lat"),
            long=step.get("long"),
            place_type=step.get("place_type"),
            authority_source=step.get("authority_source"),
            soft=bool(step.get("soft")),
            role=step.get("role"),
            note=step.get("note"),
            ts=_now(),
        )
        applied += 1
    return {"mode": "write", "applied": applied, **plan}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Stamp Pleiades id+coords on Domain Places")
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
            places = load_places(session, args.domain_id)
            plan = build_plan(args.domain_id, places)
            result = execute(session, plan, write=args.write)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
