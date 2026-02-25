# Chrystallum Node Label Architecture Table

**Date:** 2026-02-21  
**Purpose:** Clarify what we have, what we use, why, and relations. Run by architecture before further schema work.  
**Source:** Block catalog, SELF_DESCRIBING_SUBGRAPH_DESIGN, DECISIONS, ONTOLOGY_PRINCIPLES, CONCEPT_TO_SUBJECTCONCEPT_MIGRATION

---

## Summary

| Category | Count | Verdict |
|----------|-------|---------|
| **Canonical domain** | ~15 | Keep, document |
| **System / metanode** | ~10 | Keep, SYS_ prefix planned |
| **Agent / governance** | ~12 | Keep, wire to Chrystallum |
| **Legacy / staging / junk** | ~8 | Delete or migrate |
| **Unclear / investigate** | ~5 | Read contents, decide |

---

## Full Table

| Label | What we have | What we use | Why | Key relations | Verdict |
|-------|--------------|-------------|-----|---------------|--------|
| **Entity** | 13,661 | Core domain | Wikidata-derived historical entities; QID merge key (D-002) | MEMBER_OF→SubjectConcept, pleiades_id, viaf_id, etc. | **Canonical** |
| **SubjectConcept** | 61 | Thematic anchors | Research themes (Q17167 Roman Republic); SCA/SFA orbit; MEMBER_OF targets | Entity─MEMBER_OF→SC, DOMAIN_OF←KnowledgeDomain, PART_OF hierarchy | **Canonical** |
| **Subject** | 0 | — | LCSH/FAST topical classification (library backbone). Planned by Library Authority Step 1. | SUBJECT_OF (entity→subject), BROADER_THAN (subject hierarchy) | **Planned** — not yet imported |
| **Place** | 41,884 | Geographic backbone | Pleiades import; Phase 2 enrichment pending (coordinates, LOCATED_IN) | 0 edges currently — unfinished | **Canonical** — wire in Phase 2 |
| **Period** | — | Temporal backbone | Historical periods; temporal_anchor model (D-012) | PART_OF, DURING, STARTS_IN_YEAR | **Canonical** |
| **Year** | — | Temporal spine | Concrete years | FOLLOWED_BY, PART_OF→Period | **Canonical** |
| **Event** | — | Domain | Historical events | DURING→Period, CAUSED, PARTICIPATED_IN | **Canonical** |
| **Human** | — | Domain | Persons (use Human not Person per migration) | MEMBER_OF, PARTICIPATED_IN, POSITION_HELD | **Canonical** |
| **Work** | — | Domain | Literary/artistic works | MAIN_SUBJECT, AUTHOR_OF | **Canonical** |
| **Organization** | — | Domain | Institutions, groups | MEMBER_OF, LOCATED_IN | **Canonical** |
| **Office** | 147 | Domain | Magistracies, roles | POSITION_HELD→Human | **Canonical** |
| **Cognomen, Gens, Praenomen** | — | Prosopographic | Roman naming components | — | **Canonical** — Roman-specific |
| **Dynasty** | — | Domain | Royal lines | — | **Canonical** |
| **Institution** | — | Domain | Formal organizations | — | **Canonical** |
| **Location** | — | Geographic | May overlap Place; clarify | — | **Investigate** |
| **Material, Object** | — | Domain | Physical things | — | **Canonical** |
| **Activity** | — | — | Unclear vs Event | — | **Investigate** |
| **Chrystallum** | 1 | System root | Graph root; owns subsystems | HAS_FEDERATION→FederationRoot, HAS_FACET→FacetRoot, etc. | **System** |
| **SYS_FederationRegistry** | — | Metanode | Federation sources (D-016) | — | **System** |
| **SYS_FederationSource** | — | Metanode | DPRR, Pleiades, Wikidata, etc. | SCOPES, PROVIDES | **System** |
| **EntityRoot, FacetRoot, SubjectConceptRoot** | — | System | Structural roots | CONTAINS, HAS_* | **System** — SYS_ prefix planned |
| **AgentRegistry** | — | Agent | Agent deployment tracking | — | **System** |
| **Agent** | — | Agent | SFA instances | — | **System** |
| **Claim** | — | Governance | Evidence-aware assertions | SUBJECT_OF, JUSTIFIES | **Canonical** |
| **FacetClaim** | — | Governance | Facet-specific claims | — | **Canonical** |
| **ProposedEdge** | — | Governance | Pending relationship proposals | — | **Canonical** |
| **Facet** | 18 | Config | F001–F005, 18 facets | HAS_PRIMARY_FACET←PropertyMapping | **Canonical** |
| **FacetCategory** | — | Config | Facet groupings | — | **Investigate** |
| **FacetAssessment** | — | Agent | Per-claim facet scores | ASSESSES_FACET | **Canonical** |
| **AnalysisRun** | — | Governance | Analysis batch tracking | — | **Canonical** |
| **PropertyMapping** | 706 | Config | P-codes → Facet; disconnected from Chrystallum | HAS_PRIMARY_FACET→Facet | **Wire or config** — SchemaRegistry candidate |
| **PropertyType** | — | Schema | — | — | **Investigate** |
| **EntityType** | — | Schema | Entity classification | — | **Investigate** |
| **KnowledgeDomain** | 1 | Subject root | Root of SubjectConcept hierarchy; 61 DOMAIN_OF edges | DOMAIN_OF→SubjectConcept | **Wire** — merge into SubjectConceptRoot |
| **BibliographySource** | 3 | Metanode | Source citations; BibliographyRegistry (D-026) | — | **Wire** — living layer |
| **Policy** | 5 | Config | Governance (LocalFirstCanonicalAuthorities, etc.) | — | **Keep** — wire to Chrystallum |
| **Threshold** | 3 | Config | crosslink_ratio_split, facet_drift_alert, etc. | — | **Keep** — wire to Chrystallum |
| **Schema** | — | Metanode | SchemaRegistry candidate | — | **Investigate** |
| **StatusType** | — | — | — | — | **Investigate** |
| **LegalRestriction** | — | — | — | — | **Investigate** |
| **RetrievalContext** | — | — | — | — | **Investigate** |
| **PlaceName, PlaceType, PlaceVersion** | — | Geographic | Place metadata | — | **Canonical** |
| **Geometry, GeoSemanticType** | — | Geographic | Spatial representation | — | **Canonical** |
| **Position** | — | Prosopographic | Role/office holder | — | **Investigate** |
| **TemporalAnchor** | — | Temporal | Replaces Period for temporal model (D-012) | — | **Canonical** |
| **FacetedEntity** | 360 | — | Tier 2 cipher hubs; 0 edges | — | **Delete** — orphaned |
| **PeriodCandidate** | 1,077 | — | Staging; all canonicalized | — | **Delete** |
| **PlaceTypeTokenMap** | 212 | — | Pipeline lookup | — | **Delete** |
| **GeoCoverageCandidate** | 357 | — | Staging join PeriodCandidate↔Period | — | **Delete** with PeriodCandidate |

