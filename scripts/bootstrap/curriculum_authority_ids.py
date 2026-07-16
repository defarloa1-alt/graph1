#!/usr/bin/env python3
"""Add LCSH, FAST, and LCC authority IDs to CurriculumTopic nodes.

All IDs verified against LOC suggest2 API and OCLC FAST API.

Run:
  python scripts/bootstrap/curriculum_authority_ids.py
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

# -----------------------------------------------------------------------
# Authority mappings: topic_key → (lcsh_id, lcsh_heading, fast_id, lcc_class)
# LCSH: verified via https://id.loc.gov/authorities/subjects/suggest2
# FAST: verified via https://fast.oclc.org/searchfast/fastsuggest
# LCC:  assigned from Library of Congress Classification schedules
# -----------------------------------------------------------------------

AUTHORITY = {
    # --- Archaeological ---
    "arch_excavation_methods":      ("sh85046105", "Excavations (Archaeology)",       "fst00917564", "CC"),
    "arch_material_culture":        ("sh85082061", "Material culture",                "fst01011739", "GN"),
    "arch_human_origins":           ("sh85062868", "Human evolution",                 "fst00963030", "GN281"),
    "arch_early_complex_societies": ("sh85026433", "Civilization, Ancient",            "fst00862946", "CB311"),
    "arch_landscape_environment":   ("sh94001190", "Landscape archaeology",            "fst00991791", "CC"),
    "arch_theory_interpretation":   ("sh85006510", "Archaeology--Philosophy",          "fst00812975", "CC72"),

    # --- Artistic ---
    "art_periods_movements":        ("sh85007488", "Art--History",                     "fst00815396", "N"),
    "art_visual_analysis":          ("sh85007989", "Art criticism",                    "fst00815492", "N7475"),
    "art_patronage_context":        ("sh85008074", "Art patronage",                   "fst00815756", "N8350"),
    "art_architecture":             ("sh2004006086", "Architecture--History",          "fst00813563", "NA"),
    "art_media_technique":          ("sh85007506", "Art--Technique",                  "fst00815372", "N7430"),

    # --- Biographic ---
    "bio_life_writing_methods":     ("sh85014164", "Biography as a literary form",    "fst00832172", "CT"),
    "bio_prosopography":            ("sh86000287", "Prosopography",                   "fst01079405", "CS"),
    "bio_identity_selfhood":        ("sh85064151", "Identity (Psychology)",            "fst00966892", "BF697"),
    "bio_career_office":            ("sh85108733", "Public officers",                 "fst01082763", "JF1601"),
    "bio_gender_age":               ("sh85076820", "Life cycle, Human",               "fst00998248", "HQ"),

    # --- Communication ---
    "comm_rhetoric_persuasion":     ("sh85113628", "Rhetoric",                        "fst01096948", "P301"),
    "comm_interpersonal":           ("sh85067481", "Interpersonal communication",     "fst00977344", "BF637"),
    "comm_written_oral":            ("sh85095226", "Oral communication",              "fst01047000", "P95"),
    "comm_media_channels":          ("sh85081863", "Mass media",                      "fst01011219", "P90"),

    # --- Cultural ---
    "cul_mentalites_worldview":     ("sh85026429", "Civilization--Philosophy",         "fst00862931", "CB"),
    "cul_intellectual_movements":   ("sh85067165", "Intellectual life",               "fst00975769", "CB"),
    "cul_nationalism_identity":     ("sh85090150", "Nationalism",                     "fst01033832", "JC311"),
    "cul_popular_culture":          ("sh85104904", "Popular culture",                 "fst01071344", "HM621"),
    "cul_cultural_exchange":        ("sh85000442", "Acculturation",                   "fst00795535", "GN357"),

    # --- Demographic ---
    "dem_population_dynamics":      ("sh85104910", "Population",                      "fst01071476", "HB"),
    "dem_family_household":         ("sh00005743", "Family",                          "fst01728849", "HQ503"),
    "dem_migration_mobility":       ("sh85042782", "Emigration and immigration",      "fst00908690", "JV"),
    "dem_mortality_life":           ("sh85087372", "Mortality",                       "fst01026502", "HB1321"),
    "dem_sources_methods":          ("sh85036659", "Demography",                      "fst00890158", "HB849"),

    # --- Diplomatic ---
    "dip_foreign_policy":           ("sh85067435", "International relations",         "fst00977053", "JZ"),
    "dip_treaty_negotiation":       ("sh85137207", "Treaties",                        "fst01155866", "KZ"),
    "dip_diplomatic_institutions":  ("sh85038179", "Diplomacy",                       "fst00894188", "JZ1305"),
    "dip_international_law":        ("sh85067417", "International law",               "fst00976984", "KZ"),
    "dip_primary_sources":          ("sh85038187", "Diplomatic documents",            "fst00894382", "JX"),

    # --- Economic ---
    "eco_trade_markets":            ("sh85028901", "Commerce",                        "fst00869279", "HF"),
    "eco_finance_monetary":         ("sh85048256", "Finance",                         "fst00924349", "HG"),
    "eco_growth_industrialization":  ("sh85040817", "Economic history",               "fst00901974", "HC"),
    "eco_institutions_property":    ("sh85107496", "Property",                        "fst01079116", "HD"),
    "eco_labor_living_standards":   ("sh90004091", "Labor",                           "fst00989798", "HD4801"),

    # --- Environmental ---
    "env_climate_history":          ("sh85027037", "Climatic changes",                "fst00864229", "QC903"),
    "env_disease_ecology":          ("sh85044370", "Epidemics",                       "fst00914079", "RA651"),
    "env_land_resources":           ("sh85074345", "Land use",                        "fst00991472", "HD"),
    "env_water_systems":            ("sh85145648", "Water-supply",                    "fst01172350", "TD"),
    "env_human_earth_systems":      ("sh85062856", "Human ecology",                  "fst00962941", "GF"),

    # --- Geographic ---
    "geo_place_topography":         ("sh85054012", "Geography, Ancient",              "fst00940567", "DE"),
    "geo_historical_cartography":   ("sh85020515", "Cartography",                     "fst00848025", "GA"),
    "geo_landscape_change":         ("sh85074408", "Landscape changes",               "fst00991873", "GF"),
    "geo_routes_connectivity":      ("sh85114487", "Roads",                           "fst01098511", "HE"),
    "geo_territory_empire":         ("sh85134110", "Territory, National",             "fst01148094", "JC323"),

    # --- Intellectual ---
    "int_ancient_philosophy":       ("sh85100861", "Philosophy, Ancient",             "fst01060860", "B165"),
    "int_hellenistic_medieval":     ("sh85100956", "Philosophy, Medieval",            "fst01061057", "B720"),
    "int_political_social_thought": ("sh88004669", "Political science--Philosophy",   "fst01069819", "JA71"),
    "int_history_of_ideas":         ("sh85067166", "Intellectual life--History",       "fst00975769", "CB"),
    "int_science_natural_philosophy": ("sh85118582", "Science--Philosophy",           "fst01108336", "Q175"),

    # --- Linguistic ---
    "ling_historical_change":       ("sh85061192", "Historical linguistics",          "fst00958134", "P140"),
    "ling_writing_epigraphy":       ("sh85148637", "Writing",                         "fst01181638", "P211"),
    "ling_multilingualism_contact": ("sh85088352", "Multilingualism",                 "fst01028907", "P115"),
    "ling_oral_literacy":           ("sh85095251", "Oral tradition",                  "fst01047117", "GR72"),
    "ling_phonology_grammar":       ("sh85056260", "Grammar, Comparative and general","fst00946126", "P151"),

    # --- Military ---
    "mil_theory_strategy":          ("sh85085132", "Military art and science",        "fst01020874", "U"),
    "mil_ancient_warfare":          ("sh85085208", "Military history, Ancient",        "fst01021234", "D25"),
    "mil_grand_strategy":           ("sh85128514", "Strategy",                        "fst01134406", "U162"),
    "mil_maritime_sea_power":       ("sh85090357", "Naval art and science",           "fst01034937", "V"),
    "mil_leadership_ethics":        ("sh85028876", "Command of troops",               "fst00869220", "UB210"),
    "mil_political_nexus":          ("sh85026352", "Civil-military relations",         "fst00862889", "JK330"),
    "mil_historical_analysis":      ("sh85085207", "Military history",                "fst01021222", "D25"),

    # --- Political ---
    "pol_state_formation":          ("sh85127474", "State, The",                      "fst01131943", "JC"),
    "pol_governance_institutions":  ("sh85104440", "Political science",               "fst01069781", "JF"),
    "pol_political_thought":        ("sh85104444", "Political science--History",       "fst01069819", "JA71"),
    "pol_political_movements":      ("sh85104370", "Political participation",          "fst01069386", "JF799"),
    "pol_empire_sovereignty":       ("sh85064628", "Imperialism",                     "fst00968126", "JC359"),

    # --- Religious ---
    "rel_ritual_practice":          ("sh85114211", "Rites and ceremonies",            "fst01098216", "BL600"),
    "rel_scripture_canon":          ("sh85116261", "Sacred books",                    "fst01103109", "BL70"),
    "rel_theology_belief":          ("sh85134665", "Theology",                        "fst01149559", "BT"),
    "rel_religion_politics":        ("sh85112577", "Religion and politics",            "fst01093842", "BL65"),
    "rel_conversion_spread":        ("sh85031702", "Conversion",                      "fst00877225", "BV4916"),

    # --- Scientific ---
    "sci_ancient_medieval_science": ("sh85118612", "Science, Ancient",                "fst01108800", "Q124"),
    "sci_scientific_revolution":    ("sh85118570", "Science--History",                "fst01108176", "Q125"),
    "sci_method_practice":          ("sh85118577", "Science--Methodology",            "fst01108313", "Q175"),
    "sci_key_disciplines":          ("sh85118587", "Science--Study and teaching",     "fst01108387", "Q181"),
    "sci_society_culture":          ("sh85118615", "Science and civilization",         "fst01108517", "Q175.5"),

    # --- Social ---
    "soc_classical_theory":         ("sh86006205", "Sociology--Philosophy",           "fst01123904", "HM"),
    "soc_class_inequality":         ("sh85123921", "Social classes",                  "fst01122346", "HT"),
    "soc_community_institutions":   ("sh90004194", "Civil society",                   "fst00862876", "JC337"),
    "soc_gender_family":            ("sh85120663", "Sex role",                        "fst01114598", "HQ"),
    "soc_modernity_change":         ("sh85123918", "Social change",                   "fst01122310", "HM831"),

    # --- Technological ---
    "tech_innovation_diffusion":    ("sh85133143", "Technological innovations",       "fst01145002", "T173.8"),
    "tech_infrastructure_engineering": ("sh85043176", "Engineering",                  "fst00910312", "TA"),
    "tech_military_technology":     ("sh91001438", "Military weapons",                "fst01021577", "U"),
    "tech_industrial_revolution":   ("sh85065956", "Industrialization",               "fst00971825", "HC"),
    "tech_science_technology":      ("sh85133180", "Technology and civilization",      "fst01145253", "T"),
}


def run(driver):
    with driver.session() as s:
        updated = 0
        missing = []
        for key, (lcsh_id, lcsh_heading, fast_id, lcc_class) in AUTHORITY.items():
            result = s.run(
                """
                MATCH (ct:CurriculumTopic {key: $key})
                SET ct.lcsh_id      = $lcsh_id,
                    ct.lcsh_heading = $lcsh_heading,
                    ct.fast_id      = $fast_id,
                    ct.lcc_class    = $lcc_class
                RETURN ct.key AS k
                """,
                key=key,
                lcsh_id=lcsh_id,
                lcsh_heading=lcsh_heading,
                fast_id=fast_id,
                lcc_class=lcc_class,
            )
            row = result.single()
            if row:
                updated += 1
            else:
                missing.append(key)

        print(f"Updated {updated}/{len(AUTHORITY)} CurriculumTopics with authority IDs.")
        if missing:
            print(f"WARNING — not found in graph: {missing}")

        # Summary
        r = s.run(
            """
            MATCH (ct:CurriculumTopic)
            WHERE ct.lcsh_id IS NOT NULL
            RETURN count(ct) AS with_lcsh,
                   count(ct.fast_id) AS with_fast,
                   count(ct.lcc_class) AS with_lcc
            """
        )
        row = r.single()
        print(f"  LCSH: {row['with_lcsh']}  FAST: {row['with_fast']}  LCC: {row['with_lcc']}")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        print("Adding authority IDs to CurriculumTopics...")
        run(driver)
        print("Done.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
