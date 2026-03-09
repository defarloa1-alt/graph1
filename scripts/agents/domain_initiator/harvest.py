#!/usr/bin/env python3
"""
Domain Initiator (DI) — Harvest.

Given a domain QID, harvests both directions:
  - Forward links: entities the seed points TO (via its own properties)
  - Backlinks: entities that point TO the seed
  - Seed: all props, external IDs (with labels for every PID and QID)
  - Subject backbone links from seed, forward links, and backlinks

Together, forward + backward links create the full universe of Wikidata entities
connected to the seed. This maximizes context for downstream LLM classification
and SFA routing.

Rule: Never pass PID or QID without its label.

Output: JSON bundle for downstream DI classification (facet assignment, subject resolution).

Usage:
  python scripts/agents/domain_initiator/harvest.py --seed Q17167
  python scripts/agents/domain_initiator/harvest.py --seed Q17167 --limit 500 --output output/di_harvest/
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Set

import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Chrystallum-DomainInitiator/1.0"

# Backlink properties
BACKLINK_PROPERTIES = [
    "P31", "P279", "P361", "P1344", "P793",
    "P17", "P131", "P276", "P706",
]

# External IDs: federation + subject backbone
EXTERNAL_ID_PIDS = {
    "P1584": "Pleiades ID",
    "P1566": "GeoNames ID",
    "P2163": "FAST ID",
    "P1036": "Dewey Decimal Classification",
    "P244": "Library of Congress Authority ID",
    "P214": "VIAF ID",
    "P227": "GND ID",
}

# Geo properties (same set as geo_backlink_discovery) — for geo_properties section
GEO_PIDS = frozenset({"P625", "P276", "P131", "P3896", "P1584", "P1566", "P17", "P706"})
GEO_PID_LABELS = {
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
    bindings = resp.json().get("results", {}).get("bindings", [])
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
    seen: Set[str] = set()
    for prop in BACKLINK_PROPERTIES:
        query = f"""
        SELECT DISTINCT ?item WHERE {{ ?item wdt:{prop} wd:{seed_qid} . }} LIMIT {limit}
        """
        try:
            for row in _query_sparql(query):
                uri = row.get("item", "")
                if uri:
                    qid = uri.split("/")[-1]
                    if qid.startswith("Q"):
                        seen.add(qid)
        except Exception:
            pass
        time.sleep(0.3)
    return sorted(seen)


def fetch_entities(qids: List[str], props: str = "labels|claims|descriptions", batch_size: int = 50) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for i in range(0, len(qids), batch_size):
        batch = qids[i : i + batch_size]
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "format": "json",
            "props": props,
        }
        resp = requests.get(WIKIDATA_API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
        resp.raise_for_status()
        for eid, data in resp.json().get("entities", {}).items():
            if eid != "-1" and "missing" not in data:
                out[eid] = data
        time.sleep(0.5)
    return out


def fetch_property_labels(pids: List[str], batch_size: int = 50) -> Dict[str, str]:
    """Fetch labels for property IDs. Never pass PID without label."""
    out: Dict[str, str] = {}
    for i in range(0, len(pids), batch_size):
        batch = pids[i : i + batch_size]
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "format": "json",
            "props": "labels",
            "languages": "en",
        }
        resp = requests.get(WIKIDATA_API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
        resp.raise_for_status()
        for pid, data in resp.json().get("entities", {}).items():
            lbl = pid
            if "labels" in data and "en" in data["labels"]:
                lbl = data["labels"]["en"].get("value", pid)
            out[pid] = lbl
        time.sleep(0.5)
    return out


def get_label(entity: dict, fallback: str = "") -> str:
    for lang in ("en", "de", "fr", "es", "it"):
        if "labels" in entity and lang in entity["labels"]:
            return entity["labels"][lang].get("value", fallback)
    return fallback or "(no label found)"


def extract_qids_from_claims(claims: dict) -> Set[str]:
    qids: Set[str] = set()
    for pid, stmts in claims.items():
        for stmt in stmts:
            mainsnak = stmt.get("mainsnak", {})
            if mainsnak.get("snaktype") != "value":
                continue
            dv = mainsnak.get("datavalue", {})
            if dv.get("type") != "wikibase-entityid":
                continue
            val = dv.get("value", {})
            qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
            if qid:
                qids.add(qid)
    return qids


def extract_pids_from_claims(claims: dict) -> Set[str]:
    return set(claims.keys())


def extract_claims_labeled(
    claims: dict,
    pid_labels: Dict[str, str],
    qid_labels: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Extract claims with pid+label, value_qid+value_label for every reference."""
    out: List[Dict[str, Any]] = []
    for pid, stmts in claims.items():
        pid_label = pid_labels.get(pid, f"{pid} (no label found)")
        for stmt in stmts:
            mainsnak = stmt.get("mainsnak", {})
            if mainsnak.get("snaktype") != "value":
                continue
            dv = mainsnak.get("datavalue", {})
            val = dv.get("value")
            dtype = dv.get("type", "")
            entry: Dict[str, Any] = {"pid": pid, "label": pid_label}
            if dtype == "wikibase-entityid" and isinstance(val, dict):
                qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
                if qid:
                    entry["value_qid"] = qid
                    entry["value_label"] = qid_labels.get(qid, f"{qid} (no label found)")
            elif pid in EXTERNAL_ID_PIDS:
                s = val if isinstance(val, str) else (str(val.get("value", "")) if isinstance(val, dict) else "")
                if s:
                    entry["value"] = s
            elif dtype == "globecoordinate" and isinstance(val, dict):
                lat = val.get("latitude")
                lon = val.get("longitude")
                if lat is not None and lon is not None:
                    entry["value"] = f"{lat}, {lon}"
            elif isinstance(val, (str, int, float, bool)):
                entry["value"] = val
            elif isinstance(val, dict) and "time" in val:
                entry["value"] = val.get("time", "")
            if "value" in entry or "value_qid" in entry:
                out.append(entry)
    return out


