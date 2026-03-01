#!/usr/bin/env python3
"""
Survey PeriodO scholarly period definitions for Roman Republic domain.

Fetches https://n2t.net/ark:/99152/p0dataset.json (gzipped), filters by:
- Temporal overlap with -509 to -27 BCE

Outputs FederationSurvey to output/nodes/periodo_roman_republic.json + CSV.

Usage:
  python scripts/backbone/subject/survey_periodo.py
  python scripts/backbone/subject/survey_periodo.py --out output/nodes/periodo_roman_republic.json
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

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
PERIODO_URL = "https://n2t.net/ark:/99152/p0dataset.json"
ROMAN_REPUBLIC_START = -509
ROMAN_REPUBLIC_END = -27
DOMAIN = "roman_republic"
SEED_ID = ""
SEED_LABEL = "Roman Republic"


def _parse_year(val) -> int | None:
    """Parse PeriodO year string (e.g. '-509', '27') to int."""
    if val is None or (isinstance(val, str) and not val.strip()):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _temporal_overlaps(start_year: int | None, stop_year: int | None) -> bool:
    """Period range overlaps [-509, -27]."""
    if start_year is None or stop_year is None:
        return False
    return start_year <= ROMAN_REPUBLIC_END and stop_year >= ROMAN_REPUBLIC_START


def _extract_spatial_coverage(spatial_coverage: list) -> list[str]:
    """All URIs from spatialCoverage (Wikidata, etc.). No filtering."""
    if not spatial_coverage or not isinstance(spatial_coverage, list):
        return []
    uris = []
    for item in spatial_coverage:
        if isinstance(item, dict) and item.get("id"):
            uris.append(item["id"])
    return uris


def run_survey(
    out_path: Path,
    cache_path: Path | None = None,
    domain: str = DOMAIN,
) -> int:
    project_root = Path(__file__).resolve().parents[2]
    cache = cache_path or (project_root / "Geographic" / "cache" / "periodo_p0dataset.json")
    cache.parent.mkdir(parents=True, exist_ok=True)

    if cache.exists():
        print(f"Using cached: {cache}")
        with open(cache, encoding="utf-8") as f:
            data = json.load(f)
    else:
        print(f"Downloading {PERIODO_URL}...")
        req = Request(PERIODO_URL, headers={"Accept": "application/json"})
        with urlopen(req, timeout=120) as r:
            content = r.read()
        if content[:2] == bytes([0x1F, 0x8B]):
            import gzip
            content = gzip.decompress(content)
        data = json.loads(content.decode("utf-8"))
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Downloaded and cached: {cache}")

    survey = new_survey(
        Federation.PERIODO,
        domain,
        seed_id=SEED_ID,
        seed_label=SEED_LABEL,
        meta={"source": "p0dataset.json"},
    )

    authorities = data.get("authorities", {})
    if not isinstance(authorities, dict):
        authorities = {}

    count = 0
    first_seed_id = None
    for auth_id, auth_obj in authorities.items():
        periods = auth_obj.get("periods", {})
        if not isinstance(periods, dict):
            continue
        source_label = (auth_obj.get("source") or {}).get("label", auth_id) if isinstance(auth_obj.get("source"), dict) else auth_id

        for period_id, period in periods.items():
            if not isinstance(period, dict):
                continue
            start_obj = period.get("start", {})
            stop_obj = period.get("stop", {})
            start_year = _parse_year((start_obj.get("in") or {}).get("year") if isinstance(start_obj.get("in"), dict) else None)
            stop_year = _parse_year((stop_obj.get("in") or {}).get("year") if isinstance(stop_obj.get("in"), dict) else None)

            if not _temporal_overlaps(start_year, stop_year):
                continue

            label = (period.get("label") or period.get("localizedLabels", {}).get("en", [""])[0] if isinstance(period.get("localizedLabels"), dict) else "") or f"Period {period_id}"
            if isinstance(label, list):
                label = label[0] if label else f"Period {period_id}"

            uri = f"https://n2t.net/ark:/99152/{period_id}" if not period_id.startswith("http") else period_id
            spatial_uris = _extract_spatial_coverage(period.get("spatialCoverage"))

            tr = (start_year, stop_year) if start_year is not None and stop_year is not None else None

            node = new_node(
                id=period_id,
                label=label,
                federation=Federation.PERIODO,
                domain=domain,
                uri=uri,
                depth=0,
                is_seed=False,
                spatial_anchor=spatial_uris[0] if spatial_uris else None,
                temporal_range=tr,
                concept_ref=None,
                properties={
                    "authority_id": auth_id,
                    "source": source_label,
                    "spatial_coverage_description": (period.get("spatialCoverageDescription") or "").strip(),
                    "editorial_note": (period.get("editorialNote") or "").strip(),
                    "spatial_coverage_uris": spatial_uris,
                },
            )
            survey.add_node(node)
            count += 1
            if first_seed_id is None:
                first_seed_id = period_id

    if first_seed_id and survey.nodes:
        survey.seed_id = first_seed_id
        survey.seed_label = next(n.label for n in survey.nodes if n.id == first_seed_id)

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
        "temporal_start", "temporal_end", "survey_depth", "is_seed",
        "authority_id", "source", "spatial_coverage_description",
        "spatial_coverage_uris",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for n in survey.nodes:
            uris = n.properties.get("spatial_coverage_uris", [])
            row = {
                "id": n.id,
                "label": n.label,
                "federation": n.federation,
                "domain": n.domain,
                "uri": n.uri,
                "spatial_anchor": n.spatial_anchor or "",
                "temporal_start": n.temporal_range[0] if n.temporal_range else "",
                "temporal_end": n.temporal_range[1] if n.temporal_range else "",
                "survey_depth": n.survey_depth,
                "is_seed": n.is_seed,
                "authority_id": n.properties.get("authority_id", ""),
                "source": n.properties.get("source", ""),
                "spatial_coverage_description": n.properties.get("spatial_coverage_description", ""),
                "spatial_coverage_uris": "|".join(uris) if isinstance(uris, list) else str(uris),
            }
            w.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey PeriodO for Roman Republic")
    parser.add_argument("--out", type=Path, default=Path("output/nodes/periodo_roman_republic.json"))
    parser.add_argument("--domain", default=DOMAIN)
    parser.add_argument("--cache", type=Path, help="Path to cached p0dataset.json")
    args = parser.parse_args()
    return run_survey(args.out, cache_path=args.cache, domain=args.domain)


if __name__ == "__main__":
    raise SystemExit(main())
