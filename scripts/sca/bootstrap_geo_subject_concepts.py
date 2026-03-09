#!/usr/bin/env python3
"""
Bootstrap geographic SubjectConcepts from ClassificationAnchor types.

Creates SubjectConcept nodes for the 7 geographic anchor types discovered
during Place→ClassificationAnchor wiring:
  - HistoricalPlace (93 anchors — ancient cities, archaeological sites)
  - PhysicalFeature (54 — mountains, islands, peninsulas, continents)
  - Hydrography (26 — rivers, lakes, seas, waterfalls)
  - GeographicPlace (19 — general places)
  - AdministrativeDivision (4 — provinces, regions)
  - Settlement (3 — cities, towns, villages)
  - PoliticalEntity (2 — countries, empires)

Also:
  - Wires HAS_PRIMARY_FACET → Geographic Facet
  - Wires MEMBER_OF from Places → SubjectConcepts (by instance_of classification)
  - Registers SYS_SFAAgent for geographic facet
  - Enriches Geographic Facet node with description

Usage:
  python scripts/sca/bootstrap_geo_subject_concepts.py --dry-run
  python scripts/sca/bootstrap_geo_subject_concepts.py --write
"""

from __future__ import annotations

import argparse
import io
import os
import sys
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

from neo4j import GraphDatabase

# ── SubjectConcept definitions ────────────────────────────────────────────────
# Grounded in the 7 anchor types from ClassificationAnchor + real LCSH headings

GEO_SUBJECTS = [
    {
        "subject_id": "GEO_HIST_PLACES",
        "label": "Historical Places & Archaeological Sites",
        "scope_note": "Ancient cities, archaeological sites, ruined settlements, and other places "
                      "of primarily historical significance. Includes Pompeii, Troy, Carthage, etc.",
        "anchor_type": "HistoricalPlace",
        "lcsh_heading": "Historic sites",
        "lcsh_id": "sh85061212",
        "lcc_primary": "CC",
        "instance_of_patterns": [
            "archaeological site", "ancient city", "polis", "historical",
            "ruins", "ghost town", "ancient greek city",
        ],
    },
    {
        "subject_id": "GEO_PHYS_FEATURES",
        "label": "Physical Geography & Landforms",
        "scope_note": "Mountains, islands, peninsulas, continents, valleys, and other natural "
                      "landforms. Atemporal — no inception/dissolution dates expected.",
        "anchor_type": "PhysicalFeature",
        "lcsh_heading": "Landforms",
        "lcsh_id": "sh85074392",
        "lcc_primary": "GB",
        "instance_of_patterns": [
            "mountain", "volcano", "hill", "peak", "valley", "peninsula",
            "island", "continent", "cape", "plateau", "plain",
        ],
    },
    {
        "subject_id": "GEO_HYDROGRAPHY",
        "label": "Hydrography & Water Bodies",
        "scope_note": "Rivers, lakes, seas, oceans, waterfalls, straits, and other water features. "
                      "Atemporal — these are permanent geographic fixtures.",
        "anchor_type": "Hydrography",
        "lcsh_heading": "Bodies of water",
        "lcsh_id": "sh85015177",
        "lcc_primary": "GB",
        "instance_of_patterns": [
            "river", "lake", "sea", "ocean", "waterfall", "strait",
            "bay", "gulf", "lagoon", "reservoir", "canal",
        ],
    },
    {
        "subject_id": "GEO_SETTLEMENTS",
        "label": "Settlements & Urban Places",
        "scope_note": "Cities, towns, villages, and other inhabited places with modern continuity. "
                      "Distinct from HistoricalPlace which covers primarily ancient/ruined sites.",
        "anchor_type": "Settlement",
        "lcsh_heading": "Cities and towns",
        "lcsh_id": "sh85026282",
        "lcc_primary": "HT",
        "instance_of_patterns": [
            "city", "town", "village", "settlement", "metropolis",
            "big city", "megacity", "municipality", "commune",
        ],
    },
    {
        "subject_id": "GEO_ADMIN_DIVISIONS",
        "label": "Administrative & Political Divisions",
        "scope_note": "Provinces, regions, departments, prefectures, and other administrative "
                      "subdivisions of states. Includes both historical and modern divisions.",
        "anchor_type": "AdministrativeDivision",
        "lcsh_heading": "Administrative and political divisions",
        "lcsh_id": "sh99005245",
        "lcc_primary": "JS",
        "instance_of_patterns": [
            "admin", "province", "region", "department", "prefecture",
            "first-level", "second-level", "county", "district",
        ],
    },
    {
        "subject_id": "GEO_POLITICAL_ENTITIES",
        "label": "States, Empires & Political Entities",
        "scope_note": "Countries, sovereign states, empires, kingdoms, and other political entities "
                      "with territorial extent. Overlaps with Political facet.",
        "anchor_type": "PoliticalEntity",
        "lcsh_heading": "States, The",
        "lcsh_id": "sh85127474",
        "lcc_primary": "JC",
        "instance_of_patterns": [
            "country", "sovereign state", "empire", "kingdom",
            "historical country", "republic", "city-state",
        ],
    },
    {
        "subject_id": "GEO_GENERAL",
        "label": "General Geographic Places",
        "scope_note": "Geographic places that don't fit neatly into the above categories. "
                      "Includes mixed-type locations, infrastructure (bridges, roads, ports), "
                      "and unclassified places.",
        "anchor_type": "GeographicPlace",
        "lcsh_heading": "Geography",
        "lcsh_id": "sh85053986",
        "lcc_primary": "G",
        "instance_of_patterns": [
            "bridge", "road", "port", "hospital", "castle", "fortress",
            "temple", "church", "monastery", "aqueduct",
        ],
    },
]

