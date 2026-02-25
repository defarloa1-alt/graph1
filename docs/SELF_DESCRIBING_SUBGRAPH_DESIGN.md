# Self-Describing System Subgraph — Design Document

**Date:** 2026-02-25  
**Status:** Design (pre-cleanup)  
**Source:** Advisor analysis of node/edge audit

---

## Two Distinct Concerns

| Concern | Role | Machine-readable | Human-readable |
|---------|------|------------------|----------------|
| **Structure** | What the system is at a point in time | SchemaRegistry, FederationRegistry | Data dictionary, Appendix R |
| **Process** | What the system does and how it evolves | ProcessRegistry, ADRs, pipeline state | KANBAN, AI_CONTEXT, ADRs |

Both must live as subgraphs, not just markdown, for epistemic consistency. SFAs query the graph; markdown is derived.

---

## Proposed Subgraph Structure

```
(:SYSTEM {name: "Chrystallum", version: "post-DPRR-2026-02-25"})
  -[:HAS_SCHEMA]->        (:SYS_SchemaRegistry)       // data dictionary
  -[:HAS_FEDERATION]->    (:SYS_FederationRegistry)   // federation sources + status
  -[:HAS_BIBLIOGRAPHY]->  (:SYS_BibliographyRegistry) // all source nodes
  -[:HAS_PROCESS]->       (:SYS_ProcessRegistry)      // ADRs, pipeline state, KANBAN
```

### SchemaRegistry (data dictionary)

- `:SYS_NodeType` — every label (Entity, Claim, Period, SubjectConcept, etc.) with required/optional properties
- `:SYS_EdgeType` — every relationship type with domain/range constraints
- `:SYS_Facet` — F001–F005 (18 facets)
- `:SYS_PropertyDefinition` — controlled vocabulary (scoping_status values, confidence ranges)

### FederationRegistry (Appendix R as subgraph)

- `:SYS_FederationSource` — DPRR, Pleiades, Trismegistos, LGPN, Wikidata, LCSH/FAST/LCC, PeriodO, CHRR (planned), CRRO (planned), OCD (planned)
- Properties: status, confidence, scoping_role, evidence_type, license, wikidata_property
- `:SCOPES` edges to entity types it can scope
- `:PROVIDES` edges to evidence types

### BibliographyRegistry

**Design principle (D-026):** BibliographyRegistry is a **living discovery layer**, not a static curated list. It grows as the entity graph grows — every entity with `viaf_id` extends the VIAF→LC SRU→MARC chain, auto-constructing BibliographySource nodes. The pipeline runs alongside cluster assignment; it is infrastructure, not a one-time build. The node model must reflect this: dynamic extension, not manual population.

- All SOURCE nodes the graph can cite
- DPRR, Broughton, Zmeskal (secondary for POSITION_HELD, familial edges)
- Hogan et al., Monea, "KGs Get Knowledge Wrong" (design justification)
- OCD, Syme (planned)
- **VIAF→MARC discovery:** Entities with viaf_id → LC authority → subjectOf → MARC bibliographic records → BibliographySource nodes auto-constructed
- `:JUSTIFIES_DESIGN_CHOICE` edges from design decisions to literature

### ProcessRegistry

- `:SYS_ADR` — ADR-001 through ADR-006
- `:SYS_PipelineStage` — harvest → scope → enrich → SFA reasoning
- `:SYS_KanbanItem` — status, priority, blocking
- `:SYS_Baseline` — snapshots (post-DPRR is first)

---

## Label Hygiene

All system nodes: `SYS_` prefix + `{system: true}`

| Current | Proposed |
|---------|----------|
| Chrystallum | Keep as root |
| EntityRoot | SYS_EntityRoot |
| FederationRoot | SYS_FederationRoot |
| FacetRoot | SYS_FacetRoot |
| SubjectConceptRoot | SYS_SubjectConceptRoot |
| NodeType | SYS_NodeType |
| EdgeType | SYS_EdgeType |
| Federation | SYS_FederationSource |
| ADR | SYS_ADR |
| Baseline | SYS_Baseline |
| PipelineStage | SYS_PipelineStage |
| KanbanItem | SYS_KanbanItem |
| BibEntry | SYS_BibEntry |

**Domain query exclusion:**
```cypher
MATCH (n) WHERE n.system IS NULL ...  // excludes all SYS_ nodes
```

---

## Current State (from audit)

### Orphaned / zero edges

| Label | Count | Verdict |
|-------|-------|---------|
| Place | 41,884 | Unfinished Pleiades import — Phase 2 enrichment pending |
| FacetedEntity | 360 | Orphaned — delete |
| Policy | 5 | Read contents first |
| BibliographySource | 3 | Wire into Chrystallum tree |
| Threshold | 3 | Read contents first |

### Staging / pipeline artifacts

| Label | Count | Verdict |
|-------|-------|---------|
| PeriodCandidate | 1,077 | All canonicalized — delete |
| PlaceTypeTokenMap | 212 | Pipeline lookup — delete |
| GeoCoverageCandidate | 357 | **Clarify target** — see diagnostic below |
| PropertyMapping | 706 | Decision: SchemaRegistry or config file |

