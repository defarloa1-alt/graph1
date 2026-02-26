#!/usr/bin/env python3
"""
reresolve_anchors.py
--------------------
Re-resolve failed anchors from a validation report. Only processes concepts that
failed validation (ROOT_FALLBACK, PLACEHOLDER_QID, LOW_CONFIDENCE) — curated and
passed anchors are left unchanged.

Uses failure-aware prompts: tells the model why the previous attempt failed.

Usage:
    python scripts/backbone/subject/reresolve_anchors.py \
        --validation-report output/subject_concepts/anchor_validation_report.json \
        --anchors output/subject_concepts/subject_concept_wikidata_anchors.json \
        --root-qid Q17167 \
        --output output/subject_concepts/subject_concept_wikidata_anchors.json

Pipeline: resolve -> validate -> re-resolve (failures only) -> validate -> write-back
"""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

# Add project root for imports
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.config_loader import PERPLEXITY_API_KEY
except ImportError:
    import os
    PERPLEXITY_API_KEY = os.getenv("PPLX_API_KEY") or os.getenv("PERPLEXITY_API_KEY")


# Re-resolution issue codes (exclude NO_MATCH, LABEL_MISMATCH — manual curation)
RE_RESOLVE_CODES = {"ROOT_FALLBACK", "PLACEHOLDER_QID", "QID_NOT_FOUND", "LOW_CONFIDENCE"}


def build_failure_aware_prompt(
    label: str,
    code: str,
    root_qid: str,
    domain: str = "Roman Republic",
) -> str:
    """Build a prompt that explains why the previous attempt failed."""
    base = f"""Given this historiography research theme from {domain}:

Label: "{label}"

"""
    if code == "ROOT_FALLBACK":
        base += f"""Previous attempt returned {root_qid} (the domain root entity) - this is too broad.
Find a MORE SPECIFIC Wikidata entity that anchors this theme. Do NOT return {root_qid}.
"""
    elif code == "PLACEHOLDER_QID":
        base += """Previous attempt returned a placeholder or non-existent QID.
Find a REAL Wikidata entity that exists and anchors this theme.
"""
    elif code == "QID_NOT_FOUND":
        base += """Previous attempt returned a QID that does not exist in Wikidata.
Find a REAL, existing Wikidata entity that anchors this theme.
"""
    elif code == "LOW_CONFIDENCE":
        base += """Previous attempt had low confidence.
Find a more precise, well-matched Wikidata entity for this theme.
"""
    else:
        base += "Find the single best Wikidata entity (QID) that anchors this theme.\n"

    base += """
Prefer:
- Specific concepts (e.g. Roman Senate, Punic Wars, ager publicus)
- Over broad categories (e.g. "history", "war")
- Entities with rich Wikidata coverage (P31, P361, P17, P585)

Return ONLY valid JSON, no other text:
{"qid": "Q12345", "label": "Exact Wikidata label", "confidence": 0.0-1.0}

If no suitable Wikidata entity exists, return: {"qid": null, "label": null, "confidence": 0.0}
"""
    return base


