# Clean-Start Implementation Plan

## 1. Objective

Prove the revised architecture with the smallest useful vertical slice.

Do not begin by rebuilding the former agent ecosystem, importing every
authority, or reproducing the old schema. Begin with the temporal backbone and
one historical example.

## 2. Phase 0: inspect and freeze the starting database

Before writing application code:

1. Connect to the local `neo4j` database.
2. Record the actual labels, properties, indexes, constraints, and temporal
   relationship names.
3. Confirm the year sign convention.
4. Confirm the database contains only the intended temporal backbone.
5. Export a small read-only schema snapshot for this revision.

This phase is observational. Do not alter the database merely to make it match
the documents.

**Status: complete.** The local `neo4j` database contains only the validated
Year/FOLLOWED_BY backbone. `Year.year` is the canonical numeric property; year
zero is intentionally absent; and `-1 → 1` is the valid BCE-to-CE transition.

## 3. Phase 1: minimal graph schema

Add only:

- `Entity`;
- `Subject`;
- `AuthorityRecord`;
- `SourceObservation`;
- `Assertion`;
- `Proposal`;
- the existing `Year` structure.

Add uniqueness constraints for local IDs and external authority identifiers.
Avoid creating every possible label or relationship type in advance.

**Phase 1 schema artifact:** [10-PHASE-1-SCHEMA.cypher](10-PHASE-1-SCHEMA.cypher).

**Status: complete.** The eight minimum uniqueness constraints are online in
the local `neo4j` database. The application created no data nodes or
relationships; the validated temporal backbone remains unchanged. See
[11-PHASE-1-RESULTS.md](11-PHASE-1-RESULTS.md).

## 4. Phase 2: one end-to-end example

Use the Battle of Actium as the first example:

```text
Create or reuse event entity
  → connect it to 31 BCE
  → create or reuse Subject
  → attach one Wikidata authority record
  → record one source observation
  → create one participation assertion
  → review and accept one proposal
```

The example is successful only if the graph can distinguish:

- the historical event;
- the subject about the event;
- the external authority record;
- the source observation;
- the local assertion;
- the accepted decision.

**Status: complete.** The direct Battle of Actium slice implements one
accepted, provenance-bearing participation assertion without an agent. See
[12-PHASE-2-ACTIUM.md](12-PHASE-2-ACTIUM.md).

## 5. Phase 3: direct queries before agents

Implement and test direct graph operations before adding an SCA or SFA:

- create or reuse an entity;
- create or reuse a subject;
- link a subject to its focus entity;
- link an entity to a year;
- attach an authority record;
- record a source observation;
- submit a proposal;
- accept or reject a proposal;
- retrieve provenance for an accepted assertion.

This proves that the model works independently of any particular orchestration
framework or language model.

**Status: complete.** The reusable parameterized direct operations were
replayed against the Actium slice without changing graph counts. Provenance,
proposal status, and derived temporal context were also verified. See
[13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher)
and [14-PHASE-3-RESULTS.md](14-PHASE-3-RESULTS.md).

The operations were hardened on 2026-10-11 with guarded writes, a proposal
lifecycle, and a live rolled-back test suite.

## 6. Phase 4: authority adapters

Add one authority adapter at a time:

1. Wikidata for identity discovery;
2. LCSH or FAST for subject access;
3. Pleiades for ancient places;
4. PeriodO for period context.

Each adapter must:

- preserve the raw response outside the domain graph when appropriate;
- create a source observation;
- record retrieval time and source revision;
- be safe to retry;
- expose failure or stale status;
- avoid silently turning candidates into accepted claims.

**Status: Wikidata identity discovery complete.** The first bounded adapter
preserves search/entity responses and returns candidate identities plus a
revision-backed source-observation draft, without writing accepted graph
knowledge. See [15-PHASE-4-WIKIDATA-IDENTITY.md](15-PHASE-4-WIKIDATA-IDENTITY.md).

## 6.5 Phase 4.5: legacy triage and adoption boundary

Before reusing an existing script, agent, schema, data file, document, or UI
component, classify it as `ADOPT`, `ADAPT`, `REFERENCE`, `ARCHIVE`, or
`EXCLUDE`. Do not bulk-move the legacy repository into the clean-start area,
and do not run legacy writes against the local clean-start database.

**Status: first-pass triage complete.** The register identifies the active
clean-start contract, candidate areas for future adaptation, archive-only
legacy areas, and excluded generated material. See
[16-LEGACY-TRIAGE.md](16-LEGACY-TRIAGE.md).

