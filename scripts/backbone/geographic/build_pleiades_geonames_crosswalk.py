#!/usr/bin/env python3
"""
Build a Pleiades -> GeoNames crosswalk from the pleiades-plus dataset.

Sources:
- https://github.com/ryanfb/pleiades-plus (data/pleiades-plus.csv)
- Optional local Pleiades places file for label/date enrichment

Outputs:
- Geographic/pleiades_plus.csv
- CSV/geographic/pleiades_geonames_crosswalk_v1.csv
- CSV/geographic/pleiades_geonames_place_summary_v1.csv
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List


DEFAULT_PLEIADES_PLUS_URL = (
    "https://raw.githubusercontent.com/ryanfb/pleiades-plus/master/data/pleiades-plus.csv"
)
DEFAULT_GEONAMES_FEATURE_CODES_URL = "http://download.geonames.org/export/dump/featureCodes_en.txt"
DEFAULT_GEONAMES_ALLCOUNTRIES_ZIP_URL = "http://download.geonames.org/export/dump/allCountries.zip"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)


def _download_text(url: str, timeout: int = 180) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum-Graph1/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _download_file(url: str, output_path: Path, timeout: int = 600) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum-Graph1/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    output_path.write_bytes(data)


def _extract_pleiades_id(url: str) -> str:
    m = re.search(r"/places/(\d+)", url or "")
    return m.group(1) if m else ""


def _extract_geonames_id(url: str) -> str:
    m = re.search(r"/(\d+)/?$", (url or "").strip())
    return m.group(1) if m else ""


def _load_places_index(path: Path) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pid = (row.get("pleiades_id") or "").strip()
            if not pid:
                continue
            out[pid] = {
                "place_label": (row.get("label") or "").strip(),
                "place_type": (row.get("place_type") or "").strip(),
                "min_date": (row.get("min_date") or "").strip(),
                "max_date": (row.get("max_date") or "").strip(),
                "place_uri": (row.get("uri") or "").strip(),
            }
    return out


def _download_csv(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum-Graph1/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    output_path.write_bytes(data)


def _fetch_geonames_feature_code_labels(url: str) -> Dict[str, str]:
    """
    Parse featureCodes_en.txt:
      <featureCode>\t<name>\t<description>
    """
    out: Dict[str, str] = {}
    txt = _download_text(url, timeout=180)
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        code_full = parts[0].strip()
        label = parts[1].strip()
        if not code_full:
            continue
        code = code_full.split(".")[-1] if "." in code_full else code_full
        if code and label and code not in out:
            out[code] = label
    return out


def _fetch_geonames_label_sws(
    geonames_id: str,
    *,
    min_interval_seconds: float,
    max_retries: int,
    last_request_ts: List[float],
) -> str:
    """
    Get canonical GeoNames label from sws.geonames.org/<id>/about.rdf.
    """
    url = f"https://sws.geonames.org/{geonames_id}/about.rdf"
    for attempt in range(max_retries):
        now = time.time()
        elapsed = now - last_request_ts[0]
        if elapsed < min_interval_seconds:
            time.sleep(min_interval_seconds - elapsed)
        last_request_ts[0] = time.time()
        try:
            body = _download_text(url, timeout=45)
            m = re.search(r"<gn:name>(.*?)</gn:name>", body, flags=re.DOTALL | re.IGNORECASE)
            if m:
                return html.unescape(m.group(1).strip())
            return ""
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 503} and attempt < (max_retries - 1):
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                delay = 1.0 * (attempt + 1)
                if retry_after:
                    try:
                        delay = max(delay, float(retry_after))
                    except ValueError:
                        pass
                time.sleep(delay)
                continue
            return ""
        except urllib.error.URLError:
            if attempt < (max_retries - 1):
                time.sleep(1.0 * (attempt + 1))
                continue
            return ""
    return ""


def _load_geonames_labels_from_allcountries_zip(
    zip_path: Path,
    target_ids: set[str],
) -> Dict[str, str]:
    """
    Extract labels for target geonames IDs from allCountries.zip.
    GeoNames columns:
      0 geonameid, 1 name, 2 asciiname, ...
    """
    out: Dict[str, str] = {}
    if not zip_path.exists() or not target_ids:
        return out

    with zipfile.ZipFile(zip_path, "r") as zf:
        txt_name = None
        for name in zf.namelist():
            if name.lower().endswith(".txt"):
                txt_name = name
                break
        if not txt_name:
            return out

        with zf.open(txt_name, "r") as fh:
            for raw in fh:
                try:
                    line = raw.decode("utf-8", errors="replace").rstrip("\n")
                except Exception:
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                gid = parts[0].strip()
                if gid not in target_ids:
                    continue
                name = parts[1].strip() or parts[2].strip()
                if name:
                    out[gid] = name
                if len(out) >= len(target_ids):
                    break
    return out


def _build_crosswalk_rows(
    plus_csv: Path,
    places_idx: Dict[str, dict],
    *,
    geonames_labels: Dict[str, str],
    geonames_feature_code_labels: Dict[str, str],
) -> List[dict]:
    rows: List[dict] = []
    with plus_csv.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pleiades_url = (row.get("pleiades_url") or "").strip()
            geonames_url = (row.get("geonames_url") or "").strip()
            pleiades_id = _extract_pleiades_id(pleiades_url)
            geonames_id = _extract_geonames_id(geonames_url)
            if not pleiades_id or not geonames_id:
                continue

            p = places_idx.get(pleiades_id, {})
            rows.append(
                {
                    "pleiades_id": pleiades_id,
                    "pleiades_url": pleiades_url,
                    "place_label": p.get("place_label", ""),
                    "place_type": p.get("place_type", ""),
                    "min_date": p.get("min_date", ""),
                    "max_date": p.get("max_date", ""),
                    "geonames_id": geonames_id,
                    "geonames_url": geonames_url,
                    "geonames_label": geonames_labels.get(geonames_id, ""),
                    "match_type": (row.get("match_type") or "").strip(),
                    "distance_km": (row.get("distance") or "").strip(),
                    "pleiades_location_precision": (row.get("pleiades_locationPrecision") or "").strip(),
                    "pleiades_feature_types": (row.get("pleiades_featureTypes") or "").strip(),
                    "geonames_feature_code": (row.get("geonames_featurecode") or "").strip(),
                    "geonames_feature_code_label": geonames_feature_code_labels.get(
                        (row.get("geonames_featurecode") or "").strip(),
                        "",
                    ),
                }
            )
    rows.sort(key=lambda r: (r["pleiades_id"], r["geonames_id"]))
    return rows


def _build_place_summary(rows: List[dict]) -> List[dict]:
    by_pid: Dict[str, dict] = {}
    for r in rows:
        pid = r["pleiades_id"]
        d = by_pid.setdefault(
            pid,
            {
                "pleiades_id": pid,
                "place_label": r.get("place_label", ""),
                "place_type": r.get("place_type", ""),
                "min_date": r.get("min_date", ""),
                "max_date": r.get("max_date", ""),
                "geonames_count": 0,
                "match_types": set(),
                "geonames_feature_codes": set(),
            },
        )
        d["geonames_count"] += 1
        if r.get("match_type"):
            d["match_types"].add(r["match_type"])
        if r.get("geonames_feature_code"):
            d["geonames_feature_codes"].add(r["geonames_feature_code"])

    out: List[dict] = []
    for d in by_pid.values():
        out.append(
            {
                "pleiades_id": d["pleiades_id"],
                "place_label": d["place_label"],
                "place_type": d["place_type"],
                "min_date": d["min_date"],
                "max_date": d["max_date"],
                "geonames_count": str(d["geonames_count"]),
                "match_types": "|".join(sorted(d["match_types"])),
                "geonames_feature_codes": "|".join(sorted(d["geonames_feature_codes"])),
            }
        )
    out.sort(key=lambda r: (-int(r["geonames_count"]), r["pleiades_id"]))
    return out


def _build_feature_code_distinct(rows: List[dict]) -> List[dict]:
    by_code: Dict[str, dict] = {}
    for r in rows:
        code = (r.get("geonames_feature_code") or "").strip()
        if not code:
            continue
        d = by_code.setdefault(
            code,
            {
                "geonames_feature_code": code,
                "geonames_feature_code_label": (r.get("geonames_feature_code_label") or "").strip(),
                "row_count": 0,
                "distinct_geonames_ids": set(),
                "distinct_pleiades_ids": set(),
            },
        )
        d["row_count"] += 1
        if r.get("geonames_id"):
            d["distinct_geonames_ids"].add(r["geonames_id"])
        if r.get("pleiades_id"):
            d["distinct_pleiades_ids"].add(r["pleiades_id"])

    out: List[dict] = []
    for d in by_code.values():
        out.append(
            {
                "geonames_feature_code": d["geonames_feature_code"],
                "geonames_feature_code_label": d["geonames_feature_code_label"],
                "row_count": str(d["row_count"]),
                "distinct_geonames_ids": str(len(d["distinct_geonames_ids"])),
                "distinct_pleiades_ids": str(len(d["distinct_pleiades_ids"])),
            }
        )
    out.sort(key=lambda r: (-int(r["row_count"]), r["geonames_feature_code"]))
    return out


def _write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _collect_distinct_geonames_ids(plus_csv: Path) -> List[str]:
    ids: set[str] = set()
    with plus_csv.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            gid = _extract_geonames_id((row.get("geonames_url") or "").strip())
            if gid:
                ids.add(gid)
    return sorted(ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Pleiades->GeoNames crosswalk from pleiades-plus CSV.")
    parser.add_argument("--pleiades-plus-url", default=DEFAULT_PLEIADES_PLUS_URL, help="Remote pleiades-plus CSV URL")
    parser.add_argument(
        "--out-pleiades-plus-csv",
        default="Geographic/pleiades_plus.csv",
        help="Local copy of pleiades-plus CSV",
    )
    parser.add_argument(
        "--places-csv",
        default="Geographic/pleiades_places.csv",
        help="Pleiades places CSV for enrichment",
    )
    parser.add_argument(
        "--out-crosswalk-csv",
        default="CSV/geographic/pleiades_geonames_crosswalk_v1.csv",
        help="Normalized row-level crosswalk output",
    )
    parser.add_argument(
        "--out-summary-csv",
        default="CSV/geographic/pleiades_geonames_place_summary_v1.csv",
        help="Per-place summary output",
    )
    parser.add_argument(
        "--out-feature-codes-csv",
        default="CSV/geographic/geonames_feature_codes_distinct_v1.csv",
        help="Distinct GeoNames feature codes report",
    )
    parser.add_argument(
        "--geonames-label-cache-json",
        default="CSV/geographic/geonames_labels_cache_v1.json",
        help="Cache for GeoNames ID -> label lookups",
    )
    parser.add_argument(
        "--geonames-feature-codes-url",
        default=DEFAULT_GEONAMES_FEATURE_CODES_URL,
        help="GeoNames feature code definitions URL",
    )
    parser.add_argument(
        "--geonames-label-source",
        choices=["allcountries", "sws", "cache"],
        default="allcountries",
        help="GeoNames label enrichment source.",
    )
    parser.add_argument(
        "--geonames-allcountries-url",
        default=DEFAULT_GEONAMES_ALLCOUNTRIES_ZIP_URL,
        help="GeoNames allCountries.zip URL",
    )
    parser.add_argument(
        "--geonames-allcountries-zip",
        default="Geographic/geonames_allCountries.zip",
        help="Local allCountries.zip path",
    )
    parser.add_argument(
        "--skip-geonames-allcountries-download",
        action="store_true",
        help="Do not download allCountries.zip if missing.",
    )
    parser.add_argument(
        "--skip-geonames-label-fetch",
        action="store_true",
        help="Skip GeoNames label enrichment fetch (use cache only).",
    )
    parser.add_argument(
        "--geonames-min-interval-seconds",
        type=float,
        default=0.25,
        help="Minimum delay between GeoNames label requests (seconds).",
    )
    parser.add_argument(
        "--geonames-max-retries",
        type=int,
        default=5,
        help="Maximum retries for a GeoNames label request.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Use existing local pleiades_plus.csv instead of downloading",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent.parent.parent
    plus_csv = (root / args.out_pleiades_plus_csv).resolve()
    places_csv = (root / args.places_csv).resolve()
    out_crosswalk = (root / args.out_crosswalk_csv).resolve()
    out_summary = (root / args.out_summary_csv).resolve()
    out_feature_codes = (root / args.out_feature_codes_csv).resolve()
    geonames_label_cache_json = (root / args.geonames_label_cache_json).resolve()
    geonames_allcountries_zip = (root / args.geonames_allcountries_zip).resolve()

    if not args.skip_download:
        _download_csv(args.pleiades_plus_url, plus_csv)
    if not plus_csv.exists():
        print(f"ERROR: missing pleiades-plus CSV: {plus_csv}")
        return 1

    geonames_labels = _load_json(geonames_label_cache_json)
    distinct_geonames_ids = _collect_distinct_geonames_ids(plus_csv)
    if not args.skip_geonames_label_fetch:
        missing_ids = set([gid for gid in distinct_geonames_ids if not geonames_labels.get(gid)])
        if args.geonames_label_source == "allcountries":
            if (not geonames_allcountries_zip.exists()) and (not args.skip_geonames_allcountries_download):
                _download_file(args.geonames_allcountries_url, geonames_allcountries_zip, timeout=1800)
            extracted = _load_geonames_labels_from_allcountries_zip(geonames_allcountries_zip, missing_ids)
            geonames_labels.update(extracted)
        elif args.geonames_label_source == "sws":
            min_interval = max(0.0, args.geonames_min_interval_seconds)
            max_retries = max(1, args.geonames_max_retries)
            last_request_ts = [0.0]
            for gid in distinct_geonames_ids:
                if gid in geonames_labels and geonames_labels.get(gid):
                    continue
                label = _fetch_geonames_label_sws(
                    gid,
                    min_interval_seconds=min_interval,
                    max_retries=max_retries,
                    last_request_ts=last_request_ts,
                )
                geonames_labels[gid] = label
        _save_json(geonames_label_cache_json, geonames_labels)
    geonames_feature_code_labels = _fetch_geonames_feature_code_labels(args.geonames_feature_codes_url)

    places_idx = _load_places_index(places_csv)
    rows = _build_crosswalk_rows(
        plus_csv,
        places_idx,
        geonames_labels=geonames_labels,
        geonames_feature_code_labels=geonames_feature_code_labels,
    )
    summary_rows = _build_place_summary(rows)
    feature_code_rows = _build_feature_code_distinct(rows)

    _write_csv(
        out_crosswalk,
        rows,
        [
            "pleiades_id",
            "pleiades_url",
            "place_label",
            "place_type",
            "min_date",
            "max_date",
            "geonames_id",
            "geonames_url",
            "geonames_label",
            "match_type",
            "distance_km",
            "pleiades_location_precision",
            "pleiades_feature_types",
            "geonames_feature_code",
            "geonames_feature_code_label",
        ],
    )
    _write_csv(
        out_summary,
        summary_rows,
        [
            "pleiades_id",
            "place_label",
            "place_type",
            "min_date",
            "max_date",
            "geonames_count",
            "match_types",
            "geonames_feature_codes",
        ],
    )
    _write_csv(
        out_feature_codes,
        feature_code_rows,
        [
            "geonames_feature_code",
            "geonames_feature_code_label",
            "row_count",
            "distinct_geonames_ids",
            "distinct_pleiades_ids",
        ],
    )

    print("Pleiades+ GeoNames crosswalk built.")
    print(f"  Source: {plus_csv}")
    print(f"  Crosswalk: {out_crosswalk}")
    print(f"  Summary: {out_summary}")
    print(f"  Feature codes: {out_feature_codes}")
    print(f"  GeoNames label cache: {geonames_label_cache_json}")
    if args.geonames_label_source == "allcountries":
        print(f"  GeoNames allCountries zip: {geonames_allcountries_zip}")
    print(f"  GeoNames label source: {args.geonames_label_source}")
    print(f"  Rows: {len(rows)}")
    print(f"  Distinct Pleiades IDs: {len({r['pleiades_id'] for r in rows})}")
    print(f"  Distinct GeoNames IDs: {len({r['geonames_id'] for r in rows})}")
    print(f"  Distinct feature codes: {len(feature_code_rows)}")
    print(f"  Rows with GeoNames label: {sum(1 for r in rows if r.get('geonames_label'))}")
    return 0


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