def perplexity_reresolve(label: str, prompt: str) -> dict | None:
    """Call Perplexity with the failure-aware prompt."""
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_perplexity_key_here":
        return None
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a scholarly historian. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        data = json.loads(content)
        if data.get("qid") and data.get("confidence", 0) >= 0.5:
            return {"qid": data["qid"], "label": data.get("label"), "confidence": data.get("confidence", 0.7)}
        return None
    except Exception as e:
        print(f"  [Perplexity ERROR] {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Re-resolve failed anchors from validation report (failure-aware prompts)"
    )
    parser.add_argument(
        "--validation-report", "-v", required=True,
        help="Path to anchor_validation_report.json",
    )
    parser.add_argument(
        "--anchors", "-a", required=True,
        help="Path to subject_concept_wikidata_anchors.json (original)",
    )
    parser.add_argument(
        "--root-qid", "-r", required=True,
        help="Root QID (e.g. Q17167) — used in ROOT_FALLBACK prompt",
    )
    parser.add_argument(
        "--domain", "-d", default="Roman Republic",
        help="Domain context for prompts",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output path (default: overwrite --anchors)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be re-resolved, do not call Perplexity",
    )
    args = parser.parse_args()

    # Load validation report
    report_path = Path(args.validation_report)
    if not report_path.exists():
        print(f"Error: validation report not found: {report_path}", file=sys.stderr)
        sys.exit(1)
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    # Load original anchors
    anchors_path = Path(args.anchors)
    if not anchors_path.exists():
        print(f"Error: anchors file not found: {anchors_path}", file=sys.stderr)
        sys.exit(1)
    with open(anchors_path, encoding="utf-8") as f:
        anchors = json.load(f)

    # Normalise anchors to list of dicts keyed by subject_id
    if isinstance(anchors, dict) and "anchors" not in anchors:
        anchors_list = [{"subject_id": k, **v} for k, v in anchors.items()]
    elif isinstance(anchors, dict):
        anchors_list = anchors["anchors"]
    else:
        anchors_list = anchors

    anchors_by_id = {a["subject_id"]: a for a in anchors_list}

    # Partition: re-resolution candidates from failures + LOW_CONFIDENCE warnings
    to_reresolve = []
    for item in report.get("failures", []):
        if item.get("code") in RE_RESOLVE_CODES:
            to_reresolve.append({
                "subject_id": item["subject_id"],
                "label": item.get("label", ""),
                "code": item["code"],
            })
    for item in report.get("warnings", []):
        if item.get("code") == "LOW_CONFIDENCE":
            to_reresolve.append({
                "subject_id": item["subject_id"],
                "label": item.get("label", ""),
                "code": item["code"],
            })

    # Dedupe (LOW_CONFIDENCE might also be in failures as ROOT_FALLBACK)
    seen = set()
    unique = []
    for r in to_reresolve:
        if r["subject_id"] not in seen:
            seen.add(r["subject_id"])
            unique.append(r)

    print("=" * 70)
    print("RE-RESOLUTION: Failure-aware Perplexity pass")
    print("=" * 70)
    print(f"Validation report: {report_path}")
    print(f"Anchors: {anchors_path}")
    print(f"Re-resolution candidates: {len(unique)}")
    for r in unique:
        print(f"  - {r['subject_id']} [{r['code']}]: {r['label'][:50]}...")
    print()

    if args.dry_run:
        print("Dry run - no Perplexity calls.")
        return

    if not unique:
        print("Nothing to re-resolve.")
        sys.exit(0)

    # Re-resolve each
    updates = {}
    for i, item in enumerate(unique, 1):
        subject_id = item["subject_id"]
        label = item["label"]
        code = item["code"]
        print(f"[{i}/{len(unique)}] {subject_id} [{code}]")
        prompt = build_failure_aware_prompt(label, code, args.root_qid, args.domain)
        result = perplexity_reresolve(label, prompt)
        if result:
            updates[subject_id] = {
                "anchor_qid": result["qid"],
                "anchor_label": result.get("label"),
                "confidence": f"llm:{result.get('confidence', 0.7):.2f}",
            }
            print(f"  -> {result['qid']} ({result.get('label', '')}) [re-resolved]")
        else:
            print(f"  -> [no match]")
        time.sleep(1)  # Perplexity rate limit

    # Merge back into anchors
    for a in anchors_list:
        if a["subject_id"] in updates:
            a["anchor_qid"] = updates[a["subject_id"]]["anchor_qid"]
            a["anchor_label"] = updates[a["subject_id"]]["anchor_label"]
            a["confidence"] = updates[a["subject_id"]]["confidence"]

    # Output
    out_path = Path(args.output) if args.output else anchors_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(anchors_list, f, indent=2)

    print()
    print(f"Updated {len(updates)} anchors. Output: {out_path}")
    print("Run validate_anchors again to check.")


if __name__ == "__main__":
    main()
