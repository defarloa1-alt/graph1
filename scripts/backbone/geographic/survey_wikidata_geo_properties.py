#!/usr/bin/env python3
"""
Survey Wikidata for geographic properties, instance_of/subclass_of hierarchies, and external IDs.

Analogous to what biographic/agent.py does for Person — this samples the geographic property
landscape from Wikidata to understand:
  1. Which P-codes are geographic (spatial, admin, topographic, hydrographic, etc.)
  2. What instance_of (P31) classes exist for geographic entities
  3. What subclass_of (P279) hierarchies those classes belong to
  4. Which external ID properties appear on geographic entities (authority IDs = SFA routing)

Sampling strategy:
  - Start from well-known geographic root classes (city, river, mountain, etc.)
  - Sample N entities from each class via SPARQL
  - For each entity, harvest ALL properties to discover which P-codes appear on geo entities
  - Collect external IDs as potential SFA routing signals
  - Build frequency tables for analysis

Output:
  output/geo_discovery/geo_property_survey.csv         — per-entity property inventory
  output/geo_discovery/geo_property_frequencies.csv     — P-code frequency table
  output/geo_discovery/geo_external_ids.csv             — external ID frequency table
  output/geo_discovery/geo_class_hierarchy.csv          — instance_of / subclass_of tree
  output/geo_discovery/geo_survey_report.txt            — human-readable analysis

Usage:
  python scripts/backbone/geographic/survey_wikidata_geo_properties.py
  python scripts/backbone/geographic/survey_wikidata_geo_properties.py --samples 20
  python scripts/backbone/geographic/survey_wikidata_geo_properties.py --dry-run
"""

import argparse
import csv
import io
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# Fix Windows cp1252 encoding for Unicode box-drawing chars
if sys.stdout.encoding and sys.stdout.encoding.lower().startswith("cp"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "ChrystallumBot/1.0 (geographic property survey)"

PROJECT = Path(__file__).resolve().parents[3]
OUT_DIR = PROJECT / "output" / "geo_discovery"

# ── Geographic root classes to sample from ──────────────────────────────────
# Each: (QID, label, description)
# These are the instance_of targets — we sample entities that are P31 of these
GEO_ROOT_CLASSES = [
    # Settlements
    ("Q515",     "city",                    "major settlement"),
    ("Q3957",    "town",                    "medium settlement"),
    ("Q532",     "village",                 "small settlement"),
    ("Q486972",  "human settlement",        "generic settlement"),
    ("Q3024240", "historical country",      "country that no longer exists"),
    # Political/admin
    ("Q6256",    "country",                 "sovereign state"),
    ("Q10864048","first-level admin division", "province/state/region"),
    ("Q13220204","second-level admin div",  "county/district"),
    # Physical geography
    ("Q8502",    "mountain",                "elevated landform"),
    ("Q23442",   "island",                  "land surrounded by water"),
    ("Q34763",   "peninsula",               "land projecting into water"),
    ("Q39816",   "valley",                  "low area between hills"),
    ("Q5107",    "continent",               "major landmass"),
    # Hydrography
    ("Q4022",    "river",                   "flowing body of water"),
    ("Q23397",   "lake",                    "inland body of water"),
    ("Q165",     "sea",                     "large body of salt water"),
    ("Q34038",   "waterfall",               "water flowing over a drop"),
    # Ancient/historical
    ("Q839954",  "archaeological site",     "place of past human activity"),
    ("Q1549591", "big city",                "large urban area"),
    ("Q15661340","ancient city",            "city from antiquity"),
    # Infrastructure
    ("Q12280",   "bridge",                  "structure spanning obstacle"),
    ("Q34442",   "road",                    "route for travel"),
    ("Q44782",   "port",                    "facility for ships"),
    ("Q16917",   "hospital",               "healthcare institution"),
    ("Q23413",   "castle",                  "fortified structure"),
]


def query_wikidata(sparql: str, max_retries: int = 3) -> dict | None:
    """Execute SPARQL query with retry logic."""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": USER_AGENT,
    }
    for attempt in range(max_retries):
        try:
            r = requests.get(SPARQL_URL, params={"query": sparql}, headers=headers, timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                wait = (attempt + 1) * 15
                print(f"  Rate limit, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP {r.status_code}: {r.reason}")
                time.sleep(5)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)
    return None


