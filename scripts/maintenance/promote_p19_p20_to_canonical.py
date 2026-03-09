#!/usr/bin/env python3
"""
Phase 4: Promote P19/P20 (place of birth/death) to canonical BORN_IN/DIED_IN.

For each (person)-[:P19|WIKIDATA_P19]->(place_stub), resolves the stub QID
to a canonical Place node with Pleiades backing before creating BORN_IN.
Same for P20 → DIED_IN.

Resolution order (via QIDResolver):
  1. Place already has pleiades_id in graph → use it directly
  2. Wikidata P1566 (Pleiades ID) on the stub QID → find canonical Place
  3. Wikidata P131 (located in) + P1566 → parent place with Pleiades
  4. Unresolved → skip edge, flag Place with needs_resolution=True

Retains P-code edges as provenance per ADR-007 §6.

Usage:
  python scripts/maintenance/promote_p19_p20_to_canonical.py           # dry-run
  python scripts/maintenance/promote_p19_p20_to_canonical.py --execute
"""
import argparse
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
sys.stdout.reconfigure(encoding="utf-8")
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase
from scripts.federation.qid_resolver import QIDResolver


def _fetch_pending(session, p_code: str) -> list[dict]:
    """Return (person_entity_id, place_qid) pairs needing promotion."""
    rel = "P19" if p_code == "P19" else "P20"
    canonical = "BORN_IN" if p_code == "P19" else "DIED_IN"
    rows = session.run(f"""
        MATCH (p:Entity)-[:{rel}|WIKIDATA_{rel}]->(t:Entity)
        WHERE NOT (p)-[:{canonical}]->()
          AND t.qid IS NOT NULL
        RETURN DISTINCT p.entity_id AS person_id, t.qid AS place_qid
    """).data()
    return rows


def _flag_unresolved(session, place_qid: str) -> None:
    session.run(
        "MATCH (pl:Place {qid: $qid}) SET pl.needs_resolution = true",
        {"qid": place_qid},
    )


def _merge_edge(session, person_id: str, canonical_qid: str,
                edge_type: str, method: str) -> None:
    session.run(f"""
        MATCH (p:Entity {{entity_id: $person_id}})
        MATCH (pl:Place {{qid: $place_qid}})
        MERGE (p)-[r:{edge_type}]->(pl)
        ON CREATE SET r.source = $method, r.created_at = date()
        ON MATCH  SET r.source = $method
    """, {"person_id": person_id, "place_qid": canonical_qid, "method": method})


def promote(session, p_code: str, dry_run: bool, resolver: QIDResolver) -> dict:
    edge_type = "BORN_IN" if p_code == "P19" else "DIED_IN"
    pending = _fetch_pending(session, p_code)
    print(f"\n── {p_code} → {edge_type}: {len(pending)} pending ──")

    counts = {"graph_direct": 0, "wikidata_p1566": 0, "wikidata_p131": 0,
              "wikidata_p1566_no_node": 0, "unresolved": 0, "skipped_dry_run": 0}

    for row in pending:
        person_id  = row["person_id"]
        place_qid  = row["place_qid"]
        canonical, pleiades_id, method = resolver.resolve(place_qid)

        if dry_run:
            counts["skipped_dry_run"] += 1
            continue

        if pleiades_id:
            _merge_edge(session, person_id, canonical, edge_type, method)
            counts[method] = counts.get(method, 0) + 1
        else:
            _flag_unresolved(session, place_qid)
            counts["unresolved"] += 1
            print(f"  SKIP {person_id} → {place_qid} (unresolved)")

    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote P19/P20 to BORN_IN/DIED_IN")
    ap.add_argument("--execute", action="store_true",
                    help="Write to graph (default: dry-run)")
    args = ap.parse_args()

    uri      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user     = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    db       = os.getenv("NEO4J_DATABASE", "neo4j")
    if not password:
        print("NEO4J_PASSWORD required")
        return 1

    dry_run = not args.execute
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=db) as session:
        resolver = QIDResolver(session)
        for p_code in ("P19", "P20"):
            counts = promote(session, p_code, dry_run, resolver)
            print(f"  Results: {counts}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
