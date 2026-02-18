# Chrystallum v0 — SCA Bootstrap, Scaffolding, and Promotion Spec

Status: **Implementation-ready v0** (consolidated from the 2026-02-17 design discussion)

This document is a *repo-facing contract* for the development team. It defines: (1) how a subject-area SCA is instantiated and bootstrapped from a Wikidata QID, (2) how scaffolding is persisted in Neo4j without contaminating the canonical graph, and (3) how promotion transforms scaffold artifacts into canonical nodes/relationships/claims.

Primary canonical reference remains: **`Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`**.

Status note:
- This `2-17` document is a design input and implementation contract draft.
- Canonical normative architecture text is maintained in the consolidated document.

---

## 1. Terms and roles

### 1.1 Concierge (router)
A lightweight routing function (may be implemented as an agent) that:
- Interprets user input into one of the supported flows (bootstrap / schema query / data query / system-doc question).
- For subject instantiation, resolves or accepts a **Wikidata QID** and triggers SCA bootstrap.

Important: once a subject is active, the **SCA acts as the concierge for that subject** (i.e., there is no long-lived “separate concierge agent” requirement in v0). Future versions may re-introduce a separate long-lived concierge layer.

### 1.2 SCA (Subject Concierge Agent)
One SCA exists per subject area. v0 assumes “broad discipline” subjects (e.g., Roman Republic), so **all facet agents may be instantiated**, but the first phase is *structural*, not interpretive.

Responsibilities:
- Own the subject scope keyed by a seed QID (or a curated equivalent).
- Run structural bootstrap and store scaffolding artifacts.
- Coordinate (later) interpretive reading tasks for SFAs.
- Never directly write canonical graph facts except through explicit promotion.

### 1.3 SFA (Subject Facet Agents)
Facet agents propose:
- Candidate claims (interpretive assertions)
- Candidate subject concepts (granularity proposals)
- Candidate scaffold edges (`ScaffoldEdge`) with provenance

They do **not** canonize and do not write canonical labels directly in v0.

### 1.4 Query Executor (Neo4j)
A separate capability/agent that:
- Answers questions about schema and data via Cypher
- Always uses safe query patterns (LIMIT, capped traversal depth)
- Does not mutate the graph unless explicitly running an approved “promotion” or “bootstrap run write” procedure.

---

## 2. v0 scope and priority use cases

Supported, in priority order:
1) **SCA bootstrap from QID** (structural setup)
2) Queries about **our system** (architecture/policy; no graph mutation)
3) Queries about **Neo4j schema** (labels, constraints, indexes, rel types)
4) Queries about **Neo4j data** (read-only Cypher)

Deferred / enhancement:
- Fully general “free-text concierge” that decides SCAs and granularity from arbitrary user text. v0 may still do minimal QID resolution + best-match-to-existing.
- Autonomous density-driven orchestration (dynamic SFA allocation, subagent auto-spawn, and bridge-triggered routing) is deferred to v1+.

---

## 3. Canonical vs scaffold boundary (hard rule)

### 3.1 Canonical graph
Contains only promoted content:
- Canonical main node labels (SubjectConcept, Human, Event, Place, Period, etc.)
- Canonical relationship types (from `relationship_types_seed.cypher`)
- Claim, Review, ReasoningTrace, ProposedEdge, Synthesis, etc. per Claims Layer

Canonical facet assessment topology:
- `(:Claim)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun)-[:HAS_FACET_ASSESSMENT]->(:FacetAssessment)`

### 3.2 Scaffold graph (in Neo4j)
We will **persist scaffolding as real nodes in Neo4j**, but under **distinct scaffold labels** so we never collide with canonical uniqueness constraints.

Key decision: **Single scaffold node per (analysis_run_id, qid)**.

Scaffold artifacts are queryable/visualizable and support smoke-test iteration without polluting canonical truth.

---

## 4. Bootstrap pipeline (structural, bounded)

Bootstrap produces four outputs:
A) Seed dossier  
B) Upward hierarchy spine (P31/P279 up)  
C) Lateral neighborhood (mapped properties)  
D) Downward children pass (inverse P279 depth 2 + optional inverse P31 sampling)

All outputs are written into the scaffold layer for the associated **AnalysisRun**.

### 4.1 Shared caps and filters (v0 defaults)
- `max_up_levels` = **4** (P31 + P279 upward)
- `lateral_hops` = **2** (seed → hop1 → hop2)
- `down_subclass_depth` = **2** (inverse P279)
- `instances_mode` = **sampling only** (inverse P31), never exhaustive
- `per_property_cap` (forward/backlink property fanout): **25** default
- `per_node_neighbor_cap` (lateral adjacency): **200** default
- `per_parent_child_cap` (down subclasses): **50** default

