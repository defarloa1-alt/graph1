# Q17167 Roman Republic — Facet Hierarchy Baseline

**Date:** 2026-07-15  
**Event:** DI proposals approved and written; facet umbrella layer wired under SubjectDomain  
**Status:** **Definitive subject-backbone baseline for Q17167** — navigable 3-tier hierarchy live on Aura

---

## What This Baseline Marks

Roman Republic (Q17167) now has a **reviewed, written, navigable subject graph** separate from the temporal/factual layers:

1. **SubjectDomain** — topic hub (`domain_roman_republic`)
2. **FacetUmbrella** — 15 facet layer nodes (`Facet — Military`, etc.)
3. **di_proposal decompositions** — 63 approved SubjectConcepts under facet umbrellas

Human review completed on all DI proposals. Graph writes verified on Neo4j Aura (`ac63a8e5`).

**Not in this baseline:** factual Wikidata claims track (`Q17167_validated_claims_v2.json`) — separate review/write pass.

---

## Formal Baseline Numbers

```
Date:               2026-07-15
Database:           neo4j @ neo4j+s://ac63a8e5.databases.neo4j.io
Seed QID:           Q17167

SubjectDomain:
  domain_id:        domain_roman_republic
  label:            Roman Republic · Subject Domain
  elementId:        4:2ce681c2-5f2e-4f55-8da3-856508f132d1:53442

Period (temporal anchor only):
  qid:              Q17167
  label:            Roman Republic
  elementId:        4:2ce681c2-5f2e-4f55-8da3-856508f132d1:49849
  note:             NOT the subject tree — 41k+ IN_PERIOD edges

Facet umbrellas (FacetUmbrella label):
  count:            15
  on domain direct: 15 HAS_SUBJECT_CONCEPT (only layer attached to domain)
  label pattern:    Facet — {FacetName}

DI decomposition SubjectConcepts:
  approved/written: 63  (source: di_proposal)
  PART_OF umbrella: 63
  SCOPED_TO domain: 0   (scope via hierarchy, not direct)

SFA training runs:
  Q17167 runs:      14
  linked to umbrella: 14 via RELEVANT_TO_SUBJECT

Legacy bootstrap SCs:
  ccs_bootstrap:    15 (still in graph, detached from domain)
  geo_bootstrap:    4  (still in graph, detached from domain)
  on domain:        0

SubjectDomain USES_TYPE (seed P31):
  Q3024240          historical country
  Q11514315         historical period
```

### Decompositions by facet

| Facet | Umbrella ID | Decompositions |
|-------|-------------|----------------|
| archaeological | sc_q17167_facet_archaeological | 8 |
| artistic | sc_q17167_facet_artistic | 7 |
| biographic | sc_q17167_facet_biographic | 7 |
| communication | sc_q17167_facet_communication | 8 |
| cultural | sc_q17167_facet_cultural | 0 |
| demographic | sc_q17167_facet_demographic | 0 |
| economic | sc_q17167_facet_economic | 0 |
| geographic | sc_q17167_facet_geographic | 6 |
| intellectual | sc_q17167_facet_intellectual | 0 |
| linguistic | sc_q17167_facet_linguistic | 0 |
| military | sc_q17167_facet_military | 8 |
| political | sc_q17167_facet_political | 7 |
| religious | sc_q17167_facet_religious | 4 |
| scientific | sc_q17167_facet_scientific | 0 |
| social | sc_q17167_facet_social | 8 |
| **Total** | | **63** |

Six facets have training but no decompositions yet (cultural, demographic, economic, intellectual, linguistic, scientific).

---

## Hierarchy Model (live)

```
SubjectDomain  Roman Republic · Subject Domain
  ├─ HAS_SUBJECT_CONCEPT → FacetUmbrella  (15)
  │     ← PART_OF ── di_proposal SC       (63)
  ├─ OCCURS_DURING → Period Q17167
  ├─ USES_TYPE → historical country, historical period
  └─ ALIGNED_WITH_LCC → DG1-365, DG21-190, KJA*, PA6000-6971

SFA_TrainingRun -[:RELEVANT_TO_SUBJECT]-> FacetUmbrella
SFA_SubScope    -[:PROMOTED_TO]-> di_proposal SC (by scope_key)
```

**Browser navigation:** expand **SubjectDomain**, not Period. Both share seed QID context; Period has 41k+ temporal edges.

---

## Pipeline State

| Stage | Status | Artifact |
|-------|--------|----------|
| harvest | done | `output/di_harvest/Q17167_di_harvest.json` |
| classify | done | `output/di_classify/Q17167_di_classify.json` |
| route | done | `output/di_route/Q17167_*_pack.json` |
| train | 15/18 facets | `output/di_training/Q17167_*_training.json` |
| propose + review | **63 approved** | `output/di_proposals/Q17167_proposals_enriched.json` |
| graph write | **done** | 63 di_proposal + 15 FacetUmbrella |
| facet wire | **done** | `scripts/agents/domain_initiator/wire_facet_umbrellas.py` |

**Facets not yet trained:** diplomatic, environmental, technological

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/agents/domain_initiator/propose.py` | Propose, review, write DI SCs + facet wire |
| `scripts/agents/domain_initiator/facet_umbrella.py` | FacetUmbrella creation, domain prune, hierarchy |
| `scripts/agents/domain_initiator/wire_facet_umbrellas.py` | Repair/rewire existing graph |
| `scripts/neo4j/view_roman_republic_facet_tree.cypher` | Browser starter query |

---

## Verification Queries

**Facet tree (SubjectDomain only):**
```cypher
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (sd)-[:HAS_SUBJECT_CONCEPT]->(u:FacetUmbrella)
OPTIONAL MATCH (u)<-[:PART_OF]-(sc:SubjectConcept {source: 'di_proposal'})
RETURN sd, u, sc
```

**Sanity — nothing but umbrellas on domain:**
```cypher
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})-[:HAS_SUBJECT_CONCEPT]->(sc)
RETURN sc.source, count(*) ORDER BY count(*) DESC
```

Expected: single row `di_facet_umbrella | 15`.

---

## Remaining (post-baseline)

| Item | Notes |
|------|-------|
| Factual claims write | `JSON/wikidata/integrated/Q17167_validated_claims_v2.json` — separate track |
| Train 3 missing facets | diplomatic, environmental, technological |
| Proposals for 6 trained-empty facets | cultural, demographic, economic, intellectual, linguistic, scientific |
| Agent → FacetUmbrella links | optional: `SFA_*_RR` agents |
| Bootstrap SC disposition | 15 ccs + 4 geo orphaned; may PART_OF umbrellas or deprecate |

---

## Machine-readable snapshot

`output/baseline/Q17167_facet_hierarchy_baseline.json` — captured 2026-07-15 from live Aura.

Re-capture: `python scripts/tools/capture_q17167_baseline.py`

---

*Baseline established before factual claims layer and geo expansion pass.*