## 7. Phase 5: proposal workflow

Only after direct operations work should agents be introduced.

The first agent workflow should be minimal:

```text
Agent proposes
  → proposal stored
  → validation checks
  → human or SCA review
  → accepted assertion committed
```

The agent must not write directly to the accepted graph.

**Status: workflow complete; LLM proposer pending.** `ProposalDraft`, the
`predicates-v1` registry, the deterministic validator, storage, curator
review, and a deterministic Wikidata proposer are implemented and replay-tested
against the Actium observations. See
[18-PHASE-5-PROPOSALS.md](18-PHASE-5-PROPOSALS.md).

Workflow checkpoints, retries, locks, and job state should be stored outside
the durable historical graph. Raw authority payloads should also be stored
outside Neo4j, with references from source observations.

## 8. Phase 6: front-door orchestration

After the direct proposal path works, add a small front-door agent. Its first
responsibility is not research; it is to turn an ambiguous user request into a
typed inquiry plan.

For example, "Graph Bismark" may refer to Otto von Bismarck, the German
battleship, or another namesake. The front door should produce candidates and
an inquiry plan rather than silently choosing an identity.

```text
User request
  → Concierge and Command Agent (CCA)
  → InquiryPlan
  → existing Subject or SCA factory
  → proposals
  → deterministic validation
  → CommitCommand
  → Neo4j transaction
```

The CCA must not research, adjudicate historical claims, or commit graph
knowledge. Its output should identify:

- the user goal;
- candidate entities or subjects;
- ambiguity requiring clarification;
- the SCA workflow or workflows to invoke;
- selected facet applications;
- budget and stopping conditions;
- tools that may be used.

The CCA is optional for direct administrative or scripted operations. The
underlying graph commands must remain usable without a conversational agent.

## 9. Phase 7: temporal qualification

Extend the temporal model only when the Actium example or another concrete
example requires it:

- uncertain dates;
- date ranges;
- day or month precision;
- active roles;
- place attestations;
- period definitions.

Every temporal extension must preserve the existing ability to query by year.

**Requirements recorded 2026-10-12.** Many predicates need date spans, and
year granularity is not enough.

- **Where:** temporal qualifiers are properties of the Assertion, which is the
  reified relationship, and display as properties of the edge. Unlike plain
  relationship properties, this lets two sources give different dates for the
  same relationship as separate claims with their own evidence.
- **Spans:** start and end, each optionally with earliest and latest bounds
  ("married between 37 and 36 BCE").
- **Precision below the year:** day, month, season, year, decade, circa,
  using EDTF (ISO 8601-2) for exact, approximate, uncertain, and interval
  values (`-0031-09-02`, `-0037~/-0036`).
- **Relative time** for micro-events, anchored to an event ("the fifth day",
  "the sixth hour").
- **Source dating preserved separately from normalization:** consular years
  ("cos. 32"), pre-Julian Roman calendar dates, regnal years. A converted
  date such as "Sept. 2, 31 B.C." is a modern normalization (Perrin's note,
  not Plutarch).
- **Year backbone kept for navigation:** a span links to the Year nodes it
  touches, so year queries and the timeline slider keep working; finer
  detail lives in the properties.
- **Per predicate in the registry:** which predicates require a span (offices,
  marriages, alliances, `heldAuthorityOver`, command in a capacity) and their
  typical precision, extending the existing `temporalQualification` flag.

## 10. Phase 8: governance and self-description

Only after the core graph and proposal workflow are stable should the system
add a governance registry for:

```text
ArchitectureVersion
AgentDefinition
PromptVersion
OutputSchema
PredicateDefinition
NodeTypeDefinition
LifecycleMachine
TransitionRule
PolicyRule
MappingRule
AuthorityDefinition
ToolDefinition
AccessRole
TestCase
```

This registry can live in Neo4j or a separate configuration store, but it must
not be the sole trust anchor for its own validation. A versioned, externally
controlled bootstrap manifest should contain the minimum constitution, trusted
root IDs, schema hashes, allowed tools, and last-known-good prompt versions.

## 11. Acceptance criteria

The clean-start model is ready for broader use when it can demonstrate:

