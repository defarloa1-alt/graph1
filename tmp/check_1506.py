"""Check offices for entity 1506."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
with driver.session(database=NEO4J_DATABASE or "neo4j") as s:
    r = s.run("""
        MATCH (e:Entity {dprr_id: '1506'})-[r:POSITION_HELD]->(p:Position)
        RETURN e.label, p.label AS pos, p.label_name AS name, r.year_start AS year_start
    """)
    for rec in r:
        print(rec)
driver.close()
