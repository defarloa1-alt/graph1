#!/usr/bin/env python3
"""
ADR-007 Section 3: Data Quality Classification — 25 Noise Nodes

Identifies and remediates the 25 nodes in the person_ namespace that fail the veto gate:
  Veto: EXISTS { (n)-[:P31]->(m:Entity) WHERE m.label <> 'human' AND n.dprr_id IS NULL }
  Also: nodes with no P31 edge at all (mythological: Romulus, Remus, Europa)

Classification:
  - 15 Clear non-persons: Reclassify entity_type; re-ID with correct prefix; no :Person label
  - 3 Mythological: Apply :MythologicalPerson; mythological=true; DQ_UNRESOLVED_PERSONHOOD
  - 7 Biblical (P31 gap): Queue P31 re-fetch; promote to :Person after confirmation

Usage:
  python scripts/federation/adr007_section3_person_noise_cleanup.py --report
  python scripts/federation/adr007_section3_person_noise_cleanup.py --apply
"""

import argparse
import json
import re
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
    from tools.entity_cipher import generate_entity_cipher
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", os.environ.get("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
    NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")
    generate_entity_cipher = None

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

# ADR-007 Section 3 classification heuristics
MYTHOLOGICAL_LABELS = {"romulus", "remus", "europa"}
BIBLICAL_LABELS = {
    "andrew the apostle", "silas", "damaris", "aristarchus",
    "andrew", "paul", "peter", "john", "james", "jude", "thomas",
    "matthew", "mark", "luke", "philip", "bartholomew", "simon",
    "judas", "stephen", "barnabas", "timothy", "apollos",
}
# Non-person patterns (place, region, concept, etc.)
NON_PERSON_PATTERNS = [
    r"region$", r"city$", r"sea$", r"ocean$", r"empire$", r"republic$",
    r"propaganda", r"mediterranean", r"chang'an", r"big city",
]


def _normalize_label(s: str) -> str:
    return (s or "").strip().lower()


def classify_noise_node(label: str, qid: str | None, p31_targets: list[dict]) -> str:
    """
    Classify a noise node into: DQ_WRONG_ENTITY_TYPE | DQ_UNRESOLVED_PERSONHOOD | DQ_MISSING_P31
    """
    norm = _normalize_label(label)
    has_p31 = bool(p31_targets)
    p31_is_human = any(
        (t.get("qid") or "").upper() == "Q5" or _normalize_label(t.get("label") or "") == "human"
        for t in p31_targets
    )

    # Mythological: no P31, no DPRR, known legendary names
    if not has_p31 and any(m in norm for m in MYTHOLOGICAL_LABELS):
        return "DQ_UNRESOLVED_PERSONHOOD"  # Mythological

    # Biblical: P31 gap — likely human but Wikidata P31 not fetched
    if not has_p31 or not p31_is_human:
        if any(b in norm for b in BIBLICAL_LABELS):
            return "DQ_MISSING_P31"  # Biblical

    # Non-persons: everything else
    return "DQ_WRONG_ENTITY_TYPE"


def get_entity_type_from_p31(p31_targets: list[dict]) -> str:
    """Infer correct entity_type from P31 targets for non-persons."""
    if not p31_targets:
        return "CONCEPT"  # unknown
    labels = [_normalize_label(t.get("label") or "") for t in p31_targets]
    qids = [(t.get("qid") or "").upper() for t in p31_targets]
    # Place types
    if any(q in qids for q in ("Q2221906", "Q515", "Q1549591", "Q15634554")):
        return "PLACE"
    if any("place" in l or "region" in l or "city" in l for l in labels):
        return "PLACE"
    # Event
    if any(q in qids for q in ("Q1190554", "Q1656682", "Q198", "Q178561")):
        return "EVENT"
    # Concept
    if any(q in qids for q in ("Q151885", "Q16889133", "Q4167836")):
        return "CONCEPT"
    return "CONCEPT"


