#!/usr/bin/env python3
"""Create a FacetRegistry node and wire all 18 Facets to it via REGISTERED_IN edges.

Schema added:
  (FacetRegistry)-[:CONTAINS]->(Facet)

The registry provides:
  - Single entry point for the facet system
  - Version and description metadata
  - A way to assert "these 18 are the complete, authoritative set"

Run:
  python scripts/bootstrap/facet_registry.py
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

REGISTRY = {
    "key": "chrystallum_facets_v1",
    "label": "Chrystallum Facet Registry",
    "version": "1.0",
    "description": (
        "The authoritative set of 18 analytical facets used to decompose historical domains "
        "into curriculum topics and subject concepts. Each facet represents a distinct "
        "dimension of historical inquiry, grounded in university discipline sources."
    ),
    "facet_count": 18,
}

# Canonical facet definitions — key, label, description
FACETS = [
    ("archaeological",  "Archaeological",  "Material remains, excavation, and the physical traces of past societies."),
    ("artistic",        "Artistic",        "Visual arts, architecture, aesthetics, and cultural production."),
    ("biographic",      "Biographic",      "Individual lives, careers, identity, and prosopographical methods."),
    ("communication",   "Communication",   "Rhetoric, writing, oral tradition, and channels of information exchange."),
    ("cultural",        "Cultural",        "Mentalities, worldviews, cultural exchange, and symbolic systems."),
    ("demographic",     "Demographic",     "Population size, structure, migration, family, and mortality patterns."),
    ("diplomatic",      "Diplomatic",      "Foreign policy, treaties, international relations, and diplomacy."),
    ("economic",        "Economic",        "Trade, finance, labor, markets, and economic institutions."),
    ("environmental",   "Environmental",   "Climate, ecology, disease, land use, and human-environment interaction."),
    ("geographic",      "Geographic",      "Place, territory, landscape, cartography, and spatial analysis."),
    ("intellectual",    "Intellectual",    "Philosophy, history of ideas, and the development of thought."),
    ("linguistic",      "Linguistic",      "Language change, multilingualism, epigraphy, and literacy."),
    ("military",        "Military",        "Warfare, strategy, command, logistics, and the military-political nexus."),
    ("political",       "Political",       "Governance, state formation, political thought, and institutions."),
    ("religious",       "Religious",       "Ritual, theology, scripture, and the intersection of religion and power."),
    ("scientific",      "Scientific",      "Natural philosophy, scientific method, and the history of science."),
    ("social",          "Social",          "Class, gender, community, family, and social theory."),
    ("technological",   "Technological",   "Innovation, infrastructure, military technology, and diffusion of techniques."),
]


def run(driver):
    with driver.session() as s:
        # Create/update FacetRegistry node
        s.run(
            """
            MERGE (fr:FacetRegistry {key: $key})
            SET fr.label        = $label,
                fr.version      = $version,
                fr.description  = $description,
                fr.facet_count  = $facet_count
            """,
            **REGISTRY,
        )
        print(f"FacetRegistry: {REGISTRY['label']} v{REGISTRY['version']}")

        # Enrich Facet nodes with descriptions and wire CONTAINS edges
        wired = 0
        for key, label, description in FACETS:
            s.run(
                """
                MERGE (f:Facet {key: $key})
                SET f.label       = $label,
                    f.description = $description
                WITH f
                MATCH (fr:FacetRegistry {key: $reg_key})
                MERGE (fr)-[:CONTAINS]->(f)
                """,
                key=key,
                label=label,
                description=description,
                reg_key=REGISTRY["key"],
            )
            wired += 1
            print(f"  [{wired:02d}] {label}")

        # Verify
        r = s.run(
            """
            MATCH (fr:FacetRegistry)-[:CONTAINS]->(f:Facet)
            RETURN fr.label AS registry, count(f) AS facets
            """
        )
        row = r.single()
        print(f"\nRegistry '{row['registry']}' contains {row['facets']} Facets.")

        # Show full chain depth
        r2 = s.run(
            """
            MATCH (fr:FacetRegistry)-[:CONTAINS]->(f:Facet)-[:HAS_TOPIC]->(ct:CurriculumTopic)
            RETURN count(ct) AS topics
            """
        )
        row2 = r2.single()
        print(f"Reachable CurriculumTopics from registry: {row2['topics']}")

        r3 = s.run(
            """
            MATCH (fr:FacetRegistry)-[:CONTAINS]->(f:Facet)-[:HAS_TOPIC]->(ct:CurriculumTopic)
                  -[:GROUNDED_IN]->(ds:DisciplineSource)
            RETURN count(distinct ds) AS sources
            """
        )
        row3 = r3.single()
        print(f"Reachable DisciplineSources from registry: {row3['sources']}")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        run(driver)
        print("Done.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
