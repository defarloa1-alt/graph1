# Biographic claim pipeline

**Status:** Active (2026-07-15)  
**Graph:** Neo4j Aura `ac63a8e5` · `source_agent: sfa_biographic`

This doc is the single reference for the **Claims track** — staged Wikidata backlink assertions that are **not** canonical graph edges until enriched, reviewed, and promoted.

---

## Three tracks (Roman Republic)

```
SubjectConcept track     DI propose → human review → di_proposal nodes under FacetUmbrella
Canonical graph track    DPRR + forward bio harvest → Person anchors only (not Events)
Claims track             Backlink harvest → enrich → propose → human review → promote
```

**Event policy (2026-07-16):** Forward bio harvest must **not** create `:Event` nodes, invent `Event.start_date` from person birth/death years, or write canonical `PARTICIPATED_IN`. Event associations from Wikidata (P607 / P793 / P1344) are discovery evidence only until an existing, correctly typed Event has an independent date (e.g. Wikidata P585) and a Claim is reviewed. Prior bio Event contamination was quarantined via `scripts/system/quarantine_bio_event_harvest.py`.

Claims and SubjectConcepts are linked via **`(Claim)-[:IN_SCOPE]->(SubjectConcept)`** (ADR-021). Run `route_claims_to_sc.py` after claim_proposer. Claims and canonical edges may still describe the same fact via different paths.

---

## Pipeline stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Forward harvest (agent.py)                                         │
│    Person birth/death/places, SPOUSE_OF + P580/P582                     │
│    → writes CANONICAL Person anchors (no Claim node)                    │
│    → does NOT write Event / PARTICIPATED_IN (disabled 2026-07-16)       │
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
│ 3b. Scope routing (route_claims_to_sc.py)                             │
│    Claim → IN_SCOPE → di_proposal SubjectConcept (biographic scopes)    │
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

# Route claims to DI SubjectConcept scope (ADR-021)
python -m scripts.agents.biographic.route_claims_to_sc --write --limit 6000

# Seed primary corpus (Plutarch, Suetonius, …) to biographic SCs
python scripts/agents/domain_initiator/seed_primary_corpus.py --write

# Agent enrichment (Wikidata qualifiers) — before review
python -m scripts.agents.biographic.enrich_claims --limit 500 --write

# Validate SYS registry vs CSV (audit)
python -m scripts.tools.validate_sys_registry

# Sync CSV → SYS_RelationshipType (run after CSV edits)
python -m scripts.tools.sync_relationship_registry_to_graph --write --wire-schema

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

### Claim scope (ADR-021)

```
(Claim)-[:IN_SCOPE {routing_score, routing_method, routed_at}]->(SubjectConcept {source: 'di_proposal'})
```

Denormalized on Claim: `routed_subject_id`, `routed_subject_label`, `routing_score`.

### Claim enrichment properties

| Property | Source |
|----------|--------|
| `start_year`, `end_year`, `point_year` | Wikidata P580/P582/P585 via `enrich_claims.py` |
| `enrichment_status` | `pending` \| `complete` \| `partial` \| `missing` \| `not_applicable` |
| `description` | Generated prose from backlink metadata |
| `authority_ids` | JSON: `person_qid`, `candidate_qid`, `pred_pid` |
| `wd_statement` | Language-neutral Wikidata key: `Q36456-P607-Q179591` |
| `object_qid`, `pred_pid` | Top-level QIDs / PID (prefer over English labels) |

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
- [ ] Event `start_date` backfill for participation claims where Event node is null
- [ ] Batch `enrich_claims` on full 5,666 backlog before large review sessions
- [ ] Perseus passage fetch for primary-source claim evidence (Phase D federation)
- [ ] SFA training `--subject-id` mode (currently facet-wide in train.py)