def get_prefix_for_entity_type(entity_type: str) -> str:
    """Entity ID prefix per ENTITY_CIPHER_FOR_VERTEX_JUMPS.md."""
    m = {
        "PLACE": "plc",
        "EVENT": "evt",
        "CONCEPT": "con",
        "SUBJECTCONCEPT": "sub",
        "ORGANIZATION": "org",
    }
    return m.get(entity_type.upper(), "con")


def run_report(driver, database: str) -> dict:
    """Query Neo4j for person_ namespace nodes that fail the veto gate."""
    with driver.session(database=database) as session:
        # Nodes with entity_id starting person_ OR entity_cipher ent_per_*, dprr_id IS NULL
        # and either: (a) P31 to non-human, or (b) no P31 at all
        # Support both P31 and WIKIDATA_P31 (legacy) relationship types
        result = session.run("""
            MATCH (n:Entity)
            WHERE (n.entity_id STARTS WITH 'person_' OR (n.entity_cipher STARTS WITH 'ent_per_' AND n.entity_type = 'PERSON'))
              AND n.dprr_id IS NULL
            OPTIONAL MATCH (n)-[r]->(p31:Entity)
            WHERE type(r) IN ['P31', 'WIKIDATA_P31']
            WITH n,
                 collect(DISTINCT CASE WHEN p31 IS NOT NULL THEN {qid: p31.qid, label: p31.label} END) AS raw_targets
            WITH n, [t IN raw_targets WHERE t IS NOT NULL AND (t.qid IS NOT NULL OR t.label IS NOT NULL)] AS p31_targets
            WITH n, p31_targets,
                 size(p31_targets) > 0 AND any(t IN p31_targets WHERE (t.qid = 'Q5' OR toLower(coalesce(t.label, '')) = 'human')) AS has_human_p31
            WHERE (size(p31_targets) = 0) OR (NOT has_human_p31)
            RETURN n.entity_id AS entity_id,
                   n.entity_cipher AS entity_cipher,
                   n.qid AS qid,
                   n.label AS label,
                   n.entity_type AS entity_type,
                   p31_targets
            ORDER BY n.label
        """)
        rows = [dict(r) for r in result]

    # Classify each
    classified = []
    for r in rows:
        dq_flag = classify_noise_node(r["label"], r.get("qid"), r.get("p31_targets") or [])
        classified.append({
            **r,
            "dq_flag": dq_flag,
            "suggested_entity_type": get_entity_type_from_p31(r.get("p31_targets") or [])
                if dq_flag == "DQ_WRONG_ENTITY_TYPE" else None,
        })

    return {
        "total": len(classified),
        "by_flag": {
            "DQ_WRONG_ENTITY_TYPE": [c for c in classified if c["dq_flag"] == "DQ_WRONG_ENTITY_TYPE"],
            "DQ_UNRESOLVED_PERSONHOOD": [c for c in classified if c["dq_flag"] == "DQ_UNRESOLVED_PERSONHOOD"],
            "DQ_MISSING_P31": [c for c in classified if c["dq_flag"] == "DQ_MISSING_P31"],
        },
        "classified": classified,
    }


