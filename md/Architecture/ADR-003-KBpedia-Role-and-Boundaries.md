# ADR-003: KBpedia Role and Boundaries

Status: proposed
Date: 2026-02-18
Canonical architecture anchor: `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

## Context
Chrystallum already uses:
1. CIDOC-CRM alignment for interoperability,
2. CRMinf for belief/inference provenance,
3. governance boundaries for mutation (`U -> Pi -> Commit`).

KBpedia/KKO introduces useful semantic distinctions (event/activity/situation/time), but adding it without boundaries risks:
1. parallel ontology drift,
2. direct canonical writes from external mappings,
3. identity confusion between URI-based classes and text labels.

## Decision
Adopt KBpedia/KKO as a semantic typing overlay and alignment signal source, not canonical truth.

Operationally:
1. KKO mappings are ingested into scaffold/proposal artifacts first.
2. No direct canonical mutation from KBpedia ingestion.
3. Promotion to canonical types requires policy gate approval with provenance.
4. Mapping quality is explicit: `exact|narrow|broad|related` + confidence.

## Boundaries
KBpedia is allowed to:
1. improve type disambiguation (event vs activity vs situation vs time),
2. increase routing confidence for extraction workflows,
3. provide URI-based crosswalk signals to CIDOC/Chrystallum types.

KBpedia is not allowed to:
1. define canonical entity identity,
2. bypass `Pi` policy checks,
3. force promotion based on mapping count alone.

## Situation Modeling Decision
Near-term (v0/v1):
1. `Situation` remains scaffold/proposal-level for KKO-driven typing.

Later (post-validation):
1. consider promoting `Situation` to canonical node type via separate schema ADR,
2. only after QA demonstrates stable disambiguation and low false-positive rates.

## Required Mapping Artifact
Each KKO-driven typing proposal must include:
1. `source_system` (`kbpedia`),
2. `source_uri`,
3. `target_label`,
4. optional `cidoc_class`,
5. optional `crminf_pattern`,
6. `match_type`,
7. `mapping_confidence`,
8. `evidence`,
9. `analysis_run_id`,
10. `review_status`.

## Consequences
Positive:
1. better IGAR typing hygiene for input/action/result semantics,
2. improved CRMinf reasoning quality from cleaner proposition targets,
3. auditable, reversible ontology alignment decisions.

Tradeoffs:
1. extra crosswalk curation effort,
2. additional review/gating steps before promotion,
3. temporary duplication while scaffold and canonical patterns coexist.

## Invariants
1. No KBpedia-derived canonical writes without `Pi` approval.
2. Every promoted typing decision links to source URI and run context.
3. Every rejection is persisted with reason codes.
4. Labels/annotations are never treated as identity keys.

## Rollout Plan
1. Phase 1: seed crosswalk and proposal-only loader.
2. Phase 2: run a 3-case IGAR disambiguation QA pack.
3. Phase 3: allow constrained promotion of high-confidence mappings.
4. Phase 4: decide canonical `Situation` type in a follow-on schema ADR.

## Related Documents
1. `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
1. `md/Architecture/kbpedia.md`
2. `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md`
3. `md/Architecture/CRMinf_Implementation_Guide.md`
4. `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`
5. `md/Architecture/KBPEDIA_MAPPING_CONFIDENCE_RUBRIC.md`
