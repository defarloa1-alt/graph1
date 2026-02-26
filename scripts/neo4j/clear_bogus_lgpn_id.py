#!/usr/bin/env python3
"""Clear bogus lgpn_id values (D-023). P1838 = PSS-archi, not LGPN."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

QUERY = """
MATCH (e:Entity)
WHERE e.lgpn_id IS NOT NULL AND e.lgpn_id =~ '^[A-Z]{2}-\\d+-\\d+$'
REMOVE e.lgpn_id
RETURN count(e) AS cleared
"""

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as s:
        r = s.run(QUERY)
        row = r.single()
        cleared = row["cleared"] if row else 0
    driver.close()
    print(f"Cleared {cleared} bogus lgpn_id values (PSS-archi format)")

if __name__ == "__main__":
    main()
