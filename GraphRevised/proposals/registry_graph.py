"""The predicate registry in the graph: the type-level model as nodes (D-159).

    python -m GraphRevised.proposals.registry_graph            # what would change
    python -m GraphRevised.proposals.registry_graph --apply    # write it

The registry file (`predicates.v19.json`) stays the source: proposals, the
guarded operations, and the validators read it. This module draws the current
version into Neo4j so that the relationships between entity types can be
queried where the entities are ("what can relate a Person to an Event?",
"which predicates may take a Work as object?"):

    (:PredicateRegistry {version})-[:DEFINES_PREDICATE]->(:Predicate {name})
    (:PredicateRegistry)-[:DEFINES_KIND]->(:EntityKind {name})
    (:Predicate)-[:SUBJECT_KIND | OBJECT_KIND | CONTEXT_KIND | ROLE_KIND]->(:EntityKind)

An `EntityKind`'s `name` is the Neo4j subtype label (`Person`), so
`MATCH (:EntityKind {name: "Person"})<-[:SUBJECT_KIND]-(p:Predicate)` lists
what a Person may claim. A `Predicate`'s `name` is `Assertion.predicate`, and
its `factLayerType` the fact layer's edge type (D-144).

One PredicateRegistry node per version loaded; the newest has
`current: true`. A Predicate or EntityKind carries the definition of the
newest version that defines it; one the current version no longer defines is
marked `status: "retired"` with `retiredIn`, never deleted. Earlier versions'
text stays in git. Re-run after every registry bump; retry-safe.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import relationship_type
from GraphRevised.proposals.registry import REGISTRY_PATH, PredicateRegistry, load_registry

REPOSITORY = Path(__file__).resolve().parents[2]


def predicate_id(name: str) -> str:
    return f"chr:predicate:{name}"


def kind_id(name: str) -> str:
    return f"chr:kind:{name.lower()}"


def registry_id(version: str) -> str:
    return f"chr:registry:{version}"


def plan(registry: PredicateRegistry, path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """The nodes and links one registry version draws, as plain data."""
    version = registry.version
    content = path.read_bytes()
    registry_node = {
        "id": registry_id(version), "version": version,
        "label": f"Predicate registry {version}", "shortLabel": version,
        "sourcePath": path.relative_to(REPOSITORY).as_posix(),
        "contentHash": "sha256:" + hashlib.sha256(content).hexdigest(),
        "roleKind": registry.role_kind,
        "predicateCount": len(registry.predicates), "kindCount": len(registry.entity_kinds),
    }
    kinds = [{"id": kind_id(name), "name": name, "label": name} for name in registry.entity_kinds]
    predicates = []
    for definition in registry.predicates.values():
        q = definition.qualifiers
        links = [("SUBJECT_KIND", k) for k in sorted(definition.subject_kinds)]
        links += [("OBJECT_KIND", k) for k in sorted(definition.object_kinds)]
        if q.context != "none":
            links += [("CONTEXT_KIND", k) for k in sorted(definition.context_kinds)]
        if q.role != "none":
            links += [("ROLE_KIND", k) for k in sorted(registry.role_kinds(definition))]
        predicates.append({
            "properties": {
                "id": predicate_id(definition.id), "name": definition.id,
                "label": definition.display, "shortLabel": definition.id,
                "definition": definition.definition, "category": definition.category,
                "modes": sorted(definition.modes), "symmetric": definition.symmetric,
                "once": definition.once, "unary": definition.unary,
                "context": q.context, "role": q.role, "time": q.time, "quantity": q.quantity,
                "stance": q.stance, "reception": q.reception,
                "kindPairs": (sorted(f"{s} -> {o}" for s, o in definition.kind_pairs)
                              if definition.kind_pairs is not None else None),
                "wikidata": [f"{m.pid} {m.direction}" + (f" {m.bound}" if m.bound else "")
                             for m in definition.wikidata],
                "factLayerType": relationship_type(definition.id),
                "registryVersion": version, "status": "current",
            },
            "links": [{"type": t, "kind": kind_id(k)} for t, k in links],
        })
    return {"registry": registry_node, "kinds": kinds, "predicates": predicates}


UPSERT_REGISTRY = """
MERGE (r:PredicateRegistry {id: $registry.id})
SET r += $registry, r.loadedAt = coalesce(r.loadedAt, $now)
WITH r
OPTIONAL MATCH (other:PredicateRegistry) WHERE other <> r
SET other.current = false
WITH DISTINCT r
SET r.current = true
"""

UPSERT_KINDS = """
MATCH (r:PredicateRegistry {id: $registryId})
UNWIND $kinds AS kind
MERGE (k:EntityKind {id: kind.id})
SET k += kind, k.status = "current", k.registryVersion = r.version
REMOVE k.retiredIn
MERGE (r)-[:DEFINES_KIND]->(k)
"""

UPSERT_PREDICATES = """
MATCH (r:PredicateRegistry {id: $registryId})
UNWIND $predicates AS item
MERGE (p:Predicate {id: item.properties.id})
SET p += item.properties
REMOVE p.retiredIn
MERGE (r)-[:DEFINES_PREDICATE]->(p)
WITH p
OPTIONAL MATCH (p)-[old:SUBJECT_KIND|OBJECT_KIND|CONTEXT_KIND|ROLE_KIND]->()
DELETE old
"""

LINK_TYPES = ("SUBJECT_KIND", "OBJECT_KIND", "CONTEXT_KIND", "ROLE_KIND")

LINK = """
UNWIND $links AS link
MATCH (p:Predicate {id: link.predicate}), (k:EntityKind {id: link.kind})
MERGE (p)-[:%s]->(k)
"""

RETIRE = """
MATCH (n) WHERE (n:Predicate AND NOT n.id IN $predicateIds) OR (n:EntityKind AND NOT n.id IN $kindIds)
SET n.status = "retired", n.retiredIn = coalesce(n.retiredIn, $version)
RETURN count(n) AS retired
"""

DIFF = """
OPTIONAL MATCH (r:PredicateRegistry {current: true})
CALL () { MATCH (p:Predicate) RETURN collect(p.id) AS predicates }
CALL () { MATCH (k:EntityKind) RETURN collect(k.id) AS kinds }
RETURN r.version AS currentVersion, r.contentHash AS currentHash, predicates, kinds
"""


def sync(tx: Any, data: dict[str, Any], now: str) -> int:
    registry = data["registry"]
    tx.run(UPSERT_REGISTRY, registry=registry, now=now).consume()
    tx.run(UPSERT_KINDS, registryId=registry["id"], kinds=data["kinds"]).consume()
    tx.run(UPSERT_PREDICATES, registryId=registry["id"], predicates=data["predicates"]).consume()
    for link_type in LINK_TYPES:
        links = [{"predicate": p["properties"]["id"], "kind": link["kind"]}
                 for p in data["predicates"] for link in p["links"] if link["type"] == link_type]
        tx.run(LINK % link_type, links=links).consume()
    return tx.run(RETIRE, version=registry["version"],
                  predicateIds=[p["properties"]["id"] for p in data["predicates"]],
                  kindIds=[k["id"] for k in data["kinds"]]).single()["retired"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="write the registry into the graph")
    args = parser.parse_args(argv)
    registry = load_registry()
    data = plan(registry)
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]))
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            before = session.run(DIFF).single().data()
            wanted = {p["properties"]["id"] for p in data["predicates"]}
            held = set(before["predicates"])
            links = sum(len(p["links"]) for p in data["predicates"])
            print(f"registry {registry.version} ({data['registry']['contentHash'][:19]}); "
                  f"graph holds {before['currentVersion'] or 'none'}")
            print(f"{len(data['kinds'])} kinds, {len(wanted)} predicates, {links} kind links; "
                  f"new {len(wanted - held)}, to retire {len(held - wanted)}")
            if not args.apply:
                print("dry run: nothing written (use --apply)")
                return 0
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            retired = session.execute_write(sync, data, now)
            print(f"written; {retired} retired")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