NOT filters (applied at least in downward pass; recommended everywhere):
- Disambiguation items
- Wikimedia categories
- Pure encyclopedia/dictionary “article about X” nodes (unless explicitly needed as evidence)
- Other non-entity wrappers that are not intended for canonization

### 4.1.1 Backlink density metric source (v0 guardrail)
For v0 decisions and automation, backlink-density metrics MUST be computed from the bounded scaffold outputs of the current AnalysisRun:
- use mapped properties only (same rule as lateral traversal)
- respect all runtime caps (per_property_cap, per_node_neighbor_cap, per_parent_child_cap)
- prefer run-local / domain-local counts over uncapped global counts

Unrestricted global Wikidata backlink totals may be stored for diagnostics, but are non-authoritative in v0 decisioning.

### 4.2 A — Seed dossier (Q0)
Input: seed QID Q0 (explicitly provided or resolved)

Collect:
- Core properties (forward)
- External IDs (for federation alignment signals)
- Bounded backlinks restricted to properties that map into our canonical relationship set

Write:
- AnalysisRun node for this bootstrap
- ScaffoldNode(Q0)
- Optional SeedDossier node linked to ScaffoldNode(Q0)
- ScaffoldEdge records for backlinks (as described in §6)

### 4.3 B — Upward hierarchy (P31 + P279), depth 4
For each frontier node:
- Collect P31 objects (instance of)
- Collect P279 objects (subclass of)

Depth: 4 “levels up”.

Meta-ceiling:
- If the climb reaches ontology/meta constructs (e.g., concept/class/metaclass/second-order class), mark the ceiling and stop expanding upward through that node.
- These nodes may exist in scaffold for traceability, but should not be auto-promoted.

Write:
- ScaffoldNodes for discovered parents
- ScaffoldEdges with metadata `{up_level: 1..4, wd_property: P31|P279}`

### 4.4 C — Lateral neighborhood (mapped properties only), 2 hops
Only traverse Wikidata properties that have an explicit mapping into our canonical relationship types.

Hop 1:
- Expand from Q0 along mapped properties (forward + inverse mappings permitted)
Hop 2:
- Expand from hop-1 nodes similarly

Write:
- ScaffoldNodes for newly discovered QIDs
- ScaffoldEdges with `{hop: 1|2, wd_property, direction, caps_applied}`

### 4.5 D — Downward children pass (Option B selected)
Runs on:
- Seed Q0
- The “type parents” surfaced during the upward pass
- **Hop-1 neighbors** from the lateral pass (Option B)

D1 — Subclass children:
- Inverse P279, depth **2**
- Enforce `per_parent_child_cap`
- Apply NOT filters
- Write ScaffoldEdges with `{down_depth: 1|2, wd_property: P279}`

D2 — Instance sampling:
- Inverse P31, **sample only**
- Only run for selected class-like nodes (heuristics: node degree, mapped-property density, or explicit allowlist)
- Write ScaffoldEdges with `{sampled: true, wd_property: P31}`

---

## 5. Granularity governance and “profession ceiling”

v0 policy for professions/occupations:
- We do **not** introduce “Occupation” as a first-class node label.
- Professions/occupations are represented as **SubjectConcept** (canonical) when promoted.
- Human-to-profession associations require temporal bounds (use the system’s temporal envelope model).

Bootstrap and promotion guidance:
- It is acceptable to build a profession subgraph in scaffold.
- Promotion should **stop at a “profession level” ceiling** (avoid promoting meta-ontology parents).
- Meta-ceiling and NOT filters apply strictly.

Rationale:
- Occupation is time-spanning and often derived from roles/periods; the canonical model needs temporality and governance rather than a naive label import.

---

## 6. Neo4j scaffold persistence model

### 6.1 AnalysisRun
Use the canonical **:AnalysisRun** node (already defined in CONSOLIDATED.md) to anchor the run:
- `run_id` (string; use as `analysis_run_id`)
- `created_at`, `updated_at`
- `pipeline_version`
- `seed_qid`
- `params_json` (caps, filters, toggles)

### 6.2 ScaffoldNode (new supporting node label)
Label: `:ScaffoldNode`

Uniqueness identity:
- `(analysis_run_id, qid)`

Required properties:
- `analysis_run_id` (string)
- `qid` (string)
- `wd_label` (string)
- `intended_label` (string; canonical label target, e.g., SubjectConcept/Human/Event/Place/Period/Organization/etc.)
- `source` (e.g., `wikidata_entitydata`)
- `created_at`

Optional properties:
- `kind_hint` (e.g., `class_like`, `instance_like`, `profession_candidate`)
- `ceiling_hit` (bool)
- `not_filtered_reason` (string; if excluded from promotion)

Rule:
- Do **not** apply canonical labels to scaffold nodes.

