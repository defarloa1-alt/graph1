#!/usr/bin/env python3
"""
validate_anchors.py
-------------------
Generic validator for Wikidata QID anchor resolution results.
Domain-agnostic: works for any root subject (Roman Republic, Silk Road, etc.)

Usage:
    python scripts/backbone/subject/validate_anchors.py \
        --input output/subject_concepts/subject_concept_wikidata_anchors.json \
        --root-qid Q17167 \
        --confidence-threshold 0.7 \
        --verify-labels \
        --output output/subject_concepts/anchor_validation_report.json

Dependencies:
    pip install requests
"""
import json
import argparse
import time
import sys
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional

import requests


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AnchorIssue:
    subject_id: str
    label: str
    qid: Optional[str]
    issue_type: str          # FAILURE | WARNING
    code: str                # machine-readable code
    message: str             # human-readable message
    detail: Optional[str] = None


@dataclass
class ValidationReport:
    root_qid: str
    total_concepts: int
    anchored: int
    unanchored: int
    curated: int
    llm_resolved: int
    coverage_pct: float
    passed: bool
    failures: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    summary: str = ""

    @property
    def failure_count(self):
        return len(self.failures)

    @property
    def warning_count(self):
        return len(self.warnings)


# ---------------------------------------------------------------------------
# Wikidata label verification
# ---------------------------------------------------------------------------

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
_wikidata_cache: dict = {}


