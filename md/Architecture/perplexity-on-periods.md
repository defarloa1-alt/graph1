Now I have the full picture from the requirements analyst's session. Here's my analysis.

## The Period Problem: Core Analysis

Your requirements analyst identified 6 challenges. They're real, but I think the analyst is treating this as primarily a **data engineering problem** (harvest, classify, load) when it's actually an **ontological design problem** that needs to be solved *before* any harvesting begins. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/edfa1bd6-ec70-432a-a5ac-5c6c8295b91a/paste.txt)

## The Fundamental Issue: Period Is Doing Too Many Jobs

The real problem isn't "which Wikidata properties define a period." It's that **"period" is overloaded** — it's simultaneously serving as:

1. **A temporal container** — "509 BCE to 27 BCE" (a span on the year backbone)
2. **An entity in its own right** — "The Roman Republic" (a thing with properties, causes, effects)
3. **A SubjectConcept** — "Roman Republic studies" (the thematic anchor for SCAs and SFAs)
4. **A geographic scope** — "the Mediterranean under Roman republican control" (shifting boundaries)
5. **A classification label** — "this artifact is from the Roman Republican period" (used by ARCHAEOLOGICAL_SFA)

Your analyst surfaced the Q17167 confusion perfectly: the Roman Republic has `P31: Q11514315` (historical period) **AND** `P31: Q41156` (polity). It has `P580/P582` **AND** `P571/P576`. Is it a period? A state? Both? The answer in Wikidata is "yes, both" — and that's what makes the harvesting decision tables fail. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/edfa1bd6-ec70-432a-a5ac-5c6c8295b91a/paste.txt)

## The Architectural Solution: Separate the Roles

Instead of trying to build one Period entity type that does everything, decompose it into what your architecture already supports:

### Role 1: Temporal Span (The Year Backbone)

This is **not an entity** — it's a **structural property** on claims and entities. You already designed this when you removed Temporal as a standalone facet. A temporal span is just:

```
temporal_scope: "-0509/-0027"  # ISO 8601 interval
```

Every claim already carries this. The year backbone is the index structure that makes temporal queries fast. No "Period node" needed for this role.

### Role 2: The Entity Itself (Polity, Regime, Era)

Q17167 (Roman Republic) is an entity — specifically, it's a **polity/state** that happens to have temporal bounds. It gets a Tier 1 cipher: `ent_org_Q17167` (as an organization/polity) and all 18 faceted ciphers. Claims attach to it as subject or object.

