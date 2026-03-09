#!/usr/bin/env python3
"""
Enrich biographic MEMBER_OF relationships with temporal and multiplicity dimensions.

Reads POSITION_HELD edges (7,342 with year_start) and maps positions to
SubjectConcept categories. For each Person→SubjectConcept MEMBER_OF:

  - earliest_year:  earliest POSITION_HELD year for positions in this category
  - latest_year:    latest POSITION_HELD year for positions in this category
  - position_count: how many positions the person held in this category
  - rank:           'primary' (most positions) or 'secondary' (fewer)
  - source:         updated to 'bio_temporal_position_held'

For Persons without POSITION_HELD data (the Wikidata-only population),
MEMBER_OF retains occupation-based classification with rank='inferred'.

Usage:
  python scripts/sca/enrich_bio_membership_temporal.py --dry-run
  python scripts/sca/enrich_bio_membership_temporal.py --write
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

from neo4j import GraphDatabase

# ── Position → SubjectConcept mapping ─────────────────────────────────────────
# Maps position labels (from DPRR) to biographic SubjectConcept IDs.
# A position can map to multiple categories (e.g. legatus = military + political).

POSITION_TO_SC = {
    # POLITICAL
    "consul": ["BIO_POLITICAL_FIGURES"],
    "consul suffectus": ["BIO_POLITICAL_FIGURES"],
    "praetor": ["BIO_POLITICAL_FIGURES"],
    "quaestor": ["BIO_POLITICAL_FIGURES"],
    "aedilis curulis": ["BIO_POLITICAL_FIGURES"],
    "aedilis plebis": ["BIO_POLITICAL_FIGURES"],
    "tribunus plebis": ["BIO_POLITICAL_FIGURES"],
    "censor": ["BIO_POLITICAL_FIGURES"],
    "dictator": ["BIO_POLITICAL_FIGURES"],
    "magister equitum": ["BIO_POLITICAL_FIGURES"],
    "interrex": ["BIO_POLITICAL_FIGURES"],
    "princeps senatus": ["BIO_POLITICAL_FIGURES"],
    "senator - office unknown": ["BIO_POLITICAL_FIGURES"],
    "promagistrate": ["BIO_POLITICAL_FIGURES"],
    "proconsul": ["BIO_POLITICAL_FIGURES"],
    "propraetor": ["BIO_POLITICAL_FIGURES"],
    "proquaestor": ["BIO_POLITICAL_FIGURES"],
    "dictator legibus faciendis et rei publicae constituendae causa": ["BIO_POLITICAL_FIGURES"],
    "dictator perpetuus": ["BIO_POLITICAL_FIGURES"],
    "triumvir rei publicae constituendae": ["BIO_POLITICAL_FIGURES"],
    "special commissioners": ["BIO_POLITICAL_FIGURES"],
    "iudex quaestionis": ["BIO_POLITICAL_FIGURES", "BIO_LEGAL_FIGURES"],
    "duovir perduellionis": ["BIO_POLITICAL_FIGURES", "BIO_LEGAL_FIGURES"],
    "duovir aedi dedicandae": ["BIO_POLITICAL_FIGURES"],
    "duovir aedi locandae": ["BIO_POLITICAL_FIGURES"],
    "septemvir agris dividendis": ["BIO_POLITICAL_FIGURES"],

    # MILITARY
    "tribunus militum": ["BIO_MILITARY_FIGURES"],
    "tribunus militum consulari potestate": ["BIO_MILITARY_FIGURES", "BIO_POLITICAL_FIGURES"],
    "legatus (lieutenant)": ["BIO_MILITARY_FIGURES"],
    "legatus (ambassador)": ["BIO_POLITICAL_FIGURES"],
    "legatus (envoy)": ["BIO_POLITICAL_FIGURES"],
    "praefectus": ["BIO_MILITARY_FIGURES"],
    "praefectus equitum": ["BIO_MILITARY_FIGURES"],
    "triumphator": ["BIO_MILITARY_FIGURES"],
    "officer (title not preserved)": ["BIO_MILITARY_FIGURES"],

    # RELIGIOUS
    "augur": ["BIO_RELIGIOUS_FIGURES"],
    "pontifex": ["BIO_RELIGIOUS_FIGURES"],
    "pontifex maximus": ["BIO_RELIGIOUS_FIGURES"],
    "flamen Dialis": ["BIO_RELIGIOUS_FIGURES"],
    "flamen Iulialis": ["BIO_RELIGIOUS_FIGURES"],
    "flamen Martialis": ["BIO_RELIGIOUS_FIGURES"],
    "flamen Quirinalis": ["BIO_RELIGIOUS_FIGURES"],
    "salius": ["BIO_RELIGIOUS_FIGURES"],
    "decemvir sacris faciundis": ["BIO_RELIGIOUS_FIGURES"],
    "rex sacrorum": ["BIO_RELIGIOUS_FIGURES"],
    "epulo": ["BIO_RELIGIOUS_FIGURES"],
    "curio maximus": ["BIO_RELIGIOUS_FIGURES"],
    "fetialis": ["BIO_RELIGIOUS_FIGURES"],
    "sodalis sacris Idaeis Magnae Matris": ["BIO_RELIGIOUS_FIGURES"],
    "lupercus Iulianus": ["BIO_RELIGIOUS_FIGURES"],
    "lupercus Iulianus - magister": ["BIO_RELIGIOUS_FIGURES"],
    "Vestal Virgin": ["BIO_RELIGIOUS_FIGURES"],

    # ECONOMIC
    "monetalis": ["BIO_ECONOMIC_FIGURES"],
    "moneyer": ["BIO_ECONOMIC_FIGURES"],
    "curator restituendi Capitolii": ["BIO_ECONOMIC_FIGURES"],

    # LEGAL (most already cross-listed above)
    "repulsa (pr.)": ["BIO_POLITICAL_FIGURES"],
    "repulsa (cens.)": ["BIO_POLITICAL_FIGURES"],
}

# Default for unmapped positions
DEFAULT_SC = "BIO_POLITICAL_FIGURES"


def main():
    parser = argparse.ArgumentParser(description="Enrich bio MEMBER_OF with temporal dimensions")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    print(f"Bio MEMBER_OF Temporal Enrichment [{'WRITE' if write_mode else 'DRY RUN'}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Step 1: Read all POSITION_HELD edges with temporal data
    print("\nStep 1: Reading POSITION_HELD edges...")
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person)-[r:POSITION_HELD]->(pos:Position)
            WHERE r.year_start IS NOT NULL
            RETURN p.qid AS person_qid, p.entity_id AS person_eid,
                   pos.label AS position_label,
                   r.year_start AS year_start,
                   r.year_end AS year_end
        """)
        edges = [dict(r) for r in result]
    print(f"  {len(edges)} POSITION_HELD edges with year_start")

    # Step 2: Map positions to SubjectConcepts per person
    print("\nStep 2: Mapping positions to SubjectConcepts...")

    # person_id → {sc_id → {years: [], positions: []}}
    person_sc_data = defaultdict(lambda: defaultdict(lambda: {"years": [], "positions": []}))

    unmapped_positions = set()
    for edge in edges:
        person_key = edge["person_qid"] or edge["person_eid"]
        pos_label = edge["position_label"]
        year = edge["year_start"]

        sc_ids = POSITION_TO_SC.get(pos_label)
        if not sc_ids:
            # Try partial matching for positions not in map
            sc_ids = [DEFAULT_SC]
            unmapped_positions.add(pos_label)

        for sc_id in sc_ids:
            data = person_sc_data[person_key][sc_id]
            data["years"].append(year)
            if pos_label not in data["positions"]:
                data["positions"].append(pos_label)

    print(f"  {len(person_sc_data)} persons with position-derived SC memberships")
    if unmapped_positions:
        print(f"  {len(unmapped_positions)} unmapped position types (defaulted to POLITICAL):")
        for p in sorted(unmapped_positions)[:10]:
            print(f"    {p}")

    # Step 3: Compute rank per person (primary = SC with most positions)
    print("\nStep 3: Computing membership ranks...")

    # Build update records
    updates = []
    for person_key, sc_map in person_sc_data.items():
        # Find primary SC (most positions)
        max_count = max(len(d["positions"]) for d in sc_map.values())

        for sc_id, data in sc_map.items():
            years = sorted(data["years"])
            rank = "primary" if len(data["positions"]) == max_count else "secondary"
            updates.append({
                "person_key": person_key,
                "sc_id": sc_id,
                "earliest_year": years[0],
                "latest_year": years[-1],
                "position_count": len(data["positions"]),
                "rank": rank,
            })

    print(f"  {len(updates)} MEMBER_OF edges to enrich")

    # Stats
    rank_counts = defaultdict(int)
    for u in updates:
        rank_counts[u["rank"]] += 1
    for rank, cnt in sorted(rank_counts.items()):
        print(f"    {rank}: {cnt}")

    sc_counts = defaultdict(int)
    for u in updates:
        sc_counts[u["sc_id"]] += 1
    print(f"\n  Position-derived memberships per SC:")
    for sc_id, cnt in sorted(sc_counts.items(), key=lambda x: -x[1]):
        print(f"    {sc_id:30s}  {cnt:>5}")

    if not write_mode:
        print(f"\n  [DRY RUN] Re-run with --write to apply.")

        # Show examples
        examples = ["Q1048", "Q483783", "Q51673"]  # Caesar, Sulla, Antony
        for ex_qid in examples:
            if ex_qid in person_sc_data:
                print(f"\n  Example: {ex_qid}")
                for sc_id, data in person_sc_data[ex_qid].items():
                    years = sorted(data["years"])
                    print(f"    {sc_id:30s}  {years[0]:>5} to {years[-1]:>5}  "
                          f"{len(data['positions'])} positions: {', '.join(data['positions'][:3])}")

        driver.close()
        return

    # Step 4: Write temporal enrichment
    print("\nStep 4: Writing temporal enrichment to MEMBER_OF edges...")

    # First: ensure MEMBER_OF edges exist for position-derived memberships
    # (some persons may have positions in categories they weren't classified into via occupation)
    print("  4a: Ensuring MEMBER_OF edges exist for position-derived memberships...")
    with driver.session() as session:
        # Batch by SC to create any missing MEMBER_OF edges
        for sc_id in sc_counts.keys():
            person_keys = [u["person_key"] for u in updates if u["sc_id"] == sc_id]
            # Split into QID and entity_id keys
            qid_keys = [k for k in person_keys if k.startswith("Q")]
            eid_keys = [k for k in person_keys if not k.startswith("Q")]

            if qid_keys:
                session.run("""
                    UNWIND $keys AS key
                    MATCH (p:Person {qid: key}), (sc:SubjectConcept {subject_id: $sc_id})
                    MERGE (p)-[r:MEMBER_OF]->(sc)
                    ON CREATE SET r.source = 'bio_temporal_position_held',
                                  r.updated = datetime()
                    RETURN count(r) AS cnt
                """, keys=qid_keys, sc_id=sc_id)

            if eid_keys:
                session.run("""
                    UNWIND $keys AS key
                    MATCH (p:Person {entity_id: key}), (sc:SubjectConcept {subject_id: $sc_id})
                    MERGE (p)-[r:MEMBER_OF]->(sc)
                    ON CREATE SET r.source = 'bio_temporal_position_held',
                                  r.updated = datetime()
                    RETURN count(r) AS cnt
                """, keys=eid_keys, sc_id=sc_id)

    print("  4b: Enriching MEMBER_OF edges with temporal data...")
    enriched = 0
    with driver.session() as session:
        # Process in batches by SC
        for sc_id in sc_counts.keys():
            sc_updates = [u for u in updates if u["sc_id"] == sc_id]

            qid_updates = [u for u in sc_updates if u["person_key"].startswith("Q")]
            eid_updates = [u for u in sc_updates if not u["person_key"].startswith("Q")]

            if qid_updates:
                result = session.run("""
                    UNWIND $rows AS row
                    MATCH (p:Person {qid: row.person_key})-[r:MEMBER_OF]->(sc:SubjectConcept {subject_id: $sc_id})
                    SET r.earliest_year  = row.earliest_year,
                        r.latest_year    = row.latest_year,
                        r.position_count = row.position_count,
                        r.rank           = row.rank,
                        r.source         = 'bio_temporal_position_held',
                        r.updated        = datetime()
                    RETURN count(r) AS cnt
                """, rows=qid_updates, sc_id=sc_id)
                enriched += result.single()["cnt"]

            if eid_updates:
                result = session.run("""
                    UNWIND $rows AS row
                    MATCH (p:Person {entity_id: row.person_key})-[r:MEMBER_OF]->(sc:SubjectConcept {subject_id: $sc_id})
                    SET r.earliest_year  = row.earliest_year,
                        r.latest_year    = row.latest_year,
                        r.position_count = row.position_count,
                        r.rank           = row.rank,
                        r.source         = 'bio_temporal_position_held',
                        r.updated        = datetime()
                    RETURN count(r) AS cnt
                """, rows=eid_updates, sc_id=sc_id)
                enriched += result.single()["cnt"]

    print(f"  Enriched {enriched} MEMBER_OF edges with temporal data")

    # Step 5: Mark non-temporal memberships as rank='inferred'
    print("\nStep 5: Marking non-temporal memberships as rank='inferred'...")
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person)-[r:MEMBER_OF]->(sc:SubjectConcept {seed_domain: 'biographic'})
            WHERE r.rank IS NULL
            SET r.rank = 'inferred'
            RETURN count(r) AS cnt
        """)
        inferred = result.single()["cnt"]
        print(f"  {inferred} MEMBER_OF edges marked as rank='inferred'")

    # Verify
    print(f"\n{'=' * 60}")
    print("Verification:")
    with driver.session() as session:
        result = session.run("""
            MATCH (sc:SubjectConcept {seed_domain: 'biographic'})
            OPTIONAL MATCH (sc)<-[r:MEMBER_OF]-(p:Person)
            WITH sc,
                 count(DISTINCT p) AS members,
                 count(CASE WHEN r.rank = 'primary' THEN 1 END) AS primary_cnt,
                 count(CASE WHEN r.rank = 'secondary' THEN 1 END) AS secondary_cnt,
                 count(CASE WHEN r.rank = 'inferred' THEN 1 END) AS inferred_cnt,
                 count(CASE WHEN r.earliest_year IS NOT NULL THEN 1 END) AS has_temporal
            SET sc.entity_count = members
            RETURN sc.subject_id AS sid,
                   members, primary_cnt, secondary_cnt, inferred_cnt, has_temporal
            ORDER BY members DESC
        """)
        print(f"  {'SubjectConcept':30s}  {'members':>7}  {'primary':>7}  {'secondary':>9}  {'inferred':>8}  {'temporal':>8}")
        for r in result:
            print(f"  {r['sid']:30s}  {r['members']:>7}  {r['primary_cnt']:>7}  {r['secondary_cnt']:>9}  "
                  f"{r['inferred_cnt']:>8}  {r['has_temporal']:>8}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
