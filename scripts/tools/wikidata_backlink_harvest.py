#!/usr/bin/env python3
"""Harvest and gate Wikidata backlinks for a seed QID.

This script performs controlled reverse-triple discovery:
- fetch inbound triples (?source ?prop ?target),
- filter source classes against Chrystallum schema classes (P31/P279),
- profile datatype/value_type on accepted source nodes,
- enforce stop-condition thresholds,
- emit a run report with accepted/rejected reasons.

Examples:
  python scripts/tools/wikidata_backlink_harvest.py --seed-qid Q1048

  python scripts/tools/wikidata_backlink_harvest.py ^
    --seed-qid Q1048 ^
    --property P710 --property P1441 --property P138 ^
    --max-sources-per-seed 120 ^
    --max-new-nodes-per-seed 60
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import requests


SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1BacklinkHarvester/1.0 (local tooling)"
QID_RE = re.compile(r"Q\d+$", re.IGNORECASE)
PID_RE = re.compile(r"P\d+$", re.IGNORECASE)

DEFAULT_PROPERTY_ALLOWLIST = ["P710", "P1441", "P138", "P112", "P737", "P828"]

# Wikidata administrative metadata — strip during harvest; not domain data.
PROPERTY_DENYLIST = frozenset(
    ["P6104", "P5008", "P6216"]  # maintained by WikiProject, focus list, copyright status
)

# P31 (instance of) values to reject — not domain entities.
DEFAULT_P31_DENYLIST = frozenset(
    ["Q4167836"]  # Wikimedia category — Wikipedia's filing system, not domain entities
)

DISCOVERY_PROPERTY_BOOTSTRAP = [
    # Core semantic links used in current production profile.
    "P710",
    "P1441",
    "P138",
    "P112",
    "P737",
    "P828",
    # Structural/hierarchy and contextual expansion signals.
    "P31",
    "P279",
    "P361",
    "P527",
    "P131",
    "P17",
    "P39",
    "P106",
    "P921",
    "P101",
    "P2578",
    "P2579",
]

MODE_DEFAULTS: Dict[str, Dict[str, int]] = {
    "production": {
        "sparql_limit": 500,
        "max_sources_per_seed": 200,
        "max_new_nodes_per_seed": 100,
    },
    "discovery": {
        "sparql_limit": 2000,
        "max_sources_per_seed": 1000,
        "max_new_nodes_per_seed": 1500,
    },
}

# Supported pair routing contract aligned with datatype ingestion spec.
SUPPORTED_DATATYPE_VALUE_PAIRS: Set[Tuple[str, str]] = {
    ("wikibase-item", "wikibase-entityid"),
    ("wikibase-property", "wikibase-entityid"),
    ("wikibase-lexeme", "wikibase-entityid"),
    ("wikibase-form", "wikibase-entityid"),
    ("wikibase-sense", "wikibase-entityid"),
    ("time", "time"),
    ("external-id", "string"),
    ("quantity", "quantity"),
    ("monolingualtext", "monolingualtext"),
    ("string", "string"),
    ("commonsMedia", "string"),
    ("globe-coordinate", "globecoordinate"),
    ("globecoordinate", "globecoordinate"),
    ("url", "string"),
}

EDGE_PAIRS: Set[Tuple[str, str]] = {
    ("wikibase-item", "wikibase-entityid"),
    ("wikibase-property", "wikibase-entityid"),
    ("wikibase-lexeme", "wikibase-entityid"),
    ("wikibase-form", "wikibase-entityid"),
    ("wikibase-sense", "wikibase-entityid"),
}
FEDERATION_PAIRS: Set[Tuple[str, str]] = {("external-id", "string")}
TEMPORAL_PAIRS: Set[Tuple[str, str]] = {("time", "time")}
LITERAL_TEXT_PAIRS: Set[Tuple[str, str]] = {
    ("string", "string"),
    ("monolingualtext", "monolingualtext"),
    ("url", "string"),
}
MEASURED_PAIRS: Set[Tuple[str, str]] = {("quantity", "quantity")}
GEO_PAIRS: Set[Tuple[str, str]] = {
    ("globe-coordinate", "globecoordinate"),
    ("globecoordinate", "globecoordinate"),
}
MEDIA_PAIRS: Set[Tuple[str, str]] = {("commonsMedia", "string")}

LITERAL_HEAVY_ROUTES: Set[str] = {
    "node_property",
    "measured_attribute",
    "geo_attribute",
    "media_reference",
    "temporal_uncertain",
}


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("+-").isdigit():
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_qid(value: str) -> str:
    value = (value or "").strip().upper()
    if QID_RE.fullmatch(value):
        return value
    raise ValueError(f"Invalid QID: {value}")


def _normalize_pid(value: str) -> str:
    value = (value or "").strip().upper()
    if PID_RE.fullmatch(value):
        return value
    raise ValueError(f"Invalid property ID: {value}")


def _wd_uri_to_id(uri: str) -> str:
    if not uri:
        return ""
    tail = uri.rsplit("/", 1)[-1].strip().upper()
    if QID_RE.fullmatch(tail) or PID_RE.fullmatch(tail):
        return tail
    return ""


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _query_sparql(query: str, timeout_s: int) -> List[Dict[str, str]]:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": USER_AGENT,
    }
    resp = requests.get(
        SPARQL_URL,
        params={"query": query},
        headers=headers,
        timeout=timeout_s,
    )
    resp.raise_for_status()
    payload = resp.json()
    out: List[Dict[str, str]] = []
    for row in payload.get("results", {}).get("bindings", []):
        parsed: Dict[str, str] = {}
        for key, val in row.items():
            parsed[key] = val.get("value", "")
        out.append(parsed)
    return out


def _load_schema_allowlists(schema_path: Path) -> Tuple[Set[str], Set[str]]:
    data = json.loads(schema_path.read_text(encoding="utf-8"))

    classes: Set[str] = set()
    for row in (data.get("entities", {}) or {}).get("types", []) or []:
        qid = (row.get("wikidata_qid") or "").strip().upper()
        if QID_RE.fullmatch(qid):
            classes.add(qid)

    properties: Set[str] = set()
    for row in (data.get("relationships", {}) or {}).get("types", []) or []:
        pid = (row.get("wikidata_property") or "").strip().upper()
        if PID_RE.fullmatch(pid):
            properties.add(pid)

    return classes, properties


def _load_entity_category_map(schema_path: Path) -> Dict[str, str]:
    """Load wikidata_qid -> category from schema entity types."""
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    out: Dict[str, str] = {}
    for row in (data.get("entities", {}) or {}).get("types", []) or []:
        qid = (row.get("wikidata_qid") or "").strip().upper()
        category = (row.get("category") or "").strip()
        if QID_RE.fullmatch(qid) and category:
            out[qid] = category
    return out


def _load_category_to_scoping_class(schema_path: Path) -> Dict[str, str]:
    """Load category -> scoping_class from entity_scoping (temporal vs conceptual)."""
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    esc = (data.get("entity_scoping") or {}).get("category_to_scoping_class") or {}
    return dict(esc)


def _load_anchor_to_property_allowlist(schema_path: Path) -> Dict[str, List[str]]:
    """Load anchor QID -> property allowlist from entity_scoping. Skips non-QID keys (e.g. description)."""
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    raw = (data.get("entity_scoping") or {}).get("anchor_to_property_allowlist") or {}
    out = {}
    for k, v in raw.items():
        if k == "description" or not QID_RE.fullmatch(k):
            continue
        if isinstance(v, list):
            out[k] = [_normalize_pid(p) for p in v if PID_RE.fullmatch(str(p))]
    return out


def _resolve_runtime_settings(
    *,
    mode: str,
    property_args: Optional[List[str]],
    use_schema_relationship_properties: bool,
    schema_property_allowlist: Set[str],
    class_allowlist: Set[str],
    class_allowlist_mode: str,
    sparql_limit: Optional[int],
    max_sources_per_seed: Optional[int],
    max_new_nodes_per_seed: Optional[int],
) -> Dict[str, Any]:
    if mode not in MODE_DEFAULTS:
        raise ValueError(f"Unsupported mode: {mode}")

    defaults = MODE_DEFAULTS[mode]
    resolved_sparql_limit = max(1, sparql_limit or defaults["sparql_limit"])
    resolved_max_sources = max(1, max_sources_per_seed or defaults["max_sources_per_seed"])
    resolved_max_new_nodes = max(1, max_new_nodes_per_seed or defaults["max_new_nodes_per_seed"])

    if property_args:
        property_allowlist = [_normalize_pid(p) for p in property_args]
    elif mode == "discovery":
        property_allowlist = [_normalize_pid(p) for p in DISCOVERY_PROPERTY_BOOTSTRAP]
    else:
        property_allowlist = [_normalize_pid(p) for p in DEFAULT_PROPERTY_ALLOWLIST]

    if mode == "discovery":
        # Discovery mode always expands property surface using schema mappings.
        property_allowlist = sorted(
            set(property_allowlist) | schema_property_allowlist,
            key=lambda x: int(x[1:]),
        )
    elif use_schema_relationship_properties:
        property_allowlist = sorted(
            set(property_allowlist) | schema_property_allowlist,
            key=lambda x: int(x[1:]),
        )
    else:
        property_allowlist = sorted(set(property_allowlist), key=lambda x: int(x[1:]))

    if class_allowlist_mode == "auto":
        effective_class_allowlist_mode = "disabled" if mode == "discovery" else "schema"
    else:
        effective_class_allowlist_mode = class_allowlist_mode

    class_allowlist_enabled = effective_class_allowlist_mode == "schema"
    effective_class_allowlist = class_allowlist if class_allowlist_enabled else set()

    # Strip Wikidata administrative metadata (P6104, P5008, P6216 — not domain data)
    property_allowlist = [p for p in property_allowlist if p not in PROPERTY_DENYLIST]

    return {
        "sparql_limit": resolved_sparql_limit,
        "max_sources_per_seed": resolved_max_sources,
        "max_new_nodes_per_seed": resolved_max_new_nodes,
        "property_allowlist": property_allowlist,
        "class_allowlist_mode": effective_class_allowlist_mode,
        "class_allowlist_enabled": class_allowlist_enabled,
        "class_allowlist": effective_class_allowlist,
    }


def _fetch_backlink_rows(
    seed_qid: str,
    property_allowlist: List[str],
    limit: int,
    timeout_s: int,
) -> List[Dict[str, str]]:
    prop_values = " ".join(f"wdt:{p}" for p in property_allowlist)
    query = f"""
