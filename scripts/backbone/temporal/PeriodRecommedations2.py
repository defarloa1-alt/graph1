#!/usr/bin/env python3
"""
Compatibility helper for period modeling recommendations.

The detailed recommendation document lives at:
Temporal/PeriodRecommendations.md
"""

import argparse
from pathlib import Path


def resolve_recommendations_doc() -> Path:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    return project_root / "Temporal" / "PeriodRecommendations.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Show period modeling recommendation doc location.")
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print the recommendation markdown content to stdout.",
    )
    args = parser.parse_args()

    doc_path = resolve_recommendations_doc()
    if not doc_path.exists():
        print(f"Recommendation file not found: {doc_path}")
        return 1

    print(f"Recommendation file: {doc_path}")
    if args.print:
        print("\n" + "=" * 80)
        print(doc_path.read_text(encoding="utf-8", errors="replace"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
