#!/usr/bin/env python3
"""
Simulate SCA-style QID categorization with expanded Wikidata property extraction.

Key behaviors:
1. Ingest up to N QIDs from a source CSV (default: 200).
2. Pull hierarchy, temporal, and geographical claims from Wikidata.
3. Emit long-form property rows (one row per property statement/value).
4. Emit dedicated row outputs for P31 and geo properties.
5. Emit categorization rows with full JSON decision rationale.

All IDs are paired with labels (fallback label = ID when unavailable).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WIKIDATA_API = "https://www.wikidata.org/w/api.php"
LANG_PREF = ["en", "sv", "de", "fr", "es", "it", "ru", "ja", "zh", "ar", "la", "mul"]

HIERARCHY_PIDS = {
    "P31",    # instance of
    "P279",   # subclass of
    "P361",   # part of
    "P527",   # has part(s)
    "P155",   # follows
    "P156",   # followed by
    "P1365",  # replaces
    "P1366",  # replaced by
}
TEMPORAL_PIDS = {
    "P580",   # start time
    "P582",   # end time
    "P585",   # point in time
    "P571",   # inception
    "P576",   # dissolved/abolished/demolished
    "P577",   # publication date
    "P569",   # date of birth
    "P570",   # date of death
    "P2031",  # work period (start)
    "P2032",  # work period (end)
    "P2348",  # time period
}
GEOGRAPHICAL_PIDS = {
    "P131",   # located in the administrative territorial entity
    "P17",    # country
    "P276",   # location
    "P706",   # located on terrain feature
    "P7153",  # significant place
    "P625",   # coordinate location
}
PERIODO_PID = "P9350"

TARGET_PIDS = set().union(HIERARCHY_PIDS, TEMPORAL_PIDS, GEOGRAPHICAL_PIDS, {PERIODO_PID})

CANONICAL_TYPES = ["UNRESOLVED_FOR_SCA"]


def parse_qid(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    m = re.search(r"Q\d+", value.strip())
    return m.group(0) if m else None


def best_label(labels_obj: Dict[str, Dict[str, str]], fallback: str) -> str:
    for lang in LANG_PREF:
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


def fetch_entities(ids: List[str]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not ids:
        return out
    for batch in chunked(ids, 40):
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


def statement_value(stmt: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (value_qid, value_literal).
    """
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return (None, None)

    datatype = mainsnak.get("datatype")
    datavalue = mainsnak.get("datavalue", {}).get("value")
    if datavalue is None:
        return (None, None)

    if datatype == "wikibase-item":
        qid = datavalue.get("id")
        if not qid:
            numeric_id = datavalue.get("numeric-id")
            qid = f"Q{numeric_id}" if numeric_id is not None else None
        return (qid, None)

    if datatype == "globecoordinate":
        lat = datavalue.get("latitude")
        lon = datavalue.get("longitude")
        precision = datavalue.get("precision")
        lit = f"lat={lat};lon={lon};precision={precision}"
        return (None, lit)

    if datatype == "time":
        lit = datavalue.get("time")
        precision = datavalue.get("precision")
        if lit is not None:
            lit = f"time={lit};precision={precision}"
        return (None, lit)

    if datatype == "monolingualtext":
        text = datavalue.get("text")
        lang = datavalue.get("language")
        return (None, f"text={text};lang={lang}")

    if datatype == "quantity":
        amount = datavalue.get("amount")
        unit = datavalue.get("unit")
        return (None, f"amount={amount};unit={unit}")

    # strings, external-id, url, commonsMedia, etc.
    return (None, str(datavalue))


def property_group(pid: str) -> str:
    if pid in HIERARCHY_PIDS:
        return "hierarchy"
    if pid in TEMPORAL_PIDS or pid == PERIODO_PID:
        return "temporal"
    if pid in GEOGRAPHICAL_PIDS:
        return "geographical"
    return "other"


def load_subjects(source_csv: Path, limit: int) -> Dict[str, dict]:
    by_qid: Dict[str, dict] = {}
    with source_csv.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            raw_qid = (
                row.get("qid")
                or row.get("subject_qid")
                or row.get("item")
                or row.get("item_qid")
            )
            qid = parse_qid(raw_qid)
            if not qid:
                continue
            d = by_qid.setdefault(
                qid,
                {
                    "qid": qid,
                    "source_label": (
                        row.get("label")
                        or row.get("subject_label")
                        or row.get("itemLabel")
                        or ""
                    ).strip(),
                    "periodo_ids": set(),
                },
            )
            pid = (
                row.get("periodo_id")
                or row.get("periodo_id_sample")
                or row.get("period")
                or ""
            ).strip()
            if pid:
                d["periodo_ids"].add(pid)
            if len(by_qid) >= limit:
                break
    return by_qid


