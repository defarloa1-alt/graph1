#!/usr/bin/env python3
"""
Sample 30 instances of Q5 (human) from Wikidata and catalog:
- All properties (with counts across sample)
- All external identifier properties (with counts)

Focuses on historical / classical figures relevant to Chrystallum.
"""
import json
import time
import requests
from collections import Counter, defaultdict
from pathlib import Path

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "ChrystallumBot/1.0 (research project)"

# 30 diverse historical humans — mix of Roman, Greek, medieval, modern scholars
SAMPLE_QIDS = [
    "Q1048",    # Julius Caesar
    "Q1405",    # Augustus
    "Q2263",    # Cicero
    "Q2657",    # Pompey
    "Q5608",    # Cato the Elder
    "Q44398",   # Scipio Africanus
    "Q189974",  # Sulla
    "Q193945",  # Marcus Crassus
    "Q170072",  # Marius
    "Q166092",  # Brutus
    "Q8685",    # Nero
    "Q1726",    # Marcus Aurelius
    "Q868",     # Aristotle
    "Q859",     # Plato
    "Q10261",   # Thucydides
    "Q36303",   # Plutarch
    "Q42207",   # Tacitus
    "Q1067",    # Virgil
    "Q104740",  # Livy
    "Q182589",  # Polybius
    "Q7200",    # Alexander the Great
    "Q5601",    # Hannibal
    "Q8011",    # Charlemagne
    "Q1001",    # Mahatma Gandhi
    "Q937",     # Albert Einstein
    "Q7186",    # Marie Curie
    "Q9438",    # Theodor Mommsen (historian)
    "Q61085",   # Ronald Syme (historian)
    "Q1065",    # Seneca
    "Q41155",   # Sallust
]

# Property classification: which PIDs are external identifiers
# We'll use the Wikidata property type to determine this


def fetch_all_statements(qid):
    """Fetch all property IDs and their types for a QID."""
    query = f"""
    SELECT ?prop ?propLabel ?val ?valLabel WHERE {{
      wd:{qid} ?p ?statement .
      ?statement ?ps ?val .
      ?prop wikibase:claim ?p .
      ?prop wikibase:statementProperty ?ps .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 500
    """
    try:
        r = requests.get(
            SPARQL_URL,
            params={"query": query, "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()["results"]["bindings"]
    except Exception as e:
        print(f"    Error fetching {qid}: {e}")
    return []


def fetch_external_id_pids():
    """Fetch all Wikidata properties that are external identifiers."""
    query = """
    SELECT ?prop ?propLabel WHERE {
      ?prop wikibase:propertyType wikibase:ExternalId .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    try:
        r = requests.get(
            SPARQL_URL,
            params={"query": query, "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=60,
        )
        if r.status_code == 200:
            pids = set()
            for b in r.json()["results"]["bindings"]:
                pid = b["prop"]["value"].split("/")[-1]
                pids.add(pid)
            return pids
    except Exception as e:
        print(f"  Error fetching external ID list: {e}")
    return set()


def main():
    print("Fetching external identifier PID list from Wikidata...")
    ext_id_pids = fetch_external_id_pids()
    print(f"  {len(ext_id_pids)} external identifier properties known\n")

    prop_counter = Counter()       # PID -> count of humans that have it
    ext_id_counter = Counter()     # PID -> count of humans that have it
    prop_labels = {}               # PID -> label
    prop_samples = defaultdict(list)  # PID -> sample values

    for i, qid in enumerate(SAMPLE_QIDS):
        print(f"  [{i+1:2d}/30] Fetching {qid}...", end=" ")
        bindings = fetch_all_statements(qid)

        # Dedupe properties per person
        seen_pids = set()
        for b in bindings:
            pid = b["prop"]["value"].split("/")[-1]
            plabel = b.get("propLabel", {}).get("value", pid)
            prop_labels[pid] = plabel

            if pid not in seen_pids:
                seen_pids.add(pid)
                prop_counter[pid] += 1
                if pid in ext_id_pids:
                    ext_id_counter[pid] += 1

            # Collect sample values (first 2 per property)
            if len(prop_samples[pid]) < 2:
                val = b.get("val", {}).get("value", "")
                vlabel = b.get("valLabel", {}).get("value", "")
                if vlabel and vlabel != val:
                    prop_samples[pid].append(f"{vlabel} ({val})" if "wikidata" in val else vlabel)
                else:
                    prop_samples[pid].append(val.split("/")[-1] if "wikidata" in val else val[:60])

        print(f"{len(seen_pids)} properties, {sum(1 for p in seen_pids if p in ext_id_pids)} ext IDs")
        time.sleep(1.5)

    # === REPORT ===
    print("\n" + "=" * 90)
    print(f"PROPERTY SURVEY — 30 sampled humans")
    print("=" * 90)

    print(f"\n{'PID':<10} {'Label':<40} {'Count':>5}  Sample values")
    print("-" * 90)
    for pid, cnt in prop_counter.most_common():
        if pid in ext_id_pids:
            continue  # show separately
        label = prop_labels.get(pid, pid)[:40]
        samples = " | ".join(prop_samples.get(pid, [])[:2])[:50]
        safe = lambda s: s.encode("ascii", "replace").decode("ascii")
        print(f"{pid:<10} {safe(label):<40} {cnt:>5}  {safe(samples)}")

    print(f"\n{'=' * 90}")
    print(f"EXTERNAL IDENTIFIERS -- found on sampled humans")
    print("=" * 90)
    print(f"\n{'PID':<10} {'Label':<40} {'Count':>5}  Sample values")
    print("-" * 90)
    for pid, cnt in ext_id_counter.most_common():
        label = prop_labels.get(pid, pid)[:40]
        samples = " | ".join(prop_samples.get(pid, [])[:2])[:50]
        safe = lambda s: s.encode("ascii", "replace").decode("ascii")
        print(f"{pid:<10} {safe(label):<40} {cnt:>5}  {safe(samples)}")

    # Summary
    total_props = len(prop_counter)
    total_ext = len(ext_id_counter)
    high_coverage_ext = sum(1 for _, c in ext_id_counter.items() if c >= 15)

    print(f"\n--- Summary ---")
    print(f"  Total distinct properties: {total_props}")
    print(f"  Total distinct external IDs: {total_ext}")
    print(f"  External IDs on 50%+ of sample: {high_coverage_ext}")
    print(f"  Properties on ALL 30: {sum(1 for _, c in prop_counter.items() if c == 30)}")

    # Save raw data
    out = Path(__file__).resolve().parents[2] / "output" / "human_property_survey.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "sample_size": 30,
        "qids": SAMPLE_QIDS,
        "properties": {pid: {"label": prop_labels.get(pid, ""), "count": cnt, "is_external_id": pid in ext_id_pids}
                       for pid, cnt in prop_counter.most_common()},
        "external_ids": {pid: {"label": prop_labels.get(pid, ""), "count": cnt}
                         for pid, cnt in ext_id_counter.most_common()},
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out.name}")


if __name__ == "__main__":
    main()
