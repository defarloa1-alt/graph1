#!/usr/bin/env python3
"""
Build subjects_simplified.csv directly from subjects.skosrdf.jsonld.gz.
Use when the decompressed .jsonld file is locked. Writes to Subjects/subjects_simplified.csv.
"""
import csv
import gzip
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GZ_PATH = PROJECT_ROOT / "Subjects" / "subjects.skosrdf.jsonld.gz"
OUT_PATH = PROJECT_ROOT / "Subjects" / "subjects_simplified.csv"


def main():
    if not GZ_PATH.exists():
        print(f"ERROR: {GZ_PATH} not found")
        return 1

    concepts = []
    with gzip.open(GZ_PATH, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
                graph = doc.get("@graph", [doc] if isinstance(doc, dict) else [])
                for item in graph:
                    types = item.get("@type") or item.get("type")
                    if not types:
                        continue
                    if isinstance(types, list):
                        is_concept = any("Concept" in str(t) for t in types)
                    else:
                        is_concept = "Concept" in str(types)
                    if is_concept and item.get("@id", "").startswith("http://id.loc.gov"):
                        concepts.append(item)
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(concepts)} SKOS concepts")

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["id", "prefLabel", "altLabel", "broader", "narrower"])
        writer.writeheader()
        for concept in concepts:
            row = {
                "id": concept.get("@id", ""),
                "prefLabel": "",
                "altLabel": "",
                "broader": "",
                "narrower": "",
            }
            for label_type in ["prefLabel", "altLabel"]:
                val = concept.get(f"skos:{label_type}") or concept.get(label_type)
                if isinstance(val, list):
                    row[label_type] = "|".join(
                        v["@value"] if isinstance(v, dict) and "@value" in v else str(v) for v in val
                    )
                elif isinstance(val, dict):
                    row[label_type] = val.get("@value", "")
                elif val:
                    row[label_type] = str(val)
            for rel in ["broader", "narrower"]:
                val = concept.get(f"skos:{rel}") or concept.get(rel)
                if isinstance(val, list):
                    row[rel] = "|".join(v.get("@id", str(v)) for v in val)
                elif isinstance(val, dict):
                    row[rel] = val.get("@id", "")
                elif val:
                    row[rel] = str(val)
            writer.writerow(row)

    print(f"Wrote: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
