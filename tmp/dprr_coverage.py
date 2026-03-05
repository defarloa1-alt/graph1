#!/usr/bin/env python3
"""Quick DPRR coverage census from graph."""
import sys
from pathlib import Path
_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "scripts"))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    sys.exit("config_loader required")
from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
db = NEO4J_DATABASE or "neo4j"
with driver.session(database=db) as s:
    r = s.run("MATCH (e:Entity) WHERE e.dprr_id IS NOT NULL RETURN count(e) AS c").single()
    print("Entities with dprr_id:", r["c"])
    r = s.run("MATCH (e:Entity) WHERE e.dprr_uri IS NOT NULL RETURN count(e) AS c").single()
    print("Entities with dprr_uri:", r["c"])
    r = s.run("MATCH (e:Entity) WHERE e.qid IS NOT NULL AND e.dprr_id IS NOT NULL RETURN count(e) AS c").single()
    print("Entities with both qid + dprr_id (Group A):", r["c"])
    r = s.run("MATCH (e:Entity) WHERE e.dprr_uri IS NOT NULL AND (e.qid IS NULL OR e.qid = '') RETURN count(e) AS c").single()
    print("Entities dprr_uri only, no qid (Group C):", r["c"])
    r = s.run("MATCH (p:Position) RETURN count(p) AS c").single()
    print("Position nodes (DPRR offices):", r["c"])
    r = s.run("MATCH ()-[r:POSITION_HELD]->() RETURN count(r) AS c").single()
    print("POSITION_HELD relationships:", r["c"])
driver.close()