def fetch_labels_via_api(qids: list[str]) -> dict[str, str]:
    """Fetch English labels for QIDs via Wikidata API."""
    if not qids:
        return {}
    result = {}
    for i in range(0, len(qids), 50):
        batch = qids[i:i + 50]
        try:
            r = requests.get(
                WIKIDATA_API,
                params={
                    "action": "wbgetentities",
                    "ids": "|".join(batch),
                    "props": "labels",
                    "languages": "en",
                    "format": "json",
                },
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            if r.status_code == 200:
                data = r.json()
                for qid in batch:
                    ent = data.get("entities", {}).get(qid, {})
                    lbl = ent.get("labels", {}).get("en", {}).get("value", "")
                    if lbl:
                        result[qid] = lbl
        except Exception as e:
            print(f"  Label fetch error: {e}")
        time.sleep(0.3)
    return result


def fetch_entity_claims(qid: str) -> dict:
    """Fetch all claims for an entity via Wikidata API."""
    try:
        r = requests.get(
            WIKIDATA_API,
            params={
                "action": "wbgetentities",
                "ids": qid,
                "props": "claims|labels|descriptions",
                "languages": "en",
                "format": "json",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("entities", {}).get(qid, {})
    except Exception as e:
        print(f"  Entity fetch error for {qid}: {e}")
    return {}


def extract_property_profile(entity: dict) -> dict:
    """Extract a property profile from entity claims."""
    claims = entity.get("claims", {})
    label = entity.get("labels", {}).get("en", {}).get("value", "")
    desc = entity.get("descriptions", {}).get("en", {}).get("value", "")

    profile = {
        "label": label,
        "description": desc,
        "property_pids": [],
        "external_ids": [],
        "instance_of": [],
        "subclass_of": [],
        "part_of": [],
        "coordinates": None,
    }

    for pid, statements in claims.items():
        profile["property_pids"].append(pid)

        for stmt in statements:
            mainsnak = stmt.get("mainsnak", {})
            datatype = mainsnak.get("datatype", "")
            datavalue = mainsnak.get("datavalue", {})

            # Collect external IDs
            if datatype == "external-id":
                val = datavalue.get("value", "")
                profile["external_ids"].append((pid, val))

            # Instance of (P31)
            if pid == "P31" and datavalue.get("type") == "wikibase-entityid":
                qid_val = "Q" + str(datavalue["value"].get("numeric-id", ""))
                profile["instance_of"].append(qid_val)

            # Subclass of (P279)
            if pid == "P279" and datavalue.get("type") == "wikibase-entityid":
                qid_val = "Q" + str(datavalue["value"].get("numeric-id", ""))
                profile["subclass_of"].append(qid_val)

            # Part of (P361)
            if pid == "P361" and datavalue.get("type") == "wikibase-entityid":
                qid_val = "Q" + str(datavalue["value"].get("numeric-id", ""))
                profile["part_of"].append(qid_val)

            # Coordinates (P625)
            if pid == "P625" and datavalue.get("type") == "globecoordinate":
                coords = datavalue.get("value", {})
                profile["coordinates"] = (coords.get("latitude"), coords.get("longitude"))

    return profile


def sample_entities_for_class(class_qid: str, class_label: str, limit: int = 10) -> list[dict]:
    """Sample N entities that are instance_of the given class, returning QID + label."""
    sparql = f"""
    SELECT ?item ?itemLabel WHERE {{
      ?item wdt:P31 wd:{class_qid} .
      ?item wdt:P625 ?coords .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    """
    print(f"  Sampling {limit} entities from {class_qid} ({class_label})...")
    data = query_wikidata(sparql)
    if not data:
        return []

    results = []
    for b in data.get("results", {}).get("bindings", []):
        item = b.get("item", {}).get("value", "")
        qid = item.split("/")[-1] if "/" in item else item
        label = b.get("itemLabel", {}).get("value", qid)
        if label.startswith("Q") and label == qid:
            continue  # Skip items without English labels
        results.append({"qid": qid, "label": label, "source_class": class_qid, "source_class_label": class_label})

    return results


def sample_entities_no_coords(class_qid: str, class_label: str, limit: int = 5) -> list[dict]:
    """Sample entities WITHOUT P625 — to see what properties they DO have."""
    sparql = f"""
    SELECT ?item ?itemLabel WHERE {{
      ?item wdt:P31 wd:{class_qid} .
      FILTER NOT EXISTS {{ ?item wdt:P625 ?c }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    """
    data = query_wikidata(sparql)
    if not data:
        return []

    results = []
    for b in data.get("results", {}).get("bindings", []):
        item = b.get("item", {}).get("value", "")
        qid = item.split("/")[-1] if "/" in item else item
        label = b.get("itemLabel", {}).get("value", qid)
        if label.startswith("Q") and label == qid:
            continue
        results.append({"qid": qid, "label": label, "source_class": class_qid, "source_class_label": class_label})

    return results


def fetch_class_hierarchy(class_qids: list[str], depth: int = 2) -> list[dict]:
    """Fetch P279 (subclass_of) hierarchy for a set of root classes, up to N levels."""
    visited = set()
    hierarchy = []
    frontier = [(q, 0) for q in class_qids]

    while frontier:
        qid, level = frontier.pop(0)
        if qid in visited or level > depth:
            continue
        visited.add(qid)

        sparql = f"""
        SELECT ?parent ?parentLabel ?child ?childLabel WHERE {{
          {{
            wd:{qid} wdt:P279 ?parent .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
          }}
          UNION
          {{
            ?child wdt:P279 wd:{qid} .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
          }}
        }}
        """
        data = query_wikidata(sparql)
        if not data:
            continue

        for b in data.get("results", {}).get("bindings", []):
            parent_uri = b.get("parent", {}).get("value", "")
            parent_qid = parent_uri.split("/")[-1] if parent_uri else ""
            parent_label = b.get("parentLabel", {}).get("value", "")
            child_uri = b.get("child", {}).get("value", "")
            child_qid = child_uri.split("/")[-1] if child_uri else ""
            child_label = b.get("childLabel", {}).get("value", "")

            if parent_qid:
                hierarchy.append({
                    "child_qid": qid, "child_label": "",
                    "parent_qid": parent_qid, "parent_label": parent_label,
                    "level": level, "direction": "up",
                })
                if parent_qid not in visited and level + 1 <= depth:
                    frontier.append((parent_qid, level + 1))

            if child_qid:
                hierarchy.append({
                    "child_qid": child_qid, "child_label": child_label,
                    "parent_qid": qid, "parent_label": "",
                    "level": level, "direction": "down",
                })

        time.sleep(1.0)

    # Resolve labels
    all_qids = set()
    for h in hierarchy:
        all_qids.add(h["child_qid"])
        all_qids.add(h["parent_qid"])
    labels = fetch_labels_via_api(list(all_qids))
    for h in hierarchy:
        if not h["child_label"]:
            h["child_label"] = labels.get(h["child_qid"], h["child_qid"])
        if not h["parent_label"]:
            h["parent_label"] = labels.get(h["parent_qid"], h["parent_qid"])

    return hierarchy


def main():
    parser = argparse.ArgumentParser(description="Survey Wikidata geographic properties")
    parser.add_argument("--samples", type=int, default=10, help="Entities to sample per class (default 10)")
    parser.add_argument("--dry-run", action="store_true", help="Show plan, don't query")
    parser.add_argument("--classes", type=int, default=None, help="Limit number of classes to survey")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    classes = GEO_ROOT_CLASSES[:args.classes] if args.classes else GEO_ROOT_CLASSES
    print(f"Geographic Property Survey")
    print(f"  {len(classes)} root classes, {args.samples} samples each")
    print(f"  Max entities to profile: {len(classes) * (args.samples + 5)}")
    print()

    if args.dry_run:
        print("DRY RUN — classes to survey:")
        for qid, label, desc in classes:
            print(f"  {qid:12s} {label:30s} {desc}")
        return

    # ── Phase 1: Sample entities from each class ────────────────────────────
    print("═" * 60)
    print("PHASE 1: Sampling entities from root classes")
    print("═" * 60)

    all_samples = []
    for qid, label, desc in classes:
        # Sample with coords (primary) + without coords (secondary)
        with_coords = sample_entities_for_class(qid, label, args.samples)
        without_coords = sample_entities_no_coords(qid, label, max(2, args.samples // 4))
        total = with_coords + without_coords
        print(f"    → {len(with_coords)} with coords + {len(without_coords)} without = {len(total)}")
        all_samples.extend(total)
        time.sleep(1.5)

    # Deduplicate by QID
    seen = set()
    unique_samples = []
    for s in all_samples:
        if s["qid"] not in seen:
            seen.add(s["qid"])
            unique_samples.append(s)

    print(f"\n  Total unique entities to profile: {len(unique_samples)}")

    # ── Phase 2: Profile each entity (all properties + external IDs) ────────
    print()
    print("═" * 60)
    print("PHASE 2: Profiling entity properties")
    print("═" * 60)

    property_counter = Counter()      # PID → count of entities that have it
    ext_id_counter = Counter()        # PID → count (external IDs only)
    instance_of_counter = Counter()   # QID → count
    all_profiles = []
    all_ext_ids = []

    for i, sample in enumerate(unique_samples):
        qid = sample["qid"]
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  [{i + 1}/{len(unique_samples)}] {qid} ({sample['label']})...")

        entity = fetch_entity_claims(qid)
        if not entity:
            continue

        profile = extract_property_profile(entity)
        profile["qid"] = qid
        profile["source_class"] = sample["source_class"]
        profile["source_class_label"] = sample["source_class_label"]

        # Count properties
        for pid in profile["property_pids"]:
            property_counter[pid] += 1

        # Count external IDs
        seen_pids = set()
        for pid, val in profile["external_ids"]:
            if pid not in seen_pids:
                ext_id_counter[pid] += 1
                seen_pids.add(pid)
            all_ext_ids.append({
                "entity_qid": qid,
                "entity_label": profile["label"],
                "source_class": sample["source_class_label"],
                "ext_id_pid": pid,
                "ext_id_value": val,
            })

        # Count instance_of
        for ioq in profile["instance_of"]:
            instance_of_counter[ioq] += 1

        all_profiles.append(profile)
        time.sleep(0.4)

    print(f"\n  Profiled {len(all_profiles)} entities")
    print(f"  Discovered {len(property_counter)} distinct properties")
    print(f"  Discovered {len(ext_id_counter)} distinct external ID types")
    print(f"  Discovered {len(instance_of_counter)} distinct instance_of classes")

    # ── Phase 3: Resolve property labels ─────────────────────────────────────
    print()
    print("═" * 60)
    print("PHASE 3: Resolving labels")
    print("═" * 60)

    # Fetch property labels
    all_pids = list(set(list(property_counter.keys()) + list(ext_id_counter.keys())))
    print(f"  Fetching labels for {len(all_pids)} properties...")
    pid_labels = fetch_labels_via_api(all_pids)

    # Fetch instance_of class labels
    io_qids = list(instance_of_counter.keys())
    print(f"  Fetching labels for {len(io_qids)} instance_of classes...")
    io_labels = fetch_labels_via_api(io_qids)

    # Also fetch subclass_of and part_of labels
    all_sc_qids = set()
    all_po_qids = set()
    for p in all_profiles:
        for q in p["subclass_of"]:
            all_sc_qids.add(q)
        for q in p["part_of"]:
            all_po_qids.add(q)
    all_ref_qids = list(all_sc_qids | all_po_qids - set(io_labels.keys()))
    if all_ref_qids:
        print(f"  Fetching labels for {len(all_ref_qids)} subclass/part_of refs...")
        ref_labels = fetch_labels_via_api(all_ref_qids)
        io_labels.update(ref_labels)

    # ── Phase 4: Class hierarchy ─────────────────────────────────────────────
    print()
    print("═" * 60)
    print("PHASE 4: Fetching class hierarchy (2 levels up/down)")
    print("═" * 60)

    # Use top 20 instance_of classes + our root classes
    top_io = [qid for qid, _ in instance_of_counter.most_common(20)]
    root_class_qids = [qid for qid, _, _ in classes]
    hierarchy_seeds = list(set(top_io + root_class_qids))
    print(f"  {len(hierarchy_seeds)} seed classes for hierarchy exploration...")
    hierarchy = fetch_class_hierarchy(hierarchy_seeds, depth=2)
    print(f"  Found {len(hierarchy)} hierarchy edges")

    # ── Phase 5: Write outputs ───────────────────────────────────────────────
    print()
    print("═" * 60)
    print("PHASE 5: Writing output files")
    print("═" * 60)

    # 1. Per-entity property inventory
    entity_csv = OUT_DIR / "geo_property_survey.csv"
    fields = ["qid", "label", "source_class", "source_class_label", "has_coords",
              "instance_of", "instance_of_labels", "subclass_of", "subclass_of_labels",
              "part_of", "part_of_labels", "property_count", "ext_id_count", "property_pids"]
    with open(entity_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for p in all_profiles:
            w.writerow({
                "qid": p["qid"],
                "label": p["label"],
                "source_class": p["source_class"],
                "source_class_label": p["source_class_label"],
                "has_coords": "yes" if p["coordinates"] else "no",
                "instance_of": "|".join(p["instance_of"]),
                "instance_of_labels": "|".join(io_labels.get(q, q) for q in p["instance_of"]),
                "subclass_of": "|".join(p["subclass_of"]),
                "subclass_of_labels": "|".join(io_labels.get(q, q) for q in p["subclass_of"]),
                "part_of": "|".join(p["part_of"]),
                "part_of_labels": "|".join(io_labels.get(q, q) for q in p["part_of"]),
                "property_count": len(p["property_pids"]),
                "ext_id_count": len(set(pid for pid, _ in p["external_ids"])),
                "property_pids": "|".join(sorted(p["property_pids"])),
            })
    print(f"  {entity_csv.name}: {len(all_profiles)} entities")

    # 2. Property frequency table
    freq_csv = OUT_DIR / "geo_property_frequencies.csv"
    with open(freq_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pid", "label", "count", "pct", "is_external_id"])
        w.writeheader()
        for pid, cnt in property_counter.most_common():
            w.writerow({
                "pid": pid,
                "label": pid_labels.get(pid, ""),
                "count": cnt,
                "pct": f"{cnt / len(all_profiles) * 100:.1f}",
                "is_external_id": "yes" if pid in ext_id_counter else "no",
            })
    print(f"  {freq_csv.name}: {len(property_counter)} properties")

    # 3. External ID frequency table
    ext_csv = OUT_DIR / "geo_external_ids.csv"
    with open(ext_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pid", "label", "entity_count", "pct", "sample_values"])
        w.writeheader()
        # Group sample values
        ext_samples = defaultdict(list)
        for e in all_ext_ids:
            if len(ext_samples[e["ext_id_pid"]]) < 3:
                ext_samples[e["ext_id_pid"]].append(e["ext_id_value"])
        for pid, cnt in ext_id_counter.most_common():
            w.writerow({
                "pid": pid,
                "label": pid_labels.get(pid, ""),
                "entity_count": cnt,
                "pct": f"{cnt / len(all_profiles) * 100:.1f}",
                "sample_values": " | ".join(ext_samples.get(pid, [])),
            })
    print(f"  {ext_csv.name}: {len(ext_id_counter)} external ID types")

    # 4. Class hierarchy
    hier_csv = OUT_DIR / "geo_class_hierarchy.csv"
    with open(hier_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["child_qid", "child_label", "parent_qid", "parent_label", "direction", "level"])
        w.writeheader()
        w.writerows(hierarchy)
    print(f"  {hier_csv.name}: {len(hierarchy)} edges")

    # 5. Instance_of distribution
    io_csv = OUT_DIR / "geo_instance_of_distribution.csv"
    with open(io_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "label", "count", "pct"])
        w.writeheader()
        for qid, cnt in instance_of_counter.most_common():
            w.writerow({
                "qid": qid,
                "label": io_labels.get(qid, qid),
                "count": cnt,
                "pct": f"{cnt / len(all_profiles) * 100:.1f}",
            })
    print(f"  {io_csv.name}: {len(instance_of_counter)} classes")

    # ── Phase 6: Analysis report ─────────────────────────────────────────────
    print()
    print("═" * 60)
    print("ANALYSIS REPORT")
    print("═" * 60)

    report_lines = []
    def rpt(line=""):
        print(line)
        report_lines.append(line)

    rpt(f"Geographic Property Survey — {len(all_profiles)} entities from {len(classes)} classes")
    rpt(f"Date: {time.strftime('%Y-%m-%d %H:%M')}")
    rpt()

    # Core geographic properties (high frequency)
    rpt("── CORE GEOGRAPHIC PROPERTIES (>30% of entities) ──")
    core_props = [(pid, cnt) for pid, cnt in property_counter.most_common() if cnt / len(all_profiles) >= 0.3]
    for pid, cnt in core_props:
        pct = cnt / len(all_profiles) * 100
        ext = " [EXT-ID]" if pid in ext_id_counter else ""
        rpt(f"  {pid:8s} {pid_labels.get(pid, '?'):45s} {cnt:4d} ({pct:5.1f}%){ext}")

    rpt()
    rpt("── GEOGRAPHIC EXTERNAL IDS (sorted by coverage) ──")
    for pid, cnt in ext_id_counter.most_common(40):
        pct = cnt / len(all_profiles) * 100
        samples = ext_samples.get(pid, [])[:2]
        rpt(f"  {pid:8s} {pid_labels.get(pid, '?'):45s} {cnt:4d} ({pct:5.1f}%)  e.g. {', '.join(samples)}")

    rpt()
    rpt("── TOP INSTANCE_OF CLASSES ──")
    for qid, cnt in instance_of_counter.most_common(30):
        pct = cnt / len(all_profiles) * 100
        rpt(f"  {qid:12s} {io_labels.get(qid, '?'):40s} {cnt:4d} ({pct:5.1f}%)")

    rpt()
    rpt("── PROPERTIES BY CATEGORY ──")
    # Categorize properties
    spatial = [p for p in core_props if p[0] in {"P625", "P1332", "P1333", "P1334", "P1335", "P2044",
               "P2046", "P2660", "P3896", "P242", "P8712"}]
    admin = [p for p in core_props if p[0] in {"P17", "P131", "P36", "P150", "P47", "P206",
             "P421", "P1376", "P571", "P576"}]
    hydro = [p for p in core_props if p[0] in {"P403", "P469", "P474", "P4614", "P885",
             "P200", "P201", "P205", "P4552"}]

    if spatial:
        rpt("  Spatial:")
        for pid, cnt in spatial:
            rpt(f"    {pid:8s} {pid_labels.get(pid, '?'):40s} {cnt}")
    if admin:
        rpt("  Administrative:")
        for pid, cnt in admin:
            rpt(f"    {pid:8s} {pid_labels.get(pid, '?'):40s} {cnt}")
    if hydro:
        rpt("  Hydrographic:")
        for pid, cnt in hydro:
            rpt(f"    {pid:8s} {pid_labels.get(pid, '?'):40s} {cnt}")

    rpt()
    rpt("── SFA ROUTING SIGNALS (external IDs that activate geo SFAs) ──")
    rpt("  High-value authority IDs for geographic SFA routing:")
    key_geo_ids = {
        "P1566": "GeoNames ID",
        "P1667": "Getty TGN ID",
        "P1584": "Pleiades ID",
        "P244":  "LCNAF/LCSH ID",
        "P227":  "GND ID",
        "P214":  "VIAF ID",
        "P268":  "BnF ID",
        "P269":  "IdRef ID",
        "P402":  "OpenStreetMap relation ID",
        "P882":  "FIPS code",
        "P590":  "GNIS ID",
        "P3120": "TOID (Ordnance Survey)",
    }
    for pid, desc in key_geo_ids.items():
        cnt = ext_id_counter.get(pid, 0)
        pct = cnt / len(all_profiles) * 100 if cnt else 0
        status = "PRESENT" if cnt > 0 else "ABSENT"
        rpt(f"  {pid:8s} {desc:40s} {status:8s} {cnt:4d} ({pct:5.1f}%)")

    rpt()
    rpt("── COORDS COVERAGE ──")
    with_coords = sum(1 for p in all_profiles if p["coordinates"])
    rpt(f"  {with_coords}/{len(all_profiles)} entities have P625 coordinates ({with_coords / len(all_profiles) * 100:.1f}%)")

    # Write report
    report_path = OUT_DIR / "geo_survey_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n  Report: {report_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
