"""Validate the clean-start Entity subtype and Year backbone invariants.

Run with the Neo4j connection variables in the process environment:

    python -m GraphRevised.validate_ontology

The command is read-only and returns a non-zero exit status when an invariant
is violated.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from neo4j import GraphDatabase
from GraphRevised import localdb


SUBTYPES = (
    "Person",
    "Place",
    "Event",
    "Group",
    "Work",
    "Object",
    "Period",
    "Office",
    "Concept",
    "Polity",
    "Type",
    "Question",
    "Position",
    "Law",
    "Decree",
    "Other",
)


def one(tx: Any, query: str, **parameters: Any) -> Any:
    record = tx.run(query, **parameters).single()
    if record is None:
        raise RuntimeError("ontology validation query returned no record")
    return record[0]


def validate(tx: Any) -> dict[str, int]:
    subtype_counts = tx.run(
        """
        MATCH (entity:Entity)
        RETURN count(entity) AS total,
               sum(CASE WHEN size([label IN labels(entity) WHERE label IN $subtypes]) = 0
                        THEN 1 ELSE 0 END) AS untyped,
               sum(CASE WHEN size([label IN labels(entity) WHERE label IN $subtypes]) > 1
                        THEN 1 ELSE 0 END) AS multiply_typed
        """,
        subtypes=SUBTYPES,
    ).single()
    if subtype_counts is None:
        raise RuntimeError("Entity validation query returned no record")

    result = {
        "entities": subtype_counts["total"],
        "untyped_entities": subtype_counts["untyped"],
        "multiply_typed_entities": subtype_counts["multiply_typed"],
        "residual_kind_properties": one(
            tx, "MATCH (entity:Entity) WHERE entity.kind IS NOT NULL RETURN count(entity)"
        ),
        "entity_year_nodes": one(tx, "MATCH (:Entity:Year) RETURN count(*)"),
        "years": one(tx, "MATCH (year:Year) RETURN count(year)"),
        "followed_by": one(tx, "MATCH (:Year)-[:FOLLOWED_BY]->(:Year) RETURN count(*)"),
        "year_zero_nodes": one(tx, "MATCH (year:Year {year: 0}) RETURN count(year)"),
    }

    failures = {
        key: value
        for key, value in result.items()
        if key in {"untyped_entities", "multiply_typed_entities", "residual_kind_properties",
                   "entity_year_nodes", "year_zero_nodes"} and value != 0
    }
    if result["followed_by"] != result["years"] - 1:
        failures["followed_by"] = result["followed_by"]
    if failures:
        details = ", ".join(f"{key}={value}" for key, value in sorted(failures.items()))
        raise RuntimeError(f"ontology validation failed: {details}")
    return result


def main() -> int:
    password = os.environ.get("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD is required", file=sys.stderr)
        return 2
    driver = GraphDatabase.driver(
        localdb.uri(),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), password),
    )
    try:
        with driver.session(database=localdb.database()) as session:
            result = session.execute_read(validate)
    finally:
        driver.close()
    for key, value in result.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
