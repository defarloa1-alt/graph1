# Chrystallum Data Dictionary

**Purpose:** Catalog of all node labels and relationship types in Neo4j, with counts, creating scripts, and notes.  
**Source:** `output/census.json` (graph census) + codebase grep.  
**Generated:** 2026-03-06

**Architecture reference:** `Key Files/ARCHITECTURE_CORE.md`, `Key Files/ARCHITECTURE_ONTOLOGY.md`, `Key Files/Main nodes.md`, and `Key Files/Appendices/` — canonical first-class nodes and planned types. Zero-count labels are often **planned / not yet implemented**, not orphaned.

**Appendices (by topic):** Entity types → `01_Domain_Ontology/Entity_Type_Taxonomies.md`; Relationship types → `01_Domain_Ontology/Canonical_Relationship_Types.md`; Facets → `01_Domain_Ontology/Subject_Facet_Classification.md`, `05_Architecture_Decisions/ADR_004_Canonical_18_Facet_System.md`; Temporal/geographic → `02_Authority_Integration/`; Legacy patterns → `04_Implementation_Patterns/Legacy_Implementation_Patterns.md`; Claims → `05_Architecture_Decisions/ADR_001_Claim_Identity_Ciphers.md`.

For property-level detail, see `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md`.

---

## POSITION_HELD vs ACTIVE_IN_YEAR (temporal overlap)

Both encode when a person was active, but at different levels:

| Relationship | Structure | Purpose |
|--------------|-----------|---------|
| **POSITION_HELD** | `(Person)-[r:POSITION_HELD {year, start_year, end_year}]->(Position)` | Source fact: "Person X held office Y in year(s) Z." Created by `dprr_import.py`. Dates live on the edge. |
| **ACTIVE_IN_YEAR** | `(Person)-[:ACTIVE_IN_YEAR {source:'position_held'}]->(Year)` | Derived index: "Person X was active in Year Y." Created by `migration_position_active_in_year.cypher` from POSITION_HELD. One edge per year in each position's range. |

**Why both?** ACTIVE_IN_YEAR is a materialized view for queries like "who was active in -59?" without traversing all POSITION_HELD edges and expanding year ranges. It links Person directly to the Year backbone.

**Data flow:** DPRR → `dprr_import.py` → POSITION_HELD (r.year) → `enrich_position_held_temporal.py` → r.start_year, r.end_year → `migration_position_active_in_year.cypher` → ACTIVE_IN_YEAR.

**Cleanup note:** ACTIVE_IN_YEAR is 100% derived from POSITION_HELD. If you change position years, re-run the migration. No other sources (birth/death, events) currently feed ACTIVE_IN_YEAR.

---

## Summary

| Metric | Count |
|--------|-------|
| Total nodes | 106,254 |
| Total relationships | 136,305 |
| Node labels | 75 |
| Relationship types | 217 |
| Zero-count labels (planned / not yet implemented) | 18 |

---

## Node Labels

Labels with **0 count** are typically **planned** per architecture (not yet implemented), not orphaned. See sanity check below.

