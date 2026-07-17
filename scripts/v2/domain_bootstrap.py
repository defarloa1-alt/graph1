#!/usr/bin/env python3
"""Bootstrap Domain nodes and wire them to CurriculumTopics via ACTIVATES edges.

A Domain (e.g. Roman Republic) activates a subset of CurriculumTopics.
The intersection of Domain + CurriculumTopic = a candidate SubjectConcept.

Schema added here:
  (Domain)-[:ACTIVATES]->(CurriculumTopic)

Run:
  python scripts/bootstrap/domain_bootstrap.py
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

# ---------------------------------------------------------------------------
# Domain definitions
# Each domain has:
#   qid       - Wikidata QID
#   key       - stable local key
#   label     - display name
#   period    - rough date range (ISO-style, negative = BCE)
#   activates - list of CurriculumTopic keys this domain activates
# ---------------------------------------------------------------------------

DOMAINS = [
    {
        "qid": "Q17167",
        "key": "roman_republic",
        "label": "Roman Republic",
        "period_start": -509,
        "period_end": -27,
        "activates": [
            # Archaeological
            "arch_early_complex_societies",
            "arch_material_culture",
            "arch_landscape_environment",
            "arch_theory_interpretation",
            # Artistic
            "art_architecture",
            "art_patronage_context",
            "art_media_technique",
            "art_periods_movements",
            # Biographic
            "bio_career_office",
            "bio_prosopography",
            "bio_identity_selfhood",
            "bio_gender_age",
            "bio_life_writing_methods",
            # Communication
            "comm_rhetoric_persuasion",
            "comm_written_oral",
            "comm_interpersonal",
            # Cultural
            "cul_mentalites_worldview",
            "cul_intellectual_movements",
            "cul_popular_culture",
            "cul_cultural_exchange",
            # Demographic
            "dem_population_dynamics",
            "dem_family_household",
            "dem_migration_mobility",
            "dem_mortality_life",
            "dem_sources_methods",
            # Diplomatic
            "dip_foreign_policy",
            "dip_treaty_negotiation",
            "dip_diplomatic_institutions",
            "dip_primary_sources",
            # Economic
            "eco_trade_markets",
            "eco_finance_monetary",
            "eco_institutions_property",
            "eco_labor_living_standards",
            # Environmental
            "env_climate_history",
            "env_disease_ecology",
            "env_land_resources",
            "env_water_systems",
            # Geographic
            "geo_territory_empire",
            "geo_place_topography",
            "geo_routes_connectivity",
            "geo_landscape_change",
            "geo_historical_cartography",
            # Intellectual
            "int_ancient_philosophy",
            "int_political_social_thought",
            "int_history_of_ideas",
            # Linguistic
            "ling_writing_epigraphy",
            "ling_oral_literacy",
            "ling_multilingualism_contact",
            "ling_phonology_grammar",
            # Military
            "mil_ancient_warfare",
            "mil_grand_strategy",
            "mil_political_nexus",
            "mil_leadership_ethics",
            "mil_maritime_sea_power",
            # Political
            "pol_governance_institutions",
            "pol_state_formation",
            "pol_empire_sovereignty",
            "pol_political_thought",
            "pol_political_movements",
            # Religious
            "rel_ritual_practice",
            "rel_religion_politics",
            "rel_theology_belief",
            # Scientific
            "sci_ancient_medieval_science",
            "sci_society_culture",
            # Social
            "soc_class_inequality",
            "soc_gender_family",
            "soc_community_institutions",
            "soc_classical_theory",
            # Technological
            "tech_infrastructure_engineering",
            "tech_military_technology",
            "tech_innovation_diffusion",
        ],
    },
]


def run(driver):
    with driver.session() as s:
        total_activates = 0
        for d in DOMAINS:
            # Create/update Domain node
            s.run(
                """
                MERGE (dom:Domain {key: $key})
                SET dom.label       = $label,
                    dom.qid         = $qid,
                    dom.period_start = $period_start,
                    dom.period_end   = $period_end
                """,
                key=d["key"],
                label=d["label"],
                qid=d["qid"],
                period_start=d["period_start"],
                period_end=d["period_end"],
            )
            print(f"  Domain: {d['label']} ({d['qid']})")

            # Wire ACTIVATES edges
            missing = []
            for ct_key in d["activates"]:
                result = s.run(
                    """
                    MATCH (dom:Domain {key: $dom_key})
                    MATCH (ct:CurriculumTopic {key: $ct_key})
                    MERGE (dom)-[:ACTIVATES]->(ct)
                    RETURN ct.key AS k
                    """,
                    dom_key=d["key"],
                    ct_key=ct_key,
                )
                if not result.single():
                    missing.append(ct_key)

            wired = len(d["activates"]) - len(missing)
            total_activates += wired
            print(f"    ACTIVATES edges: {wired}/{len(d['activates'])}")
            if missing:
                print(f"    WARNING — missing CurriculumTopic keys: {missing}")

        # Summary
        r = s.run(
            """
            MATCH (dom:Domain)-[:ACTIVATES]->(ct:CurriculumTopic)<-[:HAS_TOPIC]-(f:Facet)
            RETURN dom.label AS domain, f.key AS facet, count(ct) AS topics
            ORDER BY dom.label, f.key
            """
        )
        print("\nActivation summary (domain × facet):")
        for row in r:
            print(f"  {row['domain']:20s}  {row['facet']:20s}  {row['topics']} topics")

        print(f"\nTotal ACTIVATES edges created: {total_activates}")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        print("Bootstrapping domains...")
        run(driver)
        print("Done.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
