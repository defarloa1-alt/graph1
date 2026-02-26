#!/usr/bin/env python3
"""Verify SYS_Threshold and SYS_Policy counts after add_dmn_threshold_policy_nodes.cypher."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

def main():
    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set in .env")
        sys.exit(1)
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        r1 = session.run("MATCH (n:SYS_Threshold) RETURN count(n) AS c")
        tc = r1.single()["c"]
        r2 = session.run("MATCH (n:SYS_Policy) RETURN count(n) AS c")
        pc = r2.single()["c"]
    driver.close()
    print(f"SYS_Threshold: {tc} (expect 24: 21 new + 3 existing)")
    print(f"SYS_Policy: {pc} (expect 10: 5 new + 5 existing)")
    ok = tc == 24 and pc == 10
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
