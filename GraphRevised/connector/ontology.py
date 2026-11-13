"""Bounded read-only ontology inspection for the MCP connector."""

from dataclasses import asdict
from typing import Any

from GraphRevised.proposals.registry import load_registry

MAX_DEPTH = 2
MAX_EDGES = 200
MAX_PAGE = 50
MAX_EVIDENCE = 5
MAX_SCHEMA_ITEMS = 200

ENTITY_QUERY = """
MATCH (e:Entity {id: $id})
RETURN e.id AS id, e.label AS label, e.status AS status,
       [label IN labels(e) WHERE label <> 'Entity'] AS kinds
"""

NEIGHBOR_QUERY = """
MATCH (a:Assertion)-[:ASSERTION_SUBJECT]->(subject:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(object:Entity)
WITH a, subject, object
WHERE a.status IN ['accepted', 'proposed'] AND NOT a.id IN $seen
  AND (subject.id IN $frontier OR object.id IN $frontier)
RETURN a.id AS id, a.predicate AS predicate, a.status AS status,
       a.mode AS mode, a.category AS category,
       subject { .id, .label, .status, kinds: [l IN labels(subject) WHERE l <> 'Entity'] } AS subject,
       CASE WHEN object IS NULL THEN null ELSE
         object { .id, .label, .status, kinds: [l IN labels(object) WHERE l <> 'Entity'] } END AS object,
       head([(a)-[:ATTRIBUTED_TO]->(w:Entity:Work) | w {.id, .label, .status}]) AS attributedTo,
       head([(a)-[:ASSERTION_CONTEXT]->(c:Entity) | c {.id, .label, .status}]) AS context,
       head([(a)-[:ASSERTION_ROLE]->(r:Entity) | r {.id, .label, .status}]) AS role,
       a.timeEdtf AS timeEdtf, a.timeSourceExpression AS timeExpression,
       a.timeRelativeOffset AS relativeOffset
ORDER BY a.id
LIMIT $limit
"""

EVIDENCE_QUERY = """
UNWIND $ids AS assertionId
MATCH (a:Assertion {id: assertionId})
CALL (a) {
  CALL (a) {
    MATCH (a)-[:SUPPORTED_BY]->(o:SourceObservation)
    RETURN o, 'supported' AS state, null AS proposalId, null AS proposalStatus
    UNION ALL
    MATCH (p:Proposal)-[:PROPOSES]->(a)
    MATCH (p)-[:PROPOSES_EVIDENCE]->(o:SourceObservation)
    RETURN o, 'proposal' AS state, p.id AS proposalId, p.status AS proposalStatus
  }
  RETURN o, state, proposalId, proposalStatus
  ORDER BY state, proposalId, o.id
  LIMIT $sampleLimit
}
WITH assertionId, o, state, proposalId, proposalStatus
ORDER BY assertionId, state, proposalId, o.id
WITH assertionId, collect({observationId: o.id, label: o.label, sourceSystem: o.sourceSystem,
                           locator: o.locator, state: state, proposalId: proposalId,
                           proposalStatus: proposalStatus}) AS evidence
RETURN assertionId, evidence[..$limit] AS evidence, size(evidence) > $limit AS truncated
"""


def describe_schema(tx: Any) -> dict[str, Any]:
    registry = load_registry()
    result: dict[str, Any] = {
        "scope": "Observed database token names, not a complete schema or inferred property constraints.",
        "registryVersion": registry.version,
        "entitySubtypes": list(registry.entity_kinds),
        "predicateCount": len(registry.predicates),
        "model": "Entity subtypes use labels; claims are Assertion nodes with subject and optional object links.",
    }
    for key, procedure, field in (
        ("labels", "db.labels", "label"),
        ("relationshipTypes", "db.relationshipTypes", "relationshipType"),
        ("propertyKeys", "db.propertyKeys", "propertyKey"),
    ):
        rows = tx.run(f"CALL {procedure}() YIELD {field} RETURN {field} ORDER BY {field} LIMIT $limit",
                      limit=MAX_SCHEMA_ITEMS + 1).value(field)
        result[key] = rows[:MAX_SCHEMA_ITEMS]
        result[key + "Truncated"] = len(rows) > MAX_SCHEMA_ITEMS
    return result


