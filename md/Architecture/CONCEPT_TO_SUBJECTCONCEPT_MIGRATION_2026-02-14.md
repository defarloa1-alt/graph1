# Concept To SubjectConcept Migration (2026-02-14)

## Decision
- `Concept` is deprecated as a canonical node label.
- `SubjectConcept` is the canonical conceptual/taxonomic node type.

## Canonical Mapping
- `Concept` -> `SubjectConcept`
- `Subject` -> `SubjectConcept`
- `Person:Concept` -> `Person`
- `Place:Concept` -> `Place`
- `Event:Concept` -> `Event`

## Scope
- Applies to active architecture docs, agent prompts, import guides, and roadmap examples.
- Does not alter source vocab terms like `skos:Concept` in FAST/LCSH JSON-LD ingestion.

## Write-Time Guardrails
- Reject graph writes that create `:Concept` nodes.
- Normalize incoming proposed labels:
  - If label list contains `Concept` and a concrete entity label (`Person`, `Place`, `Event`, `Year`, `Period`), drop `Concept`.
  - If conceptual node is intended, write `:SubjectConcept`.

## Backlink/Federation Guidance
- Wikidata `P31` values like concept/ideology should map to `SubjectConcept` in Chrystallum.
- Role and relationship mapping remains in `Relationships/relationship_types_registry_master.csv`.

## Verification Query (Neo4j)
```cypher
MATCH (n:Concept)
RETURN count(n) AS legacy_concept_nodes;
```
Expected result: `0`.
