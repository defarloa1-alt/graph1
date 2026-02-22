#!/usr/bin/env python3
"""
Cleanup Non-Canonical Nodes from Neo4j

Removes old facet class nodes and legacy federation structure.
Aligns Neo4j with canonical architecture.
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("CLEANUP: Removing Non-Canonical Nodes")
print("=" * 80)
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    
    # Count before
    result = session.run("MATCH (n) RETURN count(n) AS total_before")
    total_before = result.single()["total_before"]
    
    print(f"Nodes before cleanup: {total_before:,}")
    print()
    
    # 1. Delete 18 individual facet class nodes
    print("[1/3] Deleting 18 individual facet class nodes...")
    result = session.run("""
        MATCH (n)
        WHERE n:ArchaeologicalFacet 
           OR n:ArtisticFacet 
           OR n:BiographicFacet
           OR n:CommunicationFacet 
           OR n:CulturalFacet 
           OR n:DemographicFacet
           OR n:DiplomaticFacet 
           OR n:EconomicFacet 
           OR n:EnvironmentalFacet
           OR n:GeographicFacet 
           OR n:IntellectualFacet 
           OR n:LinguisticFacet
           OR n:MilitaryFacet 
           OR n:PoliticalFacet 
           OR n:ReligiousFacet
           OR n:ScientificFacet 
           OR n:SocialFacet 
           OR n:TechnologicalFacet
        DETACH DELETE n
        RETURN count(n) AS deleted
    """)
    facet_deleted = result.single()["deleted"]
    print(f"  Deleted: {facet_deleted} old facet nodes")
    print()
    
    # 2. Delete old federation structure nodes
    print("[2/3] Deleting old federation structure nodes...")
    result = session.run("""
        MATCH (n)
        WHERE n:AuthoritySystem 
           OR n:Category 
           OR n:Chrystallum 
           OR n:Facets 
           OR n:Root
           OR n:CanonicalFacet
        DETACH DELETE n
        RETURN count(n) AS deleted
    """)
    federation_deleted = result.single()["deleted"]
    print(f"  Deleted: {federation_deleted} old federation nodes")
    print()
    
    # 3. Remove E4_Period label from Period nodes (keep Period label)
    print("[3/3] Removing E4_Period label (keeping Period label)...")
    result = session.run("""
        MATCH (p:E4_Period)
        REMOVE p:E4_Period
        RETURN count(p) AS updated
    """)
    periods_updated = result.single()["updated"]
    print(f"  Updated: {periods_updated} period nodes (removed E4_Period label)")
    print()
    
    # Count after
    result = session.run("MATCH (n) RETURN count(n) AS total_after")
    total_after = result.single()["total_after"]
    
    # Verify canonical facets still exist
    result = session.run("""
        MATCH (:FederationRoot)-[:HAS_FACET_REGISTRY]->(f:Facet)
        RETURN count(f) AS canonical_facets
    """)
    canonical_facets = result.single()["canonical_facets"]
    
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print()
    print(f"Nodes before: {total_before:,}")
    print(f"Nodes deleted: {facet_deleted + federation_deleted:,}")
    print(f"Nodes after: {total_after:,}")
    print()
    print(f"Canonical Facet nodes remaining: {canonical_facets}")
    print()
    print("Removed:")
    print(f"  - {facet_deleted} individual facet class nodes")
    print(f"  - {federation_deleted} old federation structure nodes")
    print(f"  - E4_Period label from {periods_updated} Period nodes")
    print()
    print("Architecture now aligned!")
    print()
    
    # Show remaining labels
    result = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
    remaining_labels = [record['label'] for record in result]
    
    print(f"Remaining labels: {len(remaining_labels)}")
    print()
    print("Sample (first 20):")
    for label in remaining_labels[:20]:
        count_result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
        count = count_result.single()['count']
        print(f"  {label:30} {count:>10,}")

driver.close()

print()
print("=" * 80)
print("Neo4j now aligned with canonical architecture!")
print("=" * 80)