1. stable local IDs independent of Wikidata IDs;
2. no duplicate entities on retry;
3. a distinct Subject for a historical entity;
4. source observations preserved independently of local claims;
5. accepted and rejected proposals remain distinguishable;
6. provenance can be followed from claim to source;
7. the year backbone remains queryable;
8. missing external data does not prevent local modeling;
9. a failed authority request leaves an explicit failure or stale state;
10. the graph can be read without starting an agent workflow.
11. a bounded path query can trace across at least three entity kinds;
12. every returned path hop exposes its predicate, status, and evidence link;
13. inferred or contested paths are visibly distinguished from accepted paths.
14. a second historical domain can use the unchanged core claim and provenance
    workflow with a different federation profile.
15. a future source-ingestion test can use a machine-readable scholarly index
    as a finding aid without promoting index entries directly to claims.

## 12. Deferred work

Do not add these until the acceptance criteria pass:

- full facet routing;
- autonomous SCA/SFA round-robin operation;
- broad recursive enrichment;
- complete LCC/LCSH/FAST hierarchy import;
- full CIDOC CRM projection;
- SHACL export validation;
- graph analytics for promotion decisions;
- complex UI review surfaces;
- large-scale historical ingestion.
- self-modifying or autonomous governance rules;
- unrestricted MCP or generated graph mutations.
- domain packs and capability-based federation selection;
- broad historical inquiries that create subject constellations;
- machine-readable index harvesting and source-led passage retrieval.
- multilingual and source-perspective modeling for complex documentary
  traditions.

The purpose of deferral is not to discard those capabilities. It is to ensure
that each one is built on a working core rather than compensating for an
unclear model.

## 13. Enhancement backlog

Enhancement requests should be recorded here rather than inserted into the
active phase sequence. Each item remains deferred until a concrete use case,
acceptance test, and dependency are identified.

### E1. Historical scope classification

Add a CCA `ScopeDecision` before entity resolution:

```text
IN_SCOPE
OUT_OF_SCOPE
REFRAME_REQUIRED
```

The classifier should distinguish historical graph construction from
procedural instruction, current advice, nonhistorical lookup, and unsupported
operations. It should offer historically framed alternatives without
answering an out-of-scope procedural request.

**Dependency:** Phase 6 front-door orchestration.

### E2. Broad historical subject constellations

Support inquiries such as the history of sugar without creating one
undifferentiated SubjectConcept. The SCA should construct a constellation of
focused subjects such as cultivation, production, trade, labor, consumption,
and environmental change.

**Dependency:** E1 and domain-specific federation profiles.

### E3. Domain adaptation and federation profiles

Select authorities and source providers by domain, capability, language,
coverage, licensing, precision, and service health. The core assertion,
provenance, proposal, and commit workflow must remain unchanged across Roman,
Mesoamerican, commodity, and other domains.

**Dependency:** Phase 4 authority adapters and E2.

### E4. Visual graph navigation and semantic bridges

Provide bounded graph projections, evidence expansion, saved navigation
contexts, and explicit trace modes:

```text
TRACE_EXISTING_PATH
DISCOVER_SEMANTIC_BRIDGE
```

Semantic bridge discovery must distinguish committed paths from hypotheses,
identify missing or weak hops, and never convert a discovered path into a
durable claim automatically.

**Dependency:** Phase 3 direct queries and accepted assertion status.

### E5. Machine-readable index harvesting

Ingest edition-specific scholarly indexes as source artifacts and finding aids.
Preserve entries, subentries, locators, cross-references, rights, and edition
identity. Use deterministic parsing, passage retrieval, SourceObservations,
SFA proposals, and SCA decisions.

Index entries must not become claims or durable SubjectConcepts automatically.

**Dependency:** Phase 3 source observations, Phase 5 proposal workflow, and
rights-aware source storage.

### E6. Architecture self-description and prompt governance

Add versioned architecture, role, prompt, schema, policy, mapping, and tool
definitions with an externally controlled bootstrap manifest. Record the exact
versions used for each execution.

**Dependency:** Phase 8 governance and a proven proposal workflow.

### E7. Source perspective and multilingual terminology

Preserve Indigenous, local, historical, and source-specific terms alongside
normalized mappings. Record source perspective, language, mediation, creator
community, and production context where these affect interpretation.

**Dependency:** E3, source-observation maturity, and a concrete domain test.

### E8. Evidence stance and contested assertions

Scholarly sources disagree. The graph currently has only `SUPPORTED_BY`, so it
cannot record that a source contradicts or qualifies an Assertion. Add a
stance to the evidence link (`supports`, `contradicts`, `qualifies`) and define
when contradicting evidence moves an Assertion to `contested`, without
collapsing competing interpretations into one claim.

