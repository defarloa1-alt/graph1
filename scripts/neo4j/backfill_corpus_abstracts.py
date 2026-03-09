#!/usr/bin/env python3
"""
Backfill missing abstracts on CorpusWork nodes from the OpenAlex API.

Only processes works with work_id starting with 'openalex:' that have
null or empty abstract fields.

OpenAlex returns abstracts as inverted indexes; this script reconstructs
the full abstract text.

Usage:
    python scripts/neo4j/backfill_corpus_abstracts.py [--facet Military]

    Without --facet: backfills all CorpusWork nodes missing abstracts.
    With --facet: only backfills works RELEVANT_TO_FACET for that facet.
"""

import sys
import time
import argparse
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

OPENALEX_API = "https://api.openalex.org/works"
POLITE_EMAIL = "chrystallum@proton.me"  # for OpenAlex polite pool
SLEEP_BETWEEN = 1.0  # seconds between API calls


def reconstruct_abstract(inverted_index):
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not inverted_index:
        return None
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in word_positions)


def fetch_abstract_from_openalex(openalex_id):
    """Fetch abstract for a single OpenAlex work ID."""
    # openalex_id is like "openalex:W623795952" -> need "W623795952"
    raw_id = openalex_id.replace("openalex:", "")
    url = f"{OPENALEX_API}/{raw_id}"
    params = {"mailto": POLITE_EMAIL}

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            inverted = data.get("abstract_inverted_index")
            if inverted:
                return reconstruct_abstract(inverted)
        elif resp.status_code == 404:
            return None
        else:
            print(f"    WARNING: HTTP {resp.status_code} for {raw_id}")
            return None
    except Exception as e:
        print(f"    ERROR fetching {raw_id}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--facet", default=None, help="Only backfill works for this facet")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    updated = 0
    skipped = 0
    no_abstract = 0

    with driver.session() as session:
        # Find works needing abstracts
        if args.facet:
            result = session.run(
                """
                MATCH (cw:CorpusWork)-[:RELEVANT_TO_FACET]->(f:Facet {label: $facet})
                WHERE (cw.abstract IS NULL OR cw.abstract = '')
                  AND cw.work_id STARTS WITH 'openalex:'
                RETURN cw.work_id AS work_id, cw.title AS title
                """,
                facet=args.facet,
            )
        else:
            result = session.run(
                """
                MATCH (cw:CorpusWork)
                WHERE (cw.abstract IS NULL OR cw.abstract = '')
                  AND cw.work_id STARTS WITH 'openalex:'
                RETURN cw.work_id AS work_id, cw.title AS title
                """,
            )

        works = [(r["work_id"], r["title"]) for r in result]
        print(f"Found {len(works)} works needing abstracts")

        for work_id, title in works:
            print(f"  Fetching: {title[:60]}...", end=" ")
            abstract = fetch_abstract_from_openalex(work_id)

            if abstract:
                session.run(
                    """
                    MATCH (cw:CorpusWork {work_id: $work_id})
                    SET cw.abstract = $abstract,
                        cw.abstract_source = 'openalex_backfill'
                    """,
                    work_id=work_id,
                    abstract=abstract,
                )
                print(f"OK ({len(abstract)} chars)")
                updated += 1
            else:
                print("no abstract available")
                no_abstract += 1

            time.sleep(SLEEP_BETWEEN)

    driver.close()
    print(f"\nDone: {updated} updated, {no_abstract} unavailable, {skipped} skipped")


if __name__ == "__main__":
    main()
