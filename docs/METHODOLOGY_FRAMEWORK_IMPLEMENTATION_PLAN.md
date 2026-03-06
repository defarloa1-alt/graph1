# Methodology Framework Implementation Plan

**Purpose:** Step-by-step plan to (1) consolidate Chrystallum to one node, (2) add Framework as the unifying node for methodology overlays, and (3) implement Fischer, Milligan, and PRH in suggested order.

**Date:** 2026-03-05  
**Status:** Steps 0, 1, 2.1, 2.2 delivered; Steps 3–7 pending review

---

## Step 0: Chrystallum Consolidation

**Goal:** Exactly one Chrystallum node with `id: 'CHRYSTALLUM_ROOT'`.

### Step 0.1 — Create consolidation migration

**File:** `scripts/migrations/migration_chrystallum_consolidate.cypher`

**Actions:**
1. Ensure canonical node exists with `id: 'CHRYSTALLUM_ROOT'`
2. For each other Chrystallum node: copy outgoing relationships to canonical, then delete duplicate
3. Set canonical properties: `label`, `name`, `type`, `version`, `description`

**Output:** One Chrystallum node. All branches (HAS_FACET_CLUSTER, HAS_FEDERATION, etc.) attached to it.

### Step 0.2 — Fix scripts that use wrong MERGE keys

**Files to update:**
- `scripts/legacy/build_complete_chrystallum_architecture.py` — use `MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})` and SET name/version
- `scripts/legacy/rebuild_system_subgraph_correct.py` — same
- `scripts/backbone/system/generate_system_description.py` — `MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})` or `MATCH (c:Chrystallum)` (either works; prefer id)

**Verification:** `MATCH (c:Chrystallum) RETURN count(c)` → 1

---

## Step 1: Framework Node + HAS_FRAMEWORK Branch

**Goal:** Add Framework as the structural unifier for methodology overlays.

### Step 1.1 — Create Framework schema and link to Chrystallum

**File:** `scripts/migrations/migration_framework_schema.cypher`

**Actions:**
1. Create `:Framework` node type (no constraint yet; id is unique)
2. `MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})`
3. `MERGE (c)-[:HAS_FRAMEWORK]->(:Framework {id: 'FISCHER_LOGIC', label: 'Fischer Logic of Historical Thought', ...})`
4. `MERGE (c)-[:HAS_FRAMEWORK]->(:Framework {id: 'MILLIGAN_DIGITAL', label: 'Milligan Digital Hermeneutics', ...})`
5. `MERGE (c)-[:HAS_FRAMEWORK]->(:Framework {id: 'PRH_REPERTOIRE', label: 'PRH Patterns and Repertoires', ...})`

**Output:** Chrystallum has 3 Framework children. No content yet.

---

## Step 2: Fischer Fallacy Overlay (Phase 2)

**Goal:** Methodology cluster for Fischer's *Historians' Fallacies* — fallacies, TaskTypes, and agents can consult.

### Step 2.1 — Create Fischer schema

**File:** `scripts/migrations/migration_fischer_methodology.cypher`

**Node types:**
- `MethodologyText` (Fischer book)
- `MethodologicalDomain` (Inquiry, Explanation, Argument)
- `FallacyFamily` (e.g. Fallacies of Factual Significance)
- `Fallacy` (HOLIST_FALLACY, ESSENCE_FALLACY, etc.)
- `TaskType` (QUESTION_FRAMING, FACT_VERIFICATION, FACT_SIGNIFICANCE, CAUSATION, NARRATION, etc.)
- `MethodologicalPrinciple` (e.g. Popperian pattern-of-behavior)
- `ExampleCase` (optional)

**Relationships:**
- `(MethodologyText)-[:HAS_DOMAIN]->(MethodologicalDomain)`
- `(MethodologicalDomain)-[:HAS_FAMILY]->(FallacyFamily)`
- `(FallacyFamily)-[:HAS_FALLACY]->(Fallacy)`
- `(Fallacy)-[:GUARDS_TASKTYPE]->(TaskType)`
- `(Fallacy)-[:CONTRASTED_BY]->(MethodologicalPrinciple)`
- `(ExampleCase)-[:COMMITS_FALLACY_OF]->(Fallacy)`

**Link to Framework:**
- `(Framework {id:'FISCHER_LOGIC'})-[:CONTAINS]->(MethodologyText)`
- `(Framework)-[:CONTAINS]->(Fallacy)` for each fallacy
- `(Framework)-[:CONTAINS]->(TaskType)` for each TaskType

**Seed data:** 11 families, 5–10 core fallacies (holist, essence, aesthetic, quantitative, overgeneralization, monocausal), 11 TaskTypes.

### Step 2.2 — Create methodology linter module

**File:** `scripts/methodology/fischer.py` (package: `scripts/methodology/`)

**Functions:**
- `fetch_relevant_fallacies(task_types: list[str]) -> list[dict]` — Cypher query
- `detect_fallacy_hits(claim_text: str, fallacies: list) -> list[dict]`
- `sca_lint_claim(proposed_claim: dict) -> dict` — returns `{claim, fallacy_hits, status}`
- `narrative_lint_section(section: dict) -> dict`