| Label | Count | Creating Script(s) | Notes |
|-------|------:|--------------------|-------|
| Place | 44,040 | `build_wikidata_period_geo_backbone.py`, `link_place_admin_hierarchy.py`, `pleiades_bulk_ingest_roman_republic.py`, `import_pleiades_to_neo4j.py`, `fetch_tgn_places_sparql.py` | Core geographic |
| Pleiades_Place | 32,572 | `load_federation_survey.py`, `pleiades_bulk_ingest_roman_republic.py` | Federation survey |
| Entity | 14,469 | `dprr_import.py`, `person_harvest/executor.py`, `cluster_assignment.py`, `biographic/agent.py` | Supertype; Person/Place inherit |
| Person | 5,248 | `biographic/agent.py`, `hierarchy_relationships_loader.py`, `apply_person_label_gates.py` (SET) | Biographic core |
| LCC_Class | 4,490 | `load_lcc_nodes.py` | Library classification |
| Year | 4,030 | `genYearsToNeo.py`, `enrich_periods_multi_facet.py`, `generate_periods_cypher.py` | Temporal backbone |
| Discipline | 1,363 | `load_discipline_taxonomy.py` | Discipline registry |
| Periodo_Period | 1,118 | `load_federation_survey.py` | PeriodO federation |
| Cognomen | 1,000 | `create_onomastic_nodes.py` | Onomastic |
| Nomen | 917 | `create_onomastic_nodes.py` | Onomastic |
| Gens | 585 | `create_onomastic_nodes.py` | Onomastic |
| SYS_PropertyMapping | 500 | `import_property_mappings_direct.py`, migrations | SYS layer |
| WorldCat_Work | 196 | `load_federation_survey.py` | Federation survey |
| Position | 171 | `dprr_import.py` | DPRR offices |
| SYS_DecisionRow | 128 | `migration_remediation_decision_tables.cypher` | DMN |
| SYS_RelationshipType | 98 | `register_planned_sources.py`, `rebuild_federation_registry.py` | SYS registry |
| SYS_WikidataProperty | 55 | `migration_bio_decision_model.cypher` | DMN |
| Event | 45 | `biographic/agent.py` | Biographic |
| SYS_NodeType | 43 | `migration_facet_console.cypher`, `migration_bio_decision_model.cypher`, `sys_gaps_migration.cypher` | SYS registry |
| SubjectConcept | 30 | `create_subject_nodes.py`, `load_subject_concepts_qid_canonical.py`, `load_roman_republic_ontology.py` | Subject backbone |
| Tribe | 29 | `create_onomastic_nodes.py` | Onomastic |
| SYS_OnboardingStep | 26 | migrations | SYS |
| SYS_Threshold | 25 | `add_dmn_threshold_policy_nodes.cypher`, `hardcoded_rules_migration.cypher` | DMN |
| Praenomen | 24 | `create_onomastic_nodes.py` | Onomastic |
| WikidataType | 22 | `sca_persist.py` | SCA |
| SYS_DecisionTable | 21 | `migration_remediation_decision_tables.cypher` | DMN |
| Facet | 18 | `add_missing_facets.py`, `enrich_periods_multi_facet.py`, `create_facets_cluster.cypher` | Canonical facets |
| EntityType | 17 | legacy | See SYS_NodeType; architecture prefers SYS |
| SYS_FederationSource | 17 | `rebuild_federation_registry.py` | SYS |
| SYS_Policy | 16 | `add_dmn_threshold_policy_nodes.cypher`, `migration_bio_decision_model.cypher` | DMN |
| LCSH_Heading | 15 | `load_federation_survey.py`, `load_lcsh_survey.py` | Federation survey |
| PlaceType | 14 | `build_place_type_hierarchy.py` | Geographic |
| SYS_ValidationRule | 12 | migrations | SYS |
| Religion | 12 | migrations | Domain |
| RepertoirePattern | 12 | `migration_prh_repertoire.cypher`, `migration_prh_repertoire_extend.cypher` | PRH framework |
| TaskType | 11 | `migration_fischer_methodology.cypher` | Fischer methodology |
| SYS_ClaimStatus | 10 | migrations | SYS |
| Polity | 10 | migrations | Domain |
| Schema | 9 | migrations | Structure node |
| SYS_AnchorTypeMapping | 9 | migrations | SYS |
| HistoricalPolity | 9 | migrations | Domain |
| SYS_ConfidenceTier | 8 | migrations | SYS |
| SYS_ADR | 8 | `sys_gaps_migration.cypher` | ADRs |
| SYS_RejectionReason | 8 | migrations | SYS |
| SYS_EdgeType | 8 | migrations | SYS |
| SYS_ConfidenceModifier | 7 | migrations | SYS |
| Mechanism | 7 | `migration_prh_repertoire.cypher` | PRH |
| SYS_AuthorityTier | 6 | migrations | SYS |
| Fallacy | 6 | `migration_fischer_methodology.cypher` | Fischer |
| DigitalPrinciple | 6 | `migration_milligan_digital.cypher` | Milligan |
| SYS_QueryPattern | 5 | migrations | SYS |
| SYS_AgentType | 5 | migrations | SYS |
| Agent | 4 | `register_planned_sources.py` | Low count; SYS_AgentType (5) in migrations |
| GeoSemanticType | 4 | `build_place_type_hierarchy.py` | Geographic |
| SYS_ClassificationTier | 4 | migrations | SYS |
| RepertoireFamily | 4 | `migration_prh_repertoire.cypher` | PRH |
| BibliographySource | 3 | `dprr_import.py`, `dprr_bibliography_sources.cypher` | DPRR |
| MythologicalPerson | 3 | `apply_person_label_gates.py` (SET) | Biographic |
| SYS_FacetPolicy | 3 | `migration_facet_console.cypher` | SYS |
| Framework | 3 | `migration_framework_schema.cypher` | Frameworks |
| MethodologicalDomain | 3 | `migration_fischer_methodology.cypher` | Fischer |
| StatusType | 2 | `dprr_import.py` | DPRR |
| SYS_OnboardingProtocol | 2 | migrations | SYS |
| MethodologyText | 2 | `migration_fischer_methodology.cypher` | Fischer |
| Claim | 1 | `claim_ingestion_pipeline.py`, `subject_concept_api.py` | Claim pipeline |
| AnalysisRun | 1 | `claim_ingestion_pipeline.py` | Claim pipeline |
| FacetAssessment | 1 | `claim_ingestion_pipeline.py` | Claim pipeline |
| RetrievalContext | 1 | `claim_ingestion_pipeline.py` | Claim pipeline |
| Chrystallum | 1 | `migration_chrystallum_consolidate.cypher` | Root |
| Root | 1 | migrations | Structure node |
| FacetRoot | 1 | `bridge_facet_root.cypher` | Structure |
| EntityRoot | 1 | migrations | Structure |
| SubjectConceptRegistry | 1 | migrations | Structure |
| ProposedEdge | 1 | `claim_ingestion_pipeline.py` | Claim pipeline |
| SYS_FederationRegistry | 1 | `rebuild_federation_registry.py` | SYS |
| SYS_SubjectConceptRoot | 1 | migrations | Structure |
| DisciplineRegistry | 1 | migrations | Structure |
| SYS_ClassificationAlgorithm | 1 | migrations | SYS |
| SYS_SchemaRegistry | 1 | migrations | SYS |
| SYS_HarvestPlan | 1 | `sys_gaps_migration.cypher` | SYS |
| SYS_SchemaBootstrap | 1 | migrations | SYS |
| SubjectDomain | 1 | `sca_persist.py` | SCA |
| FallacyFamily | 1 | `migration_fischer_methodology.cypher` | Fischer |
| **Human** | **0** | `03_schema_initialization_simple.cypher` | **Planned** — ARCHITECTURE_ONTOLOGY canonical; Person (5,248) used in practice |
| **Geometry** | **0** | ARCHITECTURE_ONTOLOGY §3.1.2.2 | **Planned** — PlaceVersion→Geometry for spatial data |
| **Period** | **0** | `enrich_periods_multi_facet.py`, `create_canonical_spine.py` | **Planned** — canonical spine; Periodo_Period (1,118) exists |
| **Organization** | **0** | ARCHITECTURE_ONTOLOGY §3.1.6 | **Planned** — canonical first-class |
| **Institution** | **0** | ARCHITECTURE_ONTOLOGY §3.1.7 | **Planned** — canonical first-class |
| **Dynasty** | **0** | ARCHITECTURE_ONTOLOGY §3.1.8, Main nodes.md | **Planned** — canonical first-class |
| **LegalRestriction** | **0** | Main nodes.md | **Planned** — canonical first-class |
| **Work** | **0** | ARCHITECTURE_ONTOLOGY §3.1.10 | **Planned** — canonical; WorldCat_Work (196) is federation |
| **Material** | **0** | ARCHITECTURE_ONTOLOGY §3.1.12 | **Planned** — canonical first-class |
| **Object** | **0** | ARCHITECTURE_ONTOLOGY §3.1.13 | **Planned** — canonical first-class |
| **Activity** | **0** | ARCHITECTURE_ONTOLOGY | **Deprecated** — route to Event or SubjectConcept |
| **FacetCategory** | **0** | ARCHITECTURE_ONTOLOGY §3.2.6 | **Planned** — groups Facet nodes; Facet (18) exists |
| **PlaceName** | **0** | Pleiades import | **Planned** — place name variants |
| **Location** | **0** | Pleiades import | **Planned** — spatial hierarchy |
| **FacetedEntity** | **0** | legacy | **Deprecated** — legacy pattern |
| **FacetClaim** | **0** | CLAIM_ID_ARCHITECTURE | **Planned** — Claim (1) may implement; subtype pattern |
| **TemporalAnchor** | **0** | schema | **Planned** — temporal anchoring |
| **PropertyMapping** | **0** | legacy | **Superseded** — use SYS_PropertyMapping (500) |
| **PropertyType** | **0** | schema | **Planned** — property typing |
| **PlaceVersion** | **0** | ARCHITECTURE_ONTOLOGY §3.1.2.1 | **Planned** — time-scoped place instantiations |

