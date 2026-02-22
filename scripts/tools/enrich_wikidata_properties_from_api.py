#!/usr/bin/env python3
"""Enrich a raw Wikidata property CSV using the Wikidata API.

Input CSV can contain either:
- `property` column with full URIs (e.g., http://www.wikidata.org/entity/P31), or
- `property` / `pid` column with IDs (e.g., P31).

The script queries wbgetentities in batches and writes an enriched CSV with:
- pid
- property (URI)
- propertyLabel
- propertyDescription
- propertyAltLabels (pipe-separated)
- datatype

Usage:
  python scripts/tools/enrich_wikidata_properties_from_api.py ^
    --input CSV/wikiPvalues_raw.csv ^
    --output CSV/wikiPvalues_enriched.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path
from typing import Dict, List

import requests


API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1PropertyEnricher/1.0 (local script)"
PID_RE = re.compile(r"(P\d+)$", re.IGNORECASE)


def normalize_pid(value: str) -> str:
    if not value:
        return ""
    value = value.strip()
    m = PID_RE.search(value)
    return m.group(1).upper() if m else ""


def chunks(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def get_entities_batch(ids: List[str], max_retries: int = 4, sleep_s: float = 0.6) -> Dict[str, dict]:
    headers = {"User-Agent": USER_AGENT}
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": "|".join(ids),
        "languages": "en",
        "props": "labels|descriptions|aliases|datatype",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(API_URL, params=params, headers=headers, timeout=40)
            resp.raise_for_status()
            data = resp.json()
            return data.get("entities", {})
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(sleep_s * (attempt + 1))
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output enriched CSV path")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="IDs per API call (default: 50 for anonymous requests)",
    )
    parser.add_argument(
        "--sleep-ms",
        type=int,
        default=100,
        help="Delay between requests in milliseconds",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        raise FileNotFoundError(in_path)

    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not reader.fieldnames:
            raise RuntimeError("Input CSV has no header.")
        fieldnames = list(reader.fieldnames)

    pid_source_col = "pid" if "pid" in fieldnames else "property"
    pids: List[str] = []
    for r in rows:
        pid = normalize_pid(r.get(pid_source_col, ""))
        if not pid:
            pid = normalize_pid(r.get("property", ""))
        r["_pid"] = pid
        if pid:
            pids.append(pid)

    unique_pids = sorted(set(pids), key=lambda x: int(x[1:]))
    print(f"rows={len(rows)}")
    print(f"rows_with_pid={sum(1 for r in rows if r.get('_pid'))}")
    print(f"unique_pids={len(unique_pids)}")

    entity_map: Dict[str, dict] = {}
    req_batches = chunks(unique_pids, max(1, args.batch_size))
    for i, batch in enumerate(req_batches, start=1):
        ents = get_entities_batch(batch)
        entity_map.update(ents)
        if i % 10 == 0 or i == len(req_batches):
            print(f"fetched_batches={i}/{len(req_batches)}")
        time.sleep(max(0, args.sleep_ms) / 1000.0)

    extra_cols = [
        "pid",
        "property",
        "propertyLabel",
        "propertyDescription",
        "propertyAltLabels",
        "datatype",
        "enrich_status",
    ]
    out_fields = [c for c in fieldnames if c not in extra_cols] + extra_cols

    enriched_count = 0
    for r in rows:
        pid = r.get("_pid", "")
        r["pid"] = pid
        r["property"] = f"http://www.wikidata.org/entity/{pid}" if pid else ""
        if not pid:
            r["propertyLabel"] = ""
            r["propertyDescription"] = ""
            r["propertyAltLabels"] = ""
            r["datatype"] = ""
            r["enrich_status"] = "missing_pid"
            continue

        ent = entity_map.get(pid, {})
        labels = ent.get("labels", {})
        desc = ent.get("descriptions", {})
        aliases = ent.get("aliases", {})

        r["propertyLabel"] = labels.get("en", {}).get("value", "")
        r["propertyDescription"] = desc.get("en", {}).get("value", "")
        r["datatype"] = ent.get("datatype", "")

        alias_vals = []
        for a in aliases.get("en", []) or []:
            v = (a or {}).get("value", "").strip()
            if v:
                alias_vals.append(v)
        r["propertyAltLabels"] = " | ".join(alias_vals)

        if r["propertyLabel"] or r["propertyDescription"] or r["datatype"]:
            r["enrich_status"] = "ok"
            enriched_count += 1
        else:
            r["enrich_status"] = "not_found"

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for r in rows:
            r.pop("_pid", None)
            writer.writerow({k: r.get(k, "") for k in out_fields})

    print(f"enriched_rows={enriched_count}")
    print(f"output={out_path}")


if __name__ == "__main__":
    main()

