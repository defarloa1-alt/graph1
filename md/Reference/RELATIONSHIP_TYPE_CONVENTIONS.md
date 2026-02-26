# Relationship Type Conventions

**Created:** 2026-02-21  
**Purpose:** Document directionality and semantics for key Chrystallum relationship types.

---

## FOLLOWED_BY

**Directionality:** `(A)-[:FOLLOWED_BY]->(B)` means **B comes after A** in sequence.

- **Year chain:** `(:Year {year: -49})-[:FOLLOWED_BY]->(:Year {year: -48})` — -48 follows -49 chronologically.
- **Period succession:** `(Roman Republic)-[:FOLLOWED_BY]->(Roman Empire)` — Roman Empire succeeded Roman Republic.
- **Event sequence:** `(Event A)-[:FOLLOWED_BY]->(Event B)` — B occurred after A.

**Reverse chronology:** Query via incoming `FOLLOWED_BY` edges, or use `PRECEDED_BY` where available.

**Source:** `scripts/backbone/temporal/genYearsToNeo.py`, `Neo4j/schema/05_temporal_hierarchy_levels.cypher`, `output/neo4j/relationships_*.cypher`.

---

## HAS_GEO_COVERAGE / HAS_GEO_COVERAGE_CANDIDATE

**Purpose:** Period–place coverage links. A period (e.g. Roman Republic) has geographic coverage over specific places during its temporal span.

- **HAS_GEO_COVERAGE_CANDIDATE:** `(:PeriodCandidate)-[:HAS_GEO_COVERAGE_CANDIDATE]->(:GeoCoverageCandidate)` — triage stage.
- **HAS_GEO_COVERAGE:** `(:Period)-[:HAS_GEO_COVERAGE]->(:GeoCoverageCandidate)` — canonical period–place links.

**Source:** `scripts/backbone/temporal/import_enriched_periods.py`. ~6,000 edges total (2,961 each) are intentional structural features of the temporal/geographic backbone.

**Schema:** Documented in `REQUIREMENTS.md`, `AI_CONTEXT.md`. Edges may carry `temporal_scope` qualifiers for scoped queries.

---

## Wikimedia Category Contamination

**Q4167836 (Wikimedia category)** entities are Wikipedia's administrative categorization infrastructure — not domain entities. They enter via backlinks to domain seeds and inflate entity counts with structurally meaningless edges (e.g. P971 "connects to" between category and topic).

**Harvester:** `DEFAULT_P31_DENYLIST` includes Q4167836. Future harvests reject category entities.

**Existing graph cleanup — diagnostic queries:**

```cypher
// Count category entities (by label prefix)
MATCH (e:Entity)
WHERE e.label STARTS WITH 'Category:'
RETURN count(e) AS category_entity_count
```

```cypher
// Edge contamination from category sources
MATCH (e:Entity)-[r]->(b)
WHERE e.label STARTS WITH 'Category:'
RETURN type(r) AS edge_type, count(r) AS count
ORDER BY count DESC
```

---

## WIKIDATA_P* Edge Types

Some imports create edges with types like `WIKIDATA_P1343` instead of `P1343`. These are duplicates of the same Wikidata property. To normalize: run `remove_wikidata_prefix.py` (renames `WIKIDATA_P*` → `P*`). Requires APOC for relationship creation.
