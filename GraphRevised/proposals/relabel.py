"""Rename an Entity and rebuild the labels of the claims that name it (2026-11-19).

    python -m GraphRevised.proposals.relabel <entity-id> [--label "..."] [--short-label "..."]
        --by <name> --basis "<reason>" [--apply]
    python -m GraphRevised.proposals.relabel --all [--apply]   # refresh every stale claim label

A claim's label is written once, from its entities' names when it was stored, so a rename left
the old name in every earlier claim. Here the rename goes through `relabel_entity` (a decision
trail on the Entity), then every claim naming the Entity (as subject, object, context, role or
attributed Work) has its label rebuilt from its stored parts with the formatter `submit` uses
(store.format_claim_labels), and its Proposals' labels with it. Rebuilding, not replacing text:
an old name can be part of the new one. Labels are display only; ids, meaning and evidence are
untouched. Without --apply it reports and rolls back.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

from GraphRevised.operations import run_write

from .registry import PredicateRegistry
from .schema import QuantityQualifier
from .store import ReviewError, format_claim_labels
from .temporal import display_edtf
from GraphRevised import localdb

PARTS = """
MATCH (a:Assertion) WHERE a.id IN $ids
OPTIONAL MATCH (a)-[:ASSERTION_SUBJECT]->(s:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_ROLE]->(r:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_CONTEXT]->(c:Entity)
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity)
RETURN a.id AS id, a.label AS label, a.shortLabel AS shortLabel, properties(a) AS a,
       s {.label, .shortLabel} AS subject, o {.label, .shortLabel} AS object,
       r {.label, .shortLabel} AS role, c {.label, .shortLabel} AS context, w {.label, .shortLabel} AS work
ORDER BY id
"""
NAMING = """
MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_ROLE|ASSERTION_CONTEXT|ATTRIBUTED_TO]->(:Entity {id: $id})
RETURN DISTINCT a.id AS id ORDER BY id
"""


def _quantity(a: dict[str, Any]) -> str | None:
    figures = {key: a.get("quantity" + key.capitalize()) for key in ("minimum", "maximum", "typical")}
    if all(value is None for value in figures.values()):
        return None
    return QuantityQualifier(source_expression="stored", **{k: int(v) for k, v in figures.items() if v is not None}).display()


def _time(a: dict[str, Any]) -> str | None:
    return display_edtf(a["timeEdtf"]) if a.get("timeEdtf") else a.get("timeSourceExpression")


def rebuilt_labels(tx: Any, registry: PredicateRegistry, assertion_ids: list[str]) -> list[dict[str, Any]]:
    """Each claim's stored and rebuilt label and short caption. A claim whose predicate the
    registry no longer defines, or with no subject, is reported with `rebuilt` None."""
    rows = []
    for row in tx.run(PARTS, ids=assertion_ids).data():
        definition = registry.get(row["a"]["predicate"])
        rebuilt = None
        if definition is not None and row["subject"] is not None:
            rebuilt = format_claim_labels(
                definition.display, row["subject"], row["object"], role=row["role"], context=row["context"],
                work=row["work"] if row["a"].get("mode") == "attributed" else None,
                quantity=_quantity(row["a"]), reception=row["a"].get("reception"), time=_time(row["a"]))
        rows.append({"id": row["id"], "stored": (row["label"], row["shortLabel"]), "rebuilt": rebuilt})
    return rows


def rename_entity(
    tx: Any, operations: dict[str, str], registry: PredicateRegistry, entity_id: str, *,
    label: str | None = None, short_label: str | None = None,
    decided_by: str, decision_basis: str, decided_at: str,
) -> dict[str, Any]:
    """Rename an Entity (with its decision trail) and rebuild the labels of every claim naming it."""
    if label is None and short_label is None:
        raise ReviewError("give a new label, a new short label, or both")
    renamed = run_write(tx, operations, "relabel_entity", {
        "id": entity_id, "label": label, "shortLabel": short_label,
        "decidedAt": decided_at, "decidedBy": decided_by, "decisionBasis": decision_basis})[0]
    claims = [row["id"] for row in tx.run(NAMING, id=entity_id).data()]
    entity = renamed["entity"]
    return {"entity": {"id": entity_id, "label": entity["label"], "shortLabel": entity.get("shortLabel")},
            "renamed": renamed["changes"], **refresh_claim_labels(tx, operations, registry, claims)}


def refresh_claim_labels(tx: Any, operations: dict[str, str], registry: PredicateRegistry,
                         assertion_ids: list[str] | None = None) -> dict[str, Any]:
    """Rewrite the labels of the given claims (all claims when None) that no longer match their
    entities' current names. Display only."""
    if assertion_ids is None:
        assertion_ids = [row["id"] for row in tx.run("MATCH (a:Assertion) RETURN a.id AS id").data()]
    changed, skipped = [], []
    for row in rebuilt_labels(tx, registry, assertion_ids):
        if row["rebuilt"] is None:
            skipped.append(row["id"])
        elif tuple(row["rebuilt"]) != tuple(row["stored"]):
            run_write(tx, operations, "set_claim_labels", {
                "assertionId": row["id"], "label": row["rebuilt"][0], "shortLabel": row["rebuilt"][1]})
            changed.append({"id": row["id"], "from": row["stored"], "to": list(row["rebuilt"])})
    return {"claims": len(assertion_ids), "relabelled": changed, "skipped": skipped}


def main(argv: list[str] | None = None) -> int:
    from neo4j import GraphDatabase

    from GraphRevised.operations import load_operations

    from .registry import load_registry

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entity_id", nargs="?")
    parser.add_argument("--all", action="store_true", help="refresh every claim label that is stale")
    parser.add_argument("--label")
    parser.add_argument("--short-label")
    parser.add_argument("--by")
    parser.add_argument("--basis")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.all == bool(args.entity_id) or (args.entity_id and not (args.by and args.basis)):
        parser.error("give an entity id with --by and --basis, or --all")
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                if args.all:
                    report = refresh_claim_labels(tx, load_operations(), load_registry())
                else:
                    report = rename_entity(tx, load_operations(), load_registry(), args.entity_id,
                                           label=args.label, short_label=args.short_label, decided_by=args.by,
                                           decision_basis=args.basis,
                                           decided_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("applied" if args.apply else "dry run, rolled back")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
