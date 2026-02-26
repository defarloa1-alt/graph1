"""
prosopographic_crosswalk.py
---------------------------
Enriches Entity nodes (PERSON type) in Neo4j Aura with identifiers
from Trismegistos and LGPN by crosswalking from existing Wikidata QIDs.

Pipeline position: AFTER cluster_assignment, as an enrichment step.

Strategy:
  1. Find Entity nodes with primary_facet = BIOGRAPHIC
  2. For each entity with Wikidata QID: query P1696 (TM), P1838 (LGPN)
  3. Store crosswalk IDs as properties on Entity node

Usage:
    python scripts/integration/prosopographic_crosswalk.py \\
        --input output/cluster_assignment/member_of_edges.json \\
        --output-dir output/crosswalk --cypher

Dependencies:
    pip install requests neo4j
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional

import requests

WIKIDATA_CROSSWALK_PROPS = {
    "P1696": "trismegistos_person_id",
    "P1838": "lgpn_id",
    "P1605": "viaf_id",
}
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
TM_PERSON_API = "https://www.trismegistos.org/dataservices/per/index.php"
_wikidata_cache: dict = {}
_tm_cache: dict = {}


@dataclass
class CrosswalkResult:
    entity_qid: str
    entity_label: str
    trismegistos_id: Optional[str] = None
    trismegistos_name: Optional[str] = None
    trismegistos_dates: Optional[str] = None
    trismegistos_place: Optional[str] = None
    lgpn_id: Optional[str] = None
    viaf_id: Optional[str] = None
    crosswalk_sources: list = field(default_factory=list)
    enriched: bool = False


def fetch_wikidata_crosswalk(qid: str) -> dict:
    if qid in _wikidata_cache:
        return _wikidata_cache[qid]
    try:
        resp = requests.get(WIKIDATA_API, params={
            "action": "wbgetentities", "ids": qid,
            "props": "claims|labels", "languages": "en", "format": "json",
        }, timeout=15)
        resp.raise_for_status()
        entity = resp.json().get("entities", {}).get(qid, {})
        if entity.get("missing") == "":
            _wikidata_cache[qid] = {}
            return {}
        result = {}
        for prop_id, prop_label in WIKIDATA_CROSSWALK_PROPS.items():
            for claim in entity.get("claims", {}).get(prop_id, []):
                try:
                    val = claim["mainsnak"]["datavalue"]["value"]
                    result[prop_label] = val if isinstance(val, str) else str(val.get("id", val))
                    break
                except (KeyError, TypeError):
                    continue
        _wikidata_cache[qid] = result
        return result
    except Exception as e:
        print(f"  [warn] Wikidata fetch failed for {qid}: {e}", file=sys.stderr)
        _wikidata_cache[qid] = {}
        return {}
    finally:
        time.sleep(0.1)


def fetch_trismegistos_person(tm_id: str) -> dict:
    if tm_id in _tm_cache:
        return _tm_cache[tm_id]
    try:
        resp = requests.get(TM_PERSON_API, params={"id": tm_id, "format": "json"}, timeout=15)
        resp.raise_for_status()
        _tm_cache[tm_id] = resp.json()
        return _tm_cache[tm_id]
    except Exception as e:
        print(f"  [warn] Trismegistos fetch failed for TM {tm_id}: {e}", file=sys.stderr)
        _tm_cache[tm_id] = {}
        return {}
    finally:
        time.sleep(0.15)


def enrich_entities(entities: list[dict], biographical_only: bool = True) -> list[CrosswalkResult]:
    if biographical_only:
        targets = [e for e in entities if
                   e.get("primary_facet") in ("BIOGRAPHIC", "BIOGRAPHICAL", "") or
                   "PERSON" in e.get("entity_types", [])]
        if not targets:
            targets = entities
    else:
        targets = entities
    seen = set()
    unique = [e for e in targets if (q := e.get("entity_qid")) and q not in seen and not seen.add(q)]
    results = []
    for i, entity in enumerate(unique, 1):
        qid = entity.get("entity_qid", "")
        label = entity.get("entity_label", qid)
        # Use external_ids from harvest report when present (avoids Wikidata re-fetch)
        ext = entity.get("external_ids") or {}
        if ext:
            crosswalk = {
                "trismegistos_person_id": ext.get("P1696"),
                "lgpn_id": ext.get("P1838"),
                "viaf_id": ext.get("P1605"),
            }
        else:
            crosswalk = fetch_wikidata_crosswalk(qid)
        tm_id = crosswalk.get("trismegistos_person_id")
        lgpn_id = crosswalk.get("lgpn_id")
        viaf_id = crosswalk.get("viaf_id")
        r = CrosswalkResult(entity_qid=qid, entity_label=label, lgpn_id=lgpn_id, viaf_id=viaf_id)
        if tm_id:
            r.trismegistos_id = tm_id
            r.crosswalk_sources.append("Trismegistos")
            tm_data = fetch_trismegistos_person(tm_id)
            r.trismegistos_name = tm_data.get("name") or tm_data.get("label", "")
            r.trismegistos_dates = tm_data.get("dates") or tm_data.get("date", "")
            r.trismegistos_place = tm_data.get("place") or tm_data.get("Place", "")
        if lgpn_id:
            r.crosswalk_sources.append("LGPN")
        if viaf_id:
            r.crosswalk_sources.append("VIAF")
        r.enriched = bool(tm_id or lgpn_id or viaf_id)
        results.append(r)
        if i % 20 == 0:
            print(f"  {i}/{len(unique)} processed...", file=sys.stderr)
    return results


def load_entities(input_path: Path) -> list[dict]:
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("entities", [])


def main():
    parser = argparse.ArgumentParser(description="Enrich PERSON entities with Trismegistos/LGPN")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output-dir", "-o", default="output/crosswalk")
    parser.add_argument("--all-entities", action="store_true")
    parser.add_argument("--cypher", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--neo4j-uri", default=None)
    parser.add_argument("--neo4j-user", default="neo4j")
    parser.add_argument("--neo4j-password", default=None)
    args = parser.parse_args()

    if not args.cypher and not args.write:
        print("Error: specify --cypher, --write, or both", file=sys.stderr)
        sys.exit(1)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.write and not args.neo4j_uri:
        print("Error: --write requires --neo4j-uri", file=sys.stderr)
        sys.exit(1)
    if args.write and not args.neo4j_password:
        import getpass
        args.neo4j_password = getpass.getpass("Neo4j password: ")

    entities = load_entities(input_path)
    results = enrich_entities(entities, biographical_only=not args.all_entities)
    enriched = [r for r in results if r.enriched]

    (output_dir / "crosswalk_results.json").write_text(
        json.dumps([asdict(r) for r in results], indent=2), encoding="utf-8")
    print(f"Enriched {len(enriched)}/{len(results)} entities")

    if args.cypher:
        lines = ["// PROSOPOGRAPHIC CROSSWALK ENRICHMENT\n"]
        for r in enriched:
            def cypher(v):
                if v is None: return "null"
                if isinstance(v, list): return "[" + ", ".join(f"'{x}'" for x in v) + "]"
                return f"'{str(v).replace(chr(39), chr(92)+chr(39))}'"
            lines.append(f"MATCH (e:Entity {{qid: '{r.entity_qid}'}})\nSET e.trismegistos_id={cypher(r.trismegistos_id)}, e.lgpn_id={cypher(r.lgpn_id)}, e.viaf_id={cypher(r.viaf_id)}, e.crosswalk_sources={cypher(r.crosswalk_sources)}, e.crosswalk_enriched_at=datetime();\n\n")
        (output_dir / "crosswalk_enrichment.cypher").write_text("".join(lines), encoding="utf-8")
        print(f"Cypher written: {output_dir / 'crosswalk_enrichment.cypher'}")

    if args.write:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password))
        with driver.session() as s:
            for r in enriched:
                s.run("""
                    MATCH (e:Entity {qid: $qid}) SET e.trismegistos_id=$tm, e.lgpn_id=$lgpn,
                    e.viaf_id=$viaf, e.crosswalk_sources=$src, e.crosswalk_enriched_at=datetime()
                """, qid=r.entity_qid, tm=r.trismegistos_id, lgpn=r.lgpn_id, viaf=r.viaf_id, src=r.crosswalk_sources)
        driver.close()
        print("Neo4j write complete")


if __name__ == "__main__":
    main()
