#!/usr/bin/env python3
"""
Enrich Place nodes with external IDs from Wikidata.

For each Place node with a qid, fetches Wikidata claims and extracts:
- P1566 → geonames_id (GeoNames)
- P1667 → tgn_id (Getty TGN)
- P214  → viaf_id (VIAF)
- P227  → gnd_id (GND)
- P244  → loc_authority_id (Library of Congress)
- P2163 → fast_id (FAST)
- P268  → bnf_id (BnF)
- P269  → idref_id (IdRef)
- P402  → osm_relation_id (OpenStreetMap)
- P590  → gnis_id (GNIS)
- P1584 → pleiades_id (Pleiades, backfill if missing)
- P31   → instance_of (pipe-delimited labels)
- P571  → inception_year
- P576  → dissolved_year

Uses coalesce to avoid overwriting existing non-null values.
Idempotent (MERGE-based writes). Batched Neo4j writes (200 per batch).

Usage:
  python scripts/backbone/geographic/enrich_place_external_ids.py --dry-run
  python scripts/backbone/geographic/enrich_place_external_ids.py
  python scripts/backbone/geographic/enrich_place_external_ids.py --limit 100
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
LANG_PREF = ["en", "sv", "de", "fr", "es", "it", "ru", "ja", "zh", "ar", "la", "mul"]

# PID → property name mapping for external IDs
EXTERNAL_ID_PIDS = {
    "P1566": "geonames_id",
    "P1667": "tgn_id",
    "P214":  "viaf_id",
    "P227":  "gnd_id",
    "P244":  "loc_authority_id",
    "P2163": "fast_id",
    "P268":  "bnf_id",
    "P269":  "idref_id",
    "P402":  "osm_relation_id",
    "P590":  "gnis_id",
    # P1584 (pleiades_id) excluded — uniqueness constraint; 42k Places already have it from Pleiades import
}

NEO4J_WRITE_BATCH = 200


def _best_label(labels_obj: dict) -> str:
    for lang in LANG_PREF:
        if lang in labels_obj:
            return labels_obj[lang].get("value", "")
    if labels_obj:
        return next(iter(labels_obj.values())).get("value", "")
    return ""


def _statement_string_value(stmt: dict) -> Optional[str]:
    """Extract string value from an external-id or string statement."""
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return None
    dv = mainsnak.get("datavalue", {})
    if not dv:
        return None
    val = dv.get("value")
    if isinstance(val, str):
        return val.strip() if val.strip() else None
    return None


def _statement_qid(stmt: dict) -> Optional[str]:
    """Extract QID from a wikibase-item statement."""
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return None
    if mainsnak.get("datatype") != "wikibase-item":
        return None
    value = mainsnak.get("datavalue", {}).get("value", {})
    qid = value.get("id")
    if qid:
        return qid
    numeric_id = value.get("numeric-id")
    if numeric_id is None:
        return None
    return f"Q{numeric_id}"


def _parse_wikidata_year(value: Any) -> Optional[int]:
    """Extract year from Wikidata time value (e.g. +0200-01-01T00:00:00Z or -0100-00-00T00:00:00Z)."""
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("time", value.get("value", ""))
    text = str(value).strip()
    if not text:
        return None
    # Handle leading + or -
    negative = False
    if text.startswith("-"):
        negative = True
        text = text[1:]
    elif text.startswith("+"):
        text = text[1:]
    if "T" in text:
        text = text.split("T", 1)[0]
    parts = text.split("-")
    if not parts or not parts[0]:
        return None
    digits = parts[0]
    if not digits.isdigit():
        return None
    year = int(digits)
    return -year if negative else year


def _statement_time_year(stmt: dict) -> Optional[int]:
    """Extract year from a time-valued statement."""
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return None
    dv = mainsnak.get("datavalue", {})
    if not dv:
        return None
    val = dv.get("value", {})
    if isinstance(val, dict):
        return _parse_wikidata_year(val.get("time"))
    return _parse_wikidata_year(val)


def _chunked(items: list, size: int) -> list:
    return [items[i : i + size] for i in range(0, len(items), size)]


def fetch_entities(
    qids: List[str],
    *,
    batch_size: int = 50,
    timeout: int = 180,
    pause: float = 0.4,
) -> Dict[str, dict]:
    """Batch-fetch entities from Wikidata wbgetentities API."""
    out: Dict[str, dict] = {}
    batches = _chunked(qids, batch_size)
    for i, batch in enumerate(batches):
        params = urllib.parse.urlencode(
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "format": "json",
                "props": "labels|claims",
                "languages": "|".join(LANG_PREF),
            }
        )
        req = urllib.request.Request(
            f"{WIKIDATA_API}?{params}",
            headers={"User-Agent": "Chrystallum-Graph1/1.0 (enrich-place-external-ids)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            out.update(payload.get("entities", {}))
        except Exception as e:
            print(f"  WARNING: Batch {i+1}/{len(batches)} failed: {e}", file=sys.stderr)
        if i < len(batches) - 1:
            time.sleep(pause)
        if (i + 1) % 20 == 0:
            print(f"  Fetched {(i+1)*batch_size}/{len(qids)} entities...", flush=True)
    return out


def resolve_instance_of_labels(
    entities: Dict[str, dict],
    instance_of_qids_per_place: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """Resolve P31 QIDs to labels. Returns {place_qid: [label1, label2, ...]}."""
    # Collect all unique P31 QIDs that need labels
    all_p31_qids = set()
    for qids in instance_of_qids_per_place.values():
        all_p31_qids.update(qids)

    # Labels we already have from fetched entities
    qid_to_label: Dict[str, str] = {}
    for qid in all_p31_qids:
        if qid in entities and entities[qid].get("missing") != "":
            label = _best_label(entities[qid].get("labels", {}))
            if label:
                qid_to_label[qid] = label

    # Fetch any missing P31 QIDs
    missing = [q for q in all_p31_qids if q not in qid_to_label]
    if missing:
        print(f"  Fetching {len(missing)} P31 instance-of entities for labels...", flush=True)
        extra = fetch_entities(missing, batch_size=50, pause=0.4)
        for qid, entity in extra.items():
            if entity.get("missing") != "":
                label = _best_label(entity.get("labels", {}))
                if label:
                    qid_to_label[qid] = label

    # Build result
    result: Dict[str, List[str]] = {}
    for place_qid, p31_qids in instance_of_qids_per_place.items():
        labels = []
        for q in p31_qids:
            label = qid_to_label.get(q, q)
            labels.append(label)
        if labels:
            result[place_qid] = labels
    return result


def extract_external_ids(entity: dict) -> dict:
    """Extract external IDs, P31 instance-of QIDs, P571 inception, P576 dissolved from entity."""
    claims = entity.get("claims", {})
    result: Dict[str, Any] = {}

    # External IDs
    for pid, prop_name in EXTERNAL_ID_PIDS.items():
        for stmt in claims.get(pid, []):
            val = _statement_string_value(stmt)
            if val:
                result[prop_name] = val
                break

    # P31 instance_of QIDs (collect all)
    p31_qids: List[str] = []
    for stmt in claims.get("P31", []):
        qid = _statement_qid(stmt)
        if qid and qid not in p31_qids:
            p31_qids.append(qid)
    result["_p31_qids"] = p31_qids

    # P571 inception year
    for stmt in claims.get("P571", []):
        year = _statement_time_year(stmt)
        if year is not None:
            result["inception_year"] = year
            break

    # P576 dissolved/abolished year
    for stmt in claims.get("P576", []):
        year = _statement_time_year(stmt)
        if year is not None:
            result["dissolved_year"] = year
            break

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich Place nodes with Wikidata external IDs (P1566, P1667, P214, etc.)"
    )
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true", help="Report only, no writes")
    parser.add_argument("--limit", type=int, default=None, help="Limit places to process (for testing)")
    args = parser.parse_args()

    if not args.password:
        print("NEO4J_PASSWORD required (set in .env or --password)", file=sys.stderr)
        return 1

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    # ── Step 1: Read Place nodes with QIDs ──
    print("Reading Place nodes from Neo4j...", flush=True)
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Place)
            WHERE p.qid IS NOT NULL
            RETURN p.qid AS qid,
                   p.geonames_id AS geonames_id,
                   p.tgn_id AS tgn_id,
                   p.viaf_id AS viaf_id,
                   p.gnd_id AS gnd_id,
                   p.loc_authority_id AS loc_authority_id,
                   p.fast_id AS fast_id,
                   p.bnf_id AS bnf_id,
                   p.idref_id AS idref_id,
                   p.osm_relation_id AS osm_relation_id,
                   p.gnis_id AS gnis_id,
                   p.instance_of AS instance_of,
                   p.inception_year AS inception_year,
                   p.dissolved_year AS dissolved_year
            """
        )
        rows = list(result)
        if args.limit:
            rows = rows[: args.limit]

    # Deduplicate by qid (keep first seen)
    qid_to_row: Dict[str, dict] = {}
    for r in rows:
        qid = r["qid"]
        if qid not in qid_to_row:
            qid_to_row[qid] = dict(r)

    qids = list(qid_to_row.keys())
    print(f"Found {len(rows)} Place nodes with qid ({len(qids)} distinct QIDs)", flush=True)

    if not qids:
        print("Nothing to do.")
        driver.close()
        return 0

    # ── Step 2: Fetch from Wikidata ──
    print(f"Fetching {len(qids)} entities from Wikidata API (50/batch, 0.4s pause)...", flush=True)
    entities = fetch_entities(qids, batch_size=50, pause=0.4)
    print(f"  Received {len(entities)} entities", flush=True)

    # ── Step 3: Extract data ──
    updates: List[dict] = []
    instance_of_qids_per_place: Dict[str, List[str]] = {}

    for qid in qids:
        entity = entities.get(qid)
        if not entity or entity.get("missing") == "":
            continue

        row = qid_to_row[qid]
        data = extract_external_ids(entity)

        # Build update dict: only include fields where graph value is null/missing
        update: Dict[str, Any] = {"qid": qid}
        has_change = False

        for pid, prop_name in EXTERNAL_ID_PIDS.items():
            new_val = data.get(prop_name)
            if new_val and not row.get(prop_name):
                update[prop_name] = new_val
                has_change = True

        # P31 instance_of
        p31_qids = data.get("_p31_qids", [])
        if p31_qids and not row.get("instance_of"):
            instance_of_qids_per_place[qid] = p31_qids
            has_change = True

        # P571 inception_year
        inception = data.get("inception_year")
        if inception is not None and row.get("inception_year") is None:
            update["inception_year"] = inception
            has_change = True

        # P576 dissolved_year
        dissolved = data.get("dissolved_year")
        if dissolved is not None and row.get("dissolved_year") is None:
            update["dissolved_year"] = dissolved
            has_change = True

        if has_change:
            updates.append(update)

    # ── Step 3b: Resolve P31 labels ──
    if instance_of_qids_per_place:
        instance_of_labels = resolve_instance_of_labels(entities, instance_of_qids_per_place)
        for update in updates:
            qid = update["qid"]
            if qid in instance_of_labels:
                update["instance_of"] = "|".join(instance_of_labels[qid])

    # ── Step 4: Summary ──
    counts: Dict[str, int] = {}
    for prop_name in list(EXTERNAL_ID_PIDS.values()) + ["instance_of", "inception_year", "dissolved_year"]:
        counts[prop_name] = sum(1 for u in updates if prop_name in u and u[prop_name] is not None)

    print(f"\n--- Enrichment summary ({len(updates)} Place nodes to update) ---")
    for prop, count in sorted(counts.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {prop}: {count} new values")

    if args.dry_run:
        print("\n[DRY RUN] No writes performed.")
        if updates:
            print("\nSample updates:")
            for u in updates[:10]:
                props = {k: v for k, v in u.items() if k != "qid" and v is not None}
                print(f"  {u['qid']}: {props}")
        driver.close()
        return 0

    if not updates:
        print("Nothing to update.")
        driver.close()
        return 0

    # ── Step 5: Write to Neo4j in batches ──
    print(f"\nWriting to Neo4j ({NEO4J_WRITE_BATCH} per batch)...", flush=True)
    total_written = 0

    for batch in _chunked(updates, NEO4J_WRITE_BATCH):
        with driver.session() as session:
            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Place {qid: row.qid})
                SET
                    p.geonames_id       = coalesce(p.geonames_id,       row.geonames_id),
                    p.tgn_id            = coalesce(p.tgn_id,            row.tgn_id),
                    p.viaf_id           = coalesce(p.viaf_id,           row.viaf_id),
                    p.gnd_id            = coalesce(p.gnd_id,            row.gnd_id),
                    p.loc_authority_id   = coalesce(p.loc_authority_id,  row.loc_authority_id),
                    p.fast_id           = coalesce(p.fast_id,           row.fast_id),
                    p.bnf_id            = coalesce(p.bnf_id,            row.bnf_id),
                    p.idref_id          = coalesce(p.idref_id,          row.idref_id),
                    p.osm_relation_id   = coalesce(p.osm_relation_id,  row.osm_relation_id),
                    p.gnis_id           = coalesce(p.gnis_id,           row.gnis_id),
                    p.instance_of       = coalesce(p.instance_of,       row.instance_of),
                    p.inception_year    = coalesce(p.inception_year,     row.inception_year),
                    p.dissolved_year    = coalesce(p.dissolved_year,     row.dissolved_year),
                    p.external_ids_enriched = true,
                    p.external_ids_enriched_at = datetime()
                """,
                rows=batch,
            )
        total_written += len(batch)
        print(f"  Written {total_written}/{len(updates)}", flush=True)

    driver.close()
    print(f"\nDone. Updated {total_written} Place nodes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
