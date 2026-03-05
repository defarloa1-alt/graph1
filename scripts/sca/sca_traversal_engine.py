#!/usr/bin/env python3
"""
SCA Traversal Engine — recursive P31/P279 backlink traversal for subject domain structure.

Flow:
  1. Seed QID (e.g. Q17167 Roman Republic)
  2. Get P31 (instance of) and P279 (subclass of) for seed
  3. For each type: get backlinks (entities pointing TO that type)
  4. For each backlink: get P31; categorize backlinks by instance-of
  5. For each non-base type: recurse (backlinks → categorize → recurse) until metalevel
  6. Metalevel = type has no authority IDs (FAST, LCC, LCSH) or backlinks don't map to our entities
  7. Extend with P527 (has part), P361 (part of), P131, P17 from seed

Output: structured dict for persistence to Neo4j (WikidataType, SubjectDomain, training QIDs).

Usage:
  python scripts/sca/sca_traversal_engine.py --qid Q17167
  python scripts/sca/sca_traversal_engine.py --qid Q17167 --max-depth 3 --max-backlinks 30 -o output/sca/Q17167_domain.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Chrystallum/1.0 (SCA traversal)"
QID_RE = re.compile(r"^Q[1-9]\d*$")
PID_RE = re.compile(r"^P[1-9]\d*$")

# Authority PIDs for metalevel detection (TaxonomyHarvester)
AUTHORITY_PRIMARY = {"P2163", "P1149", "P8814", "P9842", "P1584"}  # FAST, LCC, Nomisma, PACTOLS, Pleiades
AUTHORITY_SECONDARY = {"P244", "P227", "P268"}  # LCSH, GND, BnF

# Known meta-ceiling types (no authority IDs)
META_TYPES = {
    "Q16889133",  # class
    "Q35120",     # entity
    "Q488383",    # concept
    "Q23958852",  # second-order class
    "Q19478619",  # metaclass
}

# Structural properties to extend seed (P527 has part, P361 part of, etc.)
STRUCTURAL_PROPS = ["P527", "P361", "P131", "P17", "P150"]


def _sparql(query: str, timeout_s: int = 60) -> list[dict]:
    r = requests.get(
        SPARQL_URL,
        params={"query": query, "format": "json"},
        headers={"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT},
        timeout=timeout_s,
    )
    r.raise_for_status()
    bindings = r.json().get("results", {}).get("bindings", [])
    return [{k: v.get("value", "") for k, v in row.items()} for row in bindings]


def _wd_uri_to_id(uri: str) -> str:
    if not uri:
        return ""
    tail = uri.rsplit("/", 1)[-1].strip().upper()
    return tail if (QID_RE.fullmatch(tail) or PID_RE.fullmatch(tail)) else ""


def get_p31_p279(qid: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Get P31 (instance of) and P279 (subclass of) for a QID. Returns [(qid, label), ...]."""
    query = f"""
    SELECT ?type ?typeLabel ?prop WHERE {{
      wd:{qid} ?prop ?type .
      FILTER(?prop IN (wdt:P31, wdt:P279))
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    rows = _sparql(query)
    p31, p279 = [], []
    for r in rows:
        t = _wd_uri_to_id(r.get("type", ""))
        lab = (r.get("typeLabel") or "").strip() or t
        prop = _wd_uri_to_id(r.get("prop", ""))
        if not t or not QID_RE.fullmatch(t):
            continue
        pair = (t, lab)
        if prop == "P31" and pair not in p31:
            p31.append(pair)
        elif prop == "P279" and pair not in p279:
            p279.append(pair)
    return p31, p279


def get_backlinks_to_type(type_qid: str, limit: int = 100, props: list[str] | None = None) -> list[dict]:
    """Get entities that point TO type_qid via P31 or P279. Returns list of {qid, label, via_property}."""
    props = props or ["P31", "P279"]
    prop_vals = " ".join(f"wdt:{p}" for p in props)
    query = f"""
    SELECT ?item ?itemLabel ?prop WHERE {{
      VALUES ?prop {{ {prop_vals} }}
      ?item ?prop wd:{type_qid} .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    """
    rows = _sparql(query)
    seen = set()
    out = []
    for r in rows:
        qid = _wd_uri_to_id(r.get("item", ""))
        if not qid or qid in seen:
            continue
        seen.add(qid)
        out.append({
            "qid": qid,
            "label": (r.get("itemLabel") or "").strip() or qid,
            "via_property": _wd_uri_to_id(r.get("prop", "")),
        })
    return out


def get_p31_for_qids(qids: list[str], batch: int = 50) -> dict[str, list[tuple[str, str]]]:
    """Batch fetch P31 for QIDs. Returns {qid: [(type_qid, type_label), ...]}."""
    out = defaultdict(list)
    for i in range(0, len(qids), batch):
        chunk = qids[i : i + batch]
        ids = " ".join(f"wd:{q}" for q in chunk)
        query = f"""
        SELECT ?item ?type ?typeLabel WHERE {{
          VALUES ?item {{ {ids} }}
          ?item wdt:P31 ?type .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        rows = _sparql(query)
        for r in rows:
            item = _wd_uri_to_id(r.get("item", ""))
            typ = _wd_uri_to_id(r.get("type", ""))
            lab = (r.get("typeLabel") or "").strip() or typ
            if item and typ:
                out[item].append((typ, lab))
        time.sleep(0.5)
    return dict(out)


def has_authority_ids(qid: str) -> bool:
    """Check if entity has any authority IDs (FAST, LCC, LCSH, etc.)."""
    query = f"""
    SELECT ?prop WHERE {{
      wd:{qid} ?prop ?val .
      FILTER(?prop IN (
        wdt:P2163, wdt:P1149, wdt:P244,
        wdt:P227, wdt:P268, wdt:P8814, wdt:P9842, wdt:P1584
      ))
    }}
    LIMIT 1
    """
    rows = _sparql(query)
    return len(rows) > 0


def get_labels_for_qids(qids: list[str], batch: int = 50) -> dict[str, str]:
    """Batch fetch English labels for QIDs via SPARQL. Returns {qid: label}."""
    out = {}
    for i in range(0, len(qids), batch):
        chunk = qids[i : i + batch]
        ids = " ".join(f"wd:{q}" for q in chunk)
        query = f"""
        SELECT ?item ?itemLabel WHERE {{
          VALUES ?item {{ {ids} }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        rows = _sparql(query)
        for r in rows:
            qid = _wd_uri_to_id(r.get("item", ""))
            lab = (r.get("itemLabel") or "").strip() or qid
            if qid:
                out[qid] = lab
        time.sleep(0.3)
    return out


def get_structural_props(qid: str, props: list[str] | None = None) -> dict[str, list[tuple[str, str]]]:
    """Get P527, P361, P131, P17, P150 values for seed. Returns {pid: [(target_qid, label), ...]}."""
    props = props or STRUCTURAL_PROPS
    prop_vals = " ".join(f"wdt:{p}" for p in props)
    query = f"""
    SELECT ?prop ?val ?valLabel WHERE {{
      VALUES ?prop {{ {prop_vals} }}
      wd:{qid} ?prop ?val .
      FILTER(isIRI(?val))
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    rows = _sparql(query)
    out = defaultdict(list)
    for r in rows:
        pid = _wd_uri_to_id(r.get("prop", ""))
        val = _wd_uri_to_id(r.get("val", ""))
        lab = (r.get("valLabel") or "").strip() or val
        if pid and val:
            out[pid].append((val, lab))
    return dict(out)


def categorize_backlinks_by_p31(backlinks: list[dict], p31_map: dict[str, list[tuple[str, str]]]) -> dict[str, list[dict]]:
    """Group backlinks by their P31 types. Returns {type_qid: [backlink dicts]}."""
    by_type = defaultdict(list)
    for bl in backlinks:
        types = p31_map.get(bl["qid"], [])
        for typ_qid, typ_label in types:
            by_type[typ_qid].append({**bl, "type_label": typ_label})
    return dict(by_type)


def traverse(
    seed_qid: str,
    max_depth: int = 3,
    max_backlinks_per_type: int = 50,
    max_types_to_expand: int = 20,
    sleep_s: float = 0.5,
) -> dict:
    """
    Run full SCA traversal. Returns structured output for persistence.
    """
    all_types: dict[str, dict] = {}  # qid -> {label, tier, backlinks_by_type, depth, ...}
    all_backlinks: set[str] = set()
    training_qids: set[str] = {seed_qid}
    label_map: dict[str, str] = {}  # qid -> label (for training_qids output)
    type_queue: list[tuple[str, str, int, str | None]] = []  # (type_qid, label, depth, parent_type)

    # 1. Get P31, P279 for seed
    p31, p279 = get_p31_p279(seed_qid)
    time.sleep(sleep_s)

    for qid, lab in p31 + p279:
        if qid not in all_types:
            all_types[qid] = {"qid": qid, "label": lab, "depth": 1, "source": "P31" if (qid, lab) in p31 else "P279"}
            type_queue.append((qid, lab, 1, None))

    # 2. Recursive expansion
    expanded = 0
    while type_queue and expanded < max_types_to_expand:
        type_qid, type_label, depth, parent = type_queue.pop(0)

        # Metalevel check
        if type_qid in META_TYPES:
            all_types[type_qid]["tier"] = "meta"
            all_types[type_qid]["traversal_boundary"] = True
            continue
        if not has_authority_ids(type_qid) and depth > 1:
            all_types.setdefault(type_qid, {"qid": type_qid, "label": type_label, "depth": depth})["tier"] = "meta"
            all_types[type_qid]["traversal_boundary"] = True
            time.sleep(sleep_s)
            continue

        # Get backlinks
        bl = get_backlinks_to_type(type_qid, limit=max_backlinks_per_type)
        time.sleep(sleep_s)

        for b in bl:
            all_backlinks.add(b["qid"])
            training_qids.add(b["qid"])
            if b.get("label"):
                label_map[b["qid"]] = b["label"]

        # Get P31 for backlinks, categorize
        qids = [b["qid"] for b in bl]
        p31_map = get_p31_for_qids(qids)
        time.sleep(sleep_s)
        by_type = categorize_backlinks_by_p31(bl, p31_map)

        # Store
        if type_qid not in all_types:
            all_types[type_qid] = {"qid": type_qid, "label": type_label, "depth": depth}
        all_types[type_qid]["backlink_count"] = len(bl)
        all_types[type_qid]["backlinks_by_instance_of"] = {
            t: [{"qid": x["qid"], "label": x["label"]} for x in items[:15]]
            for t, items in by_type.items()
        }
        all_types[type_qid]["tier"] = "primary" if has_authority_ids(type_qid) else "secondary"

        # Queue non-base types for expansion
        if depth < max_depth and not all_types[type_qid].get("traversal_boundary"):
            for child_type, items in by_type.items():
                if child_type not in all_types and expanded < max_types_to_expand:
                    child_label = items[0].get("type_label", child_type) if items else child_type
                    all_types[child_type] = {"qid": child_type, "label": child_label, "depth": depth + 1}
                    type_queue.append((child_type, child_label, depth + 1, type_qid))
                    expanded += 1
        if expanded >= max_types_to_expand:
            break

    # 3. Structural props for seed
    structural = get_structural_props(seed_qid)
    time.sleep(sleep_s)

    # 4. Fetch labels for any training QIDs we don't have
    missing = [q for q in training_qids if q not in label_map]
    if missing:
        fetched = get_labels_for_qids(missing)
        label_map.update(fetched)
    # Ensure seed has label
    if seed_qid not in label_map:
        label_map.update(get_labels_for_qids([seed_qid]))

    training_qids_with_labels = [
        {"qid": q, "label": label_map.get(q, q)}
        for q in sorted(training_qids)
    ]

    return {
        "seed_qid": seed_qid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "max_depth": max_depth,
        "summary": {
            "types_discovered": len(all_types),
            "backlinks_total": len(all_backlinks),
            "training_qids_count": len(training_qids),
        },
        "types": list(all_types.values()),
        "structural_props": {k: v for k, v in structural.items()},
        "training_qids": training_qids_with_labels,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="SCA Traversal Engine")
    ap.add_argument("--qid", required=True, help="Seed QID (e.g. Q17167)")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-backlinks", type=int, default=50)
    ap.add_argument("--max-types", type=int, default=20)
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    qid = args.qid.strip().upper()
    if not QID_RE.fullmatch(qid):
        print("Invalid QID", file=sys.stderr)
        return 1

    print(f"SCA traversal for {qid}...")
    result = traverse(
        qid,
        max_depth=args.max_depth,
        max_backlinks_per_type=args.max_backlinks,
        max_types_to_expand=args.max_types,
    )
    print(f"  Types: {result['summary']['types_discovered']}")
    print(f"  Backlinks: {result['summary']['backlinks_total']}")
    print(f"  Training QIDs: {result['summary']['training_qids_count']}")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Wrote {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
