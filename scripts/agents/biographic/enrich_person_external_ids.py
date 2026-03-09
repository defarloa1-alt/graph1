#!/usr/bin/env python3
"""
Enrich Person nodes with external IDs from Wikidata.

For each Person node with a qid, fetches Wikidata claims and extracts:
- P214  → viaf_id (VIAF)
- P227  → gnd_id (GND)
- P244  → loc_authority_id (Library of Congress)
- P2163 → fast_id (FAST)
- P213  → isni (ISNI)
- P268  → bnf_id (BnF)
- P269  → idref_id (IdRef)
- P949  → nli_id (National Library of Israel)
- P31   → instance_of (pipe-delimited labels)
- P569  → birth_year (date of birth)
- P570  → death_year (date of death)
- P21   → gender (sex or gender label)
- P106  → occupation (pipe-delimited labels)
- P27   → citizenship (pipe-delimited labels)

Uses coalesce to avoid overwriting existing non-null values.
Idempotent (MERGE-based writes). Batched Neo4j writes (200 per batch).

Usage:
  python scripts/agents/biographic/enrich_person_external_ids.py --dry-run
  python scripts/agents/biographic/enrich_person_external_ids.py
  python scripts/agents/biographic/enrich_person_external_ids.py --limit 100
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
LANG_PREF = ["en", "la", "de", "fr", "it", "es", "sv", "ru", "ja", "zh", "ar", "mul"]

# PID → property name mapping for external IDs
EXTERNAL_ID_PIDS = {
    "P214":  "viaf_id",
    "P227":  "gnd_id",
    "P244":  "loc_authority_id",
    "P2163": "fast_id",
    "P213":  "isni",
    "P268":  "bnf_id",
    "P269":  "idref_id",
    "P949":  "nli_id",
}

# PID → property for item-valued claims (resolve to labels)
ITEM_PIDS = {
    "P31":  "instance_of",
    "P106": "occupation",
    "P27":  "citizenship",
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
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("time", value.get("value", ""))
    text = str(value).strip()
    if not text:
        return None
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


def _statement_gender_label(stmt: dict) -> Optional[str]:
    """Extract gender QID and map to label."""
    qid = _statement_qid(stmt)
    gender_map = {
        "Q6581097": "male",
        "Q6581072": "female",
        "Q1097630": "intersex",
        "Q1052281": "transgender female",
        "Q2449503": "transgender male",
    }
    if qid:
        return gender_map.get(qid, qid)
    return None


def _chunked(items: list, size: int) -> list:
    return [items[i : i + size] for i in range(0, len(items), size)]


def fetch_entities(
    qids: List[str],
    *,
    batch_size: int = 50,
    timeout: int = 180,
    pause: float = 0.4,
) -> Dict[str, dict]:
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
            headers={"User-Agent": "Chrystallum-Graph1/1.0 (enrich-person-external-ids)"},
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


def resolve_item_labels(
    entities: Dict[str, dict],
    item_qids_per_person: Dict[str, Dict[str, List[str]]],
) -> Dict[str, Dict[str, List[str]]]:
    """Resolve item QIDs to labels for P31/P106/P27.

    item_qids_per_person: {person_qid: {prop_name: [qid1, qid2, ...]}}
    Returns: {person_qid: {prop_name: [label1, label2, ...]}}
    """
    all_item_qids = set()
    for prop_map in item_qids_per_person.values():
        for qids in prop_map.values():
            all_item_qids.update(qids)

    qid_to_label: Dict[str, str] = {}
    for qid in all_item_qids:
        if qid in entities and entities[qid].get("missing") != "":
            label = _best_label(entities[qid].get("labels", {}))
            if label:
                qid_to_label[qid] = label

    missing = [q for q in all_item_qids if q not in qid_to_label]
    if missing:
        print(f"  Fetching {len(missing)} item entities for labels...", flush=True)
        extra = fetch_entities(missing, batch_size=50, pause=0.4)
        for qid, entity in extra.items():
            if entity.get("missing") != "":
                label = _best_label(entity.get("labels", {}))
                if label:
                    qid_to_label[qid] = label

    result: Dict[str, Dict[str, List[str]]] = {}
    for person_qid, prop_map in item_qids_per_person.items():
        result[person_qid] = {}
        for prop_name, qids in prop_map.items():
            labels = [qid_to_label.get(q, q) for q in qids]
            if labels:
                result[person_qid][prop_name] = labels
    return result


def extract_person_data(entity: dict) -> dict:
    """Extract external IDs, item properties, birth/death years, gender from entity."""
    claims = entity.get("claims", {})
    result: Dict[str, Any] = {}

    # External IDs
    for pid, prop_name in EXTERNAL_ID_PIDS.items():
        for stmt in claims.get(pid, []):
            val = _statement_string_value(stmt)
            if val:
                result[prop_name] = val
                break

    # Item-valued properties (collect QIDs for batch label resolution)
    item_qids: Dict[str, List[str]] = {}
    for pid, prop_name in ITEM_PIDS.items():
        qids = []
        for stmt in claims.get(pid, []):
            qid = _statement_qid(stmt)
            if qid and qid not in qids:
                qids.append(qid)
        if qids:
            item_qids[prop_name] = qids
    result["_item_qids"] = item_qids

    # P569 birth year
    for stmt in claims.get("P569", []):
        year = _statement_time_year(stmt)
        if year is not None:
            result["birth_year"] = year
            break

    # P570 death year
    for stmt in claims.get("P570", []):
        year = _statement_time_year(stmt)
        if year is not None:
            result["death_year"] = year
            break

    # P21 gender
    for stmt in claims.get("P21", []):
        label = _statement_gender_label(stmt)
        if label:
            result["gender"] = label
            break

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich Person nodes with Wikidata external IDs"
    )
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true", help="Report only, no writes")
    parser.add_argument("--limit", type=int, default=None, help="Limit persons to process")
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

    # ── Step 1: Read Person nodes with QIDs ──
    print("Reading Person nodes from Neo4j...", flush=True)
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Person)
            WHERE p.qid IS NOT NULL
            RETURN p.qid AS qid,
                   p.viaf_id AS viaf_id,
                   p.gnd_id AS gnd_id,
                   p.loc_authority_id AS loc_authority_id,
                   p.lcnaf_id AS lcnaf_id,
                   p.fast_id AS fast_id,
                   p.isni AS isni,
                   p.bnf_id AS bnf_id,
                   p.idref_id AS idref_id,
                   p.nli_id AS nli_id,
                   p.instance_of AS instance_of,
                   p.occupation AS occupation,
                   p.citizenship AS citizenship,
                   p.birth_year AS birth_year,
                   p.death_year AS death_year,
                   p.gender AS gender
            """
        )
        rows = list(result)
        if args.limit:
            rows = rows[: args.limit]

    # Deduplicate by qid
    qid_to_row: Dict[str, dict] = {}
    for r in rows:
        qid = r["qid"]
        if qid not in qid_to_row:
            qid_to_row[qid] = dict(r)

    qids = list(qid_to_row.keys())
    print(f"Found {len(rows)} Person nodes with qid ({len(qids)} distinct QIDs)", flush=True)

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
    item_qids_per_person: Dict[str, Dict[str, List[str]]] = {}

    for qid in qids:
        entity = entities.get(qid)
        if not entity or entity.get("missing") == "":
            continue

        row = qid_to_row[qid]
        data = extract_person_data(entity)

        update: Dict[str, Any] = {"qid": qid}
        has_change = False

        # External IDs — only fill if graph value is null
        for pid, prop_name in EXTERNAL_ID_PIDS.items():
            new_val = data.get(prop_name)
            existing = row.get(prop_name)
            # Also check lcnaf_id as alternate for loc_authority_id
            if prop_name == "loc_authority_id" and not existing:
                existing = row.get("lcnaf_id")
            if new_val and not existing:
                update[prop_name] = new_val
                has_change = True

        # Item-valued properties (instance_of, occupation, citizenship)
        item_qids = data.get("_item_qids", {})
        for prop_name in ITEM_PIDS.values():
            if prop_name in item_qids and not row.get(prop_name):
                if qid not in item_qids_per_person:
                    item_qids_per_person[qid] = {}
                item_qids_per_person[qid][prop_name] = item_qids[prop_name]
                has_change = True

        # Birth year
        birth = data.get("birth_year")
        if birth is not None and row.get("birth_year") is None:
            update["birth_year"] = birth
            has_change = True

        # Death year
        death = data.get("death_year")
        if death is not None and row.get("death_year") is None:
            update["death_year"] = death
            has_change = True

        # Gender
        gender = data.get("gender")
        if gender and not row.get("gender"):
            update["gender"] = gender
            has_change = True

        if has_change:
            updates.append(update)

    # ── Step 3b: Resolve item labels ──
    if item_qids_per_person:
        resolved = resolve_item_labels(entities, item_qids_per_person)
        for update in updates:
            qid = update["qid"]
            if qid in resolved:
                for prop_name, labels in resolved[qid].items():
                    update[prop_name] = "|".join(labels)

    # ── Step 4: Summary ──
    all_props = list(EXTERNAL_ID_PIDS.values()) + list(ITEM_PIDS.values()) + [
        "birth_year", "death_year", "gender"
    ]
    counts: Dict[str, int] = {}
    for prop_name in all_props:
        counts[prop_name] = sum(1 for u in updates if prop_name in u and u[prop_name] is not None)

    print(f"\n--- Enrichment summary ({len(updates)} Person nodes to update) ---")
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
                MATCH (p:Person {qid: row.qid})
                SET
                    p.viaf_id           = coalesce(p.viaf_id,           row.viaf_id),
                    p.gnd_id            = coalesce(p.gnd_id,            row.gnd_id),
                    p.loc_authority_id   = coalesce(p.loc_authority_id,  row.loc_authority_id),
                    p.fast_id           = coalesce(p.fast_id,           row.fast_id),
                    p.isni              = coalesce(p.isni,              row.isni),
                    p.bnf_id            = coalesce(p.bnf_id,            row.bnf_id),
                    p.idref_id          = coalesce(p.idref_id,          row.idref_id),
                    p.nli_id            = coalesce(p.nli_id,            row.nli_id),
                    p.instance_of       = coalesce(p.instance_of,       row.instance_of),
                    p.occupation        = coalesce(p.occupation,        row.occupation),
                    p.citizenship       = coalesce(p.citizenship,       row.citizenship),
                    p.birth_year        = coalesce(p.birth_year,        row.birth_year),
                    p.death_year        = coalesce(p.death_year,        row.death_year),
                    p.gender            = coalesce(p.gender,            row.gender),
                    p.external_ids_enriched = true,
                    p.external_ids_enriched_at = datetime()
                """,
                rows=batch,
            )
        total_written += len(batch)
        print(f"  Written {total_written}/{len(updates)}", flush=True)

    driver.close()
    print(f"\nDone. Updated {total_written} Person nodes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
