#!/usr/bin/env python3
"""Classify harvested WikiConcepts via Claude LLM into hub-spoke predicates.

Takes noun harvest JSON from wiki_concept_map.py and classifies each concept's
relationship to the hub (root) concept.

Run:
  python scripts/v2/classify_concept_map.py Political_science
  python scripts/v2/classify_concept_map.py --all
  python scripts/v2/classify_concept_map.py --all --write-graph
"""
import sys, json, time, argparse
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

PREDICATES = {
    "HAS_SUBTYPE":     "subtypes, variants, forms, subfields, branches",
    "HAS_THEORY":      "theories, models, frameworks, paradigms, schools of thought",
    "HAS_METHOD":      "research methods, methodologies, analytical techniques",
    "HAS_FIGURE":      "notable scholars, thinkers, historical figures",
    "HAS_INSTITUTION": "organizations, associations, agencies, universities",
    "HAS_INSTRUMENT":  "laws, treaties, conventions, norms, governance mechanisms",
    "HAS_PUBLICATION": "journals, reports, datasets, key texts",
    "HAS_CONTEXT":     "historical periods, intellectual movements, related disciplines",
    "HAS_COMPONENT":   "core concepts, building blocks, key terms within the topic",
    "DRIVEN_BY":       "causes, drivers, enabling factors",
    "DROP":            "noise: geographic examples, unrelated concepts, too generic",
}


def classify_concepts(root_name, concept_names, chunk_size=200):
    """Send concept list to Claude for hub-predicate classification.

    Chunks large lists to avoid JSON parse errors on huge responses.
    """
    import anthropic

    client = anthropic.Anthropic()
    pred_desc = "\n".join(f"- {k}: {v}" for k, v in PREDICATES.items())

    all_results = []
    chunks = [concept_names[i:i+chunk_size] for i in range(0, len(concept_names), chunk_size)]

    for ci, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"(chunk {ci+1}/{len(chunks)}) ", end="", flush=True)

        prompt = (
            f'You are classifying concepts extracted from the Wikipedia article "{root_name}".\n\n'
            f"For each concept, assign exactly ONE predicate describing its relationship "
            f'to the hub concept "{root_name}".\n\n'
            f"Available predicates:\n{pred_desc}\n\n"
            f"Rules:\n"
            f"- The hub concept itself should be DROP\n"
            f"- Countries/cities used as examples should be DROP\n"
            f"- Generic science terms (physics, biology) unrelated to the topic should be DROP\n"
            f"- Prefer HAS_COMPONENT for core domain concepts that are neither subtypes nor methods\n"
            f"- HAS_THEORY is for named theoretical frameworks, not general concepts\n"
            f"- HAS_FIGURE is for real people only\n\n"
            f"Return ONLY a JSON array of objects with \"name\" and \"predicate\" keys.\n\n"
            f"Concepts:\n{json.dumps(chunk)}"
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]

        all_results.extend(json.loads(text))
        if len(chunks) > 1 and ci < len(chunks) - 1:
            time.sleep(1)

    return all_results


def classify_page(page_name, out_dir):
    """Classify one page's concepts. Returns output dict or None."""
    map_path = out_dir / f"{page_name}.json"
    if not map_path.exists():
        print(f"  No harvest for {page_name}")
        return None

    with open(map_path, encoding="utf-8") as f:
        data = json.load(f)

    root_name = data["page"]
    root_qid = data.get("root_qid")
    concepts = [c for c in data["concepts"] if c["qid"]]
    concept_names = [c["name"] for c in concepts]

    if not concept_names:
        print(f"  No QID-resolved concepts")
        return None

    # Classify
    classified = classify_concepts(root_name, concept_names)

    # Build lookup
    pred_map = {c["name"]: c["predicate"] for c in classified}

    # Merge with QIDs
    results = []
    for c in concepts:
        pred = pred_map.get(c["name"], "DROP")
        results.append({"name": c["name"], "qid": c["qid"], "predicate": pred})

    # Stats
    by_pred = {}
    for r in results:
        by_pred.setdefault(r["predicate"], []).append(r)

    kept = [r for r in results if r["predicate"] != "DROP"]
    dropped = [r for r in results if r["predicate"] == "DROP"]

    output = {
        "page": root_name,
        "page_name": page_name,
        "root_qid": root_qid,
        "classified": results,
        "stats": {
            "total": len(results),
            "kept": len(kept),
            "dropped": len(dropped),
            "by_predicate": {k: len(v) for k, v in by_pred.items()},
        },
    }

    return output


