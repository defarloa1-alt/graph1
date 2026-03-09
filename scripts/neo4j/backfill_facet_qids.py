#!/usr/bin/env python3
"""Backfill Wikidata QIDs on Facet nodes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

FACET_QIDS = [
    ("ARCHAEOLOGICAL",  "Q23498",     "archaeology"),
    ("ARTISTIC",        "Q50637",     "art history"),
    ("BIOGRAPHIC",      "Q36279",     "biography"),
    ("COMMUNICATION",   "Q11680831",  "communication studies"),
    ("CULTURAL",        "Q858517",    "cultural history"),
    ("DEMOGRAPHIC",     "Q37732",     "demography"),
    ("DIPLOMATIC",      "Q2177756",   "diplomatic history"),
    ("ECONOMIC",        "Q47398",     "economic history"),
    ("ENVIRONMENTAL",   "Q1561862",   "environmental history"),
    ("GEOGRAPHIC",      "Q384001",    "historical geography"),
    ("INTELLECTUAL",    "Q1195695",   "intellectual history"),
    ("LINGUISTIC",      "Q190375",    "historical linguistics"),
    ("MILITARY",        "Q192781",    "military history"),
    ("POLITICAL",       "Q1147507",   "political history"),
    ("RELIGIOUS",       "Q846742",    "history of religions"),
    ("SCIENTIFIC",      "Q201486",    "history of science"),
    ("SOCIAL",          "Q908604",    "social history"),
    ("TECHNOLOGICAL",   "Q465352",    "history of technology"),
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        for key, qid, wikidata_label in FACET_QIDS:
            result = session.run(
                "MATCH (f:Facet {key: $key}) "
                "SET f.qid = $qid, f.wikidata_label = $wlabel "
                "RETURN f.label",
                key=key, qid=qid, wlabel=wikidata_label,
            )
            label = result.single()["f.label"]
            print(f"  {label:20s} {key:20s} <- {qid:12s} ({wikidata_label})")

        # Verify
        print()
        result = session.run(
            "MATCH (f:Facet) RETURN f.key, f.label, f.qid, f.wikidata_label ORDER BY f.key"
        )
        for r in result:
            print(f"  {r['f.key']:20s} {r['f.qid'] or '(none)':12s} {r['f.wikidata_label'] or ''}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
