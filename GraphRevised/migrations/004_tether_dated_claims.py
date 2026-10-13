"""Migration 004 (2026-10-13): every dated claim tethers to the Year backbone (25 section 10).

    python -m GraphRevised.migrations.004_tether_dated_claims [--apply]

Before this rule, a time spanning more than 200 years got no Year link at
all, which left period bounds (such as each PeriodO definition of the Roman
Republic) untethered. This links every Assertion that has a normalized time
and no Year link yet, by temporal.year_links: start and end Years for a long
span, every Year for a short one. Without --apply it reports and writes
nothing. Retry-safe: claims already tethered are not touched.
"""

from __future__ import annotations

import argparse
import os

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.temporal import parse_edtf, year_links

UNTETHERED = """
MATCH (a:Assertion) WHERE a.timeEdtf IS NOT NULL AND a.timeCalendar IS NOT NULL AND NOT (a)-[:IN_YEAR]->(:Year)
RETURN a.id AS id, a.label AS label, a.timeEdtf AS edtf, a.timeCalendar AS calendar, coalesce(a.timeMode, 'during') AS mode
ORDER BY id
"""


def tether_all(tx, operations, apply: bool) -> list[str]:
    lines = []
    for row in tx.run(UNTETHERED).data():
        links, notes = year_links(parse_edtf(row["edtf"], row["calendar"]), row["mode"])
        shown = ", ".join(f"{year} {how}" for year, how in links) or "nothing inside the backbone"
        lines.append(f"{row['label']}: {shown}" + (f" ({'; '.join(notes)})" if notes else ""))
        if apply and links:
            run_write(tx, operations, "link_assertion_years", {
                "assertionId": row["id"], "links": [{"year": y, "as": how} for y, how in links]})
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            lines = session.execute_write(tether_all, load_operations(), args.apply)
    finally:
        driver.close()
    print(("tethered" if args.apply else "would tether") + f" {len(lines)} claim(s):")
    print("\n".join(f"  {line}" for line in lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
