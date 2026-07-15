# Self-Describing Subgraph — Design Notes and Open Issues

**Date:** 2026-02-25  
**Source:** Main chat session (recovered)  
**Status:** Design agreed, build not started. Cleanup prerequisites partially resolved.

---

## What This Is

A subgraph design for making Chrystallum epistemically consistent about itself — the graph contains a machine-readable description of its own schema, federations, bibliography, and process state. SFAs can query it directly rather than reading stale markdown files.

**Not the same as the SystemDescription node** (which is a generated narrative). This is a structured subgraph that agents can traverse.

---

## Design Decision: Same Instance

System subgraph lives in the same Neo4j instance as domain data. Label hygiene prevents contamination.

**Label convention agreed:** Prefix all system nodes with `SYS_` and add `{system: true}` property.

```cypher
// Domain query — exclude all system nodes
MATCH (n) WHERE n.system IS NULL ...

// System query — explicit
MATCH (n:SYS_NodeType) ...
```

**Node type examples:**
- `:SYS_NodeType`, `:SYS_EdgeType`
- `:SYS_FederationSource`, `:SYS_ADR`
- `:SYS_Baseline`, `:SYS_PipelineStage`, `:SYS_KanbanItem`, `:SYS_BibEntry`

---

## Agreed Subgraph Structure

Root node:
```
(:SYSTEM {name: "Chrystallum", version: "post-DPRR-2026-02-25"})
  -[:HAS_SCHEMA]->        (:SchemaRegistry)
  -[:HAS_FEDERATION]->    (:FederationRegistry)
  -[:HAS_BIBLIOGRAPHY]->  (:BibliographyRegistry)
  -[:HAS_PROCESS]->       (:ProcessRegistry)
```

### SchemaRegistry (data dictionary)
- `:NodeType` nodes for every label (required/optional properties)
- `:EdgeType` nodes for every relationship type (domain/range)
- `:FacetNode` nodes — already exist, wire here
- `:PropertyDefinition` nodes for controlled vocabulary

Machine-readable version of DATA_DICTIONARY.md. SFAs query live rather than reading markdown.

### FederationRegistry (Appendix R as subgraph)
- `:FederationSource` nodes — one per federation
- Properties: `status`, `confidence`, `license`, `wikidata_property`, `access_pattern`, `last_import_date`, `entity_count`, `edge_count`
- `:SCOPES` edges to entity types
- `:PROVIDES` edges to evidence types

**Critical gap:** Current 13 Federation nodes reflect the pre-DPRR list (BabelNet, WorldCat, MARC are there; DPRR, Trismegistos, LGPN are missing). Needs rebuild.

### BibliographyRegistry
- All SOURCE nodes the graph can cite (including sources *about* the system itself)
- DPRR, Broughton, Zmeskal as secondary sources for POSITION_HELD and familial edges
- Hogan et al., Monea, "KGs Get Knowledge Wrong" as design justification sources
- OCD, Syme as planned federation sources
- `:JUSTIFIES_DESIGN_CHOICE` edges from ADR nodes to literature

Currently: 3 BibliographySource nodes exist but have **zero edges** — never wired in.

### ProcessRegistry
- `:ADR` nodes (ADR-001 through ADR-006)
- `:PipelineStage` nodes (harvest → scope → enrich → SFA reasoning)
- `:KanbanItem` nodes — **note:** these are point-in-time snapshots only; canonical KANBAN stays in markdown
- `:Baseline` nodes — post-DPRR is the first; record graph state at significant milestones

---

## Build Priority (Agreed)

1. **FederationRegistry first** — most immediate pipeline utility; scoping advisor currently reads hardcoded config, should query live
2. **SchemaRegistry second** — unblocks SFA self-orientation queries
3. **BibliographyRegistry and ProcessRegistry** — after

---

## Node Audit — Cleanup Decisions (From Graph State 2026-02-25)

### Graph snapshot used for this audit:

| Label | Nodes | Edges | Notes |
|-------|-------|-------|-------|
| Place | 41,884 | 0 | Pleiades import, Phase 2 enrichment never run |
| Entity | 13,661 | ~34,071 | Core domain, keep |
| Year | 4,025 | ~4,024 | Temporal backbone, keep |
| PeriodCandidate | 1,077 | 5,126 | All CANONICALIZED_AS → Period; staging complete |
| Period | 1,077 | ~3,107 | Domain, keep |
| PropertyMapping | 706 | 959 | Pipeline artifact — HAS_PRIMARY_FACET to Facet |
| FacetedEntity | 360 | 0 | Orphaned, no edges |
| GeoCoverageCandidate | 357 | 5,922 | Pipeline join node — **OPEN QUESTION** |
| PlaceTypeTokenMap | 212 | 303 | Pipeline lookup table |
| Office | 147 | 6,089 | Domain node (POSITION_HELD target), keep |
| SubjectConcept | 61 | ~3,751 | Core, keep (61 edges/node avg — most connected) |
| Facet | 36 | ~546 | Should be 18 — likely duplicates from build runs |
| EntityType | 14 | 28 | System, keep |
| PlaceType | 14 | 339 | Domain taxonomy, keep |
| Federation | 13 | 125 | Keep but rebuild (wrong list) |
| Schema | 9 | 9 | Data dictionary stub, keep |
| Policy | 5 | 0 | Orphaned — read before deleting |
| GeoSemanticType | 4 | 10 | Borderline — taxonomy or pipeline config |
| BibliographySource | 3 | 0 | Keep — wire into Chrystallum tree |
| Threshold | 3 | 0 | Orphaned — read before deleting |
| Agent | 3 | 6 | System placeholder, keep |
| EntityRoot | 1 | 9 | Keep |
| SubjectConceptRoot | 1 | 2 | Keep — clarify relationship to KnowledgeDomain |
| AgentRegistry | 1 | 4 | Keep |
| SubjectConceptRegistry | 1 | 1 | Keep — clarify vs SubjectConceptRoot |
| Chrystallum | 1 | 2 | System root, keep |
| FederationRoot | 1 | 14 | Keep |
| FacetRoot | 1 | 19 | Keep |
| KnowledgeDomain | 1 | 61 | Active (61 DOMAIN_OF edges from SubjectConcept) — wire in |

