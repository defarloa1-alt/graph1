"""Migration 018 (2026-11-18): the logical model (30) as a Neo4j graph type.

    python -m GraphRevised.migrations.018_graph_type            # preflight only
    python -m GraphRevised.migrations.018_graph_type --show     # print the graph type
    python -m GraphRevised.migrations.018_graph_type --apply    # preflight, then set it

Until now the database enforced only the eleven unique ids (02 §5); every
other rule in 30 was held by the guarded operations and the validator. Neo4j
2026.09 Enterprise has Cypher 25 graph types, which can hold more of the
model in the database itself:

1. Each Entity subtype label implies `Entity`, so a Person is never stored
   without it.
2. Each core label has its required properties (`[1]` in 30 §2), with their
   types; optional properties are typed where present.
3. Infrastructure relationship types are pinned to their source and target
   labels (30 §4), with their required properties: a claim's subject and
   object are Entities (02 §2, narrowed 2026-11-18); ATTRIBUTED_TO and IN_WORK
   reach a Work; AT_LOCATION starts at a Place. So are the registry nodes'
   links and the single-pair fact-layer types (D-159).

What it leaves to the guarded operations, because a graph type cannot say it
(30 §7): exactly one subtype label per Entity; the predicate registry's kinds
at each end of a claim; multiplicities; status transitions; immutability; no
image as evidence. Relationships with more than one source or target label in
02 §2 (CONCERNS, HAS_AUTHORITY_RECORD, IN_YEAR, RESTS_ON) are not pinned, nor
are the fact-layer types whose predicate allows several kinds at an end.

Left optional although 30 §2 calls them required, because live data lacks them
by design or from legacy writes (30 §8):
- AuthorityRecord.retrievedAt, contentHash, rawPayloadUri: the LC neighbour
  headings (D-155) are stored before their record is fetched; 02 makes them
  optional (2026-11-18).
- ANNOTATES.quotation: an image note has no words to quote.
- IN_YEAR.as: the Phase 2 Battle of Actium link.

`ALTER CURRENT GRAPH TYPE SET` replaces the whole graph type, so the eleven
existing unique constraints are restated here under their own names (kept,
not rebuilt). From now on this file is the database schema: a new constraint
is added to it and the migration re-run, never created by hand. Indexes (the
`location_point` index) are not part of a graph type and are untouched.

Without --apply it checks the live data against every rule and asks the
server to plan the statement; nothing is written. With --apply it refuses
to run while any rule has a violation. Retry-safe: setting the same graph
type again changes nothing.
"""

from __future__ import annotations

import argparse
import os
import sys

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import relationship_type
from GraphRevised.proposals.registry import load_registry

SUBTYPES = ["Person", "Place", "Event", "Group", "Work", "Object", "Period", "Office",
            "Concept", "Polity", "Type", "Question", "Position", "Other"]

S, I, F, B, P = "STRING", "INTEGER", "FLOAT", "BOOLEAN", "POINT"
LS = "LIST<STRING NOT NULL>"
NUM = "INTEGER | FLOAT"
REQ = True  # required: NOT NULL

# Entity is implied by its subtypes, so it cannot also be an element type with
# properties of its own; its rules are stated as constraints (ENTITY below).
ENTITY: dict[str, tuple[str, bool]] = {
    "id": (S, REQ), "label": (S, REQ), "status": (S, REQ),
    "shortLabel": (S, False), "description": (S, False), "form": (S, False),
    "standing": (S, False), "typeCategory": (S, False), "sourceNote": (S, False),
    "when": (S, False), "where": (S, False), "partOf": (S, False), "history": (S, False),
    "eventType": (S, False),
    "alternativeNames": (LS, False), "mergedIds": (LS, False), "mergeLog": (LS, False),
}

