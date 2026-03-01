# Neo4j Node Type Gap Analysis

**Purpose:** Compare `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md` to node types defined in schema/Cypher.  
**Date:** 2026-02-27

---

## Summary

| Category | In Reference | In Schema/Cypher | Gap |
|----------|--------------|------------------|-----|
| Documented | 25+ types | — | — |
| In schema, not in reference | — | 20+ types | See below |
| Deprecated / shell | — | Several | See below |

---

## Node Types IN REFERENCE DOC ✓

| Label | Section | Status |
|-------|---------|--------|
| LCSH_Heading | 1 | Active (Phase 0 loader) |
| Pleiades_Place | 1 | Active |
| Periodo_Period | 1 | Active |
| DPRR_Office | 1 | Active |
| WorldCat_Work | 1 | Active |
| LCC_Class | 1 | Active |
| Discipline (legacy) | 1 | Legacy (lcsh_broader_than_edges) |
| CanonicalFacet | 2 | Active |
| FacetCategory | 2 | Legacy |
| Human | 3 | Active |
| Place | 3 | Active |
| Period | 3 | Active |
| Event | 3 | Active |
| Year | 3 | Active |
| Work | 3a | Spec'd, loader not wired |
| Discipline (registry) | 3a | Spec'd, loader not wired |
| SubjectDomain | 3a | Spec'd, loader not wired |
| SubjectConcept | 4 | Active |
| ClassificationAnchor | 4 | Active (SCA positioning) |
| LCSH_Subject | 4 | Active (authority, distinct from LCSH_Heading) |
| FAST_Subject | 4 | Active |
| Claim | 5 | Active |
| FacetAssessment | 5 | Active |
| Agent | 6 | Active |
| SubjectConceptRegistry | 6 | Active |
| Decade, Century, Millennium | 7 | Active |
| Chrystallum | 8 | Active |
| Federation, FederationRoot | 8 | Active |
| SYS_Policy, PolicyVersion, etc. | 8 | Active |

---

## Node Types IN SCHEMA/CYPHER — NOT IN REFERENCE (or partial)

### Used in graph — add to reference

| Label | Source | Notes |
|-------|--------|-------|
| **Entity** | relationships_comprehensive, validate_changes, REQUIREMENTS | Generic QID-based node; `MEMBER_OF`→SubjectConcept. Core harvest output. **Not in reference.** |
| **RetrievalContext** | 09_core_pipeline_pilot_seed, 07_core_pipeline_schema | Claim evidence; `retrieval_id`. **Not in reference.** |
| **AnalysisRun** | 09_core_pipeline_pilot_seed, 07_core_pipeline_schema | Tracks analysis runs; `run_id`, `pipeline_version`. **Not in reference.** |
| **Facet** (facet_id) | 09_core_pipeline_pilot_seed, bootstrap_subject_concept_agents | Legacy facet with `facet_id` (e.g. `facet_political`). Distinct from CanonicalFacet. **Partial:** reference has FacetAssessment, not Facet. |
| **SubjectConceptRoot** | bootstrap_subject_concept_agents | Root of SubjectConcept tree. **Not in reference.** |
| **AgentRegistry** | bootstrap_subject_concept_agents | Registry for agents. **Not in reference** (reference has Agent only). |
| **SYS_FederationRegistry** | validate_changes | Contains SYS_FederationSource. **Not in reference.** |
| **SYS_FederationSource** | validate_changes, SCA positioning | Federation source nodes (e.g. Wikidata). **Not in reference.** |

### Schema-defined but likely unused / shell

| Label | Source | Notes |
|-------|--------|-------|
| **Geometry** | 01_schema_constraints | geo_id. **Shell** — no loader found. |
| **Organization** | 01_schema, 06_meta_schema | entity_id, qid. **Shell** — Work HAS_PUBLISHER→Organization spec'd but not wired. |
| **Institution** | 01_schema, 06_meta_schema | entity_id. **Shell** — no loader. |
| **Dynasty** | 01_schema, 06_meta_schema | entity_id. **Shell** — Roman naming, no loader. |
| **LegalRestriction** | 01_schema, 06_meta_schema | entity_id. **Shell** — no loader. |
| **Position** | 01_schema | entity_id. **Shell** — office/role, no loader. |
| **Material** | 01_schema | entity_id. **Shell** — artifacts, no loader. |
| **Object** | 01_schema | entity_id. **Shell** — physical objects, no loader. |
| **Activity** | 01_schema | entity_id. **Shell** — no loader. |
| **Gens** | 01_schema, 06_meta_schema, SCHEMA_REFERENCE | Roman clan. **Shell** — schema only. |
| **Praenomen** | 01_schema, 06_meta_schema | Roman first name. **Shell.** |
| **Cognomen** | 01_schema, 06_meta_schema | Roman family name. **Shell.** |
| **AuthorityRecord** | pleiades_bulk_ingest | Place ALIGNED_WITH_PLEIADES→AuthorityRecord. **Partial** — reference mentions in ALIGNED_WITH_PLEIADES but no node spec. |

### Meta-schema (introspection only)

| Label | Source | Notes |
|-------|--------|-------|
| **_Schema:AuthorityTier** | 06_meta_schema_graph | Meta — tier definitions. |
| **_Schema:NodeLabel** | 06_meta_schema_graph | Meta — label definitions. |
| **_Schema:RelationshipType** | 06_meta_schema_graph | Meta — relationship definitions. |
| **_Schema:FacetReference** | 06_meta_schema_graph | Meta — facet references. |
| **FacetReference** | FACET_DISCOVERY | May be same as above. |

### Federation / category (structural)

| Label | Source | Notes |
|-------|--------|-------|
| **Federation:Category** | create_federation, view_complete_structure | Structural. |
| **Federation:AuthoritySystem** | view_complete_structure | Structural. |
| **Federation:Organization** | create_federation | Structural. |
| **Facets:Category** | create_facets_cluster | Structural. |

---

## LCSH_Subject vs LCSH_Heading

| Label | Use | In Reference |
|-------|-----|--------------|
| **LCSH_Heading** | Federation survey nodes (Phase 0 loaders) | ✓ |
| **LCSH_Subject** | SubjectConcept authority link (HAS_LCSH_AUTHORITY) | ✓ |

Both exist; reference correctly distinguishes them.

---

## Recommendations

1. **Add to reference:** Entity, RetrievalContext, AnalysisRun, Facet (facet_id), SubjectConceptRoot, AgentRegistry, SYS_FederationRegistry, SYS_FederationSource, AuthorityRecord.
2. **Mark as shell/deprecated:** Geometry, Organization, Institution, Dynasty, LegalRestriction, Position, Material, Object, Activity, Gens, Praenomen, Cognomen — add a "Schema Shells (Unused)" section.
3. **Clarify Facet vs CanonicalFacet:** Reference has CanonicalFacet and FacetAssessment. Schema also has `Facet {facet_id}` (legacy). Document both.
4. **Entity:** Entity is central to the harvest/MEMBER_OF model. Add full spec.

---

## Query to list actual node labels in Neo4j

```cypher
CALL db.labels() YIELD label RETURN label ORDER BY label;
```

Run this against your graph to get the ground truth; this analysis is from schema/Cypher files only.
