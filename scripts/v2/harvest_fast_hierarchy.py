#!/usr/bin/env python3
"""Harvest broader-than and related-term edges from FAST authority records.

For each CurriculumTopic's fast_id, fetches the RDF record from OCLC and
extracts skos:broader and skos:related relationships. When a target FAST ID
matches another CurriculumTopic, creates a graph edge.

Also stores raw harvest data for targets that don't match our topics
(useful for future expansion).

Edges created:
  (CurriculumTopic)-[:BROADER_THAN]->(CurriculumTopic)   — from skos:broader
  (CurriculumTopic)-[:RELATED_TO]->(CurriculumTopic)     — from skos:related

Run:
  python scripts/v2/harvest_fast_hierarchy.py
  python scripts/v2/harvest_fast_hierarchy.py --dry-run   # preview only
"""
import sys, json, time, re, argparse
import xml.etree.ElementTree as ET
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

FAST_RDF_URL = "https://id.worldcat.org/fast/{}"
HEADERS = {"Accept": "application/rdf+xml", "User-Agent": "Chrystallum/2.0 (research)"}

SKOS = "http://www.w3.org/2004/02/skos/core#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"


def fetch_rdf(fast_num):
    """Fetch RDF/XML for a FAST number (integer, no leading zeros)."""
    url = FAST_RDF_URL.format(fast_num)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read()
    except urllib.error.HTTPError as e:
        print(f"    HTTP {e.code} for FAST {fast_num}")
        return None
    except Exception as e:
        print(f"    Error fetching FAST {fast_num}: {e}")
        return None


def parse_relations(xml_bytes):
    """Extract broader, related, and relatedMatch from FAST RDF/XML."""
    root = ET.fromstring(xml_bytes)
    result = {"broader": [], "related": [], "wikidata_matches": []}

    for elem in root.iter(f"{{{SKOS}}}broader"):
        desc = elem.find(f"{{{RDF}}}Description")
        if desc is not None:
            about = desc.get(f"{{{RDF}}}about", "")
            label_el = desc.find(f"{{{RDFS}}}label")
            label = label_el.text if label_el is not None else ""
            # about is just the FAST number (e.g. "902116")
            fast_num = about.split("/")[-1] if "/" in about else about
            result["broader"].append({"fast_num": fast_num, "label": label})

    for elem in root.iter(f"{{{SKOS}}}related"):
        desc = elem.find(f"{{{RDF}}}Description")
        if desc is not None:
            about = desc.get(f"{{{RDF}}}about", "")
            label_el = desc.find(f"{{{RDFS}}}label")
            label = label_el.text if label_el is not None else ""
            fast_num = about.split("/")[-1] if "/" in about else about
            result["related"].append({"fast_num": fast_num, "label": label})

    for elem in root.iter(f"{{{SKOS}}}relatedMatch"):
        desc = elem.find(f"{{{RDF}}}Description")
        if desc is not None:
            about = desc.get(f"{{{RDF}}}about", "")
            if "wikidata.org" in about:
                qid = about.split("/")[-1]
                result["wikidata_matches"].append(qid)

    return result


def load_topics_from_graph(driver):
    """Load all CurriculumTopics with their fast_id from the graph."""
    with driver.session() as s:
        r = s.run("""
            MATCH (ct:CurriculumTopic)
            WHERE ct.fast_id IS NOT NULL
            RETURN ct.key AS key, ct.fast_id AS fast_id, ct.label AS label
        """)
        return [dict(row) for row in r]


