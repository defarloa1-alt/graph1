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

### Backlog acceptance rule

An enhancement may move into the active phase sequence only when its
implementation proposal identifies:

1. the user-facing use case;
2. the smallest required graph or service change;
3. the dependencies and authority boundaries;
4. an observable acceptance test;
5. its effect on existing data and retry behavior;
6. its provenance and rights requirements, when sources are involved.
