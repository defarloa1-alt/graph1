"""Migration 012 (2026-11-15, D-148): Works get a standing; modern claims start untraced.

    python -m GraphRevised.migrations.012_work_standing [--apply]

Attestation now counts independent lines of evidence (42-CORROBORATION-AND-
CLAIM-KINDS.md). Each existing Work gets a standing: primary (an ancient
source), secondary (a modern study), or tertiary (a reference work). No Work
had a composition date, so this first classification is Claude's (an agent's
reasoning, recorded on the node for the curator to check, D-145). Then every
live claim attributed to a secondary or tertiary Work gets basis `unknown`:
not yet traced to the ancient source it retells, and so not counted.

Without --apply it reports and rolls back. Retry-safe: a Work already given
the same standing, or a claim already given a basis, is left as it is.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised import localdb

BY = "Claude (agent), migration 012; for the curator to check"
PRIMARY = "written in antiquity by an ancient author"
SECONDARY = "a modern study by a named author"
TERTIARY = "a reference work, catalogue, or database"

E = "chr:entity:"
STANDING = {
    "primary": (PRIMARY, [
        "cassius-dio-roman-history", "plutarch-life-of-antony", "proposed-work-velleius-paterculus-historiae-romanae",
        "proposed-work-strabo-geography", "proposed-work-virgil-aeneid", "proposed-work-augustus-res-gestae-divi-augusti",
        "parallel-lives", "natural-history", "description-of-greece", "commentarii-de-bello-gallico",
        "proposed-work-appian-civil-wars", "proposed-work-plutarch-life-of-brutus", "proposed-work-virgil-georgics",
        "proposed-work-horace-odes", "proposed-work-horace-epistles"]),
    "secondary": (SECONDARY, [
        "weigall-life-and-times-of-cleopatra", "hale-famous-sea-fights", "strauss-war-that-made-the-roman-empire",
        "proposed-work-stokstad-art-history",
        "proposed-work-gates-ancient-cities-the-archaeology-of-urban-life-in-the-ancient-near-east-and-egypt-greece-and-rome"]),
}
# Every other Work in the graph today is a reference work, catalogue, dataset, or encyclopedia.

WORKS = "MATCH (w:Entity:Work) RETURN w.id AS id, w.label AS label, w.standing AS standing ORDER BY id"
UNTRACED = """
MATCH (a:Assertion)-[:ATTRIBUTED_TO]->(w:Entity:Work)
WHERE a.status IN ["accepted", "proposed"] AND w.standing IN ["secondary", "tertiary"] AND a.basis IS NULL
RETURN a.id AS id, w.standing AS standing
"""


def classify(tx, operations, at: str) -> tuple[list[str], Counter]:
    named = {E + key: (standing, basis) for standing, (basis, keys) in STANDING.items() for key in keys}
    lines = []
    for row in tx.run(WORKS).data():
        standing, basis = named.get(row["id"], ("tertiary", TERTIARY))
        if row["standing"] and row["standing"] != standing:
            lines.append(f"kept {row['standing']}: {row['label']} (already set; not {standing})")
            continue
        run_write(tx, operations, "set_work_standing", {"id": row["id"], "standing": standing, "decidedAt": at,
                                                        "decidedBy": BY, "decisionBasis": basis})
        lines.append(f"{standing}: {row['label']}")
    missing = set(named) - {row["id"] for row in tx.run(WORKS).data()}
    if missing:
        raise RuntimeError(f"Works named here are not in the graph: {sorted(missing)}")
    marked = Counter()
    for row in tx.run(UNTRACED).data():
        run_write(tx, operations, "set_claim_basis", {"assertionId": row["id"], "basis": "unknown",
                                                      "decidedAt": at, "decidedBy": BY})
        marked[row["standing"]] += 1
    return lines, marked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                lines, marked = classify(tx, load_operations(), at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("set" if args.apply else "would set") + f" standing on {len(lines)} Work(s):")
    print("\n".join(f"  {line}" for line in sorted(lines)))
    print(f"basis unknown on {sum(marked.values())} claim(s): {dict(marked)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