NODES: dict[str, dict[str, tuple[str, bool]]] = {
    "Subject": {"id": (S, REQ), "label": (S, REQ), "status": (S, REQ), "shortLabel": (S, False)},
    "Assertion": {
        "id": (S, REQ), "predicate": (S, REQ), "label": (S, REQ), "status": (S, REQ),
        "category": (S, REQ), "assertedBy": (S, REQ),
        "shortLabel": (S, False), "mode": (S, False), "basis": (S, False), "reception": (S, False),
        "acceptedAt": (S, False), "contextBasis": (S, False),
        "timeSourceExpression": (S, False), "timeEdtf": (S, False), "timePrecision": (S, False),
        "timeCalendar": (S, False), "timeMode": (S, False), "timeNormalizationBasis": (S, False),
        "timeApproximate": (B, False), "timeUncertain": (B, False),
        "startEarliestJdn": (I, False), "startLatestJdn": (I, False),
        "endEarliestJdn": (I, False), "endLatestJdn": (I, False),
        "quantityMinimum": (NUM, False), "quantityMaximum": (NUM, False), "quantityTypical": (NUM, False),
    },
    "Proposal": {
        "id": (S, REQ), "operation": (S, REQ), "label": (S, REQ), "status": (S, REQ),
        "createdBy": (S, REQ), "rationale": (S, REQ),
        "draftSchemaVersion": (S, REQ), "predicateRegistryVersion": (S, REQ),
        "shortLabel": (S, False), "provenanceBackfilledAt": (S, False),
        "provenanceBackfilledBy": (S, False), "provenanceBackfillBasis": (S, False),
        "promptVersion": (S, False), "modelId": (S, False), "inquiryId": (S, False),
        "relevance": (S, False), "ambiguities": (LS, False), "decisionReason": (S, False),
        "rejectedClaim": (B, False),
    },
    "SourceObservation": {
        "id": (S, REQ), "label": (S, REQ), "status": (S, REQ), "sourceSystem": (S, REQ),
        "retrievedAt": (S, REQ), "contentHash": (S, REQ),
        "shortLabel": (S, False), "observationKind": (S, False), "sourceRevision": (f"{I} | {S}", False),
        "rawPayloadUri": (S, False), "sourceUri": (S, False), "visibility": (S, False),
        "passageText": (S, False), "passageHash": (S, False), "locator": (S, False),
        "editorialNotes": (LS, False), "qualifierPropertyIds": (LS, False),
        "statementStatedIn": (LS, False), "footnotes": (LS, False),
    },
    "AuthorityRecord": {
        "id": (S, REQ), "system": (S, REQ), "identifier": (S, REQ), "label": (S, REQ),
        "shortLabel": (S, False), "description": (S, False), "retrievedAt": (S, False),
        "contentHash": (S, False), "rawPayloadUri": (S, False), "sourceUri": (S, False),
        "sourceRevision": (I, False), "mergedIds": (LS, False),
    },
    "Annotation": {
        "id": (S, REQ), "kind": (S, REQ), "label": (S, REQ), "author": (S, REQ),
        "visibility": (S, REQ), "status": (S, REQ), "createdAt": (S, REQ),
        "note": (S, False), "noteType": (S, False),
    },
    "Year": {
        "year": (I, REQ), "label": (S, REQ), "iso8601_start": (S, REQ), "iso8601_end": (S, REQ),
        "temporal_backbone": (B, REQ),
    },
    "Location": {
        "id": (S, REQ), "system": (S, REQ), "identifier": (S, REQ), "dataset": (S, REQ),
        "kind": (S, REQ), "label": (S, REQ), "location": (P, False), "population": (I, False),
        "names": (LS, False), "nameAttestations": (LS, False), "placeTypes": (LS, False),
    },
    # The registry in the graph (D-159, proposals/registry_graph.py).
    "PredicateRegistry": {
        "id": (S, REQ), "version": (S, REQ), "label": (S, REQ), "current": (B, REQ),
        "contentHash": (S, REQ), "sourcePath": (S, REQ), "loadedAt": (S, REQ),
        "shortLabel": (S, False), "roleKind": (S, False),
        "predicateCount": (I, False), "kindCount": (I, False),
    },
    "Predicate": {
        "id": (S, REQ), "name": (S, REQ), "label": (S, REQ), "category": (S, REQ),
        "modes": (LS, REQ), "symmetric": (B, REQ), "once": (B, REQ), "unary": (B, REQ),
        "factLayerType": (S, REQ), "registryVersion": (S, REQ), "status": (S, REQ),
        "context": (S, REQ), "role": (S, REQ), "time": (S, REQ), "quantity": (S, REQ),
        "stance": (S, REQ), "reception": (S, REQ),
        "shortLabel": (S, False), "definition": (S, False), "kindPairs": (LS, False),
        "wikidata": (LS, False), "retiredIn": (S, False),
    },
    "EntityKind": {
        "id": (S, REQ), "name": (S, REQ), "label": (S, REQ), "status": (S, REQ),
        "registryVersion": (S, REQ), "retiredIn": (S, False),
    },
}

