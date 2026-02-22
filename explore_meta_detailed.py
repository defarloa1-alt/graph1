#!/usr/bin/env python3
"""Detailed exploration of Chrystallum meta-model with actual properties"""

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
    log("CHRYSTALLUM META-MODEL: DETAILED EXPLORATION")
    log("="*80)
    log("")
    
    # 1. Chrystallum root with all properties
    log("1. CHRYSTALLUM ROOT (SYSTEM NODE)")
    log("-"*80)
    result = session.run("MATCH (c:Chrystallum) RETURN c")
    for r in result:
        c = r['c']
        log("Chrystallum Knowledge Graph:")
        for key, value in dict(c).items():
            log(f"  {key}: {value}")
    log("")
    
    # 2. Federation nodes (all properties)
    log("2. FEDERATION NODES (AUTHORITY SOURCES)")
    log("-"*80)
    result = session.run("MATCH (f:Federation) RETURN f ORDER BY f.name")
    for r in result:
        f = r['f']
        props = dict(f)
        log(f"Federation: {props.get('name', 'UNNAMED')}")
        for key, value in sorted(props.items()):
            log(f"  {key}: {value}")
        log("")
    
    # 3. EntityType registry (all properties)
    log("3. ENTITYTYPE REGISTRY")
    log("-"*80)
    result = session.run("MATCH (et:EntityType) RETURN et")
    for r in result:
        et = r['et']
        props = dict(et)
        log(f"EntityType:")
        for key, value in sorted(props.items()):
            log(f"  {key}: {value}")
        log("")
    
    # 4. Facet registry (all properties)
    log("4. FACET REGISTRY")
    log("-"*80)
    result = session.run("MATCH (f:Facet) RETURN f ORDER BY f.facet_id")
    for r in result:
        f = r['f']
        props = dict(f)
        facet_id = props.get('facet_id', props.get('id', 'UNKNOWN'))
        log(f"Facet {facet_id}:")
        for key, value in sorted(props.items()):
            log(f"  {key}: {value}")
        log("")
    
    # 5. Schema nodes (per entity type)
    log("5. SCHEMA NODES (ENTITY TYPE SCHEMAS)")
    log("-"*80)
    result = session.run("MATCH (s:Schema) RETURN s")
    for r in result:
        s = r['s']
        props = dict(s)
        log(f"Schema:")
        for key, value in sorted(props.items()):
            log(f"  {key}: {value}")
        log("")
    
    # 6. Complete graph structure
    log("6. META-MODEL GRAPH STRUCTURE")
    log("-"*80)
    result = session.run("""
        MATCH (c:Chrystallum)
        OPTIONAL MATCH (c)-[r1]->(root)
        WHERE root:EntityRoot OR root:FacetRoot OR root:SubjectConceptRoot 
           OR root:FederationRoot OR root:Schema
        RETURN 
          labels(c) as chrystallum_labels,
          type(r1) as rel1,
          labels(root) as root_labels,
          root.name as root_name
    """)
    
    log("Chrystallum -> Root Nodes:")
    for r in result:
        if r['rel1']:
            log(f"  [{r['chrystallum_labels'][0]}] -{r['rel1']}-> [{', '.join(r['root_labels'])}] ({r['root_name']})")
    log("")
    
    # 7. AgentRegistry
    log("7. AGENT REGISTRY")
    log("-"*80)
    result = session.run("MATCH (ar:AgentRegistry) RETURN ar")
    for r in result:
        ar = r['ar']
        props = dict(ar)
        log(f"AgentRegistry:")
        for key, value in sorted(props.items()):
            log(f"  {key}: {value}")
    log("")
    
    # 8. Agents
    log("8. AGENT NODES")
    log("-"*80)
    result = session.run("MATCH (a:Agent) RETURN a LIMIT 5")
    for r in result:
        a = r['a']
        props = dict(a)
        log(f"Agent: {props.get('agent_id', 'UNKNOWN')}")
        for key, value in sorted(props.items()):
            log(f"  {key}: {value}")
        log("")
    
    # 9. SubjectConceptRegistry
    log("9. SUBJECTCONCEPT REGISTRY")
    log("-"*80)
    result = session.run("MATCH (scr:SubjectConceptRegistry) RETURN scr")
    for r in result:
        scr = r['scr']
        props = dict(scr)
        log(f"SubjectConceptRegistry:")
        for key, value in sorted(props.items()):
            log(f"  {key}: {value}")
    
    # Count SubjectConcepts
    result = session.run("MATCH (sc:SubjectConcept) RETURN count(sc) as total")
    total_sc = result.single()['total']
    log(f"  Total SubjectConcepts: {total_sc}")
    log("")
    
    # 10. Sample SubjectConcept with relationships
    log("10. SAMPLE SUBJECTCONCEPT (Q17167)")
    log("-"*80)
    result = session.run("""
        MATCH (sc:SubjectConcept {qid: 'Q17167'})
        RETURN sc, keys(sc) as props
    """)
    for r in result:
        sc = r['sc']
        log(f"SubjectConcept Q17167:")
        for key in sorted(r['props']):
            log(f"  {key}: {sc.get(key)}")
    log("")

driver.close()

# Save to file
with open('output/META_MODEL_DETAILED.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("\n[OK] Detailed meta-model exploration complete.")
print("     Report: output/META_MODEL_DETAILED.txt")