def classify_qid(
    *,
    qid: str,
    qid_label: str,
    periodo_ids: Set[str],
    rows: List[dict],
) -> Tuple[str, float, Dict[str, int], List[dict]]:
    """
    Deterministic typing removed by request.
    Keep extraction-only output for SCA adjudication.
    """
    evidence: List[dict] = []
    property_ids = sorted({r["property_pid"] for r in rows})
    evidence.append(
        {
            "kind": "extraction_only",
            "message": "Deterministic type mapping disabled. Route to SCA adjudication.",
            "qid": {"id": qid, "label": qid_label},
            "periodo_ids": sorted(periodo_ids),
            "property_ids": property_ids,
        }
    )
    return ("UNRESOLVED_FOR_SCA", 0.00, {}, evidence)


def main() -> int:
    parser = argparse.ArgumentParser(description="Expanded SCA QID categorization simulation.")
    parser.add_argument(
        "--source-csv",
        default="Temporal/wikidata_periodo_start_end_unique_items_2026-02-18.csv",
        help="Source CSV containing QIDs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Maximum distinct QIDs to process.",
    )
    parser.add_argument(
        "--out-property-rows-csv",
        default="Temporal/wikidata_period_sca_property_rows_2026-02-18.csv",
        help="Long-form hierarchy/temporal/geographical property rows.",
    )
    parser.add_argument(
        "--out-p31-rows-csv",
        default="Temporal/wikidata_period_sca_p31_rows_2026-02-18.csv",
        help="Long-form P31 rows.",
    )
    parser.add_argument(
        "--out-geo-rows-csv",
        default="Temporal/wikidata_period_sca_geo_rows_2026-02-18.csv",
        help="Long-form geographical rows.",
    )
    parser.add_argument(
        "--out-categorization-csv",
        default="Temporal/wikidata_period_sca_categorization_2026-02-18.csv",
        help="Categorization output with JSON rationale.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    source_csv = (project_root / args.source_csv).resolve()
    out_prop_csv = (project_root / args.out_property_rows_csv).resolve()
    out_p31_csv = (project_root / args.out_p31_rows_csv).resolve()
    out_geo_csv = (project_root / args.out_geo_rows_csv).resolve()
    out_cat_csv = (project_root / args.out_categorization_csv).resolve()

    if not source_csv.exists():
        print(f"ERROR: source CSV not found: {source_csv}")
        return 1

    subjects = load_subjects(source_csv, limit=args.limit)
    qids = sorted(subjects.keys())
    if not qids:
        print("ERROR: no valid QIDs found in source CSV")
        return 1

    entities = fetch_entities(qids)

    property_rows: List[dict] = []
    value_qids: Set[str] = set()
    pids_seen: Set[str] = set()

    for qid in qids:
        entity = entities.get(qid, {})
        qid_label = best_label(entity.get("labels", {}), fallback=subjects[qid]["source_label"] or qid)
        claims = entity.get("claims", {})

        for pid, stmts in claims.items():
            if pid not in TARGET_PIDS:
                continue
            pids_seen.add(pid)
            group = property_group(pid)
            for idx, stmt in enumerate(stmts):
                value_qid, value_literal = statement_value(stmt)
                if value_qid:
                    value_qids.add(value_qid)
                row = {
                    "qid": qid,
                    "qid_label": qid_label,
                    "group": group,
                    "property_pid": pid,
                    "property_label": pid,  # filled later
                    "statement_index": idx,
                    "rank": stmt.get("rank", "normal"),
                    "value_qid": value_qid or "",
                    "value_label": value_qid or "",  # filled later
                    "value_literal": value_literal or "",
                    "periodo_ids": " | ".join(sorted(subjects[qid]["periodo_ids"])),
                }
                property_rows.append(row)

    # Fetch labels for property IDs and value QIDs.
    label_entities = fetch_entities(sorted(pids_seen | value_qids))
    label_by_id: Dict[str, str] = {}
    for eid, ent in label_entities.items():
        label_by_id[eid] = best_label(ent.get("labels", {}), fallback=eid)

    for r in property_rows:
        r["property_label"] = label_by_id.get(r["property_pid"], r["property_pid"])
        if r["value_qid"]:
            r["value_label"] = label_by_id.get(r["value_qid"], r["value_qid"])
        else:
            r["value_label"] = r["value_literal"]

    by_qid_rows: Dict[str, List[dict]] = defaultdict(list)
    for r in property_rows:
        by_qid_rows[r["qid"]].append(r)

    categorization_rows: List[dict] = []
    for qid in qids:
        rows = by_qid_rows.get(qid, [])
        qid_label = rows[0]["qid_label"] if rows else (subjects[qid]["source_label"] or qid)
        canonical_type, confidence, votes, evidence = classify_qid(
            qid=qid,
            qid_label=qid_label,
            periodo_ids=subjects[qid]["periodo_ids"],
            rows=rows,
        )

        hierarchy_rows = [r for r in rows if r["group"] == "hierarchy"]
        temporal_rows = [r for r in rows if r["group"] == "temporal"]
        geographical_rows = [r for r in rows if r["group"] == "geographical"]
        p31_rows = [r for r in rows if r["property_pid"] == "P31"]
        has_temporal = len(temporal_rows) > 0
        has_geo = len(geographical_rows) > 0
        if has_temporal and has_geo:
            coverage_badge = "gold_star"
        elif has_temporal or has_geo:
            coverage_badge = "silver"
        else:
            coverage_badge = "bronze"

        rationale = {
            "qid": {"id": qid, "label": qid_label},
            "decision": {
                "canonical_type": canonical_type,
                "confidence": round(confidence, 2),
                "vote_scores": votes,
                "coverage_badge": coverage_badge,
            },
            "periodo_ids": sorted(subjects[qid]["periodo_ids"]),
            "property_groups": {
                "hierarchy": [
                    {
                        "property": {"id": r["property_pid"], "label": r["property_label"]},
                        "value": {"id": (r["value_qid"] or None), "label": r["value_label"]},
                    }
                    for r in hierarchy_rows
                ],
                "temporal": [
                    {
                        "property": {"id": r["property_pid"], "label": r["property_label"]},
                        "value": {"id": (r["value_qid"] or None), "label": r["value_label"]},
                    }
                    for r in temporal_rows
                ],
                "geographical": [
                    {
                        "property": {"id": r["property_pid"], "label": r["property_label"]},
                        "value": {"id": (r["value_qid"] or None), "label": r["value_label"]},
                    }
                    for r in geographical_rows
                ],
            },
            "coverage_flags": {
                "has_temporal": has_temporal,
                "has_geographical": has_geo,
            },
            "evidence": evidence,
        }

        categorization_rows.append(
            {
                "qid": qid,
                "qid_label": qid_label,
                "periodo_ids": " | ".join(sorted(subjects[qid]["periodo_ids"])),
                "canonical_type": canonical_type,
                "confidence": f"{confidence:.2f}",
                "has_temporal": str(has_temporal).lower(),
                "has_geographical": str(has_geo).lower(),
                "coverage_badge": coverage_badge,
                "p31_rows_count": str(len(p31_rows)),
                "geo_rows_count": str(len(geographical_rows)),
                "temporal_rows_count": str(len(temporal_rows)),
                "decision_rationale_json": json.dumps(rationale, ensure_ascii=False),
            }
        )

    out_prop_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_prop_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "qid",
                "qid_label",
                "group",
                "property_pid",
                "property_label",
                "statement_index",
                "rank",
                "value_qid",
                "value_label",
                "value_literal",
                "periodo_ids",
            ],
        )
        writer.writeheader()
        writer.writerows(property_rows)

    with out_p31_csv.open("w", encoding="utf-8", newline="") as fh:
        p31_rows = [r for r in property_rows if r["property_pid"] == "P31"]
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "qid",
                "qid_label",
                "property_pid",
                "property_label",
                "statement_index",
                "rank",
                "value_qid",
                "value_label",
                "periodo_ids",
            ],
        )
        writer.writeheader()
        writer.writerows(
            {
                "qid": r["qid"],
                "qid_label": r["qid_label"],
                "property_pid": r["property_pid"],
                "property_label": r["property_label"],
                "statement_index": r["statement_index"],
                "rank": r["rank"],
                "value_qid": r["value_qid"],
                "value_label": r["value_label"],
                "periodo_ids": r["periodo_ids"],
            }
            for r in p31_rows
        )

    with out_geo_csv.open("w", encoding="utf-8", newline="") as fh:
        geo_rows = [r for r in property_rows if r["group"] == "geographical"]
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "qid",
                "qid_label",
                "property_pid",
                "property_label",
                "statement_index",
                "rank",
                "value_qid",
                "value_label",
                "value_literal",
                "periodo_ids",
            ],
        )
        writer.writeheader()
        writer.writerows(
            {
                "qid": r["qid"],
                "qid_label": r["qid_label"],
                "property_pid": r["property_pid"],
                "property_label": r["property_label"],
                "statement_index": r["statement_index"],
                "rank": r["rank"],
                "value_qid": r["value_qid"],
                "value_label": r["value_label"],
                "value_literal": r["value_literal"],
                "periodo_ids": r["periodo_ids"],
            }
            for r in geo_rows
        )

    with out_cat_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "qid",
                "qid_label",
                "periodo_ids",
                "canonical_type",
                "confidence",
                "has_temporal",
                "has_geographical",
                "coverage_badge",
                "p31_rows_count",
                "geo_rows_count",
                "temporal_rows_count",
                "decision_rationale_json",
            ],
        )
        writer.writeheader()
        writer.writerows(categorization_rows)

    dist = Counter(r["canonical_type"] for r in categorization_rows)
    print("Expanded SCA simulation complete.")
    print(f"  Source CSV: {source_csv}")
    print(f"  Requested limit: {args.limit}")
    print(f"  Processed QIDs: {len(qids)}")
    print(f"  Property rows: {out_prop_csv}")
    print(f"  P31 rows: {out_p31_csv}")
    print(f"  Geo rows: {out_geo_csv}")
    print(f"  Categorization: {out_cat_csv}")
    print("  Type distribution:")
    for t in CANONICAL_TYPES:
        if t in dist:
            print(f"    - {t}: {dist[t]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
