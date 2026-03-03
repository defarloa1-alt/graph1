#!/usr/bin/env python3
"""Run StatusType diagnostic query against Neo4j."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

from neo4j import GraphDatabase

QUERY = """
MATCH (n:StatusType)
RETURN n.label, n.label_latin, n.dprr_status_id, n.description,
       count { (n)<-[:HAS_STATUS]-() } AS usage
ORDER BY usage DESC
"""

def main():
    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD required (set in .env)", file=sys.stderr)
        return 1
    driver = GraphDatabase.driver(
        NEO4J_URI or "bolt://localhost:7687",
        auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD),
    )
    with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
        result = session.run(QUERY)
        rows = result.data()
    driver.close()
    if not rows:
        print("No StatusType nodes found.")
        return 0
    print(f"{'label':<12} {'label_latin':<12} {'dprr_id':<8} {'usage':<6} description")
    print("-" * 80)
    for r in rows:
        label = r.get("n.label", "")
        latin = r.get("n.label_latin", "")
        did = r.get("n.dprr_status_id", "")
        usage = r.get("usage", 0)
        desc = (r.get("n.description") or "")[:40]
        print(f"{str(label):<12} {str(latin):<12} {str(did):<8} {usage:<6} {desc}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