# ── Cypher queries ────────────────────────────────────────────────────────────

MERGE_SUBJECT = """
MERGE (sc:SubjectConcept {subject_id: $subject_id})
SET sc.label           = $label,
    sc.scope_note      = $scope_note,
    sc.anchor_type     = $anchor_type,
    sc.lcsh_heading    = $lcsh_heading,
    sc.lcsh_id         = $lcsh_id,
    sc.lcc_primary     = $lcc_primary,
    sc.source          = 'geo_bootstrap',
    sc.seed_domain     = 'geographic',
    sc.updated         = datetime()
WITH sc
MATCH (f:Facet {label: 'Geographic'})
MERGE (sc)-[:HAS_PRIMARY_FACET]->(f)
RETURN sc.subject_id AS sid
"""

# Wire MEMBER_OF by matching instance_of patterns
# This uses CONTAINS on the instance_of string (which stores labels like "river|watercourse")
WIRE_MEMBER_OF = """
MATCH (p:Place), (sc:SubjectConcept {subject_id: $subject_id})
WHERE p.instance_of IS NOT NULL
  AND any(pat IN $patterns WHERE toLower(p.instance_of) CONTAINS pat)
MERGE (p)-[r:MEMBER_OF]->(sc)
SET r.source = 'geo_bootstrap_instance_of',
    r.updated = datetime()
RETURN count(r) AS wired
"""

# Catch unclassified Places (have instance_of but didn't match any pattern)
WIRE_UNCLASSIFIED = """
MATCH (p:Place)
WHERE p.instance_of IS NOT NULL
  AND NOT (p)-[:MEMBER_OF]->(:SubjectConcept)
WITH p
MATCH (sc:SubjectConcept {subject_id: 'GEO_GENERAL'})
MERGE (p)-[r:MEMBER_OF]->(sc)
SET r.source = 'geo_bootstrap_fallback',
    r.updated = datetime()
RETURN count(r) AS wired
"""

# Wire ClassificationAnchors to their SubjectConcepts
WIRE_ANCHOR_TO_SC = """
MATCH (ca:ClassificationAnchor {source_type: 'geographic_lcsh'}),
      (sc:SubjectConcept {anchor_type: ca.anchor_type})
WHERE sc.seed_domain = 'geographic'
MERGE (ca)-[r:ANCHORS]->(sc)
SET r.source = 'geo_bootstrap',
    r.updated = datetime()
RETURN count(r) AS wired
"""

