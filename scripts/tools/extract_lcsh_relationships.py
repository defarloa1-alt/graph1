from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


def ensure_sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def extract_label_values(value: Any) -> list[str]:
    labels: list[str] = []
    for item in ensure_sequence(value):
        if isinstance(item, str):
            labels.append(item)
            continue
        if not isinstance(item, dict):
            continue
        literal = item.get("@value")
        if not literal:
            skosxl = item.get("skosxl:literalForm")
            if isinstance(skosxl, dict):
                literal = skosxl.get("@value")
        if literal:
            labels.append(str(literal))
    return labels


def extract_trailing_ids(value: Any) -> list[str]:
    ids: list[str] = []
    for item in ensure_sequence(value):
        if isinstance(item, dict):
            item = item.get("@id")
        if isinstance(item, str) and item:
            ids.append(item.rstrip("/").rsplit("/", 1)[-1])
    return ids


def node_is_concept(node: dict[str, Any]) -> bool:
    types = ensure_sequence(node.get("@type"))
    return any(t == "skos:Concept" for t in types if isinstance(t, str))


def iter_nested_nodes(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_nested_nodes(child)
        return
    if isinstance(value, list):
        for child in value:
            yield from iter_nested_nodes(child)


def iter_concepts(record: Any) -> Iterator[dict[str, Any]]:
    for node in iter_nested_nodes(record):
        if node_is_concept(node):
            yield node


def iter_records(input_path: Path) -> Iterator[Any]:
    text = input_path.read_text(encoding="utf-8")
    stripped = text.lstrip()

    # If it looks like a JSON array/object, parse once.
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            payload = json.loads(text)
            if isinstance(payload, list):
                for item in payload:
                    yield item
            else:
                yield payload
            return
        except json.JSONDecodeError:
            # Fall through to NDJSON processing.
            pass

    # NDJSON fallback (one JSON object per line).
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def process_file(input_path: Path, output_path: Path) -> int:
    seen: set[str] = set()
    rows = 0

    with output_path.open("w", encoding="utf-8", newline="") as dst:
        writer = csv.writer(dst)
        writer.writerow(["lcsh_id", "pref_label", "alt_labels", "broader_ids", "narrower_ids"])

        for record in iter_records(input_path):
            for concept in iter_concepts(record):
                concept_id = concept.get("@id")
                if not isinstance(concept_id, str) or not concept_id:
                    continue

                lcsh_id = concept_id.rstrip("/").rsplit("/", 1)[-1]
                if lcsh_id in seen:
                    continue
                seen.add(lcsh_id)

                pref_values = extract_label_values(concept.get("skos:prefLabel"))
                alt_values = extract_label_values(concept.get("skos:altLabel"))
                broader = extract_trailing_ids(concept.get("skos:broader"))
                narrower = extract_trailing_ids(concept.get("skos:narrower"))

                writer.writerow(
                    [
                        lcsh_id,
                        pref_values[0] if pref_values else "",
                        "|".join(sorted(set(alt_values))),
                        "|".join(sorted(set(broader))),
                        "|".join(sorted(set(narrower))),
                    ]
                )
                rows += 1

    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract LCSH concept labels and broader/narrower links from JSON-LD or NDJSON."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to LCSH JSON-LD/NDJSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path for output CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = process_file(args.input, args.output)
    print(f"Wrote {count} concepts to {args.output}")


if __name__ == "__main__":
    main()
