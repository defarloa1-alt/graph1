"""
populate_member_of.py — Wire MEMBER_OF edges from Person/Place → SubjectConcept

Routing strategy:
  Person → SC  : POSITION_HELD edges only (NO occupation — time-boxed, unreliable)
  Place  → SC  : place_type CONTAINS patterns (Pleiades type taxonomy)

MEMBER_OF edge properties:
  source : 'position_held' | 'place_type' | 'dprr_default'
  rank   : 'primary' | 'inferred'

Person routing rules:
  - sc_constitution  : political magistracies (consul, praetor, quaestor, …)
  - sc_military      : military commands (tribunus militum, legatus lt., …)
  - sc_religion      : priesthoods (augur, pontifex, flamen, …)
  - sc_diplomacy     : diplomatic missions (legatus ambassador/envoy)
  - sc_economy       : monetalis (mint masters)
  - ALL in-domain DPRR  : sc_constitution default (rank='inferred')

Place routing rules (place_type CONTAINS, multiple SC per place allowed):
  - GEO_SETTLEMENTS       : settlement, villa, station, colony
  - GEO_HIST_PLACES       : temple, sanctuary, tomb, cemetery, fort, road, mine, …
  - GEO_HYDROGRAPHY       : river, lake, harbor, bay, spring, sea, …
  - GEO_PHYS_FEATURES     : mountain, island, cape, valley, hill, …
  - GEO_ADMIN_DIVISIONS   : region, province
  - GEO_POLITICAL_ENTITIES: people
  - GEO_GENERAL           : catch-all (unmatched + null place_type)
"""

import sys
import time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

BATCH = 500

# ── Person routing — POSITION_HELD label → SC id ─────────────────────────────
# Key: SC subject_id | Value: list of exact Position.label strings
PERSON_ROUTES = {
    "sc_constitution": [
        "consul", "praetor", "quaestor", "censor",
        "aedilis curulis", "aedilis plebis",
        "tribunus plebis", "dictator", "interrex",
        "princeps senatus", "senator - office unknown",
        "decemvir consulari imperio legibus scribundis",
        "tribunus militum consulari potestate",
        "repulsa (cos.)", "repulsa (cens.)",
    ],
    "sc_military": [
        "tribunus militum", "legatus (lieutenant)",
        "triumphator", "praefectus", "promagistrate",
        "proconsul", "propraetor", "magister equitum",
        "officer (title not preserved)",
    ],
    "sc_religion": [
        "augur", "pontifex", "pontifex maximus",
        "flamen Martialis", "decemvir sacris faciundis",
    ],
    "sc_diplomacy": [
        "legatus (ambassador)", "legatus (envoy)",
    ],
    "sc_economy": [
        "monetalis",
    ],
}

# ── Place routing — SC id → list of substrings to CONTAINS-match in place_type ─
PLACE_ROUTES = [
    ("GEO_SETTLEMENTS",        ["settlement", "villa", "station"]),
    ("GEO_HIST_PLACES",        ["temple", "sanctuary", "tomb", "cemetery",
                                 "monument", "amphitheatre", "theatre", "bath",
                                 "aqueduct", "tumulus", "church", "mine",
                                 "quarry", "bridge", "road", "fort",
                                 "archaeological"]),
    ("GEO_HYDROGRAPHY",        ["river", "lake", "harbor", "harbour",
                                 "bay", "spring", "sea", "estuary",
                                 "pool", "channel"]),
    ("GEO_PHYS_FEATURES",      ["mountain", "island", "cape", "valley",
                                 "hill", "plain", "forest", "promontory"]),
    ("GEO_ADMIN_DIVISIONS",    ["region", "province"]),
    ("GEO_POLITICAL_ENTITIES", ["people"]),
    # GEO_GENERAL is catch-all — handled separately
]

# ─────────────────────────────────────────────────────────────────────────────

def run_with_retry(session, query, params=None, retries=3):
    for i in range(retries):
        try:
            return session.run(query, params or {}).data()
        except Exception as e:
            if i == retries - 1:
                raise
            print(f"  Retry {i+1}: {e}")
            time.sleep(2)

def wire_person_position_routes(session):
    """Wire Person → SC based on POSITION_HELD label matches."""
    total = 0
    for sc_id, positions in PERSON_ROUTES.items():
        q = """
        MATCH (sc:SubjectConcept {subject_id: $sc_id})
        MATCH (p:Person)-[:POSITION_HELD]->(pos:Position)
        WHERE p.dprr_id IS NOT NULL
          AND pos.label IN $positions
        WITH DISTINCT p, sc
        MERGE (p)-[r:MEMBER_OF]->(sc)
        ON CREATE SET r.source = 'position_held', r.rank = 'primary'
        ON MATCH  SET r.source = 'position_held', r.rank = 'primary'
        RETURN count(r) AS n
        """
        result = run_with_retry(session, q, {"sc_id": sc_id, "positions": positions})
        n = result[0]["n"]
        print(f"  {sc_id}: {n} person→SC edges")
        total += n
    return total

