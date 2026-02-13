import sys
import json
import csv
from pathlib import Path
from typing import List, Dict

# --- Facet tagging logic ---
FACET_RULES = [
    {
        "facet_class": "GeographicFacet",
        "keywords": ["Mesopotamia", "Egypt", "Greece", "Rome"],
        "intensity": 0.9,
        "reasoning": "Located in {region}",
    },
    {
        "facet_class": "PoliticalFacet",
        "keywords": ["kingdom", "empire", "dynastic", "political"],
        "intensity": 0.85,
        "reasoning": "Label contains political keywords",
    },
    {
        "facet_class": "ArchaeologicalFacet",
        "keywords": ["ceramic", "material", "archaeology", "culture"],
        "intensity": 0.8,
        "reasoning": "Material-culture terminology",
    },
    {
        "facet_class": "DiplomaticFacet",
        "keywords": ["treaty", "interstate", "relations", "diplomatic"],
        "intensity": 0.7,
        "reasoning": "Interstate relations or empires",
    },
]


def tag_facets(period: Dict) -> List[Dict]:
    facets = []
    label = period.get("label", "").lower()
    region = period.get("spatial_label", "")
    for rule in FACET_RULES:
        if rule["facet_class"] == "GeographicFacet" and region:
            for kw in rule["keywords"]:
                if kw.lower() in region.lower():
                    facets.append(
                        {
                            "facet_class": rule["facet_class"],
                            "intensity": rule["intensity"],
                            "reasoning": rule["reasoning"].format(region=region),
                        }
                    )
        else:
            for kw in rule["keywords"]:
                if kw in label:
                    facets.append(
                        {
                            "facet_class": rule["facet_class"],
                            "intensity": rule["intensity"],
                            "reasoning": rule["reasoning"],
                        }
                    )
    return facets


def main():
    if len(sys.argv) < 2:
        print("Usage: python period_facet_tagger.py <input_tsv> [query_json] [output_json]")
        sys.exit(1)

    script_dir = Path(__file__).resolve().parent
    facets_dir = script_dir.parent

    input_tsv = Path(sys.argv[1]).resolve()
    if not input_tsv.exists():
        print(f"ERROR: input file not found: {input_tsv}")
        sys.exit(1)

    # Optional for compatibility with existing invocation patterns.
    query_json = Path(sys.argv[2]).resolve() if len(sys.argv) >= 3 else None
    if query_json and not query_json.exists():
        print(f"WARN: query_json not found (ignored): {query_json}")

    output_json = Path(sys.argv[3]).resolve() if len(sys.argv) >= 4 else facets_dir / "periods_with_facets.json"

    periods = []
    with input_tsv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            period = {
                "label": row.get("label", ""),
                "qid": row.get("qid", ""),
                "spatial_label": row.get("spatial_label", ""),
                "start_date": row.get("start_date", ""),
                "end_date": row.get("end_date", ""),
            }
            period["facets"] = tag_facets(period)
            periods.append(period)

    with output_json.open("w", encoding="utf-8") as out:
        json.dump(periods, out, indent=2, ensure_ascii=False)

    print(f"Facet tagging complete. Output: {output_json}")


if __name__ == "__main__":
    main()
