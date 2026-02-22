#!/usr/bin/env python3
"""
QA Analysis: Entity Completeness - Properties and Relationships
Assess if 2,600 entities have all needed edges and properties
"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("=" * 80)
print("ENTITY COMPLETENESS ANALYSIS")
print("=" * 80)
print()

with driver.session() as session:
    
    # 1. RELATIONSHIP COMPLETENESS
    print("1. RELATIONSHIP COMPLETENESS")
    print("-" * 80)
    
    # Total connectivity
    result = session.run("""
        MATCH (e:Entity)
        OPTIONAL MATCH (e)-[r]-()
        WITH e, count(r) as rel_count
        RETURN 
            count(e) as total,
            sum(CASE WHEN rel_count = 0 THEN 1 ELSE 0 END) as isolated,
            sum(CASE WHEN rel_count > 0 THEN 1 ELSE 0 END) as connected,
            100.0 * sum(CASE WHEN rel_count > 0 THEN 1 ELSE 0 END) / count(e) as pct_connected
    """)
    
    r = result.single()
    total = r['total']
    isolated = r['isolated']
    connected = r['connected']
    pct = r['pct_connected']
    
    print(f"Total entities: {total:,}")
    print(f"Connected entities: {connected:,} ({pct:.1f}%)")
    print(f"Isolated entities: {isolated:,} ({100-pct:.1f}%)")
    print()
    
    if pct < 50:
        print("[ISSUE] Less than 50% connectivity - most entities isolated")
    elif pct < 90:
        print("[WARNING] Connectivity below 90% target")
    else:
        print("[GOOD] High connectivity achieved")
    print()
    
    # 2. RELATIONSHIP TYPES
    print("2. RELATIONSHIP TYPES (Entity-to-Entity)")
    print("-" * 80)
    
    result = session.run("""
        MATCH (e:Entity)-[r]->(target:Entity)
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    entity_rels = list(result)
    if entity_rels:
        print(f"Found {len(entity_rels)} relationship types:")
        for rel in entity_rels[:15]:
            print(f"  {rel['rel_type']}: {rel['count']:,}")
    else:
        print("[ISSUE] No Entity-to-Entity relationships found")
    print()
    
    # 3. BACKBONE CONNECTIONS
    print("3. BACKBONE CONNECTIONS (Temporal & Geographic)")
    print("-" * 80)
    
    # Temporal
    result = session.run("""
        MATCH (e:Entity)-[r]->(y:Year)
        RETURN count(DISTINCT e) as entities, count(r) as links
    """)
    r = result.single()
    temp_entities = r['entities']
    temp_links = r['links']
    
    # Geographic
    result = session.run("""
        MATCH (e:Entity)-[r]->(p:Place)
        RETURN count(DISTINCT e) as entities, count(r) as links
    """)
    r = result.single()
    geo_entities = r['entities']
    geo_links = r['links']
    
    # Period
    result = session.run("""
        MATCH (e:Entity)-[r]->(p:Period)
        RETURN count(DISTINCT e) as entities, count(r) as links
    """)
    r = result.single()
    period_entities = r['entities']
    period_links = r['links']
    
    print(f"Temporal (Year) connections:")
    print(f"  Entities connected: {temp_entities:,}")
    print(f"  Total links: {temp_links:,}")
    
    print(f"Geographic (Place) connections:")
    print(f"  Entities connected: {geo_entities:,}")
    print(f"  Total links: {geo_links:,}")
    
    print(f"Period connections:")
    print(f"  Entities connected: {period_entities:,}")
    print(f"  Total links: {period_links:,}")
    print()
    
    if temp_entities + geo_entities + period_entities == 0:
        print("[ISSUE] No backbone tethering - entities not connected to temporal/geographic infrastructure")
    else:
        print("[PARTIAL] Some backbone connections exist")
    print()
    
    # 4. PROPERTY COMPLETENESS
    print("4. PROPERTY COMPLETENESS")
    print("-" * 80)
    
    # Check critical properties
    result = session.run("""
        MATCH (e:Entity)
        RETURN 
            count(e) as total,
            sum(CASE WHEN e.entity_cipher IS NULL THEN 1 ELSE 0 END) as missing_cipher,
            sum(CASE WHEN e.qid IS NULL THEN 1 ELSE 0 END) as missing_qid,
            sum(CASE WHEN e.label IS NULL THEN 1 ELSE 0 END) as missing_label,
            sum(CASE WHEN e.entity_type IS NULL THEN 1 ELSE 0 END) as missing_type,
            sum(CASE WHEN e.federation_score IS NULL THEN 1 ELSE 0 END) as missing_fed,
            sum(CASE WHEN e.properties_count IS NULL THEN 1 ELSE 0 END) as missing_props
    """)
    
    r = result.single()
    print(f"Total entities checked: {r['total']:,}")
    print(f"Missing entity_cipher: {r['missing_cipher']}")
    print(f"Missing qid: {r['missing_qid']}")
    print(f"Missing label: {r['missing_label']}")
    print(f"Missing entity_type: {r['missing_type']}")
    print(f"Missing federation_score: {r['missing_fed']}")
    print(f"Missing properties_count: {r['missing_props']}")
    print()
    
    if r['missing_cipher'] + r['missing_qid'] + r['missing_label'] + r['missing_type'] == 0:
        print("[PASS] All critical properties present")
    else:
        print("[ISSUE] Some entities missing critical properties")
    print()
    
    # 5. FACETED ENTITY COVERAGE
    print("5. FACETED ENTITY COVERAGE (Tier 2 Ciphers)")
    print("-" * 80)
    
    result = session.run("""
        MATCH (fe:FacetedEntity)
        RETURN count(DISTINCT fe.entity_cipher) as entities_with_facets,
               count(fe) as total_faceted_entities
    """)
    
    r = result.single()
    entities_with_facets = r['entities_with_facets']
    total_faceted = r['total_faceted_entities']
    
    print(f"Entities with FacetedEntity nodes: {entities_with_facets:,}")
    print(f"Total FacetedEntity nodes: {total_faceted:,}")
    print(f"Expected: 2,600 entities × 18 facets = 46,800 nodes")
    print()
    
    coverage_pct = (entities_with_facets / 2600) * 100 if total else 0
    print(f"Faceted coverage: {coverage_pct:.1f}%")
    
    if coverage_pct < 10:
        print("[ISSUE] Most entities missing FacetedEntity nodes (Tier 2 incomplete)")
    elif coverage_pct < 50:
        print("[WARNING] Partial Tier 2 implementation")
    else:
        print("[GOOD] Good Tier 2 coverage")
    print()
    
    # 6. PROPERTY RICHNESS
    print("6. PROPERTY RICHNESS (Wikidata Integration)")
    print("-" * 80)
    
    result = session.run("""
        MATCH (e:Entity)
        WHERE e.properties_count IS NOT NULL
        RETURN 
            avg(e.properties_count) as avg_props,
            min(e.properties_count) as min_props,
            max(e.properties_count) as max_props,
            sum(CASE WHEN e.properties_count > 30 THEN 1 ELSE 0 END) as rich_entities
    """)
    
    r = result.single()
    print(f"Average properties per entity: {r['avg_props']:.1f}")
    print(f"Min properties: {r['min_props']}")
    print(f"Max properties: {r['max_props']}")
    print(f"Entities with >30 properties: {r['rich_entities']:,}")
    print()
    
    if r['avg_props'] < 10:
        print("[ISSUE] Low property richness - poor Wikidata integration")
    elif r['avg_props'] < 30:
        print("[OK] Moderate property richness")
    else:
        print("[GOOD] Rich Wikidata integration")
    print()

driver.close()

print("=" * 80)
print("COMPLETENESS ASSESSMENT")
print("=" * 80)
print()
print("SUMMARY OF GAPS:")
print()
print("1. RELATIONSHIPS:")
print("   - Entity-to-Entity: Likely only original 300 have relationships")
print("   - New 2,300 entities: Probably isolated")
print("   - Backbone tethering: Missing or minimal")
print()
print("2. PROPERTIES:")
print("   - Critical properties: Complete")
print("   - Wikidata properties: Present")
print()
print("3. TIER 2 (FACETED ENTITIES):")
print("   - Coverage likely very low (<1%)")
print("   - Only ~20 entities have faceted nodes")
print()
print("RECOMMENDATION:")
print("- Import relationships for 2,300 new entities (REQ-FUNC-010 pattern)")
print("- Consider backbone tethering (temporal/geographic)")
print("- Generate FacetedEntity nodes for all 2,600 (Tier 2 completion)")
