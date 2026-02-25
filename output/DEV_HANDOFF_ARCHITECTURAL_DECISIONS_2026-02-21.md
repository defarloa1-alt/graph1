# Dev Handoff — Architectural Decisions (2026-02-21)

**Context:** Node label audit surfaced items requiring architectural decisions before further schema work. Architect has responded. This document captures the message to dev, investigation findings, and dependency check results.

---

## Message to Dev (Updated 2026-02-21)

### Delete immediately (D-027)

**Labels:** FacetedEntity (360), PeriodCandidate (1,077), PlaceTypeTokenMap (212), GeoCoverageCandidate (357), **StatusType (2)**.

**Action:** Run `scripts/neo4j/delete_staging_nodes_d027.cypher`. Execute each statement separately. Report counts confirmed deleted.

**Logged:** DECISIONS.md D-027.

---

### Investigate before ruling — five unclear labels

Run these queries before any action on these labels:

```cypher
MATCH (n:Activity) RETURN count(n) AS cnt, collect(n.name)[0..5] AS samples
MATCH (n:Location) RETURN count(n) AS cnt, collect(n.name)[0..5] AS samples
MATCH (n:PropertyType) RETURN count(n) AS cnt, collect(n.name)[0..5] AS samples
MATCH (n:Schema) RETURN count(n) AS cnt, collect(n.name)[0..5] AS samples
MATCH (n:StatusType) RETURN count(n) AS cnt, collect(n.name)[0..5] AS samples
```

**Investigation results (pre-run):**

| Label | Count | Samples | Notes |
|-------|-------|---------|-------|
| Activity | 0 | [] | No standalone nodes; may be secondary label |
| Location | 0 | [] | No standalone nodes |
| PropertyType | 0 | [] | No standalone nodes |
| Schema | 9 | — | Entity schema definitions (uses_federations, required_props, optional_props) |
| StatusType | 2 | — | Orphaned enumeration stubs — **add to delete list** |

---

### Do not touch — reclassification (D-029)

**Schema (9), PropertyMapping (706), Policy (5), Threshold (3), KnowledgeDomain (1)** — all being reclassified into Metanode, not deleted. See D-029.

---

### PropertyMapping (706 nodes) — DMN data substrate

**Query run:**
```cypher
MATCH (pm:PropertyMapping)-[:HAS_PRIMARY_FACET]->(f:Facet)
RETURN pm.property_id, pm.property_label, f.key LIMIT 20
```

**Findings:** PropertyMapping uses `property_id` (not `pid`), `property_label`, `primary_facet`. Sample:

| property_id | property_label | facet |
|-------------|---------------|-------|
| P186 | made from material | ARCHAEOLOGICAL |
| P547 | commemorates | ARCHAEOLOGICAL |
| P344 | director of photography | ARTISTIC |
| P347 | Joconde work ID | ARTISTIC |
| P180 | depicts | ARTISTIC |
| ... | ... | ... |

**Architect note (D-029):** These *are* the data substrate for DMN HarvestAllowlistService and EdgeBuilder canonical mapping. Migrate to SYS_PropertyMapping. Add `system: true`. Do not rename yet — confirm migration approach first.

---

### KnowledgeDomain (61 edges) — do not delete, do not wire yet

**Structure:** 1 KnowledgeDomain node. 61 SubjectConcepts have `DOMAIN_OF` → KnowledgeDomain.

**KnowledgeDomain node:** `{label: "Roman Republic", qid: "Q17167"}` — root of SubjectConcept hierarchy.

**Direction:** SubjectConcept -[:DOMAIN_OF]-> KnowledgeDomain (not reversed). So each of the 61 SubjectConcepts is "domain of" the single Roman Republic KnowledgeDomain.

**Sample SubjectConcepts:** Marriage alliances and political kinship, Institutions: Senate, Assemblies, Magistracies, Trade routes and maritime networks, Landholding Agriculture and Estates, Culture Ideas and Communication, etc.

**Architect note (D-029):** Single root anchor for 61 SubjectConcepts. Absorb into SYS_SchemaRegistry as SYS_SubjectConceptRoot. Remove KnowledgeDomain label, add SYS_SubjectConceptRoot, `system: true`.

---

### Policy and Threshold nodes — high priority for DMN

**Policy (5 nodes):**

| name | description | priority |
|------|-------------|----------|
| LocalFirstCanonicalAuthorities | Always check local authorities before hub API | 1 |
| HubForDisambiguationOnly | Use Wikidata for discovery/disambiguation, not as primary source | 2 |
| NoTemporalFacet | TEMPORAL is NOT a facet — use Year backbone, Period, Event | 3 |
| NoClassificationFacet | CLASSIFICATION via LCC properties, not facet | 4 |
| ApprovalRequired | All discoveries require human approval before promotion | 5 |

**Threshold (3 nodes):**

| name | description | value |
|------|-------------|-------|
| crosslink_ratio_split | Split SFA when cross-link ratio exceeds 30% | 0.3 |
| level2_child_overload | Split when L2 node has >12 children | 12 |
| facet_drift_alert | Alert when 20%+ concepts have LCSH mismatched to facet | 0.2 |

**Architect note (D-029):** Evidence of prior rule externalisation. Migrate to SYS_Policy and SYS_Threshold. Add `system: true`. DMN tables will read these. Do not modify values yet.

---

### Schema nodes (9) — full properties

