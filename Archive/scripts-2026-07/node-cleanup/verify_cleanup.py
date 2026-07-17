"""
Final verification of node type cleanup.
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
print("FINAL VERIFICATION - NODE TYPE CLEANUP")
print("="*70)

with driver.session() as session:
    print("\n1. Duplicate consolidation verification:")
    
    # Check PERSON
    result = session.run("MATCH (p:PERSON) RETURN count(p) as count")
    person_uppercase = result.single()['count']
    print(f"   PERSON (uppercase): {person_uppercase} {('[OK] REMOVED' if person_uppercase == 0 else '[ERROR] STILL EXISTS')}")
    
    # Check Person
    result = session.run("MATCH (p:Person) RETURN count(p) as count")
    person_count = result.single()['count']
    print(f"   Person (propercase): {person_count} {('[OK]' if person_count == 5632 else '[?]')}")
    
    # Check EVENT
    result = session.run("MATCH (e:EVENT) RETURN count(e) as count")
    event_uppercase = result.single()['count']
    print(f"   EVENT (uppercase): {event_uppercase} {('[OK] REMOVED' if event_uppercase == 0 else '[ERROR] STILL EXISTS')}")
    
    # Check Event
    result = session.run("MATCH (e:Event) RETURN count(e) as count")
    event_count = result.single()['count']
    print(f"   Event (propercase): {event_count} {('[OK]' if event_count == 77 else '[?]')}")
    
    print("\n2. ProposedEdge status:")
    result = session.run("MATCH (pe:ProposedEdge) RETURN count(pe) as count")
    proposed_edge_count = result.single()['count']
    print(f"   ProposedEdge nodes: {proposed_edge_count} {('[OK] KEPT' if proposed_edge_count == 5667 else '[ERROR] UNEXPECTED')}")
    
    print("\n3. Empty node types (Material and Object):")
    result = session.run("MATCH (m:Material) RETURN count(m) as count")
    material_count = result.single()['count']
    print(f"   Material: {material_count} {('[OK] KEPT EMPTY' if material_count == 0 else '[?]')}")
    
    result = session.run("MATCH (o:Object) RETURN count(o) as count")
    object_count = result.single()['count']
    print(f"   Object: {object_count} {('[OK] KEPT EMPTY' if object_count == 0 else '[?]')}")
    
    print("\n4. Remaining uppercase labels:")
    result = session.run("""
        CALL db.labels() YIELD label
        WHERE label =~ '[A-Z][A-Z].*'
        AND label <> 'SYS_RelationshipType'
        AND label <> 'SYS_NodeType'
        AND NOT label STARTS WITH 'SYS_'
        AND NOT label STARTS WITH 'SFA_'
        RETURN label
        ORDER BY label
    """)
    uppercase_labels = [record['label'] for record in result]
    if uppercase_labels:
        print(f"   Found {len(uppercase_labels)} uppercase labels:")
        for label in uppercase_labels:
            print(f"     - {label}")
    else:
        print("   None (excluding SYS_* and SFA_* prefixes) [OK]")
    
    print("\n5. Overall cleanup status:")
    all_good = (
        person_uppercase == 0 and
        person_count == 5632 and
        event_uppercase == 0 and
        event_count == 77 and
        proposed_edge_count == 5667 and
        material_count == 0 and
        object_count == 0
    )
    
    if all_good:
        print("   *** ALL CLEANUP TASKS COMPLETED SUCCESSFULLY ***")
    else:
        print("   [ERROR] Some tasks did not complete as expected")
        print(f"     Expected: PERSON=0, Person=5632, EVENT=0, Event=77, ProposedEdge=5667")
        print(f"     Actual: PERSON={person_uppercase}, Person={person_count}, EVENT={event_uppercase}, Event={event_count}, ProposedEdge={proposed_edge_count}")

driver.close()
print("\n" + "="*70)
