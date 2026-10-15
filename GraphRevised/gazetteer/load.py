"""Load the gazetteer (27-GAZETTEER.md): GeoNames' modern tree, all of Pleiades, the bridge
between them, and the Place entities' links to their Locations.

    python -m GraphRevised.gazetteer.load [--apply] [--batch 5000]

Dry run by default: reads the preserved dumps (cache/geonames, cache/pleiades), builds
every row, and reports what would be written, writing nothing. With --apply it creates
the Location schema and writes in batches, each its own transaction, through the named
operations; every write is a MERGE, so a rerun after a failure finishes the job. The
loader never creates an Entity. Rules (which features, the bridge distance) are data
in curation/gazetteer.json. Each run writes a report to runs/.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write

from .geonames import ModernTree, build_tree, cells_around, haversine_km, nearest_populated
from .pleiades import iter_places, name_lines

GRAPH_REVISED = Path(__file__).resolve().parents[1]
CACHE = GRAPH_REVISED / "cache"
RUNS = GRAPH_REVISED / "runs"


def geonames_id(identifier: str) -> str:
    return f"chr:location:geonames:{identifier}"


def pleiades_id(identifier: str) -> str:
    return f"chr:location:pleiades:{identifier}"


def dataset_label(directory: Path, name: str, title: str) -> str:
    """Which dump a row came from: its title, Last-Modified date, and hash prefix."""
    entry = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))["files"][name]
    return f"{title}, {entry['lastModified'][:10]}, sha256 {entry['sha256'][:12]}"


def build_rows(rules: dict[str, Any], places: list[dict[str, Any]], tree: ModernTree,
               datasets: dict[str, str]) -> dict[str, Any]:
    """Every row the load writes, and what it leaves out."""
    locations, parents, bridges, report = [], [], [], Counter()
    unbridged: list[dict[str, Any]] = []

    def geonames_row(f, kind):
        return {"id": geonames_id(f.id), "label": f.name, "system": "GeoNames", "identifier": f.id, "kind": kind,
                "lat": f.lat, "lon": f.lon, "population": f.population or None, "placeTypes": None,
                "names": None, "nameAttestations": None, "dataset": datasets["geonames"]}

    for unit_id, f in tree.units.items():
        locations.append(geonames_row(f, tree.kinds[unit_id]))
        if unit_id in tree.parents:
            parents.append({"child": geonames_id(unit_id), "parent": geonames_id(tree.parents[unit_id]),
                            "tree": "modern", "relation": "admin", "periods": None})
    # Features Pleiades names that are not units: loaded and placed in the modern tree
    for f in tree.referenced.values():
        if f.id in tree.units:
            continue
        locations.append(geonames_row(f, f.code))
        unit = tree.most_specific_unit(f)
        if unit:
            parents.append({"child": geonames_id(f.id), "parent": geonames_id(unit), "tree": "modern",
                            "relation": "admin", "periods": None})
        else:
            report["referencedWithoutUnit"] += 1

    known = {p["id"] for p in places}
    parent_types = set(rules["pleiades"]["parentRelations"])
    max_km = rules["bridge"]["maxKm"]
    for p in places:
        names, attested = name_lines(p["names"])
        locations.append({"id": pleiades_id(p["id"]), "label": p["title"], "system": "Pleiades", "identifier": p["id"],
                          "kind": p["placeTypes"][0] if p["placeTypes"] else "unclassified", "lat": p["lat"],
                          "lon": p["lon"], "population": None, "placeTypes": p["placeTypes"] or None,
                          "names": names or None, "nameAttestations": attested or None,
                          "dataset": datasets["pleiades"]})
        for c in p["connections"]:
            if c["type"] not in parent_types:
                continue
            if c["target"] not in known:
                report["ancientParentMissing"] += 1
                continue
            parents.append({"child": pleiades_id(p["id"]), "parent": pleiades_id(c["target"]), "tree": "ancient",
                            "relation": c["type"], "periods": c["periods"] or None})
        referenced = [tree.referenced[g] for g in p["geonames"] if g in tree.referenced]
        if referenced:
            for f in referenced:
                distance = (round(haversine_km(p["lat"], p["lon"], f.lat, f.lon), 1)
                            if p["lat"] is not None else None)
                bridges.append({"ancient": pleiades_id(p["id"]), "modern": geonames_id(f.id), "how": "pleiades reference",
                                "distanceKm": distance, "viaId": None, "viaLabel": None})
            report["bridgedByReference"] += 1
        elif p["lat"] is None:
            report["unlocated"] += 1
        else:
            found = nearest_populated(tree, p["lat"], p["lon"], max_km)
            unit = tree.most_specific_unit(found[0]) if found else None
            if found and unit:
                bridges.append({"ancient": pleiades_id(p["id"]), "modern": geonames_id(unit), "how": "nearest place",
                                "distanceKm": round(found[1], 1), "viaId": found[0].id, "viaLabel": found[0].name})
                report["bridgedByNearestPlace"] += 1
            else:
                report["notBridged"] += 1
                unbridged.append({"pleiades": p["id"], "title": p["title"], "lat": p["lat"], "lon": p["lon"],
                                  "reason": "no populated place within range" if not found else "place has no unit"})
    return {"locations": locations, "parents": parents, "bridges": bridges, "report": dict(report),
            "unbridged": unbridged}


PLACE_ENTITIES = """
MATCH (place:Entity {kind: "Place"}) WHERE place.status <> "deprecated"
OPTIONAL MATCH (place)-[link:HAS_AUTHORITY_RECORD]->(record:AuthorityRecord)
RETURN place.id AS id, place.label AS label,
       collect({system: record.system, identifier: record.identifier, role: link.role}) AS records
