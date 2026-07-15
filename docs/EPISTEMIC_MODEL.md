# Chrystallum — Epistemic Model
**Root governance document. All other models derive from this.**

---

## 1. The Atomic Unit

A claim asserts that a **subject** has some relationship to an **object**.
The predicate — what that relationship *is* — is determined later.

```
Subject  ——[predicate TBD]——  Object
```

This is intentional. Phase 1 identifies what subjects and objects exist.
Phase 2 assigns the predicate: typed, directed, weighted, sourced.

Rushing to the predicate before both endpoints are confirmed
is the primary source of bad graph data.

---

## 2. What Makes a Subject or Object Valid

A subject or object is valid in Chrystallum only if it is:

1. **Grounded** — traceable to at least one external authority (LCSH, FAST, LCC, Wikidata QID, Pleiades, Nomisma…)
2. **Scoped** — belongs to a named scholarly domain and time period
3. **Scholarly** — a topic that a discipline studies, not a container for entity types

"Roman military history" — valid subject.
"Military figures" — invalid (entity-type container, not a topic).
"Lucius Caecilius Metellus" — valid object (person, grounded in DPRR + Wikidata).
"mollusk" — valid object if grounded (Pliny NH passage, archaeological record).

---

## 3. What Makes a Predicate Valid

A predicate is valid only when:

1. Both endpoints (subject and object) are confirmed valid
2. The relationship type exists in `SYS_RelationshipType` registry
3. The assertion is sourced — a `SYS_FederationSource` made this claim
4. The confidence is computed from authority tier + corroboration, not asserted

Predicates are **never** hardcoded in Python. They live in the graph
as typed, sourced, confidence-scored edges between confirmed nodes.

---

## 4. The Claim

When subject + predicate + object are all confirmed, the result is a **Claim**:

```
Claim {
  subject:    node (Person, Place, Concept…)
  predicate:  typed relationship from SYS_RelationshipType
  object:     node (Person, Place, Concept…)
  source:     SYS_FederationSource
  confidence: float [0.0–1.0]  — computed, never asserted
  state:      Proposed | ApprovalRequired | Approved | Contested | Superseded
  temporal:   start, end
  enrichment: pending | complete | partial | missing | not_applicable  (biographic backlink claims)
  evidence:   passage or CorpusWork that grounds it
}
```

The claim_id is a cipher: `Hash(subject + predicate + object + facet + temporal + source + passage)`.
Same assertion from same source = same ID. Different source = different claim.

**Biographic backlink claims:** temporal fields may come from Wikidata qualifiers (P580/P582/P585) via agent enrichment (`scripts/agents/biographic/enrich_claims.py`) before human approval. Missing dates on date-sensitive relationship types should default to Hold; human validation with documented rationale is permitted (soft gate). See `docs/BIOGRAPHIC_CLAIM_PIPELINE.md`.

---

## 5. The MDSE Derivation Chain

```
Epistemic model   →  what can be known and how
    ↓ drives
Conceptual model  →  what entities and relationships exist
    ↓ drives
Logical model     →  how they are structured (schema, types, rules)
    ↓ drives
Physical model    →  Neo4j nodes, edges, properties (ARCHITECTURE_CURRENT.md)
```

Any element in the physical model that cannot trace back to this document
should be removed or explicitly justified as an exception.

---

## 6. The Two Phases

**Phase 1 — Subject/Object identification (DI pipeline)**
Harvest → Classify → Route → Train → Propose.
Output: SubjectConcept candidates with authority tethers and facet vectors.
No predicates. No inter-SC relationships. Only nodes.

**Phase 2 — Predicate assignment (SCA/SFA + federation)**
Claim extraction from sources (SFA_INDEX_READER, DPRR, Pleiades…).
Each claim types the relationship: ALLIED_WITH, POSITION_HELD, OWNED, PARTICIPATED_IN…
Confidence computed from D15–D18 scoring rules.
Corroboration and contradiction tracked as first-class states.

The senator reaches the mollusk only through Phase 2:
a sourced, typed, confidence-scored Claim that links them.

---

## 7. What This Rules Out

| Prohibited | Why |
|---|---|
| Direct entity→entity edges without a Claim | Bypasses provenance — violates the atomic unit |
| Entity-type containers as SubjectConcepts | Not a scholarly topic — violates rule 3 in §2 |
| Predicates before endpoints are confirmed | Phase ordering violation |
| Confidence values hardcoded in Python | Must be computed from graph rules (D15–D18) |
| Deleting superseded claims | Superseded claims are epistemic history — MERGE only |
| Collapsing contradicting claims | Contradiction is real data, not a bug to fix |
