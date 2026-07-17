"""
Additional fix for EVENT nodes - add missing qid property.
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import uuid

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USERNAME', os.getenv('NEO4J_USER'))
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("="*70)
print("EVENT QID FIX")
print("="*70)

with driver.session() as session:
    # Check which EVENT nodes are missing qid
    print("\n1. EVENT nodes missing qid:")
    result = session.run("""
        MATCH (e:EVENT)
        WHERE e.qid IS NULL
        RETURN e.label as label, e.entity_cipher as cipher
    """)
    missing_qid = list(result)
    print(f"   Count: {len(missing_qid)}")
    for record in missing_qid:
        print(f"   - {record['label']} ({record['cipher']})")
    
    # Add placeholder qid based on entity_cipher or generate one
    print("\n2. Adding placeholder qid values:")
    result = session.run("""
        MATCH (e:EVENT)
        WHERE e.qid IS NULL
        SET e.qid = CASE 
            WHEN e.entity_cipher IS NOT NULL 
            THEN replace(e.entity_cipher, 'ent_evt_', 'Q_')
            ELSE 'Q_UNKNOWN_' + substring(toString(id(e)), 0, 8)
        END
        RETURN count(e) as fixed
    """)
    print(f"   Fixed: {result.single()['fixed']} nodes")
    
    print("\n3. Verification - All EVENT nodes now have required properties:")
    result = session.run("""
        MATCH (e:EVENT)
        RETURN 
            e.label as label,
            e.qid as qid,
            e.start_date as start_date,
            CASE WHEN e.qid IS NULL THEN 'MISSING QID' ELSE 'OK' END as qid_status,
            CASE WHEN e.start_date IS NULL THEN 'MISSING START_DATE' ELSE 'OK' END as date_status
        ORDER BY e.label
    """)
    all_good = True
    for record in result:
        status = "OK" if record['qid'] and record['start_date'] else "ERROR"
        if status == "ERROR":
            all_good = False
        print(f"   {record['label']}: qid={record['qid']}, start_date={record['start_date']} [{status}]")
    
    if all_good:
        print("\n" + "="*70)
        print("SUCCESS: All EVENT nodes ready for consolidation")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("WARNING: Some EVENT nodes still have missing properties")
        print("="*70)

driver.close()
