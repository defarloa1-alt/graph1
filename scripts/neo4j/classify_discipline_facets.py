#!/usr/bin/env python3
"""
Classify disciplines into facets using deterministic seeds + LLM.

Phase 1: Deterministic — facet QID matches + SUBCLASS_OF descendants
Phase 2: LLM — batch classify remaining disciplines (primary + secondary facet)
Phase 3: Write HAS_FACET relationships to Neo4j
"""
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("WARNING: anthropic package not installed. LLM phase will be skipped.")

PROJECT = Path(__file__).resolve().parents[2]
OUTPUT_CSV = PROJECT / "Disciplines" / "discipline_facet_assignments.csv"

FACETS = {
    "ARCHAEOLOGICAL":  "Study of material culture, excavation, artifacts, physical remains",
    "ARTISTIC":        "Visual arts, architecture, aesthetics, art history, design, museology",
    "BIOGRAPHIC":      "Life writing, prosopography, personal histories, genealogy",
    "COMMUNICATION":   "Media, information science, journalism, rhetoric, publishing",
    "CULTURAL":        "Cultural practices, traditions, folklore, cultural studies",
    "DEMOGRAPHIC":     "Population studies, migration, census, vital statistics",
    "DIPLOMATIC":      "International relations, treaties, foreign policy, diplomacy",
    "ECONOMIC":        "Trade, finance, labor, agriculture, industry, economic systems",
    "ENVIRONMENTAL":   "Climate, ecology, natural resources, land use, environmental change",
    "GEOGRAPHIC":      "Places, spatial analysis, cartography, topography, historical geography",
    "INTELLECTUAL":    "Ideas, philosophy, historiography, scholarship, education, knowledge",
    "LINGUISTIC":      "Language, philology, grammar, semantics, translation, epigraphy",
    "MILITARY":        "Warfare, armies, strategy, fortification, naval, weapons",
    "POLITICAL":       "Government, law, institutions, administration, political movements",
    "RELIGIOUS":       "Religion, theology, ritual, sacred texts, church history",
    "SCIENTIFIC":      "Natural sciences, mathematics, medicine, technology of observation",
    "SOCIAL":          "Society, class, gender, family, customs, social structures",
    "TECHNOLOGICAL":   "Engineering, tools, construction, manufacturing, applied science",
}

FACET_LIST_STR = "\n".join(f"  {k}: {v}" for k, v in FACETS.items())


def phase1_deterministic(session):
    """Assign facets deterministically where facet QID = discipline QID or ancestor."""
    assignments = {}

    # Direct QID matches + descendants
    result = session.run("""
        MATCH (f:Facet)
        MATCH (d:Discipline {qid: f.qid})
        OPTIONAL MATCH (child:Discipline)-[:SUBCLASS_OF*1..5]->(d)
        WITH f.key AS facet, collect(DISTINCT d.qid) + collect(DISTINCT child.qid) AS qids
        UNWIND qids AS qid
        WITH facet, qid WHERE qid IS NOT NULL
        RETURN DISTINCT qid, facet
    """)
    for r in result:
        qid = r["qid"]
        facet = r["facet"]
        assignments.setdefault(qid, {"primary": None, "related": []})
        if assignments[qid]["primary"] is None:
            assignments[qid]["primary"] = facet
        elif not any(r["facet"] == facet for r in assignments[qid]["related"]):
            assignments[qid]["related"].append({"facet": facet, "weight": 0.8})

    print(f"Phase 1: {len(assignments)} disciplines assigned deterministically")
    return assignments


