# Harvester Scoping Design: Temporal vs Conceptual Entities

**Architectural context:** See [FEDERATION_ARCHITECTURE.md](FEDERATION_ARCHITECTURE.md) for the two-phase model (federation as gate first, federation as source second). This doc covers Phase 1 scoping; Phase 2 is federation interrogation for enrichment.

## Problem

The Q7188 (Government) cluster at 982 entities is noise-dominated. Generic property matching (P39 office held, P31 instance of political entity) pulls in entities with no Roman Republic connection. Temporal scoping was considered as a filter — but it would exclude exactly the wrong entities.

**Concepts like *imperium*, *mos maiorum*, the Senate as an institution** don't have birth and death dates. They are persistent, trans-temporal. Same for legal concepts (*provocatio*, *tribunicia potestas*), social structures (patron-client), geographic entities (Rome, Mediterranean). These are atemporal or trans-temporal in Wikidata terms but are core Roman Republic content.

Temporal scoping would incorrectly exclude the most conceptually central entities. The right filter is **domain specificity**, not "when does this entity exist."

## Two Entity Classes, Two Scoping Rules

| Entity class | Examples | Scoping rule |
|--------------|----------|--------------|
| **Temporal** | Persons, battles, laws, offices | Federation IDs (Trismegistos, LGPN, Pleiades) or date/period. No date parsing needed when federation IDs present. |
| **Conceptual** | Institutions, structures, legal concepts, geographic entities | Domain graph proximity only. No temporal constraint. Exempt from date filtering. |

**Schema note:** Place is Conceptual (not Temporal) — Rome as a city, the Forum Romanum, Roman roads don't have death dates. Organization is Conceptual — the Roman Senate as an institution existed across the entire Republican period and into the Empire with no clean temporal boundary. The schema captures these decisions explicitly.

## Federation-Aware Scoping (Primary Mechanism)

The federations are the right mechanism. External IDs already exist in the harvester output; the scoping logic reads from `entity.external_ids`.

| Federation | Property | Signal |
|------------|----------|--------|
| **Trismegistos** | P1696 | Ancient person/place. Temporal-geographic scoping by authority identity, not date parsing. |
| **LGPN** | P1047 | Ancient person. Same logic. |
| **Pleiades** | P1584 | Ancient place. Same logic. |
| **VIAF** | P214 | Person or work. With domain graph proximity → modern scholarly identity for ancient entity. |
| **Getty AAT** | (future) | Material culture, conceptual entities. Signals "apply domain proximity scoping, not temporal." |

**Prerequisite:** Every accepted entity must have its `external_ids` dict populated. The external_ids patch is the prerequisite for federation-aware scoping.

### Scoping Rule (Pseudocode)

```python
def scoping_rule(entity):
    ext = entity.external_ids

    if ext.get("P1696") or ext.get("P1047") or ext.get("P1584"):
        # Ancient world confirmed by prosopographic/geographic authority
        return "temporal_scoped", confidence=0.95

    if ext.get("P214") and any_subject_concept_proximity(entity):
        # VIAF entity with domain graph connection
        return "domain_scoped", confidence=0.85

    if not ext:
        # No external authority corroboration
        return "unscoped", confidence=0.40
```

**Unscoped entities** are the noise candidates in Q7188 — not because they lack dates, but because no external authority has claimed them as belonging to any recognized domain. That's a principled filter.

## Ambiguous or Unknown Category

When an entity's P31 doesn't map to a schema category, it falls through both scoping rules. **Default: `unscoped` with low confidence (0.40).** Eligible for cluster assignment but flagged for review. Otherwise ambiguous entities silently get full confidence.

## Domain Specificity (Conceptual Entities)

An entity is domain-scoped if it has **Q17167 (Roman Republic) or its SubjectConcept neighborhood** anywhere in its claim set — as subject, context, part-of, related-to.

Conceptual entities (institutions, legal concepts, social structures) require domain graph proximity. BROADER_THAN and MEMBER_OF edges in Neo4j already support this; no new federation work needed.

## Implementation: Harvester Gate (Not Post-Hoc Filter)

The fix belongs at **harvest time**, not downstream. MEMBER_OF edges were supposed to guarantee domain-scoped entities only. The noise in Q7188 is a harvester scoping problem that propagated forward.

### Gate Logic

1. **Populate external_ids** — Every accepted entity has `external_ids` from harvest (already in place).

2. **Apply federation-aware scoping** — Trismegistos/LGPN/Pleiades → temporal_scoped; VIAF + domain proximity → domain_scoped; no federation IDs → unscoped.

