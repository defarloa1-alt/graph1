from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize legacy LCC->FAST seed mappings."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("Facets/lcc_fast_seed_mappings_legacy.json"),
        help="Path to seed mapping JSON.",
    )
    return parser.parse_args()


def summarize(path: Path) -> None:
    payload: dict[str, list[dict[str, Any]]] = json.loads(path.read_text(encoding="utf-8"))

    total_groups = len(payload)
    total_links = sum(len(v) for v in payload.values())

    facet_counter: Counter[str] = Counter()
    confidence_counter: Counter[str] = Counter()
    class_letter_counter: Counter[str] = Counter()

    for lcc_code, rows in payload.items():
        if lcc_code:
            class_letter_counter[lcc_code[0]] += len(rows)
        for row in rows:
            facet_counter[str(row.get("facet_type", "unknown"))] += 1
            confidence_counter[str(row.get("confidence", "unknown"))] += 1

    print(f"file={path}")
    print(f"lcc_groups={total_groups}")
    print(f"total_links={total_links}")
    print("top_class_letters=" + ", ".join(f"{k}:{v}" for k, v in class_letter_counter.most_common(10)))
    print("facet_types=" + ", ".join(f"{k}:{v}" for k, v in facet_counter.most_common()))
    print("confidence=" + ", ".join(f"{k}:{v}" for k, v in confidence_counter.most_common()))


def main() -> None:
    args = parse_args()
    summarize(args.input)


if __name__ == "__main__":
    main()