# Register geographic SFA agent
REGISTER_SFA = """
MERGE (a:SYS_SFAAgent {agent_id: 'sfa_geographic'})
SET a.label       = 'Geographic SFA',
    a.facet       = 'Geographic',
    a.status      = 'bootstrap',
    a.description = 'Subject Facet Agent for the Geographic facet. Manages Place entities, '
                  + 'spatial relationships, and geographic classification anchors. '
                  + 'Covers 7 SubjectConcepts: historical places, physical features, '
                  + 'hydrography, settlements, admin divisions, political entities, general.',
    a.entity_types = ['Place'],
    a.updated     = datetime()
WITH a
MATCH (f:Facet {label: 'Geographic'})
MERGE (a)-[:MANAGES_FACET]->(f)
RETURN a.agent_id AS aid
"""

# Enrich Facet node
ENRICH_FACET = """
MATCH (f:Facet {label: 'Geographic'})
SET f.description = 'Spatial and place-based dimension of knowledge. Covers physical geography '
                  + '(landforms, water bodies), political geography (states, admin divisions), '
                  + 'historical geography (ancient cities, archaeological sites), and settlement '
                  + 'patterns. 44,193 Place nodes, 201 ClassificationAnchors with LCSH headings.',
    f.entity_count = 44193,
    f.anchor_count = 201,
    f.subject_concept_count = 7,
    f.updated = datetime()
RETURN f.label AS label
"""

# D5 temporal bypass for atemporal geographic classes
WIRE_D5_BYPASS = """
MERGE (dt:SYS_DecisionTable {table_id: 'D5_SCOPE_temporal_overlap'})
SET dt.description = 'Temporal scope check for entity relevance. Compares entity temporal bounds '
                   + 'against study period. Includes bypass list for atemporal geographic features.',
    dt.updated = date('2026-03-08')
WITH dt
MERGE (dr:SYS_DecisionRow {row_id: 'D5_bypass_atemporal_geo'})
SET dr.conditions = 'instance_of IN [river, mountain, lake, sea, peninsula, valley, continent, waterfall, island, ocean, strait, cape]',
    dr.action = 'bypass',
    dr.action_detail = 'Skip temporal overlap check — atemporal physical feature',
    dr.dimension = 'temporal_bypass',
    dr.priority = 0,
    dr.note = 'Physical features have 0% temporal coverage in Wikidata survey (no P571/P576). '
            + 'QIDs: Q4022 (river), Q8502 (mountain), Q23397 (lake), Q165 (sea), Q34763 (peninsula), '
            + 'Q39816 (valley), Q5107 (continent), Q34038 (waterfall), Q23442 (island).'
WITH dt, dr
MERGE (dt)-[:HAS_ROW]->(dr)
RETURN dt.table_id AS tid
"""