def fetch_wikidata_label(qid: str) -> Optional[str]:
    """Fetch the canonical English label for a QID from Wikidata."""
    if qid in _wikidata_cache:
        return _wikidata_cache[qid]

    try:
        resp = requests.get(
            WIKIDATA_API,
            params={
                "action": "wbgetentities",
                "ids": qid,
                "props": "labels",
                "languages": "en",
                "format": "json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        entity = data.get("entities", {}).get(qid, {})

        if entity.get("missing") == "":
            _wikidata_cache[qid] = None
            return None

        label = entity.get("labels", {}).get("en", {}).get("value")
        _wikidata_cache[qid] = label
        return label

    except Exception as e:
        print(f"  [warn] Wikidata fetch failed for {qid}: {e}", file=sys.stderr)
        return None

    finally:
        time.sleep(0.1)  # polite rate limiting


# ---------------------------------------------------------------------------
# QID structural checks
# ---------------------------------------------------------------------------

PLACEHOLDER_PATTERNS = {
    "Q1234567",   # classic placeholder
    "Q123456",
    "Q12345",
    "Q0",
    "Q1",
    "Q2",
}

def looks_like_placeholder(qid: str) -> bool:
    """Detect obviously fake or sequential placeholder QIDs."""
    if qid in PLACEHOLDER_PATTERNS:
        return True
    # Sequential integers under Q100 are meta-entities (Wikidata itself, etc.)
    try:
        n = int(qid[1:])
        if n < 100:
            return True
    except ValueError:
        pass
    return False


# ---------------------------------------------------------------------------
# Core validator
# ---------------------------------------------------------------------------

def validate_anchors(
    anchors: list[dict],
    root_qid: str,
    confidence_threshold: float = 0.7,
    verify_labels: bool = True,
) -> ValidationReport:
    """
    Validate a list of anchor resolution records.

    Each record is expected to have:
        subject_id, label, qid (or null), confidence (0-1),
        source ("curated" | "perplexity" | "llm" | "no_match"),
        wikidata_label (optional, returned by resolver)
    """

    issues: list[AnchorIssue] = []

    total = len(anchors)
    anchored_ids = [a for a in anchors if a.get("qid")]
    unanchored_ids = [a for a in anchors if not a.get("qid")]
    curated = [a for a in anchors if a.get("source") == "curated"]
    llm_resolved = [a for a in anchors if a.get("source") not in ("curated", None)
                    and a.get("qid")]

    # -- 1. No-match concepts -------------------------------------------------
    for anchor in unanchored_ids:
        issues.append(AnchorIssue(
            subject_id=anchor["subject_id"],
            label=anchor.get("label", ""),
            qid=None,
            issue_type="WARNING",
            code="NO_MATCH",
            message="No Wikidata anchor found",
            detail="Requires manual curation or prompt refinement",
        ))

    # -- 2. Root QID fallback -------------------------------------------------
    for anchor in anchored_ids:
        if anchor["qid"] == root_qid:
            issues.append(AnchorIssue(
                subject_id=anchor["subject_id"],
                label=anchor.get("label", ""),
                qid=anchor["qid"],
                issue_type="FAILURE",
                code="ROOT_FALLBACK",
                message=f"Resolved to root QID {root_qid} - likely a fallback, not a real anchor",
                detail="LLM defaulted to the domain root rather than finding a specific entity",
            ))

    # -- 3. Placeholder QIDs --------------------------------------------------
    for anchor in anchored_ids:
        qid = anchor["qid"]
        if looks_like_placeholder(qid):
            issues.append(AnchorIssue(
                subject_id=anchor["subject_id"],
                label=anchor.get("label", ""),
                qid=qid,
                issue_type="FAILURE",
                code="PLACEHOLDER_QID",
                message=f"QID {qid} matches a known placeholder pattern",
                detail="LLM likely hallucinated this identifier",
            ))

    # -- 4. Duplicate QID assignments -----------------------------------------
    qid_to_subjects: dict[str, list[str]] = defaultdict(list)
    for anchor in anchored_ids:
        qid = anchor["qid"]
        if qid and qid != root_qid:  # root fallbacks already flagged above
            qid_to_subjects[qid].append(anchor["subject_id"])

    for qid, subjects in qid_to_subjects.items():
        if len(subjects) > 1:
            issues.append(AnchorIssue(
                subject_id=", ".join(subjects),
                label="(multiple)",
                qid=qid,
                issue_type="WARNING",
                code="DUPLICATE_ANCHOR",
                message=f"QID {qid} assigned to {len(subjects)} distinct SubjectConcepts",
                detail=f"Subjects share the same Wikidata backlink universe: {subjects}",
            ))

    # -- 5. Low confidence scores ---------------------------------------------
    for anchor in anchored_ids:
        conf = anchor.get("confidence")
        if conf is not None and conf < confidence_threshold:
            issues.append(AnchorIssue(
                subject_id=anchor["subject_id"],
                label=anchor.get("label", ""),
                qid=anchor["qid"],
                issue_type="WARNING",
                code="LOW_CONFIDENCE",
                message=f"Confidence {conf:.2f} below threshold {confidence_threshold}",
                detail="Consider manual review or re-resolution with a more specific prompt",
            ))

    # -- 6. Label mismatch (live Wikidata check) ------------------------------
    if verify_labels:
        print(f"\nVerifying labels against Wikidata ({len(anchored_ids)} QIDs)...")
        for i, anchor in enumerate(anchored_ids):
            qid = anchor["qid"]
            claimed_label = anchor.get("wikidata_label") or anchor.get("label", "")

            if not qid or looks_like_placeholder(qid):
                continue  # already flagged

            actual_label = fetch_wikidata_label(qid)

            if actual_label is None:
                issues.append(AnchorIssue(
                    subject_id=anchor["subject_id"],
                    label=claimed_label,
                    qid=qid,
                    issue_type="FAILURE",
                    code="QID_NOT_FOUND",
                    message=f"QID {qid} does not exist in Wikidata",
                    detail="Hallucinated QID - entity does not exist",
                ))
            elif (
                claimed_label
                and not str(claimed_label).strip().lower().startswith("(curated:")
                and actual_label.lower() != claimed_label.lower()
            ):
                issues.append(AnchorIssue(
                    subject_id=anchor["subject_id"],
                    label=claimed_label,
                    qid=qid,
                    issue_type="WARNING",
                    code="LABEL_MISMATCH",
                    message=f"Claimed label '{claimed_label}' != Wikidata label '{actual_label}'",
                    detail="LLM may have associated the wrong entity or used an alias",
                ))

            if (i + 1) % 10 == 0:
                print(f"  {i+1}/{len(anchored_ids)} verified...", file=sys.stderr)

    # -- 7. Specificity regression (level-based check) ------------------------
    # If a deeper concept (higher level number) resolves to the same QID
    # as a shallower parent, that's a specificity regression.
    has_levels = all(a.get("level") is not None for a in anchors)
    if has_levels:
        qid_level_map: dict[str, int] = {}
        for anchor in anchored_ids:
            qid = anchor["qid"]
            level = anchor.get("level", 0)
            if qid in qid_level_map:
                if level > qid_level_map[qid]:
                    # deeper concept resolved to same QID as shallower one
                    issues.append(AnchorIssue(
                        subject_id=anchor["subject_id"],
                        label=anchor.get("label", ""),
                        qid=qid,
                        issue_type="WARNING",
                        code="SPECIFICITY_REGRESSION",
                        message=f"Level-{level} concept resolved to same QID as a shallower concept",
                        detail="Deeper concepts should have more specific anchors than their parents",
                    ))
            else:
                qid_level_map[qid] = level

    # -- Assemble report ------------------------------------------------------
    failures = [i for i in issues if i.issue_type == "FAILURE"]
    warnings = [i for i in issues if i.issue_type == "WARNING"]

    # Real anchors = anchored minus root fallbacks and placeholders
    real_failure_subject_ids = {
        i.subject_id for i in failures
        if i.code in ("ROOT_FALLBACK", "PLACEHOLDER_QID", "QID_NOT_FOUND")
    }
    verified_anchors = len(anchored_ids) - len(real_failure_subject_ids)
    coverage_pct = round(verified_anchors / total * 100, 1) if total else 0.0

    passed = len(failures) == 0

    summary_lines = [
        f"Total concepts: {total}",
        f"Verified anchors: {verified_anchors}/{total} ({coverage_pct}%)",
        f"Curated: {len(curated)} | LLM-resolved: {len(llm_resolved)} | No-match: {len(unanchored_ids)}",
        f"Failures: {len(failures)} | Warnings: {len(warnings)}",
        f"Status: {'PASSED' if passed else 'FAILED'}",
    ]

    report = ValidationReport(
        root_qid=root_qid,
        total_concepts=total,
        anchored=len(anchored_ids),
        unanchored=len(unanchored_ids),
        curated=len(curated),
        llm_resolved=len(llm_resolved),
        coverage_pct=coverage_pct,
        passed=passed,
        failures=[asdict(f) for f in failures],
        warnings=[asdict(w) for w in warnings],
        summary="\n".join(summary_lines),
    )

    return report


# ---------------------------------------------------------------------------
# Input normalisation
# ---------------------------------------------------------------------------

def _parse_confidence(conf) -> tuple[Optional[float], str]:
    """Parse confidence and infer source. Returns (confidence_float, source)."""
    if conf is None:
        return None, "unknown"
    if isinstance(conf, (int, float)):
        return float(conf), "unknown"
    s = str(conf).lower()
    if s == "curated":
        return 1.0, "curated"
    if s == "high":
        return 0.9, "search"
    if s == "medium":
        return 0.7, "search"
    if s == "none":
        return None, "no_match"
    if s.startswith("llm:"):
        try:
            return float(s.split(":")[1]), "perplexity"
        except (IndexError, ValueError):
            return 0.7, "perplexity"
    return None, "unknown"


def normalise_anchors(raw: list[dict] | dict) -> list[dict]:
    """
    Accept several common output formats from anchor resolution scripts:

    Format A: list of dicts with subject_id, qid, label, confidence, source
    Format B: find_subject_concept_anchors output (anchor_qid, anchor_label, confidence)
    Format C: dict keyed by subject_id
    Format D: {"anchors": [...]} wrapper
    """
    if isinstance(raw, dict):
        if "anchors" in raw:
            raw = raw["anchors"]
        else:
            # keyed by subject_id
            raw = [{"subject_id": k, **v} for k, v in raw.items()]

    normalised = []
    for item in raw:
        conf_val, source = _parse_confidence(item.get("confidence", item.get("score")))
        normalised.append({
            "subject_id": item.get("subject_id", "unknown"),
            "label":       item.get("label", item.get("concept_label", "")),
            "qid":         item.get("qid") or item.get("anchor_qid") or item.get("wikidata_qid"),
            "confidence":  conf_val,
            "source":      item.get("source", item.get("resolution_source", source)),
            "wikidata_label": item.get("wikidata_label") or item.get("anchor_label"),
            "level":       item.get("level"),
        })
    return normalised


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_report(report: ValidationReport):
    sep = "=" * 70
    print(f"\n{sep}")
    print("ANCHOR VALIDATION REPORT")
    print(sep)
    print(report.summary)

    if report.failures:
        print(f"\n--- FAILURES ({report.failure_count}) ---")
        for f in report.failures:
            print(f"  [{f['code']}] {f['subject_id']}")
            print(f"    QID: {f['qid']} | {f['message']}")
            if f.get("detail"):
                print(f"    -> {f['detail']}")

    if report.warnings:
        print(f"\n--- WARNINGS ({report.warning_count}) ---")
        for w in report.warnings:
            print(f"  [{w['code']}] {w['subject_id']}")
            print(f"    QID: {w['qid']} | {w['message']}")
            if w.get("detail"):
                print(f"    -> {w['detail']}")

    print(f"\n{sep}")
    print(f"Result: {'PASSED' if report.passed else 'FAILED'}")
    print(sep)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Wikidata anchor resolutions for a SubjectConcept tree"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to anchor resolution JSON file"
    )
    parser.add_argument(
        "--root-qid", "-r", required=True,
        help="Root QID of the subject tree (e.g. Q17167). Will be flagged if used as a fallback anchor."
    )
    parser.add_argument(
        "--confidence-threshold", "-c", type=float, default=0.7,
        help="Minimum acceptable confidence score (default: 0.7)"
    )
    parser.add_argument(
        "--verify-labels", "-v", action="store_true", default=False,
        help="Live-check QID labels against Wikidata API (slower, more thorough)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Path to write JSON validation report (optional)"
    )
    args = parser.parse_args()

    # Load
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        raw = json.load(f)

    anchors = normalise_anchors(raw)
    print(f"Loaded {len(anchors)} anchor records from {input_path}")

    # Validate
    report = validate_anchors(
        anchors=anchors,
        root_qid=args.root_qid,
        confidence_threshold=args.confidence_threshold,
        verify_labels=args.verify_labels,
    )

    # Print
    print_report(report)

    # Save
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2, default=str)
        print(f"\nReport saved to: {out_path}")

    # Exit code — useful for CI pipelines
    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
