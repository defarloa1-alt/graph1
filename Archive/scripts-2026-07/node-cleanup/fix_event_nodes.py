"""
Pre-consolidation fix for EVENT nodes.
Adds required 'start_date' property to EVENT nodes before consolidation.
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USERNAME', os.getenv('NEO4J_USER'))
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("="*70)
print("EVENT PRE-CONSOLIDATION FIX")
print("="*70)

with driver.session() as session:
    # Strategy: If EVENT node has 'date' property, use it as start_date
    # Otherwise, use a placeholder date since these are test nodes
    
    print("\n1. Fixing EVENT nodes with 'date' property:")
    result = session.run("""
        MATCH (e:EVENT)
        WHERE e.date IS NOT NULL AND e.start_date IS NULL
        SET e.start_date = e.date
        RETURN count(e) as fixed, collect(e.label)[0..3] as sample_labels
    """)
    record = result.single()
    print(f"   Fixed: {record['fixed']} nodes")
    print(f"   Labels: {record['sample_labels']}")
    
    print("\n2. Fixing remaining EVENT nodes (test nodes without dates):")
    result = session.run("""
        MATCH (e:EVENT)
        WHERE e.start_date IS NULL
        SET e.start_date = 'unknown'
        RETURN count(e) as fixed, collect(e.label)[0..5] as sample_labels
    """)
    record = result.single()
    print(f"   Fixed: {record['fixed']} nodes")
    print(f"   Labels: {record['sample_labels']}")
    
    print("\n3. Verification - EVENT nodes still missing start_date:")
    result = session.run("""
        MATCH (e:EVENT)
        WHERE e.start_date IS NULL
        RETURN count(e) as still_missing
    """)
    print(f"   Count: {result.single()['still_missing']}")
    
    print("\n4. All EVENT nodes now have start_date:")
    result = session.run("""
        MATCH (e:EVENT)
        RETURN e.label as label, e.start_date as start_date
        ORDER BY e.label
    """)
    for record in result:
        print(f"   {record['label']}: {record['start_date']}")

driver.close()
print("\n" + "="*70)
print("Ready for EVENT -> Event consolidation")
print("="*70)
