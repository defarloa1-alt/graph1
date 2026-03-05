#!/usr/bin/env python3
"""
SCA Persist — write traversal findings to Neo4j.

Creates/updates:
  - WikidataType nodes (ontology lookup)
  - SubjectDomain node (skeleton per subject)
  - Links SubjectConcept -[:HAS_DOMAIN_STRUCTURE]-> SubjectDomain
  - Links SubjectDomain -[:USES_TYPE]-> WikidataType

Usage:
  python scripts/sca/sca_persist.py -i output/sca/Q17167_domain.json
  python scripts/sca/sca_persist.py -i output/sca/Q17167_domain.json --neo4j-uri bolt://localhost:7687
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))


def get_driver(uri: str | None = None, user: str = "neo4j", password: str | None = None):
    """Get Neo4j driver from args or config."""
    if not uri or not password:
        try:
            from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
            uri = uri or NEO4J_URI
            user = user or NEO4J_USERNAME
            password = password or NEO4J_PASSWORD
        except ImportError:
            pass
        if not uri or not password:
            try:
                import os
                from dotenv import load_dotenv
                load_dotenv(_root / ".env")
                uri = uri or os.getenv("NEO4J_URI")
                password = password or os.getenv("NEO4J_PASSWORD")
            except ImportError:
                pass
    if not uri or not password:
        raise ValueError("Neo4j URI and password required (config_loader, .env, or --neo4j-uri/--neo4j-password)")
    from neo4j import GraphDatabase
    return GraphDatabase.driver(uri, auth=(user, password))


def persist(data: dict, driver) -> None:
    """Write traversal output to Neo4j."""
    seed_qid = data["seed_qid"]
    ts = data.get("timestamp", "")
    summary = data.get("summary", {})
    types_list = data.get("types", [])
    structural = data.get("structural_props", {})
    training_qids = data.get("training_qids", [])

    with driver.session() as session:
        # 1. SubjectDomain (or update)
        session.run(
            """
            MERGE (d:SubjectDomain {seed_qid: $seed_qid})
            SET d.timestamp = $ts,
                d.types_count = $types_count,
                d.backlinks_total = $backlinks_total,
                d.training_qids_count = $training_qids_count,
                d.structural_props = $structural_props,
                d.updated_by = 'sca_persist'
            """,
            seed_qid=seed_qid,
            ts=ts,
            types_count=summary.get("types_discovered", 0),
            backlinks_total=summary.get("backlinks_total", 0),
            training_qids_count=summary.get("training_qids_count", 0),
            structural_props=json.dumps(structural),
        )

        # 2. WikidataType nodes
        for t in types_list:
            qid = t.get("qid", "")
            label = t.get("label", "")
            tier = t.get("tier", "primary")
            depth = t.get("depth", 0)
            backlink_count = t.get("backlink_count", 0)
            boundary = t.get("traversal_boundary", False)
            session.run(
                """
                MERGE (w:WikidataType {qid: $qid})
                SET w.label = $label,
                    w.tier = $tier,
                    w.depth = $depth,
                    w.backlink_count = $backlink_count,
                    w.traversal_boundary = $boundary,
                    w.updated_by = 'sca_persist'
                """,
                qid=qid,
                label=label,
                tier=tier,
                depth=depth,
                backlink_count=backlink_count,
                boundary=boundary,
            )

        # 3. SubjectDomain -[:USES_TYPE]-> WikidataType
        for t in types_list:
            qid = t.get("qid", "")
            if qid:
                session.run(
                    """
                    MATCH (d:SubjectDomain {seed_qid: $seed_qid})
                    MATCH (w:WikidataType {qid: $type_qid})
                    MERGE (d)-[:USES_TYPE]->(w)
                    """,
                    seed_qid=seed_qid,
                    type_qid=qid,
                )

        # 4. Link SubjectConcept to SubjectDomain (if SubjectConcept exists)
        session.run(
            """
            MATCH (d:SubjectDomain {seed_qid: $seed_qid})
            OPTIONAL MATCH (sc:SubjectConcept) WHERE sc.qid = $seed_qid
            WITH d, sc WHERE sc IS NOT NULL
            MERGE (sc)-[:HAS_DOMAIN_STRUCTURE]->(d)
            """,
            seed_qid=seed_qid,
        )

        # 5. Store training_qids on SubjectDomain (truncate if large)
        # Support both [{qid, label}, ...] and [qid, ...] formats
        to_store = training_qids[:500]
        qids_json = json.dumps(to_store)
        session.run(
            """
            MATCH (d:SubjectDomain {seed_qid: $seed_qid})
            SET d.training_qids = $qids
            """,
            seed_qid=seed_qid,
            qids=qids_json,
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Persist SCA traversal to Neo4j")
    ap.add_argument("-i", "--input", required=True, help="JSON file from sca_traversal_engine.py")
    ap.add_argument("--neo4j-uri", default=None)
    ap.add_argument("--neo4j-password", default=None)
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        driver = get_driver(uri=args.neo4j_uri, password=args.neo4j_password)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    try:
        persist(data, driver)
        print(f"Persisted {data['seed_qid']} to Neo4j: {data['summary']['types_discovered']} types, {data['summary']['training_qids_count']} training QIDs")
    finally:
        driver.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
