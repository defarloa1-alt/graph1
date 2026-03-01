#!/usr/bin/env python3
"""
Survey Pleiades places for Roman Republic domain.

Reads pleiades-places-latest.csv.gz (downloads if needed), filters by:
- Temporal overlap with -509 to -27 BCE
- No bbox filter (geopolitical options left open)

Outputs FederationSurvey to output/nodes/pleiades_roman_republic.json + CSV.

Usage:
  python scripts/backbone/subject/survey_pleiades.py
  python scripts/backbone/subject/survey_pleiades.py --out output/nodes/pleiades_roman_republic.json
"""
import argparse
import csv
import gzip
import sys
from pathlib import Path
from urllib.request import urlretrieve

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
PLEIADES_DUMPS = "https://atlantides.org/downloads/pleiades/dumps/"
PLEIADES_CSV = "pleiades-places-latest.csv.gz"
ROMAN_REPUBLIC_START = -509
ROMAN_REPUBLIC_END = -27
SEED_ID = "423025"
SEED_LABEL = "Roma"
DOMAIN = "roman_republic"


def _get_cache_path(project_root: Path) -> Path:
    cache = project_root / "Geographic" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    return cache / PLEIADES_CSV


def _download_if_needed(cache_path: Path) -> Path:
    if cache_path.exists():
        print(f"Using cached: {cache_path}")
        return cache_path
    url = PLEIADES_DUMPS + PLEIADES_CSV
    print(f"Downloading {url}...")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, cache_path)
    print(f"Downloaded: {cache_path}")
    return cache_path


def _parse_int(val) -> int | None:
    if val is None or (isinstance(val, str) and not val.strip()):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _parse_float(val) -> float | None:
    if val is None or (isinstance(val, str) and not val.strip()):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _temporal_overlaps(min_date, max_date) -> bool:
    """Place range overlaps [-509, -27]."""
    if min_date is None or max_date is None:
        return False
    return min_date <= ROMAN_REPUBLIC_END and max_date >= ROMAN_REPUBLIC_START


def run_survey(
    out_path: Path,
    cache_path: Path | None = None,
    domain: str = DOMAIN,
) -> int:
    project_root = Path(__file__).resolve().parents[2]
    cache = cache_path or _get_cache_path(project_root)
    _download_if_needed(cache)

    survey = new_survey(
        Federation.PLEIADES,
        domain,
        seed_id=SEED_ID,
        seed_label=SEED_LABEL,
        meta={"source": "pleiades-places-latest.csv.gz"},
    )

    count = 0
    with gzip.open(cache, "rt", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get("id", "").strip()
            if not pid:
                continue
            min_date = _parse_int(row.get("minDate"))
            max_date = _parse_int(row.get("maxDate"))
            if not _temporal_overlaps(min_date, max_date):
                continue
            lat = _parse_float(row.get("reprLat"))
            lon = _parse_float(row.get("reprLong"))
            title = (row.get("title") or "").strip() or f"Place {pid}"
            uri = f"https://pleiades.stoa.org/places/{pid}"
            tr = (min_date, max_date) if min_date is not None and max_date is not None else None
            node = new_node(
                id=pid,
                label=title,
                federation=Federation.PLEIADES,
                domain=domain,
                uri=uri,
                depth=0,
                is_seed=(pid == SEED_ID),
                spatial_anchor=uri,
                temporal_range=tr,
                concept_ref=None,
                properties={
                    "place_type": (row.get("featureTypes") or "").strip(),
                    "lat": lat,
                    "lon": lon,
                },
            )
            survey.add_node(node)
            count += 1

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
        "place_type", "lat", "lon",
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
                "survey_depth": n.survey_depth,
                "is_seed": n.is_seed,
                "place_type": n.properties.get("place_type", ""),
                "lat": n.properties.get("lat", ""),
                "lon": n.properties.get("lon", ""),
            }
            w.writerow(row)
    print(f"  CSV: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey Pleiades for Roman Republic")
    parser.add_argument("--out", type=Path, default=Path("output/nodes/pleiades_roman_republic.json"))
    parser.add_argument("--domain", default=DOMAIN)
    parser.add_argument("--cache", type=Path, help="Path to pleiades-places-latest.csv.gz")
    args = parser.parse_args()
    return run_survey(args.out, cache_path=args.cache, domain=args.domain)


if __name__ == "__main__":
    raise SystemExit(main())