# (type, source label, target label, properties): one source and one target label each.
RELATIONSHIPS: list[tuple[str, str, str, dict[str, tuple[str, bool]]]] = [
    ("ASSERTION_SUBJECT", "Assertion", "Entity", {}),
    ("ASSERTION_OBJECT", "Assertion", "Entity", {}),
    ("ASSERTION_CONTEXT", "Assertion", "Entity", {}),
    ("ASSERTION_ROLE", "Assertion", "Entity", {}),
    ("ATTRIBUTED_TO", "Assertion", "Work", {}),
    ("SUPERSEDED_BY", "Assertion", "Assertion", {}),
    ("PROMOTED_FROM", "Assertion", "Assertion", {}),
    ("SUPPORTED_BY", "Assertion", "SourceObservation",
     {"quotation": (S, False), "qualifierQuotations": (LS, False), "addedByProposal": (S, False)}),
    ("PROPOSES", "Proposal", "Assertion", {}),
    ("PROPOSES_EVIDENCE", "Proposal", "SourceObservation",
     {"quotation": (S, False), "qualifierQuotations": (LS, False), "migratedBy": (S, False)}),
    ("IN_WORK", "SourceObservation", "Work", {}),
    ("HAS_SUBJECT_FOCUS", "Subject", "Entity", {}),
    ("NARROWER_THAN", "Subject", "Subject", {}),
    ("IN_SUBJECT", "Entity", "Subject", {"status": (S, REQ)}),
    ("HAS_SUBJECT_HEADING", "Work", "AuthorityRecord", {"status": (S, REQ)}),
    ("BROADER_HEADING", "AuthorityRecord", "AuthorityRecord", {"status": (S, REQ)}),
    ("ANNOTATES", "Annotation", "SourceObservation", {"quotation": (S, False)}),
    ("AT_LOCATION", "Place", "Location", {"status": (S, REQ), "basis": (S, REQ)}),
    ("WITHIN", "Location", "Location", {"tree": (S, REQ), "relation": (S, REQ), "periods": (LS, False)}),
    ("MODERN_LOCATION", "Location", "Location",
     {"how": (S, REQ), "viaId": (S, False), "viaLabel": (S, False), "distanceKm": (F, False)}),
    ("FOLLOWED_BY", "Year", "Year", {}),
    ("DEFINES_PREDICATE", "PredicateRegistry", "Predicate", {}),
    ("DEFINES_KIND", "PredicateRegistry", "EntityKind", {}),
    ("SUBJECT_KIND", "Predicate", "EntityKind", {}),
    ("OBJECT_KIND", "Predicate", "EntityKind", {}),
    ("CONTEXT_KIND", "Predicate", "EntityKind", {}),
    ("ROLE_KIND", "Predicate", "EntityKind", {}),
]

# Every fact-layer edge (D-144) says what drew it.
FACT_PROPERTIES = {"derived": (S, REQ), "predicate": (S, REQ), "status": (S, REQ)}


