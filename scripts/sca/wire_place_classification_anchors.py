#!/usr/bin/env python3
"""
Wire Place nodes with LCSH subject heading IDs as ClassificationAnchor nodes.

Scans Place nodes whose loc_authority_id starts with 'sh' (= LCSH subject headings,
not 'n' = NAF named entities). For each, creates a ClassificationAnchor node and
wires POSITIONED_AS from the Place and PROVIDES_ANCHOR from the Wikidata federation
source.

This bridges the geographic backbone to the bibliographic classification system
that SubjectConcepts are built on.

Usage:
  python scripts/sca/wire_place_classification_anchors.py --dry-run
  python scripts/sca/wire_place_classification_anchors.py --write
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
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

import requests
from neo4j import GraphDatabase

# ── Constants ─────────────────────────────────────────────────────────────────

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "ChrystallumBot/1.0 (geographic classification anchors)"

# Classification properties to harvest from each Place's Wikidata entity
CLASSIFICATION_PIDS = {
    "P1036": "dewey",     # Dewey Decimal Classification
    "P1149": "lcc",       # Library of Congress Classification
    "P244":  "lcsh_id",   # Library of Congress authority ID
    "P2163": "fast_id",   # FAST subject heading ID
    "P227":  "gnd_id",    # GND ID
}


# ── Wikidata API helpers ──────────────────────────────────────────────────────

def fetch_classification_props(qids: list[str]) -> dict[str, dict]:
    """Fetch classification properties for a batch of QIDs via Wikidata API.

    Returns {qid: {dewey, lcc, lcsh_id, fast_id, gnd_id, label}} for each QID.
    """
    results = {}
    for i in range(0, len(qids), 50):
        batch = qids[i:i + 50]
        ids = "|".join(batch)
        try:
            r = requests.get(
                WIKIDATA_API,
                params={
                    "action": "wbgetentities",
                    "ids": ids,
                    "props": "claims|labels",
                    "languages": "en",
                    "format": "json",
                },
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            if r.status_code != 200:
                print(f"  HTTP {r.status_code} fetching batch {i // 50 + 1}")
                continue
            data = r.json()
            for qid in batch:
                ent = data.get("entities", {}).get(qid, {})
                claims = ent.get("claims", {})
                labels = ent.get("labels", {})

                props = {}
                for pid, prop_name in CLASSIFICATION_PIDS.items():
                    if pid in claims:
                        claim_list = claims[pid]
                        if claim_list:
                            mainsnak = claim_list[0].get("mainsnak", {})
                            dv = mainsnak.get("datavalue", {})
                            val = dv.get("value", "")
                            if isinstance(val, dict):
                                val = val.get("id", str(val))
                            props[prop_name] = str(val) if val else None
                    else:
                        props[prop_name] = None

                label = ""
                if "en" in labels:
                    label = labels["en"].get("value", "")
                props["label"] = label
                results[qid] = props
        except Exception as e:
            print(f"  Error fetching batch {i // 50 + 1}: {e}")
        time.sleep(0.4)
    return results


# ── Neo4j queries ─────────────────────────────────────────────────────────────

FIND_LCSH_PLACES = """
MATCH (p:Place)
WHERE p.loc_authority_id STARTS WITH 'sh'
  AND p.qid IS NOT NULL
RETURN p.qid AS qid,
       p.label AS label,
       p.loc_authority_id AS lcsh_id,
       p.fast_id AS fast_id,
       p.gnd_id AS gnd_id,
       p.instance_of AS instance_of
ORDER BY p.label
"""

MERGE_ANCHOR = """
MERGE (a:ClassificationAnchor {qid: $qid})
SET a.label        = $label,
    a.anchor_type  = $anchor_type,
    a.federation   = 'wikidata',
    a.source_type  = 'geographic_lcsh',
    a.dewey        = CASE WHEN $dewey   IS NOT NULL THEN $dewey   ELSE a.dewey   END,
    a.lcc          = CASE WHEN $lcc     IS NOT NULL THEN $lcc     ELSE a.lcc     END,
    a.lcsh_id      = CASE WHEN $lcsh_id IS NOT NULL THEN $lcsh_id ELSE a.lcsh_id END,
    a.fast_id      = CASE WHEN $fast_id IS NOT NULL THEN $fast_id ELSE a.fast_id END,
    a.gnd_id       = CASE WHEN $gnd_id  IS NOT NULL THEN $gnd_id  ELSE a.gnd_id  END,
    a.last_updated = $updated_at
