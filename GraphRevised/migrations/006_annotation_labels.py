"""Migration 006 (2026-10-14): an annotation's label says what it is and where, not what it says.

    python -m GraphRevised.migrations.006_annotation_labels [--apply]

Annotations were labelled with the first 120 characters of their note, so
label and note repeated each other. The label is now composed by
capture.core.annotation_label: the note type or the mention ("Anecdote",
"Mention of “Empire” (Period)") and the place (the passage's short caption,
else the source system), for example "Anecdote · Weigall 17.11". Only labels
change, through upsert_annotation; notes, links, and statuses are untouched.
Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from neo4j import GraphDatabase

from GraphRevised.capture.core import annotation_label
from GraphRevised.operations import load_operations, run_write

ANNOTATIONS = """
MATCH (n:Annotation)
OPTIONAL MATCH (n)-[link:ANNOTATES]->(o:SourceObservation)
OPTIONAL MATCH (n)-[:CONCERNS]->(e:Entity)
RETURN n {.id, .label, .kind, .noteType, .note, .author, .visibility, .createdAt} AS n,
       o.id AS observationId, link.quotation AS quotation,
       collect(e.id) AS concerns, collect(e.label) AS labels, collect(e.kind) AS kinds
ORDER BY n.id
"""
SURVEY_SOURCES = {"period-survey": "PeriodO"}  # mentions with no passage name their source system


def relabel(tx, apply: bool) -> list[str]:
    operations = load_operations()
    lines = []
    for row in tx.run(ANNOTATIONS).data():
        n = row["n"]
        mentioned = mentioned_kind = None
        if n["kind"] == "entity-mention":
            named = re.search(r'named as "(.*)"', n["note"] or "")
            mentioned = named.group(1) if named else (row["labels"][0] if row["labels"] else None)
            mentioned_kind = row["kinds"][0] if row["kinds"] else None
        label = annotation_label(tx, kind=n["kind"], note_type=n["noteType"], observation_id=row["observationId"],
                                 mentioned=mentioned, mentioned_kind=mentioned_kind,
                                 source=SURVEY_SOURCES.get(n["author"]))
        if label == n["label"]:
            continue
        lines.append(f"{label}  <-  {n['label'][:60]}")
        if apply:
            run_write(tx, operations, "upsert_annotation", {
                "id": n["id"], "label": label, "kind": n["kind"], "noteType": n["noteType"], "note": n["note"],
                "author": n["author"], "visibility": n["visibility"], "createdAt": n["createdAt"],
                "observationId": row["observationId"], "quotation": row["quotation"], "concerns": row["concerns"]})
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
                lines = relabel(tx, args.apply)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("relabelled" if args.apply else "would relabel") + f" {len(lines)} annotation(s)")
    print("\n".join(f"  {line}" for line in lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
