# ADR-020: Chrystallum Classification System (CCS)

**Status:** ACCEPTED
**Date:** 2026-03-09
**Deciders:** Architecture Review

---

## Context and Problem Statement

Library classification systems — LCC, LCSH, FAST, Dewey — were engineered for physical shelf placement. One book occupies one shelf. This monodimensional constraint is not a flaw of the systems; it is an engineering necessity of their era. They are authoritative, universal, and ubiquitous: 500 million WorldCat records use them. They cannot, however, represent what a topic *actually is* across multiple research dimensions simultaneously.

Three problems arise when using these systems naively in Chrystallum:

1. **Cross-class scatter**: A single concept may be shelved across multiple incompatible LCC branches. Roman Law appears at DG87 (history), KJA2-3660 (legal system), KJA190-2152 (primary legal sources), and PA6000-6971 (literary context of legal speeches). No single shelf captures the concept.

2. **Monodimensional classification**: A book receives one primary subject heading. "Roman Army" is MILITARY. But military service was simultaneously an economic activity (pay, booty), a social institution (patronage, class), a geographic phenomenon (provincial expansion), and a biographical record (careers). LCSH records one heading; the facet vector requires all five.

3. **Type buckets masquerading as subjects**: Without explicit governance, bootstrap processes produce entity-type containers ("Military Figures & Commanders") rather than proper subject concepts ("Roman Army & Legion Organization"). These buckets have no external authority tether and cannot be navigated across facets.

---

## Decision

Chrystallum adopts the **Chrystallum Classification System (CCS)** as the governing architecture for SubjectConcept construction. CCS is defined as:

> **An AI-powered rationalization layer over ubiquitous library shelving infrastructure, which harvests authority tethers from multiple classification branches, aggregates cross-class scatter into a single addressable concept node, and infers a weighted multidimensional facet vector from the combined context.**

CCS does not replace LCC, LCSH, FAST, or Dewey. Those systems remain the authority backbone. CCS is a layer that makes their inherently scattered, monodimensional representation navigable as a multidimensional knowledge structure.

---

## CCS Technical Architecture

### Step 1 — Authority Harvest

Starting from a Wikidata QID, a single call returns all shelf assignments:

```
Q17167 (Roman Republic)
  P244  → sh85115114    LCSH heading
  P2163 → fst01204885   FAST faceted heading
  P1149 → DG241-269     LCC shelf range
  P1036 → 937.04        Dewey number
  P214  → VIAF ID
  + domain-specific: Nomisma, PACTOLS, EAGLE, BnF, etc.
```

All tethers are preserved on the SubjectConcept node. Interoperability with any library system is maintained.

### Step 2 — Cross-Class Aggregation

The AI recognizes that one concept is scattered across multiple LCC branches and collapses them into a single SubjectConcept with multiple `ANCHORS` edges:

```cypher
(:SubjectConcept {label: 'Roman Law & Legal Institutions'})
  -[:ANCHORS]-> (:LCC_Class {code: 'DG87'})
  -[:ANCHORS]-> (:LCC_Class {code: 'DG155-167'})
  -[:ANCHORS]-> (:LCC_Class {code: 'KJA2-3660'})
  -[:ANCHORS]-> (:LCC_Class {code: 'KJA190-2152'})
```

The LCC nodes remain. The SC is the aggregation point. No library record is modified.

### Step 3 — Facet Inference

Given the full context — all authority IDs, LCSH scope notes, LCC hierarchy, Wikipedia article structure, WorldCat catalog usage — an LLM infers a weighted facet vector across all 18 canonical facets:

```
Roman Law & Legal Institutions:
  INTELLECTUAL  0.90  — jurisprudence, legal scholarship, Digest, Institutes
  POLITICAL     0.80  — magistrates, constitution, governance by law
  SOCIAL        0.50  — property rights, slavery, family law, inheritance
  BIOGRAPHIC    0.40  — Cicero, Gaius, Papinian, Ulpian as legal authors
```

Weights are LLM-inferred from evidence, not asserted by convention. They are revisable and contestable by SFAs.

---

## Validity Rules for a SubjectConcept under CCS

A SubjectConcept is **valid** if and only if:

1. **Authority tether**: Has at least one external authority ID — QID, LCSH (`sh...`), FAST (`fst...`), LCC code, or domain-specific identifier (Nomisma, PACTOLS, etc.)
2. **Multidimensional**: Has a minimum of two `HAS_FACET` edges with inferred weights (`{weight: float}`)
3. **Populatable**: At least one SYS_FederationSource can supply members (`MEMBER_OF` edges) for it
4. **Topic-grounded**: Represents a named historical/scholarly topic, not an entity type. "Roman Army Organization" is valid. "Military Figures" is not.

A SubjectConcept that fails any of these rules is a **type bucket** and must be replaced.

---

## What CCS Is Not

- **Not a replacement** for LCSH/LCC/FAST — those remain authoritative
- **Not folksonomy** — every SC requires an external authority tether
- **Not static** — facet weights are evidence-derived, not fixed
- **Not comprehensive** — CCS does not aim to classify all of human knowledge; it rationalizes the domain-specific subset needed for Chrystallum's federation sources

---

## Consequences

**Positive:**
- SubjectConcepts become genuinely multidimensional — navigable from any of their facets
- Cross-class scatter (the Roman Law problem) is resolved architecturally, not by workaround
- All SCs remain interoperable with library systems via preserved authority tethers
- Bootstrap scripts cannot produce type buckets — validity rules catch them at construction

**Negative:**
- Every SC requires an LLM inference pass (Step 3) — cannot be bulk-generated by keyword heuristics
- Facet weights require validation; first-pass LLM inference is not final
- Existing bio_bootstrap and other type-bucket SCs must be deleted and rebuilt under CCS rules

---

## Migration

The following existing SubjectConcepts are **type buckets** and do not meet CCS validity rules. They must be deleted:

| SC label | Reason |
|---|---|
| Political Figures & Magistrates | Entity type container |
| Military Figures & Commanders | Entity type container |
| Religious & Sacerdotal Figures | Entity type container |
| Legal Scholars & Jurists | Entity type container |
| Writers, Philosophers & Scholars | Entity type container |
| Economic & Financial Figures | Entity type container + contaminated membership (385 out-of-domain persons) |
| General Biographical Persons | Overly broad catch-all, not a topic |

The geo_bootstrap SCs (Settlements, Water Bodies, Historical Places, etc.) are structurally valid under CCS but require secondary facet wiring (currently GEOGRAPHIC-only).

---

## Related ADRs

- ADR-004: Canonical 18-Facet System — defines the facet vector CCS populates
- ADR-001: Claim Identity Ciphers — QID-based identity used as CCS anchor entry point
- ADR-006: Bootstrap Scaffold Contract — CCS governs what qualifies as a valid scaffold node
