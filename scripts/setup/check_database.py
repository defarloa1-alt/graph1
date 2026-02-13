#!/usr/bin/env python3
"""
Quick Database Status Check
Shows what's currently in Neo4j
"""
import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_status(password="Chrystallum"):
    """Check database status."""
    print("="*80)
    print("DATABASE STATUS")
    print("="*80)
    
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))
    
    with driver.session() as session:
        # Node counts by label
        print("\n[NODE COUNTS]")
        result = session.run("""
            CALL db.labels() YIELD label
            CALL {
                WITH label
                MATCH (n)
                WHERE label IN labels(n)
                RETURN count(n) as count
            }
            RETURN label, count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  {record['label']:20s}: {record['count']:,}")
        
        # Relationship counts by type
        print("\n[RELATIONSHIP COUNTS]")
        result = session.run("""
            CALL db.relationshipTypes() YIELD relationshipType
            CALL {
                WITH relationshipType
                MATCH ()-[r]->()
                WHERE type(r) = relationshipType
                RETURN count(r) as count
            }
            RETURN relationshipType, count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  {record['relationshipType']:25s}: {record['count']:,}")
        
        # Sample periods with LCSH
        print("\n[SAMPLE PERIODS WITH LCSH]")
        result = session.run("""
            MATCH (p:Period)-[:SUBJECT_OF]->(s:Subject)
            RETURN p.label as period, p.start_date as start, p.end_date as end, 
                   s.lcsh_id as lcsh, s.dewey_decimal as dewey
            ORDER BY p.start_date
            LIMIT 5
        """)
        for record in result:
            dewey = record['dewey'] or 'N/A'
            print(f"  {record['period']:30s} | LCSH: {record['lcsh']} | Dewey: {dewey}")
    
    driver.close()
    print("\n" + "="*80)

if __name__ == "__main__":
    check_status()

