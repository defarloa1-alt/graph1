from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, List, Sequence


def ensure_sequence(value) -> Sequence:
    """Normalize JSON values (object or list) into a list-like sequence."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def extract_label(value) -> List[str]:
    """Return human-readable labels regardless of whether the JSON uses dicts or strings."""
    labels: List[str] = []
    for item in ensure_sequence(value):
        if isinstance(item, str):
            labels.append(item)
        elif isinstance(item, dict):
            literal = item.get("@value") or item.get("skosxl:literalForm", {}).get("@value")
            if literal:
                labels.append(literal)
    return labels


def extract_ids(value) -> List[str]:
    """Collect the trailing LCSH identifiers from broader/narrower links."""
    ids: List[str] = []
    for item in ensure_sequence(value):
        if isinstance(item, dict):
            term_id = item.get("@id")
            if term_id:
                ids.append(term_id.rstrip("/").rsplit("/", 1)[-1])
        elif isinstance(item, str):
            ids.append(item.rstrip("/").rsplit("/", 1)[-1])
    return ids


def find_concept(graph: Iterable[dict]) -> dict | None:
    """Locate the skos:Concept entry inside the @graph array."""
    for node in graph:
        types = node.get("@type")
        if isinstance(types, list):
            type_list = types
        else:
            type_list = [types]
        if any(t == "skos:Concept" for t in type_list if t):
            return node
    return None


def process_file(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as src, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        writer = csv.writer(dst)
        writer.writerow(["lcsh_id", "pref_label", "alt_labels", "broader_ids", "narrower_ids"])

        for line in src:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            graph = record.get("@graph")
            if not isinstance(graph, list):
                continue

            concept = find_concept(graph)
            if not concept:
                continue

            concept_id = concept.get("@id")
            if not concept_id:
                continue
            lcsh_id = concept_id.rstrip("/").rsplit("/", 1)[-1]

            pref_label_values = extract_label(concept.get("skos:prefLabel"))
            pref_label = pref_label_values[0] if pref_label_values else ""

            alt_labels = extract_label(concept.get("skos:altLabel"))

            bt_ids = extract_ids(concept.get("skos:broader"))
            nt_ids = extract_ids(concept.get("skos:narrower"))

            writer.writerow(
                [
                    lcsh_id,
                    pref_label,
                    "|".join(sorted(set(alt_labels))),
                    "|".join(sorted(set(bt_ids))),
                    "|".join(sorted(set(nt_ids))),
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract LCSH concepts, labels, and Broader/Narrower relationships."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("subjects.skosrdf.jsonld"),
        help="Path to the NDJSON SKOS dump.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("subjects_lcsh_bt_nt.csv"),
        help="Where the CSV should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    process_file(args.input, args.output)


if __name__ == "__main__":
    main()
