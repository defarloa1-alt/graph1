#!/usr/bin/env python3
"""Readonly acceptance payload: Domain timeline lanes + sidebar.

Future UI contract for roman_republic (and later packs):
  - X = years
  - Y = Kingdom / Republic / Empire bars; Republic HAS_PART Early/Middle/Late
  - Sidebar = biblio tether, capital, replaces Kingdom, followed by Empire,
              part of Ancient Rome

Usage:
  python chrystal_2/agents/domain/acceptance_view.py --domain-id roman_republic
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

INSTANCE = "7fe339d2"

# Primary story QIDs for this acceptance vignette (not exclusive claims).
KINGDOM = "Q201038"
EMPIRE = "Q2277"
ANCIENT_ROME = "Q1747689"
EARLY = "Q2839628"
MIDDLE = "Q6106068"
LATE = "Q2815472"


def assert_chrystal_2() -> None:
    if INSTANCE not in (NEO4J_URI or ""):
        raise SystemExit(f"Refusing: not chrystal_2: {NEO4J_URI}")


def period_row(session, qid: str) -> dict[str, Any] | None:
    row = session.run(
        """
        MATCH (p:Period {qid: $qid})
        OPTIONAL MATCH (p)-[:STARTS_IN_YEAR]->(ys:Year)
        OPTIONAL MATCH (p)-[:ENDS_IN_YEAR]->(ye:Year)
        RETURN p.qid AS qid, p.label AS label,
               coalesce(p.start_year, ys.year) AS start_year,
               coalesce(p.end_year, ye.year) AS end_year,
               p.periodo_id AS periodo_id,
               p.year_source AS year_source,
               p.years_soft AS soft,
               p.authority_status AS status
        """,
        qid=qid,
    ).single()
    return dict(row) if row else None


def build_view(session, domain_id: str) -> dict[str, Any]:
    dom = session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: $d})
        OPTIONAL MATCH (sd)-[:STARTS_IN_YEAR]->(ys:Year)
        OPTIONAL MATCH (sd)-[:ENDS_IN_YEAR]->(ye:Year)
        OPTIONAL MATCH (sd)-[:HAS_LCSH_AUTHORITY]->(h:LCSH_Heading)
        OPTIONAL MATCH (sd)-[:HAS_FAST_AUTHORITY]->(f:FAST_Heading)
        OPTIONAL MATCH (sd)-[:ALIGNED_WITH_LCC]->(l:LCC_Class)
        OPTIONAL MATCH (sd)-[:CAPITAL]->(c:Place)
        OPTIONAL MATCH (sd)-[:REPLACES]->(prev:Period)
        OPTIONAL MATCH (sd)-[:FOLLOWED_BY]->(nxt:Period)
        OPTIONAL MATCH (sd)-[:PART_OF]->(parent:Period)
        OPTIONAL MATCH (sd)-[:HAS_PART]->(child:Period)
        RETURN sd.domain_id AS domain_id, sd.label AS label, sd.seed_qid AS seed_qid,
               coalesce(sd.start_year, ys.year) AS start_year,
               coalesce(sd.end_year, ye.year) AS end_year,
               sd.periodo_id AS periodo_id, sd.periodo_label AS periodo_label,
               collect(DISTINCT {id:h.lcsh_id, label:coalesce(h.label,h.heading)}) AS lcsh,
               collect(DISTINCT {id:f.fast_id, label:coalesce(f.label,f.heading)}) AS fast,
               collect(DISTINCT {id:coalesce(l.class_number,l.code), label:l.label}) AS lcc,
               collect(DISTINCT {
                 qid:c.qid, label:c.label,
                 pleiades_id:c.pleiades_id, lat:c.lat, long:c.long,
                 geo_authority:c.geo_authority
               }) AS capital,
               collect(DISTINCT {qid:prev.qid, label:prev.label}) AS replaces,
               collect(DISTINCT {qid:nxt.qid, label:nxt.label}) AS followed_by,
               collect(DISTINCT {qid:parent.qid, label:parent.label}) AS part_of,
               collect(DISTINCT {qid:child.qid, label:child.label}) AS has_part
        """,
        d=domain_id,
    ).single()
    if not dom:
        raise SystemExit(f"SubjectDomain not found: {domain_id}")

    def clean(rows: list, key: str = "id") -> list[dict]:
        out = []
        for x in rows or []:
            if not x:
                continue
            if x.get(key) or x.get("qid"):
                out.append(x)
        return out

    kingdom = period_row(session, KINGDOM)
    empire = period_row(session, EMPIRE)
    ancient = period_row(session, ANCIENT_ROME)
    children = []
    for qid, lane in ((EARLY, "early"), (MIDDLE, "middle"), (LATE, "late")):
        row = period_row(session, qid)
        if row:
            row["lane"] = lane
            children.append(row)

    timeline = {
        "x_axis": "year",
        "lanes": [
            {
                "row": 0,
                "lane_id": "kingdom",
                "label": (kingdom or {}).get("label") or "Roman Kingdom",
                "qid": KINGDOM,
                "start_year": (kingdom or {}).get("start_year"),
                "end_year": (kingdom or {}).get("end_year"),
                "drawable": bool(
                    kingdom and kingdom.get("start_year") is not None and kingdom.get("end_year") is not None
                ),
                "year_source": (kingdom or {}).get("year_source"),
            },
            {
                "row": 1,
                "lane_id": "republic",
                "label": dom["label"],
                "domain_id": domain_id,
                "seed_qid": dom["seed_qid"],
                "start_year": dom["start_year"],
                "end_year": dom["end_year"],
                "drawable": dom["start_year"] is not None and dom["end_year"] is not None,
                "year_source": "subject_domain_pack",
                "children": [
                    {
                        "lane_id": c["lane"],
                        "label": c.get("label"),
                        "qid": c.get("qid"),
                        "start_year": c.get("start_year"),
                        "end_year": c.get("end_year"),
                        "drawable": c.get("start_year") is not None and c.get("end_year") is not None,
                        "periodo_id": c.get("periodo_id"),
                        "year_source": c.get("year_source"),
                        "soft": c.get("soft"),
                    }
                    for c in children
                ],
            },
            {
                "row": 2,
                "lane_id": "empire",
                "label": (empire or {}).get("label") or "Roman Empire",
                "qid": EMPIRE,
                "start_year": (empire or {}).get("start_year"),
                "end_year": (empire or {}).get("end_year"),
                "drawable": bool(
                    empire and empire.get("start_year") is not None and empire.get("end_year") is not None
                ),
                "year_source": (empire or {}).get("year_source"),
            },
        ],
        "broader_frame": {
            "lane_id": "ancient_rome",
            "label": (ancient or {}).get("label") or "Ancient Rome",
            "qid": ANCIENT_ROME,
            "start_year": (ancient or {}).get("start_year"),
            "end_year": (ancient or {}).get("end_year"),
            "drawable": bool(
                ancient
                and ancient.get("start_year") is not None
                and ancient.get("end_year") is not None
            ),
            "year_source": (ancient or {}).get("year_source"),
            "role": "part_of_parent",
        },
    }

    sidebar = {
        "domain_id": domain_id,
        "label": dom["label"],
        "years": {"start": dom["start_year"], "end": dom["end_year"]},
        "biblio": {
            "lcsh": clean(list(dom["lcsh"])),
            "fast": clean(list(dom["fast"])),
            "lcc": clean(list(dom["lcc"])),
            "periodo_primary": {
                "periodo_id": dom.get("periodo_id"),
                "label": dom.get("periodo_label"),
            },
        },
        "capital": clean(list(dom["capital"]), key="qid"),
        "replaces": [x for x in clean(list(dom["replaces"]), key="qid") if x.get("qid") == KINGDOM]
        or clean(list(dom["replaces"]), key="qid"),
        "followed_by": [x for x in clean(list(dom["followed_by"]), key="qid") if x.get("qid") == EMPIRE]
        or clean(list(dom["followed_by"]), key="qid"),
        "part_of": [x for x in clean(list(dom["part_of"]), key="qid") if x.get("qid") == ANCIENT_ROME]
        or clean(list(dom["part_of"]), key="qid"),
        "has_part": clean(list(dom["has_part"]), key="qid"),
    }

    capital_mappable = any(
        x.get("qid") == "Q220"
        and x.get("pleiades_id")
        and x.get("lat") is not None
        and x.get("long") is not None
        for x in sidebar["capital"]
    )

    checks = {
        "timeline_primary_drawable": all(
            lane.get("drawable") for lane in timeline["lanes"]
        ),
        "republic_children_drawable": all(
            c.get("drawable") for c in timeline["lanes"][1]["children"]
        ),
        "sidebar_has_biblio": bool(sidebar["biblio"]["lcsh"]),
        "sidebar_has_capital": bool(sidebar["capital"]),
        "sidebar_capital_mappable": capital_mappable,
        "sidebar_replaces_kingdom": any(x.get("qid") == KINGDOM for x in sidebar["replaces"]),
        "sidebar_followed_by_empire": any(x.get("qid") == EMPIRE for x in sidebar["followed_by"]),
        "sidebar_part_of_ancient_rome": any(
            x.get("qid") == ANCIENT_ROME for x in sidebar["part_of"]
        ),
    }
    checks["pass"] = all(checks.values())

    return {
        "acceptance": "domain_timeline_sidebar_v1",
        "domain_id": domain_id,
        "checks": checks,
        "timeline": timeline,
        "sidebar": sidebar,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Domain timeline+sidebar acceptance view")
    p.add_argument("--domain-id", default="roman_republic")
    args = p.parse_args(argv)
    assert_chrystal_2()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            view = build_view(session, args.domain_id)
    finally:
        driver.close()
    print(json.dumps(view, indent=2, ensure_ascii=False, default=str))
    return 0 if view["checks"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
