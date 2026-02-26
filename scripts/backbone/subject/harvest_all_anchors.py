#!/usr/bin/env python3
"""
harvest_all_anchors.py
----------------------
Wrapper that reads a validated anchor JSON file and runs
wikidata_backlink_harvest.py once per unique anchor QID.

Domain-agnostic: works for any root subject / anchor set.

Usage:
    python scripts/backbone/subject/harvest_all_anchors.py \
        --anchors output/subject_concepts/subject_concept_wikidata_anchors.json \
        --harvester scripts/tools/wikidata_backlink_harvest.py \
        --output-dir output/backlinks \
        --mode discovery \
        --sleep 1.5 \
        --skip-failures

    # Override discovery caps for a specific run:
    python scripts/backbone/subject/harvest_all_anchors.py \
        --anchors subject_concept_wikidata_anchors.json \
        --harvester scripts/tools/wikidata_backlink_harvest.py \
        --output-dir output/backlinks \
        --mode discovery \
        --max-sources 500 \
        --max-new-nodes 250 \
        --sparql-limit 1000

    # Resume after interrupt:
    python scripts/backbone/subject/harvest_all_anchors.py ... --resume

Dependencies: none beyond stdlib (subprocess, json, pathlib, time)
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


# ---------------------------------------------------------------------------
# Anchor loading + normalisation
# ---------------------------------------------------------------------------

def load_anchors(path: Path) -> list[dict]:
    """
    Accept several common anchor JSON shapes:
      A) QID-canonical: list of dicts with qid, label, domain_qid (identity = qid)
      B) Legacy: list of dicts with subject_id, anchor_qid/qid, label
      C) dict keyed by subject_id
      D) {"anchors": [...]} wrapper
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict):
        if "anchors" in raw:
            raw = raw["anchors"]
        else:
            raw = [{"subject_id": k, **v} for k, v in raw.items()]

    normalised = []
    for item in raw:
        qid = item.get("qid") or item.get("anchor_qid") or item.get("wikidata_qid")
        if not qid:
            continue  # skip unresolved
        # QID-canonical: identity is qid; legacy: subject_id
        subject_id = item.get("subject_id") or qid
        normalised.append({
            "subject_id": subject_id,
            "label": item.get("label", item.get("anchor_label", item.get("concept_label", ""))),
            "qid": qid,
            "source": item.get("source", item.get("confidence", "unknown")),
            "level": item.get("level"),
        })

    return normalised


def deduplicate_by_qid(anchors: list[dict]) -> list[dict]:
    """
    Multiple SubjectConcepts may share a QID (duplicate anchors).
    We only need to harvest each QID once - track which subject_ids share it.
    QID-canonical: subject_id = qid, so subject_ids = [qid].
    """
    qid_map: dict[str, dict] = {}
    for anchor in anchors:
        qid = anchor["qid"]
        if qid not in qid_map:
            qid_map[qid] = {
                "qid": qid,
                "subject_ids": [],
                "labels": [],
                "source": anchor["source"],
            }
        qid_map[qid]["subject_ids"].append(anchor["subject_id"])
        qid_map[qid]["labels"].append(anchor["label"])

    return list(qid_map.values())


# ---------------------------------------------------------------------------
# Harvester invocation
# ---------------------------------------------------------------------------

def build_command(
    harvester: Path,
    seed_qid: str,
    report_path: Path,
    mode: str,
    sleep_ms: int,
    max_sources: int | None,
    max_new_nodes: int | None,
    sparql_limit: int | None,
    extra_args: list[str],
) -> list[str]:
    """Build harvester subprocess command. Uses --report-path for explicit output."""
    cmd = [
        sys.executable,
        str(harvester),
        "--seed-qid", seed_qid,
        "--mode", mode,
        "--report-path", str(report_path),
        "--sleep-ms", str(sleep_ms),
    ]
    if max_sources is not None:
        cmd += ["--max-sources-per-seed", str(max_sources)]
    if max_new_nodes is not None:
        cmd += ["--max-new-nodes-per-seed", str(max_new_nodes)]
    if sparql_limit is not None:
        cmd += ["--sparql-limit", str(sparql_limit)]
    if extra_args:
        cmd += extra_args
    return cmd


