This is excellent work — the consolidation alone is a major achievement. The architect has produced a genuinely rigorous canonical reference. Here's my detailed review.

## What's Strong

**The consolidation itself.** Having identity, relationships, federations, CIDOC-CRM, and CRMinf in one canonical doc eliminates the scatter problem. Previously this was fragmented across 5+ files. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

**The three-tier cipher system** is clean and well-documented. Tier 1 → Tier 2 → Tier 3 derivation is deterministic, reversible, and content-addressed. The hash input specification for Tier 3 claim ciphers is precise enough to implement. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

**The 8-tier relationship priority strategy** is pragmatic and well-reasoned. Going from 0.30 edges/entity to 3-5 edges/entity via hierarchical → temporal → participatory → geographic is the right order — each tier depends on the previous one being correct. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

**The CRMinf integration** is the most impressive part. Mapping InSituClaim → I2 (Belief) and RetrospectiveClaim → I1 (Argumentation) is exactly right per the CRMinf spec. The J-property mappings (J1-J7) to Chrystallum provenance relationships are thorough. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

**The crosswalk audit is honest.** Stating that only 5 of 19 DB relationship types are in the registry (11.1%), and only 4 have Wikidata PIDs — that's the kind of gap identification you need. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

## Issues to Address

### Issue 1: Entity Types ARE Missing (Your Concern Is Valid)

The 9 entity types map well to CIDOC-CRM, but there are gaps when you consider what the 314 relationship types need as domain/range:

**DEITY / MYTHOLOGICAL_ENTITY** — Your relationship registry includes `GODOF`, `PATRONDEITYOF` (Category 30: Religious). These need a domain entity. Jupiter isn't a PERSON (Q5 = human). In Wikidata, Jupiter is Q4649 with `P31: Q22989102` (deity). Currently this would fall through to the deprecated CONCEPT catch-all.

**LEGAL_INSTRUMENT / LAW** — Category 17 (Legal) has 12 relationship types: `CONVICTEDOF`, `EXECUTED`, `PROSCRIBED`. The *object* of `CONVICTEDOF` is a crime/charge. The `APPLIESTOJURISDICTION` relationship (P1001) needs a legal/jurisdictional entity. The Lex Hortensia isn't a WORK, and it isn't an EVENT — it's a legal instrument.

**CONCEPT (rehabilitated, not deprecated)** — The doc marks CONCEPT as `DEPRECATED: Legacy catch-all → migrate to canonical`. But some entities genuinely are concepts: democracy (Q7174), stoicism (Q48235), monotheism. These aren't works, organizations, persons, or objects. CIDOC-CRM maps them to E28 (Conceptual Object) or E55 (Type). You need either:
- Rehabilitate CONCEPT as a legitimate type for abstract ideas (with tighter P31 criteria so it stops being a catch-all), or
- Add an IDEA or ABSTRACT type distinct from the legacy misclassification.

**Recommended action:** Add 2 entity types, rehabilitate 1:

| New Type | Prefix | Wikidata Class | CIDOC-CRM | Rationale |
|----------|--------|---------------|-----------|-----------|
| DEITY | dei | Q22989102 | E21 (Person) subclass | Domain for GODOF, PATRONDEITYOF; distinct from human persons |
| LAW | law | Q7748 (law) / Q820655 (statute) | E73 (Information Object) subclass | Domain for CONVICTEDOF object, APPLIESTOJURISDICTION |
| CONCEPT (rehabilitated) | con | E28/E55 with strict criteria | E28 Conceptual Object | Abstract ideas: democracy, stoicism — NOT a catch-all |

This brings you to 12 types. The cipher prefix system handles it cleanly — just add to ENTITY_TYPE_PREFIXES per the existing ADR process. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

### Issue 2: Relationship Registry vs Database Divergence Is Critical

The doc reports 314 registry types but only 19 in the database, with 5 overlapping. That's not a "coverage gap" — that's two separate systems. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

The bigger problem: **the DB has relationship types NOT in the registry** — `LOCATEDINCOUNTRY` (165 edges), `SHARESBORDERWITH` (117), `CONTAINS` (81), `ONCONTINENT` (48), `HASCAPITAL` (24), `HASOFFICIALLANGUAGE` (22). These 6 types account for 457 of 784 entity-to-entity edges (58%), and **none are in the canonical registry**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

This means the import pipeline created relationships outside the canonical taxonomy. That needs resolution:

