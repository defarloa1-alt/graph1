#!/usr/bin/env python3
"""
Test Neo4j Connection
Quick script to verify Neo4j is running and accessible
"""
import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_connection(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """Test Neo4j connection."""
    print("="*80)
    print("TESTING NEO4J CONNECTION")
    print("="*80)
    print(f"URI: {uri}")
    print(f"User: {user}")
    print()
    
    try:
        print("Attempting connection...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful!' as message")
            record = result.single()
            print(f"[OK] {record['message']}")
            
            # Get database stats
            result = session.run("""
                MATCH (n)
                RETURN count(n) as total_nodes
            """)
            total = result.single()['total_nodes']
            print(f"[OK] Total nodes in database: {total}")
        
        driver.close()
        print()
        print("="*80)
        print("[SUCCESS] NEO4J IS RUNNING")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"[FAILED] CONNECTION FAILED: {e}")
        print()
        print("="*80)
        print("[WARNING] TROUBLESHOOTING")
        print("="*80)
        print("1. Is Neo4j Desktop running?")
        print("2. Is the database started?")
        print("3. Is it listening on bolt://localhost:7687?")
        print("4. Is the password correct? (default: Chrystallum)")
        print()
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test Neo4j connection')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j URI')
    parser.add_argument('--user', default='neo4j', help='Neo4j username')
    parser.add_argument('--password', default='Chrystallum', help='Neo4j password')
    
    args = parser.parse_args()
    success = test_connection(args.uri, args.user, args.password)
    sys.exit(0 if success else 1)