---

## Relationship Types (Top 50 by count)

| Type                               |  Count | Creating Script(s)                                                                                        |
| ---------------------------------- | -----: | --------------------------------------------------------------------------------------------------------- |
| ALIGNED_WITH_GEO_BACKBONE          | 32,480 | `link_pleiades_place_to_geo_backbone.py`                                                                  |
| ACTIVE_IN_YEAR                     | 18,217 | `migration_position_active_in_year.cypher`                                                                |
| POSITION_HELD                      |  7,342 | `dprr_import.py`                                                                                          |
| CITIZEN_OF                         |  5,243 | `promote_p27_to_citizen_of.py`, `apply_polity_amendment_migration.py`                                     |
| MEMBER_OF_GENS                     |  4,840 | `create_onomastic_nodes.py`                                                                               |
| HAS_NOMEN                          |  4,619 | `create_onomastic_nodes.py`                                                                               |
| BROADER_THAN                       |  4,154 | `load_lcc_nodes.py`, `load_subject_concepts_qid_canonical.py`                                             |
| FOLLOWED_BY                        |  4,152 | `genYearsToNeo.py`, `05_temporal_hierarchy_levels.cypher`                                                 |
| HAS_COGNOMEN                       |  3,882 | `create_onomastic_nodes.py`                                                                               |
| HAS_PRAENOMEN                      |  3,670 | `create_onomastic_nodes.py`                                                                               |
| DESCRIBED_BY_SOURCE                |  3,630 | `import_relationships_comprehensive.py` (P1343)                                                           |
| BIO_CANDIDATE_REL                  |  3,472 | `biographic/agent.py`                                                                                     |
| LOCATED_IN                         |  3,380 | `link_place_admin_hierarchy.py`, `build_wikidata_period_geo_backbone.py`, `enrich_periods_multi_facet.py` |
| CHILD_OF                           |  2,711 | `person_harvest/executor.py`, `dprr_import.py`                                                            |
| SIBLING_OF                         |  2,162 | `person_harvest/executor.py`, `dprr_import.py`                                                            |
| INSTANCE_OF                        |  2,122 | `import_relationships_comprehensive.py` (P31)                                                             |
| FATHER_OF                          |  2,122 | `person_harvest/executor.py`, `dprr_import.py`                                                            |
| HAS_STATUS                         |  1,919 | `dprr_import.py`                                                                                          |
| DIPLOMATIC_RELATION                |  1,726 | `import_relationships_comprehensive.py` (P530)                                                            |
| CONTAINS                           |  1,526 | migrations (PRH, Fischer, etc.)                                                                           |
| BORDERS                            |  1,223 | `import_relationships_comprehensive.py` (P47)                                                             |
| CONTROLLED_BY                      |  1,191 | `import_relationships_comprehensive.py` (P17)                                                             |
| BORN_IN_YEAR                       |  1,117 | `biographic/agent.py`, `person_harvest/executor.py`                                                       |
| BORN_IN_PLACE                      |  1,105 | `biographic/agent.py`                                                                                     |
| DISCIPLINE_SUBCLASS_OF             |    998 | `load_discipline_taxonomy.py`                                                                             |
| DIED_IN_YEAR                       |    949 | `biographic/agent.py`, `person_harvest/executor.py`                                                       |
| DISCIPLINE_BROADER_THAN            |    726 | `load_discipline_taxonomy.py`                                                                             |
| LOCATED_IN_TIMEZONE                |    640 | `import_relationships_comprehensive.py` (P421)                                                            |
| SPOUSE_OF                          |    625 | `person_harvest/executor.py`, `dprr_import.py`                                                            |
| MOTHER_OF                          |    589 | `person_harvest/executor.py`, `dprr_import.py`                                                            |
| HAS_PRIMARY_FACET                  |    500 | `import_property_mappings_direct.py`                                                                      |
| SUB_PERIOD_OF                      |    490 | `import_relationships_comprehensive.py` (P361)                                                            |
| DIFFERENT_FROM                     |    481 | `import_relationships_comprehensive.py` (P1889)                                                           |
| GENDER                             |    436 | `import_relationships_comprehensive.py` (P21)                                                             |
| CONTAINS_PERIOD                    |    435 | `import_relationships_comprehensive.py` (P527)                                                            |
| DIED_IN                            |    408 | `promote_p19_p20_to_canonical.py`                                                                         |
| MEMBER_OF                          |    396 | `import_relationships_comprehensive.py` (P463), `cluster_assignment.py`                                   |
| DISCIPLINE_HAS_PART                |    372 | `load_discipline_taxonomy.py`                                                                             |
| TYPE_OF                            |    361 | `import_relationships_comprehensive.py` (P279)                                                            |
| MEMBER_OF_TRIBE                    |    353 | `create_onomastic_nodes.py`                                                                               |
| ADMINISTRATIVE_PART_OF             |    353 | `import_relationships_comprehensive.py` (P150)                                                            |
| COLLABORATOR_OF                    |    330 | `import_relationships_comprehensive.py` (P767)                                                            |
| MAINTAINED_BY_WIKIPROJECT          |    312 | `import_relationships_comprehensive.py`                                                                   |
| LOCATED_IN_CONTINENT               |    278 | `import_relationships_comprehensive.py` (P30)                                                             |
| DISCIPLINE_PART_OF                 |    263 | `load_discipline_taxonomy.py`                                                                             |
| SPOKE_LANGUAGE                     |    248 | `import_relationships_comprehensive.py` (P1412)                                                           |
| ON_FOCUS_LIST_OF_WIKIMEDIA_PROJECT |    228 | `import_relationships_comprehensive.py` (P5008)                                                           |
| BORN_IN                            |    200 | `promote_p19_p20_to_canonical.py`                                                                         |
| HAS_SECONDARY_FACET                |    195 | `import_property_mappings_direct.py`                                                                      |
| DIED_IN_PLACE                      |    185 | `biographic/agent.py`                                                                                     |

