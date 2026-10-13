"""Migration 005 (2026-10-13): a date known only to its decade or century is sometime within it.

    python -m GraphRevised.migrations.005_window_dates [--apply]

The harvest read a Wikidata date given to the decade or century ("1st century
BCE") as true throughout it, so a birth was linked to every Year of its
century. The adapter now reads such a date as an uncertain window (mode
"within": its first and last Years). This migration corrects what was stored
before the fix:

1. each Wikidata observation whose recorded time the adapter now reads
   differently (recomputed from the preserved record) has its mode corrected,
   with the former mode, time, and basis recorded on it; the value itself is
   unchanged;
2. the claim the corrected observation states is proposed again through the
   deterministic proposer: a new claim, since a claim's time mode is part of
   its identity;
3. each old claim's open Proposals are rejected (reason superseded-by-model,
   the claim left open), the old claim is superseded by the new one, and its
   Year links, a navigation projection, are removed.

Without --apply everything runs in one transaction that is rolled back.
Retry-safe: a corrected observation is not found again.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_statements import statement_observation
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import Neo4jReader, reject, submit, supersede
from GraphRevised.proposals.validator import Outcome
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation

REPOSITORY = Path(__file__).resolve().parents[2]
BY = "migration-005 (curator-approved model change, 2026-10-13)"
BASIS = ("A Wikidata date given only to its decade or century is an uncertain window (sometime within it), "
         "not a span true throughout it (25 section 10).")

CANDIDATES = """
MATCH (o:SourceObservation {sourceSystem: "Wikidata"})
WHERE o.statementTimeMode = "during" AND o.statementTimeEdtf CONTAINS "/"
RETURN o.id AS id, o.label AS label, o.shortLabel AS shortLabel, o.rawPayloadUri AS uri,
       o.externalStatementId AS statementId, o.statementTimeEdtf AS edtf
ORDER BY id
"""

OLD_CLAIMS = """
MATCH (o:SourceObservation {id: $id})
MATCH (a:Assertion)
WHERE a.status IN ["proposed", "accepted"] AND coalesce(a.timeMode, "during") = "during" AND a.timeEdtf = $edtf
  AND (EXISTS { MATCH (a)-[:SUPPORTED_BY]->(o) }
       OR EXISTS { MATCH (p:Proposal)-[:PROPOSES]->(a) MATCH (p)-[:PROPOSES_EVIDENCE]->(o) })
OPTIONAL MATCH (open:Proposal)-[:PROPOSES]->(a) WHERE open.status IN ["submitted", "validating", "deferred"]
RETURN a.id AS id, a.label AS label, collect(open.id) AS openProposals
"""


def migrate(tx, apply_time: str) -> list[str]:
    operations, registry = load_operations(), load_registry()
    reader = Neo4jReader(tx)
    lines = []
    for row in tx.run(CANDIDATES).data():
        path = REPOSITORY / row["uri"]
        now = statement_observation(path, row["statementId"], label=row["label"], short_label=row["shortLabel"] or row["label"])
        if now["statementTimeMode"] != "within" or now["statementTimeEdtf"] != row["edtf"]:
            continue  # a span true throughout, read the same today
        run_write(tx, operations, "renormalize_statement_time", {
            "id": row["id"], "statementTimeEdtf": row["edtf"], "statementTimeMode": "within",
            "decidedAt": apply_time, "basis": BASIS})
        old_claims = tx.run(OLD_CLAIMS, id=row["id"], edtf=row["edtf"]).data()
        replacements = []
        for draft in drafts_from_observation(reader.observation(row["id"]), reader, registry).drafts:
            result = submit(tx, draft, registry, operations).validation
            if result.outcome in (Outcome.VALID, Outcome.ADDS_EVIDENCE, Outcome.DUPLICATE):
                replacements.append(result.assertion_id)
            else:
                lines.append(f"  ! {draft.predicate} not proposed again: {'; '.join(result.reasons)}")
        for old in old_claims:
            if not replacements:
                lines.append(f"  ! {old['label']} kept: no replacement")
                continue
            for proposal in old["openProposals"]:
                reject(tx, proposal, decided_by=BY, decision_basis=BASIS, decided_at=apply_time,
                       reason="superseded-by-model", operations=operations)
            supersede(tx, old["id"], replacements, decided_by=BY, decision_basis=BASIS, decided_at=apply_time,
                      reason="superseded-by-model", operations=operations)
            removed = run_write(tx, operations, "unlink_assertion_years", {"assertionId": old["id"]})[0]["removed"]
            new_links = tx.run("MATCH (a:Assertion)-[l:IN_YEAR]->(y:Year) WHERE a.id IN $ids "
                               "RETURN collect(y.year + ' ' + l.as) AS links", ids=replacements).single()["links"]
            lines.append(f"{old['label']}: {removed} Year links -> {', '.join(sorted(new_links))}")
    return lines


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
                lines = migrate(tx, datetime.now(timezone.utc).isoformat(timespec="seconds"))
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("APPLIED" if args.apply else "DRY RUN (rolled back)") + f": {sum(not l.startswith('  !') for l in lines)} claim(s)")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
