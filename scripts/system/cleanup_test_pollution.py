"""
Remove session test pollution from canonical Neo4j.

Deletes:
  - Fake Events (test QIDs / start_date=unknown test labels)
  - Fake demo Person nodes
  - MilitaryPrinciple + Boyd SPO cluster (domain=military_theory)
  - Demo/test Agent ASSERTS and REVIEWED edges
  - Orphan demo/test Agent nodes

Does NOT delete:
  - Methodology Mechanism nodes (M_ESCALATION, etc.) — only unlinks
    erroneous Domain:military_theory -[:CONTAINS]-> edges
  - Real entities (Cannae Q179591, real Caesar Q1048)
  - Note: Q36456 is Wikidata Hannibal — not the Battle of Cannae

Usage:
  python scripts/system/cleanup_test_pollution.py --dry-run
  python scripts/system/cleanup_test_pollution.py --apply
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

FAKE_EVENT_QIDS = [
    "Q_WORKFLOW_TEST",
    "Q_METADATA_TEST",
    "Q40979_MILITARY_TEST",
    "Q_TEST_NO_WEIGHT",
    "Q_819760b9b4f7243d",
]

FAKE_PERSON_QIDS = [
    "Q1048_DEMO_P2",
    "Q1048_TEST_PR",
]

DEMO_AGENT_IDS = [
    "demo_p2_economic_reviewer",
    "demo_p2_economic_sfa",
    "demo_p2_military_sfa",
    "demo_p2_political_reviewer",
    "demo_p2_political_sfa",
    "demo_p2_social_reviewer",
    "test_military_political",
    "test_pr_economic",
    "test_pr_mil",
    "test_pr_political",
    "SFA_MILITARY",
    "military_sfa_001",
    "military_sfa_001_enhanced",
]


def connect():
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(
            os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER"),
            os.getenv("NEO4J_PASSWORD"),
        ),
    ), os.getenv("NEO4J_DATABASE") or "neo4j"


def preview(session) -> None:
    print("\n=== PREVIEW: fake Events ===")
    for r in session.run(
        """
        MATCH (e:Event)
        WHERE e.qid IN $qids
           OR (e.start_date = 'unknown' AND toLower(coalesce(e.label,'')) CONTAINS 'test')
        RETURN e.qid AS qid, e.label AS label
        """,
        qids=FAKE_EVENT_QIDS,
    ):
        print(" ", dict(r))

    print("\n=== PREVIEW: fake Persons ===")
    for r in session.run(
        "MATCH (p:Person) WHERE p.qid IN $qids RETURN p.qid AS qid, p.label AS label",
        qids=FAKE_PERSON_QIDS,
    ):
        print(" ", dict(r))

    print("\n=== PREVIEW: Boyd/MilitaryPrinciple SPO junk ===")
    for r in session.run(
        """
        MATCH (n)
        WHERE n:MilitaryPrinciple
           OR (n.domain = 'military_theory' AND (
                n:Concept OR n:Mechanism OR n:Effect OR n:Condition
                OR n:Target OR n:Process))
           OR (n.subject = 'military_theory' AND n:MilitaryPrinciple)
        RETURN labels(n) AS labels,
               coalesce(n.principle_id, n.name, n.label, n.id) AS name
        ORDER BY labels[0], name
        """
    ):
        print(" ", dict(r))

    print("\n=== PREVIEW: methodology Mechanisms to UNLINK only (keep nodes) ===")
    for r in session.run(
        """
        MATCH (:Domain {domain_id: 'military_theory'})-[:CONTAINS]->(m:Mechanism)
        WHERE m.id STARTS WITH 'M_'
        RETURN m.id AS id, m.label AS label
        """
    ):
        print(" ", dict(r))

    print("\n=== PREVIEW: demo ASSERTS on real Cannae (drop edges, keep Event) ===")
    for r in session.run(
        """
        MATCH (a:Agent)-[c:ASSERTS]->(e:Event {qid: 'Q36456'})
        WHERE a.agent_id IN $agents
        RETURN a.agent_id AS agent, c.predicate AS predicate
        """,
        agents=DEMO_AGENT_IDS,
    ):
        print(" ", dict(r))

    print("\n=== PREVIEW: demo/test Agents ===")
    for r in session.run(
        """
        MATCH (a:Agent)
        WHERE a.agent_id IN $agents
        RETURN a.agent_id AS agent_id
        ORDER BY agent_id
        """,
        agents=DEMO_AGENT_IDS,
    ):
        print(" ", dict(r))


def apply(session) -> dict:
    counts: dict[str, int] = {}

    # 1. Drop demo ASSERTS on real Cannae (keep the Event)
    result = session.run(
        """
        MATCH (a:Agent)-[c:ASSERTS]->(e:Event {qid: 'Q36456'})
        WHERE a.agent_id IN $agents
        DELETE c
        RETURN count(c) AS n
        """,
        agents=DEMO_AGENT_IDS,
    ).single()
    counts["asserts_on_real_cannae"] = result["n"]

    # 2. Unlink methodology Mechanisms from military_theory Domain
    result = session.run(
        """
        MATCH (d:Domain {domain_id: 'military_theory'})-[c:CONTAINS]->(m:Mechanism)
        WHERE m.id STARTS WITH 'M_'
        DELETE c
        RETURN count(c) AS n
        """
    ).single()
    counts["unlinked_methodology_mechanisms"] = result["n"]

    # 3. Delete Boyd SPO cluster + MilitaryPrinciple
    result = session.run(
        """
        MATCH (n)
        WHERE n:MilitaryPrinciple
           OR (n.domain = 'military_theory' AND (
                n:Concept OR n:Mechanism OR n:Effect OR n:Condition
                OR n:Target OR n:Process))
        DETACH DELETE n
        RETURN count(n) AS n
        """
    ).single()
    counts["boyd_spo_nodes"] = result["n"]

    # 4. Delete fake Events
    result = session.run(
        """
        MATCH (e:Event)
        WHERE e.qid IN $qids
           OR (e.start_date = 'unknown' AND (
                toLower(coalesce(e.label,'')) CONTAINS 'test'
                OR e.qid CONTAINS '_TEST'
                OR e.qid STARTS WITH 'Q_819'))
        DETACH DELETE e
        RETURN count(e) AS n
        """,
        qids=FAKE_EVENT_QIDS,
    ).single()
    counts["fake_events"] = result["n"]

    # 5. Delete fake Persons
    result = session.run(
        """
        MATCH (p:Person)
        WHERE p.qid IN $qids
        DETACH DELETE p
        RETURN count(p) AS n
        """,
        qids=FAKE_PERSON_QIDS,
    ).single()
    counts["fake_persons"] = result["n"]

    # 6. Delete remaining demo Agent edges then Agents
    result = session.run(
        """
        MATCH (a:Agent)
        WHERE a.agent_id IN $agents
        OPTIONAL MATCH (a)-[r]-()
        DELETE r
        WITH DISTINCT a
        DETACH DELETE a
        RETURN count(a) AS n
        """,
        agents=DEMO_AGENT_IDS,
    ).single()
    counts["demo_agents"] = result["n"]

    return counts


def verify(session) -> dict:
    return {
        "MilitaryPrinciple": session.run(
            "MATCH (n:MilitaryPrinciple) RETURN count(n) AS n"
        ).single()["n"],
        "fake_events": session.run(
            """
            MATCH (e:Event)
            WHERE e.qid IN $qids OR e.start_date = 'unknown'
            RETURN count(e) AS n
            """,
            qids=FAKE_EVENT_QIDS,
        ).single()["n"],
        "fake_persons": session.run(
            "MATCH (p:Person) WHERE p.qid IN $qids RETURN count(p) AS n",
            qids=FAKE_PERSON_QIDS,
        ).single()["n"],
        "demo_agents": session.run(
            "MATCH (a:Agent) WHERE a.agent_id IN $agents RETURN count(a) AS n",
            agents=DEMO_AGENT_IDS,
        ).single()["n"],
        "asserts_total": session.run(
            "MATCH ()-[c:ASSERTS]->() RETURN count(c) AS n"
        ).single()["n"],
        "military_theory_children": [
            dict(r)
            for r in session.run(
                """
                MATCH (d:Domain {domain_id: 'military_theory'})-[:CONTAINS]->(n)
                RETURN labels(n) AS labels, count(*) AS n
                ORDER BY n DESC
                """
            )
        ],
        "methodology_mechanisms_kept": session.run(
            "MATCH (m:Mechanism) WHERE m.id STARTS WITH 'M_' RETURN count(m) AS n"
        ).single()["n"],
        "real_cannae": session.run(
            "MATCH (e:Event {qid: 'Q36456'}) RETURN e.label AS label, e.start_date AS start_date"
        ).single(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Specify --dry-run or --apply")

    driver, database = connect()
    try:
        with driver.session(database=database) as session:
            preview(session)
            if args.dry_run:
                print("\n[done] dry-run — no writes")
                return

            counts = apply(session)
            print("\n=== DELETED / UNLINKED ===")
            for k, v in counts.items():
                print(f"  {k}: {v}")

            after = verify(session)
            print("\n=== AFTER ===")
            for k, v in after.items():
                if k == "real_cannae" and v:
                    print(f"  {k}: {dict(v)}")
                else:
                    print(f"  {k}: {v}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
