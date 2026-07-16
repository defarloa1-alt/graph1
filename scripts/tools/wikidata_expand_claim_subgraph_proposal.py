#!/usr/bin/env python3
"""Expand a claim subgraph proposal with full Wikidata statements on a frontier.

v2 expansion (Roman Republic pilot):
- Full statements for seed P793 events (from seed index)
- Full statements for top battle backlinks (P710 + instance of battle)
- Second-hop fetch for human participants (P710) and key biographic predicates
- Drops collapsed v1 backlink stubs for expanded nodes; filters scholarly-noise (P921)

Usage:
  python scripts/tools/wikidata_expand_claim_subgraph_proposal.py --seed-qid Q17167
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.tools.wikidata_fetch_all_statements import build_statement_payload
from scripts.tools.wikidata_label_utils import (
    apply_labels_to_proposal,
    is_bare_qid_label,
    resolve_labels,
)
from scripts.tools.wikidata_generate_claim_subgraph_proposal import (
    _collect_reference_properties,
    _load_property_catalog,
    _load_registry_property_map,
    _safe_claim_id,
    _score_claim,
    _top_counter_items,
    write_markdown,
)

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1ClaimExpand/1.0 (local tooling)"
QID_RE = re.compile(r"^Q\d+$", re.IGNORECASE)
PID_RE = re.compile(r"^P\d+$", re.IGNORECASE)

BATTLE_INSTANCE_QID = "Q178561"
HUMAN_INSTANCE_QID = "Q5"

BLOCKED_INSTANCE_QIDS = frozenset(
    {
        "Q11424",  # film
        "Q7889",  # video game
        "Q4167410",  # disambiguation
        "Q4167836",  # Wikimedia category
        "Q13406463",  # Wikimedia list
        "Q571",  # book
        "Q7725634",  # literary work
        "Q1002697",  # periodical
        "Q602446",  # podcast episode
    }
)

# Low-value properties on expanded nodes (images, external ids, cataloging)
SKIP_PROPERTIES = frozenset(
    {
        "P18",
        "P373",
        "P646",
        "P244",
        "P214",
        "P227",
        "P269",
        "P268",
        "P950",
        "P1417",
        "P1296",
        "P1566",
        "P1667",
        "P3417",
        "P691",
        "P949",
        "P1015",
        "P1695",
        "P906",
        "P5587",
        "P4342",
        "P3222",
        "P5019",
        "P902",
        "P1438",
        "P1343",
        "P921",  # main subject (scholarly works about Rome)
        "P1424",  # topic has template
        "P2347",  # YSO ID
        "P8189",  # NLI J9U ID
        "P3219",  # Encyclopædia Universalis ID
        "P5008",  # Wikimedia project focus list
        "P13591",  # IDRIM ID
        "P12800",  # VIAF cluster ID
        "P508",  # BNCF Thesaurus ID
        "P2581",  # BabelNet ID
    }
)

# Predicates kept on second-hop person shells
HOP2_ALLOW_PROPERTIES = frozenset(
    {
        "P31",
        "P39",
        "P569",
        "P570",
        "P22",
        "P40",
        "P26",
        "P106",
        "P27",
        "P793",
        "P607",
        "P710",
        "P1344",
        "P585",
        "P580",
        "P582",
        "P734",
        "P735",
        "P1449",
        "P1559",
        "P19",
        "P20",
        "P463",
        "P54",
        "P166",
        "P1412",
    }
)

HOP2_LINK_PROPERTIES = frozenset({"P710", "P1344", "P607"})

# Qualifier object roles on participation statements (commanders, etc.)
HOP2_QUALIFIER_PROPERTIES = frozenset({"P4791", "P3831"})

TEMPORAL_PROPERTIES = frozenset({"P571", "P570", "P580", "P582", "P585", "P156", "P155"})


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_qid(value: str) -> str:
    qid = (value or "").strip().upper()
    if not QID_RE.fullmatch(qid):
        raise ValueError(f"Invalid QID: {value}")
    return qid


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _fetch_entities_batch(
    qids: List[str],
    *,
    timeout_s: int = 45,
    batch_size: int = 40,
    pause_s: float = 0.35,
) -> Dict[str, Dict[str, Any]]:
    headers = {"User-Agent": USER_AGENT}
    out: Dict[str, Dict[str, Any]] = {}
    unique = sorted({q.upper() for q in qids if QID_RE.fullmatch((q or "").upper())})
    for batch in _chunks(unique, max(1, batch_size)):
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": "|".join(batch),
            "languages": "en",
            "props": "labels|descriptions|claims",
        }
        resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=timeout_s)
        if resp.status_code == 429:
            time.sleep(2.0)
            resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=timeout_s)
        resp.raise_for_status()
        payload = resp.json()
        for qid, entity in (payload.get("entities") or {}).items():
            if not QID_RE.fullmatch(qid) or "missing" in (entity or {}):
                continue
            out[qid] = build_statement_payload(entity, qid)
        time.sleep(pause_s)
    return out


def _fetch_p31_map(qids: List[str]) -> Dict[str, List[str]]:
    """Lightweight P31 lookup for filtering."""
    headers = {"User-Agent": USER_AGENT}
    out: Dict[str, List[str]] = {}
    unique = sorted({q.upper() for q in qids if QID_RE.fullmatch((q or "").upper())})
    for batch in _chunks(unique, 50):
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": "|".join(batch),
            "props": "claims",
        }
        resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=45)
        if resp.status_code == 429:
            time.sleep(2.0)
            resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=45)
        resp.raise_for_status()
        payload = resp.json()
        for qid, entity in (payload.get("entities") or {}).items():
            if not QID_RE.fullmatch(qid):
                continue
            claims = (entity or {}).get("claims", {})
            p31_vals: List[str] = []
            for claim in claims.get("P31", []) or []:
                mainsnak = claim.get("mainsnak", {}) or {}
                dv = mainsnak.get("datavalue", {}) or {}
                val = dv.get("value", {}) or {}
                nid = val.get("numeric-id")
                if isinstance(nid, int):
                    p31_vals.append(f"Q{nid}")
            out[qid] = p31_vals
        time.sleep(0.25)
    return out


def _battle_score(row: Dict[str, Any]) -> Tuple[int, int, int]:
    profile = row.get("statement_profile", {}) or {}
    return (
        int(row.get("backlink_hits") or 0),
        int(profile.get("with_references") or 0),
        int(profile.get("with_qualifiers") or 0),
    )


def select_frontier(
    *,
    seed_index: Dict[str, Any],
    backlink_report: Dict[str, Any],
    max_battles: int,
) -> Dict[str, str]:
    """Return qid -> frontier role."""
    frontier: Dict[str, str] = {}
    for ev in seed_index.get("events", []) or []:
        qid = (ev.get("qid") or "").strip().upper()
        if QID_RE.fullmatch(qid):
            frontier[qid] = "event"
    battles: List[Dict[str, Any]] = []
    for src in backlink_report.get("accepted", []) or []:
        qid = (src.get("qid") or "").strip().upper()
        if not QID_RE.fullmatch(qid):
            continue
        props = {p.upper() for p in (src.get("properties") or []) if PID_RE.fullmatch((p or "").upper())}
        p31 = {p.upper() for p in (src.get("p31") or []) if QID_RE.fullmatch((p or "").upper())}
        if BATTLE_INSTANCE_QID in p31 and "P710" in props:
            battles.append(src)
    battles.sort(key=_battle_score, reverse=True)
    for src in battles[:max_battles]:
        qid = (src.get("qid") or "").strip().upper()
        frontier[qid] = "battle"
    return frontier


def _statement_to_claims(
    *,
    payload: Dict[str, Any],
    source_mode: str,
    registry_map: Dict[str, List[str]],
    property_catalog: Dict[str, Dict[str, str]],
    allow_properties: Optional[Set[str]] = None,
    skip_properties: Optional[Set[str]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Set[str]]:
    subject_qid = payload.get("qid", "")
    subject_label = payload.get("label") or subject_qid
    rel_claims: List[Dict[str, Any]] = []
    attr_claims: List[Dict[str, Any]] = []
    linked_qids: Set[str] = set()

    skip = skip_properties or SKIP_PROPERTIES
    for pid, statement_list in (payload.get("claims") or {}).items():
        pid = (pid or "").strip().upper()
        if not PID_RE.fullmatch(pid):
            continue
        if pid in skip:
            continue
        if allow_properties is not None and pid not in allow_properties:
            continue

        pred_meta = property_catalog.get(pid, {})
        pred_label = pred_meta.get("label") or pid
        canonical_rels = registry_map.get(pid, [])

        for stmt in statement_list or []:
            mainsnak = stmt.get("mainsnak", {}) or {}
            datatype = mainsnak.get("datatype", "")
            value_type = mainsnak.get("value_type", "")
            value = mainsnak.get("value")
            rank = (stmt.get("rank") or "").strip()
            qualifiers = stmt.get("qualifiers", {}) or {}
            qualifier_count = sum(len(v) for v in qualifiers.values())
            qualifier_properties = sorted((qualifiers or {}).keys())
            references = stmt.get("references", []) or []
            reference_count = len(references)
            reference_properties = _collect_reference_properties(references)
            statement_id = stmt.get("statement_id", "")

            if (
                value_type == "wikibase-entityid"
                and isinstance(value, str)
                and QID_RE.fullmatch(value)
            ):
                object_qid = value.upper()
                linked_qids.add(object_qid)
                rel_claims.append(
                    {
                        "claim_id": _safe_claim_id(subject_qid, statement_id or f"{pid}_{object_qid}"),
                        "source_mode": source_mode,
                        "source_system": "wikidata",
                        "subject_qid": subject_qid,
                        "subject_label": subject_label,
                        "predicate_pid": pid,
                        "predicate_label": pred_label,
                        "canonical_relationship_types": canonical_rels,
                        "object_qid": object_qid,
                        "object_label": "",
                        "rank": rank,
                        "statement_id": statement_id,
                        "qualifier_count": qualifier_count,
                        "qualifier_properties": qualifier_properties,
                        "qualifiers": qualifiers if qualifier_count else {},
                        "reference_count": reference_count,
                        "reference_properties": reference_properties,
                        "confidence": _score_claim(
                            source_mode="direct" if source_mode == "direct" else "backlink",
                            reference_count=reference_count,
                            qualifier_count=qualifier_count,
                            rank=rank,
                        ),
                    }
                )
            else:
                attr_claims.append(
                    {
                        "claim_id": _safe_claim_id(subject_qid, statement_id or pid),
                        "source_mode": source_mode,
                        "source_system": "wikidata",
                        "subject_qid": subject_qid,
                        "subject_label": subject_label,
                        "predicate_pid": pid,
                        "predicate_label": pred_label,
                        "datatype": datatype,
                        "value_type": value_type,
                        "value": value,
                        "rank": rank,
                        "statement_id": statement_id,
                        "qualifier_count": qualifier_count,
                        "qualifier_properties": qualifier_properties,
                        "qualifiers": qualifiers if qualifier_count else {},
                        "reference_count": reference_count,
                        "reference_properties": reference_properties,
                        "confidence": _score_claim(
                            source_mode="direct",
                            reference_count=reference_count,
                            qualifier_count=qualifier_count,
                            rank=rank,
                        ),
                    }
                )
    return rel_claims, attr_claims, linked_qids


def _collect_linked_qids(payload: Dict[str, Any]) -> Set[str]:
    candidates: Set[str] = set()
    claims = payload.get("claims") or {}
    for pid in HOP2_LINK_PROPERTIES:
        for stmt in claims.get(pid, []) or []:
            mainsnak = stmt.get("mainsnak", {}) or {}
            value = mainsnak.get("value")
            if isinstance(value, str) and QID_RE.fullmatch(value):
                candidates.add(value.upper())
            for qual_prop, qual_list in (stmt.get("qualifiers") or {}).items():
                if qual_prop not in HOP2_QUALIFIER_PROPERTIES:
                    continue
                for qual in qual_list or []:
                    qv = qual.get("value")
                    if isinstance(qv, str) and QID_RE.fullmatch(qv):
                        candidates.add(qv.upper())
    return candidates


def _extract_hop2_person_qids(
    frontier_payloads: Dict[str, Dict[str, Any]],
    *,
    max_persons: int,
) -> List[str]:
    candidates: Set[str] = set()
    for payload in frontier_payloads.values():
        candidates.update(_collect_linked_qids(payload))
    return sorted(candidates)[: max(max_persons * 3, max_persons)]


def _is_blocked_instance(p31_list: List[str]) -> bool:
    return bool(set(p31_list) & BLOCKED_INSTANCE_QIDS)


def _parse_time_year(value: Any) -> Optional[int]:
    if not isinstance(value, dict):
        return None
    raw = value.get("time")
    if not isinstance(raw, str) or len(raw) < 5:
        return None
    sign = -1 if raw.startswith("-") else 1
    digits = raw.lstrip("-")[:4]
    if not digits.isdigit():
        return None
    return sign * int(digits)


def _build_timeline_entries(
    rel_claims: List[Dict[str, Any]],
    attr_claims: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    def _add(entry: Dict[str, Any]) -> None:
        key = entry.get("entry_id", "")
        if key and key not in seen:
            seen.add(key)
            entries.append(entry)

    for row in attr_claims:
        pid = row.get("predicate_pid", "")
        if pid not in TEMPORAL_PROPERTIES:
            continue
        year = _parse_time_year(row.get("value"))
        if year is None:
            continue
        _add(
            {
                "entry_id": row.get("claim_id", ""),
                "subject_qid": row.get("subject_qid"),
                "subject_label": row.get("subject_label"),
                "predicate_pid": pid,
                "year": year,
                "statement_id": row.get("statement_id", ""),
                "source_mode": row.get("source_mode"),
            }
        )

    for row in rel_claims:
        for qprop in ("P580", "P582", "P585"):
            for qual in (row.get("qualifiers") or {}).get(qprop, []) or []:
                year = _parse_time_year(qual.get("value"))
                if year is None:
                    continue
                _add(
                    {
                        "entry_id": f"{row.get('claim_id')}_{qprop}_{year}",
                        "subject_qid": row.get("subject_qid"),
                        "subject_label": row.get("subject_label"),
                        "predicate_pid": qprop,
                        "year": year,
                        "related_object_qid": row.get("object_qid"),
                        "related_object_label": row.get("object_label"),
                        "statement_id": row.get("statement_id", ""),
                        "source_mode": row.get("source_mode"),
                    }
                )

    return sorted(entries, key=lambda e: (e.get("year", 0), e.get("subject_qid", "")))


def build_expanded_proposal(
    *,
    seed_qid: str,
    statements_payload: Dict[str, Any],
    seed_index: Dict[str, Any],
    backlink_report: Dict[str, Any],
    registry_map: Dict[str, List[str]],
    property_catalog: Dict[str, Dict[str, str]],
    max_battles: int,
    max_persons: int,
    fetch_labels: bool,
    cache_dir: Optional[Path],
) -> Dict[str, Any]:
    seed_label = statements_payload.get("label", "") or seed_qid
    seed_description = statements_payload.get("description", "")

    frontier_roles = select_frontier(
        seed_index=seed_index,
        backlink_report=backlink_report,
        max_battles=max_battles,
    )
    frontier_qids = sorted(frontier_roles.keys())

    # Fetch frontier statements (reuse cache when present)
    frontier_payloads: Dict[str, Dict[str, Any]] = {}
    missing_frontier: List[str] = []
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        for qid in frontier_qids:
            cache_path = cache_dir / f"{qid}_statements_full.json"
            if cache_path.exists():
                frontier_payloads[qid] = json.loads(cache_path.read_text(encoding="utf-8"))
            else:
                missing_frontier.append(qid)
    else:
        missing_frontier = list(frontier_qids)
    if missing_frontier:
        frontier_payloads.update(_fetch_entities_batch(missing_frontier))
    if cache_dir:
        for qid, payload in frontier_payloads.items():
            cache_path = cache_dir / f"{qid}_statements_full.json"
            if not cache_path.exists():
                cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    hop2_qids = _extract_hop2_person_qids(frontier_payloads, max_persons=max_persons)
    p31_map = _fetch_p31_map(hop2_qids)
    hop2_humans = [
        q
        for q in hop2_qids
        if HUMAN_INSTANCE_QID in (p31_map.get(q) or [])
        and not _is_blocked_instance(p31_map.get(q) or [])
    ][:max_persons]
    hop2_payloads = _fetch_entities_batch(hop2_humans)
    if cache_dir:
        for qid, payload in hop2_payloads.items():
            cache_path = cache_dir / f"{qid}_statements_full.json"
            if not cache_path.exists():
                cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    direct_rel, direct_attr, _ = _statement_to_claims(
        payload=statements_payload,
        source_mode="direct",
        registry_map=registry_map,
        property_catalog=property_catalog,
        allow_properties=None,
        skip_properties=SKIP_PROPERTIES - {"P921"},  # keep seed P793 events
    )

    expanded_rel: List[Dict[str, Any]] = []
    expanded_attr: List[Dict[str, Any]] = []
    hop2_rel: List[Dict[str, Any]] = []
    hop2_attr: List[Dict[str, Any]] = []

    pred_counter: Counter[str] = Counter()
    canonical_counter: Counter[str] = Counter()
    mode_counter: Counter[str] = Counter()

    for qid, payload in frontier_payloads.items():
        role = frontier_roles.get(qid, "frontier")
        rel, attr, _ = _statement_to_claims(
            payload=payload,
            source_mode=f"expanded_{role}",
            registry_map=registry_map,
            property_catalog=property_catalog,
        )
        expanded_rel.extend(rel)
        expanded_attr.extend(attr)

    for qid, payload in hop2_payloads.items():
        rel, attr, _ = _statement_to_claims(
            payload=payload,
            source_mode="second_hop_person",
            registry_map=registry_map,
            property_catalog=property_catalog,
            allow_properties=HOP2_ALLOW_PROPERTIES,
            skip_properties=SKIP_PROPERTIES,
        )
        hop2_rel.extend(rel)
        hop2_attr.extend(attr)

    relationship_claims = direct_rel + expanded_rel + hop2_rel
    attribute_claims = direct_attr + expanded_attr + hop2_attr

    def _dedupe(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen: Set[str] = set()
        out: List[Dict[str, Any]] = []
        for row in rows:
            key = row.get("statement_id") or row.get("claim_id")
            if key in seen:
                continue
            seen.add(key)
            out.append(row)
        return out

    relationship_claims = _dedupe(relationship_claims)
    attribute_claims = _dedupe(attribute_claims)

    relationship_claims.sort(
        key=lambda x: (-float(x.get("confidence", 0.0)), x.get("predicate_pid", ""), x.get("claim_id", ""))
    )
    attribute_claims.sort(
        key=lambda x: (-float(x.get("confidence", 0.0)), x.get("predicate_pid", ""), x.get("claim_id", ""))
    )

    for row in relationship_claims:
        pred_counter[row["predicate_pid"]] += 1
        mode_counter[row["source_mode"]] += 1
        for rel in row.get("canonical_relationship_types") or []:
            canonical_counter[rel] += 1
    for row in attribute_claims:
        pred_counter[row["predicate_pid"]] += 1
        mode_counter[row["source_mode"]] += 1

    node_roles: Dict[str, Set[str]] = defaultdict(set)
    node_roles[seed_qid].add("seed")
    for qid, role in frontier_roles.items():
        node_roles[qid].add(f"frontier_{role}")
    for qid in hop2_humans:
        node_roles[qid].add("second_hop_person")
    for row in relationship_claims:
        node_roles[row["subject_qid"]].add("claim_subject")
        node_roles[row["object_qid"]].add("claim_object")
    for row in attribute_claims:
        node_roles[row["subject_qid"]].add("claim_subject")

    nodes = [
        {
            "qid": qid,
            "label": "",
            "description": "",
            "roles": sorted(roles),
        }
        for qid, roles in sorted(node_roles.items())
    ]

    timeline = _build_timeline_entries(relationship_claims, attribute_claims)

    proposal: Dict[str, Any] = {
        "generated_at": _now_utc(),
        "version": "v2_expanded",
        "seed": {
            "qid": seed_qid,
            "label": seed_label,
            "description": seed_description,
        },
        "sources": {
            "direct_statement_count": int(statements_payload.get("statement_count") or 0),
            "seed_index": "JSON/wikidata/derived/Q17167_seed_index.json",
            "backlink_report": "JSON/wikidata/backlinks/Q17167_backlink_harvest_report.json",
            "frontier": {
                "event_count": sum(1 for r in frontier_roles.values() if r == "event"),
                "battle_count": sum(1 for r in frontier_roles.values() if r == "battle"),
                "frontier_qids": frontier_qids,
            },
            "second_hop": {
                "candidates_from_p710": len(hop2_qids),
                "human_shells_fetched": len(hop2_humans),
            },
        },
        "summary": {
            "node_count": len(nodes),
            "relationship_claim_count": len(relationship_claims),
            "attribute_claim_count": len(attribute_claims),
            "timeline_entry_count": len(timeline),
            "claims_by_source_mode": _top_counter_items(mode_counter, 10),
            "top_predicates": _top_counter_items(pred_counter, 25),
            "top_canonical_relationship_types": _top_counter_items(canonical_counter, 25),
        },
        "nodes": nodes,
        "relationship_claim_proposals": relationship_claims,
        "attribute_claim_proposals": attribute_claims,
        "timeline_entries": timeline,
        "analysis_notes": [
            "v2 replaces collapsed backlink stubs with full Wikidata statements on events and battles.",
            "P921 scholarly-work edges and media/catalog properties are filtered on expanded nodes.",
            "Second-hop person shells include biographic predicates only (P39, P22, dates, etc.).",
            "Timeline entries derive from P571/P570/P580/P582/P585 and relational qualifiers.",
            "Every QID must carry a human-readable label before review or integration.",
            "Claims remain proposals with confidence heuristics — human review before graph write.",
        ],
    }

    if fetch_labels:
        all_qids: Set[str] = {seed_qid}
        for node in nodes:
            all_qids.add(node["qid"])
        for row in relationship_claims:
            all_qids.add(row["subject_qid"])
            all_qids.add(row["object_qid"])
        for row in attribute_claims:
            all_qids.add(row["subject_qid"])
        statement_dirs = [Path("JSON/wikidata/statements")]
        if cache_dir:
            statement_dirs.append(cache_dir)
        labels = resolve_labels(
            all_qids,
            seed_index=seed_index,
            statement_dirs=statement_dirs,
            fetch_missing=True,
        )
        apply_labels_to_proposal(proposal, labels)
        bare = sum(
            1
            for n in proposal["nodes"]
            if is_bare_qid_label(n.get("label"), n.get("qid", ""))
        )
        proposal["summary"]["bare_label_nodes"] = bare

    return proposal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-qid", required=True, help="Seed QID (example: Q17167).")
    parser.add_argument(
        "--statements-json",
        help="Path to seed statements JSON.",
    )
    parser.add_argument(
        "--seed-index",
        help="Path to seed index JSON.",
    )
    parser.add_argument(
        "--backlink-report",
        help="Path to backlink harvest report JSON.",
    )
    parser.add_argument(
        "--relationship-registry",
        default="Relationships/relationship_types_registry_master.csv",
    )
    parser.add_argument(
        "--property-catalog",
        default="CSV/wikiPvalues.csv",
    )
    parser.add_argument("--max-battles", type=int, default=30)
    parser.add_argument("--max-persons", type=int, default=80)
    parser.add_argument(
        "--output-prefix",
        help="Output prefix without extension. Default: JSON/wikidata/proposals/<QID>_claim_subgraph_proposal_v2",
    )
    parser.add_argument(
        "--cache-dir",
        default="JSON/wikidata/statements/expansion",
        help="Cache fetched frontier/person statements.",
    )
    parser.add_argument(
        "--no-fetch-labels",
        action="store_true",
        help="Skip label enrichment API calls.",
    )
    args = parser.parse_args()

    seed_qid = _normalize_qid(args.seed_qid)
    statements_path = Path(
        args.statements_json or f"JSON/wikidata/statements/{seed_qid}_statements_full.json"
    )
    seed_index_path = Path(args.seed_index or f"JSON/wikidata/derived/{seed_qid}_seed_index.json")
    backlink_path = Path(
        args.backlink_report or f"JSON/wikidata/backlinks/{seed_qid}_backlink_harvest_report.json"
    )
    output_prefix = Path(
        args.output_prefix or f"JSON/wikidata/proposals/{seed_qid}_claim_subgraph_proposal_v2"
    )

    for path in (statements_path, seed_index_path, backlink_path):
        if not path.exists():
            raise FileNotFoundError(path)

    statements_payload = _load_json(statements_path)
    seed_index = _load_json(seed_index_path)
    backlink_report = _load_json(backlink_path)
    registry_map = _load_registry_property_map(Path(args.relationship_registry))
    property_catalog = _load_property_catalog(Path(args.property_catalog))

    proposal = build_expanded_proposal(
        seed_qid=seed_qid,
        statements_payload=statements_payload,
        seed_index=seed_index,
        backlink_report=backlink_report,
        registry_map=registry_map,
        property_catalog=property_catalog,
        max_battles=args.max_battles,
        max_persons=args.max_persons,
        fetch_labels=not args.no_fetch_labels,
        cache_dir=Path(args.cache_dir) if args.cache_dir else None,
    )

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_out = Path(f"{output_prefix}.json")
    md_out = Path(f"{output_prefix}.md")
    json_out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")

    write_markdown(
        proposal=proposal,
        output_path=md_out,
        statements_path=statements_path,
        backlinks_path=backlink_path,
    )
    # Append v2-specific sections
    extra_lines = [
        "",
        "## v2 Expansion",
        f"- Frontier events: **{proposal['sources']['frontier']['event_count']}**",
        f"- Frontier battles: **{proposal['sources']['frontier']['battle_count']}**",
        f"- Second-hop persons: **{proposal['sources']['second_hop']['human_shells_fetched']}**",
        f"- Timeline entries: **{proposal['summary']['timeline_entry_count']}**",
        "",
        "## Sample Timeline Entries",
    ]
    for row in (proposal.get("timeline_entries") or [])[:25]:
        extra_lines.append(
            f"- {row.get('year')}: `{row.get('subject_qid')}` ({row.get('subject_label')}) "
            f"{row.get('predicate_pid')}"
        )
    md_out.write_text(md_out.read_text(encoding="utf-8") + "\n".join(extra_lines), encoding="utf-8")

    summary = proposal.get("summary", {})
    print(f"seed={seed_qid}")
    print(f"nodes={summary.get('node_count', 0)}")
    print(f"relationship_claims={summary.get('relationship_claim_count', 0)}")
    print(f"attribute_claims={summary.get('attribute_claim_count', 0)}")
    print(f"timeline_entries={summary.get('timeline_entry_count', 0)}")
    print(f"json={json_out}")
    print(f"markdown={md_out}")


if __name__ == "__main__":
    main()