SELECT ?source ?sourceLabel ?prop ?p31 ?p31Label WHERE {{
  BIND(wd:{seed_qid} AS ?target)
  VALUES ?prop {{ {prop_values} }}
  ?source ?prop ?target .
  OPTIONAL {{ ?source wdt:P31 ?p31 . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {max(1, limit)}
"""
    return _query_sparql(query, timeout_s=timeout_s)


def _build_candidates(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    candidates: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        source_qid = _wd_uri_to_id(row.get("source", ""))
        if not QID_RE.fullmatch(source_qid):
            continue
        prop_pid = _wd_uri_to_id(row.get("prop", ""))
        p31_qid = _wd_uri_to_id(row.get("p31", ""))
        source_label = (row.get("sourceLabel") or "").strip()
        p31_label = (row.get("p31Label") or "").strip()

        entry = candidates.setdefault(
            source_qid,
            {
                "qid": source_qid,
                "label": source_label,
                "properties": set(),
                "p31": set(),
                "p31_labels": {},
                "backlink_hits": 0,
            },
        )

        entry["backlink_hits"] += 1
        if source_label and not entry["label"]:
            entry["label"] = source_label
        if PID_RE.fullmatch(prop_pid):
            entry["properties"].add(prop_pid)
        if QID_RE.fullmatch(p31_qid):
            entry["p31"].add(p31_qid)
            if p31_label:
                entry["p31_labels"][p31_qid] = p31_label
    return candidates


def _limit_candidates(
    candidates: Dict[str, Dict[str, Any]],
    max_sources: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ordered = sorted(
        candidates.values(),
        key=lambda x: (-x["backlink_hits"], -len(x["properties"]), x["qid"]),
    )
    kept = ordered[:max_sources]
    dropped = ordered[max_sources:]
    return kept, dropped


def _fetch_p279_ancestors(
    class_qids: List[str],
    max_hops: int,
    timeout_s: int,
    batch_size: int = 120,
    sleep_ms: int = 50,
) -> Dict[str, Set[str]]:
    if not class_qids:
        return {}

    max_hops = max(0, max_hops)
    out: Dict[str, Set[str]] = {qid: {qid} for qid in class_qids}
    frontier: Dict[str, Set[str]] = {qid: {qid} for qid in class_qids}

    for _ in range(max_hops):
        all_frontier_nodes = sorted({node for nodes in frontier.values() for node in nodes})
        if not all_frontier_nodes:
            break

        parent_map: Dict[str, Set[str]] = defaultdict(set)
        for batch in _chunks(all_frontier_nodes, max(1, batch_size)):
            values = " ".join(f"wd:{qid}" for qid in batch)
            query = f"""
SELECT ?child ?parent WHERE {{
  VALUES ?child {{ {values} }}
  ?child wdt:P279 ?parent .
}}
"""
            rows = _query_sparql(query, timeout_s=timeout_s)
            for row in rows:
                child = _wd_uri_to_id(row.get("child", ""))
                parent = _wd_uri_to_id(row.get("parent", ""))
                if QID_RE.fullmatch(child) and QID_RE.fullmatch(parent):
                    parent_map[child].add(parent)
            if sleep_ms > 0:
                time.sleep(sleep_ms / 1000.0)

        next_frontier: Dict[str, Set[str]] = {qid: set() for qid in class_qids}
        for origin in class_qids:
            for node in frontier.get(origin, set()):
                for parent in parent_map.get(node, set()):
                    if parent not in out[origin]:
                        out[origin].add(parent)
                        next_frontier[origin].add(parent)
        frontier = next_frontier

    return out


def _classify_candidates(
    candidates: List[Dict[str, Any]],
    class_allowlist: Set[str],
    ancestors_map: Dict[str, Set[str]],
    p31_denylist: Set[str],
    class_allowlist_enabled: bool,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Counter[str]]:
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    reasons: Counter[str] = Counter()

    for row in candidates:
        p31_list = sorted(row["p31"])
        if not p31_list:
            reasons["no_p31"] += 1
            rejected.append(
                {
                    "qid": row["qid"],
                    "label": row["label"],
                    "reason": "no_p31",
                    "properties": sorted(row["properties"]),
                    "p31": [],
                    "backlink_hits": row["backlink_hits"],
                }
            )
            continue

        deny_hits = sorted(set(p31_list) & p31_denylist)
        if deny_hits:
            reasons["p31_denylisted"] += 1
            rejected.append(
                {
                    "qid": row["qid"],
                    "label": row["label"],
                    "reason": "p31_denylisted",
                    "properties": sorted(row["properties"]),
                    "p31": p31_list,
                    "p31_deny_hits": deny_hits,
                    "backlink_hits": row["backlink_hits"],
                }
            )
            continue

        if not class_allowlist_enabled:
            accepted.append(
                {
                    "qid": row["qid"],
                    "label": row["label"],
                    "properties": sorted(row["properties"]),
                    "p31": p31_list,
                    "matched_classes": p31_list,
                    "matched_allowlist_ancestors": [],
                    "backlink_hits": row["backlink_hits"],
                }
            )
            continue

        matched_classes: Set[str] = set()
        matched_allowlist_ancestors: Set[str] = set()

        for c in p31_list:
            if c in class_allowlist:
                matched_classes.add(c)
                matched_allowlist_ancestors.add(c)
                continue
            for anc in ancestors_map.get(c, set()):
                if anc in class_allowlist:
                    matched_classes.add(c)
                    matched_allowlist_ancestors.add(anc)
                    break

        if not matched_classes:
            reasons["class_not_allowed"] += 1
            rejected.append(
                {
                    "qid": row["qid"],
                    "label": row["label"],
                    "reason": "class_not_allowed",
                    "properties": sorted(row["properties"]),
                    "p31": p31_list,
                    "backlink_hits": row["backlink_hits"],
                }
            )
            continue

        accepted.append(
            {
                "qid": row["qid"],
                "label": row["label"],
                "properties": sorted(row["properties"]),
                "p31": p31_list,
                "matched_classes": sorted(matched_classes),
                "matched_allowlist_ancestors": sorted(matched_allowlist_ancestors),
                "backlink_hits": row["backlink_hits"],
            }
        )

    return accepted, rejected, reasons


def _fetch_entities_claims(
    qids: List[str],
    timeout_s: int,
    batch_size: int = 40,
    sleep_ms: int = 100,
) -> Dict[str, Dict[str, Any]]:
    headers = {"User-Agent": USER_AGENT}
    out: Dict[str, Dict[str, Any]] = {}
    for batch in _chunks(qids, max(1, batch_size)):
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": "|".join(batch),
            "languages": "en",
            "props": "labels|claims",
        }
        resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=timeout_s)
        resp.raise_for_status()
        payload = resp.json()
        for qid, entity in (payload.get("entities") or {}).items():
            if QID_RE.fullmatch(qid) and isinstance(entity, dict) and "missing" not in entity:
                out[qid] = entity
        if sleep_ms > 0:
            time.sleep(sleep_ms / 1000.0)
    return out


# Rank precedence for external ID extraction: prefer "preferred" over "normal" over "deprecated".
_RANK_ORDER: Dict[str, int] = {"preferred": 0, "normal": 1, "deprecated": 2}

# Federation-aware scoping (HARVESTER_SCOPING_DESIGN.md)
FEDERATION_ANCIENT_WORLD_IDS: Set[str] = {"P1696", "P1047", "P1584"}  # Trismegistos, LGPN, Pleiades (D-023: P1047 not P1838)
VIAF_PID = "P214"


# DPRR (P6863): domain-specific authority for Republican persons; membership implies temporal scoping
DPRR_PID = "P6863"


def _compute_federation_scoping(
    external_ids: Dict[str, str],
    has_domain_proximity: bool = True,
    scoping_class: Optional[str] = None,
    has_dprr: bool = False,
) -> Tuple[str, float]:
    """Compute scoping status and confidence from federation external IDs.

    Returns (scoping_status, confidence). All accepted entities have domain proximity
    (backlink to seed) by definition.

    HARVESTER_SCOPING_DESIGN: Conceptual entities (Organization, Place, etc.) get
    domain_scoped when has_domain_proximity, even without federation IDs.

    DPRR (P6863 or has_dprr): Digital Prosopography of the Roman Republic — persons
    attested in DPRR are by definition temporally scoped to the Roman Republic.
    """
    ext = external_ids or {}
    if any(ext.get(pid) for pid in FEDERATION_ANCIENT_WORLD_IDS):
        return "temporal_scoped", 0.95
    if has_dprr or ext.get(DPRR_PID):
        return "temporal_scoped", 0.85
    if ext.get(VIAF_PID) and has_domain_proximity:
        return "domain_scoped", 0.85
    # Conceptual entities: domain proximity alone suffices (HARVESTER_SCOPING_DESIGN)
    if scoping_class == "conceptual" and has_domain_proximity:
        return "domain_scoped", 0.85
    return "unscoped", 0.40


def _extract_external_ids(entity: Dict[str, Any]) -> Dict[str, str]:
    """Extract all external-id typed property values from a raw wbgetentities entity.

    Returns a dict mapping PID -> best-rank value string.  One value per property;
    when multiple statements exist for the same property the highest-rank statement
    wins (preferred > normal > deprecated).  Deprecated-only values are included
    rather than silently dropped so downstream consumers can decide.

    This captures every federation identifier Wikidata holds for the entity
    (VIAF P214, BnF P268, Pleiades P1584, Trismegistos P1696, LGPN P1047,
    BAV P1017, etc.) without callers needing to know which PIDs exist.
    """
    out: Dict[str, str] = {}
    for pid, statements in (entity.get("claims") or {}).items():
        best_value: Optional[str] = None
        best_rank: int = 99
        for stmt in statements or []:
            mainsnak = stmt.get("mainsnak") or {}
            if mainsnak.get("datatype") != "external-id":
                continue
            rank = _RANK_ORDER.get(stmt.get("rank", "normal"), 1)
            datavalue = mainsnak.get("datavalue") or {}
            value = datavalue.get("value") if isinstance(datavalue, dict) else None
            if isinstance(value, str) and value.strip() and rank < best_rank:
                best_value = value.strip()
                best_rank = rank
        if best_value is not None:
            out[pid] = best_value
    return out


def _dispatch_statement(
    statement: Dict[str, Any],
    min_temporal_precision: int,
) -> Dict[str, Any]:
    mainsnak = statement.get("mainsnak", {}) or {}
    datatype = (mainsnak.get("datatype") or "").strip()
    datavalue = mainsnak.get("datavalue") or {}
    value_type = (datavalue.get("type") or "").strip() if isinstance(datavalue, dict) else ""
    pair = (datatype, value_type)
    pair_key = f"{datatype}|{value_type}"

    out: Dict[str, Any] = {
        "datatype": datatype,
        "value_type": value_type,
        "pair": pair,
        "pair_key": pair_key,
        "route": "",
        "quarantine_reason": "",
        "time_precision": None,
        "has_qualifiers": bool(statement.get("qualifiers", {})),
        "has_references": bool(statement.get("references", [])),
        "rank": (statement.get("rank") or "").strip(),
    }

    if not value_type:
        out["route"] = "quarantine_missing_datavalue"
        out["quarantine_reason"] = "missing_datavalue"
        return out

    if pair in EDGE_PAIRS:
        out["route"] = "edge_candidate"
        return out
    if pair in FEDERATION_PAIRS:
        out["route"] = "federation_id"
        return out
    if pair in TEMPORAL_PAIRS:
        val = datavalue.get("value") if isinstance(datavalue, dict) else {}
        precision = _as_int((val or {}).get("precision") if isinstance(val, dict) else None)
        out["time_precision"] = precision
        if precision is None or precision < min_temporal_precision:
            out["route"] = "temporal_uncertain"
        else:
            out["route"] = "temporal_anchor"
        return out
    if pair in LITERAL_TEXT_PAIRS:
        out["route"] = "node_property"
        return out
    if pair in MEASURED_PAIRS:
        out["route"] = "measured_attribute"
        return out
    if pair in GEO_PAIRS:
        out["route"] = "geo_attribute"
        return out
    if pair in MEDIA_PAIRS:
        out["route"] = "media_reference"
        return out

    # Known pair contract mismatch or unsupported statement shape.
    if pair in SUPPORTED_DATATYPE_VALUE_PAIRS:
        out["route"] = "node_property"
        return out

    out["route"] = "quarantine_unsupported_pair"
    out["quarantine_reason"] = "unsupported_pair"
    return out


def _profile_dispatch_routes(
    entities: Dict[str, Dict[str, Any]],
    min_temporal_precision: int,
    literal_heavy_threshold: float,
) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    pair_counts: Counter[Tuple[str, str]] = Counter()
    datatype_counts: Counter[str] = Counter()
    value_type_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    quarantine_reasons: Counter[str] = Counter()
    rank_counts: Counter[str] = Counter()

    total_statements = 0
    with_qualifiers = 0
    with_references = 0
    missing_datavalue_statement_count = 0

    per_entity: Dict[str, Dict[str, Any]] = {}

    for qid, entity in entities.items():
        claims = entity.get("claims", {}) or {}
        label = ((entity.get("labels") or {}).get("en") or {}).get("value", "")

        entity_pairs: Counter[Tuple[str, str]] = Counter()
        entity_routes: Counter[str] = Counter()
        entity_quarantine: Counter[str] = Counter()
        entity_rank_counts: Counter[str] = Counter()
        entity_statement_count = 0
        entity_with_qualifiers = 0
        entity_with_references = 0
        entity_missing_datavalue = 0

        for statements in claims.values():
            for statement in statements or []:
                route = _dispatch_statement(
                    statement=statement,
                    min_temporal_precision=min_temporal_precision,
                )

                pair = route["pair"]
                pair_counts[pair] += 1
                entity_pairs[pair] += 1
                datatype_counts[route["datatype"]] += 1
                value_type_counts[route["value_type"]] += 1
                route_counts[route["route"]] += 1
                entity_routes[route["route"]] += 1

                rank = route["rank"]
                rank_counts[rank] += 1
                entity_rank_counts[rank] += 1

                if route["has_qualifiers"]:
                    with_qualifiers += 1
                    entity_with_qualifiers += 1
                if route["has_references"]:
                    with_references += 1
                    entity_with_references += 1
                if route["route"] == "quarantine_missing_datavalue":
                    missing_datavalue_statement_count += 1
                    entity_missing_datavalue += 1
                if route["route"].startswith("quarantine_"):
                    quarantine_reasons[route["quarantine_reason"]] += 1
                    entity_quarantine[route["quarantine_reason"]] += 1

                total_statements += 1
                entity_statement_count += 1

        unsupported_pairs = {
            f"{k[0]}|{k[1]}": v
            for k, v in entity_pairs.items()
            if k[1] and k not in SUPPORTED_DATATYPE_VALUE_PAIRS
        }
        unsupported_count = sum(unsupported_pairs.values())
        entity_supported_denominator = max(0, entity_statement_count - entity_missing_datavalue)
        unsupported_pair_rate = (
            unsupported_count / entity_supported_denominator if entity_supported_denominator else 0.0
        )

        literal_heavy_count = sum(entity_routes.get(r, 0) for r in LITERAL_HEAVY_ROUTES)
        literal_heavy_ratio = (
            literal_heavy_count / entity_statement_count if entity_statement_count else 0.0
        )
        edge_candidate_count = entity_routes.get("edge_candidate", 0)
        frontier_eligible = True
        frontier_exclusion_reason = ""
        if edge_candidate_count == 0:
            frontier_eligible = False
            frontier_exclusion_reason = "no_edge_candidates"
        elif literal_heavy_ratio > literal_heavy_threshold:
            frontier_eligible = False
            frontier_exclusion_reason = "literal_heavy"

        per_entity[qid] = {
            "label": label,
            "statement_count": entity_statement_count,
            "with_qualifiers": entity_with_qualifiers,
            "with_references": entity_with_references,
            "qualifier_rate": (
                entity_with_qualifiers / entity_statement_count if entity_statement_count else 0.0
            ),
            "reference_rate": (
                entity_with_references / entity_statement_count if entity_statement_count else 0.0
            ),
            "route_counts": dict(entity_routes),
            "rank_counts": dict(entity_rank_counts),
            "unsupported_statement_count": unsupported_count,
            "unsupported_pair_rate": unsupported_pair_rate,
            "unsupported_pairs": unsupported_pairs,
            "literal_heavy_ratio": literal_heavy_ratio,
            "edge_candidate_count": edge_candidate_count,
            "frontier_eligible": frontier_eligible,
            "frontier_exclusion_reason": frontier_exclusion_reason,
            "quarantine_reasons": dict(entity_quarantine),
        }

    unsupported_pairs_global = {
        f"{k[0]}|{k[1]}": v
        for k, v in pair_counts.items()
        if k[1] and k not in SUPPORTED_DATATYPE_VALUE_PAIRS
    }
    unsupported_statement_count = sum(unsupported_pairs_global.values())
    supported_statement_denominator = max(0, total_statements - missing_datavalue_statement_count)

    frontier_eligible_count = sum(1 for p in per_entity.values() if p.get("frontier_eligible"))
    frontier_excluded_count = len(per_entity) - frontier_eligible_count

    summary = {
        "statement_count": total_statements,
        "missing_datavalue_statement_count": missing_datavalue_statement_count,
        "with_qualifiers": with_qualifiers,
        "with_references": with_references,
        "qualifier_rate": (with_qualifiers / total_statements) if total_statements else 0.0,
        "reference_rate": (with_references / total_statements) if total_statements else 0.0,
        "datatype_counts": dict(datatype_counts),
        "value_type_counts": dict(value_type_counts),
        "pair_counts": {f"{k[0]}|{k[1]}": v for k, v in pair_counts.items()},
        "route_counts": dict(route_counts),
        "rank_counts": dict(rank_counts),
        "quarantine_reasons": dict(quarantine_reasons),
        "unsupported_pairs": unsupported_pairs_global,
        "unsupported_statement_count": unsupported_statement_count,
        "unsupported_pair_rate": (
            unsupported_statement_count / supported_statement_denominator
            if supported_statement_denominator
            else 0.0
        ),
        "frontier_eligible_count": frontier_eligible_count,
        "frontier_excluded_count": frontier_excluded_count,
        "literal_heavy_threshold": literal_heavy_threshold,
        "min_temporal_precision": min_temporal_precision,
    }
    return summary, per_entity


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-qid", required=True, help="Seed item QID (example: Q1048).")
    parser.add_argument(
        "--mode",
        choices=["production", "discovery"],
        default="production",
        help="Run mode. discovery expands budgets and property surface for hierarchy learning.",
    )
    parser.add_argument(
        "--schema",
        default="JSON/chrystallum_schema.json",
        help="Path to schema JSON containing entity Wikidata QIDs.",
    )
    parser.add_argument(
        "--output-dir",
        default="JSON/wikidata/backlinks",
        help="Output directory for backlink harvest report.",
    )
    parser.add_argument(
        "--property",
        action="append",
        help="Property allowlist PID (repeatable). Default uses curated federation set.",
    )
    parser.add_argument(
        "--use-schema-relationship-properties",
        action="store_true",
        help="Union schema relationship P-values into property allowlist.",
    )
    parser.add_argument(
        "--class-allowlist-mode",
        choices=["auto", "schema", "disabled"],
        default="auto",
        help="Class gate mode. auto=disabled in discovery, schema in production.",
    )
    parser.add_argument(
        "--p31-denylist-qid",
        action="append",
        help="Reject candidates if any P31 matches this QID (repeatable).",
    )
    parser.add_argument("--max-depth", type=int, default=1, help="Backlink traversal depth (currently only 1 supported).")
    parser.add_argument(
        "--sparql-limit",
        type=int,
        default=None,
        help="Row limit for reverse-triple SPARQL query. Mode defaults: production=500, discovery=2000.",
    )
    parser.add_argument(
        "--max-sources-per-seed",
        type=int,
        default=None,
        help="Budget cap for candidate source nodes. Mode defaults: production=200, discovery=1000.",
    )
    parser.add_argument(
        "--max-new-nodes-per-seed",
        type=int,
        default=None,
        help="Budget cap for accepted source nodes. Mode defaults: production=100, discovery=1500.",
    )
    parser.add_argument(
        "--unresolved-class-threshold",
        type=float,
        default=0.20,
        help="Abort gate if unresolved class mapping rate exceeds this value.",
    )
    parser.add_argument(
        "--unsupported-pair-threshold",
        type=float,
        default=0.10,
        help="Abort gate if unsupported datatype/value_type rate exceeds this value.",
    )
    parser.add_argument(
        "--min-temporal-precision",
        type=int,
        default=9,
        help="Minimum Wikidata time precision treated as precise temporal anchor (year=9, month=10, day=11).",
    )
    parser.add_argument(
        "--literal-heavy-threshold",
        type=float,
        default=0.80,
        help="Exclude from traversal frontier when literal-heavy ratio exceeds this threshold.",
    )
    parser.add_argument(
        "--max-p279-hops",
        type=int,
        default=4,
        help="Max P279 hops for class ancestor matching.",
    )
    parser.add_argument("--timeout-s", type=int, default=45, help="HTTP timeout (seconds).")
    parser.add_argument("--sleep-ms", type=int, default=100, help="Delay between batches (milliseconds).")
    parser.add_argument("--batch-size", type=int, default=40, help="Batch size for entity API requests.")
    parser.add_argument(
        "--report-path",
        help="Optional explicit output file path. Default: <output-dir>/<seed>_backlink_harvest_report.json",
    )
    args = parser.parse_args()

    seed_qid = _normalize_qid(args.seed_qid)
    if args.max_depth != 1:
        raise ValueError("Only --max-depth 1 is currently supported.")

    schema_path = Path(args.schema)
    if not schema_path.exists():
        raise FileNotFoundError(schema_path)

    class_allowlist, schema_property_allowlist = _load_schema_allowlists(schema_path)
    entity_category_map = _load_entity_category_map(schema_path)
    category_to_scoping_class = _load_category_to_scoping_class(schema_path)
    anchor_to_property_allowlist = _load_anchor_to_property_allowlist(schema_path)
    resolved = _resolve_runtime_settings(
        mode=args.mode,
        property_args=args.property,
        use_schema_relationship_properties=args.use_schema_relationship_properties,
        schema_property_allowlist=schema_property_allowlist,
        class_allowlist=class_allowlist,
        class_allowlist_mode=args.class_allowlist_mode,
        sparql_limit=args.sparql_limit,
        max_sources_per_seed=args.max_sources_per_seed,
        max_new_nodes_per_seed=args.max_new_nodes_per_seed,
    )
    property_allowlist = resolved["property_allowlist"]
    # Override with anchor-specific allowlist when harvesting a known anchor (reduces noise)
    if seed_qid in anchor_to_property_allowlist and anchor_to_property_allowlist[seed_qid]:
        property_allowlist = anchor_to_property_allowlist[seed_qid]
        print(f"allowlist_override: {seed_qid} -> {property_allowlist}")
    class_allowlist_mode = resolved["class_allowlist_mode"]
    class_allowlist_enabled = resolved["class_allowlist_enabled"]
    effective_class_allowlist = resolved["class_allowlist"]
    sparql_limit = resolved["sparql_limit"]
    max_sources_per_seed = resolved["max_sources_per_seed"]
    max_new_nodes_per_seed = resolved["max_new_nodes_per_seed"]

    if not property_allowlist:
        raise RuntimeError("Property allowlist is empty.")
    if class_allowlist_enabled and not effective_class_allowlist:
        raise RuntimeError("Class allowlist is empty.")
    p31_denylist = set(DEFAULT_P31_DENYLIST)
    for raw_qid in args.p31_denylist_qid or []:
        p31_denylist.add(_normalize_qid(raw_qid))

    raw_rows = _fetch_backlink_rows(
        seed_qid=seed_qid,
        property_allowlist=property_allowlist,
        limit=sparql_limit,
        timeout_s=args.timeout_s,
    )
    candidate_map = _build_candidates(raw_rows)
    kept_candidates, dropped_by_source_budget = _limit_candidates(
        candidate_map,
        max_sources=max_sources_per_seed,
    )

    p31_classes: Set[str] = set()
    for row in kept_candidates:
        p31_classes.update(row["p31"])
    ancestors_map = _fetch_p279_ancestors(
        class_qids=sorted(p31_classes),
        max_hops=max(0, args.max_p279_hops),
        timeout_s=args.timeout_s,
        sleep_ms=max(0, args.sleep_ms),
    )

    accepted, rejected, rejection_counts = _classify_candidates(
        candidates=kept_candidates,
        class_allowlist=effective_class_allowlist,
        ancestors_map=ancestors_map,
        p31_denylist=p31_denylist,
        class_allowlist_enabled=class_allowlist_enabled,
    )

    accepted = sorted(accepted, key=lambda x: (-x["backlink_hits"], -len(x["properties"]), x["qid"]))
    accepted_limited = accepted[:max_new_nodes_per_seed]
    accepted_dropped_by_node_budget = accepted[max_new_nodes_per_seed:]

    # Add explicit budget rejection rows for transparency.
    for row in dropped_by_source_budget:
        rejection_counts["source_budget_exceeded"] += 1
        rejected.append(
            {
                "qid": row["qid"],
                "label": row["label"],
                "reason": "source_budget_exceeded",
                "properties": sorted(row["properties"]),
                "p31": sorted(row["p31"]),
                "backlink_hits": row["backlink_hits"],
            }
        )
    for row in accepted_dropped_by_node_budget:
        rejection_counts["node_budget_exceeded"] += 1
        rejected.append(
            {
                "qid": row["qid"],
                "label": row["label"],
                "reason": "node_budget_exceeded",
                "properties": sorted(row["properties"]),
                "p31": row["p31"],
                "backlink_hits": row["backlink_hits"],
            }
        )

    unresolved_count = rejection_counts.get("no_p31", 0) + rejection_counts.get("class_not_allowed", 0)
    unresolved_rate = (unresolved_count / len(kept_candidates)) if kept_candidates else 0.0

    accepted_qids = [row["qid"] for row in accepted_limited]
    entity_map = _fetch_entities_claims(
        qids=accepted_qids,
        timeout_s=args.timeout_s,
        batch_size=max(1, args.batch_size),
        sleep_ms=max(0, args.sleep_ms),
    ) if accepted_qids else {}

    datatype_summary, per_entity_profile = _profile_dispatch_routes(
        entities=entity_map,
        min_temporal_precision=max(0, args.min_temporal_precision),
        literal_heavy_threshold=max(0.0, args.literal_heavy_threshold),
    )
    unsupported_rate = datatype_summary.get("unsupported_pair_rate", 0.0)

    unresolved_gate_passed = unresolved_rate <= args.unresolved_class_threshold
    datatype_gate_passed = unsupported_rate <= args.unsupported_pair_threshold
    overall_status = "pass" if unresolved_gate_passed and datatype_gate_passed else "blocked_by_policy"

    # Attach per-entity profile, external IDs, and federation scoping to accepted list.
    accepted_with_profile: List[Dict[str, Any]] = []
    scoping_counts: Counter[str] = Counter()
    ambiguous_category_count = 0
    for row in accepted_limited:
        qid = row["qid"]
        prof = per_entity_profile.get(qid, {})
        entity_raw = entity_map.get(qid, {})
        merged = dict(row)
        ext_ids = _extract_external_ids(entity_raw)
        merged["external_ids"] = ext_ids
        # Resolve category and scoping_class for domain proximity gate (HARVESTER_SCOPING_DESIGN)
        p31_and_ancestors: Set[str] = set()
        for p31 in row.get("p31", []):
            p31_and_ancestors.add(p31)
            p31_and_ancestors.update(ancestors_map.get(p31, set()))
        has_known_category = any(q in entity_category_map for q in p31_and_ancestors)
        entity_category: Optional[str] = None
        scoping_class: Optional[str] = None
        if has_known_category:
            for q in p31_and_ancestors:
                if q in entity_category_map:
                    entity_category = entity_category_map[q]
                    scoping_class = category_to_scoping_class.get(entity_category)
                    break
        if not has_known_category:
            merged["ambiguous_category"] = True
            scoping_status = "unscoped"
            scoping_confidence = 0.40
            ambiguous_category_count += 1
        else:
            merged["ambiguous_category"] = False
            scoping_status, scoping_confidence = _compute_federation_scoping(
                ext_ids, has_domain_proximity=True, scoping_class=scoping_class
            )
        merged["scoping_status"] = scoping_status
        merged["scoping_confidence"] = scoping_confidence
        scoping_counts[scoping_status] += 1
        merged["statement_profile"] = {
            "statement_count": prof.get("statement_count", 0),
            "with_qualifiers": prof.get("with_qualifiers", 0),
            "with_references": prof.get("with_references", 0),
            "qualifier_rate": prof.get("qualifier_rate", 0.0),
            "reference_rate": prof.get("reference_rate", 0.0),
            "route_counts": prof.get("route_counts", {}),
            "unsupported_statement_count": prof.get("unsupported_statement_count", 0),
            "unsupported_pair_rate": prof.get("unsupported_pair_rate", 0.0),
            "unsupported_pairs": prof.get("unsupported_pairs", {}),
            "literal_heavy_ratio": prof.get("literal_heavy_ratio", 0.0),
            "edge_candidate_count": prof.get("edge_candidate_count", 0),
            "frontier_eligible": prof.get("frontier_eligible", False),
            "frontier_exclusion_reason": prof.get("frontier_exclusion_reason", ""),
            "quarantine_reasons": prof.get("quarantine_reasons", {}),
        }
        accepted_with_profile.append(merged)

    report = {
        "generated_at": _now_utc(),
        "seed_qid": seed_qid,
        "config": {
            "mode": args.mode,
            "schema_path": str(schema_path),
            "output_dir": str(args.output_dir),
            "max_depth": args.max_depth,
            "sparql_limit": sparql_limit,
            "max_sources_per_seed": max_sources_per_seed,
            "max_new_nodes_per_seed": max_new_nodes_per_seed,
            "unresolved_class_threshold": args.unresolved_class_threshold,
            "unsupported_pair_threshold": args.unsupported_pair_threshold,
            "min_temporal_precision": args.min_temporal_precision,
            "literal_heavy_threshold": args.literal_heavy_threshold,
            "max_p279_hops": args.max_p279_hops,
            "timeout_s": args.timeout_s,
            "sleep_ms": args.sleep_ms,
            "batch_size": args.batch_size,
        },
        "allowlists": {
            "properties": property_allowlist,
            "property_count": len(property_allowlist),
            "class_allowlist_mode": class_allowlist_mode,
            "classes_count": len(effective_class_allowlist),
            "p31_denylist": sorted(p31_denylist),
        },
        "counts": {
            "backlink_rows": len(raw_rows),
            "candidate_sources_before_budget": len(candidate_map),
            "candidate_sources_considered": len(kept_candidates),
            "accepted_before_node_budget": len(accepted),
            "accepted": len(accepted_limited),
            "rejected": len(rejected),
            "entities_profiled": len(entity_map),
            "frontier_eligible": datatype_summary.get("frontier_eligible_count", 0),
            "frontier_excluded": datatype_summary.get("frontier_excluded_count", 0),
        },
        "gates": {
            "unresolved_class_rate": unresolved_rate,
            "unresolved_class_gate_passed": unresolved_gate_passed,
            "unsupported_pair_rate": unsupported_rate,
            "datatype_gate_passed": datatype_gate_passed,
            "overall_status": overall_status,
        },
        "rejection_reasons": dict(rejection_counts),
        "scoping": {
            "temporal_scoped": scoping_counts.get("temporal_scoped", 0),
            "domain_scoped": scoping_counts.get("domain_scoped", 0),
            "unscoped": scoping_counts.get("unscoped", 0),
            "ambiguous_category_count": ambiguous_category_count,
        },
        "datatype_profile_summary": datatype_summary,
        "accepted": accepted_with_profile,
        "rejected": rejected,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.report_path:
        report_path = Path(args.report_path)
    else:
        report_path = output_dir / f"{seed_qid}_backlink_harvest_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"seed={seed_qid}")
    print(f"backlink_rows={len(raw_rows)}")
    print(f"candidates_considered={len(kept_candidates)}")
    print(f"accepted={len(accepted_limited)}")
    print(
        f"scoping: temporal_scoped={scoping_counts.get('temporal_scoped', 0)} "
        f"domain_scoped={scoping_counts.get('domain_scoped', 0)} "
        f"unscoped={scoping_counts.get('unscoped', 0)} "
        f"ambiguous_category={ambiguous_category_count}"
    )
    print(
        "frontier_eligible="
        f"{datatype_summary.get('frontier_eligible_count', 0)} "
        f"frontier_excluded={datatype_summary.get('frontier_excluded_count', 0)}"
    )
    print(f"rejected={len(rejected)}")
    print(f"unresolved_class_rate={unresolved_rate:.4f} gate_pass={unresolved_gate_passed}")
    print(f"unsupported_pair_rate={unsupported_rate:.4f} gate_pass={datatype_gate_passed}")
    print(f"overall_status={overall_status}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
