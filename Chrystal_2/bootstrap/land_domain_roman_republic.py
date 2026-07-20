#!/usr/bin/env python3
"""Land inert Roman Republic SubjectDomain shell on Chrystal 2.

SubjectDomain IS the pack (see architecture/TERMINOLOGY.md).

Creates a minimal shell from the pack library (or statements fallback):
  - SubjectDomain {domain_id:roman_republic} with start/end Year edges
  - 18 inert SFASlot nodes
  - reference_json → JSON/wikidata/packs/Q17167_pack_library.json

Schema specialist applies properties / first-class nodes from the pack library
(see chrystal_2/harvest/). This script does NOT invent schema from WD by hand.

Usage (repo root):
  python chrystal_2/bootstrap/land_domain_roman_republic.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

WD_JSON = ROOT / "JSON" / "wikidata" / "packs" / "Q17167_pack_library.json"
# Fallback if pack library not built yet
WD_STATEMENTS = (
    ROOT / "JSON" / "wikidata" / "statements" / "Q17167_statements_full.json"
)

DOMAIN_ID = "roman_republic"
SEED_QID = "Q17167"
LEGACY_SUBJECT_ID = "domain_roman_republic"

FACET_KEYS = [
    "ARCHAEOLOGICAL",
    "ARTISTIC",
    "BIOGRAPHIC",
    "COMMUNICATION",
    "CULTURAL",
    "DEMOGRAPHIC",
    "DIPLOMATIC",
    "ECONOMIC",
    "ENVIRONMENTAL",
    "GEOGRAPHIC",
    "INTELLECTUAL",
    "LINGUISTIC",
    "MILITARY",
    "POLITICAL",
    "RELIGIOUS",
    "SCIENTIFIC",
    "SOCIAL",
    "TECHNOLOGICAL",
]


def _wd_year(time_obj: dict[str, Any] | None) -> int | None:
    if not time_obj or not isinstance(time_obj, dict):
        return None
    raw = time_obj.get("time") or ""
    if not raw or raw[0] not in "+-":
        return None
    sign = -1 if raw[0] == "-" else 1
    try:
        y = int(raw[1:5])
    except ValueError:
        return None
    return sign * y


def _first_mainsnak_value(claims: dict[str, list], pid: str) -> Any:
    stmts = claims.get(pid) or []
    if not stmts:
        return None
    return (stmts[0].get("mainsnak") or {}).get("value")


def _instance_of_labels(claims: dict[str, list]) -> list[str]:
    out: list[str] = []
    for s in claims.get("P31") or []:
        lab = (s.get("mainsnak") or {}).get("value_label")
        if lab:
            out.append(lab)
    return out


def load_pack_or_statements(path: Path) -> tuple[dict[str, Any], dict[str, list], str]:
    """Return (seed_info, claims, reference_rel_path). Accepts pack library or statements JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("_meta") or {}
    if not meta.get("labeled"):
        raise SystemExit(f"WD JSON is not labeled: {path}")

    if "statements" in data and isinstance(data["statements"], dict):
        seed = data.get("seed") or {}
        qid = seed.get("qid")
        claims = (data["statements"].get("claims")) or {}
        seed_info = {
            "qid": qid,
            "label": seed.get("label"),
            "description": seed.get("description"),
            "statement_count": data.get("counts", {}).get("statements")
            or data["statements"].get("statement_count"),
            "property_count": data.get("counts", {}).get("properties")
            or data["statements"].get("property_count"),
        }
    else:
        qid = data.get("qid")
        claims = data.get("claims") or {}
        seed_info = {
            "qid": qid,
            "label": data.get("label"),
            "description": data.get("description"),
            "statement_count": data.get("statement_count"),
            "property_count": data.get("property_count"),
        }

    if qid != SEED_QID:
        raise SystemExit(f"Expected qid {SEED_QID}, got {qid}")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    return seed_info, claims, rel


