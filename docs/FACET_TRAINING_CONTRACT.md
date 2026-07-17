# Facet Training Contract

**Status:** Binding for all facet SFA training (2026-07-16)  
**Graph:** Neo4j Aura `ac63a8e5`  
**In-scope domains:** `roman_republic`, `military_theory`  
**Root docs:** `EPISTEMIC_MODEL.md` → this file → `SCA_SFA_CONTRACT.md` → facet prompts

Chrystallum is **one graph**. Domains are scopes of work, not separate products.  
The deliverable is **typed, sourced, confidence-scored relationship paths** — not an encyclopedia of nodes.

> The senator reaches the mollusk only through Phase 2: a sourced, typed Claim that links them.

---

## 0. Non-authoritative session material

Do **not** treat the following as design truth without verifying against this contract and the live graph:

- `Archive/docs-2026-07/handoffs/SESSION_HANDOFF_2026_07_16.md`
- `Archive/docs-2026-07/sessions/` — `*_COMPLETE.md`, `*_SUMMARY.md`, `SFA_TRAINING_*.md`, `MILITARY_SFA_*.md`, phase reports
- `Archive/docs-2026-07/agents/SFA_PROMPTS_AND_PROCEDURES.md`, `SFA_QUICK_REFERENCE.md`
- `Archive/docs-2026-07/architecture-discovery/IGAR_MULTIAGENT_INTEGRATION.md` (early notes; §5 below is binding)
- `scripts/agents/military/agent_enhanced.py` theory-discovery path (`MilitaryPrinciple`, snake_case predicates)
- Any framing of IGAR as Investigate / Generate / Assert / Relate

Those produced unregistered labels, fake Events, and demo ASSERTS — purged 2026-07-16.

---

## 1. What “training” means

Training is **claim production under this contract**, not fine-tuning and not inventing ontology labels.

A training run succeeds when:

1. Both endpoints already exist in the graph (or are created only via the approved entity path with a real QID / authority id)
2. The predicate exists in the relationship registry with `lifecycle_status=implemented` (or `candidate` with Hold + human note)
3. The claim is sourced (federation / corpus work / passage)
4. Confidence is computed or explicitly justified — not invented as decoration
5. The claim is routed into a SubjectConcept scope under the correct Domain
6. No new Neo4j labels or relationship types are invented

Failure modes (forbidden):

- Creating labels like `:MilitaryPrinciple` without `SYS_NodeType`
- Snake_case “predicates” that are not registry `relationship_type` values
- Writing `start_date='unknown'` / fake QIDs to satisfy constraints
- Treating bookmark lists (`scripts/agents/military/corpus/*_RESOURCES.md`) as ingested corpus

---

## 2. Domains (scopes of work)

| Domain id | Version | Role |
|-----------|---------|------|
| `roman_republic` | versioned subgraph | Historical entities, events, institutions (509–27 BCE) |
| `military_theory` | versioned subgraph | Theory endpoints only when a historical claim needs them |

- **One Chrystallum repo / one Neo4j graph.**
- Geography is **not** a peer domain for training scope; geo SubjectConcepts / Places remain backbone.
- Legacy `:SubjectDomain {domain_id:'domain_roman_republic'}` (seed Q17167) is an **anchor**, linked via `SEED_FOR` — not a second versioned container.
- SubjectConcepts are **lenses / folders** inside a Domain (`Domain-[:CONTAINS]->SubjectConcept`), not domains themselves.
- Agents activate at **SubjectConcept**, not FacetUmbrella (`SCA_SFA_CONTRACT.md` / ADR-021).

**Routing rule**

| Content | Domain |
|---------|--------|
| Named battle, commander, legion instance, campaign in Republic period | `roman_republic` |
| Grounded abstract military concept needed as claim endpoint | `military_theory` |
| Ambiguous (“Roman legionary tactics”) | Prefer historical instance in RR; promote a theory node only when multiple RR claims need the same abstract object |

---

## 3. Claim shape (required fields)

Every training claim must be expressible as:

```
subject     — grounded node (Person, Event, Place, Concept, …)
predicate   — registry relationship_type (UPPER_SNAKE_CASE)
object      — grounded node
facet       — one of 18 canonical facets
domain_id   — roman_republic | military_theory
agent_id    — SFA_{subject_concept_id}_{FACET}
source      — federation source and/or CorpusWork + passage locator
confidence  — [0.0–1.0], computed or reviewed
state       — Proposed | ApprovalRequired | … (Claims track)
scope       — (Claim)-[:IN_SCOPE]->(SubjectConcept) when Claim node used
```

