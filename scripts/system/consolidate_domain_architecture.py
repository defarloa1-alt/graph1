"""
Consolidate domain architecture on canonical :Domain nodes.

Scope (in): roman_republic, military_theory
Scope (out): geography domain wrapper

Removes duplicate SubjectConcept {is_domain:true} shells after migrating
HAS_VERSION edges to Domain nodes.

Usage:
  python scripts/system/consolidate_domain_architecture.py --dry-run
  python scripts/system/consolidate_domain_architecture.py --apply
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
load_dotenv()

IN_SCOPE = ("roman_republic", "military_theory")
OUT_OF_SCOPE = ("geography",)
DOMAIN_SHELL_SUBJECT_IDS = IN_SCOPE


def connect():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE") or "neo4j"
    return GraphDatabase.driver(uri, auth=(user, password)), database


def audit(session) -> dict:
    """Collect pre-migration state."""
    report: dict = {}

    report["domains"] = [
        dict(r)
        for r in session.run(
            """
            MATCH (d:Domain)
            RETURN d.domain_id AS domain_id, d.label AS label, d.version AS version
            ORDER BY domain_id
            """
        )
    ]

    report["domain_shell_scs"] = [
        dict(r)
        for r in session.run(
            """
            MATCH (sc:SubjectConcept)
            WHERE sc.subject_id IN $ids
            RETURN sc.subject_id AS subject_id, sc.is_domain AS is_domain,
                   sc.version AS version, sc.label AS label
            """,
            ids=list(DOMAIN_SHELL_SUBJECT_IDS),
        )
    ]

    report["version_edges"] = [
        dict(r)
        for r in session.run(
            """
            MATCH (parent)-[:HAS_VERSION]->(v:Version)
            RETURN labels(parent) AS parent_labels,
                   coalesce(parent.domain_id, parent.subject_id) AS parent_id,
                   v.version AS version,
                   v.subject_id AS v_subject_id,
                   v.domain_id AS v_domain_id
            ORDER BY parent_id, v.version
            """
        )
    ]

    report["depends_on"] = [
        dict(r)
        for r in session.run(
            """
            MATCH (a)-[r:DEPENDS_ON]->(b)
            RETURN labels(a) AS a_labels, coalesce(a.domain_id, a.subject_id) AS a_id,
                   labels(b) AS b_labels, coalesce(b.domain_id, b.subject_id) AS b_id,
                   r.version_spec AS version_spec
            """
        )
    ]

    report["geography_children"] = [
        dict(r)
        for r in session.run(
            """
            MATCH (d:Domain {domain_id: 'geography'})-[:CONTAINS]->(child)
            RETURN labels(child) AS labels, coalesce(child.subject_id, child.label) AS id
            """
        )
    ]

    report["tracks_domain"] = [
        dict(r)
        for r in session.run(
            """
            MATCH (scr:SubjectConceptRegistry)-[:TRACKS_DOMAIN]->(d:Domain)
            RETURN d.domain_id AS domain_id
            ORDER BY domain_id
            """
        )
    ]

    report["subject_domain_anchor"] = [
        dict(r)
        for r in session.run(
            """
            MATCH (sd:SubjectDomain)
            RETURN sd.domain_id AS domain_id, sd.label AS label, sd.seed_qid AS seed_qid
            """
        )
    ]

    return report


def print_report(title: str, report: dict) -> None:
    print(f"\n{'=' * 70}")
    print(title)
    print("=" * 70)
    for key, value in report.items():
        print(f"\n[{key}]")
        if value is None or value == "":
            print("  (empty)")
        elif isinstance(value, (int, float, str, bool)):
            print(f"  {value}")
        elif not value:
            print("  (empty)")
        else:
            for row in value:
                print(f"  {row}")


def migrate_versions(session, dry_run: bool) -> int:
    """Move HAS_VERSION from SubjectConcept shells to Domain nodes."""
    rows = list(
        session.run(
            """
            MATCH (sc:SubjectConcept)-[hv:HAS_VERSION]->(v:Version)
            WHERE sc.subject_id IN $ids
            MATCH (d:Domain {domain_id: sc.subject_id})
            RETURN sc.subject_id AS domain_id, v.version AS version,
                   id(sc) AS sc_id, id(v) AS v_id, id(d) AS d_id
            """,
            ids=list(DOMAIN_SHELL_SUBJECT_IDS),
        )
    )
    print(f"\n[migrate_versions] {len(rows)} HAS_VERSION edge(s) to re-home")
    if dry_run:
        for row in rows:
            print(f"  DRY-RUN: {row['domain_id']} v{row['version']} SC -> Domain")
        return len(rows)

    for row in rows:
        session.run(
            """
            MATCH (sc:SubjectConcept {subject_id: $domain_id})-[hv:HAS_VERSION]->(v:Version)
            MATCH (d:Domain {domain_id: $domain_id})
            MERGE (d)-[:HAS_VERSION]->(v)
            SET v.domain_id = $domain_id
            DELETE hv
            """,
            domain_id=row["domain_id"],
        )
    return len(rows)


def link_subject_domain_anchor(session, dry_run: bool) -> None:
    """Connect legacy SubjectDomain seed anchor to Domain roman_republic."""
    exists = session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
        MATCH (d:Domain {domain_id: 'roman_republic'})
        RETURN count(sd) AS n
        """
    ).single()["n"]
    if not exists:
        print("\n[link_anchor] no SubjectDomain anchor found — skip")
        return

    print("\n[link_anchor] MERGE (SubjectDomain)-[:SEED_FOR]->(Domain:roman_republic)")
    if dry_run:
        return

    session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
        MATCH (d:Domain {domain_id: 'roman_republic'})
        MERGE (sd)-[:SEED_FOR]->(d)
        SET sd.status = coalesce(sd.status, 'active'),
            d.seed_qid = coalesce(d.seed_qid, sd.seed_qid, 'Q17167')
        """
    )


def remove_geography_domain(session, dry_run: bool) -> None:
    print("\n[remove_geography] detach GEO SubjectConcepts and delete Domain:geography")
    children = list(
        session.run(
            """
            MATCH (d:Domain {domain_id: 'geography'})-[:CONTAINS]->(child)
            RETURN coalesce(child.subject_id, child.label) AS id
            """
        )
    )
    for row in children:
        print(f"  child kept in graph: {row['id']}")

    if dry_run:
        print("  DRY-RUN: would delete geography Domain + TRACKS_DOMAIN edge")
        return

    session.run(
        """
        MATCH (d:Domain {domain_id: 'geography'})-[c:CONTAINS]->()
        DELETE c
        """
    )
    session.run(
        """
        MATCH (:SubjectConceptRegistry)-[t:TRACKS_DOMAIN]->(d:Domain {domain_id: 'geography'})
        DELETE t
        """
    )
    session.run(
        """
        MATCH (d:Domain {domain_id: 'geography'})
        DETACH DELETE d
        """
    )


def remove_domain_shell_subjectconcepts(session, dry_run: bool) -> int:
    """Delete SubjectConcept nodes that duplicate Domain containers."""
    shells = list(
        session.run(
            """
            MATCH (sc:SubjectConcept)
            WHERE sc.subject_id IN $ids
            OPTIONAL MATCH (sc)-[r]-()
            RETURN sc.subject_id AS subject_id, count(r) AS rel_count
            """,
            ids=list(DOMAIN_SHELL_SUBJECT_IDS),
        )
    )
    print(f"\n[remove_shells] {len(shells)} SubjectConcept domain shell(s)")
    for row in shells:
        print(f"  {row['subject_id']}: {row['rel_count']} remaining rel(s)")

    if dry_run:
        print("  DRY-RUN: would DETACH DELETE shell SubjectConcepts")
        return len(shells)

    result = session.run(
        """
        MATCH (sc:SubjectConcept)
        WHERE sc.subject_id IN $ids
        DETACH DELETE sc
        RETURN count(sc) AS deleted
        """,
        ids=list(DOMAIN_SHELL_SUBJECT_IDS),
    ).single()
    return result["deleted"]


def ensure_registry_tracks_in_scope(session, dry_run: bool) -> None:
    print("\n[registry] ensure SubjectConceptRegistry tracks only in-scope domains")
    if dry_run:
        for domain_id in IN_SCOPE:
            print(f"  DRY-RUN: TRACKS_DOMAIN -> {domain_id}")
        return

    session.run(
        """
        MATCH (scr:SubjectConceptRegistry)
        MATCH (d:Domain)
        WHERE d.domain_id IN $ids
        MERGE (scr)-[:TRACKS_DOMAIN]->(d)
        """,
        ids=list(IN_SCOPE),
    )
    session.run(
        """
        MATCH (scr:SubjectConceptRegistry)-[t:TRACKS_DOMAIN]->(d:Domain)
        WHERE NOT d.domain_id IN $ids
        DELETE t
        """,
        ids=list(IN_SCOPE),
    )


def verify(session) -> dict:
    return {
        "domains": [
            dict(r)
            for r in session.run(
                """
                MATCH (d:Domain)
                RETURN d.domain_id AS domain_id, d.version AS version,
                       size([(d)-[:CONTAINS]->() | 1]) AS children,
                       size([(d)-[:HAS_VERSION]->() | 1]) AS versions
                ORDER BY domain_id
                """
            )
        ],
        "shell_scs_remaining": session.run(
            """
            MATCH (sc:SubjectConcept)
            WHERE sc.subject_id IN $ids OR sc.is_domain = true
            RETURN count(sc) AS n
            """,
            ids=list(DOMAIN_SHELL_SUBJECT_IDS),
        ).single()["n"],
        "geography_domain": session.run(
            "MATCH (d:Domain {domain_id: 'geography'}) RETURN count(d) AS n"
        ).single()["n"],
        "depends_on": [
            dict(r)
            for r in session.run(
                """
                MATCH (a:Domain)-[r:DEPENDS_ON]->(b:Domain)
                RETURN a.domain_id AS dependent, b.domain_id AS dependency,
                       r.version_spec AS version_spec
                """
            )
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Consolidate Domain architecture")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--apply", action="store_true", help="Execute migration")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.error("Specify --dry-run or --apply")

    driver, database = connect()
    try:
        with driver.session(database=database) as session:
            before = audit(session)
            print_report("BEFORE", before)

            dry = args.dry_run
            migrate_versions(session, dry_run=dry)
            link_subject_domain_anchor(session, dry_run=dry)
            remove_geography_domain(session, dry_run=dry)
            remove_domain_shell_subjectconcepts(session, dry_run=dry)
            ensure_registry_tracks_in_scope(session, dry_run=dry)

            if not dry:
                after = verify(session)
                print_report("AFTER", after)
            else:
                print("\n[done] dry-run complete — no writes")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
