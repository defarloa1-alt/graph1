#!/usr/bin/env python3
"""
Runner for claude/extracted Cypher scripts.
Uses config_loader for credentials.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase


def parse_statements(text: str) -> list:
    chunks = []
    buf = []
    in_single = False
    in_double = False
    escape = False
    i = 0
    chars = text

    while i < len(chars):
        ch = chars[i]

        # Handle escape sequences
        if escape:
            buf.append(ch)
            escape = False
            i += 1
            continue

        if ch == "\\":
            buf.append(ch)
            escape = True
            i += 1
            continue

        # Skip line comments outside strings
        if ch == "/" and not in_single and not in_double:
            if i + 1 < len(chars) and chars[i + 1] == "/":
                # skip to end of line
                while i < len(chars) and chars[i] != "\n":
                    i += 1
                continue

        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            i += 1
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            i += 1
            continue

        if ch == ";" and not in_single and not in_double:
            chunks.append("".join(buf))
            buf = []
            i += 1
            continue

        buf.append(ch)
        i += 1

    if buf:
        chunks.append("".join(buf))

    statements = []
    for chunk in chunks:
        lines = [ln for ln in chunk.splitlines() if ln.strip()]
        q = "\n".join(lines).strip()
        if q:
            statements.append(q)
    return statements


def run_file(path: Path, driver):
    statements = parse_statements(path.read_text(encoding="utf-8"))
    print(f"\n=== {path.name}: {len(statements)} statements ===")
    with driver.session() as session:
        for i, stmt in enumerate(statements, 1):
            result = session.run(stmt)
            rows = result.data()
            if rows:
                print(f"  [{i}] {len(rows)} row(s): {rows[:3]}")
            else:
                print(f"  [{i}] OK")
    print(f"  Done: {path.name}")


def validate(queries: list, driver):
    print("\n--- Validation ---")
    with driver.session() as session:
        for label, q in queries:
            rows = session.run(q).data()
            print(f"  {label}: {rows}")


if __name__ == "__main__":
    script_num = sys.argv[1] if len(sys.argv) > 1 else None
    base = Path(__file__).parent / "extracted"

    files = sorted(base.glob("*.cypher"))
    if script_num:
        files = [f for f in files if f.name.startswith(script_num + "_")]

    if not files:
        print(f"No files matched.")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        for f in files:
            run_file(f, driver)
    finally:
        driver.close()
    print("\nAll done.")
