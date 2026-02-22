#!/usr/bin/env python3
"""
Build GeoNames -> Wikidata mappings and merge with existing Pleiades+GeoNames and TGN+Wikidata assets.

Inputs:
  - CSV/geographic/pleiades_geonames_crosswalk_v1.csv
  - Temporal/Data/tgn_wikidata_mapping.csv

Outputs:
  - CSV/geographic/geonames_wikidata_mapping_v1.csv
  - CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv
  - CSV/geographic/pleiades_geonames_wikidata_tgn_stats_v1.json
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
USER_AGENT = "Chrystallum-Graph1/1.0 (geonames-wikidata-bridge)"


def _fetch_sparql_json(query: str, *, timeout_seconds: int, max_retries: int, pause_seconds: float) -> dict:
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{WIKIDATA_SPARQL}?{params}"
    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/sparql-results+json",
                    "User-Agent": USER_AGENT,
                },
            )
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {429, 500, 502, 503, 504} and attempt < max_retries:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                delay = pause_seconds * attempt
                if retry_after:
                    try:
                        delay = max(delay, float(retry_after))
                    except ValueError:
                        pass
                print(
                    f"[wikidata] retryable HTTP {exc.code} on attempt {attempt}/{max_retries}; sleeping {delay:.1f}s",
                    flush=True,
                )
                time.sleep(delay)
                continue
            raise
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < max_retries:
                delay = pause_seconds * attempt
                print(
                    f"[wikidata] network error on attempt {attempt}/{max_retries}; sleeping {delay:.1f}s: {exc}",
                    flush=True,
                )
                time.sleep(delay)
                continue
            raise
    if last_error:
        raise last_error
    return {}


def _chunked(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _quote_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _sparql_for_geonames_batch(geonames_ids: List[str]) -> str:
    values = " ".join(_quote_literal(gid) for gid in geonames_ids)
    return f"""
