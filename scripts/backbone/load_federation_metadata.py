#!/usr/bin/env python3
"""
Load Federation Metadata Subgraph to Neo4j

Creates the self-describing governance layer for stateless SCA bootstrap.
"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

print("=" * 80)
print("LOADING FEDERATION METADATA SUBGRAPH")
print("=" * 80)
print()

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    
    # 1. Create FederationRoot
    print("[1/7] Creating FederationRoot...")
    session.run("""
        MERGE (fed:FederationRoot {name: 'Chrystallum Federation'})
        SET fed.version = '1.0',
            fed.created = datetime(),
            fed.last_updated = datetime()
    """)
    print("  Created FederationRoot")
    print()
    
    # 2. Create FederationType nodes
    print("[2/7] Creating FederationType nodes...")
    session.run("""
        MATCH (fed:FederationRoot)
        
        MERGE (place:FederationType {name: 'Place'})
        SET place.scope = 'geographic',
            place.node_label = 'Place',
            place.current_count = 41993
        MERGE (fed)-[:HAS_FEDERATION]->(place)
        
        MERGE (period:FederationType {name: 'Period'})
        SET period.scope = 'temporal',
            period.node_label = 'Period',
            period.current_count = 1077
        MERGE (fed)-[:HAS_FEDERATION]->(period)
        
        MERGE (subject:FederationType {name: 'SubjectConcept'})
        SET subject.scope = 'semantic',
            subject.node_label = 'SubjectConcept',
            subject.current_count = 87
        MERGE (fed)-[:HAS_FEDERATION]->(subject)
    """)
    print("  Created 3 FederationType nodes")
    print()
    
    # 3. Create AuthoritySource nodes
    print("[3/7] Creating AuthoritySource nodes...")
    session.run("""
        MERGE (pleiades:AuthoritySource {name: 'Pleiades'})
        SET pleiades.mode = 'local',
            pleiades.file_path = 'Geographic/pleiades_places.csv',
            pleiades.type = 'geographic',
            pleiades.coverage = 41993
        
        MERGE (periodo:AuthoritySource {name: 'PeriodO'})
        SET periodo.mode = 'local',
            periodo.file_path = 'Temporal/periodo-dataset.csv',
            periodo.type = 'temporal',
            periodo.coverage = 8959
        
        MERGE (lcsh:AuthoritySource {name: 'LCSH'})
        SET lcsh.mode = 'local',
            lcsh.file_path = 'LCSH/skos_subjects/',
            lcsh.type = 'conceptual'
        
        MERGE (fast:AuthoritySource {name: 'FAST'})
        SET fast.mode = 'local',
            fast.file_path = 'Python/fast/key/FASTTopical_parsed.csv',
            fast.type = 'topical'
        
        MERGE (lcc:AuthoritySource {name: 'LCC'})
        SET lcc.mode = 'local',
            lcc.file_path = 'Subjects/lcc_flat.csv',
            lcc.type = 'classification'
        
        MERGE (wikidata:AuthoritySource {name: 'Wikidata'})
        SET wikidata.mode = 'hub_api',
            wikidata.api_endpoint = 'https://query.wikidata.org/sparql',
            wikidata.type = 'federation_hub',
            wikidata.role = 'Global knowledge graph - discovery and disambiguation only'
    """)
    print("  Created 6 AuthoritySource nodes (5 local + 1 hub)")
    print()
    
    # 4. Link authorities to federation types
    print("[4/7] Linking authorities to federation types...")
    session.run("""
        MATCH (place:FederationType {name: 'Place'})
        MATCH (period:FederationType {name: 'Period'})
        MATCH (subject:FederationType {name: 'SubjectConcept'})
        
        MATCH (pleiades:AuthoritySource {name: 'Pleiades'})
        MATCH (periodo:AuthoritySource {name: 'PeriodO'})
        MATCH (lcsh:AuthoritySource {name: 'LCSH'})
        MATCH (fast:AuthoritySource {name: 'FAST'})
        MATCH (lcc:AuthoritySource {name: 'LCC'})
        MATCH (wikidata:AuthoritySource {name: 'Wikidata'})
        
        MERGE (place)-[:USES_SOURCE {weight: 20, score_points: 20}]->(pleiades)
        MERGE (place)-[:USES_SOURCE {weight: 50, score_points: 50}]->(wikidata)
        
        MERGE (period)-[:USES_SOURCE {weight: 30, score_points: 30}]->(periodo)
        MERGE (period)-[:USES_SOURCE {weight: 50, score_points: 50}]->(wikidata)
        
        MERGE (subject)-[:USES_SOURCE {weight: 30, score_points: 30}]->(lcsh)
        MERGE (subject)-[:USES_SOURCE {weight: 30, score_points: 30}]->(fast)
        MERGE (subject)-[:USES_SOURCE {weight: 20, score_points: 20}]->(lcc)
        MERGE (subject)-[:USES_SOURCE {weight: 20, score_points: 20}]->(wikidata)
    """)
    print("  Linked authorities to federation types with scoring weights")
    print()
    
    # 5. Create Policy nodes
    print("[5/7] Creating Policy nodes...")
    session.run("""
        MATCH (fed:FederationRoot)
        
        MERGE (p1:Policy {name: 'LocalFirstCanonicalAuthorities'})
        SET p1.description = 'Always check local authorities before hub API',
            p1.status = 'active',
            p1.priority = 1
        MERGE (fed)-[:HAS_POLICY]->(p1)
        
        MERGE (p2:Policy {name: 'HubForDisambiguationOnly'})
        SET p2.description = 'Use Wikidata for discovery/disambiguation, not as primary source',
            p2.status = 'active',
            p2.priority = 2
        MERGE (fed)-[:HAS_POLICY]->(p2)
        
        MERGE (p3:Policy {name: 'NoTemporalFacet'})
        SET p3.description = 'TEMPORAL is NOT a facet - use Year backbone, Period, Event',
            p3.status = 'active',
            p3.priority = 3
        MERGE (fed)-[:HAS_POLICY]->(p3)
        
        MERGE (p4:Policy {name: 'NoClassificationFacet'})
        SET p4.description = 'CLASSIFICATION via LCC properties, not facet',
            p4.status = 'active',
            p4.priority = 4
        MERGE (fed)-[:HAS_POLICY]->(p4)
        
        MERGE (p5:Policy {name: 'ApprovalRequired'})
        SET p5.description = 'All discoveries require human approval before promotion',
            p5.status = 'active',
            p5.priority = 5
        MERGE (fed)-[:HAS_POLICY]->(p5)
    """)
    print("  Created 5 Policy nodes")
    print()
    
    # 6. Create Threshold nodes
    print("[6/7] Creating Threshold nodes...")
    session.run("""
        MATCH (fed:FederationRoot)
        
        MERGE (t1:Threshold {name: 'crosslink_ratio_split'})
        SET t1.value = 0.30,
            t1.description = 'Split SFA when cross-link ratio exceeds 30%'
        MERGE (fed)-[:HAS_THRESHOLD]->(t1)
        
        MERGE (t2:Threshold {name: 'level2_child_overload'})
        SET t2.value = 12,
            t2.description = 'Split when L2 node has >12 children'
        MERGE (fed)-[:HAS_THRESHOLD]->(t2)
        
        MERGE (t3:Threshold {name: 'facet_drift_alert'})
        SET t3.value = 0.20,
            t3.description = 'Alert when 20%+ concepts have LCSH mismatched to facet'
        MERGE (fed)-[:HAS_THRESHOLD]->(t3)
    """)
    print("  Created 3 Threshold nodes")
    print()
    
    # 7. Create/Link Canonical Facets
    print("[7/7] Creating canonical Facet nodes...")
    
    facets = [
        'ARCHAEOLOGICAL', 'ARTISTIC', 'BIOGRAPHIC', 'COMMUNICATION',
        'CULTURAL', 'DEMOGRAPHIC', 'DIPLOMATIC', 'ECONOMIC',
        'ENVIRONMENTAL', 'GEOGRAPHIC', 'INTELLECTUAL', 'LINGUISTIC',
        'MILITARY', 'POLITICAL', 'RELIGIOUS', 'SCIENTIFIC',
        'SOCIAL', 'TECHNOLOGICAL'
    ]
    
    for facet_key in facets:
        session.run("""
            MATCH (fed:FederationRoot)
            MERGE (f:Facet {key: $key})
            SET f.label = $label
            MERGE (fed)-[:HAS_FACET_REGISTRY]->(f)
        """, key=facet_key, label=facet_key.title())
    
    print(f"  Created {len(facets)} canonical Facet nodes")
    print()
    
    # Verification
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    result = session.run("""
        MATCH (fed:FederationRoot)
        MATCH (fed)-[:HAS_FEDERATION]->(type:FederationType)
        MATCH (fed)-[:HAS_POLICY]->(policy:Policy)
        MATCH (fed)-[:HAS_THRESHOLD]->(threshold:Threshold)
        MATCH (fed)-[:HAS_FACET_REGISTRY]->(facet:Facet)
        RETURN 
            count(DISTINCT type) AS federation_types,
            count(DISTINCT policy) AS policies,
            count(DISTINCT threshold) AS thresholds,
            count(DISTINCT facet) AS facets
    """)
    
    stats = result.single()
    print(f"\nFederation metadata loaded:")
    print(f"  Federation types: {stats['federation_types']}")
    print(f"  Policies: {stats['policies']}")
    print(f"  Thresholds: {stats['thresholds']}")
    print(f"  Canonical facets: {stats['facets']}")
    
    # Test bootstrap query
    print("\nTesting bootstrap query...")
    result = session.run("""
        MATCH (fed:FederationRoot)
        WITH fed
        
        CALL {
          WITH fed
          MATCH (fed)-[:HAS_FACET_REGISTRY]->(facet:Facet)
          WHERE NOT facet.key IN ['TEMPORAL', 'CLASSIFICATION']
          RETURN 
            collect(facet.key) AS facet_keys,
            size(collect(facet.key)) AS facet_count
        }
        
        CALL {
          WITH fed
          MATCH (fed)-[:HAS_POLICY]->(policy:Policy)
          WHERE policy.status = 'active'
          RETURN collect(policy.name) AS active_policies
        }
        
        RETURN facet_keys, facet_count, active_policies
    """)
    
    bootstrap = result.single()
    print(f"\nBootstrap test:")
    print(f"  Facet count: {bootstrap['facet_count']}")
    print(f"  Active policies: {len(bootstrap['active_policies'])}")
    print(f"  Sample facets: {bootstrap['facet_keys'][:5]}")

driver.close()

print()
print("=" * 80)
print("FEDERATION METADATA LOADED SUCCESSFULLY!")
print("=" * 80)
print()
print("SCA can now bootstrap from graph!")
print()
print("Next: SCA executes bootstrap query and gets complete operational context")

