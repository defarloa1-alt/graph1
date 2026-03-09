#!/usr/bin/env python3
"""
Enrich Place nodes with Wikidata geographic data: P625 (coords), P3896 (geoshape),
P131 (admin parent), P17 (country), and labels.

Fetches from Wikidata API for all Place nodes that have a qid. Fills gaps:
- lat/long when missing (from P625)
- geoshape_commons when P3896 present (Commons Data path for polygon)
- label when bad (label = qid)
- LOCATED_IN edges from P131 (creates parent Place nodes if needed)
- country_qid from P17

Run after: import_pleiades_to_neo4j.py, enrich_places_from_crosswalk.py

Usage:
  python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py --dry-run
  python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py
  python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py --limit 500
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
LANG_PREF = ["en", "sv", "de", "fr", "es", "it", "ru", "ja", "zh", "ar", "la", "mul"]


def _best_label(labels_obj: dict) -> str:
    for lang in LANG_PREF:
        if lang in labels_obj:
            return labels_obj[lang].get("value", "")
    if labels_obj:
        return next(iter(labels_obj.values())).get("value", "")
    return ""


def _statement_qid(stmt: dict) -> Optional[str]:
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return None
    if mainsnak.get("datatype") != "wikibase-item":
        return None
    value = mainsnak.get("datavalue", {}).get("value", {})
    qid = value.get("id")
    if qid:
        return qid
    numeric_id = value.get("numeric-id")
    if numeric_id is None:
        return None
    return f"Q{numeric_id}"


def _statement_coordinate(stmt: dict) -> Tuple[Optional[float], Optional[float]]:
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return (None, None)
    if mainsnak.get("datatype") != "globecoordinate":
        return (None, None)
    value = mainsnak.get("datavalue", {}).get("value", {})
    lat = value.get("latitude")
    lon = value.get("longitude")
    if lat is None or lon is None:
        return (None, None)
    return (float(lat), float(lon))


def _parse_wikidata_year(value: Any) -> Optional[int]:
    """Extract year from Wikidata time value (e.g. +0200-01-01T00:00:00Z or -0100-00-00T00:00:00Z)."""
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("time", value.get("value", ""))
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("+"):
        text = text[1:]
    if "T" in text:
        text = text.split("T", 1)[0]
    parts = text.split("-")
    if not parts:
        return None
    year_part = parts[0].lstrip("+")
    sign = -1 if year_part.startswith("-") else 1
    digits = year_part[1:] if year_part.startswith("-") else year_part
    if not digits.isdigit():
        return None
    return sign * int(digits)


def _get_qualifier_years(stmt: dict) -> tuple[Optional[int], Optional[int]]:
    """Extract start_year, end_year from P580/P582 qualifiers. P585 yields point-in-time for both."""
    quals = stmt.get("qualifiers", {}) or {}
    start_year = None
    end_year = None
    for q in quals.get("P580", []):
        dv = q.get("datavalue", {})
        val = dv.get("value", {}) if isinstance(dv.get("value"), dict) else dv.get("value")
        if isinstance(val, dict):
            val = val.get("time")
        start_year = _parse_wikidata_year(val)
        if start_year is not None:
            break
    for q in quals.get("P582", []):
        dv = q.get("datavalue", {})
        val = dv.get("value", {}) if isinstance(dv.get("value"), dict) else dv.get("value")
        if isinstance(val, dict):
            val = val.get("time")
        end_year = _parse_wikidata_year(val)
        if end_year is not None:
            break
    if start_year is None and end_year is None:
        for q in quals.get("P585", []):
            dv = q.get("datavalue", {})
            val = dv.get("value", {}) if isinstance(dv.get("value"), dict) else dv.get("value")
            if isinstance(val, dict):
                val = val.get("time")
            y = _parse_wikidata_year(val)
            if y is not None:
                start_year = end_year = y
                break
    return (start_year, end_year)


def _statement_geoshape(stmt: dict) -> Optional[str]:
    """Extract Commons Data path from P3896 (geoshape) statement.
    Value may be string 'Data:...map' or nested in datavalue.value."""
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return None
    dv = mainsnak.get("datavalue", {})
    if not dv:
        return None
    val = dv.get("value")
    if isinstance(val, str) and "Data:" in val and ".map" in val:
        return val if val.startswith("Data:") else f"Data:{val}"
    if isinstance(val, dict):
        s = val.get("value") or val.get("id") or val.get("content")
        if isinstance(s, str) and "Data:" in s:
            return s if s.endswith(".map") else f"{s}.map"
    return None


def _chunked(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def fetch_entities(
    qids: List[str],
    *,
    timeout: int = 180,
    pause: float = 0.5,
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for batch in _chunked(qids, 40):
        params = urllib.parse.urlencode(
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "format": "json",
                "props": "labels|aliases|claims",
                "languages": "|".join(LANG_PREF),
            }
        )
        req = urllib.request.Request(
            f"{WIKIDATA_API}?{params}",
            headers={"User-Agent": "Chrystallum-Graph1/1.0 (enrich-places-wikidata-geo)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        out.update(payload.get("entities", {}))
        time.sleep(pause)
    return out


def extract_geo_data(entity: dict) -> dict:
    """Extract P625, P3896 (with P580/P582/P585 qualifiers), P131, P17, label from Wikidata entity."""
    claims = entity.get("claims", {})
    labels = entity.get("labels", {})

    lat, lon = None, None
    coord_start_year, coord_end_year = None, None
    for stmt in claims.get("P625", []):
        lat, lon = _statement_coordinate(stmt)
        if lat is not None and lon is not None:
            cs, ce = _get_qualifier_years(stmt)
            if cs is not None or ce is not None:
                coord_start_year, coord_end_year = cs, ce
            break

    geoshape = None
    geoshape_start_year, geoshape_end_year = None, None
    for stmt in claims.get("P3896", []):
        gs = _statement_geoshape(stmt)
        if gs:
            geoshape = gs
            gs_start, gs_end = _get_qualifier_years(stmt)
            if gs_start is not None or gs_end is not None:
                geoshape_start_year, geoshape_end_year = gs_start, gs_end
            break

    parent_qids: List[str] = []
    for stmt in claims.get("P131", []):
        p = _statement_qid(stmt)
        if p and p not in parent_qids:
            parent_qids.append(p)

    country_qids: List[str] = []
    for stmt in claims.get("P17", []):
        c = _statement_qid(stmt)
        if c and c not in country_qids:
            country_qids.append(c)

    label = _best_label(labels)

    return {
        "lat": lat,
        "long": lon,
        "coord_start_year": coord_start_year,
        "coord_end_year": coord_end_year,
        "geoshape_commons": geoshape,
        "geoshape_start_year": geoshape_start_year,
        "geoshape_end_year": geoshape_end_year,
        "parent_qids": parent_qids,
        "country_qid": country_qids[0] if country_qids else None,
        "label": label,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich Place nodes with Wikidata geo data (P625, P3896, P131, P17)"
    )
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true", help="Report only, no writes")
    parser.add_argument("--limit", type=int, default=None, help="Limit places to process (for testing)")
    args = parser.parse_args()

    if not args.password:
        print("NEO4J_PASSWORD required (set in .env or --password)", file=sys.stderr)
        return 1

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Place)
            WHERE p.qid IS NOT NULL
            RETURN p.qid AS qid, p.pleiades_id AS pleiades_id, p.lat AS lat, p.long AS long,
                   p.label AS label, elementId(p) AS element_id
            """
        )
        rows = list(result)
        if args.limit:
            rows = rows[: args.limit]

    qids = list({r["qid"] for r in rows})
    print(f"Found {len(rows)} Place nodes with qid ({len(qids)} distinct QIDs)", flush=True)

    if not qids:
        print("Nothing to do.")
        driver.close()
        return 0

    print("Fetching from Wikidata API...", flush=True)
    entities = fetch_entities(qids)

    # Build qid -> row mapping (prefer pleiades_id for multiple Place nodes with same qid)
    qid_to_row: Dict[str, dict] = {}
    for r in rows:
        qid = r["qid"]
        if qid not in qid_to_row or r.get("pleiades_id"):
            qid_to_row[qid] = r

    # Extract geo data per entity
    updates: List[dict] = []
    link_rows: List[dict] = []
    parent_qids: Set[str] = set()

    for qid, entity in entities.items():
        if entity.get("missing") == "":
            continue
        row = qid_to_row.get(qid)
        if not row:
            continue

        data = extract_geo_data(entity)
        pleiades_id = row.get("pleiades_id")
        has_coords = row.get("lat") is not None and row.get("long") is not None
        bad_label = row.get("label") == qid

        update = {
            "qid": qid,
            "pleiades_id": pleiades_id,
            "lat": data["lat"] if not has_coords and data["lat"] else None,
            "long": data["long"] if not has_coords and data["long"] else None,
            "coord_start_year": data["coord_start_year"],
            "coord_end_year": data["coord_end_year"],
            "geoshape_commons": data["geoshape_commons"],
            "geoshape_start_year": data["geoshape_start_year"],
            "geoshape_end_year": data["geoshape_end_year"],
            "country_qid": data["country_qid"],
            "label": data["label"] if bad_label and data["label"] else None,
            "coord_source": "Wikidata" if not has_coords and data["lat"] else None,
        }
        if any(v is not None for k, v in update.items() if k not in ("qid", "pleiades_id")):
            updates.append(update)

        for parent_qid in data["parent_qids"]:
            parent_qids.add(parent_qid)
            link_rows.append({"child_qid": qid, "parent_qid": parent_qid})

    # Dedupe link rows
    seen_links: Set[Tuple[str, str]] = set()
    link_rows = [
        r for r in link_rows
        if (r["child_qid"], r["parent_qid"]) not in seen_links
        and not seen_links.add((r["child_qid"], r["parent_qid"]))
    ]

    # Fetch parent entities for labels
    missing_parents = [q for q in parent_qids if q not in entities]
    if missing_parents:
        print(f"Fetching {len(missing_parents)} parent entities...", flush=True)
        parent_entities = fetch_entities(missing_parents)
        entities.update(parent_entities)

    parent_place_rows = []
    for qid in parent_qids:
        entity = entities.get(qid, {})
        label = _best_label(entity.get("labels", {})) if entity else qid
        parent_place_rows.append({"qid": qid, "label": label or qid})

    # Stats
    n_coords = sum(1 for u in updates if u.get("lat") is not None)
    n_geoshape = sum(1 for u in updates if u.get("geoshape_commons"))
    n_geoshape_temporal = sum(1 for u in updates if u.get("geoshape_start_year") is not None or u.get("geoshape_end_year") is not None)
    n_coord_temporal = sum(1 for u in updates if u.get("coord_start_year") is not None or u.get("coord_end_year") is not None)
    n_labels = sum(1 for u in updates if u.get("label"))
    n_country = sum(1 for u in updates if u.get("country_qid"))

    print(f"  Coords to add (lat/long missing): {n_coords}")
    print(f"  Geoshapes (P3896): {n_geoshape} ({n_geoshape_temporal} with P580/P582/P585)")
    print(f"  Coord temporal (P625 qualifiers): {n_coord_temporal}")
    print(f"  Labels to fix: {n_labels}")
    print(f"  Country QIDs: {n_country}")
    print(f"  Parent Place nodes: {len(parent_place_rows)}")
    print(f"  LOCATED_IN edges: {len(link_rows)}")

    if args.dry_run:
        if updates:
            for u in updates[:5]:
                temporal = ""
                if u.get("geoshape_start_year") is not None or u.get("geoshape_end_year") is not None:
                    temporal = f" geoshape[{u.get('geoshape_start_year')}-{u.get('geoshape_end_year')}]"
                elif u.get("coord_start_year") is not None or u.get("coord_end_year") is not None:
                    temporal = f" coord[{u.get('coord_start_year')}-{u.get('coord_end_year')}]"
                print(f"    Sample: qid={u['qid']} lat={u.get('lat')} geoshape={u.get('geoshape_commons')}{temporal}")
        driver.close()
        return 0

    with driver.session() as session:
        # Update Place nodes
        if updates:
            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Place {qid: row.qid})
                SET
                    p.lat = coalesce(p.lat, row.lat),
                    p.long = coalesce(p.long, row.long),
                    p.geoshape_commons = coalesce(row.geoshape_commons, p.geoshape_commons),
                    p.geoshape_start_year = coalesce(row.geoshape_start_year, p.geoshape_start_year),
                    p.geoshape_end_year = coalesce(row.geoshape_end_year, p.geoshape_end_year),
                    p.coord_start_year = coalesce(row.coord_start_year, p.coord_start_year),
                    p.coord_end_year = coalesce(row.coord_end_year, p.coord_end_year),
                    p.country_qid = coalesce(row.country_qid, p.country_qid),
                    p.label = CASE WHEN row.label IS NOT NULL THEN row.label ELSE p.label END,
                    p.label_clean = CASE WHEN row.label IS NOT NULL THEN row.label ELSE p.label_clean END,
                    p.coord_source = CASE WHEN row.coord_source IS NOT NULL THEN row.coord_source ELSE p.coord_source END
                """,
                rows=[{k: v for k, v in u.items() if v is not None} for u in updates],
            )
            print(f"Updated {len(updates)} Place nodes", flush=True)

        # Ensure parent Place nodes exist
        if parent_place_rows:
            session.run(
                """
                UNWIND $rows AS row
                MERGE (pl:Place {qid: row.qid})
                ON CREATE SET
                    pl.node_type = 'wikidata_place_backbone',
                    pl.authority = 'Wikidata',
                    pl.uri = 'https://www.wikidata.org/wiki/' + row.qid
                SET pl.label = coalesce(row.label, pl.label, row.qid)
                """,
                rows=parent_place_rows,
            )
            print(f"Ensured {len(parent_place_rows)} parent Place nodes", flush=True)

        # Create LOCATED_IN edges (child Place -> parent Place by qid)
        if link_rows:
            # Match child by qid; if pleiades_id present, prefer that Place
            session.run(
                """
                UNWIND $rows AS row
                MATCH (child:Place {qid: row.child_qid})
                MATCH (parent:Place {qid: row.parent_qid})
                WHERE child <> parent
                MERGE (child)-[r:LOCATED_IN]->(parent)
                SET
                    r.source = 'wikidata',
                    r.wikidata_pid = 'P131',
                    r.mapping_note = 'admin_containment'
                RETURN count(r) AS n
                """,
                rows=link_rows,
            )
            print(f"Created/updated LOCATED_IN edges", flush=True)

    driver.close()
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