*Full list of 217 relationship types in `output/census.json`.*

---

## Sanity Check: Architecture vs Graph

Cross-reference with `Key Files/ARCHITECTURE_CORE.md`, `Key Files/ARCHITECTURE_ONTOLOGY.md`, `Key Files/Main nodes.md`, and `Key Files/Appendices/` (see index at `Appendices/README.md`).

### Canonical first-class nodes (ARCHITECTURE_ONTOLOGY §3.0.1)

| Architecture label | Graph count | Status |
|-------------------|------------:|--------|
| SubjectConcept | 30 | ✓ Implemented |
| Human | 0 | Planned — Person (5,248) used; architecture says Person→Human |
| Gens, Praenomen, Cognomen | 585 / 24 / 1,000 | ✓ Implemented |
| Event | 45 | ✓ Implemented |
| Place | 44,040 | ✓ Implemented |
| Period | 0 | Planned — Periodo_Period (1,118) exists |
| Dynasty | 0 | Planned |
| Institution | 0 | Planned |
| LegalRestriction | 0 | Planned |
| Claim | 1 | ✓ Implemented |
| Organization | 0 | Planned |
| Year | 4,030 | ✓ Implemented |
| Work | 0 | Planned — WorldCat_Work (196) is federation layer |
| Material | 0 | Planned |
| Object | 0 | Planned |
| ConditionState | — | Not in census; check schema |

