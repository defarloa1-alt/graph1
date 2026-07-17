#!/usr/bin/env python3
"""Add wikipedia_url property to CurriculumTopics by resolving QID sitelinks.

Run:
  python scripts/v2/add_wikipedia_urls.py
"""
import sys, json, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase


def get_enwiki_titles(qids):
    """Batch lookup enwiki sitelinks for a list of QIDs."""
    ids = "|".join(qids)
    url = (
        "https://www.wikidata.org/w/api.php"
        f"?action=wbgetentities&ids={ids}&props=sitelinks"
        "&sitefilter=enwiki&format=json"
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "Chrystallum/2.0 (research)"}
    )
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    result = {}
    for qid in qids:
        entity = data.get("entities", {}).get(qid, {})
        title = entity.get("sitelinks", {}).get("enwiki", {}).get("title")
        if title:
            result[qid] = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
    return result


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as s:
        r = s.run(
            "MATCH (ct:CurriculumTopic) "
            "RETURN ct.key AS key, ct.qid AS qid ORDER BY ct.key"
        )
        topics = [(row["key"], row["qid"]) for row in r]

    print(f"Loaded {len(topics)} CurriculumTopics")

    # Batch lookup (50 per request)
    wiki_map = {}
    all_qids = [t[1] for t in topics]
    for i in range(0, len(all_qids), 50):
        batch = all_qids[i : i + 50]
        wiki_map.update(get_enwiki_titles(batch))
        time.sleep(0.3)

    # Write to graph
    with driver.session() as s:
        updated = 0
        no_wiki = []
        for key, qid in topics:
            wiki_url = wiki_map.get(qid)
            if wiki_url:
                s.run(
                    "MATCH (ct:CurriculumTopic {key: $key}) "
                    "SET ct.wikipedia_url = $url",
                    key=key,
                    url=wiki_url,
                )
                updated += 1
                print(f"  {key:40s} {wiki_url}")
            else:
                no_wiki.append(key)

    print(f"\nAdded wikipedia_url to {updated}/{len(topics)} CurriculumTopics")
    if no_wiki:
        print(f"No Wikipedia article ({len(no_wiki)}): {no_wiki}")

    driver.close()


if __name__ == "__main__":
    main()