def phase2_llm(session, existing_assignments):
    """Use Claude to classify remaining disciplines."""
    if not HAS_ANTHROPIC:
        print("Phase 2: SKIPPED (no anthropic package)")
        return existing_assignments

    # Load all disciplines
    result = session.run("""
        MATCH (d:Discipline)
        OPTIONAL MATCH (d)-[:SUBCLASS_OF]->(parent:Discipline)
        RETURN d.qid as qid, d.label as label,
               collect(parent.label) as parents
        ORDER BY d.label
    """)
    all_discs = []
    for r in result:
        if r["qid"] not in existing_assignments:
            all_discs.append({
                "qid": r["qid"],
                "label": r["label"],
                "parents": [p for p in r["parents"] if p],
            })

    print(f"Phase 2: {len(all_discs)} disciplines need LLM classification")

    client = anthropic.Anthropic()
    assignments = dict(existing_assignments)

    # Process in batches of 40
    BATCH = 40
    for i in range(0, len(all_discs), BATCH):
        batch = all_discs[i : i + BATCH]
        batch_str = "\n".join(
            f"  {d['qid']}: {d['label']}" + (f" (subclass of: {', '.join(d['parents'])})" if d['parents'] else "")
            for d in batch
        )

        prompt = f"""Classify each academic discipline into ONE primary facet and any number of related facets with relevance weights.

FACETS:
{FACET_LIST_STR}

DISCIPLINES TO CLASSIFY:
{batch_str}

Return ONLY a JSON array. Each element:
{{"qid": "...", "primary": "FACET_KEY", "related": [{{"facet": "FACET_KEY", "weight": 0.8}}, ...]}}

Rules:
- primary = the single best-fit facet
- related = other facets this discipline meaningfully touches (weight 0.3-0.9)
- weight reflects how central that facet is (0.9 = almost primary, 0.3 = peripheral)
- related can be empty if the discipline is purely one facet
- do NOT include the primary facet in related
- Use ONLY the facet keys listed above. No explanation."""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            # Extract JSON from response
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            results = json.loads(text)

            for item in results:
                qid = item["qid"]
                primary = item["primary"]
                related = item.get("related", [])
                if primary in FACETS:
                    assignments[qid] = {
                        "primary": primary,
                        "related": [
                            {"facet": r["facet"], "weight": r.get("weight", 0.5)}
                            for r in related
                            if isinstance(r, dict) and r.get("facet") in FACETS and r["facet"] != primary
                        ],
                    }

            classified = sum(1 for item in results if item["qid"] in assignments)
            print(f"  Batch {i//BATCH + 1}/{(len(all_discs) + BATCH - 1)//BATCH}: {classified}/{len(batch)} classified")

        except Exception as e:
            print(f"  Batch {i//BATCH + 1} ERROR: {e}")

        time.sleep(1)

    return assignments


def phase3_write(session, assignments):
    """Write HAS_FACET relationships to Neo4j and save CSV."""
    print(f"\nPhase 3: Writing {len(assignments)} assignments to Neo4j")

    # Clear existing HAS_FACET from disciplines
    session.run("MATCH (:Discipline)-[r:HAS_FACET]->(:Facet) DELETE r")

    BATCH = 50

    # Write primary facets
    primary_batch = [{"qid": qid, "facet": a["primary"]}
                     for qid, a in assignments.items() if a["primary"]]
    primary_count = 0
    for i in range(0, len(primary_batch), BATCH):
        batch = primary_batch[i : i + BATCH]
        result = session.run("""
            UNWIND $batch AS row
            MATCH (d:Discipline {qid: row.qid})
            MATCH (f:Facet {key: row.facet})
            MERGE (d)-[r:HAS_FACET]->(f)
            SET r.primary = true, r.weight = 1.0
            RETURN count(r) as cnt
        """, batch=batch)
        primary_count += result.single()["cnt"]

    # Write related facets with weights
    related_batch = []
    for qid, a in assignments.items():
        for rel in a.get("related", []):
            related_batch.append({
                "qid": qid,
                "facet": rel["facet"],
                "weight": rel["weight"],
            })

    related_count = 0
    for i in range(0, len(related_batch), BATCH):
        batch = related_batch[i : i + BATCH]
        result = session.run("""
            UNWIND $batch AS row
            MATCH (d:Discipline {qid: row.qid})
            MATCH (f:Facet {key: row.facet})
            MERGE (d)-[r:HAS_FACET]->(f)
            SET r.primary = false, r.weight = row.weight
            RETURN count(r) as cnt
        """, batch=batch)
        related_count += result.single()["cnt"]

    print(f"  Primary: {primary_count} HAS_FACET relationships")
    print(f"  Related: {related_count} HAS_FACET relationships (with weights)")

    # Save to CSV
    rows = []
    for qid, a in sorted(assignments.items()):
        related_str = "|".join(
            f"{r['facet']}:{r['weight']}" for r in a.get("related", [])
        )
        rows.append({
            "qid": qid,
            "primary_facet": a["primary"] or "",
            "related_facets": related_str,
        })

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "primary_facet", "related_facets"])
        w.writeheader()
        w.writerows(rows)
    print(f"  Saved to {OUTPUT_CSV.name}")

    # Summary by facet
    print("\n-- Primary facet distribution --")
    result = session.run("""
        MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet)
        WHERE r.primary = true
        RETURN f.key as facet, count(d) as cnt
        ORDER BY cnt DESC
    """)
    for r in result:
        print(f"  {r['facet']:20s} {r['cnt']}")

    print("\n-- Related facet distribution --")
    result = session.run("""
        MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet)
        WHERE r.primary = false
        RETURN f.key as facet, count(r) as cnt,
               round(avg(r.weight) * 100) / 100 as avg_weight
        ORDER BY cnt DESC
    """)
    for r in result:
        print(f"  {r['facet']:20s} {r['cnt']:>4d}  avg weight: {r['avg_weight']}")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        assignments = phase1_deterministic(session)
        assignments = phase2_llm(session, assignments)
        phase3_write(session, assignments)

        # Final count
        result = session.run(
            "MATCH (:Discipline)-[r:HAS_FACET]->(:Facet) RETURN count(r) as total"
        )
        print(f"\nTotal HAS_FACET relationships: {result.single()['total']}")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
