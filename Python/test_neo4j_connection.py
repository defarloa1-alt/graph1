#!/usr/bin/env python3
"""
Quick Neo4j connection test
"""

import sys
import io
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("="*80)
print("NEO4J CONNECTION TEST")
print("="*80)

try:
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))
    
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        record = result.single()
        
        if record and record['test'] == 1:
            print("\n✅ CONNECTION SUCCESS!")
            print("   Neo4j is running and accepting connections")
            
            # Get database info
            result = session.run("""
                CALL dbms.components() YIELD name, versions, edition
                RETURN name, versions[0] as version, edition
            """)
            for r in result:
                print(f"\n   Database: {r['name']}")
                print(f"   Version:  {r['version']}")
                print(f"   Edition:  {r['edition']}")
            
            # Get node counts
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            
            print("\n   Node Counts:")
            total = 0
            for r in result:
                label = r['label'] or '(no label)'
                count = r['count']
                total += count
                print(f"     {label}: {count:,}")
            
            print(f"\n   Total Nodes: {total:,}")
    
    driver.close()

except Exception as e:
    print("\n❌ CONNECTION FAILED!")
    print(f"   Error: {e}")
    print("\n   Possible causes:")
    print("   - Neo4j Desktop is not running")
    print("   - Database is not started")
    print("   - Wrong credentials")
    print("   - Port 7687 is blocked")

print("\n" + "="*80)