def main() -> int:
    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}")
        return 2

    source = WD_JSON if WD_JSON.exists() else WD_STATEMENTS
    if not source.exists():
        print(f"Missing pack library and statements: {WD_JSON} / {WD_STATEMENTS}")
        return 2

    seed_info, claims, rel_path = load_pack_or_statements(source)

    start_year = _wd_year(_first_mainsnak_value(claims, "P571")) or _wd_year(
        _first_mainsnak_value(claims, "P580")
    )
    end_year = _wd_year(_first_mainsnak_value(claims, "P576")) or _wd_year(
        _first_mainsnak_value(claims, "P582")
    )
    # Minimal shell only — schema specialist applies the rest from pack library
    p31 = _instance_of_labels(claims)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            # Drop legacy :Domain bridge + old SubjectDomain id + Period leftovers
            legacy = session.run(
                """
                OPTIONAL MATCH (d:Domain {domain_id: $pack_id})
                DETACH DELETE d
                WITH 1 AS _
                OPTIONAL MATCH (sd_old:SubjectDomain {domain_id: $legacy_id})
                DETACH DELETE sd_old
                WITH 1 AS _
                OPTIONAL MATCH ()-[r:OCCURS_DURING]->(p:Period {qid: $qid})
                DELETE r
                WITH p
                OPTIONAL MATCH (p:Period {qid: $qid})
                WHERE p IS NOT NULL
                DETACH DELETE p
                RETURN 1 AS ok
                """,
                pack_id=DOMAIN_ID,
                legacy_id=LEGACY_SUBJECT_ID,
                qid=SEED_QID,
            ).single()
            print(f"Legacy Domain/Period cleanup: ok={legacy['ok']}")

            session.run(
                """
                MATCH (slot:SFASlot)
                WHERE slot.domain_id = $pack_id
                  AND NOT ( (:SubjectDomain {domain_id: $pack_id})-[:CONTAINS]->(slot) )
                DETACH DELETE slot
                """,
                pack_id=DOMAIN_ID,
            )

            session.run(
                """
                MERGE (n:SYS_NodeType {name: 'SFASlot'})
                SET n.domain = 'schema',
                    n.description = 'Inert facet agent slot under a SubjectDomain pack',
                    n.system = true,
                    n.ship_set = 'chrystal_2_domain_landing'
                WITH n
                OPTIONAL MATCH (sr:SYS_SchemaRegistry {system: true})
                FOREACH (_ IN CASE WHEN sr IS NULL THEN [] ELSE [1] END |
                  MERGE (sr)-[:HAS_NODE_TYPE]->(n)
                )
                """
            )

            session.run(
                """
                MERGE (sd:SubjectDomain {domain_id: $domain_id})
                SET sd.seed_qid = $seed_qid,
                    sd.label = $label,
                    sd.description = $description,
                    sd.kind = 'historical_pack',
                    sd.start_year = $start_year,
                    sd.end_year = $end_year,
                    sd.status = 'inert_shell',
                    sd.instance = 'chrystal_2',
                    sd.reference_json = $reference_json,
                    sd.statement_count = $statement_count,
                    sd.property_count = $property_count,
                    sd.wd_instance_of = $p31,
                    sd.seed_source = 'wikidata_pack_library'
                REMOVE sd.temporal_scope,
                      sd.schema_proposal_json,
                      sd.wd_capital_label,
                      sd.wd_part_of_label,
                      sd.wd_replaces_label,
                      sd.wd_lcsh_id
                WITH sd
                OPTIONAL MATCH (ys:Year {year: $start_year})
                FOREACH (_ IN CASE WHEN ys IS NULL THEN [] ELSE [1] END |
                  MERGE (sd)-[:STARTS_IN_YEAR]->(ys)
                )
                WITH sd
                OPTIONAL MATCH (ye:Year {year: $end_year})
                FOREACH (_ IN CASE WHEN ye IS NULL THEN [] ELSE [1] END |
                  MERGE (sd)-[:ENDS_IN_YEAR]->(ye)
                )
                """,
                domain_id=DOMAIN_ID,
                seed_qid=SEED_QID,
                label=seed_info.get("label") or "Roman Republic",
                description=seed_info.get("description"),
                start_year=start_year,
                end_year=end_year,
                reference_json=rel_path,
                statement_count=seed_info.get("statement_count"),
                property_count=seed_info.get("property_count"),
                p31=p31,
            )
            print(f"SubjectDomain {DOMAIN_ID}: {start_year}…{end_year}")
            print(f"reference_json: {rel_path}")

            for facet_key in FACET_KEYS:
                slot_id = f"sfa_{DOMAIN_ID}_{facet_key.lower()}"
                session.run(
                    """
                    MATCH (sd:SubjectDomain {domain_id: $domain_id})
                    MATCH (f:Facet {key: $facet_key})
                    MERGE (slot:SFASlot {slot_id: $slot_id})
                    SET slot.domain_id = $domain_id,
                        slot.facet_key = $facet_key,
                        slot.label = $label,
                        slot.status = 'inert',
                        slot.agent_type = 'SFA',
                        slot.instance = 'chrystal_2'
                    MERGE (sd)-[:CONTAINS]->(slot)
                    MERGE (slot)-[:HAS_FACET]->(f)
                    """,
                    domain_id=DOMAIN_ID,
                    facet_key=facet_key,
                    slot_id=slot_id,
                    label=f"SFA {facet_key} ({DOMAIN_ID})",
                )
            n_slots = session.run(
                """
                MATCH (:SubjectDomain {domain_id: $domain_id})-[:CONTAINS]->(s:SFASlot)
                RETURN count(s) AS c
                """,
                domain_id=DOMAIN_ID,
            ).single()["c"]
            print(f"SFASlot inert: {n_slots}")

            missing_facets = session.run(
                """
                UNWIND $keys AS k
                OPTIONAL MATCH (f:Facet {key: k})
                WITH k WHERE f IS NULL
                RETURN collect(k) AS missing
                """,
                keys=FACET_KEYS,
            ).single()["missing"]
            if missing_facets:
                print(f"WARNING: missing Facet nodes: {missing_facets}")
                return 2

            year_links = session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                OPTIONAL MATCH (sd)-[:STARTS_IN_YEAR]->(ys:Year)
                OPTIONAL MATCH (sd)-[:ENDS_IN_YEAR]->(ye:Year)
                RETURN sd.start_year AS start_prop, sd.end_year AS end_prop,
                       ys.year AS start_y, ye.year AS end_y
                """,
                domain_id=DOMAIN_ID,
            ).single()
            print(
                f"Year links: props={year_links['start_prop']}…{year_links['end_prop']} "
                f"edges={year_links['start_y']}…{year_links['end_y']}"
            )

            leftover_domain = session.run(
                "MATCH (d:Domain) RETURN count(d) AS c"
            ).single()["c"]
            print(f":Domain nodes remaining: {leftover_domain}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