**Dependency:** Phase 5 proposal workflow. Required before ingesting
secondary scholarship. Raised by
[docs/Response - Model and API Choice.md](docs/Response%20-%20Model%20and%20API%20Choice.md).

### E9. Source acquisition through a research API

Use a research API (Perplexity Agent API per the model-choice review) to
discover and fetch candidate sources. Its output is a preserved, hashed
document that may become a SourceObservation; search results and synthesized
answers are never evidence themselves.

**Dependency:** passage observations (Phase 5 step 4), E5 rights-aware source
storage.

### E10. Source discovery and source chronology

For an inquiry, the agent should discover which sources exist for the subject
and where they stand relative to one another, rather than reading only the
source it was handed. For Actium, Plutarch (early 2nd century CE) is a late
narrative; earlier witnesses include Augustan poetry (Horace, Virgil,
Propertius), Velleius Paterculus, and Augustus's own lost memoir, which
Plutarch cites at *Antony* 68.1 ("as Caesar himself has written").

Discovery channels:

1. citations inside passages already read (source chains such as 68.1);
2. Wikidata `described by source` (P1343) and work/author statements;
3. CTS catalogues (Perseus/Scaife) by author, work, and date;
4. scholarly bibliographies and the E9 research API.

Model needs: source works as `Entity {kind: Work}` with authors and
composition dates (temporal qualification, Phase 7); passage observations
linked to their Work; a predicate for one source citing or deriving from
another; and an inquiry-level source plan ranked by date, genre
(contemporary poetry versus later narrative), and independence. Discovery
proposes sources and source relations; preserving and reading them still
goes through the existing observation, proposal, and review path.

**Dependency:** E9, Phase 7 temporal qualification, Work entities.

### E12. Attributed claims and depicted events (precedes E11)

Narrative detail in a source is the author's depiction, not established fact.
"Caesar ordered his right wing to row backwards, wishing to draw the enemy
out" is *according to Plutarch (Antony 65.5)*; the goal clause is Plutarch's
reading of Caesar's intent. Following the prosopographical factoid pattern
("source S says P did X"):

- **Two claim modes.** `asserted` claims are Chrystallum's own claim that
  something happened. `attributed` claims state that a source depicts it and
  carry `attributedTo` (Work and author). Accepting an attributed claim means
  it accurately captures what the source says, which a verbatim quotation and
  curator review can verify; it does not mean the event happened.
- **Each source keeps its own narrative.** Micro-events (movements, orders,
  flights, surrenders) are depicted events within one work. Depictions by
  different sources coexist and do not contradict each other; the claim that
  two depictions refer to the same historical event is separate, interpretive,
  and contestable (E8). No cross-source merging is forced.
- **Promotion is explicit.** An attributed claim becomes asserted only by a
  curator decision with a recorded basis, such as independent corroboration or
  scholarly consensus.
- **Works become entities** (Plutarch as Person, *Life of Antony* as Work), as
  E10 also requires.
- **Existing claims.** *Mark Antony participated in Battle of Actium* rests on
  Plutarch alone; Augustus and Agrippa add Wikidata, an aggregator rather than
  an independent witness. E10 sources are what would make these corroborated.

