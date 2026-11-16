"""Migration 011 (2026-11-13): Wikidata is a voice, not our own statement (D-145).

    python -m GraphRevised.migrations.011_wikidata_as_a_voice [--apply]

The curator: Wikidata "can be trusted to some extent but is not golden". Until
now the deterministic proposers filed Wikidata statements in our own voice
(asserted). In one transaction this:

1. creates the Work `chr:entity:wikidata` (form dataset) that every Wikidata
   statement is attributed to;
2. re-files each open claim resting on Wikidata statements alone as "according
   to Wikidata": the same predicate, endpoints, time and evidence, submitted
   attributed; the old claim's open Proposals are rejected
   (superseded-by-model) and the old claim superseded by the new one;
3. accepts the code-made extractions by rule (proposals/rule_accept.py) and
   rebuilds the fact layer.

Accepted claims are left alone: the curator decided them. Without --apply it
reports and rolls back. Retry-safe: a re-filed claim is superseded, so it is
not selected again.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.rule_accept import accept_by_rule
from GraphRevised.proposals.store import _draft_from_stored, _stored_proposal, reject, submit, supersede
from GraphRevised.proposals.wikidata_proposer import WIKIDATA_WORK

WORK = {"id": WIKIDATA_WORK, "kind": "Work", "label": "Wikidata", "shortLabel": "Wikidata", "form": "dataset",
        "description": "The Wikidata knowledge base: what its editors have stated, statement by statement. "
                       "A voice that can be trusted to some extent but is not golden (curator, 2026-11-13)."}
BY = "Claude (delegated by Tony DeFarlo)"
BASIS = "Wikidata is a voice, not our own statement (curator, 2026-11-13; D-145): re-filed as according to Wikidata."

ONLY_WIKIDATA = """
MATCH (a:Assertion {status: 'proposed'}) WHERE coalesce(a.mode, 'asserted') = 'asserted'
WITH a, COLLECT { MATCH (p:Proposal)-[:PROPOSES]->(a) WHERE p.status IN ['submitted', 'validating', 'deferred']
                  RETURN p.id } AS open,
     COLLECT { MATCH (p:Proposal)-[:PROPOSES]->(a) WHERE p.status IN ['submitted', 'validating', 'deferred']
               MATCH (p)-[:PROPOSES_EVIDENCE]->(o:SourceObservation) RETURN o } AS evidence
WHERE size(open) > 0 AND size(evidence) > 0
  AND all(o IN evidence WHERE o.sourceSystem = 'Wikidata' AND o.externalStatementId IS NOT NULL)
RETURN a.id AS id, a.predicate AS predicate, open ORDER BY a.id
"""


def migrate(tx, operations, registry, at: str) -> dict:
    exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=WORK["id"]).single() is not None
    run_write(tx, operations, "upsert_entity", {k: WORK[k] for k in ("id", "kind", "label", "shortLabel", "description")}
              | {"status": None if exists else "provisional"})
    run_write(tx, operations, "set_work_form", {"workId": WORK["id"], "form": WORK["form"],
                                                "allowedForms": sorted(registry.work_forms)})
    refiled, problems = Counter(), []
    for row in tx.run(ONLY_WIKIDATA).data():
        replacements = []
        for proposal_id in row["open"]:
            stored = _stored_proposal(tx, proposal_id)
            draft = _draft_from_stored(stored, stored["evidence"], rationale=stored["rationale"] or BASIS,
                                       proposed_by=stored["createdBy"] or "unknown")
            draft = draft.model_copy(update={"mode": "attributed", "attributed_to": WIKIDATA_WORK})
            result = submit(tx, draft, registry, operations).validation
            if result.assertion_id is None:
                problems.append(f"{row['id']}: {result.outcome.value} {list(result.reasons)}")
                break
            replacements.append(result.assertion_id)
        else:
            for proposal_id in row["open"]:
                reject(tx, proposal_id, decided_by=BY, decision_basis=BASIS, decided_at=at,
                       reason="superseded-by-model", operations=operations)
            supersede(tx, row["id"], replacements, decided_by=BY, decision_basis=BASIS, decided_at=at,
                      reason="superseded-by-model", operations=operations)
            refiled[row["predicate"]] += 1
    return {"workCreated": not exists, "refiled": refiled, "problems": problems, "rule": accept_by_rule(tx, at)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                result = migrate(tx, load_operations(), load_registry(), at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("" if args.apply else "(dry run, rolled back)")
    print(f"Wikidata Work {'created' if result['workCreated'] else 'already there'}")
    print(f"re-filed as according to Wikidata: {sum(result['refiled'].values())} "
          + ", ".join(f"{p} {n}" for p, n in result["refiled"].most_common()))
    for problem in result["problems"][:20]:
        print(f"  not re-filed: {problem}")
    rule = result["rule"]
    print(f"accepted by rule: {sum(rule['accepted'].values())} "
          + ", ".join(f"{p} {n}" for (_, p), n in rule["accepted"].most_common()))
    print(f"left for the curator after the rule pass: {len(rule['refused'])}")
    for proposal_id, error in rule["refused"][:15]:
        print(f"  open: {proposal_id}: {error[:220]}")
    if rule["layer"]:
        print("fact layer: " + ", ".join(f"{k} {v}" for k, v in rule["layer"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
