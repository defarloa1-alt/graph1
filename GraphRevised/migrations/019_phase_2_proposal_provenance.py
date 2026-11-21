"""Migration 019 (2026-11-18): the Phase 2 Proposal's provenance, back-filled.

    python -m GraphRevised.migrations.019_phase_2_proposal_provenance [--apply]

The first Proposal in the graph, `accept-marcus-vipsanius-agrippa-participation-at-actium`,
was written by the Phase 2 direct workflow on 2026-10-11 at 11:25 UTC
(12-PHASE-2-ACTIUM.md), before the proposal-draft schema and predicate
registry v1 existed (their first Proposals came at 15:04 that day). It has no
`createdBy`, `rationale`, `draftSchemaVersion`, or `predicateRegistryVersion`,
so the graph type (018) could not require them (30 §8 item 8; curator,
2026-11-18).

The values say what happened, not what a later Proposal would hold: the
creator is the Assertion's own `assertedBy` (checked: the run refuses if they
differ); the rationale, written here, spells out the Phase 2 basis the Proposal
already holds in `decisionBasis` ("One preserved Wikidata P710 participant
statement") and names the plan it came from; the two versions name the
absence. The
back-fill is marked (`provenanceBackfilledAt`, `…By`, `…Basis`) so it is
never read as written at creation. Only properties that are missing are
set. Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase
from GraphRevised import localdb

PROPOSAL = "chr:proposal:accept-marcus-vipsanius-agrippa-participation-at-actium"
VALUES = {
    "createdBy": "direct_phase_2_workflow",
    "rationale": ("Phase 2 (12-PHASE-2-ACTIUM.md): Agrippa's participation in the Battle of Actium, "
                  "from one preserved Wikidata P710 (participant) statement, the observation this "
                  "Assertion is SUPPORTED_BY."),
    "draftSchemaVersion": "none: Phase 2 direct workflow, before proposal-draft-v1",
    "predicateRegistryVersion": "none: Phase 2 direct workflow, before predicates-v1",
}
BASIS = ("30 §8 item 8, curator 2026-11-18: written before the draft schema and registry existed; "
         "values from the Assertion's assertedBy and the Proposal's decisionBasis")

BACKFILL = """
MATCH (p:Proposal {id: $id})-[:PROPOSES]->(a:Assertion)
WITH p, a, [k IN keys($values) WHERE p[k] IS NULL] AS missing
FOREACH (k IN missing | SET p[k] = $values[k])
FOREACH (_ IN CASE WHEN size(missing) > 0 THEN [1] ELSE [] END |
  SET p.provenanceBackfilledAt = $now, p.provenanceBackfilledBy = $by, p.provenanceBackfillBasis = $basis)
RETURN missing, a.assertedBy AS assertedBy
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth())
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                row = tx.run(BACKFILL, id=PROPOSAL, values=VALUES, by="Claude (migration 019)", basis=BASIS,
                             now=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")).single()
                if row is None:
                    print(f"no Proposal {PROPOSAL}")
                    tx.rollback()
                    return 1
                if row["assertedBy"] != VALUES["createdBy"]:
                    print(f"refused: the Assertion was asserted by {row['assertedBy']!r}")
                    tx.rollback()
                    return 1
                print(f"set {row['missing'] or 'nothing (already complete)'}")
                tx.commit() if args.apply else tx.rollback()
                print("written" if args.apply else "dry run, rolled back")
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
