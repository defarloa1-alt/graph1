"""
Biographic Subject Agent — CLI entry point

Usage:
    python -m scripts.agents.biographic --dprr 1976
    python -m scripts.agents.biographic --all
    python -m scripts.agents.biographic --all --dry
"""

import argparse
import time

from .agent import harvest_person, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, SLEEP_SEC
from .decision_loader import load_decision_model
from neo4j import GraphDatabase


def main():
    parser = argparse.ArgumentParser(
        description="Biographic Subject Agent — harvest biographical context for Person nodes"
    )
    parser.add_argument("--dprr", help="Single DPRR ID (PoC mode)")
    parser.add_argument("--all",  action="store_true", help="All persons with QIDs")
    parser.add_argument("--dry",  action="store_true", help="Dry run — no writes")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        if args.dprr:
            records = session.run(
                "MATCH (p:Person {dprr_id: $dprr}) WHERE p.qid IS NOT NULL "
                "RETURN p.qid AS qid, p.dprr_id AS dprr_id",
                dprr=str(args.dprr)
            ).data()
        elif args.all:
            records = session.run(
                "MATCH (p:Person) WHERE p.qid IS NOT NULL "
                "RETURN p.qid AS qid, p.dprr_id AS dprr_id"
            ).data()
        else:
            parser.print_help()
            driver.close()
            return

    print(f"Persons to harvest: {len(records)}")
    if not args.dry:
        confirm = input("Proceed with writes? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            driver.close()
            return

    with driver.session() as session:
        decision_model = None
        try:
            decision_model = load_decision_model(session)
            if decision_model and decision_model._backlink:
                print("  Using graph decision model (BacklinkRouting)")
        except Exception:
            print("  Using hardcoded backlink map (run migration_bio_decision_model.cypher for graph-based routing)")

        for i, r in enumerate(records):
            try:
                harvest_person(
                    r["qid"],
                    r["dprr_id"] or "?",
                    session,
                    dry_run=args.dry,
                    decision_model=decision_model,
                )
            except Exception as e:
                print(f"  ERROR on {r['qid']}: {e}")
            if i < len(records) - 1:
                time.sleep(SLEEP_SEC)

    print(f"\nDone. Harvested {len(records)} persons.")
    driver.close()


if __name__ == "__main__":
    main()
