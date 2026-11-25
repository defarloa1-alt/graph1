"""Migration 034 (2026-11-24): the passages the Actium scene rests on, read (extraction only).

    python -m GraphRevised.migrations.034_actium_scene_passages [--apply]

The check of the Actium animation (docs/Actium/animation-check.md) found statements resting on
passages we did not hold. These are read here from the preserved editions already in the repository,
and stored as passage observations of their Works:

- Cassius Dio, Roman History (Cary, LacusCurtius): 50.9.3 (the winter at Patrae), 50.14.4 (provisions
  fail), 51.10.1 (Antony returns from Paraetonium), 51.10.4 (the fleet deserts), 51.10.7 and 51.10.9
  (Antony's death), 51.19.6 (the day Alexandria was captured);
- Plutarch, Life of Antony (Perrin, Perseus): 69.1 (Paraetonium), 76.1 to 76.3 (the fleet and the
  cavalry go over; Antony's despair), 77.1 (Antony carried to the tomb), 80.1 (Caesar enters the city).

Extraction only: no claim, no entity, no Proposal (verbatim passages need no review). The scene
(scenes/actium-campaign-31bc.proposed.json) cites them. Without --apply it reports and rolls back.
Retry-safe (upserts by id).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised import localdb
from GraphRevised.adapters import lacuscurtius_passages as lc
from GraphRevised.adapters import perseus_passages as pp
from GraphRevised.operations import load_operations, run_write

ROOT = Path(__file__).resolve().parents[1]
DIO = "chr:entity:cassius-dio-roman-history"
PLUTARCH = "chr:entity:plutarch-life-of-antony"
DIO_REFS = {"50": ["50.9.3", "50.14.4"], "51": ["51.10.1", "51.10.4", "51.10.7", "51.10.9", "51.19.6"]}
PLUTARCH_REFS = ["69.1", "76.1", "76.2", "76.3", "77.1", "80.1"]


def passages() -> list[tuple[str, dict]]:
    out = []
    for book, refs in DIO_REFS.items():
        edition = lc.load_edition([next((ROOT / "phase-6-source").glob(f"lacuscurtius-cassius-dio-{book}-html-*.html"))],
                                  translator="Earnest Cary")
        out += [(DIO, lc.passage_observation(edition, ref)) for ref in refs]
    path = next((ROOT / "phase-5-source").glob("perseus-tlg0007.tlg058.perseus-eng2-*.xml"))
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    edition = pp.load_edition(path, source_commit=metadata["sourceRevision"], rights=metadata.get("rights"))
    out += [(PLUTARCH, pp.passage_observation(edition, ref, retrieved_at=metadata["retrievedAt"],
                                              source_uri=metadata["sourceUri"])) for ref in PLUTARCH_REFS]
    return out


def migrate(tx, operations) -> dict:
    report = []
    for work, passage in passages():
        existed = tx.run("MATCH (o:SourceObservation {id: $id}) RETURN count(o) AS n", id=passage["id"]).single()["n"]
        run_write(tx, operations, "upsert_passage_observation", passage)
        run_write(tx, operations, "link_observation_work", {"observationId": passage["id"], "workId": work})
        report.append({"id": passage["id"], "shortLabel": passage["shortLabel"], "new": not existed})
    return {"passages": report}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations())
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
