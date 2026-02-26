# Entity Definition: Schema vs Pipeline

**Status:** Architectural clarification (2026-02-21)  
**Resolves:** Inconsistent use of "entity" across schema, ontology, and pipeline.

---

## Two Definitions

### 1. Schema / Ontology (Normative)

**Sources:** `Key Files/ARCHITECTURE_ONTOLOGY.md`, `Neo4j/schema/01_schema_constraints.cypher`, `07_core_pipeline_schema.cypher`

**Entity** = first-class node with a **typed label** and matching `entity_type`:

| Label       | entity_type | Identity      |
|------------|-------------|---------------|
| `:Human`   | `"Human"`   | entity_id, qid |
| `:Place`   | `"Place"`   | entity_id, qid |
| `:Event`   | `"Event"`   | entity_id, qid |
| `:Period`  | `"Period"`  | entity_id, qid |
| `:SubjectConcept` | (uses qid/subject_id) | subject_id or qid |
| `:Organization`   | `"Organization"` | entity_id, qid |
| `:Work`    | `"Work"`    | entity_id, qid |
| …          | …           | …             |

Each type has its own label, required properties, and constraints. Edges reference typed nodes: `(Human)-[:PARTICIPATED_IN]->(Event)`, `(Place)-[:LOCATED_IN]->(Place)`.

---

### 2. Pipeline (Current Implementation)

**Sources:** `scripts/backbone/subject/cluster_assignment.py`, `scripts/integration/prepare_neo4j_with_ciphers.py`, `scripts/neo4j/import_sca_to_neo4j.py`

**Entity** = any harvested Wikidata node, created as **generic `:Entity`**:

- **Label:** Always `:Entity` (no `:Human`, `:Place`, `:Event`)
- **entity_type:** Varies by script:
  - `cluster_assignment`: always `'concept'`
  - `prepare_neo4j_with_ciphers`, `import_entities_with_parameters`: `PERSON`, `PLACE`, `EVENT`, etc. (from `classify_entity_type`)
- **Edges:** `(Entity)-[:MEMBER_OF]->(SubjectConcept)`

---

## Mismatch Summary

| Aspect        | Schema / Ontology        | Pipeline (current)              |
|---------------|--------------------------|----------------------------------|
| **Label**     | `:Human`, `:Place`, `:Event`, … | `:Entity` only                  |
| **entity_type** | `"Human"`, `"Place"`, `"Event"` | `'concept'` or `PERSON`/`PLACE`/`EVENT` |
| **Type source** | Explicit per-type schema | P31-based classification or hardcoded |
| **Identity**  | entity_id per type        | entity_id, qid (generic)         |

Additional inconsistency: ontology uses `"Human"`; `entity_cipher` and `classify_entity_type` use `PERSON`. Same semantic, different strings.

---

## Proposed Alignment

### Option A — Typed labels (schema-aligned)

1. **Harvester / entity store:** Use `classify_entity_type` (or equivalent) to infer type from P31.
2. **Create typed nodes:** `:Human`, `:Place`, `:Event`, `:Period`, etc., instead of generic `:Entity`.
3. **entity_type:** Use ontology values (`"Human"`, `"Place"`, `"Event"`) for consistency with `ARCHITECTURE_ONTOLOGY.md`.
4. **entity_id:** Use type-prefixed IDs (e.g. `hum_Q1048`, `plc_Q220`) as in `entity_cipher`.

### Option B — Generic `:Entity` with typed entity_type (minimal change)

1. Keep `:Entity` as the single label.
2. Standardize `entity_type` to ontology values (`Human`, `Place`, `Event`, …).
3. Fix `cluster_assignment` to use `classify_entity_type` instead of hardcoding `'concept'`.
4. Add `entity_type` index for typed queries.

### Recommendation

**Option A** matches the schema and ontology and supports typed edges (`(Human)-[:PARTICIPATED_IN]->(Event)`). It requires more pipeline changes but yields a graph that matches the intended architecture.

**Option B** is a smaller change and keeps a single label; it is acceptable if typed labels are deferred.

---

## Type Mapping (P31 → Ontology)

| P31 QID (instance of) | Ontology entity_type | entity_cipher prefix |
|----------------------|----------------------|----------------------|
| Q5 (human)           | Human                | per                  |
| Q515, Q486972, …      | Place                | plc                  |
| Q1190554, Q198, Q178561 | Event             | evt                  |
| Q11514315, Q6428674, Q186081 | SubjectConcept | sub                  |
| Q43229, Q4830453      | Organization         | org                  |
| Q47461344, Q234460    | Work                 | wrk                  |
| (default)             | Concept              | con                  |

`scripts/tools/entity_cipher.py` already has `classify_entity_type` and `ENTITY_TYPE_PREFIXES`. Add a small mapping layer to convert `PERSON` → `Human`, `PLACE` → `Place`, etc., for ontology alignment.

---

## Affected Scripts

| Script | Current behavior | Change for Option A |
|--------|------------------|---------------------|
| `cluster_assignment.py` | `:Entity` + `entity_type='concept'` | Use `classify_entity_type`, create typed labels |
| `prepare_neo4j_with_ciphers.py` | `:Entity` + PERSON/PLACE/… | Create `:Human`, `:Place`, etc. |
| `import_entities_with_parameters.py` | `:Entity` + typed entity_type | Same |
| `import_sca_to_neo4j.py` | `:Entity` | Same |
| `link_entities_to_subjects.py` | Queries `:Entity` | Update to support both or typed only |

---

## Summary

- **Schema:** Entity = typed node (`:Human`, `:Place`, `:Event`, …) with matching `entity_type`.
- **Pipeline:** Entity = generic `:Entity` with `entity_type` often `'concept'` or inconsistently typed.
- **Fix:** Align pipeline with schema by creating typed nodes and standardizing `entity_type` values.
