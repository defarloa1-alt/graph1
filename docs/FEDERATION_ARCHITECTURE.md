# Federation Architecture: Gate First, Source Second

**Status:** Architectural decision — add before Phase 1 implementation  
**Related:** HARVESTER_SCOPING_DESIGN.md, entity_scoping in chrystallum_schema.json

---

## The Shift

**Current model:** Federation IDs as **filter** — validate that a Wikidata entity is genuinely domain-relevant.

```
Wikidata → harvest entities → assign to SubjectConcepts → check federation IDs for scoping
```

**Target model:** Federation as **source of enrichment**, not just validation gate.

```
Wikidata → harvest entities → federation IDs found → GO TO federation →
interrogate federation for what Wikidata doesn't have → bring that back into graph
```

This reorders the pipeline. Scoping (Phase 1) is the prerequisite; federation interrogation (Phase 2) is where the prosopographic richness enters.

---

## What Each Source Provides

| Wikidata | Federations (Trismegistos, LGPN, Pleiades) |
|----------|--------------------------------------------|
| Broad connectivity, relationships to other entities | Primary source citations (papyri, inscriptions) |
| Modern scholarly consensus on identity | Attestation records — every time a person appears in a source |
| Machine-readable properties at scale | Variant name forms across languages and scripts |
| Ontological classification | Social network data — family connections, career reconstructions, freedmen lists |
| | Geographic precision — coordinates, period-specific names, feature types |
| | Uncertainty metadata — when dates are approximate, when identity is contested |

**Example (Q899409 Families/Gentes):** LGPN doesn't just confirm a person is Greek — it gives attestation geography, onomastic family, social status indicators, date range of name usage. Richer prosopographic data than Wikidata carries for most individuals.

---

## Two-Phase Model

### Phase 1: Federation as Gate

**Goal:** Get federation IDs into the graph reliably. Use them for scoping (validation).

**Current harvester:**
```
find entity → check if P1696/P1047/P1584 present → if yes, mark scoped
```

**Phase 1 deliverables:**
- Trace property chains that bring Pleiades/VIAF into trustworthy clusters (Q182547, Q337547)
- Replicate across person-heavy clusters (Q899409 via LGPN)
- Domain proximity gate for conceptual entities
- Scoping status on MEMBER_OF edges

**Design constraint for Phase 1:** Do not build in a way that closes off Phase 2.

| Requirement | Rationale |
|-------------|-----------|
| Persist federation IDs on **Entity nodes** (not just edges) | Phase 2 must query "which entities have P1838?" to interrogate LGPN |
| Store `external_ids` dict on Entity | Enables federation API lookup by PID + value |
| Plan for provenance from the start | Phase 2 writes `source: trismegistos` vs `source: wikidata` |

**Phase 1 implementation anti-patterns to avoid:**

1. **Do not write federation data as metadata fields on entity nodes.** Write as graph claims with PROV-O provenance. The difference matters for Phase 2 queryability:
   ```
   # Wrong — closes off Phase 2:
   entity.trismegistos_name = "Aurelius Sarapion"
   entity.trismegistos_dates = "II AD"

   # Right — enables Phase 2:
   (e:Entity)-[:HAS_ATTESTATION {source: "trismegistos", text_id: "TM12345",
     date: "II AD", confidence: 0.95}]->(a:Attestation)
   ```

2. **Keep the federation fetch function separate from the scoping gate.** The gate reads `external_ids` already on the entity node. The federation fetch is a separate call that can be triggered independently. Don't couple them — Phase 2 runs as a separate enrichment pass, not inline with harvesting.

3. **Log federation fetches for idempotency.** Phase 2 enrichment must know what has already been interrogated to avoid redundant API calls on re-runs. A `federation_fetch_log` property on the entity or a separate log node is sufficient.

### Phase 2: Federation as Source

**Goal:** Interrogate federation APIs. Pull attestations, social connections, geographic precision into the graph.

**Enriched flow:**
```
find entity → P1696 present → fetch Trismegistos record → extract attestations,
  dates, social connections not in Wikidata → write to graph with source: trismegistos
find entity → P1047 present → fetch LGPN record → extract onomastic family,
  geographic distribution, social status → write to graph with source: lgpn
find entity → P1584 present → fetch Pleiades record → extract coordinates,
  period-specific names, connected places → write to graph with source: pleiades
```

**Phase 2 deliverables:**
- Trismegistos API client → attestation nodes, date ranges
- LGPN API client → onomastic family, geographic distribution, social status
- Pleiades API client → coordinates, period-specific names, feature types
- PROV-O or equivalent attribution on all federation-sourced claims

### Phase 3: SFA over Enriched Graph

**Goal:** SFA reasons over entity layer that has both Wikidata's ontological breadth AND federations' primary source depth.

Qualitatively different from reasoning over Wikidata alone — the narrative layer can cite attestations, social networks, geographic precision.

---

## SubjectConcepts as Multi-Source Landing Zones

Some SubjectConcepts will be populated primarily from federation data rather than Wikidata.

**Q899409 (Families/Gentes):** LGPN's onomastic and prosopographic records are more authoritative for that cluster than anything Wikidata carries.

**Implication:** SubjectConcept becomes a landing zone that aggregates across multiple sources, with provenance tracking which claims came from where.

---

## Implementation Order

1. **Phase 1** — Trace property chains, domain proximity gate, LGPN expansion. Persist `external_ids` on Entity nodes. Scoping on MEMBER_OF.
2. **Phase 2** — Federation interrogation clients. Enrichment writes with `source` attribution.
3. **Phase 3** — SFA consumes enriched graph.

Phase 1 fixes the scoping problem. Phase 2 is where the prosopographic richness enters. Phase 3 is the payoff.

---

## Relation to Other Docs

- **HARVESTER_SCOPING_DESIGN.md** — Phase 1 scoping rules, two failure modes
- **chrystallum_schema.json** — entity_scoping, category_to_scoping_class
- **PIPELINE_READ_BACK_PRINCIPLE.md** — Graph as source of truth; enrichment reads before writing
