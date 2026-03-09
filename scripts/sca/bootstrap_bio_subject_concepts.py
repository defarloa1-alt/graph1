#!/usr/bin/env python3
"""
Bootstrap biographic SubjectConcepts and ClassificationAnchors.

Phase 1: Create ClassificationAnchors from Person nodes with LoC authority IDs
Phase 2: Create SubjectConcept nodes for biographic categories (by occupation)
Phase 3: Wire MEMBER_OF from Persons to SubjectConcepts (by occupation pattern)
Phase 4: Wire ANCHORS from ClassificationAnchors to SubjectConcepts
Phase 5: Register SYS_SFAAgent for biographic facet
Phase 6: Enrich Biographic Facet node

SubjectConcept categories (derived from occupation survey):
  - BIO_POLITICAL_FIGURES  — politicians, senators, orators, diplomats
  - BIO_MILITARY_FIGURES   — military personnel, military leaders, commanders
  - BIO_RELIGIOUS_FIGURES   — priests, priestesses, augurs, religious functionaries
  - BIO_LEGAL_FIGURES       — jurists, lawyers, legal scholars
  - BIO_INTELLECTUAL_FIGURES — writers, philosophers, historians, poets, scholars
  - BIO_ECONOMIC_FIGURES    — mintmasters, tax officials, commercial agents
  - BIO_GENERAL_PERSONS     — persons not matching above categories (fallback)

Usage:
  python scripts/sca/bootstrap_bio_subject_concepts.py --dry-run
  python scripts/sca/bootstrap_bio_subject_concepts.py --write
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from datetime import datetime, timezone
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

# ── SubjectConcept definitions ────────────────────────────────────────────────

BIO_SUBJECTS = [
    {
        "subject_id": "BIO_POLITICAL_FIGURES",
        "label": "Political Figures & Magistrates",
        "scope_note": "Politicians, senators, orators, diplomats, and holders of political offices. "
                      "The largest category, reflecting the political focus of Roman prosopography.",
        "lcsh_heading": "Statesmen--Rome",
        "lcsh_id": "sh2010012590",
        "lcc_primary": "DG",
        "occupation_patterns": [
            "politician", "senator", "orator", "diplomat", "statesman",
            "consul", "magistrate", "tribune", "praetor", "censor",
            "quaestor", "aedile", "dictator", "prefect",
        ],
    },
    {
        "subject_id": "BIO_MILITARY_FIGURES",
        "label": "Military Figures & Commanders",
        "scope_note": "Military personnel, generals, commanders, and soldiers. Includes those whose "
                      "primary occupation was military service, distinct from politicians who also held "
                      "military commands.",
        "lcsh_heading": "Generals--Rome",
        "lcsh_id": "sh2008105050",
        "lcc_primary": "DG",
        "occupation_patterns": [
            "military personnel", "military leader", "commander",
            "general", "soldier", "admiral", "centurion",
            "legionnaire", "military officer",
        ],
    },
    {
        "subject_id": "BIO_RELIGIOUS_FIGURES",
        "label": "Religious & Sacerdotal Figures",
        "scope_note": "Priests, priestesses, augurs, pontiffs, flamens, Vestal Virgins, and other "
                      "religious functionaries of Roman state religion.",
        "lcsh_heading": "Priests--Rome",
        "lcsh_id": "sh2010013126",
        "lcc_primary": "BL",
        "occupation_patterns": [
            "priest", "priestess", "augur", "pontiff", "flamen",
            "vestal", "haruspex", "ancient roman priest",
            "ancient roman priestess", "religious",
        ],
    },
    {
        "subject_id": "BIO_LEGAL_FIGURES",
        "label": "Legal Scholars & Jurists",
        "scope_note": "Jurists, lawyers, legal theorists, and figures known primarily for contributions "
                      "to Roman law. Distinct from politicians who incidentally practiced law.",
        "lcsh_heading": "Lawyers--Rome",
        "lcsh_id": "sh2008106459",
        "lcc_primary": "KJA",
        "occupation_patterns": [
            "jurist", "lawyer", "legal scholar", "jurisconsult",
        ],
    },
    {
        "subject_id": "BIO_INTELLECTUAL_FIGURES",
        "label": "Writers, Philosophers & Scholars",
        "scope_note": "Writers, poets, historians, philosophers, orators (literary), grammarians, "
                      "teachers, and other intellectual figures. Includes both Roman and Greek authors.",
        "lcsh_heading": "Authors, Latin",
        "lcsh_id": "sh85009879",
        "lcc_primary": "PA",
        "occupation_patterns": [
            "writer", "poet", "historian", "philosopher", "scholar",
            "grammarian", "teacher", "university teacher", "author",
            "art historian", "classical archaeologist", "archaeologist",
            "geographer", "encyclopedist", "biographer", "playwright",
            "rhetorician", "translator",
        ],
    },
    {
        "subject_id": "BIO_ECONOMIC_FIGURES",
        "label": "Economic & Financial Figures",
        "scope_note": "Mintmasters, tax collectors, publicani, and other figures whose primary role "
                      "was economic or financial administration. Includes moneyers (triumviri monetales).",
        "lcsh_heading": "Finance--Rome",
        "lcsh_id": "sh2010013780",
        "lcc_primary": "HJ",
        "occupation_patterns": [
            "mintmaster", "moneyer", "publicanus", "tax",
            "banker", "merchant", "financier",
        ],
    },
    {
        "subject_id": "BIO_GENERAL_PERSONS",
        "label": "General Biographical Persons",
        "scope_note": "Persons who don't fit neatly into the above categories. Includes those with "
                      "unknown occupation, mythological/legendary figures, and persons identified only "
                      "through prosopographical sources without specific role classification.",
        "lcsh_heading": "Rome--Biography",
        "lcsh_id": "sh85115013",
        "lcc_primary": "DG",
        "occupation_patterns": [],  # fallback — catches unclassified
    },
]

# ── Cypher queries ────────────────────────────────────────────────────────────

# Phase 1: ClassificationAnchors from Person LoC IDs
CREATE_PERSON_ANCHORS = """
MATCH (p:Person)
WHERE (p.loc_authority_id IS NOT NULL OR p.lcnaf_id IS NOT NULL)
  AND p.qid IS NOT NULL
