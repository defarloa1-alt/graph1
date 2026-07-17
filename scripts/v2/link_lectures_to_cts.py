#!/usr/bin/env python3
"""Link Lectures to CurriculumTopics via LLM classification.

For each CourseSyllabus, sends its lecture titles to Claude and asks
which CurriculumTopics each lecture covers.

Run:
  python scripts/v2/link_lectures_to_cts.py
  python scripts/v2/link_lectures_to_cts.py --dry-run
"""
import sys, json, time, argparse
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase


def get_ct_catalog(driver):
    """Get all CurriculumTopics with context for the LLM."""
    with driver.session() as s:
        r = s.run("""
            MATCH (f:Facet)-[:HAS_TOPIC]->(ct:CurriculumTopic)
            RETURN ct.key AS key, ct.label AS label, f.label AS facet,
                   ct.wikipedia_url AS wiki
            ORDER BY ct.key
        """)
        cts = []
        for row in r:
            wiki = row["wiki"].split("/wiki/")[-1].replace("_", " ") if row["wiki"] else ""
            cts.append({
                "key": row["key"],
                "label": row["label"] or row["key"],
                "facet": row["facet"],
                "wiki": wiki,
            })
    return cts


def get_syllabi(driver):
    """Get all syllabi with their lectures."""
    with driver.session() as s:
        # Lectures via modules
        r = s.run("""
            MATCH (cs:CourseSyllabus)
            OPTIONAL MATCH (cs)-[:HAS_MODULE]->(cm:CourseModule)-[:HAS_LECTURE]->(l1:Lecture)
            OPTIONAL MATCH (cs)-[:HAS_LECTURE]->(l2:Lecture)
            WITH cs, collect(DISTINCT {key: l1.key, title: l1.title, session: l1.session}) +
                      collect(DISTINCT {key: l2.key, title: l2.title, session: l2.session}) AS lectures
            RETURN cs.label AS label, cs.url AS url,
                   [l IN lectures WHERE l.key IS NOT NULL | l] AS lectures
            ORDER BY cs.label
        """)
        syllabi = []
        for row in r:
            # Deduplicate and sort
            seen = set()
            unique = []
            for l in row["lectures"]:
                if l["key"] not in seen:
                    seen.add(l["key"])
                    unique.append(l)
            unique.sort(key=lambda x: x["session"] or 0)
            syllabi.append({
                "label": row["label"],
                "url": row["url"],
                "lectures": unique,
            })
    return syllabi


def classify_lectures(syllabus, ct_catalog):
    """Ask Claude to map lectures to CurriculumTopics."""
    import anthropic

    ct_list = "\n".join(
        f"- {ct['key']}: {ct['facet']} / {ct['wiki'] or ct['label']}"
        for ct in ct_catalog
    )

    lecture_list = "\n".join(
        f"- session {l['session']}: {l['title']}"
        for l in syllabus["lectures"]
    )

    prompt = (
        f'You are mapping lecture topics from the course "{syllabus["label"]}" '
        f"to a set of CurriculumTopics in a historical knowledge graph.\n\n"
        f"CurriculumTopics (key: facet / subject):\n{ct_list}\n\n"
        f"Lectures:\n{lecture_list}\n\n"
        f"Rules:\n"
        f"- Each lecture may map to 1-3 CurriculumTopics (most relevant)\n"
        f"- Only assign CTs that genuinely match the lecture's subject matter\n"
        f"- Some lectures (introductions, reviews, exams) may map to 0 CTs — use empty array\n"
        f"- Prefer specific CTs over generic ones\n\n"
        f'Return ONLY a JSON array of objects with "session" (int) and "ct_keys" (string array) keys.'
    )

    client = anthropic.Anthropic()
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

    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description="Link lectures to CurriculumTopics")
    parser.add_argument("--dry-run", action="store_true", help="Classify but don't write")
    args = parser.parse_args()

    sys.stdout.reconfigure(errors="replace")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    ct_catalog = get_ct_catalog(driver)
    syllabi = get_syllabi(driver)

    print(f"CurriculumTopics: {len(ct_catalog)}")
    print(f"Syllabi: {len(syllabi)}")
    print()

    # Valid CT keys for validation
    valid_keys = {ct["key"] for ct in ct_catalog}

    all_mappings = []
    total_links = 0

    for si, syllabus in enumerate(syllabi):
        lcount = len(syllabus["lectures"])
        print(f"[{si+1:02d}/{len(syllabi)}] {syllabus['label']:60s} ({lcount} lectures) ", end="", flush=True)

        if not syllabus["lectures"]:
            print("SKIP (no lectures)")
            continue

        try:
            mappings = classify_lectures(syllabus, ct_catalog)

            # Build session->key lookup
            session_to_key = {l["session"]: l["key"] for l in syllabus["lectures"]}

            links = 0
            for m in mappings:
                ct_keys = [k for k in m.get("ct_keys", []) if k in valid_keys]
                lecture_key = session_to_key.get(m["session"])
                if lecture_key and ct_keys:
                    all_mappings.append({
                        "lecture_key": lecture_key,
                        "ct_keys": ct_keys,
                    })
                    links += len(ct_keys)

            total_links += links
            print(f"{links} links")

        except Exception as e:
            print(f"ERROR: {e}")

        time.sleep(1)

    print(f"\nTotal lecture->CT links: {total_links}")

    if args.dry_run:
        # Save mappings to file
        out_path = ROOT / "output" / "lecture_ct_mappings.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_mappings, f, indent=2)
        print(f"Saved to {out_path}")
    else:
        # Write to graph
        print("\nWriting to graph...")
        with driver.session() as s:
            written = 0
            for mapping in all_mappings:
                for ct_key in mapping["ct_keys"]:
                    s.run(
                        "MATCH (l:Lecture {key: $lkey}) "
                        "MATCH (ct:CurriculumTopic {key: $ctkey}) "
                        "MERGE (l)-[:COVERS_TOPIC]->(ct)",
                        lkey=mapping["lecture_key"], ctkey=ct_key,
                    )
                    written += 1
            print(f"  Written: {written} COVERS_TOPIC edges")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
