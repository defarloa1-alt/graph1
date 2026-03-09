#!/usr/bin/env python3
"""
Export Discipline → Facet assignments from Neo4j and merge into discipline_taxonomy.csv.
Adds columns: primary_facet, related_facets (pipe-delimited FACET:weight)
Updates both output/ and viewer/public/ copies.
"""
import csv
import sys
import shutil
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
SRC_CSV = PROJECT / "output" / "discipline_taxonomy.csv"
PUBLIC_CSV = PROJECT / "viewer" / "public" / "discipline_taxonomy.csv"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Fetch all facet assignments
    facet_map = defaultdict(lambda: {"primary": "", "related": []})

    with driver.session() as session:
        result = session.run("""
            MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet)
            RETURN d.qid AS qid, f.key AS facet, r.primary AS is_primary, r.weight AS weight
            ORDER BY d.qid
        """)
        for rec in result:
            qid = rec["qid"]
            facet = rec["facet"]
            is_primary = rec["is_primary"]
            weight = rec["weight"]
            if is_primary:
                facet_map[qid]["primary"] = facet
            else:
                facet_map[qid]["related"].append(f"{facet}:{weight}")

    driver.close()
    print(f"Fetched facet assignments for {len(facet_map)} disciplines")

    # Read existing CSV
    rows = []
    with open(SRC_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        orig_fields = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"Read {len(rows)} rows from {SRC_CSV.name}")

    # Merge facet data
    new_fields = list(orig_fields)
    if "primary_facet" not in new_fields:
        new_fields.append("primary_facet")
    if "related_facets" not in new_fields:
        new_fields.append("related_facets")

    matched = 0
    for row in rows:
        qid = row["qid"]
        if qid in facet_map:
            row["primary_facet"] = facet_map[qid]["primary"]
            row["related_facets"] = "|".join(facet_map[qid]["related"])
            matched += 1
        else:
            row.setdefault("primary_facet", "")
            row.setdefault("related_facets", "")

    print(f"Matched {matched} disciplines with facet assignments")

    # Write updated CSV
    with open(SRC_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {SRC_CSV.name}")

    # Copy to viewer/public
    shutil.copy2(SRC_CSV, PUBLIC_CSV)
    print(f"Copied to {PUBLIC_CSV}")

    # Summary
    facet_counts = defaultdict(int)
    for row in rows:
        pf = row.get("primary_facet", "")
        if pf:
            facet_counts[pf] += 1
    print("\n-- Primary facet distribution --")
    for facet, cnt in sorted(facet_counts.items(), key=lambda x: -x[1]):
        print(f"  {facet:20s} {cnt}")
    print(f"\n  {len(rows) - matched} disciplines without facet assignment")


if __name__ == "__main__":
    main()