def apply_remediation(driver, database: str, report: dict, dry_run: bool = True) -> dict:
    """Apply ADR-007 Section 3 remediation actions."""
    stats = {"reclassified": 0, "mythological": 0, "biblical_queued": 0, "errors": []}

    with driver.session(database=database) as session:
        # 1. Non-persons: reclassify entity_type, re-ID, no :Person
        for c in report["by_flag"].get("DQ_WRONG_ENTITY_TYPE", []):
            entity_id = c.get("entity_id") or c.get("entity_cipher")
            entity_cipher = c.get("entity_cipher")
            new_type = c.get("suggested_entity_type") or "CONCEPT"
            prefix = get_prefix_for_entity_type(new_type)
            qid = c.get("qid")
            new_entity_id = f"{prefix}_q{qid[1:].lower()}" if qid else f"{prefix}_{(entity_id or 'unknown').replace('person_', '')}"
            new_cipher = generate_entity_cipher(qid or f"crys_{entity_id}", new_type, "wd" if qid else "crys") if generate_entity_cipher else f"ent_{prefix}_{qid or entity_id}"
            try:
                if not dry_run:
                    session.run("""
                        MATCH (n:Entity)
                        WHERE n.entity_id = $entity_id OR n.entity_cipher = $entity_cipher
                        SET n.entity_type = $new_type,
                            n.entity_id = $new_entity_id,
                            n.entity_cipher = $new_cipher,
                            n.dq_flag = $dq_flag
                        """,
                        entity_id=entity_id,
                        entity_cipher=entity_cipher,
                        new_type=new_type,
                        new_entity_id=new_entity_id,
                        new_cipher=new_cipher,
                        dq_flag="DQ_WRONG_ENTITY_TYPE",
                    )
                stats["reclassified"] += 1
            except Exception as e:
                stats["errors"].append(f"Reclassify {entity_id}: {e}")

        # 2. Mythological: add :MythologicalPerson, mythological=true
        for c in report["by_flag"].get("DQ_UNRESOLVED_PERSONHOOD", []):
            entity_id = c.get("entity_id") or c.get("entity_cipher")
            try:
                if not dry_run:
                    session.run("""
                        MATCH (n:Entity)
                        WHERE n.entity_id = $entity_id OR n.entity_cipher = $entity_cipher
                        SET n:Person:MythologicalPerson,
                            n.mythological = true,
                            n.dq_flag = $dq_flag
                        """,
                        entity_id=entity_id,
                        entity_cipher=c.get("entity_cipher"),
                        dq_flag="DQ_UNRESOLVED_PERSONHOOD",
                    )
                stats["mythological"] += 1
            except Exception as e:
                stats["errors"].append(f"Mythological {entity_id}: {e}")

        # 3. Biblical: queue P31 re-fetch (write to queue file)
        biblical = report["by_flag"].get("DQ_MISSING_P31", [])
        for c in biblical:
            stats["biblical_queued"] += 1
        if biblical and not dry_run:
            queue_path = Path(__file__).parent.parent.parent / "output" / "person_cleanup" / "p31_refetch_queue.json"
            queue_path.parent.mkdir(parents=True, exist_ok=True)
            with open(queue_path, "w") as f:
                json.dump([{"qid": c.get("qid"), "label": c.get("label")} for c in biblical], f, indent=2)

    return stats


def main():
    parser = argparse.ArgumentParser(description="ADR-007 Section 3: Person noise cleanup")
    parser.add_argument("--report", action="store_true", help="Report only (no changes)")
    parser.add_argument("--apply", action="store_true", help="Apply remediation")
    parser.add_argument("--dry-run", action="store_true", help="With --apply: report what would be done")
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--database", default=NEO4J_DATABASE)
    parser.add_argument("--output", "-o", help="Write report JSON to file")
    args = parser.parse_args()

    if not GraphDatabase:
        print("ERROR: neo4j driver not installed. pip install neo4j")
        sys.exit(1)
    if not args.password:
        print("ERROR: NEO4J_PASSWORD not set. Use .env or --password")
        sys.exit(1)

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    print("=" * 60)
    print("ADR-007 Section 3: Person Noise Cleanup")
    print("=" * 60)

    report = run_report(driver, args.database or "neo4j")

    print(f"\nTotal noise nodes: {report['total']}")
    for flag, items in report["by_flag"].items():
        print(f"  {flag}: {len(items)}")
    print()

    for flag, items in report["by_flag"].items():
        if items:
            print(f"\n--- {flag} ---")
            for c in items:
                lbl = (c.get("label") or "").encode("ascii", "replace").decode("ascii")
                print(f"  {lbl} | {c.get('entity_id')} | qid={c.get('qid')} | p31={c.get('p31_targets')}")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport written to {out_path}")

    if args.apply:
        dry = args.dry_run
        print(f"\n{'[DRY RUN] ' if dry else ''}Applying remediation...")
        stats = apply_remediation(driver, args.database or "neo4j", report, dry_run=dry)
        print(f"  Reclassified (non-persons): {stats['reclassified']}")
        print(f"  MythologicalPerson: {stats['mythological']}")
        print(f"  Biblical (P31 queue): {stats['biblical_queued']}")
        if stats["errors"]:
            for e in stats["errors"]:
                print(f"  ERROR: {e}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
