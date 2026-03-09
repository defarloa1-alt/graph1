"""
populate_member_of.py — Wire MEMBER_OF edges from Person/Place → SubjectConcept

Routing rules are loaded from SYS_RoutingRule nodes in the graph (script 18j).
No routing logic is hardcoded here — add/change rules in the graph, re-run.

MEMBER_OF edge properties (wire-complete — all set at creation time):
  source         : 'position_held' | 'place_type' | 'place_type_default' | 'dprr_default'
  rank           : 'primary' | 'inferred'
  earliest_year  : min year from POSITION_HELD year_start, or Place min_date
  latest_year    : max year from POSITION_HELD year_end, or Place max_date
  position_count : count of matching POSITION_HELD edges (person routes only)
"""

import sys
import time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase
from packages.domain.routing_rules import load_rules, summarise


def run_with_retry(session, query, params=None, retries=3):
    for i in range(retries):
        try:
            return session.run(query, params or {}).data()
        except Exception as e:
            if i == retries - 1:
                raise
            print(f"  Retry {i+1}: {e}")
            time.sleep(2)


# ── Wiring functions ──────────────────────────────────────────────────────────

def wire_person_position_routes(session, person_routes):
    """Wire Person → SC based on POSITION_HELD label matches.

    Temporal bounds (earliest_year, latest_year, position_count) are computed
    inline from the matched POSITION_HELD edges — no post-pass needed.
    OPTIONAL MATCH on dated positions means undated persons still get wired
    (bounds null — honest, not silently dropped).
    """
    total = 0
    for sc_id, positions in person_routes.items():
        q = """
        MATCH (sc:SubjectConcept {subject_id: $sc_id})
        MATCH (p:Person)-[:POSITION_HELD]->(pos:Position)
        WHERE p.dprr_id IS NOT NULL
          AND pos.label IN $positions
        WITH p, sc
        OPTIONAL MATCH (p)-[ph:POSITION_HELD]->(pos2:Position)
        WHERE pos2.label IN $positions
          AND ph.year_start IS NOT NULL
        WITH p, sc,
             min(ph.year_start) AS ey,
             max(ph.year_end)   AS ly,
             count(ph)          AS pc
        MERGE (p)-[r:MEMBER_OF]->(sc)
        ON CREATE SET r.source         = 'position_held',
                      r.rank           = 'primary',
                      r.earliest_year  = ey,
                      r.latest_year    = ly,
                      r.position_count = pc
        ON MATCH  SET r.source         = 'position_held',
                      r.rank           = 'primary',
                      r.earliest_year  = ey,
                      r.latest_year    = ly,
                      r.position_count = pc
        RETURN count(r) AS n
        """
        result = run_with_retry(session, q, {"sc_id": sc_id, "positions": positions})
        n = result[0]["n"]
        print(f"  {sc_id}: {n} person→SC edges")
        total += n
    return total


def wire_person_default(session, domain="roman_republic"):
    """All in-domain persons → domain_default SC (rank='inferred').

    Target SC is read from SYS_RoutingRule {match_mode:'domain_default'} —
    not hardcoded. ON MATCH leaves position_held edges intact (primary wins).
    """
    q = """
    MATCH (rule:SYS_RoutingRule {domain: $domain, match_mode: 'domain_default'})
    MATCH (sc:SubjectConcept {subject_id: rule.sc_id})
    MATCH (p:Person)
    WHERE p.dprr_id IS NOT NULL
      AND coalesce(p.in_domain, true) <> false
    MERGE (p)-[r:MEMBER_OF]->(sc)
    ON CREATE SET r.source = 'dprr_default', r.rank = rule.rank
    // ON MATCH: leave existing (position_held rank='primary' wins)
    RETURN sc.subject_id AS sc_id, count(r) AS n
    """
    result = run_with_retry(session, q, {"domain": domain})
    n = result[0]["n"]
    sc_id = result[0]["sc_id"]
    print(f"  {sc_id} (domain_default): {n} total person→SC edges")
    return n


def wire_places(session, place_routes, catch_all_sc):
    """Wire Place → geo SC based on place_type CONTAINS patterns.

    Pleiades min_date / max_date propagated inline as earliest_year / latest_year.
    """
    total = 0

    for sc_id, substrings in place_routes:
        where_clauses = " OR ".join(
            f"p.place_type CONTAINS '{s}'" for s in substrings
        )
        q = f"""
        MATCH (sc:SubjectConcept {{subject_id: $sc_id}})
        MATCH (p:Place)
        WHERE p.place_type IS NOT NULL
          AND ({where_clauses})
        WITH p, sc
        MERGE (p)-[r:MEMBER_OF]->(sc)
        ON CREATE SET r.source        = 'place_type',
                      r.rank          = 'primary',
                      r.earliest_year = p.min_date,
                      r.latest_year   = p.max_date
        ON MATCH  SET r.source        = 'place_type',
                      r.rank          = 'primary',
                      r.earliest_year = p.min_date,
                      r.latest_year   = p.max_date
        RETURN count(r) AS n
        """
        result = run_with_retry(session, q, {"sc_id": sc_id})
        n = result[0]["n"]
        print(f"  {sc_id}: {n} place→SC edges")
        total += n

    if catch_all_sc:
        q_general = """
        MATCH (sc:SubjectConcept {subject_id: $sc_id})
        MATCH (p:Place)
        WHERE NOT (p)-[:MEMBER_OF]->(:SubjectConcept)
        WITH p, sc
        MERGE (p)-[r:MEMBER_OF]->(sc)
        ON CREATE SET r.source        = 'place_type_default',
                      r.rank          = 'inferred',
                      r.earliest_year = p.min_date,
                      r.latest_year   = p.max_date
        ON MATCH  SET r.earliest_year = p.min_date,
                      r.latest_year   = p.max_date
        RETURN count(r) AS n
        """
        result = run_with_retry(session, q_general, {"sc_id": catch_all_sc})
        n = result[0]["n"]
        print(f"  {catch_all_sc} (catch-all): {n} place→SC edges")
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

        print("\n── Loading routing rules from graph ────────────────────────────────────")
        person_routes, place_routes, catch_all_sc = load_rules(session)
        print(f"  {summarise(person_routes, place_routes, catch_all_sc)}")

        print("\n── Pass 1: Person → SC via POSITION_HELD ──────────────────────────────")
        n1 = wire_person_position_routes(session, person_routes)
        print(f"  Subtotal: {n1}")

        print("\n── Pass 2: Person → sc_constitution (dprr_default) ─────────────────")
        n2 = wire_person_default(session)

        print("\n── Pass 3: Place → Geo SCs via place_type ──────────────────────────────")
        n3 = wire_places(session, place_routes, catch_all_sc)
        print(f"  Subtotal: {n3}")

        verify(session)

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