### Delete (safe, no investigation needed)

```cypher
-- PeriodCandidate: all canonicalized, staging complete
MATCH (pc:PeriodCandidate) DETACH DELETE pc

-- PlaceTypeTokenMap: pipeline lookup table
MATCH (n:PlaceTypeTokenMap) DETACH DELETE n

-- FacetedEntity: zero edges, confirmed orphaned
MATCH (n:FacetedEntity) DETACH DELETE n
```

### Delete after reading contents

```cypher
-- Policy: check what these are first
MATCH (n:Policy) RETURN n

-- Threshold: same
MATCH (n:Threshold) RETURN n
```

### Keep but wire into tree

- **BibliographySource (3)** — `MERGE (sys:Chrystallum)-[:HAS_BIBLIOGRAPHY]->(b:BibliographySource)`
- **KnowledgeDomain (1)** — has 61 DOMAIN_OF edges from SubjectConcept; either merge into SubjectConceptRoot or wire as `(sys)-[:HAS_KNOWLEDGE_DOMAIN_ROOT]->(kd)`
- **PropertyMapping (706)** — actively used (HAS_PRIMARY_FACET → Facet); wire into SchemaRegistry or keep as-is if pipeline queries it directly

### Clarify

- **Facet count = 36, should be 18** — run `MATCH (f:Facet) RETURN f.key, count(f) ORDER BY count(f) DESC` to find duplicates
- **SubjectConceptRoot vs SubjectConceptRegistry** — one of these is likely redundant; the edge map shows SubjectConceptRegistry connects to nothing downstream
- **KnowledgeDomain vs SubjectConceptRoot** — KnowledgeDomain has the active edges (61 DOMAIN_OF in); SubjectConceptRoot has only 2 edges. Likely KnowledgeDomain is the older label and SubjectConceptRoot was created later without migrating the edges.

### Flag as unfinished import (do not delete)

- **Place (41,884)** — Phase 2 Pleiades enrichment not run. Nodes exist with no relationships. Add `SYS_Baseline` note: *41,884 Place nodes imported from Pleiades CSV; Phase 2 geo-enrichment pending (LOCATED_IN, HAS_PLACE edges not yet built).*

---

## OPEN ISSUE — GeoCoverageCandidate (Blocking Cleanup Script)

**357 nodes, 5,922 edges.**  
Receives `HAS_GEO_COVERAGE_CANDIDATE` from Period (2,961 edges in).  
Sends `HAS_GEO_COVERAGE` out (2,961 edges out).  
But Place has zero edges — so GeoCoverageCandidate is NOT linking to Place nodes.

**Unresolved question:** What do GeoCoverageCandidate nodes actually point to?

```cypher
MATCH (gcc:GeoCoverageCandidate)-[r]->(n)
RETURN type(r) AS rel, labels(n) AS target, count(*) AS cnt
LIMIT 10
```

- If target is **Period** → these are domain data (geographic overlap between periods). **Keep.**
- If target is **Place** → these are staging artifacts linking Period to orphaned Place nodes. **Delete.**

**This query was not run before the session ended. Run it before writing the cleanup script.**

---

## Wiring Gaps (Post-Cleanup)

After cleanup, the system subgraph still needs:

1. **DPRR added to FederationRegistry** — not in the current 13 Federation nodes
2. **Trismegistos, LGPN added** — same
3. **SYS_Baseline node** — record post-DPRR counts as a graph node
4. **BibliographySource wired** — 3 nodes exist, zero edges
5. **KnowledgeDomain resolved** — bring into tree or merge with SubjectConceptRoot

---

## Relationship to Existing Docs

| This doc | Other doc | Relationship |
|----------|-----------|--------------|
| FederationRegistry design | `docs/prosopographic_federation_design.md` | Prosopographic federation design is a subset |
| SchemaRegistry design | `DATA_DICTIONARY.md` | SchemaRegistry is the machine-readable version |
| ProcessRegistry ADRs | `Federation/CHRYSTALLUM_HANDOFF.md` (legacy) | ADRs are specified there, not yet in graph |
| SYS_Baseline node | `docs/BASELINE_POST_DPRR_2026-02-25.md` | Baseline doc → should be mirrored as graph node |
