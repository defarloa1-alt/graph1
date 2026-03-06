#!/usr/bin/env python3
"""Quick check of bio harvest results."""
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")
if not password:
    print("NEO4J_PASSWORD required")
    sys.exit(1)

driver = GraphDatabase.driver(uri, auth=(user, password))
with driver.session() as s:
    # Bio-harvested persons (have bio_harvested_at)
    harvested = s.run("""
        MATCH (p:Person) WHERE p.bio_harvested_at IS NOT NULL
        RETURN p.qid AS qid, p.dprr_id AS dprr_id, p.birth_year AS by, p.death_year AS dy,
               p.birth_place_qid AS bp, p.death_place_qid AS dp, p.bio_harvested_at AS at
        ORDER BY p.bio_harvested_at DESC
        LIMIT 15
    """).data()
    print("Bio-harvested persons (recent):")
    print("-" * 80)
    for r in harvested:
        print(f"  {r['qid']} dprr:{r['dprr_id']}  birth:{r['by']} death:{r['dy']}  "
              f"b_place:{r['bp'] or '-'}  d_place:{r['dp'] or '-'}")

    # Counts
    n_harvested = s.run("MATCH (p:Person) WHERE p.bio_harvested_at IS NOT NULL RETURN count(p) AS c").single()["c"]
    n_born = s.run("MATCH (p:Person)-[:BORN_IN_YEAR]->() RETURN count(p) AS c").single()["c"]
    n_died = s.run("MATCH (p:Person)-[:DIED_IN_YEAR]->() RETURN count(p) AS c").single()["c"]
    n_born_place = s.run("MATCH (p:Person)-[:BORN_IN_PLACE]->() RETURN count(p) AS c").single()["c"]
    n_died_place = s.run("MATCH (p:Person)-[:DIED_IN_PLACE]->() RETURN count(p) AS c").single()["c"]
    n_spouse = s.run("MATCH ()-[r:SPOUSE_OF]->() WHERE r.enriched_at IS NOT NULL RETURN count(r) AS c").single()["c"]

    print()
    print("Counts:")
    print(f"  Persons with bio_harvested_at: {n_harvested}")
    print(f"  BORN_IN_YEAR edges:            {n_born}")
    print(f"  DIED_IN_YEAR edges:            {n_died}")
    print(f"  BORN_IN_PLACE edges:           {n_born_place}")
    print(f"  DIED_IN_PLACE edges:           {n_died_place}")
    print(f"  SPOUSE_OF with enriched_at:    {n_spouse}")

driver.close()
