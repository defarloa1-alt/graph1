# Node Schema Canonical Sources

`NODE_TYPE_SCHEMAS.md` is deprecated and archived.

Use the following as source of truth:

1. `Key Files/Main nodes.md`
- Current operational main-node list used as baseline labels.

2. `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
- Section 3: Entity Layer
- Section 4.1: SubjectConcept Node Schema
- Section 6.2: Claim Node Schema

3. `Neo4j/schema/01_schema_constraints.cypher`
- Enforced required properties and uniqueness constraints.

4. `Neo4j/schema/02_schema_indexes.cypher`
- Operational index model aligned to canonical property names.

Temporal modeling note:
- Use a 4-point temporal envelope for uncertain intervals:
  - `start_date_min`, `start_date_max`, `end_date_min`, `end_date_max`
- For compatibility with existing period language in consolidated architecture, emit aliases:
  - `earliest_start`, `latest_start`, `earliest_end`, `latest_end`

If examples in older docs conflict with these sources, follow these sources.

Legacy-to-canonical label mapping:
- `Person` -> `Human`
- `Subject` -> `SubjectConcept`
- `Concept` -> `SubjectConcept` (no separate `Concept` node in canonical architecture)

Migration note:
- `md/Architecture/CONCEPT_TO_SUBJECTCONCEPT_MIGRATION_2026-02-14.md`

Current operational main nodes (from `Key Files/Main nodes.md`):
- `SubjectConcept`
- `Human`
- `Gens`
- `Praenomen`
- `Cognomen`
- `Event`
- `Place`
- `Period`
- `Dynasty`
- `Institution`
- `LegalRestriction`
- `Claim`
- `Organization`
- `Year`

Main-node policy note:
- `Communication` is modeled as a facet/domain axis (e.g., propaganda, mass media), not a first-class node label.

Canonical supporting nodes (spatiotemporal and pipeline support):
- `PlaceVersion`
- `Geometry`
- `Claim`
- `Review`
- `ProposedEdge`
- `ReasoningTrace`
- `Synthesis`
- `AnalysisRun`
- `FacetAssessment`
- `FacetCategory`
- `AgentMemory`