**Predicate vs interpretive gloss**

- **Canonical edge / ProposedEdge type** = registry `relationship_type` (e.g. `FOUGHT_IN`, `COMMANDED_BY`).
- Optional **facet gloss** (why this facet cares) may live in claim metadata — it must **not** replace the registry type.
- Do not submit `employed_tactic`, `defines_principle`, `crossed_rubicon` as relationship types unless they are added to the CSV first as `candidate`.

---

## 4. Relationship registry (mandatory)

Source of truth: `Relationships/relationship_types_registry_master.csv`  
Live mirror: Neo4j `SYS_RelationshipType`

| lifecycle_status | Training action |
|------------------|-----------------|
| `implemented` | May propose / promote |
| `candidate` | Hold; document gap; human may approve promotion path |
| `routing_only` | Hold for training claims |

**Do not invent types.** Add a CSV row (`candidate`) before any agent uses a new predicate.

Military starter set (already `implemented` — prefer these in the pilot):

`FOUGHT_IN`, `BATTLED_IN`, `BESIEGED`, `DEFEATED`, `COMMANDED_BY`, `SERVED_UNDER`, `SACKED`, `GARRISONED`, `MILITARY_ACTION`, …

Validate: `python -m scripts.tools.validate_sys_registry`

---

## 5. IGAR (correct definition)

**IGAR = Input → Goal → Action → Result**

- Optional **interpretation** layer — not required for atomic participation
- Atomic participation persists as language-neutral `wd_statement` (`Q36456-P607-Q179591`)
- **Not** part of claim cipher identity; **not** a predicate vocabulary
- Year-level temporal fields on Input / Action / Result when known
- Distinct from **CIDOC-CRM** (registry predicate alignment) and **CRMinf** (claim belief lifecycle)
- `claim_layer`: `atomic_participation` (default) vs `interpretation` (IGAR required)

**Blackboard / peer feedback:** The Neo4j graph is the shared blackboard (ADR-022). Atomic Q–P–Q claims use it as **shared state** (read Place/Event/Person; write Claims via registry) but do **not** require the Phase-2 consensus loop (cross-facet `:REVIEWED`, IGAR peer argument). Interpretation claims do. See archived `Archive/docs-2026-07/architecture-discovery/IGAR_MULTIAGENT_INTEGRATION.md` for early integration notes.

**Battle / multi-actor Events:** SFAs study participants on **both sides**. Missing persons → held add-person / stub via approved entity path (real QID). If the registry predicate is unclear, set `predicate_status=tbd`, keep **Hold**, and write `research_notes` — provisional registry type allowed; do not invent predicates.

**Place geodata (hard gate):** Any Place used as an Event location must have coordinates, normally from Wikidata **P625**. Events must link via registry predicate **`LOCATION_OF_EVENT`** (P276) to such a Place. Missing Place or missing `lat`/`long` → **Hold** — Validate is blocked in the Claims UI. Backfill: `python scripts/system/ensure_event_place_geo.py --event-qid <QID>`. Do not invent coordinates; skip coarse P276 values (e.g. Roman Italy).

**Agent stance:** slow and methodical; fewer well-sourced claims beat thin batch fills. See `scripts/agents/military/igar.py` (`MILITARY_BATTLE_METHOD_PROMPT`).

See ADR-022 and §5 above (archived discovery notes: `Archive/docs-2026-07/architecture-discovery/IGAR_MULTIAGENT_INTEGRATION.md`).

---

## 6. Write path (approved only)

Training agents must not open ad-hoc Bolt sessions that `CREATE` arbitrary labels.

| Purpose | Path |
|---------|------|
| Staged factual claims (preferred for training) | Claims track: propose → enrich → human review → promote (pattern: `docs/BIOGRAPHIC_CLAIM_PIPELINE.md`) |
| Multi-agent ASSERTS about canonical entities | `ClaimRegistry.submit_claim` **only if** `relationship_type` is registry-validated and entity constraints are satisfied |
| Canonical direct writes | Approved harvest only (DPRR; forward bio Person anchors). Bio must not create Events or PARTICIPATED_IN |

**Read before write** (`PIPELINE_READ_BACK_PRINCIPLE.md`): resolve existing Person/Event/Place by QID / `entity_cipher` before creating anything.

**Entity creation rules**

