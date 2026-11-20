"""Migration 009 (2026-11-13): every Type gets its typeCategory (D-039, registry v15).

    python -m GraphRevised.migrations.009_type_categories [--apply]

The 23 Types had no category. The categories are the registry's
typeCategories: role, unit type, organizational pattern, power, status.

- The event roles of curation/event-roles.json (D-139) are "role".
- matrona is "status": a recognised standing a woman holds, not an office and
  not a part played in an event (moved from Office to Type on 2026-11-12;
  status added as a category by the curator on 2026-11-13).

Each is set through set_type_category, which keeps who set it, when, and the
basis. A Type not covered here is reported, not guessed. Without --apply it
reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised import localdb

ROOT = Path(__file__).resolve().parents[1]
ROLES = ROOT / "curation" / "event-roles.json"
BY = "Claude for the curator (approved 2026-11-13)"
OTHERS = {
    "chr:entity:matrona": ("status", "A recognised standing a woman holds (a married Roman woman of "
                                     "standing), not an office and not a part played in an event."),
}


def plan() -> dict[str, tuple[str, str]]:
    roles = json.loads(ROLES.read_text(encoding="utf-8"))["localEntities"]
    planned = {item["id"]: ("role", "A part played in a depicted event (D-139, curation/event-roles.json).")
               for item in roles if item["kind"] == "Type"}
    planned.update(OTHERS)
    return planned


def migrate(tx, apply_at: str) -> dict:
    operations, registry = load_operations(), load_registry()
    planned = plan()
    types = tx.run("MATCH (t:Entity:Type) RETURN t.id AS id, t.label AS label, t.typeCategory AS category "
                   "ORDER BY id").data()
    done, unplanned = [], []
    for row in types:
        if row["id"] not in planned:
            unplanned.append(f"{row['id']} ({row['label']})")
            continue
        category, basis = planned[row["id"]]
        run_write(tx, operations, "set_type_category", {
            "id": row["id"], "category": category, "allowedCategories": sorted(registry.type_categories),
            "decidedAt": apply_at, "decidedBy": BY, "decisionBasis": basis})
        done.append(f"{row['label']}: {row['category'] or '-'} -> {category}")
    missing = sorted(set(planned) - {row["id"] for row in types})
    return {"set": done, "unplanned": unplanned, "missing": missing}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                result = migrate(tx, datetime.now(timezone.utc).isoformat())
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    verb = "set" if args.apply else "would set"
    print(f"{verb} {len(result['set'])} Type categories:")
    print("\n".join(f"  {line}" for line in result["set"]))
    for key, text in (("unplanned", "Types with no planned category (left alone)"),
                      ("missing", "planned Types not in the graph")):
        if result[key]:
            print(f"{text}: {len(result[key])}")
            print("\n".join(f"  {line}" for line in result[key]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