SELECT ?gn ?item ?itemLabel ?lat ?long WHERE {{
  VALUES ?gn {{ {values} }}
  ?item wdt:P1566 ?gn .
  OPTIONAL {{
    ?item p:P625 ?coordinate .
    ?coordinate psv:P625 ?coordValue .
    ?coordValue wikibase:geoLatitude ?lat .
    ?coordValue wikibase:geoLongitude ?long .
  }}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en,la,it,fr,de,es,mul" .
  }}
}}
"""


def _read_csv_rows(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_existing_geonames_wikidata_cache(path: Path) -> Tuple[List[dict], Set[str]]:
    if not path.exists():
        return ([], set())
    rows = _read_csv_rows(path)
    complete_ids: Set[str] = set()
    for row in rows:
        gid = (row.get("geonames_id") or "").strip()
        if gid:
            complete_ids.add(gid)
    return (rows, complete_ids)


def _collect_distinct_geonames_ids(pleiades_geonames_rows: List[dict]) -> List[str]:
    ids: Set[str] = set()
    for row in pleiades_geonames_rows:
        gid = (row.get("geonames_id") or "").strip()
        if gid:
            ids.add(gid)
    return sorted(ids)


def build_geonames_wikidata_mapping(
    *,
    geonames_ids: List[str],
    existing_rows: List[dict],
    existing_ids: Set[str],
    batch_size: int,
    timeout_seconds: int,
    max_retries: int,
    pause_seconds: float,
    request_sleep_seconds: float,
) -> List[dict]:
    rows: List[dict] = list(existing_rows)
    pending = [gid for gid in geonames_ids if gid not in existing_ids]

    print(
        f"[wikidata] geonames ids total={len(geonames_ids)} existing_cached={len(existing_ids)} pending={len(pending)}",
        flush=True,
    )
    if not pending:
        return rows

    batches = _chunked(pending, batch_size)
    for idx, batch in enumerate(batches, start=1):
        query = _sparql_for_geonames_batch(batch)
        payload = _fetch_sparql_json(
            query,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            pause_seconds=pause_seconds,
        )
        bindings = payload.get("results", {}).get("bindings", []) or []
        mapped_in_batch = 0
        seen_pairs: Set[Tuple[str, str]] = set()
        for b in bindings:
            geonames_id = (b.get("gn", {}).get("value") or "").strip()
            qid_uri = (b.get("item", {}).get("value") or "").strip()
            qid = qid_uri.rsplit("/", 1)[-1] if qid_uri else ""
            label = (b.get("itemLabel", {}).get("value") or "").strip()
            lat = (b.get("lat", {}).get("value") or "").strip()
            lon = (b.get("long", {}).get("value") or "").strip()
            if not geonames_id or not qid:
                continue
            key = (geonames_id, qid)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            mapped_in_batch += 1
            rows.append(
                {
                    "geonames_id": geonames_id,
                    "qid": qid,
                    "wikidata_label": label,
                    "wikidata_latitude": lat,
                    "wikidata_longitude": lon,
                }
            )
        print(
            f"[wikidata] batch {idx}/{len(batches)} ids={len(batch)} mappings_added={mapped_in_batch}",
            flush=True,
        )
        time.sleep(max(0.0, request_sleep_seconds))

    # De-duplicate globally by (geonames_id, qid)
    dedup: Dict[Tuple[str, str], dict] = {}
    for row in rows:
        gid = (row.get("geonames_id") or "").strip()
        qid = (row.get("qid") or "").strip()
        if not gid or not qid:
            continue
        dedup[(gid, qid)] = {
            "geonames_id": gid,
            "qid": qid,
            "wikidata_label": (row.get("wikidata_label") or "").strip(),
            "wikidata_latitude": (row.get("wikidata_latitude") or "").strip(),
            "wikidata_longitude": (row.get("wikidata_longitude") or "").strip(),
        }

    out = list(dedup.values())
    out.sort(key=lambda r: (r["geonames_id"], r["qid"]))
    return out


def _index_tgn_by_qid(tgn_rows: List[dict]) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    seen: Set[Tuple[str, str, str, str, str]] = set()
    for row in tgn_rows:
        tgn_id = (row.get("tgn_id") or "").strip()
        qid = (row.get("qid") or "").strip()
        if not tgn_id or not qid:
            continue
        tgn_label = (row.get("label") or "").strip()
        tgn_lat = (row.get("latitude") or "").strip()
        tgn_lon = (row.get("longitude") or "").strip()
        sig = (tgn_id, qid, tgn_label, tgn_lat, tgn_lon)
        if sig in seen:
            continue
        seen.add(sig)
        out.setdefault(qid, []).append(
            {
                "tgn_id": tgn_id,
                "tgn_label": tgn_label,
                "tgn_latitude": tgn_lat,
                "tgn_longitude": tgn_lon,
            }
        )
    return out


def _index_wikidata_by_geonames(geonames_wikidata_rows: List[dict]) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    for row in geonames_wikidata_rows:
        gid = (row.get("geonames_id") or "").strip()
        if not gid:
            continue
        out.setdefault(gid, []).append(
            {
                "qid": (row.get("qid") or "").strip(),
                "wikidata_label": (row.get("wikidata_label") or "").strip(),
                "wikidata_latitude": (row.get("wikidata_latitude") or "").strip(),
                "wikidata_longitude": (row.get("wikidata_longitude") or "").strip(),
            }
        )
    return out


def _has_temporal_signal(row: dict) -> bool:
    return bool((row.get("min_date") or "").strip() or (row.get("max_date") or "").strip())


def build_federated_crosswalk(
    *,
    pleiades_geonames_rows: List[dict],
    geonames_wikidata_rows: List[dict],
    tgn_rows: List[dict],
) -> List[dict]:
    by_gn = _index_wikidata_by_geonames(geonames_wikidata_rows)
    by_qid_tgn = _index_tgn_by_qid(tgn_rows)

    out: List[dict] = []
    total = len(pleiades_geonames_rows)
    for idx, row in enumerate(pleiades_geonames_rows, start=1):
        gid = (row.get("geonames_id") or "").strip()
        gn_hits = by_gn.get(gid, [])
        temporal_signal = _has_temporal_signal(row)
        if not gn_hits:
            out.append(
                {
                    "pleiades_id": (row.get("pleiades_id") or "").strip(),
                    "place_label": (row.get("place_label") or "").strip(),
                    "place_type": (row.get("place_type") or "").strip(),
                    "min_date": (row.get("min_date") or "").strip(),
                    "max_date": (row.get("max_date") or "").strip(),
                    "geonames_id": gid,
                    "geonames_label": (row.get("geonames_label") or "").strip(),
                    "geonames_feature_code": (row.get("geonames_feature_code") or "").strip(),
                    "wikidata_qid": "",
                    "wikidata_label": "",
                    "wikidata_latitude": "",
                    "wikidata_longitude": "",
                    "tgn_id": "",
                    "tgn_label": "",
                    "tgn_latitude": "",
                    "tgn_longitude": "",
                    "has_wikidata_match": "false",
                    "has_tgn_match": "false",
                    "has_temporal_signal": "true" if temporal_signal else "false",
                    "is_fully_triangulated": "false",
                    "is_full_chain_wikidata_tgn": "false",
                }
            )
        else:
            for wd in gn_hits:
                qid = wd["qid"]
                tgn_hits = by_qid_tgn.get(qid, [])
                if not tgn_hits:
                    out.append(
                        {
                            "pleiades_id": (row.get("pleiades_id") or "").strip(),
                            "place_label": (row.get("place_label") or "").strip(),
                            "place_type": (row.get("place_type") or "").strip(),
                            "min_date": (row.get("min_date") or "").strip(),
                            "max_date": (row.get("max_date") or "").strip(),
                            "geonames_id": gid,
                            "geonames_label": (row.get("geonames_label") or "").strip(),
                            "geonames_feature_code": (row.get("geonames_feature_code") or "").strip(),
                            "wikidata_qid": qid,
                            "wikidata_label": wd["wikidata_label"],
                            "wikidata_latitude": wd["wikidata_latitude"],
                            "wikidata_longitude": wd["wikidata_longitude"],
                            "tgn_id": "",
                            "tgn_label": "",
                            "tgn_latitude": "",
                            "tgn_longitude": "",
                            "has_wikidata_match": "true",
                            "has_tgn_match": "false",
                            "has_temporal_signal": "true" if temporal_signal else "false",
                            "is_fully_triangulated": "true" if temporal_signal else "false",
                            "is_full_chain_wikidata_tgn": "false",
                        }
                    )
                else:
                    for tgn in tgn_hits:
                        out.append(
                            {
                                "pleiades_id": (row.get("pleiades_id") or "").strip(),
                                "place_label": (row.get("place_label") or "").strip(),
                                "place_type": (row.get("place_type") or "").strip(),
                                "min_date": (row.get("min_date") or "").strip(),
                                "max_date": (row.get("max_date") or "").strip(),
                                "geonames_id": gid,
                                "geonames_label": (row.get("geonames_label") or "").strip(),
                                "geonames_feature_code": (row.get("geonames_feature_code") or "").strip(),
                                "wikidata_qid": qid,
                                "wikidata_label": wd["wikidata_label"],
                                "wikidata_latitude": wd["wikidata_latitude"],
                                "wikidata_longitude": wd["wikidata_longitude"],
                                "tgn_id": tgn["tgn_id"],
                                "tgn_label": tgn["tgn_label"],
                                "tgn_latitude": tgn["tgn_latitude"],
                                "tgn_longitude": tgn["tgn_longitude"],
                                "has_wikidata_match": "true",
                                "has_tgn_match": "true",
                                "has_temporal_signal": "true" if temporal_signal else "false",
                                "is_fully_triangulated": "true" if temporal_signal else "false",
                                "is_full_chain_wikidata_tgn": "true",
                            }
                        )
        if idx % 500 == 0 or idx == total:
            print(f"[crosswalk] processed {idx}/{total} pleiades-geonames rows", flush=True)
    out.sort(
        key=lambda r: (
            r["pleiades_id"],
            r["geonames_id"],
            r["wikidata_qid"],
            r["tgn_id"],
        )
    )
    return out


def _stats(
    *,
    geonames_ids: List[str],
    geonames_wikidata_rows: List[dict],
    crosswalk_rows: List[dict],
) -> dict:
    gn_with_wd = {r["geonames_id"] for r in geonames_wikidata_rows if r.get("geonames_id")}
    rows_with_wd = [r for r in crosswalk_rows if r.get("has_wikidata_match") == "true"]
    rows_with_tgn = [r for r in crosswalk_rows if r.get("has_tgn_match") == "true"]
    rows_triang = [r for r in crosswalk_rows if r.get("is_fully_triangulated") == "true"]
    rows_full_chain = [r for r in crosswalk_rows if r.get("is_full_chain_wikidata_tgn") == "true"]
    return {
        "distinct_geonames_ids_input": len(geonames_ids),
        "distinct_geonames_ids_with_wikidata": len(gn_with_wd),
        "geonames_wikidata_rows": len(geonames_wikidata_rows),
        "federated_crosswalk_rows": len(crosswalk_rows),
        "rows_with_wikidata": len(rows_with_wd),
        "rows_with_tgn": len(rows_with_tgn),
        "rows_fully_triangulated": len(rows_triang),
        "rows_full_chain_wikidata_tgn": len(rows_full_chain),
        "generated_at_epoch_seconds": int(time.time()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build GeoNames->Wikidata and merge with TGN mapping.")
    parser.add_argument(
        "--pleiades-geonames-csv",
        default="CSV/geographic/pleiades_geonames_crosswalk_v1.csv",
        help="Input Pleiades->GeoNames crosswalk CSV.",
    )
    parser.add_argument(
        "--tgn-wikidata-csv",
        default="Temporal/Data/tgn_wikidata_mapping.csv",
        help="Input TGN->Wikidata mapping CSV.",
    )
    parser.add_argument(
        "--out-geonames-wikidata-csv",
        default="CSV/geographic/geonames_wikidata_mapping_v1.csv",
        help="Output GeoNames->Wikidata mapping CSV.",
    )
    parser.add_argument(
        "--out-federated-crosswalk-csv",
        default="CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv",
        help="Output merged federated crosswalk CSV.",
    )
    parser.add_argument(
        "--out-stats-json",
        default="CSV/geographic/pleiades_geonames_wikidata_tgn_stats_v1.json",
        help="Output stats JSON.",
    )
    parser.add_argument("--batch-size", type=int, default=150, help="GeoNames IDs per SPARQL batch.")
    parser.add_argument("--timeout-seconds", type=int, default=120, help="SPARQL request timeout.")
    parser.add_argument("--max-retries", type=int, default=5, help="SPARQL request retry count.")
    parser.add_argument(
        "--pause-seconds",
        type=float,
        default=2.0,
        help="Base retry pause in seconds (multiplied by attempt).",
    )
    parser.add_argument(
        "--request-sleep-seconds",
        type=float,
        default=0.75,
        help="Sleep between successful SPARQL batches.",
    )
    parser.add_argument(
        "--max-geonames-ids",
        type=int,
        default=0,
        help="Optional cap for smoke tests (0 = all).",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    pleiades_geonames_csv = (project_root / args.pleiades_geonames_csv).resolve()
    tgn_wikidata_csv = (project_root / args.tgn_wikidata_csv).resolve()
    out_geonames_wikidata_csv = (project_root / args.out_geonames_wikidata_csv).resolve()
    out_federated_crosswalk_csv = (project_root / args.out_federated_crosswalk_csv).resolve()
    out_stats_json = (project_root / args.out_stats_json).resolve()

    if not pleiades_geonames_csv.exists():
        print(f"ERROR: missing input crosswalk: {pleiades_geonames_csv}")
        return 1
    if not tgn_wikidata_csv.exists():
        print(f"ERROR: missing TGN mapping file: {tgn_wikidata_csv}")
        return 1

    pleiades_geonames_rows = _read_csv_rows(pleiades_geonames_csv)
    tgn_rows = _read_csv_rows(tgn_wikidata_csv)
    geonames_ids = _collect_distinct_geonames_ids(pleiades_geonames_rows)
    if args.max_geonames_ids and args.max_geonames_ids > 0:
        geonames_ids = geonames_ids[: args.max_geonames_ids]

    existing_rows, existing_ids = _load_existing_geonames_wikidata_cache(out_geonames_wikidata_csv)
    geonames_wikidata_rows = build_geonames_wikidata_mapping(
        geonames_ids=geonames_ids,
        existing_rows=existing_rows,
        existing_ids=existing_ids,
        batch_size=max(1, args.batch_size),
        timeout_seconds=max(10, args.timeout_seconds),
        max_retries=max(1, args.max_retries),
        pause_seconds=max(0.5, args.pause_seconds),
        request_sleep_seconds=max(0.0, args.request_sleep_seconds),
    )
    _write_csv(
        out_geonames_wikidata_csv,
        geonames_wikidata_rows,
        [
            "geonames_id",
            "qid",
            "wikidata_label",
            "wikidata_latitude",
            "wikidata_longitude",
        ],
    )

    crosswalk_rows = build_federated_crosswalk(
        pleiades_geonames_rows=pleiades_geonames_rows,
        geonames_wikidata_rows=geonames_wikidata_rows,
        tgn_rows=tgn_rows,
    )
    _write_csv(
        out_federated_crosswalk_csv,
        crosswalk_rows,
        [
            "pleiades_id",
            "place_label",
            "place_type",
            "min_date",
            "max_date",
            "geonames_id",
            "geonames_label",
            "geonames_feature_code",
            "wikidata_qid",
            "wikidata_label",
            "wikidata_latitude",
            "wikidata_longitude",
            "tgn_id",
            "tgn_label",
            "tgn_latitude",
            "tgn_longitude",
            "has_wikidata_match",
            "has_tgn_match",
            "has_temporal_signal",
            "is_fully_triangulated",
            "is_full_chain_wikidata_tgn",
        ],
    )

    stats = _stats(
        geonames_ids=geonames_ids,
        geonames_wikidata_rows=geonames_wikidata_rows,
        crosswalk_rows=crosswalk_rows,
    )
    out_stats_json.parent.mkdir(parents=True, exist_ok=True)
    with out_stats_json.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print("[done] GeoNames->Wikidata mapping and federated crosswalk built.", flush=True)
    print(f"  Input Pleiades->GeoNames: {pleiades_geonames_csv}", flush=True)
    print(f"  Input TGN->Wikidata: {tgn_wikidata_csv}", flush=True)
    print(f"  Output GeoNames->Wikidata: {out_geonames_wikidata_csv}", flush=True)
    print(f"  Output federated crosswalk: {out_federated_crosswalk_csv}", flush=True)
    print(f"  Output stats: {out_stats_json}", flush=True)
    print(
        "  Summary: "
        f"distinct_geonames_ids_with_wikidata={stats['distinct_geonames_ids_with_wikidata']}, "
        f"rows_full_chain_wikidata_tgn={stats['rows_full_chain_wikidata_tgn']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