### W5H1 framework (ARCHITECTURE_CORE §2.2)

- **Who:** Human (0), Organization (0), Dynasty (0) — all planned
- **What:** Event (45), Object (0), Work (0) — Event done; Object/Work planned
- **When:** Year (4,030), Period (0) — Year done; Period planned
- **Where:** Place (44,040) — done

### Deprecated / superseded

- **Activity** (0) — Deprecated; route to Event or SubjectConcept
- **FacetedEntity** (0) — Deprecated legacy pattern
- **PropertyMapping** (0) — Superseded by SYS_PropertyMapping (500)
- **Person vs Human** — Architecture: Person is legacy wording, MUST map to Human. Graph uses Person; Human migration pending.

### Implementation vs architecture mismatches

- **Position** (171) — Architecture deprecates Position (merge into Institution or Event); graph still has Position from DPRR
- **EntityType** (17) vs **SYS_NodeType** (43) — Both exist; architecture prefers SYS_NodeType
- **Facet** (18) vs **FacetCategory** (0) — Facet implemented; FacetCategory (parent of Facet) planned

### Script provenance

Consider adding `source` or `imported_at` to import scripts for traceability.

---

## Regeneration

```bash
python -m scripts.tools.graph_census --json -o output/census.json
```

Then update this document or run a script to regenerate the table from census + grep.
