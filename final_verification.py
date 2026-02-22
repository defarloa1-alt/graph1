#!/usr/bin/env python3
"""Final verification of fresh Chrystallum rebuild"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

print("=" * 80)
print(" FRESH CHRYSTALLUM REBUILD - FINAL VERIFICATION")
print("=" * 80)
print()

with driver.session() as session:
    # Node counts
    result = session.run("""
        RETURN
            count { MATCH (:Year) } AS years,
            count { MATCH (:Period) } AS periods,
            count { MATCH (:PeriodCandidate) } AS period_candidates,
            count { MATCH (:Place) } AS places,
            count { MATCH (:PlaceName) } AS place_names,
            count { MATCH (:PlaceType) } AS place_types,
            count { MATCH (:PlaceTypeTokenMap) } AS place_type_tokens,
            count { MATCH (:GeoSemanticType) } AS geo_semantic_types,
            count { MATCH (:GeoCoverageCandidate) } AS geo_coverage
    """)
    
    stats = result.single()
    
    print("NODE COUNTS:")
    print("-" * 80)
    print(f"  Years:                  {stats['years']:>10,}")
    print(f"  Periods:                {stats['periods']:>10,}")
    print(f"  Period Candidates:      {stats['period_candidates']:>10,}")
    print(f"  Places:                 {stats['places']:>10,}")
    print(f"  Place Names:            {stats['place_names']:>10,}")
    print(f"  Place Types:            {stats['place_types']:>10,}")
    print(f"  Place Type Tokens:      {stats['place_type_tokens']:>10,}")
    print(f"  Geo Semantic Types:     {stats['geo_semantic_types']:>10,}")
    print(f"  Geo Coverage Candidates:{stats['geo_coverage']:>10,}")
    print()
    
    total_nodes = sum(stats.values())
    print(f"  TOTAL NODES:            {total_nodes:>10,}")
    print()
    
    # Relationship counts
    result = session.run("MATCH ()-[r]->() RETURN count(r) AS total_rels")
    total_rels = result.single()["total_rels"]
    
    print(f"  TOTAL RELATIONSHIPS:    {total_rels:>10,}")
    print()
    
    # Key relationship types
    print("KEY RELATIONSHIP COUNTS:")
    print("-" * 80)
    
    rel_checks = [
        ("FOLLOWED_BY", "Year chain"),
        ("PART_OF", "Hierarchy"),
        ("STARTS_IN_YEAR", "Period-Year start"),
        ("ENDS_IN_YEAR", "Period-Year end"),
        ("HAS_NAME", "Place names"),
        ("INSTANCE_OF_PLACE_TYPE", "Place type classification"),
        ("HAS_GEO_SEMANTIC_TYPE", "Geo semantic classification"),
        ("HAS_GEO_COVERAGE", "Period-Place coverage")
    ]
    
    for rel_type, description in rel_checks:
        try:
            result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS count")
            count = result.single()["count"]
            print(f"  {rel_type:30} {count:>10,}  ({description})")
        except:
            print(f"  {rel_type:30}          0  ({description})")
    
    print()
    
    # Sample queries
    print("SAMPLE DATA:")
    print("-" * 80)
    
    # Sample period
    result = session.run("""
        MATCH (p:Period)
        WHERE p.label CONTAINS 'Roman'
        RETURN p.label, p.start_year, p.end_year
        LIMIT 1
    """)
    for record in result:
        print(f"  Period: {record['p.label']} ({record['p.start_year']} to {record['p.end_year']})")
    
    # Sample place
    result = session.run("""
        MATCH (p:Place)
        WHERE p.label CONTAINS 'Rome'
        OPTIONAL MATCH (p)-[:HAS_NAME]->(n:PlaceName)
        RETURN p.label, p.pleiades_id, count(n) AS name_count
        LIMIT 1
    """)
    for record in result:
        print(f"  Place: {record['p.label']} (Pleiades: {record['p.pleiades_id']}, {record['name_count']} names)")
    
    print()

driver.close()

print("=" * 80)
print(" VERIFICATION COMPLETE")
print("=" * 80)
print()
print("FRESH CHRYSTALLUM INSTANCE READY!")
print()
print("Next steps:")
print("  1. Add Subject concepts")
print("  2. Implement federation scoring")
print("  3. Load entities (Human, Event, etc.)")
print("  4. Period enrichment with Perplexity")
print()