WITH p, coalesce(p.loc_authority_id, p.lcnaf_id) AS loc_id
MERGE (a:ClassificationAnchor {qid: p.qid})
SET a.label        = p.label,
    a.anchor_type  = 'BiographicPerson',
    a.federation   = 'wikidata',
    a.source_type  = 'biographic_lcnaf',
    a.lcnaf_id     = loc_id,
    a.fast_id      = p.fast_id,
    a.gnd_id       = p.gnd_id,
    a.last_updated = datetime()
WITH p, a
MERGE (p)-[r:POSITIONED_AS {
    federation: 'wikidata',
    property: 'P244',
    hops: 0
}]->(a)
SET r.rel_type      = 'SELF_ANCHOR',
    r.anchor_type   = 'BiographicPerson',
    r.confidence    = 1.0,
    r.policy_ref    = 'FederationPositioningHopsSemantics',
    r.positioned_at = datetime()
RETURN count(a) AS anchors_created
"""

WIRE_PROVIDES_ANCHOR = """
MATCH (fed:SYS_FederationSource {source_id: 'wikidata'})
MATCH (a:ClassificationAnchor {source_type: 'biographic_lcnaf'})
WHERE NOT (fed)-[:PROVIDES_ANCHOR]->(a)
MERGE (fed)-[r:PROVIDES_ANCHOR]->(a)
SET r.confirmed_at = datetime()
RETURN count(r) AS wired
"""

# Phase 2: SubjectConcepts
MERGE_SUBJECT = """
MERGE (sc:SubjectConcept {subject_id: $subject_id})
SET sc.label           = $label,
    sc.scope_note      = $scope_note,
    sc.lcsh_heading    = $lcsh_heading,
    sc.lcsh_id         = $lcsh_id,
    sc.lcc_primary     = $lcc_primary,
    sc.source          = 'bio_bootstrap',
    sc.seed_domain     = 'biographic',
    sc.updated         = datetime()
WITH sc
MATCH (f:Facet {label: 'Biographic'})
MERGE (sc)-[:HAS_PRIMARY_FACET]->(f)
RETURN sc.subject_id AS sid
"""

# Phase 3: MEMBER_OF by occupation pattern
WIRE_MEMBER_OF = """
MATCH (p:Person), (sc:SubjectConcept {subject_id: $subject_id})
WHERE p.occupation IS NOT NULL
  AND any(pat IN $patterns WHERE toLower(p.occupation) CONTAINS pat)
MERGE (p)-[r:MEMBER_OF]->(sc)
SET r.source = 'bio_bootstrap_occupation',
    r.updated = datetime()
