#!/usr/bin/env python3
"""
Batch runner for DI training across all facet packs.

Runs train.py for each routed facet pack that hasn't been trained yet.
Supports --fetch-only (corpus only, no Claude API cost) and full training.

Usage:
  # Corpus fetch only (free, no LLM):
  python scripts/agents/domain_initiator/batch_train.py --fetch-only

  # Full training (Claude API calls):
  python scripts/agents/domain_initiator/batch_train.py

  # Specific facets:
  python scripts/agents/domain_initiator/batch_train.py --facets political,economic,social

  # Force re-train already-trained facets:
  python scripts/agents/domain_initiator/batch_train.py --force
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def find_packs(route_dir: Path, seed: str) -> list[Path]:
    """Find all facet pack files for a seed."""
    packs = sorted(route_dir.glob(f"{seed}_*_pack.json"))
    # Exclude dispatch_report
    return [p for p in packs if "dispatch_report" not in p.name]


def facet_from_pack(pack_path: Path) -> str:
    """Extract facet key from pack filename."""
    # Q17167_military_pack.json -> military
    name = pack_path.stem  # Q17167_military_pack
    parts = name.split("_")
    # Remove seed prefix and _pack suffix
    return "_".join(parts[1:-1])


def is_trained(training_dir: Path, seed: str, facet: str) -> bool:
    """Check if a training output already exists."""
    training_file = training_dir / f"{seed}_{facet.upper()}_training.json"
    if not training_file.exists():
        return False
    try:
        with open(training_file) as f:
            data = json.load(f)
        # Check it's a valid training output (not an error stub)
        return "error" not in data and (
            data.get("insights") or data.get("training_insights") or data.get("training_summary")
        )
    except (json.JSONDecodeError, KeyError):
        return False


def run_train(pack_path: Path, output_dir: Path, fetch_only: bool = False) -> bool:
    """Run train.py for a single pack. Returns True on success."""
    cmd = [
        sys.executable, str(ROOT / "scripts" / "agents" / "domain_initiator" / "train.py"),
        "--pack", str(pack_path),
        "--output", str(output_dir),
    ]
    if fetch_only:
        cmd.append("--fetch-only")

    print(f"\n{'='*60}")
    print(f"Training: {pack_path.name}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, cwd=str(ROOT), timeout=300)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {pack_path.name}")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="Q17167", help="Seed QID")
    parser.add_argument("--route-dir", type=Path, default=ROOT / "output" / "di_route")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "di_training")
    parser.add_argument("--fetch-only", action="store_true",
                        help="Corpus fetch only (no Claude API calls)")
    parser.add_argument("--facets", type=str, default=None,
                        help="Comma-separated facets to train (default: all untrained)")
    parser.add_argument("--force", action="store_true",
                        help="Re-train already-trained facets")
    args = parser.parse_args()

    packs = find_packs(args.route_dir, args.seed)
    if not packs:
        print(f"No packs found in {args.route_dir} for seed {args.seed}")
        return

    # Filter to requested facets
    if args.facets:
        requested = {f.strip().lower() for f in args.facets.split(",")}
        packs = [p for p in packs if facet_from_pack(p) in requested]

    # Skip already-trained unless --force
    if not args.force:
        untrained = []
        for p in packs:
            facet = facet_from_pack(p)
            if is_trained(args.output, args.seed, facet):
                print(f"  Skip {facet} (already trained)")
            else:
                untrained.append(p)
        packs = untrained

    if not packs:
        print("All facets already trained. Use --force to re-train.")
        return

    print(f"\nWill train {len(packs)} facets: {', '.join(facet_from_pack(p) for p in packs)}")
    mode = "FETCH-ONLY (no API cost)" if args.fetch_only else "FULL (Claude API calls)"
    print(f"Mode: {mode}")

    args.output.mkdir(parents=True, exist_ok=True)

    succeeded = 0
    failed = 0
    for pack in packs:
        ok = run_train(pack, args.output, args.fetch_only)
        if ok:
            succeeded += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Batch complete: {succeeded} succeeded, {failed} failed out of {len(packs)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