RETURN a.qid AS qid
"""

WIRE_POSITIONED_AS = """
MATCH (p:Place {qid: $place_qid})
MATCH (a:ClassificationAnchor {qid: $place_qid})
MERGE (p)-[r:POSITIONED_AS {
    federation: 'wikidata',
    property:   'P244',
    hops:       0
}]->(a)
SET r.rel_type      = 'SELF_ANCHOR',
    r.anchor_type   = $anchor_type,
    r.confidence    = 1.0,
    r.policy_ref    = 'FederationPositioningHopsSemantics',
    r.positioned_at = $positioned_at
RETURN r.federation AS federation
"""

WIRE_PROVIDES_ANCHOR = """
MATCH (fed:SYS_FederationSource {source_id: 'wikidata'})
MATCH (a:ClassificationAnchor {qid: $qid})
MERGE (fed)-[r:PROVIDES_ANCHOR]->(a)
SET r.confirmed_at = $confirmed_at
RETURN fed.source_id AS fed, a.qid AS anchor
"""


# ── Main pipeline ─────────────────────────────────────────────────────────────

def classify_anchor_type(instance_of: str | None) -> str:
    """Determine anchor_type from instance_of labels."""
    if not instance_of:
        return "GeographicPlace"
    iof = instance_of.lower()
    if any(k in iof for k in ["river", "lake", "sea", "ocean", "waterfall", "strait"]):
        return "Hydrography"
    if any(k in iof for k in ["mountain", "volcano", "hill", "peak", "valley", "peninsula", "island", "continent"]):
        return "PhysicalFeature"
    if any(k in iof for k in ["archaeological site", "ancient city", "polis", "historical"]):
        return "HistoricalPlace"
    if any(k in iof for k in ["country", "sovereign state", "empire", "kingdom"]):
        return "PoliticalEntity"
    if any(k in iof for k in ["city", "town", "village", "settlement", "metropolis"]):
        return "Settlement"
    if any(k in iof for k in ["admin", "province", "region", "department", "prefecture"]):
        return "AdministrativeDivision"
    return "GeographicPlace"


def main():
    parser = argparse.ArgumentParser(description="Wire Place LCSH IDs as ClassificationAnchors")
    parser.add_argument("--write", action="store_true", help="Actually write to Neo4j (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without writing")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    mode_label = "WRITE" if write_mode else "DRY RUN"
    print(f"Place -> ClassificationAnchor wiring [{mode_label}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Step 1: Find all Place nodes with LCSH IDs
    print("\nStep 1: Finding Place nodes with LCSH subject heading IDs...")
    with driver.session() as session:
        result = session.run(FIND_LCSH_PLACES)
        places = [dict(r) for r in result]
    print(f"  Found {len(places)} Place nodes with sh-prefix loc_authority_id")

    if not places:
        print("  Nothing to do.")
        driver.close()
        return

    # Step 2: Fetch classification properties from Wikidata
    qids = [p["qid"] for p in places]
    print(f"\nStep 2: Fetching classification properties from Wikidata ({len(qids)} QIDs)...")
    wiki_props = fetch_classification_props(qids)
    print(f"  Retrieved properties for {len(wiki_props)} entities")

    # Enrich places with Wikidata data
    enriched = 0
    for p in places:
        qid = p["qid"]
        wp = wiki_props.get(qid, {})
        # Use Wikidata values, fall back to what's already on the Place node
        p["dewey"] = wp.get("dewey")
        p["lcc"] = wp.get("lcc")
        # Prefer the lcsh_id already on the node (it's confirmed sh-prefix)
        p["wiki_lcsh_id"] = wp.get("lcsh_id")
        p["wiki_fast_id"] = wp.get("fast_id") or p.get("fast_id")
        p["wiki_gnd_id"] = wp.get("gnd_id") or p.get("gnd_id")
        p["wiki_label"] = wp.get("label") or p.get("label") or qid
        p["anchor_type"] = classify_anchor_type(p.get("instance_of"))
        if wp:
            enriched += 1

    # Stats
    has_lcc = sum(1 for p in places if p.get("lcc"))
    has_dewey = sum(1 for p in places if p.get("dewey"))
    has_fast = sum(1 for p in places if p.get("wiki_fast_id"))
    has_gnd = sum(1 for p in places if p.get("wiki_gnd_id"))
    print(f"\n  Classification coverage:")
    print(f"    LCSH (sh-prefix):  {len(places):>4} (100% — selection criterion)")
    print(f"    FAST ID:           {has_fast:>4} ({100*has_fast/len(places):.0f}%)")
    print(f"    GND ID:            {has_gnd:>4} ({100*has_gnd/len(places):.0f}%)")
    print(f"    LCC notation:      {has_lcc:>4} ({100*has_lcc/len(places):.0f}%)")
    print(f"    Dewey notation:    {has_dewey:>4} ({100*has_dewey/len(places):.0f}%)")

    # Anchor type distribution
    from collections import Counter
    type_counts = Counter(p["anchor_type"] for p in places)
    print(f"\n  Anchor type distribution:")
    for at, cnt in type_counts.most_common():
        print(f"    {at:25s}  {cnt:>4}")

    # Step 3: Write ClassificationAnchor nodes + relationships
    now = datetime.now(timezone.utc).isoformat()
    print(f"\nStep 3: {'Writing' if write_mode else 'Would write'} ClassificationAnchor nodes...")

    if not write_mode:
        print(f"\n  [DRY RUN] Would create {len(places)} ClassificationAnchor nodes")
        print(f"  [DRY RUN] Would wire {len(places)} POSITIONED_AS relationships")
        print(f"  [DRY RUN] Would wire {len(places)} PROVIDES_ANCHOR relationships")
        print(f"\n  Sample (first 10):")
        for p in places[:10]:
            print(f"    {p['qid']:12s}  {p.get('wiki_label',''):30s}  lcsh={p['lcsh_id']:15s}  "
                  f"fast={p.get('wiki_fast_id') or '-':>10s}  type={p['anchor_type']}")
        driver.close()
        print(f"\nRe-run with --write to execute.")
        return

    anchors_created = 0
    positioned = 0
    provides = 0
    errors = []

    with driver.session() as session:
        for i, p in enumerate(places):
            qid = p["qid"]
            try:
                # Create/merge ClassificationAnchor
                session.run(MERGE_ANCHOR, {
                    "qid": qid,
                    "label": p.get("wiki_label") or p.get("label") or qid,
                    "anchor_type": p["anchor_type"],
                    "dewey": p.get("dewey"),
                    "lcc": p.get("lcc"),
                    "lcsh_id": p["lcsh_id"],  # the sh-prefix ID from the Place node
                    "fast_id": p.get("wiki_fast_id"),
                    "gnd_id": p.get("wiki_gnd_id"),
                    "updated_at": now,
                })
                anchors_created += 1

                # Wire POSITIONED_AS (Place -> ClassificationAnchor)
                session.run(WIRE_POSITIONED_AS, {
                    "place_qid": qid,
                    "anchor_type": p["anchor_type"],
                    "positioned_at": now,
                })
                positioned += 1

                # Wire PROVIDES_ANCHOR (Wikidata -> ClassificationAnchor)
                session.run(WIRE_PROVIDES_ANCHOR, {
                    "qid": qid,
                    "confirmed_at": now,
                })
                provides += 1

            except Exception as e:
                errors.append(f"{qid}: {e}")
                print(f"  ERROR {qid}: {e}")

            if (i + 1) % 50 == 0:
                print(f"  [{i + 1}/{len(places)}] anchors={anchors_created} positioned={positioned} provides={provides}")

    print(f"\n{'=' * 60}")
    print(f"Results:")
    print(f"  ClassificationAnchor nodes created/merged: {anchors_created}")
    print(f"  POSITIONED_AS relationships:               {positioned}")
    print(f"  PROVIDES_ANCHOR relationships:             {provides}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors[:5]:
            print(f"    {e}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
