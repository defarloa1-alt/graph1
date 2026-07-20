#!/usr/bin/env python3
"""Domain agent — single CLI entry (Chrystal 2).

Subcommands:
  bootstrap   biblio + PeriodO propose → optional review → optional write
  schema-apply  (thin wrapper note — use apply_schema.py until folded)

Usage (repo root):
  python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --dry-run
  python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --review-only
  python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --review-write
  python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --dry-run --reuse-plan
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_bootstrap_plan import run_bootstrap


def cmd_bootstrap(args: argparse.Namespace) -> int:
    modes = sum(bool(x) for x in (args.dry_run, args.review_only, args.review_write))
    if modes != 1:
        print("bootstrap: use exactly one of --dry-run / --review-only / --review-write")
        return 2
    mode = (
        "review_write"
        if args.review_write
        else "review_only"
        if args.review_only
        else "dry_run"
    )
    result = run_bootstrap(
        qid=args.qid,
        domain_id=args.domain_id,
        mode=mode,
        model=args.model,
        reuse_plan=args.reuse_plan,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Chrystal 2 Domain pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("bootstrap", help="Biblio + PeriodO via one propose/review/write")
    b.add_argument("--qid", required=True)
    b.add_argument("--domain-id", required=True)
    b.add_argument("--dry-run", action="store_true")
    b.add_argument("--review-only", action="store_true")
    b.add_argument("--review-write", action="store_true")
    b.add_argument(
        "--reuse-plan",
        action="store_true",
        help="Skip LLM propose; reuse packs/{qid}_domain_bootstrap_plan.json",
    )
    b.add_argument("--model", default="claude-sonnet-4-5")
    b.set_defaults(func=cmd_bootstrap)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