def fact_layer(registry) -> tuple[list[tuple[str, str, str, dict]], dict[str, dict]]:
    """The fact layer's edge types, from the predicate registry.

    A predicate with one subject kind and one object kind is pinned to them
    (BORN_AT from a Person to a Place); a dated unary fact of one subject kind
    to its Years (BORN, DIED). Every other fact type is left unpinned, its
    properties still required. Re-run this migration after a registry bump.
    """
    pinned, unpinned = [], {}
    for definition in registry.predicates.values():
        rel = relationship_type(definition.id)
        subjects, objects = sorted(definition.subject_kinds), sorted(definition.object_kinds)
        target = objects[0] if len(objects) == 1 else ("Year" if not objects else None)
        if len(subjects) == 1 and target and (definition.kind_pairs is None or len(definition.kind_pairs) == 1):
            pinned.append((rel, subjects[0], target, FACT_PROPERTIES))
        else:
            unpinned[rel] = FACT_PROPERTIES
    return pinned, unpinned


_FACT_PINNED, _FACT_UNPINNED = fact_layer(load_registry())
RELATIONSHIPS += _FACT_PINNED

# Relationship properties on types that are not pinned to endpoints.
REL_PROPERTIES: dict[str, dict[str, tuple[str, bool]]] = {
    "HAS_AUTHORITY_RECORD": {"role": (S, REQ), "relation": (S, REQ), "status": (S, REQ),
                             "statementRank": (S, False), "statementReferences": (I, False)},
    "RESTS_ON": {"status": (S, REQ), "createdBy": (S, REQ), "createdAt": (S, REQ),
                 "quotation": (S, False), "citation": (S, False)},
    "IN_YEAR": {"as": (S, False)},
    **_FACT_UNPINNED,
}

# The eleven live unique constraints (02 §5), restated under their own names.
UNIQUE = [
    ("entity_id_unique", "Entity", ["id"]),
    ("subject_id_unique", "Subject", ["id"]),
    ("assertion_id_unique", "Assertion", ["id"]),
    ("proposal_id_unique", "Proposal", ["id"]),
    ("source_observation_id_unique", "SourceObservation", ["id"]),
    ("authority_record_id_unique", "AuthorityRecord", ["id"]),
    ("authority_record_system_identifier_unique", "AuthorityRecord", ["system", "identifier"]),
    ("annotation_id_unique", "Annotation", ["id"]),
    ("year_year_unique", "Year", ["year"]),
    ("location_id_unique", "Location", ["id"]),
    ("location_system_identifier_unique", "Location", ["system", "identifier"]),
    ("predicate_registry_id_unique", "PredicateRegistry", ["id"]),
    ("predicate_registry_version_unique", "PredicateRegistry", ["version"]),
    ("predicate_id_unique", "Predicate", ["id"]),
    ("predicate_name_unique", "Predicate", ["name"]),
    ("entity_kind_id_unique", "EntityKind", ["id"]),
    ("entity_kind_name_unique", "EntityKind", ["name"]),
]


def _props(props: dict[str, tuple[str, bool]]) -> str:
    return ", ".join(f"{name} :: {kind}{' NOT NULL' if required else ''}"
                     for name, (kind, required) in props.items())


def _slug(*parts: str) -> str:
    return "_".join(p.lower() for p in parts)


