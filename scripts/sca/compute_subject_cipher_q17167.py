#!/usr/bin/env python3
"""
Compute content-addressable subject cipher for Roman Republic (Q17167).

Requirement: entity_cipher = Hash(QID + all PID+value pairs) — content-addressable.
The SCA was supposed to persist this. All data comes from the graph (property_summary
or outgoing relationships).

Usage:
  python scripts/sca/compute_subject_cipher_q17167.py --dry-run
  python scripts/sca/compute_subject_cipher_q17167.py --write
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

SUBJECT_QID = "Q17167"


def build_canonical_string(qid: str, property_summary: dict) -> str:
    """
    Build deterministic string for hashing: QID + sorted PID:value pairs.
    Format: Q17167|P31:Q11514315,Q1307214,Q3024240,Q48349|P36:Q220|...
    """
    parts = [qid]
    for pid in sorted(property_summary.keys()):
        values = property_summary[pid]
        if isinstance(values, str):
            values = [values]
        values = sorted(str(v) for v in values)
        parts.append(f"{pid}:{','.join(values)}")
    return "|".join(parts)


def compute_subject_cipher(property_summary: dict) -> str:
    """
    Content-addressable cipher: readable canonical string.
    Format: Q17167|P31:val1,val2|P36:val|... — IDs the subgraph; SFA updates it.
    """
    return build_canonical_string(SUBJECT_QID, property_summary)


def get_property_summary_from_graph(session) -> dict | None:
    """Get property_summary for Q17167 from Neo4j."""
    result = session.run(
        """
        MATCH (e:Entity {qid: $qid})
        RETURN e.property_summary AS ps
        LIMIT 1
        """,
        qid=SUBJECT_QID,
    )
    row = result.single()
    if not row or not row["ps"]:
        return None
    ps = row["ps"]
    if isinstance(ps, str):
        try:
            return ast.literal_eval(ps.replace("'", '"'))
        except (ValueError, SyntaxError):
            try:
                return json.loads(ps.replace("'", '"'))
            except json.JSONDecodeError:
                return None
    return ps if isinstance(ps, dict) else None


def get_property_summary_from_relationships(session) -> dict | None:
    """
    Fallback: collect PID+value from outgoing relationships.
    (e)-[r:P31]->(t) => P31: t.qid
    """
    result = session.run(
        """
        MATCH (e:Entity {qid: $qid})-[r]->(target)
        WHERE type(r) =~ '^P[0-9]+$'
        RETURN type(r) AS pid, collect(DISTINCT target.qid) AS qids
        """,
        qid=SUBJECT_QID,
    )
    rows = list(result)
    if not rows:
        return None
    return {r["pid"]: r["qids"] for r in rows if r["qids"]}


def get_property_summary_from_stub() -> dict:
    """
    Fallback: known Q17167 property_summary from SCA import (output/neo4j/import_with_ciphers).
    Complete PID+value set as persisted by the SCA.
    """
    return {
        "P31": ["Q11514315", "Q1307214", "Q48349", "Q3024240"],
        "P36": ["Q220"],
        "P122": ["Q666680"],
        "P361": ["Q1747689"],
        "P155": ["Q201038"],
        "P527": ["Q2839628", "Q6106068", "Q2815472"],
        "P1366": ["Q2277", "Q206414"],
        "P140": ["Q337547"],
        "P194": ["Q130614", "Q1114821"],
        "P38": ["Q952064"],
        "P2348": ["Q486761"],
        "P1792": ["Q13285410"],
        "P1365": ["Q201038"],
        "P2936": ["Q397", "Q35497"],
        "P30": ["Q46", "Q48", "Q15"],
        "P3075": ["Q337547"],
        "P1889": ["Q346629"],
        "P5008": ["Q6173448"],
        "P793": ["Q124988", "Q3778726", "Q75813", "Q202161", "Q596373"],
        "P910": ["Q6944405"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compute content-addressable subject cipher for Q17167"
    )
    parser.add_argument("--dry-run", action="store_true", help="Compute only, do not write")
    parser.add_argument("--write", action="store_true", help="Update entity_cipher in Neo4j")
    parser.add_argument("--use-stub", action="store_true", help="Use STUBBED_POSITION_MAP if graph has no property_summary")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.error("Specify --dry-run or --write")

    property_summary = None
    source = ""

    if not args.use_stub:
        try:
            from neo4j import GraphDatabase
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD")
            if not uri or not password:
                print("NEO4J_URI and NEO4J_PASSWORD required. Use --use-stub to skip.")
                sys.exit(1)
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                property_summary = get_property_summary_from_graph(session)
                if property_summary:
                    source = "graph (property_summary)"
                else:
                    property_summary = get_property_summary_from_relationships(session)
                    if property_summary:
                        source = "graph (relationships)"
            driver.close()
        except Exception as e:
            print(f"Neo4j error: {e}")
            if not args.use_stub:
                sys.exit(1)

    if not property_summary and args.use_stub:
        property_summary = get_property_summary_from_stub()
        source = "STUBBED_POSITION_MAP + known Q17167 properties"

    if not property_summary:
        print("No property_summary found. Use --use-stub for demo.")
        sys.exit(1)

    cipher = compute_subject_cipher(property_summary)

    print("=" * 60)
    print("SUBJECT CIPHER (Q17167 Roman Republic)")
    print("=" * 60)
    print(f"Source: {source}")
    print(f"Properties: {len(property_summary)} PIDs")
    print(f"entity_cipher (readable, IDs subgraph):")
    print(f"  {cipher[:120]}..." if len(cipher) > 120 else f"  {cipher}")
    print(f"  Length: {len(cipher)} chars")
    print("=" * 60)

    if args.write:
        try:
            from neo4j import GraphDatabase
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD")
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                session.run(
                    """
                    MATCH (e:Entity {qid: $qid})
                    SET e.entity_cipher = $cipher,
                        e.subject_cipher_computed_at = datetime()
                    RETURN e.qid AS qid
                    """,
                    qid=SUBJECT_QID,
                    cipher=cipher,
                )
            driver.close()
            print(f"Updated Entity {SUBJECT_QID} with entity_cipher = {cipher}")
        except Exception as e:
            print(f"Write failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
