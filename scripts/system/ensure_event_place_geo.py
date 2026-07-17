#!/usr/bin/env python3
"""
Ensure an Event has a Place location with Wikidata geodata (P625).

For battle/events:
  1. Read Wikidata P276 (location) + P625 on the event and location places
  2. Enrich/create Place nodes with lat/long from P625
  3. MERGE Event -[:LOCATION_OF_EVENT]-> Place (registry P276)

Skips coarse locations (e.g. Roman Italy Q913582). Prefers settlement-level
places that themselves have P625.

Usage:
  python scripts/system/ensure_event_place_geo.py --event-qid Q179591 --dry-run
  python scripts/system/ensure_event_place_geo.py --event-qid Q179591
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase  # noqa: E402

from scripts.config_loader import (  # noqa: E402
    NEO4J_DATABASE,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)
from scripts.tools.entity_cipher import generate_entity_cipher  # noqa: E402

USER_AGENT = "ChrystallumGraph1/1.0 (ensure-event-place-geo)"

# Too coarse for battle-site LOCATION_OF_EVENT (prefer settlement QIDs).
COARSE_LOCATION_QIDS = frozenset(
    {
        "Q913582",  # Roman Italy
        "Q38",  # Italy (modern)
        "Q1747689",  # Roman Republic (polity, sometimes listed as P17)
    }
)


def _http_json(url: str, timeout: int = 45) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_entity(qid: str) -> dict[str, Any]:
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    data = _http_json(url)
    return data["entities"][qid]


def _label_en(entity: dict[str, Any]) -> str:
    labels = entity.get("labels") or {}
    if "en" in labels:
        return labels["en"].get("value") or qid_fallback(entity)
    if labels:
        return next(iter(labels.values())).get("value") or qid_fallback(entity)
    return qid_fallback(entity)


def qid_fallback(entity: dict[str, Any]) -> str:
    return entity.get("id") or ""


def _coord_p625(entity: dict[str, Any]) -> tuple[float, float] | None:
    for stmt in (entity.get("claims") or {}).get("P625", []):
        snak = stmt.get("mainsnak") or {}
        if snak.get("snaktype") != "value":
            continue
        val = (snak.get("datavalue") or {}).get("value") or {}
        lat, lon = val.get("latitude"), val.get("longitude")
        if lat is not None and lon is not None:
            return float(lat), float(lon)
    return None


def _p276_place_qids(entity: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for stmt in (entity.get("claims") or {}).get("P276", []):
        snak = stmt.get("mainsnak") or {}
        if snak.get("snaktype") != "value":
            continue
        val = (snak.get("datavalue") or {}).get("value") or {}
        qid = val.get("id")
        if qid and qid not in out:
            out.append(qid)
    return out


def choose_location_place(event_entity: dict[str, Any]) -> dict[str, Any] | None:
    """Pick best Place from P276: has P625, not coarse. Fallback: event P625 only."""
    candidates: list[dict[str, Any]] = []
    for pqid in _p276_place_qids(event_entity):
        if pqid in COARSE_LOCATION_QIDS:
            print(f"  skip coarse P276 location {pqid}")
            continue
        place_ent = fetch_entity(pqid)
        coords = _coord_p625(place_ent)
        if not coords:
            print(f"  skip P276 {pqid} ({_label_en(place_ent)}): no P625")
            continue
        candidates.append(
            {
                "qid": pqid,
                "label": _label_en(place_ent),
                "lat": coords[0],
                "long": coords[1],
                "source": "wikidata_p276_p625",
            }
        )
    if candidates:
        # Prefer first settlement-level with coords (WD order usually specific first).
        return candidates[0]

    event_coords = _coord_p625(event_entity)
    if event_coords:
        eqid = event_entity.get("id")
        print(
            f"  no usable P276 Place; will not invent Place from event P625 alone "
            f"({event_coords[0]}, {event_coords[1]}) — add a Place QID first"
        )
        return {
            "qid": None,
            "label": None,
            "lat": event_coords[0],
            "long": event_coords[1],
            "source": "wikidata_event_p625_only",
            "event_qid": eqid,
        }
    return None


def ensure_place(
    session,
    *,
    qid: str,
    label: str,
    lat: float,
    lon: float,
    dry_run: bool,
) -> str:
    place_id = f"plc_wd_{qid}"
    entity_cipher = generate_entity_cipher("PLACE", qid=qid, namespace="wd")
    if dry_run:
        print(f"  [dry-run] MERGE Place {qid} lat={lat} long={lon}")
        return place_id
    session.run(
        """
        MERGE (p:Place {qid: $qid})
        ON CREATE SET
            p.place_id = $place_id,
            p.entity_id = $place_id,
            p.entity_type = 'PLACE',
            p.entity_cipher = $entity_cipher,
            p.label = $label,
            p.authority = 'Wikidata'
        ON MATCH SET
            p.entity_cipher = coalesce(p.entity_cipher, $entity_cipher),
            p.label = coalesce(p.label, $label),
            p.place_id = coalesce(p.place_id, $place_id)
        SET p.lat = $lat,
            p.long = $lon,
            p.geo_source = 'wikidata_p625',
            p.geo_enriched_at = datetime()
        """,
        qid=qid,
        place_id=place_id,
        entity_cipher=entity_cipher,
        label=label,
        lat=lat,
        lon=lon,
    )
    print(f"  Place {qid} ({label}): lat={lat}, long={lon}")
    return place_id


def link_event_place(
    session,
    *,
    event_qid: str,
    place_qid: str,
    dry_run: bool,
) -> None:
    if dry_run:
        print(
            f"  [dry-run] MERGE (:Event {{qid:{event_qid}}})"
            f"-[:LOCATION_OF_EVENT]->(:Place {{qid:{place_qid}}})"
        )
        return
    result = session.run(
        """
        MATCH (e:Event {qid: $event_qid})
        MATCH (p:Place {qid: $place_qid})
        MERGE (e)-[r:LOCATION_OF_EVENT]->(p)
        ON CREATE SET
            r.source = 'wikidata_p276',
            r.pred_pid = 'P276',
            r.created_at = datetime(),
            r.geo_required = true
        ON MATCH SET
            r.source = coalesce(r.source, 'wikidata_p276'),
            r.pred_pid = coalesce(r.pred_pid, 'P276')
        RETURN e.label AS event_label, p.label AS place_label, p.lat AS lat, p.long AS long
        """,
        event_qid=event_qid,
        place_qid=place_qid,
    )
    row = result.single()
    if not row:
        raise RuntimeError(
            f"Could not link Event {event_qid} to Place {place_qid} — missing node?"
        )
    print(
        f"  LOCATION_OF_EVENT: {row['event_label']} -> {row['place_label']} "
        f"({row['lat']}, {row['long']})"
    )


def run(event_qid: str, *, dry_run: bool) -> int:
    print(f"Event {event_qid}: fetching Wikidata...")
    event_ent = fetch_entity(event_qid)
    print(f"  label: {_label_en(event_ent)}")
    chosen = choose_location_place(event_ent)
    if not chosen or not chosen.get("qid"):
        print("FAIL: no Place QID with P625 from P276 (geo gate cannot pass).")
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    database = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=database) as session:
            ev = session.run(
                "MATCH (e:Event {qid: $qid}) RETURN e.label AS label",
                qid=event_qid,
            ).single()
            if not ev:
                print(f"FAIL: Event {event_qid} not in graph.")
                return 1
            ensure_place(
                session,
                qid=chosen["qid"],
                label=chosen["label"],
                lat=chosen["lat"],
                lon=chosen["long"],
                dry_run=dry_run,
            )
            link_event_place(
                session,
                event_qid=event_qid,
                place_qid=chosen["qid"],
                dry_run=dry_run,
            )
            if not dry_run:
                check = session.run(
                    """
                    MATCH (e:Event {qid: $eqid})-[:LOCATION_OF_EVENT]->(p:Place)
                    WHERE p.lat IS NOT NULL AND p.long IS NOT NULL
                    RETURN p.qid AS qid, p.lat AS lat, p.long AS long
                    """,
                    eqid=event_qid,
                ).single()
                if not check:
                    print("FAIL: post-check — Event still has no geolocated Place.")
                    return 1
                print(
                    f"OK: {event_qid} @ Place {check['qid']} "
                    f"({check['lat']}, {check['long']})"
                )
    finally:
        driver.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Ensure Event has Place + Wikidata geodata")
    ap.add_argument("--event-qid", required=True, help="Event QID (e.g. Q179591)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run(args.event_qid.strip(), dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