def main():
    parser = argparse.ArgumentParser(description="Harvest FAST hierarchy")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no graph writes")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Load topics and build fast_num -> topic_key lookup
    topics = load_topics_from_graph(driver)
    print(f"Loaded {len(topics)} CurriculumTopics with FAST IDs")

    # Build lookup: fast_num (no prefix, no leading zeros) -> topic_key
    fast_to_key = {}
    for t in topics:
        fid = t["fast_id"]
        # fst01020874 -> 1020874
        num = str(int(fid.replace("fst", "")))
        fast_to_key[num] = t["key"]

    # Harvest
    all_harvest = {}
    internal_broader = []  # edges between our topics
    internal_related = []
    external_broader = []  # edges to concepts outside our topic set
    external_related = []
    wikidata_crosscheck = []

    for i, t in enumerate(topics):
        fast_num = str(int(t["fast_id"].replace("fst", "")))
        print(f"[{i+1:02d}/{len(topics)}] {t['key']:40s} FAST {fast_num}")

        xml = fetch_rdf(fast_num)
        if xml is None:
            continue

        rels = parse_relations(xml)
        all_harvest[t["key"]] = rels

        # Classify broader
        for bt in rels["broader"]:
            target_key = fast_to_key.get(bt["fast_num"])
            if target_key:
                internal_broader.append((t["key"], target_key, bt["label"]))
                print(f"    BT -> {target_key} ({bt['label']})")
            else:
                external_broader.append((t["key"], bt["fast_num"], bt["label"]))
                print(f"    BT -> [ext] {bt['fast_num']} ({bt['label']})")

        # Classify related
        for rt in rels["related"]:
            target_key = fast_to_key.get(rt["fast_num"])
            if target_key:
                internal_related.append((t["key"], target_key, rt["label"]))
                print(f"    RT -> {target_key} ({rt['label']})")
            else:
                external_related.append((t["key"], rt["fast_num"], rt["label"]))
                print(f"    RT -> [ext] {rt['fast_num']} ({rt['label']})")

        # Wikidata cross-check
        for qid in rels["wikidata_matches"]:
            wikidata_crosscheck.append((t["key"], qid))

        time.sleep(0.5)  # respect OCLC rate limits

    # Summary
    print(f"\n{'='*60}")
    print(f"HARVEST SUMMARY")
    print(f"{'='*60}")
    print(f"Topics harvested:     {len(all_harvest)}/{len(topics)}")
    print(f"Internal BROADER_THAN: {len(internal_broader)}")
    print(f"Internal RELATED_TO:   {len(internal_related)}")
    print(f"External broader:      {len(external_broader)}")
    print(f"External related:      {len(external_related)}")
    print(f"Wikidata cross-checks: {len(wikidata_crosscheck)}")

    if internal_broader:
        print(f"\n--- Internal BROADER_THAN edges ---")
        for src, tgt, label in internal_broader:
            print(f"  ({src}) -[:BROADER_THAN]-> ({tgt})  [{label}]")

    if internal_related:
        print(f"\n--- Internal RELATED_TO edges ---")
        for src, tgt, label in internal_related:
            print(f"  ({src}) -[:RELATED_TO]-> ({tgt})  [{label}]")

    if external_broader:
        print(f"\n--- External broader (not in our topics) ---")
        for src, fast_num, label in external_broader:
            print(f"  ({src}) -> FAST {fast_num} ({label})")

    if external_related:
        print(f"\n--- External related (not in our topics) ---")
        for src, fast_num, label in external_related:
            print(f"  ({src}) -> FAST {fast_num} ({label})")

    # Write to graph
    if not args.dry_run and (internal_broader or internal_related):
        print(f"\nWriting edges to graph...")
        with driver.session() as s:
            bt_count = 0
            for src, tgt, label in internal_broader:
                s.run("""
                    MATCH (a:CurriculumTopic {key: $src})
                    MATCH (b:CurriculumTopic {key: $tgt})
                    MERGE (a)-[r:BROADER_THAN]->(b)
                    SET r.source = 'fast_skos',
                        r.fast_label = $label
                """, src=src, tgt=tgt, label=label)
                bt_count += 1

            rt_count = 0
            for src, tgt, label in internal_related:
                s.run("""
                    MATCH (a:CurriculumTopic {key: $src})
                    MATCH (b:CurriculumTopic {key: $tgt})
                    MERGE (a)-[r:RELATED_TO]->(b)
                    SET r.source = 'fast_skos',
                        r.fast_label = $label
                """, src=src, tgt=tgt, label=label)
                rt_count += 1

            print(f"  Created {bt_count} BROADER_THAN + {rt_count} RELATED_TO edges")
    elif args.dry_run:
        print(f"\n[DRY RUN] No edges written.")

    # Save full harvest to JSON for reference
    out_path = ROOT / "output" / "fast_hierarchy_harvest.json"
    out_path.parent.mkdir(exist_ok=True)
    harvest_out = {
        "internal_broader": [{"src": s, "tgt": t, "label": l} for s, t, l in internal_broader],
        "internal_related": [{"src": s, "tgt": t, "label": l} for s, t, l in internal_related],
        "external_broader": [{"src": s, "fast_num": f, "label": l} for s, f, l in external_broader],
        "external_related": [{"src": s, "fast_num": f, "label": l} for s, f, l in external_related],
        "wikidata_crosscheck": [{"topic_key": k, "fast_qid": q} for k, q in wikidata_crosscheck],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(harvest_out, f, indent=2, ensure_ascii=False)
    print(f"\nFull harvest saved to {out_path}")

    driver.close()


if __name__ == "__main__":
    main()