### 6.3 ScaffoldEdge (scaffold-only edge-as-node)
Use **`:ScaffoldEdge`** for bootstrap and scaffold expansion outputs.
Do not reuse canonical `:ProposedEdge` for scaffold persistence.

Endpoints:
- `(e:ScaffoldEdge)-[:`FROM`]->(s:ScaffoldNode)`
- `(e:ScaffoldEdge)-[:`TO`]->(o:ScaffoldNode)`

Required ScaffoldEdge properties (v0):
- `edge_id` (deterministic string)
- `analysis_run_id`
- `relationship_type` (string; canonical relationship type that would be created on promotion)
- `wd_property` (string; e.g., `P279`)
- `direction` (`forward`|`inverse`|`symmetric`)
- `confidence` (float)
- `created_at`

Context properties:
- `hop` (1|2) for lateral edges
- `up_level` (1..4) for upward hierarchy
- `down_depth` (1..2) for subclass children
- `sampled` (bool) for instance sampling
- `caps_applied` (json/string note)
- `truncation_note`

### 6.4 Evidence and reasoning trace attachment
Evidence attaches at scaffold time to:
- ScaffoldEdge (structural evidence: WD statements, backlinks, etc.)
- ReasoningTrace (why a selection, why a cap stopped, why a node was excluded, etc.)

Promotion must carry forward evidence into canonical Claims where applicable.

---

## 7. Promotion model (scaffold → canonical)

Promotion is an explicit, logged operation.

Input:
- `analysis_run_id` plus a selection of scaffold nodes/edges (or “promote all eligible from run”)

Steps:
1) Validate nodes against NOT filters and meta-ceiling policy
2) Treat density/centrality as ranking signals only; density alone must never bypass promotion governance
3) MERGE canonical nodes (by canonical unique keys, typically QID where applicable)
4) CREATE canonical relationships (only relationship types that exist in the canonical relationship set)
5) Create Claim nodes for interpretive assertions (SFA outputs) and attach evidence
6) Record PromotionEvent (recommended) linking promoted artifacts back to the run and to source ScaffoldEdges
7) For structural scaffold assertions, map selected `:ScaffoldEdge` records into canonical `:ProposedEdge` and/or canonical relationships per promotion policy

Scaffold artifacts remain for audit and debugging.

---

## 8. v0 acceptance criteria (engineering)

A bootstrap run is considered successful if:
- It creates exactly one AnalysisRun (run_id) and uses it consistently everywhere.
- It creates at most one ScaffoldNode per (run_id, qid).
- It emits ScaffoldEdge edge-as-node records for all discovered relationships.
- It respects all caps/filters and records truncation metadata.
- It runs repeatedly without altering canonical nodes/relationships (unless promotion explicitly invoked).
- Promotion can be invoked for a small selected subset and creates canonical nodes/relationships without constraint violations.
- Any density metric used in v0 is traceable to mapped/capped scaffold outputs for the run.

---

## 9. Open items (explicitly decided for v0)
- Downward subclass depth: **2**
- Downward anchor scope: **Option B** (seed + type parents + hop-1 neighbors)
- Scaffold persistence: **in Neo4j as real nodes**
- Scaffold identity: **single per run**
- Subject routing ownership: active subject SCA acts as concierge for that subject (v0 policy)
- Subagent behavior: proposal-only in v0 (no autonomous spawning)
- v1 threshold policy direction: categorized + normalized density with cooldown/hysteresis; numeric defaults to be calibrated

---

## Appendix A — Relationship mapping
All lateral expansion requires an explicit mapping from Wikidata property → canonical relationship type (and direction), sourced from the canonical relationship list.

In v0: **no mapped property → no lateral traversal**.

---

## Appendix B - v1 draft (non-normative): categorized density and facet federation

This appendix is implementation guidance for v1+ and does not change v0 acceptance criteria.

### B.1 Categorized density trigger model
For each SubjectConcept `sc` in a facet domain, maintain:
- `backlinks_by_type[type]` (PERSON, EVENT, WORK, OBJECT, MATERIAL, etc.)
- `backlinks_by_facet[facet_key]`
- optional `by_type_and_facet[type][facet_key]`

Subagent proposals should be category-scoped and must satisfy all three checks:
1) Absolute floor for the category bucket
2) Relative density threshold (facet-local percentile)
3) Stability controls (cooldown + hysteresis)

Density remains a routing/prioritization signal and never bypasses promotion governance.

### B.2 Facet federation execution binding
Use the matrix in `Facets/facet_federation_matrix.json` with facet keys from `Facets/facet_registry_master.json`.

Execution order:
1) Run all primary adapters for a facet (required coverage path)
2) Run secondary adapters for enrichment (optional coverage path)
3) Persist adapter provenance and per-facet coverage metrics

Implementation checklist is tracked in:
- `md/Architecture/2-17-26-Facet-Federation-Action-Plan.md`
