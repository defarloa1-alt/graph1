#!/usr/bin/env python3
"""Build a derived Seed Knowledge Index from Wikidata statement + backlink artifacts.

Reads:
  - JSON/wikidata/statements/<QID>_statements_full.json
  - JSON/wikidata/backlinks/<QID>_backlink_harvest_report.json (accepted section)

Writes:
  - JSON/wikidata/derived/<QID>_seed_index.json

Usage:
  python scripts/tools/wikidata_build_seed_index.py --qid Q17167
  python scripts/tools/wikidata_build_seed_index.py --qid Q17167 --fetch-labels
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
HTTP_HEADERS = {"User-Agent": "Chrystallum/1.0 (seed index builder)"}
QID_RE = re.compile(r"^Q\d+$", re.IGNORECASE)

# Backlink property → facet routing hints (for scope seeding, not classification truth)
FACET_PROPERTY_HINTS: dict[str, list[str]] = {
    "P793": ["military", "political"],
    "P710": ["military"],
    "P607": ["military"],
    "P194": ["political"],
    "P39": ["political", "biographic"],
    "P1001": ["political", "geographic"],
    "P921": ["intellectual", "communication", "cultural"],
    "P101": ["intellectual"],
    "P140": ["religious"],
    "P17": ["geographic", "economic"],
    "P38": ["economic"],
    "P36": ["geographic"],
    "P30": ["geographic"],
    "P527": ["political", "geographic"],
    "P361": ["geographic", "political"],
    "P138": ["cultural"],
    "P279": ["social", "intellectual"],
}

AUTHORITY_PROPERTIES = ("P244", "P2163", "P1149", "P1036", "P646", "P227", "P214")
STRUCTURAL_PROPERTIES = (
    "P31",
    "P527",
    "P361",
    "P194",
    "P793",
    "P1366",
    "P1365",
    "P155",
    "P156",
    "P38",
    "P36",
    "P30",
    "P910",
)


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_qid(value: Any) -> bool:
    return isinstance(value, str) and bool(QID_RE.match(value))


def _extract_time_year(time_payload: dict[str, Any] | None) -> int | None:
    if not time_payload or not isinstance(time_payload, dict):
        return None
    raw = time_payload.get("time", "")
    if not raw:
        return None
    match = re.match(r"([+-]?\d+)", raw)
    if not match:
        return None
    return int(match.group(1))


def _statement_entity_targets(statement: dict[str, Any]) -> list[str]:
    qids: list[str] = []
    mainsnak = statement.get("mainsnak", {})
    value = mainsnak.get("value")
    if _is_qid(value):
        qids.append(value.upper())
    for qual_list in (statement.get("qualifiers") or {}).values():
        for snak in qual_list:
            qval = snak.get("value")
            if _is_qid(qval):
                qids.append(qval.upper())
    return qids


def _parse_direct_links(claims: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for prop, statements in claims.items():
        for stmt in statements:
            mainsnak = stmt.get("mainsnak", {})
            value = mainsnak.get("value")
            entry: dict[str, Any] = {
                "property": prop,
                "rank": stmt.get("rank", "normal"),
                "statement_id": stmt.get("statement_id"),
            }
            if _is_qid(value):
                entry["qid"] = value.upper()
            elif mainsnak.get("datatype") == "time":
                entry["time"] = mainsnak.get("value")
            elif mainsnak.get("datatype") == "external-id":
                entry["value"] = value
            else:
                entry["value"] = value
            if stmt.get("qualifiers"):
                entry["qualifiers"] = stmt["qualifiers"]
            grouped[prop].append(entry)
    return dict(grouped)


def _extract_period(instance_type_statements: list[dict[str, Any]]) -> dict[str, Any] | None:
    preferred = [s for s in instance_type_statements if s.get("rank") == "preferred"]
    candidates = preferred or instance_type_statements
    for stmt in candidates:
        quals = stmt.get("qualifiers") or {}
        start_snaks = quals.get("P580", [])
        end_snaks = quals.get("P582", [])
        if not start_snaks and not end_snaks:
            continue
        start = _extract_time_year(start_snaks[0].get("value") if start_snaks else None)
        end = _extract_time_year(end_snaks[0].get("value") if end_snaks else None)
        return {
            "start_year": start,
            "end_year": end,
            "source_property": "P31",
            "source_rank": stmt.get("rank", "normal"),
            "type_qid": stmt.get("qid"),
        }
    return None


def _extract_authority_ids(direct_links: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for prop in AUTHORITY_PROPERTIES:
        for entry in direct_links.get(prop, []):
            val = entry.get("value")
            if val:
                out[prop] = str(val)
    return out


def _fetch_labels(qids: list[str], batch_size: int = 50) -> dict[str, str]:
    labels: dict[str, str] = {}
    clean = [q for q in qids if _is_qid(q)]
    for i in range(0, len(clean), batch_size):
        batch = clean[i : i + batch_size]
        params = urllib.parse.urlencode(
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": "labels",
                "languages": "en",
                "format": "json",
            }
        )
        url = f"{WIKIDATA_API}?{params}"
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception:
            time.sleep(0.5)
            continue
        for qid, entity in payload.get("entities", {}).items():
            if entity.get("missing"):
                continue
            label = (entity.get("labels") or {}).get("en", {}).get("value")
            if label:
                labels[qid] = label
        time.sleep(0.35)
    return labels


def _load_accepted_neighbors(report_path: Path) -> list[dict[str, Any]]:
    if not report_path.exists():
        return []
    report = _load_json(report_path)
    neighbors: list[dict[str, Any]] = []
    for row in report.get("accepted", []):
        qid = (row.get("qid") or "").upper()
        if not qid:
            continue
        neighbors.append(
            {
                "qid": qid,
                "label": row.get("label"),
                "link_properties": row.get("properties") or [],
                "p31": row.get("p31") or [],
                "backlink_hits": row.get("backlink_hits", 0),
            }
        )
    return neighbors


def _build_facet_signals(neighbors: list[dict[str, Any]]) -> dict[str, Any]:
    property_counts: Counter[str] = Counter()
    facet_counts: Counter[str] = Counter()
    facet_samples: dict[str, list[str]] = defaultdict(list)

    for row in neighbors:
        qid = row["qid"]
        for prop in row.get("link_properties") or []:
            property_counts[prop] += 1
            for facet in FACET_PROPERTY_HINTS.get(prop, []):
                facet_counts[facet] += 1
                if len(facet_samples[facet]) < 12:
                    facet_samples[facet].append(qid)

    return {
        "property_counts": dict(property_counts.most_common()),
        "facet_counts": dict(facet_counts.most_common()),
        "facet_sample_qids": dict(facet_samples),
    }


def build_seed_index(
    *,
    qid: str,
    statements_path: Path,
    backlink_report_path: Path,
    fetch_labels: bool = False,
) -> dict[str, Any]:
    qid = qid.upper()
    statements = _load_json(statements_path)
    claims = statements.get("claims") or {}
    direct_links = _parse_direct_links(claims)

    direct_targets: set[str] = {qid}
    for entries in direct_links.values():
        for entry in entries:
            if entry.get("qid"):
                direct_targets.add(entry["qid"])

    neighbors = _load_accepted_neighbors(backlink_report_path)
    neighbor_qids = {n["qid"] for n in neighbors}

    labels: dict[str, str] = {}
    for n in neighbors:
        if n.get("label") and n.get("qid"):
            labels[n["qid"]] = n["label"]

    if fetch_labels:
        missing = sorted(direct_targets - set(labels.keys()))
        labels.update(_fetch_labels(missing))

    for prop in STRUCTURAL_PROPERTIES:
        for entry in direct_links.get(prop, []):
            q = entry.get("qid")
            if q and q in labels:
                entry["label"] = labels[q]

    period = _extract_period(direct_links.get("P31", []))
    authority_ids = _extract_authority_ids(direct_links)
    facet_signals = _build_facet_signals(neighbors)

    union = sorted(direct_targets | neighbor_qids)

    structural: dict[str, list[dict[str, Any]]] = {
        prop: direct_links.get(prop, []) for prop in STRUCTURAL_PROPERTIES if prop in direct_links
    }

    return {
        "generated_at": _now_utc(),
        "seed": {
            "qid": qid,
            "label": statements.get("label"),
            "description": statements.get("description"),
            "statement_count": statements.get("statement_count"),
        },
        "sources": {
            "statements": str(statements_path.as_posix()),
            "backlink_report": str(backlink_report_path.as_posix()),
        },
        "period": period,
        "authority_ids": authority_ids,
        "structural_links": structural,
        "events": [
            {**e, "label": labels.get(e["qid"])} for e in direct_links.get("P793", []) if e.get("qid")
        ],
        "parts": [
            {**e, "label": labels.get(e["qid"])} for e in direct_links.get("P527", []) if e.get("qid")
        ],
        "legislative_bodies": [
            {**e, "label": labels.get(e["qid"])} for e in direct_links.get("P194", []) if e.get("qid")
        ],
        "successors": [
            {**e, "label": labels.get(e["qid"])} for e in direct_links.get("P1366", []) if e.get("qid")
        ],
        "accepted_neighbors": neighbors,
        "facet_signals": facet_signals,
        "allowed_candidate_qids": {
            "seed_qid": qid,
            "direct_statement_targets": sorted(direct_targets - {qid}),
            "accepted_neighbors": sorted(neighbor_qids),
            "union": union,
            "count": len(union),
        },
        "labels": labels,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Seed Knowledge Index from Wikidata artifacts")
    parser.add_argument("--qid", default="Q17167", help="Seed entity QID")
    parser.add_argument(
        "--statements",
        type=Path,
        default=None,
        help="Path to statements JSON (default: JSON/wikidata/statements/<QID>_statements_full.json)",
    )
    parser.add_argument(
        "--backlink-report",
        type=Path,
        default=None,
        help="Path to backlink harvest report (default: JSON/wikidata/backlinks/<QID>_backlink_harvest_report.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: JSON/wikidata/derived/<QID>_seed_index.json)",
    )
    parser.add_argument(
        "--fetch-labels",
        action="store_true",
        help="Fetch English labels for direct statement target QIDs via Wikidata API",
    )
    args = parser.parse_args()

    qid = args.qid.upper()
    statements_path = args.statements or Path(f"JSON/wikidata/statements/{qid}_statements_full.json")
    backlink_report_path = (
        args.backlink_report or Path(f"JSON/wikidata/backlinks/{qid}_backlink_harvest_report.json")
    )
    output_path = args.output or Path(f"JSON/wikidata/derived/{qid}_seed_index.json")

    if not statements_path.exists():
        print(f"ERROR: statements file not found: {statements_path}")
        raise SystemExit(1)

    index = build_seed_index(
        qid=qid,
        statements_path=statements_path,
        backlink_report_path=backlink_report_path,
        fetch_labels=args.fetch_labels,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    allowed = index["allowed_candidate_qids"]
    print(f"Wrote seed index: {output_path}")
    print(f"  Seed: {index['seed'].get('label')} ({qid})")
    if index.get("period"):
        p = index["period"]
        print(f"  Period: {p.get('start_year')} to {p.get('end_year')}")
    print(f"  Authority IDs: {len(index.get('authority_ids', {}))}")
    print(f"  Events (P793): {len(index.get('events', []))}")
    print(f"  Parts (P527): {len(index.get('parts', []))}")
    print(f"  Accepted neighbors: {len(index.get('accepted_neighbors', []))}")
    print(f"  Allowed candidate QIDs: {allowed.get('count', 0)}")


if __name__ == "__main__":
    main()
