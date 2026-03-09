#!/usr/bin/env python3
"""
Sample 5 disciplines: fetch forward links (claims) and backlinks,
then check P31 (instance of) on linked items. Exclude persons.
"""
import requests
import time
import json
from collections import Counter

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "ChrystallumBot/1.0 (research project)"

# 5 diverse disciplines from the 675
SAMPLES = [
    ("Q11190", "medicine"),
    ("Q413", "physics"),
    ("Q8134", "economics"),
    ("Q11634", "art history"),
    ("Q7150", "ecology"),
]


def sparql(query):
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    for attempt in range(3):
        r = requests.get(SPARQL_URL, params={"query": query}, headers=headers, timeout=120)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            time.sleep((attempt + 1) * 10)
        else:
            time.sleep(5)
    return None


def analyze_discipline(qid, label):
    print(f"\n{'='*70}")
    print(f"  {label} ({qid})")
    print(f"{'='*70}")

    # Forward links: what properties does this discipline have?
    print(f"\n  FORWARD LINKS (claims on {qid}):")
    fwd = sparql(f"""
        SELECT ?prop ?propLabel ?val ?valLabel WHERE {{
          wd:{qid} ?p ?val .
          ?prop wikibase:directClaim ?p .
          FILTER(isIRI(?val))
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 50
    """)
    if fwd:
        for b in fwd["results"]["bindings"]:
            prop_label = b.get("propLabel", {}).get("value", "?")
            val_label = b.get("valLabel", {}).get("value", "?")
            val_uri = b.get("val", {}).get("value", "")
            val_qid = val_uri.split("/")[-1] if val_uri else ""
            print(f"    {prop_label:30s} → {val_label} ({val_qid})")
    time.sleep(1)

    # Backlinks: what items link TO this discipline? Get P31 types. Exclude humans.
    print(f"\n  BACKLINKS (items linking to {qid}, excl. persons):")
    back = sparql(f"""
        SELECT ?item ?itemLabel ?prop ?propLabel ?type ?typeLabel WHERE {{
          ?item ?p wd:{qid} .
          ?prop wikibase:directClaim ?p .
          OPTIONAL {{ ?item wdt:P31 ?type . }}
          FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q5 . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 200
    """)

    if back:
        bindings = back["results"]["bindings"]
        print(f"    {len(bindings)} backlinks (capped at 200)")

        # Count by linking property
        prop_counts = Counter()
        for b in bindings:
            pl = b.get("propLabel", {}).get("value", "?")
            prop_counts[pl] += 1
        print(f"\n    By linking property:")
        for prop, count in prop_counts.most_common(15):
            print(f"      {prop:35s} {count}")

        # Count by P31 type of linking item
        type_counts = Counter()
        for b in bindings:
            tl = b.get("typeLabel", {}).get("value", "")
            if tl and not tl.startswith("http://"):
                type_counts[tl] += 1
            elif not tl:
                type_counts["(no P31)"] += 1
        print(f"\n    By instance-of type of linking items:")
        for t, count in type_counts.most_common(20):
            print(f"      {t:45s} {count}")

        # Show 10 sample backlinks
        print(f"\n    Sample backlinks:")
        seen = set()
        for b in bindings[:30]:
            il = b.get("itemLabel", {}).get("value", "?")
            iu = b.get("item", {}).get("value", "")
            iq = iu.split("/")[-1] if iu else ""
            pl = b.get("propLabel", {}).get("value", "?")
            tl = b.get("typeLabel", {}).get("value", "?")
            if iq not in seen:
                seen.add(iq)
                print(f"      {il:40s} ({iq}) via {pl:20s} [type: {tl}]")
            if len(seen) >= 10:
                break
    time.sleep(2)


def main():
    for qid, label in SAMPLES:
        analyze_discipline(qid, label)
        time.sleep(1)


if __name__ == "__main__":
    main()
