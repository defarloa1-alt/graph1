# Chrystallum Graph Revised

## Purpose

This folder is the clean-start design space for Chrystallum.

The previous model accumulated too many node types, relationship types, agents,
authority mappings, and workflow states before the smallest useful graph had
been proven. This revision starts with a smaller contract:

1. represent durable things;
2. represent subjects about those things;
3. represent evidence-bearing assertions;
4. connect dates to the existing temporal backbone;
5. add external authorities only when they help resolve or explain a node;
6. expand the model only when a real use case requires it.

The design in this folder is intentionally more conservative than the legacy
architecture. It is a starting point, not a claim that every future historical
concept has already been modeled.

## Read in this order

0. [00-NEO4J-SCHEMA-SNAPSHOT.md](00-NEO4J-SCHEMA-SNAPSHOT.md) — read-only baseline of the active local database
1. [01-ARCHITECTURE.md](01-ARCHITECTURE.md) — the small conceptual model
2. [02-GRAPH-MODEL.md](02-GRAPH-MODEL.md) — the initial node and relationship contract
3. [03-TEMPORAL-YEAR-BACKBONE.md](03-TEMPORAL-YEAR-BACKBONE.md) — the temporal structure already present in Neo4j
4. [04-IMPLEMENTATION-PLAN.md](04-IMPLEMENTATION-PLAN.md) — the order in which to build and validate
5. [05-AGENT-BOUNDARIES.md](05-AGENT-BOUNDARIES.md) — the front door, agent roles, and governed write path
6. [06-GRAPH-NAVIGATION.md](06-GRAPH-NAVIGATION.md) — the visual graph navigation and read projection
7. [07-DOMAIN-ADAPTATION.md](07-DOMAIN-ADAPTATION.md) — broad historical inquiries and domain-specific federation
8. [08-SCOPE-AND-INTENT.md](08-SCOPE-AND-INTENT.md) — product boundary and front-door scope classification
9. [09-INDEX-HARVESTING.md](09-INDEX-HARVESTING.md) — machine-readable scholarly indexes and source-led harvesting
10. [10-PHASE-1-SCHEMA.cypher](10-PHASE-1-SCHEMA.cypher) — minimum uniqueness constraints
11. [11-PHASE-1-RESULTS.md](11-PHASE-1-RESULTS.md) — applied schema and validation result
12. [12-PHASE-2-ACTIUM.md](12-PHASE-2-ACTIUM.md) — first direct, evidence-bearing graph slice
13. [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher) — reusable direct reads and idempotent writes
14. [14-PHASE-3-RESULTS.md](14-PHASE-3-RESULTS.md) — Phase 3 implementation and validation status
15. [15-PHASE-4-WIKIDATA-IDENTITY.md](15-PHASE-4-WIKIDATA-IDENTITY.md) — candidate-only Wikidata identity adapter
16. [16-LEGACY-TRIAGE.md](16-LEGACY-TRIAGE.md) — legacy adoption boundary and first-pass register
17. [17-PHASE-5-HANDOFF.md](17-PHASE-5-HANDOFF.md) — verified project state and Phase 5 starting point
18. [Review of the Chrystallum Subject Backbone Architecture.md](Review%20of%20the%20Chrystallum%20Subject%20Backbone%20Architecture.md) — architectural review and recommendations

## Clean-start rules

- The documents in this folder are the active design for the revised graph.
- Legacy documentation is reference material only until explicitly adopted.
- The new graph should begin with the temporal year backbone and a small number
  of general-purpose node and relationship patterns.
- A proposed feature does not become part of the core model merely because an
  external authority supports it.
- A new node type or relationship requires a concrete query or workflow that
  cannot be expressed clearly with the existing model.
- The graph must remain useful when external services are unavailable.
- The Neo4j database is the durable graph; agent workflow state and raw source
  payloads are separate concerns.
- Agent orchestration is not part of the graph's semantic core.
- No conversational agent writes directly to accepted Neo4j knowledge.
- A domain package may extend vocabulary and routing, but may not silently
  redefine the core claim and provenance model.
- The CCA classifies the user's primary intent before entity resolution.

## Current database context

The local Neo4j `neo4j` database currently contains only the temporal year
backbone. That is a useful and intentionally limited starting point. The
separate local `historical` database is empty and is not part of the
clean-start plan.

Nothing in this documentation requires changing the database immediately.

The first implementation goal is to validate the model against that temporal
backbone, then add one small historical example end to end.