def wire_person_default(session):
    """All in-domain DPRR persons → sc_constitution (dprr_default, inferred)."""
    q = """
    MATCH (sc:SubjectConcept {subject_id: 'sc_constitution'})
    MATCH (p:Person)
    WHERE p.dprr_id IS NOT NULL
      AND coalesce(p.in_domain, true) <> false
    MERGE (p)-[r:MEMBER_OF]->(sc)
    ON CREATE SET r.source = 'dprr_default', r.rank = 'inferred'
    // ON MATCH: leave existing (position_held rank='primary' wins)
    RETURN count(r) AS n
    """
    result = run_with_retry(session, q)
    n = result[0]["n"]
    print(f"  sc_constitution (default): {n} total person→SC edges")
    return n

def wire_places(session):
    """Wire Place → geo SC based on place_type CONTAINS patterns. Batched."""
    total = 0
    matched_ids = set()  # track which places got at least one SC

    for sc_id, substrings in PLACE_ROUTES:
        # Build WHERE clause — OR of CONTAINS per substring
        where_clauses = " OR ".join(
            f"p.place_type CONTAINS '{s}'" for s in substrings
        )
        q = f"""
        MATCH (sc:SubjectConcept {{subject_id: $sc_id}})
        MATCH (p:Place)
        WHERE p.place_type IS NOT NULL
          AND ({where_clauses})
        WITH DISTINCT p, sc
        MERGE (p)-[r:MEMBER_OF]->(sc)
        ON CREATE SET r.source = 'place_type', r.rank = 'primary'
        ON MATCH  SET r.source = 'place_type', r.rank = 'primary'
        RETURN count(r) AS n
        """
        result = run_with_retry(session, q, {"sc_id": sc_id})
        n = result[0]["n"]
        print(f"  {sc_id}: {n} place→SC edges")
        total += n

    # GEO_GENERAL: places with null place_type OR unmatched types (unlocated, unknown, etc.)
    # We identify "unmatched" as: no existing MEMBER_OF → any geo_bootstrap SC
    q_general = """
    MATCH (sc:SubjectConcept {subject_id: 'GEO_GENERAL'})
    MATCH (p:Place)
    WHERE NOT (p)-[:MEMBER_OF]->(:SubjectConcept)
    WITH DISTINCT p, sc
    MERGE (p)-[r:MEMBER_OF]->(sc)
    ON CREATE SET r.source = 'place_type_default', r.rank = 'inferred'
    RETURN count(r) AS n
    """
    result = run_with_retry(session, q_general)
    n = result[0]["n"]
    print(f"  GEO_GENERAL (catch-all): {n} place→SC edges")
    total += n
    return total

def verify(session):
    """Print per-SC member counts."""
    q = """
    MATCH (sc:SubjectConcept)<-[r:MEMBER_OF]-(e)
    RETURN sc.subject_id AS sc, sc.label AS label,
           count(r) AS members,
           sum(CASE WHEN 'Person' IN labels(e) THEN 1 ELSE 0 END) AS persons,
           sum(CASE WHEN 'Place'  IN labels(e) THEN 1 ELSE 0 END) AS places
    ORDER BY members DESC
    """
    rows = run_with_retry(session, q)
    print("\n── MEMBER_OF counts per SubjectConcept ────────────────────────────────")
    print(f"  {'SC':<35} {'members':>8} {'persons':>8} {'places':>8}")
    print("  " + "─" * 62)
    for r in rows:
        label = (r["label"] or r["sc"] or "")[:35]
        print(f"  {label:<35} {r['members']:>8} {r['persons']:>8} {r['places']:>8}")

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        print("\n── Pass 1: Person → SC via POSITION_HELD ──────────────────────────────")
        n1 = wire_person_position_routes(session)
        print(f"  Subtotal: {n1}")

        print("\n── Pass 2: Person → sc_constitution (dprr_default) ─────────────────")
        n2 = wire_person_default(session)

        print("\n── Pass 3: Place → Geo SCs via place_type ──────────────────────────────")
        n3 = wire_places(session)
        print(f"  Subtotal: {n3}")

        verify(session)

    driver.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
