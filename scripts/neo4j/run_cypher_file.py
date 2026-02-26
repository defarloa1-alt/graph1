#!/usr/bin/env python3
"""
Run a Cypher file against Neo4j.

Splits the file into statements (by semicolon), skips comments and empty lines,
and executes each statement. Reports progress and errors.

Usage:
    python scripts/neo4j/run_cypher_file.py output/neo4j/relationships_comprehensive_20260223_080645.cypher
    python scripts/neo4j/run_cypher_file.py <cypher_file> [--batch-size 100] [--dry-run]
"""

import sys
import re
from pathlib import Path

from neo4j import GraphDatabase

# Neo4j connection: prefer config_loader (.env) so run_cypher_file uses project credentials
try:
    import sys
    from pathlib import Path
    _scripts = Path(__file__).resolve().parents[1]
    if str(_scripts) not in sys.path:
        sys.path.insert(0, str(_scripts))
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    NEO4J_USER = NEO4J_USERNAME
except ImportError:
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = None


def split_statements(content: str) -> list[str]:
    """Split Cypher content into executable statements (by semicolon)."""
    raw = content.strip()
    # Split on semicolon + newline; each chunk is a statement
    chunks = re.split(r";\s*\n", raw)
    statements = []
    for chunk in chunks:
        # Remove leading comment lines from chunk
        lines = [ln for ln in chunk.split("\n") if ln.strip() and not ln.strip().startswith("//")]
        stmt = "\n".join(lines).strip()
        if stmt:
            # Ensure statement ends with semicolon for Neo4j
            if not stmt.endswith(";"):
                stmt += ";"
            statements.append(stmt)
    return statements


def run_cypher_file(
    cypher_path: str,
    uri: str = NEO4J_URI,
    user: str = NEO4J_USER,
    password: str = NEO4J_PASSWORD,
    batch_size: int = 100,
    dry_run: bool = False,
) -> tuple[int, int]:
    """
    Execute a Cypher file against Neo4j.

    Returns:
        (success_count, error_count)
    """
    path = Path(cypher_path)
    if not path.exists():
        print(f"Error: File not found: {cypher_path}")
        return 0, 0

    content = path.read_text(encoding="utf-8")
    statements = split_statements(content)

    # Filter to non-empty, non-comment statements
    statements = [s for s in statements if s.strip() and not s.strip().startswith("//")]

    print(f"\n{'='*80}")
    print(f"RUN CYPHER FILE")
    print(f"{'='*80}\n")
    print(f"File: {cypher_path}")
    print(f"Statements: {len(statements)}")
    print(f"Batch size: {batch_size}")
    print(f"Dry run: {dry_run}\n")

    if dry_run:
        for i, stmt in enumerate(statements[:5], 1):
            preview = stmt[:120].replace("\n", " ")
            print(f"  {i}. {preview}...")
        if len(statements) > 5:
            print(f"  ... and {len(statements) - 5} more")
        print()
        return 0, 0

    driver = GraphDatabase.driver(uri, auth=(user, password))
    success = 0
    errors = 0

    try:
        with driver.session() as session:
            for i, stmt in enumerate(statements, 1):
                try:
                    session.run(stmt)
                    success += 1
                    if i % batch_size == 0:
                        print(f"  Progress: {i}/{len(statements)} ({success} ok, {errors} failed)")
                except Exception as e:
                    errors += 1
                    print(f"  Error at statement {i}: {e}")
                    if errors <= 3:
                        print(f"    Statement: {stmt[:200]}...")
    finally:
        driver.close()

    print(f"\nDone: {success} succeeded, {errors} failed")
    return success, errors


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run Cypher file against Neo4j")
    parser.add_argument("cypher_file", help="Path to .cypher file")
    parser.add_argument("--batch-size", type=int, default=100, help="Progress report interval")
    parser.add_argument("--dry-run", action="store_true", help="Show statements without executing")
    parser.add_argument("--uri", default=NEO4J_URI, help="Neo4j URI")
    parser.add_argument("--user", default=NEO4J_USER, help="Neo4j user")
    parser.add_argument("--password", default=NEO4J_PASSWORD, help="Neo4j password")

    args = parser.parse_args()

    run_cypher_file(
        args.cypher_file,
        uri=args.uri,
        user=args.user,
        password=args.password,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