The entity type should be what it **is**, not that it has dates:
- Q17167 → `entity_type: ORGANIZATION` (it's a polity/state)
- Q7318 (Nazi Germany) → `entity_type: ORGANIZATION` (it's a state)
- Q12548 (Holy Roman Empire) → `entity_type: ORGANIZATION`
- Q6813 (Hellenistic period) → `entity_type: PERIOD` (it's genuinely just a time designation, not an institution)
- Q11768 (Stone Age) → `entity_type: PERIOD` (purely temporal/cultural designation)

**The DMN decision table in your requirements doc is failing because it's trying to force dual-natured entities into one type**. The answer isn't a better decision table — it's allowing the entity to be **both**, via multi-label: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/edfa1bd6-ec70-432a-a5ac-5c6c8295b91a/paste.txt)

```cypher
// Roman Republic: an organization that also defines a period
(:Entity:Organization:TemporalAnchor {
  entity_cipher: "ent_org_Q17167",
  entity_type: "ORGANIZATION",     // primary classification
  is_temporal_anchor: true,         // secondary: also defines a time span
  temporal_scope: "-0509/-0027",
  qid: "Q17167"
})

// Stone Age: purely a period designation
(:Entity:Period:TemporalAnchor {
  entity_cipher: "ent_prd_Q6813",
  entity_type: "PERIOD",           // primary: this IS a period
  is_temporal_anchor: true,
  temporal_scope: "-3300/-1200",
  qid: "Q6813"
})
```

### Role 3: SubjectConcept (Thematic Anchor)

This is already solved in your architecture. Q17167 as a SubjectConcept is independent of whether it's a "period" or "polity." The SCA for Roman Republic doesn't care — it's the thematic domain that SCAs and SFAs orbit. [perplexity](https://www.perplexity.ai/search/4dc031d1-e9cb-431f-b87b-ef60407099ba)

### Role 4: Geographic Scope

Your analyst correctly identified this as Challenge #5. The Roman Republic's geographic extent in 300 BCE ≠ 100 BCE ≠ 50 BCE. This is **not a property of the period entity** — it's a series of claims: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/edfa1bd6-ec70-432a-a5ac-5c6c8295b91a/paste.txt)

```
(Q17167)-[:HAS_GEO_COVERAGE {temporal_scope: "-0300"}]->(Q220 Rome)
(Q17167)-[:HAS_GEO_COVERAGE {temporal_scope: "-0100"}]->(Q38 Italy, Q29 Spain, Q262 Algeria...)
```

Geographic scope is temporal and faceted (GEOGRAPHIC_SFA produces these claims). It doesn't belong in the period definition.

### Role 5: Classification Label

When the ARCHAEOLOGICAL_SFA says "this amphora is from the Roman Republican period," it's using the period as a **temporal qualifier** on a claim about the amphora, not referencing a Period node. This is just `temporal_scope: "-0509/-0027"` on the claim, with an optional `[:DATED_TO]->(Q17167)` edge for the human-readable label.

## What This Means for REQ-FUNC-005

The requirements analyst's 6 challenges largely dissolve once you stop trying to build a monolithic "Period" entity type:

| Challenge | Analyst's View | Architectural Solution |
|-----------|---------------|----------------------|
| **1. Definition Ambiguity** | "Which properties = period?" | Wrong question. Ask: "Is this entity primarily temporal or primarily institutional?" Multi-label if both. |
| **2. Temporal Data Quality** | P580 vs P571, missing end dates | Normalize both to `temporal_scope` interval. Missing end = open interval, flag for review. |
| **3. Classification Complexity** | "Need Perplexity to classify period type" | You already have this — it's the 18 facets. A period doesn't have a "type." It has **facet salience** like every other entity. |
| **4. PeriodO Alignment** | Fuzzy matching, date variance | PeriodO is an authority for **temporal definitions only** (Role 1). Map `temporal_scope` to PeriodO entries. 1-year variance = automatic match. |
| **5. Geographic Scope** | "Boundaries change over time" | Not a period property — it's time-stamped GEOGRAPHIC claims produced by GEOGRAPHIC_SFA. |
| **6. Scale & Quality** | Volume management | Much simpler once you're not trying to classify everything as "period." Most "periods" are just organizations/states with temporal bounds. |

## Revised Approach

Instead of the analyst's "harvest 500-1000 periods" plan, I'd suggest:

**Phase 1: Tag existing entities as temporal anchors**
- Run through your 300 existing entities
- Any entity with both P580/P582 (or P571/P576) gets `is_temporal_anchor: true` and a normalized `temporal_scope`
- No new harvesting needed — you already have many of these

**Phase 2: Harvest genuinely pure periods**
- SPARQL for entities where `P31 = Q11514315` (historical period) and **nothing else institutional**
- These are things like "Hellenistic period," "Iron Age," "Archaic Greece" — temporal/cultural designations, not states
- ~100-200 entities, high quality, no ambiguity

**Phase 3: PeriodO alignment (temporal definitions only)**
- Match your `temporal_scope` intervals against PeriodO entries
- Fuzzy match with ±5 year tolerance
- Store `periodo_id` as an authority identifier, same as `pleiades_id`

**Phase 4: Build `BROADER_THAN` temporal nesting**
- Byzantine Empire (330-1453) `BROADER_THAN` Iconoclasm (726-843)
- This is just an edge between entities that both have `is_temporal_anchor: true`
- Cycle detection via simple depth-first check

The key insight: **you don't need a "Period Discovery" pipeline at all.** You need a `temporal_anchor` flag on entities you're already harvesting, plus a small harvest of pure-period designations that aren't institutions. The "period problem" is an ontological confusion, not a data engineering bottleneck.