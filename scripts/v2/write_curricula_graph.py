#!/usr/bin/env python3
"""Write harvested curricula to Neo4j as CourseSyllabus -> Module -> Lecture structure.

Links DisciplineSource -> CourseSyllabus -> CourseModule -> Lecture.
Then auto-links Lectures to CurriculumTopics via WikiConcept keyword matching.

Run:
  python scripts/v2/write_curricula_graph.py
  python scripts/v2/write_curricula_graph.py --dry-run
  python scripts/v2/write_curricula_graph.py --clean
"""
import sys, json, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase


def main():
    parser = argparse.ArgumentParser(description="Write curricula to Neo4j")
    parser.add_argument("--clean", action="store_true", help="Delete existing curriculum nodes first")
    parser.add_argument("--dry-run", action="store_true", help="Show stats without writing")
    args = parser.parse_args()

    sys.stdout.reconfigure(errors="replace")

    data_path = ROOT / "output" / "discipline_source_curricula.json"
    data = json.load(open(data_path, encoding="utf-8"))
    sources = data["sources"]

    total_modules = sum(len(s["modules"]) for s in sources)
    total_lectures = sum(
        sum(len(m["topics"]) for m in s["modules"])
        for s in sources
    )

    print(f"Sources: {len(sources)}")
    print(f"Modules: {total_modules}")
    print(f"Lectures: {total_lectures}")

    if args.dry_run:
        for s in sources:
            lcount = sum(len(m["topics"]) for m in s["modules"])
            print(f"  {s['label']:60s} {len(s['modules']):2d} modules, {lcount:3d} lectures")
        return

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    if args.clean:
        print("\nCleaning existing curriculum nodes...")
        with driver.session() as s:
            for label in ["Lecture", "CourseModule", "CourseSyllabus"]:
                result = s.run(f"MATCH (n:{label}) DETACH DELETE n RETURN count(n) AS deleted")
                row = result.single()
                print(f"  Deleted {row['deleted']} {label} nodes")

    print("\nWriting curriculum graph...")
    ds_linked = 0

    with driver.session() as s:
        for src in sources:
            syllabus_key = src["url"].replace("https://", "").replace("/", "_")[:80]

            # Create CourseSyllabus node
            s.run(
                "MERGE (cs:CourseSyllabus {url: $url}) "
                "SET cs.label = $label, cs.provider = $provider, "
                "    cs.type = $type, cs.key = $key",
                url=src["url"], label=src["label"],
                provider=src["provider"], type=src["type"],
                key=syllabus_key,
            )

            # Link to DisciplineSource
            result = s.run(
                "MATCH (ds:DisciplineSource {url: $url}) "
                "MATCH (cs:CourseSyllabus {url: $url}) "
                "MERGE (ds)-[:HAS_SYLLABUS]->(cs) "
                "RETURN ds.label AS ds_label",
                url=src["url"],
            )
            row = result.single()
            if row:
                ds_linked += 1

            # Create modules and lectures
            for mi, module in enumerate(src["modules"]):
                module_key = f"{syllabus_key}_m{mi}"

                s.run(
                    "MATCH (cs:CourseSyllabus {url: $url}) "
                    "MERGE (cm:CourseModule {key: $key}) "
                    "SET cm.title = $title, cm.order = $order "
                    "MERGE (cs)-[:HAS_MODULE]->(cm)",
                    url=src["url"], key=module_key,
                    title=module["title"], order=mi,
                )

                for topic in module["topics"]:
                    lecture_key = f"{module_key}_s{topic['session']}"

                    s.run(
                        "MATCH (cm:CourseModule {key: $mkey}) "
                        "MERGE (l:Lecture {key: $key}) "
                        "SET l.title = $title, l.session = $session "
                        "MERGE (cm)-[:HAS_LECTURE]->(l)",
                        mkey=module_key, key=lecture_key,
                        title=topic["title"], session=topic["session"],
                    )

            lcount = sum(len(m["topics"]) for m in src["modules"])
            print(f"  {src['label']:60s} {len(src['modules']):2d} mod, {lcount:3d} lec {'(DS linked)' if row else ''}")

    print(f"\nDisciplineSource links: {ds_linked}/{len(sources)}")

    # Auto-link lectures to WikiConcepts by keyword matching
    print("\nAuto-linking lectures to WikiConcepts...")
    with driver.session() as s:
        result = s.run("""
            MATCH (l:Lecture)
            WITH l, toLower(l.title) AS ltitle
            MATCH (wc:WikiConcept)
            WHERE toLower(wc.name) = ltitle
            MERGE (l)-[:COVERS_CONCEPT]->(wc)
            RETURN count(*) AS links
        """)
        exact = result.single()["links"]
        print(f"  Exact name matches: {exact}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