def run_harvester(
    cmd: list[str],
    timeout: int = 600,
) -> tuple[bool, str]:
    """
    Run harvester subprocess. Returns (success, error_message).
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip()
        return True, ""
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Progress tracking
# ---------------------------------------------------------------------------

def load_progress(progress_file: Path) -> set[str]:
    """Return set of QIDs already successfully harvested."""
    if not progress_file.exists():
        return set()
    with open(progress_file, encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("completed", []))


def save_progress(progress_file: Path, completed: set[str], failed: dict[str, str]):
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump({
            "completed": sorted(completed),
            "failed": failed,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, f, indent=2)


# ---------------------------------------------------------------------------
# Run summary
# ---------------------------------------------------------------------------

def write_run_summary(
    output_dir: Path,
    unique_anchors: list[dict],
    completed: set[str],
    failed: dict[str, str],
    skipped: set[str],
    started_at: datetime,
    args,
) -> Path:
    """Write harvest_run_summary.json with qid->subject_ids mapping for cluster assignment."""
    qid_to_subject_ids = {a["qid"]: a["subject_ids"] for a in unique_anchors}
    summary = {
        "run_started_at": started_at.isoformat(),
        "run_finished_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "dry_run": args.dry_run,
        "total_unique_qids": len(unique_anchors),
        "completed": len(completed),
        "failed": len(failed),
        "skipped_already_done": len(skipped),
        "coverage_pct": round(len(completed) / len(unique_anchors) * 100, 1) if unique_anchors else 0,
        "failed_detail": failed,
        "completed_qids": sorted(completed),
        "qid_to_subject_ids": qid_to_subject_ids,
        "output_dir": str(output_dir),
    }
    summary_path = output_dir / "harvest_run_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run wikidata_backlink_harvest.py for all anchors in a subject concept tree"
    )
    parser.add_argument(
        "--anchors", "-a", required=True,
        help="Path to validated anchor JSON file"
    )
    parser.add_argument(
        "--harvester", required=True,
        help="Path to wikidata_backlink_harvest.py"
    )
    parser.add_argument(
        "--output-dir", "-o", default="output/backlinks",
        help="Directory for per-QID harvest reports (default: output/backlinks)"
    )
    parser.add_argument(
        "--mode", default="discovery",
        choices=["discovery", "production"],
        help="Harvester mode (default: discovery)"
    )
    parser.add_argument(
        "--sleep", type=float, default=1.5,
        help="Seconds to wait between seed QID runs (default: 1.5)"
    )
    parser.add_argument(
        "--sleep-ms", type=int, default=100,
        help="Milliseconds passed to harvester --sleep-ms (default: 100)"
    )
    parser.add_argument(
        "--max-sources", type=int, default=None,
        help="Override max_sources_per_seed"
    )
    parser.add_argument(
        "--max-new-nodes", type=int, default=None,
        help="Override max_new_nodes_per_seed"
    )
    parser.add_argument(
        "--sparql-limit", type=int, default=None,
        help="Override sparql_limit"
    )
    parser.add_argument(
        "--skip-failures", action="store_true",
        help="Continue on harvester errors rather than aborting"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip QIDs already completed in a previous run (reads harvest_progress.json)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print commands without executing"
    )
    parser.add_argument(
        "--timeout", type=int, default=600,
        help="Per-seed timeout in seconds (default: 600)"
    )
    parser.add_argument(
        "--no-verify", action="store_true",
        help="Skip pre-harvest QID verification (not recommended)"
    )
    parser.add_argument(
        "--anchor", action="append",
        help="Harvest only these QIDs (repeatable). Default: all anchors."
    )
    args, extra_args = parser.parse_known_args()

    anchors_path = Path(args.anchors)
    harvester_path = Path(args.harvester)
    output_dir = Path(args.output_dir)
    progress_file = output_dir / "harvest_progress.json"

    # Validate paths
    if not anchors_path.exists():
        print(f"Error: anchors file not found: {anchors_path}", file=sys.stderr)
        sys.exit(1)
    if not args.dry_run and not harvester_path.exists():
        print(f"Error: harvester not found: {harvester_path}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Pre-harvest verification: ensure anchor QIDs match Wikidata labels
    if not args.no_verify and not args.dry_run:
        root = Path(__file__).resolve().parents[2]
        verify_script = root / "scripts" / "analysis" / "verify_anchor_qids.py"
        if verify_script.exists():
            result = subprocess.run(
                [sys.executable, str(verify_script), "--anchors", str(anchors_path)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                print(result.stdout or result.stderr, file=sys.stderr)
                print("\nHarvest aborted: anchor QID verification failed. Fix mismatches or use --no-verify.", file=sys.stderr)
                sys.exit(1)

    # Load anchors
    raw_anchors = load_anchors(anchors_path)
    unique_anchors = deduplicate_by_qid(raw_anchors)

    # Filter to specific QIDs if --anchor given
    if args.anchor:
        anchor_set = {q.strip().upper() for q in args.anchor if q}
        unique_anchors = [a for a in unique_anchors if a["qid"] in anchor_set]
        if not unique_anchors:
            print(f"Error: no anchors match --anchor {args.anchor}", file=sys.stderr)
            sys.exit(1)
        print(f"Filtered to {len(unique_anchors)} anchor(s): {sorted(a['qid'] for a in unique_anchors)}")

    print(f"\n{'='*70}")
    print("BACKLINK HARVEST WRAPPER")
    print(f"{'='*70}")
    print(f"Anchors file : {anchors_path}")
    print(f"Total records: {len(raw_anchors)} ({len(unique_anchors)} unique QIDs)")
    print(f"Mode         : {args.mode}")
    print(f"Output dir   : {output_dir}")
    print(f"Inter-seed sleep: {args.sleep}s")
    if args.dry_run:
        print("DRY RUN - no commands will be executed")
    print(f"{'='*70}\n")

    # Resume state
    already_done: set[str] = set()
    if args.resume:
        already_done = load_progress(progress_file)
        print(f"Resume mode: {len(already_done)} QIDs already completed, skipping.\n")

    completed: set[str] = set(already_done)
    failed: dict[str, str] = {}
    skipped: set[str] = set()
    started_at = datetime.now(timezone.utc)

    for i, anchor in enumerate(unique_anchors, 1):
        qid = anchor["qid"]
        subject_ids = anchor["subject_ids"]
        labels = anchor["labels"]
        display_label = labels[0] if len(labels) == 1 else f"{labels[0]} (+{len(labels)-1} more)"

        # Resume skip
        if qid in already_done:
            skipped.add(qid)
            print(f"[{i:3}/{len(unique_anchors)}] {qid} SKIPPED (already done)")
            continue

        # Output path: QID-canonical uses {qid}_report.json; legacy used {subject_id}_{qid}_report.json
        report_path = output_dir / f"{qid}_report.json"

        # Build command
        cmd = build_command(
            harvester=harvester_path,
            seed_qid=qid,
            report_path=report_path,
            mode=args.mode,
            sleep_ms=args.sleep_ms,
            max_sources=args.max_sources,
            max_new_nodes=args.max_new_nodes,
            sparql_limit=args.sparql_limit,
            extra_args=extra_args,
        )

        print(f"[{i:3}/{len(unique_anchors)}] {qid} | {display_label}")
        if len(subject_ids) > 1:
            print(f"           Shared by: {subject_ids}")

        if args.dry_run:
            print(f"           CMD: {' '.join(cmd)}\n")
            completed.add(qid)
            continue

        # Run
        t0 = time.time()
        success, error = run_harvester(cmd, timeout=args.timeout)
        elapsed = round(time.time() - t0, 1)

        if success:
            print(f"           done in {elapsed}s -> {report_path.name}")
            completed.add(qid)
        else:
            print(f"           FAILED in {elapsed}s: {error[:120]}")
            failed[qid] = error
            if not args.skip_failures:
                print("\nAborting. Use --skip-failures to continue past errors.")
                print("Use --resume to restart from where you left off.")
                save_progress(progress_file, completed, failed)
                sys.exit(1)

        # Save progress after every seed (safe to interrupt)
        save_progress(progress_file, completed, failed)

        # Inter-seed delay (skip after last item)
        if i < len(unique_anchors):
            time.sleep(args.sleep)

    # Final summary
    summary_path = write_run_summary(
        output_dir, unique_anchors, completed, failed, skipped, started_at, args
    )

    print(f"\n{'='*70}")
    print("HARVEST COMPLETE")
    print(f"  Completed : {len(completed - skipped)}/{len(unique_anchors)} this run")
    print(f"  Skipped   : {len(skipped)} (already done)")
    print(f"  Failed    : {len(failed)}")
    coverage = round(len(completed) / len(unique_anchors) * 100, 1) if unique_anchors else 0
    print(f"  Coverage  : {coverage}%")
    print(f"  Reports   : {output_dir}/")
    print(f"  Summary   : {summary_path}")
    print(f"{'='*70}\n")

    if failed:
        print("Failed QIDs:")
        for qid, err in failed.items():
            print(f"  {qid}: {err[:100]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