| # | uses_federations | required_props | optional_props |
|---|------------------|----------------|----------------|
| 1 | [] | year, label, entity_id | — |
| 2 | Pleiades, Wikidata, GeoNames | place_id, pleiades_id | qid, lat, long, bbox |
| 3 | PeriodO, Wikidata | period_id, start_year, end_year | qid, periodo_id |
| 4 | Wikidata, VIAF | — | — |
| 5 | Wikidata | — | — |
| 6 | Wikidata | — | — |
| 7 | LCSH, FAST, LCC, Wikidata | — | — |
| 8 | WorldCat, Wikidata | — | — |
| 9 | [] | — | — |

**Action:** Report full properties before any action. Keep; investigate what they define.

---

### Subject vs SubjectConcept — architectural decision confirmed

**Before Library Authority Step 1:**

- **Subject** = library classification (LCSH/FAST). Controlled vocabulary, lcsh_id/fast_id, BROADER_THAN hierarchy. Maintained by LibraryAuthoritySubsystem.
- **SubjectConcept** = interpretive anchor. Thematic domain for SCA/SFA, narrative paths, facet assignments. Maintained by agent layer.

**Relationship:** Subject CLASSIFIES SubjectConcept (proposed edge type). One informs the other; neither replaces the other. Do not merge, do not conflate.

**Library Authority Step 1** can proceed once investigation results above are reviewed. Subject node design is clear.

---

## Dependency Check Results (grep across scripts)

### Policy (5 nodes)
- **Created by:** `scripts/backbone/load_federation_metadata.py` (lines 126–161). Links FederationRoot -[:HAS_POLICY]-> Policy.
- **Read by:** None. No operational script queries Policy nodes for decision logic. Orphaned from governance.

### Threshold (3 nodes)
- **Created by:** `scripts/backbone/load_federation_metadata.py` (lines 164–184). Links FederationRoot -[:HAS_THRESHOLD]-> Threshold.
- **Read by:** None. No operational script queries Threshold nodes. Values (0.3, 12, 0.2) are hardcoded elsewhere.

### PropertyMapping (706 nodes)
- **Created by:** `import_property_mappings_direct.py`, `convert_csv_to_cypher.py`, `output/neo4j/import_property_mappings.cypher`
- **Read by:** `verify_property_mappings.py`, `verify_property_import.py`, `check_property_facet_links.py` (verification/audit only). **Not read by** cluster_assignment, harvester, or EdgeBuilder for operational PID→facet decisions. Pipeline gets facet from other sources (CSV, backlinks report, hardcoded).

### KnowledgeDomain (1 node)
- **Created by:** `output/neo4j/load_subject_concepts_qid_canonical.cypher` — heavily used as structural anchor (61 SubjectConcepts -[:DOMAIN_OF]-> KnowledgeDomain).

**Conclusion:** Policy and Threshold are fully disconnected. PropertyMapping is stored but not used by pipeline for decisions. Safe to migrate — no live dependencies to break.

---

## Summary for Dev

| Task | Status |
|------|--------|
| Delete staging (D-027) | Run script; includes StatusType (2). Report counts |
| Unclear labels | Activity/Location/PropertyType = 0; Schema (9) keep, investigate |
| PropertyMapping | D-029: migrate to SYS_PropertyMapping; no pipeline reads it |
| KnowledgeDomain | D-029: absorb as SYS_SubjectConceptRoot |
| Policy/Threshold | D-029: migrate to SYS_Policy, SYS_Threshold; no script reads them |
| Subject vs SubjectConcept | D-028: confirmed distinct |
| Dependency check | Complete — no migration blockers |

---

## Architect Message (2026-02-21) — Inventory Confirmed

**Schema node properties:** See `output/SCHEMA_NODES_FULL_PROPERTIES.md` — 9 nodes, full JSON for architect ruling.

**Implementation:** Add properties to Policy/Threshold, then relabel. Script: `scripts/neo4j/add_sys_properties_and_relabel_d029.cypher`

**decision_table mappings:**
- LocalFirstCanonicalAuthorities → D4_DETERMINE_federation_route
- HubForDisambiguationOnly → D5_DETERMINE_federation_scope_match
- NoTemporalFacet, NoClassificationFacet → D8_DETERMINE_SFA_facet_assignment
- ApprovalRequired → D10_DETERMINE_claim_promotion_eligibility
- crosslink_ratio_split, level2_child_overload → D12_DETERMINE_SubjectConcept_split_trigger
- facet_drift_alert → D13_DETERMINE_SFA_drift_alert

**D12 and D13** added to DMN inventory — new standalone tables.

**Do not delete** FederationRoot -[:HAS_POLICY]-> edges — understand FederationRoot before removing.

---

## Schema Node Rulings (2026-02-21) — Run BEFORE D-029

**Script:** `scripts/neo4j/schema_node_actions_pre_d029.cypher`

**Delete:** Schema 3 (Period, D-012 stale), Schema 9 (empty), one of Schema 5/6 (duplicates — investigation confirmed identical).

**Update:** Schema 8: `uses_federations` WorldCat → LC_SRU.

**Flag:** Schema 4 (Human): add `status: "incomplete — required_props missing"`, `system: true`.

**Schema nodes are NOT part of D-029 relabeling.** They migrate to SYS_PropertyDefinition in SchemaRegistry build. Add `system: true` only; leave Schema label in place.

**Report** Schema 5/6 investigation (done: duplicates, delete one) and confirm deletes/updates before running D-029 relabeling.
