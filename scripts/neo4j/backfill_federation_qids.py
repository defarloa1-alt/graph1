#!/usr/bin/env python3
"""Backfill Wikidata QIDs on SYS_FederationSource nodes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

UPDATES = [
    ("edh", "Q1347027"),
    ("ocd", "Q430486"),
    ("open_alex", "Q107507571"),
    ("open_library", "Q1201876"),
    ("perseus_digital_library", "Q639661"),
    ("open_syllabus", "Q23760279"),
    ("crro", "Q24577251"),
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        for source_id, qid in UPDATES:
            result = session.run(
                "MATCH (f:SYS_FederationSource {source_id: $sid}) "
                "SET f.pid = $qid RETURN f.label",
                sid=source_id, qid=qid,
            )
            label = result.single()["f.label"]
            print(f"  {label:30s} <- {qid}")

        # Verify
        result = session.run(
            "MATCH (f:SYS_FederationSource) "
            "RETURN f.source_id, f.label, f.pid ORDER BY f.label"
        )
        print()
        for r in result:
            pid = r["f.pid"] or "(none)"
            print(f"  {r['f.label']:30s} {pid}")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
