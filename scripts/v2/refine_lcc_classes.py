#!/usr/bin/env python3
"""Refine LCC classes on CurriculumTopics using LOC authority 053 ranges.

Updates lcc_class with more specific ranges from LOC linked data.
Stores the original value in lcc_class_original for audit trail.

Run:
  python scripts/v2/refine_lcc_classes.py
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

# Refinements harvested from LOC authority records (053 field)
# key -> (new_lcc_class, source_note)
REFINEMENTS = {
    # Direct refinements (same top-level, more specific)
    "rel_theology_belief":          ("BR-BX",           "LOC 053: full Theology range"),
    "cul_mentalites_worldview":     ("CB19",            "LOC 053: Civilization--Philosophy"),
    "arch_excavation_methods":      ("CC76",            "LOC 053: CC76-CC76.4"),
    "bio_life_writing_methods":     ("CT21",            "LOC 053: CT21-CT22"),
    "geo_historical_cartography":   ("GA101",           "LOC 053: GA101-GA1776"),
    "env_human_earth_systems":      ("GF1",             "LOC 053: GF1-GF900"),
    "arch_material_culture":        ("GN406",           "LOC 053: GN406-GN442"),
    "dem_population_dynamics":      ("HB848",           "LOC 053: HB848-HB3697"),
    "env_land_resources":           ("HD101",           "LOC 053: HD101-HD1131"),
    "geo_routes_connectivity":      ("HE331",           "LOC 053: HE331-HE368.7"),
    "soc_gender_family":            ("HQ1075",          "LOC 053: HQ1075-HQ1075.5"),
    "soc_class_inequality":         ("HT601",           "LOC 053: HT601-HT1455"),
    "dem_migration_mobility":       ("JV6001",          "LOC 053: JV6001-JV9480"),
    "dip_treaty_negotiation":       ("KZ1298",          "LOC 053: KZ1298-KZ1304"),
    "art_periods_movements":        ("N5300",           "LOC 053: N5300-N7415"),
    "env_water_systems":            ("TD201",           "LOC 053: TD201-TD500"),

    # Cross-classification corrections (LOC disagrees with our top-level)
    "geo_place_topography":         ("G82",             "LOC 053: G82-G88 (was DE)"),
    "tech_industrial_revolution":   ("HD2329",          "LOC 053: HD2329 (was HC)"),
    "pol_governance_institutions":  ("JA76",            "LOC 053: JA76 (was JF)"),
    "tech_science_technology":      ("CB478",           "LOC 053: CB478 (was T)"),
}


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as s:
        updated = 0
        for key, (new_lcc, note) in REFINEMENTS.items():
            result = s.run("""
                MATCH (ct:CurriculumTopic {key: $key})
                SET ct.lcc_class_original = ct.lcc_class,
                    ct.lcc_class = $new_lcc,
                    ct.lcc_source = 'loc_053'
                RETURN ct.key AS k, ct.lcc_class_original AS old, ct.lcc_class AS new
            """, key=key, new_lcc=new_lcc)
            row = result.single()
            if row:
                updated += 1
                print(f"  {row['k']:40s} {row['old']:8s} -> {row['new']:10s}  ({note})")
            else:
                print(f"  WARNING: {key} not found")

        print(f"\nRefined {updated}/{len(REFINEMENTS)} LCC classes.")

        # Summary
        r = s.run("""
            MATCH (ct:CurriculumTopic)
            WHERE ct.lcc_class_original IS NOT NULL
            RETURN count(ct) AS refined,
                   collect(ct.key) AS keys
        """)
        row = r.single()
        print(f"Topics with refined LCC: {row['refined']}")

    driver.close()


if __name__ == "__main__":
    main()
