# Cypher scripts

Active Neo4j scripts for Chrystallum. One-off imports, period-view experiments, and superseded DDL live under `Archive/cypher-2026-07/`.

## Layout

| Folder | Purpose |
|--------|---------|
| [`schema/`](schema/) | Constraints, indexes, multi-agent claim schema, SubjectConcept schema, geographic registration |
| [`bootstrap/`](bootstrap/) | Kernel seed and SubjectConcept agent bootstrap |
| [`operations/`](operations/) | SubjectConcept ops, PID relationship listing, Wikidata hierarchy helpers |
| [`queries/`](queries/) | Diagnostic / explore queries (safe to run read-only) |

## Start here

1. Schema constraints: `schema/constraints_chrystallum_generated.cypher`
2. Multi-agent claims (ADR-022): `schema/phase1_multi_agent_schema.cypher`
3. Bootstrap agents: `bootstrap/bootstrap_subject_concept_agents.cypher`  
   (also invoked by `scripts/neo4j/bootstrap_system_subgraph.py`)
4. Ops cookbook: `operations/subject_concept_operations.cypher`

## Do not re-run from Archive without review

- `Archive/cypher-2026-07/imports/` — large Jan 2026 period imports  
- `Archive/cypher-2026-07/explore/` — early period view drafts  
- `Archive/cypher-2026-07/one-offs/` — old DDL, cleanup, property-mapping tests  
- `Archive/scripts-2026-07/node-cleanup/` — July 16 node consolidation batch  

Prefer live Aura schema + `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md` over archived scripts.