3. **Temporal entities** (Person, Event, Agreement, Position): Federation IDs handle persons and places. For events/laws/offices without federation IDs, fall back to date/period check if needed.

4. **Conceptual entities** (Organization, Place, Infrastructure, Material, Concept, Religious): Require domain graph proximity. Exempt from temporal constraint.

5. **Ambiguous category:** Default to unscoped, low confidence, flagged for review.

### Schema Reference

`JSON/chrystallum_schema.json` under `entity_scoping`:

- `category_to_scoping_class`: Maps entity category → `"temporal"` or `"conceptual"`.
- `scoping_classes`: Describes each class and its rules.

### Getty AAT (Future)

When integrated, Getty AAT ID on an entity signals material culture or conceptual entity — apply domain proximity scoping, not temporal. Not blocking the core scoping logic.

## Current State vs Target (Implementation Roadmap)

| Aspect | Current | Target |
|--------|---------|--------|
| Class allowlist | Disabled in discovery mode | Re-enable with scoping-class-aware logic |
| Federation scoping | None | Trismegistos/LGPN/Pleiades → temporal_scoped; VIAF + proximity → domain_scoped |
| Unscoped default | Accept with full confidence | Unscoped, confidence=0.40, flagged for review |
| Domain proximity | None | Gate for conceptual entities |
| Conceptual exemption | N/A | Explicit: no temporal constraint for conceptual |

**Three discrete additions** to the harvester, implementable independently: (1) federation-aware scoping, (2) unscoped default for ambiguous entities, (3) domain proximity gate for conceptual entities.

## Two Failure Modes (from Scoping Advisor Report)

The 87% unscoped figure reveals two structurally different failure modes that need different solutions:

**Failure mode 1 — Named entity clusters with no federation IDs:** Q899409 Families, Q7188 Government, Q2277 Transition to Empire — these contain real domain-relevant persons, gentes, magistrates. They fail scoping because the harvester didn't reach Trismegistos/LGPN/Pleiades records for them. **Fix:** Targeted re-harvest following the property chains that worked for Q182547 (Pleiades) and Q337547 (VIAF). Apply the same approach to persons in Q899409 via LGPN.

**Failure mode 2 — Conceptual entity clusters:** Q211364 Popular offices, Q39686 Cursus Honorum, Q952064 Markets — these contain Wikidata items for *concepts* (the office of Tribune, the institution of the cursus honorum) rather than *instances* (specific tribunes, specific market transactions). Federation IDs will never fire on these because they are not persons or places. **Fix:** Domain graph proximity scoping (entity_scoping in schema). The harvester must apply that rule for conceptual entities.

**Template for scoped re-harvest:** The trustworthy clusters (Q182547, Q337547, Q1541, Q726929) share a common pattern: named individuals or geographic places with Pleiades IDs or VIAF records. Trace the property chains that brought Pleiades and VIAF into those clusters and replicate deliberately across person-heavy clusters.

## Property Chain Trace (2026-02-24)

**Q182547 (Provinces):** P31 brings 79 temporal_scoped (all Pleiades P1584). Replicate P31-heavy harvest for geographic clusters.

**Q337547 (Public ritual):** P140 (religious affiliation) brings 86 scoped (P214 VIAF); P101 brings 22 domain_scoped. Conceptual clusters benefit from P140, P101, P361.

**Q899409 (Families/Gentes):** 0 temporal_scoped, 18 domain_scoped (all via P214 VIAF). No P1047 (LGPN) entities in current backlink harvest. LGPN expansion requires forward SPARQL: entities with P1047 AND domain relevance (e.g. P31/P279* Q899409 or Roman Republic context).

See `output/analysis/property_chain_trace.md` (generated by `scripts/analysis/trace_property_chains.py`).

---

## Relation to Other Docs

- **FEDERATION_ARCHITECTURE.md** — Two-phase model; Phase 1 (this doc) must not close off Phase 2 (federation interrogation). Persist external_ids on Entity nodes.
- **PIPELINE_READ_BACK_PRINCIPLE.md** — Harvester should read existing entity set from Neo4j before writing; scoping gate applies to new candidates.
- **BACKLINK_QID_VERIFICATION_ALGORITHM.md** — Anchor QID verification is a separate gate; scoping applies after anchor correctness.
- **chrystallum_schema.json** — `entity_scoping` section defines the category → scoping_class mapping.
- **Prosopographic scripts** — Trismegistos, LGPN, Pleiades already crosswalked; federation layer partially in place.