- Prefer existing nodes (real QIDs).
- Never invent QIDs (`Q_*_TEST`, `Q1048_DEMO_*`).
- Never invent required properties (`start_date='unknown'`) to bypass constraints — Hold the claim instead.
- Places used as locations must carry `lat`/`long` (Wikidata P625); never invent coordinates.
- New node labels require `SYS_NodeType` + model-first update before use.

---

## 7. Facets

All 18 facets train under this same contract. Facet-specific material is limited to:

1. System prompt specialization (what to look for)
2. Allowed registry predicate subset (by category)
3. Primary corpus list for that facet’s SubjectConcepts
4. Peer-review heuristics

Facets do **not** get private ontologies or private predicate languages.

Agent ID pattern: `SFA_{subject_concept_id}_{FACET}`  
Example: `SFA_sc_q17167_roman_army_military_campaigns_MILITARY`

---

## 8. Pilot definition (gate before multi-facet scale)

**Pilot facet:** MILITARY  
**Domain:** `roman_republic`  
**Scale:** 5–10 claims maximum in the first write batch  

**Seed endpoints (must already exist or be real QIDs):**

- Event: Battle of Cannae `Q179591` (not Q36456 — that QID is Hannibal)
- Person: commanders / participants on **both sides**; create Person stubs only with real QIDs

**Allowed predicates for pilot:** registry Military `implemented` types only (see §4).

**Success criteria**

- [x] Zero new Neo4j labels *(pilot 2026-07-16)*
- [x] Zero fake QIDs / `unknown` constraint fillers
- [x] Every claim has subject, registry predicate, object, source, facet, domain
- [x] Every claim `IN_SCOPE` to a military-related SubjectConcept under `roman_republic`
- [x] Human can review in Claims UI — API `source_agent` filter + Claims IGAR panel
- [x] Path queryable: Person → ProposedEdge `FOUGHT_IN` → Event (Claim chain)
- [x] IGAR metadata + both-sides roster (Roman + Carthaginian); TBD predicates held

**Pilot (revised 2026-07-16 night):** atomic Q–P–Q both-sides Cannae roster  
(`wd_statement` e.g. `Q36456-P607-Q179591`); IGAR optional / cleared from participation claims.  
Commands: `training_pilot --write`, `cannae_roster_research --write`.  
Outputs: `output/military_training_pilot_atomic_qpq.json`, `output/cannae_roster_research.json`.

**Only after pilot pass + human review:** clone the loop to Diplomatic / Political / Economic / … with the same rails.

`military_theory` stays empty until a pilot claim needs a grounded theory object as endpoint.

---

## 9. Corpus rules

- Primary ancient texts and federation sources beat modern blogs.
- Bookmark files under `scripts/agents/military/corpus/` (`MILITARY_RESOURCES.md`, `NAVAL_RESOURCES.md`) are **source directories**, not corpora.
- Training reads **passages** into claim evidence (`CorpusWork` / passage locator / hash), per ADR-021 corpus tiers.
- Anachronism: flag late doctrine applied to Republic (e.g. Vegetius) in metadata; do not silently assert.

---

## 10. Checklist (every training write)

```
[ ] Read graph first — endpoints exist?
[ ] Predicate in registry as implemented (or candidate+Hold)?
[ ] Domain = roman_republic or military_theory (correct one)?
[ ] SubjectConcept scope chosen; agent_id matches ADR-021 pattern?
[ ] Source + passage (or federation) attached?
[ ] IGAR only if actor-centric Event — and as metadata only?
[ ] No new labels / no fake QIDs / no unknown dates as hacks?
[ ] Human review path identified before batch > pilot size?
```

---

## 11. Related documents

| Doc | Role |
|-----|------|
| `docs/EPISTEMIC_MODEL.md` | What can be known |
| `docs/SCA_SFA_CONTRACT.md` | SCA vs SFA roles; SC activation |
| `docs/BIOGRAPHIC_CLAIM_PIPELINE.md` | Mature Claims-track reference implementation |
| `docs/PIPELINE_READ_BACK_PRINCIPLE.md` | Read before write |
| `Archive/docs-2026-07/architecture-discovery/IGAR_MULTIAGENT_INTEGRATION.md` | Historical IGAR notes (non-binding) |
| `scripts/agents/military/corpus/` | Military / naval source directories (not ingested corpus) |
| `Relationships/relationship_types_registry_master.csv` | Predicate law |
| ADR-021 / ADR-022 | Agent scope; multi-agent claims / blackboard |

---

**Next engineering step after this contract:** implement registry validation inside the Military training write path, then execute the §8 pilot on live entities.
