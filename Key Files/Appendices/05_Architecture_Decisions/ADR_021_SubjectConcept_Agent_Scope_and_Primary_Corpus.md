# ADR-021: SubjectConcept Agent Scope and Primary Corpus Tier

**Status:** ACCEPTED  
**Date:** 2026-07-15  
**Related:** ADR-020 (CCS), ADR-004 (18 facets), `docs/SCA_SFA_CONTRACT.md`

---

## Context

The Domain Initiator decomposed the Roman Republic (Q17167) into **63 `di_proposal` SubjectConcepts** under **15 FacetUmbrellas**. Each decomposition exists to bound scholarly scope — populatable topics with authority tethers, not facet-wide summaries.

Two gaps blocked operational use of that decomposition:

1. **Agents operated at facet-umbrella level** (e.g. "Biographic facet of Roman Republic") instead of at the decomposed SubjectConcept that defines *why* a fact belongs in the graph.
2. **Agent training corpus was secondary scholarship only** (OpenAlex, Wikidata P921). Primary ancient texts — Plutarch, Suetonius, Cicero, Caesar, Appian — were cited in DI proposals but not registered as a distinct corpus tier for facet-scoped reading and claim evidence.

---

## Decision

### 1. Operational unit = SubjectConcept (not FacetUmbrella)

| Layer | Role | Agent activation |
|-------|------|------------------|
| **SubjectDomain** | Seed anchor (Q17167) | No agent |
| **FacetUmbrella** | Index / curation shelf | No agent |
| **SubjectConcept** (`di_proposal`) | Scoped scholarly question | **Yes** — SFA activates here |
| **Person / Event / Place** | Claim endpoints | Federation entities |

**Agent ID pattern (revised):**

```
SFA_{subject_concept_id}_{primary_facet}
```

Example: `SFA_sc_q17167_senatorial_elite_careers_BIOGRAPHIC` — not `SFA_subj_roman_republic_q17167_BIOGRAPHIC`.

FacetUmbrella nodes organize proposals and route bibliography. They are **not** reasoning boundaries.

### 2. Claims route to SubjectConcept scope

Biographic and SFA-produced claims attach to the SubjectConcept that defines the scholarly question:

```cypher
(Claim)-[:IN_SCOPE {
  routing_score: float,
  routing_method: string,   // rule | person_set | fallback
  routed_at: datetime
}]->(SubjectConcept {source: 'di_proposal'})
```

Claim nodes also carry denormalized fields for review UI:

- `routed_subject_id`
- `routed_subject_label`
- `routing_score`

`IN_SCOPE` means "this claim is evaluated and approved within this scholarly scope." It is distinct from:

- `(Person)-[:MEMBER_OF]->(SubjectConcept)` — cluster membership
- `(SubjectConcept)-[:SCOPED_TO]->(SubjectDomain | Period)` — domain/period anchor

### 3. CorpusWork tier

Every `CorpusWork` node carries:

| Property | Values | Purpose |
|----------|--------|---------|
| `corpus_tier` | `primary` \| `secondary` \| `reference` | Training vs evidence hierarchy |
| `source_era` | `contemporary` \| `near_contemporary` \| `antiquarian` \| `modern_scholarly` | Confidence weighting |

**Tier definitions:**

- **primary** — Ancient literary sources (Plutarch, Suetonius, Livy, Cicero, Caesar, Appian, Nepos); passage-level citation required for claims grounded in these works.
- **secondary** — Modern scholarly monographs, journal articles, prosopographic databases (DPRR, MRR).
- **reference** — Encyclopedias, course materials, indices (Stanford Encyclopedia, OCW syllabi).

Primary sources are registered per SubjectConcept via `(SubjectConcept)-[:HAS_BIBLIO {rank, corpus_tier}]->(CorpusWork)`.

### 4. Facet-scoped primary reading (training)

During SFA training on a SubjectConcept:

1. Load SC bounds, facet vector, and `HAS_BIBLIO` works filtered by `corpus_tier`.
2. Read **primary** works first from the facet lens (Military SC → campaign passages; Biographic SC → life-narrative passages).
3. Use **secondary** works for historiographic framing and cross-check.
4. Runtime claims must cite `{work_id, passage}` — Perseus CTS URN when available — hashed into `claim_id` per ADR-001.

Training at FacetUmbrella level remains valid only for **initial decomposition** (DI `train.py`). Ongoing agent operation and claim review use SubjectConcept scope.

---

## Consequences

**Positive:**

- Claim review UI shows *which scholarly question* a biographic assertion belongs to.
- Primary texts become first-class federation inputs, not footnotes in supporting_works JSON.
- Agent prompts stay bounded — no "summarize Roman Republic military" at umbrella scale.
- Aligns with epistemic model: claims need facet + temporal + passage + scope.

**Negative / migration:**

- Existing biographic claims (5,666) need batch routing (`route_claims_to_sc.py`).
- `train.py` corpus fetch should eventually accept `--subject-id` in addition to `--facet`.
- Perseus federation (Phase D) required for automated passage retrieval; until then, Internet Archive + manual passage refs.

---

## Implementation

| Artifact | Purpose |
|----------|---------|
| `scripts/agents/biographic/claim_sc_routing.py` | Deterministic routing rules |
| `scripts/agents/biographic/route_claims_to_sc.py` | Batch write `IN_SCOPE` edges |
| `scripts/agents/domain_initiator/primary_corpus_catalog.json` | Canonical primary works |
| `scripts/agents/domain_initiator/seed_primary_corpus.py` | MERGE CorpusWork + HAS_BIBLIO |
| `proposal_backbone.normalize_corpus_work()` | Infer `corpus_tier`, `source_era` |

---

## Related ADRs

- ADR-020: CCS validity rules govern which SubjectConcepts exist
- ADR-004: 18-facet vector on each SC
- ADR-001: Claim identity cipher includes facet + passage
