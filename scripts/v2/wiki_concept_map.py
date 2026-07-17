#!/usr/bin/env python3
"""Harvest concepts (nouns) from Wikipedia articles for CurriculumTopics.

Extracts all internal [[links]] grouped by section, resolves to QIDs.
No classification — that's done by classify_concept_map.py.

Run:
  python scripts/v2/wiki_concept_map.py Human_migration
  python scripts/v2/wiki_concept_map.py --all
"""
import sys, json, re, time, argparse
import urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

NOISE_PREFIXES = ["File:", "Category:", "Image:", "#"]
NOISE_TITLES = {
    "Academic Press", "Routledge", "Palgrave Macmillan", "Oxford University Press",
    "Pantheon Books", "Stanford University Press", "Edward Elgar Publishing",
    "Google Books", "Cambridge University Press", "Springer Science+Business Media",
    "Bibcode (identifier)", "Doi (identifier)", "Hdl (identifier)",
    "ISBN (identifier)", "ISSN (identifier)", "JSTOR (identifier)",
    "PMID (identifier)", "S2CID (identifier)", "Wayback Machine",
    "The Economist", "The New York Times",
}

SKIP_SECTIONS = {
    "References", "Sources and further reading", "Journals",
    "External links", "Research contributions", "Notes",
    "Bibliography", "Further reading", "See also",
}


def fetch_article_links(title):
    """Fetch wikitext and extract section-grouped internal links (ordered)."""
    url = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=parse&page={urllib.parse.quote(title)}"
        "&prop=wikitext&format=json"
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "Chrystallum/2.0 (research)"}
    )
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    wikitext = data["parse"]["wikitext"]["*"]

    sections = re.split(r"(={2,}[^=]+={2,})", wikitext)
    current_section = "Lead"
    section_links = {}

    for part in sections:
        header_match = re.match(r"={2,}\s*(.+?)\s*={2,}", part)
        if header_match:
            current_section = header_match.group(1).strip()
            continue

        if current_section in SKIP_SECTIONS:
            continue

        links = re.findall(r"\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]", part)
        clean = []
        for l in links:
            l = l.split("#")[0].strip()
            if not l:
                continue
            if any(l.startswith(p) for p in NOISE_PREFIXES):
                continue
            if l in NOISE_TITLES:
                continue
            clean.append(l)

        if clean:
            if current_section not in section_links:
                section_links[current_section] = []
            section_links[current_section].extend(clean)

    return section_links


def resolve_qids(titles):
    """Batch resolve Wikipedia article titles to Wikidata QIDs."""
    qid_map = {}
    title_list = list(titles)
    for i in range(0, len(title_list), 50):
        batch = title_list[i : i + 50]
        titles_param = "|".join(batch)
        url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&titles={urllib.parse.quote(titles_param)}"
            "&prop=pageprops&ppprop=wikibase_item&format=json"
        )
        req = urllib.request.Request(
            url, headers={"User-Agent": "Chrystallum/2.0 (research)"}
        )
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            pages = data.get("query", {}).get("pages", {})
            normalized = {}
            for n in data.get("query", {}).get("normalized", []):
                normalized[n["from"]] = n["to"]

            for page_id, page_data in pages.items():
                if int(page_id) < 0:
                    continue
                title = page_data.get("title", "")
                qid = page_data.get("pageprops", {}).get("wikibase_item")
                if qid:
                    qid_map[title] = qid
                    for orig, norm in normalized.items():
                        if norm == title:
                            qid_map[orig] = qid
        except Exception as e:
            print(f"  QID batch error: {e}")
        time.sleep(0.3)

    return qid_map


def harvest_page(page_name):
    """Harvest one Wikipedia page. Returns output dict or None on error."""
    title = page_name.replace("_", " ")

    try:
        section_links = fetch_article_links(page_name)
    except Exception as e:
        print(f"  ERROR fetching {page_name}: {e}")
        return None

    total_links = sum(len(v) for v in section_links.values())

    # Collect unique concepts (deduplicated per-section, preserving order)
    all_concepts = set()
    sections_out = {}
    for section, links in section_links.items():
        seen = set()
        unique = []
        for l in links:
            if l not in seen:
                seen.add(l)
                unique.append(l)
        all_concepts.update(unique)
        sections_out[section] = unique

    # Include root concept
    all_concepts.add(title)

    # Resolve QIDs
    qid_map = resolve_qids(all_concepts)
    resolved = sum(1 for t in all_concepts if t in qid_map)

    output = {
        "page": title,
        "page_name": page_name,
        "url": f"https://en.wikipedia.org/wiki/{page_name}",
        "root_qid": qid_map.get(title),
        "sections": sections_out,
        "concepts": sorted(
            [{"name": c, "qid": qid_map.get(c)} for c in all_concepts],
            key=lambda x: x["name"],
        ),
        "stats": {
            "total_concepts": len(all_concepts),
            "qid_resolved": resolved,
            "sections": len(sections_out),
            "raw_links": total_links,
        },
    }

    return output


def get_all_pages():
    """Query Neo4j for all CurriculumTopics with wikipedia_url."""
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as s:
        r = s.run(
            "MATCH (ct:CurriculumTopic) "
            "WHERE ct.wikipedia_url IS NOT NULL "
            "RETURN ct.key AS key, ct.wikipedia_url AS url "
            "ORDER BY ct.key"
        )
        pages = []
        for row in r:
            page_name = row["url"].split("/wiki/")[-1]
            pages.append({"key": row["key"], "page_name": page_name})
    driver.close()
    return pages


def main():
    parser = argparse.ArgumentParser(description="Wikipedia concept harvester")
    parser.add_argument("page", nargs="?", help="Wikipedia page title (e.g. Human_migration)")
    parser.add_argument("--all", action="store_true", help="Harvest all CurriculumTopics")
    args = parser.parse_args()

    sys.stdout.reconfigure(errors="replace")

    out_dir = ROOT / "output" / "wiki_concept_maps"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        pages = get_all_pages()
        print(f"Harvesting {len(pages)} CurriculumTopics\n")

        results = []
        for i, p in enumerate(pages):
            existing = out_dir / f"{p['page_name']}.json"
            if existing.exists():
                print(f"[{i+1:02d}/{len(pages)}] {p['key']:45s} SKIP (exists)")
                results.append({"key": p["key"], "status": "exists"})
                continue

            print(f"[{i+1:02d}/{len(pages)}] {p['key']:45s} {p['page_name']}")
            output = harvest_page(p["page_name"])
            if output:
                out_path = out_dir / f"{p['page_name']}.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                s = output["stats"]
                print(f"  {s['total_concepts']} concepts, {s['qid_resolved']} QIDs ({s['sections']} sections)")
                results.append({"key": p["key"], "status": "ok", "concepts": s["total_concepts"], "qids": s["qid_resolved"]})
            else:
                results.append({"key": p["key"], "status": "error"})

            time.sleep(0.5)  # respect Wikipedia rate limits

        # Summary
        ok = sum(1 for r in results if r["status"] in ("ok", "exists"))
        err = sum(1 for r in results if r["status"] == "error")
        print(f"\nDone: {ok} harvested, {err} errors")

    elif args.page:
        print(f"Fetching article: {args.page.replace('_', ' ')}")
        output = harvest_page(args.page)
        if output:
            s = output["stats"]
            print(f"  {s['total_concepts']} concepts, {s['qid_resolved']} QIDs ({s['sections']} sections)")
            out_path = out_dir / f"{args.page}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"Saved to {out_path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
