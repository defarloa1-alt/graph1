"""Accept code-made extractions by rule; leave agent reasoning to the curator (D-145).

    python -m GraphRevised.proposals.rule_accept [--apply]

The curator reviews reasoning, not extraction (2026-11-13). A proposal is
accepted by rule only when nothing but code stood between the source and the
claim:

- made by a deterministic proposer (RULE_PROPOSERS), with no model behind it;
- attributed ("according to" its source), never our own statement;
- every piece of evidence a structured record: a Wikidata statement or a
  record observation (PeriodO, a catalog record), never a passage, which
  needs reading.

It runs proposals/store.accept (which re-validates the evidence) and is
signed by the rule, so it is reversible like any decision (`retract`).
Everything else (the passage reader, the phase agent, Claude's drafts from
the curator's notes) waits for the curator. Without --apply it reports and
rolls back. The fact layer is rebuilt in the same transaction.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations

from .registry import load_registry
from .store import accept

RULE = "rule: code-made extraction (D-145)"
RULE_PROPOSERS = ("wikidata-statement-proposer-v1", "period-survey", "polity-span-proposer-v1",
                  "crro-coin-legend",  # what a coin legend literally names (D-151); not the unit's service
                  "wikidata-reference-proposer-v1",  # a claim as the work a Wikidata statement cites (2026-11-16)
                  "getty-aat-hierarchy",  # the AAT's broader concept, from its record (45 §4.3, D-160)
                  "crro-coin-record")  # a coin record's denomination and metal (45 §5.1, D-160)
BASIS = ("Accepted by rule: a deterministic proposer drew this claim from structured records alone, "
         "attributed to its source, with no model or agent reasoning to review (D-145).")

ELIGIBLE = """
MATCH (p:Proposal)-[:PROPOSES]->(a:Assertion)
WHERE p.status IN ['submitted', 'validating', 'deferred'] AND p.createdBy IN $proposers AND p.modelId IS NULL
  AND a.status IN ['proposed', 'accepted'] AND a.mode = 'attributed'
  AND EXISTS { (p)-[:PROPOSES_EVIDENCE]->() }
  AND NOT EXISTS { (p)-[:PROPOSES_EVIDENCE]->(o:SourceObservation)
                   WHERE NOT (o.observationKind = 'record'
                              OR (o.sourceSystem = 'Wikidata' AND o.externalStatementId IS NOT NULL)) }
RETURN p.id AS id, p.createdBy AS by, a.predicate AS predicate ORDER BY p.id
"""


def eligible(tx: Any) -> list[dict[str, Any]]:
    return tx.run(ELIGIBLE, proposers=list(RULE_PROPOSERS)).data()


def accept_by_rule(tx: Any, at: str | None = None) -> dict[str, Any]:
    """Accept every eligible proposal in the caller's transaction; report what was and was not accepted."""
    from GraphRevised.export.fact_layer import rebuild  # export imports proposals; import late

    at = at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    operations, registry = load_operations(), load_registry()
    accepted, refused = Counter(), []
    for row in eligible(tx):
        try:
            accept(tx, row["id"], decided_by=RULE, decision_basis=BASIS, decided_at=at,
                   registry=registry, operations=operations)
            accepted[(row["by"], row["predicate"])] += 1
        except Exception as error:  # a proposal that no longer validates stays open for the curator
            refused.append((row["id"], str(error)))
    return {"accepted": accepted, "refused": refused, "layer": rebuild(tx) if accepted else None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                result = accept_by_rule(tx)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("" if args.apply else "(dry run, rolled back)")
    for (by, predicate), n in sorted(result["accepted"].items()):
        print(f"  accepted {n:4} {predicate:16} from {by}")
    print(f"accepted {sum(result['accepted'].values())}, left for the curator {len(result['refused'])}")
    for proposal_id, error in result["refused"][:20]:
        print(f"  open: {proposal_id}: {error[:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
