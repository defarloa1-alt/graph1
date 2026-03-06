#!/usr/bin/env python3
"""Check biographic harvest state in graph. Run after harvest to verify writes.

Progress mode (--progress): shows done/total, %, and rough ETA if elapsed_hours given.
"""
import argparse
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase


def main() -> int:
    ap = argparse.ArgumentParser(description="Biographic harvest graph check")
    ap.add_argument("--progress", "-p", action="store_true", help="Show progress (done/total, %%, ETA)")
    ap.add_argument("--elapsed", type=float, default=None, help="Hours elapsed (for ETA estimate)")
    args = ap.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required (.env)")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    with driver.session(database=db) as session:
        # Persons with bio harvested
        bio_harvested = session.run(
            "MATCH (p:Person) WHERE p.bio_harvested_at IS NOT NULL RETURN count(p) AS c"
        ).single()["c"]

        # Total to harvest (same query as --all)
        total_to_harvest = session.run(
            "MATCH (p:Person) WHERE p.qid IS NOT NULL AND p.dprr_id IS NOT NULL RETURN count(p) AS c"
        ).single()["c"]

        # Recent (last 25 by harvested_at - approximate)
        recent = session.run("""
            MATCH (p:Person) WHERE p.bio_harvested_at IS NOT NULL
            RETURN p.qid AS qid, p.dprr_id AS dprr_id, p.bio_harvested_at AS at
            ORDER BY p.bio_harvested_at DESC
            LIMIT 25
        """).data()

        # Events
        events = session.run("MATCH (e:Event) RETURN count(e) AS c").single()["c"]
        participated_in = session.run(
            "MATCH ()-[r:PARTICIPATED_IN]->() RETURN count(r) AS c"
        ).single()["c"]

        # Marriages
        spouse_of = session.run(
            "MATCH ()-[r:SPOUSE_OF]->() WHERE r.source = 'wikidata_p26_qualifiers' RETURN count(r) AS c"
        ).single()["c"]

        # Backlinks
        bio_candidates = session.run(
            "MATCH ()-[r:BIO_CANDIDATE_REL]->() RETURN count(r) AS c"
        ).single()["c"]

        # Places (from harvest)
        places = session.run("MATCH (pl:Place) RETURN count(pl) AS c").single()["c"]
        born_in = session.run(
            "MATCH (:Person)-[r:BORN_IN_PLACE]->() RETURN count(r) AS c"
        ).single()["c"]
        died_in = session.run(
            "MATCH (:Person)-[r:DIED_IN_PLACE]->() RETURN count(r) AS c"
        ).single()["c"]

        # Years
        born_in_year = session.run(
            "MATCH (:Person)-[:BORN_IN_YEAR]->(:Year) RETURN count(*) AS c"
        ).single()["c"]
        died_in_year = session.run(
            "MATCH (:Person)-[:DIED_IN_YEAR]->(:Year) RETURN count(*) AS c"
        ).single()["c"]

    driver.close()

    if args.progress:
        remaining = total_to_harvest - bio_harvested
        pct = 100 * bio_harvested / total_to_harvest if total_to_harvest else 0
        print("Biographic Harvest — Progress")
        print("=" * 50)
        print(f"Done:      {bio_harvested:,} / {total_to_harvest:,}")
        print(f"Remaining: {remaining:,}")
        print(f"Progress:  {pct:.1f}%")
        if args.elapsed and bio_harvested > 0:
            rate = bio_harvested / args.elapsed
            eta_hours = remaining / rate if rate else 0
            print(f"Rate:      ~{rate:.0f} persons/hour (last {args.elapsed}h)")
            print(f"ETA:       ~{eta_hours:.1f} hours remaining")
        return 0

    print("Biographic Harvest — Graph Check")
    print("=" * 50)
    print(f"Persons with bio_harvested_at:  {bio_harvested:,}")
    print(f"Events:                         {events:,}")
    print(f"PARTICIPATED_IN edges:           {participated_in:,}")
    print(f"SPOUSE_OF (wikidata qualifiers): {spouse_of:,}")
    print(f"BIO_CANDIDATE_REL (backlinks):   {bio_candidates:,}")
    print(f"Places:                         {places:,}")
    print(f"BORN_IN_PLACE edges:            {born_in:,}")
    print(f"DIED_IN_PLACE edges:            {died_in:,}")
    print(f"BORN_IN_YEAR edges:             {born_in_year:,}")
    print(f"DIED_IN_YEAR edges:             {died_in_year:,}")
    print()
    print("Most recent 25 harvested:")
    for r in recent:
        print(f"  {r['qid']}  dprr:{r['dprr_id']}  {r['at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
