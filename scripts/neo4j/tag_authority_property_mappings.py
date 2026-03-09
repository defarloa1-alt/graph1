#!/usr/bin/env python3
"""
Tag SYS_PropertyMapping nodes that represent bibliographic authority identifiers.

Sets:
  authority_control: true
  biblio_class: 'library' | 'crosswalk' | 'domain'

Library = cataloging systems (LoC, BnF, FAST, NLI)
Crosswalk = universal ID aggregators (VIAF, GND, ISNI)
Domain = field-specific vocabularies (Nomisma, PACTOLS, EAGLE, Getty TGN, Pleiades)

Usage:
  python scripts/neo4j/tag_authority_property_mappings.py --dry-run
  python scripts/neo4j/tag_authority_property_mappings.py --write
"""

from __future__ import annotations

import argparse
import io
import os
import sys
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

from neo4j import GraphDatabase

# ── Authority identifier P-codes ──────────────────────────────────────────────
# Maps Wikidata P-code → classification.
# entity_prop = the property name on our Person/Place nodes (for Script 2 linkage).

AUTHORITY_PIDS = [
    # LIBRARY — cataloging systems
    {"pid": "P244",  "biblio_class": "library",   "entity_prop": "loc_authority_id",
     "note": "Library of Congress authority ID"},
    {"pid": "P268",  "biblio_class": "library",   "entity_prop": "bnf_id",
     "note": "Bibliothèque nationale de France ID"},
    {"pid": "P2163", "biblio_class": "library",   "entity_prop": "fast_id",
     "note": "FAST ID (Faceted Application of Subject Terminology)"},
    {"pid": "P949",  "biblio_class": "library",   "entity_prop": "nli_id",
     "note": "National Library of Israel ID"},

    # CROSSWALK — universal ID aggregators
    {"pid": "P214",  "biblio_class": "crosswalk", "entity_prop": "viaf_id",
     "note": "VIAF cluster ID"},
    {"pid": "P227",  "biblio_class": "crosswalk", "entity_prop": "gnd_id",
     "note": "GND ID (German National Library)"},
    {"pid": "P213",  "biblio_class": "crosswalk", "entity_prop": "isni",
     "note": "ISNI (International Standard Name Identifier)"},
    {"pid": "P269",  "biblio_class": "crosswalk", "entity_prop": "idref_id",
     "note": "IdRef (French academic authority)"},

    # DOMAIN — field-specific vocabularies
    {"pid": "P1566", "biblio_class": "domain",    "entity_prop": "geonames_id",
     "note": "GeoNames ID"},
    {"pid": "P1584", "biblio_class": "domain",    "entity_prop": "pleiades_id",
     "note": "Pleiades ID (ancient geography)"},
    {"pid": "P3342", "biblio_class": "domain",    "entity_prop": None,
     "note": "Nomisma ID (numismatics)"},
    {"pid": "P4155", "biblio_class": "domain",    "entity_prop": None,
     "note": "PACTOLS ID (archaeology thesaurus)"},
    {"pid": "P2581", "biblio_class": "domain",    "entity_prop": None,
     "note": "BabelNet ID"},
    {"pid": "P245",  "biblio_class": "domain",    "entity_prop": None,
     "note": "ULAN ID (Getty Union List of Artist Names)"},
    {"pid": "P1667", "biblio_class": "domain",    "entity_prop": None,
     "note": "Getty TGN ID (Thesaurus of Geographic Names)"},
]


def main():
    parser = argparse.ArgumentParser(description="Tag authority PropertyMappings")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    print(f"Tag Authority PropertyMappings [{'WRITE' if write_mode else 'DRY RUN'}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Step 1: Check which PIDs have PropertyMapping nodes
    pids = [a["pid"] for a in AUTHORITY_PIDS]
    print(f"\nStep 1: Checking {len(pids)} authority PIDs against SYS_PropertyMapping...")
    with driver.session() as session:
        result = session.run("""
            MATCH (pm:SYS_PropertyMapping)
            WHERE pm.property_id IN $pids
            RETURN pm.property_id AS pid, pm.label AS label,
                   pm.authority_control AS current_auth
            ORDER BY pm.property_id
        """, pids=pids)
        existing = {r["pid"]: dict(r) for r in result}

    found = []
    missing = []
    for a in AUTHORITY_PIDS:
        if a["pid"] in existing:
            found.append(a)
            e = existing[a["pid"]]
            already = " (already tagged)" if e["current_auth"] else ""
            print(f"  ✓ {a['pid']:7s}  {e['label']:45s}  {a['biblio_class']:10s}{already}")
        else:
            missing.append(a)
            print(f"  ✗ {a['pid']:7s}  {a['note']:45s}  {a['biblio_class']:10s}  (no PM node)")

    print(f"\n  Found: {len(found)}  |  Missing PM: {len(missing)}")

    # Step 2: Check current Facet links
    print(f"\nStep 2: Current Facet links for authority PIDs...")
    with driver.session() as session:
        result = session.run("""
            MATCH (pm:SYS_PropertyMapping)-[r:HAS_PRIMARY_FACET|HAS_SECONDARY_FACET]->(f:Facet)
            WHERE pm.property_id IN $pids
            RETURN pm.property_id AS pid, type(r) AS rel, f.key AS facet
            ORDER BY pm.property_id, rel
        """, pids=pids)
        for r in result:
            print(f"  {r['pid']:7s} -{r['rel']:25s}-> {r['facet']}")

    if not write_mode:
        print(f"\n  [DRY RUN] Re-run with --write to apply.")
        driver.close()
        return

    # Step 3: Tag authority_control + biblio_class + entity_prop on existing PMs
    print(f"\nStep 3: Tagging {len(found)} PropertyMappings...")
    tagged = 0
    with driver.session() as session:
        for a in found:
            params = {
                "pid": a["pid"],
                "biblio_class": a["biblio_class"],
            }
            # Build SET clause dynamically for entity_prop (may be None)
            if a["entity_prop"]:
                result = session.run("""
                    MATCH (pm:SYS_PropertyMapping {property_id: $pid})
                    SET pm.authority_control = true,
                        pm.biblio_class = $biblio_class,
                        pm.entity_prop = $entity_prop,
                        pm.updated = date('2026-03-08')
                    RETURN pm.property_id AS pid
                """, pid=a["pid"], biblio_class=a["biblio_class"],
                     entity_prop=a["entity_prop"])
            else:
                result = session.run("""
                    MATCH (pm:SYS_PropertyMapping {property_id: $pid})
                    SET pm.authority_control = true,
                        pm.biblio_class = $biblio_class,
                        pm.updated = date('2026-03-08')
                    RETURN pm.property_id AS pid
                """, pid=a["pid"], biblio_class=a["biblio_class"])
            if result.single():
                tagged += 1

    print(f"  Tagged {tagged} PropertyMappings")

    # Verify
    print(f"\n{'=' * 60}")
    print("Verification:")
    with driver.session() as session:
        result = session.run("""
            MATCH (pm:SYS_PropertyMapping)
            WHERE pm.authority_control = true
            RETURN pm.biblio_class AS cls, count(pm) AS cnt
            ORDER BY cls
        """)
        for r in result:
            print(f"  {r['cls']:12s}  {r['cnt']}")

        result = session.run("""
            MATCH (pm:SYS_PropertyMapping {authority_control: true})
            RETURN count(pm) AS total
        """)
        total = result.single()["total"]
        print(f"\n  Total authority PropertyMappings: {total}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