**Integration:** SCA and narrative agents call `sca_lint_claim` / `narrative_lint_section` before emitting; optionally log `AgentTask` → `TRIGGERED_FALLACY` to graph.

---

## Step 3: Agent Gaps (Phase 1)

**Goal:** Address discipline-universe gaps so facet agents can coordinate harvests.

### Step 3.1 — Define harvest job schema

**File:** `docs/agents/HARVEST_JOB_SCHEMA.md` (or add to existing discipline spec)

**Schema:**
```json
{
  "job_id": "string",
  "discipline_qid": "string",
  "facet": "string",
  "repo_key": "string",
  "url": "string",
  "status": "pending|running|completed|failed",
  "created_at": "ISO8601"
}
```

### Step 3.2 — Add facet-scoped harvest state (optional)

**Options:**
- Add `needs_harvest_per_facet` property on Discipline (JSON map) or
- Add `HarvestJob` nodes in Neo4j with `(Discipline)-[:HARVEST_JOB]->(HarvestJob)-[:FOR_FACET]->(CanonicalFacet)`

**Decision:** Start with JSON schema + HarvestJob nodes; defer `needs_harvest_per_facet` if not needed yet.

### Step 3.3 — Multi-facet coordination (lightweight)

**File:** Add to `docs/agents/FACET_AGENT_COORDINATION.md`

**Protocol:** When discipline X is primary for facets A, B, C, first agent to claim a harvest job for (X, A) locks it; others skip or wait. Use `HarvestJob.status` as lock.

---

## Step 4: Milligan Digital Hermeneutics (Phase 3)

**Goal:** Overlay for digital evidence constraints — search bias, OCR skepticism, scale reflexivity, etc.

### Step 4.1 — Create Milligan schema

**File:** `scripts/migrations/migration_milligan_digital.cypher`

**Node types:**
- `DigitalPrinciple` (6 nodes: SEARCH_BIAS_AWARENESS, SCALE_REFLEXIVITY, INFRASTRUCTURE_LITERACY, OCR_AND_METADATA_SKEPTICISM, PLATFORM_DEPENDENCE_TRANSPARENCY, ALGORITHMIC_MODESTY)

**Relationships:**
- `(MethodologyText {id:'MILLIGAN_TRANSFORMATION'})-[:HAS_PRINCIPLE]->(DigitalPrinciple)`
- `(DigitalPrinciple)-[:IMPOSES_CONSTRAINT_ON]->(TaskType)`
- `(DigitalPrinciple)-[:HIGHLIGHTS_RISK_IN]->(FederationSource)` (where applicable)
- `(DigitalPrinciple)-[:INTENSIFIES_RISK_OF]->(Fallacy)` (e.g. SEARCH_BIAS → PRAGMATIC_FALLACY)

**Link to Framework:**
- `(Framework {id:'MILLIGAN_DIGITAL'})-[:CONTAINS]->(DigitalPrinciple)`

### Step 4.2 — Wire constraints to TaskTypes

**Actions:** Create `IMPOSES_CONSTRAINT_ON` edges from each DigitalPrinciple to relevant TaskTypes (FACT_SIGNIFICANCE, FACT_VERIFICATION, etc.).

---

## Step 5: PRH Repertoire Layer (Phase 4)

**Goal:** Event classification via patterns and mechanisms — contentious assembly, urban riot, etc.

### Step 5.1 — Create PRH schema

**File:** `scripts/migrations/migration_prh_repertoire.cypher`

**Node types:**
- `RepertoirePattern` (RP_CONTENTIOUS_ASSEMBLY, RP_URBAN_RIOT, RP_MUSHROOM_STRIKE, RP_GENERAL_STRIKE, RP_PROCESSION_DEMONSTRATION, RP_OCCUPATION)
- `RepertoireFamily` (optional grouping)
- `Mechanism` (M_ESCALATION, M_DIFFUSION, M_BROKERAGE, M_POLICING_RESPONSE, M_FRAME_ALIGNMENT)

**Relationships:**
- `(RepertoireFamily)-[:HAS_PATTERN]->(RepertoirePattern)`
- `(RepertoirePattern)-[:USES_MECHANISM]->(Mechanism)`
- `(Event)-[:INSTANCES_PATTERN]->(RepertoirePattern)`
- `(Event)-[:OPERATES_VIA]->(Mechanism)`

**Link to Framework:**
- `(Framework {id:'PRH_REPERTOIRE'})-[:CONTAINS]->(RepertoirePattern)`
- `(Framework)-[:CONTAINS]->(Mechanism)`

**Seed events:** 2–3 Roman examples (Gracchan contio 133 BCE, Gracchan riot, Caesar-era assembly) with INSTANCES_PATTERN and OPERATES_VIA.

### Step 5.2 — Create repertoire classifier

**File:** `scripts/agents/repertoire_classifier.py`

**Functions:**
- `classify_event(event: dict) -> list[dict]` — returns suggested patterns and mechanisms
- `assign_patterns_to_event(event_id: str, patterns: list[str])` — writes to Neo4j

