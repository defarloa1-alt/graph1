#!/usr/bin/env python3
"""Explore Chrystallum's self-describing meta-model"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

output = []

def log(msg):
    output.append(msg)
    print(msg)

with driver.session() as session:
    log("="*80)
    log("CHRYSTALLUM META-MODEL EXPLORATION")
    log("="*80)
    log("")
    
    # 1. Find Chrystallum root node
    log("1. CHRYSTALLUM ROOT NODE")
    log("-"*80)
    result = session.run("""
        MATCH (c:Chrystallum)
        RETURN c, keys(c) as props
    """)
    for r in result:
        node = r['c']
        log(f"Found Chrystallum node:")
        log(f"  Properties: {sorted(r['props'])}")
        for key in sorted(r['props']):
            log(f"    {key}: {node.get(key)}")
    log("")
    
    # 2. Federation structure
    log("2. FEDERATION STRUCTURE")
    log("-"*80)
    result = session.run("""
        MATCH (f:Federation)
        RETURN f.federation_id as id,
               f.label as label,
               f.description as desc,
               keys(f) as props
    """)
    
    federations = []
    for r in result:
        federations.append(r['id'])
        log(f"Federation: {r['id']}")
        log(f"  Label: {r['label']}")
        log(f"  Desc: {r['desc']}")
        log(f"  Properties: {sorted(r['props'])}")
    log("")
    
    # 3. Federation relationships
    log("3. FEDERATION RELATIONSHIPS")
    log("-"*80)
    result = session.run("""
        MATCH (c:Chrystallum)-[r:HAS_FEDERATION]->(f:Federation)
        RETURN f.federation_id as fed_id,
               f.label as label,
               type(r) as rel_type
    """)
    for r in result:
        log(f"  Chrystallum -[{r['rel_type']}]-> {r['fed_id']} ({r['label']})")
    log("")
    
    # 4. Entity Root structure
    log("4. ENTITY ROOT STRUCTURE")
    log("-"*80)
    result = session.run("""
        MATCH (root:EntityRoot)
        RETURN root, keys(root) as props
        LIMIT 5
    """)
    for r in result:
        node = r['root']
        log(f"EntityRoot node:")
        for key in sorted(r['props']):
            log(f"  {key}: {node.get(key)}")
        log("")
    
    # 5. Facet Root structure
    log("5. FACET ROOT STRUCTURE")
    log("-"*80)
    result = session.run("""
        MATCH (root:FacetRoot)
        RETURN root, keys(root) as props
    """)
    for r in result:
        node = r['root']
        log(f"FacetRoot node:")
        for key in sorted(r['props']):
            log(f"  {key}: {node.get(key)}")
    log("")
    
    # 6. SubjectConcept Root structure
    log("6. SUBJECTCONCEPT ROOT STRUCTURE")
    log("-"*80)
    result = session.run("""
        MATCH (root:SubjectConceptRoot)
        RETURN root, keys(root) as props
    """)
    for r in result:
        node = r['root']
        log(f"SubjectConceptRoot node:")
        for key in sorted(r['props']):
            log(f"  {key}: {node.get(key)}")
    log("")
    
    # 7. EntityType registry
    log("7. ENTITYTYPE REGISTRY")
    log("-"*80)
    result = session.run("""
        MATCH (et:EntityType)
        RETURN et.type_name as name,
               et.description as desc,
               et.prefix as prefix
        ORDER BY name
    """)
    for r in result:
        log(f"  EntityType: {r['name']}")
        log(f"    Prefix: {r['prefix']}")
        log(f"    Desc: {r['desc']}")
    log("")
    
    # 8. Facet registry
    log("8. FACET REGISTRY")
    log("-"*80)
    result = session.run("""
        MATCH (f:Facet)
        RETURN f.facet_id as id,
               f.facet_name as name,
               f.prefix as prefix
        ORDER BY id
    """)
    for r in result:
        log(f"  Facet: {r['id']}")
        log(f"    Name: {r['name']}")
        log(f"    Prefix: {r['prefix']}")
    log("")
    
    # 9. Schema node
    log("9. SCHEMA NODE")
    log("-"*80)
    result = session.run("""
        MATCH (s:Schema)
        RETURN s, keys(s) as props
    """)
    for r in result:
        node = r['s']
        log(f"Schema node:")
        for key in sorted(r['props']):
            log(f"  {key}: {node.get(key)}")
    log("")
    
    # 10. Complete meta-model structure
    log("10. COMPLETE META-MODEL GRAPH")
    log("-"*80)
    result = session.run("""
        MATCH path = (c:Chrystallum)-[*1..2]->(related)
        WHERE related:Federation OR related:EntityRoot OR related:FacetRoot 
           OR related:SubjectConceptRoot OR related:Schema
        RETURN 
          c.system_name as system,
          [n in nodes(path) | labels(n)] as node_labels,
          [r in relationships(path) | type(r)] as rel_types
        LIMIT 20
    """)
    
    log("Meta-model paths from Chrystallum:")
    for r in result:
        log(f"  {r['system']} -> {' -> '.join([str(labels) for labels in r['node_labels']])}")
        log(f"    Relationships: {' -> '.join(r['rel_types'])}")
    log("")
    
    # 11. Count meta-nodes
    log("11. META-NODE COUNTS")
    log("-"*80)
    meta_labels = [
        "Chrystallum", "Federation", "FederationRoot", "EntityRoot",
        "FacetRoot", "SubjectConceptRoot", "EntityType", "Facet",
        "Schema", "AgentRegistry", "SubjectConceptRegistry"
    ]
    
    for label in meta_labels:
        result = session.run(f"MATCH (n:{label}) RETURN count(n) as total")
        count = result.single()['total']
        log(f"  {label}: {count} nodes")
    log("")

driver.close()

# Save to file
with open('output/META_MODEL_EXPLORATION.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("\n[OK] Meta-model exploration complete. Report: output/META_MODEL_EXPLORATION.txt")
