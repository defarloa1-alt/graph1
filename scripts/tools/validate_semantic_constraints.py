#!/usr/bin/env python3
"""Deterministic SHACL/RDFS-lite semantic constraint validator scaffold.

This runner executes a small v1 check pack over JSON input and writes a
deterministic JSON report for policy-gate review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


CONTRACT_VERSION = "semantic_constraint_report_v1"
VALIDATOR_VERSION = "0.1.0-scaffold"
CONSTRAINT_PACK_ID = "shacl_rdfs_lite_v1"
DEFAULT_OUTPUT = Path("JSON/reports/semantic_constraints_report.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON input file. If omitted, a deterministic fixture is used.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path for JSON validation report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when one or more ERROR checks fail.",
    )
    return parser.parse_args()


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(payload.encode("utf-8")).hexdigest()


def default_fixture() -> Dict[str, Any]:
    return {
        "humans": [{"id_hash": "hum_001", "qid": "Q42"}, {"id_hash": "hum_002", "qid": "Q1"}],
        "claims": [{"claim_id": "clm_001"}, {"claim_id": "clm_002"}],
        "subject_concepts": [{"subject_id": "subj_001"}],
        "events": [
            {"event_id": "evt_001", "start_year": -44, "end_year": -44},
            {"event_id": "evt_002", "start_year": 10, "end_year": 12},
        ],
    }


def load_input(path: Path | None) -> Dict[str, Any]:
    if path is None:
        return default_fixture()
    raw = path.read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object")
    return payload


def rows_for(data: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _unique_non_null(rows: Iterable[Dict[str, Any]], field: str) -> Tuple[int, List[str]]:
    seen: set[str] = set()
    reasons: List[str] = []
    fail_count = 0
    for row in rows:
        val = row.get(field)
        if val is None or str(val).strip() == "":
            fail_count += 1
            reasons.append(f"{field}_missing")
            continue
        sval = str(val)
        if sval in seen:
            fail_count += 1
            reasons.append(f"{field}_duplicate")
            continue
        seen.add(sval)
    return fail_count, sorted(set(reasons))


def check_identity_unique(
    *,
    check_id: str,
    family: str,
    severity: str,
    rows: List[Dict[str, Any]],
    field: str,
) -> Dict[str, Any]:
    fail_count, reason_codes = _unique_non_null(rows, field)
    status = "PASS" if fail_count == 0 else "FAIL"
    return {
        "check_id": check_id,
        "family": family,
        "severity": severity,
        "status": status,
        "failure_count": fail_count,
        "reason_codes": reason_codes,
    }


def check_temporal_bounds(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    fail_count = 0
    reason_codes: set[str] = set()
    for row in events:
        start = row.get("start_year")
        end = row.get("end_year")
        if start is None or end is None:
            continue
        try:
            if float(start) > float(end):
                fail_count += 1
                reason_codes.add("start_after_end")
        except (TypeError, ValueError):
            fail_count += 1
            reason_codes.add("invalid_temporal_numeric")
    return {
        "check_id": "SHACL-TEMP-001",
        "family": "Temporal",
        "severity": "ERROR",
        "status": "PASS" if fail_count == 0 else "FAIL",
        "failure_count": fail_count,
        "reason_codes": sorted(reason_codes),
    }


def _collect_wikidata_ids(data: Dict[str, Any]) -> List[str]:
    ids: List[str] = []
    for key in ("humans", "events", "places", "claims", "subject_concepts"):
        for row in rows_for(data, key):
            if "qid" in row:
                ids.append(str(row.get("qid")))
            for auth in row.get("authority_ids", []) if isinstance(row.get("authority_ids"), list) else []:
                if isinstance(auth, dict) and str(auth.get("authority", "")).lower() == "wikidata":
                    ids.append(str(auth.get("id", "")))
    return ids


def check_wikidata_id_format(data: Dict[str, Any]) -> Dict[str, Any]:
    pattern = re.compile(r"^Q[1-9][0-9]*$")
    fail_count = 0
    reason_codes: set[str] = set()
    for qid in _collect_wikidata_ids(data):
        if qid.strip() == "":
            continue
        if not pattern.match(qid):
            fail_count += 1
            reason_codes.add("wikidata_id_format_invalid")
    return {
        "check_id": "SHACL-AUTH-001",
        "family": "Authority",
        "severity": "ERROR",
        "status": "PASS" if fail_count == 0 else "FAIL",
        "failure_count": fail_count,
        "reason_codes": sorted(reason_codes),
    }


def run_checks(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    checks = [
        check_identity_unique(
            check_id="SHACL-IDENT-001",
            family="Identity",
            severity="ERROR",
            rows=rows_for(data, "humans"),
            field="id_hash",
        ),
        check_identity_unique(
            check_id="SHACL-IDENT-002",
            family="Identity",
            severity="ERROR",
            rows=rows_for(data, "claims"),
            field="claim_id",
        ),
        check_identity_unique(
            check_id="SHACL-IDENT-003",
            family="Identity",
            severity="ERROR",
            rows=rows_for(data, "subject_concepts"),
            field="subject_id",
        ),
        check_temporal_bounds(rows_for(data, "events")),
        check_wikidata_id_format(data),
    ]
    return sorted(checks, key=lambda row: row["check_id"])


def summarize(checks: List[Dict[str, Any]]) -> Dict[str, int]:
    errors = 0
    warnings = 0
    passes = 0
    for row in checks:
        if row["status"] == "PASS":
            passes += 1
            continue
        if row["severity"] == "ERROR":
            errors += 1
        elif row["severity"] == "WARN":
            warnings += 1
    return {
        "checks_executed": len(checks),
        "errors": errors,
        "warnings": warnings,
        "passes": passes,
    }


def build_report(data: Dict[str, Any], checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    input_hash = stable_hash(data)
    check_ids = [row["check_id"] for row in checks]
    run_fingerprint = stable_hash(
        {
            "input_hash": input_hash,
            "constraint_pack_id": CONSTRAINT_PACK_ID,
            "check_ids": check_ids,
            "validator_version": VALIDATOR_VERSION,
        }
    )
    return {
        "metadata_header": {
            "contract_version": CONTRACT_VERSION,
            "validator_version": VALIDATOR_VERSION,
            "constraint_pack_id": CONSTRAINT_PACK_ID,
            "run_fingerprint": run_fingerprint,
            "input_hash": input_hash,
            "determinism_mode": "strict_input_hash",
        },
        "summary": summarize(checks),
        "checks": checks,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    data = load_input(args.input)
    checks = run_checks(data)
    report = build_report(data, checks)
    write_json(args.output, report)
    print(f"artifact={args.output.as_posix()}")
    print(f"run_fingerprint={report['metadata_header']['run_fingerprint']}")
    print(
        "summary="
        f"checks_executed:{report['summary']['checks_executed']},"
        f"errors:{report['summary']['errors']},"
        f"warnings:{report['summary']['warnings']},"
        f"passes:{report['summary']['passes']}"
    )
    if args.strict and report["summary"]["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
