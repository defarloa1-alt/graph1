#!/usr/bin/env python3
"""Profile datatypes and value types from a full Wikidata statements export.

Input format: JSON produced by `wikidata_fetch_all_statements.py`.

Outputs:
- `<prefix>_summary.json` : aggregate datatype/value-type profile
- `<prefix>_by_property.csv` : per-property profile (counts + qualifier/reference rates)
- `<prefix>_datatype_pairs.csv` : counts by (datatype, value_type) pairs
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _as_text(value: Any, max_len: int = 140) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    return text[:max_len]


def _load_payload(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _analyze(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    claims = payload.get("claims", {})

    datatype_counter: Counter[str] = Counter()
    value_type_counter: Counter[str] = Counter()
    pair_counter: Counter[Tuple[str, str]] = Counter()
    rank_counter: Counter[str] = Counter()
    property_counter: Counter[str] = Counter()

    datatype_examples: Dict[str, List[str]] = defaultdict(list)

    by_property: Dict[str, Dict[str, Any]] = {}

    total_statements = 0
    with_qualifiers = 0
    with_references = 0

    for prop, statement_list in claims.items():
        prop_total = 0
        prop_with_qual = 0
        prop_with_ref = 0
        prop_datatypes: Counter[str] = Counter()
        prop_value_types: Counter[str] = Counter()

        for statement in statement_list:
            total_statements += 1
            prop_total += 1
            property_counter[prop] += 1

            rank = statement.get("rank", "")
            rank_counter[rank] += 1

            mainsnak = statement.get("mainsnak", {})
            datatype = mainsnak.get("datatype", "")
            value_type = mainsnak.get("value_type", "")
            value = mainsnak.get("value")

            datatype_counter[datatype] += 1
            value_type_counter[value_type] += 1
            pair_counter[(datatype, value_type)] += 1

            prop_datatypes[datatype] += 1
            prop_value_types[value_type] += 1

            example_text = _as_text(value)
            if example_text and example_text not in datatype_examples[datatype]:
                if len(datatype_examples[datatype]) < 5:
                    datatype_examples[datatype].append(example_text)

            qualifiers = statement.get("qualifiers", {})
            if qualifiers:
                with_qualifiers += 1
                prop_with_qual += 1

            references = statement.get("references", [])
            if references:
                with_references += 1
                prop_with_ref += 1

        by_property[prop] = {
            "property": prop,
            "statement_count": prop_total,
            "datatypes": dict(prop_datatypes),
            "value_types": dict(prop_value_types),
            "with_qualifiers": prop_with_qual,
            "with_references": prop_with_ref,
            "qualifier_rate": (prop_with_qual / prop_total) if prop_total else 0.0,
            "reference_rate": (prop_with_ref / prop_total) if prop_total else 0.0,
        }

    pair_rows = [
        {"datatype": k[0], "value_type": k[1], "count": v}
        for k, v in sorted(pair_counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    by_property_rows = sorted(
        by_property.values(),
        key=lambda row: (-row["statement_count"], row["property"]),
    )
    for row in by_property_rows:
        row["datatypes"] = json.dumps(row["datatypes"], ensure_ascii=False)
        row["value_types"] = json.dumps(row["value_types"], ensure_ascii=False)

    summary = {
        "qid": payload.get("qid"),
        "label": payload.get("label"),
        "statement_count": total_statements,
        "property_count": len(claims),
        "datatype_counts": dict(datatype_counter),
        "value_type_counts": dict(value_type_counter),
        "rank_counts": dict(rank_counter),
        "with_qualifiers": with_qualifiers,
        "with_references": with_references,
        "qualifier_rate": (with_qualifiers / total_statements) if total_statements else 0.0,
        "reference_rate": (with_references / total_statements) if total_statements else 0.0,
        "top_properties": [
            {"property": prop, "count": count}
            for prop, count in property_counter.most_common(25)
        ],
        "datatype_examples": dict(datatype_examples),
    }

    return summary, by_property_rows, pair_rows


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Full statements JSON input path.")
    parser.add_argument(
        "--output-prefix",
        help=(
            "Output prefix path. Default: same folder/name as input "
            "with suffix '_statement_datatype_profile'."
        ),
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise FileNotFoundError(in_path)

    if args.output_prefix:
        prefix = Path(args.output_prefix)
    else:
        stem = in_path.stem
        for suffix in ("_statements_full", "_full"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        prefix = in_path.parent / f"{stem}_statement_datatype_profile"

    payload = _load_payload(in_path)
    summary, by_property_rows, pair_rows = _analyze(payload)

    summary_path = Path(f"{prefix}_summary.json")
    by_property_path = Path(f"{prefix}_by_property.csv")
    pairs_path = Path(f"{prefix}_datatype_pairs.csv")

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_csv(by_property_path, by_property_rows)
    _write_csv(pairs_path, pair_rows)

    print(f"input={in_path}")
    print(f"summary={summary_path}")
    print(f"by_property={by_property_path}")
    print(f"pairs={pairs_path}")
    print(
        "stats:"
        f" statements={summary['statement_count']}"
        f" properties={summary['property_count']}"
        f" datatypes={len(summary['datatype_counts'])}"
        f" value_types={len(summary['value_type_counts'])}"
    )


if __name__ == "__main__":
    main()