def graph_type() -> str:
    """The graph type, as one ALTER CURRENT GRAPH TYPE SET statement."""
    items = [f"(:{label} => :Entity)" for label in SUBTYPES]
    items += [f"(:{label} => {{{_props(props)}}})" for label, props in NODES.items()]
    for rel, source, target, props in RELATIONSHIPS:
        body = f" {{{_props(props)}}}" if props else ""
        items.append(f"(:{source})-[:{rel} =>{body}]->(:{target})")
    for name, label, keys in UNIQUE:
        target = ", ".join(f"n.{k}" for k in keys)
        items.append(f"CONSTRAINT {name} FOR (n:{label}) REQUIRE ({target}) IS UNIQUE")
    for prop, (kind, required) in ENTITY.items():
        if required:
            items.append(f"CONSTRAINT {_slug('entity', prop, 'exists')} FOR (n:Entity) REQUIRE n.{prop} IS NOT NULL")
        items.append(f"CONSTRAINT {_slug('entity', prop, 'type')} FOR (n:Entity) REQUIRE n.{prop} IS :: {kind}")
    for rel, props in REL_PROPERTIES.items():
        for prop, (kind, required) in props.items():
            if required:
                items.append(f"CONSTRAINT {_slug(rel, prop, 'exists')} FOR ()-[r:{rel}]->() "
                             f"REQUIRE r.{prop} IS NOT NULL")
            items.append(f"CONSTRAINT {_slug(rel, prop, 'type')} FOR ()-[r:{rel}]->() REQUIRE r.{prop} IS :: {kind}")
    return "CYPHER 25 ALTER CURRENT GRAPH TYPE SET {\n  " + ",\n  ".join(items) + "\n}"


def checks() -> list[tuple[str, str]]:
    """(rule, Cypher counting the live items that break it), one per rule."""
    out = [(f"{label} implies Entity", f"MATCH (n:{label}) WHERE NOT n:Entity RETURN count(n) AS c")
           for label in SUBTYPES]

    def node_rules(label: str, props: dict[str, tuple[str, bool]]):
        for prop, (kind, required) in props.items():
            if required:
                out.append((f"{label}.{prop} present", f"MATCH (n:{label}) WHERE n.{prop} IS NULL RETURN count(n) AS c"))
            out.append((f"{label}.{prop} :: {kind}",
                        f"MATCH (n:{label}) WHERE n.{prop} IS NOT NULL AND NOT n.{prop} IS :: {kind} RETURN count(n) AS c"))

    def rel_rules(rel: str, props: dict[str, tuple[str, bool]]):
        for prop, (kind, required) in props.items():
            if required:
                out.append((f"{rel}.{prop} present", f"MATCH ()-[r:{rel}]->() WHERE r.{prop} IS NULL RETURN count(r) AS c"))
            out.append((f"{rel}.{prop} :: {kind}",
                        f"MATCH ()-[r:{rel}]->() WHERE r.{prop} IS NOT NULL AND NOT r.{prop} IS :: {kind} "
                        "RETURN count(r) AS c"))

    node_rules("Entity", ENTITY)
    for label, props in NODES.items():
        node_rules(label, props)
    for rel, source, target, props in RELATIONSHIPS:
        out.append((f"{rel} from {source} to {target}",
                    f"MATCH (a)-[r:{rel}]->(b) WHERE NOT a:{source} OR NOT b:{target} RETURN count(r) AS c"))
        rel_rules(rel, props)
    for rel, props in REL_PROPERTIES.items():
        rel_rules(rel, props)
    return out


def preflight(session) -> list[tuple[str, int]]:
    """The rules the live data breaks, with how many items break each."""
    broken = []
    for rule, query in checks():
        count = session.run(query).single()["c"]
        if count:
            broken.append((rule, count))
    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="set the graph type (after a clean preflight)")
    parser.add_argument("--show", action="store_true", help="print the graph type statement and stop")
    args = parser.parse_args(argv)
    statement = graph_type()
    if args.show:
        print(statement)
        return 0
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]))
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            rules = checks()
            broken = preflight(session)
            print(f"{len(rules)} rules checked; {len(broken)} broken")
            for rule, count in broken:
                print(f"  {rule}: {count}")
            session.run("CYPHER 25 EXPLAIN " + statement.removeprefix("CYPHER 25 ")).consume()
            print("the server accepts the graph type statement")
            if broken:
                return 1
            if not args.apply:
                print("dry run: nothing written (use --apply)")
                return 0
            session.run(statement).consume()
            print("graph type set")
            print(session.run("CYPHER 25 SHOW CURRENT GRAPH TYPE").single()["specification"])
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
