"""
Run a .cypher file against Neo4j using the Python driver.

Usage:
  python Neo4j/schema/run_cypher_file.py Neo4j/schema/09_core_pipeline_pilot_seed.cypher
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from neo4j import GraphDatabase


def parse_statements(text: str) -> list[str]:
    # Split only on semicolons that are outside quoted strings.
    # This avoids breaking statements that contain text literals like:
    # "foo; bar"
    chunks: list[str] = []
    buf: list[str] = []
    in_single = False
    in_double = False
    escape = False

    for ch in text:
        if escape:
            buf.append(ch)
            escape = False
            continue

        if ch == "\\":
            buf.append(ch)
            escape = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            continue

        if ch == ";" and not in_single and not in_double:
            chunks.append("".join(buf))
            buf = []
            continue

        buf.append(ch)

    if buf:
        chunks.append("".join(buf))

    statements: list[str] = []
    for chunk in chunks:
        lines = [ln for ln in chunk.splitlines() if ln.strip() and not ln.strip().startswith("//")]
        q = "\n".join(lines).strip()
        if q:
            statements.append(q)
    return statements


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cypher_file", help="Path to .cypher file")
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD", "Chrystallum"))
    args = parser.parse_args()

    path = Path(args.cypher_file)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    statements = parse_statements(path.read_text(encoding="utf-8"))
    if not statements:
        print("No executable statements found.")
        return 0

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    try:
        with driver.session() as session:
            for i, stmt in enumerate(statements, start=1):
                result = session.run(stmt)
                rows = result.data()
                if rows:
                    print(f"Statement {i} returned {len(rows)} row(s):")
                    for row in rows:
                        print(row)
                print(f"Executed statement {i}/{len(statements)}")
    finally:
        driver.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
