#!/usr/bin/env python3
"""Look up Wikidata QIDs for CurriculumTopics using LCSH P244, then label fallback.

Outputs a Python dict that can be pasted into the update script.

Run:
  python scripts/bootstrap/curriculum_qid_lookup.py
"""
import sys, json, time, urllib.request, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {"Accept": "application/json", "User-Agent": "Chrystallum/1.0 (research)"}


def sparql(query):
    url = ENDPOINT + "?query=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())["results"]["bindings"]


def lookup_by_lcsh(lcsh_id):
    """Try P244 (LCSH identifier)."""
    rows = sparql(f'SELECT ?item WHERE {{ ?item wdt:P244 "{lcsh_id}" }}')
    if rows:
        return rows[0]["item"]["value"].split("/")[-1]
    return None


def lookup_by_label(heading):
    """Fallback: search by LCSH heading as English label."""
    # Clean heading for search
    heading_clean = heading.split("--")[0].strip()  # drop subdivisions
    rows = sparql(
        f'SELECT ?item WHERE {{ ?item rdfs:label "{heading_clean}"@en }} LIMIT 5'
    )
    if rows:
        return rows[0]["item"]["value"].split("/")[-1]
    return None


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as s:
        r = s.run(
            """
            MATCH (ct:CurriculumTopic)
            RETURN ct.key AS key, ct.lcsh_id AS lcsh_id, ct.lcsh_heading AS heading
            ORDER BY ct.facet_key, ct.key
            """
        )
        topics = [(row["key"], row["lcsh_id"], row["heading"]) for row in r]
    driver.close()

    results = {}
    p244_hits = 0
    label_hits = 0
    misses = 0

    for key, lcsh_id, heading in topics:
        # Strategy 1: P244
        qid = lookup_by_lcsh(lcsh_id)
        source = "P244"
        if not qid:
            # Strategy 2: label
            time.sleep(0.3)
            qid = lookup_by_label(heading)
            source = "label"
        if qid:
            results[key] = qid
            if source == "P244":
                p244_hits += 1
            else:
                label_hits += 1
            print(f"  {key:40s} {qid:12s} ({source}: {heading})")
        else:
            misses += 1
            print(f"  {key:40s} NO_MATCH     ({heading})")
        time.sleep(0.4)

    print(f"\nP244 hits: {p244_hits}  Label hits: {label_hits}  Misses: {misses}")
    print(f"Total: {len(results)}/{len(topics)}")

    # Output as Python dict
    print("\n# --- Copy below into update script ---")
    print("QID_MAP = {")
    for key, qid in sorted(results.items()):
        print(f'    "{key}": "{qid}",')
    print("}")


if __name__ == "__main__":
    main()