---

## Step 6: AgentTask Runtime Binding (Phase 6)

**Goal:** Runtime node that ties frameworks together when an agent runs.

### Step 6.1 — AgentTask schema (if not exists)

**File:** `scripts/migrations/migration_agent_task.cypher` (or add to Fischer migration)

**Node:** `AgentTask {id, kind, created_at}`

**Relationships:**
- `(AgentTask)-[:USES_TASKTYPE]->(TaskType)`
- `(AgentTask)-[:CONSULTED_FRAMEWORK]->(Framework)`
- `(AgentTask)-[:TRIGGERED_FALLACY {reason, status}]->(Fallacy)` (when linter flags)
- `(AgentTask)-[:APPLIED_PRINCIPLE]->(DigitalPrinciple)` (when digital constraint applied)

**Usage:** Agent creates AgentTask at start; attaches TaskTypes, consults frameworks, logs TRIGGERED_FALLACY / APPLIED_PRINCIPLE as it runs.

---

## Step 7: CIDOC-CRM Alignment (Phase 5 — Optional)

**Goal:** Document mapping for standards compliance; no schema changes.

**File:** `docs/CHRYSTALLUM_CIDOC_MAPPING.md`

**Content:** Mapping table from plan (Chrystallum concept → CRM/CRMinf class), URI patterns, RDF class mappings. Can be done incrementally.

---

## Execution Order Summary

| Step | Description | Deliverable |
|------|-------------|-------------|
| 0.1 | Chrystallum consolidation migration | `migration_chrystallum_consolidate.cypher` |
| 0.2 | Fix scripts that use wrong MERGE keys | 3 Python files updated |
| 1.1 | Framework schema + HAS_FRAMEWORK branch | `migration_framework_schema.cypher` |
| 2.1 | Fischer methodology schema + seed | `migration_fischer_methodology.cypher` |
| 2.2 | Methodology linter module | `methodology_linter.py` |
| 3.1–3.3 | Agent gaps (harvest job, coordination) | 2 docs + optional HarvestJob nodes |
| 4.1–4.2 | Milligan digital principles | `migration_milligan_digital.cypher` |
| 5.1–5.2 | PRH repertoire patterns | `migration_prh_repertoire.cypher` + `repertoire_classifier.py` |
| 6.1 | AgentTask runtime binding | Add to Fischer or separate migration |
| 7 | CIDOC-CRM mapping doc | `CHRYSTALLUM_CIDOC_MAPPING.md` |

---

## Review Checklist

- [ ] Step 0: Consolidation is safe (no data loss; relationships preserved)
- [ ] Step 1: Framework nodes are under Chrystallum; no duplicate branches
- [ ] Step 2: Fischer fallacies and TaskTypes are sufficient for SCA/narrative
- [ ] Step 3: Harvest job schema is minimal; coordination protocol is clear
- [ ] Step 4: Digital principles map correctly to TaskTypes
- [ ] Step 5: Repertoire patterns cover Gracchi/Caesar use cases
- [ ] Step 6: AgentTask is optional for MVP; can defer logging until Phase 6

---

## Execution Status

| Step | Status | Deliverable |
|------|--------|-------------|
| 0.1 | Done | `scripts/migrations/migration_chrystallum_consolidate.cypher` |
| 0.2 | Done | `build_complete_chrystallum_architecture.py`, `rebuild_system_subgraph_correct.py`, `FEDERATION_REGISTRY_REBUILD_SPEC.md` updated |
| 1.1 | Done | `scripts/migrations/migration_framework_schema.cypher` |
| 2.1 | Done | `scripts/migrations/migration_fischer_methodology.cypher` |
| 2.2 | Done | `scripts/methodology/fischer.py` (package) |
| 3.1–3.3 | Done | `docs/agents/HARVEST_JOB_SCHEMA.md`, `FACET_AGENT_COORDINATION.md` |
| 4.1–4.2 | Done | `migration_milligan_digital.cypher`, `scripts/methodology/milligan.py` |
| 5.1–5.2 | Done | `migration_prh_repertoire.cypher`, `scripts/methodology/prh.py`, `repertoire_classifier.py` |
| 6 | Pending | — |
| 7 | Done | `docs/CHRYSTALLUM_CIDOC_MAPPING.md` |

## Run Order

```bash
# 1. Consolidate Chrystallum (if you have multiple nodes)
#   :source scripts/migrations/migration_chrystallum_consolidate.cypher

# 2. Add Framework branch
#   :source scripts/migrations/migration_framework_schema.cypher

# 3. Add Fischer methodology
#   :source scripts/migrations/migration_fischer_methodology.cypher

# 4. Add Milligan digital principles
#   :source scripts/migrations/migration_milligan_digital.cypher

# 5. Add PRH repertoire patterns
#   :source scripts/migrations/migration_prh_repertoire.cypher

# 5b. Extend PRH (from prh.pdf index)
#   :source scripts/migrations/migration_prh_repertoire_extend.cypher
```

## Next Action

Step 6 (AgentTask runtime binding).
