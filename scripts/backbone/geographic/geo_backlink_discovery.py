#!/usr/bin/env python3
"""
Geo Backlink Discovery — Exploratory run.

Queries Wikidata for backlinks to a domain QID (e.g. Q17167 Roman Republic),
then filters for items that have at least one backbone-mappable geo property:
P625 (coords), P276 (location), P131 (admin), P3896 (geoshape), P1584 (Pleiades), P1566 (GeoNames).
P17 (country) alone does NOT qualify — topics/concepts often have P17 but are not places.

Outputs candidates with values (and labels) for each geo property.

Usage:
  python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167
  python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167 --limit 500
  python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167 --output output/geo_discovery/
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Set

import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Chrystallum-GeoDiscovery/1.0 (exploratory)"

# Backlink properties — broad set to discover items related to domain
BACKLINK_PROPERTIES = [
    "P31",   # instance of
    "P279",  # subclass of
    "P361",  # part of
    "P1344", # participated in
    "P793",  # significant event
    "P17",   # country
    "P131",  # located in administrative entity
    "P276",  # location
    "P706",  # located in/on physical feature
]

# Geo properties that QUALIFY for backbone mapping — must have at least one.
# P17 (country) alone does NOT qualify — topics/concepts often have P17.
# P625, P276, P131, P3896, P1584, P1566 = actual place-like anchors.
GEO_PROPERTIES_QUALIFYING = frozenset([
    "P625",   # coordinate location
    "P276",   # location
    "P131",   # located in administrative entity
    "P3896",  # geoshape
    "P1584",  # Pleiades ID
    "P1566",  # GeoNames ID
])

# All geo properties we extract (including P17, P706 for context when present)
GEO_PROPERTIES = {
    "P625": "coordinate location",
    "P131": "located in administrative entity",
    "P17": "country",
    "P3896": "geoshape",
    "P1584": "Pleiades ID",
    "P1566": "GeoNames ID",
    "P276": "location",
    "P706": "located in/on physical feature",
}


def _query_sparql(query: str, timeout: int = 60) -> List[Dict]:
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    resp = requests.get(SPARQL_URL, params={"query": query}, headers=headers, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    bindings = payload.get("results", {}).get("bindings", [])
    out = []
    for row in bindings:
        parsed = {}
        for k, v in row.items():
            if isinstance(v, dict):
                parsed[k] = v.get("value", "")
            else:
                parsed[k] = v
        out.append(parsed)
    return out


def fetch_backlinks(seed_qid: str, limit: int = 2000) -> List[str]:
    """Fetch backlink QIDs from seed via multiple properties."""
    seen: Set[str] = set()
    for prop in BACKLINK_PROPERTIES:
        query = f"""
        SELECT DISTINCT ?item
        WHERE {{
          ?item wdt:{prop} wd:{seed_qid} .
        }}
        LIMIT {limit}
        """
        try:
            rows = _query_sparql(query)
            for row in rows:
                uri = row.get("item", "")
                if uri:
                    qid = uri.split("/")[-1]
                    if qid.startswith("Q"):
                        seen.add(qid)
        except Exception:
            pass
        time.sleep(0.3)  # rate limit
    return sorted(seen)


def fetch_entity_claims(qids: List[str], batch_size: int = 50) -> Dict[str, dict]:
    """Fetch claims for QIDs via wbgetentities."""
    out: Dict[str, dict] = {}
    for i in range(0, len(qids), batch_size):
        batch = qids[i : i + batch_size]
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "format": "json",
            "props": "labels|claims",
        }
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=60)
        resp.raise_for_status()
        entities = resp.json().get("entities", {})
        for eid, data in entities.items():
            if eid != "-1" and "missing" not in data:
                out[eid] = data
        time.sleep(0.5)
    return out


def has_qualifying_geo_property(claims: dict) -> bool:
    """True if entity has at least one property that maps to geo backbone (P625, P276, P131, P3896, P1584, P1566)."""
    for pid in GEO_PROPERTIES_QUALIFYING:
        if pid in claims and claims[pid]:
            return True
    return False


def _extract_geo_values(claims: dict) -> Dict[str, List[dict]]:
    """Extract values for each geo property. Returns {pid: [{value, value_label?}, ...]}."""
    out: Dict[str, List[dict]] = {}
    for pid in GEO_PROPERTIES:
        if pid not in claims or not claims[pid]:
            continue
        values = []
        for stmt in claims[pid]:
            mainsnak = stmt.get("mainsnak", {})
            if mainsnak.get("snaktype") != "value":
                continue
            dv = mainsnak.get("datavalue", {})
            val = dv.get("value")
            dtype = dv.get("type", "")
            if pid == "P625":
                if isinstance(val, dict) and "latitude" in val and "longitude" in val:
                    values.append({"lat": val["latitude"], "lon": val["longitude"]})
            elif pid in ("P1584", "P1566"):
                # external-id: value is string
                s = val if isinstance(val, str) else (str(val.get("value", "")) if isinstance(val, dict) else "")
                if s:
                    values.append({"value": s})
            elif pid in ("P17", "P131", "P276", "P706"):
                if dtype == "wikibase-entityid" and isinstance(val, dict):
                    qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
                    if qid:
                        values.append({"qid": qid})
            elif pid == "P3896":
                s = val if isinstance(val, str) else (val.get("value") or val.get("id") or "") if isinstance(val, dict) else ""
                if s and ("Data:" in str(s) or ".map" in str(s)):
                    values.append({"value": s if isinstance(s, str) else str(s)})
        if values:
            out[pid] = values
    return out


def _extract_item_qids(claims: dict, pid: str) -> List[str]:
    """Extract QID values from wikibase-item claims."""
    qids = []
    for stmt in claims.get(pid, []):
        mainsnak = stmt.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        dv = mainsnak.get("datavalue", {})
        if dv.get("type") != "wikibase-entityid":
            continue
        val = dv.get("value", {})
        qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
        if qid and qid not in qids:
            qids.append(qid)
    return qids


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exploratory geo backlink discovery from domain QID"
    )
    parser.add_argument("--seed", default="Q17167", help="Domain QID (default: Q17167 Roman Republic)")
    parser.add_argument("--limit", type=int, default=2000, help="Max backlinks per property")
    parser.add_argument("--output", type=Path, default=Path("output/geo_discovery"), help="Output directory")
    args = parser.parse_args()

    seed = args.seed.strip().upper()
    if not seed.startswith("Q"):
        seed = f"Q{seed}"

    print(f"Geo Backlink Discovery — seed={seed}")
    print("=" * 60)

    # 1. Fetch backlinks
    print("\n[1] Fetching backlinks...")
    backlink_qids = fetch_backlinks(seed, limit=args.limit)
    print(f"  Found {len(backlink_qids)} unique backlink QIDs")

    # 2. Fetch claims for each (include seed for its label)
    print("\n[2] Fetching entity claims...")
    qids_to_fetch = list(set(backlink_qids) | {seed})
    entities = fetch_entity_claims(qids_to_fetch)
    print(f"  Fetched {len(entities)} entities")

    # 3. Filter for qualifying geo (P625, P276, P131, P3896, P1584, P1566 only)
    candidates: List[dict] = []
    type_qids: Set[str] = set()
    value_qids: Set[str] = set()
    for qid, data in entities.items():
        claims = data.get("claims", {})
        if not has_qualifying_geo_property(claims):
            continue
        geo_values = _extract_geo_values(claims)
        for pid, vals in geo_values.items():
            for v in vals:
                if "qid" in v:
                    value_qids.add(v["qid"])
        label = ""
        if "labels" in data:
            for lang in ("en", "de", "fr", "es", "it"):
                if lang in data["labels"]:
                    label = data["labels"][lang].get("value", "")
                    break
        if not label:
            label = f"{qid} (no label found)"
        p31_qids = _extract_item_qids(claims, "P31")
        p279_qids = _extract_item_qids(claims, "P279")
        type_qids.update(p31_qids)
        type_qids.update(p279_qids)
        candidates.append({
            "qid": qid,
            "label": label,
            "instance_of_qids": p31_qids,
            "subclass_of_qids": p279_qids,
            "geo_values_raw": geo_values,
        })

    print(f"\n[3] Geo-type candidates: {len(candidates)}")

    # 3b. Fetch labels for P31/P279 type QIDs
    type_labels: Dict[str, str] = {}
    if type_qids:
        print("\n[3b] Fetching instance-of/subclass-of labels...")
        type_entities = fetch_entity_claims(list(type_qids))
        for tid, tdata in type_entities.items():
            lbl = tid
            if "labels" in tdata:
                for lang in ("en", "de", "fr", "es", "it"):
                    if lang in tdata["labels"]:
                        lbl = tdata["labels"][lang].get("value", tid)
                        break
            if lbl == tid:
                lbl = f"{tid} (no label found)"
            type_labels[tid] = lbl

    # 3c. Fetch labels for geo value QIDs (P17, P131, P276, P706 targets)
    value_labels: Dict[str, str] = {}
    if value_qids:
        print("\n[3c] Fetching geo value labels...")
        value_entities = fetch_entity_claims(list(value_qids))
        for vid, vdata in value_entities.items():
            lbl = vid
            if "labels" in vdata:
                for lang in ("en", "de", "fr", "es", "it"):
                    if lang in vdata["labels"]:
                        lbl = vdata["labels"][lang].get("value", vid)
                        break
            if lbl == vid:
                lbl = f"{vid} (no label found)"
            value_labels[vid] = lbl

    # Add instance_of and subclass_of with labels
    for c in candidates:
        c["instance_of"] = [{"qid": q, "label": type_labels.get(q, f"{q} (no label found)")} for q in c["instance_of_qids"]]
        c["subclass_of"] = [{"qid": q, "label": type_labels.get(q, f"{q} (no label found)")} for q in c["subclass_of_qids"]]
        del c["instance_of_qids"]
        del c["subclass_of_qids"]

        # Build geo_properties with values and labels
        geo_props = []
        for pid, vals in sorted(c["geo_values_raw"].items()):
            for v in vals:
                entry = {"pid": pid, "label": GEO_PROPERTIES[pid]}
                if "qid" in v:
                    entry["value_qid"] = v["qid"]
                    entry["value_label"] = value_labels.get(v["qid"], f"{v['qid']} (no label found)")
                elif "lat" in v and "lon" in v:
                    entry["value"] = f"{v['lat']}, {v['lon']}"
                elif "value" in v:
                    entry["value"] = v["value"]
                geo_props.append(entry)
        c["geo_properties"] = geo_props
        del c["geo_values_raw"]

    # 4. Summary by geo property (labeled only)
    prop_counts: Dict[str, int] = {}
    for c in candidates:
        for item in c["geo_properties"]:
            p = item["pid"]
            prop_counts[p] = prop_counts.get(p, 0) + 1
    geo_property_counts = [
        {"pid": pid, "label": GEO_PROPERTIES[pid], "count": prop_counts.get(pid, 0)}
        for pid in sorted(GEO_PROPERTIES)
    ]
    print("\n  Geo property distribution:")
    for pid in sorted(GEO_PROPERTIES):
        cnt = prop_counts.get(pid, 0)
        print(f"    {pid} ({GEO_PROPERTIES[pid]}): {cnt}")

    # 5. Write output
    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / f"{seed}_geo_candidates.json"
    seed_label = seed
    if seed in entities and "labels" in entities.get(seed, {}):
        for lang in ("en", "de", "fr", "es", "it"):
            if lang in entities[seed]["labels"]:
                seed_label = entities[seed]["labels"][lang].get("value", seed)
                break
    if seed_label == seed:
        seed_label = f"{seed} (no label found)"

    payload = {
        "seed": {"qid": seed, "label": seed_label},
        "qualifying_filter": "at least one of P625, P276, P131, P3896, P1584, P1566 (P17 alone excluded)",
        "backlinks_total": len(backlink_qids),
        "candidates_count": len(candidates),
        "geo_property_counts": geo_property_counts,
        "candidates": candidates,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"\n  Wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