def recommend_actions(
    geo_props: List[Dict[str, Any]],
    external: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Recommend actions for a backlink. Never pass pid/qid without label."""
    actions: List[Dict[str, Any]] = []
    geo_pids_present = {p["pid"] for p in geo_props}
    external_pids = {e["pid"] for e in external}

    # Subject backbone: has FAST, Dewey, or LCNAF
    if external_pids & {"P2163", "P1036", "P244"}:
        actions.append({
            "action": "RESOLVE_SUBJECT",
            "reason": "Has FAST, Dewey, or LCNAF; resolve to most granular subject in backbone",
            "hint": "Query LCC/LCSH/FAST for finest-grained subject; tether domain",
        })

    # Geo facet: has geo properties
    if geo_pids_present:
        geo_hint = []
        if "P1584" in geo_pids_present:
            geo_hint.append("Pleiades ID → consider CREATE_OR_ENRICH_PLACE")
        if "P1566" in geo_pids_present:
            geo_hint.append("GeoNames ID → consider CREATE_OR_ENRICH_PLACE")
        if "P276" in geo_pids_present and "P1584" not in geo_pids_present and "P1566" not in geo_pids_present:
            geo_hint.append("Location only → may be event; run Geo Agent classify")
        actions.append({
            "action": "GEO_FACET",
            "reason": f"Has geo properties: {', '.join(sorted(geo_pids_present))}",
            "hint": "; ".join(geo_hint) if geo_hint else "Run Geo Agent classify for place vs event",
        })

    return actions


def extract_instance_of(claims: dict, qid_labels: Dict[str, str]) -> List[Dict[str, str]]:
    """Extract P31 as instance_of with qid+label."""
    out = []
    for stmt in claims.get("P31", []):
        mainsnak = stmt.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        val = mainsnak.get("datavalue", {}).get("value", {})
        if not isinstance(val, dict):
            continue
        qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
        if qid:
            out.append({"qid": qid, "label": qid_labels.get(qid, f"{qid} (no label found)")})
    return out


def extract_subclass_of(claims: dict, qid_labels: Dict[str, str]) -> List[Dict[str, str]]:
    """Extract P279 as subclass_of with qid+label."""
    out = []
    for stmt in claims.get("P279", []):
        mainsnak = stmt.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        val = mainsnak.get("datavalue", {}).get("value", {})
        if not isinstance(val, dict):
            continue
        qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
        if qid:
            out.append({"qid": qid, "label": qid_labels.get(qid, f"{qid} (no label found)")})
    return out


def extract_geo_properties(
    claims: dict,
    pid_labels: Dict[str, str],
    qid_labels: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Extract geo properties in geo_candidates format: pid+label, value_qid+value_label or value."""
    out: List[Dict[str, Any]] = []
    for pid in GEO_PIDS:
        if pid not in claims:
            continue
        pid_label = pid_labels.get(pid, GEO_PID_LABELS.get(pid, pid))
        for stmt in claims[pid]:
            mainsnak = stmt.get("mainsnak", {})
            if mainsnak.get("snaktype") != "value":
                continue
            dv = mainsnak.get("datavalue", {})
            val = dv.get("value")
            dtype = dv.get("type", "")
            entry: Dict[str, Any] = {"pid": pid, "label": pid_label}
            if pid in ("P1584", "P1566"):
                s = val if isinstance(val, str) else (str(val.get("value", "")) if isinstance(val, dict) else "")
                if s:
                    entry["value"] = s
                    out.append(entry)
            elif pid == "P625" and isinstance(val, dict):
                lat, lon = val.get("latitude"), val.get("longitude")
                if lat is not None and lon is not None:
                    entry["value"] = f"{lat}, {lon}"
                    out.append(entry)
            elif pid in ("P17", "P131", "P276", "P706") and dtype == "wikibase-entityid" and isinstance(val, dict):
                qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
                if qid:
                    entry["value_qid"] = qid
                    entry["value_label"] = qid_labels.get(qid, f"{qid} (no label found)")
                    out.append(entry)
            elif pid == "P3896":
                s = val if isinstance(val, str) else (str(val.get("value", "") or val.get("id", "")) if isinstance(val, dict) else "")
                if s and ("Data:" in s or ".map" in s):
                    entry["value"] = s
                    out.append(entry)
    return out


def extract_external_ids(claims: dict) -> List[Dict[str, Any]]:
    """Extract external IDs (P1584, P1566, P2163, P1036, P244, etc.) with pid+label."""
    out: List[Dict[str, Any]] = []
    for pid in EXTERNAL_ID_PIDS:
        if pid not in claims:
            continue
        label = EXTERNAL_ID_PIDS[pid]
        for stmt in claims[pid]:
            mainsnak = stmt.get("mainsnak", {})
            if mainsnak.get("snaktype") != "value":
                continue
            val = mainsnak.get("datavalue", {}).get("value")
            s = val if isinstance(val, str) else (str(val.get("value", "")) if isinstance(val, dict) else "")
            if s:
                out.append({"pid": pid, "label": label, "value": s})
    return out


def extract_forward_links(seed_claims: dict, seed_qid: str, pid_labels: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
    """
    Extract forward-linked QIDs from seed claims: entities the seed points TO.
    Returns {qid: [{"pid": ..., "label": ...}]} — which PIDs connect seed to each entity.
    """
    forward: Dict[str, List[Dict[str, str]]] = {}
    for pid, stmts in seed_claims.items():
        pid_label = pid_labels.get(pid, pid)
        for stmt in stmts:
            mainsnak = stmt.get("mainsnak", {})
            if mainsnak.get("snaktype") != "value":
                continue
            dv = mainsnak.get("datavalue", {})
            if dv.get("type") != "wikibase-entityid":
                continue
            val = dv.get("value", {})
            qid = val.get("id") or (f"Q{val['numeric-id']}" if val.get("numeric-id") is not None else None)
            if qid and qid != seed_qid:
                if qid not in forward:
                    forward[qid] = []
                forward[qid].append({"pid": pid, "label": pid_label})
    return forward


def _build_candidate(
    qid: str,
    data: dict,
    pid_labels: Dict[str, str],
    qid_labels: Dict[str, str],
    link_direction: str,
    connecting_properties: List[Dict[str, str]] | None = None,
) -> Dict[str, Any]:
    """Build a candidate dict from entity data. Shared by forward and backlink processing."""
    lbl = get_label(data, qid)
    claims = data.get("claims", {})
    instance_of = extract_instance_of(claims, qid_labels)
    subclass_of = extract_subclass_of(claims, qid_labels)
    geo_properties = extract_geo_properties(claims, pid_labels, qid_labels)
    external_ids = extract_external_ids(claims)
    recommended = recommend_actions(geo_properties, external_ids)
    candidate: Dict[str, Any] = {
        "qid": qid,
        "label": lbl,
        "link_direction": link_direction,
        "instance_of": instance_of,
        "subclass_of": subclass_of,
        "geo_properties": geo_properties,
        "external_ids": external_ids,
        "recommended_actions": recommended,
    }
    if connecting_properties:
        candidate["connecting_properties"] = connecting_properties
    return candidate


# ── Discipline traversal ─────────────────────────────────────────────
# Seed → P361 (part of) → P2579 (studied in) → P527 (has part)
# Reaches academic disciplines; each has authority IDs for corpus queries.

DISCIPLINE_TRAVERSAL_PIDS = ["P361", "P2579", "P527"]

# Properties to harvest from each discipline QID
DISCIPLINE_AUTHORITY_PIDS = {
    "P244": "Library of Congress Authority ID",
    "P1036": "Dewey Decimal Classification",
    "P2163": "FAST ID",
    "P1149": "Library of Congress Classification",
    "P910": "topic's main category",
    "P921": "main subject",
}

# Corpus endpoint templates — keyed by source_id matching SYS_FederationSource
CORPUS_ENDPOINTS = {
    "open_alex": {
        "label": "OpenAlex",
        "base_url": "https://api.openalex.org/works",
        "query_type": "topic+keyword",
        "description": "Academic works by topic and keyword, ranked by citation count",
    },
    "internet_archive": {
        "label": "Internet Archive",
        "base_url": "https://archive.org/advancedsearch.php",
        "query_type": "lcsh_subject",
        "description": "Full-text books and primary sources, especially pre-1928 public domain",
    },
    "worldcat": {
        "label": "WorldCat",
        "base_url": "https://search.worldcat.org/search",
        "query_type": "lcsh_subject",
        "description": "Global library holdings by LCSH subject heading",
    },
    "perseus_digital_library": {
        "label": "Perseus Digital Library",
        "base_url": "https://catalog.perseus.org/catalog",
        "query_type": "keyword",
        "description": "Classical primary sources with full text, morphological tools, and translations",
    },
    "jstor": {
        "label": "JSTOR",
        "base_url": "https://www.jstor.org/action/doBasicSearch",
        "query_type": "keyword",
        "description": "Academic journal articles, especially humanities and classics",
    },
    "google_books": {
        "label": "Google Books",
        "base_url": "https://www.googleapis.com/books/v1/volumes",
        "query_type": "lcsh_subject",
        "description": "Book metadata and previews, searchable by LCSH subject",
    },
    "hathi_trust": {
        "label": "HathiTrust",
        "base_url": "https://catalog.hathitrust.org/api/volumes/brief/oclc/",
        "query_type": "oclc+lcsh",
        "description": "Digitized library collections, full text for public domain works",
    },
    "open_library": {
        "label": "Open Library",
        "base_url": "https://openlibrary.org/search.json",
        "query_type": "subject+keyword",
        "description": "Open-access book metadata and lending, Internet Archive integration",
    },
    "open_syllabus": {
        "label": "Open Syllabus",
        "base_url": "https://api.opensyllabus.org/",
        "query_type": "keyword",
        "description": "Most-assigned academic texts by field, indicates canonical teaching corpus",
    },
    "wikidata_p921": {
        "label": "Wikidata (main subject reverse)",
        "base_url": "https://query.wikidata.org/sparql",
        "query_type": "sparql_p921",
        "description": "Scholarly works in Wikidata whose P921 (main subject) = seed or discipline QID",
    },
    "loc": {
        "label": "Library of Congress",
        "base_url": "https://id.loc.gov/",
        "query_type": "lcsh_id",
        "description": "Authority records, subject heading hierarchy, narrower/broader terms",
    },
    "fast": {
        "label": "FAST (OCLC)",
        "base_url": "https://fast.oclc.org/searchfast/fastsuggest",
        "query_type": "fast_id",
        "description": "Faceted subject headings derived from LCSH, optimized for machine use",
    },
    "viaf": {
        "label": "VIAF",
        "base_url": "https://viaf.org/viaf/search",
        "query_type": "keyword",
        "description": "Virtual authority file linking national libraries, resolves name variants",
    },
    "gnd": {
        "label": "GND (German National Library)",
        "base_url": "https://lobid.org/gnd/search",
        "query_type": "keyword",
        "description": "German authority file with rich subject relationships and classifications",
    },
}


def traverse_to_disciplines(seed_qid: str) -> Dict[str, Any]:
    """
    Traverse from seed QID to academic disciplines via P361 -> P2579 -> P527.
    Returns discipline nodes with authority IDs and the traversal path.
    """
    print("\n[D] Traversing to academic disciplines...")

    # Step 1: Get contextual parents — P361 (part of), P31 (instance of), P279 (subclass of)
    # These are the "hop 1" entities that might have P2579 (studied in)
    parents = []
    for pid, pid_label in [("P361", "part of"), ("P31", "instance of"), ("P279", "subclass of"), ("P2348", "time period")]:
        query = f"""
        SELECT ?parent ?parentLabel WHERE {{
          wd:{seed_qid} wdt:{pid} ?parent .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 10
        """
        try:
            for row in _query_sparql(query):
                qid = row["parent"].split("/")[-1]
                label = row.get("parentLabel", qid)
                parents.append({"qid": qid, "label": label, "via": pid})
                print(f"  {pid} ({pid_label}): {seed_qid} -> {qid} ({label})")
        except Exception:
            pass
        time.sleep(0.3)

    # Hop 2: P361 from hop-1 targets (e.g. Q11514315 historical period → P361 → Q486761 classical antiquity)
    hop2_parents = []
    for p in parents:
        query = f"""
        SELECT ?grandparent ?grandparentLabel WHERE {{
          wd:{p['qid']} wdt:P361 ?grandparent .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 5
        """
        try:
            for row in _query_sparql(query):
                gp_qid = row["grandparent"].split("/")[-1]
                gp_label = row.get("grandparentLabel", gp_qid)
                if gp_qid not in {x["qid"] for x in parents} and gp_qid != seed_qid:
                    hop2_parents.append({"qid": gp_qid, "label": gp_label, "via": f"{p['qid']}/P361"})
                    print(f"  P361 hop2: {p['qid']} -> {gp_qid} ({gp_label})")
        except Exception:
            pass
        time.sleep(0.3)

    # Also include the seed itself — some seeds have direct P2579
    search_qids = [seed_qid] + [p["qid"] for p in parents + hop2_parents]

    # Step 2: Get P2579 (studied in) from seed + parents — reaches disciplines
    disciplines_raw: Dict[str, Dict[str, Any]] = {}
    for qid in search_qids:
        query = f"""
        SELECT ?disc ?discLabel ?discDesc WHERE {{
          wd:{qid} wdt:P2579 ?disc .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 10
        """
        try:
            for row in _query_sparql(query):
                d_qid = row["disc"].split("/")[-1]
                d_label = row.get("discLabel", d_qid)
                if d_qid not in disciplines_raw:
                    disciplines_raw[d_qid] = {
                        "qid": d_qid,
                        "label": d_label,
                        "reached_via": qid,
                        "reached_via_property": "P2579",
                    }
                    print(f"  P2579 (studied in): {qid} -> {d_qid} ({d_label})")
        except Exception:
            pass
        time.sleep(0.3)

    # Step 3: Get P527 (has part) from disciplines — sub-disciplines
    sub_disciplines: Dict[str, Dict[str, Any]] = {}
    for d_qid in list(disciplines_raw.keys()):
        query = f"""
        SELECT ?sub ?subLabel WHERE {{
          wd:{d_qid} wdt:P527 ?sub .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 20
        """
        try:
            for row in _query_sparql(query):
                s_qid = row["sub"].split("/")[-1]
                s_label = row.get("subLabel", s_qid)
                if s_qid not in disciplines_raw and s_qid not in sub_disciplines:
                    sub_disciplines[s_qid] = {
                        "qid": s_qid,
                        "label": s_label,
                        "reached_via": d_qid,
                        "reached_via_property": "P527",
                    }
                    print(f"  P527 (has part): {d_qid} -> {s_qid} ({s_label})")
        except Exception:
            pass
        time.sleep(0.3)

    # Also get P279 (subclass of) children of disciplines
    for d_qid in list(disciplines_raw.keys()):
        query = f"""
        SELECT ?child ?childLabel WHERE {{
          ?child wdt:P279 wd:{d_qid} .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 20
        """
        try:
            for row in _query_sparql(query):
                c_qid = row["child"].split("/")[-1]
                c_label = row.get("childLabel", c_qid)
                if c_qid not in disciplines_raw and c_qid not in sub_disciplines:
                    sub_disciplines[c_qid] = {
                        "qid": c_qid,
                        "label": c_label,
                        "reached_via": d_qid,
                        "reached_via_property": "P279_child",
                    }
                    print(f"  P279 child: {d_qid} <- {c_qid} ({c_label})")
        except Exception:
            pass
        time.sleep(0.3)

    # Merge all discipline QIDs
    all_disc = {**disciplines_raw, **sub_disciplines}

    # Step 4: Fetch authority IDs for all discipline QIDs
    if all_disc:
        auth_pids = list(DISCIPLINE_AUTHORITY_PIDS.keys())
        values_clause = " ".join(f"wd:{q}" for q in all_disc)
        filter_clause = " ".join(f"wdt:{p}," for p in auth_pids).rstrip(",")
        query = f"""
        SELECT ?disc ?p ?val WHERE {{
          VALUES ?disc {{ {values_clause} }}
          ?disc ?p ?val .
          FILTER(?p IN ({filter_clause}))
        }} LIMIT 200
        """
        try:
            for row in _query_sparql(query):
                d_qid = row["disc"].split("/")[-1]
                pid = row["p"].split("/")[-1]
                # wdt: prefix comes back as full URI; extract PID
                if "/direct/" in row["p"]:
                    pid = row["p"].split("/direct/")[-1]
                val_raw = row.get("val", "")
                val = val_raw.split("/")[-1] if val_raw.startswith("http") else val_raw
                if d_qid in all_disc:
                    if "authority_ids" not in all_disc[d_qid]:
                        all_disc[d_qid]["authority_ids"] = {}
                    all_disc[d_qid]["authority_ids"][pid] = {
                        "label": DISCIPLINE_AUTHORITY_PIDS.get(pid, pid),
                        "value": val,
                    }
        except Exception as e:
            print(f"  Authority ID fetch failed: {e}")
        time.sleep(0.3)

    print(f"  Found {len(disciplines_raw)} disciplines + {len(sub_disciplines)} sub-disciplines")

    result = {
        "context_parents": parents + hop2_parents,
        "disciplines": list(disciplines_raw.values()),
        "sub_disciplines": list(sub_disciplines.values()),
    }

    # Enrich with Neo4j backbone if available
    result = enrich_discipline_traversal_from_backbone(result)
    return result


def enrich_discipline_traversal_from_backbone(
    discipline_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Enrich discipline_traversal with backbone data from Neo4j Discipline nodes.

    For each discipline QID discovered via SPARQL, check if it exists in the
    Neo4j backbone (tier=backbone) and attach authority IDs + hierarchy context.
    Also discover backbone disciplines connected via SUBCLASS_OF to the
    discovered disciplines (broadens context for SFA training).
    """
    try:
        from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
        from neo4j import GraphDatabase
    except ImportError:
        print("  [backbone] Neo4j driver not available, skipping backbone enrichment")
        return discipline_data

    print("\n  [backbone] Enriching from Neo4j Discipline backbone...")

    # Collect all discovered QIDs
    disc_qids = set()
    for d in discipline_data.get("disciplines", []):
        disc_qids.add(d["qid"])
    for d in discipline_data.get("sub_disciplines", []):
        disc_qids.add(d["qid"])

    if not disc_qids:
        print("  [backbone] No disciplines to enrich")
        return discipline_data

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            # 1. Match discovered QIDs against backbone
            result = session.run("""
                UNWIND $qids AS qid
                MATCH (d:Discipline {qid: qid})
                RETURN d.qid AS qid, d.label AS label, d.tier AS tier,
                       d.lcsh_id AS lcsh_id, d.fast_id AS fast_id,
                       d.lcc AS lcc, d.ddc AS ddc, d.gnd_id AS gnd_id,
                       d.aat_id AS aat_id, d.babelnet_id AS babelnet_id,
                       d.kbpedia_id AS kbpedia_id
            """, qids=list(disc_qids))

            backbone_data = {}
            for r in result:
                backbone_data[r["qid"]] = dict(r)

            matched = sum(1 for v in backbone_data.values() if v.get("tier") == "backbone")
            print(f"  [backbone] {len(backbone_data)} matched in graph ({matched} backbone)")

            # 2. Find nearby backbone disciplines (1 hop SUBCLASS_OF)
            result = session.run("""
                UNWIND $qids AS qid
                MATCH (d:Discipline {qid: qid})-[:SUBCLASS_OF]->(parent:Discipline)
                WHERE parent.tier = 'backbone' AND NOT parent.qid IN $qids
                RETURN DISTINCT parent.qid AS qid, parent.label AS label,
                       parent.lcsh_id AS lcsh_id, parent.fast_id AS fast_id,
                       parent.lcc AS lcc, parent.ddc AS ddc,
                       d.qid AS reached_from
                LIMIT 20
            """, qids=list(disc_qids))

            nearby_backbone = []
            for r in result:
                nearby_backbone.append({
                    "qid": r["qid"],
                    "label": r["label"],
                    "reached_via": r["reached_from"],
                    "reached_via_property": "SUBCLASS_OF_backbone",
                    "authority_ids": {
                        k: {"label": k, "value": r[k]}
                        for k in ("lcsh_id", "fast_id", "lcc", "ddc")
                        if r.get(k)
                    },
                    "tier": "backbone",
                })
            print(f"  [backbone] {len(nearby_backbone)} nearby backbone disciplines discovered")

        driver.close()
    except Exception as e:
        print(f"  [backbone] Neo4j enrichment failed: {e}")
        return discipline_data

    # Merge backbone authority IDs into existing discipline entries
    for d_list in (discipline_data.get("disciplines", []),
                   discipline_data.get("sub_disciplines", [])):
        for d in d_list:
            bd = backbone_data.get(d["qid"])
            if bd:
                d["tier"] = bd.get("tier", "expanded")
                if "backbone_authority_ids" not in d:
                    d["backbone_authority_ids"] = {}
                for key in ("lcsh_id", "fast_id", "lcc", "ddc", "gnd_id",
                            "aat_id", "babelnet_id", "kbpedia_id"):
                    if bd.get(key):
                        d["backbone_authority_ids"][key] = bd[key]

    # Add nearby backbone disciplines
    if nearby_backbone:
        discipline_data.setdefault("backbone_nearby", []).extend(nearby_backbone)

    # Summary counts
    backbone_count = sum(
        1 for d in discipline_data.get("disciplines", []) + discipline_data.get("sub_disciplines", [])
        if d.get("tier") == "backbone"
    )
    discipline_data["backbone_summary"] = {
        "total_in_backbone": backbone_count,
        "nearby_backbone": len(nearby_backbone),
        "enrichment_source": "neo4j_discipline_nodes",
    }

    return discipline_data


def discover_corpus_endpoints(
    seed_qid: str,
    seed_label: str,
    discipline_data: Dict[str, Any],
    seed_lcsh: str | None = None,
) -> Dict[str, Any]:
    """
    Build corpus endpoint manifest for SFA training.
    Uses seed LCSH, discipline authority IDs, and seed label as query keys.
    """
    print("\n[E] Discovering corpus endpoints...")

    # Collect all authority IDs from disciplines
    all_lcsh: List[str] = []
    all_dewey: List[str] = []
    all_fast: List[str] = []
    all_lcc: List[str] = []
    if seed_lcsh:
        all_lcsh.append(seed_lcsh)

    for disc in discipline_data.get("disciplines", []) + discipline_data.get("sub_disciplines", []):
        auth = disc.get("authority_ids", {})
        if "P244" in auth:
            all_lcsh.append(auth["P244"]["value"])
        if "P1036" in auth:
            all_dewey.append(auth["P1036"]["value"])
        if "P2163" in auth:
            all_fast.append(auth["P2163"]["value"])
        if "P1149" in auth:
            all_lcc.append(auth["P1149"]["value"])

    # Build subject query string from seed label
    subject_query = seed_label.replace("_", " ")

    # Probe OpenAlex for topic + work count
    openalex_topic_id = None
    openalex_topic_name = None
    openalex_works_count = 0
    try:
        hdrs = {"User-Agent": USER_AGENT}
        r = requests.get(
            "https://api.openalex.org/topics",
            params={"search": "Classical Antiquity", "per_page": 1},
            headers=hdrs,
            timeout=15,
        )
        if r.status_code == 200 and r.json().get("results"):
            topic = r.json()["results"][0]
            openalex_topic_id = topic["id"]
            openalex_topic_name = topic["display_name"]
            # Count works in this topic matching our seed
            r2 = requests.get(
                "https://api.openalex.org/works",
                params={
                    "filter": f"topics.id:{openalex_topic_id}",
                    "search": subject_query,
                    "per_page": 1,
                },
                headers=hdrs,
                timeout=15,
            )
            if r2.status_code == 200:
                openalex_works_count = r2.json().get("meta", {}).get("count", 0)
    except Exception:
        pass

    # Probe Internet Archive for text count
    ia_count = 0
    ia_query = f'subject:("{subject_query}" OR "{seed_label}") AND mediatype:texts'
    try:
        r = requests.get(
            "https://archive.org/advancedsearch.php",
            params={"q": ia_query, "rows": 0, "output": "json"},
            timeout=15,
        )
        if r.status_code == 200:
            ia_count = r.json().get("response", {}).get("numFound", 0)
    except Exception:
        pass

    # Probe Open Library
    ol_count = 0
    try:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params={"subject": subject_query, "limit": 1},
            timeout=15,
        )
        if r.status_code == 200:
            ol_count = r.json().get("numFound", 0)
    except Exception:
        pass

    # Build endpoint manifest
    endpoints: Dict[str, Any] = {}

    # OpenAlex
    endpoints["open_alex"] = {
        **CORPUS_ENDPOINTS["open_alex"],
        "topic_id": openalex_topic_id,
        "topic_name": openalex_topic_name,
        "works_count": openalex_works_count,
        "query_seed": subject_query,
        "status": "probed" if openalex_works_count > 0 else "no_results",
    }

    # Internet Archive
    endpoints["internet_archive"] = {
        **CORPUS_ENDPOINTS["internet_archive"],
        "query": ia_query,
        "works_count": ia_count,
        "status": "probed" if ia_count > 0 else "no_results",
    }

    # WorldCat (LCSH-keyed, not probed live)
    endpoints["worldcat"] = {
        **CORPUS_ENDPOINTS["worldcat"],
        "lcsh_ids": all_lcsh,
        "query_seed": subject_query,
        "status": "ready" if all_lcsh else "no_lcsh",
    }

    # Perseus Digital Library
    endpoints["perseus_digital_library"] = {
        **CORPUS_ENDPOINTS["perseus_digital_library"],
        "query_seed": subject_query,
        "status": "ready",
    }

    # JSTOR
    endpoints["jstor"] = {
        **CORPUS_ENDPOINTS["jstor"],
        "query_seed": subject_query,
        "status": "ready",
    }

    # Google Books
    endpoints["google_books"] = {
        **CORPUS_ENDPOINTS["google_books"],
        "lcsh_ids": all_lcsh,
        "query_seed": subject_query,
        "status": "ready" if all_lcsh else "keyword_only",
    }

    # HathiTrust
    endpoints["hathi_trust"] = {
        **CORPUS_ENDPOINTS["hathi_trust"],
        "lcsh_ids": all_lcsh,
        "query_seed": subject_query,
        "status": "ready" if all_lcsh else "keyword_only",
    }

    # Open Library
    endpoints["open_library"] = {
        **CORPUS_ENDPOINTS["open_library"],
        "works_count": ol_count,
        "query_seed": subject_query,
        "status": "probed" if ol_count > 0 else "no_results",
    }

    # Open Syllabus
    endpoints["open_syllabus"] = {
        **CORPUS_ENDPOINTS["open_syllabus"],
        "query_seed": subject_query,
        "status": "ready",
    }

    # Wikidata P921 reverse
    endpoints["wikidata_p921"] = {
        **CORPUS_ENDPOINTS["wikidata_p921"],
        "seed_qid": seed_qid,
        "discipline_qids": [d["qid"] for d in discipline_data.get("disciplines", [])],
        "status": "ready",
    }

    # Library of Congress (LCSH authority)
    endpoints["loc"] = {
        **CORPUS_ENDPOINTS["loc"],
        "lcsh_ids": all_lcsh,
        "lcc_codes": all_lcc,
        "status": "ready" if all_lcsh else "no_lcsh",
    }

    # FAST
    endpoints["fast"] = {
        **CORPUS_ENDPOINTS["fast"],
        "fast_ids": all_fast,
        "status": "ready" if all_fast else "no_fast",
    }

    # VIAF
    endpoints["viaf"] = {
        **CORPUS_ENDPOINTS["viaf"],
        "query_seed": subject_query,
        "status": "ready",
    }

    # GND
    endpoints["gnd"] = {
        **CORPUS_ENDPOINTS["gnd"],
        "query_seed": subject_query,
        "status": "ready",
    }

    # Summary
    probed = sum(1 for e in endpoints.values() if e["status"] == "probed")
    ready = sum(1 for e in endpoints.values() if e["status"] == "ready")
    print(f"  {len(endpoints)} corpus endpoints: {probed} probed, {ready} ready")
    if openalex_works_count > 0:
        print(f"  OpenAlex: {openalex_works_count} works in {openalex_topic_name} + \"{subject_query}\"")
    if ia_count > 0:
        print(f"  Internet Archive: {ia_count} texts")
    if ol_count > 0:
        print(f"  Open Library: {ol_count} books")

    return {
        "authority_keys": {
            "lcsh": all_lcsh,
            "dewey": all_dewey,
            "fast": all_fast,
            "lcc": all_lcc,
        },
        "subject_query": subject_query,
        "endpoints": endpoints,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Domain Initiator harvest")
    parser.add_argument("--seed", default="Q17167", help="Domain QID")
    parser.add_argument("--limit", type=int, default=2000, help="Max backlinks per property")
    parser.add_argument("--output", type=Path, default=Path("output/di_harvest"), help="Output directory")
    args = parser.parse_args()

    seed = args.seed.strip().upper()
    if not seed.startswith("Q"):
        seed = f"Q{seed}"

    print(f"Domain Initiator Harvest — seed={seed}")
    print("=" * 60)

    # 1. Fetch backlinks (X → seed)
    print("\n[1] Fetching backlinks...")
    backlink_qids = fetch_backlinks(seed, limit=args.limit)
    print(f"  Found {len(backlink_qids)} unique backlink QIDs")

    # 2. Fetch seed entity first (need claims to extract forward links)
    print("\n[2] Fetching seed entity...")
    seed_entities = fetch_entities([seed])
    seed_data = seed_entities.get(seed, {})
    seed_label = get_label(seed_data, seed)
    seed_claims = seed_data.get("claims", {})
    seed_external = extract_external_ids(seed_claims)

    # 3. Extract forward links (seed → X) with connecting PIDs
    #    Need PID labels first for the seed's own claims
    seed_pids = extract_pids_from_claims(seed_claims)
    seed_pid_labels = fetch_property_labels(list(seed_pids))
    forward_link_map = extract_forward_links(seed_claims, seed, seed_pid_labels)
    forward_qids = sorted(forward_link_map.keys())
    print(f"  Seed: {seed_label} ({seed})")
    print(f"  Forward links from seed: {len(forward_qids)} unique QIDs")

    # 4. Fetch all entities: backlinks + forward links (deduplicated)
    all_candidate_qids = sorted(set(backlink_qids) | set(forward_qids))
    both_directions = set(backlink_qids) & set(forward_qids)
    print(f"\n[3] Fetching entities ({len(all_candidate_qids)} unique candidates)...")
    if both_directions:
        print(f"  {len(both_directions)} entities linked in BOTH directions")
    entities = fetch_entities(all_candidate_qids)
    entities[seed] = seed_data  # include seed
    print(f"  Fetched {len(entities)} entities")

    # 5. Collect all PIDs and QIDs for label resolution
    all_pids: Set[str] = set(seed_pids)
    all_qids: Set[str] = set()
    for data in entities.values():
        claims = data.get("claims", {})
        all_pids.update(extract_pids_from_claims(claims))
        all_qids.update(extract_qids_from_claims(claims))
    all_qids.discard(seed)
    all_qids.update(all_candidate_qids)
    all_qids.add(seed)

    # 6. Fetch all property labels
    print(f"\n[4] Fetching property labels...")
    pid_labels = fetch_property_labels(list(all_pids))
    pid_labels.update(seed_pid_labels)  # merge seed PID labels
    print(f"  Resolved {len(pid_labels)} property labels")

    # 7. Fetch entity labels for all QIDs (never pass QID without label)
    print(f"\n[5] Fetching entity labels...")
    missing_qids = [q for q in all_qids if q not in entities]
    if missing_qids:
        extra = fetch_entities(missing_qids, props="labels")
        entities.update(extra)
    qid_labels = {qid: get_label(entities.get(qid, {}), qid) for qid in all_qids}
    print(f"  Resolved {len(qid_labels)} entity labels")

    # 8. Build candidates — both directions
    candidates: List[Dict[str, Any]] = []
    subject_backbone_ids: Dict[str, List[Dict[str, Any]]] = {"fast": [], "dewey": [], "lcnaf": []}
    seen_qids: Set[str] = set()

    def _collect_backbone(qid: str, lbl: str, external_ids: List[Dict]) -> None:
        for ex in external_ids:
            if ex["pid"] == "P2163":
                subject_backbone_ids["fast"].append({"qid": qid, "label": lbl, "fast_id": ex["value"]})
            elif ex["pid"] == "P1036":
                subject_backbone_ids["dewey"].append({"qid": qid, "label": lbl, "dewey_id": ex["value"]})
            elif ex["pid"] == "P244":
                subject_backbone_ids["lcnaf"].append({"qid": qid, "label": lbl, "lcnaf_id": ex["value"]})

    # Forward links first (seed → X) — tagged with connecting PIDs
    print(f"\n[6] Building candidates...")
    for qid in forward_qids:
        data = entities.get(qid, {})
        if not data:
            continue
        # Entities in both directions get "both" tag
        direction = "both" if qid in both_directions else "forward"
        connecting = forward_link_map.get(qid, [])
        c = _build_candidate(qid, data, pid_labels, qid_labels, direction, connecting)
        _collect_backbone(qid, c["label"], c["external_ids"])
        candidates.append(c)
        seen_qids.add(qid)

    # Backlinks (X → seed) — only those not already added as forward
    for qid in backlink_qids:
        if qid in seen_qids:
            continue
        data = entities.get(qid, {})
        if not data:
            continue
        c = _build_candidate(qid, data, pid_labels, qid_labels, "backlink")
        _collect_backbone(qid, c["label"], c["external_ids"])
        candidates.append(c)
        seen_qids.add(qid)

    # Seed subject backbone links
    for ex in seed_external:
        if ex["pid"] == "P2163":
            subject_backbone_ids["fast"].insert(0, {"qid": seed, "label": seed_label, "fast_id": ex["value"]})
        elif ex["pid"] == "P1036":
            subject_backbone_ids["dewey"].insert(0, {"qid": seed, "label": seed_label, "dewey_id": ex["value"]})
        elif ex["pid"] == "P244":
            subject_backbone_ids["lcnaf"].insert(0, {"qid": seed, "label": seed_label, "lcnaf_id": ex["value"]})

    # Count by direction
    fwd_count = sum(1 for c in candidates if c["link_direction"] == "forward")
    back_count = sum(1 for c in candidates if c["link_direction"] == "backlink")
    both_count = sum(1 for c in candidates if c["link_direction"] == "both")
    print(f"  Forward: {fwd_count}, Backlink: {back_count}, Both: {both_count}, Total: {len(candidates)}")

    # 9. Discipline traversal and corpus endpoint discovery
    discipline_data = traverse_to_disciplines(seed)

    # Extract seed LCSH for corpus queries
    seed_lcsh = None
    for ex in seed_external:
        if ex["pid"] == "P244":
            seed_lcsh = ex["value"]
            break

    corpus_data = discover_corpus_endpoints(seed, seed_label, discipline_data, seed_lcsh)

    # 10. Top-level recommended next steps
    has_subject_links = any(subject_backbone_ids[k] for k in subject_backbone_ids)
    geo_count = sum(1 for c in candidates if any(a["action"] == "GEO_FACET" for a in c.get("recommended_actions", [])))
    recommended_next_steps = [
        {
            "action": "DI_CLASSIFY",
            "reason": "Run LLM classification for all 18 facets",
            "hint": "Consume this harvest; output per-facet deltas for SCA routing",
        },
    ]
    if has_subject_links:
        recommended_next_steps.append({
            "action": "RESOLVE_SUBJECT",
            "reason": "Harvest contains FAST/Dewey/LCNAF links",
            "hint": "Resolve to most granular subject in LCC/LCSH/FAST backbone; tether domain",
        })
    if geo_count > 0:
        recommended_next_steps.append({
            "action": "GEO_FACET",
            "reason": f"{geo_count} candidates have geo properties",
            "hint": "Run Geo Agent classify on geo-filtered subset, or consume via DI classify",
        })

    payload = {
        "recommended_next_steps": recommended_next_steps,
        "seed": {"qid": seed, "label": seed_label},
        "backlinks_total": len(backlink_qids),
        "forward_links_total": len(forward_qids),
        "both_directions_total": len(both_directions),
        "candidates_count": len(candidates),
        "candidates": candidates,
        "subject_backbone_links": subject_backbone_ids,
        "discipline_traversal": discipline_data,
        "corpus_endpoints": corpus_data,
        "_meta": {
            "rule": "Never pass PID or QID without label",
            "pid_labels_resolved": len(pid_labels),
            "qid_labels_resolved": len(qid_labels),
        },
    }

    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / f"{seed}_di_harvest.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Wrote: {out_path}")
    print(f"  Candidates: {len(candidates)}, subject backbone: FAST={len(subject_backbone_ids['fast'])}, Dewey={len(subject_backbone_ids['dewey'])}, LCNAF={len(subject_backbone_ids['lcnaf'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
