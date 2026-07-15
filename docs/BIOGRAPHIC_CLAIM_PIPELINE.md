# Biographic claim pipeline

**Status:** Active (2026-07-15)  
**Graph:** Neo4j Aura `ac63a8e5` · `source_agent: sfa_biographic`

This doc is the single reference for the **Claims track** — staged Wikidata backlink assertions that are **not** canonical graph edges until enriched, reviewed, and promoted.

---

## Three tracks (Roman Republic)

```
SubjectConcept track     DI propose → human review → di_proposal nodes under FacetUmbrella
Canonical graph track    DPRR + forward bio harvest → Person/Event edges directly in graph
Claims track             Backlink harvest → enrich → propose → human review → promote
```

Claims and SubjectConcepts are **not linked in Neo4j today**. Claims and canonical edges may describe the same fact via different paths.

---

## Pipeline stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Forward harvest (agent.py)                                         │
│    Person birth/death/places, SPOUSE_OF + P580/P582, PARTICIPATED_IN    │
│    → writes CANONICAL edges (no Claim node)                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. Backlink harvest (backlink_harvest.py)                             │
│    Wikidata ?item ?pred wd:person → BIO_CANDIDATE_REL stubs           │
│    agent_reviewed=false                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Claim proposer (claim_proposer.py)                                 │
│    BIO_CANDIDATE_REL → Claim + ProposedEdge + Fischer lint              │
│    Marks BIO_CANDIDATE_REL.agent_reviewed=true                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. Agent enrichment (enrich_claims.py)  ← run before human review     │
│    Re-fetch Wikidata statement; harvest P580/P582/P585 qualifiers     │
│    Sets Claim.start_year/end_year/point_year, enrichment_status         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. Human review (proposal_review_api.py + Bio Claims tab)             │
│    Soft date gate: Hold recommended; Validate requires notes if gaps  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. Familial reconciliation (reconcile_familial.py)                    │
│    DPRR wins; gap-fill promote CHILD_OF/SPOUSE_OF/SIBLING_OF          │
│    Non-familial unreconciled claims need separate policy              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Commands

```powershell
# Backlink harvest (if not done during person harvest)
python -m scripts.agents.biographic.backlink_harvest --limit 3000 --write

# Promote stubs to Claim nodes
python -m scripts.agents.biographic.claim_proposer --limit 6000 --write

# Agent enrichment (Wikidata qualifiers) — before review
python -m scripts.agents.biographic.enrich_claims --limit 500 --write

# Fix inverted agent-anchor edge directions + backfill descriptions
python -m scripts.agents.biographic.fix_claim_direction --write

# Familial gap-fill promotion
python -m scripts.agents.biographic.reconcile_familial --write

# Review API + viewer
python scripts/ui/proposal_review_api.py
cd viewer; npm run dev
```

---

## Graph shapes

### BIO_CANDIDATE_REL (harvest stub)

```
(candidate:Entity)-[:BIO_CANDIDATE_REL {pred_pid, edge_type, item_label, ...}]->(p:Person)
```

### Claim (proposal)

```
(Claim)-[:ASSERTS_EDGE]->(ProposedEdge)-[:FROM]->(endpoint)
                              (ProposedEdge)-[:TO]->(endpoint)
```

For agent-on-person predicates (RAISED_LEGION, PARTICIPATED_IN, …) direction is **Person → candidate** after `claim_direction.py` / `fix_claim_direction.py`.

### Claim enrichment properties

| Property | Source |
|----------|--------|
| `start_year`, `end_year`, `point_year` | Wikidata P580/P582/P585 via `enrich_claims.py` |
| `enrichment_status` | `pending` \| `complete` \| `partial` \| `missing` \| `not_applicable` |
| `description` | Generated prose from backlink metadata |
| `authority_ids` | JSON: `person_qid`, `candidate_qid`, `pred_pid` |

---

## Human approval checklist

See `.cursor/rules/bio-claim-approval.mdc` and the **Before you approve** panel in Bio Claims.

| Check | Source |
|-------|--------|
| Who | Person anchor + lifespan (Person node) |
| What | Proposed edge direction, PID, description |
| When | Event `start_date`, relation years, enriched qualifiers |
| Provenance | Wikidata, harvest time, enrichment_status |
| Reconciliation | DPRR / canonical edge status |

**Soft date policy:** Missing dates on date-sensitive types → Hold recommended. Validate allowed with review notes (≥8 chars) + confirm dialog — not a hard block.

---

## Related docs

- `scripts/agents/biographic/HARVEST_SCOPE.md` — forward harvest scope
- `docs/BIO_BACKLINK_REVERSAL_PLAN.md` — backlink decoupling (implemented)
- `docs/EPISTEMIC_MODEL.md` — claim lifecycle
- `docs/ARCHITECTURE_CURRENT.md` — system-wide architecture

---

## Known gaps

- [ ] Non-familial unreconciled claims (~595) — promotion policy TBD
- [ ] Claims → SubjectConcept routing (architecture mentions; not wired)
- [ ] Event `start_date` backfill for participation claims where Event node is null
- [ ] Batch `enrich_claims` on full 5,666 backlog before large review sessions
