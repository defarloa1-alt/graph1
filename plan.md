# ADR-007 / ADR-008 Person Schema & Harvest Agent — Development Plan

## Current State (Baseline)

| Metric | Value |
|--------|-------|
| Nodes with `entity_id STARTS WITH 'person_'` | 5,157 |
| Nodes with `dprr_id IS NOT NULL` | 4,863 (includes some non-person-prefix) |
| DPRR persons (person_ prefix + dprr_id) | 4,772 |
| Non-DPRR person_ prefix nodes | 385 |
| Nodes already carrying `:Person` label | **3** (Romulus, Remus, Europa — MythologicalPerson) |
| `:Gens` nodes | 0 |
| `:Praenomen` / `:Nomen` / `:Cognomen` nodes | 0 |
| `:Tribe` nodes | 0 |
| P-code edges still raw (not promoted) | P21(372), P27(165), P19(88), P20(168), P140(41), P2348(20), etc. |
| Existing canonical rels | POSITION_HELD(6,934), FATHER_OF(2,011), MOTHER_OF(571), SIBLING_OF(2,091), SPOUSE_OF(578) |
| ADR-007 §3 noise classification | Done (25 nodes in report.json) |
| Noise remediation executed in graph | **No** — report exists, writes not applied |
| `claim_promotion_confidence_ancient_person` threshold | **Missing** — ADR-007 §7.4 requires 0.75 |
| Person schema constraints in Neo4j | **None** |

---

## Phase 0 — Foundation: Schema, Noise Remediation, Threshold Registration

**Goal:** Clean the 25 noise nodes, register the missing threshold, add Person-related schema constraints and indexes so all subsequent phases write into a validated schema.

