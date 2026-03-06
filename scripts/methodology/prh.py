"""
PRH repertoire methodology overlay — RepertoirePattern and Mechanism checks.

Agents consult these for repertoire-based event classification.
"""
from __future__ import annotations


def fetch_repertoire_patterns(driver=None) -> list[dict]:
    """
    Fetch all RepertoirePattern nodes with their mechanisms.

    Returns list of {id, label, mechanism_ids: [...]}.
    """
    if not driver:
        return []
    cypher = """
    MATCH (rp:RepertoirePattern)-[:USES_MECHANISM]->(m:Mechanism)
    WITH rp, collect(m.id) AS mechanism_ids
    RETURN rp.id AS id, rp.label AS label, mechanism_ids
    """
    with driver.session() as session:
        result = session.run(cypher)
        return [dict(record) for record in result]


def fetch_mechanisms(driver=None) -> list[dict]:
    """
    Fetch all Mechanism nodes.
    """
    if not driver:
        return []
    cypher = """
    MATCH (m:Mechanism) RETURN m.id AS id, m.label AS label
    """
    with driver.session() as session:
        result = session.run(cypher)
        return [dict(record) for record in result]