---

## Subject vs SubjectConcept — Architecture Clarification

| Term | Role | Source | Count | Relations |
|------|------|--------|-------|------------|
| **SubjectConcept** | Thematic anchor | QID-seeded (Q17167, etc.); hand-authored or harvested | 61 | Entity─MEMBER_OF→SC; PART_OF hierarchy; DOMAIN_OF←KnowledgeDomain |
| **Subject** | Topical classification | LCSH/FAST (library backbone) | 0 | Planned: entity─SUBJECT_OF→Subject; Subject─BROADER_THAN→Subject |

**Design note:** `create_subject_nodes.py` uses `SubjectConcept:Subject` (dual label) for LCSH-derived nodes. Library Authority Step 1 (FAST import) will create Subject nodes. The architecture separates:
- **Structure** (entity types, hierarchies) — what something IS
- **Topics** (Subject) — what something is ABOUT (ONTOLOGY_PRINCIPLES)

SubjectConcept = thematic domain for SCA/SFA. Subject = library topical classification. They can overlap when an LCSH heading maps to a SubjectConcept (e.g. "Rome--History--Republic").

---

## Key Relationship Types

| Relation | Domain | Range | Purpose |
|----------|--------|-------|---------|
| MEMBER_OF | Entity | SubjectConcept | Cluster assignment; entity belongs to thematic anchor |
| SUBJECT_OF | Entity | Subject | Topical classification (when Subject exists) |
| PART_OF | SubjectConcept, Period, Place | Parent | Hierarchy |
| DOMAIN_OF | KnowledgeDomain | SubjectConcept | Subject hierarchy root |
| SCOPES | SYS_FederationSource | Entity type | Federation can scope this type |
| HAS_PRIMARY_FACET | PropertyMapping | Facet | P-code → facet routing |
| POSITION_HELD | Human | Office | Magistracies |
| DURING | Event | Period | Temporal containment |
| LOCATED_IN | Place | Place | Geographic containment (Phase 2) |

---

## Recommended Actions

1. **Run by architecture** — Validate this table against BLOCK_CATALOG and SELF_DESCRIBING_SUBGRAPH_DESIGN.
2. **Delete staging** — FacetedEntity (360), PeriodCandidate (1,077), PlaceTypeTokenMap (212), GeoCoverageCandidate (357) — after confirming no downstream dependencies.
3. **Wire disconnected** — PropertyMapping (706), KnowledgeDomain, BibliographySource, Policy, Threshold into Chrystallum tree or SchemaRegistry.
4. **Investigate** — Activity, Location, PropertyType, EntityType, Schema, StatusType, LegalRestriction, RetrievalContext, Position.
5. **Subject design** — **D-028:** Subject and SubjectConcept are distinct layers. Do not merge. Subject = library classification; SubjectConcept = interpretive anchor. Subject CLASSIFIES SubjectConcept.