ORDER BY id
"""


def place_links(tx, places: list[dict[str, Any]], location_ids: set[str]) -> tuple[list[dict], list[dict]]:
    """Place Entities to Locations, by an identifier the Entity holds: its Pleiades or GeoNames
    record, or a Wikidata identity that Pleiades names. Identity stays the curator's: no
    match by name or coordinates is made here."""
    by_qid: dict[str, list[str]] = {}
    for p in places:
        for qid in p["wikidata"]:
            by_qid.setdefault(qid, []).append(p["id"])
    rows, unmatched = [], []
    for entity in tx.run(PLACE_ENTITIES).data():
        found = []
        for record in entity["records"]:
            system, identifier = record["system"], record["identifier"]
            if system == "Pleiades" and pleiades_id(identifier) in location_ids:
                found.append((pleiades_id(identifier), f"Pleiades {identifier} (crosswalk)"))
            elif system == "GeoNames" and geonames_id(identifier) in location_ids:
                found.append((geonames_id(identifier), f"GeoNames {identifier} (crosswalk)"))
            elif system == "Wikidata" and record["role"] == "entity_identity":
                for pid in by_qid.get(identifier, []):
                    found.append((pleiades_id(pid), f"Pleiades {pid} names Wikidata {identifier}"))
        for location, basis in dict(found).items():
            rows.append({"entity": entity["id"], "location": location, "status": "accepted", "basis": basis})
        if not found:
            unmatched.append({"entity": entity["id"], "label": entity["label"]})
    return rows, unmatched


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="write (otherwise a dry run)")
    parser.add_argument("--batch", type=int, default=5000)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # place names in every script

    rules = json.loads((GRAPH_REVISED / "curation" / "gazetteer.json").read_text(encoding="utf-8"))
    datasets = {
        "geonames": dataset_label(CACHE / "geonames", "allCountries.zip", rules["geonames"]["dataset"]),
        "pleiades": dataset_label(CACHE / "pleiades", "pleiades-places-latest.json.gz", rules["pleiades"]["dataset"]),
    }
    print("reading Pleiades ...")
    places = list(iter_places(CACHE / "pleiades" / "pleiades-places-latest.json.gz"))
    referenced = {g for p in places for g in p["geonames"]}
    needed = set()
    for p in places:
        if p["lat"] is not None and not p["geonames"]:
            needed |= cells_around(p["lat"], p["lon"], rules["bridge"]["maxKm"])
    print(f"{len(places)} places; {len(referenced)} GeoNames features named; {len(needed)} grid cells to search")
    print("reading GeoNames (one pass over allCountries) ...")
    tree = build_tree(CACHE / "geonames", rules, referenced, needed)
    rows = build_rows(rules, places, tree, datasets)

    operations = load_operations()
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            location_ids = {r["id"] for r in rows["locations"]}
            links, unmatched = session.execute_read(lambda tx: place_links(tx, places, location_ids))
            if args.apply:
                for statement in (GRAPH_REVISED / "gazetteer" / "schema.cypher").read_text(encoding="utf-8").split(";"):
                    body = "\n".join(l for l in statement.splitlines() if not l.strip().startswith("//")).strip()
                    if body:
                        session.run(body).consume()
                for name, key in (("upsert_locations", "locations"), ("link_location_parents", "parents"),
                                  ("link_modern_locations", "bridges")):
                    batch_rows = rows[key]
                    for start in range(0, len(batch_rows), args.batch):
                        chunk = batch_rows[start:start + args.batch]
                        session.execute_write(lambda tx: run_write(tx, operations, name, {"rows": chunk}))
                        print(f"{name}: {min(start + args.batch, len(batch_rows))}/{len(batch_rows)}", end="\r")
                    print()
                if links:
                    session.execute_write(lambda tx: run_write(tx, operations, "link_place_locations", {"rows": links}))
    finally:
        driver.close()

    kinds = Counter(r["kind"] for r in rows["locations"] if r["system"] == "GeoNames")
    summary = {
        "applied": args.apply, "datasets": datasets, "rules": rules["bridge"],
        "geonames": tree.report, "geonamesLocationsByKind": dict(kinds.most_common(12)),
        "locations": len(rows["locations"]),
        "withinLinks": dict(Counter(r["tree"] for r in rows["parents"])),
        "modernLocationLinks": dict(Counter(r["how"] for r in rows["bridges"])),
        "bridge": rows["report"],
        "placeEntityLinks": links, "placeEntitiesUnmatched": unmatched,
    }
    RUNS.mkdir(exist_ok=True)
    path = RUNS / f"gazetteer-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    path.write_bytes((json.dumps({**summary, "unbridged": rows["unbridged"]}, ensure_ascii=False, indent=1) + "\n")
                     .encode("utf-8"))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"report: {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
