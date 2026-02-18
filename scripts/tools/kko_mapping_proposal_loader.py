#!/usr/bin/env python3
"""Build proposal-only KKO mapping artifacts from crosswalk CSV.

This tool does not write to Neo4j or mutate canonical graph data.
It converts crosswalk rows into review-ready proposal payloads.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


ALLOWED_MATCH_TYPES = {"exact", "narrow", "broad", "related"}


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_analysis_run_id(prefix: str = "kko_map") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{stamp}"


def parse_float(value: str) -> float:
    return float((value or "").strip())


def safe_text(row: Dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def stable_id(row: Dict[str, str]) -> str:
    payload = "|".join(
        [
            safe_text(row, "source_system"),
            safe_text(row, "source_uri"),
            safe_text(row, "kko_label"),
            safe_text(row, "target_label"),
            safe_text(row, "match_type").lower(),
        ]
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"kko_map_{digest}"


def recommend_gate(match_type: str, confidence: float, review_status: str, target_label: str) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    mtype = (match_type or "").lower().strip()
    status = (review_status or "").lower().strip()

    if not target_label:
        reasons.append("TARGET_SCHEMA_MISMATCH")
        return "needs_schema_decision", reasons

    if status in {"needs_schema_decision", "blocked"}:
        reasons.append("TARGET_SCHEMA_MISMATCH")
        return "needs_schema_decision", reasons

    if confidence < 0.60:
        reasons.append("CONFIDENCE_BELOW_THRESHOLD")
        return "reject", reasons

    if mtype == "related":
        reasons.append("MATCH_TYPE_UNJUSTIFIED")
        return "proposal_only", reasons

    if mtype == "exact" and confidence >= 0.90:
        return "fast_track_review", reasons

    if mtype == "exact" and confidence >= 0.75:
        return "standard_review", reasons

    if mtype == "narrow" and confidence >= 0.75:
        reasons.append("APPROVED_WITH_CONSTRAINTS")
        return "standard_review", reasons

    if mtype == "broad" and confidence >= 0.75:
        reasons.append("APPROVED_WITH_CONSTRAINTS")
        return "review_with_constraints", reasons

    reasons.append("CONFIDENCE_BELOW_THRESHOLD")
    return "reject", reasons


def row_warnings(row: Dict[str, str], confidence: float) -> List[str]:
    warnings: List[str] = []
    source_uri = safe_text(row, "source_uri")
    match_type = safe_text(row, "match_type").lower()

    if source_uri.startswith("TODO:") or not source_uri:
        warnings.append("source_uri_not_stable")
    if match_type not in ALLOWED_MATCH_TYPES:
        warnings.append("match_type_invalid")
    if confidence < 0.0 or confidence > 1.0:
        warnings.append("confidence_out_of_range")
    return warnings


def load_crosswalk(path: Path, analysis_run_id: str) -> Dict[str, Any]:
    proposals: List[Dict[str, Any]] = []
    invalid_rows: List[Dict[str, Any]] = []
    counters = Counter()

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            try:
                confidence = parse_float(safe_text(row, "mapping_confidence"))
            except Exception:
                invalid_rows.append(
                    {
                        "line": idx,
                        "reason": "invalid_mapping_confidence",
                        "row": row,
                    }
                )
                counters["invalid_rows"] += 1
                continue

            match_type = safe_text(row, "match_type").lower()
            review_status = safe_text(row, "review_status")
            target_label = safe_text(row, "target_label")
            recommendation, reason_codes = recommend_gate(
                match_type=match_type,
                confidence=confidence,
                review_status=review_status,
                target_label=target_label,
            )
            warnings = row_warnings(row, confidence)

            proposal = {
                "proposal_id": stable_id(row),
                "analysis_run_id": analysis_run_id,
                "source_system": safe_text(row, "source_system"),
                "source_uri": safe_text(row, "source_uri"),
                "kko_label": safe_text(row, "kko_label"),
                "target_label": target_label,
                "cidoc_class": safe_text(row, "cidoc_class"),
                "crminf_pattern": safe_text(row, "crminf_pattern"),
                "match_type": match_type,
                "mapping_confidence": round(confidence, 4),
                "evidence": safe_text(row, "evidence"),
                "review_status": review_status,
                "gate_recommendation": recommendation,
                "reason_codes": reason_codes,
                "warnings": warnings,
                "notes": safe_text(row, "notes"),
                "created_at": now_utc_iso(),
                "mutation_policy": "proposal_only_non_mutating",
            }
            proposals.append(proposal)
            counters["rows_total"] += 1
            counters[f"match_type_{match_type}"] += 1
            counters[f"gate_{recommendation}"] += 1
            if warnings:
                counters["rows_with_warnings"] += 1

    return {
        "proposals": proposals,
        "invalid_rows": invalid_rows,
        "counters": dict(counters),
    }


def build_payload(crosswalk_path: Path, analysis_run_id: str, loaded: Dict[str, Any]) -> Dict[str, Any]:
    proposals = loaded["proposals"]
    invalid_rows = loaded["invalid_rows"]
    counters = loaded["counters"]

    return {
        "generated_at": now_utc_iso(),
        "tool": "kko_mapping_proposal_loader",
        "mode": "proposal_only_non_mutating",
        "analysis_run_id": analysis_run_id,
        "source_crosswalk": str(crosswalk_path.as_posix()),
        "summary": {
            "rows_total": counters.get("rows_total", 0),
            "rows_with_warnings": counters.get("rows_with_warnings", 0),
            "invalid_rows": len(invalid_rows),
            "match_type_counts": {
                "exact": counters.get("match_type_exact", 0),
                "narrow": counters.get("match_type_narrow", 0),
                "broad": counters.get("match_type_broad", 0),
                "related": counters.get("match_type_related", 0),
            },
            "gate_recommendation_counts": {
                "fast_track_review": counters.get("gate_fast_track_review", 0),
                "standard_review": counters.get("gate_standard_review", 0),
                "review_with_constraints": counters.get("gate_review_with_constraints", 0),
                "proposal_only": counters.get("gate_proposal_only", 0),
                "needs_schema_decision": counters.get("gate_needs_schema_decision", 0),
                "reject": counters.get("gate_reject", 0),
            },
        },
        "invalid_rows": invalid_rows,
        "mapping_proposals": proposals,
        "notes": [
            "This artifact is proposal-only and non-mutating.",
            "Canonical updates require explicit policy-gate approval.",
        ],
    }


def write_markdown_summary(payload: Dict[str, Any], path: Path) -> None:
    summary = payload.get("summary", {})
    proposals = payload.get("mapping_proposals", []) or []
    lines: List[str] = []
    lines.append("# KKO Mapping Proposal Summary")
    lines.append("")
    lines.append(f"- Generated at: `{payload.get('generated_at')}`")
    lines.append(f"- Analysis run: `{payload.get('analysis_run_id')}`")
    lines.append(f"- Source crosswalk: `{payload.get('source_crosswalk')}`")
    lines.append(f"- Mode: `{payload.get('mode')}`")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append(f"- Rows: `{summary.get('rows_total', 0)}`")
    lines.append(f"- Rows with warnings: `{summary.get('rows_with_warnings', 0)}`")
    lines.append(f"- Invalid rows: `{summary.get('invalid_rows', 0)}`")
    lines.append("")
    lines.append("## Gate Recommendations")
    lines.append("")
    for key, value in (summary.get("gate_recommendation_counts", {}) or {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Sample Proposals")
    lines.append("")
    lines.append("| proposal_id | kko_label | target_label | match_type | confidence | gate_recommendation | review_status |")
    lines.append("|---|---|---|---|---:|---|---|")
    for p in proposals[:20]:
        lines.append(
            f"| `{p.get('proposal_id','')}` | `{p.get('kko_label','')}` | `{p.get('target_label','')}` | "
            f"`{p.get('match_type','')}` | `{p.get('mapping_confidence','')}` | "
            f"`{p.get('gate_recommendation','')}` | `{p.get('review_status','')}` |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for n in payload.get("notes", []) or []:
        lines.append(f"- {n}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--crosswalk",
        default="CSV/kko_chrystallum_crosswalk.csv",
        help="Path to KKO crosswalk CSV.",
    )
    parser.add_argument(
        "--analysis-run-id",
        default="",
        help="Optional run id; autogenerated if omitted.",
    )
    parser.add_argument(
        "--out-prefix",
        default="",
        help="Output prefix path without extension. Default: JSON/kbpedia/proposals/<analysis_run_id>_kko_mapping_proposal",
    )
    args = parser.parse_args()

    crosswalk_path = Path(args.crosswalk)
    if not crosswalk_path.exists():
        raise FileNotFoundError(f"Crosswalk not found: {crosswalk_path}")

    analysis_run_id = args.analysis_run_id.strip() or make_analysis_run_id()
    default_prefix = Path(f"JSON/kbpedia/proposals/{analysis_run_id}_kko_mapping_proposal")
    out_prefix = Path(args.out_prefix) if args.out_prefix else default_prefix
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    loaded = load_crosswalk(crosswalk_path, analysis_run_id)
    payload = build_payload(crosswalk_path, analysis_run_id, loaded)

    json_path = out_prefix.with_suffix(".json")
    md_path = out_prefix.with_suffix(".md")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_summary(payload, md_path)

    summary = payload.get("summary", {})
    print("KBPEDIA KKO MAPPING PROPOSAL LOADER")
    print(f"Analysis run id: {analysis_run_id}")
    print(f"Rows processed: {summary.get('rows_total', 0)}")
    print(f"Invalid rows: {summary.get('invalid_rows', 0)}")
    print(f"JSON output: {json_path}")
    print(f"Markdown output: {md_path}")
    print("Mode: proposal_only_non_mutating")


if __name__ == "__main__":
    main()
