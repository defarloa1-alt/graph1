#!/usr/bin/env python3
"""
Test Aura connection and database access.
Uses .env credentials. Run from project root.
"""
import sys
from pathlib import Path

# Load from .env
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "scripts"))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

def main():
    from neo4j import GraphDatabase

    print("=" * 60)
    print("AURA CONNECTION TEST")
    print("=" * 60)
    print(f"URI: {NEO4J_URI}")
    print(f"User: {NEO4J_USERNAME}")
    print()

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("Error: NEO4J_URI and NEO4J_PASSWORD required in .env")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Test 1: session() with no database (server default)
    print("Test 1: driver.session() [no database param]")
    try:
        with driver.session() as session:
            r = session.run("RETURN 1 AS n").single()
            print(f"  OK: {r['n']}")
    except Exception as e:
        print(f"  FAILED: {e}")

    # Test 2: session(database="neo4j")
    print("\nTest 2: driver.session(database='neo4j')")
    try:
        with driver.session(database="neo4j") as session:
            r = session.run("RETURN 1 AS n").single()
            print(f"  OK: {r['n']}")
    except Exception as e:
        print(f"  FAILED: {e}")

    # Test 3: SHOW DATABASES (runs on system)
    print("\nTest 3: SHOW DATABASES")
    try:
        with driver.session(database="system") as session:
            result = session.run("SHOW DATABASES")
            for rec in result:
                print(f"  {rec.get('name')}: default={rec.get('default')}")
    except Exception as e:
        print(f"  FAILED: {e}")

    driver.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)
