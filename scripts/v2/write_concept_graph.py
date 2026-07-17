#!/usr/bin/env python3
"""Write all classified concept maps to Neo4j (Chrystal 2.0).

Replaces the inline write_to_graph in classify_concept_map.py with
improved CT linking (matches by root_qid instead of URL).

Run:
  python scripts/v2/write_concept_graph.py
  python scripts/v2/write_concept_graph.py --clean   # delete existing WikiConcept layer first
"""
import sys, json, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase


def main():
    parser = argparse.ArgumentParser(description="Write concept maps to Neo4j")
    parser.add_argument("--clean", action="store_true", help="Delete existing WikiConcept nodes first")
    parser.add_argument("--dry-run", action="store_true", help="Show stats without writing")
    args = parser.parse_args()

    sys.stdout.reconfigure(errors="replace")

    out_dir = ROOT / "output" / "wiki_concept_maps"
    classified_files = sorted(out_dir.glob("*_classified.json"))
    print(f"Found {len(classified_files)} classified files\n")

    # Load all classified data
    all_data = []
    for cf in classified_files:
        data = json.load(open(cf, encoding="utf-8"))
        root_qid = data.get("root_qid")
        page_name = data.get("page_name", cf.stem.replace("_classified", ""))
        kept = [r for r in data["classified"] if r["predicate"] != "DROP" and r.get("qid")]
        all_data.append({
            "file": cf,
            "root_qid": root_qid,
            "root_name": data["page"],
            "page_name": page_name,
            "kept": kept,
        })

    # Stats
    with_qid = [d for d in all_data if d["root_qid"]]
    total_kept = sum(len(d["kept"]) for d in with_qid)
    unique_qids = set()
    for d in with_qid:
        unique_qids.add(d["root_qid"])
        for r in d["kept"]:
            unique_qids.add(r["qid"])

    print(f"Pages with root QID: {len(with_qid)}/{len(all_data)}")
    print(f"Total kept concepts: {total_kept}")
    print(f"Unique WikiConcept QIDs: {len(unique_qids)}")

    if args.dry_run:
        # Show pages without root_qid
        no_qid = [d for d in all_data if not d["root_qid"]]
        if no_qid:
            print(f"\nPages WITHOUT root_qid ({len(no_qid)}):")
            for d in no_qid:
                print(f"  {d['page_name']}")
        return

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    if args.clean:
        print("\nCleaning existing WikiConcept layer...")
        with driver.session() as s:
            result = s.run("MATCH (wc:WikiConcept) DETACH DELETE wc RETURN count(wc) AS deleted")
            row = result.single()
            print(f"  Deleted {row['deleted']} WikiConcept nodes")

    print("\nWriting to graph...")
    total_nodes = 0
    total_edges = 0
    total_ct_links = 0

    with driver.session() as s:
        for d in with_qid:
            if not d["kept"]:
                continue

            # Root WikiConcept
            s.run(
                "MERGE (wc:WikiConcept {qid: $qid}) "
                "SET wc.name = $name, "
                "    wc.qid_url = 'https://www.wikidata.org/wiki/' + $qid",
                qid=d["root_qid"], name=d["root_name"],
            )

            # Concept nodes + RELATED edges
            for r in d["kept"]:
                s.run(
                    "MERGE (wc:WikiConcept {qid: $qid}) "
                    "SET wc.name = $name, "
                    "    wc.qid_url = 'https://www.wikidata.org/wiki/' + $qid",
                    qid=r["qid"], name=r["name"],
                )
                total_nodes += 1

                s.run(
                    "MATCH (hub:WikiConcept {qid: $root_qid}) "
                    "MATCH (c:WikiConcept {qid: $cqid}) "
                    "MERGE (hub)-[rel:RELATED]->(c) "
                    "SET rel.predicate = $predicate, "
                    "    rel.source = 'wikipedia', "
                    "    rel.article = $article",
                    root_qid=d["root_qid"], cqid=r["qid"],
                    predicate=r["predicate"], article=d["root_name"],
                )
                total_edges += 1

            # Link CurriculumTopic -> WikiConcept hub via root_qid
            # Try URL match first, then try matching by wikipedia_url pattern
            page_name = d["page_name"]
            urls_to_try = [
                f"https://en.wikipedia.org/wiki/{page_name}",
            ]

            linked = False
            for url in urls_to_try:
                result = s.run(
                    "MATCH (ct:CurriculumTopic {wikipedia_url: $url}) "
                    "MATCH (wc:WikiConcept {qid: $root_qid}) "
                    "MERGE (ct)-[:HAS_CONCEPT_MAP]->(wc) "
                    "RETURN ct.key AS key",
                    url=url, root_qid=d["root_qid"],
                )
                row = result.single()
                if row:
                    total_ct_links += 1
                    linked = True
                    break

            status = "linked" if linked else "NO CT"
            print(f"  {d['page_name']:50s} kept={len(d['kept']):3d} {status}")

    # Also try linking by CONTAINS pattern on url suffix
    # For CTs whose wikipedia_url has encoding differences
    print("\nAttempting fuzzy CT linking for unlinked pages...")
    with driver.session() as s:
        result = s.run(
            "MATCH (ct:CurriculumTopic) "
            "WHERE ct.wikipedia_url IS NOT NULL "
            "AND NOT (ct)-[:HAS_CONCEPT_MAP]->() "
            "RETURN ct.key AS key, ct.wikipedia_url AS url"
        )
        unlinked_cts = [(row["key"], row["url"]) for row in result]

    if unlinked_cts:
        print(f"  {len(unlinked_cts)} CTs still unlinked:")
        with driver.session() as s:
            for key, url in unlinked_cts:
                # Extract page name from URL and try to find matching WikiConcept
                page = url.split("/wiki/")[-1]
                # Try finding classified data for this page
                matching = [d for d in with_qid if d["page_name"] == page]
                if matching:
                    d = matching[0]
                    s.run(
                        "MATCH (ct:CurriculumTopic {key: $key}) "
                        "MATCH (wc:WikiConcept {qid: $root_qid}) "
                        "MERGE (ct)-[:HAS_CONCEPT_MAP]->(wc) "
                        "RETURN ct.key",
                        key=key, root_qid=d["root_qid"],
                    )
                    total_ct_links += 1
                    print(f"    {key:45s} -> {d['root_qid']} (matched by page_name)")
                else:
                    print(f"    {key:45s} STILL UNLINKED ({page})")

    driver.close()

    print(f"\nGraph totals:")
    print(f"  WikiConcept nodes created/updated: {total_nodes}")
    print(f"  RELATED edges created/updated:     {total_edges}")
    print(f"  HAS_CONCEPT_MAP CT links:          {total_ct_links}")


if __name__ == "__main__":
    main()
