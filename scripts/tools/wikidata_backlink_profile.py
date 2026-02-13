#!/usr/bin/env python3
"""Profile datatype/value_type patterns for backlink candidate QIDs.

This script profiles candidate nodes without running backlink harvest.

Input modes:
- Harvest report JSON (`--input-report`) and section (`accepted|rejected|all`)
- Explicit QIDs (`--qid` repeatable)
- QID file (`--qids-file`) with one QID per line or a CSV with `qid` column

Outputs:
- `<prefix>_summary.json`
- `<prefix>_by_entity.csv`
- `<prefix>_pair_counts.csv`

Examples:
  python scripts/tools/wikidata_backlink_profile.py ^
    --input-report JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json ^
    --source-section accepted

  python scripts/tools/wikidata_backlink_profile.py --qid Q11184 --qid Q569978
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

import requests


WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1BacklinkProfiler/1.0 (local tooling)"
QID_RE = re.compile(r"Q\d+$", re.IGNORECASE)

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


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_qid(value: str) -> str:
    value = (value or "").strip().upper()
    if not QID_RE.fullmatch(value):
        raise ValueError(f"Invalid QID: {value}")
    return value


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _load_qids_from_report(report_path: Path, section: str) -> Tuple[str, List[str]]:
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    seed_qid = (payload.get("seed_qid") or "").strip().upper()

    qids: List[str] = []
    if section == "accepted":
        qids = [row.get("qid", "") for row in payload.get("accepted", [])]
    elif section == "rejected":
        qids = [row.get("qid", "") for row in payload.get("rejected", [])]
    else:
        qids = [row.get("qid", "") for row in payload.get("accepted", [])]
        qids += [row.get("qid", "") for row in payload.get("rejected", [])]

    normalized = []
    for q in qids:
        q = (q or "").strip().upper()
        if QID_RE.fullmatch(q):
            normalized.append(q)
    return seed_qid, normalized


def _load_qids_from_file(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []

    # CSV mode if header contains qid.
    if "," in lines[0] and re.search(r"\bqid\b", lines[0], re.IGNORECASE):
        qids: List[str] = []
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                q = (row.get("qid") or "").strip().upper()
                if QID_RE.fullmatch(q):
                    qids.append(q)
        return qids

    # Plain text mode: one QID per line (or mixed lines, we extract QIDs).
    qids = []
    for ln in lines:
        token = ln.split(",", 1)[0].strip().upper()
        if QID_RE.fullmatch(token):
            qids.append(token)
    return qids


def _fetch_entities_claims(
    qids: List[str],
    timeout_s: int,
    batch_size: int,
    sleep_ms: int,
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


def _profile_entities(
    entities: Dict[str, Dict[str, Any]],
    unsupported_pair_threshold: float,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    pair_counts: Counter[Tuple[str, str]] = Counter()
    datatype_counts: Counter[str] = Counter()
    value_type_counts: Counter[str] = Counter()
    rank_counts: Counter[str] = Counter()
    property_counts: Counter[str] = Counter()

    by_entity_rows: List[Dict[str, Any]] = []
    total_statements = 0
    missing_datavalue_statement_count = 0

    for qid, entity in sorted(entities.items()):
        label = ((entity.get("labels") or {}).get("en") or {}).get("value", "")
        claims = entity.get("claims", {}) or {}

        entity_pairs: Counter[Tuple[str, str]] = Counter()
        statement_count = 0
        with_qualifiers = 0
        with_references = 0

        for prop, statements in claims.items():
            for statement in statements or []:
                mainsnak = statement.get("mainsnak", {}) or {}
                datatype = (mainsnak.get("datatype") or "").strip()
                datavalue = mainsnak.get("datavalue") or {}
                value_type = (datavalue.get("type") or "").strip() if isinstance(datavalue, dict) else ""
                if not value_type:
                    missing_datavalue_statement_count += 1

                pair = (datatype, value_type)
                pair_counts[pair] += 1
                entity_pairs[pair] += 1
                datatype_counts[datatype] += 1
                value_type_counts[value_type] += 1
                property_counts[prop] += 1

                rank = (statement.get("rank") or "").strip()
                rank_counts[rank] += 1

                qualifiers = statement.get("qualifiers", {}) or {}
                references = statement.get("references", []) or []
                if qualifiers:
                    with_qualifiers += 1
                if references:
                    with_references += 1

                total_statements += 1
                statement_count += 1

        unsupported_pairs = {
            f"{k[0]}|{k[1]}": v for k, v in entity_pairs.items() if k[1] and k not in SUPPORTED_DATATYPE_VALUE_PAIRS
        }
        unsupported_count = sum(unsupported_pairs.values())
        unsupported_rate = (unsupported_count / statement_count) if statement_count else 0.0

        by_entity_rows.append(
            {
                "qid": qid,
                "label": label,
                "statement_count": statement_count,
                "property_count": len(claims),
                "with_qualifiers": with_qualifiers,
                "with_references": with_references,
                "qualifier_rate": f"{(with_qualifiers / statement_count) if statement_count else 0.0:.6f}",
                "reference_rate": f"{(with_references / statement_count) if statement_count else 0.0:.6f}",
                "unsupported_statement_count": unsupported_count,
                "unsupported_pair_rate": f"{unsupported_rate:.6f}",
                "unsupported_pairs": json.dumps(unsupported_pairs, ensure_ascii=False),
                "status": "blocked_by_policy" if unsupported_rate > unsupported_pair_threshold else "pass",
            }
        )

    unsupported_pairs_global = {
        f"{k[0]}|{k[1]}": v for k, v in pair_counts.items() if k[1] and k not in SUPPORTED_DATATYPE_VALUE_PAIRS
    }
    unsupported_statement_count = sum(unsupported_pairs_global.values())
    supported_denominator = max(0, total_statements - missing_datavalue_statement_count)
    unsupported_pair_rate = (unsupported_statement_count / supported_denominator) if supported_denominator else 0.0

    pair_rows = [
        {"datatype": k[0], "value_type": k[1], "count": v}
        for k, v in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    summary = {
        "generated_at": _now_utc(),
        "entity_count": len(entities),
        "statement_count": total_statements,
        "missing_datavalue_statement_count": missing_datavalue_statement_count,
        "datatype_counts": dict(datatype_counts),
        "value_type_counts": dict(value_type_counts),
        "pair_counts": {f"{k[0]}|{k[1]}": v for k, v in pair_counts.items()},
        "unsupported_pairs": unsupported_pairs_global,
        "unsupported_statement_count": unsupported_statement_count,
        "unsupported_pair_rate": unsupported_pair_rate,
        "unsupported_pair_threshold": unsupported_pair_threshold,
        "overall_status": "blocked_by_policy" if unsupported_pair_rate > unsupported_pair_threshold else "pass",
        "rank_counts": dict(rank_counts),
        "top_properties": [
            {"property": prop, "count": cnt} for prop, cnt in property_counts.most_common(30)
        ],
    }

    return summary, by_entity_rows, pair_rows


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-report", help="Backlink harvest report JSON.")
    parser.add_argument(
        "--source-section",
        choices=["accepted", "rejected", "all"],
        default="accepted",
        help="Section to read from report (default: accepted).",
    )
    parser.add_argument("--qid", action="append", help="Explicit QID (repeatable).")
    parser.add_argument("--qids-file", help="Path to QID list file or CSV with `qid` column.")
    parser.add_argument("--output-prefix", help="Output path prefix (without suffixes).")
    parser.add_argument("--timeout-s", type=int, default=45, help="HTTP timeout in seconds.")
    parser.add_argument("--batch-size", type=int, default=40, help="Batch size for wbgetentities.")
    parser.add_argument("--sleep-ms", type=int, default=50, help="Delay between API batches.")
    parser.add_argument(
        "--unsupported-pair-threshold",
        type=float,
        default=0.10,
        help="Policy gate threshold for unsupported datatype pairs.",
    )
    args = parser.parse_args()

    qids: List[str] = []
    seed_qid = ""

    if args.input_report:
        report_path = Path(args.input_report)
        if not report_path.exists():
            raise FileNotFoundError(report_path)
        seed_qid, report_qids = _load_qids_from_report(report_path, args.source_section)
        qids.extend(report_qids)

    for raw_qid in args.qid or []:
        qids.append(_normalize_qid(raw_qid))

    if args.qids_file:
        qids_file = Path(args.qids_file)
        if not qids_file.exists():
            raise FileNotFoundError(qids_file)
        qids.extend(_load_qids_from_file(qids_file))

    deduped_qids = sorted({q.strip().upper() for q in qids if QID_RE.fullmatch((q or "").strip().upper())}, key=lambda x: int(x[1:]))
    if not deduped_qids:
        raise RuntimeError("No valid QIDs provided.")

    entities = _fetch_entities_claims(
        qids=deduped_qids,
        timeout_s=max(1, args.timeout_s),
        batch_size=max(1, args.batch_size),
        sleep_ms=max(0, args.sleep_ms),
    )

    summary, by_entity_rows, pair_rows = _profile_entities(
        entities=entities,
        unsupported_pair_threshold=args.unsupported_pair_threshold,
    )

    summary["source"] = {
        "input_report": args.input_report or "",
        "source_section": args.source_section if args.input_report else "",
        "seed_qid": seed_qid,
        "requested_qid_count": len(deduped_qids),
        "resolved_entity_count": len(entities),
    }

    if args.output_prefix:
        prefix = Path(args.output_prefix)
    else:
        base_dir = Path("JSON/wikidata/backlinks")
        base_dir.mkdir(parents=True, exist_ok=True)
        if seed_qid:
            prefix = base_dir / f"{seed_qid}_backlink_profile_{args.source_section}"
        else:
            prefix = base_dir / "backlink_profile"

    summary_path = Path(f"{prefix}_summary.json")
    by_entity_path = Path(f"{prefix}_by_entity.csv")
    pair_counts_path = Path(f"{prefix}_pair_counts.csv")

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_csv(by_entity_path, by_entity_rows)
    _write_csv(pair_counts_path, pair_rows)

    print(f"qids_requested={len(deduped_qids)}")
    print(f"entities_resolved={len(entities)}")
    print(f"statements={summary['statement_count']}")
    print(f"unsupported_pair_rate={summary['unsupported_pair_rate']:.6f}")
    print(f"overall_status={summary['overall_status']}")
    print(f"summary={summary_path}")
    print(f"by_entity={by_entity_path}")
    print(f"pair_counts={pair_counts_path}")


if __name__ == "__main__":
    main()
