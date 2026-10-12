"""Curator review CLI for stored Proposals.

    python -m GraphRevised.proposals.review list [--status submitted]
    python -m GraphRevised.proposals.review accept <proposal-id> --by <name> --basis "<reason>"
    python -m GraphRevised.proposals.review reject <proposal-id> --by <name> --basis "<reason>" --reason <code> [--claim]
    python -m GraphRevised.proposals.review reopen <assertion-id> --by <name> --basis "<reason>"
    python -m GraphRevised.proposals.review supersede <assertion-id> --replacement <assertion-id> [...]
        --by <name> --basis "<reason>" --reason <code>
    python -m GraphRevised.proposals.review retract <assertion-id> --by <name> --basis "<reason>" --reason <code>
    python -m GraphRevised.proposals.review promote <attributed-assertion-id> [...] --by <name> --basis "<reason>"

`reject` rejects a Proposal's evidence and leaves its claim open for better
evidence; `reject --claim` also rejects the claim itself. `reopen` returns a
rejected claim to `proposed` so new evidence can be proposed. `supersede`
replaces a proposed or accepted claim with more precise claims, linked by
SUPERSEDED_BY. `retract` rejects an accepted claim found to be wrong, keeping
its evidence as audit history. `promote` makes accepted "according to"
claims Chrystallum's own asserted claim, citing their evidence; the basis
names the corroboration. Reason codes: false, unsupported, malformed, underspecified,
superseded-by-model.

Reads NEO4J_PASSWORD (and optional NEO4J_URI, NEO4J_USERNAME, NEO4J_DATABASE)
from the environment. Each decision runs in one transaction.
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations

from .registry import load_registry
from .store import REASON_CODES, ReviewError, accept, list_proposals, promote, reject, reopen, retract, supersede


def mark_quotation(passage: str, quotation: str | None) -> str:
    """The full passage with the quoted span bracketed as [[...]]."""
    if quotation and quotation in passage:
        return passage.replace(quotation, f"[[{quotation}]]", 1)
    return passage


def undated(row: dict, registry) -> bool:
    """The claim's predicate expects a time and the source gave none."""
    definition = registry.get(row.get("predicate") or "")
    if definition is None or row.get("time"):
        return False
    expected = definition.qualifiers.time
    return expected == "required" or (expected == "withRole" and row.get("hasRole"))


def print_proposals(rows: list[dict], registry=None) -> None:
    for row in rows:
        print(f"{row['status']:<11} {row['operation']:<11} {row['id']}\n            {row['assertion']}")
        if registry is not None and undated(row, registry):
            print("            UNDATED: the predicate expects a time the source did not give")
        for evidence in row["evidence"]:
            print(f"            + {evidence['observation']}")
            if evidence["locator"]:
                print(f"              {evidence['locator']}")
            if evidence["quotation"]:
                print(f"              quotation: \"{evidence['quotation']}\"")
            if evidence["passage"]:
                print(textwrap.fill(
                    mark_quotation(evidence["passage"], evidence["quotation"]),
                    width=100, initial_indent="              | ", subsequent_indent="              | ",
                ))
        for doubt in row["ambiguities"] or []:
            print(textwrap.fill(f"UNCERTAIN: {doubt}", width=100,
                                initial_indent="              ", subsequent_indent="              "))
        if row["rationale"]:
            print(textwrap.fill(f"rationale: {row['rationale']}", width=100,
                                initial_indent="              ", subsequent_indent="              "))
        print()
    print(f"{len(rows)} proposal(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--status")
    for name, target in (
        ("accept", "proposal_id"), ("reject", "proposal_id"), ("reopen", "assertion_id"),
        ("supersede", "assertion_id"), ("retract", "assertion_id"), ("promote", "assertion_ids"),
    ):
        decision = commands.add_parser(name)
        decision.add_argument(target, nargs="+" if name == "promote" else None)
        decision.add_argument("--by", required=True)
        decision.add_argument("--basis", required=True)
        if name in ("reject", "supersede", "retract"):
            decision.add_argument("--reason", required=True, choices=REASON_CODES)
        if name == "reject":
            decision.add_argument("--claim", action="store_true", help="also reject the claim itself")
        if name == "supersede":
            decision.add_argument("--replacement", action="append", required=True, dest="replacements",
                                  help="a claim that replaces it (repeat for several)")
    args = parser.parse_args(argv)

    if not os.environ.get("NEO4J_PASSWORD"):
        parser.error("NEO4J_PASSWORD is not set")
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            if args.command == "list":
                print_proposals(session.execute_read(list_proposals, args.status), load_registry())
                return 0

            operations = load_operations()
            decision = {
                "decided_by": args.by,
                "decision_basis": args.basis,
                "decided_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            if args.command == "reopen":
                result = session.execute_write(
                    lambda tx: reopen(tx, args.assertion_id, operations=operations, **decision)
                )
                print(f"reopened: {result['assertion']['label']} ({result['assertion']['status']})")
                return 0
            if args.command == "promote":
                registry = load_registry()
                result = session.execute_write(lambda tx: promote(
                    tx, args.assertion_ids, registry=registry, operations=operations, **decision
                ))
                print(f"promoted: {result['assertion']['label']} (from {', '.join(result['sourceIds'])})")
                return 0
            if args.command == "retract":
                result = session.execute_write(lambda tx: retract(
                    tx, args.assertion_id, reason=args.reason, operations=operations, **decision
                ))
                print(f"retracted: {result['assertion']['label']} ({result['assertion']['status']})")
                return 0
            if args.command == "supersede":
                result = session.execute_write(lambda tx: supersede(
                    tx, args.assertion_id, args.replacements, reason=args.reason, operations=operations, **decision
                ))
                print(f"superseded: {result['assertion']['label']} -> {', '.join(result['replacementIds'])}")
                return 0
            if args.command == "accept":
                registry = load_registry()
                result = session.execute_write(
                    lambda tx: accept(tx, args.proposal_id, registry=registry, operations=operations, **decision)
                )
            else:
                result = session.execute_write(
                    lambda tx: reject(tx, args.proposal_id, operations=operations, reason=args.reason,
                                      reject_claim=args.claim, **decision)
                )
            print(f"{result['proposal']['status']}: {result['assertion']['label']} "
                  f"(claim {result['assertion']['status']})")
            return 0
    except ReviewError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