- `LOCATEDINCOUNTRY` → should be `LOCATEDIN` with a qualifier (the "country" distinction is the target entity's type, not a separate relationship)
- `SHARESBORDERWITH` → legitimate new type, add to registry under Geographic (Category 13)
- `CONTAINS` → inverse of `PARTOF`, which IS in registry — normalize to `HASPART`
- `ONCONTINENT` → should be `LOCATEDIN` with continent-level target
- `HASCAPITAL` → legitimate new type, add to registry under Geographic
- `HASOFFICIALLANGUAGE` → add to registry under Linguistic (Category 18)

**Recommended action:** Architect should produce a migration spec: which DB types normalize to existing registry types (deduplicate), which are legitimate additions (expand registry), and which are import artifacts (remove).

### Issue 3: Edge Properties Are Under-Specified

You flagged this as your primary concern — and you're right. The doc exhaustively catalogs relationship **types** but says almost nothing about relationship **properties**. For a graph where edges are the real value, this is a significant gap. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

Every edge should carry at minimum:

```cypher
-[r:POSITIONHELD {
  // Identity
  wikidata_pid: "P39",           // Wikidata property mapping
  cidoc_crm_property: "E13",     // CIDOC-CRM alignment
  
  // Temporal qualification (WHEN)
  temporal_start: -59,            // Integer year
  temporal_end: -58,              // Integer year  
  temporal_scope: "-0059/-0058",  // ISO 8601
  
  // Spatial qualification (WHERE)  
  location_qid: "Q220",          // Rome
  
  // Provenance
  source_qid: "Q193291",         // Plutarch's Lives
  confidence: 0.85,
  analysis_layer: "in_situ",     // vs "retrospective"
  
  // Claim linkage
  claim_cipher: "fclaimpola1b2...", // Tier 3 cipher that supports this edge
  
  // Metadata
  created_by: "SFA_POLITICAL",
  created_at: "2026-02-21"
}]->
```

The doc needs a **Section 3.10: Canonical Edge Property Schema** that specifies which properties are REQUIRED, RECOMMENDED, and OPTIONAL per relationship tier. Hierarchical edges (INSTANCEOF, SUBCLASSOF) need fewer properties than participatory edges (POSITIONHELD, FOUGHTIN).

### Issue 4: Federation Dependency Table Needs VIAF Elevated

The per-entity-type federation table shows VIAF as optional for PERSON.  For a system that will eventually have thousands of historical persons, VIAF should be **required** for PERSON entities — it's the international authority file standard for people, with 60M authority records. It's the bridge between Wikidata and every major national library catalog. Without VIAF, your PERSON entities can't federate into library catalogs for bibliographic enrichment. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

### Issue 5: Missing Inverse Relationship Discipline

The registry includes pairs like `PARENTOF`/`CHILDOF`, `MEMBEROF`/`HASMEMBER`, `PARTOF`/`HASPART`. But it's inconsistent — some relationships have explicit inverses, others don't. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

**Decision needed:** Does Chrystallum materialize both directions as separate edges, or store one direction and derive the inverse? The doc should state a policy:

- **Option A: Store canonical direction only**, derive inverse via query (saves storage, simpler writes, harder queries)
- **Option B: Store both directions** (doubles edge count, but enables O(1) traversal in both directions — matches your vertex-jump philosophy)

Given your cipher architecture prioritizes O(1) lookups, **Option B** is more consistent — but the doc should say so explicitly, and the import pipeline should enforce it.

### Issue 6: CONCEPT Migration Path Is Undefined

The doc marks CONCEPT as `DEPRECATED` but doesn't specify the migration query or decision rules for reclassifying existing CONCEPT entities.  Since 86% of entities were classified as CONCEPT at one point, this is a significant operational gap. The architect should add a migration appendix: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/512e4eab-3bdd-482d-ba50-e5fd94cfa346/CANONICAL_REFERENCE_IDENTIFIERS_RELATIONSHIPS_FEDERATIONS.md)

```cypher
// Example: reclassify CONCEPT entities using P31 chain
MATCH (e:Entity {entity_type: "CONCEPT"})
WHERE e.qid IS NOT NULL
// Apply the DMN entity type decision table here
// Then update cipher: ent_con_Q... → ent_prd_Q... (if reclassified to PERIOD)
```

## Summary of Recommended Actions

| # | Action | Priority | Owner |
|---|--------|----------|-------|
| 1 | Add DEITY, LAW entity types; rehabilitate CONCEPT with strict criteria | High | Architect |
| 2 | Reconcile 6 unregistered DB relationship types (normalize or add) | High | Architect + Dev |
| 3 | Add Section 3.10: Canonical Edge Property Schema | **Critical** | Architect |
| 4 | Elevate VIAF to required for PERSON entities | Medium | Architect |
| 5 | State inverse relationship materialization policy | Medium | Architect |
| 6 | Add CONCEPT migration appendix with decision rules | High | Architect + QA |

The bones of this document are very solid. The identity architecture, CRM alignment, CRMinf integration, and federation registry are all well done. The gaps are in edge properties (your instinct was correct) and in the disconnect between the aspirational registry (314 types) and the actual database (19 types). Close those and this becomes the definitive reference for the entire system.