def get_predicate(predicate_id: str) -> dict[str, Any]:
    registry = load_registry()
    definition = registry.get(predicate_id)
    if definition is None:
        return {"error": f"No predicate {predicate_id!r} in registry {registry.version}."}
    return {
        "registryVersion": registry.version,
        "id": definition.id, "display": definition.display, "definition": definition.definition,
        "subjectKinds": sorted(definition.subject_kinds), "objectKinds": sorted(definition.object_kinds),
        "kindPairs": sorted([list(pair) for pair in definition.kind_pairs]) if definition.kind_pairs is not None else None,
        "unary": definition.unary, "symmetric": definition.symmetric, "category": definition.category,
        "modes": sorted(definition.modes), "qualifiers": asdict(definition.qualifiers),
        "contextKinds": sorted(definition.context_kinds), "roleKinds": sorted(registry.role_kinds(definition)),
        "once": definition.once, "wikidata": [asdict(mapping) for mapping in definition.wikidata],
    }


def get_subgraph(tx: Any, entity_id: str, depth: int, offset: int, limit: int) -> dict[str, Any]:
    if not entity_id.strip():
        raise ValueError("A non-empty entity_id is required.")
    if not 1 <= depth <= MAX_DEPTH:
        raise ValueError(f"depth must be between 1 and {MAX_DEPTH}.")
    if offset < 0 or offset >= MAX_EDGES:
        raise ValueError(f"offset must be between 0 and {MAX_EDGES - 1}.")
    if not 1 <= limit <= MAX_PAGE:
        raise ValueError(f"limit must be between 1 and {MAX_PAGE}.")
    root = tx.run(ENTITY_QUERY, id=entity_id).single()
    if root is None:
        return {"error": f"No Entity {entity_id}."}
    root = dict(root)
    frontier, visited = {entity_id}, {entity_id}
    edges: list[dict[str, Any]] = []
    seen: set[str] = set()
    truncated = False
    for level in range(1, depth + 1):
        if not frontier:
            break
        rows = tx.run(NEIGHBOR_QUERY, frontier=sorted(frontier), seen=sorted(seen),
                      limit=MAX_EDGES - len(edges) + 1).data()
        if len(rows) > MAX_EDGES - len(edges):
            truncated = True
            rows = rows[:MAX_EDGES - len(edges)]
        next_frontier = set()
        for row in rows:
            row["distance"] = level
            seen.add(row["id"])
            for endpoint in (row["subject"], row["object"]):
                if endpoint and endpoint["id"] not in visited:
                    next_frontier.add(endpoint["id"])
            edges.append(row)
        visited.update(next_frontier)
        frontier = next_frontier
        if truncated:
            break
    page = edges[offset:offset + limit]
    evidence_rows = tx.run(EVIDENCE_QUERY, ids=[edge["id"] for edge in page], limit=MAX_EVIDENCE,
                           sampleLimit=MAX_EVIDENCE + 1).data()
    evidence = {row["assertionId"]: row for row in evidence_rows}
    nodes = {root["id"]: root}
    for edge in page:
        for endpoint in (edge["subject"], edge["object"]):
            if endpoint:
                nodes[endpoint["id"]] = endpoint
        support = evidence.get(edge["id"], {})
        edge["evidence"] = support.get("evidence", [])
        edge["evidenceTruncated"] = support.get("truncated", False)
    next_offset = offset + len(page)
    return {
        "root": root, "depth": depth, "nodes": list(nodes.values()), "assertions": page,
        "offset": offset, "limit": limit,
        "nextOffset": next_offset if next_offset < len(edges) else None,
        "traversalTruncated": truncated, "traversalLimit": MAX_EDGES,
        "scope": "Accepted and proposed assertions only; subject-to-object direction is explicit. "
                 "Evidence lists identifiers and proposal statuses, not quotations. Pages may change with graph updates.",
    }
