"""
Milligan digital methodology overlay — DigitalPrinciple checks.

Agents consult these before emitting digital-history claims.
"""
from __future__ import annotations


def fetch_relevant_principles(task_types: list[str], driver=None) -> list[dict]:
    """
    Fetch DigitalPrinciples that impose constraints on the given TaskTypes.

    Returns list of {id, label, constraint}.
    """
    if not driver:
        return []
    cypher = """
    MATCH (dp:DigitalPrinciple)-[:IMPOSES_CONSTRAINT_ON]->(tt:TaskType)
    WHERE tt.id IN $task_types
    RETURN DISTINCT dp.id AS id, dp.label AS label, dp.constraint AS constraint
    """
    with driver.session() as session:
        result = session.run(cypher, {"task_types": task_types})
        return [dict(record) for record in result]


def fetch_intensified_fallacies(principle_id: str, driver=None) -> list[str]:
    """
    Fetch fallacy IDs that a DigitalPrinciple intensifies risk of.
    """
    if not driver:
        return []
    cypher = """
    MATCH (dp:DigitalPrinciple {id: $principle_id})-[:INTENSIFIES_RISK_OF]->(fa:Fallacy)
    RETURN fa.id AS id
    """
    with driver.session() as session:
        result = session.run(cypher, {"principle_id": principle_id})
        return [r["id"] for r in result]