Micro-events in *Antony* 65–68 (about fifteen: the four-day delay, Caesar's
dawn tour, the sixth-hour advance, the backing-water order, Agrippa's
encirclement, Cleopatra's flight, Antony's pursuit, the tenth-hour surrender,
the land army's seven days) are the pilot. Plutarch marks triggers and goals
explicitly ("when he saw", "no sooner ... than", "wishing to"), so IGAR (E11)
is extracted as attributed claims over depicted events. Sequence must come
from time markers ("fifth day", "sixth hour"), not narration order.

**Dependency:** design doc first; Work entities; relative temporal markers
(Phase 7-lite); predicates performedBy, movedTo/From, triggeredBy, resultedIn,
precededBy, aimedAt.

### E11. Actor actions (IGAR) and causal context

For an event inquiry, decompose each actor's part as Input (trigger), Goal,
Action, and Result. Actions are sub-events (`Entity {kind: Event}`, such as
"Antony's flight from Actium") linked by claims: performed by an actor, part
of the event, triggered by a prior event, resulted in an outcome. Goals are
the most interpretive element and are always attributed to a source: Plutarch
66.4 ("dragged along by the woman"), rightly rejected as evidence of
participation, is valid evidence for "Antony's goal, according to Plutarch".

A broad request such as "graph the battle" becomes a subject constellation
(causes and prelude, the battle, aftermath). A "why it happened" preface is an
Explanation Agent output generated from claims, citing each; causal claims are
interpretive and attributed, and may be contested (E8).

Review the legacy `scripts/agents/military/igar.py` as reference only, per the
legacy triage rules.

**Dependency:** commanded-forces model (done), new predicates (performedBy,
triggeredBy, resultedIn, aimedAt), E8 stance, Phase 7 temporal ordering.

### E13. Geography and space-time exploration

Maps let Chrystallum test sources against the physical world, not only
display places.

**Constraints**

- Modern basemaps show today's geography; ancient coastlines and harbours
  differ (Actium's gulf mouth, Ephesus's silted harbour). Historical layers are
  required: Pleiades, the Ancient World Mapping Center, DARMC, and ORBIS
  (Roman travel time and cost).
- Canonical coordinates come from open sources (Pleiades, Wikidata P625).
  Google Maps Platform is a display and analysis layer; its terms restrict
  storing or caching most content. Verify current terms and pricing before
  building.
- A location is a claim: it has a source, a precision radius, and a time.
  Place names and boundaries change.

**Capabilities, in order**

1. Space-time explorer: a map panel beside the graph stage, linked selection
   in both directions, one timeline slider driving both.
2. Micro-event tracks by source (after E12): the battle replayed as movements
   "according to Plutarch", with other sources as alternative tracks, so
   divergence between witnesses is visible.
3. Place as a doorway through time: everything at a place across periods.
4. Place resolution on the map: candidate pins for unresolved place mentions,
   ranked by consistency with the narrative's directions and distances.
5. Physical plausibility of depictions: sightlines, travel speeds, distances,
   and wind against terrain (elevation, photorealistic 3D tiles, Earth Engine)
   and a reconstructed ancient coastline. Results are **computed claims** with
   versioned methods and data, evidence about depictions, never facts.
6. Co-presence leads: people in the same place in the same season, offered to
   semantic-bridge discovery as hypotheses, never as claims.
7. Live updates: proposed tracks dashed, accepted tracks solid, using the
   graph's status encoding.

**Model needs:** Place entities with location claims (source, precision,
time); region geometry; movement claims (movedFrom/To with relative time)
forming trajectories; a `computed` claim type with method versioning.

**Order:** Pleiades coordinates and a synchronized map panel first; source
tracks after E12; terrain and plausibility analysis last (needs reconstructed
coastlines).

**Dependency:** E12 (depicted events, attributed claims), Phase 7 temporal
qualification, Phase B read API, explorer UI.

### E14. Entity images (with Phase B)

Show Wikidata-linked images on entity cards. Nine of the first fourteen
Wikidata entities have one (P18; P242 locator maps for places).

- No graph change: the file name comes from the preserved Wikidata payload,
  like aliases and dates.
- Commons metadata (license, author, description, date, thumbnail URL) is
  fetched once per file and preserved with a hash, so attribution is
  reproducible.
- **Images are depictions.** Each card states what the image is and when it
  was made: the Battle of Actium's image is a 17th-century painting; the
  Domitius Ahenobarbus image is probably the altar relief associated with the
  family (attribution debated), not a portrait of the consul of 32 BCE. A
  model may suggest the type (contemporary, later depiction, modern photo of a
  site); the curator corrects it.
- **Licenses vary** (public domain to CC BY-SA): every card shows author,
  license, and a Commons link.
- Later: coins struck in a person's lifetime are contemporary portraits and
  primary evidence (via numismatic authorities such as Nomisma).

**Dependency:** Phase B read API; explorer UI cards.

### E15. Graph change governance: changesets, impact analysis, cluster ownership

A governance pattern for graph updates, borrowed from source-code review
(pull requests, diffs, code owners, history, revert). It is not a product
goal. Graph versioning tools exist (git-style branching and diffs); what is
typically missing is *semantic* governance before an update: knowing which
clusters a change affects, routing it to those clusters' curators, and
treating an identity merge as riskier than a label edit.

**Already in place:** Proposals (pull requests), curator review, decision
records with prompt and model provenance (history), supersede/reject/reopen
instead of delete (revert), a deterministic validator re-run at commit
(checks), and rolled-back transactions (dry runs).

**To add:**

1. **Changesets.** Group related proposals into one reviewable unit: a reader
   run, an identity merge, a predicate change.
2. **Diffs before commit.** Apply a changeset in a rolled-back transaction,
   compute the exact node and edge changes, present them for review.
3. **Explicit clusters.** A cluster is a Subject with its scope rule and
   declared members; broader/narrower Subjects form the hierarchy.
4. **Impact analysis.** Vertex jump (direct lookup by stable ID: Entity.id,
   Assertion.id, AuthorityRecord(system, identifier)) locates the touched
   vertices without traversal. A membership and dependency index then answers
   who relies on them: vertex → clusters; claim → saved paths and
   explanations; predicate → claims using it.
5. **Impact-routed review.** Low-impact changes inside one cluster (verified
   attributed claims) follow the automatic acceptance policy (Phase C); changes
   crossing clusters or touching shared vertices (Augustus belongs to many
   subjects) need each affected cluster's curators; identity and predicate
   changes always need a human with the impact report attached.
6. **Later:** cluster ownership (curators per Subject), private workspaces as
   branches with publication by review (use case 3), tagged graph versions for
   replaying saved maps (06 §10) and for domain packs.

| Change | Reach | Example |
|---|---|---|
| Identity (merge, split, re-link) | every claim on the entity, in every cluster | resolving "Domitius" to Q360920 |
| Predicate redefinition | every claim using the predicate | `commanded` v2 rejected the event-level claim |
| Claim status | paths and explanations through the edge | promotion to asserted |
| Display text | negligible | label edits |

**Start with:** dry-run diff and impact report for identity and predicate
changes, explicit clusters, and the membership index. Changesets, ownership,
and releases follow as the graph spans more clusters.

**Dependency:** Phase C review policy (shares the routing rules); multiple
Subjects in the graph.

### E16. Frontier expansion: from leaf nodes to clusters

Leaf nodes (entities with an identity link and little else, such as Marcus
Insteius) are the graph's frontier. In an exploration graph they are doors.
Expanding them is three separate jobs, not one agent:

1. **Frontier ledger (deterministic, not an agent).** What is built versus
   what is still needed, per entity: claims by status, evidence count,
   unresolved mentions that point at it, predicates typical for its kind but
   missing (a Person without birth, death, or office claims), cluster
   memberships, and, once the explorer exists, how often people navigate to
   it. Output: a ranked worklist. Being deterministic makes it auditable and
   cheap to recompute after every commit.
2. **Frontier planner (agent).** Reads the worklist and decides, per leaf,
   what kind of work it needs and routes it to the existing workers: identity
   queue, Wikidata statement harvest, source discovery (E10), or a reader
   inquiry with a facet lens. It also decides whether the expansion **extends
   the current cluster** (stays within the Subject's focus) or **opens a new
   one** (Agrippa → his building programme → the Pantheon); a new cluster is a
   proposed Subject with a broader/narrower/related link, governed by E15. The
   planner writes work orders; it does not extract claims or write the graph.
3. **Workers.** The reader with lenses, the deterministic proposers, and the
   identity queue do the extraction, through the normal proposal path.

This is not the facet SFA's job: lenses extract within a scope, while the
planner chooses scopes. It is closest to the coordinating role planned for
the SCA (a cluster steward), or a concierge for gaps rather than for user
requests.

It is deliberately **not a blind subgraph crawler.** Unbudgeted expansion
along authority links is how the legacy system produced millions of noise
edges. Expansion is budgeted per cluster, ranked by relevance to the cluster's
focus, by demand (where people explore), and by bridge potential (cross-facet
edges), with explicit stopping rules and the curator's review capacity
(E15 routing) as a hard limit.

In the explorer, leaves are marked as unexplored frontier, and "expand" on a
leaf creates a planner work order (use case 2: drill-down).

**Bridge-directed expansion.** Expansion can also be aimed at a target. When
a semantic-bridge trace (06 §14, the senator-to-mollusk path through purple)
finds the clusters at both ends but gaps between them, the planner turns each
missing hop into a work order: a missing entity ("broad purple stripe") to the
identity queue or a local entity; a missing claim to a reader inquiry with the
fitting lens (social for dress convention, technological for dye production,
biological for taxonomy). The discovered path stays a hypothesis until its
missing hops are proposed and accepted (06 §15).

**Dependency:** Phase B read API (ledger queries), E10, E15, facet lenses
(Phase D).

### Backlog acceptance rule

An enhancement may move into the active phase sequence only when its
implementation proposal identifies:

1. the user-facing use case;
2. the smallest required graph or service change;
3. the dependencies and authority boundaries;
4. an observable acceptance test;
5. its effect on existing data and retry behavior;
6. its provenance and rights requirements, when sources are involved.
