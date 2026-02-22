#!/usr/bin/env python3
"""
Build canonical place-type token mapping from Pleiades token frequencies.

Inputs:
  - Geographic/pleiades_place_type_distinct_tokens_2026-02-18.csv
  - CSV/geographic/place_type_hierarchy_v1.csv

Outputs:
  - CSV/geographic/pleiades_place_type_token_mapping_v1.csv
  - CSV/geographic/pleiades_place_type_token_mapping_review_v1.csv

Optional:
  - Load PlaceType hierarchy and mappings into Neo4j.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import sys
import time
from http import HTTPStatus
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_LANGS = ["en", "mul", "la", "fr", "de", "it", "es"]
WIKIDATA_MIN_INTERVAL_SECONDS = 0.8
WIKIDATA_MAX_RETRIES = 6
_WIKIDATA_LAST_REQUEST_TS = 0.0
WIKIDATA_GEO_PIDS = ["P131", "P17", "P276", "P706", "P7153", "P625"]
WIKIDATA_TIME_PIDS = ["P580", "P582", "P571", "P576", "P585", "P2348", "P9350"]
WIKIDATA_TIME_START_PIDS = ["P580", "P571"]
WIKIDATA_TIME_END_PIDS = ["P582", "P576"]
DISTINCTION_ROOT_TYPE_IDS = {"MAN_MADE_STRUCTURE", "PHYSICAL_FEATURE", "SETTLEMENT_TYPE"}
LOW_INFORMATION_TOKENS = {
    "unlocated",
    "unlabeled",
    "label",
    "feature",
    "people",
    "unknown",
    "false",
    "labeled feature",
    "numbered feature",
}
REVIEW_REQUIRED = "REVIEW_REQUIRED"
REVIEW_LOW_SIGNAL = "LOW_SIGNAL_SKIP_REVIEW"
REVIEW_AUTO = "AUTO_MAPPED"
STAR_GOLD_EXCEPTION_TOKENS = {
    "year",
    "years",
    "decade",
    "decades",
    "century",
    "centuries",
    "millennium",
    "millennia",
    "derived",
}


def norm(token: str) -> str:
    return re.sub(r"\s+", " ", (token or "").strip().lower())


def split_place_type_tokens(raw: str) -> List[str]:
    """
    Split a comma-separated place_type field into normalized token values.
    """
    out: List[str] = []
    for part in (raw or "").split(","):
        token = norm(part)
        if token:
            out.append(token)
    return out


def load_geonames_signal_by_token(summary_csv: Path) -> Dict[str, int]:
    """
    Build token -> count map where token appears on a row with geonames_count > 0.
    """
    out: Dict[str, int] = {}
    if not summary_csv.exists():
        return out
    with summary_csv.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                geonames_count = int((row.get("geonames_count") or "0").strip() or 0)
            except ValueError:
                geonames_count = 0
            if geonames_count <= 0:
                continue
            for token in split_place_type_tokens(row.get("place_type", "")):
                out[token] = out.get(token, 0) + 1
    return out


def best_label(labels_obj: Dict[str, Dict[str, str]], fallback: str) -> str:
    for lang in WIKIDATA_LANGS:
        if lang in labels_obj and labels_obj[lang].get("value"):
            return labels_obj[lang]["value"]
    if labels_obj:
        first = next(iter(labels_obj.values())).get("value")
        if first:
            return first
    return fallback


def chunked(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _throttle_wikidata() -> None:
    global _WIKIDATA_LAST_REQUEST_TS
    now = time.time()
    elapsed = now - _WIKIDATA_LAST_REQUEST_TS
    if elapsed < WIKIDATA_MIN_INTERVAL_SECONDS:
        time.sleep(WIKIDATA_MIN_INTERVAL_SECONDS - elapsed)
    _WIKIDATA_LAST_REQUEST_TS = time.time()


def _retry_after_seconds(exc: urllib.error.HTTPError) -> Optional[float]:
    hdr = exc.headers.get("Retry-After") if exc.headers else None
    if not hdr:
        return None
    try:
        sec = float(hdr.strip())
        return max(0.0, sec)
    except (TypeError, ValueError):
        return None


def _wikidata_api(params: Dict[str, str], timeout: int = 90) -> dict:
    qs = urllib.parse.urlencode(params)
    url = f"{WIKIDATA_API}?{qs}"
    last_exc: Optional[Exception] = None
    for attempt in range(WIKIDATA_MAX_RETRIES):
        try:
            _throttle_wikidata()
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Chrystallum-Graph1/1.0 (place-type-mapper)"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if exc.code in {HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.SERVICE_UNAVAILABLE} and attempt < (WIKIDATA_MAX_RETRIES - 1):
                retry_after = _retry_after_seconds(exc)
                if retry_after is not None:
                    delay = retry_after + 0.2
                else:
                    delay = max(WIKIDATA_MIN_INTERVAL_SECONDS, 1.5 * (attempt + 1))
                time.sleep(delay)
                continue
            raise
        except urllib.error.URLError as exc:
            last_exc = exc
            if attempt < (WIKIDATA_MAX_RETRIES - 1):
                delay = max(WIKIDATA_MIN_INTERVAL_SECONDS, 1.0 * (attempt + 1))
                time.sleep(delay)
                continue
            raise
    if last_exc:
        raise last_exc
    return {}


def wikidata_search(term: str, limit: int = 5) -> List[dict]:
    payload = _wikidata_api(
        {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "type": "item",
            "limit": str(limit),
            "search": term,
        }
    )
    return payload.get("search", []) or []


def wikidata_fetch_entities(ids: List[str]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not ids:
        return out
    for batch in chunked(ids, 40):
        payload = _wikidata_api(
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "format": "json",
                "props": "labels|claims|descriptions",
                "languages": "|".join(WIKIDATA_LANGS),
            },
            timeout=120,
        )
        out.update(payload.get("entities", {}))
    return out


def _extract_item_ids(entity: dict, pid: str) -> List[str]:
    out: List[str] = []
    for stmt in entity.get("claims", {}).get(pid, []):
        mainsnak = stmt.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        dv = mainsnak.get("datavalue", {}).get("value", {})
        qid = dv.get("id")
        if not qid:
            num = dv.get("numeric-id")
            if num is not None:
                qid = f"Q{num}"
        if qid and qid.startswith("Q"):
            out.append(qid)
    return out


def _claim_values(entity: dict, pid: str) -> List[str]:
    out: List[str] = []
    for stmt in entity.get("claims", {}).get(pid, []):
        mainsnak = stmt.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        dv = mainsnak.get("datavalue", {}).get("value")
        if dv is None:
            continue
        if isinstance(dv, dict):
            if "id" in dv:
                out.append(str(dv.get("id")))
            elif "time" in dv:
                out.append(str(dv.get("time")))
            elif "text" in dv:
                out.append(str(dv.get("text")))
            elif "latitude" in dv and "longitude" in dv:
                out.append(f"{dv.get('latitude')},{dv.get('longitude')}")
            else:
                out.append(json.dumps(dv, ensure_ascii=False))
        else:
            out.append(str(dv))
    return out


def _present_pids(entity: dict, pids: List[str]) -> List[str]:
    claims = entity.get("claims", {})
    return sorted([pid for pid in pids if pid in claims and claims.get(pid)])


def _label_match_strength(token: str, label: str) -> int:
    t = norm(token)
    l = norm(label)
    if not t or not l:
        return 0
    if l == t:
        return 3
    pattern = r"(^|[^a-z0-9])" + re.escape(t).replace(r"\ ", r"\s+") + r"([^a-z0-9]|$)"
    if re.search(pattern, l):
        return 2
    t_words = set([w for w in t.split(" ") if w])
    l_words = set([w for w in l.split(" ") if w])
    if t_words and l_words:
        overlap = len(t_words.intersection(l_words))
        if overlap > 0 and (overlap / max(1, len(t_words))) >= 0.5:
            return 1
    return 0


def _canonical_from_text(text: str) -> Tuple[str, int, str]:
    t = norm(text)
    if not t:
        return ("UNKNOWN_OR_NEEDS_REVIEW", 0, "none")

    keyword_map: Dict[str, List[str]] = {
        "SETTLEMENT": [
            "settlement",
            "populated place",
            "city",
            "town",
            "village",
            "municipality",
            "hamlet",
            "colony",
        ],
        "REGION": [
            "region",
            "province",
            "district",
            "territory",
            "kingdom",
            "country",
            "administrative",
            "county",
            "state",
            "empire",
        ],
        "ARCHAEOLOGICAL_SITE": [
            "archaeological",
            "archaeology",
            "site",
            "tomb",
            "necropolis",
            "tell",
            "ruin",
            "excavation",
            "tumulus",
        ],
        "TRANSPORT_FEATURE": [
            "road",
            "route",
            "bridge",
            "canal",
            "pass",
            "port",
            "harbor",
            "harbour",
            "station",
            "aqueduct",
            "street",
        ],
        "SACRED_BUILT_FEATURE": [
            "temple",
            "sanctuary",
            "church",
            "shrine",
            "monastery",
            "abbey",
            "basilica",
            "mosque",
        ],
        "DEFENSIVE_BUILT_FEATURE": [
            "fort",
            "fortress",
            "castle",
            "wall",
            "citadel",
            "garrison",
            "defensive",
        ],
        "WATER_FEATURE": [
            "river",
            "sea",
            "lake",
            "gulf",
            "strait",
            "bay",
            "spring",
            "water",
            "canal",
        ],
        "LAND_FEATURE": [
            "island",
            "mountain",
            "hill",
            "cave",
            "cape",
            "desert",
            "valley",
            "plain",
            "plateau",
            "archipelago",
            "peninsula",
            "oasis",
            "forest",
            "marsh",
            "wetland",
            "bay",
        ],
        "BUILT_FEATURE": [
            "building",
            "structure",
            "monument",
            "theatre",
            "theater",
            "amphitheatre",
            "amphitheater",
            "bath",
            "villa",
            "forum",
            "acropolis",
            "dam",
            "tower",
            "quarry",
            "mine",
            "palace",
            "lighthouse",
            "cistern",
            "fountain",
            "pyramid",
        ],
    }
    scores: Dict[str, int] = {}
    matches: Dict[str, List[str]] = {}
    for ctype, words in keyword_map.items():
        hit = [w for w in words if w in t]
        if hit:
            scores[ctype] = len(set(hit))
            matches[ctype] = sorted(set(hit))
    if not scores:
        return ("UNKNOWN_OR_NEEDS_REVIEW", 0, "none")
    best = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return (best, scores[best], ",".join(matches.get(best, [])))


def resolve_token_with_wikidata(token: str, search_limit: int = 5) -> Dict[str, str]:
    """
    Query Wikidata and infer a canonical place type from term match + P31/P279 labels.
    """
    out = {
        "wikidata_match_qid": "",
        "wikidata_match_label": "",
        "wikidata_match_description": "",
        "wikidata_type_qids": "",
        "wikidata_type_labels": "",
        "wikidata_geo_score": "0",
        "wikidata_geo_matches": "",
        "wikidata_label_match_strength": "0",
        "wikidata_geo_pids_present": "",
        "wikidata_geo_pid_count": "0",
        "wikidata_time_pids_present": "",
        "wikidata_time_pid_count": "0",
        "wikidata_periodo_ids": "",
        "wikidata_start_time_values": "",
        "wikidata_end_time_values": "",
        "wikidata_inferred_type": "UNKNOWN_OR_NEEDS_REVIEW",
        "wikidata_error": "",
    }
    try:
        candidates = wikidata_search(token, limit=search_limit)
        if not candidates:
            return out

        candidate_qids = [c.get("id", "") for c in candidates if c.get("id", "").startswith("Q")]
        entities = wikidata_fetch_entities(candidate_qids)

        # Pull direct type IDs for one-hop typing context.
        type_qids: Set[str] = set()
        entity_type_map: Dict[str, List[str]] = {}
        for qid in candidate_qids:
            ent = entities.get(qid, {})
            ids = sorted(set(_extract_item_ids(ent, "P31") + _extract_item_ids(ent, "P279")))
            entity_type_map[qid] = ids
            type_qids.update(ids)

        type_entities = wikidata_fetch_entities(sorted(type_qids))

        best: Optional[dict] = None
        for cand in candidates:
            qid = cand.get("id", "")
            if not qid or qid not in entities:
                continue

            entity = entities[qid]
            label = cand.get("label") or best_label(entity.get("labels", {}), qid)
            desc = cand.get("description") or best_label(entity.get("descriptions", {}), "")
            t_ids = entity_type_map.get(qid, [])
            t_labels = [
                best_label(type_entities.get(tid, {}).get("labels", {}), tid)
                for tid in t_ids
            ]
            geo_pids = _present_pids(entity, WIKIDATA_GEO_PIDS)
            time_pids = _present_pids(entity, WIKIDATA_TIME_PIDS)
            periodo_ids = sorted(set(_claim_values(entity, "P9350")))
            start_times = sorted(
                set(v for pid in WIKIDATA_TIME_START_PIDS for v in _claim_values(entity, pid))
            )
            end_times = sorted(
                set(v for pid in WIKIDATA_TIME_END_PIDS for v in _claim_values(entity, pid))
            )

            primary_blob = " | ".join([label] + t_labels)
            inferred, score, matched = _canonical_from_text(primary_blob)
            if score == 0 and desc:
                inferred, score, matched = _canonical_from_text(" | ".join([label, desc] + t_labels))
            row = {
                "qid": qid,
                "label": label,
                "description": desc,
                "type_qids": t_ids,
                "type_labels": t_labels,
                "score": score,
                "matches": matched,
                "inferred": inferred,
                "label_match_strength": _label_match_strength(token, label),
                "geo_pids": geo_pids,
                "time_pids": time_pids,
                "geo_pid_count": len(geo_pids),
                "time_pid_count": len(time_pids),
                "periodo_ids": periodo_ids,
                "start_times": start_times,
                "end_times": end_times,
            }
            if best is None or (
                row["score"],
                row["label_match_strength"],
                row["geo_pid_count"] + row["time_pid_count"],
                row["geo_pid_count"],
                row["time_pid_count"],
            ) > (
                best["score"],
                best["label_match_strength"],
                best["geo_pid_count"] + best["time_pid_count"],
                best["geo_pid_count"],
                best["time_pid_count"],
            ):
                best = row

        if not best:
            return out

        out["wikidata_match_qid"] = best["qid"]
        out["wikidata_match_label"] = best["label"]
        out["wikidata_match_description"] = best["description"]
        out["wikidata_type_qids"] = "|".join(best["type_qids"])
        out["wikidata_type_labels"] = "|".join(best["type_labels"])
        out["wikidata_geo_score"] = str(best["score"])
        out["wikidata_geo_matches"] = best["matches"]
        out["wikidata_label_match_strength"] = str(best["label_match_strength"])
        out["wikidata_geo_pids_present"] = "|".join(best["geo_pids"])
        out["wikidata_geo_pid_count"] = str(best["geo_pid_count"])
        out["wikidata_time_pids_present"] = "|".join(best["time_pids"])
        out["wikidata_time_pid_count"] = str(best["time_pid_count"])
        out["wikidata_periodo_ids"] = "|".join(best["periodo_ids"])
        out["wikidata_start_time_values"] = "|".join(best["start_times"][:3])
        out["wikidata_end_time_values"] = "|".join(best["end_times"][:3])
        out["wikidata_inferred_type"] = best["inferred"]
        return out
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
        out["wikidata_error"] = str(exc)
        return out


def classify_token(token: str) -> Tuple[str, str, bool]:
    """
    Returns: (canonical_type_id, mapping_rule, needs_review)
    """
    t = norm(token)
    if not t:
        return ("UNKNOWN_OR_NEEDS_REVIEW", "empty_token", True)

    exact = {
        # Populated place
        "settlement": "SETTLEMENT",
        "settlement-modern": "SETTLEMENT",
        "village": "SETTLEMENT",
        "town": "SETTLEMENT",
        "city": "SETTLEMENT",
        # Admin/region
        "region": "REGION",
        "province": "REGION",
        "district": "REGION",
        "territory": "REGION",
        # Archaeological
        "archaeological-site": "ARCHAEOLOGICAL_SITE",
        "findspot": "ARCHAEOLOGICAL_SITE",
        "tell": "ARCHAEOLOGICAL_SITE",
        "cemetery": "ARCHAEOLOGICAL_SITE",
        "tomb": "ARCHAEOLOGICAL_SITE",
        # Transport
        "road": "TRANSPORT_FEATURE",
        "station": "TRANSPORT_FEATURE",
        "bridge": "TRANSPORT_FEATURE",
        "aqueduct": "TRANSPORT_FEATURE",
        "harbor": "TRANSPORT_FEATURE",
        "port": "TRANSPORT_FEATURE",
        # Built
        "villa": "BUILT_FEATURE",
        "bath": "BUILT_FEATURE",
        "monument": "BUILT_FEATURE",
        "mine": "BUILT_FEATURE",
        "mine-2": "BUILT_FEATURE",
        # Defensive built
        "fort": "DEFENSIVE_BUILT_FEATURE",
        "fort-2": "DEFENSIVE_BUILT_FEATURE",
        "wall": "DEFENSIVE_BUILT_FEATURE",
        # Sacred built
        "temple": "SACRED_BUILT_FEATURE",
        "temple-2": "SACRED_BUILT_FEATURE",
        "sanctuary": "SACRED_BUILT_FEATURE",
        "church": "SACRED_BUILT_FEATURE",
        "monastery": "SACRED_BUILT_FEATURE",
        "abbey": "SACRED_BUILT_FEATURE",
        "basilica": "SACRED_BUILT_FEATURE",
        # Natural water
        "river": "WATER_FEATURE",
        "sea": "WATER_FEATURE",
        "lake": "WATER_FEATURE",
        "water-open": "WATER_FEATURE",
        "gulf": "WATER_FEATURE",
        "strait": "WATER_FEATURE",
        # Natural land
        "island": "LAND_FEATURE",
        "mountain": "LAND_FEATURE",
        "cape": "LAND_FEATURE",
        "desert": "LAND_FEATURE",
        "valley": "LAND_FEATURE",
        "plain": "LAND_FEATURE",
        "plateau": "LAND_FEATURE",
        # Known low-information
        "unlocated": "UNKNOWN_OR_NEEDS_REVIEW",
        "unlabeled": "UNKNOWN_OR_NEEDS_REVIEW",
        "label": "UNKNOWN_OR_NEEDS_REVIEW",
        "feature": "UNKNOWN_OR_NEEDS_REVIEW",
        "people": "UNKNOWN_OR_NEEDS_REVIEW",
        "unknown": "UNKNOWN_OR_NEEDS_REVIEW",
    }
    if t in exact:
        cid = exact[t]
        return (cid, f"exact:{t}", cid == "UNKNOWN_OR_NEEDS_REVIEW")

    if any(k in t for k in ["settlement", "village", "town", "city"]):
        return ("SETTLEMENT", "heuristic:settlement_keyword", False)
    if any(k in t for k in ["region", "province", "district", "territory"]):
        return ("REGION", "heuristic:admin_keyword", False)
    if any(k in t for k in ["archaeolog", "findspot", "necropolis", "tomb", "cemeter"]):
        return ("ARCHAEOLOGICAL_SITE", "heuristic:archaeology_keyword", False)
    if any(k in t for k in ["road", "station", "bridge", "aqueduct", "harbor", "port", "route"]):
        return ("TRANSPORT_FEATURE", "heuristic:transport_keyword", False)
    if any(k in t for k in ["temple", "sanctuary", "church", "shrine"]):
        return ("SACRED_BUILT_FEATURE", "heuristic:sacred_keyword", False)
    if any(k in t for k in ["fort", "wall", "camp"]):
        return ("DEFENSIVE_BUILT_FEATURE", "heuristic:defensive_keyword", False)
    if any(k in t for k in ["river", "lake", "sea", "gulf", "strait", "water"]):
        return ("WATER_FEATURE", "heuristic:water_keyword", False)
    if any(k in t for k in ["island", "mountain", "cape", "desert", "valley", "plain", "plateau"]):
        return ("LAND_FEATURE", "heuristic:land_keyword", False)
    if any(k in t for k in ["villa", "bath", "monument", "mine", "building"]):
        return ("BUILT_FEATURE", "heuristic:built_keyword", False)

    return ("UNKNOWN_OR_NEEDS_REVIEW", "fallback:unmapped", True)


def load_hierarchy(hierarchy_csv: Path) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    with hierarchy_csv.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["type_id"]] = row
    return out


def resolve_distinction_root(canonical_type_id: str, hierarchy: Dict[str, dict]) -> Tuple[str, str]:
    """
    Return the nearest distinction root for a canonical type.
    """
    seen: Set[str] = set()
    current = canonical_type_id
    while current and current not in seen:
        seen.add(current)
        if current in DISTINCTION_ROOT_TYPE_IDS:
            return (current, hierarchy.get(current, {}).get("type_label", current))
        row = hierarchy.get(current, {})
        current = (row.get("parent_type_id") or "").strip()
    return ("UNKNOWN_OR_NEEDS_REVIEW", hierarchy.get("UNKNOWN_OR_NEEDS_REVIEW", {}).get("type_label", "Unknown or Needs Review"))


def quality_star(
    *,
    token: str,
    row_count: str,
    mapping_rule: str,
    needs_review: bool,
    wikidata_match_qid: str,
    wikidata_geo_score: str,
    geonames_signal_count: str = "0",
    wikidata_geo_pid_count: str = "0",
    wikidata_time_pid_count: str = "0",
    wikidata_periodo_ids: str = "",
    wikidata_start_time_values: str = "",
    wikidata_end_time_values: str = "",
) -> Tuple[str, str, bool]:
    """
    Assign federalization stars for WHERE/WHAT/WHEN readiness.
    """
    if needs_review:
        return ("bronze_star", "unresolved_or_low_confidence", False)

    token_norm = norm(token)
    has_pleiades_signal = int((row_count or "0").strip() or 0) > 0
    has_wikidata_match = bool((wikidata_match_qid or "").strip())
    try:
        has_geonames_signal = int((geonames_signal_count or "0").strip() or 0) > 0
    except ValueError:
        has_geonames_signal = False
    has_periodo_id = bool((wikidata_periodo_ids or "").strip())
    has_start = bool((wikidata_start_time_values or "").strip())
    has_end = bool((wikidata_end_time_values or "").strip())
    has_temporal_indicator = False

    try:
        time_count = int((wikidata_time_pid_count or "0").strip() or 0)
    except ValueError:
        time_count = 0
    if time_count > 0 or has_periodo_id or has_start or has_end:
        has_temporal_indicator = True
    try:
        geo_count = int((wikidata_geo_pid_count or "0").strip() or 0)
    except ValueError:
        geo_count = 0
    has_geographic_signal = geo_count > 0
    is_fully_triangulated = (
        has_wikidata_match
        and has_pleiades_signal
        and has_geonames_signal
        and has_temporal_indicator
        and has_geographic_signal
    )

    # Exception bucket for derived temporal scaffolds.
    if token_norm in STAR_GOLD_EXCEPTION_TOKENS:
        return ("gold_star", "canonical_exception_year_or_derived", False)

    # Fully federalized v2: Wikidata + Pleiades + GeoNames + temporal + geo signal.
    if is_fully_triangulated:
        return ("gold_star", "fully_triangulated_wikidata_pleiades_geonames_temporal_geo", True)

    present_legs = int(has_wikidata_match) + int(has_pleiades_signal) + int(has_geonames_signal)
    missing_legs = 3 - present_legs
    if has_temporal_indicator and has_geographic_signal and missing_legs == 1:
        return ("silver_star", "one_federation_leg_missing_with_geo_time", False)

    if has_wikidata_match:
        try:
            score = int((wikidata_geo_score or "0").strip() or 0)
        except ValueError:
            score = 0
        if score >= 2 or geo_count > 0:
            return ("silver_star", "federated_partial_missing_leg_or_time", False)
        return ("silver_star", "wikidata_identity_without_geo_time", False)

    if mapping_rule.startswith("exact:"):
        return ("silver_star", "canonical_exact_without_wikidata_identity", False)
    if mapping_rule.startswith("heuristic:"):
        return ("silver_star", "canonical_heuristic_without_wikidata_identity", False)
    return ("silver_star", "mapped_without_federal_identity", False)


def build_mapping(
    tokens_csv: Path,
    hierarchy: Dict[str, dict],
    *,
    use_wikidata: bool,
    wikidata_search_limit: int,
    wikidata_cache: Dict[str, Dict[str, str]],
    geonames_signal_by_token: Dict[str, int],
    show_progress: bool,
    progress_every: int,
) -> List[dict]:
    rows: List[dict] = []
    with tokens_csv.open("r", encoding="utf-8") as fh:
        input_rows = list(csv.DictReader(fh))
    total_rows = len(input_rows)
    cache_hits = 0
    live_lookups = 0
    star_counts = {"gold_star": 0, "silver_star": 0, "bronze_star": 0}

    if show_progress:
        print(
            f"[mapping] starting token mapping: total_rows={total_rows}, wikidata={'on' if use_wikidata else 'off'}",
            flush=True,
        )

    for idx, row in enumerate(input_rows, start=1):
            token = row.get("place_type_token", "").strip()
            count = int((row.get("row_count") or "0").strip() or 0)
            cid, rule, needs_review = classify_token(token)
            token_key = norm(token)
            geonames_signal_count = geonames_signal_by_token.get(token_key, 0)

            wd = {
                "wikidata_match_qid": "",
                "wikidata_match_label": "",
                "wikidata_match_description": "",
                "wikidata_type_qids": "",
                "wikidata_type_labels": "",
                "wikidata_geo_score": "0",
                "wikidata_geo_matches": "",
                "wikidata_label_match_strength": "0",
                "wikidata_geo_pids_present": "",
                "wikidata_geo_pid_count": "0",
                "wikidata_time_pids_present": "",
                "wikidata_time_pid_count": "0",
                "wikidata_periodo_ids": "",
                "wikidata_start_time_values": "",
                "wikidata_end_time_values": "",
                "wikidata_inferred_type": "",
                "wikidata_error": "",
            }
            if (
                use_wikidata
                and token_key not in LOW_INFORMATION_TOKENS
                and (needs_review or cid == "UNKNOWN_OR_NEEDS_REVIEW")
            ):
                if token_key in wikidata_cache:
                    wd = wikidata_cache[token_key]
                    cache_hits += 1
                else:
                    live_lookups += 1
                    wd = resolve_token_with_wikidata(token, search_limit=wikidata_search_limit)
                    wikidata_cache[token_key] = wd

                wd_type = wd.get("wikidata_inferred_type", "UNKNOWN_OR_NEEDS_REVIEW")
                try:
                    wd_label_strength = int((wd.get("wikidata_label_match_strength", "0") or "0").strip() or 0)
                except ValueError:
                    wd_label_strength = 0
                try:
                    wd_score = int((wd.get("wikidata_geo_score", "0") or "0").strip() or 0)
                except ValueError:
                    wd_score = 0
                if (
                    wd_type in hierarchy
                    and wd_type != "UNKNOWN_OR_NEEDS_REVIEW"
                    and (wd_label_strength > 0 or wd_score >= 2)
                ):
                    cid = wd_type
                    rule = f"wikidata:{wd.get('wikidata_match_qid', '')}:{wd.get('wikidata_geo_matches', 'score')}"
                    needs_review = False

            label = hierarchy.get(cid, {}).get("type_label", cid)
            distinction_root_id, distinction_root_label = resolve_distinction_root(cid, hierarchy)
            if needs_review:
                if token_key in LOW_INFORMATION_TOKENS:
                    review_bucket = REVIEW_LOW_SIGNAL
                else:
                    review_bucket = REVIEW_REQUIRED
            else:
                review_bucket = REVIEW_AUTO
            star_tier, star_reason, is_fully_triangulated = quality_star(
                token=token,
                row_count=str(count),
                mapping_rule=rule,
                needs_review=needs_review,
                wikidata_match_qid=wd.get("wikidata_match_qid", ""),
                wikidata_geo_score=wd.get("wikidata_geo_score", "0"),
                geonames_signal_count=str(geonames_signal_count),
                wikidata_geo_pid_count=wd.get("wikidata_geo_pid_count", "0"),
                wikidata_time_pid_count=wd.get("wikidata_time_pid_count", "0"),
                wikidata_periodo_ids=wd.get("wikidata_periodo_ids", ""),
                wikidata_start_time_values=wd.get("wikidata_start_time_values", ""),
                wikidata_end_time_values=wd.get("wikidata_end_time_values", ""),
            )
            star_counts[star_tier] = star_counts.get(star_tier, 0) + 1
            rows.append(
                {
                    "place_type_token": token,
                    "row_count": str(count),
                    "geonames_signal_count": str(geonames_signal_count),
                    "geonames_signal_present": "true" if geonames_signal_count > 0 else "false",
                    "canonical_type_id": cid,
                    "canonical_type_label": label,
                    "distinction_root_type_id": distinction_root_id,
                    "distinction_root_type_label": distinction_root_label,
                    "mapping_rule": rule,
                    "needs_review": "true" if needs_review else "false",
                    "review_bucket": review_bucket,
                    "quality_star": star_tier,
                    "quality_star_reason": star_reason,
                    "is_fully_triangulated": "true" if is_fully_triangulated else "false",
                    "wikidata_match_qid": wd.get("wikidata_match_qid", ""),
                    "wikidata_match_label": wd.get("wikidata_match_label", ""),
                    "wikidata_match_description": wd.get("wikidata_match_description", ""),
                    "wikidata_type_qids": wd.get("wikidata_type_qids", ""),
                    "wikidata_type_labels": wd.get("wikidata_type_labels", ""),
                    "wikidata_geo_score": wd.get("wikidata_geo_score", "0"),
                    "wikidata_geo_matches": wd.get("wikidata_geo_matches", ""),
                    "wikidata_label_match_strength": wd.get("wikidata_label_match_strength", "0"),
                    "wikidata_geo_pids_present": wd.get("wikidata_geo_pids_present", ""),
                    "wikidata_geo_pid_count": wd.get("wikidata_geo_pid_count", "0"),
                    "wikidata_time_pids_present": wd.get("wikidata_time_pids_present", ""),
                    "wikidata_time_pid_count": wd.get("wikidata_time_pid_count", "0"),
                    "wikidata_periodo_ids": wd.get("wikidata_periodo_ids", ""),
                    "wikidata_start_time_values": wd.get("wikidata_start_time_values", ""),
                    "wikidata_end_time_values": wd.get("wikidata_end_time_values", ""),
                    "wikidata_error": wd.get("wikidata_error", ""),
                }
            )
            if show_progress and (idx % max(1, progress_every) == 0 or idx == total_rows):
                pct = (idx / total_rows * 100.0) if total_rows else 100.0
                print(
                    (
                        f"[mapping] {idx}/{total_rows} ({pct:.1f}%) "
                        f"| gold={star_counts.get('gold_star', 0)} "
                        f"silver={star_counts.get('silver_star', 0)} "
                        f"bronze={star_counts.get('bronze_star', 0)} "
                        f"| wd_cache_hits={cache_hits} wd_live_lookups={live_lookups}"
                    ),
                    flush=True,
                )
    rows.sort(key=lambda r: (-int(r["row_count"]), r["place_type_token"].lower()))
    return rows


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_json_cache(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}


def save_json_cache(path: Path, data: Dict[str, Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)


def _build_neo4j_statements(
    hierarchy_rows: List[dict],
    mapping_rows: List[dict],
    *,
    mode: str = "full",
) -> List[Tuple[str, dict]]:
    map_rows = [
        {
            "token_norm": norm(r["place_type_token"]),
            "token_raw": r["place_type_token"],
            "canonical_type_id": r["canonical_type_id"],
            "distinction_root_type_id": r["distinction_root_type_id"],
            "mapping_rule": r["mapping_rule"],
            "needs_review": r["needs_review"] == "true",
        }
        for r in mapping_rows
    ]
    geo_semantic_rows = [
        {
            "type_id": "MAN_MADE_STRUCTURE",
            "label": "Man-Made Structure",
            "description": "Human-built structures and infrastructure.",
        },
        {
            "type_id": "PHYSICAL_FEATURE",
            "label": "Physical Feature",
            "description": "Natural land, water, and terrain features.",
        },
        {
            "type_id": "SETTLEMENT_TYPE",
            "label": "Settlement Type",
            "description": "Population-place and administrative settlement units.",
        },
        {
            "type_id": "UNKNOWN_OR_NEEDS_REVIEW",
            "label": "Unknown or Needs Review",
            "description": "Fallback semantic type for unresolved mappings.",
        },
    ]
    place_type_root_map_rows = [
        {
            "place_type_id": r["canonical_type_id"],
            "geo_semantic_type_id": r["distinction_root_type_id"],
        }
        for r in mapping_rows
        if r["canonical_type_id"] and r["distinction_root_type_id"]
    ]
    full_statements = [
        (
            "CREATE CONSTRAINT place_type_id_unique IF NOT EXISTS FOR (pt:PlaceType) REQUIRE pt.type_id IS UNIQUE",
            {},
        ),
        (
            """
            UNWIND $rows AS row
            MERGE (pt:PlaceType {type_id: row.type_id})
            ON CREATE SET pt.created = datetime()
            SET pt.label = row.type_label,
                pt.reference_qid = CASE WHEN row.reference_qid = '' THEN null ELSE row.reference_qid END,
                pt.reference_label = CASE WHEN row.reference_label = '' THEN null ELSE row.reference_label END,
                pt.notes = row.notes,
                pt.updated = datetime()
            """,
            {"rows": hierarchy_rows},
        ),
        (
            """
            UNWIND $rows AS row
            WITH row WHERE row.parent_type_id <> ''
            MATCH (child:PlaceType {type_id: row.type_id})
            MATCH (parent:PlaceType {type_id: row.parent_type_id})
            MERGE (child)-[:SUBCLASS_OF]->(parent)
            """,
            {"rows": hierarchy_rows},
        ),
        (
            """
            UNWIND $rows AS row
            MATCH (pt:PlaceType {type_id: row.canonical_type_id})
            MERGE (m:PlaceTypeTokenMap {token_norm: row.token_norm})
            SET m.token_raw = row.token_raw,
                m.mapping_rule = row.mapping_rule,
                m.needs_review = row.needs_review,
                m.updated = datetime()
            MERGE (m)-[:MAPS_TO]->(pt)
            """,
            {"rows": map_rows},
        ),
        (
            "CREATE CONSTRAINT geo_semantic_type_id_unique IF NOT EXISTS FOR (gst:GeoSemanticType) REQUIRE gst.type_id IS UNIQUE",
            {},
        ),
        (
            """
            UNWIND $rows AS row
            MERGE (gst:GeoSemanticType {type_id: row.type_id})
            ON CREATE SET gst.created = datetime()
            SET gst.label = row.label,
                gst.description = row.description,
                gst.updated = datetime()
            """,
            {"rows": geo_semantic_rows},
        ),
        (
            """
            UNWIND $rows AS row
            MATCH (pt:PlaceType {type_id: row.place_type_id})
            MATCH (gst:GeoSemanticType {type_id: row.geo_semantic_type_id})
            MERGE (pt)-[r:HAS_GEO_SEMANTIC_TYPE]->(gst)
            SET r.updated = datetime()
            """,
            {"rows": place_type_root_map_rows},
        ),
        (
            """
            MATCH (p:Place {authority: 'Pleiades'})
            WHERE p.place_type IS NOT NULL AND trim(p.place_type) <> ''
            WITH p, split(p.place_type, ',') AS toks
            UNWIND toks AS tok
            WITH p, trim(toLower(tok)) AS token_norm, trim(tok) AS token_raw
            WHERE token_norm <> ''
            OPTIONAL MATCH (m:PlaceTypeTokenMap {token_norm: token_norm})-[:MAPS_TO]->(pt:PlaceType)
            WITH p, token_raw, token_norm, coalesce(pt.type_id, 'UNKNOWN_OR_NEEDS_REVIEW') AS type_id
            MATCH (t:PlaceType {type_id: type_id})
            MERGE (p)-[r:INSTANCE_OF_PLACE_TYPE {source: 'pleiades', token_norm: token_norm}]->(t)
                SET r.token_raw = token_raw,
                    r.updated = datetime()
            """,
            {},
        ),
        (
            """
            MATCH (p:Place {authority: 'Pleiades'})-[:INSTANCE_OF_PLACE_TYPE]->(pt:PlaceType)-[:HAS_GEO_SEMANTIC_TYPE]->(gst:GeoSemanticType)
            MERGE (p)-[r:HAS_GEO_SEMANTIC_TYPE {source: 'place_type_hierarchy_v1'}]->(gst)
            SET r.updated = datetime()
            """,
            {},
        ),
        (
            "CREATE CONSTRAINT building_entity_id_unique IF NOT EXISTS FOR (b:Building) REQUIRE b.entity_id IS UNIQUE",
            {},
        ),
        (
            """
            MATCH (p:Place {authority: 'Pleiades'})-[:INSTANCE_OF_PLACE_TYPE]->(:PlaceType)-[:HAS_GEO_SEMANTIC_TYPE]->(gst:GeoSemanticType {type_id:'MAN_MADE_STRUCTURE'})
            WITH DISTINCT p, gst,
                 CASE
                   WHEN p.pleiades_id IS NOT NULL AND trim(toString(p.pleiades_id)) <> '' THEN 'bldg_pleiades_' + toString(p.pleiades_id)
                   WHEN p.qid IS NOT NULL AND trim(toString(p.qid)) <> '' THEN 'bldg_qid_' + toString(p.qid)
                   ELSE 'bldg_place_' + toString(id(p))
                 END AS building_id,
                 CASE WHEN p.min_date =~ '^-?\\d+(\\.\\d+)?$' THEN toInteger(toFloat(p.min_date)) ELSE null END AS start_year,
                 CASE WHEN p.max_date =~ '^-?\\d+(\\.\\d+)?$' THEN toInteger(toFloat(p.max_date)) ELSE null END AS end_year
            MERGE (b:Building {entity_id: building_id})
            ON CREATE SET b.created = datetime()
            SET b.label = coalesce(p.label, b.label),
                b.node_type = 'building_object',
                b.source = 'Pleiades',
                b.source_place_id = p.pleiades_id,
                b.source_place_uri = p.uri,
                b.wikidata_qid = coalesce(p.wikidata_qid, p.qid, b.wikidata_qid),
                b.start_year_hint = start_year,
                b.end_year_hint = end_year,
                b.object_where_cipher_key =
                    'what=Building'
                    + '|where=' + coalesce(toString(p.pleiades_id), coalesce(toString(p.qid), coalesce(toString(p.entity_id), '')))
                    + '|qid=' + coalesce(toString(coalesce(p.wikidata_qid, p.qid)), '')
                    + '|start=' + coalesce(toString(start_year), '')
                    + '|end=' + coalesce(toString(end_year), ''),
                b.is_fully_federated = CASE
                    WHEN p.pleiades_id IS NOT NULL
                      AND trim(toString(p.pleiades_id)) <> ''
                      AND coalesce(toString(p.wikidata_qid), toString(p.qid), '') =~ '^Q\\d+$'
                      AND (start_year IS NOT NULL OR end_year IS NOT NULL)
                    THEN true ELSE false END,
                b.updated = datetime()
            MERGE (b)-[:LOCATED_IN {source:'pleiades_place'}]->(p)
            MERGE (b)-[:HAS_GEO_SEMANTIC_TYPE {source:'place_type_hierarchy_v1'}]->(gst)
            """,
            {},
        ),
        (
            """
            MATCH (b:Building)
            OPTIONAL MATCH (ot:ObjectType {type_id:'BUILT_STRUCTURE'})
            WITH b, ot WHERE ot IS NOT NULL
            MERGE (b)-[:INSTANCE_OF_OBJECT_TYPE {source:'geo_semantic_extension'}]->(ot)
            """,
            {},
        ),
        (
            """
            MATCH (b:Building)
            WITH b, b.start_year_hint AS sy, b.end_year_hint AS ey
            OPTIONAL MATCH (ys:Year {year: sy})
            OPTIONAL MATCH (ye:Year {year: ey})
            FOREACH (_ IN CASE WHEN ys IS NULL THEN [] ELSE [1] END |
                MERGE (b)-[:STARTS_IN_YEAR {source:'pleiades'}]->(ys))
            FOREACH (_ IN CASE WHEN ye IS NULL THEN [] ELSE [1] END |
                MERGE (b)-[:ENDS_IN_YEAR {source:'pleiades'}]->(ye))
            """,
            {},
        ),
    ]
    if mode == "core":
        # Core mode seeds/updates PlaceType and mapping policy only.
        return full_statements[:7]
    return full_statements


def _http_commit_url(uri: str, database: str = "neo4j") -> str:
    parsed = urllib.parse.urlparse(uri)
    scheme = parsed.scheme.lower()
    host = parsed.hostname or "localhost"
    db = (database or "neo4j").strip() or "neo4j"
    if scheme in {"bolt", "neo4j", "neo4j+s", "neo4j+ssc"}:
        return f"http://{host}:7474/db/{db}/tx/commit"
    if scheme in {"http", "https"}:
        path = parsed.path.rstrip("/")
        if path.endswith("/tx/commit") and "/db/" in path:
            return uri
        if "/db/" in path:
            return f"{uri.rstrip('/')}/tx/commit"
        return f"{uri.rstrip('/')}/db/{db}/tx/commit"
    return f"http://{host}:7474/db/{db}/tx/commit"


def _run_neo4j_http_statement(
    *,
    commit_url: str,
    user: str,
    password: str,
    statement: str,
    parameters: dict,
    timeout_seconds: int = 120,
    max_retries: int = 3,
) -> None:
    payload = {"statements": [{"statement": statement, "parameters": parameters}]}
    auth = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    req = urllib.request.Request(
        commit_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}",
        },
        method="POST",
    )
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=max(10, timeout_seconds)) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            errors = body.get("errors", [])
            if errors:
                msg = "; ".join([f"{e.get('code')}: {e.get('message')}" for e in errors])
                raise RuntimeError(f"Neo4j HTTP error: {msg}")
            return
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                delay = min(10, attempt * 2)
                print(
                    f"Neo4j HTTP statement retry {attempt}/{max_retries} after error: {exc}. "
                    f"Sleeping {delay}s...",
                    flush=True,
                )
                time.sleep(delay)
                continue
            raise
    if last_exc:
        raise last_exc


def load_to_neo4j(
    *,
    uri: str,
    user: str,
    password: str,
    database: str,
    hierarchy_rows: List[dict],
    mapping_rows: List[dict],
    force_http: bool = False,
    http_timeout_seconds: int = 120,
    http_max_retries: int = 3,
    neo4j_mode: str = "full",
) -> None:
    statements = _build_neo4j_statements(hierarchy_rows, mapping_rows, mode=neo4j_mode)
    if not force_http:
        try:
            # Keep driver path first for compatibility with existing environments.
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(uri, auth=(user, password))
            try:
                with driver.session(database=database) as session:
                    for statement, parameters in statements:
                        session.run(statement, **parameters)
                return
            finally:
                driver.close()
        except Exception as exc:
            print(f"Neo4j Python driver unavailable, falling back to HTTP endpoint: {exc}")
    else:
        print("Neo4j load using HTTP mode (--force-http).")

    commit_url = _http_commit_url(uri, database=database)
    for statement, parameters in statements:
        _run_neo4j_http_statement(
            commit_url=commit_url,
            user=user,
            password=password,
            statement=statement,
            parameters=parameters,
            timeout_seconds=http_timeout_seconds,
            max_retries=http_max_retries,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and optionally load place-type hierarchy mapping.")
    parser.add_argument(
        "--tokens-csv",
        default="Geographic/pleiades_place_type_distinct_tokens_2026-02-18.csv",
        help="Distinct Pleiades place-type token frequency CSV",
    )
    parser.add_argument(
        "--hierarchy-csv",
        default="CSV/geographic/place_type_hierarchy_v1.csv",
        help="Canonical place-type hierarchy CSV",
    )
    parser.add_argument(
        "--out-mapping-csv",
        default="CSV/geographic/pleiades_place_type_token_mapping_v1.csv",
        help="Output token mapping CSV",
    )
    parser.add_argument(
        "--out-review-csv",
        default="CSV/geographic/pleiades_place_type_token_mapping_review_v1.csv",
        help="Output subset needing review",
    )
    parser.add_argument(
        "--no-wikidata",
        action="store_true",
        help="Disable Wikidata term lookup enrichment.",
    )
    parser.add_argument(
        "--wikidata-search-limit",
        type=int,
        default=5,
        help="Maximum Wikidata search candidates per token.",
    )
    parser.add_argument(
        "--wikidata-min-interval-seconds",
        type=float,
        default=0.8,
        help="Minimum delay between Wikidata API requests (seconds).",
    )
    parser.add_argument(
        "--wikidata-max-retries",
        type=int,
        default=6,
        help="Maximum retry attempts per Wikidata API request.",
    )
    parser.add_argument(
        "--wikidata-cache-json",
        default="CSV/geographic/pleiades_place_type_wikidata_cache_v1.json",
        help="JSON cache for Wikidata token lookups.",
    )
    parser.add_argument(
        "--geonames-summary-csv",
        default="CSV/geographic/pleiades_geonames_place_summary_v1.csv",
        help="Pleiades->GeoNames place summary CSV used to derive token-level GeoNames signal.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable live progress output to terminal.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=25,
        help="Emit progress update every N token rows.",
    )
    parser.add_argument("--load-neo4j", action="store_true", help="Load hierarchy and mapping into Neo4j")
    parser.add_argument(
        "--force-http",
        action="store_true",
        help="Force Neo4j HTTP transaction endpoint mode (skip Python neo4j driver import).",
    )
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="Chrystallum", help="Neo4j password")
    parser.add_argument(
        "--database",
        default="neo4j",
        help="Neo4j database name (e.g., neo4j, training).",
    )
    parser.add_argument(
        "--neo4j-mode",
        choices=["core", "full"],
        default="core",
        help="Neo4j write scope for --load-neo4j (`core` = policy/type seed only, `full` = includes Place/Building derivations).",
    )
    parser.add_argument(
        "--http-timeout-seconds",
        type=int,
        default=300,
        help="HTTP transaction timeout seconds for --force-http mode.",
    )
    parser.add_argument(
        "--http-max-retries",
        type=int,
        default=3,
        help="HTTP transaction retry count for --force-http mode.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    tokens_csv = (project_root / args.tokens_csv).resolve()
    hierarchy_csv = (project_root / args.hierarchy_csv).resolve()
    out_mapping_csv = (project_root / args.out_mapping_csv).resolve()
    out_review_csv = (project_root / args.out_review_csv).resolve()
    wikidata_cache_json = (project_root / args.wikidata_cache_json).resolve()
    geonames_summary_csv = (project_root / args.geonames_summary_csv).resolve()

    if not tokens_csv.exists():
        print(f"ERROR: tokens CSV not found: {tokens_csv}")
        return 1
    if not hierarchy_csv.exists():
        print(f"ERROR: hierarchy CSV not found: {hierarchy_csv}")
        return 1

    global WIKIDATA_MIN_INTERVAL_SECONDS
    global WIKIDATA_MAX_RETRIES
    WIKIDATA_MIN_INTERVAL_SECONDS = max(0.0, args.wikidata_min_interval_seconds)
    WIKIDATA_MAX_RETRIES = max(1, args.wikidata_max_retries)

    hierarchy = load_hierarchy(hierarchy_csv)
    wikidata_cache = load_json_cache(wikidata_cache_json)
    geonames_signal_by_token = load_geonames_signal_by_token(geonames_summary_csv)
    if geonames_signal_by_token:
        print(
            f"GeoNames token signal loaded: {len(geonames_signal_by_token)} tokens "
            f"(source={geonames_summary_csv})",
            flush=True,
        )
    else:
        print(
            f"GeoNames token signal unavailable or empty: {geonames_summary_csv} "
            "(triangulated gold will be strict and likely sparse)",
            flush=True,
        )
    mapping_rows = build_mapping(
        tokens_csv,
        hierarchy,
        use_wikidata=not args.no_wikidata,
        wikidata_search_limit=max(1, args.wikidata_search_limit),
        wikidata_cache=wikidata_cache,
        geonames_signal_by_token=geonames_signal_by_token,
        show_progress=not args.no_progress,
        progress_every=max(1, args.progress_every),
    )
    if not args.no_wikidata:
        save_json_cache(wikidata_cache_json, wikidata_cache)
    review_rows = [r for r in mapping_rows if r["review_bucket"] == REVIEW_REQUIRED]
    low_signal_rows = [r for r in mapping_rows if r["review_bucket"] == REVIEW_LOW_SIGNAL]

    fieldnames = [
        "place_type_token",
        "row_count",
        "geonames_signal_count",
        "geonames_signal_present",
        "canonical_type_id",
        "canonical_type_label",
        "distinction_root_type_id",
        "distinction_root_type_label",
        "mapping_rule",
        "needs_review",
        "review_bucket",
        "quality_star",
        "quality_star_reason",
        "is_fully_triangulated",
        "wikidata_match_qid",
        "wikidata_match_label",
        "wikidata_match_description",
        "wikidata_type_qids",
        "wikidata_type_labels",
        "wikidata_geo_score",
        "wikidata_geo_matches",
        "wikidata_label_match_strength",
        "wikidata_geo_pids_present",
        "wikidata_geo_pid_count",
        "wikidata_time_pids_present",
        "wikidata_time_pid_count",
        "wikidata_periodo_ids",
        "wikidata_start_time_values",
        "wikidata_end_time_values",
        "wikidata_error",
    ]
    write_csv(
        out_mapping_csv,
        mapping_rows,
        fieldnames,
    )
    write_csv(
        out_review_csv,
        review_rows,
        fieldnames,
    )

    print("Place-type mapping built.")
    print(f"  Hierarchy: {hierarchy_csv}")
    print(f"  Tokens: {tokens_csv}")
    print(f"  Mapping: {out_mapping_csv}")
    print(f"  Review subset: {out_review_csv}")
    if args.no_wikidata:
        print("  Wikidata enrichment: disabled")
    else:
        print(f"  Wikidata enrichment: enabled (cache={wikidata_cache_json})")
        print(f"  Wikidata throttle: min_interval={WIKIDATA_MIN_INTERVAL_SECONDS:.2f}s, max_retries={WIKIDATA_MAX_RETRIES}")
    print(f"  Total tokens mapped: {len(mapping_rows)}")
    print(f"  Needs review (actionable): {len(review_rows)}")
    print(f"  Low-signal unresolved (excluded from review): {len(low_signal_rows)}")
    triangulated_count = sum(1 for r in mapping_rows if r.get("is_fully_triangulated") == "true")
    geonames_signal_count = sum(1 for r in mapping_rows if r.get("geonames_signal_present") == "true")
    print(f"  GeoNames signal tokens: {geonames_signal_count}")
    print(f"  Fully triangulated rows: {triangulated_count}")

    if args.load_neo4j:
        with hierarchy_csv.open("r", encoding="utf-8") as fh:
            hierarchy_rows = list(csv.DictReader(fh))
        load_to_neo4j(
            uri=args.uri,
            user=args.user,
            password=args.password,
            database=args.database,
            hierarchy_rows=hierarchy_rows,
            mapping_rows=mapping_rows,
            force_http=args.force_http,
            http_timeout_seconds=max(10, args.http_timeout_seconds),
            http_max_retries=max(1, args.http_max_retries),
            neo4j_mode=args.neo4j_mode,
        )
        print("Neo4j load complete.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