RETURN count(r) AS wired
"""

WIRE_UNCLASSIFIED = """
MATCH (p:Person)
WHERE NOT (p)-[:MEMBER_OF]->(:SubjectConcept)
WITH p
MATCH (sc:SubjectConcept {subject_id: 'BIO_GENERAL_PERSONS'})
MERGE (p)-[r:MEMBER_OF]->(sc)
SET r.source = 'bio_bootstrap_fallback',
    r.updated = datetime()
RETURN count(r) AS wired
"""

# Phase 4: Wire ClassificationAnchors to SubjectConcepts
# Uses the Person's occupation to determine which SC an anchor maps to
WIRE_ANCHOR_TO_SC = """
MATCH (a:ClassificationAnchor {source_type: 'biographic_lcnaf'})
MATCH (p:Person {qid: a.qid})
WHERE (p)-[:MEMBER_OF]->(:SubjectConcept)
WITH a, p
MATCH (p)-[:MEMBER_OF]->(sc:SubjectConcept)
WHERE sc.seed_domain = 'biographic'
WITH a, sc, sc.subject_id AS sid
ORDER BY sid
WITH a, collect(sc)[0] AS primary_sc
MERGE (a)-[r:ANCHORS]->(primary_sc)
SET r.source = 'bio_bootstrap',
    r.updated = datetime()
RETURN count(r) AS wired
"""

# Phase 5: Register SFA agent
REGISTER_SFA = """
MERGE (a:SYS_SFAAgent {agent_id: 'sfa_biographic'})
SET a.label       = 'Biographic SFA',
    a.facet       = 'Biographic',
    a.status      = 'bootstrap',
    a.description = 'Subject Facet Agent for the Biographic facet. Manages Person entities, '
                  + 'prosopographical data, and biographical classification anchors. '
                  + 'Covers 7 SubjectConcepts: political, military, religious, legal, '
                  + 'intellectual, economic figures, and general persons.',
    a.entity_types = ['Person'],
    a.updated     = datetime()
WITH a
MATCH (f:Facet {label: 'Biographic'})
MERGE (a)-[:MANAGES_FACET]->(f)
RETURN a.agent_id AS aid
"""

# Phase 6: Enrich Facet
ENRICH_FACET = """
MATCH (f:Facet {label: 'Biographic'})
SET f.description = 'Prosopographical and biographical dimension of knowledge. Covers political figures '
                  + '(magistrates, senators), military commanders, religious functionaries, legal scholars, '
                  + 'intellectual figures (writers, philosophers), and economic agents (mintmasters). '
                  + '5,248 Person nodes, D22 scoring (11 rules, max 100).',
    f.entity_count = $entity_count,
    f.anchor_count = $anchor_count,
    f.subject_concept_count = 7,
    f.updated = datetime()
