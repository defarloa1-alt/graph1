#!/usr/bin/env python3
"""
Build Wikidata-backed geographic backbone for period cohorts.

Goals:
1. Normalize fuzzy/raw place labels to canonical Wikidata place labels.
2. Build place hierarchy using Wikidata P131 (LOCATED_IN).
3. Link Period -> Place using canonical LOCATED_IN edges from extracted CSV mappings.

Inputs:
- Temporal/wikidata_period_geo_edges_all_geo_2026-02-18.csv
- Temporal/wikidata_period_geo_coordinates_all_geo_2026-02-18.csv (optional, period signals)

Usage:
    python scripts/backbone/geographic/build_wikidata_period_geo_backbone.py --dry-run
    python scripts/backbone/geographic/build_wikidata_period_geo_backbone.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from neo4j import GraphDatabase


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


LANG_PREF = ["en", "sv", "de", "fr", "es", "it", "ru", "ja", "zh", "ar", "la", "mul"]
WIKIDATA_API = "https://www.wikidata.org/w/api.php"


@dataclass
class PlaceInfo:
    qid: str
    label: str = ""
    aliases: List[str] = field(default_factory=list)
    parent_qids: List[str] = field(default_factory=list)  # P131
    country_qids: List[str] = field(default_factory=list)  # P17
    lat: Optional[float] = None
    long: Optional[float] = None
    depth: int = 0
    source: str = "wikidata"


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().split())


def parse_qid(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    if value.startswith("Q") and value[1:].isdigit():
        return value
    return None


def chunked(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def best_label(labels_obj: Dict[str, Dict[str, str]]) -> str:
    for lang in LANG_PREF:
        if lang in labels_obj:
            return labels_obj[lang].get("value", "")
    if labels_obj:
        return next(iter(labels_obj.values())).get("value", "")
    return ""


def fetch_entities(qids: List[str]) -> Dict[str, dict]:
    if not qids:
        return {}
    out: Dict[str, dict] = {}
    for batch in chunked(qids, 40):
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
            headers={"User-Agent": "Chrystallum-Graph1/1.0"},
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        out.update(payload.get("entities", {}))
    return out


def statement_qid(stmt: dict) -> Optional[str]:
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


def statement_coordinate(stmt: dict) -> tuple[Optional[float], Optional[float]]:
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


def build_place_infos(seed_qids: Set[str], max_parent_depth: int = 2) -> Dict[str, PlaceInfo]:
    place_infos: Dict[str, PlaceInfo] = {}
    frontier: Set[str] = {q for q in seed_qids if parse_qid(q)}
    seen_depth: Dict[str, int] = {q: 0 for q in frontier}

    while frontier:
        qids = sorted(frontier)
        frontier = set()
        entities = fetch_entities(qids)

        for qid in qids:
            entity = entities.get(qid, {})
            claims = entity.get("claims", {})
            labels = entity.get("labels", {})
            aliases_obj = entity.get("aliases", {})

            info = place_infos.get(qid, PlaceInfo(qid=qid, depth=seen_depth.get(qid, 0)))
            info.label = best_label(labels) or info.label or qid

            aliases: List[str] = []
            for lang in LANG_PREF:
                for a in aliases_obj.get(lang, []):
                    text = normalize_text(a.get("value"))
                    if text and text not in aliases:
                        aliases.append(text)
            info.aliases = aliases

            parent_qids: List[str] = []
            for stmt in claims.get("P131", []):
                parent = statement_qid(stmt)
                if parent and parent not in parent_qids:
                    parent_qids.append(parent)
            info.parent_qids = parent_qids

            country_qids: List[str] = []
            for stmt in claims.get("P17", []):
                cqid = statement_qid(stmt)
                if cqid and cqid not in country_qids:
                    country_qids.append(cqid)
            info.country_qids = country_qids

            lat = None
            lon = None
            for stmt in claims.get("P625", []):
                lat, lon = statement_coordinate(stmt)
                if lat is not None and lon is not None:
                    break
            info.lat = lat
            info.long = lon

            place_infos[qid] = info

            depth = seen_depth.get(qid, 0)
            if depth < max_parent_depth:
                for parent in parent_qids:
                    if parent not in seen_depth:
                        seen_depth[parent] = depth + 1
                        frontier.add(parent)

    return place_infos


def load_geo_edges(edges_csv: Path) -> List[Dict[str, str]]:
    with open(edges_csv, "r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out: List[Dict[str, str]] = []
    for row in rows:
        subject_qid = parse_qid(row.get("subject_qid"))
        object_qid = parse_qid(row.get("object_qid"))
        if not subject_qid or not object_qid:
            continue
        out.append(
            {
                "subject_qid": subject_qid,
                "subject_label": normalize_text(row.get("subject_label")),
                "periodo_id": normalize_text(row.get("periodo_id")),
                "wikidata_pid": normalize_text(row.get("wikidata_pid")),
                "wikidata_pid_label": normalize_text(row.get("wikidata_pid_label")),
                "object_qid": object_qid,
                "object_label_raw": normalize_text(row.get("object_label")),
                "mapping_note": normalize_text(row.get("mapping_note")) or "geo_authority_signal",
            }
        )
    return out


def parse_year_from_wikidata_time(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text[0] == "+":
        text = text[1:]
    if "T" in text:
        text = text.split("T", 1)[0]
    if "-" in text:
        year_part = text.split("-", 1)[0]
    else:
        year_part = text
    if not year_part:
        return None
    sign = -1 if year_part.startswith("-") else 1
    year_digits = year_part[1:] if year_part.startswith("-") else year_part
    if not year_digits.isdigit():
        return None
    return sign * int(year_digits)


def load_period_bounds(project_root: Path) -> Dict[str, Dict[str, Optional[int]]]:
    bounds: Dict[str, Dict[str, Optional[int]]] = {}
    candidate_files = [
        project_root / "Temporal" / "wikidata_periodo_start_end_unique_items_2026-02-18.csv",
        project_root / "Temporal" / "wikidata_periodo_end_before_minus2000_2026-02-18.csv",
    ]
    for fp in candidate_files:
        if not fp.exists():
            continue
        with open(fp, "r", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                qid = parse_qid(row.get("qid"))
                if not qid:
                    continue
                start_raw = row.get("start_sample") or row.get("start")
                end_raw = row.get("end_sample") or row.get("end")
                start_year = parse_year_from_wikidata_time(start_raw)
                end_year = parse_year_from_wikidata_time(end_raw)
                if qid not in bounds:
                    bounds[qid] = {"start_year": start_year, "end_year": end_year}
    return bounds


def write_normalization_report(
    out_csv: Path,
    place_infos: Dict[str, PlaceInfo],
    geo_edges: List[Dict[str, str]],
) -> None:
    raw_label_by_qid: Dict[str, Set[str]] = {}
    for edge in geo_edges:
        raw = edge.get("object_label_raw")
        if not raw:
            continue
        raw_label_by_qid.setdefault(edge["object_qid"], set()).add(raw)

    rows: List[Dict[str, str]] = []
    for qid, info in sorted(place_infos.items()):
        rows.append(
            {
                "place_qid": qid,
                "canonical_label": info.label,
                "raw_labels_seen": " | ".join(sorted(raw_label_by_qid.get(qid, set()))),
                "aliases": " | ".join(info.aliases[:20]),
                "parent_qids": " | ".join(info.parent_qids),
                "country_qids": " | ".join(info.country_qids),
                "lat": "" if info.lat is None else str(info.lat),
                "long": "" if info.long is None else str(info.long),
                "depth": str(info.depth),
            }
        )

    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "place_qid",
                "canonical_label",
                "raw_labels_seen",
                "aliases",
                "parent_qids",
                "country_qids",
                "lat",
                "long",
                "depth",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def import_to_neo4j(
    uri: str,
    user: str,
    password: str,
    place_infos: Dict[str, PlaceInfo],
    geo_edges: List[Dict[str, str]],
    period_bounds: Dict[str, Dict[str, Optional[int]]],
) -> None:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            place_rows = []
            for qid, info in place_infos.items():
                place_rows.append(
                    {
                        "qid": qid,
                        "label": info.label or qid,
                        "entity_id": f"plc_wd_{qid.lower()}",
                        "id_hash": stable_hash(f"wikidata:{qid}"),
                        "aliases": info.aliases[:50],
                        "parent_qids": info.parent_qids,
                        "country_qids": info.country_qids,
                        "lat": info.lat,
                        "long": info.long,
                        "depth": info.depth,
                    }
                )

            session.run(
                """
                UNWIND $rows AS row
                MERGE (pl:Place {qid: row.qid})
                ON CREATE SET pl.created = datetime()
                SET
                    pl.label = coalesce(row.label, pl.label, row.qid),
                    pl.entity_id = coalesce(pl.entity_id, row.entity_id),
                    pl.id_hash = coalesce(pl.id_hash, row.id_hash),
                    pl.entity_type = 'place',
                    pl.authority = 'Wikidata',
                    pl.node_type = 'wikidata_place_backbone',
                    pl.wikidata_qid = row.qid,
                    pl.uri = 'https://www.wikidata.org/wiki/' + row.qid,
                    pl.aliases = row.aliases,
                    pl.parent_qids = row.parent_qids,
                    pl.country_qids = row.country_qids,
                    pl.depth = row.depth,
                    pl.lat = coalesce(row.lat, pl.lat),
                    pl.long = coalesce(row.long, pl.long),
                    pl.updated = datetime()
                """,
                rows=place_rows,
            )

            session.run(
                """
                UNWIND $rows AS row
                MATCH (child:Place {qid: row.qid})
                UNWIND coalesce(row.parent_qids, []) AS parent_qid
                MATCH (parent:Place {qid: parent_qid})
                MERGE (child)-[r:LOCATED_IN]->(parent)
                SET
                    r.source = 'wikidata',
                    r.wikidata_pid = 'P131',
                    r.mapping_note = 'admin_containment',
                    r.updated = datetime()
                """,
                rows=place_rows,
            )

            period_link_rows = []
            for edge in geo_edges:
                periodo_ark = (
                    f"http://n2t.net/ark:/99152/{edge['periodo_id']}"
                    if edge.get("periodo_id")
                    else ""
                )
                b = period_bounds.get(edge["subject_qid"], {})
                period_link_rows.append(
                    {
                        "subject_qid": edge["subject_qid"],
                        "subject_label": edge["subject_label"],
                        "periodo_id": edge["periodo_id"],
                        "periodo_ark": periodo_ark,
                        "start_year": b.get("start_year"),
                        "end_year": b.get("end_year"),
                        "object_qid": edge["object_qid"],
                        "wikidata_pid": edge["wikidata_pid"],
                        "mapping_note": edge["mapping_note"],
                        "source_id": (
                            f"wikidata:{edge['subject_qid']}:{edge['wikidata_pid']}:{edge['object_qid']}"
                        ),
                    }
                )

            session.run(
                """
                UNWIND $rows AS row
                MATCH (pl:Place {qid: row.object_qid})
                CALL (row) {
                    MATCH (p:Period)
                    WHERE (row.subject_qid IS NOT NULL AND p.qid = row.subject_qid)
                       OR (row.periodo_id IS NOT NULL AND p.periodo_id = row.periodo_id)
                       OR (row.periodo_ark IS NOT NULL AND p.periodo_ark = row.periodo_ark)
                    RETURN p
                    UNION
                    MATCH (p:Period)
                    WHERE row.subject_label IS NOT NULL
                      AND p.label = row.subject_label
                      AND row.start_year IS NOT NULL
                      AND row.end_year IS NOT NULL
                      AND p.begin_year = row.start_year
                      AND p.end_year = row.end_year
                    RETURN p
                }
                WITH row, pl, collect(DISTINCT p) AS ps
                WHERE size(ps) = 1
                WITH row, pl, ps[0] AS p
                MERGE (p)-[r:LOCATED_IN {source_id: row.source_id}]->(pl)
                SET
                    r.source = 'wikidata',
                    r.wikidata_pid = row.wikidata_pid,
                    r.mapping_note = row.mapping_note,
                    r.updated = datetime()
                """,
                rows=period_link_rows,
            )

            stats = session.run(
                """
                RETURN
                    count { MATCH (:Place {node_type:'wikidata_place_backbone'}) } AS wd_places,
                    count { MATCH (:Place {node_type:'wikidata_place_backbone'})-[:LOCATED_IN]->(:Place) } AS place_hierarchy_edges,
                    count { MATCH (:Period)-[:LOCATED_IN {source:'wikidata'}]->(:Place) } AS period_place_wd_edges
                """
            ).single()

            print("Neo4j import stats:")
            print(f"  Wikidata backbone places: {stats['wd_places']}")
            print(f"  Place hierarchy LOCATED_IN edges: {stats['place_hierarchy_edges']}")
            print(f"  Period->Place LOCATED_IN (wikidata source): {stats['period_place_wd_edges']}")
    finally:
        driver.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize and import Wikidata place backbone for period geo mapping.")
    parser.add_argument("--uri", default="bolt://127.0.0.1:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="Chrystallum", help="Neo4j password")
    parser.add_argument(
        "--edges-csv",
        default="Temporal/wikidata_period_geo_edges_all_geo_2026-02-18.csv",
        help="Period->place wikidata edge mapping CSV",
    )
    parser.add_argument(
        "--max-parent-depth",
        type=int,
        default=2,
        help="How many P131 parent levels to pull from Wikidata",
    )
    parser.add_argument("--dry-run", action="store_true", help="Build artifacts only, no Neo4j writes")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    edges_csv = (project_root / args.edges_csv).resolve()
    if not edges_csv.exists():
        print(f"ERROR: edges CSV not found: {edges_csv}")
        return 1

    geo_edges = load_geo_edges(edges_csv)
    period_bounds = load_period_bounds(project_root)
    if not geo_edges:
        print("No valid geo edges found.")
        return 1

    seed_qids = {e["object_qid"] for e in geo_edges}
    place_infos = build_place_infos(seed_qids, max_parent_depth=args.max_parent_depth)

    norm_report = project_root / "Temporal" / "wikidata_period_geo_place_normalization_report_2026-02-18.csv"
    write_normalization_report(norm_report, place_infos, geo_edges)

    print("Normalization summary:")
    print(f"  Input edge rows: {len(geo_edges)}")
    print(f"  Period bounds loaded: {len(period_bounds)}")
    print(f"  Seed place QIDs: {len(seed_qids)}")
    print(f"  Place nodes after hierarchy expansion: {len(place_infos)}")
    print(f"  Normalization report: {norm_report}")

    if args.dry_run:
        print("Dry run complete. No Neo4j writes executed.")
        return 0

    import_to_neo4j(
        uri=args.uri,
        user=args.user,
        password=args.password,
        place_infos=place_infos,
        geo_edges=geo_edges,
        period_bounds=period_bounds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