### 0.1 Execute noise remediation (ADR-007 §3)
- Apply `DQ_WRONG_ENTITY_TYPE` flag to 17 clear non-persons; reclassify `entity_type`; remove from person_ namespace consideration (do NOT apply `:Person` label)
- MythologicalPerson already applied to Romulus/Remus/Europa — verify `mythological=true` property and `DQ_UNRESOLVED_PERSONHOOD` flag are set
- Queue 5 `DQ_MISSING_P31` biblical persons for P31 re-fetch (Andrew the Apostle, Aristarchus, Damaris, Saint Peter's mother-in-law, Silas)

### 0.2 Register `claim_promotion_confidence_ancient_person` threshold
- Create `SYS_Threshold` node: name=`claim_promotion_confidence_ancient_person`, value=0.75, unit=score, decision_table=`D10_DETERMINE_claim_promotion_eligibility`, domain_scope=`ancient_person`

### 0.3 Add Person schema constraints & indexes
- Add to `01_schema_constraints_neo5_compatible.cypher`:
  - Uniqueness constraints for `:Person(entity_id)`, `:Gens(gens_id)`, `:Praenomen(praenomen_id)`, `:Nomen(nomen_id)`, `:Cognomen(cognomen_id)`, `:Tribe(tribe_id)`, `:Polity(polity_id)`, `:SocialOrder(order_id)`, `:PoliticalFaction(faction_id)`, `:Religion(religion_id)`, `:MilitaryBranch(branch_id)`, `:Rank(rank_id)`
- Add to `02_schema_indexes.cypher`:
  - Indexes on `:Person(dprr_id)`, `:Person(qid)`, `:Person(viaf_id)`, `:Gens(label_latin)`, `:Praenomen(label_latin)`, `:Nomen(label_latin)`, `:Cognomen(label_latin)`, `:Tribe(abbreviation)`
- Add to `03_schema_initialization.cypher`:
  - `SYS_HarvestPlan` node type registration in self-describing subgraph

**Deliverables:** Cypher migration files, executed against graph; threshold node created; noise remediation applied.

---

## Phase 1 — :Person Label Application (ADR-007 §2)

**Goal:** Apply the `:Person` label to all ~5,155 qualifying nodes (after noise exclusion). This is the foundational ontological assertion that every subsequent phase depends on.

### 1.1 Gate A — DPRR authority
```
MATCH (n:Entity) WHERE n.dprr_id IS NOT NULL
  AND n.entity_id STARTS WITH 'person_'
  AND NOT EXISTS { (n)-[:P31]->(m) WHERE m.label <> 'human' }
SET n:Person
```
Population: ~4,772 nodes

### 1.2 Gate B — Wikidata-confirmed humans in person_ namespace
```
MATCH (n:Entity)-[:P31]->(m {label: 'human'})
WHERE n.entity_id STARTS WITH 'person_'
  AND n.dprr_id IS NULL
  AND NOT EXISTS { (n)-[:P31]->(x) WHERE x.label <> 'human' }
SET n:Person
```
Population: ~383 nodes (minus those already labelled or vetoed)

### 1.3 Gate C — Namespace leak repair (concept_ → person_)
- Check for `entity_type='CONCEPT'` nodes with P31→human — apply `:Person` label and correct `entity_type` to `PERSON`
- Current count: 0 (already resolved), but write the query for idempotency

### 1.4 Veto check — verify no false positives
- Confirm the 17 `DQ_WRONG_ENTITY_TYPE` nodes were excluded
- Validate total `:Person` count ≈ 5,155–5,160

**Deliverables:** Python script `scripts/neo4j/adr007_apply_person_label.py` + Cypher file; validation report.

---

## Phase 2 — Layer 1: DPRR Label Parser (ADR-008 §3.1)

**Goal:** Build a deterministic grammar-based parser that extracts onomastic components from every DPRR label string. This is the foundation for Phase 3 (onomastic node creation) and feeds into the Layer 2 agent context packet.

### 2.1 Parser implementation
- Input: DPRR label string (e.g. `POMP1976 Cn. Pompeius (31) Cn. f. Sex. n. Clu. Magnus`)
- Output: structured dict with fields per ADR-008 §3.1 token table:
  - `gens_prefix`, `dprr_id`, `praenomen_abbrev`, `nomen`, `dprr_ordinal`, `filiation_chain[]`, `tribe_abbrev`, `cognomen[]`
- Handle edge cases: unknown praenomen (`-. f.`), multi-word nomina, absent tribe, absent cognomen, multiple cognomina
- Emit `DQ_UNKNOWN_GENS` flag for unknown gens prefixes

### 2.2 Validation pass
- Run parser against all 4,772 DPRR labels
- Generate report: success count, partial parse count, failure count, unknown gens prefixes
- Store parsed results as JSON for Phase 3 consumption

### 2.3 P-code → canonical relationship lookup table
- Implement the mapping table from ADR-008 §3.2 as a Python dict/JSON config
- P19→BORN_IN, P20→DIED_IN, P21→gender, P27→CITIZEN_OF, P102→MEMBER_OF_FACTION, P106→occupation, P140→HAS_RELIGION, P241→SERVED_IN, P410→HELD_RANK, P463→MEMBER_OF_FACTION, P509→cause_of_death, P1196→manner_of_death, P1343→DESCRIBED_BY, P2348→IN_PERIOD, P3716→IN_SOCIAL_ORDER, P5025→MEMBER_OF_GENS, P11491→MEMBER_OF_TRIBE

### 2.4 Date normalisation module
- ISO 8601 with negative years for BCE
- Wikidata precision integer → date field granularity (per ADR-008 §3.3 table)
- BCE→GEDCOM offset applied only at export, never stored

**Deliverables:** `scripts/federation/dprr_label_parser.py`, `scripts/federation/pcode_canonical_map.py`, `scripts/federation/date_normaliser.py`; parse report JSON in `output/person_cleanup/`.

---

## Phase 3 — Onomastic Node Creation & Wiring (ADR-007 §5)

**Goal:** Create the six first-class onomastic node types from DPRR label parse results (Phase 2 output), then wire every `:Person` node to its onomastic components.

### 3.1 Create reference nodes (MERGE semantics — no duplicates)
- `:Gens` nodes — extract unique gens from DPRR label prefixes (~500 estimated); set `gens_id`, `label_latin`, `gens_prefix`
- `:Praenomen` nodes — extract unique praenomina (~18 canonical Roman praenomina); set `praenomen_id`, `label_latin`, `abbreviation`
- `:Nomen` nodes — extract unique nomina; set `nomen_id`, `label_latin`, `gens_link`
- `:Cognomen` nodes — extract unique cognomina; set `cognomen_id`, `label_latin`
- `:Tribe` nodes — extract unique tribes (~35 Roman voting tribes); set `tribe_id`, `label_latin`, `abbreviation`

### 3.2 Wire Person → onomastic relationships
- `HAS_PRAENOMEN` — one per person (where known)
- `HAS_NOMEN` — one per person
- `HAS_COGNOMEN` — multiple permitted
- `MEMBER_OF_GENS` — one per person
- `MEMBER_OF_TRIBE` — one per person (where known)

### 3.3 Cross-check against Wikidata P-codes
- P5025 (MEMBER_OF_GENS) — cross-validate DPRR gens_prefix against Wikidata P5025 target
- P11491 (MEMBER_OF_TRIBE) — cross-validate DPRR tribe_abbrev against Wikidata P11491 target
- Log discrepancies as Type 1 (precision gap) or Type 4 (hard conflict) per ADR-007 §7.1

**Deliverables:** `scripts/neo4j/adr007_create_onomastic_nodes.py` + Cypher templates; validation report with node counts.

---

## Phase 4 — P-code → Canonical Relationship Promotion (ADR-007 §6)

**Goal:** Promote raw Wikidata P-code edges to canonical Chrystallum relationship types. Retain P-code edges as provenance.

### 4.1 Property promotions (P-code → literal on Person node)
- P21 → `gender` property (male/female from target Entity label)
- P106 → `occupation` property
- P509 → `cause_of_death` property
- P1196 → `manner_of_death` property

### 4.2 Relational promotions (P-code → canonical edge + target node type)
- P19 → `BORN_IN` → `:Place`
- P20 → `DIED_IN` → `:Place`
- P27 → `CITIZEN_OF` → `:Polity` (create :Polity nodes if needed)
- P102 / P463 → `MEMBER_OF_FACTION` → `:PoliticalFaction` (create nodes)
- P140 → `HAS_RELIGION` → `:Religion` (create nodes)
- P241 → `SERVED_IN` → `:MilitaryBranch` (create nodes)
- P410 → `HELD_RANK` → `:Rank` (create nodes)
- P2348 → `IN_PERIOD` → `:Periodo_Period` (existing nodes)
- P3716 → `IN_SOCIAL_ORDER` → `:SocialOrder` (create nodes)
- P1343 → `DESCRIBED_BY` (retain) + derive `HAS_ENTRY_IN` → `:ReferenceWorkEntry`

### 4.3 Family relationship enrichment
- Materialise `CHILD_OF` as inverse of FATHER_OF / MOTHER_OF (~2,582 new edges)
- Enrich `SPOUSE_OF` with: `start_year`, `end_year`, `end_reason`, `series_ordinal`
- Enrich `POSITION_HELD` with: `start_year`, `end_year`, `colleague_ids[]`, `location_id`, `source_id` (pre-populating for future OfficeHolding event node migration per OI-02)

### 4.4 Authority record linking
- `LINKED_VIA_AUTHORITY` → `:AuthorityRecord` (VIAF, LC, BNF, GND, Nomisma, DPRR)
- `SAME_AS` between AuthorityRecord nodes (where VIAF clusters link them)

**Deliverables:** `scripts/neo4j/adr007_promote_pcodes.py` + Cypher templates per relationship type; report on edges created/promoted.

---

## Phase 5 — Layer 2: Agent Reasoning Infrastructure (ADR-008 §4–6)

**Goal:** Build the PersonHarvestPlan infrastructure — context packet assembler, agent invocation wrapper, plan serialiser. This is the reasoning layer that does NOT write to the graph.

### 5.1 Context packet assembler
- Pre-fetch person_stub, existing_family, existing_offices, gens_network from graph
- Federation query runners for: dprr_raw, wikidata_raw, viaf_raw, fast_raw, nomisma_raw, trismegistos_raw, lgpn_raw
- Layer 1 output inclusion (parsed onomastic, normalised dates, P-code mappings)
- System policies & thresholds inclusion
- Size cap per federation source (OI-008-02)

### 5.2 PersonHarvestPlan data model
- Python dataclass / Pydantic model matching ADR-008 §4.2 field spec
- Fields: plan_id, person_entity_id, dprr_id, created_at, harvest_mode, sources_queried[], identity_resolution_decisions[], attribute_claims[], conflict_notes[], onomastic_parse, person_class, domain_scope, threshold_override, execution_status, resume_from_step, agent_model, reasoning_tokens

### 5.3 Agent reasoning wrapper
- Invoke LLM with context packet (per ADR-008 §4.3 constraints: no graph writes, no live graph access, no Cypher generation)
- Tasks: cross-federation name reconciliation, conflict type classification, authority tier weighting, filiation disambiguation, mythological classification, ConflictNote drafting
- Output: serialised PersonHarvestPlan

### 5.4 SYS_HarvestPlan node writer
- Store plan as graph node linked to target Person
- Idempotent: skip if plan_id already exists

**Deliverables:** `scripts/agents/person_harvest_agent.py` (context assembler + agent wrapper); `Python/models/person_harvest_plan.py` (data model); Cypher template for SYS_HarvestPlan.

---

## Phase 6 — Layer 3: Deterministic Execution Engine (ADR-008 §5)

**Goal:** Consume PersonHarvestPlan and execute all graph writes via schema-validated templates. 13-step idempotent execution sequence.

### 6.1 Write template library
- One Cypher template per operation type (create :Person, merge onomastic nodes, write literal properties, write relationships, write CHALLENGES_CLAIM, write ConflictNote, evaluate D10)
- Schema validation before write (type checks, direction checks, required fields)

### 6.2 Execution sequence runner
- Steps 1–13 per ADR-008 §5.2 dependency order
- Each step is idempotent and resumable
- `execution_status` tracking: PENDING → IN_PROGRESS → COMPLETE / FAILED / RESUMED
- `resume_from_step` for interrupted harvests

### 6.3 D10 threshold evaluation
- Evaluate claim promotion eligibility per D10 decision table
- Apply domain-scoped threshold override (0.75 for ancient_person vs 0.9 global)
- Respect `ApprovalRequired` policy — no auto-promotion; all go to Under Review

**Deliverables:** `scripts/agents/person_harvest_executor.py`; Cypher write templates in `scripts/neo4j/person_write_templates/`.

---

## Phase 7 — Conflict Resolution Infrastructure (ADR-007 §7)

**Goal:** Implement the conflict resolution structures and the Type 4 resolution ladder.

### 7.1 Graph structures
- `CHALLENGES_CLAIM` edge type (challenger_source, challenge_type, created_at)
- `ConflictNote` node type (conflict_type, attributes_in_dispute[], sources_involved[], tiebreaker_needed, resolution_status, ocd_applicable)
- `source_authority_tier` property on all claims (primary / secondary_academic / secondary_populist / tertiary)

### 7.2 Conflict classification
- Type 1 (precision gap) → accept higher-precision value; both as provenance
- Type 2 (silence) → write from covering source; no conflict
- Type 3 (soft conflict) → compute intersection; write as range
- Type 4 (hard conflict) → resolution ladder (authority weighting → tiebreaker → both as Proposed → human review)

**Deliverables:** Cypher templates for conflict structures; conflict classification module in `scripts/federation/conflict_resolver.py`.

---

## Phase 8 — Proof-of-Concept: Pompey (POMP1976) End-to-End Harvest

**Goal:** Full pipeline validation using the Pompey worked example from ADR-007 §9. This exercises every phase.

### 8.1 Harvest Pompey
- Layer 1: Parse DPRR label, normalise dates, map P-codes
- Layer 2: Agent reasons over DPRR + Wikidata + VIAF + LC + Nomisma + Trismegistos + LGPN
- Layer 3: Execute PersonHarvestPlan (all 13 steps)

### 8.2 Validate against ADR-007 §9 expected output
- Core node properties match (entity_id, qid, dprr_id, label, dates, gender, death details)
- Onomastic relationships match (HAS_PRAENOMEN→Gnaeus, HAS_NOMEN→Pompeius, HAS_COGNOMEN→Magnus, MEMBER_OF_GENS→Pompeia, MEMBER_OF_TRIBE→Clustumina)
- Civic/political match (CITIZEN_OF→Roman Republic, IN_SOCIAL_ORDER→nobilis, MEMBER_OF_FACTION→optimates + First Triumvirate)
- Family rels preserved (8 POSITION_HELD, 3 FATHER_OF, 5 SPOUSE_OF, 2 SIBLING_OF)
- Authority links created (VIAF, LC, Nomisma, Trismegistos, LGPN)

### 8.3 Family tree traversal test
- Traverse Pompey's paternal line (Cn. Pompeius Strabo → ancestors)
- Traverse spouse gens subgraphs (Iulia → Julius gens)
- Validate stopping conditions work

**Deliverables:** Validation report; any bug fixes from PoC execution.

---

## Phase Dependency Graph

```
Phase 0 (Foundation)
  ├──→ Phase 1 (Label Application)
  │      └──→ Phase 4 (P-code Promotion)
  │             └──→ Phase 7 (Conflict Resolution)
  └──→ Phase 2 (DPRR Parser / Layer 1)
         └──→ Phase 3 (Onomastic Nodes)
                └──→ Phase 5 (Layer 2 Agent)
                       └──→ Phase 6 (Layer 3 Executor)
                              └──→ Phase 8 (PoC Pompey)
```

Phases 1 and 2 can run in parallel after Phase 0.
Phases 3 and 4 can run in parallel once their respective prerequisites complete.
Phases 5–8 are sequential.

---

## Open Items Carried Forward

| ID | Item | Block? | Notes |
|----|------|--------|-------|
| OI-01 | StatusType semantics (values 1, 2) — 1,911 HAS_STATUS edges | Yes (for HAS_STATUS only) | Block HAS_STATUS enrichment until resolved |
| OI-02 | OfficeHolding event node migration | No | POSITION_HELD pre-populated with properties now |
| OI-03 | MythologicalPerson schema decision | No | 3 nodes held with DQ flag |
| OI-04 | OCD federation integration | No | ocd_id slot reserved |
| OI-06 | Ancient person threshold registration | **Phase 0** | 0.75 value; register as SYS_Threshold |
| OI-008-01 | SYS_HarvestPlan node type | **Phase 5** | Register in self-describing subgraph |
| OI-008-02 | Context packet size limits | **Phase 5** | Define max payload per federation source |
| OI-008-03 | Agent model selection | **Phase 5** | Record agent_model on plan |
| OI-008-05 | GEDCOM export agent | Post Phase 8 | Separate agent; reads PersonHarvestPlan |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| DPRR label parser fails on edge-case formats | Parser emits partial parse + DQ flag; agent reasons with available data |
| :Person label applied to non-humans | Veto condition runs AFTER gates; noise remediation runs BEFORE gates |
| Onomastic node duplication | MERGE semantics on `label_latin`; uniqueness constraints |
| Runaway family tree traversal | `max_new_nodes_production=1500` threshold (already in graph) |
| Agent non-determinism across runs | Record `agent_model` + context packet hash on SYS_HarvestPlan |
| Threshold too high for ancient persons | Domain-scoped override (0.75) registered in Phase 0 |