### Keep but wire in

| Label | Notes |
|-------|-------|
| KnowledgeDomain | 1 node, 61 edges — merge into SubjectConceptRoot or wire to Chrystallum |
| BibliographySource | 3 nodes — wire into tree |

### Domain nodes (not system)

| Label | Count | Notes |
|-------|-------|-------|
| Office | 147 | Domain node — document in SchemaRegistry, not a system node |
| Entity | 13,661 | Domain |
| SubjectConcept | 61 | Domain |
| Period, Year | — | Domain |

---

## Rebuild Phases

### Phase A — Clean up (before adding)

1. Delete: FacetedEntity (360), PeriodCandidate (1,077), PlaceTypeTokenMap (212)
2. Investigate: Policy (5), Threshold (3), GeoCoverageCandidate (357)
3. Clarify: KnowledgeDomain vs SubjectConceptRoot
4. Clarify: PropertyMapping — runtime query or config?

### Phase B — Rebuild federation list

Replace 13 Federation nodes with current operational list. Add DPRR, Trismegistos, LGPN. Properties: status, confidence, scoping_role, evidence_type, license, wikidata_property.

### Phase C — Add missing branches

- SchemaRegistry (data dictionary)
- ProcessRegistry (ADRs, pipeline state, baseline)
- BibliographyRegistry (living discovery layer — VIAF→MARC auto-extends; see D-026)

### Phase D — Label hygiene

SYS_ prefix + system: true on all system nodes.

---

## Diagnostic Queries

### 1. Chrystallum-connected labels
```cypher
MATCH (sys:Chrystallum)-[*..4]->(n)
RETURN labels(n) AS label, count(n) AS count
ORDER BY count DESC
```

### 2. PropertyMapping connection to system
```cypher
MATCH (n:PropertyMapping) 
OPTIONAL MATCH (sys:Chrystallum)-[*..10]->(n)
RETURN count(n) AS total_pm, count(sys) AS connected_to_system
```

### 3. GeoCoverageCandidate target (CRITICAL — determines keep vs delete)
```cypher
MATCH (gcc:GeoCoverageCandidate)-[r]->(n)
RETURN type(r) AS rel, labels(n) AS target, count(*) AS cnt
ORDER BY cnt DESC
```

### 4. KnowledgeDomain connections
```cypher
MATCH (kd:KnowledgeDomain)
RETURN kd, [(kd)-[r]-(n) | {rel: type(r), label: labels(n), dir: "any"}] AS connections
```

### 5. FacetedEntity edges (confirm orphaned)
```cypher
MATCH (n:FacetedEntity)
OPTIONAL MATCH (n)-[r]-()
RETURN count(n) AS total, count(r) AS with_edges
```

### 6. PropertyMapping sample
```cypher
MATCH (pm:PropertyMapping)-[:HAS_PRIMARY_FACET]->(f:Facet)
RETURN pm.property_id AS property, f.key AS primary_facet
LIMIT 10
```

---

## First Deliverable (advisor recommendation)

**FederationRegistry first** — most immediate pipeline utility. Scoping advisor can query live instead of hardcoded config. Bounded list, well-defined properties.

Then SchemaRegistry (SFA self-orientation), then BibliographyRegistry, then ProcessRegistry.

---

## Diagnostic Results (2026-02-25)

| Query | Result |
|-------|--------|
| 1. Chrystallum-connected | Federation (69), Facet (18), FederationRoot, FacetRoot |
| 2. PropertyMapping | 706 total, **0 connected to system** — disconnected |
| 3. GeoCoverageCandidate | Links PeriodCandidate ←→ GeoCoverageCandidate → Period (2,961 each). Staging join node. |
| 4. KnowledgeDomain | DOMAIN_OF → 61 SubjectConcepts — **root of subject hierarchy** |
| 5. FacetedEntity | 360 total, **0 edges** — confirmed orphaned |
| 6. PropertyMapping | P-codes (P186, P547, etc.) → Facet keys. SchemaRegistry candidate. |
| 7. Policy | 5 governance policies (LocalFirstCanonicalAuthorities, etc.) — keep, wire in |
| 7. Threshold | 3 configs (crosslink_ratio_split, level2_child_overload, facet_drift_alert) — keep, wire in |
| 8. Place | 41,884 nodes, **0 edges** — unfinished Pleiades import |

**GeoCoverageCandidate verdict:** Staging. Links PeriodCandidate to Period during geo-coverage computation. Delete with PeriodCandidate, or migrate coverage to Period first.

---

## Open Questions

1. ~~**GeoCoverageCandidate**~~ — Resolved: staging join. Delete with PeriodCandidate.
2. **PropertyMapping** — Disconnected from Chrystallum. Wire into SchemaRegistry or move to config.
3. **KnowledgeDomain** — Root of SubjectConcept hierarchy (61 DOMAIN_OF). Merge into SubjectConceptRoot or wire to Chrystallum.
4. **Place (41,884)** — Add SYS_Baseline note: "41,884 Place nodes from Pleiades CSV, Phase 2 enrichment pending."
5. **Federation count** — 69 nodes with Federation label in Chrystallum tree; expected 13. Investigate.
