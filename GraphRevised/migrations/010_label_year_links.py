"""Migration 010 (2026-11-13): every Year link says how the claim's time covers it.

    python -m GraphRevised.migrations.010_label_year_links [--apply]

Four claims were tethered before Year links carried `as` (start, end, during,
earliest, latest). Two are PeriodO definitions of the Roman Republic (EAMENA,
-150 to -50; the Levantine Ceramics Project, -133 to -31), linked to every Year
of their span with no label; the others are early claims of the Actium slice.
Their unlabelled links are dropped (drop_unlabelled_year_links) and the claim
is tethered again by temporal.year_links, as a new claim would be. Without
--apply it reports and rolls back. Retry-safe: a claim whose links are all
labelled is not selected.
"""

from __future__ import annotations

import argparse
import os
import sys

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.temporal import parse_edtf, year_links

UNLABELLED = """
MATCH (a:Assertion)-[link:IN_YEAR]->(:Year)
WITH a, count(link) AS links, count(link.as) AS labelled WHERE labelled < links
RETURN a.id AS id, a.label AS label, a.timeEdtf AS edtf, a.timeCalendar AS calendar,
       coalesce(a.timeMode, 'during') AS mode, links
ORDER BY id
"""


def relabel(tx, operations) -> list[str]:
    lines = []
    for row in tx.run(UNLABELLED).data():
        links, notes = year_links(parse_edtf(row["edtf"], row["calendar"]), row["mode"])
        removed = run_write(tx, operations, "drop_unlabelled_year_links", {"assertionId": row["id"]})[0]["removed"]
        if links:
            run_write(tx, operations, "link_assertion_years", {
                "assertionId": row["id"], "links": [{"year": y, "as": how} for y, how in links]})
        shown = ", ".join(f"{year} {how}" for year, how in links) or "nothing inside the backbone"
        lines.append(f"{row['label']}: {removed} unlabelled link(s) -> {shown}" + (f" ({'; '.join(notes)})" if notes else ""))
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
                lines = relabel(tx, load_operations())
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("relabelled" if args.apply else "would relabel") + f" {len(lines)} claim(s):")
    print("\n".join(f"  {line}" for line in lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