RETURN f.label AS label
"""


def main():
    parser = argparse.ArgumentParser(description="Bootstrap biographic SubjectConcepts")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    print(f"Biographic SubjectConcept Bootstrap [{'WRITE' if write_mode else 'DRY RUN'}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    if not write_mode:
        # Preview
        print(f"\n  Would create {len(BIO_SUBJECTS)} SubjectConcept nodes:")
        for s in BIO_SUBJECTS:
            print(f"    {s['subject_id']:30s}  {s['label']}")
            print(f"      lcsh={s['lcsh_id']}, lcc={s['lcc_primary']}")

        # Preview anchor count
        with driver.session() as session:
            result = session.run("""
                MATCH (p:Person)
                WHERE (p.loc_authority_id IS NOT NULL OR p.lcnaf_id IS NOT NULL)
                  AND p.qid IS NOT NULL
                RETURN count(p) AS cnt
            """)
            anchor_cnt = result.single()["cnt"]
            print(f"\n  Would create {anchor_cnt} ClassificationAnchor nodes (biographic_lcnaf)")

        # Preview MEMBER_OF counts
        print(f"\n  MEMBER_OF preview (occupation pattern matching):")
        with driver.session() as session:
            for s in BIO_SUBJECTS:
                if not s["occupation_patterns"]:
                    continue
                result = session.run("""
                    MATCH (p:Person)
                    WHERE p.occupation IS NOT NULL
                      AND any(pat IN $patterns WHERE toLower(p.occupation) CONTAINS pat)
                    RETURN count(p) AS cnt
                """, patterns=s["occupation_patterns"])
                cnt = result.single()["cnt"]
                print(f"    {s['subject_id']:30s}  {cnt:>5} Persons")

            # Unclassified preview
            classified_patterns = []
            for s in BIO_SUBJECTS:
                classified_patterns.extend(s["occupation_patterns"])
            result = session.run("""
                MATCH (p:Person)
                WHERE p.occupation IS NULL
                   OR NOT any(pat IN $patterns WHERE toLower(p.occupation) CONTAINS pat)
                RETURN count(p) AS cnt
            """, patterns=classified_patterns)
            uncl = result.single()["cnt"]
            print(f"    {'BIO_GENERAL_PERSONS (fallback)':30s}  {uncl:>5} Persons")

        print(f"\n  Would register SYS_SFAAgent 'sfa_biographic'")
        print(f"  Would enrich Biographic Facet node")

        driver.close()
        print(f"\n  Re-run with --write to execute.")
        return

    # ── Phase 1: ClassificationAnchors ──
    print("\nPhase 1: Creating ClassificationAnchor nodes from Person LoC IDs...")
    with driver.session() as session:
        result = session.run(CREATE_PERSON_ANCHORS)
        anchor_cnt = result.single()["anchors_created"]
        print(f"  {anchor_cnt} ClassificationAnchor nodes + POSITIONED_AS relationships")

        result = session.run(WIRE_PROVIDES_ANCHOR)
        provides = result.single()["wired"]
        print(f"  {provides} PROVIDES_ANCHOR relationships")

    # ── Phase 2: SubjectConcepts ──
    print("\nPhase 2: Creating SubjectConcept nodes...")
    with driver.session() as session:
        for s in BIO_SUBJECTS:
            session.run(MERGE_SUBJECT, {
                "subject_id": s["subject_id"],
                "label": s["label"],
                "scope_note": s["scope_note"],
                "lcsh_heading": s["lcsh_heading"],
                "lcsh_id": s["lcsh_id"],
                "lcc_primary": s["lcc_primary"],
            })
            print(f"  {s['subject_id']:30s}  {s['label']}")
    print(f"  Created {len(BIO_SUBJECTS)} SubjectConcept nodes")

    # ── Phase 3: MEMBER_OF ──
    print("\nPhase 3: Wiring Person -> SubjectConcept MEMBER_OF...")
    total_wired = 0
    with driver.session() as session:
        for s in BIO_SUBJECTS:
            if not s["occupation_patterns"]:
                continue  # handle fallback separately
            result = session.run(WIRE_MEMBER_OF, {
                "subject_id": s["subject_id"],
                "patterns": s["occupation_patterns"],
            })
            cnt = result.single()["wired"]
            total_wired += cnt
            print(f"  {s['subject_id']:30s}  {cnt:>5} Persons")

        # Fallback for unclassified
        result = session.run(WIRE_UNCLASSIFIED)
        fallback = result.single()["wired"]
        total_wired += fallback
        print(f"  {'BIO_GENERAL_PERSONS (fallback)':30s}  {fallback:>5} Persons")
    print(f"  Total MEMBER_OF: {total_wired}")

    # ── Phase 4: Wire anchors to SubjectConcepts ──
    print("\nPhase 4: Wiring ClassificationAnchor -> SubjectConcept ANCHORS...")
    with driver.session() as session:
        result = session.run(WIRE_ANCHOR_TO_SC)
        anchored = result.single()["wired"]
        print(f"  {anchored} ANCHORS relationships")

    # ── Phase 5: Register SFA agent ──
    print("\nPhase 5: Registering SYS_SFAAgent...")
    with driver.session() as session:
        session.run(REGISTER_SFA)
        print("  sfa_biographic registered")

    # ── Phase 6: Enrich Facet ──
    print("\nPhase 6: Enriching Biographic Facet node...")
    with driver.session() as session:
        session.run(ENRICH_FACET, {
            "entity_count": 5248,
            "anchor_count": anchor_cnt,
        })
        print("  Biographic Facet enriched")

    # ── Verify ──
    print(f"\n{'=' * 60}")
    print("Verification:")
    with driver.session() as session:
        result = session.run("""
            MATCH (sc:SubjectConcept {seed_domain: 'biographic'})
            OPTIONAL MATCH (sc)<-[m:MEMBER_OF]-(p:Person)
            OPTIONAL MATCH (sc)<-[a:ANCHORS]-(ca:ClassificationAnchor)
            WITH sc, count(DISTINCT p) AS members, count(DISTINCT ca) AS anchors
            SET sc.entity_count = members
            RETURN sc.subject_id AS sid, sc.label AS label,
                   members, anchors
            ORDER BY members DESC
        """)
        for r in result:
            print(f"  {r['sid']:30s}  {r['members']:>5} members  {r['anchors']:>3} anchors  {r['label']}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
