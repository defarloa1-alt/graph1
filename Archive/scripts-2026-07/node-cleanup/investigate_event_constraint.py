"""
Additional investigation for EVENT consolidation issue.
Found constraint: Event nodes must have 'start_date' property
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
print("EVENT CONSTRAINT INVESTIGATION")
print("="*70)

with driver.session() as session:
    # Check Event constraints
    print("\n1. Event label constraints:")
    result = session.run("SHOW CONSTRAINTS")
    for record in result:
        if 'Event' in str(record):
            print(f"  {record}")
    
    # Check EVENT node properties
    print("\n2. EVENT node properties:")
    result = session.run("""
        MATCH (e:EVENT)
        RETURN e.label as label, 
               e.qid as qid,
               e.entity_cipher as cipher,
               e.date as date,
               e.subject as subject,
               e.start_date as start_date,
               keys(e) as all_properties
        ORDER BY e.label
    """)
    for record in result:
        print(f"  Label: {record['label']}")
        print(f"    QID: {record['qid']}")
        print(f"    Cipher: {record['cipher']}")
        print(f"    Date: {record['date']}")
        print(f"    Start date: {record['start_date']}")
        print(f"    Subject: {record['subject']}")
        print(f"    All properties: {record['all_properties']}")
        print()
    
    # Check a sample Event node to see what properties are expected
    print("\n3. Sample Event node properties:")
    result = session.run("""
        MATCH (e:Event)
        RETURN keys(e) as properties
        LIMIT 1
    """)
    for record in result:
        print(f"  Event properties: {record['properties']}")
    
    # Count how many EVENT nodes are missing start_date
    print("\n4. EVENT nodes missing start_date:")
    result = session.run("""
        MATCH (e:EVENT)
        WHERE e.start_date IS NULL
        RETURN count(e) as missing_count
    """)
    print(f"  Count: {result.single()['missing_count']}")
    
    # Check if any EVENT nodes have a 'date' property that could be used
    print("\n5. EVENT nodes with 'date' property:")
    result = session.run("""
        MATCH (e:EVENT)
        WHERE e.date IS NOT NULL
        RETURN count(e) as with_date, collect(e.date)[0..3] as sample_dates
    """)
    record = result.single()
    print(f"  Count: {record['with_date']}")
    print(f"  Sample dates: {record['sample_dates']}")

driver.close()
print("\n" + "="*70)