def write_to_graph(classified_files):
    """Write all classified concept maps to Neo4j."""
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    total_nodes = 0
    total_edges = 0
    total_ct_links = 0

    with driver.session() as s:
        for cf in classified_files:
            with open(cf, encoding="utf-8") as f:
                data = json.load(f)

            root_qid = data.get("root_qid")
            root_name = data["page"]
            page_name = data.get("page_name", cf.stem.replace("_classified", ""))
            kept = [r for r in data["classified"] if r["predicate"] != "DROP"]

            if not root_qid or not kept:
                continue

            # Root concept
            s.run(
                "MERGE (wc:WikiConcept {qid: $qid}) "
                "SET wc.name = $name, "
                "    wc.qid_url = 'https://www.wikidata.org/wiki/' + $qid",
                qid=root_qid, name=root_name,
            )

            # Concept nodes + edges
            for r in kept:
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
                    "MERGE (hub)-[r:RELATED]->(c) "
                    "SET r.predicate = $predicate, "
                    "    r.source = 'wikipedia', "
                    "    r.article = $article",
                    root_qid=root_qid, cqid=r["qid"],
                    predicate=r["predicate"], article=root_name,
                )
                total_edges += 1

            # Link to CurriculumTopic
            result = s.run(
                "MATCH (ct:CurriculumTopic {wikipedia_url: $url}) "
                "MATCH (wc:WikiConcept {qid: $root_qid}) "
                "MERGE (ct)-[:HAS_CONCEPT_MAP]->(wc) "
                "RETURN ct.key AS key",
                url=f"https://en.wikipedia.org/wiki/{page_name}",
                root_qid=root_qid,
            )
            row = result.single()
            if row:
                total_ct_links += 1

    driver.close()
    return total_nodes, total_edges, total_ct_links


def main():
    parser = argparse.ArgumentParser(description="Classify concept maps via LLM")
    parser.add_argument("page", nargs="?", help="Page name matching the harvest JSON")
    parser.add_argument("--all", action="store_true", help="Classify all harvested pages")
    parser.add_argument("--write-graph", action="store_true", help="Write to Neo4j")
    parser.add_argument("--force", action="store_true", help="Re-classify even if output exists")
    args = parser.parse_args()

    sys.stdout.reconfigure(errors="replace")

    out_dir = ROOT / "output" / "wiki_concept_maps"

    if args.all:
        # Find all harvested pages (exclude _classified files)
        harvest_files = sorted(out_dir.glob("*.json"))
        harvest_files = [f for f in harvest_files if "_classified" not in f.name]

        print(f"Found {len(harvest_files)} harvested pages\n")

        classified_files = []
        for i, hf in enumerate(harvest_files):
            page_name = hf.stem
            cls_path = out_dir / f"{page_name}_classified.json"

            if cls_path.exists() and not args.force:
                print(f"[{i+1:02d}/{len(harvest_files)}] {page_name:45s} SKIP (classified)")
                classified_files.append(cls_path)
                continue

            print(f"[{i+1:02d}/{len(harvest_files)}] {page_name:45s} ", end="", flush=True)
            try:
                output = classify_page(page_name, out_dir)
                if output:
                    with open(cls_path, "w", encoding="utf-8") as f:
                        json.dump(output, f, indent=2, ensure_ascii=False)
                    s = output["stats"]
                    print(f"kept={s['kept']} dropped={s['dropped']}")
                    classified_files.append(cls_path)
                else:
                    print("SKIP (no data)")
            except Exception as e:
                print(f"ERROR: {e}")

            time.sleep(1)  # rate limit Claude API

        # Summary
        print(f"\nClassified: {len(classified_files)} pages")

        if args.write_graph and classified_files:
            print(f"\nWriting to graph...")
            nodes, edges, ct_links = write_to_graph(classified_files)
            print(f"Graph: {nodes} WikiConcept nodes, {edges} RELATED edges, {ct_links} CT links")

    elif args.page:
        print(f"Classifying: {args.page}")
        output = classify_page(args.page, out_dir)
        if output:
            # Print results
            by_pred = {}
            for r in output["classified"]:
                by_pred.setdefault(r["predicate"], []).append(r)

            for pred, items in sorted(by_pred.items()):
                if pred == "DROP":
                    continue
                print(f"\n  {pred} ({len(items)}):")
                for r in items:
                    print(f"    {r['name']:45s} {r['qid']}")

            dropped = by_pred.get("DROP", [])
            if dropped:
                print(f"\n  DROP ({len(dropped)}): {', '.join(r['name'] for r in dropped[:10])}")

            cls_path = out_dir / f"{args.page}_classified.json"
            with open(cls_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"\nSaved to {cls_path}")

            if args.write_graph:
                nodes, edges, ct_links = write_to_graph([cls_path])
                print(f"Graph: {nodes} WikiConcept nodes, {edges} RELATED edges, {ct_links} CT links")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
