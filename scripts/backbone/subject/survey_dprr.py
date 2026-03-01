#!/usr/bin/env python3
"""
Survey DPRR office assertions (PostAssertions) for Roman Republic domain.

SPARQL: http://romanrepublic.ac.uk/rdf/endpoint/
Query offices (PostAssertions), not persons. Filter by inYear in -509 to -27 BCE.

The endpoint may return Anubis challenge (HTML). Use --cache with pre-fetched JSON:
  Format: {"results": {"bindings": [...]}}  (SPARQL JSON results)

Outputs FederationSurvey to output/nodes/dprr_roman_republic.json + CSV.

Usage:
  python scripts/backbone/subject/survey_dprr.py --cache path/to/dprr_post_assertions.json
  python scripts/backbone/subject/survey_dprr.py --out output/nodes/dprr_roman_republic.json
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import requests

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from federation_node_schema import (
    Federation,
    FederationNode,
    FederationSurvey,
    new_node,
    new_survey,
    validate_survey,
)

# Constants
DPRR_ENDPOINT = "http://romanrepublic.ac.uk/rdf/endpoint/"
DPRR_ONTOLOGY = "http://romanrepublic.ac.uk/rdf/ontology#"
USER_AGENT = "Chrystallum/1.0 (DPRR federation survey)"
PLEIADES_ROMA = "https://pleiades.stoa.org/places/423025"
ROMAN_REPUBLIC_START = -509
ROMAN_REPUBLIC_END = -27
DOMAIN = "roman_republic"
PAGE_SIZE = 2000


def _extract_id(uri: str) -> str | None:
    if not uri:
        return None
    m = re.search(r"/(\d+)$", uri)
    return m.group(1) if m else None


def _parse_year(val) -> int | None:
    """Parse DPRR year to int. BCE typically negative or small positive."""
    if val is None or (isinstance(val, str) and not val.strip()):
        return None
    try:
        v = int(float(val))
        # DPRR Roman Republic years: if positive and < 500, assume BCE
        if 0 < v < 500:
            v = -v
        return v
    except (ValueError, TypeError):
        return None


def _query_dprr(sparql: str, timeout: int = 90) -> list[dict]:
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(DPRR_ENDPOINT, params={"query": sparql}, headers=headers, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json().get("results", {}).get("bindings", [])
    except requests.exceptions.JSONDecodeError:
        # Endpoint may return Anubis challenge (HTML) instead of JSON
        raise RuntimeError(
            "DPRR endpoint returned non-JSON (possibly Anubis challenge). "
            "Use --cache with a pre-fetched SPARQL results file."
        ) from None


def run_survey(
    out_path: Path,
    cache_path: Path | None = None,
    domain: str = DOMAIN,
) -> int:
    if cache_path and cache_path.exists():
        print(f"Using cached SPARQL results: {cache_path}")
        with open(cache_path, encoding="utf-8") as f:
            import json
            data = json.load(f)
        all_rows = data.get("results", {}).get("bindings", [])
        if not all_rows:
            print("  [WARN] Cache empty")
    else:
        all_rows = []
        offset = 0
        while True:
            sparql = f"""
            PREFIX vocab: <{DPRR_ONTOLOGY}>
            SELECT ?post ?person ?office ?officeLabel ?year WHERE {{
              ?post a vocab:PostAssertion ;
                    vocab:isAboutPerson ?person ;
                    vocab:hasOffice ?office .
              OPTIONAL {{ ?office vocab:hasName ?officeLabel }}
              OPTIONAL {{ ?post vocab:inYear ?year }}
            }}
            ORDER BY ?post
            LIMIT {PAGE_SIZE}
            OFFSET {offset}
            """
            rows = _query_dprr(sparql)
            all_rows.extend(rows)
            if len(rows) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                import json
                json.dump({"results": {"bindings": all_rows}}, f, indent=2)
            print(f"Cached to {cache_path}")

    survey = new_survey(
        Federation.DPRR,
        domain,
        seed_id="",
        seed_label="DPRR offices",
        meta={"source": "romanrepublic.ac.uk SPARQL", "query": "PostAssertions"},
    )

    seen = set()
    for r in all_rows:
        post_uri = r.get("post", {}).get("value", "")
        post_id = _extract_id(post_uri)
        if not post_id or post_id in seen:
            continue
        seen.add(post_id)

        person_uri = r.get("person", {}).get("value", "")
        office_uri = r.get("office", {}).get("value", "")
        office_label = (r.get("officeLabel", {}).get("value", "") if r.get("officeLabel") else "") or (office_uri.split("/")[-1] if office_uri else "")
        year_val = r.get("year", {}).get("value", "") if r.get("year") else None
        year = _parse_year(year_val)

        if year is None or not (ROMAN_REPUBLIC_START <= year <= ROMAN_REPUBLIC_END):
            continue

        label = office_label or f"Office {post_id}"
        tr = (year, year)
        node = new_node(
            id=post_id,
            label=label,
            federation=Federation.DPRR,
            domain=domain,
            uri=post_uri,
            depth=0,
            is_seed=False,
            spatial_anchor=PLEIADES_ROMA,
            temporal_range=tr,
            concept_ref=None,
            person_ref=person_uri or None,
            properties={
                "office_uri": office_uri or "",
                "office_label": office_label,
                "year_raw": str(year_val) if year_val else "",
            },
        )
        survey.add_node(node)

    if survey.nodes:
        survey.seed_id = survey.nodes[0].id
        survey.seed_label = survey.nodes[0].label

    for w in validate_survey(survey):
        print(f"  [WARN] {w}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    survey.save(out_path)
    _write_survey_csv(survey, out_path.with_suffix(".csv"))
    return 0


def _write_survey_csv(survey: FederationSurvey, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "label", "federation", "domain", "uri", "spatial_anchor",
        "temporal_start", "temporal_end", "person_ref", "survey_depth", "is_seed",
        "office_uri", "office_label", "year_raw",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for n in survey.nodes:
            row = {
                "id": n.id,
                "label": n.label,
                "federation": n.federation,
                "domain": n.domain,
                "uri": n.uri,
                "spatial_anchor": n.spatial_anchor or "",
                "temporal_start": n.temporal_range[0] if n.temporal_range else "",
                "temporal_end": n.temporal_range[1] if n.temporal_range else "",
                "person_ref": n.person_ref or "",
                "survey_depth": n.survey_depth,
                "is_seed": n.is_seed,
                "office_uri": n.properties.get("office_uri", ""),
                "office_label": n.properties.get("office_label", ""),
                "year_raw": n.properties.get("year_raw", ""),
            }
            w.writerow(row)
    print(f"  CSV: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey DPRR offices for Roman Republic")
    parser.add_argument("--out", type=Path, default=Path("output/nodes/dprr_roman_republic.json"))
    parser.add_argument("--domain", default=DOMAIN)
    parser.add_argument("--cache", type=Path, help="Path to cached SPARQL results JSON or write cache here")
    args = parser.parse_args()
    cache = args.cache or (Path(__file__).resolve().parents[2] / "Geographic" / "cache" / "dprr_post_assertions.json")
    return run_survey(args.out, cache_path=cache, domain=args.domain)


if __name__ == "__main__":
    raise SystemExit(main())
