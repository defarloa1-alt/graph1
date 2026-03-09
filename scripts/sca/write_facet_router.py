"""
write_facet_router.py

Creates SYS_FacetRouter nodes in the graph — one per LCSH heading pattern.
Each node links to Facet nodes via HAS_PRIMARY_FACET and HAS_SECONDARY_FACET.

This replaces all pattern-matching code with queryable graph data.
Idempotent (MERGE on pattern key).
"""

from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# ── The routing table — LCSH pattern → facet assignments ────────────────────
# Derived from LoC heading conventions + Chrystallum 18-facet model.
# "Legal", "Institutional", "Organizational" from classical library science
# are mapped to their Chrystallum equivalents.
ROUTES = [
    # pattern              match_type   primary          secondaries
    ("Army",               "contains",  "Military",      ["Technological", "Social"]),
    ("Navy",               "contains",  "Military",      ["Technological", "Economic"]),
    ("Weapons",            "contains",  "Technological", ["Military"]),
    ("Technology",         "contains",  "Technological", ["Economic", "Military"]),
    ("Engineering",        "contains",  "Technological", ["Environmental", "Economic"]),
    ("Economic conditions","contains",  "Economic",      ["Social", "Environmental"]),
    ("Taxation",           "contains",  "Economic",      ["Political", "Social"]),
    ("Trade routes",       "contains",  "Economic",      ["Geographic", "Technological"]),
    ("Religion",           "contains",  "Religious",     ["Cultural", "Social"]),
    ("Cults",              "contains",  "Religious",     ["Cultural"]),
    ("Politics and government","contains","Political",   ["Social"]),
    ("Constitutional history","contains","Political",    ["Intellectual"]),
    ("Officials and employees","contains","Political",   ["Biographic"]),
    ("Senate",             "contains",  "Political",     ["Social", "Diplomatic"]),
    ("Assemblies",         "contains",  "Political",     ["Demographic", "Communication"]),
    ("Foreign relations",  "contains",  "Diplomatic",    ["Political", "Geographic"]),
    ("Slavery",            "contains",  "Social",        ["Economic", "Demographic", "Cultural"]),
    ("Women",              "contains",  "Social",        ["Biographic", "Cultural", "Demographic"]),
    ("Families",           "contains",  "Social",        ["Biographic", "Demographic", "Religious"]),
    ("Social life and customs","contains","Cultural",    ["Social", "Demographic"]),
    ("Provinces",          "contains",  "Geographic",    ["Political", "Economic"]),
    ("province",           "contains",  "Geographic",    ["Political", "Military"]),
    ("Archaeology",        "contains",  "Archaeological",["Environmental", "Cultural"]),
    ("Excavations",        "contains",  "Archaeological",["Geographic", "Environmental"]),
    ("Antiquities",        "contains",  "Archaeological",["Geographic", "Artistic"]),
    ("Land use",           "contains",  "Environmental", ["Economic", "Social"]),
    ("Deforestation",      "contains",  "Environmental", ["Economic", "Technological"]),
    ("Science, Ancient",   "contains",  "Scientific",    ["Technological", "Intellectual"]),
    ("Medicine",           "contains",  "Scientific",    ["Biographic", "Social"]),
    ("Inscriptions",       "contains",  "Communication", ["Archaeological", "Linguistic"]),
    ("Oratory",            "contains",  "Communication", ["Political", "Social"]),
    ("Education",          "contains",  "Communication", ["Cultural", "Social"]),
    ("Latin literature",   "contains",  "Intellectual",  ["Communication", "Cultural", "Linguistic"]),
    ("Historiography",     "contains",  "Intellectual",  ["Communication", "Biographic"]),
    ("Art, Roman",         "exact",     "Artistic",      ["Archaeological", "Cultural"]),
    ("Biography",          "contains",  "Biographic",    ["Political"]),
]

CYPHER = """
MERGE (r:SYS_FacetRouter {pattern: $pattern})
SET r.match_type = $match_type,
    r.primary_facet = $primary,
    r.secondary_facets = $secondaries,
    r.updated = datetime()
WITH r

// Wire primary facet
MATCH (fp:Facet {label: $primary})
MERGE (r)-[:HAS_PRIMARY_FACET]->(fp)

// Wire secondary facets
WITH r
UNWIND $secondaries AS sec
MATCH (fs:Facet {label: sec})
MERGE (r)-[:HAS_SECONDARY_FACET]->(fs)
"""

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        for pattern, match_type, primary, secondaries in ROUTES:
            result = session.run(CYPHER, {
                "pattern": pattern,
                "match_type": match_type,
                "primary": primary,
                "secondaries": secondaries,
            })
            result.consume()
            print(f"  {pattern:<30} -> {primary:<16} + {secondaries}")

    # Verify
    with driver.session() as session:
        count = session.run(
            "MATCH (r:SYS_FacetRouter) RETURN count(r) AS c"
        ).single()["c"]
        edges = session.run(
            "MATCH (r:SYS_FacetRouter)-[e]->(:Facet) RETURN count(e) AS c"
        ).single()["c"]
        print(f"\nGraph: {count} SYS_FacetRouter nodes, {edges} edges to Facet nodes")

    driver.close()


if __name__ == "__main__":
    main()
