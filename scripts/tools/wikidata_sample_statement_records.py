#!/usr/bin/env python3
"""Create a flattened sample of Wikidata statements from an exported payload.

Input is the JSON produced by:
  scripts/tools/wikidata_fetch_all_statements.py

Output can be CSV or JSON.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def flatten_claims(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    qid = payload.get("qid", "")
    label = payload.get("label", "")
    claims = payload.get("claims", {})

    for prop, statement_list in claims.items():
        for statement in statement_list:
            mainsnak = statement.get("mainsnak", {})
            qualifiers = statement.get("qualifiers", {}) or {}
            references = statement.get("references", []) or []

            qualifier_count = sum(len(v) for v in qualifiers.values())
            qualifier_properties = sorted(qualifiers.keys())

            ref_props = set()
            for ref in references:
                for p in (ref.get("snaks", {}) or {}).keys():
                    ref_props.add(p)

            rows.append(
                {
                    "qid": qid,
                    "label": label,
                    "property": prop,
                    "statement_id": statement.get("statement_id", ""),
                    "rank": statement.get("rank", ""),
                    "datatype": mainsnak.get("datatype", ""),
                    "snaktype": mainsnak.get("snaktype", ""),
                    "value_type": mainsnak.get("value_type", ""),
                    "value": _to_text(mainsnak.get("value")),
                    "qualifier_count": qualifier_count,
                    "qualifier_properties": "|".join(qualifier_properties),
                    "reference_count": len(references),
                    "reference_properties": "|".join(sorted(ref_props)),
                }
            )
    return rows


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        required=True,
        help="Path to full statements JSON (from wikidata_fetch_all_statements.py).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (.csv or .json).",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Number of rows to sample (default: 100).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling.",
    )
    parser.add_argument(
        "--mode",
        choices=["random", "first"],
        default="random",
        help="Sampling mode (default: random).",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        raise FileNotFoundError(in_path)

    payload = json.loads(in_path.read_text(encoding="utf-8"))
    rows = flatten_claims(payload)
    total = len(rows)

    if args.sample_size <= 0:
        sampled = []
    elif args.sample_size >= total:
        sampled = rows
    elif args.mode == "first":
        sampled = rows[: args.sample_size]
    else:
        rng = random.Random(args.seed)
        sampled = rng.sample(rows, args.sample_size)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".csv":
        write_csv(out_path, sampled)
    else:
        out_path.write_text(json.dumps(sampled, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"input={in_path}")
    print(f"total_rows={total}")
    print(f"sample_rows={len(sampled)}")
    print(f"output={out_path}")


if __name__ == "__main__":
    main()
