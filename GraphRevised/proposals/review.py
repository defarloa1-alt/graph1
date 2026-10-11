"""Curator review CLI for stored Proposals.

    python -m GraphRevised.proposals.review list [--status submitted]
    python -m GraphRevised.proposals.review accept <proposal-id> --by <name> --basis "<reason>"
    python -m GraphRevised.proposals.review reject <proposal-id> --by <name> --basis "<reason>"

Reads NEO4J_PASSWORD (and optional NEO4J_URI, NEO4J_USERNAME, NEO4J_DATABASE)
from the environment. Each decision runs in one transaction.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations

from .registry import load_registry
from .store import ReviewError, accept, list_proposals, reject


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--status")
    for name in ("accept", "reject"):
        decision = commands.add_parser(name)
        decision.add_argument("proposal_id")
        decision.add_argument("--by", required=True)
        decision.add_argument("--basis", required=True)
    args = parser.parse_args(argv)

    if not os.environ.get("NEO4J_PASSWORD"):
        parser.error("NEO4J_PASSWORD is not set")
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            if args.command == "list":
                rows = session.execute_read(list_proposals, args.status)
                for row in rows:
                    print(f"{row['status']:<11} {row['id']}\n            {row['assertion']}")
                print(f"{len(rows)} proposal(s)")
                return 0

            operations = load_operations()
            decision = {
                "decided_by": args.by,
                "decision_basis": args.basis,
                "decided_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            if args.command == "accept":
                registry = load_registry()
                result = session.execute_write(
                    lambda tx: accept(tx, args.proposal_id, registry=registry, operations=operations, **decision)
                )
            else:
                result = session.execute_write(
                    lambda tx: reject(tx, args.proposal_id, operations=operations, **decision)
                )
            print(f"{result['proposal']['status']}: {result['assertion']['label']}")
            return 0
    except ReviewError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