def main():
    parser = argparse.ArgumentParser(description="Bootstrap geographic SubjectConcepts")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    print(f"Geographic SubjectConcept Bootstrap [{'WRITE' if write_mode else 'DRY RUN'}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    if not write_mode:
        print(f"\n  Would create {len(GEO_SUBJECTS)} SubjectConcept nodes:")
        for s in GEO_SUBJECTS:
            print(f"    {s['subject_id']:25s}  {s['label']}")
            print(f"      anchor_type={s['anchor_type']}, lcsh={s['lcsh_id']}, lcc={s['lcc_primary']}")
        print(f"\n  Would register SYS_SFAAgent 'sfa_geographic'")
        print(f"  Would enrich Geographic Facet node")
        print(f"  Would create D5 temporal bypass rule")
        print(f"  Would wire MEMBER_OF from Places (by instance_of pattern)")
        print(f"  Would wire ANCHORS from ClassificationAnchors to SubjectConcepts")

        # Preview MEMBER_OF counts
        print(f"\n  MEMBER_OF preview (instance_of pattern matching):")
        with driver.session() as session:
            for s in GEO_SUBJECTS:
                result = session.run("""
                    MATCH (p:Place)
                    WHERE p.instance_of IS NOT NULL
                      AND any(pat IN $patterns WHERE toLower(p.instance_of) CONTAINS pat)
                    RETURN count(p) AS cnt
                """, patterns=s["instance_of_patterns"])
                cnt = result.single()["cnt"]
                print(f"    {s['subject_id']:25s}  {cnt:>5} Places")

        driver.close()
        print(f"\n  Re-run with --write to execute.")
        return

    # Step 1: Create SubjectConcepts
    print("\nStep 1: Creating SubjectConcept nodes...")
    with driver.session() as session:
        for s in GEO_SUBJECTS:
            session.run(MERGE_SUBJECT, {
                "subject_id": s["subject_id"],
                "label": s["label"],
                "scope_note": s["scope_note"],
                "anchor_type": s["anchor_type"],
                "lcsh_heading": s["lcsh_heading"],
                "lcsh_id": s["lcsh_id"],
                "lcc_primary": s["lcc_primary"],
            })
            print(f"  {s['subject_id']:25s}  {s['label']}")
    print(f"  Created {len(GEO_SUBJECTS)} SubjectConcept nodes")

    # Step 2: Wire MEMBER_OF
    print("\nStep 2: Wiring Place -> SubjectConcept MEMBER_OF...")
    total_wired = 0
    with driver.session() as session:
        for s in GEO_SUBJECTS:
            if s["subject_id"] == "GEO_GENERAL":
                continue  # handle fallback separately
            result = session.run(WIRE_MEMBER_OF, {
                "subject_id": s["subject_id"],
                "patterns": s["instance_of_patterns"],
            })
            cnt = result.single()["wired"]
            total_wired += cnt
            print(f"  {s['subject_id']:25s}  {cnt:>5} Places")

        # Fallback for unclassified
        result = session.run(WIRE_UNCLASSIFIED)
        fallback = result.single()["wired"]
        total_wired += fallback
        print(f"  {'GEO_GENERAL (fallback)':25s}  {fallback:>5} Places")
    print(f"  Total MEMBER_OF: {total_wired}")

    # Step 3: Wire ClassificationAnchors to SubjectConcepts
    print("\nStep 3: Wiring ClassificationAnchor -> SubjectConcept ANCHORS...")
    with driver.session() as session:
        result = session.run(WIRE_ANCHOR_TO_SC)
        anchored = result.single()["wired"]
        print(f"  {anchored} ANCHORS relationships")

    # Step 4: Register SFA agent
    print("\nStep 4: Registering SYS_SFAAgent...")
    with driver.session() as session:
        session.run(REGISTER_SFA)
        print("  sfa_geographic registered")

    # Step 5: Enrich Facet
    print("\nStep 5: Enriching Geographic Facet node...")
    with driver.session() as session:
        session.run(ENRICH_FACET)
        print("  Geographic Facet enriched")

    # Step 6: D5 temporal bypass
    print("\nStep 6: Creating D5 temporal bypass rule...")
    with driver.session() as session:
        session.run(WIRE_D5_BYPASS)
        print("  D5_bypass_atemporal_geo created")

    # Verify
    print(f"\n{'=' * 60}")
    print("Verification:")
    with driver.session() as session:
        result = session.run("""
            MATCH (sc:SubjectConcept {seed_domain: 'geographic'})
            OPTIONAL MATCH (sc)<-[m:MEMBER_OF]-(p:Place)
            OPTIONAL MATCH (sc)<-[a:ANCHORS]-(ca:ClassificationAnchor)
            RETURN sc.subject_id AS sid, sc.label AS label,
                   count(DISTINCT p) AS members, count(DISTINCT ca) AS anchors
            ORDER BY members DESC
        """)
        for r in result:
            print(f"  {r['sid']:25s}  {r['members']:>5} members  {r['anchors']:>3} anchors  {r['label']}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
